"""
# ══════════════════════════════════════════════════════════════
# LEGACY FIGÉ — NE PAS MODIFIER, NE PAS RÉACTIVER, NE PAS MIGRER
# Raison: Remplacé par bionic_engine_p0/ (pipeline V7 canonique)
# Date gel: 2026-03-10
# BCE: Ce fichier est exclu du pipeline de conformité
# ══════════════════════════════════════════════════════════════
SHIM de retrocompatibilite — Phase 1.8
Le contenu original de territory.py (4912 lignes) a ete decoupe en package
routes/territory/. Ce fichier re-exporte tous les symboles publics pour ne
casser aucun import existant.
"""

from routes.territory import (
    # Routers
    territory_router,
    territories_router,
    # DB
    get_db,
    close_db,
    # Lifecycle
    init_territory_module,
    shutdown_territory_module,
    # Sync functions
    sync_territory_to_partnership,
    sync_partnership_to_territory,
    on_territory_created,
    on_territory_updated,
    on_partner_status_changed,
    seed_sample_territories,
    # Utilities
    haversine_distance,
    serialize_doc,
    generate_internal_id,
    calculate_global_score,
    # Constants
    PROVINCE_NAMES,
    TYPE_LABELS,
    SPECIES_CONFIG,
    BIONIC_PRODUCTS,
    COMPETITOR_PRODUCTS,
    SPECIES_NUTRITION,
    SPECIES_HABITAT_RULES,
    WMS_LAYERS,
    calculate_point_probability,
)

__all__ = [
    "territory_router",
    "territories_router",
    "get_db",
    "close_db",
    "init_territory_module",
    "shutdown_territory_module",
    "sync_territory_to_partnership",
    "sync_partnership_to_territory",
    "on_territory_created",
    "on_territory_updated",
    "on_partner_status_changed",
    "seed_sample_territories",
    "haversine_distance",
    "serialize_doc",
    "generate_internal_id",
    "calculate_global_score",
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
