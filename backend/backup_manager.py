"""
Backup Manager - Real-time versioning system for prompts and code
Tracks file modifications and maintains version history like Git
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import os
import hashlib
import difflib
from motor.motor_asyncio import AsyncIOMotorClient

router = APIRouter(prefix="/api/backup", tags=["backup"])

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'bionic_db')

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Collections
prompt_versions = db.prompt_versions
code_versions = db.code_versions
backup_config = db.backup_config

# Tracked directories for code backup
TRACKED_PATHS = {
    "frontend": "/app/frontend/src",
    "backend": "/app/backend"
}

# File extensions to track
TRACKED_EXTENSIONS = [".py", ".jsx", ".js", ".tsx", ".ts", ".css", ".json"]

# Excluded patterns
EXCLUDED_PATTERNS = ["node_modules", "__pycache__", ".git", "test_", "*.pyc"]


class PromptBackup(BaseModel):
    content: dict
    message: Optional[str] = "Auto-save"


class CodeFileBackup(BaseModel):
    file_path: str
    content: str
    message: Optional[str] = "Auto-save"


def compute_hash(content: str) -> str:
    """Compute SHA256 hash of content"""
    return hashlib.sha256(content.encode()).hexdigest()[:12]


def compute_diff(old_content: str, new_content: str) -> List[str]:
    """Compute unified diff between two versions"""
    old_lines = old_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)
    diff = list(difflib.unified_diff(old_lines, new_lines, lineterm=''))
    return diff


def should_track_file(file_path: str) -> bool:
    """Check if file should be tracked based on extension and exclusions"""
    # Check extension
    ext = os.path.splitext(file_path)[1]
    if ext not in TRACKED_EXTENSIONS:
        return False
    
    # Check exclusions
    for pattern in EXCLUDED_PATTERNS:
        if pattern.replace("*", "") in file_path:
            return False
    
    return True


# ==================== PROMPT BACKUP ====================

@router.get("/prompts/versions")
async def get_prompt_versions(limit: int = 50, skip: int = 0):
    """Get version history of prompts"""
    versions = await prompt_versions.find(
        {},
        {"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(length=limit)
    
    total = await prompt_versions.count_documents({})
    
    return {
        "success": True,
        "versions": versions,
        "total": total,
        "has_more": total > skip + limit
    }


@router.get("/prompts/versions/{version_hash}")
async def get_prompt_version(version_hash: str):
    """Get specific prompt version by hash"""
    version = await prompt_versions.find_one(
        {"hash": version_hash},
        {"_id": 0}
    )
    
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    return {"success": True, "version": version}


@router.post("/prompts/save")
async def save_prompt_version(backup: PromptBackup):
    """Save new version of prompt data"""
    content_str = str(backup.content)
    new_hash = compute_hash(content_str)
    
    # Check if this exact version already exists
    existing = await prompt_versions.find_one({"hash": new_hash})
    if existing:
        return {
            "success": True,
            "message": "Version already exists",
            "hash": new_hash,
            "is_duplicate": True
        }
    
    # Get previous version for diff
    previous = await prompt_versions.find_one(
        {},
        {"_id": 0, "content": 1, "hash": 1},
        sort=[("created_at", -1)]
    )
    
    # Create new version
    version_data = {
        "hash": new_hash,
        "content": backup.content,
        "message": backup.message,
        "created_at": datetime.now(timezone.utc),
        "previous_hash": previous["hash"] if previous else None,
        "size_bytes": len(content_str)
    }
    
    await prompt_versions.insert_one(version_data)
    
    # Keep only last 100 versions
    count = await prompt_versions.count_documents({})
    if count > 100:
        oldest = await prompt_versions.find(
            {},
            {"_id": 1}
        ).sort("created_at", 1).limit(count - 100).to_list(length=count - 100)
        
        if oldest:
            await prompt_versions.delete_many(
                {"_id": {"$in": [v["_id"] for v in oldest]}}
            )
    
    return {
        "success": True,
        "message": "Prompt version saved",
        "hash": new_hash,
        "is_duplicate": False
    }


@router.post("/prompts/restore/{version_hash}")
async def restore_prompt_version(version_hash: str):
    """Restore a specific prompt version"""
    version = await prompt_versions.find_one(
        {"hash": version_hash},
        {"_id": 0}
    )
    
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    return {
        "success": True,
        "content": version["content"],
        "message": f"Restored version {version_hash}"
    }


@router.get("/prompts/diff/{old_hash}/{new_hash}")
async def get_prompt_diff(old_hash: str, new_hash: str):
    """Get diff between two prompt versions"""
    old_version = await prompt_versions.find_one({"hash": old_hash})
    new_version = await prompt_versions.find_one({"hash": new_hash})
    
    if not old_version or not new_version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    old_str = str(old_version["content"])
    new_str = str(new_version["content"])
    
    diff = compute_diff(old_str, new_str)
    
    return {
        "success": True,
        "diff": diff,
        "additions": len([line for line in diff if line.startswith('+') and not line.startswith('++')]),
        "deletions": len([line for line in diff if line.startswith('-') and not line.startswith('--')])
    }


# ==================== CODE BACKUP ====================

@router.get("/code/files")
async def get_tracked_files():
    """Get list of all tracked files with their latest version info"""
    # Get unique file paths
    pipeline = [
        {"$sort": {"created_at": -1}},
        {"$group": {
            "_id": "$file_path",
            "latest_hash": {"$first": "$hash"},
            "latest_date": {"$first": "$created_at"},
            "latest_message": {"$first": "$message"},
            "version_count": {"$sum": 1}
        }},
        {"$project": {
            "_id": 0,
            "file_path": "$_id",
            "latest_hash": 1,
            "latest_date": 1,
            "latest_message": 1,
            "version_count": 1
        }},
        {"$sort": {"latest_date": -1}}
    ]
    
    files = await code_versions.aggregate(pipeline).to_list(length=500)
    
    return {
        "success": True,
        "files": files,
        "total": len(files)
    }


@router.get("/code/versions/{file_path:path}")
async def get_code_versions(file_path: str, limit: int = 50):
    """Get version history for a specific file"""
    versions = await code_versions.find(
        {"file_path": file_path},
        {"_id": 0, "content": 0}  # Exclude content for list view
    ).sort("created_at", -1).limit(limit).to_list(length=limit)
    
    return {
        "success": True,
        "file_path": file_path,
        "versions": versions,
        "total": len(versions)
    }


@router.get("/code/version/{version_hash}")
async def get_code_version(version_hash: str):
    """Get specific code version with full content"""
    version = await code_versions.find_one(
        {"hash": version_hash},
        {"_id": 0}
    )
    
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    return {"success": True, "version": version}


@router.post("/code/save")
async def save_code_version(backup: CodeFileBackup):
    """Save new version of a code file"""
    # Validate file path
    if not should_track_file(backup.file_path):
        raise HTTPException(status_code=400, detail="File type not tracked")
    
    new_hash = compute_hash(backup.content + backup.file_path)
    
    # Check if this exact version already exists
    existing = await code_versions.find_one({
        "file_path": backup.file_path,
        "hash": new_hash
    })
    
    if existing:
        return {
            "success": True,
            "message": "Version already exists",
            "hash": new_hash,
            "is_duplicate": True
        }
    
    # Get previous version
    previous = await code_versions.find_one(
        {"file_path": backup.file_path},
        {"_id": 0, "hash": 1, "content": 1},
        sort=[("created_at", -1)]
    )
    
    # Compute diff if previous exists
    diff_stats = None
    if previous:
        diff = compute_diff(previous.get("content", ""), backup.content)
        diff_stats = {
            "additions": len([line for line in diff if line.startswith('+') and not line.startswith('++')]),
            "deletions": len([line for line in diff if line.startswith('-') and not line.startswith('--')])
        }
    
    # Create version
    version_data = {
        "hash": new_hash,
        "file_path": backup.file_path,
        "file_name": os.path.basename(backup.file_path),
        "content": backup.content,
        "message": backup.message,
        "created_at": datetime.now(timezone.utc),
        "previous_hash": previous["hash"] if previous else None,
        "size_bytes": len(backup.content),
        "lines": backup.content.count('\n') + 1,
        "diff_stats": diff_stats
    }
    
    await code_versions.insert_one(version_data)
    
    # Keep only last 50 versions per file
    count = await code_versions.count_documents({"file_path": backup.file_path})
    if count > 50:
        oldest = await code_versions.find(
            {"file_path": backup.file_path},
            {"_id": 1}
        ).sort("created_at", 1).limit(count - 50).to_list(length=count - 50)
        
        if oldest:
            await code_versions.delete_many(
                {"_id": {"$in": [v["_id"] for v in oldest]}}
            )
    
    return {
        "success": True,
        "message": "Code version saved",
        "hash": new_hash,
        "is_duplicate": False,
        "diff_stats": diff_stats
    }


@router.get("/code/diff/{old_hash}/{new_hash}")
async def get_code_diff(old_hash: str, new_hash: str):
    """Get diff between two code versions"""
    old_version = await code_versions.find_one({"hash": old_hash})
    new_version = await code_versions.find_one({"hash": new_hash})
    
    if not old_version or not new_version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    diff = compute_diff(
        old_version.get("content", ""),
        new_version.get("content", "")
    )
    
    return {
        "success": True,
        "diff": diff,
        "old_version": {
            "hash": old_hash,
            "date": old_version.get("created_at"),
            "message": old_version.get("message")
        },
        "new_version": {
            "hash": new_hash,
            "date": new_version.get("created_at"),
            "message": new_version.get("message")
        }
    }


@router.post("/code/restore/{version_hash}")
async def restore_code_version(version_hash: str):
    """Get content to restore a specific code version"""
    version = await code_versions.find_one(
        {"hash": version_hash},
        {"_id": 0}
    )
    
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    return {
        "success": True,
        "file_path": version["file_path"],
        "content": version["content"],
        "message": f"Restored from version {version_hash}"
    }


# ==================== SCAN & AUTO-BACKUP ====================

@router.post("/code/scan")
async def scan_and_backup_modified_files():
    """Scan tracked directories and backup modified files"""
    backed_up = []
    errors = []
    skipped = []
    
    for area, base_path in TRACKED_PATHS.items():
        if not os.path.exists(base_path):
            errors.append(f"Path not found: {base_path}")
            continue
        
        for root, dirs, files in os.walk(base_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in ["node_modules", "__pycache__", ".git", "tests"]]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                if not should_track_file(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check if file has changed
                    current_hash = compute_hash(content + file_path)
                    
                    existing = await code_versions.find_one({
                        "file_path": file_path,
                        "hash": current_hash
                    })
                    
                    if existing:
                        skipped.append(file_path)
                        continue
                    
                    # Get previous version for comparison
                    previous = await code_versions.find_one(
                        {"file_path": file_path},
                        sort=[("created_at", -1)]
                    )
                    
                    # Compute diff stats
                    diff_stats = None
                    if previous:
                        diff = compute_diff(previous.get("content", ""), content)
                        diff_stats = {
                            "additions": len([line for line in diff if line.startswith('+') and not line.startswith('++')]),
                            "deletions": len([line for line in diff if line.startswith('-') and not line.startswith('--')])
                        }
                    
                    # Save new version
                    version_data = {
                        "hash": current_hash,
                        "file_path": file_path,
                        "file_name": file,
                        "content": content,
                        "message": "Auto-scan backup",
                        "created_at": datetime.now(timezone.utc),
                        "previous_hash": previous["hash"] if previous else None,
                        "size_bytes": len(content),
                        "lines": content.count('\n') + 1,
                        "diff_stats": diff_stats,
                        "area": area
                    }
                    
                    await code_versions.insert_one(version_data)
                    backed_up.append({
                        "file": file_path,
                        "hash": current_hash,
                        "diff_stats": diff_stats
                    })
                    
                except Exception as e:
                    errors.append(f"{file_path}: {str(e)}")
    
    return {
        "success": True,
        "backed_up": len(backed_up),
        "skipped": len(skipped),
        "errors": len(errors),
        "details": {
            "backed_up_files": backed_up[:20],  # Limit response size
            "error_details": errors[:10]
        }
    }


# ==================== STATS ====================

@router.get("/stats")
async def get_backup_stats():
    """Get overall backup statistics"""
    prompt_count = await prompt_versions.count_documents({})
    code_file_count = len(await code_versions.distinct("file_path"))
    code_version_count = await code_versions.count_documents({})
    
    # Get latest backups
    latest_prompt = await prompt_versions.find_one(
        {},
        {"_id": 0, "hash": 1, "created_at": 1, "message": 1},
        sort=[("created_at", -1)]
    )
    
    latest_code = await code_versions.find_one(
        {},
        {"_id": 0, "hash": 1, "file_path": 1, "created_at": 1, "message": 1},
        sort=[("created_at", -1)]
    )
    
    # Get storage stats
    prompt_pipeline = [{"$group": {"_id": None, "total": {"$sum": "$size_bytes"}}}]
    code_pipeline = [{"$group": {"_id": None, "total": {"$sum": "$size_bytes"}}}]
    
    prompt_size = await prompt_versions.aggregate(prompt_pipeline).to_list(length=1)
    code_size = await code_versions.aggregate(code_pipeline).to_list(length=1)
    
    return {
        "success": True,
        "stats": {
            "prompts": {
                "version_count": prompt_count,
                "storage_bytes": prompt_size[0]["total"] if prompt_size else 0,
                "latest": latest_prompt
            },
            "code": {
                "file_count": code_file_count,
                "version_count": code_version_count,
                "storage_bytes": code_size[0]["total"] if code_size else 0,
                "latest": latest_code
            }
        }
    }


@router.delete("/clear/{backup_type}")
async def clear_backup_history(backup_type: str, keep_latest: int = 5):
    """Clear backup history keeping only latest versions"""
    if backup_type not in ["prompts", "code", "all"]:
        raise HTTPException(status_code=400, detail="Invalid backup type")
    
    deleted = {"prompts": 0, "code": 0}
    
    if backup_type in ["prompts", "all"]:
        # Keep latest N prompt versions
        to_keep = await prompt_versions.find(
            {},
            {"_id": 1}
        ).sort("created_at", -1).limit(keep_latest).to_list(length=keep_latest)
        
        keep_ids = [v["_id"] for v in to_keep]
        result = await prompt_versions.delete_many({"_id": {"$nin": keep_ids}})
        deleted["prompts"] = result.deleted_count
    
    if backup_type in ["code", "all"]:
        # Keep latest N versions per file
        files = await code_versions.distinct("file_path")
        for file_path in files:
            to_keep = await code_versions.find(
                {"file_path": file_path},
                {"_id": 1}
            ).sort("created_at", -1).limit(keep_latest).to_list(length=keep_latest)
            
            keep_ids = [v["_id"] for v in to_keep]
            result = await code_versions.delete_many({
                "file_path": file_path,
                "_id": {"$nin": keep_ids}
            })
            deleted["code"] += result.deleted_count
    
    return {
        "success": True,
        "deleted": deleted,
        "kept_per_item": keep_latest
    }
