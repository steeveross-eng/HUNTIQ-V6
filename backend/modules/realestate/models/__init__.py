"""
BIONIC™ Real Estate Module - Init
==================================
Phase 11-15: Module Immobilier
"""

from .property_models import (
    PropertySource,
    PropertyType,
    PropertyStatus,
    GeoCoordinates,
    PropertyBase,
    PropertyCreate,
    PropertyInDB,
    PropertyResponse,
    PropertyListResponse,
    PropertyScoreBreakdown,
    OpportunityLevel,
    PropertyOpportunity,
    OpportunityListResponse,
    B2BHotspotRequest,
    B2BScoreRequest,
    B2BPropertyRequest,
    B2BHeatmapRequest
)

__all__ = [
    "PropertySource",
    "PropertyType", 
    "PropertyStatus",
    "GeoCoordinates",
    "PropertyBase",
    "PropertyCreate",
    "PropertyInDB",
    "PropertyResponse",
    "PropertyListResponse",
    "PropertyScoreBreakdown",
    "OpportunityLevel",
    "PropertyOpportunity",
    "OpportunityListResponse",
    "B2BHotspotRequest",
    "B2BScoreRequest",
    "B2BPropertyRequest",
    "B2BHeatmapRequest"
]
