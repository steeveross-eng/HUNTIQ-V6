"""Affiliate Engine Models"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime, timezone
import uuid

class AffiliateClick(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: Optional[str] = None
    session_id: str
    product_id: str
    product_name: Optional[str] = ""
    supplier_id: Optional[str] = None
    affiliate_link: str
    converted: bool = False
    commission_amount: float = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    converted_at: Optional[datetime] = None

class AffiliateClickCreate(BaseModel):
    product_id: str
    session_id: str

class AffiliateConfirm(BaseModel):
    commission_amount: float
