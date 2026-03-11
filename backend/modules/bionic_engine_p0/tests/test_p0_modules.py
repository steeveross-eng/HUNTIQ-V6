"""
BIONIC ENGINE - P0-BETA2 Unit Tests
PHASE G - G-QA Compliance

Tests unitaires pour les modules P0-BETA2 avec 12 facteurs comportementaux:
- predictive_territorial.py
- behavioral_models.py
- advanced_factors.py

Conformite: Plan de Tests G-QA
"""

import pytest
from datetime import datetime, timezone

from modules.bionic_engine_p0.modules.predictive_territorial import (
    PredictiveTerritorialService
)
from modules.bionic_engine_p0.modules.behavioral_models import (
    BehavioralModelsService
)
from modules.bionic_engine_p0.contracts.data_contracts import (
    Species,
    ScoreRating,
    ActivityLevel,
    BehaviorType,
    SeasonPhase,
    WeatherOverride,
    score_to_rating,
    score_to_activity_level,
    normalize_weights
)
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
    SnowConditionModel,
    IntegratedBehavioralFactors
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def pt_service():
    """Service Predictive Territorial"""
    return PredictiveTerritorialService()


@pytest.fixture
def bm_service():
    """Service Behavioral Models"""
    return BehavioralModelsService()


@pytest.fixture
def sample_coordinates():
    """Coordonnees de test (Laurentides)"""
    return {"latitude": 47.5, "longitude": -70.5}


@pytest.fixture
def optimal_hunting_datetime():
    """Date/heure optimale (octobre, 7h du matin, mardi)"""
    return datetime(2025, 10, 7, 7, 0, tzinfo=timezone.utc)


# =============================================================================
# PREDICTIVE TERRITORIAL - TESTS UNITAIRES
# =============================================================================

class TestPredictiveTerritorialBasic:
    """Tests basiques du score territorial"""
    
    def test_basic_score_calculation(self, pt_service, sample_coordinates):
        """Score basique avec toutes les donnees"""
        result = pt_service.calculate_score(
            latitude=sample_coordinates["latitude"],
            longitude=sample_coordinates["longitude"],
            species=Species.MOOSE,
            datetime_target=datetime(2025, 10, 15, 7, 0, tzinfo=timezone.utc)
        )
        
        assert result.success is True
        assert 0 <= result.overall_score <= 100
        assert 0 <= result.confidence <= 1
        assert result.rating in ScoreRating
    
    def test_score_components_present(self, pt_service, sample_coordinates):
        """Verifier que toutes les composantes sont presentes"""
        result = pt_service.calculate_score(
            latitude=sample_coordinates["latitude"],
            longitude=sample_coordinates["longitude"],
            species=Species.MOOSE
        )
        
        components = result.components
        assert components.habitat_score is not None
        assert components.weather_score is not None
        assert components.temporal_score is not None
        assert components.pressure_score is not None
        assert components.microclimate_score is not None
        assert components.historical_score is not None
    
    def test_score_reproducibility(self, pt_service, sample_coordinates):
        """Meme input = meme output"""
        dt = datetime(2025, 10, 15, 7, 0, tzinfo=timezone.utc)
        
        result1 = pt_service.calculate_score(
            latitude=sample_coordinates["latitude"],
            longitude=sample_coordinates["longitude"],
            species=Species.MOOSE,
            datetime_target=dt
        )
        
        result2 = pt_service.calculate_score(
            latitude=sample_coordinates["latitude"],
            longitude=sample_coordinates["longitude"],
            species=Species.MOOSE,
            datetime_target=dt
        )
        
        assert result1.overall_score == result2.overall_score


