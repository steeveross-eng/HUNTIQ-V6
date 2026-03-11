"""Products Engine v1 Module - PHASE 7 EXTRACTION
Extracted from server.py monolith.

Handles product CRUD, filtering, and search operations.

Version: 1.0.0
"""

from .router import router
from .models import Product, ProductCreate, ProductUpdate
from .service import ProductsService, get_products_service

__all__ = [
    "router",
    "Product",
    "ProductCreate", 
    "ProductUpdate",
    "ProductsService",
    "get_products_service"
]
