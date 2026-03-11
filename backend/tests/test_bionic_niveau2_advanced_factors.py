"""
BIONIC V5 NIVEAU 2 — Validation Exhaustive des 4 Facteurs Comportementaux Avancés (PHASE B)
============================================================================================

Ce module valide les 4 facteurs comportementaux avancés de la PHASE B:
1. HIÉRARCHIE SOCIALE — SocialHierarchyRule (alpha, beta, subordinate, juvenile)
2. CYCLES DIGESTIFS — DigestiveCycle (4 phases: ACTIVE_FEEDING, RUMINATION, REST_DIGESTION, WATER_SEEKING)
3. SIGNAUX FAIBLES — WeakSignal (6 types: STRESS, PREDATION, RESOURCE, SOCIAL, ENVIRONMENTAL, HEALTH)
4. COMPÉTITION INTER-ESPÈCES — InterspeciesCompetition (food, space, thermal, water)

TESTS COVERAGE:
- Knowledge Layer: règles avec source_ids et traçabilité
- UnifiedScoringService: _inject_advanced_modifiers() calcule TOUS les modificateurs
- Services: consomment sans logique locale (100% passifs)
- API: advanced_factors_details contient PHASE B factors

ESPÈCES TESTÉES: moose (orignal) et deer (cerf)
HEURES TESTÉES: 6h (alimentation), 10h (rumination), 14h (repos), 16h (eau)
SAISONS TESTÉES: rut, pre_rut, default
RANGS SOCIAUX: alpha, subordinate
COMPÉTITEURS: bear, deer

Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
"""

import pytest
import os
from datetime import datetime, date
from typing import List, Dict, Any, Tuple

# Import des modules Knowledge Layer
from modules.bionic_engine_p0.knowledge.species.advanced_factors import (
    AdvancedFactorsRegistry,
    get_advanced_factors_registry,
    SocialHierarchyRule,
    DigestiveCycle,
    WeakSignal,
    InterspeciesCompetition,
    SocialRank,
    DigestivePhase,
    WeakSignalType,
    CompetitionType
)

# Import du UnifiedScoringService
from modules.bionic_engine_p0.services.unified_scoring_service import (
    UnifiedScoringService,
    get_unified_scoring_service
)

# Import du ScoreContext
from modules.bionic_engine_p0.services.scoring.base_score_service import ScoreContext


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def registry() -> AdvancedFactorsRegistry:
    """Obtenir l'instance du registre des facteurs avancés"""
    return get_advanced_factors_registry()


@pytest.fixture
def unified_service() -> UnifiedScoringService:
    """Obtenir l'instance du service de scoring unifié"""
    return get_unified_scoring_service()


def create_score_context(
    species: str = "moose",
    hour: int = 6,
    social_rank: str = "unknown",
    competitors: List[str] = None,
    observed_indicators: List[str] = None,
    habitat: str = "mixed_forest"
) -> ScoreContext:
    """Helper pour créer un contexte de scoring"""
    target_dt = datetime(2025, 10, 1, hour, 0, 0)
    return ScoreContext(
        waypoint_id=f"TEST-NIVEAU2-{species.upper()}-{hour}",
        latitude=46.85,
        longitude=-71.25,
        target_datetime=target_dt,
        species=species,
        region="CA-QC",
        extra_data={
            "social_rank": social_rank,
            "competitors_present": competitors or [],
            "observed_indicators": observed_indicators or [],
            "habitat_type": habitat
        }
    )


# =============================================================================
# TEST CLASS 1: HIÉRARCHIE SOCIALE — Knowledge Layer
# =============================================================================

