"""Simulation Data Layers - PHASE 5
Data provider for weather-fauna correlation simulations.

Version: 1.0.0
"""

import os
from typing import Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from pymongo import MongoClient
from pydantic import BaseModel, Field
import uuid


# ==============================================
# MODELS
# ==============================================

class WeatherCorrelationData(BaseModel):
    """Weather-activity correlation data point"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Species
    species: str
    
    # Weather conditions
    temperature: float
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    wind_speed: Optional[float] = None
    precipitation: Optional[float] = None
    cloud_cover: Optional[float] = None
    
    # Observed activity
    activity_level: float = Field(ge=0, le=1)
    observation_count: int = 1
    
    # Context
    season: str
    time_of_day: str
    moon_phase: Optional[str] = None
    
    # Metadata
    date: datetime
    region: Optional[str] = None
    source: str = "observation"


class CorrelationCoefficient(BaseModel):
    """Correlation coefficient between weather factor and activity"""
    species: str
    factor: str  # temperature, pressure, wind, etc.
    
    # Correlation
    coefficient: float = Field(ge=-1, le=1)
    p_value: Optional[float] = None
    sample_size: int = 0
    
    # Optimal range
    optimal_min: Optional[float] = None
    optimal_max: Optional[float] = None
    
    # Metadata
    computed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    confidence: float = Field(ge=0, le=1, default=0.7)


class SimulationHistoryData(BaseModel):
    """Historical simulation data for validation"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Simulation
    species: str
    predicted_activity: float
    actual_activity: Optional[float] = None
    
    # Conditions
    conditions: Dict[str, Any] = Field(default_factory=dict)
    
    # Accuracy
    error: Optional[float] = None
    accuracy_score: Optional[float] = None
    
    # Context
    simulation_date: datetime
    verification_date: Optional[datetime] = None
    verified: bool = False


class OptimalConditionsData(BaseModel):
    """Optimal hunting conditions data"""
    species: str
    
    # Temperature
    temp_optimal_min: float
    temp_optimal_max: float
    temp_acceptable_min: float
    temp_acceptable_max: float
    
    # Pressure
    pressure_trend: str  # rising, falling, stable
    pressure_optimal_min: Optional[float] = None
    pressure_optimal_max: Optional[float] = None
    
    # Wind
    wind_max_optimal: float
    wind_max_acceptable: float
    
    # Other
    precipitation_threshold: float = 5.0  # mm above which activity drops
    humidity_optimal_min: float = 40
    humidity_optimal_max: float = 80
    
    # Metadata
    source: str = "research"
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ==============================================
# DATA LAYER SERVICE
# ==============================================

