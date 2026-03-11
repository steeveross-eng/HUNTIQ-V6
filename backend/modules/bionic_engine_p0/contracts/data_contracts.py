"""
BIONIC ENGINE - Data Contracts
PHASE G - BIONIC ULTIMATE INTEGRATION
Version: 1.0.0-alpha

Modeles de donnees et contrats pour les modules P0.
Strictement conformes aux contrats JSON officiels.

Conformite: G-SEC | G-QA | G-DOC
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator, ConfigDict


# =============================================================================
# ENUMS - Types enumeres conformes aux contrats
# =============================================================================

class Species(str, Enum):
    """Especes supportees par le moteur BIONIC"""
    MOOSE = "moose"
    DEER = "deer"
    BEAR = "bear"
    WILD_TURKEY = "wild_turkey"
    ELK = "elk"


class ActivityLevel(str, Enum):
    """Niveaux d'activite"""
    VERY_HIGH = "very_high"
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    MINIMAL = "minimal"


class ScoreRating(str, Enum):
    """Classifications de score"""
    EXCEPTIONAL = "exceptional"
    EXCELLENT = "excellent"
    GOOD = "good"
    MODERATE = "moderate"
    LOW = "low"
    POOR = "poor"


class BehaviorType(str, Enum):
    """Types de comportement"""
    FEEDING = "feeding"
    TRAVELING = "traveling"
    RESTING = "resting"
    RUTTING = "rutting"
    BEDDING = "bedding"
    WATERING = "watering"
    UNKNOWN = "unknown"


class SeasonPhase(str, Enum):
    """Phases saisonnieres"""
    PRE_RUT = "pre_rut"
    RUT = "rut"
    POST_RUT = "post_rut"
    WINTER = "winter"
    SPRING = "spring"
    SUMMER = "summer"
    EARLY_FALL = "early_fall"


class HierarchyLevel(int, Enum):
    """Niveaux hierarchiques des facteurs (1 = plus prioritaire)"""
    CRITICAL = 1
    PRIMARY = 2
    SECONDARY = 3
    VALIDATION = 4


# =============================================================================
# INPUT MODELS - Modeles d'entree
# =============================================================================

class LocationInput(BaseModel):
    """
    Coordonnees geographiques.
    
    G-SEC: Validation stricte des plages Quebec
    """
    latitude: float = Field(..., ge=45.0, le=62.0, description="Latitude WGS84")
    longitude: float = Field(..., ge=-80.0, le=-57.0, description="Longitude WGS84")
    
    @field_validator('latitude')
    @classmethod
    def validate_latitude(cls, v):
        if not (45.0 <= v <= 62.0):
            raise ValueError("Latitude must be within Quebec bounds (45.0-62.0)")
        return v
    
    @field_validator('longitude')
    @classmethod
    def validate_longitude(cls, v):
        if not (-80.0 <= v <= -57.0):
            raise ValueError("Longitude must be within Quebec bounds (-80.0 to -57.0)")
        return v


class WeatherOverride(BaseModel):
    """Donnees meteo manuelles"""
    temperature: Optional[float] = Field(None, ge=-50, le=50, description="Temperature Celsius")
    wind_speed: Optional[float] = Field(None, ge=0, le=150, description="Vitesse vent km/h")
    pressure: Optional[float] = Field(None, ge=900, le=1100, description="Pression hPa")
    precipitation: Optional[float] = Field(None, ge=0, le=100, description="Precipitation mm/h")
    pressure_trend: Optional[str] = Field(None, description="rising|falling|stable")


