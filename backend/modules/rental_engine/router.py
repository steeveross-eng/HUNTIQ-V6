"""
Rental Engine Router - Location de terres
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import os
from motor.motor_asyncio import AsyncIOMotorClient

router = APIRouter(prefix="/api/rental", tags=["rental"])

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'bionic_db')
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

class LandListing(BaseModel):
    title: str
    description: Optional[str] = None
    location: str
    price_per_day: float
    area_hectares: float
    species: List[str] = []
    amenities: List[str] = []

class Booking(BaseModel):
    land_id: str
    start_date: str
    end_date: str
    guests: int = 1

@router.get("/lands")
async def list_lands(limit: int = 20):
    lands = await db.lands_rental.find({"active": True}, {"_id": 0}).limit(limit).to_list(length=limit)
    return {"success": True, "lands": lands, "total": len(lands)}

@router.post("/lands")
async def create_listing(land: LandListing):
    land_doc = {
        **land.dict(),
        "created_at": datetime.now(timezone.utc),
        "active": True,
        "bookings": []
    }
    result = await db.lands_rental.insert_one(land_doc)
    return {"success": True, "land_id": str(result.inserted_id)}

@router.get("/lands/{land_id}")
async def get_land(land_id: str):
    land = await db.lands_rental.find_one({"_id": land_id}, {"_id": 0})
    if not land:
        raise HTTPException(status_code=404, detail="Terre non trouvée")
    return {"success": True, "land": land}

@router.post("/book")
async def book_land(booking: Booking):
    booking_doc = {
        **booking.dict(),
        "created_at": datetime.now(timezone.utc),
        "status": "pending"
    }
    await db.land_bookings.insert_one(booking_doc)
    return {"success": True, "message": "Réservation créée"}

@router.get("/bookings")
async def list_bookings(limit: int = 20):
    bookings = await db.land_bookings.find({}, {"_id": 0}).limit(limit).to_list(length=limit)
    return {"success": True, "bookings": bookings}
