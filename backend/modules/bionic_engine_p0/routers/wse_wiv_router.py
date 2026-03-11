"""
ROUTER WSE/WIV — Wind/Weather Scoring Engine + Wind Impact Vector
BIONIC V5 ULTIME 300% — Phase d'Optimisation #4

Endpoint: POST /api/v1/bionic/wse-wiv/analyze
Endpoint: GET /api/v1/bionic/wse-wiv/status

Consomme: SSE (certifie) + CME (certifie)
Produit: Wind field + corridor wind impact
source_id dynamique: WSE_{SPECIES} + WIV_{SPECIES}
0 transversalite. 0 duplication. Backend = verite unique.
"""

import logging
import time
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger("bionic_engine.wse_wiv_router")

router = APIRouter(prefix="/api/v1/bionic/wse-wiv", tags=["BIONIC WSE/WIV Engine"])


class WBounds(BaseModel):
    north: float = Field(..., ge=-90, le=90)
    south: float = Field(..., ge=-90, le=90)
    east: float = Field(..., ge=-180, le=180)
    west: float = Field(..., ge=-180, le=180)


class WSEWIVAnalyzeRequest(BaseModel):
    bounds: WBounds
    species: str
    layers: Optional[List[str]] = None
    resolution: int = Field(default=60, ge=20, le=120)
    max_zones_per_layer: int = Field(default=4, ge=1, le=20)
    max_corridors: int = Field(default=6, ge=1, le=20)
    base_wind_kmh: float = Field(default=15.0, ge=0, le=120)
    base_direction_deg: float = Field(default=270.0, ge=0, le=360)


@router.post("/analyze")
async def wse_wiv_analyze(request: WSEWIVAnalyzeRequest):
    """
    Analyse WSE/WIV complete: SSE → wind field + CME corridors → wind impact.

    Pipeline:
      1. SSE composite (terrain semantique)
      2. OSG zones (pour CME)
      3. CME corridors (pour WIV)
      4. WSE: wind field module par terrain SSE
      5. WIV: wind impact sur corridors CME

    Retourne:
      - WSE: wind stats, shelter map summary, wind score
      - WIV: per-corridor wind impact (exposure, shelter, turbulence, class)
      - source_id WSE_{SPECIES} + WIV_{SPECIES}
    """
    from modules.bionic_engine_p0.services.wse_wiv_engine import (
        generate_wse_wiv_composite, get_supported_species,
    )
    from modules.bionic_engine_p0.services.sse_engine import generate_sse_composite
    from modules.bionic_engine_p0.services.osg_engine import generate_osg_multi_layer
    from modules.bionic_engine_p0.services.cme_engine import generate_cme_corridors

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

    # Step 1: SSE
    sse_data = generate_sse_composite(bounds, request.species, request.resolution)

    # Step 2: OSG (for CME input)
    osg_data = generate_osg_multi_layer(
        bounds, request.species, layers, sse_data,
        request.resolution, request.max_zones_per_layer,
    )

    # Step 3: CME corridors
    cme_data = generate_cme_corridors(
        bounds, request.species, sse_data, osg_data,
        request.resolution, ["movement", "feeding_transit"], request.max_corridors,
    )

    # Step 4+5: WSE + WIV
    composite = generate_wse_wiv_composite(
        bounds, request.species, sse_data,
        cme_data["corridors"], request.resolution,
        request.base_wind_kmh, request.base_direction_deg,
    )

    elapsed_ms = round((time.time() - start) * 1000, 1)

    wse = composite["wse"]
    wiv = composite["wiv"]

    # Wind field summary (no raw numpy in response)
    wind_field_summary = {
        "wind_speed_range": [
            round(float(wse["wind_speed"].min()), 4),
            round(float(wse["wind_speed"].max()), 4),
        ],
        "gust_range": [
            round(float(wse["gust_field"].min()), 4),
            round(float(wse["gust_field"].max()), 4),
        ],
        "shelter_range": [
            round(float(wse["shelter_map"].min()), 4),
            round(float(wse["shelter_map"].max()), 4),
        ],
        "wind_score_range": [
            round(float(wse["wind_score"].min()), 4),
            round(float(wse["wind_score"].max()), 4),
        ],
    }

    # WIV corridor impacts
    wiv_corridors = []
    for c in wiv["corridors"]:
        wiv_corridors.append({
            "corridor_id": c["corridor_id"],
            "corridor_type": c["corridor_type"],
            "wind_impact": c["wind_impact"],
            "sample_count": c["sample_count"],
        })

    response = {
        "wse_source_id": wse["source_id"],
        "wiv_source_id": wiv["source_id"],
        "species": request.species,
        "bounds": bounds,
        "resolution": request.resolution,
        "wse_stats": wse["stats"],
        "wind_field_summary": wind_field_summary,
        "wiv_corridors": wiv_corridors,
        "wiv_corridor_count": wiv["corridor_count"],
        "wiv_validation": wiv["validation"],
        "computation_time_ms": elapsed_ms,
        "pipeline_source_ids": {
            "sse": sse_data["source_id"],
            "osg": osg_data["source_id"],
            "cme": cme_data["source_id"],
            "wse": wse["source_id"],
            "wiv": wiv["source_id"],
        },
    }

    logger.info(
        f"WSE/WIV for {request.species}: {elapsed_ms}ms, "
        f"wind_mean={wse['stats']['mean_wind_speed']}, "
        f"corridors_analyzed={wiv['corridor_count']}"
    )

    return response


@router.get("/status")
async def wse_wiv_status():
    """Statut du module WSE/WIV."""
    from modules.bionic_engine_p0.services.wse_wiv_engine import get_supported_species

    return {
        "module": "WSE/WIV",
        "label": "Wind/Weather Scoring Engine + Wind Impact Vector",
        "version": "1.0.0",
        "status": "active",
        "species_supported": get_supported_species(),
        "dependencies": ["SSE (certified)", "CME (certified)"],
        "outputs": [
            "WSE: wind_field (speed, direction, gust, shelter, wind_score)",
            "WIV: per-corridor wind impact (exposure, shelter, turbulence, class, direction_vector)",
        ],
        "consumers": ["VFE", "SSVL", "TCVE"],
        "conformity": {
            "source_id_dynamic": True,
            "zero_transversality": True,
            "zero_duplication": True,
            "backend_truth": True,
            "sse_integration": True,
            "cme_integration": True,
            "vectors_normalized": True,
        },
    }
