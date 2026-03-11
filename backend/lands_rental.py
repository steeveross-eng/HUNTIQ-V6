"""
Module "Terres à Louer" - Location de terrains de chasse
- Gestion des annonces de terres
- Système d'ententes écrites sécurisées
- Monétisation multi-niveaux
- Zéro responsabilité légale pour la plateforme
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Dict, Any
from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

lands_router = APIRouter(prefix="/api/lands", tags=["Terres à Louer"])

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

class GameSpecies(str, Enum):
    ORIGNAL = "orignal"
    CHEVREUIL = "chevreuil"
    OURS = "ours"
    DINDON = "dindon"
    PETIT_GIBIER = "petit_gibier"
    MULTI_ESPECES = "multi_especes"

class TerrainType(str, Enum):
    FORET = "foret"
    MIXTE = "mixte"
    AGRICOLE = "agricole"
    MONTAGNE = "montagne"
    MARECAGE = "marecage"
    PRAIRIE = "prairie"

class AccessType(str, Enum):
    CHEMIN = "chemin"
    VTT = "vtt"
    QUATRE_ROUES = "4x4"
    STATIONNEMENT = "stationnement"
    ACCES_FACILE = "acces_facile"

class ListingStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    ACTIVE = "active"
    RENTED = "rented"
    EXPIRED = "expired"
    SUSPENDED = "suspended"

class AgreementStatus(str, Enum):
    DRAFT = "draft"
    PENDING_OWNER = "pending_owner"
    PENDING_RENTER = "pending_renter"
    SIGNED = "signed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    DISPUTED = "disputed"

# Quebec regions and hunting zones
QUEBEC_REGIONS = {
    "bas_saint_laurent": {"name": "Bas-Saint-Laurent", "zones": ["1", "2"]},
    "saguenay_lac_saint_jean": {"name": "Saguenay–Lac-Saint-Jean", "zones": ["28", "29"]},
    "capitale_nationale": {"name": "Capitale-Nationale", "zones": ["27"]},
    "mauricie": {"name": "Mauricie", "zones": ["26"]},
    "estrie": {"name": "Estrie", "zones": ["4", "5"]},
    "montreal": {"name": "Montréal", "zones": ["8"]},
    "outaouais": {"name": "Outaouais", "zones": ["10", "11", "12"]},
    "abitibi_temiscamingue": {"name": "Abitibi-Témiscamingue", "zones": ["13", "14", "15"]},
    "cote_nord": {"name": "Côte-Nord", "zones": ["18", "19", "20", "21"]},
    "nord_du_quebec": {"name": "Nord-du-Québec", "zones": ["22", "23", "24"]},
    "gaspesie": {"name": "Gaspésie–Îles-de-la-Madeleine", "zones": ["1", "2"]},
    "chaudiere_appalaches": {"name": "Chaudière-Appalaches", "zones": ["3", "4"]},
    "laval": {"name": "Laval", "zones": ["8"]},
    "lanaudiere": {"name": "Lanaudière", "zones": ["9"]},
    "laurentides": {"name": "Laurentides", "zones": ["9", "10"]},
    "monteregie": {"name": "Montérégie", "zones": ["6", "7", "8"]},
    "centre_du_quebec": {"name": "Centre-du-Québec", "zones": ["7"]}
}

HUNTING_ZONES = [str(i) for i in range(1, 30)]

# ============================================
# DEFAULT PRICING (Admin adjustable)
# ============================================

DEFAULT_PRICING = {
    # Publication fees
    "listing_basic": {"price": 4.99, "name": "Publication d'annonce", "description": "Publier une terre sur la plateforme"},
    "listing_featured_7": {"price": 10.99, "name": "Mise en vedette 7 jours", "description": "Annonce en haut des résultats pendant 7 jours"},
    "listing_featured_30": {"price": 29.99, "name": "Mise en vedette 30 jours", "description": "Annonce en haut des résultats pendant 30 jours"},
    "listing_auto_bump": {"price": 9.99, "name": "Remontée automatique", "description": "Votre annonce remonte chaque jour"},
    
    # Micro-payments
    "boost_24h": {"price": 3.99, "name": "Boost 24h", "description": "Booster l'annonce pendant 24 heures"},
    "badge_premium": {"price": 4.99, "name": "Badge Terrain Premium", "description": "Badge distinctif sur votre annonce"},
    "send_to_hunters": {"price": 7.99, "name": "Envoi ciblé", "description": "Envoyer l'annonce à 100 chasseurs ciblés"},
    "generate_agreement": {"price": 10.99, "name": "Entente légale", "description": "Générer une entente légale personnalisée"},
    "ai_analysis": {"price": 19.99, "name": "Analyse IA", "description": "Analyse IA complète du terrain (carte, accès, pente)"},
    
    # Premium subscriptions (Renter)
    "renter_basic": {"price": 4.99, "name": "Accès Chasseur Basic", "description": "Accès aux nouvelles terres 48h avant tout le monde", "duration_days": 30},
    "renter_pro": {"price": 9.99, "name": "Accès Chasseur Pro", "description": "Accès illimité + alertes personnalisées", "duration_days": 30},
    "renter_vip": {"price": 19.99, "name": "Accès Chasseur VIP", "description": "Accès VIP + terres exclusives + filtres avancés", "duration_days": 30},
    
    # Transaction fees (percentage)
    "owner_fee_percent": {"price": 10.0, "name": "Frais propriétaire", "description": "Frais de mise en relation (propriétaire)"},
    "renter_fee_percent": {"price": 10.0, "name": "Frais locataire", "description": "Frais de mise en relation (locataire)"}
}

# ============================================
# PYDANTIC MODELS
# ============================================

class LandListingCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=20, max_length=5000)
    
    # Location
    province: str = "Quebec"
    region: str
    mrc: Optional[str] = None
    city: Optional[str] = None
    hunting_zones: List[str] = []
    coordinates: Optional[Dict[str, float]] = None  # {"lat": x, "lng": y}
    
    # Land details
    surface_acres: float
    surface_hectares: Optional[float] = None
    terrain_types: List[TerrainType]
    access_types: List[AccessType]
    
    # Game & amenities
    game_species: List[GameSpecies]
    has_blinds: bool = False  # Caches
    has_salt_licks: bool = False  # Salines
    has_cameras: bool = False
    game_history: Optional[str] = None
    
    # Media
    photos: List[str] = []
    videos: List[str] = []
    
    # Pricing
    price_per_day: Optional[float] = None
    price_per_week: Optional[float] = None
    price_per_season: Optional[float] = None
    
    # Availability
    available_from: Optional[str] = None
    available_to: Optional[str] = None
    availability_notes: Optional[str] = None
    
    # Owner rules
    owner_rules: str = ""
    max_hunters: int = 4
    dogs_allowed: bool = False
    camping_allowed: bool = False
    fire_allowed: bool = False

class LandListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    region: Optional[str] = None
    mrc: Optional[str] = None
    city: Optional[str] = None
    hunting_zones: Optional[List[str]] = None
    coordinates: Optional[Dict[str, float]] = None
    surface_acres: Optional[float] = None
    terrain_types: Optional[List[TerrainType]] = None
    access_types: Optional[List[AccessType]] = None
    game_species: Optional[List[GameSpecies]] = None
    has_blinds: Optional[bool] = None
    has_salt_licks: Optional[bool] = None
    has_cameras: Optional[bool] = None
    game_history: Optional[str] = None
    photos: Optional[List[str]] = None
    videos: Optional[List[str]] = None
    price_per_day: Optional[float] = None
    price_per_week: Optional[float] = None
    price_per_season: Optional[float] = None
    available_from: Optional[str] = None
    available_to: Optional[str] = None
    availability_notes: Optional[str] = None
    owner_rules: Optional[str] = None
    max_hunters: Optional[int] = None
    dogs_allowed: Optional[bool] = None
    camping_allowed: Optional[bool] = None
    fire_allowed: Optional[bool] = None
    status: Optional[ListingStatus] = None

class RentalAgreementCreate(BaseModel):
    land_id: str
    start_date: str  # ISO format
    end_date: str
    total_price: float
    num_hunters: int = 1
    special_conditions: Optional[str] = None

class OwnerProfile(BaseModel):
    name: str
    email: str
    phone: str
    address: Optional[str] = None

class RenterProfile(BaseModel):
    name: str
    email: str
    phone: str
    hunting_license: Optional[str] = None

# ============================================
# HELPER FUNCTIONS
# ============================================

async def get_pricing():
    """Get current pricing (admin-adjustable)"""
    database = await get_db()
    pricing = await database.lands_pricing.find_one({"_id": "main"})
    if not pricing:
        pricing = DEFAULT_PRICING.copy()
        pricing["_id"] = "main"
        pricing["updated_at"] = datetime.now(timezone.utc).isoformat()
        await database.lands_pricing.insert_one(pricing)
        del pricing["_id"]
    else:
        del pricing["_id"]
    return pricing

def calculate_distance(lat1, lng1, lat2, lng2):
    """Calculate distance between two points in km (Haversine formula)"""
    from math import radians, sin, cos, sqrt, atan2
    R = 6371  # Earth's radius in km
    
    lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c

# ============================================
# LISTINGS API ENDPOINTS
# ============================================

@lands_router.get("/config")
async def get_lands_config():
    """Get configuration data for the lands module"""
    pricing = await get_pricing()
    
    return {
        "regions": QUEBEC_REGIONS,
        "hunting_zones": HUNTING_ZONES,
        "game_species": [{"id": s.value, "name": s.value.replace("_", " ").title()} for s in GameSpecies],
        "terrain_types": [{"id": t.value, "name": t.value.replace("_", " ").title()} for t in TerrainType],
        "access_types": [{"id": a.value, "name": a.value.replace("_", " ").title()} for a in AccessType],
        "pricing": pricing
    }

@lands_router.get("/listings")
async def get_land_listings(
    # Filters
    game_species: Optional[str] = None,  # Comma-separated
    region: Optional[str] = None,
    hunting_zone: Optional[str] = None,
    terrain_type: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_surface: Optional[float] = None,
    max_surface: Optional[float] = None,
    has_blinds: Optional[bool] = None,
    has_cameras: Optional[bool] = None,
    dogs_allowed: Optional[bool] = None,
    # Location-based
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    distance_km: Optional[float] = None,
    # Pagination & sorting
    page: int = 1,
    limit: int = 20,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    # Premium access
    renter_tier: Optional[str] = None  # basic, pro, vip
):
    """Get land listings with advanced filters"""
    database = await get_db()
    
    query = {"status": "active"}
    
    # Game species filter
    if game_species:
        species_list = game_species.split(",")
        query["game_species"] = {"$in": species_list}
    
    # Region filter
    if region:
        query["region"] = region
    
    # Hunting zone filter
    if hunting_zone:
        query["hunting_zones"] = hunting_zone
    
    # Terrain type filter
    if terrain_type:
        query["terrain_types"] = terrain_type
    
    # Price filters
    if min_price is not None or max_price is not None:
        price_query = {}
        if min_price is not None:
            price_query["$gte"] = min_price
        if max_price is not None:
            price_query["$lte"] = max_price
        query["$or"] = [
            {"price_per_day": price_query},
            {"price_per_week": price_query},
            {"price_per_season": price_query}
        ]
    
    # Surface filter
    if min_surface is not None:
        query["surface_acres"] = {"$gte": min_surface}
    if max_surface is not None:
        query.setdefault("surface_acres", {})["$lte"] = max_surface
    
    # Boolean filters
    if has_blinds is not None:
        query["has_blinds"] = has_blinds
    if has_cameras is not None:
        query["has_cameras"] = has_cameras
    if dogs_allowed is not None:
        query["dogs_allowed"] = dogs_allowed
    
    # Sorting
    sort_direction = -1 if sort_order == "desc" else 1
    
    # Featured listings first
    sort_fields = [("is_featured", -1), (sort_by, sort_direction)]
    
    # Get total count
    total = await database.land_listings.count_documents(query)
    
    # Get listings
    skip = (page - 1) * limit
    cursor = database.land_listings.find(query, {"_id": 0}).sort(sort_fields).skip(skip).limit(limit)
    listings = await cursor.to_list(limit)
    
    # Filter by distance if coordinates provided
    if lat is not None and lng is not None and distance_km is not None:
        filtered_listings = []
        for listing in listings:
            if listing.get("coordinates"):
                dist = calculate_distance(
                    lat, lng,
                    listing["coordinates"]["lat"],
                    listing["coordinates"]["lng"]
                )
                if dist <= distance_km:
                    listing["distance_km"] = round(dist, 1)
                    filtered_listings.append(listing)
        listings = filtered_listings
    
    # Premium content filtering
    if renter_tier not in ["pro", "vip"]:
        # Hide VIP-only listings for non-premium users
        listings = [l for l in listings if not l.get("vip_only", False)]
    
    return {
        "listings": listings,
        "total": total,
        "page": page,
        "total_pages": (total + limit - 1) // limit,
        "filters_applied": {
            "game_species": game_species,
            "region": region,
            "hunting_zone": hunting_zone
        }
    }

@lands_router.get("/listings/{listing_id}")
async def get_land_listing(listing_id: str):
    """Get a single land listing with full details"""
    database = await get_db()
    
    listing = await database.land_listings.find_one({"id": listing_id}, {"_id": 0})
    
    if not listing:
        raise HTTPException(status_code=404, detail="Annonce non trouvée")
    
    # Increment views
    await database.land_listings.update_one(
        {"id": listing_id},
        {"$inc": {"views": 1}}
    )
    
    # Get owner info (limited)
    owner = await database.land_owners.find_one({"id": listing.get("owner_id")}, {"_id": 0, "hashed_password": 0})
    
    return {
        "listing": listing,
        "owner": {
            "name": owner.get("name") if owner else "Propriétaire",
            "member_since": owner.get("created_at") if owner else None,
            "total_listings": owner.get("total_listings", 1) if owner else 1,
            "rating": owner.get("rating", 5.0) if owner else 5.0
        }
    }

@lands_router.post("/listings")
async def create_land_listing(
    listing: LandListingCreate,
    owner_id: str = Query(...)
):
    """Create a new land listing"""
    database = await get_db()
    
    # Verify owner exists
    owner = await database.land_owners.find_one({"id": owner_id})
    if not owner:
        raise HTTPException(status_code=404, detail="Propriétaire non trouvé")
    
    # Check if owner needs to pay for listing
    pricing = await get_pricing()
    listing_fee = pricing.get("listing_basic", {}).get("price", 4.99)
    
    # Create listing
    now = datetime.now(timezone.utc)
    listing_id = str(uuid.uuid4())
    
    listing_data = {
        "id": listing_id,
        "owner_id": owner_id,
        **listing.dict(),
        "surface_hectares": listing.surface_acres * 0.404686 if not listing.surface_hectares else listing.surface_hectares,
        "status": "pending",  # Requires payment to activate
        "is_featured": False,
        "is_premium": False,
        "vip_only": False,
        "has_badge_premium": False,
        "auto_bump_enabled": False,
        "views": 0,
        "inquiries": 0,
        "favorites": 0,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
        "expires_at": (now + timedelta(days=30)).isoformat(),
        "listing_fee_required": listing_fee,
        "listing_fee_paid": False
    }
    
    await database.land_listings.insert_one(listing_data)
    if "_id" in listing_data:
        del listing_data["_id"]
    
    # Update owner's listing count
    await database.land_owners.update_one(
        {"id": owner_id},
        {"$inc": {"total_listings": 1}}
    )
    
    return {
        "success": True,
        "listing": listing_data,
        "message": f"Annonce créée. Frais de publication: {listing_fee}$ pour activer.",
        "payment_required": listing_fee
    }

@lands_router.put("/listings/{listing_id}")
async def update_land_listing(
    listing_id: str,
    updates: LandListingUpdate,
    owner_id: str = Query(...)
):
    """Update a land listing"""
    database = await get_db()
    
    # Verify ownership
    listing = await database.land_listings.find_one({"id": listing_id, "owner_id": owner_id})
    if not listing:
        raise HTTPException(status_code=404, detail="Annonce non trouvée ou accès refusé")
    
    update_data = {k: v for k, v in updates.dict().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    if updates.surface_acres:
        update_data["surface_hectares"] = updates.surface_acres * 0.404686
    
    await database.land_listings.update_one(
        {"id": listing_id},
        {"$set": update_data}
    )
    
    return {"success": True, "message": "Annonce mise à jour"}

@lands_router.delete("/listings/{listing_id}")
async def delete_land_listing(listing_id: str, owner_id: str = Query(...)):
    """Delete a land listing"""
    database = await get_db()
    
    result = await database.land_listings.delete_one({"id": listing_id, "owner_id": owner_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Annonce non trouvée ou accès refusé")
    
    return {"success": True, "message": "Annonce supprimée"}

# ============================================
# OWNER REGISTRATION & AUTH
# ============================================

@lands_router.post("/owners/register")
async def register_owner(
    name: str = Query(...),
    email: str = Query(...),
    phone: str = Query(...),
    password: str = Query(...),
    address: Optional[str] = None
):
    """Register as a land owner"""
    database = await get_db()
    
    # Check if email exists
    existing = await database.land_owners.find_one({"email": email.lower()})
    if existing:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    
    import hashlib
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    owner_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    owner_data = {
        "id": owner_id,
        "name": name,
        "email": email.lower(),
        "phone": phone,
        "address": address,
        "hashed_password": hashed_password,
        "is_verified": False,
        "total_listings": 0,
        "total_rentals": 0,
        "rating": 5.0,
        "reviews_count": 0,
        "balance": 0.0,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat()
    }
    
    await database.land_owners.insert_one(owner_data)
    
    # Generate token
    token = hashlib.sha256(f"{owner_id}{now.isoformat()}".encode()).hexdigest()
    
    return {
        "success": True,
        "token": token,
        "owner": {k: v for k, v in owner_data.items() if k not in ["_id", "hashed_password"]}
    }

@lands_router.post("/owners/login")
async def login_owner(email: str = Query(...), password: str = Query(...)):
    """Login as a land owner"""
    database = await get_db()
    
    import hashlib
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    owner = await database.land_owners.find_one({
        "email": email.lower(),
        "hashed_password": hashed_password
    })
    
    if not owner:
        raise HTTPException(status_code=401, detail="Identifiants invalides")
    
    token = hashlib.sha256(f"{owner['id']}{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()
    
    return {
        "success": True,
        "token": token,
        "owner": {k: v for k, v in owner.items() if k not in ["_id", "hashed_password"]}
    }

# ============================================
# RENTER REGISTRATION & SUBSCRIPTIONS
# ============================================

@lands_router.post("/renters/register")
async def register_renter(
    name: str = Query(...),
    email: str = Query(...),
    phone: str = Query(...),
    password: str = Query(...),
    hunting_license: Optional[str] = None
):
    """Register as a renter (hunter)"""
    database = await get_db()
    
    existing = await database.land_renters.find_one({"email": email.lower()})
    if existing:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    
    import hashlib
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    renter_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    renter_data = {
        "id": renter_id,
        "name": name,
        "email": email.lower(),
        "phone": phone,
        "hunting_license": hunting_license,
        "hashed_password": hashed_password,
        "subscription_tier": "free",  # free, basic, pro, vip
        "subscription_expires": None,
        "total_rentals": 0,
        "rating": 5.0,
        "reviews_count": 0,
        "favorites": [],
        "alerts": [],
        "created_at": now.isoformat(),
        "updated_at": now.isoformat()
    }
    
    await database.land_renters.insert_one(renter_data)
    
    token = hashlib.sha256(f"{renter_id}{now.isoformat()}".encode()).hexdigest()
    
    return {
        "success": True,
        "token": token,
        "renter": {k: v for k, v in renter_data.items() if k not in ["_id", "hashed_password"]}
    }

@lands_router.post("/renters/login")
async def login_renter(email: str = Query(...), password: str = Query(...)):
    """Login as a renter"""
    database = await get_db()
    
    import hashlib
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    renter = await database.land_renters.find_one({
        "email": email.lower(),
        "hashed_password": hashed_password
    })
    
    if not renter:
        raise HTTPException(status_code=401, detail="Identifiants invalides")
    
    token = hashlib.sha256(f"{renter['id']}{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()
    
    return {
        "success": True,
        "token": token,
        "renter": {k: v for k, v in renter.items() if k not in ["_id", "hashed_password"]}
    }

@lands_router.get("/renters/{renter_id}/subscription")
async def get_renter_subscription(renter_id: str):
    """Get renter subscription status"""
    database = await get_db()
    
    renter = await database.land_renters.find_one({"id": renter_id}, {"_id": 0, "hashed_password": 0})
    if not renter:
        raise HTTPException(status_code=404, detail="Locataire non trouvé")
    
    pricing = await get_pricing()
    
    return {
        "current_tier": renter.get("subscription_tier", "free"),
        "expires": renter.get("subscription_expires"),
        "available_tiers": {
            "basic": pricing.get("renter_basic"),
            "pro": pricing.get("renter_pro"),
            "vip": pricing.get("renter_vip")
        }
    }

# ============================================
# RENTAL AGREEMENTS
# ============================================

@lands_router.post("/agreements")
async def create_rental_agreement(
    agreement: RentalAgreementCreate,
    renter_id: str = Query(...)
):
    """Create a rental agreement request"""
    database = await get_db()
    
    # Get land and owner
    land = await database.land_listings.find_one({"id": agreement.land_id, "status": "active"})
    if not land:
        raise HTTPException(status_code=404, detail="Terre non trouvée ou non disponible")
    
    owner = await database.land_owners.find_one({"id": land["owner_id"]})
    renter = await database.land_renters.find_one({"id": renter_id})
    
    if not renter:
        raise HTTPException(status_code=404, detail="Locataire non trouvé")
    
    # Calculate fees
    pricing = await get_pricing()
    owner_fee_percent = pricing.get("owner_fee_percent", {}).get("price", 10.0)
    renter_fee_percent = pricing.get("renter_fee_percent", {}).get("price", 10.0)
    
    owner_fee = round(agreement.total_price * (owner_fee_percent / 100), 2)
    renter_fee = round(agreement.total_price * (renter_fee_percent / 100), 2)
    
    agreement_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    agreement_data = {
        "id": agreement_id,
        "land_id": agreement.land_id,
        "land_title": land.get("title"),
        "owner_id": land["owner_id"],
        "owner_name": owner.get("name") if owner else "",
        "owner_email": owner.get("email") if owner else "",
        "owner_phone": owner.get("phone") if owner else "",
        "renter_id": renter_id,
        "renter_name": renter.get("name"),
        "renter_email": renter.get("email"),
        "renter_phone": renter.get("phone"),
        "renter_hunting_license": renter.get("hunting_license"),
        "start_date": agreement.start_date,
        "end_date": agreement.end_date,
        "total_price": agreement.total_price,
        "num_hunters": agreement.num_hunters,
        "special_conditions": agreement.special_conditions,
        
        # Fees (platform commission)
        "owner_fee": owner_fee,
        "renter_fee": renter_fee,
        "owner_fee_percent": owner_fee_percent,
        "renter_fee_percent": renter_fee_percent,
        
        # Status
        "status": "pending_owner",
        "owner_signed": False,
        "owner_signed_at": None,
        "renter_signed": False,
        "renter_signed_at": None,
        
        # Timestamps
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
        
        # Legal disclaimer
        "platform_disclaimer": "La plateforme n'est pas partie à cette entente et n'assume aucune responsabilité concernant la location, les accidents, blessures, pertes ou dommages."
    }
    
    await database.land_agreements.insert_one(agreement_data)
    
    return {
        "success": True,
        "agreement": {k: v for k, v in agreement_data.items() if k != "_id"},
        "fees": {
            "owner_fee": owner_fee,
            "renter_fee": renter_fee,
            "message": f"Frais de mise en relation: {renter_fee}$ (locataire) + {owner_fee}$ (propriétaire)"
        }
    }

@lands_router.put("/agreements/{agreement_id}/sign")
async def sign_agreement(
    agreement_id: str,
    signer_type: Literal["owner", "renter"] = Query(...),
    signer_id: str = Query(...),
    accept: bool = Query(...)
):
    """Sign or reject a rental agreement"""
    database = await get_db()
    
    agreement = await database.land_agreements.find_one({"id": agreement_id})
    if not agreement:
        raise HTTPException(status_code=404, detail="Entente non trouvée")
    
    # Verify signer
    if signer_type == "owner" and agreement["owner_id"] != signer_id:
        raise HTTPException(status_code=403, detail="Accès refusé")
    if signer_type == "renter" and agreement["renter_id"] != signer_id:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    now = datetime.now(timezone.utc)
    
    if not accept:
        # Reject agreement
        await database.land_agreements.update_one(
            {"id": agreement_id},
            {"$set": {
                "status": "cancelled",
                "cancelled_by": signer_type,
                "cancelled_at": now.isoformat(),
                "updated_at": now.isoformat()
            }}
        )
        return {"success": True, "message": "Entente refusée"}
    
    # Sign agreement
    update_data = {
        f"{signer_type}_signed": True,
        f"{signer_type}_signed_at": now.isoformat(),
        "updated_at": now.isoformat()
    }
    
    # Check if both parties have signed
    if signer_type == "owner" and agreement.get("renter_signed"):
        update_data["status"] = "signed"
    elif signer_type == "renter" and agreement.get("owner_signed"):
        update_data["status"] = "signed"
    else:
        update_data["status"] = f"pending_{('renter' if signer_type == 'owner' else 'owner')}"
    
    await database.land_agreements.update_one(
        {"id": agreement_id},
        {"$set": update_data}
    )
    
    return {
        "success": True,
        "message": "Entente signée",
        "status": update_data["status"],
        "both_signed": update_data["status"] == "signed"
    }

@lands_router.get("/agreements/{agreement_id}")
async def get_agreement(agreement_id: str):
    """Get agreement details"""
    database = await get_db()
    
    agreement = await database.land_agreements.find_one({"id": agreement_id}, {"_id": 0})
    if not agreement:
        raise HTTPException(status_code=404, detail="Entente non trouvée")
    
    return {"agreement": agreement}

@lands_router.get("/agreements/{agreement_id}/contract")
async def generate_contract_text(agreement_id: str):
    """Generate the legal contract text"""
    database = await get_db()
    
    agreement = await database.land_agreements.find_one({"id": agreement_id})
    if not agreement:
        raise HTTPException(status_code=404, detail="Entente non trouvée")
    
    land = await database.land_listings.find_one({"id": agreement["land_id"]})
    
    contract_text = f"""
