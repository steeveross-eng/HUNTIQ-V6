"""
BIONIC ENGINE — Score Pressure Service
=======================================
Service de calcul du score de pression de chasse.

SCORE #3: PRESSURE
- Évalue la pression de chasse et humaine sur la zone
- Facteurs: activité humaine, historique chasse, routes, urbanisation

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


class ScorePressureService(BaseScoreService):
    """
    Service de calcul du score de pression.
    
    Évalue la pression sur la zone basée sur:
    - Activité de chasse récente dans la zone
    - Proximité des routes et accès
    - Densité de population humaine
    - Niveau de perturbation
    - Fréquentation de la zone
    """
    
    def _get_category(self) -> ScoreCategory:
        return ScoreCategory.PRESSURE
    
    def _get_default_weight(self) -> ScoreWeight:
        return ScoreWeight(
            category=ScoreCategory.PRESSURE,
            weight=0.10,
            description="Pression de chasse et activité humaine"
        )
    
    def _get_score_name(self) -> str:
        return "Score Pression"
    
    def _calculate_components(self, context: ScoreContext) -> List[ScoreComponent]:
        """
        Calcule les composants du score de pression.
        
        STRUCTURE UNIQUEMENT - Logique à implémenter ultérieurement.
        """
        components = []
        
        # Composant 1: Activité de chasse
        components.append(ScoreComponent(
            name="hunting_activity",
            value=50.0,
            weight=0.30,
            weighted_value=15.0,
            description="Niveau d'activité de chasse récente",
            factors=["Activité chasse non mesurée"]
        ))
        
        # Composant 2: Proximité routes
        components.append(ScoreComponent(
            name="road_proximity",
            value=50.0,
            weight=0.25,
            weighted_value=12.5,
            description="Distance aux routes et accès",
            factors=["Proximité routes non calculée"]
        ))
        
        # Composant 3: Densité humaine
        components.append(ScoreComponent(
            name="human_density",
            value=50.0,
            weight=0.25,
            weighted_value=12.5,
            description="Densité de population environnante",
            factors=["Densité humaine non évaluée"]
        ))
        
        # Composant 4: Perturbation
        components.append(ScoreComponent(
            name="disturbance_level",
            value=50.0,
            weight=0.20,
            weighted_value=10.0,
            description="Niveau de perturbation général",
            factors=["Perturbation non mesurée"]
        ))
        
        return components


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = ['ScorePressureService']
