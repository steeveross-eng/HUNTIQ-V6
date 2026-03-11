"""
Territory Module - Territories Inventory (CRUD, scoring, scraping, sync)
Phase 1.8 - Split from territory.py
Router prefix: /api/territories
"""
import re
import os
import logging
from datetime import datetime, timezone
from typing import Optional, List
from enum import Enum

from fastapi import HTTPException, BackgroundTasks, Query
from pydantic import BaseModel, Field
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from ._base import territories_router, logger

# Database connection (separate from territory_router's get_db — uses top-level client)
MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME", "huntiq")

_inv_client = AsyncIOMotorClient(MONGO_URL)
_inv_db = _inv_client[DB_NAME]


# ============================================
# ENUMS & CONSTANTS
# ============================================

class EstablishmentType(str, Enum):
    ZEC = "zec"
    SEPAQ = "sepaq"
    POURVOIRIE = "pourvoirie"
    CLUB = "club"
    OUTFITTER = "outfitter"
    PRIVATE = "private"
    ANTICOSTI = "anticosti"
    RESERVE = "reserve"
    INDIGENOUS = "indigenous"


class Province(str, Enum):
    QC = "QC"; ON = "ON"; NB = "NB"; NS = "NS"; PE = "PE"; NL = "NL"
    MB = "MB"; SK = "SK"; AB = "AB"; BC = "BC"; YT = "YT"; NT = "NT"; NU = "NU"


class Species(str, Enum):
    ORIGNAL = "orignal"; CHEVREUIL = "chevreuil"; OURS = "ours"
    CARIBOU = "caribou"; WAPITI = "wapiti"; CERF_MULET = "cerf_mulet"
    DINDON = "dindon"; PETIT_GIBIER = "petit_gibier"; SAUVAGINE = "sauvagine"
    GRIZZLY = "grizzly"; COUGAR = "cougar"


PROVINCE_NAMES = {
    "QC": "Qu\u00e9bec", "ON": "Ontario", "NB": "Nouveau-Brunswick",
    "NS": "Nouvelle-\u00c9cosse", "PE": "\u00cele-du-Prince-\u00c9douard",
    "NL": "Terre-Neuve-et-Labrador", "MB": "Manitoba", "SK": "Saskatchewan",
    "AB": "Alberta", "BC": "Colombie-Britannique", "YT": "Yukon",
    "NT": "Territoires du Nord-Ouest", "NU": "Nunavut"
}

TYPE_LABELS = {
    "zec": {"fr": "ZEC", "en": "ZEC", "icon": "tent"},
    "sepaq": {"fr": "R\u00e9serve faunique (S\u00e9paq)", "en": "Wildlife Reserve (S\u00e9paq)", "icon": "deer"},
    "pourvoirie": {"fr": "Pourvoirie", "en": "Outfitter", "icon": "house"},
    "club": {"fr": "Club priv\u00e9", "en": "Private Club", "icon": "target"},
    "outfitter": {"fr": "Outfitter", "en": "Outfitter", "icon": "bison"},
    "private": {"fr": "Territoire priv\u00e9", "en": "Private Territory", "icon": "lock"},
    "anticosti": {"fr": "Anticosti", "en": "Anticosti", "icon": "island"},
    "reserve": {"fr": "R\u00e9serve", "en": "Reserve", "icon": "tree"},
    "indigenous": {"fr": "Territoire autochtone", "en": "Indigenous Territory", "icon": "feather"}
}

SPECIES_CONFIG = {
    "orignal": {"fr": "Orignal", "en": "Moose", "icon": "moose"},
    "chevreuil": {"fr": "Chevreuil", "en": "White-tailed Deer", "icon": "deer"},
    "ours": {"fr": "Ours noir", "en": "Black Bear", "icon": "bear"},
    "caribou": {"fr": "Caribou", "en": "Caribou", "icon": "deer"},
    "wapiti": {"fr": "Wapiti", "en": "Elk", "icon": "deer"},
    "cerf_mulet": {"fr": "Cerf mulet", "en": "Mule Deer", "icon": "deer"},
    "dindon": {"fr": "Dindon sauvage", "en": "Wild Turkey", "icon": "turkey"},
    "petit_gibier": {"fr": "Petit gibier", "en": "Small Game", "icon": "rabbit"},
    "sauvagine": {"fr": "Sauvagine", "en": "Waterfowl", "icon": "duck"},
    "grizzly": {"fr": "Grizzly", "en": "Grizzly Bear", "icon": "bear"},
    "cougar": {"fr": "Cougar", "en": "Cougar", "icon": "lion"}
}


# ============================================
# PYDANTIC MODELS (inventory-specific)
# ============================================

class HuntingZone(BaseModel):
    zone_id: str
    name: str
    description: Optional[str] = None
    species: List[str] = []
    quota: Optional[int] = None
    season_start: Optional[str] = None
    season_end: Optional[str] = None


class TerritoryScoring(BaseModel):
    habitat_index: float = Field(0.0, ge=0, le=100)
    pressure_index: float = Field(0.0, ge=0, le=100)
    success_index: float = Field(0.0, ge=0, le=100)
    accessibility_index: float = Field(0.0, ge=0, le=100)
    global_score: float = Field(0.0, ge=0, le=100)
    last_calculated: Optional[str] = None


