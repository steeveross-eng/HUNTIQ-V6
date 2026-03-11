"""
BIONIC V5 — CALIBRATION ROUTER (PHASE F → MASTER)
===================================================
Calibration vers BIONIC V5 MASTER

Endpoints REST pour le système de calibration:
- Comparaison prédiction vs observation
- Dashboard de calibration  
- Génération et validation de suggestions
- Suivi de la progression vers MASTER

VERSION: 7.1.0
Conformité: G-SEC | G-QA | G-DOC | BIONIC V5 MASTER
"""

import logging
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from fastapi import UploadFile, File

from fastapi import APIRouter, HTTPException, status, Query

# Imports du Knowledge Layer
from modules.bionic_engine_p0.knowledge.calibration.calibration_optimizer import (
    get_calibration_optimizer,
    AdjustmentStatus
)
from modules.bionic_engine_p0.knowledge.calibration import get_calibration_registry
from modules.bionic_engine_p0.services.calibration_service import get_calibration_service
from database import Database

logger = logging.getLogger(__name__)

# =============================================================================
# ROUTER
# =============================================================================

router = APIRouter(tags=["BIONIC Calibration MASTER"])


# =============================================================================
# SCHEMAS
# =============================================================================

class CompareRequest(BaseModel):
    """Requête de comparaison prédiction vs observation."""
    
    observation_id: str = Field(..., description="ID de l'observation terrain")
    
    # Prédiction BIONIC
    predicted_lat: float = Field(..., ge=-90, le=90, description="Latitude prédite")
    predicted_lng: float = Field(..., ge=-180, le=180, description="Longitude prédite")
    predicted_behavior: str = Field(..., description="Comportement prédit")
    predicted_score: float = Field(..., ge=0, le=100, description="Score prédit")
    prediction_timestamp: datetime = Field(..., description="Horodatage de la prédiction")
    
    # Observation terrain
    observed_lat: float = Field(..., ge=-90, le=90, description="Latitude observée")
    observed_lng: float = Field(..., ge=-180, le=180, description="Longitude observée")
    observed_behavior: str = Field(..., description="Comportement observé")
    observed_timestamp: datetime = Field(..., description="Horodatage de l'observation")
    
    # Contexte
    species: str = Field("moose", description="Espèce")
    season: str = Field("", description="Saison")
    
    class Config:
        json_schema_extra = {
            "example": {
                "observation_id": "OBS-20260224-0001",
                "predicted_lat": 46.8139,
                "predicted_lng": -71.2080,
                "predicted_behavior": "feeding",
                "predicted_score": 72.5,
                "prediction_timestamp": "2026-02-24T06:00:00Z",
                "observed_lat": 46.8145,
                "observed_lng": -71.2075,
                "observed_behavior": "feeding",
                "observed_timestamp": "2026-02-24T06:30:00Z",
                "species": "moose",
                "season": "winter"
            }
        }


class ApproveSuggestionRequest(BaseModel):
    """Requête d'approbation de suggestion."""
    
    validated_by: str = Field(..., description="Identifiant du validateur")
    notes: str = Field("", description="Notes de validation")


class RejectSuggestionRequest(BaseModel):
    """Requête de rejet de suggestion."""
    
    validated_by: str = Field(..., description="Identifiant du validateur")
    reason: str = Field("", description="Raison du rejet")


