"""Ecoforestry Engine Router - PLAN MAITRE
FastAPI router for ecoforestry data and habitat analysis.

Version: 1.0.0
API Prefix: /api/v1/ecoforestry
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from .service import EcoforestryService
from .models import EcoforestryRequest

router = APIRouter(prefix="/api/v1/ecoforestry", tags=["Ecoforestry Engine"])

_service = EcoforestryService()


@router.get("/")
async def ecoforestry_engine_info():
    """Get ecoforestry engine information"""
    stats = await _service.get_stats()
    
    return {
        "module": "ecoforestry_engine",
        "version": "1.0.0",
        "phase": 4,
        "description": "Données écoforestières et analyse d'habitats",
        "status": "operational",
        "features": [
            "Types de peuplements forestiers",
            "Âge et densité des forêts",
            "Coupes récentes et régénération",
            "Habitats favorables par espèce",
            "Données SIEF"
        ],
        "statistics": stats
    }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "module": "ecoforestry_engine", "version": "1.0.0"}


@router.post("/analyze")
async def analyze_area(request: EcoforestryRequest):
    """Analyze ecoforestry data for an area"""
    try:
        response = await _service.analyze_area(request)
        return {"success": True, "data": response.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stands")
async def get_forest_stands(
    lat: float = Query(...),
    lng: float = Query(...),
    radius_km: float = Query(5.0, ge=0.5, le=50)
):
    """Get forest stands in area"""
    stands = await _service.get_stands(lat, lng, radius_km)
    return {
        "success": True,
        "total": len(stands),
        "stands": [s.model_dump() for s in stands]
    }


@router.get("/habitats/{species}")
async def analyze_habitat(
    species: str,
    lat: float = Query(...),
    lng: float = Query(...),
    radius_km: float = Query(5.0, ge=0.5, le=50)
):
    """Analyze habitat suitability for a species"""
    habitat = await _service.analyze_habitat(
        species, {"lat": lat, "lng": lng}, radius_km
    )
    return {"success": True, "habitat": habitat.model_dump()}


@router.get("/analyze/{coordinates}")
async def analyze_coordinates(
    coordinates: str,
    species: Optional[str] = Query(None),
    radius_km: float = Query(5.0)
):
    """Analyze ecoforestry data at coordinates (format: lat,lng)"""
    try:
        lat, lng = map(float, coordinates.split(","))
    except ValueError:
        raise HTTPException(status_code=400, detail="Format: lat,lng")
    
    request = EcoforestryRequest(
        lat=lat, lng=lng, radius_km=radius_km, species=species
    )
    response = await _service.analyze_area(request)
    return {"success": True, "data": response.model_dump()}


@router.get("/cuts")
async def get_recent_cuts(
    lat: float = Query(...),
    lng: float = Query(...),
    radius_km: float = Query(10.0, ge=1, le=50),
    years_back: int = Query(5, ge=1, le=20)
):
    """Get recent forest cuts in area"""
    cuts = await _service.get_recent_cuts(lat, lng, radius_km, years_back)
    return {
        "success": True,
        "total": len(cuts),
        "cuts": [c.model_dump() for c in cuts]
    }
