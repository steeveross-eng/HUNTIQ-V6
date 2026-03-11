"""Collaborative Engine Service - PLAN MAITRE
Business logic for hunter collaboration system.

Version: 1.0.0
"""

import os
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from pymongo import MongoClient

from .models import (
    HuntingGroup, GroupMember, GroupRole, GroupStatus,
    SharedSpot, GroupEvent, GroupInvitation, InvitationStatus,
    ChatMessage, PositionShare,
    GroupCreateRequest, GroupUpdateRequest
)


class CollaborativeService:
    """Service for hunter collaboration"""
    
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'test_database')
        self._client = None
        self._db = None
    
    @property
    def db(self):
        """Lazy database connection"""
        if self._db is None:
            self._client = MongoClient(self.mongo_url)
            self._db = self._client[self.db_name]
        return self._db
    
    @property
    def groups_collection(self):
        return self.db.hunting_groups
    
    @property
    def members_collection(self):
        return self.db.group_members
    
    @property
    def spots_collection(self):
        return self.db.group_spots
    
    @property
    def events_collection(self):
        return self.db.group_events
    
    @property
    def invitations_collection(self):
        return self.db.group_invitations
    
    @property
    def messages_collection(self):
        return self.db.group_messages
    
    @property
    def positions_collection(self):
        return self.db.group_positions
    
    # ==========================================
    # Group Management
    # ==========================================
    
    async def create_group(
        self,
        owner_id: str,
        owner_name: str,
        request: GroupCreateRequest
    ) -> HuntingGroup:
        """Create a new hunting group"""
        group = HuntingGroup(
            name=request.name,
            description=request.description,
            owner_id=owner_id,
            is_private=request.is_private,
            max_members=request.max_members,
            primary_region=request.primary_region,
            member_count=1
        )
        
        group_dict = group.model_dump()
        group_dict.pop("_id", None)
        self.groups_collection.insert_one(group_dict)
        
        # Add owner as member
        owner_member = GroupMember(
            group_id=group.id,
            user_id=owner_id,
            user_name=owner_name,
            role=GroupRole.OWNER,
            can_invite=True,
            can_edit_spots=True,
            can_manage_events=True
        )
        
        member_dict = owner_member.model_dump()
        member_dict.pop("_id", None)
        self.members_collection.insert_one(member_dict)
        
        return group
    
    async def get_group(self, group_id: str) -> Optional[HuntingGroup]:
        """Get group by ID"""
        group_dict = self.groups_collection.find_one({"id": group_id}, {"_id": 0})
        if group_dict:
            return HuntingGroup(**group_dict)
        return None
    
    async def update_group(
        self,
        group_id: str,
        update: GroupUpdateRequest
    ) -> Optional[HuntingGroup]:
        """Update group settings"""
        update_dict = {k: v for k, v in update.model_dump().items() if v is not None}
        if not update_dict:
            return await self.get_group(group_id)
        
        update_dict["updated_at"] = datetime.now(timezone.utc)
        
        self.groups_collection.update_one(
            {"id": group_id},
            {"$set": update_dict}
        )
        
        return await self.get_group(group_id)
    
    async def delete_group(self, group_id: str) -> bool:
        """Archive a group"""
        result = self.groups_collection.update_one(
            {"id": group_id},
            {"$set": {"status": GroupStatus.ARCHIVED.value}}
        )
        return result.modified_count > 0
    
    async def get_user_groups(self, user_id: str) -> List[HuntingGroup]:
        """Get all groups a user belongs to"""
        memberships = list(self.members_collection.find(
            {"user_id": user_id},
            {"group_id": 1, "_id": 0}
        ))
        
        group_ids = [m["group_id"] for m in memberships]
        
        groups = list(self.groups_collection.find(
            {"id": {"$in": group_ids}, "status": GroupStatus.ACTIVE.value},
            {"_id": 0}
        ))
        
        return [HuntingGroup(**g) for g in groups]
    
    # ==========================================
    # Member Management
    # ==========================================
    
    async def get_group_members(self, group_id: str) -> List[GroupMember]:
        """Get all members of a group"""
        members = list(self.members_collection.find(
            {"group_id": group_id},
            {"_id": 0}
        ))
        return [GroupMember(**m) for m in members]
    
    async def add_member(
        self,
        group_id: str,
        user_id: str,
        user_name: str,
        role: GroupRole = GroupRole.MEMBER
    ) -> GroupMember:
        """Add a member to a group"""
        member = GroupMember(
            group_id=group_id,
            user_id=user_id,
            user_name=user_name,
            role=role
        )
        
        member_dict = member.model_dump()
        member_dict.pop("_id", None)
        self.members_collection.insert_one(member_dict)
        
        # Update member count
        self.groups_collection.update_one(
            {"id": group_id},
            {"$inc": {"member_count": 1}}
        )
        
        return member
    
    async def remove_member(self, group_id: str, user_id: str) -> bool:
        """Remove a member from a group"""
        result = self.members_collection.delete_one({
            "group_id": group_id,
            "user_id": user_id
        })
        
        if result.deleted_count > 0:
            self.groups_collection.update_one(
                {"id": group_id},
                {"$inc": {"member_count": -1}}
            )
            return True
        return False
    
    async def update_member_role(
        self,
        group_id: str,
        user_id: str,
        new_role: GroupRole
    ) -> Optional[GroupMember]:
        """Update a member's role"""
        permissions = {
            GroupRole.OWNER: {"can_invite": True, "can_edit_spots": True, "can_manage_events": True},
            GroupRole.ADMIN: {"can_invite": True, "can_edit_spots": True, "can_manage_events": True},
            GroupRole.MEMBER: {"can_invite": False, "can_edit_spots": False, "can_manage_events": False},
            GroupRole.GUEST: {"can_invite": False, "can_edit_spots": False, "can_manage_events": False}
        }
        
        update_data = {"role": new_role.value, **permissions.get(new_role, {})}
        
        self.members_collection.update_one(
            {"group_id": group_id, "user_id": user_id},
            {"$set": update_data}
        )
        
        member_dict = self.members_collection.find_one(
            {"group_id": group_id, "user_id": user_id},
            {"_id": 0}
        )
        
        if member_dict:
            return GroupMember(**member_dict)
        return None
    
    # ==========================================
    # Spots Management
    # ==========================================
    
    async def create_spot(
        self,
        group_id: str,
        created_by: str,
        spot_data: Dict[str, Any]
    ) -> SharedSpot:
        """Create a shared hunting spot"""
        spot = SharedSpot(
            group_id=group_id,
            created_by=created_by,
            **spot_data
        )
        
        spot_dict = spot.model_dump()
        spot_dict.pop("_id", None)
        self.spots_collection.insert_one(spot_dict)
        
        # Update spot count
        self.groups_collection.update_one(
            {"id": group_id},
            {"$inc": {"spot_count": 1}}
        )
        
        return spot
    
    async def get_group_spots(self, group_id: str) -> List[SharedSpot]:
        """Get all spots in a group"""
        spots = list(self.spots_collection.find(
            {"group_id": group_id, "is_active": True},
            {"_id": 0}
        ))
        return [SharedSpot(**s) for s in spots]
    
    async def update_spot(
        self,
        spot_id: str,
        update_data: Dict[str, Any]
    ) -> Optional[SharedSpot]:
        """Update a spot"""
        update_data["updated_at"] = datetime.now(timezone.utc)
        
        self.spots_collection.update_one(
            {"id": spot_id},
            {"$set": update_data}
        )
        
        spot_dict = self.spots_collection.find_one({"id": spot_id}, {"_id": 0})
        if spot_dict:
            return SharedSpot(**spot_dict)
        return None
    
    async def delete_spot(self, spot_id: str, group_id: str) -> bool:
        """Soft delete a spot"""
        result = self.spots_collection.update_one(
            {"id": spot_id},
            {"$set": {"is_active": False}}
        )
        
        if result.modified_count > 0:
            self.groups_collection.update_one(
                {"id": group_id},
                {"$inc": {"spot_count": -1}}
            )
            return True
        return False
    
    # ==========================================
    # Calendar/Events
    # ==========================================
    
    async def create_event(
        self,
        group_id: str,
        created_by: str,
        event_data: Dict[str, Any]
    ) -> GroupEvent:
        """Create a group event"""
        event = GroupEvent(
            group_id=group_id,
            created_by=created_by,
            **event_data
        )
        
        event_dict = event.model_dump()
        event_dict.pop("_id", None)
        self.events_collection.insert_one(event_dict)
        
        # Update event count
        self.groups_collection.update_one(
            {"id": group_id},
            {"$inc": {"event_count": 1}}
        )
        
        return event
    
    async def get_group_events(
        self,
        group_id: str,
        upcoming_only: bool = True
    ) -> List[GroupEvent]:
        """Get group events"""
        query = {"group_id": group_id}
        
        if upcoming_only:
            query["start_date"] = {"$gte": datetime.now(timezone.utc)}
        
        events = list(self.events_collection.find(
            query,
            {"_id": 0}
        ).sort("start_date", 1))
        
        return [GroupEvent(**e) for e in events]
    
    async def join_event(
        self,
        event_id: str,
        user_id: str
    ) -> bool:
        """Join a group event"""
        result = self.events_collection.update_one(
            {"id": event_id},
            {
                "$addToSet": {"participants": user_id},
                "$inc": {"confirmed_count": 1}
            }
        )
        return result.modified_count > 0
    
    async def leave_event(
        self,
        event_id: str,
        user_id: str
    ) -> bool:
        """Leave a group event"""
        result = self.events_collection.update_one(
            {"id": event_id},
            {
                "$pull": {"participants": user_id},
                "$inc": {"confirmed_count": -1}
            }
        )
        return result.modified_count > 0
    
    # ==========================================
    # Invitations
    # ==========================================
    
    async def create_invitation(
        self,
        group_id: str,
        group_name: str,
        invited_by: str,
        invited_user_id: Optional[str] = None,
        invited_email: Optional[str] = None,
        message: Optional[str] = None
    ) -> GroupInvitation:
        """Create an invitation"""
        invitation = GroupInvitation(
            group_id=group_id,
            group_name=group_name,
            invited_by=invited_by,
            invited_user_id=invited_user_id,
            invited_email=invited_email,
            message=message,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )
        
        invitation_dict = invitation.model_dump()
        invitation_dict.pop("_id", None)
        self.invitations_collection.insert_one(invitation_dict)
        
        return invitation
    
    async def get_user_invitations(self, user_id: str) -> List[GroupInvitation]:
        """Get pending invitations for a user"""
        invitations = list(self.invitations_collection.find({
            "invited_user_id": user_id,
            "status": InvitationStatus.PENDING.value,
            "expires_at": {"$gt": datetime.now(timezone.utc)}
        }, {"_id": 0}))
        
        return [GroupInvitation(**i) for i in invitations]
    
    async def respond_to_invitation(
        self,
        invitation_id: str,
        accept: bool,
        user_id: str,
        user_name: str
    ) -> Dict[str, Any]:
        """Accept or decline an invitation"""
        status = InvitationStatus.ACCEPTED if accept else InvitationStatus.DECLINED
        
        invitation = self.invitations_collection.find_one_and_update(
            {"id": invitation_id},
            {
                "$set": {
                    "status": status.value,
                    "responded_at": datetime.now(timezone.utc)
                }
            },
            return_document=True
        )
        
        if not invitation:
            return {"success": False, "error": "Invitation not found"}
        
        if accept:
            # Add user to group
            await self.add_member(
                invitation["group_id"],
                user_id,
                user_name
            )
        
        return {
            "success": True,
            "accepted": accept,
            "group_id": invitation["group_id"] if accept else None
        }
    
    # ==========================================
    # Chat
    # ==========================================
    
    async def send_message(
        self,
        group_id: str,
        sender_id: str,
        sender_name: str,
        content: str,
        message_type: str = "text"
    ) -> ChatMessage:
        """Send a chat message"""
        message = ChatMessage(
            group_id=group_id,
            sender_id=sender_id,
            sender_name=sender_name,
            message_type=message_type,
            content=content
        )
        
        message_dict = message.model_dump()
        message_dict.pop("_id", None)
        self.messages_collection.insert_one(message_dict)
        
        return message
    
    async def get_chat_messages(
        self,
        group_id: str,
        limit: int = 50,
        before: Optional[datetime] = None
    ) -> List[ChatMessage]:
        """Get chat messages"""
        query = {"group_id": group_id, "is_deleted": False}
        
        if before:
            query["created_at"] = {"$lt": before}
        
        messages = list(self.messages_collection.find(
            query,
            {"_id": 0}
        ).sort("created_at", -1).limit(limit))
        
        return [ChatMessage(**m) for m in messages]
    
    # ==========================================
    # Position Sharing
    # ==========================================
    
    async def update_position(
        self,
        group_id: str,
        user_id: str,
        user_name: str,
        coordinates: Dict[str, float],
        status: str = "hunting"
    ) -> PositionShare:
        """Update user's shared position"""
        position = PositionShare(
            group_id=group_id,
            user_id=user_id,
            user_name=user_name,
            coordinates=coordinates,
            status=status
        )
        
        position_dict = position.model_dump()
        position_dict.pop("_id", None)
        
        self.positions_collection.update_one(
            {"group_id": group_id, "user_id": user_id},
            {"$set": position_dict},
            upsert=True
        )
        
        return position
    
    async def get_group_positions(self, group_id: str) -> List[PositionShare]:
        """Get all active positions in a group"""
        # Only get positions updated in the last 30 minutes
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=30)
        
        positions = list(self.positions_collection.find({
            "group_id": group_id,
            "is_sharing": True,
            "updated_at": {"$gte": cutoff}
        }, {"_id": 0}))
        
        return [PositionShare(**p) for p in positions]
    
    async def stop_sharing_position(
        self,
        group_id: str,
        user_id: str
    ) -> bool:
        """Stop sharing position"""
        result = self.positions_collection.update_one(
            {"group_id": group_id, "user_id": user_id},
            {"$set": {"is_sharing": False}}
        )
        return result.modified_count > 0
    
    # ==========================================
    # Stats
    # ==========================================
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get collaborative engine statistics"""
        return {
            "total_groups": self.groups_collection.count_documents({"status": GroupStatus.ACTIVE.value}),
            "total_members": self.members_collection.count_documents({}),
            "total_spots": self.spots_collection.count_documents({"is_active": True}),
            "total_events": self.events_collection.count_documents({}),
            "total_messages": self.messages_collection.count_documents({})
        }
