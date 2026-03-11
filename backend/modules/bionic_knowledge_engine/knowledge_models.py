"""
BIONIC Knowledge Models - V5-ULTIME
===================================

Modèles Pydantic pour le Knowledge Layer.
Définition des structures de données pour:
- Espèces et comportements
- Règles empiriques
- Variables d'habitat
- Modèles saisonniers
- Sources de connaissances

Module isolé - aucun import croisé.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============================================
# ENUMS
# ============================================

class SpeciesCategory(str, Enum):
    CERVIDAE = "cervidae"  # Cervidés (orignal, cerf, caribou)
    URSIDAE = "ursidae"    # Ursidés (ours)
    CANIDAE = "canidae"    # Canidés (loup, coyote)
    ANATIDAE = "anatidae"  # Anatidés (canards, oies)
    TETRAONIDAE = "tetraonidae"  # Tétraonidés (gélinotte, tétras)
    LEPORIDAE = "leporidae"  # Léporidés (lièvre)
    OTHER = "other"


class SeasonType(str, Enum):
    RUT = "rut"
    PRE_RUT = "pre_rut"
    POST_RUT = "post_rut"
    WINTER = "winter"
    SPRING = "spring"
    SUMMER = "summer"
    FALL = "fall"
    MIGRATION = "migration"


class ActivityPeriod(str, Enum):
    DAWN = "dawn"
    MORNING = "morning"
    MIDDAY = "midday"
    AFTERNOON = "afternoon"
    DUSK = "dusk"
    NIGHT = "night"
    CREPUSCULAR = "crepuscular"
    DIURNAL = "diurnal"
    NOCTURNAL = "nocturnal"


class HabitatType(str, Enum):
    CONIFEROUS_FOREST = "coniferous_forest"
    DECIDUOUS_FOREST = "deciduous_forest"
    MIXED_FOREST = "mixed_forest"
    WETLAND = "wetland"
    BOG = "bog"
    MARSH = "marsh"
    LAKE_SHORE = "lake_shore"
    RIVER_CORRIDOR = "river_corridor"
    RIDGE = "ridge"
    VALLEY = "valley"
    CLEARCUT = "clearcut"
    REGENERATION = "regeneration"
    AGRICULTURAL = "agricultural"
    ALPINE = "alpine"
    TUNDRA = "tundra"


class RuleConfidence(str, Enum):
    SCIENTIFIC = "scientific"      # Basé sur études scientifiques
    EMPIRICAL = "empirical"        # Basé sur observations terrain
    THEORETICAL = "theoretical"    # Basé sur théorie
    HYBRID = "hybrid"              # Combinaison


class SourceType(str, Enum):
    SCIENTIFIC_PAPER = "scientific_paper"
    GOVERNMENT_REPORT = "government_report"
    EXPERT_INTERVIEW = "expert_interview"
    FIELD_OBSERVATION = "field_observation"
    TRADITIONAL_KNOWLEDGE = "traditional_knowledge"
    USER_REPORT = "user_report"
    SENSOR_DATA = "sensor_data"
    AI_GENERATED = "ai_generated"


# ============================================
# CORE MODELS
# ============================================

class TemperatureRange(BaseModel):
    """Plage de température pour une espèce"""
    optimal_min: float = Field(..., description="Température minimale optimale (°C)")
    optimal_max: float = Field(..., description="Température maximale optimale (°C)")
    tolerance_min: float = Field(..., description="Température minimale tolérée (°C)")
    tolerance_max: float = Field(..., description="Température maximale tolérée (°C)")
    activity_threshold: float = Field(default=0.0, description="Seuil d'activité réduite (°C)")


class ActivityPattern(BaseModel):
    """Pattern d'activité pour une période"""
    period: ActivityPeriod
    activity_level: float = Field(..., ge=0, le=1, description="Niveau d'activité (0-1)")
    feeding_probability: float = Field(default=0.5, ge=0, le=1)
    movement_probability: float = Field(default=0.5, ge=0, le=1)
    notes: Optional[str] = None


class SeasonalBehavior(BaseModel):
    """Comportement saisonnier"""
    season: SeasonType
    start_month: int = Field(..., ge=1, le=12)
    end_month: int = Field(..., ge=1, le=12)
    peak_month: Optional[int] = Field(None, ge=1, le=12)
    activity_modifier: float = Field(default=1.0, ge=0, le=2)
    habitat_preference: List[HabitatType] = []
    food_sources: List[str] = []
    behavior_notes: Optional[str] = None


class HabitatPreference(BaseModel):
    """Préférence d'habitat"""
    habitat_type: HabitatType
    preference_score: float = Field(..., ge=0, le=1, description="Score de préférence (0-1)")
    seasonal_variation: Dict[str, float] = Field(default_factory=dict)
    notes: Optional[str] = None


class FoodSource(BaseModel):
    """Source alimentaire"""
    name: str
    name_fr: str
    category: str  # browse, graze, mast, protein
    availability_months: List[int] = []
    preference_score: float = Field(default=0.5, ge=0, le=1)
    nutritional_value: float = Field(default=0.5, ge=0, le=1)


# ============================================
# MAIN KNOWLEDGE MODELS
# ============================================

