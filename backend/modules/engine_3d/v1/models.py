"""Engine 3D Models - PLAN MAITRE
Pydantic models for 3D terrain visualization and analysis.

Version: 1.0.0
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime, timezone
import uuid


class ElevationPoint(BaseModel):
    """Single elevation point"""
    lat: float
    lng: float
    elevation: float  # meters
    source: str = "DEM"


class ElevationProfile(BaseModel):
    """Elevation profile along a path"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Path
    start_point: Dict[str, float]
    end_point: Dict[str, float]
    distance_km: float = 0
    
    # Elevation data
    points: List[ElevationPoint] = Field(default_factory=list)
    min_elevation: float = 0
    max_elevation: float = 0
    elevation_gain: float = 0
    elevation_loss: float = 0
    average_slope: float = 0  # percentage
    
    # Analysis
    steep_sections: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Metadata
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ViewshedAnalysis(BaseModel):
    """Line-of-sight / viewshed analysis"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Observer position
    observer_point: Dict[str, float]
    observer_height: float = 1.7  # meters
    
    # Analysis parameters
    radius_km: float = 2.0
    resolution_m: float = 30.0
    
    # Results
    visible_area_km2: float = 0
    visible_percentage: float = 0
    viewshed_polygon: Optional[List[Dict[str, float]]] = None
    
    # Blind spots
    blind_zones: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Metadata
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TerrainAnalysis(BaseModel):
    """Comprehensive terrain analysis"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Area
    center: Dict[str, float]
    radius_km: float
    
    # Terrain characteristics
    min_elevation: float = 0
    max_elevation: float = 0
    mean_elevation: float = 0
    relief: float = 0  # max - min
    
    # Slope analysis
    average_slope: float = 0
    max_slope: float = 0
    flat_area_percentage: float = 0
    steep_area_percentage: float = 0
    
    # Aspect (direction slopes face)
    dominant_aspect: Literal["N", "NE", "E", "SE", "S", "SW", "W", "NW"] = "N"
    aspect_distribution: Dict[str, float] = Field(default_factory=dict)
    
    # Hunting relevance
    thermal_zones: List[Dict[str, Any]] = Field(default_factory=list)
    funnel_points: List[Dict[str, Any]] = Field(default_factory=list)
    saddles: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Metadata
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Terrain3DExport(BaseModel):
    """3D terrain export data"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Bounds
    bounds: Dict[str, float]  # north, south, east, west
    
    # Data
    format: Literal["glb", "obj", "stl", "geotiff"] = "glb"
    resolution_m: float = 30.0
    vertex_count: int = 0
    
    # File
    file_url: Optional[str] = None
    file_size_mb: float = 0
    
    # Metadata
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
