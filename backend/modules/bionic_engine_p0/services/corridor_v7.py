"""
BIONIC V7 — Corridor Generator V7 (A* Terrain-Aware)
Generation de trajets de chasse scientifiquement coherents.

Architecture:
  1. Construction grille de couts (trail_cost_grid_v7)
  2. Pathfinding A* sur la grille
  3. Lissage Chaikin du chemin
  4. Scoring multi-criteres du trajet
  5. Evaluation confiance (reel vs IA)
  6. Differentiation male/femelle

Types de trajets:
  - real_male: continu, bleu profond — terrain-aware, donnees solides
  - real_female: continu, rouge profond — terrain-aware, donnees solides
  - ia_male: pointille, bleu clair — estime IA, donnees partielles
  - ia_female: pointille, rouge clair — estime IA, donnees partielles

100% independant. Consomme par pipeline_v7.
"""

import math
import heapq
import logging
import time
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime, timezone

from .species_behavior_v7 import (
    get_sex_params,
    get_season_modifier,
    SEX_PARAMS,
)
from .trail_cost_grid_v7 import build_cost_grid, IMPASSABLE

logger = logging.getLogger("bionic_engine.corridor_v7")

METERS_PER_DEG_LAT = 111320.0

# =====================================================================
# STYLES VISUELS
# =====================================================================

CORRIDOR_STYLES = {
    "male_real": {
        "color": "#1565C0", "width": 3.0, "opacity": 0.85,
        "dasharray": "none", "label": "Trajet male (terrain)",
    },
    "male_ai": {
        "color": "#42A5F5", "width": 2.5, "opacity": 0.65,
        "dasharray": "12 6", "label": "Trajet male (estime IA)",
    },
    "female_real": {
        "color": "#C62828", "width": 2.5, "opacity": 0.80,
        "dasharray": "none", "label": "Trajet femelle (terrain)",
    },
    "female_ai": {
        "color": "#EF5350", "width": 2.0, "opacity": 0.60,
        "dasharray": "8 4", "label": "Trajet femelle (estime IA)",
    },
    "mixed_real": {
        "color": "#F57F17", "width": 2.0, "opacity": 0.70,
        "dasharray": "none", "label": "Trajet mixte (terrain)",
    },
    "mixed_ai": {
        "color": "#FFB74D", "width": 1.5, "opacity": 0.55,
        "dasharray": "10 5", "label": "Trajet mixte (estime IA)",
    },
}

# Paires complementaires a connecter
COMPLEMENTARY_PAIRS = frozenset({
    ("rest", "feed"), ("feed", "rest"),
    ("rest", "rut"), ("rut", "rest"),
    ("rest", "heat_ref"), ("heat_ref", "rest"),
    ("rest", "hunt_ref"), ("hunt_ref", "rest"),
    ("feed", "heat_ref"), ("heat_ref", "feed"),
    ("feed", "corridor"), ("corridor", "feed"),
    ("rest", "corridor"), ("corridor", "rest"),
    ("rut", "feed"), ("feed", "rut"),
    ("hunt_ref", "feed"), ("feed", "hunt_ref"),
})


# =====================================================================
# A* PATHFINDER
# =====================================================================

def _find_nearest_passable_cell(
    grid: np.ndarray,
    cell: Tuple[int, int],
    max_radius: int = 5,
) -> Optional[Tuple[int, int]]:
    """
    C4 (BUG-02): Si la cellule est impassable, cherche la cellule passable
    la plus proche dans un rayon de max_radius cellules.
    """
    r, c = cell
    rows, cols = grid.shape
    if grid[r, c] < IMPASSABLE * 0.9:
        return cell
    for radius in range(1, max_radius + 1):
        best = None
        best_cost = IMPASSABLE
        for dr in range(-radius, radius + 1):
            for dc in range(-radius, radius + 1):
                if abs(dr) != radius and abs(dc) != radius:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    cost = grid[nr, nc]
                    if cost < IMPASSABLE * 0.9 and cost < best_cost:
                        best = (nr, nc)
                        best_cost = cost
        if best is not None:
            logger.info(f"[C4] Cell ({r},{c}) impassable -> nearest passable ({best[0]},{best[1]}) at radius {radius}")
            return best
    return None


