"""
BIONIC V5 — GPS ULTIMATE ROUTER (PHASE F)
==========================================
PHASE F — GPS ULTIMATE

Endpoints REST pour les services temps réel:
- Auto-Cartography Engine (hotspots, corridors dynamiques)
- Safety Engine (zones de danger, alertes)

VERSION: 7.0.0
Conformité: G-SEC | G-QA | G-DOC | BIONIC V5 PHASE F
"""

import logging
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from fastapi import APIRouter, HTTPException, status, Query

# Imports des engines
from modules.bionic_engine_p0.knowledge.gps_ultimate.auto_cartography import (
    get_auto_cartography_engine
)
from modules.bionic_engine_p0.knowledge.gps_ultimate.safety_engine import (
    get_safety_engine
)

logger = logging.getLogger(__name__)

# =============================================================================
# ROUTER
# =============================================================================

router = APIRouter(tags=["BIONIC GPS Ultimate"])


# =============================================================================
# SCHEMAS
# =============================================================================

class GenerateHotspotsRequest(BaseModel):
    """Requête de génération de hotspots."""
    
    center_lat: float = Field(..., ge=-90, le=90, description="Latitude du centre")
    center_lng: float = Field(..., ge=-180, le=180, description="Longitude du centre")
    radius_km: float = Field(5.0, ge=0.5, le=50, description="Rayon de recherche en km")
    species: str = Field("moose", description="Espèce cible")
    include_corridors: bool = Field(True, description="Inclure les corridors dynamiques")
    
    class Config:
        json_schema_extra = {
            "example": {
                "center_lat": 46.8139,
                "center_lng": -71.2080,
                "radius_km": 5.0,
                "species": "moose",
                "include_corridors": True
            }
        }


class CheckSafetyRequest(BaseModel):
    """Requête de vérification de sécurité."""
    
    lat: float = Field(..., ge=-90, le=90, description="Latitude de la position")
    lng: float = Field(..., ge=-180, le=180, description="Longitude de la position")
    radius_m: float = Field(500.0, ge=50, le=5000, description="Rayon de détection en mètres")
    
    class Config:
        json_schema_extra = {
            "example": {
                "lat": 46.8139,
                "lng": -71.2080,
                "radius_m": 500.0
            }
        }


class ReportDangerRequest(BaseModel):
    """Requête de signalement de danger."""
    
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lng: float = Field(..., ge=-180, le=180, description="Longitude")
    danger_type: str = Field("human_presence", description="Type de danger")
    description: str = Field("", description="Description")
    radius_m: float = Field(200.0, description="Rayon de la zone")
    
    class Config:
        json_schema_extra = {
            "example": {
                "lat": 46.82,
                "lng": -71.20,
                "danger_type": "hunting_active",
                "description": "Chasse active observée",
                "radius_m": 300.0
            }
        }


# =============================================================================
# ENDPOINTS - AUTO-CARTOGRAPHY
# =============================================================================

