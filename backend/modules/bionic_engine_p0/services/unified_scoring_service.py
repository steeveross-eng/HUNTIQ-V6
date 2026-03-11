"""
BIONIC ENGINE — Unified Scoring Service
========================================
Orchestrateur central des 9 services de scoring BIONIC V5 ULTIME.

RESPONSABILITÉ UNIQUE:
- Orchestrer les 9 services de scoring
- Appliquer le temporal_factor (LegalHoursService)
- Intégrer les facteurs avancés (PHASE B)
- Appliquer les modificateurs de période biologique (PRE_RUT, RUT, POST_RUT)
- Agréger les scores via ScoreWeight
- Produire un ScoreFinalResult standardisé

ISOLATION:
- Aucun calcul interne aux services (appel uniquement)
- Aucun lien direct avec WQS ou BIONIC_SCORE existants
- Communication via interfaces publiques uniquement

INPUTS:
- ScoreContext (waypoint-centric)
- analysis_mode: 'live', 'pre_rut', 'rut', 'post_rut'

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
    LegalHuntingWindow,
    LegalStatus
)

# Import des facteurs avancés (PHASE B)
from modules.bionic_engine_p0.knowledge.species.advanced_factors import (
    get_advanced_factors_registry,
    SocialRank
)

# Import des modèles saisonniers (PHASE C)
from modules.bionic_engine_p0.knowledge.seasonal.seasonal_models import (
    get_seasonal_model,
    SeasonType
)

# Import du modèle de pression humaine (NIVEAU 3 - PRES-HUMAN)
from modules.bionic_engine_p0.knowledge.human_pressure import (
    get_human_pressure_registry
)

# Import du module des corridors (NIVEAU 4 - Habitat & Corridors)
from modules.bionic_engine_p0.knowledge.corridors import (
    get_corridor_registry,
    CorridorNetwork
)

# Import du module de mobilité (NIVEAU 5 - Mobilité Dynamique)
from modules.bionic_engine_p0.knowledge.mobility import (
    get_mobility_registry
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
    
    Combine les 9 scores canoniques avec:
    - L'ajustement temporel
    - Les facteurs avancés (PHASE B)
    - Le mode d'analyse biologique (PRE_RUT, RUT, POST_RUT, LIVE)
    """
    # Identification
    score_id: str
    calculated_at: datetime
    
    # Score final (requis)
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
    
    # Mode d'analyse (défaut = rut)
    analysis_mode: str = "rut"  # 'live', 'pre_rut', 'rut', 'post_rut'
    
    # Facteurs avancés (PHASE B) - avec defaults
    advanced_factors_modifier: float = 1.0
    advanced_factors_details: Dict[str, Any] = field(default_factory=dict)
    
    # Métadonnées
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "score_id": self.score_id,
            "calculated_at": self.calculated_at.isoformat(),
            "analysis_mode": self.analysis_mode,
            "final_score": round(self.final_score, 1),
            "final_level": self.final_level.value,
            "raw_aggregated_score": round(self.raw_aggregated_score, 1),
            "temporal_adjustment": self.temporal_adjustment.to_dict(),
            "advanced_factors_modifier": round(self.advanced_factors_modifier, 3),
            "advanced_factors_details": self.advanced_factors_details,
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
    - Intégrer les facteurs avancés (PHASE B)
    - Appliquer les modificateurs de période biologique
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
        """Initialise le service avec les 9 services de scoring et facteurs avancés."""
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
        
        # Registre des facteurs avancés (PHASE B)
        self._advanced_factors = get_advanced_factors_registry()
        
        # Registre de pression humaine (NIVEAU 3 - PRES-HUMAN)
        self._human_pressure = get_human_pressure_registry()
        
        # Registre des corridors (NIVEAU 4 - Habitat & Corridors)
        self._corridor_registry = get_corridor_registry()
        
        # Registre de mobilité (NIVEAU 5 - Mobilité Dynamique)
        self._mobility_registry = get_mobility_registry()
        
        # Compteur pour les IDs
        self._score_counter = 0
        
        logger.info(f"UnifiedScoringService initialized with {len(self._services)} services + Advanced Factors + PRES-HUMAN + Corridors + Mobility (NIVEAU 5)")
    
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
    
    def _get_biological_period_modifier(
        self,
        species: str,
        region: str,
        analysis_mode: str
    ) -> tuple:
        """
        Obtenir le modificateur de période biologique.
        
        Returns:
            Tuple[modifier, period_info, source_ids]
        """
        seasonal_model = get_seasonal_model(species, region)
        if not seasonal_model:
            return 1.0, {}, []
        
        mode_to_season = {
            "pre_rut": SeasonType.PRE_RUT,
            "rut": SeasonType.RUT,
            "post_rut": SeasonType.POST_RUT,
            "live": None  # Mode LIVE utilise la saison courante
        }
        
        target_season = mode_to_season.get(analysis_mode)
        
        if target_season:
            period = seasonal_model.periods.get(target_season)
            if period:
                return period.activity_modifier, {
                    "season": target_season.value,
                    "vulnerability": period.vulnerability_modifier,
                    "movement": period.movement_modifier,
                    "feeding": period.feeding_modifier
                }, period.source_ids
        
        # Pour ours noir, utiliser hyperphagia comme "rut equivalent"
        if "bear" in species.lower() or "ours" in species.lower():
            if analysis_mode in ["rut", "pre_rut", "post_rut"]:
                hyperphagia = seasonal_model.periods.get(SeasonType.HYPERPHAGIA)
                if hyperphagia:
                    return hyperphagia.activity_modifier, {
                        "season": "hyperphagia",
                        "feeding": hyperphagia.feeding_modifier
                    }, hyperphagia.source_ids
        
        return 1.0, {"season": "default"}, []
    
    def _inject_advanced_modifiers(
        self,
        context: ScoreContext,
        analysis_mode: str,
        score_id: str
    ) -> ScoreContext:
        """
        PHASE B - CENTRALISATION ABSOLUE
        
        Calcule TOUS les modificateurs avancés et les injecte dans le contexte.
        Les services CONSOMMENT ces valeurs - AUCUNE logique locale autorisée.
        
        Cette méthode est le SEUL point de calcul des modificateurs avancés.
        
        Args:
            context: Contexte original
            analysis_mode: Mode d'analyse (live, pre_rut, rut, post_rut)
            score_id: ID du score pour logging
            
        Returns:
            ScoreContext enrichi avec advanced_modifiers
        """
        hour = context.target_datetime.hour
        season = self._get_current_season_name(context)
        extra_data = context.extra_data or {}
        
        # =====================================================================
        # 1. HIÉRARCHIE SOCIALE (source: Knowledge Layer)
        # =====================================================================
        social_rank_str = extra_data.get("social_rank", "unknown")
        try:
            social_rank = SocialRank(social_rank_str)
        except ValueError:
            social_rank = SocialRank.UNKNOWN
        
        is_rut = season in ["rut", "pre_rut"]
        social_modifier, social_sources = self._advanced_factors.get_social_modifier(
            species=context.species,
            social_rank=social_rank,
            season=season,
            is_rut=is_rut
        )
        
        # =====================================================================
        # 2. COMPÉTITION INTER-ESPÈCES (source: Knowledge Layer)
        # =====================================================================
        competitors = extra_data.get("competitors_present", [])
        habitat = extra_data.get("habitat_type", "mixed_forest")
        
        competition_modifier, competition_sources = self._advanced_factors.get_competition_score_modifier(
            species=context.species,
            competitors_present=competitors,
            habitat=habitat
        )
        
        # =====================================================================
        # 3. CYCLES DIGESTIFS (source: Knowledge Layer)
        # =====================================================================
        digestive_cycle, digestive_sources = self._advanced_factors.get_current_digestive_phase(
            species=context.species,
            hour=hour
        )
        
        if digestive_cycle:
            # DigestiveCycle doesn't have activity_modifier, compute from mobility_level
            # Higher mobility = higher activity modifier
            digestive_modifier = 0.5 + (digestive_cycle.mobility_level * 0.5)  # Range: 0.5 to 1.0
            digestive_phase = digestive_cycle.phase.value
            digestive_mobility = digestive_cycle.mobility_level
            digestive_visibility = digestive_cycle.visibility_during_phase
        else:
            digestive_modifier = 1.0
            digestive_phase = "unknown"
            digestive_mobility = 0.5
            digestive_visibility = 0.5
        
        # =====================================================================
        # 4. SIGNAUX FAIBLES (source: Knowledge Layer)
        # =====================================================================
        observed_indicators = extra_data.get("observed_indicators", [])
        
        signals_impact, detected_signals, signals_sources = self._advanced_factors.evaluate_weak_signals(
            species=context.species,
            observed_indicators=observed_indicators
        )
        
        signals_modifier = 1.0 + (signals_impact / 100)  # Convertir impact en modificateur
        signals_detected_names = [s.signal_type.value for s in detected_signals]
        
        # =====================================================================
        # 5. PHASE C: MODIFICATEURS PHÉNOLOGIQUES AVANCÉS
        # =====================================================================
        seasonal_model = get_seasonal_model(context.species)
        target_date = context.target_datetime.date()
        
        # Initialisation des modificateurs PHASE C
        dispersal_active = False
        dispersal_modifier = 1.0
        dispersal_variance = 0.0
        dispersal_sources = []
        dispersal_window_info = None
        
        thermal_stress_active = False
        thermal_stress_modifier = 1.0
        thermal_sources = []
        
        hunting_pressure_active = False
        hunting_pressure_modifier = 1.0
        hunting_pressure_sources = []
        pres_human_details = {}  # NIVEAU 3 - Initialisé vide
        
        if seasonal_model:
            # 5.1 DISPERSION JUVÉNILE DYNAMIQUE (10-14 mois après naissance)
            is_dispersal, dispersal_window = seasonal_model.is_in_dynamic_dispersal(target_date)
            if is_dispersal and dispersal_window:
                dispersal_active = True
                dispersal_modifier = dispersal_window.movement_modifier
                dispersal_variance = dispersal_window.movement_variance
                dispersal_sources = dispersal_window.source_ids
                dispersal_window_info = {
                    "birth_date": dispersal_window.birth_date.isoformat(),
                    "dispersal_start": dispersal_window.dispersal_start.isoformat(),
                    "dispersal_end": dispersal_window.dispersal_end.isoformat(),
                    "version": dispersal_window.version
                }
            
            # 5.2 STRESS THERMIQUE (températures à partir de extra_data)
            temperature_c = extra_data.get("temperature_c")
            phase_c_mods = seasonal_model.get_phase_c_modifiers(
                check_date=target_date,
                temperature_c=temperature_c,
                hunting_pressure_detected=extra_data.get("hunting_pressure_detected", False)
            )
            
            thermal_stress_active = phase_c_mods.get("thermal_stress_active", False)
            thermal_stress_modifier = phase_c_mods.get("thermal_stress_modifier", 1.0)
            thermal_sources = phase_c_mods.get("thermal_source_ids", [])
            
            # 5.3 PRESSION DE CHASSE RÉELLE (NIVEAU 3 - PRES-HUMAN)
            # Utilise le nouveau HumanPressureRegistry pour un calcul complet
            hunting_pressure_detected = extra_data.get("hunting_pressure_detected", False)
            latitude = extra_data.get("latitude", 46.8)
            longitude = extra_data.get("longitude", -71.2)
            
            pres_human_modifier, pres_human_details, pres_human_sources = self._human_pressure.get_hunting_pressure_modifier(
                species=context.species,
                latitude=latitude,
                longitude=longitude,
                check_datetime=context.target_datetime,
                hunting_pressure_detected=hunting_pressure_detected
            )
            
            hunting_pressure_active = pres_human_details.get("intensity") != "none"
            hunting_pressure_modifier = pres_human_modifier
            hunting_pressure_sources = pres_human_sources
            
            # Collecter les source_ids PHASE C
            dispersal_sources.extend(phase_c_mods.get("source_ids", []))
        else:
            # Fallback si pas de modèle saisonnier: utiliser PRES-HUMAN seul
            pres_human_modifier, pres_human_details, pres_human_sources = self._human_pressure.get_hunting_pressure_modifier(
                species=context.species,
                latitude=extra_data.get("latitude", 46.8),
                longitude=extra_data.get("longitude", -71.2),
                check_datetime=context.target_datetime,
                hunting_pressure_detected=extra_data.get("hunting_pressure_detected", False)
            )
            hunting_pressure_active = pres_human_details.get("intensity") != "none"
            hunting_pressure_modifier = pres_human_modifier
            hunting_pressure_sources = pres_human_sources
            thermal_sources = []
        
        # =====================================================================
        # 5.5 NIVEAU 5: MOBILITÉ DYNAMIQUE
        # =====================================================================
        # Calculer d'abord le modificateur de phase C
        phase_c_modifier_temp = dispersal_modifier * thermal_stress_modifier * hunting_pressure_modifier
        
        # Calcul centralisé de la mobilité en intégrant tous les facteurs
        in_corridor = extra_data.get("in_corridor", False)
        corridor_type = extra_data.get("corridor_type", "primary")
        
        mobility_modifier, mobility_details, mobility_sources = self._mobility_registry.get_mobility_modifier(
            species=context.species,
            check_datetime=context.target_datetime,
            digestive_phase=digestive_phase,
            digestive_mobility=digestive_mobility,
            thermal_stress_active=thermal_stress_active,
            thermal_stress_modifier=thermal_stress_modifier,
            human_pressure_active=hunting_pressure_active,
            human_pressure_modifier=hunting_pressure_modifier,
            seasonal_modifier=phase_c_modifier_temp,
            current_season=season if seasonal_model else "default",
            in_corridor=in_corridor,
            corridor_type=corridor_type
        )
        
        # =====================================================================
        # 6. MODIFICATEUR TOTAL (agrégation PHASE B + PHASE C + NIVEAU 3 + NIVEAU 5)
        # =====================================================================
        phase_c_modifier = phase_c_modifier_temp
        total_modifier = social_modifier * competition_modifier * digestive_modifier * signals_modifier * phase_c_modifier * mobility_modifier
        
        # =====================================================================
        # 7. INJECTION DANS LE CONTEXTE (enrichi avec NIVEAU 5 - MOBILITÉ)
        # =====================================================================
        context.advanced_modifiers = {
            # PHASE B: Hiérarchie sociale
            "social_modifier": social_modifier,
            "social_rank": social_rank.value,
            "social_source_ids": social_sources,
            "social_version": "1.0.0",
            
            # PHASE B: Compétition inter-espèces
            "competition_modifier": competition_modifier,
            "competitors_present": competitors,
            "competition_source_ids": competition_sources,
            "competition_version": "1.0.0",
            
            # PHASE B: Cycles digestifs
            "digestive_modifier": digestive_modifier,
            "digestive_phase": digestive_phase,
            "digestive_mobility": digestive_mobility,
            "digestive_visibility": digestive_visibility,
            "digestive_source_ids": digestive_sources,
            "digestive_version": "1.0.0",
            
            # PHASE B: Signaux faibles
            "signals_modifier": signals_modifier,
            "signals_impact": signals_impact,
            "signals_detected": signals_detected_names,
            "signals_source_ids": signals_sources,
            "signals_version": "1.0.0",
            
            # PHASE C: Dispersion juvénile dynamique
            "dispersal_active": dispersal_active,
            "dispersal_modifier": dispersal_modifier,
            "dispersal_variance": dispersal_variance,
            "dispersal_window": dispersal_window_info,
            "dispersal_source_ids": dispersal_sources,
            "dispersal_version": "2.0.0",
            
            # PHASE C: Stress thermique
            "thermal_stress_active": thermal_stress_active,
            "thermal_stress_modifier": thermal_stress_modifier,
            "thermal_stress_source_ids": thermal_sources,
            "thermal_stress_version": "2.0.0",
            
            # NIVEAU 3: Pression de chasse réelle (PRES-HUMAN)
            "hunting_pressure_active": hunting_pressure_active,
            "hunting_pressure_modifier": hunting_pressure_modifier,
            "hunting_pressure_details": pres_human_details,
            "hunting_pressure_source_ids": hunting_pressure_sources,
            "hunting_pressure_version": "3.0.0",
            
            # NIVEAU 5: Mobilité Dynamique
            "mobility_modifier": mobility_modifier,
            "mobility_details": mobility_details,
            "mobility_source_ids": mobility_sources,
            "mobility_version": "5.0.0",
            
            # Modificateurs globaux
            "phase_b_modifier": social_modifier * competition_modifier * digestive_modifier * signals_modifier,
            "phase_c_modifier": phase_c_modifier,
            "niveau_5_modifier": mobility_modifier,
            "total_modifier": total_modifier,
            "calculation_timestamp": datetime.now(timezone.utc).isoformat(),
            "analysis_mode": analysis_mode,
            "is_rut_period": is_rut,
            
            # Métadonnées intégration complète
            "integration_mode": "centralized",
            "pres_human_integrated": True,
            "mobility_integrated": True  # NIVEAU 5
        }
        
        logger.info(f"[{score_id}] Advanced modifiers injected: "
                   f"PHASE_B={social_modifier * competition_modifier * digestive_modifier * signals_modifier:.2f}, "
                   f"PHASE_C={phase_c_modifier:.2f}, hunting_pressure={hunting_pressure_active}, "
                   f"PRES-HUMAN_modifier={hunting_pressure_modifier:.2f}, "
                   f"MOBILITY_modifier={mobility_modifier:.2f}, total={total_modifier:.2f}")
        
        return context
    
    def calculate_unified_score(
        self,
        context: ScoreContext,
        analysis_mode: str = "rut"
    ) -> UnifiedScoreResult:
        """
        Calcule le score unifié pour un contexte donné.
        
        PROCESSUS BIONIC V5 (centralisation PHASE B):
        1. INJECTER les modificateurs avancés dans le contexte (CENTRALISATION)
        2. Appeler chaque service de scoring avec le contexte enrichi
        3. Collecter les ScoreResult
        4. Calculer le score brut agrégé (somme pondérée)
        5. Appliquer le modificateur de période biologique
        6. Calculer l'ajustement temporel (LegalHoursService)
        7. Produire le UnifiedScoreResult
        
        NOTE: Les services CONSOMMENT les modificateurs - AUCUNE logique locale
        
        Args:
            context: Contexte waypoint-centric
            analysis_mode: 'live', 'pre_rut', 'rut', 'post_rut'
            
        Returns:
            UnifiedScoreResult avec score final et détails
        """
        start_time = datetime.now(timezone.utc)
        score_id = self._generate_score_id()
        
        logger.info(f"[{score_id}] Starting unified score calculation (mode={analysis_mode})")
        logger.debug(f"[{score_id}] Context: waypoint={context.waypoint_id}, species={context.species}")
        
        # ==========================================================================
        # ÉTAPE 0: INJECTION DES MODIFICATEURS AVANCÉS (PHASE B - CENTRALISATION)
        # ==========================================================================
        # Cette étape calcule TOUS les modificateurs avancés et les injecte dans le contexte.
        # Les services individuels CONSOMMENT ces valeurs - AUCUNE logique locale.
        context = self._inject_advanced_modifiers(context, analysis_mode, score_id)
        
        # ==== ÉTAPE 1: Appeler chaque service avec contexte enrichi ====
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
        
        # ==== ÉTAPE 4: Récupérer les modificateurs avancés du contexte (PHASE B) ====
        # NOTE BIONIC V5: Les modificateurs ont été calculés et injectés à l'ÉTAPE 0.
        # Les services CONSOMMENT ces valeurs sans logique locale.
        # Cette étape récupère les valeurs pour la traçabilité.
        
        advanced_modifier = context.advanced_modifiers.get("total_modifier", 1.0)
        advanced_details = {
            # PHASE B: Facteurs avancés
            "social": {
                "modifier": context.advanced_modifiers.get("social_modifier", 1.0),
                "rank": context.advanced_modifiers.get("social_rank", "unknown"),
                "version": context.advanced_modifiers.get("social_version", "1.0.0")
            },
            "competition": {
                "modifier": context.advanced_modifiers.get("competition_modifier", 1.0),
                "competitors": context.advanced_modifiers.get("competitors_present", []),
                "version": context.advanced_modifiers.get("competition_version", "1.0.0")
            },
            "digestive": {
                "modifier": context.advanced_modifiers.get("digestive_modifier", 1.0),
                "phase": context.advanced_modifiers.get("digestive_phase", "unknown"),
                "mobility": context.advanced_modifiers.get("digestive_mobility", 0.5),
                "visibility": context.advanced_modifiers.get("digestive_visibility", 0.5),
                "version": context.advanced_modifiers.get("digestive_version", "1.0.0")
            },
            "signals": {
                "modifier": context.advanced_modifiers.get("signals_modifier", 1.0),
                "impact": context.advanced_modifiers.get("signals_impact", 0.0),
                "detected": context.advanced_modifiers.get("signals_detected", []),
                "version": context.advanced_modifiers.get("signals_version", "1.0.0")
            },
            # PHASE C: Phénologie avancée
            "dispersal_juvenile": {
                "active": context.advanced_modifiers.get("dispersal_active", False),
                "modifier": context.advanced_modifiers.get("dispersal_modifier", 1.0),
                "variance": context.advanced_modifiers.get("dispersal_variance", 0.0),
                "window": context.advanced_modifiers.get("dispersal_window"),
                "version": context.advanced_modifiers.get("dispersal_version", "2.0.0")
            },
            "thermal_stress": {
                "active": context.advanced_modifiers.get("thermal_stress_active", False),
                "modifier": context.advanced_modifiers.get("thermal_stress_modifier", 1.0),
                "version": context.advanced_modifiers.get("thermal_stress_version", "2.0.0")
            },
            "hunting_pressure": {
                "active": context.advanced_modifiers.get("hunting_pressure_active", False),
                "modifier": context.advanced_modifiers.get("hunting_pressure_modifier", 1.0),
                "details": context.advanced_modifiers.get("hunting_pressure_details", {}),
                "source_ids": context.advanced_modifiers.get("hunting_pressure_source_ids", []),
                "version": context.advanced_modifiers.get("hunting_pressure_version", "3.0.0")
            },
            # NIVEAU 5: Mobilité Dynamique
            "mobility": {
                "modifier": context.advanced_modifiers.get("mobility_modifier", 1.0),
                "details": context.advanced_modifiers.get("mobility_details", {}),
                "source_ids": context.advanced_modifiers.get("mobility_source_ids", []),
                "version": context.advanced_modifiers.get("mobility_version", "5.0.0")
            },
            # Totaux par phase
            "phase_b_modifier": context.advanced_modifiers.get("phase_b_modifier", 1.0),
            "phase_c_modifier": context.advanced_modifiers.get("phase_c_modifier", 1.0),
            "niveau_5_modifier": context.advanced_modifiers.get("niveau_5_modifier", 1.0)
        }
        
        # Collecter tous les source_ids (PHASE B + PHASE C + NIVEAU 3 + NIVEAU 5)
        advanced_sources = (
            context.advanced_modifiers.get("social_source_ids", []) +
            context.advanced_modifiers.get("competition_source_ids", []) +
            context.advanced_modifiers.get("digestive_source_ids", []) +
            context.advanced_modifiers.get("signals_source_ids", []) +
            context.advanced_modifiers.get("dispersal_source_ids", []) +
            context.advanced_modifiers.get("hunting_pressure_source_ids", []) +
            context.advanced_modifiers.get("mobility_source_ids", [])  # NIVEAU 5
        )
        
        # PHASE B + C + NIVEAU 5 BIONIC V5: Le score brut intègre déjà les modificateurs via les services
        score_after_advanced = raw_score
        
        logger.info(f"[{score_id}] Advanced factors (centralized): "
                   f"PHASE_B={advanced_details.get('phase_b_modifier', 1.0):.2f}, "
                   f"PHASE_C={advanced_details.get('phase_c_modifier', 1.0):.2f}, "
                   f"NIVEAU_5={advanced_details.get('niveau_5_modifier', 1.0):.2f}, "
                   f"total={advanced_modifier:.2f}")
        
        # ==== ÉTAPE 5: Appliquer le modificateur de période biologique ====
        bio_modifier, bio_info, bio_sources = self._get_biological_period_modifier(
            context.species,
            context.region,
            analysis_mode
        )
        
        # En mode LIVE, le modificateur biologique est atténué
        if analysis_mode == "live":
            bio_modifier = 0.7 + (bio_modifier * 0.3)  # Atténuer l'impact
        
        score_after_bio = score_after_advanced * (0.5 + bio_modifier * 0.5)
        
        logger.info(f"[{score_id}] Bio period modifier ({analysis_mode}): {bio_modifier:.2f} -> score: {score_after_bio:.1f}")
        
        # ==== ÉTAPE 6: Calculer l'ajustement temporel ====
        temporal_adj = self._calculate_temporal_adjustment(context)
        
        # ==== ÉTAPE 7: Appliquer l'ajustement temporel ====
        # En mode LIVE, on n'annule pas le score hors heures légales
        if analysis_mode == "live":
            # Mode LIVE: légère pénalité hors heures légales
            if not temporal_adj.is_legal_period:
                final_score = score_after_bio * 0.85
            else:
                final_score = self._apply_temporal_adjustment(score_after_bio, temporal_adj)
        else:
            # Modes biologiques (PRE_RUT, RUT, POST_RUT): respect des heures légales
            final_score = self._apply_temporal_adjustment(score_after_bio, temporal_adj)
        
        # Clamp final score
        final_score = max(0, min(100, final_score))
        
        logger.info(f"[{score_id}] Final score (after temporal): {final_score:.1f}")
        
        # ==== ÉTAPE 8: Agréger les facteurs ====
        positive_factors, negative_factors = self._aggregate_factors(service_results)
        
        # Ajouter facteurs avancés
        if advanced_modifier > 1.05:
            positive_factors.insert(0, f"Facteurs avancés favorables (×{advanced_modifier:.2f})")
        elif advanced_modifier < 0.95:
            negative_factors.insert(0, f"Facteurs avancés défavorables (×{advanced_modifier:.2f})")
        
        # Ajouter info période biologique
        if analysis_mode != "live":
            positive_factors.insert(0, f"Mode {analysis_mode.upper()}: {bio_info.get('season', 'N/A')}")
        
        # ==== ÉTAPE 9: Calculer la confiance globale ====
        global_confidence = self._calculate_global_confidence(service_results)
        # Intégrer la confiance basée sur les sources des modificateurs avancés
        advanced_confidence = 0.8 if advanced_sources else 0.5
        global_confidence = (global_confidence * 0.8) + (advanced_confidence * 0.2)
        
        data_quality = self._assess_data_quality(service_results)
        
        # ==== ÉTAPE 10: Construire le résultat final ====
        calc_time_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        
        result = UnifiedScoreResult(
            score_id=score_id,
            calculated_at=datetime.now(timezone.utc),
            analysis_mode=analysis_mode,
            final_score=final_score,
            final_level=UnifiedScoreResult.get_level_from_value(final_score),
            raw_aggregated_score=raw_score,
            temporal_adjustment=temporal_adj,
            advanced_factors_modifier=advanced_modifier,
            advanced_factors_details={
                "factors": advanced_details,
                "source_ids": advanced_sources,
                "biological_period": bio_info,
                "biological_modifier": bio_modifier,
                "integration_mode": "centralized",  # PHASE B+C+NIVEAU 5: Centralisation complète
                "calculation_timestamp": context.advanced_modifiers.get("calculation_timestamp"),
                "integrated_services": [
                    "ScoreBehaviorService (PHASE B: social, signals, digestive)",
                    "ScoreMultiFactorService (PHASE B: competition)",
                    "ScoreRiskService (PHASE B: signals)",
                    "ScoreMobilityService (PHASE B: digestive, NIVEAU 5: mobility)",
                    "SeasonalModel (PHASE C: dispersal, thermal, hunting_pressure)",
                    "MobilityRegistry (NIVEAU 5: mobilité dynamique)"
                ],
                "phases": {
                    "phase_b": "Facteurs avancés (hiérarchie, compétition, digestif, signaux)",
                    "phase_c": "Phénologie (dispersion juvénile dynamique, stress thermique, pression chasse)",
                    "niveau_5": "Mobilité dynamique (vitesse, variance, direction, contraintes)"
                }
            },
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
                "analysis_mode": analysis_mode,
                "phases_active": ["PHASE_B", "PHASE_C", "NIVEAU_5"],
                "version": "BIONIC-V5-ULTIME-3.0-NIVEAU-5-MOBILITY"
            }
        )
        
        logger.info(f"[{score_id}] Unified score completed in {calc_time_ms:.0f}ms (mode={analysis_mode}, NIVEAU 5 active)")
        
        return result
    
    def _get_current_season_name(self, context: ScoreContext) -> str:
        """Obtenir le nom de la saison courante basé sur la date."""
        seasonal_model = get_seasonal_model(context.species, context.region)
        if seasonal_model:
            season = seasonal_model.get_current_season(context.target_datetime.date())
            if season:
                return season.value
        return "default"
    
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
    
    # =========================================================================
    # NIVEAU 4 — CORRIDORS
    # =========================================================================
    
    def generate_corridors(
        self,
        context: ScoreContext,
        analysis_mode: str = "rut"
    ) -> CorridorNetwork:
        """
        NIVEAU 4 BIONIC V5 — Génération des corridors de déplacement.
        
        Génère le réseau complet de corridors en utilisant les scores calculés
        par le UnifiedScoringService et les facteurs des NIVEAUx 1-3.
        
        Args:
            context: Contexte de scoring enrichi avec les modificateurs avancés
            analysis_mode: Mode d'analyse biologique
            
        Returns:
            CorridorNetwork: Réseau complet de corridors
        """
        # Récupérer les modificateurs avancés injectés
        advanced = context.advanced_modifiers or {}
        
        # Extraire les scores et modificateurs
        thermal_stress_active = advanced.get("thermal_stress_active", False)
        thermal_stress_modifier = advanced.get("thermal_stress_modifier", 1.0)
        hunting_pressure_active = advanced.get("hunting_pressure_active", False)
        hunting_pressure_modifier = advanced.get("hunting_pressure_modifier", 1.0)
        
        # Scores comportementaux et habitat
        habitat_score = 60.0  # Valeur par défaut, sera enrichie via les services
        edge_score = 55.0
        behavior_score = advanced.get("digestive_mobility", 0.5) * 100
        
        # Saison courante
        season = advanced.get("analysis_mode", analysis_mode)
        seasonal_modifier = advanced.get("phase_c_modifier", 1.0)
        
        # Appeler le registre des corridors
        network = self._corridor_registry.generate_corridors(
            waypoint_lat=context.latitude,
            waypoint_lng=context.longitude,
            species=context.species,
            search_radius_km=context.search_radius_km,
            habitat_score=habitat_score,
            edge_score=edge_score,
            thermal_stress_active=thermal_stress_active,
            thermal_stress_modifier=thermal_stress_modifier,
            pres_human_active=hunting_pressure_active,
            pres_human_modifier=hunting_pressure_modifier,
            behavior_score=behavior_score,
            seasonal_modifier=seasonal_modifier,
            current_season=season
        )
        
        logger.info(
            f"Corridors generated for {context.waypoint_id}: "
            f"{network.total_corridors} corridors, "
            f"{network.total_length_km:.2f} km"
        )
        
        return network


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
