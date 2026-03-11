"""
Auth Engine - Service Layer
Hybrid Authentication: JWT (email/password) + Google OAuth
"""
import os
import uuid
import hashlib
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple
import jwt
from passlib.context import CryptContext
from motor.motor_asyncio import AsyncIOMotorDatabase
import httpx

from .models import (
    UserCreate, UserLogin, UserResponse, TokenResponse,
    SessionData, AuthProvider
)
from .email_service import EmailService

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "huntiq_default_secret_change_me")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 1440))

# Emergent Auth URL
EMERGENT_AUTH_URL = "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data"


class AuthService:
    """Authentication service for BIONIC HUNT/Chasse V3"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.users_collection = db['users']
        self.sessions_collection = db['user_sessions']
        self.trusted_devices_collection = db['trusted_devices']
    
    # ==========================================
    # Password Utilities
    # ==========================================
    
    def hash_password(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def generate_user_id(self) -> str:
        """Generate a unique user ID"""
        return f"user_{uuid.uuid4().hex[:12]}"
    
    # ==========================================
    # JWT Utilities
    # ==========================================
    
    def create_access_token(self, user_id: str, email: str) -> str:
        """Create JWT access token"""
        expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": user_id,
            "email": email,
            "exp": expire,
            "iat": datetime.now(timezone.utc)
        }
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
    
    # ==========================================
    # User Management
    # ==========================================
    
    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email"""
        user = await self.users_collection.find_one(
            {"email": email.lower()},
            {"_id": 0}
        )
        return user
    
    async def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Get user by ID"""
        user = await self.users_collection.find_one(
            {"user_id": user_id},
            {"_id": 0}
        )
        return user
    
    async def create_user(
        self, 
        name: str, 
        email: str, 
        password: Optional[str] = None,
        phone: Optional[str] = None,
        picture: Optional[str] = None,
        auth_provider: AuthProvider = AuthProvider.LOCAL
    ) -> dict:
        """Create a new user"""
        user_id = self.generate_user_id()
        now = datetime.now(timezone.utc)
        
        user_doc = {
            "user_id": user_id,
            "name": name,
            "email": email.lower(),
            "phone": phone,
            "picture": picture,
            "auth_provider": auth_provider.value,
            "role": "hunter",  # Default role for new users
            "is_active": True,
            "created_at": now,
            "updated_at": now
        }
        
        if password:
            user_doc["password_hash"] = self.hash_password(password)
        
        await self.users_collection.insert_one(user_doc)
        
        # Remove password_hash from response
        user_doc.pop("password_hash", None)
        return user_doc
    
    # ==========================================
    # Local Authentication (Email/Password)
    # ==========================================
    
    async def register(self, user_data: UserCreate) -> Tuple[bool, Optional[TokenResponse], Optional[str]]:
        """Register a new user with email/password"""
        # Check if user exists
        existing = await self.get_user_by_email(user_data.email)
        if existing:
            return False, None, "Un compte avec cet email existe déjà"
        
        # Create user
        user = await self.create_user(
            name=user_data.name,
            email=user_data.email,
            password=user_data.password,
            phone=user_data.phone,
            auth_provider=AuthProvider.LOCAL
        )
        
        # Generate token
        token = self.create_access_token(user["user_id"], user["email"])
        
        # Store session
        await self._store_session(user["user_id"], token)
        
        # Send welcome email (async, non-blocking)
        try:
            email_service = EmailService(self.db)
            await email_service.send_welcome_email(user["email"], user["name"])
            logger.info(f"Welcome email sent to {user['email']}")
        except Exception as e:
            logger.warning(f"Failed to send welcome email to {user['email']}: {e}")
            # Don't fail registration if email fails
        
        return True, TokenResponse(
            success=True,
            token=token,
            user=UserResponse(**user),
            message="Compte créé avec succès"
        ), None
    
    async def login(
        self, 
        login_data: UserLogin,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Tuple[bool, Optional[TokenResponse], Optional[str]]:
        """Login with email/password"""
        user = await self.get_user_by_email(login_data.email)
        
        if not user:
            return False, None, "Email ou mot de passe incorrect"
        
        # Check if user has a password (not Google OAuth only)
        if "password_hash" not in user:
            return False, None, "Ce compte utilise Google pour se connecter"
        
        # Verify password
        if not self.verify_password(login_data.password, user["password_hash"]):
            return False, None, "Email ou mot de passe incorrect"
        
        # Generate token
        token = self.create_access_token(user["user_id"], user["email"])
        
        # Store session
        await self._store_session(user["user_id"], token)
        
        # Check/create trusted device
        device_trusted = False
        if login_data.remember_device and ip_address:
            device_trusted = await self._trust_device(
                user["user_id"], 
                ip_address, 
                user_agent
            )
        
        # Remove sensitive data
        user.pop("password_hash", None)
        
        return True, TokenResponse(
            success=True,
            token=token,
            user=UserResponse(**user),
            device_trusted=device_trusted,
            message="Connexion réussie"
        ), None
    
    # ==========================================
    # Google OAuth Authentication
    # ==========================================
    
    async def google_auth_callback(self, session_id: str) -> Tuple[bool, Optional[TokenResponse], Optional[str]]:
        """
        Handle Google OAuth callback from Emergent Auth
        REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
        """
        try:
            # Call Emergent Auth to get session data
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    EMERGENT_AUTH_URL,
                    headers={"X-Session-ID": session_id},
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    logger.error(f"Emergent Auth error: {response.status_code}")
                    return False, None, "Erreur d'authentification Google"
                
                session_data = SessionData(**response.json())
        except Exception as e:
            logger.error(f"Google auth error: {e}")
            return False, None, "Erreur de connexion avec Google"
        
        # Check if user exists
        user = await self.get_user_by_email(session_data.email)
        
        if user:
            # Update existing user with Google info if needed
            if user.get("auth_provider") == "local":
                await self.users_collection.update_one(
                    {"user_id": user["user_id"]},
                    {"$set": {
                        "picture": session_data.picture,
                        "google_id": session_data.id,
                        "updated_at": datetime.now(timezone.utc)
                    }}
                )
            user = await self.get_user_by_id(user["user_id"])
        else:
            # Create new user from Google
            user = await self.create_user(
                name=session_data.name,
                email=session_data.email,
                picture=session_data.picture,
                auth_provider=AuthProvider.GOOGLE
            )
            user["google_id"] = session_data.id
            await self.users_collection.update_one(
                {"user_id": user["user_id"]},
                {"$set": {"google_id": session_data.id}}
            )
        
        # Generate our own JWT token
        token = self.create_access_token(user["user_id"], user["email"])
        
        # Store session
        await self._store_session(user["user_id"], token)
        
        # Remove sensitive data
        user.pop("password_hash", None)
        
        return True, TokenResponse(
            success=True,
            token=token,
            user=UserResponse(**user),
            message="Connexion Google réussie"
        ), None
    
    # ==========================================
    # Session Management
    # ==========================================
    
    async def _store_session(self, user_id: str, token: str) -> None:
        """Store session in database"""
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        
        await self.sessions_collection.insert_one({
            "user_id": user_id,
            "token": token,
            "expires_at": expires_at,
            "created_at": datetime.now(timezone.utc)
        })
    
    async def logout(self, token: str) -> bool:
        """Invalidate session"""
        result = await self.sessions_collection.delete_one({"token": token})
        return result.deleted_count > 0
    
    async def verify_session(self, token: str) -> Optional[UserResponse]:
        """Verify token and return user"""
        payload = self.verify_token(token)
        if not payload:
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        user.pop("password_hash", None)
        return UserResponse(**user)
    
    # ==========================================
    # Trusted Devices / Auto-Login
    # ==========================================
    
    async def _trust_device(
        self, 
        user_id: str, 
        ip_address: str, 
        user_agent: Optional[str] = None
    ) -> bool:
        """Trust a device for auto-login"""
        device_id = hashlib.sha256(f"{user_id}:{ip_address}".encode()).hexdigest()[:16]
        now = datetime.now(timezone.utc)
        
        await self.trusted_devices_collection.update_one(
            {"device_id": device_id},
            {
                "$set": {
                    "user_id": user_id,
                    "ip_address": ip_address,
                    "user_agent": user_agent,
                    "last_used": now
                },
                "$setOnInsert": {
                    "created_at": now
                }
            },
            upsert=True
        )
        return True
    
    async def check_trusted_device(self, ip_address: str) -> Optional[dict]:
        """Check if IP is a trusted device"""
        device = await self.trusted_devices_collection.find_one(
            {"ip_address": ip_address},
            {"_id": 0}
        )
        return device
    
    async def auto_login(self, ip_address: str) -> Tuple[bool, Optional[TokenResponse], Optional[str]]:
        """Attempt auto-login from trusted device"""
        device = await self.check_trusted_device(ip_address)
        
        if not device:
            return False, None, "Appareil non reconnu"
        
        user = await self.get_user_by_id(device["user_id"])
        if not user:
            return False, None, "Utilisateur non trouvé"
        
        # Generate new token
        token = self.create_access_token(user["user_id"], user["email"])
        await self._store_session(user["user_id"], token)
        
        # Update device last used
        await self.trusted_devices_collection.update_one(
            {"device_id": device["device_id"]},
            {"$set": {"last_used": datetime.now(timezone.utc)}}
        )
        
        user.pop("password_hash", None)
        
        return True, TokenResponse(
            success=True,
            token=token,
            user=UserResponse(**user),
            device_trusted=True,
            message="Connexion automatique"
        ), None
    
    async def get_ip_info(self, ip_address: str) -> dict:
        """Get information about an IP address"""
        device = await self.check_trusted_device(ip_address)
        
        return {
            "ip_address": ip_address,
            "is_trusted": device is not None,
            "device_name": device.get("device_name") if device else None
        }
