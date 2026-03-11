"""
# ══════════════════════════════════════════════════════════════
# LEGACY FIGÉ — NE PAS MODIFIER, NE PAS RÉACTIVER, NE PAS MIGRER
# Raison: Remplacé par bionic_engine_p0/ (pipeline V7 canonique)
# Date gel: 2026-03-10
# BCE: Ce fichier est exclu du pipeline de conformité
# ══════════════════════════════════════════════════════════════
Hydrography Router - API endpoints pour l'exclusion des zones aquatiques

Endpoints:
- POST /api/hydro/filter-zones - Filtre les zones pour exclure l'eau
- GET /api/hydro/water-features - Récupère les surfaces d'eau d'une zone
- POST /api/hydro/check-point - Vérifie si un point est dans l'eau
- GET /api/hydro/sources - Liste les sources hydrographiques disponibles

Sources officielles supportées:
- Québec: Hydrographie MRNF/MSP (WFS)
- Canada: CanVec Hydrography NRCan (WFS)
- USA: USGS National Hydrography Dataset NHD (REST)
- Fallback: OpenStreetMap (Overpass API)

Auteur: BIONIC™ Team
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import logging

from hydrography_service import (
    fetch_water_features_multi_source,
    filter_zones_exclude_water,
    is_point_in_water,
    detect_region,
    SHORE_TOLERANCE_METERS,
    WATER_TYPES,
    HYDRO_SERVICES
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/hydro", tags=["Hydrography"])

# ============================================
# MODÈLES PYDANTIC
# ============================================

class ZoneInput(BaseModel):
    """Zone BIONIC à filtrer"""
    id: str
    center: List[float] = Field(..., description="[lat, lng]")
    radiusMeters: float = Field(default=100)
    moduleId: str = Field(default="habitats")
    percentage: float = Field(default=50)

class BoundsInput(BaseModel):
    """Limites de la carte"""
    north: float
    south: float
    east: float
    west: float

class FilterZonesRequest(BaseModel):
    """Requête de filtrage des zones"""
    zones: List[ZoneInput]
    bounds: BoundsInput
    tolerance_meters: float = Field(default=SHORE_TOLERANCE_METERS, description="Distance minimale du rivage (défaut: 5m)")

class FilterZonesResponse(BaseModel):
    """Réponse du filtrage des zones"""
    success: bool
    filtered_zones: List[Dict]
    stats: Dict
    message: str

class WaterFeaturesRequest(BaseModel):
    """Requête pour récupérer les surfaces d'eau"""
    lat: float
    lng: float
    radius_meters: float = Field(default=5000, description="Rayon de recherche en mètres")

class WaterFeaturesResponse(BaseModel):
    """Réponse avec les surfaces d'eau"""
    success: bool
    features: List[Dict]
    center: Dict
    radius: float
    count: int

class CheckPointRequest(BaseModel):
    """Requête pour vérifier si un point est dans l'eau"""
    lat: float
    lng: float
    tolerance_meters: float = Field(default=SHORE_TOLERANCE_METERS)
    bounds: Optional[BoundsInput] = None

class CheckPointResponse(BaseModel):
    """Réponse de vérification d'un point"""
    is_in_water: bool
    water_type: Optional[str] = None
    water_name: Optional[str] = None
    tolerance_meters: float
    message: str

# ============================================
# ENDPOINTS
# ============================================

@router.post("/filter-zones", response_model=FilterZonesResponse)
async def filter_zones_endpoint(request: FilterZonesRequest):
    """
    Filtre les zones BIONIC pour exclure celles situées dans l'eau
    
    Ce endpoint:
    1. Récupère les données hydrographiques de la zone
    2. Vérifie chaque zone contre les surfaces d'eau
    3. Exclut les zones dans l'eau ou à moins de X mètres du rivage
    4. Retourne les zones filtrées avec des statistiques
    """
    try:
        # Convertir les zones en format dict
        zones_dict = [zone.model_dump() for zone in request.zones]
        bounds_dict = request.bounds.model_dump()
        
        # Filtrer les zones
        filtered_zones, stats = await filter_zones_exclude_water(
            zones_dict,
            bounds_dict,
            request.tolerance_meters
        )
        
        return FilterZonesResponse(
            success=True,
            filtered_zones=filtered_zones,
            stats=stats,
            message=f"Filtrage terminé: {stats['filtered']}/{stats['total']} zones conservées, {stats['excluded']} exclues (eau)"
        )
        
    except Exception as e:
        logger.error(f"Error filtering zones: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du filtrage: {str(e)}")

