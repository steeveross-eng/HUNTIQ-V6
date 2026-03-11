"""
BIONIC ENGINE — Score Behavior Service
=======================================
Service de calcul du score de comportement animal.

SCORE #5: BEHAVIOR
- Évalue les patterns comportementaux de l'espèce cible
- Facteurs: rythme circadien, alimentation, reproduction, migration

KNOWLEDGE LAYER INTEGRATION (PHASE 7):
- Règles comportementales complètes par espèce
- Patterns d'activité horaires sourcés
- Modificateurs saisonniers (rut, fawning, etc.)

PHASE B - ARCHITECTURE CENTRALISÉE BIONIC V5:
- Ce service NE CALCULE PAS les modificateurs avancés
- Les modificateurs sont FOURNIS par UnifiedScoringService via context.advanced_modifiers
- Ce service CONSOMME uniquement les valeurs pré-calculées
- AUCUNE logique métier locale, AUCUN fallback, AUCUNE règle codée en dur

ISOLATION:
- Aucune dépendance aux autres services de scoring
- Utilise uniquement BaseScoreService + Knowledge Layer
- Modificateurs avancés fournis via ScoreContext.advanced_modifiers

Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
"""

import logging
from typing import List

from .base_score_service import (
    BaseScoreService,
    ScoreCategory,
    ScoreWeight,
    ScoreContext,
    ScoreComponent
)
from modules.bionic_engine_p0.knowledge import get_species_rules, get_seasonal_model
from modules.bionic_engine_p0.knowledge.species.base import BehaviorType

logger = logging.getLogger(__name__)


