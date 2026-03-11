"""Engine 3D Router - PLAN MAITRE
FastAPI router for 3D terrain visualization and analysis.

Version: 1.0.0
API Prefix: /api/v1/3d
"""

from fastapi import APIRouter, HTTPException, Query
from .service import Engine3DService

router = APIRouter(prefix="/api/v1/3d", tags=["Engine 3D"])

_service = Engine3DService()


@router.get("/")
async def engine_3d_info():
    """Get 3D engine information"""
    stats = await _service.get_stats()
    
    return {
        "module": "engine_3d",
        "version": "1.0.0",
        "phase": 4,
        "description": "Visualisation et analyse 3D des territoires",
        "status": "operational",
        "features": [
            "Modèles numériques de terrain (MNT)",
            "Profils d'élévation",
            "Lignes de vue (viewshed)",
            "Zones d'ombre/exposition",
            "Export de données 3D"
        ],
        "capabilities": stats
    }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "module": "engine_3d", "version": "1.0.0"}


@router.get("/elevation/{coordinates}")
async def get_elevation(coordinates: str):
    """Get elevation at coordinates (format: lat,lng)"""
    try:
        lat, lng = map(float, coordinates.split(","))
    except ValueError:
        raise HTTPException(status_code=400, detail="Format: lat,lng")
    
    point = await _service.get_elevation(lat, lng)
    return {"success": True, "elevation": point.model_dump()}


@router.get("/profile")
async def get_elevation_profile(
    start_lat: float = Query(...),
    start_lng: float = Query(...),
    end_lat: float = Query(...),
    end_lng: float = Query(...),
    num_points: int = Query(50, ge=10, le=200)
):
    """Generate elevation profile between two points"""
    profile = await _service.get_elevation_profile(
        start_lat, start_lng, end_lat, end_lng, num_points
    )
    return {"success": True, "profile": profile.model_dump()}


@router.get("/viewshed")
async def analyze_viewshed(
    lat: float = Query(...),
    lng: float = Query(...),
    observer_height: float = Query(1.7, ge=0, le=50),
    radius_km: float = Query(2.0, ge=0.1, le=10)
):
    """Analyze viewshed (visible area) from a point"""
    viewshed = await _service.analyze_viewshed(
        lat, lng, observer_height, radius_km
    )
    return {"success": True, "viewshed": viewshed.model_dump()}


@router.get("/terrain-analysis")
async def analyze_terrain(
    lat: float = Query(...),
    lng: float = Query(...),
    radius_km: float = Query(1.0, ge=0.1, le=10)
):
    """Comprehensive terrain analysis for hunting"""
    analysis = await _service.analyze_terrain(lat, lng, radius_km)
    return {"success": True, "terrain": analysis.model_dump()}


@router.post("/export")
async def export_3d_terrain(
    north: float = Query(...),
    south: float = Query(...),
    east: float = Query(...),
    west: float = Query(...),
    format: str = Query("glb", regex="^(glb|obj|stl|geotiff)$"),
    resolution_m: float = Query(30.0, ge=1, le=100)
):
    """Export 3D terrain data"""
    export = await _service.export_3d_terrain(
        north, south, east, west, format, resolution_m
    )
    return {
        "success": True,
        "export": export.model_dump(),
        "message": "Export en préparation" if not export.file_url else "Export prêt"
    }
