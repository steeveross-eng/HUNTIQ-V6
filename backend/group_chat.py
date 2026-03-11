"""
Group Chat System - Chat en temps réel pour les groupes de chasse BIONIC
- Messages texte
- Alertes avec vibration
- Emojis prédéfinis pour la chasse
- Historique des messages
"""

from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["Group Chat"])

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'hunttrack')

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Collections
messages_collection = db['chat_messages']
groups_collection = db['hunting_groups']
users_collection = db['users']
notifications_collection = db['notifications']

# WebSocket connections
chat_connections: Dict[str, Dict[str, WebSocket]] = {}


# ============================================
# ALERT TYPES & EMOJIS
# ============================================

ALERT_TYPES = {
    "animal_spotted": {
        "emoji": "🦌",
        "label": "Animal repéré",
        "vibrate": True,
        "priority": "high"
    },
    "position_marked": {
        "emoji": "📍",
        "label": "Position marquée",
        "vibrate": False,
        "priority": "normal"
    },
    "need_help": {
        "emoji": "🆘",
        "label": "Besoin d'aide",
        "vibrate": True,
        "priority": "urgent"
    },
    "shot_fired": {
        "emoji": "🎯",
        "label": "Tir effectué",
        "vibrate": True,
        "priority": "high"
    },
    "returning": {
        "emoji": "🏠",
        "label": "Je rentre",
        "vibrate": False,
        "priority": "normal"
    },
    "break_time": {
        "emoji": "☕",
        "label": "Pause",
        "vibrate": False,
        "priority": "low"
    },
    "silence": {
        "emoji": "🤫",
        "label": "Silence requis",
        "vibrate": True,
        "priority": "high"
    },
    "meeting_point": {
        "emoji": "🤝",
        "label": "Point de rencontre",
        "vibrate": True,
        "priority": "normal"
    }
}

QUICK_MESSAGES = [
    {"text": "OK 👍", "emoji": "👍"},
    {"text": "J'arrive", "emoji": "🏃"},
    {"text": "Attendez-moi", "emoji": "✋"},
    {"text": "Bien reçu", "emoji": "✅"},
    {"text": "Négatif", "emoji": "❌"},
    {"text": "En position", "emoji": "📍"},
    {"text": "Rien vu", "emoji": "👀"},
    {"text": "Du mouvement", "emoji": "🦌"}
]


# ============================================
# PYDANTIC MODELS
# ============================================

class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=500)
    message_type: str = Field(default="text", pattern="^(text|alert|location)$")
    alert_type: Optional[str] = None
    location: Optional[Dict[str, float]] = None  # {lat, lng}


class AlertCreate(BaseModel):
    alert_type: str
    message: Optional[str] = None
    location: Optional[Dict[str, float]] = None


class Message(BaseModel):
    id: str
    group_id: str
    sender_id: str
    sender_name: str
    content: str
    message_type: str
    alert_type: Optional[str] = None
    alert_info: Optional[Dict] = None
    location: Optional[Dict] = None
    created_at: str
    read_by: List[str] = []


# ============================================
# HELPER FUNCTIONS
# ============================================

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
    if group_id in chat_connections:
        for user_id, ws in chat_connections[group_id].items():
            if user_id != exclude_user:
                try:
                    await ws.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to {user_id}: {e}")


