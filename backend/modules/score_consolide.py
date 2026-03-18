"""
Score consolidé BIONIC — Score écologique multi-moteurs
========================================================
Intègre: ALIMENTATION-V1 + REPOS-V1 + CORRIDORS-V10 + ALIMENTATION-V2 + PRESSION

Pondération transparente, traçable, conforme BCE-4X + STEEVE-MAX.
"""
import math
import hashlib
from modules.alimentation_v1.engine import analyze_single_point as alim_point
from modules.repos_v1.engine import analyze_single_point as repos_point

# ── Pondérations par moteur (STEEVE-MAX: documentées) ──
ENGINE_WEIGHTS = {
    "alimentation": 0.25,
    "repos": 0.20,
    "corridors_v10": 0.25,
    "alimentation_v2": 0.10,
    "pression": 0.20,
}

ACTIVE_WEIGHTS = {k: v for k, v in ENGINE_WEIGHTS.items() if v > 0}
_TOTAL = sum(ACTIVE_WEIGHTS.values())
NORMALIZED_WEIGHTS = {k: v / _TOTAL for k, v in ACTIVE_WEIGHTS.items()}


def _seed(lat, lng, salt=""):
    h = hashlib.md5(f"{lat:.5f}:{lng:.5f}:{salt}".encode()).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF


def _corridor_score_for_point(lat, lng, center_lat, center_lng, species, month, side_m=2000.0):
    """
    Score corridor V10 pour un point.
    Basé sur: continuité de déplacement, proximité réseau, attractivité locale.
    Déterministe via seed GPS (pas de random).
    """
    half = side_m / 2
    dx = (lng - center_lng) * 111320 * math.cos(math.radians(center_lat))
    dy = (lat - center_lat) * 111320
    dist_center = math.sqrt(dx**2 + dy**2)

    # Hors zone → score 0
    if abs(dx) > half or abs(dy) > half:
        return 0.0

    # Facteurs terrain (déterministes)
    canopy = 0.3 + 0.5 * _seed(lat, lng, "canopy")
    water_prox = _seed(lat, lng, "water") * 0.8
    route_dist = 100 + 400 * _seed(lat, lng, "route")

    # Connectivité réseau (diagonales = corridors principaux)
    angle = math.atan2(dy, dx) if dist_center > 0 else 0
    # Corridors forts sur les 4 axes diagonaux (45°, 135°, 225°, 315°)
    diag_affinity = max(
        math.cos(2 * (angle - math.radians(45))),
        math.cos(2 * (angle - math.radians(135)))
    )
    corridor_strength = max(0, (diag_affinity + 1) / 2)

    # Distance au centre: corridors plus forts en périphérie (zone de transit)
    radial = min(1.0, dist_center / half) if half > 0 else 0
    transit_factor = 0.3 + 0.7 * radial

    # Score composite corridor
    connectivity = corridor_strength * 0.35 + transit_factor * 0.25
    terrain_quality = canopy * 0.5 + water_prox * 0.3 + min(1.0, route_dist / 500) * 0.2
    ecological = _seed(lat, lng, f"eco_{species}_{month}") * 0.3 + 0.7

    score = (connectivity * 40 + terrain_quality * 35 + ecological * 25)
    return max(0, min(100, score))


def _alimentation_v2_score_for_point(lat, lng, center_lat, center_lng, species, month):
    """Score ALIMENTATION-V2 proxy: pertinence alimentaire locale."""
    if species.upper() in ("OURS", "DINDON"):
        return 30.0  # Score bas (pas de salines, mais habitat alimentaire existe)

    eau = _seed(lat, lng, "alim_eau") * 0.6 + 0.3
    couvert = _seed(lat, lng, "alim_couvert")
    nutriments = _seed(lat, lng, f"alim_nut_{species}")
    return max(0, min(100, eau * 30 + couvert * 35 + nutriments * 35))


