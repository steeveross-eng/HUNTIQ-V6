"""
Hunt Marketplace API
Marketplace pour acheter, vendre ou louer des articles de chasse
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, timezone, timedelta
import uuid
import hashlib
import secrets
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging

logger = logging.getLogger(__name__)

marketplace_router = APIRouter(prefix="/api/marketplace", tags=["marketplace"])

# Database connection
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "bionic_territory")

client = None
db = None

async def get_db():
    global client, db
    if client is None:
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
    return db

# ============================================
# ENUMS & CONSTANTS
# ============================================

LISTING_CATEGORIES = [
    "equipement-chasse",
    "armes-munitions",
    "vetements",
    "optiques",
    "vehicules",
    "vtt-motoneige",
    "bateaux",
    "remorques",
    "camping-plein-air",
    "appeaux-leurres",
    "appats-attractants",
    "cameras-trail",
    "gps-electronique",
    "couteaux-outils",
    "taxidermie",
    "forfaits-guides",
    "terres-location",
    "pourvoiries",
    "services-specialises",
    "formation-cours",
    "autre"
]

LISTING_TYPES = [
    "a-vendre",
    "a-louer", 
    "forfait",
    "terre-a-louer",
    "service"
]

TARGET_SPECIES = [
    "orignal",
    "chevreuil",
    "ours",
    "caribou",
    "dindon",
    "oie",
    "canard",
    "petit-gibier",
    "predateurs",
    "tous"
]

LISTING_CONDITIONS = [
    "neuf",
    "comme-neuf",
    "excellent",
    "bon",
    "acceptable",
    "pour-pieces"
]

# ============================================
# PYDANTIC MODELS
# ============================================

class SellerRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: str = Field(..., min_length=2)
    phone: Optional[str] = None
    business_name: Optional[str] = None
    location: Optional[str] = None
    is_business: bool = False

class SellerLogin(BaseModel):
    email: EmailStr
    password: str

class SellerProfile(BaseModel):
    id: str
    email: str
    name: str
    phone: Optional[str] = None
    business_name: Optional[str] = None
    location: Optional[str] = None
    is_business: bool = False
    is_pro: bool = False
    is_verified: bool = False
    rating: float = 0.0
    total_sales: int = 0
    total_listings: int = 0
    free_listings_remaining: int = 3
    created_at: str
    subscription_type: Optional[str] = None  # "free", "pro", "business"

class ListingCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=100)
    description: str = Field(..., min_length=20, max_length=5000)
    price: float = Field(..., ge=0)
    price_negotiable: bool = False
    category: str
    listing_type: str  # a-vendre, a-louer, forfait, terre-a-louer, service
    condition: Optional[str] = None
    target_species: List[str] = []
    location: str
    region: Optional[str] = None
    photos: List[str] = []  # URLs des photos
    availability: str = "disponible"  # disponible, reserve, vendu
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    # For rentals/forfaits
    rental_period: Optional[str] = None  # jour, semaine, mois, saison
    rental_price_per: Optional[str] = None
    # For land/outfitters
    land_size_acres: Optional[float] = None
    species_on_land: List[str] = []
    amenities: List[str] = []

class ListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    price_negotiable: Optional[bool] = None
    category: Optional[str] = None
    listing_type: Optional[str] = None
    condition: Optional[str] = None
    target_species: Optional[List[str]] = None
    location: Optional[str] = None
    region: Optional[str] = None
    photos: Optional[List[str]] = None
    availability: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None

class ListingResponse(BaseModel):
    id: str
    seller_id: str
    seller_name: str
    seller_is_pro: bool = False
    seller_rating: float = 0.0
    title: str
    description: str
    price: float
    price_negotiable: bool = False
    category: str
    listing_type: str
    condition: Optional[str] = None
    target_species: List[str] = []
    location: str
    region: Optional[str] = None
    photos: List[str] = []
    availability: str = "disponible"
    views: int = 0
    favorites: int = 0
    is_featured: bool = False
    is_bumped: bool = False
    featured_until: Optional[str] = None
    created_at: str
    updated_at: str
    expires_at: str

class MessageCreate(BaseModel):
    listing_id: str
    message: str = Field(..., min_length=1, max_length=2000)

# ============================================
# HELPER FUNCTIONS
# ============================================

def hash_password(password: str) -> str:
    """Hash password with SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token() -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(32)

