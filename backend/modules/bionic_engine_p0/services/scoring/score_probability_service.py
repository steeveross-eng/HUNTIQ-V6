"""
BIONIC ENGINE — Score Probability Service
==========================================
Service de calcul du score de probabilité de succès de chasse.

SCORE #1: PROBABILITY
- Évalue la probabilité de succès basée sur l'historique
- Facteurs: succès passés, conditions similaires, patterns temporels

KNOWLEDGE LAYER INTEGRATION (PHASE 7):
- Patterns temporels depuis get_species_rules()
- Modèles saisonniers depuis get_seasonal_model()
- Pondérations calibrées depuis get_habitat_weights()

ISOLATION:
- Aucune dépendance aux autres services de scoring
- Utilise uniquement BaseScoreService + Knowledge Layer

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
from modules.bionic_engine_p0.knowledge import get_seasonal_model

logger = logging.getLogger(__name__)


class ScoreProbabilityService(BaseScoreService):
    """
    Service de calcul du score de probabilité.
    
    KNOWLEDGE LAYER INTEGRATED:
    - Patterns d'activité par espèce sourcés
    - Modèles saisonniers calibrés
    - Traçabilité complète des sources
    
    Évalue la probabilité de succès de chasse basée sur:
    - Historique de succès au waypoint (données terrain)
    - Niveau d'activité de l'espèce (Knowledge Layer)
    - Modificateurs saisonniers (Knowledge Layer)
    """
    
    def _get_category(self) -> ScoreCategory:
        return ScoreCategory.PROBABILITY
    
    def _get_default_weight(self) -> ScoreWeight:
        return ScoreWeight(
            category=ScoreCategory.PROBABILITY,
            weight=0.15,
            description="Probabilité de succès basée sur Knowledge Layer"
        )
    
    def _get_score_name(self) -> str:
        return "Score Probabilité"
    
    def _calculate_components(self, context: ScoreContext) -> List[ScoreComponent]:
        """
        Calcule les composants du score de probabilité avec Knowledge Layer.
        
        Utilise:
        - get_species_rules() pour les patterns d'activité
        - get_seasonal_model() pour les modificateurs saisonniers
        """
        components = []
        
        # =====================================================
        # COMPOSANT 1: Activité de l'espèce (Knowledge Layer)
        # =====================================================
        try:
            hour = context.target_datetime.hour
            target_date = context.target_datetime.date()
            
            # Get seasonal info
            seasonal_model = get_seasonal_model(context.species)
            if seasonal_model:
                season = seasonal_model.get_current_season(target_date)
                season_str = season.value if season else "default"
            else:
                season_str = "default"
            
            # Get activity level from Knowledge Layer
            activity_level, source_ids = self.get_species_activity(
                context.species, 
                hour, 
                season_str
            )
            
            activity_value = activity_level * 100
            
            components.append(ScoreComponent(
                name="species_activity",
                value=activity_value,
                weight=0.40,
                weighted_value=activity_value * 0.40,
                description=f"Niveau d'activité {context.species} à {hour}h ({season_str})",
                factors=[f"Activité: {activity_level:.0%}", f"Saison: {season_str}"],
                source_ids=source_ids,
                confidence=0.88,
                knowledge_layer_ref=f"species/{context.species}/activity/{hour}"
            ))
            
        except ValueError as e:
            logger.warning(f"Knowledge Layer error: {e}")
            components.append(ScoreComponent(
                name="species_activity",
                value=50.0,
                weight=0.40,
                weighted_value=20.0,
                description="Activité espèce non disponible",
                factors=["Espèce non supportée dans Knowledge Layer"],
                confidence=0.3
            ))
        
        # =====================================================
        # COMPOSANT 2: Modificateurs saisonniers (Knowledge Layer)
        # =====================================================
        try:
            target_date = context.target_datetime.date()
            modifiers, season, source_ids = self.get_seasonal_modifiers(
                context.species,
                target_date
            )
            
            # Calculate seasonal score based on activity modifier
            activity_mod = modifiers.get("activity", 1.0)
            vulnerability_mod = modifiers.get("vulnerability", 1.0)
            
            # Higher modifiers = better probability
            seasonal_value = min(100, (activity_mod + vulnerability_mod) / 2 * 60)
            
            components.append(ScoreComponent(
                name="seasonal_modifier",
                value=seasonal_value,
                weight=0.35,
                weighted_value=seasonal_value * 0.35,
                description=f"Modificateur saisonnier ({season.value if season else 'default'})",
                factors=[
                    f"Activité: x{activity_mod:.1f}",
                    f"Vulnérabilité: x{vulnerability_mod:.1f}"
                ],
                source_ids=source_ids,
                confidence=0.90,
                knowledge_layer_ref=f"seasonal/{context.species}/{season.value if season else 'default'}"
            ))
            
        except ValueError as e:
            logger.warning(f"Knowledge Layer seasonal error: {e}")
            components.append(ScoreComponent(
                name="seasonal_modifier",
                value=50.0,
                weight=0.35,
                weighted_value=17.5,
                description="Modificateur saisonnier non disponible",
                factors=["Modèle saisonnier non supporté"],
                confidence=0.3
            ))
        
        # =====================================================
        # COMPOSANT 3: Historique de succès (données terrain)
        # =====================================================
        # Note: Ce composant utilisera le ValidationPipeline dans le futur
        # Pour l'instant, valeur neutre avec indication de calibration requise
        components.append(ScoreComponent(
            name="success_history",
            value=50.0,
            weight=0.25,
            weighted_value=12.5,
            description="Historique de succès au waypoint",
            factors=["En attente de données de validation terrain"],
            source_ids=[],
            confidence=0.5,
            knowledge_layer_ref="validation/pending"
        ))
        
        return components


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = ['ScoreProbabilityService']
