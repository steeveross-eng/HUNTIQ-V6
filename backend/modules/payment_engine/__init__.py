"""
Payment Engine - V5-ULTIME Monétisation
=======================================

Intégration Stripe pour paiements et abonnements.

Version: 1.0.0
API Prefix: /api/v1/payments
"""

from .router import router

__all__ = ["router"]
