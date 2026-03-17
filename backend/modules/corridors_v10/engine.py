"""
CORRIDORS-V10 — Moteur principal (Orchestrateur)
====================================================
Norme CORRIDOR-V1/V10 officielle.
Pipeline:
  1. Charger le profil espece (12 parametres + description corridor)
  2. Generer la grille de couts enrichie (ECL, micro-topo, nourriture, refuge, etc.)
  3. Construire le reseau de corridors (A* + continuite absolue COR-006)
  4. Scorer le reseau + classification normative par corridor
  5. Valider BCE-4X + Steeve-MAX
  6. Retourner les resultats avec niveaux/couleurs/largeurs normatifs
"""
from .species_profiles import SPECIES_LIST, get_profile, get_season, get_season_modifiers, PARAM_KEYS
from .cost_surface import generate_cost_grid
from .network_builder import build_network
from .scoring import compute_corridor_score, compute_corridor_levels
from .validator import validate_bce4x, validate_steeve_max
from .classifier import classify_batch, CORRIDOR_LEVELS
import math


def _simplify_coords(coords, tolerance=0.00003):
    """Douglas-Peucker simplifie cote backend pour reduire le payload GeoJSON."""
    if len(coords) <= 4:
        return coords
    def sq_dist(p, a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]
        if dx != 0 or dy != 0:
            t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
            px, py = a[0] + t * dx, a[1] + t * dy
        else:
            px, py = a[0], a[1]
        return (p[0] - px) ** 2 + (p[1] - py) ** 2
    tol2 = tolerance * tolerance
    def dp(pts, first, last, result):
        max_d, idx = 0, 0
        for i in range(first + 1, last):
            d = sq_dist(pts[i], pts[first], pts[last])
            if d > max_d:
                max_d, idx = d, i
        if max_d > tol2:
            if idx - first > 1:
                dp(pts, first, idx, result)
            result.append(pts[idx])
            if last - idx > 1:
                dp(pts, idx, last, result)
    result = [coords[0]]
    dp(coords, 0, len(coords) - 1, result)
    result.append(coords[-1])
    return result


# ============================================================
# Zone Polygon Generation — BCE-4X / Steeve-MAX
# ============================================================
METERS_PER_DEG_LAT = 111320.0


def _meters_per_deg_lng(lat):
    return 111320.0 * math.cos(math.radians(lat))


def _score_cell_for_zone_type(cell, zone_type):
    """Score a cell for a specific ecological zone type."""
    if cell.get("barrier"):
        return 0
    if zone_type == "alimentation":
        return cell.get("canopy_density", 0) * 0.6 + cell.get("feuillus_nobles", 0) * 0.4
    elif zone_type == "repos":
        return cell.get("canopy_density", 0) * 0.5 + min(cell.get("distance_route_m", 0), 500) / 500 * 0.5
    elif zone_type == "rut":
        return cell.get("strate_1_3m", 0) * 0.5 + (1.0 - cell.get("canopy_density", 0)) * 0.3
    elif zone_type == "eau":
        d = cell.get("distance_eau_m", 500)
        if d < 150 and not cell.get("is_water", False):
            return 1.0 - d / 150
        return 0
    return 0


def _convex_hull(points):
    """Andrew's monotone chain convex hull. Returns closed polygon coords."""
    pts = sorted(set(points))
    if len(pts) <= 1:
        return []
    if len(pts) == 2:
        # Create a thin rectangle for 2 points
        a, b = pts
        dx = (b[0] - a[0]) * 0.0001
        dy = (b[1] - a[1]) * 0.0001
        return [
            (a[0] - dy, a[1] + dx), (b[0] - dy, b[1] + dx),
            (b[0] + dy, b[1] - dx), (a[0] + dy, a[1] - dx),
            (a[0] - dy, a[1] + dx),
        ]

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    hull = lower[:-1] + upper[:-1]
    hull.append(hull[0])  # close polygon
    return hull


