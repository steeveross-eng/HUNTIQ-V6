"""
Analytics Engine - Service Layer
Handles business logic for hunting analytics
"""
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
import logging

from .models import (
    HuntingTrip, TripCreate, OverviewStats, SpeciesStats,
    WeatherAnalysis, TimeSlotAnalysis, MonthlyTrend, AnalyticsDashboard, TimeRange
)

logger = logging.getLogger(__name__)


def serialize_trip(doc: dict) -> dict:
    """Convert MongoDB document to serializable dict"""
    # Handle date - required field, use current time as fallback
    date_val = doc.get("date")
    if date_val:
        date_str = date_val.isoformat() if hasattr(date_val, 'isoformat') else str(date_val)
    else:
        date_str = datetime.now(timezone.utc).isoformat()
    
    # Handle created_at - optional field
    created_at = doc.get("created_at")
    created_at_str = None
    if created_at and hasattr(created_at, 'isoformat'):
        created_at_str = created_at.isoformat()
    
    return {
        "id": str(doc.get("_id", "")),
        "user_id": doc.get("user_id", ""),
        "date": date_str,
        "species": doc.get("species") or "unknown",
        "location_lat": float(doc.get("location_lat") or 0),
        "location_lng": float(doc.get("location_lng") or 0),
        "duration_hours": float(doc.get("duration_hours") or 0),
        "weather_conditions": doc.get("weather_conditions"),
        "temperature": doc.get("temperature"),
        "wind_speed": doc.get("wind_speed"),
        "moon_phase": doc.get("moon_phase"),
        "success": bool(doc.get("success", False)),
        "observations": int(doc.get("observations") or 0),
        "notes": doc.get("notes"),
        "created_at": created_at_str
    }


