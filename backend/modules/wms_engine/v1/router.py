"""WMS Engine Router - CORE

FastAPI router for WMS layer management.

Version: 1.0.0
API Prefix: /api/v1/wms
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from .service import WMSService
from .models import MapExtent, TileRequest

router = APIRouter(prefix="/api/v1/wms", tags=["WMS Engine"])

# Initialize service
_service = WMSService()


@router.get("/")
async def wms_engine_info():
    """Get WMS engine information"""
    return {
        "module": "wms_engine",
        "version": "1.0.0",
        "description": "WMS layer management for hunting maps",
        "layers_count": len(_service.QUEBEC_LAYERS),
        "categories": _service.CATEGORIES,
        "features": [
            "Quebec government WMS layers",
            "Hunting zones",
            "Terrain data",
            "Forest inventory",
            "Hydrography"
        ]
    }


@router.get("/layers")
async def list_layers(category: Optional[str] = None):
    """
    List all available WMS layers.
    
    Args:
        category: Optional filter by category
    """
    if category:
        if category not in _service.CATEGORIES:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": f"Invalid category '{category}'",
                    "available_categories": list(_service.CATEGORIES.keys())
                }
            )
        layers = _service.get_layers_by_category(category)
    else:
        layers = _service.get_all_layers()
    
    return {
        "success": True,
        "count": len(layers),
        "layers": [layer.model_dump() for layer in layers]
    }


@router.get("/layers/{layer_id}")
async def get_layer(layer_id: str):
    """Get a specific layer by ID"""
    layer = _service.get_layer(layer_id)
    
    if not layer:
        raise HTTPException(
            status_code=404,
            detail={
                "message": f"Layer '{layer_id}' not found",
                "available_layers": list(_service.QUEBEC_LAYERS.keys())
            }
        )
    
    return {
        "success": True,
        "layer": layer.model_dump()
    }


@router.get("/layers/hunting/all")
async def get_hunting_layers():
    """Get all hunting-related layers"""
    layers = _service.get_hunting_layers()
    
    return {
        "success": True,
        "count": len(layers),
        "layers": [layer.model_dump() for layer in layers]
    }


@router.get("/categories")
async def list_categories():
    """List all layer categories"""
    categories_with_counts = []
    
    for cat_id, cat_name in _service.CATEGORIES.items():
        layers = _service.get_layers_by_category(cat_id)
        categories_with_counts.append({
            "id": cat_id,
            "name": cat_name,
            "layer_count": len(layers)
        })
    
    return {
        "success": True,
        "categories": categories_with_counts
    }


@router.post("/url")
async def build_wms_url(request: TileRequest):
    """
    Build a WMS GetMap URL for a layer.
    
    Returns the complete URL to fetch the map tile.
    """
    layer = _service.get_layer(request.layer_id)
    
    if not layer:
        raise HTTPException(status_code=404, detail=f"Layer '{request.layer_id}' not found")
    
    url = _service.build_wms_url(
        layer=layer,
        extent=request.extent,
        width=request.width,
        height=request.height
    )
    
    return {
        "success": True,
        "layer_id": request.layer_id,
        "wms_url": url
    }


@router.get("/recommend")
async def get_recommendations(
    use_case: str = Query("general", description="Use case: general, scouting, navigation, planning")
):
    """Get recommended layers for a specific use case"""
    valid_cases = ["general", "scouting", "navigation", "planning"]
    
    if use_case not in valid_cases:
        raise HTTPException(
            status_code=400,
            detail={
                "message": f"Invalid use case '{use_case}'",
                "valid_cases": valid_cases
            }
        )
    
    layer_ids = _service.get_recommended_layers(use_case)
    layers = [_service.get_layer(lid) for lid in layer_ids if _service.get_layer(lid)]
    
    return {
        "success": True,
        "use_case": use_case,
        "recommended_layers": [layer.model_dump() for layer in layers]
    }


@router.post("/validate-extent")
async def validate_extent(extent: MapExtent):
    """Validate that an extent is within Quebec bounds"""
    is_valid = _service.validate_extent(extent)
    
    return {
        "success": True,
        "extent": extent.model_dump(),
        "is_valid": is_valid,
        "message": "Extent is within Quebec bounds" if is_valid else "Extent is outside Quebec bounds"
    }


@router.get("/bounds/quebec")
async def get_quebec_bounds():
    """Get Quebec geographic bounds"""
    return {
        "success": True,
        "bounds": {
            "min_lat": 44.99,
            "max_lat": 62.59,
            "min_lon": -79.76,
            "max_lon": -57.10,
            "center_lat": 53.79,
            "center_lon": -68.43
        },
        "note": "EPSG:4326 coordinates"
    }
