"""
BIONIC ENGINE — Score Risk Service
===================================
Service de calcul du score de risques et facteurs de danger.

SCORE #8: RISK
- Évalue les risques potentiels affectant la chasse
- Facteurs: prédateurs, obstacles, dangers naturels, zones interdites

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


class ScoreRiskService(BaseScoreService):
    """
    Service de calcul du score de risques.
    
    Évalue les risques basés sur:
    - Présence de prédateurs
    - Obstacles et dangers naturels
    - Zones réglementées ou interdites
    - Conditions de sécurité
    - Facteurs de perturbation imprévisibles
    """
    
    def _get_category(self) -> ScoreCategory:
        return ScoreCategory.RISK
    
    def _get_default_weight(self) -> ScoreWeight:
        return ScoreWeight(
            category=ScoreCategory.RISK,
            weight=0.08,
            description="Risques et facteurs de danger"
        )
    
    def _get_score_name(self) -> str:
        return "Score Risques"
    
    def _calculate_components(self, context: ScoreContext) -> List[ScoreComponent]:
        """
        Calcule les composants du score de risques.
        
        STRUCTURE UNIQUEMENT - Logique à implémenter ultérieurement.
        
        NOTE: Score inversé - valeur haute = faible risque = favorable
        """
        components = []
        
        # Composant 1: Prédateurs (score inversé)
        components.append(ScoreComponent(
            name="predator_presence",
            value=50.0,  # 100 = pas de prédateurs, 0 = forte présence
            weight=0.30,
            weighted_value=15.0,
            description="Absence/présence de prédateurs majeurs",
            factors=["Présence prédateurs non évaluée"]
        ))
        
        # Composant 2: Dangers naturels (score inversé)
        components.append(ScoreComponent(
            name="natural_hazards",
            value=50.0,  # 100 = sûr, 0 = dangereux
            weight=0.25,
            weighted_value=12.5,
            description="Obstacles et dangers naturels",
            factors=["Dangers naturels non analysés"]
        ))
        
        # Composant 3: Zones réglementées
        components.append(ScoreComponent(
            name="regulated_zones",
            value=50.0,
            weight=0.25,
            weighted_value=12.5,
            description="Proximité zones interdites ou réglementées",
            factors=["Zones réglementées non vérifiées"]
        ))
        
        # Composant 4: Conditions sécurité
        components.append(ScoreComponent(
            name="safety_conditions",
            value=50.0,
            weight=0.20,
            weighted_value=10.0,
            description="Conditions générales de sécurité",
            factors=["Sécurité non évaluée"]
        ))
        
        return components


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = ['ScoreRiskService']