def _astar(
    grid: np.ndarray,
    start: Tuple[int, int],
    end: Tuple[int, int],
    max_iterations: int = 8000,
) -> Optional[List[Tuple[int, int]]]:
    """
    A* pathfinding sur la grille de couts.
    8-connectivity (diagonales autorisees).
    """
    rows, cols = grid.shape
    sr, sc = start
    er, ec = end

    # C4 (BUG-02): Snap impassable centroids to nearest passable cell
    passable_start = _find_nearest_passable_cell(grid, (sr, sc))
    passable_end = _find_nearest_passable_cell(grid, (er, ec))
    if passable_start is None or passable_end is None:
        return None
    sr, sc = passable_start
    er, ec = passable_end

    open_set = [(0.0, sr, sc)]
    g_score = np.full((rows, cols), np.inf)
    g_score[sr, sc] = 0.0
    came_from = {}
    closed = np.zeros((rows, cols), dtype=bool)

    # Heuristique: distance euclidienne * cout minimal
    def heuristic(r, c):
        return math.sqrt((r - er) ** 2 + (c - ec) ** 2) * 0.1

    neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    diag_cost = 1.414

    iterations = 0
    while open_set and iterations < max_iterations:
        iterations += 1
        f, cr, cc = heapq.heappop(open_set)

        if cr == er and cc == ec:
            # Reconstruct path
            path = [(er, ec)]
            cur = (er, ec)
            while cur in came_from:
                cur = came_from[cur]
                path.append(cur)
            path.reverse()
            return path

        if closed[cr, cc]:
            continue
        closed[cr, cc] = True

        for dr, dc in neighbors:
            nr, nc = cr + dr, cc + dc
            if not (0 <= nr < rows and 0 <= nc < cols):
                continue
            if closed[nr, nc]:
                continue

            cell_cost = grid[nr, nc]
            if cell_cost >= IMPASSABLE * 0.9:
                continue

            move_cost = cell_cost * (diag_cost if (dr != 0 and dc != 0) else 1.0)
            new_g = g_score[cr, cc] + move_cost

            if new_g < g_score[nr, nc]:
                g_score[nr, nc] = new_g
                came_from[(nr, nc)] = (cr, cc)
                f_val = new_g + heuristic(nr, nc)
                heapq.heappush(open_set, (f_val, nr, nc))

    # No path found — return straight line fallback
    return None


def _grid_path_to_latlon(
    path: List[Tuple[int, int]],
    bounds: Dict[str, float],
    rows: int,
    cols: int,
) -> List[List[float]]:
    """Convertit un chemin grille (row, col) en coordonnees [lng, lat]."""
    lat_span = bounds["north"] - bounds["south"]
    lng_span = bounds["east"] - bounds["west"]
    coords = []
    for r, c in path:
        lat = bounds["north"] - (r / max(1, rows - 1)) * lat_span
        lng = bounds["west"] + (c / max(1, cols - 1)) * lng_span
        coords.append([lng, lat])
    return coords


def _simplify_path(coords: List[List[float]], tolerance: float = 0.0002) -> List[List[float]]:
    """Simplifie le chemin (Douglas-Peucker simplifie)."""
    if len(coords) <= 3:
        return coords

    result = [coords[0]]
    for i in range(1, len(coords) - 1):
        prev = result[-1]
        dist = math.sqrt((coords[i][0] - prev[0]) ** 2 + (coords[i][1] - prev[1]) ** 2)
        if dist >= tolerance:
            result.append(coords[i])
    result.append(coords[-1])
    return result


def _chaikin_smooth(coords: List[List[float]], iterations: int = 3) -> List[List[float]]:
    """Lissage Chaikin du chemin."""
    points = coords
    for _ in range(iterations):
        if len(points) < 3:
            break
        new_pts = [points[0]]
        for i in range(len(points) - 1):
            p0, p1 = points[i], points[i + 1]
            q = [0.75 * p0[0] + 0.25 * p1[0], 0.75 * p0[1] + 0.25 * p1[1]]
            r = [0.25 * p0[0] + 0.75 * p1[0], 0.25 * p0[1] + 0.75 * p1[1]]
            new_pts.extend([q, r])
        new_pts.append(points[-1])
        points = new_pts
    return points


# =====================================================================
# TRAIL SCORING
# =====================================================================

