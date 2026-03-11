"""Scoring Engine Models - CORE

Pydantic models for scientific scoring of attractants.
Extracted from analyzer.py without modification.

Version: 1.0.0
"""

from pydantic import BaseModel, Field
from typing import Dict, Literal


class ScoringCriteria(BaseModel):
    """Single scoring criterion configuration"""
    weight: int = Field(ge=1, le=15, description="Weight of this criterion (1-15)")
    max: int = Field(default=10, description="Maximum possible score")
    description: str = Field(description="Human-readable description")


class ScoringResult(BaseModel):
    """Complete scoring result"""
    total_score: float = Field(ge=0, le=10, description="Final weighted score (0-10)")
    pastille: Literal["green", "yellow", "red"] = Field(description="Visual indicator")
    pastille_label: str = Field(description="Human-readable label with emoji")
    criteria_scores: Dict[str, float] = Field(default_factory=dict, description="Raw scores per criterion")
    weighted_scores: Dict[str, float] = Field(default_factory=dict, description="Weighted scores per criterion")


class ScoreRequest(BaseModel):
    """Request model for scoring calculation"""
    attraction_days: int = Field(default=10, ge=1, le=365)
    natural_palatability: float = Field(default=5.0, ge=0, le=10)
    olfactory_power: float = Field(default=5.0, ge=0, le=10)
    persistence: float = Field(default=5.0, ge=0, le=10)
    nutrition: float = Field(default=5.0, ge=0, le=10)
    behavioral_compounds: float = Field(default=5.0, ge=0, le=10)
    rainproof: bool = Field(default=False)
    feed_proof: bool = Field(default=True)
    certified: bool = Field(default=False)
    physical_resistance: float = Field(default=5.0, ge=0, le=10)
    ingredient_purity: float = Field(default=5.0, ge=0, le=10)
    loyalty: float = Field(default=5.0, ge=0, le=10)
    chemical_stability: float = Field(default=5.0, ge=0, le=10)
