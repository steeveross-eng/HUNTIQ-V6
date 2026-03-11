"""
Territory Module - Users & Cameras API
Phase 1.8 - Split from territory.py
"""
import uuid
import hashlib
from datetime import datetime, timezone

from fastapi import HTTPException, Request

from ._base import territory_router, get_db, logger
from .models import (
    UserCreate, UserResponse, UserLogin,
    CameraCreate, CameraResponse,
)


@territory_router.get("/users/auto-login")
async def auto_login_by_ip(request: Request):
    """Auto-login or create user based on IP address"""
    database = await get_db()
    client_ip = request.client.host
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
    ip_hash = hashlib.sha256(client_ip.encode()).hexdigest()[:16]
    auto_email = f"user_{ip_hash}@territory.local"
    existing = await database.territory_users.find_one({"email": auto_email})
    if existing:
        return {
            "id": str(existing['_id']),
            "email": existing['email'],
            "name": existing.get('name') or f"Utilisateur {ip_hash[:6]}",
            "plan_type": existing.get('plan_type', 'free'),
            "created_at": existing.get('created_at', datetime.now(timezone.utc)),
            "auto_created": False,
            "client_ip": client_ip
        }
    else:
        user_id = str(uuid.uuid4())
        user_name = f"Chasseur {ip_hash[:6].upper()}"
        now = datetime.now(timezone.utc)
        new_user = {
            "_id": user_id,
            "email": auto_email,
            "password_hash": ip_hash,
            "name": user_name,
            "plan_type": "free",
            "created_at": now
        }
        await database.territory_users.insert_one(new_user)
        return {
            "id": user_id,
            "email": auto_email,
            "name": user_name,
            "plan_type": "free",
            "created_at": now,
            "auto_created": True,
            "client_ip": client_ip
        }


@territory_router.post("/users/login")
async def login_user(credentials: UserLogin):
    """Login existing user or create new one"""
    database = await get_db()
    password_hash = hashlib.sha256(credentials.password.encode()).hexdigest()
    existing = await database.territory_users.find_one({"email": credentials.email})
    if existing:
        if existing.get('password_hash') == password_hash:
            return UserResponse(
                id=str(existing['_id']),
                email=existing['email'],
                name=existing.get('name'),
                plan_type=existing.get('plan_type', 'free'),
                created_at=existing.get('created_at', datetime.now(timezone.utc))
            )
        else:
            raise HTTPException(status_code=401, detail="Mot de passe incorrect")
    else:
        user_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        new_user = {
            "_id": user_id,
            "email": credentials.email,
            "password_hash": password_hash,
            "name": credentials.email.split('@')[0],
            "plan_type": "free",
            "created_at": now
        }
        await database.territory_users.insert_one(new_user)
        return UserResponse(
            id=user_id,
            email=credentials.email,
            name=credentials.email.split('@')[0],
            plan_type="free",
            created_at=now
        )


@territory_router.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate):
    """Create a new user for territory analysis"""
    database = await get_db()
    password_hash = hashlib.sha256(user.password.encode()).hexdigest()
    existing = await database.territory_users.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    new_user = {
        "_id": user_id,
        "email": user.email,
        "password_hash": password_hash,
        "name": user.name,
        "plan_type": "free",
        "created_at": now
    }
    await database.territory_users.insert_one(new_user)
    return UserResponse(id=user_id, email=user.email, name=user.name, plan_type="free", created_at=now)


@territory_router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get user by ID"""
    database = await get_db()
    user = await database.territory_users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(
        id=str(user['_id']),
        email=user['email'],
        name=user.get('name'),
        plan_type=user.get('plan_type', 'free'),
        created_at=user.get('created_at', datetime.now(timezone.utc))
    )


# --- CAMERAS ---

@territory_router.get("/cameras")
async def list_cameras(user_id: str):
    """List all cameras for a user"""
    database = await get_db()
    cameras = await database.territory_cameras.find({"user_id": user_id}).sort("created_at", -1).to_list(100)
    return [CameraResponse(
        id=str(cam['_id']), label=cam['label'], brand=cam['brand'],
        connection_type=cam['connection_type'], connected=cam.get('connected', False),
        last_seen_at=cam.get('last_seen_at'), latitude=cam.get('latitude'), longitude=cam.get('longitude')
    ) for cam in cameras]


@territory_router.post("/cameras", response_model=CameraResponse)
async def create_camera(user_id: str, camera: CameraCreate):
    """Register a new trail camera"""
    database = await get_db()
    camera_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    camera_doc = {
        "_id": camera_id, "user_id": user_id, "label": camera.label,
        "brand": camera.brand, "connection_type": camera.connection_type,
        "ftp_host": camera.ftp_host, "ftp_username": camera.ftp_username,
        "ftp_password": camera.ftp_password, "ftp_path": camera.ftp_path,
        "email_address": camera.email_address, "latitude": camera.latitude,
        "longitude": camera.longitude, "connected": False, "last_seen_at": None, "created_at": now
    }
    await database.territory_cameras.insert_one(camera_doc)
    return CameraResponse(
        id=camera_id, label=camera.label, brand=camera.brand,
        connection_type=camera.connection_type, connected=False,
        last_seen_at=None, latitude=camera.latitude, longitude=camera.longitude
    )


@territory_router.get("/cameras/{camera_id}/status")
async def get_camera_status(camera_id: str):
    """Get camera connection status"""
    database = await get_db()
    camera = await database.territory_cameras.find_one({"_id": camera_id})
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    total_photos = await database.territory_photos.count_documents({"camera_id": camera_id})
    last_photo = await database.territory_photos.find_one({"camera_id": camera_id}, sort=[("captured_at", -1)])
    return {
        "id": str(camera['_id']), "label": camera['label'],
        "connected": camera.get('connected', False), "last_seen_at": camera.get('last_seen_at'),
        "total_photos": total_photos,
        "last_photo_at": last_photo.get('captured_at') if last_photo else None
    }
