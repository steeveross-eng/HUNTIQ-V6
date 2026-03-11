"""
BIONIC ENGINE - Weather Router
PHASE P1-ENV — Endpoints Météorologiques

Endpoints API pour les données météorologiques OpenWeatherMap.

Endpoints:
- GET /api/v1/bionic/weather/status — Statut du service
- POST /api/v1/bionic/weather/current — Météo actuelle
- POST /api/v1/bionic/weather/forecast — Prévisions
- POST /api/v1/bionic/weather/behavior — Analyse comportementale

Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
import logging

from .services.weather_service import (
    get_weather_service,
    ServiceStatus
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/bionic/weather", tags=["Weather - P1-ENV"])


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class LocationRequest(BaseModel):
    """Requête avec position géographique."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude")


class WeatherRequest(LocationRequest):
    """Requête météo complète."""
    include_forecast: bool = Field(True, description="Inclure les prévisions")
    include_behavior: bool = Field(True, description="Inclure l'analyse comportementale")


class ForecastRequest(LocationRequest):
    """Requête prévisions."""
    hours: int = Field(24, ge=1, le=168, description="Nombre d'heures (24, 72, 168)")


class BehaviorRequest(LocationRequest):
    """Requête analyse comportementale."""
    species: str = Field("moose", description="Espèce cible")


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/status")
async def get_weather_status():
    """
    Retourne le statut du service météo.
    
    Returns:
        Status du service et configuration
    """
    service = get_weather_service()
    return service.get_status_info()


@router.post("/current")
async def get_current_weather(request: LocationRequest):
    """
    Récupère la météo actuelle pour une position.
    
    Returns:
        Données météo actuelles (température, humidité, vent, etc.)
    """
    service = get_weather_service()
    response = await service.get_current_weather(
        latitude=request.latitude,
        longitude=request.longitude
    )
    
    if response.status == ServiceStatus.INACTIVE:
        return {
            "success": False,
            "status": "inactive",
            "message": "Service météo inactif. Clé API OWM_API_KEY non configurée dans .env",
            "data": None
        }
    
    if response.status == ServiceStatus.ERROR:
        return {
            "success": False,
            "status": "error",
            "message": response.error_message,
            "data": None
        }
    
    return {
        "success": True,
        "status": "active",
        "data": response.current.to_dict() if response.current else None,
        "metadata": {
            "cached": response.cached,
            "cache_expires": response.cache_expires.isoformat() if response.cache_expires else None
        }
    }


@router.post("/forecast")
async def get_weather_forecast(request: ForecastRequest):
    """
    Récupère les prévisions météo.
    
    Args:
        hours: Durée des prévisions (24, 72, ou 168 pour 7 jours)
        
    Returns:
        Prévisions horaires et journalières
    """
    service = get_weather_service()
    response = await service.get_forecast(
        latitude=request.latitude,
        longitude=request.longitude,
        hours=request.hours
    )
    
    if response.status == ServiceStatus.INACTIVE:
        return {
            "success": False,
            "status": "inactive",
            "message": "Service météo inactif. Clé API OWM_API_KEY non configurée dans .env",
            "data": None
        }
    
    if response.status == ServiceStatus.ERROR:
        return {
            "success": False,
            "status": "error",
            "message": response.error_message,
            "data": None
        }
    
    # Filtrer selon la durée demandée
    if request.hours <= 24:
        hourly = [h.to_dict() for h in response.hourly_24h]
    elif request.hours <= 72:
        hourly = [h.to_dict() for h in response.hourly_72h[:request.hours]]
    else:
        hourly = [h.to_dict() for h in response.hourly_72h]
    
    return {
        "success": True,
        "status": "active",
        "data": {
            "current": response.current.to_dict() if response.current else None,
            "hourly": hourly,
            "daily": [d.to_dict() for d in response.daily_7d]
        },
        "metadata": {
            "hours_requested": request.hours,
            "hours_available": len(hourly),
            "days_available": len(response.daily_7d),
            "cached": response.cached
        }
    }


@router.post("/behavior")
async def get_weather_behavior(request: BehaviorRequest):
    """
    Analyse comportementale basée sur la météo.
    
    Calcule les facteurs d'activité, alimentation et mouvement
    en fonction des conditions météorologiques actuelles et prévues.
    
    Returns:
        Facteurs comportementaux et recommandations
    """
    service = get_weather_service()
    result = await service.get_behavior_analysis(
        latitude=request.latitude,
        longitude=request.longitude,
        species=request.species
    )
    
    if result.get("status") == "inactive":
        return {
            "success": False,
            "status": "inactive",
            "message": "Service météo inactif. Clé API OWM_API_KEY non configurée dans .env",
            "data": None
        }
    
    if result.get("status") == "error":
        return {
            "success": False,
            "status": "error",
            "message": result.get("error"),
            "data": None
        }
    
    return {
        "success": True,
        "status": "active",
        "species": result.get("species"),
        "data": {
            "current_conditions": result.get("current_conditions"),
            "behavior_factors": result.get("factors")
        }
    }


@router.post("/complete")
async def get_complete_weather(request: WeatherRequest):
    """
    Récupère toutes les données météo en une seule requête.
    
    Returns:
        Météo actuelle, prévisions et analyse comportementale
    """
    service = get_weather_service()
    response = await service.get_weather(
        latitude=request.latitude,
        longitude=request.longitude,
        include_forecast=request.include_forecast,
        include_behavior=request.include_behavior
    )
    
    if response.status == ServiceStatus.INACTIVE:
        return {
            "success": False,
            "status": "inactive",
            "message": "Service météo inactif. Clé API OWM_API_KEY non configurée dans .env",
            "data": None
        }
    
    if response.status == ServiceStatus.ERROR:
        return {
            "success": False,
            "status": "error",
            "message": response.error_message,
            "data": None
        }
    
    return {
        "success": True,
        "status": "active",
        "data": response.to_dict()
    }
