"""Recommendation Engine Router - PLAN MAITRE
FastAPI router for intelligent recommendation system.

Version: 1.0.0
API Prefix: /api/v1/recommendation
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
from .service import RecommendationService
from .models import (
    RecommendationRequest, RecommendationFeedback
)

router = APIRouter(prefix="/api/v1/recommendation", tags=["Recommendation Engine"])

# Initialize service
_service = RecommendationService()


@router.get("/")
async def recommendation_engine_info():
    """Get recommendation engine information and status"""
    stats = await _service.get_stats()
    
    return {
        "module": "recommendation_engine",
        "version": "1.0.0",
        "phase": 4,
        "description": "Système de recommandation intelligent pour produits et stratégies",
        "status": "operational",
        "features": [
            "Recommandations personnalisées",
            "Filtrage collaboratif",
            "Filtrage basé sur le contenu", 
            "Recommandations contextuelles",
            "Produits similaires",
            "Produits complémentaires"
        ],
        "algorithms": stats.get("algorithms", []),
        "statistics": stats
    }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "module": "recommendation_engine",
        "version": "1.0.0"
    }


@router.post("/products")
async def get_product_recommendations(request: RecommendationRequest):
    """
    Get product recommendations based on context and preferences.
    
    Supports:
    - Personalized recommendations (with user_id)
    - Contextual recommendations (species, season, weather)
    - Similar products (with reference_product_id)
    """
    try:
        response = await _service.get_product_recommendations(request)
        return {
            "success": True,
            "data": response.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/strategies")
async def get_strategy_recommendations(
    species: str = Query(..., description="Espèce cible"),
    season: Optional[str] = Query(None, description="Saison de chasse"),
    temperature: Optional[float] = Query(None, description="Température actuelle"),
    wind_speed: Optional[float] = Query(None, description="Vitesse du vent (km/h)"),
    user_id: Optional[str] = Query(None, description="ID utilisateur pour personnalisation")
):
    """
    Get hunting strategy recommendations.
    
    Returns optimized strategies based on conditions.
    """
    conditions = {
        "season": season,
        "temperature": temperature,
        "wind_speed": wind_speed
    }
    
    try:
        response = await _service.get_strategy_recommendations(
            species=species,
            conditions=conditions,
            user_id=user_id
        )
        return {
            "success": True,
            "data": response.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/similar/{product_id}")
async def get_similar_products(
    product_id: str,
    limit: int = Query(10, ge=1, le=50, description="Nombre max de résultats")
):
    """
    Get similar products to a given product.
    
    Uses content-based filtering on product attributes.
    """
    try:
        similar = await _service.get_similar_products(product_id, limit)
        return {
            "success": True,
            "product_id": product_id,
            "total": len(similar),
            "similar_products": [p.model_dump() for p in similar]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/complementary/{product_id}")
async def get_complementary_products(
    product_id: str,
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get complementary products (often bought together).
    
    Based on purchase pattern analysis.
    """
    try:
        complementary = await _service.get_complementary_products(product_id, limit)
        return {
            "success": True,
            "product_id": product_id,
            "total": len(complementary),
            "complementary_products": [p.model_dump() for p in complementary]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/for-context")
async def get_contextual_recommendations(
    species: str = Query(..., description="Espèce cible"),
    season: str = Query(..., description="Saison (pre-rut, rut, post-rut, etc.)"),
    temperature: Optional[float] = Query(None),
    humidity: Optional[float] = Query(None),
    wind_speed: Optional[float] = Query(None),
    lat: Optional[float] = Query(None, description="Latitude"),
    lng: Optional[float] = Query(None, description="Longitude"),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get context-aware recommendations.
    
    Considers weather, season, species, and location.
    """
    weather = None
    if temperature is not None or humidity is not None or wind_speed is not None:
        weather = {
            "temperature": temperature,
            "humidity": humidity,
            "wind_speed": wind_speed
        }
    
    location = None
    if lat is not None and lng is not None:
        location = {"lat": lat, "lng": lng}
    
    try:
        response = await _service.get_contextual_recommendations(
            species=species,
            season=season,
            weather=weather,
            location=location,
            limit=limit
        )
        return {
            "success": True,
            "data": response.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/personalized/{user_id}")
async def get_personalized_recommendations(
    user_id: str,
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get fully personalized recommendations for a user.
    
    Uses user's history, preferences, and behavior patterns.
    """
    try:
        response = await _service.get_personalized_recommendations(user_id, limit)
        return {
            "success": True,
            "user_id": user_id,
            "data": response.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback")
async def submit_recommendation_feedback(feedback: RecommendationFeedback):
    """
    Submit feedback on a recommendation.
    
    Used to improve recommendation quality.
    """
    try:
        success = await _service.record_feedback(feedback)
        return {
            "success": success,
            "message": "Feedback enregistré" if success else "Erreur d'enregistrement"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile/{user_id}")
async def get_user_recommendation_profile(user_id: str):
    """Get user's recommendation preference profile"""
    profile = await _service.get_user_profile(user_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profil non trouvé")
    
    return {
        "success": True,
        "profile": profile.model_dump()
    }


@router.put("/profile/{user_id}")
async def update_user_recommendation_profile(
    user_id: str,
    profile_data: Dict[str, Any]
):
    """Update user's recommendation preference profile"""
    try:
        profile = await _service.update_user_profile(user_id, profile_data)
        return {
            "success": True,
            "profile": profile.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
