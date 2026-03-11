"""
Payments Admin Service - V5-ULTIME
==================================

Service d'administration des paiements Stripe.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class PaymentsAdminService:
    """Service isolé pour l'administration des paiements"""
    
    @staticmethod
    async def get_transactions(db, limit: int, status: Optional[str], skip: int) -> dict:
        """Récupère toutes les transactions"""
        query = {}
        if status:
            query["payment_status"] = status
        
        transactions = await db.payment_transactions.find(
            query, {"_id": 0}
        ).sort("created_at", -1).skip(skip).limit(limit).to_list(length=limit)
        
        total = await db.payment_transactions.count_documents(query)
        
        return {
            "success": True,
            "total": total,
            "limit": limit,
            "skip": skip,
            "transactions": transactions
        }
    
    @staticmethod
    async def get_transaction_detail(db, transaction_id: str) -> dict:
        """Détail d'une transaction"""
        transaction = await db.payment_transactions.find_one(
            {"session_id": transaction_id}, {"_id": 0}
        )
        
        if not transaction:
            return {"success": False, "error": "Transaction not found"}
        
        return {"success": True, "transaction": transaction}
    
    @staticmethod
    async def get_revenue_stats(db, days: int) -> dict:
        """Statistiques de revenus"""
        since = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Transactions payées
        paid = await db.payment_transactions.find(
            {"payment_status": "paid", "created_at": {"$gte": since}},
            {"amount": 1, "tier": 1, "created_at": 1, "_id": 0}
        ).to_list(length=10000)
        
        total_revenue = sum(t.get("amount", 0) for t in paid)
        
        # Par tier
        by_tier = {}
        for t in paid:
            tier = t.get("tier", "unknown")
            if tier not in by_tier:
                by_tier[tier] = {"count": 0, "revenue": 0}
            by_tier[tier]["count"] += 1
            by_tier[tier]["revenue"] += t.get("amount", 0)
        
        # Par jour
        by_day = {}
        for t in paid:
            day = t.get("created_at", datetime.now()).strftime("%Y-%m-%d")
            if day not in by_day:
                by_day[day] = {"count": 0, "revenue": 0}
            by_day[day]["count"] += 1
            by_day[day]["revenue"] += t.get("amount", 0)
        
        return {
            "success": True,
            "period_days": days,
            "revenue": {
                "total": round(total_revenue, 2),
                "currency": "CAD",
                "transaction_count": len(paid)
            },
            "by_tier": by_tier,
            "by_day": dict(sorted(by_day.items()))
        }
    
    @staticmethod
    async def get_subscriptions(db, tier: Optional[str], limit: int) -> dict:
        """Liste des abonnements"""
        query = {}
        if tier:
            query["tier"] = tier
        
        subscriptions = await db.subscriptions.find(
            query, {"_id": 0}
        ).sort("upgraded_at", -1).limit(limit).to_list(length=limit)
        
        total = await db.subscriptions.count_documents(query)
        
        return {
            "success": True,
            "total": total,
            "subscriptions": subscriptions
        }