def _score_trail(
    path_latlon: List[List[float]],
    grid: np.ndarray,
    grid_path: List[Tuple[int, int]],
    bounds: Dict[str, float],
    exclusions: List[Dict],
    sex: str,
    species: str,
    terrain_signals: Dict,
) -> Dict[str, Any]:
    """
    Score multi-criteres du trajet.
    Sous-scores: topographie, couvert, eau, pression, comportement.
    """
    if not grid_path:
        # Fallback scoring for AI paths (no grid data)
        return _score_trail_fallback(path_latlon, exclusions, sex, species, terrain_signals)

    rows, cols = grid.shape
    costs = [grid[r, c] for r, c in grid_path if 0 <= r < rows and 0 <= c < cols]
    avg_cost = np.mean(costs) if costs else 5.0
    max_cost = np.max(costs) if costs else 10.0

    # Distance totale
    total_dist_m = 0.0
    for i in range(1, len(path_latlon)):
        dlat = (path_latlon[i][1] - path_latlon[i - 1][1]) * METERS_PER_DEG_LAT
        cos = math.cos(math.radians(path_latlon[i][1]))
        dlng = (path_latlon[i][0] - path_latlon[i - 1][0]) * METERS_PER_DEG_LAT * cos
        total_dist_m += math.sqrt(dlat * dlat + dlng * dlng)
    if total_dist_m < 1:
        total_dist_m = 100.0

    # --- TOPOGRAPHIE ---
    # Score adapte au modele ecologique V7.1:
    # Les chemins a faible cout traversent lisieres, vallees, corridors eau
    if avg_cost < 0.5:
        topo_score = 95
    elif avg_cost < 1.0:
        topo_score = 90 - (avg_cost - 0.5) * 20
    elif avg_cost < 2.5:
        topo_score = 80 - (avg_cost - 1.0) * 16
    elif avg_cost < 5.0:
        topo_score = 56 - (avg_cost - 2.5) * 10
    else:
        topo_score = max(0, 31 - (avg_cost - 5.0) * 4)
    topo_score = max(0, min(100, topo_score))

    # --- COUVERT ---
    forest_proxy = terrain_signals.get("forest_proxy", 0.5)
    cover_score = min(100, forest_proxy * 100 + 20)

    # --- EAU ---
    nearest_water = terrain_signals.get("nearest_m", {}).get("water", 1000)
    if nearest_water is None:
        nearest_water = 1000
    if nearest_water < 50:
        water_score = 60
    elif nearest_water < 200:
        water_score = 90
    elif nearest_water < 500:
        water_score = 70
    else:
        water_score = 40

    # --- PRESSION ---
    nearest_road = terrain_signals.get("nearest_m", {}).get("roads", 500)
    nearest_urban = terrain_signals.get("nearest_m", {}).get("urban", 1000)
    if nearest_road is None:
        nearest_road = 500
    if nearest_urban is None:
        nearest_urban = 1000
    pression_score = min(100, 20 + min(nearest_road, 500) / 10 + min(nearest_urban, 1000) / 20)

    # --- COMPORTEMENT ---
    params = get_sex_params(species, sex)
    behav_score = 60.0
    if total_dist_m < params["daily_range_km"] * 1000:
        behav_score += 20
    if max_cost < 5:
        behav_score += 10
    if forest_proxy > 0.5 and sex == "female":
        behav_score += 10
    behav_score = min(100, behav_score)

    # Score global
    score_global = (
        topo_score * 0.25 +
        cover_score * 0.20 +
        water_score * 0.15 +
        pression_score * 0.25 +
        behav_score * 0.15
    )

    # Justification (facteurs dominants)
    justification = []
    if topo_score > 70:
        justification.append("terrain favorable")
    if cover_score > 70:
        justification.append("bon couvert forestier")
    if water_score > 70:
        justification.append("proximite eau optimale")
    if pression_score > 70:
        justification.append("faible pression humaine")
    if behav_score > 70:
        justification.append(f"distance coherente {sex}")

    return {
        "score": round(score_global, 1),
        "subscores": {
            "topographie": round(topo_score, 1),
            "couvert": round(cover_score, 1),
            "eau": round(water_score, 1),
            "pression": round(pression_score, 1),
            "comportement": round(behav_score, 1),
        },
        "distance_m": round(total_dist_m, 0),
        "avg_cost": round(avg_cost, 3),
        "justification": justification,
    }


def _score_trail_fallback(
    path_latlon: List[List[float]],
    exclusions: List[Dict],
    sex: str,
    species: str,
    terrain_signals: Dict,
) -> Dict[str, Any]:
    """Scoring pour les trajets IA (pas de grille A*)."""
    total_dist_m = 0.0
    for i in range(1, len(path_latlon)):
        dlat = (path_latlon[i][1] - path_latlon[i - 1][1]) * METERS_PER_DEG_LAT
        cos = math.cos(math.radians(path_latlon[i][1]))
        dlng = (path_latlon[i][0] - path_latlon[i - 1][0]) * METERS_PER_DEG_LAT * cos
        total_dist_m += math.sqrt(dlat * dlat + dlng * dlng)
    if total_dist_m < 1:
        total_dist_m = 100.0

    forest_proxy = terrain_signals.get("forest_proxy", 0.5)
    dist_road = terrain_signals.get("nearest_m", {}).get("roads", 500)
    dist_urban = terrain_signals.get("nearest_m", {}).get("urban", 1000)
    dist_water = terrain_signals.get("nearest_m", {}).get("water", 1000)
    if dist_road is None:
        dist_road = 500
    if dist_urban is None:
        dist_urban = 1000
    if dist_water is None:
        dist_water = 1000

    topo_score = 45.0
    cover_score = min(100, forest_proxy * 80 + 20)
    water_score = 60.0 if dist_water < 500 else 35.0
    pression_score = min(100, 20 + min(dist_road, 500) / 10 + min(dist_urban, 1000) / 20)
    behav_score = 55.0
    params = get_sex_params(species, sex)
    if total_dist_m < params["daily_range_km"] * 1000:
        behav_score += 15

    score_global = (topo_score * 0.25 + cover_score * 0.20 + water_score * 0.15 +
                    pression_score * 0.25 + behav_score * 0.15)

    justification = ["trajet estime (IA)"]
    if pression_score > 60:
        justification.append("faible pression humaine")

    return {
        "score": round(score_global, 1),
        "subscores": {
            "topographie": round(topo_score, 1),
            "couvert": round(cover_score, 1),
            "eau": round(water_score, 1),
            "pression": round(pression_score, 1),
            "comportement": round(behav_score, 1),
        },
        "distance_m": round(total_dist_m, 0),
        "avg_cost": None,
        "justification": justification,
    }


# =====================================================================
# CONFIANCE (multi-facteurs ecologiques)
# =====================================================================

