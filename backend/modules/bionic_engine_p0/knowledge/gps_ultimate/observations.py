"""
BIONIC V5 — OBSERVATIONS MODULE (PHASE F)
==========================================
Re-export pour compatibilité avec l'ancien __init__.py.

VERSION: 7.0.0
"""

# Re-export depuis observations_models pour compatibilité
from .observations_models import (
    ObservedSpecies as ObservationType,
    FieldObservation as TerrainObservation,
    ObservationRegistry as ObservationsRegistry,
    get_observation_registry as get_observations_registry
)

# Créer un alias pour ObservationResult
class ObservationResult:
    """Alias pour compatibilité."""
    def __init__(self, observation: TerrainObservation):
        self.observation = observation
        self.success = True

__all__ = [
    'ObservationType',
    'TerrainObservation',
    'ObservationResult',
    'ObservationsRegistry',
    'get_observations_registry'
]
