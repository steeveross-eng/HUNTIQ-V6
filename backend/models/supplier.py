# Supplier Models
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal
from datetime import datetime, timezone
import uuid


class Supplier(BaseModel):
    """Supplier/Store model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    contact_name: Optional[str] = ""
    email: Optional[str] = ""
    phone: Optional[str] = ""
    address: Optional[str] = ""
    partnership_type: Literal["dropshipping", "affiliation", "hybrid"] = "dropshipping"
    shipping_delay: int = 3  # Délai d'expédition en jours
    commission_rate: float = 0.15  # Taux de commission (15%)
    active: bool = True
    notes: Optional[str] = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SupplierCreate(BaseModel):
    """Model for creating a new supplier"""
    name: str
    contact_name: Optional[str] = ""
    email: Optional[str] = ""
    phone: Optional[str] = ""
    address: Optional[str] = ""
    partnership_type: Literal["dropshipping", "affiliation", "hybrid"] = "dropshipping"
    shipping_delay: int = 3
    commission_rate: float = 0.15
    notes: Optional[str] = ""
