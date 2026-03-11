"""Suppliers Engine Service"""
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
from pymongo import MongoClient
from .models import Supplier, SupplierCreate, SupplierUpdate

class SuppliersService:
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
    def collection(self):
        return self.db.suppliers
    
    async def get_all(self, is_active: Optional[bool] = None) -> List[Supplier]:
        query = {} if is_active is None else {"is_active": is_active}
        suppliers = list(self.collection.find(query, {"_id": 0}).limit(100))
        for s in suppliers:
            if isinstance(s.get('created_at'), str):
                s['created_at'] = datetime.fromisoformat(s['created_at'])
        return [Supplier(**s) for s in suppliers]
    
    async def get_by_id(self, supplier_id: str) -> Optional[Supplier]:
        supplier = self.collection.find_one({"id": supplier_id}, {"_id": 0})
        if not supplier:
            return None
        if isinstance(supplier.get('created_at'), str):
            supplier['created_at'] = datetime.fromisoformat(supplier['created_at'])
        return Supplier(**supplier)
    
    async def create(self, supplier_input: SupplierCreate) -> Supplier:
        supplier = Supplier(**supplier_input.model_dump())
        doc = supplier.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        self.collection.insert_one(doc)
        return supplier
    
    async def update(self, supplier_id: str, update_data: SupplierUpdate) -> Optional[Supplier]:
        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
        if not update_dict:
            return await self.get_by_id(supplier_id)
        self.collection.update_one({"id": supplier_id}, {"$set": update_dict})
        return await self.get_by_id(supplier_id)
    
    async def delete(self, supplier_id: str) -> bool:
        result = self.collection.delete_one({"id": supplier_id})
        return result.deleted_count > 0
    
    async def get_stats(self) -> Dict[str, Any]:
        return {
            "engine": "suppliers_engine",
            "version": "1.0.0",
            "total_suppliers": self.collection.count_documents({}),
            "active_suppliers": self.collection.count_documents({"is_active": True}),
            "status": "operational"
        }

_service_instance = None
def get_suppliers_service() -> SuppliersService:
    global _service_instance
    if _service_instance is None:
        _service_instance = SuppliersService()
    return _service_instance
