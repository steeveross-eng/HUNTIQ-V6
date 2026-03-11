"""BIONIC V3 - Centralized Configuration Settings

This module contains all configuration constants for the modular architecture.
DO NOT modify existing values without validation.
"""

from typing import Dict, List

# =============================================================================
# ARCHITECTURE VERSION
# =============================================================================
ARCHITECTURE_VERSION = "3.0.0"
ARCHITECTURE_CREATED = "2026-02-09"

# =============================================================================
# MODULE REGISTRY
# =============================================================================
CORE_ENGINES = [
    "weather_engine",
    "scoring_engine",
    "strategy_engine",
    "geospatial_engine",
    "wms_engine",
    "ai_engine",
    "nutrition_engine",
]

BUSINESS_ENGINES = [
    "marketplace_engine",
    "user_engine",
    "admin_engine",
    "territory_engine",
    "tracking_engine",
    "notification_engine",
    "networking_engine",
    "referral_engine",
]

ADVANCED_ENGINES = [
    "ecoforestry_engine",
    "advanced_geospatial_engine",
    "engine_3d",
    "wildlife_behavior_engine",
    "weather_fauna_simulation_engine",
    "adaptive_strategy_engine",
    "recommendation_engine",
    "progression_engine",
    "collaborative_engine",
    "plugins_engine",
]

SPECIAL_MODULES = [
    "live_heading_view",
]

DATA_LAYERS = [
    "ecoforestry_layers",
    "advanced_geospatial_layers",
    "layers_3d",
    "behavioral_layers",
    "simulation_layers",
]

ALL_MODULES = CORE_ENGINES + BUSINESS_ENGINES + ADVANCED_ENGINES + SPECIAL_MODULES

# =============================================================================
# MODULE VERSIONS
# =============================================================================
MODULE_VERSIONS: Dict[str, str] = {module: "v1" for module in ALL_MODULES}

# =============================================================================
# API PREFIXES
# =============================================================================
API_PREFIXES: Dict[str, str] = {
    "weather_engine": "/api/v1/weather",
    "scoring_engine": "/api/v1/scoring",
    "strategy_engine": "/api/v1/strategy",
    "geospatial_engine": "/api/v1/geospatial",
    "wms_engine": "/api/v1/wms",
    "ai_engine": "/api/v1/ai",
    "nutrition_engine": "/api/v1/nutrition",
    "marketplace_engine": "/api/v1/marketplace",
    "user_engine": "/api/v1/users",
    "admin_engine": "/api/v1/admin",
    "territory_engine": "/api/v1/territory",
    "tracking_engine": "/api/v1/tracking",
    "notification_engine": "/api/v1/notifications",
    "networking_engine": "/api/v1/networking",
    "referral_engine": "/api/v1/referral",
    "ecoforestry_engine": "/api/v1/ecoforestry",
    "advanced_geospatial_engine": "/api/v1/advanced-geospatial",
    "engine_3d": "/api/v1/3d",
    "wildlife_behavior_engine": "/api/v1/wildlife-behavior",
    "weather_fauna_simulation_engine": "/api/v1/simulation",
    "adaptive_strategy_engine": "/api/v1/adaptive-strategy",
    "recommendation_engine": "/api/v1/recommendations",
    "progression_engine": "/api/v1/progression",
    "collaborative_engine": "/api/v1/collaborative",
    "plugins_engine": "/api/v1/plugins",
    "live_heading_view": "/api/v1/live-heading",
}

# =============================================================================
# FEATURE FLAGS
# =============================================================================
FEATURE_FLAGS: Dict[str, bool] = {
    # Core engines - enabled by default
    "weather_engine": True,
    "scoring_engine": True,
    "strategy_engine": True,
    "geospatial_engine": True,
    "wms_engine": True,
    "ai_engine": True,
    "nutrition_engine": True,
    # Business engines - enabled by default
    "marketplace_engine": True,
    "user_engine": True,
    "admin_engine": True,
    "territory_engine": True,
    "tracking_engine": True,
    "notification_engine": True,
    "networking_engine": True,
    "referral_engine": True,
    # Advanced engines - disabled until implementation
    "ecoforestry_engine": False,
    "advanced_geospatial_engine": False,
    "engine_3d": False,
    "wildlife_behavior_engine": False,
    "weather_fauna_simulation_engine": False,
    "adaptive_strategy_engine": False,
    "recommendation_engine": False,
    "progression_engine": False,
    "collaborative_engine": False,
    "plugins_engine": False,
    # Special modules
    "live_heading_view": False,
}

# =============================================================================
# DEPENDENCIES MAP (allowed dependencies between modules)
# =============================================================================
DEPENDENCIES_MAP: Dict[str, List[str]] = {
    # Core engines have no dependencies on other modules
    "weather_engine": [],
    "scoring_engine": [],
    "strategy_engine": [],
    "geospatial_engine": [],
    "wms_engine": [],
    "ai_engine": [],
    "nutrition_engine": [],
    # Business engines may depend on core engines only
    "marketplace_engine": [],
    "user_engine": [],
    "admin_engine": [],
    "territory_engine": ["geospatial_engine"],
    "tracking_engine": [],
    "notification_engine": [],
    "networking_engine": ["user_engine"],
    "referral_engine": ["user_engine"],
    # Advanced engines may depend on core engines only
    "ecoforestry_engine": ["geospatial_engine"],
    "advanced_geospatial_engine": ["geospatial_engine"],
    "engine_3d": ["geospatial_engine"],
    "wildlife_behavior_engine": ["weather_engine"],
    "weather_fauna_simulation_engine": ["weather_engine", "wildlife_behavior_engine"],
    "adaptive_strategy_engine": ["strategy_engine", "weather_engine"],
    "recommendation_engine": ["scoring_engine", "weather_engine"],
    "progression_engine": ["user_engine"],
    "collaborative_engine": ["user_engine", "networking_engine"],
    "plugins_engine": [],
    # Special modules
    "live_heading_view": ["geospatial_engine", "weather_engine", "strategy_engine"],
}

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "module": {
            "format": "%(asctime)s - [%(module_name)s] - %(levelname)s - %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

# =============================================================================
# MODULE METADATA
# =============================================================================
def get_module_info(module_name: str) -> Dict:
    """Get metadata for a specific module."""
    if module_name not in ALL_MODULES:
        raise ValueError(f"Unknown module: {module_name}")
    
    category = "core"
    if module_name in BUSINESS_ENGINES:
        category = "business"
    elif module_name in ADVANCED_ENGINES:
        category = "advanced"
    elif module_name in SPECIAL_MODULES:
        category = "special"
    
    return {
        "name": module_name,
        "version": MODULE_VERSIONS.get(module_name, "v1"),
        "category": category,
        "enabled": FEATURE_FLAGS.get(module_name, False),
        "api_prefix": API_PREFIXES.get(module_name, ""),
        "dependencies": DEPENDENCIES_MAP.get(module_name, []),
    }
