"""
BIONIC Knowledge Router - V5-ULTIME
===================================

Routes API pour le Knowledge Layer.
Prefix: /api/v1/bionic/knowledge

Endpoints:
- /dashboard : Statistiques globales
- /species/* : Gestion des espèces
- /rules/* : Gestion des règles
- /sources/* : Gestion des sources
- /seasonal/* : Modèles saisonniers
- /variables/* : Variables d'habitat
- /query : Requête intelligente
- /validation/* : Pipeline de validation

Module isolé - Architecture LEGO V5.
"""

from fastapi import APIRouter, Query, Body
from typing import Optional
from datetime import date
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient

from .knowledge_service import KnowledgeService
from .knowledge_sources import KnowledgeSourcesManager
from .knowledge_rules import KnowledgeRulesManager
from .knowledge_seasonal_models import SeasonalModelsManager
from .knowledge_validation_pipeline import ValidationPipeline

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/bionic/knowledge", tags=["BIONIC Knowledge Layer"])

# Database
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'bionic_db')
_client = None
_db = None

def get_db():
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(MONGO_URL)
        _db = _client[DB_NAME]
    return _db


# ==============================================
# MODULE INFO
# ==============================================

@router.get("/")
async def knowledge_engine_info():
    """Information sur le Knowledge Engine"""
    return {
        "module": "bionic_knowledge_engine",
        "version": "1.0.0",
        "description": "BIONIC Knowledge Layer V5-ULTIME",
        "architecture": "LEGO_V5_ISOLATED",
        "components": [
            "knowledge_service",
            "knowledge_sources",
            "knowledge_rules",
            "knowledge_seasonal_models",
            "knowledge_validation_pipeline"
        ],
        "endpoints": {
            "dashboard": "/dashboard",
            "species": "/species/*",
            "rules": "/rules/*",
            "sources": "/sources/*",
            "seasonal": "/seasonal/*",
            "variables": "/variables/*",
            "query": "/query",
            "validation": "/validation/*"
        }
    }


# ==============================================
# DASHBOARD
# ==============================================

@router.get("/dashboard")
async def get_knowledge_dashboard():
    """Dashboard du Knowledge Layer"""
    return await KnowledgeService.get_dashboard_stats(get_db())


# ==============================================
# SPECIES
# ==============================================

@router.get("/species")
async def get_all_species(category: Optional[str] = None):
    """Liste des espèces"""
    return await KnowledgeService.get_all_species(get_db(), category)

@router.get("/species/{species_id}")
async def get_species(species_id: str):
    """Détail d'une espèce"""
    return await KnowledgeService.get_species_by_id(get_db(), species_id)

@router.post("/species")
async def add_species(species_data: dict = Body(...)):
    """Ajouter une espèce"""
    return await KnowledgeService.add_species(get_db(), species_data)


# ==============================================
# RULES
# ==============================================

@router.get("/rules")
async def get_all_rules(
    species: Optional[str] = None,
    season: Optional[str] = None,
    confidence: Optional[str] = None,
    is_active: bool = True,
    limit: int = Query(100, le=500)
):
    """Liste des règles comportementales"""
    return await KnowledgeRulesManager.get_all_rules(get_db(), species, season, confidence, is_active, limit)

@router.get("/rules/stats")
async def get_rules_stats():
    """Statistiques des règles"""
    return await KnowledgeRulesManager.get_rules_stats(get_db())

@router.get("/rules/{rule_id}")
async def get_rule(rule_id: str):
    """Détail d'une règle"""
    return await KnowledgeRulesManager.get_rule_by_id(get_db(), rule_id)

@router.post("/rules")
async def add_rule(rule_data: dict = Body(...)):
    """Ajouter une règle"""
    return await KnowledgeRulesManager.add_rule(get_db(), rule_data)

@router.put("/rules/{rule_id}")
async def update_rule(rule_id: str, updates: dict = Body(...)):
    """Mettre à jour une règle"""
    return await KnowledgeRulesManager.update_rule(get_db(), rule_id, updates)

@router.put("/rules/{rule_id}/toggle")
async def toggle_rule(rule_id: str, is_active: bool):
    """Activer/désactiver une règle"""
    return await KnowledgeRulesManager.toggle_rule(get_db(), rule_id, is_active)

@router.post("/rules/{rule_id}/validate")
async def validate_rule_observation(rule_id: str, result: bool):
    """Enregistrer une validation terrain"""
    return await KnowledgeRulesManager.validate_rule(get_db(), rule_id, result)

@router.post("/rules/apply")
async def apply_rules(
    species: str,
    season: str,
    conditions: dict = Body(...)
):
    """Appliquer les règles à des conditions données"""
    return KnowledgeRulesManager.apply_rules(conditions, species, season)


# ==============================================
# SOURCES
# ==============================================

@router.get("/sources")
async def get_all_sources(
    source_type: Optional[str] = None,
    verified: Optional[bool] = None,
    limit: int = Query(100, le=500)
):
    """Liste des sources"""
    return await KnowledgeSourcesManager.get_all_sources(get_db(), source_type, verified, limit)

@router.get("/sources/stats")
async def get_sources_stats():
    """Statistiques des sources"""
    return await KnowledgeSourcesManager.get_sources_stats(get_db())

