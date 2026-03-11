"""Legal Time Engine Router

FastAPI router for legal hunting time calculations.

Version: 1.0.0
API Prefix: /api/v1/legal-time
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import date, datetime
from typing import Optional
from zoneinfo import ZoneInfo

from .service import LegalTimeService
from .models import LocationInput

router = APIRouter(prefix="/api/v1/legal-time", tags=["Legal Time Engine"])

# Initialize service
_service = LegalTimeService()


@router.get("/")
async def legal_time_engine_info():
    """Get legal time engine information"""
    return {
        "module": "legal_time_engine",
        "version": "1.0.0",
        "description": "Calcul des heures légales de chasse basé sur le lever/coucher du soleil",
        "regulations": {
            "jurisdiction": "Québec, Canada",
            "rule": "30 minutes avant le lever du soleil jusqu'à 30 minutes après le coucher",
            "source": "Règlement sur la chasse du Québec"
        },
        "default_location": {
            "name": "Québec, QC",
            "latitude": 46.8139,
            "longitude": -71.2080,
            "timezone": "America/Toronto"
        },
        "features": [
            "Calcul du lever/coucher du soleil",
            "Fenêtre de chasse légale",
            "Périodes de chasse recommandées",
            "Prévisions multi-jours",
            "Vérification de légalité en temps réel"
        ]
    }


@router.get("/sun-times")
async def get_sun_times(
    date_str: Optional[str] = Query(None, alias="date", description="Date au format YYYY-MM-DD"),
    lat: float = Query(46.8139, description="Latitude"),
    lng: float = Query(-71.2080, description="Longitude"),
    timezone: str = Query("America/Toronto", description="Timezone")
):
    """
    Get sunrise and sunset times for a specific date and location.
    
    Returns:
        Sunrise, sunset, dawn, and dusk times
    """
    # Parse date
    if date_str:
        try:
            target_date = date.fromisoformat(date_str)
        except ValueError:
            raise HTTPException(status_code=400, detail="Format de date invalide. Utilisez YYYY-MM-DD")
    else:
        target_date = date.today()
    
    location = LocationInput(latitude=lat, longitude=lng, timezone=timezone)
    
    try:
        sun_times = _service.get_sun_times(target_date, location)
        
        return {
            "success": True,
            "date": target_date.isoformat(),
            "location": {
                "latitude": lat,
                "longitude": lng,
                "timezone": timezone
            },
            "sun_times": {
                "sunrise": sun_times.sunrise.strftime("%H:%M"),
                "sunset": sun_times.sunset.strftime("%H:%M"),
                "dawn": sun_times.dawn.strftime("%H:%M"),
                "dusk": sun_times.dusk.strftime("%H:%M"),
                "day_length_hours": round(sun_times.day_length_minutes / 60, 1)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de calcul: {str(e)}")


@router.get("/legal-window")
async def get_legal_window(
    date_str: Optional[str] = Query(None, alias="date", description="Date au format YYYY-MM-DD"),
    lat: float = Query(46.8139, description="Latitude"),
    lng: float = Query(-71.2080, description="Longitude"),
    timezone: str = Query("America/Toronto", description="Timezone")
):
    """
    Get the legal hunting window for a specific date.
    
    Quebec regulations: 30 min before sunrise to 30 min after sunset.
    
    Returns:
        Legal start/end times and current status
    """
    if date_str:
        try:
            target_date = date.fromisoformat(date_str)
        except ValueError:
            raise HTTPException(status_code=400, detail="Format de date invalide. Utilisez YYYY-MM-DD")
    else:
        target_date = date.today()
    
    location = LocationInput(latitude=lat, longitude=lng, timezone=timezone)
    
    try:
        legal_window = _service.get_legal_hunting_window(target_date, location)
        
        return {
            "success": True,
            "date": target_date.isoformat(),
            "location": {
                "latitude": lat,
                "longitude": lng,
                "timezone": timezone
            },
            "legal_window": {
                "start_time": legal_window.start_time.strftime("%H:%M"),
                "end_time": legal_window.end_time.strftime("%H:%M"),
                "duration_hours": round(legal_window.duration_minutes / 60, 1),
                "sunrise": legal_window.sunrise.strftime("%H:%M"),
                "sunset": legal_window.sunset.strftime("%H:%M")
            },
            "status": {
                "is_currently_legal": legal_window.is_currently_legal,
                "current_status": legal_window.current_status,
                "next_legal_start": legal_window.next_legal_start.isoformat() if legal_window.next_legal_start else None
            },
            "regulation": "30 minutes avant le lever du soleil jusqu'à 30 minutes après le coucher"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de calcul: {str(e)}")


@router.get("/check")
async def check_legal_now(
    lat: float = Query(46.8139, description="Latitude"),
    lng: float = Query(-71.2080, description="Longitude"),
    timezone: str = Query("America/Toronto", description="Timezone")
):
    """
    Check if hunting is currently legal (right now).
    
    Returns:
        Boolean indicating if hunting is legal and a status message
    """
    location = LocationInput(latitude=lat, longitude=lng, timezone=timezone)
    
    try:
        tz = ZoneInfo(timezone)
        now = datetime.now(tz)
        
        is_legal, message = _service.is_time_legal(now, location)
        legal_window = _service.get_legal_hunting_window(now.date(), location)
        
        return {
            "success": True,
            "current_time": now.strftime("%H:%M:%S"),
            "is_legal": is_legal,
            "message": message,
            "legal_window": {
                "start": legal_window.start_time.strftime("%H:%M"),
                "end": legal_window.end_time.strftime("%H:%M")
            },
            "sunrise": legal_window.sunrise.strftime("%H:%M"),
            "sunset": legal_window.sunset.strftime("%H:%M")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de vérification: {str(e)}")


@router.get("/recommended-slots")
async def get_recommended_slots(
    date_str: Optional[str] = Query(None, alias="date", description="Date au format YYYY-MM-DD"),
    lat: float = Query(46.8139, description="Latitude"),
    lng: float = Query(-71.2080, description="Longitude"),
    timezone: str = Query("America/Toronto", description="Timezone")
):
    """
    Get recommended hunting time slots for a specific date.
    
    Slots are ranked by expected animal activity and remain within legal hours.
    
    Returns:
        List of recommended time slots with scores
    """
    if date_str:
        try:
            target_date = date.fromisoformat(date_str)
        except ValueError:
            raise HTTPException(status_code=400, detail="Format de date invalide. Utilisez YYYY-MM-DD")
    else:
        target_date = date.today()
    
    location = LocationInput(latitude=lat, longitude=lng, timezone=timezone)
    
    try:
        slots = _service.get_recommended_hunting_slots(target_date, location)
        
        return {
            "success": True,
            "date": target_date.isoformat(),
            "location": {
                "latitude": lat,
                "longitude": lng
            },
            "slots": [
                {
                    "period": slot.period_name,
                    "start_time": slot.start_time.strftime("%H:%M"),
                    "end_time": slot.end_time.strftime("%H:%M"),
                    "score": slot.score,
                    "light_condition": slot.light_condition,
                    "recommendation": slot.recommendation,
                    "is_legal": slot.is_legal
                }
                for slot in slots
            ],
            "best_slot": {
                "period": slots[0].period_name,
                "time": f"{slots[0].start_time.strftime('%H:%M')} - {slots[0].end_time.strftime('%H:%M')}",
                "score": slots[0].score
            } if slots else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de calcul: {str(e)}")


@router.get("/schedule")
async def get_daily_schedule(
    date_str: Optional[str] = Query(None, alias="date", description="Date au format YYYY-MM-DD"),
    lat: float = Query(46.8139, description="Latitude"),
    lng: float = Query(-71.2080, description="Longitude"),
    timezone: str = Query("America/Toronto", description="Timezone")
):
    """
    Get a complete daily hunting schedule.
    
    Includes legal window, sun times, and all recommended slots.
    """
    if date_str:
        try:
            target_date = date.fromisoformat(date_str)
        except ValueError:
            raise HTTPException(status_code=400, detail="Format de date invalide. Utilisez YYYY-MM-DD")
    else:
        target_date = date.today()
    
    location = LocationInput(latitude=lat, longitude=lng, timezone=timezone)
    
    try:
        schedule = _service.get_daily_schedule(target_date, location)
        
        return {
            "success": True,
            "schedule": {
                "date": schedule.date.isoformat(),
                "location": {
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "timezone": location.timezone
                },
                "sun_times": {
                    "sunrise": schedule.sun_times.sunrise.strftime("%H:%M"),
                    "sunset": schedule.sun_times.sunset.strftime("%H:%M"),
                    "dawn": schedule.sun_times.dawn.strftime("%H:%M"),
                    "dusk": schedule.sun_times.dusk.strftime("%H:%M"),
                    "day_length_hours": round(schedule.sun_times.day_length_minutes / 60, 1)
                },
                "legal_window": {
                    "start": schedule.legal_window.start_time.strftime("%H:%M"),
                    "end": schedule.legal_window.end_time.strftime("%H:%M"),
                    "duration_hours": round(schedule.legal_window.duration_minutes / 60, 1),
                    "is_currently_legal": schedule.legal_window.is_currently_legal,
                    "status": schedule.legal_window.current_status
                },
                "recommended_slots": [
                    {
                        "period": slot.period_name,
                        "start": slot.start_time.strftime("%H:%M"),
                        "end": slot.end_time.strftime("%H:%M"),
                        "score": slot.score,
                        "light": slot.light_condition,
                        "tip": slot.recommendation
                    }
                    for slot in schedule.recommended_slots
                ],
                "best_period": {
                    "name": schedule.best_slot.period_name,
                    "time": f"{schedule.best_slot.start_time.strftime('%H:%M')} - {schedule.best_slot.end_time.strftime('%H:%M')}",
                    "score": schedule.best_slot.score
                } if schedule.best_slot else None
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de calcul: {str(e)}")


@router.get("/forecast")
async def get_forecast(
    days: int = Query(7, ge=1, le=14, description="Nombre de jours"),
    lat: float = Query(46.8139, description="Latitude"),
    lng: float = Query(-71.2080, description="Longitude"),
    timezone: str = Query("America/Toronto", description="Timezone")
):
    """
    Get a multi-day hunting time forecast.
    
    Returns legal windows and best hunting times for multiple days.
    """
    location = LocationInput(latitude=lat, longitude=lng, timezone=timezone)
    
    try:
        forecast = _service.get_multi_day_forecast(date.today(), days, location)
        
        return {
            "success": True,
            "forecast": {
                "location": {
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "timezone": location.timezone
                },
                "start_date": forecast.start_date.isoformat(),
                "days": forecast.days,
                "daily_schedules": [
                    {
                        "date": schedule.date.isoformat(),
                        "legal_start": schedule.legal_window.start_time.strftime("%H:%M"),
                        "legal_end": schedule.legal_window.end_time.strftime("%H:%M"),
                        "sunrise": schedule.sun_times.sunrise.strftime("%H:%M"),
                        "sunset": schedule.sun_times.sunset.strftime("%H:%M"),
                        "best_period": {
                            "name": schedule.best_slot.period_name,
                            "time": f"{schedule.best_slot.start_time.strftime('%H:%M')} - {schedule.best_slot.end_time.strftime('%H:%M')}",
                            "score": schedule.best_slot.score
                        } if schedule.best_slot else None
                    }
                    for schedule in forecast.schedules
                ]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de calcul: {str(e)}")
