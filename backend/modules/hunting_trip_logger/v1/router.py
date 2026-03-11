"""
Hunting Trip Logger - API Router
Real data logging for hunting trips, waypoint visits, and observations
Feeds data to analytics_engine, waypoint_scoring_engine, and geolocation_engine
"""
from fastapi import APIRouter, HTTPException, Depends, Request, Query
from typing import List, Optional
import os
import logging

from .models import (
    TripCreate, TripStart, TripEnd, TripStatus,
    WaypointVisitCreate, ObservationCreate
)
from .service import HuntingTripLoggerService

# Import auth helpers
from auth_helpers import get_user_id_with_fallback

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/trips",
    tags=["Hunting Trip Logger"],
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


def get_service() -> HuntingTripLoggerService:
    return HuntingTripLoggerService(get_db())


@router.get("/")
async def trip_logger_info():
    """Get hunting trip logger module info"""
    return {
        "module": "hunting_trip_logger",
        "version": "1.0.0",
        "phase": "P4+",
        "description": "Real data logging for hunting trips, waypoint visits, and observations",
        "features": [
            "Log hunting trips with weather and location data",
            "Track waypoint visits during trips",
            "Record observations (sightings, tracks, harvest)",
            "Calculate statistics per user and waypoint",
            "Auto-sync to analytics_engine and waypoint_scoring_engine"
        ],
        "endpoints": {
            "POST /trips": "Create a new trip",
            "POST /trips/start": "Start a trip",
            "POST /trips/end": "End a trip",
            "GET /trips": "List user trips",
            "GET /trips/active": "Get active trip",
            "POST /visits": "Log waypoint visit",
            "POST /visits/{id}/end": "End waypoint visit",
            "POST /observations": "Log observation",
            "GET /statistics": "Get user statistics",
            "GET /statistics/waypoint/{id}": "Get waypoint statistics"
        }
    }


# ============================================
# HUNTING TRIPS
# ============================================

@router.post("/create", response_model=dict, summary="Créer une sortie")
async def create_trip(
    request: Request,
    trip_data: TripCreate,
    user_id: str = Depends(get_user_id_with_fallback),
    service: HuntingTripLoggerService = Depends(get_service)
):
    """
    Créer une nouvelle sortie de chasse planifiée.
    
    - **target_species**: Espèce ciblée (deer, moose, etc.)
    - **planned_date**: Date prévue de la sortie
    - **planned_waypoints**: Liste des waypoints prévus (optionnel)
    """
    try:
        trip = await service.create_trip(user_id, trip_data)
        return {
            "success": True,
            "trip": trip.dict(),
            "message": "Sortie créée avec succès"
        }
    except Exception as e:
        logger.error(f"Error creating trip: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start", response_model=dict, summary="Démarrer une sortie")
