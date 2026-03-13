"""
MODULE C — Zone Engine Core V2
BIONIC V5/V6 — Pipeline Organique Unifié — ExclusionsSpatiales.v1/v6

Orchestrateur du pipeline complet:
  layer -> raster -> contour -> polygone organique -> exclusion -> GeoJSON

Backend = seule source de vérité. Fetches ses propres exclusions.
Aucun lien transversal. Appels orchestrés uniquement.

100% indépendant. Source de vérité unique pour la génération des zones.

OPTIMISATIONS:
  - Traitement parallèle des couches (ThreadPoolExecutor)
  - Cache TTL 5 min, clé arrondie
  - Exclusion fetch avec retry 3x + timeout (ExclusionsSpatiales.v1)
  - Résolution adaptative intégrée
  - V6: Exclusion geometrique Shapely (feature flag EXCLUSION_ENGINE_VERSION)
"""

import os
import logging
import hashlib
import math
import time
import asyncio
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any

from modules.bionic_engine_p0.services.behavioral_rasterizer import (
    generate_layer_raster, get_supported_layers, get_supported_species, LAYER_PARAMS
)
from modules.bionic_engine_p0.services.organic_zone_generator_v2 import (
    extract_organic_zones
)
from modules.bionic_engine_p0.services.zone_visual_layer_v2 import (
    zones_to_geojson
)
from modules.bionic_engine_p0.services.zone_penalty_engine import (
    calculate_zone_penalty
)

# V6 Feature Flag
EXCLUSION_ENGINE_VERSION = os.environ.get("EXCLUSION_ENGINE_VERSION", "v5")

logger = logging.getLogger("bionic_engine.zone_engine_core_v2")

# Cache en memoire (TTL 15 min — R2 stabilisation)
_zone_cache: Dict[str, Any] = {}
_CACHE_TTL = 900

METERS_PER_DEG_LAT = 111320.0

# Thread pool for parallel layer processing (CPU-bound)
_executor = ThreadPoolExecutor(max_workers=6)


def _cache_key(bounds, species, layers, waypoint_center=None) -> str:
    # R1: Grille fixe 0.02deg (~2.2km) — aligne avec seed rasterizer
    s = math.floor(bounds['south'] / 0.02) * 0.02
    w = math.floor(bounds['west'] / 0.02) * 0.02
    n = math.floor(bounds['north'] / 0.02) * 0.02
    e = math.floor(bounds['east'] / 0.02) * 0.02
    data = f"{s:.4f}_{w:.4f}_{n:.4f}_{e:.4f}_{species}_{'_'.join(sorted(layers))}"
    if waypoint_center:
        data += f"_wp{waypoint_center['lat']:.4f}_{waypoint_center['lng']:.4f}"
    return hashlib.md5(data.encode()).hexdigest()



def _generate_corridors_10x(zones_by_layer, species, waypoint_center, bounds):
    """
    BIONIC 2000% — Corridors 10X avec A* pathfinding réel.
    Utilise l'algorithme A* de corridor_10x.py pour trouver des chemins optimaux
    entre zones fonctionnelles, en tenant compte des coûts de terrain.
    """
    from modules.bionic_engine_p0.services.corridor_10x import (
        corridor_10x_service, corridor_pathfinder
    )

    # --- Phase 1: Extraire les centroides par couche fonctionnelle ---
    STRUCTURAL_LAYERS = {"hydro", "pentes", "orientation", "ensoleillement", "altitude", "ndvi", "peuplements"}
    zone_centroids = {}
    zone_polygons = []  # Pour construire terrain_data

    for layer_id, zones in zones_by_layer.items():
        is_functional = layer_id not in STRUCTURAL_LAYERS
        for idx, z in enumerate(zones):
            centroid = z.get("centroid", {})
            lat = centroid.get("lat", 0)
            lng = centroid.get("lng", 0)
            coords = z.get("coordinates", [])
            if lat == 0 or lng == 0:
                if len(coords) >= 3:
                    lng = sum(c[0] for c in coords) / len(coords)
                    lat = sum(c[1] for c in coords) / len(coords)
                else:
                    continue
            # Stocker le polygone pour le terrain A*
            if coords:
                zone_polygons.append({
                    "layer_id": layer_id,
                    "coords": coords,
                    "centroid": (lat, lng),
                })
            if is_functional:
                zone_centroids.setdefault(layer_id, []).append({
                    "lat": lat, "lng": lng,
                    "zone_id": f"{layer_id}_{idx}",
                    "score": z.get("score", z.get("zoneScore", 0)),
                })

    logger.info(f"[Corridor A*] Zone centroids: { {k: len(v) for k, v in zone_centroids.items()} }")

    # --- Phase 2: Construire terrain_data pour le A* ---
    terrain_data = _build_terrain_grid(zone_polygons, bounds)

    # --- Phase 3: Générer les corridors avec A* ---
    CONNECT_PAIRS = [
        ("alimentation", "repos"), ("alimentation", "rut"), ("repos", "rut"),
        ("habitats", "alimentation"), ("habitats", "repos"), ("salines", "repos"),
        ("affuts", "habitats"), ("trajets", "alimentation"),
        ("affuts", "rut"), ("affuts", "trajets"), ("trajets", "rut"),
        ("salines", "rut"), ("salines", "affuts"), ("habitats", "rut"),
        ("habitats", "trajets"), ("salines", "trajets"),
        ("affuts", "repos"), ("affuts", "alimentation"),
    ]

    corridors = []
    corridor_id = 0
    seen_pairs = set()

    for from_layer, to_layer in CONNECT_PAIRS:
        from_zones = zone_centroids.get(from_layer, [])
        to_zones = zone_centroids.get(to_layer, [])
        if not from_zones or not to_zones:
            continue

        for fz in from_zones[:3]:
            best_tz = None
            best_dist = float("inf")
            for tz in to_zones:
                dlat = (fz["lat"] - tz["lat"]) * METERS_PER_DEG_LAT
                dlng = (fz["lng"] - tz["lng"]) * METERS_PER_DEG_LAT * math.cos(math.radians(fz["lat"]))
                dist = math.sqrt(dlat ** 2 + dlng ** 2)
                if dist < best_dist and dist > 50:
                    pair_key = f"{fz['zone_id']}-{tz['zone_id']}"
                    reverse_key = f"{tz['zone_id']}-{fz['zone_id']}"
                    if pair_key not in seen_pairs and reverse_key not in seen_pairs:
                        best_dist = dist
                        best_tz = tz

            if not best_tz or best_dist > 3000:
                continue

            pair_key = f"{fz['zone_id']}-{best_tz['zone_id']}"
            seen_pairs.add(pair_key)

            wwf_type = corridor_10x_service.classify_corridor_wwf(best_dist * 0.3)
            connectivity = corridor_10x_service.calculate_connectivity_score(from_layer, to_layer)

            # A* pathfinding
            path_coords = _find_astar_path(
                fz, best_tz, terrain_data, corridor_pathfinder, best_dist
            )

            corridors.append(_build_corridor_feature_astar(
                corridor_id, fz, best_tz, from_layer, to_layer, best_dist,
                wwf_type, connectivity, corridor_10x_service, path_coords
            ))
            corridor_id += 1

            if corridor_id >= 20:
                break
        if corridor_id >= 20:
            break

    # Fallback: intra-layer corridors
    if not corridors and zone_centroids:
        for layer_id, centroids in zone_centroids.items():
            if len(centroids) < 2:
                continue
            for i in range(len(centroids)):
                for j in range(i + 1, min(len(centroids), i + 3)):
                    fz, tz = centroids[i], centroids[j]
                    dlat = (fz["lat"] - tz["lat"]) * METERS_PER_DEG_LAT
                    dlng = (fz["lng"] - tz["lng"]) * METERS_PER_DEG_LAT * math.cos(math.radians(fz["lat"]))
                    dist = math.sqrt(dlat ** 2 + dlng ** 2)
                    if 50 < dist < 3000:
                        wwf_type = corridor_10x_service.classify_corridor_wwf(dist * 0.3)
                        path_coords = _find_astar_path(
                            fz, tz, terrain_data, corridor_pathfinder, dist
                        )
                        corridors.append(_build_corridor_feature_astar(
                            corridor_id, fz, tz, layer_id, layer_id, dist,
                            wwf_type, 50, corridor_10x_service, path_coords
                        ))
                        corridor_id += 1
                if corridor_id >= 10:
                    break
            if corridor_id >= 10:
                break

    logger.info(f"[Corridor A*] Generated {len(corridors)} corridors for species={species}")
    return corridors


