"""
BIONIC ENGINE - Behavioral Models Module
PHASE G - P0-BETA2 IMPLEMENTATION
Version: 1.0.0-beta2

Module de modelisation et prediction comportementale.
Strictement conforme au contrat: behavioral_models_contract.json

INTEGRATION DES 12 FACTEURS COMPORTEMENTAUX (BIONIC V5 ULTIME x2):
1. Predation (PredatorRisk, PredatorCorridors)
2. Stress physiologique (Thermal/Hydric/Social Stress)
3. Hierarchie sociale (DominanceScore, GroupBehavior)
4. Competition inter-especes
5. Signaux faibles (WeakSignals, Anomalies)
6. Cycles hormonaux (rut, lactation, croissance des bois)
7. Cycles digestifs (feeding->bedding transitions)
8. Memoire territoriale (AvoidanceMemory, PreferredRoutes)
9. Apprentissage comportemental (AdaptiveBehavior)
10. Activite humaine non-chasse (HumanDisturbance)
11. Disponibilite minerale (MineralAvailability, SaltLickAttraction)
12. Conditions de neige (SnowDepth, CrustRisk, WinterPenalty)

Conformite: G-SEC | G-QA | G-DOC
"""

from typing import Dict, List, Optional
from datetime import datetime, timezone
import logging

from modules.bionic_engine_p0.contracts.data_contracts import (
    Species, ActivityLevel, BehaviorType, SeasonPhase, BehavioralPredictionInput, BehavioralPredictionOutput,
    ActivityPrediction, TimelineEntry, SeasonalContext,
    StrategyRecommendation, WeatherOverride,
    BM_WEIGHTS_CONFIG, score_to_activity_level
)

# Import des 12 facteurs comportementaux avances
from modules.bionic_engine_p0.contracts.advanced_factors import (
    PredatorRiskModel,
    StressModel,
    SocialHierarchyModel,
    InterspeciesCompetitionModel,
    WeakSignalsModel,
    HormonalCycleModel,
    DigestiveCycleModel,
    TerritorialMemoryModel,
    AdaptiveBehaviorModel,
    HumanDisturbanceModel,
    MineralAvailabilityModel,
    SnowConditionModel
)

logger = logging.getLogger("bionic_engine.behavioral_models")


# =============================================================================
# CONSTANTS - Constantes conformes a l'Inventaire v1.2 et Bloc 4
# =============================================================================

# Patterns d'activite horaire detailles (Bloc 4 - Cycles Temporels)
HOURLY_ACTIVITY_PATTERNS = {
    Species.MOOSE: {
        "hourly_scores": {
            0: 15, 1: 12, 2: 10, 3: 8, 4: 10,
            5: 45, 6: 85, 7: 95, 8: 75, 9: 45,
            10: 25, 11: 18, 12: 15, 13: 18, 14: 22,
            15: 35, 16: 55, 17: 85, 18: 92, 19: 70,
            20: 45, 21: 30, 22: 22, 23: 18
        },
        "activity_probabilities": {
            "dawn": {"feeding": 0.65, "traveling": 0.25, "resting": 0.05, "other": 0.05},
            "day": {"feeding": 0.15, "traveling": 0.10, "resting": 0.70, "other": 0.05},
            "dusk": {"feeding": 0.60, "traveling": 0.30, "resting": 0.05, "other": 0.05},
            "night": {"feeding": 0.20, "traveling": 0.15, "resting": 0.60, "other": 0.05}
        }
    },
    Species.DEER: {
        "hourly_scores": {
            0: 25, 1: 20, 2: 18, 3: 15, 4: 18,
            5: 55, 6: 90, 7: 95, 8: 70, 9: 40,
            10: 22, 11: 15, 12: 12, 13: 15, 14: 20,
            15: 35, 16: 60, 17: 88, 18: 95, 19: 75,
            20: 50, 21: 35, 22: 28, 23: 25
        },
        "activity_probabilities": {
            "dawn": {"feeding": 0.70, "traveling": 0.20, "resting": 0.05, "other": 0.05},
            "day": {"feeding": 0.10, "traveling": 0.10, "resting": 0.75, "other": 0.05},
            "dusk": {"feeding": 0.65, "traveling": 0.25, "resting": 0.05, "other": 0.05},
            "night": {"feeding": 0.30, "traveling": 0.20, "resting": 0.45, "other": 0.05}
        }
    },
    Species.BEAR: {
        "hourly_scores": {
            0: 5, 1: 3, 2: 2, 3: 2, 4: 3,
            5: 25, 6: 55, 7: 80, 8: 85, 9: 75,
            10: 60, 11: 45, 12: 35, 13: 40, 14: 50,
            15: 65, 16: 75, 17: 80, 18: 70, 19: 45,
            20: 25, 21: 12, 22: 8, 23: 5
        },
        "activity_probabilities": {
            "dawn": {"feeding": 0.55, "traveling": 0.35, "resting": 0.05, "other": 0.05},
            "day": {"feeding": 0.45, "traveling": 0.30, "resting": 0.20, "other": 0.05},
            "dusk": {"feeding": 0.50, "traveling": 0.35, "resting": 0.10, "other": 0.05},
            "night": {"feeding": 0.10, "traveling": 0.10, "resting": 0.75, "other": 0.05}
        },
        "hibernation_months": [12, 1, 2, 3],
        "hyperphagia_months": [9, 10, 11]
    },
    Species.WILD_TURKEY: {
        "hourly_scores": {
            0: 0, 1: 0, 2: 0, 3: 0, 4: 0,
            5: 15, 6: 75, 7: 95, 8: 85, 9: 70,
            10: 55, 11: 45, 12: 35, 13: 40, 14: 50,
            15: 60, 16: 70, 17: 75, 18: 50, 19: 15,
            20: 0, 21: 0, 22: 0, 23: 0
        },
        "activity_probabilities": {
            "dawn": {"feeding": 0.60, "traveling": 0.30, "resting": 0.05, "other": 0.05},
            "day": {"feeding": 0.50, "traveling": 0.25, "resting": 0.20, "other": 0.05},
            "dusk": {"feeding": 0.70, "traveling": 0.20, "resting": 0.05, "other": 0.05}
        },
        "roosting_hours": [0, 1, 2, 3, 4, 5, 19, 20, 21, 22, 23]
    },
    Species.ELK: {
        "hourly_scores": {
            0: 20, 1: 15, 2: 12, 3: 10, 4: 15,
            5: 50, 6: 85, 7: 90, 8: 70, 9: 45,
            10: 25, 11: 20, 12: 15, 13: 20, 14: 25,
            15: 40, 16: 60, 17: 85, 18: 90, 19: 65,
            20: 40, 21: 30, 22: 25, 23: 22
        },
        "activity_probabilities": {
            "dawn": {"feeding": 0.60, "traveling": 0.30, "resting": 0.05, "other": 0.05},
            "day": {"feeding": 0.15, "traveling": 0.15, "resting": 0.65, "other": 0.05},
            "dusk": {"feeding": 0.55, "traveling": 0.35, "resting": 0.05, "other": 0.05},
            "night": {"feeding": 0.25, "traveling": 0.20, "resting": 0.50, "other": 0.05}
        }
    }
}

