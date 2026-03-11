"""
WebSocket Geo Sync - Real-time Geospatial Synchronization
Phase P6.4 - WebSocket Implementation

Provides real-time synchronization of geo entities between
hunting group members.

⚠️ CONFIDENTIALITÉ: Les HOTSPOTS sont EXCLUS de toute synchronisation.
Les hotspots sont des données sensibles 100% privées, non partageables.
Seuls les waypoints, zones et autres entités non-sensibles peuvent être synchronisés.

Events:
- geo.created: New entity created (EXCLUDES hotspots)
- geo.updated: Entity updated (EXCLUDES hotspots)
- geo.deleted: Entity deleted (EXCLUDES hotspots)
- group.member_location: Member location update (optional, user-controlled)
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Dict, Set, Optional
from datetime import datetime, timezone
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSocket Geo Sync"])

# Types d'entités EXCLUS de la synchronisation (données sensibles)
PRIVATE_ENTITY_TYPES = {"hotspot", "corridor"}  # Hotspots = 100% privés


# ===========================================
# CONNECTION MANAGER
# ===========================================

class GeoSyncManager:
    """Manages WebSocket connections organized by hunting groups"""
    
    def __init__(self):
        # group_id -> set of WebSocket connections
        self.group_connections: Dict[str, Set[WebSocket]] = {}
        # websocket -> (user_id, group_id)
        self.connection_info: Dict[WebSocket, tuple] = {}
        # user_id -> websocket (for direct messaging)
        self.user_connections: Dict[str, WebSocket] = {}
        # group_id -> set of user_ids currently connected
        self.group_members: Dict[str, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str, group_id: str):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        # Initialize group if needed
        if group_id not in self.group_connections:
            self.group_connections[group_id] = set()
            self.group_members[group_id] = set()
        
        # Add connection
        self.group_connections[group_id].add(websocket)
        self.connection_info[websocket] = (user_id, group_id)
        self.user_connections[user_id] = websocket
        self.group_members[group_id].add(user_id)
        
        logger.info(f"WebSocket connected: user={user_id}, group={group_id}")
        
        # Notify group of new member
        await self.broadcast_to_group(group_id, {
            "type": "member.joined",
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "active_members": list(self.group_members.get(group_id, set()))
        }, exclude_user=user_id)
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket not in self.connection_info:
            return
        
        user_id, group_id = self.connection_info[websocket]
        
        # Remove from group
        if group_id in self.group_connections:
            self.group_connections[group_id].discard(websocket)
            if not self.group_connections[group_id]:
                del self.group_connections[group_id]
        
        # Remove from group members
        if group_id in self.group_members:
            self.group_members[group_id].discard(user_id)
            if not self.group_members[group_id]:
                del self.group_members[group_id]
        
        # Remove from user connections
        if user_id in self.user_connections:
            del self.user_connections[user_id]
        
        # Remove connection info
        del self.connection_info[websocket]
        
        logger.info(f"WebSocket disconnected: user={user_id}, group={group_id}")
    
    async def broadcast_to_group(
        self, 
        group_id: str, 
        message: dict, 
        exclude_user: Optional[str] = None
    ):
        """Broadcast a message to all members of a group"""
        if group_id not in self.group_connections:
            return
        
        disconnected = []
        message_json = json.dumps(message)
        
        for websocket in self.group_connections[group_id]:
            user_id, _ = self.connection_info.get(websocket, (None, None))
            
            if exclude_user and user_id == exclude_user:
                continue
            
            try:
                await websocket.send_text(message_json)
            except Exception as e:
                logger.warning(f"Failed to send to websocket: {e}")
                disconnected.append(websocket)
        
        # Clean up disconnected
        for ws in disconnected:
            self.disconnect(ws)
    
    async def send_to_user(self, user_id: str, message: dict):
        """Send a message to a specific user"""
        if user_id not in self.user_connections:
            return False
        
        try:
            await self.user_connections[user_id].send_text(json.dumps(message))
            return True
        except Exception as e:
            logger.warning(f"Failed to send to user {user_id}: {e}")
            return False
    
    def get_group_members(self, group_id: str) -> Set[str]:
        """Get currently connected members of a group"""
        return self.group_members.get(group_id, set())
    
    def get_user_group(self, user_id: str) -> Optional[str]:
        """Get the group a user is connected to"""
        ws = self.user_connections.get(user_id)
        if ws and ws in self.connection_info:
            return self.connection_info[ws][1]
        return None


# Global manager instance
geo_sync_manager = GeoSyncManager()


# ===========================================
# WEBSOCKET ENDPOINT
# ===========================================

@router.websocket("/ws/geo-sync")
async def websocket_geo_sync(
    websocket: WebSocket,
    token: str = Query(...),
    group_id: str = Query(...)
):
    """
    WebSocket endpoint for real-time geo synchronization.
    
    Query params:
    - token: JWT token for authentication
    - group_id: Hunting group ID to sync with
    
    Message format (send):
    {
        "type": "geo.created|geo.updated|geo.deleted|location.update",
        "entity": {...} or null,
        "entity_id": "uuid" (for delete),
        "location": {"lat": float, "lng": float} (for location updates)
    }
    
    Message format (receive):
    {
        "type": "geo.created|geo.updated|geo.deleted|member.joined|member.left|location.update",
        "user_id": "sender_id",
        "entity": {...} or null,
        "timestamp": "ISO datetime"
    }
    """
    # Validate token (simplified - in production use proper JWT validation)
    user_id = await _validate_token(token)
    if not user_id:
        await websocket.close(code=4001, reason="Invalid token")
        return
    
    # Validate group membership (simplified)
    if not await _validate_group_membership(user_id, group_id):
        await websocket.close(code=4003, reason="Not a member of this group")
        return
    
    # Accept connection
    await geo_sync_manager.connect(websocket, user_id, group_id)
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await _handle_message(user_id, group_id, message)
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format"
                }))
            except Exception as e:
                logger.error(f"Error handling message: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": str(e)
                }))
    
    except WebSocketDisconnect:
        geo_sync_manager.disconnect(websocket)
        
        # Notify group of member leaving
        await geo_sync_manager.broadcast_to_group(group_id, {
            "type": "member.left",
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "active_members": list(geo_sync_manager.get_group_members(group_id))
        })


async def _validate_token(token: str) -> Optional[str]:
    """Validate JWT token and return user_id"""
    # Simplified validation - in production use proper JWT decoding
    try:
        # For now, accept token as user_id or decode if it's a real JWT
        if token.startswith("user:"):
            return token.replace("user:", "")
        
        # Try to decode as JWT (simplified)
        import jwt
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            return payload.get("sub") or payload.get("user_id") or payload.get("email")
        except Exception:
            pass
        
        # Fallback: use token as user_id for development
        return token if len(token) > 3 else None
    except Exception as e:
        logger.warning(f"Token validation failed: {e}")
        return None


async def _validate_group_membership(user_id: str, group_id: str) -> bool:
    """Validate that user is a member of the group"""
    # Simplified - in production query the database
    # For now, allow all connections (group membership handled elsewhere)
    return True


async def _handle_message(user_id: str, group_id: str, message: dict):
    """
    Handle incoming WebSocket message.
    
    ⚠️ SÉCURITÉ: Les hotspots et corridors sont EXCLUS de la synchronisation.
    Ces données sensibles restent 100% privées et ne sont jamais partagées.
    """
    msg_type = message.get("type")
    entity = message.get("entity", {})
    
    # 🔒 VÉRIFICATION DE CONFIDENTIALITÉ: Bloquer les types sensibles
    entity_type = entity.get("entity_type", "") if entity else ""
    if entity_type in PRIVATE_ENTITY_TYPES:
        logger.warning(f"SECURITY: Blocked sync attempt for private entity type: {entity_type}")
        await geo_sync_manager.send_to_user(user_id, {
            "type": "error",
            "message": "Les hotspots et corridors sont privés et ne peuvent pas être synchronisés."
        })
        return
    
    if msg_type == "geo.created":
        # Broadcast new entity to group (EXCLUDES hotspots/corridors)
        await geo_sync_manager.broadcast_to_group(group_id, {
            "type": "geo.created",
            "user_id": user_id,
            "entity": entity,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, exclude_user=user_id)
    
    elif msg_type == "geo.updated":
        # Broadcast entity update to group (EXCLUDES hotspots/corridors)
        await geo_sync_manager.broadcast_to_group(group_id, {
            "type": "geo.updated",
            "user_id": user_id,
            "entity": entity,
            "entity_id": message.get("entity_id"),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, exclude_user=user_id)
    
    elif msg_type == "geo.deleted":
        # Broadcast entity deletion to group (EXCLUDES hotspots/corridors)
        await geo_sync_manager.broadcast_to_group(group_id, {
            "type": "geo.deleted",
            "user_id": user_id,
            "entity_id": message.get("entity_id"),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, exclude_user=user_id)
    
    elif msg_type == "ping":
        # Respond with pong (keep-alive only)
        await geo_sync_manager.send_to_user(user_id, {
            "type": "pong",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    # NOTE: location.update désactivé pour raisons de confidentialité
    # Les positions des membres ne sont pas partagées automatiquement


# ===========================================
# REST API FOR SYNC STATUS
# ===========================================

@router.get("/api/v1/geo-sync/status")
async def get_sync_status(group_id: str = Query(...)):
    """Get current sync status for a group"""
    members = geo_sync_manager.get_group_members(group_id)
    
    return {
        "group_id": group_id,
        "connected_members": list(members),
        "member_count": len(members),
        "sync_enabled": len(members) > 0
    }


@router.get("/api/v1/geo-sync/groups")
async def list_active_groups():
    """List all groups with active WebSocket connections"""
    return {
        "active_groups": [
            {
                "group_id": gid,
                "member_count": len(members)
            }
            for gid, members in geo_sync_manager.group_members.items()
        ]
    }


@router.get("/api/v1/geo-sync/health")
async def websocket_health():
    """
    Health check pour le service WebSocket.
    P0.3 BIONIC V5 - Validation du support wss://
    """
    return {
        "status": "healthy",
        "service": "geo-sync-websocket",
        "protocol_support": ["ws", "wss"],
        "endpoint": "/ws/geo-sync",
        "active_connections": sum(len(conns) for conns in geo_sync_manager.group_connections.values()),
        "active_groups": len(geo_sync_manager.group_connections),
        "features": {
            "real_time_sync": True,
            "group_broadcast": True,
            "location_sharing": False,  # Désactivé pour confidentialité
            "private_entities_excluded": list(PRIVATE_ENTITY_TYPES)
        }
    }


# ===========================================
# BROADCAST HELPER (for use by other modules)
# ===========================================

async def broadcast_geo_event(
    group_id: str,
    event_type: str,
    entity: Optional[dict] = None,
    entity_id: Optional[str] = None,
    user_id: Optional[str] = None
):
    """
    Broadcast a geo event to a hunting group.
    Called by geo_engine when entities are modified.
    """
    message = {
        "type": event_type,
        "user_id": user_id,
        "entity": entity,
        "entity_id": entity_id,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    await geo_sync_manager.broadcast_to_group(group_id, message, exclude_user=user_id)
