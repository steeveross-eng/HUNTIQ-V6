"""
BIONIC Compliance Engine (BCE)
Module de validation structurelle pour BIONIC.

VERSION: 8.0.0 — BCE Ruleset complet + Auto-Run
"""

from .bce_ruleset_v8 import (
    bce_autorun_engine,
    validate_territory_load,
    BCEReport,
    ValidationStatus,
    RuleCategory,
)

__all__ = [
    'bce_autorun_engine',
    'validate_territory_load',
    'BCEReport',
    'ValidationStatus',
    'RuleCategory',
]
