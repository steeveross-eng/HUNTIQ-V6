"""
MODULE P1 — Zone Penalty Engine
BIONIC V5 — Pénalités Semi-Statiques

Calcule des multiplicateurs de pénalité (0.0 → 1.0) pour chaque zone valide.
Appliqué APRÈS exclusions dures (P0), AVANT scoring final.

Pénalités:
  1. Bords d'eau (proximité eau)
  2. Semi-urbain (proximité urbain)
  3. Routes (proximité routes)
  4. Infrastructure (proximité infra)
  5. Fragmentation (géométrie zone)

100% indépendant. Aucun couplage avec le rasteriseur ou P0.
Orchestré uniquement par zone_engine_core_v2._process_single_layer().
"""

import math
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger("bionic_engine.zone_penalty_engine")

METERS_PER_DEG_LAT = 111320.0

# =====================================================================
# BANDES DE PROXIMITÉ (mètres)
# =====================================================================
BAND_CLOSE = 200    # < 200m
BAND_MEDIUM = 500   # 200-500m
BAND_FAR = 1000     # 500-1000m

# =====================================================================
# MATRICE DE PÉNALITÉ PAR COUCHE × TYPE DE PROXIMITÉ
# Format: { layer_id: { exclusion_type: { "close": mult, "medium": mult, "far": mult } } }
#
# Ajustements BIONIC V5 300% validés:
#   - Eau close repos/rut: ×0.70 (exposition accrue)
#   - Routes close: ×0.30 (risque élevé + perturbation)
#   - Infra close: ×0.40 (alignement routes)
#   - Semi-urbain Far plafonné à ×0.85
#   - "Très fort" plafonné à ×0.25
#   - "Fort" plafonné à ×0.40
# =====================================================================
PENALTY_MATRIX: Dict[str, Dict[str, Dict[str, float]]] = {
    "alimentation": {
        "water":          {"close": 1.05, "medium": 1.00, "far": 1.00},
        "urban":          {"close": 0.40, "medium": 0.65, "far": 0.85},
        "roads":          {"close": 0.30, "medium": 0.60, "far": 0.85},
        "infrastructure": {"close": 0.40, "medium": 0.70, "far": 0.90},
    },
    "repos": {
        "water":          {"close": 0.70, "medium": 0.90, "far": 1.00},
        "urban":          {"close": 0.25, "medium": 0.55, "far": 0.80},
        "roads":          {"close": 0.25, "medium": 0.55, "far": 0.80},
        "infrastructure": {"close": 0.35, "medium": 0.65, "far": 0.85},
    },
    "rut": {
        "water":          {"close": 0.70, "medium": 0.90, "far": 1.00},
        "urban":          {"close": 0.25, "medium": 0.55, "far": 0.80},
        "roads":          {"close": 0.30, "medium": 0.60, "far": 0.85},
        "infrastructure": {"close": 0.35, "medium": 0.65, "far": 0.85},
    },
    "habitats": {
        "water":          {"close": 0.95, "medium": 1.00, "far": 1.00},
        "urban":          {"close": 0.40, "medium": 0.65, "far": 0.85},
        "roads":          {"close": 0.45, "medium": 0.70, "far": 0.90},
        "infrastructure": {"close": 0.45, "medium": 0.70, "far": 0.90},
    },
    "corridors": {
        "water":          {"close": 0.95, "medium": 1.00, "far": 1.00},
        "urban":          {"close": 0.40, "medium": 0.65, "far": 0.85},
        "roads":          {"close": 0.50, "medium": 0.70, "far": 0.90},
        "infrastructure": {"close": 0.50, "medium": 0.70, "far": 0.90},
    },
}

# Couches non listées explicitement: pénalités par défaut (modérées)
_DEFAULT_PENALTIES = {
    "water":          {"close": 0.90, "medium": 1.00, "far": 1.00},
    "urban":          {"close": 0.40, "medium": 0.65, "far": 0.85},
    "roads":          {"close": 0.40, "medium": 0.65, "far": 0.85},
    "infrastructure": {"close": 0.45, "medium": 0.70, "far": 0.90},
}

# =====================================================================
# FRAGMENTATION — Pénalité géométrique
# =====================================================================
# Compacité <0.3 ET area <10000m² → ×0.60
# Compacité <0.5 → ×0.80 (niveau intermédiaire)
FRAG_SEVERE_AREA = 10000.0
FRAG_SEVERE_COMPACT = 0.3
FRAG_SEVERE_MULT = 0.60
FRAG_MODERATE_COMPACT = 0.5
FRAG_MODERATE_MULT = 0.80


