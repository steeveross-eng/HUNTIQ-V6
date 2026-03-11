"""
BIONIC V5 — CALIBRATION OPTIMIZER (PHASE F → MASTER)
======================================================
Calibration vers BIONIC V5 MASTER

Module d'optimisation hybride des pondérations et modificateurs.
- Suggestions automatiques basées sur les écarts observés
- Validation manuelle obligatoire avant application
- Traçabilité complète de chaque ajustement

OBJECTIF: Atteindre ≥95% de précision globale pour le statut MASTER

VERSION: 7.1.0
Conformité: G-SEC | G-QA | G-DOC | BIONIC V5 MASTER
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import logging
import math

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS
# =============================================================================

class AdjustmentType(str, Enum):
    """Type d'ajustement proposé"""
    SERVICE_WEIGHT = "service_weight"           # Pondération d'un service
    LEVEL_MODIFIER = "level_modifier"           # Modificateur de niveau
    THRESHOLD = "threshold"                     # Seuil
    CORRELATION_FACTOR = "correlation_factor"   # Facteur de corrélation


class AdjustmentStatus(str, Enum):
    """Statut d'un ajustement"""
    PENDING = "pending"           # En attente de validation
    APPROVED = "approved"         # Approuvé, en attente d'application
    APPLIED = "applied"           # Appliqué au modèle
    REJECTED = "rejected"         # Rejeté par l'utilisateur


class PrecisionCategory(str, Enum):
    """Catégorie de précision pour cibler les ajustements"""
    SPATIAL = "spatial"           # Précision spatiale
    TEMPORAL = "temporal"         # Précision temporelle
    BEHAVIORAL = "behavioral"     # Précision comportementale
    GLOBAL = "global"             # Score global


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class CalibrationSuggestion:
    """
    Suggestion d'ajustement de calibration.
    
    Mode hybride: suggestion automatique + validation manuelle obligatoire.
    """
    
    # Champs requis (sans valeur par défaut)
    suggestion_id: str
    adjustment_type: AdjustmentType
    parameter_name: str
    parameter_category: str           # service_weights, level_modifiers, thresholds
    current_value: float
    suggested_value: float
    
    # Champs optionnels (avec valeur par défaut)
    status: AdjustmentStatus = AdjustmentStatus.PENDING
    change_delta: float = 0.0
    change_percent: float = 0.0
    
    # Justification automatique
    justification: str = ""
    precision_category: PrecisionCategory = PrecisionCategory.GLOBAL
    expected_impact: float = 0.0      # Impact estimé sur la précision (%)
    confidence: float = 0.5           # Confiance dans la suggestion (0-1)
    
    # Données de base
    observations_count: int = 0
    avg_error_before: float = 0.0
    
    # Validation
    validated_by: Optional[str] = None
    validated_at: Optional[datetime] = None
    validation_notes: str = ""
    
    # Traçabilité
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    applied_at: Optional[datetime] = None
    source_ids: List[str] = field(default_factory=lambda: ["SRC-CALIBRATION-SUGGESTION"])
    version: str = "7.1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire pour l'API."""
        return {
            "suggestion_id": self.suggestion_id,
            "adjustment_type": self.adjustment_type.value,
            "status": self.status.value,
            "parameter": {
                "name": self.parameter_name,
                "category": self.parameter_category,
                "current_value": round(self.current_value, 4),
                "suggested_value": round(self.suggested_value, 4),
                "change_delta": round(self.change_delta, 4),
                "change_percent": round(self.change_percent, 2)
            },
            "analysis": {
                "justification": self.justification,
                "precision_category": self.precision_category.value,
                "expected_impact": round(self.expected_impact, 2),
                "confidence": round(self.confidence, 2),
                "observations_count": self.observations_count,
                "avg_error_before": round(self.avg_error_before, 2)
            },
            "validation": {
                "validated_by": self.validated_by,
                "validated_at": self.validated_at.isoformat() if self.validated_at else None,
                "notes": self.validation_notes
            },
            "timestamps": {
                "created_at": self.created_at.isoformat(),
                "applied_at": self.applied_at.isoformat() if self.applied_at else None
            },
            "source_ids": self.source_ids,
            "version": self.version
        }


