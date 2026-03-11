"""Networking Engine Models - PLAN MAITRE
Pydantic models for hunter social network.

Version: 1.0.0
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime, timezone
from enum import Enum
import uuid


class ConnectionStatus(str, Enum):
    """Connection status"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    BLOCKED = "blocked"


class PostType(str, Enum):
    """Post types"""
    TEXT = "text"
    PHOTO = "photo"
    HARVEST = "harvest"
    SIGHTING = "sighting"
    TIP = "tip"
    QUESTION = "question"


class EventType(str, Enum):
    """Community event types"""
    MEETUP = "meetup"
    HUNT = "hunt"
    WORKSHOP = "workshop"
    COMPETITION = "competition"
    WEBINAR = "webinar"


class PublicProfile(BaseModel):
    """Public user profile"""
    user_id: str
    
    # Public info
    display_name: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    cover_photo_url: Optional[str] = None
    
    # Location (optional)
    region: Optional[str] = None
    show_region: bool = True
    
    # Stats (public)
    member_since: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    experience_years: Optional[int] = None
    preferred_species: List[str] = Field(default_factory=list)
    
    # Social stats
    connection_count: int = 0
    post_count: int = 0
    followers_count: int = 0
    following_count: int = 0
    
    # Achievements
    level: int = 1
    title: Optional[str] = None
    featured_badges: List[str] = Field(default_factory=list)
    
    # Privacy
    is_public: bool = True
    allow_messages: bool = True
    
    # Metadata
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Connection(BaseModel):
    """Connection between users"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Users
    requester_id: str
    recipient_id: str
    
    # Status
    status: ConnectionStatus = ConnectionStatus.PENDING
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    accepted_at: Optional[datetime] = None


class Post(BaseModel):
    """Social feed post"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Author
    author_id: str
    author_name: str
    author_avatar: Optional[str] = None
    
    # Content
    post_type: PostType = PostType.TEXT
    content: str
    media_urls: List[str] = Field(default_factory=list)
    
    # Context
    species: Optional[str] = None
    location: Optional[Dict[str, float]] = None
    location_name: Optional[str] = None
    
    # Harvest details (if harvest post)
    harvest_details: Optional[Dict[str, Any]] = None
    
    # Engagement
    likes_count: int = 0
    comments_count: int = 0
    shares_count: int = 0
    
    # Visibility
    visibility: Literal["public", "connections", "private"] = "public"
    
    # Status
    is_pinned: bool = False
    is_edited: bool = False
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Comment(BaseModel):
    """Comment on a post"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    post_id: str
    
    # Author
    author_id: str
    author_name: str
    author_avatar: Optional[str] = None
    
    # Content
    content: str
    
    # Reply
    reply_to: Optional[str] = None  # comment_id if reply
    
    # Engagement
    likes_count: int = 0
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_edited: bool = False


class CommunityEvent(BaseModel):
    """Community event"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Details
    title: str
    description: str
    event_type: EventType = EventType.MEETUP
    
    # Organizer
    organizer_id: str
    organizer_name: str
    
    # Timing
    start_date: datetime
    end_date: Optional[datetime] = None
    
    # Location
    is_virtual: bool = False
    location_name: Optional[str] = None
    location_address: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None
    virtual_link: Optional[str] = None
    
    # Registration
    max_participants: Optional[int] = None
    current_participants: int = 0
    registration_required: bool = True
    registration_deadline: Optional[datetime] = None
    
    # Cost
    is_free: bool = True
    cost: Optional[float] = None
    
    # Status
    status: Literal["upcoming", "ongoing", "completed", "cancelled"] = "upcoming"
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EventRegistration(BaseModel):
    """Event registration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_id: str
    user_id: str
    
    # Status
    status: Literal["registered", "waitlist", "attended", "cancelled"] = "registered"
    
    # Metadata
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FeedItem(BaseModel):
    """Feed item (aggregated)"""
    item_type: Literal["post", "connection", "event", "achievement"] = "post"
    item_id: str
    
    # Preview data
    preview: Dict[str, Any] = Field(default_factory=dict)
    
    # Relevance
    relevance_score: float = 0
    
    # Metadata
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
