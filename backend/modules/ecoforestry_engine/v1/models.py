"""Ecoforestry Engine Models - PLAN MAITRE
Pydantic models for ecoforestry data and habitat analysis.

Version: 1.0.0
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Literal
from datetime import datetime, timezone
from enum import Enum
import uuid


class ForestStandType(str, Enum):
    """Types of forest stands"""
    CONIFEROUS = "coniferous"
    DECIDUOUS = "deciduous"
    MIXED = "mixed"
    REGENERATION = "regeneration"
    PLANTATION = "plantation"


class HabitatQuality(str, Enum):
    """Habitat quality ratings"""
    EXCELLENT = "excellent"
    GOOD = "good"
    MODERATE = "moderate"
    POOR = "poor"
    UNSUITABLE = "unsuitable"


class ForestStand(BaseModel):
    """Forest stand information from SIEF data"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Location
    coordinates: Dict[str, float]  # centroid lat, lng
    boundary: Optional[List[Dict[str, float]]] = None  # polygon
    area_hectares: float = 0
    
    # Composition
    stand_type: ForestStandType = ForestStandType.MIXED
    dominant_species: List[str] = Field(default_factory=list)
    secondary_species: List[str] = Field(default_factory=list)
    
    # Characteristics
    age_years: Optional[int] = None
    density_class: Literal["A", "B", "C", "D"] = "B"
    height_class: Optional[int] = None  # meters
    crown_closure: Optional[float] = None  # percentage
    
    # Disturbances
    last_cut_year: Optional[int] = None
    cut_type: Optional[str] = None
    fire_history: Optional[List[int]] = None
    disease_presence: bool = False
    
    # Metadata
    data_source: str = "SIEF"
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class HabitatAnalysis(BaseModel):
    """Habitat suitability analysis for a species"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Target
    species: str
    coordinates: Dict[str, float]
    analysis_radius_km: float = 5.0
    
    # Results
    overall_quality: HabitatQuality = HabitatQuality.MODERATE
    quality_score: float = Field(ge=0, le=100, default=50)
    
    # Factors
    food_availability: float = Field(ge=0, le=100, default=50)
    cover_quality: float = Field(ge=0, le=100, default=50)
    water_proximity: float = Field(ge=0, le=100, default=50)
    disturbance_level: float = Field(ge=0, le=100, default=50)
    connectivity: float = Field(ge=0, le=100, default=50)
    
    # Details
    favorable_stands: List[str] = Field(default_factory=list)
    limiting_factors: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    
    # Metadata
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RecentCut(BaseModel):
    """Recent forest cut information"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Location
    coordinates: Dict[str, float]
    boundary: Optional[List[Dict[str, float]]] = None
    area_hectares: float = 0
    
    # Cut details
    cut_year: int
    cut_type: Literal["clearcut", "selective", "salvage", "thinning"] = "selective"
    remaining_coverage: float = 0  # percentage
    
    # Regeneration
    regeneration_status: Literal["none", "early", "established", "mature"] = "early"
    planted_species: List[str] = Field(default_factory=list)
    natural_regeneration: List[str] = Field(default_factory=list)
    
    # Wildlife impact
    deer_attraction_score: float = Field(ge=0, le=100, default=70)
    browse_availability: str = "moderate"


class EcoforestryRequest(BaseModel):
    """Request for ecoforestry analysis"""
    lat: float
    lng: float
    radius_km: float = Field(default=5.0, ge=0.5, le=50)
    species: Optional[str] = None
    include_cuts: bool = True
    include_habitats: bool = True


class EcoforestryResponse(BaseModel):
    """Response for ecoforestry analysis"""
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    center: Dict[str, float]
    radius_km: float
    
    # Results
    total_stands: int = 0
    stands: List[ForestStand] = Field(default_factory=list)
    recent_cuts: List[RecentCut] = Field(default_factory=list)
    habitat_analysis: Optional[HabitatAnalysis] = None
    
    # Summary
    dominant_forest_type: Optional[ForestStandType] = None
    average_stand_age: Optional[float] = None
    total_cut_area_ha: float = 0
    
    # Metadata
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
