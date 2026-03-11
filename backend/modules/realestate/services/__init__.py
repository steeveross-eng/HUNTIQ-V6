"""
BIONIC™ Real Estate Module - Services Init
============================================
Phase 11-15: Module Immobilier
"""

from .scoring_service import RealEstateScoringService
from .opportunity_service import OpportunityEngineService

__all__ = [
    'RealEstateScoringService',
    'OpportunityEngineService'
]
