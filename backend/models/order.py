# Order Models
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Literal
from datetime import datetime, timezone
import uuid


class OrderItem(BaseModel):
    """Single item in an order"""
    product_id: str
    product_name: str
    quantity: int
    unit_price: float
    subtotal: float


class Order(BaseModel):
    """Order model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    items: List[OrderItem]
    subtotal: float
    shipping_cost: float
    total: float
    
    # Customer info
    customer_name: str
    customer_email: str
    customer_phone: Optional[str] = ""
    shipping_address: str
    
    # Referral info
    referral_code: Optional[str] = None
    discount_percent: float = 0
    discount_amount: float = 0
    
    # Order status
    status: Literal["pending", "confirmed", "processing", "shipped", "delivered", "cancelled"] = "pending"
    payment_status: Literal["pending", "paid", "refunded", "failed"] = "pending"
    payment_method: Optional[str] = None
    
    # Tracking
    tracking_number: Optional[str] = None
    supplier_id: Optional[str] = None
    notes: Optional[str] = ""
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OrderCreate(BaseModel):
    """Model for creating a new order"""
    items: List[OrderItem]
    customer_name: str
    customer_email: str
    customer_phone: Optional[str] = ""
    shipping_address: str
    referral_code: Optional[str] = None
    payment_method: Optional[str] = None
    notes: Optional[str] = ""