class ObservationCreate(BaseModel):
    """Schéma de création d'une observation terrain."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude du point d'observation")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude du point d'observation")
    species: str = Field(..., min_length=1, description="Espèce observée")
    observed_behavior: str = Field(..., min_length=1, description="Comportement observé")
    observation_datetime: str = Field(..., description="Date et heure de l'observation (ISO 8601)")
    region: str = Field(default="CA-QC", description="Région administrative")
    notes: str = Field(default="", description="Notes de terrain")
    weather_conditions: Optional[dict] = Field(default=None, description="Conditions météo")
    observer_id: str = Field(default="terrain_user", description="Identifiant de l'observateur")
    confidence: float = Field(default=0.8, ge=0, le=1, description="Niveau de confiance (0-1)")
    source_ids: Optional[List[str]] = Field(default=None, description="IDs de sources")

    class Config:
        json_schema_extra = {
            "example": {
                "latitude": 46.8139,
                "longitude": -71.2080,
                "species": "orignal",
                "observed_behavior": "alimentation",
                "observation_datetime": "2026-02-24T08:30:00Z",
                "region": "CA-QC",
                "notes": "Orignal mâle adulte, broutant dans une coupe forestière",
                "confidence": 0.9
            }
        }


# =============================================================================
# ENDPOINTS - OBSERVATIONS TERRAIN (MongoDB CRUD)
# =============================================================================

@router.post(
    "/calibration/observations",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Créer une observation terrain",
    description="""
    CALIBRATION VERS MASTER — Collecte terrain
    
    Enregistre une nouvelle observation terrain dans MongoDB.
    Chaque observation est versionnée avec source_ids et traçabilité.
    """
)
async def create_observation(data: ObservationCreate):
    """Crée une observation terrain."""
    try:
        db = Database.get_database()
        service = get_calibration_service()
        result = await service.create_observation(db, data.model_dump())
        return {
            "status": "created",
            "observation": result,
            "source_ids": ["SRC-CALIBRATION-API"],
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Create observation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/calibration/observations",
    response_model=dict,
    summary="Lister les observations terrain",
    description="Liste les observations avec filtres optionnels (espèce, statut)."
)
async def list_observations(
    species: Optional[str] = Query(None, description="Filtrer par espèce"),
    obs_status: Optional[str] = Query(None, alias="status", description="Filtrer par statut (pending, compared)"),
    limit: int = Query(50, ge=1, le=200, description="Nombre maximum"),
    skip: int = Query(0, ge=0, description="Offset")
):
    """Liste les observations terrain."""
    try:
        db = Database.get_database()
        service = get_calibration_service()
        result = await service.list_observations(db, species=species, status=obs_status, limit=limit, skip=skip)
        return result
    except Exception as e:
        logger.error(f"List observations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/calibration/observations/{observation_id}",
    response_model=dict,
    summary="Détail d'une observation",
    description="Récupère les détails d'une observation terrain spécifique."
)
async def get_observation(observation_id: str):
    """Récupère une observation par ID."""
    try:
        db = Database.get_database()
        service = get_calibration_service()
        obs = await service.get_observation(db, observation_id)
        if not obs:
            raise HTTPException(status_code=404, detail="Observation non trouvée")
        return obs
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get observation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/calibration/observations/{observation_id}",
    response_model=dict,
    summary="Supprimer une observation",
    description="Supprime une observation terrain."
)
async def delete_observation(observation_id: str):
    """Supprime une observation."""
    try:
        db = Database.get_database()
        service = get_calibration_service()
        deleted = await service.delete_observation(db, observation_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Observation non trouvée")
        return {"status": "deleted", "observation_id": observation_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete observation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/calibration/observations/import",
    response_model=dict,
    summary="Import CSV/Excel d'observations terrain",
    description="""
    CALIBRATION VERS MASTER — Import en lot
    
    Accepte un fichier CSV ou Excel (.xlsx) contenant des observations terrain.
    
    **Colonnes requises:** latitude, longitude, species, observed_behavior, observation_datetime
    **Colonnes optionnelles:** region, notes, confidence, observer_id
    
    Limites: 10 MB max, 5000 lignes max.
    """
)
async def import_observations_file(file: UploadFile = File(...)):
    """Import en lot d'observations terrain depuis CSV/Excel."""
    try:
        from modules.bionic_engine_p0.services.import_service import import_observations_from_file

        if not file.filename:
            raise HTTPException(status_code=400, detail="Nom de fichier manquant")

        ext = file.filename.lower().rsplit(".", 1)[-1] if "." in file.filename else ""
        if ext not in ("csv", "xlsx", "xls"):
            raise HTTPException(
                status_code=400,
                detail=f"Format non supporté: .{ext}. Acceptés: .csv, .xlsx"
            )

        content = await file.read()
        db = Database.get_database()

        result = await import_observations_from_file(
            db=db,
            content=content,
            filename=file.filename,
            source_label="api_upload"
        )

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Import file error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/calibration/import/template",
    response_model=dict,
    summary="Template d'import CSV",
    description="Retourne le modèle CSV avec les colonnes requises."
)
async def get_import_template():
    """Retourne le template CSV pour l'import."""
    return {
        "required_columns": ["latitude", "longitude", "species", "observed_behavior", "observation_datetime"],
        "optional_columns": ["region", "notes", "confidence", "observer_id"],
        "accepted_formats": [".csv", ".xlsx"],
        "csv_example": "latitude,longitude,species,observed_behavior,observation_datetime,region,notes,confidence\n46.8139,-71.2080,orignal,alimentation,2026-02-24T08:30:00Z,CA-QC,Mâle adulte coupe forestière,0.9\n47.1000,-70.5000,cerf_de_virginie,repos,2026-02-24T14:00:00Z,CA-QC,Femelle bordure cédrière,0.85",
        "valid_species": ["orignal", "cerf_de_virginie", "ours_noir", "caribou", "wapiti"],
        "valid_behaviors": ["alimentation", "déplacement", "repos", "rut", "allaitement", "fuite", "abreuvement", "ravage"],
        "limits": {
            "max_file_size_mb": 10,
            "max_rows": 5000
        },
        "source_ids": ["SRC-IMPORT-TEMPLATE"],
        "version": "1.0.0"
    }


