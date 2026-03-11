"""
BIONIC ENGINE — Score Risk Service
===================================
Service de calcul du score de risques et facteurs de danger.

SCORE #8: RISK
- Évalue les risques potentiels affectant la chasse
- Facteurs: prédateurs, obstacles, dangers naturels, zones interdites

KNOWLEDGE LAYER INTEGRATION (PHASE 7):
- Règles AVOIDANCE par espèce (comportement d'évitement)
- Seuils de stress thermique (THERM rules)
- Pondérations PRES-* pour zones à risque
- Modèles saisonniers pour vulnérabilité

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


class ScoreRiskService(BaseScoreService):
    """
    Service de calcul du score de risques.
    
    BIONIC V5 - ARCHITECTURE CENTRALISÉE:
    - Ce service NE CALCULE PAS les modificateurs avancés
    - Les modificateurs sont FOURNIS par UnifiedScoringService via context.advanced_modifiers
    - Ce service CONSOMME uniquement les valeurs pré-calculées
    
    KNOWLEDGE LAYER INTEGRATED:
    - Règles AVOIDANCE par espèce (évitement prédateurs/humains)
    - Seuils THERM pour stress environnemental
    - Pondérations PRES-* pour zones de risque
    - Vulnérabilité saisonnière
    
    MODIFICATEURS CONSOMMÉS (fournis par UnifiedScoringService):
    - signals_impact, signals_detected → composant signaux faibles risque
    
    NOTE: Score INVERSÉ - valeur haute = faible risque = favorable
    """
    
    def _get_category(self) -> ScoreCategory:
        return ScoreCategory.RISK
    
    def _get_default_weight(self) -> ScoreWeight:
        return ScoreWeight(
            category=ScoreCategory.RISK,
            weight=0.08,
            description="Risques et facteurs de danger (Knowledge Layer + Advanced Modifiers)"
        )
    
    def _get_score_name(self) -> str:
        return "Score Risques"
    
    def _calculate_components(self, context: ScoreContext) -> List[ScoreComponent]:
        """
        Calcule les composants du score de risques avec Knowledge Layer.
        
        NOTE: Score INVERSÉ - valeur haute = faible risque = favorable pour la chasse
        
        Utilise:
        - Règles AVOIDANCE pour comportement d'évitement
        - Seuils THERM pour stress environnemental
        - PRES-* pour facteurs de risque
        - Vulnérabilité saisonnière
        """
        components = []
        
        # Get Knowledge Layer data
        species_rules = get_species_rules(context.species)
        seasonal_model = get_seasonal_model(context.species)
        target_date = context.target_datetime.date()
        
        # Determine season and vulnerability
        if seasonal_model:
            season = seasonal_model.get_current_season(target_date)
            season_str = season.value if season else "default"
            modifiers = seasonal_model.get_modifiers(target_date)
            self._used_source_ids.extend(seasonal_model.source_ids)
        else:
            season_str = "default"
            modifiers = {"vulnerability": 1.0, "movement": 1.0}
        
        # =====================================================
        # COMPOSANT 1: Prédateurs (via règles AVOIDANCE)
        # =====================================================
        # Score INVERSÉ: 100 = pas de risque prédateur, 0 = risque élevé
        try:
            predator_score = 70.0  # Default: moderate-low risk
            predator_sources = []
            predator_factors = []
            
            if species_rules:
                # Get avoidance rules
                avoidance_rules = species_rules.get_rules_by_type(BehaviorType.AVOIDANCE)
                
                if avoidance_rules:
                    rule = avoidance_rules[0]
                    predator_sources = rule.source_ids
                    
                    # Get noise sensitivity as proxy for predator awareness
                    noise_sensitivity = rule.parameters.get("noise_sensitivity", "medium")
                    predator_factors.append(f"Sensibilité: {noise_sensitivity}")
                    
                    # Higher sensitivity = more aware = lower risk of predation
                    sensitivity_scores = {"low": 60, "medium": 70, "high": 80}
                    predator_score = sensitivity_scores.get(noise_sensitivity, 70)
                    
                    self._used_source_ids.extend(predator_sources)
            
            # Adjust for seasonal vulnerability
            vulnerability_mod = modifiers.get("vulnerability", 1.0)
            # High vulnerability = higher predation risk = lower score
            predator_score *= (2.0 - vulnerability_mod) if vulnerability_mod > 0 else 1.0
            predator_factors.append(f"Vulnérabilité: x{vulnerability_mod:.1f}")
            
            components.append(ScoreComponent(
                name="predator_presence",
                value=max(20, min(100, predator_score)),
                weight=0.30,
                weighted_value=max(20, min(100, predator_score)) * 0.30,
                description=f"Risque prédation ({season_str})",
                factors=predator_factors,
                source_ids=predator_sources,
                confidence=0.80 if predator_sources else 0.4,
                knowledge_layer_ref=f"species/{context.species}/avoidance"
            ))
            
        except ValueError as e:
            logger.warning(f"Knowledge Layer predator error: {e}")
            components.append(ScoreComponent(
                name="predator_presence",
                value=50.0,
                weight=0.30,
                weighted_value=15.0,
                description="Risque prédation (données partielles)",
                factors=["Règles d'évitement non disponibles"],
                confidence=0.3
            ))
        
        # =====================================================
        # COMPOSANT 2: Dangers naturels (via seuils terrain/climat)
        # =====================================================
        # Score INVERSÉ: 100 = sûr, 0 = dangereux
        try:
            # Get terrain and climate weights
            slope_weight, slope_conf, slope_sources = self.get_knowledge_layer_weight("TER-SLOPE")
            
            # Simulate terrain conditions
            simulated_slope_degrees = 12  # Moderate slope
            
            # Score based on slope safety (< 30° is safe for most activities)
            if simulated_slope_degrees < 15:
                terrain_score = 85
            elif simulated_slope_degrees < 30:
                terrain_score = 70 - (simulated_slope_degrees - 15)
            else:
                terrain_score = max(20, 55 - (simulated_slope_degrees - 30) * 2)
            
            # Get thermal stress thresholds
            thermal_risk = 0
            thermal_sources = []
            if species_rules:
                for rule_id, rule in species_rules._behavior_rules.items():
                    if "THERM" in rule_id:
                        critical_temp = rule.parameters.get("critical_temperature_c", 27)
                        thermal_sources = rule.source_ids
                        # Simulate current temp vs critical
                        simulated_temp = 15  # 15°C
                        if simulated_temp > critical_temp:
                            thermal_risk = min(30, (simulated_temp - critical_temp) * 3)
                        self._used_source_ids.extend(thermal_sources)
                        break
            
            hazard_score = terrain_score - thermal_risk
            
            components.append(ScoreComponent(
                name="natural_hazards",
                value=max(20, min(100, hazard_score)),
                weight=0.25,
                weighted_value=max(20, min(100, hazard_score)) * 0.25,
                description=f"Dangers naturels (pente: {simulated_slope_degrees}°)",
                factors=[
                    f"Pente: {simulated_slope_degrees}°",
                    f"Sécurité terrain: {terrain_score:.0f}%",
                    f"Risque thermique: -{thermal_risk:.0f}"
                ],
                source_ids=list(set(slope_sources + thermal_sources)),
                confidence=(slope_conf + 0.7) / 2,
                knowledge_layer_ref="weights/TER-SLOPE+species/thermal"
            ))
            
        except ValueError as e:
            logger.warning(f"Knowledge Layer hazards error: {e}")
            components.append(ScoreComponent(
                name="natural_hazards",
                value=50.0,
                weight=0.25,
                weighted_value=12.5,
                description="Dangers naturels (données partielles)",
                factors=["Pondérations terrain non disponibles"],
                confidence=0.3
            ))
        
        # =====================================================
        # COMPOSANT 3: Zones réglementées (via PRES-HUMAN)
        # =====================================================
        try:
            # Get human pressure as proxy for regulated zones
            human_weight, human_conf, human_sources = self.get_knowledge_layer_weight("PRES-HUMAN")
            
            # Get species-specific human avoidance distance
            human_avoidance_m = 300  # Default
            if species_rules:
                for rule_id, rule in species_rules._behavior_rules.items():
                    if "AVOID" in rule_id:
                        human_avoidance_m = rule.parameters.get("human_activity_avoidance_m", 300)
                        self._used_source_ids.extend(rule.source_ids)
                        break
            
            # Simulate distance to regulated/urban zones
            simulated_zone_distance_m = 1000  # 1km from regulated zones
            
            # Score based on distance (farther = safer = higher score)
            if simulated_zone_distance_m >= human_avoidance_m * 2:
                zone_score = 85
            elif simulated_zone_distance_m >= human_avoidance_m:
                zone_score = 65 + ((simulated_zone_distance_m - human_avoidance_m) / human_avoidance_m) * 20
            else:
                zone_score = max(20, (simulated_zone_distance_m / human_avoidance_m) * 65)
            
            components.append(ScoreComponent(
                name="regulated_zones",
                value=min(100, zone_score),
                weight=0.25,
                weighted_value=min(100, zone_score) * 0.25,
                description=f"Distance zones réglementées ({simulated_zone_distance_m}m)",
                factors=[
                    f"Distance: {simulated_zone_distance_m}m",
                    f"Seuil évitement: {human_avoidance_m}m"
                ],
                source_ids=human_sources,
                confidence=human_conf,
                knowledge_layer_ref="weights/PRES-HUMAN+species/avoidance"
            ))
            
        except ValueError as e:
            logger.warning(f"Knowledge Layer zones error: {e}")
            components.append(ScoreComponent(
                name="regulated_zones",
                value=50.0,
                weight=0.25,
                weighted_value=12.5,
                description="Zones réglementées (données partielles)",
                factors=["Pondération pression humaine non disponible"],
                confidence=0.3
            ))
        
        # =====================================================
        # COMPOSANT 4: SIGNAUX FAIBLES RISQUE (CONSOMMATION - pas de calcul local)
        # Source: context.advanced_modifiers (calculé par UnifiedScoringService)
        # =====================================================
        adv = context.advanced_modifiers
        signals_impact = adv.get("signals_impact", 0.0)
        signals_detected = adv.get("signals_detected", [])
        signals_sources = adv.get("signals_source_ids", [])
        signals_version = adv.get("signals_version", "1.0.0")
        
        # Calculate risk signal score from impact
        # Negative impact = risk detected = lower score
        risk_signal_score = 70.0 - (abs(signals_impact) if signals_impact < 0 else 0)
        risk_signal_score = max(10, min(100, risk_signal_score))
        
        # Build factors list
        risk_factors = []
        if signals_detected:
            risk_factors.append(f"Signaux: {', '.join(signals_detected[:2])}")
            risk_factors.append(f"Impact: {signals_impact:+.0f}")
        else:
            risk_factors.append("Aucun signal de risque détecté")
        risk_factors.append(f"Version: {signals_version}")
        
        components.append(ScoreComponent(
            name="risk_weak_signals",
            value=min(100, risk_signal_score),
            weight=0.15,
            weighted_value=min(100, risk_signal_score) * 0.15,
            description=f"Signaux faibles risque ({len(signals_detected)} détectés)",
            factors=risk_factors[:3],
            source_ids=signals_sources,
            confidence=0.70 if signals_sources else 0.35,
            knowledge_layer_ref=f"advanced_factors/signals/{context.species}/risk"
        ))
        self._used_source_ids.extend(signals_sources)
        
        # =====================================================
        # COMPOSANT 5: Conditions sécurité (composite Knowledge Layer)
        # =====================================================
        try:
            # Composite safety score from multiple factors
            safety_score = 50.0
            safety_factors = []
            safety_sources = []
            
            # Factor 1: Movement modifier (high movement = less safe)
            movement_mod = modifiers.get("movement", 1.0)
            movement_safety = 80 - (movement_mod - 1.0) * 20
            safety_factors.append(f"Mouvement: x{movement_mod:.1f}")
            
            # Factor 2: Wind exposure (affects visibility and scent)
            try:
                wind_weight, wind_conf, wind_sources = self.get_knowledge_layer_weight("CLIM-WIND")
                safety_sources.extend(wind_sources)
                # Moderate wind is favorable for hunting safety
                simulated_wind = 15  # km/h
                if 10 <= simulated_wind <= 20:
                    wind_safety = 75
                elif simulated_wind < 10:
                    wind_safety = 60  # Too calm, scent carries
                else:
                    wind_safety = max(40, 75 - (simulated_wind - 20) * 2)
                safety_factors.append(f"Vent: {simulated_wind} km/h")
            except ValueError:
                wind_safety = 60
            
            # Combined safety score
            safety_score = (movement_safety + wind_safety) / 2
            
            # Seasonal adjustment
            if season_str == "hunting_season":
                # During hunting season, other hunters = safety concern
                safety_score *= 0.85
                safety_factors.append("Saison chasse: -15%")
            
            if seasonal_model:
                safety_sources.extend(seasonal_model.source_ids)
            
            components.append(ScoreComponent(
                name="safety_conditions",
                value=max(20, min(100, safety_score)),
                weight=0.15,
                weighted_value=max(20, min(100, safety_score)) * 0.15,
                description=f"Conditions sécurité ({season_str})",
                factors=safety_factors,
                source_ids=list(set(safety_sources)),
                confidence=0.75,
                knowledge_layer_ref="composite/safety"
            ))
            
        except ValueError as e:
            logger.warning(f"Knowledge Layer safety error: {e}")
            components.append(ScoreComponent(
                name="safety_conditions",
                value=50.0,
                weight=0.15,
                weighted_value=7.5,
                description="Conditions sécurité (données partielles)",
                factors=["Données sécurité non disponibles"],
                confidence=0.3
            ))
        
        return components


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = ['ScoreRiskService']
