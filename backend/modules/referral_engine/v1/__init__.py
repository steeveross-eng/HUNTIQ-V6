"""Referral Engine Module v1

Referral and affiliate system.

Version: 1.0.0
"""

from .router import router
from .service import ReferralService, SOCIAL_PLATFORMS
from .models import (
    ReferralUser, ReferralClick, ReferralInvite,
    ReferralTier, SeasonType, PartnerApplication,
    DEFAULT_DISCOUNT_TIERS
)

__all__ = [
    "router",
    "ReferralService",
    "SOCIAL_PLATFORMS",
    "ReferralUser",
    "ReferralClick",
    "ReferralInvite",
    "ReferralTier",
    "SeasonType",
    "PartnerApplication",
    "DEFAULT_DISCOUNT_TIERS"
]
