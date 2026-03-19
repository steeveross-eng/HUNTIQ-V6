from fastapi import FastAPI, APIRouter, HTTPException, Depends, BackgroundTasks
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import asyncio
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Literal, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import hashlib
import resend

# Import analyzer module
from analyzer import (
    ProductAnalyzer, AnalysisRequest, AnalysisReport, EmailConsent,
    BIONIC_PRODUCTS, COMPETITOR_PRODUCTS, INGREDIENTS_DATABASE, SCORING_CRITERIA,
    SCIENTIFIC_REFERENCES, get_scientific_references
)

# Import email service
from email_service import send_cancellation_email, send_analysis_report_email, is_email_configured

# Import product discovery service
from product_discovery import (
    ProductDiscoveryService, DiscoveredProduct, ScannerConfig, AdminNotification,
    PRIORITY_SOURCES, SEARCH_KEYWORDS, normalize_price, normalize_weight
)

# Import referral system
from referral_system import (
    ReferralService, ReferralUser, ReferralInvite, ReferralClick,
    DiscountTierConfig, SeasonalPromotion, ProductDiscount, PartnerApplication,
    ReferralTier, SeasonType, SOCIAL_PLATFORMS, MESSAGE_TEMPLATES, DEFAULT_DISCOUNT_TIERS
)

# ============================================
# MODULAR ENGINE IMPORTS (Phase 2)
# ============================================
from modules.routers import register_routers, get_router_info, MODULE_STATUS

# ============================================
# DEFAULT ANALYSIS CATEGORIES STRUCTURE
# ============================================

DEFAULT_ANALYSIS_CATEGORIES = [
    {
        "id": "attractants",
        "name": "Attractants",
        "icon": "🎯",
        "order": 1,
        "subcategories": [
            {"id": "liquides", "name": "Liquides", "icon": "💧"},
            {"id": "gels", "name": "Gels", "icon": "🧴"},
            {"id": "poudres", "name": "Poudres", "icon": "✨"},
            {"id": "granules", "name": "Granulés", "icon": "🌾"},
            {"id": "blocs", "name": "Blocs", "icon": "🧱"},
            {"id": "atomiseurs", "name": "Atomiseurs / aérosols", "icon": "💨"},
            {"id": "capsules", "name": "Capsules / systèmes contrôlés", "icon": "💊"},
            {"id": "melanges", "name": "Mélanges multi-espèces", "icon": "🔀"}
        ]
    },
    {
        "id": "armes",
        "name": "Armes",
        "icon": "🎯",
        "order": 2,
        "subcategories": [
            {"id": "carabines", "name": "Carabines", "icon": "🔫"},
            {"id": "arcs", "name": "Arcs", "icon": "🏹"},
            {"id": "arbaletes", "name": "Arbalètes", "icon": "⚔️"},
            {"id": "munitions", "name": "Munitions", "icon": "🎯"},
            {"id": "optiques", "name": "Optiques (lunettes, red dots)", "icon": "🔭"},
            {"id": "silencieux", "name": "Silencieux / modérateurs", "icon": "🔇"}
        ]
    },
    {
        "id": "cameras",
        "name": "Caméras",
        "icon": "📷",
        "order": 3,
        "subcategories": [
            {"id": "cameras_trail", "name": "Caméras de trail", "icon": "📹"},
            {"id": "cameras_cellulaires", "name": "Caméras cellulaires", "icon": "📱"},
            {"id": "cameras_solaires", "name": "Caméras solaires", "icon": "☀️"},
            {"id": "accessoires_cameras", "name": "Accessoires caméras", "icon": "🔧"}
        ]
    },
    {
        "id": "urines",
        "name": "Urines",
        "icon": "💧",
        "order": 4,
        "subcategories": [
            {"id": "urine_cerf", "name": "Urine de cerf", "icon": "🦌"},
            {"id": "urine_orignal", "name": "Urine d'orignal", "icon": "🫎"},
            {"id": "urine_ours", "name": "Urine d'ours", "icon": "🐻"},
            {"id": "urines_synthetiques", "name": "Urines synthétiques", "icon": "🧪"},
            {"id": "urines_femelles", "name": "Urines femelles en rut", "icon": "💕"}
        ]
    },
    {
        "id": "appats",
        "name": "Appâts / Nourriture",
        "icon": "🍎",
        "order": 5,
        "subcategories": [
            {"id": "mais", "name": "Maïs et céréales", "icon": "🌽"},
            {"id": "pommes", "name": "Pommes et fruits", "icon": "🍎"},
            {"id": "mineraux", "name": "Blocs minéraux", "icon": "💎"},
            {"id": "proteines", "name": "Suppléments protéinés", "icon": "💪"},
            {"id": "melanges_appats", "name": "Mélanges spéciaux", "icon": "🥣"}
        ]
    },
    {
        "id": "leurres",
        "name": "Leurres synthétiques",
        "icon": "🎭",
        "order": 6,
        "subcategories": [
            {"id": "leurres_visuels", "name": "Leurres visuels (decoys)", "icon": "👁️"},
            {"id": "leurres_sonores", "name": "Leurres sonores (calls)", "icon": "📢"},
            {"id": "leurres_olfactifs", "name": "Leurres olfactifs", "icon": "👃"},
            {"id": "leurres_combo", "name": "Combinés multi-sens", "icon": "🎯"}
        ]
    },
    {
        "id": "accessoires",
        "name": "Accessoires de chasse",
        "icon": "🎒",
        "order": 7,
        "subcategories": [
            {"id": "treestands", "name": "Treestands / miradors", "icon": "🌲"},
            {"id": "blinds", "name": "Blinds / affûts", "icon": "🏕️"},
            {"id": "couteaux", "name": "Couteaux et outils", "icon": "🔪"},
            {"id": "sacs", "name": "Sacs et rangement", "icon": "🎒"},
            {"id": "lampes", "name": "Lampes et éclairage", "icon": "🔦"}
        ]
    },
    {
        "id": "vetements",
        "name": "Vêtements / Contrôle d'odeur",
        "icon": "👕",
        "order": 8,
        "subcategories": [
            {"id": "vetements_camo", "name": "Vêtements camouflage", "icon": "🌿"},
            {"id": "bottes", "name": "Bottes et chaussures", "icon": "🥾"},
            {"id": "gants", "name": "Gants et accessoires", "icon": "🧤"},
            {"id": "eliminateurs_odeur", "name": "Éliminateurs d'odeur", "icon": "🚫"},
            {"id": "sprays_neutralisants", "name": "Sprays neutralisants", "icon": "💨"}
        ]
    },
    {
        "id": "habitat",
        "name": "Habitat / Gestion du territoire",
        "icon": "🏞️",
        "order": 9,
        "subcategories": [
            {"id": "food_plots", "name": "Food plots / plantations", "icon": "🌱"},
            {"id": "semences", "name": "Semences attractives", "icon": "🌾"},
            {"id": "engrais", "name": "Engrais et amendements", "icon": "🧪"},
            {"id": "clotures", "name": "Clôtures et protection", "icon": "🚧"}
        ]
    },
    {
        "id": "animaux",
        "name": "Produits pour animaux",
        "icon": "🐕",
        "order": 10,
        "subcategories": [
            {"id": "sante_animaux", "name": "Santé animale", "icon": "💊"},
            {"id": "nutrition_animaux", "name": "Nutrition animale", "icon": "🥣"},
            {"id": "equipement_chiens", "name": "Équipement pour chiens", "icon": "🐕"},
            {"id": "tracking", "name": "Tracking et GPS", "icon": "📍"}
        ]
    }
]

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Admin password hash (Saturn5858*)
ADMIN_PASSWORD_HASH = hashlib.sha256("Saturn5858*".encode()).hexdigest()

# Emergent LLM Key
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')

# Resend Email Configuration
RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'onboarding@resend.dev')
if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY

# Create the main app with OpenAPI documentation
app = FastAPI(
    title="BIONIC HUNT/Chasse V3 - API Modulaire",
    description="""
# BIONIC HUNT/Chasse V3 - Plateforme de Chasse Intelligente

API complète pour la gestion et l'analyse des territoires de chasse au Québec.

## Architecture Modulaire (v1)
- 7 moteurs CORE indépendants et versionnés
- Endpoints sous `/api/v1/{module}/`
- Documentation Swagger/OpenAPI intégrée

## Modules disponibles
| Module | Préfixe | Description |
|--------|---------|-------------|
| Nutrition | `/api/v1/nutrition` | Analyse des ingrédients |
| Scoring | `/api/v1/scoring` | Évaluation scientifique |
| AI | `/api/v1/ai` | Analyse GPT-5.2 |
| Weather | `/api/v1/weather` | Conditions météo |
| Geospatial | `/api/v1/geospatial` | Gestion territoires |
| WMS | `/api/v1/wms` | Couches cartographiques |
| Strategy | `/api/v1/strategy` | Stratégies de chasse |
    """,
    version="3.2.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    openapi_tags=[
        {"name": "Root", "description": "Endpoints racine"},
        {"name": "Modules Status", "description": "État des modules modulaires"},
        {"name": "Nutrition Engine", "description": "Analyse nutritionnelle des attractants"},
        {"name": "Scoring Engine", "description": "Scoring scientifique (13 critères)"},
        {"name": "AI Engine", "description": "Analyse IA GPT-5.2"},
        {"name": "Weather Engine", "description": "Conditions météo de chasse"},
        {"name": "Geospatial Engine", "description": "Gestion des territoires"},
        {"name": "WMS Engine", "description": "Couches cartographiques WMS"},
        {"name": "Strategy Engine", "description": "Stratégies de chasse"},
        {"name": "Products", "description": "Gestion des produits"},
        {"name": "Orders", "description": "Gestion des commandes"},
        {"name": "Admin", "description": "Administration"},
    ]
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# ============================================
# MODELS - Products with Hybrid System
# ============================================

