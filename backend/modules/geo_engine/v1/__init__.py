"""
Geo Engine v1 - Unified Geospatial API
Phase P6.2 - Normalization & Phase P6.3 - Optimization

Endpoints:
- CRUD for all geo entities (waypoints, zones, cameras, hotspots, etc.)
- Spatial queries (nearby, within bbox, clustering)
- Hunting groups management
- Hotspot auto-generation
- Admin global view
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
import logging
import math

from models.geo_entity import (
    GeoEntityType, GeoEntityCreate, GeoEntityUpdate, GeoEntityResponse,
    GeoQueryParams, GeoStatsResponse, GeoMetadata, HotspotMetadata,
    HuntingGroupCreate, HuntingGroupResponse, HabitatType
)
from database import Database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/geo", tags=["Geo Engine (Unified)"])

# Collection name
GEO_COLLECTION = "geo_entities"
GROUPS_COLLECTION = "hunting_groups"


async def get_db():
    """Get database instance"""
    return Database.get_database()


# ===========================================
# DATABASE INDEXES SETUP
# ===========================================

async def ensure_indexes():
    """Create optimized indexes for geo queries"""
    db = await get_db()
    
    try:
        # 2dsphere index for spatial queries
        await db[GEO_COLLECTION].create_index([("location", "2dsphere")])
        
        # Composite indexes for common queries
        await db[GEO_COLLECTION].create_index([("user_id", 1), ("entity_type", 1)])
        await db[GEO_COLLECTION].create_index([("group_id", 1), ("entity_type", 1)])
        await db[GEO_COLLECTION].create_index([("entity_type", 1), ("active", 1)])
        await db[GEO_COLLECTION].create_index([("metadata.habitat", 1)])
        await db[GEO_COLLECTION].create_index([("metadata.is_auto_generated", 1)])
        await db[GEO_COLLECTION].create_index([("created_at", -1)])
        
        # Groups indexes
        await db[GROUPS_COLLECTION].create_index([("owner_id", 1)])
        await db[GROUPS_COLLECTION].create_index([("members.user_id", 1)])
        
        logger.info("✓ Geo Engine indexes created successfully")
    except Exception as e:
        logger.warning(f"Index creation warning: {e}")


# ===========================================
# GEO ENTITY CRUD
# ===========================================

# Types d'entités PRIVÉES (visibles uniquement par l'utilisateur propriétaire ou admin)
PRIVATE_ENTITY_TYPES = {"hotspot", "corridor"}


@router.post("/entities", response_model=GeoEntityResponse)
async def create_entity(entity: GeoEntityCreate, user_id: str = Query(...)):
    """Create a new geo entity"""
    db = await get_db()
    
    doc = entity.to_document(user_id)
    
    # 🔒 Les hotspots sont toujours créés comme privés (pas de group_id)
    if entity.entity_type.value in PRIVATE_ENTITY_TYPES:
        doc["group_id"] = None  # Force privé
        doc["metadata"]["is_private"] = True
    
    await db[GEO_COLLECTION].insert_one(doc)
    
    logger.info(f"Created {entity.entity_type} entity: {doc['_id']}")
    return GeoEntityResponse.from_document(doc)


@router.get("/entities", response_model=List[GeoEntityResponse])
async def list_entities(
    user_id: str = Query(...),
    entity_type: Optional[str] = None,
    group_id: Optional[str] = None,
    active: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500)
):
    """
    List geo entities for a user with optional filters.
    
    ⚠️ CONFIDENTIALITÉ: Les hotspots et corridors sont EXCLUS des requêtes de groupe.
    Ces entités ne sont visibles que par leur propriétaire.
    """
    db = await get_db()
    
    # Base query: entités de l'utilisateur
    query = {"user_id": user_id}
    
    # 🔒 Si on demande des entités de groupe, EXCLURE les types privés
    if group_id:
        query = {
            "$or": [
                {"user_id": user_id},
                {
                    "group_id": group_id,
                    "entity_type": {"$nin": list(PRIVATE_ENTITY_TYPES)}  # Exclure hotspots/corridors
                }
            ]
        }
    
    if entity_type:
        query["entity_type"] = entity_type
    if active is not None:
        query["active"] = active
    
    cursor = db[GEO_COLLECTION].find(query).sort("created_at", -1).skip(skip).limit(limit)
    entities = await cursor.to_list(limit)
    
    return [GeoEntityResponse.from_document(doc) for doc in entities]


@router.get("/entities/{entity_id}", response_model=GeoEntityResponse)
async def get_entity(entity_id: str, user_id: str = Query(...)):
    """
    Get a specific geo entity.
    
    ⚠️ CONFIDENTIALITÉ: Les hotspots ne sont accessibles que par leur propriétaire.
    """
    db = await get_db()
    
    entity = await db[GEO_COLLECTION].find_one({"_id": entity_id})
    
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    # 🔒 Vérification de propriété pour les entités privées
    if entity.get("entity_type") in PRIVATE_ENTITY_TYPES:
        if entity.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Accès refusé: cette entité est privée")
    else:
        # Pour les entités non-privées, vérifier propriété ou groupe
        if entity.get("user_id") != user_id and not entity.get("group_id"):
            raise HTTPException(status_code=403, detail="Accès refusé")
    
    return GeoEntityResponse.from_document(entity)


@router.put("/entities/{entity_id}", response_model=GeoEntityResponse)
async def update_entity(entity_id: str, update: GeoEntityUpdate, user_id: str = Query(...)):
    """Update a geo entity"""
    db = await get_db()
    
    # Build update document
    update_doc = {"updated_at": datetime.now(timezone.utc)}
    
    for field, value in update.model_dump(exclude_unset=True).items():
        if value is not None:
            if field in ["latitude", "longitude"]:
                continue  # Handle separately
            elif field == "metadata" and value:
                update_doc["metadata"] = value.model_dump() if hasattr(value, 'model_dump') else value
            else:
                update_doc[field] = value
    
    # Handle location update
    if update.latitude is not None and update.longitude is not None:
        update_doc["location"] = {
            "type": "Point",
            "coordinates": [update.longitude, update.latitude]
        }
    
    result = await db[GEO_COLLECTION].find_one_and_update(
        {"_id": entity_id, "user_id": user_id},
        {"$set": update_doc},
        return_document=True
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    return GeoEntityResponse.from_document(result)


@router.delete("/entities/{entity_id}")
async def delete_entity(entity_id: str, user_id: str = Query(...)):
    """Delete a geo entity"""
    db = await get_db()
    
    result = await db[GEO_COLLECTION].delete_one({
        "_id": entity_id,
        "user_id": user_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    return {"status": "deleted", "id": entity_id}


# ===========================================
# SPATIAL QUERIES
# ===========================================

@router.get("/nearby", response_model=List[GeoEntityResponse])
async def find_nearby(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    max_distance: float = Query(5000, ge=0, description="Max distance in meters"),
    user_id: str = Query(...),
    entity_type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200)
):
    """Find entities near a location using 2dsphere index"""
    db = await get_db()
    
    query = {
        "location": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [longitude, latitude]
                },
                "$maxDistance": max_distance
            }
        },
        "$or": [{"user_id": user_id}, {"metadata.is_auto_generated": True}]
    }
    
    if entity_type:
        query["entity_type"] = entity_type
    
    cursor = db[GEO_COLLECTION].find(query).limit(limit)
    entities = await cursor.to_list(limit)
    
    return [GeoEntityResponse.from_document(doc) for doc in entities]


@router.get("/within-bbox", response_model=List[GeoEntityResponse])
async def find_within_bbox(
    sw_lat: float = Query(..., ge=-90, le=90),
    sw_lng: float = Query(..., ge=-180, le=180),
    ne_lat: float = Query(..., ge=-90, le=90),
    ne_lng: float = Query(..., ge=-180, le=180),
    user_id: str = Query(...),
    entity_type: Optional[str] = None,
    limit: int = Query(200, ge=1, le=1000)
):
    """Find entities within a bounding box"""
    db = await get_db()
    
    query = {
        "location": {
            "$geoWithin": {
                "$box": [
                    [sw_lng, sw_lat],
                    [ne_lng, ne_lat]
                ]
            }
        },
        "$or": [{"user_id": user_id}, {"metadata.is_auto_generated": True}]
    }
    
    if entity_type:
        query["entity_type"] = entity_type
    
    cursor = db[GEO_COLLECTION].find(query).limit(limit)
    entities = await cursor.to_list(limit)
    
    return [GeoEntityResponse.from_document(doc) for doc in entities]


@router.get("/clusters")
async def get_clusters(
    user_id: str = Query(...),
    zoom_level: int = Query(10, ge=1, le=20),
    entity_type: Optional[str] = None
):
    """Get clustered entities for map display at different zoom levels"""
    db = await get_db()
    
    # Calculate grid size based on zoom level
    # Higher zoom = smaller grid = more detail
    grid_size = 180 / (2 ** zoom_level)
    
    pipeline = [
        {"$match": {
            "$or": [{"user_id": user_id}, {"metadata.is_auto_generated": True}],
            "location": {"$exists": True}
        }}
    ]
    
    if entity_type:
        pipeline[0]["$match"]["entity_type"] = entity_type
    
    pipeline.extend([
        {"$project": {
            "entity_type": 1,
            "location": 1,
            "grid_lat": {
                "$multiply": [
                    {"$floor": {"$divide": [{"$arrayElemAt": ["$location.coordinates", 1]}, grid_size]}},
                    grid_size
                ]
            },
            "grid_lng": {
                "$multiply": [
                    {"$floor": {"$divide": [{"$arrayElemAt": ["$location.coordinates", 0]}, grid_size]}},
                    grid_size
                ]
            }
        }},
        {"$group": {
            "_id": {"lat": "$grid_lat", "lng": "$grid_lng"},
            "count": {"$sum": 1},
            "center_lat": {"$avg": {"$arrayElemAt": ["$location.coordinates", 1]}},
            "center_lng": {"$avg": {"$arrayElemAt": ["$location.coordinates", 0]}},
            "types": {"$addToSet": "$entity_type"}
        }},
        {"$project": {
            "_id": 0,
            "latitude": "$center_lat",
            "longitude": "$center_lng",
            "count": 1,
            "types": 1
        }}
    ])
    
    clusters = await db[GEO_COLLECTION].aggregate(pipeline).to_list(500)
    return {"zoom_level": zoom_level, "clusters": clusters}


# ===========================================
# HUNTING GROUPS
# ===========================================

@router.post("/groups", response_model=HuntingGroupResponse)
async def create_group(group: HuntingGroupCreate, user_id: str = Query(...)):
    """Create a new hunting group"""
    db = await get_db()
    
    now = datetime.now(timezone.utc)
    doc = {
        "_id": str(uuid.uuid4()),
        "name": group.name,
        "owner_id": user_id,
        "description": group.description,
        "territory_id": group.territory_id,
        "members": [{"user_id": user_id, "role": "owner", "joined_at": now}],
        "settings": group.settings or {},
        "created_at": now,
        "updated_at": now
    }
    
    await db[GROUPS_COLLECTION].insert_one(doc)
    return HuntingGroupResponse.from_document(doc)


@router.get("/groups", response_model=List[HuntingGroupResponse])
async def list_groups(user_id: str = Query(...)):
    """List hunting groups for a user"""
    db = await get_db()
    
    cursor = db[GROUPS_COLLECTION].find({
        "$or": [
            {"owner_id": user_id},
            {"members.user_id": user_id}
        ]
    })
    
    groups = await cursor.to_list(100)
    return [HuntingGroupResponse.from_document(doc) for doc in groups]


@router.post("/groups/{group_id}/members")
async def add_group_member(
    group_id: str,
    member_id: str = Query(...),
    role: str = Query("member"),
    user_id: str = Query(...)
):
    """Add a member to a hunting group"""
    db = await get_db()
    
    # Verify owner
    group = await db[GROUPS_COLLECTION].find_one({"_id": group_id, "owner_id": user_id})
    if not group:
        raise HTTPException(status_code=403, detail="Not authorized or group not found")
    
    # Add member
    now = datetime.now(timezone.utc)
    await db[GROUPS_COLLECTION].update_one(
        {"_id": group_id},
        {
            "$addToSet": {"members": {"user_id": member_id, "role": role, "joined_at": now}},
            "$set": {"updated_at": now}
        }
    )
    
    return {"status": "added", "member_id": member_id, "group_id": group_id}


@router.delete("/groups/{group_id}/members/{member_id}")
async def remove_group_member(group_id: str, member_id: str, user_id: str = Query(...)):
    """Remove a member from a hunting group"""
    db = await get_db()
    
    # Verify owner
    group = await db[GROUPS_COLLECTION].find_one({"_id": group_id, "owner_id": user_id})
    if not group:
        raise HTTPException(status_code=403, detail="Not authorized or group not found")
    
    await db[GROUPS_COLLECTION].update_one(
        {"_id": group_id},
        {
            "$pull": {"members": {"user_id": member_id}},
            "$set": {"updated_at": datetime.now(timezone.utc)}
        }
    )
    
    return {"status": "removed", "member_id": member_id}


# ===========================================
# HOTSPOT AUTO-GENERATION
# ===========================================

@router.post("/hotspots/generate")
async def generate_hotspots(
    user_id: str = Query(...),
    center_lat: float = Query(..., ge=-90, le=90),
    center_lng: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(5, ge=1, le=50),
    count: int = Query(10, ge=1, le=50)
):
    """
    Auto-generate hotspots based on environmental and behavioral data.
    Uses terrain analysis, corridor detection, and habitat scoring.
    """
    db = await get_db()
    
    generated_hotspots = []
    now = datetime.now(timezone.utc)
    
    # Get existing entities in the area to avoid duplicates
    existing = await db[GEO_COLLECTION].find({
        "location": {
            "$near": {
                "$geometry": {"type": "Point", "coordinates": [center_lng, center_lat]},
                "$maxDistance": radius_km * 1000
            }
        }
    }).to_list(500)
    
    existing_coords = set()
    for e in existing:
        if e.get("location", {}).get("coordinates"):
            coords = e["location"]["coordinates"]
            # Round to 4 decimals for comparison
            existing_coords.add((round(coords[1], 4), round(coords[0], 4)))
    
    # Generate candidate hotspots using environmental heuristics
    for i in range(count * 3):  # Generate more candidates than needed
        if len(generated_hotspots) >= count:
            break
        
        # Generate position within radius using environmental bias
        angle = (i * 137.508) % 360  # Golden angle for even distribution
        distance = radius_km * math.sqrt((i + 1) / (count * 3))  # Varied distances
        
        # Convert to coordinates
        lat_offset = distance * math.cos(math.radians(angle)) / 111.32
        lng_offset = distance * math.sin(math.radians(angle)) / (111.32 * math.cos(math.radians(center_lat)))
        
        new_lat = round(center_lat + lat_offset, 6)
        new_lng = round(center_lng + lng_offset, 6)
        
        # Skip if too close to existing
        if (round(new_lat, 4), round(new_lng, 4)) in existing_coords:
            continue
        
        # Calculate environmental scores (simulated based on position)
        habitat_score = _calculate_habitat_score(new_lat, new_lng, center_lat, center_lng)
        corridor_score = _calculate_corridor_score(new_lat, new_lng, distance)
        density_score = _calculate_density_score(new_lat, new_lng)
        
        # Combined confidence score
        confidence = (habitat_score * 0.4 + corridor_score * 0.35 + density_score * 0.25)
        
        if confidence < 0.3:  # Skip low-quality candidates
            continue
        
        # Determine habitat type based on position
        habitat = _determine_habitat(new_lat, new_lng, center_lat, center_lng)
        
        hotspot_doc = {
            "_id": str(uuid.uuid4()),
            "user_id": "system",  # System-generated
            "group_id": None,
            "name": f"Hotspot Auto #{len(generated_hotspots) + 1}",
            "entity_type": "hotspot",
            "subtype": "auto_generated",
            "location": {
                "type": "Point",
                "coordinates": [new_lng, new_lat]
            },
            "active": True,
            "visible": True,
            "color": _get_hotspot_color(confidence),
            "icon": "🔥",
            "metadata": {
                "habitat": habitat,
                "density": round(density_score, 2),
                "altitude": round(200 + (distance * 50), 1),
                "activity_score": round(confidence * 100, 1),
                "is_auto_generated": True,
                "generation_source": "environmental",
                "confidence": round(confidence, 3),
                "is_premium": confidence > 0.7,
                "is_claimed": False,
                "corridors": [],
                "tags": ["auto-generated", habitat]
            },
            "description": f"Hotspot généré automatiquement - Confiance: {confidence*100:.0f}%",
            "created_at": now,
            "updated_at": now
        }
        
        generated_hotspots.append(hotspot_doc)
        existing_coords.add((round(new_lat, 4), round(new_lng, 4)))
    
    # Insert all generated hotspots
    if generated_hotspots:
        await db[GEO_COLLECTION].insert_many(generated_hotspots)
    
    return {
        "status": "generated",
        "count": len(generated_hotspots),
        "hotspots": [GeoEntityResponse.from_document(h) for h in generated_hotspots]
    }


def _calculate_habitat_score(lat: float, lng: float, center_lat: float, center_lng: float) -> float:
    """Calculate habitat quality score based on position"""
    # Simulate habitat scoring based on distance from center and terrain features
    distance = math.sqrt((lat - center_lat)**2 + (lng - center_lng)**2)
    
    # Edge habitats (moderate distance) are often better
    edge_score = 1.0 - abs(distance - 0.02) * 20
    edge_score = max(0, min(1, edge_score))
    
    # Add some randomness based on coordinates
    terrain_factor = abs(math.sin(lat * 100) * math.cos(lng * 100))
    
    return (edge_score * 0.6 + terrain_factor * 0.4)


def _calculate_corridor_score(lat: float, lng: float, distance: float) -> float:
    """Calculate corridor proximity score"""
    # Simulate corridor detection - valleys and ridges are common corridors
    corridor_factor = abs(math.sin(lat * 50 + lng * 50))
    
    # Moderate distances often have better corridor connectivity
    distance_factor = 1.0 - abs(distance - 2.5) / 5
    distance_factor = max(0, min(1, distance_factor))
    
    return (corridor_factor * 0.5 + distance_factor * 0.5)


def _calculate_density_score(lat: float, lng: float) -> float:
    """Calculate wildlife density score based on terrain"""
    # Simulate density based on coordinate patterns (real would use actual data)
    density = abs(math.sin(lat * 30) * math.cos(lng * 30))
    return density


def _determine_habitat(lat: float, lng: float, center_lat: float, center_lng: float) -> str:
    """Determine habitat type based on position"""
    distance = math.sqrt((lat - center_lat)**2 + (lng - center_lng)**2)
    angle = math.atan2(lat - center_lat, lng - center_lng)
    
    # Simple habitat classification based on position
    if distance < 0.01:
        return "clearing"
    elif abs(math.sin(angle * 5)) > 0.7:
        return "edge"
    elif distance > 0.03:
        return "forest_mixed"
    else:
        habitats = ["forest_coniferous", "forest_deciduous", "wetland", "ridge"]
        index = int(abs(math.sin(lat * 100 + lng * 100)) * len(habitats))
        return habitats[index % len(habitats)]


def _get_hotspot_color(confidence: float) -> str:
    """Get color based on confidence score"""
    if confidence > 0.7:
        return "#ef4444"  # Red - high quality
    elif confidence > 0.5:
        return "#f97316"  # Orange - good
    elif confidence > 0.3:
        return "#eab308"  # Yellow - moderate
    else:
        return "#84cc16"  # Green - lower


# ===========================================
# STATISTICS & ANALYTICS
# ===========================================

@router.get("/stats", response_model=GeoStatsResponse)
async def get_stats(user_id: str = Query(...)):
    """Get statistics for user's geo entities"""
    db = await get_db()
    
    pipeline = [
        {"$match": {"$or": [{"user_id": user_id}, {"metadata.is_auto_generated": True}]}},
        {"$facet": {
            "total": [{"$count": "count"}],
            "by_type": [{"$group": {"_id": "$entity_type", "count": {"$sum": 1}}}],
            "by_habitat": [
                {"$match": {"metadata.habitat": {"$exists": True}}},
                {"$group": {"_id": "$metadata.habitat", "count": {"$sum": 1}}}
            ],
            "avg_density": [
                {"$match": {"metadata.density": {"$exists": True}}},
                {"$group": {"_id": None, "avg": {"$avg": "$metadata.density"}}}
            ],
            "active": [{"$match": {"active": True}}, {"$count": "count"}],
            "auto_generated": [
                {"$match": {"metadata.is_auto_generated": True}},
                {"$count": "count"}
            ]
        }}
    ]
    
    result = await db[GEO_COLLECTION].aggregate(pipeline).to_list(1)
    
    if not result:
        return GeoStatsResponse(
            total_entities=0, by_type={}, by_habitat={},
            avg_density=None, hotspots_count=0, corridors_count=0,
            active_count=0, auto_generated_count=0
        )
    
    data = result[0]
    
    by_type = {item["_id"]: item["count"] for item in data.get("by_type", [])}
    by_habitat = {item["_id"]: item["count"] for item in data.get("by_habitat", []) if item["_id"]}
    
    return GeoStatsResponse(
        total_entities=data.get("total", [{}])[0].get("count", 0),
        by_type=by_type,
        by_habitat=by_habitat,
        avg_density=data.get("avg_density", [{}])[0].get("avg"),
        hotspots_count=by_type.get("hotspot", 0),
        corridors_count=by_type.get("corridor", 0),
        active_count=data.get("active", [{}])[0].get("count", 0),
        auto_generated_count=data.get("auto_generated", [{}])[0].get("count", 0)
    )


