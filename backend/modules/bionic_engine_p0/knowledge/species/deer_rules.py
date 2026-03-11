"""
BIONIC V5 — WHITE-TAILED DEER BEHAVIOR RULES
=============================================
PHASE 7 — Knowledge Layer

Règles comportementales pour le cerf de Virginie (Odocoileus virginianus).
Toutes les règles sont traçables à des sources scientifiques.

SOURCES PRINCIPALES:
- SRC-MFFP-001: MFFP Québec
- SRC-NDA-001: National Deer Association
- SRC-WHS-001: Whitetail Habitat Solutions
- SRC-UMAINE-001: University of Maine

VERSION: 1.0.0
Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
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


class DeerRules(SpeciesRulesBase):
    """
    Règles comportementales pour le cerf de Virginie (Odocoileus virginianus).
    
    Le cerf de Virginie est le cervidé le plus répandu en Amérique du Nord.
    Son comportement est fortement influencé par le cycle du rut (novembre)
    et la pression de chasse.
    """
    
    def __init__(self):
        super().__init__()
        self.species_code = "deer"
        self.species_name_fr = "Cerf de Virginie"
        self.species_name_en = "White-tailed Deer"
        self.scientific_name = "Odocoileus virginianus"
    
    def _initialize_rules(self):
        """Initialiser les règles comportementales du cerf"""
        
        # =====================================================
        # RÈGLES DE COMPORTEMENT
        # =====================================================
        
        # Alimentation
        self._behavior_rules["DEER-FEED-001"] = BehaviorRule(
            rule_id="DEER-FEED-001",
            behavior_type=BehaviorType.FEEDING,
            description="Le cerf se nourrit principalement à l'aube et au crépuscule dans les zones de lisière.",
            source_ids=["SRC-NDA-001", "SRC-WHS-001"],
            confidence_score=0.93,
            seasons=["all"],
            time_periods=[ActivityPeriod.DAWN, ActivityPeriod.DUSK],
            parameters={
                "peak_hours": [6, 17, 18],
                "edge_preference_m": 100,
                "browse_height_m": 1.5
            }
        )
        
        self._behavior_rules["DEER-FEED-002"] = BehaviorRule(
            rule_id="DEER-FEED-002",
            behavior_type=BehaviorType.FEEDING,
            description="En automne, le cerf augmente sa consommation de glands et noix pour constituer des réserves.",
            source_ids=["SRC-NDA-001", "SRC-MFFP-001"],
            confidence_score=0.90,
            seasons=["fall", "pre_rut"],
            parameters={
                "acorn_preference": 0.95,
                "feeding_intensity_multiplier": 1.4
            }
        )
        
        # Repos
        self._behavior_rules["DEER-BED-001"] = BehaviorRule(
            rule_id="DEER-BED-001",
            behavior_type=BehaviorType.BEDDING,
            description="Le cerf se couche dans des zones de couvert dense avec une vue dégagée sur les approches.",
            source_ids=["SRC-WHS-001", "SRC-NDA-001"],
            confidence_score=0.88,
            seasons=["all"],
            time_periods=[ActivityPeriod.MIDDAY],
            parameters={
                "min_cover_density_percent": 70,
                "preferred_slope_degrees": 3,
                "visibility_requirement_m": 30,
                "escape_routes_min": 2
            }
        )
        
        # Mouvement
        self._behavior_rules["DEER-MOV-001"] = BehaviorRule(
            rule_id="DEER-MOV-001",
            behavior_type=BehaviorType.MOVEMENT,
            description="Le cerf utilise des sentiers établis entre ses zones de repos et d'alimentation.",
            source_ids=["SRC-NDA-001", "SRC-UMAINE-001"],
            confidence_score=0.91,
            seasons=["all"],
            parameters={
                "average_daily_distance_km": 3.0,
                "home_range_km2": 2.5,
                "trail_fidelity": 0.85
            }
        )
        
        # Rut - Pré-rut
        self._behavior_rules["DEER-RUT-001"] = BehaviorRule(
            rule_id="DEER-RUT-001",
            behavior_type=BehaviorType.RUT,
            description="Pendant le pré-rut (fin octobre), les mâles créent des grattages (scrapes) et frottoirs (rubs).",
            source_ids=["SRC-NDA-001", "SRC-WHS-001", "SRC-THP-001"],
            confidence_score=0.94,
            seasons=["pre_rut"],
            parameters={
                "pre_rut_start_date": "10-20",
                "pre_rut_end_date": "11-05",
                "scrape_activity": "high",
                "rub_activity": "very_high",
                "movement_multiplier": 1.5
            }
        )
        
        # Rut - Pic
        self._behavior_rules["DEER-RUT-002"] = BehaviorRule(
            rule_id="DEER-RUT-002",
            behavior_type=BehaviorType.RUT,
            description="Pendant le pic du rut (novembre), les mâles parcourent de grandes distances à la recherche de femelles.",
            source_ids=["SRC-NDA-001", "SRC-MFFP-001", "SRC-WHS-001"],
            confidence_score=0.96,
            seasons=["rut"],
            parameters={
                "rut_peak_start_date": "11-05",
                "rut_peak_end_date": "11-20",
                "movement_multiplier": 3.0,
                "activity_multiplier": 2.0,
                "daylight_activity_increase": 0.50
            }
        )
        
        # Rut - Post-rut
        self._behavior_rules["DEER-RUT-003"] = BehaviorRule(
            rule_id="DEER-RUT-003",
            behavior_type=BehaviorType.RUT,
            description="Pendant le post-rut, les mâles sont épuisés et cherchent à récupérer.",
            source_ids=["SRC-NDA-001"],
            confidence_score=0.88,
            seasons=["post_rut"],
            parameters={
                "post_rut_start_date": "11-20",
                "post_rut_end_date": "12-10",
                "activity_multiplier": 0.7,
                "feeding_priority": "very_high"
            }
        )
        
        # Pression de chasse
        self._behavior_rules["DEER-AVOID-001"] = BehaviorRule(
            rule_id="DEER-AVOID-001",
            behavior_type=BehaviorType.AVOIDANCE,
            description="Le cerf devient nocturne sous forte pression de chasse.",
            source_ids=["SRC-NDA-001", "SRC-UMAINE-001", "SRC-STATE-001"],
            confidence_score=0.92,
            seasons=["hunting_season"],
            parameters={
                "nocturnal_shift_factor": 0.60,
                "cover_seeking_increase": 0.40,
                "road_avoidance_distance_m": 200,
                "human_scent_avoidance_m": 150
            }
        )
        
        # =====================================================
        # PATTERNS D'ACTIVITÉ HORAIRE
        # =====================================================
        
        hourly_patterns = {
            0: (0.15, ["SRC-NDA-001"]),
            1: (0.10, ["SRC-NDA-001"]),
            2: (0.10, ["SRC-NDA-001"]),
            3: (0.15, ["SRC-NDA-001"]),
            4: (0.40, ["SRC-NDA-001", "SRC-WHS-001"]),
            5: (0.85, ["SRC-NDA-001", "SRC-WHS-001"]),
            6: (0.95, ["SRC-NDA-001", "SRC-WHS-001"]),
            7: (0.80, ["SRC-NDA-001"]),
            8: (0.50, ["SRC-NDA-001"]),
            9: (0.30, ["SRC-NDA-001"]),
            10: (0.20, ["SRC-NDA-001"]),
            11: (0.15, ["SRC-NDA-001"]),
            12: (0.15, ["SRC-NDA-001"]),
            13: (0.20, ["SRC-NDA-001"]),
            14: (0.25, ["SRC-NDA-001"]),
            15: (0.35, ["SRC-NDA-001"]),
            16: (0.60, ["SRC-NDA-001", "SRC-WHS-001"]),
            17: (0.85, ["SRC-NDA-001", "SRC-WHS-001"]),
            18: (0.95, ["SRC-NDA-001", "SRC-WHS-001"]),
            19: (0.75, ["SRC-NDA-001"]),
            20: (0.50, ["SRC-NDA-001"]),
            21: (0.35, ["SRC-NDA-001"]),
            22: (0.25, ["SRC-NDA-001"]),
            23: (0.20, ["SRC-NDA-001"])
        }
        
        for hour, (level, sources) in hourly_patterns.items():
            self._activity_patterns[hour] = ActivityPattern(
                hour=hour,
                activity_level=level,
                source_ids=sources,
                confidence=0.88
            )
        
        # =====================================================
        # PRÉFÉRENCES D'HABITAT
        # =====================================================
        
        self._habitat_preferences["hardwood_forest"] = HabitatPreference(
            habitat_type="hardwood_forest",
            preference_score=0.90,
            source_ids=["SRC-NDA-001", "SRC-WHS-001"],
            confidence=0.92,
            seasonal_variation={"fall": 0.95, "summer": 0.85, "winter": 0.80}
        )
        
        self._habitat_preferences["edge_habitat"] = HabitatPreference(
            habitat_type="edge_habitat",
            preference_score=0.95,
            source_ids=["SRC-NDA-001", "SRC-WHS-001"],
            confidence=0.95,
            seasonal_variation={"all": 0.95}
        )
        
        self._habitat_preferences["agricultural_edge"] = HabitatPreference(
            habitat_type="agricultural_edge",
            preference_score=0.88,
            source_ids=["SRC-NDA-001"],
            confidence=0.90,
            seasonal_variation={"fall": 0.95, "summer": 0.90, "winter": 0.70}
        )
        
        self._habitat_preferences["dense_cover"] = HabitatPreference(
            habitat_type="dense_cover",
            preference_score=0.85,
            source_ids=["SRC-WHS-001", "SRC-NDA-001"],
            confidence=0.88,
            seasonal_variation={"hunting_season": 0.98, "winter": 0.90}
        )
    
    def get_activity_level(self, hour: int, season: str = "default") -> Tuple[float, List[str]]:
        """Obtenir le niveau d'activité pour une heure donnée"""
        hour = hour % 24
        pattern = self._activity_patterns.get(hour)
        
        if not pattern:
            return (0.5, [])
        
        base_level = pattern.activity_level
        
        if season == "rut":
            # Pic du rut: activité diurne augmentée
            if 8 <= hour <= 16:
                base_level = min(1.0, base_level + 0.40)
            sources = pattern.source_ids + ["SRC-NDA-001"]
        elif season == "hunting_season":
            # Pression de chasse: shift nocturne
            if 7 <= hour <= 17:
                base_level *= 0.60
            else:
                base_level = min(1.0, base_level * 1.3)
            sources = pattern.source_ids
        else:
            sources = pattern.source_ids
        
        return (round(base_level, 2), sources)
    
    def get_habitat_score(self, habitat_type: str, season: str = "default") -> Tuple[float, List[str]]:
        """Obtenir le score de préférence pour un type d'habitat"""
        pref = self._habitat_preferences.get(habitat_type)
        
        if not pref:
            return (0.5, [])
        
        if season in pref.seasonal_variation:
            score = pref.seasonal_variation[season]
        else:
            score = pref.preference_score
        
        return (round(score, 2), pref.source_ids)


__all__ = ['DeerRules']