class Product(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    brand: str
    price: float
    score: int  # Score attractivité Chasse Bionic™
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
    
    # Analysis Categorization
    analysis_category: Optional[str] = None
    analysis_subcategory: Optional[str] = None
    
    # Performance tracking
    views: int = 0
    clicks: int = 0
    comparisons: int = 0
    orders: int = 0
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProductCreate(BaseModel):
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
    analysis_category: Optional[str] = None
    analysis_subcategory: Optional[str] = None

class ProductUpdate(BaseModel):
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
    analysis_category: Optional[str] = None
    analysis_subcategory: Optional[str] = None

# ============================================
# MODELS - Suppliers (Fournisseurs/Magasins)
# ============================================

class Supplier(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    contact_name: Optional[str] = ""
    email: Optional[str] = ""
    phone: Optional[str] = ""
    address: Optional[str] = ""
    partnership_type: Literal["dropshipping", "affiliation", "hybrid"] = "dropshipping"
    shipping_delay: int = 3  # Délai d'expédition en jours
    partnership_conditions: Optional[str] = ""
    is_active: bool = True
    
    # Statistics
    total_orders: int = 0
    total_revenue_supplier: float = 0  # Revenus générés pour le fournisseur
    total_revenue_scent: float = 0  # Revenus générés pour Chasse Bionic™
    confirmation_rate: float = 100  # Taux de confirmation (%)
    avg_shipping_days: float = 0
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SupplierCreate(BaseModel):
    name: str
    contact_name: Optional[str] = ""
    email: Optional[str] = ""
    phone: Optional[str] = ""
    address: Optional[str] = ""
    partnership_type: Literal["dropshipping", "affiliation", "hybrid"] = "dropshipping"
    shipping_delay: int = 3
    partnership_conditions: Optional[str] = ""

class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    partnership_type: Optional[Literal["dropshipping", "affiliation", "hybrid"]] = None
    shipping_delay: Optional[int] = None
    partnership_conditions: Optional[str] = None
    is_active: Optional[bool] = None

# ============================================
# MODELS - Customers (Clients)
# ============================================

class Customer(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    name: Optional[str] = ""
    email: Optional[str] = ""
    phone: Optional[str] = ""
    address: Optional[str] = ""
    
    # Tracking
    products_viewed: List[str] = []
    products_analyzed: List[str] = []
    products_compared: List[str] = []
    products_ordered: List[str] = []
    total_orders: int = 0
    total_spent: float = 0  # LTV - Lifetime Value
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CustomerCreate(BaseModel):
    session_id: str
    name: Optional[str] = ""
    email: Optional[str] = ""
    phone: Optional[str] = ""
    address: Optional[str] = ""

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

# ============================================
# MODELS - Orders (Commandes)
# ============================================

class Order(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    customer_name: Optional[str] = ""
    customer_email: Optional[str] = ""  # Email du client pour les notifications
    product_id: str
    product_name: Optional[str] = ""
    products_list: List[str] = []  # Liste des produits pour commandes multiples
    supplier_id: Optional[str] = None
    supplier_name: Optional[str] = ""
    
    sale_mode: Literal["dropshipping", "affiliation"] = "dropshipping"
    quantity: int = 1
    sale_price: float  # Prix de vente
    supplier_price: float = 0  # Prix fournisseur (dropshipping)
    affiliate_commission_percent: float = 0  # Commission % (affiliation)
    affiliate_commission_amount: float = 0  # Montant commission
    net_margin: float = 0  # Marge nette
    
    status: Literal["pending", "processing", "shipped", "delivered", "cancelled"] = "pending"
    affiliate_click_id: Optional[str] = None  # ID du clic affilié associé
    cancellation_reason: Optional[str] = ""  # Raison de l'annulation
    cancellation_email_sent: bool = False  # Email d'annulation envoyé
    
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class OrderCreate(BaseModel):
    customer_id: str
    product_id: str
    quantity: int = 1
    customer_name: Optional[str] = ""
    customer_email: Optional[str] = ""
    customer_address: Optional[str] = ""

class OrderUpdate(BaseModel):
    status: Optional[Literal["pending", "processing", "shipped", "delivered", "cancelled"]] = None
    customer_email: Optional[str] = None
    cancellation_reason: Optional[str] = None

class OrderCancellation(BaseModel):
    reason: Optional[str] = "Produits non disponibles"
    send_email: bool = True

# ============================================
# MODELS - Affiliate Clicks
# ============================================

class AffiliateClick(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: Optional[str] = None
    session_id: str
    product_id: str
    product_name: Optional[str] = ""
    supplier_id: Optional[str] = None
    affiliate_link: str
    
    converted: bool = False  # Si la vente a été confirmée
    commission_amount: float = 0
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    converted_at: Optional[datetime] = None

# ============================================
# MODELS - Commissions
# ============================================

class Commission(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order_id: Optional[str] = None
    affiliate_click_id: Optional[str] = None
    product_id: str
    product_name: Optional[str] = ""
    supplier_id: Optional[str] = None
    supplier_name: Optional[str] = ""
    customer_id: Optional[str] = None
    
    commission_type: Literal["dropshipping_margin", "affiliate"] = "dropshipping_margin"
    amount: float
    status: Literal["pending", "confirmed", "paid", "cancelled"] = "pending"
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    confirmed_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None

# ============================================
# MODELS - Cart & Admin
# ============================================

class CartItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    quantity: int = 1
    session_id: str

class CartItemCreate(BaseModel):
    product_id: str
    quantity: int = 1
    session_id: str

class CartItemUpdate(BaseModel):
    quantity: int

class AdminLogin(BaseModel):
    password: str

# ============================================
# MODELS - Alerts
# ============================================

class Alert(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: Literal["stock_out", "pending_commission", "unconfirmed_order", "high_growth", "low_performance"]
    title: str
    message: str
    product_id: Optional[str] = None
    supplier_id: Optional[str] = None
    order_id: Optional[str] = None
    is_read: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SiteSettings(BaseModel):
    """Paramètres globaux du site"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = "site_settings"
    maintenance_mode: bool = False
    maintenance_title: str = "Site en maintenance"
    maintenance_message: str = "Nous effectuons actuellement des mises à jour. Veuillez revenir plus tard."
    maintenance_enabled_at: Optional[datetime] = None
    maintenance_enabled_by: str = "admin"
    allow_admin_access: bool = True
    estimated_return: Optional[str] = ""
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ============================================
# ROOT ENDPOINT
# ============================================

@api_router.get("/")
async def root():
    return {"message": "Chasse Bionic™ API - Hybrid Dropshipping/Affiliation System"}


@api_router.get("/modules/status")
async def get_modules_status():
    """Get status of all modular engines (Phase 2)"""
    try:
        router_info = get_router_info()
        return {
            "success": True,
            "status": "operational",
            "total_modules": len(router_info),
            "modules": router_info,
            "architecture": "modular_v1"
        }
    except Exception as e:
        return {
            "success": False,
            "status": "error",
            "error": str(e)
        }


@api_router.get("/modules/docs")
async def get_modules_documentation():
    """Get detailed documentation for all modular engines"""
    from modules.docs import MODULES_DOCS
    return {
        "success": True,
        "documentation_url": "/api/docs",
        "redoc_url": "/api/redoc",
        "openapi_url": "/api/openapi.json",
        "modules": MODULES_DOCS
    }


# ============================================
# ADMIN AUTHENTICATION
# ============================================

@api_router.post("/admin/login")
async def admin_login(login: AdminLogin):
    password_hash = hashlib.sha256(login.password.encode()).hexdigest()
    if password_hash == ADMIN_PASSWORD_HASH:
        return {"success": True, "message": "Authentification réussie"}
    raise HTTPException(status_code=401, detail="Mot de passe incorrect")

# ============================================
# SITE SETTINGS / MAINTENANCE MODE
# ============================================

@api_router.get("/site/status")
async def get_site_status():
    """Vérifie le statut du site (accessible publiquement)"""
    settings = await db.site_settings.find_one({"id": "site_settings"}, {"_id": 0})
    if not settings:
        return {
            "maintenance_mode": False,
            "maintenance_title": "",
            "maintenance_message": "",
            "estimated_return": ""
        }
    return {
        "maintenance_mode": settings.get("maintenance_mode", False),
        "maintenance_title": settings.get("maintenance_title", "Site en maintenance"),
        "maintenance_message": settings.get("maintenance_message", ""),
        "estimated_return": settings.get("estimated_return", "")
    }

@api_router.get("/admin/site-settings")
async def get_site_settings():
    """Récupère les paramètres du site (admin seulement)"""
    settings = await db.site_settings.find_one({"id": "site_settings"}, {"_id": 0})
    if not settings:
        # Créer les paramètres par défaut
        default_settings = SiteSettings()
        await db.site_settings.insert_one(default_settings.model_dump())
        return default_settings
    return SiteSettings(**settings)

class MaintenanceModeUpdate(BaseModel):
    maintenance_mode: bool
    maintenance_title: Optional[str] = "Site en maintenance"
    maintenance_message: Optional[str] = "Nous effectuons actuellement des mises à jour. Veuillez revenir plus tard."
    estimated_return: Optional[str] = ""

@api_router.put("/admin/site-settings/maintenance")
async def toggle_maintenance_mode(update: MaintenanceModeUpdate):
    """Active ou désactive le mode maintenance"""
    update_data = {
        "maintenance_mode": update.maintenance_mode,
        "maintenance_title": update.maintenance_title,
        "maintenance_message": update.maintenance_message,
        "estimated_return": update.estimated_return,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    if update.maintenance_mode:
        update_data["maintenance_enabled_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.site_settings.find_one_and_update(
        {"id": "site_settings"},
        {"$set": update_data},
        upsert=True,
        return_document=True
    )
    
    status = "activé" if update.maintenance_mode else "désactivé"
    return {
        "success": True,
        "message": f"Mode veille {status}",
        "maintenance_mode": update.maintenance_mode
    }

# ============================================
# PRODUCTS ENDPOINTS
# ============================================

@api_router.get("/products", response_model=List[Product])
async def get_products(
    category: Optional[str] = None,
    animal_type: Optional[str] = None,
    season: Optional[str] = None,
    sale_mode: Optional[str] = None
):
    query = {}
    if category:
        query["category"] = category
    if animal_type:
        query["animal_type"] = animal_type
    if season:
        query["season"] = season
    if sale_mode:
        query["sale_mode"] = sale_mode
    
    products = await db.products.find(query, {"_id": 0}).sort("rank", 1).to_list(100)
    
    for product in products:
        if isinstance(product.get('created_at'), str):
            product['created_at'] = datetime.fromisoformat(product['created_at'])
    
    return products

@api_router.get("/products/top", response_model=List[Product])
async def get_top_products(limit: int = 5):
    products = await db.products.find({}, {"_id": 0}).sort("rank", 1).to_list(limit)
    
    for product in products:
        if isinstance(product.get('created_at'), str):
            product['created_at'] = datetime.fromisoformat(product['created_at'])
    
    return products

@api_router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Increment views
    await db.products.update_one({"id": product_id}, {"$inc": {"views": 1}})
    
    if isinstance(product.get('created_at'), str):
        product['created_at'] = datetime.fromisoformat(product['created_at'])
    
    return product

@api_router.post("/products", response_model=Product)
async def create_product(product_input: ProductCreate):
    product_dict = product_input.model_dump()
    product_obj = Product(**product_dict)
    
    doc = product_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.products.insert_one(doc)
    return product_obj

# ============================================
# ADVANCED PRODUCT FILTERS
# ============================================

@api_router.get("/products/filters/options")
async def get_filter_options():
    """Retourne toutes les options de filtres disponibles basées sur les produits existants"""
    products = await db.products.find({}, {"_id": 0}).to_list(1000)
    
    # Extract unique values for each filter
    formats = set()
    brands = set()
    scents = set()
    animals = set()
    seasons = set()
    price_ranges = {"min": float('inf'), "max": 0}
    
    for product in products:
        if product.get("product_format"):
            formats.add(product["product_format"])
        if product.get("brand"):
            brands.add(product["brand"])
        if product.get("scent_flavor"):
            scents.add(product["scent_flavor"])
        if product.get("animal_type"):
            animals.add(product["animal_type"])
        if product.get("target_animals"):
            animals.update(product["target_animals"])
        if product.get("season"):
            seasons.add(product["season"])
        if product.get("price"):
            price_ranges["min"] = min(price_ranges["min"], product["price"])
            price_ranges["max"] = max(price_ranges["max"], product["price"])
    
    return {
        "formats": [
            {"id": "gel", "name": "Gel / Gelée", "icon": "🧴"},
            {"id": "bloc", "name": "Bloc de sel", "icon": "🧱"},
            {"id": "urine", "name": "Urine / Leurre", "icon": "💧"},
            {"id": "granules", "name": "Granules / Pellets", "icon": "🌾"},
            {"id": "liquide", "name": "Liquide / Spray", "icon": "💨"},
            {"id": "poudre", "name": "Poudre / Additif", "icon": "✨"}
        ],
        "brands": sorted(list(brands)),
        "scents": [
            {"id": "pomme", "name": "Pomme", "icon": "🍎"},
            {"id": "vanille", "name": "Vanille", "icon": "🍦"},
            {"id": "anis", "name": "Anis", "icon": "⭐"},
            {"id": "hickory", "name": "Hickory / Fumé", "icon": "🔥"},
            {"id": "mais", "name": "Maïs", "icon": "🌽"},
            {"id": "gland", "name": "Gland / Chêne", "icon": "🌰"},
            {"id": "urine", "name": "Urine naturelle", "icon": "💧"},
            {"id": "mineral", "name": "Minéral", "icon": "💎"},
            {"id": "autre", "name": "Autre", "icon": "🎯"}
        ],
        "animals": [
            {"id": "deer", "name": "Cerf / Chevreuil", "icon": "🦌"},
            {"id": "moose", "name": "Orignal", "icon": "🫎"},
            {"id": "bear", "name": "Ours", "icon": "🐻"},
            {"id": "elk", "name": "Wapiti", "icon": "🦌"},
            {"id": "wild_boar", "name": "Sanglier", "icon": "🐗"},
            {"id": "other", "name": "Autre", "icon": "🎯"}
        ],
        "seasons": [
            {"id": "spring", "name": "Printemps", "icon": "🌸"},
            {"id": "summer", "name": "Été", "icon": "☀️"},
            {"id": "fall", "name": "Automne", "icon": "🍂"},
            {"id": "winter", "name": "Hiver", "icon": "❄️"},
            {"id": "all", "name": "Toutes saisons", "icon": "📅"}
        ],
        "pheromone_types": [
            {"id": "estrous", "name": "Oestrus / Rut", "icon": "💕"},
            {"id": "territorial", "name": "Territorial", "icon": "🏴"},
            {"id": "tarsal", "name": "Tarsal", "icon": "🦵"},
            {"id": "preorbital", "name": "Préorbital", "icon": "👁️"},
            {"id": "none", "name": "Sans phéromone", "icon": "❌"}
        ],
        "price_range": {
            "min": price_ranges["min"] if price_ranges["min"] != float('inf') else 0,
            "max": price_ranges["max"] if price_ranges["max"] > 0 else 100
        },
        "features": [
            {"id": "rainproof", "name": "Résistant à la pluie", "icon": "🌧️"},
            {"id": "feed_proof", "name": "Feed-Proof", "icon": "✅"},
            {"id": "certified", "name": "Certifié alimentaire", "icon": "🏆"},
            {"id": "natural", "name": "100% Naturel", "icon": "🌿"},
            {"id": "has_pheromones", "name": "Avec phéromones", "icon": "💕"}
        ],
        "shipping_options": [
            {"id": "with_shipping", "name": "Prix avec transport"},
            {"id": "without_shipping", "name": "Prix sans transport"}
        ]
    }

@api_router.post("/products/search")
async def search_products_advanced(
    formats: Optional[List[str]] = None,
    brands: Optional[List[str]] = None,
    animals: Optional[List[str]] = None,
    seasons: Optional[List[str]] = None,
    scents: Optional[List[str]] = None,
    has_pheromones: Optional[bool] = None,
    pheromone_types: Optional[List[str]] = None,
    rainproof: Optional[bool] = None,
    feed_proof: Optional[bool] = None,
    certified: Optional[bool] = None,
    natural_only: Optional[bool] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    include_shipping: bool = False,
    min_score: Optional[int] = None,
    min_attraction_days: Optional[int] = None,
    sort_by: str = "rank",
    sort_order: str = "asc"
):
    """Recherche avancée de produits avec filtres multiples"""
    query = {}
    
    # Format filter
    if formats:
        query["product_format"] = {"$in": formats}
    
    # Brand filter
    if brands:
        query["brand"] = {"$in": brands}
    
    # Animal filter
    if animals:
        query["$or"] = [
            {"animal_type": {"$in": animals}},
            {"target_animals": {"$in": animals}}
        ]
    
    # Season filter
    if seasons:
        query["season"] = {"$in": seasons}
    
    # Scent filter
    if scents:
        query["scent_flavor"] = {"$in": scents}
    
    # Pheromone filters
    if has_pheromones is not None:
        query["has_pheromones"] = has_pheromones
    
    if pheromone_types:
        query["pheromone_type"] = {"$in": pheromone_types}
    
    # Feature filters
    if rainproof is not None:
        query["rainproof"] = rainproof
    
    if feed_proof is not None:
        query["feed_proof"] = feed_proof
    
    if certified is not None:
        query["certified_food"] = certified
    
    if natural_only:
        query["ingredients_natural"] = True
    
    # Price filter
    if min_price is not None or max_price is not None:
        price_field = "price"
        price_query = {}
        if min_price is not None:
            price_query["$gte"] = min_price
        if max_price is not None:
            price_query["$lte"] = max_price
        query[price_field] = price_query
    
    # Score filter
    if min_score is not None:
        query["score"] = {"$gte": min_score}
    
    # Attraction days filter
    if min_attraction_days is not None:
        query["attraction_days"] = {"$gte": min_attraction_days}
    
    # Sort configuration
    sort_direction = 1 if sort_order == "asc" else -1
    
    products = await db.products.find(query, {"_id": 0}).sort(sort_by, sort_direction).to_list(100)
    
    # Process products
    for product in products:
        if isinstance(product.get('created_at'), str):
            product['created_at'] = datetime.fromisoformat(product['created_at'])
        
        # Calculate total price with shipping if requested
        if include_shipping:
            product['total_price'] = product.get('price', 0) + product.get('shipping_cost', 10)
        else:
            product['total_price'] = product.get('price', 0)
    
    return {
        "count": len(products),
        "products": products
    }

# Track product analysis
@api_router.post("/products/{product_id}/analyze")
async def track_product_analyze(product_id: str, session_id: str):
    await db.products.update_one({"id": product_id}, {"$inc": {"clicks": 1}})
    
    # Update customer tracking
    await db.customers.update_one(
        {"session_id": session_id},
        {"$addToSet": {"products_analyzed": product_id}},
        upsert=True
    )
    
    return {"success": True}

# Track product comparison
@api_router.post("/products/{product_id}/compare")
async def track_product_compare(product_id: str, session_id: str):
    await db.products.update_one({"id": product_id}, {"$inc": {"comparisons": 1}})
    
    # Update customer tracking
    await db.customers.update_one(
        {"session_id": session_id},
        {"$addToSet": {"products_compared": product_id}},
        upsert=True
    )
    
    return {"success": True}

# ============================================
# SUPPLIERS ENDPOINTS
# ============================================

@api_router.get("/suppliers", response_model=List[Supplier])
async def get_suppliers():
    suppliers = await db.suppliers.find({}, {"_id": 0}).to_list(100)
    for supplier in suppliers:
        if isinstance(supplier.get('created_at'), str):
            supplier['created_at'] = datetime.fromisoformat(supplier['created_at'])
    return suppliers

@api_router.get("/suppliers/{supplier_id}", response_model=Supplier)
async def get_supplier(supplier_id: str):
    supplier = await db.suppliers.find_one({"id": supplier_id}, {"_id": 0})
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    if isinstance(supplier.get('created_at'), str):
        supplier['created_at'] = datetime.fromisoformat(supplier['created_at'])
    return supplier

@api_router.post("/suppliers", response_model=Supplier)
async def create_supplier(supplier_input: SupplierCreate):
    supplier_dict = supplier_input.model_dump()
    supplier_obj = Supplier(**supplier_dict)
    
    doc = supplier_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.suppliers.insert_one(doc)
    return supplier_obj

@api_router.put("/suppliers/{supplier_id}", response_model=Supplier)
async def update_supplier(supplier_id: str, update: SupplierUpdate):
    update_data = {k: v for k, v in update.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    result = await db.suppliers.find_one_and_update(
        {"id": supplier_id},
        {"$set": update_data},
        return_document=True
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    if isinstance(result.get('created_at'), str):
        result['created_at'] = datetime.fromisoformat(result['created_at'])
    
    return Supplier(**{k: v for k, v in result.items() if k != "_id"})

@api_router.delete("/suppliers/{supplier_id}")
async def delete_supplier(supplier_id: str):
    result = await db.suppliers.delete_one({"id": supplier_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return {"message": "Supplier deleted successfully"}

# ============================================
# CUSTOMERS ENDPOINTS
# ============================================

@api_router.get("/customers", response_model=List[Customer])
async def get_customers():
    customers = await db.customers.find({}, {"_id": 0}).to_list(100)
    for customer in customers:
        if isinstance(customer.get('created_at'), str):
            customer['created_at'] = datetime.fromisoformat(customer['created_at'])
    return customers

@api_router.get("/customers/{customer_id}", response_model=Customer)
async def get_customer(customer_id: str):
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    if isinstance(customer.get('created_at'), str):
        customer['created_at'] = datetime.fromisoformat(customer['created_at'])
    return customer

@api_router.post("/customers", response_model=Customer)
async def create_or_update_customer(customer_input: CustomerCreate):
    existing = await db.customers.find_one({"session_id": customer_input.session_id})
    
    if existing:
        update_data = {k: v for k, v in customer_input.model_dump().items() if v}
        await db.customers.update_one(
            {"session_id": customer_input.session_id},
            {"$set": update_data}
        )
        updated = await db.customers.find_one({"session_id": customer_input.session_id}, {"_id": 0})
        if isinstance(updated.get('created_at'), str):
            updated['created_at'] = datetime.fromisoformat(updated['created_at'])
        return Customer(**updated)
    
    customer_dict = customer_input.model_dump()
    customer_obj = Customer(**customer_dict)
    
    doc = customer_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.customers.insert_one(doc)
    return customer_obj

# ============================================
# ORDERS ENDPOINTS (Dropshipping)
# ============================================

@api_router.get("/orders", response_model=List[Order])
async def get_orders(status: Optional[str] = None, sale_mode: Optional[str] = None):
    query = {}
    if status:
        query["status"] = status
    if sale_mode:
        query["sale_mode"] = sale_mode
    
    orders = await db.orders.find(query, {"_id": 0}).sort("created_at", -1).to_list(500)
    for order in orders:
        if isinstance(order.get('created_at'), str):
            order['created_at'] = datetime.fromisoformat(order['created_at'])
    return orders

@api_router.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: str):
    order = await db.orders.find_one({"id": order_id}, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if isinstance(order.get('created_at'), str):
        order['created_at'] = datetime.fromisoformat(order['created_at'])
    return order

@api_router.post("/orders", response_model=Order)
async def create_order(order_input: OrderCreate):
    # Get product details
    product = await db.products.find_one({"id": order_input.product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Determine sale mode (hybrid logic)
    sale_mode = product.get("sale_mode", "dropshipping")
    if sale_mode == "hybrid":
        if product.get("dropshipping_available", True):
            sale_mode = "dropshipping"
        else:
            sale_mode = "affiliation"
    
    # Get supplier info
    supplier = None
    supplier_name = ""
    supplier_id = product.get("supplier_id")
    if supplier_id:
        supplier = await db.suppliers.find_one({"id": supplier_id}, {"_id": 0})
        if supplier:
            supplier_name = supplier.get("name", "")
    
    # Calculate margins/commissions
    sale_price = product.get("price", 0) * order_input.quantity
    supplier_price = product.get("supplier_price", 0) * order_input.quantity
    affiliate_commission_percent = product.get("affiliate_commission", 0)
    
    if sale_mode == "dropshipping":
        net_margin = sale_price - supplier_price
        affiliate_commission_amount = 0
    else:  # affiliation
        affiliate_commission_amount = sale_price * (affiliate_commission_percent / 100)
        net_margin = affiliate_commission_amount
        supplier_price = 0
    
    # Create order
    order = Order(
        customer_id=order_input.customer_id,
        customer_name=order_input.customer_name,
        product_id=order_input.product_id,
        product_name=product.get("name", ""),
        supplier_id=supplier_id,
        supplier_name=supplier_name,
        sale_mode=sale_mode,
        quantity=order_input.quantity,
        sale_price=sale_price,
        supplier_price=supplier_price,
        affiliate_commission_percent=affiliate_commission_percent,
        affiliate_commission_amount=affiliate_commission_amount,
        net_margin=net_margin,
        status="pending"
    )
    
    doc = order.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.orders.insert_one(doc)
    
    # Update product orders count
    await db.products.update_one({"id": order_input.product_id}, {"$inc": {"orders": 1}})
    
    # Update customer
    await db.customers.update_one(
        {"id": order_input.customer_id},
        {
            "$addToSet": {"products_ordered": order_input.product_id},
            "$inc": {"total_orders": 1, "total_spent": sale_price}
        }
    )
    
    # Update supplier stats
    if supplier_id:
        await db.suppliers.update_one(
            {"id": supplier_id},
            {
                "$inc": {
                    "total_orders": 1,
                    "total_revenue_supplier": supplier_price,
                    "total_revenue_scent": net_margin
                }
            }
        )
    
    # Create commission record
    commission = Commission(
        order_id=order.id,
        product_id=order_input.product_id,
        product_name=product.get("name", ""),
        supplier_id=supplier_id,
        supplier_name=supplier_name,
        customer_id=order_input.customer_id,
        commission_type="dropshipping_margin" if sale_mode == "dropshipping" else "affiliate",
        amount=net_margin,
        status="pending"
    )
    
    commission_doc = commission.model_dump()
    commission_doc['created_at'] = commission_doc['created_at'].isoformat()
    await db.commissions.insert_one(commission_doc)
    
    return order

@api_router.put("/orders/{order_id}", response_model=Order)
async def update_order_status(order_id: str, update: OrderUpdate):
    update_data = {}
    if update.status:
        update_data["status"] = update.status
        if update.status == "shipped":
            update_data["shipped_at"] = datetime.now(timezone.utc).isoformat()
        elif update.status == "delivered":
            update_data["delivered_at"] = datetime.now(timezone.utc).isoformat()
            # Confirm commission
            await db.commissions.update_one(
                {"order_id": order_id},
                {"$set": {"status": "confirmed", "confirmed_at": datetime.now(timezone.utc).isoformat()}}
            )
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    result = await db.orders.find_one_and_update(
        {"id": order_id},
        {"$set": update_data},
        return_document=True
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if isinstance(result.get('created_at'), str):
        result['created_at'] = datetime.fromisoformat(result['created_at'])
    
    return Order(**{k: v for k, v in result.items() if k != "_id"})

@api_router.post("/orders/{order_id}/cancel")
async def cancel_order_with_notification(order_id: str, cancellation: OrderCancellation, background_tasks: BackgroundTasks):
    """
    Annule une commande et envoie un email de notification au client
    """
    # Récupérer la commande
    order = await db.orders.find_one({"id": order_id}, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    
    if order.get("status") == "cancelled":
        raise HTTPException(status_code=400, detail="Cette commande est déjà annulée")
    
    # Préparer les données de mise à jour
    update_data = {
        "status": "cancelled",
        "cancelled_at": datetime.now(timezone.utc).isoformat(),
        "cancellation_reason": cancellation.reason
    }
    
    # Récupérer les informations du client
    customer_email = order.get("customer_email", "")
    customer_name = order.get("customer_name", "Client")
    
    # Si pas d'email dans la commande, essayer de le récupérer depuis le client
    if not customer_email and order.get("customer_id"):
        customer = await db.customers.find_one({"id": order.get("customer_id")}, {"_id": 0})
        if customer:
            customer_email = customer.get("email", "")
            if not customer_name or customer_name == "Client":
                customer_name = customer.get("name", "Client")
    
    # Préparer la liste des produits
    products_list = order.get("products_list", [])
    if not products_list and order.get("product_name"):
        products_list = [order.get("product_name")]
    
    email_result = {"status": "skipped", "message": "Aucun email client disponible"}
    
    # Envoyer l'email si demandé et si on a un email
    if cancellation.send_email and customer_email:
        email_result = await send_cancellation_email(
            to_email=customer_email,
            customer_name=customer_name or "Client",
            products=products_list if products_list else ["Produit(s) commandé(s)"],
            order_id=order_id
        )
        update_data["cancellation_email_sent"] = email_result.get("status") in ["sent", "simulated"]
    
    # Mettre à jour la commande
    result = await db.orders.find_one_and_update(
        {"id": order_id},
        {"$set": update_data},
        return_document=True
    )
    
    # Annuler la commission associée
    await db.commissions.update_one(
        {"order_id": order_id},
        {"$set": {"status": "cancelled"}}
    )
    
    if isinstance(result.get('created_at'), str):
        result['created_at'] = datetime.fromisoformat(result['created_at'])
    
    return {
        "success": True,
        "message": "Commande annulée avec succès",
        "order": Order(**{k: v for k, v in result.items() if k != "_id"}),
        "email_notification": email_result
    }

@api_router.get("/email/status")
async def get_email_service_status():
    """Vérifie le statut du service email"""
    return {
        "configured": is_email_configured(),
        "message": "Service email configuré" if is_email_configured() else "Service email non configuré (mode simulation)"
    }

# ============================================
# AFFILIATE CLICKS ENDPOINTS
# ============================================

@api_router.post("/affiliate/click")
async def record_affiliate_click(product_id: str, session_id: str):
    # Get product details
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    affiliate_link = product.get("affiliate_link", "")
    if not affiliate_link:
        raise HTTPException(status_code=400, detail="No affiliate link for this product")
    
    # Get or create customer
    customer = await db.customers.find_one({"session_id": session_id})
    customer_id = customer.get("id") if customer else None
    
    # Create affiliate click record
    click = AffiliateClick(
        customer_id=customer_id,
        session_id=session_id,
        product_id=product_id,
        product_name=product.get("name", ""),
        supplier_id=product.get("supplier_id"),
        affiliate_link=affiliate_link
    )
    
    doc = click.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.affiliate_clicks.insert_one(doc)
    
    # Increment product clicks
    await db.products.update_one({"id": product_id}, {"$inc": {"clicks": 1}})
    
    return {"success": True, "click_id": click.id, "redirect_url": affiliate_link}

@api_router.get("/affiliate/clicks", response_model=List[AffiliateClick])
async def get_affiliate_clicks():
    clicks = await db.affiliate_clicks.find({}, {"_id": 0}).sort("created_at", -1).to_list(500)
    for click in clicks:
        if isinstance(click.get('created_at'), str):
            click['created_at'] = datetime.fromisoformat(click['created_at'])
    return clicks

@api_router.post("/affiliate/confirm/{click_id}")
async def confirm_affiliate_sale(click_id: str, commission_amount: float):
    """Confirm an affiliate sale (manual or via API callback)"""
    click = await db.affiliate_clicks.find_one({"id": click_id})
    if not click:
        raise HTTPException(status_code=404, detail="Affiliate click not found")
    
    # Update click as converted
    await db.affiliate_clicks.update_one(
        {"id": click_id},
        {
            "$set": {
                "converted": True,
                "commission_amount": commission_amount,
                "converted_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    # Create commission record
    commission = Commission(
        affiliate_click_id=click_id,
        product_id=click.get("product_id"),
        product_name=click.get("product_name"),
        supplier_id=click.get("supplier_id"),
        customer_id=click.get("customer_id"),
        commission_type="affiliate",
        amount=commission_amount,
        status="confirmed"
    )
    
    commission_doc = commission.model_dump()
    commission_doc['created_at'] = commission_doc['created_at'].isoformat()
    commission_doc['confirmed_at'] = datetime.now(timezone.utc).isoformat()
    
    await db.commissions.insert_one(commission_doc)
    
    return {"success": True, "commission_id": commission.id}

# ============================================
# COMMISSIONS ENDPOINTS
# ============================================

@api_router.get("/commissions", response_model=List[Commission])
async def get_commissions(status: Optional[str] = None, commission_type: Optional[str] = None):
    query = {}
    if status:
        query["status"] = status
    if commission_type:
        query["commission_type"] = commission_type
    
    commissions = await db.commissions.find(query, {"_id": 0}).sort("created_at", -1).to_list(500)
    for commission in commissions:
        if isinstance(commission.get('created_at'), str):
            commission['created_at'] = datetime.fromisoformat(commission['created_at'])
    return commissions

@api_router.put("/commissions/{commission_id}/pay")
async def mark_commission_paid(commission_id: str):
    result = await db.commissions.find_one_and_update(
        {"id": commission_id},
        {"$set": {"status": "paid", "paid_at": datetime.now(timezone.utc).isoformat()}},
        return_document=True
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Commission not found")
    
    return {"success": True, "message": "Commission marked as paid"}

# ============================================
# CART ENDPOINTS
# ============================================

@api_router.get("/cart/{session_id}", response_model=List[dict])
async def get_cart(session_id: str):
    cart_items = await db.cart.find({"session_id": session_id}, {"_id": 0}).to_list(100)
    
    result = []
    for item in cart_items:
        product = await db.products.find_one({"id": item["product_id"]}, {"_id": 0})
        if product:
            result.append({
                "id": item["id"],
                "product": product,
                "quantity": item["quantity"]
            })
    
    return result

@api_router.post("/cart", response_model=CartItem)
async def add_to_cart(item_input: CartItemCreate):
    product = await db.products.find_one({"id": item_input.product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    existing = await db.cart.find_one({
        "product_id": item_input.product_id,
        "session_id": item_input.session_id
    })
    
    if existing:
        new_quantity = existing["quantity"] + item_input.quantity
        await db.cart.update_one(
            {"id": existing["id"]},
            {"$set": {"quantity": new_quantity}}
        )
        existing["quantity"] = new_quantity
        return CartItem(**{k: v for k, v in existing.items() if k != "_id"})
    
    cart_item = CartItem(
        product_id=item_input.product_id,
        quantity=item_input.quantity,
        session_id=item_input.session_id
    )
    
    await db.cart.insert_one(cart_item.model_dump())
    return cart_item

@api_router.put("/cart/{item_id}", response_model=CartItem)
async def update_cart_item(item_id: str, update: CartItemUpdate):
    result = await db.cart.find_one_and_update(
        {"id": item_id},
        {"$set": {"quantity": update.quantity}},
        return_document=True
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    return CartItem(**{k: v for k, v in result.items() if k != "_id"})

@api_router.delete("/cart/{item_id}")
async def remove_from_cart(item_id: str):
    result = await db.cart.delete_one({"id": item_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return {"message": "Item removed from cart"}

@api_router.delete("/cart/session/{session_id}")
async def clear_cart(session_id: str):
    await db.cart.delete_many({"session_id": session_id})
    return {"message": "Cart cleared"}

# ============================================
# ADMIN STATISTICS & DASHBOARD
# ============================================

@api_router.get("/admin/stats")
async def admin_get_stats():
    products_count = await db.products.count_documents({})
    suppliers_count = await db.suppliers.count_documents({})
    customers_count = await db.customers.count_documents({})
    orders_count = await db.orders.count_documents({})
    
    # Orders by status
    pending_orders = await db.orders.count_documents({"status": "pending"})
    processing_orders = await db.orders.count_documents({"status": "processing"})
    shipped_orders = await db.orders.count_documents({"status": "shipped"})
    delivered_orders = await db.orders.count_documents({"status": "delivered"})
    
    # Revenue calculations
    orders = await db.orders.find({}, {"_id": 0}).to_list(1000)
    total_sales = sum(o.get("sale_price", 0) for o in orders)
    total_margins = sum(o.get("net_margin", 0) for o in orders)
    dropshipping_sales = sum(o.get("sale_price", 0) for o in orders if o.get("sale_mode") == "dropshipping")
    affiliate_sales = sum(o.get("sale_price", 0) for o in orders if o.get("sale_mode") == "affiliation")
    
    # Commission totals
    commissions = await db.commissions.find({}, {"_id": 0}).to_list(1000)
    total_commissions = sum(c.get("amount", 0) for c in commissions)
    pending_commissions = sum(c.get("amount", 0) for c in commissions if c.get("status") == "pending")
    confirmed_commissions = sum(c.get("amount", 0) for c in commissions if c.get("status") == "confirmed")
    paid_commissions = sum(c.get("amount", 0) for c in commissions if c.get("status") == "paid")
    
    # Cart stats
    cart_items_count = await db.cart.count_documents({})
    cart_items = await db.cart.find({}).to_list(1000)
    total_cart_value = 0
    for item in cart_items:
        product = await db.products.find_one({"id": item.get("product_id")})
        if product:
            total_cart_value += product.get("price", 0) * item.get("quantity", 1)
    
    return {
        "products_count": products_count,
        "suppliers_count": suppliers_count,
        "customers_count": customers_count,
        "orders_count": orders_count,
        "orders_by_status": {
            "pending": pending_orders,
            "processing": processing_orders,
            "shipped": shipped_orders,
            "delivered": delivered_orders
        },
        "total_sales": round(total_sales, 2),
        "total_margins": round(total_margins, 2),
        "dropshipping_sales": round(dropshipping_sales, 2),
        "affiliate_sales": round(affiliate_sales, 2),
        "total_commissions": round(total_commissions, 2),
        "pending_commissions": round(pending_commissions, 2),
        "confirmed_commissions": round(confirmed_commissions, 2),
        "paid_commissions": round(paid_commissions, 2),
        "cart_items_count": cart_items_count,
        "total_cart_value": round(total_cart_value, 2)
    }

@api_router.get("/admin/products", response_model=List[Product])
async def admin_get_products():
    products = await db.products.find({}, {"_id": 0}).sort("rank", 1).to_list(100)
    for product in products:
        if isinstance(product.get('created_at'), str):
            product['created_at'] = datetime.fromisoformat(product['created_at'])
    return products

@api_router.put("/admin/products/{product_id}", response_model=Product)
async def admin_update_product(product_id: str, update: ProductUpdate):
    update_data = {k: v for k, v in update.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    result = await db.products.find_one_and_update(
        {"id": product_id},
        {"$set": update_data},
        return_document=True
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if isinstance(result.get('created_at'), str):
        result['created_at'] = datetime.fromisoformat(result['created_at'])
    
    return Product(**{k: v for k, v in result.items() if k != "_id"})

@api_router.delete("/admin/products/{product_id}")
async def admin_delete_product(product_id: str):
    result = await db.products.delete_one({"id": product_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}

@api_router.post("/admin/products", response_model=Product)
async def admin_add_product(product_input: ProductCreate):
    product_dict = product_input.model_dump()
    product_obj = Product(**product_dict)
    
    doc = product_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.products.insert_one(doc)
    return product_obj

# ============================================
# ADMIN REPORTS
# ============================================

@api_router.get("/admin/reports/sales")
async def get_sales_report(period: str = "month"):
    """Get sales report for a period (week, month, year)"""
    now = datetime.now(timezone.utc)
    
    if period == "week":
        start_date = now - timedelta(days=7)
    elif period == "month":
        start_date = now - timedelta(days=30)
    else:
        start_date = now - timedelta(days=365)
    
    orders = await db.orders.find({}, {"_id": 0}).to_list(1000)
    
    # Filter by date
    period_orders = []
    for order in orders:
        created_at = order.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        if created_at and created_at >= start_date:
            period_orders.append(order)
    
    total_sales = sum(o.get("sale_price", 0) for o in period_orders)
    total_margins = sum(o.get("net_margin", 0) for o in period_orders)
    dropshipping_count = len([o for o in period_orders if o.get("sale_mode") == "dropshipping"])
    affiliate_count = len([o for o in period_orders if o.get("sale_mode") == "affiliation"])
    
    return {
        "period": period,
        "start_date": start_date.isoformat(),
        "end_date": now.isoformat(),
        "total_orders": len(period_orders),
        "total_sales": round(total_sales, 2),
        "total_margins": round(total_margins, 2),
        "dropshipping_orders": dropshipping_count,
        "affiliate_orders": affiliate_count,
        "orders": period_orders
    }

@api_router.get("/admin/reports/products")
async def get_products_performance_report():
    """Get product performance report"""
    products = await db.products.find({}, {"_id": 0}).to_list(100)
    
    # Calculate conversion rates
    for product in products:
        views = product.get("views", 0) or 1
        clicks = product.get("clicks", 0)
        comparisons = product.get("comparisons", 0)
        orders = product.get("orders", 0)
        
        product["view_to_click_rate"] = round((clicks / views) * 100, 2) if views > 0 else 0
        product["click_to_compare_rate"] = round((comparisons / clicks) * 100, 2) if clicks > 0 else 0
        product["compare_to_order_rate"] = round((orders / comparisons) * 100, 2) if comparisons > 0 else 0
        product["overall_conversion_rate"] = round((orders / views) * 100, 2) if views > 0 else 0
    
    # Sort by different metrics
    most_viewed = sorted(products, key=lambda x: x.get("views", 0), reverse=True)[:10]
    most_clicked = sorted(products, key=lambda x: x.get("clicks", 0), reverse=True)[:10]
    most_ordered = sorted(products, key=lambda x: x.get("orders", 0), reverse=True)[:10]
    best_conversion = sorted(products, key=lambda x: x.get("overall_conversion_rate", 0), reverse=True)[:10]
    
    return {
        "most_viewed": most_viewed,
        "most_clicked": most_clicked,
        "most_ordered": most_ordered,
        "best_conversion": best_conversion,
        "all_products": products
    }

@api_router.get("/admin/reports/suppliers")
async def get_suppliers_performance_report():
    """Get suppliers performance report"""
    suppliers = await db.suppliers.find({}, {"_id": 0}).to_list(100)
    
    for supplier in suppliers:
        # Get orders for this supplier
        orders = await db.orders.find({"supplier_id": supplier.get("id")}, {"_id": 0}).to_list(1000)
        
        supplier["orders_detail"] = {
            "total": len(orders),
            "pending": len([o for o in orders if o.get("status") == "pending"]),
            "delivered": len([o for o in orders if o.get("status") == "delivered"]),
            "cancelled": len([o for o in orders if o.get("status") == "cancelled"])
        }
        
        # Calculate confirmation rate
        if len(orders) > 0:
            delivered = len([o for o in orders if o.get("status") == "delivered"])
            cancelled = len([o for o in orders if o.get("status") == "cancelled"])
            supplier["confirmation_rate"] = round((delivered / (delivered + cancelled)) * 100, 2) if (delivered + cancelled) > 0 else 100
    
    return suppliers

@api_router.get("/admin/reports/commissions")
async def get_commissions_report(period: str = "month"):
    """Get commissions report"""
    now = datetime.now(timezone.utc)
    
    if period == "week":
        start_date = now - timedelta(days=7)
    elif period == "month":
        start_date = now - timedelta(days=30)
    else:
        start_date = now - timedelta(days=365)
    
    commissions = await db.commissions.find({}, {"_id": 0}).to_list(1000)
    
    # Group by product
    by_product = {}
    # Group by supplier
    by_supplier = {}
    
    total = 0
    for commission in commissions:
        amount = commission.get("amount", 0)
        total += amount
        
        product_id = commission.get("product_id")
        if product_id:
            if product_id not in by_product:
                by_product[product_id] = {"name": commission.get("product_name", ""), "total": 0, "count": 0}
            by_product[product_id]["total"] += amount
            by_product[product_id]["count"] += 1
        
        supplier_id = commission.get("supplier_id")
        if supplier_id:
            if supplier_id not in by_supplier:
                by_supplier[supplier_id] = {"name": commission.get("supplier_name", ""), "total": 0, "count": 0}
            by_supplier[supplier_id]["total"] += amount
            by_supplier[supplier_id]["count"] += 1
    
    return {
        "total_commissions": round(total, 2),
        "by_product": list(by_product.values()),
        "by_supplier": list(by_supplier.values()),
        "all_commissions": commissions
    }

# ============================================
# ALERTS
# ============================================

@api_router.get("/admin/alerts", response_model=List[Alert])
async def get_alerts():
    alerts = await db.alerts.find({}, {"_id": 0}).sort("created_at", -1).to_list(100)
    for alert in alerts:
        if isinstance(alert.get('created_at'), str):
            alert['created_at'] = datetime.fromisoformat(alert['created_at'])
    return alerts

@api_router.post("/admin/alerts/generate")
async def generate_alerts():
    """Generate system alerts"""
    alerts_created = []
    
    # Check for products with dropshipping unavailable
    products = await db.products.find({"dropshipping_available": False, "sale_mode": {"$in": ["dropshipping", "hybrid"]}}, {"_id": 0}).to_list(100)
    for product in products:
        alert = Alert(
            type="stock_out",
            title="Rupture de stock fournisseur",
            message=f"Le produit '{product.get('name')}' n'est plus disponible en dropshipping",
            product_id=product.get("id")
        )
        doc = alert.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.alerts.insert_one(doc)
        alerts_created.append(alert)
    
    # Check for pending commissions
    pending_commissions = await db.commissions.count_documents({"status": "pending"})
    if pending_commissions > 0:
        alert = Alert(
            type="pending_commission",
            title="Commissions en attente",
            message=f"{pending_commissions} commission(s) en attente de confirmation"
        )
        doc = alert.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.alerts.insert_one(doc)
        alerts_created.append(alert)
    
    # Check for unconfirmed orders (older than 7 days)
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    old_pending = await db.orders.find({"status": "pending"}, {"_id": 0}).to_list(100)
    for order in old_pending:
        created_at = order.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        if created_at and created_at < week_ago:
            alert = Alert(
                type="unconfirmed_order",
                title="Commande non confirmée",
                message=f"La commande #{order.get('id')[:8]} est en attente depuis plus de 7 jours",
                order_id=order.get("id")
            )
            doc = alert.model_dump()
            doc['created_at'] = doc['created_at'].isoformat()
            await db.alerts.insert_one(doc)
            alerts_created.append(alert)
    
    return {"alerts_created": len(alerts_created), "alerts": alerts_created}

@api_router.put("/admin/alerts/{alert_id}/read")
async def mark_alert_read(alert_id: str):
    await db.alerts.update_one({"id": alert_id}, {"$set": {"is_read": True}})
    return {"success": True}

# ============================================
# SEED DATA
# ============================================

@api_router.post("/seed")
async def seed_products():
    existing = await db.products.count_documents({})
    if existing > 0:
        return {"message": f"Products already exist ({existing} products)"}
    
    # Create default supplier
    supplier = Supplier(
        name="BIONIC™ Direct",
        contact_name="Jean Dupont",
        email="contact@bionic-direct.com",
        phone="+1-555-0123",
        address="123 Hunting Ave, Montreal, QC",
        partnership_type="hybrid",
        shipping_delay=3,
        partnership_conditions="30% margin on dropshipping, 15% commission on affiliate"
    )
    supplier_doc = supplier.model_dump()
    supplier_doc['created_at'] = supplier_doc['created_at'].isoformat()
    await db.suppliers.insert_one(supplier_doc)
    
    supplier2 = Supplier(
        name="Code Blue Distribution",
        contact_name="Marie Martin",
        email="sales@codeblue.com",
        phone="+1-555-0456",
        address="456 Hunter Rd, Quebec City, QC",
        partnership_type="affiliation",
        shipping_delay=5,
        partnership_conditions="12% commission on all sales"
    )
    supplier2_doc = supplier2.model_dump()
    supplier2_doc['created_at'] = supplier2_doc['created_at'].isoformat()
    await db.suppliers.insert_one(supplier2_doc)
    
    default_products = [
        {
            "id": str(uuid.uuid4()),
            "name": "BIONIC™ Buck Urine Premium",
            "brand": "BIONIC™",
            "price": 34.99,
            "score": 95,
            "cost_benefit_score": 88,
            "rank": 1,
            "image_url": "https://images.unsplash.com/photo-1546182990-dffeafbe841d?w=400&h=300&fit=crop",
            "description": "Premium buck urine attractant for deer hunting",
            "category": "urine",
            "animal_type": "deer",
            "season": "fall",
            "sale_mode": "hybrid",
            "supplier_id": supplier.id,
            "supplier_price": 22.00,
            "affiliate_commission": 15,
            "affiliate_link": "https://bionic-direct.com/buck-urine?ref=scentscience",
            "dropshipping_available": True,
            "views": 0, "clicks": 0, "comparisons": 0, "orders": 0,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "BIONIC™ Cow Moose Estrous",
            "brand": "BIONIC™",
            "price": 44.99,
            "score": 94,
            "cost_benefit_score": 85,
            "rank": 2,
            "image_url": "https://images.unsplash.com/photo-1517022812141-23620dba5c23?w=400&h=300&fit=crop",
            "description": "Cow moose estrous scent for moose hunting",
            "category": "urine",
            "animal_type": "moose",
            "season": "fall",
            "sale_mode": "dropshipping",
            "supplier_id": supplier.id,
            "supplier_price": 28.00,
            "affiliate_commission": 0,
            "affiliate_link": "",
            "dropshipping_available": True,
            "views": 0, "clicks": 0, "comparisons": 0, "orders": 0,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Code Blue Doe Estrous",
            "brand": "Code Blue",
            "price": 24.99,
            "score": 92,
            "cost_benefit_score": 90,
            "rank": 3,
            "image_url": "https://images.unsplash.com/photo-1504173010664-32509aeebb62?w=400&h=300&fit=crop",
            "description": "Doe estrous scent for whitetail deer",
            "category": "urine",
            "animal_type": "deer",
            "season": "fall",
            "sale_mode": "affiliation",
            "supplier_id": supplier2.id,
            "supplier_price": 0,
            "affiliate_commission": 12,
            "affiliate_link": "https://codeblue.com/doe-estrous?ref=scentscience",
            "dropshipping_available": False,
            "views": 0, "clicks": 0, "comparisons": 0, "orders": 0,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Tink's #69 Doe-in-Rut",
            "brand": "Tink's",
            "price": 29.99,
            "score": 90,
            "cost_benefit_score": 87,
            "rank": 4,
            "image_url": "https://images.unsplash.com/photo-1484406566174-9da000fda645?w=400&h=300&fit=crop",
            "description": "Classic doe-in-rut buck lure",
            "category": "lure",
            "animal_type": "deer",
            "season": "fall",
            "sale_mode": "hybrid",
            "supplier_id": supplier.id,
            "supplier_price": 18.00,
            "affiliate_commission": 10,
            "affiliate_link": "https://tinks.com/69-doe-rut?ref=scentscience",
            "dropshipping_available": True,
            "views": 0, "clicks": 0, "comparisons": 0, "orders": 0,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Bear Bomb Hickory Smoke",
            "brand": "Bear Bomb",
            "price": 26.99,
            "score": 89,
            "cost_benefit_score": 82,
            "rank": 5,
            "image_url": "https://images.unsplash.com/photo-1589656966895-2f33e7653819?w=400&h=300&fit=crop",
            "description": "Hickory smoke scent for bear hunting",
            "category": "attractant",
            "animal_type": "bear",
            "season": "spring",
            "sale_mode": "dropshipping",
            "supplier_id": supplier.id,
            "supplier_price": 16.00,
            "affiliate_commission": 0,
            "affiliate_link": "",
            "dropshipping_available": True,
            "views": 0, "clicks": 0, "comparisons": 0, "orders": 0,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    await db.products.insert_many(default_products)
    return {"message": f"Seeded {len(default_products)} products and 2 suppliers"}

# ============================================
# CLICK & ANALYSE - PRODUCT ANALYSIS MODULE
# ============================================

class AnalyzeProductRequest(BaseModel):
    product_name: str
    product_type: Optional[str] = None

class EmailConsentRequest(BaseModel):
    name: str
    email: str
    region: str
    consent_marketing: bool
    consent_statistics: bool
    report_id: str

@api_router.post("/analyze")
async def analyze_product(request: AnalyzeProductRequest):
    """Analyse complète d'un produit attractant"""
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="LLM API key not configured")
    
    try:
        analyzer = ProductAnalyzer(api_key=EMERGENT_LLM_KEY)
        report = await analyzer.analyze_product(request.product_name, request.product_type)
        
        # Sauvegarder le rapport dans la base de données
        report_dict = report.model_dump()
        report_dict['created_at'] = report_dict['created_at'].isoformat()
        
        # Convert nested datetimes
        for key in ['technical_sheet', 'scientific_analysis', 'scoring', 'comparison', 'price_analysis']:
            if key in report_dict and isinstance(report_dict[key], dict):
                for subkey, subvalue in report_dict[key].items():
                    if hasattr(subvalue, 'isoformat'):
                        report_dict[key][subkey] = subvalue.isoformat()
        
        # Save to DB without _id issues
        await db.analysis_reports.insert_one(report_dict.copy())
        
        # Remove any MongoDB _id before returning
        if '_id' in report_dict:
            del report_dict['_id']
        
        return report_dict
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@api_router.get("/analyze/categories")
async def get_product_categories():
    """Retourne les catégories de produits disponibles"""
    return {
        "categories": [
            {"id": "gel", "name": "Gel / Gelée / Jelly", "icon": "🧴"},
            {"id": "bloc", "name": "Bloc de sel", "icon": "🧱"},
            {"id": "urine", "name": "Urine / Leurre urinaire", "icon": "💧"},
            {"id": "granules", "name": "Granules / Pellets", "icon": "🌾"},
            {"id": "liquide", "name": "Liquide / Spray", "icon": "💨"},
            {"id": "poudre", "name": "Poudre / Additif", "icon": "✨"}
        ]
    }

@api_router.get("/analyze/criteria")
async def get_scoring_criteria():
    """Retourne les critères de scoring"""
    return {"criteria": SCORING_CRITERIA}

@api_router.get("/analyze/bionic-products")
async def get_bionic_products():
    """Retourne les produits BIONIC™ par catégorie"""
    return {"products": BIONIC_PRODUCTS}

@api_router.get("/analyze/competitors/{category}")
async def get_competitors(category: str):
    """Retourne les concurrents par catégorie"""
    competitors = COMPETITOR_PRODUCTS.get(category, [])
    return {"competitors": competitors}

@api_router.get("/analyze/ingredients")
async def get_ingredients_database():
    """Retourne la base de données d'ingrédients"""
    return {"ingredients": INGREDIENTS_DATABASE}

@api_router.get("/analyze/references")
async def get_scientific_references_endpoint():
    """Retourne les références scientifiques consolidées"""
    return {
        "references": get_scientific_references(),
        "total_sections": len(SCIENTIFIC_REFERENCES),
        "description": "Références scientifiques en olfaction, écologie chimique, nutrition et comportement des cervidés"
    }

# ============================================
# ANALYSE IA AVANCÉE - GPT-5.2
# ============================================

class AIAnalysisRequest(BaseModel):
    product_name: str
    species: str = "cerf"  # cerf, orignal, ours, sanglier
    season: str = "automne"  # printemps, été, automne, hiver
    weather: str = "normal"  # froid, normal, chaud, pluie, neige
    terrain: str = "forêt"  # forêt, champ, marais, montagne
    
class AIAnalysisResponse(BaseModel):
    product_name: str
    species: str
    season: str
    weather: str
    terrain: str
    score: float
    recommendation: str
    effectiveness_rating: str  # excellent, bon, moyen, faible
    best_time_of_day: str
    application_tips: List[str]
    alternative_products: List[Dict[str, Any]]
    scientific_basis: str
    weather_impact: str
    seasonal_advice: str

@api_router.post("/analyze/ai-advanced")
async def ai_advanced_analysis(request: AIAnalysisRequest):
    """Analyse IA avancée avec GPT-5.2 - Recommandations personnalisées"""
    
    # Données de référence pour l'analyse
    species_data = {
        "cerf": {"name": "Cerf de Virginie", "best_attractants": ["urine de biche", "phéromones", "pomme"], "peak_season": "automne"},
        "orignal": {"name": "Orignal", "best_attractants": ["urine d'orignal", "écorce de bouleau"], "peak_season": "automne"},
        "ours": {"name": "Ours noir", "best_attractants": ["miel", "bacon", "fruits"], "peak_season": "printemps"},
        "sanglier": {"name": "Sanglier", "best_attractants": ["maïs", "arachides"], "peak_season": "automne"},
        "dindon": {"name": "Dindon sauvage", "best_attractants": ["grains", "insectes"], "peak_season": "printemps"}
    }
    
    season_modifiers = {
        "printemps": {"score_modifier": 0.9, "advice": "Les animaux sortent de l'hiver, privilégiez les attractants nutritifs"},
        "été": {"score_modifier": 0.7, "advice": "Période moins active, concentrez-vous sur les points d'eau"},
        "automne": {"score_modifier": 1.0, "advice": "Saison du rut idéale, les phéromones sont très efficaces"},
        "hiver": {"score_modifier": 0.6, "advice": "Activité réduite, ciblez les sources de nourriture"}
    }
    
    weather_modifiers = {
        "froid": {"score_modifier": 0.9, "impact": "Le froid ralentit la diffusion des odeurs mais augmente l'activité du gibier"},
        "normal": {"score_modifier": 1.0, "impact": "Conditions idéales pour la diffusion des attractants"},
        "chaud": {"score_modifier": 0.7, "impact": "La chaleur accélère l'évaporation, renouvelez plus souvent"},
        "pluie": {"score_modifier": 0.5, "impact": "La pluie dilue les attractants, utilisez des produits résistants à l'eau"},
        "neige": {"score_modifier": 0.8, "impact": "Bonne conservation mais portée olfactive réduite"}
    }
    
    terrain_modifiers = {
        "forêt": {"score_modifier": 1.0, "tip": "Placez les attractants près des corridors naturels"},
        "champ": {"score_modifier": 0.9, "tip": "Utilisez des postes d'affût en bordure avec bonne visibilité"},
        "marais": {"score_modifier": 0.85, "tip": "L'humidité aide la diffusion, excellentes conditions"},
        "montagne": {"score_modifier": 0.8, "tip": "Tenez compte des courants d'air ascendants"}
    }
    
    # Calculer le score basé sur les conditions
    base_score = 7.5
    species_info = species_data.get(request.species, species_data["cerf"])
    season_info = season_modifiers.get(request.season, season_modifiers["automne"])
    weather_info = weather_modifiers.get(request.weather, weather_modifiers["normal"])
    terrain_info = terrain_modifiers.get(request.terrain, terrain_modifiers["forêt"])
    
    # Ajuster le score
    final_score = base_score * season_info["score_modifier"] * weather_info["score_modifier"] * terrain_info["score_modifier"]
    final_score = min(10, max(0, final_score + (0.5 if request.product_name.lower().find("bionic") >= 0 else 0)))
    
    # Déterminer l'efficacité
    if final_score >= 8:
        effectiveness = "excellent"
    elif final_score >= 6:
        effectiveness = "bon"
    elif final_score >= 4:
        effectiveness = "moyen"
    else:
        effectiveness = "faible"
    
    # Si la clé API est disponible, essayer l'analyse IA
    ai_recommendation = None
    if EMERGENT_LLM_KEY:
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            
            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=f"ai_analysis_{uuid.uuid4().hex[:8]}",
                system_message="""Tu es un expert en attractants pour la chasse. Réponds en JSON uniquement."""
            ).with_model("openai", "gpt-5.2")
            
            prompt = f"""Analyse brève de "{request.product_name}" pour {species_info['name']} en {request.season}. 
            JSON: {{"recommendation": "...", "tips": ["tip1", "tip2"]}}"""
            
            response = await chat.send_message(UserMessage(text=prompt))
            
            import json
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                ai_data = json.loads(json_match.group())
                ai_recommendation = ai_data.get("recommendation")
        except Exception as e:
            print(f"AI analysis skipped: {e}")
    
    # Construire la réponse
    return AIAnalysisResponse(
        product_name=request.product_name,
        species=request.species,
        season=request.season,
        weather=request.weather,
        terrain=request.terrain,
        score=round(final_score, 1),
        recommendation=ai_recommendation or f"{request.product_name} est un choix {effectiveness} pour la chasse au {species_info['name']} en {request.season}. {season_info['advice']}",
        effectiveness_rating=effectiveness,
        best_time_of_day="Aube (30 min avant le lever) et crépuscule (1h avant le coucher)",
        application_tips=[
            f"Pour le {species_info['name']}: placez l'attractant à hauteur de nez (1-1.5m)",
            terrain_info["tip"],
            "Renouvelez l'application tous les 3-5 jours selon les conditions",
            "Portez des gants pour éviter de contaminer le produit avec votre odeur",
            f"En {request.season}: {season_info['advice']}"
        ],
        alternative_products=[
            {"name": "BIONIC Apple Jelly Premium", "score": 9.2, "reason": "Haute efficacité prouvée pour le cerf"},
            {"name": "Code Blue Doe Estrous", "score": 8.8, "reason": "Excellent pendant le rut"},
            {"name": "Wildlife Research Golden Estrus", "score": 8.5, "reason": "Phéromones naturelles de qualité"}
        ],
        scientific_basis=f"L'analyse est basée sur les études comportementales des {species_info['name']}s, l'efficacité des attractants de type '{species_info['best_attractants'][0]}' et les conditions environnementales ({request.weather}, {request.terrain}).",
        weather_impact=weather_info["impact"],
        seasonal_advice=season_info["advice"]
    )

@api_router.get("/analyze/reports")
async def get_analysis_reports(limit: int = 50):
    """Retourne les rapports d'analyse récents"""
    reports = await db.analysis_reports.find({}, {"_id": 0}).sort("created_at", -1).to_list(limit)
    return {"reports": reports}

@api_router.get("/analyze/reports/{report_id}")
async def get_analysis_report(report_id: str):
    """Retourne un rapport d'analyse spécifique"""
    report = await db.analysis_reports.find_one({"id": report_id}, {"_id": 0})
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@api_router.post("/analyze/consent")
async def submit_email_consent(consent: EmailConsentRequest, background_tasks: BackgroundTasks):
    """Enregistre le consentement email de l'utilisateur et envoie le rapport"""
    consent_record = {
        "id": str(uuid.uuid4()),
        "name": consent.name,
        "email": consent.email,
        "region": consent.region,
        "consent_marketing": consent.consent_marketing,
        "consent_statistics": consent.consent_statistics,
        "report_id": consent.report_id,
        "email_sent": False,
        "email_sent_at": None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.email_consents.insert_one(consent_record)
    
    # Fetch the report to send
    report = await db.analysis_reports.find_one({"id": consent.report_id}, {"_id": 0})
    
    if report and RESEND_API_KEY:
        # Send email in background
        background_tasks.add_task(
            send_analysis_report_email,
            consent.email,
            consent.name,
            report,
            consent_record["id"]
        )
    
    return {
        "success": True,
        "message": "Consentement enregistré. Votre rapport sera envoyé par email.",
        "consent_id": consent_record["id"]
    }

async def send_analysis_report_email(recipient_email: str, recipient_name: str, report: dict, consent_id: str):
    """Envoie le rapport d'analyse par email via Resend"""
    try:
        # Build HTML email content
        product_name = report.get("technical_sheet", {}).get("name", "Produit")
        score = report.get("scoring", {}).get("total_score", 0)
        pastille = report.get("scoring", {}).get("pastille", "yellow")
        pastille_label = report.get("scoring", {}).get("pastille_label", "Modéré")
        
        pastille_colors = {
            "green": "#22c55e",
            "yellow": "#eab308",
            "red": "#ef4444"
        }
        pastille_color = pastille_colors.get(pastille, "#eab308")
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: Arial, sans-serif; background-color: #1a1a1a; color: #ffffff; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #2a2a2a; border-radius: 12px; overflow: hidden;">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #f5a623 0%, #d4920a 100%); padding: 30px; text-align: center;">
                    <h1 style="margin: 0; color: #000000; font-size: 24px;">Chasse Bionic™</h1>
                    <p style="margin: 10px 0 0; color: #333333;">Rapport d'Analyse Scientifique</p>
                </div>
                
                <!-- Content -->
                <div style="padding: 30px;">
                    <p style="color: #cccccc; font-size: 16px;">Bonjour {recipient_name},</p>
                    <p style="color: #cccccc; font-size: 14px;">Voici votre rapport d'analyse pour le produit demandé.</p>
                    
                    <!-- Product Card -->
                    <div style="background-color: #333333; border-radius: 8px; padding: 20px; margin: 20px 0;">
                        <h2 style="margin: 0 0 15px; color: #f5a623; font-size: 20px;">{product_name}</h2>
                        
                        <!-- Score -->
                        <div style="display: flex; align-items: center; margin-bottom: 15px;">
                            <div style="background-color: {pastille_color}; color: #ffffff; font-weight: bold; padding: 8px 16px; border-radius: 20px; font-size: 14px;">
                                Score: {score}/10 - {pastille_label}
                            </div>
                        </div>
                        
                        <!-- Type -->
                        <p style="color: #888888; font-size: 14px; margin: 10px 0;">
                            <strong>Type détecté:</strong> {report.get("technical_sheet", {}).get("detected_type", "Non identifié")}
                        </p>
                    </div>
                    
                    <!-- Conclusion -->
                    <div style="background-color: #333333; border-radius: 8px; padding: 20px; margin: 20px 0;">
                        <h3 style="color: #f5a623; margin: 0 0 10px;">Conclusion</h3>
                        <p style="color: #cccccc; font-size: 14px; line-height: 1.6;">
                            {report.get("conclusion", "Analyse complète disponible dans l'application.")}
                        </p>
                    </div>
                    
                    <!-- CTA Button -->
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="https://lisibilite-pro.preview.emergentagent.com/analyze" 
                           style="background-color: #f5a623; color: #000000; text-decoration: none; padding: 14px 28px; border-radius: 25px; font-weight: bold; display: inline-block;">
                            Voir le rapport complet
                        </a>
                    </div>
                </div>
                
                <!-- Footer -->
                <div style="background-color: #1a1a1a; padding: 20px; text-align: center; border-top: 1px solid #333333;">
                    <p style="color: #666666; font-size: 12px; margin: 0;">
                        © 2025 Chasse Bionic™ - La science valide ce que le terrain confirme.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        params = {
            "from": SENDER_EMAIL,
            "to": [recipient_email],
            "subject": f"🔬 Votre rapport d'analyse Chasse Bionic™ - {product_name}",
            "html": html_content
        }
        
        # Run sync SDK in thread to keep FastAPI non-blocking
        email_result = await asyncio.to_thread(resend.Emails.send, params)
        
        # Update consent record
        await db.email_consents.update_one(
            {"id": consent_id},
            {"$set": {"email_sent": True, "email_sent_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        logging.info(f"Email sent successfully to {recipient_email}, email_id: {email_result.get('id')}")
        
    except Exception as e:
        logging.error(f"Failed to send email to {recipient_email}: {str(e)}")
        # Update consent record with error
        await db.email_consents.update_one(
            {"id": consent_id},
            {"$set": {"email_error": str(e)}}
        )

@api_router.get("/admin/analyze/consents")
async def get_email_consents():
    """Retourne les consentements emails (admin)"""
    consents = await db.email_consents.find({}, {"_id": 0}).sort("created_at", -1).to_list(500)
    return {"consents": consents}

@api_router.get("/admin/analyze/stats")
async def get_analysis_stats():
    """Retourne les statistiques d'analyse (admin)"""
    total_reports = await db.analysis_reports.count_documents({})
    total_consents = await db.email_consents.count_documents({})
    
    # Analyses par catégorie
    reports = await db.analysis_reports.find({}, {"_id": 0}).to_list(1000)
    by_category = {}
    avg_scores = []
    
    for report in reports:
        tech = report.get("technical_sheet", {})
        category = tech.get("detected_type", "unknown")
        by_category[category] = by_category.get(category, 0) + 1
        
        scoring = report.get("scoring", {})
        if scoring.get("total_score"):
            avg_scores.append(scoring["total_score"])
    
    return {
        "total_reports": total_reports,
        "total_consents": total_consents,
        "by_category": by_category,
        "average_score": round(sum(avg_scores) / len(avg_scores), 2) if avg_scores else 0
    }

# ============================================
# ANALYSIS CATEGORIES MANAGEMENT (Menu Catégories)
# ============================================

class AnalysisCategorySubcategory(BaseModel):
    id: str
    name: str
    icon: str = "📦"

class AnalysisCategory(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str
    name: str
    icon: str = "📦"
    order: int = 0
    subcategories: List[AnalysisCategorySubcategory] = []

class AnalysisCategoryCreate(BaseModel):
    id: str
    name: str
    icon: str = "📦"
    order: int = 0
    subcategories: List[AnalysisCategorySubcategory] = []

class AnalysisCategoryUpdate(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None
    order: Optional[int] = None
    subcategories: Optional[List[AnalysisCategorySubcategory]] = None

@api_router.get("/analysis-categories")
async def get_analysis_categories():
    """Retourne toutes les catégories d'analyse (depuis DB ou défaut)"""
    # Check if custom categories exist in DB
    custom_categories = await db.analysis_categories.find({}, {"_id": 0}).sort("order", 1).to_list(100)
    
    if custom_categories and len(custom_categories) > 0:
        return {"categories": custom_categories, "source": "custom"}
    
    return {"categories": DEFAULT_ANALYSIS_CATEGORIES, "source": "default"}

@api_router.get("/analysis-categories/{category_id}")
async def get_analysis_category(category_id: str):
    """Retourne une catégorie spécifique avec ses sous-catégories"""
    # Check custom categories first
    category = await db.analysis_categories.find_one({"id": category_id}, {"_id": 0})
    
    if category:
        return category
    
    # Fallback to default
    for cat in DEFAULT_ANALYSIS_CATEGORIES:
        if cat["id"] == category_id:
            return cat
    
    raise HTTPException(status_code=404, detail="Category not found")

@api_router.post("/admin/analysis-categories")
async def create_analysis_category(category: AnalysisCategoryCreate):
    """Crée une nouvelle catégorie d'analyse (admin)"""
    existing = await db.analysis_categories.find_one({"id": category.id})
    if existing:
        raise HTTPException(status_code=400, detail="Category ID already exists")
    
    category_dict = category.model_dump()
    await db.analysis_categories.insert_one(category_dict)
    
    return {"success": True, "category": category_dict}

@api_router.put("/admin/analysis-categories/{category_id}")
async def update_analysis_category(category_id: str, update: AnalysisCategoryUpdate):
    """Met à jour une catégorie d'analyse (admin)"""
    update_data = {k: v for k, v in update.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    # Check if category exists in DB, if not, copy from default first
    existing = await db.analysis_categories.find_one({"id": category_id})
    
    if not existing:
        # Find in default and copy to DB
        default_cat = None
        for cat in DEFAULT_ANALYSIS_CATEGORIES:
            if cat["id"] == category_id:
                default_cat = cat
                break
        
        if not default_cat:
            raise HTTPException(status_code=404, detail="Category not found")
        
        await db.analysis_categories.insert_one(default_cat.copy())
    
    result = await db.analysis_categories.find_one_and_update(
        {"id": category_id},
        {"$set": update_data},
        return_document=True
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return {"success": True, "category": {k: v for k, v in result.items() if k != "_id"}}

@api_router.delete("/admin/analysis-categories/{category_id}")
async def delete_analysis_category(category_id: str):
    """Supprime une catégorie d'analyse personnalisée (admin)"""
    result = await db.analysis_categories.delete_one({"id": category_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Category not found or is default")
    
    return {"success": True, "message": "Category deleted"}

@api_router.post("/admin/analysis-categories/add-subcategory/{category_id}")
async def add_subcategory(category_id: str, subcategory: AnalysisCategorySubcategory):
    """Ajoute une sous-catégorie à une catégorie (admin)"""
    # Check if category exists in DB, if not, copy from default first
    existing = await db.analysis_categories.find_one({"id": category_id})
    
    if not existing:
        # Find in default and copy to DB
        default_cat = None
        for cat in DEFAULT_ANALYSIS_CATEGORIES:
            if cat["id"] == category_id:
                default_cat = cat.copy()
                break
        
        if not default_cat:
            raise HTTPException(status_code=404, detail="Category not found")
        
        await db.analysis_categories.insert_one(default_cat)
        existing = default_cat
    
    # Check if subcategory ID already exists
    for sub in existing.get("subcategories", []):
        if sub["id"] == subcategory.id:
            raise HTTPException(status_code=400, detail="Subcategory ID already exists")
    
    result = await db.analysis_categories.find_one_and_update(
        {"id": category_id},
        {"$push": {"subcategories": subcategory.model_dump()}},
        return_document=True
    )
    
    return {"success": True, "category": {k: v for k, v in result.items() if k != "_id"}}

@api_router.delete("/admin/analysis-categories/{category_id}/subcategory/{subcategory_id}")
async def remove_subcategory(category_id: str, subcategory_id: str):
    """Supprime une sous-catégorie d'une catégorie (admin)"""
    result = await db.analysis_categories.find_one_and_update(
        {"id": category_id},
        {"$pull": {"subcategories": {"id": subcategory_id}}},
        return_document=True
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return {"success": True, "category": {k: v for k, v in result.items() if k != "_id"}}

@api_router.post("/admin/analysis-categories/init-defaults")
async def initialize_default_categories():
    """Initialise les catégories par défaut dans la base de données (admin)"""
    existing_count = await db.analysis_categories.count_documents({})
    
    if existing_count > 0:
        return {"message": f"Categories already exist ({existing_count} categories)", "initialized": False}
    
    for cat in DEFAULT_ANALYSIS_CATEGORIES:
        await db.analysis_categories.insert_one(cat.copy())
    
    return {"message": f"Initialized {len(DEFAULT_ANALYSIS_CATEGORIES)} categories", "initialized": True}

# ============================================
# AUTOMATIC PRODUCT CATEGORIZATION
# ============================================

class AutoCategorizeRequest(BaseModel):
    product_name: str
    product_description: Optional[str] = ""
    brand: Optional[str] = ""

class AutoCategorizeResult(BaseModel):
    suggested_category: str
    suggested_category_name: str
    suggested_subcategory: Optional[str] = None
    suggested_subcategory_name: Optional[str] = None
    confidence: str  # "high", "medium", "low"
    reasoning: str

@api_router.post("/admin/products/auto-categorize")
async def auto_categorize_product(request: AutoCategorizeRequest):
    """Suggère automatiquement une catégorie pour un produit (admin - utilise l'IA)"""
    if not EMERGENT_LLM_KEY:
        # Fallback to keyword-based categorization
        return await keyword_based_categorization(request)
    
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        # Build category reference for AI
        categories_ref = []
        for cat in DEFAULT_ANALYSIS_CATEGORIES:
            subcats = ", ".join([f"{s['id']} ({s['name']})" for s in cat.get("subcategories", [])])
            categories_ref.append(f"- {cat['id']} ({cat['name']}): {subcats}")
        categories_text = "\n".join(categories_ref)
        
        prompt = f"""Tu es un expert en produits de chasse et attractants. Analyse le produit suivant et suggère la catégorie et sous-catégorie les plus appropriées.

Produit:
- Nom: {request.product_name}
- Description: {request.product_description or 'Non fournie'}
- Marque: {request.brand or 'Non fournie'}

Catégories disponibles:
{categories_text}

Réponds UNIQUEMENT avec un JSON valide (sans markdown, sans texte autour) dans ce format exact:
{{"category_id": "id_categorie", "subcategory_id": "id_sous_categorie_ou_null", "confidence": "high/medium/low", "reasoning": "explication courte"}}

Si tu ne peux pas déterminer la sous-catégorie, mets null pour subcategory_id.
"""
        
        llm = LlmChat(
            api_key=EMERGENT_LLM_KEY, 
            session_id=str(uuid.uuid4()), 
            system_message="Tu es un expert en produits de chasse."
        ).with_model("google", "gemini-2.0-flash")
        
        user_message = UserMessage(text=prompt)
        response = await llm.send_message(user_message)
        
        # Parse AI response
        import json
        response_text = response.strip()
        # Clean markdown if present
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        response_text = response_text.strip()
        
        ai_result = json.loads(response_text)
        
        # Find category and subcategory names
        category_name = ""
        subcategory_name = None
        
        for cat in DEFAULT_ANALYSIS_CATEGORIES:
            if cat["id"] == ai_result.get("category_id"):
                category_name = cat["name"]
                if ai_result.get("subcategory_id"):
                    for sub in cat.get("subcategories", []):
                        if sub["id"] == ai_result.get("subcategory_id"):
                            subcategory_name = sub["name"]
                            break
                break
        
        return {
            "success": True,
            "suggested_category": ai_result.get("category_id", "attractants"),
            "suggested_category_name": category_name or "Attractants",
            "suggested_subcategory": ai_result.get("subcategory_id"),
            "suggested_subcategory_name": subcategory_name,
            "confidence": ai_result.get("confidence", "medium"),
            "reasoning": ai_result.get("reasoning", "Catégorisation basée sur le nom du produit")
        }
        
    except Exception as e:
        logging.error(f"AI categorization failed: {str(e)}, falling back to keyword-based")
        return await keyword_based_categorization(request)

async def keyword_based_categorization(request: AutoCategorizeRequest):
    """Catégorisation basée sur des mots-clés (fallback si pas d'IA)"""
    product_text = f"{request.product_name} {request.product_description} {request.brand}".lower()
    
    # Keyword mappings
    category_keywords = {
        "urines": ["urine", "urin", "estrous", "rut", "doe", "buck", "tarsal", "scent"],
        "attractants": ["attractant", "attractif", "lure", "appât", "gel", "jelly", "spray", "liquide", "powder", "granule", "bloc", "salt"],
        "armes": ["carabine", "rifle", "arc", "bow", "arbalète", "crossbow", "munition", "ammo", "optique", "scope", "silencieux"],
        "cameras": ["camera", "caméra", "trail cam", "cellular", "photo", "video"],
        "appats": ["food", "corn", "maïs", "apple", "pomme", "mineral", "protein", "feed"],
        "leurres": ["decoy", "leurre", "call", "caller", "appeau", "sound"],
        "accessoires": ["treestand", "blind", "affût", "knife", "couteau", "bag", "sac", "light", "lampe"],
        "vetements": ["clothing", "vêtement", "boot", "botte", "glove", "gant", "camo", "scent killer", "odor"],
        "habitat": ["food plot", "seed", "semence", "fertilizer", "engrais"],
        "animaux": ["dog", "chien", "pet", "health", "santé", "nutrition", "gps", "tracker"]
    }
    
    # Find best matching category
    best_category = "attractants"
    best_score = 0
    
    for category, keywords in category_keywords.items():
        score = sum(1 for kw in keywords if kw in product_text)
        if score > best_score:
            best_score = score
            best_category = category
    
    # Find category name
    category_name = "Attractants"
    for cat in DEFAULT_ANALYSIS_CATEGORIES:
        if cat["id"] == best_category:
            category_name = cat["name"]
            break
    
    confidence = "high" if best_score >= 3 else "medium" if best_score >= 1 else "low"
    
    return {
        "success": True,
        "suggested_category": best_category,
        "suggested_category_name": category_name,
        "suggested_subcategory": None,
        "suggested_subcategory_name": None,
        "confidence": confidence,
        "reasoning": f"Catégorisation basée sur {best_score} mot(s)-clé(s) trouvé(s)" if best_score > 0 else "Catégorie par défaut (aucun mot-clé reconnu)"
    }

@api_router.put("/admin/products/{product_id}/categorize")
async def apply_product_category(product_id: str, category_id: str, subcategory_id: Optional[str] = None):
    """Applique une catégorie à un produit (admin)"""
    # Verify category exists
    category_exists = False
    for cat in DEFAULT_ANALYSIS_CATEGORIES:
        if cat["id"] == category_id:
            category_exists = True
            break
    
    if not category_exists:
        custom_cat = await db.analysis_categories.find_one({"id": category_id})
        if not custom_cat:
            raise HTTPException(status_code=404, detail="Category not found")
    
    update_data = {
        "analysis_category": category_id,
        "analysis_subcategory": subcategory_id
    }
    
    result = await db.products.find_one_and_update(
        {"id": product_id},
        {"$set": update_data},
        return_document=True
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {
        "success": True,
        "message": f"Produit catégorisé dans {category_id}" + (f" / {subcategory_id}" if subcategory_id else ""),
        "product_id": product_id
    }

# INTELLIGENT PRODUCT DETECTION SYSTEM
# ============================================

# Base keywords for category detection (évolutif)
CATEGORY_KEYWORDS_DB = {
    "gel": ["gel", "gelée", "jelly", "jam", "pâte", "paste", "apple jelly", "pomme"],
    "bloc": ["bloc", "block", "pierre", "stone", "lick", "lécher", "sel", "salt", "mineral", "trophy rock", "deer cane"],
    "urine": ["urine", "urin", "leurre", "scent", "estrous", "rut", "doe", "buck", "tarsal", "69", "estrus", "oestrus"],
    "granules": ["granules", "granulé", "pellets", "pellet", "sec", "dry", "corn", "maïs", "grain", "acorn", "gland"],
    "liquide": ["liquide", "liquid", "spray", "bombe", "bomb", "vaporisateur", "aerosol", "screamin"],
    "poudre": ["poudre", "powder", "additif", "additive", "dust", "dirt bag"]
}

# Animal type keywords
ANIMAL_KEYWORDS = {
    "deer": ["deer", "cerf", "chevreuil", "whitetail", "buck", "doe", "biche"],
    "moose": ["moose", "orignal", "élan", "bull moose", "cow moose"],
    "bear": ["bear", "ours", "black bear", "grizzly"],
    "elk": ["elk", "wapiti"],
    "wild_boar": ["boar", "sanglier", "hog", "pig"]
}

class SmartDetectionRequest(BaseModel):
    product_name: str
    product_description: Optional[str] = ""
    product_tags: Optional[List[str]] = []

class SmartDetectionResponse(BaseModel):
    detected_category: str
    category_confidence: float
    detected_animal: Optional[str] = None
    animal_confidence: float = 0
    suggested_tags: List[str] = []
    auto_filled_data: Dict[str, Any] = {}
    keywords_matched: List[str] = []

@api_router.post("/analyze/smart-detect", response_model=SmartDetectionResponse)
async def smart_detect_product(request: SmartDetectionRequest):
    """
    Système intelligent de détection automatique du produit.
    Détecte la catégorie, le type d'animal ciblé, et génère des tags automatiquement.
    """
    # Combiner toutes les sources de texte
    text_to_analyze = f"{request.product_name} {request.product_description} {' '.join(request.product_tags)}".lower()
    
    # Récupérer les mots-clés appris depuis la base de données
    learned_keywords = await db.learned_keywords.find({}, {"_id": 0}).to_list(1000)
    
    # Construire un dictionnaire étendu avec les mots-clés appris
    extended_keywords = {cat: list(kws) for cat, kws in CATEGORY_KEYWORDS_DB.items()}
    for learned in learned_keywords:
        cat = learned.get("category")
        keyword = learned.get("keyword")
        if cat in extended_keywords and keyword not in extended_keywords[cat]:
            extended_keywords[cat].append(keyword)
    
    # Détection de catégorie avec scoring
    category_scores = {}
    keywords_matched = []
    
    for category, keywords in extended_keywords.items():
        score = 0
        for keyword in keywords:
            if keyword in text_to_analyze:
                score += 1
                keywords_matched.append(keyword)
        category_scores[category] = score
    
    # Trouver la meilleure catégorie
    best_category = max(category_scores, key=category_scores.get)
    best_score = category_scores[best_category]
    total_matches = sum(category_scores.values())
    category_confidence = (best_score / max(total_matches, 1)) * 100 if total_matches > 0 else 50
    
    # Si aucun match, défaut à "granules"
    if best_score == 0:
        best_category = "granules"
        category_confidence = 30
    
    # Détection du type d'animal
    animal_scores = {}
    for animal, keywords in ANIMAL_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_to_analyze)
        animal_scores[animal] = score
    
    best_animal = max(animal_scores, key=animal_scores.get)
    animal_score = animal_scores[best_animal]
    animal_confidence = (animal_score / max(sum(animal_scores.values()), 1)) * 100 if animal_score > 0 else 0
    
    if animal_score == 0:
        best_animal = None
        animal_confidence = 0
    
    # Générer des tags suggérés
    suggested_tags = list(set(keywords_matched))
    if best_animal:
        suggested_tags.append(best_animal)
    
    # Données pré-remplies basées sur la catégorie
    bionic = BIONIC_PRODUCTS.get(best_category, BIONIC_PRODUCTS["granules"])
    auto_filled = {
        "category": best_category,
        "estimated_attraction_days": bionic.get("attraction_days", 10),
        "rainproof_typical": bionic.get("rainproof", False),
        "suggested_price_range": {"min": bionic["price"] * 0.7, "max": bionic["price"] * 1.3}
    }
    
    return SmartDetectionResponse(
        detected_category=best_category,
        category_confidence=round(category_confidence, 1),
        detected_animal=best_animal,
        animal_confidence=round(animal_confidence, 1),
        suggested_tags=suggested_tags[:10],
        auto_filled_data=auto_filled,
        keywords_matched=keywords_matched
    )

class LearnKeywordRequest(BaseModel):
    keyword: str
    category: str
    source: str = "user_correction"  # user_correction, auto_learn, admin

@api_router.post("/analyze/learn-keyword")
async def learn_new_keyword(request: LearnKeywordRequest):
    """
    Apprentissage évolutif: ajoute un nouveau mot-clé à la base de données.
    Permet au système de s'améliorer avec le temps.
    """
    if request.category not in CATEGORY_KEYWORDS_DB:
        raise HTTPException(status_code=400, detail="Invalid category")
    
    # Vérifier si le mot-clé existe déjà
    existing = await db.learned_keywords.find_one({
        "keyword": request.keyword.lower(),
        "category": request.category
    })
    
    if existing:
        # Incrémenter le compteur d'utilisation
        await db.learned_keywords.update_one(
            {"keyword": request.keyword.lower(), "category": request.category},
            {"$inc": {"usage_count": 1}, "$set": {"last_used": datetime.now(timezone.utc).isoformat()}}
        )
        return {"success": True, "message": "Keyword usage updated", "new": False}
    
    # Créer un nouveau mot-clé appris
    keyword_doc = {
        "id": str(uuid.uuid4()),
        "keyword": request.keyword.lower(),
        "category": request.category,
        "source": request.source,
        "usage_count": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_used": datetime.now(timezone.utc).isoformat()
    }
    
    await db.learned_keywords.insert_one(keyword_doc)
    
    return {"success": True, "message": "New keyword learned", "new": True, "keyword_id": keyword_doc["id"]}

@api_router.get("/analyze/learned-keywords")
async def get_learned_keywords():
    """Retourne tous les mots-clés appris par le système"""
    keywords = await db.learned_keywords.find({}, {"_id": 0}).sort("usage_count", -1).to_list(500)
    
    # Grouper par catégorie
    by_category = {}
    for kw in keywords:
        cat = kw.get("category", "unknown")
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(kw)
    
    return {
        "total": len(keywords),
        "by_category": by_category,
        "base_keywords": CATEGORY_KEYWORDS_DB
    }

@api_router.get("/analyze/top-products/{category}")
async def get_top_products_by_category(category: str, limit: int = 3):
    """
    Retourne les meilleurs produits d'une catégorie + BIONIC.
    Utilisé pour l'affichage post-analyse.
    """
    # Récupérer les produits de la base de données avec ce format/catégorie
    products = await db.products.find(
        {"$or": [{"category": category}, {"product_format": category}]},
        {"_id": 0}
    ).sort("score", -1).to_list(limit)
    
    # Récupérer le produit BIONIC correspondant
    bionic = BIONIC_PRODUCTS.get(category, BIONIC_PRODUCTS["granules"])
    bionic_product = {
        "id": f"bionic_{category}",
        "name": bionic["name"],
        "brand": "BIONIC™",
        "price": bionic["price"],
        "price_with_shipping": bionic["price_with_shipping"],
        "score": bionic["score"] * 10,  # Convertir sur 100
        "image_url": bionic["image_url"],
        "attraction_days": bionic["attraction_days"],
        "rainproof": bionic["rainproof"],
        "feed_proof": bionic["feed_proof"],
        "certified": bionic["certified"],
        "buy_link": bionic["buy_link"],
        "is_bionic": True,
        "advantages": [
            "Certification alimentaire ACIA/CFIA",
            "Formule scientifiquement optimisée",
            f"Durée d'attraction: {bionic['attraction_days']} jours",
            "Résistant aux intempéries" if bionic["rainproof"] else "Formule concentrée",
            "100% Feed-Proof"
        ]
    }
    
    # Récupérer les concurrents de la base interne
    competitors = COMPETITOR_PRODUCTS.get(category, [])
    
    # Combiner et trier tous les produits
    all_products = []
    
    # Ajouter les produits de la DB
    for p in products:
        if p.get("brand", "").upper() != "BIONIC™":
            all_products.append({
                **p,
                "is_bionic": False,
                "score": p.get("score", 70),
                "advantages": [
                    f"Prix: ${p.get('price', 0)}",
                    f"Score: {p.get('score', 70)}/100",
                    p.get("description", "")[:50] + "..." if p.get("description") else ""
                ]
            })
    
    # Ajouter les concurrents internes
    for c in competitors:
        all_products.append({
            "id": f"competitor_{c['name'][:10]}",
            "name": c["name"],
            "brand": c["brand"],
            "price": c["price"],
            "price_with_shipping": c["price_with_shipping"],
            "score": c["score"] * 10,
            "image_url": c["image_url"],
            "attraction_days": c["attraction_days"],
            "rainproof": c["rainproof"],
            "feed_proof": c["feed_proof"],
            "certified": c.get("certified", False),
            "buy_link": c["buy_link"],
            "is_bionic": False,
            "advantages": [
                f"Prix: ${c['price']}",
                f"Durée: {c['attraction_days']} jours",
                f"Score: {c['score']}/10"
            ]
        })
    
    # Trier par score et prendre les meilleurs
    all_products.sort(key=lambda x: x.get("score", 0), reverse=True)
    top_competitors = all_products[:limit - 1] if limit > 1 else []
    
    return {
        "bionic": bionic_product,
        "top_competitors": top_competitors,
        "total_in_category": len(all_products) + 1
    }

class QuickAnalysisRequest(BaseModel):
    product_id: Optional[str] = None
    product_name: str
    detected_category: str
    session_id: str

@api_router.post("/analyze/quick")
async def quick_analysis(request: QuickAnalysisRequest):
    """
    Analyse rapide pré-remplie basée sur la détection automatique.
    Prépare l'analyse sans nécessiter d'input utilisateur supplémentaire.
    """
    # Créer l'analyseur
    analyzer = ProductAnalyzer(EMERGENT_LLM_KEY)
    
    # Lancer l'analyse
    report = await analyzer.analyze_product(request.product_name, request.detected_category)
    
    # Récupérer les meilleurs produits pour la comparaison
    top_products_response = await get_top_products_by_category(request.detected_category, 3)
    
    # Sauvegarder le rapport
    report_dict = report.model_dump()
    report_dict['created_at'] = report_dict['created_at'].isoformat()
    report_dict['session_id'] = request.session_id
    report_dict['quick_analysis'] = True
    
    await db.analysis_reports.insert_one(report_dict.copy())
    
    # Nettoyer pour le retour
    if '_id' in report_dict:
        del report_dict['_id']
    
    return {
        "report": report_dict,
        "display_products": {
            "analyzed": {
                "name": request.product_name,
                "score": report.scoring.total_score,
                "pastille": report.scoring.pastille,
                "category": request.detected_category
            },
            "bionic": top_products_response["bionic"],
            "top_competitors": top_products_response["top_competitors"]
        }
    }

# ============================================
# PRODUCT DISCOVERY SYSTEM - Détection automatique
# ============================================

# Initialiser le service de découverte
discovery_service = None

async def get_discovery_service():
    global discovery_service
    if discovery_service is None:
        discovery_service = ProductDiscoveryService(EMERGENT_LLM_KEY, db)
    return discovery_service

# --- Scanner Configuration ---

class ScannerConfigUpdate(BaseModel):
    frequency: Optional[Literal["realtime", "daily", "weekly", "manual"]] = None
    priority_sources_enabled: Optional[bool] = None
    web_search_enabled: Optional[bool] = None
    auto_translate: Optional[bool] = None
    min_score_threshold: Optional[int] = None

@api_router.get("/discovery/config")
async def get_scanner_config():
    """Récupère la configuration du scanner"""
    service = await get_discovery_service()
    config = await service.get_config()
    return config.model_dump()

@api_router.put("/discovery/config")
async def update_scanner_config(updates: ScannerConfigUpdate):
    """Met à jour la configuration du scanner"""
    service = await get_discovery_service()
    update_dict = {k: v for k, v in updates.model_dump().items() if v is not None}
    config = await service.update_config(update_dict)
    return {"success": True, "config": config.model_dump()}

# --- Manual Scan ---

class ManualScanRequest(BaseModel):
    urls: Optional[List[str]] = None
    use_priority_sources: bool = True
    use_web_search: bool = False

@api_router.post("/discovery/scan")
async def trigger_manual_scan(request: ManualScanRequest, background_tasks: BackgroundTasks):
    """Déclenche un scan manuel"""
    service = await get_discovery_service()
    config = await service.get_config()
    
    if config.is_running:
        raise HTTPException(status_code=400, detail="Un scan est déjà en cours")
    
    # Marquer comme en cours
    await service.update_config({"is_running": True})
    
    # Lancer le scan en arrière-plan
    async def run_scan():
        try:
            products_found = []
            urls_to_scan = request.urls or []
            
            # Ajouter les sources prioritaires
            if request.use_priority_sources:
                for source in PRIORITY_SOURCES:
                    urls_to_scan.append(source["url"])
            
            # Scanner chaque URL
            for url in urls_to_scan:
                source_name = next(
                    (s["name"] for s in PRIORITY_SOURCES if s["url"] in url),
                    "Web"
                )
                found = await service.scan_url(url, source_name)
                products_found.extend(found)
            
            # Mettre à jour les stats
            await service.update_config({
                "is_running": False,
                "last_scan": datetime.now(timezone.utc).isoformat(),
                "products_found_last_scan": len(products_found)
            })
            
            # Notification de fin de scan
            if products_found:
                notification = AdminNotification(
                    type="scan_complete",
                    title=f"Scan terminé: {len(products_found)} nouveaux produits",
                    message=f"Le scan a trouvé {len(products_found)} nouveaux produits en attente de validation."
                )
                doc = notification.model_dump()
                doc['created_at'] = doc['created_at'].isoformat()
                await db.admin_notifications.insert_one(doc)
                
        except Exception as e:
            await service.update_config({"is_running": False})
            notification = AdminNotification(
                type="error",
                title="Erreur lors du scan",
                message=str(e)
            )
            doc = notification.model_dump()
            doc['created_at'] = doc['created_at'].isoformat()
            await db.admin_notifications.insert_one(doc)
    
    background_tasks.add_task(run_scan)
    
    return {
        "success": True,
        "message": "Scan démarré en arrière-plan",
        "urls_count": len(request.urls or []) + (len(PRIORITY_SOURCES) if request.use_priority_sources else 0)
    }

@api_router.get("/discovery/scan/status")
async def get_scan_status():
    """Retourne le statut du scan en cours"""
    service = await get_discovery_service()
    config = await service.get_config()
    return {
        "is_running": config.is_running,
        "last_scan": config.last_scan,
        "products_found_last_scan": config.products_found_last_scan,
        "total_products_found": config.total_products_found
    }

# --- Discovered Products ---

@api_router.get("/discovery/products")
async def get_discovered_products(
    status: Optional[str] = None,
    category: Optional[str] = None,
    min_score: Optional[int] = None,
    limit: int = 50,
    skip: int = 0
):
    """Liste les produits découverts"""
    query = {}
    if status:
        query["status"] = status
    if category:
        query["category"] = category
    if min_score:
        query["score_total"] = {"$gte": min_score}
    
    products = await db.discovered_products.find(
        query,
        {"_id": 0}
    ).sort("discovered_at", -1).skip(skip).limit(limit).to_list(limit)
    
    total = await db.discovered_products.count_documents(query)
    
    # Stats par statut
    stats = {
        "pending": await db.discovered_products.count_documents({"status": "pending"}),
        "approved": await db.discovered_products.count_documents({"status": "approved"}),
        "rejected": await db.discovered_products.count_documents({"status": "rejected"}),
        "active": await db.discovered_products.count_documents({"status": "active"})
    }
    
    return {
        "products": products,
        "total": total,
        "stats": stats
    }

@api_router.get("/discovery/products/{product_id}")
async def get_discovered_product(product_id: str):
    """Récupère un produit découvert par ID"""
    product = await db.discovered_products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    return product

class ProductApprovalRequest(BaseModel):
    action: Literal["approve", "reject"]
    rejection_reason: Optional[str] = None

@api_router.post("/discovery/products/{product_id}/approve")
async def approve_or_reject_product(product_id: str, request: ProductApprovalRequest):
    """Approuve ou rejette un produit découvert"""
    product = await db.discovered_products.find_one({"id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    now = datetime.now(timezone.utc).isoformat()
    
    if request.action == "approve":
        # Mettre à jour le statut
        await db.discovered_products.update_one(
            {"id": product_id},
            {
                "$set": {
                    "status": "approved",
                    "approved_at": now
                }
            }
        )
        
        # Créer le produit dans la collection principale
        new_product = {
            "id": str(uuid.uuid4()),
            "name": product.get("name_fr", ""),
            "name_en": product.get("name_en", ""),
            "brand": product.get("brand", ""),
            "category": product.get("category", "attractant"),
            "description": product.get("description_fr", ""),
            "description_en": product.get("description_en", ""),
            "price": product.get("price_regular", 0),
            "price_promo": product.get("price_promo"),
            "formats": product.get("formats", []),
            "image_url": product.get("main_image_url", ""),
            "additional_images": product.get("image_urls", []),
            "score": round(product.get("score_total", 0)),
            "target_species": product.get("target_species", []),
            "ingredients": product.get("ingredients", []),
            "advantages": product.get("advantages_fr", []),
            "advantages_en": product.get("advantages_en", []),
            "tags": product.get("tags_fr", []),
            "tags_en": product.get("tags_en", []),
            "source_url": product.get("source_url", ""),
            "source_name": product.get("source_name", ""),
            "discovered_product_id": product_id,
            "in_stock": True,
            "buy_type": "affiliate",
            "affiliate_link": product.get("source_url", ""),
            "created_at": now,
            "auto_imported": True
        }
        
        await db.products.insert_one(new_product)
        
        # Mettre à jour le statut à "active"
        await db.discovered_products.update_one(
            {"id": product_id},
            {"$set": {"status": "active"}}
        )
        
        return {
            "success": True,
            "message": "Produit approuvé et activé",
            "product_id": new_product["id"]
        }
    
    else:  # reject
        await db.discovered_products.update_one(
            {"id": product_id},
            {
                "$set": {
                    "status": "rejected",
                    "rejected_at": now,
                    "rejection_reason": request.rejection_reason
                }
            }
        )
        
        return {
            "success": True,
            "message": "Produit rejeté"
        }

# --- Admin Notifications (Boîte aux lettres IA) ---

@api_router.get("/discovery/notifications")
async def get_admin_notifications(
    unread_only: bool = False,
    notification_type: Optional[str] = None,
    limit: int = 50
):
    """Liste les notifications admin"""
    query = {}
    if unread_only:
        query["is_read"] = False
    if notification_type:
        query["type"] = notification_type
    
    notifications = await db.admin_notifications.find(
        query,
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    unread_count = await db.admin_notifications.count_documents({"is_read": False})
    
    return {
        "notifications": notifications,
        "unread_count": unread_count
    }

@api_router.post("/discovery/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str):
    """Marque une notification comme lue"""
    result = await db.admin_notifications.update_one(
        {"id": notification_id},
        {"$set": {"is_read": True}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Notification non trouvée")
    
    return {"success": True}

@api_router.post("/discovery/notifications/read-all")
async def mark_all_notifications_read():
    """Marque toutes les notifications comme lues"""
    result = await db.admin_notifications.update_many(
        {"is_read": False},
        {"$set": {"is_read": True}}
    )
    
    return {"success": True, "count": result.modified_count}

@api_router.delete("/discovery/notifications/{notification_id}")
async def delete_notification(notification_id: str):
    """Supprime une notification"""
    result = await db.admin_notifications.delete_one({"id": notification_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Notification non trouvée")
    
    return {"success": True}

# --- Priority Sources Management ---

@api_router.get("/discovery/sources")
async def get_priority_sources():
    """Liste les sources prioritaires"""
    # Récupérer les sources personnalisées de la DB
    custom_sources = await db.priority_sources.find({}, {"_id": 0}).to_list(100)
    
    # Combiner avec les sources par défaut
    all_sources = list(PRIORITY_SOURCES) + custom_sources
    
    return {"sources": all_sources}

class AddSourceRequest(BaseModel):
    name: str
    url: str
    type: str = "store"

@api_router.post("/discovery/sources")
async def add_priority_source(request: AddSourceRequest):
    """Ajoute une source prioritaire"""
    source = {
        "id": str(uuid.uuid4()),
        "name": request.name,
        "url": request.url,
        "type": request.type,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.priority_sources.insert_one(source)
    
    return {"success": True, "source": source}

@api_router.delete("/discovery/sources/{source_id}")
async def remove_priority_source(source_id: str):
    """Supprime une source prioritaire personnalisée"""
    result = await db.priority_sources.delete_one({"id": source_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Source non trouvée")
    
    return {"success": True}

# --- Quick Add Product (Manual) ---

class QuickAddProductRequest(BaseModel):
    name_fr: str
    brand: str = ""
    category: str = "attractant"
    description_fr: str = ""
    price_regular: float = 0
    image_url: str = ""
    source_url: str = ""
    target_species: List[str] = []
    auto_translate: bool = True

@api_router.post("/discovery/quick-add")
async def quick_add_product(request: QuickAddProductRequest):
    """Ajoute rapidement un produit manuellement"""
    service = await get_discovery_service()
    
    # Créer le produit découvert
    product = DiscoveredProduct(
        name_fr=request.name_fr,
        brand=request.brand,
        category=request.category,
        description_fr=request.description_fr,
        price_regular=request.price_regular,
        main_image_url=request.image_url,
        image_urls=[request.image_url] if request.image_url else [],
        source_url=request.source_url,
        source_name="Manual",
        target_species=request.target_species or ["deer"],
        status="pending"
    )
    
    # Traduire si demandé
    if request.auto_translate:
        product = await service.translate_product(product)
    
    # Calculer le score
    product = service.calculate_score(product)
    
    # Générer le hash
    product.content_hash = service._generate_content_hash(
        product.name_fr, product.brand, "Manual"
    )
    
    # Sauvegarder
    await service.save_product(product)
    await service.create_notification(product)
    
    return {
        "success": True,
        "product": product.model_dump(),
        "message": "Produit ajouté et en attente de validation"
    }

# ============================================
# REFERRAL SYSTEM - Système de parrainage
# ============================================

# Initialiser le service de parrainage
referral_service = None

async def get_referral_service():
    global referral_service
    if referral_service is None:
        base_url = os.environ.get('FRONTEND_URL', 'https://scent-science.com')
        referral_service = ReferralService(db, base_url)
    return referral_service

# --- User Referral Endpoints ---

class CreateReferralUserRequest(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None

@api_router.post("/referral/register")
async def create_referral_account(request: CreateReferralUserRequest):
    """Crée un compte de parrainage pour un utilisateur"""
    service = await get_referral_service()
    
    try:
        user = await service.create_referral_user(
            name=request.name,
            email=request.email,
            phone=request.phone
        )
        return {
            "success": True,
            "user": user.model_dump(),
            "referral_code": user.referral_code,
            "referral_link": user.referral_link
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/referral/user/{email}")
async def get_referral_user_by_email(email: str):
    """Récupère un compte de parrainage par email"""
    service = await get_referral_service()
    user = await service.get_user_by_email(email)
    
    if not user:
        raise HTTPException(status_code=404, detail="Compte non trouvé")
    
    return user

@api_router.get("/referral/code/{code}")
async def get_referral_by_code(code: str):
    """Récupère les infos d'un code de parrainage"""
    service = await get_referral_service()
    user = await service.get_user_by_code(code)
    
    if not user:
        raise HTTPException(status_code=404, detail="Code invalide")
    
    return {
        "valid": True,
        "referrer_name": user.get("name"),
        "discount_percent": user.get("current_discount_percent", 5),
        "tier": user.get("tier", "bronze")
    }

@api_router.get("/referral/dashboard/{user_id}")
async def get_referral_dashboard(user_id: str):
    """Récupère le tableau de bord de parrainage d'un utilisateur"""
    service = await get_referral_service()
    dashboard = await service.get_user_dashboard(user_id)
    
    if not dashboard:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    return dashboard

# --- Tracking ---

class TrackClickRequest(BaseModel):
    code: str
    source: str = "direct"

@api_router.post("/referral/track-click")
async def track_referral_click(request: TrackClickRequest):
    """Enregistre un clic sur un lien de parrainage"""
    service = await get_referral_service()
    success = await service.track_click(request.code, request.source)
    
    return {"success": success}

class RegisterInviteeRequest(BaseModel):
    referral_code: str
    invitee_email: str
    invitee_name: Optional[str] = None

@api_router.post("/referral/register-invitee")
async def register_invitee(request: RegisterInviteeRequest):
    """Enregistre un nouvel invité"""
    service = await get_referral_service()
    invite = await service.register_invitee(
        request.referral_code,
        request.invitee_email,
        request.invitee_name
    )
    
    if not invite:
        return {"success": False, "message": "Code invalide ou invité déjà enregistré"}
    
    return {"success": True, "invite_id": invite.id}

class RecordPurchaseRequest(BaseModel):
    referral_code: str
    invitee_email: str
    order_amount: float
    order_id: str

@api_router.post("/referral/record-purchase")
async def record_referral_purchase(request: RecordPurchaseRequest):
    """Enregistre un achat d'un invité"""
    service = await get_referral_service()
    result = await service.record_purchase(
        request.referral_code,
        request.invitee_email,
        request.order_amount,
        request.order_id
    )
    
    return result

# --- Share Tools ---

@api_router.get("/referral/share-messages/{user_id}")
async def get_share_messages(user_id: str, lang: str = "fr"):
    """Récupère les messages de partage personnalisés"""
    service = await get_referral_service()
    user = await db.referral_users.find_one({"id": user_id}, {"_id": 0})
    
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    discount = user.get("current_discount_percent", 5)
    messages = service.get_share_messages(discount, lang)
    
    return {
        "referral_link": user.get("referral_link"),
        "referral_code": user.get("referral_code"),
        "discount_percent": discount,
        "platforms": SOCIAL_PLATFORMS,
        "messages": messages
    }

# --- Discounts Calculation ---

class CalculateDiscountRequest(BaseModel):
    referral_code: Optional[str] = None
    product_id: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None

@api_router.post("/referral/calculate-discount")
async def calculate_discount(request: CalculateDiscountRequest):
    """Calcule le rabais final applicable"""
    service = await get_referral_service()
    
    # Rabais de parrainage de base
    base_discount = 0
    if request.referral_code:
        user = await service.get_user_by_code(request.referral_code)
        if user:
            base_discount = user.get("current_discount_percent", 0)
    
    # Rabais produit
    product_discounts = await service.get_product_discounts(
        request.product_id,
        request.category,
        request.brand
    )
    
    # Promotions saisonnières
    seasonal_promos = await service.get_active_promotions()
    
    # Calculer le total
    result = service.calculate_final_discount(
        base_discount,
        product_discounts,
        seasonal_promos
    )
    
    return result

# --- Admin: Discount Tiers ---

@api_router.get("/referral/admin/tiers")
async def get_discount_tiers():
    """Récupère la configuration des niveaux de rabais"""
    service = await get_referral_service()
    tiers = await service.get_discount_tiers()
    return {"tiers": tiers}

class UpdateTiersRequest(BaseModel):
    tiers: Dict[str, Any]

@api_router.put("/referral/admin/tiers")
async def update_discount_tiers(request: UpdateTiersRequest):
    """Met à jour les niveaux de rabais"""
    service = await get_referral_service()
    tiers = await service.update_discount_tiers(request.tiers)
    return {"success": True, "tiers": tiers}

# --- Admin: Seasonal Promotions ---

class CreatePromotionRequest(BaseModel):
    name: str
    season_type: str
    start_date: str
    end_date: str
    additional_discount_percent: int = 0
    applies_to_all: bool = True
    applies_to_categories: List[str] = []
    applies_to_products: List[str] = []

@api_router.post("/referral/admin/promotions")
async def create_seasonal_promotion(request: CreatePromotionRequest):
    """Crée une promotion saisonnière"""
    promo = SeasonalPromotion(
        name=request.name,
        season_type=SeasonType(request.season_type),
        start_date=datetime.fromisoformat(request.start_date),
        end_date=datetime.fromisoformat(request.end_date),
        additional_discount_percent=request.additional_discount_percent,
        applies_to_all=request.applies_to_all,
        applies_to_categories=request.applies_to_categories,
        applies_to_products=request.applies_to_products
    )
    
    doc = promo.model_dump()
    doc['start_date'] = doc['start_date'].isoformat()
    doc['end_date'] = doc['end_date'].isoformat()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.seasonal_promotions.insert_one(doc)
    
    return {"success": True, "promotion": doc}

@api_router.get("/referral/admin/promotions")
async def get_all_promotions():
    """Liste toutes les promotions"""
    promos = await db.seasonal_promotions.find({}, {"_id": 0}).sort("start_date", -1).to_list(100)
    return {"promotions": promos}

@api_router.put("/referral/admin/promotions/{promo_id}")
async def update_promotion(promo_id: str, is_active: bool):
    """Active/désactive une promotion"""
    result = await db.seasonal_promotions.update_one(
        {"id": promo_id},
        {"$set": {"is_active": is_active}}
    )
    return {"success": result.modified_count > 0}

@api_router.delete("/referral/admin/promotions/{promo_id}")
async def delete_promotion(promo_id: str):
    """Supprime une promotion"""
    result = await db.seasonal_promotions.delete_one({"id": promo_id})
    return {"success": result.deleted_count > 0}

# --- Admin: Product Discounts ---

class CreateProductDiscountRequest(BaseModel):
    discount_type: str  # category, brand, product
    target_id: str
    target_name: str
    discount_percent: int
    reason: str = ""
    start_date: Optional[str] = None
    end_date: Optional[str] = None

@api_router.post("/referral/admin/product-discounts")
async def create_product_discount(request: CreateProductDiscountRequest):
    """Crée un rabais spécifique produit/catégorie"""
    discount = ProductDiscount(
        discount_type=request.discount_type,
        target_id=request.target_id,
        target_name=request.target_name,
        discount_percent=request.discount_percent,
        reason=request.reason,
        start_date=datetime.fromisoformat(request.start_date) if request.start_date else None,
        end_date=datetime.fromisoformat(request.end_date) if request.end_date else None
    )
    
    doc = discount.model_dump()
    if doc.get('start_date'):
        doc['start_date'] = doc['start_date'].isoformat()
    if doc.get('end_date'):
        doc['end_date'] = doc['end_date'].isoformat()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.product_discounts.insert_one(doc)
    
    return {"success": True, "discount": doc}

@api_router.get("/referral/admin/product-discounts")
async def get_all_product_discounts():
    """Liste tous les rabais produit"""
    discounts = await db.product_discounts.find({}, {"_id": 0}).to_list(100)
    return {"discounts": discounts}

@api_router.delete("/referral/admin/product-discounts/{discount_id}")
async def delete_product_discount(discount_id: str):
    """Supprime un rabais produit"""
    result = await db.product_discounts.delete_one({"id": discount_id})
    return {"success": result.deleted_count > 0}

# --- Admin: Partner Management ---

@api_router.get("/referral/admin/partners")
async def get_all_partners():
    """Liste tous les partenaires privilégiés"""
    partners = await db.referral_users.find(
        {"is_partner": True},
        {"_id": 0}
    ).to_list(100)
    return {"partners": partners}

@api_router.get("/referral/admin/partner-applications")
async def get_partner_applications(status: str = None):
    """Liste les demandes de partenariat"""
    query = {}
    if status:
        query["status"] = status
    
    applications = await db.partner_applications.find(
        query,
        {"_id": 0}
    ).sort("submitted_at", -1).to_list(100)
    
    return {"applications": applications}

class SubmitPartnerApplicationRequest(BaseModel):
    user_id: str
    business_name: str
    business_type: str
    website: Optional[str] = None
    social_media: Dict[str, str] = {}
    estimated_monthly_volume: float = 0
    motivation: str = ""

@api_router.post("/referral/apply-partner")
async def submit_partner_application(request: SubmitPartnerApplicationRequest):
    """Soumet une demande de partenariat"""
    # Vérifier que l'utilisateur existe
    user = await db.referral_users.find_one({"id": request.user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Vérifier qu'il n'y a pas déjà une demande en attente
    existing = await db.partner_applications.find_one({
        "user_id": request.user_id,
        "status": "pending"
    })
    if existing:
        raise HTTPException(status_code=400, detail="Une demande est déjà en attente")
    
    application = PartnerApplication(
        user_id=request.user_id,
        business_name=request.business_name,
        business_type=request.business_type,
        website=request.website,
        social_media=request.social_media,
        estimated_monthly_volume=request.estimated_monthly_volume,
        existing_referrals=user.get("total_buyers", 0),
        motivation=request.motivation
    )
    
    doc = application.model_dump()
    doc['submitted_at'] = doc['submitted_at'].isoformat()
    
    await db.partner_applications.insert_one(doc)
    
    return {"success": True, "application_id": application.id}

class ApprovePartnerRequest(BaseModel):
    commission_rate: float = 10

@api_router.post("/referral/admin/partners/{application_id}/approve")
async def approve_partner_application(application_id: str, request: ApprovePartnerRequest):
    """Approuve une demande de partenariat"""
    service = await get_referral_service()
    result = await service.approve_partner(application_id, request.commission_rate)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result

class RejectPartnerRequest(BaseModel):
    reason: str

@api_router.post("/referral/admin/partners/{application_id}/reject")
async def reject_partner_application(application_id: str, request: RejectPartnerRequest):
    """Rejette une demande de partenariat"""
    service = await get_referral_service()
    result = await service.reject_partner(application_id, request.reason)
    
    return result

@api_router.put("/referral/admin/partners/{user_id}/commission")
async def update_partner_commission(user_id: str, commission_rate: float):
    """Met à jour le taux de commission d'un partenaire"""
    result = await db.referral_users.update_one(
        {"id": user_id, "is_partner": True},
        {"$set": {"partner_commission_rate": commission_rate}}
    )
    
    return {"success": result.modified_count > 0}

# --- Admin: Dashboard ---

@api_router.get("/referral/admin/dashboard")
async def get_referral_admin_dashboard():
    """Récupère le tableau de bord admin du programme de parrainage"""
    service = await get_referral_service()
    dashboard = await service.get_admin_dashboard()
    
    return dashboard

@api_router.get("/referral/admin/users")
async def get_all_referral_users(
    tier: str = None,
    is_partner: bool = None,
    limit: int = 50,
    skip: int = 0
):
    """Liste tous les utilisateurs du programme de parrainage"""
    query = {}
    if tier:
        query["tier"] = tier
    if is_partner is not None:
        query["is_partner"] = is_partner
    
    users = await db.referral_users.find(
        query,
        {"_id": 0}
    ).sort("total_buyers", -1).skip(skip).limit(limit).to_list(limit)
    
    total = await db.referral_users.count_documents(query)
    
    return {"users": users, "total": total}

# ============================================
# SCHEDULER SERVICE ROUTES
# ============================================

from services.scheduler_service import get_scheduler, SchedulerService

# Scheduler instance (initialized on startup)
scheduler_service: SchedulerService = None

@app.on_event("startup")
async def startup_event():
    """Initialize scheduler on startup"""
    global scheduler_service
    scheduler_service = get_scheduler(db)
    await scheduler_service.start()
    logger.info("✅ Scheduler service initialized")

class ScheduleScanRequest(BaseModel):
    frequency: str = "daily"  # hourly, daily, weekly, twice_daily, manual
    sources: Optional[List[Dict[str, str]]] = None

@api_router.post("/scheduler/scan/schedule")
async def schedule_product_scan(request: ScheduleScanRequest):
    """Configure et planifie le scanner automatique de produits"""
    global scheduler_service
    if not scheduler_service:
        raise HTTPException(status_code=500, detail="Scheduler not initialized")
    
    result = await scheduler_service.schedule_product_scan(
        frequency=request.frequency,
        sources=request.sources
    )
    return {"success": True, **result}

@api_router.post("/scheduler/scan/stop")
async def stop_product_scan():
    """Arrête le scanner automatique"""
    global scheduler_service
    if not scheduler_service:
        raise HTTPException(status_code=500, detail="Scheduler not initialized")
    
    result = await scheduler_service.stop_product_scan()
    return {"success": result}

@api_router.post("/scheduler/scan/run-now")
async def run_scan_now():
    """Force un scan immédiat"""
    global scheduler_service
    if not scheduler_service:
        raise HTTPException(status_code=500, detail="Scheduler not initialized")
    
    result = await scheduler_service.run_scan_now()
    return {"success": True, "scan_result": result}

@api_router.get("/scheduler/status")
async def get_scheduler_status():
    """Retourne le statut du scheduler"""
    global scheduler_service
    if not scheduler_service:
        return {"running": False, "jobs_count": 0, "jobs": []}
    
    return scheduler_service.get_status()

@api_router.get("/scheduler/scan/history")
async def get_scan_history(limit: int = 10):
    """Retourne l'historique des scans"""
    global scheduler_service
    if not scheduler_service:
        return {"history": []}
    
    history = await scheduler_service.get_scan_history(limit)
    return {"history": history}

class ScheduleReportRequest(BaseModel):
    job_id: str
    frequency: str = "weekly"  # daily, weekly, monthly
    report_type: str = "sales"  # sales, analytics, referral, inventory

@api_router.post("/scheduler/report/schedule")
async def schedule_report(request: ScheduleReportRequest):
    """Planifie la génération automatique de rapports"""
    global scheduler_service
    if not scheduler_service:
        raise HTTPException(status_code=500, detail="Scheduler not initialized")
    
    result = await scheduler_service.schedule_report(
        job_id=request.job_id,
        frequency=request.frequency,
        report_type=request.report_type
    )
    return {"success": True, "job_id": request.job_id, "next_run": str(result.get("next_run"))}

@api_router.get("/scheduler/reports")
async def get_generated_reports(limit: int = 20):
    """Liste les rapports générés"""
    reports = await db.reports.find({}, {"_id": 0}).sort("generated_at", -1).limit(limit).to_list(limit)
    return {"reports": reports}

# ============================================
# ADVANCED PRODUCT FILTERING
# ============================================

class ProductFilterRequest(BaseModel):
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
    sort_by: str = "rank"
    sort_order: str = "asc"
    limit: int = 50
    offset: int = 0

@api_router.post("/products/filter")
async def filter_products(request: ProductFilterRequest):
    """Filtre avancé des produits"""
    query = {}
    
    # Text search
    if request.search:
        query["$or"] = [
            {"name": {"$regex": request.search, "$options": "i"}},
            {"brand": {"$regex": request.search, "$options": "i"}},
            {"description": {"$regex": request.search, "$options": "i"}}
        ]
    
    # Category filters
    if request.category and request.category != "all":
        query["$or"] = query.get("$or", []) + [
            {"product_format": request.category},
            {"category": request.category}
        ]
    
    if request.brand and request.brand != "all":
        query["brand"] = request.brand
    
    if request.animal_type and request.animal_type != "all":
        query["$or"] = query.get("$or", []) + [
            {"animal_type": request.animal_type},
            {"target_animals": request.animal_type}
        ]
    
    if request.product_format and request.product_format != "all":
        query["product_format"] = request.product_format
    
    if request.season and request.season != "all":
        query["season"] = request.season
    
    if request.sale_mode and request.sale_mode != "all":
        query["sale_mode"] = request.sale_mode
    
    # Range filters
    if request.min_price is not None and request.min_price > 0:
        query["price"] = {"$gte": request.min_price}
    
    if request.max_price is not None:
        if "price" in query:
            query["price"]["$lte"] = request.max_price
        else:
            query["price"] = {"$lte": request.max_price}
    
    if request.min_score is not None and request.min_score > 0:
        query["score"] = {"$gte": request.min_score}
    
    if request.max_score is not None:
        if "score" in query:
            query["score"]["$lte"] = request.max_score
        else:
            query["score"] = {"$lte": request.max_score}
    
    # Boolean filters
    if request.rainproof is not None:
        query["rainproof"] = request.rainproof
    
    if request.has_pheromones is not None:
        query["has_pheromones"] = request.has_pheromones
    
    if request.certified_food is not None:
        query["certified_food"] = request.certified_food
    
    # Sorting
    sort_direction = 1 if request.sort_order == "asc" else -1
    sort_field = request.sort_by or "rank"
    
    # Execute query
    products = await db.products.find(
        query,
        {"_id": 0}
    ).sort(sort_field, sort_direction).skip(request.offset).limit(request.limit).to_list(request.limit)
    
    total = await db.products.count_documents(query)
    
    return {
        "products": products,
        "total": total,
        "offset": request.offset,
        "limit": request.limit
    }

@api_router.get("/products/brands")
async def get_product_brands():
    """Liste toutes les marques disponibles"""
    brands = await db.products.distinct("brand")
    return {"brands": sorted([b for b in brands if b])}

@api_router.get("/products/categories")
async def get_product_categories():
    """Liste toutes les catégories disponibles"""
    formats = await db.products.distinct("product_format")
    categories = await db.products.distinct("category")
    return {
        "formats": sorted([f for f in formats if f]),
        "categories": sorted([c for c in categories if c])
    }

# ============================================
# TERRITORY ANALYSIS ENDPOINTS
# ============================================

from services.territory_analysis import TerritoryAnalysisService, ANALYSIS_CATEGORIES, SPECIES_RULES

territory_service = TerritoryAnalysisService(db)

@api_router.get("/territory/categories")
async def get_analysis_categories():
    """Retourne les catégories d'analyse disponibles"""
    return {"categories": ANALYSIS_CATEGORIES}

@api_router.get("/territory/species-rules")
async def get_species_rules():
    """Retourne les règles métier par espèce"""
    return {"rules": SPECIES_RULES}

class ProbabilityRequest(BaseModel):
    species: str
    location: Dict[str, float]
    time_period: str = "tous"
    terrain_data: Optional[Dict[str, Any]] = None

@api_router.post("/territory/probability")
async def calculate_probability(request: ProbabilityRequest):
    """Calcule la probabilité de présence d'une espèce à un point"""
    result = territory_service.calculate_species_probability(
        species=request.species,
        location=request.location,
        time_period=request.time_period,
        terrain_data=request.terrain_data
    )
    return result

class HeatmapRequest(BaseModel):
    center: Dict[str, float]
    radius_km: float = 5.0
    species: Optional[str] = None
    layer_type: str = "activity"
    time_period: str = "tous"

@api_router.post("/territory/heatmap")
async def generate_heatmap(request: HeatmapRequest):
    """Génère une heatmap (activité ou probabilité)"""
    if request.layer_type == "probability":
        result = territory_service.generate_probability_heatmap(
            user_id="default",
            center=request.center,
            radius_km=request.radius_km,
            species=request.species or "chevreuil",
            time_period=request.time_period
        )
    else:
        result = territory_service.generate_activity_heatmap(
            user_id="default",
            center=request.center,
            radius_km=request.radius_km,
            species=request.species
        )
    return result

class ActionPlanRequest(BaseModel):
    species_target: str
    zone_center: Dict[str, float]
    zone_radius_km: float = 5.0
    time_period: str = "tous"

@api_router.post("/territory/action-plan")
async def generate_action_plan(request: ActionPlanRequest):
    """Génère un plan d'action complet"""
    plan = await territory_service.generate_action_plan(
        user_id="default",
        species_target=request.species_target,
        zone_center=request.zone_center,
        zone_radius_km=request.zone_radius_km,
        time_period=request.time_period
    )
    return {"success": True, "plan": plan}

@api_router.get("/territory/action-plans")
async def list_action_plans(limit: int = 10):
    """Liste les plans d'action générés"""
    plans = await db.action_plans.find({}, {"_id": 0}).sort("generated_at", -1).limit(limit).to_list(limit)
    return {"plans": plans}

# Camera management endpoints
class CameraCreate(BaseModel):
    label: str
    brand: str = "autre"
    connection_type: str = "manual"
    location: Optional[Dict[str, float]] = None
    ftp_host: Optional[str] = None
    ftp_username: Optional[str] = None
    ftp_password: Optional[str] = None

@api_router.get("/territory/cameras")
async def list_cameras():
    """Liste les caméras de l'utilisateur"""
    cameras = await db.cameras.find({}, {"_id": 0}).to_list(100)
    return {"cameras": cameras}

@api_router.post("/territory/cameras")
async def create_camera(request: CameraCreate):
    """Crée une nouvelle caméra"""
    camera = {
        "id": str(__import__('uuid').uuid4()),
        "user_id": "default",
        "label": request.label,
        "brand": request.brand,
        "connection_type": request.connection_type,
        "location": request.location,
        "ftp_host": request.ftp_host,
        "ftp_username": request.ftp_username,
        "connected": False,
        "last_seen_at": None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.cameras.insert_one(camera)
    camera.pop("_id", None)
    return {"success": True, "camera": camera}

@api_router.post("/territory/cameras/{camera_id}/test")
async def test_camera_connection(camera_id: str):
    """Teste la connexion d'une caméra"""
    camera = await db.cameras.find_one({"id": camera_id})
    if not camera:
        raise HTTPException(status_code=404, detail="Caméra non trouvée")
    
    # Simulation de test de connexion
    import random
    success = random.random() > 0.3
    
    await db.cameras.update_one(
        {"id": camera_id},
        {"$set": {
            "connected": success,
            "last_seen_at": datetime.now(timezone.utc).isoformat() if success else None
        }}
    )
    
    return {
        "success": success,
        "message": "Connexion établie ✅" if success else "Échec de connexion - vérifiez les paramètres",
        "camera_id": camera_id
    }

# Events management
class EventCreate(BaseModel):
    event_type: str
    location: Dict[str, float]
    species: Optional[str] = None
    notes: Optional[str] = None
    metadata: Dict[str, Any] = {}

# [P2] DEPRECATED - These routes are now handled by territory.py with P2 normalized geo_entities
# @api_router.get("/territory/events")
# async def list_events(species: Optional[str] = None, limit: int = 50):
#     """Liste les événements récents"""
#     query = {}
#     if species:
#         query["species"] = species
#     
#     events = await db.territory_events.find(query, {"_id": 0}).sort("captured_at", -1).limit(limit).to_list(limit)
#     return {"events": events}

# [P2] DEPRECATED - Now handled by territory.py POST /api/territory/events
# @api_router.post("/territory/events")
# async def create_event(request: EventCreate):
#     """Crée un nouvel événement"""
#     event = {
#         "id": str(__import__('uuid').uuid4()),
#         "user_id": "default",
#         "event_type": request.event_type,
#         "species": request.species,
#         "species_confidence": 1.0 if request.species else 0.0,
#         "location": request.location,
#         "captured_at": datetime.now(timezone.utc).isoformat(),
#         "source": "manual",
#         "metadata": request.metadata,
#         "notes": request.notes
#     }
#     await db.territory_events.insert_one(event)
#     event.pop("_id", None)
#     return {"success": True, "event": event}

# Photo classification (AI simulation)
@api_router.post("/territory/classify-photo")
async def classify_photo(photo_path: str = ""):
    """Classifie une photo de caméra (simulation IA)"""
    result = await territory_service.classify_photo_species(photo_path)
    return result

# ============================================
# INCLUDE ROUTER & MIDDLEWARE
# ============================================

app.include_router(api_router)

# Include Territory Analysis Module (PostGIS)
try:
    from territory import territory_router, init_territory_module, shutdown_territory_module
    app.include_router(territory_router)
    
    @app.on_event("startup")
    async def startup_territory():
        await init_territory_module()
        logger.info("Territory analysis module started")
except ImportError as e:
    logger.warning(f"Territory module not available: {e}")

# Include Hunt Marketplace Module
try:
    from marketplace import marketplace_router
    app.include_router(marketplace_router)
    print("Hunt Marketplace module loaded")
except ImportError as e:
    print(f"Marketplace module not available: {e}")

# Include SEO, Analytics & Content Depot Module
try:
    from seo_analytics import seo_router
    app.include_router(seo_router)
    print("SEO & Analytics module loaded")
except ImportError as e:
    print(f"SEO module not available: {e}")

# Include Payments Module (Stripe)
try:
    from payments import payments_router
    app.include_router(payments_router)
    print("Payments module loaded (Stripe)")
except ImportError as e:
    print(f"Payments module not available: {e}")

# Include Site Access Control Module
try:
    from site_access import access_router
    app.include_router(access_router)
    print("Site Access Control module loaded")
except ImportError as e:
    print(f"Site Access module not available: {e}")

# Include Lands Rental Module
try:
    from lands_rental import lands_router
    app.include_router(lands_router)
    print("Lands Rental module loaded")
except ImportError as e:
    print(f"Lands Rental module not available: {e}")

# Include User Authentication Module
try:
    from user_auth import auth_router
    app.include_router(auth_router)
    print("User Authentication module loaded")
except ImportError as e:
    print(f"User Auth module not available: {e}")

# Include Networking Ecosystem Module
try:
    from networking import router as networking_router
    app.include_router(networking_router, prefix="/api")
    print("Networking Ecosystem module loaded")
except ImportError as e:
    print(f"Networking module not available: {e}")

# Include Notifications Module
try:
    from notifications import router as notifications_router
    app.include_router(notifications_router, prefix="/api")
    print("Notifications module loaded")
except ImportError as e:
    print(f"Notifications module not available: {e}")

# Include Email Notifications Module
try:
    from email_notifications import router as email_router
    app.include_router(email_router, prefix="/api")
    print("Email Notifications module loaded")
except ImportError as e:
    print(f"Email module not available: {e}")

# Include Feature Controls Module
try:
    from feature_controls import feature_controls_router
    app.include_router(feature_controls_router)
    print("Feature Controls module loaded")
except ImportError as e:
    print(f"Feature Controls module not available: {e}")

# Include Brand Identity Module
try:
    from brand_identity import brand_router
    app.include_router(brand_router, prefix="/api")
    print("Brand Identity module loaded")
except ImportError as e:
    print(f"Brand Identity module not available: {e}")

# Include Partnership Engine Module
try:
    from partnership import router as partnership_router
    app.include_router(partnership_router, prefix="/api")
    print("Partnership Engine module loaded")
except ImportError as e:
    print(f"Partnership Engine module not available: {e}")

# Include Territory Inventory Module
try:
    from territories import router as territories_router
    app.include_router(territories_router)
    print("Territory Inventory module loaded")
except ImportError as e:
    print(f"Territory Inventory module not available: {e}")

# Include Territory Scraping Module
try:
    from territory_scraping import router as scraping_router
    app.include_router(scraping_router)
    print("Territory Scraping module loaded")
except ImportError as e:
    print(f"Territory Scraping module not available: {e}")

# Include Territory AI & Cartography Module
try:
    from territory_ai import router as territory_ai_router
    app.include_router(territory_ai_router)
    print("Territory AI & Cartography module loaded")
except ImportError as e:
    print(f"Territory AI module not available: {e}")

# Include Backup Manager Module
try:
    from backup_manager import router as backup_router
    app.include_router(backup_router)
    print("Backup Manager module loaded")
except ImportError as e:
    print(f"Backup Manager module not available: {e}")

# Include Maintenance Controller Module (Secure & Persistent)
try:
    from maintenance_controller import router as maintenance_router
    app.include_router(maintenance_router)
    print("Maintenance Controller module loaded (secure)")
except ImportError as e:
    print(f"Maintenance Controller module not available: {e}")

# Include BIONIC™ Territory Analysis Engine
try:
    from bionic_engine import router as bionic_router
    app.include_router(bionic_router)
    print("BIONIC™ Territory Analysis Engine loaded")
except ImportError as e:
    print(f"BIONIC™ Engine not available: {e}")

# [REMOVED - P6.2] User Waypoints migrated to unified geo_engine
# Legacy: user_waypoints.py has been deleted
# All waypoint functionality is now at /api/v1/geo/*
print("User Waypoints API REMOVED - migrated to /api/v1/geo/*")

# Include Waypoint Sharing API
try:
    from waypoint_sharing import router as sharing_router
    app.include_router(sharing_router)
    print("Waypoint Sharing API loaded")
except ImportError as e:
    print(f"Waypoint Sharing API not available: {e}")

# Include Hunting Groups API
try:
    from hunting_groups import router as groups_router
    app.include_router(groups_router)
    print("Hunting Groups API loaded")
except ImportError as e:
    print(f"Hunting Groups API not available: {e}")

# Include Live Tracking API
try:
    from live_tracking import router as tracking_router
    app.include_router(tracking_router)
    print("Live Tracking API loaded")
except ImportError as e:
    print(f"Live Tracking API not available: {e}")

# Include Group Chat API
try:
    from group_chat import router as chat_router
    app.include_router(chat_router)
    print("Group Chat API loaded")
except ImportError as e:
    print(f"Group Chat API not available: {e}")

# Include Zone Favorites API
try:
    from zone_favorites import router as favorites_router
    app.include_router(favorites_router)
    print("Zone Favorites API loaded")
except ImportError as e:
    print(f"Zone Favorites API not available: {e}")

# Hydrography Service - Water exclusion for BIONIC zones
try:
    from hydrography_router import router as hydro_router
    app.include_router(hydro_router)
    print("Hydrography API loaded - Water exclusion enabled")
except ImportError as e:
    print(f"Hydrography API not available: {e}")

try:
    from wms_proxy_router import router as wms_proxy_router
    app.include_router(wms_proxy_router)
    print("WMS Proxy API loaded - Ecoforestry maps enabled")
except ImportError as e:
    print(f"WMS Proxy API not available: {e}")

# ============================================
# MODULAR CORE ENGINES (Phase 2)
# ============================================
try:
    register_routers(app)
    print(f"✓ {MODULE_STATUS['total_modules']} CORE modules loaded successfully")
    print(f"  Modules: {', '.join(MODULE_STATUS['modules'])}")
except Exception as e:
    print(f"⚠ Modular engines loading error: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    global scheduler_service
    if scheduler_service:
        await scheduler_service.stop()
    client.close()
    # Shutdown territory module if available
    try:
        await shutdown_territory_module()
    except:
        pass
