"""
BIONIC ENGINE — Score Density Service
======================================
Service de calcul du score de densité de population animale.

SCORE #7: DENSITY
- Évalue la densité de population de l'espèce cible dans la zone
- Facteurs: observations, indices, traces, estimations populationnelles

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


class ScoreDensityService(BaseScoreService):
    """
    Service de calcul du score de densité.
    
    Évalue la densité de population basée sur:
    - Observations directes récentes
    - Indices de présence (traces, déjections)
    - Estimations de population régionale
    - Historique de présence
    - Capacité de charge du territoire
    """
    
    def _get_category(self) -> ScoreCategory:
        return ScoreCategory.DENSITY
    
    def _get_default_weight(self) -> ScoreWeight:
        return ScoreWeight(
            category=ScoreCategory.DENSITY,
            weight=0.10,
            description="Densité de population de l'espèce"
        )
    
    def _get_score_name(self) -> str:
        return "Score Densité"
    
    def _calculate_components(self, context: ScoreContext) -> List[ScoreComponent]:
        """
        Calcule les composants du score de densité.
        
        STRUCTURE UNIQUEMENT - Logique à implémenter ultérieurement.
        """
        components = []
        
        # Composant 1: Observations directes
        components.append(ScoreComponent(
            name="direct_observations",
            value=50.0,
            weight=0.35,
            weighted_value=17.5,
            description="Observations directes récentes",
            factors=["Observations non disponibles"]
        ))
        
        # Composant 2: Indices de présence
        components.append(ScoreComponent(
            name="presence_indices",
            value=50.0,
            weight=0.25,
            weighted_value=12.5,
            description="Traces, indices et signes de présence",
            factors=["Indices non analysés"]
        ))
        
        # Composant 3: Population régionale
        components.append(ScoreComponent(
            name="regional_population",
            value=50.0,
            weight=0.25,
            weighted_value=12.5,
            description="Estimation population régionale",
            factors=["Données population non disponibles"]
        ))
        
        # Composant 4: Capacité de charge
        components.append(ScoreComponent(
            name="carrying_capacity",
            value=50.0,
            weight=0.15,
            weighted_value=7.5,
            description="Capacité de charge du territoire",
            factors=["Capacité non évaluée"]
        ))
        
        return components


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = ['ScoreDensityService']
