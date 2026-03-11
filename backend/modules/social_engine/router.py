"""
Social Engine Router - API Endpoints
Version modulaire pour V5-ULTIME-FUSION
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import os
from motor.motor_asyncio import AsyncIOMotorClient

router = APIRouter(prefix="/api/social", tags=["social"])

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'bionic_db')
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# ==================== MODELS ====================

class HuntingGroup(BaseModel):
    name: str
    description: Optional[str] = None
    territory_id: Optional[str] = None
    max_members: int = 10
    is_private: bool = False

class GroupMessage(BaseModel):
    group_id: str
    content: str
    message_type: str = "text"

class ReferralCode(BaseModel):
    code: str
    reward_type: str = "discount"
    reward_value: float = 10.0

# ==================== NETWORKING ====================

@router.get("/network/stats")
async def get_network_stats():
    groups_count = await db.hunting_groups.count_documents({})
    members_count = await db.group_members.count_documents({})
    return {"groups": groups_count, "total_members": members_count}

# ==================== HUNTING GROUPS ====================

@router.post("/groups")
async def create_group(group: HuntingGroup):
    group_doc = {
        **group.dict(),
        "created_at": datetime.now(timezone.utc),
        "members": [],
        "status": "active"
    }
    result = await db.hunting_groups.insert_one(group_doc)
    return {"success": True, "group_id": str(result.inserted_id)}

@router.get("/groups")
async def list_groups(limit: int = 20):
    groups = await db.hunting_groups.find({"status": "active"}, {"_id": 0}).limit(limit).to_list(length=limit)
    return {"success": True, "groups": groups}

@router.get("/groups/{group_id}")
async def get_group(group_id: str):
    group = await db.hunting_groups.find_one({"_id": group_id}, {"_id": 0})
    if not group:
        raise HTTPException(status_code=404, detail="Groupe non trouvé")
    return {"success": True, "group": group}

# ==================== GROUP CHAT ====================

@router.post("/chat/send")
async def send_message(message: GroupMessage):
    msg_doc = {
        **message.dict(),
        "timestamp": datetime.now(timezone.utc),
        "status": "sent"
    }
    await db.group_messages.insert_one(msg_doc)
    return {"success": True}

@router.get("/chat/{group_id}")
async def get_messages(group_id: str, limit: int = 50):
    messages = await db.group_messages.find(
        {"group_id": group_id},
        {"_id": 0}
    ).sort("timestamp", -1).limit(limit).to_list(length=limit)
    return {"success": True, "messages": messages}

# ==================== REFERRAL SYSTEM ====================

@router.post("/referral/create")
async def create_referral(referral: ReferralCode):
    ref_doc = {
        **referral.dict(),
        "created_at": datetime.now(timezone.utc),
        "uses": 0,
        "active": True
    }
    await db.referral_codes.insert_one(ref_doc)
    return {"success": True, "code": referral.code}

@router.get("/referral/{code}")
async def get_referral(code: str):
    ref = await db.referral_codes.find_one({"code": code, "active": True}, {"_id": 0})
    if not ref:
        raise HTTPException(status_code=404, detail="Code invalide")
    return {"success": True, "referral": ref}

@router.post("/referral/{code}/use")
async def use_referral(code: str):
    result = await db.referral_codes.update_one(
        {"code": code, "active": True},
        {"$inc": {"uses": 1}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Code invalide")
    return {"success": True}