def serialize_listing(listing: dict, seller: dict = None) -> dict:
    """Convert MongoDB listing to response format"""
    return {
        "id": listing.get("id", str(listing.get("_id", ""))),
        "seller_id": listing.get("seller_id", ""),
        "seller_name": seller.get("name", "Vendeur") if seller else listing.get("seller_name", "Vendeur"),
        "seller_is_pro": seller.get("is_pro", False) if seller else listing.get("seller_is_pro", False),
        "seller_rating": seller.get("rating", 0.0) if seller else listing.get("seller_rating", 0.0),
        "title": listing.get("title", ""),
        "description": listing.get("description", ""),
        "price": listing.get("price", 0),
        "price_negotiable": listing.get("price_negotiable", False),
        "category": listing.get("category", ""),
        "listing_type": listing.get("listing_type", "a-vendre"),
        "condition": listing.get("condition"),
        "target_species": listing.get("target_species", []),
        "location": listing.get("location", ""),
        "region": listing.get("region"),
        "photos": listing.get("photos", []),
        "availability": listing.get("availability", "disponible"),
        "views": listing.get("views", 0),
        "favorites": listing.get("favorites", 0),
        "is_featured": listing.get("is_featured", False),
        "is_bumped": listing.get("is_bumped", False),
        "featured_until": listing.get("featured_until"),
        "created_at": listing.get("created_at", ""),
        "updated_at": listing.get("updated_at", ""),
        "expires_at": listing.get("expires_at", "")
    }

# ============================================
# SELLER AUTHENTICATION ENDPOINTS
# ============================================

@marketplace_router.post("/auth/register")
async def register_seller(data: SellerRegister):
    """Register a new seller account"""
    database = await get_db()
    
    # Check if email already exists
    existing = await database.marketplace_sellers.find_one({"email": data.email.lower()})
    if existing:
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")
    
    seller_id = str(uuid.uuid4())
    token = generate_token()
    now = datetime.now(timezone.utc).isoformat()
    
    seller = {
        "id": seller_id,
        "email": data.email.lower(),
        "password_hash": hash_password(data.password),
        "name": data.name,
        "phone": data.phone,
        "business_name": data.business_name,
        "location": data.location,
        "is_business": data.is_business,
        "is_pro": False,
        "is_verified": False,
        "rating": 0.0,
        "total_ratings": 0,
        "total_sales": 0,
        "total_listings": 0,
        "free_listings_remaining": 3,
        "subscription_type": "free",
        "token": token,
        "token_expires": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
        "created_at": now,
        "last_login": now
    }
    
    await database.marketplace_sellers.insert_one(seller)
    
    return {
        "success": True,
        "message": "Compte créé avec succès",
        "token": token,
        "seller": {
            "id": seller_id,
            "email": data.email.lower(),
            "name": data.name,
            "is_pro": False,
            "free_listings_remaining": 3
        }
    }

@marketplace_router.post("/auth/login")
async def login_seller(data: SellerLogin):
    """Login seller and return token"""
    database = await get_db()
    
    seller = await database.marketplace_sellers.find_one({
        "email": data.email.lower(),
        "password_hash": hash_password(data.password)
    })
    
    if not seller:
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    # Generate new token
    token = generate_token()
    now = datetime.now(timezone.utc).isoformat()
    
    await database.marketplace_sellers.update_one(
        {"id": seller["id"]},
        {
            "$set": {
                "token": token,
                "token_expires": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
                "last_login": now
            }
        }
    )
    
    return {
        "success": True,
        "token": token,
        "seller": {
            "id": seller["id"],
            "email": seller["email"],
            "name": seller["name"],
            "is_pro": seller.get("is_pro", False),
            "is_verified": seller.get("is_verified", False),
            "free_listings_remaining": seller.get("free_listings_remaining", 3),
            "subscription_type": seller.get("subscription_type", "free")
        }
    }

@marketplace_router.get("/auth/me")
async def get_current_seller(token: str = Query(...)):
    """Get current seller profile from token"""
    database = await get_db()
    
    seller = await database.marketplace_sellers.find_one({"token": token})
    if not seller:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")
    
    # Count active listings
    total_listings = await database.marketplace_listings.count_documents({
        "seller_id": seller["id"],
        "availability": {"$ne": "supprime"}
    })
    
    return SellerProfile(
        id=seller["id"],
        email=seller["email"],
        name=seller["name"],
        phone=seller.get("phone"),
        business_name=seller.get("business_name"),
        location=seller.get("location"),
        is_business=seller.get("is_business", False),
        is_pro=seller.get("is_pro", False),
        is_verified=seller.get("is_verified", False),
        rating=seller.get("rating", 0.0),
        total_sales=seller.get("total_sales", 0),
        total_listings=total_listings,
        free_listings_remaining=seller.get("free_listings_remaining", 3),
        created_at=seller.get("created_at", ""),
        subscription_type=seller.get("subscription_type", "free")
    )

