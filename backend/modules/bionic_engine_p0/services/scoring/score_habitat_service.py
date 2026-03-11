"""
BIONIC ENGINE — Score Habitat Service
======================================
Service de calcul du score de qualité d'habitat.

SCORE #2: HABITAT
- Évalue la qualité et pertinence de l'habitat pour l'espèce cible
- Facteurs: couverture végétale, sources d'eau, nourriture, abris

KNOWLEDGE LAYER INTEGRATION (PHASE 7):
- Pondérations calibrées depuis get_habitat_weights()
- Préférences d'habitat par espèce depuis get_species_rules()
- Traçabilité scientifique complète

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
from modules.bionic_engine_p0.knowledge import get_species_rules

logger = logging.getLogger(__name__)


class ScoreHabitatService(BaseScoreService):
    """
    Service de calcul du score d'habitat.
    
    KNOWLEDGE LAYER INTEGRATED:
    - Pondérations VEG-*, WAT-*, FOOD-* calibrées
    - Préférences d'habitat par espèce
    - Variations saisonnières
    
    Évalue la qualité de l'habitat basée sur:
    - Couverture végétale (VEG-NDVI, VEG-COVER, VEG-EDGE)
    - Proximité des sources d'eau (WAT-PROX, WAT-TYPE)
    - Disponibilité de nourriture (FOOD-MAST, FOOD-AQUA, FOOD-MINERAL)
    - Qualité des zones d'abri (VEG-BROWSE)
    """
    
    def _get_category(self) -> ScoreCategory:
        return ScoreCategory.HABITAT
    
    def _get_default_weight(self) -> ScoreWeight:
        return ScoreWeight(
            category=ScoreCategory.HABITAT,
            weight=0.12,
            description="Qualité et pertinence de l'habitat (Knowledge Layer)"
        )
    
    def _get_score_name(self) -> str:
        return "Score Habitat"
    
    def _calculate_components(self, context: ScoreContext) -> List[ScoreComponent]:
        """
        Calcule les composants du score d'habitat avec Knowledge Layer.
        
        Utilise les pondérations calibrées:
        - VEG-NDVI, VEG-COVER, VEG-EDGE pour la végétation
        - WAT-PROX pour l'eau
        - FOOD-MAST, FOOD-MINERAL pour la nourriture
        """
        components = []
        
        # Get species-specific habitat preferences
        species_rules = get_species_rules(context.species)
        target_date = context.target_datetime.date()
        
        # Determine season for habitat variation
        from modules.bionic_engine_p0.knowledge import get_seasonal_model
        seasonal_model = get_seasonal_model(context.species)
        if seasonal_model:
            season = seasonal_model.get_current_season(target_date)
            season_str = season.value if season else "default"
        else:
            season_str = "default"
        
        # =====================================================
        # COMPOSANT 1: Couverture végétale (Knowledge Layer)
        # =====================================================
        try:
            # Get calibrated weights
            ndvi_weight, ndvi_conf, ndvi_sources = self.get_knowledge_layer_weight("VEG-NDVI")
            cover_weight, cover_conf, cover_sources = self.get_knowledge_layer_weight("VEG-COVER")
            
            # Simulate base vegetation score (would come from real GIS data)
            base_veg_score = 65.0
            
            # Adjust for species if available
            if species_rules:
                habitat_score, habitat_sources = species_rules.get_habitat_score("mixed_forest", season_str)
                base_veg_score = base_veg_score * habitat_score
                self._used_source_ids.extend(habitat_sources)
            
            combined_weight = (ndvi_weight + cover_weight) / 2
            
            components.append(ScoreComponent(
                name="vegetation_cover",
                value=min(100, base_veg_score),
                weight=0.30,
                weighted_value=min(100, base_veg_score) * 0.30,
                description=f"Couverture végétale ({season_str})",
                factors=[f"NDVI: {ndvi_weight:.2f}", f"Couvert: {cover_weight:.2f}"],
                source_ids=list(set(ndvi_sources + cover_sources)),
                confidence=(ndvi_conf + cover_conf) / 2,
                knowledge_layer_ref="weights/VEG-NDVI+VEG-COVER"
            ))
            
        except ValueError as e:
            logger.warning(f"Knowledge Layer vegetation error: {e}")
            components.append(ScoreComponent(
                name="vegetation_cover",
                value=50.0,
                weight=0.30,
                weighted_value=15.0,
                description="Couverture végétale (données partielles)",
                factors=["Pondérations Knowledge Layer non disponibles"],
                confidence=0.3
            ))
        
        # =====================================================
        # COMPOSANT 2: Sources d'eau (Knowledge Layer)
        # =====================================================
        try:
            water_weight, water_conf, water_sources = self.get_knowledge_layer_weight("WAT-PROX")
            
            # Simulate water proximity score
            base_water_score = 70.0
            
            # Adjust for species-specific water preference
            if species_rules:
                # Moose has higher water preference
                water_pref, water_pref_sources = species_rules.get_habitat_score("wetland", season_str)
                base_water_score = base_water_score * water_pref
                self._used_source_ids.extend(water_pref_sources)
            
            components.append(ScoreComponent(
                name="water_sources",
                value=min(100, base_water_score),
                weight=0.25,
                weighted_value=min(100, base_water_score) * 0.25,
                description=f"Proximité sources d'eau (poids: {water_weight:.2f})",
                factors=[f"Importance eau: {water_weight:.0%}"],
                source_ids=water_sources,
                confidence=water_conf,
                knowledge_layer_ref="weights/WAT-PROX"
            ))
            
        except ValueError as e:
            logger.warning(f"Knowledge Layer water error: {e}")
            components.append(ScoreComponent(
                name="water_sources",
                value=50.0,
                weight=0.25,
                weighted_value=12.5,
                description="Sources d'eau (données partielles)",
                factors=["Pondération eau non disponible"],
                confidence=0.3
            ))
        
        # =====================================================
        # COMPOSANT 3: Nourriture (Knowledge Layer)
        # =====================================================
        try:
            mast_weight, mast_conf, mast_sources = self.get_knowledge_layer_weight("FOOD-MAST")
            mineral_weight, mineral_conf, mineral_sources = self.get_knowledge_layer_weight("FOOD-MINERAL")
            
            # Simulate food availability
            base_food_score = 60.0
            
            # Adjust for season (mast more important in fall)
            if season_str in ["fall", "pre_rut"]:
                base_food_score *= 1.2
            
            combined_food_weight = (mast_weight + mineral_weight) / 2
            
            components.append(ScoreComponent(
                name="food_availability",
                value=min(100, base_food_score),
                weight=0.25,
                weighted_value=min(100, base_food_score) * 0.25,
                description=f"Disponibilité nourriture ({season_str})",
                factors=[f"Mast: {mast_weight:.2f}", f"Minéraux: {mineral_weight:.2f}"],
                source_ids=list(set(mast_sources + mineral_sources)),
                confidence=(mast_conf + mineral_conf) / 2,
                knowledge_layer_ref="weights/FOOD-MAST+FOOD-MINERAL"
            ))
            
        except ValueError as e:
            logger.warning(f"Knowledge Layer food error: {e}")
            components.append(ScoreComponent(
                name="food_availability",
                value=50.0,
                weight=0.25,
                weighted_value=12.5,
                description="Nourriture (données partielles)",
                factors=["Pondération nourriture non disponible"],
                confidence=0.3
            ))
        
        # =====================================================
        # COMPOSANT 4: Zones d'abri (Knowledge Layer)
        # =====================================================
        try:
            browse_weight, browse_conf, browse_sources = self.get_knowledge_layer_weight("VEG-BROWSE")
            
            # Simulate shelter quality
            base_shelter_score = 55.0
            
            # Adjust for species bedding preference
            if species_rules:
                cover_pref, cover_sources = species_rules.get_habitat_score("dense_cover", season_str)
                base_shelter_score = base_shelter_score * cover_pref
                self._used_source_ids.extend(cover_sources)
            
            components.append(ScoreComponent(
                name="shelter_quality",
                value=min(100, base_shelter_score),
                weight=0.20,
                weighted_value=min(100, base_shelter_score) * 0.20,
                description=f"Qualité zones d'abri",
                factors=[f"Brout disponible: {browse_weight:.2f}"],
                source_ids=browse_sources,
                confidence=browse_conf,
                knowledge_layer_ref="weights/VEG-BROWSE"
            ))
            
        except ValueError as e:
            logger.warning(f"Knowledge Layer shelter error: {e}")
            components.append(ScoreComponent(
                name="shelter_quality",
                value=50.0,
                weight=0.20,
                weighted_value=10.0,
                description="Abris (données partielles)",
                factors=["Pondération abris non disponible"],
                confidence=0.3
            ))
        
        return components


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = ['ScoreHabitatService']