@dataclass
class ComparisonResult:
    """
    Résultat de comparaison prédiction vs observation.
    """
    
    comparison_id: str
    observation_id: str
    
    # Prédiction BIONIC
    predicted_lat: float
    predicted_lng: float
    predicted_behavior: str
    predicted_score: float
    prediction_timestamp: datetime
    
    # Observation terrain
    observed_lat: float
    observed_lng: float
    observed_behavior: str
    observed_timestamp: datetime
    
    # Écarts calculés
    spatial_error_m: float = 0.0
    temporal_error_min: float = 0.0
    behavior_match: bool = False
    
    # Scores de concordance
    spatial_concordance: float = 0.0      # %
    temporal_concordance: float = 0.0     # %
    behavioral_concordance: float = 0.0   # %
    global_concordance: float = 0.0       # %
    
    # Contexte
    species: str = ""
    season: str = ""
    
    # Traçabilité
    calculated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source_ids: List[str] = field(default_factory=lambda: ["SRC-COMPARISON"])
    version: str = "7.1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire pour l'API."""
        return {
            "comparison_id": self.comparison_id,
            "observation_id": self.observation_id,
            "prediction": {
                "lat": self.predicted_lat,
                "lng": self.predicted_lng,
                "behavior": self.predicted_behavior,
                "score": round(self.predicted_score, 2),
                "timestamp": self.prediction_timestamp.isoformat()
            },
            "observation": {
                "lat": self.observed_lat,
                "lng": self.observed_lng,
                "behavior": self.observed_behavior,
                "timestamp": self.observed_timestamp.isoformat()
            },
            "errors": {
                "spatial_m": round(self.spatial_error_m, 1),
                "temporal_min": round(self.temporal_error_min, 1),
                "behavior_match": self.behavior_match
            },
            "concordance": {
                "spatial": round(self.spatial_concordance, 1),
                "temporal": round(self.temporal_concordance, 1),
                "behavioral": round(self.behavioral_concordance, 1),
                "global": round(self.global_concordance, 1)
            },
            "context": {
                "species": self.species,
                "season": self.season
            },
            "calculated_at": self.calculated_at.isoformat(),
            "source_ids": self.source_ids,
            "version": self.version
        }


@dataclass 
class CalibrationDashboardData:
    """
    Données pour le dashboard de calibration.
    """
    
    # Précision globale
    global_precision: float = 0.0
    target_precision: float = 95.0
    precision_gap: float = 0.0
    
    # Précision par catégorie
    spatial_precision: float = 0.0
    temporal_precision: float = 0.0
    behavioral_precision: float = 0.0
    
    # Précision par espèce
    by_species: Dict[str, float] = field(default_factory=dict)
    
    # Précision par comportement
    by_behavior: Dict[str, float] = field(default_factory=dict)
    
    # Statistiques
    total_observations: int = 0
    total_comparisons: int = 0
    observations_this_week: int = 0
    
    # Tendance
    precision_trend: List[Dict[str, Any]] = field(default_factory=list)
    
    # Suggestions en attente
    pending_suggestions: int = 0
    
    # Statut MASTER
    is_master_ready: bool = False
    estimated_comparisons_to_master: int = 0
    
    # Version
    model_version: str = "5.0.0 Pre-Master"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir pour l'API."""
        return {
            "precision": {
                "global": round(self.global_precision, 1),
                "target": self.target_precision,
                "gap": round(self.precision_gap, 1),
                "spatial": round(self.spatial_precision, 1),
                "temporal": round(self.temporal_precision, 1),
                "behavioral": round(self.behavioral_precision, 1)
            },
            "by_species": {k: round(v, 1) for k, v in self.by_species.items()},
            "by_behavior": {k: round(v, 1) for k, v in self.by_behavior.items()},
            "statistics": {
                "total_observations": self.total_observations,
                "total_comparisons": self.total_comparisons,
                "observations_this_week": self.observations_this_week
            },
            "trend": self.precision_trend,
            "suggestions": {
                "pending": self.pending_suggestions
            },
            "master_status": {
                "is_ready": self.is_master_ready,
                "estimated_comparisons_needed": self.estimated_comparisons_to_master
            },
            "model_version": self.model_version
        }