# ============================================
# LISTING ENDPOINTS
# ============================================

@marketplace_router.post("/listings")
async def create_listing(data: ListingCreate, token: str = Query(...)):
    """Create a new listing"""
    database = await get_db()
    
    # Verify seller
    seller = await database.marketplace_sellers.find_one({"token": token})
    if not seller:
        raise HTTPException(status_code=401, detail="Authentification requise")
    
    # Check free listings limit for non-pro users
    if not seller.get("is_pro", False):
        active_listings = await database.marketplace_listings.count_documents({
            "seller_id": seller["id"],
            "availability": {"$ne": "supprime"}
        })
        if active_listings >= 3 and seller.get("free_listings_remaining", 0) <= 0:
            raise HTTPException(
                status_code=403, 
                detail="Limite d'annonces gratuites atteinte. Passez à PRO pour plus d'annonces."
            )
    
    # Validate category and type
    if data.category not in LISTING_CATEGORIES:
        raise HTTPException(status_code=400, detail="Catégorie invalide")
    if data.listing_type not in LISTING_TYPES:
        raise HTTPException(status_code=400, detail="Type d'offre invalide")
    
    listing_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    expires = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    
    listing = {
        "id": listing_id,
        "seller_id": seller["id"],
        "seller_name": seller["name"],
        "seller_is_pro": seller.get("is_pro", False),
        "seller_rating": seller.get("rating", 0.0),
        "title": data.title,
        "description": data.description,
        "price": data.price,
        "price_negotiable": data.price_negotiable,
        "category": data.category,
        "listing_type": data.listing_type,
        "condition": data.condition,
        "target_species": data.target_species,
        "location": data.location,
        "region": data.region,
        "photos": data.photos[:10],  # Max 10 photos
        "availability": "disponible",
        "contact_phone": data.contact_phone or seller.get("phone"),
        "contact_email": data.contact_email or seller["email"],
        "rental_period": data.rental_period,
        "rental_price_per": data.rental_price_per,
        "land_size_acres": data.land_size_acres,
        "species_on_land": data.species_on_land,
        "amenities": data.amenities,
        "views": 0,
        "favorites": 0,
        "is_featured": False,
        "is_bumped": False,
        "featured_until": None,
        "bumped_at": None,
        "created_at": now,
        "updated_at": now,
        "expires_at": expires
    }
    
    await database.marketplace_listings.insert_one(listing)
    
    # Decrement free listings if not pro
    if not seller.get("is_pro", False):
        await database.marketplace_sellers.update_one(
            {"id": seller["id"]},
            {"$inc": {"free_listings_remaining": -1}}
        )
    
    return {
        "success": True,
        "message": "Annonce créée avec succès",
        "listing": serialize_listing(listing, seller)
    }

@marketplace_router.get("/listings")
async def get_listings(
    category: Optional[str] = None,
    listing_type: Optional[str] = None,
    species: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    location: Optional[str] = None,
    region: Optional[str] = None,
    condition: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "recent",  # recent, price_asc, price_desc, popular
    page: int = 1,
    limit: int = 20
):
    """Get listings with filters"""
    database = await get_db()
    
    # Build query
    query = {"availability": {"$in": ["disponible", "reserve"]}}
    
    if category:
        query["category"] = category
    if listing_type:
        query["listing_type"] = listing_type
    if species:
        query["target_species"] = species
    if condition:
        query["condition"] = condition
    if region:
        query["region"] = {"$regex": region, "$options": "i"}
    if location:
        query["location"] = {"$regex": location, "$options": "i"}
    if min_price is not None:
        query["price"] = {"$gte": min_price}
    if max_price is not None:
        if "price" in query:
            query["price"]["$lte"] = max_price
        else:
            query["price"] = {"$lte": max_price}
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    # Sort options
    sort_options = {
        "recent": [("is_featured", -1), ("is_bumped", -1), ("created_at", -1)],
        "price_asc": [("is_featured", -1), ("price", 1)],
        "price_desc": [("is_featured", -1), ("price", -1)],
        "popular": [("is_featured", -1), ("views", -1)]
    }
    sort = sort_options.get(sort_by, sort_options["recent"])
    
    # Get total count
    total = await database.marketplace_listings.count_documents(query)
    
    # Get listings
    skip = (page - 1) * limit
    cursor = database.marketplace_listings.find(query).sort(sort).skip(skip).limit(limit)
    listings = await cursor.to_list(length=limit)
    
    return {
        "listings": [serialize_listing(l) for l in listings],
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit,
        "has_more": skip + len(listings) < total
    }