def _build_terrain_grid(zone_polygons, bounds):
    """
    Construit une grille de coûts de terrain pour l'algorithme A*.
    Optimisé: n'échantillonne que les centroides + voisinage immédiat.
    """
    terrain_data = {}
    from modules.bionic_engine_p0.services.corridor_10x import TERRAIN_COSTS

    LAYER_TO_TERRAIN = {
        "habitats": "mature_forest", "alimentation": "forest_edge",
        "repos": "conifer_forest", "rut": "mixed_forest",
        "affuts": "hedgerow", "trajets": "wooded_strip",
        "salines": "riparian", "corridors": "valley",
        "peuplements": "mixed_forest", "hydro": "water_body",
    }

    step = 0.0015  # ~167m grid resolution
    max_cells = 2000  # Limite pour performance
    cell_count = 0

    for zp in zone_polygons:
        if cell_count >= max_cells:
            break
        coords = zp["coords"]
        layer_id = zp["layer_id"]
        terrain_type = LAYER_TO_TERRAIN.get(layer_id, "mixed_forest")
        if len(coords) < 3:
            continue

        # Bounding box du polygone
        lats = [c[1] for c in coords]
        lngs = [c[0] for c in coords]
        min_lat, max_lat = min(lats), max(lats)
        min_lng, max_lng = min(lngs), max(lngs)

        # Ajouter une marge autour de la zone
        margin = step * 2
        lat = min_lat - margin
        while lat <= max_lat + margin and cell_count < max_cells:
            lng = min_lng - margin
            while lng <= max_lng + margin and cell_count < max_cells:
                key = f"{lat:.4f},{lng:.4f}"
                existing = terrain_data.get(key, {})
                existing_cost = TERRAIN_COSTS.get(existing.get("type", "open_field"), 3.0)
                new_cost = TERRAIN_COSTS.get(terrain_type, 2.0)
                if new_cost < existing_cost:
                    terrain_data[key] = {"type": terrain_type, "slope": 5, "human_pressure": 0.1}
                    cell_count += 1
                lng += step
            lat += step

    return terrain_data


