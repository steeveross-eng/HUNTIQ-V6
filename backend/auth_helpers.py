"""
Authentication Helpers for BIONIC HUNT/Chasse V3
Centralized authentication utilities for all modules

Usage in routers:
    from auth_helpers import get_current_user_id, get_optional_user_id

    @router.get("/my-data")
    async def get_data(user_id: str = Depends(get_current_user_id)):
        # user_id is required - returns 401 if not authenticated
        pass

    @router.get("/public-data")
    async def get_public(user_id: Optional[str] = Depends(get_optional_user_id)):
        # user_id is optional - returns None if not authenticated
        pass
"""
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import jwt
import os

# JWT Configuration
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "huntiq_default_secret_change_me")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")

# Optional bearer - doesn't require auth header
security = HTTPBearer(auto_error=False)


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


async def get_optional_user_id(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """
    Get user_id from token if authenticated, None otherwise.
    Use this for optional authentication.
    """
    token = extract_token_from_request(request, credentials)
    if not token:
        return None
    
    payload = decode_token(token)
    if not payload:
        return None
    
    return payload.get("sub")


async def get_current_user_id(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> str:
    """
    Get user_id from token. Raises 401 if not authenticated.
    Use this for required authentication.
    """
    user_id = await get_optional_user_id(request, credentials)
    
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Authentification requise"
        )
    
    return user_id


# Legacy support - default user for unauthenticated requests
DEFAULT_USER_ID = "default_user"


async def get_user_id_with_fallback(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> str:
    """
    Get user_id from token, or return DEFAULT_USER_ID if not authenticated.
    Use this during migration period to maintain backward compatibility.
    """
    user_id = await get_optional_user_id(request, credentials)
    return user_id or DEFAULT_USER_ID
