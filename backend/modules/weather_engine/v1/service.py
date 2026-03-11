"""Weather Engine Service - CORE

Business logic for weather-based hunting analysis.
Provides hunting condition predictions based on weather data.

Version: 1.0.0
"""

from typing import List
from datetime import datetime, timezone
from .models import WeatherCondition, HuntingForecast, MoonPhase


class WeatherService:
    """Service for weather-based hunting analysis"""
    
    # Optimal conditions for deer hunting
    OPTIMAL_CONDITIONS = {
        "temperature": {"min": -5, "max": 15, "ideal": 5},  # Celsius
        "humidity": {"min": 40, "max": 80, "ideal": 60},
        "wind_speed": {"min": 0, "max": 20, "ideal": 8},
        "pressure_change": 5  # hPa change triggers activity
    }
    
    def calculate_hunting_score(self, weather: WeatherCondition) -> float:
        """
        Calculate hunting score based on weather conditions.
        
        Score factors:
        - Temperature (30% weight)
        - Wind speed (25% weight)
        - Pressure trend (20% weight)
        - Humidity (15% weight)
        - Precipitation (10% weight)
        """
        score = 0.0
        
        # Temperature score (30%)
        temp = weather.temperature
        opt = self.OPTIMAL_CONDITIONS["temperature"]
        if opt["min"] <= temp <= opt["max"]:
            # Linear interpolation towards ideal
            if temp <= opt["ideal"]:
                temp_score = (temp - opt["min"]) / (opt["ideal"] - opt["min"]) * 10
            else:
                temp_score = 10 - ((temp - opt["ideal"]) / (opt["max"] - opt["ideal"]) * 5)
        else:
            temp_score = max(0, 10 - abs(temp - opt["ideal"]) * 0.5)
        score += temp_score * 0.30
        
        # Wind speed score (25%)
        wind = weather.wind_speed
        opt_wind = self.OPTIMAL_CONDITIONS["wind_speed"]
        if wind <= opt_wind["ideal"]:
            wind_score = 10
        elif wind <= opt_wind["max"]:
            wind_score = 10 - ((wind - opt_wind["ideal"]) / (opt_wind["max"] - opt_wind["ideal"]) * 5)
        else:
            wind_score = max(0, 5 - (wind - opt_wind["max"]) * 0.3)
        score += wind_score * 0.25
        
        # Pressure score (20%) - based on value, not trend here
        pressure = weather.pressure
        # Normal pressure is around 1013 hPa
        pressure_diff = abs(pressure - 1013)
        pressure_score = max(0, 10 - pressure_diff * 0.3)
        score += pressure_score * 0.20
        
        # Humidity score (15%)
        humidity = weather.humidity
        opt_hum = self.OPTIMAL_CONDITIONS["humidity"]
        if opt_hum["min"] <= humidity <= opt_hum["max"]:
            humidity_score = 10
        else:
            humidity_score = max(0, 10 - abs(humidity - opt_hum["ideal"]) * 0.1)
        score += humidity_score * 0.15
        
        # Precipitation score (10%)
        if weather.precipitation == 0:
            precip_score = 10
        elif weather.precipitation < 2:
            precip_score = 7
        elif weather.precipitation < 5:
            precip_score = 4
        else:
            precip_score = 2
        score += precip_score * 0.10
        
        return round(min(10, max(0, score)), 1)
    
    def get_deer_activity_level(self, score: float, pressure_trend: str = "stable") -> str:
        """Determine deer activity level based on score and pressure"""
        # Pressure changes increase activity
        activity_boost = 1.0 if pressure_trend in ["rising", "falling"] else 0
        adjusted_score = score + activity_boost
        
        if adjusted_score >= 8:
            return "peak"
        elif adjusted_score >= 6:
            return "high"
        elif adjusted_score >= 4:
            return "moderate"
        else:
            return "low"
    
    def get_best_hunting_times(self, weather: WeatherCondition) -> List[str]:
        """Determine best hunting times based on conditions"""
        times = []
        
        # Dawn is almost always good
        times.append("05:30 - 08:00 (Aube)")
        
        # Check if midday is viable (cooler temps)
        if weather.temperature < 10:
            times.append("10:00 - 14:00 (Mi-journée)")
        
        # Dusk is almost always good
        times.append("16:00 - 18:30 (Crépuscule)")
        
        # Night hunting (where legal) in certain conditions
        if weather.wind_speed < 10 and weather.precipitation == 0:
            times.append("18:30 - 21:00 (Soirée)")
        
        return times
    
    def generate_forecast(self, weather: WeatherCondition, date: datetime = None) -> HuntingForecast:
        """Generate hunting forecast from weather conditions"""
        if date is None:
            date = datetime.now(timezone.utc)
        
        score = self.calculate_hunting_score(weather)
        activity = self.get_deer_activity_level(score)
        best_times = self.get_best_hunting_times(weather)
        
        # Wind advice
        if weather.wind_speed < 5:
            wind_advice = "Vent calme - Excellent pour la chasse à l'affût"
        elif weather.wind_speed < 15:
            wind_advice = f"Vent modéré du {weather.wind_direction} - Positionnez-vous vent de face"
        else:
            wind_advice = "Vent fort - Privilégiez les vallées et zones abritées"
        
        # Recommendations
        recommendations = []
        if score >= 7:
            recommendations.append("Conditions excellentes - Maximisez votre temps sur le terrain")
        if weather.temperature < 0:
            recommendations.append("Températures froides - Prévoyez des vêtements chauds et des pauses")
        if weather.precipitation > 0:
            recommendations.append("Pluie prévue - Équipement imperméable requis")
        if activity == "peak":
            recommendations.append("Activité maximale prévue - Soyez en place avant l'aube")
        
        return HuntingForecast(
            date=date,
            overall_score=score,
            deer_activity=activity,
            best_times=best_times,
            wind_advice=wind_advice,
            pressure_trend="stable",
            recommendations=recommendations
        )
    
    def get_moon_phase(self, date: datetime = None) -> MoonPhase:
        """Calculate moon phase for a given date"""
        if date is None:
            date = datetime.now(timezone.utc)
        
        # Simplified moon phase calculation
        # Full moon cycle is approximately 29.53 days
        known_new_moon = datetime(2024, 1, 11, tzinfo=timezone.utc)
        days_since = (date - known_new_moon).days
        cycle_position = (days_since % 29.53) / 29.53
        
        # Determine phase
        if cycle_position < 0.0625:
            phase = "new"
            illumination = 0
        elif cycle_position < 0.1875:
            phase = "waxing_crescent"
            illumination = (cycle_position - 0.0625) / 0.125 * 25
        elif cycle_position < 0.3125:
            phase = "first_quarter"
            illumination = 25 + (cycle_position - 0.1875) / 0.125 * 25
        elif cycle_position < 0.4375:
            phase = "waxing_gibbous"
            illumination = 50 + (cycle_position - 0.3125) / 0.125 * 25
        elif cycle_position < 0.5625:
            phase = "full"
            illumination = 100
        elif cycle_position < 0.6875:
            phase = "waning_gibbous"
            illumination = 100 - (cycle_position - 0.5625) / 0.125 * 25
        elif cycle_position < 0.8125:
            phase = "third_quarter"
            illumination = 75 - (cycle_position - 0.6875) / 0.125 * 25
        elif cycle_position < 0.9375:
            phase = "waning_crescent"
            illumination = 50 - (cycle_position - 0.8125) / 0.125 * 25
        else:
            phase = "new"
            illumination = 0
        
        # Hunting impact
        if phase == "new":
            hunting_impact = "Lune noire - Activité diurne accrue"
        elif phase == "full":
            hunting_impact = "Pleine lune - Activité nocturne, journées plus calmes"
        elif "waxing" in phase:
            hunting_impact = "Lune croissante - Activité crépusculaire forte"
        else:
            hunting_impact = "Lune décroissante - Bonnes conditions matinales"
        
        return MoonPhase(
            phase=phase,
            illumination=round(illumination, 1),
            hunting_impact=hunting_impact
        )