def _find_astar_path(fz, tz, terrain_data, pathfinder, distance):
    """
    Trouve un chemin A* entre deux zones. Fallback Bezier si échec.
    """
    start = (fz["lat"], fz["lng"])
    end = (tz["lat"], tz["lng"])

    # Ajuster la résolution selon la distance
    if distance < 300:
        pathfinder.grid_resolution = 30.0
        max_iter = 3000
    elif distance < 800:
        pathfinder.grid_resolution = 60.0
        max_iter = 5000
    elif distance < 1500:
        pathfinder.grid_resolution = 120.0
        max_iter = 8000
    else:
        pathfinder.grid_resolution = 200.0
        max_iter = 10000

    try:
        result = pathfinder.find_corridor_path(start, end, terrain_data, max_iterations=max_iter)
        if result and result.get("path"):
            smoothed = pathfinder.smooth_path(result["path"], smoothing_factor=0.3)
            return [[round(p["lng"], 6), round(p["lat"], 6)] for p in smoothed]
    except Exception as e:
        logger.warning(f"[Corridor A*] Pathfinding failed: {e}")

    # Fallback: Bezier quadratique
    n_points = max(5, int(distance / 50))
    path_coords = []
    for i in range(n_points + 1):
        t = i / n_points
        mid_lat = (fz["lat"] + tz["lat"]) / 2 + (0.0002 * math.sin(t * math.pi))
        mid_lng = (fz["lng"] + tz["lng"]) / 2 + (0.0002 * math.cos(t * math.pi))
        lat = (1 - t) ** 2 * fz["lat"] + 2 * (1 - t) * t * mid_lat + t ** 2 * tz["lat"]
        lng = (1 - t) ** 2 * fz["lng"] + 2 * (1 - t) * t * mid_lng + t ** 2 * tz["lng"]
        path_coords.append([round(lng, 6), round(lat, 6)])
    return path_coords


def _build_corridor_feature_astar(corridor_id, fz, tz, from_layer, to_layer, dist, wwf_type, connectivity, service, path_coords):
    """Build a corridor GeoJSON Feature — V9 Pipeline with 9 BIONIC engines."""
    is_astar = len(path_coords) > 0 and len(path_coords) != max(5, int(dist / 50)) + 1
    pathfinding_method = "A*" if is_astar else "bezier_fallback"

    # V9: Build base feature, scoring will be computed by engines
    feature = {
        "type": "Feature",
        "id": f"corridor-10x-{corridor_id}",
        "geometry": {"type": "LineString", "coordinates": path_coords},
        "properties": {
            "source": "corridor_10x",
            "corridor_type": wwf_type.value,  # Will be overridden by V9 classification
            "from_zone_type": from_layer,
            "to_zone_type": to_layer,
            "from_zone_id": fz["zone_id"],
            "to_zone_id": tz["zone_id"],
            "distance_m": round(dist, 1),
            "sex": "both",
            "pathfinding": pathfinding_method,
            "dem_enhanced": False,
            "in_perimeter": True,
            "scoring": {
                "score": 0,  # Placeholder — V9 engines will compute
                "subscores": {"connectivity": round(connectivity, 1)},
                "justification": [],
            },
            "wwf_classification": {"type": wwf_type.value, "label": service._get_wwf_label(wwf_type)},
        },
    }

    # V9: Evaluate with full pipeline (9 engines + continuity fix + enrichment)
    try:
        from modules.bionic_engine_p0.engines.corridors_v9 import corridor_engine_v9, CLASSIFICATION_V9
        from datetime import datetime, timezone

        global_context = {
            "species": getattr(service, '_current_species', 'moose'),
            "season": getattr(service, '_current_season', 'automne'),
            "month": datetime.now(timezone.utc).month,
            "hour": datetime.now(timezone.utc).hour,
            "weather": getattr(service, '_current_weather', {}),
            # STEVE-MAX: Waypoint center for STRICT 2km analysis box computation
            "waypoint_lat": getattr(service, '_current_waypoint_lat', None),
            "waypoint_lng": getattr(service, '_current_waypoint_lng', None),
        }

        # Full V9 pipeline: evaluate + fix gaps + clip + enrich + validate
        bounds = getattr(service, '_current_bounds', None)
        feature = corridor_engine_v9.process_corridor_full(feature, global_context, bounds)

        # Apply V9 classification styling
        classification = feature["properties"].get("classification_v9", {})
        level = classification.get("level", "gris")
        config = CLASSIFICATION_V9.get(level, CLASSIFICATION_V9["gris"])
        feature["properties"]["style"] = {
            "color": config["color"],
            "width": config["width"],
            "opacity": config["opacity"],
            "dasharray": config.get("dash") or "none",
        }
        feature["properties"]["confidence"] = feature["properties"].get("certainty", 0.5)

    except Exception as e:
        logger.warning(f"[Corridor V9] Engine evaluation failed, using fallback: {e}")
        # Fallback: basic scoring without engines
        score = round(connectivity * 0.6 + 20, 1)
        feature["properties"]["scoring"]["score"] = score
        feature["properties"]["confidence"] = 0.3
        feature["properties"]["style"] = {"color": "#9E9E9E", "width": 1.5, "opacity": 0.5, "dasharray": "8,4"}
        feature["properties"]["v9_pipeline"] = False

    return feature