async def create_notification(user_id: str, notif_type: str, title: str, message: str, data: dict = None):
    """Crée une notification"""
    try:
        await notifications_collection.insert_one({
            "user_id": user_id,
            "type": notif_type,
            "title": title,
            "message": message,
            "data": data or {},
            "read": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
    except Exception as e:
        logger.error(f"Error creating notification: {e}")


def serialize_message(doc: dict) -> dict:
    """Sérialise un message"""
    return {
        "id": str(doc.get("_id", "")),
        "group_id": doc.get("group_id", ""),
        "sender_id": doc.get("sender_id", ""),
        "sender_name": doc.get("sender_name", ""),
        "content": doc.get("content", ""),
        "message_type": doc.get("message_type", "text"),
        "alert_type": doc.get("alert_type"),
        "alert_info": doc.get("alert_info"),
        "location": doc.get("location"),
        "created_at": doc.get("created_at", ""),
        "read_by": doc.get("read_by", [])
    }


# ============================================
# MESSAGE ENDPOINTS
# ============================================

@router.post("/{group_id}/message/{user_id}")
async def send_message(group_id: str, user_id: str, message: MessageCreate):
    """Envoie un message dans le chat du groupe"""
    try:
        # Vérifier l'appartenance au groupe
        group = await groups_collection.find_one({"_id": ObjectId(group_id)})
        if not group:
            raise HTTPException(status_code=404, detail="Groupe non trouvé")
        
        is_member = any(m.get("user_id") == user_id for m in group.get("members", []))
        if not is_member:
            raise HTTPException(status_code=403, detail="Vous n'êtes pas membre de ce groupe")
        
        user_info = await get_user_info(user_id)
        now = datetime.now(timezone.utc).isoformat()
        
        # Préparer le message
        msg_doc = {
            "group_id": group_id,
            "sender_id": user_id,
            "sender_name": user_info.get("name"),
            "content": message.content,
            "message_type": message.message_type,
            "alert_type": message.alert_type,
            "alert_info": ALERT_TYPES.get(message.alert_type) if message.alert_type else None,
            "location": message.location,
            "created_at": now,
            "read_by": [user_id]
        }
        
        result = await messages_collection.insert_one(msg_doc)
        msg_doc["_id"] = result.inserted_id
        
        serialized = serialize_message(msg_doc)
        
        # Broadcast au groupe
        await broadcast_to_group(group_id, {
            "type": "new_message",
            "message": serialized
        }, exclude_user=user_id)
        
        # Si c'est une alerte avec vibration, créer des notifications
        if message.alert_type and ALERT_TYPES.get(message.alert_type, {}).get("vibrate"):
            alert_info = ALERT_TYPES[message.alert_type]
            for member in group.get("members", []):
                if member.get("user_id") != user_id:
                    await create_notification(
                        user_id=member.get("user_id"),
                        notif_type="chat_alert",
                        title=f"{alert_info['emoji']} {alert_info['label']}",
                        message=f"{user_info.get('name')}: {message.content}",
                        data={
                            "group_id": group_id,
                            "alert_type": message.alert_type,
                            "vibrate": True,
                            "priority": alert_info.get("priority", "normal")
                        }
                    )
        
        return {
            "success": True,
            "message": serialized
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{group_id}/alert/{user_id}")
async def send_alert(group_id: str, user_id: str, alert: AlertCreate):
    """Envoie une alerte rapide au groupe"""
    try:
        if alert.alert_type not in ALERT_TYPES:
            raise HTTPException(status_code=400, detail="Type d'alerte invalide")
        
        alert_info = ALERT_TYPES[alert.alert_type]
        content = alert.message or alert_info["label"]
        
        # Utiliser send_message avec le type alert
        message = MessageCreate(
            content=f"{alert_info['emoji']} {content}",
            message_type="alert",
            alert_type=alert.alert_type,
            location=alert.location
        )
        
        return await send_message(group_id, user_id, message)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{group_id}/messages")
async def get_messages(
    group_id: str,
    user_id: str = Query(...),
    limit: int = Query(50, ge=1, le=200),
    before: Optional[str] = Query(None, description="Timestamp pour pagination")
):
    """Récupère les messages du chat"""
    try:
        # Vérifier l'appartenance
        group = await groups_collection.find_one({"_id": ObjectId(group_id)})
        if not group:
            raise HTTPException(status_code=404, detail="Groupe non trouvé")
        
        is_member = any(m.get("user_id") == user_id for m in group.get("members", []))
        if not is_member:
            raise HTTPException(status_code=403, detail="Vous n'êtes pas membre de ce groupe")
        
        query = {"group_id": group_id}
        if before:
            query["created_at"] = {"$lt": before}
        
        cursor = messages_collection.find(query).sort("created_at", -1).limit(limit)
        messages = await cursor.to_list(length=limit)
        
        # Inverser pour avoir l'ordre chronologique
        messages.reverse()
        
        return {
            "group_id": group_id,
            "messages": [serialize_message(m) for m in messages],
            "has_more": len(messages) == limit
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{group_id}/messages/read/{user_id}")
async def mark_messages_read(group_id: str, user_id: str):
    """Marque tous les messages comme lus"""
    try:
        result = await messages_collection.update_many(
            {"group_id": group_id, "read_by": {"$ne": user_id}},
            {"$push": {"read_by": user_id}}
        )
        
        return {"success": True, "marked_read": result.modified_count}
        
    except Exception as e:
        logger.error(f"Error marking messages read: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{group_id}/unread-count/{user_id}")
async def get_unread_count(group_id: str, user_id: str):
    """Compte les messages non lus"""
    try:
        count = await messages_collection.count_documents({
            "group_id": group_id,
            "read_by": {"$ne": user_id},
            "sender_id": {"$ne": user_id}
        })
        
        return {"unread_count": count}
        
    except Exception as e:
        logger.error(f"Error counting unread: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# REFERENCE DATA
# ============================================

@router.get("/alert-types")
async def get_alert_types():
    """Récupère la liste des types d'alerte disponibles"""
    return {
        "alert_types": ALERT_TYPES,
        "quick_messages": QUICK_MESSAGES
    }


# ============================================
# WEBSOCKET FOR REAL-TIME CHAT
# ============================================

@router.websocket("/ws/{group_id}/{user_id}")
async def chat_websocket(websocket: WebSocket, group_id: str, user_id: str):
    """WebSocket pour le chat en temps réel"""
    await websocket.accept()
    
    # Enregistrer la connexion
    if group_id not in chat_connections:
        chat_connections[group_id] = {}
    chat_connections[group_id][user_id] = websocket
    
    user_info = await get_user_info(user_id)
    
    # Notifier le groupe
    await broadcast_to_group(group_id, {
        "type": "user_joined_chat",
        "user_id": user_id,
        "user_name": user_info.get("name"),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }, exclude_user=user_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "message":
                # Message texte
                message = MessageCreate(
                    content=data.get("content", ""),
                    message_type=data.get("message_type", "text"),
                    alert_type=data.get("alert_type"),
                    location=data.get("location")
                )
                
                user_info = await get_user_info(user_id)
                now = datetime.now(timezone.utc).isoformat()
                
                msg_doc = {
                    "group_id": group_id,
                    "sender_id": user_id,
                    "sender_name": user_info.get("name"),
                    "content": message.content,
                    "message_type": message.message_type,
                    "alert_type": message.alert_type,
                    "alert_info": ALERT_TYPES.get(message.alert_type) if message.alert_type else None,
                    "location": message.location,
                    "created_at": now,
                    "read_by": [user_id]
                }
                
                result = await messages_collection.insert_one(msg_doc)
                msg_doc["_id"] = result.inserted_id
                
                # Broadcast à tous (incluant l'expéditeur pour confirmation)
                await broadcast_to_group(group_id, {
                    "type": "new_message",
                    "message": serialize_message(msg_doc)
                })
                
            elif data.get("type") == "typing":
                # Indicateur de frappe
                await broadcast_to_group(group_id, {
                    "type": "user_typing",
                    "user_id": user_id,
                    "user_name": user_info.get("name")
                }, exclude_user=user_id)
                
            elif data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
                
    except WebSocketDisconnect:
        if group_id in chat_connections:
            chat_connections[group_id].pop(user_id, None)
            if not chat_connections[group_id]:
                del chat_connections[group_id]
        
        await broadcast_to_group(group_id, {
            "type": "user_left_chat",
            "user_id": user_id,
            "user_name": user_info.get("name"),
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        logger.error(f"Chat WebSocket error: {e}")


# ============================================
# CHAT STATS
# ============================================

@router.get("/{group_id}/stats")
async def get_chat_stats(group_id: str):
    """Statistiques du chat du groupe"""
    try:
        total_messages = await messages_collection.count_documents({"group_id": group_id})
        
        # Messages par type
        pipeline = [
            {"$match": {"group_id": group_id}},
            {"$group": {"_id": "$message_type", "count": {"$sum": 1}}}
        ]
        by_type = await messages_collection.aggregate(pipeline).to_list(length=10)
        
        # Alertes par type
        alert_pipeline = [
            {"$match": {"group_id": group_id, "alert_type": {"$ne": None}}},
            {"$group": {"_id": "$alert_type", "count": {"$sum": 1}}}
        ]
        by_alert = await messages_collection.aggregate(alert_pipeline).to_list(length=20)
        
        # Utilisateurs connectés au chat
        connected_users = len(chat_connections.get(group_id, {}))
        
        return {
            "group_id": group_id,
            "total_messages": total_messages,
            "by_type": {t["_id"]: t["count"] for t in by_type},
            "alerts_by_type": {a["_id"]: a["count"] for a in by_alert},
            "connected_users": connected_users
        }
        
    except Exception as e:
        logger.error(f"Error getting chat stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
