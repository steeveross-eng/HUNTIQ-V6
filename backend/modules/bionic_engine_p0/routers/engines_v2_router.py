"""
STEVE-MAX: BIONIC Engines V2 Router
Endpoints for executing and querying the 12 BIONIC V2 engines.
"""

from fastapi import APIRouter
import logging

logger = logging.getLogger("bionic.engines_v2_router")

router = APIRouter(prefix="/v1/bionic", tags=["engines-v2"])


@router.post("/engines-v2/compute")
async def compute_all_engines_endpoint(request: dict):
    """
    Execute all 12 BIONIC V2 engines with the given context.
    Returns individual scores + global attractiveness score.
    """
    try:
        from modules.bionic_engine_p0.engines.engines_v2 import compute_all_engines

        context = {
            "zones": request.get("zones", []),
            "corridors": request.get("corridors", []),
            "weather": request.get("weather", {}),
            "season": request.get("season", "automne"),
            "hour": request.get("hour", 12),
            "species": request.get("species", "moose"),
            "bounds": request.get("bounds", {}),
        }

        results = compute_all_engines(context)

        # Calculate summary
        total_engines = len(results)
        avg_score = sum(r.get("score", 0) for r in results.values()) / max(1, total_engines)

        return {
            "success": True,
            "engine_count": total_engines,
            "average_score": round(avg_score, 1),
            "engines": results,
        }
    except Exception as e:
        logger.error(f"Engines V2 compute error: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


@router.get("/engines-v2/status")
async def engines_v2_status():
    """Return status of all 12 BIONIC V2 engines."""
    try:
        from modules.bionic_engine_p0.engines.engines_v2 import get_engine_statuses
        statuses = get_engine_statuses()
        return {
            "success": True,
            "engine_count": len(statuses),
            "engines": statuses,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