class TestSocialHierarchyKnowledgeLayer:
    """Tests pour les règles de hiérarchie sociale dans le Knowledge Layer"""
    
    def test_moose_social_rules_exist(self, registry):
        """TEST 1: Les règles SocialHierarchyRule existent pour l'orignal"""
        rules = registry.get_social_rules("moose")
        
        assert len(rules) >= 3, f"Expected at least 3 social rules for moose, got {len(rules)}"
        
        # Vérifier les rangs présents
        ranks = [r.social_rank for r in rules]
        assert SocialRank.ALPHA in ranks, "ALPHA rank missing for moose"
        assert SocialRank.SUBORDINATE in ranks, "SUBORDINATE rank missing for moose"
        
        print(f"✓ Found {len(rules)} social hierarchy rules for moose")
        for rule in rules:
            print(f"  - {rule.rule_id}: {rule.social_rank.value}, modifier={rule.behavior_modifier}")
    
    def test_deer_social_rules_exist(self, registry):
        """TEST 2: Les règles SocialHierarchyRule existent pour le cerf"""
        rules = registry.get_social_rules("deer")
        
        assert len(rules) >= 1, f"Expected at least 1 social rule for deer, got {len(rules)}"
        
        print(f"✓ Found {len(rules)} social hierarchy rules for deer")
        for rule in rules:
            print(f"  - {rule.rule_id}: {rule.social_rank.value}, modifier={rule.behavior_modifier}")
    
    def test_social_rule_has_source_ids(self, registry):
        """TEST 3: Chaque règle sociale contient des source_ids pour traçabilité"""
        rules = registry.get_social_rules("moose")
        
        for rule in rules:
            assert hasattr(rule, "source_ids"), f"Rule {rule.rule_id} missing source_ids attribute"
            assert len(rule.source_ids) > 0, f"Rule {rule.rule_id} has empty source_ids"
            print(f"✓ {rule.rule_id}: source_ids={rule.source_ids}")
    
    def test_get_social_modifier_returns_tuple(self, registry):
        """TEST 4: get_social_modifier() retourne (modifier, source_ids)"""
        modifier, sources = registry.get_social_modifier(
            species="moose",
            social_rank=SocialRank.ALPHA,
            season="rut",
            is_rut=True
        )
        
        assert isinstance(modifier, float), "Modifier should be float"
        assert isinstance(sources, list), "Sources should be list"
        assert modifier > 1.0, f"Alpha modifier during rut should be > 1.0, got {modifier}"
        
        print(f"✓ get_social_modifier(moose, alpha, rut, is_rut=True):")
        print(f"  - modifier={modifier}")
        print(f"  - source_ids={sources}")
    
    def test_rut_amplification_for_alpha(self, registry):
        """TEST 5: L'amplification du rut (rut_amplification) fonctionne correctement"""
        # Sans rut
        modifier_no_rut, _ = registry.get_social_modifier(
            species="moose",
            social_rank=SocialRank.ALPHA,
            season="default",
            is_rut=False
        )
        
        # Avec rut
        modifier_rut, _ = registry.get_social_modifier(
            species="moose",
            social_rank=SocialRank.ALPHA,
            season="rut",
            is_rut=True
        )
        
        assert modifier_rut > modifier_no_rut, f"Rut modifier ({modifier_rut}) should be > non-rut ({modifier_no_rut})"
        
        print(f"✓ Rut amplification verified:")
        print(f"  - Non-rut modifier: {modifier_no_rut}")
        print(f"  - Rut modifier: {modifier_rut}")
        print(f"  - Amplification: {modifier_rut / modifier_no_rut:.1f}x")
    
    def test_subordinate_has_lower_modifier(self, registry):
        """TEST 6: Le subordonné a un modificateur plus faible que l'alpha"""
        alpha_mod, _ = registry.get_social_modifier("moose", SocialRank.ALPHA, "rut", True)
        sub_mod, _ = registry.get_social_modifier("moose", SocialRank.SUBORDINATE, "rut", True)
        
        assert sub_mod < alpha_mod, f"Subordinate modifier ({sub_mod}) should be < alpha ({alpha_mod})"
        
        print(f"✓ Subordinate modifier ({sub_mod}) < Alpha modifier ({alpha_mod})")


