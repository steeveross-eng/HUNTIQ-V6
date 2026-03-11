"""
BIONIC ENGINE — Base Score Service
===================================
Interface de base et data contracts pour tous les services de scoring.

ARCHITECTURE:
- Classe abstraite BaseScoreService définissant l'interface commune
- Data contracts partagés (ScoreResult, ScoreContext, etc.)
- Intégration Knowledge Layer pour pondérations calibrées

KNOWLEDGE LAYER INTEGRATION (PHASE 7):
- Toutes les pondérations proviennent du Knowledge Layer
- Traçabilité scientifique obligatoire
- Niveaux de confiance par variable

ISOLATION:
- Aucune dépendance aux autres services BIONIC
- Interface pure pour héritage
- Accès Knowledge Layer via points d'entrée unifiés uniquement

Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

# Knowledge Layer Integration
from modules.bionic_engine_p0.knowledge import (
    get_source_registry,
    get_species_rules,
    get_habitat_weights,
    get_seasonal_model
)

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS
# =============================================================================

class ScoreLevel(str, Enum):
    """Niveau qualitatif d'un score."""
    EXCELLENT = "excellent"     # 85-100
    GOOD = "good"              # 70-84
    MODERATE = "moderate"      # 50-69
    POOR = "poor"              # 30-49
    VERY_POOR = "very_poor"    # 0-29


class ScoreCategory(str, Enum):
    """Catégorie du score."""
    PROBABILITY = "probability"
    HABITAT = "habitat"
    PRESSURE = "pressure"
    WEATHER = "weather"
    BEHAVIOR = "behavior"
    MULTIFACTOR = "multifactor"
    DENSITY = "density"
    RISK = "risk"
    MOBILITY = "mobility"


# =============================================================================
# DATA CONTRACTS
# =============================================================================

@dataclass
class ScoreWeight:
    """Pondération d'un score dans le calcul final."""
    category: ScoreCategory
    weight: float  # 0.0 à 1.0
    description: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category.value,
            "weight": self.weight,
            "description": self.description
        }


@dataclass
class ScoreContext:
    """
    Contexte d'entrée pour le calcul d'un score.
    
    Contient toutes les informations nécessaires pour calculer un score,
    centrées sur un waypoint de référence.
    
    BIONIC V5 - Architecture Modulaire:
    - Les modificateurs avancés sont calculés par UnifiedScoringService
    - Les services individuels CONSOMMENT ces modificateurs sans logique locale
    """
    # Position (waypoint-centric)
    waypoint_id: str
    latitude: float
    longitude: float
    
    # Temporel
    target_datetime: datetime
    
    # Espèce cible
    species: str
    
    # Région
    region: str = "CA-QC"
    
    # Rayon de recherche (km)
    search_radius_km: float = 3.0
    
    # Données additionnelles (flexible)
    extra_data: Dict[str, Any] = field(default_factory=dict)
    
    # ==========================================================================
    # PHASE B: MODIFICATEURS AVANCÉS (calculés par UnifiedScoringService)
    # Les services individuels CONSOMMENT ces valeurs - AUCUNE logique locale
    # ==========================================================================
    advanced_modifiers: Dict[str, Any] = field(default_factory=lambda: {
        # Hiérarchie sociale
        "social_modifier": 1.0,
        "social_rank": "unknown",
        "social_source_ids": [],
        "social_version": "1.0",
        
        # Compétition inter-espèces
        "competition_modifier": 1.0,
        "competitors_present": [],
        "competition_source_ids": [],
        "competition_version": "1.0",
        
        # Cycles digestifs
        "digestive_modifier": 1.0,
        "digestive_phase": "unknown",
        "digestive_mobility": 1.0,
        "digestive_visibility": 1.0,
        "digestive_source_ids": [],
        "digestive_version": "1.0",
        
        # Signaux faibles
        "signals_modifier": 1.0,
        "signals_impact": 0.0,
        "signals_detected": [],
        "signals_source_ids": [],
        "signals_version": "1.0",
        
        # Modificateur global
        "total_modifier": 1.0,
        "calculation_timestamp": None
    })
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "waypoint_id": self.waypoint_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "target_datetime": self.target_datetime.isoformat(),
            "species": self.species,
            "region": self.region,
            "search_radius_km": self.search_radius_km,
            "extra_data": self.extra_data
        }


@dataclass
class ScoreComponent:
    """Composant individuel d'un score avec traçabilité Knowledge Layer."""
    name: str
    value: float           # 0-100
    weight: float          # 0-1
    weighted_value: float  # value * weight
    description: str
    factors: List[str] = field(default_factory=list)
    
    # Knowledge Layer Integration
    source_ids: List[str] = field(default_factory=list)  # Traçabilité scientifique
    confidence: float = 0.5  # Confiance de la source
    knowledge_layer_ref: Optional[str] = None  # Référence Knowledge Layer
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": round(self.value, 1),
            "weight": self.weight,
            "weighted_value": round(self.weighted_value, 1),
            "description": self.description,
            "factors": self.factors,
            "source_ids": self.source_ids,
            "confidence": round(self.confidence, 2),
            "knowledge_layer_ref": self.knowledge_layer_ref
        }


