"""Referral Engine Service - MÉTIER

Business logic for referral system.
Extracted from referral_system.py.

Version: 1.0.0
"""

import os
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from pymongo import MongoClient

from .models import (
    ReferralUser, ReferralClick, ReferralInvite,
    ReferralTier, PartnerApplication, DEFAULT_DISCOUNT_TIERS
)


# Social platforms configuration
SOCIAL_PLATFORMS = {
    "facebook": {
        "name": "Facebook",
        "icon": "facebook",
        "share_url": "https://www.facebook.com/sharer/sharer.php?u={url}&quote={message}",
        "color": "#1877F2"
    },
    "messenger": {
        "name": "Messenger",
        "icon": "message-circle",
        "share_url": "https://www.facebook.com/dialog/send?link={url}&app_id=1&redirect_uri={url}",
        "color": "#0084FF"
    },
    "whatsapp": {
        "name": "WhatsApp",
        "icon": "message-circle",
        "share_url": "https://api.whatsapp.com/send?text={message}%20{url}",
        "color": "#25D366"
    },
    "sms": {
        "name": "SMS",
        "icon": "smartphone",
        "share_url": "sms:?body={message}%20{url}",
        "color": "#34C759"
    },
    "email": {
        "name": "Courriel",
        "icon": "mail",
        "share_url": "mailto:?subject={subject}&body={message}%0A%0A{url}",
        "color": "#EA4335"
    },
    "copy": {
        "name": "Copier le lien",
        "icon": "copy",
        "share_url": None,
        "color": "#6B7280"
    }
}


