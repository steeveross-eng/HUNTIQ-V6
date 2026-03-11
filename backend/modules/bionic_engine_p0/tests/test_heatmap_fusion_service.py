"""
BIONIC ENGINE — Heatmap Fusion Service — Tests Unitaires
=========================================================
Tests pour le service de fusion HeatmapFusionService.

COUVERTURE:
- Instanciation et configuration
- Fusion WQS + SCORE_FINAL
- Génération de grille
- Statistiques heatmap
- Conformité légale
- Sérialisation

Conformité: G-QA | BIONIC V5
"""

import pytest
from datetime import datetime, time
from zoneinfo import ZoneInfo

import sys
sys.path.insert(0, '/app/backend')

from modules.bionic_engine_p0.services.heatmap_fusion_service import (
    HeatmapFusionService,
    get_heatmap_fusion_service,
    HeatmapUnifieeResult,
    HeatmapStatistics,
    HeatmapFusionContext,
    WQSInput,
    WQS_WEIGHT,
    SCORE_FINAL_WEIGHT,
    HEATMAP_COLORS
)

from modules.bionic_engine_p0.services.scoring import ScoreLevel


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def service():
    """Instance du service pour les tests."""
    return HeatmapFusionService()


@pytest.fixture
def wqs_input():
    """Données WQS en entrée."""
    return WQSInput(
        waypoint_id="WP-TEST-001",
        wqs_score=75.0,
        success_history=80.0,
        weather_correlation=70.0,
        activity_history=75.0,
        accessibility=72.0
    )


@pytest.fixture
def legal_context(wqs_input):
    """Contexte avec heure légale."""
    tz = ZoneInfo("America/Montreal")
    target_dt = datetime.combine(
        datetime.now(tz).date(),
        time(10, 0),
        tzinfo=tz
    )
    return HeatmapFusionContext(
        waypoint_id="WP-TEST-001",
        latitude=46.8139,
        longitude=-71.2082,
        target_datetime=target_dt,
        species="moose",
        wqs_input=wqs_input,
        grid_radius_km=3.0,
        grid_resolution=5,  # 5x5 = 25 cellules pour tests rapides
        region="CA-QC"
    )


