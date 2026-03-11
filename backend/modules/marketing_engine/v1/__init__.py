"""
Marketing Engine V1 - Module Init
==================================
Architecture LEGO V5 - Module isolé.
"""
from .router import router as marketing_router
from .service import MarketingEngineService

__all__ = ['marketing_router', 'MarketingEngineService']
