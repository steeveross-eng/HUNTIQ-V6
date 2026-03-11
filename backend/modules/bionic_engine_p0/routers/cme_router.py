"""
ROUTER CME — Corridor Morphology Engine
BIONIC V5 ULTIME 300% — Phase d'Optimisation #3

Endpoint: POST /api/v1/bionic/cme/generate
Endpoint: GET /api/v1/bionic/cme/status

Consomme: SSE (certifie) + OSG (certifie)
Produit: Corridors GeoJSON avec metadata morphologique
source_id dynamique: CME_{SPECIES}
0 transversalite. 0 duplication. Backend = verite unique.
"""

import logging
import time
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger("bionic_engine.cme_router")

router = APIRouter(prefix="/api/v1/bionic/cme", tags=["BIONIC CME Engine"])


class CMEBounds(BaseModel):
    north: float = Field(..., ge=-90, le=90)
    south: float = Field(..., ge=-90, le=90)
    east: float = Field(..., ge=-180, le=180)
    west: float = Field(..., ge=-180, le=180)


class CMEGenerateRequest(BaseModel):
    bounds: CMEBounds
    species: str
    layers: Optional[List[str]] = None
    resolution: int = Field(default=60, ge=20, le=120)
    max_zones_per_layer: int = Field(default=6, ge=1, le=20)
    corridor_types: Optional[List[str]] = None
    max_corridors: int = Field(default=12, ge=1, le=30)


@router.post("/generate")
async def cme_generate(request: CMEGenerateRequest):
    """
    Generation CME complete: SSE + OSG → cost surface → corridors organiques.

    Pipeline:
      1. SSE composite (terrain semantique)
      2. OSG zones (zones organiques enrichies)
      3. Cost surface construction (vallee=facile, crete=difficile)
      4. Least-cost path entre zones
      5. Chaikin smoothing + jitter → corridors organiques
      6. Metadata morphologique par corridor

    Retourne:
      - source_id dynamique CME_{SPECIES}
      - Corridors GeoJSON LineString avec terrain_context
      - Validation: cost_surface_routed, chaikin_applied, jitter_applied
    """
    from modules.bionic_engine_p0.services.cme_engine import (
        generate_cme_corridors, get_supported_species,
    )
    from modules.bionic_engine_p0.services.sse_engine import generate_sse_composite
    from modules.bionic_engine_p0.services.osg_engine import generate_osg_multi_layer

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

    layers = request.layers
    if layers is None:
        layers = ["habitats", "alimentation", "repos", "corridors"]

    # Step 1: SSE composite
    sse_data = generate_sse_composite(bounds, request.species, request.resolution)

    # Step 2: OSG zones
    osg_data = generate_osg_multi_layer(
        bounds, request.species, layers, sse_data,
        request.resolution, request.max_zones_per_layer,
    )

    # Step 3: CME corridors
    result = generate_cme_corridors(
        bounds, request.species, sse_data, osg_data,
        request.resolution, request.corridor_types, request.max_corridors,
    )

    elapsed_ms = round((time.time() - start) * 1000, 1)

    # Build JSON response (corridors with coordinates)
    corridors_json = []
    for c in result["corridors"]:
        corridors_json.append({
            "corridor_id": c["corridor_id"],
            "corridor_type": c["corridor_type"],
            "geometry": c["geometry"],
            "from_zone": c["from_zone"],
            "to_zone": c["to_zone"],
            "length_m": c["length_m"],
            "width_m": c["width_m"],
            "vertices": c["vertices"],
            "usage_probability": c["usage_probability"],
            "frequency": c["frequency"],
            "terrain_context": c["terrain_context"],
            "validation": c["validation"],
        })

    response = {
        "source_id": result["source_id"],
        "species": result["species"],
        "bounds": result["bounds"],
        "resolution": result["resolution"],
        "corridors": corridors_json,
        "corridor_count": result["corridor_count"],
        "corridor_types_used": result.get("corridor_types_used", []),
        "total_length_m": result.get("total_length_m", 0),
        "validation": result["validation"],
        "sse_source_id": result.get("sse_source_id", ""),
        "osg_source_id": result.get("osg_source_id", ""),
        "computation_time_ms": elapsed_ms,
    }

    logger.info(
        f"CME generation for {request.species}: {elapsed_ms}ms, "
        f"{result['corridor_count']} corridors, "
        f"total_length={result.get('total_length_m', 0)}m"
    )

    return response


@router.get("/status")
async def cme_status():
    """Statut du module CME."""
    from modules.bionic_engine_p0.services.cme_engine import get_supported_species

    return {
        "module": "CME",
        "label": "Corridor Morphology Engine",
        "version": "1.0.0",
        "status": "active",
        "species_supported": get_supported_species(),
        "dependencies": ["SSE (certified)", "OSG (certified)"],
        "outputs": [
            "corridors (GeoJSON LineString with terrain_context)",
            "validation (cost_surface_routed, chaikin, jitter, sse/osg integrated)",
        ],
        "consumers": ["WSE/WIV", "VFE", "SSVL"],
        "conformity": {
            "source_id_dynamic": True,
            "zero_transversality": True,
            "zero_duplication": True,
            "backend_truth": True,
            "chaikin_applied": True,
            "cost_surface_routing": True,
            "sse_integration": True,
            "osg_integration": True,
        },
    }
