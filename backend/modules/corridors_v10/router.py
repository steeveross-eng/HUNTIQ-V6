"""
CORRIDORS-V10 — Router API REST
====================================
Endpoints:
  POST /api/v10/corridors/analyze     — Analyse corridors complete (leger)
  POST /api/v10/corridors/analyze-full — Analyse avec GeoJSON (visualisation)
  GET  /api/v10/corridors/multi       — Analyse multi-especes (5 especes)
  GET  /api/v10/corridors/profiles    — Liste des profils especes
  GET  /api/v10/corridors/profile/{species} — Profil detaille 12 parametres
  GET  /api/v10/corridors/documentation — Fiche technique JSON

100% independant. Zero modification des engines existants.
Normes BCE-4X et Steeve-MAX strictement respectees.
"""
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from typing import Optional

from .engine import analyze_corridors, analyze_corridors_full, analyze_multi_species
from .species_profiles import CORRIDOR_PROFILES, SPECIES_LIST, get_profile, PARAM_KEYS
from .documentation import generate_documentation

router = APIRouter(prefix="/api/v10/corridors", tags=["CORRIDORS-V10"])


class CorridorAnalyzeRequest(BaseModel):
    center_lat: float = Field(..., description="Latitude du centre du carre 2km2 existant")
    center_lng: float = Field(..., description="Longitude du centre du carre 2km2 existant")
    species: str = Field("CERF", description="Espece: CERF, ORIGNAL, OURS, DINDON, WAPITI")
    month: int = Field(10, ge=1, le=12, description="Mois (1-12)")
    cell_m: Optional[float] = Field(25.0, ge=10, le=50, description="Taille cellule en metres (25 par defaut)")


@router.post("/analyze")
async def analyze_corridor(req: CorridorAnalyzeRequest):
    """
    Analyse complete des corridors fauniques (version legere).
    Retourne le score, classification, reseau, et validations.
    N'inclut pas les chemins GeoJSON detailles.
    """
    return analyze_corridors(
        center_lat=req.center_lat,
        center_lng=req.center_lng,
        species=req.species,
        month=req.month,
        cell_m=req.cell_m,
    )


@router.post("/analyze-full")
async def analyze_corridor_full(req: CorridorAnalyzeRequest):
    """
    Analyse complete AVEC GeoJSON pour visualisation cartographique.
    Inclut les chemins detailles (LineString) et zones (Point).
    Plus lourd — utiliser pour export/visualisation.
    """
    return analyze_corridors_full(
        center_lat=req.center_lat,
        center_lng=req.center_lng,
        species=req.species,
        month=req.month,
        cell_m=req.cell_m,
    )


@router.get("/multi")
async def analyze_multi(
    lat: float = Query(...),
    lng: float = Query(...),
    month: int = Query(10, ge=1, le=12),
):
    """Analyse corridors multi-especes (5 especes)."""
    return analyze_multi_species(lat, lng, month)


@router.get("/profiles")
async def list_profiles():
    """Liste des profils d'especes supportes avec les 12 parametres."""
    profiles = []
    for key, p in CORRIDOR_PROFILES.items():
        profiles.append({
            "id": key,
            "nom_fr": p["nom_fr"],
            "nom_scientifique": p["nom_scientifique"],
            "style_deplacement": p["style_deplacement"],
            "pente_max_deg": p["pente_max_deg"],
            "largeur_corridor_m": p["largeur_corridor_m"],
            "vitesse_deplacement": p["vitesse_deplacement"],
        })
    return {
        "engine": "CORRIDORS-V10",
        "species_count": len(profiles),
        "parametres_count": 12,
        "profiles": profiles,
    }


@router.get("/profile/{species}")
async def get_species_profile(species: str):
    """Profil detaille d'une espece avec les 12 parametres obligatoires."""
    profile = get_profile(species)
    return {
        "engine": "CORRIDORS-V10",
        "species": species.upper(),
        "profile": {
            "nom_fr": profile["nom_fr"],
            "nom_scientifique": profile["nom_scientifique"],
            "parametres_12": {k: profile[k] for k in PARAM_KEYS},
            "saisonnalite": profile["saisonnalite"],
        },
    }


@router.get("/documentation")
async def get_documentation():
    """Fiche technique complete du moteur CORRIDORS-V10."""
    return generate_documentation()
