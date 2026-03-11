"""
BIONIC V5 — NOTIFICATIONS ROUTER (PHASE F — NOTIFICATIONS PUSH)
================================================================
VAPID Natif — 100% Autonome

Endpoints REST pour les notifications push.

ENDPOINTS:
- GET  /api/v1/bionic/notifications/vapid-key       - Clé publique VAPID
- POST /api/v1/bionic/notifications/subscribe       - S'abonner aux notifications
- POST /api/v1/bionic/notifications/unsubscribe     - Se désabonner
- POST /api/v1/bionic/notifications/update-location - Mettre à jour la position
- GET  /api/v1/bionic/notifications/rules           - Lister les règles
- POST /api/v1/bionic/notifications/send            - Envoyer une notification
- POST /api/v1/bionic/notifications/send-zone       - Envoyer à une zone
- GET  /api/v1/bionic/notifications/health          - Health check

VERSION: 7.2.0
Conformité: G-SEC | G-QA | G-DOC | BIONIC V5 MASTER
"""

import logging
from typing import Optional, List
from pydantic import BaseModel, Field

from fastapi import APIRouter, HTTPException, status, Query

from modules.bionic_engine_p0.knowledge.notifications import (
    get_notification_registry,
    get_webpush_service
)

logger = logging.getLogger(__name__)

# =============================================================================
# ROUTER
# =============================================================================

router = APIRouter(tags=["BIONIC Notifications Push"])


# =============================================================================
# SCHEMAS
# =============================================================================

class SubscribeRequest(BaseModel):
    """Requête d'abonnement push."""
    
    endpoint: str = Field(..., description="URL endpoint du push service")
    p256dh: str = Field(..., description="Clé publique du client (Base64)")
    auth: str = Field(..., description="Secret d'authentification (Base64)")
    user_agent: str = Field("", description="User agent du navigateur")
    device_type: str = Field("web", description="Type d'appareil (web, mobile, desktop)")
    lat: Optional[float] = Field(None, description="Latitude pour géofencing")
    lng: Optional[float] = Field(None, description="Longitude pour géofencing")
    geofence_radius_km: float = Field(5.0, ge=0.5, le=50, description="Rayon de géofencing (km)")
    alert_types: Optional[List[str]] = Field(None, description="Types d'alertes souhaitées")
    min_priority: str = Field("medium", description="Priorité minimum des alertes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "endpoint": "https://fcm.googleapis.com/fcm/send/...",
                "p256dh": "BNcRd...",
                "auth": "tBHI...",
                "user_agent": "Mozilla/5.0...",
                "device_type": "web",
                "lat": 46.8139,
                "lng": -71.2080,
                "geofence_radius_km": 5.0,
                "alert_types": ["danger", "human_pressure"],
                "min_priority": "medium"
            }
        }


class UnsubscribeRequest(BaseModel):
    """Requête de désabonnement."""
    
    subscription_id: str = Field(..., description="ID de l'abonnement")


class UpdateLocationRequest(BaseModel):
    """Requête de mise à jour de position."""
    
    subscription_id: str = Field(..., description="ID de l'abonnement")
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lng: float = Field(..., ge=-180, le=180, description="Longitude")


class SendNotificationRequest(BaseModel):
    """Requête d'envoi de notification."""
    
    alert_type: str = Field(..., description="Type d'alerte (danger, human_pressure, corridor_risk, safety_update)")
    priority: str = Field("medium", description="Priorité (critical, high, medium, low)")
    title: str = Field(..., description="Titre de la notification")
    body: str = Field(..., description="Corps de la notification")
    zone_id: Optional[str] = Field(None, description="ID de la zone Safety Engine")
    lat: Optional[float] = Field(None, description="Latitude")
    lng: Optional[float] = Field(None, description="Longitude")
    radius_m: Optional[float] = Field(None, description="Rayon en mètres")
    url: str = Field("/", description="URL à ouvrir")
    
    class Config:
        json_schema_extra = {
            "example": {
                "alert_type": "danger",
                "priority": "high",
                "title": "⚠️ Zone de danger",
                "body": "Une zone de danger a été signalée à proximité.",
                "lat": 46.8139,
                "lng": -71.2080,
                "radius_m": 500,
                "url": "/map"
            }
        }


