"""Admin Engine Router - MÉTIER

FastAPI router for administration endpoints.
Protected by role-based authentication.

Version: 1.1.0
API Prefix: /api/v1/admin
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from datetime import datetime
from .service import AdminService
from .models import (
    AdminLogin, AlertType, AlertSeverity
)

# Import role-based authentication
from modules.roles_engine.v1.dependencies import (
    require_admin
)
from modules.roles_engine.v1.models import UserWithRole

router = APIRouter(prefix="/api/v1/admin", tags=["Admin Engine"])

# Initialize service
_service = AdminService()


@router.get("/")
async def admin_engine_info():
    """Get admin engine information (public)"""
    return {
        "module": "admin_engine",
        "version": "1.1.0",
        "description": "Administration and site management",
        "features": [
            "Dashboard statistics",
            "Site settings",
            "Maintenance mode",
            "Alert management",
            "Audit logging"
        ],
        "alert_types": [t.value for t in AlertType],
        "alert_severities": [s.value for s in AlertSeverity],
        "note": "🔒 Endpoints protégés par authentification admin"
    }


@router.post("/login")
async def admin_login(credentials: AdminLogin):
    """
    Admin login endpoint (deprecated - use /api/auth/login).
    Maintained for backward compatibility.
    """
    valid = await _service.verify_admin_credentials(
        credentials.email, 
        credentials.password
    )
    
    if not valid:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # In production, generate proper JWT token
    import secrets
    token = secrets.token_urlsafe(32)
    
    return {
        "success": True,
        "message": "Login successful",
        "email": credentials.email,
        "token": token,
        "is_admin": True
    }


@router.get("/dashboard")
async def get_dashboard(
    admin: UserWithRole = Depends(require_admin)
):
    """Get dashboard statistics (admin only)"""
    stats = await _service.get_dashboard_stats()
    
    return {
        "success": True,
        "stats": stats.model_dump(),
        "admin": admin.email
    }


@router.get("/settings")
async def get_site_settings(
    admin: UserWithRole = Depends(require_admin)
):
    """Get site settings (admin only)"""
    settings = await _service.get_site_settings()
    
    return {
        "success": True,
        "settings": settings.model_dump()
    }


@router.put("/settings")
async def update_site_settings(
    settings: dict,
    admin: UserWithRole = Depends(require_admin)
):
    """Update site settings (admin only)"""
    updated = await _service.update_site_settings(settings, admin.user_id)
    
    return {
        "success": True,
        "message": "Settings updated",
        "settings": updated.model_dump(),
        "updated_by": admin.email
    }


@router.get("/maintenance")
async def get_maintenance_status(
    admin: UserWithRole = Depends(require_admin)
):
    """Get maintenance mode status (admin only)"""
    mode = await _service.get_maintenance_mode()
    
    return {
        "success": True,
        "maintenance": mode.model_dump()
    }


@router.put("/maintenance")
async def set_maintenance_mode(
    enabled: bool,
    admin: UserWithRole = Depends(require_admin),
    title: Optional[str] = None,
    message: Optional[str] = None,
    estimated_end: Optional[str] = None
):
    """Enable or disable maintenance mode (admin only)"""
    end_date = None
    if estimated_end:
        try:
            end_date = datetime.fromisoformat(estimated_end.replace('Z', '+00:00'))
        except ValueError:
            pass
    
    mode = await _service.set_maintenance_mode(
        enabled=enabled,
        admin_id=admin.user_id,
        title=title,
        message=message,
        estimated_end=end_date
    )
    
    return {
        "success": True,
        "message": "Maintenance mode " + ("enabled" if enabled else "disabled"),
        "maintenance": mode.model_dump(),
        "changed_by": admin.email
    }


@router.get("/alerts")
async def get_alerts(
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=200),
    admin: UserWithRole = Depends(require_admin)
):
    """Get system alerts (admin only)"""
    alerts = await _service.get_alerts(unread_only, limit)
    
    return {
        "success": True,
        "total": len(alerts),
        "alerts": [a.model_dump() for a in alerts]
    }


@router.post("/alerts/generate")
async def generate_alerts(
    admin: UserWithRole = Depends(require_admin)
):
    """Generate alerts based on system state (admin only)"""
    alerts = await _service.generate_alerts()
    
    return {
        "success": True,
        "generated": len(alerts),
        "alerts": [a.model_dump() for a in alerts]
    }


@router.put("/alerts/{alert_id}/read")
async def mark_alert_read(
    alert_id: str,
    admin: UserWithRole = Depends(require_admin)
):
    """Mark alert as read (admin only)"""
    success = await _service.mark_alert_read(alert_id)
    
    return {
        "success": success,
        "message": "Alert marked as read" if success else "Alert not found"
    }


@router.put("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """Mark alert as resolved"""
    success = await _service.resolve_alert(alert_id)
    
    return {
        "success": success,
        "message": "Alert resolved" if success else "Alert not found"
    }


@router.get("/audit-logs")
async def get_audit_logs(
    admin_id: Optional[str] = None,
    resource_type: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500)
):
    """Get admin audit logs"""
    logs = await _service.get_audit_logs(admin_id, resource_type, limit)
    
    return {
        "success": True,
        "total": len(logs),
        "logs": logs
    }


@router.get("/health")
async def system_health():
    """Get system health status"""
    stats = await _service.get_dashboard_stats()
    maintenance = await _service.get_maintenance_mode()
    
    # Determine health status
    status = "healthy"
    issues = []
    
    if maintenance.enabled:
        status = "maintenance"
        issues.append("Site en maintenance")
    
    if stats.unread_alerts > 10:
        status = "warning"
        issues.append(f"{stats.unread_alerts} alertes non lues")
    
    if stats.out_of_stock_products > 0:
        issues.append(f"{stats.out_of_stock_products} produits en rupture")
    
    return {
        "success": True,
        "status": status,
        "issues": issues,
        "stats": {
            "active_sessions": stats.active_sessions,
            "pending_orders": stats.pending_orders,
            "unread_alerts": stats.unread_alerts
        },
        "maintenance": maintenance.enabled
    }
