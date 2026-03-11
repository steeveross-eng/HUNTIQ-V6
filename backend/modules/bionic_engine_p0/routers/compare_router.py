"""
BIONIC V8.3.A — Compare Router
Endpoint de comparaison multi-waypoints.

POST /api/v1/compare/waypoints
  Génère les zones + météo + corridors pour 2-3 waypoints en parallèle.
  Retourne un résumé structuré pour le CompareWidget frontend.
"""

import asyncio
import logging
import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

logger = logging.getLogger("bionic_engine.compare_router")
router = APIRouter(prefix="/api/v1/compare", tags=["BIONIC Compare V8.3"])


class WaypointInput(BaseModel):
    id: str
    name: str
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)


class CompareRequest(BaseModel):
    waypoints: List[WaypointInput] = Field(..., min_length=2, max_length=3)
    species: str = "moose"
    layers: List[str] = ["habitats", "alimentation", "repos", "rut", "corridors"]


async def _generate_for_waypoint(wp: WaypointInput, species: str, layers: List[str]) -> Dict[str, Any]:
    """Génère zones + météo pour un waypoint."""
    from modules.bionic_engine_p0.services.zone_engine_core_v2 import generate_organic_zones
    from modules.bionic_engine_p0.services.weather_service_v1 import (
        fetch_current_weather, compute_weather_influence,
    )

    t0 = time.time()
    radius = 0.015
    bounds = {
        "south": wp.lat - radius, "north": wp.lat + radius,
        "west": wp.lng - radius, "east": wp.lng + radius,
    }
    waypoint_center = {"lat": wp.lat, "lng": wp.lng}

    # Generate zones
    geojson = await generate_organic_zones(
        bounds=bounds, layers=layers,
        species=species, waypoint_center=waypoint_center,
    )

    # Weather
    weather_snapshot = None
    weather_influence = None
    try:
        weather_snapshot = await fetch_current_weather(wp.lat, wp.lng)
        weather_influence = compute_weather_influence(weather_snapshot)
    except Exception:
        pass

    # Extract summary
    features = geojson.get("features", []) if isinstance(geojson, dict) else []
    stats = geojson.get("stats", {}) if isinstance(geojson, dict) else {}
    corridors = geojson.get("corridors", []) if isinstance(geojson, dict) else []
    rejection_diag = geojson.get("rejection_diagnostics", {}) if isinstance(geojson, dict) else {}

    # Score by category
    category_scores = {}
    category_counts = {}
    for f in features:
        props = f.get("properties", {})
        layer_id = props.get("layer_id", "unknown")
        score = props.get("score", 0)
        if layer_id not in category_scores:
            category_scores[layer_id] = 0
            category_counts[layer_id] = 0
        category_scores[layer_id] += score
        category_counts[layer_id] += 1

    # Average scores by category
    avg_scores = {}
    for cat, total in category_scores.items():
        count = category_counts.get(cat, 1)
        avg_scores[cat] = round(total / count) if count > 0 else 0

    # Global score (weighted average)
    all_scores = [f.get("properties", {}).get("score", 0) for f in features]
    global_score = round(sum(all_scores) / len(all_scores)) if all_scores else 0

    # Corridor summary
    corridor_count = len(corridors)
    corridor_intensity = "aucun"
    if corridor_count > 10:
        corridor_intensity = "forte"
    elif corridor_count > 5:
        corridor_intensity = "modérée"
    elif corridor_count > 0:
        corridor_intensity = "faible"

    # Anthropic pressure from rejection diagnostics
    anthropic_rejections = 0
    if rejection_diag and "by_reason" in rejection_diag:
        for reason, count in rejection_diag["by_reason"].items():
            if "anthropic" in reason:
                anthropic_rejections += count

    computation_ms = round((time.time() - t0) * 1000)

    return {
        "waypoint": {"id": wp.id, "name": wp.name, "lat": wp.lat, "lng": wp.lng},
        "scores": {
            "global": global_score,
            "by_category": avg_scores,
        },
        "zones": {
            "total": len(features),
            "rejected": stats.get("rejected_exclusion", 0),
            "by_layer": category_counts,
        },
        "corridors": {
            "count": corridor_count,
            "intensity": corridor_intensity,
        },
        "weather": {
            "temperature_c": weather_snapshot.get("temperature_c") if weather_snapshot else None,
            "wind_speed_kmh": weather_snapshot.get("wind_speed_kmh") if weather_snapshot else None,
            "wind_gust_kmh": weather_snapshot.get("wind_gust_kmh") if weather_snapshot else None,
            "precipitation_1h_mm": weather_snapshot.get("precipitation_1h_mm") if weather_snapshot else None,
            "humidity_pct": weather_snapshot.get("humidity_pct") if weather_snapshot else None,
            "condition": weather_snapshot.get("condition") if weather_snapshot else None,
            "condition_detail": weather_snapshot.get("condition_detail") if weather_snapshot else None,
        },
        "weather_influence": weather_influence,
        "anthropic_pressure": {
            "rejections": anthropic_rejections,
            "level": "élevée" if anthropic_rejections > 5 else ("modérée" if anthropic_rejections > 0 else "faible"),
        },
        "computation_ms": computation_ms,
    }


@router.post("/waypoints")
async def compare_waypoints(request: CompareRequest):
    """Compare 2-3 waypoints en parallèle. Retourne scores, zones, corridors, météo."""
    t0 = time.time()

    tasks = [
        _generate_for_waypoint(wp, request.species, request.layers)
        for wp in request.waypoints
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    comparison = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Compare failed for waypoint {request.waypoints[i].name}: {result}")
            comparison.append({
                "waypoint": {"id": request.waypoints[i].id, "name": request.waypoints[i].name},
                "error": str(result),
            })
        else:
            comparison.append(result)

    total_ms = round((time.time() - t0) * 1000)

    return {
        "comparison": comparison,
        "waypoint_count": len(request.waypoints),
        "total_computation_ms": total_ms,
    }
