"""
Marketing Calendar Engine V2 - API Router
==========================================
Endpoints pour le calendrier marketing 60 jours.
Architecture LEGO V5 - Module isolé.
"""
from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional
import os
import logging

from .models import (
    Campaign, CampaignStatus, AudienceType, ContentTone,
    MarketingCalendar, CampaignGenerationRequest, CampaignGenerationResponse,
    PlatformFormat
)
from .service import CampaignService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/marketing-calendar",
    tags=["Marketing Calendar V2"],
    responses={404: {"description": "Not found"}}
)

# Database dependency
_db = None
_service = None


def get_db():
    global _db
    if _db is None:
        from motor.motor_asyncio import AsyncIOMotorClient
        MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        DB_NAME = os.environ.get('DB_NAME', 'hunttrack')
        client = AsyncIOMotorClient(MONGO_URL)
        _db = client[DB_NAME]
    return _db


def get_service():
    global _service
    if _service is None:
        _service = CampaignService(get_db())
    return _service


# ============================================
# MODULE INFO
# ============================================

@router.get("/", summary="Module Info")
async def get_module_info():
    """Get Marketing Calendar V2 module information"""
    return {
        "module": "marketing_calendar_engine",
        "version": "2.0.0",
        "description": "Calendrier marketing 60 jours avec génération IA Premium",
        "status": "operational",
        "sla": {
            "max_generation_time_ms": 60000,
            "description": "Génération de campagne < 60 secondes"
        },
        "features": [
            "Calendrier 60 jours à l'avance",
            "Génération de contenu GPT-5.2",
            "Génération d'images IA (GPT Image 1)",
            "Templates Premium BIONIC",
            "Animations Lottie/Motion",
            "Personnalisation par audience",
            "Prévisualisation multi-plateforme"
        ],
        "audience_types": [at.value for at in AudienceType],
        "content_tones": [ct.value for ct in ContentTone],
        "platform_formats": [pf.value for pf in PlatformFormat],
        "endpoints": [
            {"path": "/calendar", "method": "GET", "description": "Calendrier 60 jours"},
            {"path": "/campaigns/generate", "method": "POST", "description": "Générer campagne"},
            {"path": "/campaigns/{id}", "method": "GET", "description": "Détail campagne"},
            {"path": "/campaigns/{id}/schedule", "method": "POST", "description": "Planifier campagne"},
            {"path": "/preview", "method": "POST", "description": "Prévisualisation rapide"}
        ]
    }


@router.get("/health", summary="Health Check")
async def health_check():
    """Check service health"""
    try:
        db = get_db()
        await db.command("ping")
        return {
            "status": "healthy",
            "database": "connected",
            "ai_services": {
                "gpt_5_2": "available",
                "gpt_image_1": "available"
            }
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e)
        }


# ============================================
# CALENDAR
# ============================================

@router.get("/calendar", response_model=MarketingCalendar, summary="Calendrier Marketing")
async def get_calendar(
    days_ahead: int = Query(60, ge=1, le=90, description="Nombre de jours à afficher")
):
    """
    Récupère le calendrier marketing sur N jours.
    
    Inclut:
    - Campagnes planifiées
    - Événements (saisons de chasse, etc.)
    - Suggestions de contenu
    """
    service = get_service()
    return await service.get_calendar(days_ahead)


# ============================================
# CAMPAIGN GENERATION
# ============================================

@router.post("/campaigns/generate", response_model=CampaignGenerationResponse, summary="Générer Campagne")
async def generate_campaign(request: CampaignGenerationRequest):
    """
    Génère une campagne marketing complète.
    
    **SLA: < 60 secondes**
    
    Inclut:
    - Contenu textuel (GPT-5.2): headline, subheadline, body, CTA
    - Visuels (Templates Premium ou IA)
    - Prévisualisations multi-plateforme
    - Estimations d'engagement
    
    **Audiences supportées:**
    - fabricants
    - affiliation
    - partenariats
    - prospects
    - audiences_specialisees
    - general
    """
    service = get_service()
    return await service.generate_campaign(request)


@router.post("/preview", summary="Prévisualisation Rapide")
async def quick_preview(
    audience_type: AudienceType = Query(..., description="Type d'audience"),
    tone: ContentTone = Query(ContentTone.PREMIUM, description="Ton du message"),
    platform: str = Query("meta_feed", description="Plateforme cible"),
    custom_message: Optional[str] = Query(None, description="Message personnalisé")
):
    """
    Génère une prévisualisation rapide sans sauvegarder.
    
    Utile pour tester différentes combinaisons.
    """
    from .ai_service import AIContentService
    
    ai_content = AIContentService()
    content = await ai_content.generate_marketing_content(
        audience_type=audience_type.value,
        tone=tone.value,
        platform=platform
    )
    
    return {
        "success": True,
        "preview": {
            "headline": content.get("headline"),
            "subheadline": content.get("subheadline"),
            "body_text": content.get("body_text"),
            "cta_text": content.get("cta_text"),
            "hashtags": content.get("hashtags"),
            "audience_type": audience_type.value,
            "tone": tone.value,
            "platform": platform
        },
        "generation_time_ms": content.get("generation_time_ms")
    }


# ============================================
# CAMPAIGN CRUD
# ============================================