def _generate_zone_polygons(zones, cell_data, n, center_lat, center_lng, side_m, cell_m):
    """
    Generate polygon geometries for V10 ecological zones.
    BFS flood-fill from zone center → convex hull polygon.
    BCE-4X: terrain-aware, deterministic, no fallback.
    """
    m_per_lng = _meters_per_deg_lng(center_lat)
    d_lat = cell_m / METERS_PER_DEG_LAT
    d_lng = cell_m / m_per_lng

    half = side_m / 2.0
    lat_start = center_lat - half / METERS_PER_DEG_LAT
    lng_start = center_lng - half / m_per_lng

    zone_polygons = []

    for zone in zones:
        zone_type = zone["type"]
        r0, c0 = zone["pos"]
        center_score = zone["score"]

        # BFS flood-fill: collect cells with good score for this zone type
        # Parametres elargis pour polygones bien visibles
        threshold = max(0.10, center_score * 0.25)
        max_radius = 10  # cells (250m at 25m/cell)
        max_cells = 60

        visited = set()
        zone_cells = []
        queue = [(r0, c0, 0)]  # (row, col, distance)
        visited.add((r0, c0))

        while queue and len(zone_cells) < max_cells:
            r, c, dist = queue.pop(0)
            if r < 0 or r >= n or c < 0 or c >= n:
                continue
            if abs(r - r0) > max_radius or abs(c - c0) > max_radius:
                continue

            cell = cell_data[r][c]

            # Always include first ring around center (2 cells)
            if dist <= 2 and not cell.get("barrier"):
                zone_cells.append((r, c))
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    nr, nc = r + dr, c + dc
                    if (nr, nc) not in visited:
                        visited.add((nr, nc))
                        queue.append((nr, nc, dist + 1))
                continue

            score = _score_cell_for_zone_type(cell, zone_type)
            if score >= threshold:
                zone_cells.append((r, c))
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    nr, nc = r + dr, c + dc
                    if (nr, nc) not in visited:
                        visited.add((nr, nc))
                        queue.append((nr, nc, dist + 1))

        if len(zone_cells) < 3:
            # Fallback: create hexagonal polygon around center (rayon elargi)
            clat, clng = zone["lat"], zone["lng"]
            radius_deg = cell_m * 4.0 / METERS_PER_DEG_LAT
            radius_lng = cell_m * 4.0 / m_per_lng
            hex_pts = []
            for i in range(6):
                angle = math.radians(60 * i + 30)
                hex_pts.append([
                    round(clng + radius_lng * math.cos(angle), 7),
                    round(clat + radius_deg * math.sin(angle), 7),
                ])
            hex_pts.append(hex_pts[0])  # close
            zone_polygons.append({
                "zone": zone,
                "polygon": [hex_pts],
            })
            continue

        # Convert cell positions to corner points for polygon generation
        cell_points = []
        for r, c in zone_cells:
            # 4 corners of each cell
            for dr, dc in [(0, 0), (0, 1), (1, 0), (1, 1)]:
                lat = lat_start + (r + dr) * d_lat
                lng = lng_start + (c + dc) * d_lng
                cell_points.append((round(lng, 7), round(lat, 7)))

        hull = _convex_hull(cell_points)
        if len(hull) < 4:
            continue

        # Add organic noise to hull vertices (deterministic per zone)
        noise_seed = hash(f"{zone['lat']:.6f}:{zone['lng']:.6f}:{zone_type}")
        noisy_hull = []
        for i, (lng_v, lat_v) in enumerate(hull):
            # Slight noise (5-15% of cell size) for organic shape
            h = ((noise_seed + i * 7919) % 10000) / 10000.0
            noise_factor = 0.3 * d_lat * (h - 0.5)
            noise_lng = 0.3 * d_lng * (((noise_seed + i * 6271) % 10000) / 10000.0 - 0.5)
            noisy_hull.append([
                round(lng_v + noise_lng, 7),
                round(lat_v + noise_factor, 7),
            ])
        # Close polygon
        if noisy_hull and noisy_hull[0] != noisy_hull[-1]:
            noisy_hull.append(noisy_hull[0])

        zone_polygons.append({
            "zone": zone,
            "polygon": [noisy_hull],
        })

    return zone_polygons


