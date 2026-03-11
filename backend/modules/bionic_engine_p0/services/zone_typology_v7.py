"""
BIONIC V7 — Zone Typology V7
Classification des zones en types enrichis + scoring multi-criteres.

Types: feed, rest, rut, heat_ref, hunt_ref, corridor, mixed
Sous-scores: food, safety, access, stealth, water, topo, dynamic
Score global composite.

Consomme: species_behavior_v7, exclusion data, weather (optionnel)
Consomme par: pipeline_v7
"""

import math
import logging
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Any

from .species_behavior_v7 import (
    get_species_needs,
    get_season_modifier,
    get_weather_modifier,
    SPECIES_NEEDS,
)

logger = logging.getLogger("bionic_engine.zone_typology_v7")

METERS_PER_DEG_LAT = 111320.0

# =====================================================================
# SUBSCORE WEIGHTS (7 sous-scores)
# =====================================================================

SUBSCORE_WEIGHTS = {
    "food": 0.25,
    "safety": 0.20,
    "access": 0.15,
    "stealth": 0.15,
    "water": 0.10,
    "topo": 0.10,
    "dynamic": 0.05,
}

# =====================================================================
# TYPE COLORS + LABELS
# =====================================================================

ZONE_TYPE_CONFIG = {
    "feed":     {"color": "#2E7D32", "label": "Zone d'alimentation"},
    "rest":     {"color": "#1A237E", "label": "Zone de repos / couvert"},
    "rut":      {"color": "#B71C1C", "label": "Zone de rut / reproduction"},
    "heat_ref": {"color": "#E65100", "label": "Zone refuge chaleur"},
    "hunt_ref": {"color": "#4A148C", "label": "Zone refuge pression chasse"},
    "corridor": {"color": "#FF8F00", "label": "Zone de transition / corridor"},
    "mixed":    {"color": "#455A64", "label": "Zone mixte"},
}


def _distance_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Distance approx en metres entre 2 points."""
    dlat = (lat2 - lat1) * METERS_PER_DEG_LAT
    cos_lat = math.cos(math.radians((lat1 + lat2) / 2))
    dlng = (lng2 - lng1) * METERS_PER_DEG_LAT * cos_lat
    return math.sqrt(dlat * dlat + dlng * dlng)


def _nearest_distance_to_type(
    centroid: Dict[str, float],
    exclusions: List[Dict],
    ex_type: str,
) -> float:
    """Distance minimale du centroid vers la plus proche exclusion d'un type."""
    min_dist = float("inf")
    clat, clng = centroid["lat"], centroid["lng"]

    for ex in exclusions:
        if ex.get("type") != ex_type or ex.get("filtered_out"):
            continue
        coords = ex.get("coordinates", [])
        if not coords:
            continue
        for c in coords[:20]:
            d = _distance_m(clat, clng, c[1], c[0])
            if d < min_dist:
                min_dist = d

    return min_dist


