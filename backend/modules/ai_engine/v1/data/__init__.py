"""AI Engine Data Layer"""

from .products import (
    BIONIC_PRODUCTS,
    COMPETITOR_PRODUCTS,
    CATEGORY_KEYWORDS,
    get_bionic_product,
    get_competitors,
    detect_category
)
from .references import (
    SCIENTIFIC_REFERENCES,
    get_scientific_references,
    get_references_by_section,
    list_sections
)

__all__ = [
    "BIONIC_PRODUCTS",
    "COMPETITOR_PRODUCTS", 
    "CATEGORY_KEYWORDS",
    "get_bionic_product",
    "get_competitors",
    "detect_category",
    "SCIENTIFIC_REFERENCES",
    "get_scientific_references",
    "get_references_by_section",
    "list_sections"
]
