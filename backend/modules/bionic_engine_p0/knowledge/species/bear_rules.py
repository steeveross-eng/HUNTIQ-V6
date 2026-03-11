"""
BIONIC V5 — BLACK BEAR BEHAVIOR RULES
======================================
PHASE 7 — Knowledge Layer

Règles comportementales pour l'ours noir (Ursus americanus).

SOURCES PRINCIPALES:
- SRC-MFFP-001: MFFP Québec
- SRC-PARCS-001: Parcs Canada
- SRC-USGS-001: USGS Wildlife Studies

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


class BearRules(SpeciesRulesBase):
    """Règles comportementales pour l'ours noir"""
    
    def __init__(self):
        super().__init__()
        self.species_code = "bear"
        self.species_name_fr = "Ours noir"
        self.species_name_en = "Black Bear"
        self.scientific_name = "Ursus americanus"
    
    def _initialize_rules(self):
        """Initialiser les règles"""
        
        self._behavior_rules["BEAR-FEED-001"] = BehaviorRule(
            rule_id="BEAR-FEED-001",
            behavior_type=BehaviorType.FEEDING,
            description="L'ours noir est omnivore avec une alimentation variable selon les saisons.",
            source_ids=["SRC-MFFP-001", "SRC-PARCS-001"],
            confidence_score=0.90,
            seasons=["all"],
            parameters={
                "spring_diet": ["grasses", "insects", "carrion"],
                "summer_diet": ["berries", "insects", "small_mammals"],
                "fall_diet": ["berries", "nuts", "acorns"],
                "hyperphagia_start": "08-15",
                "hyperphagia_end": "11-01"
            }
        )
        
        self._behavior_rules["BEAR-FEED-002"] = BehaviorRule(
            rule_id="BEAR-FEED-002",
            behavior_type=BehaviorType.FEEDING,
            description="Pendant l'hyperphagie (août-octobre), l'ours augmente drastiquement sa consommation.",
            source_ids=["SRC-MFFP-001", "SRC-USGS-001"],
            confidence_score=0.93,
            seasons=["fall"],
            parameters={
                "daily_intake_kg": 20,
                "weight_gain_per_day_kg": 1.5,
                "feeding_hours_per_day": 20
            }
        )
        
        self._behavior_rules["BEAR-MOV-001"] = BehaviorRule(
            rule_id="BEAR-MOV-001",
            behavior_type=BehaviorType.MOVEMENT,
            description="L'ours noir a un grand domaine vital et peut parcourir de longues distances.",
            source_ids=["SRC-PARCS-001", "SRC-USGS-001"],
            confidence_score=0.88,
            seasons=["all"],
            parameters={
                "home_range_male_km2": 100,
                "home_range_female_km2": 25,
                "daily_distance_km": 8
            }
        )
        
        self._behavior_rules["BEAR-AVOID-001"] = BehaviorRule(
            rule_id="BEAR-AVOID-001",
            behavior_type=BehaviorType.AVOIDANCE,
            description="L'ours évite généralement les humains mais peut s'habituer aux sources de nourriture anthropiques.",
            source_ids=["SRC-MFFP-001", "SRC-PARCS-001"],
            confidence_score=0.85,
            seasons=["all"],
            parameters={
                "human_avoidance_distance_m": 200,
                "habituation_risk": "medium"
            }
        )
        
        # Patterns d'activité - Plus actif matin et soir
        for hour in range(24):
            if hour in [6, 7, 8, 17, 18, 19]:
                level = 0.85
            elif hour in [5, 9, 10, 16, 20]:
                level = 0.60
            elif 11 <= hour <= 15:
                level = 0.35
            else:
                level = 0.20
            
            self._activity_patterns[hour] = ActivityPattern(
                hour=hour,
                activity_level=level,
                source_ids=["SRC-MFFP-001", "SRC-PARCS-001"],
                confidence=0.85
            )
        
        # Préférences d'habitat
        self._habitat_preferences["dense_forest"] = HabitatPreference(
            habitat_type="dense_forest",
            preference_score=0.90,
            source_ids=["SRC-MFFP-001"],
            confidence=0.90
        )
        
        self._habitat_preferences["berry_patches"] = HabitatPreference(
            habitat_type="berry_patches",
            preference_score=0.95,
            source_ids=["SRC-MFFP-001", "SRC-PARCS-001"],
            confidence=0.92,
            seasonal_variation={"summer": 0.98, "fall": 0.95}
        )
        
        self._habitat_preferences["wetland"] = HabitatPreference(
            habitat_type="wetland",
            preference_score=0.70,
            source_ids=["SRC-PARCS-001"],
            confidence=0.80
        )
    
    def get_activity_level(self, hour: int, season: str = "default") -> Tuple[float, List[str]]:
        pattern = self._activity_patterns.get(hour % 24)
        if not pattern:
            return (0.5, [])
        
        base_level = pattern.activity_level
        
        # Hyperphagie: activité augmentée
        if season == "fall":
            base_level = min(1.0, base_level * 1.3)
        
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


__all__ = ['BearRules']
