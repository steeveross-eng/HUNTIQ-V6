"""
Territory Module - Base (routers, DB, config)
Phase 1.8 - Split from territory.py
"""
import os
import uuid
import json
import base64
import hashlib
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Literal
from pathlib import Path
from enum import Enum

import aiofiles
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks, Request, Query
from pydantic import BaseModel, Field
import exifread
from io import BytesIO
from motor.motor_asyncio import AsyncIOMotorClient

from dotenv import load_dotenv
load_dotenv()

# Routers
territory_router = APIRouter(prefix="/api/territory", tags=["Territory Analysis"])
territories_router = APIRouter(prefix="/api/territories", tags=["Territory Inventory"])

# Database connection
mongo_client: Optional[AsyncIOMotorClient] = None
db = None

# Configuration
MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'huntiq')
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')
UPLOAD_DIR = Path("/app/backend/uploads/photos")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)


async def get_db():
    """Get or create MongoDB connection"""
    global mongo_client, db
    if mongo_client is None:
        mongo_client = AsyncIOMotorClient(MONGO_URL)
        db = mongo_client[DB_NAME]
        await db.territory_users.create_index("email", unique=True)
        await db.territory_events.create_index([("user_id", 1), ("captured_at", -1)])
        await db.territory_events.create_index([("latitude", 1), ("longitude", 1)])
        await db.territory_cameras.create_index("user_id")
        await db.territory_photos.create_index("user_id")
    return db


async def close_db():
    """Close MongoDB connection"""
    global mongo_client, db
    if mongo_client:
        mongo_client.close()
        mongo_client = None
        db = None


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points using Haversine formula (returns km)"""
    import math
    R = 6371
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c


async def init_territory_module():
    """Initialize the territory analysis module"""
    await get_db()
    logger.info("Territory analysis module initialized with MongoDB")


async def shutdown_territory_module():
    """Shutdown the territory analysis module"""
    await close_db()
    logger.info("Territory analysis module shut down")
