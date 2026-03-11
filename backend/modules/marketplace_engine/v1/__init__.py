"""Marketplace Engine Module v1

C2C marketplace for hunting equipment.
Extracted from marketplace.py.

Version: 1.0.0
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime, timezone
from enum import Enum
import uuid
import os
from pymongo import MongoClient

router = APIRouter(prefix="/api/v1/marketplace", tags=["Marketplace Engine"])


# ============================================
# MODELS
# ============================================

class ListingCategory(str, Enum):
    WEAPONS = "weapons"
    OPTICS = "optics"
    CLOTHING = "clothing"
    ACCESSORIES = "accessories"
    ATTRACTANTS = "attractants"
    VEHICLES = "vehicles"
    CAMPING = "camping"
    OTHER = "other"


class ListingCondition(str, Enum):
    NEW = "new"
    LIKE_NEW = "like_new"
    GOOD = "good"
    FAIR = "fair"
    PARTS = "parts"


class ListingStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    SOLD = "sold"
    EXPIRED = "expired"
    REMOVED = "removed"


class Listing(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    seller_id: str
    title: str
    description: str
    category: ListingCategory
    condition: ListingCondition
    price: float
    negotiable: bool = True
    location: str
    images: List[str] = []
    status: ListingStatus = ListingStatus.ACTIVE
    views: int = 0
    favorites: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None


class Review(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    listing_id: Optional[str] = None
    seller_id: str
    buyer_id: str
    rating: int = Field(ge=1, le=5)
    comment: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    listing_id: str
    sender_id: str
    receiver_id: str
    content: str
    is_read: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ============================================
# SERVICE
# ============================================

class MarketplaceService:
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'test_database')
        self._client = None
        self._db = None
    
    @property
    def db(self):
        if self._db is None:
            self._client = MongoClient(self.mongo_url)
            self._db = self._client[self.db_name]
        return self._db
    
    async def list_listings(self, category: str = None, condition: str = None,
                            min_price: float = None, max_price: float = None,
                            location: str = None, skip: int = 0, limit: int = 50) -> List[Dict]:
        query = {"status": "active"}
        if category:
            query["category"] = category
        if condition:
            query["condition"] = condition
        if min_price is not None:
            query["price"] = {"$gte": min_price}
        if max_price is not None:
            query.setdefault("price", {})["$lte"] = max_price
        if location:
            query["location"] = {"$regex": location, "$options": "i"}
        
        cursor = self.db.marketplace_listings.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit)
        return list(cursor)
    
    async def get_listing(self, listing_id: str) -> Optional[Dict]:
        # Increment view count
        self.db.marketplace_listings.update_one(
            {"id": listing_id},
            {"$inc": {"views": 1}}
        )
        return self.db.marketplace_listings.find_one({"id": listing_id}, {"_id": 0})
    
    async def create_listing(self, listing: Listing) -> Listing:
        l_dict = listing.model_dump()
        l_dict.pop("_id", None)
        self.db.marketplace_listings.insert_one(l_dict)
        return listing
    
    async def update_listing(self, listing_id: str, updates: Dict) -> Optional[Dict]:
        self.db.marketplace_listings.update_one(
            {"id": listing_id},
            {"$set": updates}
        )
        return await self.get_listing(listing_id)
    
    async def search_listings(self, query: str, limit: int = 20) -> List[Dict]:
        cursor = self.db.marketplace_listings.find(
            {
                "status": "active",
                "$or": [
                    {"title": {"$regex": query, "$options": "i"}},
                    {"description": {"$regex": query, "$options": "i"}}
                ]
            },
            {"_id": 0}
        ).limit(limit)
        return list(cursor)
    
    async def get_seller_listings(self, seller_id: str) -> List[Dict]:
        cursor = self.db.marketplace_listings.find(
            {"seller_id": seller_id},
            {"_id": 0}
        ).sort("created_at", -1)
        return list(cursor)
    
    async def get_seller_rating(self, seller_id: str) -> Dict:
        pipeline = [
            {"$match": {"seller_id": seller_id}},
            {"$group": {
                "_id": "$seller_id",
                "avg_rating": {"$avg": "$rating"},
                "total_reviews": {"$sum": 1}
            }}
        ]
        result = list(self.db.marketplace_reviews.aggregate(pipeline))
        if result:
            return {"avg_rating": round(result[0]["avg_rating"], 1), "total_reviews": result[0]["total_reviews"]}
        return {"avg_rating": 0, "total_reviews": 0}


_service = MarketplaceService()


# ============================================
# ROUTES
# ============================================

@router.get("/")
async def marketplace_engine_info():
    return {
        "module": "marketplace_engine",
        "version": "1.0.0",
        "description": "C2C marketplace for hunting equipment",
        "features": [
            "Listing management",
            "Search and filter",
            "Seller profiles",
            "Reviews and ratings",
            "Messaging"
        ],
        "categories": [c.value for c in ListingCategory],
        "conditions": [c.value for c in ListingCondition]
    }


@router.get("/listings")
async def list_listings(
    category: Optional[str] = None,
    condition: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    location: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    listings = await _service.list_listings(category, condition, min_price, max_price, location, skip, limit)
    return {"success": True, "total": len(listings), "listings": listings}


@router.get("/listings/{listing_id}")
async def get_listing(listing_id: str):
    listing = await _service.get_listing(listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return {"success": True, "listing": listing}


@router.post("/listings")
async def create_listing(listing: Listing):
    created = await _service.create_listing(listing)
    return {"success": True, "listing": created.model_dump()}


@router.put("/listings/{listing_id}")
async def update_listing(listing_id: str, updates: dict):
    updated = await _service.update_listing(listing_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Listing not found")
    return {"success": True, "listing": updated}


@router.get("/search")
async def search_listings(q: str = Query(..., min_length=2), limit: int = Query(20, ge=1, le=50)):
    listings = await _service.search_listings(q, limit)
    return {"success": True, "query": q, "results": listings}


@router.get("/seller/{seller_id}/listings")
async def get_seller_listings(seller_id: str):
    listings = await _service.get_seller_listings(seller_id)
    return {"success": True, "listings": listings}


@router.get("/seller/{seller_id}/rating")
async def get_seller_rating(seller_id: str):
    rating = await _service.get_seller_rating(seller_id)
    return {"success": True, "rating": rating}


@router.get("/categories")
async def list_categories():
    return {
        "success": True,
        "categories": [
            {"id": c.value, "name": _get_category_name(c)}
            for c in ListingCategory
        ]
    }


def _get_category_name(c: ListingCategory) -> str:
    names = {
        ListingCategory.WEAPONS: "Armes",
        ListingCategory.OPTICS: "Optiques",
        ListingCategory.CLOTHING: "Vêtements",
        ListingCategory.ACCESSORIES: "Accessoires",
        ListingCategory.ATTRACTANTS: "Attractants",
        ListingCategory.VEHICLES: "Véhicules",
        ListingCategory.CAMPING: "Camping",
        ListingCategory.OTHER: "Autres"
    }
    return names.get(c, c.value)
