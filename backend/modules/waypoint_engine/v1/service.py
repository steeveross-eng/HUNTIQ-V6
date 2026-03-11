"""
Waypoint Engine V1 - Service Layer
===================================
Service for waypoint management.
Architecture LEGO V5 - Module isolé.
"""
from datetime import datetime, timezone
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
import logging
import uuid

from .models import WaypointCreate, WaypointUpdate

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


class WaypointEngineService:
    """Service principal du Waypoint Engine"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.waypoints = db['waypoints']
    
    async def create_waypoint(self, data: WaypointCreate) -> dict:
        """Create a new waypoint"""
        waypoint = {
            "id": str(uuid.uuid4()),
            "lat": data.lat,
            "lng": data.lng,
            "name": data.name or f"Waypoint {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}",
            "description": data.description,
            "timestamp": data.timestamp or datetime.now(timezone.utc).isoformat(),
            "source": data.source,
            "user_id": data.user_id,
            "tags": data.tags,
            "metadata": data.metadata,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await self.waypoints.insert_one(waypoint)
        waypoint.pop("_id", None)
        
        logger.info(f"Created waypoint {waypoint['id']} at {waypoint['lat']}, {waypoint['lng']}")
        return waypoint
    
    async def get_waypoints(
        self,
        user_id: Optional[str] = None,
        source: Optional[str] = None,
        limit: int = 100
    ) -> List[dict]:
        """Get waypoints with optional filters"""
        query = {}
        
        if user_id:
            query["user_id"] = user_id
        if source:
            query["source"] = source
        
        waypoints = await self.waypoints.find(
            query, {"_id": 0}
        ).sort("created_at", -1).limit(limit).to_list(limit)
        
        return waypoints
    
    async def get_waypoint(self, waypoint_id: str) -> Optional[dict]:
        """Get a single waypoint by ID"""
        waypoint = await self.waypoints.find_one({"id": waypoint_id}, {"_id": 0})
        return waypoint
    
    async def update_waypoint(self, waypoint_id: str, data: WaypointUpdate) -> Optional[dict]:
        """Update a waypoint"""
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        
        if not update_data:
            return await self.get_waypoint(waypoint_id)
        
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        result = await self.waypoints.update_one(
            {"id": waypoint_id},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            return await self.get_waypoint(waypoint_id)
        return None
    
    async def delete_waypoint(self, waypoint_id: str) -> bool:
        """Delete a waypoint"""
        result = await self.waypoints.delete_one({"id": waypoint_id})
        return result.deleted_count > 0
    
    async def get_waypoints_in_bounds(
        self,
        north: float,
        south: float,
        east: float,
        west: float,
        user_id: Optional[str] = None,
        limit: int = 500
    ) -> List[dict]:
        """Get waypoints within geographic bounds"""
        query = {
            "lat": {"$gte": south, "$lte": north},
            "lng": {"$gte": west, "$lte": east}
        }
        
        if user_id:
            query["user_id"] = user_id
        
        waypoints = await self.waypoints.find(
            query, {"_id": 0}
        ).limit(limit).to_list(limit)
        
        return waypoints
    
    async def get_stats(self, user_id: Optional[str] = None) -> dict:
        """Get waypoint statistics"""
        query = {}
        if user_id:
            query["user_id"] = user_id
        
        total = await self.waypoints.count_documents(query)
        
        # By source
        by_source_pipeline = [
            {"$match": query},
            {"$group": {"_id": "$source", "count": {"$sum": 1}}}
        ]
        by_source_result = await self.waypoints.aggregate(by_source_pipeline).to_list(None)
        by_source = {r["_id"]: r["count"] for r in by_source_result}
        
        return {
            "total": total,
            "by_source": by_source
        }
