"""
BIONIC V5 — PHASE B: Unit Tests for Advanced Factors per Service
==================================================================

Deep dive unit tests to verify the internal implementation of:
1. social_hierarchy component in ScoreBehaviorService
2. digestive_cycle component in ScoreBehaviorService
3. weak_signals component in ScoreBehaviorService + ScoreRiskService
4. interspecies_competition component in ScoreMultiFactorService
5. digestive_mobility component in ScoreMobilityService

Uses direct service instantiation for component verification.
"""

import pytest
import sys
import os
from datetime import datetime, timezone

# Add backend to path for imports
sys.path.insert(0, '/app/backend')

from modules.bionic_engine_p0.services.scoring.base_score_service import ScoreContext
from modules.bionic_engine_p0.services.scoring.score_behavior_service import ScoreBehaviorService
from modules.bionic_engine_p0.services.scoring.score_multifactor_service import ScoreMultiFactorService
from modules.bionic_engine_p0.services.scoring.score_risk_service import ScoreRiskService
from modules.bionic_engine_p0.services.scoring.score_mobility_service import ScoreMobilityService
from modules.bionic_engine_p0.services.unified_scoring_service import (
    get_unified_scoring_service,
    UnifiedScoringService
)
from modules.bionic_engine_p0.knowledge.species.advanced_factors import (
    get_advanced_factors_registry,
    SocialRank,
    DigestivePhase,
    WeakSignalType,
    CompetitionType
)


