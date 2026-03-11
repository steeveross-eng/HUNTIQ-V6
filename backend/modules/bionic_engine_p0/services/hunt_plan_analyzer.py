"""
BIONIC ENGINE - Hunt Plan Analysis Service
PHASE P1-FINAL — Service d'Analyse de Plan de Chasse

Service d'analyse complète combinant:
- Génération de hotspots
- Scoring dynamique
- Données météorologiques
- Fenêtres temporelles optimales
- Synthèse comportementale par espèce

Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


# =============================================================================
# DATA CONTRACTS
# =============================================================================

class AnalysisConfidence(str, Enum):
    """Niveau de confiance de l'analyse."""
    HIGH = "high"        # Météo active + données complètes
    MEDIUM = "medium"    # Météo inactive ou partielles
    LOW = "low"          # Données minimales


class HuntingCondition(str, Enum):
    """Condition générale de chasse."""
    EXCELLENT = "excellent"    # Score >= 80
    GOOD = "good"              # Score >= 65
    MODERATE = "moderate"      # Score >= 50
    POOR = "poor"              # Score >= 35
    UNFAVORABLE = "unfavorable"  # Score < 35


@dataclass
class TimeWindow:
    """Fenêtre temporelle d'opportunité."""
    period: str  # "dawn", "dusk", "midday", etc.
    start_hour: int
    end_hour: int
    quality: str  # "excellent", "good", "moderate"
    score: float
    description: str
    factors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "period": self.period,
            "time_range": f"{self.start_hour:02d}h00 - {self.end_hour:02d}h00",
            "start_hour": self.start_hour,
            "end_hour": self.end_hour,
            "quality": self.quality,
            "score": round(self.score, 1),
            "description": self.description,
            "factors": self.factors
        }


@dataclass
class SpeciesSummary:
    """Synthèse comportementale pour une espèce."""
    species: str
    species_name: str  # Nom français
    hotspot_count: int
    average_score: float
    best_score: float
    worst_score: float
    primary_behaviors: List[str]
    activity_level: str  # "high", "moderate", "low"
    feeding_probability: float
    movement_probability: float
    optimal_windows: List[TimeWindow]
    key_factors: List[str]
    recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "species": self.species,
            "species_name": self.species_name,
            "statistics": {
                "hotspot_count": self.hotspot_count,
                "average_score": round(self.average_score, 1),
                "best_score": round(self.best_score, 1),
                "worst_score": round(self.worst_score, 1)
            },
            "behavior": {
                "primary_behaviors": self.primary_behaviors,
                "activity_level": self.activity_level,
                "feeding_probability": round(self.feeding_probability, 2),
                "movement_probability": round(self.movement_probability, 2)
            },
            "optimal_windows": [w.to_dict() for w in self.optimal_windows],
            "key_factors": self.key_factors,
            "recommendations": self.recommendations
        }


@dataclass
class HotspotAnalysis:
    """Analyse d'un hotspot individuel."""
    hotspot_id: str
    type: str
    species: List[str]
    base_score: float
    dynamic_score: float
    final_score: float
    rank: int
    location: Tuple[float, float]
    area_m2: float
    time_validity: Dict[str, Any]
    score_components: Dict[str, float]
    key_factors: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "hotspot_id": self.hotspot_id,
            "type": self.type,
            "species": self.species,
            "scores": {
                "base": round(self.base_score, 1),
                "dynamic": round(self.dynamic_score, 1),
                "final": round(self.final_score, 1)
            },
            "rank": self.rank,
            "location": {
                "latitude": self.location[0],
                "longitude": self.location[1]
            },
            "area_m2": round(self.area_m2, 0),
            "time_validity": self.time_validity,
            "score_breakdown": {k: round(v, 1) for k, v in self.score_components.items()},
            "key_factors": self.key_factors
        }


@dataclass
class WeatherSummary:
    """Résumé météo pour l'analyse."""
    available: bool
    status: str
    current: Optional[Dict[str, Any]] = None
    trend: Optional[str] = None
    impact_score: float = 0.0
    alerts: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "available": self.available,
            "status": self.status,
            "current": self.current,
            "trend": self.trend,
            "impact_score": round(self.impact_score, 1),
            "alerts": self.alerts
        }


