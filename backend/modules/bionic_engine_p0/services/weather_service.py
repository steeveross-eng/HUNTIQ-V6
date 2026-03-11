"""
BIONIC ENGINE - OpenWeatherMap Integration Service
PHASE P1-ENV — Module Météorologique

Service d'intégration OpenWeatherMap pour BIONIC V5.
Fournit les données météorologiques nécessaires au scoring dynamique.

FONCTIONNALITÉS:
- Météo actuelle (température, humidité, vent, précipitations, pression)
- Prévisions 24h, 72h, 7 jours
- Mode "inactive" si clé API absente
- Cache local pour optimiser les appels API
- Facteurs comportementaux gibier intégrés

Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
"""

import os
import logging
import httpx
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION
# =============================================================================

OWM_API_KEY = os.environ.get("OWM_API_KEY", "")
OWM_BASE_URL = "https://api.openweathermap.org/data/2.5"
OWM_ONECALL_URL = "https://api.openweathermap.org/data/3.0/onecall"

# Cache TTL
CACHE_TTL_CURRENT = 600  # 10 minutes pour météo actuelle
CACHE_TTL_FORECAST = 1800  # 30 minutes pour prévisions

# Seuils comportementaux gibier
WIND_THRESHOLD_LOW = 10  # km/h - activité normale
WIND_THRESHOLD_HIGH = 30  # km/h - réduction activité
PRESSURE_OPTIMAL_LOW = 1010  # hPa
PRESSURE_OPTIMAL_HIGH = 1025  # hPa
TEMP_COMFORT_MOOSE = (-10, 15)  # °C
TEMP_COMFORT_DEER = (-5, 20)  # °C


# =============================================================================
# DATA CONTRACTS
# =============================================================================

class WeatherCondition(str, Enum):
    """Conditions météorologiques principales."""
    CLEAR = "clear"
    CLOUDS = "clouds"
    RAIN = "rain"
    DRIZZLE = "drizzle"
    SNOW = "snow"
    THUNDERSTORM = "thunderstorm"
    MIST = "mist"
    FOG = "fog"
    UNKNOWN = "unknown"


