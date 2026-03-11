"""
ROUTER OSG — Organic Shape Generator
BIONIC V5 ULTIME 300% — Phase d'Optimisation #2

Endpoint: POST /api/v1/bionic/osg/generate
Endpoint: GET /api/v1/bionic/osg/status

Consomme: SSE (certifie)
Produit: Zones organiques GeoJSON avec metadata SSE enrichie
source_id dynamique: OSG_{SPECIES}
0 transversalite. 0 duplication. Backend = verite unique.
"""

import logging
import time
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger("bionic_engine.osg_router")

router = APIRouter(prefix="/api/v1/bionic/osg", tags=["BIONIC OSG Engine"])


class OSGBounds(BaseModel):
    north: float = Field(..., ge=-90, le=90)
    south: float = Field(..., ge=-90, le=90)
    east: float = Field(..., ge=-180, le=180)
    west: float = Field(..., ge=-180, le=180)


class OSGGenerateRequest(BaseModel):
    bounds: OSGBounds
    species: str
    layers: Optional[List[str]] = None
    resolution: int = Field(default=60, ge=20, le=120)
    max_zones_per_layer: int = Field(default=8, ge=1, le=20)


@router.post("/generate")
async def osg_generate(request: OSGGenerateRequest):
    """
    Generation OSG complete: SSE + behavioral raster → zones organiques enrichies.

    Pipeline:
      1. Genere le composite SSE pour le territoire et l'espece
      2. Pour chaque couche: raster comportemental + modulation SSE
      3. Extraction blob → Chaikin 2x+ → jitter → validation
      4. Enrichissement metadata SSE par zone

    Retourne:
      - source_id dynamique OSG_{SPECIES}
      - Zones par couche avec sse_context (forest, edge, relief)
      - Validation compactness < 0.85
      - Statistiques de generation
    """
    from modules.bionic_engine_p0.services.osg_engine import (
        generate_osg_multi_layer, get_supported_species,
    )
    from modules.bionic_engine_p0.services.sse_engine import (
        generate_sse_composite,
    )
    from modules.bionic_engine_p0.services.behavioral_rasterizer import (
        get_supported_layers,
    )

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
        layers = get_supported_layers()

    # Step 1: Generate SSE composite (certified module)
    sse_data = generate_sse_composite(bounds, request.species, request.resolution)

    # Step 2: Generate OSG zones modulated by SSE
    result = generate_osg_multi_layer(
        bounds, request.species, layers, sse_data,
        request.resolution, request.max_zones_per_layer,
    )

    elapsed_ms = round((time.time() - start) * 1000, 1)

    # Build JSON response
    zones_response = {}
    for layer_id, zones in result["zones_by_layer"].items():
        zones_response[layer_id] = [
            {
                "area_m2": z["area_m2"],
                "compactness": z["compactness"],
                "centroid": z["centroid"],
                "vertices": z["vertices"],
                "sse_context": z["sse_context"],
                "coordinates_count": len(z["coordinates"]),
            }
            for z in zones
        ]

    response = {
        "source_id": result["source_id"],
        "species": result["species"],
        "bounds": result["bounds"],
        "resolution": result["resolution"],
        "layers_processed": result["layers_processed"],
        "total_zones": result["total_zones"],
        "zones_by_layer": zones_response,
        "validation": result["validation"],
        "rejected_total": result["rejected_total"],
        "computation_time_ms": elapsed_ms,
        "sse_source_id": sse_data["source_id"],
    }

    logger.info(
        f"OSG generation for {request.species}: {elapsed_ms}ms, "
        f"{result['total_zones']} zones across {result['layers_processed']} layers, "
        f"compactness_valid={result['validation']['all_compactness_below_085']}"
    )

    return response


@router.get("/status")
async def osg_status():
    """Statut du module OSG."""
    from modules.bionic_engine_p0.services.osg_engine import get_supported_species

    return {
        "module": "OSG",
        "label": "Organic Shape Generator",
        "version": "1.0.0",
        "status": "active",
        "species_supported": get_supported_species(),
        "dependencies": ["SSE (certified)"],
        "outputs": [
            "zones_by_layer (GeoJSON-ready with SSE context)",
            "validation (compactness, chaikin, sse_modulation)",
        ],
        "consumers": ["CME", "VFE", "SSVL"],
        "conformity": {
            "source_id_dynamic": True,
            "zero_transversality": True,
            "zero_duplication": True,
            "backend_truth": True,
            "chaikin_minimum_2x": True,
            "compactness_max_085": True,
            "sse_integration": True,
        },
    }
