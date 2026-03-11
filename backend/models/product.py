# Product Models
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Literal
from datetime import datetime, timezone
import uuid


class Product(BaseModel):
    """Main product model for SCENT SCIENCE™ products"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    brand: str
    price: float
    score: int  # Score attractivité SCENT SCIENCE™
    cost_benefit_score: int = 0  # Score coût/bénéfice
    rank: int
    image_url: str
    description: Optional[str] = ""
    category: str = "attractant"
    animal_type: Optional[str] = ""
    season: Optional[str] = ""  # Saison recommandée
    
    # Format & Physical Properties
    product_format: str = "granules"  # gel, bloc, urine, granules, liquide, poudre
    weight: Optional[str] = ""  # Poids/Volume (ex: "500g", "1L")
    size: Optional[str] = ""  # Taille (ex: "petit", "moyen", "grand")
    
    # Pricing
    shipping_cost: float = 10.0  # Frais de transport
    price_per_unit: float = 0  # Prix par unité (g, ml, etc.)
    
    # Composition & Features
    has_pheromones: bool = False  # Contient des phéromones
    pheromone_type: Optional[str] = ""  # Type de phéromone
    scent_flavor: Optional[str] = ""  # Saveur/Odeur principale
    scent_notes: List[str] = []  # Notes olfactives
    ingredients_natural: bool = True  # Ingrédients naturels
    
    # Performance Characteristics
    attraction_days: int = 7  # Durée d'attraction en jours
    rainproof: bool = False
    feed_proof: bool = True
    certified_food: bool = False  # Certification alimentaire
    
    # Target Animals
    target_animals: List[str] = []  # Liste d'animaux ciblés
    
    # Hybrid System Fields
    sale_mode: Literal["dropshipping", "affiliation", "hybrid"] = "dropshipping"
    supplier_id: Optional[str] = None
    supplier_price: float = 0
    affiliate_commission: float = 0
    affiliate_link: Optional[str] = None
    dropshipping_available: bool = True
    
    # Performance tracking
    views: int = 0
    clicks: int = 0
    comparisons: int = 0
    orders: int = 0
    
    # Advantages for display
    advantages: List[str] = []
    buy_link: Optional[str] = None
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProductCreate(BaseModel):
    """Model for creating a new product"""
    name: str
    brand: str
    price: float
    score: int
    cost_benefit_score: int = 0
    rank: int
    image_url: str
    description: Optional[str] = ""
    category: str = "attractant"
    animal_type: Optional[str] = ""
    season: Optional[str] = ""
    product_format: str = "granules"
    weight: Optional[str] = ""
    size: Optional[str] = ""
    shipping_cost: float = 10.0
    price_per_unit: float = 0
    has_pheromones: bool = False
    pheromone_type: Optional[str] = ""
    scent_flavor: Optional[str] = ""
    scent_notes: List[str] = []
    ingredients_natural: bool = True
    attraction_days: int = 7
    rainproof: bool = False
    feed_proof: bool = True
    certified_food: bool = False
    target_animals: List[str] = []
    sale_mode: Literal["dropshipping", "affiliation", "hybrid"] = "dropshipping"
    supplier_id: Optional[str] = None
    supplier_price: float = 0
    affiliate_commission: float = 0
    affiliate_link: Optional[str] = None
    dropshipping_available: bool = True
    advantages: List[str] = []
    buy_link: Optional[str] = None


class ProductUpdate(BaseModel):
    """Model for updating an existing product"""
    name: Optional[str] = None
    brand: Optional[str] = None
    price: Optional[float] = None
    score: Optional[int] = None
    cost_benefit_score: Optional[int] = None
    rank: Optional[int] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    animal_type: Optional[str] = None
    season: Optional[str] = None
    product_format: Optional[str] = None
    weight: Optional[str] = None
    size: Optional[str] = None
    shipping_cost: Optional[float] = None
    price_per_unit: Optional[float] = None
    has_pheromones: Optional[bool] = None
    pheromone_type: Optional[str] = None
    scent_flavor: Optional[str] = None
    scent_notes: Optional[List[str]] = None
    ingredients_natural: Optional[bool] = None
    attraction_days: Optional[int] = None
    rainproof: Optional[bool] = None
    feed_proof: Optional[bool] = None
    certified_food: Optional[bool] = None
    target_animals: Optional[List[str]] = None
    sale_mode: Optional[Literal["dropshipping", "affiliation", "hybrid"]] = None
    supplier_id: Optional[str] = None
    supplier_price: Optional[float] = None
    affiliate_commission: Optional[float] = None
    affiliate_link: Optional[str] = None
    dropshipping_available: Optional[bool] = None
    advantages: Optional[List[str]] = None
    buy_link: Optional[str] = None


class ProductFilter(BaseModel):
    """Filter parameters for product search"""
    search: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    animal_type: Optional[str] = None
    product_format: Optional[str] = None
    season: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_score: Optional[int] = None
    max_score: Optional[int] = None
    rainproof: Optional[bool] = None
    has_pheromones: Optional[bool] = None
    certified_food: Optional[bool] = None
    sale_mode: Optional[str] = None
    sort_by: str = "rank"  # rank, price, score, name
    sort_order: str = "asc"  # asc, desc
    limit: int = 50
    offset: int = 0
