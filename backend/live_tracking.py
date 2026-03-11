"""
Live Tracking System - Suivi en temps réel des chasseurs BIONIC
- Tracking continu ou manuel avec toggle ON/OFF
- Positions des membres du groupe sur carte
- Historique des trajets
- Calcul de distances
"""

from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
import math
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tracking", tags=["Live Tracking"])

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'hunttrack')

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Collections
tracking_sessions_collection = db['tracking_sessions']
position_history_collection = db['position_history']
groups_collection = db['hunting_groups']
users_collection = db['users']

# WebSocket connections storage
active_connections: Dict[str, Dict[str, WebSocket]] = {}  # group_id -> {user_id: websocket}


# ============================================
# PYDANTIC MODELS
# ============================================

class PositionUpdate(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    accuracy: Optional[float] = None
    altitude: Optional[float] = None
    heading: Optional[float] = None
    speed: Optional[float] = None


class TrackingSettings(BaseModel):
    mode: str = Field(default="auto", pattern="^(auto|manual)$")  # auto = continu, manual = bouton
    share_exact_position: bool = Field(default=True)
    update_interval: int = Field(default=30, ge=10, le=300)  # secondes


class SessionStart(BaseModel):
    group_id: str
    settings: Optional[TrackingSettings] = None


class MemberPosition(BaseModel):
    user_id: str
    name: str
    lat: float
    lng: float
    accuracy: Optional[float] = None
    heading: Optional[float] = None
    last_update: str
    is_online: bool
    distance_km: Optional[float] = None


class TrackingSession(BaseModel):
    id: str
    user_id: str
    group_id: str
    is_active: bool
    mode: str
    started_at: str
    last_position: Optional[Dict] = None
    settings: Dict


# ============================================
# HELPER FUNCTIONS
# ============================================

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcule la distance en km entre deux points (formule Haversine)"""
    R = 6371  # Rayon de la Terre en km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


async def get_user_info(user_id: str) -> dict:
    """Récupère les infos basiques d'un utilisateur"""
    user = await users_collection.find_one(
        {"id": user_id},
        {"_id": 0, "id": 1, "name": 1, "first_name": 1, "last_name": 1}
    )
    if user:
        name = user.get("name") or f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or "Chasseur"
        return {"id": user.get("id"), "name": name}
    return {"id": user_id, "name": "Chasseur BIONIC"}


async def broadcast_to_group(group_id: str, message: dict, exclude_user: str = None):
    """Envoie un message à tous les membres connectés d'un groupe"""
    if group_id in active_connections:
        for user_id, ws in active_connections[group_id].items():
            if user_id != exclude_user:
                try:
                    await ws.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to {user_id}: {e}")


def serialize_session(doc: dict) -> dict:
    """Sérialise une session de tracking"""
    return {
        "id": str(doc.get("_id", "")),
        "user_id": doc.get("user_id", ""),
        "group_id": doc.get("group_id", ""),
        "is_active": doc.get("is_active", False),
        "mode": doc.get("mode", "auto"),
        "started_at": doc.get("started_at", ""),
        "ended_at": doc.get("ended_at"),
        "last_position": doc.get("last_position"),
        "settings": doc.get("settings", {})
    }


# ============================================
# SESSION MANAGEMENT
# ============================================

@router.post("/session/start/{user_id}")
async def start_tracking_session(user_id: str, session: SessionStart):
    """Démarre une session de tracking pour un utilisateur dans un groupe"""
    try:
        # Vérifier que l'utilisateur est membre du groupe
        group = await groups_collection.find_one({"_id": ObjectId(session.group_id)})
        if not group:
            raise HTTPException(status_code=404, detail="Groupe non trouvé")
        
        is_member = any(m.get("user_id") == user_id for m in group.get("members", []))
        if not is_member:
            raise HTTPException(status_code=403, detail="Vous n'êtes pas membre de ce groupe")
        
        # Terminer toute session active existante
        await tracking_sessions_collection.update_many(
            {"user_id": user_id, "is_active": True},
            {"$set": {"is_active": False, "ended_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        now = datetime.now(timezone.utc).isoformat()
        settings = session.settings or TrackingSettings()
        
        session_doc = {
            "user_id": user_id,
            "group_id": session.group_id,
            "is_active": True,
            "mode": settings.mode,
            "started_at": now,
            "ended_at": None,
            "last_position": None,
            "settings": {
                "mode": settings.mode,
                "share_exact_position": settings.share_exact_position,
                "update_interval": settings.update_interval
            },
            "position_count": 0
        }
        
        result = await tracking_sessions_collection.insert_one(session_doc)
        session_doc["_id"] = result.inserted_id
        
        user_info = await get_user_info(user_id)
        
        # Notifier le groupe
        await broadcast_to_group(session.group_id, {
            "type": "member_started_tracking",
            "user_id": user_id,
            "user_name": user_info.get("name"),
            "timestamp": now
        })
        
        logger.info(f"Tracking session started for {user_id} in group {session.group_id}")
        
        return {
            "success": True,
            "session": serialize_session(session_doc),
            "message": "Session de tracking démarrée"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting tracking session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session/stop/{user_id}")
async def stop_tracking_session(user_id: str, group_id: str = Query(...)):
    """Arrête la session de tracking active"""
    try:
        now = datetime.now(timezone.utc).isoformat()
        
        result = await tracking_sessions_collection.update_one(
            {"user_id": user_id, "group_id": group_id, "is_active": True},
            {"$set": {"is_active": False, "ended_at": now}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Aucune session active trouvée")
        
        user_info = await get_user_info(user_id)
        
        # Notifier le groupe
        await broadcast_to_group(group_id, {
            "type": "member_stopped_tracking",
            "user_id": user_id,
            "user_name": user_info.get("name"),
            "timestamp": now
        })
        
        return {"success": True, "message": "Session de tracking arrêtée"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping tracking session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/status/{user_id}")
async def get_session_status(user_id: str, group_id: str = Query(...)):
    """Récupère le statut de la session de tracking"""
    try:
        session = await tracking_sessions_collection.find_one({
            "user_id": user_id,
            "group_id": group_id,
            "is_active": True
        })
        
        if not session:
            return {"is_active": False, "session": None}
        
        return {
            "is_active": True,
            "session": serialize_session(session)
        }
        
    except Exception as e:
        logger.error(f"Error getting session status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# POSITION UPDATES
# ============================================

@router.post("/position/{user_id}")
async def update_position(user_id: str, group_id: str, position: PositionUpdate):
    """Met à jour la position d'un utilisateur"""
    try:
        now = datetime.now(timezone.utc).isoformat()
        
        # Vérifier session active
        session = await tracking_sessions_collection.find_one({
            "user_id": user_id,
            "group_id": group_id,
            "is_active": True
        })
        
        if not session:
            raise HTTPException(status_code=400, detail="Aucune session de tracking active")
        
        position_data = {
            "lat": position.lat,
            "lng": position.lng,
            "accuracy": position.accuracy,
            "altitude": position.altitude,
            "heading": position.heading,
            "speed": position.speed,
            "timestamp": now
        }
        
        # Si position approximative configurée, arrondir les coordonnées
        if not session.get("settings", {}).get("share_exact_position", True):
            position_data["lat"] = round(position.lat, 3)  # ~111m de précision
            position_data["lng"] = round(position.lng, 3)
        
        # Mettre à jour la session
        await tracking_sessions_collection.update_one(
            {"_id": session["_id"]},
            {
                "$set": {"last_position": position_data},
                "$inc": {"position_count": 1}
            }
        )
        
        # Sauvegarder dans l'historique
        history_doc = {
            "session_id": str(session["_id"]),
            "user_id": user_id,
            "group_id": group_id,
            **position_data
        }
        await position_history_collection.insert_one(history_doc)
        
        user_info = await get_user_info(user_id)
        
        # Broadcast aux membres du groupe
        await broadcast_to_group(group_id, {
            "type": "position_update",
            "user_id": user_id,
            "user_name": user_info.get("name"),
            "position": position_data
        }, exclude_user=user_id)
        
        return {"success": True, "timestamp": now}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating position: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# GROUP POSITIONS
# ============================================

@router.get("/group/{group_id}/positions")
async def get_group_positions(
    group_id: str,
    user_id: str = Query(..., description="ID de l'utilisateur qui demande")
):
    """Récupère les positions de tous les membres du groupe"""
    try:
        # Vérifier l'appartenance au groupe
        group = await groups_collection.find_one({"_id": ObjectId(group_id)})
        if not group:
            raise HTTPException(status_code=404, detail="Groupe non trouvé")
        
        is_member = any(m.get("user_id") == user_id for m in group.get("members", []))
        if not is_member:
            raise HTTPException(status_code=403, detail="Vous n'êtes pas membre de ce groupe")
        
        # Récupérer la position de l'utilisateur demandeur
        user_session = await tracking_sessions_collection.find_one({
            "user_id": user_id,
            "group_id": group_id,
            "is_active": True
        })
        user_position = user_session.get("last_position") if user_session else None
        
        # Récupérer les sessions actives du groupe
        cursor = tracking_sessions_collection.find({
            "group_id": group_id,
            "is_active": True
        })
        sessions = await cursor.to_list(length=50)
        
        # Construire la liste des positions
        members_positions = []
        online_timeout = datetime.now(timezone.utc) - timedelta(minutes=5)
        
        for session in sessions:
            last_pos = session.get("last_position")
            if not last_pos:
                continue
            
            user_info = await get_user_info(session.get("user_id"))
            
            # Vérifier si en ligne (dernière mise à jour < 5 min)
            last_update = datetime.fromisoformat(last_pos.get("timestamp", "").replace("Z", "+00:00"))
            is_online = last_update > online_timeout
            
            # Calculer la distance si on a la position de l'utilisateur
            distance_km = None
            if user_position and session.get("user_id") != user_id:
                distance_km = calculate_distance(
                    user_position.get("lat", 0),
                    user_position.get("lng", 0),
                    last_pos.get("lat", 0),
                    last_pos.get("lng", 0)
                )
            
            members_positions.append({
                "user_id": session.get("user_id"),
                "name": user_info.get("name"),
                "lat": last_pos.get("lat"),
                "lng": last_pos.get("lng"),
                "accuracy": last_pos.get("accuracy"),
                "heading": last_pos.get("heading"),
                "speed": last_pos.get("speed"),
                "last_update": last_pos.get("timestamp"),
                "is_online": is_online,
                "distance_km": round(distance_km, 2) if distance_km else None
            })
        
        return {
            "group_id": group_id,
            "group_name": group.get("name"),
            "members": members_positions,
            "total_tracking": len(members_positions),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting group positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# POSITION HISTORY (TRAJET)
# ============================================

@router.get("/history/{user_id}")
async def get_position_history(
    user_id: str,
    group_id: str = Query(...),
    session_id: Optional[str] = Query(None),
    hours: int = Query(6, ge=1, le=24)
):
    """Récupère l'historique des positions (trajet parcouru)"""
    try:
        # Construire la requête
        query = {
            "user_id": user_id,
            "group_id": group_id
        }
        
        if session_id:
            query["session_id"] = session_id
        else:
            # Dernières X heures
            since = datetime.now(timezone.utc) - timedelta(hours=hours)
            query["timestamp"] = {"$gte": since.isoformat()}
        
        cursor = position_history_collection.find(
            query,
            {"_id": 0, "lat": 1, "lng": 1, "timestamp": 1, "speed": 1, "heading": 1}
        ).sort("timestamp", 1).limit(1000)
        
        positions = await cursor.to_list(length=1000)
        
        # Calculer la distance totale parcourue
        total_distance = 0
        for i in range(1, len(positions)):
            total_distance += calculate_distance(
                positions[i-1]["lat"], positions[i-1]["lng"],
                positions[i]["lat"], positions[i]["lng"]
            )
        
        return {
            "user_id": user_id,
            "positions": positions,
            "total_points": len(positions),
            "total_distance_km": round(total_distance, 2),
            "period_hours": hours
        }
        
    except Exception as e:
        logger.error(f"Error getting position history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# TRACKING SETTINGS
# ============================================

@router.put("/settings/{user_id}")
async def update_tracking_settings(
    user_id: str,
    group_id: str,
    settings: TrackingSettings
):
    """Met à jour les paramètres de tracking"""
    try:
        result = await tracking_sessions_collection.update_one(
            {"user_id": user_id, "group_id": group_id, "is_active": True},
            {"$set": {
                "mode": settings.mode,
                "settings": {
                    "mode": settings.mode,
                    "share_exact_position": settings.share_exact_position,
                    "update_interval": settings.update_interval
                }
            }}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Session non trouvée")
        
        return {"success": True, "settings": settings.model_dump()}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# WEBSOCKET FOR REAL-TIME UPDATES
# ============================================

@router.websocket("/ws/{group_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, group_id: str, user_id: str):
    """WebSocket pour les mises à jour en temps réel"""
    await websocket.accept()
    
    # Enregistrer la connexion
    if group_id not in active_connections:
        active_connections[group_id] = {}
    active_connections[group_id][user_id] = websocket
    
    user_info = await get_user_info(user_id)
    
    # Notifier le groupe de la connexion
    await broadcast_to_group(group_id, {
        "type": "member_connected",
        "user_id": user_id,
        "user_name": user_info.get("name"),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }, exclude_user=user_id)
    
    try:
        while True:
            # Recevoir les messages du client
            data = await websocket.receive_json()
            
            if data.get("type") == "position":
                # Mise à jour de position via WebSocket
                position = PositionUpdate(**data.get("position", {}))
                # Traiter comme une mise à jour normale
                # (On pourrait appeler update_position directement mais on broadcast ici)
                await broadcast_to_group(group_id, {
                    "type": "position_update",
                    "user_id": user_id,
                    "user_name": user_info.get("name"),
                    "position": {
                        "lat": position.lat,
                        "lng": position.lng,
                        "accuracy": position.accuracy,
                        "heading": position.heading,
                        "speed": position.speed,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                }, exclude_user=user_id)
                
            elif data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
                
    except WebSocketDisconnect:
        # Retirer la connexion
        if group_id in active_connections:
            active_connections[group_id].pop(user_id, None)
            if not active_connections[group_id]:
                del active_connections[group_id]
        
        # Notifier le groupe de la déconnexion
        await broadcast_to_group(group_id, {
            "type": "member_disconnected",
            "user_id": user_id,
            "user_name": user_info.get("name"),
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        logger.error(f"WebSocket error: {e}")


# ============================================
# GROUP TRACKING STATS
# ============================================

@router.get("/stats/{group_id}")
async def get_group_tracking_stats(group_id: str):
    """Statistiques de tracking du groupe"""
    try:
        # Sessions actives
        active_sessions = await tracking_sessions_collection.count_documents({
            "group_id": group_id,
            "is_active": True
        })
        
        # Total de sessions
        total_sessions = await tracking_sessions_collection.count_documents({
            "group_id": group_id
        })
        
        # Points de position total
        pipeline = [
            {"$match": {"group_id": group_id}},
            {"$group": {"_id": None, "total": {"$sum": "$position_count"}}}
        ]
        result = await tracking_sessions_collection.aggregate(pipeline).to_list(length=1)
        total_positions = result[0]["total"] if result else 0
        
        return {
            "group_id": group_id,
            "active_sessions": active_sessions,
            "total_sessions": total_sessions,
            "total_positions_recorded": total_positions
        }
        
    except Exception as e:
        logger.error(f"Error getting tracking stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
