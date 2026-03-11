"""
BIONIC Knowledge Rules - V5-ULTIME
==================================

Gestion des règles comportementales empiriques et scientifiques.
Règles basées sur:
- Études scientifiques
- Observations terrain
- Connaissances traditionnelles
- Données capteurs

Module isolé - aucun import croisé.
"""

from datetime import datetime, timezone
import logging
import uuid

logger = logging.getLogger(__name__)


class KnowledgeRulesManager:
    """Gestionnaire des règles comportementales"""
    
    # Règles de base empiriques (Québec)
    BASE_RULES = {
        # ===== ORIGNAL (MOOSE) =====
        "moose_thermal_stress": {
            "id": "moose_thermal_stress",
            "name": "Moose Thermal Stress Response",
            "name_fr": "Réponse au stress thermique de l'orignal",
            "description": "Moose reduce activity when temperature exceeds 14°C and seek thermal cover",
            "description_fr": "L'orignal réduit son activité lorsque la température dépasse 14°C et recherche un couvert thermique",
            "species": ["moose"],
            "seasons": ["summer", "fall"],
            "habitats": ["coniferous_forest", "mixed_forest", "wetland"],
            "conditions": {
                "temperature": {"min": 14, "trigger": "above"},
                "time_of_day": ["midday", "afternoon"]
            },
            "effect_type": "activity_modifier",
            "effect_value": -0.4,
            "effect_description": "40% reduction in daytime activity",
            "confidence": "scientific",
            "confidence_score": 0.92,
            "source_ids": ["mffp_quebec"],
            "is_active": True,
            "tags": ["thermal", "behavior", "critical"]
        },
        "moose_rut_peak": {
            "id": "moose_rut_peak",
            "name": "Moose Rut Peak Activity",
            "name_fr": "Pic d'activité du rut de l'orignal",
            "description": "Bull moose dramatically increase movement and calling during rut peak",
            "description_fr": "Les mâles augmentent drastiquement leurs déplacements et vocalisations pendant le pic du rut",
            "species": ["moose"],
            "seasons": ["rut"],
            "habitats": ["mixed_forest", "wetland", "lake_shore"],
            "conditions": {
                "date_range": {"start_month": 9, "end_month": 10, "peak_days": [25, 5]},
                "temperature": {"max": 15, "optimal": 5}
            },
            "effect_type": "activity_modifier",
            "effect_value": 0.8,
            "effect_description": "80% increase in movement and vocalization",
            "confidence": "scientific",
            "confidence_score": 0.95,
            "source_ids": ["mffp_quebec", "fqf"],
            "is_active": True,
            "tags": ["rut", "breeding", "critical"]
        },
        "moose_dawn_dusk": {
            "id": "moose_dawn_dusk",
            "name": "Moose Crepuscular Activity Pattern",
            "name_fr": "Activité crépusculaire de l'orignal",
            "description": "Moose are most active during dawn and dusk periods",
            "description_fr": "L'orignal est plus actif à l'aube et au crépuscule",
            "species": ["moose"],
            "seasons": ["fall", "winter", "spring", "summer"],
            "habitats": ["all"],
            "conditions": {
                "time_of_day": ["dawn", "dusk"],
                "light_level": {"min": 0.1, "max": 0.6}
            },
            "effect_type": "activity_modifier",
            "effect_value": 0.6,
            "effect_description": "60% higher activity at crepuscular periods",
            "confidence": "scientific",
            "confidence_score": 0.90,
            "source_ids": ["mffp_quebec"],
            "is_active": True,
            "tags": ["timing", "activity", "fundamental"]
        },
        
        # ===== CERF DE VIRGINIE (DEER) =====
        "deer_moon_phase": {
            "id": "deer_moon_phase",
            "name": "Deer Moon Phase Response",
            "name_fr": "Réponse du cerf aux phases lunaires",
            "description": "Deer activity increases during full moon, especially during rut",
            "description_fr": "L'activité du cerf augmente pendant la pleine lune, surtout pendant le rut",
            "species": ["deer"],
            "seasons": ["rut", "pre_rut", "fall"],
            "habitats": ["deciduous_forest", "mixed_forest", "agricultural"],
            "conditions": {
                "moon_phase": {"phases": ["full", "waxing_gibbous"], "intensity": 0.7}
            },
            "effect_type": "activity_modifier",
            "effect_value": 0.35,
            "effect_description": "35% increase in nocturnal movement",
            "confidence": "empirical",
            "confidence_score": 0.75,
            "source_ids": ["fqf"],
            "is_active": True,
            "tags": ["moon", "nocturnal", "rut"]
        },
        "deer_cold_front": {
            "id": "deer_cold_front",
            "name": "Deer Cold Front Response",
            "name_fr": "Réponse du cerf aux fronts froids",
            "description": "Deer increase feeding activity 24-48h before cold front arrival",
            "description_fr": "Le cerf intensifie son alimentation 24-48h avant l'arrivée d'un front froid",
            "species": ["deer"],
            "seasons": ["fall", "winter"],
            "habitats": ["deciduous_forest", "mixed_forest", "agricultural"],
            "conditions": {
                "pressure_change": {"direction": "falling", "rate": -5},
                "temperature_forecast": {"drop": -10, "hours": 48}
            },
            "effect_type": "activity_modifier",
            "effect_value": 0.5,
            "effect_description": "50% increase in feeding activity before front",
            "confidence": "empirical",
            "confidence_score": 0.80,
            "source_ids": ["fqf", "mffp_quebec"],
            "is_active": True,
            "tags": ["weather", "feeding", "critical"]
        },
        
        # ===== OURS NOIR (BEAR) =====
        "bear_hyperphagia": {
            "id": "bear_hyperphagia",
            "name": "Bear Hyperphagia Period",
            "name_fr": "Période d'hyperphagie de l'ours",
            "description": "Bears dramatically increase feeding to prepare for hibernation",
            "description_fr": "L'ours augmente drastiquement son alimentation pour préparer l'hibernation",
            "species": ["bear"],
            "seasons": ["fall"],
            "habitats": ["mixed_forest", "deciduous_forest", "wetland"],
            "conditions": {
                "date_range": {"start_month": 8, "end_month": 10},
                "food_availability": {"min": 0.5}
            },
            "effect_type": "activity_modifier",
            "effect_value": 1.0,
            "effect_description": "Feeding duration doubles, 20+ hours/day",
            "confidence": "scientific",
            "confidence_score": 0.95,
            "source_ids": ["mffp_quebec"],
            "is_active": True,
            "tags": ["feeding", "seasonal", "critical"]
        },
        "bear_mast_attraction": {
            "id": "bear_mast_attraction",
            "name": "Bear Mast Crop Attraction",
            "name_fr": "Attraction de l'ours vers les glands",
            "description": "Bears concentrate in areas with abundant oak mast",
            "description_fr": "L'ours se concentre dans les zones riches en glands de chêne",
            "species": ["bear"],
            "seasons": ["fall"],
            "habitats": ["deciduous_forest", "mixed_forest"],
            "conditions": {
                "vegetation": {"mast_index": {"min": 0.6}},
                "oak_presence": True
            },
            "effect_type": "location_preference",
            "effect_value": 0.8,
            "effect_description": "Strong preference for mast-rich areas",
            "confidence": "scientific",
            "confidence_score": 0.90,
            "source_ids": ["mffp_quebec"],
            "is_active": True,
            "tags": ["food", "habitat", "fall"]
        },
        
        # ===== RÈGLES GÉNÉRALES =====
        "wind_avoidance": {
            "id": "wind_avoidance",
            "name": "High Wind Activity Reduction",
            "name_fr": "Réduction d'activité par vent fort",
            "description": "Most ungulates reduce movement in high wind conditions",
            "description_fr": "La plupart des ongulés réduisent leurs déplacements par vent fort",
            "species": ["moose", "deer", "caribou"],
            "seasons": ["all"],
            "habitats": ["all"],
            "conditions": {
                "wind_speed": {"min": 25, "unit": "km/h"}
            },
            "effect_type": "activity_modifier",
            "effect_value": -0.5,
            "effect_description": "50% reduction in exposed area activity",
            "confidence": "scientific",
            "confidence_score": 0.85,
            "source_ids": ["mffp_quebec"],
            "is_active": True,
            "tags": ["weather", "wind", "fundamental"]
        },
        "precipitation_shelter": {
            "id": "precipitation_shelter",
            "name": "Precipitation Shelter Seeking",
            "name_fr": "Recherche d'abri lors de précipitations",
            "description": "Wildlife seeks conifer cover during heavy precipitation",
            "description_fr": "La faune recherche un couvert de conifères lors de fortes précipitations",
            "species": ["moose", "deer", "bear"],
            "seasons": ["all"],
            "habitats": ["coniferous_forest", "mixed_forest"],
            "conditions": {
                "precipitation": {"min": 5, "unit": "mm/h"}
            },
            "effect_type": "location_preference",
            "effect_value": 0.7,
            "effect_description": "Strong preference for conifer stands",
            "confidence": "empirical",
            "confidence_score": 0.80,
            "source_ids": ["fqf"],
            "is_active": True,
            "tags": ["weather", "shelter", "fundamental"]
        }
    }
    
    # ============ CRUD OPERATIONS ============
    
    @staticmethod
    async def get_all_rules(db, species: str = None, season: str = None, 
                           confidence: str = None, is_active: bool = True, limit: int = 100) -> dict:
        """Récupérer toutes les règles avec filtres"""
        try:
            # Commencer avec les règles de base
            rules = list(KnowledgeRulesManager.BASE_RULES.values())
            
            # Ajouter les règles custom de la DB
            query = {"is_active": is_active} if is_active else {}
            custom_rules = await db.knowledge_rules.find(query, {"_id": 0}).limit(limit).to_list(limit)
            rules.extend(custom_rules)
            
            # Filtrer
            if species:
                rules = [r for r in rules if species in r.get("species", [])]
            if season:
                rules = [r for r in rules if season in r.get("seasons", []) or "all" in r.get("seasons", [])]
            if confidence:
                rules = [r for r in rules if r.get("confidence") == confidence]
            
            return {
                "success": True,
                "total": len(rules),
                "rules": rules
            }
        except Exception as e:
            logger.error(f"Error getting rules: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def get_rule_by_id(db, rule_id: str) -> dict:
        """Récupérer une règle par ID"""
        try:
            if rule_id in KnowledgeRulesManager.BASE_RULES:
                return {
                    "success": True,
                    "rule": KnowledgeRulesManager.BASE_RULES[rule_id],
                    "is_base": True
                }
            
            rule = await db.knowledge_rules.find_one({"id": rule_id}, {"_id": 0})
            if rule:
                return {"success": True, "rule": rule, "is_base": False}
            
            return {"success": False, "error": "Règle non trouvée"}
        except Exception as e:
            logger.error(f"Error getting rule: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def add_rule(db, rule_data: dict) -> dict:
        """Ajouter une nouvelle règle"""
        try:
            rule = {
                "id": rule_data.get("id", str(uuid.uuid4())),
                "name": rule_data.get("name"),
                "name_fr": rule_data.get("name_fr"),
                "description": rule_data.get("description"),
                "description_fr": rule_data.get("description_fr"),
                "species": rule_data.get("species", []),
                "seasons": rule_data.get("seasons", []),
                "habitats": rule_data.get("habitats", []),
                "conditions": rule_data.get("conditions", {}),
                "effect_type": rule_data.get("effect_type", "activity_modifier"),
                "effect_value": rule_data.get("effect_value", 0),
                "effect_description": rule_data.get("effect_description", ""),
                "confidence": rule_data.get("confidence", "empirical"),
                "confidence_score": rule_data.get("confidence_score", 0.5),
                "validation_count": 0,
                "source_ids": rule_data.get("source_ids", []),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "is_active": True,
                "tags": rule_data.get("tags", [])
            }
            
            await db.knowledge_rules.insert_one(rule)
            rule.pop("_id", None)
            
            return {"success": True, "rule": rule}
        except Exception as e:
            logger.error(f"Error adding rule: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def update_rule(db, rule_id: str, updates: dict) -> dict:
        """Mettre à jour une règle"""
        try:
            if rule_id in KnowledgeRulesManager.BASE_RULES:
                return {"success": False, "error": "Impossible de modifier une règle de base"}
            
            protected = ["id", "created_at"]
            for field in protected:
                updates.pop(field, None)
            
            updates["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            result = await db.knowledge_rules.update_one(
                {"id": rule_id},
                {"$set": updates}
            )
            
            if result.matched_count == 0:
                return {"success": False, "error": "Règle non trouvée"}
            
            return {"success": True, "message": "Règle mise à jour"}
        except Exception as e:
            logger.error(f"Error updating rule: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def toggle_rule(db, rule_id: str, is_active: bool) -> dict:
        """Activer/désactiver une règle"""
        try:
            if rule_id in KnowledgeRulesManager.BASE_RULES:
                return {"success": False, "error": "Impossible de désactiver une règle de base"}
            
            result = await db.knowledge_rules.update_one(
                {"id": rule_id},
                {"$set": {"is_active": is_active}}
            )
            
            if result.matched_count == 0:
                return {"success": False, "error": "Règle non trouvée"}
            
            return {"success": True, "is_active": is_active}
        except Exception as e:
            logger.error(f"Error toggling rule: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def validate_rule(db, rule_id: str, validation_result: bool) -> dict:
        """Enregistrer une validation de règle"""
        try:
            inc_value = 1 if validation_result else 0
            
            # Pour les règles custom
            if rule_id not in KnowledgeRulesManager.BASE_RULES:
                await db.knowledge_rules.update_one(
                    {"id": rule_id},
                    {"$inc": {"validation_count": inc_value}}
                )
            
            # Logger la validation
            await db.knowledge_rule_validations.insert_one({
                "rule_id": rule_id,
                "result": validation_result,
                "validated_at": datetime.now(timezone.utc).isoformat()
            })
            
            return {"success": True, "message": "Validation enregistrée"}
        except Exception as e:
            logger.error(f"Error validating rule: {e}")
            return {"success": False, "error": str(e)}
    
    # ============ RULE APPLICATION ============
    
    @staticmethod
    def apply_rules(conditions: dict, species: str, season: str) -> dict:
        """Appliquer les règles pertinentes aux conditions données"""
        applicable_rules = []
        total_modifier = 0.0
        location_preferences = []
        
        for rule_id, rule in KnowledgeRulesManager.BASE_RULES.items():
            if not rule.get("is_active", True):
                continue
            
            # Vérifier applicabilité espèce/saison
            if species not in rule.get("species", []):
                continue
            if season not in rule.get("seasons", []) and "all" not in rule.get("seasons", []):
                continue
            
            # Vérifier conditions
            rule_conditions = rule.get("conditions", {})
            match_score = KnowledgeRulesManager._evaluate_conditions(conditions, rule_conditions)
            
            if match_score > 0.5:
                applicable_rules.append({
                    "rule_id": rule_id,
                    "name": rule["name_fr"],
                    "match_score": match_score,
                    "effect_type": rule["effect_type"],
                    "effect_value": rule["effect_value"] * match_score,
                    "confidence": rule["confidence_score"]
                })
                
                if rule["effect_type"] == "activity_modifier":
                    total_modifier += rule["effect_value"] * match_score * rule["confidence_score"]
                elif rule["effect_type"] == "location_preference":
                    location_preferences.append({
                        "habitats": rule.get("habitats", []),
                        "strength": rule["effect_value"] * match_score
                    })
        
        return {
            "success": True,
            "applicable_rules": applicable_rules,
            "activity_modifier": round(total_modifier, 3),
            "location_preferences": location_preferences,
            "rules_evaluated": len(KnowledgeRulesManager.BASE_RULES)
        }
    
    @staticmethod
    def _evaluate_conditions(actual: dict, required: dict) -> float:
        """Évaluer le degré de correspondance entre conditions actuelles et requises"""
        if not required:
            return 1.0
        
        total_score = 0
        total_weight = 0
        
        for key, req_value in required.items():
            if key not in actual:
                continue
            
            actual_value = actual[key]
            
            if isinstance(req_value, dict):
                if "min" in req_value and "max" in req_value:
                    if req_value["min"] <= actual_value <= req_value["max"]:
                        total_score += 1
                    else:
                        total_score += max(0, 1 - abs(actual_value - (req_value["min"] + req_value["max"])/2) / 10)
                elif "min" in req_value:
                    if actual_value >= req_value["min"]:
                        total_score += 1
                    else:
                        total_score += max(0, actual_value / req_value["min"])
                elif "max" in req_value:
                    if actual_value <= req_value["max"]:
                        total_score += 1
                    else:
                        total_score += max(0, req_value["max"] / actual_value)
            elif isinstance(req_value, list):
                if actual_value in req_value:
                    total_score += 1
            else:
                if actual_value == req_value:
                    total_score += 1
            
            total_weight += 1
        
        return total_score / max(total_weight, 1)
    
    # ============ STATISTICS ============
    
    @staticmethod
    async def get_rules_stats(db) -> dict:
        """Statistiques des règles"""
        try:
            custom_rules = await db.knowledge_rules.count_documents({})
            active_custom = await db.knowledge_rules.count_documents({"is_active": True})
            
            # Par espèce
            by_species = {}
            for species in ["moose", "deer", "bear", "caribou"]:
                base_count = len([r for r in KnowledgeRulesManager.BASE_RULES.values() 
                                 if species in r.get("species", [])])
                custom_count = await db.knowledge_rules.count_documents({"species": species})
                by_species[species] = base_count + custom_count
            
            # Par confiance
            by_confidence = {}
            for conf in ["scientific", "empirical", "theoretical", "hybrid"]:
                base_count = len([r for r in KnowledgeRulesManager.BASE_RULES.values() 
                                 if r.get("confidence") == conf])
                custom_count = await db.knowledge_rules.count_documents({"confidence": conf})
                by_confidence[conf] = base_count + custom_count
            
            return {
                "success": True,
                "stats": {
                    "total_base": len(KnowledgeRulesManager.BASE_RULES),
                    "total_custom": custom_rules,
                    "total": len(KnowledgeRulesManager.BASE_RULES) + custom_rules,
                    "active": len(KnowledgeRulesManager.BASE_RULES) + active_custom,
                    "by_species": by_species,
                    "by_confidence": by_confidence
                }
            }
        except Exception as e:
            logger.error(f"Error getting rules stats: {e}")
            return {"success": False, "error": str(e)}


logger.info("KnowledgeRulesManager initialized - V5 LEGO Module")
