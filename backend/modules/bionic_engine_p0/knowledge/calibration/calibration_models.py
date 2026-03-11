"""
BIONIC V5 — CALIBRATION MODELS (NIVEAU 6)
==========================================
NIVEAU 6 — Mesure & Figeage

Module de calibration et versionnage du modèle BIONIC V5.

TESTS PRÉDICTIFS:
1. Concordance spatiale (distance réelle vs prédite)
2. Concordance temporelle (timing de l'observation)
3. Précision comportementale (activité observée vs prédite)
4. Précision environnementale (conditions terrain)
5. Score global pondéré

CALIBRATION:
- Ajustement des pondérations des 9 services
- Ajustement des modificateurs (NIVEAU 1-5)
- Ajustement des seuils (saisonniers, thermiques, PRES-HUMAN)

VERSIONNAGE MAÎTRE:
- BIONIC V5 MASTER = modèle verrouillé et validé
- Documentation complète des paramètres

VERSION: 1.0.0
Conformité: G-SEC | G-QA | G-DOC | BIONIC V5 NIVEAU 6
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import logging
import math

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS
# =============================================================================

class TestType(str, Enum):
    """Types de tests prédictifs NIVEAU 6"""
    SPATIAL_CONCORDANCE = "spatial_concordance"
    TEMPORAL_CONCORDANCE = "temporal_concordance"
    BEHAVIORAL_ACCURACY = "behavioral_accuracy"
    ENVIRONMENTAL_ACCURACY = "environmental_accuracy"
    GLOBAL_WEIGHTED = "global_weighted"


class CalibrationStatus(str, Enum):
    """Statut de calibration"""
    NOT_CALIBRATED = "not_calibrated"
    IN_PROGRESS = "in_progress"
    CALIBRATED = "calibrated"
    VALIDATED = "validated"
    MASTER = "master"  # Version finale verrouillée


class AccuracyLevel(str, Enum):
    """Niveau de précision"""
    EXCELLENT = "excellent"   # >= 90%
    GOOD = "good"             # >= 80%
    ACCEPTABLE = "acceptable" # >= 70%
    POOR = "poor"             # >= 50%
    FAILING = "failing"       # < 50%


# =============================================================================
# DATA MODELS - TESTS PRÉDICTIFS
# =============================================================================

@dataclass
class PredictiveTest:
    """
    Test prédictif individuel.
    
    Compare une prédiction BIONIC avec une observation terrain.
    """
    
    test_id: str
    test_type: TestType
    
    # Prédiction
    predicted_lat: float
    predicted_lng: float
    predicted_score: float
    predicted_behavior: str
    prediction_timestamp: datetime
    
    # Observation terrain
    observed_lat: Optional[float] = None
    observed_lng: Optional[float] = None
    observed_behavior: Optional[str] = None
    observation_timestamp: Optional[datetime] = None
    
    # Résultat
    spatial_error_m: Optional[float] = None     # Distance en mètres
    temporal_error_min: Optional[float] = None  # Écart en minutes
    behavior_match: Optional[bool] = None
    
    # Score de concordance (0-100)
    concordance_score: float = 0.0
    
    # Métadonnées
    species: str = ""
    season: str = ""
    analysis_mode: str = ""
    
    # Traçabilité
    source_ids: List[str] = field(default_factory=lambda: ["SRC-TEST-PREDICTIVE"])
    version: str = "6.0.0"
    
    def calculate_concordance(self) -> float:
        """Calcule le score de concordance après observation."""
        if self.observed_lat is None or self.observed_lng is None:
            return 0.0
        
        scores = []
        
        # 1. Concordance spatiale (40%)
        if self.spatial_error_m is not None:
            # <100m = 100%, <500m = 80%, <1000m = 60%, >1000m = décroissant
            if self.spatial_error_m < 100:
                spatial_score = 100.0
            elif self.spatial_error_m < 500:
                spatial_score = 80.0 + 20 * (1 - (self.spatial_error_m - 100) / 400)
            elif self.spatial_error_m < 1000:
                spatial_score = 60.0 + 20 * (1 - (self.spatial_error_m - 500) / 500)
            else:
                spatial_score = max(0, 60 - (self.spatial_error_m - 1000) / 100)
            scores.append(("spatial", spatial_score, 0.40))
        
        # 2. Concordance temporelle (25%)
        if self.temporal_error_min is not None:
            # <15min = 100%, <60min = 80%, <120min = 60%
            if self.temporal_error_min < 15:
                temporal_score = 100.0
            elif self.temporal_error_min < 60:
                temporal_score = 80.0 + 20 * (1 - (self.temporal_error_min - 15) / 45)
            elif self.temporal_error_min < 120:
                temporal_score = 60.0 + 20 * (1 - (self.temporal_error_min - 60) / 60)
            else:
                temporal_score = max(0, 60 - (self.temporal_error_min - 120) / 30)
            scores.append(("temporal", temporal_score, 0.25))
        
        # 3. Concordance comportementale (35%)
        if self.behavior_match is not None:
            behavior_score = 100.0 if self.behavior_match else 30.0
            scores.append(("behavior", behavior_score, 0.35))
        
        # Calcul pondéré
        if not scores:
            return 0.0
        
        total_weight = sum(s[2] for s in scores)
        weighted_sum = sum(s[1] * s[2] for s in scores)
        
        self.concordance_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        return self.concordance_score


@dataclass
class PredictiveTestResult:
    """
    Résultat agrégé d'une série de tests prédictifs.
    """
    
    result_id: str
    
    # Tests inclus
    tests: List[PredictiveTest] = field(default_factory=list)
    total_tests: int = 0
    
    # Scores par type
    spatial_accuracy: float = 0.0       # %
    temporal_accuracy: float = 0.0      # %
    behavioral_accuracy: float = 0.0    # %
    environmental_accuracy: float = 0.0 # %
    
    # Score global
    global_accuracy: float = 0.0        # %
    accuracy_level: AccuracyLevel = AccuracyLevel.FAILING
    
    # Statistiques
    avg_spatial_error_m: float = 0.0
    avg_temporal_error_min: float = 0.0
    behavior_match_rate: float = 0.0
    
    # Métadonnées
    test_period_start: Optional[datetime] = None
    test_period_end: Optional[datetime] = None
    species_tested: List[str] = field(default_factory=list)
    
    # Traçabilité
    source_ids: List[str] = field(default_factory=lambda: ["SRC-TEST-RESULT"])
    version: str = "6.0.0"
    
    def calculate_global_accuracy(self) -> float:
        """Calcule la précision globale pondérée."""
        if not self.tests:
            return 0.0
        
        # Pondérations officielles BIONIC V5
        weights = {
            "spatial": 0.35,
            "temporal": 0.25,
            "behavioral": 0.30,
            "environmental": 0.10
        }
        
        self.global_accuracy = (
            self.spatial_accuracy * weights["spatial"] +
            self.temporal_accuracy * weights["temporal"] +
            self.behavioral_accuracy * weights["behavioral"] +
            self.environmental_accuracy * weights["environmental"]
        )
        
        # Déterminer le niveau
        if self.global_accuracy >= 90:
            self.accuracy_level = AccuracyLevel.EXCELLENT
        elif self.global_accuracy >= 80:
            self.accuracy_level = AccuracyLevel.GOOD
        elif self.global_accuracy >= 70:
            self.accuracy_level = AccuracyLevel.ACCEPTABLE
        elif self.global_accuracy >= 50:
            self.accuracy_level = AccuracyLevel.POOR
        else:
            self.accuracy_level = AccuracyLevel.FAILING
        
        return self.global_accuracy
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire pour l'API."""
        return {
            "result_id": self.result_id,
            "total_tests": self.total_tests,
            "accuracy": {
                "spatial": round(self.spatial_accuracy, 1),
                "temporal": round(self.temporal_accuracy, 1),
                "behavioral": round(self.behavioral_accuracy, 1),
                "environmental": round(self.environmental_accuracy, 1),
                "global": round(self.global_accuracy, 1),
                "level": self.accuracy_level.value
            },
            "statistics": {
                "avg_spatial_error_m": round(self.avg_spatial_error_m, 1),
                "avg_temporal_error_min": round(self.avg_temporal_error_min, 1),
                "behavior_match_rate": round(self.behavior_match_rate, 1)
            },
            "test_period": {
                "start": self.test_period_start.isoformat() if self.test_period_start else None,
                "end": self.test_period_end.isoformat() if self.test_period_end else None
            },
            "species_tested": self.species_tested,
            "source_ids": self.source_ids,
            "version": self.version
        }