class SendZoneNotificationRequest(BaseModel):
    """Requête d'envoi à une zone (géofencing)."""
    
    alert_type: str = Field(..., description="Type d'alerte")
    priority: str = Field("medium", description="Priorité")
    title: str = Field(..., description="Titre")
    body: str = Field(..., description="Corps")
    lat: float = Field(..., ge=-90, le=90, description="Latitude du centre")
    lng: float = Field(..., ge=-180, le=180, description="Longitude du centre")
    radius_km: float = Field(5.0, ge=0.5, le=50, description="Rayon de diffusion (km)")


# =============================================================================
# ENDPOINTS - CONFIGURATION
# =============================================================================

@router.get(
    "/notifications/vapid-key",
    response_model=dict,
    summary="Obtenir la clé publique VAPID",
    description="""
    VAPID Natif — 100% Autonome
    
    Retourne la clé publique VAPID nécessaire pour s'abonner aux notifications push.
    Cette clé doit être utilisée par le frontend lors de l'appel à PushManager.subscribe().
    """
)
async def get_vapid_key():
    """Retourne la clé publique VAPID."""
    
    try:
        registry = get_notification_registry()
        public_key = registry.get_vapid_public_key()
        
        if not public_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"error": True, "message": "VAPID keys not configured"}
            )
        
        return {
            "status": "success",
            "vapid_public_key": public_key,
            "usage": "Use this key with PushManager.subscribe({ applicationServerKey: vapid_public_key })"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get VAPID key: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": True, "message": str(e)}
        )


# =============================================================================
# ENDPOINTS - ABONNEMENTS
# =============================================================================

@router.post(
    "/notifications/subscribe",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="S'abonner aux notifications push",
    description="""
    VAPID Natif — Géofencing Dynamique
    
    Enregistre un nouvel abonnement push.
    
    L'abonné recevra les notifications :
    - Selon ses préférences de types d'alertes
    - Selon sa position et le rayon de géofencing
    - Selon sa priorité minimum configurée
    """
)
async def subscribe(request: SubscribeRequest):
    """Crée un abonnement push."""
    
    try:
        registry = get_notification_registry()
        
        subscription = registry.create_subscription(
            endpoint=request.endpoint,
            p256dh=request.p256dh,
            auth=request.auth,
            user_agent=request.user_agent,
            device_type=request.device_type,
            lat=request.lat,
            lng=request.lng,
            geofence_radius_km=request.geofence_radius_km,
            alert_types=request.alert_types,
            min_priority=request.min_priority
        )
        
        return {
            "status": "success",
            "message": "Abonnement créé avec succès",
            "subscription": subscription.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Failed to subscribe: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": True, "message": str(e)}
        )


@router.post(
    "/notifications/unsubscribe",
    response_model=dict,
    summary="Se désabonner des notifications",
    description="Désactive un abonnement push existant."
)
async def unsubscribe(request: UnsubscribeRequest):
    """Désactive un abonnement."""
    
    try:
        registry = get_notification_registry()
        success = registry.unsubscribe(request.subscription_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": True,
                    "error_code": "SUBSCRIPTION_NOT_FOUND",
                    "message": f"Abonnement {request.subscription_id} non trouvé"
                }
            )
        
        return {
            "status": "success",
            "message": "Désabonnement effectué",
            "subscription_id": request.subscription_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to unsubscribe: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": True, "message": str(e)}
        )


@router.post(
    "/notifications/update-location",
    response_model=dict,
    summary="Mettre à jour la position pour géofencing",
    description="Met à jour la position d'un abonné pour le géofencing dynamique."
)
async def update_location(request: UpdateLocationRequest):
    """Met à jour la position d'un abonnement."""
    
    try:
        registry = get_notification_registry()
        subscription = registry.update_subscription_location(
            subscription_id=request.subscription_id,
            lat=request.lat,
            lng=request.lng
        )
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": True,
                    "error_code": "SUBSCRIPTION_NOT_FOUND",
                    "message": f"Abonnement {request.subscription_id} non trouvé"
                }
            )
        
        return {
            "status": "success",
            "message": "Position mise à jour",
            "subscription": subscription.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update location: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": True, "message": str(e)}
        )


# =============================================================================
# ENDPOINTS - RÈGLES
# =============================================================================

@router.get(
    "/notifications/rules",
    response_model=dict,
    summary="Lister les règles de déclenchement",
    description="""
    Retourne les règles de déclenchement centralisées.
    
    Conformité BIONIC V5:
    - Règles versionnées
    - Documentées
    - Traçables (source_ids)
    """
)
async def list_rules(
    active_only: bool = Query(True, description="Uniquement les règles actives")
):
    """Liste les règles de déclenchement."""
    
    try:
        registry = get_notification_registry()
        
        if active_only:
            rules = registry.get_active_rules()
        else:
            rules = registry.get_trigger_rules()
        
        return {
            "status": "success",
            "total": len(rules),
            "rules": [r.to_dict() for r in rules],
            "filter": {"active_only": active_only}
        }
        
    except Exception as e:
        logger.error(f"Failed to list rules: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": True, "message": str(e)}
        )


