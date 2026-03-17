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
from .multi_engine import score_cell_multi_engine, ENGINE_REGISTRY, ENGINE_WEIGHTS, get_seasonal_weights
import math
from shapely.geometry import MultiPoint
from shapely import concave_hull as shapely_concave_hull


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


def _catmull_rom_closed(points, segments=8):
    """
    Catmull-Rom spline fermee pour polygone organique.
    BCE-4X: Courbure continue, fluide, naturelle.
    Steeve-MAX: Resolution maximale, 100% des points preserves.
    """
    np = len(points)
    if np < 3:
        return list(points)

    result = []
    for i in range(np):
        p0 = points[(i - 1) % np]
        p1 = points[i]
        p2 = points[(i + 1) % np]
        p3 = points[(i + 2) % np]

        for s in range(segments):
            t = s / segments
            t2 = t * t
            t3 = t2 * t

            x = 0.5 * (
                (2 * p1[0]) +
                (-p0[0] + p2[0]) * t +
                (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
                (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3
            )
            y = 0.5 * (
                (2 * p1[1]) +
                (-p0[1] + p2[1]) * t +
                (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
                (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3
            )
            result.append((round(x, 7), round(y, 7)))

    return result


def _terrain_perturbation(r, c, cr, cc, cell, zone_type, d_lat, d_lng):
    """
    Calcule la perturbation terrain pour un point de frontiere.
    Fidelite ecologique: essences forestieres, pente, eau, peuplements.
    """
    # Direction outward from centroid
    dr_norm = r - cr
    dc_norm = c - cc
    dist = math.sqrt(dr_norm ** 2 + dc_norm ** 2) + 0.001

    # Terrain factors from cell data
    canopy = cell.get("canopy_density", 0.5)
    feuillus = cell.get("feuillus_nobles", 0.3)
    strate = cell.get("strate_1_3m", 0.3)
    slope = min(cell.get("slope", 0), 35)
    d_eau = cell.get("distance_eau_m", 500)
    d_route = cell.get("distance_route_m", 500)

    # Slope factor: reduce perturbation at steep slopes (ruptures de pente)
    slope_factor = 1.0 - slope / 50.0

    # Forest stand factor: push boundary along forest edges
    # High canopy change = boundary follows stand edge
    forest_push = (canopy - 0.5) * d_lat * 0.35 * slope_factor

    # Water proximity: expand toward water for "eau" zones
    water_factor = 0.0
    if d_eau < 200:
        water_factor = (1.0 - d_eau / 200) * d_lat * 0.25
        if zone_type == "eau":
            water_factor *= 2.5  # Strong pull toward water features

    # Feuillus nobles factor: expand toward noble hardwoods for alimentation
    feuillus_push = 0.0
    if zone_type == "alimentation":
        feuillus_push = (feuillus - 0.3) * d_lat * 0.2

    # Strate factor: expand toward understory for rut zones
    strate_push = 0.0
    if zone_type == "rut":
        strate_push = (strate - 0.3) * d_lat * 0.2

    # Route avoidance: pull boundary away from roads
    route_pull = 0.0
    if d_route < 150:
        route_pull = -(1.0 - d_route / 150) * d_lat * 0.15

    # Deterministic micro-variation (simulates micro-relief, micro-depressions)
    seed = hash(f"{r}:{c}:{zone_type}")
    micro_lat = ((seed % 10000) / 10000.0 - 0.5) * d_lat * 0.2
    micro_lng = (((seed >> 16) % 10000) / 10000.0 - 0.5) * d_lng * 0.2

    # Outward push (base)
    base_push_lat = (dr_norm / dist) * d_lat * 0.45
    base_push_lng = (dc_norm / dist) * d_lng * 0.45

    total_lat = base_push_lat + forest_push + water_factor + feuillus_push + strate_push + route_pull + micro_lat
    total_lng = base_push_lng + micro_lng

    return total_lat, total_lng


def _chaikin_smooth(points, iterations=3):
    """
    Chaikin corner-cutting algorithm — Adoucissement anti-etoile.
    Steeve-MAX: Elimine spikes/etoiles tout en preservant la forme organique.
    BCE-4X: Respecte topographie et micro-reliefs.
    """
    if len(points) < 4:
        return points
    for _ in range(iterations):
        new_pts = []
        n_pts = len(points) - 1  # last point = first point (closed)
        for i in range(n_pts):
            p0 = points[i]
            p1 = points[(i + 1) % n_pts]
            new_pts.append((
                0.75 * p0[0] + 0.25 * p1[0],
                0.75 * p0[1] + 0.25 * p1[1],
            ))
            new_pts.append((
                0.25 * p0[0] + 0.75 * p1[0],
                0.25 * p0[1] + 0.75 * p1[1],
            ))
        if new_pts:
            new_pts.append(new_pts[0])  # close polygon
        points = new_pts
    return points


def _cluster_zones_by_type(zones, n):
    """
    Fusion ecologique — Steeve-MAX.
    Groupe les zones de meme type par super-quadrant (2x2).
    Resultat: 3-5 grandes zones organiques par type au lieu de 16 confetti.
    """
    quad_size = n // 4  # taille d'un quadrant en cellules
    by_type = {}
    for z in zones:
        by_type.setdefault(z["type"], []).append(z)

    clusters = []
    for ztype, type_zones in by_type.items():
        # Grouper par super-quadrant 2x2
        super_quads = {}
        for z in type_zones:
            r, c = z["pos"]
            sq_r = min(r // (quad_size * 2), 1)
            sq_c = min(c // (quad_size * 2), 1)
            super_quads.setdefault((sq_r, sq_c), []).append(z)

        for cluster in super_quads.values():
            clusters.append(cluster)

    return clusters


def _generate_zone_polygons(zones, cell_data, n, center_lat, center_lng, side_m, cell_m, month=10):
    """
    NORME STEEVE-MAX — Polygones organiques BIONIC V10
    Superposition libre + Dimension dynamique + Adoucissement
    Protection BCE-4X obligatoire.

    Pipeline:
    0. Fusion ecologique (clustering super-quadrant 2x2)
    1. Dimension dynamique (rayon proportionnel a l'attraction)
    2. BFS multi-source terrain-aware (superposition libre)
    3. Concave hull (Shapely) — contour propre sans spikes
    4. Lissage morphologique (buffer+/buffer-) — supprime aretes
    5. Sous-echantillonnage control points (~50 pts)
    6. Catmull-Rom spline (courbure continue, 6 segments)
    7. Chaikin smoothing (anti-etoile, 2 iterations)
    8. Firewall BCE-4X (spike detection, continuite)
    """
    m_per_lng = _meters_per_deg_lng(center_lat)
    d_lat = cell_m / METERS_PER_DEG_LAT
    d_lng = cell_m / m_per_lng

    half = side_m / 2.0
    lat_start = center_lat - half / METERS_PER_DEG_LAT
    lng_start = center_lng - half / m_per_lng

    NEIGHBORS_8 = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    # ══════ Phase 0: Fusion ecologique ══════
    clusters = _cluster_zones_by_type(zones, n)

    zone_polygons = []

    for cluster in clusters:
        zone_type = cluster[0]["type"]
        max_score = max(z["score"] for z in cluster)
        primary_zone = max(cluster, key=lambda z: z["score"])

        # ══════ Phase 1: Dimension dynamique ══════
        score_factor = max_score
        max_radius = int(8 + score_factor * 14)
        max_cells = int(40 + score_factor * 200)
        threshold = max(0.06, max_score * 0.12)
        inner_ring = int(2 + score_factor * 2)

        # ══════ Phase 2: BFS multi-source (superposition libre) ══════
        visited = set()
        zone_cells = []
        queue = []

        for z in cluster:
            r0, c0 = z["pos"]
            if (r0, c0) not in visited:
                queue.append((r0, c0, 0))
                visited.add((r0, c0))

        cluster_cr = sum(z["pos"][0] for z in cluster) / len(cluster)
        cluster_cc = sum(z["pos"][1] for z in cluster) / len(cluster)

        while queue and len(zone_cells) < max_cells:
            r, c, dist = queue.pop(0)
            if r < 0 or r >= n or c < 0 or c >= n:
                continue
            if abs(r - cluster_cr) > max_radius or abs(c - cluster_cc) > max_radius:
                continue

            cell = cell_data[r][c]

            if dist <= inner_ring and not cell.get("barrier"):
                zone_cells.append((r, c))
                for dr, dc in NEIGHBORS_8:
                    nr, nc = r + dr, c + dc
                    if (nr, nc) not in visited:
                        visited.add((nr, nc))
                        queue.append((nr, nc, dist + 1))
                continue

            score = _score_cell_for_zone_type(cell, zone_type)
            multi_score = score_cell_multi_engine(cell, zone_type, score, month=month)
            if multi_score >= threshold:
                zone_cells.append((r, c))
                for dr, dc in NEIGHBORS_8:
                    nr, nc = r + dr, c + dc
                    if (nr, nc) not in visited:
                        visited.add((nr, nc))
                        queue.append((nr, nc, dist + 1))

        if len(zone_cells) < 3:
            clat, clng = primary_zone["lat"], primary_zone["lng"]
            base_r = cell_m * (3.0 + score_factor * 4.0)
            radius_deg = base_r / METERS_PER_DEG_LAT
            radius_lng = base_r / m_per_lng
            ctrl_pts = []
            for k in range(12):
                angle = math.radians(30 * k)
                seed = hash(f"{clat:.5f}:{clng:.5f}:{k}")
                r_var = 1.0 + ((seed % 10000) / 10000.0 - 0.5) * 0.3
                ctrl_pts.append((
                    clng + radius_lng * math.cos(angle) * r_var,
                    clat + radius_deg * math.sin(angle) * r_var,
                ))
            smoothed = _catmull_rom_closed(ctrl_pts, segments=6)
            smoothed = _chaikin_smooth(smoothed + [smoothed[0]], iterations=2)
            smoothed = [[round(x, 7), round(y, 7)] for x, y in smoothed]
            zone_polygons.append({
                "cluster": cluster,
                "primary_zone": primary_zone,
                "polygon": [smoothed],
            })
            continue

        # ══════ Phase 3: Contour organique via buffer union (Shapely) ══════
        # Union de cercles autour de chaque cellule BFS → blob lisse sans spikes
        geo_points = []
        for r, c in zone_cells:
            lat = lat_start + (r + 0.5) * d_lat
            lng = lng_start + (c + 0.5) * d_lng
            geo_points.append((lng, lat))

        mp = MultiPoint(geo_points)
        # Buffer chaque point par ~1.5 cell width → union = blob organique lisse
        blob = mp.buffer(d_lat * 1.5)

        # Gerer MultiPolygon (garder le plus grand)
        if blob.geom_type == 'MultiPolygon':
            blob = max(blob.geoms, key=lambda g: g.area)

        if blob.is_empty or blob.geom_type not in ('Polygon',):
            blob = mp.convex_hull.buffer(d_lat * 0.5)

        # ══════ Phase 4: Reduction control points ══════
        # Simplifier pour ~60-80 pts de controle (intermediaire seulement)
        simplified = blob.simplify(d_lat * 0.6, preserve_topology=True)
        if simplified.is_empty or simplified.geom_type != 'Polygon':
            simplified = blob

        raw_coords = list(simplified.exterior.coords)

        # ══════ Phase 5: Sous-echantillonnage control points ══════
        if raw_coords and raw_coords[0] == raw_coords[-1]:
            raw_coords = raw_coords[:-1]

        target_pts = 50
        if len(raw_coords) > target_pts:
            step = len(raw_coords) / target_pts
            control_points = []
            for i in range(target_pts):
                idx = int(i * step) % len(raw_coords)
                control_points.append(raw_coords[idx])
        else:
            control_points = list(raw_coords)

        if len(control_points) < 3:
            control_points = list(raw_coords) if len(raw_coords) >= 3 else geo_points[:12]

        # Convertir en tuples (lng, lat)
        control_points = [(round(x, 7), round(y, 7)) for x, y in control_points]

        # ══════ Phase 6: Catmull-Rom spline (courbure continue) ══════
        smoothed = _catmull_rom_closed(control_points, segments=6)
        if smoothed:
            smoothed.append(smoothed[0])

        # ══════ Phase 7: Chaikin smoothing (anti-etoile, 3 iterations) ══════
        smoothed = _chaikin_smooth(smoothed, iterations=3)

        # BCE-4X: Validation post-smoothing — garantir polygone valide
        from shapely.geometry import Polygon as ShapelyPolygon
        test_poly = ShapelyPolygon(smoothed)
        if not test_poly.is_valid:
            # Reparer auto-intersections via buffer(0)
            fixed = test_poly.buffer(0)
            if fixed.geom_type == 'MultiPolygon':
                fixed = max(fixed.geoms, key=lambda g: g.area)
            if fixed.is_valid and fixed.geom_type == 'Polygon':
                smoothed = [list(c) for c in fixed.exterior.coords]

        # BCE-4X: Resolution maximale preservee
        smoothed = [[round(x, 7), round(y, 7)] for x, y in smoothed]

        zone_polygons.append({
            "cluster": cluster,
            "primary_zone": primary_zone,
            "polygon": [smoothed],
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

    # GeoJSON zones ecologiques V10 — POLYGONES ORGANIQUES (BCE-4X / Steeve-MAX)
    # STEVE-MAX-MULTI: Fusion + Dimension dynamique + Multi-engine + Smoothing
    zone_colors = {
        "alimentation": "#4CAF50",
        "repos": "#2196F3",
        "rut": "#FF5722",
        "eau": "#00BCD4",
    }
    zone_polygons = _generate_zone_polygons(
        network["zones"], grid_result["cell_data"], grid_result["n"],
        center_lat, center_lng, side_m, cell_m, month=month,
    )
    for zp in zone_polygons:
        cluster = zp["cluster"]
        pz = zp["primary_zone"]
        all_centers = [{"lat": z["lat"], "lng": z["lng"], "score": z["score"]} for z in cluster]
        feature = {
            "type": "Feature",
            "properties": {
                "zone_type": pz["type"],
                "score": pz["score"],
                "species": species,
                "color": zone_colors.get(pz["type"], "#9E9E9E"),
                "center_lat": pz["lat"],
                "center_lng": pz["lng"],
                "all_centers": all_centers,
                "cluster_size": len(cluster),
                "engine": "STEVE-MAX-MULTI",
                "engines_active": list(ENGINE_REGISTRY.keys()),
                "engines_count": len(ENGINE_REGISTRY),
                "season_month": month,
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
