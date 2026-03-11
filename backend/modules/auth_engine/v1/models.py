"""
Auth Engine - Pydantic Models
Hybrid Authentication: JWT (email/password) + Google OAuth
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class AuthProvider(str, Enum):
    """Authentication provider types"""
    LOCAL = "local"  # Email/password
    GOOGLE = "google"  # Google OAuth


class UserCreate(BaseModel):
    """User registration model"""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    phone: Optional[str] = None


class UserLogin(BaseModel):
    """User login model"""
    email: EmailStr
    password: str
    remember_device: bool = False


class UserResponse(BaseModel):
    """User response model (excludes sensitive data)"""
    user_id: str
    name: str
    email: str
    phone: Optional[str] = None
    picture: Optional[str] = None
    auth_provider: str = "local"
    role: str = "hunter"  # Default role for backward compatibility
    created_at: Optional[datetime] = None
    is_active: bool = True


class TokenResponse(BaseModel):
    """Token response model"""
    success: bool
    token: str
    user: UserResponse
    device_trusted: bool = False
    message: Optional[str] = None


class GoogleAuthCallback(BaseModel):
    """Google OAuth callback data"""
    session_id: str


class SessionData(BaseModel):
    """Session data from Emergent Auth"""
    id: str
    email: str
    name: str
    picture: Optional[str] = None
    session_token: str


class PasswordReset(BaseModel):
    """Password reset request"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=6)


class DeviceTrust(BaseModel):
    """Trusted device model"""
    device_id: str
    user_id: str
    ip_address: str
    user_agent: Optional[str] = None
    device_name: Optional[str] = None
    created_at: datetime
    last_used: datetime