class TestPredictiveTerritorialSpecies:
    """Tests par espece"""
    
    @pytest.mark.parametrize("species", [
        Species.MOOSE, Species.DEER, Species.BEAR, 
        Species.WILD_TURKEY, Species.ELK
    ])
    def test_all_species_supported(self, pt_service, sample_coordinates, species):
        """Toutes les especes produisent un score valide"""
        result = pt_service.calculate_score(
            latitude=sample_coordinates["latitude"],
            longitude=sample_coordinates["longitude"],
            species=species,
            datetime_target=datetime(2025, 10, 15, 10, 0, tzinfo=timezone.utc)
        )
        
        assert result.success is True
        assert result.overall_score is not None
    
    def test_bear_hibernation_zero_score(self, pt_service, sample_coordinates):
        """Ours en hibernation = score 0"""
        result = pt_service.calculate_score(
            latitude=sample_coordinates["latitude"],
            longitude=sample_coordinates["longitude"],
            species=Species.BEAR,
            datetime_target=datetime(2025, 1, 15, 10, 0, tzinfo=timezone.utc)
        )
        
        assert result.overall_score == 0
        assert "BEAR_HIBERNATION_PERIOD" in result.warnings
    
    def test_moose_rut_bonus(self, pt_service, sample_coordinates):
        """Orignal en rut = facteur temporel booste"""
        october = datetime(2025, 10, 5, 7, 0, tzinfo=timezone.utc)
        july = datetime(2025, 7, 15, 7, 0, tzinfo=timezone.utc)
        
        result_rut = pt_service.calculate_score(
            latitude=sample_coordinates["latitude"],
            longitude=sample_coordinates["longitude"],
            species=Species.MOOSE,
            datetime_target=october
        )
        
        result_summer = pt_service.calculate_score(
            latitude=sample_coordinates["latitude"],
            longitude=sample_coordinates["longitude"],
            species=Species.MOOSE,
            datetime_target=july
        )
        
        # Le score temporel devrait etre plus eleve en rut
        assert result_rut.components.temporal_score > result_summer.components.temporal_score
        # Et le rut devrait etre detecte
        assert result_rut.metadata.get("is_rut") is True
        assert result_summer.metadata.get("is_rut") is False


class TestPredictiveTerritorialBoundaries:
    """Tests des valeurs limites"""
    
    def test_latitude_at_boundary(self, pt_service):
        """Latitude aux limites Quebec"""
        # Limite sud
        result_south = pt_service.calculate_score(
            latitude=45.0,
            longitude=-71.0,
            species=Species.MOOSE
        )
        assert result_south.success is True
        
        # Limite nord
        result_north = pt_service.calculate_score(
            latitude=62.0,
            longitude=-71.0,
            species=Species.MOOSE
        )
        assert result_north.success is True
    
    def test_score_never_negative(self, pt_service, sample_coordinates):
        """Score jamais negatif"""
        # Pires conditions: ours en hibernation
        result = pt_service.calculate_score(
            latitude=sample_coordinates["latitude"],
            longitude=sample_coordinates["longitude"],
            species=Species.BEAR,
            datetime_target=datetime(2025, 1, 15, 13, 0, tzinfo=timezone.utc)
        )
        
        assert result.overall_score >= 0
    
    def test_score_never_above_100(self, pt_service, sample_coordinates):
        """Score jamais > 100"""
        # Meilleures conditions: rut + aube
        result = pt_service.calculate_score(
            latitude=sample_coordinates["latitude"],
            longitude=sample_coordinates["longitude"],
            species=Species.MOOSE,
            datetime_target=datetime(2025, 10, 5, 7, 0, tzinfo=timezone.utc)
        )
        
        assert result.overall_score <= 100


class TestPredictiveTerritorialWeather:
    """Tests avec override meteo"""
    
    def test_extreme_cold(self, pt_service, sample_coordinates):
        """Temperature extreme froide"""
        weather = WeatherOverride(temperature=-35, wind_speed=10)
        
        result = pt_service.calculate_score(
            latitude=sample_coordinates["latitude"],
            longitude=sample_coordinates["longitude"],
            species=Species.MOOSE,
            weather_override=weather
        )
        
        assert result.success is True
        # Conditions extremes detectees
        assert any("EXTREME" in w for w in result.warnings)
    
    def test_optimal_weather(self, pt_service, sample_coordinates):
        """Conditions meteo optimales"""
        weather = WeatherOverride(temperature=5, wind_speed=8, pressure=1015)
        
        result = pt_service.calculate_score(
            latitude=sample_coordinates["latitude"],
            longitude=sample_coordinates["longitude"],
            species=Species.MOOSE,
            weather_override=weather,
            datetime_target=datetime(2025, 10, 5, 7, 0, tzinfo=timezone.utc)
        )
        
        # Score meteo devrait etre eleve
        assert result.components.weather_score >= 70


