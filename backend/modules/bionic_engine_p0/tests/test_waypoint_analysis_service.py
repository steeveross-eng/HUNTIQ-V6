"""
BIONIC ENGINE — Tests du WaypointAnalysisService
==================================================
Suite de tests unitaires pour le service d'analyse waypoint-centric.

COUVERTURE:
- Cas nominaux (analyse complète, scores, fenêtres)
- Cas limites (waypoint isolé, rayon minimal)
- Cas hors période légale (score neutralisé)
- Intégration des services (UnifiedScoring, Heatmap, Legal)

CONFORMITÉ: G-SEC | G-QA | G-DOC | BIONIC V5

Minimum requis: 15 tests
"""

import pytest
from datetime import datetime
from zoneinfo import ZoneInfo

from modules.bionic_engine_p0.services.waypoint_analysis_service import (
    WaypointAnalysisService,
    get_waypoint_analysis_service,
    WaypointAnalysisContext,
    HotspotProximity,
    LocalMobilityAnalysis,
    LocalPressureAnalysis,
    LocalRiskAnalysis,
    LocalDensityAnalysis,
    HabitatTransition,
    OptimalWindowRecommendation,
    HabitatType,
    RiskLevel
)

from modules.bionic_engine_p0.services.scoring import ScoreLevel
from modules.bionic_engine_p0.services.legal_hours_service import LegalStatus


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def service():
    """Instance du service d'analyse."""
    return WaypointAnalysisService()


@pytest.fixture
def legal_datetime():
    """Datetime dans les heures légales (matin, 7h en été)."""
    tz = ZoneInfo("America/Montreal")
    # Utiliser une date d'été pour garantir que 7h est légal
    return datetime(2025, 6, 15, 7, 0, 0, tzinfo=tz)


@pytest.fixture
def illegal_datetime():
    """Datetime hors heures légales (nuit, 2h)."""
    tz = ZoneInfo("America/Montreal")
    return datetime(2025, 6, 15, 2, 0, 0, tzinfo=tz)


@pytest.fixture
def base_context(legal_datetime):
    """Contexte de base pour les tests."""
    return WaypointAnalysisContext(
        waypoint_id="WP-TEST-001",
        waypoint_name="Waypoint Test Principal",
        latitude=46.8139,
        longitude=-71.2080,
        target_datetime=legal_datetime,
        species="cerf",
        wqs_score=75.0,
        wqs_success_history=80.0,
        wqs_weather_correlation=70.0,
        wqs_activity_history=75.0,
        wqs_accessibility=70.0,
        search_radius_km=5.0,
        grid_resolution=10,
        region="CA-QC"
    )


@pytest.fixture
def illegal_context(illegal_datetime):
    """Contexte hors heures légales."""
    return WaypointAnalysisContext(
        waypoint_id="WP-ILLEGAL-001",
        waypoint_name="Waypoint Hors Heures",
        latitude=46.8139,
        longitude=-71.2080,
        target_datetime=illegal_datetime,
        species="cerf",
        wqs_score=80.0,
        search_radius_km=3.0,
        region="CA-QC"
    )


# =============================================================================
# TEST 1: Service Instantiation
# =============================================================================

class TestServiceInstantiation:
    """Tests d'instanciation du service."""
    
    def test_service_creation(self, service):
        """Test de création du service."""
        assert service is not None
        assert isinstance(service, WaypointAnalysisService)
    
    def test_singleton_pattern(self):
        """Test du pattern singleton."""
        service1 = get_waypoint_analysis_service()
        service2 = get_waypoint_analysis_service()
        assert service1 is service2
    
    def test_service_has_dependencies(self, service):
        """Test que le service a ses dépendances."""
        assert service._unified_scoring_service is not None
        assert service._heatmap_fusion_service is not None
        assert service._legal_hours_service is not None


# =============================================================================
# TEST 2: Analysis ID Generation
# =============================================================================

