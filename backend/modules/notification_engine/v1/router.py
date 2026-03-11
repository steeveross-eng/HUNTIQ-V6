"""Notification Engine Router - MÉTIER

FastAPI router for notification endpoints.

Version: 1.0.0
API Prefix: /api/v1/notification
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from .service import NotificationService
from .models import (
    NotificationType, NotificationChannel,
    SendNotificationRequest, BroadcastRequest
)

router = APIRouter(prefix="/api/v1/notification", tags=["Notification Engine"])

# Initialize service
_service = NotificationService()


@router.get("/")
async def notification_engine_info():
    """Get notification engine information"""
    return {
        "module": "notification_engine",
        "version": "1.0.0",
        "description": "Multi-channel notification system",
        "features": [
            "In-app notifications",
            "Email notifications",
            "Push notifications",
            "SMS notifications",
            "Notification preferences",
            "Templates"
        ],
        "types": [t.value for t in NotificationType],
        "channels": [c.value for c in NotificationChannel]
    }


@router.post("/send")
async def send_notification(request: SendNotificationRequest):
    """Send a notification to a user"""
    notification = await _service.send_notification(
        user_id=request.user_id,
        notification_type=request.type,
        title=request.title,
        message=request.message,
        channels=request.channels,
        priority=request.priority,
        data=request.data,
        action_url=request.action_url
    )
    
    return {
        "success": True,
        "notification": notification.model_dump()
    }


@router.post("/broadcast")
async def broadcast_notification(request: BroadcastRequest):
    """Broadcast notification to multiple users"""
    if not request.user_ids:
        raise HTTPException(status_code=400, detail="User IDs required for broadcast")
    
    sent_count = await _service.broadcast(
        user_ids=request.user_ids,
        notification_type=request.type,
        title=request.title,
        message=request.message,
        channels=request.channels
    )
    
    return {
        "success": True,
        "sent_count": sent_count,
        "total_users": len(request.user_ids)
    }


@router.get("/user/{user_id}")
async def get_user_notifications(
    user_id: str,
    unread_only: bool = Query(False),
    type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200)
):
    """Get notifications for a user"""
    notification_type = None
    if type:
        try:
            notification_type = NotificationType(type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid notification type: {type}")
    
    notifications = await _service.get_notifications(
        user_id=user_id,
        unread_only=unread_only,
        notification_type=notification_type,
        limit=limit
    )
    
    unread_count = await _service.get_unread_count(user_id)
    
    return {
        "success": True,
        "total": len(notifications),
        "unread_count": unread_count,
        "notifications": [n.model_dump() for n in notifications]
    }


@router.get("/user/{user_id}/unread-count")
async def get_unread_count(user_id: str):
    """Get unread notification count"""
    count = await _service.get_unread_count(user_id)
    
    return {
        "success": True,
        "unread_count": count
    }


@router.put("/{notification_id}/read")
async def mark_as_read(notification_id: str, user_id: str = Query(...)):
    """Mark notification as read"""
    success = await _service.mark_as_read(notification_id, user_id)
    
    return {
        "success": success,
        "message": "Notification marked as read" if success else "Notification not found"
    }


@router.put("/user/{user_id}/read-all")
async def mark_all_as_read(user_id: str):
    """Mark all notifications as read"""
    count = await _service.mark_all_as_read(user_id)
    
    return {
        "success": True,
        "marked_count": count
    }


@router.delete("/{notification_id}")
async def delete_notification(notification_id: str, user_id: str = Query(...)):
    """Delete a notification"""
    success = await _service.delete_notification(notification_id, user_id)
    
    return {
        "success": success,
        "message": "Notification deleted" if success else "Notification not found"
    }


@router.get("/preferences/{user_id}")
async def get_preferences(user_id: str):
    """Get user notification preferences"""
    prefs = await _service.get_preferences(user_id)
    
    return {
        "success": True,
        "preferences": prefs.model_dump()
    }


@router.put("/preferences/{user_id}")
async def update_preferences(user_id: str, prefs_data: dict):
    """Update notification preferences"""
    prefs = await _service.update_preferences(user_id, prefs_data)
    
    return {
        "success": True,
        "preferences": prefs.model_dump()
    }


@router.get("/templates")
async def get_templates(type: Optional[str] = None):
    """Get notification templates"""
    notification_type = None
    if type:
        try:
            notification_type = NotificationType(type)
        except ValueError:
            pass
    
    templates = await _service.get_templates(notification_type)
    
    return {
        "success": True,
        "templates": [t.model_dump() for t in templates]
    }


@router.get("/types")
async def list_types():
    """List all notification types"""
    return {
        "success": True,
        "types": [
            {"id": t.value, "name": _get_type_name(t)}
            for t in NotificationType
        ]
    }


@router.get("/channels")
async def list_channels():
    """List all notification channels"""
    return {
        "success": True,
        "channels": [
            {"id": c.value, "name": _get_channel_name(c)}
            for c in NotificationChannel
        ]
    }


def _get_type_name(t: NotificationType) -> str:
    names = {
        NotificationType.SYSTEM: "Système",
        NotificationType.ORDER: "Commande",
        NotificationType.PROMOTION: "Promotion",
        NotificationType.ALERT: "Alerte",
        NotificationType.MESSAGE: "Message",
        NotificationType.REMINDER: "Rappel"
    }
    return names.get(t, t.value)


def _get_channel_name(c: NotificationChannel) -> str:
    names = {
        NotificationChannel.IN_APP: "Dans l'application",
        NotificationChannel.EMAIL: "Courriel",
        NotificationChannel.PUSH: "Notification push",
        NotificationChannel.SMS: "SMS"
    }
    return names.get(c, c.value)



# ==========================================
# LEGAL TIME ALERTS (P1 - Phase 11)
# ==========================================

@router.get("/legal-time/status")
async def get_legal_time_status(
    lat: float = Query(46.8139, description="Latitude"),
    lng: float = Query(-71.2080, description="Longitude")
):
    """
    Get current legal time status for notifications.
    
    Returns whether a warning should be displayed.
    """
    from modules.legal_time_engine.v1.service import LegalTimeService
    from modules.legal_time_engine.v1.models import LocationInput
    from datetime import datetime
    from zoneinfo import ZoneInfo
    
    service = LegalTimeService()
    location = LocationInput(latitude=lat, longitude=lng, timezone="America/Toronto")
    tz = ZoneInfo("America/Toronto")
    now = datetime.now(tz)
    
    # Get legal window
    legal_window = service.get_legal_hunting_window(now.date(), location)
    
    # Calculate time remaining if in legal period
    is_legal = legal_window.is_currently_legal
    warning_active = False
    minutes_remaining = 0
    
    if is_legal:
        legal_end_dt = datetime.combine(now.date(), legal_window.end_time, tzinfo=tz)
        minutes_remaining = int((legal_end_dt - now).total_seconds() / 60)
        warning_active = minutes_remaining <= 15
    
    return {
        "success": True,
        "current_time": now.strftime("%H:%M:%S"),
        "is_legal_period": is_legal,
        "legal_window": {
            "start": legal_window.start_time.strftime("%H:%M"),
            "end": legal_window.end_time.strftime("%H:%M")
        },
        "warning_active": warning_active,
        "minutes_remaining": minutes_remaining if is_legal else None,
        "alert": {
            "type": "legal_time_warning",
            "title": f"⏰ Fin de période dans {minutes_remaining} min",
            "body": f"La chasse se termine à {legal_window.end_time.strftime('%H:%M')}",
            "priority": "urgent" if minutes_remaining <= 5 else "high" if minutes_remaining <= 10 else "medium"
        } if warning_active else None
    }


@router.get("/legal-time/upcoming")
async def get_upcoming_legal_alerts(
    lat: float = Query(46.8139, description="Latitude"),
    lng: float = Query(-71.2080, description="Longitude"),
    hours: int = Query(24, ge=1, le=48, description="Hours to look ahead")
):
    """
    Get upcoming legal time notifications.
    
    Returns scheduled alerts for the next N hours.
    """
    from modules.legal_time_engine.v1.service import LegalTimeService
    from modules.legal_time_engine.v1.models import LocationInput
    from datetime import datetime, timedelta
    from zoneinfo import ZoneInfo
    
    service = LegalTimeService()
    location = LocationInput(latitude=lat, longitude=lng, timezone="America/Toronto")
    tz = ZoneInfo("America/Toronto")
    now = datetime.now(tz)
    
    notifications = []
    
    # Check today and tomorrow
    for day_offset in range(2):
        target_date = now.date() + timedelta(days=day_offset)
        legal_window = service.get_legal_hunting_window(target_date, location)
        
        # Legal start
        start_dt = datetime.combine(target_date, legal_window.start_time, tzinfo=tz)
        if now < start_dt < now + timedelta(hours=hours):
            notifications.append({
                "type": "legal_time_start",
                "scheduled_time": start_dt.isoformat(),
                "title": "🌅 Début période légale",
                "body": f"La chasse est autorisée à {legal_window.start_time.strftime('%H:%M')}",
                "priority": "medium"
            })
        
        # Warning (15 min before end)
        end_dt = datetime.combine(target_date, legal_window.end_time, tzinfo=tz)
        warning_dt = end_dt - timedelta(minutes=15)
        if now < warning_dt < now + timedelta(hours=hours):
            notifications.append({
                "type": "legal_time_warning",
                "scheduled_time": warning_dt.isoformat(),
                "title": "⏰ 15 min avant fin",
                "body": f"Préparez-vous, fin de chasse à {legal_window.end_time.strftime('%H:%M')}",
                "priority": "high"
            })
        
        # Legal end
        if now < end_dt < now + timedelta(hours=hours):
            notifications.append({
                "type": "legal_time_end",
                "scheduled_time": end_dt.isoformat(),
                "title": "🌙 Fin période légale",
                "body": "La chasse n'est plus autorisée",
                "priority": "urgent"
            })
    
    notifications.sort(key=lambda x: x["scheduled_time"])
    
    return {
        "success": True,
        "count": len(notifications),
        "hours_ahead": hours,
        "notifications": notifications
    }
