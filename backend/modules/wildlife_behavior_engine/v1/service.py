"""Wildlife Behavior Engine Service - PLAN MAITRE
Business logic for wildlife behavior modeling.

Version: 1.0.0
"""

import os
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from pymongo import MongoClient

from .models import (
    SpeciesProfile, ActivityPrediction, ActivityLevel, BehaviorType,
    MovementPattern, SeasonalBehavior, Season, PresencePrediction
)


class WildlifeBehaviorService:
    """Service for wildlife behavior analysis"""
    
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'test_database')
        self._client = None
        self._db = None
        
        # Species profiles (would be in DB in production)
        self.species_profiles = {
            "deer": SpeciesProfile(
                species="deer",
                common_name="Cerf de Virginie",
                scientific_name="Odocoileus virginianus",
                primary_activity_time="crepuscular",
                peak_activity_hours=["05:30-08:00", "17:00-19:30"],
                preferred_habitat=["forest_edge", "regeneration", "agricultural"],
                food_sources=["browse", "forbs", "mast", "agricultural"],
                water_dependency="medium",
                home_range_km2=2.5,
                daily_travel_km=3.0,
                group_behavior="small_groups",
                rut_period="October-November"
            ),
            "moose": SpeciesProfile(
                species="moose",
                common_name="Orignal",
                scientific_name="Alces alces",
                primary_activity_time="crepuscular",
                peak_activity_hours=["05:00-09:00", "16:00-20:00"],
                preferred_habitat=["wetlands", "boreal_forest", "regeneration"],
                food_sources=["aquatic_plants", "browse", "bark"],
                water_dependency="high",
                home_range_km2=25.0,
                daily_travel_km=5.0,
                group_behavior="solitary",
                rut_period="September-October"
            ),
            "bear": SpeciesProfile(
                species="bear",
                common_name="Ours noir",
                scientific_name="Ursus americanus",
                primary_activity_time="crepuscular",
                peak_activity_hours=["05:00-10:00", "16:00-21:00"],
                preferred_habitat=["mixed_forest", "berry_patches", "wetlands"],
                food_sources=["berries", "nuts", "insects", "carrion"],
                water_dependency="medium",
                home_range_km2=50.0,
                daily_travel_km=8.0,
                group_behavior="solitary"
            )
        }
    
    @property
    def db(self):
        if self._db is None:
            self._client = MongoClient(self.mongo_url)
            self._db = self._client[self.db_name]
        return self._db
    
    async def get_species_info(self, species: str) -> Optional[SpeciesProfile]:
        """Get species profile"""
        return self.species_profiles.get(species.lower())
    
    async def get_all_species(self) -> List[SpeciesProfile]:
        """Get all tracked species"""
        return list(self.species_profiles.values())
    
    async def predict_activity(
        self,
        species: str,
        date: Optional[datetime] = None,
        coordinates: Optional[Dict[str, float]] = None,
        weather: Optional[Dict[str, Any]] = None
    ) -> ActivityPrediction:
        """Predict species activity level"""
        if date is None:
            date = datetime.now(timezone.utc)
        
        profile = self.species_profiles.get(species.lower())
        if not profile:
            profile = SpeciesProfile(species=species, common_name=species.title())
        
        # Determine season
        month = date.month
        season = self._get_season(month, species)
        
        # Calculate activity score based on factors
        factors = {}
        
        # Time of day factor
        hour = date.hour
        time_score = self._calculate_time_score(hour, profile)
        factors["time_of_day"] = time_score
        
        # Season factor
        season_score = self._calculate_season_score(season, species)
        factors["season"] = season_score
        
        # Weather factor (if provided)
        if weather:
            weather_score = self._calculate_weather_score(weather)
            factors["weather"] = weather_score
        else:
            factors["weather"] = 0.7
        
        # Moon phase (simplified)
        moon_score = 0.7
        factors["moon_phase"] = moon_score
        
        # Calculate overall score
        avg_score = sum(factors.values()) / len(factors) * 100
        
        # Determine activity level
        if avg_score >= 80:
            level = ActivityLevel.VERY_HIGH
        elif avg_score >= 65:
            level = ActivityLevel.HIGH
        elif avg_score >= 50:
            level = ActivityLevel.MODERATE
        elif avg_score >= 35:
            level = ActivityLevel.LOW
        else:
            level = ActivityLevel.MINIMAL
        
        # Determine primary behavior
        behavior = self._get_primary_behavior(hour, season)
        
        # Time of day description
        if 5 <= hour < 9:
            time_desc = "morning"
        elif 9 <= hour < 12:
            time_desc = "mid_morning"
        elif 12 <= hour < 15:
            time_desc = "afternoon"
        elif 15 <= hour < 19:
            time_desc = "evening"
        else:
            time_desc = "night"
        
        return ActivityPrediction(
            species=species,
            date=date,
            time_of_day=time_desc,
            season=season,
            activity_level=level,
            activity_score=round(avg_score, 1),
            primary_behavior=behavior,
            coordinates=coordinates,
            factors=factors,
            confidence=0.75,
            strategy_tips=self._get_strategy_tips(level, behavior, season)
        )
    
    async def get_movement_patterns(
        self,
        species: str,
        pattern_type: str = "daily"
    ) -> MovementPattern:
        """Get movement patterns for species"""
        profile = self.species_profiles.get(species.lower())
        
        peak_times = profile.peak_activity_hours if profile else ["06:00-08:00", "17:00-19:00"]
        
        return MovementPattern(
            species=species,
            pattern_type=pattern_type,
            typical_routes=[
                {"type": "feeding_to_bedding", "distance_km": 0.5, "typical_time": "08:00"},
                {"type": "bedding_to_feeding", "distance_km": 0.5, "typical_time": "16:00"}
            ],
            concentration_zones=[
                {"type": "feeding_area", "habitat": "forest_edge"},
                {"type": "bedding_area", "habitat": "thick_cover"},
                {"type": "water_source", "habitat": "stream"}
            ],
            travel_corridors=[
                {"type": "ridge_line", "usage": "high"},
                {"type": "creek_bottom", "usage": "medium"}
            ],
            peak_movement_times=peak_times
        )
    
    async def get_seasonal_behavior(
        self,
        species: str,
        season: str
    ) -> SeasonalBehavior:
        """Get seasonal behavior patterns"""
        try:
            season_enum = Season(season.lower())
        except ValueError:
            season_enum = Season.EARLY_FALL
        
        # Define behaviors by season
        seasonal_data = {
            Season.PRE_RUT: {
                "activity_modifier": 1.2,
                "primary_behaviors": [BehaviorType.FEEDING, BehaviorType.TERRITORIAL],
                "territorial_intensity": "high",
                "events": ["scrape_making", "rub_activity"]
            },
            Season.RUT: {
                "activity_modifier": 1.5,
                "primary_behaviors": [BehaviorType.RUTTING, BehaviorType.TRAVELING],
                "territorial_intensity": "high",
                "events": ["peak_breeding", "chasing"]
            },
            Season.POST_RUT: {
                "activity_modifier": 0.8,
                "primary_behaviors": [BehaviorType.FEEDING, BehaviorType.RESTING],
                "territorial_intensity": "low",
                "events": ["recovery_feeding"]
            }
        }
        
        data = seasonal_data.get(season_enum, {
            "activity_modifier": 1.0,
            "primary_behaviors": [BehaviorType.FEEDING],
            "territorial_intensity": "medium",
            "events": []
        })
        
        return SeasonalBehavior(
            species=species,
            season=season_enum,
            **data
        )
    
    async def predict_presence(
        self,
        lat: float,
        lng: float,
        radius_km: float = 1.0,
        species_list: Optional[List[str]] = None
    ) -> PresencePrediction:
        """Predict wildlife presence in an area"""
        coords = {"lat": lat, "lng": lng}
        
        if species_list is None:
            species_list = list(self.species_profiles.keys())
        
        predictions = {}
        best_score = 0
        best_species = None
        
        for species in species_list:
            activity = await self.predict_activity(species, coordinates=coords)
            
            prob = activity.activity_score / 100
            predictions[species] = {
                "probability": round(prob, 2),
                "activity_level": activity.activity_level.value,
                "best_time": "06:00-08:00",
                "confidence": activity.confidence
            }
            
            if prob > best_score:
                best_score = prob
                best_species = species
        
        return PresencePrediction(
            coordinates=coords,
            radius_km=radius_km,
            species_predictions=predictions,
            best_species=best_species,
            optimal_hunting_time="06:00-08:00",
            overall_score=round(best_score * 100, 1)
        )
    
    def _get_season(self, month: int, species: str) -> Season:
        """Determine current season for species"""
        if species.lower() == "deer":
            if month == 10:
                return Season.PRE_RUT
            elif month == 11:
                return Season.RUT
            elif month == 12:
                return Season.POST_RUT
        
        if month in [12, 1, 2]:
            return Season.WINTER
        elif month in [3, 4, 5]:
            return Season.SPRING
        elif month in [6, 7, 8]:
            return Season.SUMMER
        else:
            return Season.EARLY_FALL
    
    def _calculate_time_score(self, hour: int, profile: SpeciesProfile) -> float:
        """Calculate activity score based on time"""
        if profile.primary_activity_time == "crepuscular":
            if 5 <= hour <= 8 or 16 <= hour <= 19:
                return 0.95
            elif 8 < hour < 16:
                return 0.3
            else:
                return 0.5
        return 0.6
    
    def _calculate_season_score(self, season: Season, species: str) -> float:
        """Calculate season activity multiplier"""
        scores = {
            Season.RUT: 0.95,
            Season.PRE_RUT: 0.85,
            Season.POST_RUT: 0.6,
            Season.EARLY_FALL: 0.8,
            Season.WINTER: 0.5,
            Season.SPRING: 0.7,
            Season.SUMMER: 0.6
        }
        return scores.get(season, 0.7)
    
    def _calculate_weather_score(self, weather: Dict[str, Any]) -> float:
        """Calculate weather impact on activity"""
        score = 0.7
        
        temp = weather.get("temperature")
        if temp is not None:
            if 5 <= temp <= 15:
                score += 0.2
            elif temp > 25 or temp < -10:
                score -= 0.2
        
        wind = weather.get("wind_speed", 0)
        if wind > 30:
            score -= 0.15
        
        return max(0.2, min(1.0, score))
    
    def _get_primary_behavior(self, hour: int, season: Season) -> BehaviorType:
        """Determine primary behavior"""
        if season == Season.RUT:
            return BehaviorType.RUTTING
        
        if 5 <= hour <= 9 or 16 <= hour <= 19:
            return BehaviorType.FEEDING
        elif 10 <= hour <= 15:
            return BehaviorType.RESTING
        else:
            return BehaviorType.TRAVELING
    
    def _get_strategy_tips(
        self,
        level: ActivityLevel,
        behavior: BehaviorType,
        season: Season
    ) -> List[str]:
        """Get hunting strategy tips"""
        tips = []
        
        if level in [ActivityLevel.VERY_HIGH, ActivityLevel.HIGH]:
            tips.append("Conditions favorables - soyez prêt")
        
        if behavior == BehaviorType.FEEDING:
            tips.append("Surveillez les zones d'alimentation")
        elif behavior == BehaviorType.TRAVELING:
            tips.append("Positionnez-vous sur les corridors de déplacement")
        elif behavior == BehaviorType.RUTTING:
            tips.append("Utilisez des appels et attractants de rut")
        
        if season == Season.RUT:
            tips.append("Période de rut - activité diurne accrue")
        
        return tips
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics"""
        return {
            "tracked_species": len(self.species_profiles),
            "species_list": list(self.species_profiles.keys()),
            "seasons": [s.value for s in Season],
            "behavior_types": [b.value for b in BehaviorType]
        }
