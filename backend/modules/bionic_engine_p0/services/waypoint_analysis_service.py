"""
BIONIC ENGINE — Waypoint Analysis Service
==========================================
Service d'analyse complète centrée sur le waypoint.

RESPONSABILITÉ UNIQUE:
- Orchestrer une analyse complète autour du waypoint de référence
- Intégrer SCORE_FINAL, Heatmap Unifiée, et tous les sous-scores
- Calculer les distances, hotspots pertinents, transitions d'habitats
- Produire un WaypointAnalysisResult standardisé

ANALYSES INCLUSES:
- Score final unifié (9 scores)
- Heatmap unifiée (WQS + SCORE_FINAL)
- Hotspots dans le rayon de recherche
- Mobilité locale et corridors
- Pression de chasse locale
- Risques environnementaux
- Densité de population
- Transitions d'habitats
- Fenêtres optimales légales

ISOLATION:
- Aucun calcul interne des scores ou heatmaps (appel uniquement)
- Waypoint = centre absolu de toute l'analyse
- Aucune modification des services existants

INPUTS:
- WaypointAnalysisContext (waypoint + paramètres)

OUTPUTS:
- WaypointAnalysisResult (analyse complète)

Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum

# Import des services
from modules.bionic_engine_p0.services.unified_scoring_service import (
    get_unified_scoring_service,
    UnifiedScoreResult
)

from modules.bionic_engine_p0.services.heatmap_fusion_service import (
    get_heatmap_fusion_service,
    HeatmapUnifieeResult,
    HeatmapFusionContext,
    WQSInput
)

from modules.bionic_engine_p0.services.scoring import (
    ScoreContext,
    ScoreLevel
)

from modules.bionic_engine_p0.services.legal_hours_service import (
    get_legal_hours_service,
    LegalHuntingWindow,
    LegalStatus
)

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS
# =============================================================================

class HabitatType(str, Enum):
    """Types d'habitats."""
    FOREST_DENSE = "forest_dense"
    FOREST_MIXED = "forest_mixed"
    CLEARING = "clearing"
    WETLAND = "wetland"
    EDGE = "edge"
    CORRIDOR = "corridor"
    WATER_PROXIMITY = "water_proximity"
    UNKNOWN = "unknown"