class TestAdvancedFactorsRegistryUnit:
    """Unit tests for AdvancedFactorsRegistry"""
    
    def test_registry_initialization(self):
        """Test registry initializes with moose and deer factors"""
        registry = get_advanced_factors_registry()
        
        # Social rules
        moose_social = registry.get_social_rules("moose")
        assert len(moose_social) > 0, "Expected moose social rules"
        
        deer_social = registry.get_social_rules("deer")
        assert len(deer_social) > 0, "Expected deer social rules"
        
        print(f"✓ Registry has {len(moose_social)} moose social rules and {len(deer_social)} deer social rules")
    
    def test_social_modifier_alpha_moose(self):
        """Test social modifier for alpha moose"""
        registry = get_advanced_factors_registry()
        
        modifier, source_ids = registry.get_social_modifier(
            species="moose",
            social_rank=SocialRank.ALPHA,
            season="rut",
            is_rut=True
        )
        
        assert modifier > 1.0, f"Expected alpha modifier > 1.0, got {modifier}"
        assert len(source_ids) > 0, "Expected source_ids for traceability"
        print(f"✓ Alpha moose modifier (rut): {modifier:.2f}, sources: {source_ids}")
    
    def test_social_modifier_subordinate_moose(self):
        """Test social modifier for subordinate moose"""
        registry = get_advanced_factors_registry()
        
        modifier, source_ids = registry.get_social_modifier(
            species="moose",
            social_rank=SocialRank.SUBORDINATE,
            season="rut",
            is_rut=True
        )
        
        assert modifier < 1.0, f"Expected subordinate modifier < 1.0, got {modifier}"
        print(f"✓ Subordinate moose modifier (rut): {modifier:.2f}")
    
    def test_competition_rules_moose(self):
        """Test competition rules for moose"""
        registry = get_advanced_factors_registry()
        
        # Moose vs deer competition
        rules = registry.get_competition_rules("moose", "deer")
        assert len(rules) > 0, "Expected moose-deer competition rules"
        
        # Verify rule structure
        rule = rules[0]
        assert rule.competition_type in [CompetitionType.FOOD, CompetitionType.SPACE]
        assert 0 <= rule.competition_intensity <= 1.0
        assert len(rule.source_ids) > 0
        
        print(f"✓ Moose-deer competition: intensity={rule.competition_intensity}, type={rule.competition_type.value}")
    
    def test_competition_score_modifier(self):
        """Test competition score modifier calculation"""
        registry = get_advanced_factors_registry()
        
        # With deer competitor
        modifier, sources = registry.get_competition_score_modifier(
            species="moose",
            competitors_present=["deer"],
            habitat="mixed_forest"
        )
        
        assert modifier <= 1.0, "Competition should reduce score (modifier <= 1.0)"
        print(f"✓ Competition modifier with deer: {modifier:.2f}")
        
        # Without competitors
        modifier_no_comp, _ = registry.get_competition_score_modifier(
            species="moose",
            competitors_present=[],
            habitat="mixed_forest"
        )
        
        assert modifier_no_comp == 1.0, "No competition should yield modifier = 1.0"
        print(f"✓ Competition modifier without competitors: {modifier_no_comp:.2f}")
    
    def test_digestive_cycles_moose(self):
        """Test digestive cycles for moose"""
        registry = get_advanced_factors_registry()
        
        cycles = registry.get_digestive_cycles("moose")
        assert len(cycles) >= 4, f"Expected at least 4 digestive cycles, got {len(cycles)}"
        
        phases = [c.phase for c in cycles]
        assert DigestivePhase.ACTIVE_FEEDING in phases
        assert DigestivePhase.RUMINATION in phases
        assert DigestivePhase.REST_DIGESTION in phases
        assert DigestivePhase.WATER_SEEKING in phases
        
        print(f"✓ Moose has {len(cycles)} digestive cycles: {[p.value for p in phases]}")
    
    def test_current_digestive_phase(self):
        """Test current digestive phase detection"""
        registry = get_advanced_factors_registry()
        
        # Test morning (feeding hour)
        cycle_6h, sources_6h = registry.get_current_digestive_phase("moose", 6)
        assert cycle_6h is not None
        assert cycle_6h.phase == DigestivePhase.ACTIVE_FEEDING
        print(f"✓ Hour 6: {cycle_6h.phase.value}, mobility={cycle_6h.mobility_level}")
        
        # Test midday (rumination)
        cycle_10h, sources_10h = registry.get_current_digestive_phase("moose", 10)
        assert cycle_10h is not None
        assert cycle_10h.phase == DigestivePhase.RUMINATION
        print(f"✓ Hour 10: {cycle_10h.phase.value}, mobility={cycle_10h.mobility_level}")
    
    def test_weak_signals_moose(self):
        """Test weak signals for moose"""
        registry = get_advanced_factors_registry()
        
        signals = registry.get_weak_signals("moose")
        assert len(signals) >= 3, f"Expected at least 3 weak signals, got {len(signals)}"
        
        signal_types = [s.signal_type for s in signals]
        assert WeakSignalType.PREDATION_ALERT in signal_types
        assert WeakSignalType.STRESS_INDICATOR in signal_types
        
        print(f"✓ Moose has {len(signals)} weak signals: {[t.value for t in signal_types]}")
    
    def test_evaluate_weak_signals(self):
        """Test weak signal evaluation"""
        registry = get_advanced_factors_registry()
        
        # Test with rut indicators
        impact, detected, sources = registry.evaluate_weak_signals(
            species="moose",
            observed_indicators=["Frottoirs frais", "Vocalises mâles"]
        )
        
        assert len(detected) > 0, "Expected to detect rut signals"
        assert impact != 0, "Expected non-zero impact"
        print(f"✓ Rut indicators impact: {impact:+.0f} pts, detected: {len(detected)} signals")
        
        # Test with stress indicators
        impact_stress, detected_stress, _ = registry.evaluate_weak_signals(
            species="moose",
            observed_indicators=["Alimentation réduite", "Évitement de zones habituelles"]
        )
        
        if detected_stress:
            print(f"✓ Stress indicators impact: {impact_stress:+.0f} pts")
    
    def test_calculate_advanced_modifier(self):
        """Test combined advanced modifier calculation"""
        registry = get_advanced_factors_registry()
        
        result = registry.calculate_advanced_modifier(
            species="moose",
            hour=6,
            season="rut",
            social_rank=SocialRank.ALPHA,
            competitors_present=["deer"],
            observed_indicators=["Frottoirs frais"],
            habitat="mixed_forest"
        )
        
        assert "total_modifier" in result
        assert "factors" in result
        assert "source_ids" in result
        assert "confidence" in result
        
        assert "social_hierarchy" in result["factors"]
        assert "interspecies_competition" in result["factors"]
        assert "digestive_cycle" in result["factors"]
        
        print(f"✓ Combined modifier: {result['total_modifier']:.2f}")
        print(f"  - Factors: {list(result['factors'].keys())}")
        print(f"  - Sources: {len(result['source_ids'])} source_ids")


