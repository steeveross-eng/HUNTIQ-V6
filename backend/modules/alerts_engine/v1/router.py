"""Alerts Engine Router"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
from .models import Alert, AlertCreate, SiteSettings, MaintenanceModeUpdate
from .service import get_alerts_service

router = APIRouter(prefix="/api/v1/alerts", tags=["Alerts Engine"])

class HealthResponse(BaseModel):
    status: str
    engine: str
    version: str
    message: str

@router.get("/health", response_model=HealthResponse)
async def health_check():
    service = get_alerts_service()
    stats = await service.get_stats()
    return HealthResponse(
        status="operational", engine="alerts_engine", version="1.0.0",
        message=f"Engine opérationnel - {stats['unread_alerts']} alertes non lues"
    )

@router.get("/stats")
async def get_stats():
    service = get_alerts_service()
    return await service.get_stats()

# ===========================================
# ALERTS ENDPOINTS
# ===========================================

@router.get("/", response_model=List[Alert])
async def get_alerts(is_read: Optional[bool] = None, limit: int = Query(100, le=500)):
    service = get_alerts_service()
    return await service.get_all_alerts(is_read, limit)

@router.post("/", response_model=Alert)
async def create_alert(alert_input: AlertCreate):
    service = get_alerts_service()
    return await service.create_alert(alert_input)

@router.put("/{alert_id}/read")
async def mark_alert_read(alert_id: str):
    service = get_alerts_service()
    success = await service.mark_read(alert_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alerte non trouvée")
    return {"success": True, "message": "Alerte marquée comme lue"}

@router.put("/read-all")
async def mark_all_alerts_read():
    service = get_alerts_service()
    count = await service.mark_all_read()
    return {"success": True, "count": count, "message": f"{count} alertes marquées comme lues"}

@router.delete("/{alert_id}")
async def delete_alert(alert_id: str):
    service = get_alerts_service()
    success = await service.delete_alert(alert_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alerte non trouvée")
    return {"success": True, "message": "Alerte supprimée"}

# ===========================================
# SITE SETTINGS / MAINTENANCE
# ===========================================

@router.get("/site/status")
async def get_site_status():
    """Public endpoint - check site maintenance status"""
    service = get_alerts_service()
    return await service.get_site_status()

@router.get("/site/settings", response_model=SiteSettings)
async def get_site_settings():
    """Admin endpoint - get full site settings"""
    service = get_alerts_service()
    return await service.get_site_settings()

@router.put("/site/maintenance")
async def toggle_maintenance(update: MaintenanceModeUpdate):
    """Toggle maintenance mode"""
    service = get_alerts_service()
    result = await service.toggle_maintenance(update)
    return {
        "success": True,
        "message": f"Mode veille {result['status']}",
        "maintenance_mode": result["maintenance_mode"]
    }
