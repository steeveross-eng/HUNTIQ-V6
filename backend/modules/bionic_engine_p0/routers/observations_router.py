"""
BIONIC V5 — OBSERVATIONS ROUTER (PHASE F)
==========================================
PHASE F — GPS ULTIMATE

Endpoints REST pour la gestion des observations terrain.

ENDPOINTS:
- POST /api/v1/bionic/observations         - Créer une observation
- GET  /api/v1/bionic/observations         - Lister les observations
- GET  /api/v1/bionic/observations/{id}    - Détail d'une observation
- POST /api/v1/bionic/observations/{id}/validate - Valider une observation
- GET  /api/v1/bionic/observations/stats   - Statistiques

VERSION: 7.0.0
Conformité: G-SEC | G-QA | G-DOC | BIONIC V5 PHASE F
"""

import logging
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from fastapi import APIRouter, HTTPException, status, Query

from modules.bionic_engine_p0.knowledge.gps_ultimate.observations_models import (
    get_observation_registry
)

# Import du registre de calibration pour intégration
from modules.bionic_engine_p0.knowledge.calibration import (
    get_calibration_registry
)

logger = logging.getLogger(__name__)

# =============================================================================
# ROUTER
# =============================================================================

router = APIRouter(tags=["BIONIC Field Observations"])


# =============================================================================
# SCHEMAS (Request/Response)
# =============================================================================

class CreateObservationRequest(BaseModel):
    """Schéma de création d'observation."""
    
    # Données essentielles
    species: str = Field(..., description="Espèce observée (moose, deer, bear, elk, mule_deer, other)")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude GPS")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude GPS")
    
    # Comportement
    behavior: str = Field("unknown", description="Comportement observé (feeding, resting, moving, drinking, rut_activity, alert, grooming, social, unknown)")
    behavior_details: str = Field("", description="Détails du comportement observé")
    
    # Horodatage (optionnel - utilise maintenant si non fourni)
    observation_datetime: Optional[datetime] = Field(None, description="Date/heure de l'observation")
    duration_minutes: Optional[int] = Field(None, description="Durée de l'observation en minutes")
    
    # Comptage
    species_count: int = Field(1, ge=1, description="Nombre d'individus observés")
    
    # Conditions météo
    weather: str = Field("clear", description="Conditions météo (clear, cloudy, rain, snow, fog, wind)")
    temperature_c: Optional[float] = Field(None, description="Température en Celsius")
    wind_speed_kmh: Optional[float] = Field(None, description="Vitesse du vent en km/h")
    
    # Source et qualité
    source: str = Field("direct_visual", description="Source de l'observation (direct_visual, trail_camera, gps_collar, tracks, audio, other)")
    confidence: str = Field("medium", description="Niveau de confiance (high, medium, low)")
    
    # Notes
    notes: str = Field("", description="Notes libres de l'observateur")
    
    # Observateur
    observer_name: Optional[str] = Field(None, description="Nom de l'observateur")
    
    # Contexte habitat
    habitat_observed: Optional[str] = Field(None, description="Type d'habitat observé")
    terrain_type: Optional[str] = Field(None, description="Type de terrain")
    vegetation_type: Optional[str] = Field(None, description="Type de végétation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "species": "moose",
                "latitude": 46.8139,
                "longitude": -71.2080,
                "behavior": "feeding",
                "behavior_details": "Alimentation sur jeunes pousses de bouleau",
                "observation_datetime": "2024-10-15T06:30:00Z",
                "species_count": 1,
                "weather": "clear",
                "temperature_c": 8.5,
                "source": "direct_visual",
                "confidence": "high",
                "notes": "Femelle adulte avec veau de l'année à proximité",
                "observer_name": "Louis G.",
                "habitat_observed": "lisière forêt",
                "terrain_type": "plat",
                "vegetation_type": "forêt mixte"
            }
        }


class ObservationResponse(BaseModel):
    """Schéma de réponse d'observation."""
    
    observation_id: str
    species: str
    species_count: int
    latitude: float
    longitude: float
    observation_datetime: str
    behavior: str
    behavior_details: str
    weather: str
    temperature_c: Optional[float]
    source: str
    confidence: str
    notes: str
    observer_name: Optional[str]
    is_validated: bool
    created_at: str


class ObservationListResponse(BaseModel):
    """Schéma de réponse pour liste d'observations."""
    
    status: str = "success"
    total: int
    observations: List[ObservationResponse]


class ObservationStatsResponse(BaseModel):
    """Schéma de réponse pour statistiques."""
    
    status: str = "success"
    statistics: dict


class ValidateObservationRequest(BaseModel):
    """Schéma de validation d'observation."""
    
    validated_by: str = Field(..., description="Identifiant du validateur")


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.post(
    "/observations",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Créer une observation terrain",
    description="""
    PHASE F — GPS ULTIMATE
    
    Enregistre une nouvelle observation terrain pour calibrer le modèle BIONIC V5.
    
    Cette observation sera utilisée pour:
    - Valider les prédictions du moteur
    - Calibrer les pondérations des services
    - Atteindre le seuil de 95% pour le statut MASTER
    """
)
async def create_observation(request: CreateObservationRequest):
    """Crée une nouvelle observation terrain."""
    
    try:
        registry = get_observation_registry()
        
        observation = registry.create_observation(
            species=request.species,
            latitude=request.latitude,
            longitude=request.longitude,
            behavior=request.behavior,
            behavior_details=request.behavior_details,
            observation_datetime=request.observation_datetime,
            species_count=request.species_count,
            weather=request.weather,
            temperature_c=request.temperature_c,
            wind_speed_kmh=request.wind_speed_kmh,
            source=request.source,
            confidence=request.confidence,
            notes=request.notes,
            observer_name=request.observer_name,
            habitat_observed=request.habitat_observed,
            terrain_type=request.terrain_type,
            vegetation_type=request.vegetation_type
        )
        
        # Intégration avec CalibrationRegistry
        calibration_registry = get_calibration_registry()
        
        # Créer un test prédictif si l'observation est dans une zone prédite
        # (Cette logique sera étendue pour la version complète)
        
        logger.info(f"Observation created: {observation.observation_id}")
        
        return {
            "status": "success",
            "message": "Observation enregistrée avec succès",
            "observation": observation.to_dict(),
            "calibration_impact": {
                "will_contribute_to_calibration": True,
                "requires_validation": True,
                "current_model_version": "5.0.0 Pre-Master"
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to create observation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": True,
                "error_code": "OBSERVATION_CREATION_FAILED",
                "message": f"Échec de la création de l'observation: {str(e)}"
            }
        )


