"""
Waypoint Scoring Engine - Service Layer
Calculates WQS, Success Forecast, and AI recommendations
"""
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Tuple
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
import logging
import random
import math

from .models import (
    WaypointQualityScore, SuccessForecast, HeatmapData,
    WaypointRecommendation, ForecastRequest
)

logger = logging.getLogger(__name__)

# Scoring weights
WEIGHTS = {
    "success_history": 0.40,
    "weather": 0.25,
    "activity": 0.20,
    "accessibility": 0.15
}

# Weather impact on hunting success
WEATHER_SUCCESS_RATES = {
    "Ensoleillé": 0.75,
    "Nuageux": 0.85,  # Best for hunting
    "Pluvieux": 0.45,
    "Brumeux": 0.65,
    "Neigeux": 0.55
}

# Optimal hunting hours
OPTIMAL_HOURS = {
    "dawn": (5, 8),      # Best
    "dusk": (16, 19),    # Best
    "morning": (8, 12),  # Good
    "afternoon": (12, 16),  # Moderate
    "night": (19, 5)     # Poor
}


def make_aware(dt):
    """Ensure datetime is timezone-aware"""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def safe_days_ago(dt):
    """Safely calculate days since a datetime, handling timezone issues"""
    if dt is None:
        return float('inf')
    try:
        aware_dt = make_aware(dt)
        now = datetime.now(timezone.utc)
        return (now - aware_dt).days
    except Exception:
        return float('inf')


