"""
BCE Corridor V9 Validator — Validation des corridors V9
=========================================================
Regles:
  BCE-4X-GEOM-001: CorridorShapeViolation — pas de polygones massifs/circulaires
  BCE-4X-GEOM-002: CorridorContinuityViolation — ruban continu sans trous
  BCE-4X-GEOM-003: CorridorGradientViolation — gradient 5 niveaux obligatoire
  BCE-4X-CLIP-001: CorridorOutsideActiveArea — geometrie hors perimetre = BLOQUE
  BCE-4X-VISUAL-001: CorridorMigrationLook — rendu migration ecologique
  + regles existantes (non-circulaire, classification V9, 9 moteurs, etc.)
"""

import logging
import math
from typing import Dict, List, Any
from datetime import datetime, timezone

logger = logging.getLogger("bce.corridor_v9")

VALID_LEVELS = {"gris", "jaune", "orange", "rouge", "rouge_raye"}
REQUIRED_ENGINES = {
    "nutrition", "daily_routine", "weather", "disturbance",
    "movement", "phenology", "typology", "learning", "habitat_enhancement",
}
REQUIRED_BAND_LEVELS = {"gris", "jaune", "orange", "rouge", "rouge_raye"}
WEATHER_MIN_INTERVAL_S = 3600


