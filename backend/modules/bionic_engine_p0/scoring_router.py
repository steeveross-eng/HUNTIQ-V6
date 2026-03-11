"""
BIONIC ENGINE - Dynamic Scoring Router
PHASE P1-SCORE — Endpoints de Scoring Dynamique

Endpoints API pour le système de scoring dynamique BIONIC.

Endpoints:
- POST /api/v1/bionic/score/calculate — Calcul score pour une position
- POST /api/v1/bionic/score/hotspot — Score pour un hotspot spécifique
- POST /api/v1/bionic/score/batch — Scores pour plusieurs hotspots
- GET /api/v1/bionic/score/weights — Configuration des pondérations

Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import logging

from .services.dynamic_scoring_service import (
    get_scoring_service,
    WeatherInputs,
    SCORE_WEIGHTS,
    SPECIES_THRESHOLDS
)
from .services.weather_service import get_weather_service, ServiceStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/bionic/score", tags=["Scoring - P1-SCORE"])


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class ScoreRequest(BaseModel):
    """Requête de calcul de score."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude")
    species: str = Field("moose", description="Espèce cible")
    include_weather: bool = Field(True, description="Inclure données météo live")
    target_datetime: Optional[str] = Field(None, description="Date/heure cible (ISO format)")


class HotspotScoreRequest(BaseModel):
    """Requête de score pour un hotspot."""
    hotspot_id: str = Field(..., description="ID du hotspot")
    base_score: float = Field(..., ge=0, le=100, description="Score de base")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    species: str = Field("moose")
    include_weather: bool = Field(True)


class BatchScoreRequest(BaseModel):
    """Requête batch pour plusieurs hotspots."""
    hotspots: List[HotspotScoreRequest] = Field(..., max_length=50)
    include_weather: bool = Field(True)


class ManualWeatherInput(BaseModel):
    """Données météo manuelles pour le scoring."""
    temperature: float = Field(0, description="Température °C")
    humidity: int = Field(50, ge=0, le=100, description="Humidité %")
    pressure: float = Field(1013, description="Pression hPa")
    wind_speed: float = Field(0, ge=0, description="Vent km/h")
    precipitation: float = Field(0, ge=0, description="Précipitations mm")
    pressure_trend: str = Field("stable", description="Tendance: rising, falling, stable")
    moon_phase: float = Field(0.5, ge=0, le=1, description="Phase lunaire 0-1")


