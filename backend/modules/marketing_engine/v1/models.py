"""
Marketing Engine V1 - Models
=============================
Data models for marketing automation.
Architecture LEGO V5 - Module isolé.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from enum import Enum
import uuid


class CampaignStatus(str, Enum):
    """Statuts de campagne"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class PostStatus(str, Enum):
    """Statuts de publication"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"


class Platform(str, Enum):
    """Plateformes sociales"""
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"


class ContentType(str, Enum):
    """Types de contenu"""
    PRODUCT_PROMO = "product_promo"
    EDUCATIONAL = "educational"
    SEASONAL = "seasonal"
    TESTIMONIAL = "testimonial"
    TIP = "tip"
    ENGAGEMENT = "engagement"


class TriggerType(str, Enum):
    """Types de déclencheurs d'automation"""
    USER_SIGNUP = "user_signup"
    FIRST_LOGIN = "first_login"
    CART_ABANDONED = "cart_abandoned_24h"
    INACTIVE_7_DAYS = "inactive_7_days"
    INACTIVE_30_DAYS = "inactive_30_days"
    PAGE_VIEW = "page_view"
    FEATURE_USED = "feature_used"
    PURCHASE_COMPLETED = "purchase_completed"
    SUBSCRIPTION_EXPIRED = "subscription_expired"
    CUSTOM_EVENT = "custom_event"


class ActionType(str, Enum):
    """Types d'actions d'automation"""
    SEND_EMAIL = "send_email"
    SEND_PUSH = "send_push"
    SEND_SMS = "send_sms"
    IN_APP_MESSAGE = "in_app_message"
    OFFER_DISCOUNT = "offer_discount"
    TAG_USER = "tag_user"
    UPDATE_SEGMENT = "update_segment"
    WEBHOOK = "webhook"


# ============================================
# CAMPAIGN MODELS
# ============================================

class Campaign(BaseModel):
    """Campagne marketing"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    type: str = "promotional"
    status: CampaignStatus = CampaignStatus.DRAFT
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    target_platforms: List[Platform] = [Platform.FACEBOOK]
    target_segment: Optional[str] = None
    budget: float = 0
    goals: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CampaignCreate(BaseModel):
    """Schema création campagne"""
    name: str
    description: Optional[str] = None
    type: str = "promotional"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    target_platforms: List[str] = ["facebook"]
    target_segment: Optional[str] = None
    budget: float = 0
    goals: Dict[str, Any] = {}


# ============================================
# POST MODELS
# ============================================

class Post(BaseModel):
    """Publication marketing"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    campaign_id: Optional[str] = None
    platform: Platform
    content: str
    hashtags: List[str] = []
    media_urls: List[str] = []
    content_type: ContentType = ContentType.PRODUCT_PROMO
    status: PostStatus = PostStatus.DRAFT
    scheduled_at: Optional[str] = None
    published_at: Optional[str] = None
    impressions: int = 0
    clicks: int = 0
    engagement: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PostCreate(BaseModel):
    """Schema création post"""
    campaign_id: Optional[str] = None
    platform: str = "facebook"
    content: str
    hashtags: List[str] = []
    media_urls: List[str] = []
    content_type: str = "product_promo"
    status: str = "draft"
    scheduled_at: Optional[str] = None


# ============================================
# SEGMENT MODELS
# ============================================

class Segment(BaseModel):
    """Segment d'audience"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    criteria: Dict[str, Any] = {}
    count: int = 0
    is_default: bool = False
    is_dynamic: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SegmentCreate(BaseModel):
    """Schema création segment"""
    name: str
    description: Optional[str] = None
    criteria: Dict[str, Any] = {}
    is_dynamic: bool = False


# ============================================
# AUTOMATION MODELS
# ============================================

class AutomationAction(BaseModel):
    """Action d'une automation"""
    type: ActionType
    config: Dict[str, Any] = {}
    delay_minutes: int = 0


class Automation(BaseModel):
    """Automation marketing"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    trigger: TriggerType
    trigger_config: Dict[str, Any] = {}
    actions: List[AutomationAction] = []
    is_active: bool = False
    runs_count: int = 0
    last_run_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AutomationCreate(BaseModel):
    """Schema création automation"""
    name: str
    description: Optional[str] = None
    trigger: str
    trigger_config: Dict[str, Any] = {}
    actions: List[Dict[str, Any]] = []


# ============================================
# CONTENT GENERATION MODELS
# ============================================

class ContentGenerationRequest(BaseModel):
    """Requête de génération de contenu"""
    content_type: ContentType = ContentType.PRODUCT_PROMO
    platform: Platform = Platform.FACEBOOK
    product_name: Optional[str] = None
    keywords: List[str] = []
    tone: str = "professional"
    brand_name: str = "BIONIC HUNT/Chasse"


class ContentGenerationResponse(BaseModel):
    """Réponse de génération de contenu"""
    content: str
    hashtags: List[str]
    platform: str
    content_type: str
    generated_at: datetime


# ============================================
# TRACKING INTEGRATION MODELS
# ============================================

class BehavioralTrigger(BaseModel):
    """Déclencheur comportemental (lié au Tracking Engine)"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    automation_id: str
    event_type: str
    event_name: Optional[str] = None
    page_url_pattern: Optional[str] = None
    min_occurrences: int = 1
    time_window_hours: int = 24
    is_active: bool = True


class TriggerExecution(BaseModel):
    """Exécution d'un trigger"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    trigger_id: str
    automation_id: str
    user_id: str
    session_id: Optional[str] = None
    event_data: Dict[str, Any] = {}
    executed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "pending"  # pending, executed, failed