# =============================================================================
# DATA MODELS - CALIBRATION
# =============================================================================

@dataclass
class CalibrationParameter:
    """
    Paramètre de calibration individuel.
    """
    
    param_id: str
    category: str               # service, modifier, threshold
    name: str
    
    # Valeurs
    default_value: float
    current_value: float
    min_value: float = 0.0
    max_value: float = 2.0
    
    # Métadonnées de calibration
    last_calibrated: Optional[datetime] = None
    calibration_confidence: float = 0.5
    
    # Impact sur la précision
    impact_on_accuracy: float = 0.0  # -1 à +1
    
    # Traçabilité
    source_ids: List[str] = field(default_factory=list)
    version: str = "6.0.0"


@dataclass
class CalibrationProfile:
    """
    Profil de calibration complet pour le modèle BIONIC V5.
    """
    
    profile_id: str
    profile_name: str
    status: CalibrationStatus = CalibrationStatus.NOT_CALIBRATED
    
    # Paramètres de calibration
    parameters: Dict[str, CalibrationParameter] = field(default_factory=dict)
    
    # Pondérations des 9 services
    service_weights: Dict[str, float] = field(default_factory=lambda: {
        "probability": 0.15,
        "habitat": 0.12,
        "pressure": 0.10,
        "weather": 0.12,
        "behavior": 0.12,
        "multifactor": 0.10,
        "density": 0.10,
        "risk": 0.08,
        "mobility": 0.11
    })
    
    # Modificateurs par niveau
    level_modifiers: Dict[str, float] = field(default_factory=lambda: {
        "niveau_1_seasonal": 1.0,
        "niveau_1_thermal": 1.0,
        "niveau_2_digestive": 1.0,
        "niveau_2_social": 1.0,
        "niveau_3_pres_human": 1.0,
        "niveau_4_corridor": 1.0,
        "niveau_5_mobility": 1.0
    })
    
    # Seuils
    thresholds: Dict[str, float] = field(default_factory=lambda: {
        "thermal_stress_activation": 25.0,      # °C
        "hunting_pressure_high": 0.7,           # niveau
        "mobility_low_speed": 0.5,              # km/h
        "corridor_bonus": 1.2,                  # multiplicateur
        "seasonal_rut_boost": 1.5               # multiplicateur
    })
    
    # Résultats de validation
    validation_accuracy: float = 0.0
    validation_tests_count: int = 0
    last_validated: Optional[datetime] = None
    
    # Traçabilité
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source_ids: List[str] = field(default_factory=lambda: ["SRC-CALIBRATION-PROFILE"])
    version: str = "6.0.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire pour l'API."""
        return {
            "profile_id": self.profile_id,
            "profile_name": self.profile_name,
            "status": self.status.value,
            "service_weights": {k: round(v, 3) for k, v in self.service_weights.items()},
            "level_modifiers": {k: round(v, 3) for k, v in self.level_modifiers.items()},
            "thresholds": self.thresholds,
            "validation": {
                "accuracy": round(self.validation_accuracy, 1),
                "tests_count": self.validation_tests_count,
                "last_validated": self.last_validated.isoformat() if self.last_validated else None
            },
            "created_at": self.created_at.isoformat(),
            "source_ids": self.source_ids,
            "version": self.version
        }


