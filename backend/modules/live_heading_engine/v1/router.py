"""Live Heading Engine Router - PHASE 6
API endpoints for immersive live heading view.

Version: 1.0.0
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pydantic import BaseModel

from .models import (
    HeadingUpdate,
    HeadingViewState,
    POIType,
    SessionSettings,
    CreateSessionRequest,
    CreateSessionResponse
)
from .service import get_live_heading_service


router = APIRouter(
    prefix="/api/v1/live-heading",
    tags=["Live Heading Engine"]
)


# ==============================================
# RESPONSE MODELS
# ==============================================

class HealthResponse(BaseModel):
    status: str
    engine: str
    version: str
    message: str


# ==============================================
# HEALTH CHECK
# ==============================================

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check live heading engine health"""
    service = get_live_heading_service()
    stats = await service.get_stats()
    
    return HealthResponse(
        status="operational",
        engine="live_heading_engine",
        version="1.0.0",
        message=f"Engine opérationnel - {stats['active_sessions']} sessions actives"
    )


@router.get("/stats")
async def get_engine_stats():
    """Get live heading engine statistics"""
    service = get_live_heading_service()
    return await service.get_stats()


# ==============================================
# SESSION MANAGEMENT
# ==============================================

@router.post("/session/create", response_model=CreateSessionResponse)
async def create_session(request: CreateSessionRequest):
    """Create a new live heading session"""
    service = get_live_heading_service()
    
    session = await service.create_session(
        user_id=request.user_id,
        lat=request.lat,
        lng=request.lng,
        heading=request.heading,
        cone_aperture=request.cone_aperture,
        cone_range=request.cone_range
    )
    
    return CreateSessionResponse(
        success=True,
        session_id=session.id,
        message="Session Live Heading créée avec succès"
    )


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get session details"""
    service = get_live_heading_service()
    session = await service.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    
    return session.model_dump()


@router.post("/session/{session_id}/update", response_model=HeadingViewState)
async def update_session_position(session_id: str, update: HeadingUpdate):
    """Update position and get new view state"""
    if update.session_id != session_id:
        raise HTTPException(status_code=400, detail="Session ID mismatch")
    
    service = get_live_heading_service()
    view_state = await service.update_position(update)
    
    if not view_state:
        raise HTTPException(status_code=404, detail="Session non trouvée ou inactive")
    
    return view_state


@router.put("/session/{session_id}/settings")
async def update_session_settings(session_id: str, settings: SessionSettings):
    """Update session settings"""
    service = get_live_heading_service()
    session = await service.update_settings(session_id, settings)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    
    return {
        "success": True,
        "message": "Paramètres mis à jour",
        "settings": session.settings
    }


@router.post("/session/{session_id}/pause")
async def pause_session(session_id: str):
    """Pause session"""
    service = get_live_heading_service()
    success = await service.pause_session(session_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Impossible de mettre en pause")
    
    return {"success": True, "message": "Session en pause"}


@router.post("/session/{session_id}/resume")
async def resume_session(session_id: str):
    """Resume paused session"""
    service = get_live_heading_service()
    success = await service.resume_session(session_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Impossible de reprendre")
    
    return {"success": True, "message": "Session reprise"}


@router.post("/session/{session_id}/end")
async def end_session(session_id: str):
    """End session and get summary"""
    service = get_live_heading_service()
    summary = await service.end_session(session_id)
    
    if not summary:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    
    return {
        "success": True,
        "message": "Session terminée",
        "summary": summary
    }


# ==============================================
# ALERTS
# ==============================================

@router.post("/session/{session_id}/alert/{alert_id}/acknowledge")
async def acknowledge_alert(session_id: str, alert_id: str):
    """Acknowledge an alert"""
    service = get_live_heading_service()
    success = await service.acknowledge_alert(session_id, alert_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Alerte non trouvée")
    
    return {"success": True, "message": "Alerte acquittée"}


# ==============================================
# POINTS OF INTEREST
# ==============================================

@router.post("/session/{session_id}/poi")
async def add_poi(
    session_id: str,
    poi_type: str,
    lat: float = Query(...),
    lng: float = Query(...),
    name: Optional[str] = None,
    description: Optional[str] = None
):
    """Add a point of interest during session"""
    try:
        poi_type_enum = POIType(poi_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Type de POI invalide. Valeurs possibles: {[t.value for t in POIType]}"
        )
    
    service = get_live_heading_service()
    poi = await service.add_poi(
        session_id, poi_type_enum, lat, lng, name, description
    )
    
    return {
        "success": True,
        "poi": poi.model_dump()
    }


@router.get("/session/{session_id}/pois")
async def get_session_pois(session_id: str):
    """Get all POIs for a session"""
    service = get_live_heading_service()
    pois = await service.get_session_pois(session_id)
    
    return {
        "count": len(pois),
        "pois": [p.model_dump() for p in pois]
    }


# ==============================================
# REFERENCE DATA
# ==============================================

@router.get("/reference/poi-types")
async def get_poi_types():
    """Get available POI types"""
    service = get_live_heading_service()
    
    return {
        "poi_types": [
            {
                "type": poi_type.value,
                "name": poi_type.value.replace("_", " ").title(),
                "icon": service.poi_configs.get(poi_type, {}).get("icon", "📍"),
                "color": service.poi_configs.get(poi_type, {}).get("color", "#64748b")
            }
            for poi_type in POIType
        ]
    }


@router.get("/reference/default-settings")
async def get_default_settings():
    """Get default session settings"""
    return {
        "cone_aperture": 60,
        "cone_range": 500,
        "auto_rotate_map": True,
        "show_wind_indicator": True,
        "show_terrain": True,
        "show_trails": True,
        "show_group_members": True,
        "alert_sounds": True,
        "vibrate_on_alert": True
    }
