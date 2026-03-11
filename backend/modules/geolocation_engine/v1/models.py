"""
Geolocation Engine - Pydantic Models
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime


class LocationUpdate(BaseModel):
    """Location update from client"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    accuracy: Optional[float] = None
    altitude: Optional[float] = None
    speed: Optional[float] = None
    heading: Optional[float] = None
    timestamp: Optional[datetime] = None


class ProximityAlert(BaseModel):
    """Proximity alert when near a waypoint"""
    waypoint_id: str
    waypoint_name: str
    waypoint_type: str
    distance_meters: float
    wqs_score: Optional[float] = None
    classification: Optional[str] = None
    alert_type: str = "proximity"  # proximity, entered, exited
    message: str


class LocationHistory(BaseModel):
    """User location history entry"""
    id: Optional[str] = None
    user_id: str
    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    timestamp: datetime
    session_id: Optional[str] = None


class GeofenceZone(BaseModel):
    """Geofence zone definition"""
    id: str
    name: str
    center_lat: float
    center_lng: float
    radius_meters: float = 500
    type: str = "waypoint"  # waypoint, custom, territory
    waypoint_id: Optional[str] = None
    active: bool = True


class TrackingSession(BaseModel):
    """Tracking session for a hunting trip"""
    id: Optional[str] = None
    user_id: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    locations_count: int = 0
    distance_km: float = 0.0
    active: bool = True


class PushSubscription(BaseModel):
    """Web Push subscription"""
    endpoint: str
    keys: Dict[str, str]  # p256dh, auth


class PushNotification(BaseModel):
    """Push notification payload"""
    title: str
    body: str
    icon: Optional[str] = "/logos/bionic-logo.svg"
    badge: Optional[str] = "/logos/bionic-logo.svg"
    url: Optional[str] = "/"
    tag: Optional[str] = None
    data: Optional[Dict] = None
