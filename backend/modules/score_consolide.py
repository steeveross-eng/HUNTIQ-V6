"""
Score consolidé BIONIC — Score écologique multi-moteurs
========================================================
Calcule un score consolidé basé sur ALIMENTATION-V1 + REPOS-V1
(+ futurs CORRIDORS-V10, HABITAT-V1, RUT-V1 quand disponibles)

Pondération transparente, traçable, conforme BCE-4X.
"""
from modules.alimentation_v1.engine import analyze_single_point as alim_point
from modules.repos_v1.engine import analyze_single_point as repos_point

# Pondérations par moteur (transparentes, documentées)
# Les futurs moteurs seront ajoutés ici avec weight > 0
ENGINE_WEIGHTS = {
    "alimentation": 0.45,
    "repos": 0.35,
    "corridors_v10": 0.00,  # À ACTIVER quand livré
    "habitat_v1": 0.00,     # À ACTIVER quand livré
    "rut_v1": 0.00,         # À ACTIVER quand livré
    "pression": 0.20,       # Calculé inline
}

# Active weights (normalisé à 1.0)
ACTIVE_WEIGHTS = {k: v for k, v in ENGINE_WEIGHTS.items() if v > 0}
_TOTAL = sum(ACTIVE_WEIGHTS.values())
NORMALIZED_WEIGHTS = {k: v / _TOTAL for k, v in ACTIVE_WEIGHTS.items()}


def compute_consolidated_score(lat: float, lng: float, species: str = "CERF", month: int = 10) -> dict:
    """
    Calcule le score consolidé pour un point.
    Traçabilité complète: chaque composante est documentée.
    """
    alim = alim_point(lat, lng, species, month)
    repos = repos_point(lat, lng, species, month)

    # Score pression (inversé: plus loin = meilleur)
    layers = alim.get("layers", {})
    pert = layers.get("perturbations", {})
    dist_route = pert.get("distance_route_m", 200)
    dist_bat = pert.get("distance_batiment_m", 300)
    pression_score = min(100, (dist_route / 8.0) + (dist_bat / 10.0))

    # Scores individuels
    scores = {
        "alimentation": alim["score_alimentation"],
        "repos": repos["score_repos"],
        "pression": round(pression_score, 1),
    }

    # Score consolidé pondéré
    consolidated = sum(scores[k] * NORMALIZED_WEIGHTS[k] for k in NORMALIZED_WEIGHTS if k in scores)
    consolidated = max(0, min(100, consolidated))

    # Classification
    if consolidated >= 80:
        classe, label, color = "OPTIMAL", "Optimal", "#DC2626"
    elif consolidated >= 60:
        classe, label, color = "BON", "Bon", "#F59E0B"
    elif consolidated >= 40:
        classe, label, color = "MODERE", "Modere", "#22C55E"
    else:
        classe, label, color = "FAIBLE", "Faible", "#3B82F6"

    return {
        "score": round(consolidated, 1),
        "classe": classe,
        "label": label,
        "color": color,
        "species": species.upper(),
        "month": month,
        "components": scores,
        "weights": {k: round(v, 3) for k, v in NORMALIZED_WEIGHTS.items()},
        "tracability": {
            "alimentation_v1": alim["score_alimentation"],
            "repos_v1": repos["score_repos"],
            "pression_calc": round(pression_score, 1),
            "engines_active": list(NORMALIZED_WEIGHTS.keys()),
            "engines_pending": ["corridors_v10", "habitat_v1", "rut_v1"],
        },
    }


def compute_heatmap_grid(
    center_lat: float, center_lng: float,
    species: str = "CERF", month: int = 10,
    grid_size: int = 20,
    side_m: float = 2000.0,
) -> dict:
    """
    Calcule la grille de scores consolidés pour le heatmap.
    grid_size: nombre de points par côté (20 = 400 points, performant)
    """
    import math

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
            result = compute_consolidated_score(lat, lng, species, month)
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
        overall_classe, overall_label = "MODERE", "Modere"
    else:
        overall_classe, overall_label = "FAIBLE", "Faible"

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
        "weights": {k: round(v, 3) for k, v in NORMALIZED_WEIGHTS.items()},
        "points": points,
    }