@router.post(
    "/gps/hotspots/generate",
    response_model=dict,
    summary="Générer des hotspots automatiquement",
    description="""
    PHASE F — AUTO-CARTOGRAPHY ENGINE
    
    Génère automatiquement des hotspots d'activité basés sur:
    - Les données de NIVEAU 1-6
    - La position centrale et le rayon de recherche
    - L'espèce cible
    
    Retourne des zones d'intérêt en format GeoJSON.
    """
)
async def generate_hotspots(request: GenerateHotspotsRequest):
    """Génère des hotspots automatiquement."""
    
    try:
        engine = get_auto_cartography_engine()
        
        # Déterminer l'heure actuelle
        current_hour = datetime.now(timezone.utc).hour
        
        # Générer les hotspots
        hotspots = engine.generate_hotspots(
            center_lat=request.center_lat,
            center_lng=request.center_lng,
            search_radius_km=request.radius_km,
            species=request.species,
            current_hour=current_hour
        )
        
        # Convertir en GeoJSON
        features = [h.to_geojson_feature() for h in hotspots]
        
        # Optionnellement inclure les corridors
        corridor_features = []
        if request.include_corridors and len(hotspots) >= 2:
            corridors = engine.generate_dynamic_corridors(
                hotspots=hotspots
            )
            corridor_features = [c.to_geojson_feature() for c in corridors]
        
        return {
            "status": "success",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "parameters": {
                "center": [request.center_lat, request.center_lng],
                "radius_km": request.radius_km,
                "species": request.species
            },
            "hotspots": {
                "type": "FeatureCollection",
                "features": features,
                "count": len(features)
            },
            "corridors": {
                "type": "FeatureCollection",
                "features": corridor_features,
                "count": len(corridor_features)
            },
            "metadata": {
                "engine": "AutoCartographyEngine",
                "version": "7.0.0",
                "phase": "PHASE F"
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to generate hotspots: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": True, "message": str(e)}
        )


@router.get(
    "/gps/hotspots/stats",
    response_model=dict,
    summary="Statistiques du moteur de cartographie",
    description="Retourne les statistiques du moteur Auto-Cartography."
)
async def get_cartography_stats():
    """Statistiques du moteur de cartographie."""
    
    try:
        engine = get_auto_cartography_engine()
        stats = engine.get_stats()
        
        return {
            "status": "success",
            "engine": "AutoCartographyEngine",
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get stats: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": True, "message": str(e)}
        )


# =============================================================================
# ENDPOINTS - SAFETY ENGINE
# =============================================================================

@router.post(
    "/gps/safety/check",
    response_model=dict,
    summary="Vérifier la sécurité d'une position",
    description="""
    PHASE F — SAFETY ENGINE
    
    Analyse la sécurité autour d'une position:
    - Détecte les zones de danger actives
    - Calcule un score de sécurité global
    - Génère des alertes si nécessaire
    
    Intègre NIVEAU 3 (Pression Humaine).
    """
)
async def check_safety(request: CheckSafetyRequest):
    """Vérifie la sécurité d'une position."""
    
    try:
        engine = get_safety_engine()
        
        # Analyser la sécurité
        danger_zones, alerts = engine.analyze_safety(
            center_lat=request.lat,
            center_lng=request.lng,
            search_radius_km=request.radius_m / 1000.0  # Convertir en km
        )
        
        # Convertir en GeoJSON
        danger_features = [z.to_geojson_feature() for z in danger_zones]
        
        # Calculer le score de sécurité global
        if danger_zones:
            max_threat = max(z.threat_score for z in danger_zones)
            overall_score = 1.0 - max_threat
            is_safe = all(z.danger_level.value in ['none', 'low'] for z in danger_zones)
        else:
            overall_score = 1.0
            is_safe = True
        
        return {
            "status": "success",
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "position": {
                "lat": request.lat,
                "lng": request.lng
            },
            "safety_assessment": {
                "overall_score": round(overall_score, 2),
                "danger_level": danger_zones[0].danger_level.value if danger_zones else "none",
                "is_safe": is_safe,
                "recommendations": ["Zone sécuritaire" if is_safe else "Vigilance recommandée"]
            },
            "active_threats": {
                "count": len(danger_zones),
                "zones": danger_features
            },
            "alerts": [
                {
                    "id": alert.alert_id,
                    "priority": alert.priority.value,
                    "title": alert.title,
                    "message": alert.message,
                    "timestamp": alert.timestamp.isoformat()
                }
                for alert in alerts
            ],
            "metadata": {
                "engine": "SafetyEngine",
                "version": "7.0.0",
                "phase": "PHASE F"
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to check safety: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": True, "message": str(e)}
        )


@router.post(
    "/gps/safety/report",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Signaler un danger",
    description="""
    PHASE F — SAFETY ENGINE
    
    Permet de signaler un danger observé sur le terrain.
    Ce signalement crée une zone de danger temporaire
    et peut déclencher des alertes pour les autres chasseurs.
    """
)
async def report_danger(request: ReportDangerRequest):
    """Signale un danger observé."""
    
    try:
        engine = get_safety_engine()
        
        # Créer la zone de danger
        zone = engine.report_danger(
            lat=request.lat,
            lng=request.lng,
            danger_type=request.danger_type,
            description=request.description,
            radius_m=request.radius_m
        )
        
        return {
            "status": "success",
            "message": "Danger signalé avec succès",
            "danger_zone": zone.to_geojson_feature(),
            "zone_id": zone.zone_id,
            "expires_at": zone.expires_at.isoformat() if zone.expires_at else None,
            "metadata": {
                "engine": "SafetyEngine",
                "version": "7.0.0"
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to report danger: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": True, "message": str(e)}
        )


@router.get(
    "/gps/safety/zones",
    response_model=dict,
    summary="Lister les zones de danger actives",
    description="Retourne toutes les zones de danger actuellement actives."
)
async def list_danger_zones(
    active_only: bool = Query(True, description="Uniquement les zones actives")
):
    """Liste les zones de danger."""
    
    try:
        engine = get_safety_engine()
        zones = engine.list_danger_zones(active_only=active_only)
        
        features = [z.to_geojson_feature() for z in zones]
        
        return {
            "status": "success",
            "danger_zones": {
                "type": "FeatureCollection",
                "features": features,
                "count": len(features)
            },
            "filters": {
                "active_only": active_only
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to list zones: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": True, "message": str(e)}
        )


@router.get(
    "/gps/safety/stats",
    response_model=dict,
    summary="Statistiques du moteur de sécurité",
    description="Retourne les statistiques du Safety Engine."
)
async def get_safety_stats():
    """Statistiques du moteur de sécurité."""
    
    try:
        engine = get_safety_engine()
        stats = engine.get_stats()
        
        return {
            "status": "success",
            "engine": "SafetyEngine",
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get stats: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": True, "message": str(e)}
        )


# =============================================================================
# HEALTH CHECK
# =============================================================================

@router.get("/gps/health")
async def gps_ultimate_health():
    """Vérification santé des services GPS Ultimate."""
    
    try:
        cartography_engine = get_auto_cartography_engine()
        safety_engine = get_safety_engine()
        
        return {
            "status": "healthy",
            "phase": "PHASE F - GPS ULTIMATE",
            "version": "7.0.0",
            "engines": {
                "auto_cartography": {
                    "status": "active",
                    "version": cartography_engine._version
                },
                "safety": {
                    "status": "active",
                    "version": safety_engine._version
                }
            },
            "features": [
                "hotspot_generation",
                "dynamic_corridors",
                "danger_zone_detection",
                "real_time_alerts",
                "safety_scoring"
            ]
        }
        
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e)
        }
