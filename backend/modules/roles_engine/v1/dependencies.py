"""
Roles Engine - Authentication Dependencies
Provides role-based authentication decorators and dependencies
"""
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
import jwt
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from .models import UserRole, UserWithRole, ROLE_PERMISSIONS

logger = logging.getLogger(__name__)

# JWT Configuration - Secure: No default values, fail fast if not configured
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise RuntimeError("CRITICAL: JWT_SECRET_KEY environment variable is not set. Application cannot start.")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")

# Optional bearer - doesn't require auth header
security = HTTPBearer(auto_error=False)

# Database connection
_db = None

def get_db() -> AsyncIOMotorDatabase:
    """Get database connection using environment variables only."""
    global _db
    if _db is None:
        MONGO_URL = os.environ.get('MONGO_URL')
        DB_NAME = os.environ.get('DB_NAME')
        if not MONGO_URL:
            raise RuntimeError("CRITICAL: MONGO_URL environment variable is not set.")
        if not DB_NAME:
            raise RuntimeError("CRITICAL: DB_NAME environment variable is not set.")
        client = AsyncIOMotorClient(MONGO_URL)
        _db = client[DB_NAME]
    return _db


def extract_token_from_request(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = None
) -> Optional[str]:
    """Extract token from request (header, cookie, or query param)"""
    # 1. Try Authorization header
    if credentials and credentials.credentials:
        return credentials.credentials
    
    # 2. Try cookie
    token = request.cookies.get("session_token")
    if token:
        return token
    
    # 3. Try query param (legacy support)
    token = request.query_params.get("token")
    if token:
        return token
    
    return None


def decode_token(token: str) -> Optional[dict]:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def has_permission(role: UserRole, permission: str) -> bool:
    """Check if a role has a specific permission"""
    role_perms = ROLE_PERMISSIONS.get(role.value, [])
    
    # Admin has all permissions (wildcard)
    if "*" in role_perms:
        return True
    
    return permission in role_perms


async def get_current_user_with_role(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> UserWithRole:
    """
    Get current user with role information.
    Raises 401 if not authenticated.
    """
    token = extract_token_from_request(request, credentials)
    
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Authentification requise"
        )
    
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Token invalide ou expiré"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Token invalide"
        )
    
    # Get user from database with role
    db = get_db()
    user = await db['users'].find_one(
        {"user_id": user_id},
        {"_id": 0}
    )
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Utilisateur non trouvé"
        )
    
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=403,
            detail="Compte désactivé"
        )
    
    # Get role (default to hunter if not set)
    role_str = user.get("role", UserRole.HUNTER.value)
    try:
        role = UserRole(role_str)
    except ValueError:
        role = UserRole.HUNTER
    
    # Get permissions for role
    permissions = ROLE_PERMISSIONS.get(role.value, [])
    
    return UserWithRole(
        user_id=user.get("user_id"),
        name=user.get("name", ""),
        email=user.get("email", ""),
        phone=user.get("phone"),
        picture=user.get("picture"),
        auth_provider=user.get("auth_provider", "local"),
        role=role,
        permissions=permissions,
        created_at=user.get("created_at"),
        is_active=user.get("is_active", True)
    )


async def get_optional_user_with_role(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[UserWithRole]:
    """
    Get current user with role if authenticated, None otherwise.
    Use for optional authentication.
    """
    try:
        return await get_current_user_with_role(request, credentials)
    except HTTPException:
        return None


# ============================================
# ROLE-BASED DEPENDENCIES
# ============================================

async def require_admin(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> UserWithRole:
    """
    Require admin role.
    Raises 403 if user is not an admin.
    """
    user = await get_current_user_with_role(request, credentials)
    
    if user.role != UserRole.ADMIN:
        logger.warning(f"Access denied: User {user.user_id} ({user.role.value}) attempted admin action")
        raise HTTPException(
            status_code=403,
            detail="Accès réservé aux administrateurs"
        )
    
    return user


async def require_guide_or_admin(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> UserWithRole:
    """
    Require guide or admin role.
    Raises 403 if user is not a guide or admin.
    """
    user = await get_current_user_with_role(request, credentials)
    
    if user.role not in [UserRole.GUIDE, UserRole.ADMIN]:
        logger.warning(f"Access denied: User {user.user_id} ({user.role.value}) attempted guide/admin action")
        raise HTTPException(
            status_code=403,
            detail="Accès réservé aux guides et administrateurs"
        )
    
    return user


async def require_business_or_admin(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> UserWithRole:
    """
    Require business or admin role.
    Raises 403 if user is not a business user or admin.
    """
    user = await get_current_user_with_role(request, credentials)
    
    if user.role not in [UserRole.BUSINESS, UserRole.ADMIN]:
        logger.warning(f"Access denied: User {user.user_id} ({user.role.value}) attempted business action")
        raise HTTPException(
            status_code=403,
            detail="Accès réservé aux comptes Business et administrateurs"
        )
    
    return user


async def require_elevated_role(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> UserWithRole:
    """Require any elevated role (guide, business, or admin)"""
    user = await get_current_user_with_role(request, credentials)
    
    if user.role not in [UserRole.GUIDE, UserRole.BUSINESS, UserRole.ADMIN]:
        logger.warning(f"Access denied: User {user.user_id} ({user.role.value}) attempted elevated action")
        raise HTTPException(
            status_code=403,
            detail="Accès réservé aux comptes professionnels"
        )
    
    return user


def require_permission(permission: str):
    """
    Factory function to create a dependency that requires a specific permission.
    
    Usage:
        @router.get("/sensitive")
        async def sensitive_endpoint(user: UserWithRole = Depends(require_permission("view_sensitive_data"))):
            pass
    """
    async def dependency(
        request: Request,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ) -> UserWithRole:
        user = await get_current_user_with_role(request, credentials)
        
        if not has_permission(user.role, permission):
            logger.warning(f"Permission denied: User {user.user_id} lacks '{permission}'")
            raise HTTPException(
                status_code=403,
                detail=f"Permission requise: {permission}"
            )
        
        return user
    
    return dependency


def require_any_permission(permissions: List[str]):
    """
    Factory function to create a dependency that requires any of the specified permissions.
    """
    async def dependency(
        request: Request,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ) -> UserWithRole:
        user = await get_current_user_with_role(request, credentials)
        
        for perm in permissions:
            if has_permission(user.role, perm):
                return user
        
        logger.warning(f"Permission denied: User {user.user_id} lacks any of {permissions}")
        raise HTTPException(
            status_code=403,
            detail=f"Une des permissions requises: {', '.join(permissions)}"
        )
    
    return dependency


def require_all_permissions(permissions: List[str]):
    """
    Factory function to create a dependency that requires all of the specified permissions.
    """
    async def dependency(
        request: Request,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ) -> UserWithRole:
        user = await get_current_user_with_role(request, credentials)
        
        missing = [p for p in permissions if not has_permission(user.role, p)]
        
        if missing:
            logger.warning(f"Permission denied: User {user.user_id} lacks {missing}")
            raise HTTPException(
                status_code=403,
                detail=f"Permissions manquantes: {', '.join(missing)}"
            )
        
        return user
    
    return dependency
