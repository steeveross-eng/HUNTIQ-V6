"""Recommendation Engine Models - PLAN MAITRE
Pydantic models for intelligent recommendation system.

Version: 1.0.0
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime, timezone
from enum import Enum
import uuid


class RecommendationType(str, Enum):
    """Types of recommendations"""
    PRODUCT = "product"
    STRATEGY = "strategy"
    LOCATION = "location"
    TIMING = "timing"
    EQUIPMENT = "equipment"


class RecommendationContext(str, Enum):
    """Context for recommendations"""
    WEATHER = "weather"
    SEASON = "season"
    SPECIES = "species"
    TERRITORY = "territory"
    HISTORY = "history"


class ProductRecommendation(BaseModel):
    """Product recommendation result"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    product_name: str
    product_type: str
    score: float = Field(ge=0, le=100, description="Relevance score 0-100")
    confidence: float = Field(ge=0, le=1, description="Confidence level 0-1")
    reasons: List[str] = Field(default_factory=list)
    context_match: Dict[str, float] = Field(default_factory=dict)
    is_complementary: bool = False
    is_similar: bool = False


class StrategyRecommendation(BaseModel):
    """Hunting strategy recommendation"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    strategy_type: str
    title: str
    description: str
    score: float = Field(ge=0, le=100)
    conditions: Dict[str, Any] = Field(default_factory=dict)
    suggested_products: List[str] = Field(default_factory=list)
    best_timing: Optional[str] = None


class RecommendationRequest(BaseModel):
    """Request model for recommendations"""
    user_id: Optional[str] = None
    recommendation_type: RecommendationType = RecommendationType.PRODUCT
    
    # Context filters
    species: Optional[str] = None
    season: Optional[str] = None
    weather_conditions: Optional[Dict[str, Any]] = None
    location: Optional[Dict[str, float]] = None  # lat, lng
    
    # Preferences
    max_results: int = Field(default=10, ge=1, le=50)
    include_similar: bool = True
    include_complementary: bool = True
    
    # Product context (for similar/complementary)
    reference_product_id: Optional[str] = None


class RecommendationResponse(BaseModel):
    """Response model for recommendations"""
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    recommendation_type: RecommendationType
    total_results: int = 0
    products: List[ProductRecommendation] = Field(default_factory=list)
    strategies: List[StrategyRecommendation] = Field(default_factory=list)
    context_used: Dict[str, Any] = Field(default_factory=dict)
    processing_time_ms: float = 0
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserPreferenceProfile(BaseModel):
    """User preference profile for personalization"""
    user_id: str
    preferred_species: List[str] = Field(default_factory=list)
    preferred_product_types: List[str] = Field(default_factory=list)
    preferred_brands: List[str] = Field(default_factory=list)
    hunting_experience: Literal["beginner", "intermediate", "expert"] = "intermediate"
    price_sensitivity: Literal["low", "medium", "high"] = "medium"
    analysis_history: List[str] = Field(default_factory=list)  # Product IDs analyzed
    purchase_history: List[str] = Field(default_factory=list)
    rating_history: Dict[str, float] = Field(default_factory=dict)  # product_id: rating
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SimilarityScore(BaseModel):
    """Similarity score between products or users"""
    source_id: str
    target_id: str
    similarity_type: Literal["product", "user"] = "product"
    score: float = Field(ge=0, le=1)
    factors: Dict[str, float] = Field(default_factory=dict)
    computed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RecommendationFeedback(BaseModel):
    """User feedback on recommendations"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    recommendation_id: str
    product_id: str
    action: Literal["clicked", "purchased", "dismissed", "saved"] = "clicked"
    rating: Optional[float] = Field(default=None, ge=1, le=5)
    feedback_text: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
