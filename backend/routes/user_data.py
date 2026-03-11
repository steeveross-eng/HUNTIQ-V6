"""
User Waypoints and Places API — BIONIC P0
Persistance backend MongoDB pour waypoints et lieux.
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/user-data", tags=["User Waypoints & Places"])

# MongoDB (lazy init)
_db = None

def get_db():
    global _db
    if _db is None:
        from motor.motor_asyncio import AsyncIOMotorClient
        MONGO_URL = os.environ.get('MONGO_URL')
        DB_NAME = os.environ.get('DB_NAME')
        client = AsyncIOMotorClient(MONGO_URL)
        _db = client[DB_NAME]
    return _db


# ── Models ──
class WaypointCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    type: str = Field(default="autre")
    active: bool = Field(default=True)
    notes: Optional[str] = None

class WaypointUpdate(BaseModel):
    name: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    type: Optional[str] = None
    active: Optional[bool] = None
    notes: Optional[str] = None

class PlaceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    type: str = Field(default="autre")
    notes: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None

class PlaceUpdate(BaseModel):
    name: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    type: Optional[str] = None
    notes: Optional[str] = None

class SyncRequest(BaseModel):
    waypoints: list = []
    places: list = []


def _ser_wp(doc):
    return {
        "id": str(doc["_id"]),
        "user_id": doc.get("user_id", ""),
        "name": doc.get("name", ""),
        "lat": doc.get("lat", 0),
        "lng": doc.get("lng", 0),
        "type": doc.get("type", "autre"),
        "active": doc.get("active", True),
        "notes": doc.get("notes"),
        "created_at": doc.get("created_at", ""),
        "updated_at": doc.get("updated_at"),
    }

def _ser_place(doc):
    return {
        "id": str(doc["_id"]),
        "user_id": doc.get("user_id", ""),
        "name": doc.get("name", ""),
        "lat": doc.get("lat", 0),
        "lng": doc.get("lng", 0),
        "type": doc.get("type", "autre"),
        "notes": doc.get("notes"),
        "address": doc.get("address"),
        "phone": doc.get("phone"),
        "website": doc.get("website"),
        "created_at": doc.get("created_at", ""),
        "updated_at": doc.get("updated_at"),
    }


# ── WAYPOINTS ──

@router.get("/waypoints/{user_id}")
async def get_user_waypoints(user_id: str, active_only: bool = Query(False)):
    db = get_db()
    query = {"user_id": user_id}
    if active_only:
        query["active"] = True
    cursor = db.user_waypoints.find(query).sort("created_at", -1)
    docs = await cursor.to_list(length=500)
    return [_ser_wp(d) for d in docs]


@router.post("/waypoints/{user_id}")
async def create_waypoint(user_id: str, wp: WaypointCreate):
    db = get_db()
    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "user_id": user_id,
        **wp.model_dump(),
        "created_at": now,
        "updated_at": None,
    }
    result = await db.user_waypoints.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _ser_wp(doc)


@router.put("/waypoints/{user_id}/{waypoint_id}")
async def update_waypoint(user_id: str, waypoint_id: str, updates: WaypointUpdate):
    from bson import ObjectId
    db = get_db()
    update_data = {k: v for k, v in updates.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    result = await db.user_waypoints.find_one_and_update(
        {"_id": ObjectId(waypoint_id), "user_id": user_id},
        {"$set": update_data},
        return_document=True,
    )
    if not result:
        raise HTTPException(404, "Waypoint not found")
    return _ser_wp(result)


@router.delete("/waypoints/{user_id}/{waypoint_id}")
async def delete_waypoint(user_id: str, waypoint_id: str):
    from bson import ObjectId
    db = get_db()
    result = await db.user_waypoints.delete_one({"_id": ObjectId(waypoint_id), "user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Waypoint not found")
    return {"status": "deleted", "id": waypoint_id}


# ── PLACES ──

@router.get("/places/{user_id}")
async def get_user_places(user_id: str):
    db = get_db()
    cursor = db.user_places.find({"user_id": user_id}).sort("created_at", -1)
    docs = await cursor.to_list(length=500)
    return [_ser_place(d) for d in docs]


@router.post("/places/{user_id}")
async def create_place(user_id: str, place: PlaceCreate):
    db = get_db()
    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "user_id": user_id,
        **place.model_dump(),
        "created_at": now,
        "updated_at": None,
    }
    result = await db.user_places.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _ser_place(doc)


@router.put("/places/{user_id}/{place_id}")
async def update_place(user_id: str, place_id: str, updates: PlaceUpdate):
    from bson import ObjectId
    db = get_db()
    update_data = {k: v for k, v in updates.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    result = await db.user_places.find_one_and_update(
        {"_id": ObjectId(place_id), "user_id": user_id},
        {"$set": update_data},
        return_document=True,
    )
    if not result:
        raise HTTPException(404, "Place not found")
    return _ser_place(result)


@router.delete("/places/{user_id}/{place_id}")
async def delete_place(user_id: str, place_id: str):
    from bson import ObjectId
    db = get_db()
    result = await db.user_places.delete_one({"_id": ObjectId(place_id), "user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Place not found")
    return {"status": "deleted", "id": place_id}


# ── SYNC ──

@router.post("/sync/{user_id}")
async def sync_user_data(user_id: str, data: SyncRequest):
    db = get_db()
    now = datetime.now(timezone.utc).isoformat()
    wp_synced = 0
    pl_synced = 0

    for wp in data.waypoints:
        wp_data = wp if isinstance(wp, dict) else wp.model_dump() if hasattr(wp, 'model_dump') else dict(wp)
        name = wp_data.get("name", "")
        lat = wp_data.get("lat", 0)
        lng = wp_data.get("lng", 0)
        existing = await db.user_waypoints.find_one({"user_id": user_id, "name": name, "lat": lat, "lng": lng})
        if not existing:
            await db.user_waypoints.insert_one({
                "user_id": user_id,
                "name": name,
                "lat": lat,
                "lng": lng,
                "type": wp_data.get("type", "autre"),
                "active": wp_data.get("active", True),
                "notes": wp_data.get("notes"),
                "created_at": wp_data.get("created_at", now),
                "updated_at": None,
            })
            wp_synced += 1

    for pl in data.places:
        pl_data = pl if isinstance(pl, dict) else pl.model_dump() if hasattr(pl, 'model_dump') else dict(pl)
        name = pl_data.get("name", "")
        lat = pl_data.get("lat", 0)
        lng = pl_data.get("lng", 0)
        existing = await db.user_places.find_one({"user_id": user_id, "name": name, "lat": lat, "lng": lng})
        if not existing:
            await db.user_places.insert_one({
                "user_id": user_id,
                "name": name,
                "lat": lat,
                "lng": lng,
                "type": pl_data.get("type", "autre"),
                "notes": pl_data.get("notes"),
                "address": pl_data.get("address"),
                "phone": pl_data.get("phone"),
                "website": pl_data.get("website"),
                "created_at": pl_data.get("created_at", now),
                "updated_at": None,
            })
            pl_synced += 1

    return {
        "waypoints_synced": wp_synced,
        "places_synced": pl_synced,
        "message": f"{wp_synced} waypoints et {pl_synced} lieux synchronisés",
    }
