"""Wildlife Behavior Engine Models - PLAN MAITRE
Pydantic models for wildlife behavior modeling.

Version: 1.0.0
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime, timezone
from enum import Enum
import uuid


class ActivityLevel(str, Enum):
    """Animal activity levels"""
    VERY_HIGH = "very_high"
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    MINIMAL = "minimal"


class BehaviorType(str, Enum):
    """Types of wildlife behavior"""
    FEEDING = "feeding"
    RESTING = "resting"
    TRAVELING = "traveling"
    RUTTING = "rutting"
    NURSING = "nursing"
    TERRITORIAL = "territorial"


class Season(str, Enum):
    """Hunting seasons / behavior periods"""
    PRE_RUT = "pre_rut"
    RUT = "rut"
    POST_RUT = "post_rut"
    WINTER = "winter"
    SPRING = "spring"
    SUMMER = "summer"
    EARLY_FALL = "early_fall"


class SpeciesProfile(BaseModel):
    """Species behavior profile"""
    species: str
    common_name: str
    scientific_name: Optional[str] = None
    
    # Activity patterns
    primary_activity_time: Literal["diurnal", "nocturnal", "crepuscular"] = "crepuscular"
    peak_activity_hours: List[str] = Field(default_factory=list)  # "05:00-08:00"
    
    # Habitat preferences
    preferred_habitat: List[str] = Field(default_factory=list)
    food_sources: List[str] = Field(default_factory=list)
    water_dependency: Literal["high", "medium", "low"] = "medium"
    
    # Behavior
    home_range_km2: float = 0
    daily_travel_km: float = 0
    group_behavior: Literal["solitary", "pairs", "small_groups", "herds"] = "solitary"
    
    # Seasonal
    rut_period: Optional[str] = None
    migration_pattern: Optional[str] = None


class ActivityPrediction(BaseModel):
    """Predicted activity for a species"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    species: str
    
    # Time context
    date: datetime
    time_of_day: str
    season: Season
    
    # Prediction
    activity_level: ActivityLevel
    activity_score: float = Field(ge=0, le=100)
    primary_behavior: BehaviorType
    
    # Location factors
    coordinates: Optional[Dict[str, float]] = None
    location_bonus: float = 0
    
    # Contributing factors
    factors: Dict[str, float] = Field(default_factory=dict)
    # e.g., {"moon_phase": 0.8, "weather": 0.7, "season": 0.9}
    
    # Recommendations
    best_spots: List[str] = Field(default_factory=list)
    strategy_tips: List[str] = Field(default_factory=list)
    
    # Metadata
    confidence: float = Field(ge=0, le=1, default=0.7)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MovementPattern(BaseModel):
    """Wildlife movement pattern"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    species: str
    pattern_type: Literal["daily", "seasonal", "weather_driven"] = "daily"
    
    # Pattern data
    typical_routes: List[Dict[str, Any]] = Field(default_factory=list)
    concentration_zones: List[Dict[str, Any]] = Field(default_factory=list)
    travel_corridors: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Timing
    peak_movement_times: List[str] = Field(default_factory=list)
    trigger_conditions: Dict[str, Any] = Field(default_factory=dict)
    
    # Validity
    valid_season: Optional[Season] = None
    valid_weather: Optional[Dict[str, Any]] = None


class SeasonalBehavior(BaseModel):
    """Seasonal behavior changes"""
    species: str
    season: Season
    
    # Behavior changes
    activity_modifier: float = 1.0  # Multiplier on base activity
    primary_behaviors: List[BehaviorType] = Field(default_factory=list)
    
    # Location preferences
    habitat_shift: Optional[str] = None
    elevation_preference: Optional[str] = None
    
    # Food preferences
    primary_food: List[str] = Field(default_factory=list)
    attractant_effectiveness: Dict[str, float] = Field(default_factory=dict)
    
    # Social behavior
    group_size_change: Optional[str] = None
    territorial_intensity: Literal["high", "medium", "low"] = "medium"
    
    # Special events
    events: List[str] = Field(default_factory=list)  # "rut peak", "migration"


class PresencePrediction(BaseModel):
    """Wildlife presence prediction for an area"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Location
    coordinates: Dict[str, float]
    radius_km: float = 1.0
    
    # Predictions by species
    species_predictions: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    # species: {probability: 0.75, best_time: "06:00", confidence: 0.8}
    
    # Overall assessment
    best_species: Optional[str] = None
    optimal_hunting_time: Optional[str] = None
    overall_score: float = Field(ge=0, le=100, default=50)
    
    # Metadata
    analysis_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
