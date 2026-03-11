"""
Site Access Control Module
- Manage site mode (live/development/maintenance)
- Control access during development
- Auto-disable features when in maintenance mode
- Protected by role-based authentication
"""

from fastapi import APIRouter, Query, Depends
from pydantic import BaseModel
from typing import Optional, Literal, List
from datetime import datetime, timezone
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Import role-based authentication
from modules.roles_engine.v1.dependencies import require_admin
from modules.roles_engine.v1.models import UserWithRole

load_dotenv()

logger = logging.getLogger(__name__)

access_router = APIRouter(prefix="/api/site", tags=["Site Access Control"])

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
# PYDANTIC MODELS
# ============================================

class SiteConfig(BaseModel):
    mode: Literal["live", "development", "maintenance"] = "live"
    message: str = ""
    allowed_ips: List[str] = []
    show_progress: bool = True
    progress_percent: int = 0
    estimated_completion: Optional[str] = None
    contact_email: Optional[str] = None
    updated_at: str = ""
    updated_by: str = ""

class UpdateSiteMode(BaseModel):
    mode: Literal["live", "development", "maintenance"]
    message: Optional[str] = None
    show_progress: Optional[bool] = None
    progress_percent: Optional[int] = None
    estimated_completion: Optional[str] = None
    contact_email: Optional[str] = None

# ============================================
# DEFAULT CONFIG
# ============================================

DEFAULT_CONFIG = {
    "mode": "development",  # ACTIVÉ PAR DÉFAUT
    "message": "🚧 Site en cours de développement. Nous travaillons activement à améliorer votre expérience. Revenez bientôt!",
    "allowed_ips": [],
    "show_progress": True,
    "progress_percent": 65,
    "estimated_completion": "Bientôt disponible",
    "contact_email": "contact@bionic.ca",
    "updated_at": datetime.now(timezone.utc).isoformat(),
    "updated_by": "system"
}


# ============================================
# FEATURE SYNC FUNCTIONS
# ============================================

# Import feature definitions from feature_controls module
FEATURE_IDS = [
    "social_posts", "comments", "likes", "groups",
    "push_notifications", "email_notifications", "email_digest",
    "social_sharing_facebook", "social_sharing_instagram", "seo_auto_generation",
    "marketplace", "payments", "lands_rental",
    "referral_program", "wallet_system",
    "user_registration", "auto_login", "password_reset",
    "ai_species_recognition", "ai_territory_analysis", "ai_product_categorization",
    "leads_management", "contacts_management"
]


async def backup_feature_states():
    """Save current feature states before disabling for maintenance"""
    database = await get_db()
    
    # Get all current feature states
    features = await database.feature_controls.find({}, {"_id": 0}).to_list(100)
    feature_states = {f["feature_id"]: f["enabled"] for f in features}
    
    # Save to maintenance backup collection
    await database.maintenance_feature_backup.update_one(
        {"_id": "backup"},
        {
            "$set": {
                "states": feature_states,
                "backed_up_at": datetime.now(timezone.utc).isoformat()
            }
        },
        upsert=True
    )
    
    logger.info(f"Backed up {len(feature_states)} feature states for maintenance")
    return feature_states


async def disable_all_features(admin_email: str = "system"):
    """Disable all features when entering maintenance mode"""
    database = await get_db()
    
    disabled_count = 0
    for feature_id in FEATURE_IDS:
        await database.feature_controls.update_one(
            {"feature_id": feature_id},
            {
                "$set": {
                    "feature_id": feature_id,
                    "enabled": False,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "updated_by": admin_email,
                    "disabled_by_maintenance": True
                }
            },
            upsert=True
        )
        disabled_count += 1
    
    # Log to feature control logs
    await database.feature_control_logs.insert_one({
        "feature_id": "ALL_FEATURES",
        "feature_name": "Toutes les fonctionnalités",
        "old_value": True,
        "new_value": False,
        "changed_by": admin_email,
        "changed_at": datetime.now(timezone.utc).isoformat(),
        "reason": "Mode maintenance activé - Désactivation automatique"
    })
    
    logger.info(f"Disabled {disabled_count} features for maintenance mode")
    return disabled_count


