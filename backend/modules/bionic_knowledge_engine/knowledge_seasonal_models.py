"""
BIONIC Knowledge Seasonal Models - V5-ULTIME
=============================================

Modèles saisonniers pour prédire les comportements selon:
- Photopériode
- Température
- Phases lunaires
- Cycles biologiques (rut, migration, etc.)

Module isolé - aucun import croisé.
"""

from datetime import datetime, timezone, date
import logging
import uuid

logger = logging.getLogger(__name__)


class SeasonalModelsManager:
    """Gestionnaire des modèles saisonniers"""
    
    # Modèles saisonniers de base par espèce et région
    BASE_SEASONAL_MODELS = {
        # ===== ORIGNAL QUÉBEC =====
        "moose_quebec_south": {
            "id": "moose_quebec_south",
            "species_id": "moose",
            "region": "quebec_south",
            "year": 2024,
            "phases": [
                {
                    "name": "spring_dispersal",
                    "name_fr": "Dispersion printanière",
                    "start_month": 4, "start_day": 15,
                    "end_month": 5, "end_day": 31,
                    "activity_level": 0.7,
                    "habitat_focus": ["wetland", "regeneration"],
                    "behavior": "dispersal_feeding"
                },
                {
                    "name": "summer_range",
                    "name_fr": "Territoire estival",
                    "start_month": 6, "start_day": 1,
                    "end_month": 8, "end_day": 31,
                    "activity_level": 0.5,
                    "habitat_focus": ["wetland", "lake_shore", "coniferous_forest"],
                    "behavior": "thermal_regulation"
                },
                {
                    "name": "pre_rut",
                    "name_fr": "Pré-rut",
                    "start_month": 9, "start_day": 1,
                    "end_month": 9, "end_day": 20,
                    "activity_level": 0.75,
                    "habitat_focus": ["mixed_forest", "wetland"],
                    "behavior": "territorial_marking"
                },
                {
                    "name": "rut_peak",
                    "name_fr": "Pic du rut",
                    "start_month": 9, "start_day": 21,
                    "end_month": 10, "end_day": 15,
                    "peak_date": "10-01",
                    "activity_level": 1.0,
                    "habitat_focus": ["mixed_forest", "wetland", "lake_shore"],
                    "behavior": "breeding"
                },
                {
                    "name": "post_rut",
                    "name_fr": "Post-rut",
                    "start_month": 10, "start_day": 16,
                    "end_month": 11, "end_day": 15,
                    "activity_level": 0.6,
                    "habitat_focus": ["coniferous_forest", "mixed_forest"],
                    "behavior": "recovery_feeding"
                },
                {
                    "name": "winter_yard",
                    "name_fr": "Ravage hivernal",
                    "start_month": 11, "start_day": 16,
                    "end_month": 4, "end_day": 14,
                    "activity_level": 0.4,
                    "habitat_focus": ["coniferous_forest"],
                    "behavior": "energy_conservation"
                }
            ],
            "temperature_sensitivity": 0.7,
            "photoperiod_sensitivity": 0.85,
            "regional_adjustments": {
                "elevation_500m": -3,
                "elevation_1000m": -7,
                "latitude_north": -5
            },
            "accuracy_score": 0.88
        },
        
        # ===== CERF QUÉBEC =====
        "deer_quebec_south": {
            "id": "deer_quebec_south",
            "species_id": "deer",
            "region": "quebec_south",
            "year": 2024,
            "phases": [
                {
                    "name": "spring_recovery",
                    "name_fr": "Récupération printanière",
                    "start_month": 4, "start_day": 1,
                    "end_month": 5, "end_day": 31,
                    "activity_level": 0.8,
                    "habitat_focus": ["agricultural", "deciduous_forest"],
                    "behavior": "intensive_feeding"
                },
                {
                    "name": "summer_range",
                    "name_fr": "Territoire estival",
                    "start_month": 6, "start_day": 1,
                    "end_month": 9, "end_day": 30,
                    "activity_level": 0.6,
                    "habitat_focus": ["deciduous_forest", "agricultural"],
                    "behavior": "fawning_rearing"
                },
                {
                    "name": "pre_rut",
                    "name_fr": "Pré-rut",
                    "start_month": 10, "start_day": 15,
                    "end_month": 11, "end_day": 5,
                    "activity_level": 0.85,
                    "habitat_focus": ["deciduous_forest", "mixed_forest"],
                    "behavior": "rubbing_scraping"
                },
                {
                    "name": "rut_peak",
                    "name_fr": "Pic du rut",
                    "start_month": 11, "start_day": 6,
                    "end_month": 11, "end_day": 25,
                    "peak_date": "11-15",
                    "activity_level": 1.0,
                    "habitat_focus": ["deciduous_forest", "mixed_forest", "agricultural"],
                    "behavior": "breeding"
                },
                {
                    "name": "post_rut",
                    "name_fr": "Post-rut",
                    "start_month": 11, "start_day": 26,
                    "end_month": 12, "end_day": 31,
                    "activity_level": 0.5,
                    "habitat_focus": ["coniferous_forest", "mixed_forest"],
                    "behavior": "recovery"
                },
                {
                    "name": "winter_yard",
                    "name_fr": "Ravage hivernal",
                    "start_month": 1, "start_day": 1,
                    "end_month": 3, "end_day": 31,
                    "activity_level": 0.35,
                    "habitat_focus": ["coniferous_forest"],
                    "behavior": "yarding"
                }
            ],
            "temperature_sensitivity": 0.5,
            "photoperiod_sensitivity": 0.9,
            "regional_adjustments": {
                "latitude_south": 5,
                "latitude_north": -7
            },
            "accuracy_score": 0.85
        },
        
        # ===== OURS QUÉBEC =====
        "bear_quebec": {
            "id": "bear_quebec",
            "species_id": "bear",
            "region": "quebec_all",
            "year": 2024,
            "phases": [
                {
                    "name": "emergence",
                    "name_fr": "Émergence",
                    "start_month": 4, "start_day": 1,
                    "end_month": 5, "end_day": 15,
                    "activity_level": 0.6,
                    "habitat_focus": ["mixed_forest", "wetland"],
                    "behavior": "slow_foraging"
                },
                {
                    "name": "breeding",
                    "name_fr": "Reproduction",
                    "start_month": 5, "start_day": 16,
                    "end_month": 7, "end_day": 15,
                    "activity_level": 0.8,
                    "habitat_focus": ["mixed_forest", "deciduous_forest"],
                    "behavior": "breeding_roaming"
                },
                {
                    "name": "summer_foraging",
                    "name_fr": "Alimentation estivale",
                    "start_month": 7, "start_day": 16,
                    "end_month": 8, "end_day": 15,
                    "activity_level": 0.75,
                    "habitat_focus": ["wetland", "mixed_forest", "berry_patches"],
                    "behavior": "berry_feeding"
                },
                {
                    "name": "hyperphagia",
                    "name_fr": "Hyperphagie",
                    "start_month": 8, "start_day": 16,
                    "end_month": 10, "end_day": 31,
                    "peak_date": "09-15",
                    "activity_level": 1.0,
                    "habitat_focus": ["deciduous_forest", "agricultural", "mast_areas"],
                    "behavior": "intensive_feeding"
                },
                {
                    "name": "pre_denning",
                    "name_fr": "Pré-tanière",
                    "start_month": 11, "start_day": 1,
                    "end_month": 11, "end_day": 30,
                    "activity_level": 0.4,
                    "habitat_focus": ["coniferous_forest", "ridge"],
                    "behavior": "den_preparation"
                },
                {
                    "name": "hibernation",
                    "name_fr": "Hibernation",
                    "start_month": 12, "start_day": 1,
                    "end_month": 3, "end_day": 31,
                    "activity_level": 0.0,
                    "habitat_focus": ["den_sites"],
                    "behavior": "dormancy"
                }
            ],
            "temperature_sensitivity": 0.6,
            "photoperiod_sensitivity": 0.7,
            "regional_adjustments": {
                "mast_year_bonus": 0.2,
                "mast_failure_penalty": -0.3
            },
            "accuracy_score": 0.82
        },
        
        # ===== WAPITI QUÉBEC =====
        "elk_quebec": {
            "id": "elk_quebec",
            "species_id": "elk",
            "region": "quebec_south",
            "year": 2024,
            "phases": [
                {
                    "name": "spring_calving",
                    "name_fr": "Mise bas printanière",
                    "start_month": 5, "start_day": 15,
                    "end_month": 6, "end_day": 30,
                    "activity_level": 0.6,
                    "habitat_focus": ["meadow", "forest_edge"],
                    "behavior": "calving_nursing"
                },
                {
                    "name": "summer_grazing",
                    "name_fr": "Pâturage estival",
                    "start_month": 7, "start_day": 1,
                    "end_month": 8, "end_day": 31,
                    "activity_level": 0.7,
                    "habitat_focus": ["meadow", "alpine_meadow", "riparian"],
                    "behavior": "intensive_grazing"
                },
                {
                    "name": "pre_rut",
                    "name_fr": "Pré-rut",
                    "start_month": 9, "start_day": 1,
                    "end_month": 9, "end_day": 14,
                    "activity_level": 0.85,
                    "habitat_focus": ["meadow", "forest_edge"],
                    "behavior": "sparring_bugling_start"
                },
                {
                    "name": "rut_peak",
                    "name_fr": "Pic du rut (Bugling)",
                    "start_month": 9, "start_day": 15,
                    "end_month": 10, "end_day": 15,
                    "peak_date": "09-25",
                    "activity_level": 1.0,
                    "habitat_focus": ["meadow", "forest_edge", "wallow"],
                    "behavior": "breeding_bugling"
                },
                {
                    "name": "post_rut",
                    "name_fr": "Post-rut",
                    "start_month": 10, "start_day": 16,
                    "end_month": 11, "end_day": 30,
                    "activity_level": 0.55,
                    "habitat_focus": ["mixed_forest", "meadow"],
                    "behavior": "recovery_feeding"
                },
                {
                    "name": "winter_range",
                    "name_fr": "Territoire hivernal",
                    "start_month": 12, "start_day": 1,
                    "end_month": 5, "end_day": 14,
                    "activity_level": 0.4,
                    "habitat_focus": ["mixed_forest", "wind_sheltered"],
                    "behavior": "energy_conservation"
                }
            ],
            "temperature_sensitivity": 0.55,
            "photoperiod_sensitivity": 0.9,
            "regional_adjustments": {
                "elevation_500m": -2,
                "latitude_north": -4
            },
            "accuracy_score": 0.78
        }
    }
    
    # ============ PHASE CALCULATION ============
    
    @staticmethod
    def get_current_phase(model_id: str, target_date: date = None) -> dict:
        """Déterminer la phase actuelle pour un modèle"""
        if target_date is None:
            target_date = date.today()
        
        model = SeasonalModelsManager.BASE_SEASONAL_MODELS.get(model_id)
        if not model:
            return {"success": False, "error": "Modèle non trouvé"}
        
        current_month = target_date.month
        current_day = target_date.day
        
        for phase in model["phases"]:
            start_m, start_d = phase["start_month"], phase["start_day"]
            end_m, end_d = phase["end_month"], phase["end_day"]
            
            # Gérer les phases qui traversent l'année
            if start_m > end_m:  # Ex: Nov -> Apr
                if current_month >= start_m or current_month <= end_m:
                    if (current_month > start_m or (current_month == start_m and current_day >= start_d)) or \
                       (current_month < end_m or (current_month == end_m and current_day <= end_d)):
                        return {
                            "success": True,
                            "phase": phase,
                            "species_id": model["species_id"],
                            "region": model["region"]
                        }
            else:
                if (current_month > start_m or (current_month == start_m and current_day >= start_d)) and \
                   (current_month < end_m or (current_month == end_m and current_day <= end_d)):
                    return {
                        "success": True,
                        "phase": phase,
                        "species_id": model["species_id"],
                        "region": model["region"]
                    }
        
        return {"success": False, "error": "Aucune phase trouvée pour cette date"}
    
    @staticmethod
    def calculate_phase_progress(model_id: str, target_date: date = None) -> dict:
        """Calculer la progression dans la phase actuelle"""
        if target_date is None:
            target_date = date.today()
        
        phase_result = SeasonalModelsManager.get_current_phase(model_id, target_date)
        if not phase_result.get("success"):
            return phase_result
        
        phase = phase_result["phase"]
        start_date = date(target_date.year, phase["start_month"], phase["start_day"])
        end_date = date(target_date.year, phase["end_month"], phase["end_day"])
        
        # Ajuster si traversée d'année
        if phase["start_month"] > phase["end_month"]:
            if target_date.month <= phase["end_month"]:
                start_date = date(target_date.year - 1, phase["start_month"], phase["start_day"])
            else:
                end_date = date(target_date.year + 1, phase["end_month"], phase["end_day"])
        
        total_days = (end_date - start_date).days
        elapsed_days = (target_date - start_date).days
        progress = elapsed_days / max(total_days, 1)
        
        # Calculer si proche du pic
        peak_proximity = 0.0
        if "peak_date" in phase:
            peak_parts = phase["peak_date"].split("-")
            peak_date = date(target_date.year, int(peak_parts[0]), int(peak_parts[1]))
            days_to_peak = abs((target_date - peak_date).days)
            peak_proximity = max(0, 1 - (days_to_peak / 10))  # 10 jours de fenêtre
        
        return {
            "success": True,
            "phase": phase,
            "progress": round(progress, 3),
            "days_remaining": total_days - elapsed_days,
            "peak_proximity": round(peak_proximity, 3),
            "activity_level": phase["activity_level"] * (1 + peak_proximity * 0.2)
        }
    
    # ============ CRUD OPERATIONS ============
    
    @staticmethod
    async def get_all_models(db, species_id: str = None, region: str = None, limit: int = 50) -> dict:
        """Récupérer tous les modèles saisonniers"""
        try:
            models = list(SeasonalModelsManager.BASE_SEASONAL_MODELS.values())
            
            # Ajouter les modèles custom
            query = {}
            if species_id:
                query["species_id"] = species_id
            if region:
                query["region"] = region
            
            custom_models = await db.seasonal_models.find(query, {"_id": 0}).limit(limit).to_list(limit)
            models.extend(custom_models)
            
            # Filtrer les modèles de base si filtres appliqués
            if species_id:
                models = [m for m in models if m.get("species_id") == species_id]
            if region:
                models = [m for m in models if m.get("region") == region or region in m.get("region", "")]
            
            return {
                "success": True,
                "total": len(models),
                "models": models
            }
        except Exception as e:
            logger.error(f"Error getting seasonal models: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def get_model_by_id(db, model_id: str) -> dict:
        """Récupérer un modèle par ID"""
        try:
            if model_id in SeasonalModelsManager.BASE_SEASONAL_MODELS:
                return {
                    "success": True,
                    "model": SeasonalModelsManager.BASE_SEASONAL_MODELS[model_id],
                    "is_base": True
                }
            
            model = await db.seasonal_models.find_one({"id": model_id}, {"_id": 0})
            if model:
                return {"success": True, "model": model, "is_base": False}
            
            return {"success": False, "error": "Modèle non trouvé"}
        except Exception as e:
            logger.error(f"Error getting model: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def add_model(db, model_data: dict) -> dict:
        """Ajouter un nouveau modèle saisonnier"""
        try:
            model = {
                "id": model_data.get("id", str(uuid.uuid4())),
                "species_id": model_data.get("species_id"),
                "region": model_data.get("region"),
                "year": model_data.get("year", datetime.now().year),
                "phases": model_data.get("phases", []),
                "temperature_sensitivity": model_data.get("temperature_sensitivity", 0.5),
                "photoperiod_sensitivity": model_data.get("photoperiod_sensitivity", 0.5),
                "regional_adjustments": model_data.get("regional_adjustments", {}),
                "elevation_adjustments": model_data.get("elevation_adjustments", {}),
                "accuracy_score": model_data.get("accuracy_score", 0.5),
                "validation_observations": 0,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "is_active": True
            }
            
            await db.seasonal_models.insert_one(model)
            model.pop("_id", None)
            
            return {"success": True, "model": model}
        except Exception as e:
            logger.error(f"Error adding model: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def update_model(db, model_id: str, updates: dict) -> dict:
        """Mettre à jour un modèle"""
        try:
            if model_id in SeasonalModelsManager.BASE_SEASONAL_MODELS:
                return {"success": False, "error": "Impossible de modifier un modèle de base"}
            
            protected = ["id", "created_at"]
            for field in protected:
                updates.pop(field, None)
            
            updates["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            result = await db.seasonal_models.update_one(
                {"id": model_id},
                {"$set": updates}
            )
            
            if result.matched_count == 0:
                return {"success": False, "error": "Modèle non trouvé"}
            
            return {"success": True, "message": "Modèle mis à jour"}
        except Exception as e:
            logger.error(f"Error updating model: {e}")
            return {"success": False, "error": str(e)}
    
    # ============ PREDICTIONS ============
    
    @staticmethod
    def predict_activity_level(model_id: str, target_date: date = None,
                               temperature: float = None, conditions: dict = None) -> dict:
        """Prédire le niveau d'activité pour une date et des conditions données"""
        if target_date is None:
            target_date = date.today()
        
        phase_result = SeasonalModelsManager.calculate_phase_progress(model_id, target_date)
        if not phase_result.get("success"):
            return phase_result
        
        model = SeasonalModelsManager.BASE_SEASONAL_MODELS.get(model_id)
        base_activity = phase_result["activity_level"]
        
        # Ajustements température
        temp_modifier = 0.0
        if temperature is not None and model:
            temp_sensitivity = model.get("temperature_sensitivity", 0.5)
            # Réduction si trop chaud (surtout pour orignal)
            if model["species_id"] == "moose" and temperature > 14:
                temp_modifier = -0.1 * temp_sensitivity * (temperature - 14) / 10
            # Bonus si températures fraîches pendant le rut
            if phase_result["phase"]["name"] in ["rut_peak", "pre_rut"]:
                if 0 <= temperature <= 10:
                    temp_modifier = 0.1 * temp_sensitivity
        
        # Ajustements conditions
        condition_modifier = 0.0
        if conditions:
            if conditions.get("wind_speed", 0) > 25:
                condition_modifier -= 0.15
            if conditions.get("precipitation", 0) > 5:
                condition_modifier -= 0.1
            if conditions.get("barometric_trend") == "falling":
                condition_modifier += 0.1  # Augmentation avant front
        
        final_activity = min(1.0, max(0.0, base_activity + temp_modifier + condition_modifier))
        
        return {
            "success": True,
            "date": target_date.isoformat(),
            "phase": phase_result["phase"]["name_fr"],
            "base_activity": round(base_activity, 3),
            "temperature_modifier": round(temp_modifier, 3),
            "condition_modifier": round(condition_modifier, 3),
            "predicted_activity": round(final_activity, 3),
            "peak_proximity": phase_result["peak_proximity"],
            "confidence": model.get("accuracy_score", 0.7) if model else 0.5
        }
    
    # ============ STATISTICS ============
    
    @staticmethod
    async def get_models_stats(db) -> dict:
        """Statistiques des modèles saisonniers"""
        try:
            custom_models = await db.seasonal_models.count_documents({})
            active_models = await db.seasonal_models.count_documents({"is_active": True})
            
            # Par espèce
            by_species = {}
            for species in ["moose", "deer", "bear", "caribou"]:
                base_count = len([m for m in SeasonalModelsManager.BASE_SEASONAL_MODELS.values() 
                                 if m.get("species_id") == species])
                custom_count = await db.seasonal_models.count_documents({"species_id": species})
                by_species[species] = base_count + custom_count
            
            return {
                "success": True,
                "stats": {
                    "total_base": len(SeasonalModelsManager.BASE_SEASONAL_MODELS),
                    "total_custom": custom_models,
                    "total": len(SeasonalModelsManager.BASE_SEASONAL_MODELS) + custom_models,
                    "active": len(SeasonalModelsManager.BASE_SEASONAL_MODELS) + active_models,
                    "by_species": by_species
                }
            }
        except Exception as e:
            logger.error(f"Error getting models stats: {e}")
            return {"success": False, "error": str(e)}


logger.info("SeasonalModelsManager initialized - V5 LEGO Module")