@dataclass
class ScoreResult:
    """
    Résultat standardisé d'un calcul de score.
    
    Structure commune pour tous les 9 services de scoring.
    Intègre la traçabilité Knowledge Layer.
    """
    # Identification
    category: ScoreCategory
    score_name: str
    
    # Score principal
    value: float           # 0-100
    level: ScoreLevel
    
    # Composants détaillés
    components: List[ScoreComponent] = field(default_factory=list)
    
    # Facteurs positifs/négatifs
    positive_factors: List[str] = field(default_factory=list)
    negative_factors: List[str] = field(default_factory=list)
    
    # Confiance
    confidence: float = 0.5  # 0-1
    data_quality: str = "partial"  # full, partial, minimal
    
    # Knowledge Layer Integration
    knowledge_layer_version: str = "1.0.0"
    calibration_status: str = "calibrated"  # calibrated, pre_calibrated, uncalibrated
    source_ids_aggregate: List[str] = field(default_factory=list)
    
    # Métadonnées
    calculated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    context: Optional[ScoreContext] = None
    
    # Conformité légale
    legal_compliant: bool = True
    legal_badge: str = "LÉGAL"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category.value,
            "score_name": self.score_name,
            "value": round(self.value, 1),
            "level": self.level.value,
            "components": [c.to_dict() for c in self.components],
            "positive_factors": self.positive_factors,
            "negative_factors": self.negative_factors,
            "confidence": round(self.confidence, 2),
            "data_quality": self.data_quality,
            "knowledge_layer_version": self.knowledge_layer_version,
            "calibration_status": self.calibration_status,
            "source_ids_aggregate": self.source_ids_aggregate,
            "calculated_at": self.calculated_at.isoformat(),
            "legal_compliant": self.legal_compliant,
            "legal_badge": self.legal_badge
        }
    
    @staticmethod
    def get_level_from_value(value: float) -> ScoreLevel:
        """Détermine le niveau qualitatif à partir de la valeur."""
        if value >= 85:
            return ScoreLevel.EXCELLENT
        elif value >= 70:
            return ScoreLevel.GOOD
        elif value >= 50:
            return ScoreLevel.MODERATE
        elif value >= 30:
            return ScoreLevel.POOR
        else:
            return ScoreLevel.VERY_POOR


# =============================================================================
# BASE SERVICE (ABSTRACT)
# =============================================================================

