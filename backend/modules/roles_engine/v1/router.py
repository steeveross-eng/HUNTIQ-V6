"""
Roles Engine - API Router
Endpoints for role management (admin only)
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from .models import (
    UserRole, UserWithRole, RoleUpdate, RoleInfo,
    ROLE_METADATA, PermissionCheck
)
from .service import RolesService

# Import role-based auth dependencies
from .dependencies import require_admin, get_current_user_with_role

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/roles",
    tags=["Roles Engine"],
    responses={404: {"description": "Not found"}}
)

# Database dependency
_db = None

def get_db() -> AsyncIOMotorDatabase:
    global _db
    if _db is None:
        MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        DB_NAME = os.environ.get('DB_NAME', 'hunttrack')
        client = AsyncIOMotorClient(MONGO_URL)
        _db = client[DB_NAME]
    return _db


def get_service() -> RolesService:
    return RolesService(get_db())


# ============================================
# PUBLIC ENDPOINTS
# ============================================

@router.get("/", summary="Module Info")
async def get_module_info():
    """Get roles engine module information"""
    return {
        "module": "roles_engine",
        "version": "1.0.0",
        "description": "Gestion des rôles et permissions utilisateurs",
        "roles": [
            {"value": r.value, "label": ROLE_METADATA[r.value].label}
            for r in UserRole
        ],
        "endpoints": [
            "GET /me - Get current user role and permissions",
            "GET /info - Get all roles information",
            "GET /check/{permission} - Check if current user has permission",
            "PUT /update (admin) - Update user role",
            "GET /users (admin) - List users by role",
            "GET /statistics (admin) - Role distribution stats",
            "GET /logs (admin) - Role change history"
        ]
    }


@router.get("/info", summary="Liste des rôles", response_model=List[RoleInfo])
async def get_roles_info():
    """Get information about all available roles"""
    service = get_service()
    return service.get_all_roles()


@router.get("/me", summary="Mon rôle", response_model=UserWithRole)
async def get_my_role(
    user: UserWithRole = Depends(get_current_user_with_role)
):
    """Get current user's role and permissions"""
    return user


@router.get("/check/{permission}", summary="Vérifier permission")
async def check_permission(
    permission: str,
    user: UserWithRole = Depends(get_current_user_with_role)
):
    """Check if current user has a specific permission"""
    service = get_service()
    has_perm = service.has_permission(user.role, permission)
    
    return PermissionCheck(
        has_permission=has_perm,
        permission=permission,
        user_role=user.role,
        message="Permission accordée" if has_perm else "Permission refusée"
    )


# ============================================
# ADMIN ENDPOINTS
# ============================================

@router.put("/update", summary="Modifier rôle (admin)")
async def update_user_role(
    role_update: RoleUpdate,
    admin: UserWithRole = Depends(require_admin),
    service: RolesService = Depends(get_service)
):
    """Update a user's role (admin only)"""
    # Prevent self-demotion from admin
    if role_update.user_id == admin.user_id and role_update.new_role != UserRole.ADMIN:
        raise HTTPException(
            status_code=400,
            detail="Vous ne pouvez pas rétrograder votre propre compte admin"
        )
    
    success, message = await service.set_user_role(
        user_id=role_update.user_id,
        new_role=role_update.new_role,
        changed_by=admin.user_id,
        reason=role_update.reason
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {
        "success": True,
        "message": message,
        "user_id": role_update.user_id,
        "new_role": role_update.new_role.value
    }


@router.post("/promote/guide/{user_id}", summary="Promouvoir en Guide (admin)")
async def promote_to_guide(
    user_id: str,
    admin: UserWithRole = Depends(require_admin),
    service: RolesService = Depends(get_service)
):
    """Promote a user to guide role (terrain/group management)"""
    success, message = await service.promote_to_guide(user_id, admin.user_id)
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"success": True, "message": message}


@router.post("/promote/business/{user_id}", summary="Promouvoir en Business (admin)")
async def promote_to_business(
    user_id: str,
    admin: UserWithRole = Depends(require_admin),
    service: RolesService = Depends(get_service)
):
    """Promote a user to business role (marketplace/commercial access)"""
    success, message = await service.promote_to_business(user_id, admin.user_id)
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"success": True, "message": message}


@router.post("/promote/admin/{user_id}", summary="Promouvoir en Admin (admin)")
async def promote_to_admin(
    user_id: str,
    admin: UserWithRole = Depends(require_admin),
    service: RolesService = Depends(get_service)
):
    """Promote a user to admin role"""
    success, message = await service.promote_to_admin(user_id, admin.user_id)
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"success": True, "message": message}


@router.post("/demote/{user_id}", summary="Rétrograder (admin)")
async def demote_user(
    user_id: str,
    reason: Optional[str] = Query(None),
    admin: UserWithRole = Depends(require_admin),
    service: RolesService = Depends(get_service)
):
    """Demote a user to hunter role"""
    if user_id == admin.user_id:
        raise HTTPException(
            status_code=400,
            detail="Vous ne pouvez pas rétrograder votre propre compte"
        )
    
    success, message = await service.demote_to_hunter(user_id, admin.user_id, reason)
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"success": True, "message": message}


@router.get("/users", summary="Utilisateurs par rôle (admin)")
async def get_users_by_role(
    role: UserRole = Query(UserRole.HUNTER),
    limit: int = Query(50, ge=1, le=200),
    admin: UserWithRole = Depends(require_admin),
    service: RolesService = Depends(get_service)
):
    """Get all users with a specific role"""
    users = await service.get_users_by_role(role, limit)
    
    return {
        "success": True,
        "role": role.value,
        "count": len(users),
        "users": [u.model_dump() for u in users]
    }


@router.get("/statistics", summary="Statistiques des rôles (admin)")
async def get_role_statistics(
    admin: UserWithRole = Depends(require_admin),
    service: RolesService = Depends(get_service)
):
    """Get role distribution statistics"""
    stats = await service.get_role_statistics()
    
    return {
        "success": True,
        "statistics": stats,
        "breakdown": [
            {
                "role": role.value,
                "label": ROLE_METADATA[role.value].label,
                "count": stats.get(role.value, 0),
                "percentage": round(stats.get(role.value, 0) / max(stats["total"], 1) * 100, 1)
            }
            for role in UserRole
        ]
    }


@router.get("/logs", summary="Historique des changements (admin)")
async def get_role_change_logs(
    user_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    admin: UserWithRole = Depends(require_admin),
    service: RolesService = Depends(get_service)
):
    """Get role change history"""
    if user_id:
        logs = await service.get_role_change_history(user_id, limit)
        return {
            "success": True,
            "user_id": user_id,
            "logs": [log.model_dump() for log in logs]
        }
    else:
        logs = await service.get_all_role_changes(limit)
        return {
            "success": True,
            "logs": logs
        }


@router.post("/migrate", summary="Migrer utilisateurs (admin)")
async def migrate_users_to_default_role(
    admin: UserWithRole = Depends(require_admin),
    service: RolesService = Depends(get_service)
):
    """Migrate users without role to default hunter role"""
    count = await service.migrate_users_default_role()
    
    return {
        "success": True,
        "message": f"{count} utilisateurs migrés vers le rôle Chasseur",
        "migrated_count": count
    }


logger.info("Roles Engine module loaded")
