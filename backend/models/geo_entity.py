"""
GeoEntity - Unified Geospatial Model for BIONIC HUNT/Chasse V3
Phase P6.2 - Normalization

Single source of truth for all geospatial entities:
- waypoints, zones, sectors, caches, cameras, POI, hotspots, corridors

Collection: geo_entities (with 2dsphere index)
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime, timezone
from enum import Enum
import uuid


# ===========================================
# ENUMS
# ===========================================

class GeoEntityType(str, Enum):
    """Types of geospatial entities"""
    WAYPOINT = "waypoint"
    ZONE = "zone"
    SECTOR = "sector"
    CACHE = "cache"
    CAMERA = "camera"
    POI = "poi"
    HOTSPOT = "hotspot"
    CORRIDOR = "corridor"
    TRAIL = "trail"
    STAND = "stand"
    FEEDER = "feeder"
    WATER_SOURCE = "water_source"
    OBSERVATION = "observation"


class WaypointSubtype(str, Enum):
    """Subtypes for waypoint entities"""
    OBSERVATION = "observation"
    CAMERA = "camera"
    CACHE = "cache"
    STAND = "stand"
    WATER = "water"
    TRAIL_START = "trail_start"
    CUSTOM = "custom"
    HUNTING = "hunting"
    FEEDER = "feeder"
    SIGHTING = "sighting"
    PARKING = "parking"


class HabitatType(str, Enum):
    """Types of habitat for metadata"""
    FOREST_MIXED = "forest_mixed"
    FOREST_CONIFEROUS = "forest_coniferous"
    FOREST_DECIDUOUS = "forest_deciduous"
    CLEARING = "clearing"
    WETLAND = "wetland"
    FIELD = "field"
    EDGE = "edge"
    RIDGE = "ridge"
    VALLEY = "valley"
    STREAM = "stream"
    UNKNOWN = "unknown"


class Exposure(str, Enum):
    """Cardinal exposure directions"""
    NORTH = "N"
    SOUTH = "S"
    EAST = "E"
    WEST = "W"
    NORTHEAST = "NE"
    NORTHWEST = "NW"
    SOUTHEAST = "SE"
    SOUTHWEST = "SW"
    FLAT = "FLAT"


# ===========================================
# GEOJSON LOCATION MODEL
# ===========================================

class GeoJSONPoint(BaseModel):
    """GeoJSON Point format for MongoDB 2dsphere"""
    type: Literal["Point"] = "Point"
    coordinates: List[float] = Field(
        ..., 
        description="[longitude, latitude] - Note: GeoJSON uses lng,lat order",
        min_length=2,
        max_length=2
    )
    
    @classmethod
    def from_lat_lng(cls, latitude: float, longitude: float) -> "GeoJSONPoint":
        """Create from latitude/longitude (human-friendly order)"""
        return cls(coordinates=[longitude, latitude])
    
    @property
    def latitude(self) -> float:
        return self.coordinates[1]
    
    @property
    def longitude(self) -> float:
        return self.coordinates[0]


# ===========================================
# METADATA MODELS
# ===========================================

class GeoMetadata(BaseModel):
    """Enriched metadata for geospatial entities"""
    # Environmental
    habitat: Optional[HabitatType] = None
    density: Optional[float] = Field(None, ge=0, le=1, description="Wildlife density 0-1")
    altitude: Optional[float] = Field(None, description="Altitude in meters")
    slope: Optional[float] = Field(None, ge=0, le=90, description="Slope in degrees")
    exposure: Optional[Exposure] = None
    
    # Connectivity
    corridors: Optional[List[str]] = Field(default_factory=list, description="Connected corridor IDs")
    nearby_zones: Optional[List[str]] = Field(default_factory=list, description="Nearby zone IDs")
    nearby_water: Optional[float] = Field(None, description="Distance to nearest water in meters")
    
    # Behavioral
    activity_score: Optional[float] = Field(None, ge=0, le=100, description="Wildlife activity score 0-100")
    best_time: Optional[str] = Field(None, description="Best time of day (morning/evening/night)")
    seasonal_rating: Optional[Dict[str, float]] = Field(default_factory=dict, description="Rating by season")
    
    # Hotspot-specific fields (included in base for API compatibility)
    is_auto_generated: Optional[bool] = False
    generation_source: Optional[str] = None  # "environmental", "behavioral", "user"
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Generation confidence 0-1")
    is_premium: Optional[bool] = False
    is_claimed: Optional[bool] = False
    claimed_by: Optional[str] = None
    wqs_score: Optional[float] = Field(None, ge=0, le=100, description="Waypoint Quality Score")
    success_rate: Optional[float] = Field(None, ge=0, le=100, description="Historical success rate")
    visit_count: Optional[int] = Field(0, ge=0)
    last_success: Optional[datetime] = None
    
    # Corridor-specific fields
    start_point_id: Optional[str] = None
    end_point_id: Optional[str] = None
    length_meters: Optional[float] = None
    width_meters: Optional[float] = None
    traffic_score: Optional[float] = Field(None, ge=0, le=100)
    direction: Optional[str] = None  # "bidirectional", "north-south", etc.
    
    # Custom
    tags: Optional[List[str]] = Field(default_factory=list)
    notes: Optional[str] = None
    custom: Optional[Dict[str, Any]] = Field(default_factory=dict)
    legacy_id: Optional[str] = None  # For migration tracking


class HotspotMetadata(GeoMetadata):
    """Extended metadata specific to hotspots"""
    # Scoring
    wqs_score: Optional[float] = Field(None, ge=0, le=100, description="Waypoint Quality Score")
    success_rate: Optional[float] = Field(None, ge=0, le=100, description="Historical success rate")
    visit_count: Optional[int] = Field(0, ge=0)
    last_success: Optional[datetime] = None
    
    # Auto-generation
    is_auto_generated: bool = False
    generation_source: Optional[str] = None  # "environmental", "behavioral", "user"
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Generation confidence 0-1")
    
    # Monetization
    is_premium: bool = False
    is_claimed: bool = False
    claimed_by: Optional[str] = None


class CorridorMetadata(GeoMetadata):
    """Extended metadata specific to corridors"""
    start_point_id: Optional[str] = None
    end_point_id: Optional[str] = None
    length_meters: Optional[float] = None
    width_meters: Optional[float] = None
    traffic_score: Optional[float] = Field(None, ge=0, le=100)
    direction: Optional[str] = None  # "bidirectional", "north-south", etc.


# ===========================================
# MAIN GEO ENTITY MODELS
# ===========================================

class GeoEntityBase(BaseModel):
    """Base model for creating geo entities"""
    name: str = Field(..., min_length=1, max_length=200)
    entity_type: GeoEntityType
    subtype: Optional[str] = None
    
    # Location (can be provided as lat/lng or GeoJSON)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    location: Optional[GeoJSONPoint] = None
    
    # For zones/polygons
    geometry: Optional[Dict[str, Any]] = None  # GeoJSON Polygon
    radius: Optional[float] = Field(None, ge=0, description="Radius in meters for circular zones")
    
    # Visual
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    icon: Optional[str] = None
    
    # State
    active: bool = True
    visible: bool = True
    
    # Metadata
    metadata: Optional[GeoMetadata] = None
    description: Optional[str] = None


class GeoEntityCreate(GeoEntityBase):
    """Model for creating a new geo entity"""
    group_id: Optional[str] = None  # For group sync
    
    def to_document(self, user_id: str) -> dict:
        """Convert to MongoDB document"""
        now = datetime.now(timezone.utc)
        
        # Build GeoJSON location
        if self.location:
            location = self.location.model_dump()
        elif self.latitude is not None and self.longitude is not None:
            location = {"type": "Point", "coordinates": [self.longitude, self.latitude]}
        else:
            location = None
        
        return {
            "_id": str(uuid.uuid4()),
            "user_id": user_id,
            "group_id": self.group_id,
            "name": self.name,
            "entity_type": self.entity_type.value,
            "subtype": self.subtype,
            "location": location,
            "geometry": self.geometry,
            "radius": self.radius,
            "color": self.color,
            "icon": self.icon,
            "active": self.active,
            "visible": self.visible,
            "metadata": self.metadata.model_dump() if self.metadata else {},
            "description": self.description,
            "created_at": now,
            "updated_at": now
        }


class GeoEntityUpdate(BaseModel):
    """Model for updating a geo entity"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    subtype: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    geometry: Optional[Dict[str, Any]] = None
    radius: Optional[float] = Field(None, ge=0)
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    icon: Optional[str] = None
    active: Optional[bool] = None
    visible: Optional[bool] = None
    metadata: Optional[GeoMetadata] = None
    description: Optional[str] = None
    group_id: Optional[str] = None


