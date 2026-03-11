"""
Advanced Zones API - Zones BIONIC avancées (14 types)

Endpoints pour gérer les zones d'analyse BIONIC sur le territoire.
Types de zones:
- Comportementales: rut, repos, alimentation, corridor
- Environnementales: habitat, soleil, pente, hydro, foret, thermique
- Stratégiques: affut, hotspot, pression, acces

Auteur: BIONIC HUNT/Chasse V3 / BIONIC™
Date: Février 2026
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
from bson import ObjectId
import os

# Router
router = APIRouter(prefix="/api/territory/zones", tags=["Advanced Zones"])

# MongoDB connection
from motor.motor_asyncio import AsyncIOMotorClient
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "huntiq")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Collections
advanced_zones = db["advanced_zones"]
geo_entities = db["geo_entities"]


# ==================================================
# TYPES DE ZONES
# ==================================================

ZONE_TYPES = {
    # Comportementales
    "rut": {"category": "behavioral", "color": "#FF4D6D", "priority": 1},
    "repos": {"category": "behavioral", "color": "#8B5CF6", "priority": 2},
    "alimentation": {"category": "behavioral", "color": "#22C55E", "priority": 3},
    "corridor": {"category": "behavioral", "color": "#06B6D4", "priority": 4},
    # Environnementales
    "habitat": {"category": "environmental", "color": "#10B981", "priority": 5},
    "soleil": {"category": "environmental", "color": "#FCD34D", "priority": 10},
    "pente": {"category": "environmental", "color": "#A78BFA", "priority": 11},
    "hydro": {"category": "environmental", "color": "#3B82F6", "priority": 9},
    "foret": {"category": "environmental", "color": "#15803D", "priority": 12},
    "thermique": {"category": "environmental", "color": "#EF4444", "priority": 8},
    # Stratégiques
    "affut": {"category": "strategic", "color": "#F5A623", "priority": 6},
    "hotspot": {"category": "strategic", "color": "#FF6B6B", "priority": 7},
    "pression": {"category": "strategic", "color": "#F97316", "priority": 13},
    "acces": {"category": "strategic", "color": "#8B5CF6", "priority": 14},
}

ZONE_CATEGORIES = ["behavioral", "environmental", "strategic"]


# ==================================================
# MODÈLES PYDANTIC
# ==================================================

class ZoneCoordinate(BaseModel):
    """Coordonnée [lat, lng]"""
    lat: float
    lng: float

class ZoneBase(BaseModel):
    """Modèle de base pour une zone"""
    type: str = Field(..., description="Type de zone (rut, repos, etc.)")
    geometry: Literal["polygon", "circle", "corridor"] = "polygon"
    coordinates: Optional[List[List[float]]] = None  # Pour polygon et corridor
    center: Optional[List[float]] = None  # Pour circle [lat, lng]
    radius: Optional[float] = None  # Pour circle (mètres)
    width: Optional[float] = None  # Pour corridor (mètres)
    score: Optional[int] = Field(None, ge=0, le=100)
    confirmed: bool = False
    notes: Optional[str] = None

class ZoneCreate(ZoneBase):
    """Modèle pour créer une zone"""
    territory_id: Optional[str] = None
    user_id: Optional[str] = None

class ZoneUpdate(BaseModel):
    """Modèle pour mettre à jour une zone"""
    coordinates: Optional[List[List[float]]] = None
    center: Optional[List[float]] = None
    radius: Optional[float] = None
    score: Optional[int] = Field(None, ge=0, le=100)
    confirmed: Optional[bool] = None
    notes: Optional[str] = None

class ZoneResponse(BaseModel):
    """Réponse avec zone"""
    id: str
    type: str
    geometry: str
    coordinates: Optional[List[List[float]]] = None
    center: Optional[List[float]] = None
    radius: Optional[float] = None
    width: Optional[float] = None
    score: Optional[int] = None
    confirmed: bool = False
    category: str
    color: str
    created_at: Optional[str] = None


# ==================================================
# ENDPOINTS
# ==================================================

@router.get("", summary="Liste des zones avancées")
async def list_zones(
    territory_id: Optional[str] = Query(None, description="Filtrer par territoire"),
    zone_type: Optional[str] = Query(None, description="Filtrer par type de zone"),
    category: Optional[str] = Query(None, description="Filtrer par catégorie"),
    min_score: Optional[int] = Query(None, ge=0, le=100, description="Score minimum"),
    sw_lat: Optional[float] = Query(None, description="Latitude sud-ouest"),
    sw_lng: Optional[float] = Query(None, description="Longitude sud-ouest"),
    ne_lat: Optional[float] = Query(None, description="Latitude nord-est"),
    ne_lng: Optional[float] = Query(None, description="Longitude nord-est"),
    limit: int = Query(100, le=500),
    skip: int = Query(0, ge=0)
):
    """
    Récupère la liste des zones avancées avec filtres optionnels.
    """
    query = {}
    
    if territory_id:
        query["territory_id"] = territory_id
    
    if zone_type and zone_type in ZONE_TYPES:
        query["type"] = zone_type
    
    if category and category in ZONE_CATEGORIES:
        zone_types = [k for k, v in ZONE_TYPES.items() if v["category"] == category]
        query["type"] = {"$in": zone_types}
    
    if min_score is not None:
        query["score"] = {"$gte": min_score}
    
    # Filtre géospatial (bounding box)
    if all([sw_lat, sw_lng, ne_lat, ne_lng]):
        # Pour les zones avec center (circles)
        geo_query_center = {
            "$and": [
                {"center.0": {"$gte": sw_lat, "$lte": ne_lat}},
                {"center.1": {"$gte": sw_lng, "$lte": ne_lng}}
            ]
        }
        # Note: Pour les polygones, une requête géospatiale plus complexe serait nécessaire
        # Pour l'instant, on filtre simplement par center si présent
        query["$or"] = [
            geo_query_center,
            {"center": {"$exists": False}}  # Inclure les zones sans center
        ]
    
    cursor = advanced_zones.find(query, {"_id": 0}).skip(skip).limit(limit)
    zones_list = await cursor.to_list(length=limit)
    
    # Enrichir avec les métadonnées de type
    for zone in zones_list:
        zone_type_config = ZONE_TYPES.get(zone.get("type"), {})
        zone["category"] = zone_type_config.get("category", "unknown")
        zone["color"] = zone_type_config.get("color", "#888888")
    
    total = await advanced_zones.count_documents(query)
    
    return {
        "success": True,
        "total": total,
        "zones": zones_list
    }


@router.get("/types", summary="Liste des types de zones disponibles")
async def list_zone_types():
    """
    Retourne la liste des 14 types de zones avec leurs métadonnées.
    """
    return {
        "success": True,
        "types": ZONE_TYPES,
        "categories": {
            "behavioral": {
                "name": "Comportementales",
                "nameEn": "Behavioral",
                "types": ["rut", "repos", "alimentation", "corridor"]
            },
            "environmental": {
                "name": "Environnementales",
                "nameEn": "Environmental",
                "types": ["habitat", "soleil", "pente", "hydro", "foret", "thermique"]
            },
            "strategic": {
                "name": "Stratégiques",
                "nameEn": "Strategic",
                "types": ["affut", "hotspot", "pression", "acces"]
            }
        }
    }


@router.post("", summary="Créer une zone avancée")
async def create_zone(zone: ZoneCreate):
    """
    Créer une nouvelle zone avancée.
    """
    if zone.type not in ZONE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Type de zone invalide. Types valides: {list(ZONE_TYPES.keys())}"
        )
    
    # Validation de la géométrie
    if zone.geometry == "circle" and not zone.center:
        raise HTTPException(status_code=400, detail="center requis pour geometry=circle")
    
    if zone.geometry in ["polygon", "corridor"] and not zone.coordinates:
        raise HTTPException(status_code=400, detail="coordinates requis pour polygon/corridor")
    
    zone_doc = {
        "id": str(ObjectId()),
        "type": zone.type,
        "geometry": zone.geometry,
        "coordinates": zone.coordinates,
        "center": zone.center,
        "radius": zone.radius,
        "width": zone.width,
        "score": zone.score,
        "confirmed": zone.confirmed,
        "notes": zone.notes,
        "territory_id": zone.territory_id,
        "user_id": zone.user_id,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    await advanced_zones.insert_one(zone_doc)
    
    # Ajouter les métadonnées
    zone_type_config = ZONE_TYPES[zone.type]
    zone_doc["category"] = zone_type_config["category"]
    zone_doc["color"] = zone_type_config["color"]
    
    return {
        "success": True,
        "zone": {k: v for k, v in zone_doc.items() if k != "_id"}
    }


@router.get("/{zone_id}", summary="Détails d'une zone")
async def get_zone(zone_id: str):
    """
    Récupère les détails d'une zone spécifique.
    """
    zone = await advanced_zones.find_one({"id": zone_id}, {"_id": 0})
    
    if not zone:
        raise HTTPException(status_code=404, detail="Zone non trouvée")
    
    # Ajouter les métadonnées
    zone_type_config = ZONE_TYPES.get(zone.get("type"), {})
    zone["category"] = zone_type_config.get("category", "unknown")
    zone["color"] = zone_type_config.get("color", "#888888")
    
    return {
        "success": True,
        "zone": zone
    }


@router.put("/{zone_id}", summary="Mettre à jour une zone")
async def update_zone(zone_id: str, updates: ZoneUpdate):
    """
    Mettre à jour une zone existante.
    """
    zone = await advanced_zones.find_one({"id": zone_id})
    
    if not zone:
        raise HTTPException(status_code=404, detail="Zone non trouvée")
    
    update_doc = {k: v for k, v in updates.dict().items() if v is not None}
    update_doc["updated_at"] = datetime.utcnow().isoformat()
    
    await advanced_zones.update_one(
        {"id": zone_id},
        {"$set": update_doc}
    )
    
    return {
        "success": True,
        "message": "Zone mise à jour",
        "zone_id": zone_id
    }


@router.delete("/{zone_id}", summary="Supprimer une zone")
async def delete_zone(zone_id: str):
    """
    Supprimer une zone.
    """
    result = await advanced_zones.delete_one({"id": zone_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Zone non trouvée")
    
    return {
        "success": True,
        "message": "Zone supprimée",
        "zone_id": zone_id
    }


@router.get("/stats/summary", summary="Statistiques des zones")
async def get_zones_stats(territory_id: Optional[str] = None):
    """
    Statistiques globales sur les zones.
    """
    query = {}
    if territory_id:
        query["territory_id"] = territory_id
    
    # Agrégation par type
    pipeline = [
        {"$match": query} if query else {"$match": {}},
        {
            "$group": {
                "_id": "$type",
                "count": {"$sum": 1},
                "avg_score": {"$avg": "$score"},
                "confirmed_count": {
                    "$sum": {"$cond": ["$confirmed", 1, 0]}
                }
            }
        }
    ]
    
    cursor = advanced_zones.aggregate(pipeline)
    type_stats = await cursor.to_list(length=20)
    
    # Organiser par catégorie
    stats_by_category = {
        "behavioral": [],
        "environmental": [],
        "strategic": []
    }
    
    for stat in type_stats:
        zone_type = stat["_id"]
        if zone_type and zone_type in ZONE_TYPES:
            category = ZONE_TYPES[zone_type]["category"]
            stats_by_category[category].append({
                "type": zone_type,
                "count": stat["count"],
                "avg_score": round(stat["avg_score"] or 0, 1),
                "confirmed": stat["confirmed_count"]
            })
    
    total = await advanced_zones.count_documents(query)
    
    return {
        "success": True,
        "total_zones": total,
        "by_category": stats_by_category
    }
