"""3D Data Layers Router - PHASE 5
API endpoints for terrain elevation and 3D analysis data.

Version: 1.0.0
"""

from fastapi import APIRouter, Query
from typing import List
from pydantic import BaseModel

from ..data_layer import get_3d_layer


router = APIRouter(
    prefix="/api/v1/data/3d",
    tags=["Data Layers - 3D Terrain"]
)


# ==============================================
# RESPONSE MODELS
# ==============================================

class HealthResponse(BaseModel):
    status: str
    layer: str
    version: str
    message: str


class ElevationResponse(BaseModel):
    lat: float
    lng: float
    elevation: float
    source: str
    resolution_m: float


class SlopeAspectResponse(BaseModel):
    lat: float
    lng: float
    slope_degrees: float
    slope_percent: float
    slope_class: str
    aspect_degrees: float
    aspect_direction: str


# ==============================================
# HEALTH CHECK
# ==============================================

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check 3D data layer health"""
    layer = get_3d_layer()
    stats = await layer.get_stats()
    
    return HealthResponse(
        status="operational",
        layer="layers_3d",
        version="1.0.0",
        message=f"Layer opérationnel - {len(stats['dem_sources'])} sources DEM disponibles"
    )


@router.get("/stats")
async def get_layer_stats():
    """Get 3D data layer statistics"""
    layer = get_3d_layer()
    return await layer.get_stats()


# ==============================================
# ELEVATION
# ==============================================

@router.get("/elevation", response_model=ElevationResponse)
async def get_elevation(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    source: str = Query("SRTM", description="DEM source: SRTM, CDEM, LiDAR")
):
    """Get elevation at a point"""
    layer = get_3d_layer()
    elev = await layer.get_elevation(lat, lng, source)
    
    return ElevationResponse(
        lat=elev.lat,
        lng=elev.lng,
        elevation=elev.elevation,
        source=elev.source,
        resolution_m=elev.resolution_m
    )


@router.post("/elevation/bulk")
async def get_elevations_bulk(points: List[List[float]]):
    """Get elevations for multiple points
    
    Body: [[lat1, lng1], [lat2, lng2], ...]
    """
    layer = get_3d_layer()
    
    point_tuples = [(p[0], p[1]) for p in points]
    elevations = await layer.get_elevations_bulk(point_tuples)
    
    return {
        "count": len(elevations),
        "elevations": [e.model_dump() for e in elevations]
    }


@router.get("/elevation/profile")
async def get_elevation_profile(
    start_lat: float = Query(..., description="Start latitude"),
    start_lng: float = Query(..., description="Start longitude"),
    end_lat: float = Query(..., description="End latitude"),
    end_lng: float = Query(..., description="End longitude"),
    num_points: int = Query(50, description="Number of sample points")
):
    """Get elevation profile along a line"""
    layer = get_3d_layer()
    profile = await layer.get_elevation_profile(
        start_lat, start_lng, end_lat, end_lng, num_points
    )
    
    return profile


# ==============================================
# SLOPE & ASPECT
# ==============================================

@router.get("/slope-aspect", response_model=SlopeAspectResponse)
async def get_slope_aspect(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    cell_size_m: float = Query(30, description="Analysis cell size in meters")
):
    """Calculate slope and aspect at a point"""
    layer = get_3d_layer()
    result = await layer.get_slope_aspect(lat, lng, cell_size_m)
    
    return SlopeAspectResponse(
        lat=lat,
        lng=lng,
        slope_degrees=result.slope_degrees,
        slope_percent=result.slope_percent,
        slope_class=result.slope_class,
        aspect_degrees=result.aspect_degrees,
        aspect_direction=result.aspect_direction
    )


# ==============================================
# TERRAIN FEATURES
# ==============================================

@router.get("/features")
async def get_terrain_features(
    lat: float = Query(..., description="Center latitude"),
    lng: float = Query(..., description="Center longitude"),
    radius_km: float = Query(2.0, description="Search radius in km")
):
    """Identify terrain features in an area"""
    layer = get_3d_layer()
    features = await layer.identify_terrain_features(lat, lng, radius_km)
    
    return {
        "center": {"lat": lat, "lng": lng},
        "radius_km": radius_km,
        "count": len(features),
        "features": [f.model_dump() for f in features]
    }


@router.get("/features/saddles")
async def get_saddles(
    lat: float = Query(..., description="Center latitude"),
    lng: float = Query(..., description="Center longitude"),
    radius_km: float = Query(2.0, description="Search radius in km")
):
    """Get saddle points (key hunting locations)"""
    layer = get_3d_layer()
    saddles = await layer.get_saddles_in_area(lat, lng, radius_km)
    
    return {
        "center": {"lat": lat, "lng": lng},
        "radius_km": radius_km,
        "count": len(saddles),
        "saddles": [s.model_dump() for s in saddles],
        "hunting_tip": "Les cols sont des points de passage privilégiés pour le gibier"
    }


# ==============================================
# VIEWSHED
# ==============================================

@router.get("/viewshed")
async def calculate_viewshed(
    lat: float = Query(..., description="Observer latitude"),
    lng: float = Query(..., description="Observer longitude"),
    observer_height: float = Query(1.7, description="Observer height in meters"),
    radius_m: float = Query(2000, description="Analysis radius in meters"),
    resolution_m: float = Query(50, description="Cell resolution in meters")
):
    """Calculate viewshed from an observation point"""
    layer = get_3d_layer()
    viewshed = await layer.calculate_viewshed(
        lat, lng, observer_height, radius_m, resolution_m
    )
    
    return viewshed


# ==============================================
# REFERENCE DATA
# ==============================================

@router.get("/reference/dem-sources")
async def get_dem_sources():
    """Get available DEM sources"""
    layer = get_3d_layer()
    
    return {
        "sources": layer.dem_sources,
        "default": "SRTM"
    }


@router.get("/reference/slope-classes")
async def get_slope_classes():
    """Get slope classification definitions"""
    layer = get_3d_layer()
    
    return {
        "classes": [
            {"min_degrees": c[0], "max_degrees": c[1], "class": c[2]}
            for c in layer.slope_classes
        ]
    }
