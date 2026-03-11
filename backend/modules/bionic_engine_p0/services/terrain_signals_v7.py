"""
BIONIC V7 — Terrain Signals V7
Extraction de signaux terrain a partir des donnees existantes.

Extrait des signaux terrain utiles pour le scoring et la typologie:
  - Depuis OSM/Overpass (deja disponible via exclusions)
  - Depuis DEM si cle API presente (via dem_service)
  - Depuis meteo Open-Meteo (gratuit, sans cle)
  - Fallback heuristique si donnees manquantes

100% independant. Consomme par pipeline_v7.
"""

import math
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger("bionic_engine.terrain_signals_v7")

METERS_PER_DEG_LAT = 111320.0


def extract_terrain_signals_from_exclusions(
    centroid: Dict[str, float],
    exclusions: List[Dict],
    radius_m: float = 1000.0,
) -> Dict[str, Any]:
    """
    Extrait des signaux terrain depuis les exclusions OSM deja fetchees.
    Analyse la densite et la proximite des features autour du centroid.
    """
    clat, clng = centroid.get("lat", 0), centroid.get("lng", 0)
    cos_lat = math.cos(math.radians(clat))
    radius_deg_lat = radius_m / METERS_PER_DEG_LAT
    radius_deg_lng = radius_m / (METERS_PER_DEG_LAT * max(cos_lat, 0.01))

    counts = {"water": 0, "wetland": 0, "roads": 0, "urban": 0, "infrastructure": 0}
    nearest = {"water": float("inf"), "wetland": float("inf"), "roads": float("inf"),
               "urban": float("inf"), "infrastructure": float("inf")}
    road_subtypes = {}
    water_subtypes = {}
    urban_subtypes = {}

    for ex in exclusions:
        if ex.get("filtered_out"):
            continue
        ex_type = ex.get("type", "")
        coords = ex.get("coordinates", [])
        if not coords:
            continue

        in_radius = False
        min_d = float("inf")
        for c in coords[:30]:
            dlat = abs(c[1] - clat)
            dlng = abs(c[0] - clng)
            if dlat < radius_deg_lat and dlng < radius_deg_lng:
                in_radius = True
                d = math.sqrt(
                    ((c[1] - clat) * METERS_PER_DEG_LAT) ** 2 +
                    ((c[0] - clng) * METERS_PER_DEG_LAT * cos_lat) ** 2
                )
                if d < min_d:
                    min_d = d

        if in_radius:
            if ex_type in counts:
                counts[ex_type] += 1
            if ex_type in nearest and min_d < nearest[ex_type]:
                nearest[ex_type] = min_d

            sub = ex.get("sub_type", "unknown")
            if ex_type == "roads":
                road_subtypes[sub] = road_subtypes.get(sub, 0) + 1
            elif ex_type == "water":
                water_subtypes[sub] = water_subtypes.get(sub, 0) + 1
            elif ex_type == "urban":
                urban_subtypes[sub] = urban_subtypes.get(sub, 0) + 1

    # Compute derived signals
    has_major_road = any(
        st in road_subtypes
        for st in ("motorway", "trunk", "primary", "secondary")
    )
    has_water_body = any(
        st in water_subtypes
        for st in ("lake", "reservoir", "pond", "river")
    )
    has_stream = any(
        st in water_subtypes
        for st in ("stream", "ditch", "drain")
    )
    is_edge_zone = (
        counts["urban"] > 0 and nearest["urban"] > 200 and nearest["urban"] < 800
    ) or (
        counts["roads"] > 0 and nearest["roads"] > 100 and nearest["roads"] < 500
    )

    forest_proxy = 1.0 - min(1.0, counts["urban"] / 5.0)
    disturbance = min(1.0, (counts["roads"] + counts["urban"] + counts["infrastructure"]) / 10.0)

    return {
        "counts": counts,
        "nearest_m": {k: round(v, 1) if v < 10000 else None for k, v in nearest.items()},
        "road_subtypes": road_subtypes,
        "water_subtypes": water_subtypes,
        "urban_subtypes": urban_subtypes,
        "has_major_road": has_major_road,
        "has_water_body": has_water_body,
        "has_stream": has_stream,
        "is_edge_zone": is_edge_zone,
        "forest_proxy": round(forest_proxy, 2),
        "disturbance_index": round(disturbance, 2),
    }


async def fetch_weather_signals(
    bounds: Dict[str, float],
) -> Optional[Dict[str, Any]]:
    """
    Fetch weather signals from Open-Meteo (gratuit).
    Returns simplified weather dict for scoring.
    """
    try:
        from modules.bionic_engine_p0.services.open_meteo_service import (
            fetch_weather_raw,
        )
        raw = await fetch_weather_raw(bounds)
        if raw is None:
            return None

        hourly = raw.get("hourly", {})
        temps = hourly.get("temperature_2m", [])
        winds = hourly.get("wind_speed_10m", [])
        precips = hourly.get("precipitation", [])
        clouds = hourly.get("cloud_cover", [])

        now_idx = min(12, len(temps) - 1) if temps else 0

        result = {
            "temperature": temps[now_idx] if temps else 15.0,
            "wind_speed": winds[now_idx] if winds else 10.0,
            "precipitation": precips[now_idx] if precips else 0.0,
            "cloud_cover": clouds[now_idx] if clouds else 50.0,
        }

        # Classify condition
        if result["wind_speed"] > 30:
            result["condition"] = "high_wind"
        elif result["precipitation"] > 5:
            result["condition"] = "rain"
        elif result["temperature"] > 25:
            result["condition"] = "heat"
        elif result["temperature"] < -10:
            result["condition"] = "cold"
        elif result["cloud_cover"] > 95 and result["temperature"] < 5:
            result["condition"] = "fog"
        else:
            result["condition"] = "clear"

        return result

    except Exception as e:
        logger.debug(f"Weather fetch skipped: {e}")
        return None


async def fetch_dem_signals(
    bounds: Dict[str, float],
    species: str,
    resolution: int = 60,
) -> Optional[Dict[str, Any]]:
    """
    Fetch DEM signals si la cle API est disponible.
    Returns simplified terrain dict for scoring.
    """
    try:
        from modules.bionic_engine_p0.services.dem_service import fetch_dem_composite
        result = await fetch_dem_composite(bounds, species, resolution)
        if result.get("status") != "success":
            return None
        return {
            "available": True,
            "stats": result.get("stats", {}),
            "fields": result.get("fields", {}),
        }
    except Exception as e:
        logger.debug(f"DEM fetch skipped: {e}")
        return None
