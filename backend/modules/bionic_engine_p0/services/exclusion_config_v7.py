"""
BIONIC V7 — Exclusion Config V7
Configuration OFFICIELLE des buffers et seuils d'exclusion geometrique.

Marges REDUITES calibrées pour les contextes ruraux québécois (chasse).
Remplace exclusion_config_v6 pour le moteur V7.

Orchestré EXCLUSIVEMENT par exclusion_engine_v7.py
"""

# =====================================================================
# BUFFERS GEOMETRIQUES V7 (metres) PAR TYPE ET SOUS-TYPE
# Marges réduites — Instruction officielle P0
# =====================================================================

BUFFER_CONFIG_V7 = {
    "water": {
        "lake": 75,           # Grand plan d'eau: 200 → 75
        "reservoir": 75,      # Grand plan d'eau: 200 → 75
        "pond": 30,
        "micro_water": 0,
        "river": 40,          # Rivière: 100 → 40
        "riverbank": 40,
        "canal": 30,
        "stream": 10,         # Ruisseau: 50 → 10
        "ditch": 0,
        "drain": 0,
        "water": 75,          # Grand plan d'eau générique
        "basin": 30,
        "salt_pond": 30,
        "bay": 75,
        "strait": 75,
        "coastline": 75,
        "wetland": 0,
        "_default": 30,
    },
    "roads": {
        "motorway": 120,
        "motorway_link": 100,
        "trunk": 120,
        "trunk_link": 100,
        "primary": 75,        # Route principale: 100 → 75
        "primary_link": 60,
        "secondary": 35,      # Route secondaire: 50 → 35
        "secondary_link": 30,
        "tertiary": 20,
        "tertiary_link": 15,
        "residential": 20,
        "living_street": 10,
        "service": 10,
        "unclassified": 10,
        "track": 10,          # Chemin de terre: 25 → 10
        "footway": 0,
        "cycleway": 0,
        "path": 0,
        "pedestrian": 0,
        "_default": 15,
    },
    "urban": {
        "residential": 120,   # Habitation: 150 → 120
        "commercial": 100,
        "industrial": 100,
        "retail": 80,
        "farmyard": 75,       # Bâtiments agricoles: 100 → 75
        "recreation_ground": 30,
        "cemetery": 30,
        "construction": 120,
        "military": 150,
        "quarry": 120,
        "landfill": 120,
        "building": 20,
        "_default": 40,
    },
    "infrastructure": {
        "rail": 60,
        "siding": 25,
        "spur": 25,
        "narrow_gauge": 30,
        "subway": 0,
        "tram": 25,
        "aerodrome": 400,
        "runway": 400,
        "taxiway": 250,
        "helipad": 150,
        "plant": 150,
        "substation": 80,
        "line": 30,
        "works": 120,
        "storage_tank": 60,
        "water_tower": 30,
        "chimney": 80,
        "tower": 25,
        "mast": 25,
        "_default": 40,
    },
}

# =====================================================================
# SEUILS D'INTERSECTION V7 — ratio area_overlap / area_zone
# Relaxés pour contexte rural québécois
# =====================================================================

INTERSECTION_THRESHOLDS_V7 = {
    "water": 0.03,           # V7.1 BCE-4X: strictifié de 0.08 à 0.03 (quasi-zéro eau)
    "urban": 0.12,           # V6: 0.08 → V7: 0.12 (tolère bordure zone urbaine)
    "roads": 0.20,           # V6: 0.15 → V7: 0.20 (routes rurales fréquentes)
    "infrastructure": 0.25,  # V6: 0.18 → V7: 0.25 (lignes électriques rurales)
}

# BCE-4X: Seuils spécifiques par couche — les affûts et salines ont tolérance ZÉRO eau
LAYER_WATER_THRESHOLDS = {
    "affuts": 0.0,           # BCE-4X: STRICT — aucune eau sur un affût
    "salines": 0.0,          # BCE-4X: STRICT — aucune eau sur une saline
    "trajets": 0.01,         # BCE-4X: quasi-zéro
    "habitats": 0.03,        # BCE-4X: très faible tolérance
    "alimentation": 0.05,    # Eau = ressource pour certaines espèces
    "repos": 0.04,           # Faible tolérance
    "corridors": 0.06,       # Corridors peuvent longer l'eau
}

# =====================================================================
# BANDES DE PENALITE V7
# =====================================================================

BAND_CLOSE_M_V7 = 200
BAND_MEDIUM_M_V7 = 500
BAND_FAR_M_V7 = 1000

# =====================================================================
# ZONE TRIMMING V7 — seuils ajustés
# =====================================================================

TRIMMING_MIN_AREA_M2_V7 = 3000.0      # V6: 5000 → V7: 3000 (petites zones rurales ok)
TRIMMING_MIN_COMPACTNESS_V7 = 0.20     # V6: 0.25 → V7: 0.20
TRIMMING_MAX_AREA_M2_V7 = 500000.0

# =====================================================================
# VEGETATION V7 — densité minimale
# =====================================================================

VEGETATION_MIN_DENSITY_V7 = 0.20       # 0.35 → 0.20

# =====================================================================
# PRESSION ANTHROPIQUE V7 — seuils relaxés pour rural
# =====================================================================

ANTHROPIC_THRESHOLDS_V7 = {
    "urban_roads_combo": {"urban_max": 0.40, "roads_max": 0.45},
    "major_road_alone": {"roads_max": 0.25},
    "infra_roads_combo": {"infra_max": 0.35, "roads_max": 0.45},
    "urban_alone": {"urban_max": 0.25},
    "combined_product_min": 0.10,
}


def get_buffer_m_v7(exclusion_type: str, sub_type: str) -> float:
    """Retourne le buffer V7 en metres pour un type/sous-type d'exclusion."""
    type_config = BUFFER_CONFIG_V7.get(exclusion_type, {})
    st = (sub_type or "").lower()
    return type_config.get(st, type_config.get("_default", 0))
