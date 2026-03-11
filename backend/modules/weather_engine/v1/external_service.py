"""
Weather External Service - OpenWeatherMap Integration
Version: 1.0.0

Provides real-time weather data from OpenWeatherMap API
with caching, normalization, and error handling.
"""

import os
import httpx
import logging
import math
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List, Tuple

from .models import (
    WeatherLocation, WindData, WeatherConditionDetail, PrecipitationData,
    SunData, CurrentWeather, HourlyForecast, DailyForecast,
    DailyTemperature, MoonData, HuntingAnalysis, FullWeatherResponse
)

logger = logging.getLogger(__name__)


class OpenWeatherMapService:
    """Service for fetching and normalizing OpenWeatherMap data"""
    
    # API Configuration - Using 2.5 API (free tier)
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
    ICON_BASE_URL = "https://openweathermap.org/img/wn"
    
    # Cache configuration
    CACHE_TTL_MINUTES = 30
    
    # Cardinal directions mapping
    CARDINAL_DIRECTIONS = [
        "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"
    ]
    
    # Weather condition translations (French)
    CONDITION_TRANSLATIONS = {
        "clear sky": "Ciel dégagé",
        "few clouds": "Quelques nuages",
        "scattered clouds": "Nuages épars",
        "broken clouds": "Nuages fragmentés",
        "overcast clouds": "Couvert",
        "shower rain": "Averses",
        "rain": "Pluie",
        "light rain": "Pluie légère",
        "moderate rain": "Pluie modérée",
        "heavy intensity rain": "Pluie forte",
        "thunderstorm": "Orage",
        "snow": "Neige",
        "light snow": "Neige légère",
        "mist": "Brume",
        "fog": "Brouillard",
        "haze": "Brume sèche"
    }
    
    # Moon phases
    MOON_PHASES = [
        ("new", "Nouvelle lune"),
        ("waxing_crescent", "Premier croissant"),
        ("first_quarter", "Premier quartier"),
        ("waxing_gibbous", "Gibbeuse croissante"),
        ("full", "Pleine lune"),
        ("waning_gibbous", "Gibbeuse décroissante"),
        ("third_quarter", "Dernier quartier"),
        ("waning_crescent", "Dernier croissant")
    ]
    
    def __init__(self):
        self.api_key = os.environ.get("OPENWEATHERMAP_API_KEY")
        self._cache: Dict[str, Tuple[datetime, Any]] = {}
        
        if not self.api_key:
            logger.warning("OPENWEATHERMAP_API_KEY not configured")
    
    def _get_cache_key(self, lat: float, lng: float) -> str:
        """Generate cache key from coordinates (rounded to 2 decimals)"""
        return f"{round(lat, 2)}_{round(lng, 2)}"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self._cache:
            return False
        
        cached_time, _ = self._cache[cache_key]
        return datetime.now(timezone.utc) - cached_time < timedelta(minutes=self.CACHE_TTL_MINUTES)
    
    def _get_cached(self, cache_key: str) -> Optional[Any]:
        """Get data from cache if valid"""
        if self._is_cache_valid(cache_key):
            _, data = self._cache[cache_key]
            logger.debug(f"Cache hit for {cache_key}")
            return data
        return None
    
    def _set_cache(self, cache_key: str, data: Any) -> None:
        """Store data in cache"""
        self._cache[cache_key] = (datetime.now(timezone.utc), data)
        logger.debug(f"Cached data for {cache_key}")
    
    def _degrees_to_cardinal(self, degrees: int) -> str:
        """Convert wind direction in degrees to cardinal direction"""
        index = round(degrees / 22.5) % 16
        return self.CARDINAL_DIRECTIONS[index]
    
    def _translate_condition(self, description: str) -> str:
        """Translate weather condition to French"""
        return self.CONDITION_TRANSLATIONS.get(description.lower(), description.capitalize())
    
    def _get_icon_url(self, icon_code: str) -> str:
        """Get full URL for weather icon"""
        return f"{self.ICON_BASE_URL}/{icon_code}@2x.png"
    
    def _calculate_moon_phase(self, timestamp: Optional[int] = None) -> Tuple[str, str, float]:
        """Calculate moon phase from timestamp or current time"""
        if timestamp:
            date = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        else:
            date = datetime.now(timezone.utc)
        
        # Approximate moon phase calculation
        # New moon reference: January 6, 2000
        reference = datetime(2000, 1, 6, tzinfo=timezone.utc)
        days_since = (date - reference).days
        lunar_cycle = 29.53059  # days
        
        phase_day = days_since % lunar_cycle
        phase_index = int((phase_day / lunar_cycle) * 8) % 8
        illumination = (1 - math.cos(2 * math.pi * phase_day / lunar_cycle)) / 2 * 100
        
        phase_code, phase_name = self.MOON_PHASES[phase_index]
        return phase_code, phase_name, round(illumination, 1)
    
    def _get_hunting_impact(self, moon_phase: str, illumination: float) -> str:
        """Get hunting impact description based on moon phase"""
        impacts = {
            "new": "Activité nocturne réduite - Excellentes conditions diurnes",
            "waxing_crescent": "Activité crépusculaire modérée",
            "first_quarter": "Activité accrue en fin de journée",
            "waxing_gibbous": "Activité nocturne croissante",
            "full": "Activité nocturne maximale - Chasse matinale recommandée",
            "waning_gibbous": "Activité crépusculaire élevée",
            "third_quarter": "Bonnes conditions matinales",
            "waning_crescent": "Retour aux conditions diurnes favorables"
        }
        return impacts.get(moon_phase, "Conditions standard")
    
    def _calculate_hunting_score(self, weather_data: Dict) -> Tuple[float, str, List[str]]:
        """Calculate hunting score based on weather conditions"""
        score = 5.0  # Base score
        recommendations = []
        
        current = weather_data.get("current", {})
        
        # Temperature factor (-5 to +15°C is ideal for deer)
        temp = current.get("temp", 10)
        if -5 <= temp <= 15:
            score += 1.5
            recommendations.append("Température idéale pour l'activité du gibier")
        elif temp < -15 or temp > 25:
            score -= 1.5
            recommendations.append("Température extrême - activité réduite")
        
        # Wind factor (5-20 km/h is ideal)
        wind_speed = current.get("wind_speed", 10) * 3.6  # Convert m/s to km/h
        if 5 <= wind_speed <= 20:
            score += 1.0
            recommendations.append("Vent favorable - positionnez-vous vent de face")
        elif wind_speed > 35:
            score -= 1.5
            recommendations.append("Vent fort - chasse à l'affût recommandée")
        
        # Pressure factor (rising pressure is good)
        pressure = current.get("pressure", 1015)
        if pressure > 1020:
            score += 1.0
            recommendations.append("Haute pression - activité accrue")
        elif pressure < 1000:
            score -= 0.5
            recommendations.append("Basse pression - activité réduite possible")
        
        # Precipitation factor
        rain = current.get("rain", {}).get("1h", 0)
        snow = current.get("snow", {}).get("1h", 0)
        if rain == 0 and snow == 0:
            score += 0.5
        elif rain > 5 or snow > 5:
            score -= 1.0
            recommendations.append("Précipitations significatives - visibilité réduite")
        
        # Humidity factor (60-80% is ideal)
        humidity = current.get("humidity", 70)
        if 60 <= humidity <= 80:
            score += 0.5
        
        # Normalize score
        score = max(0, min(10, score))
        
        # Determine activity level
        if score >= 7.5:
            activity = "peak"
        elif score >= 6:
            activity = "high"
        elif score >= 4:
            activity = "moderate"
        else:
            activity = "low"
        
        if not recommendations:
            recommendations.append("Conditions standard pour la chasse")
        
        return round(score, 1), activity, recommendations
    
    def _get_best_hunting_times(self, sunrise: int, sunset: int) -> List[str]:
        """Calculate best hunting times based on sunrise/sunset"""
        sunrise_dt = datetime.fromtimestamp(sunrise, tz=timezone.utc)
        sunset_dt = datetime.fromtimestamp(sunset, tz=timezone.utc)
        
        # Best times: 30 min before sunrise to 2h after, and 2h before sunset to 30 min after
        morning_start = (sunrise_dt - timedelta(minutes=30)).strftime("%H:%M")
        morning_end = (sunrise_dt + timedelta(hours=2)).strftime("%H:%M")
        evening_start = (sunset_dt - timedelta(hours=2)).strftime("%H:%M")
        evening_end = (sunset_dt + timedelta(minutes=30)).strftime("%H:%M")
        
        return [f"{morning_start}-{morning_end}", f"{evening_start}-{evening_end}"]
    
    async def get_full_weather(self, lat: float, lng: float) -> FullWeatherResponse:
        """Get complete weather data with hunting analysis"""
        cache_key = self._get_cache_key(lat, lng)
        
        # Check cache
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        now = datetime.now(timezone.utc)
        
        # Try to fetch real data from OpenWeatherMap 2.5 API
        current_data = None
        forecast_data = []
        api_success = False
        
        if self.api_key:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    # Fetch current weather
                    current_response = await client.get(
                        f"{self.BASE_URL}/weather",
                        params={
                            "lat": lat,
                            "lon": lng,
                            "appid": self.api_key,
                            "units": "metric",
                            "lang": "fr"
                        }
                    )
                    
                    # Fetch 5-day forecast (3-hour intervals)
                    forecast_response = await client.get(
                        self.FORECAST_URL,
                        params={
                            "lat": lat,
                            "lon": lng,
                            "appid": self.api_key,
                            "units": "metric",
                            "lang": "fr"
                        }
                    )
                    
                    if current_response.status_code == 200:
                        current_data = current_response.json()
                        api_success = True
                        logger.info(f"OpenWeatherMap current weather fetched for {lat},{lng}")
                    else:
                        logger.warning(f"OpenWeatherMap current API error: {current_response.status_code}")
                    
                    if forecast_response.status_code == 200:
                        forecast_data = forecast_response.json().get("list", [])
                        logger.info(f"OpenWeatherMap forecast fetched: {len(forecast_data)} entries")
                    else:
                        logger.warning(f"OpenWeatherMap forecast API error: {forecast_response.status_code}")
                        
            except httpx.RequestError as e:
                logger.warning(f"OpenWeatherMap request failed, using fallback: {e}")
        else:
            logger.warning("OpenWeatherMap API key not configured, using simulated data")
        
        # Use real data or generate simulated data
        if api_success and current_data:
            result = self._build_response_from_api(lat, lng, current_data, forecast_data, now)
        else:
            result = self._build_simulated_response(lat, lng, now)
        
        # Store in cache
        self._set_cache(cache_key, result)
        
        return result
    
    def _build_response_from_api(
        self, lat: float, lng: float, 
        current_data: Dict, forecast_data: List, 
        now: datetime
    ) -> FullWeatherResponse:
        """Build response from real API data"""
        
        # Build location
        location = WeatherLocation(
            lat=lat,
            lng=lng,
            city=current_data.get("name"),
            country=current_data.get("sys", {}).get("country"),
            timezone="UTC"
        )
        
        # Build current weather
        wind_deg = current_data.get("wind", {}).get("deg", 0)
        weather_info = current_data.get("weather", [{}])[0]
        sys_info = current_data.get("sys", {})
        
        sunrise_ts = sys_info.get("sunrise", int(now.timestamp()))
        sunset_ts = sys_info.get("sunset", int(now.timestamp()) + 36000)
        
        current = CurrentWeather(
            timestamp=datetime.fromtimestamp(current_data.get("dt", now.timestamp()), tz=timezone.utc),
            temperature=current_data.get("main", {}).get("temp", 0),
            feels_like=current_data.get("main", {}).get("feels_like", 0),
            humidity=current_data.get("main", {}).get("humidity", 0),
            pressure=current_data.get("main", {}).get("pressure", 1015),
            wind=WindData(
                speed=round(current_data.get("wind", {}).get("speed", 0) * 3.6, 1),
                gust=round(current_data.get("wind", {}).get("gust", 0) * 3.6, 1) if current_data.get("wind", {}).get("gust") else None,
                direction=wind_deg,
                direction_text=self._degrees_to_cardinal(wind_deg)
            ),
            visibility=current_data.get("visibility", 10000),
            uv_index=0,  # Not available in 2.5 API
            clouds=current_data.get("clouds", {}).get("all", 0),
            dew_point=0,  # Not available in 2.5 API
            condition=WeatherConditionDetail(
                main=weather_info.get("main", "Unknown"),
                description=weather_info.get("description", "").capitalize(),
                icon=weather_info.get("icon", "01d"),
                icon_url=self._get_icon_url(weather_info.get("icon", "01d"))
            ),
            precipitation=PrecipitationData(
                probability=0,
                amount_1h=current_data.get("rain", {}).get("1h", 0) + current_data.get("snow", {}).get("1h", 0)
            ),
            sun=SunData(
                sunrise=datetime.fromtimestamp(sunrise_ts, tz=timezone.utc),
                sunset=datetime.fromtimestamp(sunset_ts, tz=timezone.utc)
            )
        )
        
        # Build hourly forecast from 3-hour intervals
        hourly = []
        for f in forecast_data[:16]:  # ~48 hours from 3-hour intervals
            f_weather = f.get("weather", [{}])[0]
            hourly.append(HourlyForecast(
                timestamp=datetime.fromtimestamp(f.get("dt", now.timestamp()), tz=timezone.utc),
                temperature=f.get("main", {}).get("temp", 0),
                feels_like=f.get("main", {}).get("feels_like", 0),
                humidity=f.get("main", {}).get("humidity", 0),
                wind_speed=round(f.get("wind", {}).get("speed", 0) * 3.6, 1),
                condition=WeatherConditionDetail(
                    main=f_weather.get("main", "Unknown"),
                    description=f_weather.get("description", "").capitalize(),
                    icon=f_weather.get("icon", "01d"),
                    icon_url=self._get_icon_url(f_weather.get("icon", "01d"))
                ),
                precipitation_probability=f.get("pop", 0) * 100
            ))
        
        # Build daily forecast by aggregating 3-hour data
        daily = self._aggregate_daily_forecast(forecast_data, now)
        
        # Calculate hunting analysis
        score, activity, recommendations = self._calculate_hunting_score({"current": current_data.get("main", {})})
        moon_phase, moon_name, moon_illum = self._calculate_moon_phase()
        best_times = self._get_best_hunting_times(sunrise_ts, sunset_ts)
        
        hunting = HuntingAnalysis(
            overall_score=score,
            activity_level=activity,
            best_times_today=best_times,
            moon=MoonData(
                phase=moon_phase,
                phase_name=moon_name,
                illumination=moon_illum,
                impact=self._get_hunting_impact(moon_phase, moon_illum)
            ),
            recommendations=recommendations
        )
        
        return FullWeatherResponse(
            success=True,
            location=location,
            current=current,
            hourly=hourly,
            daily=daily,
            hunting_analysis=hunting,
            cached_at=now,
            cache_expires=now + timedelta(minutes=self.CACHE_TTL_MINUTES)
        )
    
    def _aggregate_daily_forecast(self, forecast_data: List, now: datetime) -> List[DailyForecast]:
        """Aggregate 3-hour forecast data into daily forecasts"""
        daily_map: Dict[str, List] = {}
        
        for f in forecast_data:
            date_str = datetime.fromtimestamp(f.get("dt", now.timestamp()), tz=timezone.utc).strftime("%Y-%m-%d")
            if date_str not in daily_map:
                daily_map[date_str] = []
            daily_map[date_str].append(f)
        
        daily = []
        for date_str, entries in list(daily_map.items())[:7]:
            temps = [e.get("main", {}).get("temp", 0) for e in entries]
            humidities = [e.get("main", {}).get("humidity", 0) for e in entries]
            pressures = [e.get("main", {}).get("pressure", 1015) for e in entries]
            winds = [e.get("wind", {}).get("speed", 0) * 3.6 for e in entries]
            pops = [e.get("pop", 0) * 100 for e in entries]
            
            # Get most common weather condition
            weather = entries[len(entries)//2].get("weather", [{}])[0]
            
            daily.append(DailyForecast(
                date=date_str,
                temperature=DailyTemperature(
                    min=min(temps) if temps else 0,
                    max=max(temps) if temps else 0,
                    morning=temps[0] if len(temps) > 0 else 0,
                    day=temps[len(temps)//2] if len(temps) > 2 else temps[0] if temps else 0,
                    evening=temps[-2] if len(temps) > 2 else temps[-1] if temps else 0,
                    night=temps[-1] if temps else 0
                ),
                feels_like=DailyTemperature(
                    min=min(temps) - 3,
                    max=max(temps) - 2,
                    morning=temps[0] - 3 if temps else 0,
                    day=temps[len(temps)//2] - 2 if len(temps) > 2 else 0,
                    evening=temps[-2] - 2 if len(temps) > 2 else 0,
                    night=temps[-1] - 4 if temps else 0
                ),
                humidity=sum(humidities) / len(humidities) if humidities else 70,
                pressure=sum(pressures) / len(pressures) if pressures else 1015,
                wind_speed=round(sum(winds) / len(winds), 1) if winds else 10,
                condition=WeatherConditionDetail(
                    main=weather.get("main", "Clouds"),
                    description=weather.get("description", "").capitalize(),
                    icon=weather.get("icon", "03d"),
                    icon_url=self._get_icon_url(weather.get("icon", "03d"))
                ),
                precipitation_probability=max(pops) if pops else 0,
                uv_index=3,  # Default value
                sun=SunData(
                    sunrise=now.replace(hour=7, minute=0),
                    sunset=now.replace(hour=17, minute=30)
                )
            ))
        
        return daily
    
    def _build_simulated_response(self, lat: float, lng: float, now: datetime) -> FullWeatherResponse:
        """Build simulated response when API is unavailable"""
        logger.info(f"Building simulated weather response for {lat},{lng}")
        
        # Simulate seasonal temperature for Quebec area
        month = now.month
        base_temp = {1: -10, 2: -8, 3: -2, 4: 5, 5: 12, 6: 18, 7: 22, 8: 21, 9: 15, 10: 8, 11: 2, 12: -5}
        temp = base_temp.get(month, 10) + (hash(f"{lat}{lng}") % 6 - 3)
        
        location = WeatherLocation(lat=lat, lng=lng, timezone="America/Toronto")
        
        sunrise = now.replace(hour=7, minute=0, second=0, microsecond=0)
        sunset = now.replace(hour=17, minute=30, second=0, microsecond=0)
        
        current = CurrentWeather(
            timestamp=now,
            temperature=temp,
            feels_like=temp - 3,
            humidity=72,
            pressure=1015,
            wind=WindData(speed=15, gust=22, direction=225, direction_text="SW"),
            visibility=10000,
            uv_index=2,
            clouds=45,
            dew_point=temp - 8,
            condition=WeatherConditionDetail(
                main="Clouds",
                description="Partiellement nuageux",
                icon="03d",
                icon_url=self._get_icon_url("03d")
            ),
            precipitation=PrecipitationData(probability=15, amount_1h=0),
            sun=SunData(sunrise=sunrise, sunset=sunset)
        )
        
        # Generate hourly forecast
        hourly = []
        for h in range(48):
            hour_time = now + timedelta(hours=h)
            hour_temp = temp + (3 if 10 <= hour_time.hour <= 16 else -2)
            hourly.append(HourlyForecast(
                timestamp=hour_time,
                temperature=hour_temp,
                feels_like=hour_temp - 3,
                humidity=70 + (h % 10),
                wind_speed=12 + (h % 8),
                condition=WeatherConditionDetail(
                    main="Clouds",
                    description="Nuageux",
                    icon="04d" if 6 <= hour_time.hour <= 18 else "04n",
                    icon_url=self._get_icon_url("04d")
                ),
                precipitation_probability=10 + (h % 20)
            ))
        
        # Generate daily forecast
        daily = []
        for d in range(7):
            day_date = now + timedelta(days=d)
            day_temp = temp + (d - 3)
            daily.append(DailyForecast(
                date=day_date.strftime("%Y-%m-%d"),
                temperature=DailyTemperature(
                    min=day_temp - 5, max=day_temp + 3,
                    morning=day_temp - 3, day=day_temp + 2,
                    evening=day_temp, night=day_temp - 4
                ),
                feels_like=DailyTemperature(
                    min=day_temp - 8, max=day_temp,
                    morning=day_temp - 6, day=day_temp - 1,
                    evening=day_temp - 3, night=day_temp - 7
                ),
                humidity=68 + (d * 2),
                pressure=1015 - d,
                wind_speed=12 + d,
                condition=WeatherConditionDetail(
                    main="Clouds",
                    description="Variable",
                    icon="03d",
                    icon_url=self._get_icon_url("03d")
                ),
                precipitation_probability=15 + (d * 5),
                uv_index=3,
                sun=SunData(sunrise=sunrise, sunset=sunset)
            ))
        
        # Hunting analysis
        moon_phase, moon_name, moon_illum = self._calculate_moon_phase()
        
        hunting = HuntingAnalysis(
            overall_score=7.2,
            activity_level="high",
            best_times_today=["06:30-08:30", "16:00-18:00"],
            moon=MoonData(
                phase=moon_phase,
                phase_name=moon_name,
                illumination=moon_illum,
                impact=self._get_hunting_impact(moon_phase, moon_illum)
            ),
            recommendations=[
                "Données simulées - API en attente d'activation",
                "Conditions généralement favorables",
                "Positionnez-vous vent de face"
            ]
        )
        
        return FullWeatherResponse(
            success=True,
            location=location,
            current=current,
            hourly=hourly,
            daily=daily,
            hunting_analysis=hunting,
            cached_at=now,
            cache_expires=now + timedelta(minutes=self.CACHE_TTL_MINUTES)
        )
    
    async def get_current(self, lat: float, lng: float) -> CurrentWeather:
        """Get current weather only"""
        full = await self.get_full_weather(lat, lng)
        return full.current
    
    async def get_hourly(self, lat: float, lng: float, hours: int = 48) -> List[HourlyForecast]:
        """Get hourly forecast"""
        full = await self.get_full_weather(lat, lng)
        return full.hourly[:hours]
    
    async def get_daily(self, lat: float, lng: float, days: int = 7) -> List[DailyForecast]:
        """Get daily forecast"""
        full = await self.get_full_weather(lat, lng)
        return full.daily[:days]


# Singleton instance
_weather_service: Optional[OpenWeatherMapService] = None


def get_openweathermap_service() -> OpenWeatherMapService:
    """Get or create OpenWeatherMap service instance"""
    global _weather_service
    if _weather_service is None:
        _weather_service = OpenWeatherMapService()
    return _weather_service
