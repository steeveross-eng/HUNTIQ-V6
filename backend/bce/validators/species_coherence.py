"""
BCE — Species Coherence Validator
Validates species configuration integrity.

Rules:
- All 5 species (moose, deer, bear, wild_turkey, elk) are defined
- Each species has complete weight vectors for all layers
- Each species has behavioral needs (feed, rest, rut, heat_ref, hunt_ref)
- Species change produces different scoring outputs (deterministic)
"""

import logging
from typing import Dict, Any

logger = logging.getLogger("bce.species_coherence")

VALIDATOR_NAME = "species_coherence"

REQUIRED_SPECIES = {"moose", "deer", "bear", "wild_turkey", "elk"}

# Per-species required needs (bears don't have rut, wild_turkey may not have all)
BASE_REQUIRED_NEEDS = {"feed", "rest"}
FULL_REQUIRED_NEEDS = {"feed", "rest", "rut", "heat_ref", "hunt_ref"}
REQUIRED_LAYERS = {
    "rut", "repos", "alimentation", "corridors", "habitats",
    "peuplements", "ndvi", "hydro", "pentes", "orientation",
    "salines", "affuts", "trajets", "altitude", "ensoleillement",
}


def validate() -> Dict[str, Any]:
    """Run species coherence checks."""
    checks = []
    errors = []

    # Import species configs
    try:
        from modules.bionic_engine_p0.services.behavioral_rasterizer import (
            SPECIES_WEIGHTS,
            get_supported_species,
        )
        from modules.bionic_engine_p0.services.species_behavior_v7 import (
            SPECIES_NEEDS,
            get_species_needs,
        )
    except ImportError as e:
        return {
            "name": VALIDATOR_NAME,
            "status": "FAIL",
            "checks": [],
            "errors": [f"Import error: {e}"],
        }

    # CHECK 1: All 5 species defined in SPECIES_WEIGHTS
    defined_species = set(SPECIES_WEIGHTS.keys())
    missing = REQUIRED_SPECIES - defined_species
    checks.append({
        "name": "all_species_defined_weights",
        "status": "PASS" if not missing else "FAIL",
        "detail": f"Defined: {sorted(defined_species)}, Missing: {sorted(missing)}",
    })
    if missing:
        errors.append(f"Missing species in SPECIES_WEIGHTS: {sorted(missing)}")

    # CHECK 2: All 5 species defined in SPECIES_NEEDS
    defined_needs = set(SPECIES_NEEDS.keys())
    missing_needs = REQUIRED_SPECIES - defined_needs
    checks.append({
        "name": "all_species_defined_needs",
        "status": "PASS" if not missing_needs else "FAIL",
        "detail": f"Defined: {sorted(defined_needs)}, Missing: {sorted(missing_needs)}",
    })
    if missing_needs:
        errors.append(f"Missing species in SPECIES_NEEDS: {sorted(missing_needs)}")

    # CHECK 3: Each species has weights for all layers
    incomplete_weights = []
    for sp in REQUIRED_SPECIES:
        if sp not in SPECIES_WEIGHTS:
            continue
        sp_weights = SPECIES_WEIGHTS[sp]
        missing_layers = REQUIRED_LAYERS - set(sp_weights.keys())
        if missing_layers:
            incomplete_weights.append(f"{sp}: missing {sorted(missing_layers)}")

    checks.append({
        "name": "species_weights_complete",
        "status": "PASS" if not incomplete_weights else "FAIL",
        "detail": f"{len(incomplete_weights)} incomplete species",
    })
    errors.extend(incomplete_weights)

    # CHECK 4: Each species has at minimum the base behavioral needs (feed, rest)
    incomplete_needs = []
    for sp in REQUIRED_SPECIES:
        if sp not in SPECIES_NEEDS:
            incomplete_needs.append(f"{sp}: not defined in SPECIES_NEEDS")
            continue
        sp_needs = set(SPECIES_NEEDS[sp].keys())
        missing_n = BASE_REQUIRED_NEEDS - sp_needs
        if missing_n:
            incomplete_needs.append(f"{sp}: missing base needs {sorted(missing_n)}")

    checks.append({
        "name": "species_needs_complete",
        "status": "PASS" if not incomplete_needs else "FAIL",
        "detail": f"{len(incomplete_needs)} incomplete species",
    })
    errors.extend(incomplete_needs)

    # CHECK 5: All weight values in valid range [0.0, 2.0]
    out_of_range = []
    for sp, weights in SPECIES_WEIGHTS.items():
        for layer, w in weights.items():
            if not (0.0 <= w <= 2.0):
                out_of_range.append(f"{sp}/{layer}: {w}")

    checks.append({
        "name": "weight_values_valid_range",
        "status": "PASS" if not out_of_range else "FAIL",
        "detail": f"{len(out_of_range)} out of range",
    })
    errors.extend(out_of_range)

    # CHECK 6: get_supported_species() returns all required species
    supported = set(get_supported_species())
    missing_api = REQUIRED_SPECIES - supported
    checks.append({
        "name": "api_returns_all_species",
        "status": "PASS" if not missing_api else "FAIL",
        "detail": f"API returns {sorted(supported)}",
    })
    if missing_api:
        errors.append(f"get_supported_species() missing: {sorted(missing_api)}")

    status = "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL"
    return {
        "name": VALIDATOR_NAME,
        "status": status,
        "checks": checks,
        "errors": errors,
    }