═══════════════════════════════════════════════════════════════
              ENTENTE DE LOCATION DE TERRAIN DE CHASSE
                          (Modèle légal)
═══════════════════════════════════════════════════════════════

ENTRE :

Le Propriétaire :
  Nom : {agreement['owner_name']}
  Téléphone : {agreement['owner_phone']}
  Courriel : {agreement['owner_email']}

ET

Le Locataire :
  Nom : {agreement['renter_name']}
  Téléphone : {agreement['renter_phone']}
  Courriel : {agreement['renter_email']}
  Permis de chasse : {agreement.get('renter_hunting_license', 'Non fourni')}

───────────────────────────────────────────────────────────────
                           OBJET
───────────────────────────────────────────────────────────────

Location temporaire d'un terrain privé pour la pratique de la chasse.

Terrain : {agreement['land_title']}
{f"Superficie : {land.get('surface_acres', 'N/A')} acres" if land else ""}
{f"Région : {land.get('region', 'N/A')}" if land else ""}

───────────────────────────────────────────────────────────────
                          DURÉE
───────────────────────────────────────────────────────────────

Du : {agreement['start_date']}
Au : {agreement['end_date']}

Nombre de chasseurs autorisés : {agreement['num_hunters']}

───────────────────────────────────────────────────────────────
                        PRIX TOTAL
