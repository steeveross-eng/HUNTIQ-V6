"""
Admin Geo Engine - Global Geospatial Administration
Phase P6.5 - Admin Dashboard Backend

⚠️ CONFIDENTIALITÉ ABSOLUE DES HOTSPOTS
===========================================
Les hotspots sont des données STRICTEMENT PRIVÉES:
- Jamais exposés aux utilisateurs non-propriétaires
- Jamais synchronisés via WebSocket
- Jamais inclus dans les notifications push
- Accessibles UNIQUEMENT via cet espace admin (réservé aux administrateurs système)

Cette API est réservée aux administrateurs pour:
- Analyse globale du territoire
- Génération de hotspots système
- Statistiques agrégées (anonymisées)
- Préparation de la monétisation (hotspots système uniquement)

Les hotspots utilisateur restent 100% confidentiels et ne sont jamais exposés.
"""

from fastapi import APIRouter, Query, HTTPException, Depends
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import logging

from models.geo_entity import GeoEntityResponse
from database import Database

# Import role-based authentication
from modules.roles_engine.v1.dependencies import require_admin
from modules.roles_engine.v1.models import UserWithRole

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/geo", tags=["Admin Geo (ADMIN ONLY - Confidential)"])

GEO_COLLECTION = "geo_entities"


async def get_db():
    """Get database instance"""
    return Database.get_database()


# ===========================================
# GLOBAL VIEW ENDPOINTS (ADMIN ONLY)
# ===========================================

