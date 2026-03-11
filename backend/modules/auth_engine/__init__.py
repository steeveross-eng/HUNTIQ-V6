"""
Auth Engine Module
Hybrid Authentication: JWT + Google OAuth
"""

from .v1.router import router, get_current_user, require_auth
from .v1.service import AuthService

__all__ = ['router', 'get_current_user', 'require_auth', 'AuthService']
__version__ = '1.0.0'
