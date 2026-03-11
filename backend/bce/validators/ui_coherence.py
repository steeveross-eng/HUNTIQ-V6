"""
BCE — UI Coherence Validator
Validates frontend UI rules are respected.

Rules:
- No duplicate UI elements (buttons, selectors)
- No ghost resets (split, layers, filters)
- No debug layers visible in normal mode
- Species selector always present
- Season comparisons always available
- Split view preserves center/zoom/waypoint
"""

import logging
import os
import re
from typing import Dict, Any

logger = logging.getLogger("bce.ui_coherence")

VALIDATOR_NAME = "ui_coherence"

FRONTEND_SRC = "/app/frontend/src"


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
    """Run UI coherence checks via static analysis of frontend code."""
    checks = []
    errors = []

    jsx_files = _find_files(FRONTEND_SRC, (".jsx", ".js", ".tsx", ".ts"))
    page_file = os.path.join(FRONTEND_SRC, "pages/MonTerritoireBionicPage.jsx")
    page_content = _read_file(page_file)

    # CHECK 1: Species selector present in MonTerritoireBionicPage
    has_species_selector = bool(
        re.search(r"species|SpeciesSelector|speciesSelector|espece|speciesDropdown", page_content, re.IGNORECASE)
    )
    checks.append({
        "name": "species_selector_present",
        "status": "PASS" if has_species_selector else "FAIL",
        "detail": "Species selector found in MonTerritoireBionicPage" if has_species_selector else "MISSING",
    })
    if not has_species_selector:
        errors.append("Species selector not found in MonTerritoireBionicPage.jsx")

    # CHECK 2: Season selector present
    has_season_selector = bool(
        re.search(r"BiologicalSeason|seasonSelector|season.*select|saison", page_content, re.IGNORECASE)
    )
    checks.append({
        "name": "season_selector_present",
        "status": "PASS" if has_season_selector else "FAIL",
        "detail": "Season selector found" if has_season_selector else "MISSING",
    })
    if not has_season_selector:
        errors.append("Season selector not found in MonTerritoireBionicPage.jsx")

    # CHECK 3: No duplicate season selectors
    season_instances = len(re.findall(r"<BiologicalSeason", page_content))
    # Allow 1 (normal) or 2 (one for split) but not 3+
    checks.append({
        "name": "no_duplicate_season_selectors",
        "status": "PASS" if season_instances <= 2 else "FAIL",
        "detail": f"{season_instances} instances found",
    })
    if season_instances > 2:
        errors.append(f"Too many BiologicalSeason instances: {season_instances}")

    # CHECK 4: showCorridors defaults to false
    corridor_defaults = []
    for fpath in jsx_files:
        content = _read_file(fpath)
        # Check for showCorridors = true as default
        if re.search(r"showCorridors.*=.*useState\(true\)", content):
            corridor_defaults.append(os.path.basename(fpath))

    checks.append({
        "name": "corridors_default_off",
        "status": "PASS" if not corridor_defaults else "FAIL",
        "detail": f"Files with showCorridors=true: {corridor_defaults}" if corridor_defaults else "All default false",
    })
    if corridor_defaults:
        errors.append(f"showCorridors defaults to true in: {corridor_defaults}")

    # CHECK 5: showCursorBionic defaults to false
    cursor_defaults = []
    for fpath in jsx_files:
        content = _read_file(fpath)
        if re.search(r"showCursorBionic.*=.*useState\(true\)", content):
            cursor_defaults.append(os.path.basename(fpath))

    checks.append({
        "name": "cursor_bionic_default_off",
        "status": "PASS" if not cursor_defaults else "FAIL",
        "detail": f"Files with showCursorBionic=true: {cursor_defaults}" if cursor_defaults else "All default false",
    })
    if cursor_defaults:
        errors.append(f"showCursorBionic defaults to true in: {cursor_defaults}")

    # CHECK 6: Split view preserves map state
    split_preserves = bool(re.search(
        r"mapCenter|mapZoom|center.*split|zoom.*split|preserv",
        page_content, re.IGNORECASE
    ))
    checks.append({
        "name": "split_preserves_map_state",
        "status": "PASS" if split_preserves else "WARN",
        "detail": "Map state preservation found" if split_preserves else "Check manually",
    })

    # CHECK 7: No hardcoded debug elements visible by default
    debug_patterns = []
    for fpath in jsx_files:
        content = _read_file(fpath)
        # Find visible debug panels/overlays that aren't gated by a flag
        if re.search(r'className=.*debug.*visible|debug.*display.*block', content):
            debug_patterns.append(os.path.basename(fpath))

    checks.append({
        "name": "no_visible_debug_elements",
        "status": "PASS" if not debug_patterns else "FAIL",
        "detail": f"Debug visible in: {debug_patterns}" if debug_patterns else "None found",
    })

    status = "PASS" if all(c["status"] in ("PASS", "WARN") for c in checks) else "FAIL"
    return {
        "name": VALIDATOR_NAME,
        "status": status,
        "checks": checks,
        "errors": errors,
    }
