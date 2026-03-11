"""
BIONIC V5 — ADVANCED BEHAVIORAL FACTORS
========================================
PHASE B — Facteurs Comportementaux Avancés

Module intégrant les 4 facteurs avancés:
1. Hiérarchie sociale (dominance, subordination)
2. Compétition inter-espèces
3. Signaux faibles comportementaux
4. Cycles digestifs

KNOWLEDGE LAYER INTEGRATION:
- Aucun accès direct aux sources
- Traçabilité obligatoire (source_ids)
- Intégration via knowledge/species/ et seasonal/

VERSION: 1.0.0
Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS
# =============================================================================

class SocialRank(str, Enum):
    """Rang social dans la hiérarchie"""
    ALPHA = "alpha"              # Mâle dominant
    BETA = "beta"                # Second rang
    SUBORDINATE = "subordinate"  # Subordonné
    JUVENILE = "juvenile"        # Jeune
    UNKNOWN = "unknown"


class CompetitionType(str, Enum):
    """Types de compétition inter-espèces"""
    FOOD = "food"                # Compétition alimentaire
    SPACE = "space"              # Compétition spatiale
    THERMAL = "thermal"          # Compétition refuges thermiques
    WATER = "water"              # Compétition points d'eau


class WeakSignalType(str, Enum):
    """Types de signaux faibles comportementaux"""
    STRESS_INDICATOR = "stress_indicator"
    PREDATION_ALERT = "predation_alert"
    RESOURCE_SCARCITY = "resource_scarcity"
    SOCIAL_TENSION = "social_tension"
    ENVIRONMENTAL_CHANGE = "environmental_change"
    HEALTH_INDICATOR = "health_indicator"


class DigestivePhase(str, Enum):
    """Phases du cycle digestif (ruminants)"""
    ACTIVE_FEEDING = "active_feeding"    # Broutage actif
    RUMINATION = "rumination"            # Rumination
    REST_DIGESTION = "rest_digestion"    # Repos digestif
    WATER_SEEKING = "water_seeking"      # Recherche d'eau


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class SocialHierarchyRule:
    """
    Règle de hiérarchie sociale.
    
    Définit les comportements basés sur le rang social
    et les interactions dominance/subordination.
    """
    rule_id: str
    species: str
    
    # Rang et comportement
    social_rank: SocialRank
    behavior_modifier: float  # Multiplicateur d'activité (0.5-2.0)
    
    # Territorialité
    territory_expansion_factor: float = 1.0  # Alpha > 1.0, Subordinate < 1.0
    aggression_level: float = 0.5  # 0.0-1.0
    
    # Saisonnalité
    applicable_seasons: List[str] = field(default_factory=lambda: ["all"])
    rut_amplification: float = 1.0  # Multiplicateur pendant le rut
    
    # Effets sur scoring
    visibility_modifier: float = 1.0  # Impact sur probabilité d'observation
    predictability_modifier: float = 1.0  # Impact sur prédictibilité des mouvements
    
    # Traçabilité
    source_ids: List[str] = field(default_factory=list)
    confidence: float = 0.75
    description: str = ""


@dataclass
class InterspeciesCompetition:
    """
    Règle de compétition inter-espèces.
    
    Définit les interactions compétitives entre espèces
    et leurs effets sur les comportements.
    """
    rule_id: str
    primary_species: str
    competitor_species: str
    
    # Type de compétition
    competition_type: CompetitionType
    
    # Intensité et effets
    competition_intensity: float  # 0.0-1.0
    displacement_probability: float  # Probabilité que primary soit déplacé
    temporal_avoidance: bool = False  # Évitement temporel
    spatial_avoidance: bool = False  # Évitement spatial
    
    # Zones affectées
    affected_habitats: List[str] = field(default_factory=list)
    
    # Saisonnalité
    peak_seasons: List[str] = field(default_factory=list)
    
    # Effets sur scoring
    score_reduction_factor: float = 1.0  # Réduction du score si compétiteur présent
    
    # Traçabilité
    source_ids: List[str] = field(default_factory=list)
    confidence: float = 0.70
    description: str = ""


@dataclass
class WeakSignal:
    """
    Signal faible comportemental.
    
    Indicateurs subtils permettant de détecter
    des changements comportementaux avant qu'ils ne deviennent évidents.
    """
    signal_id: str
    species: str
    
    # Type et détection
    signal_type: WeakSignalType
    detection_threshold: float  # Seuil de détection (0.0-1.0)
    
    # Indicateurs observables
    observable_indicators: List[str] = field(default_factory=list)
    
    # Effets comportementaux
    behavior_change: str = ""
    activity_modifier: float = 1.0
    movement_modifier: float = 1.0
    
    # Temporalité
    lag_hours: float = 0.0  # Délai entre signal et effet
    duration_hours: float = 24.0  # Durée de l'effet
    
    # Scoring
    score_impact: float = 0.0  # Impact sur le score (-20 à +20)
    
    # Traçabilité
    source_ids: List[str] = field(default_factory=list)
    confidence: float = 0.60
    description: str = ""


@dataclass
class DigestiveCycle:
    """
    Cycle digestif pour ruminants.
    
    Définit les phases du cycle digestif et leurs
    impacts sur les comportements et la mobilité.
    """
    cycle_id: str
    species: str
    
    # Phase
    phase: DigestivePhase
    
    # Timing
    typical_start_hour: int  # Heure typique de début
    typical_duration_hours: float  # Durée typique
    
    # Comportement pendant cette phase
    mobility_level: float  # 0.0-1.0 (0 = immobile)
    alertness_level: float  # 0.0-1.0
    feeding_probability: float  # 0.0-1.0
    
    # Habitat préféré pendant cette phase
    preferred_habitat: str = ""
    cover_requirement: float = 0.5  # Besoin de couvert (0.0-1.0)
    
    # Effets sur scoring
    visibility_during_phase: float = 0.5  # Probabilité d'observation
    
    # Traçabilité
    source_ids: List[str] = field(default_factory=list)
    confidence: float = 0.80
    description: str = ""


# =============================================================================
# ADVANCED FACTORS REGISTRY
# =============================================================================

class AdvancedFactorsRegistry:
    """
    Registre centralisé des facteurs avancés.
    
    Point d'entrée unique pour le Knowledge Layer.
    """
    
    def __init__(self):
        self._social_rules: Dict[str, SocialHierarchyRule] = {}
        self._competition_rules: Dict[str, InterspeciesCompetition] = {}
        self._weak_signals: Dict[str, WeakSignal] = {}
        self._digestive_cycles: Dict[str, DigestiveCycle] = {}
        
        self._version = "1.0.0"
        self._initialize_moose_factors()
        self._initialize_deer_factors()
        
        logger.info(f"AdvancedFactorsRegistry initialized: "
                   f"{len(self._social_rules)} social, "
                   f"{len(self._competition_rules)} competition, "
                   f"{len(self._weak_signals)} signals, "
                   f"{len(self._digestive_cycles)} digestive")
    
    def _initialize_moose_factors(self):
        """Initialiser les facteurs avancés pour l'orignal"""
        
        # =====================================================
        # HIÉRARCHIE SOCIALE — ORIGNAL
        # =====================================================
        
        self._social_rules["MOOSE-SOC-ALPHA"] = SocialHierarchyRule(
            rule_id="MOOSE-SOC-ALPHA",
            species="moose",
            social_rank=SocialRank.ALPHA,
            behavior_modifier=1.4,  # Plus actif
            territory_expansion_factor=1.5,
            aggression_level=0.8,
            applicable_seasons=["rut", "pre_rut"],
            rut_amplification=2.0,  # Très amplifié pendant le rut
            visibility_modifier=1.3,  # Plus visible (vocalises, déplacements)
            predictability_modifier=0.7,  # Moins prévisible (patrouille)
            source_ids=["SRC-LAVAL-001", "SRC-MFFP-001"],
            confidence=0.85,
            description="Mâle dominant - territoire étendu, comportement agressif pendant le rut"
        )
        
        self._social_rules["MOOSE-SOC-SUB"] = SocialHierarchyRule(
            rule_id="MOOSE-SOC-SUB",
            species="moose",
            social_rank=SocialRank.SUBORDINATE,
            behavior_modifier=0.8,  # Moins actif
            territory_expansion_factor=0.6,
            aggression_level=0.2,
            applicable_seasons=["all"],
            rut_amplification=0.5,  # Évite les conflits
            visibility_modifier=0.7,  # Moins visible (discret)
            predictability_modifier=1.3,  # Plus prévisible (zones marginales)
            source_ids=["SRC-LAVAL-001", "SRC-GAGNON-001"],
            confidence=0.80,
            description="Mâle subordonné - zones périphériques, évite les dominants"
        )
        
        self._social_rules["MOOSE-SOC-FEM"] = SocialHierarchyRule(
            rule_id="MOOSE-SOC-FEM",
            species="moose",
            social_rank=SocialRank.BETA,
            behavior_modifier=1.0,
            territory_expansion_factor=1.0,
            aggression_level=0.3,
            applicable_seasons=["all"],
            rut_amplification=1.2,  # Plus mobile pendant le rut
            visibility_modifier=1.0,
            predictability_modifier=1.1,
            source_ids=["SRC-MFFP-001", "SRC-PARCS-001"],
            confidence=0.82,
            description="Femelle adulte - comportement stable, mobilité accrue pendant le rut"
        )
        
        # =====================================================
        # COMPÉTITION INTER-ESPÈCES — ORIGNAL
        # =====================================================
        
        self._competition_rules["MOOSE-COMP-DEER"] = InterspeciesCompetition(
            rule_id="MOOSE-COMP-DEER",
            primary_species="moose",
            competitor_species="deer",
            competition_type=CompetitionType.FOOD,
            competition_intensity=0.3,  # Faible (niches différentes)
            displacement_probability=0.1,
            temporal_avoidance=False,
            spatial_avoidance=True,  # Ségrégation spatiale naturelle
            affected_habitats=["mixed_forest", "regeneration_zone"],
            peak_seasons=["winter"],  # Plus intense en hiver
            score_reduction_factor=0.95,
            source_ids=["SRC-LAVAL-001"],
            confidence=0.75,
            description="Compétition alimentaire limitée avec le cerf - ségrégation spatiale"
        )
        
        self._competition_rules["MOOSE-COMP-BEAR"] = InterspeciesCompetition(
            rule_id="MOOSE-COMP-BEAR",
            primary_species="moose",
            competitor_species="bear",
            competition_type=CompetitionType.FOOD,
            competition_intensity=0.2,
            displacement_probability=0.15,
            temporal_avoidance=True,  # Évitement temporel des ours
            spatial_avoidance=False,
            affected_habitats=["berry_patches", "wetland"],
            peak_seasons=["summer", "hyperphagia"],
            score_reduction_factor=0.90,
            source_ids=["SRC-PARCS-001", "SRC-LAVAL-001"],
            confidence=0.70,
            description="Évitement temporel des ours, surtout près des baies"
        )
        
        # =====================================================
        # SIGNAUX FAIBLES — ORIGNAL
        # =====================================================
        
        self._weak_signals["MOOSE-SIG-PRED"] = WeakSignal(
            signal_id="MOOSE-SIG-PRED",
            species="moose",
            signal_type=WeakSignalType.PREDATION_ALERT,
            detection_threshold=0.6,
            observable_indicators=[
                "Vocalises d'alarme",
                "Regroupement inhabituel",
                "Mouvements nerveux",
                "Changement de direction soudain"
            ],
            behavior_change="Fuite ou regroupement défensif",
            activity_modifier=0.5,  # Réduction activité normale
            movement_modifier=2.0,  # Augmentation mouvements évasifs
            lag_hours=0.0,
            duration_hours=4.0,
            score_impact=-15.0,  # Moins prévisible
            source_ids=["SRC-PARCS-001", "SRC-GAGNON-001"],
            confidence=0.75,
            description="Signaux d'alerte prédation (loups, ours)"
        )
        
        self._weak_signals["MOOSE-SIG-STRESS"] = WeakSignal(
            signal_id="MOOSE-SIG-STRESS",
            species="moose",
            signal_type=WeakSignalType.STRESS_INDICATOR,
            detection_threshold=0.5,
            observable_indicators=[
                "Alimentation réduite",
                "Activité nocturne augmentée",
                "Évitement de zones habituelles",
                "Perte de poids visible"
            ],
            behavior_change="Modification des patterns d'activité",
            activity_modifier=0.7,
            movement_modifier=1.3,
            lag_hours=48.0,  # Effet différé
            duration_hours=168.0,  # Une semaine
            score_impact=-10.0,
            source_ids=["SRC-LAVAL-001"],
            confidence=0.65,
            description="Indicateurs de stress (pression de chasse, perturbation)"
        )
        
        self._weak_signals["MOOSE-SIG-RUT"] = WeakSignal(
            signal_id="MOOSE-SIG-RUT",
            species="moose",
            signal_type=WeakSignalType.SOCIAL_TENSION,
            detection_threshold=0.4,
            observable_indicators=[
                "Frottoirs frais",
                "Vocalises mâles",
                "Traces de combat",
                "Marquage urinaire"
            ],
            behavior_change="Activité rut imminente",
            activity_modifier=1.5,
            movement_modifier=1.8,
            lag_hours=24.0,
            duration_hours=48.0,
            score_impact=+20.0,  # Très favorable pour la chasse
            source_ids=["SRC-MFFP-001", "SRC-GAGNON-001"],
            confidence=0.88,
            description="Signaux précurseurs du rut actif"
        )
        
        # =====================================================
        # CYCLES DIGESTIFS — ORIGNAL
        # =====================================================
        
        self._digestive_cycles["MOOSE-DIG-FEED"] = DigestiveCycle(
            cycle_id="MOOSE-DIG-FEED",
            species="moose",
            phase=DigestivePhase.ACTIVE_FEEDING,
            typical_start_hour=6,
            typical_duration_hours=2.0,
            mobility_level=0.8,
            alertness_level=0.6,
            feeding_probability=0.95,
            preferred_habitat="edge_forest_water",
            cover_requirement=0.3,
            visibility_during_phase=0.85,
            source_ids=["SRC-LAVAL-001", "SRC-MFFP-001"],
            confidence=0.90,
            description="Phase d'alimentation active - haute visibilité"
        )
        
        self._digestive_cycles["MOOSE-DIG-RUM"] = DigestiveCycle(
            cycle_id="MOOSE-DIG-RUM",
            species="moose",
            phase=DigestivePhase.RUMINATION,
            typical_start_hour=10,
            typical_duration_hours=4.0,
            mobility_level=0.1,
            alertness_level=0.8,
            feeding_probability=0.05,
            preferred_habitat="dense_cover",
            cover_requirement=0.8,
            visibility_during_phase=0.25,
            source_ids=["SRC-LAVAL-001"],
            confidence=0.88,
            description="Phase de rumination - immobile mais alerte"
        )
        
        self._digestive_cycles["MOOSE-DIG-REST"] = DigestiveCycle(
            cycle_id="MOOSE-DIG-REST",
            species="moose",
            phase=DigestivePhase.REST_DIGESTION,
            typical_start_hour=14,
            typical_duration_hours=2.0,
            mobility_level=0.05,
            alertness_level=0.4,
            feeding_probability=0.0,
            preferred_habitat="thermal_cover",
            cover_requirement=0.9,
            visibility_during_phase=0.15,
            source_ids=["SRC-MFFP-001"],
            confidence=0.85,
            description="Repos digestif - très faible visibilité"
        )
        
        self._digestive_cycles["MOOSE-DIG-WATER"] = DigestiveCycle(
            cycle_id="MOOSE-DIG-WATER",
            species="moose",
            phase=DigestivePhase.WATER_SEEKING,
            typical_start_hour=16,
            typical_duration_hours=1.0,
            mobility_level=0.9,
            alertness_level=0.7,
            feeding_probability=0.3,
            preferred_habitat="water_edge",
            cover_requirement=0.2,
            visibility_during_phase=0.90,
            source_ids=["SRC-LAVAL-001", "SRC-PARCS-001"],
            confidence=0.87,
            description="Recherche d'eau - déplacement prévisible"
        )
    
    def _initialize_deer_factors(self):
        """Initialiser les facteurs avancés pour le cerf"""
        
        # Hiérarchie sociale - Cerf
        self._social_rules["DEER-SOC-ALPHA"] = SocialHierarchyRule(
            rule_id="DEER-SOC-ALPHA",
            species="deer",
            social_rank=SocialRank.ALPHA,
            behavior_modifier=1.3,
            territory_expansion_factor=1.4,
            aggression_level=0.7,
            applicable_seasons=["rut"],
            rut_amplification=1.8,
            visibility_modifier=1.2,
            predictability_modifier=0.8,
            source_ids=["SRC-DEER-001"],
            confidence=0.80,
            description="Buck dominant - très actif pendant le rut"
        )
        
        # Compétition - Cerf vs Orignal
        self._competition_rules["DEER-COMP-MOOSE"] = InterspeciesCompetition(
            rule_id="DEER-COMP-MOOSE",
            primary_species="deer",
            competitor_species="moose",
            competition_type=CompetitionType.SPACE,
            competition_intensity=0.4,
            displacement_probability=0.25,  # Le cerf cède souvent
            temporal_avoidance=True,
            spatial_avoidance=True,
            affected_habitats=["mixed_forest"],
            peak_seasons=["winter"],
            score_reduction_factor=0.85,
            source_ids=["SRC-DEER-001"],
            confidence=0.72,
            description="Le cerf évite les zones dominées par l'orignal"
        )
        
        # Cycles digestifs - Cerf (similaire mais plus courts)
        self._digestive_cycles["DEER-DIG-FEED"] = DigestiveCycle(
            cycle_id="DEER-DIG-FEED",
            species="deer",
            phase=DigestivePhase.ACTIVE_FEEDING,
            typical_start_hour=6,
            typical_duration_hours=1.5,
            mobility_level=0.7,
            alertness_level=0.8,
            feeding_probability=0.90,
            preferred_habitat="field_edge",
            cover_requirement=0.4,
            visibility_during_phase=0.80,
            source_ids=["SRC-DEER-001"],
            confidence=0.85,
            description="Alimentation active - bonne visibilité"
        )
    
    # =========================================================================
    # SOCIAL HIERARCHY
    # =========================================================================
    
    def get_social_rules(
        self,
        species: str,
        season: Optional[str] = None
    ) -> List[SocialHierarchyRule]:
        """Obtenir les règles de hiérarchie sociale"""
        rules = [
            r for r in self._social_rules.values()
            if r.species.lower() == species.lower()
        ]
        
        if season:
            rules = [
                r for r in rules
                if "all" in r.applicable_seasons or season in r.applicable_seasons
            ]
        
        return rules
    
    def get_social_modifier(
        self,
        species: str,
        social_rank: SocialRank,
        season: str,
        is_rut: bool = False
    ) -> Tuple[float, List[str]]:
        """
        Obtenir le modificateur comportemental basé sur le rang social.
        
        Returns:
            Tuple[modificateur, source_ids]
        """
        rules = [
            r for r in self._social_rules.values()
            if r.species.lower() == species.lower()
            and r.social_rank == social_rank
        ]
        
        if not rules:
            return 1.0, []
        
        rule = rules[0]
        modifier = rule.behavior_modifier
        
        if is_rut:
            modifier *= rule.rut_amplification
        
        return modifier, rule.source_ids
    
    # =========================================================================
    # INTERSPECIES COMPETITION
    # =========================================================================
    
    def get_competition_rules(
        self,
        species: str,
        competitor: Optional[str] = None
    ) -> List[InterspeciesCompetition]:
        """Obtenir les règles de compétition inter-espèces"""
        rules = [
            r for r in self._competition_rules.values()
            if r.primary_species.lower() == species.lower()
        ]
        
        if competitor:
            rules = [
                r for r in rules
                if r.competitor_species.lower() == competitor.lower()
            ]
        
        return rules
    
    def get_competition_score_modifier(
        self,
        species: str,
        competitors_present: List[str],
        habitat: str
    ) -> Tuple[float, List[str]]:
        """
        Calculer le modificateur de score basé sur la compétition.
        
        Returns:
            Tuple[modificateur, source_ids]
        """
        total_modifier = 1.0
        all_sources = []
        
        for competitor in competitors_present:
            rules = self.get_competition_rules(species, competitor)
            for rule in rules:
                if habitat in rule.affected_habitats or not rule.affected_habitats:
                    total_modifier *= rule.score_reduction_factor
                    all_sources.extend(rule.source_ids)
        
        return total_modifier, list(set(all_sources))
    
    # =========================================================================
    # WEAK SIGNALS
    # =========================================================================
    
    def get_weak_signals(
        self,
        species: str,
        signal_type: Optional[WeakSignalType] = None
    ) -> List[WeakSignal]:
        """Obtenir les signaux faibles"""
        signals = [
            s for s in self._weak_signals.values()
            if s.species.lower() == species.lower()
        ]
        
        if signal_type:
            signals = [s for s in signals if s.signal_type == signal_type]
        
        return signals
    
    def evaluate_weak_signals(
        self,
        species: str,
        observed_indicators: List[str]
    ) -> Tuple[float, List[WeakSignal], List[str]]:
        """
        Évaluer les signaux faibles basés sur les indicateurs observés.
        
        Returns:
            Tuple[score_impact_total, signaux_détectés, source_ids]
        """
        signals = self.get_weak_signals(species)
        detected = []
        total_impact = 0.0
        all_sources = []
        
        for signal in signals:
            matches = sum(
                1 for ind in signal.observable_indicators
                if any(obs.lower() in ind.lower() for obs in observed_indicators)
            )
            
            if matches > 0:
                detection_strength = matches / len(signal.observable_indicators)
                if detection_strength >= signal.detection_threshold:
                    detected.append(signal)
                    total_impact += signal.score_impact * detection_strength
                    all_sources.extend(signal.source_ids)
        
        return total_impact, detected, list(set(all_sources))
    
    # =========================================================================
    # DIGESTIVE CYCLES
    # =========================================================================
    
    def get_digestive_cycles(
        self,
        species: str
    ) -> List[DigestiveCycle]:
        """Obtenir les cycles digestifs pour une espèce"""
        return [
            c for c in self._digestive_cycles.values()
            if c.species.lower() == species.lower()
        ]
    
    def get_current_digestive_phase(
        self,
        species: str,
        hour: int
    ) -> Tuple[Optional[DigestiveCycle], List[str]]:
        """
        Déterminer la phase digestive actuelle basée sur l'heure.
        
        Returns:
            Tuple[cycle, source_ids]
        """
        cycles = self.get_digestive_cycles(species)
        
        for cycle in cycles:
            start = cycle.typical_start_hour
            end = (start + int(cycle.typical_duration_hours)) % 24
            
            if start <= end:
                if start <= hour < end:
                    return cycle, cycle.source_ids
            else:  # Passage par minuit
                if hour >= start or hour < end:
                    return cycle, cycle.source_ids
        
        # Défaut: phase de repos
        rest_cycles = [c for c in cycles if c.phase == DigestivePhase.REST_DIGESTION]
        if rest_cycles:
            return rest_cycles[0], rest_cycles[0].source_ids
        
        return None, []
    
    def get_visibility_by_digestive_phase(
        self,
        species: str,
        hour: int
    ) -> Tuple[float, List[str]]:
        """
        Obtenir la visibilité basée sur la phase digestive.
        
        Returns:
            Tuple[visibility_score, source_ids]
        """
        cycle, sources = self.get_current_digestive_phase(species, hour)
        
        if cycle:
            return cycle.visibility_during_phase, sources
        
        return 0.5, []  # Défaut
    
    # =========================================================================
    # COMBINED ADVANCED SCORE
    # =========================================================================
    
    def calculate_advanced_modifier(
        self,
        species: str,
        hour: int,
        season: str,
        social_rank: SocialRank = SocialRank.UNKNOWN,
        competitors_present: List[str] = None,
        observed_indicators: List[str] = None,
        habitat: str = "mixed_forest"
    ) -> Dict[str, Any]:
        """
        Calculer le modificateur avancé combiné.
        
        Combine tous les facteurs avancés en un seul modificateur
        avec traçabilité complète.
        """
        competitors_present = competitors_present or []
        observed_indicators = observed_indicators or []
        
        result = {
            "total_modifier": 1.0,
            "factors": {},
            "source_ids": [],
            "confidence": 0.0
        }
        
        all_sources = []
        all_confidences = []
        
        # 1. Hiérarchie sociale
        if social_rank != SocialRank.UNKNOWN:
            social_mod, social_sources = self.get_social_modifier(
                species, social_rank, season, is_rut=(season in ["rut", "pre_rut"])
            )
            result["factors"]["social_hierarchy"] = {
                "modifier": social_mod,
                "rank": social_rank.value
            }
            result["total_modifier"] *= social_mod
            all_sources.extend(social_sources)
            if social_sources:
                all_confidences.append(0.80)
        
        # 2. Compétition inter-espèces
        if competitors_present:
            comp_mod, comp_sources = self.get_competition_score_modifier(
                species, competitors_present, habitat
            )
            result["factors"]["interspecies_competition"] = {
                "modifier": comp_mod,
                "competitors": competitors_present
            }
            result["total_modifier"] *= comp_mod
            all_sources.extend(comp_sources)
            if comp_sources:
                all_confidences.append(0.70)
        
        # 3. Signaux faibles
        if observed_indicators:
            signal_impact, detected, signal_sources = self.evaluate_weak_signals(
                species, observed_indicators
            )
            if detected:
                # Convertir l'impact en modificateur (±20 points → ±20%)
                signal_mod = 1.0 + (signal_impact / 100)
                result["factors"]["weak_signals"] = {
                    "modifier": signal_mod,
                    "detected_count": len(detected),
                    "impact_points": signal_impact
                }
                result["total_modifier"] *= signal_mod
                all_sources.extend(signal_sources)
                all_confidences.append(0.65)
        
        # 4. Cycles digestifs
        visibility, digest_sources = self.get_visibility_by_digestive_phase(species, hour)
        cycle, _ = self.get_current_digestive_phase(species, hour)
        
        result["factors"]["digestive_cycle"] = {
            "visibility": visibility,
            "phase": cycle.phase.value if cycle else "unknown",
            "mobility": cycle.mobility_level if cycle else 0.5
        }
        # Visibilité impacte le score (haute visibilité = meilleur score)
        result["total_modifier"] *= (0.5 + visibility * 0.5)
        all_sources.extend(digest_sources)
        if digest_sources:
            all_confidences.append(0.85)
        
        # Agrégation
        result["source_ids"] = list(set(all_sources))
        result["confidence"] = sum(all_confidences) / len(all_confidences) if all_confidences else 0.5
        
        return result


# =============================================================================
# SINGLETON
# =============================================================================

_registry_instance: Optional[AdvancedFactorsRegistry] = None


def get_advanced_factors_registry() -> AdvancedFactorsRegistry:
    """Obtenir l'instance singleton du registre des facteurs avancés"""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = AdvancedFactorsRegistry()
    return _registry_instance


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    'SocialRank',
    'CompetitionType',
    'WeakSignalType',
    'DigestivePhase',
    # Data models
    'SocialHierarchyRule',
    'InterspeciesCompetition',
    'WeakSignal',
    'DigestiveCycle',
    # Registry
    'AdvancedFactorsRegistry',
    'get_advanced_factors_registry'
]