# =============================================================================
# DATA MODELS - VERSIONNAGE MAÎTRE
# =============================================================================

@dataclass
class ModelVersion:
    """
    Version du modèle BIONIC V5.
    
    BIONIC V5 MASTER = version verrouillée et validée à 95%+ de précision.
    """
    
    version_id: str
    version_name: str
    version_number: str         # ex: "5.0.0-MASTER"
    
    # Statut
    is_master: bool = False
    is_locked: bool = False
    
    # Profil de calibration associé
    calibration_profile: Optional[CalibrationProfile] = None
    
    # Métriques de validation
    global_accuracy: float = 0.0
    spatial_accuracy: float = 0.0
    temporal_accuracy: float = 0.0
    behavioral_accuracy: float = 0.0
    
    # Tests de validation
    validation_tests_count: int = 0
    validation_species: List[str] = field(default_factory=list)
    validation_seasons: List[str] = field(default_factory=list)
    
    # Niveaux intégrés
    levels_integrated: List[str] = field(default_factory=lambda: [
        "NIVEAU 1 - Saisonnalité & Phénologie",
        "NIVEAU 2 - Comportements Avancés",
        "NIVEAU 3 - PRES-HUMAN",
        "NIVEAU 4 - Habitat & Corridors",
        "NIVEAU 5 - Mobilité Dynamique"
    ])
    
    # Documentation
    changelog: List[str] = field(default_factory=list)
    known_limitations: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    locked_at: Optional[datetime] = None
    
    # Traçabilité
    source_ids: List[str] = field(default_factory=lambda: ["SRC-MODEL-VERSION"])
    
    def lock_as_master(self, accuracy: float) -> bool:
        """Verrouille la version comme MASTER si la précision >= 95%."""
        if accuracy >= 95.0:
            self.is_master = True
            self.is_locked = True
            self.locked_at = datetime.now(timezone.utc)
            self.global_accuracy = accuracy
            self.version_number = f"{self.version_number}-MASTER"
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire pour l'API."""
        return {
            "version_id": self.version_id,
            "version_name": self.version_name,
            "version_number": self.version_number,
            "status": {
                "is_master": self.is_master,
                "is_locked": self.is_locked,
                "locked_at": self.locked_at.isoformat() if self.locked_at else None
            },
            "accuracy": {
                "global": round(self.global_accuracy, 1),
                "spatial": round(self.spatial_accuracy, 1),
                "temporal": round(self.temporal_accuracy, 1),
                "behavioral": round(self.behavioral_accuracy, 1)
            },
            "validation": {
                "tests_count": self.validation_tests_count,
                "species": self.validation_species,
                "seasons": self.validation_seasons
            },
            "levels_integrated": self.levels_integrated,
            "changelog": self.changelog,
            "known_limitations": self.known_limitations,
            "created_at": self.created_at.isoformat(),
            "source_ids": self.source_ids
        }


