"""
Admin Unified Engine - V5-ULTIME-FUSION
========================================

Module unifié fusionnant:
- admin_engine (V4): Dashboard, settings, maintenance, alerts, audit
- admin_advanced_engine (BASE): Brand identity, feature controls, site access

Version: 1.0.0
API Prefix: /api/v1/admin
"""

from .router import router

__all__ = ["router"]
