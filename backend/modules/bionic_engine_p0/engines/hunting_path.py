"""
BIONIC HUNT — Hunting Path Engine V1
STEVE-MAX++: Moteur de generation de trajet de chasse optimal.

Le trajet:
- Relie les zones cles dans un ordre strategique
- Suit la topographie et la logique ecologique
- Maximise les chances de rencontre
- Est lineaire, continu et marchable

Algorithme:
1. Collecte les centroides des zones cles (habitats, rut, repos, alimentation, affuts)
2. Ordonne les zones par priorite ecologique (nearest-neighbor TSP)
3. Smooth le trajet pour un rendu naturel
4. Ajoute des waypoints strategiques (saline, cache, alimentation secondaire)

Note: Le vent est gere separement par Wind Intelligence Engine (#4).
"""

import logging
import math
from typing import Dict, List, Any, Tuple, Optional

logger = logging.getLogger("bionic.hunting_path")

# Zone priority for hunting path (higher = visit first)
ZONE_PRIORITY = {
    "affuts": 10,     # Observation posts — strategic start/end
    "repos": 8,       # Rest zones — high encounter probability
    "rut": 9,         # Rut zones — peak activity
    "habitats": 7,    # Habitat zones — general presence
    "alimentation": 6,# Feeding zones — predictable activity
    "corridors": 5,   # Movement corridors — transit areas
    "salines": 8,     # Salt licks — attraction points
    "trajets": 4,     # Existing trails
    "peuplements": 3, # Forest stands
}

# Hunting path style
PATH_STYLE = {
    "color": "#FF6B00",
    "weight": 3,
    "opacity": 0.9,
    "dashArray": "12, 6",
}

# Waypoint markers for the path
WAYPOINT_TYPES = {
    "start": {"icon": "flag", "color": "#4CAF50", "label": "Depart"},
    "saline": {"icon": "droplet", "color": "#FFEB3B", "label": "Saline suggeree"},
    "cache": {"icon": "eye", "color": "#795548", "label": "Cache suggeree"},
    # ALIMENTATION-V2: "alimentation_sec" SUPPRIME — directive STEEVE-MAX
    "end": {"icon": "target", "color": "#F44336", "label": "Position finale"},
}


