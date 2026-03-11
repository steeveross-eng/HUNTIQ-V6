"""Geospatial Engine Models - CORE

Pydantic models for geospatial hunting analysis.

Version: 1.0.0
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime, timezone


class Coordinates(BaseModel):
    """Geographic coordinates"""
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    altitude: Optional[float] = None


class HuntingZone(BaseModel):
    """Hunting zone definition"""
    id: str
    name: str
    zone_type: Literal["zec", "pourvoirie", "public", "reserve", "private"]
    region: str
    area_km2: float
    coordinates: List[Coordinates] = Field(default_factory=list)
    species: List[str] = Field(default_factory=list)
    regulations: Dict[str, Any] = Field(default_factory=dict)


class TerrainAnalysis(BaseModel):
    """Terrain analysis result"""
    elevation: float
    slope: float
    aspect: str  # N, S, E, W
    vegetation_type: str
    water_proximity: float  # meters
    road_proximity: float  # meters
    hunting_score: float = Field(ge=0, le=10)


class POI(BaseModel):
    """Point of Interest"""
    id: str
    name: str
    poi_type: Literal["stand", "feeder", "water", "trail", "crossing", "bedding"]
    coordinates: Coordinates
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RouteRequest(BaseModel):
    """Request for route calculation"""
    start: Coordinates
    end: Coordinates
    avoid_roads: bool = False
    prefer_cover: bool = True
