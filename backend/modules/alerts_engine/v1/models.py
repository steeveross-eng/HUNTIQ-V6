"""Alerts Engine Models"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal
from datetime import datetime, timezone
import uuid

class Alert(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: Literal["stock_out", "pending_commission", "unconfirmed_order", "high_growth", "low_performance"]
    title: str
    message: str
    product_id: Optional[str] = None
    supplier_id: Optional[str] = None
    order_id: Optional[str] = None
    is_read: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AlertCreate(BaseModel):
    type: Literal["stock_out", "pending_commission", "unconfirmed_order", "high_growth", "low_performance"]
    title: str
    message: str
    product_id: Optional[str] = None
    supplier_id: Optional[str] = None
    order_id: Optional[str] = None

class SiteSettings(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = "site_settings"
    maintenance_mode: bool = False
    maintenance_title: str = "Site en maintenance"
    maintenance_message: str = "Nous effectuons actuellement des mises à jour. Veuillez revenir plus tard."
    maintenance_enabled_at: Optional[datetime] = None
    maintenance_enabled_by: str = "admin"
    allow_admin_access: bool = True
    estimated_return: Optional[str] = ""
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MaintenanceModeUpdate(BaseModel):
    maintenance_mode: bool
    maintenance_title: Optional[str] = "Site en maintenance"
    maintenance_message: Optional[str] = "Nous effectuons actuellement des mises à jour."
    estimated_return: Optional[str] = ""
