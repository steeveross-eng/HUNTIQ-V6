"""
BIONIC ENGINE — Score Density Service
======================================
Service de calcul du score de densité de population animale.

SCORE #7: DENSITY
- Évalue la densité de population de l'espèce cible dans la zone
- Facteurs: observations, indices, traces, estimations populationnelles

KNOWLEDGE LAYER INTEGRATION (PHASE 7):
- VEG-NDVI pour corrélation densité-végétation
- Préférences d'habitat par espèce (habitat quality → density proxy)
- Modèles saisonniers pour ajustements de distribution
- Pondérations FOOD-* pour capacité de charge

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
from modules.bionic_engine_p0.knowledge import (
    get_species_rules,
    get_seasonal_model
)

logger = logging.getLogger(__name__)


class ScoreDensityService(BaseScoreService):
    """
    Service de calcul du score de densité.
    
    KNOWLEDGE LAYER INTEGRATED:
    - VEG-NDVI pour corrélation végétation-densité
    - Préférences d'habitat espèce (proxy densité)
    - Modèles saisonniers (distribution/concentration)
    - FOOD-MAST, FOOD-AQUA pour capacité de charge
    
    Évalue la densité de population basée sur:
    - Qualité d'habitat (proxy observations)
    - Indices de présence basés sur habitat
    - Estimations de population régionale
    - Capacité de charge du territoire
    """
    
    def _get_category(self) -> ScoreCategory:
        return ScoreCategory.DENSITY
    
    def _get_default_weight(self) -> ScoreWeight:
        return ScoreWeight(
            category=ScoreCategory.DENSITY,
            weight=0.10,
            description="Densité de population de l'espèce (Knowledge Layer)"
        )
    
    def _get_score_name(self) -> str:
        return "Score Densité"
    
    def _calculate_components(self, context: ScoreContext) -> List[ScoreComponent]:
        """
        Calcule les composants du score de densité avec Knowledge Layer.
        
        Utilise:
        - VEG-NDVI comme proxy de qualité d'habitat
        - Préférences d'habitat espèce
        - Modèles saisonniers pour concentration/dispersion
        - FOOD-* pour capacité de charge
        """
        components = []
        
        # Get Knowledge Layer data
        species_rules = get_species_rules(context.species)
        seasonal_model = get_seasonal_model(context.species)
        target_date = context.target_datetime.date()
        
        # Determine season
        if seasonal_model:
            season = seasonal_model.get_current_season(target_date)
            season_str = season.value if season else "default"
            modifiers = seasonal_model.get_modifiers(target_date)
            self._used_source_ids.extend(seasonal_model.source_ids)
        else:
            season_str = "default"
            modifiers = {"activity": 1.0, "movement": 1.0}
        
        # =====================================================
        # COMPOSANT 1: Observations (via qualité habitat - proxy)
        # =====================================================
        try:
            # Use NDVI as proxy for habitat quality and likely density
            ndvi_weight, ndvi_conf, ndvi_sources = self.get_knowledge_layer_weight("VEG-NDVI")
            
            # Simulate NDVI-based observation likelihood
            # High NDVI → more vegetation → more food → higher density
            simulated_ndvi = 0.65  # Moderate-high NDVI
            
            # Get species-specific NDVI correlation
            ndvi_hw = self._habitat_weights.get("VEG-NDVI")
            species_ndvi_factor = 1.0
            if ndvi_hw and context.species.lower() in ["orignal", "moose"]:
                species_ndvi_factor = ndvi_hw.species_variations.get("moose", 0.95)
            elif ndvi_hw and context.species.lower() in ["deer", "cerf"]:
                species_ndvi_factor = ndvi_hw.species_variations.get("deer", 0.90)
            
            # Observation score: NDVI × species factor × seasonal movement
            movement_mod = modifiers.get("movement", 1.0)
            # During high movement (rut), animals are MORE visible but spread out
            # During low movement (winter), concentrated in yards
            # Both have observation benefits, but different mechanisms
            if movement_mod > 1.5:
                # High movement = more encounters possible
                concentration_factor = 1.0 + (movement_mod - 1.0) * 0.3
            else:
                # Low movement = concentrated, easier to find
                concentration_factor = 1.0 + (1.5 - movement_mod) * 0.3
            
            observation_score = simulated_ndvi * species_ndvi_factor * concentration_factor * 100
            
            components.append(ScoreComponent(
                name="direct_observations",
                value=min(100, observation_score),
                weight=0.35,
                weighted_value=min(100, observation_score) * 0.35,
                description=f"Probabilité observations ({season_str})",
                factors=[
                    f"NDVI: {simulated_ndvi:.2f}",
                    f"Facteur espèce: {species_ndvi_factor:.2f}",
                    f"Concentration: x{concentration_factor:.1f}"
                ],
                source_ids=ndvi_sources,
                confidence=ndvi_conf,
                knowledge_layer_ref="weights/VEG-NDVI"
            ))
            
        except ValueError as e:
            logger.warning(f"Knowledge Layer NDVI error: {e}")
            components.append(ScoreComponent(
                name="direct_observations",
                value=50.0,
                weight=0.35,
                weighted_value=17.5,
                description="Observations (données partielles)",
                factors=["Pondération NDVI non disponible"],
                confidence=0.3
            ))
        
        # =====================================================
        # COMPOSANT 2: Indices de présence (via préférences habitat)
        # =====================================================
        try:
            # Get species habitat preferences as presence indicator
            presence_score = 50.0
            presence_sources = []
            
            if species_rules:
                # Check multiple habitat types
                habitat_types = ["mixed_forest", "coniferous_forest", "wetland", "regeneration_zone"]
                habitat_scores = []
                
                for habitat_type in habitat_types:
                    try:
                        score, sources = species_rules.get_habitat_score(habitat_type, season_str)
                        habitat_scores.append(score)
                        presence_sources.extend(sources)
                    except:
                        pass
                
                if habitat_scores:
                    # Average habitat preference as presence indicator
                    presence_score = (sum(habitat_scores) / len(habitat_scores)) * 100
                    self._used_source_ids.extend(presence_sources)
            
            components.append(ScoreComponent(
                name="presence_indices",
                value=min(100, presence_score),
                weight=0.25,
                weighted_value=min(100, presence_score) * 0.25,
                description=f"Indices de présence ({context.species})",
                factors=[
                    f"Préf. habitat moyenne: {presence_score:.0f}%",
                    f"Saison: {season_str}"
                ],
                source_ids=list(set(presence_sources)),
                confidence=0.85 if presence_sources else 0.4,
                knowledge_layer_ref=f"species/{context.species}/habitat_preferences"
            ))
            
        except ValueError as e:
            logger.warning(f"Knowledge Layer presence error: {e}")
            components.append(ScoreComponent(
                name="presence_indices",
                value=50.0,
                weight=0.25,
                weighted_value=12.5,
                description="Indices de présence (données partielles)",
                factors=["Règles espèce non disponibles"],
                confidence=0.3
            ))
        
        # =====================================================
        # COMPOSANT 3: Population régionale (via modèle saisonnier)
        # =====================================================
        try:
            # Use seasonal movement modifier as population distribution indicator
            # Low movement = concentrated population
            # High movement = dispersed population
            
            movement_mod = modifiers.get("movement", 1.0)
            activity_mod = modifiers.get("activity", 1.0)
            
            # During rut/hyperphagia = higher local concentrations
            if season_str in ["rut", "pre_rut", "hyperphagia"]:
                population_score = 75 + min(25, activity_mod * 15)
            elif season_str == "winter":
                # Winter yards = higher concentration in specific areas
                population_score = 70
            else:
                # Normal distribution
                population_score = 50 + (activity_mod * 10)
            
            regional_sources = seasonal_model.source_ids if seasonal_model else []
            
            components.append(ScoreComponent(
                name="regional_population",
                value=min(100, population_score),
                weight=0.25,
                weighted_value=min(100, population_score) * 0.25,
                description=f"Distribution population ({season_str})",
                factors=[
                    f"Mouvement: x{movement_mod:.1f}",
                    f"Activité: x{activity_mod:.1f}",
                    f"Période: {season_str}"
                ],
                source_ids=regional_sources,
                confidence=0.82 if seasonal_model else 0.4,
                knowledge_layer_ref=f"seasonal/{context.species}/{season_str}"
            ))
            
        except ValueError as e:
            logger.warning(f"Knowledge Layer population error: {e}")
            components.append(ScoreComponent(
                name="regional_population",
                value=50.0,
                weight=0.25,
                weighted_value=12.5,
                description="Population régionale (données partielles)",
                factors=["Modèle saisonnier non disponible"],
                confidence=0.3
            ))
        
        # =====================================================
        # COMPOSANT 4: Capacité de charge (via FOOD-* Knowledge Layer)
        # =====================================================
        try:
            # Get food availability weights
            mast_weight, mast_conf, mast_sources = self.get_knowledge_layer_weight("FOOD-MAST")
            
            # Try to get aquatic food (important for moose)
            aqua_weight = 0.5
            aqua_sources = []
            try:
                aqua_weight, _, aqua_sources = self.get_knowledge_layer_weight("FOOD-AQUA")
            except ValueError:
                pass
            
            # Get species-specific food importance
            mast_hw = self._habitat_weights.get("FOOD-MAST")
            species_mast_factor = 1.0
            if mast_hw:
                if context.species.lower() in ["orignal", "moose"]:
                    species_mast_factor = mast_hw.species_variations.get("moose", 0.30)
                elif context.species.lower() in ["deer", "cerf"]:
                    species_mast_factor = mast_hw.species_variations.get("deer", 1.0)
            
            # Seasonal food availability modifier
            mast_seasonal = 1.0
            if mast_hw and season_str in mast_hw.seasonal_variations:
                mast_seasonal = mast_hw.seasonal_variations.get(season_str, 1.0)
            
            # Carrying capacity score
            base_capacity = ((mast_weight * species_mast_factor) + aqua_weight) / 2
            capacity_score = base_capacity * mast_seasonal * 100
            
            components.append(ScoreComponent(
                name="carrying_capacity",
                value=min(100, capacity_score),
                weight=0.15,
                weighted_value=min(100, capacity_score) * 0.15,
                description=f"Capacité de charge ({season_str})",
                factors=[
                    f"Mast: {mast_weight:.2f}",
                    f"Facteur espèce: {species_mast_factor:.2f}",
                    f"Mod. saisonnier: x{mast_seasonal:.1f}"
                ],
                source_ids=list(set(mast_sources + aqua_sources)),
                confidence=(mast_conf + 0.7) / 2,
                knowledge_layer_ref="weights/FOOD-MAST+FOOD-AQUA"
            ))
            
        except ValueError as e:
            logger.warning(f"Knowledge Layer capacity error: {e}")
            components.append(ScoreComponent(
                name="carrying_capacity",
                value=50.0,
                weight=0.15,
                weighted_value=7.5,
                description="Capacité de charge (données partielles)",
                factors=["Pondérations nourriture non disponibles"],
                confidence=0.3
            ))
        
        return components


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = ['ScoreDensityService']
