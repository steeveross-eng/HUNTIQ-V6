"""
BIONIC ENGINE - API Router
PHASE G - P0 IMPLEMENTATION
Version: 1.0.0-alpha

Routes API pour les modules P0 du moteur BIONIC.
Prefixe: /api/v1/bionic/

Conformite: G-SEC | G-QA | G-DOC
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime
import logging

from modules.bionic_engine_p0.modules.predictive_territorial import PredictiveTerritorialService
from modules.bionic_engine_p0.modules.behavioral_models import BehavioralModelsService
from modules.bionic_engine_p0.contracts.data_contracts import (
    Species,
    TerritorialScoreInput,
    BehavioralPredictionInput
)
from modules.bionic_engine_p0.core import get_engine

# P1-HOTSPOTS: Import services cartographiques
from modules.bionic_engine_p0.services.hotspot_service import (
    HotspotService,
    HotspotRequest,
    HotspotResponse
)
from modules.bionic_engine_p0.services.zone_service import (
    ZoneService,
    ZoneRequest,
    ZoneResponse
)
from modules.bionic_engine_p0.services.corridor_service import (
    CorridorService,
    CorridorRequest,
    CorridorResponse
)

logger = logging.getLogger("bionic_engine.router")

# Router principal
router = APIRouter(prefix="/v1/bionic", tags=["BIONIC Engine P0"])

# Instances des services
_pt_service = PredictiveTerritorialService()
_bm_service = BehavioralModelsService()

# P1-HOTSPOTS: Services cartographiques
_hotspot_service = HotspotService()
_zone_service = ZoneService()
_corridor_service = CorridorService()


# =============================================================================
# HEALTH & STATUS
# =============================================================================

@router.get("/health")
async def bionic_health():
    """
    Verification sante du moteur BIONIC.
    
    G-QA: Monitoring endpoint
    """
    engine = get_engine()
    return engine.health_check()


@router.get("/modules")
async def list_modules():
    """
    Liste les modules enregistres.
    
    G-DOC: Documentation des modules actifs
    """
    return {
        "modules": [
            {
                "id": "predictive_territorial",
                "phase": "P0",
                "status": "active",
                "endpoint": "/api/v1/bionic/territorial/score"
            },
            {
                "id": "behavioral_models",
                "phase": "P0",
                "status": "active",
                "endpoint": "/api/v1/bionic/behavioral/predict"
            }
        ],
        "phase": "P0",
        "version": "1.0.0-alpha"
    }


# =============================================================================
# PREDICTIVE TERRITORIAL ENDPOINTS
# =============================================================================

@router.post("/territorial/score")
async def calculate_territorial_score(request: TerritorialScoreInput):
    """
    Calcule le score territorial predictif.
    
    Conforme a: predictive_territorial_contract.json
    P0-BETA2: Integration des 12 facteurs comportementaux avances
    
    Args:
        request: TerritorialScoreInput conforme au contrat
            - include_advanced_factors: bool (default True) - Inclure les 12 facteurs
            - snow_depth_cm: float (default 0) - Profondeur de neige
            - is_crusted: bool (default False) - Presence de croute de glace
        
    Returns:
        TerritorialScoreOutput avec score 0-100 et recommandations
        - metadata.version = "P0-beta2"
        - metadata.advanced_factors = Dict des 12 facteurs si enabled
    
    G-SEC: Validation automatique via Pydantic
    G-QA: P95 < 500ms
    """
    try:
        result = _pt_service.calculate_score(
            latitude=request.latitude,
            longitude=request.longitude,
            species=request.species,
            datetime_target=request.datetime_target,
            radius_km=request.radius_km,
            weather_override=request.weather_override,
            include_recommendations=request.include_recommendations,
            snow_depth_cm=request.snow_depth_cm,
            is_crusted=request.is_crusted,
            include_advanced_factors=request.include_advanced_factors
        )
        
        return result.dict()
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Territorial score error: {e}")
        raise HTTPException(status_code=500, detail="Calculation error")


@router.get("/territorial/score")
async def calculate_territorial_score_get(
    latitude: float = Query(..., ge=45.0, le=62.0),
    longitude: float = Query(..., ge=-80.0, le=-57.0),
    species: str = Query(default="moose"),
    datetime_str: Optional[str] = Query(default=None, alias="datetime"),
    radius_km: float = Query(default=5.0, ge=0.5, le=25.0)
):
    """
    Calcule le score territorial (version GET simplifiee).
    
    G-DOC: Endpoint simplifie pour tests rapides
    """
    try:
        # Parse species
        species_enum = Species(species)
        
        # Parse datetime
        dt = None
        if datetime_str:
            dt = datetime.fromisoformat(datetime_str)
        
        result = _pt_service.calculate_score(
            latitude=latitude,
            longitude=longitude,
            species=species_enum,
            datetime_target=dt,
            radius_km=radius_km,
            include_recommendations=True
        )
        
        return result.dict()
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Territorial score error: {e}")
        raise HTTPException(status_code=500, detail="Calculation error")


# =============================================================================
# BEHAVIORAL MODELS ENDPOINTS
# =============================================================================

@router.post("/behavioral/predict")
async def predict_behavior(request: BehavioralPredictionInput):
    """
    Prediction comportementale complete.
    
    Conforme a: behavioral_models_contract.json
    P0-BETA2: Integration des 12 facteurs comportementaux avances
    
    Args:
        request: BehavioralPredictionInput conforme au contrat
            - include_advanced_factors: bool (default True) - Inclure les 12 facteurs
            - snow_depth_cm: float (default 0) - Profondeur de neige
            - is_crusted: bool (default False) - Presence de croute de glace
        
    Returns:
        BehavioralPredictionOutput avec activite, timeline, strategies
        - metadata.version = "P0-beta2"
        - metadata.advanced_factors = Dict des 12 facteurs si enabled
    
    G-SEC: Validation automatique via Pydantic
    G-QA: P95 < 300ms
    """
    try:
        result = _bm_service.predict_behavior(
            species=request.species,
            datetime_target=request.datetime_target,
            latitude=request.latitude,
            longitude=request.longitude,
            weather_context=request.weather_context,
            include_strategy=request.include_strategy,
            snow_depth_cm=request.snow_depth_cm,
            is_crusted=request.is_crusted,
            include_advanced_factors=request.include_advanced_factors
        )
        
        return result.dict()
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Behavioral prediction error: {e}")
        raise HTTPException(status_code=500, detail="Prediction error")


@router.get("/behavioral/activity")
async def get_current_activity(
    species: str = Query(...),
    datetime_str: Optional[str] = Query(default=None, alias="datetime")
):
    """
    Obtient le niveau d'activite actuel (endpoint simplifie).
    
    G-DOC: Pour integration rapide
    """
    try:
        species_enum = Species(species)
        dt = None
        if datetime_str:
            dt = datetime.fromisoformat(datetime_str)
        
        result = _bm_service.predict_activity(
            species=species_enum,
            datetime_target=dt or datetime.now()
        )
        
        return result.dict()
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Activity error: {e}")
        raise HTTPException(status_code=500, detail="Error")


@router.get("/behavioral/timeline")
async def get_activity_timeline(
    species: str = Query(...),
    date: Optional[str] = Query(default=None)
):
    """
    Obtient la timeline d'activite 24h.
    
    G-DOC: 24 entrees, une par heure
    """
    try:
        species_enum = Species(species)
        dt = datetime.now()
        if date:
            dt = datetime.fromisoformat(date)
        
        timeline = _bm_service.get_activity_timeline(
            species=species_enum,
            date=dt
        )
        
        return {
            "species": species,
            "date": dt.date().isoformat(),
            "timeline": [entry.dict() for entry in timeline]
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Timeline error: {e}")
        raise HTTPException(status_code=500, detail="Error")


# =============================================================================
# COMBINED ENDPOINTS
# =============================================================================

@router.get("/analysis")
async def combined_analysis(
    latitude: float = Query(..., ge=45.0, le=62.0),
    longitude: float = Query(..., ge=-80.0, le=-57.0),
    species: str = Query(default="moose"),
    datetime_str: Optional[str] = Query(default=None, alias="datetime")
):
    """
    Analyse combinee: territorial + behavioral.
    
    Retourne les deux analyses en un seul appel.
    
    G-QA: Optimisation pour frontend
    """
    try:
        species_enum = Species(species)
        dt = None
        if datetime_str:
            dt = datetime.fromisoformat(datetime_str)
        
        # Score territorial
        territorial = _pt_service.calculate_score(
            latitude=latitude,
            longitude=longitude,
            species=species_enum,
            datetime_target=dt,
            include_recommendations=True
        )
        
        # Prediction comportementale
        behavioral = _bm_service.predict_behavior(
            species=species_enum,
            datetime_target=dt,
            latitude=latitude,
            longitude=longitude,
            include_strategy=True
        )
        
        return {
            "success": True,
            "territorial": territorial.dict(),
            "behavioral": behavioral.dict(),
            "combined_score": round(
                (territorial.overall_score * 0.5 + behavioral.activity.activity_score * 0.5),
                1
            ),
            "metadata": {
                "species": species,
                "latitude": latitude,
                "longitude": longitude,
                "datetime": (dt or datetime.now()).isoformat()
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Combined analysis error: {e}")
        raise HTTPException(status_code=500, detail="Analysis error")



# =============================================================================
# P1-HOTSPOTS - MAP ENDPOINTS
# =============================================================================

@router.post("/map/hotspots", response_model=HotspotResponse)
async def get_map_hotspots(request: HotspotRequest):
    """
    Genere les hotspots cartographiques pour une zone.
    
    PHASE P1-HOTSPOTS - Endpoint principal
    
    Specifications visuelles BIONIC V5:
    - Contours ultra-fins (1-2px)
    - Centre 100% transparent (fill_opacity = 0)
    - Formes naturelles (Chaikin smoothing)
    - ZERO glow, shadow, halo
    
    Args:
        request: HotspotRequest conforme au contrat hotspot_contract.json
            - bounds: Zone geographique (north, south, east, west)
            - species: Liste d'especes ["moose", "deer", ...]
            - time_range: "24h" | "72h" | "7d"
            - hotspot_types: Types de hotspots a generer
            - min_score_threshold: Seuil minimum (default 70)
            
    Returns:
        HotspotResponse avec hotspots GeoJSON pre-calcules
        - hotspots[].geometry: Polygones prets pour Leaflet
        - hotspots[].style: Styles visuels conformes
        - statistics: Metriques de couverture
        
    G-QA: P95 < 2000ms
    G-SEC: Validation automatique via Pydantic
    """
    try:
        result = _hotspot_service.generate_hotspots(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Hotspot generation error: {e}")
        raise HTTPException(status_code=500, detail="Hotspot generation error")


@router.post("/map/zones", response_model=ZoneResponse)
async def get_map_zones(request: ZoneRequest):
    """
    Genere les zones comportementales pour une zone.
    
    PHASE P1-HOTSPOTS - Zones comportementales
    
    Types de zones:
    - feeding: Zones d'alimentation
    - bedding: Zones de repos
    - rut_arena: Arenes de rut
    - thermal_cover: Couvert thermique
    - water_access: Acces a l'eau
    - predation_zone: Zones de predation
    - yarding_zone: Ravages hivernaux
    
    Args:
        request: ZoneRequest conforme au contrat zone_contract.json
            - bounds: Zone geographique
            - species: Espece cible
            - zone_types: Types de zones a generer
            - include_overlaps: Calculer la matrice de superposition
            
    Returns:
        ZoneResponse avec zones GeoJSON
        - zones[].geometry: Polygones prets pour Leaflet
        - overlap_matrix: Relations entre zones
        
    G-QA: P95 < 1500ms
    """
    try:
        result = _zone_service.generate_zones(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Zone generation error: {e}")
        raise HTTPException(status_code=500, detail="Zone generation error")


@router.post("/map/corridors", response_model=CorridorResponse)
async def get_map_corridors(request: CorridorRequest):
    """
    Genere les corridors de deplacement pour une zone.
    
    PHASE P1-HOTSPOTS - Corridors de deplacement
    
    Types de corridors:
    - movement: Corridors principaux
    - avoidance: Corridors d'evitement
    - preferred: Routes preferees
    - feeding_transit: Transit alimentation-repos
    
    Args:
        request: CorridorRequest conforme au contrat corridor_contract.json
            - bounds: Zone geographique
            - species: Espece cible
            - corridor_types: Types de corridors
            - connect_zones: Connecter aux zones comportementales
            
    Returns:
        CorridorResponse avec corridors GeoJSON
        - corridors[].geometry: LineStrings prets pour Leaflet
        - corridors[].movement_context: Contexte de deplacement
        
    G-QA: P95 < 1200ms
    """
    try:
        result = _corridor_service.generate_corridors(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Corridor generation error: {e}")
        raise HTTPException(status_code=500, detail="Corridor generation error")


@router.get("/map/status")
async def get_map_engine_status():
    """
    Statut du module P1-HOTSPOTS.
    
    G-DOC: Endpoint de monitoring
    """
    return {
        "module": "P1-HOTSPOTS",
        "version": "1.0.0",
        "status": "active",
        "endpoints": [
            {
                "path": "/api/v1/bionic/map/hotspots",
                "method": "POST",
                "description": "Hotspots cartographiques"
            },
            {
                "path": "/api/v1/bionic/map/zones",
                "method": "POST",
                "description": "Zones comportementales"
            },
            {
                "path": "/api/v1/bionic/map/corridors",
                "method": "POST",
                "description": "Corridors de deplacement"
            }
        ],
        "visual_spec": {
            "contour_width_px": "1-2",
            "fill_opacity": 0,
            "smoothing": "chaikin",
            "effects": "none"
        }
    }
