"""
BIONIC V5 — SPECIES RULES BASE
===============================
PHASE 7 — Knowledge Layer

Classe de base pour les règles comportementales par espèce.
Chaque règle DOIT être traçable à une source scientifique.

VERSION: 1.0.0
Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone


class BehaviorType(str, Enum):
    """Types de comportements"""
    FEEDING = "feeding"
    BEDDING = "bedding"
    MOVEMENT = "movement"
    RUT = "rut"
    TERRITORIAL = "territorial"
    AVOIDANCE = "avoidance"
    SOCIAL = "social"
    THERMAL = "thermal"


class ActivityPeriod(str, Enum):
    """Périodes d'activité"""
    DAWN = "dawn"           # 30 min avant lever - 1h après
    MORNING = "morning"     # 1h après lever - midi
    MIDDAY = "midday"       # 10h - 14h
    AFTERNOON = "afternoon" # 14h - 2h avant coucher
    DUSK = "dusk"           # 2h avant coucher - 30 min après
    NIGHT = "night"         # Nuit


@dataclass
class BehaviorRule:
    """
    Règle comportementale traçable.
    
    Chaque règle est liée à une ou plusieurs sources scientifiques
    via source_ids, garantissant la traçabilité complète.
    """
    rule_id: str
    behavior_type: BehaviorType
    description: str
    
    # Traçabilité
    source_ids: List[str] = field(default_factory=list)
    confidence_score: float = 0.5
    
    # Conditions d'application
    seasons: List[str] = field(default_factory=lambda: ["all"])
    time_periods: List[ActivityPeriod] = field(default_factory=list)
    
    # Paramètres
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Métadonnées
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ActivityPattern:
    """Pattern d'activité horaire sourcé"""
    hour: int
    activity_level: float  # 0.0 à 1.0
    source_ids: List[str] = field(default_factory=list)
    confidence: float = 0.5
    notes: str = ""


@dataclass 
class HabitatPreference:
    """Préférence d'habitat sourcée"""
    habitat_type: str
    preference_score: float  # 0.0 à 1.0
    source_ids: List[str] = field(default_factory=list)
    confidence: float = 0.5
    seasonal_variation: Dict[str, float] = field(default_factory=dict)


class SpeciesRulesBase(ABC):
    """
    Classe de base abstraite pour les règles comportementales par espèce.
    
    Chaque espèce DOIT implémenter cette classe avec des règles
    traçables à des sources scientifiques.
    """
    
    def __init__(self):
        self.species_code: str = ""
        self.species_name_fr: str = ""
        self.species_name_en: str = ""
        self.scientific_name: str = ""
        
        self._behavior_rules: Dict[str, BehaviorRule] = {}
        self._activity_patterns: Dict[int, ActivityPattern] = {}
        self._habitat_preferences: Dict[str, HabitatPreference] = {}
        
        self._initialize_rules()
    
    @abstractmethod
    def _initialize_rules(self):
        """Initialiser les règles - à implémenter par chaque espèce"""
        pass
    
    @abstractmethod
    def get_activity_level(self, hour: int, season: str) -> Tuple[float, List[str]]:
        """
        Obtenir le niveau d'activité pour une heure et saison.
        
        Returns:
            Tuple[float, List[str]]: (niveau d'activité, source_ids)
        """
        pass
    
    @abstractmethod
    def get_habitat_score(self, habitat_type: str, season: str) -> Tuple[float, List[str]]:
        """
        Obtenir le score de préférence pour un type d'habitat.
        
        Returns:
            Tuple[float, List[str]]: (score de préférence, source_ids)
        """
        pass
    
    def get_behavior_rule(self, rule_id: str) -> Optional[BehaviorRule]:
        """Obtenir une règle par ID"""
        return self._behavior_rules.get(rule_id)
    
    def get_rules_by_type(self, behavior_type: BehaviorType) -> List[BehaviorRule]:
        """Obtenir toutes les règles d'un type"""
        return [r for r in self._behavior_rules.values() if r.behavior_type == behavior_type]
    
    def get_all_rules(self) -> List[BehaviorRule]:
        """Obtenir toutes les règles"""
        return list(self._behavior_rules.values())
    
    def get_all_source_ids(self) -> List[str]:
        """Obtenir tous les IDs de sources utilisées"""
        source_ids = set()
        for rule in self._behavior_rules.values():
            source_ids.update(rule.source_ids)
        for pattern in self._activity_patterns.values():
            source_ids.update(pattern.source_ids)
        for pref in self._habitat_preferences.values():
            source_ids.update(pref.source_ids)
        return list(source_ids)
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques des règles"""
        return {
            "species": self.species_code,
            "total_rules": len(self._behavior_rules),
            "total_activity_patterns": len(self._activity_patterns),
            "total_habitat_preferences": len(self._habitat_preferences),
            "unique_sources": len(self.get_all_source_ids()),
            "average_confidence": self._calculate_average_confidence()
        }
    
    def _calculate_average_confidence(self) -> float:
        """Calculer la confiance moyenne"""
        confidences = [r.confidence_score for r in self._behavior_rules.values()]
        confidences.extend([p.confidence for p in self._activity_patterns.values()])
        confidences.extend([p.confidence for p in self._habitat_preferences.values()])
        return sum(confidences) / len(confidences) if confidences else 0.0


__all__ = [
    'BehaviorType',
    'ActivityPeriod',
    'BehaviorRule',
    'ActivityPattern',
    'HabitatPreference',
    'SpeciesRulesBase'
]
