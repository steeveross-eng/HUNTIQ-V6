"""
ROUTER VFE — Visual Fusion Engine
BIONIC V5 ULTIME 300% — Phase d'Optimisation #5

Endpoint: POST /api/v1/bionic/vfe/analyze
Endpoint: GET /api/v1/bionic/vfe/status

Consomme: SSE + OSG + CME + WSE/WIV (tous certifies)
Produit: Champ visuel fusionne par espece
source_id dynamique: VFE_{SPECIES}
0 transversalite. 0 duplication. Backend = verite unique.
"""

import logging
import time
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger("bionic_engine.vfe_router")

router = APIRouter(prefix="/api/v1/bionic/vfe", tags=["BIONIC VFE Engine"])


class VFEBounds(BaseModel):
    north: float = Field(..., ge=-90, le=90)
    south: float = Field(..., ge=-90, le=90)
    east: float = Field(..., ge=-180, le=180)
    west: float = Field(..., ge=-180, le=180)


class VFEAnalyzeRequest(BaseModel):
    bounds: VFEBounds
    species: str
    layers: Optional[List[str]] = None
    resolution: int = Field(default=60, ge=20, le=120)
    max_zones_per_layer: int = Field(default=4, ge=1, le=20)
    max_corridors: int = Field(default=6, ge=1, le=20)
    base_wind_kmh: float = Field(default=15.0, ge=0, le=120)
    base_direction_deg: float = Field(default=270.0, ge=0, le=360)


@router.post("/analyze")
async def vfe_analyze(request: VFEAnalyzeRequest):
    """
    Analyse VFE complete: SSE + WSE → visibility field → corridor + zone enrichment.

    Pipeline:
      1. SSE composite (terrain)
      2. OSG zones (organic shapes)
      3. CME corridors (morphological paths)
      4. WSE wind field (for visibility modulation)
      5. VFE: visibility_field, cover_opacity, exposure_gradient, flight_line
      6. Corridor visibility analysis + zone visibility enrichment
    """
    from modules.bionic_engine_p0.services.vfe_engine import (
        generate_vfe_composite, get_supported_species,
    )
    from modules.bionic_engine_p0.services.sse_engine import generate_sse_composite
    from modules.bionic_engine_p0.services.osg_engine import generate_osg_multi_layer
    from modules.bionic_engine_p0.services.cme_engine import generate_cme_corridors
    from modules.bionic_engine_p0.services.wse_wiv_engine import generate_wind_field

    if request.species not in get_supported_species():
        raise HTTPException(
            status_code=400,
            detail=f"Espece '{request.species}' non supportee. Supportees: {get_supported_species()}",
        )

    start = time.time()

    bounds = {
        "north": request.bounds.north,
        "south": request.bounds.south,
        "east": request.bounds.east,
        "west": request.bounds.west,
    }

    layers = request.layers or ["habitats", "alimentation"]

    # Pipeline: SSE → OSG → CME → WSE → VFE
    sse_data = generate_sse_composite(bounds, request.species, request.resolution)

    osg_data = generate_osg_multi_layer(
        bounds, request.species, layers, sse_data,
        request.resolution, request.max_zones_per_layer,
    )

    cme_data = generate_cme_corridors(
        bounds, request.species, sse_data, osg_data,
        request.resolution, ["movement", "feeding_transit"], request.max_corridors,
    )

    wse_data = generate_wind_field(
        bounds, request.species, sse_data, request.resolution,
        request.base_wind_kmh, request.base_direction_deg,
    )

    # VFE composite
    vfe_result = generate_vfe_composite(
        bounds, request.species, sse_data, wse_data,
        cme_data["corridors"], osg_data, request.resolution,
    )

    elapsed_ms = round((time.time() - start) * 1000, 1)

    response = {
        "source_id": vfe_result["source_id"],
        "species": request.species,
        "bounds": bounds,
        "resolution": request.resolution,
        "stats": vfe_result["stats"],
        "corridor_visibility": vfe_result["corridor_visibility"],
        "zone_visibility": vfe_result["zone_visibility"],
        "validation": vfe_result["validation"],
        "computation_time_ms": elapsed_ms,
        "pipeline_source_ids": {
            "sse": sse_data["source_id"],
            "osg": osg_data["source_id"],
            "cme": cme_data["source_id"],
            "wse": wse_data["source_id"],
            "vfe": vfe_result["source_id"],
        },
    }

    logger.info(
        f"VFE for {request.species}: {elapsed_ms}ms, "
        f"vis_mean={vfe_result['stats']['mean_visibility']}, "
        f"corridors_analyzed={len(vfe_result['corridor_visibility'])}"
    )

    return response


@router.get("/status")
async def vfe_status():
    """Statut du module VFE."""
    from modules.bionic_engine_p0.services.vfe_engine import get_supported_species

    return {
        "module": "VFE",
        "label": "Visual Fusion Engine",
        "version": "1.0.0",
        "status": "active",
        "species_supported": get_supported_species(),
        "dependencies": ["SSE (certified)", "OSG (certified)", "CME (certified)", "WSE/WIV (certified)"],
        "outputs": [
            "visibility_field (overall visibility quality)",
            "cover_opacity (visual concealment)",
            "exposure_gradient (directional exposure)",
            "flight_line_field (escape route quality)",
            "corridor_visibility (per-corridor visual analysis)",
            "zone_visibility (per-zone visual enrichment)",
        ],
        "consumers": ["SSVL", "TCVE", "PME"],
        "conformity": {
            "source_id_dynamic": True,
            "zero_transversality": True,
            "zero_duplication": True,
            "backend_truth": True,
            "sse_integration": True,
            "osg_integration": True,
            "cme_integration": True,
            "wse_integration": True,
            "all_fields_normalized": True,
        },
    }