class RiskLevel(str, Enum):
    """Niveaux de risque."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


# =============================================================================
# DATA CONTRACTS
# =============================================================================

@dataclass
class WaypointAnalysisContext:
    """
    Contexte d'entrée pour l'analyse waypoint.
    """
    # Identification du waypoint
    waypoint_id: str
    waypoint_name: str
    latitude: float
    longitude: float
    
    # Temporel
    target_datetime: datetime
    
    # Espèce cible
    species: str
    
    # Données WQS (fourni en entrée)
    wqs_score: float
    wqs_success_history: float = 50.0
    wqs_weather_correlation: float = 50.0
    wqs_activity_history: float = 50.0
    wqs_accessibility: float = 50.0
    
    # Paramètres d'analyse
    search_radius_km: float = 3.0
    grid_resolution: int = 10
    
    # Région
    region: str = "CA-QC"
    
    # Données additionnelles
    extra_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "waypoint": {
                "id": self.waypoint_id,
                "name": self.waypoint_name,
                "latitude": self.latitude,
                "longitude": self.longitude
            },
            "target_datetime": self.target_datetime.isoformat(),
            "species": self.species,
            "wqs": {
                "score": self.wqs_score,
                "success_history": self.wqs_success_history,
                "weather_correlation": self.wqs_weather_correlation,
                "activity_history": self.wqs_activity_history,
                "accessibility": self.wqs_accessibility
            },
            "parameters": {
                "search_radius_km": self.search_radius_km,
                "grid_resolution": self.grid_resolution,
                "region": self.region
            }
        }


@dataclass
class HotspotProximity:
    """Hotspot dans la zone de recherche."""
    hotspot_id: str
    hotspot_type: str
    distance_km: float
    bearing_degrees: float  # Direction depuis le waypoint
    score: float
    species: List[str]
    optimal_window: str
    is_reachable: bool
    travel_time_minutes: float  # Estimation
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "hotspot_id": self.hotspot_id,
            "type": self.hotspot_type,
            "distance_km": round(self.distance_km, 2),
            "bearing_degrees": round(self.bearing_degrees, 1),
            "score": round(self.score, 1),
            "species": self.species,
            "optimal_window": self.optimal_window,
            "is_reachable": self.is_reachable,
            "travel_time_minutes": round(self.travel_time_minutes, 0)
        }


@dataclass
class LocalMobilityAnalysis:
    """Analyse de la mobilité locale."""
    corridor_proximity_km: float
    movement_probability: float  # 0-1
    daily_route_alignment: float  # 0-1
    migration_relevance: float  # 0-1
    territorial_stability: float  # 0-1
    mobility_score: float  # 0-100
    key_corridors: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "corridor_proximity_km": round(self.corridor_proximity_km, 2),
            "movement_probability": round(self.movement_probability, 2),
            "daily_route_alignment": round(self.daily_route_alignment, 2),
            "migration_relevance": round(self.migration_relevance, 2),
            "territorial_stability": round(self.territorial_stability, 2),
            "mobility_score": round(self.mobility_score, 1),
            "key_corridors": self.key_corridors
        }


@dataclass
class LocalPressureAnalysis:
    """Analyse de la pression locale."""
    hunting_activity_index: float  # 0-100
    human_proximity_km: float
    road_density_per_km2: float
    disturbance_level: float  # 0-100
    pressure_score: float  # 0-100 (inversé: haut = faible pression)
    pressure_factors: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "hunting_activity_index": round(self.hunting_activity_index, 1),
            "human_proximity_km": round(self.human_proximity_km, 2),
            "road_density_per_km2": round(self.road_density_per_km2, 2),
            "disturbance_level": round(self.disturbance_level, 1),
            "pressure_score": round(self.pressure_score, 1),
            "pressure_factors": self.pressure_factors
        }


@dataclass
class LocalRiskAnalysis:
    """Analyse des risques locaux."""
    risk_level: RiskLevel
    predator_presence: float  # 0-1
    natural_hazards: float  # 0-1
    regulated_zones_proximity_km: float
    safety_score: float  # 0-100 (haut = sûr)
    risk_factors: List[str]
    mitigation_suggestions: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "risk_level": self.risk_level.value,
            "predator_presence": round(self.predator_presence, 2),
            "natural_hazards": round(self.natural_hazards, 2),
            "regulated_zones_proximity_km": round(self.regulated_zones_proximity_km, 2),
            "safety_score": round(self.safety_score, 1),
            "risk_factors": self.risk_factors,
            "mitigation_suggestions": self.mitigation_suggestions
        }


@dataclass
class LocalDensityAnalysis:
    """Analyse de la densité locale."""
    estimated_density_per_km2: float
    observation_frequency: float  # 0-1
    population_trend: str  # "increasing", "stable", "decreasing"
    density_score: float  # 0-100
    density_factors: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "estimated_density_per_km2": round(self.estimated_density_per_km2, 2),
            "observation_frequency": round(self.observation_frequency, 2),
            "population_trend": self.population_trend,
            "density_score": round(self.density_score, 1),
            "density_factors": self.density_factors
        }


@dataclass
class HabitatTransition:
    """Transition d'habitat détectée."""
    from_habitat: HabitatType
    to_habitat: HabitatType
    distance_km: float
    bearing_degrees: float
    transition_quality: float  # 0-100
    species_relevance: float  # 0-1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "from": self.from_habitat.value,
            "to": self.to_habitat.value,
            "distance_km": round(self.distance_km, 2),
            "bearing_degrees": round(self.bearing_degrees, 1),
            "transition_quality": round(self.transition_quality, 1),
            "species_relevance": round(self.species_relevance, 2)
        }


@dataclass
class OptimalWindowRecommendation:
    """Recommandation de fenêtre optimale."""
    period: str
    start_time: str
    end_time: str
    score: float
    quality: str
    species_activity: str
    legal_badge: str
    recommendation: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "period": self.period,
            "time_range": f"{self.start_time} - {self.end_time}",
            "score": round(self.score, 1),
            "quality": self.quality,
            "species_activity": self.species_activity,
            "legal_badge": self.legal_badge,
            "recommendation": self.recommendation
        }