def _haversine_approx(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Distance approximative en mètres (rapide, suffisant pour pénalités)."""
    cos_lat = math.cos(math.radians((lat1 + lat2) / 2))
    dlat = (lat2 - lat1) * METERS_PER_DEG_LAT
    dlng = (lng2 - lng1) * METERS_PER_DEG_LAT * cos_lat
    return math.sqrt(dlat * dlat + dlng * dlng)


def _min_distance_to_exclusion_type(
    clat: float, clng: float,
    exclusions: List[Dict],
    target_type: str
) -> float:
    """
    Distance minimale (mètres) entre un point et les exclusions d'un type donné.
    Retourne float('inf') si aucune exclusion de ce type trouvée.
    """
    min_dist = float('inf')

    for ex in exclusions:
        ex_type = ex.get("type", "")
        if ex_type != target_type:
            continue

        coords = ex.get("coordinates", [])
        if not coords:
            continue

        geom = ex.get("geometry_type", "polygon")

        if geom == "polygon" and len(coords) >= 3:
            # Distance au point le plus proche du polygone
            for coord in coords:
                d = _haversine_approx(clat, clng, coord[1], coord[0])
                if d < min_dist:
                    min_dist = d
                    if d < 10:  # Early exit: inside or touching
                        return d

        elif geom == "line" and len(coords) >= 2:
            # Distance au segment le plus proche
            for i in range(len(coords) - 1):
                x1, y1 = coords[i][0], coords[i][1]
                x2, y2 = coords[i + 1][0], coords[i + 1][1]
                # Projection sur segment
                dx, dy = x2 - x1, y2 - y1
                len_sq = dx * dx + dy * dy
                if len_sq > 0:
                    t = max(0, min(1, ((clng - x1) * dx + (clat - y1) * dy) / len_sq))
                    px, py = x1 + t * dx, y1 + t * dy
                else:
                    px, py = x1, y1
                d = _haversine_approx(clat, clng, py, px)
                if d < min_dist:
                    min_dist = d
                    if d < 10:
                        return d

    return min_dist


def _distance_to_band(distance_m: float) -> str:
    """Convertit une distance en bande de proximité."""
    if distance_m < BAND_CLOSE:
        return "close"
    elif distance_m < BAND_MEDIUM:
        return "medium"
    elif distance_m < BAND_FAR:
        return "far"
    return "none"


def calculate_zone_penalty(
    zone: Dict,
    layer_id: str,
    exclusions: List[Dict],
) -> Tuple[float, Dict[str, float]]:
    """
    Calcule le multiplicateur de pénalité total pour une zone.

    Args:
        zone: Zone avec 'coordinates', 'area_m2', 'compactness', 'centroid'
        layer_id: ID couche BIONIC (alimentation, repos, rut, etc.)
        exclusions: Liste des exclusions Overpass

    Returns:
        (penalty_factor, details)
        penalty_factor: multiplicateur total (0.0 → 1.0+)
        details: { "water": 0.95, "urban": 1.0, "roads": 0.85, ... }
    """
    centroid = zone.get("centroid", {})
    clat = centroid.get("lat", 0)
    clng = centroid.get("lng", 0)

    layer_penalties = PENALTY_MATRIX.get(layer_id, _DEFAULT_PENALTIES)
    details = {}
    total_mult = 1.0

    # 1-4: Pénalités de proximité (eau, urbain, routes, infrastructure)
    for excl_type in ("water", "urban", "roads", "infrastructure"):
        dist = _min_distance_to_exclusion_type(clat, clng, exclusions, excl_type)
        band = _distance_to_band(dist)

        if band == "none":
            details[excl_type] = 1.0
            continue

        type_penalties = layer_penalties.get(excl_type, _DEFAULT_PENALTIES.get(excl_type, {}))
        mult = type_penalties.get(band, 1.0)
        details[excl_type] = round(mult, 3)
        total_mult *= mult

    # 5: Pénalité de fragmentation (géométrie)
    area = zone.get("area_m2", 0)
    compactness = zone.get("compactness", 1.0)

    if area < FRAG_SEVERE_AREA and compactness < FRAG_SEVERE_COMPACT:
        details["fragmentation"] = FRAG_SEVERE_MULT
        total_mult *= FRAG_SEVERE_MULT
    elif compactness < FRAG_MODERATE_COMPACT:
        details["fragmentation"] = FRAG_MODERATE_MULT
        total_mult *= FRAG_MODERATE_MULT
    else:
        details["fragmentation"] = 1.0

    # Plafonnement: le multiplicateur total ne descend pas en dessous de 0.15
    # (une zone très pénalisée reste visible mais avec score minimal)
    total_mult = max(0.15, min(1.10, total_mult))

    return round(total_mult, 3), details
