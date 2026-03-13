"""
BIONIC Compliance Engine (BCE) — API Router
============================================

Endpoints:
  POST /api/bce/validate           — Full compliance validation
  POST /api/bce/validate/{name}    — Single validator
  POST /api/bce/certify            — Certify current state as Golden State
  GET  /api/bce/status             — Quick BCE health check
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter

from bce.engine import run_full_validation, run_single_validator, BCE_VERSION
from bce.validators.golden_state import save_golden_state
from bce.validators.corridor_v9 import validate_corridor_batch
from bce.validators.bionic_engine_framework import validate_all_engines, ENGINE_VALIDATORS
from bce.bce_corridor_v9 import validate_corridors_batch, validate_weather_cache_compliance

logger = logging.getLogger("bce.router")

router = APIRouter(prefix="/api/bce", tags=["BCE"])


@router.get("/status")
async def bce_status():
    """Quick health check for the BCE module."""
    # Essayer d'obtenir le statut Auto-Run V8
    autorun_status = None
    try:
        from bce.bce_ruleset_v8 import bce_autorun_engine
        autorun_status = bce_autorun_engine.get_status()
    except ImportError:
        pass
    
    # BCE-MAX x4.1 status
    bce_max_status = None
    try:
        from bce.bce_max_4_1 import get_bce_max_status
        bce_max_status = get_bce_max_status()
    except ImportError:
        pass
    
    return {
        "status": "operational",
        "version": BCE_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "validators": [
            "spatial_integrity", "water_exclusion", "species_coherence",
            "season_coherence", "scoring_determinism", "ui_coherence",
            "engine_isolation", "pipeline_order", "debug_layer_guard",
            "golden_state",
        ],
        "v8_ruleset": {
            "zones": [
                "bce_zone_classification_valid",
                "bce_zone_topographic_valid", 
                "bce_zone_hydrology_valid",
                "bce_zone_human_pressure_valid",
            ],
            "corridors": [
                "bce_corridor_continuity_valid",
                "bce_corridor_topography_valid",
                "bce_corridor_wwf_classification_valid",
                "bce_corridor_human_pressure_respected",
                "bce_corridor_stopover_detection_valid",
            ],
        },
        "bce_4x_corridor": {
            "module": "corridor_v9",
            "critical": True,
            "rules": [
                "hardcoded_score_detection",
                "geometry_linestring_valid",
                "circular_corridor_detection",
                "continuity_gap_check",
                "bounds_clipping_2km",
                "classification_valid",
                "scoring_range_check",
                "enrichment_check",
            ],
        },
        "auto_run": autorun_status,
        "bce_max_4_1": bce_max_status,
    }


@router.post("/validate")
async def bce_validate():
    """
    Run FULL BCE compliance validation.
    This is the MANDATORY CI/CD gate — no merge allowed if any validator fails.

    Validators that need live zone data (spatial_integrity, water_exclusion)
    will run in SKIP mode without it. To fully validate them, use the
    /validate-with-zones endpoint or provide zone data.
    """
    report = run_full_validation()
    return report


@router.post("/validate/{validator_name}")
async def bce_validate_single(validator_name: str):
    """Run a single validator by name."""
    result = run_single_validator(validator_name)
    return {
        "bce_version": BCE_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "validator": result,
    }


@router.post("/validate-with-zones")
async def bce_validate_with_zones():
    """
    Run FULL BCE validation including spatial/water checks
    against live zone generation for a test area.
    """
    try:
        from modules.bionic_engine_p0.services.zone_engine_core_v2 import (
            generate_organic_zones,
        )

        # Generate zones for a known test area (rural Quebec, near water)
        test_bounds = {
            "north": 46.96,
            "south": 46.93,
            "east": -71.27,
            "west": -71.33,
        }
        test_layers = ["habitats", "alimentation", "repos"]

        geojson = await generate_organic_zones(
            bounds=test_bounds,
            layers=test_layers,
            species="moose",
            resolution=40,
            max_zones_per_layer=5,
        )

        # Extract exclusions from the stats for water validation
        exclusions = geojson.get("_exclusions", [])

        report = run_full_validation(
            zones_geojson=geojson,
            exclusions=exclusions,
        )
        report["test_area"] = test_bounds
        report["zones_generated"] = len(geojson.get("features", []))
        return report

    except Exception as e:
        logger.error(f"BCE validate-with-zones failed: {e}")
        # Fall back to validation without zones
        report = run_full_validation()
        report["zone_generation_error"] = str(e)
        return report


@router.post("/certify")
async def bce_certify():
    """
    Certify the current state as the Golden State reference.
    Allows certification if ONLY golden_state validator fails (expected on update).
    All other validators must pass.
    """
    report = run_full_validation()

    # Check if only golden_state is failing (acceptable for re-certification)
    non_golden_failures = [
        v for v in report["validators"]
        if v["name"] != "golden_state"
        and v["status"] not in ("PASS", "SKIP", "WARN")
    ]

    if not non_golden_failures:
        state = save_golden_state()
        return {
            "status": "certified",
            "golden_state": state,
            "validation_report": report,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    else:
        return {
            "status": "rejected",
            "reason": f"Cannot certify — {len(non_golden_failures)} non-golden validators failed",
            "failed_validators": [v["name"] for v in non_golden_failures],
            "validation_report": report,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


@router.post("/validate-corridors")
async def bce_validate_corridors():
    """
    BCE-4X Corridor Validator — Module critique.
    Genere des corridors pour une zone test et execute toutes les validations.
    """
    try:
        from modules.bionic_engine_p0.services.zone_engine_core_v2 import (
            generate_organic_zones,
        )

        test_bounds = {
            "north": 46.96,
            "south": 46.93,
            "east": -71.27,
            "west": -71.33,
        }
        test_layers = ["habitats", "alimentation", "repos", "rut", "trajets"]

        geojson = await generate_organic_zones(
            bounds=test_bounds,
            layers=test_layers,
            species="moose",
            resolution=40,
            max_zones_per_layer=5,
        )

        raw_corridors = geojson.get("corridors", [])
        report = validate_corridor_batch(raw_corridors, test_bounds)
        report["test_area"] = test_bounds
        return report

    except Exception as e:
        logger.error(f"BCE-4X corridor validation failed: {e}")
        return {
            "module": "bce_4x_corridor_validator",
            "status": "ERROR",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


@router.post("/validate-engines")
async def bce_validate_engines():
    """
    BCE-4X Engine Framework — Valide tous les moteurs BIONIC enregistres.
    Les moteurs sans donnees retourneront des violations "data missing".
    """
    report = validate_all_engines()
    return report


@router.get("/registry")
async def bce_registry():
    """
    Retourne le registre complet des modules critiques BCE-4X.
    """
    from bce.bce_max_4_1 import CRITICAL_MODULES_REGISTRY, check_critical_module_coverage, validate_branch_compliance
    uncovered = check_critical_module_coverage()
    return {
        "total_modules": len(CRITICAL_MODULES_REGISTRY),
        "uncovered_active": uncovered,
        "modules": {k: {
            "status": v["status"],
            "validator": v.get("validator", "pending"),
            "since": v.get("since"),
        } for k, v in CRITICAL_MODULES_REGISTRY.items()},
        "engine_validators": list(ENGINE_VALIDATORS.keys()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/branch-compliance/{branch_name:path}")
async def bce_branch_compliance(branch_name: str):
    """
    BCE-4X Branch Protection — Verifie si une branche est conforme pour merge.
    """
    from bce.bce_max_4_1 import validate_branch_compliance
    report = validate_branch_compliance(branch_name)
    return report


@router.get("/branch-compliance")
async def bce_branch_compliance_current():
    """
    BCE-4X Branch Protection — Verifie la branche courante.
    """
    import subprocess
    from bce.bce_max_4_1 import validate_branch_compliance
    try:
        result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True, cwd="/app")
        branch = result.stdout.strip()
    except Exception:
        branch = "unknown"
    report = validate_branch_compliance(branch)
    return report


@router.get("/weather-compliance")
async def bce_weather_compliance():
    """
    BCE-4X: Statut de conformite du Weather Engine (regle 60 min OWM).
    """
    return validate_weather_cache_compliance()


@router.post("/validate-corridors-v9")
async def bce_validate_corridors_v9():
    """
    BCE-4X Corridor V9 Validator — Pipeline complet.
    Genere corridors V9 et valide avec le nouveau systeme 5 niveaux.
    """
    try:
        from modules.bionic_engine_p0.services.zone_engine_core_v2 import generate_organic_zones

        test_bounds = {
            "north": 46.96, "south": 46.93,
            "east": -71.27, "west": -71.33,
        }

        geojson = await generate_organic_zones(
            bounds=test_bounds,
            layers=["habitats", "alimentation", "repos", "rut", "trajets"],
            species="moose",
            resolution=40,
            max_zones_per_layer=5,
        )

        raw_corridors = geojson.get("corridors", [])
        report = validate_corridors_batch(raw_corridors, test_bounds)
        report["test_area"] = test_bounds
        report["weather_compliance"] = validate_weather_cache_compliance()
        return report

    except Exception as e:
        logger.error(f"BCE-4X V9 corridor validation failed: {e}")
        return {
            "module": "bce_4x_corridor_v9",
            "status": "ERROR",
            "error": str(e),
        }



@router.post("/validate-color-contract")
async def validate_color_contract_endpoint():
    """
    STEVE-MAX: BCE-4X Color Contract validation.
    Rules: COLOR-001, COLOR-002, COLOR-003, UI-004, UI-005, UI-006
    """
    try:
        from bce.validators.color_contract import validate as validate_cc
        result = validate_cc()
        return {
            "module": "bce_4x_color_contract",
            "branch": "steve-max",
            **result,
        }
    except Exception as e:
        logger.error(f"Color contract validation error: {e}")
        return {
            "module": "bce_4x_color_contract",
            "status": "ERROR",
            "error": str(e),
        }



@router.post("/validate-geometry-compliance")
async def validate_geometry_compliance_endpoint():
    """
    STEVE-MAX: BCE-4X Geometry + Clipping validation.
    Rules: GEOM-004, GEOM-005, CLIP-002, PIPE-002
    """
    try:
        from bce.validators.geometry_compliance import validate as validate_gc
        result = validate_gc()
        return {
            "module": "bce_4x_geometry_compliance",
            "branch": "steve-max",
            **result,
        }
    except Exception as e:
        logger.error(f"Geometry compliance validation error: {e}")
        return {
            "module": "bce_4x_geometry_compliance",
            "status": "ERROR",
            "error": str(e),
        }


@router.post("/validate-corridors-runtime")
async def validate_corridors_runtime_endpoint(request: dict):
    """
    STEVE-MAX: Runtime validation of corridor data against 2km bounds.
    Send corridors + bounds to validate GEOM-004 and GEOM-005.
    """
    try:
        from bce.validators.geometry_compliance import validate_corridor_data
        corridors = request.get("corridors", [])
        bounds = request.get("bounds", {})
        result = validate_corridor_data(corridors, bounds)
        return {
            "module": "bce_4x_geometry_runtime",
            "branch": "steve-max",
            **result,
        }
    except Exception as e:
        logger.error(f"Runtime corridor validation error: {e}")
        return {
            "module": "bce_4x_geometry_runtime",
            "status": "ERROR",
            "error": str(e),
        }



@router.post("/validate-corridor-continuity")
async def validate_corridor_continuity_endpoint(request: dict):
    """
    STEVE-MAX++: BCE-4X-COR-006 — Corridor Network Continuity validation.
    Checks that no corridor endpoint is isolated.
    """
    try:
        from bce.bce_corridor_v9 import validate_corridor_network_continuity
        corridors = request.get("corridors", [])
        zones = request.get("zones", [])
        result = validate_corridor_network_continuity(corridors, zones)
        return {"module": "bce_4x_cor_006", "branch": "steve-max", **result}
    except Exception as e:
        logger.error(f"COR-006 validation error: {e}")
        return {"module": "bce_4x_cor_006", "status": "ERROR", "error": str(e)}


@router.post("/validate-visual-balance")
async def validate_visual_balance_endpoint(request: dict):
    """
    STEVE-MAX++: BCE-4X-VIS-007 — Corridor Visual Balance validation.
    Checks that corridor band widths and opacities are within reduced limits.
    """
    try:
        from bce.bce_corridor_v9 import validate_corridor_visual_balance
        corridors = request.get("corridors", [])
        result = validate_corridor_visual_balance(corridors)
        return {"module": "bce_4x_vis_007", "branch": "steve-max", **result}
    except Exception as e:
        logger.error(f"VIS-007 validation error: {e}")
        return {"module": "bce_4x_vis_007", "status": "ERROR", "error": str(e)}
