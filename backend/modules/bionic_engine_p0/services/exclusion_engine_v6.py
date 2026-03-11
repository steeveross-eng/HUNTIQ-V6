# ══════════════════════════════════════════════════════════════
# LEGACY FIGÉ — NE PAS MODIFIER
# Remplacé par: exclusion_engine_v7.py (moteur V7 exclusif)
# Date gel: 2026-03-10
# Motif: Incident P0 — pipeline_v7 utilise exclusivement V7
# ══════════════════════════════════════════════════════════════
"""
BIONIC V6 — Exclusion Engine V6
Pipeline d'exclusion geometrique Shapely.

Remplace l'exclusion P0 multi-points et la penalite P1 centroid-only de V5
par des operations geometriques exactes:
  - P0-V6: Intersection polygon-polygon exacte avec buffers adaptatifs
  - P1-V6: Distance polygon-polygon exacte pour penalites
  - P2-V6: Zone trimming (decoupe des zones partiellement exclues)

100% independant. Orchestré par zone_engine_core_v2 via feature flag.
"""

import math
import logging
import time
from typing import Dict, List, Tuple, Any, Optional

from shapely.geometry import Polygon

from .exclusion_config_v6 import (
    INTERSECTION_THRESHOLDS_V6,
    BAND_CLOSE_M,
    BAND_MEDIUM_M,
    BAND_FAR_M,
    TRIMMING_MIN_AREA_M2,
    TRIMMING_MIN_COMPACTNESS,
    TRIMMING_MAX_AREA_M2,
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

logger = logging.getLogger("bionic_engine.exclusion_engine_v6")


def _distance_to_band(distance_m: float) -> str:
    """Convertit une distance en bande de proximite."""
    if distance_m < BAND_CLOSE_M:
        return "close"
    elif distance_m < BAND_MEDIUM_M:
        return "medium"
    elif distance_m < BAND_FAR_M:
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


def process_zones_v6(
    raw_zones: List[Dict],
    bounds: Dict[str, float],
    exclusions: List[Dict],
    layer_id: str,
    species: str = "moose",
) -> Tuple[List[Dict], List[Dict], Dict]:
    """
    Pipeline d'exclusion V6 complet.

    Etapes:
      1. Pre-traitement: construire les unions Shapely bufferisees
      2. P0-V6: exclusion geometrique exacte (intersection ratio)
      3. P2-V6: zone trimming (decoupe partielle)
      4. P1-V6: penalite distance polygon-polygon

    Args:
        raw_zones: Zones extraites par organic_zone_generator
        bounds: Viewport bounds {north, south, east, west}
        exclusions: Exclusions Overpass brutes
        layer_id: Couche BIONIC (alimentation, repos, etc.)
        species: Espece cible

    Returns:
        (valid_zones, rejected_zones, stats)
    """
    t0 = time.time()
    lat_center = _compute_lat_center(bounds)
    min_area_deg2 = _area_m2_to_deg2(TRIMMING_MIN_AREA_M2, lat_center)

    stats = {
        "engine": "v6",
        "total_raw": len(raw_zones),
        "rejected_p0": 0,
        "rejected_trimming": 0,
        "trimmed": 0,
        "valid": 0,
        "shapely_time_ms": 0,
        "exclusion_unions_built": 0,
    }

    if not raw_zones:
        return [], [], stats

    # STEP 1: Build exclusion unions (BIONIC WATER FIX: pass bounds for clipping)
    t_union = time.time()
    unions = build_exclusion_unions(exclusions, lat_center, bounds=bounds)
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

        # STEP 2+3 COMBINED: P0-V6 with integrated trimming
        # Strategy: Check overlap → if above threshold, try trimming → re-check
        exclusion_details = {}

        for ex_type in ("water", "urban", "roads", "infrastructure"):
            prep_union = unions.get(ex_type)
            if prep_union is None:
                continue
            ratio = calculate_intersection_ratio(zone_poly, prep_union)
            exclusion_details[ex_type] = round(ratio, 4)

        # Check if any type exceeds threshold
        max_violation = None
        for ex_type in ("water", "urban", "roads", "infrastructure"):
            ratio = exclusion_details.get(ex_type, 0)
            threshold = INTERSECTION_THRESHOLDS_V6.get(ex_type, 0.5)
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
                    "rejection_reason": f"p0_v6_{max_violation[0]}_after_trim",
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
                threshold = INTERSECTION_THRESHOLDS_V6.get(ex_type, 0.5)
                if new_ratio > threshold:
                    still_violated = True
                    rejected_zones.append({
                        **zone,
                        "rejection_reason": f"p0_v6_{ex_type}_post_trim",
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
            # No combined_raw to trim with, just reject
            rejected_zones.append({
                **zone,
                "rejection_reason": f"p0_v6_{max_violation[0]}",
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

        # STEP 4: P1-V6 — Penalty with exact polygon-polygon distances
        layer_penalties = PENALTY_MATRIX.get(layer_id, _DEFAULT_PENALTIES)
        penalty_details = {}
        total_mult = 1.0

        for ex_type in ("water", "urban", "roads", "infrastructure"):
            raw_union = unions.get(f"raw_{ex_type}")
            dist_deg = calculate_min_distance_deg(trimmed_poly, raw_union)
            dist_m = distance_deg_to_meters(dist_deg, lat_center)
            band = _distance_to_band(dist_m)

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

        # BIONIC V7.3 — Calibrated anthropic pressure reject
        # V7.3: Thresholds recalibrated after removing farmland from "urban".
        # Now "urban" only includes real urban landuse (residential, commercial, industrial).
        # Roads thresholds relaxed to tolerate rural country roads.
        urban_pen = penalty_details.get("urban", 1.0)
        roads_pen = penalty_details.get("roads", 1.0)
        infra_pen = penalty_details.get("infrastructure", 1.0)

        reject_reason = None
        # 1) Dense urban: urban close + roads close
        if urban_pen < 0.50 and roads_pen < 0.55:
            reject_reason = "anthropic_urban_roads"
        # 2) Major road proximity: roads very close (highway/motorway)
        elif roads_pen < 0.35:
            reject_reason = "anthropic_major_road"
        # 3) Infrastructure + roads combo (interchange, industrial)
        elif infra_pen < 0.45 and roads_pen < 0.55:
            reject_reason = "anthropic_infra_roads"
        # 4) Urban alone very close
        elif urban_pen < 0.35:
            reject_reason = "anthropic_urban_close"
        # 5) Combined anthropic pressure (product of all penalties)
        elif urban_pen * roads_pen * infra_pen < 0.15:
            reject_reason = "anthropic_combined"

        if reject_reason:
            rejected_zones.append({
                **zone,
                "rejection_reason": f"{reject_reason}_v72",
                "penalty_details": penalty_details,
            })
            stats["rejected_p0"] += 1
            continue

        # BIONIC V7.2 — Reject chaotic / oversized zones
        if area_m2 > TRIMMING_MAX_AREA_M2:
            rejected_zones.append({
                **zone,
                "rejection_reason": "oversized_v72",
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
        output_zone["exclusion_engine"] = "v6"

        valid_zones.append(output_zone)
        stats["valid"] += 1

    stats["shapely_time_ms"] = round((time.time() - t0) * 1000, 1)

    logger.info(
        f"[V6] {layer_id}: {stats['valid']} valid, "
        f"{stats['rejected_p0']} rejected P0, "
        f"{stats['rejected_trimming']} rejected trim, "
        f"{stats['trimmed']} trimmed, "
        f"{stats['shapely_time_ms']}ms"
    )

    return valid_zones, rejected_zones, stats
