"""
Analytics Engine - Pydantic Models
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class TimeRange(str, Enum):
    WEEK = "week"
    MONTH = "month"
    SEASON = "season"
    YEAR = "year"
    ALL = "all"


class Species(str, Enum):
    DEER = "deer"
    MOOSE = "moose"
    BEAR = "bear"
    WILD_TURKEY = "wild_turkey"
    WILD_BOAR = "wild_boar"
    DUCK = "duck"
    GOOSE = "goose"


class HuntingTrip(BaseModel):
    """Model for a hunting trip record"""
    id: Optional[str] = None
    user_id: str
    date: datetime
    species: str
    location_lat: float
    location_lng: float
    duration_hours: float
    weather_conditions: Optional[str] = None
    temperature: Optional[float] = None
    wind_speed: Optional[float] = None
    moon_phase: Optional[str] = None
    success: bool = False
    observations: int = 0
    notes: Optional[str] = None
    created_at: Optional[datetime] = None


class TripCreate(BaseModel):
    """Model for creating a hunting trip"""
    date: datetime
    species: str
    location_lat: float = Field(..., ge=-90, le=90)
    location_lng: float = Field(..., ge=-180, le=180)
    duration_hours: float = Field(..., gt=0, le=24)
    weather_conditions: Optional[str] = None
    temperature: Optional[float] = None
    wind_speed: Optional[float] = None
    moon_phase: Optional[str] = None
    success: bool = False
    observations: int = Field(default=0, ge=0)
    notes: Optional[str] = None


class OverviewStats(BaseModel):
    """Overall hunting statistics"""
    total_trips: int
    successful_trips: int
    success_rate: float
    total_hours: float
    total_observations: int
    avg_trip_duration: float
    most_active_species: Optional[str] = None
    best_success_species: Optional[str] = None


class SpeciesStats(BaseModel):
    """Statistics per species"""
    species: str
    trips: int
    successes: int
    success_rate: float
    total_observations: int
    avg_duration: float


class WeatherAnalysis(BaseModel):
    """Weather impact analysis"""
    condition: str
    trips: int
    success_rate: float
    avg_observations: float


class TimeSlotAnalysis(BaseModel):
    """Optimal time analysis"""
    hour: int
    label: str
    trips: int
    success_rate: float
    activity_score: float


class MonthlyTrend(BaseModel):
    """Monthly trend data"""
    month: str
    year: int
    trips: int
    successes: int
    success_rate: float
    observations: int


class AnalyticsDashboard(BaseModel):
    """Complete analytics dashboard data"""
    overview: OverviewStats
    species_breakdown: List[SpeciesStats]
    weather_analysis: List[WeatherAnalysis]
    optimal_times: List[TimeSlotAnalysis]
    monthly_trends: List[MonthlyTrend]
    recent_trips: List[HuntingTrip]
