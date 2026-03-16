"""
REPOS-V1 — Router API REST
==============================
Endpoints:
  POST /api/v1/repos/analyze — Analyse complète d'un carré 2km²
  GET  /api/v1/repos/profiles — Liste des profils espèces
  GET  /api/v1/repos/profile/{species} — Profil détaillé
  GET  /api/v1/repos/point — Analyse d'un point unique
  GET  /api/v1/repos/multi — Analyse multi-espèces
  GET  /api/v1/repos/documentation — Fiche technique JSON
"""
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from typing import Optional

from .engine import analyze_square, analyze_single_point, analyze_multi_species
from .species_profiles import REPOS_PROFILES, SPECIES_LIST, get_profile
from .documentation import generate_documentation

router = APIRouter(prefix="/api/v1/repos", tags=["REPOS-V1"])


class AnalyzeRequest(BaseModel):
    center_lat: float = Field(..., description="Latitude du centre du carre 2km2 existant")
    center_lng: float = Field(..., description="Longitude du centre du carre 2km2 existant")
    species: str = Field("CERF", description="Espece: CERF, ORIGNAL, OURS, DINDON, WAPITI")
    month: int = Field(10, ge=1, le=12, description="Mois (1-12)")
    sample_step: Optional[int] = Field(5, ge=1, le=20, description="Pas echantillonnage")


@router.post("/analyze")
async def analyze_repos(req: AnalyzeRequest):
    """Analyse repos complète d'un carré 2km² existant."""
    return analyze_square(
        center_lat=req.center_lat,
        center_lng=req.center_lng,
        species=req.species,
        month=req.month,
        sample_step=req.sample_step,
    )


@router.get("/point")
async def analyze_point(
    lat: float = Query(...),
    lng: float = Query(...),
    species: str = Query("CERF"),
    month: int = Query(10, ge=1, le=12),
):
    return analyze_single_point(lat, lng, species, month)


@router.get("/multi")
async def analyze_multi(
    lat: float = Query(...),
    lng: float = Query(...),
    month: int = Query(10, ge=1, le=12),
    sample_step: int = Query(10, ge=1, le=20),
):
    return analyze_multi_species(lat, lng, month, sample_step)


@router.get("/profiles")
async def list_profiles():
    profiles = []
    for key, p in REPOS_PROFILES.items():
        profiles.append({
            "id": key,
            "nom_fr": p["nom_fr"],
            "nom_scientifique": p["nom_scientifique"],
            "repos_pct": p["rythme_circadien"]["repos_pct"],
            "couvert_keys": list(p["couvert"].keys()),
        })
    return {"engine": "REPOS-V1", "species_count": len(profiles), "profiles": profiles}


@router.get("/profile/{species}")
async def get_species_profile(species: str):
    profile = get_profile(species)
    return {"engine": "REPOS-V1", "species": species.upper(), "profile": profile}


@router.get("/documentation")
async def get_documentation():
    return generate_documentation()
