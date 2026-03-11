"""
BIONIC V5 — CORRIDORS MODULE (NIVEAU 4)
=======================================
Module de gestion des corridors de déplacement.

TYPES DE CORRIDORS:
- Principaux (primary)
- Secondaires (secondary)
- Saisonniers (seasonal)
- Thermiques (thermal)
- À risque (risk) - PRES-HUMAN + stress thermique

Conformité: G-SEC | G-QA | G-DOC | BIONIC V5 NIVEAU 4
"""

from .corridor_models import (
    # Enums
    CorridorType,
    CorridorPriority,
    CorridorQuality,
    # Data models
    CorridorStyle,
    CorridorSegment,
    Corridor,
    CorridorNetwork,
    # Registry
    CorridorRegistry,
    get_corridor_registry
)

__all__ = [
    'CorridorType',
    'CorridorPriority',
    'CorridorQuality',
    'CorridorStyle',
    'CorridorSegment',
    'Corridor',
    'CorridorNetwork',
    'CorridorRegistry',
    'get_corridor_registry'
]
