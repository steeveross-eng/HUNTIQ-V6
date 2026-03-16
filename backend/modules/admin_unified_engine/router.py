"""
Admin Unified Engine Router - V5-ULTIME-FUSION
===============================================

Fusion de admin_engine (V4) + admin_advanced_engine (BASE)

Endpoints unifiés:
- /api/v1/admin/* - Core admin functions
- /api/v1/admin/brand/* - Brand identity (ex admin-advanced)
- /api/v1/admin/features/* - Feature controls (ex admin-advanced)
- /api/v1/admin/site-access/* - Site access control (ex admin-advanced)

Version: 1.0.0
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from enum import Enum
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/admin", tags=["Admin Unified Engine"])

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'bionic_db')
_client = None
_db = None

def get_db():
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(MONGO_URL)
        _db = _client[DB_NAME]
    return _db

# ==============================================
# MODELS
# ==============================================

class AlertType(str, Enum):
    SYSTEM = "system"
    ORDER = "order"
    STOCK = "stock"
    USER = "user"
    SECURITY = "security"

class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class BrandIdentity(BaseModel):
    logo_url: Optional[str] = None
    primary_color: str = "#f5a623"
    secondary_color: str = "#1a1a1a"
    site_name: str = "BIONIC HUNT/Chasse"
    tagline: Optional[str] = None

class FeatureControl(BaseModel):
    feature_id: str
    enabled: bool = True
    config: Optional[Dict[str, Any]] = None

class MaintenanceMode(BaseModel):
    enabled: bool = False
    message: str = "Site en maintenance"
    title: Optional[str] = None
    estimated_end: Optional[str] = None

class SiteAccess(BaseModel):
    public_access: bool = True
    require_auth: bool = False
    allowed_ips: List[str] = []

class SiteSettings(BaseModel):
    site_name: str = "BIONIC HUNT/Chasse"
    tagline: str = "Chasse Bionic™"
    contact_email: str = "contact@huntiq.ca"
    support_phone: Optional[str] = None
    social_links: Dict[str, str] = {}
    features_enabled: Dict[str, bool] = {}

class AdminLogin(BaseModel):
    email: str
    password: str

# ==============================================
# MODULE INFO
# ==============================================

@router.get("/")
async def admin_engine_info():
    """Get admin unified engine information"""
    return {
        "module": "admin_unified_engine",
        "version": "1.0.0",
        "description": "Administration unifiée V5-ULTIME-FUSION",
        "fusion": ["admin_engine (V4)", "admin_advanced_engine (BASE)"],
        "features": [
            "Dashboard statistics",
            "Site settings",
            "Maintenance mode",
            "Alert management",
            "Audit logging",
            "Brand identity",
            "Feature controls",
            "Site access control"
        ],
        "endpoints": {
            "core": ["/dashboard", "/settings", "/maintenance", "/alerts", "/audit-logs", "/health"],
            "brand": ["/brand"],
            "features": ["/features", "/features/{feature_id}"],
            "access": ["/site-access"]
        }
    }

# ==============================================
# AUTHENTICATION
# ==============================================

@router.post("/login")
async def admin_login(credentials: AdminLogin):
    """Admin login endpoint"""
    db = get_db()
    
    # Check credentials
    admin = await db.admins.find_one({"email": credentials.email}, {"_id": 0})
    if not admin:
        # Default admin check
        if credentials.email == "admin@huntiq.ca" and credentials.password == "Saturn5858*":
            import secrets
            token = secrets.token_urlsafe(32)
            return {
                "success": True,
                "message": "Login successful (default admin)",
                "email": credentials.email,
                "token": token,
                "is_admin": True
            }
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password (simplified - use proper hashing in production)
    if admin.get("password") != credentials.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    import secrets
    token = secrets.token_urlsafe(32)
    
    return {
        "success": True,
        "message": "Login successful",
        "email": credentials.email,
        "token": token,
        "is_admin": True
    }

# ==============================================
# DASHBOARD & STATS
# ==============================================

@router.get("/dashboard")
async def get_dashboard():
    """Get dashboard statistics"""
    db = get_db()
    
    # Get counts
    products_count = await db.products.count_documents({})
    orders_count = await db.orders.count_documents({})
    customers_count = await db.customers.count_documents({})
    suppliers_count = await db.suppliers.count_documents({})
    
    # Get sales totals
    pipeline = [
        {"$group": {
            "_id": None,
            "total_sales": {"$sum": "$sale_price"},
            "total_margins": {"$sum": "$net_margin"}
        }}
    ]
    sales_result = await db.orders.aggregate(pipeline).to_list(1)
    total_sales = sales_result[0]["total_sales"] if sales_result else 0
    total_margins = sales_result[0]["total_margins"] if sales_result else 0
    
    # Get alerts count
    unread_alerts = await db.admin_alerts.count_documents({"is_read": False})
    
    return {
        "success": True,
        "stats": {
            "products_count": products_count,
            "orders_count": orders_count,
            "customers_count": customers_count,
            "suppliers_count": suppliers_count,
            "total_sales": total_sales,
            "total_margins": total_margins,
            "unread_alerts": unread_alerts,
            "active_sessions": 0,
            "pending_orders": await db.orders.count_documents({"status": "pending"}),
            "out_of_stock_products": 0
        }
    }

# ==============================================
# SITE SETTINGS
# ==============================================

@router.get("/settings")
async def get_site_settings():
    """Get site settings"""
    db = get_db()
    settings = await db.site_settings.find_one({}, {"_id": 0})
    
    if not settings:
        settings = SiteSettings().dict()
    
    return {"success": True, "settings": settings}

@router.put("/settings")
async def update_site_settings(settings: dict):
    """Update site settings"""
    db = get_db()
    
    settings["updated_at"] = datetime.now(timezone.utc)
    
    await db.site_settings.update_one(
        {},
        {"$set": settings},
        upsert=True
    )
    
    return {"success": True, "message": "Settings updated", "settings": settings}

# ==============================================
# MAINTENANCE MODE (Unified from V4 + BASE)
# ==============================================

@router.get("/maintenance")
async def get_maintenance_status():
    """Get maintenance mode status"""
    db = get_db()
    mode = await db.maintenance_mode.find_one({}, {"_id": 0})
    
    if not mode:
        mode = {"enabled": False, "message": "Site en maintenance"}
    
    return {"success": True, "maintenance": mode}

@router.put("/maintenance")
async def set_maintenance_mode(mode: MaintenanceMode):
    """Enable or disable maintenance mode"""
    db = get_db()
    
    mode_dict = mode.dict()
    mode_dict["updated_at"] = datetime.now(timezone.utc)
    
    await db.maintenance_mode.update_one(
        {},
        {"$set": mode_dict},
        upsert=True
    )
    
    return {
        "success": True,
        "message": "Maintenance mode " + ("enabled" if mode.enabled else "disabled"),
        "maintenance": mode_dict
    }

# ==============================================
# ALERTS
# ==============================================

@router.get("/alerts")
async def get_alerts(
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=200)
):
    """Get system alerts"""
    db = get_db()
    
    query = {}
    if unread_only:
        query["is_read"] = False
    
    alerts = await db.admin_alerts.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    
    return {"success": True, "total": len(alerts), "alerts": alerts}

@router.post("/alerts/generate")
async def generate_alerts():
    """Generate alerts based on system state"""
    db = get_db()
    alerts = []
    
    # Check for low stock products
    low_stock = await db.products.count_documents({"stock": {"$lt": 5}})
    if low_stock > 0:
        alert = {
            "type": AlertType.STOCK.value,
            "severity": AlertSeverity.MEDIUM.value,
            "title": f"{low_stock} produits en stock faible",
            "message": "Certains produits nécessitent un réapprovisionnement",
            "is_read": False,
            "created_at": datetime.now(timezone.utc)
        }
        await db.admin_alerts.insert_one(alert)
        del alert["_id"]
        alerts.append(alert)
    
    # Check pending orders
    pending = await db.orders.count_documents({"status": "pending"})
    if pending > 10:
        alert = {
            "type": AlertType.ORDER.value,
            "severity": AlertSeverity.HIGH.value,
            "title": f"{pending} commandes en attente",
            "message": "Les commandes s'accumulent",
            "is_read": False,
            "created_at": datetime.now(timezone.utc)
        }
        await db.admin_alerts.insert_one(alert)
        del alert["_id"]
        alerts.append(alert)
    
    return {"success": True, "generated": len(alerts), "alerts": alerts}

@router.put("/alerts/{alert_id}/read")
async def mark_alert_read(alert_id: str):
    """Mark alert as read"""
    db = get_db()
    result = await db.admin_alerts.update_one(
        {"id": alert_id},
        {"$set": {"is_read": True, "read_at": datetime.now(timezone.utc)}}
    )
    
    return {"success": result.modified_count > 0, "message": "Alert marked as read" if result.modified_count > 0 else "Alert not found"}

@router.put("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """Mark alert as resolved"""
    db = get_db()
    result = await db.admin_alerts.update_one(
        {"id": alert_id},
        {"$set": {"resolved": True, "resolved_at": datetime.now(timezone.utc)}}
    )
    
    return {"success": result.modified_count > 0, "message": "Alert resolved" if result.modified_count > 0 else "Alert not found"}

# ==============================================
# AUDIT LOGS
# ==============================================

@router.get("/audit-logs")
async def get_audit_logs(
    admin_id: Optional[str] = None,
    resource_type: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500)
):
    """Get admin audit logs"""
    db = get_db()
    
    query = {}
    if admin_id:
        query["admin_id"] = admin_id
    if resource_type:
        query["resource_type"] = resource_type
    
    logs = await db.audit_logs.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    
    return {"success": True, "total": len(logs), "logs": logs}

# ==============================================
# HEALTH CHECK
# ==============================================

@router.get("/health")
async def system_health():
    """Get system health status"""
    db = get_db()
    
    # Get maintenance status
    maintenance = await db.maintenance_mode.find_one({}, {"_id": 0})
    is_maintenance = maintenance.get("enabled", False) if maintenance else False
    
    # Get alert counts
    unread_alerts = await db.admin_alerts.count_documents({"is_read": False})
    
    # Determine health status
    status = "healthy"
    issues = []
    
    if is_maintenance:
        status = "maintenance"
        issues.append("Site en maintenance")
    
    if unread_alerts > 10:
        status = "warning"
        issues.append(f"{unread_alerts} alertes non lues")
    
    return {
        "success": True,
        "status": status,
        "issues": issues,
        "stats": {
            "active_sessions": 0,
            "pending_orders": 0,
            "unread_alerts": unread_alerts
        },
        "maintenance": is_maintenance
    }

# ==============================================
# BRAND IDENTITY (ex admin_advanced_engine)
# ==============================================

@router.get("/brand")
async def get_brand():
    """Get brand identity settings"""
    db = get_db()
    brand = await db.brand_identity.find_one({}, {"_id": 0})
    return {"success": True, "brand": brand or BrandIdentity().dict()}

@router.post("/brand")
async def update_brand(brand: BrandIdentity):
    """Update brand identity"""
    db = get_db()
    brand_dict = brand.dict()
    brand_dict["updated_at"] = datetime.now(timezone.utc)
    
    await db.brand_identity.update_one(
        {},
        {"$set": brand_dict},
        upsert=True
    )
    return {"success": True, "brand": brand_dict}

# ==============================================
# FEATURE CONTROLS (ex admin_advanced_engine)
# ==============================================

@router.get("/features")
async def list_features():
    """List all feature controls"""
    db = get_db()
    features = await db.feature_controls.find({}, {"_id": 0}).to_list(length=100)
    return {"success": True, "features": features}

@router.post("/features")
async def update_feature(feature: FeatureControl):
    """Update or create feature control"""
    db = get_db()
    feature_dict = feature.dict()
    feature_dict["updated_at"] = datetime.now(timezone.utc)
    
    await db.feature_controls.update_one(
        {"feature_id": feature.feature_id},
        {"$set": feature_dict},
        upsert=True
    )
    return {"success": True, "feature": feature_dict}

@router.get("/features/{feature_id}")
async def get_feature(feature_id: str):
    """Get specific feature control"""
    db = get_db()
    feature = await db.feature_controls.find_one({"feature_id": feature_id}, {"_id": 0})
    return {
        "success": True,
        "feature": feature,
        "enabled": feature.get("enabled", True) if feature else True
    }

# ==============================================
# SITE ACCESS CONTROL (ex admin_advanced_engine)
# ==============================================

@router.get("/site-access")
async def get_access():
    """Get site access settings"""
    db = get_db()
    access = await db.site_access.find_one({}, {"_id": 0})
    return {"success": True, "access": access or SiteAccess().dict()}

@router.post("/site-access")
async def set_access(access: SiteAccess):
    """Update site access settings"""
    db = get_db()
    access_dict = access.dict()
    access_dict["updated_at"] = datetime.now(timezone.utc)
    
    await db.site_access.update_one(
        {},
        {"$set": access_dict},
        upsert=True
    )
    return {"success": True, "access": access_dict}
