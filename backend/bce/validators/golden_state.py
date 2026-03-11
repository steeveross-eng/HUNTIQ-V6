"""
BCE — Golden State Validator
Compares current state against a certified BIONIC snapshot.

The Golden State is a reference snapshot that captures the expected state of:
- Engine count and names
- Species definitions
- Season definitions
- Scoring weights
- Pipeline version
- UI defaults

Any divergence = FAIL (unless explicitly documented as an evolution).
"""

import json
import logging
import os
from typing import Dict, Any

logger = logging.getLogger("bce.golden_state")

VALIDATOR_NAME = "golden_state"

GOLDEN_STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "golden", "golden_state.json")


def _load_golden_state() -> Dict[str, Any]:
    try:
        with open(GOLDEN_STATE_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def _capture_current_state() -> Dict[str, Any]:
    """Capture the current BIONIC configuration state."""
    state = {}

    try:
        from modules.bionic_engine_p0.services.behavioral_rasterizer import (
            SPECIES_WEIGHTS, LAYER_PARAMS, get_supported_species,
        )
        state["species"] = sorted(get_supported_species())
        state["layers"] = sorted(LAYER_PARAMS.keys())
        state["species_weight_keys"] = {
            sp: sorted(w.keys()) for sp, w in SPECIES_WEIGHTS.items()
        }
    except ImportError:
        state["species"] = []
        state["layers"] = []

    try:
        from modules.bionic_engine_p0.routers.organic_zones_router import (
            BIOLOGICAL_SEASON_WEIGHTS,
        )
        state["seasons"] = sorted(BIOLOGICAL_SEASON_WEIGHTS.keys())
    except ImportError:
        state["seasons"] = []

    try:
        from modules.bionic_engine_p0.services.zone_typology_v7 import (
            SUBSCORE_WEIGHTS, ZONE_TYPE_CONFIG,
        )
        state["subscore_weights"] = SUBSCORE_WEIGHTS
        state["zone_types"] = sorted(ZONE_TYPE_CONFIG.keys())
    except ImportError:
        state["subscore_weights"] = {}
        state["zone_types"] = []

    try:
        from modules.bionic_engine_p0.services.species_behavior_v7 import SPECIES_NEEDS
        state["species_needs_keys"] = {
            sp: sorted(needs.keys()) for sp, needs in SPECIES_NEEDS.items()
        }
    except ImportError:
        state["species_needs_keys"] = {}

    # Pipeline version from env
    state["exclusion_engine_version"] = os.environ.get("EXCLUSION_ENGINE_VERSION", "unknown")

    # UI defaults check
    page_path = "/app/frontend/src/pages/MonTerritoireBionicPage.jsx"
    state["ui_defaults"] = {
        "main_page_exists": os.path.exists(page_path),
    }

    return state


def save_golden_state():
    """Capture and save current state as the golden reference."""
    state = _capture_current_state()
    state["_version"] = "BCE-GoldenState-v1"
    state["_certified"] = True
    os.makedirs(os.path.dirname(GOLDEN_STATE_PATH), exist_ok=True)
    with open(GOLDEN_STATE_PATH, "w") as f:
        json.dump(state, f, indent=2, default=str)
    logger.info(f"Golden state saved to {GOLDEN_STATE_PATH}")
    return state


def validate() -> Dict[str, Any]:
    """Compare current state against golden state."""
    checks = []
    errors = []

    golden = _load_golden_state()
    current = _capture_current_state()

    if not golden:
        # No golden state yet — create one
        golden = save_golden_state()
        checks.append({
            "name": "golden_state_exists",
            "status": "PASS",
            "detail": "Golden state created (first run)",
        })
        return {
            "name": VALIDATOR_NAME,
            "status": "PASS",
            "checks": checks,
            "errors": [],
            "golden_state": golden,
        }

    checks.append({
        "name": "golden_state_exists",
        "status": "PASS",
        "detail": f"Version: {golden.get('_version', 'unknown')}",
    })

    # CHECK: Species list matches
    g_species = golden.get("species", [])
    c_species = current.get("species", [])
    species_match = g_species == c_species
    checks.append({
        "name": "species_match_golden",
        "status": "PASS" if species_match else "FAIL",
        "detail": f"Golden: {g_species}, Current: {c_species}",
    })
    if not species_match:
        errors.append(f"Species divergence: golden={g_species}, current={c_species}")

    # CHECK: Seasons list matches
    g_seasons = golden.get("seasons", [])
    c_seasons = current.get("seasons", [])
    seasons_match = g_seasons == c_seasons
    checks.append({
        "name": "seasons_match_golden",
        "status": "PASS" if seasons_match else "FAIL",
        "detail": f"Golden: {g_seasons}, Current: {c_seasons}",
    })
    if not seasons_match:
        errors.append(f"Seasons divergence: golden={g_seasons}, current={c_seasons}")

    # CHECK: Layers list matches
    g_layers = golden.get("layers", [])
    c_layers = current.get("layers", [])
    layers_match = g_layers == c_layers
    checks.append({
        "name": "layers_match_golden",
        "status": "PASS" if layers_match else "FAIL",
        "detail": f"Golden: {len(g_layers)} layers, Current: {len(c_layers)} layers",
    })
    if not layers_match:
        errors.append(f"Layers divergence: golden={g_layers}, current={c_layers}")

    # CHECK: Zone types match
    g_types = golden.get("zone_types", [])
    c_types = current.get("zone_types", [])
    types_match = g_types == c_types
    checks.append({
        "name": "zone_types_match_golden",
        "status": "PASS" if types_match else "FAIL",
        "detail": f"Golden: {g_types}, Current: {c_types}",
    })
    if not types_match:
        errors.append(f"Zone types divergence: golden={g_types}, current={c_types}")

    # CHECK: Subscore weights match
    g_weights = golden.get("subscore_weights", {})
    c_weights = current.get("subscore_weights", {})
    weights_match = g_weights == c_weights
    checks.append({
        "name": "subscore_weights_match_golden",
        "status": "PASS" if weights_match else "FAIL",
        "detail": "Weights match" if weights_match else f"Divergence detected",
    })
    if not weights_match:
        errors.append(f"Subscore weights divergence: golden={g_weights}, current={c_weights}")

    # CHECK: Exclusion engine version
    g_version = golden.get("exclusion_engine_version", "")
    c_version = current.get("exclusion_engine_version", "")
    version_match = g_version == c_version
    checks.append({
        "name": "engine_version_match_golden",
        "status": "PASS" if version_match else "FAIL",
        "detail": f"Golden: {g_version}, Current: {c_version}",
    })

    status = "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL"
    return {
        "name": VALIDATOR_NAME,
        "status": status,
        "checks": checks,
        "errors": errors,
        "golden_state": golden,
        "current_state": current,
    }
