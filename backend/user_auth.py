"""
User Authentication Module
- Unified login for all site modules
- IP-based auto-login (device recognition)
- Session management
"""

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime, timezone, timedelta
import uuid
import hashlib
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

auth_router = APIRouter(prefix="/api/auth", tags=["Authentication"])

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

class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5)
    password: str = Field(..., min_length=6)
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str
    remember_device: bool = False

class DeviceInfo(BaseModel):
    ip_address: str
    user_agent: Optional[str] = None
    device_name: Optional[str] = None

class PasswordResetRequest(BaseModel):
    email: str

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6)

# ============================================
# HELPER FUNCTIONS
# ============================================

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token(user_id: str) -> str:
    return hashlib.sha256(f"{user_id}{datetime.now(timezone.utc).isoformat()}{uuid.uuid4()}".encode()).hexdigest()

def generate_reset_token() -> str:
    """Generate a secure password reset token"""
    return hashlib.sha256(f"{uuid.uuid4()}{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()[:32]

def get_client_ip(request: Request) -> str:
    """Extract client IP from request, handling proxies"""
    # Check for forwarded IP (behind proxy/load balancer)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Direct connection
    return request.client.host if request.client else "unknown"

# ============================================
# USER REGISTRATION
# ============================================

@auth_router.post("/register")
async def register_user(user: UserRegister, request: Request):
    """Register a new user"""
    database = await get_db()
    
    # Check if email exists
    existing = await database.users.find_one({"email": user.email.lower()})
    if existing:
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")
    
    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    user_data = {
        "id": user_id,
        "name": user.name,
        "email": user.email.lower(),
        "phone": user.phone,
        "hashed_password": hash_password(user.password),
        "is_verified": False,
        "is_active": True,
        "role": "user",  # user, admin, owner, hunter
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
        "last_login": now.isoformat(),
        "login_count": 1,
        # Linked accounts
        "marketplace_seller_id": None,
        "land_owner_id": None,
        "land_renter_id": None,
        # Preferences
        "preferences": {
            "notifications": True,
            "newsletter": True,
            "language": "fr"
        }
    }
    
    await database.users.insert_one(user_data)
    
    # Generate token
    token = generate_token(user_id)
    
    # Store session
    client_ip = get_client_ip(request)
    await database.user_sessions.insert_one({
        "user_id": user_id,
        "token": token,
        "ip_address": client_ip,
        "user_agent": request.headers.get("User-Agent", ""),
        "created_at": now.isoformat(),
        "expires_at": (now + timedelta(days=30)).isoformat(),
        "is_active": True
    })
    
    logger.info(f"New user registered: {user.email}")
    
    # Send welcome email with credentials (async, non-blocking)
    try:
        from email_notifications import send_welcome_email
        import asyncio
        asyncio.create_task(send_welcome_email(
            user_id=user_id,
            user_email=user.email.lower(),
            user_password=user.password  # Original password before hashing
        ))
    except Exception as e:
        logger.warning(f"Could not send welcome email: {e}")
    
    return {
        "success": True,
        "token": token,
        "user": {
            "id": user_id,
            "name": user.name,
            "email": user.email.lower(),
            "role": "user"
        }
    }

# ============================================
# USER LOGIN
# ============================================

@auth_router.post("/login")
async def login_user(credentials: UserLogin, request: Request):
    """Login user with email and password"""
    database = await get_db()
    
    user = await database.users.find_one({
        "email": credentials.email.lower(),
        "hashed_password": hash_password(credentials.password)
    })
    
    if not user:
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="Compte désactivé")
    
    now = datetime.now(timezone.utc)
    client_ip = get_client_ip(request)
    user_agent = request.headers.get("User-Agent", "")
    
    # Generate token
    token = generate_token(user["id"])
    
    # Store session
    session_duration = timedelta(days=90) if credentials.remember_device else timedelta(days=7)
    
    session_data = {
        "user_id": user["id"],
        "token": token,
        "ip_address": client_ip,
        "user_agent": user_agent,
        "created_at": now.isoformat(),
        "expires_at": (now + session_duration).isoformat(),
        "is_active": True,
        "remember_device": credentials.remember_device
    }
    
    await database.user_sessions.insert_one(session_data)
    
    # If remember_device, also store trusted device
    if credentials.remember_device:
        await database.trusted_devices.update_one(
            {"user_id": user["id"], "ip_address": client_ip},
            {
                "$set": {
                    "user_id": user["id"],
                    "ip_address": client_ip,
                    "user_agent": user_agent,
                    "device_name": f"Appareil ({client_ip[:8]}...)",
                    "last_used": now.isoformat(),
                    "created_at": now.isoformat(),
                    "is_trusted": True
                }
            },
            upsert=True
        )
    
    # Update user last login
    await database.users.update_one(
        {"id": user["id"]},
        {
            "$set": {"last_login": now.isoformat()},
            "$inc": {"login_count": 1}
        }
    )
    
    logger.info(f"User logged in: {user['email']} from IP {client_ip}")
    
    return {
        "success": True,
        "token": token,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user.get("role", "user"),
            "phone": user.get("phone"),
            "preferences": user.get("preferences", {})
        },
        "device_trusted": credentials.remember_device
    }

