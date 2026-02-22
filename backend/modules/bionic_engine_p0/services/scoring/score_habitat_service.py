"""
BIONIC ENGINE — Score Habitat Service
======================================
Service de calcul du score de qualité d'habitat.

SCORE #2: HABITAT
- Évalue la qualité et pertinence de l'habitat pour l'espèce cible
- Facteurs: couverture végétale, sources d'eau, nourriture, abris

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


class ScoreHabitatService(BaseScoreService):
    """
    Service de calcul du score d'habitat.
    
    Évalue la qualité de l'habitat basée sur:
    - Couverture végétale et type de forêt
    - Proximité des sources d'eau
    - Disponibilité de nourriture
    - Qualité des zones d'abri
    - Pertinence pour l'espèce cible
    """
    
    def _get_category(self) -> ScoreCategory:
        return ScoreCategory.HABITAT
    
    def _get_default_weight(self) -> ScoreWeight:
        return ScoreWeight(
            category=ScoreCategory.HABITAT,
            weight=0.12,
            description="Qualité et pertinence de l'habitat"
        )
    
    def _get_score_name(self) -> str:
        return "Score Habitat"
    
    def _calculate_components(self, context: ScoreContext) -> List[ScoreComponent]:
        """
        Calcule les composants du score d'habitat.
        
        STRUCTURE UNIQUEMENT - Logique à implémenter ultérieurement.
        """
        components = []
        
        # Composant 1: Couverture végétale
        components.append(ScoreComponent(
            name="vegetation_cover",
            value=50.0,
            weight=0.25,
            weighted_value=12.5,
            description="Type et densité de couverture végétale",
            factors=["Données végétation non disponibles"]
        ))
        
        # Composant 2: Sources d'eau
        components.append(ScoreComponent(
            name="water_sources",
            value=50.0,
            weight=0.25,
            weighted_value=12.5,
            description="Proximité et qualité des sources d'eau",
            factors=["Sources d'eau non analysées"]
        ))
        
        # Composant 3: Nourriture
        components.append(ScoreComponent(
            name="food_availability",
            value=50.0,
            weight=0.25,
            weighted_value=12.5,
            description="Disponibilité de nourriture pour l'espèce",
            factors=["Nourriture non évaluée"]
        ))
        
        # Composant 4: Zones d'abri
        components.append(ScoreComponent(
            name="shelter_quality",
            value=50.0,
            weight=0.25,
            weighted_value=12.5,
            description="Qualité des zones d'abri et de repos",
            factors=["Abris non analysés"]
        ))
        
        return components


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = ['ScoreHabitatService']
