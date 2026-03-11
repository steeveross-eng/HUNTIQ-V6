"""
Freemium Admin Service - V5-ULTIME
==================================

Service d'administration des quotas et tiers freemium.
"""

from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class FreemiumAdminService:
    """Service isolé pour l'administration freemium"""
    
    @staticmethod
    async def get_quota_overview(db) -> dict:
        """Vue d'ensemble des quotas utilisés"""
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Quotas du jour
        quotas = await db.quota_usage.find(
            {"date": {"$gte": today}},
            {"_id": 0}
        ).to_list(length=10000)
        
        # Agrégation par feature
        by_feature = {}
        for q in quotas:
            feature = q.get("feature", "unknown")
            if feature not in by_feature:
                by_feature[feature] = {"total_usage": 0, "users": 0}
            by_feature[feature]["total_usage"] += q.get("count", 0)
            by_feature[feature]["users"] += 1
        
        return {
            "success": True,
            "date": today.isoformat(),
            "quotas_by_feature": by_feature,
            "total_quota_records": len(quotas)
        }
    
    @staticmethod
    async def get_user_status(db, user_id: str) -> dict:
        """Statut freemium d'un utilisateur"""
        # Subscription
        sub = await db.subscriptions.find_one({"user_id": user_id}, {"_id": 0})
        
        # Quotas du jour
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        quotas = await db.quota_usage.find(
            {"user_id": user_id, "date": {"$gte": today}},
            {"_id": 0}
        ).to_list(length=100)
        
        # Overrides
        overrides = await db.user_overrides.find_one({"user_id": user_id}, {"_id": 0})
        
        return {
            "success": True,
            "user_id": user_id,
            "subscription": sub or {"tier": "free"},
            "today_quotas": quotas,
            "overrides": overrides
        }
    
    @staticmethod
    async def set_user_override(db, user_id: str, overrides: dict) -> dict:
        """Override les limites d'un utilisateur"""
        await db.user_overrides.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "overrides": overrides,
                    "updated_at": datetime.now(timezone.utc),
                    "updated_by": "admin"
                }
            },
            upsert=True
        )
        
        return {
            "success": True,
            "message": f"Overrides set for user {user_id}",
            "overrides": overrides
        }
    
    @staticmethod
    async def get_tier_distribution(db) -> dict:
        """Distribution des utilisateurs par tier"""
        pipeline = [
            {"$group": {"_id": "$tier", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        results = await db.subscriptions.aggregate(pipeline).to_list(length=10)
        
        distribution = {r["_id"]: r["count"] for r in results}
        total = sum(distribution.values())
        
        return {
            "success": True,
            "distribution": distribution,
            "total_users": total,
            "percentages": {
                tier: round((count / max(total, 1)) * 100, 1) 
                for tier, count in distribution.items()
            }
        }
