"""
Marketing Controls Service - V5-ULTIME
======================================

Service de contrôle global ON/OFF pour promotions, campagnes, upsells.
Module isolé - Architecture LEGO V5.
"""

from datetime import datetime, timezone
from typing import List
import logging

logger = logging.getLogger(__name__)


class MarketingControlsService:
    """Service de gestion des contrôles marketing globaux"""
    
    # Configuration par défaut des contrôles
    DEFAULT_CONTROLS = {
        "promotions": {
            "id": "promotions",
            "name_fr": "Promotions",
            "description_fr": "Affichage des promotions et réductions sur le site",
            "enabled": True,
            "category": "sales",
            "priority": 1
        },
        "campaigns": {
            "id": "campaigns",
            "name_fr": "Campagnes Marketing",
            "description_fr": "Campagnes email, SMS et notifications push",
            "enabled": True,
            "category": "outreach",
            "priority": 2
        },
        "upsells": {
            "id": "upsells",
            "name_fr": "Upsells & Cross-sells",
            "description_fr": "Suggestions d'upgrade et produits complémentaires",
            "enabled": True,
            "category": "sales",
            "priority": 3
        },
        "popups": {
            "id": "popups",
            "name_fr": "Popups Marketing",
            "description_fr": "Fenêtres modales de capture email et promotions",
            "enabled": False,
            "category": "capture",
            "priority": 4
        },
        "banners": {
            "id": "banners",
            "name_fr": "Bannières Promotionnelles",
            "description_fr": "Bannières d'annonce en haut de page",
            "enabled": True,
            "category": "display",
            "priority": 5
        },
        "seasonal_themes": {
            "id": "seasonal_themes",
            "name_fr": "Thèmes Saisonniers",
            "description_fr": "Habillage visuel selon la saison de chasse",
            "enabled": True,
            "category": "display",
            "priority": 6
        },
        "referral_program": {
            "id": "referral_program",
            "name_fr": "Programme de Parrainage",
            "description_fr": "Système de parrainage et récompenses",
            "enabled": True,
            "category": "growth",
            "priority": 7
        },
        "ab_testing": {
            "id": "ab_testing",
            "name_fr": "Tests A/B",
            "description_fr": "Expérimentations et tests de conversion",
            "enabled": False,
            "category": "optimization",
            "priority": 8
        }
    }
    
    @staticmethod
    async def get_all_controls(db) -> dict:
        """Récupérer tous les contrôles marketing"""
        try:
            # Charger depuis DB ou utiliser defaults
            controls = await db.marketing_controls.find({}, {"_id": 0}).to_list(50)
            
            if not controls:
                # Utiliser les défauts
                controls = list(MarketingControlsService.DEFAULT_CONTROLS.values())
            
            # Stats
            enabled_count = sum(1 for c in controls if c.get("enabled"))
            
            return {
                "success": True,
                "total": len(controls),
                "enabled": enabled_count,
                "disabled": len(controls) - enabled_count,
                "controls": controls
            }
        except Exception as e:
            logger.error(f"Error getting marketing controls: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def toggle_control(db, control_id: str, enabled: bool) -> dict:
        """Activer/désactiver un contrôle"""
        try:
            # Vérifier si le contrôle existe
            if control_id not in MarketingControlsService.DEFAULT_CONTROLS:
                return {"success": False, "error": f"Control '{control_id}' not found"}
            
            # Mettre à jour ou créer
            result = await db.marketing_controls.update_one(
                {"id": control_id},
                {
                    "$set": {
                        "enabled": enabled,
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    },
                    "$setOnInsert": {
                        **MarketingControlsService.DEFAULT_CONTROLS[control_id],
                        "created_at": datetime.now(timezone.utc).isoformat()
                    }
                },
                upsert=True
            )
            
            return {
                "success": True,
                "control_id": control_id,
                "enabled": enabled,
                "message": f"Control '{control_id}' {'enabled' if enabled else 'disabled'}"
            }
        except Exception as e:
            logger.error(f"Error toggling control: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def bulk_toggle(db, control_ids: List[str], enabled: bool) -> dict:
        """Activer/désactiver plusieurs contrôles"""
        try:
            results = []
            for control_id in control_ids:
                result = await MarketingControlsService.toggle_control(db, control_id, enabled)
                results.append(result)
            
            success_count = sum(1 for r in results if r.get("success"))
            
            return {
                "success": True,
                "total": len(control_ids),
                "success_count": success_count,
                "results": results
            }
        except Exception as e:
            logger.error(f"Error bulk toggling: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def get_control_status(db, control_id: str) -> dict:
        """Vérifier le statut d'un contrôle spécifique"""
        try:
            control = await db.marketing_controls.find_one(
                {"id": control_id}, {"_id": 0}
            )
            
            if not control:
                # Retourner le défaut
                if control_id in MarketingControlsService.DEFAULT_CONTROLS:
                    control = MarketingControlsService.DEFAULT_CONTROLS[control_id]
                else:
                    return {"success": False, "error": f"Control '{control_id}' not found"}
            
            return {
                "success": True,
                "control": control
            }
        except Exception as e:
            logger.error(f"Error getting control status: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def reset_to_defaults(db) -> dict:
        """Réinitialiser tous les contrôles aux valeurs par défaut"""
        try:
            await db.marketing_controls.delete_many({})
            
            # Insérer les défauts
            defaults = list(MarketingControlsService.DEFAULT_CONTROLS.values())
            for control in defaults:
                control["created_at"] = datetime.now(timezone.utc).isoformat()
            
            await db.marketing_controls.insert_many(defaults)
            
            return {
                "success": True,
                "message": "All controls reset to defaults",
                "total": len(defaults)
            }
        except Exception as e:
            logger.error(f"Error resetting controls: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def get_active_features(db) -> dict:
        """Récupérer la liste des fonctionnalités marketing actives (pour le frontend)"""
        try:
            controls = await db.marketing_controls.find(
                {"enabled": True}, {"_id": 0, "id": 1, "name_fr": 1}
            ).to_list(50)
            
            if not controls:
                # Utiliser les défauts actifs
                controls = [
                    {"id": c["id"], "name_fr": c["name_fr"]}
                    for c in MarketingControlsService.DEFAULT_CONTROLS.values()
                    if c.get("enabled")
                ]
            
            return {
                "success": True,
                "active_features": [c["id"] for c in controls],
                "details": controls
            }
        except Exception as e:
            logger.error(f"Error getting active features: {e}")
            return {"success": False, "error": str(e)}


logger.info("MarketingControlsService initialized - V5 LEGO Module")
