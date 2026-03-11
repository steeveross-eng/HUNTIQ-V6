"""
BIONIC ENGINE - Module Initialization
PHASE G - P0

Exports principaux du moteur BIONIC.
"""

from .core import BionicEngineCore, get_engine, BionicPhase, BionicModuleStatus

__all__ = [
    "BionicEngineCore",
    "get_engine",
    "BionicPhase",
    "BionicModuleStatus"
]

__version__ = "1.0.0-alpha"
__phase__ = "P0"
