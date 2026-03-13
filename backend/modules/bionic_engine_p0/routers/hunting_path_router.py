"""
STEVE-MAX: Hunting Path & Amenagement Router
Endpoints for optimal hunting path generation and 2km setup report.
"""

from fastapi import APIRouter
import logging
import math

logger = logging.getLogger("bionic.hunting_path_router")

router = APIRouter(prefix="/v1/bionic", tags=["hunting-path"])


@router.post("/hunting-path")
async def generate_hunting_path_endpoint(request: dict):
    """
    Generate an optimal hunting path through key zones.
    
    Input:
    - zones: list of zone GeoJSON features
    - corridors: list of corridor GeoJSON features
    - wind_direction: degrees (0=N, 90=E, 180=S, 270=W)
    - wind_speed: km/h
    - waypoint_center: {lat, lng}
    - bounds: {north, south, east, west}
    """
    try:
        from modules.bionic_engine_p0.engines.hunting_path import generate_hunting_path

        zones = request.get("zones", [])
        corridors = request.get("corridors", [])
        waypoint_center = request.get("waypoint_center")
        bounds = request.get("bounds")

        # Compute analysis bounds from waypoint if needed
        analysis_bounds = bounds
        if waypoint_center and not bounds:
            half_m = 1000
            lat_rad = math.radians(waypoint_center.get("lat", 46.815))
            delta_lat = half_m / 111320
            delta_lng = half_m / (111320 * math.cos(lat_rad))
            analysis_bounds = {
                "south": waypoint_center["lat"] - delta_lat,
                "north": waypoint_center["lat"] + delta_lat,
                "west": waypoint_center["lng"] - delta_lng,
                "east": waypoint_center["lng"] + delta_lng,
            }

        result = generate_hunting_path(
            zones=zones,
            corridors=corridors,
            waypoint_center=waypoint_center,
            bounds=analysis_bounds,
        )

        return {
            "success": True,
            "hunting_path": result,
        }
    except Exception as e:
        logger.error(f"Hunting path error: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


@router.post("/amenagement-report")
async def generate_amenagement_report_endpoint(request: dict):
    """
    Generate a complete amenagement (setup) report for the 2km square.
    """
    try:
        from modules.bionic_engine_p0.engines.hunting_path import (
            generate_hunting_path,
            generate_amenagement_report,
        )

        zones = request.get("zones", [])
        corridors = request.get("corridors", [])
        waypoint_center = request.get("waypoint_center")
        bounds = request.get("bounds")

        # Compute analysis bounds
        analysis_bounds = bounds
        if waypoint_center and not bounds:
            half_m = 1000
            lat_rad = math.radians(waypoint_center.get("lat", 46.815))
            delta_lat = half_m / 111320
            delta_lng = half_m / (111320 * math.cos(lat_rad))
            analysis_bounds = {
                "south": waypoint_center["lat"] - delta_lat,
                "north": waypoint_center["lat"] + delta_lat,
                "west": waypoint_center["lng"] - delta_lng,
                "east": waypoint_center["lng"] + delta_lng,
            }

        # First generate hunting path (P0: no wind in decisional pipeline)
        hunting_path = generate_hunting_path(
            zones=zones,
            corridors=corridors,
            waypoint_center=waypoint_center,
            bounds=analysis_bounds,
        )

        # Then generate full report
        report = generate_amenagement_report(
            zones=zones,
            corridors=corridors,
            hunting_path=hunting_path,
            waypoint_center=waypoint_center,
        )

        return {
            "success": True,
            "hunting_path": hunting_path,
            "amenagement_report": report,
        }
    except Exception as e:
        logger.error(f"Amenagement report error: {e}", exc_info=True)
        return {"success": False, "error": str(e)}
