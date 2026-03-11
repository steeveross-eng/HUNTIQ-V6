"""
BIONIC ENGINE - Dynamic Scoring Service
PHASE P1-SCORE — Système de Scoring Dynamique

Service de calcul de scores comportementaux dynamiques pour les hotspots BIONIC.
Intègre les données météorologiques et les facteurs environnementaux.

COMPOSANTS DU SCORE:
- Score Météo (weather_score): Basé sur les conditions actuelles
- Score Activité (activity_score): Probabilité d'activité du gibier
- Score Alimentation (feeding_score): Conditions d'alimentation
- Score Mouvement (movement_score): Probabilité de déplacement
- Score Temporel (temporal_score): Heure de la journée, saison
- Score Pression (pressure_score): Tendance barométrique
- Score Lunaire (lunar_score): Phase de la lune
- Score Final (composite_score): Moyenne pondérée

Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION - SEUILS ET PONDÉRATIONS
# =============================================================================

# Pondérations des composants du score (total = 1.0)
SCORE_WEIGHTS = {
    "weather": 0.20,      # Conditions météo actuelles
    "activity": 0.20,     # Probabilité d'activité
    "feeding": 0.15,      # Conditions d'alimentation
    "movement": 0.15,     # Probabilité de mouvement
    "temporal": 0.15,     # Facteur temporel
    "pressure": 0.10,     # Tendance barométrique
    "lunar": 0.05         # Phase lunaire
}

# Seuils météo par espèce
SPECIES_THRESHOLDS = {
    "moose": {
        "temp_optimal": (-5, 15),      # °C
        "temp_stress_cold": -25,       # °C
        "temp_stress_heat": 25,        # °C
        "wind_optimal_max": 20,        # km/h
        "wind_stress": 40,             # km/h
        "precip_tolerance": 5,         # mm/h
        "activity_peak_hours": [5, 6, 7, 17, 18, 19, 20],
        "feeding_hours": [4, 5, 6, 7, 16, 17, 18, 19, 20],
        "pressure_sensitivity": 0.8,   # Sensibilité à la pression
    },
    "deer": {
        "temp_optimal": (0, 20),
        "temp_stress_cold": -20,
        "temp_stress_heat": 30,
        "wind_optimal_max": 15,
        "wind_stress": 35,
        "precip_tolerance": 3,
        "activity_peak_hours": [5, 6, 7, 18, 19, 20],
        "feeding_hours": [5, 6, 7, 17, 18, 19, 20],
        "pressure_sensitivity": 0.7,
    },
    "bear": {
        "temp_optimal": (5, 25),
        "temp_stress_cold": -10,
        "temp_stress_heat": 35,
        "wind_optimal_max": 25,
        "wind_stress": 50,
        "precip_tolerance": 10,
        "activity_peak_hours": [6, 7, 8, 17, 18, 19],
        "feeding_hours": [6, 7, 8, 9, 16, 17, 18, 19],
        "pressure_sensitivity": 0.5,
    },
    "wild_turkey": {
        "temp_optimal": (5, 25),
        "temp_stress_cold": -15,
        "temp_stress_heat": 35,
        "wind_optimal_max": 20,
        "wind_stress": 40,
        "precip_tolerance": 2,
        "activity_peak_hours": [6, 7, 8, 16, 17, 18],
        "feeding_hours": [6, 7, 8, 9, 15, 16, 17, 18],
        "pressure_sensitivity": 0.6,
    },
    "elk": {
        "temp_optimal": (-10, 20),
        "temp_stress_cold": -30,
        "temp_stress_heat": 28,
        "wind_optimal_max": 25,
        "wind_stress": 45,
        "precip_tolerance": 8,
        "activity_peak_hours": [5, 6, 7, 17, 18, 19, 20],
        "feeding_hours": [5, 6, 7, 8, 16, 17, 18, 19],
        "pressure_sensitivity": 0.7,
    }
}

# Seuils pression atmosphérique
PRESSURE_OPTIMAL_LOW = 1010  # hPa
PRESSURE_OPTIMAL_HIGH = 1025  # hPa
PRESSURE_RISING_THRESHOLD = 3  # hPa/3h
PRESSURE_FALLING_THRESHOLD = -3  # hPa/3h

# Phases lunaires et leur impact
LUNAR_PHASES = {
    (0.0, 0.1): {"name": "new_moon", "activity_mod": -0.1, "feeding_mod": 0.2},
    (0.1, 0.25): {"name": "waxing_crescent", "activity_mod": 0.0, "feeding_mod": 0.1},
    (0.25, 0.4): {"name": "first_quarter", "activity_mod": 0.1, "feeding_mod": 0.0},
    (0.4, 0.6): {"name": "full_moon", "activity_mod": 0.2, "feeding_mod": -0.1},
    (0.6, 0.75): {"name": "waning_gibbous", "activity_mod": 0.1, "feeding_mod": 0.0},
    (0.75, 0.9): {"name": "last_quarter", "activity_mod": 0.0, "feeding_mod": 0.1},
    (0.9, 1.0): {"name": "waning_crescent", "activity_mod": -0.1, "feeding_mod": 0.15},
}


# =============================================================================
# DATA CONTRACTS
# =============================================================================

class ScoreLevel(str, Enum):
    """Niveaux de score."""
    EXCELLENT = "excellent"    # 85-100
    GOOD = "good"              # 70-84
    MODERATE = "moderate"      # 50-69
    POOR = "poor"              # 30-49
    VERY_POOR = "very_poor"    # 0-29


@dataclass
class ScoreComponent:
    """Composant individuel du score."""
    name: str
    value: float  # 0-100
    weight: float
    weighted_value: float
    factors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": round(self.value, 1),
            "weight": self.weight,
            "weighted_value": round(self.weighted_value, 2),
            "factors": self.factors
        }


@dataclass
class WeatherInputs:
    """Données météo pour le calcul du score."""
    temperature: float = 0.0
    feels_like: float = 0.0
    humidity: int = 50
    pressure: float = 1013.0
    wind_speed: float = 0.0
    wind_gust: Optional[float] = None
    precipitation: float = 0.0
    cloud_cover: int = 0
    visibility: int = 10000
    pressure_trend: str = "stable"  # rising, falling, stable
    moon_phase: float = 0.5
    sunrise_hour: int = 6
    sunset_hour: int = 18
    
    @classmethod
    def from_weather_response(cls, weather_data: Dict[str, Any]) -> "WeatherInputs":
        """Crée les inputs depuis une réponse du service météo."""
        current = weather_data.get("current", {})
        behavior = weather_data.get("behavior_factors", {})
        
        sunrise = current.get("sun", {}).get("sunrise")
        sunset = current.get("sun", {}).get("sunset")
        
        return cls(
            temperature=current.get("temperature", 0),
            feels_like=current.get("feels_like", 0),
            humidity=current.get("humidity", 50),
            pressure=current.get("pressure", 1013),
            wind_speed=current.get("wind", {}).get("speed", 0),
            wind_gust=current.get("wind", {}).get("gust"),
            precipitation=current.get("precipitation", {}).get("rain_1h", 0) + 
                         current.get("precipitation", {}).get("snow_1h", 0),
            cloud_cover=current.get("cloud_cover", 0),
            visibility=current.get("visibility", 10000),
            pressure_trend=behavior.get("pressure_trend", "stable"),
            moon_phase=0.5,  # Par défaut si non disponible
            sunrise_hour=int(sunrise[11:13]) if sunrise else 6,
            sunset_hour=int(sunset[11:13]) if sunset else 18
        )


@dataclass
class DynamicScore:
    """Score dynamique complet pour un hotspot."""
    composite_score: float  # 0-100
    level: ScoreLevel
    components: List[ScoreComponent]
    species: str
    location: Tuple[float, float]  # (lat, lng)
    timestamp: datetime
    weather_available: bool
    recommendations: List[str]
    optimal_windows: List[Dict[str, Any]]
    confidence: float  # 0-1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "composite_score": round(self.composite_score, 1),
            "level": self.level.value,
            "components": [c.to_dict() for c in self.components],
            "species": self.species,
            "location": {
                "latitude": self.location[0],
                "longitude": self.location[1]
            },
            "timestamp": self.timestamp.isoformat(),
            "weather_available": self.weather_available,
            "recommendations": self.recommendations,
            "optimal_windows": self.optimal_windows,
            "confidence": round(self.confidence, 2)
        }


@dataclass
class HotspotScore:
    """Score pour un hotspot spécifique."""
    hotspot_id: str
    base_score: float  # Score de base du hotspot
    dynamic_score: DynamicScore
    final_score: float  # Score final combiné
    score_delta: float  # Différence base vs dynamic
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "hotspot_id": self.hotspot_id,
            "base_score": round(self.base_score, 1),
            "dynamic_score": self.dynamic_score.to_dict(),
            "final_score": round(self.final_score, 1),
            "score_delta": round(self.score_delta, 1)
        }


# =============================================================================
# SCORING SERVICE
# =============================================================================

class DynamicScoringService:
    """
    Service de calcul de scores dynamiques pour BIONIC V5.
    
    Calcule les scores comportementaux en intégrant:
    - Conditions météorologiques
    - Facteurs temporels
    - Caractéristiques par espèce
    - Tendances barométriques
    - Phase lunaire
    """
    
    def __init__(self):
        self._weights = SCORE_WEIGHTS.copy()
    
    def calculate_dynamic_score(
        self,
        latitude: float,
        longitude: float,
        species: str,
        weather_inputs: Optional[WeatherInputs] = None,
        target_datetime: Optional[datetime] = None
    ) -> DynamicScore:
        """
        Calcule le score dynamique pour une position et espèce.
        
        Args:
            latitude: Latitude
            longitude: Longitude
            species: Espèce cible
            weather_inputs: Données météo (si disponibles)
            target_datetime: Date/heure cible
            
        Returns:
            DynamicScore avec tous les composants
        """
        now = target_datetime or datetime.now(timezone.utc)
        
        # Récupérer les seuils de l'espèce
        thresholds = SPECIES_THRESHOLDS.get(species, SPECIES_THRESHOLDS["moose"])
        
        # Initialiser les composants
        components = []
        weather_available = weather_inputs is not None
        
        if weather_inputs:
            # Score Météo
            weather_score = self._calculate_weather_score(weather_inputs, thresholds)
            components.append(weather_score)
            
            # Score Activité
            activity_score = self._calculate_activity_score(weather_inputs, thresholds, now)
            components.append(activity_score)
            
            # Score Alimentation
            feeding_score = self._calculate_feeding_score(weather_inputs, thresholds, now)
            components.append(feeding_score)
            
            # Score Mouvement
            movement_score = self._calculate_movement_score(weather_inputs, thresholds)
            components.append(movement_score)
            
            # Score Pression
            pressure_score = self._calculate_pressure_score(weather_inputs, thresholds)
            components.append(pressure_score)
            
            # Score Lunaire
            lunar_score = self._calculate_lunar_score(weather_inputs)
            components.append(lunar_score)
        else:
            # Scores par défaut sans météo
            for name, weight in self._weights.items():
                if name not in ["temporal"]:
                    components.append(ScoreComponent(
                        name=name,
                        value=50.0,
                        weight=weight,
                        weighted_value=50.0 * weight,
                        factors=["Données météo non disponibles"]
                    ))
        
        # Score Temporel (toujours calculé)
        temporal_score = self._calculate_temporal_score(thresholds, now, weather_inputs)
        components.append(temporal_score)
        
        # Calcul du score composite
        total_weighted = sum(c.weighted_value for c in components)
        composite_score = min(100, max(0, total_weighted / sum(self._weights.values())))
        
        # Déterminer le niveau
        level = self._get_score_level(composite_score)
        
        # Générer les recommandations
        recommendations = self._generate_recommendations(
            components, weather_inputs, thresholds, now
        )
        
        # Calculer les fenêtres optimales
        optimal_windows = self._calculate_optimal_windows(
            weather_inputs, thresholds, now
        )
        
        # Calcul de la confiance
        confidence = 0.9 if weather_available else 0.5
        
        return DynamicScore(
            composite_score=composite_score,
            level=level,
            components=components,
            species=species,
            location=(latitude, longitude),
            timestamp=now,
            weather_available=weather_available,
            recommendations=recommendations,
            optimal_windows=optimal_windows,
            confidence=confidence
        )
    
    def calculate_hotspot_score(
        self,
        hotspot_id: str,
        base_score: float,
        latitude: float,
        longitude: float,
        species: str,
        weather_inputs: Optional[WeatherInputs] = None,
        target_datetime: Optional[datetime] = None
    ) -> HotspotScore:
        """
        Calcule le score final d'un hotspot en combinant score de base et dynamique.
        
        Args:
            hotspot_id: ID du hotspot
            base_score: Score de base (0-100)
            latitude: Latitude du centre du hotspot
            longitude: Longitude du centre du hotspot
            species: Espèce cible
            weather_inputs: Données météo
            target_datetime: Date/heure cible
            
        Returns:
            HotspotScore avec score final
        """
        dynamic = self.calculate_dynamic_score(
            latitude, longitude, species, weather_inputs, target_datetime
        )
        
        # Combinaison: 60% base + 40% dynamique
        final_score = (base_score * 0.6) + (dynamic.composite_score * 0.4)
        
        return HotspotScore(
            hotspot_id=hotspot_id,
            base_score=base_score,
            dynamic_score=dynamic,
            final_score=final_score,
            score_delta=dynamic.composite_score - base_score
        )
    
    def _calculate_weather_score(
        self,
        inputs: WeatherInputs,
        thresholds: Dict[str, Any]
    ) -> ScoreComponent:
        """Calcule le score météo."""
        score = 70.0  # Base
        factors = []
        
        # Température
        temp_opt = thresholds["temp_optimal"]
        if temp_opt[0] <= inputs.temperature <= temp_opt[1]:
            score += 15
            factors.append(f"Température optimale ({inputs.temperature}°C)")
        elif inputs.temperature < thresholds["temp_stress_cold"]:
            score -= 30
            factors.append(f"Froid extrême ({inputs.temperature}°C)")
        elif inputs.temperature > thresholds["temp_stress_heat"]:
            score -= 25
            factors.append(f"Chaleur excessive ({inputs.temperature}°C)")
        else:
            # Pénalité progressive
            if inputs.temperature < temp_opt[0]:
                penalty = min(20, (temp_opt[0] - inputs.temperature) * 2)
            else:
                penalty = min(20, (inputs.temperature - temp_opt[1]) * 2)
            score -= penalty
            factors.append(f"Température non optimale ({inputs.temperature}°C)")
        
        # Vent
        if inputs.wind_speed <= thresholds["wind_optimal_max"]:
            score += 10
            factors.append(f"Vent favorable ({inputs.wind_speed:.0f} km/h)")
        elif inputs.wind_speed >= thresholds["wind_stress"]:
            score -= 25
            factors.append(f"Vent fort ({inputs.wind_speed:.0f} km/h)")
        else:
            penalty = (inputs.wind_speed - thresholds["wind_optimal_max"]) * 0.5
            score -= penalty
        
        # Précipitations
        if inputs.precipitation > thresholds["precip_tolerance"]:
            score -= 20
            factors.append(f"Précipitations importantes ({inputs.precipitation:.1f} mm)")
        elif inputs.precipitation > 0:
            score -= 5
            factors.append("Légères précipitations")
        
        # Visibilité
        if inputs.visibility < 1000:
            score -= 15
            factors.append("Visibilité réduite")
        
        score = min(100, max(0, score))
        
        return ScoreComponent(
            name="weather",
            value=score,
            weight=self._weights["weather"],
            weighted_value=score * self._weights["weather"],
            factors=factors
        )
    
    def _calculate_activity_score(
        self,
        inputs: WeatherInputs,
        thresholds: Dict[str, Any],
        now: datetime
    ) -> ScoreComponent:
        """Calcule le score d'activité."""
        score = 60.0
        factors = []
        current_hour = now.hour
        
        # Heures de pic d'activité
        if current_hour in thresholds["activity_peak_hours"]:
            score += 25
            factors.append(f"Heure de pic d'activité ({current_hour}h)")
        elif current_hour in range(8, 16):
            score -= 10
            factors.append("Période de repos diurne")
        elif current_hour in range(22, 5):
            score -= 15
            factors.append("Période nocturne")
        
        # Impact météo sur l'activité
        if inputs.pressure_trend == "falling":
            score += 15
            factors.append("Pression en baisse → activité accrue")
        elif inputs.pressure_trend == "rising":
            score += 5
            factors.append("Pression en hausse → stabilisation")
        
        # Conditions calmes = plus d'activité
        if inputs.wind_speed < 10 and inputs.precipitation == 0:
            score += 10
            factors.append("Conditions calmes favorables")
        
        score = min(100, max(0, score))
        
        return ScoreComponent(
            name="activity",
            value=score,
            weight=self._weights["activity"],
            weighted_value=score * self._weights["activity"],
            factors=factors
        )
    
    def _calculate_feeding_score(
        self,
        inputs: WeatherInputs,
        thresholds: Dict[str, Any],
        now: datetime
    ) -> ScoreComponent:
        """Calcule le score d'alimentation."""
        score = 55.0
        factors = []
        current_hour = now.hour
        
        # Heures d'alimentation
        if current_hour in thresholds["feeding_hours"]:
            score += 20
            factors.append(f"Période d'alimentation ({current_hour}h)")
        
        # Pression en baisse = alimentation avant tempête
        if inputs.pressure_trend == "falling":
            score += 20
            factors.append("Alimentation pré-tempête")
        
        # Humidité modérée favorable
        if 40 <= inputs.humidity <= 70:
            score += 10
            factors.append("Humidité favorable")
        elif inputs.humidity > 85:
            score -= 5
            factors.append("Humidité élevée")
        
        # Température confortable
        temp_opt = thresholds["temp_optimal"]
        if temp_opt[0] <= inputs.temperature <= temp_opt[1]:
            score += 10
            factors.append("Température de confort")
        
        score = min(100, max(0, score))
        
        return ScoreComponent(
            name="feeding",
            value=score,
            weight=self._weights["feeding"],
            weighted_value=score * self._weights["feeding"],
            factors=factors
        )
    
    def _calculate_movement_score(
        self,
        inputs: WeatherInputs,
        thresholds: Dict[str, Any]
    ) -> ScoreComponent:
        """Calcule le score de mouvement."""
        score = 60.0
        factors = []
        
        # Vent faible = plus de mouvement
        if inputs.wind_speed < 10:
            score += 20
            factors.append("Vent faible → mouvement facilité")
        elif inputs.wind_speed > thresholds["wind_stress"]:
            score -= 25
            factors.append("Vent fort → mouvement réduit")
        
        # Précipitations réduisent le mouvement
        if inputs.precipitation > 2:
            score -= 15
            factors.append("Précipitations → mouvement limité")
        
        # Visibilité
        if inputs.visibility > 5000:
            score += 10
            factors.append("Bonne visibilité")
        elif inputs.visibility < 1000:
            score -= 15
            factors.append("Mauvaise visibilité")
        
        # Pression en baisse = mouvement vers les abris
        if inputs.pressure_trend == "falling":
            score += 10
            factors.append("Mouvement vers zones d'abri")
        
        score = min(100, max(0, score))
        
        return ScoreComponent(
            name="movement",
            value=score,
            weight=self._weights["movement"],
            weighted_value=score * self._weights["movement"],
            factors=factors
        )
    
    def _calculate_temporal_score(
        self,
        thresholds: Dict[str, Any],
        now: datetime,
        inputs: Optional[WeatherInputs]
    ) -> ScoreComponent:
        """Calcule le score temporel."""
        score = 50.0
        factors = []
        current_hour = now.hour
        
        # Crépuscules
        sunrise = inputs.sunrise_hour if inputs else 6
        sunset = inputs.sunset_hour if inputs else 18
        
        # Aube (sunrise - 1 à sunrise + 1)
        if sunrise - 1 <= current_hour <= sunrise + 1:
            score += 30
            factors.append("Période de l'aube (optimale)")
        # Crépuscule (sunset - 1 à sunset + 1)
        elif sunset - 1 <= current_hour <= sunset + 1:
            score += 30
            factors.append("Période du crépuscule (optimale)")
        # Matin
        elif sunrise + 1 < current_hour < 10:
            score += 15
            factors.append("Matinée (favorable)")
        # Fin d'après-midi
        elif 15 < current_hour < sunset - 1:
            score += 15
            factors.append("Fin d'après-midi (favorable)")
        # Milieu de journée
        elif 10 <= current_hour <= 15:
            score -= 10
            factors.append("Milieu de journée (repos)")
        # Nuit
        else:
            score -= 15
            factors.append("Période nocturne")
        
        # Saison (approximation)
        month = now.month
        if month in [9, 10, 11]:  # Automne - rut
            score += 15
            factors.append("Saison du rut (activité accrue)")
        elif month in [5, 6]:  # Printemps
            score += 10
            factors.append("Printemps (reprise activité)")
        
        score = min(100, max(0, score))
        
        return ScoreComponent(
            name="temporal",
            value=score,
            weight=self._weights["temporal"],
            weighted_value=score * self._weights["temporal"],
            factors=factors
        )
    
    def _calculate_pressure_score(
        self,
        inputs: WeatherInputs,
        thresholds: Dict[str, Any]
    ) -> ScoreComponent:
        """Calcule le score basé sur la pression atmosphérique."""
        score = 60.0
        factors = []
        sensitivity = thresholds["pressure_sensitivity"]
        
        # Pression actuelle
        if PRESSURE_OPTIMAL_LOW <= inputs.pressure <= PRESSURE_OPTIMAL_HIGH:
            score += 20
            factors.append(f"Pression optimale ({inputs.pressure:.0f} hPa)")
        elif inputs.pressure < 1000:
            score -= 15 * sensitivity
            factors.append(f"Basse pression ({inputs.pressure:.0f} hPa)")
        elif inputs.pressure > 1030:
            score += 5
            factors.append(f"Haute pression ({inputs.pressure:.0f} hPa)")
        
        # Tendance
        if inputs.pressure_trend == "falling":
            score += 25 * sensitivity
            factors.append("Pression en baisse → activité accrue")
        elif inputs.pressure_trend == "rising":
            score += 10 * sensitivity
            factors.append("Pression en hausse → conditions stables")
        else:
            factors.append("Pression stable")
        
        score = min(100, max(0, score))
        
        return ScoreComponent(
            name="pressure",
            value=score,
            weight=self._weights["pressure"],
            weighted_value=score * self._weights["pressure"],
            factors=factors
        )
    
    def _calculate_lunar_score(
        self,
        inputs: WeatherInputs
    ) -> ScoreComponent:
        """Calcule le score basé sur la phase lunaire."""
        score = 60.0
        factors = []
        phase = inputs.moon_phase
        
        # Trouver la phase
        phase_info = None
        for (low, high), info in LUNAR_PHASES.items():
            if low <= phase < high:
                phase_info = info
                break
        
        if phase_info is None:
            phase_info = {"name": "unknown", "activity_mod": 0, "feeding_mod": 0}
        
        # Appliquer les modificateurs
        activity_mod = phase_info["activity_mod"] * 100
        score += activity_mod
        
        phase_names = {
            "new_moon": "Nouvelle lune",
            "waxing_crescent": "Premier croissant",
            "first_quarter": "Premier quartier",
            "full_moon": "Pleine lune",
            "waning_gibbous": "Lune gibbeuse",
            "last_quarter": "Dernier quartier",
            "waning_crescent": "Dernier croissant"
        }
        
        factors.append(f"Phase: {phase_names.get(phase_info['name'], 'Inconnue')}")
        
        if phase_info["name"] == "full_moon":
            factors.append("Pleine lune → activité nocturne accrue")
        elif phase_info["name"] == "new_moon":
            factors.append("Nouvelle lune → activité crépusculaire")
        
        score = min(100, max(0, score))
        
        return ScoreComponent(
            name="lunar",
            value=score,
            weight=self._weights["lunar"],
            weighted_value=score * self._weights["lunar"],
            factors=factors
        )
    
    def _get_score_level(self, score: float) -> ScoreLevel:
        """Détermine le niveau du score."""
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
    
    def _generate_recommendations(
        self,
        components: List[ScoreComponent],
        inputs: Optional[WeatherInputs],
        thresholds: Dict[str, Any],
        now: datetime
    ) -> List[str]:
        """Génère des recommandations basées sur les scores."""
        recommendations = []
        
        # Analyser les composants
        scores = {c.name: c.value for c in components}
        
        # Recommandations basées sur le score météo
        if scores.get("weather", 0) < 50:
            recommendations.append("Conditions météo défavorables - privilégier les zones d'abri")
        elif scores.get("weather", 0) > 80:
            recommendations.append("Excellentes conditions météo - opportunité optimale")
        
        # Recommandations temporelles
        if scores.get("temporal", 0) > 70:
            recommendations.append("Période d'activité maximale - moment idéal")
        elif scores.get("temporal", 0) < 40:
            recommendations.append("Période de repos - activité réduite probable")
        
        # Recommandations pression
        if inputs and inputs.pressure_trend == "falling":
            recommendations.append("Pression en baisse - anticipez une augmentation d'activité")
        
        # Recommandations d'alimentation
        if scores.get("feeding", 0) > 75:
            recommendations.append("Conditions favorables à l'alimentation - zones de nourrissage actives")
        
        # Recommandations de mouvement
        if scores.get("movement", 0) > 75:
            recommendations.append("Fort potentiel de mouvement - surveillez les corridors")
        elif scores.get("movement", 0) < 40:
            recommendations.append("Mouvement limité - gibier probablement stationnaire")
        
        return recommendations[:5]  # Max 5 recommandations
    
    def _calculate_optimal_windows(
        self,
        inputs: Optional[WeatherInputs],
        thresholds: Dict[str, Any],
        now: datetime
    ) -> List[Dict[str, Any]]:
        """Calcule les fenêtres optimales d'observation."""
        windows = []
        
        # Fenêtre du matin
        sunrise = inputs.sunrise_hour if inputs else 6
        windows.append({
            "period": "dawn",
            "start_hour": sunrise - 1,
            "end_hour": sunrise + 2,
            "quality": "excellent" if now.hour in range(sunrise - 1, sunrise + 2) else "optimal",
            "description": "Période de l'aube - activité maximale"
        })
        
        # Fenêtre du soir
        sunset = inputs.sunset_hour if inputs else 18
        windows.append({
            "period": "dusk",
            "start_hour": sunset - 2,
            "end_hour": sunset + 1,
            "quality": "excellent" if now.hour in range(sunset - 2, sunset + 1) else "optimal",
            "description": "Période du crépuscule - activité maximale"
        })
        
        # Fenêtre de mi-journée (si conditions favorables)
        if inputs and inputs.cloud_cover > 70:
            windows.append({
                "period": "midday_overcast",
                "start_hour": 11,
                "end_hour": 14,
                "quality": "moderate",
                "description": "Couverture nuageuse - activité possible"
            })
        
        return windows


# =============================================================================
# SINGLETON
# =============================================================================

_scoring_service: Optional[DynamicScoringService] = None


def get_scoring_service() -> DynamicScoringService:
    """Retourne l'instance singleton du service de scoring."""
    global _scoring_service
    if _scoring_service is None:
        _scoring_service = DynamicScoringService()
    return _scoring_service


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'DynamicScoringService',
    'get_scoring_service',
    'DynamicScore',
    'HotspotScore',
    'ScoreComponent',
    'WeatherInputs',
    'ScoreLevel',
    'SCORE_WEIGHTS',
    'SPECIES_THRESHOLDS'
]
