"""
Maintenance Admin Service - V5-ULTIME Administration Premium
============================================================

Service d'administration de l'infrastructure pour:
- Contrôle d'accès au site (maintenance mode)
- Gestion des périodes de maintenance
- Logs de maintenance
- Configuration système

Module isolé - aucun import croisé.
Phase 3 Migration.
"""

from datetime import datetime, timezone
import logging
import uuid

logger = logging.getLogger(__name__)


class MaintenanceAdminService:
    """Service isolé pour l'administration de la maintenance"""
    
    # ============ MAINTENANCE MODE ============
    @staticmethod
    async def get_maintenance_status(db) -> dict:
        """Récupérer le statut de maintenance actuel"""
        config = await db.site_config.find_one(
            {"type": "maintenance"},
            {"_id": 0}
        )
        
        if not config:
            # Créer config par défaut
            config = {
                "type": "maintenance",
                "enabled": False,
                "message": "Le site est temporairement en maintenance. Veuillez réessayer plus tard.",
                "estimated_end": None,
                "allowed_ips": [],
                "allowed_roles": ["admin"],
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            await db.site_config.insert_one(config)
            config.pop("_id", None)
        
        return {
            "success": True,
            "maintenance": config
        }
    
    @staticmethod
    async def toggle_maintenance_mode(db, enabled: bool, message: str = None, estimated_end: str = None) -> dict:
        """Activer/Désactiver le mode maintenance"""
        update = {
            "enabled": enabled,
            "updated_at": datetime.now(timezone.utc)
        }
        
        if message:
            update["message"] = message
        if estimated_end:
            update["estimated_end"] = estimated_end
        
        await db.site_config.update_one(
            {"type": "maintenance"},
            {"$set": update},
            upsert=True
        )
        
        # Log l'action
        log_entry = {
            "id": str(uuid.uuid4()),
            "action": "maintenance_toggled",
            "enabled": enabled,
            "message": message,
            "timestamp": datetime.now(timezone.utc)
        }
        await db.maintenance_logs.insert_one(log_entry)
        
        return {
            "success": True,
            "enabled": enabled,
            "message": "Mode maintenance activé" if enabled else "Mode maintenance désactivé"
        }
    
    @staticmethod
    async def update_maintenance_config(db, config_updates: dict) -> dict:
        """Mettre à jour la configuration de maintenance"""
        config_updates["updated_at"] = datetime.now(timezone.utc)
        
        await db.site_config.update_one(
            {"type": "maintenance"},
            {"$set": config_updates},
            upsert=True
        )
        
        return {"success": True, "updated": True}
    
    # ============ ACCESS CONTROL ============
    @staticmethod
    async def get_access_rules(db) -> dict:
        """Récupérer les règles d'accès"""
        rules = await db.access_rules.find(
            {}, {"_id": 0}
        ).sort("priority", 1).to_list(length=100)
        
        return {
            "success": True,
            "total": len(rules),
            "rules": rules
        }
    
    @staticmethod
    async def create_access_rule(db, rule_data: dict) -> dict:
        """Créer une nouvelle règle d'accès"""
        rule = {
            "id": str(uuid.uuid4()),
            "name": rule_data.get("name", ""),
            "description": rule_data.get("description", ""),
            "type": rule_data.get("type", "ip"),  # ip, role, time, geo
            "condition": rule_data.get("condition", {}),
            "action": rule_data.get("action", "allow"),  # allow, deny, redirect
            "priority": rule_data.get("priority", 100),
            "enabled": rule_data.get("enabled", True),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        await db.access_rules.insert_one(rule)
        rule.pop("_id", None)
        
        return {"success": True, "rule": rule}
    
    @staticmethod
    async def update_access_rule(db, rule_id: str, updates: dict) -> dict:
        """Mettre à jour une règle d'accès"""
        updates["updated_at"] = datetime.now(timezone.utc)
        
        result = await db.access_rules.update_one(
            {"id": rule_id},
            {"$set": updates}
        )
        
        if result.matched_count == 0:
            return {"success": False, "error": "Rule not found"}
        
        return {"success": True, "rule_id": rule_id, "updated": True}
    
    @staticmethod
    async def delete_access_rule(db, rule_id: str) -> dict:
        """Supprimer une règle d'accès"""
        result = await db.access_rules.delete_one({"id": rule_id})
        
        if result.deleted_count == 0:
            return {"success": False, "error": "Rule not found"}
        
        return {"success": True, "rule_id": rule_id, "deleted": True}
    
    @staticmethod
    async def toggle_access_rule(db, rule_id: str, enabled: bool) -> dict:
        """Activer/Désactiver une règle d'accès"""
        result = await db.access_rules.update_one(
            {"id": rule_id},
            {"$set": {"enabled": enabled, "updated_at": datetime.now(timezone.utc)}}
        )
        
        if result.matched_count == 0:
            return {"success": False, "error": "Rule not found"}
        
        return {"success": True, "rule_id": rule_id, "enabled": enabled}
    
    # ============ ALLOWED IPS ============
    @staticmethod
    async def get_allowed_ips(db) -> dict:
        """Récupérer les IPs autorisées en mode maintenance"""
        config = await db.site_config.find_one(
            {"type": "maintenance"},
            {"_id": 0, "allowed_ips": 1}
        )
        
        return {
            "success": True,
            "allowed_ips": config.get("allowed_ips", []) if config else []
        }
    
    @staticmethod
    async def add_allowed_ip(db, ip: str, label: str = "") -> dict:
        """Ajouter une IP autorisée"""
        ip_entry = {
            "ip": ip,
            "label": label,
            "added_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.site_config.update_one(
            {"type": "maintenance"},
            {"$push": {"allowed_ips": ip_entry}},
            upsert=True
        )
        
        return {"success": True, "ip": ip, "added": True}
    
    @staticmethod
    async def remove_allowed_ip(db, ip: str) -> dict:
        """Retirer une IP autorisée"""
        await db.site_config.update_one(
            {"type": "maintenance"},
            {"$pull": {"allowed_ips": {"ip": ip}}}
        )
        
        return {"success": True, "ip": ip, "removed": True}
    
    # ============ MAINTENANCE LOGS ============
    @staticmethod
    async def get_maintenance_logs(db, limit: int = 50) -> dict:
        """Récupérer les logs de maintenance"""
        logs = await db.maintenance_logs.find(
            {}, {"_id": 0}
        ).sort("timestamp", -1).limit(limit).to_list(length=limit)
        
        return {
            "success": True,
            "total": len(logs),
            "logs": logs
        }
    
    # ============ SCHEDULED MAINTENANCE ============
    @staticmethod
    async def get_scheduled_maintenances(db) -> dict:
        """Récupérer les maintenances planifiées"""
        schedules = await db.scheduled_maintenance.find(
            {}, {"_id": 0}
        ).sort("start_time", 1).to_list(length=50)
        
        return {
            "success": True,
            "total": len(schedules),
            "schedules": schedules
        }
    
    @staticmethod
    async def create_scheduled_maintenance(db, schedule_data: dict) -> dict:
        """Créer une maintenance planifiée"""
        schedule = {
            "id": str(uuid.uuid4()),
            "title": schedule_data.get("title", "Maintenance planifiée"),
            "description": schedule_data.get("description", ""),
            "start_time": schedule_data.get("start_time"),
            "end_time": schedule_data.get("end_time"),
            "auto_enable": schedule_data.get("auto_enable", True),
            "notify_users": schedule_data.get("notify_users", True),
            "status": "scheduled",
            "created_at": datetime.now(timezone.utc)
        }
        
        await db.scheduled_maintenance.insert_one(schedule)
        schedule.pop("_id", None)
        
        return {"success": True, "schedule": schedule}
    
    @staticmethod
    async def delete_scheduled_maintenance(db, schedule_id: str) -> dict:
        """Supprimer une maintenance planifiée"""
        result = await db.scheduled_maintenance.delete_one({"id": schedule_id})
        
        if result.deleted_count == 0:
            return {"success": False, "error": "Schedule not found"}
        
        return {"success": True, "schedule_id": schedule_id, "deleted": True}
    
    # ============ SYSTEM STATUS ============
    @staticmethod
    async def get_system_status(db) -> dict:
        """Récupérer le statut système global"""
        # Vérifier la maintenance
        maintenance = await db.site_config.find_one(
            {"type": "maintenance"},
            {"_id": 0}
        )
        
        # Compter les règles actives
        active_rules = await db.access_rules.count_documents({"enabled": True})
        total_rules = await db.access_rules.count_documents({})
        
        # Maintenances planifiées à venir
        now = datetime.now(timezone.utc)
        upcoming = await db.scheduled_maintenance.count_documents({
            "start_time": {"$gte": now.isoformat()},
            "status": "scheduled"
        })
        
        return {
            "success": True,
            "status": {
                "maintenance_enabled": maintenance.get("enabled", False) if maintenance else False,
                "access_rules": {
                    "active": active_rules,
                    "total": total_rules
                },
                "scheduled_maintenances": upcoming,
                "last_check": datetime.now(timezone.utc).isoformat()
            }
        }
