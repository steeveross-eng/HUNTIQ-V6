"""
BIONIC™ Real Estate Module - Models
====================================
Phase 11-15: Module Immobilier

Modèles de données pour la gestion des propriétés immobilières
et le scoring géospatial.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class PropertySource(str, Enum):
    """Source d'une propriété"""
    centris = "centris"
    duproprio = "duproprio"
    kijiji = "kijiji"
    manual = "manual"
    api_b2b = "api_b2b"


class PropertyType(str, Enum):
    """Type de propriété"""
    terrain = "terrain"
    chalet = "chalet"
    ferme = "ferme"
    pourvoirie = "pourvoirie"
    zec = "zec"
    domaine = "domaine"
    lot_boise = "lot_boise"


class PropertyStatus(str, Enum):
    """Statut d'une propriété"""
    available = "available"
    pending = "pending"
    sold = "sold"
    expired = "expired"


class GeoCoordinates(BaseModel):
    """Coordonnées géographiques"""
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)


class PropertyBase(BaseModel):
    """Modèle de base pour une propriété"""
    title: str
    description: Optional[str] = None
    price: float
    area_m2: float
    coordinates: GeoCoordinates
    property_type: PropertyType = PropertyType.terrain
    source: PropertySource = PropertySource.manual
    source_url: Optional[str] = None
    source_id: Optional[str] = None
    images: List[str] = []
    features: Dict[str, Any] = {}


class PropertyCreate(PropertyBase):
    """Modèle pour créer une propriété"""
    pass


class PropertyInDB(PropertyBase):
    """Modèle d'une propriété en base de données"""
    id: str = Field(alias="_id")
    status: PropertyStatus = PropertyStatus.available
    bionic_score: Optional[float] = None
    hunting_potential: Optional[Dict[str, float]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True


class PropertyResponse(PropertyBase):
    """Modèle de réponse pour une propriété"""
    id: str
    status: PropertyStatus
    bionic_score: Optional[float] = None
    hunting_potential: Optional[Dict[str, float]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class PropertyListResponse(BaseModel):
    """Réponse liste de propriétés"""
    success: bool = True
    total: int
    properties: List[PropertyResponse]


class PropertyScoreBreakdown(BaseModel):
    """Détail du scoring BIONIC pour une propriété"""
    habitat_score: float = 0
    water_score: float = 0
    terrain_score: float = 0
    access_score: float = 0
    biodiversity_score: float = 0
    species_potential: Dict[str, float] = {}
    overall_score: float = 0
    rating: str = "Non évalué"


class OpportunityLevel(str, Enum):
    """Niveau d'opportunité"""
    excellent = "excellent"
    very_good = "very_good"
    good = "good"
    average = "average"
    below_average = "below_average"


class PropertyOpportunity(BaseModel):
    """Opportunité d'investissement"""
    property_id: str
    property_title: str
    opportunity_level: OpportunityLevel
    price_per_m2: float
    market_average_per_m2: float
    bionic_score: float
    discount_percentage: float
    investment_potential: str
    recommended_actions: List[str] = []


class OpportunityListResponse(BaseModel):
    """Réponse liste d'opportunités"""
    success: bool = True
    total: int
    opportunities: List[PropertyOpportunity]


# B2B API Models

class B2BHotspotRequest(BaseModel):
    """Requête pour hotspots B2B"""
    lat: float
    lng: float
    radius_km: float = 10
    species: Optional[List[str]] = None
    min_score: float = 0


class B2BScoreRequest(BaseModel):
    """Requête pour score B2B"""
    coordinates: List[GeoCoordinates]
    species: Optional[str] = None


class B2BPropertyRequest(BaseModel):
    """Requête pour propriétés B2B"""
    bbox: Optional[Dict[str, float]] = None
    property_type: Optional[PropertyType] = None
    min_area: Optional[float] = None
    max_price: Optional[float] = None
    min_bionic_score: Optional[float] = None


class B2BHeatmapRequest(BaseModel):
    """Requête pour heatmap B2B"""
    bbox: Dict[str, float]
    resolution: int = 100
    species: Optional[str] = None
    layer_type: str = "habitat"