@marketplace_router.get("/listings/{listing_id}")
async def get_listing(listing_id: str):
    """Get a single listing and increment views"""
    database = await get_db()
    
    listing = await database.marketplace_listings.find_one({"id": listing_id})
    if not listing:
        raise HTTPException(status_code=404, detail="Annonce non trouvée")
    
    # Increment views
    await database.marketplace_listings.update_one(
        {"id": listing_id},
        {"$inc": {"views": 1}}
    )
    listing["views"] = listing.get("views", 0) + 1
    
    # Get seller info
    seller = await database.marketplace_sellers.find_one({"id": listing["seller_id"]})
    
    return serialize_listing(listing, seller)

@marketplace_router.put("/listings/{listing_id}")
async def update_listing(listing_id: str, data: ListingUpdate, token: str = Query(...)):
    """Update a listing"""
    database = await get_db()
    
    # Verify seller
    seller = await database.marketplace_sellers.find_one({"token": token})
    if not seller:
        raise HTTPException(status_code=401, detail="Authentification requise")
    
    # Get listing
    listing = await database.marketplace_listings.find_one({"id": listing_id})
    if not listing:
        raise HTTPException(status_code=404, detail="Annonce non trouvée")
    
    # Verify ownership
    if listing["seller_id"] != seller["id"]:
        raise HTTPException(status_code=403, detail="Vous n'êtes pas le propriétaire de cette annonce")
    
    # Build update
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await database.marketplace_listings.update_one(
        {"id": listing_id},
        {"$set": update_data}
    )
    
    updated = await database.marketplace_listings.find_one({"id": listing_id})
    return serialize_listing(updated, seller)