def _assess_confidence(
    grid_path: Optional[List[Tuple[int, int]]],
    grid: np.ndarray,
    terrain_signals: Dict,
    distance_m: float,
    has_dem: bool = False,
    grid_meta: Dict = None,
) -> Tuple[str, float]:
    """
    Evalue la confiance du trajet selon des criteres ecologiques.

    Facteurs:
      - A* path quality (chemin trouve, longueur suffisante)
      - Cout moyen du chemin (bas = ecologiquement coherent)
      - Couvert forestier le long du trajet
      - Presence de ruisseaux/eau
      - Faible perturbation humaine
      - Distance raisonnable
      - Donnees DEM disponibles (terrain reel)
      - Lisieres et corridors eau dans la grille

    "real": confiance >= 0.60, chemin A* valide, donnees solides
    "ai": chemin direct/estime, donnees partielles, confiance < 0.60
    """
    if grid_path is None:
        # Pas de chemin A* -> trajet estime (IA)
        base = 0.25
        if terrain_signals.get("forest_proxy", 0) > 0.5:
            base += 0.05
        if distance_m < 2000:
            base += 0.05
        return "ai", round(min(0.50, base), 2)

    grid_meta = grid_meta or {}
    rows, cols = grid.shape
    path_len = len(grid_path)

    # Cout moyen du chemin A*
    costs = [grid[r, c] for r, c in grid_path if 0 <= r < rows and 0 <= c < cols]
    avg_cost = np.mean(costs) if costs else 5.0
    max_cost = np.max(costs) if costs else 10.0

    confidence = 0.40

    # Facteur 1: Qualite du chemin A*
    if path_len > 5:
        confidence += 0.12
    if path_len > 15:
        confidence += 0.05

    # Facteur 2: Cout ecologique du chemin (bas = corridors naturels)
    if avg_cost < 0.4:
        confidence += 0.12  # Chemin suit les corridors ecologiques
    elif avg_cost < 0.8:
        confidence += 0.08
    elif avg_cost < 1.5:
        confidence += 0.03

    # Facteur 3: Absence de cout extremement eleve (pas de passage force)
    if max_cost < 3.0:
        confidence += 0.06

    # Facteur 4: Couvert forestier
    forest_proxy = terrain_signals.get("forest_proxy", 0.5)
    if forest_proxy > 0.6:
        confidence += 0.06
    elif forest_proxy > 0.4:
        confidence += 0.03

    # Facteur 5: Presence d'eau
    if terrain_signals.get("has_stream", False):
        confidence += 0.04

    # Facteur 6: Faible perturbation humaine
    disturbance = terrain_signals.get("disturbance_index", 0.5)
    if disturbance < 0.3:
        confidence += 0.05

    # Facteur 7: Distance coherente avec le comportement
    if distance_m < 2500:
        confidence += 0.04
    elif distance_m < 4000:
        confidence += 0.02

    # Facteur 8: DEM SRTM reel disponible
    if has_dem:
        confidence += 0.06

    # Facteur 9: Grille contient des corridors ecologiques identifies
    lisiere_pct = grid_meta.get("lisiere_cells", 0) / max(1, grid_meta.get("total_cells", 1))
    water_corr_pct = grid_meta.get("water_corridor_cells", 0) / max(1, grid_meta.get("total_cells", 1))
    if lisiere_pct > 0.05:
        confidence += 0.03
    if water_corr_pct > 0.03:
        confidence += 0.03

    confidence = min(0.95, max(0.15, confidence))

    # Seuil: "real" si confiance >= 0.60 et chemin A* valide
    if confidence >= 0.60:
        return "real", round(confidence, 2)
    return "ai", round(confidence, 2)


# =====================================================================
# FALLBACK DIRECT PATH
# =====================================================================

def _corridors_intersect_roads(
    path_latlon: List[List[float]],
    exclusions: List[Dict],
    threshold_m: float = 15.0,
) -> Tuple[bool, int]:
    """
    C6 (IC2): Vérifie si un corridor intersecte des routes significatives.
    Retourne (intersecte, nombre_d_intersections).
    """
    road_segments = []
    for ex in exclusions:
        if ex.get("type") != "roads" or ex.get("filtered_out"):
            continue
        sub = ex.get("sub_type", "")
        if sub in ("track", "footway", "path", "cycleway"):
            continue
        coords = ex.get("coordinates", [])
        if len(coords) >= 2:
            road_segments.append(coords)

    if not road_segments:
        return False, 0

    intersection_count = 0
    for i in range(len(path_latlon) - 1):
        p1 = path_latlon[i]
        p2 = path_latlon[i + 1]
        mid_lat = (p1[1] + p2[1]) / 2
        cos_lat = math.cos(math.radians(mid_lat))

        for road_coords in road_segments:
            for j in range(len(road_coords) - 1):
                r1 = road_coords[j]
                r2 = road_coords[j + 1]
                d = _segment_distance_m(p1, p2, r1, r2, cos_lat)
                if d < threshold_m:
                    intersection_count += 1
                    break

    return intersection_count > 0, intersection_count


