"""Strategy Engine Models - CORE

Pydantic models for hunting strategy generation.

Version: 1.0.0
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime, timezone


class HuntingContext(BaseModel):
    """Hunting context for strategy generation"""
    species: Literal["deer", "moose", "bear", "wild_boar", "turkey"] = "deer"
    season: Literal["spring", "summer", "fall", "winter"] = "fall"
    time_of_day: Literal["dawn", "morning", "midday", "afternoon", "dusk", "night"] = "dawn"
    weather: Literal["clear", "cloudy", "rain", "snow", "fog", "wind"] = "clear"
    terrain: Literal["forest", "field", "edge", "swamp", "mountain"] = "forest"
    moon_phase: Optional[str] = None


class StrategyRecommendation(BaseModel):
    """Single strategy recommendation"""
    priority: int = Field(ge=1, le=5)
    category: str
    title: str
    description: str
    tips: List[str] = Field(default_factory=list)
    success_probability: float = Field(ge=0, le=100)


class HuntingStrategy(BaseModel):
    """Complete hunting strategy"""
    id: str
    context: HuntingContext
    overall_score: float = Field(ge=0, le=10)
    success_estimate: str
    primary_approach: str
    recommendations: List[StrategyRecommendation] = Field(default_factory=list)
    equipment: List[str] = Field(default_factory=list)
    timing: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StandPlacement(BaseModel):
    """Recommended stand/blind placement"""
    placement_type: Literal["tree_stand", "ground_blind", "natural_blind", "elevated"]
    orientation: str  # Wind direction to face
    height_meters: float
    distance_from_trail_meters: float
    cover_requirements: str
    entry_exit_strategy: str


class AttractantStrategy(BaseModel):
    """Attractant usage strategy"""
    product_type: str
    placement_distance_meters: float
    quantity: str
    timing: str
    renewal_frequency: str
    wind_considerations: str
