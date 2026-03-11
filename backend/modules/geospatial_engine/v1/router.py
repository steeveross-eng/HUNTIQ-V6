"""Geospatial Engine Router - CORE

FastAPI router for geospatial hunting analysis.

Version: 1.0.0
API Prefix: /api/v1/geospatial
"""

from fastapi import APIRouter, HTTPException, Query
from .service import GeospatialService
from .models import Coordinates

router = APIRouter(prefix="/api/v1/geospatial", tags=["Geospatial Engine"])

# Initialize service
_service = GeospatialService()


@router.get("/")
async def geospatial_engine_info():
    """Get geospatial engine information"""
    return {
        "module": "geospatial_engine",
        "version": "1.0.0",
        "description": "Geospatial analysis for hunting territory management",
        "features": [
            "Distance calculation",
            "Terrain analysis",
            "Zone lookup",
            "Bearing calculation",
            "Quebec region data"
        ],
        "regions_count": len(_service.QUEBEC_REGIONS)
    }


@router.post("/distance")
async def calculate_distance(point1: Coordinates, point2: Coordinates):
    """Calculate distance between two points"""
    distance = _service.calculate_distance(point1, point2)
    bearing = _service.get_bearing(point1, point2)
    direction = _service.bearing_to_direction(bearing)
    
    return {
        "success": True,
        "distance_km": distance,
        "bearing": bearing,
        "direction": direction
    }


@router.post("/terrain")
async def analyze_terrain(coordinates: Coordinates):
    """Analyze terrain at given coordinates"""
    terrain = _service.analyze_terrain(coordinates)
    hunting_score = _service.calculate_hunting_score(terrain)
    
    return {
        "success": True,
        "coordinates": coordinates.model_dump(),
        "terrain": terrain.model_dump(),
        "hunting_potential": {
            "score": hunting_score,
            "rating": _get_rating(hunting_score)
        }
    }


@router.get("/regions")
async def list_regions():
    """List all Quebec hunting regions"""
    return {
        "success": True,
        "regions": [
            {"code": code, "name": name}
            for code, name in _service.QUEBEC_REGIONS.items()
        ]
    }


@router.get("/regions/{region_code}")
async def get_region(region_code: str):
    """Get detailed information about a region"""
    if region_code not in _service.QUEBEC_REGIONS:
        raise HTTPException(
            status_code=404,
            detail={
                "message": f"Region '{region_code}' not found",
                "available_regions": list(_service.QUEBEC_REGIONS.keys())
            }
        )
    
    info = _service.get_region_info(region_code)
    
    return {
        "success": True,
        "region": info
    }


@router.post("/zones/nearby")
async def find_nearby_zones(
    coordinates: Coordinates,
    radius_km: float = Query(50, ge=1, le=200)
):
    """Find hunting zones near coordinates"""
    zones = _service.find_nearby_zones(coordinates, radius_km)
    
    return {
        "success": True,
        "search_center": coordinates.model_dump(),
        "radius_km": radius_km,
        "zones_found": len(zones),
        "zones": zones
    }


@router.get("/bearing")
async def calculate_bearing(
    lat1: float = Query(..., ge=-90, le=90),
    lon1: float = Query(..., ge=-180, le=180),
    lat2: float = Query(..., ge=-90, le=90),
    lon2: float = Query(..., ge=-180, le=180)
):
    """Calculate bearing between two points"""
    point1 = Coordinates(latitude=lat1, longitude=lon1)
    point2 = Coordinates(latitude=lat2, longitude=lon2)
    
    bearing = _service.get_bearing(point1, point2)
    direction = _service.bearing_to_direction(bearing)
    
    return {
        "success": True,
        "bearing_degrees": bearing,
        "cardinal_direction": direction
    }


def _get_rating(score: float) -> str:
    """Convert score to rating"""
    if score >= 8:
        return "🟢 Excellent"
    elif score >= 6:
        return "🟡 Bon"
    elif score >= 4:
        return "🟠 Moyen"
    else:
        return "🔴 Faible"
