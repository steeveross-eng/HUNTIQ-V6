"""Advanced Geospatial Data Layers Router - PHASE 5
API endpoints for corridors, concentration zones, and connectivity analysis.

Version: 1.0.0
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pydantic import BaseModel

from ..data_layer import get_advanced_geospatial_layer


router = APIRouter(
    prefix="/api/v1/data/geospatial-advanced",
    tags=["Data Layers - Advanced Geospatial"]
)


# ==============================================
# RESPONSE MODELS
# ==============================================

class HealthResponse(BaseModel):
    status: str
    layer: str
    version: str
    message: str


# ==============================================
# HEALTH CHECK
# ==============================================

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check advanced geospatial data layer health"""
    layer = get_advanced_geospatial_layer()
    stats = await layer.get_stats()
    
    return HealthResponse(
        status="operational",
        layer="advanced_geospatial_layers",
        version="1.0.0",
        message=f"Layer opérationnel - {len(stats['corridor_types'])} types de corridors, {len(stats['zone_types'])} types de zones"
    )


@router.get("/stats")
async def get_layer_stats():
    """Get advanced geospatial data layer statistics"""
    layer = get_advanced_geospatial_layer()
    return await layer.get_stats()


# ==============================================
# CORRIDORS
# ==============================================

@router.get("/corridors")
async def get_corridors_in_area(
    lat: float = Query(..., description="Center latitude"),
    lng: float = Query(..., description="Center longitude"),
    radius_km: float = Query(5.0, description="Search radius in km"),
    species: Optional[str] = Query(None, description="Filter by species"),
    corridor_type: Optional[str] = Query(None, description="Filter by type: travel, migration, daily, seasonal")
):
    """Get wildlife corridors in an area"""
    layer = get_advanced_geospatial_layer()
    corridors = await layer.get_corridors_in_area(lat, lng, radius_km, species, corridor_type)
    
    return {
        "center": {"lat": lat, "lng": lng},
        "radius_km": radius_km,
        "count": len(corridors),
        "corridors": [c.model_dump() for c in corridors]
    }


@router.get("/corridors/{corridor_id}")
async def get_corridor_by_id(corridor_id: str):
    """Get a specific corridor by ID"""
    layer = get_advanced_geospatial_layer()
    corridor = await layer.get_corridor_by_id(corridor_id)
    
    if not corridor:
        raise HTTPException(status_code=404, detail="Corridor not found")
    
    return corridor.model_dump()


# ==============================================
# CONCENTRATION ZONES
# ==============================================

@router.get("/zones")
async def get_zones_in_area(
    lat: float = Query(..., description="Center latitude"),
    lng: float = Query(..., description="Center longitude"),
    radius_km: float = Query(5.0, description="Search radius in km"),
    species: Optional[str] = Query(None, description="Filter by species"),
    zone_type: Optional[str] = Query(None, description="Filter by type: feeding, bedding, watering, staging, crossing")
):
    """Get concentration zones in an area"""
    layer = get_advanced_geospatial_layer()
    zones = await layer.get_zones_in_area(lat, lng, radius_km, species, zone_type)
    
    return {
        "center": {"lat": lat, "lng": lng},
        "radius_km": radius_km,
        "count": len(zones),
        "zones": [z.model_dump() for z in zones]
    }


@router.get("/zones/feeding")
async def get_feeding_zones(
    lat: float = Query(..., description="Center latitude"),
    lng: float = Query(..., description="Center longitude"),
    radius_km: float = Query(5.0, description="Search radius in km"),
    species: Optional[str] = Query(None, description="Filter by species")
):
    """Get feeding zones specifically"""
    layer = get_advanced_geospatial_layer()
    zones = await layer.get_feeding_zones(lat, lng, radius_km, species)
    
    return {
        "zone_type": "feeding",
        "count": len(zones),
        "zones": [z.model_dump() for z in zones]
    }