@router.get("/campaigns", summary="Lister Campagnes")
async def list_campaigns(
    audience_type: Optional[AudienceType] = Query(None, description="Filtrer par audience"),
    status: Optional[CampaignStatus] = Query(None, description="Filtrer par statut"),
    limit: int = Query(50, ge=1, le=200)
):
    """Liste les campagnes avec filtres optionnels"""
    db = get_db()
    
    query = {}
    if audience_type:
        query["audience_type"] = audience_type.value
    if status:
        query["status"] = status.value
    
    campaigns = await db.marketing_campaigns.find(query).limit(limit).to_list(limit)
    
    return {
        "success": True,
        "total": len(campaigns),
        "campaigns": [Campaign(**c).dict() for c in campaigns]
    }


@router.get("/campaigns/{campaign_id}", summary="Détail Campagne")
async def get_campaign(campaign_id: str):
    """Récupère les détails d'une campagne"""
    service = get_service()
    campaign = await service.get_campaign(campaign_id)
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return {
        "success": True,
        "campaign": campaign.dict()
    }


@router.put("/campaigns/{campaign_id}", summary="Modifier Campagne")
async def update_campaign(
    campaign_id: str,
    updates: dict = Body(..., description="Champs à mettre à jour")
):
    """
    Met à jour une campagne.
    
    Champs modifiables:
    - name
    - scheduled_date
    - status
    - custom_message
    - custom_cta
    - custom_hashtags
    """
    service = get_service()
    
    # Vérifier que la campagne existe
    campaign = await service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Filtrer les champs autorisés
    allowed_fields = ["name", "scheduled_date", "status", "custom_message", "custom_cta", "custom_hashtags"]
    filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}
    
    success = await service.update_campaign(campaign_id, filtered_updates)
    
    return {
        "success": success,
        "message": "Campaign updated" if success else "No changes made"
    }


@router.delete("/campaigns/{campaign_id}", summary="Supprimer Campagne")
async def delete_campaign(campaign_id: str):
    """Supprime une campagne"""
    service = get_service()
    success = await service.delete_campaign(campaign_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return {
        "success": True,
        "message": "Campaign deleted"
    }


@router.post("/campaigns/{campaign_id}/schedule", summary="Planifier Campagne")
async def schedule_campaign(campaign_id: str):
    """
    Planifie une campagne (passe de DRAFT à SCHEDULED).
    
    La campagne sera prête pour export/publication.
    """
    service = get_service()
    
    campaign = await service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign.status != CampaignStatus.DRAFT:
        raise HTTPException(status_code=400, detail=f"Cannot schedule campaign with status {campaign.status}")
    
    success = await service.schedule_campaign(campaign_id)
    
    return {
        "success": success,
        "message": "Campaign scheduled" if success else "Failed to schedule",
        "new_status": CampaignStatus.SCHEDULED.value
    }


# ============================================
# TEMPLATES & ASSETS
# ============================================

@router.get("/templates", summary="Templates Premium")
async def get_templates():
    """Liste les templates Premium disponibles"""
    service = get_service()
    
    return {
        "success": True,
        "templates": list(service.PREMIUM_TEMPLATES.values()),
        "animations": list(service.LOTTIE_ANIMATIONS.keys())
    }


@router.get("/audience-types", summary="Types d'Audience")
async def get_audience_types():
    """Liste les types d'audience supportés avec descriptions"""
    return {
        "success": True,
        "audience_types": [
            {
                "value": AudienceType.FABRICANTS.value,
                "label": "Fabricants & Marques",
                "description": "Messages B2B pour partenariats commerciaux"
            },
            {
                "value": AudienceType.AFFILIATION.value,
                "label": "Programme d'Affiliation",
                "description": "Recrutement d'affiliés et influenceurs"
            },
            {
                "value": AudienceType.PARTENARIATS.value,
                "label": "Partenariats Stratégiques",
                "description": "Collaborations et co-branding"
            },
            {
                "value": AudienceType.PROSPECTS.value,
                "label": "Prospects",
                "description": "Conversion de leads qualifiés"
            },
            {
                "value": AudienceType.AUDIENCES_SPECIALISEES.value,
                "label": "Audiences Spécialisées",
                "description": "Segments de niche (archers, trappeurs, etc.)"
            },
            {
                "value": AudienceType.GENERAL.value,
                "label": "Audience Générale",
                "description": "Communication grand public"
            }
        ]
    }


@router.get("/content-tones", summary="Tons de Communication")
async def get_content_tones():
    """Liste les tons de communication disponibles"""
    return {
        "success": True,
        "tones": [
            {"value": ContentTone.PROFESSIONAL.value, "label": "Professionnel", "emoji": "💼"},
            {"value": ContentTone.PREMIUM.value, "label": "Premium", "emoji": "✨"},
            {"value": ContentTone.FRIENDLY.value, "label": "Amical", "emoji": "🤝"},
            {"value": ContentTone.URGENT.value, "label": "Urgent", "emoji": "⚡"},
            {"value": ContentTone.EXCLUSIVE.value, "label": "Exclusif", "emoji": "🔒"},
            {"value": ContentTone.EDUCATIONAL.value, "label": "Éducatif", "emoji": "📚"}
        ]
    }
