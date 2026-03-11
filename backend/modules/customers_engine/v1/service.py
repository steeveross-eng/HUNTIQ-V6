"""Customers Engine Service"""
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
from pymongo import MongoClient
from .models import Customer, CustomerCreate, CustomerUpdate

class CustomersService:
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
        return self.db.customers
    
    async def get_all(self, limit: int = 100) -> List[Customer]:
        customers = list(self.collection.find({}, {"_id": 0}).limit(limit))
        for c in customers:
            if isinstance(c.get('created_at'), str):
                c['created_at'] = datetime.fromisoformat(c['created_at'])
        return [Customer(**c) for c in customers]
    
    async def get_by_id(self, customer_id: str) -> Optional[Customer]:
        customer = self.collection.find_one({"id": customer_id}, {"_id": 0})
        if not customer:
            return None
        if isinstance(customer.get('created_at'), str):
            customer['created_at'] = datetime.fromisoformat(customer['created_at'])
        return Customer(**customer)
    
    async def get_by_session(self, session_id: str) -> Optional[Customer]:
        customer = self.collection.find_one({"session_id": session_id}, {"_id": 0})
        if not customer:
            return None
        if isinstance(customer.get('created_at'), str):
            customer['created_at'] = datetime.fromisoformat(customer['created_at'])
        return Customer(**customer)
    
    async def create(self, customer_input: CustomerCreate) -> Customer:
        customer = Customer(**customer_input.model_dump())
        doc = customer.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        self.collection.insert_one(doc)
        return customer
    
    async def update(self, customer_id: str, update_data: CustomerUpdate) -> Optional[Customer]:
        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
        if not update_dict:
            return await self.get_by_id(customer_id)
        self.collection.update_one({"id": customer_id}, {"$set": update_dict})
        return await self.get_by_id(customer_id)
    
    async def get_stats(self) -> Dict[str, Any]:
        return {
            "engine": "customers_engine",
            "version": "1.0.0",
            "total_customers": self.collection.count_documents({}),
            "status": "operational"
        }

_service_instance = None
def get_customers_service() -> CustomersService:
    global _service_instance
    if _service_instance is None:
        _service_instance = CustomersService()
    return _service_instance
