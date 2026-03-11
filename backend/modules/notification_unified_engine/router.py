"""
Notification Unified Engine Router - V5-ULTIME-FUSION
=====================================================

Fusion de notification_engine (V4) + communication_engine (BASE)

Endpoints unifiés:
- /api/v1/notifications/* - Core notification functions
- /api/v1/notifications/email/* - Email templates (unifié)

Version: 1.0.0
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from enum import Enum
import os
import logging
import uuid
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/notifications", tags=["Notification Unified Engine"])

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'bionic_db')
_client = None
_db = None

def get_db():
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(MONGO_URL)
        _db = _client[DB_NAME]
    return _db

# ==============================================
# MODELS
# ==============================================

class NotificationType(str, Enum):
    SYSTEM = "system"
    ORDER = "order"
    PROMOTION = "promotion"
    ALERT = "alert"
    MESSAGE = "message"
    REMINDER = "reminder"
    LEGAL_TIME = "legal_time"
    INFO = "info"
    WARNING = "warning"

class NotificationChannel(str, Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"

class NotificationPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class SendNotificationRequest(BaseModel):
    user_id: str
    type: NotificationType = NotificationType.INFO
    title: str
    message: str
    channels: List[NotificationChannel] = [NotificationChannel.IN_APP]
    priority: NotificationPriority = NotificationPriority.NORMAL
    data: Optional[Dict[str, Any]] = None
    action_url: Optional[str] = None

class BroadcastRequest(BaseModel):
    user_ids: List[str]
    type: NotificationType = NotificationType.SYSTEM
    title: str
    message: str
    channels: List[NotificationChannel] = [NotificationChannel.IN_APP]

class NotificationPreferences(BaseModel):
    user_id: str
    email_enabled: bool = True
    push_enabled: bool = True
    sms_enabled: bool = False
    in_app_enabled: bool = True
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    types_disabled: List[str] = []

class EmailTemplate(BaseModel):
    name: str
    subject: str
    html_content: str
    category: str = "general"
    variables: List[str] = []

# ==============================================
# MODULE INFO
# ==============================================

@router.get("/")
async def notification_engine_info():
    """Get notification unified engine information"""
    return {
        "module": "notification_unified_engine",
        "version": "1.0.0",
        "description": "Système de notifications unifié V5-ULTIME-FUSION",
        "fusion": ["notification_engine (V4)", "communication_engine (BASE)"],
        "features": [
            "In-app notifications",
            "Email notifications",
            "Push notifications",
            "SMS notifications",
            "Notification preferences",
            "Email templates",
            "Legal time alerts",
            "Broadcast messaging"
        ],
        "types": [t.value for t in NotificationType],
        "channels": [c.value for c in NotificationChannel],
        "priorities": [p.value for p in NotificationPriority]
    }

# ==============================================
# SEND NOTIFICATIONS
# ==============================================

@router.post("/send")
async def send_notification(request: SendNotificationRequest):
    """Send a notification to a user"""
    db = get_db()
    
    notification = {
        "id": str(uuid.uuid4()),
        "user_id": request.user_id,
        "type": request.type.value,
        "title": request.title,
        "message": request.message,
        "channels": [c.value for c in request.channels],
        "priority": request.priority.value,
        "data": request.data or {},
        "action_url": request.action_url,
        "read": False,
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.notifications.insert_one(notification)
    del notification["_id"]
    
    return {"success": True, "notification": notification}

@router.post("/broadcast")
async def broadcast_notification(request: BroadcastRequest):
    """Broadcast notification to multiple users"""
    if not request.user_ids:
        raise HTTPException(status_code=400, detail="User IDs required for broadcast")
    
    db = get_db()
    sent_count = 0
    
    for user_id in request.user_ids:
        notification = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "type": request.type.value,
            "title": request.title,
            "message": request.message,
            "channels": [c.value for c in request.channels],
            "priority": NotificationPriority.NORMAL.value,
            "read": False,
            "created_at": datetime.now(timezone.utc)
        }
        await db.notifications.insert_one(notification)
        sent_count += 1
    
    return {
        "success": True,
        "sent_count": sent_count,
        "total_users": len(request.user_ids)
    }

# ==============================================
# GET NOTIFICATIONS
# ==============================================

@router.get("/user/{user_id}")
async def get_user_notifications(
    user_id: str,
    unread_only: bool = Query(False),
    type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200)
):
    """Get notifications for a user"""
    db = get_db()
    
    query = {"user_id": user_id}
    if unread_only:
        query["read"] = False
    if type:
        query["type"] = type
    
    notifications = await db.notifications.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    unread_count = await db.notifications.count_documents({"user_id": user_id, "read": False})
    
    return {
        "success": True,
        "total": len(notifications),
        "unread_count": unread_count,
        "notifications": notifications
    }

@router.get("/user/{user_id}/unread-count")
async def get_unread_count(user_id: str):
    """Get unread notification count"""
    db = get_db()
    count = await db.notifications.count_documents({"user_id": user_id, "read": False})
    
    return {"success": True, "unread_count": count}

# ==============================================
# MARK AS READ
# ==============================================

@router.put("/{notification_id}/read")
async def mark_as_read(notification_id: str, user_id: str = Query(...)):
    """Mark notification as read"""
    db = get_db()
    result = await db.notifications.update_one(
        {"id": notification_id, "user_id": user_id},
        {"$set": {"read": True, "read_at": datetime.now(timezone.utc)}}
    )
    
    return {
        "success": result.modified_count > 0,
        "message": "Notification marked as read" if result.modified_count > 0 else "Notification not found"
    }

@router.put("/user/{user_id}/read-all")
async def mark_all_as_read(user_id: str):
    """Mark all notifications as read"""
    db = get_db()
    result = await db.notifications.update_many(
        {"user_id": user_id, "read": False},
        {"$set": {"read": True, "read_at": datetime.now(timezone.utc)}}
    )
    
    return {"success": True, "marked_count": result.modified_count}

# ==============================================
# DELETE NOTIFICATIONS
# ==============================================

@router.delete("/{notification_id}")
async def delete_notification(notification_id: str, user_id: str = Query(...)):
    """Delete a notification"""
    db = get_db()
    result = await db.notifications.delete_one({"id": notification_id, "user_id": user_id})
    
    return {
        "success": result.deleted_count > 0,
        "message": "Notification deleted" if result.deleted_count > 0 else "Notification not found"
    }

# ==============================================
# PREFERENCES
# ==============================================

@router.get("/preferences/{user_id}")
async def get_preferences(user_id: str):
    """Get user notification preferences"""
    db = get_db()
    prefs = await db.notification_preferences.find_one({"user_id": user_id}, {"_id": 0})
    
    if not prefs:
        prefs = NotificationPreferences(user_id=user_id).dict()
    
    return {"success": True, "preferences": prefs}

@router.put("/preferences/{user_id}")
async def update_preferences(user_id: str, prefs_data: dict):
    """Update notification preferences"""
    db = get_db()
    
    prefs_data["user_id"] = user_id
    prefs_data["updated_at"] = datetime.now(timezone.utc)
    
    await db.notification_preferences.update_one(
        {"user_id": user_id},
        {"$set": prefs_data},
        upsert=True
    )
    
    return {"success": True, "preferences": prefs_data}

# ==============================================
# EMAIL TEMPLATES (Unified from BASE)
# ==============================================

@router.get("/email/templates")
async def list_templates(category: Optional[str] = None):
    """List all email templates"""
    db = get_db()
    
    query = {}
    if category:
        query["category"] = category
    
    templates = await db.email_templates.find(query, {"_id": 0}).to_list(length=100)
    return {"success": True, "templates": templates}

@router.post("/email/templates")
async def create_template(template: EmailTemplate):
    """Create or update email template"""
    db = get_db()
    
    template_dict = template.dict()
    template_dict["id"] = str(uuid.uuid4())
    template_dict["created_at"] = datetime.now(timezone.utc)
    
    # Check if template with same name exists
    existing = await db.email_templates.find_one({"name": template.name})
    if existing:
        template_dict["id"] = existing.get("id", template_dict["id"])
        template_dict["updated_at"] = datetime.now(timezone.utc)
        await db.email_templates.update_one(
            {"name": template.name},
            {"$set": template_dict}
        )
    else:
        await db.email_templates.insert_one(template_dict)
    
    if "_id" in template_dict:
        del template_dict["_id"]
    return {"success": True, "template": template_dict}

@router.get("/email/templates/{template_name}")
async def get_template(template_name: str):
    """Get specific email template"""
    db = get_db()
    template = await db.email_templates.find_one({"name": template_name}, {"_id": 0})
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return {"success": True, "template": template}

@router.delete("/email/templates/{template_name}")
async def delete_template(template_name: str):
    """Delete email template"""
    db = get_db()
    result = await db.email_templates.delete_one({"name": template_name})
    
    return {
        "success": result.deleted_count > 0,
        "message": "Template deleted" if result.deleted_count > 0 else "Template not found"
    }

# ==============================================
# NOTIFICATION TYPES & CHANNELS
# ==============================================

@router.get("/types")
async def list_types():
    """List all notification types"""
    type_names = {
        "system": "Système",
        "order": "Commande",
        "promotion": "Promotion",
        "alert": "Alerte",
        "message": "Message",
        "reminder": "Rappel",
        "legal_time": "Heure légale",
        "info": "Information",
        "warning": "Avertissement"
    }
    
    return {
        "success": True,
        "types": [
            {"id": t.value, "name": type_names.get(t.value, t.value)}
            for t in NotificationType
        ]
    }

@router.get("/channels")
async def list_channels():
    """List all notification channels"""
    channel_names = {
        "in_app": "Dans l'application",
        "email": "Courriel",
        "push": "Notification push",
        "sms": "SMS"
    }
    
    return {
        "success": True,
        "channels": [
            {"id": c.value, "name": channel_names.get(c.value, c.value)}
            for c in NotificationChannel
        ]
    }

# ==============================================
# LEGAL TIME ALERTS (from V4 notification_engine)
# ==============================================

@router.get("/legal-time/status")
async def get_legal_time_status(
    lat: float = Query(46.8139, description="Latitude"),
    lng: float = Query(-71.2080, description="Longitude")
):
    """Get current legal time status for notifications"""
    try:
        from modules.legal_time_engine.v1.service import LegalTimeService
        from modules.legal_time_engine.v1.models import LocationInput
        from zoneinfo import ZoneInfo
        
        service = LegalTimeService()
        location = LocationInput(latitude=lat, longitude=lng, timezone="America/Toronto")
        tz = ZoneInfo("America/Toronto")
        now = datetime.now(tz)
        
        legal_window = service.get_legal_hunting_window(now.date(), location)
        
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
    except ImportError:
        return {
            "success": True,
            "message": "Legal time engine not available",
            "is_legal_period": True,
            "warning_active": False
        }
    except Exception as e:
        logger.error(f"Error getting legal time status: {e}")
        return {
            "success": False,
            "error": str(e)
        }
