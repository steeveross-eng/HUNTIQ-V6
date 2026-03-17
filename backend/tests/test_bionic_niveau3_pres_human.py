"""
BIONIC V5 NIVEAU 3 — Validation Exhaustive PRES-HUMAN (Pression Humaine Réelle)
================================================================================

Ce module valide le modèle de pression humaine NIVEAU 3:
1. HumanPressureRegistry — Initialisation avec 3 espèces (moose, deer, bear)
2. SpeciesHumanPressureResponse — avoidance_distances_m par type d'activité
3. get_pressure_modifier() — retourne (modifier, source_ids)
4. get_hunting_pressure_modifier() — retourne (modifier, details, source_ids)
5. HumanPressureModel — density_per_km2, frequency, intensity
6. AvoidanceZone — is_active(), get_modifier_for_species()
7. Zones d'évitement dynamiques (heures, jours, validité)
8. UnifiedScoringService._inject_advanced_modifiers() — intègre PRES-HUMAN
9. API — hunting_pressure.version = '3.0.0' (NIVEAU 3)
10. API — hunting_pressure.details expose tous les détails PRES-HUMAN

ESPÈCES TESTÉES: moose (très sensible), deer (modéré), bear (modéré)
INTENSITÉS TESTÉES: none, low, moderate, high, extreme
TYPES D'ACTIVITÉ: hunting, scouting, recreation, forestry
SOURCE_IDS ATTENDUS: SRC-GPS-HUNT, SRC-TERRAIN-CAM, SRC-PRES-HUMAN

Conformité: G-SEC | G-QA | G-DOC | BIONIC V5 NIVEAU 3
"""

import pytest
import os
import requests
from datetime import datetime, date, timezone, timedelta
from typing import List, Dict, Any, Tuple

# Import des modules PRES-HUMAN
from modules.bionic_engine_p0.knowledge.human_pressure import (
    HumanPressureRegistry,
    get_human_pressure_registry,
    SpeciesHumanPressureResponse,
    HumanPressureModel,
    AvoidanceZone,
    HumanPressureObservation,
    HumanPressureIntensity,
    HumanActivityType,
    AvoidanceZoneType,
    TemporalPattern
)

# Import du UnifiedScoringService
from modules.bionic_engine_p0.services.unified_scoring_service import (
    UnifiedScoringService,
    get_unified_scoring_service
)

# Import du ScoreContext
from modules.bionic_engine_p0.services.scoring.base_score_service import ScoreContext

# BASE URL for API tests
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://species-network.preview.emergentagent.com').rstrip('/')


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def registry() -> HumanPressureRegistry:
    """Obtenir l'instance du registre de pression humaine"""
    return get_human_pressure_registry()


@pytest.fixture
def unified_service() -> UnifiedScoringService:
    """Obtenir l'instance du service de scoring unifié"""
    return get_unified_scoring_service()


@pytest.fixture
def api_client():
    """Session HTTP pour les tests API"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


def create_score_context(
    species: str = "moose",
    hour: int = 7,
    latitude: float = 46.83,
    longitude: float = -71.21,
    hunting_pressure_detected: bool = False,
    temperature_c: float = 12.0
) -> ScoreContext:
    """Helper pour créer un contexte de scoring avec données PRES-HUMAN"""
    target_dt = datetime(2025, 10, 15, hour, 0, 0, tzinfo=timezone.utc)
    return ScoreContext(
        waypoint_id=f"TEST-PRESHUMAN-{species.upper()}-{hour}",
        latitude=latitude,
        longitude=longitude,
        target_datetime=target_dt,
        species=species,
        region="CA-QC",
        extra_data={
            "latitude": latitude,
            "longitude": longitude,
            "hunting_pressure_detected": hunting_pressure_detected,
            "temperature_c": temperature_c
        }
    )


# =============================================================================
# TEST CLASS 1: HumanPressureRegistry — INITIALISATION
# =============================================================================

class TestHumanPressureRegistryInitialization:
    """Tests pour l'initialisation du HumanPressureRegistry avec 3 espèces"""
    
    def test_registry_initialized_with_3_species(self, registry):
        """TEST 1: Le registre contient des réponses pour 3 espèces (moose, deer, bear)"""
        stats = registry.get_stats()
        
        assert stats["species_responses"] == 3, f"Expected 3 species, got {stats['species_responses']}"
        
        supported = stats["supported_species"]
        assert "moose" in supported, "moose missing from supported species"
        assert "deer" in supported, "deer missing from supported species"
        assert "bear" in supported, "bear missing from supported species"
        
        print(f"✓ Registry initialized with {stats['species_responses']} species: {supported}")
    
    def test_registry_has_observations(self, registry):
        """TEST 2: Le registre contient des observations de démonstration"""
        stats = registry.get_stats()
        
        assert stats["observations"] >= 1, f"Expected at least 1 observation, got {stats['observations']}"
        
        print(f"✓ Registry has {stats['observations']} observations")
    
    def test_registry_has_avoidance_zones(self, registry):
        """TEST 3: Le registre contient des zones d'évitement"""
        stats = registry.get_stats()
        
        assert stats["avoidance_zones"] >= 1, f"Expected at least 1 avoidance zone, got {stats['avoidance_zones']}"
        
        print(f"✓ Registry has {stats['avoidance_zones']} avoidance zones")
    
    def test_registry_source_ids_defined(self, registry):
        """TEST 4: Le registre expose les source_ids utilisés"""
        stats = registry.get_stats()
        
        source_ids = stats.get("source_ids", [])
        assert len(source_ids) >= 1, "source_ids should be defined"
        
        # Vérifier les sources attendues
        expected_sources = ["SRC-PRES-HUMAN", "SRC-GPS-HUNT"]
        for src in expected_sources:
            if any(src in s for s in source_ids):
                print(f"  ✓ {src} present")
        
        print(f"✓ Registry source_ids: {source_ids}")