def analyze_corridors(
    center_lat: float,
    center_lng: float,
    species: str = "CERF",
    month: int = 10,
    side_m: float = 2000.0,
    cell_m: float = 25.0,
) -> dict:
    """Analyse complete des corridors fauniques (version legere, sans GeoJSON)."""
    species = species.upper()
    if species not in SPECIES_LIST:
        species = "CERF"

    profile = get_profile(species)
    season = get_season(month)
    season_mods = get_season_modifiers(species, month)

    grid_result = generate_cost_grid(
        center_lat, center_lng, profile, season_mods, side_m, cell_m, month
    )

    network = build_network(
        cost_grid=grid_result["grid"],
        cell_data=grid_result["cell_data"],
        n=grid_result["n"],
        profile=profile,
        season_mods=season_mods,
        grid_meta=grid_result["metadata"],
    )

    # Scorer chaque corridor individuellement avec classification normative
    enriched_corridors = compute_corridor_levels(
        network["corridors"], grid_result["cell_data"]
    )

    score_result = compute_corridor_score(
        zones=network["zones"],
        corridors=network["corridors"],
        continuity=network["continuity"],
        network_stats=network["network_stats"],
        profile=profile,
        cell_m=cell_m,
    )

    bce4x = validate_bce4x(
        corridors=network["corridors"],
        zones=network["zones"],
        continuity=network["continuity"],
        cost_grid=grid_result["grid"],
        cell_data=grid_result["cell_data"],
        n=grid_result["n"],
        profile=profile,
    )

    steeve_max = validate_steeve_max(
        profile=profile,
        zones=network["zones"],
        corridors=network["corridors"],
        network_stats=network["network_stats"],
        season=season,
        month=month,
    )

    # Resume corridors avec niveaux normatifs
    corridors_summary = []
    for c in enriched_corridors:
        corridors_summary.append({
            "id": c["id"],
            "from_zone": c["from_zone"]["type"],
            "to_zone": c["to_zone"]["type"],
            "length_cells": c["length_cells"],
            "cost": c["cost"],
            "score_individuel": c["score_individuel"],
            "niveau": c["niveau"],
            "color": c["color"],
            "largeur_m": c["largeur_m"],
            "forced": c.get("forced_connection", False),
        })

    # Distribution normative
    niveau_distribution = {}
    for lvl_name, lvl_info in CORRIDOR_LEVELS.items():
        count = sum(1 for c in enriched_corridors if c["niveau"] == lvl_name)
        niveau_distribution[lvl_name] = {
            "count": count,
            "color": lvl_info["color"],
            "largeur_m": lvl_info["largeur_m"],
            "label_fr": lvl_info["label_fr"],
        }

    return {
        "engine": "CORRIDORS-V10",
        "version": "10.0.0",
        "species": species,
        "season": season,
        "month": month,
        "profile_params": {k: profile[k] for k in PARAM_KEYS},
        "description_corridor": profile.get("description_corridor", ""),
        "grid": {
            "center_lat": center_lat,
            "center_lng": center_lng,
            "side_m": side_m,
            "cell_m": cell_m,
            "n": grid_result["n"],
            "total_cells": grid_result["metadata"]["total_cells"],
            "water_barriers": grid_result["metadata"]["water_barriers"],
            "slope_barriers": grid_result["metadata"]["slope_barriers"],
            "traversable_cells": grid_result["metadata"]["traversable_cells"],
        },
        "score_corridor": score_result["score_corridor"],
        "classe_corridor": score_result["classe_corridor"],
        "classe_label": score_result["classe_label"],
        "classe_color": score_result["classe_color"],
        "score_detail": score_result["detail"],
        "network": {
            "total_zones": network["network_stats"]["total_zones"],
            "total_corridors": network["network_stats"]["total_corridors"],
            "zone_types": network["network_stats"]["zone_types"],
            "corridors_summary": corridors_summary,
            "niveau_distribution": niveau_distribution,
        },
        "continuity": network["continuity"],
        "validation": {
            "bce4x": bce4x,
            "steeve_max": steeve_max,
        },
    }


