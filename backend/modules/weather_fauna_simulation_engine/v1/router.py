"""Weather Fauna Simulation Engine Router - PLAN MAITRE
FastAPI router for weather-wildlife correlation simulation.

Version: 1.0.0
API Prefix: /api/v1/simulation
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime, timedelta, timezone
from .service import WeatherFaunaSimulationService
from .models import (
    WeatherConditions, SimulationRequest
)

router = APIRouter(prefix="/api/v1/simulation", tags=["Weather Fauna Simulation Engine"])

_service = WeatherFaunaSimulationService()


@router.get("/")
async def simulation_engine_info():
    """Get simulation engine information"""
    stats = await _service.get_stats()
    
    return {
        "module": "weather_fauna_simulation_engine",
        "version": "1.0.0",
        "phase": 4,
        "description": "Simulation de l'impact météo sur la faune",
        "status": "operational",
        "features": [
            "Corrélation météo/activité",
            "Simulations prédictives",
            "Seuils d'activité par conditions",
            "Historique des corrélations",
            "Alertes de conditions optimales"
        ],
        "statistics": stats
    }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "module": "weather_fauna_simulation_engine", "version": "1.0.0"}


@router.post("/run")
async def run_simulation(request: SimulationRequest):
    """Run a simulation"""
    try:
        result = await _service.run_simulation(request)
        return {"success": True, **result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/weather-impact")
async def simulate_weather_impact(
    species: str = Query(...),
    temperature: float = Query(...),
    wind_speed: float = Query(0),
    humidity: Optional[float] = Query(None),
    pressure: Optional[float] = Query(None),
    precipitation: Optional[float] = Query(None)
):
    """Simulate weather impact on species activity"""
    conditions = WeatherConditions(
        temperature=temperature,
        wind_speed=wind_speed,
        humidity=humidity,
        pressure=pressure,
        precipitation=precipitation
    )
    
    result = await _service.simulate_weather_impact(species, conditions)
    return {"success": True, "impact": result.model_dump()}


@router.get("/predict/{species}")
async def predict_activity(
    species: str,
    lat: float = Query(...),
    lng: float = Query(...),
    days: int = Query(7, ge=1, le=14)
):
    """Generate activity forecast for species"""
    forecast = await _service.generate_activity_forecast(species, lat, lng, days)
    return {"success": True, "forecast": forecast.model_dump()}


@router.get("/optimal-conditions")
async def get_optimal_conditions(species: str = Query(...)):
    """Get optimal hunting conditions for a species"""
    conditions = await _service.get_optimal_conditions(species)
    return {"success": True, "optimal_conditions": conditions.model_dump()}


@router.get("/alerts")
async def get_active_alerts(species: Optional[str] = Query(None)):
    """Get active hunting condition alerts"""
    alerts = await _service.get_active_alerts(species)
    return {
        "success": True,
        "total": len(alerts),
        "alerts": [a.model_dump() for a in alerts]
    }


@router.post("/alerts")
async def create_alert(
    species: str = Query(...),
    alert_type: str = Query("favorable"),
    title: str = Query(...),
    message: str = Query(...),
    hours_valid: int = Query(24, ge=1, le=168)
):
    """Create a hunting condition alert"""
    now = datetime.now(timezone.utc)
    
    alert = await _service.create_alert(
        species=species,
        alert_type=alert_type,
        valid_from=now,
        valid_until=now + timedelta(hours=hours_valid),
        title=title,
        message=message
    )
    
    return {"success": True, "alert": alert.model_dump()}
