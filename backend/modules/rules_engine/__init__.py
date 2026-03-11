"""
Rules Engine - V5-ULTIME Plan Maître
====================================

Moteur de règles de chasse intelligentes.
Centralise toutes les règles métier du Plan Maître.

Version: 1.0.0
API Prefix: /api/v1/rules
"""

from .router import router

__all__ = ["router"]
