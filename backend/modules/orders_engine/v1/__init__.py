"""Orders Engine v1 Module - PHASE 7 EXTRACTION
Extracted from server.py monolith.

Handles order management, commissions, and email notifications.

Version: 1.0.0
"""

from .router import router
from .models import Order, OrderCreate, OrderUpdate, OrderCancellation, Commission
from .service import OrdersService, get_orders_service

__all__ = [
    "router",
    "Order",
    "OrderCreate",
    "OrderUpdate",
    "OrderCancellation",
    "Commission",
    "OrdersService",
    "get_orders_service"
]
