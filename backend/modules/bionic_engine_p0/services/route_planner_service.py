"""
SERVICE ROUTE PLANNER — Tactical Route Optimization (A* Weighted)
BIONIC V5 ULTIME 300% — route_planner_v1

Calcule le parcours tactique optimal entre les hotspots (>70%)
en utilisant A* pondere sur la grille habitat_score.

Maximise: score habitat, connectivite ecologique, discretion.
Minimise: exposition, pression humaine, bruit.

Integre les waypoints QuickAdd comme points d'ancrage obligatoires.
Module isole. Shadow Mode. 0 impact sur pipeline principal.
"""

import heapq
import logging
import math
import time
import numpy as np
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("bionic_engine.route_planner")


def _extract_hotspots(
    scores: np.ndarray,
    grid_lats: List[float],
    grid_lngs: List[float],
    threshold: float = 70.0,
    min_distance_cells: int = 3,
) -> List[Dict[str, Any]]:
    """Extract hotspot cells (score > threshold) with spatial filtering."""
    rows, cols = scores.shape
    candidates = []

    for r in range(rows):
        for c in range(cols):
            if scores[r, c] >= threshold:
                candidates.append((scores[r, c], r, c))

    candidates.sort(key=lambda x: -x[0])

    hotspots = []
    used = set()

    for score, r, c in candidates:
        too_close = False
        for ur, uc in used:
            if abs(r - ur) < min_distance_cells and abs(c - uc) < min_distance_cells:
                too_close = True
                break
        if too_close:
            continue

        used.add((r, c))
        hotspots.append({
            "row": r, "col": c,
            "lat": grid_lats[r], "lng": grid_lngs[c],
            "score": round(float(score), 1),
        })

    return hotspots


def _astar_path(
    scores: np.ndarray,
    start: Tuple[int, int],
    end: Tuple[int, int],
) -> List[Tuple[int, int]]:
    """A* pathfinding weighted by habitat score (higher = cheaper to traverse)."""
    rows, cols = scores.shape
    sr, sc = start
    er, ec = end

    def heuristic(r, c):
        return math.sqrt((r - er) ** 2 + (c - ec) ** 2)

    def cost(r, c):
        s = scores[r, c]
        return max(0.1, (100.0 - s) / 100.0)

    open_set = [(heuristic(sr, sc), 0.0, sr, sc)]
    came_from = {}
    g_score = {(sr, sc): 0.0}
    closed = set()

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    while open_set:
        _, g, cr, cc = heapq.heappop(open_set)

        if (cr, cc) in closed:
            continue
        closed.add((cr, cc))

        if cr == er and cc == ec:
            path = [(cr, cc)]
            while (cr, cc) in came_from:
                cr, cc = came_from[(cr, cc)]
                path.append((cr, cc))
            return list(reversed(path))

        for dr, dc in dirs:
            nr, nc = cr + dr, cc + dc
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in closed:
                move_cost = cost(nr, nc) * (1.414 if abs(dr) + abs(dc) == 2 else 1.0)
                tentative_g = g + move_cost

                if tentative_g < g_score.get((nr, nc), float('inf')):
                    g_score[(nr, nc)] = tentative_g
                    came_from[(nr, nc)] = (cr, cc)
                    f = tentative_g + heuristic(nr, nc)
                    heapq.heappush(open_set, (f, tentative_g, nr, nc))

    return [(sr, sc), (er, ec)]


def _simplify_path(path: List[Tuple[int, int]], tolerance: int = 2) -> List[Tuple[int, int]]:
    """Reduce path points while keeping shape."""
    if len(path) <= 3:
        return path

    simplified = [path[0]]
    for i in range(1, len(path) - 1):
        pr, pc = simplified[-1]
        cr, cc = path[i]
        if abs(cr - pr) >= tolerance or abs(cc - pc) >= tolerance:
            simplified.append(path[i])
    simplified.append(path[-1])
    return simplified


def _order_waypoints_nearest(
    hotspots: List[Dict],
    waypoints: List[Dict],
    start_idx: int = 0,
) -> List[Dict]:
    """Order all points using nearest-neighbor heuristic."""
    all_points = hotspots + waypoints
    if len(all_points) <= 2:
        return all_points

    remaining = list(range(len(all_points)))
    start = min(start_idx, len(remaining) - 1)
    ordered = [remaining.pop(start)]

    while remaining:
        last = all_points[ordered[-1]]
        best_dist = float('inf')
        best_idx = 0
        for i, ri in enumerate(remaining):
            pt = all_points[ri]
            d = math.sqrt((last["lat"] - pt["lat"]) ** 2 + (last["lng"] - pt["lng"]) ** 2)
            if d < best_dist:
                best_dist = d
                best_idx = i
        ordered.append(remaining.pop(best_idx))

    return [all_points[i] for i in ordered]