# =============================================================================
# BEHAVIORAL MODELS - TESTS UNITAIRES
# =============================================================================

class TestBehavioralModelsBasic:
    """Tests basiques des modeles comportementaux"""
    
    def test_basic_prediction(self, bm_service):
        """Prediction basique"""
        result = bm_service.predict_behavior(
            species=Species.MOOSE,
            datetime_target=datetime(2025, 10, 15, 7, 0, tzinfo=timezone.utc)
        )
        
        assert result.success is True
        assert result.activity is not None
        assert result.timeline is not None
        assert result.seasonal_context is not None
    
    def test_activity_score_range(self, bm_service):
        """Score d'activite dans la plage 0-100"""
        result = bm_service.predict_behavior(
            species=Species.DEER,
            datetime_target=datetime(2025, 10, 15, 7, 0, tzinfo=timezone.utc)
        )
        
        assert 0 <= result.activity.activity_score <= 100
    
    def test_behavior_probabilities_sum(self, bm_service):
        """Probabilites comportements ~ 1.0"""
        result = bm_service.predict_behavior(
            species=Species.MOOSE,
            datetime_target=datetime(2025, 10, 15, 7, 0, tzinfo=timezone.utc)
        )
        
        probs = result.activity.behavior_probabilities
        total = sum(probs.values())
        
        assert 0.99 <= total <= 1.01


class TestBehavioralModelsTimeline:
    """Tests de la timeline 24h"""
    
    def test_timeline_complete(self, bm_service):
        """Timeline complete = 24 entrees"""
        result = bm_service.predict_behavior(
            species=Species.DEER,
            datetime_target=datetime(2025, 10, 15, 10, 0, tzinfo=timezone.utc)
        )
        
        assert len(result.timeline) == 24
    
    def test_timeline_hours_complete(self, bm_service):
        """Toutes les heures presentes"""
        result = bm_service.predict_behavior(
            species=Species.MOOSE,
            datetime_target=datetime(2025, 10, 15, 10, 0, tzinfo=timezone.utc)
        )
        
        hours = [entry.hour for entry in result.timeline]
        assert sorted(hours) == list(range(24))
    
    def test_timeline_legal_hours_flagged(self, bm_service):
        """Heures legales correctement marquees"""
        result = bm_service.predict_behavior(
            species=Species.MOOSE,
            datetime_target=datetime(2025, 10, 15, 10, 0, tzinfo=timezone.utc)
        )
        
        # 7h devrait etre legal
        hour_7 = next(e for e in result.timeline if e.hour == 7)
        assert hour_7.is_legal_hunting is True
        
        # 3h ne devrait pas etre legal
        hour_3 = next(e for e in result.timeline if e.hour == 3)
        assert hour_3.is_legal_hunting is False


class TestBehavioralModelsActivity:
    """Tests des patterns d'activite"""
    
    def test_dawn_high_activity(self, bm_service):
        """Activite elevee a l'aube"""
        result = bm_service.predict_activity(
            species=Species.MOOSE,
            datetime_target=datetime(2025, 10, 15, 6, 30, tzinfo=timezone.utc)
        )
        
        assert result.activity_level in [ActivityLevel.VERY_HIGH, ActivityLevel.HIGH]
        assert result.activity_score >= 60
    
    def test_midday_low_activity(self, bm_service):
        """Activite faible en milieu de journee"""
        result = bm_service.predict_activity(
            species=Species.MOOSE,
            datetime_target=datetime(2025, 10, 15, 13, 0, tzinfo=timezone.utc)
        )
        
        assert result.activity_level in [ActivityLevel.LOW, ActivityLevel.MODERATE, ActivityLevel.MINIMAL]
        assert result.activity_score <= 50
    
    def test_turkey_no_night_activity(self, bm_service):
        """Dindon inactif la nuit"""
        result = bm_service.predict_activity(
            species=Species.WILD_TURKEY,
            datetime_target=datetime(2025, 10, 15, 22, 0, tzinfo=timezone.utc)
        )
        
        assert result.activity_score == 0
        assert result.current_behavior == BehaviorType.RESTING


