"""
BIONIC V7 — Pipeline V7
Orchestrateur principal du moteur V7.

Integre:
  - exclusion_engine_v6 (exclusion geometrique Shapely)
  - zone_typology_v7 (classification + scoring multi-criteres)
  - terrain_signals_v7 (signaux terrain depuis OSM/DEM/meteo)
  - corridor_v7 (corridors male/femelle, reel/IA)
  - zone_shape_v7 (morphologie terrain-aware)
  - species_behavior_v7 (matrices comportementales)

Remplace _process_single_layer() quand EXCLUSION_ENGINE_VERSION=v7.

100% independant. Feature flag V7.
"""

import math
import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Any

from .exclusion_engine_v7 import process_zones_v7_exclusion
from .zone_typology_v7 import (
    enrich_zone_v7,
    detect_hotspots,
    compute_global_score,
    compute_subscores,
    ZONE_TYPE_CONFIG,
)
from .terrain_signals_v7 import extract_terrain_signals_from_exclusions
from .corridor_v7 import generate_corridors_v7, CORRIDOR_STYLES
from .zone_shape_v7 import (
    smooth_zone_adaptive,
    snap_to_shorelines,
    validate_zone_topology,
)
from .species_behavior_v7 import get_species_needs, get_season_modifier

logger = logging.getLogger("bionic_engine.pipeline_v7")


def _merge_nearby_same_type_zones(zones: List[Dict], max_dist_m: float = 200.0) -> List[Dict]:
    """
    BIONIC V7.2 — Fusionne les zones du même type à moins de max_dist_m.
    Deux zones du même layer_id dont les centroides sont à <200m
    sont fusionnées en une seule zone elargie, coherente.
    """
    if len(zones) < 2:
        return zones

    from shapely.geometry import Polygon
    from shapely.ops import unary_union

    # Group by layer_id (zone type)
    groups = {}
    for z in zones:
        lid = z.get("layer_id", z.get("v7", {}).get("zone_type", "unknown"))
        groups.setdefault(lid, []).append(z)

    merged_zones = []
    for lid, group in groups.items():
        if len(group) < 2:
            merged_zones.extend(group)
            continue

        # Build proximity graph: which zones are within max_dist_m of each other
        n = len(group)
        parent = list(range(n))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a, b):
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb

        for i in range(n):
            ci = group[i].get("centroid", {})
            lat_i, lng_i = ci.get("lat", 0), ci.get("lng", 0)
            for j in range(i + 1, n):
                cj = group[j].get("centroid", {})
                lat_j, lng_j = cj.get("lat", 0), cj.get("lng", 0)
                dist = _haversine_m(lat_i, lng_i, lat_j, lng_j)
                if dist < max_dist_m:
                    union(i, j)

        # Collect clusters
        clusters = {}
        for i in range(n):
            root = find(i)
            clusters.setdefault(root, []).append(i)

        for root, indices in clusters.items():
            if len(indices) == 1:
                merged_zones.append(group[indices[0]])
                continue

            # Merge: union of all polygons, take best scoring zone as base
            # BIONIC V7.4: Use v7.score_global for best-zone selection
            polys = []
            best_zone = None
            best_score = -1
            for idx in indices:
                z = group[idx]
                coords = z.get("coordinates", [])
                if len(coords) >= 3:
                    try:
                        poly = Polygon([(c[1], c[0]) for c in coords])
                        if poly.is_valid:
                            polys.append(poly)
                    except Exception:
                        pass
                sc = z.get("v7", {}).get("score_global", 0)
                if sc > best_score:
                    best_score = sc
                    best_zone = z

            if not polys or best_zone is None:
                merged_zones.extend(group[idx] for idx in indices)
                continue

            merged_poly = unary_union(polys)
            if merged_poly.is_empty:
                merged_zones.extend(group[idx] for idx in indices)
                continue

            # Extract largest polygon if MultiPolygon
            if merged_poly.geom_type == "MultiPolygon":
                merged_poly = max(merged_poly.geoms, key=lambda g: g.area)

            # Update coordinates
            new_coords = [(lat, lng) for lng, lat in merged_poly.exterior.coords]
            centroid = merged_poly.centroid
            new_centroid = {"lat": centroid.y, "lng": centroid.x}

            merged_zone = {**best_zone}
            merged_zone["coordinates"] = new_coords
            merged_zone["centroid"] = new_centroid
            merged_zone["zone_id"] = f"{best_zone.get('zone_id', 'z')}_merged"
            merged_zone["merged_count"] = len(indices)
            merged_zones.append(merged_zone)
            logger.info(
                f"[V7.2-Merge] {lid}: merged {len(indices)} zones "
                f"(dist < {max_dist_m}m) into 1"
            )

    return merged_zones


