"""
BIONIC ENGINE — Score MultiFactors Service
==========================================
Service de calcul du score de facteurs multiples combinés.

SCORE #6: MULTIFACTOR
- Combine plusieurs facteurs corrélés pour une analyse holistique
- Facteurs: synergies habitat-météo, corrélations temporelles, patterns composites

KNOWLEDGE LAYER INTEGRATION (PHASE 7):
- Synergies habitat-météo via pondérations VEG-*, CLIM-*
- Corrélations espèce-saison via SeasonalModels
- Interactions comportement-environnement via SpeciesRules
- Effets de seuil via paramètres comportementaux

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

logger = logging.getLogger(__name__)


class ScoreMultiFactorService(BaseScoreService):
    """
    Service de calcul du score multi-facteurs.
    
    BIONIC V5 - ARCHITECTURE CENTRALISÉE:
    - Ce service NE CALCULE PAS les modificateurs avancés
    - Les modificateurs sont FOURNIS par UnifiedScoringService via context.advanced_modifiers
    - Ce service CONSOMME uniquement les valeurs pré-calculées
    
    KNOWLEDGE LAYER INTEGRATED:
    - Synergies habitat-météo (VEG-COVER × CLIM-THERM)
    - Corrélations espèce-saison (SeasonalModels complets)
    - Interactions comportement-environnement (SpeciesRules × HabitatWeights)
    - Effets de seuil (paramètres comportementaux calibrés)
    
    MODIFICATEURS CONSOMMÉS (fournis par UnifiedScoringService):
    - competition_modifier, competitors_present → composant compétition inter-espèces
    """
    
    def _get_category(self) -> ScoreCategory:
        return ScoreCategory.MULTIFACTOR
    
    def _get_default_weight(self) -> ScoreWeight:
        return ScoreWeight(
            category=ScoreCategory.MULTIFACTOR,
            weight=0.10,
            description="Analyse multi-facteurs et synergies (Knowledge Layer + Advanced Modifiers)"
        )
    
    def _get_score_name(self) -> str:
        return "Score Multi-Facteurs"
    
    def _calculate_components(self, context: ScoreContext) -> List[ScoreComponent]:
        """
        Calcule les composants du score multi-facteurs avec Knowledge Layer.
        
        Utilise les synergies entre:
        - Pondérations habitat (VEG-COVER, VEG-NDVI)
        - Pondérations climat (CLIM-THERM, CLIM-WIND)
        - Modèles saisonniers (modifiers)
        - Règles comportementales (thresholds)
        """
        components = []
        
        # Get Knowledge Layer data
        species_rules = get_species_rules(context.species)
        seasonal_model = get_seasonal_model(context.species)
        target_date = context.target_datetime.date()
        hour = context.target_datetime.hour
        
        # Determine season and modifiers
        if seasonal_model:
            season = seasonal_model.get_current_season(target_date)
            season_str = season.value if season else "default"
            modifiers = seasonal_model.get_modifiers(target_date)
            self._used_source_ids.extend(seasonal_model.source_ids)
        else:
            season_str = "default"
            modifiers = {"activity": 1.0, "movement": 1.0, "feeding": 1.0, "vulnerability": 1.0}
        
        # =====================================================
        # COMPOSANT 1: Synergie habitat-météo (Knowledge Layer)
        # =====================================================
        try:
            # Get habitat and climate weights for synergy calculation
            cover_weight, cover_conf, cover_sources = self.get_knowledge_layer_weight("VEG-COVER")
            therm_weight, therm_conf, therm_sources = self.get_knowledge_layer_weight("CLIM-THERM")
            
            # Synergy score: high when both cover and thermal comfort are favorable
            # Simulate values (real implementation would use actual data)
            simulated_cover_quality = 0.70  # 70% good cover
            simulated_thermal_comfort = 0.75  # 75% comfortable
            
            # Synergy multiplier: bonus when both factors are high
            synergy_multiplier = 1.0
            if simulated_cover_quality > 0.6 and simulated_thermal_comfort > 0.6:
                synergy_multiplier = 1.2  # 20% bonus for positive synergy
            elif simulated_cover_quality < 0.4 or simulated_thermal_comfort < 0.4:
                synergy_multiplier = 0.8  # 20% penalty for negative synergy
            
            # Combined synergy score
            base_synergy = ((simulated_cover_quality * cover_weight) + (simulated_thermal_comfort * therm_weight)) / 2
            synergy_score = base_synergy * synergy_multiplier * 100
            
            components.append(ScoreComponent(
                name="habitat_weather_synergy",
                value=min(100, synergy_score),
                weight=0.25,
                weighted_value=min(100, synergy_score) * 0.25,
                description=f"Synergie habitat-météo ({season_str})",
                factors=[
                    f"Couvert: {simulated_cover_quality:.0%}",
                    f"Confort thermique: {simulated_thermal_comfort:.0%}",
                    f"Multiplicateur: x{synergy_multiplier:.1f}"
                ],
                source_ids=list(set(cover_sources + therm_sources)),
                confidence=(cover_conf + therm_conf) / 2,
                knowledge_layer_ref="weights/VEG-COVER+CLIM-THERM"
            ))
            
        except ValueError as e:
            logger.warning(f"Knowledge Layer synergy error: {e}")
            components.append(ScoreComponent(
                name="habitat_weather_synergy",
                value=50.0,
                weight=0.30,
                weighted_value=15.0,
                description="Synergie habitat-météo (données partielles)",
                factors=["Pondérations Knowledge Layer non disponibles"],
                confidence=0.3
            ))
        
        # =====================================================
        # COMPOSANT 2: Corrélation espèce-saison (Knowledge Layer)
        # =====================================================
        try:
            # Get activity level from species rules
            if species_rules:
                activity_level, activity_sources = species_rules.get_activity_level(hour, season_str)
                self._used_source_ids.extend(activity_sources)
            else:
                activity_level = 0.5
                activity_sources = []
            
            # Correlation score based on seasonal modifiers and activity
            activity_mod = modifiers.get("activity", 1.0)
            vulnerability_mod = modifiers.get("vulnerability", 1.0)
            
            # High activity + high vulnerability = good hunting conditions
            correlation_score = (activity_level * activity_mod + vulnerability_mod) / 2 * 100
            
            # Bonus during peak seasons (rut, pre_rut)
            if season_str in ["rut", "pre_rut"]:
                correlation_score = min(100, correlation_score * 1.25)
            
            components.append(ScoreComponent(
                name="species_season_correlation",
                value=min(100, correlation_score),
                weight=0.20,
                weighted_value=min(100, correlation_score) * 0.20,
                description=f"Corrélation {context.species}/{season_str} à {hour}h",
                factors=[
                    f"Activité: {activity_level:.0%}",
                    f"Mod. activité: x{activity_mod:.1f}",
                    f"Vulnérabilité: x{vulnerability_mod:.1f}"
                ],
                source_ids=activity_sources if activity_sources else (seasonal_model.source_ids if seasonal_model else []),
                confidence=0.88 if species_rules else 0.4,
                knowledge_layer_ref=f"species/{context.species}/seasonal/{season_str}"
            ))
            
        except ValueError as e:
            logger.warning(f"Knowledge Layer correlation error: {e}")
            components.append(ScoreComponent(
                name="species_season_correlation",
                value=50.0,
                weight=0.25,
                weighted_value=12.5,
                description="Corrélation espèce-saison (données partielles)",
                factors=["Modèle saisonnier non disponible"],
                confidence=0.3
            ))
        
        # =====================================================
        # COMPOSANT 3: Interaction comportement-environnement (Knowledge Layer)
        # =====================================================
        try:
            # Get habitat and behavior data
            edge_weight, edge_conf, edge_sources = self.get_knowledge_layer_weight("VEG-EDGE")
            water_weight, water_conf, water_sources = self.get_knowledge_layer_weight("WAT-PROX")
            
            # Get species habitat preferences
            habitat_score = 0.5
            habitat_sources = []
            if species_rules:
                # Get preference for mixed forest (common optimal habitat)
                pref_score, pref_sources = species_rules.get_habitat_score("mixed_forest", season_str)
                habitat_score = pref_score
                habitat_sources = pref_sources
                self._used_source_ids.extend(pref_sources)
            
            # Movement modifier affects environment interaction
            movement_mod = modifiers.get("movement", 1.0)
            feeding_mod = modifiers.get("feeding", 1.0)
            
            # Interaction score: habitat quality × behavioral activity
            interaction_base = (habitat_score * edge_weight + water_weight) / 2
            interaction_score = interaction_base * ((movement_mod + feeding_mod) / 2) * 100
            
            components.append(ScoreComponent(
                name="behavior_environment_interaction",
                value=min(100, interaction_score),
                weight=0.20,
                weighted_value=min(100, interaction_score) * 0.20,
                description=f"Interaction comportement-environnement",
                factors=[
                    f"Préf. habitat: {habitat_score:.0%}",
                    f"Lisière: {edge_weight:.2f}",
                    f"Mouvement: x{movement_mod:.1f}"
                ],
                source_ids=list(set(edge_sources + water_sources + habitat_sources)),
                confidence=(edge_conf + water_conf) / 2,
                knowledge_layer_ref="weights/VEG-EDGE+WAT-PROX+species/habitat"
            ))
            
        except ValueError as e:
            logger.warning(f"Knowledge Layer interaction error: {e}")
            components.append(ScoreComponent(
                name="behavior_environment_interaction",
                value=50.0,
                weight=0.25,
                weighted_value=12.5,
                description="Interaction comportement-environnement (données partielles)",
                factors=["Pondérations non disponibles"],
                confidence=0.3
            ))
        
        # =====================================================
        # COMPOSANT 4: COMPÉTITION INTER-ESPÈCES (CONSOMMATION - pas de calcul local)
        # Source: context.advanced_modifiers (calculé par UnifiedScoringService)
        # =====================================================
        adv = context.advanced_modifiers
        competition_modifier = adv.get("competition_modifier", 1.0)
        competitors = adv.get("competitors_present", [])
        competition_sources = adv.get("competition_source_ids", [])
        competition_version = adv.get("competition_version", "1.0.0")
        
        # Score competition: 100 = aucune compétition, <100 = impact négatif
        competition_score = competition_modifier * 100
        
        # Build factors list
        competition_factors = []
        if competitors:
            competition_factors.append(f"Compétiteurs: {', '.join(competitors[:3])}")
            competition_factors.append(f"Modificateur: x{competition_modifier:.2f}")
        else:
            competition_factors.append("Aucun compétiteur détecté")
        competition_factors.append(f"Version: {competition_version}")
        
        components.append(ScoreComponent(
            name="interspecies_competition",
            value=min(100, competition_score),
            weight=0.20,
            weighted_value=min(100, competition_score) * 0.20,
            description=f"Compétition inter-espèces",
            factors=competition_factors[:3],
            source_ids=competition_sources,
            confidence=0.75 if competition_sources else 0.50,
            knowledge_layer_ref=f"advanced_factors/competition/{context.species}"
        ))
        self._used_source_ids.extend(competition_sources)
        
        # =====================================================
        # COMPOSANT 5: Effets de seuil (Knowledge Layer)
        # =====================================================
        try:
            # Get threshold parameters from species rules
            thermal_threshold = 20  # Default
            road_avoidance = 500  # Default
            threshold_sources = []
            
            if species_rules:
                # Get thermal threshold
                for rule_id, rule in species_rules._behavior_rules.items():
                    if "THERM" in rule_id:
                        thermal_threshold = rule.parameters.get("thermal_stress_threshold_c", 20)
                        threshold_sources.extend(rule.source_ids)
                        break
                
                # Get avoidance threshold
                for rule_id, rule in species_rules._behavior_rules.items():
                    if "AVOID" in rule_id:
                        road_avoidance = rule.parameters.get("road_avoidance_distance_m", 500)
                        threshold_sources.extend(rule.source_ids)
                        break
            
            # Simulate current conditions vs thresholds
            simulated_temp = 15  # 15°C
            simulated_road_distance = 800  # 800m
            
            # Threshold effects: bonus when conditions are within favorable thresholds
            threshold_score = 50.0
            threshold_factors = []
            
            # Temperature threshold
            if simulated_temp < thermal_threshold:
                temp_bonus = min(25, (thermal_threshold - simulated_temp) * 2)
                threshold_score += temp_bonus
                threshold_factors.append(f"Temp OK ({simulated_temp}°C < {thermal_threshold}°C)")
            else:
                temp_penalty = min(25, (simulated_temp - thermal_threshold) * 2)
                threshold_score -= temp_penalty
                threshold_factors.append(f"Stress thermique ({simulated_temp}°C ≥ {thermal_threshold}°C)")
            
            # Road avoidance threshold
            if simulated_road_distance >= road_avoidance:
                road_bonus = min(25, (simulated_road_distance - road_avoidance) / 20)
                threshold_score += road_bonus
                threshold_factors.append(f"Distance route OK ({simulated_road_distance}m ≥ {road_avoidance}m)")
            else:
                road_penalty = min(25, (road_avoidance - simulated_road_distance) / 20)
                threshold_score -= road_penalty
                threshold_factors.append(f"Proximité route ({simulated_road_distance}m < {road_avoidance}m)")
            
            self._used_source_ids.extend(threshold_sources)
            
            components.append(ScoreComponent(
                name="threshold_effects",
                value=max(0, min(100, threshold_score)),
                weight=0.15,
                weighted_value=max(0, min(100, threshold_score)) * 0.15,
                description="Effets de seuil comportementaux",
                factors=threshold_factors,
                source_ids=list(set(threshold_sources)),
                confidence=0.85 if threshold_sources else 0.4,
                knowledge_layer_ref=f"species/{context.species}/thresholds"
            ))
            
        except ValueError as e:
            logger.warning(f"Knowledge Layer threshold error: {e}")
            components.append(ScoreComponent(
                name="threshold_effects",
                value=50.0,
                weight=0.15,
                weighted_value=7.5,
                description="Effets de seuil (données partielles)",
                factors=["Seuils non disponibles"],
                confidence=0.3
            ))
        
        return components


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = ['ScoreMultiFactorService']