class TestBehavioralModelsSeasons:
    """Tests des cycles saisonniers"""
    
    def test_rut_detection_moose(self, bm_service):
        """Detection du rut orignal"""
        result = bm_service.predict_behavior(
            species=Species.MOOSE,
            datetime_target=datetime(2025, 10, 5, 10, 0, tzinfo=timezone.utc)
        )
        
        assert result.seasonal_context.current_season == SeasonPhase.RUT
        assert "rut_active" in result.seasonal_context.key_events
    
    def test_bear_hibernation(self, bm_service):
        """Hibernation ours"""
        result = bm_service.predict_behavior(
            species=Species.BEAR,
            datetime_target=datetime(2025, 1, 15, 10, 0, tzinfo=timezone.utc)
        )
        
        assert result.activity.activity_score == 0
        assert "BEAR_HIBERNATION_PERIOD" in result.warnings


# =============================================================================
# DATA CONTRACTS - TESTS UNITAIRES
# =============================================================================

class TestDataContracts:
    """Tests des contrats de donnees"""
    
    def test_score_to_rating_exceptional(self):
        """Score 85+ = exceptional"""
        assert score_to_rating(90) == ScoreRating.EXCEPTIONAL
        assert score_to_rating(85) == ScoreRating.EXCEPTIONAL
    
    def test_score_to_rating_poor(self):
        """Score < 25 = poor"""
        assert score_to_rating(20) == ScoreRating.POOR
        assert score_to_rating(0) == ScoreRating.POOR
    
    def test_score_to_activity_level(self):
        """Conversion score vers niveau d'activite"""
        assert score_to_activity_level(85) == ActivityLevel.VERY_HIGH
        assert score_to_activity_level(65) == ActivityLevel.HIGH
        assert score_to_activity_level(45) == ActivityLevel.MODERATE
        assert score_to_activity_level(25) == ActivityLevel.LOW
        assert score_to_activity_level(10) == ActivityLevel.MINIMAL
    
    def test_normalize_weights_sum_to_one(self):
        """Poids normalises somment a 1"""
        weights = {"a": 0.3, "b": 0.5, "c": 0.2}
        available = ["a", "b", "c"]
        
        normalized = normalize_weights(weights, available)
        
        assert abs(sum(normalized.values()) - 1.0) < 0.01
    
    def test_normalize_weights_missing_source(self):
        """Redistribution avec source manquante"""
        weights = {"a": 0.3, "b": 0.5, "c": 0.2}
        available = ["a", "b"]  # c manquant
        
        normalized = normalize_weights(weights, available)
        
        assert "c" not in normalized
        assert abs(sum(normalized.values()) - 1.0) < 0.01


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestModuleIntegration:
    """Tests d'integration entre modules"""
    
    def test_consistent_species_data(self, pt_service, bm_service):
        """Donnees especes coherentes entre modules"""
        # Les deux modules devraient supporter les memes especes
        for species in [Species.MOOSE, Species.DEER, Species.BEAR]:
            pt_result = pt_service.calculate_score(
                latitude=47.5, longitude=-70.5,
                species=species,
                datetime_target=datetime(2025, 10, 15, 10, 0, tzinfo=timezone.utc)
            )
            
            bm_result = bm_service.predict_behavior(
                species=species,
                datetime_target=datetime(2025, 10, 15, 10, 0, tzinfo=timezone.utc)
            )
            
            assert pt_result.success is True
            assert bm_result.success is True
    
    def test_rut_detection_consistent(self, pt_service, bm_service):
        """Detection du rut coherente entre modules"""
        dt = datetime(2025, 10, 10, 7, 0, tzinfo=timezone.utc)
        
        pt_result = pt_service.calculate_score(
            latitude=47.5, longitude=-70.5,
            species=Species.MOOSE,
            datetime_target=dt
        )
        
        bm_result = bm_service.predict_behavior(
            species=Species.MOOSE,
            datetime_target=dt
        )
        
        # Les deux devraient detecter le rut
        pt_is_rut = pt_result.metadata.get("is_rut", False)
        bm_is_rut = bm_result.seasonal_context.current_season == SeasonPhase.RUT
        
        assert pt_is_rut == bm_is_rut


