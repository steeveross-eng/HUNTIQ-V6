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
from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo

from modules.bionic_engine_p0.services.waypoint_analysis_service import (
    WaypointAnalysisService,
    get_waypoint_analysis_service,
    WaypointAnalysisContext,
    WaypointAnalysisResult,
    AnalysisQuality,
    HotspotDistance,
    LocalPressureAnalysis,
    LocalDensityAnalysis,
    LocalMobilityAnalysis,
    LocalRiskAnalysis,
    SpeciesScore,
    OptimalWindow,
    SCORE_THRESHOLD_EXCELLENT,
    SCORE_THRESHOLD_GOOD,
    SCORE_THRESHOLD_MODERATE,
    SCORE_THRESHOLD_POOR,
    DEFAULT_ANALYSIS_RADIUS_KM
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
    """Datetime dans les heures légales (matin, 7h)."""
    tz = ZoneInfo("America/Montreal")
    # Utiliser une date fixe pour des tests reproductibles
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
        analysis_radius_km=5.0,
        region="CA-QC"
    )


@pytest.fixture
def context_with_hotspots(legal_datetime):
    """Contexte avec hotspots à proximité."""
    return WaypointAnalysisContext(
        waypoint_id="WP-TEST-002",
        waypoint_name="Waypoint avec Hotspots",
        latitude=46.8139,
        longitude=-71.2080,
        target_datetime=legal_datetime,
        species="orignal",
        wqs_score=65.0,
        analysis_radius_km=10.0,
        nearby_hotspots=[
            {
                "id": "HS-001",
                "name": "Hotspot Nord",
                "latitude": 46.8500,
                "longitude": -71.2000,
                "score": 85.0,
                "species": ["orignal", "cerf"]
            },
            {
                "id": "HS-002",
                "name": "Hotspot Sud",
                "latitude": 46.7800,
                "longitude": -71.2200,
                "score": 60.0,
                "species": ["orignal"]
            },
            {
                "id": "HS-003",
                "name": "Hotspot Loin",
                "latitude": 47.0000,
                "longitude": -71.5000,
                "score": 90.0,
                "species": ["orignal"]
            }
        ],
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
        result = service.analyze_waypoint(base_context, include_heatmap=False)
        assert result.analysis_id.startswith("WPA-")
        assert len(result.analysis_id) > 10
    
    def test_analysis_id_unique(self, service, base_context):
        """Test d'unicité des IDs."""
        result1 = service.analyze_waypoint(base_context, include_heatmap=False)
        result2 = service.analyze_waypoint(base_context, include_heatmap=False)
        assert result1.analysis_id != result2.analysis_id


# =============================================================================
# TEST 3: Legal Period Analysis (CRITICAL)
# =============================================================================

class TestLegalPeriodAnalysis:
    """Tests de conformité aux heures légales."""
    
    def test_legal_period_detected(self, service, base_context):
        """Test de détection de période légale."""
        result = service.analyze_waypoint(base_context, include_heatmap=False)
        assert result.is_legal_period is True
        assert result.legal_status in [LegalStatus.LEGAL, LegalStatus.MARGINAL]
    
    def test_illegal_period_detected(self, service, illegal_context):
        """Test de détection de période illégale."""
        result = service.analyze_waypoint(illegal_context, include_heatmap=False)
        assert result.is_legal_period is False
        assert result.legal_status == LegalStatus.ILLEGAL
    
    def test_score_neutralized_when_illegal(self, service, illegal_context):
        """Test de neutralisation du score hors période légale."""
        result = service.analyze_waypoint(illegal_context, include_heatmap=False)
        assert result.global_score == 0.0
        assert result.fused_score == 0.0
        assert result.wqs_contribution == 0.0
        assert result.score_final_contribution == 0.0
    
    def test_legal_badge_correct(self, service, base_context, illegal_context):
        """Test des badges de légalité."""
        legal_result = service.analyze_waypoint(base_context, include_heatmap=False)
        illegal_result = service.analyze_waypoint(illegal_context, include_heatmap=False)
        
        assert "LÉGAL" in legal_result.legal_badge
        assert "HORS HEURES" in illegal_result.legal_badge
    
    def test_analysis_quality_illegal(self, service, illegal_context):
        """Test de la qualité d'analyse en période illégale."""
        result = service.analyze_waypoint(illegal_context, include_heatmap=False)
        assert result.analysis_quality == AnalysisQuality.ILLEGAL


# =============================================================================
# TEST 4: Score Calculation
# =============================================================================

class TestScoreCalculation:
    """Tests du calcul des scores."""
    
    def test_unified_score_calculated(self, service, base_context):
        """Test que le score unifié est calculé."""
        result = service.analyze_waypoint(base_context, include_heatmap=False)
        assert result.unified_score >= 0
        assert result.unified_score <= 100
    
    def test_fused_score_formula(self, service, base_context):
        """Test de la formule de fusion (40% WQS + 60% SCORE_FINAL)."""
        result = service.analyze_waypoint(base_context, include_heatmap=False)
        
        # Vérifier les contributions
        expected_wqs_contrib = base_context.wqs_score * 0.40
        expected_sf_contrib = result.unified_score * 0.60
        expected_fused = expected_wqs_contrib + expected_sf_contrib
        
        # Tolérance pour les arrondis
        assert abs(result.fused_score - expected_fused) < 1.0
    
    def test_score_level_mapping(self, service, base_context):
        """Test du mapping score -> niveau."""
        result = service.analyze_waypoint(base_context, include_heatmap=False)
        
        if result.global_score >= SCORE_THRESHOLD_EXCELLENT:
            assert result.global_level == ScoreLevel.EXCELLENT
        elif result.global_score >= SCORE_THRESHOLD_GOOD:
            assert result.global_level == ScoreLevel.GOOD
        elif result.global_score >= SCORE_THRESHOLD_MODERATE:
            assert result.global_level == ScoreLevel.MODERATE
        elif result.global_score >= SCORE_THRESHOLD_POOR:
            assert result.global_level == ScoreLevel.POOR
        else:
            assert result.global_level == ScoreLevel.VERY_POOR


# =============================================================================
# TEST 5: Local Analyses Extraction
# =============================================================================

class TestLocalAnalyses:
    """Tests des analyses locales."""
    
    def test_pressure_analysis_extracted(self, service, base_context):
        """Test de l'extraction de l'analyse de pression."""
        result = service.analyze_waypoint(base_context, include_heatmap=False)
        
        assert result.pressure_analysis is not None
        assert isinstance(result.pressure_analysis, LocalPressureAnalysis)
        assert 0 <= result.pressure_analysis.pressure_score <= 100
    
    def test_density_analysis_extracted(self, service, base_context):
        """Test de l'extraction de l'analyse de densité."""
        result = service.analyze_waypoint(base_context, include_heatmap=False)
        
        assert result.density_analysis is not None
        assert isinstance(result.density_analysis, LocalDensityAnalysis)
        assert result.density_analysis.estimated_population in ["low", "moderate", "high"]
    
    def test_mobility_analysis_extracted(self, service, base_context):
        """Test de l'extraction de l'analyse de mobilité."""
        result = service.analyze_waypoint(base_context, include_heatmap=False)
        
        assert result.mobility_analysis is not None
        assert isinstance(result.mobility_analysis, LocalMobilityAnalysis)
        assert result.mobility_analysis.expected_movement in ["static", "low", "moderate", "high"]
    
    def test_risk_analysis_extracted(self, service, base_context):
        """Test de l'extraction de l'analyse des risques."""
        result = service.analyze_waypoint(base_context, include_heatmap=False)
        
        assert result.risk_analysis is not None
        assert isinstance(result.risk_analysis, LocalRiskAnalysis)
        assert result.risk_analysis.access_difficulty in ["easy", "moderate", "difficult"]


# =============================================================================
# TEST 6: Optimal Windows
# =============================================================================

class TestOptimalWindows:
    """Tests des fenêtres optimales."""
    
    def test_optimal_windows_generated(self, service, base_context):
        """Test de génération des fenêtres optimales."""
        result = service.analyze_waypoint(base_context, include_heatmap=False)
        
        assert result.optimal_windows is not None
        assert len(result.optimal_windows) > 0
    
    def test_optimal_windows_are_legal(self, service, base_context):
        """Test que les fenêtres optimales sont légales."""
        result = service.analyze_waypoint(base_context, include_heatmap=False)
        
        for window in result.optimal_windows:
            assert window.is_legal is True
    
    def test_best_window_selected(self, service, base_context):
        """Test de sélection de la meilleure fenêtre."""
        result = service.analyze_waypoint(base_context, include_heatmap=False)
        
        if result.optimal_windows:
            assert result.best_window is not None
            assert isinstance(result.best_window, OptimalWindow)
    
    def test_window_structure(self, service, base_context):
        """Test de la structure des fenêtres."""
        result = service.analyze_waypoint(base_context, include_heatmap=False)
        
        if result.optimal_windows:
            window = result.optimal_windows[0]
            assert window.period in ["dawn", "morning", "afternoon", "dusk"]
            assert window.quality in ["excellent", "good", "moderate"]
            assert 0 <= window.score_modifier <= 1


# =============================================================================
# TEST 7: Hotspot Analysis
# =============================================================================

class TestHotspotAnalysis:
    """Tests de l'analyse des hotspots."""
    
    def test_hotspots_analyzed(self, service, context_with_hotspots):
        """Test de l'analyse des hotspots."""
        result = service.analyze_waypoint(context_with_hotspots, include_heatmap=False)
        
        assert len(result.nearby_hotspots) == 3
    
    def test_hotspots_sorted_by_distance(self, service, context_with_hotspots):
        """Test du tri des hotspots par distance."""
        result = service.analyze_waypoint(context_with_hotspots, include_heatmap=False)
        
        distances = [h.distance_km for h in result.nearby_hotspots]
        assert distances == sorted(distances)
    
    def test_hotspot_within_radius_flag(self, service, context_with_hotspots):
        """Test du flag is_within_radius."""
        result = service.analyze_waypoint(context_with_hotspots, include_heatmap=False)
        
        for hotspot in result.nearby_hotspots:
            if hotspot.distance_km <= context_with_hotspots.analysis_radius_km:
                assert hotspot.is_within_radius is True
            else:
                assert hotspot.is_within_radius is False
    
    def test_best_hotspot_selected(self, service, context_with_hotspots):
        """Test de sélection du meilleur hotspot."""
        result = service.analyze_waypoint(context_with_hotspots, include_heatmap=False)
        
        # Le meilleur hotspot doit être dans le rayon et avoir le meilleur score
        if result.best_hotspot:
            assert result.best_hotspot.is_within_radius is True
            within_radius = [h for h in result.nearby_hotspots if h.is_within_radius]
            best_score = max(h.score for h in within_radius)
            assert result.best_hotspot.score == best_score
    
    def test_hotspot_direction_calculated(self, service, context_with_hotspots):
        """Test du calcul de la direction des hotspots."""
        result = service.analyze_waypoint(context_with_hotspots, include_heatmap=False)
        
        for hotspot in result.nearby_hotspots:
            assert hotspot.direction_label in ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
            assert 0 <= hotspot.bearing_degrees < 360


# =============================================================================
# TEST 8: Species Scores
# =============================================================================

class TestSpeciesScores:
    """Tests des scores par espèce."""
    
    def test_species_score_generated(self, service, base_context):
        """Test de génération du score par espèce."""
        result = service.analyze_waypoint(base_context, include_heatmap=False)
        
        assert len(result.species_scores) > 0
    
    def test_species_matches_context(self, service, base_context):
        """Test que l'espèce correspond au contexte."""
        result = service.analyze_waypoint(base_context, include_heatmap=False)
        
        species_names = [s.species for s in result.species_scores]
        assert base_context.species in species_names


# =============================================================================
# TEST 9: Heatmap Integration
# =============================================================================

class TestHeatmapIntegration:
    """Tests de l'intégration de la heatmap."""
    
    def test_heatmap_generated_when_requested(self, service, base_context):
        """Test de génération de la heatmap."""
        result = service.analyze_waypoint(base_context, include_heatmap=True)
        
        assert result.heatmap_result is not None
        assert len(result.heatmap_result.cells) > 0
    
    def test_heatmap_not_generated_when_not_requested(self, service, base_context):
        """Test que la heatmap n'est pas générée si non demandée."""
        result = service.analyze_waypoint(base_context, include_heatmap=False)
        
        assert result.heatmap_result is None
    
    def test_heatmap_not_generated_when_illegal(self, service, illegal_context):
        """Test que la heatmap n'est pas générée hors période légale."""
        result = service.analyze_waypoint(illegal_context, include_heatmap=True)
        
        assert result.heatmap_result is None


# =============================================================================
# TEST 10: Recommendations
# =============================================================================

class TestRecommendations:
    """Tests des recommandations."""
    
    def test_recommendations_generated(self, service, base_context):
        """Test de génération des recommandations."""
        result = service.analyze_waypoint(base_context, include_heatmap=False)
        
        assert len(result.recommendations) > 0
    
    def test_illegal_period_recommendation(self, service, illegal_context):
        """Test de recommandation pour période illégale."""
        result = service.analyze_waypoint(illegal_context, include_heatmap=False)
        
        assert any("NON AUTORISÉE" in r or "heures légales" in r.lower() for r in result.recommendations)
    
    def test_positive_negative_factors(self, service, base_context):
        """Test des facteurs positifs et négatifs."""
        result = service.analyze_waypoint(base_context, include_heatmap=False)
        
        assert isinstance(result.key_positive_factors, list)
        assert isinstance(result.key_negative_factors, list)


# =============================================================================
# TEST 11: Analysis Quality
# =============================================================================

class TestAnalysisQuality:
    """Tests de la qualité d'analyse."""
    
    def test_quality_exceptional(self):
        """Test de qualité exceptionnelle."""
        quality = WaypointAnalysisResult.get_quality_from_score_and_legal(90.0, True)
        assert quality == AnalysisQuality.EXCEPTIONAL
    
    def test_quality_favorable(self):
        """Test de qualité favorable."""
        quality = WaypointAnalysisResult.get_quality_from_score_and_legal(75.0, True)
        assert quality == AnalysisQuality.FAVORABLE
    
    def test_quality_acceptable(self):
        """Test de qualité acceptable."""
        quality = WaypointAnalysisResult.get_quality_from_score_and_legal(55.0, True)
        assert quality == AnalysisQuality.ACCEPTABLE
    
    def test_quality_defavorable(self):
        """Test de qualité défavorable."""
        quality = WaypointAnalysisResult.get_quality_from_score_and_legal(35.0, True)
        assert quality == AnalysisQuality.DEFAVORABLE
    
    def test_quality_illegal_overrides_score(self):
        """Test que la période illégale override le score."""
        quality = WaypointAnalysisResult.get_quality_from_score_and_legal(95.0, False)
        assert quality == AnalysisQuality.ILLEGAL


# =============================================================================
# TEST 12: Context Conversions
# =============================================================================

class TestContextConversions:
    """Tests des conversions de contexte."""
    
    def test_to_score_context(self, base_context):
        """Test de conversion en ScoreContext."""
        score_context = base_context.to_score_context()
        
        assert score_context.waypoint_id == base_context.waypoint_id
        assert score_context.latitude == base_context.latitude
        assert score_context.longitude == base_context.longitude
        assert score_context.species == base_context.species
    
    def test_to_heatmap_context(self, base_context):
        """Test de conversion en HeatmapFusionContext."""
        heatmap_context = base_context.to_heatmap_context()
        
        assert heatmap_context.waypoint_id == base_context.waypoint_id
        assert heatmap_context.wqs_input.wqs_score == base_context.wqs_score
    
    def test_to_wqs_input(self, base_context):
        """Test de conversion en WQSInput."""
        wqs_input = base_context.to_wqs_input()
        
        assert wqs_input.wqs_score == base_context.wqs_score
        assert wqs_input.success_history == base_context.wqs_success_history


# =============================================================================
# TEST 13: Result Serialization
# =============================================================================

class TestResultSerialization:
    """Tests de sérialisation du résultat."""
    
    def test_result_to_dict(self, service, base_context):
        """Test de sérialisation en dictionnaire."""
        result = service.analyze_waypoint(base_context, include_heatmap=False)
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert "analysis_id" in result_dict
        assert "global_summary" in result_dict
        assert "legal_compliance" in result_dict
        assert "scores" in result_dict
    
    def test_result_dict_contains_all_sections(self, service, base_context):
        """Test que le dictionnaire contient toutes les sections."""
        result = service.analyze_waypoint(base_context, include_heatmap=False)
        result_dict = result.to_dict()
        
        required_sections = [
            "analysis_id", "calculated_at", "global_summary",
            "legal_compliance", "scores", "score_breakdown",
            "local_analyses", "species_analysis", "hotspots",
            "optimal_windows", "heatmap_summary", "insights",
            "context", "metadata"
        ]
        
        for section in required_sections:
            assert section in result_dict, f"Section manquante: {section}"


# =============================================================================
# TEST 14: Metadata
# =============================================================================

class TestMetadata:
    """Tests des métadonnées."""
    
    def test_metadata_contains_timing(self, service, base_context):
        """Test que les métadonnées contiennent le timing."""
        result = service.analyze_waypoint(base_context, include_heatmap=False)
        
        assert "calculation_time_ms" in result.metadata
        assert result.metadata["calculation_time_ms"] >= 0
    
    def test_metadata_contains_version(self, service, base_context):
        """Test que les métadonnées contiennent la version."""
        result = service.analyze_waypoint(base_context, include_heatmap=False)
        
        assert "version" in result.metadata
        assert "BIONIC" in result.metadata["version"]
    
    def test_metadata_contains_score_id(self, service, base_context):
        """Test que les métadonnées contiennent l'ID du score unifié."""
        result = service.analyze_waypoint(base_context, include_heatmap=False)
        
        assert "unified_score_id" in result.metadata


# =============================================================================
# TEST 15: Edge Cases
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
        
        result = service.analyze_waypoint(context, include_heatmap=False)
        assert result is not None
        assert result.fused_score >= 0
    
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
        
        result = service.analyze_waypoint(context, include_heatmap=False)
        assert result is not None
        assert result.fused_score <= 100
    
    def test_empty_hotspots_list(self, service, base_context):
        """Test avec liste de hotspots vide."""
        base_context.nearby_hotspots = []
        
        result = service.analyze_waypoint(base_context, include_heatmap=False)
        assert result.nearby_hotspots == []
        assert result.best_hotspot is None
    
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
            analysis_radius_km=0.1,
            region="CA-QC"
        )
        
        result = service.analyze_waypoint(context, include_heatmap=False)
        assert result is not None


