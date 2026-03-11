"""Products Engine Router - PHASE 7 EXTRACTION
API endpoints extracted from server.py monolith.

Version: 1.0.1
Security: @require_business_or_admin on write endpoints (P0 - 11 Feb 2026)
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
from pydantic import BaseModel

from .models import Product, ProductCreate, ProductUpdate, ProductSearchRequest
from .service import get_products_service

# Role-based access control
from modules.roles_engine.v1.dependencies import require_business_or_admin
from modules.roles_engine.v1.models import UserWithRole


router = APIRouter(
    prefix="/api/v1/products",
    tags=["Products Engine"]
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
    """Check products engine health"""
    service = get_products_service()
    stats = await service.get_stats()
    
    return HealthResponse(
        status="operational",
        engine="products_engine",
        version="1.0.0",
        message=f"Engine opérationnel - {stats['total_products']} produits"
    )


@router.get("/stats")
async def get_engine_stats():
    """Get products engine statistics"""
    service = get_products_service()
    return await service.get_stats()


# ==============================================
# CRUD ENDPOINTS
# ==============================================

@router.get("/", response_model=List[Product])
async def get_products(
    category: Optional[str] = None,
    animal_type: Optional[str] = None,
    season: Optional[str] = None,
    sale_mode: Optional[str] = None,
    limit: int = Query(100, le=500)
):
    """Get all products with optional filters"""
    service = get_products_service()
    return await service.get_all(category, animal_type, season, sale_mode, limit)


@router.get("/top", response_model=List[Product])
async def get_top_products(limit: int = Query(5, le=50)):
    """Get top products by rank"""
    service = get_products_service()
    return await service.get_top(limit)


@router.get("/filters/options")
async def get_filter_options():
    """Get all available filter options"""
    service = get_products_service()
    return await service.get_filter_options()


@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """Get product by ID"""
    service = get_products_service()
    product = await service.get_by_id(product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    return product


@router.post("/", response_model=Product)
async def create_product(
    product_input: ProductCreate,
    user: UserWithRole = Depends(require_business_or_admin)
):
    """Create a new product (Business/Admin only)"""
    service = get_products_service()
    return await service.create(product_input)


@router.put("/{product_id}", response_model=Product)
async def update_product(
    product_id: str,
    update_data: ProductUpdate,
    user: UserWithRole = Depends(require_business_or_admin)
):
    """Update a product (Business/Admin only)"""
    service = get_products_service()
    product = await service.update(product_id, update_data)
    
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    return product


@router.delete("/{product_id}")
async def delete_product(
    product_id: str,
    user: UserWithRole = Depends(require_business_or_admin)
):
    """Delete a product (Business/Admin only)"""
    service = get_products_service()
    success = await service.delete(product_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    return {"success": True, "message": "Produit supprimé"}


# ==============================================
# SEARCH
# ==============================================

@router.post("/search")
async def search_products(request: ProductSearchRequest):
    """Advanced product search"""
    service = get_products_service()
    return await service.search(request)


# ==============================================
# TRACKING
# ==============================================

@router.post("/{product_id}/track/analyze")
async def track_analyze(product_id: str):
    """Track product analysis action"""
    service = get_products_service()
    success = await service.track_analyze(product_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    return {"success": True, "action": "analyze"}


@router.post("/{product_id}/track/compare")
async def track_compare(product_id: str):
    """Track product comparison action"""
    service = get_products_service()
    success = await service.track_compare(product_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    return {"success": True, "action": "compare"}


@router.post("/{product_id}/track/click")
async def track_click(product_id: str):
    """Track product click action"""
    service = get_products_service()
    success = await service.track_click(product_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    return {"success": True, "action": "click"}