class SpeciesKnowledge(BaseModel):
    """Connaissances complètes sur une espèce"""
    id: str
    scientific_name: str
    common_name_fr: str
    common_name_en: str
    category: SpeciesCategory
    
    # Caractéristiques physiques
    weight_range_kg: Dict[str, float] = Field(default_factory=dict)  # male_min, male_max, female_min, female_max
    home_range_km2: Dict[str, float] = Field(default_factory=dict)  # male, female, seasonal
    
    # Préférences environnementales
    temperature_range: TemperatureRange
    elevation_range_m: Dict[str, float] = Field(default_factory=dict)  # min, max, optimal
    humidity_preference: Dict[str, float] = Field(default_factory=dict)  # min, max, optimal
    
    # Comportement
    activity_patterns: List[ActivityPattern] = []
    seasonal_behaviors: List[SeasonalBehavior] = []
    habitat_preferences: List[HabitatPreference] = []
    food_sources: List[FoodSource] = []
    
    # Réponse à la pression
    human_tolerance: float = Field(default=0.3, ge=0, le=1)
    flight_distance_m: float = Field(default=100)
    road_avoidance_m: float = Field(default=200)
    
    # Reproduction
    breeding_season: Optional[SeasonalBehavior] = None
    gestation_days: Optional[int] = None
    
    # Métadonnées
    data_quality_score: float = Field(default=0.5, ge=0, le=1)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    sources: List[str] = []
    notes: Optional[str] = None


class BehaviorRule(BaseModel):
    """Règle comportementale empirique"""
    id: str
    name: str
    name_fr: str
    description: str
    description_fr: str
    
    # Applicabilité
    species: List[str] = []  # IDs des espèces concernées
    seasons: List[SeasonType] = []
    habitats: List[HabitatType] = []
    
    # Conditions
    conditions: Dict[str, Any] = Field(default_factory=dict)
    # Ex: {"temperature": {"min": -5, "max": 10}, "wind_speed": {"max": 20}}
    
    # Effet
    effect_type: str  # activity_modifier, location_preference, timing_shift
    effect_value: float
    effect_description: str
    
    # Fiabilité
    confidence: RuleConfidence
    confidence_score: float = Field(default=0.5, ge=0, le=1)
    validation_count: int = Field(default=0)
    
    # Métadonnées
    source_ids: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    tags: List[str] = []


class HabitatVariable(BaseModel):
    """Variable d'habitat mesurable"""
    id: str
    name: str
    name_fr: str
    category: str  # terrain, vegetation, hydrology, climate, human_impact
    
    # Définition
    unit: str
    data_type: str  # float, int, category, boolean
    value_range: Dict[str, Any] = Field(default_factory=dict)
    
    # Sources de données
    data_sources: List[str] = []
    update_frequency: str  # realtime, daily, weekly, seasonal, static
    
    # Scoring
    scoring_method: str  # linear, exponential, categorical, custom
    scoring_params: Dict[str, Any] = Field(default_factory=dict)
    
    # Importance par espèce
    species_weights: Dict[str, float] = Field(default_factory=dict)
    
    # Métadonnées
    description: Optional[str] = None
    is_active: bool = True


class SeasonalModel(BaseModel):
    """Modèle saisonnier pour une espèce/région"""
    id: str
    species_id: str
    region: str  # quebec_south, quebec_north, etc.
    year: int
    
    # Phases saisonnières
    phases: List[Dict[str, Any]] = []
    # Ex: [{"name": "rut", "start": "2024-09-15", "peak": "2024-10-01", "end": "2024-10-20"}]
    
    # Modèles prédictifs
    temperature_sensitivity: float = Field(default=0.5)
    photoperiod_sensitivity: float = Field(default=0.7)
    
    # Ajustements
    regional_adjustments: Dict[str, float] = Field(default_factory=dict)
    elevation_adjustments: Dict[str, float] = Field(default_factory=dict)
    
    # Validation
    accuracy_score: float = Field(default=0.5, ge=0, le=1)
    validation_observations: int = Field(default=0)
    
    # Métadonnées
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class KnowledgeSource(BaseModel):
    """Source de connaissances"""
    id: str
    name: str
    source_type: SourceType
    
    # Référence
    reference: str  # DOI, URL, or description
    authors: List[str] = []
    publication_date: Optional[datetime] = None
    
    # Couverture
    species_covered: List[str] = []
    regions_covered: List[str] = []
    topics: List[str] = []
    
    # Fiabilité
    reliability_score: float = Field(default=0.5, ge=0, le=1)
    peer_reviewed: bool = False
    citation_count: int = Field(default=0)
    
    # Métadonnées
    added_at: datetime = Field(default_factory=datetime.utcnow)
    verified: bool = False
    notes: Optional[str] = None


# ============================================
# API RESPONSE MODELS
# ============================================

class KnowledgeStats(BaseModel):
    """Statistiques du Knowledge Layer"""
    total_species: int
    total_rules: int
    total_variables: int
    total_seasonal_models: int
    total_sources: int
    data_quality_avg: float
    last_update: datetime


class KnowledgeQueryResult(BaseModel):
    """Résultat de requête knowledge"""
    success: bool
    query_type: str
    results: List[Dict[str, Any]]
    count: int
    processing_time_ms: float


class ValidationResult(BaseModel):
    """Résultat de validation"""
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    suggestions: List[str] = []
