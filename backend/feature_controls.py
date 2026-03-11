"""
Feature Controls Module
- Centralized ON/OFF control for all application features
- Admin can enable/disable features in real-time
- Full audit log of all changes
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime, timezone
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

feature_controls_router = APIRouter(prefix="/api/feature-controls", tags=["Feature Controls"])

# Database connection
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "bionic_territory")

client = None
db = None

async def get_db():
    global client, db
    if client is None:
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
    return db


# ============================================
# FEATURE DEFINITIONS
# ============================================

# All controllable features with their metadata
FEATURE_DEFINITIONS = {
    # Social & Communication
    "social_posts": {
        "name": "Publications Sociales",
        "name_en": "Social Posts",
        "description": "Création et affichage de posts dans le réseau social",
        "category": "social",
        "icon": "MessageSquare",
        "default": True
    },
    "comments": {
        "name": "Commentaires",
        "name_en": "Comments",
        "description": "Système de commentaires sur les posts",
        "category": "social",
        "icon": "MessageCircle",
        "default": True
    },
    "likes": {
        "name": "J'aime",
        "name_en": "Likes",
        "description": "Système de likes sur posts et commentaires",
        "category": "social",
        "icon": "Heart",
        "default": True
    },
    "groups": {
        "name": "Groupes",
        "name_en": "Groups",
        "description": "Création et gestion de groupes",
        "category": "social",
        "icon": "Users",
        "default": True
    },
    
    # Notifications
    "push_notifications": {
        "name": "Notifications Push",
        "name_en": "Push Notifications",
        "description": "Notifications en temps réel dans l'application",
        "category": "notifications",
        "icon": "Bell",
        "default": True
    },
    "email_notifications": {
        "name": "Notifications Email",
        "name_en": "Email Notifications",
        "description": "Envoi d'emails de notification",
        "category": "notifications",
        "icon": "Mail",
        "default": True
    },
    "email_digest": {
        "name": "Résumés Email",
        "name_en": "Email Digests",
        "description": "Envoi de résumés quotidiens/hebdomadaires",
        "category": "notifications",
        "icon": "Newspaper",
        "default": True
    },
    
    # Marketing & Social Media
    "social_sharing_facebook": {
        "name": "Partage Facebook",
        "name_en": "Facebook Sharing",
        "description": "Publication automatique sur Facebook",
        "category": "marketing",
        "icon": "Facebook",
        "default": False
    },
    "social_sharing_instagram": {
        "name": "Partage Instagram",
        "name_en": "Instagram Sharing",
        "description": "Publication automatique sur Instagram",
        "category": "marketing",
        "icon": "Instagram",
        "default": False
    },
    "seo_auto_generation": {
        "name": "Génération SEO Auto",
        "name_en": "Auto SEO Generation",
        "description": "Génération automatique de contenu SEO par IA",
        "category": "marketing",
        "icon": "Search",
        "default": True
    },
    
    # Commerce
    "marketplace": {
        "name": "Marketplace",
        "name_en": "Marketplace",
        "description": "Publication et achat d'annonces",
        "category": "commerce",
        "icon": "ShoppingBag",
        "default": True
    },
    "payments": {
        "name": "Paiements Stripe",
        "name_en": "Stripe Payments",
        "description": "Traitement des paiements en ligne",
        "category": "commerce",
        "icon": "CreditCard",
        "default": True
    },
    "lands_rental": {
        "name": "Location de Terres",
        "name_en": "Land Rentals",
        "description": "Module de location de terres de chasse",
        "category": "commerce",
        "icon": "MapPin",
        "default": True
    },
    
    # Referral & Loyalty
    "referral_program": {
        "name": "Programme Parrainage",
        "name_en": "Referral Program",
        "description": "Système de parrainage avec récompenses",
        "category": "loyalty",
        "icon": "Gift",
        "default": True
    },
    "wallet_system": {
        "name": "Portefeuille Interne",
        "name_en": "Internal Wallet",
        "description": "Système de crédits et transferts",
        "category": "loyalty",
        "icon": "Wallet",
        "default": True
    },
    
    # User Management
    "user_registration": {
        "name": "Inscriptions",
        "name_en": "User Registration",
        "description": "Nouvelles inscriptions d'utilisateurs",
        "category": "users",
        "icon": "UserPlus",
        "default": True
    },
    "auto_login": {
        "name": "Connexion Automatique",
        "name_en": "Auto Login",
        "description": "Connexion automatique par reconnaissance IP",
        "category": "users",
        "icon": "Fingerprint",
        "default": True
    },
    "password_reset": {
        "name": "Réinitialisation MDP",
        "name_en": "Password Reset",
        "description": "Réinitialisation de mot de passe par email",
        "category": "users",
        "icon": "KeyRound",
        "default": True
    },
    
    # AI & Analysis
    "ai_species_recognition": {
        "name": "Reconnaissance Espèces IA",
        "name_en": "AI Species Recognition",
        "description": "Identification d'espèces par photo avec IA",
        "category": "ai",
        "icon": "Sparkles",
        "default": True
    },
    "ai_territory_analysis": {
        "name": "Analyse Territoire IA",
        "name_en": "AI Territory Analysis",
        "description": "Analyse de territoire avec probabilités",
        "category": "ai",
        "icon": "Brain",
        "default": True
    },
    "ai_product_categorization": {
        "name": "Catégorisation Produits IA",
        "name_en": "AI Product Categorization",
        "description": "Catégorisation automatique des produits",
        "category": "ai",
        "icon": "Tags",
        "default": True
    },
    
    # Leads & CRM
    "leads_management": {
        "name": "Gestion Prospects",
        "name_en": "Leads Management",
        "description": "Suivi et gestion des prospects",
        "category": "crm",
        "icon": "Target",
        "default": True
    },
    "contacts_management": {
        "name": "Gestion Contacts",
        "name_en": "Contacts Management",
        "description": "Carnet d'adresses personnel",
        "category": "crm",
        "icon": "BookUser",
        "default": True
    }
}

# Feature categories for UI organization
FEATURE_CATEGORIES = {
    "social": {"name": "Réseau Social", "name_en": "Social Network", "icon": "Users", "order": 1},
    "notifications": {"name": "Notifications", "name_en": "Notifications", "icon": "Bell", "order": 2},
    "marketing": {"name": "Marketing & Réseaux", "name_en": "Marketing & Social", "icon": "Megaphone", "order": 3},
    "commerce": {"name": "E-Commerce", "name_en": "E-Commerce", "icon": "ShoppingCart", "order": 4},
    "loyalty": {"name": "Fidélité & Parrainage", "name_en": "Loyalty & Referral", "icon": "Gift", "order": 5},
    "users": {"name": "Gestion Utilisateurs", "name_en": "User Management", "icon": "UserCog", "order": 6},
    "ai": {"name": "Intelligence Artificielle", "name_en": "Artificial Intelligence", "icon": "Brain", "order": 7},
    "crm": {"name": "CRM & Prospects", "name_en": "CRM & Leads", "icon": "Target", "order": 8}
}


# ============================================
# PYDANTIC MODELS
# ============================================

class FeatureToggleRequest(BaseModel):
    feature_id: str
    enabled: bool
    reason: Optional[str] = None

class BulkToggleRequest(BaseModel):
    features: Dict[str, bool]
    reason: Optional[str] = None

class FeatureLogEntry(BaseModel):
    feature_id: str
    feature_name: str
    old_value: bool
    new_value: bool
    changed_by: str
    changed_at: str
    reason: Optional[str] = None


# ============================================
# HELPER FUNCTIONS
# ============================================

async def get_feature_status(feature_id: str) -> bool:
    """Get the current status of a feature (enabled/disabled)"""
    database = await get_db()
    
    # Check if feature exists in definitions
    if feature_id not in FEATURE_DEFINITIONS:
        return False
    
    # Check database for override
    feature_doc = await database.feature_controls.find_one({"feature_id": feature_id}, {"_id": 0})
    
    if feature_doc:
        return feature_doc.get("enabled", FEATURE_DEFINITIONS[feature_id]["default"])
    
    # Return default value
    return FEATURE_DEFINITIONS[feature_id]["default"]


async def is_feature_enabled(feature_id: str) -> bool:
    """Public function to check if a feature is enabled - use this in other modules"""
    return await get_feature_status(feature_id)


async def log_feature_change(feature_id: str, old_value: bool, new_value: bool, 
                             changed_by: str, reason: Optional[str] = None):
    """Log a feature change to the audit log"""
    database = await get_db()
    
    log_entry = {
        "feature_id": feature_id,
        "feature_name": FEATURE_DEFINITIONS.get(feature_id, {}).get("name", feature_id),
        "old_value": old_value,
        "new_value": new_value,
        "changed_by": changed_by,
        "changed_at": datetime.now(timezone.utc).isoformat(),
        "reason": reason
    }
    
    await database.feature_control_logs.insert_one(log_entry)
    logger.info(f"Feature '{feature_id}' changed from {old_value} to {new_value} by {changed_by}")


# ============================================
# API ENDPOINTS
# ============================================

@feature_controls_router.get("/definitions")
async def get_feature_definitions():
    """Get all feature definitions with categories"""
    return {
        "features": FEATURE_DEFINITIONS,
        "categories": FEATURE_CATEGORIES
    }


@feature_controls_router.get("/status")
async def get_all_feature_status():
    """Get current status of all features"""
    database = await get_db()
    
    # Get all overrides from database
    overrides = await database.feature_controls.find({}, {"_id": 0}).to_list(100)
    override_map = {doc["feature_id"]: doc["enabled"] for doc in overrides}
    
    # Build status map
    status = {}
    for feature_id, definition in FEATURE_DEFINITIONS.items():
        status[feature_id] = {
            **definition,
            "enabled": override_map.get(feature_id, definition["default"]),
            "is_default": feature_id not in override_map
        }
    
    # Count enabled/disabled
    enabled_count = sum(1 for s in status.values() if s["enabled"])
    disabled_count = len(status) - enabled_count
    
    return {
        "features": status,
        "categories": FEATURE_CATEGORIES,
        "summary": {
            "total": len(status),
            "enabled": enabled_count,
            "disabled": disabled_count
        }
    }


@feature_controls_router.get("/status/{feature_id}")
async def get_single_feature_status(feature_id: str):
    """Get status of a single feature"""
    if feature_id not in FEATURE_DEFINITIONS:
        raise HTTPException(status_code=404, detail=f"Feature '{feature_id}' not found")
    
    enabled = await get_feature_status(feature_id)
    
    return {
        "feature_id": feature_id,
        **FEATURE_DEFINITIONS[feature_id],
        "enabled": enabled
    }


@feature_controls_router.post("/toggle")
async def toggle_feature(
    request: FeatureToggleRequest,
    admin_email: str = Query(..., description="Admin email for audit log")
):
    """Toggle a single feature ON or OFF"""
    database = await get_db()
    
    if request.feature_id not in FEATURE_DEFINITIONS:
        raise HTTPException(status_code=404, detail=f"Feature '{request.feature_id}' not found")
    
    # Get current status
    old_value = await get_feature_status(request.feature_id)
    
    # Update or create feature control
    await database.feature_controls.update_one(
        {"feature_id": request.feature_id},
        {
            "$set": {
                "feature_id": request.feature_id,
                "enabled": request.enabled,
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "updated_by": admin_email
            }
        },
        upsert=True
    )
    
    # Log the change
    await log_feature_change(
        feature_id=request.feature_id,
        old_value=old_value,
        new_value=request.enabled,
        changed_by=admin_email,
        reason=request.reason
    )
    
    return {
        "success": True,
        "feature_id": request.feature_id,
        "enabled": request.enabled,
        "message": f"Feature '{FEATURE_DEFINITIONS[request.feature_id]['name']}' {'activée' if request.enabled else 'désactivée'}"
    }


@feature_controls_router.post("/toggle-bulk")
async def toggle_features_bulk(
    request: BulkToggleRequest,
    admin_email: str = Query(..., description="Admin email for audit log")
):
    """Toggle multiple features at once"""
    database = await get_db()
    
    results = []
    for feature_id, enabled in request.features.items():
        if feature_id not in FEATURE_DEFINITIONS:
            results.append({"feature_id": feature_id, "success": False, "error": "Feature not found"})
            continue
        
        old_value = await get_feature_status(feature_id)
        
        await database.feature_controls.update_one(
            {"feature_id": feature_id},
            {
                "$set": {
                    "feature_id": feature_id,
                    "enabled": enabled,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "updated_by": admin_email
                }
            },
            upsert=True
        )
        
        await log_feature_change(
            feature_id=feature_id,
            old_value=old_value,
            new_value=enabled,
            changed_by=admin_email,
            reason=request.reason
        )
        
        results.append({"feature_id": feature_id, "success": True, "enabled": enabled})
    
    return {
        "success": True,
        "results": results,
        "message": f"{len([r for r in results if r['success']])} fonctionnalités mises à jour"
    }


@feature_controls_router.post("/reset-defaults")
async def reset_to_defaults(admin_email: str = Query(..., description="Admin email for audit log")):
    """Reset all features to their default values"""
    database = await get_db()
    
    # Get current statuses for logging
    current_statuses = {}
    overrides = await database.feature_controls.find({}, {"_id": 0}).to_list(100)
    for doc in overrides:
        current_statuses[doc["feature_id"]] = doc["enabled"]
    
    # Delete all overrides
    await database.feature_controls.delete_many({})
    
    # Log all changes
    for feature_id, old_value in current_statuses.items():
        if feature_id in FEATURE_DEFINITIONS:
            new_value = FEATURE_DEFINITIONS[feature_id]["default"]
            if old_value != new_value:
                await log_feature_change(
                    feature_id=feature_id,
                    old_value=old_value,
                    new_value=new_value,
                    changed_by=admin_email,
                    reason="Reset to defaults"
                )
    
    return {
        "success": True,
        "message": "Toutes les fonctionnalités ont été réinitialisées aux valeurs par défaut"
    }


@feature_controls_router.get("/logs")
async def get_feature_logs(
    limit: int = Query(50, ge=1, le=500),
    feature_id: Optional[str] = None,
    admin_email: Optional[str] = None
):
    """Get audit log of feature changes"""
    database = await get_db()
    
    query = {}
    if feature_id:
        query["feature_id"] = feature_id
    if admin_email:
        query["changed_by"] = admin_email
    
    logs = await database.feature_control_logs.find(
        query,
        {"_id": 0}
    ).sort("changed_at", -1).limit(limit).to_list(limit)
    
    return {
        "logs": logs,
        "total": len(logs)
    }


@feature_controls_router.get("/logs/stats")
async def get_logs_stats():
    """Get statistics about feature changes"""
    database = await get_db()
    
    # Total changes
    total_changes = await database.feature_control_logs.count_documents({})
    
    # Changes by feature
    pipeline = [
        {"$group": {"_id": "$feature_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    by_feature = await database.feature_control_logs.aggregate(pipeline).to_list(10)
    
    # Changes by admin
    pipeline_admin = [
        {"$group": {"_id": "$changed_by", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    by_admin = await database.feature_control_logs.aggregate(pipeline_admin).to_list(10)
    
    # Recent changes (last 24h)
    from datetime import timedelta
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    recent_count = await database.feature_control_logs.count_documents({
        "changed_at": {"$gte": yesterday}
    })
    
    return {
        "total_changes": total_changes,
        "changes_last_24h": recent_count,
        "by_feature": [{"feature_id": item["_id"], "count": item["count"]} for item in by_feature],
        "by_admin": [{"admin": item["_id"], "count": item["count"]} for item in by_admin]
    }


@feature_controls_router.post("/toggle-category")
async def toggle_category(
    category: str,
    enabled: bool,
    admin_email: str = Query(..., description="Admin email for audit log"),
    reason: Optional[str] = None
):
    """Toggle all features in a category"""
    if category not in FEATURE_CATEGORIES:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found")
    
    # Find all features in this category
    features_to_toggle = {
        fid: enabled 
        for fid, fdef in FEATURE_DEFINITIONS.items() 
        if fdef["category"] == category
    }
    
    # Use bulk toggle
    request = BulkToggleRequest(features=features_to_toggle, reason=reason or f"Category toggle: {category}")
    return await toggle_features_bulk(request, admin_email)


logger.info("Feature Controls module initialized")
