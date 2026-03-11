"""
BIONIC ENGINE - Predictive Territorial Module
PHASE G - P0-BETA2 IMPLEMENTATION
Version: 1.0.0-beta2

Module de calcul de score territorial predictif.
Strictement conforme au contrat: predictive_territorial_contract.json

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

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
import logging

from modules.bionic_engine_p0.contracts.data_contracts import (
    Species, ScoreRating, TerritorialScoreInput, TerritorialScoreOutput,
    ScoreComponents, Recommendation, WeatherOverride,
    PT_WEIGHTS_CONFIG, score_to_rating
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

logger = logging.getLogger("bionic_engine.predictive_territorial")


# =============================================================================
# EXTENDED OUTPUT MODEL - Score avec 12 facteurs
# =============================================================================

class ExtendedScoreComponents(ScoreComponents):
    """Composantes etendues avec les 12 facteurs comportementaux"""
    # Facteurs comportementaux avances (12 facteurs)
    predation_factor: float = 0.0
    thermal_stress_factor: float = 0.0
    hydric_stress_factor: float = 0.0
    social_stress_factor: float = 0.0
    competition_factor: float = 0.0
    weak_signals_factor: float = 0.0
    hormonal_factor: float = 0.0
    digestive_factor: float = 0.0
    territorial_memory_factor: float = 0.0
    adaptive_behavior_factor: float = 0.0
    human_disturbance_factor: float = 0.0
    mineral_availability_factor: float = 0.0
    snow_conditions_factor: float = 0.0


# =============================================================================
# CONSTANTS - Constantes conformes a l'Inventaire v1.2
# =============================================================================

# Patterns d'activite horaire par espece (F12 - Cycles Temporels)
HOURLY_ACTIVITY_PATTERNS = {
    Species.MOOSE: {
        0: 15, 1: 12, 2: 10, 3: 8, 4: 10,
        5: 45, 6: 85, 7: 95, 8: 75, 9: 45,
        10: 25, 11: 18, 12: 15, 13: 18, 14: 22,
        15: 35, 16: 55, 17: 85, 18: 92, 19: 70,
        20: 45, 21: 30, 22: 22, 23: 18
    },
    Species.DEER: {
        0: 25, 1: 20, 2: 18, 3: 15, 4: 18,
        5: 55, 6: 90, 7: 95, 8: 70, 9: 40,
        10: 22, 11: 15, 12: 12, 13: 15, 14: 20,
        15: 35, 16: 60, 17: 88, 18: 95, 19: 75,
        20: 50, 21: 35, 22: 28, 23: 25
    },
    Species.BEAR: {
        0: 5, 1: 3, 2: 2, 3: 2, 4: 3,
        5: 25, 6: 55, 7: 80, 8: 85, 9: 75,
        10: 60, 11: 45, 12: 35, 13: 40, 14: 50,
        15: 65, 16: 75, 17: 80, 18: 70, 19: 45,
        20: 25, 21: 12, 22: 8, 23: 5
    },
    Species.WILD_TURKEY: {
        0: 0, 1: 0, 2: 0, 3: 0, 4: 0,
        5: 15, 6: 75, 7: 95, 8: 85, 9: 70,
        10: 55, 11: 45, 12: 35, 13: 40, 14: 50,
        15: 60, 16: 70, 17: 75, 18: 50, 19: 15,
        20: 0, 21: 0, 22: 0, 23: 0
    },
    Species.ELK: {
        0: 20, 1: 15, 2: 12, 3: 10, 4: 15,
        5: 50, 6: 85, 7: 90, 8: 70, 9: 45,
        10: 25, 11: 20, 12: 15, 13: 20, 14: 25,
        15: 40, 16: 60, 17: 85, 18: 90, 19: 65,
        20: 40, 21: 30, 22: 25, 23: 22
    }
}

# Facteurs saisonniers (F12 - Cycles)
SEASON_FACTORS = {
    1: 0.5,   # Janvier
    2: 0.45,  # Fevrier
    3: 0.55,  # Mars
    4: 0.7,   # Avril
    5: 0.75,  # Mai
    6: 0.7,   # Juin
    7: 0.6,   # Juillet
    8: 0.75,  # Aout
    9: 0.9,   # Septembre
    10: 1.0,  # Octobre (pic)
    11: 0.95, # Novembre
    12: 0.55  # Decembre
}

# Modificateurs hebdomadaires (Bloc 4 - Cycles Temporels)
WEEKLY_MODIFIERS = {
    0: 1.10,  # Lundi
    1: 1.10,  # Mardi
    2: 1.08,  # Mercredi
    3: 1.05,  # Jeudi
    4: 1.00,  # Vendredi
    5: 0.80,  # Samedi
    6: 0.85   # Dimanche
}

# Periodes de rut par espece
RUT_PERIODS = {
    Species.MOOSE: {"start_month": 9, "peak_month": 10, "end_month": 10},
    Species.DEER: {"start_month": 10, "peak_month": 11, "end_month": 11},
    Species.ELK: {"start_month": 9, "peak_month": 9, "end_month": 10}
}

# Mois d'hibernation ours
BEAR_HIBERNATION_MONTHS = [12, 1, 2, 3]

# Conditions meteo optimales
OPTIMAL_WEATHER = {
    "temperature": {"min": -5, "max": 15, "ideal": 5},
    "wind_speed": {"min": 0, "max": 20, "ideal": 8},
    "pressure": {"min": 1000, "max": 1030, "ideal": 1015}
}


# =============================================================================
# SERVICE CLASS
# =============================================================================

class PredictiveTerritorialService:
    """
    Service de calcul de score territorial predictif.
    
    Responsabilites:
    - Calculer un score de probabilite de presence faunique
    - Appliquer les ponderations dynamiques
    - Generer des recommandations
    
    Conformite:
    - Contrat: predictive_territorial_contract.json
    - Hierarchie: Inventaire v1.2 - Normalisation des ponderations
    - Arbitrage: 6 regles documentees
    
    G-SEC: Validation stricte des inputs
    G-QA: Tests unitaires requis
    G-DOC: Documentation complete
    """
    
    def __init__(self):
        self.weights_config = PT_WEIGHTS_CONFIG
        self._available_sources = [
            "habitat_quality",
            "weather_conditions", 
            "temporal_alignment",
            "pressure_index",
            "microclimate",
            "historical_baseline"
        ]
        logger.info("PredictiveTerritorialService initialized")
    
    def execute(self, inputs: Dict) -> Dict:
        """
        Point d'entree principal conforme au contrat.
        
        Args:
            inputs: Dict conforme a TerritorialScoreInput
            
        Returns:
            Dict conforme a TerritorialScoreOutput
        """
        try:
            # Parse et validation input (G-SEC)
            parsed_input = TerritorialScoreInput(**inputs)
            
            # Calcul du score
            result = self.calculate_score(
                latitude=parsed_input.latitude,
                longitude=parsed_input.longitude,
                species=parsed_input.species,
                datetime_target=parsed_input.datetime_target,
                radius_km=parsed_input.radius_km,
                weather_override=parsed_input.weather_override,
                include_recommendations=parsed_input.include_recommendations
            )
            
            return result.dict()
            
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "CALCULATION_ERROR"
            }
    
    def calculate_score(
        self,
        latitude: float,
        longitude: float,
        species: Species,
        datetime_target: Optional[datetime] = None,
        radius_km: float = 5.0,
        weather_override: Optional[WeatherOverride] = None,
        include_recommendations: bool = True,
        snow_depth_cm: float = 0,
        is_crusted: bool = False,
        include_advanced_factors: bool = True
    ) -> TerritorialScoreOutput:
        """
        Calcule le score territorial pour une position.
        
        VERSION P0-BETA2: Integration des 12 facteurs comportementaux
        
        Formule:
        Score = sum(component_score * weight) pour tous les composants
        Avec ajustements arbitrage selon hierarchie
        + Integration des 12 facteurs comportementaux avances
        
        Args:
            latitude: Latitude WGS84
            longitude: Longitude WGS84
            species: Espece cible
            datetime_target: Date/heure cible
            radius_km: Rayon d'analyse
            weather_override: Donnees meteo manuelles
            include_recommendations: Inclure recommandations
            snow_depth_cm: Profondeur de neige (cm)
            is_crusted: Presence de croute de glace
            include_advanced_factors: Inclure les 12 facteurs avances
            
        Returns:
            TerritorialScoreOutput complet avec 12 facteurs
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
        
        # Verification hibernation ours (Niveau 1 - CRITIQUE)
        if species == Species.BEAR and datetime_target.month in BEAR_HIBERNATION_MONTHS:
            return TerritorialScoreOutput(
                success=True,
                overall_score=0,
                confidence=1.0,
                rating=ScoreRating.POOR,
                components=ScoreComponents(
                    habitat_score=0,
                    weather_score=0,
                    temporal_score=0,
                    pressure_score=0,
                    microclimate_score=0,
                    historical_score=0
                ),
                recommendations=[
                    Recommendation(
                        type="timing",
                        priority="critical",
                        message_fr="L'ours est en hibernation durant cette periode. Score = 0.",
                        message_en="Bear is hibernating during this period. Score = 0."
                    )
                ],
                warnings=["BEAR_HIBERNATION_PERIOD"],
                metadata={
                    "species": species.value,
                    "hibernation": True,
                    "datetime": datetime_target.isoformat(),
                    "advanced_factors_enabled": False
                }
            )
        
        # Calculer chaque composante de base
        habitat_score = self._calculate_habitat_score(latitude, longitude, species)
        weather_score, weather_data = self._calculate_weather_score(
            latitude, longitude, weather_override
        )
        temporal_score = self._calculate_temporal_score(species, datetime_target)
        pressure_score = self._calculate_pressure_score(latitude, longitude, datetime_target)
        microclimate_score = self._calculate_microclimate_score(
            latitude, longitude, weather_data, datetime_target
        )
        historical_score = self._calculate_historical_score(latitude, longitude, species)
        
        # Detection conditions extremes (Niveau 1 - CRITIQUE)
        is_extreme, extreme_type = self._detect_extreme_conditions(weather_data)
        
        # Detection periode rut
        is_rut = self._is_rut_period(species, datetime_target)
        
        # Detection haute pression
        is_high_pressure = pressure_score < 30  # IPC inverse
        
        # =================================================================
        # P0-BETA2: INTEGRATION DES 12 FACTEURS COMPORTEMENTAUX
        # =================================================================
        advanced_factors = {}
        advanced_factor_scores = {}
        temperature = weather_data.get("temperature", 10)
        
        if include_advanced_factors:
            # 1. PREDATION (PredatorRisk, PredatorCorridors)
            predation_result = PredatorRiskModel.calculate_predation_risk(
                species_str, latitude, hour, month
            )
            advanced_factors["predation"] = predation_result
            advanced_factor_scores["predation"] = predation_result["risk_score"]
            
            # 2. STRESS THERMIQUE
            thermal_stress = StressModel.calculate_thermal_stress(species_str, temperature)
            advanced_factors["thermal_stress"] = thermal_stress
            advanced_factor_scores["thermal_stress"] = thermal_stress["stress_score"]
            
            # 3. STRESS HYDRIQUE
            estimated_water_distance = 300 if latitude < 50 else 500
            hydric_stress = StressModel.calculate_hydric_stress(
                species_str, estimated_water_distance, temperature
            )
            advanced_factors["hydric_stress"] = hydric_stress
            advanced_factor_scores["hydric_stress"] = hydric_stress["stress_score"]
            
            # 4. STRESS SOCIAL
            social_stress = StressModel.calculate_social_stress(species_str, month, group_size=3)
            advanced_factors["social_stress"] = social_stress
            advanced_factor_scores["social_stress"] = social_stress["stress_score"]
            
            # 5. HIERARCHIE SOCIALE
            dominance = SocialHierarchyModel.calculate_dominance_context(
                species_str, month, is_male=True
            )
            advanced_factors["social_hierarchy"] = dominance
            advanced_factor_scores["social_hierarchy"] = dominance["dominance_score"]
            
            # 6. COMPETITION INTER-ESPECES
            region_species = ["deer", "bear"] if latitude < 50 else ["moose", "caribou"]
            competition = InterspeciesCompetitionModel.calculate_competition(
                species_str, region_species
            )
            advanced_factors["competition"] = competition
            advanced_factor_scores["competition"] = competition["total_competition_score"]
            
            # 7. SIGNAUX FAIBLES
            weak_signals = WeakSignalsModel.detect_anomalies(
                current_score=70,
                historical_avg=65,
                weather_rapid_change=abs(temperature) > 20,
                unusual_activity=False
            )
            advanced_factors["weak_signals"] = weak_signals
            advanced_factor_scores["weak_signals"] = weak_signals["anomaly_score"]
            
            # 8. CYCLES HORMONAUX
            hormonal = HormonalCycleModel.get_hormonal_phase(species_str, month)
            advanced_factors["hormonal"] = hormonal
            # Convertir activity_modifier en score (1.5 = 50 bonus, 0.5 = -50)
            hormonal_score = (hormonal["activity_modifier"] - 1.0) * 100 + 50
            advanced_factor_scores["hormonal"] = max(0, min(100, hormonal_score))
            
            # 9. CYCLES DIGESTIFS
            digestive = DigestiveCycleModel.get_digestive_phase(species_str, hour)
            advanced_factors["digestive"] = digestive
            # Score base sur probabilite d'alimentation
            advanced_factor_scores["digestive"] = digestive["feeding_probability"] * 100
            
            # 10. MEMOIRE TERRITORIALE
            territorial_memory = TerritorialMemoryModel.calculate_avoidance_factor(
                species_str, days_since_disturbance=7, disturbance_intensity=0.5
            )
            advanced_factors["territorial_memory"] = territorial_memory
            # Score inverse (evitement = mauvais)
            advanced_factor_scores["territorial_memory"] = 100 - territorial_memory["avoidance_score"]
            
            # 11. APPRENTISSAGE COMPORTEMENTAL
            adaptive = AdaptiveBehaviorModel.calculate_adaptation(
                species_str,
                hunting_pressure_history=[30, 40, 35, 50, 45],
                success_rate_hunters=0.15
            )
            advanced_factors["adaptive_behavior"] = adaptive
            # Score inverse (adaptation = animal plus difficile)
            advanced_factor_scores["adaptive_behavior"] = 100 - adaptive["adaptation_level"]
            
            # 12. ACTIVITE HUMAINE NON-CHASSE
            disturbances = ["hiking"] if is_weekend else []
            human_disturbance = HumanDisturbanceModel.calculate_disturbance(
                disturbances,
                is_weekend=is_weekend,
                is_summer=month in [6, 7, 8]
            )
            advanced_factors["human_disturbance"] = human_disturbance
            # Score inverse (perturbation = mauvais)
            advanced_factor_scores["human_disturbance"] = 100 - human_disturbance["disturbance_score"]
            
            # 13. DISPONIBILITE MINERALE
            mineral = MineralAvailabilityModel.calculate_mineral_attraction(
                species_str, month, salt_lick_distance_m=800
            )
            advanced_factors["mineral"] = mineral
            advanced_factor_scores["mineral"] = mineral["salt_lick_attraction"]
            
            # 14. CONDITIONS DE NEIGE
            snow = SnowConditionModel.calculate_snow_impact(
                species_str, snow_depth_cm, is_crusted, temperature
            )
            advanced_factors["snow"] = snow
            # Score inverse (penalite = mauvais)
            advanced_factor_scores["snow"] = 100 - snow["winter_penalty_score"]
            
            # Ajouter warnings des facteurs avances
            if predation_result["risk_score"] > 50:
                warnings.append("HIGH_PREDATION_RISK")
            if thermal_stress["stress_score"] > 40:
                warnings.append(f"THERMAL_STRESS_{thermal_stress['stress_type'].upper()}")
            if snow["winter_penalty_score"] > 50:
                warnings.append("DIFFICULT_SNOW_CONDITIONS")
            if human_disturbance["disturbance_score"] > 40:
                warnings.append("HUMAN_DISTURBANCE_DETECTED")
            if hormonal["phase"] in ["rut_peak", "pre_rut"]:
                warnings.append(f"HORMONAL_PHASE_{hormonal['phase'].upper()}")
        
        # Obtenir poids dynamiques selon contexte
        weights = self._get_dynamic_weights(
            is_extreme=is_extreme,
            is_rut=is_rut,
            is_high_pressure=is_high_pressure
        )
        
        # Calcul score pondere de base
        component_scores = {
            "habitat_quality": habitat_score,
            "weather_conditions": weather_score,
            "temporal_alignment": temporal_score,
            "pressure_index": pressure_score,
            "microclimate": microclimate_score,
            "historical_baseline": historical_score
        }
        
        base_score = sum(
            score * weights.get(key, 0)
            for key, score in component_scores.items()
        )
        
        # =================================================================
        # INTEGRATION AVANCEE: Appliquer les modificateurs des 12 facteurs
        # =================================================================
        overall_score = base_score
        
        if include_advanced_factors and advanced_factor_scores:
            # Poids des 12 facteurs (total = 0.20 du score final)
            ADVANCED_WEIGHTS = {
                "predation": 0.020,
                "thermal_stress": 0.015,
                "hydric_stress": 0.010,
                "social_stress": 0.010,
                "social_hierarchy": 0.015,
                "competition": 0.010,
                "weak_signals": 0.010,
                "hormonal": 0.025,
                "digestive": 0.015,
                "territorial_memory": 0.015,
                "adaptive_behavior": 0.020,
                "human_disturbance": 0.015,
                "mineral": 0.010,
                "snow": 0.020
            }
            
            # Le score de base represente 80% du total
            overall_score = base_score * 0.80
            
            # Les facteurs avances representent 20%
            for factor_name, factor_score in advanced_factor_scores.items():
                weight = ADVANCED_WEIGHTS.get(factor_name, 0.01)
                overall_score += factor_score * weight * 100
        
        # Borner le score
        overall_score = max(0, min(100, overall_score))
        
        # Calculer confiance
        confidence = self._calculate_confidence(
            weather_override is None,
            is_extreme
        )
        
        # Ajuster confiance si signaux faibles detectes
        if include_advanced_factors and advanced_factors.get("weak_signals", {}).get("confidence_adjustment"):
            confidence += advanced_factors["weak_signals"]["confidence_adjustment"]
            confidence = max(0.5, min(1.0, confidence))
        
        # Rating
        rating = score_to_rating(overall_score)
        
        # Avertissements
        if is_extreme:
            warnings.append(f"EXTREME_CONDITIONS_{extreme_type.upper()}")
        if is_high_pressure:
            warnings.append("HIGH_HUNTING_PRESSURE")
        if is_rut:
            warnings.append("RUT_PERIOD_ACTIVE")
        
        # Recommandations
        recommendations = []
        if include_recommendations:
            recommendations = self._generate_recommendations(
                overall_score=overall_score,
                species=species,
                datetime_target=datetime_target,
                is_extreme=is_extreme,
                is_rut=is_rut,
                is_high_pressure=is_high_pressure,
                weather_data=weather_data
            )
        
        # Construire output avec les 12 facteurs avances
        metadata = {
            "species": species.value,
            "datetime": datetime_target.isoformat(),
            "latitude": latitude,
            "longitude": longitude,
            "weights_applied": weights,
            "is_rut": is_rut,
            "is_extreme": is_extreme,
            "data_sources_used": self._available_sources,
            "advanced_factors_enabled": include_advanced_factors,
            "version": "P0-beta2"
        }
        
        # Ajouter les donnees des 12 facteurs si actives
        if include_advanced_factors and advanced_factors:
            metadata["advanced_factors"] = advanced_factors
            metadata["advanced_factor_scores"] = advanced_factor_scores
            
            # Identifier les facteurs dominants
            dominant_factors = []
            for factor_name, score in advanced_factor_scores.items():
                if factor_name in ["predation", "thermal_stress", "snow"] and score > 50:
                    dominant_factors.append(f"{factor_name}_impact")
                elif factor_name == "hormonal" and score > 70:
                    dominant_factors.append("hormonal_peak")
            metadata["dominant_factors"] = dominant_factors if dominant_factors else ["balanced"]
            
            # Recommandations basees sur les facteurs avances
            if include_recommendations:
                advanced_recs = self._generate_advanced_recommendations(advanced_factors, species)
                recommendations.extend(advanced_recs)
        
        return TerritorialScoreOutput(
            success=True,
            overall_score=round(overall_score, 1),
            confidence=round(confidence, 2),
            rating=rating,
            components=ScoreComponents(
                habitat_score=round(habitat_score, 1),
                weather_score=round(weather_score, 1),
                temporal_score=round(temporal_score, 1),
                pressure_score=round(pressure_score, 1),
                microclimate_score=round(microclimate_score, 1),
                historical_score=round(historical_score, 1)
            ),
            recommendations=recommendations,
            warnings=warnings,
            metadata=metadata
        )
    
    # =========================================================================
    # COMPONENT CALCULATORS
    # =========================================================================
    
    def _calculate_habitat_score(
        self, 
        latitude: float, 
        longitude: float, 
        species: Species
    ) -> float:
        """
        Calcule le score d'habitat (F2 - Vegetation).
        
        Utilise les variables d'habitat de l'inventaire:
        - NDVI, canopy_cover, edge_density, water_proximity
        
        NOTE: Version P0 - Simulation basee sur position
        P1 integrera donnees Sentinel-2 et LiDAR
        """
        # Simulation basee sur la position (P0)
        # Zones connues favorables au Quebec
        
        # Facteur latitude (nord = plus sauvage)
        lat_factor = min(1.0, (latitude - 45) / 15 * 0.8 + 0.5)
        
        # Facteur longitude (centre = plus forestier)
        lng_center = -70.0
        lng_factor = 1.0 - abs(longitude - lng_center) / 20 * 0.3
        
        # Score de base
        base_score = (lat_factor * 0.6 + lng_factor * 0.4) * 100
        
        # Ajustement par espece
        species_modifier = {
            Species.MOOSE: 1.0,
            Species.DEER: 0.95,
            Species.BEAR: 0.90,
            Species.WILD_TURKEY: 0.85,
            Species.ELK: 0.88
        }
        
        return base_score * species_modifier.get(species, 1.0)
    
    def _calculate_weather_score(
        self,
        latitude: float,
        longitude: float,
        weather_override: Optional[WeatherOverride]
    ) -> Tuple[float, Dict]:
        """
        Calcule le score meteo (F5 - Microclimats, F9 - Extremes).
        
        Utilise les seuils de l'inventaire:
        - Temperature optimale: -5C a 15C
        - Vent optimal: 0-20 km/h
        - Pression optimale: 1000-1030 hPa
        """
        # Donnees meteo
        if weather_override:
            weather_data = {
                "temperature": weather_override.temperature or 10,
                "wind_speed": weather_override.wind_speed or 10,
                "pressure": weather_override.pressure or 1015,
                "precipitation": weather_override.precipitation or 0
            }
        else:
            # Valeurs par defaut simulees (P0)
            # P1 integrera Open-Meteo / Environment Canada
            weather_data = {
                "temperature": 8,
                "wind_speed": 12,
                "pressure": 1018,
                "precipitation": 0
            }
        
        # Score temperature
        temp = weather_data["temperature"]
        if OPTIMAL_WEATHER["temperature"]["min"] <= temp <= OPTIMAL_WEATHER["temperature"]["max"]:
            temp_score = 100 - abs(temp - OPTIMAL_WEATHER["temperature"]["ideal"]) * 3
        elif temp < OPTIMAL_WEATHER["temperature"]["min"]:
            temp_score = max(0, 50 - abs(temp - OPTIMAL_WEATHER["temperature"]["min"]) * 2)
        else:
            temp_score = max(0, 50 - abs(temp - OPTIMAL_WEATHER["temperature"]["max"]) * 3)
        
        # Score vent
        wind = weather_data["wind_speed"]
        if wind <= OPTIMAL_WEATHER["wind_speed"]["max"]:
            wind_score = 100 - (wind / OPTIMAL_WEATHER["wind_speed"]["max"]) * 30
        else:
            wind_score = max(0, 70 - (wind - OPTIMAL_WEATHER["wind_speed"]["max"]) * 2)
        
        # Score pression
        pressure = weather_data["pressure"]
        pressure_score = 100 - abs(pressure - OPTIMAL_WEATHER["pressure"]["ideal"]) * 2
        pressure_score = max(0, min(100, pressure_score))
        
        # Score precipitation (leger = bon, fort = mauvais)
        precip = weather_data["precipitation"]
        if precip < 1:
            precip_score = 100
        elif precip < 5:
            precip_score = 80
        else:
            precip_score = max(0, 60 - precip * 5)
        
        # Score global meteo
        weather_score = (
            temp_score * 0.40 +
            wind_score * 0.25 +
            pressure_score * 0.20 +
            precip_score * 0.15
        )
        
        return weather_score, weather_data
    
    def _calculate_temporal_score(
        self,
        species: Species,
        datetime_target: datetime
    ) -> float:
        """
        Calcule le score temporel (F12 - Cycles Temporels).
        
        Combine:
        - Pattern horaire par espece
        - Facteur saisonnier
        - Modificateur hebdomadaire
        """
        hour = datetime_target.hour
        month = datetime_target.month
        weekday = datetime_target.weekday()
        
        # Score horaire
        hourly_patterns = HOURLY_ACTIVITY_PATTERNS.get(species, HOURLY_ACTIVITY_PATTERNS[Species.MOOSE])
        hourly_score = hourly_patterns.get(hour, 50)
        
        # Facteur saisonnier
        seasonal_factor = SEASON_FACTORS.get(month, 0.7)
        
        # Facteur hebdomadaire
        weekly_factor = WEEKLY_MODIFIERS.get(weekday, 1.0)
        
        # Bonus rut
        rut_bonus = 1.0
        if self._is_rut_period(species, datetime_target):
            rut_bonus = self.weights_config.arbitrage.get("rut_boost_factor", 1.5)
        
        # Score combine
        temporal_score = hourly_score * seasonal_factor * weekly_factor * rut_bonus
        
        return min(100, temporal_score)
    
    def _calculate_pressure_score(
        self,
        latitude: float,
        longitude: float,
        datetime_target: datetime
    ) -> float:
        """
        Calcule le score de pression de chasse (F8 - Pression).
        
        NOTE: P0 - Simulation basee sur jour de semaine et periode
        P1 integrera agregation des sorties BIONIC HUNT/Chasse
        
        Score INVERSE: 100 = pas de pression, 0 = pression maximale
        """
        weekday = datetime_target.weekday()
        month = datetime_target.month
        
        # Pression plus elevee le weekend
        if weekday >= 5:  # Samedi, Dimanche
            base_pressure = 60
        elif weekday == 4:  # Vendredi
            base_pressure = 40
        else:
            base_pressure = 20
        
        # Pression plus elevee en saison de chasse (Oct-Nov)
        if month in [10, 11]:
            base_pressure += 20
        elif month in [9, 12]:
            base_pressure += 10
        
        # Convertir en score inverse (100 = favorable)
        pressure_score = 100 - min(100, base_pressure)
        
        return pressure_score
    
    def _calculate_microclimate_score(
        self,
        latitude: float,
        longitude: float,
        weather_data: Dict,
        datetime_target: datetime
    ) -> float:
        """
        Calcule l'indice microclimatique (Bloc 2 - Microclimats).
        
        Formule IMC:
        IMC = T_base + Delta_elev + Delta_aspect + Delta_canopy + Delta_wind
        
        NOTE: P0 - Version simplifiee
        P1 integrera DEM et LiDAR
        """
        temp = weather_data.get("temperature", 10)
        wind = weather_data.get("wind_speed", 10)
        month = datetime_target.month
        
        # Estimation elevation basee sur latitude (approximation)
        estimated_elevation = (latitude - 45) * 50  # metres
        delta_elev = -0.0065 * estimated_elevation
        
        # Effet vent (windchill simplifie)
        if temp < 10 and wind > 10:
            delta_wind = -0.5 * (wind / 10)
        else:
            delta_wind = 0
        
        # Temperature estimee
        estimated_temp = temp + delta_elev + delta_wind
        
        # Score: temperature estimee vs optimale pour la saison
        if month in [12, 1, 2]:  # Hiver
            optimal_temp = -5
        elif month in [6, 7, 8]:  # Ete
            optimal_temp = 15
        else:
            optimal_temp = 10
        
        diff = abs(estimated_temp - optimal_temp)
        microclimate_score = max(0, 100 - diff * 4)
        
        return microclimate_score
    
    def _calculate_historical_score(
        self,
        latitude: float,
        longitude: float,
        species: Species
    ) -> float:
        """
        Calcule le score historique (F10 - Historiques).
        
        NOTE: P0 - Baseline regional
        P1 integrera donnees MELCCFP et observations utilisateurs
        """
        # Baseline regional (P0)
        # Zones connues favorables
        
        # Score de base selon position
        base_score = 60
        
        # Bonus zones reconnues (simplification P0)
        if 47 <= latitude <= 49 and -72 <= longitude <= -68:
            # Cote-Nord / Laurentides
            base_score += 15
        elif 48 <= latitude <= 50 and -68 <= longitude <= -65:
            # Gaspesie / Bas-St-Laurent
            base_score += 10
        
        return min(100, base_score)
    
    # =========================================================================
    # ARBITRAGE & WEIGHTS
    # =========================================================================
    
    def _detect_extreme_conditions(self, weather_data: Dict) -> Tuple[bool, str]:
        """
        Detecte les conditions extremes (Niveau 1 - CRITIQUE).
        
        Seuils de l'inventaire v1.2:
        - Temperature < -30C ou > 32C
        - Vent > 60 km/h
        """
        thresholds = self.weights_config.arbitrage.get("extreme_weather_threshold", {})
        
        temp = weather_data.get("temperature", 10)
        wind = weather_data.get("wind_speed", 10)
        
        if temp < thresholds.get("temp_min", -30):
            return True, "cold"
        if temp > thresholds.get("temp_max", 32):
            return True, "heat"
        if wind > thresholds.get("wind_max", 60):
            return True, "wind"
        
        return False, ""
    
    def _is_rut_period(self, species: Species, datetime_target: datetime) -> bool:
        """Verifie si on est en periode de rut."""
        if species not in RUT_PERIODS:
            return False
        
        rut = RUT_PERIODS[species]
        month = datetime_target.month
        
        return rut["start_month"] <= month <= rut["end_month"]
    
    def _get_dynamic_weights(
        self,
        is_extreme: bool,
        is_rut: bool,
        is_high_pressure: bool
    ) -> Dict[str, float]:
        """
        Retourne les poids dynamiques selon le contexte.
        
        Conforme a: Inventaire v1.2 - Ponderations Dynamiques
        
        Regles d'arbitrage (priorite):
        1. Conditions extremes -> weather domine
        2. Rut actif -> temporal domine, pression reduite
        3. Haute pression seule -> pression augmentee
        """
        weights = self.weights_config.base.copy()
        
        # Conditions extremes (Niveau 1 - Override)
        if is_extreme:
            weights["weather_conditions"] *= 2.0
            weights["microclimate"] *= 1.5
        
        # Periode rut (Niveau 2 - Primaire)
        if is_rut:
            weights["temporal_alignment"] *= 1.5
            weights["habitat_quality"] *= 1.25
            # REGLE ARBITRAGE: Rut domine pression
            # Le rut transcende la pression de chasse - les animaux
            # sont plus actifs malgre la presence de chasseurs
            if is_high_pressure:
                weights["pressure_index"] *= 0.5  # Reduire impact pression
            else:
                weights["pressure_index"] *= 0.7
        
        # Haute pression seule (sans rut)
        elif is_high_pressure:
            weights["pressure_index"] *= 2.0
            weights["habitat_quality"] *= 0.8
        
        # Normaliser
        total = sum(weights.values())
        weights = {k: v / total for k, v in weights.items()}
        
        return weights
    
    def _calculate_confidence(
        self,
        has_live_weather: bool,
        is_extreme: bool
    ) -> float:
        """Calcule le niveau de confiance du score."""
        confidence = 0.85  # Base
        
        if not has_live_weather:
            confidence -= 0.15
        
        if is_extreme:
            confidence -= 0.10
        
        return max(0.5, confidence)
    
    # =========================================================================
    # RECOMMENDATIONS
    # =========================================================================
    
    def _generate_recommendations(
        self,
        overall_score: float,
        species: Species,
        datetime_target: datetime,
        is_extreme: bool,
        is_rut: bool,
        is_high_pressure: bool,
        weather_data: Dict
    ) -> List[Recommendation]:
        """
        Genere les recommandations contextuelles.
        
        G-DOC: Chaque recommandation est justifiee
        """
        recommendations = []
        
        # Recommandations de timing
        hour = datetime_target.hour
        if 5 <= hour <= 8 or 16 <= hour <= 19:
            recommendations.append(Recommendation(
                type="timing",
                priority="high",
                message_fr="Periode d'activite elevee. Excellent moment pour la chasse.",
                message_en="High activity period. Excellent hunting time."
            ))
        elif 11 <= hour <= 14:
            recommendations.append(Recommendation(
                type="timing",
                priority="medium",
                message_fr="Activite reduite en milieu de journee. Privilegiez l'aube ou le crepuscule.",
                message_en="Reduced midday activity. Prefer dawn or dusk."
            ))
        
        # Recommandations conditions
        if is_extreme:
            recommendations.append(Recommendation(
                type="strategy",
                priority="critical",
                message_fr="Conditions extremes detectees. Les animaux cherchent un refuge. Ciblez les zones protegees.",
                message_en="Extreme conditions detected. Animals seeking shelter. Target protected areas."
            ))
        
        # Recommandations rut
        if is_rut:
            if species == Species.MOOSE:
                recommendations.append(Recommendation(
                    type="strategy",
                    priority="high",
                    message_fr="Periode de rut de l'orignal. Utilisez les appels (calls) et surveillez les zones ouvertes.",
                    message_en="Moose rut period. Use calls and watch open areas."
                ))
            elif species == Species.DEER:
                recommendations.append(Recommendation(
                    type="strategy",
                    priority="high",
                    message_fr="Periode de rut du cerf. Cherchez les grattages (scrapes) et les lignes de cretes.",
                    message_en="Deer rut period. Look for scrapes and ridgelines."
                ))
        
        # Recommandations pression
        if is_high_pressure:
            recommendations.append(Recommendation(
                type="position",
                priority="high",
                message_fr="Forte pression de chasse dans la zone. Explorez les zones moins accessibles ou revenez en semaine.",
                message_en="High hunting pressure in the area. Explore less accessible areas or return during weekdays."
            ))
        
        # Recommandation score global
        if overall_score >= 70:
            recommendations.append(Recommendation(
                type="strategy",
                priority="high",
                message_fr=f"Conditions excellentes (score {overall_score:.0f}/100). Maximisez votre temps sur le terrain.",
                message_en=f"Excellent conditions (score {overall_score:.0f}/100). Maximize your time in the field."
            ))
        elif overall_score < 40:
            recommendations.append(Recommendation(
                type="timing",
                priority="medium",
                message_fr=f"Conditions difficiles (score {overall_score:.0f}/100). Envisagez de reporter votre sortie.",
                message_en=f"Challenging conditions (score {overall_score:.0f}/100). Consider postponing your trip."
            ))
        
        return recommendations

    # =========================================================================
    # P0-BETA2: ADVANCED FACTOR RECOMMENDATIONS
    # =========================================================================
    
    def _generate_advanced_recommendations(
        self,
        advanced_factors: Dict,
        species: Species
    ) -> List[Recommendation]:
        """
        Genere des recommandations basees sur les 12 facteurs comportementaux.
        
        P0-BETA2: Integration des facteurs avances dans les recommandations
        
        G-DOC: Chaque recommandation est justifiee par un facteur specifique
        """
        recommendations = []
        
        # 1. Recommandations PREDATION
        predation = advanced_factors.get("predation", {})
        if predation.get("risk_score", 0) > 50:
            dominant_predator = predation.get("dominant_predator", "unknown")
            recommendations.append(Recommendation(
                type="strategy",
                priority="high",
                message_fr=f"Risque de predation eleve ({dominant_predator}). Les animaux seront plus vigilants - privilegiez les zones de couvert dense.",
                message_en=f"High predation risk ({dominant_predator}). Animals will be more vigilant - favor dense cover areas."
            ))
        
        # 2. Recommandations STRESS THERMIQUE
        thermal = advanced_factors.get("thermal_stress", {})
        if thermal.get("stress_score", 0) > 30:
            response = thermal.get("behavioral_response", "")
            if response == "seeking_water_shade":
                recommendations.append(Recommendation(
                    type="position",
                    priority="high",
                    message_fr="Stress thermique eleve - les animaux cherchent l'eau et l'ombre. Postez-vous pres des cours d'eau ou zones ombragees.",
                    message_en="High thermal stress - animals seeking water and shade. Position near water or shaded areas."
                ))
            elif response == "seeking_shelter":
                recommendations.append(Recommendation(
                    type="position",
                    priority="medium",
                    message_fr="Froid intense - les animaux cherchent des abris. Surveillez les ravages et zones de coniferes denses.",
                    message_en="Intense cold - animals seeking shelter. Watch yards and dense conifer areas."
                ))
        
        # 3. Recommandations HIERARCHIE SOCIALE
        hierarchy = advanced_factors.get("social_hierarchy", {})
        if hierarchy.get("aggression_level") == "high":
            recommendations.append(Recommendation(
                type="strategy",
                priority="high",
                message_fr="Periode de forte dominance - les males se deplacent davantage. Utilisez leurres et appels de defi.",
                message_en="High dominance period - males moving more. Use decoys and challenge calls."
            ))
        
        # 4. Recommandations CYCLES HORMONAUX
        hormonal = advanced_factors.get("hormonal", {})
        phase = hormonal.get("phase", "")
        if phase == "rut_peak":
            recommendations.append(Recommendation(
                type="strategy",
                priority="critical",
                message_fr="PIC DU RUT - Activite maximale des males. Moment ideal pour les appels et techniques de rattling.",
                message_en="RUT PEAK - Maximum male activity. Ideal time for calls and rattling techniques."
            ))
        elif phase == "antler_growth":
            recommendations.append(Recommendation(
                type="strategy",
                priority="medium",
                message_fr="Croissance des bois - les animaux recherchent les mineraux. Surveillez les salines naturelles.",
                message_en="Antler growth - animals seeking minerals. Watch natural salt licks."
            ))
        
        # 5. Recommandations CYCLES DIGESTIFS
        digestive = advanced_factors.get("digestive", {})
        if digestive.get("phase") == "active_feeding":
            recommendations.append(Recommendation(
                type="timing",
                priority="high",
                message_fr="Phase d'alimentation active - les animaux sont en deplacement vers les sources de nourriture.",
                message_en="Active feeding phase - animals moving toward food sources."
            ))
        elif digestive.get("phase") == "transitioning":
            recommendations.append(Recommendation(
                type="timing",
                priority="medium",
                message_fr="Transition alimentation/repos - surveillez les corridors entre zones d'alimentation et de repos.",
                message_en="Feeding/resting transition - watch corridors between feeding and bedding areas."
            ))
        
        # 6. Recommandations MEMOIRE TERRITORIALE
        memory = advanced_factors.get("territorial_memory", {})
        if memory.get("memory_active") and memory.get("avoidance_score", 0) > 50:
            days_until = memory.get("days_until_return", 0)
            recommendations.append(Recommendation(
                type="position",
                priority="medium",
                message_fr=f"Zone recemment perturbee - evitement actif. Retour normal dans ~{days_until} jours.",
                message_en=f"Recently disturbed area - active avoidance. Normal return in ~{days_until} days."
            ))
        
        # 7. Recommandations APPRENTISSAGE COMPORTEMENTAL
        adaptive = advanced_factors.get("adaptive_behavior", {})
        if adaptive.get("behavioral_shift") in ["highly_nocturnal", "increased_caution"]:
            nocturnal_shift = adaptive.get("nocturnal_shift", 0)
            recommendations.append(Recommendation(
                type="strategy",
                priority="high",
                message_fr=f"Animaux tres prudents (shift nocturne {nocturnal_shift*100:.0f}%). Privilegiez les premieres lueurs de l'aube.",
                message_en=f"Highly cautious animals (nocturnal shift {nocturnal_shift*100:.0f}%). Prioritize first light."
            ))
        
        # 8. Recommandations DERANGEMENT HUMAIN
        disturbance = advanced_factors.get("human_disturbance", {})
        if disturbance.get("disturbance_score", 0) > 40:
            recommendations.append(Recommendation(
                type="position",
                priority="medium",
                message_fr="Activite humaine detectee dans la zone. Les animaux seront plus eloignes des sentiers.",
                message_en="Human activity detected in the area. Animals will be further from trails."
            ))
        
        # 9. Recommandations DISPONIBILITE MINERALE
        mineral = advanced_factors.get("mineral", {})
        if mineral.get("seeking_behavior"):
            optimal_time = mineral.get("optimal_monitoring_time", "anytime")
            recommendations.append(Recommendation(
                type="position",
                priority="medium",
                message_fr=f"Forte attraction minerale - surveillez les salines. Moment optimal: {optimal_time}.",
                message_en=f"Strong mineral attraction - watch salt licks. Optimal time: {optimal_time}."
            ))
        
        # 10. Recommandations CONDITIONS DE NEIGE
        snow = advanced_factors.get("snow", {})
        if snow.get("yarding_likelihood"):
            recommendations.append(Recommendation(
                type="position",
                priority="critical",
                message_fr="Neige profonde - les animaux se concentrent dans les ravages. Localisez les zones de cedres et sapins denses.",
                message_en="Deep snow - animals yarding. Locate dense cedar and fir areas."
            ))
        elif snow.get("snow_condition") == "crusted":
            recommendations.append(Recommendation(
                type="strategy",
                priority="high",
                message_fr="Croute de neige - mobilite reduite pour le gibier. Approche plus facile mais soyez patient.",
                message_en="Snow crust - reduced mobility for game. Easier approach but be patient."
            ))
        
        return recommendations

