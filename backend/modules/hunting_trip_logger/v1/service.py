"""
Hunting Trip Logger - Service Layer
Real data logging for hunting trips, waypoint visits, and observations
Feeds data to analytics_engine, waypoint_scoring_engine, and geolocation_engine
"""
import uuid
import logging
from datetime import datetime, timezone
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from .models import (
    TripCreate, TripStart, TripEnd, HuntingTrip, TripStatus,
    WaypointVisitCreate, WaypointVisit,
    ObservationCreate, Observation, ObservationType,
    TripStatistics, WaypointStatistics
)

# Import email service for trip completion notifications
from modules.auth_engine.v1.email_service import EmailService

logger = logging.getLogger(__name__)


class HuntingTripLoggerService:
    """Service for logging hunting trips, visits, and observations"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.trips_collection = db['hunting_trips']
        self.visits_collection = db['waypoint_visits']
        self.observations_collection = db['hunting_observations']
        self.waypoints_collection = db['user_waypoints']
        self.users_collection = db['users']
        # Analytics collections
        self.analytics_trips_collection = db['analytics_trips']
        # Email service
        self.email_service = EmailService(db)
    
    def _generate_id(self, prefix: str = "trip") -> str:
        """Generate a unique ID"""
        return f"{prefix}_{uuid.uuid4().hex[:12]}"
    
    # ============================================
    # HUNTING TRIPS
    # ============================================
    
    async def create_trip(self, user_id: str, trip_data: TripCreate) -> HuntingTrip:
        """Create a new hunting trip"""
        now = datetime.now(timezone.utc)
        trip_id = self._generate_id("trip")
        
        trip_doc = {
            "trip_id": trip_id,
            "user_id": user_id,
            "title": trip_data.title or f"Sortie {trip_data.target_species}",
            "target_species": trip_data.target_species,
            "status": TripStatus.PLANNED.value,
            "planned_date": trip_data.planned_date,
            "start_time": None,
            "end_time": None,
            "duration_hours": None,
            "weather": None,
            "temperature": None,
            "wind_speed": None,
            "success": False,
            "planned_waypoints": trip_data.planned_waypoints,
            "visited_waypoints": [],
            "observations_count": 0,
            "notes": trip_data.notes,
            "created_at": now,
            "updated_at": None
        }
        
        await self.trips_collection.insert_one(trip_doc)
        logger.info(f"Created trip {trip_id} for user {user_id}")
        
        return HuntingTrip(**trip_doc)
    
    async def start_trip(self, user_id: str, start_data: TripStart) -> Optional[HuntingTrip]:
        """Start a hunting trip"""
        trip = await self.trips_collection.find_one({
            "trip_id": start_data.trip_id,
            "user_id": user_id
        })
        
        if not trip:
            return None
        
        now = datetime.now(timezone.utc)
        update_data = {
            "status": TripStatus.IN_PROGRESS.value,
            "start_time": now,
            "updated_at": now
        }
        
        if start_data.actual_weather:
            update_data["weather"] = start_data.actual_weather.value
        if start_data.temperature is not None:
            update_data["temperature"] = start_data.temperature
        if start_data.wind_speed is not None:
            update_data["wind_speed"] = start_data.wind_speed
        
        await self.trips_collection.update_one(
            {"trip_id": start_data.trip_id},
            {"$set": update_data}
        )
        
        # Get updated trip
        updated_trip = await self.trips_collection.find_one(
            {"trip_id": start_data.trip_id},
            {"_id": 0}
        )
        
        logger.info(f"Started trip {start_data.trip_id}")
        return HuntingTrip(**updated_trip)
    
    async def end_trip(self, user_id: str, end_data: TripEnd) -> Optional[HuntingTrip]:
        """End a hunting trip and sync to analytics"""
        trip = await self.trips_collection.find_one({
            "trip_id": end_data.trip_id,
            "user_id": user_id
        })
        
        if not trip:
            return None
        
        now = datetime.now(timezone.utc)
        start_time = trip.get("start_time")
        duration_hours = 0
        
        if start_time:
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            # Ensure start_time is timezone-aware
            if start_time.tzinfo is None:
                start_time = start_time.replace(tzinfo=timezone.utc)
            duration = now - start_time
            duration_hours = round(duration.total_seconds() / 3600, 2)
        
        # Count observations for this trip
        obs_count = await self.observations_collection.count_documents({
            "trip_id": end_data.trip_id
        })
        
        update_data = {
            "status": TripStatus.COMPLETED.value,
            "end_time": now,
            "duration_hours": duration_hours,
            "success": end_data.success,
            "observations_count": obs_count,
            "updated_at": now
        }
        
        if end_data.notes:
            update_data["notes"] = end_data.notes
        
        await self.trips_collection.update_one(
            {"trip_id": end_data.trip_id},
            {"$set": update_data}
        )
        
        # Get updated trip
        updated_trip = await self.trips_collection.find_one(
            {"trip_id": end_data.trip_id},
            {"_id": 0}
        )
        
        # Sync to analytics_engine
        await self._sync_trip_to_analytics(updated_trip)
        
        # Update waypoint scoring data
        await self._update_waypoint_scores(user_id, updated_trip)
        
        # Send trip summary email (non-blocking)
        await self._send_trip_summary_email(user_id, updated_trip)
        
        logger.info(f"Ended trip {end_data.trip_id} - Success: {end_data.success}, Duration: {duration_hours}h")
        return HuntingTrip(**updated_trip)
    
    async def get_trip(self, user_id: str, trip_id: str) -> Optional[HuntingTrip]:
        """Get a specific trip"""
        trip = await self.trips_collection.find_one(
            {"trip_id": trip_id, "user_id": user_id},
            {"_id": 0}
        )
        if trip:
            return HuntingTrip(**trip)
        return None
    
    async def get_user_trips(
        self, 
        user_id: str, 
        status: Optional[TripStatus] = None,
        limit: int = 50
    ) -> List[HuntingTrip]:
        """Get all trips for a user"""
        # Only query trips with new schema (trip_id field exists)
        query = {"user_id": user_id, "trip_id": {"$exists": True}}
        if status:
            query["status"] = status.value
        
        cursor = self.trips_collection.find(query, {"_id": 0}).sort("created_at", -1).limit(limit)
        trips = await cursor.to_list(length=limit)
        return [HuntingTrip(**t) for t in trips]
    
    async def get_active_trip(self, user_id: str) -> Optional[HuntingTrip]:
        """Get the currently active trip for a user"""
        trip = await self.trips_collection.find_one(
            {"user_id": user_id, "status": TripStatus.IN_PROGRESS.value},
            {"_id": 0}
        )
        if trip:
            return HuntingTrip(**trip)
        return None
    
    async def _send_trip_summary_email(self, user_id: str, trip: dict) -> None:
        """Send trip completion summary email to user (non-blocking)"""
        try:
            # Get user info
            user = await self.users_collection.find_one(
                {"user_id": user_id},
                {"_id": 0, "email": 1, "name": 1}
            )
            
            if not user or not user.get("email"):
                logger.warning(f"Cannot send trip email: user {user_id} not found or no email")
                return
            
            # Format times
            start_time = trip.get("start_time")
            end_time = trip.get("end_time")
            
            def format_datetime(dt):
                if dt is None:
                    return "N/A"
                if isinstance(dt, str):
                    dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
                return dt.strftime("%d/%m/%Y %H:%M")
            
            start_str = format_datetime(start_time)
            end_str = format_datetime(end_time)
            
            # Send email
            success, result = await self.email_service.send_trip_summary_email(
                email=user["email"],
                user_name=user.get("name", "Chasseur"),
                trip_title=trip.get("title", "Sortie de chasse"),
                target_species=trip.get("target_species", "unknown"),
                duration_hours=trip.get("duration_hours", 0),
                observations_count=trip.get("observations_count", 0),
                success=trip.get("success", False),
                start_time=start_str,
                end_time=end_str,
                weather=trip.get("actual_weather"),
                notes=trip.get("notes")
            )
            
            if success:
                logger.info(f"Trip summary email sent to {user['email']} for trip {trip.get('trip_id')}")
            else:
                logger.warning(f"Failed to send trip summary email: {result}")
                
        except Exception as e:
            logger.error(f"Error sending trip summary email: {e}")
            # Don't raise - email failure should not affect trip ending
    
    # ============================================
    # WAYPOINT VISITS
    # ============================================
    
    async def log_waypoint_visit(
        self, 
        user_id: str, 
        visit_data: WaypointVisitCreate
    ) -> WaypointVisit:
        """Log a visit to a waypoint"""
        now = datetime.now(timezone.utc)
        visit_id = self._generate_id("visit")
        
        # Get waypoint name
        waypoint = await self.waypoints_collection.find_one(
            {"_id": ObjectId(visit_data.waypoint_id)} if len(visit_data.waypoint_id) == 24 
            else {"waypoint_id": visit_data.waypoint_id}
        )
        waypoint_name = waypoint.get("name", "Unknown") if waypoint else "Unknown"
        
        arrival_time = visit_data.arrival_time or now
        
        visit_doc = {
            "visit_id": visit_id,
            "user_id": user_id,
            "waypoint_id": visit_data.waypoint_id,
            "waypoint_name": waypoint_name,
            "trip_id": visit_data.trip_id,
            "arrival_time": arrival_time,
            "departure_time": visit_data.departure_time,
            "duration_minutes": None,
            "weather": visit_data.weather.value if visit_data.weather else None,
            "activity_level": visit_data.activity_level,
            "success": False,
            "observations_count": 0,
            "notes": visit_data.notes,
            "created_at": now
        }
        
        # Calculate duration if departure time provided
        if visit_data.departure_time:
            duration = visit_data.departure_time - arrival_time
            visit_doc["duration_minutes"] = round(duration.total_seconds() / 60, 1)
        
        await self.visits_collection.insert_one(visit_doc)
        
        # Update trip's visited waypoints
        if visit_data.trip_id:
            await self.trips_collection.update_one(
                {"trip_id": visit_data.trip_id},
                {"$addToSet": {"visited_waypoints": visit_data.waypoint_id}}
            )
        
        logger.info(f"Logged visit {visit_id} to waypoint {visit_data.waypoint_id}")
        return WaypointVisit(**visit_doc)
    
    async def end_waypoint_visit(
        self, 
        user_id: str, 
        visit_id: str,
        success: bool = False,
        notes: Optional[str] = None
    ) -> Optional[WaypointVisit]:
        """End a waypoint visit"""
        visit = await self.visits_collection.find_one({
            "visit_id": visit_id,
            "user_id": user_id
        })
        
        if not visit:
            return None
        
        now = datetime.now(timezone.utc)
        arrival_time = visit.get("arrival_time")
        duration_minutes = None
        
        if arrival_time:
            if isinstance(arrival_time, str):
                arrival_time = datetime.fromisoformat(arrival_time.replace('Z', '+00:00'))
            duration = now - arrival_time
            duration_minutes = round(duration.total_seconds() / 60, 1)
        
        # Count observations for this visit
        obs_count = await self.observations_collection.count_documents({
            "visit_id": visit_id
        })
        
        update_data = {
            "departure_time": now,
            "duration_minutes": duration_minutes,
            "success": success,
            "observations_count": obs_count
        }
        
        if notes:
            update_data["notes"] = notes
        
        await self.visits_collection.update_one(
            {"visit_id": visit_id},
            {"$set": update_data}
        )
        
        updated_visit = await self.visits_collection.find_one(
            {"visit_id": visit_id},
            {"_id": 0}
        )
        
        logger.info(f"Ended visit {visit_id} - Success: {success}")
        return WaypointVisit(**updated_visit)
    
    async def get_waypoint_visits(
        self, 
        user_id: str, 
        waypoint_id: Optional[str] = None,
        limit: int = 50
    ) -> List[WaypointVisit]:
        """Get waypoint visits"""
        query = {"user_id": user_id}
        if waypoint_id:
            query["waypoint_id"] = waypoint_id
        
        cursor = self.visits_collection.find(query, {"_id": 0}).sort("arrival_time", -1).limit(limit)
        visits = await cursor.to_list(length=limit)
        return [WaypointVisit(**v) for v in visits]
    
    # ============================================
    # OBSERVATIONS
    # ============================================
    
    async def log_observation(
        self, 
        user_id: str, 
        obs_data: ObservationCreate
    ) -> Observation:
        """Log an observation during a trip"""
        now = datetime.now(timezone.utc)
        obs_id = self._generate_id("obs")
        
        obs_doc = {
            "observation_id": obs_id,
            "user_id": user_id,
            "trip_id": obs_data.trip_id,
            "waypoint_id": obs_data.waypoint_id,
            "observation_type": obs_data.observation_type.value,
            "species": obs_data.species,
            "count": obs_data.count,
            "distance_meters": obs_data.distance_meters,
            "direction": obs_data.direction,
            "behavior": obs_data.behavior,
            "location_lat": obs_data.location_lat,
            "location_lng": obs_data.location_lng,
            "notes": obs_data.notes,
            "photo_url": obs_data.photo_url,
            "timestamp": now,
            "created_at": now
        }
        
        await self.observations_collection.insert_one(obs_doc)
        
        # Update trip observations count
        if obs_data.trip_id:
            await self.trips_collection.update_one(
                {"trip_id": obs_data.trip_id},
                {"$inc": {"observations_count": 1}}
            )
        
        # If it's a harvest, mark trip and visit as successful
        if obs_data.observation_type == ObservationType.HARVEST:
            if obs_data.trip_id:
                await self.trips_collection.update_one(
                    {"trip_id": obs_data.trip_id},
                    {"$set": {"success": True}}
                )
        
        logger.info(f"Logged observation {obs_id} - {obs_data.observation_type.value} of {obs_data.species}")
        return Observation(**obs_doc)
    
    async def get_observations(
        self, 
        user_id: str, 
        trip_id: Optional[str] = None,
        waypoint_id: Optional[str] = None,
        species: Optional[str] = None,
        limit: int = 100
    ) -> List[Observation]:
        """Get observations with filters"""
        query = {"user_id": user_id}
        if trip_id:
            query["trip_id"] = trip_id
        if waypoint_id:
            query["waypoint_id"] = waypoint_id
        if species:
            query["species"] = species
        
        cursor = self.observations_collection.find(query, {"_id": 0}).sort("timestamp", -1).limit(limit)
        observations = await cursor.to_list(length=limit)
        return [Observation(**o) for o in observations]
    
    # ============================================
    # STATISTICS
    # ============================================
    
    async def get_trip_statistics(self, user_id: str) -> TripStatistics:
        """Get comprehensive trip statistics for a user"""
        # Get all completed trips
        trips = await self.trips_collection.find(
            {"user_id": user_id, "status": TripStatus.COMPLETED.value},
            {"_id": 0}
        ).to_list(length=1000)
        
        if not trips:
            return TripStatistics()
        
        total_trips = len(trips)
        successful_trips = sum(1 for t in trips if t.get("success"))
        total_hours = sum(t.get("duration_hours", 0) or 0 for t in trips)
        total_observations = sum(t.get("observations_count", 0) for t in trips)
        
        # Count waypoints visited
        all_waypoints = []
        for t in trips:
            all_waypoints.extend(t.get("visited_waypoints", []))
        
        # By species
        by_species = {}
        for t in trips:
            species = t.get("target_species", "unknown")
            if species not in by_species:
                by_species[species] = {"trips": 0, "success": 0}
            by_species[species]["trips"] += 1
            if t.get("success"):
                by_species[species]["success"] += 1
        
        # By weather
        by_weather = {}
        for t in trips:
            weather = t.get("weather", "unknown")
            if weather not in by_weather:
                by_weather[weather] = {"trips": 0, "success": 0}
            by_weather[weather]["trips"] += 1
            if t.get("success"):
                by_weather[weather]["success"] += 1
        
        # By month
        by_month = {}
        for t in trips:
            planned_date = t.get("planned_date")
            if planned_date:
                if isinstance(planned_date, str):
                    planned_date = datetime.fromisoformat(planned_date.replace('Z', '+00:00'))
                month_key = planned_date.strftime("%Y-%m")
                if month_key not in by_month:
                    by_month[month_key] = {"trips": 0, "success": 0}
                by_month[month_key]["trips"] += 1
                if t.get("success"):
                    by_month[month_key]["success"] += 1
        
        # Find most visited and best waypoint
        waypoint_counts = {}
        for wp in all_waypoints:
            waypoint_counts[wp] = waypoint_counts.get(wp, 0) + 1
        
        most_visited = max(waypoint_counts.keys(), key=lambda x: waypoint_counts[x]) if waypoint_counts else None
        
        # Find favorite species
        favorite_species = max(by_species.keys(), key=lambda x: by_species[x]["trips"]) if by_species else None
        
        return TripStatistics(
            total_trips=total_trips,
            completed_trips=total_trips,
            successful_trips=successful_trips,
            success_rate=round((successful_trips / total_trips) * 100, 1) if total_trips > 0 else 0,
            total_hours=round(total_hours, 1),
            average_duration=round(total_hours / total_trips, 1) if total_trips > 0 else 0,
            total_observations=total_observations,
            total_waypoints_visited=len(all_waypoints),
            most_visited_waypoint=most_visited,
            favorite_species=favorite_species,
            by_species=by_species,
            by_weather=by_weather,
            by_month=by_month
        )
    
    async def get_waypoint_statistics(
        self, 
        user_id: str, 
        waypoint_id: str
    ) -> Optional[WaypointStatistics]:
        """Get statistics for a specific waypoint"""
        visits = await self.visits_collection.find(
            {"user_id": user_id, "waypoint_id": waypoint_id},
            {"_id": 0}
        ).to_list(length=1000)
        
        if not visits:
            return None
        
        # Get waypoint info
        waypoint = await self.waypoints_collection.find_one(
            {"_id": ObjectId(waypoint_id)} if len(waypoint_id) == 24 
            else {"waypoint_id": waypoint_id}
        )
        waypoint_name = waypoint.get("name", "Unknown") if waypoint else "Unknown"
        
        total_visits = len(visits)
        successful_visits = sum(1 for v in visits if v.get("success"))
        total_observations = sum(v.get("observations_count", 0) for v in visits)
        
        # Average activity
        activity_levels = [v.get("activity_level") for v in visits if v.get("activity_level") is not None]
        avg_activity = sum(activity_levels) / len(activity_levels) if activity_levels else 0
        
        # Best weather
        weather_success = {}
        for v in visits:
            weather = v.get("weather", "unknown")
            if weather not in weather_success:
                weather_success[weather] = {"visits": 0, "success": 0}
            weather_success[weather]["visits"] += 1
            if v.get("success"):
                weather_success[weather]["success"] += 1
        
        best_weather = None
        best_rate = 0
        for w, data in weather_success.items():
            if data["visits"] >= 2:  # Minimum visits to count
                rate = data["success"] / data["visits"]
                if rate > best_rate:
                    best_rate = rate
                    best_weather = w
        
        # Get species observed
        observations = await self.observations_collection.find(
            {"user_id": user_id, "waypoint_id": waypoint_id},
            {"species": 1}
        ).to_list(length=500)
        species_observed = list(set(o.get("species") for o in observations if o.get("species")))
        
        return WaypointStatistics(
            waypoint_id=waypoint_id,
            waypoint_name=waypoint_name,
            total_visits=total_visits,
            successful_visits=successful_visits,
            success_rate=round((successful_visits / total_visits) * 100, 1) if total_visits > 0 else 0,
            total_observations=total_observations,
            average_activity=round(avg_activity, 1),
            best_weather=best_weather,
            species_observed=species_observed
        )
    
    # ============================================
    # DATA SYNC TO OTHER ENGINES
    # ============================================
    
    async def _sync_trip_to_analytics(self, trip: dict) -> None:
        """Sync completed trip data to analytics_engine"""
        # Format for analytics_engine
        analytics_doc = {
            "user_id": trip["user_id"],
            "date": trip.get("planned_date") or trip.get("start_time"),
            "species": trip.get("target_species", "deer"),
            "location_lat": 46.8139,  # Default Quebec location
            "location_lng": -71.2080,
            "duration_hours": trip.get("duration_hours", 0),
            "weather_conditions": trip.get("weather"),
            "temperature": trip.get("temperature"),
            "success": trip.get("success", False),
            "observations": trip.get("observations_count", 0),
            "notes": trip.get("notes"),
            "source": "hunting_trip_logger",
            "trip_id": trip.get("trip_id"),
            "created_at": datetime.now(timezone.utc)
        }
        
        # Insert into analytics trips collection
        await self.analytics_trips_collection.insert_one(analytics_doc)
        logger.info(f"Synced trip {trip.get('trip_id')} to analytics_engine")
    
    async def _update_waypoint_scores(self, user_id: str, trip: dict) -> None:
        """Update waypoint scoring data based on trip results"""
        visited_waypoints = trip.get("visited_waypoints", [])
        success = trip.get("success", False)
        trip_weather = trip.get("weather")
        
        for waypoint_id in visited_waypoints:
            # Update visit success in waypoint_visits for scoring
            await self.visits_collection.update_many(
                {
                    "trip_id": trip.get("trip_id"),
                    "waypoint_id": waypoint_id
                },
                {"$set": {"success": success, "weather": trip_weather}}
            )
        
        logger.info(f"Updated scoring data for {len(visited_waypoints)} waypoints")
