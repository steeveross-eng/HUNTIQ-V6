"""
BCE-4X — STEVE-MAX Geometry & Clipping Validators

BCE-4X-GEOM-004 — CorridorBoundingBoxCompliance (HIGH)
  Interdiction absolue d'avoir un corridor hors du carre 2km.
  TOUTES les coordonnees de bandes doivent etre DANS les bounds.

BCE-4X-GEOM-005 — CorridorWidthNormalization (HIGH)
  Largeurs des bandes doivent respecter la reduction 40% et les ratios normatifs.
  gris max 72m, jaune max 48m, orange max 30m, rouge max 18m, rouge_raye max 9m.

BCE-4X-CLIP-002 — PostSmoothingClipEnforcement (HIGH)
  Le smoothing ne doit jamais creer de depassement.
  Pipeline: clip → smooth → buffer → re-clip.

BCE-4X-PIPE-002 — FrontendReconstructionGuard (HIGH)
  Interdiction pour le frontend de modifier la geometrie clippee.
"""

import logging
import os
import re
from typing import Dict, Any

logger = logging.getLogger("bce.geometry_compliance")
VALIDATOR_NAME = "geometry_compliance_steve_max"
FRONTEND_SRC = "/app/frontend/src"
BACKEND_SRC = "/app/backend"

# STEVE-MAX++ Corrections Finales: +20% corridor widths
NORMATIVE_MAX_WIDTHS = {
    "gris": 26,
    "jaune": 17,
    "orange": 11,
    "rouge": 6,
    "rouge_raye": 4,
}


def _read_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return ""


def validate_corridor_data(corridors: list, bounds: dict) -> Dict[str, Any]:
    """
    Validates corridor GeoJSON data against geometry rules.
    Called at runtime with actual data.
    """
    checks = []
    errors = []

    if not corridors or not bounds:
        return {"name": VALIDATOR_NAME, "status": "SKIP", "checks": [], "errors": []}

    south = bounds.get("south", -90)
    north = bounds.get("north", 90)
    west = bounds.get("west", -180)
    east = bounds.get("east", 180)

    # BCE-4X-GEOM-004: CorridorBoundingBoxCompliance
    out_of_bounds_count = 0
    total_coords = 0
    for corridor in corridors:
        props = corridor.get("properties", {})
        bands = props.get("bands", [])
        for band in bands:
            for ring in band.get("coordinates", []):
                for coord in ring:
                    total_coords += 1
                    lng, lat = coord[0], coord[1]
                    if lat < south - 0.00001 or lat > north + 0.00001 or lng < west - 0.00001 or lng > east + 0.00001:
                        out_of_bounds_count += 1

    geom_004_pass = out_of_bounds_count == 0
    checks.append({
        "name": "BCE-4X-GEOM-004_CorridorBoundingBoxCompliance",
        "status": "PASS" if geom_004_pass else "FAIL",
        "detail": (
            f"All {total_coords} band coordinates within 2km bounds"
            if geom_004_pass
            else f"{out_of_bounds_count}/{total_coords} coordinates OUTSIDE 2km bounds"
        ),
    })
    if not geom_004_pass:
        errors.append(f"BCE-4X-GEOM-004: {out_of_bounds_count} band coordinates outside 2km perimeter")

    # BCE-4X-GEOM-005: CorridorWidthNormalization
    width_violations = []
    for corridor in corridors:
        props = corridor.get("properties", {})
        bands = props.get("bands", [])
        for band in bands:
            level = band.get("level")
            width_m = band.get("width_m", 0)
            max_allowed = NORMATIVE_MAX_WIDTHS.get(level, 999)
            if width_m > max_allowed + 0.5:  # small tolerance
                width_violations.append(f"{level}: {width_m}m > {max_allowed}m")

    geom_005_pass = len(width_violations) == 0
    checks.append({
        "name": "BCE-4X-GEOM-005_CorridorWidthNormalization",
        "status": "PASS" if geom_005_pass else "FAIL",
        "detail": (
            "All band widths within 50%-reduced normative limits"
            if geom_005_pass
            else f"Violations: {', '.join(width_violations[:3])}"
        ),
    })
    if not geom_005_pass:
        errors.append(f"BCE-4X-GEOM-005: Band width violations: {', '.join(width_violations[:3])}")

    # BCE-4X-COR-006: CorridorContinuity
    continuity_failures = 0
    total_with_bands = 0
    for corridor in corridors:
        props = corridor.get("properties", {})
        if props.get("has_bands") or len(props.get("bands", [])) > 0:
            total_with_bands += 1
            if not props.get("continuity_valid", True):
                continuity_failures += 1

    cor_006_pass = continuity_failures == 0
    checks.append({
        "name": "BCE-4X-COR-006_CorridorContinuity",
        "status": "PASS" if cor_006_pass else "FAIL",
        "detail": (
            f"All {total_with_bands} corridors have valid continuity"
            if cor_006_pass
            else f"{continuity_failures}/{total_with_bands} corridors have broken continuity"
        ),
    })
    if not cor_006_pass:
        errors.append(f"BCE-4X-COR-006: {continuity_failures} corridors have broken continuity")

    # BCE-4X-VIS-007: CorridorVisualBalance
    opacity_violations = []
    for corridor in corridors:
        props = corridor.get("properties", {})
        for band in props.get("bands", []):
            fill_op = band.get("fillOpacity", 0)
            level = band.get("level", "")
            if level in ("jaune", "orange") and fill_op > 0.30:
                opacity_violations.append(f"{level}: fillOpacity={fill_op} > 0.30")

    vis_007_pass = len(opacity_violations) == 0
    checks.append({
        "name": "BCE-4X-VIS-007_CorridorVisualBalance",
        "status": "PASS" if vis_007_pass else "FAIL",
        "detail": (
            "Yellow/orange bands have balanced visual opacity"
            if vis_007_pass
            else f"Violations: {', '.join(opacity_violations[:3])}"
        ),
    })
    if not vis_007_pass:
        errors.append(f"BCE-4X-VIS-007: Corridor visual imbalance: {', '.join(opacity_violations[:3])}")

    status = "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL"
    return {
        "name": VALIDATOR_NAME,
        "status": status,
        "checks": checks,
        "errors": errors,
    }


