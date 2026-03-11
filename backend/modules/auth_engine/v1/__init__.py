"""
Auth Engine v1
Hybrid Authentication: JWT (email/password) + Google OAuth
"""

from .router import router, get_current_user, require_auth
from .service import AuthService
from .models import (
    UserCreate, UserLogin, UserResponse, TokenResponse,
    GoogleAuthCallback, AuthProvider
)

__all__ = [
    'router',
    'get_current_user',
    'require_auth',
    'AuthService',
    'UserCreate',
    'UserLogin',
    'UserResponse',
    'TokenResponse',
    'GoogleAuthCallback',
    'AuthProvider'
]
