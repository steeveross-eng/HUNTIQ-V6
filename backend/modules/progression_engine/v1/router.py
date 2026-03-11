"""Progression Engine Router - PLAN MAITRE
FastAPI router for gamification and user progression.

Version: 1.0.0
API Prefix: /api/v1/progression
"""

from fastapi import APIRouter, Query
from typing import Optional
from .service import ProgressionService

router = APIRouter(prefix="/api/v1/progression", tags=["Progression Engine"])

_service = ProgressionService()


@router.get("/")
async def progression_engine_info():
    """Get progression engine information"""
    stats = await _service.get_stats()
    
    return {
        "module": "progression_engine",
        "version": "1.0.0",
        "phase": 4,
        "description": "Gamification et progression utilisateur",
        "status": "operational",
        "features": [
            "Niveaux et XP",
            "Badges et accomplissements",
            "Défis saisonniers",
            "Classements",
            "Récompenses"
        ],
        "statistics": stats
    }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "module": "progression_engine", "version": "1.0.0"}


@router.get("/user/{user_id}")
async def get_user_progression(user_id: str):
    """Get user's progression data"""
    progression = await _service.get_user_progression(user_id)
    return {"success": True, "progression": progression.model_dump()}


@router.post("/user/{user_id}/xp")
async def add_user_xp(
    user_id: str,
    xp_amount: int = Query(..., ge=1, le=10000),
    action: str = Query(...),
    detail: Optional[str] = Query(None)
):
    """Add XP to user"""
    details = {"detail": detail} if detail else None
    event = await _service.add_xp(user_id, xp_amount, action, details)
    return {
        "success": True,
        "event": event.model_dump(),
        "level_up": event.level_up
    }


@router.get("/badges")
async def list_badges():
    """List all available badges"""
    badges = await _service.get_badges()
    return {
        "success": True,
        "total": len(badges),
        "badges": [b.model_dump() for b in badges]
    }


@router.get("/user/{user_id}/badges")
async def get_user_badges(user_id: str):
    """Get badges earned by user"""
    badges = await _service.get_user_badges(user_id)
    return {
        "success": True,
        "total": len(badges),
        "badges": [b.model_dump() for b in badges]
    }


@router.get("/user/{user_id}/eligible-badges")
async def check_eligible_badges(user_id: str):
    """Check which badges user is eligible for"""
    eligible = await _service.check_badge_eligibility(user_id)
    return {
        "success": True,
        "eligible_count": len(eligible),
        "badges": [b.model_dump() for b in eligible]
    }


@router.post("/user/{user_id}/badges/{badge_id}")
async def award_badge(
    user_id: str,
    badge_id: str,
    badge_name: str = Query(...),
    xp_reward: int = Query(0, ge=0)
):
    """Award a badge to user"""
    badge = await _service.award_badge(user_id, badge_id, badge_name, xp_reward)
    return {"success": True, "badge": badge.model_dump()}


@router.get("/challenges")
async def list_active_challenges():
    """List active challenges"""
    challenges = await _service.get_active_challenges()
    return {
        "success": True,
        "total": len(challenges),
        "challenges": [c.model_dump() for c in challenges]
    }


@router.get("/challenges/{challenge_id}/progress")
async def get_challenge_progress(
    challenge_id: str,
    user_id: str = Query(...)
):
    """Get user's progress on a challenge"""
    progress = await _service.get_challenge_progress(user_id, challenge_id)
    
    if not progress:
        return {
            "success": True,
            "progress": None,
            "message": "Pas encore commencé"
        }
    
    return {"success": True, "progress": progress.model_dump()}


@router.post("/challenges/{challenge_id}/progress")
async def update_challenge_progress(
    challenge_id: str,
    user_id: str = Query(...),
    increment: int = Query(1, ge=1)
):
    """Update challenge progress"""
    progress = await _service.update_challenge_progress(
        user_id, challenge_id, increment
    )
    return {
        "success": True,
        "progress": progress.model_dump(),
        "completed": progress.completed
    }


@router.get("/leaderboard")
async def get_leaderboard(
    limit: int = Query(50, ge=1, le=200),
    region: Optional[str] = Query(None)
):
    """Get leaderboard"""
    entries = await _service.get_leaderboard(limit, region)
    return {
        "success": True,
        "total": len(entries),
        "leaderboard": [e.model_dump() for e in entries]
    }


@router.get("/rewards")
async def get_available_rewards(user_id: str = Query(...)):
    """Get available rewards for user"""
    rewards = await _service.get_rewards(user_id)
    return {
        "success": True,
        "total": len(rewards),
        "rewards": [r.model_dump() for r in rewards]
    }
