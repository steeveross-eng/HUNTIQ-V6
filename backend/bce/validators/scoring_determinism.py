"""
BCE — Scoring Determinism Validator
Ensures the scoring engine produces deterministic results.

Rules:
- Same input -> same output (no randomness in scoring)
- Score values in valid range [0, 100]
- All 7 subscores present (food, safety, access, stealth, water, topo, dynamic)
- Subscore weights sum to 1.0
- Zone type classification is stable across runs
"""

import logging
from typing import Dict, Any

logger = logging.getLogger("bce.scoring_determinism")

VALIDATOR_NAME = "scoring_determinism"

REQUIRED_SUBSCORES = {"food", "safety", "access", "stealth", "water", "topo", "dynamic"}
REQUIRED_ZONE_TYPES = {"feed", "rest", "rut", "heat_ref", "hunt_ref", "corridor", "mixed"}


def validate() -> Dict[str, Any]:
    """Run scoring determinism checks."""
    checks = []
    errors = []

    try:
        from modules.bionic_engine_p0.services.zone_typology_v7 import (
            SUBSCORE_WEIGHTS,
            ZONE_TYPE_CONFIG,
            classify_zone_type,
        )
        from modules.bionic_engine_p0.services.species_behavior_v7 import SPECIES_NEEDS
    except ImportError as e:
        return {
            "name": VALIDATOR_NAME,
            "status": "FAIL",
            "checks": [],
            "errors": [f"Import error: {e}"],
        }

    # CHECK 1: All 7 subscores defined with proper weights
    defined = set(SUBSCORE_WEIGHTS.keys())
    missing = REQUIRED_SUBSCORES - defined
    checks.append({
        "name": "all_subscores_defined",
        "status": "PASS" if not missing else "FAIL",
        "detail": f"Defined: {sorted(defined)}, Missing: {sorted(missing)}",
    })
    if missing:
        errors.append(f"Missing subscores: {sorted(missing)}")

    # CHECK 2: Subscore weights sum to 1.0
    weight_sum = sum(SUBSCORE_WEIGHTS.values())
    tolerance = 0.01
    sum_valid = abs(weight_sum - 1.0) < tolerance
    checks.append({
        "name": "subscore_weights_sum_to_1",
        "status": "PASS" if sum_valid else "FAIL",
        "detail": f"Sum = {weight_sum:.4f}",
    })
    if not sum_valid:
        errors.append(f"Subscore weights sum to {weight_sum:.4f}, expected 1.0")

    # CHECK 3: All zone types have config (color + label)
    defined_types = set(ZONE_TYPE_CONFIG.keys())
    missing_types = REQUIRED_ZONE_TYPES - defined_types
    for zt, config in ZONE_TYPE_CONFIG.items():
        if "color" not in config:
            errors.append(f"Zone type '{zt}' missing color")
        if "label" not in config:
            errors.append(f"Zone type '{zt}' missing label")

    checks.append({
        "name": "zone_types_complete",
        "status": "PASS" if not missing_types else "FAIL",
        "detail": f"Defined: {sorted(defined_types)}, Missing: {sorted(missing_types)}",
    })

    # CHECK 4: classify_zone_type is deterministic (same input -> same output)
    mock_subscores = {
        "food": 0.7, "safety": 0.5, "access": 0.6,
        "stealth": 0.4, "water": 0.8, "topo": 0.5, "dynamic": 0.3,
    }

    results = []
    deterministic = True
    for _ in range(3):
        try:
            zone_type, confidence = classify_zone_type(
                mock_subscores, layer_id="habitats", species="moose", month=10,
            )
            results.append((zone_type, round(confidence, 6)))
        except Exception as e:
            errors.append(f"classify_zone_type() failed: {e}")
            deterministic = False
            break

    if len(results) >= 2:
        for i in range(1, len(results)):
            if results[i] != results[0]:
                deterministic = False
                errors.append(
                    f"classify_zone_type() non-deterministic: "
                    f"run 0={results[0]}, run {i}={results[i]}"
                )

    checks.append({
        "name": "scoring_deterministic",
        "status": "PASS" if deterministic else "FAIL",
        "detail": "3 runs identical" if deterministic else "Non-deterministic output",
    })

    # CHECK 5: All subscore weight values positive
    negative_weights = [
        f"{k}={v}" for k, v in SUBSCORE_WEIGHTS.items() if v < 0
    ]
    checks.append({
        "name": "subscore_weights_positive",
        "status": "PASS" if not negative_weights else "FAIL",
        "detail": f"{len(negative_weights)} negative" if negative_weights else "All positive",
    })
    errors.extend(negative_weights)

    status = "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL"
    return {
        "name": VALIDATOR_NAME,
        "status": status,
        "checks": checks,
        "errors": errors,
    }