# ============================================
# AUTO-LOGIN BY IP (Device Recognition)
# ============================================

@auth_router.get("/auto-login")
async def auto_login_by_ip(request: Request):
    """Try to auto-login user based on trusted IP/device"""
    database = await get_db()
    
    client_ip = get_client_ip(request)
    user_agent = request.headers.get("User-Agent", "")
    
    # Check for trusted device
    trusted_device = await database.trusted_devices.find_one({
        "ip_address": client_ip,
        "is_trusted": True
    })
    
    if not trusted_device:
        return {
            "success": False,
            "auto_login": False,
            "message": "Appareil non reconnu"
        }
    
    # Get user
    user = await database.users.find_one({"id": trusted_device["user_id"]})
    
    if not user or not user.get("is_active", True):
        return {
            "success": False,
            "auto_login": False,
            "message": "Utilisateur non trouvé ou désactivé"
        }
    
    now = datetime.now(timezone.utc)
    
    # Generate new token
    token = generate_token(user["id"])
    
    # Create session
    await database.user_sessions.insert_one({
        "user_id": user["id"],
        "token": token,
        "ip_address": client_ip,
        "user_agent": user_agent,
        "created_at": now.isoformat(),
        "expires_at": (now + timedelta(days=90)).isoformat(),
        "is_active": True,
        "auto_login": True
    })
    
    # Update device last used
    await database.trusted_devices.update_one(
        {"ip_address": client_ip, "user_id": user["id"]},
        {"$set": {"last_used": now.isoformat()}}
    )
    
    # Update user last login
    await database.users.update_one(
        {"id": user["id"]},
        {
            "$set": {"last_login": now.isoformat()},
            "$inc": {"login_count": 1}
        }
    )
    
    logger.info(f"Auto-login successful for {user['email']} from IP {client_ip}")
    
    return {
        "success": True,
        "auto_login": True,
        "token": token,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user.get("role", "user"),
            "phone": user.get("phone"),
            "preferences": user.get("preferences", {})
        },
        "device_name": trusted_device.get("device_name", "Appareil reconnu")
    }

# ============================================
# VERIFY SESSION
# ============================================