class ScoreWithManualWeatherRequest(BaseModel):
    """Requête avec données météo manuelles."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    species: str = Field("moose")
    weather: ManualWeatherInput


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/weights")
async def get_score_weights():
    """
    Retourne la configuration des pondérations du score.
    
    Returns:
        Pondérations et seuils par espèce
    """
    return {
        "success": True,
        "data": {
            "weights": SCORE_WEIGHTS,
            "species_available": list(SPECIES_THRESHOLDS.keys()),
            "species_thresholds": {
                species: {
                    "temp_optimal": thresholds["temp_optimal"],
                    "wind_optimal_max": thresholds["wind_optimal_max"],
                    "activity_peak_hours": thresholds["activity_peak_hours"],
                    "feeding_hours": thresholds["feeding_hours"]
                }
                for species, thresholds in SPECIES_THRESHOLDS.items()
            }
        }
    }


@router.post("/calculate")
async def calculate_score(request: ScoreRequest):
    """
    Calcule le score dynamique pour une position.
    
    Le score intègre automatiquement les données météo si disponibles.
    
    Returns:
        Score dynamique avec tous les composants
    """
    scoring_service = get_scoring_service()
    weather_inputs = None
    weather_status = "not_requested"
    
    # Récupérer les données météo si demandé
    if request.include_weather:
        weather_service = get_weather_service()
        
        if weather_service.is_active:
            try:
                weather_response = await weather_service.get_weather(
                    latitude=request.latitude,
                    longitude=request.longitude,
                    include_forecast=False,
                    include_behavior=True
                )
                
                if weather_response.status == ServiceStatus.ACTIVE and weather_response.current:
                    weather_inputs = WeatherInputs(
                        temperature=weather_response.current.temperature,
                        feels_like=weather_response.current.feels_like,
                        humidity=weather_response.current.humidity,
                        pressure=weather_response.current.pressure,
                        wind_speed=weather_response.current.wind_speed,
                        wind_gust=weather_response.current.wind_gust,
                        precipitation=weather_response.current.precipitation_1h + weather_response.current.snow_1h,
                        cloud_cover=weather_response.current.cloud_cover,
                        visibility=weather_response.current.visibility,
                        pressure_trend=weather_response.behavior_factors.pressure_trend if weather_response.behavior_factors else "stable",
                        moon_phase=weather_response.daily_7d[0].moon_phase if weather_response.daily_7d else 0.5,
                        sunrise_hour=weather_response.current.sunrise.hour if weather_response.current.sunrise else 6,
                        sunset_hour=weather_response.current.sunset.hour if weather_response.current.sunset else 18
                    )
                    weather_status = "active"
                else:
                    weather_status = "error"
            except Exception as e:
                logger.warning(f"Erreur récupération météo: {e}")
                weather_status = "error"
        else:
            weather_status = "inactive"
    
    # Parser la date cible
    target_dt = None
    if request.target_datetime:
        try:
            target_dt = datetime.fromisoformat(request.target_datetime.replace('Z', '+00:00'))
        except ValueError:
            pass
    
    # Calculer le score
    score = scoring_service.calculate_dynamic_score(
        latitude=request.latitude,
        longitude=request.longitude,
        species=request.species,
        weather_inputs=weather_inputs,
        target_datetime=target_dt
    )
    
    return {
        "success": True,
        "weather_status": weather_status,
        "data": score.to_dict()
    }


@router.post("/calculate/manual")
async def calculate_score_manual_weather(request: ScoreWithManualWeatherRequest):
    """
    Calcule le score avec des données météo manuelles.
    
    Utile pour les simulations et tests.
    
    Returns:
        Score dynamique calculé avec les données fournies
    """
    scoring_service = get_scoring_service()
    
    weather_inputs = WeatherInputs(
        temperature=request.weather.temperature,
        humidity=request.weather.humidity,
        pressure=request.weather.pressure,
        wind_speed=request.weather.wind_speed,
        precipitation=request.weather.precipitation,
        pressure_trend=request.weather.pressure_trend,
        moon_phase=request.weather.moon_phase
    )
    
    score = scoring_service.calculate_dynamic_score(
        latitude=request.latitude,
        longitude=request.longitude,
        species=request.species,
        weather_inputs=weather_inputs
    )
    
    return {
        "success": True,
        "weather_status": "manual",
        "data": score.to_dict()
    }


@router.post("/hotspot")
async def calculate_hotspot_score(request: HotspotScoreRequest):
    """
    Calcule le score final d'un hotspot.
    
    Combine le score de base avec le score dynamique (60% base + 40% dynamique).
    
    Returns:
        Score hotspot avec détail des composants
    """
    scoring_service = get_scoring_service()
    weather_inputs = None
    weather_status = "not_requested"
    
    if request.include_weather:
        weather_service = get_weather_service()
        
        if weather_service.is_active:
            try:
                weather_response = await weather_service.get_weather(
                    latitude=request.latitude,
                    longitude=request.longitude,
                    include_forecast=False,
                    include_behavior=True
                )
                
                if weather_response.status == ServiceStatus.ACTIVE and weather_response.current:
                    weather_inputs = WeatherInputs(
                        temperature=weather_response.current.temperature,
                        feels_like=weather_response.current.feels_like,
                        humidity=weather_response.current.humidity,
                        pressure=weather_response.current.pressure,
                        wind_speed=weather_response.current.wind_speed,
                        precipitation=weather_response.current.precipitation_1h,
                        pressure_trend=weather_response.behavior_factors.pressure_trend if weather_response.behavior_factors else "stable",
                    )
                    weather_status = "active"
            except Exception as e:
                logger.warning(f"Erreur récupération météo: {e}")
                weather_status = "error"
        else:
            weather_status = "inactive"
    
    hotspot_score = scoring_service.calculate_hotspot_score(
        hotspot_id=request.hotspot_id,
        base_score=request.base_score,
        latitude=request.latitude,
        longitude=request.longitude,
        species=request.species,
        weather_inputs=weather_inputs
    )
    
    return {
        "success": True,
        "weather_status": weather_status,
        "data": hotspot_score.to_dict()
    }


@router.post("/batch")
async def calculate_batch_scores(request: BatchScoreRequest):
    """
    Calcule les scores pour plusieurs hotspots en batch.
    
    Optimise les appels météo en utilisant un seul appel par zone.
    
    Returns:
        Liste des scores de hotspots
    """
    if not request.hotspots:
        return {
            "success": True,
            "data": {
                "hotspots": [],
                "count": 0
            }
        }
    
    scoring_service = get_scoring_service()
    weather_service = get_weather_service()
    
    # Récupérer la météo une seule fois pour le centre approximatif
    weather_inputs = None
    weather_status = "not_requested"
    
    if request.include_weather and weather_service.is_active:
        # Utiliser le premier hotspot comme référence météo
        ref = request.hotspots[0]
        try:
            weather_response = await weather_service.get_weather(
                latitude=ref.latitude,
                longitude=ref.longitude,
                include_forecast=False,
                include_behavior=True
            )
            
            if weather_response.status == ServiceStatus.ACTIVE and weather_response.current:
                weather_inputs = WeatherInputs(
                    temperature=weather_response.current.temperature,
                    feels_like=weather_response.current.feels_like,
                    humidity=weather_response.current.humidity,
                    pressure=weather_response.current.pressure,
                    wind_speed=weather_response.current.wind_speed,
                    precipitation=weather_response.current.precipitation_1h,
                    pressure_trend=weather_response.behavior_factors.pressure_trend if weather_response.behavior_factors else "stable",
                )
                weather_status = "active"
        except Exception as e:
            logger.warning(f"Erreur récupération météo batch: {e}")
            weather_status = "error"
    elif request.include_weather:
        weather_status = "inactive"
    
    # Calculer les scores
    results = []
    for hs in request.hotspots:
        try:
            hotspot_score = scoring_service.calculate_hotspot_score(
                hotspot_id=hs.hotspot_id,
                base_score=hs.base_score,
                latitude=hs.latitude,
                longitude=hs.longitude,
                species=hs.species,
                weather_inputs=weather_inputs
            )
            results.append(hotspot_score.to_dict())
        except Exception as e:
            logger.error(f"Erreur calcul score hotspot {hs.hotspot_id}: {e}")
            results.append({
                "hotspot_id": hs.hotspot_id,
                "error": str(e)
            })
    
    # Statistiques
    valid_scores = [r for r in results if "final_score" in r]
    avg_score = sum(r["final_score"] for r in valid_scores) / len(valid_scores) if valid_scores else 0
    
    return {
        "success": True,
        "weather_status": weather_status,
        "data": {
            "hotspots": results,
            "count": len(results),
            "statistics": {
                "average_final_score": round(avg_score, 1),
                "valid_count": len(valid_scores),
                "error_count": len(results) - len(valid_scores)
            }
        }
    }


@router.get("/species/{species_name}")
async def get_species_info(species_name: str):
    """
    Retourne les informations de scoring pour une espèce.
    
    Returns:
        Seuils et paramètres de scoring pour l'espèce
    """
    if species_name not in SPECIES_THRESHOLDS:
        raise HTTPException(
            status_code=404,
            detail=f"Espèce '{species_name}' non trouvée. Espèces disponibles: {list(SPECIES_THRESHOLDS.keys())}"
        )
    
    thresholds = SPECIES_THRESHOLDS[species_name]
    
    return {
        "success": True,
        "data": {
            "species": species_name,
            "thresholds": {
                "temperature": {
                    "optimal_range": thresholds["temp_optimal"],
                    "stress_cold": thresholds["temp_stress_cold"],
                    "stress_heat": thresholds["temp_stress_heat"]
                },
                "wind": {
                    "optimal_max": thresholds["wind_optimal_max"],
                    "stress": thresholds["wind_stress"]
                },
                "precipitation_tolerance": thresholds["precip_tolerance"],
                "pressure_sensitivity": thresholds["pressure_sensitivity"]
            },
            "activity": {
                "peak_hours": thresholds["activity_peak_hours"],
                "feeding_hours": thresholds["feeding_hours"]
            }
        }
    }