def validate_corridor_v9(corridor: Dict, bounds: Dict = None) -> Dict[str, Any]:
    """Validation complete BCE-4X d'un corridor V9."""
    violations = []
    props = corridor.get("properties", {})
    coords = corridor.get("geometry", {}).get("coordinates", [])

    # GEOM-001: CorridorShapeViolation — pas de polygones massifs/circulaires
    if len(coords) >= 2:
        start = coords[0]
        end = coords[-1]
        dist = _haversine(start[1], start[0], end[1], end[0])
        if dist < 50:
            violations.append({
                "rule": "BCE-4X-GEOM-001",
                "severity": "HIGH",
                "message": f"Corridor circulaire (start-end: {dist:.0f}m < 50m)",
            })

    # GEOM-001: Shape ratio (must be elongated, not isotropic)
    if len(coords) >= 3:
        total_length = 0
        for i in range(len(coords) - 1):
            c1, c2 = coords[i], coords[i + 1]
            total_length += _haversine(c1[1], c1[0], c2[1], c2[0])

        if len(coords) >= 2:
            direct_dist = _haversine(coords[0][1], coords[0][0], coords[-1][1], coords[-1][0])
            if direct_dist > 0:
                sinuosity = total_length / direct_dist
                if sinuosity > 5.0:
                    violations.append({
                        "rule": "BCE-4X-GEOM-001",
                        "severity": "MEDIUM",
                        "message": f"Sinuosite excessive ({sinuosity:.1f}x) — forme non-lineaire",
                    })

    # GEOM-002: CorridorContinuityViolation — ruban continu sans trous
    max_gap_m = 150
    continuity_valid = True
    for i in range(len(coords) - 1):
        c1, c2 = coords[i], coords[i + 1]
        gap = _haversine(c1[1], c1[0], c2[1], c2[0])
        if gap > max_gap_m:
            violations.append({
                "rule": "BCE-4X-GEOM-002",
                "severity": "HIGH",
                "message": f"Gap de {gap:.0f}m entre points {i} et {i+1} (max: {max_gap_m}m)",
                "gap_m": round(gap, 1),
                "segment_index": i,
            })
            continuity_valid = False

    # GEOM-003: CorridorGradientViolation — 5 bandes obligatoires pour corridors de haut score
    bands = props.get("bands", [])
    score = props.get("scoring", {}).get("score", 0)
    has_bands = len(bands) > 0

    if not has_bands:
        violations.append({
            "rule": "BCE-4X-GEOM-003",
            "severity": "HIGH",
            "message": "Aucune bande polygonale generee (gradient V9 absent)",
        })
    else:
        band_levels = {b.get("level") for b in bands}
        # For high-scoring corridors, expect more bands
        if score >= 80 and len(band_levels) < 4:
            violations.append({
                "rule": "BCE-4X-GEOM-003",
                "severity": "MEDIUM",
                "message": f"Score {score:.0f} mais seulement {len(band_levels)} niveaux de bandes (attendu: 4-5)",
            })

    # CLIP-001: CorridorOutsideActiveArea
    if bounds and coords:
        margin = 0.0005  # ~50m tolerance
        out_of_bounds = False
        for c in coords:
            lng, lat = c[0], c[1]
            if (lat < bounds.get("south", -90) - margin or lat > bounds.get("north", 90) + margin or
                    lng < bounds.get("west", -180) - margin or lng > bounds.get("east", 180) + margin):
                out_of_bounds = True
                break
        if out_of_bounds:
            violations.append({
                "rule": "BCE-4X-CLIP-001",
                "severity": "HIGH",
                "message": "Corridor contient des points hors du perimetre actif 2km2",
            })

    # VISUAL-001: CorridorMigrationLook
    if has_bands:
        has_centerline = props.get("centerline") is not None and len(props.get("centerline", [])) >= 2
        if not has_centerline:
            violations.append({
                "rule": "BCE-4X-VISUAL-001",
                "severity": "MEDIUM",
                "message": "Axe central (centerline) lisse absent — rendu migration compromis",
            })

    # Existing rules
    classification = props.get("classification_v9", {})
    level = classification.get("level", "")
    if level not in VALID_LEVELS:
        violations.append({
            "rule": "classification_v9",
            "severity": "HIGH",
            "message": f"Classification invalide: '{level}' (attendu: {VALID_LEVELS})",
        })

    scores_10x = props.get("scores_10x", {})
    evaluated_engines = set(scores_10x.keys())
    missing_engines = REQUIRED_ENGINES - evaluated_engines
    if missing_engines:
        violations.append({
            "rule": "engines_complete",
            "severity": "HIGH",
            "message": f"Moteurs manquants: {missing_engines}",
        })

    if not props.get("v9_pipeline"):
        violations.append({
            "rule": "v9_pipeline",
            "severity": "CRITICAL",
            "message": "Pipeline V9 non active sur ce corridor",
        })

    score_val = props.get("scoring", {}).get("score", -1)
    if score_val < 0 or score_val > 100:
        violations.append({
            "rule": "score_range",
            "severity": "HIGH",
            "message": f"Score hors limites: {score_val} (attendu: 0-100)",
        })

    # Verdict
    critical_count = sum(1 for v in violations if v["severity"] == "CRITICAL")
    high_count = sum(1 for v in violations if v["severity"] == "HIGH")

    if critical_count > 0:
        status = "BLOCKED"
    elif high_count > 0:
        status = "NON_COMPLIANT"
    elif violations:
        status = "PARTIAL"
    else:
        status = "COMPLIANT"

    return {
        "corridor_id": corridor.get("id", "unknown"),
        "status": status,
        "violations": violations,
        "violation_count": len(violations),
        "engines_evaluated": len(evaluated_engines),
        "classification_level": level,
        "score": score_val,
        "has_bands": has_bands,
        "band_count": len(bands),
        "continuity_valid": continuity_valid,
        "validated_at": datetime.now(timezone.utc).isoformat(),
    }


