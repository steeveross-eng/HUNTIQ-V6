"""
Analytics Engine - API Router
Provides endpoints for hunting analytics and statistics
"""
from fastapi import APIRouter, HTTPException, Query, Depends, Request
from typing import List, Optional
import os
import logging

from .models import (
    TripCreate, OverviewStats, SpeciesStats,
    WeatherAnalysis, TimeSlotAnalysis, MonthlyTrend, 
    AnalyticsDashboard, TimeRange
)
from .service import AnalyticsService

# Import auth helpers
from auth_helpers import get_user_id_with_fallback

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/analytics",
    tags=["Analytics Engine"],
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


def get_service() -> AnalyticsService:
    return AnalyticsService(get_db())


# ============================================
# MODULE INFO
# ============================================

@router.get("/", summary="Module Info")
async def get_module_info():
    """Get analytics engine module information"""
    return {
        "module": "analytics_engine",
        "version": "1.0.0",
        "description": "Moteur d'analytique pour statistiques de chasse",
        "endpoints": [
            "GET /dashboard - Tableau de bord complet",
            "GET /overview - Statistiques globales",
            "GET /species - Répartition par espèce",
            "GET /weather - Analyse météo",
            "GET /optimal-times - Heures optimales",
            "GET /trends - Tendances mensuelles",
            "GET /trips - Liste des sorties",
            "POST /trips - Créer une sortie",
            "DELETE /trips/{id} - Supprimer une sortie",
            "POST /seed - Générer données démo"
        ]
    }


# ============================================
# DASHBOARD
# ============================================

