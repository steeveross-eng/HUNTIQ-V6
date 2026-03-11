"""
ROUTER SSE — Satellite-to-Semantic Engine
BIONIC V5 ULTIME 300% — Phase d'Optimisation #1

Endpoint: POST /api/v1/bionic/sse/analyze
Endpoint: GET /api/v1/bionic/sse/status

source_id dynamique: SSE_{SPECIES}
0 transversalite. 0 duplication. Backend = verite unique.
"""

import logging
import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger("bionic_engine.sse_router")

router = APIRouter(prefix="/api/v1/bionic/sse", tags=["BIONIC SSE Engine"])


class SSEBounds(BaseModel):
    north: float = Field(..., ge=-90, le=90)
    south: float = Field(..., ge=-90, le=90)
    east: float = Field(..., ge=-180, le=180)
    west: float = Field(..., ge=-180, le=180)


class SSEAnalyzeRequest(BaseModel):
    bounds: SSEBounds
    species: str
    resolution: int = Field(default=60, ge=20, le=120)
    include_vectors: bool = True


@router.post("/analyze")
async def sse_analyze(request: SSEAnalyzeRequest):
    """
    Analyse SSE complete: landcover + microrelief + transitions.

    Retourne:
      - source_id dynamique SSE_{SPECIES}
      - Statistiques normalisees pour chaque sous-couche
      - Vecteurs de lisiere (si include_vectors=True)
      - Composite qualite habitat [0,1]

    Sorties consommables par OSG et CME.
    """
    from modules.bionic_engine_p0.services.sse_engine import (
        generate_sse_composite, get_supported_species,
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

    composite_data = generate_sse_composite(bounds, request.species, request.resolution)

    elapsed_ms = round((time.time() - start) * 1000, 1)

    # Build JSON-serializable response (numpy arrays -> summary stats only)
    response = {
        "source_id": composite_data["source_id"],
        "species": composite_data["species"],
        "bounds": composite_data["bounds"],
        "resolution": composite_data["resolution"],
        "stats": composite_data["stats"],
        "computation_time_ms": elapsed_ms,
        "landcover_summary": {
            "forest_density_range": [
                round(float(composite_data["landcover"]["forest_density"].min()), 4),
                round(float(composite_data["landcover"]["forest_density"].max()), 4),
            ],
            "clearing_range": [
                round(float(composite_data["landcover"]["clearing_map"].min()), 4),
                round(float(composite_data["landcover"]["clearing_map"].max()), 4),
            ],
            "conifer_ratio_range": [
                round(float(composite_data["landcover"]["conifer_ratio"].min()), 4),
                round(float(composite_data["landcover"]["conifer_ratio"].max()), 4),
            ],
            "wetland_prob_range": [
                round(float(composite_data["landcover"]["wetland_prob"].min()), 4),
                round(float(composite_data["landcover"]["wetland_prob"].max()), 4),
            ],
        },
        "microrelief_summary": {
            "ridge_range": [
                round(float(composite_data["microrelief"]["ridge_map"].min()), 4),
                round(float(composite_data["microrelief"]["ridge_map"].max()), 4),
            ],
            "valley_range": [
                round(float(composite_data["microrelief"]["valley_map"].min()), 4),
                round(float(composite_data["microrelief"]["valley_map"].max()), 4),
            ],
            "slope_range": [
                round(float(composite_data["microrelief"]["slope_intensity"].min()), 4),
                round(float(composite_data["microrelief"]["slope_intensity"].max()), 4),
            ],
            "plateau_range": [
                round(float(composite_data["microrelief"]["plateau_map"].min()), 4),
                round(float(composite_data["microrelief"]["plateau_map"].max()), 4),
            ],
        },
        "composite_summary": {
            "mean": round(float(composite_data["composite"].mean()), 4),
            "std": round(float(composite_data["composite"].std()), 4),
            "min": round(float(composite_data["composite"].min()), 4),
            "max": round(float(composite_data["composite"].max()), 4),
        },
    }

    if request.include_vectors:
        response["edge_vectors"] = composite_data["edges"]["edge_vectors"]
        response["edge_count"] = composite_data["edges"]["edge_count"]

    logger.info(
        f"SSE analysis for {request.species}: {elapsed_ms}ms, "
        f"composite_mean={composite_data['stats']['composite_mean']}, "
        f"edges={composite_data['edges']['edge_count']}"
    )

    return response


@router.get("/status")
async def sse_status():
    """Statut du module SSE."""
    from modules.bionic_engine_p0.services.sse_engine import get_supported_species

    return {
        "module": "SSE",
        "label": "Satellite-to-Semantic Engine",
        "version": "1.0.0",
        "status": "active",
        "species_supported": get_supported_species(),
        "outputs": [
            "landcover (forest_density, clearing_map, conifer_ratio, wetland_prob)",
            "microrelief (ridge_map, valley_map, slope_intensity, plateau_map)",
            "edge_transitions (edge_intensity, edge_vectors)",
            "composite (habitat quality raster)",
        ],
        "consumers": ["OSG", "CME", "WSE"],
        "conformity": {
            "source_id_dynamic": True,
            "zero_transversality": True,
            "zero_duplication": True,
            "backend_truth": True,
        },
    }
