"""
BIONIC V5 — MOOSE BEHAVIOR RULES
=================================
PHASE 7 — Knowledge Layer

Règles comportementales pour l'orignal (Alces alces).
Toutes les règles sont traçables à des sources scientifiques.

SOURCES PRINCIPALES:
- SRC-LAVAL-001: Université Laval - Écologie de l'orignal
- SRC-MFFP-001: MFFP Québec - Plan de gestion
- SRC-PARCS-001: Parcs Canada - Télémétrie
- SRC-GAGNON-001: Expertise terrain guides nordiques

VERSION: 1.0.0
Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
"""

from typing import Dict, List, Tuple, Any
from .base import (
    SpeciesRulesBase,
    BehaviorRule,
    BehaviorType,
    ActivityPeriod,
    ActivityPattern,
    HabitatPreference
)


class MooseRules(SpeciesRulesBase):
    """
    Règles comportementales pour l'orignal (Alces alces).
    
    L'orignal est le plus grand cervidé d'Amérique du Nord.
    Ses comportements varient significativement selon les saisons,
    particulièrement pendant le rut (mi-septembre à mi-octobre).
    """
    
    def __init__(self):
        super().__init__()
        self.species_code = "moose"
        self.species_name_fr = "Orignal"
        self.species_name_en = "Moose"
        self.scientific_name = "Alces alces"
    
    def _initialize_rules(self):
        """Initialiser les règles comportementales de l'orignal"""
        
        # =====================================================
        # RÈGLES DE COMPORTEMENT
        # =====================================================
        
        # Alimentation
        self._behavior_rules["MOOSE-FEED-001"] = BehaviorRule(
            rule_id="MOOSE-FEED-001",
            behavior_type=BehaviorType.FEEDING,
            description="L'orignal se nourrit principalement à l'aube et au crépuscule, avec une préférence pour les zones de bordure forêt-eau.",
            source_ids=["SRC-LAVAL-001", "SRC-MFFP-001"],
            confidence_score=0.92,
            seasons=["all"],
            time_periods=[ActivityPeriod.DAWN, ActivityPeriod.DUSK],
            parameters={
                "peak_hours": [6, 7, 17, 18],
                "preferred_distance_water_m": 200,
                "browse_height_m": 2.5
            }
        )
        
        self._behavior_rules["MOOSE-FEED-002"] = BehaviorRule(
            rule_id="MOOSE-FEED-002",
            behavior_type=BehaviorType.FEEDING,
            description="En été, l'orignal favorise les plantes aquatiques riches en sodium.",
            source_ids=["SRC-LAVAL-001", "SRC-PARCS-001"],
            confidence_score=0.88,
            seasons=["summer"],
            time_periods=[ActivityPeriod.DAWN, ActivityPeriod.MORNING, ActivityPeriod.DUSK],
            parameters={
                "aquatic_feeding_depth_m": 1.5,
                "sodium_requirement_mg_day": 3000
            }
        )
        
        # Repos
        self._behavior_rules["MOOSE-BED-001"] = BehaviorRule(
            rule_id="MOOSE-BED-001",
            behavior_type=BehaviorType.BEDDING,
            description="L'orignal se couche dans des zones avec couvert dense, généralement sur des pentes douces orientées vers le soleil.",
            source_ids=["SRC-MFFP-001", "SRC-GAGNON-001"],
            confidence_score=0.85,
            seasons=["all"],
            time_periods=[ActivityPeriod.MIDDAY, ActivityPeriod.NIGHT],
            parameters={
                "preferred_slope_degrees": 5,
                "min_cover_density_percent": 60,
                "preferred_orientation": "south"
            }
        )
        
        # Mouvement
        self._behavior_rules["MOOSE-MOV-001"] = BehaviorRule(
            rule_id="MOOSE-MOV-001",
            behavior_type=BehaviorType.MOVEMENT,
            description="L'orignal utilise des corridors de déplacement réguliers entre ses zones d'alimentation et de repos.",
            source_ids=["SRC-PARCS-001", "SRC-LAVAL-001"],
            confidence_score=0.90,
            seasons=["all"],
            parameters={
                "average_daily_distance_km": 5.0,
                "home_range_km2": 25.0,
                "corridor_width_m": 50
            }
        )
        
        # Rut
        self._behavior_rules["MOOSE-RUT-001"] = BehaviorRule(
            rule_id="MOOSE-RUT-001",
            behavior_type=BehaviorType.RUT,
            description="Pendant le rut (mi-sept à mi-oct), les mâles deviennent très actifs et parcourent de grandes distances.",
            source_ids=["SRC-LAVAL-001", "SRC-MFFP-001", "SRC-GAGNON-001"],
            confidence_score=0.95,
            seasons=["rut"],
            parameters={
                "rut_start_date": "09-15",
                "rut_peak_date": "09-25",
                "rut_end_date": "10-15",
                "movement_multiplier": 2.5,
                "activity_multiplier": 1.8,
                "response_to_calls": 0.85
            }
        )
        
        self._behavior_rules["MOOSE-RUT-002"] = BehaviorRule(
            rule_id="MOOSE-RUT-002",
            behavior_type=BehaviorType.RUT,
            description="Les mâles en rut répondent aux appels (calls) et créent des souilles (wallow).",
            source_ids=["SRC-GAGNON-001", "SRC-LAVAL-001"],
            confidence_score=0.88,
            seasons=["rut"],
            parameters={
                "wallow_diameter_m": 3.0,
                "scent_marking_frequency": "high",
                "vocal_activity": "very_high"
            }
        )
        
        # Évitement
        self._behavior_rules["MOOSE-AVOID-001"] = BehaviorRule(
            rule_id="MOOSE-AVOID-001",
            behavior_type=BehaviorType.AVOIDANCE,
            description="L'orignal évite les zones à forte pression humaine et les routes principales.",
            source_ids=["SRC-MFFP-001", "SRC-PARCS-001"],
            confidence_score=0.87,
            seasons=["all"],
            parameters={
                "road_avoidance_distance_m": 500,
                "human_activity_avoidance_m": 300,
                "noise_sensitivity": "medium"
            }
        )
        
        # Thermorégulation
        self._behavior_rules["MOOSE-THERM-001"] = BehaviorRule(
            rule_id="MOOSE-THERM-001",
            behavior_type=BehaviorType.THERMAL,
            description="L'orignal est sensible à la chaleur et recherche des refuges thermiques au-dessus de 20°C.",
            source_ids=["SRC-LAVAL-001", "SRC-USGS-001"],
            confidence_score=0.90,
            seasons=["summer"],
            parameters={
                "thermal_stress_threshold_c": 20,
                "critical_temperature_c": 27,
                "preferred_water_immersion": True,
                "shade_seeking_threshold_c": 22
            }
        )
        
        # =====================================================
        # PATTERNS D'ACTIVITÉ HORAIRE
        # =====================================================
        
        # Pattern horaire (0-23h) - Sourcé Laval + MFFP
        hourly_patterns = {
            0: (0.20, ["SRC-LAVAL-001"]),
            1: (0.15, ["SRC-LAVAL-001"]),
            2: (0.15, ["SRC-LAVAL-001"]),
            3: (0.20, ["SRC-LAVAL-001"]),
            4: (0.50, ["SRC-LAVAL-001", "SRC-GAGNON-001"]),
            5: (0.80, ["SRC-LAVAL-001", "SRC-MFFP-001"]),
            6: (0.90, ["SRC-LAVAL-001", "SRC-MFFP-001"]),
            7: (0.85, ["SRC-LAVAL-001"]),
            8: (0.60, ["SRC-LAVAL-001"]),
            9: (0.40, ["SRC-LAVAL-001"]),
            10: (0.25, ["SRC-LAVAL-001"]),
            11: (0.20, ["SRC-LAVAL-001"]),
            12: (0.20, ["SRC-LAVAL-001"]),
            13: (0.25, ["SRC-LAVAL-001"]),
            14: (0.30, ["SRC-LAVAL-001"]),
            15: (0.45, ["SRC-LAVAL-001"]),
            16: (0.70, ["SRC-LAVAL-001", "SRC-MFFP-001"]),
            17: (0.90, ["SRC-LAVAL-001", "SRC-MFFP-001"]),
            18: (0.85, ["SRC-LAVAL-001"]),
            19: (0.70, ["SRC-LAVAL-001"]),
            20: (0.55, ["SRC-LAVAL-001"]),
            21: (0.40, ["SRC-LAVAL-001"]),
            22: (0.30, ["SRC-LAVAL-001"]),
            23: (0.25, ["SRC-LAVAL-001"])
        }
        
        for hour, (level, sources) in hourly_patterns.items():
            self._activity_patterns[hour] = ActivityPattern(
                hour=hour,
                activity_level=level,
                source_ids=sources,
                confidence=0.85,
                notes="Pattern standard hors période de rut"
            )
        
        # =====================================================
        # PRÉFÉRENCES D'HABITAT
        # =====================================================
        
        self._habitat_preferences["coniferous_forest"] = HabitatPreference(
            habitat_type="coniferous_forest",
            preference_score=0.85,
            source_ids=["SRC-LAVAL-001", "SRC-MFFP-001"],
            confidence=0.90,
            seasonal_variation={"winter": 0.95, "summer": 0.75, "rut": 0.80}
        )
        
        self._habitat_preferences["mixed_forest"] = HabitatPreference(
            habitat_type="mixed_forest",
            preference_score=0.90,
            source_ids=["SRC-LAVAL-001", "SRC-MFFP-001"],
            confidence=0.92,
            seasonal_variation={"winter": 0.85, "summer": 0.90, "rut": 0.92}
        )
        
        self._habitat_preferences["wetland"] = HabitatPreference(
            habitat_type="wetland",
            preference_score=0.80,
            source_ids=["SRC-LAVAL-001", "SRC-PARCS-001"],
            confidence=0.88,
            seasonal_variation={"winter": 0.30, "summer": 0.95, "rut": 0.60}
        )
        
        self._habitat_preferences["lake_shore"] = HabitatPreference(
            habitat_type="lake_shore",
            preference_score=0.75,
            source_ids=["SRC-LAVAL-001"],
            confidence=0.85,
            seasonal_variation={"winter": 0.20, "summer": 0.90, "rut": 0.50}
        )
        
        self._habitat_preferences["regeneration_zone"] = HabitatPreference(
            habitat_type="regeneration_zone",
            preference_score=0.85,
            source_ids=["SRC-MFFP-001", "SRC-GAGNON-001"],
            confidence=0.87,
            seasonal_variation={"winter": 0.70, "summer": 0.90, "rut": 0.85}
        )
        
        self._habitat_preferences["clearcut"] = HabitatPreference(
            habitat_type="clearcut",
            preference_score=0.65,
            source_ids=["SRC-MFFP-001"],
            confidence=0.80,
            seasonal_variation={"winter": 0.40, "summer": 0.80, "rut": 0.60}
        )
    
    def get_activity_level(self, hour: int, season: str = "default") -> Tuple[float, List[str]]:
        """
        Obtenir le niveau d'activité pour une heure donnée.
        
        Args:
            hour: Heure (0-23)
            season: Saison (summer, winter, rut, default)
            
        Returns:
            Tuple[float, List[str]]: (niveau d'activité ajusté, source_ids)
        """
        hour = hour % 24
        pattern = self._activity_patterns.get(hour)
        
        if not pattern:
            return (0.5, [])
        
        base_level = pattern.activity_level
        
        # Ajustement saisonnier
        if season == "rut":
            # Pendant le rut, activité accrue tout au long de la journée
            base_level = min(1.0, base_level * 1.5)
            sources = pattern.source_ids + ["SRC-GAGNON-001"]
        elif season == "winter":
            # En hiver, activité réduite pendant les heures froides
            if 0 <= hour <= 6:
                base_level *= 0.7
            sources = pattern.source_ids
        else:
            sources = pattern.source_ids
        
        return (round(base_level, 2), sources)
    
    def get_habitat_score(self, habitat_type: str, season: str = "default") -> Tuple[float, List[str]]:
        """
        Obtenir le score de préférence pour un type d'habitat.
        
        Args:
            habitat_type: Type d'habitat
            season: Saison
            
        Returns:
            Tuple[float, List[str]]: (score de préférence, source_ids)
        """
        pref = self._habitat_preferences.get(habitat_type)
        
        if not pref:
            return (0.5, [])
        
        if season in pref.seasonal_variation:
            score = pref.seasonal_variation[season]
        else:
            score = pref.preference_score
        
        return (round(score, 2), pref.source_ids)
    
    def get_rut_parameters(self) -> Dict[str, Any]:
        """Obtenir les paramètres spécifiques au rut"""
        rule = self._behavior_rules.get("MOOSE-RUT-001")
        if rule:
            return {
                "parameters": rule.parameters,
                "source_ids": rule.source_ids,
                "confidence": rule.confidence_score
            }
        return {}
    
    def get_thermal_thresholds(self) -> Dict[str, Any]:
        """Obtenir les seuils de stress thermique"""
        rule = self._behavior_rules.get("MOOSE-THERM-001")
        if rule:
            return {
                "parameters": rule.parameters,
                "source_ids": rule.source_ids,
                "confidence": rule.confidence_score
            }
        return {}


__all__ = ['MooseRules']