@router.get("/dashboard", response_model=AnalyticsDashboard, summary="Tableau de bord complet")
async def get_dashboard(
    request: Request,
    time_range: TimeRange = Query(TimeRange.ALL, description="Période de temps"),
    user_id: str = Depends(get_user_id_with_fallback),
    service: AnalyticsService = Depends(get_service)
):
    """
    Récupère toutes les données du tableau de bord analytique.
    
    - **time_range**: Filtre par période (week, month, season, year, all)
    """
    try:
        return await service.get_full_dashboard(user_id, time_range)
    except Exception as e:
        logger.error(f"Error getting dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# STATISTICS ENDPOINTS
# ============================================

@router.get("/overview", response_model=OverviewStats, summary="Statistiques globales")
async def get_overview(
    request: Request,
    time_range: TimeRange = Query(TimeRange.ALL, description="Période de temps"),
    user_id: str = Depends(get_user_id_with_fallback),
    service: AnalyticsService = Depends(get_service)
):
    """
    Récupère les statistiques globales de chasse.
    
    Inclut:
    - Nombre total de sorties
    - Taux de succès
    - Heures totales de chasse
    - Observations totales
    """
    try:
        return await service.get_overview_stats(user_id, time_range)
    except Exception as e:
        logger.error(f"Error getting overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/species", response_model=List[SpeciesStats], summary="Répartition par espèce")
async def get_species_breakdown(
    request: Request,
    time_range: TimeRange = Query(TimeRange.ALL, description="Période de temps"),
    user_id: str = Depends(get_user_id_with_fallback),
    service: AnalyticsService = Depends(get_service)
):
    """
    Récupère les statistiques détaillées par espèce.
    
    Inclut pour chaque espèce:
    - Nombre de sorties
    - Taux de succès
    - Observations totales
    - Durée moyenne
    """
    try:
        return await service.get_species_breakdown(user_id, time_range)
    except Exception as e:
        logger.error(f"Error getting species breakdown: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/weather", response_model=List[WeatherAnalysis], summary="Analyse météo")
async def get_weather_analysis(
    request: Request,
    user_id: str = Depends(get_user_id_with_fallback),
    service: AnalyticsService = Depends(get_service)
):
    """
    Analyse l'impact des conditions météo sur le succès de chasse.
    
    Retourne le taux de succès et les observations moyennes
    pour chaque type de condition météo.
    """
    try:
        return await service.get_weather_analysis(user_id)
    except Exception as e:
        logger.error(f"Error getting weather analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/optimal-times", response_model=List[TimeSlotAnalysis], summary="Heures optimales")
async def get_optimal_times(
    request: Request,
    user_id: str = Depends(get_user_id_with_fallback),
    service: AnalyticsService = Depends(get_service)
):
    """
    Analyse les heures optimales de chasse basée sur l'historique.
    
    Retourne pour chaque créneau horaire:
    - Nombre de sorties
    - Taux de succès
    - Score d'activité
    """
    try:
        return await service.get_optimal_times(user_id)
    except Exception as e:
        logger.error(f"Error getting optimal times: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends", response_model=List[MonthlyTrend], summary="Tendances mensuelles")
async def get_monthly_trends(
    request: Request,
    months: int = Query(12, ge=1, le=24, description="Nombre de mois"),
    user_id: str = Depends(get_user_id_with_fallback),
    service: AnalyticsService = Depends(get_service)
):
    """
    Récupère les tendances mensuelles de chasse.
    
    Permet de visualiser l'évolution sur plusieurs mois.
    """
    try:
        return await service.get_monthly_trends(user_id, months)
    except Exception as e:
        logger.error(f"Error getting trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# TRIPS CRUD
# ============================================

@router.get("/trips", response_model=List[dict], summary="Liste des sorties")
async def get_trips(
    request: Request,
    time_range: TimeRange = Query(TimeRange.ALL, description="Période de temps"),
    species: Optional[str] = Query(None, description="Filtrer par espèce"),
    limit: int = Query(50, ge=1, le=200, description="Nombre maximum"),
    user_id: str = Depends(get_user_id_with_fallback),
    service: AnalyticsService = Depends(get_service)
):
    """
    Récupère la liste des sorties de chasse.
    
    - **time_range**: Filtre par période
    - **species**: Filtre par espèce (optionnel)
    - **limit**: Nombre maximum de résultats
    """
    try:
        return await service.get_trips(user_id, time_range, species, limit)
    except Exception as e:
        logger.error(f"Error getting trips: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trips", response_model=dict, summary="Créer une sortie")
async def create_trip(
    request: Request,
    trip: TripCreate,
    user_id: str = Depends(get_user_id_with_fallback),
    service: AnalyticsService = Depends(get_service)
):
    """
    Enregistre une nouvelle sortie de chasse.
    
    - **date**: Date et heure de la sortie
    - **species**: Espèce ciblée
    - **location_lat/lng**: Coordonnées GPS
    - **duration_hours**: Durée en heures
    - **success**: Sortie réussie ou non
    - **observations**: Nombre d'observations
    """
    try:
        result = await service.create_trip(user_id, trip)
        return {"success": True, "trip": result}
    except Exception as e:
        logger.error(f"Error creating trip: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/trips/{trip_id}", summary="Supprimer une sortie")
async def delete_trip(
    request: Request,
    trip_id: str,
    user_id: str = Depends(get_user_id_with_fallback),
    service: AnalyticsService = Depends(get_service)
):
    """Supprime une sortie de chasse"""
    try:
        deleted = await service.delete_trip(user_id, trip_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Sortie non trouvée")
        return {"success": True, "message": "Sortie supprimée"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting trip: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# DEMO DATA
# ============================================

@router.post("/seed", summary="Générer données démo")
async def seed_demo_data(
    request: Request,
    user_id: str = Depends(get_user_id_with_fallback),
    service: AnalyticsService = Depends(get_service)
):
    """
    Génère des données de démonstration pour tester le tableau de bord.
    
    Crée 50 sorties de chasse simulées sur les 12 derniers mois.
    """
    try:
        count = await service.seed_demo_data(user_id)
        return {
            "success": True,
            "message": f"{count} sorties de démonstration créées",
            "count": count
        }
    except Exception as e:
        logger.error(f"Error seeding data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