@auth_router.get("/verify")
async def verify_session(token: str = Query(...)):
    """Verify if a session token is valid"""
    database = await get_db()
    
    session = await database.user_sessions.find_one({
        "token": token,
        "is_active": True
    })
    
    if not session:
        return {"valid": False, "message": "Session invalide"}
    
    # Check expiry
    expires_at = datetime.fromisoformat(session["expires_at"].replace('Z', '+00:00'))
    if expires_at < datetime.now(timezone.utc):
        # Session expired, deactivate it
        await database.user_sessions.update_one(
            {"token": token},
            {"$set": {"is_active": False}}
        )
        return {"valid": False, "message": "Session expirée"}
    
    # Get user
    user = await database.users.find_one({"id": session["user_id"]})
    
    if not user or not user.get("is_active", True):
        return {"valid": False, "message": "Utilisateur non trouvé"}
    
    return {
        "valid": True,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user.get("role", "user"),
            "phone": user.get("phone")
        }
    }

# ============================================
# LOGOUT
# ============================================

@auth_router.post("/logout")
async def logout_user(token: str = Query(...)):
    """Logout user and invalidate session"""
    database = await get_db()
    
    result = await database.user_sessions.update_one(
        {"token": token},
        {"$set": {"is_active": False}}
    )
    
    return {
        "success": True,
        "message": "Déconnexion réussie"
    }

@auth_router.post("/logout-all")
async def logout_all_devices(user_id: str = Query(...)):
    """Logout from all devices"""
    database = await get_db()
    
    await database.user_sessions.update_many(
        {"user_id": user_id},
        {"$set": {"is_active": False}}
    )
    
    return {
        "success": True,
        "message": "Déconnexion de tous les appareils"
    }

# ============================================
# TRUSTED DEVICES MANAGEMENT
# ============================================

@auth_router.get("/devices")
async def get_trusted_devices(user_id: str = Query(...)):
    """Get list of trusted devices for a user"""
    database = await get_db()
    
    devices = await database.trusted_devices.find(
        {"user_id": user_id, "is_trusted": True},
        {"_id": 0}
    ).to_list(50)
    
    return {"devices": devices}

@auth_router.delete("/devices/{device_ip}")
async def remove_trusted_device(device_ip: str, user_id: str = Query(...)):
    """Remove a trusted device"""
    database = await get_db()
    
    await database.trusted_devices.update_one(
        {"user_id": user_id, "ip_address": device_ip},
        {"$set": {"is_trusted": False}}
    )
    
    # Also invalidate sessions from this IP
    await database.user_sessions.update_many(
        {"user_id": user_id, "ip_address": device_ip},
        {"$set": {"is_active": False}}
    )
    
    return {"success": True, "message": "Appareil retiré"}

# ============================================
# USER PROFILE
# ============================================

@auth_router.get("/profile/{user_id}")
async def get_user_profile(user_id: str):
    """Get user profile"""
    database = await get_db()
    
    user = await database.users.find_one({"id": user_id}, {"_id": 0, "hashed_password": 0})
    
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    return {"user": user}

@auth_router.put("/profile/{user_id}")
async def update_user_profile(
    user_id: str,
    name: Optional[str] = None,
    phone: Optional[str] = None,
    preferences: Optional[Dict] = None
):
    """Update user profile"""
    database = await get_db()
    
    update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
    
    if name:
        update_data["name"] = name
    if phone:
        update_data["phone"] = phone
    if preferences:
        update_data["preferences"] = preferences
    
    await database.users.update_one(
        {"id": user_id},
        {"$set": update_data}
    )
    
    return {"success": True, "message": "Profil mis à jour"}

# ============================================
# CHECK IP INFO
# ============================================

@auth_router.get("/ip-info")
async def get_ip_info(request: Request):
    """Get current client IP and device info"""
    client_ip = get_client_ip(request)
    user_agent = request.headers.get("User-Agent", "")
    
    database = await get_db()
    
    # Check if IP is trusted
    trusted_device = await database.trusted_devices.find_one({
        "ip_address": client_ip,
        "is_trusted": True
    })
    
    return {
        "ip_address": client_ip,
        "user_agent": user_agent,
        "is_trusted": trusted_device is not None,
        "device_name": trusted_device.get("device_name") if trusted_device else None,
        "user_id": trusted_device.get("user_id") if trusted_device else None
    }

# ============================================
# PASSWORD RESET
# ============================================

