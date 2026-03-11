# Analytics Models
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import uuid


class AnalyticsEvent(BaseModel):
    """Analytics event model for tracking user interactions"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str  # page_view, product_view, product_click, add_to_cart, order, etc.
    page: Optional[str] = None
    product_id: Optional[str] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    referral_code: Optional[str] = None
    metadata: Dict[str, Any] = {}
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
