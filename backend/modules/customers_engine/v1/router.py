"""Customers Engine Router
Version: 1.0.1
Security: @require_business_or_admin on sensitive endpoints (P0 - 11 Feb 2026)
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from pydantic import BaseModel
from .models import Customer, CustomerCreate, CustomerUpdate
from .service import get_customers_service

# Role-based access control
from modules.roles_engine.v1.dependencies import require_business_or_admin
from modules.roles_engine.v1.models import UserWithRole

router = APIRouter(prefix="/api/v1/customers", tags=["Customers Engine"])

class HealthResponse(BaseModel):
    status: str
    engine: str
    version: str
    message: str

@router.get("/health", response_model=HealthResponse)
async def health_check():
    service = get_customers_service()
    stats = await service.get_stats()
    return HealthResponse(
        status="operational", engine="customers_engine", version="1.0.1",
        message=f"Engine opérationnel - {stats['total_customers']} clients"
    )

@router.get("/stats")
async def get_stats():
    service = get_customers_service()
    return await service.get_stats()

@router.get("/", response_model=List[Customer])
async def get_customers(
    user: UserWithRole = Depends(require_business_or_admin)
):
    """Get all customers (Business/Admin only)"""
    service = get_customers_service()
    return await service.get_all()

@router.get("/{customer_id}", response_model=Customer)
async def get_customer(
    customer_id: str,
    user: UserWithRole = Depends(require_business_or_admin)
):
    """Get customer by ID (Business/Admin only)"""
    service = get_customers_service()
    customer = await service.get_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    return customer

@router.get("/session/{session_id}", response_model=Customer)
async def get_customer_by_session(session_id: str):
    """Get customer by session ID (Public - self-identification)"""
    service = get_customers_service()
    customer = await service.get_by_session(session_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    return customer

@router.post("/", response_model=Customer)
async def create_customer(customer_input: CustomerCreate):
    """Create a new customer (Public - registration)"""
    service = get_customers_service()
    return await service.create(customer_input)

@router.put("/{customer_id}", response_model=Customer)
async def update_customer(
    customer_id: str,
    update_data: CustomerUpdate,
    user: UserWithRole = Depends(require_business_or_admin)
):
    """Update a customer (Business/Admin only)"""
    service = get_customers_service()
    customer = await service.update(customer_id, update_data)
    if not customer:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    return customer