@pytest.fixture
def illegal_context(wqs_input):
    """Contexte avec heure illégale."""
    tz = ZoneInfo("America/Montreal")
    target_dt = datetime.combine(
        datetime.now(tz).date(),
        time(2, 0),  # 2h du matin = illégal
        tzinfo=tz
    )
    return HeatmapFusionContext(
        waypoint_id="WP-TEST-002",
        latitude=46.8139,
        longitude=-71.2082,
        target_datetime=target_dt,
        species="moose",
        wqs_input=wqs_input,
        grid_radius_km=3.0,
        grid_resolution=5,
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
        assert isinstance(service, HeatmapFusionService)
    
    def test_singleton_pattern(self):
        """Test du pattern singleton."""
        service1 = get_heatmap_fusion_service()
        service2 = get_heatmap_fusion_service()
        assert service1 is service2
    
    def test_weights_sum_to_one(self):
        """Les poids WQS + SCORE_FINAL = 1."""
        assert WQS_WEIGHT + SCORE_FINAL_WEIGHT == 1.0
    
    def test_heatmap_colors_defined(self):
        """Couleurs définies pour tous les niveaux."""
        for level in ScoreLevel:
            assert level in HEATMAP_COLORS
            assert "color" in HEATMAP_COLORS[level]
            assert "opacity" in HEATMAP_COLORS[level]


# =============================================================================
# TESTS: Data Contracts
# =============================================================================

class TestDataContracts:
    """Tests des data contracts."""
    
    def test_wqs_input_creation(self, wqs_input):
        """Test création WQSInput."""
        assert wqs_input.wqs_score == 75.0
        assert wqs_input.waypoint_id == "WP-TEST-001"
        
        data = wqs_input.to_dict()
        assert "wqs_score" in data
        assert "components" in data
    
    def test_fusion_context_creation(self, legal_context):
        """Test création HeatmapFusionContext."""
        assert legal_context.waypoint_id == "WP-TEST-001"
        assert legal_context.grid_resolution == 5
        assert legal_context.species == "moose"
    
    def test_context_to_score_context(self, legal_context):
        """Test conversion vers ScoreContext."""
        score_ctx = legal_context.to_score_context()
        assert score_ctx.waypoint_id == legal_context.waypoint_id
        assert score_ctx.latitude == legal_context.latitude
        assert score_ctx.species == legal_context.species
    
    def test_heatmap_result_level_calculation(self):
        """Test calcul niveau depuis valeur."""
        assert HeatmapUnifieeResult.get_level_from_value(90) == ScoreLevel.EXCELLENT
        assert HeatmapUnifieeResult.get_level_from_value(75) == ScoreLevel.GOOD
        assert HeatmapUnifieeResult.get_level_from_value(55) == ScoreLevel.MODERATE
        assert HeatmapUnifieeResult.get_level_from_value(35) == ScoreLevel.POOR
        assert HeatmapUnifieeResult.get_level_from_value(15) == ScoreLevel.VERY_POOR


# =============================================================================
# TESTS: Fusion WQS + SCORE_FINAL
# =============================================================================

class TestFusionCalculation:
    """Tests de fusion des scores."""
    
    def test_calculate_returns_result(self, service, legal_context):
        """calculate() retourne un HeatmapUnifieeResult."""
        result = service.calculate_fused_heatmap(legal_context)
        assert isinstance(result, HeatmapUnifieeResult)
    
    def test_fusion_formula(self, service, legal_context):
        """Vérifie la formule de fusion 40% WQS + 60% SCORE_FINAL."""
        result = service.calculate_fused_heatmap(legal_context)
        
        # Calculer manuellement
        expected_fused = (result.wqs_score * WQS_WEIGHT) + (result.score_final * SCORE_FINAL_WEIGHT)
        
        # Tolérance de 0.5 pour les arrondis
        assert abs(result.central_fused_score - expected_fused) < 0.5
    
    def test_wqs_preserved(self, service, legal_context):
        """Le WQS en entrée est préservé."""
        result = service.calculate_fused_heatmap(legal_context)
        assert result.wqs_score == legal_context.wqs_input.wqs_score
    
    def test_score_final_calculated(self, service, legal_context):
        """Le SCORE_FINAL est calculé via UnifiedScoringService."""
        result = service.calculate_fused_heatmap(legal_context)
        # SCORE_FINAL devrait être entre 0 et 100
        assert 0 <= result.score_final <= 100
    
    def test_central_score_in_range(self, service, legal_context):
        """Le score fusionné central est entre 0 et 100."""
        result = service.calculate_fused_heatmap(legal_context)
        assert 0 <= result.central_fused_score <= 100


# =============================================================================
# TESTS: Génération de Grille
# =============================================================================

class TestGridGeneration:
    """Tests de génération de grille."""
    
    def test_grid_cells_count(self, service, legal_context):
        """Nombre de cellules = résolution²."""
        result = service.calculate_fused_heatmap(legal_context)
        expected_count = legal_context.grid_resolution ** 2
        assert len(result.cells) == expected_count
    
    def test_grid_bounds_calculated(self, service, legal_context):
        """Les bornes de la grille sont calculées."""
        result = service.calculate_fused_heatmap(legal_context)
        
        bounds = result.grid_bounds
        assert "north" in bounds
        assert "south" in bounds
        assert "east" in bounds
        assert "west" in bounds
        
        # Nord > Sud, Est > Ouest
        assert bounds["north"] > bounds["south"]
        assert bounds["east"] > bounds["west"]
    
    def test_cells_have_coordinates(self, service, legal_context):
        """Chaque cellule a des coordonnées."""
        result = service.calculate_fused_heatmap(legal_context)
        
        for cell in result.cells:
            assert isinstance(cell.center_lat, float)
            assert isinstance(cell.center_lng, float)
            assert -90 <= cell.center_lat <= 90
            assert -180 <= cell.center_lng <= 180
    
    def test_cells_have_scores(self, service, legal_context):
        """Chaque cellule a un score fusionné."""
        result = service.calculate_fused_heatmap(legal_context)
        
        for cell in result.cells:
            assert 0 <= cell.fused_score <= 100
            assert isinstance(cell.level, ScoreLevel)
    
    def test_cells_have_sub_scores(self, service, legal_context):
        """Chaque cellule a les sous-scores."""
        result = service.calculate_fused_heatmap(legal_context)
        
        for cell in result.cells:
            assert hasattr(cell, 'density_score')
            assert hasattr(cell, 'pressure_score')
            assert hasattr(cell, 'mobility_score')
            assert hasattr(cell, 'risk_score')


# =============================================================================
# TESTS: Conformité Légale
# =============================================================================

class TestLegalCompliance:
    """Tests de conformité aux heures légales."""
    
    def test_legal_period_cells_have_scores(self, service, legal_context):
        """Période légale = cellules avec scores > 0."""
        result = service.calculate_fused_heatmap(legal_context)
        
        # Au moins une cellule devrait avoir un score > 0
        scores = [c.fused_score for c in result.cells]
        assert max(scores) > 0
    
    def test_illegal_period_cells_zero(self, service, illegal_context):
        """Période illégale = toutes les cellules à 0."""
        result = service.calculate_fused_heatmap(illegal_context)
        
        for cell in result.cells:
            assert cell.fused_score == 0
            assert cell.is_legal_period is False
    
    def test_legal_window_present(self, service, legal_context):
        """La fenêtre légale est présente."""
        result = service.calculate_fused_heatmap(legal_context)
        assert result.legal_window is not None
    
    def test_legal_badge_in_cells(self, service, legal_context):
        """Les cellules ont un badge légal."""
        result = service.calculate_fused_heatmap(legal_context)
        
        for cell in result.cells:
            assert "⚖️" in cell.legal_badge or "❌" in cell.legal_badge
    
    def test_illegal_badge_when_illegal(self, service, illegal_context):
        """Badge ❌ quand illégal."""
        result = service.calculate_fused_heatmap(illegal_context)
        
        for cell in result.cells:
            assert "❌" in cell.legal_badge


# =============================================================================
# TESTS: Statistiques
# =============================================================================

class TestStatistics:
    """Tests des statistiques de heatmap."""
    
    def test_statistics_calculated(self, service, legal_context):
        """Les statistiques sont calculées."""
        result = service.calculate_fused_heatmap(legal_context)
        
        stats = result.statistics
        assert isinstance(stats, HeatmapStatistics)
    
    def test_statistics_total_cells(self, service, legal_context):
        """Total des cellules correct."""
        result = service.calculate_fused_heatmap(legal_context)
        
        assert result.statistics.total_cells == len(result.cells)
    
    def test_statistics_distribution(self, service, legal_context):
        """Distribution par niveau calculée."""
        result = service.calculate_fused_heatmap(legal_context)
        stats = result.statistics
        
        total_distribution = (
            stats.cells_excellent + 
            stats.cells_good + 
            stats.cells_moderate + 
            stats.cells_poor + 
            stats.cells_very_poor
        )
        assert total_distribution == stats.total_cells
    
    def test_statistics_min_max(self, service, legal_context):
        """Min/Max cohérents."""
        result = service.calculate_fused_heatmap(legal_context)
        stats = result.statistics
        
        assert stats.min_score <= stats.average_score <= stats.max_score
    
    def test_hotspot_center_calculated(self, service, legal_context):
        """Centre des hotspots calculé."""
        result = service.calculate_fused_heatmap(legal_context)
        stats = result.statistics
        
        assert stats.hotspot_center_lat != 0 or stats.hotspot_center_lng != 0


# =============================================================================
# TESTS: Sérialisation
# =============================================================================

class TestSerialization:
    """Tests de sérialisation."""
    
    def test_result_to_dict(self, service, legal_context):
        """Le résultat se sérialise en dict."""
        result = service.calculate_fused_heatmap(legal_context)
        data = result.to_dict()
        
        assert isinstance(data, dict)
        assert "heatmap_id" in data
        assert "central_score" in data
        assert "sources" in data
        assert "cells" in data
        assert "statistics" in data
    
    def test_cells_serialization(self, service, legal_context):
        """Les cellules se sérialisent correctement."""
        result = service.calculate_fused_heatmap(legal_context)
        data = result.to_dict()
        
        assert len(data["cells"]) == len(result.cells)
        
        for cell_data in data["cells"]:
            assert "position" in cell_data
            assert "coordinates" in cell_data
            assert "fused_score" in cell_data
            assert "sub_scores" in cell_data
    
    def test_statistics_serialization(self, service, legal_context):
        """Les statistiques se sérialisent."""
        result = service.calculate_fused_heatmap(legal_context)
        data = result.to_dict()
        
        stats = data["statistics"]
        assert "total_cells" in stats
        assert "distribution" in stats
        assert "statistics" in stats
        assert "hotspot_center" in stats
    
    def test_metadata_present(self, service, legal_context):
        """Les métadonnées sont présentes."""
        result = service.calculate_fused_heatmap(legal_context)
        
        assert "calculation_time_ms" in result.metadata
        assert "wqs_weight" in result.metadata
        assert result.metadata["wqs_weight"] == WQS_WEIGHT


# =============================================================================
# TESTS: Waypoint-Centric
# =============================================================================

class TestWaypointCentric:
    """Tests de conformité waypoint-centric."""
    
    def test_context_preserved(self, service, legal_context):
        """Le contexte est préservé."""
        result = service.calculate_fused_heatmap(legal_context)
        
        assert result.context.waypoint_id == legal_context.waypoint_id
        assert result.context.species == legal_context.species
    
    def test_grid_centered_on_waypoint(self, service, legal_context):
        """La grille est centrée sur le waypoint."""
        result = service.calculate_fused_heatmap(legal_context)
        
        # Le centre de la grille devrait être proche du waypoint
        bounds = result.grid_bounds
        center_lat = (bounds["north"] + bounds["south"]) / 2
        center_lng = (bounds["east"] + bounds["west"]) / 2
        
        # Tolérance de 0.001 degré (~100m)
        assert abs(center_lat - legal_context.latitude) < 0.001
        assert abs(center_lng - legal_context.longitude) < 0.001


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
