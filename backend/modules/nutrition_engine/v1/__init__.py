"""Nutrition Engine v1 - CORE

Nutritional analysis for hunting attractants.
Provides ingredient database and analysis capabilities.

Version: 1.0.0
API Prefix: /api/v1/nutrition

Exports:
- router: FastAPI router
- NutritionService: Main service class
- INGREDIENTS_DATABASE: Complete ingredients database
- models: Pydantic models
"""

from .router import router
from .service import NutritionService
from .data.ingredients import INGREDIENTS_DATABASE
from . import models

__all__ = [
    "router",
    "NutritionService",
    "INGREDIENTS_DATABASE",
    "models"
]

__version__ = "1.0.0"
__module_type__ = "core"