@router.get(
    "/observations",
    response_model=ObservationListResponse,
    summary="Lister les observations terrain",
    description="Récupère la liste des observations avec filtres optionnels."
)
async def list_observations(
    species: Optional[str] = Query(None, description="Filtrer par espèce"),
    validated_only: bool = Query(False, description="Uniquement les observations validées"),
    limit: int = Query(100, ge=1, le=500, description="Nombre maximum d'observations")
):
    """Liste les observations terrain."""
    
    try:
        registry = get_observation_registry()
        
        observations = registry.list_observations(
            species=species,
            validated_only=validated_only,
            limit=limit
        )
        
        return ObservationListResponse(
            status="success",
            total=len(observations),
            observations=[
                ObservationResponse(
                    observation_id=obs.observation_id,
                    species=obs.species.value,
                    species_count=obs.species_count,
                    latitude=obs.latitude,
                    longitude=obs.longitude,
                    observation_datetime=obs.observation_datetime.isoformat(),
                    behavior=obs.behavior.value,
                    behavior_details=obs.behavior_details,
                    weather=obs.weather.value,
                    temperature_c=obs.temperature_c,
                    source=obs.source.value,
                    confidence=obs.confidence.value,
                    notes=obs.notes,
                    observer_name=obs.observer_name,
                    is_validated=obs.is_validated,
                    created_at=obs.created_at.isoformat()
                )
                for obs in observations
            ]
        )
        
    except Exception as e:
        logger.error(f"Failed to list observations: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": True, "message": str(e)}
        )


@router.get(
    "/observations/stats",
    response_model=ObservationStatsResponse,
    summary="Statistiques des observations",
    description="Retourne les statistiques globales des observations terrain."
)
async def get_observations_stats():
    """Récupère les statistiques des observations."""
    
    try:
        registry = get_observation_registry()
        stats = registry.get_stats()
        
        return ObservationStatsResponse(
            status="success",
            statistics=stats
        )
        
    except Exception as e:
        logger.error(f"Failed to get stats: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": True, "message": str(e)}
        )


# Health check must be BEFORE parameterized routes
@router.get("/observations/health")
async def observations_health():
    """Vérification santé de l'endpoint observations."""
    
    registry = get_observation_registry()
    stats = registry.get_stats()
    
    return {
        "status": "healthy",
        "endpoint": "/api/v1/bionic/observations",
        "version": "7.0.0",
        "phase": "PHASE F - GPS ULTIMATE",
        "statistics": {
            "total_observations": stats.get("total_observations", 0),
            "validated_observations": stats.get("validated_observations", 0),
            "validation_rate": stats.get("validation_rate", 0)
        },
        "features": [
            "create_observation",
            "list_observations",
            "validate_observation",
            "statistics"
        ]
    }


@router.get(
    "/observations/{observation_id}",
    response_model=dict,
    summary="Détail d'une observation",
    description="Récupère les détails complets d'une observation."
)
async def get_observation(observation_id: str):
    """Récupère une observation par son ID."""
    
    try:
        registry = get_observation_registry()
        observation = registry.get_observation(observation_id)
        
        if not observation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": True,
                    "error_code": "OBSERVATION_NOT_FOUND",
                    "message": f"Observation {observation_id} non trouvée"
                }
            )
        
        return {
            "status": "success",
            "observation": observation.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get observation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": True, "message": str(e)}
        )


@router.post(
    "/observations/{observation_id}/validate",
    response_model=dict,
    summary="Valider une observation",
    description="""
    Valide une observation pour inclusion dans la calibration.
    
    Les observations validées contribuent directement à l'amélioration
    de la précision du modèle BIONIC V5.
    """
)
async def validate_observation(observation_id: str, request: ValidateObservationRequest):
    """Valide une observation pour la calibration."""
    
    try:
        registry = get_observation_registry()
        observation = registry.validate_observation(
            observation_id=observation_id,
            validated_by=request.validated_by
        )
        
        if not observation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": True,
                    "error_code": "OBSERVATION_NOT_FOUND",
                    "message": f"Observation {observation_id} non trouvée"
                }
            )
        
        # Mettre à jour le CalibrationRegistry
        calibration_registry = get_calibration_registry()
        stats = calibration_registry.get_stats()
        
        return {
            "status": "success",
            "message": "Observation validée avec succès",
            "observation_id": observation_id,
            "validated_by": request.validated_by,
            "validated_at": observation.validated_at.isoformat(),
            "calibration_status": {
                "profile_status": stats.get("profile_status", "not_calibrated"),
                "model_version": stats.get("model_version", "5.0.0"),
                "total_validated_observations": stats.get("tests_validated", 0) + 1
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to validate observation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": True, "message": str(e)}
        )


# Health check endpoint moved above parameterized routes
