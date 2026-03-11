"""Collaborative Engine Models - PLAN MAITRE
Pydantic models for hunter collaboration system.

Version: 1.0.0
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime, timezone
from enum import Enum
import uuid


class GroupRole(str, Enum):
    """Roles within a hunting group"""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    GUEST = "guest"


class GroupStatus(str, Enum):
    """Group status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class InvitationStatus(str, Enum):
    """Invitation status"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"


class HuntingGroup(BaseModel):
    """Hunting group model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    owner_id: str
    
    # Settings
    is_private: bool = True
    max_members: int = Field(default=20, ge=2, le=100)
    allow_guest_spots: bool = False
    require_approval: bool = True
    
    # Stats
    member_count: int = 0
    spot_count: int = 0
    event_count: int = 0
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: GroupStatus = GroupStatus.ACTIVE
    
    # Location
    primary_region: Optional[str] = None
    territory_ids: List[str] = Field(default_factory=list)


class GroupMember(BaseModel):
    """Group member model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    group_id: str
    user_id: str
    user_name: str
    role: GroupRole = GroupRole.MEMBER
    
    # Permissions
    can_invite: bool = False
    can_edit_spots: bool = False
    can_manage_events: bool = False
    can_view_positions: bool = True
    
    # Activity
    joined_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_active: Optional[datetime] = None
    contribution_score: int = 0


class SharedSpot(BaseModel):
    """Shared hunting spot within a group"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    group_id: str
    created_by: str
    
    # Location
    name: str
    description: Optional[str] = None
    coordinates: Dict[str, float]  # lat, lng
    territory_id: Optional[str] = None
    
    # Details
    spot_type: Literal["stand", "blind", "trail", "feeding", "water", "other"] = "stand"
    target_species: List[str] = Field(default_factory=list)
    best_conditions: Optional[str] = None
    
    # Stats
    sighting_count: int = 0
    success_count: int = 0
    rating: float = Field(default=0, ge=0, le=5)
    rating_count: int = 0
    
    # Visibility
    is_active: bool = True
    visibility: Literal["all", "admins", "owner"] = "all"
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GroupEvent(BaseModel):
    """Group hunting event/calendar entry"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    group_id: str
    created_by: str
    
    # Event details
    title: str
    description: Optional[str] = None
    event_type: Literal["hunt", "scout", "meeting", "maintenance", "other"] = "hunt"
    
    # Timing
    start_date: datetime
    end_date: Optional[datetime] = None
    all_day: bool = False
    
    # Location
    location_name: Optional[str] = None
    spot_id: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None
    
    # Participation
    max_participants: Optional[int] = None
    participants: List[str] = Field(default_factory=list)  # user_ids
    confirmed_count: int = 0
    
    # Status
    status: Literal["planned", "ongoing", "completed", "cancelled"] = "planned"
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GroupInvitation(BaseModel):
    """Invitation to join a group"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    group_id: str
    group_name: str
    
    # Parties
    invited_by: str
    invited_user_id: Optional[str] = None
    invited_email: Optional[str] = None
    
    # Details
    role: GroupRole = GroupRole.MEMBER
    message: Optional[str] = None
    
    # Status
    status: InvitationStatus = InvitationStatus.PENDING
    expires_at: datetime
    
    # Tracking
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    responded_at: Optional[datetime] = None


class ChatMessage(BaseModel):
    """Group chat message"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    group_id: str
    sender_id: str
    sender_name: str
    
    # Content
    message_type: Literal["text", "image", "location", "spot", "event"] = "text"
    content: str
    attachments: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Reference
    reply_to: Optional[str] = None
    spot_id: Optional[str] = None
    event_id: Optional[str] = None
    
    # Status
    is_edited: bool = False
    is_deleted: bool = False
    read_by: List[str] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    edited_at: Optional[datetime] = None


class PositionShare(BaseModel):
    """Real-time position sharing"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    group_id: str
    user_id: str
    user_name: str
    
    # Position
    coordinates: Dict[str, float]  # lat, lng
    accuracy: Optional[float] = None
    altitude: Optional[float] = None
    heading: Optional[float] = None
    speed: Optional[float] = None
    
    # Sharing settings
    is_sharing: bool = True
    share_until: Optional[datetime] = None
    
    # Status
    status: Literal["hunting", "scouting", "traveling", "resting", "emergency"] = "hunting"
    status_message: Optional[str] = None
    
    # Metadata
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GroupCreateRequest(BaseModel):
    """Request to create a new group"""
    name: str
    description: Optional[str] = None
    is_private: bool = True
    max_members: int = 20
    primary_region: Optional[str] = None


class GroupUpdateRequest(BaseModel):
    """Request to update group settings"""
    name: Optional[str] = None
    description: Optional[str] = None
    is_private: Optional[bool] = None
    max_members: Optional[int] = None
    allow_guest_spots: Optional[bool] = None
    require_approval: Optional[bool] = None
