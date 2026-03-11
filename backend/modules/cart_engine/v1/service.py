"""Cart Engine Service"""
import os
from typing import Optional, List, Dict, Any
from pymongo import MongoClient
from .models import CartItem, CartItemCreate, CartItemUpdate

class CartService:
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'test_database')
        self._client = None
        self._db = None
    
    @property
    def db(self):
        if self._db is None:
            self._client = MongoClient(self.mongo_url)
            self._db = self._client[self.db_name]
        return self._db
    
    @property
    def cart(self):
        return self.db.cart
    
    @property
    def products(self):
        return self.db.products
    
    async def get_by_session(self, session_id: str) -> List[Dict[str, Any]]:
        items = list(self.cart.find({"session_id": session_id}, {"_id": 0}))
        enriched = []
        for item in items:
            product = self.products.find_one({"id": item["product_id"]}, {"_id": 0})
            if product:
                enriched.append({
                    **item,
                    "product": product
                })
        return enriched
    
    async def add_item(self, item_input: CartItemCreate) -> CartItem:
        existing = self.cart.find_one({
            "session_id": item_input.session_id,
            "product_id": item_input.product_id
        }, {"_id": 0})
        
        if existing:
            new_qty = existing.get("quantity", 1) + item_input.quantity
            self.cart.update_one(
                {"id": existing["id"]},
                {"$set": {"quantity": new_qty}}
            )
            return CartItem(**{**existing, "quantity": new_qty})
        
        item = CartItem(**item_input.model_dump())
        self.cart.insert_one(item.model_dump())
        return item
    
    async def update_item(self, item_id: str, update_data: CartItemUpdate) -> Optional[CartItem]:
        result = self.cart.find_one_and_update(
            {"id": item_id},
            {"$set": {"quantity": update_data.quantity}},
            return_document=True
        )
        if not result:
            return None
        return CartItem(**{k: v for k, v in result.items() if k != "_id"})
    
    async def delete_item(self, item_id: str) -> bool:
        result = self.cart.delete_one({"id": item_id})
        return result.deleted_count > 0
    
    async def clear_session(self, session_id: str) -> int:
        result = self.cart.delete_many({"session_id": session_id})
        return result.deleted_count
    
    async def get_stats(self) -> Dict[str, Any]:
        return {
            "engine": "cart_engine",
            "version": "1.0.0",
            "total_items": self.cart.count_documents({}),
            "status": "operational"
        }

_service_instance = None
def get_cart_service() -> CartService:
    global _service_instance
    if _service_instance is None:
        _service_instance = CartService()
    return _service_instance
