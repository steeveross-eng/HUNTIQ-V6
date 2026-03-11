"""Affiliate Engine Service"""
import os
from typing import List, Dict, Any
from datetime import datetime, timezone
from pymongo import MongoClient
from .models import AffiliateClick

class AffiliateService:
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
    def clicks(self):
        return self.db.affiliate_clicks
    
    @property
    def products(self):
        return self.db.products
    
    @property
    def customers(self):
        return self.db.customers
    
    @property
    def commissions(self):
        return self.db.commissions
    
    async def record_click(self, product_id: str, session_id: str) -> Dict[str, Any]:
        """Record an affiliate click"""
        product = self.products.find_one({"id": product_id}, {"_id": 0})
        if not product:
            raise ValueError("Product not found")
        
        affiliate_link = product.get("affiliate_link", "")
        if not affiliate_link:
            raise ValueError("No affiliate link for this product")
        
        customer = self.customers.find_one({"session_id": session_id})
        customer_id = customer.get("id") if customer else None
        
        click = AffiliateClick(
            customer_id=customer_id,
            session_id=session_id,
            product_id=product_id,
            product_name=product.get("name", ""),
            supplier_id=product.get("supplier_id"),
            affiliate_link=affiliate_link
        )
        
        doc = click.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        
        self.clicks.insert_one(doc)
        self.products.update_one({"id": product_id}, {"$inc": {"clicks": 1}})
        
        return {"click_id": click.id, "redirect_url": affiliate_link}
    
    async def get_all_clicks(self, limit: int = 500) -> List[AffiliateClick]:
        """Get all affiliate clicks"""
        clicks = list(self.clicks.find({}, {"_id": 0}).sort("created_at", -1).limit(limit))
        for click in clicks:
            if isinstance(click.get('created_at'), str):
                click['created_at'] = datetime.fromisoformat(click['created_at'])
        return [AffiliateClick(**c) for c in clicks]
    
    async def confirm_sale(self, click_id: str, commission_amount: float) -> Dict[str, Any]:
        """Confirm an affiliate sale"""
        click = self.clicks.find_one({"id": click_id})
        if not click:
            raise ValueError("Affiliate click not found")
        
        self.clicks.update_one(
            {"id": click_id},
            {
                "$set": {
                    "converted": True,
                    "commission_amount": commission_amount,
                    "converted_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        # Create commission record
        from modules.orders_engine.v1.models import Commission
        commission = Commission(
            affiliate_click_id=click_id,
            product_id=click.get("product_id"),
            product_name=click.get("product_name"),
            supplier_id=click.get("supplier_id"),
            customer_id=click.get("customer_id"),
            commission_type="affiliate",
            amount=commission_amount,
            status="confirmed"
        )
        
        commission_doc = commission.model_dump()
        commission_doc['created_at'] = commission_doc['created_at'].isoformat()
        commission_doc['confirmed_at'] = datetime.now(timezone.utc).isoformat()
        
        self.commissions.insert_one(commission_doc)
        
        return {"commission_id": commission.id}
    
    async def get_stats(self) -> Dict[str, Any]:
        total = self.clicks.count_documents({})
        converted = self.clicks.count_documents({"converted": True})
        return {
            "engine": "affiliate_engine",
            "version": "1.0.0",
            "total_clicks": total,
            "converted_clicks": converted,
            "conversion_rate": round(converted / total * 100, 2) if total > 0 else 0,
            "status": "operational"
        }

_service_instance = None
def get_affiliate_service() -> AffiliateService:
    global _service_instance
    if _service_instance is None:
        _service_instance = AffiliateService()
    return _service_instance
