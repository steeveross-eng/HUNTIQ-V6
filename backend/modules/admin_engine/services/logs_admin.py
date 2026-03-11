"""
Logs Admin Service - V5-ULTIME
==============================

Service d'administration des logs système.
"""

from typing import Optional
import logging

logger = logging.getLogger(__name__)


class LogsAdminService:
    """Service isolé pour l'administration des logs"""
    
    @staticmethod
    async def get_errors(db, limit: int, severity: Optional[str]) -> dict:
        """Récupère les logs d'erreurs"""
        query = {}
        if severity:
            query["severity"] = severity
        
        errors = await db.error_logs.find(
            query, {"_id": 0}
        ).sort("timestamp", -1).limit(limit).to_list(length=limit)
        
        # Statistiques
        total = await db.error_logs.count_documents(query)
        by_severity = {}
        for sev in ["critical", "error", "warning", "info"]:
            count = await db.error_logs.count_documents({"severity": sev})
            if count > 0:
                by_severity[sev] = count
        
        return {
            "success": True,
            "total": total,
            "by_severity": by_severity,
            "errors": errors
        }
    
    @staticmethod
    async def get_webhooks(db, limit: int) -> dict:
        """Récupère les logs de webhooks"""
        # Webhooks Stripe
        webhooks = await db.webhook_logs.find(
            {}, {"_id": 0}
        ).sort("received_at", -1).limit(limit).to_list(length=limit)
        
        # Stats
        total = await db.webhook_logs.count_documents({})
        success = await db.webhook_logs.count_documents({"status": "success"})
        failed = await db.webhook_logs.count_documents({"status": "failed"})
        
        return {
            "success": True,
            "total": total,
            "stats": {
                "success": success,
                "failed": failed,
                "success_rate": round((success / max(total, 1)) * 100, 1)
            },
            "webhooks": webhooks
        }
    
    @staticmethod
    async def get_events(db, limit: int, event_type: Optional[str]) -> dict:
        """Récupère les logs d'événements"""
        query = {}
        if event_type:
            query["event_type"] = event_type
        
        events = await db.event_logs.find(
            query, {"_id": 0}
        ).sort("timestamp", -1).limit(limit).to_list(length=limit)
        
        # Types d'événements
        event_types = await db.event_logs.distinct("event_type")
        
        return {
            "success": True,
            "total": len(events),
            "event_types": event_types,
            "events": events
        }