async def restore_feature_states(admin_email: str = "system"):
    """Restore feature states from backup when exiting maintenance mode"""
    database = await get_db()
    
    # Get backup
    backup = await database.maintenance_feature_backup.find_one({"_id": "backup"})
    
    if not backup or not backup.get("states"):
        logger.warning("No feature backup found, features will remain in current state")
        return 0
    
    restored_count = 0
    for feature_id, was_enabled in backup["states"].items():
        await database.feature_controls.update_one(
            {"feature_id": feature_id},
            {
                "$set": {
                    "enabled": was_enabled,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "updated_by": admin_email,
                    "disabled_by_maintenance": False
                }
            }
        )
        restored_count += 1
    
    # For features not in backup (were using defaults), remove the override
    backed_up_ids = set(backup["states"].keys())
    for feature_id in FEATURE_IDS:
        if feature_id not in backed_up_ids:
            await database.feature_controls.delete_one({"feature_id": feature_id})
    
    # Log restoration
    await database.feature_control_logs.insert_one({
        "feature_id": "ALL_FEATURES",
        "feature_name": "Toutes les fonctionnalités",
        "old_value": False,
        "new_value": True,
        "changed_by": admin_email,
        "changed_at": datetime.now(timezone.utc).isoformat(),
        "reason": "Sortie du mode maintenance - Restauration automatique"
    })
    
    logger.info(f"Restored {restored_count} feature states from maintenance backup")
    return restored_count


# ============================================
# API ENDPOINTS
# ============================================

@access_router.get("/status")
async def get_site_status():
    """Get current site status (public endpoint)"""
    database = await get_db()
    
    config = await database.site_config.find_one({"_id": "main"})
    
    if not config:
        # Initialize with default config (development mode)
        config = DEFAULT_CONFIG.copy()
        config["_id"] = "main"
        await database.site_config.insert_one(config)
        del config["_id"]
    else:
        del config["_id"]
    
    return {
        "mode": config.get("mode", "live"),
        "message": config.get("message", ""),
        "show_progress": config.get("show_progress", False),
        "progress_percent": config.get("progress_percent", 0),
        "estimated_completion": config.get("estimated_completion", ""),
        "contact_email": config.get("contact_email", ""),
        "is_accessible": config.get("mode") == "live"
    }

@access_router.get("/config")
async def get_site_config():
    """Get full site configuration (admin only)"""
    database = await get_db()
    
    config = await database.site_config.find_one({"_id": "main"})
    
    if not config:
        config = DEFAULT_CONFIG.copy()
        config["_id"] = "main"
        await database.site_config.insert_one(config)
    
    return {
        "mode": config.get("mode", "live"),
        "message": config.get("message", ""),
        "allowed_ips": config.get("allowed_ips", []),
        "show_progress": config.get("show_progress", False),
        "progress_percent": config.get("progress_percent", 0),
        "estimated_completion": config.get("estimated_completion", ""),
        "contact_email": config.get("contact_email", ""),
        "updated_at": config.get("updated_at", ""),
        "updated_by": config.get("updated_by", "")
    }

