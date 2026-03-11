"""
Backup Admin Service - V5-ULTIME Administration Premium
=======================================================

Service d'administration des sauvegardes pour:
- Backup MongoDB (collections, données)
- Versioning de code
- Historique des prompts
- Restauration

Module isolé - aucun import croisé.
Phase 2 Migration.
"""

from datetime import datetime, timezone
from typing import Optional
import logging
import uuid

logger = logging.getLogger(__name__)


class BackupAdminService:
    """Service isolé pour l'administration des backups"""
    
    # ============ BACKUP STATS ============
    @staticmethod
    async def get_backup_stats(db) -> dict:
        """Statistiques globales des backups"""
        # Code files tracked
        code_files = await db.code_backups.count_documents({})
        
        # Prompt versions
        prompt_versions = await db.prompt_versions.count_documents({})
        
        # DB backups
        db_backups = await db.db_backups.count_documents({})
        
        # Last backup
        last_backup = await db.db_backups.find_one(
            {}, {"_id": 0, "created_at": 1, "size": 1, "status": 1}
        )
        
        # Total size (approximation)
        backups = await db.db_backups.find(
            {}, {"size": 1, "_id": 0}
        ).to_list(length=1000)
        total_size = sum(b.get("size", 0) for b in backups)
        
        return {
            "success": True,
            "stats": {
                "code_files_tracked": code_files,
                "prompt_versions": prompt_versions,
                "db_backups_count": db_backups,
                "total_backup_size": total_size,
                "last_backup": last_backup
            }
        }
    
    # ============ CODE BACKUPS ============
    @staticmethod
    async def get_code_files(db, search: Optional[str] = None, limit: int = 50) -> dict:
        """Liste les fichiers de code suivis"""
        query = {}
        if search:
            query["file_path"] = {"$regex": search, "$options": "i"}
        
        files = await db.code_backups.find(
            query, {"_id": 0}
        ).sort("updated_at", -1).limit(limit).to_list(length=limit)
        
        total = await db.code_backups.count_documents(query)
        
        return {
            "success": True,
            "total": total,
            "files": files
        }
    
    @staticmethod
    async def get_file_versions(db, file_path: str, limit: int = 20) -> dict:
        """Récupérer les versions d'un fichier"""
        versions = await db.code_versions.find(
            {"file_path": file_path},
            {"_id": 0}
        ).sort("version", -1).limit(limit).to_list(length=limit)
        
        return {
            "success": True,
            "file_path": file_path,
            "total_versions": len(versions),
            "versions": versions
        }
    
    @staticmethod
    async def create_code_backup(db, file_path: str, content: str, commit_message: str = "") -> dict:
        """Créer une nouvelle version d'un fichier"""
        # Récupérer la dernière version
        last_version = await db.code_versions.find_one(
            {"file_path": file_path},
            sort=[("version", -1)]
        )
        
        new_version = (last_version.get("version", 0) if last_version else 0) + 1
        
        version_doc = {
            "id": str(uuid.uuid4()),
            "file_path": file_path,
            "version": new_version,
            "content": content,
            "size": len(content.encode('utf-8')),
            "commit_message": commit_message or f"Version {new_version}",
            "created_at": datetime.now(timezone.utc)
        }
        
        await db.code_versions.insert_one(version_doc)
        
        # Mettre à jour le tracker de fichier
        await db.code_backups.update_one(
            {"file_path": file_path},
            {
                "$set": {
                    "file_path": file_path,
                    "latest_version": new_version,
                    "size": len(content.encode('utf-8')),
                    "updated_at": datetime.now(timezone.utc)
                },
                "$inc": {"total_versions": 1}
            },
            upsert=True
        )
        
        version_doc.pop("_id", None)
        
        return {"success": True, "version": version_doc}
    
    @staticmethod
    async def restore_version(db, file_path: str, version: int) -> dict:
        """Restaurer une version spécifique"""
        version_doc = await db.code_versions.find_one(
            {"file_path": file_path, "version": version},
            {"_id": 0}
        )
        
        if not version_doc:
            return {"success": False, "error": "Version not found"}
        
        return {
            "success": True,
            "file_path": file_path,
            "version": version,
            "content": version_doc.get("content", ""),
            "restored_at": datetime.now(timezone.utc).isoformat()
        }
    
    # ============ PROMPT BACKUPS ============
    @staticmethod
    async def get_prompt_versions(db, prompt_type: Optional[str] = None, limit: int = 50) -> dict:
        """Liste les versions de prompts"""
        query = {}
        if prompt_type:
            query["prompt_type"] = prompt_type
        
        versions = await db.prompt_versions.find(
            query, {"_id": 0, "content": 0}  # Exclure le contenu pour la liste
        ).sort("created_at", -1).limit(limit).to_list(length=limit)
        
        # Types distincts
        prompt_types = await db.prompt_versions.distinct("prompt_type")
        
        return {
            "success": True,
            "total": len(versions),
            "prompt_types": prompt_types,
            "versions": versions
        }
    
    @staticmethod
    async def get_prompt_version_detail(db, version_id: str) -> dict:
        """Détail d'une version de prompt"""
        version = await db.prompt_versions.find_one(
            {"id": version_id},
            {"_id": 0}
        )
        
        if not version:
            return {"success": False, "error": "Version not found"}
        
        return {"success": True, "version": version}
    
    @staticmethod
    async def save_prompt_version(db, prompt_type: str, content: str, metadata: dict = None) -> dict:
        """Sauvegarder une nouvelle version de prompt"""
        # Compter les versions existantes
        count = await db.prompt_versions.count_documents({"prompt_type": prompt_type})
        
        version_doc = {
            "id": str(uuid.uuid4()),
            "prompt_type": prompt_type,
            "version": count + 1,
            "content": content,
            "metadata": metadata or {},
            "created_at": datetime.now(timezone.utc)
        }
        
        await db.prompt_versions.insert_one(version_doc)
        version_doc.pop("_id", None)
        
        return {"success": True, "version": version_doc}
    
    # ============ DATABASE BACKUPS ============
    @staticmethod
    async def get_db_backups(db, limit: int = 20) -> dict:
        """Liste les backups de base de données"""
        backups = await db.db_backups.find(
            {}, {"_id": 0}
        ).sort("created_at", -1).limit(limit).to_list(length=limit)
        
        return {
            "success": True,
            "total": len(backups),
            "backups": backups
        }
    
    @staticmethod
    async def create_db_backup(db, backup_type: str = "manual", description: str = "") -> dict:
        """Créer un backup de base de données (métadonnées)"""
        # Note: Le backup réel serait géré par un service externe (mongodump, GCS, etc.)
        # Ici on enregistre les métadonnées
        
        backup_doc = {
            "id": str(uuid.uuid4()),
            "backup_type": backup_type,
            "description": description or f"Backup {backup_type}",
            "status": "pending",
            "collections": [],
            "size": 0,
            "created_at": datetime.now(timezone.utc)
        }
        
        # Simuler la collecte d'infos sur les collections
        collections = await db.list_collection_names()
        backup_doc["collections"] = collections
        backup_doc["status"] = "completed"
        
        await db.db_backups.insert_one(backup_doc)
        backup_doc.pop("_id", None)
        
        return {"success": True, "backup": backup_doc}
    
    @staticmethod
    async def delete_db_backup(db, backup_id: str) -> dict:
        """Supprimer un backup"""
        result = await db.db_backups.delete_one({"id": backup_id})
        
        if result.deleted_count == 0:
            return {"success": False, "error": "Backup not found"}
        
        return {"success": True, "backup_id": backup_id, "deleted": True}
