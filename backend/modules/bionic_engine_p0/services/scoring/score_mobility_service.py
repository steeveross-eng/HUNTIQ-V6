"""
BIONIC ENGINE — Score Mobility Service
=======================================
Service de calcul du score de mobilité et mouvements.

SCORE #9: MOBILITY
- Évalue les patterns de mouvement de l'espèce cible
- Facteurs: corridors, migrations, déplacements quotidiens, routes

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


class ScoreMobilityService(BaseScoreService):
    """
    Service de calcul du score de mobilité.
    
    Évalue les mouvements basés sur:
    - Corridors de déplacement
    - Routes quotidiennes (gagnage, repos)
    - Migrations saisonnières
    - Dispersion et territorialité
    - Réponse aux perturbations
    """
    
    def _get_category(self) -> ScoreCategory:
        return ScoreCategory.MOBILITY
    
    def _get_default_weight(self) -> ScoreWeight:
        return ScoreWeight(
            category=ScoreCategory.MOBILITY,
            weight=0.11,
            description="Mobilité et patterns de mouvement"
        )
    
    def _get_score_name(self) -> str:
        return "Score Mobilité"
    
    def _calculate_components(self, context: ScoreContext) -> List[ScoreComponent]:
        """
        Calcule les composants du score de mobilité.
        
        STRUCTURE UNIQUEMENT - Logique à implémenter ultérieurement.
        """
        components = []
        
        # Composant 1: Corridors de déplacement
        components.append(ScoreComponent(
            name="movement_corridors",
            value=50.0,
            weight=0.30,
            weighted_value=15.0,
            description="Proximité des corridors de déplacement",
            factors=["Corridors non analysés"]
        ))
        
        # Composant 2: Routes quotidiennes
        components.append(ScoreComponent(
            name="daily_routes",
            value=50.0,
            weight=0.30,
            weighted_value=15.0,
            description="Position sur les routes quotidiennes",
            factors=["Routes quotidiennes non évaluées"]
        ))
        
        # Composant 3: Migration saisonnière
        components.append(ScoreComponent(
            name="seasonal_migration",
            value=50.0,
            weight=0.20,
            weighted_value=10.0,
            description="Phase de migration actuelle",
            factors=["Migration non évaluée"]
        ))
        
        # Composant 4: Territorialité
        components.append(ScoreComponent(
            name="territoriality",
            value=50.0,
            weight=0.20,
            weighted_value=10.0,
            description="Comportement territorial de l'espèce",
            factors=["Territorialité non analysée"]
        ))
        
        return components


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = ['ScoreMobilityService']