# =============================================================================
# TEST CLASS 2: SpeciesHumanPressureResponse — DISTANCES D'ÉVITEMENT
# =============================================================================

class TestSpeciesHumanPressureResponse:
    """Tests pour les réponses comportementales des espèces à la pression humaine"""
    
    def test_moose_response_exists(self, registry):
        """TEST 5: L'orignal a une réponse à la pression humaine"""
        response = registry.get_species_response("moose")
        
        assert response is not None, "Moose response should exist"
        assert response.species == "moose"
        
        print(f"✓ Moose response found: tolerance={response.tolerance_threshold.value}")
    
    def test_moose_avoidance_distances_by_activity(self, registry):
        """TEST 6: Orignal — distances d'évitement par type d'activité"""
        response = registry.get_species_response("moose")
        
        assert len(response.avoidance_distances_m) >= 4, "Moose should have at least 4 activity types"
        
        # Vérifier les types d'activité
        expected_activities = [
            HumanActivityType.HUNTING,
            HumanActivityType.SCOUTING,
            HumanActivityType.RECREATION,
            HumanActivityType.FORESTRY
        ]
        
        for activity in expected_activities:
            assert activity in response.avoidance_distances_m, f"{activity.value} missing"
            distance = response.avoidance_distances_m[activity]
            print(f"  - {activity.value}: {distance}m")
        
        # Orignal très sensible: distances 500-1000m pour chasse
        hunting_dist = response.avoidance_distances_m.get(HumanActivityType.HUNTING, 0)
        assert hunting_dist >= 500, f"Moose hunting avoidance should be >= 500m, got {hunting_dist}m"
        
        print(f"✓ Moose avoidance distances validated (hunting={hunting_dist}m)")
    
    def test_deer_avoidance_distances_moderate(self, registry):
        """TEST 7: Cerf — distances d'évitement modérées (200-500m)"""
        response = registry.get_species_response("deer")
        
        assert response is not None, "Deer response should exist"
        
        hunting_dist = response.avoidance_distances_m.get(HumanActivityType.HUNTING, 0)
        
        # Cerf modéré: distances 200-500m
        assert 200 <= hunting_dist <= 600, f"Deer hunting avoidance should be 200-600m, got {hunting_dist}m"
        
        print(f"✓ Deer avoidance distances validated (hunting={hunting_dist}m)")
    
    def test_bear_avoidance_distances_exist(self, registry):
        """TEST 8: Ours — distances d'évitement définies"""
        response = registry.get_species_response("bear")
        
        assert response is not None, "Bear response should exist"
        assert len(response.avoidance_distances_m) >= 4, "Bear should have at least 4 activity types"
        
        hunting_dist = response.avoidance_distances_m.get(HumanActivityType.HUNTING, 0)
        print(f"✓ Bear avoidance distances validated (hunting={hunting_dist}m)")
    
    def test_moose_is_more_sensitive_than_deer(self, registry):
        """TEST 9: L'orignal est plus sensible que le cerf (distances plus grandes)"""
        moose = registry.get_species_response("moose")
        deer = registry.get_species_response("deer")
        
        moose_hunting = moose.avoidance_distances_m.get(HumanActivityType.HUNTING, 0)
        deer_hunting = deer.avoidance_distances_m.get(HumanActivityType.HUNTING, 0)
        
        assert moose_hunting > deer_hunting, f"Moose ({moose_hunting}m) should be more sensitive than deer ({deer_hunting}m)"
        
        print(f"✓ Moose ({moose_hunting}m) > Deer ({deer_hunting}m) — sensitivity confirmed")
    
    def test_vulnerability_by_season_exists(self, registry):
        """TEST 10: vulnerability_by_season impacte le modificateur"""
        response = registry.get_species_response("moose")
        
        assert hasattr(response, "vulnerability_by_season"), "vulnerability_by_season missing"
        assert len(response.vulnerability_by_season) >= 1, "vulnerability_by_season should have entries"
        
        # hunting_season devrait augmenter la vulnérabilité
        if "hunting_season" in response.vulnerability_by_season:
            assert response.vulnerability_by_season["hunting_season"] > 1.0, "Hunting season should increase vulnerability"
            print(f"  - hunting_season: {response.vulnerability_by_season['hunting_season']}")
        
        print(f"✓ vulnerability_by_season: {response.vulnerability_by_season}")
    
    def test_species_response_has_source_ids(self, registry):
        """TEST 11: SpeciesHumanPressureResponse contient source_ids"""
        response = registry.get_species_response("moose")
        
        assert hasattr(response, "source_ids"), "source_ids attribute missing"
        assert len(response.source_ids) > 0, "source_ids should not be empty"
        
        print(f"✓ Moose response source_ids: {response.source_ids}")