class TerritoryCoordinates(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    polygon: Optional[List[List[float]]] = None
    center: Optional[List[float]] = None


class TerritoryServices(BaseModel):
    accommodation: bool = False
    guided_hunts: bool = False
    equipment_rental: bool = False
    meat_processing: bool = False
    transportation: bool = False
    meals_included: bool = False
    fishing: bool = False
    atv_access: bool = False
    boat_access: bool = False
    dog_friendly: bool = False


class TerritoryCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    establishment_type: str
    province: str
    region: Optional[str] = None
    hunting_zones: List[str] = []
    species: List[str] = []
    description: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    coordinates: Optional[TerritoryCoordinates] = None
    services: Optional[TerritoryServices] = None
    price_range: Optional[str] = None
    success_rate: Optional[float] = None
    surface_area: Optional[float] = None
    official_map_url: Optional[str] = None
    source_url: Optional[str] = None
    is_verified: bool = False
    is_partner: bool = False


class TerritoryUpdate(BaseModel):
    name: Optional[str] = None
    establishment_type: Optional[str] = None
    province: Optional[str] = None
    region: Optional[str] = None
    hunting_zones: Optional[List[str]] = None
    species: Optional[List[str]] = None
    description: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    coordinates: Optional[TerritoryCoordinates] = None
    services: Optional[TerritoryServices] = None
    price_range: Optional[str] = None
    success_rate: Optional[float] = None
    surface_area: Optional[float] = None
    official_map_url: Optional[str] = None
    source_url: Optional[str] = None
    is_verified: Optional[bool] = None
    is_partner: Optional[bool] = None


class ScrapingSource(BaseModel):
    name: str
    url: str
    source_type: str
    province: Optional[str] = None
    enabled: bool = True
    last_scraped: Optional[str] = None
    items_found: int = 0


# ============================================
# HELPER FUNCTIONS
# ============================================

def serialize_doc(doc: dict) -> dict:
    if doc is None:
        return None
    result = {}
    for key, value in doc.items():
        if key == '_id':
            result['id'] = str(value)
        elif isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, datetime):
            result[key] = value.isoformat()
        else:
            result[key] = value
    return result


def generate_internal_id(establishment_type: str, name: str, province: str, zone: str = None) -> str:
    clean_name = re.sub(r'[^a-zA-Z0-9]', '', name.upper())[:15]
    type_prefixes = {
        "zec": "ZEC", "sepaq": "RF", "pourvoirie": "PV", "club": "CLUB",
        "outfitter": "OUT", "private": "PRIV", "anticosti": "ANT",
        "reserve": "RES", "indigenous": "IND"
    }
    prefix = type_prefixes.get(establishment_type, "TER")
    if zone:
        zone_clean = re.sub(r'[^a-zA-Z0-9]', '', zone.upper())[:5]
        return f"{prefix}-{clean_name}-{zone_clean}"
    return f"{prefix}-{clean_name}-{province}"


def calculate_global_score(scoring: dict) -> float:
    h = scoring.get('habitat_index', 0)
    p = scoring.get('pressure_index', 50)
    s = scoring.get('success_index', 0)
    a = scoring.get('accessibility_index', 0)
    p_inverted = 100 - p
    global_score = (h * 0.35) + (s * 0.30) + (a * 0.20) + (p_inverted * 0.15)
    return round(global_score, 1)


# ============================================
# API ENDPOINTS - TERRITORIES CRUD
# ============================================

@territories_router.get("/types")
async def get_establishment_types():
    return {"success": True, "types": TYPE_LABELS}


@territories_router.get("/provinces")
async def get_provinces():
    return {"success": True, "provinces": PROVINCE_NAMES}


@territories_router.get("/species")
async def get_species():
    return {"success": True, "species": SPECIES_CONFIG}