class AnalyticsService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.trips_collection = db['hunting_trips']
    
    async def create_trip(self, user_id: str, trip_data: TripCreate) -> dict:
        """Create a new hunting trip record"""
        now = datetime.now(timezone.utc)
        
        doc = {
            "user_id": user_id,
            "date": trip_data.date,
            "species": trip_data.species,
            "location_lat": trip_data.location_lat,
            "location_lng": trip_data.location_lng,
            "duration_hours": trip_data.duration_hours,
            "weather_conditions": trip_data.weather_conditions,
            "temperature": trip_data.temperature,
            "wind_speed": trip_data.wind_speed,
            "moon_phase": trip_data.moon_phase,
            "success": trip_data.success,
            "observations": trip_data.observations,
            "notes": trip_data.notes,
            "created_at": now
        }
        
        result = await self.trips_collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        
        logger.info(f"Created hunting trip {result.inserted_id} for user {user_id}")
        return serialize_trip(doc)
    
    async def get_trips(self, user_id: str, time_range: TimeRange = TimeRange.ALL, 
                        species: Optional[str] = None, limit: int = 100) -> List[dict]:
        """Get hunting trips with optional filters"""
        query = {"user_id": user_id}
        
        # Apply time range filter
        if time_range != TimeRange.ALL:
            now = datetime.now(timezone.utc)
            if time_range == TimeRange.WEEK:
                start_date = now - timedelta(days=7)
            elif time_range == TimeRange.MONTH:
                start_date = now - timedelta(days=30)
            elif time_range == TimeRange.SEASON:
                start_date = now - timedelta(days=90)
            elif time_range == TimeRange.YEAR:
                start_date = now - timedelta(days=365)
            query["date"] = {"$gte": start_date}
        
        if species:
            query["species"] = species
        
        cursor = self.trips_collection.find(query).sort("date", -1).limit(limit)
        trips = await cursor.to_list(length=limit)
        
        return [serialize_trip(t) for t in trips]
    
    async def delete_trip(self, user_id: str, trip_id: str) -> bool:
        """Delete a hunting trip"""
        result = await self.trips_collection.delete_one({
            "_id": ObjectId(trip_id),
            "user_id": user_id
        })
        return result.deleted_count > 0
    
    async def get_overview_stats(self, user_id: str, time_range: TimeRange = TimeRange.ALL) -> OverviewStats:
        """Get overview statistics"""
        query = {"user_id": user_id}
        
        if time_range != TimeRange.ALL:
            now = datetime.now(timezone.utc)
            days_map = {"week": 7, "month": 30, "season": 90, "year": 365}
            start_date = now - timedelta(days=days_map.get(time_range.value, 365))
            query["date"] = {"$gte": start_date}
        
        # Aggregate stats
        pipeline = [
            {"$match": query},
            {"$group": {
                "_id": None,
                "total_trips": {"$sum": 1},
                "successful_trips": {"$sum": {"$cond": ["$success", 1, 0]}},
                "total_hours": {"$sum": "$duration_hours"},
                "total_observations": {"$sum": "$observations"}
            }}
        ]
        
        result = await self.trips_collection.aggregate(pipeline).to_list(length=1)
        
        if not result:
            return OverviewStats(
                total_trips=0, successful_trips=0, success_rate=0.0,
                total_hours=0.0, total_observations=0, avg_trip_duration=0.0
            )
        
        stats = result[0]
        total = stats.get("total_trips", 0)
        successful = stats.get("successful_trips", 0)
        
        # Get most active and best success species
        species_pipeline = [
            {"$match": query},
            {"$group": {
                "_id": "$species",
                "count": {"$sum": 1},
                "successes": {"$sum": {"$cond": ["$success", 1, 0]}}
            }},
            {"$sort": {"count": -1}}
        ]
        
        species_stats = await self.trips_collection.aggregate(species_pipeline).to_list(length=10)
        
        most_active = species_stats[0]["_id"] if species_stats else None
        best_success = max(species_stats, key=lambda x: x["successes"] / max(x["count"], 1) if x["count"] > 0 else 0)["_id"] if species_stats else None
        
        return OverviewStats(
            total_trips=total,
            successful_trips=successful,
            success_rate=round((successful / total * 100) if total > 0 else 0, 1),
            total_hours=round(stats.get("total_hours", 0), 1),
            total_observations=stats.get("total_observations", 0),
            avg_trip_duration=round(stats.get("total_hours", 0) / max(total, 1), 1),
            most_active_species=most_active,
            best_success_species=best_success
        )
    
    async def get_species_breakdown(self, user_id: str, time_range: TimeRange = TimeRange.ALL) -> List[SpeciesStats]:
        """Get statistics broken down by species"""
        query = {"user_id": user_id}
        
        if time_range != TimeRange.ALL:
            now = datetime.now(timezone.utc)
            days_map = {"week": 7, "month": 30, "season": 90, "year": 365}
            start_date = now - timedelta(days=days_map.get(time_range.value, 365))
            query["date"] = {"$gte": start_date}
        
        pipeline = [
            {"$match": query},
            {"$group": {
                "_id": "$species",
                "trips": {"$sum": 1},
                "successes": {"$sum": {"$cond": ["$success", 1, 0]}},
                "total_observations": {"$sum": "$observations"},
                "total_duration": {"$sum": "$duration_hours"}
            }},
            {"$sort": {"trips": -1}}
        ]
        
        results = await self.trips_collection.aggregate(pipeline).to_list(length=20)
        
        # Filter out entries with None species
        return [
            SpeciesStats(
                species=r["_id"] or "unknown",
                trips=r["trips"],
                successes=r["successes"],
                success_rate=round((r["successes"] / r["trips"] * 100) if r["trips"] > 0 else 0, 1),
                total_observations=r["total_observations"],
                avg_duration=round(r["total_duration"] / max(r["trips"], 1), 1)
            )
            for r in results
            if r["_id"] is not None  # Skip entries without species
        ]
    
    async def get_weather_analysis(self, user_id: str) -> List[WeatherAnalysis]:
        """Analyze success rates by weather conditions"""
        pipeline = [
            {"$match": {"user_id": user_id, "weather_conditions": {"$ne": None}}},
            {"$group": {
                "_id": "$weather_conditions",
                "trips": {"$sum": 1},
                "successes": {"$sum": {"$cond": ["$success", 1, 0]}},
                "total_observations": {"$sum": "$observations"}
            }},
            {"$sort": {"trips": -1}}
        ]
        
        results = await self.trips_collection.aggregate(pipeline).to_list(length=10)
        
        return [
            WeatherAnalysis(
                condition=r["_id"],
                trips=r["trips"],
                success_rate=round((r["successes"] / r["trips"] * 100) if r["trips"] > 0 else 0, 1),
                avg_observations=round(r["total_observations"] / max(r["trips"], 1), 1)
            )
            for r in results
        ]
    
    async def get_optimal_times(self, user_id: str) -> List[TimeSlotAnalysis]:
        """Analyze optimal hunting times"""
        pipeline = [
            {"$match": {"user_id": user_id, "date": {"$ne": None}}},
            {"$project": {
                "hour": {"$hour": "$date"},
                "success": 1,
                "observations": 1
            }},
            {"$group": {
                "_id": "$hour",
                "trips": {"$sum": 1},
                "successes": {"$sum": {"$cond": ["$success", 1, 0]}},
                "total_observations": {"$sum": "$observations"}
            }},
            {"$sort": {"_id": 1}}
        ]
        
        results = await self.trips_collection.aggregate(pipeline).to_list(length=24)
        
        # Create labels for time slots
        def get_label(hour: int) -> str:
            if hour is None:
                return "Inconnu"
            if 5 <= hour < 8:
                return "Aube"
            elif 8 <= hour < 12:
                return "Matin"
            elif 12 <= hour < 14:
                return "Midi"
            elif 14 <= hour < 17:
                return "Après-midi"
            elif 17 <= hour < 20:
                return "Crépuscule"
            else:
                return "Nuit"
        
        # Filter out results with None _id (no date)
        return [
            TimeSlotAnalysis(
                hour=r["_id"] if r["_id"] is not None else 0,
                label=get_label(r["_id"]),
                trips=r["trips"],
                success_rate=round((r["successes"] / r["trips"] * 100) if r["trips"] > 0 else 0, 1),
                activity_score=round(r["total_observations"] / max(r["trips"], 1) * 10, 1)
            )
            for r in results
            if r["_id"] is not None
        ]
    
    async def get_monthly_trends(self, user_id: str, months: int = 12) -> List[MonthlyTrend]:
        """Get monthly hunting trends"""
        start_date = datetime.now(timezone.utc) - timedelta(days=months * 30)
        
        pipeline = [
            {"$match": {"user_id": user_id, "date": {"$gte": start_date}}},
            {"$project": {
                "month": {"$month": "$date"},
                "year": {"$year": "$date"},
                "success": 1,
                "observations": 1
            }},
            {"$group": {
                "_id": {"month": "$month", "year": "$year"},
                "trips": {"$sum": 1},
                "successes": {"$sum": {"$cond": ["$success", 1, 0]}},
                "observations": {"$sum": "$observations"}
            }},
            {"$sort": {"_id.year": 1, "_id.month": 1}}
        ]
        
        results = await self.trips_collection.aggregate(pipeline).to_list(length=months)
        
        month_names = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", 
                       "Juil", "Août", "Sep", "Oct", "Nov", "Déc"]
        
        return [
            MonthlyTrend(
                month=month_names[r["_id"]["month"] - 1],
                year=r["_id"]["year"],
                trips=r["trips"],
                successes=r["successes"],
                success_rate=round((r["successes"] / r["trips"] * 100) if r["trips"] > 0 else 0, 1),
                observations=r["observations"]
            )
            for r in results
        ]
    
    async def get_full_dashboard(self, user_id: str, time_range: TimeRange = TimeRange.ALL) -> AnalyticsDashboard:
        """Get complete analytics dashboard data"""
        overview = await self.get_overview_stats(user_id, time_range)
        species = await self.get_species_breakdown(user_id, time_range)
        weather = await self.get_weather_analysis(user_id)
        times = await self.get_optimal_times(user_id)
        trends = await self.get_monthly_trends(user_id)
        trips = await self.get_trips(user_id, time_range, limit=10)
        
        return AnalyticsDashboard(
            overview=overview,
            species_breakdown=species,
            weather_analysis=weather,
            optimal_times=times,
            monthly_trends=trends,
            recent_trips=[HuntingTrip(**t) for t in trips]
        )
    
    async def seed_demo_data(self, user_id: str) -> int:
        """Seed demo data for analytics testing"""
        import random
        
        species_list = ["deer", "moose", "bear", "wild_turkey", "duck"]
        weather_list = ["Ensoleillé", "Nuageux", "Pluvieux", "Brumeux", "Neigeux"]
        moon_phases = ["Nouvelle lune", "Premier quartier", "Pleine lune", "Dernier quartier"]
        
        trips = []
        now = datetime.now(timezone.utc)
        
        for i in range(50):
            days_ago = random.randint(1, 365)
            hour = random.choice([5, 6, 7, 16, 17, 18])  # Peak hunting hours
            
            trip_date = now - timedelta(days=days_ago, hours=random.randint(0, 12))
            trip_date = trip_date.replace(hour=hour)
            
            species = random.choice(species_list)
            weather = random.choice(weather_list)
            
            # Success more likely in good weather and optimal times
            base_success_chance = 0.3
            if weather in ["Ensoleillé", "Nuageux"]:
                base_success_chance += 0.1
            if hour in [6, 7, 17]:
                base_success_chance += 0.15
            
            success = random.random() < base_success_chance
            
            trips.append({
                "user_id": user_id,
                "date": trip_date,
                "species": species,
                "location_lat": 46.8139 + random.uniform(-0.5, 0.5),
                "location_lng": -71.208 + random.uniform(-0.5, 0.5),
                "duration_hours": round(random.uniform(2, 8), 1),
                "weather_conditions": weather,
                "temperature": round(random.uniform(-10, 25), 1),
                "wind_speed": round(random.uniform(0, 30), 1),
                "moon_phase": random.choice(moon_phases),
                "success": success,
                "observations": random.randint(0, 10) if not success else random.randint(1, 15),
                "notes": f"Sortie de test #{i+1}",
                "created_at": now
            })
        
        if trips:
            result = await self.trips_collection.insert_many(trips)
            logger.info(f"Seeded {len(result.inserted_ids)} demo trips for user {user_id}")
            return len(result.inserted_ids)
        
        return 0