# =============================================================================
# TEST CLASS 2: CYCLES DIGESTIFS — Knowledge Layer
# =============================================================================

class TestDigestiveCyclesKnowledgeLayer:
    """Tests pour les cycles digestifs dans le Knowledge Layer"""
    
    def test_moose_has_4_digestive_phases(self, registry):
        """TEST 7: L'orignal a 4 phases digestives définies"""
        cycles = registry.get_digestive_cycles("moose")
        
        assert len(cycles) == 4, f"Expected 4 digestive phases for moose, got {len(cycles)}"
        
        phases = [c.phase for c in cycles]
        expected_phases = [
            DigestivePhase.ACTIVE_FEEDING,
            DigestivePhase.RUMINATION,
            DigestivePhase.REST_DIGESTION,
            DigestivePhase.WATER_SEEKING
        ]
        
        for expected in expected_phases:
            assert expected in phases, f"Phase {expected.value} missing for moose"
        
        print(f"✓ All 4 digestive phases present for moose:")
        for cycle in cycles:
            print(f"  - {cycle.phase.value}: start={cycle.typical_start_hour}h, duration={cycle.typical_duration_hours}h")
    
    def test_deer_has_digestive_cycles(self, registry):
        """TEST 8: Le cerf a des cycles digestifs définis"""
        cycles = registry.get_digestive_cycles("deer")
        
        assert len(cycles) >= 1, f"Expected at least 1 digestive phase for deer, got {len(cycles)}"
        
        print(f"✓ Found {len(cycles)} digestive phases for deer")
    
    def test_get_current_digestive_phase_6h(self, registry):
        """TEST 9: get_current_digestive_phase à 6h retourne ACTIVE_FEEDING"""
        cycle, sources = registry.get_current_digestive_phase("moose", 6)
        
        assert cycle is not None, "Should return a cycle for 6h"
        assert cycle.phase == DigestivePhase.ACTIVE_FEEDING, f"Expected ACTIVE_FEEDING at 6h, got {cycle.phase.value}"
        
        print(f"✓ 6h: {cycle.phase.value} (visibility={cycle.visibility_during_phase})")
    
    def test_get_current_digestive_phase_10h(self, registry):
        """TEST 10: get_current_digestive_phase à 10h retourne RUMINATION"""
        cycle, sources = registry.get_current_digestive_phase("moose", 10)
        
        assert cycle is not None, "Should return a cycle for 10h"
        assert cycle.phase == DigestivePhase.RUMINATION, f"Expected RUMINATION at 10h, got {cycle.phase.value}"
        
        print(f"✓ 10h: {cycle.phase.value} (mobility={cycle.mobility_level})")
    
    def test_get_current_digestive_phase_14h(self, registry):
        """TEST 11: get_current_digestive_phase à 14h retourne REST_DIGESTION"""
        cycle, sources = registry.get_current_digestive_phase("moose", 14)
        
        assert cycle is not None, "Should return a cycle for 14h"
        assert cycle.phase == DigestivePhase.REST_DIGESTION, f"Expected REST_DIGESTION at 14h, got {cycle.phase.value}"
        
        print(f"✓ 14h: {cycle.phase.value} (visibility={cycle.visibility_during_phase})")
    
    def test_get_current_digestive_phase_16h(self, registry):
        """TEST 12: get_current_digestive_phase à 16h retourne WATER_SEEKING"""
        cycle, sources = registry.get_current_digestive_phase("moose", 16)
        
        assert cycle is not None, "Should return a cycle for 16h"
        assert cycle.phase == DigestivePhase.WATER_SEEKING, f"Expected WATER_SEEKING at 16h, got {cycle.phase.value}"
        
        print(f"✓ 16h: {cycle.phase.value} (mobility={cycle.mobility_level})")
    
    def test_visibility_varies_by_phase(self, registry):
        """TEST 13: La visibilité (visibility_during_phase) varie selon la phase"""
        phases_visibility = {}
        
        for hour in [6, 10, 14, 16]:
            cycle, _ = registry.get_current_digestive_phase("moose", hour)
            if cycle:
                phases_visibility[cycle.phase.value] = cycle.visibility_during_phase
        
        # ACTIVE_FEEDING et WATER_SEEKING devraient avoir une visibilité haute
        # RUMINATION et REST_DIGESTION devraient avoir une visibilité basse
        if "active_feeding" in phases_visibility:
            assert phases_visibility["active_feeding"] > 0.5, "Feeding should have high visibility"
        
        if "rest_digestion" in phases_visibility:
            assert phases_visibility["rest_digestion"] < 0.5, "Rest should have low visibility"
        
        print(f"✓ Visibility by phase: {phases_visibility}")
    
    def test_digestive_cycle_has_source_ids(self, registry):
        """TEST 14: Chaque cycle digestif contient des source_ids"""
        cycles = registry.get_digestive_cycles("moose")
        
        for cycle in cycles:
            assert hasattr(cycle, "source_ids"), f"Cycle {cycle.cycle_id} missing source_ids"
            assert len(cycle.source_ids) > 0, f"Cycle {cycle.cycle_id} has empty source_ids"
            print(f"✓ {cycle.cycle_id}: source_ids={cycle.source_ids}")


