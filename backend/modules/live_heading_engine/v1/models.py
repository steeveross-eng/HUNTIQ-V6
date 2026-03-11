"""Live Heading Engine Models - PHASE 6
Data models for immersive heading view.

Version: 1.0.0
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from enum import Enum
import uuid


# ==============================================
# ENUMS
# ==============================================

class SessionState(str, Enum):
    """Session states"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"


class AlertType(str, Enum):
    """Alert types for heading view"""
    WILDLIFE_DETECTED = "wildlife_detected"
    WIND_CHANGE = "wind_change"
    POI_NEARBY = "poi_nearby"
    TERRAIN_ALERT = "terrain_alert"
    GROUP_MEMBER = "group_member"
    STRATEGY_UPDATE = "strategy_update"


class AlertPriority(str, Enum):
    """Alert priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class POIType(str, Enum):
    """Point of Interest types"""
    FEEDING_ZONE = "feeding_zone"
    BEDDING_ZONE = "bedding_zone"
    WATER_SOURCE = "water_source"
    TRAIL = "trail"
    STAND = "stand"
    BLIND = "blind"
    CAMERA = "camera"
    OBSERVATION = "observation"
    SIGN = "sign"  # Animal sign (tracks, rubs, etc.)
    WAYPOINT = "waypoint"


# ==============================================
# CORE MODELS
# ==============================================

class GeoPosition(BaseModel):
    """Geographic position with heading"""
    lat: float
    lng: float
    altitude: Optional[float] = None
    accuracy: Optional[float] = None  # meters
    heading: Optional[float] = None  # 0-360 degrees, 0=North
    speed: Optional[float] = None  # m/s
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ViewCone(BaseModel):
    """Forward view cone configuration"""
    aperture_degrees: float = 60  # Total cone width
    range_meters: float = 500  # View distance
    direction: float = 0  # Center direction (0-360)
    
    # Calculated vertices (for polygon rendering)
    vertices: List[Dict[str, float]] = Field(default_factory=list)


class WindData(BaseModel):
    """Wind conditions"""
    direction: float  # Wind coming FROM this direction (0-360)
    speed_kmh: float
    gusts_kmh: Optional[float] = None
    favorable: bool = True  # True if wind is favorable for hunting
    notes: Optional[str] = None


class PointOfInterest(BaseModel):
    """Point of interest in heading view"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Location
    lat: float
    lng: float
    elevation: Optional[float] = None
    
    # Properties
    poi_type: POIType
    name: Optional[str] = None
    description: Optional[str] = None
    
    # Visibility
    visible_in_cone: bool = False
    distance_m: float = 0
    bearing: float = 0  # Bearing from user position
    relative_angle: float = 0  # Angle relative to heading
    
    # Metadata
    priority: int = 5  # 1-10, higher = more important
    icon: Optional[str] = None
    color: Optional[str] = None
    
    # Time-based
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None


class HeadingAlert(BaseModel):
    """Alert for heading view"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Alert info
    alert_type: AlertType
    priority: AlertPriority = AlertPriority.MEDIUM
    title: str
    message: str
    
    # Location (optional)
    lat: Optional[float] = None
    lng: Optional[float] = None
    distance_m: Optional[float] = None
    bearing: Optional[float] = None
    
    # Display
    icon: Optional[str] = None
    color: Optional[str] = None
    duration_ms: int = 5000  # How long to show
    
    # State
    acknowledged: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ==============================================
# SESSION MODELS
# ==============================================

class HeadingSession(BaseModel):
    """Live heading session"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    
    # State
    state: SessionState = SessionState.INITIALIZING
    
    # Current position
    position: Optional[GeoPosition] = None
    
    # View configuration
    view_cone: ViewCone = Field(default_factory=ViewCone)
    
    # Environmental data
    wind: Optional[WindData] = None
    
    # Points of interest in view
    visible_pois: List[PointOfInterest] = Field(default_factory=list)
    
    # Active alerts
    alerts: List[HeadingAlert] = Field(default_factory=list)
    
    # Settings
    settings: Dict[str, Any] = Field(default_factory=lambda: {
        "cone_aperture": 60,
        "cone_range": 500,
        "auto_rotate_map": True,
        "show_wind_indicator": True,
        "show_terrain": True,
        "show_trails": True,
        "show_group_members": True,
        "alert_sounds": True,
        "vibrate_on_alert": True
    })
    
    # Statistics
    distance_traveled_m: float = 0
    duration_seconds: int = 0
    pois_visited: List[str] = Field(default_factory=list)
    
    # Timestamps
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_update: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ended_at: Optional[datetime] = None


class HeadingUpdate(BaseModel):
    """Position/heading update from client"""
    session_id: str
    
    # New position
    lat: float
    lng: float
    altitude: Optional[float] = None
    accuracy: Optional[float] = None
    
    # Heading
    heading: float  # 0-360
    
    # Optional
    speed: Optional[float] = None
    timestamp: Optional[datetime] = None


class SessionSettings(BaseModel):
    """Session settings update"""
    cone_aperture: Optional[float] = None
    cone_range: Optional[float] = None
    auto_rotate_map: Optional[bool] = None
    show_wind_indicator: Optional[bool] = None
    show_terrain: Optional[bool] = None
    show_trails: Optional[bool] = None
    show_group_members: Optional[bool] = None
    alert_sounds: Optional[bool] = None
    vibrate_on_alert: Optional[bool] = None


# ==============================================
# RESPONSE MODELS
# ==============================================

class HeadingViewState(BaseModel):
    """Complete view state for client"""
    session_id: str
    state: SessionState
    
    # Position
    position: GeoPosition
    
    # View cone
    view_cone: ViewCone
    
    # Environment
    wind: Optional[WindData] = None
    
    # Content
    pois: List[PointOfInterest] = Field(default_factory=list)
    alerts: List[HeadingAlert] = Field(default_factory=list)
    
    # Stats
    distance_traveled_m: float = 0
    duration_seconds: int = 0
    
    # Timestamp
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CreateSessionRequest(BaseModel):
    """Request to create a new heading session"""
    user_id: str
    lat: float
    lng: float
    heading: float = 0
    cone_aperture: float = 60
    cone_range: float = 500


class CreateSessionResponse(BaseModel):
    """Response after creating session"""
    success: bool
    session_id: str
    message: str
