"""
BIONIC Contact Engine - X300% Strategy
=======================================

Module de captation totale des contacts:
- Visitor Tracker (visiteurs anonymes)
- Ads Tracker (trafic publicitaire)
- Social Tracker (interactions sociales)
- Shadow Profiles (profils enrichis)

Architecture LEGO V5 - Module isolé.
"""

from fastapi import APIRouter, Body, Query
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/contact-engine", tags=["Contact Engine X300%"])

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'bionic_db')

_client = None
_db = None

def get_db():
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(MONGO_URL)
        _db = _client[DB_NAME]
    return _db


# ============================================
# VISITOR TRACKING
# ============================================

@router.post("/track/visitor")
async def track_visitor(
    visitor_data: Dict[str, Any] = Body(...)
):
    """
    Track un visiteur anonyme.
    Génère un shadow profile si nouveau.
    """
    db = get_db()
    
    visitor_id = visitor_data.get("visitor_id") or str(uuid.uuid4())
    
    # Check if visitor exists
    existing = await db.contacts_visitors.find_one({"visitor_id": visitor_id})
    
    if existing:
        # Update visit count and last seen
        await db.contacts_visitors.update_one(
            {"visitor_id": visitor_id},
            {
                "$inc": {"visit_count": 1},
                "$set": {
                    "last_seen": datetime.now(timezone.utc).isoformat(),
                    "last_page": visitor_data.get("page_url"),
                    "last_referrer": visitor_data.get("referrer"),
                    "user_agent": visitor_data.get("user_agent"),
                },
                "$push": {
                    "page_history": {
                        "url": visitor_data.get("page_url"),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "duration": visitor_data.get("duration", 0)
                    }
                }
            }
        )
        return {"success": True, "visitor_id": visitor_id, "status": "updated"}
    else:
        # Create new shadow profile
        shadow_profile = {
            "visitor_id": visitor_id,
            "profile_type": "anonymous",
            "first_seen": datetime.now(timezone.utc).isoformat(),
            "last_seen": datetime.now(timezone.utc).isoformat(),
            "visit_count": 1,
            "page_history": [{
                "url": visitor_data.get("page_url"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "duration": visitor_data.get("duration", 0)
            }],
            "last_page": visitor_data.get("page_url"),
            "last_referrer": visitor_data.get("referrer"),
            "user_agent": visitor_data.get("user_agent"),
            "device_info": visitor_data.get("device_info", {}),
            "geo_info": visitor_data.get("geo_info", {}),
            "source": visitor_data.get("source", "organic"),
            "utm_params": visitor_data.get("utm_params", {}),
            # Scoring initial
            "scores": {
                "interest": 10,
                "heat": 5,
                "retention": 0,
                "purchase_intent": 0
            },
            "consent": {
                "behavioral": True,  # Autorisé par défaut
                "personal": False,
                "marketing": False
            },
            "merged_with": None,
            "is_identified": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.contacts_visitors.insert_one(shadow_profile)
        return {"success": True, "visitor_id": visitor_id, "status": "created"}


# ============================================
# ADS TRACKING
# ============================================

@router.post("/track/ad-click")
async def track_ad_click(
    ad_data: Dict[str, Any] = Body(...)
):
    """
    Track un clic publicitaire.
    Enrichit le shadow profile avec les données publicitaires.
    """
    db = get_db()
    
    visitor_id = ad_data.get("visitor_id") or str(uuid.uuid4())
    
    ad_event = {
        "visitor_id": visitor_id,
        "event_type": "ad_click",
        "platform": ad_data.get("platform", "unknown"),  # google, meta, tiktok, etc.
        "campaign_id": ad_data.get("campaign_id"),
        "ad_id": ad_data.get("ad_id"),
        "ad_group": ad_data.get("ad_group"),
        "keyword": ad_data.get("keyword"),
        "creative": ad_data.get("creative"),
        "cost": ad_data.get("cost", 0),
        "landing_page": ad_data.get("landing_page"),
        "gclid": ad_data.get("gclid"),
        "fbclid": ad_data.get("fbclid"),
        "utm_params": ad_data.get("utm_params", {}),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    await db.contacts_ads_events.insert_one(ad_event)
    
    # Update visitor profile with ad source
    await db.contacts_visitors.update_one(
        {"visitor_id": visitor_id},
        {
            "$set": {
                "source": f"ads_{ad_data.get('platform', 'unknown')}",
                "last_ad_click": datetime.now(timezone.utc).isoformat()
            },
            "$inc": {
                "scores.heat": 15,
                "scores.purchase_intent": 10
            },
            "$push": {
                "ad_interactions": {
                    "platform": ad_data.get("platform"),
                    "campaign_id": ad_data.get("campaign_id"),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
        },
        upsert=True
    )
    
    return {"success": True, "visitor_id": visitor_id, "event": "ad_click_tracked"}


# ============================================
# SOCIAL TRACKING
# ============================================

@router.post("/track/social")
async def track_social_interaction(
    social_data: Dict[str, Any] = Body(...)
):
    """
    Track une interaction sociale.
    """
    db = get_db()
    
    visitor_id = social_data.get("visitor_id") or str(uuid.uuid4())
    
    social_event = {
        "visitor_id": visitor_id,
        "event_type": "social_interaction",
        "platform": social_data.get("platform"),  # facebook, instagram, tiktok, youtube
        "action": social_data.get("action"),  # share, like, comment, follow
        "content_id": social_data.get("content_id"),
        "referrer": social_data.get("referrer"),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    await db.contacts_social_events.insert_one(social_event)
    
    # Update visitor profile
    await db.contacts_visitors.update_one(
        {"visitor_id": visitor_id},
        {
            "$set": {
                "last_social_interaction": datetime.now(timezone.utc).isoformat()
            },
            "$inc": {
                "scores.interest": 10,
                "scores.heat": 5
            },
            "$push": {
                "social_interactions": {
                    "platform": social_data.get("platform"),
                    "action": social_data.get("action"),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
        },
        upsert=True
    )
    
    return {"success": True, "visitor_id": visitor_id, "event": "social_tracked"}


# ============================================
# IDENTITY GRAPH
# ============================================

@router.post("/identify")
async def identify_visitor(
    identification_data: Dict[str, Any] = Body(...)
):
    """
    Identifie un visiteur anonyme (après consentement).
    Fusionne le shadow profile avec les données personnelles.
    """
    db = get_db()
    
    visitor_id = identification_data.get("visitor_id")
    email = identification_data.get("email")
    
    if not visitor_id or not email:
        return {"success": False, "error": "visitor_id et email requis"}
    
    # Get existing visitor
    visitor = await db.contacts_visitors.find_one({"visitor_id": visitor_id})
    
    if not visitor:
        return {"success": False, "error": "Visiteur non trouvé"}
    
    # Check if email already exists in contacts
    existing_contact = await db.contacts.find_one({"email": email})
    
    if existing_contact:
        # Merge profiles
        merged_data = {
            **visitor,
            "email": email,
            "name": identification_data.get("name") or existing_contact.get("name"),
            "phone": identification_data.get("phone") or existing_contact.get("phone"),
            "is_identified": True,
            "identified_at": datetime.now(timezone.utc).isoformat(),
            "consent": {
                "behavioral": True,
                "personal": True,
                "marketing": identification_data.get("consent_marketing", False)
            }
        }
        
        await db.contacts.update_one(
            {"email": email},
            {"$set": merged_data}
        )
        
        # Mark visitor as merged
        await db.contacts_visitors.update_one(
            {"visitor_id": visitor_id},
            {"$set": {"merged_with": email, "is_identified": True}}
        )
        
        return {"success": True, "status": "merged", "contact_email": email}
    else:
        # Create new identified contact
        new_contact = {
            "email": email,
            "name": identification_data.get("name"),
            "phone": identification_data.get("phone"),
            "visitor_id": visitor_id,
            "is_identified": True,
            "identified_at": datetime.now(timezone.utc).isoformat(),
            "first_seen": visitor.get("first_seen"),
            "visit_count": visitor.get("visit_count", 1),
            "page_history": visitor.get("page_history", []),
            "ad_interactions": visitor.get("ad_interactions", []),
            "social_interactions": visitor.get("social_interactions", []),
            "source": visitor.get("source", "organic"),
            "utm_params": visitor.get("utm_params", {}),
            "scores": visitor.get("scores", {
                "interest": 20,
                "heat": 15,
                "retention": 10,
                "purchase_intent": 10
            }),
            "consent": {
                "behavioral": True,
                "personal": True,
                "marketing": identification_data.get("consent_marketing", False)
            },
            "tags": [],
            "segments": [],
            "lifecycle_stage": "lead",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.contacts.insert_one(new_contact)
        
        # Mark visitor as merged
        await db.contacts_visitors.update_one(
            {"visitor_id": visitor_id},
            {"$set": {"merged_with": email, "is_identified": True}}
        )
        
        return {"success": True, "status": "created", "contact_email": email}


# ============================================
# SCORING
# ============================================

@router.post("/score/update")
async def update_contact_score(
    score_data: Dict[str, Any] = Body(...)
):
    """
    Met à jour les scores d'un contact.
    """
    db = get_db()
    
    identifier = score_data.get("email") or score_data.get("visitor_id")
    if not identifier:
        return {"success": False, "error": "email ou visitor_id requis"}
    
    score_updates = {}
    for key in ["interest", "heat", "retention", "purchase_intent"]:
        if key in score_data:
            score_updates[f"scores.{key}"] = score_data[key]
    
    if score_data.get("email"):
        await db.contacts.update_one(
            {"email": score_data["email"]},
            {"$set": score_updates}
        )
    else:
        await db.contacts_visitors.update_one(
            {"visitor_id": score_data["visitor_id"]},
            {"$set": score_updates}
        )
    
    return {"success": True, "updated_scores": list(score_updates.keys())}


# ============================================
# DASHBOARD & STATS
# ============================================

@router.get("/dashboard")
async def get_contact_engine_dashboard():
    """
    Dashboard du Contact Engine.
    """
    db = get_db()
    
    # Count visitors
    total_visitors = await db.contacts_visitors.count_documents({})
    anonymous_visitors = await db.contacts_visitors.count_documents({"is_identified": False})
    identified_visitors = await db.contacts_visitors.count_documents({"is_identified": True})
    
    # Count contacts
    total_contacts = await db.contacts.count_documents({})
    
    # Count events
    ad_events = await db.contacts_ads_events.count_documents({})
    social_events = await db.contacts_social_events.count_documents({})
    
    # Top sources
    pipeline = [
        {"$group": {"_id": "$source", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    top_sources = await db.contacts_visitors.aggregate(pipeline).to_list(5)
    
    # Average scores
    score_pipeline = [
        {"$group": {
            "_id": None,
            "avg_interest": {"$avg": "$scores.interest"},
            "avg_heat": {"$avg": "$scores.heat"},
            "avg_retention": {"$avg": "$scores.retention"},
            "avg_purchase_intent": {"$avg": "$scores.purchase_intent"}
        }}
    ]
    avg_scores_result = await db.contacts_visitors.aggregate(score_pipeline).to_list(1)
    avg_scores = avg_scores_result[0] if avg_scores_result else {}
    
    return {
        "success": True,
        "dashboard": {
            "visitors": {
                "total": total_visitors,
                "anonymous": anonymous_visitors,
                "identified": identified_visitors,
                "conversion_rate": round((identified_visitors / max(total_visitors, 1)) * 100, 2)
            },
            "contacts": {
                "total": total_contacts
            },
            "events": {
                "ad_clicks": ad_events,
                "social_interactions": social_events,
                "total": ad_events + social_events
            },
            "top_sources": top_sources,
            "average_scores": {
                "interest": round(avg_scores.get("avg_interest", 0), 1),
                "heat": round(avg_scores.get("avg_heat", 0), 1),
                "retention": round(avg_scores.get("avg_retention", 0), 1),
                "purchase_intent": round(avg_scores.get("avg_purchase_intent", 0), 1)
            }
        }
    }


@router.get("/contacts")
async def get_contacts(
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100),
    source: Optional[str] = None,
    is_identified: Optional[bool] = None,
    min_heat: Optional[int] = None
):
    """
    Liste des contacts avec filtres.
    """
    db = get_db()
    
    query = {}
    if source:
        query["source"] = source
    if is_identified is not None:
        query["is_identified"] = is_identified
    if min_heat:
        query["scores.heat"] = {"$gte": min_heat}
    
    skip = (page - 1) * limit
    
    contacts = await db.contacts_visitors.find(query).sort("last_seen", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.contacts_visitors.count_documents(query)
    
    # Remove MongoDB _id
    for contact in contacts:
        contact.pop("_id", None)
    
    return {
        "success": True,
        "contacts": contacts,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    }


logger.info("Contact Engine X300% initialized - LEGO V5 Module")