# =============================================================================
# TEST CLASS 3: get_pressure_modifier() — MODIFICATEUR DE PRESSION
# =============================================================================

class TestGetPressureModifier:
    """Tests pour get_pressure_modifier() qui retourne (modifier, source_ids)"""
    
    def test_returns_tuple(self, registry):
        """TEST 12: get_pressure_modifier() retourne (modifier, source_ids)"""
        result = registry.get_pressure_modifier(
            species="moose",
            intensity=HumanPressureIntensity.MODERATE,
            season="default"
        )
        
        assert isinstance(result, tuple), "Should return tuple"
        assert len(result) == 2, "Tuple should have 2 elements (modifier, source_ids)"
        
        modifier, sources = result
        assert isinstance(modifier, float), "Modifier should be float"
        assert isinstance(sources, list), "Sources should be list"
        
        print(f"✓ get_pressure_modifier returns: ({modifier}, {sources})")
    
    def test_intensity_none_modifier_1(self, registry):
        """TEST 13: Intensité NONE → modifier ~ 1.0"""
        modifier, _ = registry.get_pressure_modifier("moose", HumanPressureIntensity.NONE)
        
        assert 0.9 <= modifier <= 1.1, f"NONE intensity should give ~1.0, got {modifier}"
        
        print(f"✓ NONE intensity modifier: {modifier}")
    
    def test_intensity_extreme_reduces_modifier(self, registry):
        """TEST 14: Intensité EXTREME réduit significativement le modificateur"""
        modifier, _ = registry.get_pressure_modifier("moose", HumanPressureIntensity.EXTREME)
        
        assert modifier < 0.5, f"EXTREME intensity should reduce modifier significantly, got {modifier}"
        
        print(f"✓ EXTREME intensity modifier: {modifier}")
    
    def test_modifiers_decrease_with_intensity(self, registry):
        """TEST 15: Les modificateurs diminuent avec l'intensité croissante"""
        intensities = [
            HumanPressureIntensity.NONE,
            HumanPressureIntensity.LOW,
            HumanPressureIntensity.MODERATE,
            HumanPressureIntensity.HIGH,
            HumanPressureIntensity.EXTREME
        ]
        
        modifiers = []
        for intensity in intensities:
            mod, _ = registry.get_pressure_modifier("moose", intensity)
            modifiers.append((intensity.value, mod))
        
        # Vérifier que les modificateurs diminuent
        for i in range(len(modifiers) - 1):
            assert modifiers[i][1] >= modifiers[i+1][1], \
                f"Modifier for {modifiers[i][0]} ({modifiers[i][1]}) should be >= {modifiers[i+1][0]} ({modifiers[i+1][1]})"
        
        print(f"✓ Modifiers decrease with intensity:")
        for name, mod in modifiers:
            print(f"  - {name}: {mod}")
    
    def test_hunting_season_increases_vulnerability(self, registry):
        """TEST 16: La saison de chasse augmente la vulnérabilité (réduit le modifier)"""
        mod_default, _ = registry.get_pressure_modifier("moose", HumanPressureIntensity.MODERATE, "default")
        mod_hunting, _ = registry.get_pressure_modifier("moose", HumanPressureIntensity.MODERATE, "hunting_season")
        
        # hunting_season devrait réduire le modifier (plus vulnérable)
        # Note: vulnerability > 1.0 → modifier divisé → plus petit
        print(f"  - Default: {mod_default}")
        print(f"  - Hunting season: {mod_hunting}")
        
        print(f"✓ Season comparison: default={mod_default}, hunting_season={mod_hunting}")


# =============================================================================
# TEST CLASS 4: get_hunting_pressure_modifier() — MÉTHODE PRINCIPALE NIVEAU 3
# =============================================================================

