"""
E-Commerce Admin Service - V5-ULTIME Administration Premium
===========================================================

Service d'administration E-Commerce pour la gestion des:
- Dashboard stats (produits, ventes, marges)
- Commandes (orders)
- Produits (products)
- Fournisseurs (suppliers)
- Clients (customers)
- Commissions (affiliate/dropshipping)
- Performance (analytics produits)

Module isolé - aucun import croisé.
"""

from datetime import datetime, timezone
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class EcommerceAdminService:
    """Service isolé pour l'administration E-Commerce"""
    
    # ============ DASHBOARD STATS ============
    @staticmethod
    async def get_dashboard_stats(db) -> dict:
        """Statistiques globales E-Commerce"""
        # Comptages
        products_count = await db.products.count_documents({})
        orders_count = await db.orders.count_documents({})
        suppliers_count = await db.suppliers.count_documents({})
        customers_count = await db.customers.count_documents({})
        
        # Ventes totales
        orders = await db.orders.find(
            {"status": {"$ne": "cancelled"}},
            {"sale_price": 1, "net_margin": 1, "sale_mode": 1, "_id": 0}
        ).to_list(length=10000)
        
        total_sales = sum(o.get("sale_price", 0) for o in orders)
        total_margins = sum(o.get("net_margin", 0) for o in orders)
        
        # Ventes par mode
        dropshipping_sales = sum(
            o.get("sale_price", 0) for o in orders 
            if o.get("sale_mode") == "dropshipping"
        )
        affiliate_sales = sum(
            o.get("sale_price", 0) for o in orders 
            if o.get("sale_mode") == "affiliation"
        )
        
        # Commissions
        commissions = await db.commissions.find(
            {}, {"amount": 1, "status": 1, "_id": 0}
        ).to_list(length=10000)
        
        pending_commissions = sum(
            c.get("amount", 0) for c in commissions 
            if c.get("status") == "pending"
        )
        confirmed_commissions = sum(
            c.get("amount", 0) for c in commissions 
            if c.get("status") == "confirmed"
        )
        paid_commissions = sum(
            c.get("amount", 0) for c in commissions 
            if c.get("status") == "paid"
        )
        
        return {
            "success": True,
            "stats": {
                "products_count": products_count,
                "orders_count": orders_count,
                "suppliers_count": suppliers_count,
                "customers_count": customers_count,
                "total_sales": round(total_sales, 2),
                "total_margins": round(total_margins, 2),
                "margin_rate": round((total_margins / max(total_sales, 1)) * 100, 1),
                "dropshipping_sales": round(dropshipping_sales, 2),
                "affiliate_sales": round(affiliate_sales, 2),
                "pending_commissions": round(pending_commissions, 2),
                "confirmed_commissions": round(confirmed_commissions, 2),
                "paid_commissions": round(paid_commissions, 2)
            }
        }
    
    # ============ ORDERS ============
    @staticmethod
    async def get_orders(db, limit: int = 50, status: Optional[str] = None, skip: int = 0) -> dict:
        """Liste des commandes"""
        query = {}
        if status:
            query["status"] = status
        
        orders = await db.orders.find(
            query, {"_id": 0}
        ).sort("created_at", -1).skip(skip).limit(limit).to_list(length=limit)
        
        total = await db.orders.count_documents(query)
        
        # Stats par statut
        status_counts = {}
        for s in ["pending", "processing", "shipped", "delivered", "cancelled"]:
            status_counts[s] = await db.orders.count_documents({"status": s})
        
        return {
            "success": True,
            "total": total,
            "status_counts": status_counts,
            "orders": orders
        }
    
    @staticmethod
    async def update_order_status(db, order_id: str, new_status: str) -> dict:
        """Mettre à jour le statut d'une commande"""
        valid_statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
        if new_status not in valid_statuses:
            return {"success": False, "error": f"Invalid status. Must be one of: {valid_statuses}"}
        
        result = await db.orders.update_one(
            {"id": order_id},
            {
                "$set": {
                    "status": new_status,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        if result.matched_count == 0:
            return {"success": False, "error": "Order not found"}
        
        return {"success": True, "order_id": order_id, "new_status": new_status}
    
    # ============ PRODUCTS ============
    @staticmethod
    async def get_products(db, limit: int = 50, category: Optional[str] = None) -> dict:
        """Liste des produits"""
        query = {}
        if category:
            query["category"] = category
        
        products = await db.products.find(
            query, {"_id": 0}
        ).sort("rank", 1).limit(limit).to_list(length=limit)
        
        total = await db.products.count_documents(query)
        
        # Catégories disponibles
        categories = await db.products.distinct("category")
        
        return {
            "success": True,
            "total": total,
            "categories": categories,
            "products": products
        }
    
    @staticmethod
    async def create_product(db, product_data: dict) -> dict:
        """Créer un nouveau produit"""
        import uuid
        
        product = {
            "id": str(uuid.uuid4()),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            **product_data
        }
        
        await db.products.insert_one(product)
        
        # Remove _id for response
        product.pop("_id", None)
        
        return {"success": True, "product": product}
    
    @staticmethod
    async def update_product(db, product_id: str, updates: dict) -> dict:
        """Mettre à jour un produit"""
        updates["updated_at"] = datetime.now(timezone.utc)
        
        result = await db.products.update_one(
            {"id": product_id},
            {"$set": updates}
        )
        
        if result.matched_count == 0:
            return {"success": False, "error": "Product not found"}
        
        return {"success": True, "product_id": product_id, "updated": True}
    
    @staticmethod
    async def delete_product(db, product_id: str) -> dict:
        """Supprimer un produit"""
        result = await db.products.delete_one({"id": product_id})
        
        if result.deleted_count == 0:
            return {"success": False, "error": "Product not found"}
        
        return {"success": True, "product_id": product_id, "deleted": True}
    
    # ============ SUPPLIERS ============
    @staticmethod
    async def get_suppliers(db, limit: int = 50, partnership_type: Optional[str] = None) -> dict:
        """Liste des fournisseurs"""
        query = {}
        if partnership_type:
            query["partnership_type"] = partnership_type
        
        suppliers = await db.suppliers.find(
            query, {"_id": 0}
        ).sort("name", 1).limit(limit).to_list(length=limit)
        
        total = await db.suppliers.count_documents(query)
        
        return {
            "success": True,
            "total": total,
            "suppliers": suppliers
        }
    
    @staticmethod
    async def create_supplier(db, supplier_data: dict) -> dict:
        """Créer un nouveau fournisseur"""
        import uuid
        
        supplier = {
            "id": str(uuid.uuid4()),
            "created_at": datetime.now(timezone.utc),
            "total_orders": 0,
            "total_revenue_supplier": 0,
            "total_revenue_scent": 0,
            **supplier_data
        }
        
        await db.suppliers.insert_one(supplier)
        supplier.pop("_id", None)
        
        return {"success": True, "supplier": supplier}
    
    # ============ CUSTOMERS ============
    @staticmethod
    async def get_customers(db, limit: int = 50, sort_by: str = "total_spent") -> dict:
        """Liste des clients"""
        sort_field = sort_by if sort_by in ["total_spent", "total_orders", "created_at"] else "total_spent"
        
        customers = await db.customers.find(
            {}, {"_id": 0}
        ).sort(sort_field, -1).limit(limit).to_list(length=limit)
        
        total = await db.customers.count_documents({})
        
        # Stats
        total_ltv = sum(c.get("total_spent", 0) for c in customers)
        avg_ltv = total_ltv / max(len(customers), 1)
        
        return {
            "success": True,
            "total": total,
            "total_ltv": round(total_ltv, 2),
            "average_ltv": round(avg_ltv, 2),
            "customers": customers
        }
    
    # ============ COMMISSIONS ============
    @staticmethod
    async def get_commissions(db, limit: int = 50, status: Optional[str] = None) -> dict:
        """Liste des commissions"""
        query = {}
        if status:
            query["status"] = status
        
        commissions = await db.commissions.find(
            query, {"_id": 0}
        ).sort("created_at", -1).limit(limit).to_list(length=limit)
        
        total = await db.commissions.count_documents(query)
        
        # Stats par type
        by_type = {}
        for c in commissions:
            ctype = c.get("commission_type", "unknown")
            if ctype not in by_type:
                by_type[ctype] = {"count": 0, "total": 0}
            by_type[ctype]["count"] += 1
            by_type[ctype]["total"] += c.get("amount", 0)
        
        return {
            "success": True,
            "total": total,
            "by_type": by_type,
            "commissions": commissions
        }
    
    @staticmethod
    async def update_commission_status(db, commission_id: str, new_status: str) -> dict:
        """Mettre à jour le statut d'une commission"""
        valid_statuses = ["pending", "confirmed", "paid"]
        if new_status not in valid_statuses:
            return {"success": False, "error": f"Invalid status. Must be one of: {valid_statuses}"}
        
        result = await db.commissions.update_one(
            {"id": commission_id},
            {
                "$set": {
                    "status": new_status,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        if result.matched_count == 0:
            return {"success": False, "error": "Commission not found"}
        
        return {"success": True, "commission_id": commission_id, "new_status": new_status}
    
    # ============ PERFORMANCE / ANALYTICS ============
    @staticmethod
    async def get_performance_report(db) -> dict:
        """Rapport de performance des produits"""
        products = await db.products.find(
            {}, {"_id": 0, "id": 1, "name": 1, "views": 1, "clicks": 1, "orders": 1, "overall_conversion_rate": 1}
        ).to_list(length=1000)
        
        # Most viewed
        most_viewed = sorted(
            [p for p in products if p.get("views", 0) > 0],
            key=lambda x: x.get("views", 0),
            reverse=True
        )[:10]
        
        # Most ordered
        most_ordered = sorted(
            [p for p in products if p.get("orders", 0) > 0],
            key=lambda x: x.get("orders", 0),
            reverse=True
        )[:10]
        
        # Most clicked
        most_clicked = sorted(
            [p for p in products if p.get("clicks", 0) > 0],
            key=lambda x: x.get("clicks", 0),
            reverse=True
        )[:10]
        
        # Best conversion
        best_conversion = sorted(
            [p for p in products if p.get("overall_conversion_rate", 0) > 0],
            key=lambda x: x.get("overall_conversion_rate", 0),
            reverse=True
        )[:10]
        
        return {
            "success": True,
            "report": {
                "most_viewed": most_viewed,
                "most_ordered": most_ordered,
                "most_clicked": most_clicked,
                "best_conversion": best_conversion
            }
        }
    
    # ============ ALERTS ============
    @staticmethod
    async def get_alerts(db, limit: int = 20, unread_only: bool = False) -> dict:
        """Liste des alertes admin"""
        query = {}
        if unread_only:
            query["is_read"] = False
        
        alerts = await db.admin_alerts.find(
            query, {"_id": 0}
        ).sort("created_at", -1).limit(limit).to_list(length=limit)
        
        unread_count = await db.admin_alerts.count_documents({"is_read": False})
        
        return {
            "success": True,
            "unread_count": unread_count,
            "alerts": alerts
        }
