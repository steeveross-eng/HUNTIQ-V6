"""
API Router — Organic Zones V2
BIONIC V5 — Pipeline Organique Unifié

POST /api/v1/bionic/organic-zones
Entrée: bounds + species + layers[]
Sortie: GeoJSON organiques (toutes couches) + métadonnées

100% backend. 0 logique UI. 0 dépendance transversale.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime, timezone

logger = logging.getLogger("bionic_engine.organic_zones_router")

router = APIRouter(prefix="/api/v1/bionic", tags=["BIONIC Organic Zones V2"])


class OrganicZoneBounds(BaseModel):
    north: float = Field(..., ge=-90, le=90)
    south: float = Field(..., ge=-90, le=90)
    east: float = Field(..., ge=-180, le=180)
    west: float = Field(..., ge=-180, le=180)


class WaypointCenter(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)


class OrganicZoneRequest(BaseModel):
    bounds: OrganicZoneBounds
    species: str = "moose"
    layers: Optional[List[str]] = None
    exclusions: Optional[List[dict]] = None
    resolution: int = Field(default=80, ge=30, le=150)
    max_zones_per_layer: int = Field(default=8, ge=1, le=20)
    include_scoring: bool = True
    season: Optional[str] = None
    biological_season: Optional[str] = None  # V8.1: pre_rut, rut, post_rut, winter, spring
    weather: Optional[dict] = None
    waypoint_center: Optional[WaypointCenter] = None


# V8.1 — Poids des couches par saison biologique
BIOLOGICAL_SEASON_WEIGHTS = {
    "pre_rut": {"habitats": 1.2, "rut": 1.5, "repos": 0.8, "alimentation": 1.3, "corridors": 1.6, "salines": 1.4, "affuts": 1.2},
    "rut":     {"habitats": 1.0, "rut": 2.0, "repos": 0.5, "alimentation": 0.7, "corridors": 1.8, "salines": 0.8, "affuts": 1.5},
    "post_rut":{"habitats": 1.3, "rut": 0.3, "repos": 1.5, "alimentation": 1.8, "corridors": 1.0, "salines": 0.6, "affuts": 1.0},
    "winter":  {"habitats": 1.5, "rut": 0.0, "repos": 1.8, "alimentation": 1.6, "corridors": 0.5, "salines": 0.3, "affuts": 0.5},
    "spring":  {"habitats": 1.0, "rut": 0.1, "repos": 1.0, "alimentation": 1.5, "corridors": 1.2, "salines": 1.3, "affuts": 0.8},
}


@router.post("/organic-zones")
async def generate_zones(request: OrganicZoneRequest):
    """
    Génère des zones organiques BIONIC V5 pour les bounds donnés.

    Pipeline complet:
    1. Rasterisation comportementale (behavioral_rasterizer)
    2. Extraction contours (Marching Squares)
    3. Lissage Chaikin 2x
    4. Filtrage compactness < 0.85 + aire 4500-10000 m²
    5. Exclusion OSM (eau, routes, urbain)
    6. Scoring intégré
    7. Export GeoJSON
    """
    try:
        from modules.bionic_engine_p0.services.zone_engine_core_v2 import generate_organic_zones
        from modules.bionic_engine_p0.services.scoring_zone_integration import enrich_geojson_with_scores

        bounds = {
            "north": request.bounds.north,
            "south": request.bounds.south,
            "east": request.bounds.east,
            "west": request.bounds.west,
        }

        # Determine season
        season = request.season
        if not season:
            month = datetime.now(timezone.utc).month
            if month in (3, 4, 5):
                season = "spring"
            elif month in (6, 7, 8):
                season = "summer"
            elif month in (9, 10, 11):
                season = "autumn"
            else:
                season = "winter"

        # Adaptive resolution based on viewport size (always applied)
        lat_range = bounds["north"] - bounds["south"]
        lng_range = bounds["east"] - bounds["west"]
        if lat_range > 0.15 or lng_range > 0.2:
            resolution = 25  # Very large viewport
        elif lat_range > 0.1 or lng_range > 0.15:
            resolution = 30  # Large viewport
        elif lat_range > 0.05:
            resolution = 40
        else:
            resolution = min(request.resolution, 80)  # Cap at 80

        # Limit layers for large viewports to keep response fast
        layers = request.layers
        if layers and len(layers) > 5 and (lat_range > 0.05 or lng_range > 0.08):
            # Large viewport: only top-priority layers
            priority_order = ["habitats", "rut", "alimentation", "corridors", "repos", "affuts", "hydro", "peuplements", "ndvi", "pentes"]
            layers = [ly for ly in priority_order if ly in layers][:5]

        # Waypoint center for corridor perimeter filtering
        waypoint_center = None
        if request.waypoint_center:
            waypoint_center = {"lat": request.waypoint_center.lat, "lng": request.waypoint_center.lng}

        # Generate organic zones (async — backend fetches own exclusions)
        geojson = await generate_organic_zones(
            bounds=bounds,
            species=request.species,
            layers=layers,
            exclusions=request.exclusions,
            resolution=resolution,
            max_zones_per_layer=request.max_zones_per_layer,
            waypoint_center=waypoint_center,
        )

        # BIONIC V7.4: Skip legacy V5 scoring enrichment when V7 engine is active.
        # V7 score_global is the SOLE source of truth. The V5 scoring module
        # (enrich_geojson_with_scores) would overwrite it with incorrect values.
        import os
        engine_version = os.environ.get("EXCLUSION_ENGINE_VERSION", "v5")
        if request.include_scoring and engine_version != "v7":
            geojson = enrich_geojson_with_scores(geojson, request.species, season, request.weather)

        # BIONIC OPTIM: Réduction payload — arrondi coordonnées à 6 décimales
        # V8.1: Application des poids saisonniers biologiques aux scores
        bio_season = request.biological_season
        season_weights = BIOLOGICAL_SEASON_WEIGHTS.get(bio_season, {}) if bio_season else {}

        # V8.2.1: Weather influence on zone scores
        weather_snapshot = None
        weather_influence = None
        weather_badges = []
        if isinstance(geojson, dict) and waypoint_center:
            try:
                from modules.bionic_engine_p0.services.weather_service_v1 import (
                    fetch_current_weather, compute_weather_influence,
                )
                weather_snapshot = await fetch_current_weather(
                    waypoint_center["lat"], waypoint_center["lng"]
                )
                weather_influence = compute_weather_influence(weather_snapshot)

                # Compute global multiplier (average of all categories)
                if weather_influence:
                    vals = [v for v in weather_influence.values() if isinstance(v, (int, float))]
                    weather_global = round(sum(vals) / len(vals), 3) if vals else 1.0
                else:
                    weather_global = 1.0

                # Determine weather badges
                if weather_global > 1.10:
                    weather_badges.append({"type": "favorable", "label": "Météo favorable", "color": "#22c55e"})
                wind_kmh = weather_snapshot.get("wind_speed_kmh", 0) or 0
                corr_mult = weather_influence.get("corridors", 1.0) if weather_influence else 1.0
                if wind_kmh > 25 and corr_mult < 0.85:
                    weather_badges.append({"type": "wind_alert", "label": "Alerte vent", "color": "#ef4444"})
                precip = weather_snapshot.get("precipitation_1h_mm", 0) or 0
                if precip > 5:
                    weather_badges.append({"type": "heavy_rain", "label": "Pluie forte", "color": "#3b82f6"})

            except Exception as weather_err:
                logger.warning(f"Weather influence skipped: {weather_err}")
                weather_influence = None
                weather_global = 1.0

        if isinstance(geojson, dict) and "features" in geojson:
            for feature in geojson.get("features", []):
                props = feature.get("properties", {})

                # V8.1: Ajuster le score selon la saison biologique
                if season_weights:
                    layer_id = props.get("layer_id", "")
                    weight = season_weights.get(layer_id, 1.0)
                    original_score = props.get("score", 0)
                    props["score"] = min(100, max(0, round(original_score * weight)))
                    props["seasonal_weight"] = weight
                    props["biological_season"] = bio_season

                # V8.2.1: Apply weather influence multipliers per category
                if weather_influence:
                    layer_id = props.get("layer_id", "")
                    w_mult = weather_influence.get(layer_id, weather_influence.get("habitats", 1.0))
                    score_before_weather = props.get("score", 0)
                    props["score"] = min(100, max(0, round(score_before_weather * w_mult)))
                    props["weather_multiplier"] = round(w_mult, 3)
                    props["weather_global"] = round(weather_global, 3)
                    props["score_pre_weather"] = score_before_weather
                    props["weather_badges"] = weather_badges

                # Arrondi coordonnées
                geom = feature.get("geometry", {})
                if geom.get("type") == "Polygon" and "coordinates" in geom:
                    geom["coordinates"] = [
                        [[round(c, 6) for c in pt] for pt in ring]
                        for ring in geom["coordinates"]
                    ]
                elif geom.get("type") == "MultiPolygon" and "coordinates" in geom:
                    geom["coordinates"] = [
                        [[[round(c, 6) for c in pt] for pt in ring] for ring in poly]
                        for poly in geom["coordinates"]
                    ]

        # V8.1: Ajouter les métadonnées de saison biologique à la réponse
        if bio_season and isinstance(geojson, dict):
            geojson["biological_season"] = {
                "id": bio_season,
                "weights_applied": bool(season_weights),
                "season_calendar": season,
            }

        # V8.2.1: Ajouter les métadonnées météo à la réponse
        if isinstance(geojson, dict) and weather_influence:
            geojson["weather_metadata"] = {
                "applied": True,
                "influence_multipliers": weather_influence,
                "global_multiplier": weather_global,
                "badges": weather_badges,
                "snapshot": {
                    "temperature_c": weather_snapshot.get("temperature_c") if weather_snapshot else None,
                    "wind_speed_kmh": weather_snapshot.get("wind_speed_kmh") if weather_snapshot else None,
                    "wind_gust_kmh": weather_snapshot.get("wind_gust_kmh") if weather_snapshot else None,
                    "precipitation_1h_mm": weather_snapshot.get("precipitation_1h_mm") if weather_snapshot else None,
                    "condition": weather_snapshot.get("condition") if weather_snapshot else None,
                    "condition_detail": weather_snapshot.get("condition_detail") if weather_snapshot else None,
                    "from_cache": weather_snapshot.get("from_cache") if weather_snapshot else None,
                },
                "cache_ttl_minutes": 30,
            }

        return geojson

    except Exception as e:
        logger.error(f"Error generating organic zones: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/organic-zones/layers")
async def list_available_layers():
    """Liste les couches et espèces supportées."""
    from modules.bionic_engine_p0.services.behavioral_rasterizer import get_supported_layers, get_supported_species
    from modules.bionic_engine_p0.services.zone_visual_layer_v2 import BIONIC_COLORS

    layers = []
    for lid in get_supported_layers():
        meta = BIONIC_COLORS.get(lid, {})
        layers.append({
            "id": lid,
            "label": meta.get("label", lid),
            "color": meta.get("color", "#999"),
            "category": meta.get("category", "unknown"),
        })

    return {
        "layers": layers,
        "species": [
            {"id": s, "label": s.replace("_", " ").title()}
            for s in get_supported_species()
        ]
    }



class SpeciesCorridorRequest(BaseModel):
    bounds: OrganicZoneBounds
    species: str = "moose"
    resolution: int = Field(default=40, ge=30, le=80)


@router.post("/corridors-v9/by-species")
async def generate_corridors_by_species(request: SpeciesCorridorRequest):
    """
    V9: Genere les corridors ecologiques pour une espece specifique.
    Retourne uniquement les corridors avec classification V9 et scores des 9 moteurs.
    """
    try:
        from modules.bionic_engine_p0.services.zone_engine_core_v2 import generate_organic_zones
        from bce.bce_corridor_v9 import validate_corridors_batch

        bounds = {
            "north": request.bounds.north, "south": request.bounds.south,
            "east": request.bounds.east, "west": request.bounds.west,
        }

        # Generate full zone data to extract corridors
        geojson = await generate_organic_zones(
            bounds=bounds,
            species=request.species,
            resolution=request.resolution,
            max_zones_per_layer=6,
        )

        corridors = geojson.get("corridors", [])

        # V9 classification stats
        classification_counts = {}
        engine_averages = {}
        engine_totals = {}
        for c in corridors:
            props = c.get("properties", {})
            level = props.get("classification_v9", {}).get("level", "gris")
            classification_counts[level] = classification_counts.get(level, 0) + 1

            scores_10x = props.get("scores_10x", {})
            for eng_id, eng_data in scores_10x.items():
                if isinstance(eng_data, dict):
                    engine_totals[eng_id] = engine_totals.get(eng_id, 0) + eng_data.get("score", 0)
                    engine_averages[eng_id] = engine_averages.get(eng_id, 0) + 1

        for eng_id in engine_totals:
            count = engine_averages.get(eng_id, 1)
            engine_averages[eng_id] = round(engine_totals[eng_id] / count, 1)

        # BCE validation
        bce_report = validate_corridors_batch(corridors, bounds)

        return {
            "species": request.species,
            "corridors": corridors,
            "total_corridors": len(corridors),
            "classification_v9": classification_counts,
            "engine_averages": engine_averages,
            "bce_validation": {
                "status": bce_report["status"],
                "compliance_rate": bce_report["compliance_rate"],
                "total_violations": bce_report["total_violations"],
            },
            "bounds": bounds,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.error(f"Species corridor generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
