"""Legal Time Engine v1
Provides sunrise/sunset calculations and legal hunting windows.

Version: 1.0.0
"""
from .router import router
from .service import LegalTimeService

__all__ = ["router", "LegalTimeService"]
