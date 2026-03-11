"""Weather Fauna Simulation Engine Models - PLAN MAITRE
Pydantic models for weather-wildlife correlation simulation.

Version: 1.0.0
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime, timezone
from enum import Enum
import uuid


class SimulationType(str, Enum):
    """Types of simulations"""
    WEATHER_IMPACT = "weather_impact"
    ACTIVITY_FORECAST = "activity_forecast"
    OPTIMAL_CONDITIONS = "optimal_conditions"
    HISTORICAL_ANALYSIS = "historical_analysis"


class WeatherConditions(BaseModel):
    """Weather conditions model"""
    temperature: float  # Celsius
    humidity: Optional[float] = None  # Percentage
    wind_speed: Optional[float] = None  # km/h
    wind_direction: Optional[str] = None
    precipitation: Optional[float] = None  # mm
    pressure: Optional[float] = None  # hPa
    cloud_cover: Optional[float] = None  # Percentage
    moon_phase: Optional[str] = None
    visibility: Optional[float] = None  # km


class ActivityCorrelation(BaseModel):
    """Correlation between weather and activity"""
    factor: str
    correlation_strength: float = Field(ge=-1, le=1)
    optimal_range: Optional[Dict[str, float]] = None
    description: str


class WeatherImpactResult(BaseModel):
    """Result of weather impact simulation"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    species: str
    conditions: WeatherConditions
    
    # Impact scores
    overall_impact_score: float = Field(ge=0, le=100)
    activity_multiplier: float = Field(ge=0, le=2, default=1.0)
    
    # Individual factor impacts
    factor_impacts: Dict[str, float] = Field(default_factory=dict)
    # e.g., {"temperature": 0.8, "pressure": 0.9, "wind": 0.6}
    
    # Analysis
    positive_factors: List[str] = Field(default_factory=list)
    negative_factors: List[str] = Field(default_factory=list)
    limiting_factor: Optional[str] = None
    
    # Recommendations
    hunting_recommendation: Literal["excellent", "good", "fair", "poor", "avoid"] = "fair"
    tips: List[str] = Field(default_factory=list)
    
    # Metadata
    simulated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ActivityForecast(BaseModel):
    """Multi-day activity forecast"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    species: str
    location: Dict[str, float]
    
    # Forecast period
    start_date: datetime
    end_date: datetime
    
    # Daily forecasts
    daily_forecasts: List[Dict[str, Any]] = Field(default_factory=list)
    # [{date, activity_score, weather, recommendation}]
    
    # Best periods
    best_dates: List[str] = Field(default_factory=list)
    best_time_slots: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Alerts
    alerts: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Metadata
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    forecast_confidence: float = Field(ge=0, le=1, default=0.7)


class OptimalConditions(BaseModel):
    """Optimal hunting conditions for a species"""
    species: str
    
    # Temperature
    optimal_temp_min: float
    optimal_temp_max: float
    
    # Wind
    max_wind_speed: float
    preferred_wind_direction: Optional[str] = None
    
    # Pressure
    pressure_trend: Literal["rising", "falling", "stable", "any"] = "falling"
    optimal_pressure_min: Optional[float] = None
    optimal_pressure_max: Optional[float] = None
    
    # Other factors
    preferred_cloud_cover: Literal["clear", "partly_cloudy", "overcast", "any"] = "partly_cloudy"
    moon_phase_preference: Optional[str] = None
    
    # Precipitation
    avoid_precipitation: bool = True
    
    # Correlations
    correlations: List[ActivityCorrelation] = Field(default_factory=list)


class SimulationAlert(BaseModel):
    """Alert for optimal hunting conditions"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Alert details
    species: str
    alert_type: Literal["optimal", "favorable", "frontal", "pressure_drop"] = "favorable"
    severity: Literal["high", "medium", "low"] = "medium"
    
    # Timing
    valid_from: datetime
    valid_until: datetime
    
    # Location
    location: Optional[Dict[str, float]] = None
    region: Optional[str] = None
    
    # Details
    title: str
    message: str
    conditions: Optional[WeatherConditions] = None
    expected_activity_score: float = 0
    
    # Status
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SimulationRequest(BaseModel):
    """Request for simulation"""
    species: str
    simulation_type: SimulationType = SimulationType.WEATHER_IMPACT
    
    # Location (optional)
    lat: Optional[float] = None
    lng: Optional[float] = None
    
    # Weather (for impact simulation)
    conditions: Optional[WeatherConditions] = None
    
    # Forecast parameters
    forecast_days: int = Field(default=7, ge=1, le=14)
