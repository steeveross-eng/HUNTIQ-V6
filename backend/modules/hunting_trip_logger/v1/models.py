"""
Hunting Trip Logger - Pydantic Models
Real data logging for hunting trips, waypoint visits, and observations
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class TripStatus(str, Enum):
    """Trip status enum"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class WeatherCondition(str, Enum):
    """Weather conditions enum"""
    SUNNY = "sunny"
    CLOUDY = "cloudy"
    RAINY = "rainy"
    SNOWY = "snowy"
    FOGGY = "foggy"
    WINDY = "windy"
    OVERCAST = "overcast"


class ObservationType(str, Enum):
    """Observation type enum"""
    SIGHTING = "sighting"        # Animal seen
    TRACKS = "tracks"            # Tracks found
    SOUNDS = "sounds"            # Animal heard
    SIGNS = "signs"              # Other signs (droppings, rubs, etc.)
    HARVEST = "harvest"          # Successful harvest


# ============================================
# HUNTING TRIP MODELS
# ============================================

class TripCreate(BaseModel):
    """Create a new hunting trip"""
    title: Optional[str] = None
    target_species: str = Field(..., description="Target species (deer, moose, etc.)")
    planned_date: datetime
    planned_waypoints: List[str] = Field(default=[], description="List of waypoint IDs to visit")
    notes: Optional[str] = None


class TripStart(BaseModel):
    """Start a hunting trip"""
    trip_id: str
    actual_weather: Optional[WeatherCondition] = None
    temperature: Optional[float] = None
    wind_speed: Optional[float] = None
    start_location_lat: Optional[float] = None
    start_location_lng: Optional[float] = None


class TripEnd(BaseModel):
    """End a hunting trip"""
    trip_id: str
    success: bool = False
    notes: Optional[str] = None


class HuntingTrip(BaseModel):
    """Full hunting trip model"""
    trip_id: str
    user_id: str
    title: Optional[str] = None
    target_species: str
    status: TripStatus = TripStatus.PLANNED
    planned_date: datetime
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_hours: Optional[float] = None
    weather: Optional[WeatherCondition] = None
    temperature: Optional[float] = None
    wind_speed: Optional[float] = None
    success: bool = False
    planned_waypoints: List[str] = []
    visited_waypoints: List[str] = []
    observations_count: int = 0
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


# ============================================
# WAYPOINT VISIT MODELS
# ============================================

class WaypointVisitCreate(BaseModel):
    """Log a waypoint visit during a trip"""
    waypoint_id: str
    trip_id: Optional[str] = None
    arrival_time: Optional[datetime] = None
    departure_time: Optional[datetime] = None
    weather: Optional[WeatherCondition] = None
    activity_level: Optional[int] = Field(None, ge=0, le=10, description="Animal activity 0-10")
    notes: Optional[str] = None


class WaypointVisit(BaseModel):
    """Full waypoint visit model"""
    visit_id: str
    user_id: str
    waypoint_id: str
    waypoint_name: Optional[str] = None
    trip_id: Optional[str] = None
    arrival_time: datetime
    departure_time: Optional[datetime] = None
    duration_minutes: Optional[float] = None
    weather: Optional[WeatherCondition] = None
    activity_level: Optional[int] = None
    success: bool = False
    observations_count: int = 0
    notes: Optional[str] = None
    created_at: datetime


# ============================================
# OBSERVATION MODELS
# ============================================

class ObservationCreate(BaseModel):
    """Log an observation during a trip"""
    trip_id: Optional[str] = None
    waypoint_id: Optional[str] = None
    observation_type: ObservationType
    species: str
    count: int = Field(default=1, ge=1, description="Number of animals observed")
    distance_meters: Optional[float] = None
    direction: Optional[str] = None  # N, NE, E, SE, S, SW, W, NW
    behavior: Optional[str] = None   # feeding, moving, resting, etc.
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    notes: Optional[str] = None
    photo_url: Optional[str] = None


class Observation(BaseModel):
    """Full observation model"""
    observation_id: str
    user_id: str
    trip_id: Optional[str] = None
    waypoint_id: Optional[str] = None
    observation_type: ObservationType
    species: str
    count: int = 1
    distance_meters: Optional[float] = None
    direction: Optional[str] = None
    behavior: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    notes: Optional[str] = None
    photo_url: Optional[str] = None
    timestamp: datetime
    created_at: datetime


# ============================================
# STATISTICS MODELS
# ============================================

class TripStatistics(BaseModel):
    """Statistics for a user's hunting trips"""
    total_trips: int = 0
    completed_trips: int = 0
    successful_trips: int = 0
    success_rate: float = 0.0
    total_hours: float = 0.0
    average_duration: float = 0.0
    total_observations: int = 0
    total_waypoints_visited: int = 0
    most_visited_waypoint: Optional[str] = None
    best_waypoint: Optional[str] = None  # Highest success rate
    favorite_species: Optional[str] = None
    by_species: dict = {}
    by_weather: dict = {}
    by_month: dict = {}


class WaypointStatistics(BaseModel):
    """Statistics for a specific waypoint"""
    waypoint_id: str
    waypoint_name: str
    total_visits: int = 0
    successful_visits: int = 0
    success_rate: float = 0.0
    total_observations: int = 0
    average_activity: float = 0.0
    best_time_slot: Optional[str] = None
    best_weather: Optional[str] = None
    species_observed: List[str] = []