# =============================================================================
# CALIBRATION OPTIMIZER
# =============================================================================

class CalibrationOptimizer:
    """
    Optimiseur de calibration hybride.
    
    FONCTIONNALITÉS:
    1. Analyse des écarts observation vs prédiction
    2. Génération automatique de suggestions d'ajustement
    3. Validation manuelle obligatoire
    4. Application contrôlée des ajustements
    5. Suivi de la progression vers MASTER
    
    OBJECTIF: Atteindre ≥95% de précision pour le statut BIONIC V5 MASTER
    """
    
    def __init__(self):
        self._version = "7.1.0"
        self._suggestion_counter = 0
        self._comparison_counter = 0
        
        # Stockage
        self._comparisons: Dict[str, ComparisonResult] = {}
        self._suggestions: Dict[str, CalibrationSuggestion] = {}
        
        # Historique de précision (pour tendance)
        self._precision_history: List[Dict[str, Any]] = []
        
        # Pondérations de calcul de concordance
        self._concordance_weights = {
            "spatial": 0.40,
            "temporal": 0.25,
            "behavioral": 0.35
        }
        
        logger.info(f"CalibrationOptimizer initialized: v{self._version}")
    
    # =========================================================================
    # GÉNÉRATION D'IDS
    # =========================================================================
    
    def _generate_comparison_id(self) -> str:
        """Génère un ID unique pour une comparaison."""
        self._comparison_counter += 1
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"CMP-{timestamp}-{self._comparison_counter:04d}"
    
    def _generate_suggestion_id(self) -> str:
        """Génère un ID unique pour une suggestion."""
        self._suggestion_counter += 1
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"SUG-{timestamp}-{self._suggestion_counter:04d}"
    
    # =========================================================================
    # COMPARAISON PRÉDICTION VS OBSERVATION
    # =========================================================================
    
    def compare_prediction_vs_observation(
        self,
        observation_id: str,
        # Prédiction
        predicted_lat: float,
        predicted_lng: float,
        predicted_behavior: str,
        predicted_score: float,
        prediction_timestamp: datetime,
        # Observation
        observed_lat: float,
        observed_lng: float,
        observed_behavior: str,
        observed_timestamp: datetime,
        # Contexte
        species: str = "",
        season: str = ""
    ) -> ComparisonResult:
        """
        Compare une prédiction BIONIC avec une observation terrain.
        
        Calcule les écarts et scores de concordance.
        """
        comparison_id = self._generate_comparison_id()
        
        # Calculer l'erreur spatiale (Haversine)
        spatial_error = self._calculate_distance(
            predicted_lat, predicted_lng,
            observed_lat, observed_lng
        )
        
        # Calculer l'erreur temporelle
        time_delta = abs((observed_timestamp - prediction_timestamp).total_seconds())
        temporal_error = time_delta / 60  # En minutes
        
        # Vérifier la concordance comportementale
        behavior_match = predicted_behavior.lower() == observed_behavior.lower()
        
        # Calculer les scores de concordance
        spatial_concordance = self._calculate_spatial_concordance(spatial_error)
        temporal_concordance = self._calculate_temporal_concordance(temporal_error)
        behavioral_concordance = 100.0 if behavior_match else 30.0
        
        # Concordance globale pondérée
        global_concordance = (
            spatial_concordance * self._concordance_weights["spatial"] +
            temporal_concordance * self._concordance_weights["temporal"] +
            behavioral_concordance * self._concordance_weights["behavioral"]
        )
        
        # Créer le résultat
        result = ComparisonResult(
            comparison_id=comparison_id,
            observation_id=observation_id,
            predicted_lat=predicted_lat,
            predicted_lng=predicted_lng,
            predicted_behavior=predicted_behavior,
            predicted_score=predicted_score,
            prediction_timestamp=prediction_timestamp,
            observed_lat=observed_lat,
            observed_lng=observed_lng,
            observed_behavior=observed_behavior,
            observed_timestamp=observed_timestamp,
            spatial_error_m=spatial_error,
            temporal_error_min=temporal_error,
            behavior_match=behavior_match,
            spatial_concordance=spatial_concordance,
            temporal_concordance=temporal_concordance,
            behavioral_concordance=behavioral_concordance,
            global_concordance=global_concordance,
            species=species,
            season=season
        )
        
        # Stocker
        self._comparisons[comparison_id] = result
        
        # Mettre à jour l'historique de précision
        self._update_precision_history()
        
        logger.info(f"Comparison created: {comparison_id} (concordance={global_concordance:.1f}%)")
        
        return result
    
    def _calculate_distance(
        self, lat1: float, lng1: float,
        lat2: float, lng2: float
    ) -> float:
        """Calcule la distance en mètres (Haversine)."""
        R = 6371000  # Rayon de la Terre
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def _calculate_spatial_concordance(self, error_m: float) -> float:
        """Calcule le score de concordance spatiale."""
        if error_m < 100:
            return 100.0
        elif error_m < 300:
            return 90.0 - (error_m - 100) * 0.05
        elif error_m < 500:
            return 80.0 - (error_m - 300) * 0.05
        elif error_m < 1000:
            return 70.0 - (error_m - 500) * 0.04
        else:
            return max(0, 50.0 - (error_m - 1000) * 0.01)
    
    def _calculate_temporal_concordance(self, error_min: float) -> float:
        """Calcule le score de concordance temporelle."""
        if error_min < 15:
            return 100.0
        elif error_min < 30:
            return 95.0 - (error_min - 15) * 0.33
        elif error_min < 60:
            return 90.0 - (error_min - 30) * 0.33
        elif error_min < 120:
            return 80.0 - (error_min - 60) * 0.33
        else:
            return max(0, 60.0 - (error_min - 120) * 0.25)
    
    # =========================================================================
    # GÉNÉRATION DE SUGGESTIONS
    # =========================================================================
    
    def generate_suggestions(
        self,
        current_service_weights: Dict[str, float],
        current_level_modifiers: Dict[str, float],
        current_thresholds: Dict[str, float]
    ) -> List[CalibrationSuggestion]:
        """
        Génère des suggestions d'ajustement basées sur les comparaisons.
        
        Analyse les écarts et propose des modifications ciblées.
        """
        if len(self._comparisons) < 5:
            logger.info("Not enough comparisons for suggestions (need >= 5)")
            return []
        
        suggestions = []
        comparisons = list(self._comparisons.values())
        
        # Analyser les erreurs par catégorie
        spatial_errors = [c.spatial_error_m for c in comparisons]
        temporal_errors = [c.temporal_error_min for c in comparisons]
        behavior_matches = [c.behavior_match for c in comparisons]
        
        avg_spatial = sum(spatial_errors) / len(spatial_errors)
        avg_temporal = sum(temporal_errors) / len(temporal_errors)
        behavior_rate = sum(1 for b in behavior_matches if b) / len(behavior_matches)
        
        # =====================================================================
        # 1. SUGGESTIONS POUR AMÉLIORER LA PRÉCISION SPATIALE
        # =====================================================================
        
        if avg_spatial > 300:  # Erreur spatiale moyenne > 300m
            # Suggérer d'augmenter le poids du service habitat
            current_habitat = current_service_weights.get("habitat", 0.12)
            suggested_habitat = min(0.20, current_habitat * 1.15)
            
            if suggested_habitat != current_habitat:
                suggestion = CalibrationSuggestion(
                    suggestion_id=self._generate_suggestion_id(),
                    adjustment_type=AdjustmentType.SERVICE_WEIGHT,
                    parameter_name="habitat",
                    parameter_category="service_weights",
                    current_value=current_habitat,
                    suggested_value=suggested_habitat,
                    change_delta=suggested_habitat - current_habitat,
                    change_percent=((suggested_habitat - current_habitat) / current_habitat) * 100,
                    justification=f"L'erreur spatiale moyenne ({avg_spatial:.0f}m) est élevée. "
                                  f"Augmenter le poids du service habitat devrait améliorer la localisation.",
                    precision_category=PrecisionCategory.SPATIAL,
                    expected_impact=2.5,
                    confidence=0.7,
                    observations_count=len(comparisons),
                    avg_error_before=avg_spatial
                )
                suggestions.append(suggestion)
                self._suggestions[suggestion.suggestion_id] = suggestion
        
        # =====================================================================
        # 2. SUGGESTIONS POUR AMÉLIORER LA PRÉCISION COMPORTEMENTALE
        # =====================================================================
        
        if behavior_rate < 0.7:  # Taux de correspondance comportementale < 70%
            current_behavior = current_service_weights.get("behavior", 0.12)
            suggested_behavior = min(0.18, current_behavior * 1.20)
            
            if suggested_behavior != current_behavior:
                suggestion = CalibrationSuggestion(
                    suggestion_id=self._generate_suggestion_id(),
                    adjustment_type=AdjustmentType.SERVICE_WEIGHT,
                    parameter_name="behavior",
                    parameter_category="service_weights",
                    current_value=current_behavior,
                    suggested_value=suggested_behavior,
                    change_delta=suggested_behavior - current_behavior,
                    change_percent=((suggested_behavior - current_behavior) / current_behavior) * 100,
                    justification=f"Le taux de concordance comportementale ({behavior_rate*100:.0f}%) est faible. "
                                  f"Renforcer le service behavior devrait améliorer les prédictions.",
                    precision_category=PrecisionCategory.BEHAVIORAL,
                    expected_impact=3.0,
                    confidence=0.75,
                    observations_count=len(comparisons),
                    avg_error_before=behavior_rate
                )
                suggestions.append(suggestion)
                self._suggestions[suggestion.suggestion_id] = suggestion
        
        # =====================================================================
        # 3. SUGGESTIONS POUR LES MODIFICATEURS DE NIVEAU
        # =====================================================================
        
        # Analyser par espèce
        by_species = {}
        for c in comparisons:
            sp = c.species or "unknown"
            if sp not in by_species:
                by_species[sp] = []
            by_species[sp].append(c.global_concordance)
        
        for species, concordances in by_species.items():
            avg_concordance = sum(concordances) / len(concordances)
            if avg_concordance < 70 and species != "unknown":
                # Suggérer d'ajuster le modificateur de mobilité pour cette espèce
                current_mobility = current_level_modifiers.get("niveau_5_mobility", 1.0)
                suggested_mobility = current_mobility * 1.10
                
                suggestion = CalibrationSuggestion(
                    suggestion_id=self._generate_suggestion_id(),
                    adjustment_type=AdjustmentType.LEVEL_MODIFIER,
                    parameter_name="niveau_5_mobility",
                    parameter_category="level_modifiers",
                    current_value=current_mobility,
                    suggested_value=suggested_mobility,
                    change_delta=suggested_mobility - current_mobility,
                    change_percent=10.0,
                    justification=f"La concordance pour {species} ({avg_concordance:.0f}%) est insuffisante. "
                                  f"Ajuster le modificateur de mobilité peut aider.",
                    precision_category=PrecisionCategory.GLOBAL,
                    expected_impact=2.0,
                    confidence=0.65,
                    observations_count=len(concordances),
                    avg_error_before=100 - avg_concordance
                )
                suggestions.append(suggestion)
                self._suggestions[suggestion.suggestion_id] = suggestion
        
        logger.info(f"Generated {len(suggestions)} calibration suggestions")
        return suggestions
    
    # =========================================================================
    # VALIDATION ET APPLICATION
    # =========================================================================
    
    def approve_suggestion(
        self,
        suggestion_id: str,
        validated_by: str,
        notes: str = ""
    ) -> Optional[CalibrationSuggestion]:
        """
        Approuve une suggestion (validation manuelle obligatoire).
        """
        suggestion = self._suggestions.get(suggestion_id)
        if suggestion and suggestion.status == AdjustmentStatus.PENDING:
            suggestion.status = AdjustmentStatus.APPROVED
            suggestion.validated_by = validated_by
            suggestion.validated_at = datetime.now(timezone.utc)
            suggestion.validation_notes = notes
            
            logger.info(f"Suggestion approved: {suggestion_id} by {validated_by}")
            return suggestion
        return None
    
    def reject_suggestion(
        self,
        suggestion_id: str,
        validated_by: str,
        reason: str = ""
    ) -> Optional[CalibrationSuggestion]:
        """
        Rejette une suggestion.
        """
        suggestion = self._suggestions.get(suggestion_id)
        if suggestion and suggestion.status == AdjustmentStatus.PENDING:
            suggestion.status = AdjustmentStatus.REJECTED
            suggestion.validated_by = validated_by
            suggestion.validated_at = datetime.now(timezone.utc)
            suggestion.validation_notes = reason
            
            logger.info(f"Suggestion rejected: {suggestion_id} by {validated_by}")
            return suggestion
        return None
    
    def apply_approved_suggestions(self) -> Dict[str, Any]:
        """
        Applique toutes les suggestions approuvées.
        
        Retourne les nouveaux paramètres à appliquer au CalibrationProfile.
        """
        approved = [s for s in self._suggestions.values() if s.status == AdjustmentStatus.APPROVED]
        
        if not approved:
            return {"applied": 0, "adjustments": {}}
        
        adjustments = {
            "service_weights": {},
            "level_modifiers": {},
            "thresholds": {}
        }
        
        for suggestion in approved:
            suggestion.status = AdjustmentStatus.APPLIED
            suggestion.applied_at = datetime.now(timezone.utc)
            
            category = suggestion.parameter_category
            if category in adjustments:
                adjustments[category][suggestion.parameter_name] = suggestion.suggested_value
        
        logger.info(f"Applied {len(approved)} calibration adjustments")
        
        return {
            "applied": len(approved),
            "adjustments": adjustments,
            "suggestions_applied": [s.suggestion_id for s in approved]
        }
    
    # =========================================================================
    # DASHBOARD DATA
    # =========================================================================
    
    def get_dashboard_data(self) -> CalibrationDashboardData:
        """
        Génère les données pour le dashboard de calibration.
        """
        comparisons = list(self._comparisons.values())
        
        data = CalibrationDashboardData()
        
        if comparisons:
            # Précision globale
            concordances = [c.global_concordance for c in comparisons]
            data.global_precision = sum(concordances) / len(concordances)
            data.precision_gap = data.target_precision - data.global_precision
            
            # Précision par catégorie
            data.spatial_precision = sum(c.spatial_concordance for c in comparisons) / len(comparisons)
            data.temporal_precision = sum(c.temporal_concordance for c in comparisons) / len(comparisons)
            data.behavioral_precision = sum(c.behavioral_concordance for c in comparisons) / len(comparisons)
            
            # Par espèce
            by_species = {}
            for c in comparisons:
                sp = c.species or "unknown"
                if sp not in by_species:
                    by_species[sp] = []
                by_species[sp].append(c.global_concordance)
            data.by_species = {sp: sum(v)/len(v) for sp, v in by_species.items()}
            
            # Par comportement
            by_behavior = {}
            for c in comparisons:
                bh = c.observed_behavior or "unknown"
                if bh not in by_behavior:
                    by_behavior[bh] = []
                by_behavior[bh].append(c.global_concordance)
            data.by_behavior = {bh: sum(v)/len(v) for bh, v in by_behavior.items()}
        
        # Statistiques
        data.total_comparisons = len(comparisons)
        data.total_observations = len(comparisons)  # Approximation
        
        # Comparaisons cette semaine
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        data.observations_this_week = len([
            c for c in comparisons if c.calculated_at > week_ago
        ])
        
        # Tendance
        data.precision_trend = self._precision_history[-30:]  # 30 derniers points
        
        # Suggestions en attente
        data.pending_suggestions = len([
            s for s in self._suggestions.values() if s.status == AdjustmentStatus.PENDING
        ])
        
        # Statut MASTER
        data.is_master_ready = data.global_precision >= 95.0
        if not data.is_master_ready and data.total_comparisons > 0:
            # Estimation grossière du nombre de comparaisons nécessaires
            gap_to_close = data.precision_gap
            avg_improvement_per_10 = 1.5  # Hypothèse: +1.5% par 10 comparaisons calibrées
            data.estimated_comparisons_to_master = int((gap_to_close / avg_improvement_per_10) * 10)
        
        return data
    
    def _update_precision_history(self):
        """Met à jour l'historique de précision."""
        if self._comparisons:
            comparisons = list(self._comparisons.values())
            avg_precision = sum(c.global_concordance for c in comparisons) / len(comparisons)
            
            self._precision_history.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "precision": round(avg_precision, 1),
                "comparisons_count": len(comparisons)
            })
            
            # Garder les 100 derniers points
            self._precision_history = self._precision_history[-100:]
    
    # =========================================================================
    # ACCESSORS
    # =========================================================================
    
    def get_comparison(self, comparison_id: str) -> Optional[ComparisonResult]:
        """Récupère une comparaison."""
        return self._comparisons.get(comparison_id)
    
    def list_comparisons(self, limit: int = 100) -> List[ComparisonResult]:
        """Liste les comparaisons."""
        comparisons = list(self._comparisons.values())
        comparisons.sort(key=lambda x: x.calculated_at, reverse=True)
        return comparisons[:limit]
    
    def get_suggestion(self, suggestion_id: str) -> Optional[CalibrationSuggestion]:
        """Récupère une suggestion."""
        return self._suggestions.get(suggestion_id)
    
    def list_suggestions(
        self,
        status: Optional[AdjustmentStatus] = None
    ) -> List[CalibrationSuggestion]:
        """Liste les suggestions."""
        suggestions = list(self._suggestions.values())
        if status:
            suggestions = [s for s in suggestions if s.status == status]
        suggestions.sort(key=lambda x: x.created_at, reverse=True)
        return suggestions
    
    def get_stats(self) -> Dict[str, Any]:
        """Statistiques de l'optimiseur."""
        pending = len([s for s in self._suggestions.values() if s.status == AdjustmentStatus.PENDING])
        approved = len([s for s in self._suggestions.values() if s.status == AdjustmentStatus.APPROVED])
        applied = len([s for s in self._suggestions.values() if s.status == AdjustmentStatus.APPLIED])
        
        return {
            "version": self._version,
            "comparisons_count": len(self._comparisons),
            "suggestions": {
                "total": len(self._suggestions),
                "pending": pending,
                "approved": approved,
                "applied": applied
            },
            "precision_history_points": len(self._precision_history)
        }


# =============================================================================
# SINGLETON
# =============================================================================

_optimizer_instance: Optional[CalibrationOptimizer] = None


def get_calibration_optimizer() -> CalibrationOptimizer:
    """Obtenir l'instance singleton de l'optimiseur."""
    global _optimizer_instance
    if _optimizer_instance is None:
        _optimizer_instance = CalibrationOptimizer()
    return _optimizer_instance


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    'AdjustmentType',
    'AdjustmentStatus',
    'PrecisionCategory',
    # Models
    'CalibrationSuggestion',
    'ComparisonResult',
    'CalibrationDashboardData',
    # Optimizer
    'CalibrationOptimizer',
    'get_calibration_optimizer'
]
