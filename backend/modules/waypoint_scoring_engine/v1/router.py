"""
Waypoint Scoring Engine - API Router
Provides WQS, Success Forecast, and AI recommendations
"""
from fastapi import APIRouter, HTTPException, Query, Depends, Request
from typing import List, Optional
import os
import logging

from .models import (
    WaypointQualityScore, SuccessForecast, HeatmapData,
    WaypointRecommendation, ForecastRequest, WaypointRanking
)
from .service import WaypointScoringService

# Import auth helpers
from auth_helpers import get_user_id_with_fallback

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/waypoint-scoring",
    tags=["Waypoint Scoring Engine"],
    responses={404: {"description": "Not found"}}
)

# Database dependency
_db = None

def get_db():
    global _db
    if _db is None:
        from motor.motor_asyncio import AsyncIOMotorClient
        MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        DB_NAME = os.environ.get('DB_NAME', 'hunttrack')
        client = AsyncIOMotorClient(MONGO_URL)
        _db = client[DB_NAME]
    return _db


def get_service() -> WaypointScoringService:
    return WaypointScoringService(get_db())


# ============================================
# MODULE INFO
# ============================================

@router.get("/", summary="Module Info")
async def get_module_info():
    """Get waypoint scoring engine module information"""
    return {
        "module": "waypoint_scoring_engine",
        "version": "1.0.0",
        "description": "Moteur de scoring des waypoints avec WQS et Success Forecast",
        "features": [
            "Waypoint Quality Score (WQS)",
            "Success Forecast predictions",
            "Performance heatmap",
            "AI-powered recommendations",
            "Dynamic waypoint ranking"
        ],
        "wqs_weights": {
            "success_history": "40%",
            "weather_conditions": "25%",
            "animal_activity": "20%",
            "accessibility": "15%"
        }
    }


# ============================================
# WAYPOINT QUALITY SCORE
# ============================================