def process_zones_v7(
    raw_zones: List[Dict],
    bounds: Dict[str, float],
    exclusions: List[Dict],
    layer_id: str,
    species: str = "moose",
    weather: Dict = None,
    dem_data: Dict = None,
    month: int = None,
) -> Tuple[List[Dict], List[Dict], Dict]:
    """
    Pipeline V7 complet pour une couche.

    Etapes:
      1. Exclusion V6 Shapely (P0 + P1 + P2)
      2. Shape enhancement (lissage adaptatif, snapping berges)
      3. Enrichissement V7 (typologie, scoring, hotspots)
         Avec donnees DEM reelles si disponibles.
    R3: month pinne pour determinisme.

    Returns:
        (valid_zones, rejected_zones, stats)
    """
    t0 = time.time()
    # R3: Utilise le mois pinne (pas de datetime.now())
    if month is None:
        month = datetime.now(timezone.utc).month

    stats = {
        "engine": "v7",
        "total_raw": len(raw_zones),
        "rejected_v6": 0,
        "trimmed": 0,
        "valid": 0,
        "hotspots": 0,
        "zone_types": {},
        "pipeline_time_ms": 0,
        "dem_available": dem_data is not None and dem_data.get("status") == "success",
    }

    if not raw_zones:
        return [], [], stats

    # STEP 1: V7 Exclusion Engine (geometric, V7 REDUCED margins)
    valid_zones, rejected_zones, v6_stats = process_zones_v7_exclusion(
        raw_zones=raw_zones,
        bounds=bounds,
        exclusions=exclusions,
        layer_id=layer_id,
        species=species,
    )

    stats["rejected_v6"] = v6_stats.get("rejected_p0", 0) + v6_stats.get("rejected_trimming", 0)
    stats["trimmed"] = v6_stats.get("trimmed", 0)
    stats["v6_stats"] = v6_stats

    if not valid_zones:
        stats["pipeline_time_ms"] = round((time.time() - t0) * 1000, 1)
        return [], rejected_zones, stats

    # STEP 2: Shape Enhancement
    for zone in valid_zones:
        coords = zone.get("coordinates", [])
        if len(coords) >= 3:
            smoothed = smooth_zone_adaptive(coords, iterations=4, terrain_roughness=0.3)
            validated = validate_zone_topology(smoothed)
            if validated:
                zone["coordinates"] = validated

    # STEP 3: V7 Enrichment (typology + scoring)
    # Prepare DEM data for zone-level sampling
    dem_stats = None
    _sample_dem = None
    if dem_data and dem_data.get("status") == "success":
        dem_stats = dem_data.get("stats", {})
        try:
            from .srtm_provider_v7 import sample_dem_at_point
            _sample_dem = lambda lat, lng: sample_dem_at_point(dem_data, lat, lng)
        except Exception:
            pass

    for idx, zone in enumerate(valid_zones):
        zone["zone_id"] = f"z_{species}_{layer_id}_{idx:03d}"

        # Sample DEM at zone centroid if available
        dem_point = None
        if _sample_dem:
            centroid = zone.get("centroid", {})
            dem_point = _sample_dem(centroid.get("lat", 0), centroid.get("lng", 0))

        enrich_zone_v7(
            zone=zone,
            layer_id=layer_id,
            species=species,
            exclusions=exclusions,
            weather=weather,
            month=month,
            dem_stats=dem_stats,
            dem_point=dem_point,
        )

        zone["exclusion_engine"] = "v7"

    # STEP 4: Detect Hotspots
    hotspot_list = detect_hotspots(valid_zones, threshold=68.0)
    stats["hotspots"] = len(hotspot_list)

    # STEP 5: Count zone types
    for zone in valid_zones:
        zt = zone.get("v7", {}).get("zone_type", "mixed")
        stats["zone_types"][zt] = stats["zone_types"].get(zt, 0) + 1

    stats["valid"] = len(valid_zones)
    stats["pipeline_time_ms"] = round((time.time() - t0) * 1000, 1)

    # STEP 6: BIONIC V7.2 — Merge same-type zones within 200m
    valid_zones = _merge_nearby_same_type_zones(valid_zones, max_dist_m=200.0)
    stats["valid_after_merge"] = len(valid_zones)

    merge_info = ""
    if stats["valid"] != stats["valid_after_merge"]:
        merge_info = f" -> {stats['valid_after_merge']} after merge"

    logger.info(
        f"[V7] {layer_id}: {stats['valid']} valid{merge_info}, "
        f"{stats['rejected_v6']} rejected, "
        f"{stats['hotspots']} hotspots, "
        f"types={stats['zone_types']}, "
        f"{stats['pipeline_time_ms']}ms"
    )

    return valid_zones, rejected_zones, stats


