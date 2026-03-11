"""
BCE — Debug Layer Guard Validator
Ensures no debug/development layers are visible in production mode.

Rules:
- showCorridors defaults to false
- showCursorBionic defaults to false
- No debug overlays visible by default
- No console.log spam in production components
- No hardcoded debug coordinates or bbox
"""

import logging
import os
import re
from typing import Dict, Any

logger = logging.getLogger("bce.debug_layer_guard")

VALIDATOR_NAME = "debug_layer_guard"

FRONTEND_SRC = "/app/frontend/src"

DEBUG_PATTERNS = {
    "debug_bbox": r"showBbox.*=.*useState\(true\)|debugBbox.*true",
    "debug_grid": r"showGrid.*=.*useState\(true\)|debugGrid.*true",
    "debug_console_log_heavy": r"console\.log\(.{0,10}DEBUG|console\.log\(.{0,10}TEST",
    "hardcoded_debug_coords": r"46\.81.*-71\.21.*debug|debug.*46\.81",
}


def _read_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return ""


def _find_files(directory: str, extensions: tuple) -> list:
    results = []
    for root, _, files in os.walk(directory):
        for fn in files:
            if fn.endswith(extensions):
                results.append(os.path.join(root, fn))
    return results


def validate() -> Dict[str, Any]:
    """Run debug layer guard checks."""
    checks = []
    errors = []

    jsx_files = _find_files(FRONTEND_SRC, (".jsx", ".js", ".tsx", ".ts"))

    # CHECK 1: No debug patterns in production code
    for pattern_name, pattern in DEBUG_PATTERNS.items():
        violations = []
        for fpath in jsx_files:
            if "node_modules" in fpath or "test" in fpath.lower():
                continue
            content = _read_file(fpath)
            if re.search(pattern, content, re.IGNORECASE):
                violations.append(os.path.basename(fpath))

        checks.append({
            "name": f"no_{pattern_name}",
            "status": "PASS" if not violations else "WARN",
            "detail": f"Found in: {violations}" if violations else "Clean",
        })
        if violations:
            errors.append(f"{pattern_name} found in: {violations}")

    # CHECK 2: MonTerritoireBionicPage debug defaults off
    page_path = os.path.join(FRONTEND_SRC, "pages/MonTerritoireBionicPage.jsx")
    page_content = _read_file(page_path)

    debug_states_on = []
    debug_state_patterns = [
        ("showCorridorsV1", r"showCorridorsV1.*useState\(true\)"),
        ("showCursorBionic", r"showCursorBionic.*useState\(true\)"),
        ("showDebugOverlay", r"showDebugOverlay.*useState\(true\)"),
        ("showBbox", r"showBbox.*useState\(true\)"),
    ]

    for name, pattern in debug_state_patterns:
        if re.search(pattern, page_content):
            debug_states_on.append(name)

    checks.append({
        "name": "main_page_debug_defaults_off",
        "status": "PASS" if not debug_states_on else "FAIL",
        "detail": f"Debug ON: {debug_states_on}" if debug_states_on else "All debug defaults OFF",
    })
    if debug_states_on:
        errors.append(f"Debug states default to true: {debug_states_on}")

    # CHECK 3: Split view hides debug elements
    split_path = os.path.join(FRONTEND_SRC, "components/territoire/map/SplitViewContainer.jsx")
    split_content = _read_file(split_path)
    split_hides_cursor = bool(re.search(r"showCursorBionic.*false", split_content))
    checks.append({
        "name": "split_view_hides_debug",
        "status": "PASS" if split_hides_cursor else "WARN",
        "detail": "Debug hidden in split" if split_hides_cursor else "Check manually",
    })

    # CHECK 4: No WMS debug layers enabled by default
    config_files = _find_files(os.path.join(FRONTEND_SRC, "config"), (".js", ".jsx"))
    wms_debug_on = []
    for fpath in config_files:
        content = _read_file(fpath)
        if re.search(r"wms.*debug.*true|ecoforest.*enabled.*true", content, re.IGNORECASE):
            wms_debug_on.append(os.path.basename(fpath))

    checks.append({
        "name": "no_wms_debug_layers",
        "status": "PASS" if not wms_debug_on else "WARN",
        "detail": f"WMS debug in: {wms_debug_on}" if wms_debug_on else "Clean",
    })

    status = "PASS" if all(c["status"] in ("PASS", "WARN") for c in checks) else "FAIL"
    return {
        "name": VALIDATOR_NAME,
        "status": status,
        "checks": checks,
        "errors": errors,
    }