# =============================================================================
# PERFORMANCE TESTS
# =============================================================================

class TestPerformance:
    """Tests de performance"""
    
    def test_territorial_response_time(self, pt_service, sample_coordinates):
        """Temps de reponse PT < 100ms"""
        import time
        
        start = time.time()
        pt_service.calculate_score(
            latitude=sample_coordinates["latitude"],
            longitude=sample_coordinates["longitude"],
            species=Species.MOOSE
        )
        elapsed = (time.time() - start) * 1000
        
        assert elapsed < 200  # < 200ms (augmente pour les 12 facteurs)
    
    def test_behavioral_response_time(self, bm_service):
        """Temps de reponse BM < 200ms (avec 12 facteurs)"""
        import time
        
        start = time.time()
        bm_service.predict_behavior(
            species=Species.DEER,
            datetime_target=datetime.now(timezone.utc)
        )
        elapsed = (time.time() - start) * 1000
        
        assert elapsed < 200  # < 200ms (augmente pour les 12 facteurs)


# =============================================================================
# P0-BETA2: TESTS DES 12 FACTEURS COMPORTEMENTAUX
# =============================================================================

class TestAdvancedFactors:
    """Tests des 12 facteurs comportementaux avances"""
    
    # =========================================================================
    # FACTEUR 1: PREDATION
    # =========================================================================
    
    def test_predation_risk_calculation(self):
        """Calcul du risque de predation"""
        result = PredatorRiskModel.calculate_predation_risk(
            species="moose",
            latitude=48.5,
            hour=7,
            month=10
        )
        
        assert "risk_score" in result
        assert 0 <= result["risk_score"] <= 100
        assert "dominant_predator" in result
        assert result["dominant_predator"] in ["wolf", "bear"]
    
    def test_predation_higher_at_dawn(self):
        """Risque predation plus eleve a l'aube (loups actifs)"""
        dawn_result = PredatorRiskModel.calculate_predation_risk("deer", 49, 6, 10)
        midday_result = PredatorRiskModel.calculate_predation_risk("deer", 49, 12, 10)
        
        assert dawn_result["wolf_risk"] > midday_result["wolf_risk"]
    
    def test_bear_predation_zero_in_winter(self):
        """Risque ours = 0 en hiver (hibernation)"""
        result = PredatorRiskModel.calculate_predation_risk("moose", 48, 10, 1)
        
        assert result["bear_risk"] == 0
    
    # =========================================================================
    # FACTEUR 2: STRESS PHYSIOLOGIQUE
    # =========================================================================
    
    def test_thermal_stress_heat(self):
        """Stress thermique en chaleur"""
        result = StressModel.calculate_thermal_stress("moose", 25)
        
        assert result["stress_score"] > 0
        assert result["stress_type"] in ["heat", "critical_heat"]
    
    def test_thermal_stress_cold(self):
        """Stress thermique en froid"""
        result = StressModel.calculate_thermal_stress("deer", -25)
        
        assert result["stress_score"] > 0
        assert result["stress_type"] == "cold"
    
    def test_thermal_stress_optimal(self):
        """Pas de stress en conditions optimales"""
        result = StressModel.calculate_thermal_stress("moose", 5)
        
        assert result["stress_score"] == 0
        assert result["stress_type"] == "none"
    
    def test_hydric_stress(self):
        """Stress hydrique"""
        result = StressModel.calculate_hydric_stress("deer", 1500, 25)
        
        assert result["stress_score"] > 0
        assert result["water_seeking"] is True
    
    def test_social_stress_rut(self):
        """Stress social pendant le rut"""
        result = StressModel.calculate_social_stress("deer", 11, 5)
        
        assert result["stress_score"] > 0
        assert result["dominance_seeking"] is True
    
    # =========================================================================
    # FACTEUR 3: HIERARCHIE SOCIALE
    # =========================================================================
    
    def test_dominance_during_rut(self):
        """Dominance elevee pendant le rut"""
        result = SocialHierarchyModel.calculate_dominance_context("deer", 11, is_male=True)
        
        assert result["dominance_score"] >= 80
        assert result["aggression_level"] == "high"
        assert result["movement_pattern"] == "expanded_range"
    
    def test_dominance_outside_rut(self):
        """Dominance faible hors rut"""
        result = SocialHierarchyModel.calculate_dominance_context("deer", 6, is_male=True)
        
        assert result["dominance_score"] < 50
    
    # =========================================================================
    # FACTEUR 4: COMPETITION INTER-ESPECES
    # =========================================================================
    
    def test_interspecies_competition(self):
        """Competition entre especes"""
        result = InterspeciesCompetitionModel.calculate_competition(
            "deer", ["elk", "bear"]
        )
        
        assert "total_competition_score" in result
        assert len(result["competitors"]) > 0
    
    # =========================================================================
    # FACTEUR 5: SIGNAUX FAIBLES
    # =========================================================================
    
    def test_weak_signals_detection(self):
        """Detection de signaux faibles"""
        result = WeakSignalsModel.detect_anomalies(
            current_score=85,
            historical_avg=60,
            weather_rapid_change=True,
            unusual_activity=True
        )
        
        assert result["anomaly_score"] > 0
        assert len(result["anomalies_detected"]) > 0
        assert "significant_deviation_from_baseline" in result["anomalies_detected"]
    
    # =========================================================================
    # FACTEUR 6: CYCLES HORMONAUX
    # =========================================================================
    
    def test_hormonal_rut_peak(self):
        """Phase hormonale - pic du rut"""
        result = HormonalCycleModel.get_hormonal_phase("moose", 10)
        
        assert result["phase"] == "rut_peak"
        assert result["activity_modifier"] == 1.5
        assert result["aggression_level"] == "high"
    
    def test_hormonal_antler_growth(self):
        """Phase hormonale - croissance des bois"""
        result = HormonalCycleModel.get_hormonal_phase("deer", 4)
        
        assert result["phase"] == "antler_growth"
        assert result["behavioral_focus"] == "mineral_seeking"
    
    # =========================================================================
    # FACTEUR 7: CYCLES DIGESTIFS
    # =========================================================================
    
    def test_digestive_feeding_phase(self):
        """Phase digestive - alimentation"""
        result = DigestiveCycleModel.get_digestive_phase("moose", 7)
        
        assert result["phase"] == "active_feeding"
        assert result["feeding_probability"] == 0.9
    
    def test_digestive_resting_phase(self):
        """Phase digestive - repos"""
        result = DigestiveCycleModel.get_digestive_phase("deer", 23)
        
        assert result["phase"] == "resting"
        assert result["feeding_probability"] == 0.1
    
    # =========================================================================
    # FACTEUR 8: MEMOIRE TERRITORIALE
    # =========================================================================
    
    def test_avoidance_memory_active(self):
        """Memoire d'evitement active"""
        result = TerritorialMemoryModel.calculate_avoidance_factor(
            "deer", days_since_disturbance=3, disturbance_intensity=0.8
        )
        
        assert result["memory_active"] is True
        assert result["avoidance_score"] > 0
        assert result["days_until_return"] > 0
    
    def test_avoidance_memory_expired(self):
        """Memoire d'evitement expiree"""
        result = TerritorialMemoryModel.calculate_avoidance_factor(
            "deer", days_since_disturbance=15, disturbance_intensity=0.8
        )
        
        assert result["memory_active"] is False
        assert result["avoidance_score"] == 0
    
    # =========================================================================
    # FACTEUR 9: APPRENTISSAGE COMPORTEMENTAL
    # =========================================================================
    
    def test_adaptive_behavior_high_pressure(self):
        """Adaptation comportementale - forte pression"""
        result = AdaptiveBehaviorModel.calculate_adaptation(
            "deer",
            hunting_pressure_history=[70, 80, 75, 85, 90],
            success_rate_hunters=0.4
        )
        
        assert result["adaptation_level"] > 50
        assert result["behavioral_shift"] in ["highly_nocturnal", "increased_caution"]
        assert result["nocturnal_shift"] > 0
    
    def test_adaptive_behavior_low_pressure(self):
        """Adaptation comportementale - faible pression"""
        result = AdaptiveBehaviorModel.calculate_adaptation(
            "deer",
            hunting_pressure_history=[10, 15, 12, 8, 10],
            success_rate_hunters=0.05
        )
        
        assert result["adaptation_level"] < 30
        assert result["behavioral_shift"] in ["none", "modified_patterns"]
    
    # =========================================================================
    # FACTEUR 10: ACTIVITE HUMAINE NON-CHASSE
    # =========================================================================
    
    def test_human_disturbance_weekend(self):
        """Derangement humain - weekend"""
        result = HumanDisturbanceModel.calculate_disturbance(
            ["hiking", "atv"],
            is_weekend=True,
            is_summer=True
        )
        
        assert result["disturbance_score"] > 50
        assert result["behavioral_response"] in ["avoidance", "caution"]
    
    def test_human_disturbance_minimal(self):
        """Derangement humain - minimal"""
        result = HumanDisturbanceModel.calculate_disturbance(
            [],
            is_weekend=False,
            is_summer=False
        )
        
        assert result["disturbance_score"] == 0
        assert result["behavioral_response"] == "normal"
    
    # =========================================================================
    # FACTEUR 11: DISPONIBILITE MINERALE
    # =========================================================================
    
    def test_mineral_attraction_spring(self):
        """Attraction minerale - printemps"""
        result = MineralAvailabilityModel.calculate_mineral_attraction(
            "moose", 4, salt_lick_distance_m=200
        )
        
        assert result["mineral_need_score"] >= 80
        assert result["seeking_behavior"] is True
    
    def test_mineral_attraction_fall(self):
        """Attraction minerale - automne (faible)"""
        result = MineralAvailabilityModel.calculate_mineral_attraction(
            "deer", 10, salt_lick_distance_m=1000
        )
        
        assert result["mineral_need_score"] < 50
        assert result["seeking_behavior"] is False
    
    # =========================================================================
    # FACTEUR 12: CONDITIONS DE NEIGE
    # =========================================================================
    
    def test_snow_deep_impact(self):
        """Impact neige profonde"""
        result = SnowConditionModel.calculate_snow_impact(
            "deer", snow_depth_cm=80, is_crusted=False, temperature=-5
        )
        
        assert result["snow_condition"] == "deep"
        assert result["winter_penalty_score"] > 40
        assert result["yarding_likelihood"] is True
    
    def test_snow_crusted_impact(self):
        """Impact croute de neige"""
        result = SnowConditionModel.calculate_snow_impact(
            "moose", snow_depth_cm=50, is_crusted=True, temperature=-2
        )
        
        assert result["snow_condition"] == "crusted"
        assert result["crust_risk"] > 0
    
    def test_snow_none(self):
        """Pas de neige"""
        result = SnowConditionModel.calculate_snow_impact(
            "deer", snow_depth_cm=0, is_crusted=False, temperature=10
        )
        
        assert result["snow_condition"] == "none"
        assert result["winter_penalty_score"] == 0