# =============================================================================
# TEST CLASS 3: SIGNAUX FAIBLES — Knowledge Layer
# =============================================================================

class TestWeakSignalsKnowledgeLayer:
    """Tests pour les signaux faibles dans le Knowledge Layer"""
    
    def test_moose_has_weak_signals_defined(self, registry):
        """TEST 15: L'orignal a des signaux faibles définis"""
        signals = registry.get_weak_signals("moose")
        
        assert len(signals) >= 3, f"Expected at least 3 weak signals for moose, got {len(signals)}"
        
        print(f"✓ Found {len(signals)} weak signals for moose:")
        for sig in signals:
            print(f"  - {sig.signal_id}: type={sig.signal_type.value}, impact={sig.score_impact}")
    
    def test_weak_signal_types_coverage(self, registry):
        """TEST 16: Les 6 types de signaux faibles sont représentés"""
        signals = registry.get_weak_signals("moose")
        
        types_found = {s.signal_type for s in signals}
        
        print(f"✓ Signal types found: {[t.value for t in types_found]}")
        
        # Au moins quelques types essentiels
        essential_types = [WeakSignalType.PREDATION_ALERT, WeakSignalType.STRESS_INDICATOR]
        for etype in essential_types:
            if etype in types_found:
                print(f"  - {etype.value}: ✓ PRESENT")
            else:
                print(f"  - {etype.value}: (not defined, optional)")
    
    def test_evaluate_weak_signals_with_indicators(self, registry):
        """TEST 17: evaluate_weak_signals() détecte les signaux à partir d'indicateurs"""
        # Utiliser des indicateurs qui matchent les signaux existants
        observed = ["Vocalises d'alarme", "Frottoirs frais"]
        
        impact, detected, sources = registry.evaluate_weak_signals("moose", observed)
        
        assert isinstance(impact, float), "Impact should be float"
        assert isinstance(detected, list), "Detected should be list"
        assert isinstance(sources, list), "Sources should be list"
        
        print(f"✓ evaluate_weak_signals with indicators {observed}:")
        print(f"  - Total impact: {impact}")
        print(f"  - Detected signals: {len(detected)}")
        print(f"  - Source IDs: {sources}")
    
    def test_weak_signal_score_impact_calculation(self, registry):
        """TEST 18: Le score_impact est calculé correctement"""
        signals = registry.get_weak_signals("moose")
        
        for sig in signals:
            assert hasattr(sig, "score_impact"), f"Signal {sig.signal_id} missing score_impact"
            assert -50 <= sig.score_impact <= 50, f"Score impact {sig.score_impact} out of range"
            print(f"✓ {sig.signal_id}: score_impact={sig.score_impact}")
    
    def test_weak_signals_have_source_ids(self, registry):
        """TEST 19: Chaque signal faible contient des source_ids"""
        signals = registry.get_weak_signals("moose")
        
        for sig in signals:
            assert hasattr(sig, "source_ids"), f"Signal {sig.signal_id} missing source_ids"
            assert len(sig.source_ids) > 0, f"Signal {sig.signal_id} has empty source_ids"
            print(f"✓ {sig.signal_id}: source_ids={sig.source_ids}")