class TestScoreBehaviorServiceUnit:
    """Unit tests for ScoreBehaviorService PHASE B components"""
    
    @pytest.fixture
    def service(self):
        return ScoreBehaviorService()
    
    @pytest.fixture
    def context(self):
        return ScoreContext(
            waypoint_id="TEST-UNIT-001",
            latitude=46.85,
            longitude=-71.25,
            target_datetime=datetime.now(timezone.utc),
            species="moose",
            region="QC",
            search_radius_km=5.0
        )
    
    def test_service_has_advanced_factors(self, service):
        """Verify service has advanced factors registry"""
        assert hasattr(service, '_advanced_factors')
        assert service._advanced_factors is not None
        print("✓ ScoreBehaviorService has _advanced_factors registry")
    
    def test_calculate_returns_social_hierarchy_component(self, service, context):
        """Verify social_hierarchy component is calculated"""
        result = service.calculate(context)
        
        component_names = [c.name for c in result.components]
        assert "social_hierarchy" in component_names, f"Expected social_hierarchy, got: {component_names}"
        
        social_comp = next(c for c in result.components if c.name == "social_hierarchy")
        assert 0 <= social_comp.value <= 100
        assert social_comp.weight > 0
        
        print(f"✓ social_hierarchy component: value={social_comp.value:.1f}, weight={social_comp.weight}")
    
    def test_calculate_returns_digestive_cycle_component(self, service, context):
        """Verify digestive_cycle component is calculated"""
        result = service.calculate(context)
        
        component_names = [c.name for c in result.components]
        assert "digestive_cycle" in component_names, f"Expected digestive_cycle, got: {component_names}"
        
        digest_comp = next(c for c in result.components if c.name == "digestive_cycle")
        assert 0 <= digest_comp.value <= 100
        
        print(f"✓ digestive_cycle component: value={digest_comp.value:.1f}, weight={digest_comp.weight}")
    
    def test_calculate_returns_weak_signals_component(self, service, context):
        """Verify weak_signals component is calculated"""
        result = service.calculate(context)
        
        component_names = [c.name for c in result.components]
        assert "weak_signals" in component_names, f"Expected weak_signals, got: {component_names}"
        
        signals_comp = next(c for c in result.components if c.name == "weak_signals")
        assert 0 <= signals_comp.value <= 100
        
        print(f"✓ weak_signals component: value={signals_comp.value:.1f}, weight={signals_comp.weight}")


class TestScoreMultiFactorServiceUnit:
    """Unit tests for ScoreMultiFactorService PHASE B components"""
    
    @pytest.fixture
    def service(self):
        return ScoreMultiFactorService()
    
    @pytest.fixture
    def context(self):
        return ScoreContext(
            waypoint_id="TEST-UNIT-002",
            latitude=46.85,
            longitude=-71.25,
            target_datetime=datetime.now(timezone.utc),
            species="moose",
            region="QC",
            search_radius_km=5.0
        )
    
    def test_service_has_advanced_factors(self, service):
        """Verify service has advanced factors registry"""
        assert hasattr(service, '_advanced_factors')
        assert service._advanced_factors is not None
        print("✓ ScoreMultiFactorService has _advanced_factors registry")
    
    def test_calculate_returns_interspecies_competition_component(self, service, context):
        """Verify interspecies_competition component is calculated"""
        result = service.calculate(context)
        
        component_names = [c.name for c in result.components]
        assert "interspecies_competition" in component_names, f"Expected interspecies_competition, got: {component_names}"
        
        comp_comp = next(c for c in result.components if c.name == "interspecies_competition")
        assert 0 <= comp_comp.value <= 100
        
        print(f"✓ interspecies_competition component: value={comp_comp.value:.1f}, weight={comp_comp.weight}")