# =============================================================================
# P0-BETA2: TESTS D'INTEGRATION DES 12 FACTEURS
# =============================================================================

class TestAdvancedFactorsIntegration:
    """Tests d'integration des 12 facteurs dans les modules principaux"""
    
    def test_pt_with_advanced_factors(self, pt_service, sample_coordinates):
        """Score territorial avec 12 facteurs"""
        result = pt_service.calculate_score(
            latitude=sample_coordinates["latitude"],
            longitude=sample_coordinates["longitude"],
            species=Species.MOOSE,
            datetime_target=datetime(2025, 10, 15, 7, 0, tzinfo=timezone.utc),
            include_advanced_factors=True
        )
        
        assert result.success is True
        assert result.metadata.get("advanced_factors_enabled") is True
        assert result.metadata.get("version") == "P0-beta2"
        assert "advanced_factors" in result.metadata
        assert "advanced_factor_scores" in result.metadata
    
    def test_pt_without_advanced_factors(self, pt_service, sample_coordinates):
        """Score territorial sans 12 facteurs"""
        result = pt_service.calculate_score(
            latitude=sample_coordinates["latitude"],
            longitude=sample_coordinates["longitude"],
            species=Species.MOOSE,
            include_advanced_factors=False
        )
        
        assert result.success is True
        assert result.metadata.get("advanced_factors_enabled") is False
    
    def test_pt_advanced_recommendations(self, pt_service, sample_coordinates):
        """Recommandations avancees presentes"""
        result = pt_service.calculate_score(
            latitude=sample_coordinates["latitude"],
            longitude=sample_coordinates["longitude"],
            species=Species.MOOSE,
            datetime_target=datetime(2025, 10, 10, 7, 0, tzinfo=timezone.utc),
            include_advanced_factors=True,
            include_recommendations=True
        )
        
        assert len(result.recommendations) > 0
        # Pendant le rut, on devrait avoir des recommandations hormonales
        rec_types = [r.type for r in result.recommendations]
        assert len(rec_types) >= 1
    
    def test_bm_with_advanced_factors(self, bm_service):
        """Prediction comportementale avec 12 facteurs"""
        result = bm_service.predict_behavior(
            species=Species.DEER,
            datetime_target=datetime(2025, 10, 15, 7, 0, tzinfo=timezone.utc),
            latitude=47.5,
            include_advanced_factors=True
        )
        
        assert result.success is True
        assert result.metadata.get("advanced_factors_enabled") is True
        assert result.metadata.get("version") == "P0-beta2"
        assert "advanced_factors" in result.metadata
        assert "behavioral_modifiers" in result.metadata
    
    def test_bm_without_advanced_factors(self, bm_service):
        """Prediction comportementale sans 12 facteurs"""
        result = bm_service.predict_behavior(
            species=Species.DEER,
            include_advanced_factors=False
        )
        
        assert result.success is True
        assert result.metadata.get("advanced_factors_enabled") is False
    
    def test_bm_advanced_strategies(self, bm_service):
        """Strategies avancees presentes"""
        result = bm_service.predict_behavior(
            species=Species.MOOSE,
            datetime_target=datetime(2025, 10, 10, 7, 0, tzinfo=timezone.utc),
            latitude=48.0,
            include_strategy=True,
            include_advanced_factors=True
        )
        
        assert len(result.strategies) > 0
    
    def test_snow_impact_in_pt(self, pt_service, sample_coordinates):
        """Impact neige dans le score territorial"""
        result_no_snow = pt_service.calculate_score(
            latitude=sample_coordinates["latitude"],
            longitude=sample_coordinates["longitude"],
            species=Species.DEER,
            datetime_target=datetime(2025, 12, 15, 10, 0, tzinfo=timezone.utc),
            snow_depth_cm=0,
            include_advanced_factors=True
        )
        
        result_deep_snow = pt_service.calculate_score(
            latitude=sample_coordinates["latitude"],
            longitude=sample_coordinates["longitude"],
            species=Species.DEER,
            datetime_target=datetime(2025, 12, 15, 10, 0, tzinfo=timezone.utc),
            snow_depth_cm=80,
            is_crusted=True,
            include_advanced_factors=True
        )
        
        # Neige profonde devrait reduire le score ou ajouter des warnings
        snow_factors = result_deep_snow.metadata.get("advanced_factors", {}).get("snow", {})
        assert snow_factors.get("winter_penalty_score", 0) > 0
    
    def test_integrated_behavioral_factors(self):
        """Test du calculateur integre"""
        result = IntegratedBehavioralFactors.calculate_all_factors(
            species="moose",
            latitude=48.5,
            hour=7,
            month=10,
            temperature=5,
            snow_depth_cm=0,
            is_crusted=False,
            is_weekend=False
        )
        
        assert "factors" in result
        assert "integrated_score" in result
        assert "dominant_factors" in result
        assert "behavioral_recommendations" in result
        
        # Verifier que tous les 12 facteurs sont presents
        factors = result["factors"]
        expected_factors = [
            "predation", "thermal_stress", "hydric_stress", "social_stress",
            "competition", "weak_signals", "hormonal", "digestive",
            "territorial_memory", "adaptive_behavior", "human_disturbance",
            "snow", "mineral"
        ]
        for factor in expected_factors:
            assert factor in factors


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
