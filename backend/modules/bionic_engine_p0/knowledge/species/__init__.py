"""
BIONIC V5 — SPECIES RULES MODULE
=================================
PHASE 7 — Knowledge Layer
PHASE B — Facteurs Avancés

Module d'exportation des règles comportementales par espèce.
"""

from typing import Optional
from .base import (
    SpeciesRulesBase,
    BehaviorType,
    ActivityPeriod,
    BehaviorRule,
    ActivityPattern,
    HabitatPreference
)
from .moose_rules import MooseRules
from .deer_rules import DeerRules
from .mule_deer_rules import MuleDeerRules
from .bear_rules import BearRules
from .elk_rules import ElkRules

# PHASE B — Facteurs Avancés
from .advanced_factors import (
    SocialRank,
    CompetitionType,
    WeakSignalType,
    DigestivePhase,
    SocialHierarchyRule,
    InterspeciesCompetition,
    WeakSignal,
    DigestiveCycle,
    AdvancedFactorsRegistry,
    get_advanced_factors_registry
)


# Registre des espèces disponibles
_SPECIES_REGISTRY = {
    "moose": MooseRules,
    "orignal": MooseRules,
    "deer": DeerRules,
    "white-tailed deer": DeerRules,
    "cerf de virginie": DeerRules,
    "mule_deer": MuleDeerRules,
    "cerf-mulet": MuleDeerRules,
    "bear": BearRules,
    "black bear": BearRules,
    "ours noir": BearRules,
    "elk": ElkRules,
    "wapiti": ElkRules
}

# Cache des instances
_species_instances = {}


def get_species_rules(species: str) -> Optional[SpeciesRulesBase]:
    """
    Obtenir les règles comportementales pour une espèce.
    
    Args:
        species: Nom de l'espèce (FR ou EN, case insensitive)
        
    Returns:
        Instance de SpeciesRulesBase ou None si non trouvée
    """
    species_lower = species.lower().strip()
    
    # Vérifier le cache
    if species_lower in _species_instances:
        return _species_instances[species_lower]
    
    # Chercher dans le registre
    species_class = _SPECIES_REGISTRY.get(species_lower)
    
    if species_class:
        instance = species_class()
        _species_instances[species_lower] = instance
        return instance
    
    return None


def get_available_species() -> list:
    """Obtenir la liste des espèces disponibles"""
    return list(set(cls().species_code for cls in set(_SPECIES_REGISTRY.values())))


__all__ = [
    # Base classes
    'SpeciesRulesBase',
    'BehaviorType',
    'ActivityPeriod',
    'BehaviorRule',
    'ActivityPattern',
    'HabitatPreference',
    # Species implementations
    'MooseRules',
    'DeerRules',
    'MuleDeerRules',
    'BearRules',
    'ElkRules',
    # Functions
    'get_species_rules',
    'get_available_species',
    # PHASE B — Advanced Factors
    'SocialRank',
    'CompetitionType',
    'WeakSignalType',
    'DigestivePhase',
    'SocialHierarchyRule',
    'InterspeciesCompetition',
    'WeakSignal',
    'DigestiveCycle',
    'AdvancedFactorsRegistry',
    'get_advanced_factors_registry'
]