@dataclass
class HuntPlanAnalysis:
    """Analyse complète du plan de chasse."""
    analysis_id: str
    timestamp: datetime
    bounds: Dict[str, float]
    target_datetime: datetime
    time_range_hours: int
    
    # Résultats principaux
    overall_condition: HuntingCondition
    overall_score: float
    confidence: AnalysisConfidence
    
    # Données météo
    weather: WeatherSummary
    
    # Hotspots analysés
    hotspots: List[HotspotAnalysis]
    hotspot_count: int
    
    # Synthèses par espèce
    species_summaries: List[SpeciesSummary]
    
    # Fenêtres optimales globales
    optimal_windows: List[TimeWindow]
    
    # Recommandations générales
    executive_summary: str
    key_insights: List[str]
    action_items: List[str]
    
    # Métadonnées
    calculation_time_ms: float
    data_sources: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "analysis_id": self.analysis_id,
            "timestamp": self.timestamp.isoformat(),
            "parameters": {
                "bounds": self.bounds,
                "target_datetime": self.target_datetime.isoformat(),
                "time_range_hours": self.time_range_hours
            },
            "results": {
                "overall_condition": self.overall_condition.value,
                "overall_score": round(self.overall_score, 1),
                "confidence": self.confidence.value
            },
            "weather": self.weather.to_dict(),
            "hotspots": {
                "count": self.hotspot_count,
                "items": [h.to_dict() for h in self.hotspots]
            },
            "species_analysis": [s.to_dict() for s in self.species_summaries],
            "optimal_windows": [w.to_dict() for w in self.optimal_windows],
            "insights": {
                "executive_summary": self.executive_summary,
                "key_insights": self.key_insights,
                "action_items": self.action_items
            },
            "metadata": {
                "calculation_time_ms": round(self.calculation_time_ms, 1),
                "data_sources": self.data_sources
            }
        }


# =============================================================================
# HUNT PLAN ANALYZER SERVICE
# =============================================================================

