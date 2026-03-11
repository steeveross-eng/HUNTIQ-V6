"""
BIONIC SEO Models - V5-ULTIME
=============================

Modèles Pydantic pour le SEO Engine.
Définition des structures pour:
- Clusters SEO
- Pages (piliers, satellites, opportunités)
- Schémas JSON-LD
- Campagnes et automation
- Analytics et KPIs

Module isolé - aucun import croisé.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============================================
# ENUMS
# ============================================

class ClusterType(str, Enum):
    SPECIES = "species"           # Cluster par espèce
    REGION = "region"             # Cluster par région
    SEASON = "season"             # Cluster par saison
    TECHNIQUE = "technique"       # Cluster par technique
    EQUIPMENT = "equipment"       # Cluster par équipement
    TERRITORY = "territory"       # Cluster par territoire
    BEHAVIOR = "behavior"         # Cluster comportemental
    WEATHER = "weather"           # Cluster météo


class PageType(str, Enum):
    PILLAR = "pillar"             # Page pilier (guide complet)
    SATELLITE = "satellite"       # Page satellite (sous-sujet)
    OPPORTUNITY = "opportunity"   # Page opportunité (longue traîne)
    VIRAL = "viral"               # Capsule virale
    INTERACTIVE = "interactive"   # Guide interactif
    TOOL = "tool"                 # Outil/widget
    LANDING = "landing"           # Landing page


class PageStatus(str, Enum):
    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    SCHEDULED = "scheduled"
    ARCHIVED = "archived"


class ContentFormat(str, Enum):
    ARTICLE = "article"
    GUIDE = "guide"
    CHECKLIST = "checklist"
    INFOGRAPHIC = "infographic"
    VIDEO = "video"
    PODCAST = "podcast"
    QUIZ = "quiz"
    CALCULATOR = "calculator"
    MAP = "map"
    COMPARISON = "comparison"


class JsonLDType(str, Enum):
    ARTICLE = "Article"
    HOWTO = "HowTo"
    FAQ = "FAQPage"
    LOCAL_BUSINESS = "LocalBusiness"
    PRODUCT = "Product"
    EVENT = "Event"
    ORGANIZATION = "Organization"
    BREADCRUMB = "BreadcrumbList"
    VIDEO = "VideoObject"


class TargetAudience(str, Enum):
    BEGINNER = "beginner"         # Chasseur débutant
    INTERMEDIATE = "intermediate" # Chasseur intermédiaire
    EXPERT = "expert"             # Chasseur expert
    GUIDE = "guide"               # Guide professionnel
    LANDOWNER = "landowner"       # Propriétaire terrain
    ALL = "all"                   # Tous publics


# ============================================
# CORE MODELS
# ============================================

class SEOKeyword(BaseModel):
    """Mot-clé SEO avec métriques"""
    keyword: str
    keyword_fr: str
    search_volume: int = 0
    difficulty: float = Field(default=0.5, ge=0, le=1)
    cpc: float = 0.0
    intent: str = "informational"  # informational, transactional, navigational
    priority: int = Field(default=3, ge=1, le=5)
    is_primary: bool = False


class SEOCluster(BaseModel):
    """Cluster SEO thématique"""
    id: str
    name: str
    name_fr: str
    cluster_type: ClusterType
    description: str
    description_fr: str
    
    # Mots-clés
    primary_keyword: SEOKeyword
    secondary_keywords: List[SEOKeyword] = []
    long_tail_keywords: List[str] = []
    
    # Pages
    pillar_page_id: Optional[str] = None
    satellite_page_ids: List[str] = []
    opportunity_page_ids: List[str] = []
    
    # Hiérarchie
    parent_cluster_id: Optional[str] = None
    sub_cluster_ids: List[str] = []
    
    # Métriques
    total_pages: int = 0
    total_traffic: int = 0
    avg_position: float = 0.0
    
    # Knowledge Layer
    species_ids: List[str] = []
    region_ids: List[str] = []
    season_tags: List[str] = []
    
    # Métadonnées
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class InternalLink(BaseModel):
    """Lien interne pour maillage"""
    target_page_id: str
    anchor_text: str
    anchor_text_fr: str
    context: str = ""
    link_type: str = "contextual"  # contextual, navigation, related, cta
    priority: int = 3


class SEOPage(BaseModel):
    """Page SEO complète"""
    id: str
    cluster_id: str
    page_type: PageType
    status: PageStatus = PageStatus.DRAFT
    
    # URL et titre
    slug: str
    url_path: str
    title: str
    title_fr: str
    meta_description: str
    meta_description_fr: str
    
    # Contenu
    content_format: ContentFormat
    h1: str
    h2_list: List[str] = []
    word_count: int = 0
    reading_time_min: int = 0
    
    # SEO
    primary_keyword: str
    secondary_keywords: List[str] = []
    keyword_density: float = 0.0
    seo_score: float = Field(default=0.0, ge=0, le=100)
    
    # Maillage interne
    internal_links_out: List[InternalLink] = []
    internal_links_in: List[str] = []  # Page IDs linking to this page
    
    # JSON-LD
    jsonld_types: List[JsonLDType] = []
    jsonld_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Ciblage
    target_audience: TargetAudience = TargetAudience.ALL
    target_regions: List[str] = []
    target_seasons: List[str] = []
    target_species: List[str] = []
    
    # Knowledge Layer
    knowledge_rules_applied: List[str] = []
    knowledge_data_used: Dict[str, Any] = Field(default_factory=dict)
    
    # Performance
    impressions: int = 0
    clicks: int = 0
    ctr: float = 0.0
    avg_position: float = 0.0
    conversions: int = 0
    
    # Métadonnées
    author: str = "BIONIC"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None
    scheduled_at: Optional[datetime] = None


class SEOJsonLD(BaseModel):
    """Schéma JSON-LD structuré"""
    id: str
    page_id: str
    schema_type: JsonLDType
    
    # Données structurées
    schema_data: Dict[str, Any]
    
    # Validation
    is_valid: bool = True
    validation_errors: List[str] = []
    
    # Métadonnées
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ViralCapsule(BaseModel):
    """Capsule virale pour partage social"""
    id: str
    title: str
    title_fr: str
    hook: str  # Accroche virale
    
    # Contenu
    format: str  # infographic, video_short, quiz, fact, tip
    content: Dict[str, Any]
    
    # Ciblage
    target_platforms: List[str] = ["facebook", "instagram", "tiktok"]
    target_audience: TargetAudience = TargetAudience.ALL
    
    # Partage
    share_text: str
    hashtags: List[str] = []
    cta_text: str
    cta_url: str
    
    # Performance
    shares: int = 0
    engagement_rate: float = 0.0
    
    # Knowledge Layer
    species_id: Optional[str] = None
    fact_source: Optional[str] = None
    
    # Métadonnées
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class InteractiveWidget(BaseModel):
    """Widget interactif SEO"""
    id: str
    name: str
    name_fr: str
    widget_type: str  # calculator, quiz, map, comparison, planner
    
    # Configuration
    config: Dict[str, Any]
    embed_code: str = ""
    
    # Intégration
    page_ids: List[str] = []  # Pages où le widget est intégré
    
    # Performance
    interactions: int = 0
    completions: int = 0
    leads_generated: int = 0
    
    # Knowledge Layer
    uses_knowledge_api: bool = False
    knowledge_endpoints: List[str] = []
    
    # Métadonnées
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class SEOCampaign(BaseModel):
    """Campagne SEO avec objectifs"""
    id: str
    name: str
    name_fr: str
    
    # Objectifs
    target_cluster_ids: List[str] = []
    target_keywords: List[str] = []
    target_traffic: int = 0
    target_conversions: int = 0
    
    # Timeline
    start_date: datetime
    end_date: Optional[datetime] = None
    
    # Pages à créer/optimiser
    pages_planned: int = 0
    pages_created: int = 0
    pages_optimized: int = 0
    
    # Performance
    current_traffic: int = 0
    current_conversions: int = 0
    progress_percent: float = 0.0
    
    # Métadonnées
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "active"


class SEOAnalytics(BaseModel):
    """Analytics SEO agrégées"""
    period: str  # daily, weekly, monthly
    date: datetime
    
    # Trafic
    total_impressions: int = 0
    total_clicks: int = 0
    avg_ctr: float = 0.0
    avg_position: float = 0.0
    
    # Pages
    total_pages: int = 0
    pages_indexed: int = 0
    pages_ranking: int = 0
    
    # Conversions
    total_conversions: int = 0
    conversion_rate: float = 0.0
    
    # Top performers
    top_pages: List[Dict[str, Any]] = []
    top_keywords: List[Dict[str, Any]] = []
    top_clusters: List[Dict[str, Any]] = []
    
    # Évolution
    traffic_change: float = 0.0
    position_change: float = 0.0
    
    # Santé technique
    crawl_errors: int = 0
    mobile_issues: int = 0
    speed_score: float = 0.0


# ============================================
# API RESPONSE MODELS
# ============================================

class SEODashboardStats(BaseModel):
    """Statistiques dashboard SEO"""
    total_clusters: int
    total_pages: int
    total_keywords: int
    avg_seo_score: float
    total_traffic: int
    total_conversions: int
    health_score: float


# ============================================
# REQUEST MODELS FOR API ENDPOINTS
# ============================================

class GenerateOutlineRequest(BaseModel):
    """Requête de génération d'outline"""
    cluster_id: str
    page_type: str
    target_keyword: str
    knowledge_data: Optional[Dict[str, Any]] = None


