"""
BIONIC V5 — CALIBRATION MODULE (NIVEAU 6 + MASTER)
====================================================
Module de mesure, calibration et figeage du modèle.

NIVEAU 6 — Mesure & Figeage:
- Tests prédictifs (concordance spatiale, temporelle, comportementale)
- Calibration (pondérations, modificateurs, seuils)
- Versionnage maître (BIONIC V5 MASTER)

PHASE F → MASTER — Calibration Optimizer:
- Comparaison prédiction vs observation
- Suggestions automatiques (validation manuelle obligatoire)
- Dashboard de calibration
- Verrouillage MASTER à 95%+

Conformité: G-SEC | G-QA | G-DOC | BIONIC V5 MASTER
"""

from .calibration_models import (
    # Enums
    TestType,
    CalibrationStatus,
    AccuracyLevel,
    # Data models
    PredictiveTest,
    PredictiveTestResult,
    CalibrationParameter,
    CalibrationProfile,
    ModelVersion,
    # Registry
    CalibrationRegistry,
    get_calibration_registry
)

from .mobility_prediction import (
    MobilityPrediction,
    MovementZone,
    TrajectoryPoint,
    MobilityPredictionService,
    get_mobility_prediction_service
)

from .calibration_optimizer import (
    # Enums
    AdjustmentType,
    AdjustmentStatus,
    PrecisionCategory,
    # Data models
    CalibrationSuggestion,
    ComparisonResult,
    CalibrationDashboardData,
    # Optimizer
    CalibrationOptimizer,
    get_calibration_optimizer
)

__all__ = [
    # Enums
    'TestType',
    'CalibrationStatus',
    'AccuracyLevel',
    'AdjustmentType',
    'AdjustmentStatus',
    'PrecisionCategory',
    # Data models
    'PredictiveTest',
    'PredictiveTestResult',
    'CalibrationParameter',
    'CalibrationProfile',
    'ModelVersion',
    'CalibrationSuggestion',
    'ComparisonResult',
    'CalibrationDashboardData',
    # Registry
    'CalibrationRegistry',
    'get_calibration_registry',
    # Mobility Prediction
    'MobilityPrediction',
    'MovementZone',
    'TrajectoryPoint',
    'MobilityPredictionService',
    'get_mobility_prediction_service',
    # Calibration Optimizer
    'CalibrationOptimizer',
    'get_calibration_optimizer'
]
