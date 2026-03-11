"""
Waypoint Scoring Engine - Pydantic Models
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class WeatherCondition(str, Enum):
    SUNNY = "Ensoleillé"
    CLOUDY = "Nuageux"
    RAINY = "Pluvieux"
    FOGGY = "Brumeux"
    SNOWY = "Neigeux"


class WaypointQualityScore(BaseModel):
    """Waypoint Quality Score breakdown"""
    waypoint_id: str
    waypoint_name: str
    total_score: float = Field(..., ge=0, le=100)
    
    # Score components (weights sum to 100%)
    success_history_score: float = Field(..., ge=0, le=100, description="40% weight")
    weather_score: float = Field(..., ge=0, le=100, description="25% weight")
    activity_score: float = Field(..., ge=0, le=100, description="20% weight")
    accessibility_score: float = Field(..., ge=0, le=100, description="15% weight")
    
    # Stats
    total_visits: int = 0
    successful_visits: int = 0
    success_rate: float = 0.0
    last_visit: Optional[str] = None
    
    # Classification
    classification: str = "standard"  # hotspot, good, standard, weak


class SuccessForecast(BaseModel):
    """Success probability forecast"""
    probability: float = Field(..., ge=0, le=100)
    confidence: str = "medium"  # low, medium, high
    
    best_waypoint: Optional[WaypointQualityScore] = None
    optimal_time_window: Optional[str] = None
    favorable_conditions: List[str] = []
    unfavorable_conditions: List[str] = []
    
    # AI recommendation
    ai_recommendation: Optional[str] = None
    

class HeatmapData(BaseModel):
    """Heatmap data point"""
    lat: float
    lng: float
    intensity: float  # 0-1 scale
    waypoint_id: str
    waypoint_name: str
    wqs: float


class WaypointRecommendation(BaseModel):
    """AI-powered waypoint recommendation"""
    waypoint_id: str
    waypoint_name: str
    wqs: float
    success_probability: float
    
    reasoning: str
    weather_match: float
    time_match: float
    species_match: float
    
    recommended_time: str
    tips: List[str] = []


class ForecastRequest(BaseModel):
    """Request for success forecast"""
    species: str = "deer"
    target_date: Optional[datetime] = None
    weather_conditions: Optional[str] = None
    temperature: Optional[float] = None
    wind_speed: Optional[float] = None
    target_hour: Optional[int] = None


class WaypointRanking(BaseModel):
    """Ranked list of waypoints"""
    rankings: List[WaypointQualityScore]
    generated_at: str
    species_filter: Optional[str] = None
    weather_filter: Optional[str] = None
