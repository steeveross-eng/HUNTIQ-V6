"""
ROUTER SHADOW — Full Comparison + Wind Field
BIONIC V5 ULTIME 300% — PHASE P2

Endpoints:
  POST /api/v1/bionic/shadow/full-comparison  — Synthetic vs Real (DEM+Weather)
  POST /api/v1/bionic/weather-shadow/windfield — u10/v10 wind vectors for frontend
  GET  /api/v1/bionic/shadow/status
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger("bionic_engine.shadow_router")
router = APIRouter(prefix="/api/v1/bionic/shadow", tags=["BIONIC Shadow Engine"])

SUPPORTED_SPECIES = ["moose", "deer", "bear", "wild_turkey", "elk"]


class ShadowBounds(BaseModel):
    north: float = Field(..., ge=-90, le=90)
    south: float = Field(..., ge=-90, le=90)
    east: float = Field(..., ge=-180, le=180)
    west: float = Field(..., ge=-180, le=180)


class FullComparisonRequest(BaseModel):
    bounds: ShadowBounds
    species: str
    resolution: int = Field(default=30, ge=20, le=60)


@router.post("/full-comparison")
async def shadow_full_comparison(request: FullComparisonRequest):
    """Compare synthetic pipeline vs full-real (DEM+Weather) pipeline."""
    from modules.bionic_engine_p0.services.full_shadow_service import execute_full_shadow_comparison

    if request.species not in SUPPORTED_SPECIES:
        raise HTTPException(status_code=400, detail=f"Espece non supportee: {request.species}")

    bounds = {"north": request.bounds.north, "south": request.bounds.south,
              "east": request.bounds.east, "west": request.bounds.west}

    result = await execute_full_shadow_comparison(bounds, request.species, request.resolution)
    return result


@router.get("/status")
async def shadow_status():
    from modules.bionic_engine_p0.services.dem_cache_service import cache_stats as dem_stats
    from modules.bionic_engine_p0.services.weather_cache_service import cache_stats as weather_stats

    try:
        ds = dem_stats()
    except Exception:
        ds = {"total_entries": 0, "active": 0}
    try:
        ws = weather_stats()
    except Exception:
        ws = {"total_entries": 0, "active": 0}

    return {
        "module": "SHADOW_ENGINE",
        "label": "Full Shadow Comparison Engine",
        "version": "full_comparison_v1",
        "status": "active",
        "data_sources": {
            "dem": {"provider": "OpenTopography", "cache_entries": ds.get("active", 0)},
            "weather": {"provider": "Open-Meteo", "cache_entries": ws.get("active", 0)},
        },
        "endpoints": [
            "POST /api/v1/bionic/shadow/full-comparison",
            "GET /api/v1/bionic/shadow/status",
        ],
    }
