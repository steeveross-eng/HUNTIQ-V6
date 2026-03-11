"""Orders Engine Service - PHASE 7 EXTRACTION
Version: 1.0.0
"""

import os
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from pymongo import MongoClient

from .models import Order, OrderCreate, OrderUpdate, OrderCancellation, Commission


class OrdersService:
    """Service for order operations"""
    
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
    def orders(self):
        return self.db.orders
    
    @property
    def products(self):
        return self.db.products
    
    @property
    def suppliers(self):
        return self.db.suppliers
    
    @property
    def customers(self):
        return self.db.customers
    
    @property
    def commissions(self):
        return self.db.commissions
    
    # ===========================================
    # ORDERS CRUD
    # ===========================================
    
    async def get_all(
        self,
        status: Optional[str] = None,
        sale_mode: Optional[str] = None,
        limit: int = 500
    ) -> List[Order]:
        """Get all orders with optional filters"""
        query = {}
        if status:
            query["status"] = status
        if sale_mode:
            query["sale_mode"] = sale_mode
        
        orders = list(self.orders.find(query, {"_id": 0}).sort("created_at", -1).limit(limit))
        
        for order in orders:
            if isinstance(order.get('created_at'), str):
                order['created_at'] = datetime.fromisoformat(order['created_at'])
        
        return [Order(**o) for o in orders]
    
    async def get_by_id(self, order_id: str) -> Optional[Order]:
        """Get order by ID"""
        order = self.orders.find_one({"id": order_id}, {"_id": 0})
        if not order:
            return None
        
        if isinstance(order.get('created_at'), str):
            order['created_at'] = datetime.fromisoformat(order['created_at'])
        
        return Order(**order)
    
    async def create(self, order_input: OrderCreate) -> Order:
        """Create a new order with hybrid logic"""
        # Get product details
        product = self.products.find_one({"id": order_input.product_id}, {"_id": 0})
        if not product:
            raise ValueError("Product not found")
        
        # Determine sale mode (hybrid logic)
        sale_mode = product.get("sale_mode", "dropshipping")
        if sale_mode == "hybrid":
            if product.get("dropshipping_available", True):
                sale_mode = "dropshipping"
            else:
                sale_mode = "affiliation"
        
        # Get supplier info
        supplier_name = ""
        supplier_id = product.get("supplier_id")
        if supplier_id:
            supplier = self.suppliers.find_one({"id": supplier_id}, {"_id": 0})
            if supplier:
                supplier_name = supplier.get("name", "")
        
        # Calculate margins/commissions
        sale_price = product.get("price", 0) * order_input.quantity
        supplier_price = product.get("supplier_price", 0) * order_input.quantity
        affiliate_commission_percent = product.get("affiliate_commission", 0)
        
        if sale_mode == "dropshipping":
            net_margin = sale_price - supplier_price
            affiliate_commission_amount = 0
        else:  # affiliation
            affiliate_commission_amount = sale_price * (affiliate_commission_percent / 100)
            net_margin = affiliate_commission_amount
            supplier_price = 0
        
        # Create order
        order = Order(
            customer_id=order_input.customer_id,
            customer_name=order_input.customer_name,
            customer_email=order_input.customer_email,
            product_id=order_input.product_id,
            product_name=product.get("name", ""),
            supplier_id=supplier_id,
            supplier_name=supplier_name,
            sale_mode=sale_mode,
            quantity=order_input.quantity,
            sale_price=sale_price,
            supplier_price=supplier_price,
            affiliate_commission_percent=affiliate_commission_percent,
            affiliate_commission_amount=affiliate_commission_amount,
            net_margin=net_margin,
            status="pending"
        )
        
        doc = order.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        
        self.orders.insert_one(doc)
        
        # Update product orders count
        self.products.update_one({"id": order_input.product_id}, {"$inc": {"orders": 1}})
        
        # Update customer
        self.customers.update_one(
            {"id": order_input.customer_id},
            {
                "$addToSet": {"products_ordered": order_input.product_id},
                "$inc": {"total_orders": 1, "total_spent": sale_price}
            }
        )
        
        # Update supplier stats
        if supplier_id:
            self.suppliers.update_one(
                {"id": supplier_id},
                {
                    "$inc": {
                        "total_orders": 1,
                        "total_revenue_supplier": supplier_price,
                        "total_revenue_scent": net_margin
                    }
                }
            )
        
        # Create commission record
        commission = Commission(
            order_id=order.id,
            product_id=order_input.product_id,
            product_name=product.get("name", ""),
            supplier_id=supplier_id,
            supplier_name=supplier_name,
            customer_id=order_input.customer_id,
            commission_type="dropshipping_margin" if sale_mode == "dropshipping" else "affiliate",
            amount=net_margin,
            status="pending"
        )
        
        commission_doc = commission.model_dump()
        commission_doc['created_at'] = commission_doc['created_at'].isoformat()
        self.commissions.insert_one(commission_doc)
        
        return order
    
    async def update_status(self, order_id: str, update: OrderUpdate) -> Optional[Order]:
        """Update order status"""
        update_data = {}
        if update.status:
            update_data["status"] = update.status
            if update.status == "shipped":
                update_data["shipped_at"] = datetime.now(timezone.utc).isoformat()
            elif update.status == "delivered":
                update_data["delivered_at"] = datetime.now(timezone.utc).isoformat()
                # Confirm commission
                self.commissions.update_one(
                    {"order_id": order_id},
                    {"$set": {"status": "confirmed", "confirmed_at": datetime.now(timezone.utc).isoformat()}}
                )
        
        if not update_data:
            return None
        
        result = self.orders.find_one_and_update(
            {"id": order_id},
            {"$set": update_data},
            return_document=True
        )
        
        if not result:
            return None
        
        if isinstance(result.get('created_at'), str):
            result['created_at'] = datetime.fromisoformat(result['created_at'])
        
        return Order(**{k: v for k, v in result.items() if k != "_id"})
    
    async def cancel(self, order_id: str, cancellation: OrderCancellation) -> Dict[str, Any]:
        """Cancel an order"""
        order = self.orders.find_one({"id": order_id}, {"_id": 0})
        if not order:
            raise ValueError("Order not found")
        
        if order.get("status") == "cancelled":
            raise ValueError("Order already cancelled")
        
        update_data = {
            "status": "cancelled",
            "cancelled_at": datetime.now(timezone.utc).isoformat(),
            "cancellation_reason": cancellation.reason
        }
        
        # Get customer info
        customer_email = order.get("customer_email", "")
        customer_name = order.get("customer_name", "Client")
        
        if not customer_email and order.get("customer_id"):
            customer = self.customers.find_one({"id": order.get("customer_id")}, {"_id": 0})
            if customer:
                customer_email = customer.get("email", "")
                if not customer_name or customer_name == "Client":
                    customer_name = customer.get("name", "Client")
        
        products_list = order.get("products_list", [])
        if not products_list and order.get("product_name"):
            products_list = [order.get("product_name")]
        
        email_result = {"status": "skipped", "message": "Aucun email client disponible"}
        
        # Send cancellation email if requested
        if cancellation.send_email and customer_email:
            try:
                from email_service import send_cancellation_email
                email_result = await send_cancellation_email(
                    to_email=customer_email,
                    customer_name=customer_name or "Client",
                    products=products_list if products_list else ["Produit(s) commandé(s)"],
                    order_id=order_id
                )
                update_data["cancellation_email_sent"] = email_result.get("status") in ["sent", "simulated"]
            except Exception as e:
                email_result = {"status": "error", "message": str(e)}
        
        # Update order
        result = self.orders.find_one_and_update(
            {"id": order_id},
            {"$set": update_data},
            return_document=True
        )
        
        # Cancel associated commission
        self.commissions.update_one(
            {"order_id": order_id},
            {"$set": {"status": "cancelled"}}
        )
        
        if isinstance(result.get('created_at'), str):
            result['created_at'] = datetime.fromisoformat(result['created_at'])
        
        return {
            "success": True,
            "order": Order(**{k: v for k, v in result.items() if k != "_id"}),
            "email_notification": email_result
        }
    
    # ===========================================
    # COMMISSIONS
    # ===========================================
    
    async def get_commissions(
        self,
        status: Optional[str] = None,
        commission_type: Optional[str] = None,
        limit: int = 500
    ) -> List[Commission]:
        """Get all commissions"""
        query = {}
        if status:
            query["status"] = status
        if commission_type:
            query["commission_type"] = commission_type
        
        commissions = list(self.commissions.find(query, {"_id": 0}).sort("created_at", -1).limit(limit))
        
        for c in commissions:
            if isinstance(c.get('created_at'), str):
                c['created_at'] = datetime.fromisoformat(c['created_at'])
        
        return [Commission(**c) for c in commissions]
    
    async def mark_commission_paid(self, commission_id: str) -> Optional[Commission]:
        """Mark a commission as paid"""
        result = self.commissions.find_one_and_update(
            {"id": commission_id, "status": "confirmed"},
            {"$set": {"status": "paid", "paid_at": datetime.now(timezone.utc).isoformat()}},
            return_document=True
        )
        
        if not result:
            return None
        
        if isinstance(result.get('created_at'), str):
            result['created_at'] = datetime.fromisoformat(result['created_at'])
        
        return Commission(**{k: v for k, v in result.items() if k != "_id"})
    
    # ===========================================
    # STATS
    # ===========================================
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        total_orders = self.orders.count_documents({})
        total_commissions = self.commissions.count_documents({})
        
        by_status = {}
        pipeline = [{"$group": {"_id": "$status", "count": {"$sum": 1}}}]
        for doc in self.orders.aggregate(pipeline):
            by_status[doc["_id"]] = doc["count"]
        
        return {
            "engine": "orders_engine",
            "version": "1.0.0",
            "total_orders": total_orders,
            "total_commissions": total_commissions,
            "orders_by_status": by_status,
            "status": "operational"
        }


# Singleton instance
_service_instance = None

def get_orders_service() -> OrdersService:
    """Get singleton instance"""
    global _service_instance
    if _service_instance is None:
        _service_instance = OrdersService()
    return _service_instance