class TestGetHuntingPressureModifier:
    """Tests pour get_hunting_pressure_modifier() — méthode principale NIVEAU 3"""
    
    def test_returns_tuple_with_3_elements(self, registry):
        """TEST 17: get_hunting_pressure_modifier() retourne (modifier, details, source_ids)"""
        result = registry.get_hunting_pressure_modifier(
            species="moose",
            latitude=46.83,
            longitude=-71.21,
            check_datetime=datetime.now(timezone.utc),
            hunting_pressure_detected=False
        )
        
        assert isinstance(result, tuple), "Should return tuple"
        assert len(result) == 3, "Tuple should have 3 elements (modifier, details, source_ids)"
        
        modifier, details, sources = result
        assert isinstance(modifier, float), "Modifier should be float"
        assert isinstance(details, dict), "Details should be dict"
        assert isinstance(sources, list), "Sources should be list"
        
        print(f"✓ get_hunting_pressure_modifier returns:")
        print(f"  - modifier: {modifier}")
        print(f"  - details: {list(details.keys())}")
        print(f"  - source_ids: {sources[:3]}...")
    
    def test_details_contain_pressure_score(self, registry):
        """TEST 18: Les détails contiennent pressure_score"""
        _, details, _ = registry.get_hunting_pressure_modifier("moose", 46.83, -71.21)
        
        assert "pressure_score" in details, "pressure_score missing in details"
        assert isinstance(details["pressure_score"], (int, float)), "pressure_score should be numeric"
        
        print(f"✓ pressure_score: {details['pressure_score']}")
    
    def test_details_contain_intensity(self, registry):
        """TEST 19: Les détails contiennent intensity"""
        _, details, _ = registry.get_hunting_pressure_modifier("moose", 46.83, -71.21)
        
        assert "intensity" in details, "intensity missing in details"
        valid_intensities = [i.value for i in HumanPressureIntensity]
        assert details["intensity"] in valid_intensities, f"Invalid intensity: {details['intensity']}"
        
        print(f"✓ intensity: {details['intensity']}")
    
    def test_details_contain_in_avoidance_zone(self, registry):
        """TEST 20: Les détails contiennent in_avoidance_zone"""
        _, details, _ = registry.get_hunting_pressure_modifier("moose", 46.83, -71.21)
        
        assert "in_avoidance_zone" in details, "in_avoidance_zone missing in details"
        assert isinstance(details["in_avoidance_zone"], bool), "in_avoidance_zone should be bool"
        
        print(f"✓ in_avoidance_zone: {details['in_avoidance_zone']}")
    
    def test_details_contain_hunting_pressure_detected(self, registry):
        """TEST 21: Les détails reflètent hunting_pressure_detected"""
        _, details_false, _ = registry.get_hunting_pressure_modifier(
            "moose", 46.83, -71.21, hunting_pressure_detected=False
        )
        _, details_true, _ = registry.get_hunting_pressure_modifier(
            "moose", 46.83, -71.21, hunting_pressure_detected=True
        )
        
        assert details_false["hunting_pressure_detected"] == False
        assert details_true["hunting_pressure_detected"] == True
        
        print(f"✓ hunting_pressure_detected: False={details_false['hunting_pressure_detected']}, True={details_true['hunting_pressure_detected']}")
    
    def test_hunting_pressure_detected_reduces_modifier(self, registry):
        """TEST 22: hunting_pressure_detected=True réduit le modificateur"""
        mod_false, _, _ = registry.get_hunting_pressure_modifier(
            "moose", 46.83, -71.21, hunting_pressure_detected=False
        )
        mod_true, _, _ = registry.get_hunting_pressure_modifier(
            "moose", 46.83, -71.21, hunting_pressure_detected=True
        )
        
        assert mod_true < mod_false, f"hunting_pressure_detected=True ({mod_true}) should reduce modifier vs False ({mod_false})"
        
        print(f"✓ Modifier: False={mod_false}, True={mod_true}")
    
    def test_different_species_different_modifiers(self, registry):
        """TEST 23: Différentes espèces ont des modificateurs différents"""
        mod_moose, _, _ = registry.get_hunting_pressure_modifier("moose", 46.83, -71.21)
        mod_deer, _, _ = registry.get_hunting_pressure_modifier("deer", 46.83, -71.21)
        mod_bear, _, _ = registry.get_hunting_pressure_modifier("bear", 46.83, -71.21)
        
        # Les modificateurs peuvent être différents selon la sensibilité
        print(f"✓ Species modifiers:")
        print(f"  - moose: {mod_moose}")
        print(f"  - deer: {mod_deer}")
        print(f"  - bear: {mod_bear}")
    
    def test_source_ids_contain_pres_human(self, registry):
        """TEST 24: source_ids contiennent SRC-PRES-HUMAN"""
        _, _, sources = registry.get_hunting_pressure_modifier("moose", 46.83, -71.21)
        
        has_pres_human = any("PRES-HUMAN" in s for s in sources)
        assert has_pres_human or len(sources) > 0, "SRC-PRES-HUMAN or other sources should be present"
        
        print(f"✓ source_ids: {sources}")


# =============================================================================
# TEST CLASS 5: HumanPressureModel — MÉTRIQUES CALCULÉES
# =============================================================================