def compute_subscores(
    zone: Dict,
    layer_id: str,
    species: str,
    exclusions: List[Dict],
    weather: Dict = None,
    month: int = None,
    dem_stats: Dict = None,
    dem_point: Dict = None,
) -> Dict[str, float]:
    """
    Calcule les 7 sous-scores (0-100) pour une zone.
    dem_stats: Stats globales DEM {elevation_min, elevation_max, slope_mean_deg, ...}
    dem_point: Valeurs DEM au centroid {elevation_m, slope_deg, aspect_deg, roughness}
    """
    centroid = zone.get("centroid", {"lat": 0, "lng": 0})
    area_m2 = zone.get("area_m2", 5000)
    compactness = zone.get("compactness", 0.5)

    # Distances aux exclusions
    dist_water = _nearest_distance_to_type(centroid, exclusions, "water")
    dist_roads = _nearest_distance_to_type(centroid, exclusions, "roads")
    dist_urban = _nearest_distance_to_type(centroid, exclusions, "urban")
    dist_infra = _nearest_distance_to_type(centroid, exclusions, "infrastructure")

    # Wetland proximity (positive for moose)
    dist_wetland = float("inf")
    for ex in exclusions:
        if ex.get("type") == "wetland":
            coords = ex.get("coordinates", [])
            for c in coords[:10]:
                d = _distance_m(centroid["lat"], centroid["lng"], c[1], c[0])
                if d < dist_wetland:
                    dist_wetland = d

    # --- FOOD SCORE ---
    food = 50.0
    if layer_id in ("alimentation", "ndvi", "salines"):
        food += 25.0
    if dist_water < 300:
        food += 10.0 * (1.0 - dist_water / 300)
    if dist_wetland < 500 and species == "moose":
        food += 15.0 * (1.0 - dist_wetland / 500)
    if 5000 < area_m2 < 20000:
        food += 5.0
    food = min(100, max(0, food))

    # --- SAFETY SCORE ---
    safety = 30.0
    if dist_roads > 500:
        safety += 25.0
    elif dist_roads > 200:
        safety += 15.0 * ((dist_roads - 200) / 300)
    if dist_urban > 1000:
        safety += 20.0
    elif dist_urban > 500:
        safety += 10.0 * ((dist_urban - 500) / 500)
    if dist_infra > 300:
        safety += 10.0
    if layer_id in ("repos", "habitats"):
        safety += 10.0
    safety = min(100, max(0, safety))

    # --- ACCESS SCORE ---
    access = 40.0
    if dist_roads < 1500:
        access += 20.0 * (1.0 - max(0, dist_roads - 200) / 1300)
    if dist_water < 500:
        access += 15.0 * (1.0 - dist_water / 500)
    if area_m2 > 3000:
        access += 10.0
    if compactness > 0.4:
        access += 10.0
    access = min(100, max(0, access))

    # --- STEALTH SCORE ---
    stealth = 35.0
    if dist_roads > 300:
        stealth += 15.0
    if dist_urban > 800:
        stealth += 15.0
    if layer_id in ("repos", "habitats", "peuplements"):
        stealth += 15.0
    if compactness > 0.5:
        stealth += 5.0
    if area_m2 > 8000:
        stealth += 5.0
    stealth = min(100, max(0, stealth))

    # --- WATER SCORE ---
    water = 20.0
    if dist_water < 50:
        water = 95.0
    elif dist_water < 200:
        water = 80.0 - 30.0 * ((dist_water - 50) / 150)
    elif dist_water < 500:
        water = 50.0 - 20.0 * ((dist_water - 200) / 300)
    elif dist_water < 1000:
        water = 30.0 - 10.0 * ((dist_water - 500) / 500)
    water = min(100, max(0, water))

    # --- TOPO SCORE --- (ENHANCED with real DEM data when available)
    topo = 50.0
    dem_available = dem_point is not None and dem_stats is not None
    if dem_available:
        slope_deg = dem_point.get("slope_deg", 15)
        elevation_m = dem_point.get("elevation_m", 300)
        roughness_val = dem_point.get("roughness", 2)
        elev_min = dem_stats.get("elevation_min", 0)
        elev_max = dem_stats.get("elevation_max", 1000)
        elev_range = max(1, elev_max - elev_min)
        rel_elev = (elevation_m - elev_min) / elev_range

        # Pente: douce = bonus, raide = malus
        if slope_deg < 8:
            topo += 20
        elif slope_deg < 15:
            topo += 12
        elif slope_deg < 25:
            topo += 0
        elif slope_deg < 35:
            topo -= 10
        else:
            topo -= 20

        # Elevation relative: mi-pente = favorable (zone transitoire riche)
        if 0.25 < rel_elev < 0.75:
            topo += 10
        elif rel_elev < 0.1 or rel_elev > 0.9:
            topo -= 5

        # Rugosité: faible = terrain praticable
        if roughness_val < 3:
            topo += 8
        elif roughness_val > 8:
            topo -= 8

        # Area bonus (kept)
        if area_m2 > 5000:
            topo += 5
    else:
        # Fallback heuristique (comportement V7 original)
        if layer_id in ("pentes", "altitude", "orientation"):
            topo += 20.0
        if area_m2 > 5000:
            topo += 10.0
        if compactness > 0.3:
            topo += 10.0
    topo = min(100, max(0, topo))

    # --- DYNAMIC SCORE ---
    dynamic = 50.0
    if month is not None:
        season_mod = get_season_modifier(layer_id, month)
        dynamic = min(100, max(0, dynamic * season_mod))
    if weather:
        temp = weather.get("temperature", 15)
        if 5 < temp < 20:
            dynamic += 10.0
        wind = weather.get("wind_speed", 10)
        if wind > 30:
            dynamic -= 15.0
        precip = weather.get("precipitation", 0)
        if precip > 5:
            dynamic -= 10.0
    dynamic = min(100, max(0, dynamic))

    return {
        "food": round(food, 1),
        "safety": round(safety, 1),
        "access": round(access, 1),
        "stealth": round(stealth, 1),
        "water": round(water, 1),
        "topo": round(topo, 1),
        "dynamic": round(dynamic, 1),
    }


