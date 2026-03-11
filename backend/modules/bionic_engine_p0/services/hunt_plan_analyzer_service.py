"""
BIONIC ENGINE - Hunt Plan Analyzer Service
PHASE P1-FINAL — Orchestrateur d'Analyse du Plan de Chasse

Service d'orchestration qui combine:
- HotspotService (génération de hotspots organiques)
- WeatherService (conditions météorologiques)
- DynamicScoringService (scores comportementaux)

FONCTIONNALITÉS:
- Analyse consolidée du plan de chasse
- Synthèse par espèce avec score final
- Fenêtres optimales d'observation
- Recommandations contextuelles
- Architecture préparant P2 (Moteur de Recommandations)

Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from modules.bionic_engine_p0.services.hotspot_service import (
    HotspotService,
    HotspotRequest,
    BoundsInput
)
from modules.bionic_engine_p0.services.weather_service import (
    get_weather_service,
    WeatherResponse,
    ServiceStatus as WeatherServiceStatus
)
from modules.bionic_engine_p0.services.dynamic_scoring_service import (
    get_scoring_service,
    WeatherInputs,
    HotspotScore,
    ScoreLevel
)

logger = logging.getLogger(__name__)


# =============================================================================
# DATA CONTRACTS
# =============================================================================

class AnalysisQuality(str, Enum):
    """Qualité de l'analyse basée sur les données disponibles."""
    FULL = "full"           # Météo réelle + tous les services actifs
    PARTIAL = "partial"     # Météo inactive, scores de base seulement
    MINIMAL = "minimal"     # Données minimales disponibles


@dataclass
class SpeciesSynthesis:
    """Synthèse pour une espèce donnée."""
    species: str
    species_label: str
    total_hotspots: int
    average_base_score: float
    average_final_score: float
    score_improvement: float  # Différence finale - base
    best_hotspot_id: Optional[str]
    best_hotspot_score: float
    hotspots_by_type: Dict[str, int]
    optimal_windows: List[Dict[str, Any]]
    recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "species": self.species,
            "species_label": self.species_label,
            "total_hotspots": self.total_hotspots,
            "scores": {
                "average_base": round(self.average_base_score, 1),
                "average_final": round(self.average_final_score, 1),
                "improvement": round(self.score_improvement, 1)
            },
            "best_hotspot": {
                "id": self.best_hotspot_id,
                "score": round(self.best_hotspot_score, 1)
            } if self.best_hotspot_id else None,
            "hotspots_by_type": self.hotspots_by_type,
            "optimal_windows": self.optimal_windows,
            "recommendations": self.recommendations
        }


@dataclass
class GlobalOptimalWindow:
    """Fenêtre optimale globale tous espèces confondues."""
    period: str
    start_hour: int
    end_hour: int
    quality: str
    species_active: List[str]
    combined_score: float
    description: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "period": self.period,
            "time_range": f"{self.start_hour:02d}:00 - {self.end_hour:02d}:00",
            "quality": self.quality,
            "species_active": self.species_active,
            "combined_score": round(self.combined_score, 1),
            "description": self.description
        }


@dataclass
class WeatherSummary:
    """Résumé des conditions météorologiques."""
    status: str
    current_conditions: Optional[Dict[str, Any]]
    behavior_factors: Optional[Dict[str, Any]]
    pressure_trend: str
    overall_impact: str  # "favorable", "neutral", "unfavorable"
    key_factors: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "current_conditions": self.current_conditions,
            "behavior_factors": self.behavior_factors,
            "pressure_trend": self.pressure_trend,
            "overall_impact": self.overall_impact,
            "key_factors": self.key_factors
        }