class GeoEntityResponse(BaseModel):
    """Response model for geo entities"""
    id: str
    user_id: str
    group_id: Optional[str] = None
    name: str
    entity_type: str
    subtype: Optional[str] = None
    
    # Dual format for convenience
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location: Optional[Dict[str, Any]] = None
    
    geometry: Optional[Dict[str, Any]] = None
    radius: Optional[float] = None
    
    color: Optional[str] = None
    icon: Optional[str] = None
    active: bool = True
    visible: bool = True
    
    metadata: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_document(cls, doc: dict) -> "GeoEntityResponse":
        """Create from MongoDB document"""
        location = doc.get("location")
        lat = None
        lng = None
        
        if location and "coordinates" in location:
            lng = location["coordinates"][0]
            lat = location["coordinates"][1]
        
        return cls(
            id=str(doc["_id"]),
            user_id=doc.get("user_id", ""),
            group_id=doc.get("group_id"),
            name=doc.get("name", ""),
            entity_type=doc.get("entity_type", "waypoint"),
            subtype=doc.get("subtype"),
            latitude=lat,
            longitude=lng,
            location=location,
            geometry=doc.get("geometry"),
            radius=doc.get("radius"),
            color=doc.get("color"),
            icon=doc.get("icon"),
            active=doc.get("active", True),
            visible=doc.get("visible", True),
            metadata=doc.get("metadata", {}),
            description=doc.get("description"),
            created_at=doc.get("created_at", datetime.now(timezone.utc)),
            updated_at=doc.get("updated_at", datetime.now(timezone.utc))
        )


