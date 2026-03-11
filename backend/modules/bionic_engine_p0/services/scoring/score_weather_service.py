"""
BIONIC ENGINE — Score Weather Service
======================================
Service de calcul du score d'impact météorologique.

SCORE #4: WEATHER
- Évalue l'impact des conditions météo sur l'activité animale
- Facteurs: température, vent, précipitations, pression, visibilité

KNOWLEDGE LAYER INTEGRATION (PHASE 7):
- Pondérations CLIM-THERM, CLIM-WIND, CLIM-SNOW calibrées
- Seuils de stress thermique par espèce
- Variations saisonnières

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


class ScoreWeatherService(BaseScoreService):
    """
    Service de calcul du score météo.
    
    KNOWLEDGE LAYER INTEGRATED:
    - Pondérations CLIM-THERM, CLIM-WIND, CLIM-SNOW calibrées
    - Seuils de stress thermique par espèce (MOOSE-THERM-001)
    - Variations saisonnières (winter amplification)
    """
    
    def _get_category(self) -> ScoreCategory:
        return ScoreCategory.WEATHER
    
    def _get_default_weight(self) -> ScoreWeight:
        return ScoreWeight(
            category=ScoreCategory.WEATHER,
            weight=0.12,
            description="Impact conditions météorologiques (Knowledge Layer)"
        )
    
    def _get_score_name(self) -> str:
        return "Score Météo"
    
    def _calculate_components(self, context: ScoreContext) -> List[ScoreComponent]:
        """
        Calcule les composants du score météo avec Knowledge Layer.
        
        Utilise:
        - CLIM-THERM pour le confort thermique
        - CLIM-WIND pour l'exposition au vent
        - CLIM-SNOW pour les conditions de neige
        - Seuils de stress thermique par espèce
        """
        components = []
        
        # Get species thermal rules
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
        # COMPOSANT 1: Confort thermique (Knowledge Layer)
        # =====================================================
        try:
            therm_weight, therm_conf, therm_sources = self.get_knowledge_layer_weight("CLIM-THERM")
            
            # Get species-specific thermal thresholds
            thermal_stress_threshold = 20  # default
            critical_temp = 27
            
            if species_rules:
                for rule_id, rule in species_rules._behavior_rules.items():
                    if "THERM" in rule_id:
                        thermal_stress_threshold = rule.parameters.get("thermal_stress_threshold_c", 20)
                        critical_temp = rule.parameters.get("critical_temperature_c", 27)
                        self._used_source_ids.extend(rule.source_ids)
                        break
            
            # Simulate current temperature (would come from weather API)
            simulated_temp = 15  # 15°C
            
            # Calculate thermal comfort score
            if simulated_temp < thermal_stress_threshold:
                temp_score = 80 + min(20, (thermal_stress_threshold - simulated_temp) * 2)
            elif simulated_temp < critical_temp:
                temp_score = 80 - ((simulated_temp - thermal_stress_threshold) / (critical_temp - thermal_stress_threshold)) * 40
            else:
                temp_score = max(20, 40 - (simulated_temp - critical_temp) * 5)
            
            components.append(ScoreComponent(
                name="temperature",
                value=min(100, temp_score),
                weight=0.30,
                weighted_value=min(100, temp_score) * 0.30,
                description=f"Confort thermique ({simulated_temp}°C, seuil: {thermal_stress_threshold}°C)",
                factors=[f"Température: {simulated_temp}°C", f"Stress thermique: {thermal_stress_threshold}°C"],
                source_ids=therm_sources,
                confidence=therm_conf,
                knowledge_layer_ref="weights/CLIM-THERM"
            ))
            
        except ValueError as e:
            logger.warning(f"Knowledge Layer CLIM-THERM error: {e}")
            components.append(ScoreComponent(
                name="temperature",
                value=50.0,
                weight=0.30,
                weighted_value=15.0,
                description="Température (données partielles)",
                factors=["Pondération non disponible"],
                confidence=0.3
            ))
        
        # =====================================================
        # COMPOSANT 2: Exposition au vent (Knowledge Layer)
        # =====================================================
        try:
            wind_weight, wind_conf, wind_sources = self.get_knowledge_layer_weight("CLIM-WIND")
            
            # Simulate wind conditions (would come from weather API)
            simulated_wind_kmh = 15  # 15 km/h
            
            # Wind scoring: low wind is generally favorable
            if simulated_wind_kmh < 10:
                wind_score = 85
            elif simulated_wind_kmh < 20:
                wind_score = 70
            elif simulated_wind_kmh < 30:
                wind_score = 50
            else:
                wind_score = max(20, 50 - (simulated_wind_kmh - 30))
            
            components.append(ScoreComponent(
                name="wind",
                value=wind_score,
                weight=0.20,
                weighted_value=wind_score * 0.20,
                description=f"Exposition au vent ({simulated_wind_kmh} km/h)",
                factors=[f"Vent: {simulated_wind_kmh} km/h"],
                source_ids=wind_sources,
                confidence=wind_conf,
                knowledge_layer_ref="weights/CLIM-WIND"
            ))
            
        except ValueError as e:
            logger.warning(f"Knowledge Layer CLIM-WIND error: {e}")
            components.append(ScoreComponent(
                name="wind",
                value=50.0,
                weight=0.20,
                weighted_value=10.0,
                description="Vent (données partielles)",
                factors=["Pondération non disponible"],
                confidence=0.3
            ))
        
        # =====================================================
        # COMPOSANT 3: Conditions de neige (Knowledge Layer)
        # =====================================================
        try:
            snow_weight, snow_conf, snow_sources = self.get_knowledge_layer_weight("CLIM-SNOW")
            
            # Get species variation for snow
            hw = self._habitat_weights.get("CLIM-SNOW")
            species_snow_factor = 1.0
            if hw and context.species.lower() in ["orignal", "moose"]:
                species_snow_factor = hw.species_variations.get("moose", 0.70)
            elif hw and context.species.lower() in ["deer", "cerf"]:
                species_snow_factor = hw.species_variations.get("deer", 1.0)
            
            # Simulate snow depth (would come from weather data)
            simulated_snow_cm = 0  # No snow in September
            
            # Score based on snow and species adaptation
            if simulated_snow_cm == 0:
                snow_score = 75  # Neutral
            elif simulated_snow_cm < 30:
                snow_score = 70 - (simulated_snow_cm * species_snow_factor)
            else:
                snow_score = max(20, 40 - (simulated_snow_cm - 30) * 0.5 * species_snow_factor)
            
            components.append(ScoreComponent(
                name="snow_conditions",
                value=max(0, snow_score),
                weight=0.15,
                weighted_value=max(0, snow_score) * 0.15,
                description=f"Conditions de neige ({simulated_snow_cm}cm)",
                factors=[f"Neige: {simulated_snow_cm}cm", f"Facteur espèce: {species_snow_factor:.2f}"],
                source_ids=snow_sources,
                confidence=snow_conf,
                knowledge_layer_ref="weights/CLIM-SNOW"
            ))
            
        except ValueError as e:
            logger.warning(f"Knowledge Layer CLIM-SNOW error: {e}")
            components.append(ScoreComponent(
                name="snow_conditions",
                value=50.0,
                weight=0.15,
                weighted_value=7.5,
                description="Neige (données partielles)",
                factors=["Pondération non disponible"],
                confidence=0.3
            ))
        
        # =====================================================
        # COMPOSANT 4: Pression atmosphérique
        # =====================================================
        # Using general weather knowledge (no specific KL weight)
        simulated_pressure_hpa = 1015  # Normal pressure
        pressure_trend = "stable"
        
        # Rising pressure is generally favorable for wildlife activity
        if pressure_trend == "rising":
            pressure_score = 80
        elif pressure_trend == "stable" and simulated_pressure_hpa > 1010:
            pressure_score = 70
        else:
            pressure_score = 50
        
        components.append(ScoreComponent(
            name="pressure",
            value=pressure_score,
            weight=0.20,
            weighted_value=pressure_score * 0.20,
            description=f"Pression atmosphérique ({simulated_pressure_hpa} hPa, {pressure_trend})",
            factors=[f"Pression: {simulated_pressure_hpa} hPa", f"Tendance: {pressure_trend}"],
            source_ids=[],
            confidence=0.70,
            knowledge_layer_ref="general/pressure"
        ))
        
        # =====================================================
        # COMPOSANT 5: Visibilité
        # =====================================================
        simulated_visibility_km = 10  # Good visibility
        
        if simulated_visibility_km > 8:
            visibility_score = 75
        elif simulated_visibility_km > 4:
            visibility_score = 60
        else:
            visibility_score = 40
        
        components.append(ScoreComponent(
            name="visibility",
            value=visibility_score,
            weight=0.15,
            weighted_value=visibility_score * 0.15,
            description=f"Visibilité ({simulated_visibility_km} km)",
            factors=[f"Visibilité: {simulated_visibility_km} km"],
            source_ids=[],
            confidence=0.65,
            knowledge_layer_ref="general/visibility"
        ))
        
        return components


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = ['ScoreWeatherService']
