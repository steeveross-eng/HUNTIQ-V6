"""
Auth Engine - API Router
Hybrid Authentication: JWT (email/password) + Google OAuth
Phase P4 Security Update
"""
from fastapi import APIRouter, HTTPException, Request, Depends, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from datetime import datetime, timezone
import logging

from .models import (
    UserCreate, UserLogin, UserResponse, TokenResponse,
    GoogleAuthCallback, PasswordReset
)
from .service import AuthService

# Database dependency
def get_db():
    from database import Database
    return Database.get_database()

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)

# Optional bearer token - don't make it required
security = HTTPBearer(auto_error=False)


def get_client_ip(request: Request) -> str:
    """Get client IP address"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[UserResponse]:
    """Get current authenticated user from token"""
    db = get_db()
    service = AuthService(db)
    
    # Try Authorization header first
    token = None
    if credentials:
        token = credentials.credentials
    
    # Fall back to cookie
    if not token:
        token = request.cookies.get("session_token")
    
    # Fall back to query param (for legacy support)
    if not token:
        token = request.query_params.get("token")
    
    if not token:
        return None
    
    return await service.verify_session(token)


async def require_auth(
    user: Optional[UserResponse] = Depends(get_current_user)
) -> UserResponse:
    """Require authenticated user"""
    if not user:
        raise HTTPException(status_code=401, detail="Non authentifié")
    return user


# ==========================================
# Registration & Login
# ==========================================

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, request: Request, response: Response):
    """Register a new user with email/password"""
    db = get_db()
    service = AuthService(db)
    
    success, token_response, error = await service.register(user_data)
    
    if not success:
        raise HTTPException(status_code=400, detail=error)
    
    # Set cookie
    response.set_cookie(
        key="session_token",
        value=token_response.token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=60 * 60 * 24 * 7,  # 7 days
        path="/"
    )
    
    return token_response


@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLogin, request: Request, response: Response):
    """Login with email/password"""
    db = get_db()
    service = AuthService(db)
    
    ip_address = get_client_ip(request)
    user_agent = request.headers.get("User-Agent")
    
    success, token_response, error = await service.login(
        login_data, ip_address, user_agent
    )
    
    if not success:
        raise HTTPException(status_code=401, detail=error)
    
    # Set cookie
    response.set_cookie(
        key="session_token",
        value=token_response.token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=60 * 60 * 24 * 7,
        path="/"
    )
    
    return token_response


# ==========================================
# Google OAuth
# ==========================================

@router.post("/google/callback", response_model=TokenResponse)
async def google_callback(callback_data: GoogleAuthCallback, response: Response):
    """
    Handle Google OAuth callback from Emergent Auth
    REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    """
    db = get_db()
    service = AuthService(db)
    
    success, token_response, error = await service.google_auth_callback(
        callback_data.session_id
    )
    
    if not success:
        raise HTTPException(status_code=401, detail=error)
    
    # Set cookie
    response.set_cookie(
        key="session_token",
        value=token_response.token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=60 * 60 * 24 * 7,
        path="/"
    )
    
    return token_response


# ==========================================
# Session Management
# ==========================================

@router.get("/me", response_model=UserResponse)
async def get_me(user: UserResponse = Depends(require_auth)):
    """Get current user info"""
    return user


@router.get("/verify")
async def verify_token(token: str):
    """Verify if a token is valid"""
    db = get_db()
    service = AuthService(db)
    
    user = await service.verify_session(token)
    
    return {
        "valid": user is not None,
        "user": user
    }


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """Logout and invalidate session"""
    db = get_db()
    service = AuthService(db)
    
    # Get token from various sources
    token = None
    if credentials:
        token = credentials.credentials
    if not token:
        token = request.cookies.get("session_token")
    if not token:
        token = request.query_params.get("token")
    
    if token:
        await service.logout(token)
    
    # Clear cookie
    response.delete_cookie(key="session_token", path="/")
    
    return {"success": True, "message": "Déconnexion réussie"}


# ==========================================
# Auto-Login & Device Trust
# ==========================================

@router.get("/auto-login")
async def auto_login(request: Request, response: Response):
    """Attempt auto-login from trusted device"""
    db = get_db()
    service = AuthService(db)
    
    ip_address = get_client_ip(request)
    success, token_response, error = await service.auto_login(ip_address)
    
    if not success:
        return {"success": False, "auto_login": False, "message": error}
    
    # Set cookie
    response.set_cookie(
        key="session_token",
        value=token_response.token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=60 * 60 * 24 * 7,
        path="/"
    )
    
    return {
        "success": True,
        "auto_login": True,
        "token": token_response.token,
        "user": token_response.user
    }


@router.get("/ip-info")
async def ip_info(request: Request):
    """Get information about client IP"""
    db = get_db()
    service = AuthService(db)
    
    ip_address = get_client_ip(request)
    return await service.get_ip_info(ip_address)


# ==========================================
# Password Reset (Full Implementation)
# ==========================================

@router.post("/forgot-password")
async def forgot_password(reset_data: PasswordReset):
    """
    Request password reset email.
    REMINDER: Always returns success to prevent email enumeration attacks.
    """
    from .email_service import EmailService
    
    db = get_db()
    auth_service = AuthService(db)
    email_service = EmailService(db)
    
    # Check if user exists
    user = await auth_service.get_user_by_email(reset_data.email)
    
    if user:
        # Send reset email
        success, message = await email_service.send_password_reset_email(
            user_id=user["user_id"],
            email=user["email"],
            user_name=user.get("name", "Utilisateur")
        )
        logger.info(f"Password reset requested for {reset_data.email}: {message}")
    else:
        logger.info(f"Password reset requested for non-existent email: {reset_data.email}")
    
    # Always return success to prevent email enumeration
    return {
        "success": True,
        "message": "Si un compte existe avec cet email, un lien de réinitialisation a été envoyé"
    }


@router.post("/reset-password")
async def reset_password(token: str, new_password: str):
    """
    Reset password using token from email.
    """
    from .email_service import EmailService
    
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="Le mot de passe doit contenir au moins 6 caractères")
    
    db = get_db()
    auth_service = AuthService(db)
    email_service = EmailService(db)
    
    # Verify token
    token_data = await email_service.verify_reset_token(token)
    if not token_data:
        raise HTTPException(status_code=400, detail="Lien invalide ou expiré")
    
    # Get user
    user = await auth_service.get_user_by_id(token_data["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Update password
    new_hash = auth_service.hash_password(new_password)
    await auth_service.users_collection.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"password_hash": new_hash, "updated_at": datetime.now(timezone.utc)}}
    )
    
    # Mark token as used
    await email_service.mark_token_used(token)
    
    logger.info(f"Password reset completed for user {user['user_id']}")
    
    return {
        "success": True,
        "message": "Mot de passe réinitialisé avec succès. Vous pouvez maintenant vous connecter."
    }


@router.get("/verify-reset-token")
async def verify_reset_token(token: str):
    """Verify if a reset token is valid"""
    from .email_service import EmailService
    
    db = get_db()
    email_service = EmailService(db)
    
    token_data = await email_service.verify_reset_token(token)
    
    return {
        "valid": token_data is not None,
        "email": token_data.get("email") if token_data else None
    }


# ==========================================
# Health Check
# ==========================================

@router.get("/")
async def auth_info():
    """Get auth engine info"""
    return {
        "module": "auth_engine",
        "version": "1.0.0",
        "phase": "P4",
        "description": "Hybrid Authentication (JWT + Google OAuth)",
        "features": [
            "Email/password registration and login",
            "Google OAuth via Emergent Auth",
            "JWT access tokens (24h expiry)",
            "Trusted device auto-login",
            "Session management"
        ],
        "endpoints": {
            "POST /register": "Create account with email/password",
            "POST /login": "Login with email/password",
            "POST /google/callback": "Google OAuth callback",
            "GET /me": "Get current user",
            "GET /verify": "Verify token",
            "POST /logout": "Logout",
            "GET /auto-login": "Auto-login from trusted device",
            "GET /ip-info": "Get IP trust info"
        }
    }
