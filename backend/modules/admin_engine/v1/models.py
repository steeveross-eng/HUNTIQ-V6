"""Admin Engine Models - MÉTIER

Pydantic models for administration.

Version: 1.0.0
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal
from datetime import datetime, timezone
from enum import Enum
import uuid


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertType(str, Enum):
    """Alert types"""
    STOCK_LOW = "stock_low"
    ORDER_FAILED = "order_failed"
    PAYMENT_ISSUE = "payment_issue"
    SYSTEM_ERROR = "system_error"
    SECURITY = "security"
    PERFORMANCE = "performance"
    USER_REPORT = "user_report"


class AdminLogin(BaseModel):
    """Admin login request"""
    email: str
    password: str
    otp_code: Optional[str] = None


class Alert(BaseModel):
    """System alert"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    data: Dict[str, Any] = Field(default_factory=dict)
    is_read: bool = False
    is_resolved: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    read_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None


class SiteSettings(BaseModel):
    """Site-wide settings"""
    site_name: str = "BIONIC HUNT/Chasse V3"
    site_description: str = "Plateforme de chasse intelligente"
    contact_email: str = ""
    support_phone: str = ""
    
    # Features
    maintenance_mode: bool = False
    registration_enabled: bool = True
    orders_enabled: bool = True
    
    # Appearance
    theme: str = "default"
    logo_url: Optional[str] = None
    favicon_url: Optional[str] = None
    
    # SEO
    meta_title: str = ""
    meta_description: str = ""
    
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: str = ""


class MaintenanceMode(BaseModel):
    """Maintenance mode configuration"""
    enabled: bool = False
    title: str = "Site en maintenance"
    message: str = "Nous effectuons des mises à jour. Revenez bientôt."
    estimated_end: Optional[datetime] = None
    allow_admin_access: bool = True
    enabled_at: Optional[datetime] = None
    enabled_by: str = ""


class DashboardStats(BaseModel):
    """Dashboard statistics"""
    # Users
    total_users: int = 0
    new_users_today: int = 0
    new_users_week: int = 0
    active_users_today: int = 0
    
    # Orders
    total_orders: int = 0
    orders_today: int = 0
    orders_week: int = 0
    pending_orders: int = 0
    
    # Revenue
    revenue_today: float = 0.0
    revenue_week: float = 0.0
    revenue_month: float = 0.0
    
    # Products
    total_products: int = 0
    low_stock_products: int = 0
    out_of_stock_products: int = 0
    
    # Analyses
    total_analyses: int = 0
    analyses_today: int = 0
    
    # System
    active_sessions: int = 0
    unread_alerts: int = 0
    
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AuditLog(BaseModel):
    """Admin audit log entry"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    admin_id: str
    admin_email: str
    action: str
    resource_type: str  # user, product, order, setting
    resource_id: Optional[str] = None
    old_value: Optional[Dict[str, Any]] = None
    new_value: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ReportConfig(BaseModel):
    """Report configuration"""
    report_type: Literal["sales", "users", "products", "commissions"]
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    format: Literal["json", "csv", "pdf"] = "json"
    filters: Dict[str, Any] = Field(default_factory=dict)
