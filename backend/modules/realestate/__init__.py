"""
BIONIC™ Real Estate Module
===========================
Phase 11-15: Module Immobilier

"La plateforme qui révèle la valeur géospatiale d'un terrain"

Ce module fournit:
- Import et gestion de propriétés immobilières
- Scoring BIONIC géospatial
- Moteur d'opportunités d'investissement
- API B2B pour intégrations tierces
- Marketplace interne
"""

from .models import (
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

from .services import (
    RealEstateScoringService,
    OpportunityEngineService
)

from .controllers import (
    realestate_router,
    b2b_router
)

__version__ = "0.1.0"
__phase__ = "11-15"

__all__ = [
    # Models
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
    "B2BHeatmapRequest",
    
    # Services
    "RealEstateScoringService",
    "OpportunityEngineService",
    
    # Routers
    "realestate_router",
    "b2b_router"
]
