"""
BIONIC ENGINE — Scoring Services — Tests Unitaires
===================================================
Tests minimalistes pour la structure des 9 services de scoring.

COUVERTURE:
- Instanciation de chaque service
- Validation des interfaces
- Vérification des data contracts
- Test de calculate() avec contexte minimal

Conformité: G-QA | BIONIC V5
"""

import pytest
from datetime import datetime
from zoneinfo import ZoneInfo

# Import du package de scoring
import sys
sys.path.insert(0, '/app/backend')

from modules.bionic_engine_p0.services.scoring import (
    # Base
    ScoreResult,
    ScoreComponent,
    ScoreContext,
    ScoreWeight,
    ScoreLevel,
    ScoreCategory,
    # Services (9 scores)
    ScoreProbabilityService,
    ScoreHabitatService,
    ScorePressureService,
    ScoreWeatherService,
    ScoreBehaviorService,
    ScoreMultiFactorService,
    ScoreDensityService,
    ScoreRiskService,
    ScoreMobilityService
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def valid_context():
    """Contexte valide pour les tests."""
    tz = ZoneInfo("America/Montreal")
    return ScoreContext(
        waypoint_id="WP-TEST-001",
        latitude=46.8139,
        longitude=-71.2082,
        target_datetime=datetime.now(tz),
        species="moose",
        region="CA-QC",
        search_radius_km=3.0
    )


@pytest.fixture
def all_services():
    """Liste de tous les services de scoring."""
    return [
        ScoreProbabilityService(),
        ScoreHabitatService(),
        ScorePressureService(),
        ScoreWeatherService(),
        ScoreBehaviorService(),
        ScoreMultiFactorService(),
        ScoreDensityService(),
        ScoreRiskService(),
        ScoreMobilityService()
    ]


# =============================================================================
# TESTS: Data Contracts
# =============================================================================

class TestDataContracts:
    """Tests pour les data contracts."""
    
    def test_score_level_enum(self):
        """Test enum ScoreLevel."""
        assert ScoreLevel.EXCELLENT.value == "excellent"
        assert ScoreLevel.GOOD.value == "good"
        assert ScoreLevel.MODERATE.value == "moderate"
        assert ScoreLevel.POOR.value == "poor"
        assert ScoreLevel.VERY_POOR.value == "very_poor"
    
    def test_score_category_enum(self):
        """Test enum ScoreCategory avec 9 catégories."""
        categories = [
            ScoreCategory.PROBABILITY,
            ScoreCategory.HABITAT,
            ScoreCategory.PRESSURE,
            ScoreCategory.WEATHER,
            ScoreCategory.BEHAVIOR,
            ScoreCategory.MULTIFACTOR,
            ScoreCategory.DENSITY,
            ScoreCategory.RISK,
            ScoreCategory.MOBILITY
        ]
        assert len(categories) == 9
    
    def test_score_context_creation(self, valid_context):
        """Test création ScoreContext."""
        assert valid_context.waypoint_id == "WP-TEST-001"
        assert valid_context.species == "moose"
        assert valid_context.region == "CA-QC"
    
    def test_score_context_serialization(self, valid_context):
        """Test sérialisation ScoreContext."""
        data = valid_context.to_dict()
        assert "waypoint_id" in data
        assert "latitude" in data
        assert "longitude" in data
        assert "species" in data
    
    def test_score_weight_creation(self):
        """Test création ScoreWeight."""
        weight = ScoreWeight(
            category=ScoreCategory.PROBABILITY,
            weight=0.15,
            description="Test weight"
        )
        assert weight.weight == 0.15
        data = weight.to_dict()
        assert data["weight"] == 0.15
    
    def test_score_component_creation(self):
        """Test création ScoreComponent."""
        component = ScoreComponent(
            name="test_component",
            value=75.0,
            weight=0.5,
            weighted_value=37.5,
            description="Test component",
            factors=["Factor 1", "Factor 2"]
        )
        assert component.value == 75.0
        data = component.to_dict()
        assert data["name"] == "test_component"
    
    def test_score_result_get_level(self):
        """Test détermination niveau depuis valeur."""
        assert ScoreResult.get_level_from_value(90) == ScoreLevel.EXCELLENT
        assert ScoreResult.get_level_from_value(75) == ScoreLevel.GOOD
        assert ScoreResult.get_level_from_value(55) == ScoreLevel.MODERATE
        assert ScoreResult.get_level_from_value(35) == ScoreLevel.POOR
        assert ScoreResult.get_level_from_value(15) == ScoreLevel.VERY_POOR


# =============================================================================
# TESTS: Service Instantiation
# =============================================================================

class TestServiceInstantiation:
    """Tests d'instanciation des 9 services."""
    
    def test_score_probability_service(self):
        """Test instanciation ScoreProbabilityService."""
        service = ScoreProbabilityService()
        assert service.category == ScoreCategory.PROBABILITY
        assert service.weight.weight == 0.15
    
    def test_score_habitat_service(self):
        """Test instanciation ScoreHabitatService."""
        service = ScoreHabitatService()
        assert service.category == ScoreCategory.HABITAT
        assert service.weight.weight == 0.12
    
    def test_score_pressure_service(self):
        """Test instanciation ScorePressureService."""
        service = ScorePressureService()
        assert service.category == ScoreCategory.PRESSURE
        assert service.weight.weight == 0.10
    
    def test_score_weather_service(self):
        """Test instanciation ScoreWeatherService."""
        service = ScoreWeatherService()
        assert service.category == ScoreCategory.WEATHER
        assert service.weight.weight == 0.12
    
    def test_score_behavior_service(self):
        """Test instanciation ScoreBehaviorService."""
        service = ScoreBehaviorService()
        assert service.category == ScoreCategory.BEHAVIOR
        assert service.weight.weight == 0.12
    
    def test_score_multifactor_service(self):
        """Test instanciation ScoreMultiFactorService."""
        service = ScoreMultiFactorService()
        assert service.category == ScoreCategory.MULTIFACTOR
        assert service.weight.weight == 0.10
    
    def test_score_density_service(self):
        """Test instanciation ScoreDensityService."""
        service = ScoreDensityService()
        assert service.category == ScoreCategory.DENSITY
        assert service.weight.weight == 0.10
    
    def test_score_risk_service(self):
        """Test instanciation ScoreRiskService."""
        service = ScoreRiskService()
        assert service.category == ScoreCategory.RISK
        assert service.weight.weight == 0.08
    
    def test_score_mobility_service(self):
        """Test instanciation ScoreMobilityService."""
        service = ScoreMobilityService()
        assert service.category == ScoreCategory.MOBILITY
        assert service.weight.weight == 0.11


# =============================================================================
# TESTS: Interface Validation
# =============================================================================

class TestServiceInterfaces:
    """Tests des interfaces communes."""
    
    def test_all_services_have_category(self, all_services):
        """Tous les services ont une catégorie."""
        for service in all_services:
            assert hasattr(service, 'category')
            assert isinstance(service.category, ScoreCategory)
    
    def test_all_services_have_weight(self, all_services):
        """Tous les services ont une pondération."""
        for service in all_services:
            assert hasattr(service, 'weight')
            assert isinstance(service.weight, ScoreWeight)
            assert 0 < service.weight.weight <= 1
    
    def test_all_services_have_calculate(self, all_services):
        """Tous les services ont la méthode calculate."""
        for service in all_services:
            assert hasattr(service, 'calculate')
            assert callable(service.calculate)
    
    def test_all_services_have_validate_context(self, all_services):
        """Tous les services ont la méthode validate_context."""
        for service in all_services:
            assert hasattr(service, 'validate_context')
            assert callable(service.validate_context)
    
    def test_weights_sum_approximately_one(self, all_services):
        """La somme des pondérations est proche de 1."""
        total_weight = sum(s.weight.weight for s in all_services)
        # Tolérance de 0.01
        assert 0.99 <= total_weight <= 1.01, f"Total weight: {total_weight}"


# =============================================================================
# TESTS: Calculate Method
# =============================================================================

class TestCalculateMethod:
    """Tests de la méthode calculate pour chaque service."""
    
    def test_probability_calculate(self, valid_context):
        """Test calculate pour ScoreProbabilityService."""
        service = ScoreProbabilityService()
        result = service.calculate(valid_context)
        
        assert isinstance(result, ScoreResult)
        assert result.category == ScoreCategory.PROBABILITY
        assert 0 <= result.value <= 100
        assert len(result.components) > 0
    
    def test_habitat_calculate(self, valid_context):
        """Test calculate pour ScoreHabitatService."""
        service = ScoreHabitatService()
        result = service.calculate(valid_context)
        
        assert isinstance(result, ScoreResult)
        assert result.category == ScoreCategory.HABITAT
        assert len(result.components) == 4  # 4 composants définis
    
    def test_pressure_calculate(self, valid_context):
        """Test calculate pour ScorePressureService."""
        service = ScorePressureService()
        result = service.calculate(valid_context)
        
        assert isinstance(result, ScoreResult)
        assert result.category == ScoreCategory.PRESSURE
    
    def test_weather_calculate(self, valid_context):
        """Test calculate pour ScoreWeatherService."""
        service = ScoreWeatherService()
        result = service.calculate(valid_context)
        
        assert isinstance(result, ScoreResult)
        assert result.category == ScoreCategory.WEATHER
        assert len(result.components) == 5  # 5 composants définis
    
    def test_behavior_calculate(self, valid_context):
        """Test calculate pour ScoreBehaviorService."""
        service = ScoreBehaviorService()
        result = service.calculate(valid_context)
        
        assert isinstance(result, ScoreResult)
        assert result.category == ScoreCategory.BEHAVIOR
    
    def test_multifactor_calculate(self, valid_context):
        """Test calculate pour ScoreMultiFactorService."""
        service = ScoreMultiFactorService()
        result = service.calculate(valid_context)
        
        assert isinstance(result, ScoreResult)
        assert result.category == ScoreCategory.MULTIFACTOR
    
    def test_density_calculate(self, valid_context):
        """Test calculate pour ScoreDensityService."""
        service = ScoreDensityService()
        result = service.calculate(valid_context)
        
        assert isinstance(result, ScoreResult)
        assert result.category == ScoreCategory.DENSITY
    
    def test_risk_calculate(self, valid_context):
        """Test calculate pour ScoreRiskService."""
        service = ScoreRiskService()
        result = service.calculate(valid_context)
        
        assert isinstance(result, ScoreResult)
        assert result.category == ScoreCategory.RISK
    
    def test_mobility_calculate(self, valid_context):
        """Test calculate pour ScoreMobilityService."""
        service = ScoreMobilityService()
        result = service.calculate(valid_context)
        
        assert isinstance(result, ScoreResult)
        assert result.category == ScoreCategory.MOBILITY
    
    def test_all_services_return_valid_result(self, all_services, valid_context):
        """Tous les services retournent un ScoreResult valide."""
        for service in all_services:
            result = service.calculate(valid_context)
            
            assert isinstance(result, ScoreResult)
            assert result.score_name is not None
            assert 0 <= result.value <= 100
            assert isinstance(result.level, ScoreLevel)
            assert result.legal_compliant is True


# =============================================================================
# TESTS: Context Validation
# =============================================================================

class TestContextValidation:
    """Tests de validation du contexte."""
    
    def test_valid_context_passes(self, all_services, valid_context):
        """Contexte valide passe la validation."""
        for service in all_services:
            assert service.validate_context(valid_context) is True
    
    def test_invalid_waypoint_id(self, all_services):
        """Waypoint ID vide = invalide."""
        tz = ZoneInfo("America/Montreal")
        invalid_context = ScoreContext(
            waypoint_id="",  # Vide
            latitude=46.8,
            longitude=-71.2,
            target_datetime=datetime.now(tz),
            species="moose"
        )
        
        for service in all_services:
            assert service.validate_context(invalid_context) is False
    
    def test_invalid_latitude(self, all_services):
        """Latitude hors bornes = invalide."""
        tz = ZoneInfo("America/Montreal")
        invalid_context = ScoreContext(
            waypoint_id="WP-001",
            latitude=100.0,  # Hors bornes
            longitude=-71.2,
            target_datetime=datetime.now(tz),
            species="moose"
        )
        
        for service in all_services:
            assert service.validate_context(invalid_context) is False
    
    def test_invalid_species(self, all_services):
        """Espèce vide = invalide."""
        tz = ZoneInfo("America/Montreal")
        invalid_context = ScoreContext(
            waypoint_id="WP-001",
            latitude=46.8,
            longitude=-71.2,
            target_datetime=datetime.now(tz),
            species=""  # Vide
        )
        
        for service in all_services:
            assert service.validate_context(invalid_context) is False


# =============================================================================
# TESTS: Result Serialization
# =============================================================================

class TestResultSerialization:
    """Tests de sérialisation des résultats."""
    
    def test_result_to_dict(self, all_services, valid_context):
        """Tous les résultats se sérialisent en dict."""
        for service in all_services:
            result = service.calculate(valid_context)
            data = result.to_dict()
            
            assert isinstance(data, dict)
            assert "category" in data
            assert "score_name" in data
            assert "value" in data
            assert "level" in data
            assert "components" in data
            assert "legal_compliant" in data
            assert "legal_badge" in data


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
