"""
Geolocation Engine - Service Layer
Handles location tracking, proximity detection, and push notifications
"""
import os
from datetime import datetime, timezone
from typing import List, Optional, Dict, Tuple
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
import math
import logging
import json

from .models import (
    LocationUpdate, ProximityAlert, LocationHistory,
    TrackingSession, PushSubscription, PushNotification
)

logger = logging.getLogger(__name__)

PROXIMITY_RADIUS_METERS = 500  # Alert when within 500m of waypoint
HOTSPOT_BONUS_RADIUS = 200  # Extra alert radius for hotspots

# VAPID Configuration for Push Notifications
VAPID_PUBLIC_KEY = os.environ.get("VAPID_PUBLIC_KEY", "")
VAPID_PRIVATE_KEY = os.environ.get("VAPID_PRIVATE_KEY", "")
VAPID_CONTACT_EMAIL = os.environ.get("VAPID_CONTACT_EMAIL", "support@huntiq.ca")


def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance between two points in meters using Haversine formula"""
    R = 6371000  # Earth's radius in meters
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lng2 - lng1)
    
    a = math.sin(delta_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


class GeolocationService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.locations_collection = db['user_locations']
        self.sessions_collection = db['tracking_sessions']
        self.subscriptions_collection = db['push_subscriptions']
        self.waypoints_collection = db['user_waypoints']
        self.alerts_collection = db['proximity_alerts']
    
    async def record_location(
        self, 
        user_id: str, 
        location: LocationUpdate,
        session_id: Optional[str] = None
    ) -> Tuple[LocationHistory, List[ProximityAlert]]:
        """Record a location update and check for proximity alerts"""
        
        now = datetime.now(timezone.utc)
        
        # Save location
        doc = {
            "user_id": user_id,
            "latitude": location.latitude,
            "longitude": location.longitude,
            "accuracy": location.accuracy,
            "altitude": location.altitude,
            "speed": location.speed,
            "heading": location.heading,
            "timestamp": location.timestamp or now,
            "session_id": session_id,
            "created_at": now
        }
        
        result = await self.locations_collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        
        # Update session if active
        if session_id:
            await self.sessions_collection.update_one(
                {"_id": ObjectId(session_id), "user_id": user_id},
                {"$inc": {"locations_count": 1}}
            )
        
        # Check proximity to waypoints
        alerts = await self.check_proximity_alerts(
            user_id, location.latitude, location.longitude
        )
        
        location_history = LocationHistory(
            id=str(result.inserted_id),
            user_id=user_id,
            latitude=location.latitude,
            longitude=location.longitude,
            accuracy=location.accuracy,
            timestamp=doc["timestamp"]
        )
        
        return location_history, alerts
    
    async def check_proximity_alerts(
        self, 
        user_id: str, 
        lat: float, 
        lng: float
    ) -> List[ProximityAlert]:
        """Check if user is near any waypoints and generate alerts"""
        
        alerts = []
        
        # Get user waypoints
        cursor = self.waypoints_collection.find({"user_id": user_id})
        waypoints = await cursor.to_list(length=500)
        
        # Get WQS scores for classification
        from modules.waypoint_scoring_engine.v1.service import WaypointScoringService
        wqs_service = WaypointScoringService(self.db)
        
        for wp in waypoints:
            wp_lat = wp.get("lat") or wp.get("latitude", 0)
            wp_lng = wp.get("lng") or wp.get("longitude", 0)
            
            distance = haversine_distance(lat, lng, wp_lat, wp_lng)
            
            # Determine alert radius based on classification
            try:
                wqs = await wqs_service.calculate_wqs(str(wp["_id"]), user_id)
                classification = wqs.classification
                wqs_score = wqs.total_score
            except Exception:
                classification = "standard"
                wqs_score = None
            
            alert_radius = PROXIMITY_RADIUS_METERS
            if classification == "hotspot":
                alert_radius += HOTSPOT_BONUS_RADIUS
            
            if distance <= alert_radius:
                # Check if we already sent this alert recently (within 30 min)
                from datetime import timedelta
                thirty_min_ago = datetime.now(timezone.utc) - timedelta(minutes=30)
                recent_alert = await self.alerts_collection.find_one({
                    "user_id": user_id,
                    "waypoint_id": str(wp["_id"]),
                    "created_at": {"$gte": thirty_min_ago}
                })
                
                if not recent_alert:
                    alert = ProximityAlert(
                        waypoint_id=str(wp["_id"]),
                        waypoint_name=wp.get("name", "Waypoint"),
                        waypoint_type=wp.get("type", "unknown"),
                        distance_meters=round(distance, 1),
                        wqs_score=wqs_score,
                        classification=classification,
                        alert_type="proximity",
                        message=self._generate_proximity_message(
                            wp.get("name"), distance, classification
                        )
                    )
                    alerts.append(alert)
                    
                    # Record alert
                    await self.alerts_collection.insert_one({
                        "user_id": user_id,
                        "waypoint_id": str(wp["_id"]),
                        "alert": alert.dict(),
                        "created_at": datetime.now(timezone.utc)
                    })
        
        return alerts
    
    def _generate_proximity_message(
        self, 
        waypoint_name: str, 
        distance: float, 
        classification: str
    ) -> str:
        """Generate proximity alert message"""
        
        distance_str = f"{int(distance)}m" if distance < 1000 else f"{distance/1000:.1f}km"
        
        if classification == "hotspot":
            return f"🔥 Hotspot '{waypoint_name}' à {distance_str}! Excellent spot de chasse."
        elif classification == "good":
            return f"📍 Waypoint '{waypoint_name}' à {distance_str}. Bon potentiel."
        else:
            return f"📍 Vous approchez de '{waypoint_name}' ({distance_str})."
    
    async def start_tracking_session(self, user_id: str) -> TrackingSession:
        """Start a new tracking session"""
        
        # End any active sessions
        await self.sessions_collection.update_many(
            {"user_id": user_id, "active": True},
            {"$set": {"active": False, "ended_at": datetime.now(timezone.utc)}}
        )
        
        session = {
            "user_id": user_id,
            "started_at": datetime.now(timezone.utc),
            "ended_at": None,
            "locations_count": 0,
            "distance_km": 0.0,
            "active": True
        }
        
        result = await self.sessions_collection.insert_one(session)
        
        return TrackingSession(
            id=str(result.inserted_id),
            **session
        )
    
    async def end_tracking_session(self, user_id: str, session_id: str) -> Optional[TrackingSession]:
        """End a tracking session and calculate stats"""
        
        session = await self.sessions_collection.find_one({
            "_id": ObjectId(session_id),
            "user_id": user_id
        })
        
        if not session:
            return None
        
        # Calculate total distance
        locations = await self.locations_collection.find({
            "session_id": session_id
        }).sort("timestamp", 1).to_list(length=10000)
        
        total_distance = 0.0
        for i in range(1, len(locations)):
            prev = locations[i - 1]
            curr = locations[i]
            total_distance += haversine_distance(
                prev["latitude"], prev["longitude"],
                curr["latitude"], curr["longitude"]
            )
        
        # Update session
        await self.sessions_collection.update_one(
            {"_id": ObjectId(session_id)},
            {
                "$set": {
                    "active": False,
                    "ended_at": datetime.now(timezone.utc),
                    "distance_km": round(total_distance / 1000, 2)
                }
            }
        )
        
        updated = await self.sessions_collection.find_one({"_id": ObjectId(session_id)})
        
        return TrackingSession(
            id=str(updated["_id"]),
            user_id=updated["user_id"],
            started_at=updated["started_at"],
            ended_at=updated.get("ended_at"),
            locations_count=updated.get("locations_count", 0),
            distance_km=updated.get("distance_km", 0.0),
            active=updated.get("active", False)
        )
    
    async def get_location_history(
        self, 
        user_id: str, 
        session_id: Optional[str] = None,
        limit: int = 100
    ) -> List[LocationHistory]:
        """Get location history for user"""
        
        query = {"user_id": user_id}
        if session_id:
            query["session_id"] = session_id
        
        cursor = self.locations_collection.find(query).sort("timestamp", -1).limit(limit)
        locations = await cursor.to_list(length=limit)
        
        return [
            LocationHistory(
                id=str(loc["_id"]),
                user_id=loc["user_id"],
                latitude=loc["latitude"],
                longitude=loc["longitude"],
                accuracy=loc.get("accuracy"),
                timestamp=loc["timestamp"],
                session_id=loc.get("session_id")
            )
            for loc in locations
        ]
    
    # Push Notification Methods
    async def save_push_subscription(
        self, 
        user_id: str, 
        subscription: PushSubscription
    ) -> bool:
        """Save or update push subscription"""
        
        await self.subscriptions_collection.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "endpoint": subscription.endpoint,
                    "keys": subscription.keys,
                    "updated_at": datetime.now(timezone.utc)
                },
                "$setOnInsert": {
                    "created_at": datetime.now(timezone.utc)
                }
            },
            upsert=True
        )
        
        logger.info(f"Saved push subscription for user {user_id}")
        return True
    
    async def remove_push_subscription(self, user_id: str) -> bool:
        """Remove push subscription"""
        
        result = await self.subscriptions_collection.delete_one({"user_id": user_id})
        return result.deleted_count > 0
    
    async def get_push_subscription(self, user_id: str) -> Optional[Dict]:
        """Get push subscription for user"""
        
        sub = await self.subscriptions_collection.find_one({"user_id": user_id})
        if sub:
            return {
                "endpoint": sub["endpoint"],
                "keys": sub["keys"]
            }
        return None
    
    async def send_push_notification(
        self, 
        user_id: str, 
        notification: PushNotification
    ) -> bool:
        """Send push notification to user using Web Push with VAPID"""
        
        subscription = await self.get_push_subscription(user_id)
        if not subscription:
            logger.warning(f"No push subscription for user {user_id}")
            return False
        
        # Store notification for retrieval
        await self.db['notifications'].insert_one({
            "user_id": user_id,
            "notification": notification.dict(),
            "sent_at": datetime.now(timezone.utc),
            "read": False
        })
        
        # Send actual push notification if VAPID keys are configured
        if VAPID_PUBLIC_KEY and VAPID_PRIVATE_KEY:
            try:
                from pywebpush import webpush, WebPushException
                
                payload = json.dumps({
                    "title": notification.title,
                    "body": notification.body,
                    "icon": notification.icon,
                    "badge": notification.badge,
                    "url": notification.url,
                    "tag": notification.tag,
                    "data": notification.data
                })
                
                webpush(
                    subscription_info={
                        "endpoint": subscription["endpoint"],
                        "keys": subscription["keys"]
                    },
                    data=payload,
                    vapid_private_key=VAPID_PRIVATE_KEY,
                    vapid_claims={
                        "sub": f"mailto:{VAPID_CONTACT_EMAIL}"
                    }
                )
                
                logger.info(f"Push notification sent to {user_id}: {notification.title}")
                return True
                
            except WebPushException as e:
                logger.error(f"Push notification failed for {user_id}: {e}")
                # If subscription is invalid, remove it
                if e.response and e.response.status_code in [404, 410]:
                    await self.remove_push_subscription(user_id)
                return False
            except Exception as e:
                logger.error(f"Push error: {e}")
                return False
        else:
            logger.info(f"Push notification logged for {user_id}: {notification.title} (VAPID not configured)")
            return True
    
    async def get_nearby_hotspots(
        self, 
        user_id: str, 
        lat: float, 
        lng: float, 
        radius_km: float = 5.0
    ) -> List[Dict]:
        """Get hotspot waypoints near a location"""
        
        cursor = self.waypoints_collection.find({"user_id": user_id})
        waypoints = await cursor.to_list(length=500)
        
        from modules.waypoint_scoring_engine.v1.service import WaypointScoringService
        wqs_service = WaypointScoringService(self.db)
        
        nearby = []
        for wp in waypoints:
            wp_lat = wp.get("lat") or wp.get("latitude", 0)
            wp_lng = wp.get("lng") or wp.get("longitude", 0)
            
            distance = haversine_distance(lat, lng, wp_lat, wp_lng)
            
            if distance <= radius_km * 1000:
                try:
                    wqs = await wqs_service.calculate_wqs(str(wp["_id"]), user_id)
                    nearby.append({
                        "waypoint_id": str(wp["_id"]),
                        "name": wp.get("name"),
                        "lat": wp_lat,
                        "lng": wp_lng,
                        "distance_m": round(distance, 1),
                        "wqs": wqs.total_score,
                        "classification": wqs.classification
                    })
                except Exception:
                    pass
        
        # Sort by WQS score descending
        return sorted(nearby, key=lambda x: x.get("wqs", 0), reverse=True)