class WaypointScoringService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.waypoints_collection = db['user_waypoints']
        self.trips_collection = db['hunting_trips']
        self.visits_collection = db['waypoint_visits']
    
    async def calculate_wqs(self, waypoint_id: str, user_id: str) -> WaypointQualityScore:
        """Calculate Waypoint Quality Score for a single waypoint"""
        
        # Try different ways to find the waypoint
        waypoint = None
        
        # Try by ObjectId (if it's a valid hex string)
        try:
            if len(waypoint_id) == 24:
                waypoint = await self.waypoints_collection.find_one({
                    "_id": ObjectId(waypoint_id),
                    "user_id": user_id
                })
                # Also try with _id as string
                if not waypoint:
                    waypoint = await self.waypoints_collection.find_one({
                        "_id": waypoint_id,
                        "user_id": user_id
                    })
        except Exception as e:
            logger.debug(f"ObjectId lookup failed: {e}")
        
        # Try by string id field
        if not waypoint:
            waypoint = await self.waypoints_collection.find_one({
                "user_id": user_id,
                "id": waypoint_id
            })
        
        if not waypoint:
            raise ValueError(f"Waypoint {waypoint_id} not found")
        
        waypoint_name = waypoint.get("name", "Unknown")
        # Support both lat/lng and latitude/longitude
        wp_lat = waypoint.get("lat") or waypoint.get("latitude", 0)
        wp_lng = waypoint.get("lng") or waypoint.get("longitude", 0)
        
        # Get visits/trips near this waypoint (within 0.5km)
        nearby_trips = await self._get_nearby_trips(wp_lat, wp_lng, user_id, radius_km=0.5)
        
        # Calculate component scores
        success_score, total_visits, successful_visits, success_rate, last_visit = await self._calc_success_history_score(nearby_trips)
        weather_score = await self._calc_weather_score(nearby_trips)
        activity_score = await self._calc_activity_score(nearby_trips, waypoint)
        accessibility_score = await self._calc_accessibility_score(waypoint, nearby_trips)
        
        # Calculate total WQS
        total_score = (
            success_score * WEIGHTS["success_history"] +
            weather_score * WEIGHTS["weather"] +
            activity_score * WEIGHTS["activity"] +
            accessibility_score * WEIGHTS["accessibility"]
        )
        
        # Classification
        if total_score >= 75:
            classification = "hotspot"
        elif total_score >= 55:
            classification = "good"
        elif total_score >= 35:
            classification = "standard"
        else:
            classification = "weak"
        
        return WaypointQualityScore(
            waypoint_id=str(waypoint.get("_id", waypoint_id)),
            waypoint_name=waypoint_name,
            total_score=round(total_score, 1),
            success_history_score=round(success_score, 1),
            weather_score=round(weather_score, 1),
            activity_score=round(activity_score, 1),
            accessibility_score=round(accessibility_score, 1),
            total_visits=total_visits,
            successful_visits=successful_visits,
            success_rate=round(success_rate, 1),
            last_visit=last_visit,
            classification=classification
        )
    
    async def _get_nearby_trips(self, lat: float, lng: float, user_id: str, radius_km: float = 0.5) -> List[dict]:
        """Get hunting trips near a location"""
        # Simple distance filter (approximate)
        lat_diff = radius_km / 111  # 1 degree lat ≈ 111 km
        lng_diff = radius_km / (111 * abs(math.cos(math.radians(lat))))
        
        cursor = self.trips_collection.find({
            "user_id": user_id,
            "location_lat": {"$gte": lat - lat_diff, "$lte": lat + lat_diff},
            "location_lng": {"$gte": lng - lng_diff, "$lte": lng + lng_diff}
        })
        
        return await cursor.to_list(length=500)
    
    async def _calc_success_history_score(self, trips: List[dict]) -> Tuple[float, int, int, float, Optional[str]]:
        """Calculate success history score (40% weight)"""
        if not trips:
            return 50.0, 0, 0, 0.0, None  # Default score for no data
        
        total = len(trips)
        successful = sum(1 for t in trips if t.get("success", False))
        success_rate = (successful / total * 100) if total > 0 else 0
        
        # Score based on success rate with bonus for volume
        base_score = success_rate
        volume_bonus = min(10, total * 0.5)  # Up to 10 points for volume
        
        # Get last visit
        sorted_trips = sorted(trips, key=lambda x: x.get("date", datetime.min), reverse=True)
        last_visit = sorted_trips[0].get("date").isoformat() if sorted_trips and sorted_trips[0].get("date") else None
        
        return min(100, base_score + volume_bonus), total, successful, success_rate, last_visit
    
    async def _calc_weather_score(self, trips: List[dict]) -> float:
        """Calculate weather-based score (25% weight)"""
        if not trips:
            return 50.0
        
        weather_success = {}
        for trip in trips:
            weather = trip.get("weather_conditions", "Unknown")
            if weather not in weather_success:
                weather_success[weather] = {"total": 0, "success": 0}
            weather_success[weather]["total"] += 1
            if trip.get("success"):
                weather_success[weather]["success"] += 1
        
        # Score based on favorable weather correlation
        scores = []
        for weather, stats in weather_success.items():
            if stats["total"] > 0:
                rate = stats["success"] / stats["total"]
                expected = WEATHER_SUCCESS_RATES.get(weather, 0.5)
                # Higher score if actual rate exceeds expected
                scores.append(min(100, (rate / max(expected, 0.1)) * 50 + 25))
        
        return sum(scores) / len(scores) if scores else 50.0
    
    async def _calc_activity_score(self, trips: List[dict], waypoint: dict) -> float:
        """Calculate animal activity score (20% weight)"""
        if not trips:
            return 50.0
        
        total_observations = sum(t.get("observations", 0) for t in trips)
        avg_observations = total_observations / len(trips) if trips else 0
        
        # Score based on observation density
        # 5+ observations per trip is excellent
        score = min(100, avg_observations * 20)
        
        # Bonus for recent activity
        recent_trips = [t for t in trips if t.get("date") and safe_days_ago(t["date"]) < 30]
        if recent_trips:
            score = min(100, score + 10)
        
        return score
    
    async def _calc_accessibility_score(self, waypoint: dict, trips: List[dict]) -> float:
        """Calculate accessibility/frequency score (15% weight)"""
        # Based on visit frequency and recency
        if not trips:
            return 40.0  # New waypoint gets moderate accessibility score
        
        total_visits = len(trips)
        
        # Recent visits (last 90 days)
        recent_visits = sum(1 for t in trips if t.get("date") and safe_days_ago(t["date"]) < 90)
        
        # Score based on frequency
        frequency_score = min(50, total_visits * 5)
        recency_score = min(50, recent_visits * 10)
        
        return frequency_score + recency_score
    
    async def get_all_wqs(self, user_id: str) -> List[WaypointQualityScore]:
        """Calculate WQS for all user waypoints"""
        cursor = self.waypoints_collection.find({"user_id": user_id})
        waypoints = await cursor.to_list(length=500)
        
        logger.info(f"Found {len(waypoints)} waypoints for user {user_id}")
        
        scores = []
        for wp in waypoints:
            try:
                # Get ID from either _id (as string or ObjectId) or id field
                wp_id = wp.get("_id")
                if wp_id:
                    wp_id = str(wp_id)
                else:
                    wp_id = wp.get("id", "")
                
                logger.debug(f"Calculating WQS for waypoint {wp_id}: {wp.get('name')}")
                wqs = await self.calculate_wqs(wp_id, user_id)
                scores.append(wqs)
            except Exception as e:
                logger.error(f"Error calculating WQS for {wp.get('name')}: {e}")
        
        return sorted(scores, key=lambda x: x.total_score, reverse=True)
    
    async def get_heatmap_data(self, user_id: str) -> List[HeatmapData]:
        """Generate heatmap data for waypoint performance visualization"""
        cursor = self.waypoints_collection.find({"user_id": user_id})
        waypoints = await cursor.to_list(length=500)
        
        heatmap = []
        for wp in waypoints:
            try:
                wp_id = str(wp.get("_id", wp.get("id", "")))
                wqs = await self.calculate_wqs(wp_id, user_id)
                # Normalize intensity to 0-1 scale
                intensity = wqs.total_score / 100
                
                # Support both lat/lng and latitude/longitude
                lat = wp.get("lat") or wp.get("latitude", 0)
                lng = wp.get("lng") or wp.get("longitude", 0)
                
                heatmap.append(HeatmapData(
                    lat=lat,
                    lng=lng,
                    intensity=intensity,
                    waypoint_id=wp_id,
                    waypoint_name=wp.get("name", "Unknown"),
                    wqs=wqs.total_score
                ))
            except Exception as e:
                logger.error(f"Error generating heatmap for {wp.get('name')}: {e}")
        
        return heatmap
    
    async def calculate_success_forecast(
        self, 
        request: ForecastRequest,
        user_id: str
    ) -> SuccessForecast:
        """Calculate success probability forecast"""
        
        # Get all waypoint scores
        all_wqs = await self.get_all_wqs(user_id)
        
        if not all_wqs:
            return SuccessForecast(
                probability=0,
                confidence="low",
                favorable_conditions=["Aucun waypoint enregistré"],
                unfavorable_conditions=[]
            )
        
        # Base probability from best waypoint WQS
        best_waypoint = all_wqs[0]
        base_prob = best_waypoint.total_score * 0.6  # Max 60% from WQS
        
        # Weather modifier
        weather_mod = 0
        favorable = []
        unfavorable = []
        
        if request.weather_conditions:
            weather_rate = WEATHER_SUCCESS_RATES.get(request.weather_conditions, 0.5)
            weather_mod = (weather_rate - 0.5) * 40  # -20 to +14
            
            if weather_rate >= 0.7:
                favorable.append(f"Météo favorable: {request.weather_conditions}")
            elif weather_rate < 0.5:
                unfavorable.append(f"Météo défavorable: {request.weather_conditions}")
        
        # Time modifier
        time_mod = 0
        target_hour = request.target_hour or datetime.now().hour
        
        if 5 <= target_hour < 8 or 16 <= target_hour < 19:
            time_mod = 15
            favorable.append("Créneau optimal (aube/crépuscule)")
        elif 8 <= target_hour < 12:
            time_mod = 5
            favorable.append("Bon créneau (matin)")
        elif 19 <= target_hour or target_hour < 5:
            time_mod = -10
            unfavorable.append("Créneau peu favorable (nuit)")
        
        # Temperature modifier (if provided)
        if request.temperature is not None:
            if -5 <= request.temperature <= 15:
                time_mod += 5
                favorable.append(f"Température idéale: {request.temperature}°C")
            elif request.temperature < -15 or request.temperature > 25:
                time_mod -= 10
                unfavorable.append(f"Température extrême: {request.temperature}°C")
        
        # Calculate final probability
        final_prob = min(95, max(5, base_prob + weather_mod + time_mod))
        
        # Determine optimal time window
        optimal_window = "06:00-08:00 ou 17:00-19:00"
        
        # Confidence based on data quality
        if best_waypoint.total_visits >= 10:
            confidence = "high"
        elif best_waypoint.total_visits >= 3:
            confidence = "medium"
        else:
            confidence = "low"
        
        return SuccessForecast(
            probability=round(final_prob, 1),
            confidence=confidence,
            best_waypoint=best_waypoint,
            optimal_time_window=optimal_window,
            favorable_conditions=favorable,
            unfavorable_conditions=unfavorable
        )
    
    async def get_ai_recommendations(
        self,
        species: str,
        weather: Optional[str],
        user_id: str,
        ai_client = None
    ) -> List[WaypointRecommendation]:
        """Generate AI-powered waypoint recommendations"""
        
        # Get all waypoints with scores
        all_wqs = await self.get_all_wqs(user_id)
        
        if not all_wqs:
            return []
        
        recommendations = []
        current_hour = datetime.now().hour
        
        for wqs in all_wqs[:5]:  # Top 5 waypoints
            # Calculate match scores
            weather_match = 0.7  # Default
            if weather:
                weather_rate = WEATHER_SUCCESS_RATES.get(weather, 0.5)
                weather_match = weather_rate
            
            # Time match based on current time
            if 5 <= current_hour < 8 or 16 <= current_hour < 19:
                time_match = 0.95
            elif 8 <= current_hour < 12:
                time_match = 0.7
            else:
                time_match = 0.4
            
            # Species match (simplified)
            species_match = 0.8 if species in ["deer", "moose"] else 0.6
            
            # Success probability
            success_prob = (
                wqs.total_score * 0.4 +
                weather_match * 100 * 0.3 +
                time_match * 100 * 0.3
            )
            
            # Generate reasoning
            reasoning = f"Score WQS de {wqs.total_score}% avec {wqs.total_visits} visites. "
            if wqs.success_rate > 40:
                reasoning += f"Taux de succès historique de {wqs.success_rate}%. "
            
            # Tips
            tips = []
            if 5 <= current_hour < 8:
                tips.append("Arrivez 30 min avant le lever du soleil")
            elif 16 <= current_hour < 19:
                tips.append("Positionnez-vous face au vent")
            tips.append(f"Espèce ciblée: {species}")
            
            # Recommended time
            if current_hour < 6:
                rec_time = "06:00-08:00"
            elif current_hour < 16:
                rec_time = "17:00-19:00"
            else:
                rec_time = "06:00-08:00 demain"
            
            recommendations.append(WaypointRecommendation(
                waypoint_id=wqs.waypoint_id,
                waypoint_name=wqs.waypoint_name,
                wqs=wqs.total_score,
                success_probability=round(success_prob, 1),
                reasoning=reasoning,
                weather_match=round(weather_match * 100, 1),
                time_match=round(time_match * 100, 1),
                species_match=round(species_match * 100, 1),
                recommended_time=rec_time,
                tips=tips
            ))
        
        return sorted(recommendations, key=lambda x: x.success_probability, reverse=True)
    
    async def seed_demo_visits(self, user_id: str) -> int:
        """Seed demo visit data for testing WQS calculations"""
        # Get existing waypoints
        cursor = self.waypoints_collection.find({"user_id": user_id})
        waypoints = await cursor.to_list(length=500)
        
        if not waypoints:
            return 0
        
        trips = []
        now = datetime.now(timezone.utc)
        weather_options = list(WEATHER_SUCCESS_RATES.keys())
        
        for wp in waypoints:
            # Support both lat/lng and latitude/longitude
            wp_lat = wp.get("lat") or wp.get("latitude", 0)
            wp_lng = wp.get("lng") or wp.get("longitude", 0)
            
            # Generate 5-15 visits per waypoint
            num_visits = random.randint(5, 15)
            
            for _ in range(num_visits):
                days_ago = random.randint(1, 180)
                hour = random.choice([6, 7, 17, 18, 8, 9, 15, 16])
                
                trip_date = now - timedelta(days=days_ago)
                trip_date = trip_date.replace(hour=hour)
                
                weather = random.choice(weather_options)
                
                # Success probability based on conditions
                base_prob = 0.35
                base_prob += WEATHER_SUCCESS_RATES.get(weather, 0.5) * 0.2
                if hour in [6, 7, 17, 18]:
                    base_prob += 0.15
                
                success = random.random() < base_prob
                
                trips.append({
                    "user_id": user_id,
                    "date": trip_date,
                    "species": random.choice(["deer", "moose", "bear"]),
                    "location_lat": wp_lat + random.uniform(-0.001, 0.001),
                    "location_lng": wp_lng + random.uniform(-0.001, 0.001),
                    "duration_hours": round(random.uniform(2, 6), 1),
                    "weather_conditions": weather,
                    "temperature": round(random.uniform(-5, 20), 1),
                    "wind_speed": round(random.uniform(0, 25), 1),
                    "moon_phase": random.choice(["Nouvelle lune", "Premier quartier", "Pleine lune"]),
                    "success": success,
                    "observations": random.randint(0, 8) if not success else random.randint(1, 12),
                    "notes": f"Visite au waypoint {wp['name']}",
                    "created_at": now
                })
        
        if trips:
            result = await self.trips_collection.insert_many(trips)
            logger.info(f"Seeded {len(result.inserted_ids)} demo visits for WQS")
            return len(result.inserted_ids)
        
        return 0
