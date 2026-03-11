"""Networking Engine Service - PLAN MAITRE
Business logic for hunter social network.

Version: 1.0.0
"""

import os
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from pymongo import MongoClient

from .models import (
    PublicProfile, Connection, ConnectionStatus,
    Post, PostType, Comment, CommunityEvent, EventRegistration
)


class NetworkingService:
    """Service for social networking"""
    
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'test_database')
        self._client = None
        self._db = None
    
    @property
    def db(self):
        if self._db is None:
            self._client = MongoClient(self.mongo_url)
            self._db = self._client[self.db_name]
        return self._db
    
    @property
    def profiles_collection(self):
        return self.db.public_profiles
    
    @property
    def connections_collection(self):
        return self.db.connections
    
    @property
    def posts_collection(self):
        return self.db.posts
    
    @property
    def comments_collection(self):
        return self.db.post_comments
    
    @property
    def events_collection(self):
        return self.db.community_events
    
    @property
    def registrations_collection(self):
        return self.db.event_registrations
    
    # ==========================================
    # Profiles
    # ==========================================
    
    async def get_profile(self, user_id: str) -> Optional[PublicProfile]:
        """Get public profile"""
        profile_dict = self.profiles_collection.find_one(
            {"user_id": user_id}, {"_id": 0}
        )
        if profile_dict:
            return PublicProfile(**profile_dict)
        return None
    
    async def create_or_update_profile(
        self,
        user_id: str,
        profile_data: Dict[str, Any]
    ) -> PublicProfile:
        """Create or update public profile"""
        profile_data["user_id"] = user_id
        profile_data["updated_at"] = datetime.now(timezone.utc)
        
        self.profiles_collection.update_one(
            {"user_id": user_id},
            {"$set": profile_data},
            upsert=True
        )
        
        return await self.get_profile(user_id)
    
    async def search_profiles(
        self,
        query: str,
        limit: int = 20
    ) -> List[PublicProfile]:
        """Search profiles by name"""
        profiles = list(self.profiles_collection.find({
            "is_public": True,
            "display_name": {"$regex": query, "$options": "i"}
        }, {"_id": 0}).limit(limit))
        
        return [PublicProfile(**p) for p in profiles]
    
    # ==========================================
    # Connections
    # ==========================================
    
    async def send_connection_request(
        self,
        requester_id: str,
        recipient_id: str
    ) -> Connection:
        """Send connection request"""
        # Check if connection exists
        existing = self.connections_collection.find_one({
            "$or": [
                {"requester_id": requester_id, "recipient_id": recipient_id},
                {"requester_id": recipient_id, "recipient_id": requester_id}
            ]
        })
        
        if existing:
            return Connection(**existing)
        
        connection = Connection(
            requester_id=requester_id,
            recipient_id=recipient_id
        )
        
        conn_dict = connection.model_dump()
        conn_dict.pop("_id", None)
        self.connections_collection.insert_one(conn_dict)
        
        return connection
    
    async def respond_to_connection(
        self,
        connection_id: str,
        accept: bool
    ) -> Optional[Connection]:
        """Accept or decline connection request"""
        status = ConnectionStatus.ACCEPTED if accept else ConnectionStatus.BLOCKED
        
        update_data = {"status": status.value}
        if accept:
            update_data["accepted_at"] = datetime.now(timezone.utc)
        
        self.connections_collection.update_one(
            {"id": connection_id},
            {"$set": update_data}
        )
        
        # Update connection counts if accepted
        if accept:
            conn = self.connections_collection.find_one({"id": connection_id})
            if conn:
                self.profiles_collection.update_one(
                    {"user_id": conn["requester_id"]},
                    {"$inc": {"connection_count": 1}}
                )
                self.profiles_collection.update_one(
                    {"user_id": conn["recipient_id"]},
                    {"$inc": {"connection_count": 1}}
                )
        
        conn_dict = self.connections_collection.find_one(
            {"id": connection_id}, {"_id": 0}
        )
        if conn_dict:
            return Connection(**conn_dict)
        return None
    
    async def get_connections(
        self,
        user_id: str,
        status: Optional[str] = None
    ) -> List[Connection]:
        """Get user's connections"""
        query = {
            "$or": [
                {"requester_id": user_id},
                {"recipient_id": user_id}
            ]
        }
        
        if status:
            query["status"] = status
        
        connections = list(self.connections_collection.find(query, {"_id": 0}))
        return [Connection(**c) for c in connections]
    
    async def get_pending_requests(self, user_id: str) -> List[Connection]:
        """Get pending connection requests for user"""
        requests = list(self.connections_collection.find({
            "recipient_id": user_id,
            "status": ConnectionStatus.PENDING.value
        }, {"_id": 0}))
        
        return [Connection(**r) for r in requests]
    
    # ==========================================
    # Posts
    # ==========================================
    
    async def create_post(
        self,
        author_id: str,
        author_name: str,
        content: str,
        post_type: str = "text",
        media_urls: Optional[List[str]] = None,
        author_avatar: Optional[str] = None,
        **kwargs
    ) -> Post:
        """Create a new post"""
        post = Post(
            author_id=author_id,
            author_name=author_name,
            author_avatar=author_avatar,
            post_type=PostType(post_type),
            content=content,
            media_urls=media_urls or [],
            **kwargs
        )
        
        post_dict = post.model_dump()
        post_dict.pop("_id", None)
        self.posts_collection.insert_one(post_dict)
        
        # Update post count
        self.profiles_collection.update_one(
            {"user_id": author_id},
            {"$inc": {"post_count": 1}}
        )
        
        return post
    
    async def get_post(self, post_id: str) -> Optional[Post]:
        """Get a post by ID"""
        post_dict = self.posts_collection.find_one({"id": post_id}, {"_id": 0})
        if post_dict:
            return Post(**post_dict)
        return None
    
    async def get_feed(
        self,
        user_id: str,
        limit: int = 50,
        skip: int = 0
    ) -> List[Post]:
        """Get user's feed"""
        # Get user's connections
        connections = await self.get_connections(user_id, ConnectionStatus.ACCEPTED.value)
        connected_ids = set()
        
        for conn in connections:
            if conn.requester_id == user_id:
                connected_ids.add(conn.recipient_id)
            else:
                connected_ids.add(conn.requester_id)
        
        # Include own posts and public posts from connections
        query = {
            "$or": [
                {"author_id": user_id},
                {"author_id": {"$in": list(connected_ids)}},
                {"visibility": "public"}
            ]
        }
        
        posts = list(self.posts_collection.find(
            query, {"_id": 0}
        ).sort("created_at", -1).skip(skip).limit(limit))
        
        return [Post(**p) for p in posts]
    
    async def get_user_posts(
        self,
        user_id: str,
        limit: int = 20
    ) -> List[Post]:
        """Get posts by a specific user"""
        posts = list(self.posts_collection.find(
            {"author_id": user_id}, {"_id": 0}
        ).sort("created_at", -1).limit(limit))
        
        return [Post(**p) for p in posts]
    
    async def like_post(self, post_id: str, user_id: str) -> bool:
        """Like a post"""
        result = self.posts_collection.update_one(
            {"id": post_id},
            {"$inc": {"likes_count": 1}}
        )
        return result.modified_count > 0
    
    async def add_comment(
        self,
        post_id: str,
        author_id: str,
        author_name: str,
        content: str,
        author_avatar: Optional[str] = None
    ) -> Comment:
        """Add comment to post"""
        comment = Comment(
            post_id=post_id,
            author_id=author_id,
            author_name=author_name,
            author_avatar=author_avatar,
            content=content
        )
        
        comment_dict = comment.model_dump()
        comment_dict.pop("_id", None)
        self.comments_collection.insert_one(comment_dict)
        
        # Update comment count
        self.posts_collection.update_one(
            {"id": post_id},
            {"$inc": {"comments_count": 1}}
        )
        
        return comment
    
    async def get_post_comments(
        self,
        post_id: str,
        limit: int = 50
    ) -> List[Comment]:
        """Get comments on a post"""
        comments = list(self.comments_collection.find(
            {"post_id": post_id}, {"_id": 0}
        ).sort("created_at", 1).limit(limit))
        
        return [Comment(**c) for c in comments]
    
    # ==========================================
    # Events
    # ==========================================
    
    async def create_event(
        self,
        organizer_id: str,
        organizer_name: str,
        event_data: Dict[str, Any]
    ) -> CommunityEvent:
        """Create a community event"""
        event = CommunityEvent(
            organizer_id=organizer_id,
            organizer_name=organizer_name,
            **event_data
        )
        
        event_dict = event.model_dump()
        event_dict.pop("_id", None)
        self.events_collection.insert_one(event_dict)
        
        return event
    
    async def get_upcoming_events(
        self,
        limit: int = 20,
        event_type: Optional[str] = None
    ) -> List[CommunityEvent]:
        """Get upcoming events"""
        query = {
            "status": "upcoming",
            "start_date": {"$gte": datetime.now(timezone.utc)}
        }
        
        if event_type:
            query["event_type"] = event_type
        
        events = list(self.events_collection.find(
            query, {"_id": 0}
        ).sort("start_date", 1).limit(limit))
        
        return [CommunityEvent(**e) for e in events]
    
    async def register_for_event(
        self,
        event_id: str,
        user_id: str
    ) -> EventRegistration:
        """Register for an event"""
        # Check capacity
        event = self.events_collection.find_one({"id": event_id})
        if event and event.get("max_participants"):
            if event["current_participants"] >= event["max_participants"]:
                # Add to waitlist
                registration = EventRegistration(
                    event_id=event_id,
                    user_id=user_id,
                    status="waitlist"
                )
            else:
                registration = EventRegistration(
                    event_id=event_id,
                    user_id=user_id
                )
        else:
            registration = EventRegistration(
                event_id=event_id,
                user_id=user_id
            )
        
        reg_dict = registration.model_dump()
        reg_dict.pop("_id", None)
        self.registrations_collection.insert_one(reg_dict)
        
        # Update participant count
        if registration.status == "registered":
            self.events_collection.update_one(
                {"id": event_id},
                {"$inc": {"current_participants": 1}}
            )
        
        return registration
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get networking engine statistics"""
        return {
            "total_profiles": self.profiles_collection.count_documents({}),
            "total_connections": self.connections_collection.count_documents({
                "status": ConnectionStatus.ACCEPTED.value
            }),
            "total_posts": self.posts_collection.count_documents({}),
            "total_events": self.events_collection.count_documents({})
        }
