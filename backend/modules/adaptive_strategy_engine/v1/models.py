"""Adaptive Strategy Engine Models - PLAN MAITRE
Pydantic models for adaptive hunting strategies.

Version: 1.0.0
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime, timezone
from enum import Enum
import uuid


class StrategyType(str, Enum):
    """Types of hunting strategies"""
    STAND = "stand"
    STALKING = "stalking"
    CALLING = "calling"
    DRIVING = "driving"
    AMBUSH = "ambush"
    SPOT_AND_STALK = "spot_and_stalk"


class AdaptationTrigger(str, Enum):
    """Triggers for strategy adaptation"""
    WEATHER_CHANGE = "weather_change"
    TIME_ELAPSED = "time_elapsed"
    NO_ACTIVITY = "no_activity"
    WIND_SHIFT = "wind_shift"
    ANIMAL_MOVEMENT = "animal_movement"
    USER_REQUEST = "user_request"


class AdaptiveStrategy(BaseModel):
    """Adaptive hunting strategy"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Base strategy
    primary_strategy: StrategyType
    backup_strategies: List[StrategyType] = Field(default_factory=list)
    
    # Context
    species: str
    location: Dict[str, float]
    conditions: Dict[str, Any] = Field(default_factory=dict)
    
    # Timing
    start_time: datetime
    current_phase: int = 1
    total_phases: int = 3
    
    # Adaptations
    adaptations_made: List[Dict[str, Any]] = Field(default_factory=list)
    next_adaptation_check: Optional[datetime] = None
    
    # Scoring
    initial_score: float = 0
    current_score: float = 0
    success_probability: float = Field(ge=0, le=1, default=0.5)
    
    # Status
    status: Literal["active", "paused", "completed", "abandoned"] = "active"
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StrategyAdjustment(BaseModel):
    """Strategy adjustment recommendation"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    strategy_id: str
    
    # Trigger
    trigger: AdaptationTrigger
    trigger_details: Dict[str, Any] = Field(default_factory=dict)
    
    # Recommendation
    recommended_action: str
    new_strategy: Optional[StrategyType] = None
    location_change: Optional[Dict[str, float]] = None
    timing_change: Optional[str] = None
    
    # Impact
    expected_improvement: float = 0  # percentage
    confidence: float = Field(ge=0, le=1, default=0.7)
    
    # Priority
    priority: Literal["high", "medium", "low"] = "medium"
    reason: str
    
    # Status
    applied: bool = False
    applied_at: Optional[datetime] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StrategyFeedback(BaseModel):
    """User feedback on strategy"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    strategy_id: str
    user_id: str
    
    # Outcome
    outcome: Literal["success", "partial", "failure", "abandoned"] = "partial"
    sighting: bool = False
    harvest: bool = False
    
    # Ratings
    overall_rating: int = Field(ge=1, le=5, default=3)
    accuracy_rating: Optional[int] = Field(default=None, ge=1, le=5)
    
    # Details
    notes: Optional[str] = None
    conditions_accurate: bool = True
    followed_recommendations: bool = True
    
    # Learning data
    what_worked: List[str] = Field(default_factory=list)
    what_failed: List[str] = Field(default_factory=list)
    suggestions: Optional[str] = None
    
    # Metadata
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RouteOptimization(BaseModel):
    """Optimized hunting route"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Route details
    start_point: Dict[str, float]
    end_point: Optional[Dict[str, float]] = None
    waypoints: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Optimization criteria
    optimized_for: Literal["wind", "cover", "distance", "activity", "balanced"] = "balanced"
    
    # Route stats
    total_distance_km: float = 0
    estimated_time_hours: float = 0
    terrain_difficulty: Literal["easy", "moderate", "difficult"] = "moderate"
    
    # Scoring
    route_score: float = Field(ge=0, le=100, default=70)
    wind_advantage_score: float = 0
    cover_score: float = 0
    
    # Metadata
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LearningEntry(BaseModel):
    """Machine learning entry for strategy improvement"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Input features
    species: str
    strategy_type: StrategyType
    conditions: Dict[str, Any]
    location_features: Dict[str, Any]
    
    # Outcome
    success: bool
    score: float
    
    # Metadata
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