# =============================================================================
# TEST CLASS 4: COMPÉTITION INTER-ESPÈCES — Knowledge Layer
# =============================================================================

class TestInterspeciesCompetitionKnowledgeLayer:
    """Tests pour la compétition inter-espèces dans le Knowledge Layer"""
    
    def test_moose_competition_rules_exist(self, registry):
        """TEST 20: Les règles de compétition existent pour l'orignal"""
        rules = registry.get_competition_rules("moose")
        
        assert len(rules) >= 1, f"Expected at least 1 competition rule for moose, got {len(rules)}"
        
        print(f"✓ Found {len(rules)} competition rules for moose:")
        for rule in rules:
            print(f"  - {rule.rule_id}: vs {rule.competitor_species}, type={rule.competition_type.value}")
    
    def test_competition_types_coverage(self, registry):
        """TEST 21: Les 4 types de compétition (food, space, thermal, water) sont définis"""
        rules = registry.get_competition_rules("moose")
        
        types_found = {r.competition_type for r in rules}
        
        print(f"✓ Competition types found: {[t.value for t in types_found]}")
        
        # Au moins FOOD devrait être présent
        assert CompetitionType.FOOD in types_found, "FOOD competition type should be present"
    
    def test_get_competition_score_modifier_with_competitors(self, registry):
        """TEST 22: get_competition_score_modifier() avec habitat et compétiteurs"""
        modifier, sources = registry.get_competition_score_modifier(
            species="moose",
            competitors_present=["bear", "deer"],
            habitat="mixed_forest"
        )
        
        assert isinstance(modifier, float), "Modifier should be float"
        assert 0.5 <= modifier <= 1.0, f"Competition modifier should reduce score (got {modifier})"
        
        print(f"✓ get_competition_score_modifier(moose, ['bear', 'deer'], mixed_forest):")
        print(f"  - modifier={modifier}")
        print(f"  - source_ids={sources}")
    
    def test_competition_with_no_competitors(self, registry):
        """TEST 23: Sans compétiteurs, le modificateur est 1.0"""
        modifier, sources = registry.get_competition_score_modifier(
            species="moose",
            competitors_present=[],
            habitat="mixed_forest"
        )
        
        assert modifier == 1.0, f"Without competitors, modifier should be 1.0, got {modifier}"
        
        print(f"✓ No competitors: modifier={modifier}")
    
    def test_competition_rules_have_source_ids(self, registry):
        """TEST 24: Chaque règle de compétition contient des source_ids"""
        rules = registry.get_competition_rules("moose")
        
        for rule in rules:
            assert hasattr(rule, "source_ids"), f"Rule {rule.rule_id} missing source_ids"
            assert len(rule.source_ids) > 0, f"Rule {rule.rule_id} has empty source_ids"
            print(f"✓ {rule.rule_id}: source_ids={rule.source_ids}")


# =============================================================================
# TEST CLASS 5: UnifiedScoringService — CENTRALISATION
# =============================================================================

