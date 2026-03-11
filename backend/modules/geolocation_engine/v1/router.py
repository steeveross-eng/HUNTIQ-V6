"""
Geolocation Engine - API Router
Phase P4 - Background Geolocation & Proximity Alerts

Endpoints:
- POST /location - Record location update
- GET /history - Get location history
- POST /session/start - Start tracking session
- POST /session/end - End tracking session
- POST /subscribe - Subscribe to push notifications
- DELETE /subscribe - Unsubscribe from push notifications
- GET /nearby-hotspots - Get nearby hotspot waypoints
- POST /check-proximity - Check proximity to waypoints
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

from .models import (
    LocationUpdate, PushSubscription, PushNotification
)
from .service import GeolocationService

# Import auth helpers
from auth_helpers import get_user_id_with_fallback

# Database dependency
def get_db() -> AsyncIOMotorDatabase:
    from database import Database
    return Database.get_database()

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/geolocation",
    tags=["Geolocation Engine"]
)


@router.get("/")
async def geolocation_info():
    """Get geolocation engine info"""
    return {
        "module": "geolocation_engine",
        "version": "1.0.0",
        "phase": "P4",
        "description": "Background geolocation tracking and proximity alerts",
        "features": [
            "Background location tracking (5-minute intervals)",
            "Proximity alerts for hotspot waypoints",
            "Web Push notifications",
            "Tracking sessions for hunting trips",
            "Location history and statistics"
        ],
        "endpoints": {
            "POST /location": "Record location update",
            "GET /history": "Get location history",
            "POST /session/start": "Start tracking session",
            "POST /session/{id}/end": "End tracking session",
            "POST /subscribe": "Subscribe to push notifications",
            "DELETE /subscribe": "Unsubscribe from push",
            "GET /nearby-hotspots": "Get nearby waypoints",
            "POST /check-proximity": "Manual proximity check"
        }
    }


@router.post("/location", response_model=dict)
async def record_location(
    location: LocationUpdate,
    request: Request,
    session_id: Optional[str] = None,
    user_id: str = Depends(get_user_id_with_fallback),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Record a location update from background tracking.
    Returns the saved location and any proximity alerts triggered.
    """
    service = GeolocationService(db)
    
    try:
        location_record, alerts = await service.record_location(
            user_id=user_id,
            location=location,
            session_id=session_id
        )
        
        return {
            "success": True,
            "location": {
                "id": location_record.id,
                "latitude": location_record.latitude,
                "longitude": location_record.longitude,
                "timestamp": location_record.timestamp.isoformat()
            },
            "alerts": [alert.dict() for alert in alerts],
            "alerts_count": len(alerts)
        }
    except Exception as e:
        logger.error(f"Error recording location: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=List[dict])
async def get_location_history(
    request: Request,
    session_id: Optional[str] = None,
    limit: int = 100,
    user_id: str = Depends(get_user_id_with_fallback),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get location history for user"""
    service = GeolocationService(db)
    
    history = await service.get_location_history(
        user_id=user_id,
        session_id=session_id,
        limit=limit
    )
    
    return [
        {
            "id": loc.id,
            "latitude": loc.latitude,
            "longitude": loc.longitude,
            "accuracy": loc.accuracy,
            "timestamp": loc.timestamp.isoformat(),
            "session_id": loc.session_id
        }
        for loc in history
    ]


@router.post("/session/start", response_model=dict)
async def start_tracking_session(
    request: Request,
    user_id: str = Depends(get_user_id_with_fallback),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Start a new tracking session for a hunting trip"""
    service = GeolocationService(db)
    
    session = await service.start_tracking_session(user_id)
    
    return {
        "success": True,
        "session": {
            "id": session.id,
            "started_at": session.started_at.isoformat(),
            "active": session.active
        },
        "message": "Session de tracking démarrée"
    }


@router.post("/session/{session_id}/end", response_model=dict)
async def end_tracking_session(
    session_id: str,
    request: Request,
    user_id: str = Depends(get_user_id_with_fallback),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """End a tracking session and get statistics"""
    service = GeolocationService(db)
    
    session = await service.end_tracking_session(user_id, session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    
    return {
        "success": True,
        "session": {
            "id": session.id,
            "started_at": session.started_at.isoformat(),
            "ended_at": session.ended_at.isoformat() if session.ended_at else None,
            "locations_count": session.locations_count,
            "distance_km": session.distance_km,
            "active": session.active
        },
        "message": f"Session terminée. Distance parcourue: {session.distance_km} km"
    }


@router.post("/subscribe", response_model=dict)
async def subscribe_push(
    subscription: PushSubscription,
    request: Request,
    user_id: str = Depends(get_user_id_with_fallback),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Subscribe to push notifications for proximity alerts"""
    service = GeolocationService(db)
    
    success = await service.save_push_subscription(user_id, subscription)
    
    return {
        "success": success,
        "message": "Abonnement aux notifications activé" if success else "Erreur d'abonnement"
    }


@router.delete("/subscribe", response_model=dict)
async def unsubscribe_push(
    request: Request,
    user_id: str = Depends(get_user_id_with_fallback),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Unsubscribe from push notifications"""
    service = GeolocationService(db)
    
    success = await service.remove_push_subscription(user_id)
    
    return {
        "success": success,
        "message": "Désabonnement effectué" if success else "Aucun abonnement trouvé"
    }


@router.get("/nearby-hotspots", response_model=dict)
async def get_nearby_hotspots(
    lat: float,
    lng: float,
    request: Request,
    radius_km: float = 5.0,
    user_id: str = Depends(get_user_id_with_fallback),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get hotspot waypoints near a location"""
    service = GeolocationService(db)
    
    hotspots = await service.get_nearby_hotspots(
        user_id=user_id,
        lat=lat,
        lng=lng,
        radius_km=radius_km
    )
    
    return {
        "center": {"lat": lat, "lng": lng},
        "radius_km": radius_km,
        "hotspots": hotspots,
        "count": len(hotspots)
    }


@router.post("/check-proximity", response_model=dict)
async def check_proximity(
    lat: float,
    lng: float,
    request: Request,
    user_id: str = Depends(get_user_id_with_fallback),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Manually check proximity to waypoints"""
    service = GeolocationService(db)
    
    alerts = await service.check_proximity_alerts(user_id, lat, lng)
    
    return {
        "position": {"lat": lat, "lng": lng},
        "alerts": [alert.dict() for alert in alerts],
        "alerts_count": len(alerts),
        "has_alerts": len(alerts) > 0
    }


@router.post("/notify", response_model=dict)
async def send_notification(
    notification: PushNotification,
    request: Request,
    user_id: str = Depends(get_user_id_with_fallback),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Send a push notification to user (admin/test endpoint)"""
    service = GeolocationService(db)
    
    success = await service.send_push_notification(user_id, notification)
    
    return {
        "success": success,
        "message": "Notification envoyée" if success else "Échec de l'envoi"
    }


@router.get("/tracking-status", response_model=dict)
async def get_tracking_status(
    request: Request,
    user_id: str = Depends(get_user_id_with_fallback),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get current tracking status for user"""
    service = GeolocationService(db)
    
    # Check for active session
    active_session = await service.sessions_collection.find_one({
        "user_id": user_id,
        "active": True
    })
    
    # Check for push subscription
    has_subscription = await service.get_push_subscription(user_id) is not None
    
    # Get recent location count
    recent_locations = await service.locations_collection.count_documents({
        "user_id": user_id
    })
    
    return {
        "tracking_active": active_session is not None,
        "session_id": str(active_session["_id"]) if active_session else None,
        "push_enabled": has_subscription,
        "total_locations": recent_locations,
        "features": {
            "background_tracking": True,
            "proximity_alerts": True,
            "push_notifications": has_subscription,
            "session_tracking": True
        }
    }