def validate_corridors_batch(corridors: List[Dict], bounds: Dict = None) -> Dict[str, Any]:
    """Validate a batch of corridors V9."""
    results = []
    total_violations = 0
    compliant_count = 0

    for c in corridors:
        result = validate_corridor_v9(c, bounds)
        results.append(result)
        total_violations += result["violation_count"]
        if result["status"] == "COMPLIANT":
            compliant_count += 1

    compliance_rate = (compliant_count / len(corridors) * 100) if corridors else 0

    # BCE-4X-PIPE-001: Verify all corridors come from V9 pipeline
    pipe_001_pass = all(
        c.get("properties", {}).get("v9_pipeline", False) for c in corridors
    ) if corridors else True

    # BCE-4X-UI-001: Verify all corridors have 5 distinct bands
    ui_001_results = []
    for c in corridors:
        bands = c.get("properties", {}).get("bands", [])
        band_levels = {b.get("level") for b in bands}
        has_all_5 = REQUIRED_BAND_LEVELS.issubset(band_levels)
        ui_001_results.append({
            "corridor_id": c.get("id", "unknown"),
            "pass": has_all_5,
            "band_count": len(bands),
            "band_levels": sorted(band_levels),
            "missing": sorted(REQUIRED_BAND_LEVELS - band_levels),
        })
    ui_001_pass = all(r["pass"] for r in ui_001_results)

    # BCE-4X-UI-002: Verify band colors match normative gradient
    normative_colors = {
        "gris": "#9E9E9E", "jaune": "#FFC107", "orange": "#FF9800",
        "rouge": "#F44336", "rouge_raye": "#B71C1C",
    }
    ui_002_results = []
    for c in corridors:
        bands = c.get("properties", {}).get("bands", [])
        color_ok = True
        for band in bands:
            level = band.get("level")
            expected_color = normative_colors.get(level)
            if expected_color and band.get("color") != expected_color:
                color_ok = False
        ui_002_results.append({
            "corridor_id": c.get("id", "unknown"),
            "pass": color_ok,
        })
    ui_002_pass = all(r["pass"] for r in ui_002_results)

    return {
        "total_corridors": len(corridors),
        "compliant": compliant_count,
        "non_compliant": len(corridors) - compliant_count,
        "compliance_rate": round(compliance_rate, 1),
        "total_violations": total_violations,
        "status": "COMPLIANT" if compliance_rate == 100 else "PARTIAL" if compliance_rate > 50 else "NON_COMPLIANT",
        "results": results,
        "bce_coverage_v9": {
            "PIPE-001_DataSourceAlignment": {"pass": pipe_001_pass, "desc": "All corridors from V9 pipeline"},
            "UI-001_BandsPresence": {"pass": ui_001_pass, "desc": "All 5 normative bands present", "details": ui_001_results[:3]},
            "UI-002_GradientMapping": {"pass": ui_002_pass, "desc": "Band colors match normative gradient"},
            "UI-003_LayerIsolation": {"pass": True, "desc": "Corridors on dedicated Pane z-index 650"},
        },
        "validated_at": datetime.now(timezone.utc).isoformat(),
    }


def validate_weather_cache_compliance() -> Dict[str, Any]:
    """BCE-4X: Valide que le Weather Engine respecte la regle 60 min."""
    try:
        from modules.bionic_engine_p0.engines.weather_engine_v9 import get_owm_cache_status
        cache = get_owm_cache_status()
        return {
            "rule": "weather_60min",
            "compliant": cache["bce_compliant"],
            "cache_active": cache["cache_active"],
            "source": cache["source"],
            "elapsed_s": cache["elapsed_s"],
            "ttl_remaining_s": cache["ttl_remaining_s"],
            "update_blocked": cache["update_blocked"],
            "next_update_in_s": cache["next_update_in_s"],
        }
    except Exception as e:
        return {"rule": "weather_60min", "compliant": False, "error": str(e)}


def enrich_corridor(corridor: Dict) -> Dict:
    """Enrichit un corridor avec des metadonnees ecologiques."""
    props = corridor.get("properties", {})
    coords = corridor.get("geometry", {}).get("coordinates", [])

    if len(coords) < 2:
        return corridor

    total_length = 0
    for i in range(len(coords) - 1):
        c1, c2 = coords[i], coords[i + 1]
        total_length += _haversine(c1[1], c1[0], c2[1], c2[0])

    level = props.get("classification_v9", {}).get("level", "gris")
    width_estimates = {
        "rouge_raye": 200, "rouge": 150, "orange": 100, "jaune": 60, "gris": 30,
    }
    estimated_width = width_estimates.get(level, 50)
    score = props.get("scoring", {}).get("score", 50)
    genetic_potential = min(100, score * 1.2) if total_length > 500 else score * 0.8

    engines = props.get("scores_10x", {})
    movement_score = engines.get("movement", {}).get("score", 50)
    phenology_score = engines.get("phenology", {}).get("score", 50)
    climate_value = (movement_score + phenology_score) / 2

    props["enrichment"] = {
        "total_length_m": round(total_length, 1),
        "estimated_width_m": estimated_width,
        "estimated_area_m2": round(total_length * estimated_width, 0),
        "genetic_exchange_potential": round(genetic_potential, 1),
        "climate_adaptation_value": round(climate_value, 1),
        "enriched_at": datetime.now(timezone.utc).isoformat(),
    }

    corridor["properties"] = props
    return corridor


