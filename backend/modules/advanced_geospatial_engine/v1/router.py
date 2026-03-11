"""Advanced Geospatial Engine Router - PLAN MAITRE
FastAPI router for advanced geospatial analysis.

Version: 1.0.0
API Prefix: /api/v1/advanced-geo
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from .service import AdvancedGeospatialService

router = APIRouter(prefix="/api/v1/advanced-geo", tags=["Advanced Geospatial Engine"])

_service = AdvancedGeospatialService()


@router.get("/")
async def advanced_geo_engine_info():
    """Get advanced geospatial engine information"""
    stats = await _service.get_stats()
    
    return {
        "module": "advanced_geospatial_engine",
        "version": "1.0.0",
        "phase": 4,
        "description": "Analyses géospatiales avancées",
        "status": "operational",
        "features": [
            "Analyse de corridors de déplacement",
            "Détection de zones de concentration",
            "Analyse de connectivité d'habitat",
            "Modélisation de dispersion",
            "Cartes de chaleur"
        ],
        "statistics": stats
    }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "module": "advanced_geospatial_engine", "version": "1.0.0"}


@router.get("/corridors")
async def identify_corridors(
    lat: float = Query(...),
    lng: float = Query(...),
    radius_km: float = Query(5.0, ge=0.5, le=50),
    species: Optional[str] = Query(None)
):
    """Identify movement corridors in area"""
    corridors = await _service.identify_corridors(lat, lng, radius_km, species)
    return {
        "success": True,
        "total": len(corridors),
        "corridors": [c.model_dump() for c in corridors]
    }


@router.get("/concentration-zones")
async def identify_concentration_zones(
    lat: float = Query(...),
    lng: float = Query(...),
    radius_km: float = Query(5.0, ge=0.5, le=50),
    species: Optional[str] = Query(None)
):
    """Identify wildlife concentration zones"""
    zones = await _service.identify_concentration_zones(lat, lng, radius_km, species)
    return {
        "success": True,
        "total": len(zones),
        "zones": [z.model_dump() for z in zones]
    }


@router.get("/connectivity")
async def analyze_connectivity(
    lat: float = Query(...),
    lng: float = Query(...),
    radius_km: float = Query(5.0, ge=0.5, le=50)
):
    """Analyze habitat connectivity"""
    connectivity = await _service.analyze_connectivity(lat, lng, radius_km)
    return {"success": True, "connectivity": connectivity.model_dump()}


@router.get("/heatmap")
async def generate_heatmap(
    north: float = Query(...),
    south: float = Query(...),
    east: float = Query(...),
    west: float = Query(...),
    species: Optional[str] = Query(None),
    data_type: str = Query("activity", regex="^(activity|sightings|harvest|signs)$"),
    resolution_m: float = Query(100, ge=10, le=1000)
):
    """Generate activity heatmap"""
    if north <= south or east <= west:
        raise HTTPException(
            status_code=400,
            detail="Invalid bounds: north > south and east > west required"
        )
    
    heatmap = await _service.generate_heatmap(
        north, south, east, west, species, data_type, resolution_m
    )
    return {"success": True, "heatmap": heatmap.model_dump()}


@router.get("/dispersion")
async def model_dispersion(
    lat: float = Query(...),
    lng: float = Query(...),
    species: str = Query(...),
    time_hours: float = Query(24, ge=1, le=168)
):
    """Model wildlife dispersion from a point"""
    model = await _service.model_dispersion(lat, lng, species, time_hours)
    return {"success": True, "dispersion": model.model_dump()}