@router.get("/all", response_model=List[GeoEntityResponse])
async def get_all_entities(
    admin: UserWithRole = Depends(require_admin),
    entity_type: Optional[str] = None,
    habitat: Optional[str] = None,
    min_density: Optional[float] = Query(None, ge=0, le=1),
    max_density: Optional[float] = Query(None, ge=0, le=1),
    is_auto_generated: Optional[bool] = None,
    is_premium: Optional[bool] = None,
    is_claimed: Optional[bool] = None,
    user_id: Optional[str] = None,
    group_id: Optional[str] = None,
    active: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """
    Get ALL geo entities across all users (admin only).
    Supports advanced filtering for analysis.
    """
    db = await get_db()
    
    # Build query
    query: Dict[str, Any] = {}
    
    if entity_type:
        query["entity_type"] = entity_type
    
    if habitat:
        query["metadata.habitat"] = habitat
    
    if min_density is not None:
        query.setdefault("metadata.density", {})["$gte"] = min_density
    
    if max_density is not None:
        query.setdefault("metadata.density", {})["$lte"] = max_density
    
    if is_auto_generated is not None:
        query["metadata.is_auto_generated"] = is_auto_generated
    
    if is_premium is not None:
        query["metadata.is_premium"] = is_premium
    
    if is_claimed is not None:
        query["metadata.is_claimed"] = is_claimed
    
    if user_id:
        query["user_id"] = user_id
    
    if group_id:
        query["group_id"] = group_id
    
    if active is not None:
        query["active"] = active
    
    cursor = db[GEO_COLLECTION].find(query).sort("created_at", -1).skip(skip).limit(limit)
    entities = await cursor.to_list(limit)
    
    return [GeoEntityResponse.from_document(doc) for doc in entities]


@router.get("/hotspots")
async def get_admin_hotspots(
    admin: UserWithRole = Depends(require_admin),
    category: Optional[str] = Query(None, description="standard|premium|land_rental|environmental|chalet|user_personal|inactive"),
    user_id: Optional[str] = Query(None, description="Filter by specific user"),
    min_confidence: Optional[float] = Query(None, ge=0, le=1),
    habitat: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500)
):
    """
    Get ALL hotspots for admin management (ADMIN ONLY).
    
    🔒 ADMIN SEULEMENT: Cette section affiche TOUS les hotspots de TOUS les membres
    pour permettre la gestion, modération et supervision globale.
    Ces données ne sont jamais partagées ni accessibles aux utilisateurs réguliers.
    
    Catégories:
    - standard: Hotspots de base
    - premium: Hotspots haute qualité (confidence > 0.7)
    - land_rental: Hotspots "Terre à louer"
    - chalet: Chalets disponibles
    - environmental: Hotspots auto-générés par analyse environnementale
    - user_personal: Hotspots personnels des utilisateurs
    - inactive: Hotspots expirés ou désactivés
    """
    db = await get_db()
    
    # 🔓 ADMIN: Afficher TOUS les hotspots (pas de filtre d'exclusion)
    base_query: Dict[str, Any] = {
        "entity_type": "hotspot"
    }
    
    # Filtrer par catégorie
    if category == "standard":
        base_query["metadata.is_premium"] = {"$ne": True}
        base_query["metadata.is_auto_generated"] = {"$ne": True}
        base_query["metadata.hotspot_category"] = {"$nin": ["land_rental", "chalet"]}
    elif category == "premium":
        base_query["metadata.is_premium"] = True
    elif category == "land_rental":
        base_query["metadata.hotspot_category"] = "land_rental"
    elif category == "chalet":
        base_query["metadata.hotspot_category"] = "chalet"
    elif category == "environmental":
        base_query["metadata.is_auto_generated"] = True
    elif category == "user_personal":
        base_query["user_id"] = {"$ne": "system"}
        base_query["metadata.is_auto_generated"] = {"$ne": True}
    elif category == "inactive":
        base_query["active"] = False
    
    # Filtrer par utilisateur spécifique
    if user_id:
        base_query["user_id"] = user_id
    
    if min_confidence is not None:
        base_query["metadata.confidence"] = {"$gte": min_confidence}
    
    if habitat:
        base_query["metadata.habitat"] = habitat
    
    pipeline = [
        {"$match": base_query},
        {"$sort": {"metadata.confidence": -1, "created_at": -1}},
        {"$skip": skip},
        {"$limit": limit},
        {"$project": {
            "_id": 1,
            "name": 1,
            "location": 1,
            "user_id": 1,
            "metadata": 1,
            "created_at": 1,
            "active": 1
        }}
    ]
    
    hotspots = await db[GEO_COLLECTION].aggregate(pipeline).to_list(limit)
    
    # Déterminer la catégorie de chaque hotspot
    def get_hotspot_category(h):
        meta = h.get("metadata", {})
        user_id = h.get("user_id", "")
        
        if not h.get("active", True):
            return "inactive"
        if meta.get("hotspot_category") == "land_rental":
            return "land_rental"
        if meta.get("hotspot_category") == "chalet":
            return "chalet"
        if meta.get("is_auto_generated"):
            return "environmental"
        if meta.get("is_premium"):
            return "premium"
        # Hotspot personnel d'un utilisateur (pas système, pas auto-généré)
        if user_id and user_id != "system" and not meta.get("is_auto_generated"):
            return "user_personal"
        return "standard"
    
    # Compter par catégorie
    category_counts = {
        "standard": 0,
        "premium": 0,
        "land_rental": 0,
        "chalet": 0,
        "environmental": 0,
        "user_personal": 0,
        "inactive": 0
    }
    
    formatted_hotspots = []
    for h in hotspots:
        cat = get_hotspot_category(h)
        category_counts[cat] += 1
        
        loc = h.get("location", {})
        coords = loc.get("coordinates", [0, 0])
        meta = h.get("metadata", {})
        
        formatted_hotspots.append({
            "id": str(h["_id"]),
            "name": h.get("name", "Hotspot sans nom"),
            "user_id": h.get("user_id", ""),
            "category": cat,
            "category_label": {
                "standard": "Hotspot standard",
                "premium": "Hotspot premium",
                "land_rental": "Terre à louer",
                "chalet": "Chalet",
                "environmental": "Environnemental",
                "user_personal": "Personnel (membre)",
                "inactive": "Inactif"
            }.get(cat, cat),
            "latitude": coords[1] if len(coords) > 1 else None,
            "longitude": coords[0] if len(coords) > 0 else None,
            "status": _get_hotspot_status(h),
            "confidence": meta.get("confidence"),
            "habitat": meta.get("habitat"),
            "density": meta.get("density"),
            "is_premium": meta.get("is_premium", False),
            "is_claimed": meta.get("is_claimed", False),
            "active": h.get("active", True),
            "created_at": h.get("created_at"),
            "map_link": f"/map?lat={coords[1]}&lng={coords[0]}&zoom=17" if len(coords) > 1 else None
        })
    
    return {
        "hotspots": formatted_hotspots,
        "total": len(formatted_hotspots),
        "by_category": category_counts,
        "note": "🔒 ADMIN: Tous les hotspots de tous les membres sont visibles ici pour gestion et modération. Ces données ne sont jamais partagées aux utilisateurs."
    }


def _get_hotspot_status(hotspot: dict) -> str:
    """Déterminer le statut d'affichage d'un hotspot"""
    if not hotspot.get("active", True):
        return "Inactif"
    
    meta = hotspot.get("metadata", {})
    
    if meta.get("hotspot_category") == "land_rental":
        if meta.get("is_claimed"):
            return "Terre louée"
        return "Terre disponible"
    
    if meta.get("hotspot_category") == "chalet":
        if meta.get("is_claimed"):
            return "Chalet réservé"
        return "Chalet disponible"
    
    if meta.get("is_premium"):
        if meta.get("is_claimed"):
            return "Premium (réclamé)"
        return "Premium (disponible)"
    
    if meta.get("is_auto_generated"):
        return "Auto-généré"
    
    return "Standard"


