"""
ROUTER HABITAT SCORE — Real-time Habitat Quality Grid
BIONIC V5 ULTIME 300% — habitat_score_v1

Endpoint:
  POST /api/v1/bionic/habitat-score/realtime — Pre-computed grid for cursor interpolation
  GET  /api/v1/bionic/habitat-score/status    — Service status

Score normalise 0-100%. Grille pre-calculee pour latence <20ms frontend.
Module isole. 0 impact sur pipeline principal.
"""

import logging
import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger("bionic_engine.habitat_score_router")
router = APIRouter(prefix="/api/v1/bionic/habitat-score", tags=["BIONIC Habitat Score"])

SUPPORTED_SPECIES = ["moose", "deer", "bear", "wild_turkey", "elk"]


class ScoreBounds(BaseModel):
    north: float = Field(..., ge=-90, le=90)
    south: float = Field(..., ge=-90, le=90)
    east: float = Field(..., ge=-180, le=180)
    west: float = Field(..., ge=-180, le=180)


class HabitatScoreRequest(BaseModel):
    bounds: ScoreBounds
    species: str = Field(default="moose")
    resolution: int = Field(default=30, ge=10, le=60)


@router.post("/realtime")
async def habitat_score_realtime(request: HabitatScoreRequest):
    """
    Pre-computed habitat quality grid for real-time cursor interpolation.
    Returns a resolution x resolution grid of scores (0-100%).
    """
    from modules.bionic_engine_p0.services.habitat_score_service import get_habitat_grid

    if request.species not in SUPPORTED_SPECIES:
        raise HTTPException(status_code=400, detail=f"Espece non supportee: {request.species}")

    bounds = {
        "north": request.bounds.north, "south": request.bounds.south,
        "east": request.bounds.east, "west": request.bounds.west,
    }

    start = time.time()
    result = await get_habitat_grid(bounds, request.species, request.resolution)
    elapsed = round((time.time() - start) * 1000, 1)

    return {
        "version": "habitat_score_v1",
        "species": request.species,
        "bounds": bounds,
        "resolution": request.resolution,
        "scores": result["scores"],
        "grid": result["grid"],
        "stats": result["stats"],
        "data_sources": result["data_sources"],
        "computation_time_ms": elapsed,
        "validation": {
            "score_range": "0-100%",
            "shadow_mode": True,
            "zero_impact_on_production": True,
        },
    }


@router.get("/status")
async def habitat_score_status():
    """Service status for Habitat Score."""
    return {
        "module": "HABITAT_SCORE",
        "label": "Score d'Habitat Optimal (Temps Reel)",
        "version": "habitat_score_v1",
        "status": "active",
        "mode": "shadow (non-destructif)",
        "score_range": "0-100%",
        "factors": [
            "micro-relief", "vegetation (NDVI)", "essences forestieres",
            "drainage", "distance eau", "distance anthropique",
            "connectivite ecologique", "pression humaine", "thermique",
            "altitude", "regles espece", "zones fonctionnelles",
        ],
        "species_supported": list(SUPPORTED_SPECIES),
        "endpoints": [
            "POST /api/v1/bionic/habitat-score/realtime",
            "GET /api/v1/bionic/habitat-score/status",
        ],
    }
