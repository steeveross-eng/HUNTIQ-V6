# Territory Analysis Models
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime, timezone
import uuid


class Camera(BaseModel):
    """Camera model for trail cameras"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    label: str
    brand: Literal["GardePro", "WingHome", "SOVACAM", "Reconyx", "Bushnell", "Moultrie", "autre"] = "autre"
    connection_type: Literal["ftp", "email", "manual"] = "manual"
    ftp_host: Optional[str] = None
    ftp_username: Optional[str] = None
    ftp_password: Optional[str] = None
    ftp_path: Optional[str] = None
    email_address: Optional[str] = None
    location: Optional[Dict[str, float]] = None  # {lat, lng}
    connected: bool = False
    last_seen_at: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CameraPhoto(BaseModel):
    """Photo captured by a trail camera"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    camera_id: str
    user_id: str
    event_id: Optional[str] = None
    photo_path: str
    photo_url: Optional[str] = None
    species: Optional[Literal["orignal", "chevreuil", "ours", "autre", "aucun"]] = None
    species_confidence: float = 0.0
    count_estimate: int = 0
    location: Optional[Dict[str, float]] = None  # {lat, lng}
    captured_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    processed: bool = False
    metadata: Dict[str, Any] = {}


class TerritoryEvent(BaseModel):
    """Event on territory (observation, shot, cache, etc.)"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    event_type: Literal["gps_track", "cache", "camera", "tir", "observation", "camera_photo", "saline", "attractant"]
    species: Optional[Literal["orignal", "chevreuil", "ours", "autre"]] = None
    species_confidence: float = 0.0
    location: Dict[str, float]  # {lat, lng}
    captured_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source: Literal["app", "camera", "import", "manual"] = "manual"
    metadata: Dict[str, Any] = {}
    notes: Optional[str] = None


class TerritoryZone(BaseModel):
    """Analysis zone on territory"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    zone_type: Literal["hunting_zone", "refuge", "corridor", "feeding", "water"]
    species: Optional[str] = None
    bounds: List[Dict[str, float]]  # Polygon coordinates [{lat, lng}, ...]
    probability: float = 0.0
    refuge_score: float = 0.0
    intensity: float = 0.0
    recommendations: List[str] = []
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class HeatmapLayer(BaseModel):
    """Heatmap layer for activity visualization"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    species: Optional[str] = None
    layer_type: Literal["activity", "probability", "pressure", "refuge"]
    points: List[Dict[str, Any]]  # [{lat, lng, intensity}, ...]
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ActionPlan(BaseModel):
    """Generated action plan for hunting"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    species_target: Literal["orignal", "chevreuil", "ours"]
    zone_center: Dict[str, float]  # {lat, lng}
    zone_radius_km: float = 5.0
    time_period: Literal["matin", "jour", "soir", "nuit", "tous"]
    recommendations: List[Dict[str, Any]] = []
    camera_placements: List[Dict[str, Any]] = []
    attractant_placements: List[Dict[str, Any]] = []
    cache_recommendations: List[Dict[str, Any]] = []
    probability_map: Optional[Dict[str, Any]] = None
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    pdf_url: Optional[str] = None


class SpeciesRules(BaseModel):
    """Business rules for species probability calculation"""
    species: Literal["orignal", "chevreuil", "ours"]
    
    # Distance preferences (meters)
    water_distance_optimal: float = 300  # Distance optimale à l'eau
    road_distance_min: float = 400  # Distance min aux chemins
    edge_distance_optimal: float = 150  # Distance optimale aux lisières
    
    # Terrain preferences
    preferred_terrain: List[str] = []  # Types de terrain préférés
    preferred_cover: List[str] = []  # Types de couvert préférés
    slope_max: float = 15  # Pente maximale en %
    
    # Activity patterns
    activity_hours: Dict[str, float] = {}  # Probabilité par période
    recent_activity_window_hours: int = 72  # Fenêtre d'activité récente
    
    # Pressure response
    pressure_sensitivity: float = 0.5  # Sensibilité à la pression (0-1)
