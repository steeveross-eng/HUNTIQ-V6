"""
Roles Engine - Service Layer
Business logic for role management and permission checking
"""
import logging
from datetime import datetime, timezone
from typing import Optional, List, Tuple
from motor.motor_asyncio import AsyncIOMotorDatabase

from .models import (
    UserRole, UserWithRole, RoleChangeLog,
    ROLE_PERMISSIONS, ROLE_METADATA, RoleInfo
)

logger = logging.getLogger(__name__)


class RolesService:
    """Service for managing user roles and permissions"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.users_collection = db['users']
        self.role_logs_collection = db['role_change_logs']
    
    # ============================================
    # PERMISSION CHECKING
    # ============================================
    
    def has_permission(self, role: UserRole, permission: str) -> bool:
        """Check if a role has a specific permission"""
        role_perms = ROLE_PERMISSIONS.get(role.value, [])
        
        # Admin has all permissions (wildcard)
        if "*" in role_perms:
            return True
        
        return permission in role_perms
    
    def get_permissions_for_role(self, role: UserRole) -> List[str]:
        """Get all permissions for a role"""
        return ROLE_PERMISSIONS.get(role.value, [])
    
    def is_elevated_role(self, role: UserRole) -> bool:
        """Check if role is elevated (guide or admin)"""
        return role in [UserRole.GUIDE, UserRole.ADMIN]
    
    def can_manage_role(self, actor_role: UserRole, target_role: UserRole) -> bool:
        """Check if actor can manage target role"""
        # Only admins can manage roles
        if actor_role != UserRole.ADMIN:
            return False
        
        # Admins can manage all roles
        return True
    
    # ============================================
    # USER ROLE MANAGEMENT
    # ============================================
    
    async def get_user_role(self, user_id: str) -> Optional[UserRole]:
        """Get the role of a user"""
        user = await self.users_collection.find_one(
            {"user_id": user_id},
            {"role": 1}
        )
        
        if not user:
            return None
        
        role_str = user.get("role", UserRole.HUNTER.value)
        try:
            return UserRole(role_str)
        except ValueError:
            return UserRole.HUNTER
    
    async def get_user_with_role(self, user_id: str) -> Optional[UserWithRole]:
        """Get user with full role information"""
        user = await self.users_collection.find_one(
            {"user_id": user_id},
            {"_id": 0}
        )
        
        if not user:
            return None
        
        role_str = user.get("role", UserRole.HUNTER.value)
        try:
            role = UserRole(role_str)
        except ValueError:
            role = UserRole.HUNTER
        
        permissions = self.get_permissions_for_role(role)
        
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
    
    async def set_user_role(
        self, 
        user_id: str, 
        new_role: UserRole,
        changed_by: str,
        reason: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Set a user's role"""
        # Get current role
        current_role = await self.get_user_role(user_id)
        
        if current_role is None:
            return False, "Utilisateur non trouvé"
        
        if current_role == new_role:
            return True, "Le rôle est déjà défini"
        
        now = datetime.now(timezone.utc)
        
        # Update user role
        result = await self.users_collection.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "role": new_role.value,
                    "role_updated_at": now,
                    "role_updated_by": changed_by
                }
            }
        )
        
        if result.modified_count == 0:
            return False, "Échec de la mise à jour du rôle"
        
        # Log the change
        log_entry = {
            "user_id": user_id,
            "old_role": current_role.value,
            "new_role": new_role.value,
            "changed_by": changed_by,
            "changed_at": now,
            "reason": reason
        }
        await self.role_logs_collection.insert_one(log_entry)
        
        role_label = ROLE_METADATA[new_role.value].label
        logger.info(f"Role changed for user {user_id}: {current_role.value} -> {new_role.value} by {changed_by}")
        
        return True, f"Rôle mis à jour: {role_label}"
    
    async def promote_to_guide(self, user_id: str, admin_id: str) -> Tuple[bool, str]:
        """Promote a hunter to guide"""
        return await self.set_user_role(
            user_id, 
            UserRole.GUIDE, 
            admin_id,
            "Promotion au rôle Guide"
        )
    
    async def promote_to_business(self, user_id: str, admin_id: str) -> Tuple[bool, str]:
        """Promote a user to business role"""
        return await self.set_user_role(
            user_id, 
            UserRole.BUSINESS, 
            admin_id,
            "Promotion au rôle Business"
        )
    
    async def promote_to_admin(self, user_id: str, admin_id: str) -> Tuple[bool, str]:
        """Promote a user to admin"""
        return await self.set_user_role(
            user_id, 
            UserRole.ADMIN, 
            admin_id,
            "Promotion au rôle Administrateur"
        )
    
    async def demote_to_hunter(self, user_id: str, admin_id: str, reason: str = None) -> Tuple[bool, str]:
        """Demote a user to hunter"""
        return await self.set_user_role(
            user_id, 
            UserRole.HUNTER, 
            admin_id,
            reason or "Rétrogradation au rôle Chasseur"
        )
    
    # ============================================
    # BULK OPERATIONS
    # ============================================
    
    async def get_users_by_role(self, role: UserRole, limit: int = 100) -> List[UserWithRole]:
        """Get all users with a specific role"""
        cursor = self.users_collection.find(
            {"role": role.value},
            {"_id": 0}
        ).limit(limit)
        
        users = await cursor.to_list(length=limit)
        
        permissions = self.get_permissions_for_role(role)
        
        return [
            UserWithRole(
                user_id=u.get("user_id"),
                name=u.get("name", ""),
                email=u.get("email", ""),
                phone=u.get("phone"),
                picture=u.get("picture"),
                auth_provider=u.get("auth_provider", "local"),
                role=role,
                permissions=permissions,
                created_at=u.get("created_at"),
                is_active=u.get("is_active", True)
            )
            for u in users
        ]
    
    async def get_role_statistics(self) -> dict:
        """Get statistics about role distribution"""
        pipeline = [
            {
                "$group": {
                    "_id": {"$ifNull": ["$role", "hunter"]},
                    "count": {"$sum": 1}
                }
            }
        ]
        
        results = await self.users_collection.aggregate(pipeline).to_list(10)
        
        stats = {
            "hunter": 0,
            "guide": 0,
            "business": 0,
            "admin": 0,
            "total": 0
        }
        
        for r in results:
            role = r["_id"]
            count = r["count"]
            if role in stats:
                stats[role] = count
            stats["total"] += count
        
        return stats
    
    async def migrate_users_default_role(self) -> int:
        """Migrate existing users without role to hunter"""
        result = await self.users_collection.update_many(
            {"role": {"$exists": False}},
            {"$set": {"role": UserRole.HUNTER.value}}
        )
        
        if result.modified_count > 0:
            logger.info(f"Migrated {result.modified_count} users to default hunter role")
        
        return result.modified_count
    
    # ============================================
    # ROLE CHANGE LOGS
    # ============================================
    
    async def get_role_change_history(self, user_id: str, limit: int = 20) -> List[RoleChangeLog]:
        """Get role change history for a user"""
        cursor = self.role_logs_collection.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("changed_at", -1).limit(limit)
        
        logs = await cursor.to_list(length=limit)
        
        return [
            RoleChangeLog(
                user_id=log["user_id"],
                old_role=UserRole(log["old_role"]),
                new_role=UserRole(log["new_role"]),
                changed_by=log["changed_by"],
                changed_at=log["changed_at"],
                reason=log.get("reason")
            )
            for log in logs
        ]
    
    async def get_all_role_changes(self, limit: int = 50) -> List[dict]:
        """Get all recent role changes (for admin dashboard)"""
        pipeline = [
            {"$sort": {"changed_at": -1}},
            {"$limit": limit},
            {
                "$lookup": {
                    "from": "users",
                    "localField": "user_id",
                    "foreignField": "user_id",
                    "as": "user_info"
                }
            },
            {
                "$unwind": {
                    "path": "$user_info",
                    "preserveNullAndEmptyArrays": True
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "user_id": 1,
                    "user_name": "$user_info.name",
                    "user_email": "$user_info.email",
                    "old_role": 1,
                    "new_role": 1,
                    "changed_by": 1,
                    "changed_at": 1,
                    "reason": 1
                }
            }
        ]
        
        return await self.role_logs_collection.aggregate(pipeline).to_list(limit)
    
    # ============================================
    # UTILITY
    # ============================================
    
    def get_role_info(self, role: UserRole) -> RoleInfo:
        """Get metadata about a role"""
        return ROLE_METADATA.get(role.value, ROLE_METADATA[UserRole.HUNTER.value])
    
    def get_all_roles(self) -> List[RoleInfo]:
        """Get all available roles with metadata"""
        return list(ROLE_METADATA.values())
