"""
Maintenance Mode Controller - Secure & Persistent
- 100% persistent maintenance mode stored in MongoDB
- Password-protected activation/deactivation
- No auto-disable, no bypass except explicit admin auth
- Logging of all mode changes
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone
import os
import hashlib
import logging
from motor.motor_asyncio import AsyncIOMotorClient

router = APIRouter(prefix="/api/maintenance", tags=["Maintenance Mode"])

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Database connection
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "bionic_territory")

# Admin password hash (SHA256 of Saturn5858*)
ADMIN_PASSWORD_HASH = hashlib.sha256("Saturn5858*".encode()).hexdigest()

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

class MaintenanceConfig(BaseModel):
    is_active: bool = False
    message: str = "🚧 Site en maintenance. Nous revenons bientôt!"
    show_progress: bool = True
    progress_percent: int = 0
    estimated_completion: Optional[str] = None
    contact_email: str = "contact@bionic.ca"
    activated_at: Optional[str] = None
    activated_by: str = "system"
    last_modified_at: str = ""
    modification_count: int = 0
    allowed_bypass_tokens: List[str] = []  # Admin tokens that can bypass


class MaintenanceToggleRequest(BaseModel):
    admin_password: str = Field(..., description="Admin password required")
    activate: bool = Field(..., description="True to activate, False to deactivate")
    message: Optional[str] = None
    progress_percent: Optional[int] = None
    estimated_completion: Optional[str] = None


class MaintenanceUpdateRequest(BaseModel):
    admin_password: str = Field(..., description="Admin password required")
    message: Optional[str] = None
    show_progress: Optional[bool] = None
    progress_percent: Optional[int] = None
    estimated_completion: Optional[str] = None
    contact_email: Optional[str] = None


class AdminBypassRequest(BaseModel):
    admin_password: str = Field(..., description="Admin password to get bypass token")


# ============================================
# HELPER FUNCTIONS
# ============================================

def verify_admin_password(password: str) -> bool:
    """Verify admin password using SHA256 hash comparison"""
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    return password_hash == ADMIN_PASSWORD_HASH


def generate_bypass_token() -> str:
    """Generate a unique bypass token for admin access"""
    import secrets
    return secrets.token_urlsafe(32)


async def get_maintenance_config() -> dict:
    """Get current maintenance configuration from database"""
    database = await get_db()
    config = await database.maintenance_mode.find_one({"_id": "config"})
    
    if not config:
        # Initialize with maintenance DISABLED by default
        default_config = {
            "_id": "config",
            "is_active": False,
            "message": "🚧 Site en maintenance. Nous revenons bientôt!",
            "show_progress": True,
            "progress_percent": 0,
            "estimated_completion": None,
            "contact_email": "contact@bionic.ca",
            "activated_at": None,
            "activated_by": "system",
            "last_modified_at": datetime.now(timezone.utc).isoformat(),
            "modification_count": 0,
            "allowed_bypass_tokens": []
        }
        await database.maintenance_mode.insert_one(default_config)
        config = default_config
    
    return config


async def log_maintenance_action(action: str, details: dict):
    """Log all maintenance mode actions for audit trail"""
    database = await get_db()
    log_entry = {
        "action": action,
        "details": details,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ip_address": details.get("ip_address", "unknown")
    }
    await database.maintenance_logs.insert_one(log_entry)
    logger.info(f"Maintenance action: {action} - {details}")


# ============================================
# PUBLIC ENDPOINTS (No Auth Required)
# ============================================

@router.get("/status")
async def get_maintenance_status():
    """
    Get current maintenance mode status.
    This is the ONLY endpoint that should be checked to determine site accessibility.
    Returns: is_active (bool), message, progress info
    """
    config = await get_maintenance_config()
    
    return {
        "is_active": config.get("is_active", False),
        "message": config.get("message", ""),
        "show_progress": config.get("show_progress", True),
        "progress_percent": config.get("progress_percent", 0),
        "estimated_completion": config.get("estimated_completion"),
        "contact_email": config.get("contact_email", ""),
        "activated_at": config.get("activated_at"),
        # IMPORTANT: Never expose bypass tokens or admin info in public endpoint
    }


@router.post("/verify-bypass")
async def verify_bypass_token(token: str):
    """
    Verify if a bypass token is valid.
    Used by frontend to check if user has admin access during maintenance.
    """
    config = await get_maintenance_config()
    allowed_tokens = config.get("allowed_bypass_tokens", [])
    
    is_valid = token in allowed_tokens
    
    return {
        "valid": is_valid,
        "maintenance_active": config.get("is_active", False)
    }


# ============================================
# PROTECTED ENDPOINTS (Password Required)
# ============================================

@router.post("/toggle")
async def toggle_maintenance_mode(request: MaintenanceToggleRequest):
    """
    Toggle maintenance mode ON or OFF.
    REQUIRES admin password for BOTH activation AND deactivation.
    This is the ONLY way to change maintenance mode status.
    """
    # Verify admin password
    if not verify_admin_password(request.admin_password):
        await log_maintenance_action("TOGGLE_FAILED", {
            "reason": "Invalid password",
            "attempted_action": "activate" if request.activate else "deactivate"
        })
        raise HTTPException(
            status_code=401, 
            detail="Mot de passe administrateur invalide"
        )
    
    database = await get_db()
    config = await get_maintenance_config()
    
    current_state = config.get("is_active", False)
    new_state = request.activate
    
    # Build update data
    update_data = {
        "is_active": new_state,
        "last_modified_at": datetime.now(timezone.utc).isoformat(),
        "modification_count": config.get("modification_count", 0) + 1
    }
    
    if new_state:  # Activating maintenance
        update_data["activated_at"] = datetime.now(timezone.utc).isoformat()
        update_data["activated_by"] = "admin"
        if request.message:
            update_data["message"] = request.message
        if request.progress_percent is not None:
            update_data["progress_percent"] = max(0, min(100, request.progress_percent))
        if request.estimated_completion:
            update_data["estimated_completion"] = request.estimated_completion
    else:  # Deactivating maintenance
        update_data["activated_at"] = None
        update_data["activated_by"] = "system"
        # Clear bypass tokens when deactivating
        update_data["allowed_bypass_tokens"] = []
    
    # Update database
    await database.maintenance_mode.update_one(
        {"_id": "config"},
        {"$set": update_data}
    )
    
    # Log the action
    await log_maintenance_action(
        "MAINTENANCE_TOGGLED",
        {
            "previous_state": current_state,
            "new_state": new_state,
            "message": request.message if request.message else config.get("message")
        }
    )
    
    # Also sync with site_config for backward compatibility
    await database.site_config.update_one(
        {"_id": "main"},
        {"$set": {
            "mode": "maintenance" if new_state else "live",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "updated_by": "admin"
        }},
        upsert=True
    )
    
    action_text = "activé" if new_state else "désactivé"
    return {
        "success": True,
        "is_active": new_state,
        "message": f"Mode maintenance {action_text} avec succès",
        "activated_at": update_data.get("activated_at"),
        "modification_count": update_data["modification_count"]
    }


@router.post("/update")
async def update_maintenance_settings(request: MaintenanceUpdateRequest):
    """
    Update maintenance mode settings (message, progress, etc.)
    REQUIRES admin password.
    Does NOT change the is_active status - use /toggle for that.
    """
    # Verify admin password
    if not verify_admin_password(request.admin_password):
        await log_maintenance_action("UPDATE_FAILED", {
            "reason": "Invalid password"
        })
        raise HTTPException(
            status_code=401, 
            detail="Mot de passe administrateur invalide"
        )
    
    database = await get_db()
    config = await get_maintenance_config()
    
    update_data = {
        "last_modified_at": datetime.now(timezone.utc).isoformat(),
        "modification_count": config.get("modification_count", 0) + 1
    }
    
    if request.message is not None:
        update_data["message"] = request.message
    if request.show_progress is not None:
        update_data["show_progress"] = request.show_progress
    if request.progress_percent is not None:
        update_data["progress_percent"] = max(0, min(100, request.progress_percent))
    if request.estimated_completion is not None:
        update_data["estimated_completion"] = request.estimated_completion
    if request.contact_email is not None:
        update_data["contact_email"] = request.contact_email
    
    await database.maintenance_mode.update_one(
        {"_id": "config"},
        {"$set": update_data}
    )
    
    await log_maintenance_action("SETTINGS_UPDATED", {
        "changes": {k: v for k, v in update_data.items() if k != "last_modified_at"}
    })
    
    return {
        "success": True,
        "message": "Paramètres mis à jour avec succès"
    }


@router.post("/get-bypass-token")
async def get_admin_bypass_token(request: AdminBypassRequest):
    """
    Get a bypass token for admin access during maintenance.
    REQUIRES admin password.
    Token allows bypassing maintenance mode in frontend.
    """
    # Verify admin password
    if not verify_admin_password(request.admin_password):
        await log_maintenance_action("BYPASS_TOKEN_FAILED", {
            "reason": "Invalid password"
        })
        raise HTTPException(
            status_code=401, 
            detail="Mot de passe administrateur invalide"
        )
    
    database = await get_db()
    config = await get_maintenance_config()
    
    # Generate new bypass token
    new_token = generate_bypass_token()
    
    # Add to allowed tokens (keep max 10 tokens)
    allowed_tokens = config.get("allowed_bypass_tokens", [])
    allowed_tokens.append(new_token)
    if len(allowed_tokens) > 10:
        allowed_tokens = allowed_tokens[-10:]  # Keep only last 10
    
    await database.maintenance_mode.update_one(
        {"_id": "config"},
        {"$set": {"allowed_bypass_tokens": allowed_tokens}}
    )
    
    await log_maintenance_action("BYPASS_TOKEN_GENERATED", {
        "token_count": len(allowed_tokens)
    })
    
    return {
        "success": True,
        "bypass_token": new_token,
        "message": "Token de contournement généré. Utilisez-le pour accéder au site en maintenance."
    }


@router.post("/revoke-all-tokens")
async def revoke_all_bypass_tokens(request: AdminBypassRequest):
    """
    Revoke all bypass tokens.
    REQUIRES admin password.
    Forces all admin users to re-authenticate.
    """
    # Verify admin password
    if not verify_admin_password(request.admin_password):
        raise HTTPException(
            status_code=401, 
            detail="Mot de passe administrateur invalide"
        )
    
    database = await get_db()
    
    await database.maintenance_mode.update_one(
        {"_id": "config"},
        {"$set": {"allowed_bypass_tokens": []}}
    )
    
    await log_maintenance_action("ALL_TOKENS_REVOKED", {})
    
    return {
        "success": True,
        "message": "Tous les tokens de contournement ont été révoqués"
    }


@router.get("/logs")
async def get_maintenance_logs(
    limit: int = 50,
    admin_password: str = None
):
    """
    Get maintenance mode audit logs.
    REQUIRES admin password as query parameter.
    """
    if not admin_password or not verify_admin_password(admin_password):
        raise HTTPException(
            status_code=401, 
            detail="Mot de passe administrateur requis"
        )
    
    database = await get_db()
    
    logs = await database.maintenance_logs.find(
        {},
        {"_id": 0}
    ).sort("timestamp", -1).limit(limit).to_list(length=limit)
    
    return {
        "success": True,
        "logs": logs,
        "total": len(logs)
    }


@router.get("/full-config")
async def get_full_maintenance_config(admin_password: str = None):
    """
    Get full maintenance configuration including sensitive data.
    REQUIRES admin password as query parameter.
    """
    if not admin_password or not verify_admin_password(admin_password):
        raise HTTPException(
            status_code=401, 
            detail="Mot de passe administrateur requis"
        )
    
    config = await get_maintenance_config()
    
    # Remove _id from response
    if "_id" in config:
        del config["_id"]
    
    return {
        "success": True,
        "config": config
    }
