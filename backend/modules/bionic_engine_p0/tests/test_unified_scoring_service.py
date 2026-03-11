"""
BIONIC ENGINE — Unified Scoring Service — Tests Unitaires
==========================================================
Tests pour le service d'orchestration UnifiedScoringService.

COUVERTURE:
- Instanciation et configuration
- Orchestration des 9 services
- Agrégation des scores
- Ajustement temporel
- Conformité aux heures légales
- Sérialisation des résultats

Conformité: G-QA | BIONIC V5
"""

import pytest
from datetime import datetime, time
from zoneinfo import ZoneInfo

import sys
sys.path.insert(0, '/app/backend')

from modules.bionic_engine_p0.services.unified_scoring_service import (
    UnifiedScoringService,
    get_unified_scoring_service,
    UnifiedScoreResult,
    ScoreBreakdown,
    TemporalAdjustment
)

from modules.bionic_engine_p0.services.scoring import (
    ScoreContext,
    ScoreLevel,
    ScoreCategory
)

from modules.bionic_engine_p0.services.legal_hours_service import LegalStatus


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def service():
    """Instance du service pour les tests."""
    return UnifiedScoringService()


@pytest.fixture
def legal_context():
    """Contexte avec heure légale (matin)."""
    tz = ZoneInfo("America/Montreal")
    # 8h du matin en été = légal
    target_dt = datetime.combine(
        datetime.now(tz).date(),
        time(8, 0),
        tzinfo=tz
    )
    return ScoreContext(
        waypoint_id="WP-TEST-001",
        latitude=46.8139,
        longitude=-71.2082,
        target_datetime=target_dt,
        species="moose",
        region="CA-QC",
        search_radius_km=3.0
    )


@pytest.fixture
def illegal_context():
    """Contexte avec heure illégale (nuit)."""
    tz = ZoneInfo("America/Montreal")
    # 2h du matin = illégal
    target_dt = datetime.combine(
        datetime.now(tz).date(),
        time(2, 0),
        tzinfo=tz
    )
    return ScoreContext(
        waypoint_id="WP-TEST-002",
        latitude=46.8139,
        longitude=-71.2082,
        target_datetime=target_dt,
        species="moose",
        region="CA-QC"
    )


@pytest.fixture
def dawn_context():
    """Contexte à l'aube (heure optimale légale)."""
    tz = ZoneInfo("America/Montreal")
    # 7h du matin = légal même en hiver, proche de l'aube
    target_dt = datetime.combine(
        datetime.now(tz).date(),
        time(7, 0),
        tzinfo=tz
    )
    return ScoreContext(
        waypoint_id="WP-TEST-003",
        latitude=46.8139,
        longitude=-71.2082,
        target_datetime=target_dt,
        species="deer",
        region="CA-QC"
    )


# =============================================================================
# TESTS: Instanciation et Configuration
# =============================================================================

class TestServiceInstantiation:
    """Tests d'instanciation du service."""
    
    def test_service_creation(self, service):
        """Test création du service."""
        assert service is not None
        assert isinstance(service, UnifiedScoringService)
    
    def test_service_has_9_services(self, service):
        """Le service a exactement 9 sous-services."""
        assert service.services_count == 9
    
    def test_services_list_readonly(self, service):
        """La liste des services est une copie (lecture seule)."""
        services = service.services
        original_count = service.services_count
        services.clear()
        assert service.services_count == original_count
    
    def test_total_weight_is_one(self, service):
        """La somme des pondérations est ~1.0."""
        total = service.get_total_weight()
        assert 0.99 <= total <= 1.01, f"Total weight: {total}"
    
    def test_singleton_pattern(self):
        """Test du pattern singleton."""
        service1 = get_unified_scoring_service()
        service2 = get_unified_scoring_service()
        assert service1 is service2


# =============================================================================
# TESTS: Orchestration des 9 Services
# =============================================================================

class TestOrchestration:
    """Tests d'orchestration des services."""
    
    def test_calculate_returns_result(self, service, legal_context):
        """calculate() retourne un UnifiedScoreResult."""
        result = service.calculate_unified_score(legal_context)
        assert isinstance(result, UnifiedScoreResult)
    
    def test_result_has_all_breakdowns(self, service, legal_context):
        """Le résultat contient les 9 breakdowns."""
        result = service.calculate_unified_score(legal_context)
        assert len(result.score_breakdown) == 9
    
    def test_all_categories_present(self, service, legal_context):
        """Toutes les 9 catégories sont présentes."""
        result = service.calculate_unified_score(legal_context)
        categories = {b.category for b in result.score_breakdown}
        
        expected = {
            ScoreCategory.PROBABILITY,
            ScoreCategory.HABITAT,
            ScoreCategory.PRESSURE,
            ScoreCategory.WEATHER,
            ScoreCategory.BEHAVIOR,
            ScoreCategory.MULTIFACTOR,
            ScoreCategory.DENSITY,
            ScoreCategory.RISK,
            ScoreCategory.MOBILITY
        }
        assert categories == expected
    
    def test_breakdowns_have_weights(self, service, legal_context):
        """Chaque breakdown a une pondération."""
        result = service.calculate_unified_score(legal_context)
        
        for breakdown in result.score_breakdown:
            assert 0 < breakdown.weight <= 1
            assert breakdown.weighted_value == breakdown.raw_value * breakdown.weight