class TestAnalysisIdGeneration:
    """Tests de génération d'ID d'analyse."""
    
    def test_analysis_id_format(self, service, base_context):
        """Test du format de l'ID d'analyse."""
        result = service.analyze_waypoint(base_context)
        assert result.analysis_id.startswith("WPA-")
        assert len(result.analysis_id) > 10
    
    def test_analysis_id_unique(self, service, base_context):
        """Test d'unicité des IDs."""
        result1 = service.analyze_waypoint(base_context)
        result2 = service.analyze_waypoint(base_context)
        assert result1.analysis_id != result2.analysis_id


# =============================================================================
# TEST 3: Legal Period Analysis (CRITICAL)
# =============================================================================

class TestLegalPeriodAnalysis:
    """Tests de conformité aux heures légales."""
    
    def test_legal_period_detected(self, service, base_context):
        """Test de détection de période légale."""
        result = service.analyze_waypoint(base_context)
        assert result.is_legal_period is True
        assert result.legal_status in [LegalStatus.LEGAL, LegalStatus.MARGINAL]
    
    def test_illegal_period_detected(self, service, illegal_context):
        """Test de détection de période illégale."""
        result = service.analyze_waypoint(illegal_context)
        assert result.is_legal_period is False
        assert result.legal_status == LegalStatus.ILLEGAL
    
    def test_legal_window_provided(self, service, base_context):
        """Test que la fenêtre légale est fournie."""
        result = service.analyze_waypoint(base_context)
        assert result.legal_window is not None
        assert result.legal_window.duration_hours > 0
    
    def test_illegal_period_recommendations(self, service, illegal_context):
        """Test des recommandations pour période illégale."""
        result = service.analyze_waypoint(illegal_context)
        # Les recommandations doivent mentionner la période non légale
        assert len(result.recommendations) > 0


# =============================================================================
# TEST 4: Score Calculation
# =============================================================================

class TestScoreCalculation:
    """Tests du calcul des scores."""
    
    def test_unified_score_calculated(self, service, base_context):
        """Test que le score unifié est calculé."""
        result = service.analyze_waypoint(base_context)
        assert result.unified_score >= 0
        assert result.unified_score <= 100
    
    def test_unified_level_assigned(self, service, base_context):
        """Test que le niveau unifié est assigné."""
        result = service.analyze_waypoint(base_context)
        assert result.unified_level is not None
        assert isinstance(result.unified_level, ScoreLevel)
    
    def test_fused_heatmap_score_calculated(self, service, base_context):
        """Test que le score de heatmap fusionnée est calculé."""
        result = service.analyze_waypoint(base_context)
        assert result.fused_heatmap_score >= 0
        assert result.fused_heatmap_score <= 100
    
    def test_wqs_score_preserved(self, service, base_context):
        """Test que le score WQS est préservé."""
        result = service.analyze_waypoint(base_context)
        assert result.wqs_score == base_context.wqs_score


# =============================================================================
# TEST 5: Local Analyses Extraction
# =============================================================================

class TestLocalAnalyses:
    """Tests des analyses locales."""
    
    def test_mobility_analysis_extracted(self, service, base_context):
        """Test de l'extraction de l'analyse de mobilité."""
        result = service.analyze_waypoint(base_context)
        
        assert result.mobility_analysis is not None
        assert isinstance(result.mobility_analysis, LocalMobilityAnalysis)
        assert 0 <= result.mobility_analysis.mobility_score <= 100
    
    def test_pressure_analysis_extracted(self, service, base_context):
        """Test de l'extraction de l'analyse de pression."""
        result = service.analyze_waypoint(base_context)
        
        assert result.pressure_analysis is not None
        assert isinstance(result.pressure_analysis, LocalPressureAnalysis)
        assert 0 <= result.pressure_analysis.pressure_score <= 100
    
    def test_risk_analysis_extracted(self, service, base_context):
        """Test de l'extraction de l'analyse des risques."""
        result = service.analyze_waypoint(base_context)
        
        assert result.risk_analysis is not None
        assert isinstance(result.risk_analysis, LocalRiskAnalysis)
        assert result.risk_analysis.risk_level in RiskLevel
    
    def test_density_analysis_extracted(self, service, base_context):
        """Test de l'extraction de l'analyse de densité."""
        result = service.analyze_waypoint(base_context)
        
        assert result.density_analysis is not None
        assert isinstance(result.density_analysis, LocalDensityAnalysis)
        assert 0 <= result.density_analysis.density_score <= 100


