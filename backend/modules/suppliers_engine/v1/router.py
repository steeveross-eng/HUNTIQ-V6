"""Suppliers Engine Router
Version: 1.0.1
Security: @require_business_or_admin on all endpoints (P0 - 11 Feb 2026)
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from pydantic import BaseModel
from .models import Supplier, SupplierCreate, SupplierUpdate
from .service import get_suppliers_service

# Role-based access control
from modules.roles_engine.v1.dependencies import require_business_or_admin
from modules.roles_engine.v1.models import UserWithRole

router = APIRouter(prefix="/api/v1/suppliers", tags=["Suppliers Engine"])

class HealthResponse(BaseModel):
    status: str
    engine: str
    version: str
    message: str

@router.get("/health", response_model=HealthResponse)
async def health_check():
    service = get_suppliers_service()
    stats = await service.get_stats()
    return HealthResponse(
        status="operational", engine="suppliers_engine", version="1.0.1",
        message=f"Engine opérationnel - {stats['total_suppliers']} fournisseurs"
    )

@router.get("/stats")
async def get_stats():
    service = get_suppliers_service()
    return await service.get_stats()

@router.get("/", response_model=List[Supplier])
async def get_suppliers(
    is_active: Optional[bool] = None,
    user: UserWithRole = Depends(require_business_or_admin)
):
    """Get all suppliers (Business/Admin only)"""
    service = get_suppliers_service()
    return await service.get_all(is_active)

@router.get("/{supplier_id}", response_model=Supplier)
async def get_supplier(
    supplier_id: str,
    user: UserWithRole = Depends(require_business_or_admin)
):
    """Get supplier by ID (Business/Admin only)"""
    service = get_suppliers_service()
    supplier = await service.get_by_id(supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Fournisseur non trouvé")
    return supplier

@router.post("/", response_model=Supplier)
async def create_supplier(
    supplier_input: SupplierCreate,
    user: UserWithRole = Depends(require_business_or_admin)
):
    """Create a new supplier (Business/Admin only)"""
    service = get_suppliers_service()
    return await service.create(supplier_input)

@router.put("/{supplier_id}", response_model=Supplier)
async def update_supplier(
    supplier_id: str,
    update_data: SupplierUpdate,
    user: UserWithRole = Depends(require_business_or_admin)
):
    """Update a supplier (Business/Admin only)"""
    service = get_suppliers_service()
    supplier = await service.update(supplier_id, update_data)
    if not supplier:
        raise HTTPException(status_code=404, detail="Fournisseur non trouvé")
    return supplier

@router.delete("/{supplier_id}")
async def delete_supplier(
    supplier_id: str,
    user: UserWithRole = Depends(require_business_or_admin)
):
    """Delete a supplier (Business/Admin only)"""
    service = get_suppliers_service()
    success = await service.delete(supplier_id)
    if not success:
        raise HTTPException(status_code=404, detail="Fournisseur non trouvé")
    return {"success": True, "message": "Fournisseur supprimé"}
