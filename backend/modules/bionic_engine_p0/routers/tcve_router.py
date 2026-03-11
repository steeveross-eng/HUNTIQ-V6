"""
ROUTER TCVE — Terrain Calibration Visual Engine
BIONIC V5 ULTIME 300% — Phase d'Optimisation #7

Endpoint: POST /api/v1/bionic/tcve/analyze
Endpoint: GET /api/v1/bionic/tcve/status

Consomme: SSVL + VFE + SSE + WSE/WIV + CME (tous certifies)
source_id dynamique: TCVE_{SPECIES}
"""

import logging
import time
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger("bionic_engine.tcve_router")

router = APIRouter(prefix="/api/v1/bionic/tcve", tags=["BIONIC TCVE Engine"])


class TCVEBounds(BaseModel):
    north: float = Field(..., ge=-90, le=90)
    south: float = Field(..., ge=-90, le=90)
    east: float = Field(..., ge=-180, le=180)
    west: float = Field(..., ge=-180, le=180)


class TCVEAnalyzeRequest(BaseModel):
    bounds: TCVEBounds
    species: str
    layers: Optional[List[str]] = None
    resolution: int = Field(default=60, ge=20, le=120)
    max_zones_per_layer: int = Field(default=4, ge=1, le=20)
    max_corridors: int = Field(default=6, ge=1, le=20)
    base_wind_kmh: float = Field(default=15.0, ge=0, le=120)
    base_direction_deg: float = Field(default=270.0, ge=0, le=360)


@router.post("/analyze")
async def tcve_analyze(request: TCVEAnalyzeRequest):
    """Pipeline: SSE → OSG → CME → WSE → VFE → SSVL → TCVE"""
    from modules.bionic_engine_p0.services.tcve_engine import generate_tcve_composite, get_supported_species
    from modules.bionic_engine_p0.services.sse_engine import generate_sse_composite
    from modules.bionic_engine_p0.services.osg_engine import generate_osg_multi_layer
    from modules.bionic_engine_p0.services.cme_engine import generate_cme_corridors
    from modules.bionic_engine_p0.services.wse_wiv_engine import generate_wind_field
    from modules.bionic_engine_p0.services.vfe_engine import generate_visibility_field
    from modules.bionic_engine_p0.services.ssvl_engine import generate_ssvl_fields

    if request.species not in get_supported_species():
        raise HTTPException(status_code=400, detail=f"Espece '{request.species}' non supportee. Supportees: {get_supported_species()}")

    start = time.time()
    bounds = {"north": request.bounds.north, "south": request.bounds.south, "east": request.bounds.east, "west": request.bounds.west}
    layers = request.layers or ["habitats", "alimentation"]

    sse_data = generate_sse_composite(bounds, request.species, request.resolution)
    osg_data = generate_osg_multi_layer(bounds, request.species, layers, sse_data, request.resolution, request.max_zones_per_layer)
    cme_data = generate_cme_corridors(bounds, request.species, sse_data, osg_data, request.resolution, ["movement", "feeding_transit"], request.max_corridors)
    wse_data = generate_wind_field(bounds, request.species, sse_data, request.resolution, request.base_wind_kmh, request.base_direction_deg)
    vfe_vis_data = generate_visibility_field(sse_data, wse_data, request.species, request.resolution)
    ssvl_fields = generate_ssvl_fields(vfe_vis_data, sse_data, wse_data, request.species, request.resolution)

    result = generate_tcve_composite(bounds, request.species, sse_data, wse_data, ssvl_fields, vfe_vis_data, cme_data["corridors"], request.resolution)

    elapsed_ms = round((time.time() - start) * 1000, 1)

    return {
        "source_id": result["source_id"],
        "species": request.species,
        "bounds": bounds,
        "resolution": request.resolution,
        "stats": result["stats"],
        "corridor_terrain": result["corridor_terrain"],
        "validation": result["validation"],
        "computation_time_ms": elapsed_ms,
        "pipeline_source_ids": {
            "sse": sse_data["source_id"],
            "osg": osg_data["source_id"],
            "cme": cme_data["source_id"],
            "wse": wse_data["source_id"],
            "vfe": f"VFE_{request.species.upper()}",
            "ssvl": f"SSVL_{request.species.upper()}",
            "tcve": result["source_id"],
        },
    }


@router.get("/status")
async def tcve_status():
    from modules.bionic_engine_p0.services.tcve_engine import get_supported_species
    return {
        "module": "TCVE",
        "label": "Terrain Calibration Visual Engine",
        "version": "1.0.0",
        "status": "active",
        "species_supported": get_supported_species(),
        "dependencies": ["SSVL (certified)", "VFE (certified)", "SSE (certified)", "WSE/WIV (certified)", "CME (certified)"],
        "outputs": ["slope_visibility_calibration", "elevation_exposure_field", "aspect_sun_field", "terrain_roughness_field", "terrain_visibility_calibration_field", "corridor_terrain (per-corridor calibration)"],
        "consumers": ["PME", "BMPE", "TFE"],
        "conformity": {"source_id_dynamic": True, "zero_transversality": True, "zero_duplication": True, "backend_truth": True, "all_fields_normalized": True, "species_profile_applied": True},
    }