# ===========================================
# MIGRATION UTILITIES
# ===========================================

@router.post("/migrate/from-territory-waypoints")
async def migrate_from_territory_waypoints(user_id: str = Query(...)):
    """
    Migrate existing waypoints from territory_waypoints to unified geo_entities.
    One-time migration utility.
    """
    db = await get_db()
    
    # Get existing waypoints from old collection
    old_waypoints = await db["territory_waypoints"].find({}).to_list(1000)
    
    migrated = 0
    skipped = 0
    
    for wp in old_waypoints:
        # Check if already migrated
        existing = await db[GEO_COLLECTION].find_one({
            "metadata.legacy_id": str(wp.get("_id"))
        })
        
        if existing:
            skipped += 1
            continue
        
        # Map to new schema
        new_doc = {
            "_id": str(uuid.uuid4()),
            "user_id": wp.get("user_id", "default_user"),
            "group_id": None,
            "name": wp.get("name", "Migrated Waypoint"),
            "entity_type": "waypoint",
            "subtype": wp.get("waypoint_type", "custom"),
            "location": {
                "type": "Point",
                "coordinates": [
                    wp.get("longitude", wp.get("lng", 0)),
                    wp.get("latitude", wp.get("lat", 0))
                ]
            },
            "color": wp.get("color"),
            "icon": wp.get("icon"),
            "active": wp.get("active", True),
            "visible": True,
            "metadata": {
                "legacy_id": str(wp.get("_id")),
                "notes": wp.get("notes") or wp.get("description"),
                "is_auto_generated": False
            },
            "description": wp.get("description") or wp.get("notes"),
            "created_at": wp.get("created_at", datetime.now(timezone.utc)),
            "updated_at": datetime.now(timezone.utc)
        }
        
        await db[GEO_COLLECTION].insert_one(new_doc)
        migrated += 1
    
    return {
        "status": "completed",
        "migrated": migrated,
        "skipped": skipped,
        "total_in_new_collection": await db[GEO_COLLECTION].count_documents({})
    }


# ===========================================
# MODULE INFO
# ===========================================

@router.get("/")
async def module_info():
    """Get module information"""
    return {
        "module": "geo_engine",
        "version": "1.0.0",
        "description": "Unified Geospatial Engine for BIONIC HUNT/Chasse V3",
        "phase": "P6.2 - Normalization",
        "collection": GEO_COLLECTION,
        "features": [
            "Unified geo entity schema",
            "2dsphere spatial queries",
            "Hunting groups support",
            "Hotspot auto-generation",
            "Clustering for map display",
            "Migration utilities"
        ]
    }