@dataclass
class HuntPlanAnalysis:
    """Analyse complète du plan de chasse."""
    success: bool
    analysis_id: str
    generated_at: datetime
    quality: AnalysisQuality
    bounds: Dict[str, float]
    time_range: str
    
    # Données globales
    total_hotspots: int
    global_average_score: float
    global_score_level: ScoreLevel
    
    # Synthèse par espèce
    species_synthesis: List[SpeciesSynthesis]
    
    # Fenêtres optimales globales
    global_optimal_windows: List[GlobalOptimalWindow]
    
    # Météo
    weather_summary: WeatherSummary
    
    # Recommandations globales
    global_recommendations: List[str]
    
    # Hotspots scorés (optionnel, pour visualisation)
    scored_hotspots: List[Dict[str, Any]]
    
    # Métadonnées
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "analysis_id": self.analysis_id,
            "generated_at": self.generated_at.isoformat(),
            "quality": self.quality.value,
            "request": {
                "bounds": self.bounds,
                "time_range": self.time_range
            },
            "summary": {
                "total_hotspots": self.total_hotspots,
                "global_average_score": round(self.global_average_score, 1),
                "global_score_level": self.global_score_level.value
            },
            "species_synthesis": [s.to_dict() for s in self.species_synthesis],
            "global_optimal_windows": [w.to_dict() for w in self.global_optimal_windows],
            "weather": self.weather_summary.to_dict(),
            "global_recommendations": self.global_recommendations,
            "scored_hotspots": self.scored_hotspots,
            "metadata": self.metadata
        }


# =============================================================================
# SPECIES LABELS
# =============================================================================

SPECIES_LABELS = {
    "moose": "Orignal",
    "deer": "Chevreuil",
    "bear": "Ours noir",
    "wild_turkey": "Dindon sauvage",
    "elk": "Wapiti",
    "caribou": "Caribou"
}


# =============================================================================
# HUNT PLAN ANALYZER SERVICE
# =============================================================================