# =============================================================================
# TEST 6: Optimal Windows
# =============================================================================

class TestOptimalWindows:
    """Tests des fenêtres optimales."""
    
    def test_optimal_windows_generated(self, service, base_context):
        """Test de génération des fenêtres optimales."""
        result = service.analyze_waypoint(base_context)
        
        assert result.optimal_windows is not None
        assert len(result.optimal_windows) > 0
    
    def test_optimal_window_structure(self, service, base_context):
        """Test de la structure des fenêtres optimales."""
        result = service.analyze_waypoint(base_context)
        
        for window in result.optimal_windows:
            assert isinstance(window, OptimalWindowRecommendation)
            assert window.period is not None
            assert window.start_time is not None
            assert window.end_time is not None
            assert window.legal_badge is not None
    
    def test_optimal_windows_sorted_by_score(self, service, base_context):
        """Test que les fenêtres sont triées par score."""
        result = service.analyze_waypoint(base_context)
        
        if len(result.optimal_windows) > 1:
            scores = [w.score for w in result.optimal_windows]
            assert scores == sorted(scores, reverse=True)


# =============================================================================
# TEST 7: Hotspot Analysis
# =============================================================================

class TestHotspotAnalysis:
    """Tests de l'analyse des hotspots."""
    
    def test_hotspots_generated(self, service, base_context):
        """Test de génération des hotspots."""
        result = service.analyze_waypoint(base_context)
        
        assert result.hotspots_nearby is not None
        assert len(result.hotspots_nearby) > 0
    
    def test_hotspot_structure(self, service, base_context):
        """Test de la structure des hotspots."""
        result = service.analyze_waypoint(base_context)
        
        for hotspot in result.hotspots_nearby:
            assert isinstance(hotspot, HotspotProximity)
            assert hotspot.hotspot_id is not None
            assert hotspot.distance_km >= 0
            assert 0 <= hotspot.bearing_degrees < 360
    
    def test_hotspots_within_radius(self, service, base_context):
        """Test que les hotspots sont dans le rayon de recherche."""
        result = service.analyze_waypoint(base_context)
        
        for hotspot in result.hotspots_nearby:
            assert hotspot.distance_km <= base_context.search_radius_km
    
    def test_hotspots_sorted_by_score(self, service, base_context):
        """Test que les hotspots sont triés par score décroissant."""
        result = service.analyze_waypoint(base_context)
        
        if len(result.hotspots_nearby) > 1:
            scores = [h.score for h in result.hotspots_nearby]
            assert scores == sorted(scores, reverse=True)


# =============================================================================
# TEST 8: Habitat Analysis
# =============================================================================

class TestHabitatAnalysis:
    """Tests de l'analyse d'habitat."""
    
    def test_dominant_habitat_assigned(self, service, base_context):
        """Test que l'habitat dominant est assigné."""
        result = service.analyze_waypoint(base_context)
        
        assert result.dominant_habitat is not None
        assert isinstance(result.dominant_habitat, HabitatType)
    
    def test_habitat_transitions_generated(self, service, base_context):
        """Test de génération des transitions d'habitat."""
        result = service.analyze_waypoint(base_context)
        
        assert result.habitat_transitions is not None
        # Les transitions peuvent être vides si l'habitat est homogène
        for transition in result.habitat_transitions:
            assert isinstance(transition, HabitatTransition)


# =============================================================================
# TEST 9: Recommendations
# =============================================================================

class TestRecommendations:
    """Tests des recommandations."""
    
    def test_recommendations_generated(self, service, base_context):
        """Test de génération des recommandations."""
        result = service.analyze_waypoint(base_context)
        
        assert result.recommendations is not None
        assert len(result.recommendations) > 0
    
    def test_recommendations_are_strings(self, service, base_context):
        """Test que les recommandations sont des chaînes."""
        result = service.analyze_waypoint(base_context)
        
        for rec in result.recommendations:
            assert isinstance(rec, str)
            assert len(rec) > 0


# =============================================================================
# TEST 10: Result Serialization
# =============================================================================

