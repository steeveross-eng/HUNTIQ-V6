"""
Camera Engine - API Router
Phase 1: Camera management and email ingestion endpoints
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..dependencies import get_camera_db
from .models import (
    CameraCreate, CameraUpdate, CameraResponse, CameraListResponse,
    CameraEventResponse, CameraEventListResponse,
    EmailIngestionRequest, EmailIngestionResponse
)
from .services import CameraRegistryService, EmailIngestionService
from ...roles_engine.v1.dependencies import get_current_user_with_role
from ...roles_engine.v1.models import UserWithRole

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/camera", tags=["Camera Engine"])


# ============================================
# CAMERA MANAGEMENT ENDPOINTS
# ============================================

@router.post("/cameras", response_model=CameraResponse, status_code=201)
async def create_camera(
    data: CameraCreate,
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db)
):
    """
    Create a new camera.
    
    RÈGLE ABSOLUE: waypoint_id est OBLIGATOIRE.
    Une caméra sans waypoint sera rejetée.
    """
    service = CameraRegistryService(db)
    camera, error = await service.create_camera(user.user_id, data)
    
    if error:
        logger.warning(f"Camera creation rejected for user {user.user_id}: {error}")
        raise HTTPException(status_code=400, detail=error)
    
    return CameraResponse(**camera.model_dump())


@router.get("/cameras", response_model=CameraListResponse)
async def list_cameras(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db)
):
    """List all cameras for the current user."""
    service = CameraRegistryService(db)
    cameras, total = await service.list_cameras(user.user_id, skip, limit)
    
    return CameraListResponse(
        cameras=[CameraResponse(**c.model_dump()) for c in cameras],
        total=total
    )


@router.get("/cameras/{camera_id}", response_model=CameraResponse)
async def get_camera(
    camera_id: str,
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db)
):
    """Get camera details by ID."""
    service = CameraRegistryService(db)
    camera = await service.get_camera(camera_id, user.user_id)
    
    if not camera:
        raise HTTPException(status_code=404, detail="Caméra non trouvée")
    
    return CameraResponse(**camera.model_dump())


@router.patch("/cameras/{camera_id}", response_model=CameraResponse)
async def update_camera(
    camera_id: str,
    data: CameraUpdate,
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db)
):
    """
    Update camera details.
    
    Note: Le waypoint_id ne peut pas être modifié ou supprimé.
    """
    service = CameraRegistryService(db)
    camera, error = await service.update_camera(camera_id, user.user_id, data)
    
    if error:
        raise HTTPException(status_code=404, detail=error)
    
    return CameraResponse(**camera.model_dump())


@router.delete("/cameras/{camera_id}", status_code=204)
async def delete_camera(
    camera_id: str,
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db)
):
    """Delete (deactivate) a camera."""
    service = CameraRegistryService(db)
    success = await service.delete_camera(camera_id, user.user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Caméra non trouvée")
    
    return None


# ============================================
# EMAIL INGESTION ENDPOINT
# ============================================

@router.post("/email-ingest", response_model=EmailIngestionResponse)
async def ingest_email(
    request: EmailIngestionRequest,
    background_tasks: BackgroundTasks,
    db: AsyncIOMotorDatabase = Depends(get_camera_db)
):
    """
    Process incoming email with photo attachments.
    
    This endpoint is called by the email forwarding service.
    
    RÈGLES:
    - L'email doit être envoyé à l'alias email de la caméra
    - La caméra DOIT avoir un waypoint associé
    - Seules les images sont traitées
    
    Statuts possibles:
    - SUCCESS: Photo ingérée et événement créé
    - FAILED: Rejet (caméra non trouvée, pas de waypoint, pas d'image)
    - QUARANTINED: Erreur lors du traitement
    """
    service = EmailIngestionService(db)
    response = await service.process_email(request)
    
    return response


# ============================================
# CAMERA EVENTS ENDPOINTS
# ============================================

@router.get("/events", response_model=CameraEventListResponse)
async def list_events(
    camera_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db)
):
    """List camera events for user."""
    service = EmailIngestionService(db)
    events, total = await service.get_events(user.user_id, camera_id, skip, limit)
    
    return CameraEventListResponse(
        events=[CameraEventResponse(
            id=e.id,
            user_id=e.user_id,
            camera_id=e.camera_id,
            waypoint_id=e.waypoint_id,
            timestamp=e.timestamp,
            species=e.species,
            direction=e.direction,
            activity=e.activity,
            individual_id=e.individual_id,
            thumbnail_url=e.thumbnail_url,
            is_quarantined=e.is_quarantined,
            created_at=e.created_at
        ) for e in events],
        total=total
    )


@router.get("/events/{event_id}", response_model=CameraEventResponse)
async def get_event(
    event_id: str,
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db)
):
    """Get camera event details."""
    service = EmailIngestionService(db)
    event = await service.get_event(event_id, user.user_id)
    
    if not event:
        raise HTTPException(status_code=404, detail="Événement non trouvé")
    
    return CameraEventResponse(
        id=event.id,
        user_id=event.user_id,
        camera_id=event.camera_id,
        waypoint_id=event.waypoint_id,
        timestamp=event.timestamp,
        species=event.species,
        direction=event.direction,
        activity=event.activity,
        individual_id=event.individual_id,
        thumbnail_url=event.thumbnail_url,
        is_quarantined=event.is_quarantined,
        created_at=event.created_at
    )


# ============================================
# INGESTION LOGS ENDPOINT
# ============================================

@router.get("/ingestion-logs")
async def get_ingestion_logs(
    camera_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db)
):
    """Get ingestion logs for debugging and monitoring."""
    service = EmailIngestionService(db)
    logs = await service.get_ingestion_logs(user.user_id, camera_id, limit)
    
    return {
        "logs": [log.model_dump() for log in logs],
        "total": len(logs)
    }