def _haversine_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _bearing(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Returns bearing in degrees from point 1 to point 2."""
    dlng = math.radians(lng2 - lng1)
    lat1_r, lat2_r = math.radians(lat1), math.radians(lat2)
    x = math.sin(dlng) * math.cos(lat2_r)
    y = math.cos(lat1_r) * math.sin(lat2_r) - math.sin(lat1_r) * math.cos(lat2_r) * math.cos(dlng)
    return (math.degrees(math.atan2(x, y)) + 360) % 360



def _offset_point(lat: float, lng: float, bearing_deg: float, distance_m: float) -> Tuple[float, float]:
    """Returns a new point offset from the given point by distance in the given bearing."""
    d = distance_m / 6371000
    brng = math.radians(bearing_deg)
    lat1 = math.radians(lat)
    lng1 = math.radians(lng)
    lat2 = math.asin(math.sin(lat1) * math.cos(d) + math.cos(lat1) * math.sin(d) * math.cos(brng))
    lng2 = lng1 + math.atan2(math.sin(brng) * math.sin(d) * math.cos(lat1), math.cos(d) - math.sin(lat1) * math.sin(lat2))
    return math.degrees(lat2), math.degrees(lng2)


def _smooth_path(coords: List[List[float]], iterations: int = 2) -> List[List[float]]:
    """Chaikin smoothing for natural path rendering."""
    if len(coords) < 3:
        return coords
    result = coords
    for _ in range(iterations):
        smoothed = [result[0]]
        for i in range(len(result) - 1):
            p0, p1 = result[i], result[i + 1]
            q = [0.75 * p0[0] + 0.25 * p1[0], 0.75 * p0[1] + 0.25 * p1[1]]
            r = [0.25 * p0[0] + 0.75 * p1[0], 0.25 * p0[1] + 0.75 * p1[1]]
            smoothed.extend([q, r])
        smoothed.append(result[-1])
        result = smoothed
    return result


def generate_hunting_path(
    zones: List[Dict],
    corridors: List[Dict],
    waypoint_center: Optional[Dict] = None,
    bounds: Optional[Dict] = None,
) -> Dict[str, Any]:
    """
    STEVE-MAX V2: Generate an optimal hunting path.
    P0: Logique vent SUPPRIMEE du pipeline decisionnel.
    Le Wind Intelligence Engine (#4) sera integre separement.

    Algorithm:
    1. Extract zone centroids with priorities
    2. Start from center of analysis area
    3. Use nearest-neighbor heuristic weighted by zone PRIORITY ONLY
    4. Generate waypoints for saline, cache, secondary feeding
    5. Smooth the path for natural rendering

    Returns GeoJSON-compatible hunting path + analysis.
    """
    if not zones:
        return {"path": [], "waypoints": [], "analysis": {"error": "No zones provided"}}

    # 1. Extract zone centroids
    zone_points = []
    for z in zones:
        geom = z.get("geometry", {})
        props = z.get("properties", {})
        layer_id = props.get("layer_id", "unknown")
        priority = ZONE_PRIORITY.get(layer_id, 1)

        coords = geom.get("coordinates", [])
        if not coords:
            continue

        # Compute centroid from polygon
        if geom.get("type") == "Polygon" and coords:
            ring = coords[0] if isinstance(coords[0][0], (list, tuple)) else coords
            if ring:
                avg_lng = sum(c[0] for c in ring) / len(ring)
                avg_lat = sum(c[1] for c in ring) / len(ring)
                zone_points.append({
                    "lat": avg_lat, "lng": avg_lng,
                    "layer_id": layer_id,
                    "priority": priority,
                    "label": props.get("label", layer_id),
                    "score": props.get("score", 50),
                })

    if len(zone_points) < 2:
        return {"path": [], "waypoints": [], "analysis": {"error": "Insufficient zones for path"}}

    # 2. Determine start point (center of analysis area)
    if waypoint_center:
        center_lat = waypoint_center.get("lat", 46.815)
        center_lng = waypoint_center.get("lng", -71.205)
    else:
        center_lat = sum(p["lat"] for p in zone_points) / len(zone_points)
        center_lng = sum(p["lng"] for p in zone_points) / len(zone_points)

    # Start from highest-priority zone closest to center
    zone_points.sort(key=lambda p: -p["priority"] + _haversine_m(center_lat, center_lng, p["lat"], p["lng"]) / 500)
    start_zone = zone_points[0]

    # 3. Nearest-neighbor TSP weighted by priority ONLY (no wind)
    visited = []
    current = {"lat": start_zone["lat"], "lng": start_zone["lng"], "layer_id": "start", "label": "Depart", "priority": 0}
    remaining = list(zone_points)

    visited.append(current)
    while remaining:
        best_score = float("inf")
        best_idx = 0
        for idx, candidate in enumerate(remaining):
            dist = _haversine_m(current["lat"], current["lng"], candidate["lat"], candidate["lng"])
            # Score: distance - priority bonus (pure ecological routing)
            score = dist - candidate["priority"] * 40
            if score < best_score:
                best_score = score
                best_idx = idx

        chosen = remaining.pop(best_idx)
        visited.append(chosen)
        current = chosen

    # 4. Build path coordinates
    raw_path = [[p["lng"], p["lat"]] for p in visited]

    # Smooth the path
    smoothed = _smooth_path(raw_path, iterations=2)

    # Clip to bounds if provided
    if bounds:
        clipped = []
        for coord in smoothed:
            lng = max(bounds.get("west", -180), min(bounds.get("east", 180), coord[0]))
            lat = max(bounds.get("south", -90), min(bounds.get("north", 90), coord[1]))
            clipped.append([round(lng, 6), round(lat, 6)])
        smoothed = clipped

    # 5. Generate strategic waypoints (P0: sans logique vent — ecologique pur)
    waypoints = []

    # Start waypoint
    waypoints.append({
        "type": "start",
        "position": [visited[0]["lng"], visited[0]["lat"]],
        "label": "Depart (zone prioritaire)",
        **WAYPOINT_TYPES["start"],
    })

    # Saline suggestion — near feeding/habitat zones (offset 80m from centroid)
    feeding_zones = [p for p in visited if p["layer_id"] in ("alimentation", "habitats")]
    if feeding_zones:
        sz = feeding_zones[0]
        salt_lat, salt_lng = _offset_point(sz["lat"], sz["lng"], 45, 80)
        waypoints.append({
            "type": "saline",
            "position": [round(salt_lng, 6), round(salt_lat, 6)],
            "label": "Saline suggeree (80m de la zone d'alimentation)",
            **WAYPOINT_TYPES["saline"],
        })

    # Cache suggestion — near rut/repos zones (offset 60m)
    high_activity = [p for p in visited if p["layer_id"] in ("rut", "repos")]
    if high_activity:
        hz = high_activity[0]
        cache_lat, cache_lng = _offset_point(hz["lat"], hz["lng"], 135, 60)
        waypoints.append({
            "type": "cache",
            "position": [round(cache_lng, 6), round(cache_lat, 6)],
            "label": "Cache suggeree (60m de la zone de rut/repos)",
            **WAYPOINT_TYPES["cache"],
        })

    # ALIMENTATION-V2: "alimentation secondaire" SUPPRIME — remplace par ENGINE ALIMENTATION-V2
    # (Directive STEEVE-MAX: seul ALIMENTATION-V2 controle les salines et sites d'alimentation)

    # End waypoint (last zone visited)
    last = visited[-1]
    waypoints.append({
        "type": "end",
        "position": [last["lng"], last["lat"]],
        "label": f"Position finale ({last['layer_id']})",
        **WAYPOINT_TYPES["end"],
    })

    # 6. Calculate path statistics
    total_dist = 0
    for i in range(len(visited) - 1):
        total_dist += _haversine_m(visited[i]["lat"], visited[i]["lng"], visited[i+1]["lat"], visited[i+1]["lng"])

    zone_sequence = [{"layer_id": p["layer_id"], "label": p.get("label", p["layer_id"]), "priority": p["priority"]} for p in visited if p["layer_id"] != "start"]

    # Build analysis report (P0: aucune reference vent dans le pipeline)
    analysis = {
        "total_distance_m": round(total_dist, 0),
        "total_distance_km": round(total_dist / 1000, 2),
        "zones_visited": len(zone_sequence),
        "zone_sequence": zone_sequence,
        "path_points": len(smoothed),
        "start_strategy": f"Depart depuis zone prioritaire ({zone_sequence[0]['layer_id'] if zone_sequence else 'n/a'})",
        "note": "Wind Intelligence Engine (#4) sera integre separement",
        "recommendations": [
            f"Priorite aux zones de {zone_sequence[0]['layer_id'] if zone_sequence else 'n/a'}",
            f"Distance totale estimee: {round(total_dist/1000, 1)} km",
            "Placer la saline 80m de la zone d'alimentation",
            "Installer la cache 60m de la zone de rut/repos",
        ],
    }

    return {
        "path": smoothed,
        "style": PATH_STYLE,
        "waypoints": waypoints,
        "analysis": analysis,
    }



def generate_amenagement_report(
    zones: List[Dict],
    corridors: List[Dict],
    hunting_path: Dict,
    waypoint_center: Optional[Dict] = None,
) -> Dict[str, Any]:
    """
    STEVE-MAX P5: Generate a complete aménagement (setup) report for the 2km square.

    Returns:
    - Saline suggestion
    - Secondary feeding site
    - Cache location
    - Optimal path
    - Wind Intelligence (via Engine #4)
    - Key zones analysis
    - Corridors analysis
    - Action plan
    """
    path_analysis = hunting_path.get("analysis", {})
    path_waypoints = hunting_path.get("waypoints", [])

    # Zone stats
    zone_types = {}
    for z in zones:
        lid = z.get("properties", {}).get("layer_id", "unknown")
        zone_types[lid] = zone_types.get(lid, 0) + 1

    # Corridor stats
    corridor_stats = {
        "total": len(corridors),
        "in_perimeter": sum(1 for c in corridors if c.get("properties", {}).get("in_perimeter")),
        "total_distance_km": round(sum(c.get("properties", {}).get("distance_m", 0) for c in corridors) / 1000, 1),
    }

    # Find strategic waypoints
    saline_wp = next((w for w in path_waypoints if w["type"] == "saline"), None)
    cache_wp = next((w for w in path_waypoints if w["type"] == "cache"), None)
    # ALIMENTATION-V2: alimentation_sec SUPPRIME (directive STEEVE-MAX)

    report = {
        "title": "Rapport d'amenagement BIONIC — Carre 2km",
        "version": "STEVE-MAX V9",
        "sections": {
            "1_saline": {
                "title": "Suggestion de SALINE",
                "position": saline_wp["position"] if saline_wp else None,
                "justification": saline_wp["label"] if saline_wp else "Aucune zone d'alimentation detectee",
                "priority": "HIGH",
            },
            "3_cache": {
                "title": "Suggestion de CACHE",
                "position": cache_wp["position"] if cache_wp else None,
                "justification": cache_wp["label"] if cache_wp else "Aucune zone haute activite detectee",
                "priority": "HIGH",
            },
            "4_trajet_optimal": {
                "title": "Trajet optimal",
                "distance_km": path_analysis.get("total_distance_km", 0),
                "zones_visited": path_analysis.get("zones_visited", 0),
                "strategy": path_analysis.get("start_strategy", ""),
            },
            "5_vents_dominants": {
                "title": "Analyse des vents dominants",
                "status": "En attente Wind Intelligence Engine (#4)",
                "note": "Le moteur vent sera integre via ENGINE #4 — aucune logique vent dans le pipeline actuel",
            },
            "6_zones_cles": {
                "title": "Analyse des zones cles",
                "total_zones": len(zones),
                "types_detectes": zone_types,
                "couverture": "bonne" if len(zone_types) >= 5 else "moyenne" if len(zone_types) >= 3 else "insuffisante",
            },
            "7_corridors": {
                "title": "Analyse des corridors",
                **corridor_stats,
            },
            "8_plan_action": {
                "title": "Plan d'action concret",
                "etapes": path_analysis.get("recommendations", []),
                "score_confiance": min(95, 50 + len(zones) * 3 + corridor_stats["in_perimeter"] * 5),
            },
        },
    }

    return report
