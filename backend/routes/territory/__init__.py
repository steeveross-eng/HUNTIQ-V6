"""
Territory Package - Phase 1.8
Assembles all sub-modules and exports routers + public API.
"""

from ._base import (
    territory_router,
    territories_router,
    get_db,
    close_db,
    haversine_distance,
    init_territory_module,
    shutdown_territory_module,
    logger,
)

# Import sub-modules to register their routes on the routers
from . import users_cameras
from . import events_photos
from . import analysis_layers
from . import gps_routes
from . import commerce
from . import quebec_hunting
from . import inventory

# Re-export sync functions used by territories.py shim
from .inventory import (
    sync_territory_to_partnership,
    sync_partnership_to_territory,
    on_territory_created,
    on_territory_updated,
    on_partner_status_changed,
    seed_sample_territories,
    # Re-export constants/helpers that may be imported externally
    serialize_doc,
    generate_internal_id,
    calculate_global_score,
    PROVINCE_NAMES,
    TYPE_LABELS,
    SPECIES_CONFIG,
)

# Re-export product catalogs (used externally)
from .commerce import BIONIC_PRODUCTS, COMPETITOR_PRODUCTS, SPECIES_NUTRITION

# Re-export analysis constants
from .analysis_layers import SPECIES_HABITAT_RULES, WMS_LAYERS, calculate_point_probability

__all__ = [
    # Routers
    "territory_router",
    "territories_router",
    # DB
    "get_db",
    "close_db",
    # Lifecycle
    "init_territory_module",
    "shutdown_territory_module",
    # Sync
    "sync_territory_to_partnership",
    "sync_partnership_to_territory",
    "on_territory_created",
    "on_territory_updated",
    "on_partner_status_changed",
    "seed_sample_territories",
    # Utilities
    "haversine_distance",
    "serialize_doc",
    "generate_internal_id",
    "calculate_global_score",
    # Constants
    "PROVINCE_NAMES",
    "TYPE_LABELS",
    "SPECIES_CONFIG",
    "BIONIC_PRODUCTS",
    "COMPETITOR_PRODUCTS",
    "SPECIES_NUTRITION",
    "SPECIES_HABITAT_RULES",
    "WMS_LAYERS",
    "calculate_point_probability",
]