def _haversine_km(lat1, lng1, lat2, lng2):
    """Distance in km between two lat/lng points."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


async def compute_tactical_route(
    bounds: Dict[str, float],
    species: str,
    resolution: int = 30,
    hotspot_threshold: float = 70.0,
    anchor_waypoints: Optional[List[Dict]] = None,
    walking_speed_kmh: float = 3.5,
) -> Dict[str, Any]:
    """
    Full route planning pipeline:
    1. Get habitat grid
    2. Extract hotspots
    3. Merge with anchor waypoints
    4. Order via nearest-neighbor
    5. Connect via A* on habitat grid
    6. Build route with distances and times
    """
    from modules.bionic_engine_p0.services.habitat_score_service import get_habitat_grid

    start = time.time()

    grid_result = await get_habitat_grid(bounds, species, resolution)
    scores = np.array(grid_result["scores"])
    grid = grid_result["grid"]

    hotspots = _extract_hotspots(scores, grid["lats"], grid["lngs"], hotspot_threshold)

    anchors = []
    if anchor_waypoints:
        for wp in anchor_waypoints:
            lat, lng = wp.get("lat", wp.get("latitude")), wp.get("lng", wp.get("longitude"))
            if lat is None or lng is None:
                continue
            row = int(round(((bounds["north"] - lat) / (bounds["north"] - bounds["south"])) * (resolution - 1)))
            col = int(round(((lng - bounds["west"]) / (bounds["east"] - bounds["west"])) * (resolution - 1)))
            row = max(0, min(row, resolution - 1))
            col = max(0, min(col, resolution - 1))
            anchors.append({
                "row": row, "col": col,
                "lat": lat, "lng": lng,
                "score": round(float(scores[row, col]), 1),
                "is_anchor": True,
                "name": wp.get("name", "Waypoint"),
            })

    if not hotspots and not anchors:
        elapsed = round((time.time() - start) * 1000, 1)
        return {
            "version": "route_planner_v1",
            "species": species,
            "bounds": bounds,
            "hotspots_found": 0,
            "route": None,
            "message": f"Aucun hotspot detecte (seuil: {hotspot_threshold}%)",
            "computation_time_ms": elapsed,
            "grid_stats": grid_result["stats"],
        }

    ordered_points = _order_waypoints_nearest(hotspots, anchors)

    full_path_coords = []
    segments = []

    for i in range(len(ordered_points) - 1):
        p1 = ordered_points[i]
        p2 = ordered_points[i + 1]

        raw_path = _astar_path(scores, (p1["row"], p1["col"]), (p2["row"], p2["col"]))
        simplified = _simplify_path(raw_path, tolerance=2)

        seg_coords = []
        seg_scores = []
        for r, c in simplified:
            lat = grid["lats"][min(r, len(grid["lats"]) - 1)]
            lng = grid["lngs"][min(c, len(grid["lngs"]) - 1)]
            seg_coords.append({"lat": lat, "lng": lng})
            seg_scores.append(round(float(scores[r, c]), 1))

        if seg_coords:
            dist_km = _haversine_km(p1["lat"], p1["lng"], p2["lat"], p2["lng"])
            path_dist = sum(
                _haversine_km(seg_coords[j]["lat"], seg_coords[j]["lng"],
                              seg_coords[j + 1]["lat"], seg_coords[j + 1]["lng"])
                for j in range(len(seg_coords) - 1)
            )

            segments.append({
                "from": {"lat": p1["lat"], "lng": p1["lng"], "score": p1["score"]},
                "to": {"lat": p2["lat"], "lng": p2["lng"], "score": p2["score"]},
                "path": seg_coords,
                "scores_along_path": seg_scores,
                "direct_distance_km": round(dist_km, 3),
                "path_distance_km": round(path_dist, 3),
                "estimated_time_min": round(path_dist / walking_speed_kmh * 60, 1),
                "avg_score_along_path": round(float(np.mean(seg_scores)), 1),
            })

            full_path_coords.extend(seg_coords)

    total_distance = sum(s["path_distance_km"] for s in segments)
    total_time = sum(s["estimated_time_min"] for s in segments)
    avg_path_score = float(np.mean([s["avg_score_along_path"] for s in segments])) if segments else 0

    elapsed = round((time.time() - start) * 1000, 1)

    route_points = []
    for i, pt in enumerate(ordered_points):
        route_points.append({
            "order": i + 1,
            "lat": pt["lat"],
            "lng": pt["lng"],
            "score": pt["score"],
            "is_anchor": pt.get("is_anchor", False),
            "name": pt.get("name", f"Hotspot #{i + 1}"),
        })

    logger.info(
        f"Route computed: species={species}, points={len(route_points)}, "
        f"segments={len(segments)}, dist={total_distance:.2f}km, "
        f"time={total_time:.0f}min, avg_score={avg_path_score:.1f}%, "
        f"elapsed={elapsed}ms"
    )

    return {
        "version": "route_planner_v1",
        "species": species,
        "bounds": bounds,
        "resolution": resolution,
        "hotspot_threshold": hotspot_threshold,
        "hotspots_found": len(hotspots),
        "anchor_waypoints_used": len(anchors),
        "route": {
            "points": route_points,
            "segments": segments,
            "full_path": full_path_coords,
            "total_distance_km": round(total_distance, 3),
            "total_time_min": round(total_time, 1),
            "avg_path_score": round(avg_path_score, 1),
            "walking_speed_kmh": walking_speed_kmh,
        },
        "grid_stats": grid_result["stats"],
        "data_sources": grid_result["data_sources"],
        "computation_time_ms": elapsed,
        "validation": {
            "shadow_mode": True,
            "zero_impact_on_production": True,
            "algorithm": "A* weighted (habitat_score inverse cost)",
        },
    }