# ===========================================
# HUNTING GROUP MODELS
# ===========================================

class HuntingGroupCreate(BaseModel):
    """Model for creating a hunting group"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    territory_id: Optional[str] = None  # Link to a territory
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict)


class HuntingGroupResponse(BaseModel):
    """Response model for hunting groups"""
    id: str
    name: str
    owner_id: str
    description: Optional[str] = None
    territory_id: Optional[str] = None
    members: List[Dict[str, Any]] = []  # [{user_id, role, joined_at}]
    settings: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_document(cls, doc: dict) -> "HuntingGroupResponse":
        return cls(
            id=str(doc["_id"]),
            name=doc.get("name", ""),
            owner_id=doc.get("owner_id", ""),
            description=doc.get("description"),
            territory_id=doc.get("territory_id"),
            members=doc.get("members", []),
            settings=doc.get("settings", {}),
            created_at=doc.get("created_at", datetime.now(timezone.utc)),
            updated_at=doc.get("updated_at", datetime.now(timezone.utc))
        )


# ===========================================
# QUERY/FILTER MODELS
# ===========================================

class GeoQueryParams(BaseModel):
    """Query parameters for geo entity searches"""
    entity_type: Optional[GeoEntityType] = None
    subtypes: Optional[List[str]] = None
    active: Optional[bool] = None
    
    # Spatial queries
    near_lat: Optional[float] = None
    near_lng: Optional[float] = None
    max_distance: Optional[float] = Field(None, description="Max distance in meters")
    
    # Bounding box
    bbox_sw_lat: Optional[float] = None
    bbox_sw_lng: Optional[float] = None
    bbox_ne_lat: Optional[float] = None
    bbox_ne_lng: Optional[float] = None
    
    # Metadata filters
    habitat: Optional[HabitatType] = None
    min_density: Optional[float] = None
    min_altitude: Optional[float] = None
    max_altitude: Optional[float] = None
    
    # Pagination
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)
    
    # Sorting
    sort_by: Optional[str] = "created_at"
    sort_order: Literal["asc", "desc"] = "desc"


class GeoStatsResponse(BaseModel):
    """Statistics response for geo entities"""
    total_entities: int
    by_type: Dict[str, int]
    by_habitat: Dict[str, int]
    avg_density: Optional[float]
    hotspots_count: int
    corridors_count: int
    active_count: int
    auto_generated_count: int