def _segment_distance_m(
    p1: List[float], p2: List[float],
    r1: list, r2: list,
    cos_lat: float,
) -> float:
    """Distance minimale approximée entre deux segments en mètres."""
    mid_p = [(p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2]
    mid_r = [(r1[0] + r2[0]) / 2, (r1[1] + r2[1]) / 2]
    dlat = (mid_p[1] - mid_r[1]) * METERS_PER_DEG_LAT
    dlng = (mid_p[0] - mid_r[0]) * METERS_PER_DEG_LAT * cos_lat
    return math.sqrt(dlat * dlat + dlng * dlng)


def _deduplicate_corridors(
    corridors: List[Dict],
    min_dist_m: float = 5.0,
) -> List[Dict]:
    """
    C7 (BUG-05): Élimine les corridors male/female quasi-identiques.
    Pour chaque paire male/female sur le même trajet, garde celui avec
    la meilleure confiance.
    """
    if len(corridors) < 2:
        return corridors

    keep = [True] * len(corridors)
    for i in range(len(corridors)):
        if not keep[i]:
            continue
        props_i = corridors[i].get("properties", {})
        coords_i = corridors[i].get("geometry", {}).get("coordinates", [])
        if not coords_i:
            continue

        for j in range(i + 1, len(corridors)):
            if not keep[j]:
                continue
            props_j = corridors[j].get("properties", {})
            coords_j = corridors[j].get("geometry", {}).get("coordinates", [])

            if props_i.get("sex") == props_j.get("sex"):
                continue
            if props_i.get("from_zone_id") != props_j.get("from_zone_id"):
                continue
            if props_i.get("to_zone_id") != props_j.get("to_zone_id"):
                continue

            avg_dist = _path_avg_distance_m(coords_i, coords_j)
            if avg_dist < min_dist_m:
                conf_i = props_i.get("confidence", 0)
                conf_j = props_j.get("confidence", 0)
                if conf_i >= conf_j:
                    keep[j] = False
                    logger.info(f"[C7] Duplicate removed: {corridors[j]['id']} (dist={avg_dist:.1f}m)")
                else:
                    keep[i] = False
                    logger.info(f"[C7] Duplicate removed: {corridors[i]['id']} (dist={avg_dist:.1f}m)")
                    break

    return [c for c, k in zip(corridors, keep) if k]


def _path_avg_distance_m(
    coords_a: List[List[float]],
    coords_b: List[List[float]],
) -> float:
    """Distance moyenne entre deux chemins (échantillonnage uniforme)."""
    samples = min(10, min(len(coords_a), len(coords_b)))
    if samples < 2:
        return float("inf")

    total = 0.0
    for k in range(samples):
        idx_a = int(k * (len(coords_a) - 1) / max(1, samples - 1))
        idx_b = int(k * (len(coords_b) - 1) / max(1, samples - 1))
        pa = coords_a[idx_a]
        pb = coords_b[idx_b]
        dlat = (pa[1] - pb[1]) * METERS_PER_DEG_LAT
        cos = math.cos(math.radians((pa[1] + pb[1]) / 2))
        dlng = (pa[0] - pb[0]) * METERS_PER_DEG_LAT * cos
        total += math.sqrt(dlat * dlat + dlng * dlng)
    return total / samples


def _direct_path_latlon(
    start: Dict[str, float],
    end: Dict[str, float],
    sex: str,
    species: str,
    exclusions: List[Dict],
    num_points: int = 8,
) -> List[List[float]]:
    """
    Chemin direct avec perturbations terrain (fallback si A* echoue).
    """
    slat, slng = start["lat"], start["lng"]
    elat, elng = end["lat"], end["lng"]
    params = get_sex_params(species, sex)
    cover_pref = params.get("cover_preference", 0.5)
    min_road_m = params.get("min_road_distance_m", 200)

    path = [[slng, slat]]
    import hashlib
    for i in range(1, num_points + 1):
        t = i / (num_points + 1)
        lat = slat + (elat - slat) * t
        lng = slng + (elng - slng) * t

        seed = int(hashlib.md5(f"{lat:.6f}{lng:.6f}{sex}".encode()).hexdigest()[:8], 16)
        rng = ((seed % 1000) / 1000.0 - 0.5) * 2.0
        perturb = rng * 0.0008 * (1.0 + cover_pref)
        lat += perturb
        lng += perturb * 0.7

        # Push from roads/urban
        for ex in exclusions[:30]:
            if ex.get("type") not in ("roads", "urban"):
                continue
            if ex.get("filtered_out"):
                continue
            coords = ex.get("coordinates", [])
            for c in coords[:3]:
                d = math.sqrt(
                    ((lat - c[1]) * METERS_PER_DEG_LAT) ** 2 +
                    ((lng - c[0]) * METERS_PER_DEG_LAT * math.cos(math.radians(lat))) ** 2
                )
                if d < min_road_m:
                    push = 0.0002 * (1.0 - d / min_road_m)
                    dlat = lat - c[1]
                    dlng = lng - c[0]
                    norm = math.sqrt(dlat * dlat + dlng * dlng) or 0.0001
                    lat += (dlat / norm) * push
                    lng += (dlng / norm) * push
                    break
        path.append([lng, lat])

    path.append([elng, elat])
    return path


# =====================================================================
# MAIN GENERATOR
# =====================================================================

def _dist_m(lat1, lng1, lat2, lng2):
    dlat = (lat2 - lat1) * METERS_PER_DEG_LAT
    cos = math.cos(math.radians((lat1 + lat2) / 2))
    dlng = (lng2 - lng1) * METERS_PER_DEG_LAT * cos
    return math.sqrt(dlat * dlat + dlng * dlng)


def _find_complementary_pairs(
    zones: List[Dict],
    max_distance_m: float,
) -> List[Tuple]:
    """Trouve les paires de zones complementaires a connecter."""
    pairs = []
    for i, z1 in enumerate(zones):
        t1 = z1.get("v7", {}).get("zone_type", "mixed")
        c1 = z1.get("centroid", {"lat": 0, "lng": 0})

        for j, z2 in enumerate(zones):
            if j <= i:
                continue
            t2 = z2.get("v7", {}).get("zone_type", "mixed")

            is_comp = (t1, t2) in COMPLEMENTARY_PAIRS or (t2, t1) in COMPLEMENTARY_PAIRS
            is_mixed = t1 == "mixed" or t2 == "mixed"
            if not is_comp and not is_mixed:
                continue

            c2 = z2.get("centroid", {"lat": 0, "lng": 0})
            dist = _dist_m(c1["lat"], c1["lng"], c2["lat"], c2["lng"])
            if dist > max_distance_m or dist < 150:
                continue

            pair_type = f"{t1}_to_{t2}"
            pairs.append((z1, z2, pair_type, dist))

    pairs.sort(key=lambda p: p[3])
    return pairs[:40]


def generate_corridors_v7(
    zones: List[Dict],
    exclusions: List[Dict],
    species: str,
    terrain_signals_by_zone: Dict[str, Dict] = None,
    max_corridors: int = 20,
    max_distance_m: float = 5000.0,
    dem_data: Dict = None,
    month: int = None,
    waypoint_center: Dict[str, float] = None,
    wind_direction_deg: float = None,
) -> List[Dict]:
    """
    Genere des trajets de chasse V7 scientifiquement coherents.
    Passe 2 MASTER PLAN: C4-C8 integres.

    Args:
        waypoint_center: {"lat": ..., "lng": ...} pour ancrage C5.
        wind_direction_deg: Direction vent dominant en degres (0=N, 90=E, 180=S, 270=O).
                           None = defaut SO→NE (225°) pour Quebec automne.
    """
    t0 = time.time()
    if not zones or len(zones) < 2:
        return []

    terrain_signals_by_zone = terrain_signals_by_zone or {}
    pairs = _find_complementary_pairs(zones, max_distance_m)
    if not pairs:
        return []

    # Include waypoint in bounds calculation if provided
    all_lats = [z.get("centroid", {}).get("lat", 0) for z in zones]
    all_lngs = [z.get("centroid", {}).get("lng", 0) for z in zones]
    if waypoint_center:
        all_lats.append(waypoint_center["lat"])
        all_lngs.append(waypoint_center["lng"])
    margin = 0.005
    grid_bounds = {
        "north": max(all_lats) + margin,
        "south": min(all_lats) - margin,
        "east": max(all_lngs) + margin,
        "west": min(all_lngs) - margin,
    }

    grid_size = 60
    if month is None:
        month = datetime.now(timezone.utc).month

    # C8 (IM2): Default wind direction SO→NE (225°) for Quebec autumn
    if wind_direction_deg is None:
        wind_direction_deg = 225.0

    has_dem = dem_data is not None and dem_data.get("status") == "success"
    grids = {}
    grid_meta = {}
    for sex in ("male", "female"):
        grids[sex], grid_meta[sex] = build_cost_grid(
            grid_bounds, exclusions, species, sex, grid_size,
            dem_data=dem_data,
            month=month,
        )
        # C8 (IM2): Apply wind cost modifier to grid
        _apply_wind_cost(grids[sex], wind_direction_deg, grid_bounds, grid_size, sex)

    corridors = []
    corr_count = 0

    # --- C5 (BUG-03): Generate waypoint access corridors ---
    if waypoint_center:
        access_corridors = _generate_waypoint_access(
            waypoint_center, zones, exclusions, species, grids,
            grid_bounds, grid_size, grid_meta, terrain_signals_by_zone,
            has_dem, month, wind_direction_deg,
        )
        corridors.extend(access_corridors)
        corr_count += len(access_corridors)
        logger.info(f"[C5] Generated {len(access_corridors)} waypoint access corridors")

    for z_from, z_to, pair_type, distance in pairs:
        if corr_count >= max_corridors:
            break

        from_centroid = z_from.get("centroid", {"lat": 0, "lng": 0})
        to_centroid = z_to.get("centroid", {"lat": 0, "lng": 0})
        from_id = z_from.get("zone_id", "")
        signals = terrain_signals_by_zone.get(from_id, {})

        for sex in ("male", "female"):
            if corr_count >= max_corridors:
                break

            grid = grids[sex]

            start_cell = (
                max(0, min(grid_size - 1, int((grid_bounds["north"] - from_centroid["lat"]) / max(1e-9, grid_bounds["north"] - grid_bounds["south"]) * grid_size))),
                max(0, min(grid_size - 1, int((from_centroid["lng"] - grid_bounds["west"]) / max(1e-9, grid_bounds["east"] - grid_bounds["west"]) * grid_size))),
            )
            end_cell = (
                max(0, min(grid_size - 1, int((grid_bounds["north"] - to_centroid["lat"]) / max(1e-9, grid_bounds["north"] - grid_bounds["south"]) * grid_size))),
                max(0, min(grid_size - 1, int((to_centroid["lng"] - grid_bounds["west"]) / max(1e-9, grid_bounds["east"] - grid_bounds["west"]) * grid_size))),
            )

            # C4 (BUG-02): A* with passable cell snap
            grid_path = _astar(grid, start_cell, end_cell)
            is_astar = grid_path is not None and len(grid_path) > 2

            if is_astar:
                path_latlon = _grid_path_to_latlon(grid_path, grid_bounds, grid_size, grid_size)
                path_latlon = _simplify_path(path_latlon, tolerance=0.00015)
                path_latlon = _chaikin_smooth(path_latlon, iterations=3)
            else:
                path_latlon = _direct_path_latlon(
                    from_centroid, to_centroid, sex, species, exclusions, 10
                )
                path_latlon = _chaikin_smooth(path_latlon, iterations=2)
                grid_path = None

            # C6 (IC2): Route intersection validation
            crosses_road, road_crossings = _corridors_intersect_roads(path_latlon, exclusions)

            source_type, confidence = _assess_confidence(
                grid_path, grid, signals, distance,
                has_dem=has_dem,
                grid_meta=grid_meta.get(sex, {}),
            )

            # C6: Downgrade confidence if corridor crosses roads
            if crosses_road:
                confidence = min(confidence, 0.45)
                source_type = "ai"
                logger.info(f"[C6] Corridor crosses {road_crossings} roads -> low_confidence")

            trail_score = _score_trail(
                path_latlon, grid, grid_path or [],
                grid_bounds, exclusions, sex, species, signals,
            )

            from_type = z_from.get("v7", {}).get("zone_type", "mixed")
            to_type = z_to.get("v7", {}).get("zone_type", "mixed")
            season_rel = {
                "spring": round(get_season_modifier(from_type, 4) * get_season_modifier(to_type, 4), 2),
                "summer": round(get_season_modifier(from_type, 7) * get_season_modifier(to_type, 7), 2),
                "fall": round(get_season_modifier(from_type, 10) * get_season_modifier(to_type, 10), 2),
                "winter": round(get_season_modifier(from_type, 1) * get_season_modifier(to_type, 1), 2),
            }
            max_season = max(season_rel.values()) or 1.0
            season_rel = {k: round(v / max_season, 2) for k, v in season_rel.items()}

            style_key = f"{sex}_{source_type}"
            style = CORRIDOR_STYLES.get(style_key, CORRIDOR_STYLES["mixed_real"])
            corridor_id = f"trail_{species}_{sex[0]}_{corr_count:03d}"

            corridors.append({
                "id": corridor_id,
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": path_latlon,
                },
                "properties": {
                    "trail_type": f"{source_type}_{sex}",
                    "corridor_type": pair_type,
                    "sex": sex,
                    "source": source_type,
                    "confidence": confidence,
                    "from_zone_type": from_type,
                    "to_zone_type": to_type,
                    "from_zone_id": from_id,
                    "to_zone_id": z_to.get("zone_id", ""),
                    "distance_m": round(distance, 0),
                    "species": species,
                    "style": {
                        **style,
                        "opacity": min(1.0, style.get("opacity", 0.85) + 0.10),
                    },
                    "scoring": trail_score,
                    "season_relevance": season_rel,
                    "month": month,
                    "dem_enhanced": has_dem,
                    "in_perimeter": True,
                    "road_crossings": road_crossings if crosses_road else 0,
                    "wind_direction_deg": wind_direction_deg,
                },
            })
            corr_count += 1

    # C7 (BUG-05): Deduplicate male/female corridors
    before_dedup = len(corridors)
    corridors = _deduplicate_corridors(corridors, min_dist_m=5.0)
    if before_dedup != len(corridors):
        logger.info(f"[C7] Deduplication: {before_dedup} -> {len(corridors)} corridors")

    elapsed = round((time.time() - t0) * 1000, 1)
    logger.info(
        f"[V7-Trail] Generated {len(corridors)} trails for {species} in {elapsed}ms "
        f"(pairs={len(pairs)}, grid={grid_size}x{grid_size}, wind={wind_direction_deg}deg)"
    )
    return corridors