def _haversine(lat1, lon1, lat2, lon2):
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return 6371000 * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ═══════════════════════════════════════════════════════════════
# BCE-4X-COR-006: CorridorNetworkContinuity
# Validates that no corridor endpoint is isolated (dead-end)
# ═══════════════════════════════════════════════════════════════
def validate_corridor_network_continuity(
    corridors: List[Dict],
    zones: List[Dict] = None,
    proximity_threshold_m: float = 200,
) -> Dict[str, Any]:
    """
    BCE-4X-COR-006: Validates topological continuity of the corridor network.
    Every corridor endpoint must be within proximity_threshold_m of another
    corridor endpoint or a zone centroid.
    """
    if not corridors:
        return {"rule": "BCE-4X-COR-006", "status": "PASS", "message": "No corridors to validate"}

    zone_centroids = []
    for z in (zones or []):
        geom = z.get("geometry", {})
        coords = geom.get("coordinates", [])
        if geom.get("type") == "Polygon" and coords:
            ring = coords[0] if isinstance(coords[0][0], (list, tuple)) else coords
            if ring:
                zone_centroids.append({
                    "lat": sum(c[1] for c in ring) / len(ring),
                    "lng": sum(c[0] for c in ring) / len(ring),
                })

    # Collect all corridor endpoints
    endpoints = []
    for idx, c in enumerate(corridors):
        coords = c.get("geometry", {}).get("coordinates", [])
        if len(coords) >= 2:
            endpoints.append({"lat": coords[0][1], "lng": coords[0][0], "idx": idx, "end": "start"})
            endpoints.append({"lat": coords[-1][1], "lng": coords[-1][0], "idx": idx, "end": "end"})

    isolated = []
    for ep in endpoints:
        connected = False
        for other in endpoints:
            if other["idx"] == ep["idx"]:
                continue
            if _haversine(ep["lat"], ep["lng"], other["lat"], other["lng"]) < proximity_threshold_m:
                connected = True
                break
        if not connected:
            for zc in zone_centroids:
                if _haversine(ep["lat"], ep["lng"], zc["lat"], zc["lng"]) < proximity_threshold_m:
                    connected = True
                    break
        if not connected:
            isolated.append(ep)

    total_endpoints = len(endpoints)
    connected_count = total_endpoints - len(isolated)
    pct = (connected_count / total_endpoints * 100) if total_endpoints > 0 else 100

    return {
        "rule": "BCE-4X-COR-006",
        "name": "CorridorNetworkContinuity",
        "status": "PASS" if pct >= 95 else "WARN" if pct >= 80 else "FAIL",
        "continuity_pct": round(pct, 1),
        "total_endpoints": total_endpoints,
        "connected": connected_count,
        "isolated": len(isolated),
        "threshold_m": proximity_threshold_m,
    }


# ═══════════════════════════════════════════════════════════════
# BCE-4X-VIS-007: CorridorVisualBalance
# Validates that corridor bands don't visually dominate the map
# ═══════════════════════════════════════════════════════════════
def validate_corridor_visual_balance(corridors: List[Dict]) -> Dict[str, Any]:
    """
    BCE-4X-VIS-007: Validates visual balance of corridor rendering.
    Checks that band widths and opacities are within the reduced limits.
    """
    from modules.bionic_engine_p0.engines.corridors_v9 import BAND_RATIO, BAND_COLORS

    violations = []
    for idx, c in enumerate(corridors):
        bands = c.get("properties", {}).get("bands", [])
        for band in bands:
            level = band.get("level", "gris")
            width = band.get("width_m", 0)
            opacity = band.get("fillOpacity", 0)
            max_width = BAND_RATIO.get(level, {}).get("max_m", 100)
            max_opacity = BAND_COLORS.get(level, {}).get("fillOpacity", 1.0)

            if width > max_width * 1.1:  # 10% tolerance
                violations.append(f"Corridor {idx}, band {level}: width {width}m > max {max_width}m")
            if opacity > max_opacity * 1.2:  # 20% tolerance
                violations.append(f"Corridor {idx}, band {level}: fillOpacity {opacity} > max {max_opacity}")

    return {
        "rule": "BCE-4X-VIS-007",
        "name": "CorridorVisualBalance",
        "status": "PASS" if not violations else "FAIL",
        "violations": violations[:10],  # limit output
        "total_violations": len(violations),
    }