@access_router.put("/mode")
async def update_site_mode(
    update: UpdateSiteMode,
    admin: UserWithRole = Depends(require_admin)
):
    """Update site mode (admin only) - Auto-syncs feature controls"""
    database = await get_db()
    
    # Get current mode to detect mode changes
    current_config = await database.site_config.find_one({"_id": "main"})
    current_mode = current_config.get("mode", "live") if current_config else "live"
    
    update_data = {
        "mode": update.mode,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "updated_by": admin.email
    }
    
    if update.message is not None:
        update_data["message"] = update.message
    if update.show_progress is not None:
        update_data["show_progress"] = update.show_progress
    if update.progress_percent is not None:
        update_data["progress_percent"] = max(0, min(100, update.progress_percent))
    if update.estimated_completion is not None:
        update_data["estimated_completion"] = update.estimated_completion
    if update.contact_email is not None:
        update_data["contact_email"] = update.contact_email
    
    # Handle feature sync based on mode change
    features_action = None
    features_count = 0
    
    # ENTERING maintenance mode - backup and disable all features
    if update.mode == "maintenance" and current_mode != "maintenance":
        await backup_feature_states()
        features_count = await disable_all_features(admin.email)
        features_action = "disabled"
        logger.info(f"Entering maintenance mode - {features_count} features disabled by {admin.email}")
    
    # EXITING maintenance mode to live - restore feature states
    elif current_mode == "maintenance" and update.mode == "live":
        features_count = await restore_feature_states(admin.email)
        features_action = "restored"
        logger.info(f"Exiting maintenance mode - {features_count} features restored by {admin.email}")
    
    await database.site_config.update_one(
        {"_id": "main"},
        {"$set": update_data},
        upsert=True
    )
    
    mode_labels = {
        "live": "🟢 En ligne",
        "development": "🟡 En développement",
        "maintenance": "🔴 En maintenance"
    }
    
    logger.info(f"Site mode changed to: {update.mode}")
    
    response = {
        "success": True,
        "mode": update.mode,
        "mode_label": mode_labels.get(update.mode, update.mode),
        "message": f"Mode du site changé: {mode_labels.get(update.mode, update.mode)}"
    }
    
    # Add feature sync info to response
    if features_action:
        response["features_sync"] = {
            "action": features_action,
            "count": features_count,
            "message": f"{features_count} fonctionnalités {'désactivées' if features_action == 'disabled' else 'restaurées'}"
        }
    
    return response

@access_router.post("/add-allowed-ip")
async def add_allowed_ip(
    ip: str = Query(...),
    admin: UserWithRole = Depends(require_admin)
):
    """Add an IP to the allowed list (admin only)"""
    database = await get_db()
    
    await database.site_config.update_one(
        {"_id": "main"},
        {"$addToSet": {"allowed_ips": ip}},
        upsert=True
    )
    
    logger.info(f"IP {ip} whitelisted by {admin.email}")
    return {"success": True, "message": f"IP {ip} ajoutée à la liste blanche"}

@access_router.delete("/remove-allowed-ip")
async def remove_allowed_ip(
    ip: str = Query(...),
    admin: UserWithRole = Depends(require_admin)
):
    """Remove an IP from the allowed list (admin only)"""
    database = await get_db()
    
    await database.site_config.update_one(
        {"_id": "main"},
        {"$pull": {"allowed_ips": ip}}
    )
    
    logger.info(f"IP {ip} removed from whitelist by {admin.email}")
    return {"success": True, "message": f"IP {ip} retirée de la liste blanche"}

# ============================================
# ACCESS LOG
# ============================================

@access_router.get("/access-log")
async def get_access_log(
    limit: int = 50,
    admin: UserWithRole = Depends(require_admin)
):
    """Get recent access attempts log (admin only)"""
    database = await get_db()
    
    logs = await database.access_log.find({}).sort("timestamp", -1).limit(limit).to_list(limit)
    
    return {
        "logs": [{k: v for k, v in log.items() if k != "_id"} for log in logs],
        "total": await database.access_log.count_documents({})
    }

@access_router.post("/log-access")
async def log_access(
    page: str = Query(...),
    user_agent: Optional[str] = None,
    ip: Optional[str] = None
):
    """Log an access attempt (for analytics)"""
    database = await get_db()
    
    log_entry = {
        "page": page,
        "user_agent": user_agent,
        "ip": ip,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "blocked": False  # Will be set by frontend
    }
    
    await database.access_log.insert_one(log_entry)
    
    return {"logged": True}

logger.info("Site Access Control module initialized")
