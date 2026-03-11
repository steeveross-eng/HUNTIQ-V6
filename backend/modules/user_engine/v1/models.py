"""User Engine Models - MÉTIER

Pydantic models for user management.
Base models for authentication, profiles, and preferences.

Version: 1.0.0
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime, timezone
from enum import Enum
import uuid


class UserRole(str, Enum):
    """User roles in the system"""
    GUEST = "guest"
    USER = "user"
    PREMIUM = "premium"
    PARTNER = "partner"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class UserStatus(str, Enum):
    """User account status"""
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class User(BaseModel):
    """Core user model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Identity
    email: str
    name: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    
    # Account
    role: UserRole = UserRole.USER
    status: UserStatus = UserStatus.ACTIVE
    is_verified: bool = False
    
    # Preferences
    language: str = "fr"
    region: Optional[str] = None  # Quebec region code
    notification_preferences: Dict[str, bool] = Field(default_factory=lambda: {
        "email": True,
        "push": True,
        "sms": False,
        "marketing": False
    })
    
    # Activity
    last_login: Optional[datetime] = None
    login_count: int = 0
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserProfile(BaseModel):
    """Extended user profile for hunting preferences"""
    user_id: str
    
    # Hunting preferences
    preferred_species: List[str] = Field(default_factory=list)  # deer, moose, bear, etc.
    hunting_experience: Literal["beginner", "intermediate", "expert"] = "intermediate"
    hunting_regions: List[str] = Field(default_factory=list)  # Region codes
    
    # Equipment
    preferred_attractant_types: List[str] = Field(default_factory=list)  # gel, bloc, urine, etc.
    hunting_style: Literal["stand", "stalking", "calling", "mixed"] = "mixed"
    
    # Territory
    owns_land: bool = False
    has_zec_membership: bool = False
    has_pourvoirie_membership: bool = False
    
    # Statistics
    total_analyses: int = 0
    favorite_products: List[str] = Field(default_factory=list)
    
    # Metadata
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserPreferences(BaseModel):
    """User application preferences"""
    user_id: str
    
    # Display
    theme: Literal["light", "dark", "system"] = "system"
    language: str = "fr"
    units: Literal["metric", "imperial"] = "metric"
    
    # Notifications
    email_notifications: bool = True
    push_notifications: bool = True
    sms_notifications: bool = False
    marketing_emails: bool = False
    
    # Privacy
    profile_public: bool = False
    show_activity: bool = True
    allow_tracking: bool = True
    
    # Map preferences
    default_map_layer: str = "base_topo"
    show_hunting_zones: bool = True
    show_weather: bool = True
    
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserCreate(BaseModel):
    """Model for creating a new user"""
    email: str
    name: str
    phone: Optional[str] = None
    password: Optional[str] = None  # Hashed before storage
    language: str = "fr"
    region: Optional[str] = None


class UserUpdate(BaseModel):
    """Model for updating user information"""
    name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    language: Optional[str] = None
    region: Optional[str] = None


class UserLogin(BaseModel):
    """Login request model"""
    email: str
    password: str


class UserSession(BaseModel):
    """User session information"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    token: str
    device_info: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime
    is_active: bool = True


class UserActivity(BaseModel):
    """User activity log entry"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    action: str  # login, logout, analyze, purchase, etc.
    details: Dict[str, Any] = Field(default_factory=dict)
    ip_address: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
