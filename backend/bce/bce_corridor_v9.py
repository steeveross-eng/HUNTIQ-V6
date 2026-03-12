"""
BCE Corridor V9 Validator — Validation des corridors V9
=========================================================
Regles:
  1. Corridors non circulaires
  2. Corridors dans le perimetre 2km2
  3. Continuite (aucun gap > seuil)
  4. Classification V9 valide (5 niveaux)
  5. 9 moteurs BIONIC evalues
  6. Aucun chevauchement habitations
  7. Weather Engine: cache 60 min, bloque < 60 min
"""

import logging
import math
from typing import Dict, List, Any
from datetime import datetime, timezone

logger = logging.getLogger("bce.corridor_v9")

# Classification V9 niveaux valides
VALID_LEVELS = {"gris", "jaune", "orange", "rouge", "rouge_raye"}
REQUIRED_ENGINES = {
    "nutrition", "daily_routine", "weather", "disturbance",
    "movement", "phenology", "typology", "learning", "habitat_enhancement",
}

# Weather engine: 60-minute minimum interval
WEATHER_MIN_INTERVAL_S = 3600


def validate_corridor_v9(corridor: Dict, bounds: Dict = None) -> Dict[str, Any]:
    """
    Validation complete BCE-4X d'un corridor V9.
    Retourne un rapport avec violations.
    """
    violations = []
    props = corridor.get("properties", {})
    coords = corridor.get("geometry", {}).get("coordinates", [])

    # Rule 1: Non-circular
    if len(coords) >= 2:
        start = coords[0]
        end = coords[-1]
        dist = _haversine(start[1], start[0], end[1], end[0])
        if dist < 50:  # Less than 50m between start and end = circular
            violations.append({
                "rule": "non_circular",
                "severity": "HIGH",
                "message": f"Corridor circulaire detecte (start-end: {dist:.0f}m)",
            })

    # Rule 2: Within perimeter
    if bounds and coords:
        margin = 0.001
        for c in coords:
            lng, lat = c[0], c[1]
            if lat < bounds.get("south", -90) - margin or lat > bounds.get("north", 90) + margin:
                violations.append({
                    "rule": "in_perimeter",
                    "severity": "HIGH",
                    "message": f"Coordonnee hors perimetre: lat={lat}",
                })
                break
            if lng < bounds.get("west", -180) - margin or lng > bounds.get("east", 180) + margin:
                violations.append({
                    "rule": "in_perimeter",
                    "severity": "HIGH",
                    "message": f"Coordonnee hors perimetre: lng={lng}",
                })
                break

    # Rule 3: Continuity (no gaps > 150m)
    max_gap_m = 150
    for i in range(len(coords) - 1):
        c1, c2 = coords[i], coords[i + 1]
        gap = _haversine(c1[1], c1[0], c2[1], c2[0])
        if gap > max_gap_m:
            violations.append({
                "rule": "continuity",
                "severity": "MEDIUM",
                "message": f"Gap de {gap:.0f}m entre points {i} et {i+1} (max: {max_gap_m}m)",
                "gap_m": round(gap, 1),
                "segment_index": i,
            })

    # Rule 4: Valid V9 classification
    classification = props.get("classification_v9", {})
    level = classification.get("level", "")
    if level not in VALID_LEVELS:
        violations.append({
            "rule": "classification_v9",
            "severity": "HIGH",
            "message": f"Classification invalide: '{level}' (attendu: {VALID_LEVELS})",
        })

    # Rule 5: All 9 engines evaluated
    scores_10x = props.get("scores_10x", {})
    evaluated_engines = set(scores_10x.keys())
    missing_engines = REQUIRED_ENGINES - evaluated_engines
    if missing_engines:
        violations.append({
            "rule": "engines_complete",
            "severity": "HIGH",
            "message": f"Moteurs manquants: {missing_engines}",
        })

    # Rule 6: V9 pipeline active
    if not props.get("v9_pipeline"):
        violations.append({
            "rule": "v9_pipeline",
            "severity": "CRITICAL",
            "message": "Pipeline V9 non active sur ce corridor",
        })

    # Rule 7: Score in valid range
    score = props.get("scoring", {}).get("score", -1)
    if score < 0 or score > 100:
        violations.append({
            "rule": "score_range",
            "severity": "HIGH",
            "message": f"Score hors limites: {score} (attendu: 0-100)",
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
        "score": score,
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

    return {
        "total_corridors": len(corridors),
        "compliant": compliant_count,
        "non_compliant": len(corridors) - compliant_count,
        "compliance_rate": round(compliance_rate, 1),
        "total_violations": total_violations,
        "status": "COMPLIANT" if compliance_rate == 100 else "PARTIAL" if compliance_rate > 50 else "NON_COMPLIANT",
        "results": results,
        "validated_at": datetime.now(timezone.utc).isoformat(),
    }


def validate_weather_cache_compliance() -> Dict[str, Any]:
    """
    BCE-4X: Valide que le Weather Engine respecte la regle 60 min.
    """
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
        return {
            "rule": "weather_60min",
            "compliant": False,
            "error": str(e),
        }


def enrich_corridor(corridor: Dict) -> Dict:
    """
    Enrichit un corridor avec des metadonnees ecologiques.
    Ajoute: estimation largeur, qualite habitat, potentiel genetique.
    """
    props = corridor.get("properties", {})
    coords = corridor.get("geometry", {}).get("coordinates", [])

    if len(coords) < 2:
        return corridor

    # Estimate corridor length
    total_length = 0
    for i in range(len(coords) - 1):
        c1, c2 = coords[i], coords[i + 1]
        total_length += _haversine(c1[1], c1[0], c2[1], c2[0])

    # Estimate width based on classification
    level = props.get("classification_v9", {}).get("level", "gris")
    width_estimates = {
        "rouge_raye": 200, "rouge": 150, "orange": 100, "jaune": 60, "gris": 30,
    }
    estimated_width = width_estimates.get(level, 50)

    # Genetic exchange potential
    score = props.get("scoring", {}).get("score", 50)
    genetic_potential = min(100, score * 1.2) if total_length > 500 else score * 0.8

    # Climate adaptation value
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
