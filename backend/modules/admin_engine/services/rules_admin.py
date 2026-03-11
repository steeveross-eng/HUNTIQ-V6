"""
Rules Admin Service - V5-ULTIME
===============================

Service d'administration des règles du Plan Maître.
"""

from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

# Règles par défaut
DEFAULT_RULES = [
    {"id": "wind_direction", "category": "weather", "weight": 1.0},
    {"id": "temperature_optimal", "category": "weather", "weight": 0.8},
    {"id": "pressure_change", "category": "weather", "weight": 0.9},
    {"id": "moon_phase", "category": "timing", "weight": 0.7},
    {"id": "golden_hours", "category": "timing", "weight": 1.0},
    {"id": "legal_hours", "category": "legal", "weight": 1.0},
    {"id": "habitat_quality", "category": "territory", "weight": 0.9},
    {"id": "corridor_activity", "category": "territory", "weight": 0.85},
    {"id": "water_proximity", "category": "territory", "weight": 0.75},
    {"id": "human_activity", "category": "disturbance", "weight": -0.5},
    {"id": "historical_success", "category": "data", "weight": 0.8},
    {"id": "species_behavior", "category": "wildlife", "weight": 0.9}
]


class RulesAdminService:
    """Service isolé pour l'administration des règles"""
    
    @staticmethod
    async def get_rules(db) -> dict:
        """Liste toutes les règles avec statuts"""
        # Récupérer les configurations personnalisées
        custom_configs = await db.rules_config.find(
            {}, {"_id": 0}
        ).to_list(length=100)
        
        config_map = {c["rule_id"]: c for c in custom_configs}
        
        rules = []
        for rule in DEFAULT_RULES:
            config = config_map.get(rule["id"], {})
            rules.append({
                **rule,
                "enabled": config.get("enabled", True),
                "custom_weight": config.get("weight", rule["weight"]),
                "modified_at": config.get("modified_at")
            })
        
        return {
            "success": True,
            "total": len(rules),
            "rules": rules
        }
    
    @staticmethod
    async def toggle_rule(db, rule_id: str, enabled: bool) -> dict:
        """Activer/désactiver une règle"""
        valid_ids = [r["id"] for r in DEFAULT_RULES]
        if rule_id not in valid_ids:
            return {"success": False, "error": "Rule not found"}
        
        await db.rules_config.update_one(
            {"rule_id": rule_id},
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
            "rule_id": rule_id,
            "enabled": enabled
        }
    
    @staticmethod
    async def update_weight(db, rule_id: str, weight: float) -> dict:
        """Modifier le poids d'une règle"""
        valid_ids = [r["id"] for r in DEFAULT_RULES]
        if rule_id not in valid_ids:
            return {"success": False, "error": "Rule not found"}
        
        if weight < -1.0 or weight > 2.0:
            return {"success": False, "error": "Weight must be between -1.0 and 2.0"}
        
        await db.rules_config.update_one(
            {"rule_id": rule_id},
            {
                "$set": {
                    "weight": weight,
                    "modified_at": datetime.now(timezone.utc)
                }
            },
            upsert=True
        )
        
        return {
            "success": True,
            "rule_id": rule_id,
            "weight": weight
        }
    
    @staticmethod
    async def get_stats(db) -> dict:
        """Statistiques d'utilisation des règles"""
        # Nombre de stratégies générées
        strategies = await db.master_plans.count_documents({})
        
        # Règles les plus impactantes (placeholder)
        top_rules = [r["id"] for r in sorted(DEFAULT_RULES, key=lambda x: abs(x["weight"]), reverse=True)[:5]]
        
        return {
            "success": True,
            "stats": {
                "total_rules": len(DEFAULT_RULES),
                "strategies_generated": strategies,
                "categories": list(set(r["category"] for r in DEFAULT_RULES)),
                "top_impact_rules": top_rules
            }
        }