# Modificateurs hebdomadaires (Bloc 4)
WEEKLY_MODIFIERS = {
    0: 1.10,  # Lundi
    1: 1.10,  # Mardi
    2: 1.08,  # Mercredi
    3: 1.05,  # Jeudi
    4: 1.00,  # Vendredi
    5: 0.80,  # Samedi
    6: 0.85   # Dimanche
}

# Calendrier annuel par espece (Bloc 4)
ANNUAL_CALENDAR = {
    Species.MOOSE: {
        1: {"season": SeasonPhase.WINTER, "activity_mod": 0.5, "behavior": "survival"},
        2: {"season": SeasonPhase.WINTER, "activity_mod": 0.4, "behavior": "survival"},
        3: {"season": SeasonPhase.WINTER, "activity_mod": 0.5, "behavior": "recovery"},
        4: {"season": SeasonPhase.SPRING, "activity_mod": 0.7, "behavior": "feeding"},
        5: {"season": SeasonPhase.SPRING, "activity_mod": 0.8, "behavior": "feeding"},
        6: {"season": SeasonPhase.SUMMER, "activity_mod": 0.7, "behavior": "feeding_aquatic"},
        7: {"season": SeasonPhase.SUMMER, "activity_mod": 0.6, "behavior": "heat_avoidance"},
        8: {"season": SeasonPhase.SUMMER, "activity_mod": 0.7, "behavior": "pre_rut"},
        9: {"season": SeasonPhase.PRE_RUT, "activity_mod": 0.9, "behavior": "territorial"},
        10: {"season": SeasonPhase.RUT, "activity_mod": 1.0, "behavior": "breeding"},
        11: {"season": SeasonPhase.POST_RUT, "activity_mod": 0.8, "behavior": "recovery_feeding"},
        12: {"season": SeasonPhase.WINTER, "activity_mod": 0.6, "behavior": "yarding"}
    },
    Species.DEER: {
        1: {"season": SeasonPhase.WINTER, "activity_mod": 0.5, "behavior": "yarding"},
        2: {"season": SeasonPhase.WINTER, "activity_mod": 0.5, "behavior": "yarding"},
        3: {"season": SeasonPhase.WINTER, "activity_mod": 0.6, "behavior": "recovery"},
        4: {"season": SeasonPhase.SPRING, "activity_mod": 0.75, "behavior": "feeding"},
        5: {"season": SeasonPhase.SPRING, "activity_mod": 0.8, "behavior": "fawning"},
        6: {"season": SeasonPhase.SUMMER, "activity_mod": 0.7, "behavior": "nurturing"},
        7: {"season": SeasonPhase.SUMMER, "activity_mod": 0.6, "behavior": "heat_avoidance"},
        8: {"season": SeasonPhase.SUMMER, "activity_mod": 0.75, "behavior": "velvet_shed"},
        9: {"season": SeasonPhase.EARLY_FALL, "activity_mod": 0.85, "behavior": "pre_rut"},
        10: {"season": SeasonPhase.PRE_RUT, "activity_mod": 0.95, "behavior": "scraping"},
        11: {"season": SeasonPhase.RUT, "activity_mod": 1.0, "behavior": "breeding"},
        12: {"season": SeasonPhase.POST_RUT, "activity_mod": 0.7, "behavior": "recovery"}
    }
}