class TestScoreRiskServiceUnit:
    """Unit tests for ScoreRiskService PHASE B components"""
    
    @pytest.fixture
    def service(self):
        return ScoreRiskService()
    
    @pytest.fixture
    def context(self):
        return ScoreContext(
            waypoint_id="TEST-UNIT-003",
            latitude=46.85,
            longitude=-71.25,
            target_datetime=datetime.now(timezone.utc),
            species="moose",
            region="QC",
            search_radius_km=5.0
        )
    
    def test_service_has_advanced_factors(self, service):
        """Verify service has advanced factors registry"""
        assert hasattr(service, '_advanced_factors')
        assert service._advanced_factors is not None
        print("✓ ScoreRiskService has _advanced_factors registry")
    
    def test_calculate_returns_risk_weak_signals_component(self, service, context):
        """Verify risk_weak_signals component is calculated"""
        result = service.calculate(context)
        
        component_names = [c.name for c in result.components]
        assert "risk_weak_signals" in component_names, f"Expected risk_weak_signals, got: {component_names}"
        
        risk_sig_comp = next(c for c in result.components if c.name == "risk_weak_signals")
        assert 0 <= risk_sig_comp.value <= 100
        
        print(f"✓ risk_weak_signals component: value={risk_sig_comp.value:.1f}, weight={risk_sig_comp.weight}")


class TestScoreMobilityServiceUnit:
    """Unit tests for ScoreMobilityService PHASE B components"""
    
    @pytest.fixture
    def service(self):
        return ScoreMobilityService()
    
    @pytest.fixture
    def context(self):
        return ScoreContext(
            waypoint_id="TEST-UNIT-004",
            latitude=46.85,
            longitude=-71.25,
            target_datetime=datetime.now(timezone.utc),
            species="moose",
            region="QC",
            search_radius_km=5.0
        )
    
    def test_service_has_advanced_factors(self, service):
        """Verify service has advanced factors registry"""
        assert hasattr(service, '_advanced_factors')
        assert service._advanced_factors is not None
        print("✓ ScoreMobilityService has _advanced_factors registry")
    
    def test_calculate_returns_digestive_mobility_component(self, service, context):
        """Verify digestive_mobility component is calculated"""
        result = service.calculate(context)
        
        component_names = [c.name for c in result.components]
        assert "digestive_mobility" in component_names, f"Expected digestive_mobility, got: {component_names}"
        
        dig_mob_comp = next(c for c in result.components if c.name == "digestive_mobility")
        assert 0 <= dig_mob_comp.value <= 100
        
        print(f"✓ digestive_mobility component: value={dig_mob_comp.value:.1f}, weight={dig_mob_comp.weight}")


class TestUnifiedScoringServiceUnit:
    """Unit tests for UnifiedScoringService PHASE B integration"""
    
    @pytest.fixture
    def service(self):
        return get_unified_scoring_service()
    
    @pytest.fixture
    def context(self):
        return ScoreContext(
            waypoint_id="TEST-UNIFIED-001",
            latitude=46.85,
            longitude=-71.25,
            target_datetime=datetime.now(timezone.utc),
            species="moose",
            region="QC",
            search_radius_km=5.0
        )
    
    def test_unified_service_has_advanced_factors(self, service):
        """Verify unified service has advanced factors registry"""
        assert hasattr(service, '_advanced_factors')
        assert service._advanced_factors is not None
        print("✓ UnifiedScoringService has _advanced_factors registry")
    
    def test_unified_result_has_advanced_factors_details(self, service, context):
        """Verify unified result includes advanced_factors_details"""
        result = service.calculate_unified_score(context, analysis_mode="rut")
        
        assert hasattr(result, 'advanced_factors_modifier')
        assert hasattr(result, 'advanced_factors_details')
        
        details = result.advanced_factors_details
        assert "integration_mode" in details
        assert details["integration_mode"] == "by_service"
        
        assert "integrated_services" in details
        
        print(f"✓ advanced_factors_modifier: {result.advanced_factors_modifier:.2f}")
        print(f"✓ integration_mode: {details['integration_mode']}")
        print(f"✓ integrated_services: {len(details['integrated_services'])}")
    
    def test_unified_result_metadata_version(self, service, context):
        """Verify unified result metadata contains PHASE B version"""
        result = service.calculate_unified_score(context, analysis_mode="rut")
        
        metadata = result.metadata
        assert "version" in metadata
        assert "PHASE-B" in metadata["version"]
        assert "advanced_factors_phase" in metadata
        assert metadata["advanced_factors_phase"] == "B"
        
        print(f"✓ Metadata version: {metadata['version']}")
        print(f"✓ advanced_factors_phase: {metadata['advanced_factors_phase']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
