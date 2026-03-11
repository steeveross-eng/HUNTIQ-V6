"""Wildlife Behavior Engine Router - PLAN MAITRE
FastAPI router for wildlife behavior modeling.

Version: 1.0.0
API Prefix: /api/v1/wildlife
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime
from .service import WildlifeBehaviorService

router = APIRouter(prefix="/api/v1/wildlife", tags=["Wildlife Behavior Engine"])

_service = WildlifeBehaviorService()


@router.get("/")
async def wildlife_engine_info():
    """Get wildlife behavior engine information"""
    stats = await _service.get_stats()
    
    return {
        "module": "wildlife_behavior_engine",
        "version": "1.0.0",
        "phase": 4,
        "description": "Modélisation du comportement animalier",
        "status": "operational",
        "features": [
            "Patterns de déplacement par espèce",
            "Zones d'alimentation/repos",
            "Périodes d'activité",
            "Comportement saisonnier",
            "Prédiction de présence"
        ],
        "statistics": stats
    }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "module": "wildlife_behavior_engine", "version": "1.0.0"}


@router.get("/species")
async def list_species():
    """List all tracked species"""
    species = await _service.get_all_species()
    return {
        "success": True,
        "total": len(species),
        "species": [s.model_dump() for s in species]
    }


@router.get("/species/{species}")
async def get_species_info(species: str):
    """Get detailed species profile"""
    profile = await _service.get_species_info(species)
    
    if not profile:
        raise HTTPException(status_code=404, detail=f"Espèce non trouvée: {species}")
    
    return {"success": True, "species": profile.model_dump()}


@router.get("/patterns/{species}")
async def get_movement_patterns(
    species: str,
    pattern_type: str = Query("daily", regex="^(daily|seasonal|weather_driven)$")
):
    """Get movement patterns for a species"""
    patterns = await _service.get_movement_patterns(species, pattern_type)
    return {"success": True, "patterns": patterns.model_dump()}


@router.get("/predict-activity")
async def predict_activity(
    species: str = Query(...),
    lat: Optional[float] = Query(None),
    lng: Optional[float] = Query(None),
    date: Optional[str] = Query(None, description="ISO date format"),
    temperature: Optional[float] = Query(None),
    wind_speed: Optional[float] = Query(None)
):
    """Predict species activity level"""
    coords = None
    if lat is not None and lng is not None:
        coords = {"lat": lat, "lng": lng}
    
    dt = None
    if date:
        try:
            dt = datetime.fromisoformat(date.replace('Z', '+00:00'))
        except ValueError:
            pass
    
    weather = None
    if temperature is not None or wind_speed is not None:
        weather = {"temperature": temperature, "wind_speed": wind_speed}
    
    prediction = await _service.predict_activity(
        species=species,
        date=dt,
        coordinates=coords,
        weather=weather
    )
    
    return {"success": True, "prediction": prediction.model_dump()}


@router.get("/seasonal/{species}/{season}")
async def get_seasonal_behavior(species: str, season: str):
    """Get seasonal behavior patterns"""
    behavior = await _service.get_seasonal_behavior(species, season)
    return {"success": True, "behavior": behavior.model_dump()}


@router.get("/presence")
async def predict_presence(
    lat: float = Query(...),
    lng: float = Query(...),
    radius_km: float = Query(1.0, ge=0.1, le=10),
    species: Optional[str] = Query(None, description="Comma-separated species list")
):
    """Predict wildlife presence in an area"""
    species_list = None
    if species:
        species_list = [s.strip() for s in species.split(",")]
    
    prediction = await _service.predict_presence(lat, lng, radius_km, species_list)
    return {"success": True, "presence": prediction.model_dump()}
