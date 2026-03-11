"""
BIONIC Compliance Engine (BCE) — Main Orchestrator
===================================================

Central compliance validation engine for BIONIC.
Runs all 10 validators and produces a structured compliance report.

Usage:
  POST /api/bce/validate            — Full compliance report
  POST /api/bce/validate/certify    — Certify current state as Golden State
  GET  /api/bce/status              — Quick health check

The BCE is the MANDATORY gate for CI/CD.
No merge is allowed if ANY validator fails.
"""

import logging
import time
from datetime import datetime, timezone
from typing import Dict, Any, List

from bce.validators import (
    spatial_integrity,
    water_exclusion,
    species_coherence,
    season_coherence,
    scoring_determinism,
    ui_coherence,
    engine_isolation,
    pipeline_order,
    debug_layer_guard,
    golden_state,
)

logger = logging.getLogger("bce.engine")

BCE_VERSION = "1.0.0"

ALL_VALIDATORS = [
    ("spatial_integrity", spatial_integrity),
    ("water_exclusion", water_exclusion),
    ("species_coherence", species_coherence),
    ("season_coherence", season_coherence),
    ("scoring_determinism", scoring_determinism),
    ("ui_coherence", ui_coherence),
    ("engine_isolation", engine_isolation),
    ("pipeline_order", pipeline_order),
    ("debug_layer_guard", debug_layer_guard),
    ("golden_state", golden_state),
]


def run_full_validation(
    zones_geojson: Dict[str, Any] = None,
    exclusions: List[Dict] = None,
) -> Dict[str, Any]:
    """
    Run ALL 10 BCE validators and produce a compliance report.

    Args:
        zones_geojson: Optional GeoJSON zones for spatial/water validation
        exclusions: Optional exclusion data for water validation

    Returns:
        Full compliance report with pass/fail for each validator.
    """
    start = time.time()
    results = []
    total_checks = 0
    total_pass = 0
    total_fail = 0
    all_errors = []

    for name, validator in ALL_VALIDATORS:
        try:
            if name == "spatial_integrity":
                if zones_geojson:
                    result = validator.validate(zones_geojson)
                else:
                    result = {
                        "name": name, "status": "SKIP",
                        "checks": [], "errors": ["No zones_geojson provided"],
                    }
            elif name == "water_exclusion":
                if zones_geojson:
                    result = validator.validate(zones_geojson, exclusions=exclusions)
                else:
                    result = {
                        "name": name, "status": "SKIP",
                        "checks": [], "errors": ["No zones_geojson provided"],
                    }
            else:
                result = validator.validate()

            results.append(result)
            checks = result.get("checks", [])
            total_checks += len(checks)
            for c in checks:
                if c.get("status") == "PASS":
                    total_pass += 1
                elif c.get("status") == "FAIL":
                    total_fail += 1
            all_errors.extend(result.get("errors", []))

        except Exception as e:
            logger.error(f"BCE validator '{name}' crashed: {e}")
            results.append({
                "name": name,
                "status": "ERROR",
                "checks": [],
                "errors": [f"Validator crashed: {e}"],
            })
            total_fail += 1
            all_errors.append(f"{name}: {e}")

    elapsed_ms = (time.time() - start) * 1000

    # Overall verdict
    statuses = [r["status"] for r in results]
    if any(s == "FAIL" for s in statuses):
        overall = "FAIL"
    elif any(s == "ERROR" for s in statuses):
        overall = "ERROR"
    elif any(s == "SKIP" for s in statuses):
        overall = "PARTIAL"
    else:
        overall = "PASS"

    # Merge allowed if no FAIL or ERROR (SKIP and WARN are acceptable)
    merge_allowed = overall in ("PASS", "PARTIAL")

    report = {
        "bce_version": BCE_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "overall_status": overall,
        "merge_allowed": merge_allowed,
        "summary": {
            "total_validators": len(ALL_VALIDATORS),
            "passed": sum(1 for s in statuses if s == "PASS"),
            "failed": sum(1 for s in statuses if s == "FAIL"),
            "errors": sum(1 for s in statuses if s == "ERROR"),
            "skipped": sum(1 for s in statuses if s == "SKIP"),
            "total_checks": total_checks,
            "checks_passed": total_pass,
            "checks_failed": total_fail,
        },
        "validators": results,
        "all_errors": all_errors,
        "computation_time_ms": round(elapsed_ms, 1),
    }

    if overall == "PASS":
        logger.info(
            f"BCE PASS — {total_pass}/{total_checks} checks passed "
            f"({elapsed_ms:.0f}ms)"
        )
    else:
        logger.warning(
            f"BCE {overall} — {total_fail} checks failed, "
            f"{len(all_errors)} errors ({elapsed_ms:.0f}ms)"
        )

    return report


def run_single_validator(
    validator_name: str,
    zones_geojson: Dict[str, Any] = None,
    exclusions: List[Dict] = None,
) -> Dict[str, Any]:
    """Run a single validator by name."""
    for name, validator in ALL_VALIDATORS:
        if name == validator_name:
            if name in ("spatial_integrity", "water_exclusion"):
                if zones_geojson:
                    if name == "water_exclusion":
                        return validator.validate(zones_geojson, exclusions=exclusions)
                    return validator.validate(zones_geojson)
                return {"name": name, "status": "SKIP", "errors": ["No zones data"]}
            return validator.validate()

    return {"name": validator_name, "status": "ERROR", "errors": ["Unknown validator"]}
