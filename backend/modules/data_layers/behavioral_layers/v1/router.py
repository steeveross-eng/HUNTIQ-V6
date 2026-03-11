"""Behavioral Data Layers Router - PHASE 5
API endpoints for wildlife behavior data access.

Version: 1.0.0
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pydantic import BaseModel
from datetime import datetime, timezone

from ..data_layer import (
    get_behavioral_layer,
    ObservationData,
    ActivityType
)


router = APIRouter(
    prefix="/api/v1/data/behavioral",
    tags=["Data Layers - Behavioral"]
)


# ==============================================
# RESPONSE MODELS
# ==============================================

class HealthResponse(BaseModel):
    status: str
    layer: str
    version: str
    message: str


class ActivityLevelResponse(BaseModel):
    species: str
    hour: int
    activity_level: float
    description: str


# ==============================================
# HEALTH CHECK
# ==============================================

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check behavioral data layer health"""
    layer = get_behavioral_layer()
    stats = await layer.get_stats()
    
    return HealthResponse(
        status="operational",
        layer="behavioral_layers",
        version="1.0.0",
        message=f"Layer opérationnel - {len(stats['supported_species'])} espèces supportées"
    )


@router.get("/stats")
async def get_layer_stats():
    """Get behavioral data layer statistics"""
    layer = get_behavioral_layer()
    return await layer.get_stats()


# ==============================================
# OBSERVATIONS
# ==============================================

@router.get("/observations/area")
async def get_observations_in_area(
    lat: float = Query(..., description="Center latitude"),
    lng: float = Query(..., description="Center longitude"),
    radius_km: float = Query(5.0, description="Search radius in km"),
    species: Optional[str] = Query(None, description="Filter by species"),
    days_back: int = Query(365, description="Days of history")
):
    """Get wildlife observations in an area"""
    layer = get_behavioral_layer()
    observations = await layer.get_observations_in_area(lat, lng, radius_km, species, days_back)
    
    return {
        "count": len(observations),
        "center": {"lat": lat, "lng": lng},
        "radius_km": radius_km,
        "species_filter": species,
        "observations": [o.model_dump() for o in observations]
    }


@router.get("/observations/species/{species}")
async def get_observations_by_species(
    species: str,
    limit: int = Query(100, description="Maximum results")
):
    """Get recent observations for a species"""
    layer = get_behavioral_layer()
    observations = await layer.get_observations_by_species(species, limit)
    
    return {
        "species": species,
        "count": len(observations),
        "observations": [o.model_dump() for o in observations]
    }


@router.post("/observations")
async def record_observation(
    species: str,
    lat: float,
    lng: float,
    count: int = 1,
    activity: Optional[str] = None,
    time_of_day: str = "morning",
    observation_type: str = "visual"
):
    """Record a new wildlife observation"""
    layer = get_behavioral_layer()
    
    # Create observation
    observation = ObservationData(
        coordinates={"lat": lat, "lng": lng},
        species=species.lower(),
        count=count,
        activity=ActivityType(activity) if activity else None,
        observed_at=datetime.now(timezone.utc),
        time_of_day=time_of_day,
        observation_type=observation_type
    )
    
    result = await layer.record_observation(observation)
    
    return {
        "success": True,
        "observation_id": result.id,
        "message": "Observation enregistrée"
    }


# ==============================================
# ACTIVITY PATTERNS
# ==============================================

@router.get("/patterns/{species}")
async def get_activity_pattern(
    species: str,
    region: Optional[str] = Query(None, description="Regional filter")
):
    """Get activity pattern for a species"""
    layer = get_behavioral_layer()
    pattern = await layer.get_activity_pattern(species, region)
    
    return pattern.model_dump()


@router.get("/patterns/{species}/hour/{hour}", response_model=ActivityLevelResponse)
async def get_activity_at_hour(
    species: str,
    hour: int
):
    """Get activity level at a specific hour"""
    if not 0 <= hour <= 23:
        raise HTTPException(status_code=400, detail="Hour must be between 0 and 23")
    
    layer = get_behavioral_layer()
    activity = await layer.get_activity_at_hour(species, hour)
    
    # Describe activity level
    if activity >= 0.85:
        desc = "Très haute activité"
    elif activity >= 0.65:
        desc = "Haute activité"
    elif activity >= 0.45:
        desc = "Activité modérée"
    elif activity >= 0.25:
        desc = "Faible activité"
    else:
        desc = "Activité minimale"
    
    return ActivityLevelResponse(
        species=species,
        hour=hour,
        activity_level=activity,
        description=desc
    )


@router.get("/patterns/{species}/peak-hours")
async def get_peak_hours(species: str):
    """Get peak activity hours for a species"""
    layer = get_behavioral_layer()
    pattern = await layer.get_activity_pattern(species)
    
    return {
        "species": species,
        "peak_hours": pattern.peak_hours,
        "low_hours": pattern.low_hours,
        "recommendation": f"Heures optimales: {pattern.peak_hours}"
    }


# ==============================================
# SEASONAL PATTERNS
# ==============================================

@router.get("/seasons/{species}/current")
async def get_current_season(species: str):
    """Get the current behavioral season for a species"""
    layer = get_behavioral_layer()
    season = await layer.get_current_season(species)
    
    return {
        "species": species,
        "current_season": season,
        "date": datetime.now(timezone.utc).isoformat()
    }


@router.get("/seasons/{species}/{season}")
async def get_seasonal_pattern(species: str, season: str):
    """Get seasonal behavior pattern"""
    layer = get_behavioral_layer()
    pattern = await layer.get_seasonal_pattern(species, season)
    
    return pattern.model_dump()


# ==============================================
# MOVEMENT DATA
# ==============================================

@router.get("/movement/{species}")
async def get_movement_data(
    species: str,
    period_type: str = Query("daily", description="Period type: daily, weekly, seasonal")
):
    """Get movement tracking data for a species"""
    layer = get_behavioral_layer()
    movements = await layer.get_movement_data(species, period_type)
    
    return {
        "species": species,
        "period_type": period_type,
        "track_count": len(movements),
        "movements": [m.model_dump() for m in movements]
    }


@router.get("/movement/{species}/daily-stats")
async def get_daily_movement_stats(species: str):
    """Get average daily movement statistics"""
    layer = get_behavioral_layer()
    stats = await layer.get_average_daily_movement(species)
    
    return {
        "species": species,
        **stats
    }
