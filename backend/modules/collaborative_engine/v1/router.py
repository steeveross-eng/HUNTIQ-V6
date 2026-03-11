"""Collaborative Engine Router - PLAN MAITRE
FastAPI router for hunter collaboration system.

Version: 1.0.0
API Prefix: /api/v1/collaborative
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
from datetime import datetime
from .service import CollaborativeService
from .models import (
    GroupRole, GroupCreateRequest, GroupUpdateRequest
)

router = APIRouter(prefix="/api/v1/collaborative", tags=["Collaborative Engine"])

# Initialize service
_service = CollaborativeService()


@router.get("/")
async def collaborative_engine_info():
    """Get collaborative engine information and status"""
    stats = await _service.get_stats()
    
    return {
        "module": "collaborative_engine",
        "version": "1.0.0",
        "phase": 4,
        "description": "Système de collaboration entre chasseurs",
        "status": "operational",
        "features": [
            "Groupes de chasse",
            "Partage de spots",
            "Calendrier de groupe",
            "Chat en temps réel",
            "Partage de positions",
            "Système d'invitations"
        ],
        "statistics": stats
    }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "module": "collaborative_engine",
        "version": "1.0.0"
    }


# ==========================================
# Groups
# ==========================================

@router.get("/groups")
async def get_user_groups(
    user_id: str = Query(..., description="User ID")
):
    """Get all groups a user belongs to"""
    groups = await _service.get_user_groups(user_id)
    return {
        "success": True,
        "total": len(groups),
        "groups": [g.model_dump() for g in groups]
    }


@router.post("/groups")
async def create_group(
    request: GroupCreateRequest,
    user_id: str = Query(..., description="Owner user ID"),
    user_name: str = Query(..., description="Owner name")
):
    """Create a new hunting group"""
    try:
        group = await _service.create_group(user_id, user_name, request)
        return {
            "success": True,
            "message": "Groupe créé avec succès",
            "group": group.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/groups/{group_id}")
async def get_group(group_id: str):
    """Get group details"""
    group = await _service.get_group(group_id)
    
    if not group:
        raise HTTPException(status_code=404, detail="Groupe non trouvé")
    
    return {
        "success": True,
        "group": group.model_dump()
    }


@router.put("/groups/{group_id}")
async def update_group(
    group_id: str,
    request: GroupUpdateRequest
):
    """Update group settings"""
    group = await _service.update_group(group_id, request)
    
    if not group:
        raise HTTPException(status_code=404, detail="Groupe non trouvé")
    
    return {
        "success": True,
        "group": group.model_dump()
    }


@router.delete("/groups/{group_id}")
async def delete_group(group_id: str):
    """Archive a group"""
    success = await _service.delete_group(group_id)
    return {
        "success": success,
        "message": "Groupe archivé" if success else "Échec de l'archivage"
    }


# ==========================================
# Members
# ==========================================

@router.get("/groups/{group_id}/members")
async def get_group_members(group_id: str):
    """Get all members of a group"""
    members = await _service.get_group_members(group_id)
    return {
        "success": True,
        "total": len(members),
        "members": [m.model_dump() for m in members]
    }


@router.post("/groups/{group_id}/members")
async def add_group_member(
    group_id: str,
    user_id: str = Query(...),
    user_name: str = Query(...),
    role: str = Query("member")
):
    """Add a member to a group"""
    try:
        member_role = GroupRole(role)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Rôle invalide: {role}")
    
    member = await _service.add_member(group_id, user_id, user_name, member_role)
    return {
        "success": True,
        "member": member.model_dump()
    }


@router.delete("/groups/{group_id}/members/{user_id}")
async def remove_group_member(group_id: str, user_id: str):
    """Remove a member from a group"""
    success = await _service.remove_member(group_id, user_id)
    return {
        "success": success,
        "message": "Membre retiré" if success else "Membre non trouvé"
    }


@router.put("/groups/{group_id}/members/{user_id}/role")
async def update_member_role(
    group_id: str,
    user_id: str,
    role: str = Query(...)
):
    """Update a member's role"""
    try:
        new_role = GroupRole(role)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Rôle invalide: {role}")
    
    member = await _service.update_member_role(group_id, user_id, new_role)
    
    if not member:
        raise HTTPException(status_code=404, detail="Membre non trouvé")
    
    return {
        "success": True,
        "member": member.model_dump()
    }


# ==========================================
# Spots
# ==========================================

@router.get("/groups/{group_id}/spots")
async def get_group_spots(group_id: str):
    """Get all spots in a group"""
    spots = await _service.get_group_spots(group_id)
    return {
        "success": True,
        "total": len(spots),
        "spots": [s.model_dump() for s in spots]
    }