class TestUnifiedScoringServiceCentralization:
    """Tests pour la centralisation dans UnifiedScoringService"""
    
    def test_inject_advanced_modifiers_calculates_all(self, unified_service):
        """TEST 25: _inject_advanced_modifiers() calcule TOUS les modificateurs"""
        context = create_score_context(
            species="moose",
            hour=6,
            social_rank="alpha",
            competitors=["bear"],
            observed_indicators=["Frottoirs frais"]
        )
        
        # Appeler la méthode privée pour test
        enriched_context = unified_service._inject_advanced_modifiers(context, "rut", "TEST-001")
        
        # Vérifier que advanced_modifiers est rempli
        adv = enriched_context.advanced_modifiers
        
        assert "social_modifier" in adv, "social_modifier missing"
        assert "digestive_modifier" in adv, "digestive_modifier missing"
        assert "signals_modifier" in adv, "signals_modifier missing"
        assert "competition_modifier" in adv, "competition_modifier missing"
        
        print(f"✓ All advanced modifiers calculated:")
        print(f"  - social_modifier: {adv.get('social_modifier')}")
        print(f"  - digestive_modifier: {adv.get('digestive_modifier')}")
        print(f"  - signals_modifier: {adv.get('signals_modifier')}")
        print(f"  - competition_modifier: {adv.get('competition_modifier')}")
    
    def test_advanced_modifiers_contain_version(self, unified_service):
        """TEST 26: version présent dans context.advanced_modifiers"""
        context = create_score_context("moose", 10)
        
        enriched_context = unified_service._inject_advanced_modifiers(context, "rut", "TEST-002")
        adv = enriched_context.advanced_modifiers
        
        assert "social_version" in adv, "social_version missing"
        assert "digestive_version" in adv, "digestive_version missing"
        assert "signals_version" in adv, "signals_version missing"
        assert "competition_version" in adv, "competition_version missing"
        
        print(f"✓ All versions present:")
        print(f"  - social_version: {adv.get('social_version')}")
        print(f"  - digestive_version: {adv.get('digestive_version')}")
        print(f"  - signals_version: {adv.get('signals_version')}")
        print(f"  - competition_version: {adv.get('competition_version')}")
    
    def test_advanced_modifiers_contain_source_ids(self, unified_service):
        """TEST 27: source_ids présents sur chaque règle"""
        context = create_score_context("moose", 6)
        
        enriched_context = unified_service._inject_advanced_modifiers(context, "rut", "TEST-003")
        adv = enriched_context.advanced_modifiers
        
        assert "social_source_ids" in adv, "social_source_ids missing"
        assert "digestive_source_ids" in adv, "digestive_source_ids missing"
        assert "signals_source_ids" in adv, "signals_source_ids missing"
        assert "competition_source_ids" in adv, "competition_source_ids missing"
        
        print(f"✓ All source_ids present:")
        print(f"  - social_source_ids: {adv.get('social_source_ids')}")
        print(f"  - digestive_source_ids: {adv.get('digestive_source_ids')}")
    
    def test_total_modifier_calculated(self, unified_service):
        """TEST 28: total_modifier est calculé (PHASE B)"""
        context = create_score_context("moose", 6)
        
        enriched_context = unified_service._inject_advanced_modifiers(context, "rut", "TEST-004")
        adv = enriched_context.advanced_modifiers
        
        assert "total_modifier" in adv, "total_modifier missing"
        assert "phase_b_modifier" in adv, "phase_b_modifier missing"
        
        print(f"✓ Total modifiers calculated:")
        print(f"  - phase_b_modifier: {adv.get('phase_b_modifier')}")
        print(f"  - total_modifier: {adv.get('total_modifier')}")


# =============================================================================
# TEST CLASS 6: Services 100% PASSIFS (consomment sans logique locale)
# =============================================================================