class ScoreBehaviorService(BaseScoreService):
    """
    Service de calcul du score de comportement.
    
    BIONIC V5 - ARCHITECTURE CENTRALISÉE:
    - Ce service NE CALCULE PAS les modificateurs avancés
    - Les modificateurs sont FOURNIS par UnifiedScoringService via context.advanced_modifiers
    - Ce service CONSOMME uniquement les valeurs pré-calculées
    
    KNOWLEDGE LAYER INTEGRATED:
    - Règles FEEDING, BEDDING, MOVEMENT, RUT par espèce
    - Patterns d'activité horaires calibrés
    - Modificateurs saisonniers complets
    
    MODIFICATEURS CONSOMMÉS (fournis par UnifiedScoringService):
    - social_modifier, social_rank → composant hiérarchie sociale
    - digestive_modifier, digestive_phase, digestive_visibility → composant cycle digestif
    - signals_modifier, signals_impact, signals_detected → composant signaux faibles
    """
    
    def _get_category(self) -> ScoreCategory:
        return ScoreCategory.BEHAVIOR
    
    def _get_default_weight(self) -> ScoreWeight:
        return ScoreWeight(
            category=ScoreCategory.BEHAVIOR,
            weight=0.12,
            description="Patterns comportementaux (Knowledge Layer + Advanced Modifiers)"
        )
    
    def _get_score_name(self) -> str:
        return "Score Comportement"
    
    def _calculate_components(self, context: ScoreContext) -> List[ScoreComponent]:
        """
        BIONIC V5 - ARCHITECTURE CENTRALISÉE
        
        Ce service CONSOMME les modificateurs fournis par UnifiedScoringService.
        AUCUNE logique métier locale, AUCUN fallback, AUCUNE règle codée en dur.
        
        Les modificateurs avancés sont dans context.advanced_modifiers:
        - social_modifier, social_rank, social_source_ids, social_version
        - digestive_modifier, digestive_phase, digestive_visibility, digestive_source_ids
        - signals_modifier, signals_impact, signals_detected, signals_source_ids
        """
        components = []
        
        # Récupérer les modificateurs avancés du contexte (calculés par UnifiedScoringService)
        adv = context.advanced_modifiers
        
        # Get species rules and seasonal model (Knowledge Layer)
        species_rules = get_species_rules(context.species)
        seasonal_model = get_seasonal_model(context.species)
        hour = context.target_datetime.hour
        target_date = context.target_datetime.date()
        
        # Determine current season
        if seasonal_model:
            season = seasonal_model.get_current_season(target_date)
            season_str = season.value if season else "default"
            modifiers = seasonal_model.get_modifiers(target_date)
        else:
            season_str = "default"
            modifiers = {"activity": 1.0, "movement": 1.0, "feeding": 1.0}
        
        # =====================================================
        # COMPOSANT 1: Rythme circadien (Knowledge Layer)
        # =====================================================
        try:
            activity_level, source_ids = self.get_species_activity(context.species, hour, season_str)
            circadian_score = activity_level * 100 * modifiers.get("activity", 1.0)
            
            components.append(ScoreComponent(
                name="circadian_rhythm",
                value=min(100, circadian_score),
                weight=0.25,
                weighted_value=min(100, circadian_score) * 0.25,
                description=f"Activité {context.species} à {hour}h ({season_str})",
                factors=[f"Niveau: {activity_level:.0%}", f"Mod. saisonnier: x{modifiers.get('activity', 1.0):.1f}"],
                source_ids=source_ids,
                confidence=0.90,
                knowledge_layer_ref=f"species/{context.species}/activity/{hour}"
            ))
        except ValueError:
            components.append(ScoreComponent(
                name="circadian_rhythm", value=50.0, weight=0.25, weighted_value=12.5,
                description="Rythme circadien (données partielles)", factors=["Espèce non supportée"],
                confidence=0.3
            ))
        
        # =====================================================
        # COMPOSANT 2: Pattern alimentation (Knowledge Layer)
        # =====================================================
        if species_rules:
            feeding_rules = [r for r in species_rules._behavior_rules.values() if r.behavior_type == BehaviorType.FEEDING]
            if feeding_rules:
                rule = feeding_rules[0]
                peak_hours = rule.parameters.get("peak_hours", [6, 17])
                is_peak = hour in peak_hours or any(abs(hour - ph) <= 1 for ph in peak_hours)
                feeding_score = 85 if is_peak else 50
                feeding_score *= modifiers.get("feeding", 1.0)
                
                components.append(ScoreComponent(
                    name="feeding_pattern",
                    value=min(100, feeding_score),
                    weight=0.20,
                    weighted_value=min(100, feeding_score) * 0.20,
                    description=f"Pattern alimentation ({hour}h)",
                    factors=[f"Heures pic: {peak_hours}", f"Période active: {'Oui' if is_peak else 'Non'}"],
                    source_ids=rule.source_ids,
                    confidence=rule.confidence_score,
                    knowledge_layer_ref=f"species/{context.species}/feeding"
                ))
                self._used_source_ids.extend(rule.source_ids)
            else:
                components.append(ScoreComponent(
                    name="feeding_pattern", value=50.0, weight=0.20, weighted_value=10.0,
                    description="Pattern alimentation (non disponible)", factors=["Règles non trouvées"],
                    confidence=0.4
                ))
        else:
            components.append(ScoreComponent(
                name="feeding_pattern", value=50.0, weight=0.20, weighted_value=10.0,
                description="Pattern alimentation (espèce non supportée)", factors=["Knowledge Layer absent"],
                confidence=0.3
            ))
        
        # =====================================================
        # COMPOSANT 3: Cycle reproduction (Knowledge Layer)
        # =====================================================
        rut_score = 50.0
        rut_sources = []
        if species_rules:
            rut_rules = [r for r in species_rules._behavior_rules.values() if r.behavior_type == BehaviorType.RUT]
            if rut_rules:
                rule = rut_rules[0]
                rut_sources = rule.source_ids
                if season_str in ["rut", "pre_rut", "post_rut"]:
                    rut_score = 90 if season_str == "rut" else 70
                    rut_score *= modifiers.get("vulnerability", 1.0)
                self._used_source_ids.extend(rut_sources)
        
        components.append(ScoreComponent(
            name="reproduction_cycle",
            value=min(100, rut_score),
            weight=0.15,
            weighted_value=min(100, rut_score) * 0.15,
            description=f"Cycle reproduction ({season_str})",
            factors=[f"Saison: {season_str}", f"Score rut: {rut_score:.0f}"],
            source_ids=rut_sources,
            confidence=0.88 if rut_sources else 0.4,
            knowledge_layer_ref=f"species/{context.species}/rut"
        ))
        
        # =====================================================
        # COMPOSANT 4: HIÉRARCHIE SOCIALE (CONSOMMATION - pas de calcul local)
        # Source: context.advanced_modifiers (calculé par UnifiedScoringService)
        # =====================================================
        social_modifier = adv.get("social_modifier", 1.0)
        social_rank = adv.get("social_rank", "unknown")
        social_sources = adv.get("social_source_ids", [])
        social_version = adv.get("social_version", "1.0.0")
        is_rut = adv.get("is_rut_period", False)
        
        # Convertir modificateur en score (50 = neutre, >50 = favorable, <50 = défavorable)
        social_score = 50.0 + ((social_modifier - 1.0) * 30)
        social_score = max(20, min(90, social_score))
        
        components.append(ScoreComponent(
            name="social_hierarchy",
            value=social_score,
            weight=0.15,
            weighted_value=social_score * 0.15,
            description=f"Hiérarchie sociale ({social_rank})",
            factors=[
                f"Rang: {social_rank}",
                f"Modificateur: x{social_modifier:.2f}",
                f"Version: {social_version}"
            ],
            source_ids=social_sources,
            confidence=0.80 if social_sources else 0.50,
            knowledge_layer_ref=f"advanced_factors/social/{context.species}/{social_rank}"
        ))
        self._used_source_ids.extend(social_sources)
        
        # =====================================================
        # COMPOSANT 5: CYCLES DIGESTIFS (CONSOMMATION - pas de calcul local)
        # Source: context.advanced_modifiers (calculé par UnifiedScoringService)
        # =====================================================
        digestive_visibility = adv.get("digestive_visibility", 0.5)
        digestive_phase = adv.get("digestive_phase", "unknown")
        digestive_mobility = adv.get("digestive_mobility", 0.5)
        digestive_sources = adv.get("digestive_source_ids", [])
        digestive_version = adv.get("digestive_version", "1.0.0")
        
        # Visibilité haute = score favorable pour observation
        digestive_score = digestive_visibility * 100
        
        components.append(ScoreComponent(
            name="digestive_cycle",
            value=digestive_score,
            weight=0.15,
            weighted_value=digestive_score * 0.15,
            description=f"Cycle digestif ({digestive_phase})",
            factors=[
                f"Phase: {digestive_phase}",
                f"Visibilité: {digestive_score:.0f}%",
                f"Version: {digestive_version}"
            ],
            source_ids=digestive_sources,
            confidence=0.85 if digestive_sources else 0.40,
            knowledge_layer_ref=f"advanced_factors/digestive/{context.species}/{hour}"
        ))
        self._used_source_ids.extend(digestive_sources)
        
        # =====================================================
        # COMPOSANT 6: SIGNAUX FAIBLES (CONSOMMATION - pas de calcul local)
        # Source: context.advanced_modifiers (calculé par UnifiedScoringService)
        # =====================================================
        signals_impact = adv.get("signals_impact", 0.0)
        signals_detected = adv.get("signals_detected", [])
        signals_sources = adv.get("signals_source_ids", [])
        signals_version = adv.get("signals_version", "1.0.0")
        
        # Convertir impact en score (50 = neutre)
        signal_score = 50.0 + signals_impact
        signal_score = max(10, min(95, signal_score))
        
        components.append(ScoreComponent(
            name="weak_signals",
            value=signal_score,
            weight=0.10,
            weighted_value=signal_score * 0.10,
            description=f"Signaux faibles ({len(signals_detected)} détectés)",
            factors=[
                f"Impact: {signals_impact:+.0f} pts",
                f"Signaux: {', '.join(signals_detected[:3]) if signals_detected else 'Aucun'}",
                f"Version: {signals_version}"
            ],
            source_ids=signals_sources,
            confidence=0.65 if signals_sources else 0.30,
            knowledge_layer_ref=f"advanced_factors/signals/{context.species}"
        ))
        self._used_source_ids.extend(signals_sources)
        
        return components


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = ['ScoreBehaviorService']