class ServiceStatus(str, Enum):
    """Statut du service météo."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"


@dataclass
class CurrentWeather:
    """Données météo actuelles."""
    timestamp: datetime
    temperature: float  # °C
    feels_like: float  # °C
    humidity: int  # %
    pressure: float  # hPa
    wind_speed: float  # km/h
    wind_direction: int  # degrés
    wind_gust: Optional[float] = None  # km/h
    precipitation_1h: float = 0.0  # mm
    snow_1h: float = 0.0  # mm
    cloud_cover: int = 0  # %
    visibility: int = 10000  # m
    condition: WeatherCondition = WeatherCondition.UNKNOWN
    condition_description: str = ""
    sunrise: Optional[datetime] = None
    sunset: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "temperature": round(self.temperature, 1),
            "feels_like": round(self.feels_like, 1),
            "humidity": self.humidity,
            "pressure": round(self.pressure, 1),
            "wind": {
                "speed": round(self.wind_speed, 1),
                "direction": self.wind_direction,
                "gust": round(self.wind_gust, 1) if self.wind_gust else None
            },
            "precipitation": {
                "rain_1h": round(self.precipitation_1h, 1),
                "snow_1h": round(self.snow_1h, 1)
            },
            "cloud_cover": self.cloud_cover,
            "visibility": self.visibility,
            "condition": self.condition.value,
            "condition_description": self.condition_description,
            "sun": {
                "sunrise": self.sunrise.isoformat() if self.sunrise else None,
                "sunset": self.sunset.isoformat() if self.sunset else None
            }
        }


@dataclass
class HourlyForecast:
    """Prévision horaire."""
    timestamp: datetime
    temperature: float
    feels_like: float
    humidity: int
    pressure: float
    wind_speed: float
    wind_direction: int
    precipitation_prob: float  # 0-1
    precipitation_mm: float
    condition: WeatherCondition
    condition_description: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "temperature": round(self.temperature, 1),
            "feels_like": round(self.feels_like, 1),
            "humidity": self.humidity,
            "pressure": round(self.pressure, 1),
            "wind_speed": round(self.wind_speed, 1),
            "wind_direction": self.wind_direction,
            "precipitation_prob": round(self.precipitation_prob, 2),
            "precipitation_mm": round(self.precipitation_mm, 1),
            "condition": self.condition.value,
            "condition_description": self.condition_description
        }


@dataclass
class DailyForecast:
    """Prévision journalière."""
    date: datetime
    temp_min: float
    temp_max: float
    temp_day: float
    temp_night: float
    humidity: int
    pressure: float
    wind_speed: float
    wind_direction: int
    precipitation_prob: float
    precipitation_mm: float
    condition: WeatherCondition
    condition_description: str
    sunrise: datetime
    sunset: datetime
    moon_phase: float  # 0-1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "date": self.date.strftime("%Y-%m-%d"),
            "temperature": {
                "min": round(self.temp_min, 1),
                "max": round(self.temp_max, 1),
                "day": round(self.temp_day, 1),
                "night": round(self.temp_night, 1)
            },
            "humidity": self.humidity,
            "pressure": round(self.pressure, 1),
            "wind_speed": round(self.wind_speed, 1),
            "wind_direction": self.wind_direction,
            "precipitation_prob": round(self.precipitation_prob, 2),
            "precipitation_mm": round(self.precipitation_mm, 1),
            "condition": self.condition.value,
            "condition_description": self.condition_description,
            "sun": {
                "sunrise": self.sunrise.isoformat(),
                "sunset": self.sunset.isoformat()
            },
            "moon_phase": round(self.moon_phase, 2)
        }


@dataclass
class WeatherBehaviorFactors:
    """Facteurs comportementaux dérivés de la météo."""
    activity_modifier: float  # -1 à +1
    feeding_modifier: float  # -1 à +1
    movement_modifier: float  # -1 à +1
    pressure_trend: str  # "rising", "falling", "stable"
    optimal_hours: List[int]  # Heures optimales pour observation
    risk_factors: List[str]  # Facteurs de risque
    recommendations: List[str]  # Recommandations
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "activity_modifier": round(self.activity_modifier, 2),
            "feeding_modifier": round(self.feeding_modifier, 2),
            "movement_modifier": round(self.movement_modifier, 2),
            "pressure_trend": self.pressure_trend,
            "optimal_hours": self.optimal_hours,
            "risk_factors": self.risk_factors,
            "recommendations": self.recommendations
        }


@dataclass
class WeatherResponse:
    """Réponse complète du service météo."""
    status: ServiceStatus
    current: Optional[CurrentWeather] = None
    hourly_24h: List[HourlyForecast] = field(default_factory=list)
    hourly_72h: List[HourlyForecast] = field(default_factory=list)
    daily_7d: List[DailyForecast] = field(default_factory=list)
    behavior_factors: Optional[WeatherBehaviorFactors] = None
    cached: bool = False
    cache_expires: Optional[datetime] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "current": self.current.to_dict() if self.current else None,
            "forecast": {
                "hourly_24h": [h.to_dict() for h in self.hourly_24h],
                "hourly_72h": [h.to_dict() for h in self.hourly_72h],
                "daily_7d": [d.to_dict() for d in self.daily_7d]
            },
            "behavior_factors": self.behavior_factors.to_dict() if self.behavior_factors else None,
            "metadata": {
                "cached": self.cached,
                "cache_expires": self.cache_expires.isoformat() if self.cache_expires else None,
                "error": self.error_message
            }
        }


# =============================================================================
# WEATHER SERVICE
# =============================================================================

class WeatherService:
    """
    Service météorologique OpenWeatherMap pour BIONIC V5.
    
    Fournit les données météo nécessaires au scoring dynamique
    et à l'analyse comportementale du gibier.
    """
    
    def __init__(self):
        self._api_key = OWM_API_KEY
        self._cache: Dict[str, Tuple[Any, datetime]] = {}
        self._last_pressure: Optional[float] = None
        self._pressure_history: List[Tuple[datetime, float]] = []
    
    @property
    def is_active(self) -> bool:
        """Vérifie si le service est actif (clé API présente)."""
        return bool(self._api_key and len(self._api_key) > 10)
    
    @property
    def status(self) -> ServiceStatus:
        """Retourne le statut du service."""
        if not self.is_active:
            return ServiceStatus.INACTIVE
        return ServiceStatus.ACTIVE
    
    def get_status_info(self) -> Dict[str, Any]:
        """Retourne les informations de statut du service."""
        return {
            "service": "OpenWeatherMap",
            "status": self.status.value,
            "api_key_configured": self.is_active,
            "cache_entries": len(self._cache),
            "endpoints": {
                "current": "/api/v1/bionic/weather/current",
                "forecast": "/api/v1/bionic/weather/forecast",
                "behavior": "/api/v1/bionic/weather/behavior"
            }
        }
    
    async def get_weather(
        self,
        latitude: float,
        longitude: float,
        include_forecast: bool = True,
        include_behavior: bool = True
    ) -> WeatherResponse:
        """
        Récupère les données météo complètes pour une position.
        
        Args:
            latitude: Latitude du point
            longitude: Longitude du point
            include_forecast: Inclure les prévisions
            include_behavior: Inclure l'analyse comportementale
            
        Returns:
            WeatherResponse avec toutes les données
        """
        # Vérifier si le service est actif
        if not self.is_active:
            return WeatherResponse(
                status=ServiceStatus.INACTIVE,
                error_message="Service météo inactif. Clé API OWM_API_KEY non configurée."
            )
        
        # Vérifier le cache
        cache_key = f"{latitude:.4f},{longitude:.4f}"
        cached_data = self._get_cached(cache_key)
        if cached_data:
            return cached_data
        
        try:
            # Appel API OpenWeatherMap One Call 3.0
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(
                    OWM_ONECALL_URL,
                    params={
                        "lat": latitude,
                        "lon": longitude,
                        "appid": self._api_key,
                        "units": "metric",
                        "exclude": "" if include_forecast else "minutely,hourly,daily"
                    }
                )
                
                if response.status_code == 401:
                    return WeatherResponse(
                        status=ServiceStatus.ERROR,
                        error_message="Clé API OpenWeatherMap invalide"
                    )
                
                if response.status_code == 429:
                    return WeatherResponse(
                        status=ServiceStatus.RATE_LIMITED,
                        error_message="Limite d'appels API atteinte"
                    )
                
                response.raise_for_status()
                data = response.json()
            
            # Parser les données
            weather_response = self._parse_onecall_response(data, include_behavior)
            
            # Mettre en cache
            self._set_cache(cache_key, weather_response)
            
            return weather_response
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Erreur HTTP OpenWeatherMap: {e}")
            return WeatherResponse(
                status=ServiceStatus.ERROR,
                error_message=f"Erreur API: {e.response.status_code}"
            )
        except Exception as e:
            logger.error(f"Erreur OpenWeatherMap: {e}")
            return WeatherResponse(
                status=ServiceStatus.ERROR,
                error_message=str(e)
            )
    
    async def get_current_weather(
        self,
        latitude: float,
        longitude: float
    ) -> WeatherResponse:
        """Récupère uniquement la météo actuelle."""
        return await self.get_weather(
            latitude, longitude,
            include_forecast=False,
            include_behavior=False
        )
    
    async def get_forecast(
        self,
        latitude: float,
        longitude: float,
        hours: int = 24
    ) -> WeatherResponse:
        """
        Récupère les prévisions pour une durée spécifique.
        
        Args:
            latitude: Latitude
            longitude: Longitude
            hours: Nombre d'heures (24, 72, ou 168 pour 7 jours)
        """
        response = await self.get_weather(latitude, longitude)
        
        if response.status != ServiceStatus.ACTIVE:
            return response
        
        # Filtrer selon la durée demandée
        if hours <= 24:
            response.hourly_72h = []
        elif hours <= 72:
            response.hourly_72h = response.hourly_72h[:72]
        
        return response
    
    async def get_behavior_analysis(
        self,
        latitude: float,
        longitude: float,
        species: str = "moose"
    ) -> Dict[str, Any]:
        """
        Analyse comportementale basée sur la météo.
        
        Returns:
            Dict avec les facteurs comportementaux
        """
        response = await self.get_weather(latitude, longitude)
        
        if response.status != ServiceStatus.ACTIVE:
            return {
                "status": response.status.value,
                "error": response.error_message,
                "factors": None
            }
        
        # Calculer les facteurs spécifiques à l'espèce
        factors = self._calculate_species_factors(
            response.current,
            response.hourly_24h,
            species
        )
        
        return {
            "status": "active",
            "species": species,
            "current_conditions": response.current.to_dict() if response.current else None,
            "factors": factors.to_dict() if factors else None
        }
    
    def _parse_onecall_response(
        self,
        data: Dict[str, Any],
        include_behavior: bool
    ) -> WeatherResponse:
        """Parse la réponse One Call API."""
        
        # Current weather
        current_data = data.get("current", {})
        current = CurrentWeather(
            timestamp=datetime.fromtimestamp(current_data.get("dt", 0), tz=timezone.utc),
            temperature=current_data.get("temp", 0),
            feels_like=current_data.get("feels_like", 0),
            humidity=current_data.get("humidity", 0),
            pressure=current_data.get("pressure", 1013),
            wind_speed=current_data.get("wind_speed", 0) * 3.6,  # m/s to km/h
            wind_direction=current_data.get("wind_deg", 0),
            wind_gust=current_data.get("wind_gust", 0) * 3.6 if current_data.get("wind_gust") else None,
            precipitation_1h=current_data.get("rain", {}).get("1h", 0),
            snow_1h=current_data.get("snow", {}).get("1h", 0),
            cloud_cover=current_data.get("clouds", 0),
            visibility=current_data.get("visibility", 10000),
            condition=self._parse_condition(current_data.get("weather", [{}])[0].get("main", "")),
            condition_description=current_data.get("weather", [{}])[0].get("description", ""),
            sunrise=datetime.fromtimestamp(current_data.get("sunrise", 0), tz=timezone.utc) if current_data.get("sunrise") else None,
            sunset=datetime.fromtimestamp(current_data.get("sunset", 0), tz=timezone.utc) if current_data.get("sunset") else None
        )
        
        # Mettre à jour l'historique de pression
        self._update_pressure_history(current.pressure)
        
        # Hourly forecast (48h disponibles)
        hourly_data = data.get("hourly", [])
        hourly_24h = []
        hourly_72h = []
        
        for i, hour in enumerate(hourly_data):
            forecast = HourlyForecast(
                timestamp=datetime.fromtimestamp(hour.get("dt", 0), tz=timezone.utc),
                temperature=hour.get("temp", 0),
                feels_like=hour.get("feels_like", 0),
                humidity=hour.get("humidity", 0),
                pressure=hour.get("pressure", 1013),
                wind_speed=hour.get("wind_speed", 0) * 3.6,
                wind_direction=hour.get("wind_deg", 0),
                precipitation_prob=hour.get("pop", 0),
                precipitation_mm=hour.get("rain", {}).get("1h", 0) + hour.get("snow", {}).get("1h", 0),
                condition=self._parse_condition(hour.get("weather", [{}])[0].get("main", "")),
                condition_description=hour.get("weather", [{}])[0].get("description", "")
            )
            
            if i < 24:
                hourly_24h.append(forecast)
            hourly_72h.append(forecast)
        
        # Daily forecast (8 jours)
        daily_data = data.get("daily", [])
        daily_7d = []
        
        for day in daily_data[:7]:
            daily = DailyForecast(
                date=datetime.fromtimestamp(day.get("dt", 0), tz=timezone.utc),
                temp_min=day.get("temp", {}).get("min", 0),
                temp_max=day.get("temp", {}).get("max", 0),
                temp_day=day.get("temp", {}).get("day", 0),
                temp_night=day.get("temp", {}).get("night", 0),
                humidity=day.get("humidity", 0),
                pressure=day.get("pressure", 1013),
                wind_speed=day.get("wind_speed", 0) * 3.6,
                wind_direction=day.get("wind_deg", 0),
                precipitation_prob=day.get("pop", 0),
                precipitation_mm=day.get("rain", 0) + day.get("snow", 0),
                condition=self._parse_condition(day.get("weather", [{}])[0].get("main", "")),
                condition_description=day.get("weather", [{}])[0].get("description", ""),
                sunrise=datetime.fromtimestamp(day.get("sunrise", 0), tz=timezone.utc),
                sunset=datetime.fromtimestamp(day.get("sunset", 0), tz=timezone.utc),
                moon_phase=day.get("moon_phase", 0)
            )
            daily_7d.append(daily)
        
        # Behavior factors
        behavior_factors = None
        if include_behavior:
            behavior_factors = self._calculate_behavior_factors(current, hourly_24h)
        
        return WeatherResponse(
            status=ServiceStatus.ACTIVE,
            current=current,
            hourly_24h=hourly_24h,
            hourly_72h=hourly_72h,
            daily_7d=daily_7d,
            behavior_factors=behavior_factors,
            cached=False,
            cache_expires=datetime.now(timezone.utc) + timedelta(seconds=CACHE_TTL_CURRENT)
        )
    
    def _parse_condition(self, condition: str) -> WeatherCondition:
        """Parse la condition météo."""
        condition_map = {
            "Clear": WeatherCondition.CLEAR,
            "Clouds": WeatherCondition.CLOUDS,
            "Rain": WeatherCondition.RAIN,
            "Drizzle": WeatherCondition.DRIZZLE,
            "Snow": WeatherCondition.SNOW,
            "Thunderstorm": WeatherCondition.THUNDERSTORM,
            "Mist": WeatherCondition.MIST,
            "Fog": WeatherCondition.FOG,
        }
        return condition_map.get(condition, WeatherCondition.UNKNOWN)
    
    def _update_pressure_history(self, pressure: float) -> None:
        """Met à jour l'historique de pression."""
        now = datetime.now(timezone.utc)
        self._pressure_history.append((now, pressure))
        
        # Garder seulement les 24 dernières heures
        cutoff = now - timedelta(hours=24)
        self._pressure_history = [
            (ts, p) for ts, p in self._pressure_history if ts > cutoff
        ]
        
        self._last_pressure = pressure
    
    def _get_pressure_trend(self) -> str:
        """Calcule la tendance de pression."""
        if len(self._pressure_history) < 2:
            return "stable"
        
        recent = self._pressure_history[-1][1]
        older = self._pressure_history[0][1]
        
        diff = recent - older
        
        if diff > 2:
            return "rising"
        elif diff < -2:
            return "falling"
        return "stable"
    
    def _calculate_behavior_factors(
        self,
        current: CurrentWeather,
        hourly: List[HourlyForecast]
    ) -> WeatherBehaviorFactors:
        """Calcule les facteurs comportementaux basés sur la météo."""
        
        # Activity modifier basé sur le vent et les précipitations
        activity_mod = 0.0
        
        # Vent
        if current.wind_speed < WIND_THRESHOLD_LOW:
            activity_mod += 0.2
        elif current.wind_speed > WIND_THRESHOLD_HIGH:
            activity_mod -= 0.4
        
        # Précipitations
        if current.precipitation_1h > 5:
            activity_mod -= 0.3
        elif current.precipitation_1h > 0:
            activity_mod -= 0.1
        
        # Pression atmosphérique
        if PRESSURE_OPTIMAL_LOW <= current.pressure <= PRESSURE_OPTIMAL_HIGH:
            activity_mod += 0.2
        
        # Feeding modifier
        feeding_mod = activity_mod
        pressure_trend = self._get_pressure_trend()
        
        if pressure_trend == "falling":
            feeding_mod += 0.3  # Alimentation avant tempête
        elif pressure_trend == "rising":
            feeding_mod += 0.1
        
        # Movement modifier
        movement_mod = activity_mod
        if current.condition in [WeatherCondition.RAIN, WeatherCondition.SNOW]:
            movement_mod -= 0.2
        
        # Heures optimales
        optimal_hours = []
        for h in hourly[:24]:
            hour = h.timestamp.hour
            # Crépuscule = optimal
            if hour in [5, 6, 7, 17, 18, 19]:
                if h.precipitation_prob < 0.5 and h.wind_speed < WIND_THRESHOLD_HIGH:
                    optimal_hours.append(hour)
        
        if not optimal_hours:
            optimal_hours = [6, 7, 17, 18]  # Défaut
        
        # Risk factors
        risk_factors = []
        if current.wind_speed > WIND_THRESHOLD_HIGH:
            risk_factors.append("Vent fort - activité réduite")
        if current.precipitation_1h > 5:
            risk_factors.append("Précipitations importantes")
        if current.visibility < 1000:
            risk_factors.append("Visibilité réduite")
        if pressure_trend == "falling":
            risk_factors.append("Pression en baisse - tempête possible")
        
        # Recommendations
        recommendations = []
        if pressure_trend == "falling":
            recommendations.append("Augmentation probable de l'activité avant la tempête")
        if current.condition == WeatherCondition.CLEAR and current.wind_speed < WIND_THRESHOLD_LOW:
            recommendations.append("Conditions optimales pour l'observation")
        if current.temperature < -15:
            recommendations.append("Grand froid - gibier regroupé dans les ravages")
        
        return WeatherBehaviorFactors(
            activity_modifier=max(-1, min(1, activity_mod)),
            feeding_modifier=max(-1, min(1, feeding_mod)),
            movement_modifier=max(-1, min(1, movement_mod)),
            pressure_trend=pressure_trend,
            optimal_hours=list(set(optimal_hours)),
            risk_factors=risk_factors,
            recommendations=recommendations
        )
    
    def _calculate_species_factors(
        self,
        current: Optional[CurrentWeather],
        hourly: List[HourlyForecast],
        species: str
    ) -> Optional[WeatherBehaviorFactors]:
        """Calcule les facteurs spécifiques à une espèce."""
        if not current:
            return None
        
        base_factors = self._calculate_behavior_factors(current, hourly)
        
        # Ajustements par espèce
        if species == "moose":
            # Orignal préfère le froid
            temp_comfort = TEMP_COMFORT_MOOSE
            if current.temperature > temp_comfort[1]:
                base_factors.activity_modifier -= 0.2
                base_factors.recommendations.append("Chaleur - orignal moins actif en journée")
            elif current.temperature < temp_comfort[0]:
                base_factors.activity_modifier -= 0.1
        
        elif species == "deer":
            # Chevreuil plus sensible au froid
            temp_comfort = TEMP_COMFORT_DEER
            if current.temperature < temp_comfort[0]:
                base_factors.activity_modifier -= 0.3
                base_factors.recommendations.append("Froid intense - chevreuil regroupé")
        
        elif species == "bear":
            # Ours sensible aux précipitations
            if current.precipitation_1h > 2:
                base_factors.activity_modifier -= 0.4
        
        return base_factors
    
    def _get_cached(self, key: str) -> Optional[WeatherResponse]:
        """Récupère les données en cache."""
        if key in self._cache:
            data, expires = self._cache[key]
            if datetime.now(timezone.utc) < expires:
                data.cached = True
                return data
            del self._cache[key]
        return None
    
    def _set_cache(self, key: str, data: WeatherResponse) -> None:
        """Met en cache les données."""
        expires = datetime.now(timezone.utc) + timedelta(seconds=CACHE_TTL_CURRENT)
        data.cache_expires = expires
        self._cache[key] = (data, expires)


# =============================================================================
# SINGLETON
# =============================================================================

_weather_service: Optional[WeatherService] = None


def get_weather_service() -> WeatherService:
    """Retourne l'instance singleton du service météo."""
    global _weather_service
    if _weather_service is None:
        _weather_service = WeatherService()
    return _weather_service


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'WeatherService',
    'get_weather_service',
    'WeatherResponse',
    'CurrentWeather',
    'HourlyForecast',
    'DailyForecast',
    'WeatherBehaviorFactors',
    'WeatherCondition',
    'ServiceStatus'
]
