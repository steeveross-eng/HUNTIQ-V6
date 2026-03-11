"""
BIONIC V6 — Exclusion Geometry V6
Operations geometriques Shapely pour le pipeline d'exclusion.

Fonctions utilitaires:
  - Conversion coords OSM → Shapely
  - Buffer en metres (via conversion degres)
  - Construction d'index spatial STRtree
  - Calcul intersection/distance exact polygon-polygon

Orchestré par exclusion_engine_v6.py
"""

import math
import logging
from typing import Dict, List, Optional, Tuple

from shapely.geometry import Polygon, LineString, MultiPolygon, GeometryCollection
from shapely.ops import unary_union
from shapely.strtree import STRtree
from shapely import prepared

from .exclusion_config_v6 import get_buffer_m

logger = logging.getLogger("bionic_engine.exclusion_geometry_v6")

METERS_PER_DEG_LAT = 111320.0


def _meters_to_deg(meters: float, lat_center: float) -> Tuple[float, float]:
    """Convertit des metres en degres lat/lng a une latitude donnee."""
    deg_lat = meters / METERS_PER_DEG_LAT
    cos_lat = math.cos(math.radians(lat_center))
    deg_lng = meters / (METERS_PER_DEG_LAT * max(cos_lat, 0.01))
    return deg_lat, deg_lng


def osm_coords_to_shapely(coords: list, geom_type: str) -> Optional[object]:
    """
    Convertit les coordonnees OSM [lng, lat] en geometrie Shapely.
    Returns None si la geometrie est invalide.
    """
    if not coords or len(coords) < 2:
        return None

    try:
        if geom_type == "polygon":
            if len(coords) < 3:
                return None
            ring = [(c[0], c[1]) for c in coords]
            if ring[0] != ring[-1]:
                ring.append(ring[0])
            poly = Polygon(ring)
            if not poly.is_valid:
                poly = poly.buffer(0)
            return poly if not poly.is_empty else None

        elif geom_type == "line":
            if len(coords) < 2:
                return None
            line = LineString([(c[0], c[1]) for c in coords])
            return line if line.is_valid and not line.is_empty else None

    except Exception as e:
        logger.debug(f"Shapely conversion failed: {e}")
        return None

    return None


def apply_buffer_m(geom, buffer_m: float, lat_center: float):
    """
    Applique un buffer en metres autour d'une geometrie Shapely.
    Conversion degres via la latitude centrale.
    Retourne la geometrie bufferisee ou l'originale si buffer=0.
    """
    if buffer_m <= 0 or geom is None:
        return geom

    deg_lat, deg_lng = _meters_to_deg(buffer_m, lat_center)
    avg_deg = (deg_lat + deg_lng) / 2.0

    try:
        buffered = geom.buffer(avg_deg, resolution=8)
        return buffered if not buffered.is_empty else geom
    except Exception:
        return geom


def build_exclusion_unions(
    exclusions: List[Dict],
    lat_center: float,
    bounds: Dict[str, float] = None,
    buffer_fn=None,
) -> Dict[str, object]:
    """
    Construit les unions geometriques par type d'exclusion.
    Applique les buffers V6 par sous-type.

    BIONIC WATER FIX: Les features water filtered_out (rivières > 2km²,
    relations > 10km²) sont INCLUSES et clippées au viewport bounds.
    Ceci garantit qu'aucune zone n'est generee dans l'eau.

    Returns:
        {
          "water": PreparedGeometry(MultiPolygon),
          "urban": PreparedGeometry(MultiPolygon),
          "roads": PreparedGeometry(MultiPolygon),
          "infrastructure": PreparedGeometry(MultiPolygon),
          "raw_water": MultiPolygon (non-prepared, pour distance),
          "raw_urban": ...,
          ...
        }
    """
    from shapely.geometry import box as shapely_box

    geoms_by_type: Dict[str, list] = {
        "water": [],
        "urban": [],
        "roads": [],
        "infrastructure": [],
    }

    # Build clip box from bounds (with margin for buffers)
    clip_box = None
    if bounds:
        margin = 0.005  # ~500m margin
        clip_box = shapely_box(
            bounds["west"] - margin,
            bounds["south"] - margin,
            bounds["east"] + margin,
            bounds["north"] + margin,
        )

    for ex in exclusions:
        is_filtered = ex.get("filtered_out", False)
        ex_type = ex.get("type", "")

        # BIONIC WATER FIX: Include filtered_out WATER features (large rivers/relations).
        # These were excluded for performance but this caused zones in water.
        # For non-water types, still skip filtered_out entries.
        if is_filtered and ex_type != "water":
            continue

        if ex_type == "wetland":
            continue
        if ex_type not in geoms_by_type:
            continue

        sub_type = ex.get("sub_type", "")
        geom_type = ex.get("geometry_type", "polygon")
        coords = ex.get("coordinates", [])

        shapely_geom = osm_coords_to_shapely(coords, geom_type)
        if shapely_geom is None:
            continue

        # For filtered_out (oversized) water features, clip to viewport bounds
        # to keep the geometry manageable for Shapely operations
        if is_filtered and ex_type == "water" and clip_box is not None:
            try:
                if not shapely_geom.is_valid:
                    shapely_geom = shapely_geom.buffer(0)
                clipped = shapely_geom.intersection(clip_box)
                if clipped.is_empty:
                    continue
                shapely_geom = clipped
                logger.info(
                    f"[WATER-FIX] Clipped oversized water feature "
                    f"(sub_type={sub_type}, reason={ex.get('reason')}) to viewport bounds"
                )
            except Exception as e:
                logger.warning(f"[WATER-FIX] Clip failed for oversized water: {e}")
                continue

        _buffer_lookup = buffer_fn if buffer_fn is not None else get_buffer_m
        buffer_m = _buffer_lookup(ex_type, sub_type)
        if buffer_m > 0:
            shapely_geom = apply_buffer_m(shapely_geom, buffer_m, lat_center)

        if shapely_geom is not None and not shapely_geom.is_empty:
            if shapely_geom.geom_type == "Point":
                continue
            # Handle MultiPolygon/GeometryCollection from clipping
            if shapely_geom.geom_type in ("MultiPolygon", "GeometryCollection"):
                for geom in shapely_geom.geoms:
                    if geom.geom_type == "Polygon" and not geom.is_empty:
                        geoms_by_type[ex_type].append(geom)
            else:
                geoms_by_type[ex_type].append(shapely_geom)

    result = {}
    for ex_type, geom_list in geoms_by_type.items():
        if geom_list:
            try:
                union = unary_union(geom_list)
                if union.is_empty:
                    result[f"raw_{ex_type}"] = None
                    result[ex_type] = None
                else:
                    # Final clip to bounds for performance (water especially)
                    if clip_box is not None and ex_type == "water":
                        union = union.intersection(clip_box)
                        if not union.is_valid:
                            union = union.buffer(0)
                    result[f"raw_{ex_type}"] = union
                    result[ex_type] = prepared.prep(union)
            except Exception as e:
                logger.warning(f"Union failed for {ex_type}: {e}")
                result[f"raw_{ex_type}"] = None
                result[ex_type] = None
        else:
            result[f"raw_{ex_type}"] = None
            result[ex_type] = None

    water_count = len(geoms_by_type.get("water", []))
    if water_count > 0:
        logger.info(
            f"[WATER-FIX] Water union built from {water_count} geometries "
            f"(bounds_clipped={'yes' if clip_box else 'no'})"
        )

    return result