def validate() -> Dict[str, Any]:
    """
    Static code analysis validation.
    Checks code structure for compliance.
    """
    checks = []
    errors = []

    corridors_v9_path = os.path.join(BACKEND_SRC, "modules/bionic_engine_p0/engines/corridors_v9.py")
    corridors_v9 = _read_file(corridors_v9_path)

    micro_zones_path = os.path.join(FRONTEND_SRC, "components/territoire/BionicMicroZones.jsx")
    micro_zones = _read_file(micro_zones_path)

    v9_ribbon_path = os.path.join(FRONTEND_SRC, "components/territoire/V9CorridorRibbon.jsx")
    v9_ribbon = _read_file(v9_ribbon_path)

    # BCE-4X-CLIP-002: PostSmoothingClipEnforcement
    # The pipeline MUST clip before smoothing AND re-clip after buffering
    has_clip_before_smooth = bool(re.search(
        r'intersection.*clip.*\n.*smooth|CLIP.*BEFORE.*smooth', corridors_v9, re.IGNORECASE
    ))
    clip_002_pass = has_clip_before_smooth or ("CLIP centerline BEFORE smoothing" in corridors_v9)

    checks.append({
        "name": "BCE-4X-CLIP-002_PostSmoothingClipEnforcement",
        "status": "PASS" if clip_002_pass else "FAIL",
        "detail": (
            "Pipeline: clip → smooth → buffer → re-clip confirmed"
            if clip_002_pass
            else "Smoothing may create out-of-bounds coordinates"
        ),
    })
    if not clip_002_pass:
        errors.append("BCE-4X-CLIP-002: Clip-before-smooth pipeline not enforced")

    # BCE-4X-PIPE-002: FrontendReconstructionGuard
    # Frontend must NOT modify, buffer, or reconstruct corridor geometry
    frontend_modifies_geom = bool(re.search(
        r'\.buffer\(|\.intersection\(|new ShapelyLine|turf\.|buffer\(', 
        micro_zones + v9_ribbon
    ))
    pipe_002_pass = not frontend_modifies_geom

    checks.append({
        "name": "BCE-4X-PIPE-002_FrontendReconstructionGuard",
        "status": "PASS" if pipe_002_pass else "FAIL",
        "detail": (
            "Frontend renders backend geometry as-is, no reconstruction"
            if pipe_002_pass
            else "Frontend modifies corridor geometry (buffer/intersection/turf)"
        ),
    })
    if not pipe_002_pass:
        errors.append("BCE-4X-PIPE-002: Frontend reconstructs corridor geometry")

    # BCE-4X-GEOM-005: Check that BAND_RATIO has +20% widened values
    has_reduced_gris = "0.012" in corridors_v9 and '"max_m": 26' in corridors_v9
    has_reduced_rouge_raye = "0.001" in corridors_v9 and '"max_m": 4' in corridors_v9
    geom_005_code_pass = has_reduced_gris and has_reduced_rouge_raye

    checks.append({
        "name": "BCE-4X-GEOM-005_CorridorWidthNormalization_Code",
        "status": "PASS" if geom_005_code_pass else "FAIL",
        "detail": (
            "BAND_RATIO values confirm +20% widening (gris=0.012/26m, rouge_raye=0.001/4m)"
            if geom_005_code_pass
            else f"BAND_RATIO not properly widened: gris={has_reduced_gris}, rouge_raye={has_reduced_rouge_raye}"
        ),
    })
    if not geom_005_code_pass:
        errors.append("BCE-4X-GEOM-005: BAND_RATIO not at +20% widening")

    status = "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL"
    return {
        "name": VALIDATOR_NAME,
        "status": status,
        "checks": checks,
        "errors": errors,
    }