@router.get("/water-features", response_model=WaterFeaturesResponse)
async def get_water_features_endpoint(lat: float, lng: float, radius: float = 5000):
    """
    Récupère les surfaces d'eau autour d'un point depuis les sources officielles
    
    Sources utilisées (par priorité):
    - Québec: MRNF/MSP Hydrographie
    - Canada: CanVec NRCan
    - USA: USGS NHD
    - Fallback: OpenStreetMap
    
    Types de surfaces détectées:
    - Lacs, étangs, réservoirs
    - Rivières, ruisseaux, canaux
    - Zones humides, marais
    - Océans, mers, baies
    """
    try:
        hydro_data = await fetch_water_features_multi_source(lat, lng, radius)
        features = hydro_data.get("features", [])
        
        return WaterFeaturesResponse(
            success=True,
            features=features,
            center={"lat": lat, "lng": lng},
            radius=radius,
            count=len(features)
        )
        
    except Exception as e:
        logger.error(f"Error fetching water features: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@router.post("/check-point", response_model=CheckPointResponse)
async def check_point_endpoint(request: CheckPointRequest):
    """
    Vérifie si un point spécifique est situé dans l'eau ou trop proche du rivage
    
    Utilise les sources hydrographiques officielles pour la détection.
    
    Retourne:
    - is_in_water: True si le point est dans l'eau ou à moins de X mètres du rivage
    - water_type: Type de surface d'eau (lake, river, etc.)
    - water_name: Nom de la surface d'eau si disponible
    """
    try:
        # Définir les limites de recherche
        if request.bounds:
            bounds_dict = request.bounds.model_dump()
            center_lat = (bounds_dict["north"] + bounds_dict["south"]) / 2
            center_lng = (bounds_dict["east"] + bounds_dict["west"]) / 2
            search_radius = 5000
        else:
            center_lat = request.lat
            center_lng = request.lng
            search_radius = 2000
        
        # Récupérer les données hydrographiques depuis les sources officielles
        hydro_data = await fetch_water_features_multi_source(center_lat, center_lng, search_radius)
        water_features = hydro_data.get("features", [])
        
        # Vérifier le point
        is_water, water_info = is_point_in_water(
            request.lat, 
            request.lng, 
            water_features, 
            request.tolerance_meters
        )
        
        return CheckPointResponse(
            is_in_water=is_water,
            water_type=water_info.get("type") if water_info else None,
            water_name=water_info.get("name") if water_info else None,
            tolerance_meters=request.tolerance_meters,
            message="Point dans l'eau" if is_water else "Point sur terre"
        )
        
    except Exception as e:
        logger.error(f"Error checking point: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@router.get("/water-types")
async def get_water_types():
    """
    Retourne la liste des types de surfaces d'eau détectées
    """
    return {
        "water_types": list(WATER_TYPES),
        "shore_tolerance_default": SHORE_TOLERANCE_METERS,
        "description": "Types de surfaces d'eau exclues des zones BIONIC"
    }

@router.get("/sources")
async def get_hydro_sources():
    """
    Retourne la liste des sources hydrographiques disponibles
    """
    sources_info = []
    for source, config in HYDRO_SERVICES.items():
        sources_info.append({
            "id": source.value,
            "name": config["name"],
            "type": config["type"],
            "priority": config["priority"],
            "coverage": config["bounds"]
        })
    
    return {
        "sources": sorted(sources_info, key=lambda x: x["priority"]),
        "description": "Sources hydrographiques officielles pour l'exclusion des zones aquatiques",
        "fallback": "OpenStreetMap est utilisé si aucune source officielle n'est disponible"
    }

@router.get("/sources/detect")
async def detect_sources_for_location(lat: float, lng: float):
    """
    Détecte les sources hydrographiques disponibles pour une position donnée
    """
    sources = detect_region(lat, lng)
    
    sources_info = []
    for source in sources:
        config = HYDRO_SERVICES.get(source, {})
        sources_info.append({
            "id": source.value,
            "name": config.get("name", "Unknown"),
            "priority": config.get("priority", 99)
        })
    
    return {
        "lat": lat,
        "lng": lng,
        "available_sources": sources_info,
        "primary_source": sources_info[0] if sources_info else None,
        "message": f"{len(sources_info)} source(s) disponible(s) pour cette position"
    }

logger.info("Hydrography Router initialized with multi-source support")