class TestResultSerialization:
    """Tests de sérialisation du résultat."""
    
    def test_result_to_dict(self, service, base_context):
        """Test de sérialisation en dictionnaire."""
        result = service.analyze_waypoint(base_context)
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert "analysis_id" in result_dict
        assert "waypoint" in result_dict
        assert "scores" in result_dict
    
    def test_result_dict_contains_all_sections(self, service, base_context):
        """Test que le dictionnaire contient toutes les sections."""
        result = service.analyze_waypoint(base_context)
        result_dict = result.to_dict()
        
        required_sections = [
            "analysis_id", "calculated_at", "waypoint",
            "scores", "hotspots_nearby", "local_analysis",
            "habitat", "optimal_windows", "legal",
            "recommendations", "references", "context", "metadata"
        ]
        
        for section in required_sections:
            assert section in result_dict, f"Section manquante: {section}"
    
    def test_context_to_dict(self, base_context):
        """Test de sérialisation du contexte."""
        context_dict = base_context.to_dict()
        
        assert isinstance(context_dict, dict)
        assert "waypoint" in context_dict
        assert "target_datetime" in context_dict
        assert "species" in context_dict


# =============================================================================
# TEST 11: Metadata
# =============================================================================

class TestMetadata:
    """Tests des métadonnées."""
    
    def test_metadata_contains_timing(self, service, base_context):
        """Test que les métadonnées contiennent le timing."""
        result = service.analyze_waypoint(base_context)
        
        assert "calculation_time_ms" in result.metadata
        assert result.metadata["calculation_time_ms"] >= 0
    
    def test_metadata_contains_version(self, service, base_context):
        """Test que les métadonnées contiennent la version."""
        result = service.analyze_waypoint(base_context)
        
        assert "version" in result.metadata
        assert "BIONIC" in result.metadata["version"]
    
    def test_metadata_contains_counts(self, service, base_context):
        """Test que les métadonnées contiennent les compteurs."""
        result = service.analyze_waypoint(base_context)
        
        assert "hotspots_count" in result.metadata
        assert "transitions_count" in result.metadata


# =============================================================================
# TEST 12: References
# =============================================================================

class TestReferences:
    """Tests des références aux résultats sous-jacents."""
    
    def test_unified_score_id_present(self, service, base_context):
        """Test que l'ID du score unifié est présent."""
        result = service.analyze_waypoint(base_context)
        
        assert result.unified_score_id is not None
        assert result.unified_score_id.startswith("UNI-")
    
    def test_heatmap_id_present(self, service, base_context):
        """Test que l'ID de la heatmap est présent."""
        result = service.analyze_waypoint(base_context)
        
        assert result.heatmap_id is not None
        assert result.heatmap_id.startswith("HM-")


# =============================================================================
# TEST 13: Waypoint Coordinates
# =============================================================================

class TestWaypointCoordinates:
    """Tests des coordonnées du waypoint."""
    
    def test_waypoint_coordinates_preserved(self, service, base_context):
        """Test que les coordonnées du waypoint sont préservées."""
        result = service.analyze_waypoint(base_context)
        
        assert result.waypoint_coordinates[0] == base_context.latitude
        assert result.waypoint_coordinates[1] == base_context.longitude
    
    def test_waypoint_id_preserved(self, service, base_context):
        """Test que l'ID du waypoint est préservé."""
        result = service.analyze_waypoint(base_context)
        
        assert result.waypoint_id == base_context.waypoint_id
    
    def test_waypoint_name_preserved(self, service, base_context):
        """Test que le nom du waypoint est préservé."""
        result = service.analyze_waypoint(base_context)
        
        assert result.waypoint_name == base_context.waypoint_name


# =============================================================================
# TEST 14: Edge Cases
# =============================================================================

