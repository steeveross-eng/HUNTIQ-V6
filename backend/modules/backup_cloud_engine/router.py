"""
Backup Cloud Router - API Endpoints
Version modulaire pour V5-ULTIME-FUSION
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timezone
import os
import json
import shutil
import zipfile
import tempfile
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

try:
    import resend
    RESEND_AVAILABLE = True
except ImportError:
    RESEND_AVAILABLE = False

router = APIRouter(prefix="/api/backup-cloud", tags=["backup-cloud"])

# MongoDB connections
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'bionic_db')
RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'onboarding@resend.dev')

local_client = AsyncIOMotorClient(MONGO_URL)
local_db = local_client[DB_NAME]
backup_config = local_db.backup_cloud_config
backup_logs = local_db.backup_logs

ZIP_BACKUP_DIR = "/app/backups"
os.makedirs(ZIP_BACKUP_DIR, exist_ok=True)

TRACKED_PATHS = {
    "frontend": "/app/frontend/src",
    "backend": "/app/backend"
}
TRACKED_EXTENSIONS = [".py", ".jsx", ".js", ".tsx", ".ts", ".css", ".json", ".md"]

auto_backup_running = False
auto_backup_task = None

# ==================== MODELS ====================

class AtlasConfig(BaseModel):
    connection_string: str
    database_name: Optional[str] = "huntiq_backup"
    enabled: bool = True

class GCSConfig(BaseModel):
    project_id: str
    bucket_name: str
    credentials_json: str
    enabled: bool = True

class BackupSchedule(BaseModel):
    zip_interval_minutes: int = 1
    atlas_interval_minutes: int = 60
    gcs_interval_minutes: int = 60
    enabled: bool = True

class NotificationConfig(BaseModel):
    enabled: bool = True
    recipient_email: EmailStr
    send_daily_summary: bool = True
    send_on_failure: bool = True
    summary_hour: int = 8

class ResendApiKeyConfig(BaseModel):
    api_key: str

# ==================== HELPERS ====================

async def get_resend_api_key():
    config = await backup_config.find_one({"type": "resend_api"})
    if config and config.get("api_key"):
        return config["api_key"]
    return RESEND_API_KEY

async def send_backup_email(subject: str, html_content: str, recipient: str):
    if not RESEND_AVAILABLE:
        return False
    api_key = await get_resend_api_key()
    if not api_key:
        return False
    try:
        resend.api_key = api_key
        params = {
            "from": SENDER_EMAIL,
            "to": [recipient],
            "subject": subject,
            "html": html_content
        }
        result = await asyncio.to_thread(resend.Emails.send, params)
        await backup_logs.insert_one({
            "type": "email_notification",
            "timestamp": datetime.now(timezone.utc),
            "recipient": recipient,
            "subject": subject,
            "status": "success"
        })
        return True
    except Exception as e:
        await backup_logs.insert_one({
            "type": "email_notification",
            "timestamp": datetime.now(timezone.utc),
            "status": "error",
            "error": str(e)
        })
        return False

async def create_full_backup_zip() -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = os.path.join(tempfile.gettempdir(), f"huntiq_backup_{timestamp}.zip")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for area, base_path in TRACKED_PATHS.items():
            if os.path.exists(base_path):
                for root, dirs, files in os.walk(base_path):
                    dirs[:] = [d for d in dirs if d not in ["node_modules", "__pycache__", ".git"]]
                    for file in files:
                        ext = os.path.splitext(file)[1]
                        if ext in TRACKED_EXTENSIONS:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, "/app")
                            try:
                                zipf.write(file_path, arcname)
                            except:
                                pass
        
        # MongoDB export
        try:
            collections = await local_db.list_collection_names()
            db_export = {}
            for coll_name in collections:
                if not coll_name.startswith("system."):
                    docs = await local_db[coll_name].find({}).to_list(length=None)
                    for doc in docs:
                        if "_id" in doc:
                            doc["_id"] = str(doc["_id"])
                    db_export[coll_name] = docs
            zipf.writestr("database/mongodb_export.json", json.dumps(db_export, default=str, indent=2))
        except Exception as e:
            zipf.writestr("database/export_error.txt", str(e))
        
        metadata = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "platform": "BIONIC-HUNT-V5-ULTIME-FUSION",
            "version": "5.0"
        }
        zipf.writestr("backup_metadata.json", json.dumps(metadata, indent=2))
    
    return zip_path

# ==================== ENDPOINTS ====================

@router.post("/resend/configure")
async def configure_resend_api(config: ResendApiKeyConfig):
    if not config.api_key or not config.api_key.startswith("re_"):
        raise HTTPException(status_code=400, detail="Clé API invalide")
    await backup_config.update_one(
        {"type": "resend_api"},
        {"$set": {"type": "resend_api", "api_key": config.api_key, "configured_at": datetime.now(timezone.utc)}},
        upsert=True
    )
    return {"success": True, "message": "Clé API Resend configurée"}

@router.get("/resend/status")
async def get_resend_status():
    api_key = await get_resend_api_key()
    return {"configured": bool(api_key) and api_key.startswith("re_")}

@router.post("/atlas/configure")
async def configure_atlas(config: AtlasConfig):
    try:
        test_client = AsyncIOMotorClient(config.connection_string, serverSelectionTimeoutMS=5000)
        await test_client.admin.command('ping')
        test_client.close()
        await backup_config.update_one(
            {"type": "atlas"},
            {"$set": {
                "type": "atlas",
                "connection_string": config.connection_string,
                "database_name": config.database_name,
                "enabled": config.enabled,
                "configured_at": datetime.now(timezone.utc),
                "status": "connected"
            }},
            upsert=True
        )
        return {"success": True, "message": "MongoDB Atlas configuré"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/atlas/status")
async def get_atlas_status():
    config = await backup_config.find_one({"type": "atlas"}, {"_id": 0})
    if not config:
        return {"configured": False}
    return {"configured": True, "enabled": config.get("enabled", False), "database": config.get("database_name")}

@router.post("/atlas/sync")
async def sync_to_atlas():
    config = await backup_config.find_one({"type": "atlas"})
    if not config or not config.get("enabled"):
        raise HTTPException(status_code=400, detail="Atlas non configuré")
    
    try:
        atlas_client = AsyncIOMotorClient(config["connection_string"])
        atlas_db = atlas_client[config["database_name"]]
        collection_names = await local_db.list_collection_names()
        total_docs = 0
        
        for coll_name in collection_names:
            if coll_name.startswith("system."):
                continue
            docs = await local_db[coll_name].find({}).to_list(length=None)
            if docs:
                await atlas_db[coll_name].delete_many({})
                await atlas_db[coll_name].insert_many(docs)
                total_docs += len(docs)
        
        atlas_client.close()
        await backup_logs.insert_one({"type": "atlas_sync", "timestamp": datetime.now(timezone.utc), "documents": total_docs, "status": "success"})
        await backup_config.update_one({"type": "atlas"}, {"$set": {"last_backup": datetime.now(timezone.utc)}})
        return {"success": True, "total_documents": total_docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/zip/create")
async def create_backup_zip():
    try:
        zip_path = await create_full_backup_zip()
        final_path = os.path.join(ZIP_BACKUP_DIR, os.path.basename(zip_path))
        shutil.move(zip_path, final_path)
        file_size = os.path.getsize(final_path)
        await backup_logs.insert_one({"type": "zip_create", "timestamp": datetime.now(timezone.utc), "size_bytes": file_size, "status": "success"})
        return {"success": True, "filename": os.path.basename(final_path), "size_bytes": file_size}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/zip/download/{filename}")
async def download_backup_zip(filename: str):
    file_path = os.path.join(ZIP_BACKUP_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Fichier non trouvé")
    return FileResponse(file_path, media_type="application/zip", filename=filename)

@router.get("/zip/latest")
async def get_latest_zip():
    main_zip = os.path.join(ZIP_BACKUP_DIR, "BIONIC HUNT/Chasse_BACKUP.zip")
    if os.path.exists(main_zip):
        stat = os.stat(main_zip)
        return {"exists": True, "filename": "BIONIC HUNT/Chasse_BACKUP.zip", "size_bytes": stat.st_size}
    return {"exists": False}

@router.post("/zip/update")
async def update_main_zip():
    try:
        zip_path = await create_full_backup_zip()
        main_zip = os.path.join(ZIP_BACKUP_DIR, "BIONIC HUNT/Chasse_BACKUP.zip")
        shutil.move(zip_path, main_zip)
        file_size = os.path.getsize(main_zip)
        await backup_config.update_one(
            {"type": "zip_auto"},
            {"$set": {"type": "zip_auto", "last_update": datetime.now(timezone.utc), "size_bytes": file_size}},
            upsert=True
        )
        return {"success": True, "size_bytes": file_size}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_backup_stats():
    atlas_config = await backup_config.find_one({"type": "atlas"}, {"_id": 0, "connection_string": 0})
    schedule_config = await backup_config.find_one({"type": "schedule"}, {"_id": 0})
    zip_config = await backup_config.find_one({"type": "zip_auto"}, {"_id": 0})
    return {
        "success": True,
        "atlas": atlas_config,
        "schedule": {**(schedule_config or {}), "running": auto_backup_running},
        "zip": zip_config
    }

@router.get("/logs")
async def get_backup_logs(limit: int = 50):
    logs = await backup_logs.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(length=limit)
    return {"success": True, "logs": logs}
