"""Referral Engine Router - MÉTIER

FastAPI router for referral system endpoints.

Version: 1.0.0
API Prefix: /api/v1/referral
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from .service import ReferralService, SOCIAL_PLATFORMS
from .models import (
    ReferralTier, CreateReferralUserRequest, 
    TrackClickRequest, RecordPurchaseRequest,
    PartnerApplication
)

router = APIRouter(prefix="/api/v1/referral", tags=["Referral Engine"])

# Initialize service
_service = ReferralService()


@router.get("/")
async def referral_engine_info():
    """Get referral engine information"""
    return {
        "module": "referral_engine",
        "version": "1.0.0",
        "description": "Referral and affiliate system",
        "features": [
            "Referral code generation",
            "Click tracking",
            "Tier-based discounts",
            "Partner program",
            "Social sharing"
        ],
        "tiers": [t.value for t in ReferralTier],
        "platforms": list(SOCIAL_PLATFORMS.keys())
    }


@router.post("/users")
async def create_referral_user(request: CreateReferralUserRequest):
    """Create a new referral user"""
    try:
        user = await _service.create_user(
            name=request.name,
            email=request.email,
            phone=request.phone
        )
        
        return {
            "success": True,
            "message": "Referral account created",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "referral_code": user.referral_code,
                "referral_link": user.referral_link,
                "tier": user.tier.value,
                "discount_percent": user.current_discount_percent
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/users/{user_id}")
async def get_referral_user(user_id: str):
    """Get referral user by ID"""
    user = await _service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "success": True,
        "user": user
    }


@router.get("/users/email/{email}")
async def get_user_by_email(email: str):
    """Get referral user by email"""
    user = await _service.get_user_by_email(email)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "success": True,
        "user": user
    }


@router.get("/users/code/{code}")
async def get_user_by_code(code: str):
    """Get referral user by code"""
    user = await _service.get_user_by_code(code)
    
    if not user:
        raise HTTPException(status_code=404, detail="Referral code not found")
    
    return {
        "success": True,
        "user": user
    }


@router.post("/track-click")
async def track_click(request: TrackClickRequest):
    """Track a referral link click"""
    success = await _service.track_click(
        code=request.referral_code,
        source=request.source,
        ip=request.ip_address,
        user_agent=request.user_agent
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Referral code not found")
    
    return {
        "success": True,
        "message": "Click tracked"
    }


@router.post("/record-signup")
async def record_signup(
    referral_code: str,
    invitee_email: str,
    invitee_name: Optional[str] = None
):
    """Record a signup from referral"""
    invite = await _service.record_signup(referral_code, invitee_email, invitee_name)
    
    if not invite:
        raise HTTPException(status_code=404, detail="Referral code not found")
    
    return {
        "success": True,
        "message": "Signup recorded",
        "invite": invite.model_dump()
    }


@router.post("/record-purchase")
async def record_purchase(request: RecordPurchaseRequest):
    """Record a purchase from referred user"""
    success = await _service.record_purchase(
        referral_code=request.referral_code,
        invitee_email=request.invitee_email,
        order_amount=request.order_amount,
        order_id=request.order_id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Referral code not found")
    
    return {
        "success": True,
        "message": "Purchase recorded"
    }


@router.get("/dashboard/{user_id}")
async def get_dashboard(user_id: str):
    """Get referral dashboard for a user"""
    dashboard = await _service.get_dashboard(user_id)
    
    if not dashboard:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "success": True,
        "dashboard": dashboard
    }


@router.get("/share/{user_id}")
async def get_share_data(user_id: str, lang: str = Query("fr")):
    """Get share messages and links for user"""
    data = await _service.get_share_data(user_id, lang)
    
    if not data:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "success": True,
        "share_data": data
    }


@router.get("/tiers")
async def get_discount_tiers():
    """Get discount tier configuration"""
    tiers = await _service.get_discount_tiers()
    
    return {
        "success": True,
        "tiers": tiers
    }


@router.get("/platforms")
async def get_social_platforms():
    """Get social sharing platforms"""
    return {
        "success": True,
        "platforms": SOCIAL_PLATFORMS
    }


@router.post("/partner/apply")
async def apply_for_partner(application: PartnerApplication):
    """Submit partner application"""
    result = await _service.apply_for_partner(application)
    
    return {
        "success": True,
        "message": "Application submitted",
        "application_id": result.id
    }


@router.put("/partner/{user_id}/approve")
async def approve_partner(
    user_id: str,
    commission_rate: float = Query(0.1, ge=0, le=1)
):
    """Approve partner application (admin only)"""
    success = await _service.approve_partner(user_id, commission_rate)
    
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "success": True,
        "message": "Partner approved"
    }


@router.get("/admin/users")
async def admin_list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    tier: Optional[str] = None
):
    """List all referral users (admin)"""
    users = await _service.list_users(skip, limit, tier)
    
    return {
        "success": True,
        "total": len(users),
        "users": users
    }
