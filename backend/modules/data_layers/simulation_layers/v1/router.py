"""Simulation Data Layers Router - PHASE 5
API endpoints for weather-fauna simulation data access.

Version: 1.0.0
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pydantic import BaseModel

from ..data_layer import get_simulation_layer


router = APIRouter(
    prefix="/api/v1/data/simulation",
    tags=["Data Layers - Simulation"]
)


# ==============================================
# RESPONSE MODELS
# ==============================================

class HealthResponse(BaseModel):
    status: str
    layer: str
    version: str
    message: str


class ConditionsRatingResponse(BaseModel):
    species: str
    factors: dict
    overall_score: float
    recommendation: str


# ==============================================
# HEALTH CHECK
# ==============================================

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check simulation data layer health"""
    layer = get_simulation_layer()
    stats = await layer.get_stats()
    
    return HealthResponse(
        status="operational",
        layer="simulation_layers",
        version="1.0.0",
        message=f"Layer opérationnel - {len(stats['supported_species'])} espèces supportées"
    )


@router.get("/stats")
async def get_layer_stats():
    """Get simulation data layer statistics"""
    layer = get_simulation_layer()
    return await layer.get_stats()


# ==============================================
# CORRELATIONS
# ==============================================

@router.get("/correlations/{species}")
async def get_all_correlations(species: str):
    """Get all weather correlations for a species"""
    layer = get_simulation_layer()
    correlations = await layer.get_all_correlations(species)
    
    if not correlations:
        raise HTTPException(
            status_code=404, 
            detail=f"No correlations found for species: {species}"
        )
    
    return {
        "species": species,
        "correlations": {k: v.model_dump() for k, v in correlations.items()}
    }


@router.get("/correlations/{species}/{factor}")
async def get_correlation(species: str, factor: str):
    """Get correlation coefficient for a specific factor"""
    layer = get_simulation_layer()
    correlation = await layer.get_correlation(species, factor)
    
    if not correlation:
        raise HTTPException(
            status_code=404,
            detail=f"No correlation found for {species}/{factor}"
        )
    
    return correlation.model_dump()


# ==============================================
# OPTIMAL CONDITIONS
# ==============================================

@router.get("/optimal/{species}")
async def get_optimal_conditions(species: str):
    """Get optimal hunting conditions for a species"""
    layer = get_simulation_layer()
    optimal = await layer.get_optimal_conditions(species)
    
    return optimal.model_dump()


@router.post("/conditions/rate", response_model=ConditionsRatingResponse)
async def rate_conditions(
    species: str,
    temperature: float,
    wind_speed: float = 0,
    pressure: Optional[float] = None,
    precipitation: float = 0
):
    """Rate current conditions against optimal for a species"""
    layer = get_simulation_layer()
    rating = await layer.check_conditions_rating(
        species, temperature, wind_speed, pressure, precipitation
    )
    
    return ConditionsRatingResponse(
        species=species,
        factors=rating["factors"],
        overall_score=rating["overall_score"],
        recommendation=rating["recommendation"]
    )


# ==============================================
# ACTIVITY IMPACT
# ==============================================

@router.post("/impact/calculate")
async def calculate_activity_impact(
    species: str,
    temperature: float,
    wind_speed: float = 0,
    pressure: Optional[float] = None,
    precipitation: float = 0
):
    """Calculate weather impact on wildlife activity"""
    layer = get_simulation_layer()
    impact = await layer.calculate_activity_impact(
        species, temperature, wind_speed, pressure, precipitation
    )
    
    return impact


# ==============================================
# SIMULATION HISTORY
# ==============================================

@router.post("/history/record")
async def record_simulation(
    species: str,
    predicted_activity: float,
    temperature: float,
    wind_speed: Optional[float] = None,
    pressure: Optional[float] = None,
    precipitation: Optional[float] = None
):
    """Record a simulation prediction for later validation"""
    layer = get_simulation_layer()
    
    conditions = {
        "temperature": temperature,
        "wind_speed": wind_speed,
        "pressure": pressure,
        "precipitation": precipitation
    }
    
    result = await layer.record_simulation(species, predicted_activity, conditions)
    
    return {
        "success": True,
        "simulation_id": result.id,
        "message": "Simulation enregistrée pour validation future"
    }


@router.post("/history/verify/{simulation_id}")
async def verify_simulation(
    simulation_id: str,
    actual_activity: float
):
    """Verify a past simulation with actual observation"""
    layer = get_simulation_layer()
    result = await layer.verify_simulation(simulation_id, actual_activity)
    
    if not result:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    return {
        "success": True,
        "simulation_id": simulation_id,
        "predicted": result.predicted_activity,
        "actual": result.actual_activity,
        "accuracy_score": result.accuracy_score,
        "error": result.error
    }


@router.get("/history/accuracy/{species}")
async def get_simulation_accuracy(
    species: str,
    days_back: int = Query(30, description="Days of history to analyze")
):
    """Get simulation accuracy statistics for a species"""
    layer = get_simulation_layer()
    accuracy = await layer.get_simulation_accuracy(species, days_back)
    
    return {
        "species": species,
        "period_days": days_back,
        **accuracy
    }
