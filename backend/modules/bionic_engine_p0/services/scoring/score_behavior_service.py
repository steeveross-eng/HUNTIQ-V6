"""
BIONIC ENGINE — Score Behavior Service
=======================================
Service de calcul du score de comportement animal.

SCORE #5: BEHAVIOR
- Évalue les patterns comportementaux de l'espèce cible
- Facteurs: rythme circadien, alimentation, reproduction, migration

ISOLATION:
- Aucune dépendance aux autres services de scoring
- Utilise uniquement BaseScoreService

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

logger = logging.getLogger(__name__)


class ScoreBehaviorService(BaseScoreService):
    """
    Service de calcul du score de comportement.
    
    Évalue le comportement animal basé sur:
    - Rythme circadien (activité jour/nuit)
    - Patterns d'alimentation
    - Période de reproduction (rut)
    - Comportements saisonniers
    - Réactions aux perturbations
    """
    
    def _get_category(self) -> ScoreCategory:
        return ScoreCategory.BEHAVIOR
    
    def _get_default_weight(self) -> ScoreWeight:
        return ScoreWeight(
            category=ScoreCategory.BEHAVIOR,
            weight=0.12,
            description="Patterns comportementaux de l'espèce"
        )
    
    def _get_score_name(self) -> str:
        return "Score Comportement"
    
    def _calculate_components(self, context: ScoreContext) -> List[ScoreComponent]:
        """
        Calcule les composants du score de comportement.
        
        STRUCTURE UNIQUEMENT - Logique à implémenter ultérieurement.
        """
        components = []
        
        # Composant 1: Rythme circadien
        components.append(ScoreComponent(
            name="circadian_rhythm",
            value=50.0,
            weight=0.30,
            weighted_value=15.0,
            description="Alignement avec le rythme d'activité naturel",
            factors=["Rythme circadien non évalué"]
        ))
        
        # Composant 2: Alimentation
        components.append(ScoreComponent(
            name="feeding_pattern",
            value=50.0,
            weight=0.25,
            weighted_value=12.5,
            description="Période d'alimentation active",
            factors=["Pattern alimentation non analysé"]
        ))
        
        # Composant 3: Reproduction
        components.append(ScoreComponent(
            name="reproduction_cycle",
            value=50.0,
            weight=0.25,
            weighted_value=12.5,
            description="Période de rut et reproduction",
            factors=["Cycle reproduction non évalué"]
        ))
        
        # Composant 4: Saisonnier
        components.append(ScoreComponent(
            name="seasonal_behavior",
            value=50.0,
            weight=0.20,
            weighted_value=10.0,
            description="Comportements saisonniers spécifiques",
            factors=["Comportement saisonnier non analysé"]
        ))
        
        return components


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = ['ScoreBehaviorService']
