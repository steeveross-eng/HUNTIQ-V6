"""
BIONIC V3 Router — API pour le pipeline integre complet.
STEVE-MAX++: 24 engines + 3 modeles fauniques + 3 IA engines.
"""

from fastapi import APIRouter
import logging

logger = logging.getLogger("bionic_v3_router")
router = APIRouter(prefix="/v1/bionic/engines-v3", tags=["bionic-v3"])


@router.post("/compute")
async def compute_v3(request: dict):
    """Compute ALL engines (V2 + V3 + AI + Species) and return integrated results."""
    try:
        from modules.bionic_engine_p0.engines.engines_v3 import compute_all_v3

        context = {
            "zones": request.get("zones", []),
            "corridors": request.get("corridors", []),
            "weather": request.get("weather", {}),
            "season": request.get("season", "automne"),
            "hour": request.get("hour", 6),
            "species": request.get("species", "moose"),
            "bounds": request.get("bounds", {}),
        }
        return compute_all_v3(context)
    except Exception as e:
        logger.error(f"V3 compute error: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


@router.get("/status")
async def status_v3():
    """Get status of ALL engines (V2 + V3 + AI)."""
    try:
        from modules.bionic_engine_p0.engines.engines_v3 import get_all_engine_statuses
        statuses = get_all_engine_statuses()
        return {
            "success": True,
            "engine_count": len(statuses),
            "v2_count": sum(1 for s in statuses if s.get("source") == "v2"),
            "v3_count": sum(1 for s in statuses if s.get("source") == "v3"),
            "ai_count": sum(1 for s in statuses if s.get("source") == "ai"),
            "engines": statuses,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/species/{species_id}")
async def compute_species(species_id: str, request: dict):
    """Compute scores for a specific species (moose, deer, bear)."""
    if species_id not in ("moose", "deer", "bear"):
        return {"success": False, "error": f"Unknown species: {species_id}"}
    try:
        from modules.bionic_engine_p0.engines.engines_v3 import compute_all_v3

        context = {
            "zones": request.get("zones", []),
            "corridors": request.get("corridors", []),
            "weather": request.get("weather", {}),
            "season": request.get("season", "automne"),
            "hour": request.get("hour", 6),
            "species": species_id,
            "bounds": request.get("bounds", {}),
        }
        result = compute_all_v3(context)
        species_data = result.get("species_scores", {}).get(species_id, {})
        return {
            "success": True,
            "species": species_id,
            "score": species_data.get("score", 0),
            "food_zone_score": species_data.get("food_zone_score", 0),
            "rest_zone_score": species_data.get("rest_zone_score", 0),
            "corridor_influence": species_data.get("corridor_influence", 0),
            "hotspot_influence": species_data.get("hotspot_influence", 0),
            "details": species_data.get("details", {}),
            "final_score": result.get("final_score", 0),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/predictions")
async def compute_predictions(request: dict):
    """Get AI predictions (24h, 72h, 7d) for all species."""
    try:
        from modules.bionic_engine_p0.engines.engines_v3 import compute_all_v3

        results = {}
        for sp in ["moose", "deer", "bear"]:
            context = {
                "zones": request.get("zones", []),
                "corridors": request.get("corridors", []),
                "weather": request.get("weather", {}),
                "season": request.get("season", "automne"),
                "hour": request.get("hour", 6),
                "species": sp,
                "bounds": request.get("bounds", {}),
            }
            v3_result = compute_all_v3(context)
            pred = v3_result.get("engines", {}).get("predictive_models", {})
            temporal = v3_result.get("engines", {}).get("temporal_analysis", {})
            dynamic = v3_result.get("engines", {}).get("dynamic_scoring", {})
            results[sp] = {
                "predictions": pred.get("predictions", {}),
                "trend": temporal.get("trend", "stable"),
                "dynamic_score": dynamic.get("score", 0),
                "species_score": v3_result.get("species_scores", {}).get(sp, {}).get("score", 0),
            }

        return {"success": True, "predictions": results}
    except Exception as e:
        return {"success": False, "error": str(e)}
