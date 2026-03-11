"""
Admin Advanced Engine Router
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import os
from motor.motor_asyncio import AsyncIOMotorClient

router = APIRouter(prefix="/api/admin-advanced", tags=["admin-advanced"])

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'bionic_db')
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

class BrandIdentity(BaseModel):
    logo_url: Optional[str] = None
    primary_color: str = "#f5a623"
    secondary_color: str = "#1a1a1a"
    site_name: str = "BIONIC HUNT/Chasse"
    tagline: Optional[str] = None

class FeatureControl(BaseModel):
    feature_id: str
    enabled: bool = True
    config: Optional[Dict[str, Any]] = None

class MaintenanceMode(BaseModel):
    enabled: bool = False
    message: str = "Site en maintenance"
    estimated_end: Optional[str] = None

class SiteAccess(BaseModel):
    public_access: bool = True
    require_auth: bool = False
    allowed_ips: list = []

# Brand Identity
@router.get("/brand")
async def get_brand():
    brand = await db.brand_identity.find_one({}, {"_id": 0})
    return {"success": True, "brand": brand or {}}

@router.post("/brand")
async def update_brand(brand: BrandIdentity):
    await db.brand_identity.update_one(
        {},
        {"$set": {**brand.dict(), "updated_at": datetime.now(timezone.utc)}},
        upsert=True
    )
    return {"success": True}

# Feature Controls
@router.get("/features")
async def list_features():
    features = await db.feature_controls.find({}, {"_id": 0}).to_list(length=100)
    return {"success": True, "features": features}

@router.post("/features")
async def update_feature(feature: FeatureControl):
    await db.feature_controls.update_one(
        {"feature_id": feature.feature_id},
        {"$set": {**feature.dict(), "updated_at": datetime.now(timezone.utc)}},
        upsert=True
    )
    return {"success": True}

@router.get("/features/{feature_id}")
async def get_feature(feature_id: str):
    feature = await db.feature_controls.find_one({"feature_id": feature_id}, {"_id": 0})
    return {"success": True, "feature": feature, "enabled": feature.get("enabled", True) if feature else True}

# Maintenance Mode
@router.get("/maintenance")
async def get_maintenance():
    maint = await db.maintenance_mode.find_one({}, {"_id": 0})
    return {"success": True, "maintenance": maint or {"enabled": False}}

@router.post("/maintenance")
async def set_maintenance(mode: MaintenanceMode):
    await db.maintenance_mode.update_one(
        {},
        {"$set": {**mode.dict(), "updated_at": datetime.now(timezone.utc)}},
        upsert=True
    )
    return {"success": True}

# Site Access
@router.get("/access")
async def get_access():
    access = await db.site_access.find_one({}, {"_id": 0})
    return {"success": True, "access": access or {"public_access": True}}

@router.post("/access")
async def set_access(access: SiteAccess):
    await db.site_access.update_one(
        {},
        {"$set": {**access.dict(), "updated_at": datetime.now(timezone.utc)}},
        upsert=True
    )
    return {"success": True}
