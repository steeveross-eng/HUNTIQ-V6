"""Tracking Engine Module v1

GPS tracking and location sharing for hunting.
Extracted from live_tracking.py.

Version: 1.0.0
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime, timezone, timedelta
import uuid
import os
from pymongo import MongoClient

router = APIRouter(prefix="/api/v1/tracking", tags=["Tracking Engine"])


# ============================================
# MODELS
# ============================================

class Position(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    altitude: Optional[float] = None
    accuracy: Optional[float] = None
    heading: Optional[float] = None
    speed: Optional[float] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TrackingSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str = "Session de chasse"
    positions: List[Position] = []
    is_active: bool = True
    is_sharing: bool = False
    share_code: Optional[str] = None
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ended_at: Optional[datetime] = None


class SafetyZone(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    center: Position
    radius_meters: float = 500
    alert_on_exit: bool = True
    is_active: bool = True


class ProximityAlert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    target_user_id: str
    distance_meters: float
    triggered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ============================================
# SERVICE
# ============================================

class TrackingService:
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'test_database')
        self._client = None
        self._db = None
    
    @property
    def db(self):
        if self._db is None:
            self._client = MongoClient(self.mongo_url)
            self._db = self._client[self.db_name]
        return self._db
    
    async def start_session(self, user_id: str, name: str = None) -> TrackingSession:
        session = TrackingSession(user_id=user_id, name=name or "Session de chasse")
        s_dict = session.model_dump()
        s_dict.pop("_id", None)
        self.db.tracking_sessions.insert_one(s_dict)
        return session
    
    async def update_position(self, session_id: str, position: Position) -> bool:
        result = self.db.tracking_sessions.update_one(
            {"id": session_id, "is_active": True},
            {"$push": {"positions": position.model_dump()}}
        )
        return result.modified_count > 0
    
    async def get_session(self, session_id: str) -> Optional[Dict]:
        return self.db.tracking_sessions.find_one({"id": session_id}, {"_id": 0})
    
    async def end_session(self, session_id: str) -> bool:
        result = self.db.tracking_sessions.update_one(
            {"id": session_id},
            {"$set": {"is_active": False, "ended_at": datetime.now(timezone.utc)}}
        )
        return result.modified_count > 0
    
    async def get_active_sessions(self, user_id: str) -> List[Dict]:
        cursor = self.db.tracking_sessions.find(
            {"user_id": user_id, "is_active": True},
            {"_id": 0}
        )
        return list(cursor)
    
    async def get_session_history(self, user_id: str, limit: int = 20) -> List[Dict]:
        cursor = self.db.tracking_sessions.find(
            {"user_id": user_id},
            {"_id": 0, "positions": 0}  # Exclude positions for performance
        ).sort("started_at", -1).limit(limit)
        return list(cursor)
    
    async def enable_sharing(self, session_id: str) -> str:
        import secrets
        share_code = secrets.token_urlsafe(8)
        self.db.tracking_sessions.update_one(
            {"id": session_id},
            {"$set": {"is_sharing": True, "share_code": share_code}}
        )
        return share_code
    
    async def get_shared_session(self, share_code: str) -> Optional[Dict]:
        return self.db.tracking_sessions.find_one(
            {"share_code": share_code, "is_sharing": True},
            {"_id": 0}
        )


_service = TrackingService()


# ============================================
# ROUTES
# ============================================

@router.get("/")
async def tracking_engine_info():
    return {
        "module": "tracking_engine",
        "version": "1.0.0",
        "description": "GPS tracking and location sharing",
        "features": [
            "Real-time position tracking",
            "Session management",
            "Position sharing",
            "Safety zones",
            "Track history"
        ]
    }


@router.post("/sessions")
async def start_tracking_session(user_id: str, name: Optional[str] = None):
    session = await _service.start_session(user_id, name)
    return {"success": True, "session": session.model_dump()}


@router.post("/sessions/{session_id}/position")
async def update_position(session_id: str, position: Position):
    success = await _service.update_position(session_id, position)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found or inactive")
    return {"success": True, "message": "Position updated"}


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    session = await _service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"success": True, "session": session}


@router.put("/sessions/{session_id}/end")
async def end_session(session_id: str):
    success = await _service.end_session(session_id)
    return {"success": success, "message": "Session ended" if success else "Session not found"}


@router.get("/sessions/user/{user_id}/active")
async def get_active_sessions(user_id: str):
    sessions = await _service.get_active_sessions(user_id)
    return {"success": True, "sessions": sessions}


@router.get("/sessions/user/{user_id}/history")
async def get_session_history(user_id: str, limit: int = Query(20, ge=1, le=100)):
    sessions = await _service.get_session_history(user_id, limit)
    return {"success": True, "sessions": sessions}


@router.post("/sessions/{session_id}/share")
async def enable_sharing(session_id: str):
    share_code = await _service.enable_sharing(session_id)
    return {"success": True, "share_code": share_code}


@router.get("/share/{share_code}")
async def get_shared_session(share_code: str):
    session = await _service.get_shared_session(share_code)
    if not session:
        raise HTTPException(status_code=404, detail="Shared session not found")
    return {"success": True, "session": session}