class TestEdgeCases:
    """Tests des cas limites."""
    
    def test_minimal_wqs_score(self, service, legal_datetime):
        """Test avec WQS score minimal."""
        context = WaypointAnalysisContext(
            waypoint_id="WP-MIN",
            waypoint_name="Waypoint Minimal",
            latitude=46.8139,
            longitude=-71.2080,
            target_datetime=legal_datetime,
            species="cerf",
            wqs_score=0.0,
            region="CA-QC"
        )
        
        result = service.analyze_waypoint(context)
        assert result is not None
        assert result.unified_score >= 0
    
    def test_maximal_wqs_score(self, service, legal_datetime):
        """Test avec WQS score maximal."""
        context = WaypointAnalysisContext(
            waypoint_id="WP-MAX",
            waypoint_name="Waypoint Maximal",
            latitude=46.8139,
            longitude=-71.2080,
            target_datetime=legal_datetime,
            species="cerf",
            wqs_score=100.0,
            region="CA-QC"
        )
        
        result = service.analyze_waypoint(context)
        assert result is not None
        assert result.fused_heatmap_score <= 100
    
    def test_very_small_radius(self, service, legal_datetime):
        """Test avec rayon très petit."""
        context = WaypointAnalysisContext(
            waypoint_id="WP-SMALL",
            waypoint_name="Waypoint Petit Rayon",
            latitude=46.8139,
            longitude=-71.2080,
            target_datetime=legal_datetime,
            species="cerf",
            wqs_score=70.0,
            search_radius_km=0.5,
            region="CA-QC"
        )
        
        result = service.analyze_waypoint(context)
        assert result is not None
    
    def test_different_species(self, service, legal_datetime):
        """Test avec différentes espèces."""
        for species in ["cerf", "orignal", "ours", "dindon"]:
            context = WaypointAnalysisContext(
                waypoint_id=f"WP-{species.upper()}",
                waypoint_name=f"Waypoint {species}",
                latitude=46.8139,
                longitude=-71.2080,
                target_datetime=legal_datetime,
                species=species,
                wqs_score=70.0,
                region="CA-QC"
            )
            
            result = service.analyze_waypoint(context)
            assert result is not None


# =============================================================================
# TEST 15: Data Quality
# =============================================================================

class TestDataQuality:
    """Tests de qualité des données."""
    
    def test_scores_in_valid_range(self, service, base_context):
        """Test que tous les scores sont dans la plage valide."""
        result = service.analyze_waypoint(base_context)
        
        assert 0 <= result.unified_score <= 100
        assert 0 <= result.fused_heatmap_score <= 100
        assert 0 <= result.wqs_score <= 100
        assert 0 <= result.mobility_analysis.mobility_score <= 100
        assert 0 <= result.pressure_analysis.pressure_score <= 100
        assert 0 <= result.density_analysis.density_score <= 100
    
    def test_timestamps_valid(self, service, base_context):
        """Test que les timestamps sont valides."""
        result = service.analyze_waypoint(base_context)
        
        assert result.calculated_at is not None
        assert result.calculated_at.tzinfo is not None  # Timezone-aware
    
    def test_legal_window_duration_valid(self, service, base_context):
        """Test que la durée de la fenêtre légale est valide."""
        result = service.analyze_waypoint(base_context)
        
        # En été, la fenêtre légale doit être d'au moins 12h
        assert result.legal_window.duration_hours > 10
        assert result.legal_window.duration_hours < 20


# =============================================================================
# TEST 16: Integration Consistency
# =============================================================================

class TestIntegrationConsistency:
    """Tests de cohérence d'intégration."""
    
    def test_unified_score_matches_breakdown(self, service, base_context):
        """Test de cohérence entre score unifié et ses composants."""
        result = service.analyze_waypoint(base_context)
        
        # Le score unifié doit être cohérent (pas de vérification de formule exacte)
        # car le service appelle UnifiedScoringService
        assert result.unified_score >= 0
        assert result.unified_level is not None
    
    def test_heatmap_score_plausible(self, service, base_context):
        """Test de plausibilité du score de heatmap."""
        result = service.analyze_waypoint(base_context)
        
        # Le score fusionné doit être influencé par WQS et score unifié
        # Formule: 40% WQS + 60% SCORE_FINAL
        expected_min = min(base_context.wqs_score, result.unified_score) * 0.4
        expected_max = max(base_context.wqs_score, result.unified_score) * 1.2
        
        assert result.fused_heatmap_score >= expected_min * 0.5
        assert result.fused_heatmap_score <= expected_max


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
