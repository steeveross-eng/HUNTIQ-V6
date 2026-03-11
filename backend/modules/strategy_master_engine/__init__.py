"""
Strategy Master Engine - V5-ULTIME Plan Maître
==============================================

Orchestrateur de stratégies de chasse.
Intègre: rules, scoring, weather, territory, progression.

Version: 1.0.0
API Prefix: /api/v1/strategy-master
"""

from .router import router

__all__ = ["router"]