class TerritorialScoreInput(BaseModel):
    """
    Input pour calcul de score territorial.
    
    Conforme a: predictive_territorial_contract.json
    P0-BETA2: Support des 12 facteurs comportementaux avances
    """
    model_config = ConfigDict(populate_by_name=True)
    
    latitude: float = Field(..., ge=45.0, le=62.0)
    longitude: float = Field(..., ge=-80.0, le=-57.0)
    species: Species = Field(default=Species.MOOSE)
    datetime_target: Optional[datetime] = Field(default=None, alias="datetime")
    radius_km: float = Field(default=5.0, ge=0.5, le=25.0)
    weather_override: Optional[WeatherOverride] = None
    historical_mode: bool = Field(default=False)
    include_recommendations: bool = Field(default=True)
    include_zones: bool = Field(default=False)
    # P0-BETA2: 12 facteurs comportementaux avances
    include_advanced_factors: bool = Field(default=True, description="Inclure les 12 facteurs comportementaux avances")
    snow_depth_cm: float = Field(default=0, ge=0, le=300, description="Profondeur de neige en cm")
    is_crusted: bool = Field(default=False, description="Presence de croute de glace sur la neige")


class BehavioralPredictionInput(BaseModel):
    """
    Input pour prediction comportementale.
    
    Conforme a: behavioral_models_contract.json
    P0-BETA2: Support des 12 facteurs comportementaux avances
    """
    model_config = ConfigDict(populate_by_name=True)
    
    species: Species
    datetime_target: Optional[datetime] = Field(default=None, alias="datetime")
    latitude: Optional[float] = Field(None, ge=45.0, le=62.0)
    longitude: Optional[float] = Field(None, ge=-80.0, le=-57.0)
    weather_context: Optional[WeatherOverride] = None
    habitat_type: Optional[str] = None
    canopy_cover: Optional[float] = Field(None, ge=0, le=100)
    include_zones: bool = Field(default=False)
    include_strategy: bool = Field(default=True)
    # P0-BETA2: 12 facteurs comportementaux avances
    include_advanced_factors: bool = Field(default=True, description="Inclure les 12 facteurs comportementaux avances")
    snow_depth_cm: float = Field(default=0, ge=0, le=300, description="Profondeur de neige en cm")
    is_crusted: bool = Field(default=False, description="Presence de croute de glace sur la neige")


# =============================================================================
# OUTPUT MODELS - Modeles de sortie
# =============================================================================

class ScoreComponents(BaseModel):
    """Composantes detaillees du score"""
    habitat_score: float = Field(..., ge=0, le=100)
    weather_score: float = Field(..., ge=0, le=100)
    temporal_score: float = Field(..., ge=0, le=100)
    pressure_score: float = Field(..., ge=0, le=100)
    microclimate_score: float = Field(..., ge=0, le=100)
    historical_score: float = Field(..., ge=0, le=100)


class Recommendation(BaseModel):
    """Recommandation pour le chasseur"""
    type: str = Field(..., description="position|timing|equipment|strategy")
    priority: str = Field(..., description="critical|high|medium|low")
    message_fr: str
    message_en: Optional[str] = None


class TerritorialScoreOutput(BaseModel):
    """
    Output du calcul de score territorial.
    
    Conforme a: predictive_territorial_contract.json
    """
    success: bool = True
    overall_score: float = Field(..., ge=0, le=100)
    confidence: float = Field(..., ge=0, le=1)
    rating: ScoreRating
    components: ScoreComponents
    recommendations: List[Recommendation] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ActivityPrediction(BaseModel):
    """Prediction d'activite"""
    current_behavior: BehaviorType
    behavior_confidence: float = Field(..., ge=0, le=1)
    activity_level: ActivityLevel
    activity_score: float = Field(..., ge=0, le=100)
    behavior_probabilities: Dict[str, float]


class TimelineEntry(BaseModel):
    """Entree de la timeline 24h"""
    hour: int = Field(..., ge=0, le=23)
    activity_score: float = Field(..., ge=0, le=100)
    primary_behavior: BehaviorType
    probability: float = Field(..., ge=0, le=1)
    is_legal_hunting: bool


class SeasonalContext(BaseModel):
    """Contexte saisonnier"""
    current_season: SeasonPhase
    activity_modifier: float
    primary_behaviors: List[str]
    key_events: List[str]


class StrategyRecommendation(BaseModel):
    """Recommandation de strategie"""
    strategy_type: str
    effectiveness_score: float = Field(..., ge=0, le=100)
    best_conditions: str
    tips_fr: List[str]


