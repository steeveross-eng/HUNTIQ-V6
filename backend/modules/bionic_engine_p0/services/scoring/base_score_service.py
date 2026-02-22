"""
BIONIC ENGINE — Base Score Service
===================================
Interface de base et data contracts pour tous les services de scoring.

ARCHITECTURE:
- Classe abstraite BaseScoreService définissant l'interface commune
- Data contracts partagés (ScoreResult, ScoreContext, etc.)
- Aucune logique métier (structure uniquement)

ISOLATION:
- Aucune dépendance aux autres services BIONIC
- Interface pure pour héritage

Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

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
    """Composant individuel d'un score."""
    name: str
    value: float           # 0-100
    weight: float          # 0-1
    weighted_value: float  # value * weight
    description: str
    factors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": round(self.value, 1),
            "weight": self.weight,
            "weighted_value": round(self.weighted_value, 1),
            "description": self.description,
            "factors": self.factors
        }


@dataclass
class ScoreResult:
    """
    Résultat standardisé d'un calcul de score.
    
    Structure commune pour tous les 9 services de scoring.
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
    
    # Métadonnées
    calculated_at: datetime = field(default_factory=datetime.utcnow)
    context: Optional[ScoreContext] = None
    
    # Conformité légale
    legal_compliant: bool = True
    legal_badge: str = "⚖️ LÉGAL"
    
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
    
    ISOLATION:
    - Aucune dépendance aux autres services
    - Chaque implémentation = module isolé
    """
    
    def __init__(self):
        """Initialise le service."""
        self._category = self._get_category()
        self._weight = self._get_default_weight()
        logger.debug(f"Initialized {self.__class__.__name__}")
    
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
            ScoreResult avec le score calculé
        """
        # Validation
        if not self.validate_context(context):
            return self._create_error_result(context, "Contexte invalide")
        
        # Calcul des composants
        components = self._calculate_components(context)
        
        # Calcul du score final
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
        
        # Créer le résultat
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
            context=context
        )
    
    def _calculate_confidence(self, components: List[ScoreComponent]) -> float:
        """Calcule la confiance basée sur les composants."""
        if not components:
            return 0.3
        
        # Plus de composants = plus de confiance
        base_confidence = min(0.5, len(components) * 0.1)
        
        # Variance faible = plus de confiance
        values = [c.value for c in components]
        if len(values) > 1:
            variance = sum((v - sum(values)/len(values))**2 for v in values) / len(values)
            variance_factor = max(0, 0.3 - variance / 1000)
        else:
            variance_factor = 0.2
        
        return min(1.0, base_confidence + variance_factor)
    
    def _assess_data_quality(self, context: ScoreContext) -> str:
        """Évalue la qualité des données."""
        # Par défaut, qualité partielle
        # Les implémentations spécifiques peuvent override
        return "partial"
    
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
