"""
Upsell Admin Service - V5-ULTIME
================================

Service d'administration des campagnes upsell.
"""

from datetime import datetime, timezone, timedelta
import logging

logger = logging.getLogger(__name__)

# Campagnes par défaut (référence)
DEFAULT_CAMPAIGNS = [
    "quota_strategy_reached",
    "feature_live_heading_locked",
    "feature_advanced_layers_locked",
    "feature_custom_rules_locked",
    "time_7_days_free",
    "pattern_high_usage",
    "action_export_blocked"
]


class UpsellAdminService:
    """Service isolé pour l'administration upsell"""
    
    @staticmethod
    async def get_campaigns(db) -> dict:
        """Liste des campagnes avec statuts"""
        # Récupérer les statuts personnalisés
        custom_statuses = await db.upsell_campaign_config.find(
            {}, {"_id": 0}
        ).to_list(length=100)
        
        status_map = {s["campaign_name"]: s for s in custom_statuses}
        
        campaigns = []
        for name in DEFAULT_CAMPAIGNS:
            campaign = {
                "name": name,
                "enabled": status_map.get(name, {}).get("enabled", True),
                "priority": status_map.get(name, {}).get("priority", 5),
                "modified_at": status_map.get(name, {}).get("modified_at")
            }
            campaigns.append(campaign)
        
        return {
            "success": True,
            "total": len(campaigns),
            "campaigns": campaigns
        }
    
    @staticmethod
    async def toggle_campaign(db, campaign_name: str, enabled: bool) -> dict:
        """Activer/désactiver une campagne"""
        if campaign_name not in DEFAULT_CAMPAIGNS:
            return {"success": False, "error": "Campaign not found"}
        
        await db.upsell_campaign_config.update_one(
            {"campaign_name": campaign_name},
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
            "campaign": campaign_name,
            "enabled": enabled
        }
    
    @staticmethod
    async def get_analytics(db, days: int) -> dict:
        """Analytics des campagnes"""
        since = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Impressions par campagne
        impressions = await db.upsell_impressions.find(
            {"shown_at": {"$gte": since}},
            {"campaign_name": 1, "_id": 0}
        ).to_list(length=100000)
        
        # Clicks par campagne
        clicks = await db.upsell_clicks.find(
            {"clicked_at": {"$gte": since}},
            {"campaign_name": 1, "_id": 0}
        ).to_list(length=100000)
        
        # Dismissals
        dismissals = await db.upsell_dismissals.find(
            {"dismissed_at": {"$gte": since}},
            {"campaign_name": 1, "_id": 0}
        ).to_list(length=100000)
        
        # Agrégation
        stats = {}
        for i in impressions:
            name = i.get("campaign_name", "unknown")
            if name not in stats:
                stats[name] = {"impressions": 0, "clicks": 0, "dismissals": 0}
            stats[name]["impressions"] += 1
        
        for c in clicks:
            name = c.get("campaign_name", "unknown")
            if name in stats:
                stats[name]["clicks"] += 1
        
        for d in dismissals:
            name = d.get("campaign_name", "unknown")
            if name in stats:
                stats[name]["dismissals"] += 1
        
        # Calculer CTR
        for name, data in stats.items():
            imp = data["impressions"]
            data["ctr"] = round((data["clicks"] / max(imp, 1)) * 100, 2)
        
        return {
            "success": True,
            "period_days": days,
            "campaigns": stats,
            "totals": {
                "impressions": len(impressions),
                "clicks": len(clicks),
                "dismissals": len(dismissals)
            }
        }
    
    @staticmethod
    async def get_conversion_funnel(db) -> dict:
        """Funnel de conversion upsell"""
        # Impressions totales
        impressions = await db.upsell_impressions.count_documents({})
        
        # Clicks totaux
        clicks = await db.upsell_clicks.count_documents({})
        
        # Conversions (utilisateurs qui ont upgrade après click)
        # Note: Simplification - compter les upgrades
        upgrades = await db.subscription_upgrades.count_documents({})
        
        return {
            "success": True,
            "funnel": {
                "impressions": impressions,
                "clicks": clicks,
                "conversions": upgrades,
                "impression_to_click": round((clicks / max(impressions, 1)) * 100, 2),
                "click_to_conversion": round((upgrades / max(clicks, 1)) * 100, 2),
                "overall_conversion": round((upgrades / max(impressions, 1)) * 100, 2)
            }
        }