@router.get("/sources/{source_id}")
async def get_source(source_id: str):
    """Détail d'une source"""
    return await KnowledgeSourcesManager.get_source_by_id(get_db(), source_id)

@router.post("/sources")
async def add_source(source_data: dict = Body(...)):
    """Ajouter une source"""
    return await KnowledgeSourcesManager.add_source(get_db(), source_data)

@router.put("/sources/{source_id}")
async def update_source(source_id: str, updates: dict = Body(...)):
    """Mettre à jour une source"""
    return await KnowledgeSourcesManager.update_source(get_db(), source_id, updates)

@router.put("/sources/{source_id}/verify")
async def verify_source(source_id: str, verified: bool = True):
    """Vérifier une source"""
    return await KnowledgeSourcesManager.verify_source(get_db(), source_id, verified)

@router.delete("/sources/{source_id}")
async def delete_source(source_id: str):
    """Supprimer une source"""
    return await KnowledgeSourcesManager.delete_source(get_db(), source_id)


# ==============================================
# SEASONAL MODELS
# ==============================================

@router.get("/seasonal")
async def get_all_seasonal_models(
    species_id: Optional[str] = None,
    region: Optional[str] = None,
    limit: int = Query(50, le=200)
):
    """Liste des modèles saisonniers"""
    return await SeasonalModelsManager.get_all_models(get_db(), species_id, region, limit)

@router.get("/seasonal/stats")
async def get_seasonal_stats():
    """Statistiques des modèles saisonniers"""
    return await SeasonalModelsManager.get_models_stats(get_db())

@router.get("/seasonal/{model_id}")
async def get_seasonal_model(model_id: str):
    """Détail d'un modèle"""
    return await SeasonalModelsManager.get_model_by_id(get_db(), model_id)

@router.get("/seasonal/{model_id}/current-phase")
async def get_current_phase(model_id: str, target_date: Optional[str] = None):
    """Phase actuelle pour un modèle"""
    dt = date.fromisoformat(target_date) if target_date else None
    return SeasonalModelsManager.get_current_phase(model_id, dt)

@router.get("/seasonal/{model_id}/progress")
async def get_phase_progress(model_id: str, target_date: Optional[str] = None):
    """Progression dans la phase actuelle"""
    dt = date.fromisoformat(target_date) if target_date else None
    return SeasonalModelsManager.calculate_phase_progress(model_id, dt)

@router.get("/seasonal/{model_id}/predict")
async def predict_activity(
    model_id: str,
    target_date: Optional[str] = None,
    temperature: Optional[float] = None
):
    """Prédire le niveau d'activité"""
    dt = date.fromisoformat(target_date) if target_date else None
    conditions = {"temperature": temperature} if temperature else None
    return SeasonalModelsManager.predict_activity_level(model_id, dt, temperature, conditions)

@router.post("/seasonal")
async def add_seasonal_model(model_data: dict = Body(...)):
    """Ajouter un modèle saisonnier"""
    return await SeasonalModelsManager.add_model(get_db(), model_data)

@router.put("/seasonal/{model_id}")
async def update_seasonal_model(model_id: str, updates: dict = Body(...)):
    """Mettre à jour un modèle"""
    return await SeasonalModelsManager.update_model(get_db(), model_id, updates)


# ==============================================
# HABITAT VARIABLES
# ==============================================

@router.get("/variables")
async def get_habitat_variables():
    """Liste des variables d'habitat"""
    return await KnowledgeService.get_habitat_variables(get_db())


# ==============================================
# INTELLIGENT QUERY
# ==============================================

@router.post("/query")
async def query_knowledge(
    species_id: str,
    target_date: Optional[str] = None,
    location: Optional[dict] = Body(default=None),
    conditions: Optional[dict] = Body(default=None)
):
    """Requête intelligente du Knowledge Layer"""
    dt = date.fromisoformat(target_date) if target_date else None
    return await KnowledgeService.query_knowledge(get_db(), species_id, dt, location, conditions)


# ==============================================
# VALIDATION
# ==============================================

@router.get("/validation/report")
async def get_validation_report():
    """Rapport de validation global"""
    return await ValidationPipeline.validate_all(get_db())

@router.post("/validation/species")
async def validate_species_data(species_data: dict = Body(...)):
    """Valider des données d'espèce"""
    result = ValidationPipeline.validate_species(species_data)
    return ValidationPipeline.generate_validation_report(result, "species", species_data.get("id", "unknown"))

@router.post("/validation/rule")
async def validate_rule_data(rule_data: dict = Body(...)):
    """Valider des données de règle"""
    result = ValidationPipeline.validate_rule(rule_data)
    return ValidationPipeline.generate_validation_report(result, "rule", rule_data.get("id", "unknown"))

@router.post("/validation/source")
async def validate_source_data(source_data: dict = Body(...)):
    """Valider des données de source"""
    result = ValidationPipeline.validate_source(source_data)
    return ValidationPipeline.generate_validation_report(result, "source", source_data.get("id", "unknown"))

@router.post("/validation/seasonal")
async def validate_seasonal_data(model_data: dict = Body(...)):
    """Valider des données de modèle saisonnier"""
    result = ValidationPipeline.validate_seasonal_model(model_data)
    return ValidationPipeline.generate_validation_report(result, "seasonal_model", model_data.get("id", "unknown"))


logger.info("BIONIC Knowledge Router initialized - V5 LEGO Module")
