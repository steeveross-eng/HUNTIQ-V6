"""
BIONIC ENGINE — Score Pressure Service
=======================================
Service de calcul du score de pression de chasse.

SCORE #3: PRESSURE
- Évalue la pression de chasse et humaine sur la zone
- Facteurs: activité humaine, historique chasse, routes, urbanisation

KNOWLEDGE LAYER INTEGRATION (PHASE 7):
- Pondérations PRES-HUMAN, PRES-ROAD, PRES-HUNT calibrées
- Règles AVOIDANCE par espèce
- Variations saisonnières (hunting_season)

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
from modules.bionic_engine_p0.knowledge import get_species_rules, get_seasonal_model

logger = logging.getLogger(__name__)


class ScorePressureService(BaseScoreService):
    """
    Service de calcul du score de pression.
    
    KNOWLEDGE LAYER INTEGRATED:
    - Pondérations PRES-HUMAN, PRES-ROAD, PRES-HUNT calibrées
    - Règles d'évitement par espèce (AVOID-001)
    - Variations saisonnières (hunting_season amplification)
    
    NOTE: Score INVERSÉ - pression élevée = score faible (défavorable)
    """
    
    def _get_category(self) -> ScoreCategory:
        return ScoreCategory.PRESSURE
    
    def _get_default_weight(self) -> ScoreWeight:
        return ScoreWeight(
            category=ScoreCategory.PRESSURE,
            weight=0.10,
            description="Pression de chasse et activité humaine (Knowledge Layer)"
        )
    
    def _get_score_name(self) -> str:
        return "Score Pression"
    
    def _calculate_components(self, context: ScoreContext) -> List[ScoreComponent]:
        """
        Calcule les composants du score de pression avec Knowledge Layer.
        
        Utilise:
        - PRES-HUMAN, PRES-ROAD, PRES-HUNT pour les pondérations
        - Règles AVOIDANCE par espèce
        - Modificateurs saisonniers (hunting_season)
        
        NOTE: Score INVERSÉ pour la pression
        """
        components = []
        
        # Get species avoidance rules
        species_rules = get_species_rules(context.species)
        
        # Get seasonal context
        target_date = context.target_datetime.date()
        seasonal_model = get_seasonal_model(context.species)
        if seasonal_model:
            season = seasonal_model.get_current_season(target_date)
            season_str = season.value if season else "default"
        else:
            season_str = "default"
        
        # =====================================================
        # COMPOSANT 1: Densité activité humaine (Knowledge Layer)
        # =====================================================
        try:
            human_weight, human_conf, human_sources = self.get_knowledge_layer_weight("PRES-HUMAN")
            
            # Simulate human activity level (would come from real data)
            # Lower human activity = higher score (better for hunting)
            simulated_human_activity = 0.4  # 40% human activity
            
            # Invert: low activity = high score
            human_score = (1 - simulated_human_activity) * 100
            
            # Apply hunting season modifier if applicable
            if season_str == "hunting_season":
                human_score *= 0.8  # Reduce score during hunting season
            
            components.append(ScoreComponent(
                name="human_density",
                value=human_score,
                weight=0.35,
                weighted_value=human_score * 0.35,
                description=f"Densité activité humaine (poids: {human_weight:.2f})",
                factors=[f"Activité: {simulated_human_activity:.0%}", f"Impact: {human_weight:.0%}"],
                source_ids=human_sources,
                confidence=human_conf,
                knowledge_layer_ref="weights/PRES-HUMAN"
            ))
            
        except ValueError as e:
            logger.warning(f"Knowledge Layer PRES-HUMAN error: {e}")
            components.append(ScoreComponent(
                name="human_density",
                value=50.0,
                weight=0.35,
                weighted_value=17.5,
                description="Densité humaine (données partielles)",
                factors=["Pondération non disponible"],
                confidence=0.3
            ))
        
        # =====================================================
        # COMPOSANT 2: Proximité routes (Knowledge Layer)
        # =====================================================
        try:
            road_weight, road_conf, road_sources = self.get_knowledge_layer_weight("PRES-ROAD")
            
            # Get species-specific road avoidance distance
            road_avoidance_m = 500  # default
            if species_rules:
                avoidance_rules = species_rules.get_rules_by_type(
                    species_rules._behavior_rules.get("MOOSE-AVOID-001", 
                    species_rules._behavior_rules.get("DEER-AVOID-001"))
                )
                # Try to get from behavior rules
                for rule_id, rule in species_rules._behavior_rules.items():
                    if "AVOID" in rule_id:
                        road_avoidance_m = rule.parameters.get("road_avoidance_distance_m", 500)
                        self._used_source_ids.extend(rule.source_ids)
                        break
            
            # Simulate road distance (would come from GIS data)
            simulated_road_distance_m = 800  # 800m from road
            
            # Score based on distance vs avoidance threshold
            if simulated_road_distance_m >= road_avoidance_m:
                road_score = 80 + min(20, (simulated_road_distance_m - road_avoidance_m) / 50)
            else:
                road_score = (simulated_road_distance_m / road_avoidance_m) * 80
            
            components.append(ScoreComponent(
                name="road_proximity",
                value=min(100, road_score),
                weight=0.25,
                weighted_value=min(100, road_score) * 0.25,
                description=f"Distance routes ({simulated_road_distance_m}m, seuil: {road_avoidance_m}m)",
                factors=[f"Distance: {simulated_road_distance_m}m", f"Évitement espèce: {road_avoidance_m}m"],
                source_ids=road_sources,
                confidence=road_conf,
                knowledge_layer_ref="weights/PRES-ROAD"
            ))
            
        except ValueError as e:
            logger.warning(f"Knowledge Layer PRES-ROAD error: {e}")
            components.append(ScoreComponent(
                name="road_proximity",
                value=50.0,
                weight=0.25,
                weighted_value=12.5,
                description="Proximité routes (données partielles)",
                factors=["Pondération non disponible"],
                confidence=0.3
            ))
        
        # =====================================================
        # COMPOSANT 3: Pression de chasse (Knowledge Layer)
        # =====================================================
        try:
            hunt_weight, hunt_conf, hunt_sources = self.get_knowledge_layer_weight("PRES-HUNT")
            
            # Simulate hunting pressure (would come from historical data)
            simulated_hunt_pressure = 0.3  # 30% pressure
            
            # Invert: low pressure = high score
            hunt_score = (1 - simulated_hunt_pressure) * 100
            
            # Get seasonal variation from Knowledge Layer
            hw = self._habitat_weights.get("PRES-HUNT")
            if hw and season_str in hw.seasonal_variations:
                seasonal_multiplier = hw.seasonal_variations[season_str]
                # During hunting season, pressure impact is higher
                hunt_score *= (2 - seasonal_multiplier)  # Reduce score more
            
            components.append(ScoreComponent(
                name="hunting_pressure",
                value=max(0, hunt_score),
                weight=0.25,
                weighted_value=max(0, hunt_score) * 0.25,
                description=f"Pression chasse historique ({season_str})",
                factors=[f"Pression: {simulated_hunt_pressure:.0%}", f"Saison: {season_str}"],
                source_ids=hunt_sources,
                confidence=hunt_conf,
                knowledge_layer_ref="weights/PRES-HUNT"
            ))
            
        except ValueError as e:
            logger.warning(f"Knowledge Layer PRES-HUNT error: {e}")
            components.append(ScoreComponent(
                name="hunting_pressure",
                value=50.0,
                weight=0.25,
                weighted_value=12.5,
                description="Pression chasse (données partielles)",
                factors=["Pondération non disponible"],
                confidence=0.3
            ))
        
        # =====================================================
        # COMPOSANT 4: Perturbation générale (Knowledge Layer)
        # =====================================================
        try:
            # Use combination of weights for general disturbance
            human_weight, _, human_sources = self.get_knowledge_layer_weight("PRES-HUMAN")
            
            # Get species disturbance sensitivity from rules
            disturbance_sensitivity = "medium"
            if species_rules:
                for rule_id, rule in species_rules._behavior_rules.items():
                    if "AVOID" in rule_id:
                        disturbance_sensitivity = rule.parameters.get("noise_sensitivity", "medium")
                        break
            
            # Score based on sensitivity
            sensitivity_scores = {"low": 70, "medium": 50, "high": 30}
            base_disturbance = sensitivity_scores.get(disturbance_sensitivity, 50)
            
            components.append(ScoreComponent(
                name="disturbance_level",
                value=base_disturbance,
                weight=0.15,
                weighted_value=base_disturbance * 0.15,
                description=f"Perturbation générale (sensibilité: {disturbance_sensitivity})",
                factors=[f"Sensibilité espèce: {disturbance_sensitivity}"],
                source_ids=human_sources,
                confidence=0.75,
                knowledge_layer_ref="species/avoidance/noise_sensitivity"
            ))
            
        except ValueError as e:
            logger.warning(f"Knowledge Layer disturbance error: {e}")
            components.append(ScoreComponent(
                name="disturbance_level",
                value=50.0,
                weight=0.15,
                weighted_value=7.5,
                description="Perturbation (données partielles)",
                factors=["Données non disponibles"],
                confidence=0.3
            ))
        
        return components


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = ['ScorePressureService']
