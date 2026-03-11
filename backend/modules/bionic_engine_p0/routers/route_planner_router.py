"""
ROUTER ROUTE PLANNER — Tactical Route Optimization
BIONIC V5 ULTIME 300% — route_planner_v1

Endpoints:
  POST /api/v1/bionic/route-planner/compute  — Compute optimal tactical route
  GET  /api/v1/bionic/route-planner/status    — Service status

Module isole. Shadow Mode. 0 impact sur pipeline principal.
"""

import logging
import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

logger = logging.getLogger("bionic_engine.route_planner_router")
router = APIRouter(prefix="/api/v1/bionic/route-planner", tags=["BIONIC Route Planner"])

SUPPORTED_SPECIES = ["moose", "deer", "bear", "wild_turkey", "elk"]


class RouteBounds(BaseModel):
    north: float = Field(..., ge=-90, le=90)
    south: float = Field(..., ge=-90, le=90)
    east: float = Field(..., ge=-180, le=180)
    west: float = Field(..., ge=-180, le=180)


class AnchorWaypoint(BaseModel):
    lat: float
    lng: float
    name: Optional[str] = "Waypoint"


class RoutePlannerRequest(BaseModel):
    bounds: RouteBounds
    species: str = Field(default="moose")
    resolution: int = Field(default=30, ge=10, le=60)
    hotspot_threshold: float = Field(default=70.0, ge=30, le=95)
    anchor_waypoints: Optional[List[AnchorWaypoint]] = None
    walking_speed_kmh: float = Field(default=3.5, ge=1.0, le=10.0)


@router.post("/compute")
async def route_planner_compute(request: RoutePlannerRequest):
    """
    Compute optimal tactical route between hotspots and anchor waypoints.
    Uses A* weighted pathfinding on habitat_score grid.
    """
    from modules.bionic_engine_p0.services.route_planner_service import compute_tactical_route

    if request.species not in SUPPORTED_SPECIES:
        raise HTTPException(status_code=400, detail=f"Espece non supportee: {request.species}")

    bounds = {
        "north": request.bounds.north, "south": request.bounds.south,
        "east": request.bounds.east, "west": request.bounds.west,
    }

    anchors = None
    if request.anchor_waypoints:
        anchors = [{"lat": wp.lat, "lng": wp.lng, "name": wp.name} for wp in request.anchor_waypoints]

    start = time.time()
    result = await compute_tactical_route(
        bounds, request.species, request.resolution,
        request.hotspot_threshold, anchors, request.walking_speed_kmh,
    )
    result["router_time_ms"] = round((time.time() - start) * 1000, 1)

    logger.info(
        f"Route planner: species={request.species}, "
        f"hotspots={result.get('hotspots_found', 0)}, "
        f"time={result.get('router_time_ms')}ms"
    )

    return result


@router.get("/status")
async def route_planner_status():
    """Service status for Route Planner."""
    return {
        "module": "ROUTE_PLANNER",
        "label": "Planificateur de Parcours Tactique",
        "version": "route_planner_v1",
        "status": "active",
        "mode": "shadow (non-destructif)",
        "algorithm": "A* weighted (habitat_score inverse cost)",
        "features": [
            "hotspot detection (>threshold)",
            "ecological corridor pathfinding",
            "waypoint anchor integration",
            "nearest-neighbor ordering",
            "distance and time estimation",
        ],
        "species_supported": SUPPORTED_SPECIES,
        "endpoints": [
            "POST /api/v1/bionic/route-planner/compute",
            "GET /api/v1/bionic/route-planner/status",
        ],
    }