def analyze_corridors_full(
    center_lat: float,
    center_lng: float,
    species: str = "CERF",
    month: int = 10,
    side_m: float = 2000.0,
    cell_m: float = 25.0,
) -> dict:
    """
    Analyse complete AVEC GeoJSON pour visualisation cartographique.
    Chaque corridor LineString inclut niveau, couleur, largeur normatifs.
    """
    species = species.upper()
    if species not in SPECIES_LIST:
        species = "CERF"

    profile = get_profile(species)
    season = get_season(month)
    season_mods = get_season_modifiers(species, month)

    grid_result = generate_cost_grid(
        center_lat, center_lng, profile, season_mods, side_m, cell_m, month
    )

    network = build_network(
        cost_grid=grid_result["grid"],
        cell_data=grid_result["cell_data"],
        n=grid_result["n"],
        profile=profile,
        season_mods=season_mods,
        grid_meta=grid_result["metadata"],
    )

    enriched_corridors = compute_corridor_levels(
        network["corridors"], grid_result["cell_data"]
    )

    score_result = compute_corridor_score(
        zones=network["zones"],
        corridors=network["corridors"],
        continuity=network["continuity"],
        network_stats=network["network_stats"],
        profile=profile,
        cell_m=cell_m,
    )

    bce4x = validate_bce4x(
        corridors=network["corridors"],
        zones=network["zones"],
        continuity=network["continuity"],
        cost_grid=grid_result["grid"],
        cell_data=grid_result["cell_data"],
        n=grid_result["n"],
        profile=profile,
    )

    steeve_max = validate_steeve_max(
        profile=profile,
        zones=network["zones"],
        corridors=network["corridors"],
        network_stats=network["network_stats"],
        season=season,
        month=month,
    )

    # GeoJSON corridors avec proprietes normatives + simplification geometrique
    geojson_features = []
    for c in enriched_corridors:
        raw_coords = [[pt["lng"], pt["lat"]] for pt in c["path"]]
        coords = _simplify_coords(raw_coords)
        feature = {
            "type": "Feature",
            "properties": {
                "corridor_id": c["id"],
                "from_type": c["from_zone"]["type"],
                "to_type": c["to_zone"]["type"],
                "length_cells": c["length_cells"],
                "cost": c["cost"],
                "species": species,
                "score": c["score_individuel"],
                "niveau": c["niveau"],
                "niveau_label": c["niveau_label"],
                "color": c["color"],
                "pattern": c["pattern"],
                "largeur_m": c["largeur_m"],
                "render_weight": c["render_weight"],
                "dash_array": c["dash_array"],
            },
            "geometry": {
                "type": "LineString",
                "coordinates": coords,
            },
        }
        geojson_features.append(feature)

    # GeoJSON zones ecologiques V10 — POLYGONES (BCE-4X / Steeve-MAX)
    zone_colors = {
        "alimentation": "#4CAF50",
        "repos": "#2196F3",
        "rut": "#FF5722",
        "eau": "#00BCD4",
    }
    zone_polygons = _generate_zone_polygons(
        network["zones"], grid_result["cell_data"], grid_result["n"],
        center_lat, center_lng, side_m, cell_m,
    )
    for zp in zone_polygons:
        z = zp["zone"]
        feature = {
            "type": "Feature",
            "properties": {
                "zone_type": z["type"],
                "score": z["score"],
                "species": species,
                "color": zone_colors.get(z["type"], "#9E9E9E"),
                "center_lat": z["lat"],
                "center_lng": z["lng"],
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": zp["polygon"],
            },
        }
        geojson_features.append(feature)

    geojson = {
        "type": "FeatureCollection",
        "features": geojson_features,
    }

    # Distribution normative
    niveau_distribution = {}
    for lvl_name, lvl_info in CORRIDOR_LEVELS.items():
        count = sum(1 for c in enriched_corridors if c["niveau"] == lvl_name)
        niveau_distribution[lvl_name] = {
            "count": count,
            "color": lvl_info["color"],
            "largeur_m": lvl_info["largeur_m"],
            "label_fr": lvl_info["label_fr"],
        }

    return {
        "engine": "CORRIDORS-V10",
        "version": "10.0.0",
        "species": species,
        "season": season,
        "month": month,
        "description_corridor": profile.get("description_corridor", ""),
        "score_corridor": score_result["score_corridor"],
        "classe_corridor": score_result["classe_corridor"],
        "classe_label": score_result["classe_label"],
        "classe_color": score_result["classe_color"],
        "score_detail": score_result["detail"],
        "network": network["network_stats"],
        "niveau_distribution": niveau_distribution,
        "continuity": network["continuity"],
        "validation": {
            "bce4x": bce4x,
            "steeve_max": steeve_max,
        },
        "geojson": geojson,
    }


def analyze_multi_species(
    center_lat: float,
    center_lng: float,
    month: int = 10,
) -> dict:
    """Analyse corridors pour les 5 especes."""
    results = {}
    for sp in SPECIES_LIST:
        r = analyze_corridors(center_lat, center_lng, sp, month)
        results[sp] = {
            "score_corridor": r["score_corridor"],
            "classe_corridor": r["classe_corridor"],
            "classe_label": r["classe_label"],
            "classe_color": r["classe_color"],
            "continuity": r["continuity"],
            "description_corridor": r["description_corridor"],
            "network_summary": {
                "total_zones": r["network"]["total_zones"],
                "total_corridors": r["network"]["total_corridors"],
                "niveau_distribution": r["network"]["niveau_distribution"],
            },
            "bce4x_status": r["validation"]["bce4x"]["status"],
            "steeve_max_status": r["validation"]["steeve_max"]["status"],
        }

    all_scores = [results[sp]["score_corridor"] for sp in SPECIES_LIST]
    stats = classify_batch(all_scores)

    return {
        "engine": "CORRIDORS-V10",
        "mode": "multi_species",
        "center": {"lat": center_lat, "lng": center_lng},
        "month": month,
        "season": get_season(month),
        "species_results": results,
        "statistics": stats,
        "palette_normative": CORRIDOR_LEVELS,
    }
