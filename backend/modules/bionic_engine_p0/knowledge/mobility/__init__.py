"""
BIONIC V5 — MOBILITY MODULE (NIVEAU 5)
======================================
Module de gestion de la mobilité dynamique.

NIVEAU 5 — Mobilité Dynamique:
Modèle de variance de mobilité liée aux contraintes digestives/thermiques.

PARAMÈTRES DE MOBILITÉ:
- Vitesse moyenne (km/h)
- Variance de vitesse
- Direction préférentielle
- Contraintes digestives
- Contraintes thermiques
- Modulation PRES-HUMAN

Conformité: G-SEC | G-QA | G-DOC | BIONIC V5 NIVEAU 5
"""

from .mobility_models import (
    # Enums
    MovementIntensity,
    MovementDirection,
    TerrainDifficulty,
    # Data models
    MobilityParameters,
    MobilityConstraint,
    MobilityState,
    MobilityPrediction,
    # Registry
    MobilityRegistry,
    get_mobility_registry
)

__all__ = [
    'MovementIntensity',
    'MovementDirection',
    'TerrainDifficulty',
    'MobilityParameters',
    'MobilityConstraint',
    'MobilityState',
    'MobilityPrediction',
    'MobilityRegistry',
    'get_mobility_registry'
]