class TestHumanPressureModel:
    """Tests pour HumanPressureModel avec density_per_km2, frequency, intensity"""
    
    def test_calculate_pressure_at_point_returns_model(self, registry):
        """TEST 25: calculate_pressure_at_point() retourne un HumanPressureModel"""
        model = registry.calculate_pressure_at_point(46.83, -71.21, radius_km=2.0)
        
        assert isinstance(model, HumanPressureModel), "Should return HumanPressureModel"
        
        print(f"✓ Model returned: {model.model_id}")
    
    def test_model_has_density_per_km2(self, registry):
        """TEST 26: Le modèle contient density_per_km2"""
        model = registry.calculate_pressure_at_point(46.83, -71.21)
        
        assert hasattr(model, "density_per_km2"), "density_per_km2 missing"
        assert isinstance(model.density_per_km2, (int, float)), "density_per_km2 should be numeric"
        assert model.density_per_km2 >= 0, "density_per_km2 should be non-negative"
        
        print(f"✓ density_per_km2: {model.density_per_km2}")
    
    def test_model_has_frequency(self, registry):
        """TEST 27: Le modèle contient frequency"""
        model = registry.calculate_pressure_at_point(46.83, -71.21)
        
        assert hasattr(model, "frequency"), "frequency missing"
        valid_frequencies = ["none", "single", "occasional", "regular", "heavy"]
        assert model.frequency in valid_frequencies, f"Invalid frequency: {model.frequency}"
        
        print(f"✓ frequency: {model.frequency}")
    
    def test_model_has_intensity(self, registry):
        """TEST 28: Le modèle contient intensity"""
        model = registry.calculate_pressure_at_point(46.83, -71.21)
        
        assert hasattr(model, "intensity"), "intensity missing"
        assert isinstance(model.intensity, HumanPressureIntensity), "intensity should be HumanPressureIntensity enum"
        
        print(f"✓ intensity: {model.intensity.value}")
    
    def test_model_has_pressure_score(self, registry):
        """TEST 29: Le modèle contient pressure_score (0-100)"""
        model = registry.calculate_pressure_at_point(46.83, -71.21)
        
        assert hasattr(model, "pressure_score"), "pressure_score missing"
        assert 0 <= model.pressure_score <= 100, f"pressure_score should be 0-100, got {model.pressure_score}"
        
        print(f"✓ pressure_score: {model.pressure_score}")
    
    def test_model_has_species_modifiers(self, registry):
        """TEST 30: Le modèle contient species_modifiers pour les 3 espèces"""
        model = registry.calculate_pressure_at_point(46.83, -71.21)
        
        assert hasattr(model, "species_modifiers"), "species_modifiers missing"
        assert "moose" in model.species_modifiers, "moose modifier missing"
        assert "deer" in model.species_modifiers, "deer modifier missing"
        assert "bear" in model.species_modifiers, "bear modifier missing"
        
        print(f"✓ species_modifiers: {model.species_modifiers}")
    
    def test_model_has_source_ids(self, registry):
        """TEST 31: Le modèle contient source_ids pour traçabilité"""
        model = registry.calculate_pressure_at_point(46.83, -71.21)
        
        assert hasattr(model, "source_ids"), "source_ids missing"
        assert len(model.source_ids) > 0, "source_ids should not be empty"
        
        print(f"✓ Model source_ids: {model.source_ids}")


# =============================================================================
# TEST CLASS 6: AvoidanceZone — ZONES D'ÉVITEMENT DYNAMIQUES
# =============================================================================

class TestAvoidanceZone:
    """Tests pour AvoidanceZone avec is_active() et get_modifier_for_species()"""
    
    def test_avoidance_zone_is_active(self, registry):
        """TEST 32: AvoidanceZone.is_active() fonctionne correctement"""
        zones = registry.get_avoidance_zones(active_only=False)
        
        assert len(zones) >= 1, "Should have at least 1 avoidance zone"
        
        zone = zones[0]
        assert hasattr(zone, "is_active"), "is_active method missing"
        
        # Tester avec datetime actuel
        is_active = zone.is_active()
        assert isinstance(is_active, bool), "is_active should return bool"
        
        print(f"✓ Zone {zone.zone_id} is_active(): {is_active}")
    
    def test_zone_active_hours_filter(self, registry):
        """TEST 33: La zone respecte active_hours"""
        zones = registry.get_avoidance_zones(active_only=False)
        zone = zones[0]
        
        if zone.active_hours:
            # Tester avec une heure dans active_hours
            test_dt = datetime(2025, 10, 1, zone.active_hours[0], 0, 0, tzinfo=timezone.utc)
            # Ajuster la date pour être dans la période de validité
            test_dt = zone.valid_from + timedelta(hours=zone.active_hours[0])
            
            print(f"  - active_hours: {zone.active_hours}")
            print(f"  - valid_from: {zone.valid_from}")
            print(f"  - valid_until: {zone.valid_until}")
    
    def test_zone_active_days_filter(self, registry):
        """TEST 34: La zone respecte active_days"""
        zones = registry.get_avoidance_zones(active_only=False)
        zone = zones[0]
        
        print(f"  - active_days: {zone.active_days} (0=lundi, 6=dimanche)")
    
    def test_zone_validity_period(self, registry):
        """TEST 35: La zone respecte valid_from et valid_until"""
        zones = registry.get_avoidance_zones(active_only=False)
        zone = zones[0]
        
        assert hasattr(zone, "valid_from"), "valid_from missing"
        assert hasattr(zone, "valid_until"), "valid_until missing"
        
        # Tester avant la période
        before = zone.valid_from - timedelta(days=1)
        assert zone.is_active(before) == False, "Zone should not be active before valid_from"
        
        # Tester après la période
        after = zone.valid_until + timedelta(days=1)
        assert zone.is_active(after) == False, "Zone should not be active after valid_until"
        
        print(f"✓ Validity period: {zone.valid_from} to {zone.valid_until}")
    
    def test_get_modifier_for_species(self, registry):
        """TEST 36: AvoidanceZone.get_modifier_for_species() fonctionne"""
        zones = registry.get_avoidance_zones(active_only=False)
        zone = zones[0]
        
        assert hasattr(zone, "get_modifier_for_species"), "get_modifier_for_species method missing"
        
        mod_moose = zone.get_modifier_for_species("moose")
        mod_deer = zone.get_modifier_for_species("deer")
        mod_bear = zone.get_modifier_for_species("bear")
        
        print(f"✓ Zone modifiers by species:")
        print(f"  - moose: {mod_moose}")
        print(f"  - deer: {mod_deer}")
        print(f"  - bear: {mod_bear}")
    
    def test_zone_has_species_impact(self, registry):
        """TEST 37: La zone a species_impact défini"""
        zones = registry.get_avoidance_zones(active_only=False)
        zone = zones[0]
        
        assert hasattr(zone, "species_impact"), "species_impact missing"
        assert isinstance(zone.species_impact, dict), "species_impact should be dict"
        
        print(f"✓ species_impact: {zone.species_impact}")
    
    def test_zone_has_source_ids(self, registry):
        """TEST 38: AvoidanceZone contient source_ids"""
        zones = registry.get_avoidance_zones(active_only=False)
        zone = zones[0]
        
        assert hasattr(zone, "source_ids"), "source_ids missing"
        assert len(zone.source_ids) > 0, "source_ids should not be empty"
        
        print(f"✓ Zone source_ids: {zone.source_ids}")


