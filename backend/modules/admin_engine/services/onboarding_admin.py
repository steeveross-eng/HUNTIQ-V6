"""
Onboarding Admin Service - V5-ULTIME
====================================

Service d'administration des parcours d'onboarding.
"""

from typing import Optional
import logging

logger = logging.getLogger(__name__)

ONBOARDING_STEPS = ["profile", "territory", "objectives", "plan_maitre"]


class OnboardingAdminService:
    """Service isolé pour l'administration onboarding"""
    
    @staticmethod
    async def get_stats(db) -> dict:
        """Statistiques globales d'onboarding"""
        total_users = await db.onboarding_status.count_documents({})
        completed = await db.onboarding_status.count_documents({"completed": True})
        skipped = await db.onboarding_status.count_documents({"skipped": True})
        in_progress = total_users - completed - skipped
        
        # Taux de complétion par étape
        step_stats = {}
        for step in ONBOARDING_STEPS:
            count = await db.onboarding_status.count_documents({
                "completed_steps": step
            })
            step_stats[step] = {
                "completed": count,
                "rate": round((count / max(total_users, 1)) * 100, 1)
            }
        
        return {
            "success": True,
            "stats": {
                "total_users": total_users,
                "completed": completed,
                "skipped": skipped,
                "in_progress": in_progress,
                "completion_rate": round((completed / max(total_users, 1)) * 100, 1),
                "skip_rate": round((skipped / max(total_users, 1)) * 100, 1)
            },
            "by_step": step_stats
        }
    
    @staticmethod
    async def get_flows(db) -> dict:
        """Configuration des flows d'onboarding"""
        flows = [
            {
                "step": "profile",
                "title": "Profil chasseur",
                "questions": 3,
                "required": True
            },
            {
                "step": "territory",
                "title": "Configuration territoire",
                "questions": 3,
                "required": True
            },
            {
                "step": "objectives",
                "title": "Objectifs de saison",
                "questions": 3,
                "required": True
            },
            {
                "step": "plan_maitre",
                "title": "Création Plan Maître",
                "auto_generate": True,
                "required": True
            }
        ]
        
        return {
            "success": True,
            "total_steps": len(flows),
            "flows": flows
        }
    
    @staticmethod
    async def get_users_status(db, completed: Optional[bool], limit: int) -> dict:
        """Liste des utilisateurs et leur statut onboarding"""
        query = {}
        if completed is not None:
            query["completed"] = completed
        
        users = await db.onboarding_status.find(
            query, {"_id": 0}
        ).sort("started_at", -1).limit(limit).to_list(length=limit)
        
        total = await db.onboarding_status.count_documents(query)
        
        return {
            "success": True,
            "total": total,
            "users": users
        }
