"""
BIONIC ENGINE — Unified Scoring Service
========================================
Orchestrateur central des 9 services de scoring BIONIC V5 ULTIME.

RESPONSABILITÉ UNIQUE:
- Orchestrer les 9 services de scoring
- Appliquer le temporal_factor (LegalHoursService)
- Agréger les scores via ScoreWeight
- Produire un ScoreFinalResult standardisé

ISOLATION:
- Aucun calcul interne aux services (appel uniquement)
- Aucun lien direct avec WQS ou BIONIC_SCORE existants
- Communication via interfaces publiques uniquement

INPUTS:
- ScoreContext (waypoint-centric)

OUTPUTS:
- UnifiedScoreResult (score final agrégé + détail par service)

Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

# Import des 9 services de scoring (via package)
from modules.bionic_engine_p0.services.scoring import (
    ScoreContext,
    ScoreResult,
    ScoreLevel,
    ScoreCategory,
    ScoreProbabilityService,
    ScoreHabitatService,
    ScorePressureService,
    ScoreWeatherService,
    ScoreBehaviorService,
    ScoreMultiFactorService,
    ScoreDensityService,
    ScoreRiskService,
    ScoreMobilityService
)

# Import du service des heures légales
from modules.bionic_engine_p0.services.legal_hours_service import (
    get_legal_hours_service,
    LegalHoursService,
    LegalHuntingWindow,
    LegalStatus
)

logger = logging.getLogger(__name__)


# =============================================================================
# DATA CONTRACTS
# =============================================================================

@dataclass
class ScoreBreakdown:
    """Détail d'un score individuel dans l'agrégation."""
    category: ScoreCategory
    score_name: str
    raw_value: float           # 0-100
    weight: float              # 0-1
    weighted_value: float      # raw_value * weight
    level: ScoreLevel
    components_count: int
    confidence: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category.value,
            "score_name": self.score_name,
            "raw_value": round(self.raw_value, 1),
            "weight": round(self.weight, 3),
            "weighted_value": round(self.weighted_value, 2),
            "level": self.level.value,
            "components_count": self.components_count,
            "confidence": round(self.confidence, 2)
        }


@dataclass
class TemporalAdjustment:
    """Ajustement temporel appliqué au score."""
    is_legal_period: bool
    legal_status: LegalStatus
    temporal_factor: float      # 0-1
    legal_window: Optional[LegalHuntingWindow]
    adjustment_applied: float   # Différence appliquée
    legal_badge: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_legal_period": self.is_legal_period,
            "legal_status": self.legal_status.value,
            "temporal_factor": round(self.temporal_factor, 3),
            "legal_window": self.legal_window.to_dict() if self.legal_window else None,
            "adjustment_applied": round(self.adjustment_applied, 2),
            "legal_badge": self.legal_badge
        }


@dataclass
class UnifiedScoreResult:
    """
    Résultat final du scoring unifié.
    
    Combine les 9 scores canoniques avec l'ajustement temporel
    pour produire un score final unique.
    """
    # Identification
    score_id: str
    calculated_at: datetime
    
    # Score final
    final_score: float          # 0-100 (après ajustement temporel)
    final_level: ScoreLevel
    
    # Score brut (avant ajustement)
    raw_aggregated_score: float
    
    # Ajustement temporel
    temporal_adjustment: TemporalAdjustment
    
    # Détail des 9 scores
    score_breakdown: List[ScoreBreakdown]
    
    # Facteurs positifs/négatifs agrégés
    top_positive_factors: List[str]
    top_negative_factors: List[str]
    
    # Confiance globale
    global_confidence: float
    data_quality: str           # full, partial, minimal
    
    # Contexte d'entrée
    context: ScoreContext
    
    # Métadonnées
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "score_id": self.score_id,
            "calculated_at": self.calculated_at.isoformat(),
            "final_score": round(self.final_score, 1),
            "final_level": self.final_level.value,
            "raw_aggregated_score": round(self.raw_aggregated_score, 1),
            "temporal_adjustment": self.temporal_adjustment.to_dict(),
            "score_breakdown": [s.to_dict() for s in self.score_breakdown],
            "top_positive_factors": self.top_positive_factors,
            "top_negative_factors": self.top_negative_factors,
            "global_confidence": round(self.global_confidence, 2),
            "data_quality": self.data_quality,
            "context": self.context.to_dict(),
            "metadata": self.metadata
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
# UNIFIED SCORING SERVICE
# =============================================================================

class UnifiedScoringService:
    """
    Service d'orchestration du scoring unifié BIONIC V5 ULTIME.
    
    RESPONSABILITÉ:
    - Instancier et appeler les 9 services de scoring
    - Collecter les ScoreResult de chaque service
    - Agréger les scores via les pondérations (ScoreWeight)
    - Appliquer l'ajustement temporel (LegalHoursService)
    - Produire un UnifiedScoreResult standardisé
    
    ISOLATION:
    - N'effectue AUCUN calcul interne aux services
    - Appelle uniquement les méthodes publiques
    - Ne modifie pas les services existants
    """
    
    def __init__(self):
        """Initialise le service avec les 9 services de scoring."""
        # Instanciation des 9 services (isolés)
        self._services = [
            ScoreProbabilityService(),
            ScoreHabitatService(),
            ScorePressureService(),
            ScoreWeatherService(),
            ScoreBehaviorService(),
            ScoreMultiFactorService(),
            ScoreDensityService(),
            ScoreRiskService(),
            ScoreMobilityService()
        ]
        
        # Service des heures légales
        self._legal_hours_service = get_legal_hours_service()
        
        # Compteur pour les IDs
        self._score_counter = 0
        
        logger.info(f"UnifiedScoringService initialized with {len(self._services)} services")
    
    def _generate_score_id(self) -> str:
        """Génère un ID unique pour le score."""
        self._score_counter += 1
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"UNI-{timestamp}-{self._score_counter:04d}"
    
    @property
    def services(self) -> list:
        """Liste des services de scoring (lecture seule)."""
        return self._services.copy()
    
    @property
    def services_count(self) -> int:
        """Nombre de services de scoring."""
        return len(self._services)
    
    def get_total_weight(self) -> float:
        """Retourne la somme des pondérations (doit être ~1.0)."""
        return sum(s.weight.weight for s in self._services)
    
    def calculate_unified_score(self, context: ScoreContext) -> UnifiedScoreResult:
        """
        Calcule le score unifié pour un contexte donné.
        
        PROCESSUS:
        1. Appeler chaque service de scoring avec le contexte
        2. Collecter les ScoreResult
        3. Calculer le score brut agrégé (somme pondérée)
        4. Calculer l'ajustement temporel (LegalHoursService)
        5. Appliquer l'ajustement au score brut
        6. Produire le UnifiedScoreResult
        
        Args:
            context: Contexte waypoint-centric
            
        Returns:
            UnifiedScoreResult avec score final et détails
        """
        start_time = datetime.now(timezone.utc)
        score_id = self._generate_score_id()
        
        logger.info(f"[{score_id}] Starting unified score calculation")
        logger.debug(f"[{score_id}] Context: waypoint={context.waypoint_id}, species={context.species}")
        
        # ==== ÉTAPE 1: Appeler chaque service ====
        service_results: List[ScoreResult] = []
        
        for service in self._services:
            try:
                result = service.calculate(context)
                service_results.append(result)
                logger.debug(f"[{score_id}] {service.category.value}: {result.value:.1f}")
            except Exception as e:
                logger.error(f"[{score_id}] Error in {service.category.value}: {e}")
                # Créer un résultat d'erreur
                service_results.append(self._create_error_result(service, context, str(e)))
        
        # ==== ÉTAPE 2: Construire les breakdowns ====
        breakdowns = self._build_score_breakdowns(service_results)
        
        # ==== ÉTAPE 3: Calculer le score brut agrégé ====
        raw_score = self._calculate_aggregated_score(service_results)
        
        logger.info(f"[{score_id}] Raw aggregated score: {raw_score:.1f}")
        
        # ==== ÉTAPE 4: Calculer l'ajustement temporel ====
        temporal_adj = self._calculate_temporal_adjustment(context)
        
        # ==== ÉTAPE 5: Appliquer l'ajustement ====
        final_score = self._apply_temporal_adjustment(raw_score, temporal_adj)
        
        logger.info(f"[{score_id}] Final score (after temporal): {final_score:.1f}")
        
        # ==== ÉTAPE 6: Agréger les facteurs ====
        positive_factors, negative_factors = self._aggregate_factors(service_results)
        
        # ==== ÉTAPE 7: Calculer la confiance globale ====
        global_confidence = self._calculate_global_confidence(service_results)
        data_quality = self._assess_data_quality(service_results)
        
        # ==== ÉTAPE 8: Construire le résultat final ====
        calc_time_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        
        result = UnifiedScoreResult(
            score_id=score_id,
            calculated_at=datetime.now(timezone.utc),
            final_score=final_score,
            final_level=UnifiedScoreResult.get_level_from_value(final_score),
            raw_aggregated_score=raw_score,
            temporal_adjustment=temporal_adj,
            score_breakdown=breakdowns,
            top_positive_factors=positive_factors[:5],
            top_negative_factors=negative_factors[:5],
            global_confidence=global_confidence,
            data_quality=data_quality,
            context=context,
            metadata={
                "calculation_time_ms": round(calc_time_ms, 1),
                "services_count": len(self._services),
                "total_weight": round(self.get_total_weight(), 3),
                "version": "BIONIC-V5-ULTIME-1.0"
            }
        )
        
        logger.info(f"[{score_id}] Unified score completed in {calc_time_ms:.0f}ms")
        
        return result
    
    def _build_score_breakdowns(self, results: List[ScoreResult]) -> List[ScoreBreakdown]:
        """Construit les détails de chaque score."""
        breakdowns = []
        
        for i, result in enumerate(results):
            service = self._services[i]
            
            breakdown = ScoreBreakdown(
                category=result.category,
                score_name=result.score_name,
                raw_value=result.value,
                weight=service.weight.weight,
                weighted_value=result.value * service.weight.weight,
                level=result.level,
                components_count=len(result.components),
                confidence=result.confidence
            )
            breakdowns.append(breakdown)
        
        return breakdowns
    
    def _calculate_aggregated_score(self, results: List[ScoreResult]) -> float:
        """
        Calcule le score agrégé pondéré.
        
        Formule: Σ(score_i × weight_i) / Σ(weight_i)
        """
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for i, result in enumerate(results):
            weight = self._services[i].weight.weight
            total_weighted_score += result.value * weight
            total_weight += weight
        
        if total_weight > 0:
            return total_weighted_score / total_weight
        else:
            return 50.0  # Score neutre par défaut
    
    def _calculate_temporal_adjustment(self, context: ScoreContext) -> TemporalAdjustment:
        """
        Calcule l'ajustement temporel via LegalHoursService.
        
        RÈGLE BIONIC V5:
        - temporal_factor = 0 si hors heures légales
        - Le score final est modulé par ce facteur
        """
        # Vérifier le statut légal
        check_result = self._legal_hours_service.check_legal_status(
            target_time=context.target_datetime,
            latitude=context.latitude,
            longitude=context.longitude,
            region=context.region
        )
        
        # Calculer le temporal_factor
        temporal_factor = self._legal_hours_service.calculate_temporal_factor(
            target_time=context.target_datetime,
            latitude=context.latitude,
            longitude=context.longitude,
            region=context.region
        )
        
        # Déterminer le badge
        if check_result.is_legal:
            if temporal_factor >= 0.9:
                legal_badge = "⚖️ LÉGAL - OPTIMAL"
            else:
                legal_badge = "⚖️ LÉGAL"
        else:
            legal_badge = "❌ HORS HEURES LÉGALES"
        
        return TemporalAdjustment(
            is_legal_period=check_result.is_legal,
            legal_status=check_result.status,
            temporal_factor=temporal_factor,
            legal_window=check_result.legal_window,
            adjustment_applied=(1 - temporal_factor) * 100,  # En points perdus
            legal_badge=legal_badge
        )
    
    def _apply_temporal_adjustment(
        self, 
        raw_score: float, 
        temporal_adj: TemporalAdjustment
    ) -> float:
        """
        Applique l'ajustement temporel au score brut.
        
        RÈGLE BIONIC V5:
        - Si hors heures légales: temporal_factor = 0, donc score = 0
        - Sinon: score modulé par le facteur temporel
        
        Formule: final = raw × (0.7 + 0.3 × temporal_factor)
        - Le facteur temporel peut réduire le score jusqu'à 30%
        - À l'aube/crépuscule (factor=0.95), réduction minimale
        - À midi (factor=0.3), réduction de ~21%
        """
        if not temporal_adj.is_legal_period:
            # RÈGLE STRICTE: Score = 0 hors heures légales
            return 0.0
        
        # Modulation: 70% fixe + 30% variable selon temporal_factor
        modulation = 0.7 + (0.3 * temporal_adj.temporal_factor)
        
        return raw_score * modulation
    
    def _aggregate_factors(
        self, 
        results: List[ScoreResult]
    ) -> tuple[List[str], List[str]]:
        """Agrège les facteurs positifs et négatifs de tous les scores."""
        all_positive = []
        all_negative = []
        
        for result in results:
            all_positive.extend(result.positive_factors)
            all_negative.extend(result.negative_factors)
        
        # Dédupliquer et limiter
        unique_positive = list(dict.fromkeys(all_positive))
        unique_negative = list(dict.fromkeys(all_negative))
        
        return unique_positive, unique_negative
    
    def _calculate_global_confidence(self, results: List[ScoreResult]) -> float:
        """Calcule la confiance globale moyenne pondérée."""
        total_confidence = 0.0
        total_weight = 0.0
        
        for i, result in enumerate(results):
            weight = self._services[i].weight.weight
            total_confidence += result.confidence * weight
            total_weight += weight
        
        if total_weight > 0:
            return total_confidence / total_weight
        else:
            return 0.5
    
    def _assess_data_quality(self, results: List[ScoreResult]) -> str:
        """Évalue la qualité globale des données."""
        qualities = [r.data_quality for r in results]
        
        full_count = qualities.count("full")
        partial_count = qualities.count("partial")
        minimal_count = qualities.count("minimal")
        
        if full_count >= 7:
            return "full"
        elif minimal_count >= 5:
            return "minimal"
        else:
            return "partial"
    
    def _create_error_result(
        self, 
        service, 
        context: ScoreContext, 
        error: str
    ) -> ScoreResult:
        """Crée un ScoreResult d'erreur pour un service défaillant."""
        return ScoreResult(
            category=service.category,
            score_name=service._get_score_name(),
            value=0.0,
            level=ScoreLevel.VERY_POOR,
            components=[],
            positive_factors=[],
            negative_factors=[f"Erreur: {error}"],
            confidence=0.0,
            data_quality="minimal",
            context=context
        )


# =============================================================================
# SINGLETON
# =============================================================================

_unified_scoring_service: Optional[UnifiedScoringService] = None


def get_unified_scoring_service() -> UnifiedScoringService:
    """Retourne l'instance singleton du service."""
    global _unified_scoring_service
    if _unified_scoring_service is None:
        _unified_scoring_service = UnifiedScoringService()
    return _unified_scoring_service


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'UnifiedScoringService',
    'get_unified_scoring_service',
    'UnifiedScoreResult',
    'ScoreBreakdown',
    'TemporalAdjustment'
]
