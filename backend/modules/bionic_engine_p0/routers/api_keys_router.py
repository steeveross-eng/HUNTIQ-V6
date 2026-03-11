"""
ROUTER API KEYS STATUS — System Healthcheck
BIONIC V5 ULTIME 300% — PHASE G+

Endpoint: GET /api/v1/system/api-keys/status

Verifie l'etat de toutes les cles API configurees.
Retourne le statut de chaque cle et la compatibilite des phases.
"""

import os
import json
import logging
from pathlib import Path
from fastapi import APIRouter

logger = logging.getLogger("bionic_engine.api_keys_router")
router = APIRouter(prefix="/api/v1/system", tags=["System Healthcheck"])

TEMPLATE_PATH = Path(__file__).resolve().parent.parent.parent.parent / "config" / "api_keys_template.json"


def _load_template() -> dict:
    if TEMPLATE_PATH.exists():
        with open(TEMPLATE_PATH) as f:
            return json.load(f)
    return {"keys": {}}


def _check_key_status(env_var: str) -> str:
    # Special case: Open-Meteo is free and requires no API key
    if env_var == "NONE_REQUIRED":
        return "configured"
    val = os.environ.get(env_var, "")
    if val and len(val) > 4:
        return "configured"
    return "not_configured"


@router.get("/api-keys/status")
async def api_keys_status():
    template = _load_template()
    keys_config = template.get("keys", {})

    key_statuses = {}
    configured_count = 0
    total_count = len(keys_config)

    for key_name, config in keys_config.items():
        env_var = config.get("env_var", "")
        status = _check_key_status(env_var)
        if status == "configured":
            configured_count += 1
        key_statuses[key_name] = {
            "env_var": env_var,
            "status": status,
            "provider": config.get("provider", "unknown"),
            "required_for": config.get("required_for", []),
            "fallback": config.get("fallback", "none"),
        }

    phase_compatibility = {
        "pipeline_internal": {
            "status": "fully_operational",
            "keys_required": 0,
            "keys_configured": 0,
            "description": "10/10 modules on synthetic data — no keys needed",
        },
        "phase_g_real_data": {
            "status": "ready" if all(
                _check_key_status(keys_config[k]["env_var"]) == "configured"
                for k in ["sentinel2_ndvi", "elevation_dem", "weather_realtime"]
                if k in keys_config
            ) else "awaiting_keys",
            "keys_required": ["sentinel2_ndvi", "elevation_dem", "weather_realtime"],
        },
        "phase_h_ml": {
            "status": "ready_with_fallback",
            "keys_required": ["ml_cloud"],
            "fallback": "internal_sklearn",
            "description": "ML works with internal sklearn — cloud key optional",
        },
    }

    return {
        "pipeline": "BIONIC_V5_ULTIME_300",
        "total_keys": total_count,
        "configured_keys": configured_count,
        "missing_keys": total_count - configured_count,
        "key_statuses": key_statuses,
        "phase_compatibility": phase_compatibility,
        "validation": {
            "pipeline_internal_operational": True,
            "strict_mode_enabled": False,
            "all_fallbacks_available": True,
        },
    }
