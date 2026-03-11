"""Nutrition Engine Service - CORE

Business logic for nutritional analysis.
Extracted from analyzer.py without modification.

Version: 1.0.0
"""

from typing import List, Dict, Any, Optional
from .data.ingredients import (
    INGREDIENTS_DATABASE,
    get_ingredient,
    search_ingredients,
    get_ingredients_by_type,
    get_ingredients_by_category
)
from .models import NutritionAnalysis


class NutritionService:
    """Service for nutritional analysis of attractants"""
    
    def __init__(self):
        self.database = INGREDIENTS_DATABASE
    
    def analyze_ingredients(self, ingredient_names: List[str]) -> NutritionAnalysis:
        """
        Analyze a list of ingredients and categorize them.
        
        Args:
            ingredient_names: List of ingredient names to analyze
            
        Returns:
            NutritionAnalysis with categorized compounds
        """
        olfactory = []
        nutritional = []
        behavioral = []
        fixatives = []
        
        total_attraction = 0
        nutrition_score = 0
        count = 0
        
        for name in ingredient_names:
            ingredient_data = get_ingredient(name)
            if ingredient_data:
                count += 1
                total_attraction += ingredient_data["attraction_value"]
                
                compound = {
                    "name": name,
                    "category": ingredient_data["category"],
                    "attraction_value": ingredient_data["attraction_value"],
                    "description": ingredient_data["description"]
                }
                
                if ingredient_data["type"] == "olfactif":
                    olfactory.append(compound)
                elif ingredient_data["type"] == "nutritionnel":
                    nutritional.append(compound)
                    nutrition_score += ingredient_data["attraction_value"]
                elif ingredient_data["type"] == "comportemental":
                    behavioral.append(compound)
                elif ingredient_data["type"] == "fixateur":
                    fixatives.append(compound)
        
        return NutritionAnalysis(
            olfactory_compounds=olfactory,
            nutritional_compounds=nutritional,
            behavioral_compounds=behavioral,
            fixatives=fixatives,
            total_attraction_score=round(total_attraction / max(count, 1), 1),
            nutrition_score=round(nutrition_score / max(len(nutritional), 1), 1) if nutritional else 0
        )
    
    def get_ingredient_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about an ingredient"""
        return get_ingredient(name)
    
    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search ingredients by name"""
        return search_ingredients(query, limit)
    
    def get_by_type(self, ingredient_type: str) -> List[Dict[str, Any]]:
        """Get all ingredients of a type"""
        return get_ingredients_by_type(ingredient_type)
    
    def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all ingredients of a category"""
        return get_ingredients_by_category(category)
    
    def get_all_types(self) -> List[str]:
        """Get all available ingredient types"""
        return list(set(data["type"] for data in self.database.values()))
    
    def get_all_categories(self) -> List[str]:
        """Get all available ingredient categories"""
        return list(set(data["category"] for data in self.database.values()))
    
    def calculate_nutrition_score(self, ingredients: List[str]) -> float:
        """
        Calculate nutrition score from ingredients list.
        Score based on nutritional compounds only.
        """
        nutritional_scores = []
        
        for name in ingredients:
            data = get_ingredient(name)
            if data and data["type"] == "nutritionnel":
                nutritional_scores.append(data["attraction_value"])
        
        if not nutritional_scores:
            return 0.0
        
        return round(sum(nutritional_scores) / len(nutritional_scores), 1)
