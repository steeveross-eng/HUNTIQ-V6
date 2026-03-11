"""
Tracking Engine - API Router V1
================================
Endpoints for user behavior tracking, events, funnels and heatmaps.
Architecture LEGO V5 - Module isolé.
"""
from fastapi import APIRouter, HTTPException, Query, Depends, Request
from typing import List, Optional
from datetime import datetime, timezone, timedelta
import os
import logging

from .models import (
    TrackingEventCreate, EventType,
    FunnelCreate, FunnelAnalysis,
    HeatmapData, SessionSummary, EngagementMetrics
)
from .service import TrackingEngineService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/tracking-engine",
    tags=["Tracking Engine V1"],
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


def get_service() -> TrackingEngineService:
    return TrackingEngineService(get_db())


# ============================================
# MODULE INFO
# ============================================

@router.get("/", summary="Module Info")
async def get_module_info():
    """Get tracking engine module information"""
    return {
        "module": "tracking_engine",
        "version": "1.0.0",
        "description": "Moteur de tracking comportemental utilisateur",
        "features": [
            "Event tracking (clicks, page views, scrolls)",
            "Conversion funnels",
            "Heatmaps",
            "Session analysis",
            "Engagement metrics"
        ],
        "endpoints": [
            "POST /events - Track a single event",
            "POST /events/batch - Track multiple events",
            "GET /events - Get events with filters",
            "POST /funnels - Create a conversion funnel",
            "GET /funnels - List all funnels",
            "GET /funnels/{id}/analyze - Analyze funnel performance",
            "GET /heatmap - Get heatmap data for a page",
            "GET /sessions/{id} - Get session summary",
            "GET /engagement - Get engagement metrics",
            "POST /seed - Generate demo data"
        ]
    }


# ============================================
# EVENTS
# ============================================

@router.post("/events", response_model=dict, summary="Track Event")
async def track_event(
    request: Request,
    event: TrackingEventCreate,
    service: TrackingEngineService = Depends(get_service)
):
    """
    Enregistre un événement de tracking.
    
    Types d'événements supportés:
    - page_view: Vue de page
    - click: Clic
    - scroll: Défilement
    - form_submit: Soumission de formulaire
    - search: Recherche
    - map_interaction: Interaction avec la carte
    - feature_use: Utilisation de fonctionnalité
    - purchase: Achat
    - signup: Inscription
    - login: Connexion
    - error: Erreur
    - custom: Événement personnalisé
    """
    try:
        ip_address = request.client.host if request.client else None
        result = await service.track_event(event, ip_address)
        return {"success": True, "event_id": result.id}
    except Exception as e:
        logger.error(f"Error tracking event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/events/batch", response_model=dict, summary="Batch Track Events")
async def batch_track_events(
    request: Request,
    events: List[TrackingEventCreate],
    service: TrackingEngineService = Depends(get_service)
):
    """Enregistre plusieurs événements en batch"""
    try:
        ip_address = request.client.host if request.client else None
        count = await service.batch_track_events(events, ip_address)
        return {"success": True, "events_tracked": count}
    except Exception as e:
        logger.error(f"Error batch tracking events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events", response_model=List[dict], summary="Get Events")