@router.get("/zones/bedding")
async def get_bedding_zones(
    lat: float = Query(..., description="Center latitude"),
    lng: float = Query(..., description="Center longitude"),
    radius_km: float = Query(5.0, description="Search radius in km"),
    species: Optional[str] = Query(None, description="Filter by species")
):
    """Get bedding zones specifically"""
    layer = get_advanced_geospatial_layer()
    zones = await layer.get_bedding_zones(lat, lng, radius_km, species)
    
    return {
        "zone_type": "bedding",
        "count": len(zones),
        "zones": [z.model_dump() for z in zones]
    }


# ==============================================
# CONNECTIVITY
# ==============================================

@router.get("/connectivity")
async def analyze_connectivity(
    lat: float = Query(..., description="Center latitude"),
    lng: float = Query(..., description="Center longitude"),
    radius_km: float = Query(5.0, description="Analysis radius in km")
):
    """Analyze habitat connectivity in an area"""
    layer = get_advanced_geospatial_layer()
    analysis = await layer.analyze_connectivity(lat, lng, radius_km)
    
    return analysis.model_dump()


@router.get("/barriers")
async def get_barriers_in_area(
    lat: float = Query(..., description="Center latitude"),
    lng: float = Query(..., description="Center longitude"),
    radius_km: float = Query(5.0, description="Search radius in km")
):
    """Get movement barriers in an area"""
    layer = get_advanced_geospatial_layer()
    barriers = await layer.get_barriers_in_area(lat, lng, radius_km)
    
    return {
        "center": {"lat": lat, "lng": lng},
        "radius_km": radius_km,
        "count": len(barriers),
        "barriers": barriers
    }


# ==============================================
# HEATMAPS
# ==============================================

@router.get("/heatmap")
async def generate_heatmap(
    north: float = Query(..., description="North boundary"),
    south: float = Query(..., description="South boundary"),
    east: float = Query(..., description="East boundary"),
    west: float = Query(..., description="West boundary"),
    species: Optional[str] = Query(None, description="Filter by species"),
    resolution_m: float = Query(100, description="Cell resolution in meters")
):
    """Generate activity heatmap for an area"""
    layer = get_advanced_geospatial_layer()
    heatmap = await layer.generate_heatmap(north, south, east, west, species, resolution_m)
    
    return heatmap.model_dump()


@router.post("/heatmap/hotspots")
async def extract_hotspots(
    north: float = Query(..., description="North boundary"),
    south: float = Query(..., description="South boundary"),
    east: float = Query(..., description="East boundary"),
    west: float = Query(..., description="West boundary"),
    species: Optional[str] = Query(None, description="Filter by species"),
    threshold: float = Query(0.7, description="Hotspot threshold (0-1)")
):
    """Extract hotspots from activity heatmap"""
    layer = get_advanced_geospatial_layer()
    
    # Generate heatmap
    heatmap = await layer.generate_heatmap(north, south, east, west, species)
    
    # Extract hotspots
    hotspots = await layer.get_hotspots(heatmap, threshold)
    
    return {
        "threshold": threshold,
        "hotspot_count": len(hotspots),
        "hotspots": hotspots
    }


# ==============================================
# REFERENCE DATA
# ==============================================

@router.get("/reference/corridor-types")
async def get_corridor_types():
    """Get available corridor types"""
    layer = get_advanced_geospatial_layer()
    stats = await layer.get_stats()
    
    return {
        "corridor_types": stats["corridor_types"],
        "descriptions": {
            "travel": "Corridor de déplacement quotidien",
            "migration": "Corridor de migration saisonnière",
            "daily": "Corridor d'activité journalière",
            "seasonal": "Corridor d'utilisation saisonnière"
        }
    }


@router.get("/reference/zone-types")
async def get_zone_types():
    """Get available zone types"""
    layer = get_advanced_geospatial_layer()
    stats = await layer.get_stats()
    
    return {
        "zone_types": stats["zone_types"],
        "descriptions": {
            "feeding": "Zone d'alimentation",
            "bedding": "Zone de repos",
            "watering": "Zone d'abreuvement",
            "staging": "Zone de rassemblement",
            "crossing": "Zone de traversée"
        }
    }


@router.get("/reference/barrier-types")
async def get_barrier_types():
    """Get available barrier types"""
    layer = get_advanced_geospatial_layer()
    
    return {
        "barrier_types": layer.barrier_types
    }