class HuntPlanAnalyzerService:
    """
    Service d'analyse du plan de chasse BIONIC V5.
    
    Orchestre les services HotspotService, WeatherService et DynamicScoringService
    pour produire une analyse consolidée du potentiel de chasse.
    
    ARCHITECTURE P2-READY:
    - Structure modulaire permettant l'ajout du moteur de recommandations
    - Données normalisées pour l'entraînement ML futur
    - Interfaces extensibles pour intégrations additionnelles
    """
    
    def __init__(self):
        self._hotspot_service = HotspotService()
        self._weather_service = get_weather_service()
        self._scoring_service = get_scoring_service()
        self._analysis_counter = 0
    
    def _generate_analysis_id(self) -> str:
        """Génère un ID unique pour l'analyse."""
        self._analysis_counter += 1
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"HPA-{timestamp}-{self._analysis_counter:04d}"
    
    async def analyze_hunt_plan(
        self,
        bounds: Dict[str, float],
        species: List[str],
        time_range: str = "24h",
        hotspot_types: Optional[List[str]] = None,
        min_score_threshold: int = 70,
        include_scored_hotspots: bool = True,
        target_datetime: Optional[datetime] = None
    ) -> HuntPlanAnalysis:
        """
        Analyse complète du plan de chasse.
        
        Args:
            bounds: Zone géographique {north, south, east, west}
            species: Liste des espèces à analyser
            time_range: Plage temporelle ("24h", "72h", "7d")
            hotspot_types: Types de hotspots à générer
            min_score_threshold: Seuil minimum de score
            include_scored_hotspots: Inclure les hotspots scorés dans la réponse
            target_datetime: Date/heure cible (défaut: maintenant)
            
        Returns:
            HuntPlanAnalysis avec tous les résultats
        """
        start_time = datetime.now(timezone.utc)
        analysis_id = self._generate_analysis_id()
        target_dt = target_datetime or datetime.now(timezone.utc)
        
        # Types de hotspots par défaut
        if hotspot_types is None:
            hotspot_types = ["activity_peak", "feeding_zone", "rut_zone"]
        
        logger.info(f"[{analysis_id}] Démarrage analyse plan de chasse")
        logger.info(f"[{analysis_id}] Zone: {bounds}")
        logger.info(f"[{analysis_id}] Espèces: {species}")
        
        # ==== ÉTAPE 1: Générer les hotspots ====
        hotspot_request = HotspotRequest(
            bounds=BoundsInput(**bounds),
            species=species,
            time_range=time_range,
            hotspot_types=hotspot_types,
            min_score_threshold=min_score_threshold
        )
        
        hotspot_response = self._hotspot_service.generate_hotspots(hotspot_request)
        hotspots = hotspot_response.hotspots
        
        logger.info(f"[{analysis_id}] {len(hotspots)} hotspots générés")
        
        # ==== ÉTAPE 2: Récupérer la météo ====
        center_lat = (bounds["north"] + bounds["south"]) / 2
        center_lng = (bounds["east"] + bounds["west"]) / 2
        
        weather_response = await self._weather_service.get_weather(
            center_lat, center_lng,
            include_forecast=True,
            include_behavior=True
        )
        
        weather_active = weather_response.status == WeatherServiceStatus.ACTIVE
        weather_data = weather_response.to_dict() if weather_active else None
        
        logger.info(f"[{analysis_id}] Météo: {'active' if weather_active else 'inactive'}")
        
        # ==== ÉTAPE 3: Calculer les scores dynamiques ====
        weather_inputs = None
        if weather_active and weather_data:
            weather_inputs = WeatherInputs.from_weather_response(weather_data)
        
        scored_hotspots_data = []
        species_data: Dict[str, List[HotspotScore]] = {sp: [] for sp in species}
        
        for hotspot in hotspots:
            # Extraire les coordonnées du centre du hotspot
            coords = hotspot.geometry["coordinates"][0]
            center_lat_hs = sum(c[1] for c in coords) / len(coords)
            center_lng_hs = sum(c[0] for c in coords) / len(coords)
            
            # Calculer le score dynamique
            hotspot_score = self._scoring_service.calculate_hotspot_score(
                hotspot_id=hotspot.id,
                base_score=hotspot.score,
                latitude=center_lat_hs,
                longitude=center_lng_hs,
                species=hotspot.species[0] if hotspot.species else "moose",
                weather_inputs=weather_inputs,
                target_datetime=target_dt
            )
            
            # Grouper par espèce
            for sp in hotspot.species:
                if sp in species_data:
                    species_data[sp].append(hotspot_score)
            
            # Ajouter aux hotspots scorés
            if include_scored_hotspots:
                scored_hotspots_data.append({
                    "hotspot_id": hotspot.id,
                    "type": hotspot.type,
                    "species": hotspot.species,
                    "geometry": hotspot.geometry,
                    "base_score": hotspot.score,
                    "final_score": hotspot_score.final_score,
                    "score_delta": hotspot_score.score_delta,
                    "dynamic_score": {
                        "composite": hotspot_score.dynamic_score.composite_score,
                        "level": hotspot_score.dynamic_score.level.value,
                        "recommendations": hotspot_score.dynamic_score.recommendations[:3]
                    },
                    "style": {
                        "stroke_color": hotspot.style.stroke_color,
                        "stroke_width": hotspot.style.stroke_width,
                        "fill_opacity": hotspot.style.fill_opacity
                    },
                    "time_validity": {
                        "start": hotspot.time_validity.start,
                        "end": hotspot.time_validity.end,
                        "optimal_hours": hotspot.time_validity.optimal_hours
                    }
                })
        
        logger.info(f"[{analysis_id}] {len(scored_hotspots_data)} hotspots scorés")
        
        # ==== ÉTAPE 4: Générer la synthèse par espèce ====
        species_synthesis = []
        all_scores = []
        
        for sp in species:
            sp_scores = species_data.get(sp, [])
            if not sp_scores:
                continue
            
            # Calculer les moyennes
            base_scores = [s.base_score for s in sp_scores]
            final_scores = [s.final_score for s in sp_scores]
            
            avg_base = sum(base_scores) / len(base_scores)
            avg_final = sum(final_scores) / len(final_scores)
            
            # Meilleur hotspot
            best = max(sp_scores, key=lambda s: s.final_score)
            
            # Comptage par type
            type_counts: Dict[str, int] = {}
            for hs in hotspots:
                if sp in hs.species:
                    type_counts[hs.type] = type_counts.get(hs.type, 0) + 1
            
            # Fenêtres optimales (depuis le premier score)
            optimal_windows = []
            if sp_scores and sp_scores[0].dynamic_score.optimal_windows:
                optimal_windows = sp_scores[0].dynamic_score.optimal_windows
            
            # Recommandations agrégées
            recommendations = self._aggregate_recommendations(sp_scores, sp)
            
            synthesis = SpeciesSynthesis(
                species=sp,
                species_label=SPECIES_LABELS.get(sp, sp.capitalize()),
                total_hotspots=len(sp_scores),
                average_base_score=avg_base,
                average_final_score=avg_final,
                score_improvement=avg_final - avg_base,
                best_hotspot_id=best.hotspot_id,
                best_hotspot_score=best.final_score,
                hotspots_by_type=type_counts,
                optimal_windows=optimal_windows,
                recommendations=recommendations
            )
            
            species_synthesis.append(synthesis)
            all_scores.extend(final_scores)
        
        # ==== ÉTAPE 5: Calculer les métriques globales ====
        global_avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
        global_level = self._get_global_level(global_avg_score)
        
        # ==== ÉTAPE 6: Générer les fenêtres optimales globales ====
        global_windows = self._calculate_global_windows(species_synthesis, weather_inputs)
        
        # ==== ÉTAPE 7: Résumé météo ====
        weather_summary = self._create_weather_summary(weather_response, weather_data)
        
        # ==== ÉTAPE 8: Recommandations globales ====
        global_recommendations = self._generate_global_recommendations(
            species_synthesis, weather_summary, global_avg_score
        )
        
        # ==== ÉTAPE 9: Déterminer la qualité de l'analyse ====
        quality = AnalysisQuality.FULL if weather_active else AnalysisQuality.PARTIAL
        if len(hotspots) == 0:
            quality = AnalysisQuality.MINIMAL
        
        # ==== ÉTAPE 10: Construire la réponse ====
        calc_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        
        analysis = HuntPlanAnalysis(
            success=True,
            analysis_id=analysis_id,
            generated_at=datetime.now(timezone.utc),
            quality=quality,
            bounds=bounds,
            time_range=time_range,
            total_hotspots=len(hotspots),
            global_average_score=global_avg_score,
            global_score_level=global_level,
            species_synthesis=species_synthesis,
            global_optimal_windows=global_windows,
            weather_summary=weather_summary,
            global_recommendations=global_recommendations,
            scored_hotspots=scored_hotspots_data,
            metadata={
                "calculation_time_ms": round(calc_time, 1),
                "services": {
                    "hotspots": "active",
                    "weather": "active" if weather_active else "inactive",
                    "scoring": "active"
                },
                "hotspot_config": {
                    "types": hotspot_types,
                    "min_threshold": min_score_threshold
                },
                "version": "P1-FINAL-1.0"
            }
        )
        
        logger.info(f"[{analysis_id}] Analyse terminée en {calc_time:.0f}ms")
        
        return analysis
    
    def _aggregate_recommendations(
        self,
        scores: List[HotspotScore],
        species: str
    ) -> List[str]:
        """Agrège les recommandations pour une espèce."""
        all_recs: Dict[str, int] = {}
        
        for score in scores:
            for rec in score.dynamic_score.recommendations:
                all_recs[rec] = all_recs.get(rec, 0) + 1
        
        # Trier par fréquence et prendre les top 5
        sorted_recs = sorted(all_recs.items(), key=lambda x: x[1], reverse=True)
        
        # Ajouter des recommandations spécifiques à l'espèce
        species_recs = {
            "moose": "L'orignal est plus actif aux crépuscules - privilégiez l'aube et le coucher de soleil",
            "deer": "Le chevreuil réagit fortement aux changements de pression atmosphérique",
            "bear": "L'ours noir est moins actif par temps de pluie - surveillez les accalmies"
        }
        
        result = [rec for rec, _ in sorted_recs[:4]]
        if species in species_recs and len(result) < 5:
            result.append(species_recs[species])
        
        return result[:5]
    
    def _get_global_level(self, score: float) -> ScoreLevel:
        """Détermine le niveau global du score."""
        if score >= 85:
            return ScoreLevel.EXCELLENT
        elif score >= 70:
            return ScoreLevel.GOOD
        elif score >= 50:
            return ScoreLevel.MODERATE
        elif score >= 30:
            return ScoreLevel.POOR
        else:
            return ScoreLevel.VERY_POOR
    
    def _calculate_global_windows(
        self,
        species_synthesis: List[SpeciesSynthesis],
        weather_inputs: Optional[WeatherInputs]
    ) -> List[GlobalOptimalWindow]:
        """Calcule les fenêtres optimales globales."""
        windows = []
        
        # Collecter toutes les fenêtres par période
        period_data: Dict[str, Dict[str, Any]] = {}
        
        for synthesis in species_synthesis:
            for window in synthesis.optimal_windows:
                period = window.get("period", "unknown")
                if period not in period_data:
                    period_data[period] = {
                        "start_hour": window.get("start_hour", 6),
                        "end_hour": window.get("end_hour", 8),
                        "quality": window.get("quality", "moderate"),
                        "species": [],
                        "scores": [],
                        "description": window.get("description", "")
                    }
                
                period_data[period]["species"].append(synthesis.species)
                period_data[period]["scores"].append(synthesis.average_final_score)
        
        # Créer les fenêtres globales
        for period, data in period_data.items():
            combined_score = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 50
            
            windows.append(GlobalOptimalWindow(
                period=period,
                start_hour=data["start_hour"],
                end_hour=data["end_hour"],
                quality=data["quality"],
                species_active=list(set(data["species"])),
                combined_score=combined_score,
                description=data["description"]
            ))
        
        # Si aucune fenêtre, créer des défauts
        if not windows:
            sunrise = weather_inputs.sunrise_hour if weather_inputs else 6
            sunset = weather_inputs.sunset_hour if weather_inputs else 18
            
            windows = [
                GlobalOptimalWindow(
                    period="dawn",
                    start_hour=sunrise - 1,
                    end_hour=sunrise + 2,
                    quality="optimal",
                    species_active=[s.species for s in species_synthesis],
                    combined_score=75.0,
                    description="Aube - période d'activité maximale"
                ),
                GlobalOptimalWindow(
                    period="dusk",
                    start_hour=sunset - 2,
                    end_hour=sunset + 1,
                    quality="optimal",
                    species_active=[s.species for s in species_synthesis],
                    combined_score=75.0,
                    description="Crépuscule - période d'activité maximale"
                )
            ]
        
        return sorted(windows, key=lambda w: w.combined_score, reverse=True)
    
    def _create_weather_summary(
        self,
        weather_response: WeatherResponse,
        weather_data: Optional[Dict[str, Any]]
    ) -> WeatherSummary:
        """Crée le résumé météo."""
        if weather_response.status != WeatherServiceStatus.ACTIVE:
            return WeatherSummary(
                status="inactive",
                current_conditions=None,
                behavior_factors=None,
                pressure_trend="unknown",
                overall_impact="neutral",
                key_factors=["Service météo inactif - données simulées utilisées"]
            )
        
        # Extraire les données
        current = weather_data.get("current", {}) if weather_data else {}
        behavior = weather_data.get("behavior_factors", {}) if weather_data else {}
        
        # Déterminer l'impact global
        activity_mod = behavior.get("activity_modifier", 0)
        if activity_mod > 0.2:
            overall_impact = "favorable"
        elif activity_mod < -0.2:
            overall_impact = "unfavorable"
        else:
            overall_impact = "neutral"
        
        # Facteurs clés
        key_factors = behavior.get("risk_factors", [])[:3]
        if not key_factors:
            key_factors = ["Conditions météo normales"]
        
        return WeatherSummary(
            status="active",
            current_conditions={
                "temperature": current.get("temperature"),
                "humidity": current.get("humidity"),
                "wind_speed": current.get("wind", {}).get("speed"),
                "condition": current.get("condition"),
                "visibility": current.get("visibility")
            },
            behavior_factors={
                "activity_modifier": behavior.get("activity_modifier"),
                "feeding_modifier": behavior.get("feeding_modifier"),
                "movement_modifier": behavior.get("movement_modifier")
            },
            pressure_trend=behavior.get("pressure_trend", "stable"),
            overall_impact=overall_impact,
            key_factors=key_factors
        )
    
    def _generate_global_recommendations(
        self,
        species_synthesis: List[SpeciesSynthesis],
        weather_summary: WeatherSummary,
        global_score: float
    ) -> List[str]:
        """Génère les recommandations globales."""
        recommendations = []
        
        # Recommandation basée sur le score global
        if global_score >= 80:
            recommendations.append("Conditions excellentes - journée idéale pour la chasse")
        elif global_score >= 60:
            recommendations.append("Bonnes conditions - potentiel d'observation élevé")
        elif global_score >= 40:
            recommendations.append("Conditions modérées - privilégiez les créneaux optimaux")
        else:
            recommendations.append("Conditions difficiles - reportez si possible")
        
        # Recommandation météo
        if weather_summary.status == "inactive":
            recommendations.append("Activez la météo réelle (OWM_API_KEY) pour une analyse plus précise")
        elif weather_summary.overall_impact == "favorable":
            recommendations.append("La météo favorise l'activité du gibier")
        elif weather_summary.overall_impact == "unfavorable":
            recommendations.append("Conditions météo défavorables - adaptez votre approche")
        
        # Recommandation pression
        if weather_summary.pressure_trend == "falling":
            recommendations.append("Pression en baisse - anticipez une augmentation de l'activité")
        elif weather_summary.pressure_trend == "rising":
            recommendations.append("Pression en hausse - conditions stables à venir")
        
        # Recommandation multi-espèces
        if len(species_synthesis) > 1:
            best_species = max(species_synthesis, key=lambda s: s.average_final_score)
            recommendations.append(
                f"Meilleur potentiel: {best_species.species_label} (score: {best_species.average_final_score:.0f})"
            )
        
        # Recommandation zone
        if species_synthesis:
            total_hs = sum(s.total_hotspots for s in species_synthesis)
            if total_hs > 20:
                recommendations.append("Zone riche en hotspots - explorez méthodiquement")
            elif total_hs < 5:
                recommendations.append("Peu de hotspots - élargissez la zone de recherche")
        
        return recommendations[:6]


# =============================================================================
# SINGLETON
# =============================================================================

_analyzer_service: Optional[HuntPlanAnalyzerService] = None


def get_hunt_plan_analyzer_service() -> HuntPlanAnalyzerService:
    """Retourne l'instance singleton du service d'analyse."""
    global _analyzer_service
    if _analyzer_service is None:
        _analyzer_service = HuntPlanAnalyzerService()
    return _analyzer_service


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'HuntPlanAnalyzerService',
    'get_hunt_plan_analyzer_service',
    'HuntPlanAnalysis',
    'SpeciesSynthesis',
    'GlobalOptimalWindow',
    'WeatherSummary',
    'AnalysisQuality'
]
