"""Suppliers Engine Models"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal
from datetime import datetime, timezone
import uuid

class Supplier(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    contact_name: Optional[str] = ""
    email: Optional[str] = ""
    phone: Optional[str] = ""
    address: Optional[str] = ""
    partnership_type: Literal["dropshipping", "affiliation", "hybrid"] = "dropshipping"
    shipping_delay: int = 3
    partnership_conditions: Optional[str] = ""
    is_active: bool = True
    total_orders: int = 0
    total_revenue_supplier: float = 0
    total_revenue_scent: float = 0
    confirmation_rate: float = 100
    avg_shipping_days: float = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SupplierCreate(BaseModel):
    name: str
    contact_name: Optional[str] = ""
    email: Optional[str] = ""
    phone: Optional[str] = ""
    address: Optional[str] = ""
    partnership_type: Literal["dropshipping", "affiliation", "hybrid"] = "dropshipping"
    shipping_delay: int = 3
    partnership_conditions: Optional[str] = ""

class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    partnership_type: Optional[Literal["dropshipping", "affiliation", "hybrid"]] = None
    shipping_delay: Optional[int] = None
    partnership_conditions: Optional[str] = None
    is_active: Optional[bool] = None