───────────────────────────────────────────────────────────────

Montant convenu : {agreement['total_price']:.2f} $

Le paiement est effectué directement entre le Propriétaire et 
le Locataire. La plateforme n'intervient pas dans la transaction.

───────────────────────────────────────────────────────────────
                   CONDITIONS GÉNÉRALES
───────────────────────────────────────────────────────────────

1. Le Locataire reconnaît que la chasse comporte des risques 
   inhérents et assume l'entière responsabilité de sa sécurité 
   et celle de ses invités.

2. Le Propriétaire n'est pas responsable des accidents, 
   blessures, pertes ou dommages survenant sur le terrain.

3. Le Locataire s'engage à respecter toutes les lois 
   provinciales et fédérales applicables à la chasse.

4. Le Locataire s'engage à ne causer aucun dommage au terrain, 
   aux installations ou à l'environnement.

5. Le Locataire doit quitter les lieux au plus tard à la date 
   de fin prévue dans cette entente.

6. Toute violation des présentes conditions entraîne la 
   résiliation immédiate de l'entente, sans remboursement.

7. ⚠️ IMPORTANT : La plateforme BIONIC™ n'est PAS partie à 
   cette entente et n'assume AUCUNE responsabilité concernant 
   la location, les accidents, blessures, pertes, dommages ou 
   tout litige entre les parties.