@router.get(
    "/calibration/observations-metrics",
    response_model=dict,
    summary="Métriques des observations",
    description="Dashboard avancé de calibration avec métriques MongoDB."
)
async def get_observations_metrics():
    """Métriques basées sur les observations MongoDB."""
    try:
        db = Database.get_database()
        service = get_calibration_service()
        metrics = await service.get_metrics(db)
        return metrics
    except Exception as e:
        logger.error(f"Metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/calibration/calibration-status",
    response_model=dict,
    summary="Statut de calibration terrain",
    description="Statut de calibration basé sur les observations terrain."
)
async def get_terrain_calibration_status():
    """Statut de calibration basé sur les données terrain."""
    try:
        db = Database.get_database()
        service = get_calibration_service()
        cal_status = await service.get_calibration_status(db)
        return cal_status
    except Exception as e:
        logger.error(f"Status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/calibration/compare",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Comparer prédiction vs observation",
    description="""
    CALIBRATION VERS MASTER
    
    Compare une prédiction BIONIC avec une observation terrain.
    
    Calcule:
    - Erreur spatiale (distance en mètres)
    - Erreur temporelle (écart en minutes)
    - Concordance comportementale
    - Score de concordance global
    
    Chaque comparaison contribue à la calibration vers BIONIC V5 MASTER.
    """
)
async def compare_prediction_vs_observation(request: CompareRequest):
    """Compare une prédiction avec une observation."""
    
    try:
        optimizer = get_calibration_optimizer()
        
        result = optimizer.compare_prediction_vs_observation(
            observation_id=request.observation_id,
            predicted_lat=request.predicted_lat,
            predicted_lng=request.predicted_lng,
            predicted_behavior=request.predicted_behavior,
            predicted_score=request.predicted_score,
            prediction_timestamp=request.prediction_timestamp,
            observed_lat=request.observed_lat,
            observed_lng=request.observed_lng,
            observed_behavior=request.observed_behavior,
            observed_timestamp=request.observed_timestamp,
            species=request.species,
            season=request.season
        )
        
        # Récupérer les stats de précision mises à jour
        dashboard = optimizer.get_dashboard_data()
        
        return {
            "status": "success",
            "message": "Comparaison enregistrée avec succès",
            "comparison": result.to_dict(),
            "current_precision": {
                "global": round(dashboard.global_precision, 1),
                "target": dashboard.target_precision,
                "gap": round(dashboard.precision_gap, 1),
                "is_master_ready": dashboard.is_master_ready
            },
            "metadata": {
                "version": "7.1.0",
                "total_comparisons": dashboard.total_comparisons
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to compare: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": True, "message": str(e)}
        )


@router.get(
    "/calibration/comparisons",
    response_model=dict,
    summary="Lister les comparaisons",
    description="Récupère l'historique des comparaisons prédiction vs observation."
)
async def list_comparisons(
    limit: int = Query(50, ge=1, le=500, description="Nombre maximum")
):
    """Liste les comparaisons."""
    
    try:
        optimizer = get_calibration_optimizer()
        comparisons = optimizer.list_comparisons(limit=limit)
        
        return {
            "status": "success",
            "total": len(comparisons),
            "comparisons": [c.to_dict() for c in comparisons]
        }
        
    except Exception as e:
        logger.error(f"Failed to list comparisons: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": True, "message": str(e)}
        )