def compute_global_score(subscores: Dict[str, float]) -> float:
    """Calcule le score global pondere."""
    total = 0.0
    for key, weight in SUBSCORE_WEIGHTS.items():
        total += subscores.get(key, 50.0) * weight
    return round(min(100, max(0, total)), 1)


def classify_zone_type(
    subscores: Dict[str, float],
    layer_id: str,
    species: str,
    month: int = 10,
) -> Tuple[str, float]:
    """
    BIONIC V7.4 — Classification layer-ID primaire.
    
    Le layer_id EST le signal écologique primaire:
    - alimentation/ndvi/salines → feed
    - repos/habitats/peuplements → rest (habitats peut varier)
    - rut → rut
    - corridors/trajets → corridor
    
    Le season modifier affecte le SCORE (attractivité), 
    PAS la classification (type stable toute l'année).
    Les subscores servent à confirmer/ajuster la confiance.
    
    Returns: (zone_type, confidence)
    """
    # === CLASSIFICATION PRIMAIRE PAR LAYER-ID ===
    LAYER_PRIMARY_TYPE = {
        "alimentation": "feed",
        "ndvi": "feed",
        "salines": "feed",
        "repos": "rest",
        "peuplements": "rest",
        "rut": "rut",
        "corridors": "corridor",
        "trajets": "corridor",
    }
    
    forced_type = LAYER_PRIMARY_TYPE.get(layer_id)
    
    if forced_type:
        # Classification forcée par layer — calculer confiance via subscores
        confidence = _compute_confidence_for_type(forced_type, subscores)
        return forced_type, confidence
    
    # === CLASSIFICATION MULTI-CRITÈRES (habitats, affuts, etc.) ===
    # Pour les layers sans type forcé, calcul par subscores SANS season modifier
    type_scores = {}
    
    # FEED
    type_scores["feed"] = subscores["food"] * 0.5 + subscores["water"] * 0.2 + subscores["topo"] * 0.15 + subscores["access"] * 0.15
    
    # REST
    type_scores["rest"] = subscores["safety"] * 0.35 + subscores["stealth"] * 0.30 + subscores["topo"] * 0.15 + subscores["water"] * 0.10 + subscores["food"] * 0.10
    
    # RUT (pondération accrue food+water+dynamic pour différencier de rest)
    type_scores["rut"] = subscores["food"] * 0.15 + subscores["access"] * 0.2 + subscores["water"] * 0.2 + subscores["topo"] * 0.25 + subscores["dynamic"] * 0.2
    
    # HEAT REFUGE
    type_scores["heat_ref"] = subscores["water"] * 0.35 + subscores["stealth"] * 0.25 + subscores["topo"] * 0.25 + subscores["safety"] * 0.15
    
    # HUNT REFUGE
    type_scores["hunt_ref"] = subscores["safety"] * 0.45 + subscores["stealth"] * 0.3 + subscores["topo"] * 0.15 + subscores["access"] * 0.1
    
    # CORRIDOR
    type_scores["corridor"] = subscores["access"] * 0.3 + subscores["topo"] * 0.25 + subscores["safety"] * 0.2 + subscores["stealth"] * 0.15 + subscores["dynamic"] * 0.1

    # Find dominant — NO season modifier on classification
    best_type = max(type_scores, key=type_scores.get)
    sorted_scores = sorted(type_scores.values(), reverse=True)
    if len(sorted_scores) >= 2 and sorted_scores[0] > 0:
        gap = (sorted_scores[0] - sorted_scores[1]) / sorted_scores[0]
    else:
        gap = 0.0

    if gap < 0.08:
        best_type = "mixed"

    confidence = min(1.0, max(0.2, 0.3 + gap * 2.0))
    if best_type == "mixed":
        confidence = max(0.2, confidence * 0.7)

    return best_type, round(confidence, 2)


