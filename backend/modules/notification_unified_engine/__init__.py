"""
Notification Unified Engine - V5-ULTIME-FUSION
==============================================

Module unifié fusionnant:
- notification_engine (V4): Multi-channel notifications, preferences, templates
- communication_engine (BASE): Simple notifications, email templates

Version: 1.0.0
API Prefix: /api/v1/notifications
"""

from .router import router

__all__ = ["router"]
