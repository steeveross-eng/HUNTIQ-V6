"""
Backup Cloud Service - Business Logic
"""

from datetime import datetime, timezone

class BackupCloudService:
    """Service centralisé pour la gestion des backups cloud"""
    
    def __init__(self, db):
        self.db = db
        self.backup_config = db.backup_cloud_config
        self.backup_logs = db.backup_logs
    
    async def get_status(self):
        """Retourne le statut global des backups"""
        atlas = await self.backup_config.find_one({"type": "atlas"}, {"_id": 0, "connection_string": 0})
        schedule = await self.backup_config.find_one({"type": "schedule"}, {"_id": 0})
        return {
            "atlas_configured": atlas is not None,
            "schedule_enabled": schedule.get("enabled", False) if schedule else False,
            "last_atlas_backup": atlas.get("last_backup") if atlas else None
        }
    
    async def log_operation(self, op_type: str, status: str, details: dict = None):
        """Log une opération de backup"""
        log_entry = {
            "type": op_type,
            "timestamp": datetime.now(timezone.utc),
            "status": status
        }
        if details:
            log_entry.update(details)
        await self.backup_logs.insert_one(log_entry)
