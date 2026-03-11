"""Advanced Geospatial Engine Models - PLAN MAITRE
Pydantic models for advanced geospatial analysis.

Version: 1.0.0
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime, timezone
from enum import Enum
import uuid


class CorridorType(str, Enum):
    """Types of movement corridors"""
    TRAVEL = "travel"
    MIGRATION = "migration"
    DAILY = "daily"
    SEASONAL = "seasonal"


class ConcentrationZone(BaseModel):
    """Wildlife concentration zone"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Location
    center: Dict[str, float]
    radius_m: float = 500
    boundary: Optional[List[Dict[str, float]]] = None
    
    # Classification
    zone_type: Literal["feeding", "bedding", "watering", "staging", "crossing"] = "feeding"
    species: List[str] = Field(default_factory=list)
    
    # Scoring
    concentration_score: float = Field(ge=0, le=100, default=50)
    confidence: float = Field(ge=0, le=1, default=0.7)
    
    # Timing
    peak_activity_times: List[str] = Field(default_factory=list)
    seasonal_variation: Optional[str] = None
    
    # Data sources
    data_sources: List[str] = Field(default_factory=list)
    observation_count: int = 0
    
    # Metadata
    identified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MovementCorridor(BaseModel):
    """Wildlife movement corridor"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Path
    path: List[Dict[str, float]] = Field(default_factory=list)
    width_m: float = 100
    length_km: float = 0
    
    # Classification
    corridor_type: Literal["travel", "migration", "daily", "seasonal"] = "travel"
    species: List[str] = Field(default_factory=list)
    
    # Characteristics
    terrain_type: List[str] = Field(default_factory=list)
    vegetation_cover: float = 0  # percentage
    elevation_change: float = 0  # meters
    
    # Usage
    usage_frequency: Literal["high", "medium", "low"] = "medium"
    peak_usage_times: List[str] = Field(default_factory=list)
    
    # Scoring
    importance_score: float = Field(ge=0, le=100, default=50)
    hunting_potential: float = Field(ge=0, le=100, default=50)
    
    # Funnel points along corridor
    funnel_points: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Metadata
    identified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class HabitatConnectivity(BaseModel):
    """Habitat connectivity analysis"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Analysis area
    center: Dict[str, float]
    radius_km: float = 5.0
    
    # Connectivity metrics
    overall_connectivity: float = Field(ge=0, le=100, default=50)
    fragmentation_index: float = Field(ge=0, le=1, default=0.5)
    
    # Habitat patches
    patch_count: int = 0
    average_patch_size_ha: float = 0
    largest_patch_ha: float = 0
    
    # Barriers
    barriers: List[Dict[str, Any]] = Field(default_factory=list)
    # roads, rivers, development, etc.
    
    # Corridors
    corridors_identified: int = 0
    primary_corridors: List[str] = Field(default_factory=list)  # corridor IDs
    
    # Recommendations
    connectivity_gaps: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Metadata
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class HeatmapData(BaseModel):
    """Wildlife activity heatmap"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Bounds
    bounds: Dict[str, float]  # north, south, east, west
    resolution_m: float = 100
    
    # Data
    species: Optional[str] = None
    data_type: Literal["activity", "sightings", "harvest", "signs"] = "activity"
    time_period: Optional[str] = None  # "last_30_days", "season", etc.
    
    # Grid data
    grid: List[List[float]] = Field(default_factory=list)
    # 2D array of intensity values 0-1
    
    # Stats
    total_points: int = 0
    max_intensity: float = 0
    hotspot_count: int = 0
    
    # Hotspots
    hotspots: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Metadata
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DispersionModel(BaseModel):
    """Wildlife dispersion modeling"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Source
    source_point: Dict[str, float]
    species: str
    
    # Parameters
    time_hours: float = 24
    terrain_influence: bool = True
    
    # Results
    probable_area_km2: float = 0
    dispersion_polygon: Optional[List[Dict[str, float]]] = None
    
    # Probability zones
    high_probability_area: Optional[List[Dict[str, float]]] = None  # >70%
    medium_probability_area: Optional[List[Dict[str, float]]] = None  # 40-70%
    low_probability_area: Optional[List[Dict[str, float]]] = None  # <40%
    
    # Influencing factors
    terrain_barriers: List[Dict[str, Any]] = Field(default_factory=list)
    attractors: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Metadata
    modeled_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