# =============================================================================
# TEST 16: Distance Calculations
# =============================================================================

class TestDistanceCalculations:
    """Tests des calculs de distance."""
    
    def test_distance_calculation_same_point(self, service):
        """Test de distance pour le même point."""
        distance = service._calculate_distance_km(
            46.8139, -71.2080,
            46.8139, -71.2080
        )
        assert distance == 0.0
    
    def test_distance_calculation_known_points(self, service):
        """Test de distance pour des points connus."""
        # Environ 4km de distance
        distance = service._calculate_distance_km(
            46.8139, -71.2080,
            46.8500, -71.2000
        )
        assert 3 < distance < 5
    
    def test_bearing_calculation(self, service):
        """Test du calcul de bearing."""
        # Point au nord
        bearing = service._calculate_bearing(
            46.8139, -71.2080,
            46.9000, -71.2080
        )
        assert 350 <= bearing or bearing <= 10  # Environ Nord
    
    def test_bearing_to_direction(self, service):
        """Test de conversion bearing -> direction."""
        assert service._bearing_to_direction(0) == "N"
        assert service._bearing_to_direction(45) == "NE"
        assert service._bearing_to_direction(90) == "E"
        assert service._bearing_to_direction(180) == "S"
        assert service._bearing_to_direction(270) == "W"


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
