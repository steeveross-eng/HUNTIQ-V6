"""
BIONIC HUNT/Chasse V3 - Routes Package
API routes for BIONIC features
"""

from .bathymetry import router as bathymetry_router
from .advanced_zones import router as advanced_zones_router

__all__ = ['bathymetry_router', 'advanced_zones_router']