class SimulationDataLayer:
    """Data layer for simulation data"""
    
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'test_database')
        self._client = None
        self._db = None
        
        # Default correlations
        self._correlations = {
            "deer": {
                "temperature": CorrelationCoefficient(
                    species="deer",
                    factor="temperature",
                    coefficient=0.75,
                    optimal_min=2,
                    optimal_max=15,
                    sample_size=5000,
                    confidence=0.85
                ),
                "pressure": CorrelationCoefficient(
                    species="deer",
                    factor="pressure",
                    coefficient=0.82,
                    optimal_min=1000,
                    optimal_max=1010,
                    sample_size=4500,
                    confidence=0.80
                ),
                "wind_speed": CorrelationCoefficient(
                    species="deer",
                    factor="wind_speed",
                    coefficient=-0.65,
                    optimal_min=0,
                    optimal_max=15,
                    sample_size=4800,
                    confidence=0.78
                ),
                "precipitation": CorrelationCoefficient(
                    species="deer",
                    factor="precipitation",
                    coefficient=-0.70,
                    optimal_min=0,
                    optimal_max=2,
                    sample_size=4200,
                    confidence=0.82
                )
            },
            "moose": {
                "temperature": CorrelationCoefficient(
                    species="moose",
                    factor="temperature",
                    coefficient=0.70,
                    optimal_min=-5,
                    optimal_max=10,
                    sample_size=2500,
                    confidence=0.75
                ),
                "pressure": CorrelationCoefficient(
                    species="moose",
                    factor="pressure",
                    coefficient=0.78,
                    optimal_min=1000,
                    optimal_max=1015,
                    sample_size=2200,
                    confidence=0.72
                ),
                "wind_speed": CorrelationCoefficient(
                    species="moose",
                    factor="wind_speed",
                    coefficient=-0.55,
                    optimal_min=0,
                    optimal_max=20,
                    sample_size=2300,
                    confidence=0.70
                )
            },
            "bear": {
                "temperature": CorrelationCoefficient(
                    species="bear",
                    factor="temperature",
                    coefficient=0.65,
                    optimal_min=10,
                    optimal_max=25,
                    sample_size=1800,
                    confidence=0.70
                ),
                "precipitation": CorrelationCoefficient(
                    species="bear",
                    factor="precipitation",
                    coefficient=-0.50,
                    optimal_min=0,
                    optimal_max=5,
                    sample_size=1600,
                    confidence=0.65
                )
            }
        }
        
        # Optimal conditions by species
        self._optimal_conditions = {
            "deer": OptimalConditionsData(
                species="deer",
                temp_optimal_min=2,
                temp_optimal_max=15,
                temp_acceptable_min=-10,
                temp_acceptable_max=25,
                pressure_trend="falling",
                pressure_optimal_min=1000,
                pressure_optimal_max=1015,
                wind_max_optimal=15,
                wind_max_acceptable=30
            ),
            "moose": OptimalConditionsData(
                species="moose",
                temp_optimal_min=-5,
                temp_optimal_max=10,
                temp_acceptable_min=-20,
                temp_acceptable_max=20,
                pressure_trend="falling",
                wind_max_optimal=20,
                wind_max_acceptable=40
            ),
            "bear": OptimalConditionsData(
                species="bear",
                temp_optimal_min=10,
                temp_optimal_max=25,
                temp_acceptable_min=5,
                temp_acceptable_max=30,
                pressure_trend="stable",
                wind_max_optimal=25,
                wind_max_acceptable=45
            )
        }
    
    @property
    def db(self):
        if self._db is None:
            self._client = MongoClient(self.mongo_url)
            self._db = self._client[self.db_name]
        return self._db
    
    @property
    def correlations_collection(self):
        return self.db.weather_correlations
    
    @property
    def history_collection(self):
        return self.db.simulation_history
    
    # ===========================================
    # CORRELATIONS
    # ===========================================
    
    async def get_correlation(
        self,
        species: str,
        factor: str
    ) -> Optional[CorrelationCoefficient]:
        """Get correlation coefficient for species/factor"""
        species_corr = self._correlations.get(species.lower(), {})
        return species_corr.get(factor)
    
    async def get_all_correlations(
        self,
        species: str
    ) -> Dict[str, CorrelationCoefficient]:
        """Get all correlations for a species"""
        return self._correlations.get(species.lower(), {})
    
    async def add_correlation_data(
        self,
        data: WeatherCorrelationData
    ) -> bool:
        """Add new correlation data point"""
        data_dict = data.model_dump()
        data_dict.pop("_id", None)
        self.correlations_collection.insert_one(data_dict)
        return True
    
    # ===========================================
    # OPTIMAL CONDITIONS
    # ===========================================
    
    async def get_optimal_conditions(
        self,
        species: str
    ) -> OptimalConditionsData:
        """Get optimal hunting conditions for species"""
        return self._optimal_conditions.get(
            species.lower(),
            self._optimal_conditions["deer"]
        )
    
    async def check_conditions_rating(
        self,
        species: str,
        temperature: float,
        wind_speed: float = 0,
        pressure: Optional[float] = None,
        precipitation: float = 0
    ) -> Dict[str, Any]:
        """Rate current conditions against optimal"""
        optimal = await self.get_optimal_conditions(species)
        
        ratings = {}
        
        # Temperature rating
        if optimal.temp_optimal_min <= temperature <= optimal.temp_optimal_max:
            ratings["temperature"] = {"score": 1.0, "status": "optimal"}
        elif optimal.temp_acceptable_min <= temperature <= optimal.temp_acceptable_max:
            ratings["temperature"] = {"score": 0.6, "status": "acceptable"}
        else:
            ratings["temperature"] = {"score": 0.2, "status": "poor"}
        
        # Wind rating
        if wind_speed <= optimal.wind_max_optimal:
            ratings["wind"] = {"score": 1.0, "status": "optimal"}
        elif wind_speed <= optimal.wind_max_acceptable:
            ratings["wind"] = {"score": 0.5, "status": "acceptable"}
        else:
            ratings["wind"] = {"score": 0.2, "status": "poor"}
        
        # Precipitation rating
        if precipitation <= 2:
            ratings["precipitation"] = {"score": 1.0, "status": "optimal"}
        elif precipitation <= optimal.precipitation_threshold:
            ratings["precipitation"] = {"score": 0.6, "status": "acceptable"}
        else:
            ratings["precipitation"] = {"score": 0.3, "status": "poor"}
        
        # Overall rating
        scores = [r["score"] for r in ratings.values()]
        overall = sum(scores) / len(scores)
        
        return {
            "factors": ratings,
            "overall_score": round(overall, 2),
            "recommendation": self._get_recommendation(overall)
        }
    
    def _get_recommendation(self, score: float) -> str:
        """Get hunting recommendation based on score"""
        if score >= 0.85:
            return "excellent"
        elif score >= 0.70:
            return "good"
        elif score >= 0.50:
            return "fair"
        elif score >= 0.35:
            return "poor"
        else:
            return "avoid"
    
    # ===========================================
    # SIMULATION HISTORY
    # ===========================================
    
    async def record_simulation(
        self,
        species: str,
        predicted_activity: float,
        conditions: Dict[str, Any]
    ) -> SimulationHistoryData:
        """Record a simulation for later validation"""
        history = SimulationHistoryData(
            species=species.lower(),
            predicted_activity=predicted_activity,
            conditions=conditions,
            simulation_date=datetime.now(timezone.utc)
        )
        
        history_dict = history.model_dump()
        history_dict.pop("_id", None)
        self.history_collection.insert_one(history_dict)
        
        return history
    
    async def verify_simulation(
        self,
        simulation_id: str,
        actual_activity: float
    ) -> Optional[SimulationHistoryData]:
        """Verify a past simulation with actual data"""
        simulation = self.history_collection.find_one(
            {"id": simulation_id}, {"_id": 0}
        )
        
        if not simulation:
            return None
        
        error = abs(simulation["predicted_activity"] - actual_activity)
        accuracy = 1 - min(1, error)
        
        self.history_collection.update_one(
            {"id": simulation_id},
            {"$set": {
                "actual_activity": actual_activity,
                "error": error,
                "accuracy_score": accuracy,
                "verified": True,
                "verification_date": datetime.now(timezone.utc)
            }}
        )
        
        updated = self.history_collection.find_one(
            {"id": simulation_id}, {"_id": 0}
        )
        
        return SimulationHistoryData(**updated) if updated else None
    
    async def get_simulation_accuracy(
        self,
        species: str,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """Get simulation accuracy statistics"""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)
        
        verified = list(self.history_collection.find({
            "species": species.lower(),
            "verified": True,
            "verification_date": {"$gte": cutoff}
        }, {"_id": 0}))
        
        if not verified:
            return {
                "sample_size": 0,
                "average_accuracy": None,
                "message": "Pas assez de données vérifiées"
            }
        
        accuracies = [s.get("accuracy_score", 0) for s in verified]
        
        return {
            "sample_size": len(verified),
            "average_accuracy": round(sum(accuracies) / len(accuracies), 3),
            "min_accuracy": round(min(accuracies), 3),
            "max_accuracy": round(max(accuracies), 3)
        }
    
    # ===========================================
    # WEATHER DATA INTEGRATION
    # ===========================================
    
    async def calculate_activity_impact(
        self,
        species: str,
        temperature: float,
        wind_speed: float = 0,
        pressure: Optional[float] = None,
        precipitation: float = 0
    ) -> Dict[str, Any]:
        """Calculate weather impact on activity"""
        correlations = await self.get_all_correlations(species)
        
        impacts = {}
        total_impact = 0
        weight_sum = 0
        
        # Temperature impact
        if "temperature" in correlations:
            corr = correlations["temperature"]
            if corr.optimal_min <= temperature <= corr.optimal_max:
                impact = 1.0
            else:
                distance = min(
                    abs(temperature - corr.optimal_min),
                    abs(temperature - corr.optimal_max)
                )
                impact = max(0.2, 1 - (distance / 20))
            
            impacts["temperature"] = round(impact, 2)
            total_impact += impact * abs(corr.coefficient)
            weight_sum += abs(corr.coefficient)
        
        # Wind impact
        if "wind_speed" in correlations:
            corr = correlations["wind_speed"]
            if wind_speed <= corr.optimal_max:
                impact = 1.0 - (wind_speed / corr.optimal_max) * 0.3
            else:
                impact = max(0.2, 0.7 - (wind_speed - corr.optimal_max) / 50)
            
            impacts["wind_speed"] = round(impact, 2)
            total_impact += impact * abs(corr.coefficient)
            weight_sum += abs(corr.coefficient)
        
        # Precipitation impact
        if precipitation > 0:
            impact = max(0.3, 1 - (precipitation / 20))
            impacts["precipitation"] = round(impact, 2)
            total_impact += impact * 0.7
            weight_sum += 0.7
        
        # Calculate weighted average
        overall_impact = total_impact / weight_sum if weight_sum > 0 else 0.5
        
        return {
            "species": species,
            "factor_impacts": impacts,
            "overall_activity_multiplier": round(overall_impact, 2),
            "expected_activity_level": self._get_activity_level(overall_impact)
        }
    
    def _get_activity_level(self, multiplier: float) -> str:
        """Convert multiplier to activity level"""
        if multiplier >= 0.85:
            return "very_high"
        elif multiplier >= 0.70:
            return "high"
        elif multiplier >= 0.50:
            return "moderate"
        elif multiplier >= 0.35:
            return "low"
        else:
            return "minimal"
    
    # ===========================================
    # STATS
    # ===========================================
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get data layer statistics"""
        return {
            "layer": "simulation_layers",
            "version": "1.0.0",
            "correlation_data_points": self.correlations_collection.count_documents({}),
            "simulation_history": self.history_collection.count_documents({}),
            "verified_simulations": self.history_collection.count_documents({"verified": True}),
            "supported_species": list(self._correlations.keys()),
            "correlation_factors": ["temperature", "pressure", "wind_speed", "precipitation", "humidity"],
            "status": "operational"
        }


# Singleton instance
_layer_instance = None

def get_simulation_layer() -> SimulationDataLayer:
    """Get singleton instance"""
    global _layer_instance
    if _layer_instance is None:
        _layer_instance = SimulationDataLayer()
    return _layer_instance
