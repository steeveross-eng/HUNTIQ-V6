"""Weather Engine Models - CORE

Pydantic models for weather-related hunting analysis.

Version: 1.1.0 - Extended for Advanced Weather Widget
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime


# === EXISTING MODELS (PRESERVED) ===

class WeatherCondition(BaseModel):
    """Current weather conditions"""
    temperature: float = Field(description="Temperature in Celsius")
    humidity: float = Field(ge=0, le=100, description="Humidity percentage")
    wind_speed: float = Field(ge=0, description="Wind speed in km/h")
    wind_direction: str = Field(description="Cardinal direction")
    pressure: float = Field(description="Atmospheric pressure in hPa")
    precipitation: float = Field(ge=0, description="Precipitation in mm")
    condition: str = Field(description="Weather condition text")
    icon: Optional[str] = None


class HuntingForecast(BaseModel):
    """Hunting conditions forecast"""
    date: datetime
    overall_score: float = Field(ge=0, le=10, description="Overall hunting score")
    deer_activity: Literal["low", "moderate", "high", "peak"] = "moderate"
    best_times: List[str] = Field(default_factory=list, description="Best hunting times")
    wind_advice: str = ""
    pressure_trend: Literal["rising", "stable", "falling"] = "stable"
    recommendations: List[str] = Field(default_factory=list)


class WeatherRequest(BaseModel):
    """Request for weather data"""
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    days: int = Field(default=3, ge=1, le=7)


class MoonPhase(BaseModel):
    """Moon phase information"""
    phase: Literal["new", "waxing_crescent", "first_quarter", "waxing_gibbous", 
                   "full", "waning_gibbous", "third_quarter", "waning_crescent"]
    illumination: float = Field(ge=0, le=100)
    rise_time: Optional[str] = None
    set_time: Optional[str] = None
    hunting_impact: str = ""


# === NEW MODELS FOR ADVANCED WEATHER WIDGET ===

class WeatherLocation(BaseModel):
    """Geographic location with metadata"""
    lat: float
    lng: float
    city: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None


class WindData(BaseModel):
    """Detailed wind information"""
    speed: float = Field(description="Wind speed in km/h")
    gust: Optional[float] = Field(default=None, description="Wind gust in km/h")
    direction: int = Field(ge=0, le=360, description="Wind direction in degrees")
    direction_text: str = Field(description="Cardinal direction (N, NE, E, etc.)")


class WeatherConditionDetail(BaseModel):
    """Detailed weather condition with icon"""
    main: str = Field(description="Main condition (Clouds, Rain, etc.)")
    description: str = Field(description="Localized description")
    icon: str = Field(description="OpenWeather icon code")
    icon_url: str = Field(description="Full URL to weather icon")


class PrecipitationData(BaseModel):
    """Precipitation information"""
    probability: float = Field(ge=0, le=100, description="Probability in %")
    amount_1h: float = Field(default=0, ge=0, description="Amount in mm for 1h")


class SunData(BaseModel):
    """Sunrise and sunset times"""
    sunrise: datetime
    sunset: datetime


class CurrentWeather(BaseModel):
    """Complete current weather data"""
    timestamp: datetime
    temperature: float = Field(description="Temperature in Celsius")
    feels_like: float = Field(description="Feels like temperature in Celsius")
    humidity: float = Field(ge=0, le=100)
    pressure: float = Field(description="Atmospheric pressure in hPa")
    wind: WindData
    visibility: int = Field(description="Visibility in meters")
    uv_index: float = Field(ge=0)
    clouds: int = Field(ge=0, le=100, description="Cloud coverage in %")
    dew_point: float = Field(description="Dew point in Celsius")
    condition: WeatherConditionDetail
    precipitation: PrecipitationData
    sun: SunData


class HourlyForecast(BaseModel):
    """Hourly weather forecast"""
    timestamp: datetime
    temperature: float
    feels_like: float
    humidity: float
    wind_speed: float
    condition: WeatherConditionDetail
    precipitation_probability: float = Field(ge=0, le=100)


class DailyTemperature(BaseModel):
    """Daily temperature breakdown"""
    min: float
    max: float
    morning: float
    day: float
    evening: float
    night: float


class DailyForecast(BaseModel):
    """Daily weather forecast"""
    date: str = Field(description="Date in YYYY-MM-DD format")
    temperature: DailyTemperature
    feels_like: DailyTemperature
    humidity: float
    pressure: float
    wind_speed: float
    condition: WeatherConditionDetail
    precipitation_probability: float = Field(ge=0, le=100)
    uv_index: float
    sun: SunData


class MoonData(BaseModel):
    """Moon information for hunting analysis"""
    phase: str
    phase_name: str
    illumination: float = Field(ge=0, le=100)
    impact: str = Field(description="Impact on hunting activity")


class HuntingAnalysis(BaseModel):
    """Hunting conditions analysis"""
    overall_score: float = Field(ge=0, le=10)
    activity_level: Literal["low", "moderate", "high", "peak"]
    best_times_today: List[str]
    moon: MoonData
    recommendations: List[str]


class FullWeatherResponse(BaseModel):
    """Complete weather response for advanced widget"""
    success: bool = True
    location: WeatherLocation
    current: CurrentWeather
    hourly: List[HourlyForecast]
    daily: List[DailyForecast]
    hunting_analysis: HuntingAnalysis
    cached_at: datetime
    cache_expires: datetime
