"""
Waypoint Engine V1 - Models
============================
Data models for waypoint management.
Architecture LEGO V5 - Module isolé.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone
import uuid


class WaypointSource(str):
    """Sources de création de waypoint"""
    USER_DOUBLE_CLICK = "user_double_click"
    USER_MANUAL = "user_manual"
    GPS_TRACKING = "gps_tracking"
    IMPORT = "import"
    AI_SUGGESTION = "ai_suggestion"


class WaypointCreate(BaseModel):
    """Schema pour créer un waypoint"""
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lng: float = Field(..., ge=-180, le=180, description="Longitude")
    name: Optional[str] = None
    description: Optional[str] = None
    timestamp: Optional[str] = None
    source: str = "user_double_click"
    user_id: Optional[str] = None
    tags: List[str] = []
    metadata: dict = {}


class Waypoint(BaseModel):
    """Waypoint complet"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    lat: float
    lng: float
    name: str
    description: Optional[str] = None
    timestamp: str
    source: str
    user_id: Optional[str] = None
    tags: List[str] = []
    metadata: dict = {}
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WaypointUpdate(BaseModel):
    """Schema pour modifier un waypoint"""
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = None
