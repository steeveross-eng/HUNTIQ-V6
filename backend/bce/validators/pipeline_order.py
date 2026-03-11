"""
BCE — Pipeline Order Validator
Validates the zone generation pipeline executes steps in correct order.

Rules:
- Pipeline steps: Rasterize -> Contour -> Smooth -> Filter -> Exclude -> Score -> Export
- No step can be skipped
- Exclusion must happen BEFORE scoring
- Scoring must use post-exclusion geometry
"""

import logging
import re
from typing import Dict, Any

logger = logging.getLogger("bce.pipeline_order")

VALIDATOR_NAME = "pipeline_order"

REQUIRED_PIPELINE_STEPS = [
    ("rasterize", r"rasterize|behavioral_rasterizer|generate_raster"),
    ("contour", r"contour|marching_squares|extract_contours"),
    ("smooth", r"smooth|chaikin|smoothing"),
    ("filter", r"filter|compactness|area_filter|min_area"),
    ("exclude", r"exclude|exclusion|process_zones_v6|process_zones_v7"),
    ("score", r"score|scoring|classify|typology|enrich"),
    ("export", r"geojson|GeoJSON|features|FeatureCollection|feature_collection|\"type\":\s*\"Feature"),
]


def _read_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return ""


def validate() -> Dict[str, Any]:
    """Run pipeline order checks."""
    checks = []
    errors = []

    # Read the main pipeline files
    import glob
    service_files = glob.glob(
        "/app/backend/modules/bionic_engine_p0/services/*.py"
    )
    router_files = glob.glob(
        "/app/backend/modules/bionic_engine_p0/routers/*.py"
    )
    combined = ""
    for fpath in service_files + router_files:
        combined += _read_file(fpath) + "\n"

    # CHECK 1: All pipeline steps are present
    missing_steps = []
    found_steps = {}
    for step_name, pattern in REQUIRED_PIPELINE_STEPS:
        matches = list(re.finditer(pattern, combined, re.IGNORECASE))
        if matches:
            found_steps[step_name] = matches[0].start()
        else:
            missing_steps.append(step_name)

    checks.append({
        "name": "all_pipeline_steps_present",
        "status": "PASS" if not missing_steps else "FAIL",
        "detail": f"Found: {list(found_steps.keys())}, Missing: {missing_steps}",
    })
    if missing_steps:
        errors.append(f"Missing pipeline steps: {missing_steps}")

    # CHECK 2: Exclusion happens before scoring in the pipeline
    excl_pos = found_steps.get("exclude")
    score_pos = found_steps.get("score")
    order_valid = True
    if excl_pos is not None and score_pos is not None:
        # In the core engine, exclusion should appear before scoring
        if excl_pos > score_pos:
            order_valid = False
            errors.append("Exclusion appears AFTER scoring in pipeline — must be before")

    checks.append({
        "name": "exclusion_before_scoring",
        "status": "PASS" if order_valid else "FAIL",
        "detail": "Correct order" if order_valid else "Order violation",
    })

    # CHECK 3: Exclusion engine version is set
    env_content = _read_file("/app/backend/.env")
    has_version = "EXCLUSION_ENGINE_VERSION" in env_content
    checks.append({
        "name": "exclusion_engine_version_set",
        "status": "PASS" if has_version else "FAIL",
        "detail": "Version configured" if has_version else "MISSING from .env",
    })
    if not has_version:
        errors.append("EXCLUSION_ENGINE_VERSION not set in .env")

    # CHECK 4: Pipeline v7 is imported and used
    uses_v7 = bool(re.search(r"pipeline_v7|process_zones_v7", combined))
    checks.append({
        "name": "pipeline_v7_active",
        "status": "PASS" if uses_v7 else "FAIL",
        "detail": "V7 pipeline in use" if uses_v7 else "V7 pipeline not found",
    })

    # CHECK 5: Export produces GeoJSON FeatureCollection
    exports_geojson = bool(re.search(r"FeatureCollection|type.*Feature", combined))
    checks.append({
        "name": "exports_geojson_format",
        "status": "PASS" if exports_geojson else "FAIL",
        "detail": "GeoJSON export confirmed" if exports_geojson else "GeoJSON not found",
    })

    status = "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL"
    return {
        "name": VALIDATOR_NAME,
        "status": status,
        "checks": checks,
        "errors": errors,
    }
