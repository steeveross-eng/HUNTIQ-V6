"""Nutrition Engine Models - CORE

Pydantic models for nutritional analysis of attractants.
Extracted from analyzer.py without modification.

Version: 1.0.0
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal


class Ingredient(BaseModel):
    """Single ingredient data model"""
    name: str
    type: Literal["olfactif", "nutritionnel", "comportemental", "fixateur"]
    attraction_value: int = Field(ge=1, le=10)
    category: str
    description: str


class NutritionAnalysis(BaseModel):
    """Nutritional analysis result"""
    olfactory_compounds: List[Dict[str, Any]] = []
    nutritional_compounds: List[Dict[str, Any]] = []
    behavioral_compounds: List[Dict[str, Any]] = []
    fixatives: List[Dict[str, Any]] = []
    total_attraction_score: float = 0
    nutrition_score: float = 0
    

class IngredientLookupRequest(BaseModel):
    """Request model for ingredient lookup"""
    ingredient_name: str
    
    
class IngredientLookupResponse(BaseModel):
    """Response model for ingredient lookup"""
    found: bool
    ingredient: Optional[Ingredient] = None
    similar_ingredients: List[str] = []
