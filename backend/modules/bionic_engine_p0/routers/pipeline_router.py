"""
ROUTER PIPELINE — Full Pipeline & Metrics
BIONIC V5 ULTIME 300% — PHASE G

Endpoints:
  POST /api/v1/bionic/pipeline/full-analysis
  POST /api/v1/bionic/pipeline/metrics
  GET  /api/v1/bionic/pipeline/status

Pipeline organique immuable: SSE->OSG->CME->WSE->VFE->SSVL->TCVE->PME->BMPE->TFE
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger("bionic_engine.pipeline_router")
router = APIRouter(prefix="/api/v1/bionic/pipeline", tags=["BIONIC Pipeline Engine"])

SUPPORTED_SPECIES = ["moose", "deer", "bear", "wild_turkey", "elk"]


class PipelineBounds(BaseModel):
    north: float = Field(..., ge=-90, le=90)
    south: float = Field(..., ge=-90, le=90)
    east: float = Field(..., ge=-180, le=180)
    west: float = Field(..., ge=-180, le=180)


class FullAnalysisRequest(BaseModel):
    bounds: PipelineBounds
    species: str
    layers: Optional[List[str]] = None
    resolution: int = Field(default=60, ge=20, le=120)
    max_zones_per_layer: int = Field(default=4, ge=1, le=20)
    max_corridors: int = Field(default=6, ge=1, le=20)
    base_wind_kmh: float = Field(default=15.0, ge=0, le=120)
    base_direction_deg: float = Field(default=270.0, ge=0, le=360)


class MetricsRequest(BaseModel):
    bounds: PipelineBounds
    species: Optional[List[str]] = None
    resolution: int = Field(default=30, ge=20, le=60)


class ComparisonRequest(BaseModel):
    bounds_a: PipelineBounds
    bounds_b: PipelineBounds
    species: str
    resolution: int = Field(default=60, ge=20, le=120)
    layers: Optional[List[str]] = None
    max_zones_per_layer: int = Field(default=4, ge=1, le=20)
    max_corridors: int = Field(default=6, ge=1, le=20)
    base_wind_kmh: float = Field(default=15.0, ge=0, le=120)
    base_direction_deg: float = Field(default=270.0, ge=0, le=360)


@router.post("/full-analysis")
async def pipeline_full_analysis(request: FullAnalysisRequest):
    """Execute the complete 10-module pipeline in strict sequential order."""
    from modules.bionic_engine_p0.services.pipeline_service import execute_full_pipeline

    if request.species not in SUPPORTED_SPECIES:
        raise HTTPException(status_code=400, detail=f"Espece '{request.species}' non supportee. Supportees: {SUPPORTED_SPECIES}")

    bounds = {"north": request.bounds.north, "south": request.bounds.south,
              "east": request.bounds.east, "west": request.bounds.west}

    result = execute_full_pipeline(
        bounds, request.species, request.resolution,
        request.layers, request.max_zones_per_layer, request.max_corridors,
        request.base_wind_kmh, request.base_direction_deg,
    )
    return result


@router.post("/metrics")
async def pipeline_metrics(request: MetricsRequest):
    """Generate global metrics across multiple species for a territory."""
    from modules.bionic_engine_p0.services.pipeline_service import generate_pipeline_metrics

    species_list = request.species or SUPPORTED_SPECIES
    for sp in species_list:
        if sp not in SUPPORTED_SPECIES:
            raise HTTPException(status_code=400, detail=f"Espece '{sp}' non supportee. Supportees: {SUPPORTED_SPECIES}")

    bounds = {"north": request.bounds.north, "south": request.bounds.south,
              "east": request.bounds.east, "west": request.bounds.west}

    result = generate_pipeline_metrics(bounds, species_list, request.resolution)
    return result


@router.post("/comparison")
async def pipeline_comparison(request: ComparisonRequest):
    """Compare two territories side-by-side for a given species."""
    from modules.bionic_engine_p0.services.comparison_service import compare_territories

    if request.species not in SUPPORTED_SPECIES:
        raise HTTPException(status_code=400, detail=f"Espece '{request.species}' non supportee. Supportees: {SUPPORTED_SPECIES}")

    bounds_a = {"north": request.bounds_a.north, "south": request.bounds_a.south,
                "east": request.bounds_a.east, "west": request.bounds_a.west}
    bounds_b = {"north": request.bounds_b.north, "south": request.bounds_b.south,
                "east": request.bounds_b.east, "west": request.bounds_b.west}

    result = compare_territories(
        bounds_a, bounds_b, request.species, request.resolution,
        request.layers, request.max_zones_per_layer, request.max_corridors,
        request.base_wind_kmh, request.base_direction_deg,
    )
    return result


@router.get("/status")
async def pipeline_status():
    return {
        "pipeline": "BIONIC_V5_ULTIME_300",
        "label": "Full Pipeline Orchestrator",
        "version": "1.0.0",
        "status": "active",
        "module_count": 10,
        "pipeline_order": ["SSE", "OSG", "CME", "WSE_WIV", "VFE", "SSVL", "TCVE", "PME", "BMPE", "TFE"],
        "species_supported": SUPPORTED_SPECIES,
        "endpoints": [
            "POST /api/v1/bionic/pipeline/full-analysis",
            "POST /api/v1/bionic/pipeline/metrics",
            "GET /api/v1/bionic/pipeline/status",
        ],
        "conformity": {
            "zero_transversality": True,
            "zero_duplication": True,
            "strict_sequential_order": True,
            "backend_truth": True,
        },
    }