8. Cette entente est conclue directement entre le Propriétaire 
   et le Locataire. Tout différend doit être résolu entre eux.

{f'''
───────────────────────────────────────────────────────────────
                  CONDITIONS SPÉCIALES
───────────────────────────────────────────────────────────────

{agreement.get('special_conditions', '')}
''' if agreement.get('special_conditions') else ''}

───────────────────────────────────────────────────────────────
                       ACCEPTATION
───────────────────────────────────────────────────────────────

En signant électroniquement cette entente (case à cocher), 
les deux parties confirment avoir lu, compris et accepté 
l'ensemble des conditions ci-dessus.

Propriétaire : {'✓ SIGNÉ le ' + agreement['owner_signed_at'] if agreement.get('owner_signed') else '☐ En attente de signature'}

Locataire : {'✓ SIGNÉ le ' + agreement['renter_signed_at'] if agreement.get('renter_signed') else '☐ En attente de signature'}

───────────────────────────────────────────────────────────────
              Document généré automatiquement
                   Référence : {agreement['id'][:8].upper()}
                   Date : {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC
═══════════════════════════════════════════════════════════════
"""
    
    return {
        "contract_text": contract_text,
        "agreement_id": agreement_id,
        "status": agreement["status"],
        "owner_signed": agreement.get("owner_signed", False),
        "renter_signed": agreement.get("renter_signed", False)
    }

# ============================================
# MONETIZATION - PURCHASES
# ============================================

@lands_router.post("/purchase")
async def purchase_service(
    service_id: str = Query(...),
    user_type: Literal["owner", "renter"] = Query(...),
    user_id: str = Query(...),
    listing_id: Optional[str] = None,
    origin_url: str = Query(...)
):
    """Purchase a service (uses Stripe)"""
    database = await get_db()
    
    pricing = await get_pricing()
    service = pricing.get(service_id)
    
    if not service:
        raise HTTPException(status_code=400, detail="Service non trouvé")
    
    # Create purchase record
    purchase_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    purchase_data = {
        "id": purchase_id,
        "service_id": service_id,
        "service_name": service["name"],
        "amount": service["price"],
        "user_type": user_type,
        "user_id": user_id,
        "listing_id": listing_id,
        "status": "pending",
        "created_at": now.isoformat()
    }
    
    await database.lands_purchases.insert_one(purchase_data)
    
    # Create Stripe checkout session
    try:
        from emergentintegrations.payments.stripe.checkout import (
            StripeCheckout, 
            CheckoutSessionRequest
        )
        
        STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY", "")
        if not STRIPE_API_KEY:
            raise HTTPException(status_code=500, detail="Paiement non configuré")
        
        success_url = f"{origin_url}/terres?payment=success&purchase_id={purchase_id}"
        cancel_url = f"{origin_url}/terres?payment=cancelled"
        
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url="")
        
        checkout_request = CheckoutSessionRequest(
            amount=float(service["price"]),
            currency="cad",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "purchase_id": purchase_id,
                "service_id": service_id,
                "user_type": user_type,
                "user_id": user_id,
                "listing_id": listing_id or ""
            }
        )
        
        session = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Update purchase with session ID
        await database.lands_purchases.update_one(
            {"id": purchase_id},
            {"$set": {"stripe_session_id": session.session_id}}
        )
        
        return {
            "success": True,
            "checkout_url": session.url,
            "session_id": session.session_id,
            "purchase_id": purchase_id,
            "amount": service["price"],
            "service": service["name"]
        }
        
    except Exception as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@lands_router.get("/purchase/{purchase_id}/status")
async def get_purchase_status(purchase_id: str):
    """Check purchase status and apply benefits"""
    database = await get_db()
    
    purchase = await database.lands_purchases.find_one({"id": purchase_id})
    if not purchase:
        raise HTTPException(status_code=404, detail="Achat non trouvé")
    
    # If already completed, return
    if purchase.get("status") == "completed":
        return {"status": "completed", "applied": True}
    
    # Check Stripe status
    try:
        from emergentintegrations.payments.stripe.checkout import StripeCheckout
        
        STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY", "")
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url="")
        
        session_id = purchase.get("stripe_session_id")
        if not session_id:
            return {"status": "pending", "applied": False}
        
        checkout_status = await stripe_checkout.get_checkout_status(session_id)
        
        if checkout_status.payment_status == "paid":
            # Apply the benefit
            await apply_lands_purchase(database, purchase)
            
            return {"status": "completed", "applied": True}
        
        return {"status": purchase.get("status", "pending"), "applied": False}
        
    except Exception as e:
        logger.error(f"Status check error: {e}")
        return {"status": "error", "error": str(e)}

async def apply_lands_purchase(database, purchase):
    """Apply purchased benefits"""
    service_id = purchase["service_id"]
    listing_id = purchase.get("listing_id")
    user_id = purchase["user_id"]
    user_type = purchase["user_type"]
    now = datetime.now(timezone.utc)
    
    # Listing-related services
    if listing_id:
        update = {"updated_at": now.isoformat()}
        
        if service_id == "listing_basic":
            update["status"] = "active"
            update["listing_fee_paid"] = True
        elif service_id == "listing_featured_7":
            update["is_featured"] = True
            update["featured_until"] = (now + timedelta(days=7)).isoformat()
        elif service_id == "listing_featured_30":
            update["is_featured"] = True
            update["featured_until"] = (now + timedelta(days=30)).isoformat()
        elif service_id == "listing_auto_bump":
            update["auto_bump_enabled"] = True
            update["auto_bump_until"] = (now + timedelta(days=30)).isoformat()
        elif service_id == "boost_24h":
            update["boosted_until"] = (now + timedelta(hours=24)).isoformat()
        elif service_id == "badge_premium":
            update["has_badge_premium"] = True
            update["is_premium"] = True
        
        await database.land_listings.update_one(
            {"id": listing_id},
            {"$set": update}
        )
    
    # Subscription services
    pricing = await get_pricing()
    if service_id in ["renter_basic", "renter_pro", "renter_vip"]:
        tier = service_id.replace("renter_", "")
        duration = pricing.get(service_id, {}).get("duration_days", 30)
        
        await database.land_renters.update_one(
            {"id": user_id},
            {"$set": {
                "subscription_tier": tier,
                "subscription_expires": (now + timedelta(days=duration)).isoformat(),
                "updated_at": now.isoformat()
            }}
        )
    
    # Mark purchase as completed
    await database.lands_purchases.update_one(
        {"id": purchase["id"]},
        {"$set": {"status": "completed", "completed_at": now.isoformat()}}
    )

# ============================================
# ADMIN PRICING MANAGEMENT
# ============================================

@lands_router.get("/admin/pricing")
async def admin_get_pricing():
    """Get all pricing (admin)"""
    return await get_pricing()

@lands_router.put("/admin/pricing")
async def admin_update_pricing(updates: Dict[str, Any]):
    """Update pricing (admin)"""
    database = await get_db()
    
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await database.lands_pricing.update_one(
        {"_id": "main"},
        {"$set": updates},
        upsert=True
    )
    
    return {"success": True, "message": "Tarification mise à jour"}

@lands_router.get("/admin/stats")
async def admin_get_lands_stats():
    """Get lands module statistics (admin)"""
    database = await get_db()
    
    total_listings = await database.land_listings.count_documents({})
    active_listings = await database.land_listings.count_documents({"status": "active"})
    total_owners = await database.land_owners.count_documents({})
    total_renters = await database.land_renters.count_documents({})
    total_agreements = await database.land_agreements.count_documents({})
    signed_agreements = await database.land_agreements.count_documents({"status": "signed"})
    
    # Revenue
    purchases = await database.lands_purchases.find({"status": "completed"}).to_list(1000)
    total_revenue = sum(p.get("amount", 0) for p in purchases)
    
    # Premium renters
    premium_renters = await database.land_renters.count_documents({
        "subscription_tier": {"$in": ["basic", "pro", "vip"]}
    })
    
    return {
        "listings": {
            "total": total_listings,
            "active": active_listings,
            "pending": total_listings - active_listings
        },
        "users": {
            "owners": total_owners,
            "renters": total_renters,
            "premium_renters": premium_renters
        },
        "agreements": {
            "total": total_agreements,
            "signed": signed_agreements,
            "conversion_rate": round((signed_agreements / total_agreements * 100) if total_agreements > 0 else 0, 1)
        },
        "revenue": {
            "total": round(total_revenue, 2),
            "transactions": len(purchases)
        }
    }

logger.info("Terres à Louer module initialized")