class GenerateMetaTagsRequest(BaseModel):
    """Requête de génération de meta tags"""
    title: str
    keyword: str
    content_summary: str = ""


class GenerateViralCapsuleRequest(BaseModel):
    """Requête de génération de capsule virale"""
    topic: str
    species_id: Optional[str] = None
    knowledge_data: Optional[Dict[str, Any]] = None


class CreateContentWorkflowRequest(BaseModel):
    """Requête workflow de création de contenu"""
    cluster_id: str
    page_type: str
    target_keyword: str
    knowledge_data: Optional[Dict[str, Any]] = None


class EnrichWithKnowledgeRequest(BaseModel):
    """Requête d'enrichissement Knowledge Layer"""
    page_id: str
    species_id: Optional[str] = None
    knowledge_api_response: Optional[Dict[str, Any]] = None


class GeneratePillarContentRequest(BaseModel):
    """Requête de génération de contenu pilier"""
    species_id: str
    keyword: str
    knowledge_data: Dict[str, Any]


class GenerateFAQRequest(BaseModel):
    """Requête de génération FAQ JSON-LD"""
    questions: List[Dict[str, str]]


class ContentGenerationRequest(BaseModel):
    """Requête de génération de contenu"""
    cluster_id: str
    page_type: PageType
    target_keyword: str
    content_format: ContentFormat
    target_audience: TargetAudience = TargetAudience.ALL
    word_count_target: int = 1500
    use_knowledge_layer: bool = True
    species_focus: Optional[str] = None
    region_focus: Optional[str] = None
    season_focus: Optional[str] = None