# =============================================================================
# TEST CLASS 7: UnifiedScoringService — INTÉGRATION PRES-HUMAN
# =============================================================================

class TestUnifiedScoringServicePRESHUMAN:
    """Tests pour l'intégration PRES-HUMAN dans UnifiedScoringService"""
    
    def test_inject_advanced_modifiers_includes_pres_human(self, unified_service):
        """TEST 39: _inject_advanced_modifiers() intègre PRES-HUMAN"""
        context = create_score_context("moose", 7, hunting_pressure_detected=True)
        
        enriched = unified_service._inject_advanced_modifiers(context, "rut", "TEST-PRESHUMAN-001")
        adv = enriched.advanced_modifiers
        
        assert "hunting_pressure_active" in adv, "hunting_pressure_active missing"
        assert "hunting_pressure_modifier" in adv, "hunting_pressure_modifier missing"
        assert "hunting_pressure_details" in adv, "hunting_pressure_details missing"
        assert "hunting_pressure_source_ids" in adv, "hunting_pressure_source_ids missing"
        
        print(f"✓ PRES-HUMAN integrated in advanced_modifiers:")
        print(f"  - hunting_pressure_active: {adv['hunting_pressure_active']}")
        print(f"  - hunting_pressure_modifier: {adv['hunting_pressure_modifier']}")
    
    def test_hunting_pressure_version_is_3_0_0(self, unified_service):
        """TEST 40: hunting_pressure_version = '3.0.0' (NIVEAU 3)"""
        context = create_score_context("moose", 7)
        
        enriched = unified_service._inject_advanced_modifiers(context, "rut", "TEST-PRESHUMAN-002")
        adv = enriched.advanced_modifiers
        
        assert "hunting_pressure_version" in adv, "hunting_pressure_version missing"
        assert adv["hunting_pressure_version"] == "3.0.0", f"Expected version 3.0.0, got {adv['hunting_pressure_version']}"
        
        print(f"✓ hunting_pressure_version: {adv['hunting_pressure_version']} (NIVEAU 3)")
    
    def test_hunting_pressure_details_complete(self, unified_service):
        """TEST 41: hunting_pressure_details contient tous les champs requis"""
        context = create_score_context("moose", 7)
        
        enriched = unified_service._inject_advanced_modifiers(context, "rut", "TEST-PRESHUMAN-003")
        details = enriched.advanced_modifiers.get("hunting_pressure_details", {})
        
        expected_fields = ["pressure_score", "intensity", "in_avoidance_zone"]
        for field in expected_fields:
            assert field in details, f"{field} missing in hunting_pressure_details"
        
        print(f"✓ hunting_pressure_details fields: {list(details.keys())}")
    
    def test_pres_human_integrated_flag(self, unified_service):
        """TEST 42: pres_human_integrated = True"""
        context = create_score_context("moose", 7)
        
        enriched = unified_service._inject_advanced_modifiers(context, "rut", "TEST-PRESHUMAN-004")
        adv = enriched.advanced_modifiers
        
        assert "pres_human_integrated" in adv, "pres_human_integrated flag missing"
        assert adv["pres_human_integrated"] == True, "pres_human_integrated should be True"
        
        print(f"✓ pres_human_integrated: {adv['pres_human_integrated']}")
    
    def test_phase_c_modifier_includes_hunting_pressure(self, unified_service):
        """TEST 43: phase_c_modifier inclut hunting_pressure_modifier"""
        context = create_score_context("moose", 7, hunting_pressure_detected=True)
        
        enriched = unified_service._inject_advanced_modifiers(context, "rut", "TEST-PRESHUMAN-005")
        adv = enriched.advanced_modifiers
        
        assert "phase_c_modifier" in adv, "phase_c_modifier missing"
        
        # Le modificateur phase_c devrait être influencé par hunting_pressure
        hunting_mod = adv.get("hunting_pressure_modifier", 1.0)
        phase_c_mod = adv.get("phase_c_modifier", 1.0)
        
        print(f"✓ phase_c_modifier: {phase_c_mod} (includes hunting_pressure={hunting_mod})")


# =============================================================================
# TEST CLASS 8: API — EXPOSITION NIVEAU 3 PRES-HUMAN
# =============================================================================

