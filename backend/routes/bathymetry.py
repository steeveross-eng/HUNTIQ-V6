"""
Bathymetry API - Données bathymétriques des lacs du Québec

Endpoints pour gérer les données de profondeur des plans d'eau.
Structure préparée pour l'intégration des données MFFP et utilisateur.

Collections MongoDB:
- bathymetry_lakes: Métadonnées des lacs avec données bathymétriques
- bathymetry_contours: Courbes de niveau (isobathes)
- bathymetry_points: Points de sondage

Auteur: BIONIC HUNT/Chasse V3 / BIONIC™
Date: Février 2026
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from bson import ObjectId
import os

# Router
router = APIRouter(prefix="/api/bathymetry", tags=["Bathymetry"])

# MongoDB connection
from motor.motor_asyncio import AsyncIOMotorClient
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "huntiq")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Collections
bathymetry_lakes = db["bathymetry_lakes"]
bathymetry_contours = db["bathymetry_contours"]
bathymetry_points = db["bathymetry_points"]


# ==================================================
# MODÈLES PYDANTIC
# ==================================================

class Coordinate(BaseModel):
    lat: float
    lng: float

class DepthPoint(BaseModel):
    """Point de sondage avec profondeur"""
    coordinates: List[float]  # [lat, lng]
    depth: float  # Profondeur en mètres
    type: str = "sounding"  # 'sounding', 'shallow', 'deep'
    name: Optional[str] = None
    source: str = "user"  # 'mffp', 'user', 'navionics'

class DepthContour(BaseModel):
    """Courbe isobathe (même profondeur)"""
    depth: float  # Profondeur en mètres
    coordinates: List[List[float]]  # Liste de [lat, lng]

class DepthZone(BaseModel):
    """Zone de profondeur (polygone)"""
    minDepth: float
    maxDepth: float
    depth: float  # Profondeur moyenne/représentative
    coordinates: List[List[float]]  # Polygone

class LakeBathymetry(BaseModel):
    """Données bathymétriques complètes d'un lac"""
    lake_id: str
    name: str
    region: Optional[str] = None
    municipality: Optional[str] = None
    area_km2: Optional[float] = None
    max_depth: Optional[float] = None
    mean_depth: Optional[float] = None
    contours: List[DepthContour] = []
    zones: List[DepthZone] = []
    points: List[DepthPoint] = []
    source: str = "user"
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class BathymetryUpload(BaseModel):
    """Modèle pour upload de données bathymétriques"""
    lake_name: str
    lake_id: Optional[str] = None
    center: List[float]  # [lat, lng]
    points: List[DepthPoint] = []
    notes: Optional[str] = None

class BathymetryResponse(BaseModel):
    """Réponse avec données bathymétriques"""
    success: bool
    lake_id: str
    name: str
    max_depth: Optional[float] = None
    mean_depth: Optional[float] = None
    contours: List[Dict] = []
    zones: List[Dict] = []
    points: List[Dict] = []
    source: str
    last_updated: Optional[str] = None


# ==================================================
# ENDPOINTS
# ==================================================

@router.get("/lakes", summary="Liste des lacs avec données bathymétriques")
async def list_bathymetry_lakes(
    region: Optional[str] = Query(None, description="Filtrer par région"),
    min_area: Optional[float] = Query(None, description="Surface minimale en km²"),
    limit: int = Query(50, le=200),
    skip: int = Query(0, ge=0)
):
    """
    Récupère la liste des lacs ayant des données bathymétriques.
    """
    query = {}
    
    if region:
        query["region"] = {"$regex": region, "$options": "i"}
    
    if min_area:
        query["area_km2"] = {"$gte": min_area}
    
    cursor = bathymetry_lakes.find(
        query,
        {"_id": 0, "contours": 0, "zones": 0, "points": 0}  # Exclure les données volumineuses
    ).skip(skip).limit(limit)
    
    lakes = await cursor.to_list(length=limit)
    total = await bathymetry_lakes.count_documents(query)
    
    return {
        "success": True,
        "total": total,
        "lakes": lakes
    }


@router.get("/{lake_id}", summary="Données bathymétriques d'un lac")
async def get_lake_bathymetry(
    lake_id: str,
    include_contours: bool = Query(True, description="Inclure les courbes de niveau"),
    include_zones: bool = Query(True, description="Inclure les zones de profondeur"),
    include_points: bool = Query(True, description="Inclure les points de sondage")
):
    """
    Récupère les données bathymétriques complètes d'un lac.
    """
    # Projection conditionnelle
    projection = {"_id": 0}
    if not include_contours:
        projection["contours"] = 0
    if not include_zones:
        projection["zones"] = 0
    if not include_points:
        projection["points"] = 0
    
    lake = await bathymetry_lakes.find_one(
        {"lake_id": lake_id},
        projection
    )
    
    if not lake:
        raise HTTPException(
            status_code=404,
            detail=f"Aucune donnée bathymétrique pour le lac {lake_id}"
        )
    
    # Convertir datetime si présent
    if "last_updated" in lake and lake["last_updated"]:
        lake["last_updated"] = lake["last_updated"].isoformat()
    
    return {
        "success": True,
        **lake
    }


