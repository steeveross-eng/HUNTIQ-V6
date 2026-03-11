"""
Settings Admin Service - V5-ULTIME
==================================

Service d'administration des paramètres système.
"""

from datetime import datetime, timezone
from typing import Any
import os
import logging

logger = logging.getLogger(__name__)

# Toggles par défaut
DEFAULT_TOGGLES = [
    {"id": "maintenance_mode", "name": "Mode maintenance", "enabled": False, "category": "system"},
    {"id": "new_registrations", "name": "Nouvelles inscriptions", "enabled": True, "category": "auth"},
    {"id": "payment_enabled", "name": "Paiements actifs", "enabled": True, "category": "payment"},
    {"id": "upsell_enabled", "name": "Upsells actifs", "enabled": True, "category": "monetisation"},
    {"id": "onboarding_enabled", "name": "Onboarding actif", "enabled": True, "category": "onboarding"},
    {"id": "tutorials_enabled", "name": "Tutoriels actifs", "enabled": True, "category": "tutorials"},
    {"id": "analytics_enabled", "name": "Analytics actifs", "enabled": True, "category": "analytics"},
    {"id": "live_heading_enabled", "name": "Live Heading actif", "enabled": True, "category": "features"},
    {"id": "advanced_layers_enabled", "name": "Couches avancées actives", "enabled": True, "category": "features"},
    {"id": "debug_mode", "name": "Mode debug", "enabled": False, "category": "dev"}
]


class SettingsAdminService:
    """Service isolé pour l'administration des paramètres"""
    
    @staticmethod
    async def get_settings(db) -> dict:
        """Récupère tous les paramètres"""
        settings = await db.system_settings.find(
            {}, {"_id": 0}
        ).to_list(length=100)
        
        settings_map = {s["key"]: s["value"] for s in settings}
        
        return {
            "success": True,
            "settings": settings_map,
            "default_settings": {
                "app_name": "BIONIC HUNT/Chasse V5-ULTIME",
                "app_version": "5.0.0",
                "currency": "CAD",
                "timezone": "America/Toronto",
                "language": "fr"
            }
        }
    
    @staticmethod
    async def update_setting(db, key: str, value: Any) -> dict:
        """Modifier un paramètre"""
        await db.system_settings.update_one(
            {"key": key},
            {
                "$set": {
                    "value": value,
                    "updated_at": datetime.now(timezone.utc)
                }
            },
            upsert=True
        )
        
        return {
            "success": True,
            "key": key,
            "value": value
        }
    
    @staticmethod
    async def get_api_keys_status(db) -> dict:
        """Statut des clés API (masquées)"""
        # Vérifier les clés d'environnement
        keys = {
            "STRIPE_API_KEY": bool(os.environ.get("STRIPE_API_KEY")),
            "MONGO_URL": bool(os.environ.get("MONGO_URL")),
            "JWT_SECRET_KEY": bool(os.environ.get("JWT_SECRET_KEY")),
            "OPENAI_API_KEY": bool(os.environ.get("OPENAI_API_KEY")),
            "EMERGENT_LLM_KEY": bool(os.environ.get("EMERGENT_LLM_KEY"))
        }
        
        # Masquer les valeurs
        masked_keys = {}
        for key, exists in keys.items():
            if exists:
                val = os.environ.get(key, "")
                if len(val) > 8:
                    masked_keys[key] = {
                        "configured": True,
                        "preview": f"{val[:4]}...{val[-4:]}"
                    }
                else:
                    masked_keys[key] = {"configured": True, "preview": "***"}
            else:
                masked_keys[key] = {"configured": False, "preview": None}
        
        return {
            "success": True,
            "api_keys": masked_keys
        }
    
    @staticmethod
    async def get_toggles(db) -> dict:
        """Récupère les toggles de fonctionnalités"""
        custom_toggles = await db.feature_toggles.find(
            {}, {"_id": 0}
        ).to_list(length=100)
        
        toggle_map = {t["toggle_id"]: t for t in custom_toggles}
        
        toggles = []
        for toggle in DEFAULT_TOGGLES:
            custom = toggle_map.get(toggle["id"], {})
            toggles.append({
                **toggle,
                "enabled": custom.get("enabled", toggle["enabled"]),
                "modified_at": custom.get("modified_at")
            })
        
        return {
            "success": True,
            "toggles": toggles
        }
    
    @staticmethod
    async def update_toggle(db, toggle_id: str, enabled: bool) -> dict:
        """Modifier un toggle"""
        valid_ids = [t["id"] for t in DEFAULT_TOGGLES]
        if toggle_id not in valid_ids:
            return {"success": False, "error": "Toggle not found"}
        
        await db.feature_toggles.update_one(
            {"toggle_id": toggle_id},
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
            "toggle_id": toggle_id,
            "enabled": enabled
        }
