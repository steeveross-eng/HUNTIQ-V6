"""AI Engine Models - CORE

Pydantic models for AI-powered product analysis.
Extracted from analyzer.py without modification.

Version: 1.0.0
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid


class AnalysisRequest(BaseModel):
    """Request model for product analysis"""
    product_name: str
    product_type: Optional[str] = None  # Auto-detected if not provided


class ProductTechnicalSheet(BaseModel):
    """Technical sheet for analyzed product"""
    name: str
    detected_type: str
    brand: Optional[str] = None
    estimated_price: Optional[float] = None
    estimated_price_with_shipping: Optional[float] = None
    estimated_ingredients: List[str] = []
    estimated_composition: Dict[str, Any] = {}
    confidence_level: str = "estimated"  # "confirmed" or "estimated"
    notes: List[str] = []


class ScientificAnalysis(BaseModel):
    """Scientific analysis breakdown"""
    olfactory_compounds: List[Dict[str, Any]] = []
    nutritional_compounds: List[Dict[str, Any]] = []
    behavioral_compounds: List[Dict[str, Any]] = []
    fixatives: List[Dict[str, Any]] = []
    durability_criteria: Dict[str, Any] = {}


class CompetitorProduct(BaseModel):
    """Competitor product for comparison"""
    name: str
    brand: Optional[str] = None
    image_url: Optional[str] = None
    score: float
    price: float
    price_with_shipping: float
    buy_link: Optional[str] = None


class CompetitorComparison(BaseModel):
    """Comparison table with competitors"""
    bionic_product: Dict[str, Any]
    competitor_1: Dict[str, Any]
    competitor_2: Dict[str, Any]
    comparison_table: List[Dict[str, Any]]


class AIAnalysisReport(BaseModel):
    """Complete AI analysis report"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_name: str
    technical_sheet: ProductTechnicalSheet
    scientific_analysis: ScientificAnalysis
    scoring: Dict[str, Any] = {}
    comparison: Optional[CompetitorComparison] = None
    price_analysis: Dict[str, Any] = {}
    recommendations: List[str] = []
    bionic_arguments: List[str] = []
    conclusion: str = ""
    scientific_references: List[Dict[str, Any]] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AdvancedAnalysisRequest(BaseModel):
    """Request for advanced AI analysis with hunting context"""
    product_name: str
    species: Optional[str] = "deer"  # deer, moose, bear, wild_boar, turkey
    season: Optional[str] = "fall"  # spring, summer, fall, winter
    weather: Optional[str] = "normal"  # cold, normal, hot, rain, snow
    terrain: Optional[str] = "forest"  # forest, field, marsh, mountain


class AdvancedAnalysisResponse(BaseModel):
    """Response for advanced AI analysis"""
    product_name: str
    species: str
    season: str
    weather: str
    terrain: str
    score: float
    recommendation: str
    best_time: str
    application_tips: List[str] = []
    alternatives: List[Dict[str, Any]] = []
    scientific_basis: str = ""


class EmailConsent(BaseModel):
    """Email consent for report delivery"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    region: str
    consent_marketing: bool
    consent_statistics: bool
    report_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
