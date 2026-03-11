"""
Upsell Engine Router - V5-ULTIME Monétisation
============================================

Popups premium intelligents et déclencheurs comportementaux.

Déclencheurs:
- Quota atteint
- Fonctionnalité bloquée
- Temps d'utilisation
- Actions spécifiques
- Patterns d'utilisation

Version: 1.0.0
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime, timezone, timedelta
from enum import Enum
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/upsell", tags=["Upsell Engine - Monétisation"])

# Database
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'bionic_db')
_client = None
_db = None

def get_db():
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(MONGO_URL)
        _db = _client[DB_NAME]
    return _db

# ==============================================
# MODELS
# ==============================================

class TriggerType(str, Enum):
    QUOTA_REACHED = "quota_reached"
    FEATURE_LOCKED = "feature_locked"
    TIME_BASED = "time_based"
    ACTION_BASED = "action_based"
    PATTERN_BASED = "pattern_based"

class UpsellType(str, Enum):
    POPUP = "popup"
    BANNER = "banner"
    INLINE = "inline"
    TOAST = "toast"

class UpsellCampaign(BaseModel):
    name: str
    trigger_type: TriggerType
    trigger_config: Dict[str, Any]
    upsell_type: UpsellType
    content: Dict[str, str]  # title, description, cta
    target_tier: str
    priority: int = 1
    enabled: bool = True

class TriggerEvent(BaseModel):
    user_id: str
    trigger_type: TriggerType
    context: Dict[str, Any] = {}

# ==============================================
# DEFAULT UPSELL CAMPAIGNS
# ==============================================

DEFAULT_CAMPAIGNS = [
    {
        "name": "quota_strategy_reached",
        "trigger_type": TriggerType.QUOTA_REACHED.value,
        "trigger_config": {"feature": "daily_strategy_generations", "threshold": 100},
        "upsell_type": UpsellType.POPUP.value,
        "content": {
            "title": "Limite quotidienne atteinte",
            "description": "Passez à Premium pour générer plus de stratégies et optimiser vos sorties de chasse.",
            "cta": "Passer à Premium",
            "icon": "zap"
        },
        "target_tier": "premium",
        "priority": 10,
        "enabled": True
    },
    {
        "name": "feature_live_heading_locked",
        "trigger_type": TriggerType.FEATURE_LOCKED.value,
        "trigger_config": {"feature": "live_heading"},
        "upsell_type": UpsellType.POPUP.value,
        "content": {
            "title": "Fonctionnalité Premium",
            "description": "Live Heading View vous permet de naviguer en immersion avec boussole et indicateurs en temps réel.",
            "cta": "Débloquer maintenant",
            "icon": "compass"
        },
        "target_tier": "premium",
        "priority": 8,
        "enabled": True
    },
    {
        "name": "feature_advanced_layers_locked",
        "trigger_type": TriggerType.FEATURE_LOCKED.value,
        "trigger_config": {"feature": "advanced_layers"},
        "upsell_type": UpsellType.POPUP.value,
        "content": {
            "title": "Couches Avancées",
            "description": "Accédez aux couches 3D, simulation comportementale et analyses géospatiales avancées.",
            "cta": "Activer Premium",
            "icon": "layers"
        },
        "target_tier": "premium",
        "priority": 7,
        "enabled": True
    },
    {
        "name": "feature_custom_rules_locked",
        "trigger_type": TriggerType.FEATURE_LOCKED.value,
        "trigger_config": {"feature": "custom_rules"},
        "upsell_type": UpsellType.INLINE.value,
        "content": {
            "title": "Règles Personnalisées",
            "description": "Créez vos propres règles de chasse pour des recommandations sur mesure.",
            "cta": "Créer mes règles",
            "icon": "settings"
        },
        "target_tier": "premium",
        "priority": 6,
        "enabled": True
    },
    {
        "name": "time_7_days_free",
        "trigger_type": TriggerType.TIME_BASED.value,
        "trigger_config": {"days_since_signup": 7, "tier": "free"},
        "upsell_type": UpsellType.BANNER.value,
        "content": {
            "title": "Déjà 7 jours avec BIONIC HUNT/Chasse!",
            "description": "Profitez de -20% sur Premium cette semaine seulement.",
            "cta": "Voir l'offre",
            "icon": "gift"
        },
        "target_tier": "premium",
        "priority": 5,
        "enabled": True
    },
    {
        "name": "pattern_high_usage",
        "trigger_type": TriggerType.PATTERN_BASED.value,
        "trigger_config": {"strategy_count_7d": 15, "tier": "free"},
        "upsell_type": UpsellType.TOAST.value,
        "content": {
            "title": "Chasseur actif détecté!",
            "description": "Vous utilisez beaucoup BIONIC HUNT/Chasse. Premium vous donnerait encore plus de puissance.",
            "cta": "Explorer Premium",
            "icon": "trending-up"
        },
        "target_tier": "premium",
        "priority": 4,
        "enabled": True
    },
    {
        "name": "action_export_blocked",
        "trigger_type": TriggerType.ACTION_BASED.value,
        "trigger_config": {"action": "export_report"},
        "upsell_type": UpsellType.POPUP.value,
        "content": {
            "title": "Export Premium",
            "description": "Exportez vos données de chasse en PDF ou Excel pour les partager ou les analyser.",
            "cta": "Débloquer les exports",
            "icon": "download"
        },
        "target_tier": "premium",
        "priority": 6,
        "enabled": True
    }
]

# ==============================================
# MODULE INFO
# ==============================================

@router.get("/")
async def upsell_engine_info():
    """Get upsell engine information"""
    return {
        "module": "upsell_engine",
        "version": "1.0.0",
        "description": "Upsell intelligent V5-ULTIME",
        "trigger_types": [t.value for t in TriggerType],
        "upsell_types": [u.value for u in UpsellType],
        "campaigns_count": len(DEFAULT_CAMPAIGNS)
    }

# ==============================================
# TRIGGER CHECK
# ==============================================

@router.post("/trigger")
async def check_trigger(event: TriggerEvent):
    """Check if an event triggers an upsell"""
    db = get_db()
    
    # Get user subscription
    sub = await db.subscriptions.find_one({"user_id": event.user_id}, {"_id": 0})
    user_tier = sub.get("tier", "free") if sub else "free"
    
    # Don't show upsells to premium/pro users for premium features
    if user_tier in ["premium", "pro"]:
        return {"success": True, "upsell": None, "reason": "User already premium"}
    
    # Find matching campaign
    matching_campaign = None
    
    for campaign in DEFAULT_CAMPAIGNS:
        if not campaign.get("enabled", True):
            continue
        
        if campaign["trigger_type"] != event.trigger_type.value:
            continue
        
        # Check trigger config match
        config = campaign.get("trigger_config", {})
        
        if event.trigger_type == TriggerType.QUOTA_REACHED:
            if config.get("feature") == event.context.get("feature"):
                matching_campaign = campaign
                break
        
        elif event.trigger_type == TriggerType.FEATURE_LOCKED:
            if config.get("feature") == event.context.get("feature"):
                matching_campaign = campaign
                break
        
        elif event.trigger_type == TriggerType.ACTION_BASED:
            if config.get("action") == event.context.get("action"):
                matching_campaign = campaign
                break
        
        elif event.trigger_type == TriggerType.TIME_BASED:
            # Check days since signup
            user = await db.users.find_one({"user_id": event.user_id})
            if user and user.get("created_at"):
                days_since = (datetime.now(timezone.utc) - user["created_at"]).days
                if days_since >= config.get("days_since_signup", 0):
                    matching_campaign = campaign
                    break
        
        elif event.trigger_type == TriggerType.PATTERN_BASED:
            # Check usage patterns
            if config.get("tier") == user_tier:
                matching_campaign = campaign
                break
    
    if not matching_campaign:
        return {"success": True, "upsell": None, "reason": "No matching campaign"}
    
    # Check if recently shown (rate limiting)
    recent_shown = await db.upsell_impressions.find_one({
        "user_id": event.user_id,
        "campaign_name": matching_campaign["name"],
        "shown_at": {"$gte": datetime.now(timezone.utc) - timedelta(hours=24)}
    })
    
    if recent_shown:
        return {"success": True, "upsell": None, "reason": "Recently shown"}
    
    # Record impression
    await db.upsell_impressions.insert_one({
        "user_id": event.user_id,
        "campaign_name": matching_campaign["name"],
        "trigger_type": event.trigger_type.value,
        "context": event.context,
        "shown_at": datetime.now(timezone.utc)
    })
    
    return {
        "success": True,
        "upsell": {
            "type": matching_campaign["upsell_type"],
            "content": matching_campaign["content"],
            "target_tier": matching_campaign["target_tier"],
            "campaign_name": matching_campaign["name"]
        }
    }

# ==============================================
# CAMPAIGNS MANAGEMENT
# ==============================================

@router.get("/campaigns")
async def list_campaigns():
    """List all upsell campaigns"""
    return {"success": True, "campaigns": DEFAULT_CAMPAIGNS}

@router.post("/campaigns/dismiss")
async def dismiss_campaign(user_id: str, campaign_name: str):
    """Record campaign dismissal"""
    db = get_db()
    
    await db.upsell_dismissals.insert_one({
        "user_id": user_id,
        "campaign_name": campaign_name,
        "dismissed_at": datetime.now(timezone.utc)
    })
    
    return {"success": True, "message": "Campaign dismissed"}

@router.post("/campaigns/click")
async def record_click(user_id: str, campaign_name: str):
    """Record campaign CTA click"""
    db = get_db()
    
    await db.upsell_clicks.insert_one({
        "user_id": user_id,
        "campaign_name": campaign_name,
        "clicked_at": datetime.now(timezone.utc)
    })
    
    return {"success": True, "message": "Click recorded"}

# ==============================================
# ANALYTICS
# ==============================================

@router.get("/analytics")
async def get_upsell_analytics(days: int = Query(30, le=90)):
    """Get upsell campaign analytics"""
    db = get_db()
    
    since = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Count impressions
    impressions = await db.upsell_impressions.count_documents({"shown_at": {"$gte": since}})
    
    # Count clicks
    clicks = await db.upsell_clicks.count_documents({"clicked_at": {"$gte": since}})
    
    # Count dismissals
    dismissals = await db.upsell_dismissals.count_documents({"dismissed_at": {"$gte": since}})
    
    # Conversion rate
    conversion_rate = (clicks / impressions * 100) if impressions > 0 else 0
    
    return {
        "success": True,
        "period_days": days,
        "metrics": {
            "impressions": impressions,
            "clicks": clicks,
            "dismissals": dismissals,
            "conversion_rate": round(conversion_rate, 2)
        }
    }