# =====================================================================
# C5 (BUG-03): WAYPOINT ACCESS CORRIDORS
# =====================================================================

def _generate_waypoint_access(
    waypoint: Dict[str, float],
    zones: List[Dict],
    exclusions: List[Dict],
    species: str,
    grids: Dict[str, np.ndarray],
    grid_bounds: Dict,
    grid_size: int,
    grid_meta: Dict,
    terrain_signals_by_zone: Dict,
    has_dem: bool,
    month: int,
    wind_direction_deg: float,
) -> List[Dict]:
    """
    C5 (BUG-03): Génère des corridors d'accès du waypoint vers les zones
    les plus proches (rest/feed) pour chaque sexe.
    """
    access_corridors = []
    target_types = {"rest", "feed"}

    for sex in ("male", "female"):
        grid = grids[sex]
        best_zone = None
        best_dist = float("inf")

        for z in zones:
            zt = z.get("v7", {}).get("zone_type", "mixed")
            if zt not in target_types:
                continue
            c = z.get("centroid", {})
            d = _dist_m(waypoint["lat"], waypoint["lng"], c.get("lat", 0), c.get("lng", 0))
            if d < best_dist and d > 50:
                best_dist = d
                best_zone = z

        if not best_zone:
            continue

        zone_centroid = best_zone.get("centroid", {})
        wp_cell = (
            max(0, min(grid_size - 1, int((grid_bounds["north"] - waypoint["lat"]) / max(1e-9, grid_bounds["north"] - grid_bounds["south"]) * grid_size))),
            max(0, min(grid_size - 1, int((waypoint["lng"] - grid_bounds["west"]) / max(1e-9, grid_bounds["east"] - grid_bounds["west"]) * grid_size))),
        )
        zone_cell = (
            max(0, min(grid_size - 1, int((grid_bounds["north"] - zone_centroid["lat"]) / max(1e-9, grid_bounds["north"] - grid_bounds["south"]) * grid_size))),
            max(0, min(grid_size - 1, int((zone_centroid["lng"] - grid_bounds["west"]) / max(1e-9, grid_bounds["east"] - grid_bounds["west"]) * grid_size))),
        )

        grid_path = _astar(grid, wp_cell, zone_cell)
        is_astar = grid_path is not None and len(grid_path) > 2

        if is_astar:
            path_latlon = _grid_path_to_latlon(grid_path, grid_bounds, grid_size, grid_size)
            path_latlon = _simplify_path(path_latlon, tolerance=0.00015)
            path_latlon = _chaikin_smooth(path_latlon, iterations=3)
        else:
            path_latlon = _direct_path_latlon(
                waypoint, zone_centroid, sex, species, exclusions, 8
            )
            path_latlon = _chaikin_smooth(path_latlon, iterations=2)
            grid_path = None

        zone_id = best_zone.get("zone_id", "")
        signals = terrain_signals_by_zone.get(zone_id, {})
        source_type, confidence = _assess_confidence(
            grid_path, grid, signals, best_dist,
            has_dem=has_dem,
            grid_meta=grid_meta.get(sex, {}),
        )

        # C6 (IC2): Route intersection validation for access corridors
        crosses_road, road_crossings = _corridors_intersect_roads(path_latlon, exclusions)
        
        # Downgrade confidence if crosses roads
        if crosses_road:
            confidence = min(confidence, 0.45)
            source_type = "ai"

        trail_score = _score_trail(
            path_latlon, grid, grid_path or [],
            grid_bounds, exclusions, sex, species, signals,
        )

        zone_type = best_zone.get("v7", {}).get("zone_type", "mixed")
        style_key = f"{sex}_{source_type}"
        style = CORRIDOR_STYLES.get(style_key, CORRIDOR_STYLES["mixed_real"])
        corridor_id = f"access_{species}_{sex[0]}_{zone_type}"

        access_corridors.append({
            "id": corridor_id,
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": path_latlon,
            },
            "properties": {
                "trail_type": f"{source_type}_{sex}",
                "corridor_type": f"waypoint_to_{zone_type}",
                "sex": sex,
                "source": source_type,
                "confidence": confidence,
                "from_zone_type": "waypoint",
                "to_zone_type": zone_type,
                "from_zone_id": "waypoint",
                "to_zone_id": zone_id,
                "distance_m": round(best_dist, 0),
                "species": species,
                "style": {
                    **style,
                    "opacity": min(1.0, style.get("opacity", 0.85) + 0.15),
                    "width": style.get("width", 2.5) + 0.5,
                },
                "scoring": trail_score,
                "month": month,
                "dem_enhanced": has_dem,
                "in_perimeter": True,
                "is_access_corridor": True,
                "road_crossings": road_crossings if crosses_road else 0,
                "wind_direction_deg": wind_direction_deg,
            },
        })

    return access_corridors