class HuntPlanAnalyzer:
    """
    Service d'analyse de plan de chasse BIONIC V5.
    
    Combine hotspots, scoring dynamique et météo pour produire
    une analyse complète avec recommandations.
    """
    
    # Noms français des espèces
    SPECIES_NAMES = {
        "moose": "Orignal",
        "deer": "Chevreuil",
        "bear": "Ours noir",
        "wild_turkey": "Dindon sauvage",
        "elk": "Wapiti"
    }
    
    # Types de hotspots traduits
    HOTSPOT_TYPES = {
        "activity_peak": "Pic d'activité",
        "feeding_zone": "Zone d'alimentation",
        "rut_zone": "Zone de rut",
        "thermal_refuge": "Refuge thermique",
        "water_source": "Point d'eau",
        "composite_optimal": "Zone optimale"
    }
    
    def __init__(self):
        self._analysis_counter = 0
    
    def _generate_analysis_id(self) -> str:
        """Génère un ID unique pour l'analyse."""
        self._analysis_counter += 1
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"HPA-{timestamp}-{self._analysis_counter:04d}"
    
    async def analyze(
        self,
        bounds: Dict[str, float],
        species: List[str],
        target_datetime: Optional[datetime] = None,
        time_range_hours: int = 24,
        hotspots_data: Optional[List[Dict]] = None,
        weather_data: Optional[Dict] = None,
        scoring_service: Optional[Any] = None
    ) -> HuntPlanAnalysis:
        """
        Effectue une analyse complète du plan de chasse.
        
        Args:
            bounds: Zone d'analyse {north, south, east, west}
            species: Liste des espèces cibles
            target_datetime: Date/heure cible
            time_range_hours: Durée de l'analyse
            hotspots_data: Données de hotspots (si déjà générés)
            weather_data: Données météo (si déjà récupérées)
            scoring_service: Service de scoring (injection)
            
        Returns:
            HuntPlanAnalysis complète
        """
        import time
        start_time = time.time()
        
        now = target_datetime or datetime.now(timezone.utc)
        
        # Initialiser les sources de données
        data_sources = ["bionic_hotspots", "dynamic_scoring"]
        
        # Traiter la météo
        weather_summary = self._process_weather(weather_data)
        if weather_summary.available:
            data_sources.append("openweathermap")
        
        # Traiter les hotspots
        hotspot_analyses = []
        if hotspots_data:
            hotspot_analyses = self._analyze_hotspots(
                hotspots_data, weather_data, scoring_service, now
            )
        
        # Générer les synthèses par espèce
        species_summaries = self._generate_species_summaries(
            species, hotspot_analyses, weather_summary, now
        )
        
        # Calculer les fenêtres optimales globales
        optimal_windows = self._calculate_global_windows(
            weather_summary, species, now
        )
        
        # Calculer le score global
        overall_score = self._calculate_overall_score(
            hotspot_analyses, weather_summary, species_summaries
        )
        
        # Déterminer la condition globale
        overall_condition = self._determine_condition(overall_score)
        
        # Déterminer le niveau de confiance
        confidence = self._determine_confidence(weather_summary, hotspot_analyses)
        
        # Générer les insights
        executive_summary = self._generate_executive_summary(
            overall_condition, overall_score, species_summaries, weather_summary
        )
        
        key_insights = self._generate_key_insights(
            hotspot_analyses, species_summaries, weather_summary, now
        )
        
        action_items = self._generate_action_items(
            overall_condition, species_summaries, optimal_windows, weather_summary
        )
        
        calculation_time = (time.time() - start_time) * 1000
        
        return HuntPlanAnalysis(
            analysis_id=self._generate_analysis_id(),
            timestamp=datetime.now(timezone.utc),
            bounds=bounds,
            target_datetime=now,
            time_range_hours=time_range_hours,
            overall_condition=overall_condition,
            overall_score=overall_score,
            confidence=confidence,
            weather=weather_summary,
            hotspots=hotspot_analyses,
            hotspot_count=len(hotspot_analyses),
            species_summaries=species_summaries,
            optimal_windows=optimal_windows,
            executive_summary=executive_summary,
            key_insights=key_insights,
            action_items=action_items,
            calculation_time_ms=calculation_time,
            data_sources=data_sources
        )
    
    def _process_weather(self, weather_data: Optional[Dict]) -> WeatherSummary:
        """Traite les données météo."""
        if not weather_data or weather_data.get("status") != "active":
            return WeatherSummary(
                available=False,
                status="inactive",
                alerts=["Données météo non disponibles - analyse basée sur les données historiques"]
            )
        
        current = weather_data.get("current", {})
        behavior = weather_data.get("behavior_factors", {})
        
        # Calculer l'impact météo
        impact_score = 70.0  # Base
        
        # Température
        temp = current.get("temperature", 0)
        if -5 <= temp <= 15:
            impact_score += 15
        elif temp < -20 or temp > 25:
            impact_score -= 20
        
        # Vent
        wind = current.get("wind", {}).get("speed", 0)
        if wind < 15:
            impact_score += 10
        elif wind > 35:
            impact_score -= 15
        
        # Précipitations
        precip = current.get("precipitation", {}).get("rain_1h", 0)
        if precip > 5:
            impact_score -= 15
        
        # Pression
        pressure_trend = behavior.get("pressure_trend", "stable")
        if pressure_trend == "falling":
            impact_score += 10
        
        impact_score = max(0, min(100, impact_score))
        
        # Alertes
        alerts = []
        if wind > 30:
            alerts.append(f"Vent fort ({wind:.0f} km/h) - activité réduite probable")
        if precip > 3:
            alerts.append(f"Précipitations ({precip:.1f} mm/h) - mouvement limité")
        if pressure_trend == "falling":
            alerts.append("Pression en baisse - augmentation d'activité attendue")
        if temp > 20:
            alerts.append(f"Température élevée ({temp:.0f}°C) - activité diurne réduite")
        
        return WeatherSummary(
            available=True,
            status="active",
            current={
                "temperature": current.get("temperature"),
                "humidity": current.get("humidity"),
                "wind_speed": current.get("wind", {}).get("speed"),
                "pressure": current.get("pressure"),
                "condition": current.get("condition")
            },
            trend=pressure_trend,
            impact_score=impact_score,
            alerts=alerts
        )
    
    def _analyze_hotspots(
        self,
        hotspots_data: List[Dict],
        weather_data: Optional[Dict],
        scoring_service: Optional[Any],
        now: datetime
    ) -> List[HotspotAnalysis]:
        """Analyse les hotspots individuellement."""
        analyses = []
        
        for i, hs in enumerate(hotspots_data):
            # Extraire les coordonnées du centre
            coords = hs.get("geometry", {}).get("coordinates", [[]])[0]
            if coords:
                center_lat = sum(c[1] for c in coords) / len(coords)
                center_lng = sum(c[0] for c in coords) / len(coords)
            else:
                center_lat, center_lng = 0, 0
            
            # Score de base
            base_score = hs.get("score", 50)
            
            # Score dynamique (simplifié si pas de service)
            dynamic_score = base_score
            score_components = {}
            
            # Score final combiné
            final_score = base_score  # Simplifié
            
            # Calculer l'aire approximative
            area_m2 = hs.get("metadata", {}).get("area_m2", 7500)
            
            # Facteurs clés
            key_factors = []
            if hs.get("type") == "activity_peak":
                key_factors.append("Zone de pic d'activité identifiée")
            if hs.get("type") == "feeding_zone":
                key_factors.append("Zone d'alimentation active")
            if base_score >= 80:
                key_factors.append("Score élevé - haute probabilité de présence")
            
            analyses.append(HotspotAnalysis(
                hotspot_id=hs.get("id", f"HS-{i}"),
                type=hs.get("type", "unknown"),
                species=hs.get("species", []),
                base_score=base_score,
                dynamic_score=dynamic_score,
                final_score=final_score,
                rank=i + 1,
                location=(center_lat, center_lng),
                area_m2=area_m2,
                time_validity=hs.get("time_validity", {}),
                score_components=score_components,
                key_factors=key_factors
            ))
        
        # Trier par score final décroissant et réassigner les rangs
        analyses.sort(key=lambda x: x.final_score, reverse=True)
        for i, a in enumerate(analyses):
            a.rank = i + 1
        
        return analyses
    
    def _generate_species_summaries(
        self,
        species: List[str],
        hotspot_analyses: List[HotspotAnalysis],
        weather: WeatherSummary,
        now: datetime
    ) -> List[SpeciesSummary]:
        """Génère les synthèses par espèce."""
        summaries = []
        
        for sp in species:
            # Filtrer les hotspots pour cette espèce
            sp_hotspots = [h for h in hotspot_analyses if sp in h.species]
            
            if not sp_hotspots:
                # Créer une synthèse vide
                summaries.append(SpeciesSummary(
                    species=sp,
                    species_name=self.SPECIES_NAMES.get(sp, sp),
                    hotspot_count=0,
                    average_score=0,
                    best_score=0,
                    worst_score=0,
                    primary_behaviors=[],
                    activity_level="unknown",
                    feeding_probability=0,
                    movement_probability=0,
                    optimal_windows=[],
                    key_factors=["Aucun hotspot identifié pour cette espèce"],
                    recommendations=["Élargir la zone de recherche"]
                ))
                continue
            
            # Calculer les statistiques
            scores = [h.final_score for h in sp_hotspots]
            avg_score = sum(scores) / len(scores)
            best_score = max(scores)
            worst_score = min(scores)
            
            # Déterminer le niveau d'activité
            if avg_score >= 75:
                activity_level = "high"
            elif avg_score >= 55:
                activity_level = "moderate"
            else:
                activity_level = "low"
            
            # Probabilités comportementales
            feeding_prob = 0.6 if now.hour in [5, 6, 7, 17, 18, 19] else 0.3
            movement_prob = 0.5
            
            if weather.available and weather.trend == "falling":
                feeding_prob += 0.2
                movement_prob += 0.1
            
            # Comportements primaires
            behaviors = []
            types = [h.type for h in sp_hotspots]
            if "feeding_zone" in types:
                behaviors.append("Alimentation active")
            if "activity_peak" in types:
                behaviors.append("Activité élevée")
            if "rut_zone" in types:
                behaviors.append("Comportement de rut")
            
            # Fenêtres optimales
            windows = self._get_species_windows(sp, weather, now)
            
            # Facteurs clés
            key_factors = []
            key_factors.append(f"{len(sp_hotspots)} hotspots identifiés")
            if activity_level == "high":
                key_factors.append("Niveau d'activité élevé attendu")
            if weather.trend == "falling":
                key_factors.append("Pression en baisse favorable")
            
            # Recommandations
            recommendations = []
            if best_score >= 80:
                best_hs = max(sp_hotspots, key=lambda x: x.final_score)
                recommendations.append(f"Priorité au hotspot {best_hs.hotspot_id} (score: {best_score:.0f})")
            
            if windows:
                best_window = windows[0]
                recommendations.append(f"Période optimale: {best_window.time_range}")
            
            if activity_level == "low":
                recommendations.append("Considérer un changement de zone")
            
            summaries.append(SpeciesSummary(
                species=sp,
                species_name=self.SPECIES_NAMES.get(sp, sp),
                hotspot_count=len(sp_hotspots),
                average_score=avg_score,
                best_score=best_score,
                worst_score=worst_score,
                primary_behaviors=behaviors,
                activity_level=activity_level,
                feeding_probability=min(1.0, feeding_prob),
                movement_probability=min(1.0, movement_prob),
                optimal_windows=windows,
                key_factors=key_factors,
                recommendations=recommendations
            ))
        
        return summaries
    
    def _get_species_windows(
        self,
        species: str,
        weather: WeatherSummary,
        now: datetime
    ) -> List[TimeWindow]:
        """Génère les fenêtres optimales pour une espèce."""
        windows = []
        
        # Aube
        dawn_score = 85 if weather.impact_score > 60 else 70
        windows.append(TimeWindow(
            period="dawn",
            start_hour=5,
            end_hour=8,
            quality="excellent" if dawn_score >= 80 else "good",
            score=dawn_score,
            description="Période de l'aube - activité maximale",
            factors=["Pic d'activité naturel", "Alimentation matinale"]
        ))
        
        # Crépuscule
        dusk_score = 85 if weather.impact_score > 60 else 70
        windows.append(TimeWindow(
            period="dusk",
            start_hour=17,
            end_hour=20,
            quality="excellent" if dusk_score >= 80 else "good",
            score=dusk_score,
            description="Période du crépuscule - activité maximale",
            factors=["Pic d'activité naturel", "Alimentation vespérale"]
        ))
        
        # Mi-journée (si couvert)
        if weather.available:
            if weather.current and weather.current.get("condition") in ["clouds", "mist"]:
                windows.append(TimeWindow(
                    period="midday_overcast",
                    start_hour=11,
                    end_hour=14,
                    quality="moderate",
                    score=55,
                    description="Mi-journée nuageuse - activité possible",
                    factors=["Couverture nuageuse favorable"]
                ))
        
        return windows
    
    def _calculate_global_windows(
        self,
        weather: WeatherSummary,
        species: List[str],
        now: datetime
    ) -> List[TimeWindow]:
        """Calcule les fenêtres optimales globales."""
        windows = []
        
        # Score de base selon l'heure actuelle
        current_hour = now.hour
        
        # Aube (meilleure fenêtre)
        dawn_factors = ["Pic d'activité toutes espèces", "Température fraîche"]
        if weather.trend == "falling":
            dawn_factors.append("Pression en baisse favorable")
        
        windows.append(TimeWindow(
            period="dawn",
            start_hour=5,
            end_hour=8,
            quality="excellent",
            score=90 if weather.impact_score > 70 else 80,
            description="FENÊTRE PRINCIPALE - Aube",
            factors=dawn_factors
        ))
        
        # Crépuscule
        dusk_factors = ["Pic d'activité toutes espèces", "Retour à l'alimentation"]
        windows.append(TimeWindow(
            period="dusk",
            start_hour=17,
            end_hour=20,
            quality="excellent",
            score=90 if weather.impact_score > 70 else 80,
            description="FENÊTRE PRINCIPALE - Crépuscule",
            factors=dusk_factors
        ))
        
        # Fenêtre actuelle (si applicable)
        if 5 <= current_hour <= 8 or 17 <= current_hour <= 20:
            windows.insert(0, TimeWindow(
                period="current",
                start_hour=current_hour,
                end_hour=current_hour + 1,
                quality="excellent",
                score=95,
                description="MAINTENANT - Période optimale en cours",
                factors=["Fenêtre d'opportunité immédiate"]
            ))
        
        return windows
    
    def _calculate_overall_score(
        self,
        hotspot_analyses: List[HotspotAnalysis],
        weather: WeatherSummary,
        species_summaries: List[SpeciesSummary]
    ) -> float:
        """Calcule le score global de l'analyse."""
        scores = []
        
        # Score moyen des hotspots (40%)
        if hotspot_analyses:
            avg_hotspot = sum(h.final_score for h in hotspot_analyses) / len(hotspot_analyses)
            scores.append(avg_hotspot * 0.4)
        else:
            scores.append(30 * 0.4)  # Pénalité si pas de hotspots
        
        # Score météo (30%)
        if weather.available:
            scores.append(weather.impact_score * 0.3)
        else:
            scores.append(50 * 0.3)  # Neutre si pas de météo
        
        # Score espèces (30%)
        if species_summaries:
            valid_summaries = [s for s in species_summaries if s.hotspot_count > 0]
            if valid_summaries:
                avg_species = sum(s.average_score for s in valid_summaries) / len(valid_summaries)
                scores.append(avg_species * 0.3)
            else:
                scores.append(30 * 0.3)
        else:
            scores.append(50 * 0.3)
        
        return sum(scores)
    
    def _determine_condition(self, score: float) -> HuntingCondition:
        """Détermine la condition de chasse globale."""
        if score >= 80:
            return HuntingCondition.EXCELLENT
        elif score >= 65:
            return HuntingCondition.GOOD
        elif score >= 50:
            return HuntingCondition.MODERATE
        elif score >= 35:
            return HuntingCondition.POOR
        else:
            return HuntingCondition.UNFAVORABLE
    
    def _determine_confidence(
        self,
        weather: WeatherSummary,
        hotspot_analyses: List[HotspotAnalysis]
    ) -> AnalysisConfidence:
        """Détermine le niveau de confiance de l'analyse."""
        if weather.available and len(hotspot_analyses) >= 5:
            return AnalysisConfidence.HIGH
        elif weather.available or len(hotspot_analyses) >= 3:
            return AnalysisConfidence.MEDIUM
        else:
            return AnalysisConfidence.LOW
    
    def _generate_executive_summary(
        self,
        condition: HuntingCondition,
        score: float,
        species_summaries: List[SpeciesSummary],
        weather: WeatherSummary
    ) -> str:
        """Génère le résumé exécutif."""
        condition_text = {
            HuntingCondition.EXCELLENT: "EXCELLENTES",
            HuntingCondition.GOOD: "BONNES",
            HuntingCondition.MODERATE: "MODÉRÉES",
            HuntingCondition.POOR: "FAIBLES",
            HuntingCondition.UNFAVORABLE: "DÉFAVORABLES"
        }
        
        summary = f"Conditions de chasse {condition_text[condition]} (Score: {score:.0f}/100). "
        
        # Ajouter info espèces
        active_species = [s for s in species_summaries if s.hotspot_count > 0]
        if active_species:
            best = max(active_species, key=lambda x: x.average_score)
            summary += f"Meilleur potentiel: {best.species_name} ({best.hotspot_count} hotspots, score moyen {best.average_score:.0f}). "
        
        # Ajouter info météo
        if weather.available:
            if weather.impact_score >= 70:
                summary += "Météo favorable à l'activité. "
            elif weather.impact_score < 50:
                summary += "Météo limitant l'activité. "
            
            if weather.trend == "falling":
                summary += "Pression en baisse - activité accrue attendue."
        else:
            summary += "Données météo non disponibles."
        
        return summary
    
    def _generate_key_insights(
        self,
        hotspot_analyses: List[HotspotAnalysis],
        species_summaries: List[SpeciesSummary],
        weather: WeatherSummary,
        now: datetime
    ) -> List[str]:
        """Génère les insights clés."""
        insights = []
        
        # Insight hotspots
        if hotspot_analyses:
            top_3 = hotspot_analyses[:3]
            insights.append(f"{len(hotspot_analyses)} hotspots identifiés, top 3 avec scores de {', '.join([str(int(h.final_score)) for h in top_3])}")
        
        # Insight temporel
        current_hour = now.hour
        if 5 <= current_hour <= 8:
            insights.append("🟢 Période d'aube en cours - fenêtre d'opportunité active")
        elif 17 <= current_hour <= 20:
            insights.append("🟢 Période de crépuscule en cours - fenêtre d'opportunité active")
        elif 10 <= current_hour <= 15:
            insights.append("🟡 Mi-journée - activité réduite, planifier pour le crépuscule")
        
        # Insight météo
        if weather.available:
            if weather.trend == "falling":
                insights.append("📈 Pression barométrique en baisse - anticipez une hausse d'activité")
            if weather.alerts:
                insights.append(f"⚠️ Alerte météo: {weather.alerts[0]}")
        
        # Insight espèces
        for sp in species_summaries:
            if sp.activity_level == "high":
                insights.append(f"🎯 {sp.species_name}: niveau d'activité ÉLEVÉ prévu")
        
        return insights[:6]  # Max 6 insights
    
    def _generate_action_items(
        self,
        condition: HuntingCondition,
        species_summaries: List[SpeciesSummary],
        windows: List[TimeWindow],
        weather: WeatherSummary
    ) -> List[str]:
        """Génère les actions recommandées."""
        actions = []
        
        # Action principale selon condition
        if condition in [HuntingCondition.EXCELLENT, HuntingCondition.GOOD]:
            actions.append("✅ SORTIE RECOMMANDÉE - Conditions favorables")
        elif condition == HuntingCondition.MODERATE:
            actions.append("⚠️ Sortie possible - Cibler les fenêtres optimales")
        else:
            actions.append("❌ Reporter la sortie si possible")
        
        # Action fenêtre
        if windows:
            best_window = windows[0]
            actions.append(f"⏰ Prioriser la période {best_window.start_hour}h-{best_window.end_hour}h ({best_window.period})")
        
        # Action espèce
        for sp in species_summaries:
            if sp.hotspot_count > 0 and sp.recommendations:
                actions.append(f"🎯 {sp.species_name}: {sp.recommendations[0]}")
                break
        
        # Action météo
        if weather.trend == "falling":
            actions.append("📊 Surveiller la pression - pic d'activité imminent")
        
        return actions[:5]  # Max 5 actions


# =============================================================================
# SINGLETON
# =============================================================================

_hunt_plan_analyzer: Optional[HuntPlanAnalyzer] = None


def get_hunt_plan_analyzer() -> HuntPlanAnalyzer:
    """Retourne l'instance singleton de l'analyseur."""
    global _hunt_plan_analyzer
    if _hunt_plan_analyzer is None:
        _hunt_plan_analyzer = HuntPlanAnalyzer()
    return _hunt_plan_analyzer


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'HuntPlanAnalyzer',
    'get_hunt_plan_analyzer',
    'HuntPlanAnalysis',
    'HotspotAnalysis',
    'SpeciesSummary',
    'TimeWindow',
    'WeatherSummary',
    'HuntingCondition',
    'AnalysisConfidence'
]
