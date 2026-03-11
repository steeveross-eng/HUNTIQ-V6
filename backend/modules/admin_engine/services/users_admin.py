"""
Users Admin Service - V5-ULTIME
===============================

Service d'administration des utilisateurs.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class UsersAdminService:
    """Service isolé pour l'administration des utilisateurs"""
    
    @staticmethod
    async def get_users(db, limit: int, role: Optional[str], tier: Optional[str]) -> dict:
        """Liste tous les utilisateurs"""
        query = {}
        if role:
            query["role"] = role
        
        users = await db.users.find(
            query, {"_id": 0, "password": 0, "hashed_password": 0}
        ).sort("created_at", -1).limit(limit).to_list(length=limit)
        
        # Enrichir avec les subscriptions si tier filter
        if tier:
            user_ids = [u.get("user_id") or u.get("email") for u in users]
            subs = await db.subscriptions.find(
                {"user_id": {"$in": user_ids}, "tier": tier},
                {"_id": 0}
            ).to_list(length=limit)
            
            sub_user_ids = {s["user_id"] for s in subs}
            users = [u for u in users if (u.get("user_id") or u.get("email")) in sub_user_ids]
        
        total = await db.users.count_documents(query)
        
        return {
            "success": True,
            "total": total,
            "users": users
        }
    
    @staticmethod
    async def get_user_detail(db, user_id: str) -> dict:
        """Détail complet d'un utilisateur"""
        # User info
        user = await db.users.find_one(
            {"$or": [{"user_id": user_id}, {"email": user_id}]},
            {"_id": 0, "password": 0, "hashed_password": 0}
        )
        
        if not user:
            return {"success": False, "error": "User not found"}
        
        # Subscription
        sub = await db.subscriptions.find_one(
            {"user_id": user_id}, {"_id": 0}
        )
        
        # Onboarding
        onboarding = await db.onboarding_status.find_one(
            {"user_id": user_id}, {"_id": 0}
        )
        
        # Transactions
        transactions = await db.payment_transactions.find(
            {"user_id": user_id}, {"_id": 0}
        ).sort("created_at", -1).limit(10).to_list(length=10)
        
        # Plans
        plans = await db.master_plans.find(
            {"user_id": user_id}, {"_id": 0}
        ).sort("created_at", -1).limit(5).to_list(length=5)
        
        return {
            "success": True,
            "user": user,
            "subscription": sub,
            "onboarding": onboarding,
            "recent_transactions": transactions,
            "plans": plans
        }
    
    @staticmethod
    async def update_role(db, user_id: str, role: str) -> dict:
        """Modifier le rôle d'un utilisateur"""
        valid_roles = ["hunter", "guide", "business", "admin"]
        if role not in valid_roles:
            return {"success": False, "error": f"Invalid role. Must be one of: {valid_roles}"}
        
        result = await db.users.update_one(
            {"$or": [{"user_id": user_id}, {"email": user_id}]},
            {"$set": {"role": role, "role_updated_at": datetime.now(timezone.utc)}}
        )
        
        if result.matched_count == 0:
            return {"success": False, "error": "User not found"}
        
        return {
            "success": True,
            "user_id": user_id,
            "new_role": role
        }
    
    @staticmethod
    async def get_activity(db, user_id: str, days: int) -> dict:
        """Historique d'activité d'un utilisateur"""
        since = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Stratégies générées
        strategies = await db.master_plans.count_documents({
            "user_id": user_id,
            "created_at": {"$gte": since}
        })
        
        # Quotas utilisés
        quotas = await db.quota_usage.find(
            {"user_id": user_id, "date": {"$gte": since}},
            {"_id": 0}
        ).to_list(length=1000)
        
        total_quota_usage = sum(q.get("count", 0) for q in quotas)
        
        # Tutoriels complétés
        tutorials = await db.tutorial_progress.count_documents({
            "user_id": user_id,
            "completed": True,
            "completed_at": {"$gte": since}
        })
        
        return {
            "success": True,
            "user_id": user_id,
            "period_days": days,
            "activity": {
                "strategies_generated": strategies,
                "total_quota_usage": total_quota_usage,
                "tutorials_completed": tutorials,
                "quotas_by_feature": {
                    q.get("feature"): q.get("count", 0) for q in quotas
                }
            }
        }
