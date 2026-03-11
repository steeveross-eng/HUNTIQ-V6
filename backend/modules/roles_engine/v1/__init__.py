"""Roles Engine v1"""
from .router import router
from .models import UserRole, UserWithRole, ROLE_PERMISSIONS, ROLE_METADATA
from .service import RolesService
from .dependencies import (
    require_admin,
    require_guide_or_admin,
    require_business_or_admin,
    require_elevated_role,
    require_permission,
    require_any_permission,
    require_all_permissions,
    get_current_user_with_role,
    get_optional_user_with_role,
    has_permission
)

__all__ = [
    'router',
    'UserRole',
    'UserWithRole',
    'ROLE_PERMISSIONS',
    'ROLE_METADATA',
    'RolesService',
    'require_admin',
    'require_guide_or_admin',
    'require_business_or_admin',
    'require_elevated_role',
    'require_permission',
    'require_any_permission',
    'require_all_permissions',
    'get_current_user_with_role',
    'get_optional_user_with_role',
    'has_permission'
]