def _compute_confidence_for_type(zone_type: str, subscores: Dict[str, float]) -> float:
    """Compute confidence for a forced type based on how well subscores match."""
    if zone_type == "feed":
        primary = subscores.get("food", 50)
        confidence = 0.5 + (primary - 50) / 200  # food=80 → conf=0.65
    elif zone_type == "rest":
        primary = subscores.get("safety", 50)
        confidence = 0.5 + (primary - 50) / 200
    elif zone_type == "rut":
        primary = (subscores.get("dynamic", 50) + subscores.get("water", 50)) / 2
        confidence = 0.5 + (primary - 50) / 200
    elif zone_type == "corridor":
        primary = subscores.get("access", 50)
        confidence = 0.5 + (primary - 50) / 200
    else:
        confidence = 0.5
    return round(min(0.95, max(0.35, confidence)), 2)


def get_zone_season_relevance(zone_type: str) -> Dict[str, float]:
    """Retourne la pertinence saisonniere d'un type de zone."""
    mods = {
        "spring": get_season_modifier(zone_type, 4),
        "summer": get_season_modifier(zone_type, 7),
        "fall": get_season_modifier(zone_type, 10),
        "winter": get_season_modifier(zone_type, 1),
    }
    max_val = max(mods.values()) or 1.0
    return {k: round(v / max_val, 2) for k, v in mods.items()}


def enrich_zone_v7(
    zone: Dict,
    layer_id: str,
    species: str,
    exclusions: List[Dict],
    weather: Dict = None,
    month: int = None,
    dem_stats: Dict = None,
    dem_point: Dict = None,
) -> Dict:
    """
    Enrichit une zone V6 avec la typologie et le scoring V7.
    Non-destructif: ajoute des champs sans modifier les existants.
    dem_stats: Stats globales DEM
    dem_point: Valeurs DEM au centroid de la zone
    """
    if month is None:
        month = datetime.now(timezone.utc).month

    subscores = compute_subscores(
        zone, layer_id, species, exclusions, weather, month,
        dem_stats=dem_stats, dem_point=dem_point,
    )
    global_score = compute_global_score(subscores)
    # BIONIC V7.4: Classification SANS season modifier (type stable toute l'année)
    zone_type, confidence = classify_zone_type(subscores, layer_id, species, month)
    # Season modifier applied to score only (attractivity varies by season)
    season_mod = get_season_modifier(zone_type, month)
    seasonal_score = global_score * min(1.2, max(0.6, season_mod))

    type_config = ZONE_TYPE_CONFIG.get(zone_type, ZONE_TYPE_CONFIG["mixed"])

    zone["v7"] = {
        "zone_type": zone_type,
        "zone_type_label": type_config["label"],
        "zone_type_color": type_config["color"],
        "score_global": round(seasonal_score, 1),
        "score_raw": round(global_score, 1),
        "subscores": subscores,
        "confidence": confidence,
        "season_relevance": get_zone_season_relevance(zone_type),
        "season_modifier": round(season_mod, 2),
        "month": month,
        "species": species,
        "layer_id": layer_id,
        "dem_enhanced": dem_point is not None,
    }

    # Add DEM point data to zone if available
    if dem_point:
        zone["v7"]["terrain"] = dem_point

    return zone


def detect_hotspots(
    zones: List[Dict],
    threshold: float = 70.0,
) -> List[Dict]:
    """
    Detecte les hotspots parmi les zones enrichies V7.
    Un hotspot = zone avec score global >= threshold.
    """
    hotspots = []
    for zone in zones:
        v7 = zone.get("v7", {})
        if not v7:
            continue
        score = v7.get("score_global", 0)
        if score >= threshold:
            zone_type = v7.get("zone_type", "mixed")
            hotspot_type = _map_zone_to_hotspot(zone_type)
            v7["hotspot"] = True
            v7["hotspot_type"] = hotspot_type
            hotspots.append(zone)
        else:
            v7["hotspot"] = False
            v7["hotspot_type"] = None

    return hotspots


def _map_zone_to_hotspot(zone_type: str) -> str:
    """Mappe un type de zone a un type de hotspot."""
    mapping = {
        "feed": "alimentation",
        "rest": "repos",
        "rut": "rut",
        "heat_ref": "refuge",
        "hunt_ref": "refuge",
        "corridor": "passage",
        "mixed": "general",
    }
    return mapping.get(zone_type, "general")