METERS_PER_DEG_LAT = 111320.0
# Perimetre 2 km² — rayon effectif ~1500m
# Le frontend genere des bounds de 0.015° (~1670m) autour du waypoint.
# Les zones generees sont dispersees dans ces bounds.
# Un rayon de 1500m couvre les zones pertinentes tout en
# excluant les corridors hors contexte pour les viewports larges.
PERIMETER_RADIUS_M = 1500.0


def _haversine_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Distance approx en metres entre deux points (Quebec latitudes)."""
    dlat = (lat2 - lat1) * METERS_PER_DEG_LAT
    cos_lat = math.cos(math.radians((lat1 + lat2) / 2))
    dlng = (lng2 - lng1) * METERS_PER_DEG_LAT * cos_lat
    return math.sqrt(dlat * dlat + dlng * dlng)


def _filter_zones_by_perimeter(
    zones: List[Dict],
    waypoint_center: Dict[str, float],
    radius_m: float = PERIMETER_RADIUS_M,
) -> List[Dict]:
    """
    Filtre les zones pour ne garder que celles dont le centroide
    est dans le perimetre de 2 km² autour du waypoint de l'usager.
    """
    wp_lat = waypoint_center["lat"]
    wp_lng = waypoint_center["lng"]
    filtered = []
    for zone in zones:
        centroid = zone.get("centroid", {})
        z_lat = centroid.get("lat", 0)
        z_lng = centroid.get("lng", 0)
        dist = _haversine_m(wp_lat, wp_lng, z_lat, z_lng)
        if dist <= radius_m:
            filtered.append(zone)
    logger.info(
        f"[V7-Perimeter] Waypoint ({wp_lat:.4f}, {wp_lng:.4f}): "
        f"{len(filtered)}/{len(zones)} zones dans le perimetre de {radius_m:.0f}m"
    )
    return filtered


def generate_all_corridors_v7(
    all_zones: Dict[str, List[Dict]],
    exclusions: List[Dict],
    species: str,
    max_corridors: int = 20,
    dem_data: Dict = None,
    month: int = None,
    waypoint_center: Dict[str, float] = None,
) -> List[Dict]:
    """
    Genere les corridors V7 entre toutes les zones de toutes les couches.
    R3: month pinne pour determinisme.
    
    FILTRAGE V7.1:
    - Si waypoint_center fourni, filtre les zones au perimetre de 2 km²
      avant la generation (evite le calcul A* sur des paires hors perimetre).
    """
    flat_zones = []
    for layer_zones in all_zones.values():
        flat_zones.extend(layer_zones)

    # Filtrage spatial: perimetre 2 km² autour du waypoint de l'usager
    if waypoint_center:
        flat_zones = _filter_zones_by_perimeter(flat_zones, waypoint_center)

    if len(flat_zones) < 2:
        return []

    # Build terrain signals for zones
    terrain_by_zone = {}
    for zone in flat_zones:
        zid = zone.get("zone_id", "")
        centroid = zone.get("centroid", {"lat": 0, "lng": 0})
        signals = extract_terrain_signals_from_exclusions(centroid, exclusions, 800.0)
        terrain_by_zone[zid] = signals

    corridors = generate_corridors_v7(
        zones=flat_zones,
        exclusions=exclusions,
        species=species,
        terrain_signals_by_zone=terrain_by_zone,
        max_corridors=max_corridors,
        dem_data=dem_data,
        month=month,
        waypoint_center=waypoint_center,
    )

    return corridors


def build_v7_response_metadata(
    stats_by_layer: Dict[str, Dict],
    corridors: List[Dict],
    species: str,
) -> Dict[str, Any]:
    """
    Construit les metadonnees V7 pour la reponse API.
    """
    total_zones = sum(s.get("valid", 0) for s in stats_by_layer.values())
    total_hotspots = sum(s.get("hotspots", 0) for s in stats_by_layer.values())
    total_rejected = sum(s.get("rejected_v6", 0) for s in stats_by_layer.values())
    total_trimmed = sum(s.get("trimmed", 0) for s in stats_by_layer.values())

    all_types = {}
    for s in stats_by_layer.values():
        for zt, count in s.get("zone_types", {}).items():
            all_types[zt] = all_types.get(zt, 0) + count

    return {
        "engine": "v7",
        "species": species,
        "total_zones": total_zones,
        "total_hotspots": total_hotspots,
        "total_rejected": total_rejected,
        "total_trimmed": total_trimmed,
        "zone_type_distribution": all_types,
        "corridor_count": len(corridors),
        "corridor_styles": CORRIDOR_STYLES,
        "zone_type_config": ZONE_TYPE_CONFIG,
    }