@router.get("/corridors")
async def get_all_corridors(
    admin: UserWithRole = Depends(require_admin),
    min_traffic: Optional[float] = Query(None, ge=0, le=100),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500)
):
    """
    Get all detected wildlife corridors.
    """
    db = await get_db()
    
    query: Dict[str, Any] = {"entity_type": "corridor"}
    
    if min_traffic is not None:
        query["metadata.traffic_score"] = {"$gte": min_traffic}
    
    cursor = db[GEO_COLLECTION].find(query).sort("metadata.traffic_score", -1).skip(skip).limit(limit)
    corridors = await cursor.to_list(limit)
    
    return {
        "corridors": [GeoEntityResponse.from_document(c) for c in corridors],
        "total": len(corridors)
    }


# ===========================================
# ANALYTICS ENDPOINTS
# ===========================================

@router.get("/analytics/overview")
async def get_analytics_overview(
    admin: UserWithRole = Depends(require_admin)
):
    """
    Get comprehensive analytics overview for all geo data.
    """
    db = await get_db()
    
    pipeline = [
        {"$facet": {
            "total": [{"$count": "count"}],
            "by_type": [
                {"$group": {"_id": "$entity_type", "count": {"$sum": 1}}}
            ],
            "by_habitat": [
                {"$match": {"metadata.habitat": {"$exists": True, "$ne": None}}},
                {"$group": {"_id": "$metadata.habitat", "count": {"$sum": 1}}}
            ],
            "by_user": [
                {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ],
            "by_group": [
                {"$match": {"group_id": {"$exists": True, "$ne": None}}},
                {"$group": {"_id": "$group_id", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ],
            "auto_generated": [
                {"$match": {"metadata.is_auto_generated": True}},
                {"$count": "count"}
            ],
            "premium_hotspots": [
                {"$match": {"entity_type": "hotspot", "metadata.is_premium": True}},
                {"$count": "count"}
            ],
            "claimed_hotspots": [
                {"$match": {"entity_type": "hotspot", "metadata.is_claimed": True}},
                {"$count": "count"}
            ],
            "avg_confidence": [
                {"$match": {"metadata.confidence": {"$exists": True}}},
                {"$group": {"_id": None, "avg": {"$avg": "$metadata.confidence"}}}
            ],
            "avg_density": [
                {"$match": {"metadata.density": {"$exists": True}}},
                {"$group": {"_id": None, "avg": {"$avg": "$metadata.density"}}}
            ],
            "recent_activity": [
                {"$sort": {"created_at": -1}},
                {"$limit": 5},
                {"$project": {"_id": 1, "name": 1, "entity_type": 1, "created_at": 1}}
            ]
        }}
    ]
    
    result = await db[GEO_COLLECTION].aggregate(pipeline).to_list(1)
    
    if not result:
        return {
            "total_entities": 0,
            "by_type": {},
            "by_habitat": {},
            "top_users": [],
            "top_groups": [],
            "auto_generated_count": 0,
            "premium_hotspots": 0,
            "claimed_hotspots": 0,
            "avg_confidence": 0,
            "avg_density": 0,
            "recent_activity": []
        }
    
    data = result[0]
    
    # Safely extract counts with defaults
    def safe_count(facet_result):
        if facet_result and len(facet_result) > 0:
            return facet_result[0].get("count", 0)
        return 0
    
    def safe_avg(facet_result):
        if facet_result and len(facet_result) > 0:
            return facet_result[0].get("avg", 0) or 0
        return 0
    
    return {
        "total_entities": safe_count(data.get("total", [])),
        "by_type": {item["_id"]: item["count"] for item in data.get("by_type", []) if item.get("_id")},
        "by_habitat": {item["_id"]: item["count"] for item in data.get("by_habitat", []) if item.get("_id")},
        "top_users": [
            {"user_id": item["_id"], "count": item["count"]}
            for item in data.get("by_user", []) if item.get("_id")
        ],
        "top_groups": [
            {"group_id": item["_id"], "count": item["count"]}
            for item in data.get("by_group", []) if item.get("_id")
        ],
        "auto_generated_count": safe_count(data.get("auto_generated", [])),
        "premium_hotspots": safe_count(data.get("premium_hotspots", [])),
        "claimed_hotspots": safe_count(data.get("claimed_hotspots", [])),
        "avg_confidence": round(safe_avg(data.get("avg_confidence", [])), 3),
        "avg_density": round(safe_avg(data.get("avg_density", [])), 3),
        "recent_activity": [
            {
                "id": str(item["_id"]),
                "name": item.get("name"),
                "type": item.get("entity_type"),
                "created_at": item.get("created_at").isoformat() if item.get("created_at") else None
            }
            for item in data.get("recent_activity", [])
        ]
    }


@router.get("/analytics/heatmap")
async def get_heatmap_data(
    admin: UserWithRole = Depends(require_admin),
    entity_type: Optional[str] = None,
    resolution: int = Query(20, ge=5, le=100, description="Grid resolution")
):
    """
    Get heatmap data for visualization.
    Returns aggregated points for efficient rendering.
    """
    db = await get_db()
    
    match_stage = {"location": {"$exists": True}}
    if entity_type:
        match_stage["entity_type"] = entity_type
    
    # Calculate grid size (approximate degrees)
    grid_size = 1.0 / resolution
    
    pipeline = [
        {"$match": match_stage},
        {"$project": {
            "entity_type": 1,
            "lat": {"$arrayElemAt": ["$location.coordinates", 1]},
            "lng": {"$arrayElemAt": ["$location.coordinates", 0]},
            "density": "$metadata.density",
            "confidence": "$metadata.confidence"
        }},
        {"$group": {
            "_id": {
                "lat_grid": {"$floor": {"$divide": ["$lat", grid_size]}},
                "lng_grid": {"$floor": {"$divide": ["$lng", grid_size]}}
            },
            "count": {"$sum": 1},
            "avg_lat": {"$avg": "$lat"},
            "avg_lng": {"$avg": "$lng"},
            "avg_density": {"$avg": "$density"},
            "avg_confidence": {"$avg": "$confidence"},
            "types": {"$addToSet": "$entity_type"}
        }},
        {"$project": {
            "_id": 0,
            "latitude": "$avg_lat",
            "longitude": "$avg_lng",
            "intensity": "$count",
            "density": "$avg_density",
            "confidence": "$avg_confidence",
            "types": 1
        }}
    ]
    
    heatmap_points = await db[GEO_COLLECTION].aggregate(pipeline).to_list(1000)
    
    return {
        "resolution": resolution,
        "points": heatmap_points,
        "total_points": len(heatmap_points)
    }


@router.get("/analytics/density-map")
async def get_density_map(
    admin: UserWithRole = Depends(require_admin),
    bbox_sw_lat: float = Query(...),
    bbox_sw_lng: float = Query(...),
    bbox_ne_lat: float = Query(...),
    bbox_ne_lng: float = Query(...)
):
    """
    Get density data within a bounding box for detailed analysis.
    """
    db = await get_db()
    
    pipeline = [
        {"$match": {
            "location": {
                "$geoWithin": {
                    "$box": [
                        [bbox_sw_lng, bbox_sw_lat],
                        [bbox_ne_lng, bbox_ne_lat]
                    ]
                }
            }
        }},
        {"$group": {
            "_id": "$entity_type",
            "count": {"$sum": 1},
            "avg_density": {"$avg": "$metadata.density"},
            "points": {
                "$push": {
                    "lat": {"$arrayElemAt": ["$location.coordinates", 1]},
                    "lng": {"$arrayElemAt": ["$location.coordinates", 0]},
                    "density": "$metadata.density"
                }
            }
        }}
    ]
    
    result = await db[GEO_COLLECTION].aggregate(pipeline).to_list(20)
    
    return {
        "bbox": {
            "sw": {"lat": bbox_sw_lat, "lng": bbox_sw_lng},
            "ne": {"lat": bbox_ne_lat, "lng": bbox_ne_lng}
        },
        "data": result
    }


# ===========================================
# MONETIZATION ENDPOINTS
# ===========================================

@router.get("/monetization/available-hotspots")
async def get_available_hotspots(
    admin: UserWithRole = Depends(require_admin),
    min_confidence: float = Query(0.5, ge=0, le=1),
    limit: int = Query(50, ge=1, le=200)
):
    """
    Get unclaimed premium hotspots available for monetization.
    """
    db = await get_db()
    
    pipeline = [
        {"$match": {
            "entity_type": "hotspot",
            "metadata.is_premium": True,
            "metadata.is_claimed": {"$ne": True},
            "metadata.confidence": {"$gte": min_confidence}
        }},
        {"$sort": {"metadata.confidence": -1}},
        {"$limit": limit},
        {"$project": {
            "_id": 1,
            "name": 1,
            "location": 1,
            "metadata": 1,
            "created_at": 1
        }}
    ]
    
    hotspots = await db[GEO_COLLECTION].aggregate(pipeline).to_list(limit)
    
    return {
        "available_hotspots": [
            {
                "id": str(h["_id"]),
                "name": h.get("name"),
                "latitude": h["location"]["coordinates"][1] if h.get("location") else None,
                "longitude": h["location"]["coordinates"][0] if h.get("location") else None,
                "confidence": h.get("metadata", {}).get("confidence"),
                "habitat": h.get("metadata", {}).get("habitat"),
                "density": h.get("metadata", {}).get("density"),
                "estimated_value": _calculate_hotspot_value(h.get("metadata", {}))
            }
            for h in hotspots
        ],
        "total_available": len(hotspots)
    }


@router.post("/monetization/claim-hotspot/{hotspot_id}")
async def claim_hotspot(
    hotspot_id: str,
    admin: UserWithRole = Depends(require_admin),
    user_id: str = Query(...)
):
    """
    Claim a premium hotspot for a user.
    """
    db = await get_db()
    
    result = await db[GEO_COLLECTION].find_one_and_update(
        {
            "_id": hotspot_id,
            "entity_type": "hotspot",
            "metadata.is_premium": True,
            "metadata.is_claimed": {"$ne": True}
        },
        {
            "$set": {
                "metadata.is_claimed": True,
                "metadata.claimed_by": user_id,
                "metadata.claimed_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
        },
        return_document=True
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Hotspot not found or already claimed")
    
    return {
        "status": "claimed",
        "hotspot_id": hotspot_id,
        "claimed_by": user_id
    }


def _calculate_hotspot_value(metadata: dict) -> float:
    """Calculate estimated value of a hotspot for monetization"""
    confidence = metadata.get("confidence", 0.5)
    density = metadata.get("density", 0.5)
    
    # Simple value calculation (can be made more sophisticated)
    base_value = 10.0
    confidence_multiplier = 1 + (confidence * 2)
    density_multiplier = 1 + (density * 1.5)
    
    return round(base_value * confidence_multiplier * density_multiplier, 2)


# ===========================================
# EXPORT ENDPOINTS
# ===========================================

@router.get("/export/geojson")
async def export_geojson(
    admin: UserWithRole = Depends(require_admin),
    entity_type: Optional[str] = None,
    user_id: Optional[str] = None,
    limit: int = Query(1000, ge=1, le=10000)
):
    """
    Export geo entities as GeoJSON FeatureCollection.
    """
    db = await get_db()
    
    query: Dict[str, Any] = {"location": {"$exists": True}}
    
    if entity_type:
        query["entity_type"] = entity_type
    if user_id:
        query["user_id"] = user_id
    
    cursor = db[GEO_COLLECTION].find(query).limit(limit)
    entities = await cursor.to_list(limit)
    
    features = []
    for e in entities:
        feature = {
            "type": "Feature",
            "geometry": e.get("location"),
            "properties": {
                "id": str(e["_id"]),
                "name": e.get("name"),
                "entity_type": e.get("entity_type"),
                "subtype": e.get("subtype"),
                "user_id": e.get("user_id"),
                "active": e.get("active"),
                "metadata": e.get("metadata", {}),
                "created_at": e.get("created_at", "").isoformat() if e.get("created_at") else None
            }
        }
        features.append(feature)
    
    return {
        "type": "FeatureCollection",
        "features": features,
        "properties": {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "total_features": len(features)
        }
    }


# ===========================================
# MODULE INFO
# ===========================================

@router.get("/")
async def admin_module_info(
    admin: UserWithRole = Depends(require_admin)
):
    """Get admin module information (ADMIN ONLY)"""
    return {
        "module": "admin_geo_engine",
        "version": "1.0.0",
        "description": "Global Geospatial Administration for BIONIC HUNT/Chasse V3",
        "phase": "P6.5 - Admin Dashboard",
        "features": [
            "Global view of all geo entities",
            "Advanced filtering (habitat, density, user, group)",
            "Hotspot monetization tools",
            "Analytics and heatmap generation",
            "GeoJSON export"
        ],
        "endpoints": {
            "all": "/api/admin/geo/all",
            "hotspots": "/api/admin/geo/hotspots",
            "corridors": "/api/admin/geo/corridors",
            "analytics": "/api/admin/geo/analytics/overview",
            "heatmap": "/api/admin/geo/analytics/heatmap",
            "monetization": "/api/admin/geo/monetization/available-hotspots",
            "export": "/api/admin/geo/export/geojson"
        }
    }
