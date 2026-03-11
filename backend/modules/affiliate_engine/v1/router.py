"""Affiliate Engine Router
Version: 1.0.1
Security: @require_business_or_admin on sensitive endpoints (P0 - 11 Feb 2026)
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List
from pydantic import BaseModel
from .models import AffiliateClick
from .service import get_affiliate_service

# Role-based access control
from modules.roles_engine.v1.dependencies import require_business_or_admin
from modules.roles_engine.v1.models import UserWithRole

router = APIRouter(prefix="/api/v1/affiliate", tags=["Affiliate Engine"])

class HealthResponse(BaseModel):
    status: str
    engine: str
    version: str
    message: str

@router.get("/health", response_model=HealthResponse)
async def health_check():
    service = get_affiliate_service()
    stats = await service.get_stats()
    return HealthResponse(
        status="operational", engine="affiliate_engine", version="1.0.1",
        message=f"Engine opérationnel - {stats['total_clicks']} clics, {stats['conversion_rate']}% conversion"
    )

@router.get("/stats")
async def get_stats(
    user: UserWithRole = Depends(require_business_or_admin)
):
    """Get affiliate statistics (Business/Admin only)"""
    service = get_affiliate_service()
    return await service.get_stats()

@router.post("/click")
async def record_click(product_id: str = Query(...), session_id: str = Query(...)):
    """Record an affiliate click and get redirect URL (Public - tracking)"""
    service = get_affiliate_service()
    try:
        result = await service.record_click(product_id, session_id)
        return {"success": True, **result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/clicks", response_model=List[AffiliateClick])
async def get_clicks(
    limit: int = Query(500, le=1000),
    user: UserWithRole = Depends(require_business_or_admin)
):
    """Get all affiliate clicks (Business/Admin only)"""
    service = get_affiliate_service()
    return await service.get_all_clicks(limit)

@router.post("/confirm/{click_id}")
async def confirm_sale(
    click_id: str,
    commission_amount: float = Query(...),
    user: UserWithRole = Depends(require_business_or_admin)
):
    """Confirm an affiliate sale (Business/Admin only)"""
    service = get_affiliate_service()
    try:
        result = await service.confirm_sale(click_id, commission_amount)
        return {"success": True, **result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