class BehavioralPredictionOutput(BaseModel):
    """
    Output de la prediction comportementale.
    
    Conforme a: behavioral_models_contract.json
    """
    success: bool = True
    activity: ActivityPrediction
    timeline: List[TimelineEntry] = Field(default_factory=list)
    seasonal_context: SeasonalContext
    strategies: List[StrategyRecommendation] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# WEIGHT CONFIGURATIONS - Configurations des poids (Inventaire v1.2)
# =============================================================================

class WeightConfig(BaseModel):
    """Configuration des poids pour un module"""
    base: Dict[str, float]
    constraints: Dict[str, float]
    arbitrage: Dict[str, Any]


# Configuration officielle PT (predictive_territorial)
PT_WEIGHTS_CONFIG = WeightConfig(
    base={
        "habitat_quality": 0.25,
        "weather_conditions": 0.20,
        "temporal_alignment": 0.20,
        "pressure_index": 0.15,
        "microclimate": 0.10,
        "historical_baseline": 0.10
    },
    constraints={
        "min_weight": 0.05,
        "max_weight": 0.40,
        "sum_tolerance": 0.01
    },
    arbitrage={
        "extreme_weather_threshold": {"temp_min": -30, "temp_max": 32, "wind_max": 60},
        "high_pressure_threshold": 80,
        "rut_boost_factor": 1.5
    }
)

# Configuration officielle BM (behavioral_models)
BM_WEIGHTS_CONFIG = WeightConfig(
    base={
        "temporal_pattern": 0.30,
        "habitat_suitability": 0.25,
        "weather_influence": 0.20,
        "pressure_influence": 0.15,
        "camera_validation": 0.10
    },
    constraints={
        "min_weight": 0.05,
        "max_weight": 0.45,
        "sum_tolerance": 0.01
    },
    arbitrage={
        "rut_temporal_boost": 1.33,
        "extreme_weather_boost": 1.75,
        "high_pressure_boost": 1.67,
        "hibernation_zero": ["bear"]
    }
)


# =============================================================================
# UTILITY FUNCTIONS - Fonctions utilitaires
# =============================================================================

def normalize_weights(
    weights: Dict[str, float], 
    available_sources: List[str],
    min_weight: float = 0.05,
    max_weight: float = 0.40
) -> Dict[str, float]:
    """
    Normalise les poids selon les sources disponibles.
    
    Conforme a: Inventaire v1.2 - Normalisation des ponderations
    
    Args:
        weights: Poids de base
        available_sources: Sources disponibles
        min_weight: Poids minimum
        max_weight: Poids maximum
        
    Returns:
        Dict poids normalises
    """
    # Filtrer sources indisponibles
    active_weights = {k: v for k, v in weights.items() if k in available_sources}
    
    if not active_weights:
        return weights  # Fallback
    
    # Redistribuer
    total = sum(active_weights.values())
    if total == 0:
        return weights
    
    normalized = {k: v / total for k, v in active_weights.items()}
    
    # Appliquer contraintes
    for k, v in normalized.items():
        normalized[k] = max(min_weight, min(max_weight, v))
    
    # Re-normaliser
    total = sum(normalized.values())
    if total > 0:
        normalized = {k: v / total for k, v in normalized.items()}
    
    return normalized


def score_to_rating(score: float) -> ScoreRating:
    """
    Convertit un score numerique en rating.
    
    G-DOC: Seuils documentes
    """
    if score >= 85:
        return ScoreRating.EXCEPTIONAL
    elif score >= 70:
        return ScoreRating.EXCELLENT
    elif score >= 55:
        return ScoreRating.GOOD
    elif score >= 40:
        return ScoreRating.MODERATE
    elif score >= 25:
        return ScoreRating.LOW
    else:
        return ScoreRating.POOR


def score_to_activity_level(score: float) -> ActivityLevel:
    """
    Convertit un score en niveau d'activite.
    
    G-DOC: Seuils documentes
    """
    if score >= 80:
        return ActivityLevel.VERY_HIGH
    elif score >= 60:
        return ActivityLevel.HIGH
    elif score >= 40:
        return ActivityLevel.MODERATE
    elif score >= 20:
        return ActivityLevel.LOW
    else:
        return ActivityLevel.MINIMAL
