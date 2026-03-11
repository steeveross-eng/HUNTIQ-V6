"""
Strategy Admin Service - V5-ULTIME
==================================

Service d'administration des stratégies générées.
"""

from datetime import datetime, timezone
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class StrategyAdminService:
    """Service isolé pour l'administration des stratégies"""
    
    @staticmethod
    async def get_strategies(db, limit: int, user_id: Optional[str]) -> dict:
        """Liste les stratégies générées"""
        query = {}
        if user_id:
            query["user_id"] = user_id
        
        strategies = await db.master_plans.find(
            query, {"_id": 0}
        ).sort("created_at", -1).limit(limit).to_list(length=limit)
        
        total = await db.master_plans.count_documents(query)
        
        return {
            "success": True,
            "total": total,
            "strategies": strategies
        }
    
    @staticmethod
    async def get_logs(db, limit: int) -> dict:
        """Logs de génération de stratégies"""
        logs = await db.strategy_logs.find(
            {}, {"_id": 0}
        ).sort("timestamp", -1).limit(limit).to_list(length=limit)
        
        return {
            "success": True,
            "total": len(logs),
            "logs": logs
        }
    
    @staticmethod
    async def get_diagnostics(db) -> dict:
        """Diagnostics du moteur de stratégie"""
        # Compter les plans par statut
        total_plans = await db.master_plans.count_documents({})
        
        # Plans par phase
        pipeline = [
            {"$group": {"_id": "$current_phase", "count": {"$sum": 1}}}
        ]
        by_phase = await db.master_plans.aggregate(pipeline).to_list(length=10)
        
        # Plans créés aujourd'hui
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        today_count = await db.master_plans.count_documents({
            "created_at": {"$gte": today}
        })
        
        # Plans par source
        pipeline_source = [
            {"$group": {"_id": "$created_from", "count": {"$sum": 1}}}
        ]
        by_source = await db.master_plans.aggregate(pipeline_source).to_list(length=10)
        
        return {
            "success": True,
            "diagnostics": {
                "engine_status": "operational",
                "total_plans": total_plans,
                "plans_today": today_count,
                "by_phase": {r["_id"]: r["count"] for r in by_phase if r["_id"]},
                "by_source": {r["_id"]: r["count"] for r in by_source if r["_id"]},
                "last_check": datetime.now(timezone.utc).isoformat()
            }
        }