# =====================================================================
# C8 (IM2): WIND COST MODIFIER
# =====================================================================

def _apply_wind_cost(
    grid: np.ndarray,
    wind_dir_deg: float,
    bounds: Dict[str, float],
    grid_size: int,
    sex: str,
) -> None:
    """
    C8 (IM2): Modifie la grille de coûts pour intégrer le vent dominant.
    Les animaux préfèrent se déplacer face au vent (upwind) pour détecter
    les odeurs. Réduit le coût dans la direction contre le vent.

    wind_dir_deg: direction D'OÙ vient le vent (225° = SO = vent vient du SO)
    """
    rows, cols = grid.shape
    wind_rad = math.radians(wind_dir_deg)
    # Vecteur vent normalisé (d'où il vient)
    wind_dx = math.sin(wind_rad)
    wind_dy = -math.cos(wind_rad)

    # Créer une carte directionnelle
    for r in range(rows):
        for c in range(cols):
            if grid[r, c] >= IMPASSABLE * 0.9:
                continue
            # Position normalisée dans la grille
            nr = r / max(1, rows - 1)
            nc = c / max(1, cols - 1)
            # Projection sur la direction du vent (dot product)
            projection = nr * wind_dy + nc * wind_dx
            # Bonus pour les positions face au vent (projection positive)
            # Réduction de coût de 5-15% face au vent
            wind_factor = projection * 0.10
            # Males en rut sont moins influencés par le vent
            if sex == "male":
                wind_factor *= 0.6
            grid[r, c] = max(0.1, grid[r, c] - wind_factor)

    logger.info(f"[C8] Wind cost applied: dir={wind_dir_deg}deg, sex={sex}")
