"""
BIONIC ENGINE - Hunt Plan Analyzer Router
PHASE P1-FINAL — Endpoint d'Analyse du Plan de Chasse

Expose l'endpoint POST /api/v1/bionic/analyze_hunt_plan
pour l'analyse consolidée du potentiel de chasse.

Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
"""

import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from modules.bionic_engine_p0.services.hunt_plan_analyzer_service import (
    get_hunt_plan_analyzer_service
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Hunt Plan Analyzer"])


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class BoundsInput(BaseModel):
    """Zone géographique pour l'analyse."""
    north: float = Field(..., ge=-90, le=90, description="Latitude nord")
    south: float = Field(..., ge=-90, le=90, description="Latitude sud")
    east: float = Field(..., ge=-180, le=180, description="Longitude est")
    west: float = Field(..., ge=-180, le=180, description="Longitude ouest")


class HuntPlanRequest(BaseModel):
    """Requête d'analyse du plan de chasse."""
    bounds: BoundsInput = Field(..., description="Zone géographique à analyser")
    species: List[str] = Field(
        default=["moose"],
        description="Espèces à analyser (moose, deer, bear, wild_turkey, elk)"
    )
    time_range: str = Field(
        default="24h",
        description="Plage temporelle (24h, 72h, 7d)"
    )
    hotspot_types: Optional[List[str]] = Field(
        default=None,
        description="Types de hotspots (activity_peak, feeding_zone, rut_zone, thermal_refuge)"
    )
    min_score_threshold: int = Field(
        default=70,
        ge=0,
        le=100,
        description="Score minimum pour inclusion d'un hotspot"
    )
    include_scored_hotspots: bool = Field(
        default=True,
        description="Inclure les hotspots scorés dans la réponse"
    )
    target_datetime: Optional[str] = Field(
        default=None,
        description="Date/heure cible ISO 8601 (défaut: maintenant)"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "bounds": {
                        "north": 46.95,
                        "south": 46.85,
                        "east": -71.15,
                        "west": -71.35
                    },
                    "species": ["moose", "deer"],
                    "time_range": "24h",
                    "hotspot_types": ["activity_peak", "feeding_zone"],
                    "min_score_threshold": 70,
                    "include_scored_hotspots": True
                }
            ]
        }
    }


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.post("/analyze_hunt_plan")
async def analyze_hunt_plan(request: HuntPlanRequest):
    """
    Analyse complète du plan de chasse.
    
    Orchestre les services BIONIC pour produire une analyse consolidée:
    - Génération des hotspots organiques (HotspotService)
    - Récupération des conditions météo (WeatherService)
    - Calcul des scores comportementaux dynamiques (DynamicScoringService)
    
    **Réponse**:
    - Synthèse par espèce avec scores moyens et meilleurs hotspots
    - Fenêtres optimales d'observation
    - Recommandations contextuelles
    - Hotspots scorés avec géométrie (si include_scored_hotspots=true)
    
    **Qualité de l'analyse**:
    - `full`: Météo réelle active, tous les services opérationnels
    - `partial`: Météo inactive (OWM_API_KEY absent), scores de base
    - `minimal`: Données insuffisantes
    """
    try:
        service = get_hunt_plan_analyzer_service()
        
        # Parser la date/heure si fournie
        target_dt = None
        if request.target_datetime:
            try:
                target_dt = datetime.fromisoformat(
                    request.target_datetime.replace('Z', '+00:00')
                )
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Format de date invalide. Utilisez ISO 8601."
                )
        
        # Exécuter l'analyse
        analysis = await service.analyze_hunt_plan(
            bounds={
                "north": request.bounds.north,
                "south": request.bounds.south,
                "east": request.bounds.east,
                "west": request.bounds.west
            },
            species=request.species,
            time_range=request.time_range,
            hotspot_types=request.hotspot_types,
            min_score_threshold=request.min_score_threshold,
            include_scored_hotspots=request.include_scored_hotspots,
            target_datetime=target_dt
        )
        
        return analysis.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur analyse plan de chasse: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'analyse: {str(e)}"
        )


@router.get("/analyze_hunt_plan/status")
async def get_analyzer_status():
    """
    Retourne le statut du service d'analyse.
    
    Vérifie la disponibilité des services sous-jacents:
    - HotspotService
    - WeatherService
    - DynamicScoringService
    """
    try:
        from modules.bionic_engine_p0.services.weather_service import get_weather_service
        
        weather_service = get_weather_service()
        
        return {
            "status": "operational",
            "services": {
                "hotspot_service": "active",
                "weather_service": weather_service.status.value,
                "scoring_service": "active",
                "hunt_plan_analyzer": "active"
            },
            "weather_info": weather_service.get_status_info(),
            "supported_species": ["moose", "deer", "bear", "wild_turkey", "elk"],
            "supported_time_ranges": ["24h", "72h", "7d"],
            "supported_hotspot_types": [
                "activity_peak",
                "feeding_zone", 
                "rut_zone",
                "thermal_refuge",
                "water_source",
                "predation_risk"
            ],
            "version": "P1-FINAL-1.0"
        }
    except Exception as e:
        logger.error(f"Erreur statut analyzer: {e}")
        return {
            "status": "error",
            "error": str(e)
        }
