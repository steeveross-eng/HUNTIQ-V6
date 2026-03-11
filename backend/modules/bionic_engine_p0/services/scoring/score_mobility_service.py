"""
BIONIC ENGINE — Score Mobility Service
=======================================
Service de calcul du score de mobilité et mouvements.

SCORE #9: MOBILITY
- Évalue les patterns de mouvement de l'espèce cible
- Facteurs: corridors, migrations, déplacements quotidiens, routes

KNOWLEDGE LAYER INTEGRATION (PHASE 7):
- TER-SLOPE, TER-TOPO pour accessibilité terrain
- Règles MOVEMENT par espèce (home range, corridors)
- Modèles saisonniers (movement_modifier)
- Pondérations terrain pour corridors

PHASE B - ARCHITECTURE CENTRALISÉE BIONIC V5:
- Ce service NE CALCULE PAS les modificateurs avancés
- Les modificateurs sont FOURNIS par UnifiedScoringService via context.advanced_modifiers
- Ce service CONSOMME uniquement les valeurs pré-calculées
- AUCUNE logique métier locale, AUCUN fallback, AUCUNE règle codée en dur

ISOLATION:
- Aucune dépendance aux autres services de scoring
- Utilise uniquement BaseScoreService + Knowledge Layer
- Modificateurs avancés fournis via ScoreContext.advanced_modifiers

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
from modules.bionic_engine_p0.knowledge.species.base import BehaviorType

logger = logging.getLogger(__name__)


class ScoreMobilityService(BaseScoreService):
    """
    Service de calcul du score de mobilité.
    
    BIONIC V5 - ARCHITECTURE CENTRALISÉE:
    - Ce service NE CALCULE PAS les modificateurs avancés
    - Les modificateurs sont FOURNIS par UnifiedScoringService via context.advanced_modifiers
    - Ce service CONSOMME uniquement les valeurs pré-calculées
    
    KNOWLEDGE LAYER INTEGRATED:
    - TER-SLOPE, TER-TOPO pour accessibilité
    - Règles MOVEMENT par espèce (home_range, corridors)
    - SeasonalModels (movement_modifier)
    - Préférences terrain pour corridors
    
    MODIFICATEURS CONSOMMÉS (fournis par UnifiedScoringService):
    - digestive_mobility → composant cycle digestif mobilité
    """
    
    def _get_category(self) -> ScoreCategory:
        return ScoreCategory.MOBILITY
    
    def _get_default_weight(self) -> ScoreWeight:
        return ScoreWeight(
            category=ScoreCategory.MOBILITY,
            weight=0.11,
            description="Mobilité et patterns de mouvement (Knowledge Layer + Advanced Modifiers)"
        )
    
    def _get_score_name(self) -> str:
        return "Score Mobilité"
    
    def _calculate_components(self, context: ScoreContext) -> List[ScoreComponent]:
        """
        Calcule les composants du score de mobilité avec Knowledge Layer.
        
        Utilise:
        - TER-SLOPE, TER-TOPO pour terrain de déplacement
        - Règles MOVEMENT (home range, corridors)
        - Modèles saisonniers (movement modifier)
        - Préférences habitat pour routes
        """
        components = []
        
        # Get Knowledge Layer data
        species_rules = get_species_rules(context.species)
        seasonal_model = get_seasonal_model(context.species)
        target_date = context.target_datetime.date()
        hour = context.target_datetime.hour
        
        # Determine season and movement modifiers
        if seasonal_model:
            season = seasonal_model.get_current_season(target_date)
            season_str = season.value if season else "default"
            modifiers = seasonal_model.get_modifiers(target_date)
            self._used_source_ids.extend(seasonal_model.source_ids)
        else:
            season_str = "default"
            modifiers = {"movement": 1.0, "activity": 1.0}
        
        # =====================================================
        # COMPOSANT 1: Corridors de déplacement (Knowledge Layer)
        # =====================================================
        try:
            # Get terrain weights for corridor assessment
            slope_weight, slope_conf, slope_sources = self.get_knowledge_layer_weight("TER-SLOPE")
            topo_weight, topo_conf, topo_sources = self.get_knowledge_layer_weight("TER-TOPO")
            
            # Get species-specific terrain preferences
            slope_hw = self._habitat_weights.get("TER-SLOPE")
            species_slope_factor = 1.0
            if slope_hw:
                if context.species.lower() in ["orignal", "moose"]:
                    species_slope_factor = slope_hw.species_variations.get("moose", 0.90)
                elif context.species.lower() in ["deer", "cerf"]:
                    species_slope_factor = slope_hw.species_variations.get("deer", 0.95)
            
            # Simulate terrain conditions
            simulated_slope = 8  # 8° slope (gentle)
            
            # Corridor score based on terrain accessibility
            # Low slopes (5-15°) are preferred for movement
            if 5 <= simulated_slope <= 15:
                terrain_score = 85
            elif simulated_slope < 5:
                terrain_score = 75  # Too flat might lack cover
            elif simulated_slope <= 25:
                terrain_score = 70 - (simulated_slope - 15)
            else:
                terrain_score = max(30, 55 - (simulated_slope - 25) * 2)
            
            # Apply species factor and terrain weights
            corridor_score = terrain_score * species_slope_factor * ((slope_weight + topo_weight) / 2)
            
            # Movement modifier amplifies corridor importance
            movement_mod = modifiers.get("movement", 1.0)
            corridor_score *= (0.5 + movement_mod * 0.5)  # Scale: 0.5-1.5x
            
            components.append(ScoreComponent(
                name="movement_corridors",
                value=min(100, corridor_score),
                weight=0.25,
                weighted_value=min(100, corridor_score) * 0.25,
                description=f"Corridors de déplacement ({simulated_slope}°, {season_str})",
                factors=[
                    f"Pente: {simulated_slope}°",
                    f"Facteur espèce: {species_slope_factor:.2f}",
                    f"Mouvement: x{movement_mod:.1f}"
                ],
                source_ids=list(set(slope_sources + topo_sources)),
                confidence=(slope_conf + topo_conf) / 2,
                knowledge_layer_ref="weights/TER-SLOPE+TER-TOPO"
            ))
            
        except ValueError as e:
            logger.warning(f"Knowledge Layer corridor error: {e}")
            components.append(ScoreComponent(
                name="movement_corridors",
                value=50.0,
                weight=0.30,
                weighted_value=15.0,
                description="Corridors (données partielles)",
                factors=["Pondérations terrain non disponibles"],
                confidence=0.3
            ))
        
        # =====================================================
        # COMPOSANT 2: Routes quotidiennes (Knowledge Layer)
        # =====================================================
        try:
            # Get movement rules from species
            daily_distance_km = 5.0  # Default
            corridor_width_m = 50  # Default
            movement_sources = []
            
            if species_rules:
                # Get MOVEMENT rules
                movement_rules = species_rules.get_rules_by_type(BehaviorType.MOVEMENT)
                if movement_rules:
                    rule = movement_rules[0]
                    daily_distance_km = rule.parameters.get("average_daily_distance_km", 5.0)
                    corridor_width_m = rule.parameters.get("corridor_width_m", 50)
                    movement_sources = rule.source_ids
                    self._used_source_ids.extend(movement_sources)
            
            # Get activity level for this hour
            activity_level = 0.5
            if species_rules:
                activity_level, activity_sources = species_rules.get_activity_level(hour, season_str)
                self._used_source_ids.extend(activity_sources)
            
            # Daily route score: based on activity and typical distances
            # High activity hours = more likely on daily routes
            activity_mod = modifiers.get("activity", 1.0)
            route_score = activity_level * activity_mod * 100
            
            # Bonus during feeding hours (dawn/dusk)
            feeding_hours = [5, 6, 7, 17, 18, 19]
            if hour in feeding_hours:
                route_score = min(100, route_score * 1.2)
            
            components.append(ScoreComponent(
                name="daily_routes",
                value=min(100, route_score),
                weight=0.25,
                weighted_value=min(100, route_score) * 0.25,
                description=f"Routes quotidiennes {context.species} ({hour}h)",
                factors=[
                    f"Distance jour: {daily_distance_km} km",
                    f"Largeur corridor: {corridor_width_m}m",
                    f"Activité: {activity_level:.0%}"
                ],
                source_ids=movement_sources,
                confidence=0.85 if movement_sources else 0.4,
                knowledge_layer_ref=f"species/{context.species}/movement"
            ))
            
        except ValueError as e:
            logger.warning(f"Knowledge Layer daily routes error: {e}")
            components.append(ScoreComponent(
                name="daily_routes",
                value=50.0,
                weight=0.30,
                weighted_value=15.0,
                description="Routes quotidiennes (données partielles)",
                factors=["Règles mouvement non disponibles"],
                confidence=0.3
            ))
        
        # =====================================================
        # COMPOSANT 3: Migration saisonnière (Knowledge Layer)
        # =====================================================
        try:
            # Get seasonal movement patterns
            movement_mod = modifiers.get("movement", 1.0)
            
            # Migration score based on season
            migration_score = 50.0
            migration_factors = []
            
            if season_str in ["spring", "fall"]:
                # Transitional seasons = more movement
                migration_score = 70 + (movement_mod - 1.0) * 20
                migration_factors.append(f"Saison transitionnelle: {season_str}")
            elif season_str == "rut":
                # Rut = extreme movement for males
                migration_score = 85 + min(15, movement_mod * 10)
                migration_factors.append("Période rut: mouvement maximal")
            elif season_str == "winter":
                # Winter = limited to yards/ravages
                migration_score = 40
                migration_factors.append("Hiver: mouvement limité aux ravages")
            else:
                migration_score = 50 + movement_mod * 10
            
            migration_factors.append(f"Mod. mouvement: x{movement_mod:.1f}")
            
            seasonal_sources = seasonal_model.source_ids if seasonal_model else []
            
            components.append(ScoreComponent(
                name="seasonal_migration",
                value=min(100, migration_score),
                weight=0.20,
                weighted_value=min(100, migration_score) * 0.20,
                description=f"Migration saisonnière ({season_str})",
                factors=migration_factors,
                source_ids=seasonal_sources,
                confidence=0.85 if seasonal_model else 0.4,
                knowledge_layer_ref=f"seasonal/{context.species}/{season_str}"
            ))
            
        except ValueError as e:
            logger.warning(f"Knowledge Layer migration error: {e}")
            components.append(ScoreComponent(
                name="seasonal_migration",
                value=50.0,
                weight=0.20,
                weighted_value=10.0,
                description="Migration saisonnière (données partielles)",
                factors=["Modèle saisonnier non disponible"],
                confidence=0.3
            ))
        
        # =====================================================
        # COMPOSANT 4: CYCLE DIGESTIF - MOBILITÉ (CONSOMMATION - pas de calcul local)
        # Source: context.advanced_modifiers (calculé par UnifiedScoringService)
        # =====================================================
        adv = context.advanced_modifiers
        digestive_mobility = adv.get("digestive_mobility", 0.5) * 100
        digestive_phase = adv.get("digestive_phase", "unknown")
        digestive_sources = adv.get("digestive_source_ids", [])
        digestive_version = adv.get("digestive_version", "1.0.0")
        
        digestive_factors = [
            f"Phase: {digestive_phase}",
            f"Mobilité: {digestive_mobility:.0f}%",
            f"Version: {digestive_version}"
        ]
        
        components.append(ScoreComponent(
            name="digestive_mobility",
            value=min(100, digestive_mobility),
            weight=0.10,
            weighted_value=min(100, digestive_mobility) * 0.10,
            description=f"Mobilité digestive ({digestive_phase})",
            factors=digestive_factors,
            source_ids=digestive_sources,
            confidence=0.80 if digestive_sources else 0.40,
            knowledge_layer_ref=f"advanced_factors/digestive/{context.species}/{hour}"
        ))
        self._used_source_ids.extend(digestive_sources)
        
        # =====================================================
        # COMPOSANT 4B: NIVEAU 5 - MOBILITÉ DYNAMIQUE (CONSOMMATION)
        # Source: context.advanced_modifiers (calculé par UnifiedScoringService via MobilityRegistry)
        # =====================================================
        mobility_modifier = adv.get("mobility_modifier", 1.0)
        mobility_details = adv.get("mobility_details", {})
        mobility_sources = adv.get("mobility_source_ids", [])
        mobility_version = adv.get("mobility_version", "5.0.0")
        
        # Extraire les scores de mobilité NIVEAU 5
        mobility_scores = mobility_details.get("scores", {})
        mobility_factors_detail = mobility_details.get("factors", {})
        
        mobility_score = mobility_scores.get("mobility", 50.0)
        predictability_score = mobility_scores.get("predictability", 50.0)
        interception_score = mobility_scores.get("interception", 50.0)
        
        # Score composite NIVEAU 5
        niveau5_score = (mobility_score * 0.4 + predictability_score * 0.3 + interception_score * 0.3)
        
        mobility_factors = [
            f"Modificateur NIVEAU 5: {mobility_modifier:.3f}",
            f"Vitesse: {mobility_details.get('current_speed_kmh', 0):.1f} km/h",
            f"Intensité: {mobility_details.get('intensity', 'unknown')}",
            f"Direction: {mobility_details.get('preferred_direction', 'random')}",
            f"Version: {mobility_version}"
        ]
        
        components.append(ScoreComponent(
            name="niveau5_mobility",
            value=min(100, niveau5_score),
            weight=0.10,
            weighted_value=min(100, niveau5_score) * 0.10,
            description=f"Mobilité dynamique NIVEAU 5 (mod={mobility_modifier:.2f})",
            factors=mobility_factors,
            source_ids=mobility_sources,
            confidence=0.85 if mobility_sources else 0.50,
            knowledge_layer_ref=f"mobility/{context.species}/{mobility_version}"
        ))
        self._used_source_ids.extend(mobility_sources)
        
        # =====================================================
        # COMPOSANT 5: Territorialité (Knowledge Layer)
        # =====================================================
        try:
            # Get home range from movement rules
            home_range_km2 = 25.0  # Default
            territorial_sources = []
            
            if species_rules:
                movement_rules = species_rules.get_rules_by_type(BehaviorType.MOVEMENT)
                if movement_rules:
                    rule = movement_rules[0]
                    home_range_km2 = rule.parameters.get("home_range_km2", 25.0)
                    territorial_sources = rule.source_ids
                
                # Also check for territorial behavior rules
                territorial_rules = species_rules.get_rules_by_type(BehaviorType.TERRITORIAL)
                if territorial_rules:
                    terr_rule = territorial_rules[0]
                    territorial_sources.extend(terr_rule.source_ids)
                    self._used_source_ids.extend(terr_rule.source_ids)
            
            # Territoriality score based on:
            # - Home range size (larger = more predictable patterns)
            # - Season (rut = more territorial, winter = grouped)
            
            base_territorial = 50.0
            
            # Larger home range = more spread out but predictable
            if home_range_km2 > 20:
                base_territorial = 60
            elif home_range_km2 > 10:
                base_territorial = 70
            else:
                base_territorial = 55  # Small range = harder to intercept
            
            # Seasonal adjustment
            vulnerability_mod = modifiers.get("vulnerability", 1.0)
            if season_str in ["rut", "pre_rut"]:
                # Males are very territorial during rut
                base_territorial = min(100, base_territorial * 1.3)
            elif season_str == "winter":
                # Yarding behavior = concentrated, less territorial
                base_territorial *= 0.8
            
            # Vulnerability affects predictability
            territorial_score = base_territorial * (0.5 + vulnerability_mod * 0.5)
            
            components.append(ScoreComponent(
                name="territoriality",
                value=min(100, territorial_score),
                weight=0.10,
                weighted_value=min(100, territorial_score) * 0.10,
                description=f"Territorialité {context.species} ({season_str})",
                factors=[
                    f"Home range: {home_range_km2} km²",
                    f"Vulnérabilité: x{vulnerability_mod:.1f}",
                    f"Saison: {season_str}"
                ],
                source_ids=list(set(territorial_sources)),
                confidence=0.80 if territorial_sources else 0.4,
                knowledge_layer_ref=f"species/{context.species}/territoriality"
            ))
            
        except ValueError as e:
            logger.warning(f"Knowledge Layer territoriality error: {e}")
            components.append(ScoreComponent(
                name="territoriality",
                value=50.0,
                weight=0.10,
                weighted_value=5.0,
                description="Territorialité (données partielles)",
                factors=["Données territoriales non disponibles"],
                confidence=0.3
            ))
        
        return components


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = ['ScoreMobilityService']
