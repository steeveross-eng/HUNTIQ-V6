"""Weather Fauna Simulation Engine Service - PLAN MAITRE
Business logic for weather-wildlife correlation simulation.

Version: 1.0.0
"""

import os
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from pymongo import MongoClient

from .models import (
    SimulationType, WeatherConditions, ActivityCorrelation,
    WeatherImpactResult, ActivityForecast, OptimalConditions,
    SimulationAlert, SimulationRequest
)


class WeatherFaunaSimulationService:
    """Service for weather-fauna simulation"""
    
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'test_database')
        self._client = None
        self._db = None
        
        # Optimal conditions by species
        self.optimal_conditions = {
            "deer": OptimalConditions(
                species="deer",
                optimal_temp_min=2,
                optimal_temp_max=15,
                max_wind_speed=25,
                pressure_trend="falling",
                preferred_cloud_cover="partly_cloudy",
                correlations=[
                    ActivityCorrelation(
                        factor="temperature",
                        correlation_strength=0.75,
                        optimal_range={"min": 2, "max": 15},
                        description="Activité maximale entre 2°C et 15°C"
                    ),
                    ActivityCorrelation(
                        factor="barometric_pressure",
                        correlation_strength=0.82,
                        description="Activité accrue lors de chutes de pression"
                    ),
                    ActivityCorrelation(
                        factor="wind_speed",
                        correlation_strength=-0.65,
                        optimal_range={"min": 0, "max": 25},
                        description="Activité réduite par vents forts"
                    )
                ]
            ),
            "moose": OptimalConditions(
                species="moose",
                optimal_temp_min=-5,
                optimal_temp_max=10,
                max_wind_speed=30,
                pressure_trend="falling",
                correlations=[]
            ),
            "bear": OptimalConditions(
                species="bear",
                optimal_temp_min=10,
                optimal_temp_max=25,
                max_wind_speed=35,
                pressure_trend="stable",
                correlations=[]
            )
        }
    
    @property
    def db(self):
        if self._db is None:
            self._client = MongoClient(self.mongo_url)
            self._db = self._client[self.db_name]
        return self._db
    
    @property
    def alerts_collection(self):
        return self.db.simulation_alerts
    
    async def simulate_weather_impact(
        self,
        species: str,
        conditions: WeatherConditions
    ) -> WeatherImpactResult:
        """Simulate impact of weather on wildlife activity"""
        optimal = self.optimal_conditions.get(
            species.lower(),
            OptimalConditions(
                species=species,
                optimal_temp_min=5,
                optimal_temp_max=20,
                max_wind_speed=30
            )
        )
        
        factor_impacts = {}
        positive = []
        negative = []
        
        # Temperature impact
        temp = conditions.temperature
        if optimal.optimal_temp_min <= temp <= optimal.optimal_temp_max:
            factor_impacts["temperature"] = 1.0
            positive.append("Température idéale")
        elif temp < optimal.optimal_temp_min - 10 or temp > optimal.optimal_temp_max + 10:
            factor_impacts["temperature"] = 0.4
            negative.append("Température extrême")
        else:
            factor_impacts["temperature"] = 0.7
        
        # Wind impact
        wind = conditions.wind_speed or 0
        if wind <= 10:
            factor_impacts["wind"] = 1.0
            positive.append("Vent calme")
        elif wind <= optimal.max_wind_speed:
            factor_impacts["wind"] = 0.8
        else:
            factor_impacts["wind"] = 0.5
            negative.append("Vents forts")
        
        # Pressure impact
        pressure = conditions.pressure or 1013
        if 1005 <= pressure <= 1015:
            factor_impacts["pressure"] = 0.9
        elif pressure < 1005:
            factor_impacts["pressure"] = 1.0
            positive.append("Basse pression favorable")
        else:
            factor_impacts["pressure"] = 0.7
        
        # Precipitation impact
        precip = conditions.precipitation or 0
        if precip == 0:
            factor_impacts["precipitation"] = 1.0
        elif precip < 5:
            factor_impacts["precipitation"] = 0.7
        else:
            factor_impacts["precipitation"] = 0.4
            negative.append("Précipitations importantes")
        
        # Calculate overall score
        scores = list(factor_impacts.values())
        overall = (sum(scores) / len(scores)) * 100
        multiplier = sum(scores) / len(scores)
        
        # Determine recommendation
        if overall >= 80:
            rec = "excellent"
        elif overall >= 65:
            rec = "good"
        elif overall >= 50:
            rec = "fair"
        elif overall >= 35:
            rec = "poor"
        else:
            rec = "avoid"
        
        # Find limiting factor
        limiting = min(factor_impacts, key=factor_impacts.get) if factor_impacts else None
        
        # Generate tips
        tips = []
        if rec in ["excellent", "good"]:
            tips.append("Conditions favorables - profitez-en!")
        if factor_impacts.get("wind", 1) < 0.7:
            tips.append("Chassez face au vent pour masquer votre odeur")
        if factor_impacts.get("pressure", 1) > 0.9:
            tips.append("Chute de pression détectée - activité accrue probable")
        
        return WeatherImpactResult(
            species=species,
            conditions=conditions,
            overall_impact_score=round(overall, 1),
            activity_multiplier=round(multiplier, 2),
            factor_impacts=factor_impacts,
            positive_factors=positive,
            negative_factors=negative,
            limiting_factor=limiting,
            hunting_recommendation=rec,
            tips=tips
        )
    
    async def generate_activity_forecast(
        self,
        species: str,
        lat: float,
        lng: float,
        days: int = 7
    ) -> ActivityForecast:
        """Generate multi-day activity forecast"""
        now = datetime.now(timezone.utc)
        
        daily_forecasts = []
        best_dates = []
        
        for i in range(days):
            date = now + timedelta(days=i)
            
            # Simulate weather (would use real API)
            temp = 8 + (i * 0.5) + ((hash(str(date.date())) % 10) - 5)
            wind = 10 + (hash(str(date.date())) % 20)
            
            conditions = WeatherConditions(
                temperature=temp,
                wind_speed=wind,
                pressure=1010 + (hash(str(date.date())) % 15)
            )
            
            impact = await self.simulate_weather_impact(species, conditions)
            
            forecast = {
                "date": date.date().isoformat(),
                "activity_score": impact.overall_impact_score,
                "recommendation": impact.hunting_recommendation,
                "conditions": {
                    "temperature": temp,
                    "wind_speed": wind
                }
            }
            daily_forecasts.append(forecast)
            
            if impact.overall_impact_score >= 70:
                best_dates.append(date.date().isoformat())
        
        # Best time slots
        best_slots = [
            {"time": "06:00-08:00", "score": 85, "reason": "Activité matinale maximale"},
            {"time": "17:00-19:00", "score": 80, "reason": "Activité vespérale"}
        ]
        
        return ActivityForecast(
            species=species,
            location={"lat": lat, "lng": lng},
            start_date=now,
            end_date=now + timedelta(days=days),
            daily_forecasts=daily_forecasts,
            best_dates=best_dates,
            best_time_slots=best_slots,
            forecast_confidence=0.75
        )
    
    async def get_optimal_conditions(
        self,
        species: str
    ) -> OptimalConditions:
        """Get optimal hunting conditions for a species"""
        return self.optimal_conditions.get(
            species.lower(),
            OptimalConditions(
                species=species,
                optimal_temp_min=5,
                optimal_temp_max=18,
                max_wind_speed=25
            )
        )
    
    async def create_alert(
        self,
        species: str,
        alert_type: str,
        valid_from: datetime,
        valid_until: datetime,
        title: str,
        message: str,
        conditions: Optional[WeatherConditions] = None,
        location: Optional[Dict[str, float]] = None
    ) -> SimulationAlert:
        """Create a hunting condition alert"""
        alert = SimulationAlert(
            species=species,
            alert_type=alert_type,
            valid_from=valid_from,
            valid_until=valid_until,
            title=title,
            message=message,
            conditions=conditions,
            location=location
        )
        
        alert_dict = alert.model_dump()
        alert_dict.pop("_id", None)
        self.alerts_collection.insert_one(alert_dict)
        
        return alert
    
    async def get_active_alerts(
        self,
        species: Optional[str] = None
    ) -> List[SimulationAlert]:
        """Get active alerts"""
        query = {
            "is_active": True,
            "valid_until": {"$gt": datetime.now(timezone.utc)}
        }
        
        if species:
            query["species"] = species.lower()
        
        alerts = list(self.alerts_collection.find(query, {"_id": 0}))
        return [SimulationAlert(**a) for a in alerts]
    
    async def run_simulation(
        self,
        request: SimulationRequest
    ) -> Dict[str, Any]:
        """Run a simulation based on request type"""
        if request.simulation_type == SimulationType.WEATHER_IMPACT:
            if not request.conditions:
                raise ValueError("Weather conditions required for impact simulation")
            result = await self.simulate_weather_impact(
                request.species, request.conditions
            )
            return {"type": "weather_impact", "result": result.model_dump()}
        
        elif request.simulation_type == SimulationType.ACTIVITY_FORECAST:
            if request.lat is None or request.lng is None:
                raise ValueError("Location required for forecast")
            result = await self.generate_activity_forecast(
                request.species, request.lat, request.lng, request.forecast_days
            )
            return {"type": "activity_forecast", "result": result.model_dump()}
        
        elif request.simulation_type == SimulationType.OPTIMAL_CONDITIONS:
            result = await self.get_optimal_conditions(request.species)
            return {"type": "optimal_conditions", "result": result.model_dump()}
        
        return {"error": "Unknown simulation type"}
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get simulation engine statistics"""
        return {
            "supported_species": list(self.optimal_conditions.keys()),
            "simulation_types": [t.value for t in SimulationType],
            "active_alerts": self.alerts_collection.count_documents({"is_active": True}),
            "correlation_factors": [
                "temperature", "wind_speed", "barometric_pressure",
                "precipitation", "humidity", "moon_phase"
            ]
        }
