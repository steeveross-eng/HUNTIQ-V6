"""
Waypoint Engine V1 - API Router
================================
Endpoints for waypoint management.
Architecture LEGO V5 - Module isolé.
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
import os
import logging

from .models import WaypointCreate, WaypointUpdate
from .service import WaypointEngineService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/waypoints",
    tags=["Waypoint Engine V1"],
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


def get_service() -> WaypointEngineService:
    return WaypointEngineService(get_db())


# ============================================
# MODULE INFO
# ============================================

@router.get("/", summary="Module Info")
async def get_module_info(service: WaypointEngineService = Depends(get_service)):
    """Get waypoint engine module information"""
    stats = await service.get_stats()
    return {
        "module": "waypoint_engine",
        "version": "1.0.0",
        "description": "Moteur de gestion des waypoints utilisateur",
        "features": [
            "Create waypoints from map interaction",
            "GPS tracking waypoints",
            "Waypoint filtering by source/user",
            "Geographic bounds queries",
            "Waypoint statistics"
        ],
        "stats": stats
    }


# ============================================
# WAYPOINT CRUD
# ============================================

@router.post("/create", summary="Create Waypoint")
async def create_waypoint(
    data: WaypointCreate,
    service: WaypointEngineService = Depends(get_service)
):
    """
    Create a new waypoint.
    
    Sources supportées:
    - user_double_click: Création via double-clic sur la carte
    - user_manual: Création manuelle (formulaire)
    - gps_tracking: Tracking GPS automatique
    - import: Import externe
    - ai_suggestion: Suggestion IA
    """
    try:
        waypoint = await service.create_waypoint(data)
        return {"success": True, "waypoint": waypoint}
    except Exception as e:
        logger.error(f"Error creating waypoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", summary="List Waypoints")
async def list_waypoints(
    user_id: Optional[str] = Query(None, description="Filter by user"),
    source: Optional[str] = Query(None, description="Filter by source"),
    limit: int = Query(100, ge=1, le=1000),
    service: WaypointEngineService = Depends(get_service)
):
    """List waypoints with optional filters"""
    try:
        waypoints = await service.get_waypoints(user_id, source, limit)
        return {"success": True, "total": len(waypoints), "waypoints": waypoints}
    except Exception as e:
        logger.error(f"Error listing waypoints: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bounds", summary="Get Waypoints in Bounds")
async def get_waypoints_in_bounds(
    north: float = Query(..., ge=-90, le=90),
    south: float = Query(..., ge=-90, le=90),
    east: float = Query(..., ge=-180, le=180),
    west: float = Query(..., ge=-180, le=180),
    user_id: Optional[str] = Query(None),
    limit: int = Query(500, ge=1, le=5000),
    service: WaypointEngineService = Depends(get_service)
):
    """Get waypoints within geographic bounds"""
    try:
        waypoints = await service.get_waypoints_in_bounds(
            north, south, east, west, user_id, limit
        )
        return {"success": True, "total": len(waypoints), "waypoints": waypoints}
    except Exception as e:
        logger.error(f"Error getting waypoints in bounds: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", summary="Get Waypoint Stats")
async def get_stats(
    user_id: Optional[str] = Query(None),
    service: WaypointEngineService = Depends(get_service)
):
    """Get waypoint statistics"""
    try:
        stats = await service.get_stats(user_id)
        return {"success": True, "stats": stats}
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{waypoint_id}", summary="Get Waypoint")
async def get_waypoint(
    waypoint_id: str,
    service: WaypointEngineService = Depends(get_service)
):
    """Get a single waypoint by ID"""
    try:
        waypoint = await service.get_waypoint(waypoint_id)
        if not waypoint:
            raise HTTPException(status_code=404, detail="Waypoint not found")
        return {"success": True, "waypoint": waypoint}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting waypoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{waypoint_id}", summary="Update Waypoint")
async def update_waypoint(
    waypoint_id: str,
    data: WaypointUpdate,
    service: WaypointEngineService = Depends(get_service)
):
    """Update a waypoint"""
    try:
        waypoint = await service.update_waypoint(waypoint_id, data)
        if not waypoint:
            raise HTTPException(status_code=404, detail="Waypoint not found")
        return {"success": True, "waypoint": waypoint}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating waypoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{waypoint_id}", summary="Delete Waypoint")
async def delete_waypoint(
    waypoint_id: str,
    service: WaypointEngineService = Depends(get_service)
):
    """Delete a waypoint"""
    try:
        deleted = await service.delete_waypoint(waypoint_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Waypoint not found")
        return {"success": True, "deleted": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting waypoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
