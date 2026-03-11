"""
Communication Engine Router
"""

from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime, timezone
import os
from motor.motor_asyncio import AsyncIOMotorClient

router = APIRouter(prefix="/api/communication", tags=["communication"])

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'bionic_db')
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

class Notification(BaseModel):
    user_id: str
    title: str
    message: str
    type: str = "info"
    priority: str = "normal"

class EmailTemplate(BaseModel):
    name: str
    subject: str
    html_content: str
    category: str = "general"

@router.post("/notifications")
async def create_notification(notif: Notification):
    notif_doc = {
        **notif.dict(),
        "created_at": datetime.now(timezone.utc),
        "read": False
    }
    await db.notifications.insert_one(notif_doc)
    return {"success": True}

@router.get("/notifications/{user_id}")
async def get_notifications(user_id: str, limit: int = 20):
    notifs = await db.notifications.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(length=limit)
    return {"success": True, "notifications": notifs}

@router.post("/notifications/{user_id}/mark-read")
async def mark_notifications_read(user_id: str):
    await db.notifications.update_many(
        {"user_id": user_id, "read": False},
        {"$set": {"read": True}}
    )
    return {"success": True}

@router.post("/email/templates")
async def create_template(template: EmailTemplate):
    template_doc = {
        **template.dict(),
        "created_at": datetime.now(timezone.utc)
    }
    await db.email_templates.insert_one(template_doc)
    return {"success": True}

@router.get("/email/templates")
async def list_templates():
    templates = await db.email_templates.find({}, {"_id": 0}).to_list(length=100)
    return {"success": True, "templates": templates}
