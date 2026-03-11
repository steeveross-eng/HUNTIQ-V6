"""Alerts Engine Service"""
import os
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from pymongo import MongoClient
from .models import Alert, AlertCreate, SiteSettings, MaintenanceModeUpdate

class AlertsService:
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'test_database')
        self._client = None
        self._db = None
    
    @property
    def db(self):
        if self._db is None:
            self._client = MongoClient(self.mongo_url)
            self._db = self._client[self.db_name]
        return self._db
    
    @property
    def alerts(self):
        return self.db.alerts
    
    @property
    def site_settings(self):
        return self.db.site_settings
    
    # ===========================================
    # ALERTS
    # ===========================================
    
    async def get_all_alerts(self, is_read: Optional[bool] = None, limit: int = 100) -> List[Alert]:
        query = {} if is_read is None else {"is_read": is_read}
        alerts = list(self.alerts.find(query, {"_id": 0}).sort("created_at", -1).limit(limit))
        for a in alerts:
            if isinstance(a.get('created_at'), str):
                a['created_at'] = datetime.fromisoformat(a['created_at'])
        return [Alert(**a) for a in alerts]
    
    async def create_alert(self, alert_input: AlertCreate) -> Alert:
        alert = Alert(**alert_input.model_dump())
        doc = alert.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        self.alerts.insert_one(doc)
        return alert
    
    async def mark_read(self, alert_id: str) -> bool:
        result = self.alerts.update_one({"id": alert_id}, {"$set": {"is_read": True}})
        return result.modified_count > 0
    
    async def mark_all_read(self) -> int:
        result = self.alerts.update_many({"is_read": False}, {"$set": {"is_read": True}})
        return result.modified_count
    
    async def delete_alert(self, alert_id: str) -> bool:
        result = self.alerts.delete_one({"id": alert_id})
        return result.deleted_count > 0
    
    # ===========================================
    # SITE SETTINGS
    # ===========================================
    
    async def get_site_status(self) -> Dict[str, Any]:
        settings = self.site_settings.find_one({"id": "site_settings"}, {"_id": 0})
        if not settings:
            return {
                "maintenance_mode": False,
                "maintenance_title": "",
                "maintenance_message": "",
                "estimated_return": ""
            }
        return {
            "maintenance_mode": settings.get("maintenance_mode", False),
            "maintenance_title": settings.get("maintenance_title", "Site en maintenance"),
            "maintenance_message": settings.get("maintenance_message", ""),
            "estimated_return": settings.get("estimated_return", "")
        }
    
    async def get_site_settings(self) -> SiteSettings:
        settings = self.site_settings.find_one({"id": "site_settings"}, {"_id": 0})
        if not settings:
            default = SiteSettings()
            self.site_settings.insert_one(default.model_dump())
            return default
        return SiteSettings(**settings)
    
    async def toggle_maintenance(self, update: MaintenanceModeUpdate) -> Dict[str, Any]:
        update_data = {
            "maintenance_mode": update.maintenance_mode,
            "maintenance_title": update.maintenance_title,
            "maintenance_message": update.maintenance_message,
            "estimated_return": update.estimated_return,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        if update.maintenance_mode:
            update_data["maintenance_enabled_at"] = datetime.now(timezone.utc).isoformat()
        
        self.site_settings.find_one_and_update(
            {"id": "site_settings"},
            {"$set": update_data},
            upsert=True
        )
        
        return {
            "maintenance_mode": update.maintenance_mode,
            "status": "activé" if update.maintenance_mode else "désactivé"
        }
    
    async def get_stats(self) -> Dict[str, Any]:
        total = self.alerts.count_documents({})
        unread = self.alerts.count_documents({"is_read": False})
        return {
            "engine": "alerts_engine",
            "version": "1.0.0",
            "total_alerts": total,
            "unread_alerts": unread,
            "status": "operational"
        }

_service_instance = None
def get_alerts_service() -> AlertsService:
    global _service_instance
    if _service_instance is None:
        _service_instance = AlertsService()
    return _service_instance
