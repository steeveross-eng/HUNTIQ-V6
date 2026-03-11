"""User Engine Router - MÉTIER

FastAPI router for user management endpoints.

Version: 1.0.0
API Prefix: /api/v1/user
"""

from fastapi import APIRouter, HTTPException, Header, Query
from typing import Optional
from .service import UserService
from .models import (
    UserCreate, UserUpdate,
    UserLogin, UserRole, UserStatus
)

router = APIRouter(prefix="/api/v1/user", tags=["User Engine"])

# Initialize service
_service = UserService()


@router.get("/")
async def user_engine_info():
    """Get user engine information"""
    total_users = await _service.count_users()
    
    return {
        "module": "user_engine",
        "version": "1.0.0",
        "description": "User management and authentication",
        "total_users": total_users,
        "features": [
            "User registration",
            "Authentication",
            "Profile management",
            "Preferences",
            "Activity tracking",
            "Role management"
        ],
        "roles": [role.value for role in UserRole],
        "statuses": [status.value for status in UserStatus]
    }


@router.post("/register")
async def register_user(user_data: UserCreate):
    """
    Register a new user account.
    
    Creates user with default profile and preferences.
    """
    try:
        user = await _service.create_user(user_data)
        return {
            "success": True,
            "message": "User registered successfully",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "role": user.role.value
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@router.post("/login")
async def login_user(credentials: UserLogin):
    """
    Authenticate user and create session.
    
    Returns user data and session token.
    """
    result = await _service.authenticate(credentials.email, credentials.password)
    
    if not result:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    return {
        "success": True,
        "message": "Login successful",
        "user": result["user"],
        "token": result["token"],
        "expires_at": result["expires_at"]
    }


@router.post("/logout")
async def logout_user(authorization: str = Header(None)):
    """Logout and invalidate session"""
    if not authorization:
        raise HTTPException(status_code=401, detail="No authorization token")
    
    token = authorization.replace("Bearer ", "")
    success = await _service.logout(token)
    
    return {
        "success": success,
        "message": "Logged out successfully" if success else "Session not found"
    }


@router.get("/me")
async def get_current_user(authorization: str = Header(None)):
    """Get current authenticated user"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    user = await _service.validate_session(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    return {
        "success": True,
        "user": user.model_dump()
    }


@router.put("/me")
async def update_current_user(
    update_data: UserUpdate,
    authorization: str = Header(None)
):
    """Update current user's information"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    user = await _service.validate_session(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    updated_user = await _service.update_user(user.id, update_data)
    
    return {
        "success": True,
        "user": updated_user.model_dump() if updated_user else None
    }


@router.get("/profile/{user_id}")
async def get_user_profile(user_id: str):
    """Get user's hunting profile"""
    profile = await _service.get_profile(user_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return {
        "success": True,
        "profile": profile.model_dump()
    }


@router.put("/profile")
async def update_user_profile(
    profile_data: dict,
    authorization: str = Header(None)
):
    """Update current user's hunting profile"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    user = await _service.validate_session(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    profile = await _service.update_profile(user.id, profile_data)
    
    return {
        "success": True,
        "profile": profile.model_dump() if profile else None
    }


@router.get("/preferences")
async def get_user_preferences(authorization: str = Header(None)):
    """Get current user's preferences"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    user = await _service.validate_session(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    prefs = await _service.get_preferences(user.id)
    
    return {
        "success": True,
        "preferences": prefs.model_dump()
    }


@router.put("/preferences")
async def update_user_preferences(
    prefs_data: dict,
    authorization: str = Header(None)
):
    """Update current user's preferences"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    user = await _service.validate_session(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    prefs = await _service.update_preferences(user.id, prefs_data)
    
    return {
        "success": True,
        "preferences": prefs.model_dump()
    }


@router.get("/activity")
async def get_user_activity(
    limit: int = Query(50, ge=1, le=200),
    authorization: str = Header(None)
):
    """Get current user's activity history"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    user = await _service.validate_session(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    activity = await _service.get_activity_history(user.id, limit)
    
    return {
        "success": True,
        "activity": activity
    }


@router.get("/{user_id}")
async def get_user_by_id(user_id: str):
    """Get public user information by ID"""
    user = await _service.get_user(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Return only public information
    return {
        "success": True,
        "user": {
            "id": user.id,
            "name": user.name,
            "role": user.role.value,
            "created_at": user.created_at.isoformat()
        }
    }


# Admin endpoints
@router.get("/admin/list")
async def admin_list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    role: Optional[str] = None,
    authorization: str = Header(None)
):
    """List all users (admin only)"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    admin = await _service.validate_session(token)
    
    if not admin or admin.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    users = await _service.list_users(skip, limit, role)
    total = await _service.count_users(role)
    
    return {
        "success": True,
        "total": total,
        "skip": skip,
        "limit": limit,
        "users": [u.model_dump() for u in users]
    }


@router.put("/admin/{user_id}/role")
async def admin_update_role(
    user_id: str,
    new_role: str,
    authorization: str = Header(None)
):
    """Update user role (admin only)"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    admin = await _service.validate_session(token)
    
    if not admin or admin.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Super admin access required")
    
    try:
        role = UserRole(new_role)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid role: {new_role}")
    
    user = await _service.update_role(user_id, role)
    
    return {
        "success": True,
        "user": user.model_dump() if user else None
    }


@router.put("/admin/{user_id}/suspend")
async def admin_suspend_user(
    user_id: str,
    reason: str = "",
    authorization: str = Header(None)
):
    """Suspend user account (admin only)"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    admin = await _service.validate_session(token)
    
    if not admin or admin.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user = await _service.suspend_user(user_id, reason)
    
    return {
        "success": True,
        "message": "User suspended",
        "user": user.model_dump() if user else None
    }


@router.put("/admin/{user_id}/reactivate")
async def admin_reactivate_user(
    user_id: str,
    authorization: str = Header(None)
):
    """Reactivate suspended user (admin only)"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    admin = await _service.validate_session(token)
    
    if not admin or admin.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user = await _service.reactivate_user(user_id)
    
    return {
        "success": True,
        "message": "User reactivated",
        "user": user.model_dump() if user else None
    }


@router.get("/roles")
async def list_roles():
    """List all available roles"""
    return {
        "success": True,
        "roles": [
            {"id": role.value, "name": role.name, "description": _get_role_description(role)}
            for role in UserRole
        ]
    }


def _get_role_description(role: UserRole) -> str:
    """Get role description"""
    descriptions = {
        UserRole.GUEST: "Visiteur non inscrit",
        UserRole.USER: "Utilisateur standard",
        UserRole.PREMIUM: "Utilisateur premium avec accès étendu",
        UserRole.PARTNER: "Partenaire privilégié (boutique, pourvoirie, guide)",
        UserRole.ADMIN: "Administrateur avec accès de gestion",
        UserRole.SUPER_ADMIN: "Super administrateur avec accès complet"
    }
    return descriptions.get(role, "")