# Strategies de chasse par espece et contexte
HUNTING_STRATEGIES = {
    Species.MOOSE: {
        "rut": [
            {"type": "call", "effectiveness": 90, "conditions": "Matin calme, temperature fraiche"},
            {"type": "stalk", "effectiveness": 70, "conditions": "Vent favorable, terrain silencieux"}
        ],
        "general": [
            {"type": "stand", "effectiveness": 75, "conditions": "Pres des corridors, zones d'alimentation"},
            {"type": "stalk", "effectiveness": 60, "conditions": "Zones humides, lisieres"}
        ]
    },
    Species.DEER: {
        "rut": [
            {"type": "rattling", "effectiveness": 85, "conditions": "Pre-rut et rut, males dominants"},
            {"type": "decoy", "effectiveness": 75, "conditions": "Zones ouvertes, bon vent"},
            {"type": "stand", "effectiveness": 80, "conditions": "Pres des scrapes et corridors"}
        ],
        "general": [
            {"type": "stand", "effectiveness": 80, "conditions": "Zones de transition, lisieres"},
            {"type": "ambush", "effectiveness": 70, "conditions": "Corridors identifies"}
        ]
    },
    Species.BEAR: {
        "general": [
            {"type": "stand", "effectiveness": 75, "conditions": "Pres des sources de nourriture"},
            {"type": "stalk", "effectiveness": 65, "conditions": "Terrains ouverts, baies"}
        ]
    },
    Species.WILD_TURKEY: {
        "spring": [
            {"type": "call", "effectiveness": 90, "conditions": "Matin, perchoirs identifies"},
            {"type": "decoy", "effectiveness": 80, "conditions": "Zones ouvertes"}
        ],
        "fall": [
            {"type": "ambush", "effectiveness": 70, "conditions": "Zones d'alimentation"}
        ]
    }
}


# =============================================================================
# SERVICE CLASS
# =============================================================================