async def get_events(
    session_id: Optional[str] = Query(None, description="Filter by session"),
    user_id: Optional[str] = Query(None, description="Filter by user"),
    event_type: Optional[EventType] = Query(None, description="Filter by event type"),
    page_url: Optional[str] = Query(None, description="Filter by page URL pattern"),
    days: int = Query(30, ge=1, le=365, description="Look back period in days"),
    limit: int = Query(100, ge=1, le=1000, description="Max results"),
    service: TrackingEngineService = Depends(get_service)
):
    """Récupère les événements avec filtres optionnels"""
    try:
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        return await service.get_events(
            session_id=session_id,
            user_id=user_id,
            event_type=event_type,
            page_url=page_url,
            start_date=start_date,
            limit=limit
        )
    except Exception as e:
        logger.error(f"Error getting events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# FUNNELS
# ============================================

@router.post("/funnels", response_model=dict, summary="Create Funnel")
async def create_funnel(
    funnel: FunnelCreate,
    service: TrackingEngineService = Depends(get_service)
):
    """
    Crée un nouveau funnel de conversion.
    
    Exemple de funnel "Inscription":
    - Step 1: page_view sur /signup
    - Step 2: click sur signup_form_submit
    - Step 3: page_view sur /welcome
    """
    try:
        result = await service.create_funnel(funnel)
        return {"success": True, "funnel": result.model_dump()}
    except Exception as e:
        logger.error(f"Error creating funnel: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/funnels", response_model=List[dict], summary="List Funnels")
async def list_funnels(
    active_only: bool = Query(True, description="Show only active funnels"),
    service: TrackingEngineService = Depends(get_service)
):
    """Liste tous les funnels de conversion"""
    try:
        return await service.get_funnels(active_only)
    except Exception as e:
        logger.error(f"Error listing funnels: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/funnels/{funnel_id}", response_model=dict, summary="Get Funnel")
async def get_funnel(
    funnel_id: str,
    service: TrackingEngineService = Depends(get_service)
):
    """Récupère un funnel par ID"""
    try:
        funnel = await service.get_funnel(funnel_id)
        if not funnel:
            raise HTTPException(status_code=404, detail="Funnel not found")
        return {"success": True, "funnel": funnel}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting funnel: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/funnels/{funnel_id}", summary="Delete Funnel")
async def delete_funnel(
    funnel_id: str,
    service: TrackingEngineService = Depends(get_service)
):
    """Supprime un funnel"""
    try:
        deleted = await service.delete_funnel(funnel_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Funnel not found")
        return {"success": True, "message": "Funnel deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting funnel: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/funnels/{funnel_id}/analyze", response_model=FunnelAnalysis, summary="Analyze Funnel")
async def analyze_funnel(
    funnel_id: str,
    days: int = Query(30, ge=1, le=365, description="Look back period in days"),
    service: TrackingEngineService = Depends(get_service)
):
    """
    Analyse les performances d'un funnel de conversion.
    
    Retourne:
    - Nombre total de sessions ayant commencé le funnel
    - Nombre de sessions ayant complété le funnel
    - Taux de conversion global
    - Analyse étape par étape avec taux d'abandon
    """
    try:
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        end_date = datetime.now(timezone.utc)
        return await service.analyze_funnel(funnel_id, start_date, end_date)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error analyzing funnel: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# HEATMAPS
# ============================================

@router.get("/heatmap", response_model=HeatmapData, summary="Get Heatmap Data")
async def get_heatmap_data(
    page_url: str = Query(..., description="Page URL to get heatmap for"),
    days: int = Query(30, ge=1, le=365, description="Look back period in days"),
    viewport_width: int = Query(1920, description="Viewport width"),
    viewport_height: int = Query(1080, description="Viewport height"),
    service: TrackingEngineService = Depends(get_service)
):
    """
    Génère les données de heatmap pour une page.
    
    Agrège tous les clics sur la page spécifiée et retourne
    les coordonnées groupées pour visualisation.
    """
    try:
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        return await service.get_heatmap_data(
            page_url=page_url,
            start_date=start_date,
            viewport_width=viewport_width,
            viewport_height=viewport_height
        )
    except Exception as e:
        logger.error(f"Error getting heatmap data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# SESSIONS & ENGAGEMENT
# ============================================

@router.get("/sessions/{session_id}", response_model=SessionSummary, summary="Get Session Summary")
async def get_session_summary(
    session_id: str,
    service: TrackingEngineService = Depends(get_service)
):
    """Récupère le résumé détaillé d'une session utilisateur"""
    try:
        summary = await service.get_session_summary(session_id)
        if not summary:
            raise HTTPException(status_code=404, detail="Session not found")
        return summary
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/engagement", response_model=EngagementMetrics, summary="Get Engagement Metrics")
async def get_engagement_metrics(
    days: int = Query(30, ge=1, le=365, description="Look back period in days"),
    service: TrackingEngineService = Depends(get_service)
):
    """
    Calcule les métriques d'engagement globales.
    
    Inclut:
    - Sessions totales et utilisateurs uniques
    - Vues de page et événements
    - Taux de rebond
    - Pages par session
    - Top pages et événements
    - Répartition par appareil et pays
    """
    try:
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        end_date = datetime.now(timezone.utc)
        return await service.get_engagement_metrics(start_date, end_date)
    except Exception as e:
        logger.error(f"Error getting engagement metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# DEMO DATA
# ============================================

@router.post("/seed", summary="Seed Demo Data")
async def seed_demo_data(
    service: TrackingEngineService = Depends(get_service)
):
    """
    Génère des données de démonstration pour tester le tracking engine.
    
    Crée ~500 événements répartis sur 30 sessions simulées.
    """
    try:
        count = await service.seed_demo_data()
        return {
            "success": True,
            "message": f"{count} événements de démonstration créés",
            "count": count
        }
    except Exception as e:
        logger.error(f"Error seeding demo data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
