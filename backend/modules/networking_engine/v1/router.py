"""Networking Engine Router - PLAN MAITRE
FastAPI router for hunter social network.

Version: 1.0.0
API Prefix: /api/v1/network
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
from .service import NetworkingService

router = APIRouter(prefix="/api/v1/network", tags=["Networking Engine"])

_service = NetworkingService()


@router.get("/")
async def networking_engine_info():
    """Get networking engine information"""
    stats = await _service.get_stats()
    
    return {
        "module": "networking_engine",
        "version": "1.0.0",
        "phase": 4,
        "description": "Réseau social de chasseurs",
        "status": "operational",
        "features": [
            "Profils publics",
            "Connexions/amis",
            "Feed d'activité",
            "Partage de succès",
            "Événements communautaires"
        ],
        "statistics": stats
    }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "module": "networking_engine", "version": "1.0.0"}


# ==========================================
# Profiles
# ==========================================

@router.get("/profile/{user_id}")
async def get_profile(user_id: str):
    """Get public profile"""
    profile = await _service.get_profile(user_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profil non trouvé")
    
    return {"success": True, "profile": profile.model_dump()}


@router.put("/profile/{user_id}")
async def update_profile(user_id: str, profile_data: Dict[str, Any]):
    """Update public profile"""
    profile = await _service.create_or_update_profile(user_id, profile_data)
    return {"success": True, "profile": profile.model_dump()}


@router.get("/profiles/search")
async def search_profiles(
    query: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=100)
):
    """Search profiles"""
    profiles = await _service.search_profiles(query, limit)
    return {
        "success": True,
        "total": len(profiles),
        "profiles": [p.model_dump() for p in profiles]
    }


# ==========================================
# Connections
# ==========================================

@router.get("/connections")
async def get_connections(
    user_id: str = Query(...),
    status: Optional[str] = Query(None, regex="^(pending|accepted|blocked)$")
):
    """Get user's connections"""
    connections = await _service.get_connections(user_id, status)
    return {
        "success": True,
        "total": len(connections),
        "connections": [c.model_dump() for c in connections]
    }


@router.post("/connections/request")
async def send_connection_request(
    requester_id: str = Query(...),
    recipient_id: str = Query(...)
):
    """Send connection request"""
    if requester_id == recipient_id:
        raise HTTPException(status_code=400, detail="Cannot connect to yourself")
    
    connection = await _service.send_connection_request(requester_id, recipient_id)
    return {"success": True, "connection": connection.model_dump()}


@router.post("/connections/{connection_id}/respond")
async def respond_to_connection(
    connection_id: str,
    accept: bool = Query(...)
):
    """Accept or decline connection request"""
    connection = await _service.respond_to_connection(connection_id, accept)
    
    if not connection:
        raise HTTPException(status_code=404, detail="Connexion non trouvée")
    
    return {
        "success": True,
        "connection": connection.model_dump(),
        "accepted": accept
    }


@router.get("/connections/pending")
async def get_pending_requests(user_id: str = Query(...)):
    """Get pending connection requests"""
    requests = await _service.get_pending_requests(user_id)
    return {
        "success": True,
        "total": len(requests),
        "requests": [r.model_dump() for r in requests]
    }


# ==========================================
# Feed & Posts
# ==========================================

@router.get("/feed")
async def get_feed(
    user_id: str = Query(...),
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0)
):
    """Get user's activity feed"""
    posts = await _service.get_feed(user_id, limit, skip)
    return {
        "success": True,
        "total": len(posts),
        "posts": [p.model_dump() for p in posts]
    }


@router.post("/posts")
async def create_post(
    author_id: str = Query(...),
    author_name: str = Query(...),
    content: str = Query(...),
    post_type: str = Query("text"),
    visibility: str = Query("public"),
    species: Optional[str] = Query(None)
):
    """Create a new post"""
    post = await _service.create_post(
        author_id=author_id,
        author_name=author_name,
        content=content,
        post_type=post_type,
        visibility=visibility,
        species=species
    )
    return {"success": True, "post": post.model_dump()}


@router.get("/posts/{post_id}")
async def get_post(post_id: str):
    """Get a specific post"""
    post = await _service.get_post(post_id)
    
    if not post:
        raise HTTPException(status_code=404, detail="Publication non trouvée")
    
    return {"success": True, "post": post.model_dump()}


@router.get("/posts/user/{user_id}")
async def get_user_posts(
    user_id: str,
    limit: int = Query(20, ge=1, le=100)
):
    """Get posts by a specific user"""
    posts = await _service.get_user_posts(user_id, limit)
    return {
        "success": True,
        "total": len(posts),
        "posts": [p.model_dump() for p in posts]
    }


@router.post("/posts/{post_id}/like")
async def like_post(
    post_id: str,
    user_id: str = Query(...)
):
    """Like a post"""
    success = await _service.like_post(post_id, user_id)
    return {"success": success}


@router.post("/posts/{post_id}/comments")
async def add_comment(
    post_id: str,
    author_id: str = Query(...),
    author_name: str = Query(...),
    content: str = Query(...)
):
    """Add comment to post"""
    comment = await _service.add_comment(
        post_id, author_id, author_name, content
    )
    return {"success": True, "comment": comment.model_dump()}


@router.get("/posts/{post_id}/comments")
async def get_post_comments(
    post_id: str,
    limit: int = Query(50, ge=1, le=200)
):
    """Get comments on a post"""
    comments = await _service.get_post_comments(post_id, limit)
    return {
        "success": True,
        "total": len(comments),
        "comments": [c.model_dump() for c in comments]
    }


# ==========================================
# Events
# ==========================================

@router.get("/events")
async def get_upcoming_events(
    limit: int = Query(20, ge=1, le=100),
    event_type: Optional[str] = Query(None)
):
    """Get upcoming community events"""
    events = await _service.get_upcoming_events(limit, event_type)
    return {
        "success": True,
        "total": len(events),
        "events": [e.model_dump() for e in events]
    }


@router.post("/events")
async def create_event(
    organizer_id: str = Query(...),
    organizer_name: str = Query(...),
    event_data: Dict[str, Any] = None
):
    """Create a community event"""
    if event_data is None:
        event_data = {}
    
    event = await _service.create_event(organizer_id, organizer_name, event_data)
    return {"success": True, "event": event.model_dump()}


@router.post("/events/{event_id}/register")
async def register_for_event(
    event_id: str,
    user_id: str = Query(...)
):
    """Register for an event"""
    registration = await _service.register_for_event(event_id, user_id)
    return {
        "success": True,
        "registration": registration.model_dump(),
        "waitlist": registration.status == "waitlist"
    }
