"""
ROUTER FULL SHADOW COMPARISON — DEM + Meteo combines
BIONIC V5 ULTIME 300% — full_comparison_v1

Endpoint:
  POST /api/v1/bionic/shadow/full-comparison — Compare synthetic vs full-real pipeline

Mode: STRICT SHADOW — 0 impact sur predictions actuelles.
Modules certifies: INCHANGES.
"""

import logging
import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger("bionic_engine.full_shadow_comparison")
router = APIRouter(prefix="/api/v1/bionic/shadow", tags=["BIONIC Full Shadow Comparison"])

SUPPORTED_SPECIES = ["moose", "deer", "bear", "wild_turkey", "elk"]


class ComparisonBounds(BaseModel):
    north: float = Field(..., ge=-90, le=90)
    south: float = Field(..., ge=-90, le=90)
    east: float = Field(..., ge=-180, le=180)
    west: float = Field(..., ge=-180, le=180)


class FullComparisonRequest(BaseModel):
    bounds: ComparisonBounds
    species: str = Field(default="moose")
    resolution: int = Field(default=30, ge=20, le=60)


@router.post("/full-comparison")
async def full_shadow_comparison(request: FullComparisonRequest):
    """
    Compare le pipeline synthetique complet vs le pipeline enrichi
    avec TOUTES les donnees reelles (DEM + Meteo injectees simultanement).

    Mesure l'impact combine sur TCVE, TFE et BMPE.
    Mode STRICT SHADOW — aucun impact sur la production.
    """
    from modules.bionic_engine_p0.services.full_shadow_service import execute_full_shadow_comparison

    if request.species not in SUPPORTED_SPECIES:
        raise HTTPException(status_code=400, detail=f"Espece non supportee: {request.species}")

    bounds = {
        "north": request.bounds.north,
        "south": request.bounds.south,
        "east": request.bounds.east,
        "west": request.bounds.west,
    }

    start = time.time()
    try:
        result = await execute_full_shadow_comparison(bounds, request.species, request.resolution)
    except Exception as e:
        logger.error(f"Full shadow comparison failed: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la comparaison: {str(e)}")

    router_ms = round((time.time() - start) * 1000, 1)
    result["router_overhead_ms"] = round(router_ms - result.get("total_computation_time_ms", 0), 1)

    logger.info(
        f"Full shadow comparison complete: species={request.species}, "
        f"dem={result['data_sources']['dem']}, weather={result['data_sources']['weather']}, "
        f"total={router_ms}ms"
    )

    return result


@router.get("/full-comparison/status")
async def full_comparison_status():
    """Statut du service de comparaison complete Shadow."""
    return {
        "module": "FULL_SHADOW_COMPARISON",
        "label": "Full Shadow Comparison (DEM + Meteo)",
        "version": "full_comparison_v1",
        "status": "active",
        "mode": "shadow (non-destructif)",
        "impact_on_production": "zero",
        "data_sources": ["DEM (OpenTopography)", "Meteo (Open-Meteo)"],
        "compared_modules": ["TCVE", "TFE", "BMPE"],
        "endpoints": [
            "POST /api/v1/bionic/shadow/full-comparison",
            "GET /api/v1/bionic/shadow/full-comparison/status",
        ],
        "validation": {
            "certified_modules_unmodified": True,
            "shadow_mode": True,
            "zero_impact_on_production": True,
        },
    }
