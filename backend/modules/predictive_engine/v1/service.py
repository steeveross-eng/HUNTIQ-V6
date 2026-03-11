"""Predictive Engine Service

Business logic for hunting success predictions.
Integrates with legal_time_engine to ensure all predictions respect legal hunting hours.

Version: 1.0.0
"""

from datetime import datetime, date, timedelta, time
from typing import List, Optional, Dict, Any
from zoneinfo import ZoneInfo
import random

from .models import (
    PredictionFactor, OptimalTimeSlot, HuntingPrediction,
    ActivityLevel, ActivityTimeline
)

# Import legal time service for legal window calculations
from modules.legal_time_engine.v1.service import LegalTimeService
from modules.legal_time_engine.v1.models import LocationInput


class PredictiveService:
    """Service for hunting success predictions"""
    
    # Species activity patterns (base scores by hour, 0-24)
    SPECIES_PATTERNS = {
        "deer": {
            "name": "Cerf de Virginie",
            "dawn_activity": 95,
            "midday_activity": 30,
            "dusk_activity": 90,
            "night_activity": 60,
            "best_temp_range": (-5, 15),
            "weather_sensitivity": 0.7
        },
        "moose": {
            "name": "Orignal",
            "dawn_activity": 85,
            "midday_activity": 25,
            "dusk_activity": 80,
            "night_activity": 50,
            "best_temp_range": (-10, 10),
            "weather_sensitivity": 0.6
        },
        "bear": {
            "name": "Ours noir",
            "dawn_activity": 70,
            "midday_activity": 40,
            "dusk_activity": 75,
            "night_activity": 45,
            "best_temp_range": (5, 25),
            "weather_sensitivity": 0.5
        },
        "wild_turkey": {
            "name": "Dindon sauvage",
            "dawn_activity": 90,
            "midday_activity": 50,
            "dusk_activity": 70,
            "night_activity": 5,
            "best_temp_range": (5, 20),
            "weather_sensitivity": 0.8
        }
    }
    
    # Season factors (month -> multiplier)
    SEASON_FACTORS = {
        1: 0.6,   # January - cold
        2: 0.5,   # February - very cold
        3: 0.6,   # March - late winter
        4: 0.7,   # April - spring
        5: 0.75,  # May - spring
        6: 0.65,  # June - summer start
        7: 0.5,   # July - hot
        8: 0.6,   # August - hot
        9: 0.85,  # September - early fall
        10: 0.95, # October - peak hunting
        11: 0.9,  # November - rut season
        12: 0.7   # December - early winter
    }
    
    def __init__(self):
        self.legal_time_service = LegalTimeService()
        self.default_location = LocationInput(
            latitude=46.8139,
            longitude=-71.2080,
            timezone="America/Toronto"
        )
    
    def predict_hunting_success(
        self,
        species: str = "deer",
        target_date: Optional[date] = None,
        location: Optional[LocationInput] = None,
        weather: Optional[Dict[str, Any]] = None
    ) -> HuntingPrediction:
        """
        Predict hunting success probability for a given species, date, and location.
        
        Args:
            species: Target species (deer, moose, bear, wild_turkey)
            target_date: Date for prediction
            location: Location for sun calculations
            weather: Optional weather data
            
        Returns:
            HuntingPrediction with success probability and factors
        """
        if target_date is None:
            target_date = date.today()
        
        loc = location or self.default_location
        species_data = self.SPECIES_PATTERNS.get(species, self.SPECIES_PATTERNS["deer"])
        
        # Calculate factors
        factors = []
        
        # 1. Season factor
        season_score = int(self.SEASON_FACTORS.get(target_date.month, 0.7) * 100)
        season_impact = self._score_to_impact(season_score)
        factors.append(PredictionFactor(
            name="Saison",
            impact=season_impact,
            score=season_score,
            description=self._get_season_description(target_date.month)
        ))
        
        # 2. Weather factor
        if weather:
            weather_score = self._calculate_weather_score(weather, species_data)
        else:
            weather_score = 70  # Default moderate
        weather_impact = self._score_to_impact(weather_score)
        factors.append(PredictionFactor(
            name="Météo",
            impact=weather_impact,
            score=weather_score,
            description="Conditions météo pour l'espèce ciblée"
        ))
        
        # 3. Moon phase factor (simplified)
        moon_score = self._calculate_moon_score(target_date)
        moon_impact = self._score_to_impact(moon_score)
        factors.append(PredictionFactor(
            name="Phase lunaire",
            impact=moon_impact,
            score=moon_score,
            description=self._get_moon_description(moon_score)
        ))
        
        # 4. Pressure factor (simulated)
        pressure_score = 65 + random.randint(-10, 20)
        pressure_impact = self._score_to_impact(pressure_score)
        factors.append(PredictionFactor(
            name="Pression atmosphérique",
            impact=pressure_impact,
            score=pressure_score,
            description="Tendance de la pression barométrique"
        ))
        
        # 5. Recent activity factor (simulated)
        activity_score = 60 + random.randint(-5, 25)
        activity_impact = self._score_to_impact(activity_score)
        factors.append(PredictionFactor(
            name="Activité récente",
            impact=activity_impact,
            score=activity_score,
            description="Observations récentes dans la région"
        ))
        
        # Calculate overall success probability
        weights = [0.25, 0.20, 0.15, 0.20, 0.20]
        scores = [f.score for f in factors]
        success_probability = int(sum(s * w for s, w in zip(scores, weights)))
        
        # Confidence based on data completeness
        confidence = 0.85 if weather else 0.70
        
        # Get optimal times (integrated with legal window)
        optimal_times = self._get_optimal_times_for_prediction(target_date, loc, species_data)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(success_probability, factors, species)
        
        return HuntingPrediction(
            success_probability=success_probability,
            confidence=confidence,
            factors=factors,
            optimal_times=optimal_times,
            recommendation=recommendation
        )
    
    def get_activity_level(
        self,
        species: str = "deer",
        target_datetime: Optional[datetime] = None,
        location: Optional[LocationInput] = None
    ) -> ActivityLevel:
        """
        Get current or predicted activity level for a species.
        """
        if target_datetime is None:
            tz = ZoneInfo(self.default_location.timezone)
            target_datetime = datetime.now(tz)
        
        loc = location or self.default_location
        species_data = self.SPECIES_PATTERNS.get(species, self.SPECIES_PATTERNS["deer"])
        
        # Get legal window
        legal_window = self.legal_time_service.get_legal_hunting_window(
            target_datetime.date(), loc
        )
        
        # Calculate activity based on time of day
        hour = target_datetime.hour
        activity_score = self._get_activity_by_hour(hour, species_data, legal_window)
        
        # Determine level
        if activity_score >= 80:
            level = "very_high"
        elif activity_score >= 60:
            level = "high"
        elif activity_score >= 40:
            level = "moderate"
        elif activity_score >= 20:
            level = "low"
        else:
            level = "very_low"
        
        # Get peak times
        peak_times = [
            f"{legal_window.start_time.strftime('%H:%M')} - {(datetime.combine(date.today(), legal_window.start_time) + timedelta(hours=2)).time().strftime('%H:%M')}",
            f"{(datetime.combine(date.today(), legal_window.end_time) - timedelta(hours=2)).time().strftime('%H:%M')} - {legal_window.end_time.strftime('%H:%M')}"
        ]
        
        return ActivityLevel(
            species=species,
            level=level,
            score=activity_score,
            peak_times=peak_times
        )
    
    def get_activity_timeline(
        self,
        species: str = "deer",
        target_date: Optional[date] = None,
        location: Optional[LocationInput] = None
    ) -> List[ActivityTimeline]:
        """
        Get hourly activity timeline for a species on a given date.
        Only shows legal hunting hours.
        """
        if target_date is None:
            target_date = date.today()
        
        loc = location or self.default_location
        species_data = self.SPECIES_PATTERNS.get(species, self.SPECIES_PATTERNS["deer"])
        
        # Get legal window and sun times
        legal_window = self.legal_time_service.get_legal_hunting_window(target_date, loc)
        sun_times = self.legal_time_service.get_sun_times(target_date, loc)
        
        timeline = []
        
        for hour in range(24):
            current_time = time(hour, 0)
            
            # Check if within legal hours
            is_legal = legal_window.start_time <= current_time <= legal_window.end_time
            
            # Calculate activity
            activity_score = self._get_activity_by_hour(hour, species_data, legal_window)
            
            # If not legal, still show the score but mark as illegal
            if not is_legal:
                activity_score = int(activity_score * 0.5)  # Reduce displayed score for illegal hours
            
            # Determine light condition
            light_condition = self._get_light_condition(current_time, sun_times)
            
            timeline.append(ActivityTimeline(
                hour=hour,
                activity_level=activity_score,
                is_legal=is_legal,
                light_condition=light_condition
            ))
        
        return timeline
    
    def get_success_factors(
        self,
        species: str = "deer",
        target_date: Optional[date] = None,
        weather: Optional[Dict[str, Any]] = None
    ) -> List[PredictionFactor]:
        """
        Get detailed success factors for hunting prediction.
        """
        prediction = self.predict_hunting_success(species, target_date, weather=weather)
        return prediction.factors
    
    def _calculate_weather_score(self, weather: Dict[str, Any], species_data: Dict) -> int:
        """Calculate weather-based score for a species"""
        score = 70  # Base score
        
        temp = weather.get("temperature", 10)
        min_temp, max_temp = species_data["best_temp_range"]
        
        if min_temp <= temp <= max_temp:
            score += 15
        elif temp < min_temp - 10 or temp > max_temp + 10:
            score -= 20
        
        # Wind penalty
        wind = weather.get("wind_speed", 10)
        if wind > 30:
            score -= 25
        elif wind > 20:
            score -= 15
        elif wind < 10:
            score += 10
        
        # Rain penalty
        if weather.get("precipitation", 0) > 0:
            score -= 10
        
        return max(0, min(100, score))
    
    def _calculate_moon_score(self, target_date: date) -> int:
        """Calculate moon phase score (simplified)"""
        # Simple moon phase calculation
        known_new_moon = date(2024, 1, 11)
        days_since = (target_date - known_new_moon).days
        cycle_position = (days_since % 29.53) / 29.53
        
        # New moon and full moon have different effects
        if cycle_position < 0.1 or cycle_position > 0.9:  # New moon
            return 75  # Good - more daytime activity
        elif 0.4 < cycle_position < 0.6:  # Full moon
            return 50  # Less daytime activity
        else:
            return 65  # Moderate
    
    def _get_moon_description(self, score: int) -> str:
        """Get moon phase description"""
        if score >= 70:
            return "Nouvelle lune - Activité diurne accrue"
        elif score <= 55:
            return "Pleine lune - Activité nocturne, journées plus calmes"
        else:
            return "Phase intermédiaire - Conditions normales"
    
    def _get_season_description(self, month: int) -> str:
        """Get season description"""
        descriptions = {
            1: "Hiver - Activité réduite",
            2: "Hiver rigoureux - Conditions difficiles",
            3: "Fin d'hiver - Reprise progressive",
            4: "Printemps - Activité en hausse",
            5: "Printemps - Bonnes conditions",
            6: "Début d'été - Chaleur modérée",
            7: "Été - Chaleur, activité réduite",
            8: "Fin d'été - Préparation automne",
            9: "Début automne - Excellent",
            10: "Automne - Saison optimale",
            11: "Rut - Période exceptionnelle",
            12: "Début hiver - Bonnes conditions"
        }
        return descriptions.get(month, "Conditions variables")
    
    def _score_to_impact(self, score: int) -> str:
        """Convert score to impact string"""
        if score >= 85:
            return "very_positive"
        elif score >= 65:
            return "positive"
        elif score >= 45:
            return "neutral"
        elif score >= 25:
            return "negative"
        else:
            return "very_negative"
    
    def _get_activity_by_hour(self, hour: int, species_data: Dict, legal_window) -> int:
        """Calculate activity score by hour for a species"""
        sunrise_hour = legal_window.sunrise.hour
        sunset_hour = legal_window.sunset.hour
        
        # Dawn period (2 hours around sunrise)
        if sunrise_hour - 1 <= hour <= sunrise_hour + 2:
            return species_data["dawn_activity"]
        
        # Dusk period (2 hours around sunset)
        if sunset_hour - 2 <= hour <= sunset_hour + 1:
            return species_data["dusk_activity"]
        
        # Midday
        if sunrise_hour + 2 < hour < sunset_hour - 2:
            return species_data["midday_activity"]
        
        # Night
        return species_data["night_activity"]
    
    def _get_optimal_times_for_prediction(
        self, 
        target_date: date, 
        location: LocationInput,
        species_data: Dict
    ) -> List[OptimalTimeSlot]:
        """Get optimal time slots for prediction, respecting legal hours"""
        
        # Use legal time service for accurate windows
        recommended_slots = self.legal_time_service.get_recommended_hunting_slots(target_date, location)
        
        optimal_times = []
        for slot in recommended_slots[:3]:  # Top 3 slots
            # Adjust score based on species activity pattern
            if slot.light_condition == "dawn":
                adjusted_score = int(slot.score * (species_data["dawn_activity"] / 95))
            elif slot.light_condition == "dusk":
                adjusted_score = int(slot.score * (species_data["dusk_activity"] / 90))
            else:
                adjusted_score = int(slot.score * (species_data["midday_activity"] / 55))
            
            optimal_times.append(OptimalTimeSlot(
                period=slot.period_name,
                time=f"{slot.start_time.strftime('%H:%M')}-{slot.end_time.strftime('%H:%M')}",
                score=min(100, adjusted_score),
                is_legal=slot.is_legal
            ))
        
        # Sort by score
        optimal_times.sort(key=lambda x: x.score, reverse=True)
        
        return optimal_times
    
    def _get_light_condition(self, current_time: time, sun_times) -> str:
        """Determine light condition based on time"""
        if current_time < sun_times.dawn:
            return "dark"
        elif current_time < sun_times.sunrise:
            return "dawn"
        elif current_time < sun_times.sunset:
            return "daylight"
        elif current_time < sun_times.dusk:
            return "dusk"
        else:
            return "dark"
    
    def _generate_recommendation(
        self, 
        success_probability: int, 
        factors: List[PredictionFactor],
        species: str
    ) -> str:
        """Generate a recommendation based on prediction results"""
        species_name = self.SPECIES_PATTERNS.get(species, {}).get("name", "gibier")
        
        if success_probability >= 80:
            return f"Conditions excellentes pour la chasse au {species_name}. Maximisez votre temps à l'aube."
        elif success_probability >= 65:
            return f"Bonnes conditions pour le {species_name}. Privilégiez les périodes d'aube et crépuscule."
        elif success_probability >= 50:
            return f"Conditions moyennes. La patience sera clé pour le {species_name}."
        else:
            return "Conditions défavorables. Reportez si possible ou concentrez-vous sur les meilleures fenêtres."
