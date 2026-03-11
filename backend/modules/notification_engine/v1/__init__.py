"""Notification Engine Module v1

Multi-channel notification system.

Version: 1.0.0
"""

from .router import router
from .service import NotificationService
from .models import (
    Notification, NotificationTemplate, NotificationPreferences,
    NotificationType, NotificationChannel, NotificationPriority
)

__all__ = [
    "router",
    "NotificationService",
    "Notification",
    "NotificationTemplate",
    "NotificationPreferences",
    "NotificationType",
    "NotificationChannel",
    "NotificationPriority"
]
