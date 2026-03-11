"""Behavioral Data Layers - PHASE 5
Data provider for wildlife behavior patterns and observations.

Version: 1.0.0
"""

import os
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from pymongo import MongoClient
from pydantic import BaseModel, Field
from enum import Enum
import uuid


# ==============================================
# MODELS
# ==============================================

class ActivityType(str, Enum):
    """Wildlife activity types"""
    FEEDING = "feeding"
    RESTING = "resting"
    TRAVELING = "traveling"
    RUTTING = "rutting"
    NURSING = "nursing"


class ObservationData(BaseModel):
    """Wildlife observation record"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Location
    coordinates: Dict[str, float]
    location_accuracy_m: Optional[float] = None
    
    # Observation
    species: str
    count: int = 1
    activity: Optional[ActivityType] = None
    behavior_notes: Optional[str] = None
    
    # Timing
    observed_at: datetime
    time_of_day: str  # dawn, morning, midday, afternoon, dusk, night
    moon_phase: Optional[str] = None
    
    # Weather at time
    temperature: Optional[float] = None
    wind_speed: Optional[float] = None
    precipitation: Optional[str] = None
    
    # Observer
    observer_id: Optional[str] = None
    observation_type: str = "visual"  # visual, trail_cam, tracks, sign
    
    # Validation
    verified: bool = False
    confidence: float = Field(ge=0, le=1, default=0.7)
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MovementData(BaseModel):
    """Wildlife movement tracking data"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Animal
    species: str
    individual_id: Optional[str] = None  # If tracking specific animal
    
    # Path
    path_points: List[Dict[str, Any]] = Field(default_factory=list)
    # Each point: {lat, lng, timestamp, speed_kmh, heading}
    
    # Stats
    total_distance_km: float = 0
    duration_hours: float = 0
    average_speed_kmh: float = 0
    max_speed_kmh: float = 0
    
    # Context
    start_time: datetime
    end_time: datetime
    period_type: str = "daily"  # daily, weekly, seasonal
    
    # Metadata
    data_source: str = "telemetry"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ActivityPatternData(BaseModel):
    """Aggregated activity pattern data"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Target
    species: str
    region: Optional[str] = None
    
    # Pattern
    pattern_type: str  # hourly, daily, seasonal
    
    # Hourly distribution (0-23)
    hourly_activity: Dict[str, float] = Field(default_factory=dict)
    # e.g., {"5": 0.8, "6": 0.95, "7": 0.7, ...}
    
    # Peak times
    peak_hours: List[int] = Field(default_factory=list)
    low_hours: List[int] = Field(default_factory=list)
    
    # Sample info
    observation_count: int = 0
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    
    # Confidence
    confidence: float = Field(ge=0, le=1, default=0.7)
    
    # Metadata
    computed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SeasonalPatternData(BaseModel):
    """Seasonal behavior pattern data"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Target
    species: str
    season: str  # pre_rut, rut, post_rut, winter, spring, summer, early_fall
    
    # Activity modifiers
    activity_multiplier: float = 1.0
    movement_multiplier: float = 1.0
    
    # Behavior shifts
    primary_activities: List[str] = Field(default_factory=list)
    habitat_preferences: List[str] = Field(default_factory=list)
    food_preferences: List[str] = Field(default_factory=list)
    
    # Timing shifts
    activity_shift_hours: float = 0  # Earlier/later than baseline
    
    # Social behavior
    group_size_avg: float = 1.0
    territorial_level: str = "medium"  # low, medium, high
    
    # Special events
    events: List[str] = Field(default_factory=list)
    
    # Metadata
    data_source: str = "research"
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ==============================================
# DATA LAYER SERVICE
# ==============================================

