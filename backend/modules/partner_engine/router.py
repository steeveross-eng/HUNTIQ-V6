"""
Partner Engine Router
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import os
from motor.motor_asyncio import AsyncIOMotorClient

router = APIRouter(prefix="/api/partners", tags=["partners"])

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'bionic_db')
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

class Partner(BaseModel):
    name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    website: Optional[str] = None
    category: str = "pourvoirie"
    region: Optional[str] = None

class PartnerOffer(BaseModel):
    partner_id: str
    title: str
    description: str
    discount_percent: Optional[float] = None
    valid_until: Optional[str] = None
    code: Optional[str] = None

class PartnerEvent(BaseModel):
    partner_id: str
    title: str
    date: str
    location: Optional[str] = None
    description: Optional[str] = None

@router.get("/")
async def list_partners(category: Optional[str] = None, limit: int = 20):
    query = {"active": True}
    if category:
        query["category"] = category
    partners = await db.partners.find(query, {"_id": 0}).limit(limit).to_list(length=limit)
    return {"success": True, "partners": partners}

@router.post("/")
async def create_partner(partner: Partner):
    partner_doc = {
        **partner.dict(),
        "created_at": datetime.now(timezone.utc),
        "active": True
    }
    result = await db.partners.insert_one(partner_doc)
    return {"success": True, "partner_id": str(result.inserted_id)}

@router.get("/{partner_id}")
async def get_partner(partner_id: str):
    partner = await db.partners.find_one({"_id": partner_id}, {"_id": 0})
    if not partner:
        raise HTTPException(status_code=404, detail="Partenaire non trouvé")
    return {"success": True, "partner": partner}

# Offers
@router.get("/offers/all")
async def list_offers(limit: int = 20):
    offers = await db.partner_offers.find({"active": True}, {"_id": 0}).limit(limit).to_list(length=limit)
    return {"success": True, "offers": offers}

@router.post("/offers")
async def create_offer(offer: PartnerOffer):
    offer_doc = {
        **offer.dict(),
        "created_at": datetime.now(timezone.utc),
        "active": True
    }
    await db.partner_offers.insert_one(offer_doc)
    return {"success": True}

# Calendar/Events
@router.get("/events/all")
async def list_events(limit: int = 20):
    events = await db.partner_events.find({}, {"_id": 0}).sort("date", 1).limit(limit).to_list(length=limit)
    return {"success": True, "events": events}

@router.post("/events")
async def create_event(event: PartnerEvent):
    event_doc = {
        **event.dict(),
        "created_at": datetime.now(timezone.utc)
    }
    await db.partner_events.insert_one(event_doc)
    return {"success": True}
