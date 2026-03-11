"""
ROUTER NDVI SHADOW — Sentinel-2 NDVI Integration (Shadow Mode)
BIONIC V5 ULTIME 300% — PHASE P2 Shadow Mode

Endpoints:
  POST /api/v1/bionic/ndvi-shadow/fetch    — Fetch NDVI data (real or synthetic)
  POST /api/v1/bionic/ndvi-shadow/analyze  — Fetch + analyze with cache
  GET  /api/v1/bionic/ndvi-shadow/cache    — List cached entries
  GET  /api/v1/bionic/ndvi-shadow/status   — Service status

Mode STRICT SHADOW. 0 impact sur pipeline principal.
Versionnement: ndvi_v1
"""

import logging
import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger("bionic_engine.ndvi_shadow_router")
router = APIRouter(prefix="/api/v1/bionic/ndvi-shadow", tags=["BIONIC NDVI Shadow"])

SUPPORTED_SPECIES = ["moose", "deer", "bear", "wild_turkey", "elk"]


class NdviBounds(BaseModel):
    north: float = Field(..., ge=-90, le=90)
    south: float = Field(..., ge=-90, le=90)
    east: float = Field(..., ge=-180, le=180)
    west: float = Field(..., ge=-180, le=180)


class NdviRequest(BaseModel):
    bounds: NdviBounds
    species: str = Field(default="moose")
    resolution: int = Field(default=30, ge=20, le=120)


@router.post("/fetch")
async def ndvi_fetch(request: NdviRequest):
    """Fetch NDVI from Sentinel-2 (or synthetic fallback)."""
    from modules.bionic_engine_p0.services.ndvi_service import fetch_ndvi_composite

    if request.species not in SUPPORTED_SPECIES:
        raise HTTPException(status_code=400, detail=f"Espece non supportee: {request.species}")

    bounds = {
        "north": request.bounds.north, "south": request.bounds.south,
        "east": request.bounds.east, "west": request.bounds.west,
    }

    start = time.time()
    result = await fetch_ndvi_composite(bounds, request.species, request.resolution)
    elapsed = round((time.time() - start) * 1000, 1)

    fields = result.get("fields", {})
    ndvi_field = fields.get("ndvi_field")
    ndvi_list = ndvi_field.tolist() if hasattr(ndvi_field, "tolist") else ndvi_field

    return {
        "source_id": result.get("source_id"),
        "version": "ndvi_v1",
        "species": request.species,
        "bounds": bounds,
        "resolution": request.resolution,
        "source": result.get("source"),
        "image_id": result.get("image_id"),
        "image_date": result.get("image_date"),
        "cloud_cover": result.get("cloud_cover"),
        "stats": result.get("stats", {}),
        "ndvi_field": ndvi_list,
        "stac_info": result.get("stac_info"),
        "reason": result.get("reason"),
        "computation_time_ms": elapsed,
        "status": result.get("status", "unknown"),
        "validation": {
            "data_real": result.get("source") == "sentinel2_real",
            "shadow_mode": True,
            "zero_impact_on_production": True,
        },
    }


@router.post("/analyze")
async def ndvi_analyze(request: NdviRequest):
    """Fetch NDVI with cache support."""
    from modules.bionic_engine_p0.services.ndvi_service import fetch_ndvi_composite
    from modules.bionic_engine_p0.services.ndvi_cache_service import cache_get, cache_put

    if request.species not in SUPPORTED_SPECIES:
        raise HTTPException(status_code=400, detail=f"Espece non supportee: {request.species}")

    bounds = {
        "north": request.bounds.north, "south": request.bounds.south,
        "east": request.bounds.east, "west": request.bounds.west,
    }

    start = time.time()

    cached, cache_status = cache_get(bounds, request.resolution)
    if cached and cache_status == "hit":
        elapsed = round((time.time() - start) * 1000, 1)
        return {
            "source_id": cached.get("source_id"),
            "version": "ndvi_v1",
            "species": request.species,
            "bounds": bounds,
            "resolution": request.resolution,
            "source": cached.get("source"),
            "image_id": cached.get("image_id"),
            "image_date": cached.get("image_date"),
            "stats": cached.get("stats", {}),
            "cache_status": "hit",
            "computation_time_ms": elapsed,
            "status": "success",
            "validation": {
                "data_real": cached.get("source") == "sentinel2_real",
                "shadow_mode": True,
                "zero_impact_on_production": True,
                "cached": True,
            },
        }

    result = await fetch_ndvi_composite(bounds, request.species, request.resolution)

    try:
        cache_put(bounds, request.resolution, request.species, result)
        cache_status = "stored"
    except Exception as e:
        logger.warning(f"NDVI cache store failed: {e}")
        cache_status = "store_failed"

    elapsed = round((time.time() - start) * 1000, 1)

    return {
        "source_id": result.get("source_id"),
        "version": "ndvi_v1",
        "species": request.species,
        "bounds": bounds,
        "resolution": request.resolution,
        "source": result.get("source"),
        "image_id": result.get("image_id"),
        "image_date": result.get("image_date"),
        "cloud_cover": result.get("cloud_cover"),
        "stats": result.get("stats", {}),
        "cache_status": cache_status,
        "computation_time_ms": elapsed,
        "status": result.get("status", "unknown"),
        "validation": {
            "data_real": result.get("source") == "sentinel2_real",
            "shadow_mode": True,
            "zero_impact_on_production": True,
        },
    }


@router.get("/cache")
async def ndvi_cache_list():
    """List all cached NDVI entries."""
    from modules.bionic_engine_p0.services.ndvi_cache_service import cache_stats
    return cache_stats()


@router.get("/status")
async def ndvi_status():
    """Service status for NDVI Shadow integration."""
    from modules.bionic_engine_p0.services.sentinel_oauth_service import check_credentials
    from modules.bionic_engine_p0.services.ndvi_cache_service import cache_stats

    cred_status = await check_credentials()

    try:
        cs = cache_stats()
    except Exception:
        cs = {"total_entries": 0, "active": 0, "expired": 0}

    return {
        "module": "NDVI_SHADOW",
        "label": "Sentinel-2 NDVI Integration (Shadow)",
        "version": "ndvi_v1",
        "status": "active" if cred_status["status"] == "valid" else "awaiting_credentials",
        "credentials": cred_status,
        "provider": "Copernicus Data Space (Sentinel-2 L2A)",
        "mode": "shadow (non-destructif)",
        "impact_on_production": "zero",
        "enriched_modules": ["VFE", "SSVL"],
        "outputs": ["ndvi_field", "vegetation_pct", "dense_vegetation_pct", "bare_soil_pct"],
        "cache": {
            "enabled": True,
            "backend": "MongoDB",
            "collection": "ndvi_cache",
            "ttl_days": 30,
            "total_cached": cs.get("total_entries", 0),
            "active": cs.get("active", 0),
        },
        "endpoints": [
            "POST /api/v1/bionic/ndvi-shadow/fetch",
            "POST /api/v1/bionic/ndvi-shadow/analyze",
            "GET /api/v1/bionic/ndvi-shadow/cache",
            "GET /api/v1/bionic/ndvi-shadow/status",
        ],
    }