# =============================================================================
# TESTS: Agrégation des Scores
# =============================================================================

class TestScoreAggregation:
    """Tests d'agrégation des scores."""
    
    def test_raw_score_in_range(self, service, legal_context):
        """Le score brut est entre 0 et 100."""
        result = service.calculate_unified_score(legal_context)
        assert 0 <= result.raw_aggregated_score <= 100
    
    def test_final_score_in_range(self, service, legal_context):
        """Le score final est entre 0 et 100."""
        result = service.calculate_unified_score(legal_context)
        assert 0 <= result.final_score <= 100
    
    def test_final_level_matches_score(self, service, legal_context):
        """Le niveau final correspond au score."""
        result = service.calculate_unified_score(legal_context)
        expected_level = UnifiedScoreResult.get_level_from_value(result.final_score)
        assert result.final_level == expected_level
    
    def test_weighted_sum_calculation(self, service, legal_context):
        """Vérifie le calcul de la somme pondérée."""
        result = service.calculate_unified_score(legal_context)
        
        # Calculer manuellement
        total_weighted = sum(b.weighted_value for b in result.score_breakdown)
        total_weight = sum(b.weight for b in result.score_breakdown)
        expected_raw = total_weighted / total_weight
        
        # Tolérance de 0.1 pour les arrondis
        assert abs(result.raw_aggregated_score - expected_raw) < 0.1


# =============================================================================
# TESTS: Ajustement Temporel
# =============================================================================

class TestTemporalAdjustment:
    """Tests de l'ajustement temporel."""
    
    def test_legal_time_has_positive_factor(self, service, legal_context):
        """Heure légale = temporal_factor > 0."""
        result = service.calculate_unified_score(legal_context)
        assert result.temporal_adjustment.temporal_factor > 0
    
    def test_legal_time_is_legal(self, service, legal_context):
        """Heure légale = is_legal_period True."""
        result = service.calculate_unified_score(legal_context)
        assert result.temporal_adjustment.is_legal_period is True
    
    def test_illegal_time_zero_factor(self, service, illegal_context):
        """Heure illégale = temporal_factor = 0."""
        result = service.calculate_unified_score(illegal_context)
        assert result.temporal_adjustment.temporal_factor == 0
    
    def test_illegal_time_zero_score(self, service, illegal_context):
        """Heure illégale = score final = 0."""
        result = service.calculate_unified_score(illegal_context)
        assert result.final_score == 0
    
    def test_illegal_status(self, service, illegal_context):
        """Heure illégale = status ILLEGAL."""
        result = service.calculate_unified_score(illegal_context)
        assert result.temporal_adjustment.legal_status == LegalStatus.ILLEGAL
    
    def test_dawn_high_temporal_factor(self, service, dawn_context):
        """Aube = temporal_factor élevé."""
        result = service.calculate_unified_score(dawn_context)
        # À 7h, le facteur devrait être élevé (proche de l'aube)
        # En hiver, c'est juste après le début légal, donc >= 0.7
        assert result.temporal_adjustment.temporal_factor >= 0.7
        assert result.temporal_adjustment.is_legal_period is True
    
    def test_legal_badge_present(self, service, legal_context):
        """Le badge légal est présent."""
        result = service.calculate_unified_score(legal_context)
        assert "⚖️" in result.temporal_adjustment.legal_badge
    
    def test_illegal_badge_present(self, service, illegal_context):
        """Le badge illégal est présent."""
        result = service.calculate_unified_score(illegal_context)
        assert "❌" in result.temporal_adjustment.legal_badge


# =============================================================================
# TESTS: Conformité Waypoint-Centric
# =============================================================================

class TestWaypointCentric:
    """Tests de conformité waypoint-centric."""
    
    def test_context_preserved_in_result(self, service, legal_context):
        """Le contexte est préservé dans le résultat."""
        result = service.calculate_unified_score(legal_context)
        assert result.context.waypoint_id == legal_context.waypoint_id
        assert result.context.latitude == legal_context.latitude
        assert result.context.species == legal_context.species
    
    def test_different_waypoints_different_ids(self, service):
        """Waypoints différents = IDs de score différents."""
        tz = ZoneInfo("America/Montreal")
        
        context1 = ScoreContext(
            waypoint_id="WP-A",
            latitude=46.8,
            longitude=-71.2,
            target_datetime=datetime.now(tz).replace(hour=10),
            species="moose"
        )
        
        context2 = ScoreContext(
            waypoint_id="WP-B",
            latitude=46.9,
            longitude=-71.3,
            target_datetime=datetime.now(tz).replace(hour=10),
            species="deer"
        )
        
        result1 = service.calculate_unified_score(context1)
        result2 = service.calculate_unified_score(context2)
        
        assert result1.score_id != result2.score_id