@router.post("/groups/{group_id}/spots")
async def create_spot(
    group_id: str,
    spot_data: Dict[str, Any],
    user_id: str = Query(..., description="Creator user ID")
):
    """Create a shared hunting spot"""
    try:
        spot = await _service.create_spot(group_id, user_id, spot_data)
        return {
            "success": True,
            "spot": spot.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/groups/{group_id}/spots/{spot_id}")
async def update_spot(
    group_id: str,
    spot_id: str,
    update_data: Dict[str, Any]
):
    """Update a spot"""
    spot = await _service.update_spot(spot_id, update_data)
    
    if not spot:
        raise HTTPException(status_code=404, detail="Spot non trouvé")
    
    return {
        "success": True,
        "spot": spot.model_dump()
    }


@router.delete("/groups/{group_id}/spots/{spot_id}")
async def delete_spot(group_id: str, spot_id: str):
    """Delete a spot"""
    success = await _service.delete_spot(spot_id, group_id)
    return {
        "success": success,
        "message": "Spot supprimé" if success else "Spot non trouvé"
    }


# ==========================================
# Calendar/Events
# ==========================================

@router.get("/groups/{group_id}/calendar")
async def get_group_calendar(
    group_id: str,
    upcoming_only: bool = Query(True)
):
    """Get group calendar/events"""
    events = await _service.get_group_events(group_id, upcoming_only)
    return {
        "success": True,
        "total": len(events),
        "events": [e.model_dump() for e in events]
    }


@router.post("/groups/{group_id}/calendar")
async def create_event(
    group_id: str,
    event_data: Dict[str, Any],
    user_id: str = Query(..., description="Creator user ID")
):
    """Create a group event"""
    try:
        event = await _service.create_event(group_id, user_id, event_data)
        return {
            "success": True,
            "event": event.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/groups/{group_id}/calendar/{event_id}/join")
async def join_event(
    group_id: str,
    event_id: str,
    user_id: str = Query(...)
):
    """Join a group event"""
    success = await _service.join_event(event_id, user_id)
    return {
        "success": success,
        "message": "Inscription confirmée" if success else "Erreur d'inscription"
    }


@router.post("/groups/{group_id}/calendar/{event_id}/leave")
async def leave_event(
    group_id: str,
    event_id: str,
    user_id: str = Query(...)
):
    """Leave a group event"""
    success = await _service.leave_event(event_id, user_id)
    return {
        "success": success,
        "message": "Désinscription confirmée" if success else "Erreur"
    }


# ==========================================
# Chat
# ==========================================

@router.get("/groups/{group_id}/chat")
async def get_chat_messages(
    group_id: str,
    limit: int = Query(50, ge=1, le=200),
    before: Optional[str] = Query(None, description="ISO datetime for pagination")
):
    """Get group chat messages"""
    before_dt = None
    if before:
        try:
            before_dt = datetime.fromisoformat(before.replace('Z', '+00:00'))
        except ValueError:
            pass
    
    messages = await _service.get_chat_messages(group_id, limit, before_dt)
    return {
        "success": True,
        "total": len(messages),
        "messages": [m.model_dump() for m in messages]
    }


@router.post("/groups/{group_id}/chat")
async def send_chat_message(
    group_id: str,
    content: str = Query(...),
    user_id: str = Query(...),
    user_name: str = Query(...),
    message_type: str = Query("text")
):
    """Send a chat message"""
    message = await _service.send_message(
        group_id, user_id, user_name, content, message_type
    )
    return {
        "success": True,
        "message": message.model_dump()
    }


# ==========================================
# Invitations
# ==========================================

@router.get("/invitations")
async def get_user_invitations(user_id: str = Query(...)):
    """Get pending invitations for a user"""
    invitations = await _service.get_user_invitations(user_id)
    return {
        "success": True,
        "total": len(invitations),
        "invitations": [i.model_dump() for i in invitations]
    }


@router.post("/groups/{group_id}/invite")
async def invite_to_group(
    group_id: str,
    invited_by: str = Query(...),
    invited_user_id: Optional[str] = Query(None),
    invited_email: Optional[str] = Query(None),
    message: Optional[str] = Query(None)
):
    """Send an invitation to join a group"""
    if not invited_user_id and not invited_email:
        raise HTTPException(
            status_code=400,
            detail="user_id ou email requis"
        )
    
    group = await _service.get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Groupe non trouvé")
    
    invitation = await _service.create_invitation(
        group_id=group_id,
        group_name=group.name,
        invited_by=invited_by,
        invited_user_id=invited_user_id,
        invited_email=invited_email,
        message=message
    )
    
    return {
        "success": True,
        "invitation": invitation.model_dump()
    }


@router.post("/invitations/{invitation_id}/respond")
async def respond_to_invitation(
    invitation_id: str,
    accept: bool = Query(...),
    user_id: str = Query(...),
    user_name: str = Query(...)
):
    """Accept or decline an invitation"""
    result = await _service.respond_to_invitation(
        invitation_id, accept, user_id, user_name
    )
    return result


# ==========================================
# Position Sharing
# ==========================================

@router.get("/groups/{group_id}/positions")
async def get_group_positions(group_id: str):
    """Get all active positions in a group"""
    positions = await _service.get_group_positions(group_id)
    return {
        "success": True,
        "total": len(positions),
        "positions": [p.model_dump() for p in positions]
    }


@router.post("/groups/{group_id}/positions")
async def update_position(
    group_id: str,
    user_id: str = Query(...),
    user_name: str = Query(...),
    lat: float = Query(...),
    lng: float = Query(...),
    status: str = Query("hunting")
):
    """Update user's shared position"""
    position = await _service.update_position(
        group_id=group_id,
        user_id=user_id,
        user_name=user_name,
        coordinates={"lat": lat, "lng": lng},
        status=status
    )
    return {
        "success": True,
        "position": position.model_dump()
    }


@router.delete("/groups/{group_id}/positions")
async def stop_sharing_position(
    group_id: str,
    user_id: str = Query(...)
):
    """Stop sharing position"""
    success = await _service.stop_sharing_position(group_id, user_id)
    return {
        "success": success,
        "message": "Partage arrêté" if success else "Position non trouvée"
    }
