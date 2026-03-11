"""
Tracking Engine - Service Layer V1
===================================
Service for user behavior tracking, events, funnels and heatmaps.
Architecture LEGO V5 - Module isolé.
"""
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
import logging
import re

from .models import (
    TrackingEvent, TrackingEventCreate, EventType,
    Funnel, FunnelCreate, FunnelAnalysis,
    HeatmapData, HeatmapPoint,
    SessionSummary, EngagementMetrics
)

logger = logging.getLogger(__name__)


def serialize_doc(doc: dict) -> dict:
    """Convert MongoDB document to serializable dict"""
    if doc is None:
        return None
    result = dict(doc)
    if "_id" in result:
        result["id"] = str(result.pop("_id"))
    for key, value in result.items():
        if isinstance(value, datetime):
            result[key] = value.isoformat()
        elif isinstance(value, ObjectId):
            result[key] = str(value)
    return result


class TrackingEngineService:
    """Service principal du Tracking Engine"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.events_collection = db['tracking_events']
        self.sessions_collection = db['tracking_sessions']
        self.funnels_collection = db['tracking_funnels']
    
    # ============================================
    # EVENTS
    # ============================================
    
    async def track_event(self, event_data: TrackingEventCreate, ip_address: Optional[str] = None) -> TrackingEvent:
        """Enregistre un événement de tracking"""
        event = TrackingEvent(
            **event_data.model_dump(),
            ip_address=ip_address
        )
        
        doc = event.model_dump()
        doc.pop("id", None)
        
        result = await self.events_collection.insert_one(doc)
        logger.info(f"Tracked event: {event.event_type} - {event.event_name}")
        
        return event
    
    async def batch_track_events(self, events: List[TrackingEventCreate], ip_address: Optional[str] = None) -> int:
        """Enregistre plusieurs événements en batch"""
        docs = []
        for event_data in events:
            event = TrackingEvent(**event_data.model_dump(), ip_address=ip_address)
            doc = event.model_dump()
            doc.pop("id", None)
            docs.append(doc)
        
        if docs:
            result = await self.events_collection.insert_many(docs)
            logger.info(f"Batch tracked {len(result.inserted_ids)} events")
            return len(result.inserted_ids)
        return 0
    
    async def get_events(
        self,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        event_type: Optional[EventType] = None,
        page_url: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[dict]:
        """Récupère les événements avec filtres"""
        query = {}
        
        if session_id:
            query["session_id"] = session_id
        if user_id:
            query["user_id"] = user_id
        if event_type:
            query["event_type"] = event_type.value
        if page_url:
            query["page_url"] = {"$regex": page_url, "$options": "i"}
        
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date
        
        cursor = self.events_collection.find(query).sort("timestamp", -1).limit(limit)
        events = await cursor.to_list(length=limit)
        
        return [serialize_doc(e) for e in events]
    
    # ============================================
    # FUNNELS
    # ============================================
    
    async def create_funnel(self, funnel_data: FunnelCreate) -> Funnel:
        """Crée un nouveau funnel de conversion"""
        funnel = Funnel(**funnel_data.model_dump())
        
        doc = funnel.model_dump()
        doc.pop("id", None)
        
        result = await self.funnels_collection.insert_one(doc)
        funnel.id = str(result.inserted_id)
        
        logger.info(f"Created funnel: {funnel.name}")
        return funnel
    
    async def get_funnels(self, active_only: bool = True) -> List[dict]:
        """Récupère tous les funnels"""
        query = {"is_active": True} if active_only else {}
        cursor = self.funnels_collection.find(query).sort("created_at", -1)
        funnels = await cursor.to_list(length=100)
        return [serialize_doc(f) for f in funnels]
    
    async def get_funnel(self, funnel_id: str) -> Optional[dict]:
        """Récupère un funnel par ID"""
        funnel = await self.funnels_collection.find_one({"_id": ObjectId(funnel_id)})
        return serialize_doc(funnel)
    
    async def delete_funnel(self, funnel_id: str) -> bool:
        """Supprime un funnel"""
        result = await self.funnels_collection.delete_one({"_id": ObjectId(funnel_id)})
        return result.deleted_count > 0
    
    async def analyze_funnel(
        self,
        funnel_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> FunnelAnalysis:
        """Analyse les performances d'un funnel"""
        funnel = await self.get_funnel(funnel_id)
        if not funnel:
            raise ValueError(f"Funnel {funnel_id} not found")
        
        steps = funnel.get("steps", [])
        if not steps:
            return FunnelAnalysis(
                funnel_id=funnel_id,
                funnel_name=funnel.get("name", ""),
                total_started=0,
                total_completed=0,
                conversion_rate=0.0,
                steps_analysis=[]
            )
        
        # Build date query
        date_query = {}
        if start_date or end_date:
            date_query["timestamp"] = {}
            if start_date:
                date_query["timestamp"]["$gte"] = start_date
            if end_date:
                date_query["timestamp"]["$lte"] = end_date
        
        # Analyze each step
        steps_analysis = []
        sessions_at_step = set()
        first_step_sessions = set()
        
        for i, step in enumerate(steps):
            step_query = {"event_name": step.get("event_name"), **date_query}
            
            if step.get("event_type"):
                step_query["event_type"] = step["event_type"]
            
            if step.get("page_url_pattern"):
                step_query["page_url"] = {"$regex": step["page_url_pattern"], "$options": "i"}
            
            # Get unique sessions at this step
            pipeline = [
                {"$match": step_query},
                {"$group": {"_id": "$session_id"}}
            ]
            
            result = await self.events_collection.aggregate(pipeline).to_list(length=None)
            current_sessions = {r["_id"] for r in result}
            
            if i == 0:
                first_step_sessions = current_sessions
                sessions_at_step = current_sessions
            else:
                # Only count sessions that were in previous step
                sessions_at_step = sessions_at_step & current_sessions
            
            steps_analysis.append({
                "step_number": step.get("step_number", i + 1),
                "event_name": step.get("event_name"),
                "sessions_count": len(sessions_at_step),
                "drop_off_rate": round(
                    ((len(first_step_sessions) - len(sessions_at_step)) / max(len(first_step_sessions), 1)) * 100, 2
                ) if i > 0 else 0
            })
        
        total_started = len(first_step_sessions)
        total_completed = len(sessions_at_step)
        
        return FunnelAnalysis(
            funnel_id=funnel_id,
            funnel_name=funnel.get("name", ""),
            total_started=total_started,
            total_completed=total_completed,
            conversion_rate=round((total_completed / max(total_started, 1)) * 100, 2),
            steps_analysis=steps_analysis
        )
    
    # ============================================
    # HEATMAPS
    # ============================================
    
    async def get_heatmap_data(
        self,
        page_url: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        viewport_width: int = 1920,
        viewport_height: int = 1080
    ) -> HeatmapData:
        """Génère les données de heatmap pour une page"""
        query = {
            "event_type": EventType.CLICK.value,
            "page_url": {"$regex": f"^{re.escape(page_url)}", "$options": "i"},
            "position_x": {"$ne": None},
            "position_y": {"$ne": None}
        }
        
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date
        
        # Aggregate clicks by position
        pipeline = [
            {"$match": query},
            {"$group": {
                "_id": {
                    "x": {"$round": [{"$divide": ["$position_x", 10]}, 0]},
                    "y": {"$round": [{"$divide": ["$position_y", 10]}, 0]}
                },
                "count": {"$sum": 1}
            }}
        ]
        
        results = await self.events_collection.aggregate(pipeline).to_list(length=None)
        
        points = []
        total_clicks = 0
        
        for r in results:
            x = int(r["_id"]["x"]) * 10
            y = int(r["_id"]["y"]) * 10
            count = r["count"]
            total_clicks += count
            points.append(HeatmapPoint(x=x, y=y, value=count))
        
        # Get page title from most recent event
        page_event = await self.events_collection.find_one(
            {"page_url": {"$regex": f"^{re.escape(page_url)}", "$options": "i"}},
            {"page_title": 1}
        )
        
        return HeatmapData(
            page_url=page_url,
            page_title=page_event.get("page_title") if page_event else None,
            viewport_width=viewport_width,
            viewport_height=viewport_height,
            total_clicks=total_clicks,
            points=points
        )
    
    # ============================================
    # SESSIONS & ENGAGEMENT
    # ============================================
    
    async def get_session_summary(self, session_id: str) -> Optional[SessionSummary]:
        """Récupère le résumé d'une session"""
        events = await self.events_collection.find(
            {"session_id": session_id}
        ).sort("timestamp", 1).to_list(length=1000)
        
        if not events:
            return None
        
        first_event = events[0]
        last_event = events[-1]
        
        page_views = sum(1 for e in events if e.get("event_type") == EventType.PAGE_VIEW.value)
        pages_visited = list(set(
            e.get("page_url") for e in events 
            if e.get("page_url") and e.get("event_type") == EventType.PAGE_VIEW.value
        ))
        
        started_at = first_event.get("timestamp")
        ended_at = last_event.get("timestamp")
        duration = None
        
        if started_at and ended_at:
            if hasattr(started_at, 'timestamp') and hasattr(ended_at, 'timestamp'):
                duration = int((ended_at - started_at).total_seconds())
        
        return SessionSummary(
            session_id=session_id,
            user_id=first_event.get("user_id"),
            started_at=started_at,
            ended_at=ended_at,
            duration_seconds=duration,
            page_views=page_views,
            total_events=len(events),
            pages_visited=pages_visited,
            device_type=first_event.get("device_type"),
            country=first_event.get("country")
        )
    
    async def get_engagement_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> EngagementMetrics:
        """Calcule les métriques d'engagement globales"""
        if not start_date:
            start_date = datetime.now(timezone.utc) - timedelta(days=30)
        if not end_date:
            end_date = datetime.now(timezone.utc)
        
        date_query = {"timestamp": {"$gte": start_date, "$lte": end_date}}
        
        # Basic counts
        total_events = await self.events_collection.count_documents(date_query)
        
        # Unique sessions and users
        sessions_pipeline = [
            {"$match": date_query},
            {"$group": {"_id": "$session_id"}}
        ]
        sessions_result = await self.events_collection.aggregate(sessions_pipeline).to_list(length=None)
        total_sessions = len(sessions_result)
        
        users_pipeline = [
            {"$match": {**date_query, "user_id": {"$ne": None}}},
            {"$group": {"_id": "$user_id"}}
        ]
        users_result = await self.events_collection.aggregate(users_pipeline).to_list(length=None)
        unique_users = len(users_result)
        
        # Page views
        page_views_query = {**date_query, "event_type": EventType.PAGE_VIEW.value}
        total_page_views = await self.events_collection.count_documents(page_views_query)
        
        # Top pages
        top_pages_pipeline = [
            {"$match": page_views_query},
            {"$group": {"_id": "$page_url", "views": {"$sum": 1}}},
            {"$sort": {"views": -1}},
            {"$limit": 10}
        ]
        top_pages_result = await self.events_collection.aggregate(top_pages_pipeline).to_list(length=10)
        top_pages = [{"page_url": r["_id"], "views": r["views"]} for r in top_pages_result]
        
        # Top events
        top_events_pipeline = [
            {"$match": date_query},
            {"$group": {"_id": {"type": "$event_type", "name": "$event_name"}, "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        top_events_result = await self.events_collection.aggregate(top_events_pipeline).to_list(length=10)
        top_events = [
            {"event_type": r["_id"]["type"], "event_name": r["_id"]["name"], "count": r["count"]}
            for r in top_events_result
        ]
        
        # Device breakdown
        device_pipeline = [
            {"$match": {**date_query, "device_type": {"$ne": None}}},
            {"$group": {"_id": "$device_type", "count": {"$sum": 1}}}
        ]
        device_result = await self.events_collection.aggregate(device_pipeline).to_list(length=None)
        device_breakdown = {r["_id"]: r["count"] for r in device_result}
        
        # Country breakdown
        country_pipeline = [
            {"$match": {**date_query, "country": {"$ne": None}}},
            {"$group": {"_id": "$country", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 20}
        ]
        country_result = await self.events_collection.aggregate(country_pipeline).to_list(length=20)
        country_breakdown = {r["_id"]: r["count"] for r in country_result}
        
        # Calculate averages
        pages_per_session = round(total_page_views / max(total_sessions, 1), 2)
        
        # Bounce rate (sessions with only 1 page view)
        bounce_pipeline = [
            {"$match": page_views_query},
            {"$group": {"_id": "$session_id", "page_count": {"$sum": 1}}},
            {"$match": {"page_count": 1}}
        ]
        bounce_result = await self.events_collection.aggregate(bounce_pipeline).to_list(length=None)
        bounce_rate = round((len(bounce_result) / max(total_sessions, 1)) * 100, 2)
        
        return EngagementMetrics(
            total_sessions=total_sessions,
            total_page_views=total_page_views,
            total_events=total_events,
            unique_users=unique_users,
            avg_session_duration=0,  # Would need session end tracking
            bounce_rate=bounce_rate,
            pages_per_session=pages_per_session,
            top_pages=top_pages,
            top_events=top_events,
            device_breakdown=device_breakdown,
            country_breakdown=country_breakdown,
            time_range_start=start_date,
            time_range_end=end_date
        )
    
    # ============================================
    # DEMO DATA
    # ============================================
    
    async def seed_demo_data(self) -> int:
        """Génère des données de démonstration"""
        import random
        
        pages = [
            "/", "/map", "/analytics", "/profile", "/settings",
            "/territories", "/species/moose", "/species/deer", "/species/bear"
        ]
        
        event_types_weights = [
            (EventType.PAGE_VIEW, 40),
            (EventType.CLICK, 30),
            (EventType.SCROLL, 15),
            (EventType.SEARCH, 5),
            (EventType.MAP_INTERACTION, 8),
            (EventType.FEATURE_USE, 2)
        ]
        
        devices = ["desktop", "mobile", "tablet"]
        countries = ["CA", "US", "FR", "BE", "CH"]
        
        events = []
        now = datetime.now(timezone.utc)
        
        # Generate 30 sessions
        for session_num in range(30):
            session_id = f"demo-session-{session_num}"
            user_id = f"demo-user-{session_num % 10}" if random.random() > 0.3 else None
            device = random.choice(devices)
            country = random.choice(countries)
            
            # Each session has 5-20 events
            num_events = random.randint(5, 20)
            session_start = now - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
            
            for event_num in range(num_events):
                event_type = random.choices(
                    [et for et, _ in event_types_weights],
                    weights=[w for _, w in event_types_weights]
                )[0]
                
                page = random.choice(pages)
                
                event = {
                    "session_id": session_id,
                    "user_id": user_id,
                    "event_type": event_type.value,
                    "event_name": f"{event_type.value}_{page.replace('/', '_')}",
                    "page_url": f"https://huntiq.com{page}",
                    "page_title": f"BIONIC HUNT/Chasse - {page.replace('/', ' ').title()}",
                    "position_x": random.randint(0, 1920) if event_type == EventType.CLICK else None,
                    "position_y": random.randint(0, 1080) if event_type == EventType.CLICK else None,
                    "viewport_width": 1920 if device == "desktop" else 375,
                    "viewport_height": 1080 if device == "desktop" else 812,
                    "device_type": device,
                    "country": country,
                    "browser": random.choice(["Chrome", "Firefox", "Safari", "Edge"]),
                    "timestamp": session_start + timedelta(seconds=event_num * random.randint(5, 60))
                }
                events.append(event)
        
        if events:
            result = await self.events_collection.insert_many(events)
            logger.info(f"Seeded {len(result.inserted_ids)} demo tracking events")
            return len(result.inserted_ids)
        
        return 0
