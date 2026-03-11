"""
Camera Engine - Dependencies
Database connection for camera module
"""
import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

_camera_db = None


def get_camera_db() -> AsyncIOMotorDatabase:
    """Get database connection for camera engine."""
    global _camera_db
    if _camera_db is None:
        MONGO_URL = os.environ.get('MONGO_URL')
        DB_NAME = os.environ.get('DB_NAME')
        if not MONGO_URL:
            raise RuntimeError("CRITICAL: MONGO_URL environment variable is not set.")
        if not DB_NAME:
            raise RuntimeError("CRITICAL: DB_NAME environment variable is not set.")
        client = AsyncIOMotorClient(MONGO_URL)
        _camera_db = client[DB_NAME]
    return _camera_db
