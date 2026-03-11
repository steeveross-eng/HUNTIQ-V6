"""
Marketing Calendar Engine V2
============================
Calendrier marketing 60 jours avec génération IA Premium.
Architecture LEGO V5 - Module isolé.
"""
from .router import router
from .models import (
    Campaign, CampaignStatus, AudienceType, ContentTone,
    MarketingCalendar, CampaignGenerationRequest, CampaignGenerationResponse,
    PlatformFormat, GeneratedContent, GeneratedVisual
)
from .service import CampaignService
from .ai_service import AIContentService, AIImageService

__all__ = [
    "router",
    "Campaign",
    "CampaignStatus",
    "AudienceType",
    "ContentTone",
    "MarketingCalendar",
    "CampaignGenerationRequest",
    "CampaignGenerationResponse",
    "PlatformFormat",
    "GeneratedContent",
    "GeneratedVisual",
    "CampaignService",
    "AIContentService",
    "AIImageService"
]
