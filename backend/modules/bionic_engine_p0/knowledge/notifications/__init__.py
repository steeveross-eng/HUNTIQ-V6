"""
BIONIC V5 — NOTIFICATIONS MODULE (PHASE F)
==========================================
VAPID Natif — 100% Autonome

Module de notifications push temps réel.

COMPOSANTS:
- NotificationRegistry: Registre centralisé (Knowledge Layer)
- WebPushService: Service d'envoi push (passif)
- Règles de déclenchement: Centralisées, versionnées, traçables

VERSION: 7.2.0
Conformité: G-SEC | G-QA | G-DOC | BIONIC V5 MASTER
"""

from .notification_registry import (
    # Enums
    AlertType,
    AlertPriority,
    SubscriptionStatus,
    # Models
    VAPIDKeys,
    PushSubscription,
    NotificationPayload,
    AlertTriggerRule,
    # Registry
    NotificationRegistry,
    get_notification_registry
)

from .webpush_service import (
    WebPushService,
    get_webpush_service
)

__all__ = [
    # Enums
    'AlertType',
    'AlertPriority',
    'SubscriptionStatus',
    # Models
    'VAPIDKeys',
    'PushSubscription',
    'NotificationPayload',
    'AlertTriggerRule',
    # Registry
    'NotificationRegistry',
    'get_notification_registry',
    # Service
    'WebPushService',
    'get_webpush_service'
]