class BehavioralDataLayer:
    """Data layer for wildlife behavior information"""
    
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'test_database')
        self._client = None
        self._db = None
        
        # Default activity patterns by species
        self._default_patterns = {
            "deer": {
                "hourly": {
                    "5": 0.85, "6": 0.95, "7": 0.80, "8": 0.50,
                    "9": 0.30, "10": 0.20, "11": 0.15, "12": 0.15,
                    "13": 0.20, "14": 0.25, "15": 0.35, "16": 0.60,
                    "17": 0.85, "18": 0.95, "19": 0.75, "20": 0.50,
                    "21": 0.35, "22": 0.25, "23": 0.20, "0": 0.15,
                    "1": 0.10, "2": 0.10, "3": 0.15, "4": 0.40
                },
                "peak_hours": [6, 17, 18],
                "low_hours": [11, 12, 1, 2]
            },
            "moose": {
                "hourly": {
                    "5": 0.80, "6": 0.90, "7": 0.85, "8": 0.60,
                    "9": 0.40, "10": 0.25, "11": 0.20, "12": 0.20,
                    "13": 0.25, "14": 0.30, "15": 0.45, "16": 0.70,
                    "17": 0.90, "18": 0.85, "19": 0.70, "20": 0.55,
                    "21": 0.40, "22": 0.30, "23": 0.25, "0": 0.20,
                    "1": 0.15, "2": 0.15, "3": 0.20, "4": 0.50
                },
                "peak_hours": [6, 7, 17],
                "low_hours": [11, 12, 0, 1]
            },
            "bear": {
                "hourly": {
                    "5": 0.60, "6": 0.75, "7": 0.85, "8": 0.80,
                    "9": 0.65, "10": 0.50, "11": 0.40, "12": 0.35,
                    "13": 0.40, "14": 0.50, "15": 0.65, "16": 0.80,
                    "17": 0.90, "18": 0.85, "19": 0.75, "20": 0.60,
                    "21": 0.45, "22": 0.30, "23": 0.20, "0": 0.15,
                    "1": 0.10, "2": 0.10, "3": 0.15, "4": 0.30
                },
                "peak_hours": [7, 8, 17, 18],
                "low_hours": [0, 1, 2, 3]
            }
        }
        
        # Seasonal patterns
        self._seasonal_patterns = {
            "deer": {
                "pre_rut": {
                    "activity_multiplier": 1.2,
                    "movement_multiplier": 1.3,
                    "primary_activities": ["feeding", "territorial"],
                    "events": ["scrape_making", "rub_activity"]
                },
                "rut": {
                    "activity_multiplier": 1.5,
                    "movement_multiplier": 2.0,
                    "primary_activities": ["rutting", "traveling"],
                    "events": ["peak_breeding", "chasing"]
                },
                "post_rut": {
                    "activity_multiplier": 0.8,
                    "movement_multiplier": 0.7,
                    "primary_activities": ["feeding", "resting"],
                    "events": ["recovery_feeding"]
                }
            }
        }
    
    @property
    def db(self):
        if self._db is None:
            self._client = MongoClient(self.mongo_url)
            self._db = self._client[self.db_name]
        return self._db
    
    @property
    def observations_collection(self):
        return self.db.wildlife_observations
    
    @property
    def movements_collection(self):
        return self.db.wildlife_movements
    
    @property
    def patterns_collection(self):
        return self.db.activity_patterns
    
    # ===========================================
    # OBSERVATIONS
    # ===========================================
    
    async def record_observation(
        self,
        observation: ObservationData
    ) -> ObservationData:
        """Record a new wildlife observation"""
        obs_dict = observation.model_dump()
        obs_dict.pop("_id", None)
        self.observations_collection.insert_one(obs_dict)
        return observation
    
    async def get_observations_in_area(
        self,
        lat: float,
        lng: float,
        radius_km: float = 5.0,
        species: Optional[str] = None,
        days_back: int = 365
    ) -> List[ObservationData]:
        """Get observations in area"""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)
        
        query = {
            "observed_at": {"$gte": cutoff}
        }
        
        if species:
            query["species"] = species.lower()
        
        observations = list(self.observations_collection.find(
            query, {"_id": 0}
        ).limit(500))
        
        if observations:
            return [ObservationData(**o) for o in observations]
        
        # Generate placeholder data
        return self._generate_placeholder_observations(lat, lng, species, days_back)
    
    async def get_observations_by_species(
        self,
        species: str,
        limit: int = 100
    ) -> List[ObservationData]:
        """Get recent observations for a species"""
        observations = list(self.observations_collection.find(
            {"species": species.lower()},
            {"_id": 0}
        ).sort("observed_at", -1).limit(limit))
        
        return [ObservationData(**o) for o in observations]
    
    # ===========================================
    # ACTIVITY PATTERNS
    # ===========================================
    
    async def get_activity_pattern(
        self,
        species: str,
        region: Optional[str] = None
    ) -> ActivityPatternData:
        """Get activity pattern for species"""
        # Check for cached pattern
        query = {"species": species.lower()}
        if region:
            query["region"] = region
        
        pattern = self.patterns_collection.find_one(query, {"_id": 0})
        
        if pattern:
            return ActivityPatternData(**pattern)
        
        # Return default pattern
        default = self._default_patterns.get(species.lower(), self._default_patterns["deer"])
        
        return ActivityPatternData(
            species=species.lower(),
            region=region,
            pattern_type="hourly",
            hourly_activity=default["hourly"],
            peak_hours=default["peak_hours"],
            low_hours=default["low_hours"],
            confidence=0.75
        )
    
    async def get_activity_at_hour(
        self,
        species: str,
        hour: int
    ) -> float:
        """Get activity level at specific hour"""
        pattern = await self.get_activity_pattern(species)
        return pattern.hourly_activity.get(str(hour), 0.5)
    
    # ===========================================
    # SEASONAL PATTERNS
    # ===========================================
    
    async def get_seasonal_pattern(
        self,
        species: str,
        season: str
    ) -> SeasonalPatternData:
        """Get seasonal behavior pattern"""
        species_patterns = self._seasonal_patterns.get(
            species.lower(),
            {}
        )
        
        season_data = species_patterns.get(season, {
            "activity_multiplier": 1.0,
            "movement_multiplier": 1.0,
            "primary_activities": ["feeding"],
            "events": []
        })
        
        return SeasonalPatternData(
            species=species.lower(),
            season=season,
            **season_data
        )
    
    async def get_current_season(self, species: str) -> str:
        """Determine current season for species"""
        month = datetime.now().month
        
        if species.lower() == "deer":
            if month == 10:
                return "pre_rut"
            elif month == 11:
                return "rut"
            elif month == 12:
                return "post_rut"
            elif month in [1, 2]:
                return "winter"
            elif month in [3, 4, 5]:
                return "spring"
            elif month in [6, 7, 8]:
                return "summer"
            else:
                return "early_fall"
        
        # Default seasons
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "fall"
    
    # ===========================================
    # MOVEMENT DATA
    # ===========================================
    
    async def get_movement_data(
        self,
        species: str,
        period_type: str = "daily"
    ) -> List[MovementData]:
        """Get movement tracking data"""
        movements = list(self.movements_collection.find(
            {"species": species.lower(), "period_type": period_type},
            {"_id": 0}
        ).limit(50))
        
        if movements:
            return [MovementData(**m) for m in movements]
        
        # Return placeholder
        return self._generate_placeholder_movements(species, period_type)
    
    async def get_average_daily_movement(self, species: str) -> Dict[str, float]:
        """Get average daily movement stats"""
        movement_rates = {
            "deer": {"distance_km": 3.0, "home_range_km2": 2.5},
            "moose": {"distance_km": 5.0, "home_range_km2": 25.0},
            "bear": {"distance_km": 8.0, "home_range_km2": 50.0}
        }
        
        return movement_rates.get(species.lower(), {"distance_km": 3.0, "home_range_km2": 5.0})
    
    # ===========================================
    # PLACEHOLDER GENERATORS
    # ===========================================
    
    def _generate_placeholder_observations(
        self,
        lat: float,
        lng: float,
        species: Optional[str],
        days_back: int
    ) -> List[ObservationData]:
        """Generate placeholder observations"""
        import random
        
        observations = []
        species_list = [species] if species else ["deer", "moose", "bear"]
        activities = list(ActivityType)
        times_of_day = ["dawn", "morning", "midday", "afternoon", "dusk", "night"]
        
        for i in range(random.randint(10, 30)):
            obs_date = datetime.now(timezone.utc) - timedelta(
                days=random.randint(0, days_back)
            )
            
            observations.append(ObservationData(
                coordinates={
                    "lat": lat + (random.random() - 0.5) * 0.1,
                    "lng": lng + (random.random() - 0.5) * 0.1
                },
                species=random.choice(species_list),
                count=random.randint(1, 5),
                activity=random.choice(activities),
                observed_at=obs_date,
                time_of_day=random.choice(times_of_day),
                observation_type=random.choice(["visual", "trail_cam", "tracks"]),
                confidence=random.uniform(0.6, 0.95)
            ))
        
        return observations
    
    def _generate_placeholder_movements(
        self,
        species: str,
        period_type: str
    ) -> List[MovementData]:
        """Generate placeholder movement data"""
        import random
        
        movements = []
        
        for i in range(5):
            path_points = []
            base_lat = 46.5 + random.random() * 0.5
            base_lng = -72.5 + random.random() * 0.5
            
            for j in range(24):  # 24 hours
                path_points.append({
                    "lat": base_lat + random.random() * 0.02,
                    "lng": base_lng + random.random() * 0.02,
                    "timestamp": (datetime.now(timezone.utc) - timedelta(hours=24-j)).isoformat(),
                    "speed_kmh": random.uniform(0, 5)
                })
            
            movements.append(MovementData(
                species=species.lower(),
                path_points=path_points,
                total_distance_km=random.uniform(2, 8),
                duration_hours=24,
                average_speed_kmh=random.uniform(0.1, 0.5),
                max_speed_kmh=random.uniform(3, 8),
                start_time=datetime.now(timezone.utc) - timedelta(hours=24),
                end_time=datetime.now(timezone.utc),
                period_type=period_type
            ))
        
        return movements
    
    # ===========================================
    # STATS
    # ===========================================
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get data layer statistics"""
        return {
            "layer": "behavioral_layers",
            "version": "1.0.0",
            "cached_observations": self.observations_collection.count_documents({}),
            "cached_movements": self.movements_collection.count_documents({}),
            "cached_patterns": self.patterns_collection.count_documents({}),
            "supported_species": ["deer", "moose", "bear"],
            "pattern_types": ["hourly", "daily", "seasonal"],
            "status": "operational"
        }


# Singleton instance
_layer_instance = None

def get_behavioral_layer() -> BehavioralDataLayer:
    """Get singleton instance"""
    global _layer_instance
    if _layer_instance is None:
        _layer_instance = BehavioralDataLayer()
    return _layer_instance
