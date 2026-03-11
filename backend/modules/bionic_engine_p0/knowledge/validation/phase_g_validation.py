"""
BIONIC V5 — PHASE G: Validation Terrain Multi-Années/Multi-Espèces
====================================================================
Structure de validation pour la certification MASTER.

OBJECTIF:
Fournir un cadre pour valider le modèle BIONIC V5 sur:
- Plusieurs saisons consécutives (multi-années)
- Plusieurs espèces simultanément
- Des métriques standardisées et reproductibles

MÉTRIQUES DE VALIDATION:
- Précision spatiale (erreur en mètres)
- Précision temporelle (erreur en minutes)
- Concordance comportementale (%)
- Score global pondéré (objectif ≥95%)

STATUT: Structure préparée — En attente de données terrain
VERSION: 1.0.0
Conformité: G-SEC | G-QA | G-DOC | BIONIC V5 MASTER
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class ValidationScope(str, Enum):
    """Portée de la validation."""
    SINGLE_SEASON = "single_season"
    MULTI_SEASON = "multi_season"
    ANNUAL = "annual"
    MULTI_YEAR = "multi_year"


class ValidationMetricType(str, Enum):
    """Types de métriques de validation."""
    SPATIAL_ACCURACY = "spatial_accuracy"
    TEMPORAL_ACCURACY = "temporal_accuracy"
    BEHAVIORAL_MATCH = "behavioral_match"
    SCORE_CORRELATION = "score_correlation"
    GLOBAL_CONCORDANCE = "global_concordance"


class SpeciesValidationTier(str, Enum):
    """Niveaux de validation par espèce."""
    TIER_1_PRIMARY = "tier_1"     # Orignal — Espèce primaire de validation
    TIER_2_SECONDARY = "tier_2"   # Cerf de Virginie, Ours noir
    TIER_3_EXTENDED = "tier_3"    # Caribou, Wapiti


@dataclass
class ValidationMetric:
    """Métrique individuelle de validation."""
    metric_type: ValidationMetricType
    value: float
    target: float
    unit: str
    is_passing: bool = False
    sample_size: int = 0
    confidence_interval: float = 0.0
    
    def __post_init__(self):
        if self.metric_type in (
            ValidationMetricType.BEHAVIORAL_MATCH,
            ValidationMetricType.GLOBAL_CONCORDANCE,
            ValidationMetricType.SCORE_CORRELATION
        ):
            self.is_passing = self.value >= self.target
        else:
            self.is_passing = self.value <= self.target


@dataclass
class SpeciesValidationProfile:
    """Profil de validation pour une espèce."""
    species: str
    tier: SpeciesValidationTier
    min_observations: int = 30
    target_precision: float = 95.0
    
    # Seuils par métrique
    spatial_threshold_m: float = 500.0
    temporal_threshold_min: float = 60.0
    behavioral_threshold_pct: float = 85.0
    
    # Résultats
    observations_count: int = 0
    metrics: Dict[str, ValidationMetric] = field(default_factory=dict)
    is_validated: bool = False
    validation_date: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "species": self.species,
            "tier": self.tier.value,
            "min_observations": self.min_observations,
            "target_precision": self.target_precision,
            "observations_count": self.observations_count,
            "is_validated": self.is_validated,
            "validation_date": self.validation_date,
            "thresholds": {
                "spatial_m": self.spatial_threshold_m,
                "temporal_min": self.temporal_threshold_min,
                "behavioral_pct": self.behavioral_threshold_pct
            },
            "metrics": {k: vars(v) for k, v in self.metrics.items()}
        }


@dataclass
class SeasonValidationWindow:
    """Fenêtre de validation saisonnière."""
    season: str
    year: int
    start_date: str
    end_date: str
    observations_count: int = 0
    precision: float = 0.0
    is_complete: bool = False


@dataclass
class PhaseGValidationPlan:
    """Plan de validation PHASE G complet."""
    plan_id: str = "PHASE-G-V1"
    version: str = "1.0.0"
    status: str = "prepared"
    
    # Configuration
    target_years: int = 2
    target_species: List[str] = field(default_factory=lambda: [
        "orignal", "cerf_de_virginie", "ours_noir"
    ])
    target_global_precision: float = 95.0
    min_observations_per_species: int = 30
    
    # Profils par espèce
    species_profiles: Dict[str, SpeciesValidationProfile] = field(default_factory=dict)
    
    # Fenêtres saisonnières
    season_windows: List[SeasonValidationWindow] = field(default_factory=list)
    
    # Source IDs
    source_ids: List[str] = field(default_factory=lambda: ["SRC-PHASE-G-VALIDATION"])
    
    def __post_init__(self):
        if not self.species_profiles:
            self.species_profiles = {
                "orignal": SpeciesValidationProfile(
                    species="orignal",
                    tier=SpeciesValidationTier.TIER_1_PRIMARY,
                    min_observations=50,
                    target_precision=95.0,
                    spatial_threshold_m=400.0,
                    temporal_threshold_min=45.0,
                    behavioral_threshold_pct=90.0
                ),
                "cerf_de_virginie": SpeciesValidationProfile(
                    species="cerf_de_virginie",
                    tier=SpeciesValidationTier.TIER_2_SECONDARY,
                    min_observations=30,
                    target_precision=90.0,
                    spatial_threshold_m=500.0,
                    temporal_threshold_min=60.0,
                    behavioral_threshold_pct=85.0
                ),
                "ours_noir": SpeciesValidationProfile(
                    species="ours_noir",
                    tier=SpeciesValidationTier.TIER_2_SECONDARY,
                    min_observations=25,
                    target_precision=90.0,
                    spatial_threshold_m=600.0,
                    temporal_threshold_min=90.0,
                    behavioral_threshold_pct=80.0
                )
            }
    
    def get_progress(self) -> Dict[str, Any]:
        """Calcule la progression globale de la validation."""
        total_species = len(self.target_species)
        validated_species = sum(
            1 for sp in self.species_profiles.values() 
            if sp.is_validated
        )
        
        total_obs_needed = sum(
            sp.min_observations 
            for sp in self.species_profiles.values()
        )
        total_obs_collected = sum(
            sp.observations_count 
            for sp in self.species_profiles.values()
        )
        
        return {
            "species_validated": validated_species,
            "species_total": total_species,
            "species_progress_pct": round((validated_species / total_species * 100) if total_species > 0 else 0, 1),
            "observations_collected": total_obs_collected,
            "observations_needed": total_obs_needed,
            "observations_progress_pct": round((total_obs_collected / total_obs_needed * 100) if total_obs_needed > 0 else 0, 1),
            "is_complete": validated_species >= total_species,
            "status": self.status
        }
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "version": self.version,
            "status": self.status,
            "target_years": self.target_years,
            "target_species": self.target_species,
            "target_global_precision": self.target_global_precision,
            "progress": self.get_progress(),
            "species_profiles": {
                k: v.to_dict() for k, v in self.species_profiles.items()
            },
            "source_ids": self.source_ids
        }


# =============================================================================
# REGISTRY SINGLETON
# =============================================================================

class PhaseGRegistry:
    """Registre singleton pour la PHASE G."""
    
    _instance = None
    _plan = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_plan(self) -> PhaseGValidationPlan:
        """Retourne le plan de validation PHASE G."""
        if self._plan is None:
            self._plan = PhaseGValidationPlan()
        return self._plan
    
    def get_species_profile(self, species: str) -> Optional[SpeciesValidationProfile]:
        """Retourne le profil de validation pour une espèce."""
        plan = self.get_plan()
        return plan.species_profiles.get(species)
    
    def update_species_observations(self, species: str, count: int) -> bool:
        """Met à jour le nombre d'observations pour une espèce."""
        plan = self.get_plan()
        profile = plan.species_profiles.get(species)
        if profile:
            profile.observations_count = count
            return True
        return False