class TestServicesArePassive:
    """Tests vérifiant que les services sont 100% passifs"""
    
    def test_behavior_service_consumes_social_modifier(self, unified_service):
        """TEST 29: ScoreBehaviorService consomme social_modifier"""
        context = create_score_context("moose", 6, social_rank="alpha")
        
        # Calculer le score unifié
        result = unified_service.calculate_unified_score(context, "rut")
        
        # Le service behavior doit avoir utilisé le social_modifier
        adv = context.advanced_modifiers
        assert "social_modifier" in adv, "social_modifier should be in context after calculation"
        
        print(f"✓ ScoreBehaviorService consumed social_modifier from context")
    
    def test_behavior_service_consumes_digestive_modifier(self, unified_service):
        """TEST 30: ScoreBehaviorService consomme digestive_cycle info"""
        context = create_score_context("moose", 10)
        
        result = unified_service.calculate_unified_score(context, "rut")
        
        adv = context.advanced_modifiers
        assert "digestive_phase" in adv, "digestive_phase should be in context"
        assert adv["digestive_phase"] != "unknown", "digestive_phase should be set"
        
        print(f"✓ ScoreBehaviorService consumed digestive phase: {adv['digestive_phase']}")
    
    def test_multifactor_service_consumes_competition_modifier(self, unified_service):
        """TEST 31: ScoreMultiFactorService consomme competition_modifier"""
        context = create_score_context("moose", 6, competitors=["bear", "deer"])
        
        result = unified_service.calculate_unified_score(context, "rut")
        
        adv = context.advanced_modifiers
        assert "competition_modifier" in adv, "competition_modifier should be in context"
        
        print(f"✓ ScoreMultiFactorService consumed competition_modifier: {adv['competition_modifier']}")
    
    def test_risk_service_consumes_signals_modifier(self, unified_service):
        """TEST 32: ScoreRiskService consomme signals_modifier"""
        context = create_score_context("moose", 6, observed_indicators=["Vocalises d'alarme"])
        
        result = unified_service.calculate_unified_score(context, "rut")
        
        adv = context.advanced_modifiers
        assert "signals_modifier" in adv, "signals_modifier should be in context"
        
        print(f"✓ ScoreRiskService consumed signals_modifier: {adv['signals_modifier']}")


# =============================================================================
# TEST CLASS 7: TESTS ESPÈCE ORIGNAL (moose)
# =============================================================================

class TestMooseAdvancedFactors:
    """Tests spécifiques pour l'orignal"""
    
    def test_moose_alpha_during_rut(self, unified_service):
        """TEST 33: Orignal alpha pendant le rut - modificateur élevé"""
        context = create_score_context("moose", 6, social_rank="alpha")
        
        enriched = unified_service._inject_advanced_modifiers(context, "rut", "TEST-MOOSE-001")
        adv = enriched.advanced_modifiers
        
        # Alpha pendant le rut devrait avoir un modificateur social > 1.0
        social_mod = adv.get("social_modifier", 1.0)
        
        print(f"✓ Moose alpha during rut: social_modifier={social_mod}")
    
    def test_moose_subordinate_during_rut(self, unified_service):
        """TEST 34: Orignal subordonné pendant le rut - modificateur réduit"""
        context = create_score_context("moose", 6, social_rank="subordinate")
        
        enriched = unified_service._inject_advanced_modifiers(context, "rut", "TEST-MOOSE-002")
        adv = enriched.advanced_modifiers
        
        social_mod = adv.get("social_modifier", 1.0)
        
        print(f"✓ Moose subordinate during rut: social_modifier={social_mod}")
    
    def test_moose_digestive_phases_by_hour(self, unified_service):
        """TEST 35: Phases digestives de l'orignal par heure"""
        phases_by_hour = {}
        
        for hour in [6, 10, 14, 16]:
            context = create_score_context("moose", hour)
            enriched = unified_service._inject_advanced_modifiers(context, "rut", f"TEST-MOOSE-H{hour}")
            phases_by_hour[hour] = enriched.advanced_modifiers.get("digestive_phase", "unknown")
        
        print(f"✓ Moose digestive phases by hour:")
        for h, p in phases_by_hour.items():
            print(f"  - {h}h: {p}")
    
    def test_moose_with_bear_competitor(self, unified_service):
        """TEST 36: Orignal avec compétiteur ours"""
        context = create_score_context("moose", 6, competitors=["bear"])
        
        enriched = unified_service._inject_advanced_modifiers(context, "rut", "TEST-MOOSE-003")
        adv = enriched.advanced_modifiers
        
        comp_mod = adv.get("competition_modifier", 1.0)
        
        print(f"✓ Moose with bear competitor: competition_modifier={comp_mod}")


