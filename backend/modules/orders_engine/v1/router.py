"""Orders Engine Router - PHASE 7 EXTRACTION
Version: 1.0.1
Security: @require_business_or_admin on sensitive endpoints (P0 - 11 Feb 2026)
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks, Depends
from typing import Optional, List
from pydantic import BaseModel

from .models import Order, OrderCreate, OrderUpdate, OrderCancellation, Commission
from .service import get_orders_service

# Role-based access control
from modules.roles_engine.v1.dependencies import require_business_or_admin
from modules.roles_engine.v1.models import UserWithRole


router = APIRouter(
    prefix="/api/v1/orders",
    tags=["Orders Engine"]
)


# ==============================================
# RESPONSE MODELS
# ==============================================

class HealthResponse(BaseModel):
    status: str
    engine: str
    version: str
    message: str


# ==============================================
# HEALTH CHECK
# ==============================================

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check orders engine health"""
    service = get_orders_service()
    stats = await service.get_stats()
    
    return HealthResponse(
        status="operational",
        engine="orders_engine",
        version="1.0.0",
        message=f"Engine opérationnel - {stats['total_orders']} commandes"
    )


@router.get("/stats")
async def get_engine_stats():
    """Get orders engine statistics"""
    service = get_orders_service()
    return await service.get_stats()


# ==============================================
# ORDERS ENDPOINTS
# ==============================================

@router.get("/", response_model=List[Order])
async def get_orders(
    status: Optional[str] = None,
    sale_mode: Optional[str] = None,
    limit: int = Query(500, le=1000),
    user: UserWithRole = Depends(require_business_or_admin)
):
    """Get all orders with optional filters (Business/Admin only)"""
    service = get_orders_service()
    return await service.get_all(status, sale_mode, limit)


@router.get("/{order_id}", response_model=Order)
async def get_order(
    order_id: str,
    user: UserWithRole = Depends(require_business_or_admin)
):
    """Get order by ID (Business/Admin only)"""
    service = get_orders_service()
    order = await service.get_by_id(order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    
    return order


@router.post("/", response_model=Order)
async def create_order(order_input: OrderCreate):
    """Create a new order (Public - customers can order)"""
    service = get_orders_service()
    
    try:
        return await service.create(order_input)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{order_id}", response_model=Order)
async def update_order_status(
    order_id: str,
    update: OrderUpdate,
    user: UserWithRole = Depends(require_business_or_admin)
):
    """Update order status (Business/Admin only)"""
    service = get_orders_service()
    order = await service.update_status(order_id, update)
    
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvée ou données invalides")
    
    return order


@router.post("/{order_id}/cancel")
async def cancel_order(
    order_id: str,
    cancellation: OrderCancellation,
    background_tasks: BackgroundTasks,
    user: UserWithRole = Depends(require_business_or_admin)
):
    """Cancel an order and send notification email (Business/Admin only)"""
    service = get_orders_service()
    
    try:
        result = await service.cancel(order_id, cancellation)
        return {
            "success": True,
            "message": "Commande annulée avec succès",
            "order": result["order"],
            "email_notification": result["email_notification"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==============================================
# COMMISSIONS ENDPOINTS
# ==============================================

@router.get("/commissions/", response_model=List[Commission])
async def get_commissions(
    status: Optional[str] = None,
    commission_type: Optional[str] = None,
    limit: int = Query(500, le=1000),
    user: UserWithRole = Depends(require_business_or_admin)
):
    """Get all commissions (Business/Admin only)"""
    service = get_orders_service()
    return await service.get_commissions(status, commission_type, limit)


@router.put("/commissions/{commission_id}/pay")
async def mark_commission_paid(
    commission_id: str,
    user: UserWithRole = Depends(require_business_or_admin)
):
    """Mark a commission as paid (Business/Admin only)"""
    service = get_orders_service()
    commission = await service.mark_commission_paid(commission_id)
    
    if not commission:
        raise HTTPException(
            status_code=400, 
            detail="Commission non trouvée ou non confirmée"
        )
    
    return {
        "success": True,
        "message": "Commission marquée comme payée",
        "commission": commission
    }
