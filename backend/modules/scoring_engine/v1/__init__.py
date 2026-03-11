"""Scoring Engine Module v1

Scientific scoring for hunting attractants based on 13 weighted criteria.
Extracted from analyzer.py calculate_score method.

Version: 1.0.0
"""

from .router import router
from .service import ScoringService
from .models import ScoringResult, ScoreRequest

__all__ = [
    "router",
    "ScoringService", 
    "ScoringResult",
    "ScoreRequest"
]
