"""
BIONIC V5 — WEB PUSH SERVICE (PHASE F — NOTIFICATIONS PUSH)
============================================================
VAPID Natif — 100% Autonome

Service d'envoi de notifications push via Web Push API.

VERSION: 7.2.0
Conformité: G-SEC | G-QA | G-DOC | BIONIC V5 MASTER
"""

from typing import Dict, Optional, Any, Tuple
from datetime import datetime, timezone
import logging

from pywebpush import webpush, WebPushException

from .notification_registry import (
    get_notification_registry,
    NotificationPayload,
    PushSubscription,
    AlertPriority
)

logger = logging.getLogger(__name__)


class WebPushService:
    """
    Service d'envoi de notifications Web Push.
    
    CONFORMITÉ BIONIC V5:
    - Service 100% passif (aucune logique locale)
    - Utilise exclusivement NotificationRegistry (Knowledge Layer)
    - Traçabilité complète des envois
    """
    
    def __init__(self):
        self._version = "7.2.0"
        self._registry = get_notification_registry()
        
        logger.info(f"WebPushService initialized: v{self._version}")
    
    def send_notification(
        self,
        subscription: PushSubscription,
        notification: NotificationPayload
    ) -> Tuple[bool, Optional[str]]:
        """
        Envoie une notification push à un abonné.
        
        Returns:
            (success, error_message)
        """
        vapid_keys = self._registry.get_vapid_keys()
        if not vapid_keys:
            return False, "VAPID keys not configured"
        
        # Préparer les données d'abonnement
        subscription_info = {
            "endpoint": subscription.endpoint,
            "keys": {
                "p256dh": subscription.p256dh,
                "auth": subscription.auth
            }
        }
        
        # Préparer les claims VAPID
        vapid_claims = {
            "sub": "mailto:alerts@bionic-v5.com"
        }
        
        try:
            webpush(
                subscription_info=subscription_info,
                data=notification.to_push_payload(),
                vapid_private_key=vapid_keys.private_key,
                vapid_claims=vapid_claims
            )
            
            # Mettre à jour les stats de l'abonnement
            subscription.last_push_at = datetime.now(timezone.utc)
            subscription.push_count += 1
            
            logger.info(f"Push sent: {notification.notification_id} -> {subscription.subscription_id}")
            
            return True, None
            
        except WebPushException as e:
            error_msg = str(e)
            
            # Si l'abonnement est expiré, le marquer
            if e.response and e.response.status_code in [404, 410]:
                from .notification_registry import SubscriptionStatus
                subscription.status = SubscriptionStatus.EXPIRED
                logger.warning(f"Subscription expired: {subscription.subscription_id}")
            
            logger.error(f"Push failed: {notification.notification_id} -> {error_msg}")
            
            return False, error_msg
        
        except Exception as e:
            logger.error(f"Push error: {str(e)}")
            return False, str(e)
    
    def send_to_zone(
        self,
        notification: NotificationPayload,
        lat: float,
        lng: float,
        radius_km: float
    ) -> Dict[str, Any]:
        """
        Envoie une notification à tous les abonnés dans une zone (géofencing).
        
        Returns:
            Statistiques d'envoi
        """
        # Trouver les abonnés dans la zone
        subscriptions = self._registry.get_subscriptions_in_radius(lat, lng, radius_km)
        
        # Filtrer par type d'alerte et priorité
        eligible = []
        for sub in subscriptions:
            if notification.alert_type in sub.alert_types:
                # Comparer les priorités
                priority_order = {
                    AlertPriority.LOW: 0,
                    AlertPriority.MEDIUM: 1,
                    AlertPriority.HIGH: 2,
                    AlertPriority.CRITICAL: 3
                }
                if priority_order.get(notification.priority, 0) >= priority_order.get(sub.min_priority, 0):
                    eligible.append(sub)
        
        # Envoyer
        sent = 0
        failed = 0
        errors = []
        
        for sub in eligible:
            success, error = self.send_notification(sub, notification)
            if success:
                sent += 1
            else:
                failed += 1
                if error:
                    errors.append(error)
        
        result = {
            "notification_id": notification.notification_id,
            "zone": {
                "lat": lat,
                "lng": lng,
                "radius_km": radius_km
            },
            "statistics": {
                "subscriptions_in_zone": len(subscriptions),
                "eligible": len(eligible),
                "sent": sent,
                "failed": failed
            },
            "errors": errors[:5] if errors else []  # Max 5 erreurs
        }
        
        logger.info(f"Zone push complete: {sent}/{len(eligible)} sent")
        
        return result
    
    def send_to_all(self, notification: NotificationPayload) -> Dict[str, Any]:
        """
        Envoie une notification à tous les abonnés actifs.
        
        Returns:
            Statistiques d'envoi
        """
        subscriptions = self._registry.get_all_active_subscriptions()
        
        # Filtrer par préférences
        eligible = []
        for sub in subscriptions:
            if notification.alert_type in sub.alert_types:
                priority_order = {
                    AlertPriority.LOW: 0,
                    AlertPriority.MEDIUM: 1,
                    AlertPriority.HIGH: 2,
                    AlertPriority.CRITICAL: 3
                }
                if priority_order.get(notification.priority, 0) >= priority_order.get(sub.min_priority, 0):
                    eligible.append(sub)
        
        sent = 0
        failed = 0
        
        for sub in eligible:
            success, _ = self.send_notification(sub, notification)
            if success:
                sent += 1
            else:
                failed += 1
        
        return {
            "notification_id": notification.notification_id,
            "statistics": {
                "total_active": len(subscriptions),
                "eligible": len(eligible),
                "sent": sent,
                "failed": failed
            }
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Statistiques du service."""
        return {
            "version": self._version,
            "registry_stats": self._registry.get_stats()
        }


# =============================================================================
# SINGLETON
# =============================================================================

_service_instance: Optional[WebPushService] = None


def get_webpush_service() -> WebPushService:
    """Obtenir l'instance singleton du service."""
    global _service_instance
    if _service_instance is None:
        _service_instance = WebPushService()
    return _service_instance


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'WebPushService',
    'get_webpush_service'
]
