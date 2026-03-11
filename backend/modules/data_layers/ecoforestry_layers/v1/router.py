"""Ecoforestry Data Layers Router - PHASE 5
API endpoints for ecoforestry data access (SIEF, forest inventory, habitat).

Version: 1.0.0
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
from pydantic import BaseModel

from ..data_layer import (
    get_ecoforestry_layer
)


router = APIRouter(
    prefix="/api/v1/data/ecoforestry",
    tags=["Data Layers - Ecoforestry"]
)


# ==============================================
# RESPONSE MODELS
# ==============================================

class HealthResponse(BaseModel):
    status: str
    layer: str
    version: str
    message: str


class StandsResponse(BaseModel):
    count: int
    stands: List[dict]


class CutsResponse(BaseModel):
    count: int
    cuts: List[dict]


class HSIResponse(BaseModel):
    species: str
    location: dict
    hsi_food: float
    hsi_cover: float
    hsi_water: float
    hsi_overall: float


# ==============================================
# HEALTH CHECK
# ==============================================

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check ecoforestry data layer health"""
    layer = get_ecoforestry_layer()
    stats = await layer.get_stats()
    
    return HealthResponse(
        status="operational",
        layer="ecoforestry_layers",
        version="1.0.0",
        message=f"Layer opérationnel - {stats['tree_species_count']} essences d'arbres configurées"
    )


@router.get("/stats")
async def get_layer_stats():
    """Get ecoforestry data layer statistics"""
    layer = get_ecoforestry_layer()
    return await layer.get_stats()


# ==============================================
# FOREST STANDS
# ==============================================

@router.get("/stands/bbox", response_model=StandsResponse)
async def get_stands_in_bbox(
    north: float = Query(..., description="North latitude boundary"),
    south: float = Query(..., description="South latitude boundary"),
    east: float = Query(..., description="East longitude boundary"),
    west: float = Query(..., description="West longitude boundary")
):
    """Get forest stands within a bounding box"""
    layer = get_ecoforestry_layer()
    stands = await layer.get_stands_in_bbox(north, south, east, west)
    
    return StandsResponse(
        count=len(stands),
        stands=[s.model_dump() for s in stands]
    )


@router.get("/stands/point")
async def get_stands_at_point(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    radius_km: float = Query(1.0, description="Search radius in km")
):
    """Get forest stands around a point"""
    layer = get_ecoforestry_layer()
    stands = await layer.get_stands_at_point(lat, lng, radius_km)
    
    return {
        "count": len(stands),
        "center": {"lat": lat, "lng": lng},
        "radius_km": radius_km,
        "stands": [s.model_dump() for s in stands]
    }


@router.get("/stands/{stand_id}")
async def get_stand_by_id(stand_id: str):
    """Get a specific forest stand by ID"""
    layer = get_ecoforestry_layer()
    stand = await layer.get_stand_by_id(stand_id)
    
    if not stand:
        raise HTTPException(status_code=404, detail="Stand not found")
    
    return stand.model_dump()


# ==============================================
# FOREST CUTS
# ==============================================

@router.get("/cuts/area", response_model=CutsResponse)
async def get_cuts_in_area(
    lat: float = Query(..., description="Center latitude"),
    lng: float = Query(..., description="Center longitude"),
    radius_km: float = Query(5.0, description="Search radius in km"),
    years_back: int = Query(10, description="Years of history")
):
    """Get forest cuts in an area"""
    layer = get_ecoforestry_layer()
    cuts = await layer.get_cuts_in_area(lat, lng, radius_km, years_back)
    
    return CutsResponse(
        count=len(cuts),
        cuts=[c.model_dump() for c in cuts]
    )


@router.get("/cuts/year/{year}")
async def get_cuts_by_year(year: int):
    """Get all forest cuts for a specific year"""
    layer = get_ecoforestry_layer()
    cuts = await layer.get_cuts_by_year(year)
    
    return {
        "year": year,
        "count": len(cuts),
        "cuts": [c.model_dump() for c in cuts]
    }


# ==============================================
# HABITAT SUITABILITY INDEX
# ==============================================

@router.get("/hsi/{species}")
async def get_hsi_data(
    species: str,
    lat: float = Query(..., description="Center latitude"),
    lng: float = Query(..., description="Center longitude"),
    radius_km: float = Query(2.0, description="Search radius in km")
):
    """Get habitat suitability index data for a species"""
    layer = get_ecoforestry_layer()
    hsi_data = await layer.get_hsi_data(species, lat, lng, radius_km)
    
    return {
        "species": species,
        "center": {"lat": lat, "lng": lng},
        "radius_km": radius_km,
        "data_points": len(hsi_data),
        "hsi_data": [h.model_dump() for h in hsi_data]
    }


@router.get("/hsi/{species}/compute", response_model=HSIResponse)
async def compute_hsi_at_point(
    species: str,
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude")
):
    """Compute HSI at a specific point"""
    layer = get_ecoforestry_layer()
    hsi = await layer.compute_hsi(species, lat, lng)
    
    return HSIResponse(
        species=hsi.species,
        location=hsi.coordinates,
        hsi_food=hsi.hsi_food,
        hsi_cover=hsi.hsi_cover,
        hsi_water=hsi.hsi_water,
        hsi_overall=hsi.hsi_overall
    )


# ==============================================
# REFERENCE DATA
# ==============================================

@router.get("/reference/tree-species")
async def get_tree_species():
    """Get all tree species codes and names"""
    layer = get_ecoforestry_layer()
    return {
        "count": len(layer.tree_species),
        "species": layer.get_all_tree_species()
    }


@router.get("/reference/forest-types")
async def get_forest_types():
    """Get forest type codes and names"""
    layer = get_ecoforestry_layer()
    return {
        "types": layer.forest_types
    }


@router.get("/reference/species-groups")
async def get_species_groups():
    """Get species group codes and names"""
    layer = get_ecoforestry_layer()
    return {
        "groups": layer.species_groups
    }
