"""
BIONIC V7 — Exclusion Engine V7
Pipeline d'exclusion geometrique Shapely avec marges V7 REDUITES.

Utilise EXCLUSIVEMENT exclusion_config_v7.py pour les buffers et seuils.
Aucun appel au moteur legacy V6 ne doit transiter ici.

Operations:
  - P0-V7: Intersection polygon-polygon avec buffers V7 adaptatifs
  - P1-V7: Distance polygon-polygon pour penalites
  - P2-V7: Zone trimming (decoupe partielle)
  - Pression anthropique V7 (seuils relaxes rural)

Orchestré par pipeline_v7.py
"""

import math
import logging
import time
from typing import Dict, List, Tuple, Any

from shapely.geometry import Polygon

from .exclusion_config_v7 import (
    INTERSECTION_THRESHOLDS_V7,
    LAYER_WATER_THRESHOLDS,
    BAND_CLOSE_M_V7,
    BAND_MEDIUM_M_V7,
    BAND_FAR_M_V7,
    TRIMMING_MIN_AREA_M2_V7,
    TRIMMING_MIN_COMPACTNESS_V7,
    TRIMMING_MAX_AREA_M2_V7,
    ANTHROPIC_THRESHOLDS_V7,
    get_buffer_m_v7,
)
from .exclusion_geometry_v6 import (
    osm_coords_to_shapely,
    build_exclusion_unions,
    calculate_intersection_ratio,
    calculate_min_distance_deg,
    distance_deg_to_meters,
    trim_zone,
    shapely_to_osm_coords,
    polygon_area_m2_shapely,
    compute_compactness,
    METERS_PER_DEG_LAT,
)
from .zone_penalty_engine import PENALTY_MATRIX, _DEFAULT_PENALTIES

logger = logging.getLogger("bionic_engine.exclusion_engine_v7")


def _distance_to_band_v7(distance_m: float) -> str:
    """Convertit une distance en bande de proximite (V7)."""
    if distance_m < BAND_CLOSE_M_V7:
        return "close"
    elif distance_m < BAND_MEDIUM_M_V7:
        return "medium"
    elif distance_m < BAND_FAR_M_V7:
        return "far"
    return "none"


def _compute_lat_center(bounds: Dict[str, float]) -> float:
    return (bounds["north"] + bounds["south"]) / 2.0


def _area_m2_to_deg2(area_m2: float, lat_center: float) -> float:
    """Convertit m2 en deg2 pour les seuils Shapely."""
    cos_lat = math.cos(math.radians(lat_center))
    m_per_deg_lat = METERS_PER_DEG_LAT
    m_per_deg_lng = METERS_PER_DEG_LAT * cos_lat
    return area_m2 / (m_per_deg_lat * m_per_deg_lng)


