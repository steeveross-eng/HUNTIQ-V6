"""Territory Engine Module v1

Territory and land management for hunting.
Extracted from territories.py.

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

router = APIRouter(prefix="/api/v1/territory", tags=["Territory Engine"])


# ============================================
# MODELS
# ============================================

class TerritoryType(str, Enum):
    ZEC = "zec"
    POURVOIRIE = "pourvoirie"
    PUBLIC = "public"
    RESERVE = "reserve"
    PRIVATE = "private"


class Territory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: TerritoryType
    region: str
    area_km2: float = 0
    coordinates: List[Dict[str, float]] = []  # Polygon points
    species: List[str] = []
    features: List[str] = []  # cabin, boat, guide
    contact_info: Dict[str, str] = {}
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LandRental(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    territory_id: str
    owner_id: str
    title: str
    description: str
    price_per_day: float
    min_days: int = 1
    max_guests: int = 4
    amenities: List[str] = []
    images: List[str] = []
    is_available: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AccessPermit(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    territory_id: str
    permit_type: Literal["daily", "seasonal", "annual"]
    valid_from: datetime
    valid_until: datetime
    species_allowed: List[str] = []
    is_active: bool = True


# ============================================
# SERVICE
# ============================================

class TerritoryService:
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
    
    async def list_territories(self, territory_type: str = None, region: str = None,
                                skip: int = 0, limit: int = 50) -> List[Dict]:
        query = {}
        if territory_type:
            query["type"] = territory_type
        if region:
            query["region"] = region
        
        cursor = self.db.territories.find(query, {"_id": 0}).skip(skip).limit(limit)
        return list(cursor)
    
    async def get_territory(self, territory_id: str) -> Optional[Dict]:
        return self.db.territories.find_one({"id": territory_id}, {"_id": 0})
    
    async def create_territory(self, territory: Territory) -> Territory:
        t_dict = territory.model_dump()
        t_dict.pop("_id", None)
        self.db.territories.insert_one(t_dict)
        return territory
    
    async def search_by_species(self, species: str) -> List[Dict]:
        cursor = self.db.territories.find(
            {"species": {"$in": [species]}},
            {"_id": 0}
        )
        return list(cursor)
    
    async def get_rentals(self, territory_id: str = None) -> List[Dict]:
        query = {}
        if territory_id:
            query["territory_id"] = territory_id
        query["is_available"] = True
        
        cursor = self.db.land_rentals.find(query, {"_id": 0})
        return list(cursor)


_service = TerritoryService()


# ============================================
# ROUTES
# ============================================

@router.get("/")
async def territory_engine_info():
    return {
        "module": "territory_engine",
        "version": "1.0.0",
        "description": "Territory and land management",
        "features": ["Territory listing", "Land rentals", "Access permits", "Species search"],
        "types": [t.value for t in TerritoryType]
    }


@router.get("/list")
async def list_territories(
    type: Optional[str] = None,
    region: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200)
):
    territories = await _service.list_territories(type, region, skip, limit)
    return {"success": True, "total": len(territories), "territories": territories}


@router.get("/{territory_id}")
async def get_territory(territory_id: str):
    territory = await _service.get_territory(territory_id)
    if not territory:
        raise HTTPException(status_code=404, detail="Territory not found")
    return {"success": True, "territory": territory}


@router.get("/search/species/{species}")
async def search_by_species(species: str):
    territories = await _service.search_by_species(species)
    return {"success": True, "species": species, "territories": territories}


@router.get("/rentals")
async def list_rentals(territory_id: Optional[str] = None):
    rentals = await _service.get_rentals(territory_id)
    return {"success": True, "rentals": rentals}


@router.get("/types")
async def list_territory_types():
    return {
        "success": True,
        "types": [
            {"id": "zec", "name": "ZEC", "description": "Zone d'exploitation contrôlée"},
            {"id": "pourvoirie", "name": "Pourvoirie", "description": "Territoire privé avec services"},
            {"id": "public", "name": "Terres publiques", "description": "Domaine de l'État"},
            {"id": "reserve", "name": "Réserve faunique", "description": "Gérée par SÉPAQ"},
            {"id": "private", "name": "Terrain privé", "description": "Propriété individuelle"}
        ]
    }