async def start_trip(
    request: Request,
    start_data: TripStart,
    user_id: str = Depends(get_user_id_with_fallback),
    service: HuntingTripLoggerService = Depends(get_service)
):
    """
    Démarrer une sortie de chasse planifiée.
    
    - **trip_id**: ID de la sortie à démarrer
    - **actual_weather**: Météo réelle (optionnel)
    - **temperature**: Température actuelle (optionnel)
    """
    try:
        trip = await service.start_trip(user_id, start_data)
        if not trip:
            raise HTTPException(status_code=404, detail="Sortie non trouvée")
        return {
            "success": True,
            "trip": trip.dict(),
            "message": "Sortie démarrée"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting trip: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/end", response_model=dict, summary="Terminer une sortie")
async def end_trip(
    request: Request,
    end_data: TripEnd,
    user_id: str = Depends(get_user_id_with_fallback),
    service: HuntingTripLoggerService = Depends(get_service)
):
    """
    Terminer une sortie de chasse et synchroniser les données.
    
    - **trip_id**: ID de la sortie à terminer
    - **success**: La sortie a-t-elle été un succès?
    - **notes**: Notes de fin de sortie (optionnel)
    
    Les données sont automatiquement synchronisées avec:
    - analytics_engine (statistiques)
    - waypoint_scoring_engine (scores WQS)
    """
    try:
        trip = await service.end_trip(user_id, end_data)
        if not trip:
            raise HTTPException(status_code=404, detail="Sortie non trouvée")
        return {
            "success": True,
            "trip": trip.dict(),
            "message": f"Sortie terminée. Durée: {trip.duration_hours}h, Observations: {trip.observations_count}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending trip: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=List[dict], summary="Liste des sorties")
async def list_trips(
    request: Request,
    status: Optional[str] = Query(None, description="Filtrer par statut"),
    limit: int = Query(50, ge=1, le=200),
    user_id: str = Depends(get_user_id_with_fallback),
    service: HuntingTripLoggerService = Depends(get_service)
):
    """Liste toutes les sorties de l'utilisateur"""
    try:
        trip_status = TripStatus(status) if status else None
        trips = await service.get_user_trips(user_id, trip_status, limit)
        return [t.dict() for t in trips]
    except ValueError:
        raise HTTPException(status_code=400, detail="Statut invalide")
    except Exception as e:
        logger.error(f"Error listing trips: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/active", response_model=dict, summary="Sortie active")
async def get_active_trip(
    request: Request,
    user_id: str = Depends(get_user_id_with_fallback),
    service: HuntingTripLoggerService = Depends(get_service)
):
    """Récupère la sortie en cours"""
    try:
        trip = await service.get_active_trip(user_id)
        if trip:
            return {"active": True, "trip": trip.dict()}
        return {"active": False, "trip": None}
    except Exception as e:
        logger.error(f"Error getting active trip: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# STATISTICS (before /{trip_id} to avoid conflicts)
# ============================================

@router.get("/statistics", response_model=dict, summary="Statistiques utilisateur")
async def get_user_statistics(
    request: Request,
    user_id: str = Depends(get_user_id_with_fallback),
    service: HuntingTripLoggerService = Depends(get_service)
):
    """
    Récupère les statistiques complètes de l'utilisateur.
    
    Inclut:
    - Nombre total de sorties
    - Taux de succès
    - Heures totales
    - Statistiques par espèce et météo
    """
    try:
        stats = await service.get_trip_statistics(user_id)
        return {
            "success": True,
            "statistics": stats.dict()
        }
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics/waypoint/{waypoint_id}", response_model=dict, summary="Stats waypoint")
async def get_waypoint_stats(
    request: Request,
    waypoint_id: str,
    user_id: str = Depends(get_user_id_with_fallback),
    service: HuntingTripLoggerService = Depends(get_service)
):
    """Récupère les statistiques d'un waypoint spécifique"""
    try:
        stats = await service.get_waypoint_statistics(user_id, waypoint_id)
        if not stats:
            return {"success": True, "statistics": None, "message": "Aucune visite pour ce waypoint"}
        return {
            "success": True,
            "statistics": stats.dict()
        }
    except Exception as e:
        logger.error(f"Error getting waypoint statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{trip_id}", response_model=dict, summary="Détails sortie")
async def get_trip(
    request: Request,
    trip_id: str,
    user_id: str = Depends(get_user_id_with_fallback),
    service: HuntingTripLoggerService = Depends(get_service)
):
    """Récupère les détails d'une sortie"""
    try:
        trip = await service.get_trip(user_id, trip_id)
        if not trip:
            raise HTTPException(status_code=404, detail="Sortie non trouvée")
        return {"success": True, "trip": trip.dict()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting trip: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# WAYPOINT VISITS
# ============================================

@router.post("/visits", response_model=dict, summary="Logger visite waypoint")
async def log_visit(
    request: Request,
    visit_data: WaypointVisitCreate,
    user_id: str = Depends(get_user_id_with_fallback),
    service: HuntingTripLoggerService = Depends(get_service)
):
    """
    Logger une visite à un waypoint pendant une sortie.
    
    - **waypoint_id**: ID du waypoint visité
    - **trip_id**: ID de la sortie (optionnel si pas en sortie)
    - **activity_level**: Niveau d'activité observé 0-10 (optionnel)
    """
    try:
        visit = await service.log_waypoint_visit(user_id, visit_data)
        return {
            "success": True,
            "visit": visit.dict(),
            "message": f"Visite loggée: {visit.waypoint_name}"
        }
    except Exception as e:
        logger.error(f"Error logging visit: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/visits/{visit_id}/end", response_model=dict, summary="Terminer visite")
async def end_visit(
    request: Request,
    visit_id: str,
    success: bool = Query(False, description="Visite réussie?"),
    notes: Optional[str] = Query(None, description="Notes"),
    user_id: str = Depends(get_user_id_with_fallback),
    service: HuntingTripLoggerService = Depends(get_service)
):
    """Terminer une visite à un waypoint"""
    try:
        visit = await service.end_waypoint_visit(user_id, visit_id, success, notes)
        if not visit:
            raise HTTPException(status_code=404, detail="Visite non trouvée")
        return {
            "success": True,
            "visit": visit.dict(),
            "message": f"Visite terminée: {visit.duration_minutes} min"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending visit: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/visits/list", response_model=List[dict], summary="Liste des visites")
async def list_visits(
    request: Request,
    waypoint_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    user_id: str = Depends(get_user_id_with_fallback),
    service: HuntingTripLoggerService = Depends(get_service)
):
    """Liste les visites de waypoints"""
    try:
        visits = await service.get_waypoint_visits(user_id, waypoint_id, limit)
        return [v.dict() for v in visits]
    except Exception as e:
        logger.error(f"Error listing visits: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# OBSERVATIONS
# ============================================

@router.post("/observations", response_model=dict, summary="Logger observation")
async def log_observation(
    request: Request,
    obs_data: ObservationCreate,
    user_id: str = Depends(get_user_id_with_fallback),
    service: HuntingTripLoggerService = Depends(get_service)
):
    """
    Logger une observation pendant une sortie.
    
    - **observation_type**: sighting, tracks, sounds, signs, harvest
    - **species**: Espèce observée
    - **count**: Nombre d'animaux (défaut: 1)
    - **distance_meters**: Distance estimée (optionnel)
    - **behavior**: Comportement observé (optionnel)
    """
    try:
        observation = await service.log_observation(user_id, obs_data)
        return {
            "success": True,
            "observation": observation.dict(),
            "message": f"Observation loggée: {obs_data.observation_type.value} de {obs_data.species}"
        }
    except Exception as e:
        logger.error(f"Error logging observation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/observations/list", response_model=List[dict], summary="Liste observations")
async def list_observations(
    request: Request,
    trip_id: Optional[str] = Query(None),
    waypoint_id: Optional[str] = Query(None),
    species: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    user_id: str = Depends(get_user_id_with_fallback),
    service: HuntingTripLoggerService = Depends(get_service)
):
    """Liste les observations avec filtres"""
    try:
        observations = await service.get_observations(user_id, trip_id, waypoint_id, species, limit)
        return [o.dict() for o in observations]
    except Exception as e:
        logger.error(f"Error listing observations: {e}")
        raise HTTPException(status_code=500, detail=str(e))
