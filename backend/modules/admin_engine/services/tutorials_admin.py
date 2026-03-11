"""
Tutorials Admin Service - V5-ULTIME
===================================

Service d'administration des tutoriels.
"""

from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

# Tutoriels par défaut
DEFAULT_TUTORIALS = [
    {"id": "tut_strategy_generation", "type": "feature", "feature": "strategy"},
    {"id": "tut_plan_maitre", "type": "workflow", "feature": "plan_maitre"},
    {"id": "tut_territory", "type": "feature", "feature": "territory"},
    {"id": "tut_live_heading_preview", "type": "premium_preview", "feature": "live_heading"},
    {"id": "tut_advanced_layers_preview", "type": "premium_preview", "feature": "advanced_layers"},
    {"id": "tip_wind_direction", "type": "tip", "feature": "weather"},
    {"id": "tip_golden_hours", "type": "tip", "feature": "timing"}
]


class TutorialsAdminService:
    """Service isolé pour l'administration des tutoriels"""
    
    @staticmethod
    async def get_tutorials(db) -> dict:
        """Liste tous les tutoriels avec statuts"""
        # Récupérer les statuts personnalisés
        custom_statuses = await db.tutorial_config.find(
            {}, {"_id": 0}
        ).to_list(length=100)
        
        status_map = {s["tutorial_id"]: s for s in custom_statuses}
        
        tutorials = []
        for tut in DEFAULT_TUTORIALS:
            tutorial = {
                **tut,
                "enabled": status_map.get(tut["id"], {}).get("enabled", True),
                "modified_at": status_map.get(tut["id"], {}).get("modified_at")
            }
            tutorials.append(tutorial)
        
        return {
            "success": True,
            "total": len(tutorials),
            "tutorials": tutorials
        }
    
    @staticmethod
    async def toggle_tutorial(db, tutorial_id: str, enabled: bool) -> dict:
        """Activer/désactiver un tutoriel"""
        valid_ids = [t["id"] for t in DEFAULT_TUTORIALS]
        if tutorial_id not in valid_ids:
            return {"success": False, "error": "Tutorial not found"}
        
        await db.tutorial_config.update_one(
            {"tutorial_id": tutorial_id},
            {
                "$set": {
                    "enabled": enabled,
                    "modified_at": datetime.now(timezone.utc)
                }
            },
            upsert=True
        )
        
        return {
            "success": True,
            "tutorial_id": tutorial_id,
            "enabled": enabled
        }
    
    @staticmethod
    async def get_progress_stats(db) -> dict:
        """Statistiques de progression globale"""
        # Compter les completions
        completions = await db.tutorial_progress.count_documents({"completed": True})
        skips = await db.tutorial_progress.count_documents({"skipped": True})
        total = await db.tutorial_progress.count_documents({})
        
        # Par tutoriel
        pipeline = [
            {"$match": {"completed": True}},
            {"$group": {"_id": "$tutorial_id", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        by_tutorial = await db.tutorial_progress.aggregate(pipeline).to_list(length=20)
        
        return {
            "success": True,
            "stats": {
                "total_interactions": total,
                "completions": completions,
                "skips": skips,
                "completion_rate": round((completions / max(total, 1)) * 100, 1)
            },
            "by_tutorial": {r["_id"]: r["count"] for r in by_tutorial}
        }
