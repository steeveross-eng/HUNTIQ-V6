"""Admin Engine Service - MÉTIER

Business logic for administration.

Version: 1.0.0
"""

import os
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta
from pymongo import MongoClient

from .models import (
    Alert, AlertType, AlertSeverity,
    SiteSettings, MaintenanceMode, DashboardStats, AuditLog
)


class AdminService:
    """Service for administration"""
    
    # Default admin credentials (should be changed in production)
    DEFAULT_ADMIN_EMAIL = "admin@bionic.com"
    DEFAULT_ADMIN_PASSWORD = "Saturn5858*"
    
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'test_database')
        self._client = None
        self._db = None
    
    @property
    def db(self):
        """Lazy database connection"""
        if self._db is None:
            self._client = MongoClient(self.mongo_url)
            self._db = self._client[self.db_name]
        return self._db
    
    async def verify_admin_credentials(self, email: str, password: str) -> bool:
        """Verify admin login credentials"""
        # Check default admin first
        if email == self.DEFAULT_ADMIN_EMAIL and password == self.DEFAULT_ADMIN_PASSWORD:
            return True
        
        # Check database for admin users
        admin = self.db.admins.find_one({
            "email": email,
            "is_active": True
        })
        
        if admin:
            # In production, use proper password hashing
            return admin.get("password") == password
        
        return False
    
    async def get_dashboard_stats(self) -> DashboardStats:
        """Get dashboard statistics"""
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=7)
        month_start = today_start - timedelta(days=30)
        
        # Users
        total_users = self.db.users.count_documents({}) if "users" in self.db.list_collection_names() else 0
        new_users_today = self.db.users.count_documents({"created_at": {"$gte": today_start}}) if total_users else 0
        new_users_week = self.db.users.count_documents({"created_at": {"$gte": week_start}}) if total_users else 0
        
        # Orders
        total_orders = self.db.orders.count_documents({}) if "orders" in self.db.list_collection_names() else 0
        orders_today = self.db.orders.count_documents({"created_at": {"$gte": today_start}}) if total_orders else 0
        orders_week = self.db.orders.count_documents({"created_at": {"$gte": week_start}}) if total_orders else 0
        pending_orders = self.db.orders.count_documents({"status": "pending"}) if total_orders else 0
        
        # Revenue
        revenue_today = 0.0
        revenue_week = 0.0
        revenue_month = 0.0
        
        if "orders" in self.db.list_collection_names():
            pipeline_today = [
                {"$match": {"created_at": {"$gte": today_start}, "status": {"$ne": "cancelled"}}},
                {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
            ]
            result = list(self.db.orders.aggregate(pipeline_today))
            revenue_today = result[0]["total"] if result else 0.0
            
            pipeline_week = [
                {"$match": {"created_at": {"$gte": week_start}, "status": {"$ne": "cancelled"}}},
                {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
            ]
            result = list(self.db.orders.aggregate(pipeline_week))
            revenue_week = result[0]["total"] if result else 0.0
            
            pipeline_month = [
                {"$match": {"created_at": {"$gte": month_start}, "status": {"$ne": "cancelled"}}},
                {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
            ]
            result = list(self.db.orders.aggregate(pipeline_month))
            revenue_month = result[0]["total"] if result else 0.0
        
        # Products
        total_products = self.db.products.count_documents({}) if "products" in self.db.list_collection_names() else 0
        low_stock = self.db.products.count_documents({"stock": {"$lt": 10, "$gt": 0}}) if total_products else 0
        out_of_stock = self.db.products.count_documents({"stock": 0}) if total_products else 0
        
        # Analyses
        total_analyses = self.db.analyses.count_documents({}) if "analyses" in self.db.list_collection_names() else 0
        analyses_today = self.db.analyses.count_documents({"created_at": {"$gte": today_start}}) if total_analyses else 0
        
        # Alerts
        unread_alerts = self.db.alerts.count_documents({"is_read": False}) if "alerts" in self.db.list_collection_names() else 0
        
        # Active sessions
        active_sessions = self.db.user_sessions.count_documents({
            "is_active": True,
            "expires_at": {"$gt": now}
        }) if "user_sessions" in self.db.list_collection_names() else 0
        
        return DashboardStats(
            total_users=total_users,
            new_users_today=new_users_today,
            new_users_week=new_users_week,
            active_users_today=0,  # Would need activity tracking
            total_orders=total_orders,
            orders_today=orders_today,
            orders_week=orders_week,
            pending_orders=pending_orders,
            revenue_today=revenue_today,
            revenue_week=revenue_week,
            revenue_month=revenue_month,
            total_products=total_products,
            low_stock_products=low_stock,
            out_of_stock_products=out_of_stock,
            total_analyses=total_analyses,
            analyses_today=analyses_today,
            active_sessions=active_sessions,
            unread_alerts=unread_alerts
        )
    
    async def get_site_settings(self) -> SiteSettings:
        """Get site settings"""
        settings = self.db.site_settings.find_one({}, {"_id": 0})
        if settings:
            return SiteSettings(**settings)
        return SiteSettings()
    
    async def update_site_settings(self, settings: Dict[str, Any], admin_id: str) -> SiteSettings:
        """Update site settings"""
        settings["updated_at"] = datetime.now(timezone.utc)
        settings["updated_by"] = admin_id
        
        self.db.site_settings.update_one({}, {"$set": settings}, upsert=True)
        
        # Audit log
        await self.log_audit(admin_id, "update_site_settings", "settings", None, None, settings)
        
        return await self.get_site_settings()
    
    async def get_maintenance_mode(self) -> MaintenanceMode:
        """Get maintenance mode status"""
        mode = self.db.maintenance_mode.find_one({}, {"_id": 0})
        if mode:
            return MaintenanceMode(**mode)
        return MaintenanceMode()
    
    async def set_maintenance_mode(self, enabled: bool, admin_id: str, 
                                    title: str = None, message: str = None,
                                    estimated_end: datetime = None) -> MaintenanceMode:
        """Enable or disable maintenance mode"""
        mode_data = {
            "enabled": enabled,
            "allow_admin_access": True
        }
        
        if enabled:
            mode_data["enabled_at"] = datetime.now(timezone.utc)
            mode_data["enabled_by"] = admin_id
            if title:
                mode_data["title"] = title
            if message:
                mode_data["message"] = message
            if estimated_end:
                mode_data["estimated_end"] = estimated_end
        else:
            mode_data["enabled_at"] = None
            mode_data["enabled_by"] = ""
        
        self.db.maintenance_mode.update_one({}, {"$set": mode_data}, upsert=True)
        
        await self.log_audit(admin_id, "toggle_maintenance", "settings", None, None, mode_data)
        
        return await self.get_maintenance_mode()
    
    async def get_alerts(self, unread_only: bool = False, limit: int = 50) -> List[Alert]:
        """Get system alerts"""
        query = {}
        if unread_only:
            query["is_read"] = False
        
        cursor = self.db.alerts.find(query, {"_id": 0}).sort("created_at", -1).limit(limit)
        return [Alert(**doc) for doc in cursor]
    
    async def create_alert(self, alert_type: AlertType, severity: AlertSeverity,
                           title: str, message: str, data: Dict = None) -> Alert:
        """Create a system alert"""
        alert = Alert(
            type=alert_type,
            severity=severity,
            title=title,
            message=message,
            data=data or {}
        )
        
        alert_dict = alert.model_dump()
        alert_dict.pop("_id", None)
        self.db.alerts.insert_one(alert_dict)
        
        return alert
    
    async def mark_alert_read(self, alert_id: str) -> bool:
        """Mark alert as read"""
        result = self.db.alerts.update_one(
            {"id": alert_id},
            {"$set": {"is_read": True, "read_at": datetime.now(timezone.utc)}}
        )
        return result.modified_count > 0
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Mark alert as resolved"""
        result = self.db.alerts.update_one(
            {"id": alert_id},
            {"$set": {
                "is_resolved": True,
                "resolved_at": datetime.now(timezone.utc),
                "is_read": True,
                "read_at": datetime.now(timezone.utc)
            }}
        )
        return result.modified_count > 0
    
    async def log_audit(self, admin_id: str, action: str, resource_type: str,
                        resource_id: str = None, old_value: Dict = None,
                        new_value: Dict = None, ip_address: str = None):
        """Log admin action for audit"""
        # Get admin email
        admin = self.db.admins.find_one({"id": admin_id})
        admin_email = admin.get("email", "unknown") if admin else "unknown"
        
        log = AuditLog(
            admin_id=admin_id,
            admin_email=admin_email,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_value=old_value,
            new_value=new_value,
            ip_address=ip_address
        )
        
        log_dict = log.model_dump()
        log_dict.pop("_id", None)
        self.db.audit_logs.insert_one(log_dict)
    
    async def get_audit_logs(self, admin_id: str = None, 
                              resource_type: str = None,
                              limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit logs with optional filtering"""
        query = {}
        if admin_id:
            query["admin_id"] = admin_id
        if resource_type:
            query["resource_type"] = resource_type
        
        cursor = self.db.audit_logs.find(query, {"_id": 0}).sort("timestamp", -1).limit(limit)
        return list(cursor)
    
    async def generate_alerts(self) -> List[Alert]:
        """Generate alerts based on system state"""
        alerts = []
        
        # Check low stock products
        if "products" in self.db.list_collection_names():
            low_stock = list(self.db.products.find({"stock": {"$lt": 5, "$gt": 0}}, {"_id": 0, "name": 1, "stock": 1}))
            for product in low_stock[:5]:  # Limit to 5
                alert = await self.create_alert(
                    AlertType.STOCK_LOW,
                    AlertSeverity.WARNING,
                    f"Stock faible: {product.get('name', 'Produit')}",
                    f"Stock actuel: {product.get('stock', 0)} unités",
                    {"product_name": product.get('name')}
                )
                alerts.append(alert)
        
        # Check failed orders
        if "orders" in self.db.list_collection_names():
            failed = self.db.orders.count_documents({
                "status": "failed",
                "created_at": {"$gte": datetime.now(timezone.utc) - timedelta(days=1)}
            })
            if failed > 0:
                alert = await self.create_alert(
                    AlertType.ORDER_FAILED,
                    AlertSeverity.ERROR,
                    f"{failed} commande(s) échouée(s)",
                    "Des commandes ont échoué dans les dernières 24h",
                    {"count": failed}
                )
                alerts.append(alert)
        
        return alerts
