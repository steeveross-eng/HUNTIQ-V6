"""Orders Engine Models - PHASE 7 EXTRACTION
Version: 1.0.0
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Literal
from datetime import datetime, timezone
import uuid


class Order(BaseModel):
    """Order model with hybrid dropshipping/affiliation support"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    customer_name: Optional[str] = ""
    customer_email: Optional[str] = ""
    product_id: str
    product_name: Optional[str] = ""
    products_list: List[str] = []
    supplier_id: Optional[str] = None
    supplier_name: Optional[str] = ""
    
    sale_mode: Literal["dropshipping", "affiliation"] = "dropshipping"
    quantity: int = 1
    sale_price: float
    supplier_price: float = 0
    affiliate_commission_percent: float = 0
    affiliate_commission_amount: float = 0
    net_margin: float = 0
    
    status: Literal["pending", "processing", "shipped", "delivered", "cancelled"] = "pending"
    affiliate_click_id: Optional[str] = None
    cancellation_reason: Optional[str] = ""
    cancellation_email_sent: bool = False
    
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OrderCreate(BaseModel):
    """Create order request"""
    customer_id: str
    product_id: str
    quantity: int = 1
    customer_name: Optional[str] = ""
    customer_email: Optional[str] = ""
    customer_address: Optional[str] = ""


class OrderUpdate(BaseModel):
    """Update order request"""
    status: Optional[Literal["pending", "processing", "shipped", "delivered", "cancelled"]] = None
    customer_email: Optional[str] = None
    cancellation_reason: Optional[str] = None


class OrderCancellation(BaseModel):
    """Order cancellation request"""
    reason: Optional[str] = "Produits non disponibles"
    send_email: bool = True


class Commission(BaseModel):
    """Commission tracking model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order_id: Optional[str] = None
    affiliate_click_id: Optional[str] = None
    product_id: str
    product_name: Optional[str] = ""
    supplier_id: Optional[str] = None
    supplier_name: Optional[str] = ""
    customer_id: Optional[str] = None
    
    commission_type: Literal["dropshipping_margin", "affiliate"] = "dropshipping_margin"
    amount: float
    status: Literal["pending", "confirmed", "paid", "cancelled"] = "pending"
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    confirmed_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
