"""
ALIMENTATION-V2 — Router API REST
====================================
Endpoint: POST /api/v2/alimentation/analyze
Conforme BCE-4X. Aucune modification géométrique.
"""
from fastapi import APIRouter
from pydantic import BaseModel, Field

from .engine import analyze_alimentation_v2, SPECIES_LIST

router = APIRouter(prefix="/api/v2/alimentation", tags=["ALIMENTATION-V2"])


class AlimentationV2Request(BaseModel):
    center_lat: float = Field(..., description="Latitude du centre")
    center_lng: float = Field(..., description="Longitude du centre")
    species: str = Field("CERF", description="Espèce: CERF, ORIGNAL, OURS, WAPITI, DINDON")
    month: int = Field(10, ge=1, le=12, description="Mois (1-12)")
    max_salines: int = Field(4, ge=1, le=4, description="Nombre max de salines (1-4)")


@router.post("/analyze")
async def analyze(req: AlimentationV2Request):
    """Analyse alimentaire V2 complète: terrain + salines + nutrition."""
    result = analyze_alimentation_v2(
        center_lat=req.center_lat,
        center_lng=req.center_lng,
        species=req.species,
        month=req.month,
        max_salines=req.max_salines,
    )
    return result


@router.get("/species")
async def list_species():
    """Liste des espèces supportées."""
    return {"species": SPECIES_LIST}
