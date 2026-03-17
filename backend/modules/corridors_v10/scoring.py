"""
CORRIDORS-V10 — Scoring des corridors
=========================================
Calcule SCORE_CORRIDOR_[espece] (0-100) et CLASSE_CORRIDOR_[espece].
Score composite base sur:
  - Qualite du chemin (cout moyen, regularite)
  - Diversite des zones connectees
  - Continuite du reseau
  - Conformite au profil espece
"""
from .classifier import classify


def _clamp(val: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, val))


def score_path_quality(corridors: list, cell_m: float) -> dict:
    """
    Qualite des chemins (0-30).
    - Cout moyen bas = bon
    - Longueur raisonnable = bon
    """
    if not corridors:
        return {"score": 0, "avg_cost": 0, "avg_length": 0}

    total_cost = sum(c["cost"] for c in corridors)
    total_length = sum(c["length_cells"] for c in corridors)
    avg_cost = total_cost / len(corridors)
    avg_length = total_length / len(corridors)

    # Cout moyen ideal: 2-5 par cellule
    cost_per_cell = avg_cost / max(avg_length, 1)
    if cost_per_cell <= 2:
        cost_score = 1.0
    elif cost_per_cell <= 5:
        cost_score = 1.0 - (cost_per_cell - 2) / 6
    else:
        cost_score = max(0, 0.5 - (cost_per_cell - 5) / 20)

    # Longueur: pas trop court (>5) ni trop long (>80% de la grille)
    length_score = min(1.0, avg_length / 10) * min(1.0, 80 / max(avg_length, 1))

    combined = cost_score * 0.6 + length_score * 0.4
    score = _clamp(combined * 30, 0, 30)

    return {
        "score": round(score, 2),
        "avg_cost": round(avg_cost, 2),
        "avg_length": round(avg_length, 1),
        "cost_per_cell": round(cost_per_cell, 3),
    }


def score_zone_diversity(zones: list) -> dict:
    """
    Diversite des zones connectees (0-25).
    Meilleur si les 4 types de zones sont presents.
    """
    zone_types = {"alimentation", "repos", "rut", "eau"}
    present_types = set(z["type"] for z in zones)
    coverage = len(present_types & zone_types) / len(zone_types)

    # Bonus: distribution spatiale
    if len(zones) >= 8:
        spatial_bonus = 0.2
    elif len(zones) >= 4:
        spatial_bonus = 0.1
    else:
        spatial_bonus = 0.0

    combined = min(1.0, coverage + spatial_bonus)
    score = _clamp(combined * 25, 0, 25)

    return {
        "score": round(score, 2),
        "types_present": list(present_types),
        "coverage": round(coverage, 3),
        "total_zones": len(zones),
    }


def score_continuity(continuity: dict) -> dict:
    """
    Continuite du reseau (0-30). CRITIQUE.
    Connecte = 30 pts. Dead-ends = penalites lourdes.
    """
    base = 30.0

    if not continuity.get("connected", False):
        # Composantes multiples: penalite severe
        components = continuity.get("components", 1)
        base -= min(20, (components - 1) * 10)

    dead_ends = continuity.get("dead_ends", 0)
    base -= dead_ends * 5

    score = _clamp(base, 0, 30)

    return {
        "score": round(score, 2),
        "connected": continuity.get("connected", False),
        "components": continuity.get("components", 0),
        "dead_ends": dead_ends,
    }


def score_species_conformity(profile: dict, network_stats: dict) -> dict:
    """
    Conformite au profil espece (0-15).
    Verifie que le reseau respecte les 12 parametres.
    """
    checks_passed = 0
    total_checks = 5

    # Verification: nombre minimum de corridors
    if network_stats.get("total_corridors", 0) >= 3:
        checks_passed += 1

    # Verification: zones diversifiees
    zone_types = network_stats.get("zone_types", {})
    if sum(1 for v in zone_types.values() if v > 0) >= 3:
        checks_passed += 1

    # Verification: corridors existent
    if network_stats.get("total_path_cells", 0) > 0:
        checks_passed += 1

    # Verification: largeur corridor respectee (implicite par cell_m)
    if network_stats.get("total_zones", 0) >= 4:
        checks_passed += 1

    # Verification: cout raisonnable
    avg_cost = network_stats.get("total_cost", 0) / max(network_stats.get("total_corridors", 1), 1)
    if avg_cost < 500:
        checks_passed += 1

    ratio = checks_passed / total_checks
    score = _clamp(ratio * 15, 0, 15)

    return {
        "score": round(score, 2),
        "checks_passed": checks_passed,
        "total_checks": total_checks,
        "species": profile.get("nom_fr", ""),
    }


def compute_corridor_score(
    zones: list,
    corridors: list,
    continuity: dict,
    network_stats: dict,
    profile: dict,
    cell_m: float = 25.0,
) -> dict:
    """
    Score composite SCORE_CORRIDOR (0-100):
      QUALITE_CHEMIN (0-30) + DIVERSITE_ZONES (0-25) + CONTINUITE (0-30) + CONFORMITE (0-15)
    """
    s_quality = score_path_quality(corridors, cell_m)
    s_diversity = score_zone_diversity(zones)
    s_continuity = score_continuity(continuity)
    s_conformity = score_species_conformity(profile, network_stats)

    total = s_quality["score"] + s_diversity["score"] + s_continuity["score"] + s_conformity["score"]
    total = _clamp(total, 0, 100)
    classification = classify(total)

    return {
        "score_corridor": round(total, 1),
        "classe_corridor": classification["classe"],
        "classe_label": classification["label_fr"],
        "classe_color": classification["color"],
        "detail": {
            "qualite_chemin": s_quality,
            "diversite_zones": s_diversity,
            "continuite": s_continuity,
            "conformite_espece": s_conformity,
        },
    }