def _point_in_polygon(lat: float, lng: float, poly_coords: list) -> bool:
    inside = False
    n = len(poly_coords)
    j = n - 1
    for i in range(n):
        xi, yi = poly_coords[i]
        xj, yj = poly_coords[j]
        if ((yi > lat) != (yj > lat)) and (lng < (xj - xi) * (lat - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def _point_near_line(lat: float, lng: float, line_coords: list, threshold_m: float) -> bool:
    threshold_deg = threshold_m / METERS_PER_DEG_LAT
    for i in range(len(line_coords) - 1):
        x1, y1 = line_coords[i]
        x2, y2 = line_coords[i + 1]
        dx, dy = x2 - x1, y2 - y1
        len_sq = dx * dx + dy * dy
        if len_sq == 0:
            continue
        t = max(0, min(1, ((lng - x1) * dx + (lat - y1) * dy) / len_sq))
        cx, cy = x1 + t * dx, y1 + t * dy
        dist = math.sqrt(
            ((lng - cx) * math.cos(math.radians(lat))) ** 2 + (lat - cy) ** 2
        )
        if dist < threshold_deg:
            return True
    return False


def _is_zone_excluded(zone_coords: list, exclusions: list) -> bool:
    """
    HYDRO FIX FINAL — Filtrage écologique corrigé.
    Règles d'exclusion :
      - Eau UNIQUEMENT : lake, reservoir, pond > 2000 m² → > 50% hits = rejet
      - JAMAIS exclure : wetland, stream, ditch, micro_water, filtered_out
      - Routes tertiaires+ : buffer 25m, > 50% hits = rejet
      - Pistes forestières (track) : IGNORÉ
      - Urbain : > 50% hits = rejet
      - Infrastructure : > 80% hits = rejet
    """
    if not exclusions:
        return False
    n = len(zone_coords)
    if n < 3:
        return False

    clat = sum(c[1] for c in zone_coords) / n
    clng = sum(c[0] for c in zone_coords) / n

    lats = [c[1] for c in zone_coords]
    lngs = [c[0] for c in zone_coords]
    min_lat, max_lat = min(lats), max(lats)
    min_lng, max_lng = min(lngs), max(lngs)

    test_points = [
        (clat, clng),
        ((clat + max_lat) / 2, clng),
        ((clat + min_lat) / 2, clng),
        (clat, (clng + max_lng) / 2),
        (clat, (clng + min_lng) / 2),
    ]

    DEEP_WATER_ONLY = {"lake", "reservoir"}
    POND_MIN_AREA = 2000

    hits_standard = 0
    hits_infra = 0
    total = len(test_points)

    for plat, plng in test_points:
        point_hit_standard = False
        point_hit_infra = False
        for ex in exclusions:
            # HYDRO FIX: skip filtered_out zones
            if ex.get("filtered_out"):
                continue

            ex_type = ex.get("type", "")

            # HYDRO FIX: never exclude wetland
            if ex_type == "wetland":
                continue

            sub_type = ex.get("sub_type", "")
            geom = ex.get("geometry_type", "polygon")
            coords = ex.get("coordinates", [])
            if not coords or len(coords) < 2:
                continue

            # --- EAU (HYDRO FIX: uniquement lake, reservoir, pond > 2000m²) ---
            if ex_type == "water":
                if geom == "polygon" and len(coords) >= 3:
                    st = (sub_type or "").lower()
                    if st in DEEP_WATER_ONLY:
                        if _point_in_polygon(plat, plng, coords):
                            point_hit_standard = True
                            break
                    elif st == "pond":
                        area = ex.get("area_m2", 0)
                        if area > POND_MIN_AREA:
                            if _point_in_polygon(plat, plng, coords):
                                point_hit_standard = True
                                break
                    # micro_water, stream, ditch, river, unknown → IGNORÉ
                continue

            # --- ROUTES ---
            if ex_type == "roads":
                if geom == "line":
                    st = (sub_type or "").lower()
                    if st == "track":
                        continue
                    if _point_near_line(plat, plng, coords, 25):
                        point_hit_standard = True
                        break
                continue

            # --- URBAIN ---
            if ex_type == "urban":
                if geom == "polygon" and len(coords) >= 3:
                    if _point_in_polygon(plat, plng, coords):
                        point_hit_standard = True
                        break
                continue

            # --- INFRASTRUCTURE (seuil séparé: > 80%) ---
            if ex_type == "infrastructure":
                if geom == "polygon" and len(coords) >= 3:
                    if _point_in_polygon(plat, plng, coords):
                        point_hit_infra = True
                        break
                continue

        if point_hit_standard:
            hits_standard += 1
        if point_hit_infra:
            hits_infra += 1

    if hits_standard > (total / 2):
        return True
    if hits_infra > (total * 0.8):
        return True
    return False


async def _fetch_exclusions_from_terrain(bounds: Dict[str, float]) -> List[Dict]:
    """
    ExclusionsSpatiales.v1 — Fetch exclusions depuis l'API Overpass.
    Inclut: water, urban, roads, infrastructure.
    RETRY 3x avec délai exponentiel en cas d'échec.
    Couvre exactement le viewport utilisateur.
    Tiling automatique si viewport > 0.3° pour respecter la limite Overpass.

    BIONIC V8.2 RESILIENCE:
    - Timeout Overpass: 12s (fast-fail)
    - Fallback sur cache expiré AVANT le 2e retry
    - Dégradation gracieuse: génère des zones avec exclusions=[] si tout échoue
    - Temps max total estimé: ~15s au lieu de ~42s
    """
    OVERPASS_TIMEOUT = 12  # secondes — fast-fail
    RETRY_DELAY = 1.0

    import httpx
    from modules.bionic_engine_p0.routers.terrain_data_router import (
        _build_overpass_query, _load_cache, _load_cache_expired, _save_cache,
        _cache_key as terrain_cache_key,
        _parse_overpass, OVERPASS_API_URL
    )

    exclude_types = ["water", "urban", "roads", "infrastructure"]
    detail_level = "low"

    # Tiling
    lat_range = bounds["north"] - bounds["south"]
    lng_range = bounds["east"] - bounds["west"]
    tiles = []
    if lat_range > 0.08 or lng_range > 0.12:
        tile_h, tile_w = 0.06, 0.08
        lat = bounds["south"]
        while lat < bounds["north"]:
            lng = bounds["west"]
            while lng < bounds["east"]:
                tiles.append({
                    "south": lat, "north": min(lat + tile_h, bounds["north"]),
                    "west": lng, "east": min(lng + tile_w, bounds["east"]),
                })
                lng += tile_w
            lat += tile_h
    else:
        tiles = [bounds]

    tile_cache_keys = []
    for tile in tiles[:9]:
        bbox = (tile["south"], tile["west"], tile["north"], tile["east"])
        ck = terrain_cache_key(bbox, exclude_types, detail_level)
        tile_cache_keys.append((tile, bbox, ck))

    # === PHASE 1: Cache frais ===
    fresh_exclusions = []
    uncached_tiles = []
    for tile, bbox, ck in tile_cache_keys:
        cached = await _load_cache(ck)
        if cached:
            fresh_exclusions.extend(cached.get("exclusion_zones", []))
        else:
            uncached_tiles.append((tile, bbox, ck))

    if not uncached_tiles:
        logger.info(f"ExclusionsSpatiales.v1: ALL from fresh cache — {len(fresh_exclusions)} exclusions")
        return fresh_exclusions

    # === PHASE 2: Overpass API (1 seul essai, fast-fail) ===
    overpass_ok = False
    try:
        for tile, bbox, ck in uncached_tiles:
            query = _build_overpass_query(
                tile["south"], tile["west"], tile["north"], tile["east"],
                exclude_types, detail_level
            )
            async with httpx.AsyncClient(timeout=OVERPASS_TIMEOUT) as client:
                resp = await client.post(OVERPASS_API_URL, data={"data": query})
                if resp.status_code == 200:
                    data = resp.json()
                    result = _parse_overpass(data, exclude_types)
                    await _save_cache(ck, {"success": True, "exclusion_zones": result})
                    fresh_exclusions.extend(result)
                    overpass_ok = True
                else:
                    logger.warning(f"Overpass HTTP {resp.status_code} for tile {bbox}")
                    raise Exception(f"HTTP {resp.status_code}")
    except Exception as e:
        logger.warning(f"ExclusionsSpatiales.v1: Overpass failed: {e}")

    if overpass_ok and fresh_exclusions:
        logger.info(f"ExclusionsSpatiales.v1: Overpass OK — {len(fresh_exclusions)} exclusions")
        return fresh_exclusions

    # === PHASE 3: Fallback cache expiré (AVANT un 2e retry) ===
    expired_exclusions = list(fresh_exclusions)  # keep any fresh ones
    for tile, bbox, ck in uncached_tiles:
        expired = await _load_cache_expired(ck)
        if expired:
            expired_exclusions.extend(expired.get("exclusion_zones", []))

    if expired_exclusions:
        logger.info(
            f"ExclusionsSpatiales.v1: EXPIRED CACHE FALLBACK — "
            f"{len(expired_exclusions)} exclusions (stale data)"
        )
        return expired_exclusions

    # === PHASE 4: 2e essai Overpass (dernier recours avant dégradation) ===
    try:
        await asyncio.sleep(RETRY_DELAY)
        for tile, bbox, ck in uncached_tiles:
            query = _build_overpass_query(
                tile["south"], tile["west"], tile["north"], tile["east"],
                exclude_types, detail_level
            )
            async with httpx.AsyncClient(timeout=OVERPASS_TIMEOUT) as client:
                resp = await client.post(OVERPASS_API_URL, data={"data": query})
                if resp.status_code == 200:
                    data = resp.json()
                    result = _parse_overpass(data, exclude_types)
                    await _save_cache(ck, {"success": True, "exclusion_zones": result})
                    fresh_exclusions.extend(result)
    except Exception as e:
        logger.warning(f"ExclusionsSpatiales.v1: Retry 2 failed: {e}")

    if fresh_exclusions:
        logger.info(f"ExclusionsSpatiales.v1: Retry 2 OK — {len(fresh_exclusions)} exclusions")
        return fresh_exclusions

    # === PHASE 5: Dégradation gracieuse ===
    logger.warning(
        "ExclusionsSpatiales.v1: ALL sources exhausted. "
        "BIONIC V8.2: Graceful degradation — generating zones WITHOUT exclusions."
    )
    return []


def _process_single_layer(
    layer_id: str,
    bounds: Dict[str, float],
    species: str,
    resolution: int,
    max_zones_per_layer: int,
    exclusions: List[Dict],
    dem_data: Dict = None,
    pinned_month: int = None,
) -> Dict[str, Any]:
    """
    Process a single layer (CPU-bound, runs in thread pool).
    BIONIC V5 P1: Applique les pénalités semi-statiques après exclusion dure.
    BIONIC V6: Utilise le moteur Shapely si EXCLUSION_ENGINE_VERSION=v6.
    BIONIC V7: DEM SRTM data passed for terrain-aware scoring.
    R3: pinned_month propagé pour déterminisme.
    """
    if layer_id not in LAYER_PARAMS:
        return {"layer_id": layer_id, "zones": [], "scores": [], "penalties": [], "rejected": 0}

    params = LAYER_PARAMS[layer_id]
    grid = generate_layer_raster(bounds, layer_id, species, resolution)

    raw_zones = extract_organic_zones(
        grid, bounds,
        threshold=params["threshold"],
        min_area=8000.0,
        max_area=80000.0,
        chaikin_iterations=4,
        max_compactness=0.85
    )

    # === V7 FULL ENGINE (Shapely + Typology + Scoring + Shaping) ===
    if EXCLUSION_ENGINE_VERSION == "v7":
        try:
            from modules.bionic_engine_p0.services.pipeline_v7 import process_zones_v7

            valid_zones, rejected_list, v7_stats = process_zones_v7(
                raw_zones=raw_zones,
                bounds=bounds,
                exclusions=exclusions,
                layer_id=layer_id,
                species=species,
                dem_data=dem_data,
                month=pinned_month,
            )

            rejected = len(rejected_list)

            valid_zones.sort(key=lambda z: abs(z.get("area_m2", 0) - 6500))
            valid_zones = valid_zones[:max_zones_per_layer]

            layer_scores = []
            layer_penalties = []
            for zone in valid_zones:
                # BIONIC V7.4: Score V7 direct — UNIQUE source de vérité.
                # score_global inclut déjà le season modifier de enrich_zone_v7.
                # AUCUNE double pénalisation, AUCUN fallback sur le grid V5.
                v7_data = zone.get("v7", {})
                score_global = v7_data.get("score_global", 0)
                penalized_score = max(25, int(score_global)) if score_global else 50
                logger.info(
                    f"[V7.4-SCORE] {layer_id}: score_global={score_global}, "
                    f"final={penalized_score}, type={v7_data.get('zone_type')}"
                )

                layer_scores.append(penalized_score)
                layer_penalties.append({
                    "factor": 1.0,
                    "raw_score": int(v7_data.get("score_raw", score_global)),
                    "details": {},
                    "v7": v7_data,
                })

            return {
                "layer_id": layer_id,
                "zones": valid_zones,
                "scores": layer_scores,
                "penalties": layer_penalties,
                "rejected": rejected,
                "rejected_zones": rejected_list,
                "exclusion_engine": "v7",
                "exclusion_stats": v7_stats,
            }

        except Exception as e:
            logger.warning(f"V7 engine failed for {layer_id}, falling back to V6: {e}")

    # === V6 SHAPELY ENGINE ===
    if EXCLUSION_ENGINE_VERSION in ("v6", "v7"):
        try:
            from modules.bionic_engine_p0.services.exclusion_engine_v6 import process_zones_v6

            valid_zones, rejected_list, excl_stats = process_zones_v6(
                raw_zones=raw_zones,
                bounds=bounds,
                exclusions=exclusions,
                layer_id=layer_id,
                species=species,
            )

            rejected = len(rejected_list)

            valid_zones.sort(key=lambda z: abs(z.get("area_m2", 0) - 6500))
            valid_zones = valid_zones[:max_zones_per_layer]

            layer_scores = []
            layer_penalties = []
            for zone in valid_zones:
                clat = zone.get("centroid", {}).get("lat", 0)
                clng = zone.get("centroid", {}).get("lng", 0)
                row = int(((bounds["north"] - clat) / max(0.0001, bounds["north"] - bounds["south"])) * (resolution - 1))
                col = int(((clng - bounds["west"]) / max(0.0001, bounds["east"] - bounds["west"])) * (resolution - 1))
                row = max(0, min(resolution - 1, row))
                col = max(0, min(resolution - 1, col))
                intensity = float(grid[row, col])
                raw_score = max(55, min(100, int(55 + intensity * 45)))

                penalty_factor = zone.get("penalty_factor", 1.0)
                penalty_details = zone.get("penalty_details", {})
                penalized_score = max(15, int(raw_score * penalty_factor))

                layer_scores.append(penalized_score)
                layer_penalties.append({
                    "factor": penalty_factor,
                    "raw_score": raw_score,
                    "details": penalty_details,
                })

            return {
                "layer_id": layer_id,
                "zones": valid_zones,
                "scores": layer_scores,
                "penalties": layer_penalties,
                "rejected": rejected,
                "rejected_zones": rejected_list,
                "exclusion_engine": "v6",
                "exclusion_stats": excl_stats,
            }

        except Exception as e:
            logger.warning(f"V6 engine failed for {layer_id}, falling back to V5: {e}")

    # === V5 LEGACY ENGINE (fallback) ===
    rejected = 0
    valid_zones = []
    for zone in raw_zones:
        if _is_zone_excluded(zone["coordinates"], exclusions):
            rejected += 1
            continue
        valid_zones.append(zone)

    valid_zones.sort(key=lambda z: abs(z["area_m2"] - 6500))
    valid_zones = valid_zones[:max_zones_per_layer]

    # P1: Calcul des scores avec pénalités semi-statiques
    layer_scores = []
    layer_penalties = []
    for zone in valid_zones:
        clat, clng = zone["centroid"]["lat"], zone["centroid"]["lng"]
        row = int(((bounds["north"] - clat) / max(0.0001, bounds["north"] - bounds["south"])) * (resolution - 1))
        col = int(((clng - bounds["west"]) / max(0.0001, bounds["east"] - bounds["west"])) * (resolution - 1))
        row = max(0, min(resolution - 1, row))
        col = max(0, min(resolution - 1, col))
        intensity = float(grid[row, col])
        raw_score = max(55, min(100, int(55 + intensity * 45)))

        # P1: Appliquer les pénalités de proximité + fragmentation
        penalty_factor, penalty_details = calculate_zone_penalty(zone, layer_id, exclusions)
        penalized_score = max(15, int(raw_score * penalty_factor))

        layer_scores.append(penalized_score)
        layer_penalties.append({
            "factor": penalty_factor,
            "raw_score": raw_score,
            "details": penalty_details,
        })

    return {
        "layer_id": layer_id,
        "zones": valid_zones,
        "scores": layer_scores,
        "penalties": layer_penalties,
        "rejected": rejected,
    }


async def generate_organic_zones(
    bounds: Dict[str, float],
    species: str = "moose",
    layers: List[str] = None,
    exclusions: List[Dict] = None,
    resolution: int = 80,
    max_zones_per_layer: int = 8,
    waypoint_center: Dict[str, float] = None,
) -> Dict[str, Any]:
    """
    Pipeline complet de génération des zones organiques BIONIC V5.
    Backend = seule source de vérité. Fetch ses propres exclusions.
    OPTIMISÉ: traitement parallèle des couches via ThreadPoolExecutor.
    """
    start = time.time()

    if layers is None:
        layers = get_supported_layers()
    if species not in get_supported_species():
        species = "moose"

    # Filter to valid layers only
    layers = [ly for ly in layers if ly in LAYER_PARAMS]

    cache_k = _cache_key(bounds, species, layers, waypoint_center)
    cached = _zone_cache.get(cache_k)
    if cached and (time.time() - cached["ts"]) < _CACHE_TTL:
        return cached["data"]

    # Fetch exclusions with short timeout (non-blocking if fails)
    if exclusions is None or len(exclusions) == 0:
        exclusions = await _fetch_exclusions_from_terrain(bounds)

    # BIONIC V8.2 RESILIENCE: Dégradation gracieuse.
    # - exclusions=None ne devrait plus arriver (le fetch retourne [] en dernier recours)
    # - exclusions=[] signifie: Overpass indisponible, on génère les zones sans filtrage
    exclusion_degraded = False
    if exclusions is None:
        exclusions = []
        exclusion_degraded = True
        logger.warning("[BIONIC V8.2] Exclusions=None, forcing graceful degradation")
    elif len(exclusions) == 0:
        exclusion_degraded = True
        logger.warning("[BIONIC V8.2] Exclusions empty (Overpass unavailable), zones will be generated without exclusion filtering")

    # R3: Pin month once for the entire pipeline (determinism)
    pinned_month = datetime.now(timezone.utc).month

    # Fetch DEM SRTM data (async, cached in MongoDB)
    dem_data = None
    if EXCLUSION_ENGINE_VERSION == "v7":
        try:
            from modules.bionic_engine_p0.services.srtm_provider_v7 import (
                fetch_dem_for_pipeline,
            )
            dem_data = await fetch_dem_for_pipeline(bounds, species)
            if dem_data:
                logger.info(
                    f"[DEM] SRTM data available: "
                    f"elev=[{dem_data.get('stats', {}).get('elevation_min', '?')}, "
                    f"{dem_data.get('stats', {}).get('elevation_max', '?')}]m, "
                    f"slope_mean={dem_data.get('stats', {}).get('slope_mean_deg', '?')}deg"
                )
            else:
                logger.info("[DEM] SRTM data unavailable, using heuristic terrain signals")
        except Exception as e:
            logger.warning(f"[DEM] SRTM fetch failed, using heuristic: {e}")

    # Process ALL layers in PARALLEL using ThreadPoolExecutor
    loop = asyncio.get_event_loop()
    futures = []
    for layer_id in layers:
        future = loop.run_in_executor(
            _executor,
            _process_single_layer,
            layer_id, bounds, species, resolution, max_zones_per_layer, exclusions, dem_data, pinned_month
        )
        futures.append(future)

    results = await asyncio.gather(*futures, return_exceptions=True)

    zones_by_layer: Dict[str, List[Dict]] = {}
    scores_by_layer: Dict[str, List[int]] = {}
    penalties_by_layer: Dict[str, List[Dict]] = {}
    stats = {
        "layers_processed": 0,
        "total_zones": 0,
        "rejected_exclusion": 0,
        "exclusions_count": len(exclusions),
        "penalties_applied": 0,
        "exclusion_engine": EXCLUSION_ENGINE_VERSION,
    }

    # Aggregate rejection diagnostics
    rejection_diagnostics = {
        "total_rejected": 0,
        "by_reason": {},
        "by_layer": {},
        "details": [],
    }

    for result in results:
        if isinstance(result, Exception):
            logger.warning(f"Layer processing failed: {result}")
            continue
        layer_id = result["layer_id"]
        zones = result["zones"]
        scores = result["scores"]
        penalties = result.get("penalties", [])
        rejected_zones_list = result.get("rejected_zones", [])
        stats["rejected_exclusion"] += result["rejected"]
        stats["layers_processed"] += 1

        # Aggregate rejection reasons
        layer_rejections = []
        for rz in rejected_zones_list:
            reason = rz.get("rejection_reason", "unknown")
            pen = rz.get("penalty_details", {})
            centroid = rz.get("centroid", {})
            area = rz.get("area_m2", 0)

            # Count by reason
            rejection_diagnostics["by_reason"][reason] = \
                rejection_diagnostics["by_reason"].get(reason, 0) + 1
            rejection_diagnostics["total_rejected"] += 1

            # Count by layer
            if layer_id not in rejection_diagnostics["by_layer"]:
                rejection_diagnostics["by_layer"][layer_id] = {"count": 0, "reasons": {}}
            rejection_diagnostics["by_layer"][layer_id]["count"] += 1
            rejection_diagnostics["by_layer"][layer_id]["reasons"][reason] = \
                rejection_diagnostics["by_layer"][layer_id]["reasons"].get(reason, 0) + 1

            # Keep detail for first 20 rejections (avoid huge payload)
            if len(rejection_diagnostics["details"]) < 20:
                detail = {
                    "layer": layer_id,
                    "reason": reason,
                    "area_m2": round(area, 0) if area else None,
                }
                if centroid:
                    detail["centroid"] = {
                        "lat": round(centroid.get("lat", 0), 5),
                        "lng": round(centroid.get("lng", 0), 5),
                    }
                if pen:
                    detail["penalties"] = {
                        k: round(v, 3) if isinstance(v, (int, float)) else v
                        for k, v in pen.items()
                    }
                layer_rejections.append(detail)

        rejection_diagnostics["details"].extend(layer_rejections)

        if zones:
            zones_by_layer[layer_id] = zones
            scores_by_layer[layer_id] = scores
            penalties_by_layer[layer_id] = penalties
            stats["total_zones"] += len(zones)
            # Count zones that received a meaningful penalty (factor < 0.95)
            stats["penalties_applied"] += sum(1 for p in penalties if p.get("factor", 1.0) < 0.95)

    geojson = zones_to_geojson(zones_by_layer, species, scores_by_layer, penalties_by_layer)

    # T4 COHERENCE: Count features in GeoJSON = source of truth for frontend
    t4_feature_count = len(geojson.get("features", []))
    if t4_feature_count != stats["total_zones"]:
        logger.warning(
            f"[T4-COHERENCE] MISMATCH: stats.total_zones={stats['total_zones']} "
            f"vs geojson.features={t4_feature_count}"
        )
    stats["t4_zone_count"] = t4_feature_count

    # V8/10X: Generate corridors — ALWAYS (not just v7)
    corridors = []
    v7_metadata = {}
    if EXCLUSION_ENGINE_VERSION == "v7":
        try:
            from modules.bionic_engine_p0.services.pipeline_v7 import (
                generate_all_corridors_v7,
                build_v7_response_metadata,
            )
            corridors = generate_all_corridors_v7(
                all_zones=zones_by_layer,
                exclusions=exclusions,
                species=species,
                max_corridors=20,
                dem_data=dem_data,
                month=pinned_month,
                waypoint_center=waypoint_center,
            )
            v7_stats_by_layer = {}
            for result in results:
                if isinstance(result, Exception):
                    continue
                lid = result["layer_id"]
                v7_stats_by_layer[lid] = result.get("exclusion_stats", {})
            v7_metadata = build_v7_response_metadata(v7_stats_by_layer, corridors, species)
        except Exception as e:
            logger.warning(f"V7 corridor generation failed: {e}")

    # BCE-MAX x4.1: Fallback corridor generation for non-v7 engines
    if not corridors and zones_by_layer:
        try:
            # V9: Set context for BIONIC engines
            from modules.bionic_engine_p0.services.corridor_10x import corridor_10x_service
            corridor_10x_service._current_species = species
            corridor_10x_service._current_season = season if 'season' in dir() else 'automne'
            corridor_10x_service._current_bounds = bounds
            corridor_10x_service._current_weather = weather_metadata if 'weather_metadata' in dir() else {}
            # STEVE-MAX: Pass waypoint center for STRICT 2km analysis box
            if waypoint_center:
                corridor_10x_service._current_waypoint_lat = waypoint_center.get('lat')
                corridor_10x_service._current_waypoint_lng = waypoint_center.get('lng')
            corridors = _generate_corridors_10x(zones_by_layer, species, waypoint_center, bounds)
        except Exception as e:
            logger.warning(f"Corridor 10X fallback failed: {e}")

    # V9: Filter out circular corridors (start-end < 50m is circular)
    if corridors:
        pre_filter = len(corridors)
        filtered_corridors = []
        for c in corridors:
            coords = c.get("geometry", {}).get("coordinates", [])
            if len(coords) >= 2:
                start_c = coords[0]
                end_c = coords[-1]
                dist = math.sqrt(
                    ((start_c[1] - end_c[1]) * METERS_PER_DEG_LAT) ** 2
                    + ((start_c[0] - end_c[0]) * METERS_PER_DEG_LAT * math.cos(math.radians(start_c[1]))) ** 2
                )
                if dist >= 50:
                    filtered_corridors.append(c)
                else:
                    logger.info(f"[V9-Filter] Removed circular corridor (start-end: {dist:.0f}m)")
            else:
                filtered_corridors.append(c)
        corridors = filtered_corridors
        if pre_filter != len(corridors):
            logger.info(f"[V9-Filter] Removed {pre_filter - len(corridors)} circular corridors")

    # STEVE-MAX++ P0: Ensure 100% topological continuity via graph-based post-processing
    if corridors:
        try:
            from modules.bionic_engine_p0.engines.corridors_v9 import ensure_corridor_network_continuity
            all_zone_features = []
            for layer_id, zone_list in zones_by_layer.items():
                for z in zone_list:
                    all_zone_features.append(z)
            corridors = ensure_corridor_network_continuity(
                corridors=corridors,
                zones=all_zone_features,
                bounds=bounds,
            )
        except Exception as e:
            logger.warning(f"[Continuity] Network continuity post-processing failed: {e}")

    elapsed = round((time.time() - start) * 1000, 1)

    # BIONIC V7.3: Diagnostic — provide zero_zones_reason when all zones are filtered
    zero_reason = None
    if stats["total_zones"] == 0 and stats["rejected_exclusion"] > 0:
        zero_reason = "all_filtered_by_exclusions"
    elif stats["total_zones"] == 0 and stats["layers_processed"] > 0:
        zero_reason = "no_candidates_generated"

    result = {
        **geojson,
        "stats": {
            **stats,
            "computation_time_ms": elapsed,
            "species": species,
            "bounds": bounds,
            "resolution": resolution,
            "exclusion_degraded": exclusion_degraded,
            **({"zero_zones_reason": zero_reason} if zero_reason else {}),
            "dem_srtm": {
                "available": dem_data is not None and dem_data.get("status") == "success",
                "source": dem_data.get("validation", {}).get("source", "none") if dem_data else "none",
                "dataset": dem_data.get("dataset", "none") if dem_data else "none",
                "stats": dem_data.get("stats", {}) if dem_data and dem_data.get("status") == "success" else {},
            } if EXCLUSION_ENGINE_VERSION == "v7" else None,
        }
    }

    if corridors:
        result["corridors"] = corridors
    if v7_metadata:
        result["v7_metadata"] = v7_metadata

    # BIONIC V8.0: Include rejection diagnostics
    if rejection_diagnostics["total_rejected"] > 0:
        result["rejection_diagnostics"] = rejection_diagnostics

    _zone_cache[cache_k] = {"data": result, "ts": time.time()}

    logger.info(
        f"Generated {stats['total_zones']} organic zones for {species} "
        f"across {stats['layers_processed']} layers in {elapsed}ms "
        f"(rejected: excl={stats['rejected_exclusion']}, total_excl={len(exclusions)})"
    )

    return result


def clear_cache():
    global _zone_cache
    _zone_cache = {}
