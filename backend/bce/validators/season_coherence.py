"""
BCE — Season Coherence Validator
Validates biological season configuration integrity.

Rules:
- All 5 biological seasons (pre_rut, rut, post_rut, winter, spring) are defined
- Each season has weight modifiers for all relevant layers
- Season change produces different scoring adjustments
- All weight values in valid range
"""

import logging
from typing import Dict, Any

logger = logging.getLogger("bce.season_coherence")

VALIDATOR_NAME = "season_coherence"

REQUIRED_SEASONS = {"pre_rut", "rut", "post_rut", "winter", "spring"}
CORE_LAYERS = {"habitats", "rut", "repos", "alimentation", "corridors"}


def validate() -> Dict[str, Any]:
    """Run season coherence checks."""
    checks = []
    errors = []

    try:
        from modules.bionic_engine_p0.routers.organic_zones_router import (
            BIOLOGICAL_SEASON_WEIGHTS,
        )
        from modules.bionic_engine_p0.services.species_behavior_v7 import (
            get_season_modifier,
        )
    except ImportError as e:
        return {
            "name": VALIDATOR_NAME,
            "status": "FAIL",
            "checks": [],
            "errors": [f"Import error: {e}"],
        }

    # CHECK 1: All 5 seasons defined
    defined = set(BIOLOGICAL_SEASON_WEIGHTS.keys())
    missing = REQUIRED_SEASONS - defined
    checks.append({
        "name": "all_seasons_defined",
        "status": "PASS" if not missing else "FAIL",
        "detail": f"Defined: {sorted(defined)}, Missing: {sorted(missing)}",
    })
    if missing:
        errors.append(f"Missing seasons: {sorted(missing)}")

    # CHECK 2: Each season has weights for all core layers
    incomplete = []
    for season in REQUIRED_SEASONS:
        if season not in BIOLOGICAL_SEASON_WEIGHTS:
            continue
        sw = BIOLOGICAL_SEASON_WEIGHTS[season]
        missing_layers = CORE_LAYERS - set(sw.keys())
        if missing_layers:
            incomplete.append(f"{season}: missing {sorted(missing_layers)}")

    checks.append({
        "name": "season_weights_complete",
        "status": "PASS" if not incomplete else "FAIL",
        "detail": f"{len(incomplete)} incomplete seasons",
    })
    errors.extend(incomplete)

    # CHECK 3: All weight values in valid range [0.0, 3.0]
    out_of_range = []
    for season, weights in BIOLOGICAL_SEASON_WEIGHTS.items():
        for layer, w in weights.items():
            if not (0.0 <= w <= 3.0):
                out_of_range.append(f"{season}/{layer}: {w}")

    checks.append({
        "name": "weight_values_valid_range",
        "status": "PASS" if not out_of_range else "FAIL",
        "detail": f"{len(out_of_range)} out of range",
    })
    errors.extend(out_of_range)

    # CHECK 4: Seasons produce distinct weight profiles
    # (rut season must heavily weight "rut" layer, winter must suppress it)
    distinct_violations = []
    rut_weights = BIOLOGICAL_SEASON_WEIGHTS.get("rut", {})
    winter_weights = BIOLOGICAL_SEASON_WEIGHTS.get("winter", {})
    if rut_weights.get("rut", 0) <= 1.0:
        distinct_violations.append("rut season should boost rut layer (>1.0)")
    if winter_weights.get("rut", 1) > 0.5:
        distinct_violations.append("winter season should suppress rut layer (<=0.5)")
    if winter_weights.get("repos", 0) <= 1.0:
        distinct_violations.append("winter season should boost repos layer (>1.0)")

    checks.append({
        "name": "seasons_produce_distinct_profiles",
        "status": "PASS" if not distinct_violations else "FAIL",
        "detail": "; ".join(distinct_violations) if distinct_violations else "All distinct",
    })
    errors.extend(distinct_violations)

    # CHECK 5: get_season_modifier returns valid values for all months
    modifier_ok = True
    for month in range(1, 13):
        for zone_type in ["feed", "rest", "rut"]:
            mod = get_season_modifier(zone_type, month)
            if not (0.0 <= mod <= 3.0):
                modifier_ok = False
                errors.append(f"get_season_modifier({zone_type}, month={month}) = {mod} out of range")

    checks.append({
        "name": "season_modifiers_valid",
        "status": "PASS" if modifier_ok else "FAIL",
        "detail": "All 36 modifier checks OK" if modifier_ok else "Some modifiers out of range",
    })

    status = "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL"
    return {
        "name": VALIDATOR_NAME,
        "status": status,
        "checks": checks,
        "errors": errors,
    }