@auth_router.post("/forgot-password")
async def request_password_reset(request_data: PasswordResetRequest):
    """Request a password reset email"""
    database = await get_db()
    
    email = request_data.email.lower().strip()
    
    # Find user by email
    user = await database.users.find_one({"email": email}, {"_id": 0})
    
    # Always return success to prevent email enumeration
    if not user:
        logger.warning(f"Password reset requested for non-existent email: {email}")
        return {
            "success": True,
            "message": "Si un compte existe avec cet email, vous recevrez un lien de réinitialisation."
        }
    
    # Generate reset token
    reset_token = generate_reset_token()
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)  # Token valid for 1 hour
    
    # Store reset token in database
    await database.password_resets.delete_many({"user_id": user["id"]})  # Remove old tokens
    await database.password_resets.insert_one({
        "id": str(uuid.uuid4()),
        "user_id": user["id"],
        "email": email,
        "token": reset_token,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": expires_at.isoformat(),
        "used": False
    })
    
    # Send reset email
    try:
        from email_notifications import send_password_reset_email
        import asyncio
        asyncio.create_task(send_password_reset_email(
            user_email=email,
            user_name=user.get("name", "Utilisateur"),
            reset_token=reset_token
        ))
        logger.info(f"Password reset email sent to: {email}")
    except Exception as e:
        logger.error(f"Failed to send reset email: {e}")
    
    return {
        "success": True,
        "message": "Si un compte existe avec cet email, vous recevrez un lien de réinitialisation."
    }


@auth_router.post("/reset-password")
async def reset_password(request_data: PasswordResetConfirm):
    """Reset password using token"""
    database = await get_db()
    
    # Find the reset token
    reset_record = await database.password_resets.find_one({
        "token": request_data.token,
        "used": False
    }, {"_id": 0})
    
    if not reset_record:
        raise HTTPException(status_code=400, detail="Token invalide ou expiré")
    
    # Check if token is expired
    expires_at = datetime.fromisoformat(reset_record["expires_at"].replace("Z", "+00:00"))
    if datetime.now(timezone.utc) > expires_at:
        await database.password_resets.update_one(
            {"token": request_data.token},
            {"$set": {"used": True}}
        )
        raise HTTPException(status_code=400, detail="Le lien de réinitialisation a expiré")
    
    # Update user's password
    new_hashed_password = hash_password(request_data.new_password)
    
    await database.users.update_one(
        {"id": reset_record["user_id"]},
        {
            "$set": {
                "hashed_password": new_hashed_password,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    # Mark token as used
    await database.password_resets.update_one(
        {"token": request_data.token},
        {"$set": {"used": True, "used_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    # Send confirmation email
    try:
        from email_notifications import send_password_changed_email
        import asyncio
        asyncio.create_task(send_password_changed_email(
            user_email=reset_record["email"],
            user_name=reset_record.get("user_name", "Utilisateur"),
            new_password=request_data.new_password
        ))
    except Exception as e:
        logger.warning(f"Could not send password changed email: {e}")
    
    logger.info(f"Password reset successful for user: {reset_record['user_id']}")
    
    return {
        "success": True,
        "message": "Mot de passe réinitialisé avec succès"
    }


@auth_router.get("/verify-reset-token/{token}")
async def verify_reset_token(token: str):
    """Verify if a reset token is valid"""
    database = await get_db()
    
    reset_record = await database.password_resets.find_one({
        "token": token,
        "used": False
    }, {"_id": 0})
    
    if not reset_record:
        return {"valid": False, "message": "Token invalide"}
    
    # Check if token is expired
    expires_at = datetime.fromisoformat(reset_record["expires_at"].replace("Z", "+00:00"))
    if datetime.now(timezone.utc) > expires_at:
        return {"valid": False, "message": "Token expiré"}
    
    return {
        "valid": True,
        "email": reset_record["email"]
    }


logger.info("User Authentication module initialized")
