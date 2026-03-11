"""
BIONIC Knowledge Service - V5-ULTIME
====================================

Service principal du Knowledge Layer.
Orchestration de tous les composants:
- Sources
- Règles
- Modèles saisonniers
- Validation

Module isolé - aucun import croisé.
"""

from datetime import datetime, timezone, date
from typing import List
import logging
import uuid

from .knowledge_sources import KnowledgeSourcesManager
from .knowledge_rules import KnowledgeRulesManager
from .knowledge_seasonal_models import SeasonalModelsManager
from .knowledge_validation_pipeline import ValidationPipeline

logger = logging.getLogger(__name__)


class KnowledgeService:
    """Service principal du BIONIC Knowledge Layer"""
    
    # Espèces principales (Québec)
    SPECIES_REGISTRY = {
        "moose": {
            "id": "moose",
            "scientific_name": "Alces alces",
            "common_name_fr": "Orignal",
            "common_name_en": "Moose",
            "category": "cervidae",
            "hunting_season_fr": "Septembre-Octobre",
            "primary_regions": ["quebec_north", "quebec_south", "laurentides", "abitibi"]
        },
        "deer": {
            "id": "deer",
            "scientific_name": "Odocoileus virginianus",
            "common_name_fr": "Cerf de Virginie",
            "common_name_en": "White-tailed Deer",
            "category": "cervidae",
            "hunting_season_fr": "Novembre",
            "primary_regions": ["monteregie", "estrie", "outaouais", "lanaudiere"]
        },
        "bear": {
            "id": "bear",
            "scientific_name": "Ursus americanus",
            "common_name_fr": "Ours noir",
            "common_name_en": "Black Bear",
            "category": "ursidae",
            "hunting_season_fr": "Mai-Juin, Septembre",
            "primary_regions": ["quebec_all"]
        },
        "elk": {
            "id": "elk",
            "scientific_name": "Cervus canadensis",
            "common_name_fr": "Wapiti",
            "common_name_en": "Elk",
            "category": "cervidae",
            "hunting_season_fr": "Octobre",
            "primary_regions": ["la_verendrye", "quebec_south"]
        },
        "caribou": {
            "id": "caribou",
            "scientific_name": "Rangifer tarandus",
            "common_name_fr": "Caribou",
            "common_name_en": "Caribou",
            "category": "cervidae",
            "hunting_season_fr": "Août-Septembre",
            "primary_regions": ["ungava", "nouveau_quebec"]
        }
    }
    
    # ============ DASHBOARD ============
    
    @staticmethod
    async def get_dashboard_stats(db) -> dict:
        """Statistiques globales du Knowledge Layer"""
        try:
            # Stats sources
            sources_stats = await KnowledgeSourcesManager.get_sources_stats(db)
            
            # Stats règles
            rules_stats = await KnowledgeRulesManager.get_rules_stats(db)
            
            # Stats modèles saisonniers
            models_stats = await SeasonalModelsManager.get_models_stats(db)
            
            # Stats espèces
            custom_species = await db.knowledge_species.count_documents({})
            
            # Validation globale
            validation_result = await ValidationPipeline.validate_all(db)
            
            return {
                "success": True,
                "stats": {
                    "species": {
                        "base": len(KnowledgeService.SPECIES_REGISTRY),
                        "custom": custom_species,
                        "total": len(KnowledgeService.SPECIES_REGISTRY) + custom_species
                    },
                    "sources": sources_stats.get("stats", {}),
                    "rules": rules_stats.get("stats", {}),
                    "seasonal_models": models_stats.get("stats", {}),
                    "validation": {
                        "health_score": validation_result.get("overall_health", 0),
                        "critical_issues": len(validation_result.get("critical_issues", []))
                    }
                },
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {e}")
            return {"success": False, "error": str(e)}
    
    # ============ SPECIES ============
    
    @staticmethod
    async def get_all_species(db, category: str = None) -> dict:
        """Récupérer toutes les espèces"""
        try:
            species_list = list(KnowledgeService.SPECIES_REGISTRY.values())
            
            # Ajouter espèces custom
            query = {}
            if category:
                query["category"] = category
            custom = await db.knowledge_species.find(query, {"_id": 0}).to_list(50)
            species_list.extend(custom)
            
            if category:
                species_list = [s for s in species_list if s.get("category") == category]
            
            return {
                "success": True,
                "total": len(species_list),
                "species": species_list
            }
        except Exception as e:
            logger.error(f"Error getting species: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def get_species_by_id(db, species_id: str) -> dict:
        """Récupérer une espèce par ID"""
        try:
            if species_id in KnowledgeService.SPECIES_REGISTRY:
                return {
                    "success": True,
                    "species": KnowledgeService.SPECIES_REGISTRY[species_id],
                    "is_base": True
                }
            
            species = await db.knowledge_species.find_one({"id": species_id}, {"_id": 0})
            if species:
                return {"success": True, "species": species, "is_base": False}
            
            return {"success": False, "error": "Espèce non trouvée"}
        except Exception as e:
            logger.error(f"Error getting species: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def add_species(db, species_data: dict) -> dict:
        """Ajouter une nouvelle espèce"""
        try:
            # Valider d'abord
            validation = ValidationPipeline.validate_species(species_data)
            if not validation["is_valid"]:
                return {
                    "success": False,
                    "error": "Validation échouée",
                    "validation": validation
                }
            
            species = {
                "id": species_data.get("id", str(uuid.uuid4())),
                **species_data,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            await db.knowledge_species.insert_one(species)
            species.pop("_id", None)
            
            return {"success": True, "species": species}
        except Exception as e:
            logger.error(f"Error adding species: {e}")
            return {"success": False, "error": str(e)}
    
    # ============ QUERY ENGINE ============
    
    @staticmethod
    async def query_knowledge(db, species_id: str, 
                             target_date: date = None,
                             location: dict = None,
                             conditions: dict = None) -> dict:
        """Requête intelligente du Knowledge Layer"""
        try:
            if target_date is None:
                target_date = date.today()
            
            result = {
                "species_id": species_id,
                "query_date": target_date.isoformat(),
                "location": location,
                "conditions": conditions
            }
            
            # 1. Récupérer info espèce
            species_result = await KnowledgeService.get_species_by_id(db, species_id)
            if not species_result.get("success"):
                return {"success": False, "error": "Espèce non trouvée"}
            
            result["species"] = species_result["species"]
            
            # 2. Déterminer phase saisonnière
            model_id = f"{species_id}_quebec_south"
            phase_result = SeasonalModelsManager.calculate_phase_progress(model_id, target_date)
            if phase_result.get("success"):
                result["seasonal_phase"] = {
                    "name": phase_result["phase"]["name_fr"],
                    "progress": phase_result["progress"],
                    "peak_proximity": phase_result["peak_proximity"],
                    "base_activity": phase_result["activity_level"]
                }
            
            # 3. Appliquer règles comportementales
            season = phase_result.get("phase", {}).get("name", "fall") if phase_result.get("success") else "fall"
            rules_result = KnowledgeRulesManager.apply_rules(
                conditions or {},
                species_id,
                season
            )
            result["applied_rules"] = rules_result
            
            # 4. Prédire niveau d'activité
            temperature = conditions.get("temperature") if conditions else None
            prediction = SeasonalModelsManager.predict_activity_level(
                model_id,
                target_date,
                temperature,
                conditions
            )
            if prediction.get("success"):
                result["activity_prediction"] = prediction
            
            # 5. Recommandations habitat
            result["habitat_recommendations"] = KnowledgeService._generate_habitat_recommendations(
                species_id,
                phase_result.get("phase", {}) if phase_result.get("success") else {},
                rules_result.get("location_preferences", [])
            )
            
            result["success"] = True
            return result
            
        except Exception as e:
            logger.error(f"Error in query_knowledge: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def _generate_habitat_recommendations(species_id: str, phase: dict, location_prefs: List[dict]) -> List[dict]:
        """Générer recommandations d'habitat basées sur la phase et les règles"""
        recommendations = []
        
        # Habitats de la phase
        phase_habitats = phase.get("habitat_focus", [])
        for habitat in phase_habitats:
            recommendations.append({
                "habitat": habitat,
                "source": "seasonal_phase",
                "priority": 0.8,
                "reason_fr": f"Habitat préféré pendant {phase.get('name_fr', 'cette période')}"
            })
        
        # Habitats des règles
        for pref in location_prefs:
            for habitat in pref.get("habitats", []):
                if habitat not in [r["habitat"] for r in recommendations]:
                    recommendations.append({
                        "habitat": habitat,
                        "source": "behavior_rule",
                        "priority": pref.get("strength", 0.5),
                        "reason_fr": "Conditions actuelles favorisent cet habitat"
                    })
        
        # Trier par priorité
        recommendations.sort(key=lambda x: x["priority"], reverse=True)
        
        return recommendations[:5]  # Top 5
    
    # ============ VARIABLES ============
    
    @staticmethod
    async def get_habitat_variables(db) -> dict:
        """Récupérer les variables d'habitat depuis le fichier JSON"""
        try:
            import json
            import os
            
            # Chemin vers le fichier JSON des variables
            base_path = os.path.dirname(os.path.abspath(__file__))
            variables_path = os.path.join(base_path, "data", "habitat_variables.json")
            
            base_variables = []
            if os.path.exists(variables_path):
                with open(variables_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    base_variables = data.get("variables", [])
            
            # Ajouter variables custom depuis DB
            custom = await db.habitat_variables.find({}, {"_id": 0}).to_list(50)
            
            return {
                "success": True,
                "total": len(base_variables) + len(custom),
                "variables": base_variables + custom
            }
        except Exception as e:
            logger.error(f"Error getting habitat variables: {e}")
            return {"success": False, "error": str(e)}


logger.info("KnowledgeService initialized - V5 LEGO Module")
