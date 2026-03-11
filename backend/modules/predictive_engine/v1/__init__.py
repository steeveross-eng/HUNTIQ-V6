"""Predictive Engine v1
Hunting success predictions and activity forecasts.

Version: 1.0.0
"""
from .router import router
from .service import PredictiveService

__all__ = ["router", "PredictiveService"]