@router.get("/wqs/{waypoint_id}", response_model=WaypointQualityScore, summary="WQS pour un waypoint")
async def get_waypoint_wqs(
    waypoint_id: str,
    service: WaypointScoringService = Depends(get_service)
):
    """
    Calcule le Waypoint Quality Score (WQS) pour un waypoint spécifique.
    
    Le WQS est basé sur:
    - Historique de succès (40%)
    - Conditions météo associées (25%)
    - Activité animale (20%)
    - Accessibilité/fréquence (15%)
    """
    try:
        return await service.calculate_wqs(waypoint_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error calculating WQS: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/wqs", response_model=List[WaypointQualityScore], summary="WQS pour tous les waypoints")
async def get_all_wqs(
    request: Request,
    user_id: str = Depends(get_user_id_with_fallback),
    service: WaypointScoringService = Depends(get_service)
):
    """
    Calcule le WQS pour tous les waypoints de l'utilisateur.
    Retourne la liste triée par score décroissant.
    """
    try:
        return await service.get_all_wqs(user_id)
    except Exception as e:
        logger.error(f"Error getting all WQS: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ranking", response_model=WaypointRanking, summary="Classement dynamique")
async def get_waypoint_ranking(
    request: Request,
    species: Optional[str] = Query(None, description="Filtrer par espèce"),
    weather: Optional[str] = Query(None, description="Filtrer par météo"),
    user_id: str = Depends(get_user_id_with_fallback),
    service: WaypointScoringService = Depends(get_service)
):
    """
    Récupère le classement dynamique des waypoints.
    Permet de filtrer par espèce et/ou conditions météo.
    """
    try:
        from datetime import datetime, timezone
        rankings = await service.get_all_wqs(user_id)
        
        return WaypointRanking(
            rankings=rankings,
            generated_at=datetime.now(timezone.utc).isoformat(),
            species_filter=species,
            weather_filter=weather
        )
    except Exception as e:
        logger.error(f"Error getting ranking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# HEATMAP
# ============================================

@router.get("/heatmap", response_model=List[HeatmapData], summary="Données heatmap")
async def get_heatmap_data(
    request: Request,
    user_id: str = Depends(get_user_id_with_fallback),
    service: WaypointScoringService = Depends(get_service)
):
    """
    Génère les données pour la heatmap de performance des waypoints.
    
    Chaque point contient:
    - Position (lat/lng)
    - Intensité (0-1) basée sur le WQS
    - Informations du waypoint
    """
    try:
        return await service.get_heatmap_data(user_id)
    except Exception as e:
        logger.error(f"Error getting heatmap: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# SUCCESS FORECAST
# ============================================

@router.post("/forecast", response_model=SuccessForecast, summary="Prévision de succès")
async def get_success_forecast(
    http_request: Request,
    request: ForecastRequest,
    user_id: str = Depends(get_user_id_with_fallback),
    service: WaypointScoringService = Depends(get_service)
):
    """
    Calcule une prévision de succès basée sur:
    - WQS des waypoints
    - Météo prévue
    - Horaires prévus
    - Espèce ciblée
    - Historique personnel
    
    Retourne une probabilité de succès (0-100%) avec recommandations.
    """
    try:
        return await service.calculate_success_forecast(request, user_id)
    except Exception as e:
        logger.error(f"Error calculating forecast: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecast/quick", response_model=SuccessForecast, summary="Prévision rapide")
async def get_quick_forecast(
    http_request: Request,
    species: str = Query("deer", description="Espèce ciblée"),
    weather: Optional[str] = Query(None, description="Conditions météo"),
    hour: Optional[int] = Query(None, ge=0, le=23, description="Heure prévue"),
    temperature: Optional[float] = Query(None, description="Température prévue"),
    user_id: str = Depends(get_user_id_with_fallback),
    service: WaypointScoringService = Depends(get_service)
):
    """
    Calcul rapide de prévision de succès via paramètres GET.
    """
    try:
        request = ForecastRequest(
            species=species,
            weather_conditions=weather,
            target_hour=hour,
            temperature=temperature
        )
        return await service.calculate_success_forecast(request, user_id)
    except Exception as e:
        logger.error(f"Error calculating quick forecast: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# AI RECOMMENDATIONS
# ============================================

@router.get("/recommendations", response_model=List[WaypointRecommendation], summary="Recommandations IA")
async def get_ai_recommendations(
    request: Request,
    species: str = Query("deer", description="Espèce ciblée"),
    weather: Optional[str] = Query(None, description="Conditions météo actuelles"),
    user_id: str = Depends(get_user_id_with_fallback),
    service: WaypointScoringService = Depends(get_service)
):
    """
    Génère des recommandations de waypoints basées sur:
    - Météo actuelle et prévue
    - Horaires optimaux
    - Espèce ciblée
    - Patterns comportementaux
    
    Retourne les 5 meilleurs waypoints avec tips et probabilités.
    """
    try:
        return await service.get_ai_recommendations(species, weather, user_id)
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations/ai", summary="Recommandation IA GPT-5.2")
async def get_gpt_recommendation(
    request: Request,
    waypoint_id: Optional[str] = Query(None, description="ID du waypoint (optionnel)"),
    species: str = Query("deer", description="Espèce ciblée"),
    weather: Optional[str] = Query(None, description="Conditions météo"),
    user_id: str = Depends(get_user_id_with_fallback),
    service: WaypointScoringService = Depends(get_service)
):
    """
    Génère une recommandation personnalisée via GPT-5.2.
    
    Utilise l'intelligence artificielle pour analyser:
    - Les données du waypoint et son historique
    - Les conditions météo actuelles
    - Les patterns comportementaux du gibier
    - L'heure actuelle
    
    Retourne un conseil expert personnalisé.
    """
    from datetime import datetime
    from .ai_service import AIRecommendationService
    
    try:
        ai_service = AIRecommendationService()
        
        # Get waypoint data
        waypoint_data = {}
        if waypoint_id:
            try:
                wqs = await service.calculate_wqs(waypoint_id, user_id)
                waypoint_data = {
                    "name": wqs.waypoint_name,
                    "wqs": wqs.total_score,
                    "classification": wqs.classification,
                    "total_visits": wqs.total_visits,
                    "success_rate": wqs.success_rate
                }
            except Exception:
                pass
        
        if not waypoint_data:
            # Use best waypoint
            all_wqs = await service.get_all_wqs(user_id)
            if all_wqs:
                best = all_wqs[0]
                waypoint_data = {
                    "name": best.waypoint_name,
                    "wqs": best.total_score,
                    "classification": best.classification,
                    "total_visits": best.total_visits,
                    "success_rate": best.success_rate
                }
        
        current_hour = datetime.now().hour
        
        recommendation = await ai_service.generate_recommendation(
            waypoint_data=waypoint_data,
            weather_conditions=weather,
            target_species=species,
            current_hour=current_hour
        )
        
        return {
            "success": True,
            "waypoint": waypoint_data.get("name", "Meilleur spot"),
            "recommendation": recommendation,
            "species": species,
            "weather": weather,
            "hour": current_hour,
            "powered_by": "GPT-5.2"
        }
        
    except Exception as e:
        logger.error(f"Error generating AI recommendation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/briefing", summary="Briefing quotidien IA")
async def get_daily_briefing(
    request: Request,
    species: str = Query("deer", description="Espèce ciblée"),
    weather: Optional[str] = Query(None, description="Météo prévue"),
    user_id: str = Depends(get_user_id_with_fallback),
    service: WaypointScoringService = Depends(get_service)
):
    """
    Génère un briefing quotidien personnalisé via GPT-5.2.
    
    Inclut:
    - Analyse des meilleurs waypoints
    - Créneaux horaires recommandés
    - Conseils basés sur la météo
    - Plan d'action pour la journée
    """
    from .ai_service import AIRecommendationService
    
    try:
        ai_service = AIRecommendationService()
        
        # Get all waypoints with scores
        all_wqs = await service.get_all_wqs(user_id)
        
        waypoints_data = [
            {
                "name": wqs.waypoint_name,
                "wqs": wqs.total_score,
                "classification": wqs.classification
            }
            for wqs in all_wqs[:5]
        ]
        
        briefing = await ai_service.generate_daily_briefing(
            waypoints=waypoints_data,
            weather_forecast=weather,
            target_species=species
        )
        
        return {
            "success": True,
            "briefing": briefing,
            "species": species,
            "weather": weather,
            "waypoints_analyzed": len(waypoints_data),
            "powered_by": "GPT-5.2"
        }
        
    except Exception as e:
        logger.error(f"Error generating briefing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# DEMO DATA
# ============================================

@router.post("/seed-visits", summary="Générer visites démo")
async def seed_demo_visits(
    request: Request,
    user_id: str = Depends(get_user_id_with_fallback),
    service: WaypointScoringService = Depends(get_service)
):
    """
    Génère des données de visites de démonstration pour tester le WQS.
    Crée 5-15 visites par waypoint existant.
    """
    try:
        count = await service.seed_demo_visits(user_id)
        return {
            "success": True,
            "message": f"{count} visites de démonstration créées",
            "count": count
        }
    except Exception as e:
        logger.error(f"Error seeding visits: {e}")
        raise HTTPException(status_code=500, detail=str(e))
