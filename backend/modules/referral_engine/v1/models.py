"""Referral Engine Models - MÉTIER

Pydantic models for referral system.
Extracted from referral_system.py.

Version: 1.0.0
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime, timezone
from enum import Enum
import uuid
import secrets


class ReferralTier(str, Enum):
    """Referral tier levels"""
    BRONZE = "bronze"      # 0-2 invités
    SILVER = "silver"      # 3-4 invités
    GOLD = "gold"          # 5-9 invités
    PLATINUM = "platinum"  # 10-19 invités
    DIAMOND = "diamond"    # 20+ invités
    PARTNER = "partner"    # Partenaire Privilégié


class SeasonType(str, Enum):
    """Season types for promotions"""
    PRE_SEASON = "pre_season"
    RUT = "rut"
    POST_RUT = "post_rut"
    OPENING = "opening"
    END_SEASON = "end_season"
    OFF_PEAK = "off_peak"
    BLACK_FRIDAY = "black_friday"
    BOXING_DAY = "boxing_day"
    CUSTOM = "custom"


# Default discount tiers
DEFAULT_DISCOUNT_TIERS = {
    "bronze": {"min_buyers": 0, "max_buyers": 2, "discount_percent": 5, "label": "Bronze"},
    "silver": {"min_buyers": 3, "max_buyers": 4, "discount_percent": 10, "label": "Argent"},
    "gold": {"min_buyers": 5, "max_buyers": 9, "discount_percent": 15, "label": "Or"},
    "platinum": {"min_buyers": 10, "max_buyers": 19, "discount_percent": 25, "label": "Platine"},
    "diamond": {"min_buyers": 20, "max_buyers": 999, "discount_percent": 40, "label": "Diamant"},
    "partner": {"min_buyers": 0, "max_buyers": 999, "discount_percent": 50, "label": "Partenaire Privilégié"}
}


class ReferralUser(BaseModel):
    """Referral system user"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Identity
    name: str
    email: str
    phone: Optional[str] = None
    
    # Referral code
    referral_code: str = Field(default_factory=lambda: secrets.token_urlsafe(8)[:10].upper())
    referral_link: str = ""
    
    # Statistics
    total_clicks: int = 0
    total_signups: int = 0
    total_buyers: int = 0
    total_revenue_generated: float = 0.0
    
    # Tier and discount
    tier: ReferralTier = ReferralTier.BRONZE
    current_discount_percent: int = 5
    
    # Partner status
    is_partner: bool = False
    partner_type: Optional[str] = None
    partner_approved_at: Optional[datetime] = None
    partner_commission_rate: float = 0.0
    
    # History
    rewards_history: List[Dict[str, Any]] = []
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: Optional[datetime] = None
    is_active: bool = True


class ReferralClick(BaseModel):
    """Referral link click tracking"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    referral_code: str
    referrer_id: str
    
    # Source
    source_platform: str = "direct"
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Conversion
    converted_to_signup: bool = False
    converted_to_purchase: bool = False
    conversion_value: float = 0.0
    
    clicked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ReferralInvite(BaseModel):
    """Referred invitee"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Referrer
    referrer_id: str
    referral_code: str
    
    # Invitee
    invitee_email: str
    invitee_name: Optional[str] = None
    
    # Status
    status: Literal["clicked", "signed_up", "purchased"] = "clicked"
    
    # Purchases
    total_purchases: int = 0
    total_spent: float = 0.0
    first_purchase_at: Optional[datetime] = None
    last_purchase_at: Optional[datetime] = None
    
    # Dates
    invited_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    signed_up_at: Optional[datetime] = None


class DiscountTierConfig(BaseModel):
    """Discount tier configuration"""
    tier_id: str
    min_buyers: int
    max_buyers: int
    discount_percent: int
    label: str
    is_active: bool = True


class SeasonalPromotion(BaseModel):
    """Seasonal promotion"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    season_type: SeasonType
    
    # Period
    start_date: datetime
    end_date: datetime
    
    # Discount
    additional_discount_percent: int = 0
    applies_to_all: bool = True
    applies_to_categories: List[str] = []
    applies_to_products: List[str] = []
    
    # Status
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PartnerApplication(BaseModel):
    """Partner application"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    
    # Business info
    business_name: str
    business_type: Literal["boutique", "pourvoirie", "guide", "influenceur", "revendeur"]
    website: Optional[str] = None
    social_media: Dict[str, str] = {}
    
    # Justification
    estimated_monthly_volume: float = 0
    existing_referrals: int = 0
    motivation: str = ""
    
    # Status
    status: Literal["pending", "approved", "rejected"] = "pending"
    reviewed_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CreateReferralUserRequest(BaseModel):
    """Request to create referral user"""
    name: str
    email: str
    phone: Optional[str] = None


class TrackClickRequest(BaseModel):
    """Request to track referral click"""
    referral_code: str
    source: str = "direct"
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class RecordPurchaseRequest(BaseModel):
    """Request to record a purchase from referral"""
    referral_code: str
    invitee_email: str
    order_amount: float
    order_id: str