# =============================================================================
# ENDPOINTS - DASHBOARD
# =============================================================================

@router.get(
    "/calibration/dashboard",
    response_model=dict,
    summary="Dashboard de calibration",
    description="""
    CALIBRATION VERS MASTER
    
    Retourne les données complètes du dashboard de calibration:
    - Précision globale actuelle vs objectif (95%)
    - Précision par catégorie (spatial, temporal, behavioral)
    - Précision par espèce
    - Précision par comportement
    - Tendance historique
    - Suggestions en attente
    - Statut MASTER
    """
)
async def get_calibration_dashboard():
    """Récupère les données du dashboard."""
    
    try:
        optimizer = get_calibration_optimizer()
        registry = get_calibration_registry()
        
        dashboard = optimizer.get_dashboard_data()
        profile = registry.get_current_profile()
        model_version = registry.get_model_version()
        
        dashboard_data = dashboard.to_dict()
        
        # Ajouter les infos du profil et de la version
        dashboard_data["calibration_profile"] = profile.to_dict()
        dashboard_data["model_version"] = model_version.to_dict()
        
        return {
            "status": "success",
            "dashboard": dashboard_data
        }
        
    except Exception as e:
        logger.error(f"Failed to get dashboard: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": True, "message": str(e)}
        )


# =============================================================================
# ENDPOINTS - SUGGESTIONS
# =============================================================================

@router.post(
    "/calibration/suggestions/generate",
    response_model=dict,
    summary="Générer des suggestions d'ajustement",
    description="""
    CALIBRATION VERS MASTER — MODE HYBRIDE
    
    Analyse les comparaisons et génère des suggestions automatiques
    d'ajustement des pondérations et modificateurs.
    
    Les suggestions nécessitent une VALIDATION MANUELLE OBLIGATOIRE
    avant d'être appliquées au modèle.
    """
)
async def generate_suggestions():
    """Génère des suggestions d'ajustement."""
    
    try:
        optimizer = get_calibration_optimizer()
        registry = get_calibration_registry()
        
        profile = registry.get_current_profile()
        
        suggestions = optimizer.generate_suggestions(
            current_service_weights=profile.service_weights,
            current_level_modifiers=profile.level_modifiers,
            current_thresholds=profile.thresholds
        )
        
        return {
            "status": "success",
            "message": f"{len(suggestions)} suggestion(s) générée(s)",
            "suggestions": [s.to_dict() for s in suggestions],
            "requires_validation": True,
            "metadata": {
                "version": "7.1.0",
                "mode": "hybrid"
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to generate suggestions: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": True, "message": str(e)}
        )


@router.get(
    "/calibration/suggestions",
    response_model=dict,
    summary="Lister les suggestions",
    description="Récupère la liste des suggestions d'ajustement."
)
async def list_suggestions(
    status_filter: Optional[str] = Query(None, description="Filtrer par statut (pending, approved, applied, rejected)")
):
    """Liste les suggestions."""
    
    try:
        optimizer = get_calibration_optimizer()
        
        filter_status = None
        if status_filter:
            try:
                filter_status = AdjustmentStatus(status_filter)
            except ValueError:
                pass
        
        suggestions = optimizer.list_suggestions(status=filter_status)
        
        return {
            "status": "success",
            "total": len(suggestions),
            "suggestions": [s.to_dict() for s in suggestions],
            "filter": status_filter
        }
        
    except Exception as e:
        logger.error(f"Failed to list suggestions: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": True, "message": str(e)}
        )


