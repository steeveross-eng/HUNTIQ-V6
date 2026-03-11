"""Nutrition Engine Router - CORE

FastAPI router for nutrition-related endpoints.

Version: 1.0.0
API Prefix: /api/v1/nutrition
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from .service import NutritionService
from .data.ingredients import INGREDIENTS_DATABASE

router = APIRouter(prefix="/api/v1/nutrition", tags=["Nutrition Engine"])

# Initialize service
_service = NutritionService()


@router.get("/")
async def nutrition_engine_info():
    """Get nutrition engine information"""
    return {
        "module": "nutrition_engine",
        "version": "1.0.0",
        "description": "Nutritional analysis for hunting attractants",
        "total_ingredients": len(INGREDIENTS_DATABASE),
        "types": _service.get_all_types(),
        "categories": _service.get_all_categories()
    }


@router.get("/ingredients")
async def list_ingredients(
    type: Optional[str] = Query(None, description="Filter by type: olfactif, nutritionnel, comportemental, fixateur"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(50, le=100)
):
    """List all ingredients with optional filters"""
    if type:
        ingredients = _service.get_by_type(type)
    elif category:
        ingredients = _service.get_by_category(category)
    else:
        ingredients = [
            {"name": name, **data}
            for name, data in list(INGREDIENTS_DATABASE.items())[:limit]
        ]
    
    return {
        "success": True,
        "count": len(ingredients),
        "ingredients": ingredients
    }


@router.get("/ingredients/search")
async def search_ingredients(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, le=50)
):
    """Search ingredients by name"""
    results = _service.search(q, limit)
    return {
        "success": True,
        "query": q,
        "count": len(results),
        "results": results
    }


@router.get("/ingredients/{ingredient_name}")
async def get_ingredient(ingredient_name: str):
    """Get detailed information about a specific ingredient"""
    data = _service.get_ingredient_info(ingredient_name.lower())
    
    if not data:
        # Try to find similar ingredients
        similar = _service.search(ingredient_name, limit=5)
        raise HTTPException(
            status_code=404,
            detail={
                "message": f"Ingredient '{ingredient_name}' not found",
                "similar_ingredients": [s["name"] for s in similar]
            }
        )
    
    return {
        "success": True,
        "ingredient": {
            "name": ingredient_name.lower(),
            **data
        }
    }


@router.post("/analyze")
async def analyze_ingredients(ingredient_names: List[str]):
    """
    Analyze a list of ingredients and get nutritional breakdown.
    
    Args:
        ingredient_names: List of ingredient names to analyze
        
    Returns:
        Categorized analysis with scores
    """
    if not ingredient_names:
        raise HTTPException(status_code=400, detail="At least one ingredient required")
    
    analysis = _service.analyze_ingredients(ingredient_names)
    
    return {
        "success": True,
        "input_count": len(ingredient_names),
        "analysis": analysis.model_dump()
    }


@router.get("/types")
async def list_types():
    """List all ingredient types"""
    types = _service.get_all_types()
    return {
        "success": True,
        "types": types,
        "descriptions": {
            "olfactif": "Composés olfactifs - attraction par l'odeur",
            "nutritionnel": "Composés nutritionnels - attraction par la nutrition",
            "comportemental": "Composés comportementaux - phéromones et signaux",
            "fixateur": "Fixateurs - prolongent la durée d'action"
        }
    }


@router.get("/categories")
async def list_categories():
    """List all ingredient categories"""
    categories = _service.get_all_categories()
    return {
        "success": True,
        "categories": sorted(categories)
    }


@router.post("/score")
async def calculate_score(ingredient_names: List[str]):
    """
    Calculate nutrition score for a list of ingredients.
    
    Score is based on nutritional compounds only (1-10 scale).
    """
    if not ingredient_names:
        raise HTTPException(status_code=400, detail="At least one ingredient required")
    
    score = _service.calculate_nutrition_score(ingredient_names)
    
    return {
        "success": True,
        "input_count": len(ingredient_names),
        "nutrition_score": score,
        "rating": _get_score_rating(score)
    }


def _get_score_rating(score: float) -> str:
    """Convert score to rating"""
    if score >= 8:
        return "Excellent"
    elif score >= 6:
        return "Bon"
    elif score >= 4:
        return "Moyen"
    elif score > 0:
        return "Faible"
    else:
        return "Non évalué"
