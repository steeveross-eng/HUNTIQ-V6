"""
Marketing Calendar Engine V2 - Models
=====================================
Modèles Pydantic pour le calendrier marketing 60 jours.
Architecture LEGO V5 - Module isolé.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class AudienceType(str, Enum):
    """Types d'interlocuteurs pour personnalisation"""
    FABRICANTS = "fabricants"
    AFFILIATION = "affiliation"
    PARTENARIATS = "partenariats"
    PROSPECTS = "prospects"
    AUDIENCES_SPECIALISEES = "audiences_specialisees"
    GENERAL = "general"


class CampaignStatus(str, Enum):
    """Statuts de campagne"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ContentTone(str, Enum):
    """Tons de communication"""
    PROFESSIONAL = "professional"
    PREMIUM = "premium"
    FRIENDLY = "friendly"
    URGENT = "urgent"
    EXCLUSIVE = "exclusive"
    EDUCATIONAL = "educational"


class PlatformFormat(str, Enum):
    """Formats de plateforme"""
    META_FEED = "meta_feed"           # 1200x628
    META_STORY = "meta_story"         # 1080x1920
    META_CAROUSEL = "meta_carousel"   # 1080x1080
    TIKTOK = "tiktok"                 # 1080x1920
    YOUTUBE_THUMBNAIL = "youtube_thumbnail"  # 1280x720
    YOUTUBE_BANNER = "youtube_banner"        # 2560x1440
    EMAIL_HEADER = "email_header"     # 600x200
    WEBSITE_BANNER = "website_banner" # 1920x600


class VisualTemplate(BaseModel):
    """Template visuel Premium"""
    id: str
    name: str
    description: str
    category: str  # hero, product, testimonial, cta, feature
    format: PlatformFormat
    base_image_url: Optional[str] = None
    lottie_animation_url: Optional[str] = None
    css_animation: Optional[str] = None
    color_scheme: Dict[str, str] = Field(default_factory=dict)
    placeholders: List[str] = Field(default_factory=list)  # headline, subheadline, cta, image


class GeneratedContent(BaseModel):
    """Contenu généré par IA"""
    headline: str
    subheadline: Optional[str] = None
    body_text: Optional[str] = None
    cta_text: str
    hashtags: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    tone: ContentTone
    audience_type: AudienceType
    generation_time_ms: int


class GeneratedVisual(BaseModel):
    """Visuel généré"""
    id: str
    template_id: str
    format: PlatformFormat
    image_base64: Optional[str] = None
    image_url: Optional[str] = None
    ai_generated: bool = False
    lottie_json: Optional[Dict] = None
    css_styles: Optional[str] = None
    generation_time_ms: int


class CampaignPreview(BaseModel):
    """Prévisualisation de campagne"""
    campaign_id: str
    platform: str
    format: PlatformFormat
    content: GeneratedContent
    visual: GeneratedVisual
    preview_url: Optional[str] = None
    mock_engagement: Dict[str, int] = Field(default_factory=dict)


class Campaign(BaseModel):
    """Campagne marketing complète"""
    id: str = Field(default="")
    name: str
    description: Optional[str] = None
    
    # Scheduling
    scheduled_date: datetime
    end_date: Optional[datetime] = None
    status: CampaignStatus = CampaignStatus.DRAFT
    
    # Targeting
    audience_type: AudienceType
    target_segments: List[str] = Field(default_factory=list)
    platforms: List[str] = Field(default_factory=list)
    
    # Content
    tone: ContentTone = ContentTone.PREMIUM
    content: Optional[GeneratedContent] = None
    visuals: List[GeneratedVisual] = Field(default_factory=list)
    
    # Customization
    custom_message: Optional[str] = None
    custom_cta: Optional[str] = None
    custom_hashtags: List[str] = Field(default_factory=list)
    
    # Preview
    previews: List[CampaignPreview] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    
    # Performance (future)
    estimated_reach: Optional[int] = None
    estimated_engagement: Optional[float] = None
    
    # SLA tracking
    generation_time_ms: Optional[int] = None


class CalendarDay(BaseModel):
    """Jour du calendrier marketing"""
    date: str  # YYYY-MM-DD
    campaigns: List[Campaign] = Field(default_factory=list)
    events: List[str] = Field(default_factory=list)  # Holidays, seasons, etc.
    suggestions: List[str] = Field(default_factory=list)


class MarketingCalendar(BaseModel):
    """Calendrier marketing 60 jours"""
    start_date: str
    end_date: str
    days: List[CalendarDay] = Field(default_factory=list)
    total_campaigns: int = 0
    total_scheduled: int = 0
    total_draft: int = 0


class CampaignGenerationRequest(BaseModel):
    """Requête de génération de campagne"""
    name: str
    scheduled_date: datetime
    audience_type: AudienceType
    tone: ContentTone = ContentTone.PREMIUM
    platforms: List[str] = Field(default=["meta_feed", "meta_story"])
    
    # Optional customization
    custom_message: Optional[str] = None
    custom_keywords: List[str] = Field(default_factory=list)
    product_focus: Optional[str] = None
    
    # Generation options
    generate_visuals: bool = True
    use_ai_images: bool = False  # If True, generate AI images; else use templates


class CampaignGenerationResponse(BaseModel):
    """Réponse de génération de campagne"""
    success: bool
    campaign: Optional[Campaign] = None
    generation_time_ms: int
    sla_met: bool  # < 60 seconds
    error: Optional[str] = None