# =============================================================================
# TESTS: Sérialisation
# =============================================================================

class TestSerialization:
    """Tests de sérialisation."""
    
    def test_result_to_dict(self, service, legal_context):
        """Le résultat se sérialise en dict."""
        result = service.calculate_unified_score(legal_context)
        data = result.to_dict()
        
        assert isinstance(data, dict)
        assert "score_id" in data
        assert "final_score" in data
        assert "final_level" in data
        assert "temporal_adjustment" in data
        assert "score_breakdown" in data
    
    def test_breakdown_serialization(self, service, legal_context):
        """Les breakdowns se sérialisent correctement."""
        result = service.calculate_unified_score(legal_context)
        data = result.to_dict()
        
        assert len(data["score_breakdown"]) == 9
        
        for breakdown in data["score_breakdown"]:
            assert "category" in breakdown
            assert "raw_value" in breakdown
            assert "weight" in breakdown
            assert "weighted_value" in breakdown
    
    def test_temporal_adjustment_serialization(self, service, legal_context):
        """L'ajustement temporel se sérialise correctement."""
        result = service.calculate_unified_score(legal_context)
        data = result.to_dict()
        
        ta = data["temporal_adjustment"]
        assert "is_legal_period" in ta
        assert "temporal_factor" in ta
        assert "legal_badge" in ta
    
    def test_metadata_present(self, service, legal_context):
        """Les métadonnées sont présentes."""
        result = service.calculate_unified_score(legal_context)
        
        assert "calculation_time_ms" in result.metadata
        assert "services_count" in result.metadata
        assert result.metadata["services_count"] == 9
        assert "version" in result.metadata


# =============================================================================
# TESTS: Data Contracts
# =============================================================================

class TestDataContracts:
    """Tests des data contracts."""
    
    def test_score_breakdown_creation(self):
        """Test création ScoreBreakdown."""
        breakdown = ScoreBreakdown(
            category=ScoreCategory.HABITAT,
            score_name="Test Score",
            raw_value=75.0,
            weight=0.12,
            weighted_value=9.0,
            level=ScoreLevel.GOOD,
            components_count=4,
            confidence=0.7
        )
        
        assert breakdown.category == ScoreCategory.HABITAT
        assert breakdown.raw_value == 75.0
        
        data = breakdown.to_dict()
        assert data["category"] == "habitat"
    
    def test_temporal_adjustment_creation(self):
        """Test création TemporalAdjustment."""
        adj = TemporalAdjustment(
            is_legal_period=True,
            legal_status=LegalStatus.LEGAL,
            temporal_factor=0.9,
            legal_window=None,
            adjustment_applied=10.0,
            legal_badge="⚖️ LÉGAL"
        )
        
        assert adj.is_legal_period is True
        assert adj.temporal_factor == 0.9
        
        data = adj.to_dict()
        assert data["legal_status"] == "legal"
    
    def test_unified_result_level_calculation(self):
        """Test calcul niveau depuis valeur."""
        assert UnifiedScoreResult.get_level_from_value(90) == ScoreLevel.EXCELLENT
        assert UnifiedScoreResult.get_level_from_value(75) == ScoreLevel.GOOD
        assert UnifiedScoreResult.get_level_from_value(55) == ScoreLevel.MODERATE
        assert UnifiedScoreResult.get_level_from_value(35) == ScoreLevel.POOR
        assert UnifiedScoreResult.get_level_from_value(15) == ScoreLevel.VERY_POOR


# =============================================================================
# TESTS: Qualité et Confiance
# =============================================================================

class TestQualityAndConfidence:
    """Tests de qualité et confiance."""
    
    def test_confidence_in_range(self, service, legal_context):
        """La confiance globale est entre 0 et 1."""
        result = service.calculate_unified_score(legal_context)
        assert 0 <= result.global_confidence <= 1
    
    def test_data_quality_valid(self, service, legal_context):
        """La qualité des données est valide."""
        result = service.calculate_unified_score(legal_context)
        assert result.data_quality in ["full", "partial", "minimal"]
    
    def test_factors_lists_present(self, service, legal_context):
        """Les listes de facteurs sont présentes."""
        result = service.calculate_unified_score(legal_context)
        assert isinstance(result.top_positive_factors, list)
        assert isinstance(result.top_negative_factors, list)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
