"""Cart Engine Router"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .models import CartItem, CartItemCreate, CartItemUpdate
from .service import get_cart_service

router = APIRouter(prefix="/api/v1/cart", tags=["Cart Engine"])

class HealthResponse(BaseModel):
    status: str
    engine: str
    version: str
    message: str

@router.get("/health", response_model=HealthResponse)
async def health_check():
    service = get_cart_service()
    stats = await service.get_stats()
    return HealthResponse(
        status="operational", engine="cart_engine", version="1.0.0",
        message=f"Engine opérationnel - {stats['total_items']} items"
    )

@router.get("/stats")
async def get_stats():
    service = get_cart_service()
    return await service.get_stats()

@router.get("/session/{session_id}")
async def get_cart(session_id: str):
    service = get_cart_service()
    return await service.get_by_session(session_id)

@router.post("/", response_model=CartItem)
async def add_to_cart(item_input: CartItemCreate):
    service = get_cart_service()
    return await service.add_item(item_input)

@router.put("/{item_id}", response_model=CartItem)
async def update_cart_item(item_id: str, update_data: CartItemUpdate):
    service = get_cart_service()
    item = await service.update_item(item_id, update_data)
    if not item:
        raise HTTPException(status_code=404, detail="Item non trouvé")
    return item

@router.delete("/{item_id}")
async def delete_cart_item(item_id: str):
    service = get_cart_service()
    success = await service.delete_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item non trouvé")
    return {"success": True, "message": "Item supprimé"}

@router.delete("/session/{session_id}/clear")
async def clear_cart(session_id: str):
    service = get_cart_service()
    count = await service.clear_session(session_id)
    return {"success": True, "items_removed": count}
