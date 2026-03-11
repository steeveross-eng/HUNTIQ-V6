"""BIONIC V3 - Modular Architecture

This package contains all modular engines for the BIONIC platform.
Each module is isolated and versioned independently.

Categories:
- CORE: Essential engines (weather, scoring, strategy, geospatial, wms, ai, nutrition)
- BUSINESS: Business logic engines (marketplace, user, admin, territory, etc.)
- ADVANCED: Advanced features (ecoforestry, 3d, wildlife behavior, simulation, etc.)
- SPECIAL: Special modules (live_heading_view)
- DATA_LAYERS: Data layer definitions

Rules:
1. Modules are isolated - no cross-module imports except through public interfaces
2. Each module has its own router, models, and service
3. Versioning follows /v1/, /v2/ convention
4. New features = new modules (never modify existing modules)
"""

__version__ = "3.0.0"
__author__ = "BIONIC Team"

# Module categories will be populated as modules are implemented
CORE_ENGINES = []
BUSINESS_ENGINES = []
ADVANCED_ENGINES = []
SPECIAL_MODULES = []
DATA_LAYERS = []
