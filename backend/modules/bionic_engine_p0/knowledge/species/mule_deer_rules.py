"""
BIONIC V5 — MULE DEER BEHAVIOR RULES
=====================================
PHASE 7 — Knowledge Layer

Règles comportementales pour le cerf-mulet (Odocoileus hemionus).

SOURCES PRINCIPALES:
- SRC-USGS-001: USGS Wildlife Studies
- SRC-ABBC-001: Alberta/BC Wildlife Programs
- SRC-ME-001: MeatEater Conservation Data

VERSION: 1.0.0
"""

from typing import List, Tuple
from .base import (
    SpeciesRulesBase,
    BehaviorRule,
    BehaviorType,
    ActivityPeriod,
    ActivityPattern,
    HabitatPreference
)


class MuleDeerRules(SpeciesRulesBase):
    """Règles comportementales pour le cerf-mulet"""
    
    def __init__(self):
        super().__init__()
        self.species_code = "mule_deer"
        self.species_name_fr = "Cerf-mulet"
        self.species_name_en = "Mule Deer"
        self.scientific_name = "Odocoileus hemionus"
    
    def _initialize_rules(self):
        """Initialiser les règles"""
        
        self._behavior_rules["MULE-FEED-001"] = BehaviorRule(
            rule_id="MULE-FEED-001",
            behavior_type=BehaviorType.FEEDING,
            description="Le cerf-mulet préfère les terrains accidentés et les zones de broussailles.",
            source_ids=["SRC-USGS-001", "SRC-ABBC-001"],
            confidence_score=0.88,
            seasons=["all"],
            time_periods=[ActivityPeriod.DAWN, ActivityPeriod.DUSK],
            parameters={
                "terrain_preference": "rugged",
                "elevation_preference_m": 1500,
                "browse_species": ["sagebrush", "bitterbrush", "mountain_mahogany"]
            }
        )
        
        self._behavior_rules["MULE-MOV-001"] = BehaviorRule(
            rule_id="MULE-MOV-001",
            behavior_type=BehaviorType.MOVEMENT,
            description="Le cerf-mulet effectue des migrations saisonnières significatives.",
            source_ids=["SRC-USGS-001", "SRC-ABBC-001"],
            confidence_score=0.90,
            seasons=["all"],
            parameters={
                "migration_distance_km": 80,
                "elevation_change_m": 1000,
                "home_range_km2": 15.0
            }
        )
        
        self._behavior_rules["MULE-RUT-001"] = BehaviorRule(
            rule_id="MULE-RUT-001",
            behavior_type=BehaviorType.RUT,
            description="Le rut du cerf-mulet est plus tardif (novembre-décembre).",
            source_ids=["SRC-USGS-001", "SRC-ME-001"],
            confidence_score=0.87,
            seasons=["rut"],
            parameters={
                "rut_start_date": "11-10",
                "rut_peak_date": "11-25",
                "rut_end_date": "12-15"
            }
        )
        
        # Patterns d'activité
        for hour in range(24):
            if hour in [5, 6, 7, 17, 18, 19]:
                level = 0.85
            elif hour in [8, 9, 16]:
                level = 0.50
            elif 10 <= hour <= 15:
                level = 0.25
            else:
                level = 0.30
            
            self._activity_patterns[hour] = ActivityPattern(
                hour=hour,
                activity_level=level,
                source_ids=["SRC-USGS-001"],
                confidence=0.82
            )
        
        # Préférences d'habitat
        self._habitat_preferences["sagebrush"] = HabitatPreference(
            habitat_type="sagebrush",
            preference_score=0.90,
            source_ids=["SRC-USGS-001", "SRC-ABBC-001"],
            confidence=0.88
        )
        
        self._habitat_preferences["mountain_terrain"] = HabitatPreference(
            habitat_type="mountain_terrain",
            preference_score=0.85,
            source_ids=["SRC-USGS-001"],
            confidence=0.85
        )
    
    def get_activity_level(self, hour: int, season: str = "default") -> Tuple[float, List[str]]:
        pattern = self._activity_patterns.get(hour % 24)
        if not pattern:
            return (0.5, [])
        return (pattern.activity_level, pattern.source_ids)
    
    def get_habitat_score(self, habitat_type: str, season: str = "default") -> Tuple[float, List[str]]:
        pref = self._habitat_preferences.get(habitat_type)
        if not pref:
            return (0.5, [])
        return (pref.preference_score, pref.source_ids)


__all__ = ['MuleDeerRules']