class ReferralService:
    """Service for referral system"""
    
    def __init__(self, base_url: str = None):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'test_database')
        self.base_url = base_url or os.environ.get('REACT_APP_BACKEND_URL', 'https://bionic-hunt.com')
        self._client = None
        self._db = None
    
    @property
    def db(self):
        if self._db is None:
            self._client = MongoClient(self.mongo_url)
            self._db = self._client[self.db_name]
        return self._db
    
    def generate_referral_link(self, code: str) -> str:
        """Generate full referral link"""
        return f"{self.base_url}?ref={code}"
    
    def calculate_tier(self, total_buyers: int, is_partner: bool = False) -> tuple:
        """Calculate tier and discount based on buyers count"""
        if is_partner:
            return ReferralTier.PARTNER, DEFAULT_DISCOUNT_TIERS["partner"]["discount_percent"]
        
        for tier_id, config in DEFAULT_DISCOUNT_TIERS.items():
            if tier_id == "partner":
                continue
            if config["min_buyers"] <= total_buyers <= config["max_buyers"]:
                return ReferralTier(tier_id), config["discount_percent"]
        
        return ReferralTier.DIAMOND, DEFAULT_DISCOUNT_TIERS["diamond"]["discount_percent"]
    
    async def create_user(self, name: str, email: str, phone: str = None) -> ReferralUser:
        """Create a new referral user"""
        # Check if email exists
        existing = self.db.referral_users.find_one({"email": email})
        if existing:
            raise ValueError("Un compte de parrainage existe déjà pour cet email")
        
        user = ReferralUser(name=name, email=email, phone=phone)
        user.referral_link = self.generate_referral_link(user.referral_code)
        
        user_dict = user.model_dump()
        user_dict.pop("_id", None)
        # Convert datetime to ISO string for MongoDB
        for key in ["created_at", "last_activity", "partner_approved_at"]:
            if user_dict.get(key):
                user_dict[key] = user_dict[key].isoformat() if isinstance(user_dict[key], datetime) else user_dict[key]
        
        self.db.referral_users.insert_one(user_dict)
        return user
    
    async def get_user_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """Get user by referral code"""
        return self.db.referral_users.find_one({"referral_code": code}, {"_id": 0})
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        return self.db.referral_users.find_one({"email": email}, {"_id": 0})
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        return self.db.referral_users.find_one({"id": user_id}, {"_id": 0})
    
    async def track_click(self, code: str, source: str = "direct", 
                          ip: str = None, user_agent: str = None) -> bool:
        """Track a referral link click"""
        user = await self.get_user_by_code(code)
        if not user:
            return False
        
        click = ReferralClick(
            referral_code=code,
            referrer_id=user["id"],
            source_platform=source,
            ip_address=ip,
            user_agent=user_agent
        )
        
        click_dict = click.model_dump()
        click_dict.pop("_id", None)
        click_dict["clicked_at"] = click_dict["clicked_at"].isoformat()
        
        self.db.referral_clicks.insert_one(click_dict)
        
        # Update user stats
        self.db.referral_users.update_one(
            {"referral_code": code},
            {
                "$inc": {"total_clicks": 1},
                "$set": {"last_activity": datetime.now(timezone.utc).isoformat()}
            }
        )
        
        return True
    
    async def record_signup(self, referral_code: str, invitee_email: str, 
                            invitee_name: str = None) -> Optional[ReferralInvite]:
        """Record a signup from referral"""
        user = await self.get_user_by_code(referral_code)
        if not user:
            return None
        
        invite = ReferralInvite(
            referrer_id=user["id"],
            referral_code=referral_code,
            invitee_email=invitee_email,
            invitee_name=invitee_name,
            status="signed_up",
            signed_up_at=datetime.now(timezone.utc)
        )
        
        invite_dict = invite.model_dump()
        invite_dict.pop("_id", None)
        for key in ["invited_at", "signed_up_at", "first_purchase_at", "last_purchase_at"]:
            if invite_dict.get(key):
                invite_dict[key] = invite_dict[key].isoformat() if isinstance(invite_dict[key], datetime) else invite_dict[key]
        
        self.db.referral_invites.insert_one(invite_dict)
        
        # Update user stats
        self.db.referral_users.update_one(
            {"referral_code": referral_code},
            {
                "$inc": {"total_signups": 1},
                "$set": {"last_activity": datetime.now(timezone.utc).isoformat()}
            }
        )
        
        return invite
    
    async def record_purchase(self, referral_code: str, invitee_email: str,
                              order_amount: float, order_id: str) -> bool:
        """Record a purchase from referred user"""
        user = await self.get_user_by_code(referral_code)
        if not user:
            return False
        
        now = datetime.now(timezone.utc)
        
        # Update invite
        result = self.db.referral_invites.update_one(
            {"referral_code": referral_code, "invitee_email": invitee_email},
            {
                "$set": {"status": "purchased", "last_purchase_at": now.isoformat()},
                "$inc": {"total_purchases": 1, "total_spent": order_amount},
                "$setOnInsert": {"first_purchase_at": now.isoformat()}
            },
            upsert=True
        )
        
        # Update user stats
        old_buyers = user.get("total_buyers", 0)
        new_buyers = old_buyers + (1 if result.upserted_id else 0)
        
        # Calculate new tier
        new_tier, new_discount = self.calculate_tier(new_buyers, user.get("is_partner", False))
        
        self.db.referral_users.update_one(
            {"referral_code": referral_code},
            {
                "$inc": {
                    "total_buyers": 1 if result.upserted_id else 0,
                    "total_revenue_generated": order_amount
                },
                "$set": {
                    "last_activity": now.isoformat(),
                    "tier": new_tier.value,
                    "current_discount_percent": new_discount
                }
            }
        )
        
        return True
    
    async def get_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get referral dashboard for a user"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return {}
        
        # Get invites
        invites = list(self.db.referral_invites.find(
            {"referrer_id": user_id},
            {"_id": 0}
        ).sort("invited_at", -1).limit(50))
        
        # Get recent clicks
        clicks = list(self.db.referral_clicks.find(
            {"referrer_id": user_id},
            {"_id": 0}
        ).sort("clicked_at", -1).limit(20))
        
        return {
            "user": user,
            "stats": {
                "total_clicks": user.get("total_clicks", 0),
                "total_signups": user.get("total_signups", 0),
                "total_buyers": user.get("total_buyers", 0),
                "total_revenue": user.get("total_revenue_generated", 0),
                "current_tier": user.get("tier", "bronze"),
                "discount_percent": user.get("current_discount_percent", 5)
            },
            "invites": invites,
            "recent_clicks": clicks,
            "referral_link": user.get("referral_link", ""),
            "referral_code": user.get("referral_code", "")
        }
    
    async def get_share_data(self, user_id: str, lang: str = "fr") -> Dict[str, Any]:
        """Get share messages and links for user"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return {}
        
        discount = user.get("current_discount_percent", 5)
        link = user.get("referral_link", "")
        
        message_fr = f"🎯 Découvrez SCENT SCIENCE™ - Analyse scientifique des attractants de chasse! Utilisez mon lien pour {discount}% de rabais: {link}"
        message_en = f"🎯 Discover SCENT SCIENCE™ - Scientific hunting attractant analysis! Use my link for {discount}% off: {link}"
        
        return {
            "referral_link": link,
            "referral_code": user.get("referral_code", ""),
            "discount_percent": discount,
            "platforms": SOCIAL_PLATFORMS,
            "messages": {
                "fr": message_fr,
                "en": message_en
            }
        }
    
    async def get_discount_tiers(self) -> Dict[str, Any]:
        """Get discount tier configuration"""
        config = self.db.referral_config.find_one({"type": "discount_tiers"}, {"_id": 0})
        if config:
            return config.get("tiers", DEFAULT_DISCOUNT_TIERS)
        return DEFAULT_DISCOUNT_TIERS
    
    async def list_users(self, skip: int = 0, limit: int = 50, 
                         tier: str = None) -> List[Dict[str, Any]]:
        """List referral users"""
        query = {}
        if tier:
            query["tier"] = tier
        
        cursor = self.db.referral_users.find(query, {"_id": 0}).skip(skip).limit(limit)
        return list(cursor)
    
    async def apply_for_partner(self, application: PartnerApplication) -> PartnerApplication:
        """Submit partner application"""
        app_dict = application.model_dump()
        app_dict.pop("_id", None)
        app_dict["submitted_at"] = app_dict["submitted_at"].isoformat()
        
        self.db.partner_applications.insert_one(app_dict)
        return application
    
    async def approve_partner(self, user_id: str, commission_rate: float = 0.1) -> bool:
        """Approve partner application"""
        result = self.db.referral_users.update_one(
            {"id": user_id},
            {
                "$set": {
                    "is_partner": True,
                    "tier": ReferralTier.PARTNER.value,
                    "current_discount_percent": DEFAULT_DISCOUNT_TIERS["partner"]["discount_percent"],
                    "partner_commission_rate": commission_rate,
                    "partner_approved_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        return result.modified_count > 0
