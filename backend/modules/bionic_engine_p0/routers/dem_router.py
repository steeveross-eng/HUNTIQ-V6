"""
ROUTER DEM — Digital Elevation Model (OpenTopography)
BIONIC V5 ULTIME 300% — PHASE G+ Real Data

Endpoints:
  POST /api/v1/bionic/dem/fetch        — Fetch DEM data for bounds
  POST /api/v1/bionic/dem/analyze       — Fetch + compute derived fields
  GET  /api/v1/bionic/dem/status        — DEM service status + API key check
"""

import os
import logging
import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger("bionic_engine.dem_router")
router = APIRouter(prefix="/api/v1/bionic/dem", tags=["BIONIC DEM Engine"])

SUPPORTED_DATASETS = ["SRTMGL1", "SRTMGL3", "AW3D30"]


class DEMBounds(BaseModel):
    north: float = Field(..., ge=-90, le=90)
    south: float = Field(..., ge=-90, le=90)
    east: float = Field(..., ge=-180, le=180)
    west: float = Field(..., ge=-180, le=180)


class DEMFetchRequest(BaseModel):
    bounds: DEMBounds
    species: str = Field(default="moose")
    resolution: int = Field(default=60, ge=20, le=120)
    dataset: str = Field(default="SRTMGL1")


@router.post("/fetch")
async def dem_fetch(request: DEMFetchRequest):
    """Fetch raw DEM stats from OpenTopography."""
    from modules.bionic_engine_p0.services.dem_service import fetch_dem_raw

    if request.dataset not in SUPPORTED_DATASETS:
        raise HTTPException(status_code=400, detail=f"Dataset non supporte: {request.dataset}. Supportes: {SUPPORTED_DATASETS}")

    api_key = os.environ.get("OPENTOPOGRAPHY_API_KEY", "")
    if not api_key:
        raise HTTPException(status_code=503, detail="OPENTOPOGRAPHY_API_KEY non configuree")

    bounds = {"north": request.bounds.north, "south": request.bounds.south,
              "east": request.bounds.east, "west": request.bounds.west}

    start = time.time()
    try:
        raw = await fetch_dem_raw(bounds, request.dataset)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=429, detail=str(e))

    if raw is None:
        raise HTTPException(status_code=503, detail="Echec de recuperation DEM")

    elapsed = round((time.time() - start) * 1000, 1)

    return {
        "source_id": f"DEM_{request.species.upper()}",
        "dataset": request.dataset,
        "bounds": bounds,
        "raw_shape": list(raw.shape),
        "elevation_min": round(float(raw.min()), 2),
        "elevation_max": round(float(raw.max()), 2),
        "elevation_mean": round(float(raw.mean()), 2),
        "computation_time_ms": elapsed,
        "status": "success",
    }


@router.post("/analyze")
async def dem_analyze(request: DEMFetchRequest):
    """Fetch DEM + compute slope, aspect, roughness."""
    from modules.bionic_engine_p0.services.dem_service import fetch_dem_composite

    if request.dataset not in SUPPORTED_DATASETS:
        raise HTTPException(status_code=400, detail=f"Dataset non supporte: {request.dataset}")

    api_key = os.environ.get("OPENTOPOGRAPHY_API_KEY", "")
    if not api_key:
        raise HTTPException(status_code=503, detail="OPENTOPOGRAPHY_API_KEY non configuree")

    bounds = {"north": request.bounds.north, "south": request.bounds.south,
              "east": request.bounds.east, "west": request.bounds.west}

    start = time.time()
    try:
        result = await fetch_dem_composite(bounds, request.species, request.resolution, request.dataset)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=429, detail=str(e))

    if result.get("status") == "no_api_key":
        raise HTTPException(status_code=503, detail="OPENTOPOGRAPHY_API_KEY non configuree")

    elapsed = round((time.time() - start) * 1000, 1)

    # Return stats only (not numpy arrays)
    return {
        "source_id": result["source_id"],
        "species": result["species"],
        "dataset": result["dataset"],
        "bounds": result["bounds"],
        "resolution": result["resolution"],
        "raw_shape": result["raw_shape"],
        "stats": result["stats"],
        "status": result["status"],
        "validation": result["validation"],
        "computation_time_ms": elapsed,
    }


@router.get("/status")
async def dem_status():
    api_key = os.environ.get("OPENTOPOGRAPHY_API_KEY", "")
    key_configured = bool(api_key and len(api_key) > 4)
    return {
        "module": "DEM",
        "label": "Digital Elevation Model (OpenTopography)",
        "version": "1.0.0",
        "status": "active" if key_configured else "awaiting_key",
        "api_key_configured": key_configured,
        "provider": "OpenTopography (SRTM/ALOS)",
        "datasets_supported": SUPPORTED_DATASETS,
        "endpoints": [
            "POST /api/v1/bionic/dem/fetch",
            "POST /api/v1/bionic/dem/analyze",
            "GET /api/v1/bionic/dem/status",
        ],
        "consumers": ["TCVE (terrain calibration)", "TFE (thermal flow)"],
        "conformity": {
            "source_id_dynamic": True,
            "zero_transversality": True,
            "backend_truth": True,
            "real_data_source": True,
        },
    }
