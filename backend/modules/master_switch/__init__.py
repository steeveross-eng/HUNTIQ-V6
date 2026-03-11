"""
Master Switch X300% - Module Export
Inclut aussi le Global Master Switch (Phase 1.6-B)
"""
from .router import router, global_switch_router

__all__ = ["router", "global_switch_router"]
__version__ = "1.1.0"
__module__ = "master_switch"
