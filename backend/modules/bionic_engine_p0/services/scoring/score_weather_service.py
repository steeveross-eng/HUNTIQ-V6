"""
BIONIC ENGINE — Score Weather Service
======================================
Service de calcul du score d'impact météorologique.

SCORE #4: WEATHER
- Évalue l'impact des conditions météo sur l'activité animale
- Facteurs: température, vent, précipitations, pression, visibilité

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


class ScoreWeatherService(BaseScoreService):
    """
    Service de calcul du score météo.
    
    Évalue l'impact météo basé sur:
    - Température et ressenti
    - Vitesse et direction du vent
    - Précipitations (pluie, neige)
    - Pression atmosphérique et tendance
    - Visibilité et couverture nuageuse
    - Phase lunaire
    """
    
    def _get_category(self) -> ScoreCategory:
        return ScoreCategory.WEATHER
    
    def _get_default_weight(self) -> ScoreWeight:
        return ScoreWeight(
            category=ScoreCategory.WEATHER,
            weight=0.12,
            description="Impact des conditions météorologiques"
        )
    
    def _get_score_name(self) -> str:
        return "Score Météo"
    
    def _calculate_components(self, context: ScoreContext) -> List[ScoreComponent]:
        """
        Calcule les composants du score météo.
        
        STRUCTURE UNIQUEMENT - Logique à implémenter ultérieurement.
        """
        components = []
        
        # Composant 1: Température
        components.append(ScoreComponent(
            name="temperature",
            value=50.0,
            weight=0.20,
            weighted_value=10.0,
            description="Impact de la température sur l'activité",
            factors=["Température non évaluée"]
        ))
        
        # Composant 2: Vent
        components.append(ScoreComponent(
            name="wind",
            value=50.0,
            weight=0.20,
            weighted_value=10.0,
            description="Vitesse et direction du vent",
            factors=["Vent non mesuré"]
        ))
        
        # Composant 3: Précipitations
        components.append(ScoreComponent(
            name="precipitation",
            value=50.0,
            weight=0.20,
            weighted_value=10.0,
            description="Niveau et type de précipitations",
            factors=["Précipitations non évaluées"]
        ))
        
        # Composant 4: Pression atmosphérique
        components.append(ScoreComponent(
            name="pressure",
            value=50.0,
            weight=0.25,
            weighted_value=12.5,
            description="Pression et tendance barométrique",
            factors=["Pression non mesurée"]
        ))
        
        # Composant 5: Visibilité
        components.append(ScoreComponent(
            name="visibility",
            value=50.0,
            weight=0.15,
            weighted_value=7.5,
            description="Visibilité et conditions lumineuses",
            factors=["Visibilité non évaluée"]
        ))
        
        return components


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = ['ScoreWeatherService']
