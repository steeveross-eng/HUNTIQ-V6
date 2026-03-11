"""
Freemium Engine Router - V5-ULTIME Monétisation
===============================================

Gestion des limitations, quotas et niveaux d'accès freemium.

Niveaux:
- FREE: Accès limité, quotas stricts
- PREMIUM: Accès complet, sans limitations
- PRO: Fonctionnalités avancées + support prioritaire

Version: 1.0.0
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone, timedelta
from enum import Enum
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/freemium", tags=["Freemium Engine - Monétisation"])

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

class SubscriptionTier(str, Enum):
    FREE = "free"
    PREMIUM = "premium"
    PRO = "pro"

class FeatureAccess(str, Enum):
    FULL = "full"
    LIMITED = "limited"
    LOCKED = "locked"

# Default quotas and limits per tier
TIER_LIMITS = {
    SubscriptionTier.FREE: {
        "daily_strategy_generations": 3,
        "daily_weather_checks": 10,
        "territory_zones": 2,
        "waypoints_per_zone": 5,
        "analytics_history_days": 7,
        "ai_recommendations": 5,
        "plan_maitre_phases": 2,
        "export_reports": False,
        "custom_rules": False,
        "priority_support": False,
        "advanced_layers": False,
        "live_heading": False,
    },
    SubscriptionTier.PREMIUM: {
        "daily_strategy_generations": 50,
        "daily_weather_checks": 100,
        "territory_zones": 10,
        "waypoints_per_zone": 50,
        "analytics_history_days": 90,
        "ai_recommendations": 50,
        "plan_maitre_phases": 5,
        "export_reports": True,
        "custom_rules": True,
        "priority_support": False,
        "advanced_layers": True,
        "live_heading": True,
    },
    SubscriptionTier.PRO: {
        "daily_strategy_generations": -1,  # Unlimited
        "daily_weather_checks": -1,
        "territory_zones": -1,
        "waypoints_per_zone": -1,
        "analytics_history_days": 365,
        "ai_recommendations": -1,
        "plan_maitre_phases": 5,
        "export_reports": True,
        "custom_rules": True,
        "priority_support": True,
        "advanced_layers": True,
        "live_heading": True,
    }
}

# Feature descriptions for UI
FEATURES = {
    "daily_strategy_generations": {
        "name": "Générations de stratégie",
        "description": "Nombre de stratégies générées par jour",
        "type": "quota"
    },
    "territory_zones": {
        "name": "Zones de territoire",
        "description": "Nombre de zones de chasse personnalisées",
        "type": "quota"
    },
    "analytics_history_days": {
        "name": "Historique analytics",
        "description": "Jours d'historique disponibles",
        "type": "quota"
    },
    "export_reports": {
        "name": "Export de rapports",
        "description": "Exporter les données en PDF/Excel",
        "type": "feature"
    },
    "custom_rules": {
        "name": "Règles personnalisées",
        "description": "Créer vos propres règles de chasse",
        "type": "feature"
    },
    "live_heading": {
        "name": "Live Heading View",
        "description": "Navigation immersive en temps réel",
        "type": "feature"
    },
    "advanced_layers": {
        "name": "Couches avancées",
        "description": "Accès aux couches 3D, simulation, comportement",
        "type": "feature"
    },
    "priority_support": {
        "name": "Support prioritaire",
        "description": "Assistance rapide et dédiée",
        "type": "feature"
    }
}

class UserSubscription(BaseModel):
    user_id: str
    tier: SubscriptionTier = SubscriptionTier.FREE
    expires_at: Optional[datetime] = None
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None

class QuotaUsage(BaseModel):
    feature: str
    used: int
    limit: int
    remaining: int
    reset_at: datetime

class FeatureCheckRequest(BaseModel):
    user_id: str
    feature: str

# ==============================================
# MODULE INFO
# ==============================================

@router.get("/")
async def freemium_engine_info():
    """Get freemium engine information"""
    return {
        "module": "freemium_engine",
        "version": "1.0.0",
        "description": "Gestion freemium V5-ULTIME",
        "tiers": [t.value for t in SubscriptionTier],
        "features_count": len(FEATURES),
        "tier_limits": {
            tier.value: limits for tier, limits in TIER_LIMITS.items()
        }
    }

# ==============================================
# SUBSCRIPTION MANAGEMENT
# ==============================================

@router.get("/subscription/{user_id}")
async def get_subscription(user_id: str):
    """Get user subscription details"""
    db = get_db()
    
    sub = await db.subscriptions.find_one({"user_id": user_id}, {"_id": 0})
    
    if not sub:
        # Return default free subscription
        sub = {
            "user_id": user_id,
            "tier": SubscriptionTier.FREE.value,
            "expires_at": None,
            "created_at": datetime.now(timezone.utc)
        }
        await db.subscriptions.insert_one(sub)
    
    # Check if subscription is expired
    if sub.get("expires_at") and sub["expires_at"] < datetime.now(timezone.utc):
        sub["tier"] = SubscriptionTier.FREE.value
        sub["expired"] = True
    
    # Add limits for current tier
    tier = SubscriptionTier(sub.get("tier", "free"))
    sub["limits"] = TIER_LIMITS.get(tier, TIER_LIMITS[SubscriptionTier.FREE])
    
    return {"success": True, "subscription": sub}

@router.post("/subscription/upgrade")
async def upgrade_subscription(user_id: str, tier: SubscriptionTier, duration_days: int = 30):
    """Upgrade user subscription (called after payment)"""
    db = get_db()
    
    expires_at = datetime.now(timezone.utc) + timedelta(days=duration_days)
    
    sub_data = {
        "user_id": user_id,
        "tier": tier.value,
        "expires_at": expires_at,
        "upgraded_at": datetime.now(timezone.utc)
    }
    
    await db.subscriptions.update_one(
        {"user_id": user_id},
        {"$set": sub_data},
        upsert=True
    )
    
    return {
        "success": True,
        "subscription": sub_data,
        "message": f"Upgraded to {tier.value} until {expires_at.isoformat()}"
    }

# ==============================================
# QUOTA MANAGEMENT
# ==============================================

@router.get("/quota/{user_id}/{feature}")
async def get_quota_usage(user_id: str, feature: str):
    """Get quota usage for a specific feature"""
    db = get_db()
    
    # Get user subscription
    sub = await db.subscriptions.find_one({"user_id": user_id}, {"_id": 0})
    tier = SubscriptionTier(sub.get("tier", "free")) if sub else SubscriptionTier.FREE
    
    # Get limit for feature
    limits = TIER_LIMITS.get(tier, TIER_LIMITS[SubscriptionTier.FREE])
    limit = limits.get(feature, 0)
    
    if limit == -1:  # Unlimited
        return {
            "success": True,
            "quota": {
                "feature": feature,
                "used": 0,
                "limit": -1,
                "remaining": -1,
                "unlimited": True,
                "reset_at": None
            }
        }
    
    # Get usage for today
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    
    usage = await db.quota_usage.find_one({
        "user_id": user_id,
        "feature": feature,
        "date": {"$gte": today, "$lt": tomorrow}
    }, {"_id": 0})
    
    used = usage.get("count", 0) if usage else 0
    remaining = max(0, limit - used)
    
    return {
        "success": True,
        "quota": {
            "feature": feature,
            "used": used,
            "limit": limit,
            "remaining": remaining,
            "unlimited": False,
            "reset_at": tomorrow.isoformat()
        }
    }

@router.post("/quota/{user_id}/{feature}/increment")
async def increment_quota(user_id: str, feature: str, amount: int = 1):
    """Increment quota usage"""
    db = get_db()
    
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    
    await db.quota_usage.update_one(
        {"user_id": user_id, "feature": feature, "date": today},
        {"$inc": {"count": amount}},
        upsert=True
    )
    
    return {"success": True, "incremented": amount}

# ==============================================
# FEATURE ACCESS CHECK
# ==============================================

@router.post("/check-access")
async def check_feature_access(request: FeatureCheckRequest):
    """Check if user has access to a feature"""
    db = get_db()
    
    # Get user subscription
    sub = await db.subscriptions.find_one({"user_id": request.user_id}, {"_id": 0})
    tier = SubscriptionTier(sub.get("tier", "free")) if sub else SubscriptionTier.FREE
    
    # Check expiration
    if sub and sub.get("expires_at"):
        if sub["expires_at"] < datetime.now(timezone.utc):
            tier = SubscriptionTier.FREE
    
    # Get limits for tier
    limits = TIER_LIMITS.get(tier, TIER_LIMITS[SubscriptionTier.FREE])
    feature_value = limits.get(request.feature)
    
    # Determine access
    if feature_value is None:
        access = FeatureAccess.LOCKED
        can_access = False
    elif isinstance(feature_value, bool):
        access = FeatureAccess.FULL if feature_value else FeatureAccess.LOCKED
        can_access = feature_value
    elif feature_value == -1:
        access = FeatureAccess.FULL
        can_access = True
    elif feature_value > 0:
        # Check quota
        quota_result = await get_quota_usage(request.user_id, request.feature)
        remaining = quota_result["quota"]["remaining"]
        
        if remaining > 0:
            access = FeatureAccess.FULL
            can_access = True
        else:
            access = FeatureAccess.LIMITED
            can_access = False
    else:
        access = FeatureAccess.LOCKED
        can_access = False
    
    return {
        "success": True,
        "feature": request.feature,
        "tier": tier.value,
        "access": access.value,
        "can_access": can_access,
        "upgrade_required": not can_access and tier == SubscriptionTier.FREE
    }

# ==============================================
# TIER COMPARISON
# ==============================================

@router.get("/tiers/compare")
async def compare_tiers():
    """Get comparison of all tiers"""
    comparison = []
    
    for feature_id, feature_info in FEATURES.items():
        feature_comparison = {
            "id": feature_id,
            "name": feature_info["name"],
            "description": feature_info["description"],
            "type": feature_info["type"],
            "tiers": {}
        }
        
        for tier in SubscriptionTier:
            value = TIER_LIMITS[tier].get(feature_id)
            if isinstance(value, bool):
                feature_comparison["tiers"][tier.value] = "✓" if value else "✗"
            elif value == -1:
                feature_comparison["tiers"][tier.value] = "∞"
            else:
                feature_comparison["tiers"][tier.value] = str(value)
        
        comparison.append(feature_comparison)
    
    return {
        "success": True,
        "tiers": [t.value for t in SubscriptionTier],
        "features": comparison
    }

# ==============================================
# PRICING
# ==============================================

PRICING = {
    SubscriptionTier.PREMIUM: {
        "monthly": {"amount": 9.99, "currency": "CAD", "stripe_price_id": None},
        "yearly": {"amount": 99.99, "currency": "CAD", "stripe_price_id": None}
    },
    SubscriptionTier.PRO: {
        "monthly": {"amount": 19.99, "currency": "CAD", "stripe_price_id": None},
        "yearly": {"amount": 199.99, "currency": "CAD", "stripe_price_id": None}
    }
}

@router.get("/pricing")
async def get_pricing():
    """Get subscription pricing"""
    return {
        "success": True,
        "currency": "CAD",
        "pricing": {
            "free": {
                "name": "Gratuit",
                "price": 0,
                "description": "Pour découvrir BIONIC HUNT/Chasse",
                "features": ["3 stratégies/jour", "2 zones", "7 jours d'historique"]
            },
            "premium": {
                "name": "Premium",
                "monthly_price": 9.99,
                "yearly_price": 99.99,
                "description": "Pour les chasseurs réguliers",
                "features": ["50 stratégies/jour", "10 zones", "90 jours d'historique", "Règles personnalisées", "Export PDF"]
            },
            "pro": {
                "name": "Pro",
                "monthly_price": 19.99,
                "yearly_price": 199.99,
                "description": "Pour les chasseurs experts",
                "features": ["Illimité", "Support prioritaire", "1 an d'historique", "Toutes les fonctionnalités"]
            }
        }
    }