@dataclass
class WaypointAnalysisResult:
    """
    Résultat complet de l'analyse waypoint-centric.
    """
    # Identification
    analysis_id: str
    calculated_at: datetime
    
    # Waypoint de référence
    waypoint_id: str
    waypoint_name: str
    waypoint_coordinates: Tuple[float, float]
    
    # Scores principaux
    unified_score: float
    unified_level: ScoreLevel
    fused_heatmap_score: float
    wqs_score: float
    
    # Analyses locales
    hotspots_nearby: List[HotspotProximity]
    mobility_analysis: LocalMobilityAnalysis
    pressure_analysis: LocalPressureAnalysis
    risk_analysis: LocalRiskAnalysis
    density_analysis: LocalDensityAnalysis
    
    # Transitions d'habitats
    habitat_transitions: List[HabitatTransition]
    dominant_habitat: HabitatType
    
    # Fenêtres optimales
    optimal_windows: List[OptimalWindowRecommendation]
    
    # Conformité légale
    legal_window: LegalHuntingWindow
    is_legal_period: bool
    legal_status: LegalStatus
    
    # Recommandations globales
    recommendations: List[str]
    
    # Contexte d'entrée
    context: WaypointAnalysisContext
    
    # Références aux résultats sous-jacents
    unified_score_id: str
    heatmap_id: str
    
    # Métadonnées
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "analysis_id": self.analysis_id,
            "calculated_at": self.calculated_at.isoformat(),
            "waypoint": {
                "id": self.waypoint_id,
                "name": self.waypoint_name,
                "coordinates": {
                    "lat": self.waypoint_coordinates[0],
                    "lng": self.waypoint_coordinates[1]
                }
            },
            "scores": {
                "unified_score": round(self.unified_score, 1),
                "unified_level": self.unified_level.value,
                "fused_heatmap_score": round(self.fused_heatmap_score, 1),
                "wqs_score": round(self.wqs_score, 1)
            },
            "hotspots_nearby": [h.to_dict() for h in self.hotspots_nearby],
            "local_analysis": {
                "mobility": self.mobility_analysis.to_dict(),
                "pressure": self.pressure_analysis.to_dict(),
                "risk": self.risk_analysis.to_dict(),
                "density": self.density_analysis.to_dict()
            },
            "habitat": {
                "dominant": self.dominant_habitat.value,
                "transitions": [t.to_dict() for t in self.habitat_transitions]
            },
            "optimal_windows": [w.to_dict() for w in self.optimal_windows],
            "legal": {
                "window": self.legal_window.to_dict(),
                "is_legal_period": self.is_legal_period,
                "status": self.legal_status.value
            },
            "recommendations": self.recommendations,
            "references": {
                "unified_score_id": self.unified_score_id,
                "heatmap_id": self.heatmap_id
            },
            "context": self.context.to_dict(),
            "metadata": self.metadata
        }


# =============================================================================
# WAYPOINT ANALYSIS SERVICE
# =============================================================================

