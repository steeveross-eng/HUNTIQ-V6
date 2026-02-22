"""
BIONIC ENGINE — Scoring Services Package
=========================================
Architecture des 9 scores canoniques BIONIC V5 ULTIME.

SCORES:
1. ScoreProbabilityService  - Probabilité de succès de chasse
2. ScoreHabitatService      - Qualité et pertinence de l'habitat
3. ScorePressureService     - Pression de chasse et humaine
4. ScoreWeatherService      - Impact des conditions météorologiques
5. ScoreBehaviorService     - Comportement et patterns animaux
6. ScoreMultiFactorService  - Combinaison de facteurs multiples
7. ScoreDensityService      - Densité de population animale
8. ScoreRiskService         - Risques et facteurs de danger
9. ScoreMobilityService     - Mobilité et mouvements

ISOLATION:
- Chaque score = module isolé
- Aucun import transversal
- Interface commune via BaseScoreService

Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
"""

from .base_score_service import (
    BaseScoreService,
    ScoreResult,
    ScoreComponent,
    ScoreLevel,
    ScoreContext,
    ScoreWeight,
    ScoreCategory
)

from .score_probability_service import ScoreProbabilityService
from .score_habitat_service import ScoreHabitatService
from .score_pressure_service import ScorePressureService
from .score_weather_service import ScoreWeatherService
from .score_behavior_service import ScoreBehaviorService
from .score_multifactor_service import ScoreMultiFactorService
from .score_density_service import ScoreDensityService
from .score_risk_service import ScoreRiskService
from .score_mobility_service import ScoreMobilityService

__all__ = [
    # Base
    'BaseScoreService',
    'ScoreResult',
    'ScoreComponent',
    'ScoreLevel',
    'ScoreContext',
    'ScoreWeight',
    'ScoreCategory',
    # Services (9 scores)
    'ScoreProbabilityService',
    'ScoreHabitatService',
    'ScorePressureService',
    'ScoreWeatherService',
    'ScoreBehaviorService',
    'ScoreMultiFactorService',
    'ScoreDensityService',
    'ScoreRiskService',
    'ScoreMobilityService'
]
