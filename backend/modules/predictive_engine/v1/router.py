"""Predictive Engine Router

FastAPI router for hunting predictions and activity forecasts.

Version: 1.0.0
API Prefix: /api/v1/predictive
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import date, datetime
from typing import Optional
import json
from zoneinfo import ZoneInfo

from .service import PredictiveService
from modules.legal_time_engine.v1.models import LocationInput

router = APIRouter(prefix="/api/v1/predictive", tags=["Predictive Engine"])

# Initialize service
_service = PredictiveService()


@router.get("/")
async def predictive_engine_info():
    """Get predictive engine information"""
    return {
        "module": "predictive_engine",
        "version": "1.0.0",
        "description": "Prédiction de succès de chasse et prévisions d'activité",
        "features": [
            "Prédiction de probabilité de succès",
            "Analyse des facteurs d'influence",
            "Périodes optimales de chasse",
            "Timeline d'activité par espèce",
            "Intégration avec les heures légales"
        ],
        "supported_species": list(_service.SPECIES_PATTERNS.keys()),
        "default_location": {
            "name": "Québec, QC",
            "latitude": 46.8139,
            "longitude": -71.2080
        }
    }


@router.get("/success")
async def predict_success(
    species: str = Query("deer", description="Espèce ciblée"),
    date_str: Optional[str] = Query(None, alias="date", description="Date YYYY-MM-DD"),
    lat: float = Query(46.8139, description="Latitude"),
    lng: float = Query(-71.2080, description="Longitude"),
    weather: Optional[str] = Query(None, description="Données météo JSON")
):
    """
    Predict hunting success probability.
    
    Returns a complete prediction with:
    - Success probability (0-100%)
    - Confidence level
    - Influencing factors
    - Optimal hunting times
    - Recommendation
    """
    # Parse date
    if date_str:
        try:
            target_date = date.fromisoformat(date_str)
        except ValueError:
            raise HTTPException(status_code=400, detail="Format de date invalide. Utilisez YYYY-MM-DD")
    else:
        target_date = date.today()
    
    # Parse weather if provided
    weather_data = None
    if weather:
        try:
            weather_data = json.loads(weather)
        except json.JSONDecodeError:
            pass  # Ignore invalid JSON
    
    location = LocationInput(latitude=lat, longitude=lng, timezone="America/Toronto")
    
    try:
        prediction = _service.predict_hunting_success(
            species=species,
            target_date=target_date,
            location=location,
            weather=weather_data
        )
        
        return {
            "success": True,
            "species": species,
            "date": target_date.isoformat(),
            "location": {
                "latitude": lat,
                "longitude": lng
            },
            "prediction": {
                "success_probability": prediction.success_probability,
                "confidence": prediction.confidence,
                "factors": [
                    {
                        "name": f.name,
                        "impact": f.impact,
                        "score": f.score,
                        "description": f.description
                    }
                    for f in prediction.factors
                ],
                "optimal_times": [
                    {
                        "period": t.period,
                        "time": t.time,
                        "score": t.score,
                        "is_legal": t.is_legal
                    }
                    for t in prediction.optimal_times
                ],
                "recommendation": prediction.recommendation
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de prédiction: {str(e)}")


@router.get("/activity")
async def get_activity(
    species: str = Query("deer", description="Espèce ciblée"),
    lat: float = Query(46.8139, description="Latitude"),
    lng: float = Query(-71.2080, description="Longitude")
):
    """
    Get current activity level for a species.
    
    Returns the current activity level and peak hunting times.
    """
    location = LocationInput(latitude=lat, longitude=lng, timezone="America/Toronto")
    
    try:
        tz = ZoneInfo("America/Toronto")
        now = datetime.now(tz)
        
        activity = _service.get_activity_level(
            species=species,
            target_datetime=now,
            location=location
        )
        
        return {
            "success": True,
            "species": species,
            "current_time": now.strftime("%H:%M"),
            "activity": {
                "level": activity.level,
                "score": activity.score,
                "peak_times": activity.peak_times
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@router.get("/factors")
async def get_factors(
    species: str = Query("deer", description="Espèce ciblée"),
    date_str: Optional[str] = Query(None, alias="date", description="Date YYYY-MM-DD")
):
    """
    Get detailed success factors for a species and date.
    
    Returns all factors that influence hunting success.
    """
    if date_str:
        try:
            target_date = date.fromisoformat(date_str)
        except ValueError:
            raise HTTPException(status_code=400, detail="Format de date invalide")
    else:
        target_date = date.today()
    
    try:
        factors = _service.get_success_factors(species=species, target_date=target_date)
        
        # Calculate overall score
        weights = [0.25, 0.20, 0.15, 0.20, 0.20]
        overall = int(sum(f.score * w for f, w in zip(factors, weights)))
        
        return {
            "success": True,
            "species": species,
            "date": target_date.isoformat(),
            "overall_score": overall,
            "factors": [
                {
                    "name": f.name,
                    "impact": f.impact,
                    "score": f.score,
                    "description": f.description
                }
                for f in factors
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@router.get("/timeline")
async def get_timeline(
    species: str = Query("deer", description="Espèce ciblée"),
    date_str: Optional[str] = Query(None, alias="date", description="Date YYYY-MM-DD"),
    lat: float = Query(46.8139, description="Latitude"),
    lng: float = Query(-71.2080, description="Longitude")
):
    """
    Get hourly activity timeline for a species.
    
    Shows activity levels for each hour, indicating legal hunting hours.
    """
    if date_str:
        try:
            target_date = date.fromisoformat(date_str)
        except ValueError:
            raise HTTPException(status_code=400, detail="Format de date invalide")
    else:
        target_date = date.today()
    
    location = LocationInput(latitude=lat, longitude=lng, timezone="America/Toronto")
    
    try:
        timeline = _service.get_activity_timeline(
            species=species,
            target_date=target_date,
            location=location
        )
        
        # Get legal window for reference
        legal_window = _service.legal_time_service.get_legal_hunting_window(target_date, location)
        
        return {
            "success": True,
            "species": species,
            "date": target_date.isoformat(),
            "legal_window": {
                "start": legal_window.start_time.strftime("%H:%M"),
                "end": legal_window.end_time.strftime("%H:%M")
            },
            "timeline": [
                {
                    "hour": t.hour,
                    "time": f"{t.hour:02d}:00",
                    "activity_level": t.activity_level,
                    "is_legal": t.is_legal,
                    "light_condition": t.light_condition
                }
                for t in timeline
            ],
            "peak_hours": [
                t for t in timeline 
                if t.activity_level >= 70 and t.is_legal
            ][:3]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@router.get("/optimal-times")
async def get_optimal_times(
    species: str = Query("deer", description="Espèce ciblée"),
    date_str: Optional[str] = Query(None, alias="date", description="Date YYYY-MM-DD"),
    lat: float = Query(46.8139, description="Latitude"),
    lng: float = Query(-71.2080, description="Longitude")
):
    """
    Get optimal hunting times for a species.
    
    Returns the best time slots ranked by expected success.
    """
    if date_str:
        try:
            target_date = date.fromisoformat(date_str)
        except ValueError:
            raise HTTPException(status_code=400, detail="Format de date invalide")
    else:
        target_date = date.today()
    
    location = LocationInput(latitude=lat, longitude=lng, timezone="America/Toronto")
    
    try:
        prediction = _service.predict_hunting_success(
            species=species,
            target_date=target_date,
            location=location
        )
        
        return {
            "success": True,
            "species": species,
            "date": target_date.isoformat(),
            "times": [
                {
                    "period": t.period,
                    "time": t.time,
                    "score": t.score,
                    "is_legal": t.is_legal
                }
                for t in prediction.optimal_times
            ],
            "best_time": {
                "period": prediction.optimal_times[0].period,
                "time": prediction.optimal_times[0].time,
                "score": prediction.optimal_times[0].score
            } if prediction.optimal_times else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@router.get("/forecast/{species}")
async def get_forecast(
    species: str,
    days: int = Query(7, ge=1, le=14, description="Nombre de jours"),
    lat: float = Query(46.8139, description="Latitude"),
    lng: float = Query(-71.2080, description="Longitude")
):
    """
    Get multi-day activity forecast for a species.
    
    Returns daily predictions for the specified number of days.
    """
    location = LocationInput(latitude=lat, longitude=lng, timezone="America/Toronto")
    
    try:
        forecasts = []
        for i in range(days):
            target_date = date.today() + __import__('datetime').timedelta(days=i)
            
            prediction = _service.predict_hunting_success(
                species=species,
                target_date=target_date,
                location=location
            )
            
            activity = _service.get_activity_level(
                species=species,
                target_datetime=datetime.combine(target_date, __import__('datetime').time(7, 0)),
                location=location
            )
            
            forecasts.append({
                "date": target_date.isoformat(),
                "day_name": target_date.strftime("%A"),
                "success_probability": prediction.success_probability,
                "activity_level": activity.level,
                "best_time": prediction.optimal_times[0].time if prediction.optimal_times else None,
                "recommendation": prediction.recommendation
            })
        
        return {
            "success": True,
            "species": species,
            "days": days,
            "forecast": forecasts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")
