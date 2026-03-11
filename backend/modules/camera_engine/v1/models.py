"""
Camera Engine - Pydantic Models
Phase 1: Data models for cameras and camera events
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid


class CameraManufacturer(str, Enum):
    """Supported camera manufacturers"""
    BUSHNELL = "bushnell"
    MOULTRIE = "moultrie"
    RECONYX = "reconyx"
    STEALTH_CAM = "stealth_cam"
    BROWNING = "browning"
    SPYPOINT = "spypoint"
    TACTACAM = "tactacam"
    CUDDEBACK = "cuddeback"
    WILDGAME = "wildgame"
    OTHER = "other"


class CameraStatus(str, Enum):
    """Camera operational status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"


class EventActivity(str, Enum):
    """Types of activity captured"""
    PASSAGE = "passage"
    FEEDING = "feeding"
    RESTING = "resting"
    ALERT = "alert"
    UNKNOWN = "unknown"


class EventDirection(str, Enum):
    """Direction of movement"""
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"
    STATIONARY = "stationary"
    UNKNOWN = "unknown"


# ============================================
# CAMERA MODELS
# ============================================

class CameraBase(BaseModel):
    """Base camera model with shared fields"""
    manufacturer: CameraManufacturer = CameraManufacturer.OTHER
    model: Optional[str] = None
    serial: Optional[str] = None
    name: Optional[str] = None
    gps_lat: Optional[float] = None
    gps_lon: Optional[float] = None


class CameraCreate(CameraBase):
    """Model for creating a new camera - waypoint_id is MANDATORY"""
    waypoint_id: str = Field(..., description="ID du waypoint associé - OBLIGATOIRE")
    
    @field_validator('waypoint_id')
    @classmethod
    def waypoint_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("waypoint_id est OBLIGATOIRE - une caméra ne peut pas exister sans waypoint")
        return v.strip()


class CameraUpdate(BaseModel):
    """Model for updating camera (waypoint cannot be removed)"""
    manufacturer: Optional[CameraManufacturer] = None
    model: Optional[str] = None
    serial: Optional[str] = None
    name: Optional[str] = None
    gps_lat: Optional[float] = None
    gps_lon: Optional[float] = None
    status: Optional[CameraStatus] = None


class Camera(CameraBase):
    """Complete camera model for database storage and responses"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    email_alias: str  # Unique email for this camera's photo ingestion
    waypoint_id: str  # MANDATORY - enforced at creation
    status: CameraStatus = CameraStatus.ACTIVE
    photo_count: int = 0
    last_photo_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class CameraResponse(BaseModel):
    """API response model for camera"""
    id: str
    user_id: str
    email_alias: str
    waypoint_id: str
    manufacturer: CameraManufacturer
    model: Optional[str]
    serial: Optional[str]
    name: Optional[str]
    gps_lat: Optional[float]
    gps_lon: Optional[float]
    status: CameraStatus
    photo_count: int
    last_photo_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class CameraListResponse(BaseModel):
    """Response for listing cameras"""
    cameras: List[CameraResponse]
    total: int


# ============================================
# CAMERA EVENT MODELS
# ============================================

class CameraEventBase(BaseModel):
    """Base camera event model"""
    species: Optional[str] = None
    direction: EventDirection = EventDirection.UNKNOWN
    activity: EventActivity = EventActivity.UNKNOWN
    individual_id: Optional[str] = None  # For tracking specific animals
    notes: Optional[str] = None


class CameraEventCreate(CameraEventBase):
    """Model for creating camera event (internal use)"""
    camera_id: str
    timestamp: datetime
    raw_image_url: str  # Encrypted storage URL


class CameraEvent(CameraEventBase):
    """Complete camera event model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    camera_id: str
    waypoint_id: str  # Denormalized for faster queries
    timestamp: datetime
    raw_image_url: str  # Encrypted
    thumbnail_url: Optional[str] = None
    exif_data: Optional[dict] = None
    is_quarantined: bool = False
    quarantine_reason: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class CameraEventResponse(BaseModel):
    """API response model for camera event"""
    id: str
    user_id: str
    camera_id: str
    waypoint_id: str
    timestamp: datetime
    species: Optional[str]
    direction: EventDirection
    activity: EventActivity
    individual_id: Optional[str]
    thumbnail_url: Optional[str]
    is_quarantined: bool
    created_at: datetime


class CameraEventListResponse(BaseModel):
    """Response for listing camera events"""
    events: List[CameraEventResponse]
    total: int


# ============================================
# EMAIL INGESTION MODELS
# ============================================

class EmailIngestionStatus(str, Enum):
    """Status of email ingestion"""
    SUCCESS = "success"
    FAILED = "failed"
    QUARANTINED = "quarantined"


class EmailIngestionRequest(BaseModel):
    """Request model for email ingestion webhook"""
    from_email: str
    to_email: str  # Should contain camera email_alias
    subject: Optional[str] = None
    body: Optional[str] = None
    attachments: List[dict] = []  # List of {filename, content_type, data (base64)}


class EmailIngestionResponse(BaseModel):
    """Response for email ingestion"""
    status: EmailIngestionStatus
    message: str
    event_id: Optional[str] = None
    camera_id: Optional[str] = None
    quarantine_reason: Optional[str] = None


class IngestionLog(BaseModel):
    """Log entry for ingestion attempts"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    camera_id: Optional[str]
    email_alias: str
    from_email: str
    status: EmailIngestionStatus
    message: str
    event_id: Optional[str] = None
    error_details: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