class BaseScoreService(ABC):
    """
    Classe abstraite de base pour tous les services de scoring.
    
    INTERFACE COMMUNE:
    - calculate(context) -> ScoreResult
    - get_weight() -> ScoreWeight
    - get_category() -> ScoreCategory
    - validate_context(context) -> bool
    
    KNOWLEDGE LAYER INTEGRATION:
    - Accès aux pondérations via get_habitat_weights()
    - Accès aux règles via get_species_rules()
    - Accès aux modèles saisonniers via get_seasonal_model()
    - Traçabilité complète des sources
    
    ISOLATION:
    - Aucune dépendance aux autres services
    - Chaque implémentation = module isolé
    - Aucun fallback arbitraire autorisé
    """
    
    def __init__(self):
        """Initialise le service avec accès au Knowledge Layer."""
        self._category = self._get_category()
        self._weight = self._get_default_weight()
        
        # Knowledge Layer Access Points
        self._habitat_weights = get_habitat_weights()
        self._source_registry = get_source_registry()
        
        # Track all source IDs used in calculations
        self._used_source_ids: List[str] = []
        
        logger.debug(f"Initialized {self.__class__.__name__} with Knowledge Layer")
    
    @abstractmethod
    def _get_category(self) -> ScoreCategory:
        """Retourne la catégorie du score (à implémenter)."""
        pass
    
    @abstractmethod
    def _get_default_weight(self) -> ScoreWeight:
        """Retourne la pondération par défaut (à implémenter)."""
        pass
    
    @abstractmethod
    def _get_score_name(self) -> str:
        """Retourne le nom du score (à implémenter)."""
        pass
    
    @abstractmethod
    def _calculate_components(self, context: ScoreContext) -> List[ScoreComponent]:
        """Calcule les composants du score (à implémenter)."""
        pass
    
    @property
    def category(self) -> ScoreCategory:
        """Catégorie du score."""
        return self._category
    
    @property
    def weight(self) -> ScoreWeight:
        """Pondération du score."""
        return self._weight
    
    def get_knowledge_layer_weight(self, weight_id: str) -> tuple:
        """
        Obtenir une pondération calibrée du Knowledge Layer.
        
        Args:
            weight_id: ID de la pondération (ex: VEG-NDVI)
            
        Returns:
            tuple: (weight, confidence, source_ids)
            
        Raises:
            ValueError: Si weight_id non trouvé (aucun fallback)
        """
        hw = self._habitat_weights.get(weight_id)
        if not hw:
            raise ValueError(f"Knowledge Layer weight '{weight_id}' not found. No fallback allowed.")
        
        self._used_source_ids.extend(hw.source_ids)
        return (hw.weight, hw.confidence_score, hw.source_ids)
    
    def get_species_activity(self, species: str, hour: int, season: str) -> tuple:
        """
        Obtenir le niveau d'activité depuis le Knowledge Layer.
        
        Args:
            species: Espèce (orignal, deer, etc.)
            hour: Heure (0-23)
            season: Saison
            
        Returns:
            tuple: (activity_level, source_ids)
        """
        rules = get_species_rules(species)
        if not rules:
            raise ValueError(f"Knowledge Layer species '{species}' not found. No fallback allowed.")
        
        activity, source_ids = rules.get_activity_level(hour, season)
        self._used_source_ids.extend(source_ids)
        return (activity, source_ids)
    
    def get_seasonal_modifiers(self, species: str, target_date) -> tuple:
        """
        Obtenir les modificateurs saisonniers depuis le Knowledge Layer.
        
        Args:
            species: Espèce
            target_date: Date cible
            
        Returns:
            tuple: (modifiers_dict, season_type, source_ids)
        """
        model = get_seasonal_model(species)
        if not model:
            raise ValueError(f"Knowledge Layer seasonal model for '{species}' not found. No fallback allowed.")
        
        season = model.get_current_season(target_date)
        modifiers = model.get_modifiers(target_date)
        
        self._used_source_ids.extend(model.source_ids)
        return (modifiers, season, model.source_ids)
    
    def validate_context(self, context: ScoreContext) -> bool:
        """
        Valide le contexte d'entrée.
        
        Args:
            context: Contexte à valider
            
        Returns:
            True si valide, False sinon
        """
        if not context.waypoint_id:
            return False
        if not (-90 <= context.latitude <= 90):
            return False
        if not (-180 <= context.longitude <= 180):
            return False
        if not context.species:
            return False
        return True
    
    def calculate(self, context: ScoreContext) -> ScoreResult:
        """
        Calcule le score pour le contexte donné.
        
        Args:
            context: Contexte d'entrée (waypoint-centric)
            
        Returns:
            ScoreResult avec le score calculé et traçabilité Knowledge Layer
        """
        # Reset used sources for this calculation
        self._used_source_ids = []
        
        # Validation
        if not self.validate_context(context):
            return self._create_error_result(context, "Contexte invalide")
        
        # Calcul des composants
        components = self._calculate_components(context)
        
        # Calcul du score final pondéré
        if components:
            total_weight = sum(c.weight for c in components)
            if total_weight > 0:
                value = sum(c.weighted_value for c in components) / total_weight
            else:
                value = 50.0
        else:
            value = 50.0  # Score neutre par défaut
        
        # Déterminer le niveau
        level = ScoreResult.get_level_from_value(value)
        
        # Extraire les facteurs
        positive = []
        negative = []
        for comp in components:
            if comp.value >= 70:
                positive.extend(comp.factors)
            elif comp.value < 50:
                negative.extend(comp.factors)
        
        # Aggregate source IDs from all components
        all_source_ids = list(set(self._used_source_ids))
        
        # Créer le résultat avec traçabilité
        return ScoreResult(
            category=self._category,
            score_name=self._get_score_name(),
            value=value,
            level=level,
            components=components,
            positive_factors=positive[:5],
            negative_factors=negative[:5],
            confidence=self._calculate_confidence(components),
            data_quality=self._assess_data_quality(context),
            knowledge_layer_version="1.0.0",
            calibration_status="calibrated",
            source_ids_aggregate=all_source_ids,
            context=context
        )
    
    def _calculate_confidence(self, components: List[ScoreComponent]) -> float:
        """Calcule la confiance basée sur les composants et leurs sources."""
        if not components:
            return 0.3
        
        # Confiance basée sur les composants Knowledge Layer
        component_confidences = [c.confidence for c in components if c.confidence > 0]
        
        if component_confidences:
            avg_confidence = sum(component_confidences) / len(component_confidences)
            # Bonus pour nombre de sources
            source_bonus = min(0.1, len(self._used_source_ids) * 0.01)
            return min(1.0, avg_confidence + source_bonus)
        
        # Fallback to basic calculation
        base_confidence = min(0.5, len(components) * 0.1)
        return base_confidence
    
    def _assess_data_quality(self, context: ScoreContext) -> str:
        """Évalue la qualité des données."""
        # Basé sur les sources utilisées
        if len(self._used_source_ids) >= 5:
            return "full"
        elif len(self._used_source_ids) >= 2:
            return "partial"
        else:
            return "minimal"
    
    def _create_error_result(self, context: ScoreContext, error: str) -> ScoreResult:
        """Crée un résultat d'erreur."""
        return ScoreResult(
            category=self._category,
            score_name=self._get_score_name(),
            value=0.0,
            level=ScoreLevel.VERY_POOR,
            components=[],
            positive_factors=[],
            negative_factors=[error],
            confidence=0.0,
            data_quality="minimal",
            knowledge_layer_version="1.0.0",
            calibration_status="error",
            source_ids_aggregate=[],
            context=context
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'BaseScoreService',
    'ScoreResult',
    'ScoreComponent',
    'ScoreContext',
    'ScoreWeight',
    'ScoreLevel',
    'ScoreCategory'
]