@router.post(
    "/calibration/suggestions/{suggestion_id}/approve",
    response_model=dict,
    summary="Approuver une suggestion",
    description="""
    VALIDATION MANUELLE OBLIGATOIRE
    
    Approuve une suggestion d'ajustement.
    La suggestion sera marquée comme approuvée et prête à être appliquée.
    """
)
async def approve_suggestion(suggestion_id: str, request: ApproveSuggestionRequest):
    """Approuve une suggestion."""
    
    try:
        optimizer = get_calibration_optimizer()
        
        suggestion = optimizer.approve_suggestion(
            suggestion_id=suggestion_id,
            validated_by=request.validated_by,
            notes=request.notes
        )
        
        if not suggestion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": True,
                    "error_code": "SUGGESTION_NOT_FOUND",
                    "message": f"Suggestion {suggestion_id} non trouvée ou déjà traitée"
                }
            )
        
        return {
            "status": "success",
            "message": "Suggestion approuvée",
            "suggestion": suggestion.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to approve suggestion: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": True, "message": str(e)}
        )


@router.post(
    "/calibration/suggestions/{suggestion_id}/reject",
    response_model=dict,
    summary="Rejeter une suggestion",
    description="Rejette une suggestion d'ajustement."
)
async def reject_suggestion(suggestion_id: str, request: RejectSuggestionRequest):
    """Rejette une suggestion."""
    
    try:
        optimizer = get_calibration_optimizer()
        
        suggestion = optimizer.reject_suggestion(
            suggestion_id=suggestion_id,
            validated_by=request.validated_by,
            reason=request.reason
        )
        
        if not suggestion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": True,
                    "error_code": "SUGGESTION_NOT_FOUND",
                    "message": f"Suggestion {suggestion_id} non trouvée ou déjà traitée"
                }
            )
        
        return {
            "status": "success",
            "message": "Suggestion rejetée",
            "suggestion": suggestion.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reject suggestion: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": True, "message": str(e)}
        )


@router.post(
    "/calibration/suggestions/apply",
    response_model=dict,
    summary="Appliquer les suggestions approuvées",
    description="""
    CALIBRATION VERS MASTER
    
    Applique toutes les suggestions approuvées au CalibrationProfile.
    Les ajustements seront effectifs immédiatement.
    """
)
async def apply_approved_suggestions():
    """Applique les suggestions approuvées."""
    
    try:
        optimizer = get_calibration_optimizer()
        registry = get_calibration_registry()
        
        result = optimizer.apply_approved_suggestions()
        
        if result["applied"] == 0:
            return {
                "status": "success",
                "message": "Aucune suggestion approuvée à appliquer",
                "applied": 0
            }
        
        # Mettre à jour le profil de calibration
        profile = registry.get_current_profile()
        
        # Appliquer les ajustements
        adjustments = result["adjustments"]
        
        for key, value in adjustments.get("service_weights", {}).items():
            if key in profile.service_weights:
                profile.service_weights[key] = value
        
        for key, value in adjustments.get("level_modifiers", {}).items():
            if key in profile.level_modifiers:
                profile.level_modifiers[key] = value
        
        for key, value in adjustments.get("thresholds", {}).items():
            if key in profile.thresholds:
                profile.thresholds[key] = value
        
        return {
            "status": "success",
            "message": f"{result['applied']} suggestion(s) appliquée(s)",
            "applied": result["applied"],
            "suggestions_applied": result["suggestions_applied"],
            "updated_profile": profile.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Failed to apply suggestions: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": True, "message": str(e)}
        )


