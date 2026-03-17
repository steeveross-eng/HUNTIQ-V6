"""
CORRIDORS-V10 — Scoring des corridors (Norme CORRIDOR-V1/V10)
================================================================
Score reseau global SCORE_CORRIDOR (0-100).
Score individuel par corridor pour classification normative.

Facteurs du score:
  - pente + micro-topographie
  - structure forestiere (essences, densite, age, mosaiques)
  - hydrologie (ruisseaux, zones humides, suintements)
  - pression humaine (routes, sentiers, perturbations)
  - connectivite ecologique (ECL)
  - nourriture disponible
  - refuge
  - distance aux perturbations
  - zones tampons
  - regeneration

Normalisation obligatoire: 0-100.
"""
from .classifier import classify, classify_corridor


def _clamp(val: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, val))


def score_single_corridor(corridor: dict, cell_data: list) -> float:
    """
    Score individuel d'un corridor (0-100).
    Distribution reelle sur 5 niveaux normatifs.
    """
    path = corridor.get("path", [])
    if not path:
        return 0.0

    n = len(path)

    # Metriques le long du chemin
    total_canopy = 0.0
    total_ecl = 0.0
    total_nourriture = 0.0
    total_refuge = 0.0
    total_dist_route = 0.0
    vallon_count = 0
    tampon_count = 0
    regen_total = 0.0
    hydro_near = 0

    for pt in path:
        r, c = pt["row"], pt["col"]
        cell = cell_data[r][c]
        total_canopy += cell.get("canopy_density", 0)
        total_ecl += cell.get("ecl", 0)
        total_nourriture += cell.get("nourriture", 0)
        total_refuge += cell.get("refuge_score", 0)
        total_dist_route += min(cell.get("distance_route_m", 0), 500)
        if cell.get("micro_topo_vallon"):
            vallon_count += 1
        if cell.get("zone_tampon"):
            tampon_count += 1
        regen_total += cell.get("regeneration", 0)
        if cell.get("distance_eau_m", 500) < 150:
            hydro_near += 1

    avg_canopy = total_canopy / n
    avg_ecl = total_ecl / n
    avg_nourriture = total_nourriture / n
    avg_refuge = total_refuge / n
    avg_dist_route = total_dist_route / n
    pct_vallon = vallon_count / n
    avg_regen = regen_total / n
    pct_hydro = hydro_near / n

    # === Score base (0-100) avec forte variance ===
    score = 0.0

    # 1. ECL (0-25) — facteur dominant avec seuils stricts
    if avg_ecl >= 0.7:
        score += 25
    elif avg_ecl >= 0.5:
        score += 15 + (avg_ecl - 0.5) * 50
    elif avg_ecl >= 0.3:
        score += 5 + (avg_ecl - 0.3) * 50
    else:
        score += avg_ecl * 17

    # 2. Structure forestiere (0-20) — seuils progressifs
    if avg_canopy >= 0.7:
        score += 20
    elif avg_canopy >= 0.4:
        score += 8 + (avg_canopy - 0.4) * 40
    else:
        score += avg_canopy * 20

    # 3. Pression humaine (0-15) — tres penalisant si proche
    if avg_dist_route >= 400:
        score += 15
    elif avg_dist_route >= 200:
        score += 8 + (avg_dist_route - 200) / 200 * 7
    elif avg_dist_route >= 80:
        score += (avg_dist_route - 80) / 120 * 8
    else:
        score += 0

    # 4. Nourriture + refuge (0-15)
    score += min(15, (avg_nourriture + avg_refuge) * 10)

    # 5. Micro-topographie + hydro (0-10)
    topo_hydro = pct_vallon * 0.5 + pct_hydro * 0.3 + float(tampon_count > 0) * 0.2
    score += min(10, topo_hydro * 15)

    # 6. Regeneration (0-5)
    score += min(5, avg_regen * 7)

    # 7. Cout de traversee (0-10) — discriminant fort
    cost = corridor.get("cost", 0)
    cost_per_cell = cost / max(n, 1)
    if cost_per_cell <= 0.3:
        score += 10
    elif cost_per_cell <= 0.8:
        score += 6 + (0.8 - cost_per_cell) * 8
    elif cost_per_cell <= 1.5:
        score += 2 + (1.5 - cost_per_cell) / 0.7 * 4
    else:
        score += max(0, 2 - cost_per_cell * 0.3)

    # === Modificateurs ===
    # Bonus: connecte types de zones differents
    from_type = corridor.get("from_zone", {}).get("type", "")
    to_type = corridor.get("to_zone", {}).get("type", "")
    if from_type != to_type:
        score *= 1.05  # +5% pour diversite
    # Bonus: corridor court = goulot critique
    if n < 8:
        score *= 1.10  # +10% corridors courts critiques
    elif n > 40:
        score *= 0.85  # -15% corridors tres longs
    # Penalite: connexion forcee
    if corridor.get("forced_connection"):
        score *= 0.60
    if corridor.get("dead_end_fix"):
        score *= 0.70

    return round(_clamp(score, 0, 100), 1)


def score_path_quality(corridors: list, cell_m: float) -> dict:
    """Qualite des chemins (0-30)."""
    if not corridors:
        return {"score": 0, "avg_cost": 0, "avg_length": 0}

    total_cost = sum(c["cost"] for c in corridors)
    total_length = sum(c["length_cells"] for c in corridors)
    avg_cost = total_cost / len(corridors)
    avg_length = total_length / len(corridors)

    cost_per_cell = avg_cost / max(avg_length, 1)
    if cost_per_cell <= 2:
        cost_score = 1.0
    elif cost_per_cell <= 5:
        cost_score = 1.0 - (cost_per_cell - 2) / 6
    else:
        cost_score = max(0, 0.5 - (cost_per_cell - 5) / 20)

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
    """Diversite des zones connectees (0-25)."""
    zone_types = {"alimentation", "repos", "rut", "eau"}
    present_types = set(z["type"] for z in zones)
    coverage = len(present_types & zone_types) / len(zone_types)

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
    """Continuite du reseau (0-30). CRITIQUE — COR-006."""
    base = 30.0

    if not continuity.get("connected", False):
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
    """Conformite au profil espece (0-15)."""
    checks_passed = 0
    total_checks = 5

    if network_stats.get("total_corridors", 0) >= 3:
        checks_passed += 1

    zone_types = network_stats.get("zone_types", {})
    if sum(1 for v in zone_types.values() if v > 0) >= 3:
        checks_passed += 1

    if network_stats.get("total_path_cells", 0) > 0:
        checks_passed += 1

    if network_stats.get("total_zones", 0) >= 4:
        checks_passed += 1

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
    Score composite reseau SCORE_CORRIDOR (0-100):
      QUALITE (30) + DIVERSITE (25) + CONTINUITE (30) + CONFORMITE (15)
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


def compute_corridor_levels(corridors: list, cell_data: list) -> list:
    """
    Attribue un score et un niveau normatif a chaque corridor.
    Retourne la liste des corridors enrichis avec niveau/couleur/largeur.
    """
    enriched = []
    for c in corridors:
        score = score_single_corridor(c, cell_data)
        level = classify_corridor(score)
        enriched.append({
            **c,
            "score_individuel": score,
            "niveau": level["niveau"],
            "niveau_label": level["label_fr"],
            "color": level["color"],
            "pattern": level["pattern"],
            "largeur_m": level["largeur_m"],
            "render_weight": level["render_weight"],
            "dash_array": level["dash_array"],
        })
    return enriched