@marketplace_router.delete("/listings/{listing_id}")
async def delete_listing(listing_id: str, token: str = Query(...)):
    """Delete (soft) a listing"""
    database = await get_db()
    
    # Verify seller
    seller = await database.marketplace_sellers.find_one({"token": token})
    if not seller:
        raise HTTPException(status_code=401, detail="Authentification requise")
    
    # Get listing
    listing = await database.marketplace_listings.find_one({"id": listing_id})
    if not listing:
        raise HTTPException(status_code=404, detail="Annonce non trouvée")
    
    # Verify ownership
    if listing["seller_id"] != seller["id"]:
        raise HTTPException(status_code=403, detail="Vous n'êtes pas le propriétaire de cette annonce")
    
    # Soft delete
    await database.marketplace_listings.update_one(
        {"id": listing_id},
        {"$set": {"availability": "supprime", "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    # Restore free listing credit if not pro
    if not seller.get("is_pro", False):
        await database.marketplace_sellers.update_one(
            {"id": seller["id"]},
            {"$inc": {"free_listings_remaining": 1}}
        )
    
    return {"success": True, "message": "Annonce supprimée"}

@marketplace_router.get("/my-listings")
async def get_my_listings(token: str = Query(...), page: int = 1, limit: int = 20):
    """Get current seller's listings"""
    database = await get_db()
    
    seller = await database.marketplace_sellers.find_one({"token": token})
    if not seller:
        raise HTTPException(status_code=401, detail="Authentification requise")
    
    query = {"seller_id": seller["id"], "availability": {"$ne": "supprime"}}
    total = await database.marketplace_listings.count_documents(query)
    
    skip = (page - 1) * limit
    cursor = database.marketplace_listings.find(query).sort("created_at", -1).skip(skip).limit(limit)
    listings = await cursor.to_list(length=limit)
    
    return {
        "listings": [serialize_listing(l, seller) for l in listings],
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit,
        "seller": {
            "id": seller["id"],
            "name": seller["name"],
            "is_pro": seller.get("is_pro", False),
            "free_listings_remaining": seller.get("free_listings_remaining", 3)
        }
    }

# ============================================
# FAVORITES ENDPOINT
# ============================================

@marketplace_router.post("/listings/{listing_id}/favorite")
async def toggle_favorite(listing_id: str, token: str = Query(...)):
    """Toggle favorite on a listing"""
    database = await get_db()
    
    seller = await database.marketplace_sellers.find_one({"token": token})
    if not seller:
        raise HTTPException(status_code=401, detail="Authentification requise")
    
    # Check if already favorited
    existing = await database.marketplace_favorites.find_one({
        "user_id": seller["id"],
        "listing_id": listing_id
    })
    
    if existing:
        # Remove favorite
        await database.marketplace_favorites.delete_one({"_id": existing["_id"]})
        await database.marketplace_listings.update_one(
            {"id": listing_id},
            {"$inc": {"favorites": -1}}
        )
        return {"success": True, "favorited": False}
    else:
        # Add favorite
        await database.marketplace_favorites.insert_one({
            "user_id": seller["id"],
            "listing_id": listing_id,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        await database.marketplace_listings.update_one(
            {"id": listing_id},
            {"$inc": {"favorites": 1}}
        )
        return {"success": True, "favorited": True}

@marketplace_router.get("/favorites")
async def get_favorites(token: str = Query(...)):
    """Get user's favorite listings"""
    database = await get_db()
    
    seller = await database.marketplace_sellers.find_one({"token": token})
    if not seller:
        raise HTTPException(status_code=401, detail="Authentification requise")
    
    favorites = await database.marketplace_favorites.find({"user_id": seller["id"]}).to_list(length=100)
    listing_ids = [f["listing_id"] for f in favorites]
    
    listings = await database.marketplace_listings.find({
        "id": {"$in": listing_ids},
        "availability": {"$ne": "supprime"}
    }).to_list(length=100)
    
    return {"listings": [serialize_listing(l) for l in listings]}

# ============================================
# MESSAGING ENDPOINTS
# ============================================

@marketplace_router.post("/messages")
async def send_message(data: MessageCreate, token: str = Query(...)):
    """Send a message to a listing seller"""
    database = await get_db()
    
    sender = await database.marketplace_sellers.find_one({"token": token})
    if not sender:
        raise HTTPException(status_code=401, detail="Authentification requise")
    
    listing = await database.marketplace_listings.find_one({"id": data.listing_id})
    if not listing:
        raise HTTPException(status_code=404, detail="Annonce non trouvée")
    
    message = {
        "id": str(uuid.uuid4()),
        "listing_id": data.listing_id,
        "listing_title": listing["title"],
        "sender_id": sender["id"],
        "sender_name": sender["name"],
        "receiver_id": listing["seller_id"],
        "message": data.message,
        "read": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await database.marketplace_messages.insert_one(message)
    
    return {"success": True, "message": "Message envoyé"}

@marketplace_router.get("/messages")
async def get_messages(token: str = Query(...)):
    """Get all messages for current user"""
    database = await get_db()
    
    seller = await database.marketplace_sellers.find_one({"token": token})
    if not seller:
        raise HTTPException(status_code=401, detail="Authentification requise")
    
    # Get received messages
    received = await database.marketplace_messages.find({
        "receiver_id": seller["id"]
    }).sort("created_at", -1).to_list(length=100)
    
    # Get sent messages
    sent = await database.marketplace_messages.find({
        "sender_id": seller["id"]
    }).sort("created_at", -1).to_list(length=100)
    
    return {
        "received": [{
            "id": m["id"],
            "listing_id": m["listing_id"],
            "listing_title": m["listing_title"],
            "sender_name": m["sender_name"],
            "message": m["message"],
            "read": m["read"],
            "created_at": m["created_at"]
        } for m in received],
        "sent": [{
            "id": m["id"],
            "listing_id": m["listing_id"],
            "listing_title": m["listing_title"],
            "message": m["message"],
            "created_at": m["created_at"]
        } for m in sent],
        "unread_count": sum(1 for m in received if not m["read"])
    }

# ============================================
# CATEGORIES & FILTERS ENDPOINT
# ============================================

@marketplace_router.get("/categories")
async def get_categories():
    """Get all available categories and filters"""
    return {
        "categories": [
            {"id": "equipement-chasse", "name": "Équipement de chasse", "icon": "🎯"},
            {"id": "armes-munitions", "name": "Armes & Munitions", "icon": "🔫"},
            {"id": "vetements", "name": "Vêtements", "icon": "🧥"},
            {"id": "optiques", "name": "Optiques", "icon": "🔭"},
            {"id": "vehicules", "name": "Véhicules", "icon": "🚗"},
            {"id": "vtt-motoneige", "name": "VTT & Motoneige", "icon": "🏍️"},
            {"id": "bateaux", "name": "Bateaux", "icon": "🚤"},
            {"id": "remorques", "name": "Remorques", "icon": "🚛"},
            {"id": "camping-plein-air", "name": "Camping & Plein air", "icon": "⛺"},
            {"id": "appeaux-leurres", "name": "Appeaux & Leurres", "icon": "🦆"},
            {"id": "appats-attractants", "name": "Appâts & Attractants", "icon": "🧪"},
            {"id": "cameras-trail", "name": "Caméras trail", "icon": "📷"},
            {"id": "gps-electronique", "name": "GPS & Électronique", "icon": "📡"},
            {"id": "couteaux-outils", "name": "Couteaux & Outils", "icon": "🔪"},
            {"id": "taxidermie", "name": "Taxidermie", "icon": "🦌"},
            {"id": "forfaits-guides", "name": "Forfaits guidés", "icon": "🧭"},
            {"id": "terres-location", "name": "Terres à louer", "icon": "🏞️"},
            {"id": "pourvoiries", "name": "Pourvoiries", "icon": "🏕️"},
            {"id": "services-specialises", "name": "Services spécialisés", "icon": "🛠️"},
            {"id": "formation-cours", "name": "Formation & Cours", "icon": "📚"},
            {"id": "autre", "name": "Autre", "icon": "📦"}
        ],
        "listing_types": [
            {"id": "a-vendre", "name": "À vendre", "icon": "💰"},
            {"id": "a-louer", "name": "À louer", "icon": "🔄"},
            {"id": "forfait", "name": "Forfait", "icon": "📋"},
            {"id": "terre-a-louer", "name": "Terre à louer", "icon": "🏞️"},
            {"id": "service", "name": "Service", "icon": "🛠️"}
        ],
        "species": [
            {"id": "orignal", "name": "Orignal", "emoji": "🫎"},
            {"id": "chevreuil", "name": "Chevreuil", "emoji": "🦌"},
            {"id": "ours", "name": "Ours", "emoji": "🐻"},
            {"id": "caribou", "name": "Caribou", "emoji": "🦌"},
            {"id": "dindon", "name": "Dindon sauvage", "emoji": "🦃"},
            {"id": "oie", "name": "Oie", "emoji": "🪿"},
            {"id": "canard", "name": "Canard", "emoji": "🦆"},
            {"id": "petit-gibier", "name": "Petit gibier", "emoji": "🐇"},
            {"id": "predateurs", "name": "Prédateurs", "emoji": "🦊"},
            {"id": "tous", "name": "Tous", "emoji": "🎯"}
        ],
        "conditions": [
            {"id": "neuf", "name": "Neuf"},
            {"id": "comme-neuf", "name": "Comme neuf"},
            {"id": "excellent", "name": "Excellent état"},
            {"id": "bon", "name": "Bon état"},
            {"id": "acceptable", "name": "Acceptable"},
            {"id": "pour-pieces", "name": "Pour pièces"}
        ],
        "regions": [
            "Abitibi-Témiscamingue",
            "Bas-Saint-Laurent",
            "Capitale-Nationale",
            "Centre-du-Québec",
            "Chaudière-Appalaches",
            "Côte-Nord",
            "Estrie",
            "Gaspésie-Îles-de-la-Madeleine",
            "Lanaudière",
            "Laurentides",
            "Laval",
            "Mauricie",
            "Montérégie",
            "Montréal",
            "Nord-du-Québec",
            "Outaouais",
            "Saguenay-Lac-Saint-Jean"
        ]
    }

# ============================================
# STATS ENDPOINT
# ============================================

@marketplace_router.get("/stats")
async def get_marketplace_stats():
    """Get marketplace statistics"""
    database = await get_db()
    
    total_listings = await database.marketplace_listings.count_documents({
        "availability": {"$in": ["disponible", "reserve"]}
    })
    
    total_sellers = await database.marketplace_sellers.count_documents({})
    
    # Get category counts
    pipeline = [
        {"$match": {"availability": {"$in": ["disponible", "reserve"]}}},
        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    category_counts = await database.marketplace_listings.aggregate(pipeline).to_list(length=50)
    
    return {
        "total_listings": total_listings,
        "total_sellers": total_sellers,
        "categories": {c["_id"]: c["count"] for c in category_counts},
        "featured_count": await database.marketplace_listings.count_documents({"is_featured": True})
    }

logger.info("Hunt Marketplace API initialized")
