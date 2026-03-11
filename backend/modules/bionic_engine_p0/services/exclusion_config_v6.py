# ══════════════════════════════════════════════════════════════
# LEGACY FIGÉ — NE PAS MODIFIER
# Remplacé par: exclusion_config_v7.py (marges V7 REDUITES)
# Date gel: 2026-03-10
# Motif: Incident P0 — marges trop agressives en contexte rural
# ══════════════════════════════════════════════════════════════
"""
BIONIC V6 — Exclusion Config V6
Configuration des buffers et seuils d'exclusion geometrique Shapely.

Buffers adaptatifs par sous-type (autoroute != chemin),
seuils d'intersection par type, bandes de penalite.

Orchestré par exclusion_engine_v6.py
"""

# =====================================================================
# BUFFERS GEOMETRIQUES (metres) PAR TYPE ET SOUS-TYPE
# =====================================================================

BUFFER_CONFIG_V6 = {
    "water": {
        "lake": 50,
        "reservoir": 50,
        "pond": 30,
        "micro_water": 0,
        "river": 40,
        "riverbank": 40,
        "canal": 30,
        "stream": 10,
        "ditch": 0,
        "drain": 0,
        "water": 40,
        "basin": 30,
        "salt_pond": 30,
        "bay": 50,
        "strait": 50,
        "coastline": 50,
        "wetland": 0,
        "_default": 30,
    },
    "roads": {
        "motorway": 150,
        "motorway_link": 120,
        "trunk": 150,
        "trunk_link": 120,
        "primary": 100,
        "primary_link": 80,
        "secondary": 60,
        "secondary_link": 50,
        "tertiary": 30,
        "tertiary_link": 25,
        "residential": 30,
        "living_street": 20,
        "service": 20,
        "unclassified": 20,
        "track": 0,
        "footway": 0,
        "cycleway": 0,
        "path": 0,
        "pedestrian": 0,
        "_default": 25,
    },
    "urban": {
        "residential": 100,
        "commercial": 100,
        "industrial": 100,
        "retail": 80,
        # BIONIC V7.3: farmland/farmyard/orchard/vineyard/allotments REMOVED
        # These agricultural tags are NOT urban and caused 0-zone generation
        # in rural hunting contexts.
        "recreation_ground": 30,
        "cemetery": 30,
        "construction": 150,
        "military": 150,
        "quarry": 150,
        "landfill": 150,
        "building": 20,
        "_default": 50,
    },
    "infrastructure": {
        "rail": 80,
        "siding": 30,
        "spur": 30,
        "narrow_gauge": 40,
        "subway": 0,
        "tram": 30,
        "aerodrome": 500,
        "runway": 500,
        "taxiway": 300,
        "helipad": 200,
        "plant": 200,
        "substation": 100,
        "line": 40,
        "works": 150,
        "storage_tank": 80,
        "water_tower": 40,
        "chimney": 100,
        "tower": 30,
        "mast": 30,
        "_default": 50,
    },
}

# =====================================================================
# SEUILS D'INTERSECTION — ratio area_overlap / area_zone
# Si le ratio depasse le seuil, la zone est REJETEE (P0-V6)
# =====================================================================

INTERSECTION_THRESHOLDS_V6 = {
    "water": 0.05,
    "urban": 0.08,       # Strict: real urban (residential/commercial/industrial)
    "roads": 0.15,        # V7.3: relaxed from 0.08 — rural roads are common but low-traffic
    "infrastructure": 0.18, # V7.3: relaxed from 0.12 — tolerates rural infra (power lines, tracks)
}

# =====================================================================
# BANDES DE PENALITE P1 (identiques a V5 pour compatibilite)
# =====================================================================

BAND_CLOSE_M = 200
BAND_MEDIUM_M = 500
BAND_FAR_M = 1000

# =====================================================================
# ZONE TRIMMING P2 — seuils min
# =====================================================================

TRIMMING_MIN_AREA_M2 = 5000.0
TRIMMING_MIN_COMPACTNESS = 0.25
TRIMMING_MAX_AREA_M2 = 500000.0  # 0.5 km² max per zone


def get_buffer_m(exclusion_type: str, sub_type: str) -> float:
    """Retourne le buffer en metres pour un type/sous-type d'exclusion."""
    type_config = BUFFER_CONFIG_V6.get(exclusion_type, {})
    st = (sub_type or "").lower()
    return type_config.get(st, type_config.get("_default", 0))
