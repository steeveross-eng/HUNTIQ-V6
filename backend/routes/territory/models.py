"""
Territory Module - Pydantic Models
Phase 1.8 - Split from territory.py
"""
from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    email: str
    password: str
    name: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str]
    plan_type: str
    created_at: datetime

class UserLogin(BaseModel):
    email: str
    password: str

class CameraCreate(BaseModel):
    label: str
    brand: Literal['GardePro', 'WingHome', 'SOVACAM', 'Reconyx', 'Bushnell', 'Browning', 'autre']
    connection_type: Literal['ftp', 'email', 'manual']
    ftp_host: Optional[str] = None
    ftp_username: Optional[str] = None
    ftp_password: Optional[str] = None
    ftp_path: Optional[str] = None
    email_address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class CameraResponse(BaseModel):
    id: str
    label: str
    brand: str
    connection_type: str
    connected: bool
    last_seen_at: Optional[datetime]
    latitude: Optional[float]
    longitude: Optional[float]

class EventCreate(BaseModel):
    event_type: Literal['gps_track', 'cache', 'camera_photo', 'tir', 'observation', 'saline', 'feeding_station']
    latitude: float
    longitude: float
    species: Optional[Literal['orignal', 'chevreuil', 'ours', 'autre']] = None
    species_confidence: Optional[float] = None
    count_estimate: Optional[int] = 1
    captured_at: Optional[datetime] = None
    source: Literal['app', 'camera', 'import', 'manual'] = 'app'
    metadata: Optional[dict] = {}

class EventResponse(BaseModel):
    id: str
    event_type: str
    species: Optional[str]
    species_confidence: Optional[float]
    count_estimate: int
    latitude: float
    longitude: float
    captured_at: datetime
    source: str
    metadata: dict

class PhotoUploadResponse(BaseModel):
    id: str
    photo_url: str
    processing_status: str
    exif_datetime: Optional[datetime]
    exif_gps_lat: Optional[float]
    exif_gps_lon: Optional[float]
    species: Optional[str]
    species_confidence: Optional[float]
    count_estimate: Optional[int]

class AIClassificationResult(BaseModel):
    species: Literal['orignal', 'chevreuil', 'ours', 'autre']
    confidence: float
    count_estimate: int
    reasoning: str

class WaypointCreate(BaseModel):
    latitude: float
    longitude: float
    name: str
    description: Optional[str] = None
    waypoint_type: Literal['observation', 'camera', 'cache', 'stand', 'water', 'trail_start', 'custom', 'hunting', 'feeder', 'sighting', 'parking'] = 'custom'
    icon: Optional[str] = None
    active: Optional[bool] = True
    color: Optional[str] = None
    notes: Optional[str] = None

class WaypointResponse(BaseModel):
    id: str
    latitude: float
    longitude: float
    name: str
    description: Optional[str]
    waypoint_type: str
    icon: Optional[str]
    created_at: datetime
    active: Optional[bool] = True
    color: Optional[str] = None
    notes: Optional[str] = None
    user_id: Optional[str] = None

class TrackPointCreate(BaseModel):
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    accuracy: Optional[float] = None
    speed: Optional[float] = None
    heading: Optional[float] = None

class TrackCreate(BaseModel):
    name: str
    description: Optional[str] = None

class TrackResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    points_count: int
    distance_km: float
    duration_minutes: float
    started_at: datetime
    ended_at: Optional[datetime]
    is_active: bool

class ProbabilityRequest(BaseModel):
    latitude: float
    longitude: float
    species: Literal['orignal', 'chevreuil', 'ours']
    forest_type: Optional[str] = None
    water_distance_m: Optional[float] = None
    altitude_m: Optional[float] = None
    slope_direction: Optional[str] = None
    road_distance_m: Optional[float] = None
    is_transition_zone: Optional[bool] = None
    is_coulee: Optional[bool] = None

class ProbabilityResponse(BaseModel):
    latitude: float
    longitude: float
    species: str
    probability_score: float
    confidence: str
    factors: dict
    recommendations: List[str]
    refuge_zones: List[dict]
    cooling_zones: List[dict]

class GuidedRouteRequest(BaseModel):
    species: Literal['orignal', 'chevreuil', 'ours']
    optimize_for: Literal['probability', 'distance', 'balanced'] = 'balanced'
    start_from_current_position: bool = False
    current_lat: Optional[float] = None
    current_lng: Optional[float] = None

class RouteSegment(BaseModel):
    from_waypoint: dict
    to_waypoint: dict
    distance_km: float
    probability_score: float
    probability_level: str
    color: str
    recommendations: List[str]

class GuidedRouteResponse(BaseModel):
    route_id: str
    species: str
    total_distance_km: float
    estimated_time_hours: float
    average_probability: float
    highest_probability_zone: dict
    segments: List[RouteSegment]
    waypoint_order: List[dict]
    summary: str

class NutritionAnalysisRequest(BaseModel):
    latitude: float
    longitude: float
    species: Literal['orignal', 'chevreuil', 'ours']
    forest_type: Optional[Literal['mixte', 'feuillus', 'coniferes', 'regeneration']] = 'mixte'
    season: Optional[Literal['printemps', 'ete', 'automne', 'hiver']] = None
    water_nearby: bool = True
    altitude_m: Optional[float] = None

class OrderItem(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    price: float

class OrderCreate(BaseModel):
    customer_name: str
    customer_email: str
    customer_phone: Optional[str] = None
    notes: Optional[str] = None
    items: List[OrderItem]
    total: float
    source: str = "territory_bionic"
    user_id: Optional[str] = None

class OrderResponse(BaseModel):
    id: str
    customer_name: str
    customer_email: str
    items: List[dict]
    total: float
    status: str
    created_at: datetime

class PromptDocumentation(BaseModel):
    app_name: str
    version: str
    description: str
    modules: List[dict]
    api_endpoints: dict
    bionic_products: List[dict]
    species_rules: dict
    integrations: List[str]
    tech_stack: dict
