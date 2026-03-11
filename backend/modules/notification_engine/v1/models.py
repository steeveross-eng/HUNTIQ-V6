"""Notification Engine Models - MÉTIER

Pydantic models for notifications.

Version: 1.0.0
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from enum import Enum
import uuid


class NotificationType(str, Enum):
    """Notification types"""
    SYSTEM = "system"
    ORDER = "order"
    PROMOTION = "promotion"
    ALERT = "alert"
    MESSAGE = "message"
    REMINDER = "reminder"


class NotificationChannel(str, Enum):
    """Notification delivery channels"""
    IN_APP = "in_app"
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"


class NotificationPriority(str, Enum):
    """Notification priority"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class Notification(BaseModel):
    """User notification"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    type: NotificationType
    channel: NotificationChannel = NotificationChannel.IN_APP
    priority: NotificationPriority = NotificationPriority.NORMAL
    
    # Content
    title: str
    message: str
    data: Dict[str, Any] = Field(default_factory=dict)
    action_url: Optional[str] = None
    
    # Status
    is_read: bool = False
    is_sent: bool = False
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None


class NotificationTemplate(BaseModel):
    """Notification template"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: NotificationType
    
    # Content
    title_template: str
    message_template: str
    
    # Channels
    channels: List[NotificationChannel] = Field(default_factory=lambda: [NotificationChannel.IN_APP])
    
    # Status
    is_active: bool = True
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EmailTemplate(BaseModel):
    """Email template"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    subject: str
    body_html: str
    body_text: str
    
    # Variables
    variables: List[str] = Field(default_factory=list)  # e.g., ["name", "order_id"]
    
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class NotificationPreferences(BaseModel):
    """User notification preferences"""
    user_id: str
    
    # By channel
    in_app_enabled: bool = True
    email_enabled: bool = True
    push_enabled: bool = False
    sms_enabled: bool = False
    
    # By type
    system_notifications: bool = True
    order_notifications: bool = True
    promotion_notifications: bool = False
    message_notifications: bool = True
    reminder_notifications: bool = True
    
    # Timing
    quiet_hours_enabled: bool = False
    quiet_hours_start: str = "22:00"
    quiet_hours_end: str = "08:00"
    
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SendNotificationRequest(BaseModel):
    """Request to send a notification"""
    user_id: str
    type: NotificationType
    title: str
    message: str
    channels: List[NotificationChannel] = Field(default_factory=lambda: [NotificationChannel.IN_APP])
    priority: NotificationPriority = NotificationPriority.NORMAL
    data: Dict[str, Any] = Field(default_factory=dict)
    action_url: Optional[str] = None


class BroadcastRequest(BaseModel):
    """Request to broadcast notification to multiple users"""
    user_ids: Optional[List[str]] = None  # None = all users
    type: NotificationType
    title: str
    message: str
    channels: List[NotificationChannel] = Field(default_factory=lambda: [NotificationChannel.IN_APP])