class BehavioralModelsService:
    """
    Service de modelisation et prediction comportementale.
    
    Responsabilites:
    - Predire le comportement actuel de l'animal
    - Generer la timeline d'activite 24h
    - Recommander des strategies de chasse
    
    Modeles integres (Bloc 4):
    - Hourly Activity Model
    - Movement Model
    - Feeding Model
    - Resting Model
    
    Conformite:
    - Contrat: behavioral_models_contract.json
    - Cycles: Inventaire v1.2 - Bloc 4
    
    G-SEC: Validation stricte des inputs
    G-QA: Tests unitaires requis
    G-DOC: Documentation complete
    """
    
    def __init__(self):
        self.weights_config = BM_WEIGHTS_CONFIG
        logger.info("BehavioralModelsService initialized")
    
    def execute(self, inputs: Dict) -> Dict:
        """
        Point d'entree principal conforme au contrat.
        
        Args:
            inputs: Dict conforme a BehavioralPredictionInput
            
        Returns:
            Dict conforme a BehavioralPredictionOutput
        """
        try:
            # Parse et validation input (G-SEC)
            parsed_input = BehavioralPredictionInput(**inputs)
            
            # Prediction comportementale
            result = self.predict_behavior(
                species=parsed_input.species,
                datetime_target=parsed_input.datetime_target,
                latitude=parsed_input.latitude,
                longitude=parsed_input.longitude,
                weather_context=parsed_input.weather_context,
                include_strategy=parsed_input.include_strategy
            )
            
            return result.dict()
            
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "CALCULATION_ERROR"
            }
    
    def predict_behavior(
        self,
        species: Species,
        datetime_target: Optional[datetime] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        weather_context: Optional[WeatherOverride] = None,
        include_strategy: bool = True,
        snow_depth_cm: float = 0,
        is_crusted: bool = False,
        include_advanced_factors: bool = True
    ) -> BehavioralPredictionOutput:
        """
        Prediction comportementale complete.
        
        VERSION P0-BETA2: Integration des 12 facteurs comportementaux
        
        Args:
            species: Espece cible
            datetime_target: Date/heure cible
            latitude: Latitude (optionnel)
            longitude: Longitude (optionnel)
            weather_context: Contexte meteo
            include_strategy: Inclure recommandations strategie
            snow_depth_cm: Profondeur de neige (cm)
            is_crusted: Presence de croute de glace
            include_advanced_factors: Inclure les 12 facteurs avances
            
        Returns:
            BehavioralPredictionOutput complet avec 12 facteurs
        """
        # Datetime par defaut
        if datetime_target is None:
            datetime_target = datetime.now(timezone.utc)
        
        warnings = []
        hour = datetime_target.hour
        month = datetime_target.month
        weekday = datetime_target.weekday()
        is_weekend = weekday >= 5
        species_str = species.value
        
        # Latitude par defaut si non fournie
        if latitude is None:
            latitude = 47.5  # Centre Quebec
        
        # Verification hibernation ours
        if species == Species.BEAR:
            patterns = HOURLY_ACTIVITY_PATTERNS.get(species, {})
            if datetime_target.month in patterns.get("hibernation_months", []):
                return BehavioralPredictionOutput(
                    success=True,
                    activity=ActivityPrediction(
                        current_behavior=BehaviorType.RESTING,
                        behavior_confidence=1.0,
                        activity_level=ActivityLevel.MINIMAL,
                        activity_score=0,
                        behavior_probabilities={"resting": 1.0}
                    ),
                    timeline=[],
                    seasonal_context=SeasonalContext(
                        current_season=SeasonPhase.WINTER,
                        activity_modifier=0.0,
                        primary_behaviors=["hibernation"],
                        key_events=["bear_hibernating"]
                    ),
                    strategies=[],
                    warnings=["BEAR_HIBERNATION_PERIOD"],
                    metadata={
                        "species": species.value,
                        "hibernation": True,
                        "advanced_factors_enabled": False,
                        "version": "P0-beta2"
                    }
                )
        
        # Calculer l'activite actuelle
        activity = self._predict_current_activity(species, datetime_target, weather_context)
        
        # Generer timeline 24h
        timeline = self._generate_timeline(species, datetime_target)
        
        # Contexte saisonnier
        seasonal_context = self._get_seasonal_context(species, datetime_target)
        
        # =================================================================
        # P0-BETA2: INTEGRATION DES 12 FACTEURS COMPORTEMENTAUX
        # =================================================================
        advanced_factors = {}
        behavioral_modifiers = {}
        temperature = weather_context.temperature if weather_context and weather_context.temperature else 10
        
        if include_advanced_factors:
            # 1. PREDATION
            predation = PredatorRiskModel.calculate_predation_risk(
                species_str, latitude, hour, month
            )
            advanced_factors["predation"] = predation
            behavioral_modifiers["vigilance_increase"] = predation["risk_score"] / 100
            
            # 2. STRESS THERMIQUE
            thermal_stress = StressModel.calculate_thermal_stress(species_str, temperature)
            advanced_factors["thermal_stress"] = thermal_stress
            behavioral_modifiers["thermal_response"] = thermal_stress["behavioral_response"]
            
            # 3. STRESS HYDRIQUE
            estimated_water_distance = 300 if latitude < 50 else 500
            hydric_stress = StressModel.calculate_hydric_stress(
                species_str, estimated_water_distance, temperature
            )
            advanced_factors["hydric_stress"] = hydric_stress
            behavioral_modifiers["water_seeking"] = hydric_stress["water_seeking"]
            
            # 4. STRESS SOCIAL
            social_stress = StressModel.calculate_social_stress(species_str, month, group_size=3)
            advanced_factors["social_stress"] = social_stress
            
            # 5. HIERARCHIE SOCIALE
            dominance = SocialHierarchyModel.calculate_dominance_context(
                species_str, month, is_male=True
            )
            advanced_factors["social_hierarchy"] = dominance
            behavioral_modifiers["movement_pattern"] = dominance["movement_pattern"]
            
            # 6. COMPETITION INTER-ESPECES
            region_species = ["deer", "bear"] if latitude < 50 else ["moose", "caribou"]
            competition = InterspeciesCompetitionModel.calculate_competition(
                species_str, region_species
            )
            advanced_factors["competition"] = competition
            
            # 7. SIGNAUX FAIBLES
            weak_signals = WeakSignalsModel.detect_anomalies(
                current_score=activity.activity_score,
                historical_avg=65,
                weather_rapid_change=abs(temperature) > 20,
                unusual_activity=False
            )
            advanced_factors["weak_signals"] = weak_signals
            
            # 8. CYCLES HORMONAUX
            hormonal = HormonalCycleModel.get_hormonal_phase(species_str, month)
            advanced_factors["hormonal"] = hormonal
            behavioral_modifiers["hormonal_activity_modifier"] = hormonal["activity_modifier"]
            behavioral_modifiers["behavioral_focus"] = hormonal["behavioral_focus"]
            
            # 9. CYCLES DIGESTIFS
            digestive = DigestiveCycleModel.get_digestive_phase(species_str, hour)
            advanced_factors["digestive"] = digestive
            behavioral_modifiers["digestive_phase"] = digestive["phase"]
            behavioral_modifiers["movement_likelihood"] = digestive["movement_likelihood"]
            
            # 10. MEMOIRE TERRITORIALE
            territorial_memory = TerritorialMemoryModel.calculate_avoidance_factor(
                species_str, days_since_disturbance=7, disturbance_intensity=0.5
            )
            advanced_factors["territorial_memory"] = territorial_memory
            behavioral_modifiers["route_avoidance"] = territorial_memory["preferred_route_shift"]
            
            # 11. APPRENTISSAGE COMPORTEMENTAL
            adaptive = AdaptiveBehaviorModel.calculate_adaptation(
                species_str,
                hunting_pressure_history=[30, 40, 35, 50, 45],
                success_rate_hunters=0.15
            )
            advanced_factors["adaptive_behavior"] = adaptive
            behavioral_modifiers["nocturnal_shift"] = adaptive["nocturnal_shift"]
            behavioral_modifiers["behavioral_shift"] = adaptive["behavioral_shift"]
            
            # 12. ACTIVITE HUMAINE NON-CHASSE
            disturbances = ["hiking"] if is_weekend else []
            human_disturbance = HumanDisturbanceModel.calculate_disturbance(
                disturbances,
                is_weekend=is_weekend,
                is_summer=month in [6, 7, 8]
            )
            advanced_factors["human_disturbance"] = human_disturbance
            behavioral_modifiers["human_avoidance"] = human_disturbance["behavioral_response"]
            
            # 13. DISPONIBILITE MINERALE
            mineral = MineralAvailabilityModel.calculate_mineral_attraction(
                species_str, month, salt_lick_distance_m=800
            )
            advanced_factors["mineral"] = mineral
            behavioral_modifiers["mineral_seeking"] = mineral["seeking_behavior"]
            
            # 14. CONDITIONS DE NEIGE
            snow = SnowConditionModel.calculate_snow_impact(
                species_str, snow_depth_cm, is_crusted, temperature
            )
            advanced_factors["snow"] = snow
            behavioral_modifiers["yarding"] = snow["yarding_likelihood"]
            behavioral_modifiers["energy_expenditure"] = snow["energy_expenditure_increase"]
            
            # =================================================================
            # AJUSTEMENT DU SCORE D'ACTIVITE AVEC LES 12 FACTEURS
            # =================================================================
            adjusted_score = activity.activity_score
            
            # Appliquer les modificateurs
            adjusted_score *= hormonal["activity_modifier"]
            
            # Reduction si conditions difficiles
            if snow["winter_penalty_score"] > 30:
                adjusted_score *= (1 - snow["winter_penalty_score"] / 200)
            
            # Reduction si stress thermique
            if thermal_stress["stress_score"] > 30:
                adjusted_score *= 0.85
            
            # Augmentation si alimentation active et mineraux
            if digestive["phase"] == "active_feeding" and mineral["seeking_behavior"]:
                adjusted_score *= 1.1
            
            # Shift nocturne - reduction diurne
            if adaptive["nocturnal_shift"] > 0.2 and 8 <= hour <= 16:
                adjusted_score *= (1 - adaptive["nocturnal_shift"])
            
            adjusted_score = max(0, min(100, adjusted_score))
            
            # Mettre a jour l'activite avec le score ajuste
            activity = ActivityPrediction(
                current_behavior=activity.current_behavior,
                behavior_confidence=activity.behavior_confidence,
                activity_level=score_to_activity_level(adjusted_score),
                activity_score=round(adjusted_score, 1),
                behavior_probabilities=activity.behavior_probabilities
            )
            
            # Ajouter warnings des facteurs avances
            if predation["risk_score"] > 50:
                warnings.append("HIGH_PREDATION_RISK")
            if thermal_stress["stress_score"] > 40:
                warnings.append(f"THERMAL_STRESS_{thermal_stress['stress_type'].upper()}")
            if snow["winter_penalty_score"] > 50:
                warnings.append("DIFFICULT_SNOW_CONDITIONS")
            if adaptive["behavioral_shift"] == "highly_nocturnal":
                warnings.append("NOCTURNAL_SHIFT_DETECTED")
            if hormonal["phase"] in ["rut_peak", "pre_rut"]:
                warnings.append(f"HORMONAL_PHASE_{hormonal['phase'].upper()}")
        
        # Strategies
        strategies = []
        if include_strategy:
            strategies = self._generate_strategies(species, datetime_target, seasonal_context)
            
            # Ajouter strategies basees sur les facteurs avances
            if include_advanced_factors:
                advanced_strategies = self._generate_advanced_strategies(
                    advanced_factors, species, behavioral_modifiers
                )
                strategies.extend(advanced_strategies)
        
        # Construire metadata avec les 12 facteurs
        metadata = {
            "species": species.value,
            "datetime": datetime_target.isoformat(),
            "latitude": latitude,
            "longitude": longitude,
            "has_location": latitude is not None,
            "has_weather": weather_context is not None,
            "advanced_factors_enabled": include_advanced_factors,
            "version": "P0-beta2"
        }
        
        if include_advanced_factors:
            metadata["advanced_factors"] = advanced_factors
            metadata["behavioral_modifiers"] = behavioral_modifiers
            
            # Identifier les facteurs dominants
            dominant_factors = []
            if predation["risk_score"] > 50:
                dominant_factors.append("high_predation")
            if hormonal["activity_modifier"] > 1.2:
                dominant_factors.append("hormonal_peak")
            if snow["winter_penalty_score"] > 40:
                dominant_factors.append("snow_impact")
            if adaptive["nocturnal_shift"] > 0.25:
                dominant_factors.append("nocturnal_adaptation")
            metadata["dominant_factors"] = dominant_factors if dominant_factors else ["balanced"]
        
        return BehavioralPredictionOutput(
            success=True,
            activity=activity,
            timeline=timeline,
            seasonal_context=seasonal_context,
            strategies=strategies,
            warnings=warnings,
            metadata=metadata
        )
    
    # =========================================================================
    # ACTIVITY PREDICTION
    # =========================================================================
    
    def _predict_current_activity(
        self,
        species: Species,
        datetime_target: datetime,
        weather_context: Optional[WeatherOverride]
    ) -> ActivityPrediction:
        """
        Predit l'activite actuelle de l'animal.
        
        Formule:
        activity = base_hourly * seasonal_mod * weather_mod * weekly_mod
        """
        hour = datetime_target.hour
        month = datetime_target.month
        weekday = datetime_target.weekday()
        
        # Patterns de l'espece
        patterns = HOURLY_ACTIVITY_PATTERNS.get(species, HOURLY_ACTIVITY_PATTERNS[Species.MOOSE])
        
        # Score horaire de base
        hourly_scores = patterns.get("hourly_scores", {})
        base_score = hourly_scores.get(hour, 50)
        
        # Modificateur saisonnier
        calendar = ANNUAL_CALENDAR.get(species, ANNUAL_CALENDAR.get(Species.MOOSE, {}))
        month_data = calendar.get(month, {"activity_mod": 0.7})
        seasonal_mod = month_data.get("activity_mod", 0.7)
        
        # Modificateur hebdomadaire
        weekly_mod = WEEKLY_MODIFIERS.get(weekday, 1.0)
        
        # Modificateur meteo
        weather_mod = 1.0
        if weather_context:
            weather_mod = self._calculate_weather_modifier(weather_context)
        
        # Score final
        activity_score = base_score * seasonal_mod * weekly_mod * weather_mod
        activity_score = min(100, max(0, activity_score))
        
        # Determiner la periode du jour
        period = self._get_day_period(hour)
        
        # Probabilites de comportement
        activity_probs = patterns.get("activity_probabilities", {})
        period_probs = activity_probs.get(period, {"feeding": 0.25, "traveling": 0.25, "resting": 0.45, "other": 0.05})
        
        # Comportement principal
        current_behavior = max(period_probs, key=period_probs.get)
        behavior_type = self._map_to_behavior_type(current_behavior)
        
        # Cas special: dindon qui dort
        if species == Species.WILD_TURKEY:
            roosting_hours = patterns.get("roosting_hours", [])
            if hour in roosting_hours:
                behavior_type = BehaviorType.RESTING
                period_probs = {"resting": 1.0}
                activity_score = 0
        
        return ActivityPrediction(
            current_behavior=behavior_type,
            behavior_confidence=period_probs.get(current_behavior, 0.5),
            activity_level=score_to_activity_level(activity_score),
            activity_score=round(activity_score, 1),
            behavior_probabilities=period_probs
        )
    
    def _calculate_weather_modifier(self, weather: WeatherOverride) -> float:
        """Calcule l'impact de la meteo sur l'activite."""
        modifier = 1.0
        
        if weather.temperature is not None:
            temp = weather.temperature
            if temp < -20 or temp > 30:
                modifier *= 0.5
            elif temp < -10 or temp > 25:
                modifier *= 0.7
            elif -5 <= temp <= 15:
                modifier *= 1.1  # Optimal
        
        if weather.wind_speed is not None:
            wind = weather.wind_speed
            if wind > 40:
                modifier *= 0.6
            elif wind > 25:
                modifier *= 0.8
        
        if weather.precipitation is not None:
            precip = weather.precipitation
            if precip > 5:
                modifier *= 0.7
            elif precip > 2:
                modifier *= 0.85
        
        return modifier
    
    def _get_day_period(self, hour: int) -> str:
        """Determine la periode du jour."""
        if 5 <= hour <= 8:
            return "dawn"
        elif 9 <= hour <= 16:
            return "day"
        elif 17 <= hour <= 20:
            return "dusk"
        else:
            return "night"
    
    def _map_to_behavior_type(self, behavior_str: str) -> BehaviorType:
        """Mappe une string vers BehaviorType."""
        mapping = {
            "feeding": BehaviorType.FEEDING,
            "traveling": BehaviorType.TRAVELING,
            "resting": BehaviorType.RESTING,
            "rutting": BehaviorType.RUTTING,
            "bedding": BehaviorType.BEDDING,
            "watering": BehaviorType.WATERING
        }
        return mapping.get(behavior_str, BehaviorType.UNKNOWN)
    
    # =========================================================================
    # TIMELINE GENERATION
    # =========================================================================
    
    def _generate_timeline(
        self,
        species: Species,
        datetime_target: datetime
    ) -> List[TimelineEntry]:
        """
        Genere la timeline d'activite sur 24h.
        
        Conforme au contrat: 24 entrees, une par heure
        """
        timeline = []
        patterns = HOURLY_ACTIVITY_PATTERNS.get(species, HOURLY_ACTIVITY_PATTERNS[Species.MOOSE])
        hourly_scores = patterns.get("hourly_scores", {})
        activity_probs = patterns.get("activity_probabilities", {})
        
        # Heures legales de chasse (approximation)
        legal_start = 6  # 30 min avant lever soleil
        legal_end = 18   # 30 min apres coucher soleil
        
        for hour in range(24):
            score = hourly_scores.get(hour, 50)
            period = self._get_day_period(hour)
            probs = activity_probs.get(period, {"resting": 1.0})
            
            # Comportement principal
            primary = max(probs, key=probs.get)
            behavior_type = self._map_to_behavior_type(primary)
            
            # Cas special dindon
            if species == Species.WILD_TURKEY:
                roosting = patterns.get("roosting_hours", [])
                if hour in roosting:
                    behavior_type = BehaviorType.RESTING
                    score = 0
            
            timeline.append(TimelineEntry(
                hour=hour,
                activity_score=round(score, 1),
                primary_behavior=behavior_type,
                probability=probs.get(primary, 0.5),
                is_legal_hunting=legal_start <= hour <= legal_end
            ))
        
        return timeline
    
    # =========================================================================
    # SEASONAL CONTEXT
    # =========================================================================
    
    def _get_seasonal_context(
        self,
        species: Species,
        datetime_target: datetime
    ) -> SeasonalContext:
        """
        Retourne le contexte saisonnier pour l'espece.
        """
        month = datetime_target.month
        calendar = ANNUAL_CALENDAR.get(species, ANNUAL_CALENDAR.get(Species.MOOSE, {}))
        month_data = calendar.get(month, {
            "season": SeasonPhase.SUMMER,
            "activity_mod": 0.7,
            "behavior": "general"
        })
        
        # Comportements principaux selon la saison
        primary_behaviors = [month_data.get("behavior", "general")]
        
        # Evenements cles
        key_events = []
        season = month_data.get("season", SeasonPhase.SUMMER)
        
        if season == SeasonPhase.RUT:
            key_events.append("rut_active")
            primary_behaviors.extend(["breeding", "territorial"])
        elif season == SeasonPhase.PRE_RUT:
            key_events.append("pre_rut_preparation")
            primary_behaviors.append("increasing_activity")
        elif season == SeasonPhase.WINTER:
            key_events.append("winter_survival")
            primary_behaviors.append("energy_conservation")
        
        # Hyperphagie ours
        if species == Species.BEAR and month in [9, 10, 11]:
            key_events.append("hyperphagia")
            primary_behaviors.append("intensive_feeding")
        
        return SeasonalContext(
            current_season=season,
            activity_modifier=month_data.get("activity_mod", 0.7),
            primary_behaviors=list(set(primary_behaviors)),
            key_events=key_events
        )
    
    # =========================================================================
    # STRATEGY RECOMMENDATIONS
    # =========================================================================
    
    def _generate_strategies(
        self,
        species: Species,
        datetime_target: datetime,
        seasonal_context: SeasonalContext
    ) -> List[StrategyRecommendation]:
        """
        Genere les recommandations de strategies de chasse.
        """
        strategies = []
        species_strategies = HUNTING_STRATEGIES.get(species, {})
        
        # Determiner le contexte
        context = "general"
        if seasonal_context.current_season in [SeasonPhase.RUT, SeasonPhase.PRE_RUT]:
            context = "rut"
        elif species == Species.WILD_TURKEY:
            if datetime_target.month in [4, 5]:
                context = "spring"
            else:
                context = "fall"
        
        # Strategies pour ce contexte
        context_strategies = species_strategies.get(context, species_strategies.get("general", []))
        
        for strat in context_strategies:
            tips_fr = []
            
            if strat["type"] == "call":
                tips_fr = [
                    "Utilisez des appels authentiques et varies",
                    "Attendez 15-20 minutes entre les sequences",
                    "Commencez doucement et augmentez l'intensite"
                ]
            elif strat["type"] == "stand":
                tips_fr = [
                    "Arrivez sur place 30 minutes avant l'aube",
                    "Minimisez les mouvements",
                    "Surveillez les zones de transition"
                ]
            elif strat["type"] == "stalk":
                tips_fr = [
                    "Deplacez-vous lentement, 2-3 pas puis stop",
                    "Utilisez le vent a votre avantage",
                    "Evitez de faire craquer les branches"
                ]
            elif strat["type"] == "rattling":
                tips_fr = [
                    "Plus efficace en pre-rut et debut de rut",
                    "Commencez par un cliquetis leger",
                    "Ajoutez des grattages au sol pour plus de realisme"
                ]
            elif strat["type"] == "decoy":
                tips_fr = [
                    "Placez le decoy visible mais pas trop proche",
                    "Assurez-vous que le vent porte vers votre position",
                    "Combinez avec des appels pour plus d'efficacite"
                ]
            elif strat["type"] == "ambush":
                tips_fr = [
                    "Identifiez les corridors de deplacement",
                    "Preparez plusieurs positions de repli",
                    "Restez immobile et patient"
                ]
            
            strategies.append(StrategyRecommendation(
                strategy_type=strat["type"],
                effectiveness_score=strat["effectiveness"],
                best_conditions=strat["conditions"],
                tips_fr=tips_fr
            ))
        
        # Trier par efficacite
        strategies.sort(key=lambda x: x.effectiveness_score, reverse=True)
        
        return strategies
    
    # =========================================================================
    # SPECIALIZED METHODS
    # =========================================================================
    
    def get_activity_timeline(
        self,
        species: Species,
        date: datetime
    ) -> List[TimelineEntry]:
        """
        Retourne uniquement la timeline (endpoint simplifie).
        """
        return self._generate_timeline(species, date)
    
    def predict_activity(
        self,
        species: Species,
        datetime_target: datetime,
        weather_context: Optional[WeatherOverride] = None
    ) -> ActivityPrediction:
        """
        Retourne uniquement la prediction d'activite (endpoint simplifie).
        """
        return self._predict_current_activity(species, datetime_target, weather_context)

    # =========================================================================
    # P0-BETA2: ADVANCED FACTOR STRATEGIES
    # =========================================================================
    
    def _generate_advanced_strategies(
        self,
        advanced_factors: Dict,
        species: Species,
        behavioral_modifiers: Dict
    ) -> List[StrategyRecommendation]:
        """
        Genere des strategies basees sur les 12 facteurs comportementaux.
        
        P0-BETA2: Integration des facteurs avances dans les recommandations
        
        G-DOC: Chaque strategie est justifiee par un facteur specifique
        """
        strategies = []
        
        # Strategie PREDATION
        predation = advanced_factors.get("predation", {})
        if predation.get("risk_score", 0) > 40:
            strategies.append(StrategyRecommendation(
                strategy_type="predator_aware",
                effectiveness_score=75,
                best_conditions=f"Zone a risque de predation ({predation.get('dominant_predator', 'wolf')})",
                tips_fr=[
                    "Positionnez-vous pres des zones de couvert dense",
                    "Les animaux seront plus vigilants et groups",
                    "Utilisez le terrain pour bloquer les lignes de vue des predateurs"
                ]
            ))
        
        # Strategie STRESS THERMIQUE
        thermal = advanced_factors.get("thermal_stress", {})
        if thermal.get("stress_type") == "heat":
            strategies.append(StrategyRecommendation(
                strategy_type="thermal_comfort",
                effectiveness_score=80,
                best_conditions="Chaleur - animaux cherchant fraicheur",
                tips_fr=[
                    "Surveillez les points d'eau et zones ombragees",
                    "Les animaux seront moins actifs en milieu de journee",
                    "Privilegiez l'aube et le crepuscule"
                ]
            ))
        elif thermal.get("stress_type") == "cold":
            strategies.append(StrategyRecommendation(
                strategy_type="cold_weather",
                effectiveness_score=70,
                best_conditions="Froid intense - animaux cherchant abri",
                tips_fr=[
                    "Surveillez les ravages et zones de coniferes",
                    "Les animaux s'alimentent plus intensement",
                    "Reduisez vos deplacements - le froid porte les sons"
                ]
            ))
        
        # Strategie CYCLES HORMONAUX
        hormonal = advanced_factors.get("hormonal", {})
        if hormonal.get("phase") == "rut_peak":
            strategies.append(StrategyRecommendation(
                strategy_type="rut_peak_strategy",
                effectiveness_score=95,
                best_conditions="PIC DU RUT - Activite maximale",
                tips_fr=[
                    "Utilisez les appels de femelles et de defi",
                    "Le rattling est extremement efficace",
                    "Les males negligent leur securite - profitez-en",
                    "Surveillez les zones ouvertes pour les confrontations"
                ]
            ))
        elif hormonal.get("phase") == "antler_growth":
            strategies.append(StrategyRecommendation(
                strategy_type="mineral_focus",
                effectiveness_score=70,
                best_conditions="Croissance des bois - recherche de mineraux",
                tips_fr=[
                    "Installez-vous pres des salines naturelles",
                    "Les males visitent regulierement ces sites",
                    "Horaire optimal: tot le matin"
                ]
            ))
        
        # Strategie CYCLES DIGESTIFS
        digestive = advanced_factors.get("digestive", {})
        if digestive.get("phase") == "active_feeding":
            strategies.append(StrategyRecommendation(
                strategy_type="feeding_pattern",
                effectiveness_score=85,
                best_conditions="Phase d'alimentation active",
                tips_fr=[
                    "Identifiez les sources de nourriture preferees",
                    "Les animaux sont en deplacement - soyez pret",
                    "Bons moments: 6-8h et 17-19h"
                ]
            ))
        elif digestive.get("phase") == "transitioning":
            strategies.append(StrategyRecommendation(
                strategy_type="transition_ambush",
                effectiveness_score=80,
                best_conditions="Transition alimentation/repos",
                tips_fr=[
                    "Postez-vous sur les corridors de deplacement",
                    "Les animaux suivent des routes previsibles",
                    "Moment ideal pour l'embuscade"
                ]
            ))
        
        # Strategie APPRENTISSAGE COMPORTEMENTAL
        adaptive = advanced_factors.get("adaptive_behavior", {})
        if adaptive.get("behavioral_shift") == "highly_nocturnal":
            strategies.append(StrategyRecommendation(
                strategy_type="nocturnal_adapted",
                effectiveness_score=75,
                best_conditions="Animaux tres prudents avec shift nocturne",
                tips_fr=[
                    "Concentrez-vous sur les 30 premieres minutes apres l'aube",
                    "Les dernieres minutes de lumiere sont critiques",
                    "Evitez les zones a forte pression de chasse",
                    "Patience maximale requise"
                ]
            ))
        
        # Strategie CONDITIONS DE NEIGE
        snow = advanced_factors.get("snow", {})
        if snow.get("yarding_likelihood"):
            strategies.append(StrategyRecommendation(
                strategy_type="yarding_strategy",
                effectiveness_score=90,
                best_conditions="Neige profonde - animaux en ravage",
                tips_fr=[
                    "Localisez les ravages (cedres/sapins denses)",
                    "Les animaux sont concentres - approche discrete",
                    "Utilisez les raquettes ou skis pour acceder",
                    "Ethique: evitez de stresser les groupes en survie"
                ]
            ))
        elif snow.get("snow_condition") == "crusted":
            strategies.append(StrategyRecommendation(
                strategy_type="crusted_snow",
                effectiveness_score=80,
                best_conditions="Croute de neige - mobilite reduite",
                tips_fr=[
                    "La croute ralentit le gibier plus que vous",
                    "Approche plus silencieuse possible",
                    "Les animaux restent sur les pistes battues"
                ]
            ))
        
        # Strategie DISPONIBILITE MINERALE
        mineral = advanced_factors.get("mineral", {})
        if mineral.get("seeking_behavior"):
            strategies.append(StrategyRecommendation(
                strategy_type="mineral_site",
                effectiveness_score=75,
                best_conditions="Forte attraction vers les mineraux",
                tips_fr=[
                    "Identifiez les salines naturelles ou artificielles",
                    f"Meilleur moment: {mineral.get('optimal_monitoring_time', 'matin')}",
                    "Camera de trail recommandee pour reperage"
                ]
            ))
        
        # Strategie MEMOIRE TERRITORIALE
        memory = advanced_factors.get("territorial_memory", {})
        if memory.get("memory_active") and memory.get("avoidance_score", 0) > 40:
            strategies.append(StrategyRecommendation(
                strategy_type="avoidance_aware",
                effectiveness_score=65,
                best_conditions="Zone avec evitement actif",
                tips_fr=[
                    "Cette zone a ete perturbee recemment",
                    "Explorez les zones alternatives moins frequentees",
                    f"Retour normal estime dans {memory.get('days_until_return', 7)} jours"
                ]
            ))
        
        # Trier par efficacite
        strategies.sort(key=lambda x: x.effectiveness_score, reverse=True)
        
        return strategies