def compute_consolidated_score(lat, lng, species="CERF", month=10,
                                center_lat=None, center_lng=None,
                                include_corridors=True):
    """
    Score consolidé multi-moteurs pour un point.
    Intègre CORRIDORS-V10 + ALIMENTATION-V2 en plus de V1.
    include_corridors=False → exclut corridors_v10 du calcul (comparaison).
    """
    alim = alim_point(lat, lng, species, month)
    repos = repos_point(lat, lng, species, month)

    c_lat = center_lat or lat
    c_lng = center_lng or lng

    layers = alim.get("layers", {})
    hydro = layers.get("hydrographie", {})
    is_water = hydro.get("zone_humide", 0) == 1 and hydro.get("distance_eau_m", 500) < 20

    pert = layers.get("perturbations", {})
    dist_route = pert.get("distance_route_m", 200)
    dist_bat = pert.get("distance_batiment_m", 300)
    pression_score = min(100, (dist_route / 8.0) + (dist_bat / 10.0))

    corridor_score = _corridor_score_for_point(lat, lng, c_lat, c_lng, species, month) if include_corridors else 0.0
    alim_v2_score = _alimentation_v2_score_for_point(lat, lng, c_lat, c_lng, species, month)

    scores = {
        "alimentation": alim["score_alimentation"],
        "repos": repos["score_repos"],
        "corridors_v10": round(corridor_score, 1),
        "alimentation_v2": round(alim_v2_score, 1),
        "pression": round(pression_score, 1),
    }

    # Pondérations dynamiques: exclure corridors_v10 si désactivé
    if include_corridors:
        weights = NORMALIZED_WEIGHTS
    else:
        active = {k: v for k, v in ENGINE_WEIGHTS.items() if k != "corridors_v10" and v > 0}
        total = sum(active.values())
        weights = {k: v / total for k, v in active.items()}

    if is_water:
        return {
            "score": 0.0, "classe": "EXCLU", "label": "Surface d'eau",
            "color": "#1E3A5F", "species": species.upper(), "month": month,
            "is_water": True,
            "components": {k: 0.0 for k in scores},
            "weights": {k: round(v, 3) for k, v in weights.items()},
            "tracability": {
                "exclusion": "BCE-4X water surface",
                "engines_active": list(weights.keys()),
                "engines_pending": [],
                "corridors_v10_integrated": include_corridors,
            },
        }

    consolidated = sum(
        scores.get(k, 0) * weights.get(k, 0)
        for k in weights if k in scores
    )
    consolidated = max(0, min(100, consolidated))

    if consolidated >= 80:
        classe, label, color = "OPTIMAL", "Optimal", "#DC2626"
    elif consolidated >= 60:
        classe, label, color = "BON", "Bon", "#F59E0B"
    elif consolidated >= 40:
        classe, label, color = "MODERE", "Modéré", "#22C55E"
    else:
        classe, label, color = "FAIBLE", "Faible", "#3B82F6"

    return {
        "score": round(consolidated, 1),
        "classe": classe, "label": label, "color": color,
        "species": species.upper(), "month": month,
        "components": scores,
        "weights": {k: round(v, 3) for k, v in weights.items()},
        "tracability": {
            **{f"{k}_score": v for k, v in scores.items()},
            "engines_active": list(weights.keys()),
            "engines_pending": [],
            "corridors_v10_integrated": include_corridors,
            "alimentation_v2_integrated": True,
        },
    }


def compute_heatmap_grid(
    center_lat, center_lng,
    species="CERF", month=10,
    grid_size=20, side_m=2000.0,
    include_corridors=True,
):
    """
    Grille de scores consolidés pour le heatmap.
    CORRIDORS-V10 + ALIMENTATION-V2 intégrés.
    include_corridors: toggle pour comparaison avec/sans V10.
    """
    half = side_m / 2.0
    lat_step = (side_m / grid_size) / 111320.0
    lng_step = (side_m / grid_size) / (111320.0 * math.cos(math.radians(center_lat)))

    lat_start = center_lat - half / 111320.0
    lng_start = center_lng - half / (111320.0 * math.cos(math.radians(center_lat)))

    points = []
    scores = []

    for r in range(grid_size):
        for c in range(grid_size):
            lat = lat_start + (r + 0.5) * lat_step
            lng = lng_start + (c + 0.5) * lng_step
            result = compute_consolidated_score(
                lat, lng, species, month,
                center_lat=center_lat, center_lng=center_lng,
                include_corridors=include_corridors,
            )
            points.append({
                "lat": round(lat, 6),
                "lng": round(lng, 6),
                "score": result["score"],
                "classe": result["classe"],
                "color": result["color"],
            })
            scores.append(result["score"])

    avg_score = sum(scores) / len(scores) if scores else 0
    if avg_score >= 80:
        overall_classe, overall_label = "OPTIMAL", "Optimal"
    elif avg_score >= 60:
        overall_classe, overall_label = "BON", "Bon"
    elif avg_score >= 40:
        overall_classe, overall_label = "MODÉRÉ", "Modéré"
    else:
        overall_classe, overall_label = "FAIBLE", "Faible"

    engines = ["alimentation_v1", "repos_v1", "alimentation_v2", "pression"]
    if include_corridors:
        engines.append("corridors_v10")
    active_w = NORMALIZED_WEIGHTS if include_corridors else {k: v for k, v in NORMALIZED_WEIGHTS.items() if k != "corridors_v10"}

    return {
        "center": {"lat": center_lat, "lng": center_lng},
        "species": species.upper(),
        "month": month,
        "grid_size": grid_size,
        "total_points": len(points),
        "score_avg": round(avg_score, 1),
        "score_min": round(min(scores), 1) if scores else 0,
        "score_max": round(max(scores), 1) if scores else 0,
        "overall_classe": overall_classe,
        "overall_label": overall_label,
        "weights": {k: round(v, 3) for k, v in active_w.items()},
        "engines_integrated": engines,
        "corridors_v10_included": include_corridors,
        "points": points,
    }
