"""Predictive Engine Models

Pydantic models for hunting predictions.

Version: 1.0.0
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import date


class PredictionFactor(BaseModel):
    """A factor influencing hunting success"""
    name: str
    impact: Literal["very_positive", "positive", "neutral", "negative", "very_negative"]
    score: int = Field(ge=0, le=100)
    description: Optional[str] = None


class OptimalTimeSlot(BaseModel):
    """An optimal time slot for hunting"""
    period: str
    time: str
    score: int = Field(ge=0, le=100)
    is_legal: bool = True


class HuntingPrediction(BaseModel):
    """Complete hunting success prediction"""
    success_probability: int = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=1)
    factors: List[PredictionFactor] = []
    optimal_times: List[OptimalTimeSlot] = []
    recommendation: str = ""


class ActivityLevel(BaseModel):
    """Activity level for a species at a given time"""
    species: str
    level: Literal["very_low", "low", "moderate", "high", "very_high"]
    score: int = Field(ge=0, le=100)
    peak_times: List[str] = []


class ActivityTimeline(BaseModel):
    """Hourly activity timeline"""
    hour: int = Field(ge=0, le=23)
    activity_level: int = Field(ge=0, le=100)
    is_legal: bool = True
    light_condition: str = ""


class DailyActivityForecast(BaseModel):
    """Daily activity forecast for a species"""
    date: date
    species: str
    overall_activity: int = Field(ge=0, le=100)
    peak_period: str = ""
    timeline: List[ActivityTimeline] = []