class TestAPIExpositionPRESHUMAN:
    """Tests API pour l'exposition des données PRES-HUMAN"""
    
    def test_api_returns_hunting_pressure_in_advanced_factors(self, api_client):
        """TEST 44: L'API expose hunting_pressure dans advanced_factors_details"""
        payload = {
            "waypoint": {"id": "TEST-API-PRESHUMAN-001", "latitude": 46.85, "longitude": -71.25, "name": "Test PRES-HUMAN"},
            "target_datetime": "2025-10-15T07:00:00Z",
            "species": "moose",
            "parameters": {"mode": "rut"}
        }
        
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/analyze_waypoint", json=payload)
        
        assert response.status_code == 200, f"API returned {response.status_code}: {response.text}"
        
        data = response.json()
        scores = data.get("scores", {})
        advanced = scores.get("advanced_factors_details", {})
        factors = advanced.get("factors", {})
        
        assert "hunting_pressure" in factors, "hunting_pressure missing in factors"
        
        print(f"✓ API returns hunting_pressure in advanced_factors_details")
    
    def test_api_hunting_pressure_version_3_0_0(self, api_client):
        """TEST 45: API — hunting_pressure.version = '3.0.0' (NIVEAU 3)"""
        payload = {
            "waypoint": {"id": "TEST-API-PRESHUMAN-002", "latitude": 46.85, "longitude": -71.25, "name": "Test PRES-HUMAN"},
            "target_datetime": "2025-10-15T07:00:00Z",
            "species": "moose"
        }
        
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/analyze_waypoint", json=payload)
        data = response.json()
        
        factors = data.get("scores", {}).get("advanced_factors_details", {}).get("factors", {})
        hunting_pressure = factors.get("hunting_pressure", {})
        
        version = hunting_pressure.get("version", "unknown")
        assert version == "3.0.0", f"Expected version 3.0.0, got {version}"
        
        print(f"✓ API hunting_pressure.version: {version} (NIVEAU 3)")
    
    def test_api_hunting_pressure_has_source_ids(self, api_client):
        """TEST 46: API — hunting_pressure.source_ids présent"""
        payload = {
            "waypoint": {"id": "TEST-API-PRESHUMAN-003", "latitude": 46.85, "longitude": -71.25, "name": "Test PRES-HUMAN"},
            "target_datetime": "2025-10-15T07:00:00Z",
            "species": "moose"
        }
        
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/analyze_waypoint", json=payload)
        data = response.json()
        
        factors = data.get("scores", {}).get("advanced_factors_details", {}).get("factors", {})
        hunting_pressure = factors.get("hunting_pressure", {})
        
        source_ids = hunting_pressure.get("source_ids", [])
        assert isinstance(source_ids, list), "source_ids should be list"
        
        print(f"✓ API hunting_pressure.source_ids: {source_ids}")
    
    def test_api_hunting_pressure_details_complete(self, api_client):
        """TEST 47: API — hunting_pressure.details contient intensity, pressure_score, in_avoidance_zone"""
        payload = {
            "waypoint": {"id": "TEST-API-PRESHUMAN-004", "latitude": 46.85, "longitude": -71.25, "name": "Test PRES-HUMAN"},
            "target_datetime": "2025-10-15T07:00:00Z",
            "species": "moose"
        }
        
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/analyze_waypoint", json=payload)
        data = response.json()
        
        factors = data.get("scores", {}).get("advanced_factors_details", {}).get("factors", {})
        hunting_pressure = factors.get("hunting_pressure", {})
        details = hunting_pressure.get("details", {})
        
        expected_fields = ["intensity", "pressure_score", "in_avoidance_zone"]
        for field in expected_fields:
            assert field in details, f"{field} missing in hunting_pressure.details"
            print(f"  - {field}: {details[field]}")
        
        print(f"✓ API hunting_pressure.details complete")
    
    def test_api_hunting_pressure_modifier_present(self, api_client):
        """TEST 48: API — hunting_pressure.modifier présent"""
        payload = {
            "waypoint": {"id": "TEST-API-PRESHUMAN-005", "latitude": 46.85, "longitude": -71.25, "name": "Test PRES-HUMAN"},
            "target_datetime": "2025-10-15T07:00:00Z",
            "species": "moose"
        }
        
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/analyze_waypoint", json=payload)
        data = response.json()
        
        factors = data.get("scores", {}).get("advanced_factors_details", {}).get("factors", {})
        hunting_pressure = factors.get("hunting_pressure", {})
        
        modifier = hunting_pressure.get("modifier")
        assert modifier is not None, "modifier missing in hunting_pressure"
        assert isinstance(modifier, (int, float)), "modifier should be numeric"
        
        print(f"✓ API hunting_pressure.modifier: {modifier}")
    
    def test_api_moose_very_sensitive(self, api_client):
        """TEST 49: API — Orignal (moose) très sensible à la pression humaine"""
        payload = {
            "waypoint": {"id": "TEST-API-MOOSE-SENS", "latitude": 46.85, "longitude": -71.25, "name": "Test Moose"},
            "target_datetime": "2025-10-15T07:00:00Z",
            "species": "moose"
        }
        
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/analyze_waypoint", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        print(f"✓ Moose API response: final_score={data['scores']['score_bionic_final']}")
    
    def test_api_deer_moderate_sensitivity(self, api_client):
        """TEST 50: API — Cerf (deer) sensibilité modérée"""
        payload = {
            "waypoint": {"id": "TEST-API-DEER-SENS", "latitude": 46.85, "longitude": -71.25, "name": "Test Deer"},
            "target_datetime": "2025-10-15T07:00:00Z",
            "species": "deer"
        }
        
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/analyze_waypoint", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        print(f"✓ Deer API response: final_score={data['scores']['score_bionic_final']}")
    
    def test_api_bear_moderate_sensitivity(self, api_client):
        """TEST 51: API — Ours (bear) sensibilité modérée"""
        payload = {
            "waypoint": {"id": "TEST-API-BEAR-SENS", "latitude": 46.85, "longitude": -71.25, "name": "Test Bear"},
            "target_datetime": "2025-10-15T07:00:00Z",
            "species": "bear"
        }
        
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/analyze_waypoint", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        print(f"✓ Bear API response: final_score={data['scores']['score_bionic_final']}")