def process_zones_v7_exclusion(
    raw_zones: List[Dict],
    bounds: Dict[str, float],
    exclusions: List[Dict],
    layer_id: str,
    species: str = "moose",
) -> Tuple[List[Dict], List[Dict], Dict]:
    """
    Pipeline d'exclusion V7 complet avec marges REDUITES.

    Utilise EXCLUSIVEMENT exclusion_config_v7.py.
    Aucun fallback vers V6.

    Etapes:
      1. Pre-traitement: construire les unions Shapely avec buffers V7
      2. P0-V7: exclusion geometrique exacte (intersection ratio V7)
      3. P2-V7: zone trimming
      4. P1-V7: penalite distance polygon-polygon
      5. Pression anthropique V7 (seuils relaxes)

    Returns:
        (valid_zones, rejected_zones, stats)
    """
    t0 = time.time()
    lat_center = _compute_lat_center(bounds)
    min_area_deg2 = _area_m2_to_deg2(TRIMMING_MIN_AREA_M2_V7, lat_center)

    stats = {
        "engine": "v7",
        "config": "exclusion_config_v7",
        "total_raw": len(raw_zones),
        "rejected_p0": 0,
        "rejected_trimming": 0,
        "trimmed": 0,
        "valid": 0,
        "shapely_time_ms": 0,
        "exclusion_unions_built": 0,
        "margins_applied": "V7_REDUCED",
    }

    if not raw_zones:
        return [], [], stats

    # STEP 1: Build exclusion unions with V7 buffers
    t_union = time.time()
    unions = build_exclusion_unions(
        exclusions, lat_center, bounds=bounds,
        buffer_fn=get_buffer_m_v7,
    )
    stats["shapely_time_ms"] = round((time.time() - t_union) * 1000, 1)
    stats["exclusion_unions_built"] = sum(
        1 for k in ("water", "urban", "roads", "infrastructure")
        if unions.get(k) is not None
    )

    # Build combined raw union for trimming
    raw_parts = []
    for ex_type in ("water", "urban", "roads", "infrastructure"):
        raw = unions.get(f"raw_{ex_type}")
        if raw is not None:
            raw_parts.append(raw)

    from shapely.ops import unary_union as _union
    combined_raw = _union(raw_parts) if raw_parts else None

    valid_zones = []
    rejected_zones = []

    for zone in raw_zones:
        coords = zone.get("coordinates", [])
        zone_poly = osm_coords_to_shapely(coords, "polygon")
        if zone_poly is None or zone_poly.is_empty:
            rejected_zones.append({**zone, "rejection_reason": "invalid_geometry"})
            stats["rejected_p0"] += 1
            continue

        # STEP 2+3: P0-V7 with integrated trimming (V7 thresholds)
        exclusion_details = {}

        for ex_type in ("water", "urban", "roads", "infrastructure"):
            prep_union = unions.get(ex_type)
            if prep_union is None:
                continue
            ratio = calculate_intersection_ratio(zone_poly, prep_union)
            exclusion_details[ex_type] = round(ratio, 4)

        # Check if any type exceeds V7 threshold
        # BCE-4X: Pour l'eau, utiliser le seuil spécifique par couche (affûts = 0.0)
        max_violation = None
        for ex_type in ("water", "urban", "roads", "infrastructure"):
            ratio = exclusion_details.get(ex_type, 0)
            if ex_type == "water":
                # Seuil par couche pour l'eau (BCE-4X)
                threshold = LAYER_WATER_THRESHOLDS.get(layer_id, INTERSECTION_THRESHOLDS_V7.get(ex_type, 0.03))
            else:
                threshold = INTERSECTION_THRESHOLDS_V7.get(ex_type, 0.5)
            if ratio > threshold:
                max_violation = (ex_type, ratio, threshold)
                break

        # If violation found, try trimming FIRST before rejecting
        trimmed_poly = zone_poly
        was_trimmed = False

        if max_violation is not None and combined_raw is not None:
            result_poly = trim_zone(zone_poly, combined_raw, min_area_deg2)
            if result_poly is None or result_poly.is_empty:
                rejected_zones.append({
                    **zone,
                    "rejection_reason": f"p0_v7_{max_violation[0]}_after_trim",
                    "intersection_ratio": round(max_violation[1], 4),
                    "threshold": max_violation[2],
                })
                stats["rejected_p0"] += 1
                continue

            # Re-check ratios after trimming
            still_violated = False
            for ex_type in ("water", "urban", "roads", "infrastructure"):
                prep_union = unions.get(ex_type)
                if prep_union is None:
                    continue
                new_ratio = calculate_intersection_ratio(result_poly, prep_union)
                exclusion_details[ex_type] = round(new_ratio, 4)
                # BCE-4X: seuil par couche pour l'eau
                if ex_type == "water":
                    threshold = LAYER_WATER_THRESHOLDS.get(layer_id, INTERSECTION_THRESHOLDS_V7.get(ex_type, 0.03))
                else:
                    threshold = INTERSECTION_THRESHOLDS_V7.get(ex_type, 0.5)
                if new_ratio > threshold:
                    still_violated = True
                    rejected_zones.append({
                        **zone,
                        "rejection_reason": f"p0_v7_{ex_type}_post_trim",
                        "intersection_ratio": round(new_ratio, 4),
                        "threshold": threshold,
                    })
                    stats["rejected_p0"] += 1
                    break

            if still_violated:
                continue

            if result_poly.area < zone_poly.area * 0.98:
                trimmed_poly = result_poly
                was_trimmed = True
                stats["trimmed"] += 1

        elif max_violation is not None:
            rejected_zones.append({
                **zone,
                "rejection_reason": f"p0_v7_{max_violation[0]}",
                "intersection_ratio": round(max_violation[1], 4),
                "threshold": max_violation[2],
            })
            stats["rejected_p0"] += 1
            continue

        else:
            # No violation — check if minor trimming would help
            if combined_raw is not None:
                any_intersection = any(
                    exclusion_details.get(t, 0) > 0.001
                    for t in ("water", "urban", "roads", "infrastructure")
                )
                if any_intersection:
                    result_poly = trim_zone(zone_poly, combined_raw, min_area_deg2)
                    if result_poly is not None and result_poly.area < zone_poly.area * 0.98:
                        trimmed_poly = result_poly
                        was_trimmed = True
                        stats["trimmed"] += 1

        # STEP 4: P1-V7 Penalty with exact polygon-polygon distances
        layer_penalties = PENALTY_MATRIX.get(layer_id, _DEFAULT_PENALTIES)
        penalty_details = {}
        total_mult = 1.0

        for ex_type in ("water", "urban", "roads", "infrastructure"):
            raw_union = unions.get(f"raw_{ex_type}")
            dist_deg = calculate_min_distance_deg(trimmed_poly, raw_union)
            dist_m = distance_deg_to_meters(dist_deg, lat_center)
            band = _distance_to_band_v7(dist_m)

            if band == "none":
                penalty_details[ex_type] = 1.0
                continue

            type_penalties = layer_penalties.get(
                ex_type, _DEFAULT_PENALTIES.get(ex_type, {})
            )
            mult = type_penalties.get(band, 1.0)
            penalty_details[ex_type] = round(mult, 3)
            total_mult *= mult

        # Fragmentation penalty
        comp = compute_compactness(trimmed_poly)
        area_m2 = polygon_area_m2_shapely(trimmed_poly, lat_center)

        if area_m2 < 10000 and comp < 0.3:
            penalty_details["fragmentation"] = 0.60
            total_mult *= 0.60
        elif comp < 0.5:
            penalty_details["fragmentation"] = 0.80
            total_mult *= 0.80
        else:
            penalty_details["fragmentation"] = 1.0

        total_mult = max(0.15, min(1.10, total_mult))

        # BIONIC V7 — Anthropic pressure reject (RELAXED for rural)
        urban_pen = penalty_details.get("urban", 1.0)
        roads_pen = penalty_details.get("roads", 1.0)
        infra_pen = penalty_details.get("infrastructure", 1.0)

        anthro = ANTHROPIC_THRESHOLDS_V7
        reject_reason = None

        # 1) Dense urban + roads combo
        if urban_pen < anthro["urban_roads_combo"]["urban_max"] and \
           roads_pen < anthro["urban_roads_combo"]["roads_max"]:
            reject_reason = "anthropic_urban_roads"
        # 2) Major road proximity
        elif roads_pen < anthro["major_road_alone"]["roads_max"]:
            reject_reason = "anthropic_major_road"
        # 3) Infrastructure + roads combo
        elif infra_pen < anthro["infra_roads_combo"]["infra_max"] and \
             roads_pen < anthro["infra_roads_combo"]["roads_max"]:
            reject_reason = "anthropic_infra_roads"
        # 4) Urban alone very close
        elif urban_pen < anthro["urban_alone"]["urban_max"]:
            reject_reason = "anthropic_urban_close"
        # 5) Combined pressure
        elif urban_pen * roads_pen * infra_pen < anthro["combined_product_min"]:
            reject_reason = "anthropic_combined"

        if reject_reason:
            rejected_zones.append({
                **zone,
                "rejection_reason": f"{reject_reason}_v7",
                "penalty_details": penalty_details,
            })
            stats["rejected_p0"] += 1
            continue

        # BIONIC V7 — Reject oversized zones
        if area_m2 > TRIMMING_MAX_AREA_M2_V7:
            rejected_zones.append({
                **zone,
                "rejection_reason": "oversized_v7",
                "area_m2": round(area_m2, 0),
            })
            stats["rejected_p0"] += 1
            continue

        # Build output zone
        if was_trimmed:
            new_coords = shapely_to_osm_coords(trimmed_poly)
            if len(new_coords) < 3:
                rejected_zones.append({
                    **zone,
                    "rejection_reason": "trimmed_degenerate",
                })
                stats["rejected_trimming"] += 1
                continue

            centroid = trimmed_poly.centroid
            output_zone = {
                **zone,
                "coordinates": new_coords,
                "area_m2": round(area_m2, 1),
                "compactness": round(comp, 3),
                "centroid": {"lat": centroid.y, "lng": centroid.x},
                "trimmed": True,
            }
        else:
            centroid = trimmed_poly.centroid
            output_zone = {
                **zone,
                "area_m2": round(area_m2, 1),
                "compactness": round(comp, 3),
                "centroid": {"lat": centroid.y, "lng": centroid.x},
                "trimmed": False,
            }

        output_zone["penalty_factor"] = round(total_mult, 3)
        output_zone["penalty_details"] = penalty_details
        output_zone["exclusion_engine"] = "v7"

        valid_zones.append(output_zone)
        stats["valid"] += 1

    stats["shapely_time_ms"] = round((time.time() - t0) * 1000, 1)

    logger.info(
        f"[V7-EXCL] {layer_id}: {stats['valid']} valid, "
        f"{stats['rejected_p0']} rejected P0, "
        f"{stats['rejected_trimming']} rejected trim, "
        f"{stats['trimmed']} trimmed, "
        f"{stats['shapely_time_ms']}ms "
        f"(config=V7_REDUCED)"
    )

    return valid_zones, rejected_zones, stats
