"""
BIONIC Knowledge Validation Pipeline - V5-ULTIME
=================================================

Pipeline de validation pour:
- Vérifier la cohérence des données
- Valider les règles comportementales
- Tester les modèles saisonniers
- Scorer la qualité des connaissances

Module isolé - aucun import croisé.
"""

from datetime import datetime, timezone
from typing import List
import logging

logger = logging.getLogger(__name__)


class ValidationPipeline:
    """Pipeline de validation des connaissances"""
    
    # Seuils de validation
    THRESHOLDS = {
        "min_confidence_score": 0.4,
        "min_source_reliability": 0.5,
        "min_validation_count": 3,
        "max_rule_age_days": 365,
        "min_species_fields": 5
    }
    
    # Champs requis par type
    REQUIRED_FIELDS = {
        "species": ["id", "scientific_name", "common_name_fr", "category", "temperature_range"],
        "rule": ["id", "name", "species", "conditions", "effect_type", "effect_value", "confidence"],
        "source": ["id", "name", "source_type", "reference"],
        "seasonal_model": ["id", "species_id", "region", "phases"]
    }
    
    # ============ VALIDATION METHODS ============
    
    @staticmethod
    def validate_species(species_data: dict) -> dict:
        """Valider les données d'une espèce"""
        errors = []
        warnings = []
        suggestions = []
        
        # Vérifier champs requis
        for field in ValidationPipeline.REQUIRED_FIELDS["species"]:
            if field not in species_data or not species_data[field]:
                errors.append(f"Champ requis manquant: {field}")
        
        # Vérifier plage de température
        temp_range = species_data.get("temperature_range", {})
        if temp_range:
            if temp_range.get("optimal_min", 0) > temp_range.get("optimal_max", 100):
                errors.append("temperature_range: optimal_min > optimal_max")
            if temp_range.get("tolerance_min", 0) > temp_range.get("optimal_min", 0):
                warnings.append("temperature_range: tolerance_min devrait être <= optimal_min")
        
        # Vérifier patterns d'activité
        patterns = species_data.get("activity_patterns", [])
        if len(patterns) < 2:
            warnings.append("Moins de 2 patterns d'activité définis")
        
        # Vérifier comportements saisonniers
        seasonal = species_data.get("seasonal_behaviors", [])
        if len(seasonal) < 3:
            suggestions.append("Ajouter plus de comportements saisonniers pour une couverture complète")
        
        # Vérifier score de qualité
        quality = species_data.get("data_quality_score", 0)
        if quality < ValidationPipeline.THRESHOLDS["min_confidence_score"]:
            warnings.append(f"Score de qualité faible: {quality}")
        
        # Vérifier sources
        sources = species_data.get("sources", [])
        if len(sources) == 0:
            errors.append("Aucune source référencée")
        elif len(sources) < 2:
            suggestions.append("Ajouter des sources supplémentaires pour améliorer la fiabilité")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "suggestions": suggestions,
            "validation_score": ValidationPipeline._calculate_validation_score(errors, warnings, suggestions)
        }
    
    @staticmethod
    def validate_rule(rule_data: dict) -> dict:
        """Valider une règle comportementale"""
        errors = []
        warnings = []
        suggestions = []
        
        # Vérifier champs requis
        for field in ValidationPipeline.REQUIRED_FIELDS["rule"]:
            if field not in rule_data or not rule_data[field]:
                errors.append(f"Champ requis manquant: {field}")
        
        # Vérifier espèces ciblées
        species = rule_data.get("species", [])
        if not species:
            errors.append("Aucune espèce ciblée")
        
        # Vérifier conditions
        conditions = rule_data.get("conditions", {})
        if not conditions:
            warnings.append("Aucune condition définie (règle toujours applicable)")
        
        # Vérifier effet
        effect_value = rule_data.get("effect_value", 0)
        effect_type = rule_data.get("effect_type", "")
        
        if effect_type == "activity_modifier":
            if not -1 <= effect_value <= 1:
                errors.append(f"effect_value hors plage pour activity_modifier: {effect_value}")
        elif effect_type == "location_preference":
            if not 0 <= effect_value <= 1:
                errors.append(f"effect_value hors plage pour location_preference: {effect_value}")
        
        # Vérifier confiance
        confidence_score = rule_data.get("confidence_score", 0)
        if confidence_score < ValidationPipeline.THRESHOLDS["min_confidence_score"]:
            warnings.append(f"Score de confiance faible: {confidence_score}")
        
        # Vérifier sources
        source_ids = rule_data.get("source_ids", [])
        if not source_ids:
            warnings.append("Aucune source référencée")
        
        # Vérifier validations
        validation_count = rule_data.get("validation_count", 0)
        if validation_count < ValidationPipeline.THRESHOLDS["min_validation_count"]:
            suggestions.append(f"Règle nécessite plus de validations terrain ({validation_count}/{ValidationPipeline.THRESHOLDS['min_validation_count']})")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "suggestions": suggestions,
            "validation_score": ValidationPipeline._calculate_validation_score(errors, warnings, suggestions)
        }
    
    @staticmethod
    def validate_source(source_data: dict) -> dict:
        """Valider une source de connaissances"""
        errors = []
        warnings = []
        suggestions = []
        
        # Vérifier champs requis
        for field in ValidationPipeline.REQUIRED_FIELDS["source"]:
            if field not in source_data or not source_data[field]:
                errors.append(f"Champ requis manquant: {field}")
        
        # Vérifier type de source
        source_type = source_data.get("source_type", "")
        valid_types = ["scientific_paper", "government_report", "expert_interview", 
                       "field_observation", "traditional_knowledge", "user_report", 
                       "sensor_data", "ai_generated"]
        if source_type not in valid_types:
            errors.append(f"Type de source invalide: {source_type}")
        
        # Vérifier fiabilité
        reliability = source_data.get("reliability_score", 0)
        if reliability < ValidationPipeline.THRESHOLDS["min_source_reliability"]:
            warnings.append(f"Score de fiabilité faible: {reliability}")
        
        # Suggestions selon type
        if source_type == "scientific_paper" and not source_data.get("peer_reviewed"):
            warnings.append("Article scientifique non peer-reviewed")
        
        if source_type == "user_report" and source_data.get("reliability_score", 0) > 0.7:
            warnings.append("Score de fiabilité élevé pour un rapport utilisateur")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "suggestions": suggestions,
            "validation_score": ValidationPipeline._calculate_validation_score(errors, warnings, suggestions)
        }
    
    @staticmethod
    def validate_seasonal_model(model_data: dict) -> dict:
        """Valider un modèle saisonnier"""
        errors = []
        warnings = []
        suggestions = []
        
        # Vérifier champs requis
        for field in ValidationPipeline.REQUIRED_FIELDS["seasonal_model"]:
            if field not in model_data or not model_data[field]:
                errors.append(f"Champ requis manquant: {field}")
        
        # Vérifier phases
        phases = model_data.get("phases", [])
        if len(phases) < 3:
            warnings.append(f"Seulement {len(phases)} phases définies (min recommandé: 3)")
        
        # Vérifier couverture annuelle
        covered_months = set()
        for phase in phases:
            start_m = phase.get("start_month", 0)
            end_m = phase.get("end_month", 0)
            if start_m <= end_m:
                covered_months.update(range(start_m, end_m + 1))
            else:  # Traverse l'année
                covered_months.update(range(start_m, 13))
                covered_months.update(range(1, end_m + 1))
        
        missing_months = set(range(1, 13)) - covered_months
        if missing_months:
            warnings.append(f"Mois non couverts: {sorted(missing_months)}")
        
        # Vérifier niveaux d'activité
        for phase in phases:
            activity = phase.get("activity_level", 0)
            if not 0 <= activity <= 1:
                errors.append(f"Phase '{phase.get('name', '?')}': activity_level hors plage [0-1]")
        
        # Vérifier précision
        accuracy = model_data.get("accuracy_score", 0)
        if accuracy < 0.6:
            warnings.append(f"Score de précision faible: {accuracy}")
        
        # Suggestions
        if not model_data.get("regional_adjustments"):
            suggestions.append("Ajouter des ajustements régionaux pour plus de précision")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "suggestions": suggestions,
            "validation_score": ValidationPipeline._calculate_validation_score(errors, warnings, suggestions)
        }
    
    # ============ BATCH VALIDATION ============
    
    @staticmethod
    async def validate_all(db) -> dict:
        """Valider toutes les connaissances"""
        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "species": {"valid": 0, "invalid": 0, "total": 0},
            "rules": {"valid": 0, "invalid": 0, "total": 0},
            "sources": {"valid": 0, "invalid": 0, "total": 0},
            "seasonal_models": {"valid": 0, "invalid": 0, "total": 0},
            "overall_health": 0.0,
            "critical_issues": []
        }
        
        try:
            # Valider espèces
            species_list = await db.knowledge_species.find({}, {"_id": 0}).to_list(100)
            for species in species_list:
                validation = ValidationPipeline.validate_species(species)
                results["species"]["total"] += 1
                if validation["is_valid"]:
                    results["species"]["valid"] += 1
                else:
                    results["species"]["invalid"] += 1
                    results["critical_issues"].extend([
                        f"Species '{species.get('id', '?')}': {e}" for e in validation["errors"]
                    ])
            
            # Valider règles
            rules_list = await db.knowledge_rules.find({}, {"_id": 0}).to_list(200)
            for rule in rules_list:
                validation = ValidationPipeline.validate_rule(rule)
                results["rules"]["total"] += 1
                if validation["is_valid"]:
                    results["rules"]["valid"] += 1
                else:
                    results["rules"]["invalid"] += 1
            
            # Valider sources
            sources_list = await db.knowledge_sources.find({}, {"_id": 0}).to_list(100)
            for source in sources_list:
                validation = ValidationPipeline.validate_source(source)
                results["sources"]["total"] += 1
                if validation["is_valid"]:
                    results["sources"]["valid"] += 1
                else:
                    results["sources"]["invalid"] += 1
            
            # Valider modèles saisonniers
            models_list = await db.seasonal_models.find({}, {"_id": 0}).to_list(50)
            for model in models_list:
                validation = ValidationPipeline.validate_seasonal_model(model)
                results["seasonal_models"]["total"] += 1
                if validation["is_valid"]:
                    results["seasonal_models"]["valid"] += 1
                else:
                    results["seasonal_models"]["invalid"] += 1
            
            # Calculer santé globale
            total_valid = (results["species"]["valid"] + results["rules"]["valid"] + 
                          results["sources"]["valid"] + results["seasonal_models"]["valid"])
            total = (results["species"]["total"] + results["rules"]["total"] + 
                    results["sources"]["total"] + results["seasonal_models"]["total"])
            
            results["overall_health"] = round(total_valid / max(total, 1), 3)
            
        except Exception as e:
            logger.error(f"Error in batch validation: {e}")
            results["error"] = str(e)
        
        return results
    
    # ============ HELPERS ============
    
    @staticmethod
    def _calculate_validation_score(errors: List[str], warnings: List[str], suggestions: List[str]) -> float:
        """Calculer un score de validation"""
        score = 1.0
        score -= len(errors) * 0.3
        score -= len(warnings) * 0.1
        score -= len(suggestions) * 0.02
        return max(0.0, min(1.0, score))
    
    @staticmethod
    def generate_validation_report(validation_result: dict, entity_type: str, entity_id: str) -> dict:
        """Générer un rapport de validation formaté"""
        return {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "is_valid": validation_result["is_valid"],
            "validation_score": validation_result.get("validation_score", 0),
            "summary": {
                "errors": len(validation_result.get("errors", [])),
                "warnings": len(validation_result.get("warnings", [])),
                "suggestions": len(validation_result.get("suggestions", []))
            },
            "details": validation_result
        }


logger.info("ValidationPipeline initialized - V5 LEGO Module")