# =============================================================================
# ENDPOINTS - MASTER STATUS
# =============================================================================

@router.get(
    "/calibration/master-status",
    response_model=dict,
    summary="Statut MASTER",
    description="""
    Vérifie si le modèle est prêt pour le statut BIONIC V5 MASTER.
    
    Critère: Précision globale ≥ 95%
    """
)
async def get_master_status():
    """Vérifie le statut MASTER."""
    
    try:
        optimizer = get_calibration_optimizer()
        registry = get_calibration_registry()
        
        dashboard = optimizer.get_dashboard_data()
        model_version = registry.get_model_version()
        
        is_ready = dashboard.global_precision >= 95.0
        
        return {
            "status": "success",
            "master_status": {
                "is_ready": is_ready,
                "is_locked": model_version.is_locked,
                "is_master": model_version.is_master,
                "current_precision": round(dashboard.global_precision, 1),
                "target_precision": 95.0,
                "gap": round(dashboard.precision_gap, 1),
                "total_comparisons": dashboard.total_comparisons,
                "estimated_comparisons_needed": dashboard.estimated_comparisons_to_master
            },
            "model_version": model_version.to_dict(),
            "recommendation": (
                "Le modèle est prêt pour le verrouillage MASTER !" if is_ready
                else f"Il reste environ {dashboard.estimated_comparisons_to_master} comparaisons pour atteindre 95%"
            )
        }
        
    except Exception as e:
        logger.error(f"Failed to get master status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": True, "message": str(e)}
        )


@router.post(
    "/calibration/lock-master",
    response_model=dict,
    summary="Verrouiller comme MASTER",
    description="""
    ATTENTION: Action irréversible
    
    Verrouille le modèle actuel comme BIONIC V5 MASTER si la précision ≥ 95%.
    Une fois verrouillé, le modèle ne peut plus être modifié.
    """
)
async def lock_as_master():
    """Verrouille le modèle comme MASTER."""
    
    try:
        optimizer = get_calibration_optimizer()
        registry = get_calibration_registry()
        
        dashboard = optimizer.get_dashboard_data()
        model_version = registry.get_model_version()
        
        if model_version.is_locked:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": True,
                    "error_code": "ALREADY_LOCKED",
                    "message": "Le modèle est déjà verrouillé"
                }
            )
        
        if dashboard.global_precision < 95.0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": True,
                    "error_code": "PRECISION_INSUFFICIENT",
                    "message": f"Précision insuffisante ({dashboard.global_precision:.1f}%). Objectif: 95%",
                    "current_precision": dashboard.global_precision,
                    "gap": dashboard.precision_gap
                }
            )
        
        # Verrouiller
        success = model_version.lock_as_master(dashboard.global_precision)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": True,
                    "message": "Échec du verrouillage"
                }
            )
        
        return {
            "status": "success",
            "message": "BIONIC V5 MASTER verrouillé avec succès !",
            "model_version": model_version.to_dict(),
            "final_precision": round(dashboard.global_precision, 1)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to lock as master: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": True, "message": str(e)}
        )


# =============================================================================
# HEALTH CHECK
# =============================================================================

@router.get("/calibration/health")
async def calibration_health():
    """Vérification santé du service de calibration."""
    
    try:
        optimizer = get_calibration_optimizer()
        registry = get_calibration_registry()
        
        optimizer_stats = optimizer.get_stats()
        registry_stats = registry.get_stats()
        
        return {
            "status": "healthy",
            "endpoint": "/api/v1/bionic/calibration",
            "version": "7.1.0",
            "phase": "CALIBRATION VERS MASTER",
            "optimizer": optimizer_stats,
            "registry": registry_stats,
            "features": [
                "compare_prediction_vs_observation",
                "calibration_dashboard",
                "suggestion_generation",
                "manual_validation",
                "master_locking"
            ]
        }
        
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e)
        }
