"""
Tracking Engine - Models V1
============================
Models for user behavior tracking, events, funnels and heatmaps.
Architecture LEGO V5 - Module isolé.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from enum import Enum
import uuid


class EventType(str, Enum):
    """Types d'événements trackés"""
    PAGE_VIEW = "page_view"
    CLICK = "click"
    SCROLL = "scroll"
    FORM_SUBMIT = "form_submit"
    SEARCH = "search"
    MAP_INTERACTION = "map_interaction"
    FEATURE_USE = "feature_use"
    PURCHASE = "purchase"
    SIGNUP = "signup"
    LOGIN = "login"
    ERROR = "error"
    CUSTOM = "custom"


class TrackingEvent(BaseModel):
    """Événement de tracking utilisateur"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    user_id: Optional[str] = None
    event_type: EventType
    event_name: str
    page_url: Optional[str] = None
    page_title: Optional[str] = None
    element_id: Optional[str] = None
    element_class: Optional[str] = None
    element_text: Optional[str] = None
    properties: Dict[str, Any] = {}
    position_x: Optional[int] = None
    position_y: Optional[int] = None
    viewport_width: Optional[int] = None
    viewport_height: Optional[int] = None
    referrer: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    country: Optional[str] = None
    device_type: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TrackingEventCreate(BaseModel):
    """Schema pour créer un événement"""
    session_id: str
    user_id: Optional[str] = None
    event_type: EventType
    event_name: str
    page_url: Optional[str] = None
    page_title: Optional[str] = None
    element_id: Optional[str] = None
    element_class: Optional[str] = None
    element_text: Optional[str] = None
    properties: Dict[str, Any] = {}
    position_x: Optional[int] = None
    position_y: Optional[int] = None
    viewport_width: Optional[int] = None
    viewport_height: Optional[int] = None
    referrer: Optional[str] = None
    user_agent: Optional[str] = None


class FunnelStep(BaseModel):
    """Étape dans un funnel de conversion"""
    step_number: int
    event_name: str
    event_type: Optional[EventType] = None
    page_url_pattern: Optional[str] = None
    is_required: bool = True


class Funnel(BaseModel):
    """Définition d'un funnel de conversion"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    steps: List[FunnelStep]
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FunnelCreate(BaseModel):
    """Schema pour créer un funnel"""
    name: str
    description: Optional[str] = None
    steps: List[FunnelStep]


class FunnelAnalysis(BaseModel):
    """Résultat d'analyse d'un funnel"""
    funnel_id: str
    funnel_name: str
    total_started: int
    total_completed: int
    conversion_rate: float
    steps_analysis: List[Dict[str, Any]]
    avg_time_to_complete: Optional[float] = None


class HeatmapPoint(BaseModel):
    """Point de données pour heatmap"""
    x: int
    y: int
    value: int = 1


class HeatmapData(BaseModel):
    """Données de heatmap pour une page"""
    page_url: str
    page_title: Optional[str] = None
    viewport_width: int
    viewport_height: int
    total_clicks: int
    points: List[HeatmapPoint]
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SessionSummary(BaseModel):
    """Résumé d'une session utilisateur"""
    session_id: str
    user_id: Optional[str] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    page_views: int
    total_events: int
    pages_visited: List[str]
    device_type: Optional[str] = None
    country: Optional[str] = None


class EngagementMetrics(BaseModel):
    """Métriques d'engagement utilisateur"""
    total_sessions: int
    total_page_views: int
    total_events: int
    unique_users: int
    avg_session_duration: float
    bounce_rate: float
    pages_per_session: float
    top_pages: List[Dict[str, Any]]
    top_events: List[Dict[str, Any]]
    device_breakdown: Dict[str, int]
    country_breakdown: Dict[str, int]
    time_range_start: datetime
    time_range_end: datetime


class TrackingConfig(BaseModel):
    """Configuration du tracking"""
    track_page_views: bool = True
    track_clicks: bool = True
    track_scrolls: bool = False
    track_forms: bool = True
    track_searches: bool = True
    track_errors: bool = True
    anonymize_ip: bool = True
    session_timeout_minutes: int = 30
    excluded_paths: List[str] = []
    excluded_user_agents: List[str] = []