def calculate_intersection_ratio(
    zone_poly: Polygon,
    exclusion_union,
) -> float:
    """
    Calcule le ratio d'intersection exact: zone_overlap_area / zone_area.
    exclusion_union peut etre un PreparedGeometry ou une geometrie brute.
    """
    if exclusion_union is None or zone_poly is None:
        return 0.0

    zone_area = zone_poly.area
    if zone_area <= 0:
        return 0.0

    try:
        raw = exclusion_union
        if hasattr(exclusion_union, "context"):
            raw = exclusion_union.context

        if not raw.intersects(zone_poly):
            return 0.0

        intersection = zone_poly.intersection(raw)
        if intersection.is_empty:
            return 0.0

        return intersection.area / zone_area

    except Exception:
        return 0.0


def calculate_min_distance_deg(
    zone_poly: Polygon,
    exclusion_raw,
) -> float:
    """
    Distance minimale polygon-polygon en degres.
    Retourne float('inf') si pas d'exclusion.
    """
    if exclusion_raw is None or zone_poly is None:
        return float("inf")

    try:
        return zone_poly.distance(exclusion_raw)
    except Exception:
        return float("inf")


def distance_deg_to_meters(dist_deg: float, lat_center: float) -> float:
    """Convertit une distance en degres en metres (approximation)."""
    cos_lat = math.cos(math.radians(lat_center))
    avg_m_per_deg = METERS_PER_DEG_LAT * (1.0 + cos_lat) / 2.0
    return dist_deg * avg_m_per_deg


def trim_zone(
    zone_poly: Polygon,
    all_exclusion_raw,
    min_area_deg2: float,
) -> Optional[Polygon]:
    """
    Decoupe une zone en retirant les exclusions.
    Retourne le plus grand fragment ou None si trop petit.
    """
    if all_exclusion_raw is None:
        return zone_poly

    try:
        trimmed = zone_poly.difference(all_exclusion_raw)
        if trimmed.is_empty:
            return None

        if trimmed.geom_type == "Polygon":
            if trimmed.area >= min_area_deg2:
                return trimmed
            return None

        if trimmed.geom_type in ("MultiPolygon", "GeometryCollection"):
            polygons = []
            if trimmed.geom_type == "MultiPolygon":
                polygons = list(trimmed.geoms)
            else:
                polygons = [g for g in trimmed.geoms if g.geom_type == "Polygon"]

            if not polygons:
                return None

            largest = max(polygons, key=lambda p: p.area)
            if largest.area >= min_area_deg2:
                return largest
            return None

    except Exception:
        return zone_poly

    return None


def shapely_to_osm_coords(geom) -> list:
    """Convertit une geometrie Shapely en coordonnees OSM [lng, lat]."""
    if geom is None or geom.is_empty:
        return []

    if geom.geom_type == "Polygon":
        return [[c[0], c[1]] for c in geom.exterior.coords]
    elif geom.geom_type == "MultiPolygon":
        largest = max(geom.geoms, key=lambda p: p.area)
        return [[c[0], c[1]] for c in largest.exterior.coords]

    return []


def polygon_area_m2_shapely(geom, lat_center: float) -> float:
    """Calcule l'aire en m2 d'une geometrie Shapely."""
    if geom is None or geom.is_empty:
        return 0.0
    cos_lat = math.cos(math.radians(lat_center))
    m_per_deg_lat = METERS_PER_DEG_LAT
    m_per_deg_lng = METERS_PER_DEG_LAT * cos_lat
    return geom.area * m_per_deg_lat * m_per_deg_lng


def compute_compactness(geom) -> float:
    """Calcule la compacite (4*pi*area / perimeter^2) d'un polygone."""
    if geom is None or geom.is_empty or geom.geom_type != "Polygon":
        return 0.0
    area = geom.area
    perim = geom.length
    if perim <= 0:
        return 0.0
    return (4.0 * math.pi * area) / (perim * perim)