@router.post("/upload", summary="Uploader des données bathymétriques")
async def upload_bathymetry_data(data: BathymetryUpload):
    """
    Upload de nouvelles données bathymétriques pour un lac.
    Peut être utilisé pour ajouter des sondages personnels.
    """
    # Générer un ID si non fourni
    lake_id = data.lake_id or f"user_lake_{ObjectId()}"
    
    # Calculer les statistiques
    depths = [p.depth for p in data.points]
    max_depth = max(depths) if depths else None
    mean_depth = sum(depths) / len(depths) if depths else None
    
    # Créer ou mettre à jour le document
    lake_doc = {
        "lake_id": lake_id,
        "name": data.lake_name,
        "center": data.center,
        "max_depth": max_depth,
        "mean_depth": mean_depth,
        "points": [p.dict() for p in data.points],
        "source": "user",
        "notes": data.notes,
        "last_updated": datetime.utcnow()
    }
    
    # Upsert
    await bathymetry_lakes.update_one(
        {"lake_id": lake_id},
        {"$set": lake_doc},
        upsert=True
    )
    
    return {
        "success": True,
        "lake_id": lake_id,
        "message": "Données bathymétriques enregistrées",
        "points_count": len(data.points),
        "max_depth": max_depth,
        "mean_depth": mean_depth
    }


@router.post("/{lake_id}/points", summary="Ajouter des points de sondage")
async def add_sounding_points(lake_id: str, points: List[DepthPoint]):
    """
    Ajouter des points de sondage à un lac existant.
    """
    lake = await bathymetry_lakes.find_one({"lake_id": lake_id})
    
    if not lake:
        raise HTTPException(
            status_code=404,
            detail=f"Lac {lake_id} non trouvé"
        )
    
    # Ajouter les nouveaux points
    new_points = [p.dict() for p in points]
    
    await bathymetry_lakes.update_one(
        {"lake_id": lake_id},
        {
            "$push": {"points": {"$each": new_points}},
            "$set": {"last_updated": datetime.utcnow()}
        }
    )
    
    return {
        "success": True,
        "lake_id": lake_id,
        "points_added": len(points),
        "message": f"{len(points)} points de sondage ajoutés"
    }


@router.get("/search/nearby", summary="Rechercher des lacs à proximité")
async def search_nearby_lakes(
    lat: float = Query(..., description="Latitude du centre"),
    lng: float = Query(..., description="Longitude du centre"),
    radius_km: float = Query(10, description="Rayon de recherche en km")
):
    """
    Rechercher des lacs avec données bathymétriques dans un rayon donné.
    """
    # Conversion du rayon en degrés (approximation)
    radius_deg = radius_km / 111  # ~111km par degré
    
    # Recherche géospatiale simple (bounding box)
    query = {
        "center.0": {"$gte": lat - radius_deg, "$lte": lat + radius_deg},
        "center.1": {"$gte": lng - radius_deg, "$lte": lng + radius_deg}
    }
    
    cursor = bathymetry_lakes.find(
        query,
        {"_id": 0, "lake_id": 1, "name": 1, "center": 1, "max_depth": 1, "area_km2": 1}
    ).limit(20)
    
    lakes = await cursor.to_list(length=20)
    
    return {
        "success": True,
        "center": [lat, lng],
        "radius_km": radius_km,
        "lakes_found": len(lakes),
        "lakes": lakes
    }


@router.delete("/{lake_id}", summary="Supprimer les données d'un lac")
async def delete_lake_bathymetry(lake_id: str):
    """
    Supprimer les données bathymétriques d'un lac (utilisateur uniquement).
    """
    # Vérifier que c'est une donnée utilisateur
    lake = await bathymetry_lakes.find_one({"lake_id": lake_id})
    
    if not lake:
        raise HTTPException(status_code=404, detail="Lac non trouvé")
    
    if lake.get("source") != "user":
        raise HTTPException(
            status_code=403,
            detail="Seules les données utilisateur peuvent être supprimées"
        )
    
    await bathymetry_lakes.delete_one({"lake_id": lake_id})
    
    return {
        "success": True,
        "message": f"Données du lac {lake_id} supprimées"
    }


@router.get("/stats/overview", summary="Statistiques globales bathymétriques")
async def get_bathymetry_stats():
    """
    Statistiques globales sur les données bathymétriques disponibles.
    """
    total_lakes = await bathymetry_lakes.count_documents({})
    user_lakes = await bathymetry_lakes.count_documents({"source": "user"})
    mffp_lakes = await bathymetry_lakes.count_documents({"source": "mffp"})
    
    # Agrégation pour les stats
    pipeline = [
        {
            "$group": {
                "_id": None,
                "total_points": {"$sum": {"$size": {"$ifNull": ["$points", []]}}},
                "avg_max_depth": {"$avg": "$max_depth"},
                "max_depth_overall": {"$max": "$max_depth"}
            }
        }
    ]
    
    stats_result = await bathymetry_lakes.aggregate(pipeline).to_list(1)
    stats = stats_result[0] if stats_result else {}
    
    return {
        "success": True,
        "total_lakes": total_lakes,
        "by_source": {
            "user": user_lakes,
            "mffp": mffp_lakes,
            "other": total_lakes - user_lakes - mffp_lakes
        },
        "total_sounding_points": stats.get("total_points", 0),
        "average_max_depth": round(stats.get("avg_max_depth", 0) or 0, 2),
        "deepest_recorded": stats.get("max_depth_overall", 0)
    }