class WaypointAnalysisService:
    """
    Service d'analyse complète centrée sur le waypoint.
    
    RESPONSABILITÉ:
    - Orchestrer tous les services pour produire une analyse complète
    - Le waypoint est le centre absolu de toute l'analyse
    - Intégrer SCORE_FINAL, Heatmap, et tous les sous-scores
    - Calculer les analyses locales (mobilité, pression, risques, densité)
    - Identifier les hotspots et transitions d'habitats
    - Produire des recommandations contextuelles
    
    ISOLATION:
    - N'effectue AUCUN calcul interne des scores
    - Appelle uniquement les services via leurs interfaces publiques
    """
    
    def __init__(self):
        """Initialise le service."""
        self._unified_scoring_service = get_unified_scoring_service()
        self._heatmap_fusion_service = get_heatmap_fusion_service()
        self._legal_hours_service = get_legal_hours_service()
        self._analysis_counter = 0
        
        logger.info("WaypointAnalysisService initialized")
    
    def _generate_analysis_id(self) -> str:
        """Génère un ID unique pour l'analyse."""
        self._analysis_counter += 1
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"WPA-{timestamp}-{self._analysis_counter:04d}"
    
    def analyze_waypoint(
        self, 
        context: WaypointAnalysisContext
    ) -> WaypointAnalysisResult:
        """
        Analyse complète centrée sur le waypoint.
        
        PROCESSUS:
        1. Calculer le SCORE_FINAL via UnifiedScoringService
        2. Générer la Heatmap via HeatmapFusionService
        3. Extraire les sous-scores locaux
        4. Identifier les hotspots à proximité
        5. Analyser mobilité, pression, risques, densité
        6. Détecter les transitions d'habitats
        7. Calculer les fenêtres optimales légales
        8. Générer les recommandations
        
        Args:
            context: Contexte d'analyse waypoint
            
        Returns:
            WaypointAnalysisResult complet
        """
        start_time = datetime.now(timezone.utc)
        analysis_id = self._generate_analysis_id()
        
        logger.info(f"[{analysis_id}] Starting waypoint analysis")
        logger.debug(f"[{analysis_id}] Waypoint: {context.waypoint_name} ({context.waypoint_id})")
        
        # ==== ÉTAPE 1: Calculer le SCORE_FINAL ====
        score_context = ScoreContext(
            waypoint_id=context.waypoint_id,
            latitude=context.latitude,
            longitude=context.longitude,
            target_datetime=context.target_datetime,
            species=context.species,
            region=context.region,
            search_radius_km=context.search_radius_km
        )
        
        unified_result = self._unified_scoring_service.calculate_unified_score(score_context)
        logger.info(f"[{analysis_id}] Unified score: {unified_result.final_score:.1f}")
        
        # ==== ÉTAPE 2: Générer la Heatmap ====
        wqs_input = WQSInput(
            waypoint_id=context.waypoint_id,
            wqs_score=context.wqs_score,
            success_history=context.wqs_success_history,
            weather_correlation=context.wqs_weather_correlation,
            activity_history=context.wqs_activity_history,
            accessibility=context.wqs_accessibility
        )
        
        heatmap_context = HeatmapFusionContext(
            waypoint_id=context.waypoint_id,
            latitude=context.latitude,
            longitude=context.longitude,
            target_datetime=context.target_datetime,
            species=context.species,
            wqs_input=wqs_input,
            grid_radius_km=context.search_radius_km,
            grid_resolution=context.grid_resolution,
            region=context.region
        )
        
        heatmap_result = self._heatmap_fusion_service.calculate_fused_heatmap(heatmap_context)
        logger.info(f"[{analysis_id}] Heatmap fused score: {heatmap_result.central_fused_score:.1f}")
        
        # ==== ÉTAPE 3: Extraire les sous-scores ====
        sub_scores = self._extract_sub_scores(unified_result)
        
        # ==== ÉTAPE 4: Identifier les hotspots à proximité ====
        hotspots = self._generate_nearby_hotspots(context, sub_scores)
        
        # ==== ÉTAPE 5: Analyses locales ====
        mobility_analysis = self._analyze_local_mobility(context, sub_scores)
        pressure_analysis = self._analyze_local_pressure(context, sub_scores)
        risk_analysis = self._analyze_local_risks(context, sub_scores)
        density_analysis = self._analyze_local_density(context, sub_scores)
        
        # ==== ÉTAPE 6: Transitions d'habitats ====
        habitat_transitions = self._detect_habitat_transitions(context)
        dominant_habitat = self._determine_dominant_habitat(context)
        
        # ==== ÉTAPE 7: Fenêtres optimales légales ====
        legal_window = self._legal_hours_service.get_legal_hunting_window(
            latitude=context.latitude,
            longitude=context.longitude,
            target_date=context.target_datetime.date(),
            region=context.region
        )
        
        legal_check = self._legal_hours_service.check_legal_status(
            target_time=context.target_datetime,
            latitude=context.latitude,
            longitude=context.longitude,
            region=context.region
        )
        
        optimal_windows = self._calculate_optimal_windows(context, legal_window, sub_scores)
        
        # ==== ÉTAPE 8: Recommandations ====
        recommendations = self._generate_recommendations(
            context, unified_result, heatmap_result,
            mobility_analysis, pressure_analysis,
            risk_analysis, density_analysis,
            legal_check.is_legal
        )
        
        # ==== Construire le résultat ====
        calc_time_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        
        result = WaypointAnalysisResult(
            analysis_id=analysis_id,
            calculated_at=datetime.now(timezone.utc),
            waypoint_id=context.waypoint_id,
            waypoint_name=context.waypoint_name,
            waypoint_coordinates=(context.latitude, context.longitude),
            unified_score=unified_result.final_score,
            unified_level=unified_result.final_level,
            fused_heatmap_score=heatmap_result.central_fused_score,
            wqs_score=context.wqs_score,
            hotspots_nearby=hotspots,
            mobility_analysis=mobility_analysis,
            pressure_analysis=pressure_analysis,
            risk_analysis=risk_analysis,
            density_analysis=density_analysis,
            habitat_transitions=habitat_transitions,
            dominant_habitat=dominant_habitat,
            optimal_windows=optimal_windows,
            legal_window=legal_window,
            is_legal_period=legal_check.is_legal,
            legal_status=legal_check.status,
            recommendations=recommendations,
            context=context,
            unified_score_id=unified_result.score_id,
            heatmap_id=heatmap_result.heatmap_id,
            metadata={
                "calculation_time_ms": round(calc_time_ms, 1),
                "hotspots_count": len(hotspots),
                "transitions_count": len(habitat_transitions),
                "version": "BIONIC-V5-ULTIME-WPA-1.0"
            }
        )
        
        logger.info(f"[{analysis_id}] Waypoint analysis completed in {calc_time_ms:.0f}ms")
        
        return result
    
    def _extract_sub_scores(self, unified_result: UnifiedScoreResult) -> Dict[str, float]:
        """Extrait les sous-scores du résultat unifié."""
        sub_scores = {}
        
        for breakdown in unified_result.score_breakdown:
            sub_scores[breakdown.category.value] = breakdown.raw_value
        
        return sub_scores
    
    def _generate_nearby_hotspots(
        self, 
        context: WaypointAnalysisContext,
        sub_scores: Dict[str, float]
    ) -> List[HotspotProximity]:
        """
        Génère les hotspots à proximité du waypoint.
        
        STRUCTURE UNIQUEMENT - Données simulées.
        """
        hotspots = []
        
        # Générer quelques hotspots simulés basés sur les sous-scores
        hotspot_types = [
            ("activity_peak", "Pic d'activité", 0.5, 45),
            ("feeding_zone", "Zone d'alimentation", 0.8, 120),
            ("rut_zone", "Zone de rut", 1.2, 200),
            ("thermal_refuge", "Refuge thermique", 1.5, 280),
            ("water_source", "Point d'eau", 0.9, 330)
        ]
        
        base_score = sub_scores.get("behavior", 50.0)
        
        for hs_type, name, dist, bearing in hotspot_types:
            if dist <= context.search_radius_km:
                # Score basé sur la distance et le score de comportement
                score = base_score * (1 - dist / context.search_radius_km * 0.3)
                
                hotspots.append(HotspotProximity(
                    hotspot_id=f"HS-{hs_type.upper()[:3]}-{int(dist*100):03d}",
                    hotspot_type=hs_type,
                    distance_km=dist,
                    bearing_degrees=bearing,
                    score=score,
                    species=[context.species],
                    optimal_window="Aube/Crépuscule",
                    is_reachable=dist <= 2.0,
                    travel_time_minutes=dist * 20  # ~3 km/h en forêt
                ))
        
        # Trier par score décroissant
        hotspots.sort(key=lambda h: h.score, reverse=True)
        
        return hotspots
    
    def _analyze_local_mobility(
        self, 
        context: WaypointAnalysisContext,
        sub_scores: Dict[str, float]
    ) -> LocalMobilityAnalysis:
        """Analyse de la mobilité locale."""
        mobility_score = sub_scores.get("mobility", 50.0)
        
        return LocalMobilityAnalysis(
            corridor_proximity_km=0.8,
            movement_probability=mobility_score / 100,
            daily_route_alignment=0.65,
            migration_relevance=0.3,
            territorial_stability=0.7,
            mobility_score=mobility_score,
            key_corridors=["Corridor Nord-Sud", "Route d'alimentation Est"]
        )
    
    def _analyze_local_pressure(
        self, 
        context: WaypointAnalysisContext,
        sub_scores: Dict[str, float]
    ) -> LocalPressureAnalysis:
        """Analyse de la pression locale."""
        pressure_score = sub_scores.get("pressure", 50.0)
        
        # Score inversé: haut = faible pression
        factors = []
        if pressure_score < 50:
            factors.append("Forte activité de chasse récente")
        if pressure_score < 70:
            factors.append("Proximité routes")
        
        return LocalPressureAnalysis(
            hunting_activity_index=100 - pressure_score,
            human_proximity_km=1.5,
            road_density_per_km2=0.8,
            disturbance_level=100 - pressure_score,
            pressure_score=pressure_score,
            pressure_factors=factors if factors else ["Pression modérée"]
        )
    
    def _analyze_local_risks(
        self, 
        context: WaypointAnalysisContext,
        sub_scores: Dict[str, float]
    ) -> LocalRiskAnalysis:
        """Analyse des risques locaux."""
        risk_score = sub_scores.get("risk", 50.0)
        
        # Déterminer le niveau de risque
        if risk_score >= 80:
            level = RiskLevel.LOW
        elif risk_score >= 60:
            level = RiskLevel.MODERATE
        elif risk_score >= 40:
            level = RiskLevel.HIGH
        else:
            level = RiskLevel.CRITICAL
        
        risk_factors = []
        mitigations = []
        
        if risk_score < 70:
            risk_factors.append("Présence potentielle de prédateurs")
            mitigations.append("Rester vigilant et éviter les déplacements isolés")
        if risk_score < 50:
            risk_factors.append("Terrain accidenté")
            mitigations.append("Prévoir équipement adapté")
        
        return LocalRiskAnalysis(
            risk_level=level,
            predator_presence=(100 - risk_score) / 100,
            natural_hazards=(100 - risk_score) / 200,
            regulated_zones_proximity_km=2.5,
            safety_score=risk_score,
            risk_factors=risk_factors if risk_factors else ["Risques faibles"],
            mitigation_suggestions=mitigations if mitigations else ["Conditions favorables"]
        )
    
    def _analyze_local_density(
        self, 
        context: WaypointAnalysisContext,
        sub_scores: Dict[str, float]
    ) -> LocalDensityAnalysis:
        """Analyse de la densité locale."""
        density_score = sub_scores.get("density", 50.0)
        
        # Estimation de densité basée sur le score
        estimated_density = density_score / 10  # 0-10 par km²
        
        # Tendance
        if density_score >= 70:
            trend = "increasing"
        elif density_score >= 40:
            trend = "stable"
        else:
            trend = "decreasing"
        
        factors = []
        if density_score >= 70:
            factors.append("Zone à forte densité de population")
        elif density_score >= 50:
            factors.append("Densité modérée")
        else:
            factors.append("Faible densité observée")
        
        return LocalDensityAnalysis(
            estimated_density_per_km2=estimated_density,
            observation_frequency=density_score / 100,
            population_trend=trend,
            density_score=density_score,
            density_factors=factors
        )
    
    def _detect_habitat_transitions(
        self, 
        context: WaypointAnalysisContext
    ) -> List[HabitatTransition]:
        """Détecte les transitions d'habitats."""
        transitions = []
        
        # Transitions simulées basées sur la position
        # En réalité, utiliserait des données géospatiales
        transitions.append(HabitatTransition(
            from_habitat=HabitatType.FOREST_MIXED,
            to_habitat=HabitatType.CLEARING,
            distance_km=0.4,
            bearing_degrees=60,
            transition_quality=85,
            species_relevance=0.9
        ))
        
        transitions.append(HabitatTransition(
            from_habitat=HabitatType.FOREST_MIXED,
            to_habitat=HabitatType.WETLAND,
            distance_km=0.7,
            bearing_degrees=180,
            transition_quality=75,
            species_relevance=0.7
        ))
        
        transitions.append(HabitatTransition(
            from_habitat=HabitatType.FOREST_DENSE,
            to_habitat=HabitatType.EDGE,
            distance_km=0.9,
            bearing_degrees=300,
            transition_quality=90,
            species_relevance=0.95
        ))
        
        return transitions
    
    def _determine_dominant_habitat(
        self, 
        context: WaypointAnalysisContext
    ) -> HabitatType:
        """Détermine l'habitat dominant autour du waypoint."""
        # Simulation - en réalité utiliserait des données géospatiales
        return HabitatType.FOREST_MIXED
    
    def _calculate_optimal_windows(
        self, 
        context: WaypointAnalysisContext,
        legal_window: LegalHuntingWindow,
        sub_scores: Dict[str, float]
    ) -> List[OptimalWindowRecommendation]:
        """Calcule les fenêtres optimales légales."""
        windows = []
        
        behavior_score = sub_scores.get("behavior", 50.0)
        
        # Fenêtre Aube
        windows.append(OptimalWindowRecommendation(
            period="dawn",
            start_time=legal_window.start_time.strftime("%H:%M"),
            end_time=(legal_window.sunrise.strftime("%H:%M") if hasattr(legal_window, 'sunrise') 
                      else legal_window.start_time.strftime("%H:%M")),
            score=behavior_score * 1.2,
            quality="excellent" if behavior_score >= 70 else "good",
            species_activity="Activité maximale",
            legal_badge="⚖️ LÉGAL",
            recommendation=f"Meilleur créneau pour {context.species}"
        ))
        
        # Fenêtre Crépuscule
        windows.append(OptimalWindowRecommendation(
            period="dusk",
            start_time=(legal_window.sunset.strftime("%H:%M") if hasattr(legal_window, 'sunset')
                        else "17:00"),
            end_time=legal_window.end_time.strftime("%H:%M"),
            score=behavior_score * 1.15,
            quality="excellent" if behavior_score >= 70 else "good",
            species_activity="Activité maximale",
            legal_badge="⚖️ LÉGAL",
            recommendation="Excellente fenêtre de fin de journée"
        ))
        
        # Fenêtre Matin
        windows.append(OptimalWindowRecommendation(
            period="morning",
            start_time="08:00",
            end_time="11:00",
            score=behavior_score * 0.7,
            quality="moderate",
            species_activity="Activité modérée",
            legal_badge="⚖️ LÉGAL",
            recommendation="Activité en déclin progressif"
        ))
        
        # Trier par score
        windows.sort(key=lambda w: w.score, reverse=True)
        
        return windows
    
    def _generate_recommendations(
        self,
        context: WaypointAnalysisContext,
        unified_result: UnifiedScoreResult,
        heatmap_result: HeatmapUnifieeResult,
        mobility: LocalMobilityAnalysis,
        pressure: LocalPressureAnalysis,
        risk: LocalRiskAnalysis,
        density: LocalDensityAnalysis,
        is_legal: bool
    ) -> List[str]:
        """Génère les recommandations contextuelles."""
        recommendations = []
        
        # Recommandation légale
        if not is_legal:
            recommendations.append("❌ Hors heures légales - chasse non autorisée")
            return recommendations
        
        # Score global
        if unified_result.final_score >= 70:
            recommendations.append(f"✅ Conditions excellentes pour {context.species}")
        elif unified_result.final_score >= 50:
            recommendations.append(f"⚠️ Conditions modérées - privilégiez les fenêtres optimales")
        else:
            recommendations.append(f"❌ Conditions défavorables - envisagez de reporter")
        
        # Mobilité
        if mobility.mobility_score >= 70:
            recommendations.append("✅ Bonne probabilité de mouvement - position stratégique")
        
        # Pression
        if pressure.pressure_score < 50:
            recommendations.append("⚠️ Zone sous pression - le gibier peut être méfiant")
        
        # Densité
        if density.density_score >= 70:
            recommendations.append(f"✅ Forte densité de {context.species} observée")
        elif density.density_score < 40:
            recommendations.append(f"⚠️ Faible densité - élargissez votre zone")
        
        # Risques
        if risk.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            recommendations.append("⚠️ Attention aux risques - consultez l'analyse détaillée")
        
        # Corridor
        if mobility.corridor_proximity_km < 1.0:
            recommendations.append("✅ Proximité d'un corridor de déplacement")
        
        return recommendations[:6]


# =============================================================================
# SINGLETON
# =============================================================================

_waypoint_analysis_service: Optional[WaypointAnalysisService] = None


def get_waypoint_analysis_service() -> WaypointAnalysisService:
    """Retourne l'instance singleton du service."""
    global _waypoint_analysis_service
    if _waypoint_analysis_service is None:
        _waypoint_analysis_service = WaypointAnalysisService()
    return _waypoint_analysis_service


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'WaypointAnalysisService',
    'get_waypoint_analysis_service',
    'WaypointAnalysisResult',
    'WaypointAnalysisContext',
    'HotspotProximity',
    'LocalMobilityAnalysis',
    'LocalPressureAnalysis',
    'LocalRiskAnalysis',
    'LocalDensityAnalysis',
    'HabitatTransition',
    'OptimalWindowRecommendation',
    'HabitatType',
    'RiskLevel'
]
