"""
ROUTER BMPE — Behavioral Micro-Patterns Engine
BIONIC V5 ULTIME 300% — Phase d'Optimisation #9

Endpoint: POST /api/v1/bionic/bmpe/analyze
Endpoint: GET /api/v1/bionic/bmpe/status

source_id dynamique: BMPE_{SPECIES}
"""

import logging, time
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger("bionic_engine.bmpe_router")
router = APIRouter(prefix="/api/v1/bionic/bmpe", tags=["BIONIC BMPE Engine"])


class BMPEBounds(BaseModel):
    north: float = Field(..., ge=-90, le=90)
    south: float = Field(..., ge=-90, le=90)
    east: float = Field(..., ge=-180, le=180)
    west: float = Field(..., ge=-180, le=180)

class BMPEAnalyzeRequest(BaseModel):
    bounds: BMPEBounds
    species: str
    layers: Optional[List[str]] = None
    resolution: int = Field(default=60, ge=20, le=120)
    max_zones_per_layer: int = Field(default=4, ge=1, le=20)
    max_corridors: int = Field(default=6, ge=1, le=20)
    base_wind_kmh: float = Field(default=15.0, ge=0, le=120)
    base_direction_deg: float = Field(default=270.0, ge=0, le=360)


@router.post("/analyze")
async def bmpe_analyze(request: BMPEAnalyzeRequest):
    """Pipeline: SSE → OSG → CME → WSE → VFE → SSVL → TCVE → PME → BMPE"""
    from modules.bionic_engine_p0.services.bmpe_engine import generate_bmpe_composite, get_supported_species
    from modules.bionic_engine_p0.services.sse_engine import generate_sse_composite
    from modules.bionic_engine_p0.services.osg_engine import generate_osg_multi_layer
    from modules.bionic_engine_p0.services.cme_engine import generate_cme_corridors
    from modules.bionic_engine_p0.services.wse_wiv_engine import generate_wind_field
    from modules.bionic_engine_p0.services.vfe_engine import generate_visibility_field
    from modules.bionic_engine_p0.services.ssvl_engine import generate_ssvl_fields
    from modules.bionic_engine_p0.services.tcve_engine import generate_tcve_fields
    from modules.bionic_engine_p0.services.pme_engine import generate_pme_fields

    if request.species not in get_supported_species():
        raise HTTPException(status_code=400, detail=f"Espece '{request.species}' non supportee. Supportees: {get_supported_species()}")

    start = time.time()
    bounds = {"north": request.bounds.north, "south": request.bounds.south, "east": request.bounds.east, "west": request.bounds.west}
    layers = request.layers or ["habitats", "alimentation"]

    sse = generate_sse_composite(bounds, request.species, request.resolution)
    osg = generate_osg_multi_layer(bounds, request.species, layers, sse, request.resolution, request.max_zones_per_layer)
    cme = generate_cme_corridors(bounds, request.species, sse, osg, request.resolution, ["movement", "feeding_transit"], request.max_corridors)
    wse = generate_wind_field(bounds, request.species, sse, request.resolution, request.base_wind_kmh, request.base_direction_deg)
    vfe = generate_visibility_field(sse, wse, request.species, request.resolution)
    ssvl = generate_ssvl_fields(vfe, sse, wse, request.species, request.resolution)
    tcve = generate_tcve_fields(sse, wse, ssvl, vfe, request.species, request.resolution)
    pme = generate_pme_fields(sse, wse, ssvl, tcve, bounds, request.species, request.resolution)

    result = generate_bmpe_composite(bounds, request.species, sse, wse, ssvl, tcve, pme, cme["corridors"], request.resolution)
    elapsed_ms = round((time.time() - start) * 1000, 1)

    return {
        "source_id": result["source_id"], "species": request.species, "bounds": bounds,
        "resolution": request.resolution, "stats": result["stats"],
        "corridor_micro_patterns": result["corridor_micro_patterns"],
        "validation": result["validation"], "computation_time_ms": elapsed_ms,
        "pipeline_source_ids": {
            "sse": sse["source_id"], "osg": osg["source_id"], "cme": cme["source_id"],
            "wse": wse["source_id"], "vfe": f"VFE_{request.species.upper()}", "ssvl": f"SSVL_{request.species.upper()}",
            "tcve": f"TCVE_{request.species.upper()}", "pme": f"PME_{request.species.upper()}",
            "bmpe": result["source_id"],
        },
    }


@router.get("/status")
async def bmpe_status():
    from modules.bionic_engine_p0.services.bmpe_engine import get_supported_species
    return {
        "module": "BMPE", "label": "Behavioral Micro-Patterns Engine", "version": "1.0.0", "status": "active",
        "species_supported": get_supported_species(),
        "dependencies": ["PME (certified)", "TCVE (certified)", "SSVL (certified)", "SSE (certified)", "WSE/WIV (certified)", "CME (certified)"],
        "outputs": ["micro_retreat_field", "micro_exploration_field", "hesitation_field", "fine_movement_field", "composite_micro_pattern", "corridor_micro_patterns"],
        "consumers": ["TFE"],
        "conformity": {"source_id_dynamic": True, "zero_transversality": True, "zero_duplication": True, "backend_truth": True, "all_fields_normalized": True, "species_profile_applied": True},
    }