@territories_router.post("", response_model=dict)
async def create_territory(territory: TerritoryCreate):
    try:
        internal_id = generate_internal_id(
            territory.establishment_type, territory.name, territory.province,
            territory.hunting_zones[0] if territory.hunting_zones else None
        )
        existing = await _inv_db.territories.find_one({
            "$or": [{"internal_id": internal_id}, {"name": territory.name, "province": territory.province}]
        })
        if existing:
            raise HTTPException(status_code=400, detail="Ce territoire existe d\u00e9j\u00e0")
        doc = {
            "internal_id": internal_id, "name": territory.name,
            "establishment_type": territory.establishment_type,
            "province": territory.province, "region": territory.region,
            "hunting_zones": territory.hunting_zones, "species": territory.species,
            "description": territory.description, "website": territory.website,
            "email": territory.email, "phone": territory.phone,
            "address": territory.address,
            "coordinates": territory.coordinates.dict() if territory.coordinates else None,
            "services": territory.services.dict() if territory.services else None,
            "price_range": territory.price_range, "success_rate": territory.success_rate,
            "surface_area": territory.surface_area,
            "official_map_url": territory.official_map_url,
            "source_url": territory.source_url,
            "is_verified": territory.is_verified, "is_partner": territory.is_partner,
            "scoring": {"habitat_index": 0, "pressure_index": 50,
                        "success_index": territory.success_rate or 0,
                        "accessibility_index": 0, "global_score": 0, "last_calculated": None},
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "scraped_at": None, "status": "active"
        }
        result = await _inv_db.territories.insert_one(doc)
        territory_id = str(result.inserted_id)
        doc['id'] = territory_id
        doc.pop('_id', None)
        logger.info(f"Created territory: {internal_id}")
        try:
            await sync_territory_to_partnership(territory_id, doc)
        except Exception as sync_err:
            logger.warning(f"Auto-sync to partnership failed: {sync_err}")
        return {"success": True, "message": "Territoire cr\u00e9\u00e9 avec succ\u00e8s", "territory": serialize_doc(doc)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating territory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@territories_router.get("", response_model=dict)
async def list_territories(
    page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100),
    establishment_type: Optional[str] = None, province: Optional[str] = None,
    species: Optional[str] = None, search: Optional[str] = None,
    is_verified: Optional[bool] = None, is_partner: Optional[bool] = None,
    min_score: Optional[float] = None, sort_by: str = "global_score"
):
    try:
        query = {"status": "active"}
        if establishment_type: query["establishment_type"] = establishment_type
        if province: query["province"] = province
        if species: query["species"] = {"$in": [species]}
        if is_verified is not None: query["is_verified"] = is_verified
        if is_partner is not None: query["is_partner"] = is_partner
        if min_score is not None: query["scoring.global_score"] = {"$gte": min_score}
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"region": {"$regex": search, "$options": "i"}},
                {"internal_id": {"$regex": search, "$options": "i"}}
            ]
        sort_options = {
            "global_score": [("scoring.global_score", -1)], "name": [("name", 1)],
            "created_at": [("created_at", -1)], "success_rate": [("success_rate", -1)]
        }
        sort = sort_options.get(sort_by, [("scoring.global_score", -1)])
        skip = (page - 1) * limit
        cursor = _inv_db.territories.find(query).sort(sort).skip(skip).limit(limit)
        territories = await cursor.to_list(length=limit)
        total = await _inv_db.territories.count_documents(query)
        return {
            "success": True,
            "territories": [serialize_doc(t) for t in territories],
            "pagination": {"page": page, "limit": limit, "total": total, "pages": (total + limit - 1) // limit}
        }
    except Exception as e:
        logger.error(f"Error listing territories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@territories_router.get("/stats")
async def get_territory_stats_inv():
    try:
        type_pipeline = [{"$match": {"status": "active"}}, {"$group": {"_id": "$establishment_type", "count": {"$sum": 1}}}]
        type_counts = await _inv_db.territories.aggregate(type_pipeline).to_list(20)
        province_pipeline = [{"$match": {"status": "active"}}, {"$group": {"_id": "$province", "count": {"$sum": 1}}}]
        province_counts = await _inv_db.territories.aggregate(province_pipeline).to_list(20)
        species_pipeline = [{"$match": {"status": "active"}}, {"$unwind": "$species"}, {"$group": {"_id": "$species", "count": {"$sum": 1}}}]
        species_counts = await _inv_db.territories.aggregate(species_pipeline).to_list(20)
        total = await _inv_db.territories.count_documents({"status": "active"})
        verified = await _inv_db.territories.count_documents({"status": "active", "is_verified": True})
        partners = await _inv_db.territories.count_documents({"status": "active", "is_partner": True})
        score_pipeline = [{"$match": {"status": "active", "scoring.global_score": {"$gt": 0}}}, {"$group": {"_id": None, "avg_score": {"$avg": "$scoring.global_score"}}}]
        score_result = await _inv_db.territories.aggregate(score_pipeline).to_list(1)
        avg_score = round(score_result[0]["avg_score"], 1) if score_result else 0
        return {
            "success": True,
            "stats": {
                "total": total, "verified": verified, "partners": partners, "avg_score": avg_score,
                "by_type": {item["_id"]: item["count"] for item in type_counts},
                "by_province": {item["_id"]: item["count"] for item in province_counts},
                "by_species": {item["_id"]: item["count"] for item in species_counts}
            }
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@territories_router.get("/{territory_id}")
async def get_territory(territory_id: str):
    try:
        try: query = {"_id": ObjectId(territory_id)}
        except Exception: query = {"internal_id": territory_id}
        territory = await _inv_db.territories.find_one(query)
        if not territory:
            raise HTTPException(status_code=404, detail="Territoire non trouv\u00e9")
        return {"success": True, "territory": serialize_doc(territory)}
    except HTTPException: raise
    except Exception as e:
        logger.error(f"Error getting territory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@territories_router.put("/{territory_id}")
async def update_territory(territory_id: str, update: TerritoryUpdate):
    try:
        update_doc = {"updated_at": datetime.now(timezone.utc)}
        for field, value in update.dict(exclude_unset=True).items():
            if value is not None:
                if field in ["coordinates", "services"] and isinstance(value, dict):
                    update_doc[field] = value
                else:
                    update_doc[field] = value
        try: query = {"_id": ObjectId(territory_id)}
        except Exception: query = {"internal_id": territory_id}
        result = await _inv_db.territories.update_one(query, {"$set": update_doc})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Territoire non trouv\u00e9")
        territory = await _inv_db.territories.find_one(query)
        try:
            await sync_territory_to_partnership(str(territory['_id']), territory)
        except Exception as sync_err:
            logger.warning(f"Auto-sync to partnership failed: {sync_err}")
        return {"success": True, "message": "Territoire mis \u00e0 jour", "territory": serialize_doc(territory)}
    except HTTPException: raise
    except Exception as e:
        logger.error(f"Error updating territory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@territories_router.delete("/{territory_id}")
async def delete_territory(territory_id: str):
    try:
        try: query = {"_id": ObjectId(territory_id)}
        except Exception: query = {"internal_id": territory_id}
        result = await _inv_db.territories.update_one(query, {"$set": {"status": "deleted", "deleted_at": datetime.now(timezone.utc)}})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Territoire non trouv\u00e9")
        return {"success": True, "message": "Territoire supprim\u00e9"}
    except HTTPException: raise
    except Exception as e:
        logger.error(f"Error deleting territory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# SCORING
# ============================================

@territories_router.post("/{territory_id}/calculate-score")
async def calculate_territory_score(territory_id: str):
    try:
        try: query = {"_id": ObjectId(territory_id)}
        except Exception: query = {"internal_id": territory_id}
        territory = await _inv_db.territories.find_one(query)
        if not territory:
            raise HTTPException(status_code=404, detail="Territoire non trouv\u00e9")
        scoring = territory.get("scoring", {})
        global_score = calculate_global_score(scoring)
        await _inv_db.territories.update_one(query, {"$set": {"scoring.global_score": global_score, "scoring.last_calculated": datetime.now(timezone.utc).isoformat()}})
        return {"success": True, "territory_id": territory_id, "global_score": global_score, "scoring": {**scoring, "global_score": global_score}}
    except HTTPException: raise
    except Exception as e:
        logger.error(f"Error calculating score: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@territories_router.put("/{territory_id}/scoring")
async def update_territory_scoring(territory_id: str, scoring: TerritoryScoring):
    try:
        try: query = {"_id": ObjectId(territory_id)}
        except Exception: query = {"internal_id": territory_id}
        scoring_dict = scoring.dict()
        global_score = calculate_global_score(scoring_dict)
        scoring_dict["global_score"] = global_score
        scoring_dict["last_calculated"] = datetime.now(timezone.utc).isoformat()
        result = await _inv_db.territories.update_one(query, {"$set": {"scoring": scoring_dict, "updated_at": datetime.now(timezone.utc)}})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Territoire non trouv\u00e9")
        return {"success": True, "message": "Scoring mis \u00e0 jour", "scoring": scoring_dict}
    except HTTPException: raise
    except Exception as e:
        logger.error(f"Error updating scoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# SCRAPING SOURCES
# ============================================

@territories_router.get("/scraping/sources")
async def get_scraping_sources():
    try:
        sources = await _inv_db.scraping_sources.find({}).to_list(100)
        if not sources:
            default_sources = [
                {"name": "Association des pourvoiries du Qu\u00e9bec", "url": "https://www.pourvoiries.com/pourvoiries", "source_type": "pourvoiries", "province": "QC", "enabled": True, "last_scraped": None, "items_found": 0},
                {"name": "CHA-ACC Pourvoiries", "url": "https://cha-acc.com/pourvoirie/", "source_type": "pourvoiries", "province": None, "enabled": True, "last_scraped": None, "items_found": 0},
                {"name": "White Hills Outfitters", "url": "http://whitehillsoutfitters.com/", "source_type": "outfitters", "province": "NL", "enabled": True, "last_scraped": None, "items_found": 0},
                {"name": "S\u00e9paq - R\u00e9serves fauniques", "url": "https://www.sepaq.com/rf/", "source_type": "sepaq", "province": "QC", "enabled": True, "last_scraped": None, "items_found": 0},
                {"name": "ZECs Qu\u00e9bec", "url": "https://www.zecquebec.com/", "source_type": "zecs", "province": "QC", "enabled": True, "last_scraped": None, "items_found": 0}
            ]
            await _inv_db.scraping_sources.insert_many(default_sources)
            sources = default_sources
        return {"success": True, "sources": [serialize_doc(s) for s in sources]}
    except Exception as e:
        logger.error(f"Error getting scraping sources: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@territories_router.post("/scraping/sources")
async def add_scraping_source(source: ScrapingSource):
    try:
        doc = source.dict()
        doc["created_at"] = datetime.now(timezone.utc)
        result = await _inv_db.scraping_sources.insert_one(doc)
        doc["id"] = str(result.inserted_id)
        return {"success": True, "message": "Source ajout\u00e9e", "source": doc}
    except Exception as e:
        logger.error(f"Error adding scraping source: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# BATCH IMPORT
# ============================================

@territories_router.post("/import/batch")
async def batch_import_territories(territories: List[TerritoryCreate]):
    try:
        created = 0; skipped = 0; errors = []
        for territory in territories:
            try:
                internal_id = generate_internal_id(territory.establishment_type, territory.name, territory.province, territory.hunting_zones[0] if territory.hunting_zones else None)
                existing = await _inv_db.territories.find_one({"internal_id": internal_id})
                if existing:
                    skipped += 1; continue
                doc = {
                    "internal_id": internal_id, "name": territory.name,
                    "establishment_type": territory.establishment_type,
                    "province": territory.province, "region": territory.region,
                    "hunting_zones": territory.hunting_zones, "species": territory.species,
                    "description": territory.description, "website": territory.website,
                    "email": territory.email, "phone": territory.phone, "address": territory.address,
                    "coordinates": territory.coordinates.dict() if territory.coordinates else None,
                    "services": territory.services.dict() if territory.services else None,
                    "price_range": territory.price_range, "success_rate": territory.success_rate,
                    "surface_area": territory.surface_area,
                    "official_map_url": territory.official_map_url,
                    "source_url": territory.source_url,
                    "is_verified": territory.is_verified, "is_partner": territory.is_partner,
                    "scoring": {"habitat_index": 0, "pressure_index": 50,
                                "success_index": territory.success_rate or 0,
                                "accessibility_index": 0, "global_score": 0, "last_calculated": None},
                    "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc),
                    "status": "active"
                }
                await _inv_db.territories.insert_one(doc)
                created += 1
            except Exception as e:
                errors.append({"name": territory.name, "error": str(e)})
        return {"success": True, "message": f"Import termin\u00e9: {created} cr\u00e9\u00e9s, {skipped} ignor\u00e9s",
                "created": created, "skipped": skipped, "errors": errors}
    except Exception as e:
        logger.error(f"Error in batch import: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# SEARCH & RECOMMENDATIONS
# ============================================

@territories_router.get("/search/advanced")
async def advanced_search(
    q: Optional[str] = None, types: Optional[str] = None,
    provinces: Optional[str] = None, species: Optional[str] = None,
    min_score: Optional[float] = None, max_pressure: Optional[float] = None,
    has_accommodation: Optional[bool] = None, has_guided: Optional[bool] = None,
    price_range: Optional[str] = None, limit: int = Query(20, ge=1, le=100)
):
    try:
        query = {"status": "active"}
        if q:
            query["$or"] = [{"name": {"$regex": q, "$options": "i"}}, {"region": {"$regex": q, "$options": "i"}}, {"description": {"$regex": q, "$options": "i"}}]
        if types:
            query["establishment_type"] = {"$in": [t.strip() for t in types.split(",")]}
        if provinces:
            query["province"] = {"$in": [p.strip() for p in provinces.split(",")]}
        if species:
            query["species"] = {"$in": [s.strip() for s in species.split(",")]}
        if min_score is not None:
            query["scoring.global_score"] = {"$gte": min_score}
        if max_pressure is not None:
            query["scoring.pressure_index"] = {"$lte": max_pressure}
        if has_accommodation:
            query["services.accommodation"] = True
        if has_guided:
            query["services.guided_hunts"] = True
        if price_range:
            query["price_range"] = price_range
        cursor = _inv_db.territories.find(query).sort([("scoring.global_score", -1)]).limit(limit)
        results = await cursor.to_list(length=limit)
        return {"success": True, "count": len(results), "territories": [serialize_doc(t) for t in results]}
    except Exception as e:
        logger.error(f"Error in advanced search: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@territories_router.get("/recommendations/{species}")
async def get_recommendations_by_species(species: str, province: Optional[str] = None, limit: int = Query(10, ge=1, le=50)):
    try:
        query = {"status": "active", "species": {"$in": [species]}}
        if province:
            query["province"] = province
        cursor = _inv_db.territories.find(query).sort([("scoring.global_score", -1), ("success_rate", -1)]).limit(limit)
        results = await cursor.to_list(length=limit)
        return {"success": True, "species": species, "species_info": SPECIES_CONFIG.get(species, {}),
                "count": len(results), "recommendations": [serialize_doc(t) for t in results]}
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# SEED DATA
# ============================================

async def seed_sample_territories():
    sample_territories = [
        {"name": "ZEC Bas-Saint-Laurent", "establishment_type": "zec", "province": "QC", "region": "Bas-Saint-Laurent", "hunting_zones": ["Zone 2", "Zone 3"], "species": ["orignal", "chevreuil", "ours", "petit_gibier"], "description": "Grande ZEC offrant une diversit\u00e9 d'habitats.", "website": "https://www.zecquebec.com/", "surface_area": 1250.0, "success_rate": 35.5, "is_verified": True, "scoring": {"habitat_index": 78, "pressure_index": 45, "success_index": 35.5, "accessibility_index": 70}},
        {"name": "ZEC Chapais", "establishment_type": "zec", "province": "QC", "region": "Nord-du-Qu\u00e9bec", "hunting_zones": ["Zone 17", "Zone 22"], "species": ["orignal", "ours", "petit_gibier"], "description": "ZEC nordique avec forte population d'orignaux.", "surface_area": 2100.0, "success_rate": 42.0, "is_verified": True, "scoring": {"habitat_index": 85, "pressure_index": 25, "success_index": 42, "accessibility_index": 55}},
        {"name": "R\u00e9serve faunique de Matane", "establishment_type": "sepaq", "province": "QC", "region": "Gasp\u00e9sie", "hunting_zones": ["Secteur A", "Secteur B", "Secteur C"], "species": ["orignal", "chevreuil", "ours"], "description": "R\u00e9serve faunique renomm\u00e9e.", "website": "https://www.sepaq.com/rf/mat/", "surface_area": 1282.0, "success_rate": 48.5, "is_verified": True, "scoring": {"habitat_index": 92, "pressure_index": 55, "success_index": 48.5, "accessibility_index": 75}},
        {"name": "R\u00e9serve faunique des Chic-Chocs", "establishment_type": "sepaq", "province": "QC", "region": "Gasp\u00e9sie", "hunting_zones": ["Zone 4", "Zone 5"], "species": ["orignal", "caribou"], "description": "Territoire montagneux unique.", "website": "https://www.sepaq.com/rf/chc/", "surface_area": 1127.0, "success_rate": 38.0, "is_verified": True, "scoring": {"habitat_index": 88, "pressure_index": 30, "success_index": 38, "accessibility_index": 45}},
        {"name": "R\u00e9serve faunique Duni\u00e8re", "establishment_type": "sepaq", "province": "QC", "region": "Bas-Saint-Laurent", "hunting_zones": ["Zone 2"], "species": ["orignal", "chevreuil", "ours", "petit_gibier"], "description": "R\u00e9serve accessible.", "surface_area": 780.0, "success_rate": 41.0, "is_verified": True, "scoring": {"habitat_index": 80, "pressure_index": 50, "success_index": 41, "accessibility_index": 80}},
        {"name": "Pourvoirie Lechasseur", "establishment_type": "pourvoirie", "province": "QC", "region": "Laurentides", "hunting_zones": ["Zone 4"], "species": ["orignal", "chevreuil", "ours", "dindon"], "description": "Pourvoirie familiale.", "website": "https://www.pourvoirie-lechasseur.com/", "price_range": "$$$", "success_rate": 55.0, "is_verified": True, "services": {"accommodation": True, "guided_hunts": True, "meals_included": True, "meat_processing": True}, "scoring": {"habitat_index": 75, "pressure_index": 60, "success_index": 55, "accessibility_index": 85}},
        {"name": "Club Appalaches", "establishment_type": "club", "province": "QC", "region": "Chaudi\u00e8re-Appalaches", "hunting_zones": ["Zone 4"], "species": ["chevreuil", "dindon", "petit_gibier"], "description": "Club priv\u00e9.", "success_rate": 62.0, "is_verified": True, "services": {"guided_hunts": True}, "scoring": {"habitat_index": 70, "pressure_index": 35, "success_index": 62, "accessibility_index": 75}},
        {"name": "\u00cele d'Anticosti - Secteur Est", "establishment_type": "anticosti", "province": "QC", "region": "C\u00f4te-Nord", "hunting_zones": ["Zone 1", "Zone 2"], "species": ["chevreuil"], "description": "Destination l\u00e9gendaire.", "website": "https://www.sepaq.com/rf/ant/", "success_rate": 95.0, "is_verified": True, "services": {"accommodation": True, "guided_hunts": True, "transportation": True}, "scoring": {"habitat_index": 95, "pressure_index": 40, "success_index": 95, "accessibility_index": 60}},
        {"name": "\u00cele d'Anticosti - Secteur Ouest", "establishment_type": "anticosti", "province": "QC", "region": "C\u00f4te-Nord", "hunting_zones": ["Zone 3", "Zone 4"], "species": ["chevreuil"], "description": "Secteur ouest.", "success_rate": 92.0, "is_verified": True, "services": {"accommodation": True, "guided_hunts": True}, "scoring": {"habitat_index": 93, "pressure_index": 45, "success_index": 92, "accessibility_index": 55}},
        {"name": "Moose Valley Outfitters", "establishment_type": "outfitter", "province": "NB", "region": "Northern New Brunswick", "hunting_zones": ["Zone 6"], "species": ["orignal", "ours", "chevreuil"], "description": "Premier outfitter du NB.", "website": "https://moosevalleyoutfitters.com/", "price_range": "$$$$", "success_rate": 85.0, "is_verified": True, "services": {"accommodation": True, "guided_hunts": True, "meals_included": True, "transportation": True}, "scoring": {"habitat_index": 88, "pressure_index": 30, "success_index": 85, "accessibility_index": 70}},
        {"name": "White Hills Outfitters", "establishment_type": "outfitter", "province": "NL", "region": "Terre-Neuve", "hunting_zones": ["Zone 45", "Zone 46"], "species": ["orignal", "caribou", "ours"], "description": "Outfitter sp\u00e9cialis\u00e9.", "website": "http://whitehillsoutfitters.com/", "price_range": "$$$$", "success_rate": 78.0, "is_verified": True, "services": {"accommodation": True, "guided_hunts": True, "meals_included": True, "transportation": True, "meat_processing": True}, "scoring": {"habitat_index": 90, "pressure_index": 20, "success_index": 78, "accessibility_index": 50}},
        {"name": "Alberta Elk Outfitters", "establishment_type": "outfitter", "province": "AB", "region": "Rocky Mountains", "hunting_zones": ["WMU 400", "WMU 402"], "species": ["wapiti", "cerf_mulet", "ours"], "description": "Chasse au wapiti.", "price_range": "$$$$", "success_rate": 70.0, "is_verified": False, "services": {"accommodation": True, "guided_hunts": True, "meals_included": True}, "scoring": {"habitat_index": 85, "pressure_index": 35, "success_index": 70, "accessibility_index": 60}},
        {"name": "Saskatchewan Trophy Whitetail", "establishment_type": "outfitter", "province": "SK", "region": "Saskatchewan", "hunting_zones": ["Zone 43"], "species": ["chevreuil"], "description": "Chevreuils troph\u00e9es.", "price_range": "$$$$", "success_rate": 88.0, "is_verified": False, "services": {"accommodation": True, "guided_hunts": True, "meals_included": True}, "scoring": {"habitat_index": 80, "pressure_index": 40, "success_index": 88, "accessibility_index": 65}},
        {"name": "BC Grizzly Adventures", "establishment_type": "outfitter", "province": "BC", "region": "Northern BC", "hunting_zones": ["Region 6", "Region 7"], "species": ["grizzly", "orignal", "ours"], "description": "Chasse au grizzly.", "price_range": "$$$$", "success_rate": 65.0, "is_verified": False, "services": {"accommodation": True, "guided_hunts": True, "transportation": True}, "scoring": {"habitat_index": 92, "pressure_index": 15, "success_index": 65, "accessibility_index": 35}},
        {"name": "Algoma Bear Outfitters", "establishment_type": "outfitter", "province": "ON", "region": "Algoma", "hunting_zones": ["WMU 21A", "WMU 21B"], "species": ["ours", "orignal", "chevreuil"], "description": "Sp\u00e9cialiste ours en Ontario.", "price_range": "$$$", "success_rate": 72.0, "is_verified": False, "services": {"accommodation": True, "guided_hunts": True, "meals_included": True}, "scoring": {"habitat_index": 82, "pressure_index": 45, "success_index": 72, "accessibility_index": 70}},
        {"name": "Nipissing Moose Camp", "establishment_type": "outfitter", "province": "ON", "region": "Nipissing", "hunting_zones": ["WMU 37"], "species": ["orignal", "ours"], "description": "Camp traditionnel.", "price_range": "$$", "success_rate": 58.0, "is_verified": False, "services": {"accommodation": True, "meals_included": True}, "scoring": {"habitat_index": 75, "pressure_index": 55, "success_index": 58, "accessibility_index": 75}}
    ]
    count = await _inv_db.territories.count_documents({})
    if count > 0:
        logger.info(f"Database already has {count} territories, skipping seed")
        return count
    for territory in sample_territories:
        internal_id = generate_internal_id(territory["establishment_type"], territory["name"], territory["province"], territory.get("hunting_zones", [None])[0])
        territory["internal_id"] = internal_id
        territory["created_at"] = datetime.now(timezone.utc)
        territory["updated_at"] = datetime.now(timezone.utc)
        territory["status"] = "active"
        if "scoring" in territory:
            territory["scoring"]["global_score"] = calculate_global_score(territory["scoring"])
            territory["scoring"]["last_calculated"] = datetime.now(timezone.utc).isoformat()
        if "services" not in territory:
            territory["services"] = {"accommodation": False, "guided_hunts": False, "equipment_rental": False, "meat_processing": False, "transportation": False, "meals_included": False, "fishing": False, "atv_access": False, "boat_access": False, "dog_friendly": False}
    await _inv_db.territories.insert_many(sample_territories)
    logger.info(f"Seeded {len(sample_territories)} sample territories")
    return len(sample_territories)


@territories_router.post("/seed")
async def trigger_seed():
    try:
        count = await seed_sample_territories()
        return {"success": True, "message": f"Base de donn\u00e9es initialis\u00e9e avec {count} territoires"}
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# BIDIRECTIONAL SYNC WITH PARTNERSHIP MODULE
# ============================================

async def sync_territory_to_partnership(territory_id: str, territory_data: dict = None):
    try:
        if not territory_data:
            territory = await _inv_db.territories.find_one({"_id": ObjectId(territory_id)})
            if not territory:
                return {"success": False, "message": "Territory not found"}
            territory_data = territory
        territory_id_str = str(territory_data.get('_id', territory_id))
        existing = await _inv_db.partner_requests.find_one({"territory_id": territory_id_str})
        establishment_type = territory_data.get('establishment_type', 'pourvoirie')
        partner_type_map = {"pourvoirie": "pourvoiries", "sepaq": "pourvoiries", "zec": "zec", "club": "clubs", "outfitter": "pourvoiries", "reserve": "pourvoiries", "anticosti": "pourvoiries", "private": "proprietaires"}
        partner_type = partner_type_map.get(establishment_type, 'pourvoiries')
        sync_data = {
            "territory_id": territory_id_str,
            "company_name": territory_data.get('name'),
            "partner_type": partner_type,
            "contact_name": territory_data.get('contact', {}).get('name', '\u00c0 contacter'),
            "email": territory_data.get('contact', {}).get('email', ''),
            "phone": territory_data.get('contact', {}).get('phone', ''),
            "website": territory_data.get('website'),
            "description": territory_data.get('description', f"Territoire de chasse - {territory_data.get('name')}"),
            "region": territory_data.get('region'),
            "province": territory_data.get('province'),
            "establishment_type": establishment_type,
            "species": territory_data.get('species', []),
            "hunting_zones": territory_data.get('hunting_zones', []),
            "services": territory_data.get('services', {}),
            "scoring": territory_data.get('scoring', {}),
            "coordinates": territory_data.get('coordinates'),
            "is_verified": territory_data.get('is_verified', False),
            "is_partner": territory_data.get('is_partner', False),
            "last_sync": datetime.now(timezone.utc),
            "sync_source": "territory"
        }
        if existing:
            await _inv_db.partner_requests.update_one({"territory_id": territory_id_str}, {"$set": {**sync_data, "updated_at": datetime.now(timezone.utc)}})
            logger.info(f"Synced territory {territory_id_str} to partnership (update)")
        else:
            sync_data.update({
                "status": "pending", "source": "territory_sync",
                "created_at": datetime.now(timezone.utc), "updated_at": None,
                "admin_notes": f"Auto-sync depuis l'inventaire. Score BIONIC\u2122: {territory_data.get('scoring', {}).get('global_score', 'N/D')}",
                "legal_consent": True, "preferred_language": "fr"
            })
            await _inv_db.partner_requests.insert_one(sync_data)
            logger.info(f"Synced territory {territory_id_str} to partnership (create)")
        return {"success": True, "synced": territory_id_str}
    except Exception as e:
        logger.error(f"Error syncing territory to partnership: {e}")
        return {"success": False, "error": str(e)}


async def sync_partnership_to_territory(partner_request_id: str):
    try:
        partner = await _inv_db.partner_requests.find_one({"_id": ObjectId(partner_request_id)})
        if not partner:
            return {"success": False, "message": "Partner request not found"}
        territory_id = partner.get('territory_id')
        if not territory_id:
            return {"success": False, "message": "No territory linked"}
        update_data = {
            "is_partner": partner.get('status') in ['approved', 'converted'],
            "partner_status": partner.get('status'),
            "partner_since": partner.get('approved_at') if partner.get('status') in ['approved', 'converted'] else None,
            "last_sync": datetime.now(timezone.utc),
            "sync_source": "partnership"
        }
        if partner.get('email') or partner.get('phone'):
            update_data["contact"] = {"name": partner.get('contact_name', ''), "email": partner.get('email', ''), "phone": partner.get('phone', '')}
        result = await _inv_db.territories.update_one({"_id": ObjectId(territory_id)}, {"$set": update_data})
        if result.modified_count > 0:
            logger.info(f"Synced partnership {partner_request_id} back to territory {territory_id}")
            return {"success": True, "synced": territory_id}
        return {"success": False, "message": "Territory not found or no changes"}
    except Exception as e:
        logger.error(f"Error syncing partnership to territory: {e}")
        return {"success": False, "error": str(e)}


# ============================================
# SYNC API ENDPOINTS
# ============================================

@territories_router.post("/sync/to-partnership/{territory_id}")
async def api_sync_territory_to_partnership(territory_id: str):
    return await sync_territory_to_partnership(territory_id)


@territories_router.post("/sync/from-partnership/{partner_id}")
async def api_sync_from_partnership(partner_id: str):
    return await sync_partnership_to_territory(partner_id)


@territories_router.post("/sync/all-to-partnership")
async def sync_all_territories_to_partnership(background_tasks: BackgroundTasks):
    try:
        territories = await _inv_db.territories.find({}).to_list(1000)
        synced = 0; errors = 0
        for territory in territories:
            result = await sync_territory_to_partnership(str(territory['_id']), territory)
            if result.get('success'): synced += 1
            else: errors += 1
        return {"success": True, "message": f"Synchronisation termin\u00e9e: {synced} territoires synchronis\u00e9s, {errors} erreurs", "synced": synced, "errors": errors, "total": len(territories)}
    except Exception as e:
        logger.error(f"Error in bulk sync: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@territories_router.post("/sync/all-from-partnership")
async def sync_all_from_partnership():
    try:
        partners = await _inv_db.partner_requests.find({"territory_id": {"$exists": True}}).to_list(1000)
        synced = 0; errors = 0
        for partner in partners:
            result = await sync_partnership_to_territory(str(partner['_id']))
            if result.get('success'): synced += 1
            else: errors += 1
        return {"success": True, "message": f"Synchronisation termin\u00e9e: {synced} partenaires synchronis\u00e9s, {errors} erreurs", "synced": synced, "errors": errors, "total": len(partners)}
    except Exception as e:
        logger.error(f"Error in bulk sync from partnership: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@territories_router.get("/sync/status")
async def get_sync_status():
    try:
        total_territories = await _inv_db.territories.count_documents({})
        synced_to_partnership = await _inv_db.partner_requests.count_documents({"territory_id": {"$exists": True}})
        territories_as_partners = await _inv_db.territories.count_documents({"is_partner": True})
        partner_territory_ids = []
        async for p in _inv_db.partner_requests.find({"territory_id": {"$exists": True}}, {"territory_id": 1}):
            partner_territory_ids.append(p['territory_id'])
        unsynced = await _inv_db.territories.count_documents({"_id": {"$nin": [ObjectId(tid) for tid in partner_territory_ids if ObjectId.is_valid(tid)]}})
        last_territory_sync = await _inv_db.territories.find_one({"last_sync": {"$exists": True}}, sort=[("last_sync", -1)])
        last_partner_sync = await _inv_db.partner_requests.find_one({"last_sync": {"$exists": True}}, sort=[("last_sync", -1)])
        return {
            "success": True, "status": {
                "total_territories": total_territories, "synced_to_partnership": synced_to_partnership,
                "territories_as_partners": territories_as_partners, "unsynced_territories": unsynced,
                "sync_percentage": round((synced_to_partnership / total_territories * 100), 1) if total_territories > 0 else 0,
                "last_territory_sync": last_territory_sync.get('last_sync') if last_territory_sync else None,
                "last_partner_sync": last_partner_sync.get('last_sync') if last_partner_sync else None
            }
        }
    except Exception as e:
        logger.error(f"Error getting sync status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# AUTO-SYNC HOOKS
# ============================================

async def on_territory_created(territory_id: str, territory_data: dict):
    await sync_territory_to_partnership(territory_id, territory_data)


async def on_territory_updated(territory_id: str, territory_data: dict):
    await sync_territory_to_partnership(territory_id, territory_data)


async def on_partner_status_changed(partner_request_id: str):
    await sync_partnership_to_territory(partner_request_id)


logger.info("Territory Inventory module initialized")