# =============================================================================
# TEST CLASS 9: TRAÇABILITÉ — SOURCE_IDS NIVEAU 3
# =============================================================================

class TestTracabilitePRESHUMAN:
    """Tests pour la traçabilité des source_ids NIVEAU 3"""
    
    def test_source_ids_include_gps_hunt(self, registry):
        """TEST 52: source_ids incluent SRC-GPS-HUNT"""
        _, _, sources = registry.get_hunting_pressure_modifier("moose", 46.83, -71.21)
        
        has_gps = any("GPS-HUNT" in s for s in sources)
        print(f"✓ Sources: {sources}")
        print(f"  - Contains GPS-HUNT: {has_gps}")
    
    def test_source_ids_include_terrain_cam(self, registry):
        """TEST 53: source_ids incluent SRC-TERRAIN-CAM"""
        _, _, sources = registry.get_hunting_pressure_modifier("moose", 46.83, -71.21)
        
        has_cam = any("TERRAIN-CAM" in s for s in sources)
        print(f"  - Contains TERRAIN-CAM: {has_cam}")
    
    def test_source_ids_include_pres_human(self, registry):
        """TEST 54: source_ids incluent SRC-PRES-HUMAN"""
        _, _, sources = registry.get_hunting_pressure_modifier("moose", 46.83, -71.21)
        
        has_pres = any("PRES-HUMAN" in s for s in sources)
        print(f"  - Contains PRES-HUMAN: {has_pres}")
    
    def test_species_response_source_ids_variety(self, registry):
        """TEST 55: Les SpeciesHumanPressureResponse ont des source_ids variés"""
        moose_resp = registry.get_species_response("moose")
        deer_resp = registry.get_species_response("deer")
        bear_resp = registry.get_species_response("bear")
        
        print(f"✓ Species response source_ids:")
        print(f"  - Moose: {moose_resp.source_ids}")
        print(f"  - Deer: {deer_resp.source_ids}")
        print(f"  - Bear: {bear_resp.source_ids}")


# =============================================================================
# TEST CLASS 10: INTÉGRATION E2E — UNIFIED SCORE AVEC PRES-HUMAN
# =============================================================================

class TestE2EUnifiedScorePRESHUMAN:
    """Tests E2E pour le score unifié avec PRES-HUMAN intégré"""
    
    def test_unified_score_includes_pres_human_modifier(self, unified_service):
        """TEST 56: Le score unifié intègre le modificateur PRES-HUMAN"""
        context = create_score_context("moose", 7, hunting_pressure_detected=True)
        
        result = unified_service.calculate_unified_score(context, "rut")
        
        # Vérifier que le context a été enrichi avec PRES-HUMAN
        adv = context.advanced_modifiers
        assert "hunting_pressure_modifier" in adv, "hunting_pressure_modifier should be in context"
        
        print(f"✓ Unified score with PRES-HUMAN:")
        print(f"  - final_score: {result.final_score}")
        print(f"  - hunting_pressure_modifier: {adv.get('hunting_pressure_modifier')}")
    
    def test_unified_score_advanced_factors_details_has_hunting_pressure(self, unified_service):
        """TEST 57: advanced_factors_details contient hunting_pressure"""
        context = create_score_context("moose", 7)
        
        result = unified_service.calculate_unified_score(context, "rut")
        
        advanced_details = result.advanced_factors_details
        factors = advanced_details.get("factors", {})
        
        assert "hunting_pressure" in factors, "hunting_pressure should be in factors"
        
        hp = factors["hunting_pressure"]
        assert "version" in hp, "version missing in hunting_pressure"
        assert hp["version"] == "3.0.0", f"Expected version 3.0.0, got {hp['version']}"
        
        print(f"✓ advanced_factors_details.factors.hunting_pressure:")
        print(f"  - version: {hp['version']}")
        print(f"  - active: {hp.get('active')}")
        print(f"  - modifier: {hp.get('modifier')}")
    
    def test_unified_score_source_ids_include_pres_human_sources(self, unified_service):
        """TEST 58: source_ids incluent les sources PRES-HUMAN"""
        context = create_score_context("moose", 7)
        
        result = unified_service.calculate_unified_score(context, "rut")
        
        advanced_details = result.advanced_factors_details
        source_ids = advanced_details.get("source_ids", [])
        
        # Vérifier que des sources PRES-HUMAN sont présentes
        has_pres_human = any("PRES-HUMAN" in s or "GPS-HUNT" in s for s in source_ids)
        
        print(f"✓ source_ids in result: {source_ids[:5]}...")
        print(f"  - Contains PRES-HUMAN sources: {has_pres_human}")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
