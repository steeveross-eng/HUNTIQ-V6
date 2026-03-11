"""
ROUTER WEATHER SHADOW — Open-Meteo Weather Integration
BIONIC V5 ULTIME 300% — PHASE P2 Shadow Mode

Endpoints:
  POST /api/v1/bionic/weather-shadow/fetch     — Fetch real weather data
  POST /api/v1/bionic/weather-shadow/analyze    — Fetch + compute derived fields
  GET  /api/v1/bionic/weather-shadow/cache      — List cached entries
  GET  /api/v1/bionic/weather-shadow/status     — Service status + cache info
"""

import logging
import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger("bionic_engine.weather_shadow_router")
router = APIRouter(prefix="/api/v1/bionic/weather-shadow", tags=["BIONIC Weather Shadow"])

SUPPORTED_SPECIES = ["moose", "deer", "bear", "wild_turkey", "elk"]


class WeatherBounds(BaseModel):
    north: float = Field(..., ge=-90, le=90)
    south: float = Field(..., ge=-90, le=90)
    east: float = Field(..., ge=-180, le=180)
    west: float = Field(..., ge=-180, le=180)


class WeatherRequest(BaseModel):
    bounds: WeatherBounds
    species: str = Field(default="moose")
    resolution: int = Field(default=30, ge=20, le=120)


@router.post("/fetch")
async def weather_fetch(request: WeatherRequest):
    """Fetch raw weather stats from Open-Meteo."""
    from modules.bionic_engine_p0.services.open_meteo_service import fetch_weather_raw, compute_weather_stats

    bounds = {"north": request.bounds.north, "south": request.bounds.south,
              "east": request.bounds.east, "west": request.bounds.west}

    start = time.time()
    raw = await fetch_weather_raw(bounds)
    if raw is None:
        raise HTTPException(status_code=503, detail="Open-Meteo API indisponible")

    stats = compute_weather_stats(raw)
    elapsed = round((time.time() - start) * 1000, 1)

    return {
        "source_id": f"WEATHER_{request.species.upper()}",
        "bounds": bounds,
        "latitude": raw.get("latitude"),
        "longitude": raw.get("longitude"),
        "elevation": raw.get("elevation"),
        "stats": stats,
        "computation_time_ms": elapsed,
        "status": "success",
        "validation": {"data_real": True, "source": "Open-Meteo"},
    }


@router.post("/analyze")
async def weather_analyze(request: WeatherRequest):
    """Fetch weather + compute fields, with cache."""
    from modules.bionic_engine_p0.services.open_meteo_service import fetch_weather_composite
    from modules.bionic_engine_p0.services.weather_cache_service import cache_get, cache_put

    if request.species not in SUPPORTED_SPECIES:
        raise HTTPException(status_code=400, detail=f"Espece non supportee: {request.species}")

    bounds = {"north": request.bounds.north, "south": request.bounds.south,
              "east": request.bounds.east, "west": request.bounds.west}

    start = time.time()
    cache_status = "miss"

    # Try cache
    cached, cache_status = cache_get(bounds, request.resolution)
    if cached is not None and cache_status == "hit":
        elapsed = round((time.time() - start) * 1000, 1)
        return {
            "source_id": cached.get("source_id", f"WEATHER_{request.species.upper()}"),
            "species": request.species,
            "bounds": bounds,
            "resolution": request.resolution,
            "stats": cached.get("stats", {}),
            "cache_status": "hit",
            "computation_time_ms": elapsed,
            "status": "success",
            "validation": {"data_real": True, "source": "Open-Meteo", "cached": True},
        }

    # Fetch from API
    result = await fetch_weather_composite(bounds, request.species, request.resolution)

    if result.get("status") != "success":
        raise HTTPException(status_code=503, detail="Open-Meteo API indisponible")

    # Cache
    try:
        cache_put(bounds, request.resolution, request.species, result)
        cache_status = "stored"
    except Exception as e:
        logger.warning(f"Weather cache store failed: {e}")
        cache_status = "store_failed"

    elapsed = round((time.time() - start) * 1000, 1)

    return {
        "source_id": result["source_id"],
        "species": request.species,
        "bounds": bounds,
        "resolution": request.resolution,
        "provider": result.get("provider"),
        "latitude": result.get("latitude"),
        "longitude": result.get("longitude"),
        "elevation": result.get("elevation"),
        "stats": result["stats"],
        "cache_status": cache_status,
        "computation_time_ms": elapsed,
        "status": "success",
        "validation": result.get("validation", {}),
    }


@router.post("/windfield")
async def weather_windfield(request: WeatherRequest):
    """Generate a vector wind field (u10, v10) for Ventusky-like Canvas 2D rendering."""
    from modules.bionic_engine_p0.services.windfield_service import fetch_and_generate_windfield

    bounds = {"north": request.bounds.north, "south": request.bounds.south,
              "east": request.bounds.east, "west": request.bounds.west}

    start = time.time()
    result = await fetch_and_generate_windfield(bounds, request.resolution)
    elapsed = round((time.time() - start) * 1000, 1)

    field = result["field"]
    return {
        "version": "windfield_v1",
        "source": result["source"],
        "bounds": bounds,
        "resolution": request.resolution,
        "u10": field["u10"],
        "v10": field["v10"],
        "speed": field["speed"],
        "grid": field["grid"],
        "metadata": field["metadata"],
        "computation_time_ms": elapsed,
        "validation": {
            "data_real": result["source"] != "fallback_synthetic",
            "shadow_mode": True,
            "zero_impact_on_production": True,
        },
    }


@router.get("/cache")
async def weather_cache_list():
    from modules.bionic_engine_p0.services.weather_cache_service import cache_stats
    return cache_stats()


@router.get("/status")
async def weather_status():
    from modules.bionic_engine_p0.services.weather_cache_service import cache_stats
    try:
        cs = cache_stats()
    except Exception:
        cs = {"total_entries": 0, "active": 0, "expired": 0}

    return {
        "module": "WEATHER_SHADOW",
        "label": "Open-Meteo Weather Integration (Shadow)",
        "version": "1.0.0",
        "status": "active",
        "provider": "Open-Meteo (api.open-meteo.com)",
        "api_key_required": False,
        "mode": "shadow (non-destructif)",
        "impact_on_production": "zero",
        "enriched_modules": ["WSE_WIV", "TFE"],
        "outputs": ["temperature", "wind_speed", "humidity", "precipitation", "cloud_cover", "surface_pressure"],
        "cache": {
            "enabled": True,
            "backend": "MongoDB",
            "collection": "weather_cache",
            "ttl_hours": 6,
            "total_cached": cs.get("total_entries", 0),
            "active": cs.get("active", 0),
        },
        "endpoints": [
            "POST /api/v1/bionic/weather-shadow/fetch",
            "POST /api/v1/bionic/weather-shadow/analyze",
            "GET /api/v1/bionic/weather-shadow/cache",
            "GET /api/v1/bionic/weather-shadow/status",
        ],
    }
