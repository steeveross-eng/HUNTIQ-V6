"""User Engine Service - MÉTIER

Business logic for user management.

Version: 1.0.0
"""

import os
import hashlib
import secrets
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from pymongo import MongoClient

from .models import (
    User, UserProfile, UserPreferences, UserCreate, UserUpdate,
    UserRole, UserStatus, UserSession, UserActivity
)


class UserService:
    """Service for user management"""
    
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
    def users_collection(self):
        return self.db.users
    
    @property
    def profiles_collection(self):
        return self.db.user_profiles
    
    @property
    def sessions_collection(self):
        return self.db.user_sessions
    
    @property
    def activity_collection(self):
        return self.db.user_activity
    
    def _hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return f"{salt}:{hash_obj.hex()}"
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            salt, hash_value = hashed.split(':')
            hash_obj = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            )
            return hash_obj.hex() == hash_value
        except Exception:
            return False
    
    def _generate_token(self) -> str:
        """Generate secure session token"""
        return secrets.token_urlsafe(32)
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        # Check if email exists
        existing = self.users_collection.find_one({"email": user_data.email})
        if existing:
            raise ValueError("Email already registered")
        
        user = User(
            email=user_data.email,
            name=user_data.name,
            phone=user_data.phone,
            language=user_data.language,
            region=user_data.region
        )
        
        # Store with hashed password if provided
        user_dict = user.model_dump()
        if user_data.password:
            user_dict["password_hash"] = self._hash_password(user_data.password)
        user_dict.pop("_id", None)
        
        self.users_collection.insert_one(user_dict)
        
        # Create default profile
        profile = UserProfile(user_id=user.id)
        profile_dict = profile.model_dump()
        profile_dict.pop("_id", None)
        self.profiles_collection.insert_one(profile_dict)
        
        # Log activity
        await self.log_activity(user.id, "account_created")
        
        return user
    
    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        user_dict = self.users_collection.find_one({"id": user_id}, {"_id": 0, "password_hash": 0})
        if user_dict:
            return User(**user_dict)
        return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        user_dict = self.users_collection.find_one({"email": email}, {"_id": 0, "password_hash": 0})
        if user_dict:
            return User(**user_dict)
        return None
    
    async def update_user(self, user_id: str, update_data: UserUpdate) -> Optional[User]:
        """Update user information"""
        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
        if not update_dict:
            return await self.get_user(user_id)
        
        update_dict["updated_at"] = datetime.now(timezone.utc)
        
        self.users_collection.update_one(
            {"id": user_id},
            {"$set": update_dict}
        )
        
        await self.log_activity(user_id, "profile_updated", update_dict)
        return await self.get_user(user_id)
    
    async def authenticate(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user and create session"""
        user_dict = self.users_collection.find_one({"email": email})
        if not user_dict:
            return None
        
        # Verify password
        password_hash = user_dict.get("password_hash", "")
        if not password_hash or not self._verify_password(password, password_hash):
            return None
        
        # Check status
        if user_dict.get("status") != UserStatus.ACTIVE.value:
            return None
        
        # Create session
        token = self._generate_token()
        session = UserSession(
            user_id=user_dict["id"],
            token=token,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )
        
        session_dict = session.model_dump()
        session_dict.pop("_id", None)
        self.sessions_collection.insert_one(session_dict)
        
        # Update login stats
        self.users_collection.update_one(
            {"id": user_dict["id"]},
            {
                "$set": {"last_login": datetime.now(timezone.utc)},
                "$inc": {"login_count": 1}
            }
        )
        
        await self.log_activity(user_dict["id"], "login")
        
        user_dict.pop("password_hash", None)
        user_dict.pop("_id", None)
        
        return {
            "user": user_dict,
            "token": token,
            "expires_at": session.expires_at.isoformat()
        }
    
    async def validate_session(self, token: str) -> Optional[User]:
        """Validate session token and return user"""
        session = self.sessions_collection.find_one({
            "token": token,
            "is_active": True,
            "expires_at": {"$gt": datetime.now(timezone.utc)}
        })
        
        if not session:
            return None
        
        return await self.get_user(session["user_id"])
    
    async def logout(self, token: str) -> bool:
        """Invalidate session"""
        result = self.sessions_collection.update_one(
            {"token": token},
            {"$set": {"is_active": False}}
        )
        return result.modified_count > 0
    
    async def get_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile"""
        profile_dict = self.profiles_collection.find_one({"user_id": user_id}, {"_id": 0})
        if profile_dict:
            return UserProfile(**profile_dict)
        return None
    
    async def update_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Optional[UserProfile]:
        """Update user profile"""
        profile_data["updated_at"] = datetime.now(timezone.utc)
        
        self.profiles_collection.update_one(
            {"user_id": user_id},
            {"$set": profile_data},
            upsert=True
        )
        
        await self.log_activity(user_id, "profile_updated")
        return await self.get_profile(user_id)
    
    async def get_preferences(self, user_id: str) -> Optional[UserPreferences]:
        """Get user preferences"""
        prefs_dict = self.db.user_preferences.find_one({"user_id": user_id}, {"_id": 0})
        if prefs_dict:
            return UserPreferences(**prefs_dict)
        # Return defaults
        return UserPreferences(user_id=user_id)
    
    async def update_preferences(self, user_id: str, prefs_data: Dict[str, Any]) -> UserPreferences:
        """Update user preferences"""
        prefs_data["user_id"] = user_id
        prefs_data["updated_at"] = datetime.now(timezone.utc)
        
        self.db.user_preferences.update_one(
            {"user_id": user_id},
            {"$set": prefs_data},
            upsert=True
        )
        
        return await self.get_preferences(user_id)
    
    async def log_activity(self, user_id: str, action: str, details: Dict[str, Any] = None):
        """Log user activity"""
        activity = UserActivity(
            user_id=user_id,
            action=action,
            details=details or {}
        )
        activity_dict = activity.model_dump()
        activity_dict.pop("_id", None)
        self.activity_collection.insert_one(activity_dict)
    
    async def get_activity_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user activity history"""
        cursor = self.activity_collection.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("timestamp", -1).limit(limit)
        
        return list(cursor)
    
    async def list_users(self, skip: int = 0, limit: int = 50, 
                         role: Optional[str] = None) -> List[User]:
        """List users with optional filtering"""
        query = {}
        if role:
            query["role"] = role
        
        cursor = self.users_collection.find(
            query,
            {"_id": 0, "password_hash": 0}
        ).skip(skip).limit(limit)
        
        return [User(**doc) for doc in cursor]
    
    async def count_users(self, role: Optional[str] = None) -> int:
        """Count users"""
        query = {}
        if role:
            query["role"] = role
        return self.users_collection.count_documents(query)
    
    async def update_role(self, user_id: str, new_role: UserRole) -> Optional[User]:
        """Update user role (admin only)"""
        self.users_collection.update_one(
            {"id": user_id},
            {"$set": {"role": new_role.value, "updated_at": datetime.now(timezone.utc)}}
        )
        await self.log_activity(user_id, "role_changed", {"new_role": new_role.value})
        return await self.get_user(user_id)
    
    async def suspend_user(self, user_id: str, reason: str = "") -> Optional[User]:
        """Suspend user account"""
        self.users_collection.update_one(
            {"id": user_id},
            {"$set": {
                "status": UserStatus.SUSPENDED.value,
                "updated_at": datetime.now(timezone.utc)
            }}
        )
        
        # Invalidate all sessions
        self.sessions_collection.update_many(
            {"user_id": user_id},
            {"$set": {"is_active": False}}
        )
        
        await self.log_activity(user_id, "account_suspended", {"reason": reason})
        return await self.get_user(user_id)
    
    async def reactivate_user(self, user_id: str) -> Optional[User]:
        """Reactivate suspended user"""
        self.users_collection.update_one(
            {"id": user_id},
            {"$set": {
                "status": UserStatus.ACTIVE.value,
                "updated_at": datetime.now(timezone.utc)
            }}
        )
        await self.log_activity(user_id, "account_reactivated")
        return await self.get_user(user_id)
