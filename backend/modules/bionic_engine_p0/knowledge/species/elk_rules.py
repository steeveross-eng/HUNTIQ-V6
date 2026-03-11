"""
BIONIC V5 — ELK BEHAVIOR RULES
===============================
PHASE 7 — Knowledge Layer

Règles comportementales pour l'élan/wapiti (Cervus canadensis).

SOURCES PRINCIPALES:
- SRC-USGS-001: USGS Wildlife Studies
- SRC-ABBC-001: Alberta/BC Wildlife Programs

VERSION: 1.0.0
"""

from typing import List, Tuple
from .base import (
    SpeciesRulesBase,
    BehaviorRule,
    BehaviorType,
    ActivityPattern,
    HabitatPreference
)


class ElkRules(SpeciesRulesBase):
    """Règles comportementales pour l'élan/wapiti"""
    
    def __init__(self):
        super().__init__()
        self.species_code = "elk"
        self.species_name_fr = "Wapiti"
        self.species_name_en = "Elk"
        self.scientific_name = "Cervus canadensis"
    
    def _initialize_rules(self):
        """Initialiser les règles"""
        
        self._behavior_rules["ELK-FEED-001"] = BehaviorRule(
            rule_id="ELK-FEED-001",
            behavior_type=BehaviorType.FEEDING,
            description="Le wapiti est principalement un brouteur de prairies et de zones alpines.",
            source_ids=["SRC-USGS-001", "SRC-ABBC-001"],
            confidence_score=0.90,
            seasons=["all"],
            parameters={
                "preferred_grass_height_cm": 15,
                "grazing_hours_per_day": 8
            }
        )
        
        self._behavior_rules["ELK-MOV-001"] = BehaviorRule(
            rule_id="ELK-MOV-001",
            behavior_type=BehaviorType.MOVEMENT,
            description="Le wapiti effectue des migrations altitudinales saisonnières.",
            source_ids=["SRC-USGS-001", "SRC-ABBC-001"],
            confidence_score=0.92,
            seasons=["all"],
            parameters={
                "summer_elevation_m": 2500,
                "winter_elevation_m": 1500,
                "migration_distance_km": 50,
                "home_range_km2": 100
            }
        )
        
        self._behavior_rules["ELK-RUT-001"] = BehaviorRule(
            rule_id="ELK-RUT-001",
            behavior_type=BehaviorType.RUT,
            description="Le rut du wapiti (bugle) est spectaculaire et se déroule en septembre-octobre.",
            source_ids=["SRC-USGS-001", "SRC-ME-001"],
            confidence_score=0.94,
            seasons=["rut"],
            parameters={
                "rut_start_date": "09-01",
                "rut_peak_date": "09-20",
                "rut_end_date": "10-15",
                "bugling_frequency": "very_high",
                "harem_size_avg": 15
            }
        )
        
        self._behavior_rules["ELK-SOCIAL-001"] = BehaviorRule(
            rule_id="ELK-SOCIAL-001",
            behavior_type=BehaviorType.SOCIAL,
            description="Le wapiti est grégaire et forme des hardes importantes.",
            source_ids=["SRC-USGS-001"],
            confidence_score=0.88,
            seasons=["all"],
            parameters={
                "herd_size_summer": 50,
                "herd_size_winter": 200,
                "bull_groups_non_rut": 10
            }
        )
        
        # Patterns d'activité
        for hour in range(24):
            if hour in [5, 6, 7, 17, 18, 19, 20]:
                level = 0.85
            elif hour in [8, 9, 16]:
                level = 0.55
            elif 10 <= hour <= 15:
                level = 0.30
            else:
                level = 0.25
            
            self._activity_patterns[hour] = ActivityPattern(
                hour=hour,
                activity_level=level,
                source_ids=["SRC-USGS-001"],
                confidence=0.85
            )
        
        # Préférences d'habitat
        self._habitat_preferences["alpine_meadow"] = HabitatPreference(
            habitat_type="alpine_meadow",
            preference_score=0.95,
            source_ids=["SRC-USGS-001", "SRC-ABBC-001"],
            confidence=0.92,
            seasonal_variation={"summer": 0.98, "winter": 0.40}
        )
        
        self._habitat_preferences["mountain_forest"] = HabitatPreference(
            habitat_type="mountain_forest",
            preference_score=0.80,
            source_ids=["SRC-USGS-001"],
            confidence=0.85
        )
        
        self._habitat_preferences["valley_grassland"] = HabitatPreference(
            habitat_type="valley_grassland",
            preference_score=0.85,
            source_ids=["SRC-ABBC-001"],
            confidence=0.88,
            seasonal_variation={"winter": 0.95}
        )
    
    def get_activity_level(self, hour: int, season: str = "default") -> Tuple[float, List[str]]:
        pattern = self._activity_patterns.get(hour % 24)
        if not pattern:
            return (0.5, [])
        
        base_level = pattern.activity_level
        
        # Rut: bugling augmente l'activité en soirée
        if season == "rut" and 17 <= hour <= 21:
            base_level = min(1.0, base_level * 1.4)
        
        return (round(base_level, 2), pattern.source_ids)
    
    def get_habitat_score(self, habitat_type: str, season: str = "default") -> Tuple[float, List[str]]:
        pref = self._habitat_preferences.get(habitat_type)
        if not pref:
            return (0.5, [])
        
        if season in pref.seasonal_variation:
            score = pref.seasonal_variation[season]
        else:
            score = pref.preference_score
        
        return (round(score, 2), pref.source_ids)


__all__ = ['ElkRules']