# =============================================================================
# CALIBRATION REGISTRY
# =============================================================================

class CalibrationRegistry:
    """
    Registre centralisé de calibration et versionnage.
    
    NIVEAU 6 - Knowledge Layer:
    - Tests prédictifs
    - Calibration des paramètres
    - Versionnage MASTER
    """
    
    def __init__(self):
        self._version = "6.0.0"
        self._test_counter = 0
        
        # Profil de calibration courant
        self._current_profile = CalibrationProfile(
            profile_id="CALIB-DEFAULT",
            profile_name="BIONIC V5 Default Calibration"
        )
        
        # Version du modèle
        self._current_model_version = ModelVersion(
            version_id="BIONIC-V5-001",
            version_name="BIONIC V5 Pre-Master",
            version_number="5.0.0",
            changelog=[
                "NIVEAU 1: Saisonnalité et phénologie",
                "NIVEAU 2: Comportements avancés (social, digestif, signaux)",
                "NIVEAU 3: PRES-HUMAN (pression humaine réelle)",
                "NIVEAU 4: Habitat & Corridors (5 types)",
                "NIVEAU 5: Mobilité dynamique"
            ]
        )
        
        # Historique des tests
        self._test_history: List[PredictiveTest] = []
        
        logger.info(f"CalibrationRegistry initialized: v{self._version}")
    
    def _generate_test_id(self) -> str:
        """Génère un ID unique pour un test."""
        self._test_counter += 1
        timestamp = datetime.now(timezone.utc).strftime("%H%M%S")
        return f"TEST-{timestamp}-{self._test_counter:04d}"
    
    def create_predictive_test(
        self,
        predicted_lat: float,
        predicted_lng: float,
        predicted_score: float,
        predicted_behavior: str,
        prediction_timestamp: datetime,
        species: str,
        season: str,
        analysis_mode: str
    ) -> PredictiveTest:
        """Crée un nouveau test prédictif."""
        test = PredictiveTest(
            test_id=self._generate_test_id(),
            test_type=TestType.GLOBAL_WEIGHTED,
            predicted_lat=predicted_lat,
            predicted_lng=predicted_lng,
            predicted_score=predicted_score,
            predicted_behavior=predicted_behavior,
            prediction_timestamp=prediction_timestamp,
            species=species,
            season=season,
            analysis_mode=analysis_mode
        )
        self._test_history.append(test)
        return test
    
    def record_observation(
        self,
        test_id: str,
        observed_lat: float,
        observed_lng: float,
        observed_behavior: str,
        observation_timestamp: datetime
    ) -> Optional[PredictiveTest]:
        """Enregistre une observation terrain pour un test."""
        for test in self._test_history:
            if test.test_id == test_id:
                test.observed_lat = observed_lat
                test.observed_lng = observed_lng
                test.observed_behavior = observed_behavior
                test.observation_timestamp = observation_timestamp
                
                # Calculer les erreurs
                test.spatial_error_m = self._calculate_distance(
                    test.predicted_lat, test.predicted_lng,
                    observed_lat, observed_lng
                )
                
                if test.prediction_timestamp and observation_timestamp:
                    delta = abs((observation_timestamp - test.prediction_timestamp).total_seconds())
                    test.temporal_error_min = delta / 60
                
                test.behavior_match = (
                    test.predicted_behavior.lower() == observed_behavior.lower()
                )
                
                test.calculate_concordance()
                
                logger.info(f"Observation recorded for {test_id}: concordance={test.concordance_score:.1f}%")
                return test
        
        return None
    
    def _calculate_distance(
        self,
        lat1: float, lng1: float,
        lat2: float, lng2: float
    ) -> float:
        """Calcule la distance en mètres entre deux points (Haversine)."""
        R = 6371000  # Rayon de la Terre en mètres
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def calculate_test_results(self) -> PredictiveTestResult:
        """Calcule les résultats agrégés des tests."""
        validated_tests = [t for t in self._test_history if t.observed_lat is not None]
        
        if not validated_tests:
            return PredictiveTestResult(
                result_id=f"RES-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
                total_tests=0
            )
        
        result = PredictiveTestResult(
            result_id=f"RES-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            tests=validated_tests,
            total_tests=len(validated_tests)
        )
        
        # Calculer les moyennes
        spatial_errors = [t.spatial_error_m for t in validated_tests if t.spatial_error_m]
        temporal_errors = [t.temporal_error_min for t in validated_tests if t.temporal_error_min]
        behavior_matches = [t.behavior_match for t in validated_tests if t.behavior_match is not None]
        
        if spatial_errors:
            result.avg_spatial_error_m = sum(spatial_errors) / len(spatial_errors)
            # Convertir en pourcentage de précision
            result.spatial_accuracy = max(0, 100 - (result.avg_spatial_error_m / 10))
        
        if temporal_errors:
            result.avg_temporal_error_min = sum(temporal_errors) / len(temporal_errors)
            result.temporal_accuracy = max(0, 100 - (result.avg_temporal_error_min / 2))
        
        if behavior_matches:
            result.behavior_match_rate = sum(1 for m in behavior_matches if m) / len(behavior_matches) * 100
            result.behavioral_accuracy = result.behavior_match_rate
        
        # Environmental accuracy (simulé basé sur les autres métriques)
        result.environmental_accuracy = (result.spatial_accuracy + result.behavioral_accuracy) / 2
        
        # Période de test
        timestamps = [t.prediction_timestamp for t in validated_tests]
        result.test_period_start = min(timestamps)
        result.test_period_end = max(timestamps)
        
        # Espèces testées
        result.species_tested = list(set(t.species for t in validated_tests))
        
        result.calculate_global_accuracy()
        
        return result
    
    def get_current_profile(self) -> CalibrationProfile:
        """Retourne le profil de calibration courant."""
        return self._current_profile
    
    def get_model_version(self) -> ModelVersion:
        """Retourne la version du modèle."""
        return self._current_model_version
    
    def update_service_weight(self, service_name: str, new_weight: float) -> bool:
        """Met à jour le poids d'un service."""
        if service_name in self._current_profile.service_weights:
            old_weight = self._current_profile.service_weights[service_name]
            self._current_profile.service_weights[service_name] = max(0, min(1, new_weight))
            self._current_profile.status = CalibrationStatus.IN_PROGRESS
            logger.info(f"Weight updated: {service_name} {old_weight:.3f} -> {new_weight:.3f}")
            return True
        return False
    
    def update_level_modifier(self, level_name: str, new_modifier: float) -> bool:
        """Met à jour un modificateur de niveau."""
        if level_name in self._current_profile.level_modifiers:
            old_mod = self._current_profile.level_modifiers[level_name]
            self._current_profile.level_modifiers[level_name] = max(0.1, min(3.0, new_modifier))
            self._current_profile.status = CalibrationStatus.IN_PROGRESS
            logger.info(f"Modifier updated: {level_name} {old_mod:.3f} -> {new_modifier:.3f}")
            return True
        return False
    
    def validate_calibration(self, test_result: PredictiveTestResult) -> bool:
        """Valide la calibration avec les résultats de tests."""
        self._current_profile.validation_accuracy = test_result.global_accuracy
        self._current_profile.validation_tests_count = test_result.total_tests
        self._current_profile.last_validated = datetime.now(timezone.utc)
        
        if test_result.global_accuracy >= 70:
            self._current_profile.status = CalibrationStatus.VALIDATED
            logger.info(f"Calibration validated: {test_result.global_accuracy:.1f}%")
            return True
        
        logger.warning(f"Calibration failed: {test_result.global_accuracy:.1f}% < 70%")
        return False
    
    def lock_as_master(self, accuracy: float) -> Optional[ModelVersion]:
        """Verrouille le modèle comme MASTER si précision >= 95%."""
        if accuracy >= 95.0:
            self._current_model_version.lock_as_master(accuracy)
            self._current_model_version.calibration_profile = self._current_profile
            self._current_profile.status = CalibrationStatus.MASTER
            
            logger.info(f"MODEL LOCKED AS MASTER: {self._current_model_version.version_number}")
            return self._current_model_version
        
        logger.warning(f"Cannot lock as MASTER: {accuracy:.1f}% < 95%")
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Statistiques du registre."""
        return {
            "version": self._version,
            "profile_status": self._current_profile.status.value,
            "model_version": self._current_model_version.version_number,
            "is_master": self._current_model_version.is_master,
            "tests_recorded": len(self._test_history),
            "tests_validated": len([t for t in self._test_history if t.observed_lat]),
            "current_accuracy": self._current_profile.validation_accuracy
        }


# =============================================================================
# SINGLETON
# =============================================================================

_registry_instance: Optional[CalibrationRegistry] = None


def get_calibration_registry() -> CalibrationRegistry:
    """Obtenir l'instance singleton du registre de calibration."""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = CalibrationRegistry()
    return _registry_instance


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    'TestType',
    'CalibrationStatus',
    'AccuracyLevel',
    # Data models
    'PredictiveTest',
    'PredictiveTestResult',
    'CalibrationParameter',
    'CalibrationProfile',
    'ModelVersion',
    # Registry
    'CalibrationRegistry',
    'get_calibration_registry'
]