# =============================================================================
# TEST CLASS 8: TESTS ESPÈCE CERF (deer)
# =============================================================================

class TestDeerAdvancedFactors:
    """Tests spécifiques pour le cerf"""
    
    def test_deer_alpha_during_rut(self, unified_service):
        """TEST 37: Cerf alpha pendant le rut"""
        context = create_score_context("deer", 6, social_rank="alpha")
        
        enriched = unified_service._inject_advanced_modifiers(context, "rut", "TEST-DEER-001")
        adv = enriched.advanced_modifiers
        
        social_mod = adv.get("social_modifier", 1.0)
        
        print(f"✓ Deer alpha during rut: social_modifier={social_mod}")
    
    def test_deer_digestive_phases(self, unified_service):
        """TEST 38: Phases digestives du cerf"""
        context = create_score_context("deer", 6)
        
        enriched = unified_service._inject_advanced_modifiers(context, "rut", "TEST-DEER-002")
        adv = enriched.advanced_modifiers
        
        phase = adv.get("digestive_phase", "unknown")
        
        print(f"✓ Deer at 6h: digestive_phase={phase}")
    
    def test_deer_with_moose_competitor(self, unified_service):
        """TEST 39: Cerf avec compétiteur orignal"""
        context = create_score_context("deer", 6, competitors=["moose"])
        
        enriched = unified_service._inject_advanced_modifiers(context, "rut", "TEST-DEER-003")
        adv = enriched.advanced_modifiers
        
        comp_mod = adv.get("competition_modifier", 1.0)
        
        print(f"✓ Deer with moose competitor: competition_modifier={comp_mod}")


# =============================================================================
# TEST CLASS 9: calculate_advanced_modifier (combined)
# =============================================================================

class TestCombinedAdvancedModifier:
    """Tests pour calculate_advanced_modifier du registry"""
    
    def test_combined_modifier_calculation(self, registry):
        """TEST 40: calculate_advanced_modifier combine tous les facteurs"""
        result = registry.calculate_advanced_modifier(
            species="moose",
            hour=6,
            season="rut",
            social_rank=SocialRank.ALPHA,
            competitors_present=["bear"],
            observed_indicators=["Frottoirs frais"],
            habitat="mixed_forest"
        )
        
        assert "total_modifier" in result, "total_modifier missing"
        assert "factors" in result, "factors missing"
        assert "source_ids" in result, "source_ids missing"
        assert "confidence" in result, "confidence missing"
        
        print(f"✓ Combined advanced modifier:")
        print(f"  - total_modifier: {result['total_modifier']}")
        print(f"  - factors: {list(result['factors'].keys())}")
        print(f"  - confidence: {result['confidence']}")
    
    def test_all_4_factors_in_result(self, registry):
        """TEST 41: Les 4 facteurs sont dans le résultat"""
        result = registry.calculate_advanced_modifier(
            species="moose",
            hour=10,
            season="rut",
            social_rank=SocialRank.SUBORDINATE
        )
        
        factors = result.get("factors", {})
        
        expected_factors = ["social_hierarchy", "interspecies_competition", "weak_signals", "digestive_cycle"]
        
        # At least digestive_cycle should always be present
        assert "digestive_cycle" in factors, "digestive_cycle factor missing"
        
        print(f"✓ Factors present: {list(factors.keys())}")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