# =============================================================================
# ENDPOINTS - ENVOI
# =============================================================================

@router.post(
    "/notifications/send",
    response_model=dict,
    summary="Envoyer une notification à tous",
    description="""
    SAFETY ENGINE INTEGRATION
    
    Envoie une notification push à tous les abonnés actifs
    qui correspondent aux critères (type d'alerte, priorité).
    """
)
async def send_notification(request: SendNotificationRequest):
    """Envoie une notification à tous les abonnés éligibles."""
    
    try:
        registry = get_notification_registry()
        push_service = get_webpush_service()
        
        # Créer la notification
        notification = registry.create_custom_notification(
            alert_type=request.alert_type,
            priority=request.priority,
            title=request.title,
            body=request.body,
            zone_id=request.zone_id,
            lat=request.lat,
            lng=request.lng,
            radius_m=request.radius_m,
            url=request.url
        )
        
        # Envoyer
        result = push_service.send_to_all(notification)
        
        return {
            "status": "success",
            "message": f"Notification envoyée à {result['statistics']['sent']} abonné(s)",
            "notification": notification.to_dict(),
            "delivery": result["statistics"]
        }
        
    except Exception as e:
        logger.error(f"Failed to send notification: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": True, "message": str(e)}
        )


@router.post(
    "/notifications/send-zone",
    response_model=dict,
    summary="Envoyer une notification à une zone (géofencing)",
    description="""
    GÉOFENCING DYNAMIQUE
    
    Envoie une notification push uniquement aux abonnés
    situés dans le rayon spécifié autour du point central.
    
    Idéal pour les alertes Safety Engine localisées.
    """
)
async def send_zone_notification(request: SendZoneNotificationRequest):
    """Envoie une notification à une zone géographique."""
    
    try:
        registry = get_notification_registry()
        push_service = get_webpush_service()
        
        # Créer la notification
        notification = registry.create_custom_notification(
            alert_type=request.alert_type,
            priority=request.priority,
            title=request.title,
            body=request.body,
            lat=request.lat,
            lng=request.lng,
            radius_m=request.radius_km * 1000,
            url="/map"
        )
        
        # Envoyer à la zone
        result = push_service.send_to_zone(
            notification=notification,
            lat=request.lat,
            lng=request.lng,
            radius_km=request.radius_km
        )
        
        return {
            "status": "success",
            "message": f"Notification envoyée à {result['statistics']['sent']}/{result['statistics']['eligible']} abonné(s) dans la zone",
            "notification": notification.to_dict(),
            "zone": result["zone"],
            "delivery": result["statistics"]
        }
        
    except Exception as e:
        logger.error(f"Failed to send zone notification: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": True, "message": str(e)}
        )


# =============================================================================
# ENDPOINTS - HISTORIQUE
# =============================================================================

@router.get(
    "/notifications/history",
    response_model=dict,
    summary="Historique des notifications",
    description="Récupère l'historique des notifications envoyées."
)
async def get_notification_history(
    limit: int = Query(50, ge=1, le=200, description="Nombre maximum")
):
    """Récupère l'historique des notifications."""
    
    try:
        registry = get_notification_registry()
        notifications = registry.list_notifications(limit=limit)
        
        return {
            "status": "success",
            "total": len(notifications),
            "notifications": [n.to_dict() for n in notifications]
        }
        
    except Exception as e:
        logger.error(f"Failed to get history: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": True, "message": str(e)}
        )


# =============================================================================
# HEALTH CHECK
# =============================================================================

@router.get("/notifications/health")
async def notifications_health():
    """Vérification santé du service de notifications."""
    
    try:
        registry = get_notification_registry()
        push_service = get_webpush_service()
        
        registry_stats = registry.get_stats()
        
        return {
            "status": "healthy",
            "endpoint": "/api/v1/bionic/notifications",
            "version": "7.2.0",
            "phase": "PHASE F — NOTIFICATIONS PUSH",
            "vapid": {
                "configured": registry_stats["vapid_configured"],
                "type": "native"
            },
            "statistics": registry_stats,
            "features": [
                "vapid_native",
                "web_push",
                "geofencing",
                "trigger_rules",
                "safety_engine_integration"
            ]
        }
        
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e)
        }
