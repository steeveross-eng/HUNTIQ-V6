"""Live Heading Engine Service - PHASE 6
Business logic for live heading view.

Version: 1.0.0
"""

import os
import math
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timezone
from pymongo import MongoClient

from .models import (
    HeadingSession,
    HeadingUpdate,
    HeadingViewState,
    GeoPosition,
    ViewCone,
    WindData,
    PointOfInterest,
    HeadingAlert,
    SessionState,
    AlertType,
    AlertPriority,
    POIType,
    SessionSettings
)


class LiveHeadingService:
    """Service for live heading view operations"""
    
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'test_database')
        self._client = None
        self._db = None
        
        # In-memory session cache for real-time performance
        self._active_sessions: Dict[str, HeadingSession] = {}
        
        # POI type configurations
        self.poi_configs = {
            POIType.FEEDING_ZONE: {"icon": "🍽️", "color": "#22c55e", "priority": 8},
            POIType.BEDDING_ZONE: {"icon": "🛏️", "color": "#8b5cf6", "priority": 7},
            POIType.WATER_SOURCE: {"icon": "💧", "color": "#3b82f6", "priority": 6},
            POIType.TRAIL: {"icon": "👣", "color": "#f59e0b", "priority": 5},
            POIType.STAND: {"icon": "🌲", "color": "#84cc16", "priority": 9},
            POIType.BLIND: {"icon": "🏕️", "color": "#a3e635", "priority": 9},
            POIType.CAMERA: {"icon": "📷", "color": "#06b6d4", "priority": 6},
            POIType.OBSERVATION: {"icon": "👁️", "color": "#f97316", "priority": 7},
            POIType.SIGN: {"icon": "🦌", "color": "#ef4444", "priority": 8},
            POIType.WAYPOINT: {"icon": "📍", "color": "#64748b", "priority": 4}
        }
    
    @property
    def db(self):
        if self._db is None:
            self._client = MongoClient(self.mongo_url)
            self._db = self._client[self.db_name]
        return self._db
    
    @property
    def sessions_collection(self):
        return self.db.heading_sessions
    
    @property
    def pois_collection(self):
        return self.db.heading_pois
    
    # ===========================================
    # SESSION MANAGEMENT
    # ===========================================
    
    async def create_session(
        self,
        user_id: str,
        lat: float,
        lng: float,
        heading: float = 0,
        cone_aperture: float = 60,
        cone_range: float = 500
    ) -> HeadingSession:
        """Create a new heading session"""
        
        # Create initial position
        position = GeoPosition(
            lat=lat,
            lng=lng,
            heading=heading
        )
        
        # Create view cone
        view_cone = ViewCone(
            aperture_degrees=cone_aperture,
            range_meters=cone_range,
            direction=heading
        )
        view_cone.vertices = self._calculate_cone_vertices(lat, lng, heading, cone_aperture, cone_range)
        
        # Create session
        session = HeadingSession(
            user_id=user_id,
            state=SessionState.ACTIVE,
            position=position,
            view_cone=view_cone,
            settings={
                "cone_aperture": cone_aperture,
                "cone_range": cone_range,
                "auto_rotate_map": True,
                "show_wind_indicator": True,
                "show_terrain": True,
                "show_trails": True,
                "show_group_members": True,
                "alert_sounds": True,
                "vibrate_on_alert": True
            }
        )
        
        # Get initial wind data
        session.wind = await self._get_wind_data(lat, lng, heading)
        
        # Get POIs in view
        session.visible_pois = await self._get_pois_in_cone(session)
        
        # Cache session
        self._active_sessions[session.id] = session
        
        # Persist to DB
        session_dict = session.model_dump()
        self.sessions_collection.insert_one(session_dict)
        
        return session
    
    async def get_session(self, session_id: str) -> Optional[HeadingSession]:
        """Get session by ID"""
        # Check cache first
        if session_id in self._active_sessions:
            return self._active_sessions[session_id]
        
        # Load from DB
        session_data = self.sessions_collection.find_one(
            {"id": session_id}, {"_id": 0}
        )
        
        if session_data:
            session = HeadingSession(**session_data)
            self._active_sessions[session_id] = session
            return session
        
        return None
    
    async def update_position(self, update: HeadingUpdate) -> Optional[HeadingViewState]:
        """Update session position and get new view state"""
        session = await self.get_session(update.session_id)
        
        if not session or session.state != SessionState.ACTIVE:
            return None
        
        # Calculate distance traveled
        if session.position:
            distance = self._haversine(
                session.position.lat, session.position.lng,
                update.lat, update.lng
            ) * 1000  # km to meters
            session.distance_traveled_m += distance
        
        # Update position
        session.position = GeoPosition(
            lat=update.lat,
            lng=update.lng,
            altitude=update.altitude,
            accuracy=update.accuracy,
            heading=update.heading,
            speed=update.speed
        )
        
        # Update view cone
        session.view_cone.direction = update.heading
        session.view_cone.vertices = self._calculate_cone_vertices(
            update.lat, update.lng, update.heading,
            session.view_cone.aperture_degrees,
            session.view_cone.range_meters
        )
        
        # Update wind data periodically
        session.wind = await self._get_wind_data(update.lat, update.lng, update.heading)
        
        # Get POIs in cone
        session.visible_pois = await self._get_pois_in_cone(session)
        
        # Check for alerts
        new_alerts = await self._check_for_alerts(session)
        session.alerts = [a for a in session.alerts if not a.acknowledged][:5]  # Keep recent
        session.alerts.extend(new_alerts)
        
        # Update timestamps
        session.last_update = datetime.now(timezone.utc)
        session.duration_seconds = int(
            (session.last_update - session.started_at).total_seconds()
        )
        
        # Update cache
        self._active_sessions[update.session_id] = session
        
        # Persist update
        self.sessions_collection.update_one(
            {"id": update.session_id},
            {"$set": session.model_dump()}
        )
        
        # Return view state
        return HeadingViewState(
            session_id=session.id,
            state=session.state,
            position=session.position,
            view_cone=session.view_cone,
            wind=session.wind,
            pois=session.visible_pois,
            alerts=session.alerts,
            distance_traveled_m=session.distance_traveled_m,
            duration_seconds=session.duration_seconds
        )
    
    async def update_settings(
        self,
        session_id: str,
        settings: SessionSettings
    ) -> Optional[HeadingSession]:
        """Update session settings"""
        session = await self.get_session(session_id)
        
        if not session:
            return None
        
        # Update settings
        settings_dict = settings.model_dump(exclude_none=True)
        session.settings.update(settings_dict)
        
        # Apply cone changes
        if settings.cone_aperture is not None:
            session.view_cone.aperture_degrees = settings.cone_aperture
        if settings.cone_range is not None:
            session.view_cone.range_meters = settings.cone_range
        
        # Recalculate cone if needed
        if session.position:
            session.view_cone.vertices = self._calculate_cone_vertices(
                session.position.lat,
                session.position.lng,
                session.view_cone.direction,
                session.view_cone.aperture_degrees,
                session.view_cone.range_meters
            )
        
        # Update cache and DB
        self._active_sessions[session_id] = session
        self.sessions_collection.update_one(
            {"id": session_id},
            {"$set": session.model_dump()}
        )
        
        return session
    
    async def pause_session(self, session_id: str) -> bool:
        """Pause a session"""
        session = await self.get_session(session_id)
        if session and session.state == SessionState.ACTIVE:
            session.state = SessionState.PAUSED
            self._active_sessions[session_id] = session
            self.sessions_collection.update_one(
                {"id": session_id},
                {"$set": {"state": SessionState.PAUSED.value}}
            )
            return True
        return False
    
    async def resume_session(self, session_id: str) -> bool:
        """Resume a paused session"""
        session = await self.get_session(session_id)
        if session and session.state == SessionState.PAUSED:
            session.state = SessionState.ACTIVE
            self._active_sessions[session_id] = session
            self.sessions_collection.update_one(
                {"id": session_id},
                {"$set": {"state": SessionState.ACTIVE.value}}
            )
            return True
        return False
    
    async def end_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """End a session and return summary"""
        session = await self.get_session(session_id)
        
        if not session:
            return None
        
        session.state = SessionState.ENDED
        session.ended_at = datetime.now(timezone.utc)
        
        # Calculate final stats
        summary = {
            "session_id": session_id,
            "user_id": session.user_id,
            "duration_seconds": session.duration_seconds,
            "duration_formatted": self._format_duration(session.duration_seconds),
            "distance_traveled_m": round(session.distance_traveled_m, 1),
            "distance_formatted": f"{session.distance_traveled_m / 1000:.2f} km",
            "pois_visited": len(session.pois_visited),
            "alerts_received": len(session.alerts),
            "started_at": session.started_at.isoformat(),
            "ended_at": session.ended_at.isoformat()
        }
        
        # Remove from cache
        if session_id in self._active_sessions:
            del self._active_sessions[session_id]
        
        # Update DB
        self.sessions_collection.update_one(
            {"id": session_id},
            {"$set": session.model_dump()}
        )
        
        return summary
    
    async def acknowledge_alert(self, session_id: str, alert_id: str) -> bool:
        """Acknowledge an alert"""
        session = await self.get_session(session_id)
        if not session:
            return False
        
        for alert in session.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                self._active_sessions[session_id] = session
                return True
        
        return False
    
    # ===========================================
    # POI MANAGEMENT
    # ===========================================
    
    async def add_poi(
        self,
        session_id: str,
        poi_type: POIType,
        lat: float,
        lng: float,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> PointOfInterest:
        """Add a POI during session"""
        config = self.poi_configs.get(poi_type, {"icon": "📍", "color": "#64748b", "priority": 5})
        
        poi = PointOfInterest(
            lat=lat,
            lng=lng,
            poi_type=poi_type,
            name=name or poi_type.value.replace("_", " ").title(),
            description=description,
            priority=config["priority"],
            icon=config["icon"],
            color=config["color"]
        )
        
        # Persist POI
        poi_dict = poi.model_dump()
        poi_dict["session_id"] = session_id
        self.pois_collection.insert_one(poi_dict)
        
        # Update session
        session = await self.get_session(session_id)
        if session:
            session.pois_visited.append(poi.id)
        
        return poi
    
    async def get_session_pois(self, session_id: str) -> List[PointOfInterest]:
        """Get all POIs for a session"""
        pois = list(self.pois_collection.find(
            {"session_id": session_id}, {"_id": 0}
        ))
        return [PointOfInterest(**p) for p in pois]
    
    # ===========================================
    # INTERNAL METHODS
    # ===========================================
    
    def _calculate_cone_vertices(
        self,
        lat: float,
        lng: float,
        heading: float,
        aperture: float,
        range_m: float
    ) -> List[Dict[str, float]]:
        """Calculate cone polygon vertices"""
        vertices = [{"lat": lat, "lng": lng}]  # Apex
        
        # Calculate left edge bearing (right_bearing calculated for symmetry reference)
        half_aperture = aperture / 2
        left_bearing = (heading - half_aperture) % 360
        # right_bearing would be: (heading + half_aperture) % 360
        
        # Number of points along arc
        num_arc_points = 8
        
        for i in range(num_arc_points + 1):
            t = i / num_arc_points
            bearing = left_bearing + t * aperture
            if bearing >= 360:
                bearing -= 360
            
            point = self._destination_point(lat, lng, bearing, range_m / 1000)
            vertices.append(point)
        
        return vertices
    
    def _destination_point(
        self,
        lat: float,
        lng: float,
        bearing: float,
        distance_km: float
    ) -> Dict[str, float]:
        """Calculate destination point given start, bearing, and distance"""
        R = 6371  # Earth radius in km
        
        lat_rad = math.radians(lat)
        lng_rad = math.radians(lng)
        bearing_rad = math.radians(bearing)
        
        lat2 = math.asin(
            math.sin(lat_rad) * math.cos(distance_km / R) +
            math.cos(lat_rad) * math.sin(distance_km / R) * math.cos(bearing_rad)
        )
        
        lng2 = lng_rad + math.atan2(
            math.sin(bearing_rad) * math.sin(distance_km / R) * math.cos(lat_rad),
            math.cos(distance_km / R) - math.sin(lat_rad) * math.sin(lat2)
        )
        
        return {
            "lat": math.degrees(lat2),
            "lng": math.degrees(lng2)
        }
    
    def _haversine(
        self,
        lat1: float,
        lng1: float,
        lat2: float,
        lng2: float
    ) -> float:
        """Calculate distance in km"""
        R = 6371
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def _calculate_bearing(
        self,
        lat1: float,
        lng1: float,
        lat2: float,
        lng2: float
    ) -> float:
        """Calculate bearing from point 1 to point 2"""
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lng = math.radians(lng2 - lng1)
        
        x = math.sin(delta_lng) * math.cos(lat2_rad)
        y = (math.cos(lat1_rad) * math.sin(lat2_rad) -
             math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lng))
        
        bearing = math.degrees(math.atan2(x, y))
        return (bearing + 360) % 360
    
    def _is_point_in_cone(
        self,
        user_lat: float,
        user_lng: float,
        heading: float,
        aperture: float,
        range_m: float,
        point_lat: float,
        point_lng: float
    ) -> Tuple[bool, float, float]:
        """Check if point is in cone, return (in_cone, distance, relative_angle)"""
        # Calculate distance
        distance = self._haversine(user_lat, user_lng, point_lat, point_lng) * 1000
        
        if distance > range_m:
            return False, distance, 0
        
        # Calculate bearing to point
        bearing = self._calculate_bearing(user_lat, user_lng, point_lat, point_lng)
        
        # Calculate relative angle
        relative_angle = bearing - heading
        if relative_angle > 180:
            relative_angle -= 360
        if relative_angle < -180:
            relative_angle += 360
        
        # Check if within aperture
        half_aperture = aperture / 2
        in_cone = abs(relative_angle) <= half_aperture
        
        return in_cone, distance, relative_angle
    
    async def _get_pois_in_cone(self, session: HeadingSession) -> List[PointOfInterest]:
        """Get POIs visible in the current view cone"""
        if not session.position:
            return []
        
        # Get POIs from database
        all_pois = list(self.pois_collection.find({}, {"_id": 0}).limit(100))
        
        visible_pois = []
        
        for poi_data in all_pois:
            poi = PointOfInterest(**poi_data)
            
            in_cone, distance, relative_angle = self._is_point_in_cone(
                session.position.lat,
                session.position.lng,
                session.view_cone.direction,
                session.view_cone.aperture_degrees,
                session.view_cone.range_meters,
                poi.lat,
                poi.lng
            )
            
            if in_cone:
                poi.visible_in_cone = True
                poi.distance_m = distance
                poi.bearing = self._calculate_bearing(
                    session.position.lat, session.position.lng,
                    poi.lat, poi.lng
                )
                poi.relative_angle = relative_angle
                visible_pois.append(poi)
        
        # Sort by distance
        visible_pois.sort(key=lambda p: p.distance_m)
        
        # If no real POIs, generate some placeholder ones
        if not visible_pois:
            visible_pois = self._generate_placeholder_pois(session)
        
        return visible_pois[:20]  # Limit to 20
    
    def _generate_placeholder_pois(self, session: HeadingSession) -> List[PointOfInterest]:
        """Generate placeholder POIs for demo"""
        import random
        
        pois = []
        poi_types = list(POIType)
        
        for i in range(random.randint(3, 8)):
            # Random point within cone
            angle = session.view_cone.direction + random.uniform(
                -session.view_cone.aperture_degrees/2,
                session.view_cone.aperture_degrees/2
            )
            distance = random.uniform(50, session.view_cone.range_meters * 0.8)
            
            point = self._destination_point(
                session.position.lat,
                session.position.lng,
                angle,
                distance / 1000
            )
            
            poi_type = random.choice(poi_types)
            config = self.poi_configs.get(poi_type, {})
            
            poi = PointOfInterest(
                lat=point["lat"],
                lng=point["lng"],
                poi_type=poi_type,
                name=f"{poi_type.value.replace('_', ' ').title()} #{i+1}",
                visible_in_cone=True,
                distance_m=distance,
                bearing=angle,
                relative_angle=angle - session.view_cone.direction,
                priority=config.get("priority", 5),
                icon=config.get("icon", "📍"),
                color=config.get("color", "#64748b")
            )
            pois.append(poi)
        
        return pois
    
    async def _get_wind_data(
        self,
        lat: float,
        lng: float,
        heading: float
    ) -> WindData:
        """Get wind data for position"""
        # Placeholder - would integrate with weather service
        import random
        
        # Simulate wind direction
        wind_direction = random.randint(0, 359)
        wind_speed = random.uniform(5, 25)
        
        # Check if favorable (wind in face is good)
        relative_wind = (wind_direction - heading + 180) % 360
        favorable = 135 <= relative_wind <= 225  # Wind coming towards hunter
        
        notes = "Vent favorable - dans la face" if favorable else "Attention - vent dans le dos"
        
        return WindData(
            direction=wind_direction,
            speed_kmh=round(wind_speed, 1),
            gusts_kmh=round(wind_speed * random.uniform(1.1, 1.5), 1),
            favorable=favorable,
            notes=notes
        )
    
    async def _check_for_alerts(self, session: HeadingSession) -> List[HeadingAlert]:
        """Check for conditions that should trigger alerts"""
        alerts = []
        
        # Check wind change
        if session.wind and not session.wind.favorable:
            if not any(a.alert_type == AlertType.WIND_CHANGE for a in session.alerts):
                alerts.append(HeadingAlert(
                    alert_type=AlertType.WIND_CHANGE,
                    priority=AlertPriority.HIGH,
                    title="⚠️ Changement de vent",
                    message=session.wind.notes or "Le vent a changé de direction",
                    icon="💨",
                    color="#f59e0b"
                ))
        
        # Check for nearby high-priority POIs
        for poi in session.visible_pois[:3]:  # Top 3 closest
            if poi.distance_m < 100 and poi.priority >= 8:
                if not any(a.alert_type == AlertType.POI_NEARBY and a.title == poi.name for a in session.alerts):
                    alerts.append(HeadingAlert(
                        alert_type=AlertType.POI_NEARBY,
                        priority=AlertPriority.MEDIUM,
                        title=f"{poi.icon} {poi.name}",
                        message=f"Point d'intérêt à {int(poi.distance_m)}m",
                        lat=poi.lat,
                        lng=poi.lng,
                        distance_m=poi.distance_m,
                        bearing=poi.bearing,
                        icon=poi.icon,
                        color=poi.color
                    ))
        
        return alerts
    
    def _format_duration(self, seconds: int) -> str:
        """Format duration as human readable string"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}min"
        elif minutes > 0:
            return f"{minutes}min {secs}s"
        else:
            return f"{secs}s"
    
    # ===========================================
    # STATS
    # ===========================================
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        return {
            "engine": "live_heading_engine",
            "version": "1.0.0",
            "active_sessions": len(self._active_sessions),
            "total_sessions": self.sessions_collection.count_documents({}),
            "total_pois": self.pois_collection.count_documents({}),
            "poi_types": [t.value for t in POIType],
            "alert_types": [t.value for t in AlertType],
            "status": "operational"
        }


# Singleton instance
_service_instance = None

def get_live_heading_service() -> LiveHeadingService:
    """Get singleton instance"""
    global _service_instance
    if _service_instance is None:
        _service_instance = LiveHeadingService()
    return _service_instance
