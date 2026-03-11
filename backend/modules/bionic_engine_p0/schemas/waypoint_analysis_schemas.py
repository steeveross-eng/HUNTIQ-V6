"""
BIONIC ENGINE — Waypoint Analysis Schemas
==========================================
Schémas Pydantic pour l'endpoint POST /api/v1/bionic/analyze_waypoint

RESPONSABILITÉ UNIQUE:
- Validation des entrées (WaypointAnalysisRequest)
- Structure des sorties (WaypointAnalysisResponse)
- Typage strict de tous les sous-modèles

ISOLATION:
- Aucune logique métier
- Aucun import de services
- Modèles de données purs

CONTRACT VERSION: 1.0.0
Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field


# =============================================================================
# ENUMS
# =============================================================================

class DataQuality(str, Enum):
    """Qualité des données disponibles."""
    FULL = "full"           # Toutes sources primaires
    PARTIAL = "partial"     # 1-2 fallbacks, confiance > 0.80
    DEGRADED = "degraded"   # 3+ fallbacks, confiance 0.60-0.80
    MINIMAL = "minimal"     # Données insuffisantes, confiance < 0.60


class ScoreLevel(str, Enum):
    """Niveau qualitatif du score."""
    EXCELLENT = "excellent"   # 85-100
    GOOD = "good"             # 70-84
    MODERATE = "moderate"     # 50-69
    POOR = "poor"             # 30-49
    VERY_POOR = "very_poor"   # 0-29


class ZoneType(str, Enum):
    """Types de zones comportementales."""
    BEDDING = "bedding"
    FEEDING = "feeding"
    RUT = "rut"
    MOVEMENT = "movement"
    PRESSURE = "pressure"


class AttractionType(str, Enum):
    """Types de points d'attraction."""
    SALINE = "saline"
    WATER_SOURCE = "water_source"
    THERMAL_REFUGE = "thermal_refuge"
    AFFUT = "affut"


class FusionMode(str, Enum):
    """Mode de fusion des zones."""
    WEIGHTED = "weighted"
    PRIORITY = "priority"
    AVERAGE = "average"


class AnalysisMode(str, Enum):
    """Mode d'analyse BIONIC V5 — basé sur les périodes biologiques."""
    LIVE = "live"                        # Score temps réel (date/heure système)
    PRE_RUT = "pre_rut"                  # Score période pré-rut
    RUT = "rut"                          # Score période rut (pic)
    POST_RUT = "post_rut"                # Score période post-rut


# =============================================================================
# REQUEST MODELS
# =============================================================================

class WaypointInput(BaseModel):
    """Waypoint de référence pour l'analyse."""
    id: str = Field(..., description="Identifiant unique du waypoint")
    name: str = Field(..., description="Nom du waypoint")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude")


class WQSInput(BaseModel):
    """Données WQS (Waypoint Quality Score) en entrée."""
    score: float = Field(default=50.0, ge=0, le=100, description="Score WQS global")
    success_history: float = Field(default=50.0, ge=0, le=100, description="Historique de succès")
    weather_correlation: float = Field(default=50.0, ge=0, le=100, description="Corrélation météo")
    activity_history: float = Field(default=50.0, ge=0, le=100, description="Historique d'activité")
    accessibility: float = Field(default=50.0, ge=0, le=100, description="Accessibilité")


class AnalysisParameters(BaseModel):
    """Paramètres d'analyse."""
    search_radius_km: float = Field(default=3.0, ge=0.5, le=10.0, description="Rayon de recherche en km")
    grid_resolution: int = Field(default=10, ge=5, le=50, description="Résolution de la grille")
    region: str = Field(default="CA-QC", description="Code région")
    mode: AnalysisMode = Field(default=AnalysisMode.RUT, description="Mode d'analyse biologique: LIVE, PRE_RUT, RUT, POST_RUT")


class VisualizationParameters(BaseModel):
    """Paramètres de visualisation des zones organiques."""
    organic_shape: bool = Field(default=True, description="Activer les formes organiques")
    exclude_water: bool = Field(default=True, description="Exclure les plans d'eau")
    follow_topography: bool = Field(default=True, description="Suivre la topographie")
    follow_vegetation: bool = Field(default=True, description="Suivre la végétation")
    allow_overlap: bool = Field(default=True, description="Autoriser le chevauchement")
    fusion_mode: FusionMode = Field(default=FusionMode.WEIGHTED, description="Mode de fusion")
    smoothing_factor: float = Field(default=0.35, ge=0.1, le=0.9, description="Facteur de lissage")
    max_points_per_shape: int = Field(default=200, ge=50, le=500, description="Points max par forme")
    terrain_adaptation_strength: float = Field(default=0.8, ge=0, le=1, description="Force d'adaptation terrain")
    vegetation_influence: float = Field(default=0.7, ge=0, le=1, description="Influence végétation")
    hydrography_influence: float = Field(default=0.9, ge=0, le=1, description="Influence hydrographie")


class WeatherInput(BaseModel):
    """Conditions météorologiques."""
    wind_speed_kmh: float = Field(default=10.0, ge=0, description="Vitesse du vent en km/h")
    temperature_c: float = Field(default=10.0, description="Température en °C")
    precipitation: str = Field(default="none", description="Type de précipitation")


class TemporalParameters(BaseModel):
    """Paramètres temporels."""
    period: str = Field(default="dawn", description="Période: dawn, day, dusk, night")
    season: str = Field(default="autumn", description="Saison: spring, summer, autumn, winter")
    weather: Optional[WeatherInput] = Field(default=None, description="Conditions météo")


class WaypointAnalysisRequest(BaseModel):
    """
    Requête d'analyse waypoint-centric.
    
    Payload complet pour l'endpoint POST /api/v1/bionic/analyze_waypoint
    """
    waypoint: WaypointInput = Field(..., description="Waypoint de référence")
    target_datetime: datetime = Field(..., description="Date/heure cible de l'analyse")
    species: str = Field(default="orignal", description="Espèce cible")
    wqs: Optional[WQSInput] = Field(default=None, description="Données WQS")
    parameters: Optional[AnalysisParameters] = Field(default=None, description="Paramètres d'analyse")
    visualization: Optional[VisualizationParameters] = Field(default=None, description="Paramètres de visualisation")
    temporal: Optional[TemporalParameters] = Field(default=None, description="Paramètres temporels")
    
    class Config:
        json_schema_extra = {
            "example": {
                "waypoint": {
                    "id": "WP-001",
                    "name": "Zone Nord - Affût Principal",
                    "latitude": 46.8250,
                    "longitude": -71.2050
                },
                "target_datetime": "2025-10-15T06:30:00",
                "species": "orignal",
                "wqs": {
                    "score": 72.5,
                    "success_history": 65.0,
                    "weather_correlation": 78.0,
                    "activity_history": 70.0,
                    "accessibility": 85.0
                }
            }
        }


# =============================================================================
# RESPONSE MODELS - SCORES
# =============================================================================

class ScoreComponent(BaseModel):
    """Composant individuel du breakdown de score."""
    value: float = Field(..., ge=0, le=100, description="Valeur du score")
    weight: float = Field(..., ge=0, le=1, description="Pondération")
    weighted: float = Field(..., description="Valeur pondérée")
    level: ScoreLevel = Field(..., description="Niveau qualitatif")


class ScoreBreakdown(BaseModel):
    """Détail des 9 scores canoniques BIONIC."""
    H_habitat: ScoreComponent = Field(..., description="Score Habitat")
    R_risk: ScoreComponent = Field(..., description="Score Risque")
    S_probability: ScoreComponent = Field(..., description="Score Probabilité")
    A_mobility: ScoreComponent = Field(..., description="Score Mobilité")
    T_weather: ScoreComponent = Field(..., description="Score Météo")
    P_pressure: ScoreComponent = Field(..., description="Score Pression")
    behavior: ScoreComponent = Field(..., description="Score Comportement")
    density: ScoreComponent = Field(..., description="Score Densité")
    multifactor: ScoreComponent = Field(..., description="Score Multi-facteurs")


class FusionContribution(BaseModel):
    """Contribution à la fusion WQS + SCORE_FINAL."""
    value: float = Field(..., ge=0, le=100, description="Valeur source")
    weight: float = Field(..., ge=0, le=1, description="Pondération")
    contribution: float = Field(..., description="Contribution au score final")


class ScoreFusion(BaseModel):
    """Détail de la fusion WQS (40%) + Dynamic (60%)."""
    wqs: FusionContribution = Field(..., description="Contribution WQS")
    dynamic: FusionContribution = Field(..., description="Contribution dynamique")


class ScoreCategory(BaseModel):
    """Catégorie qualitative du score."""
    label: str = Field(..., description="Label: FAVORABLE, MODÉRÉ, DÉFAVORABLE")
    color: str = Field(..., description="Couleur hex")


class ScoresOutput(BaseModel):
    """Scores complets avec breakdown."""
    score_bionic_final: float = Field(..., ge=0, le=100, description="Score final 0-100")
    score_bionic_final_10: float = Field(..., ge=0, le=10, description="Score final 0-10")
    level: ScoreLevel = Field(..., description="Niveau qualitatif")
    category: ScoreCategory = Field(..., description="Catégorie")
    breakdown: ScoreBreakdown = Field(..., description="Détail des 9 scores")
    fusion: ScoreFusion = Field(..., description="Détail fusion WQS/Dynamic")
    confidence: float = Field(..., ge=0, le=1, description="Confiance globale")
    data_quality: DataQuality = Field(..., description="Qualité des données")
    # Mode d'analyse utilisé
    analysis_mode: Optional[str] = Field(default=None, description="Mode: live, pre_rut, rut, post_rut")
    # PHASE B: Facteurs avancés avec traçabilité complète
    advanced_factors_details: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="PHASE B: Détails des facteurs avancés avec source_ids et versionnement"
    )


class DualModeScores(BaseModel):
    """Scores pour les 4 modes biologiques (LIVE, PRE_RUT, RUT, POST_RUT)."""
    live: Optional[ScoresOutput] = Field(default=None, description="Score temps réel")
    pre_rut: Optional[ScoresOutput] = Field(default=None, description="Score période pré-rut")
    rut: Optional[ScoresOutput] = Field(default=None, description="Score période rut (pic)")
    post_rut: Optional[ScoresOutput] = Field(default=None, description="Score période post-rut")
    active_mode: str = Field(default="live", description="Mode actif pour ce calcul")


# =============================================================================
# RESPONSE MODELS - LAYERS
# =============================================================================

class Geometry(BaseModel):
    """Géométrie GeoJSON."""
    type: str = Field(..., description="Type: Polygon, LineString, Point")
    coordinates: List[Any] = Field(..., description="Coordonnées")
    point_count: Optional[int] = Field(default=None, description="Nombre de points")


class RenderingStyle(BaseModel):
    """Style de rendu cartographique."""
    fill_color: Optional[str] = Field(default=None, description="Couleur de remplissage")
    fill_opacity: Optional[float] = Field(default=None, ge=0, le=1, description="Opacité de remplissage")
    stroke_color: Optional[str] = Field(default=None, description="Couleur de contour")
    stroke_width: Optional[float] = Field(default=None, description="Épaisseur de contour")
    dash_array: Optional[str] = Field(default=None, description="Motif de tirets")


class BehavioralZone(BaseModel):
    """Zone comportementale organique."""
    zone_id: str = Field(..., description="Identifiant unique")
    organic: bool = Field(default=True, description="Pipeline organique appliqué")
    geometry: Geometry = Field(..., description="Géométrie organique")
    properties: Dict[str, Any] = Field(..., description="Propriétés de la zone")
    rendering: RenderingStyle = Field(..., description="Style de rendu")


class MovementCorridor(BaseModel):
    """Corridor de mouvement."""
    corridor_id: str = Field(..., description="Identifiant unique")
    organic: bool = Field(default=True, description="Pipeline organique appliqué")
    geometry: Geometry = Field(..., description="Géométrie LineString")
    properties: Dict[str, Any] = Field(..., description="Propriétés du corridor")
    rendering: RenderingStyle = Field(..., description="Style de rendu")


class BehavioralZonesLayer(BaseModel):
    """Famille de couches comportementales."""
    bedding_zones: List[BehavioralZone] = Field(default_factory=list, description="Zones de repos")
    feeding_zones: List[BehavioralZone] = Field(default_factory=list, description="Zones d'alimentation")
    rut_zones: List[BehavioralZone] = Field(default_factory=list, description="Zones de rut")
    movement_corridors: List[MovementCorridor] = Field(default_factory=list, description="Corridors")
    pressure_avoidance: List[BehavioralZone] = Field(default_factory=list, description="Zones d'évitement")


class AttractionPoint(BaseModel):
    """Point d'attraction."""
    point_id: str = Field(..., description="Identifiant unique")
    coordinates: Dict[str, float] = Field(..., description="lat/lng")
    type: Optional[str] = Field(default=None, description="Type de point")
    score: Optional[float] = Field(default=None, description="Score")
    distance_m: Optional[float] = Field(default=None, description="Distance en mètres")
    confirmed: Optional[bool] = Field(default=None, description="Confirmé")


class ThermalRefuge(BaseModel):
    """Refuge thermique."""
    zone_id: str = Field(..., description="Identifiant unique")
    geometry: Geometry = Field(..., description="Géométrie")
    temperature_delta: Optional[float] = Field(default=None, description="Delta température")


class AttractionPointsLayer(BaseModel):
    """Famille de couches de points d'attraction."""
    salines: List[AttractionPoint] = Field(default_factory=list, description="Salines")
    water_sources: List[AttractionPoint] = Field(default_factory=list, description="Sources d'eau")
    thermal_refuges: List[ThermalRefuge] = Field(default_factory=list, description="Refuges thermiques")
    affuts_potentiels: List[AttractionPoint] = Field(default_factory=list, description="Affûts potentiels")


class SlopeAnalysis(BaseModel):
    """Analyse des pentes."""
    average_degrees: float = Field(..., description="Pente moyenne")
    max_degrees: float = Field(..., description="Pente maximale")
    distribution: Dict[str, float] = Field(..., description="Distribution par classe")


class AltitudeAnalysis(BaseModel):
    """Analyse d'altitude relative."""
    waypoint_elevation_m: float = Field(..., description="Altitude du waypoint")
    min_m: float = Field(..., description="Altitude minimale")
    max_m: float = Field(..., description="Altitude maximale")
    range_m: float = Field(..., description="Amplitude")


class OrientationAnalysis(BaseModel):
    """Analyse d'orientation."""
    dominant: str = Field(..., description="Orientation dominante")
    degrees: float = Field(..., description="Degrés")
    distribution: Dict[str, float] = Field(..., description="Distribution par direction")


class SolarExposure(BaseModel):
    """Analyse d'ensoleillement."""
    current_exposure: float = Field(..., ge=0, le=1, description="Exposition actuelle")
    dawn_quality: float = Field(..., ge=0, le=1, description="Qualité à l'aube")
    dusk_quality: float = Field(..., ge=0, le=1, description="Qualité au crépuscule")
    shade_zones_pct: float = Field(..., ge=0, le=1, description="Pourcentage zones ombragées")


class WaterProximity(BaseModel):
    """Proximité à l'eau."""
    nearest_water_m: float = Field(..., description="Distance eau la plus proche")
    water_type: str = Field(..., description="Type d'eau")
    water_coverage_pct: float = Field(..., ge=0, le=1, description="Couverture eau")


class SoilMoisture(BaseModel):
    """Humidité du sol."""
    twi_index: float = Field(..., ge=0, le=1, description="Index TWI")
    moisture_class: str = Field(..., description="Classe d'humidité")
    wetland_proximity_m: float = Field(..., description="Proximité zone humide")


class TerrainAnalysisLayer(BaseModel):
    """Famille de couches d'analyse terrain."""
    slopes: SlopeAnalysis = Field(..., description="Analyse des pentes")
    altitude_relative: AltitudeAnalysis = Field(..., description="Altitude relative")
    orientation: OrientationAnalysis = Field(..., description="Orientation")
    solar_exposure: SolarExposure = Field(..., description="Ensoleillement")
    water_proximity: WaterProximity = Field(..., description="Proximité eau")
    soil_moisture: SoilMoisture = Field(..., description="Humidité sol")


class NDVIAnalysis(BaseModel):
    """Analyse NDVI."""
    average: float = Field(..., ge=0, le=1, description="NDVI moyen")
    min: float = Field(..., ge=0, le=1, description="NDVI minimum")
    max: float = Field(..., ge=0, le=1, description="NDVI maximum")
    healthy_vegetation_pct: float = Field(..., ge=0, le=1, description="Végétation saine")


class ForestStands(BaseModel):
    """Peuplements forestiers."""
    dominant_type: str = Field(..., description="Type dominant")
    distribution: Dict[str, float] = Field(..., description="Distribution")
    canopy_closure: float = Field(..., ge=0, le=1, description="Fermeture canopée")


class EdgeTransition(BaseModel):
    """Transition de peuplement."""
    transition_id: str = Field(..., description="Identifiant")
    from_type: str = Field(..., alias="from", description="Type source")
    to_type: str = Field(..., alias="to", description="Type destination")
    distance_m: float = Field(..., description="Distance")
    quality: float = Field(..., ge=0, le=1, description="Qualité")


class VegetationAnalysisLayer(BaseModel):
    """Famille de couches d'analyse végétation."""
    ndvi: NDVIAnalysis = Field(..., description="Analyse NDVI")
    forest_stands: ForestStands = Field(..., description="Peuplements forestiers")
    edge_transitions: List[EdgeTransition] = Field(default_factory=list, description="Transitions")
    cover_types: List[str] = Field(default_factory=list, description="Types de couvert")


class OptimalRoute(BaseModel):
    """Route optimale de chasse."""
    route_id: str = Field(..., description="Identifiant")
    geometry: Geometry = Field(..., description="Géométrie")
    distance_m: float = Field(..., description="Distance")
    difficulty: str = Field(..., description="Difficulté")
    stealth_score: float = Field(..., ge=0, le=1, description="Score discrétion")


class StandPosition(BaseModel):
    """Position d'affût."""
    position_id: str = Field(..., description="Identifiant")
    coordinates: Dict[str, float] = Field(..., description="lat/lng")
    type: str = Field(..., description="Type d'affût")
    score: float = Field(..., description="Score")


class AccessibilityAnalysis(BaseModel):
    """Analyse d'accessibilité."""
    nearest_road_m: float = Field(..., description="Distance route")
    nearest_trail_m: float = Field(..., description="Distance sentier")
    parking_available: bool = Field(..., description="Stationnement disponible")
    access_difficulty: str = Field(..., description="Difficulté d'accès")


class Trail(BaseModel):
    """Sentier."""
    trail_id: str = Field(..., description="Identifiant")
    geometry: Geometry = Field(..., description="Géométrie")
    type: str = Field(..., description="Type de sentier")
    condition: str = Field(..., description="Condition")


class HuntPlanningLayer(BaseModel):
    """Famille de couches de planification de chasse."""
    optimal_routes: List[OptimalRoute] = Field(default_factory=list, description="Routes optimales")
    stand_positions: List[StandPosition] = Field(default_factory=list, description="Positions d'affût")
    accessibility: AccessibilityAnalysis = Field(..., description="Accessibilité")
    trails: List[Trail] = Field(default_factory=list, description="Sentiers")


class LayersOutput(BaseModel):
    """Structure complète des 5 familles de layers."""
    behavioral_zones: BehavioralZonesLayer = Field(..., description="Zones comportementales")
    attraction_points: AttractionPointsLayer = Field(..., description="Points d'attraction")
    terrain_analysis: TerrainAnalysisLayer = Field(..., description="Analyse terrain")
    vegetation_analysis: VegetationAnalysisLayer = Field(..., description="Analyse végétation")
    hunt_planning: HuntPlanningLayer = Field(..., description="Planification chasse")


# =============================================================================
# RESPONSE MODELS - HEATMAP
# =============================================================================

class HeatmapBounds(BaseModel):
    """Limites géographiques de la heatmap."""
    north: float = Field(..., description="Latitude nord")
    south: float = Field(..., description="Latitude sud")
    east: float = Field(..., description="Longitude est")
    west: float = Field(..., description="Longitude ouest")


class HeatmapCell(BaseModel):
    """Cellule de la grille heatmap."""
    row: int = Field(..., description="Ligne")
    col: int = Field(..., description="Colonne")
    lat: float = Field(..., description="Latitude centre")
    lng: float = Field(..., description="Longitude centre")
    score: float = Field(..., ge=0, le=100, description="Score fusionné")
    level: ScoreLevel = Field(..., description="Niveau")
    color: str = Field(..., description="Couleur hex")


class ColorScaleLevel(BaseModel):
    """Niveau de l'échelle de couleurs."""
    min: float = Field(..., description="Score minimum")
    max: float = Field(..., description="Score maximum")
    color: str = Field(..., description="Couleur hex")


class ColorScale(BaseModel):
    """Échelle de couleurs BIONIC."""
    excellent: ColorScaleLevel = Field(..., description="85-100")
    good: ColorScaleLevel = Field(..., description="70-84")
    moderate: ColorScaleLevel = Field(..., description="50-69")
    poor: ColorScaleLevel = Field(..., description="30-49")
    critical: ColorScaleLevel = Field(..., description="0-29")


class HeatmapOutput(BaseModel):
    """Grille heatmap fusionnée."""
    bounds: HeatmapBounds = Field(..., description="Limites géographiques")
    resolution: int = Field(..., description="Résolution de la grille")
    cell_size_m: float = Field(..., description="Taille des cellules en mètres")
    grid: List[HeatmapCell] = Field(..., description="Cellules de la grille")
    color_scale: ColorScale = Field(..., description="Échelle de couleurs")


# =============================================================================
# RESPONSE MODELS - LEGAL STATUS
# =============================================================================

class LegalStatusOutput(BaseModel):
    """Statut de conformité légale."""
    is_legal_period: bool = Field(..., description="Période légale active")
    legal_status: str = Field(..., description="Statut détaillé")
    sunrise: str = Field(..., description="Heure lever soleil")
    sunset: str = Field(..., description="Heure coucher soleil")
    legal_start: str = Field(..., description="Début période légale")
    legal_end: str = Field(..., description="Fin période légale")
    legal_badge: str = Field(..., description="Badge: LEGAL ou HORS_HEURES")
    temporal_factor: float = Field(..., ge=0, le=1, description="Facteur temporel")
    next_legal_window: Optional[str] = Field(default=None, description="Prochaine fenêtre légale")


# =============================================================================
# RESPONSE MODELS - OPTIMAL WINDOWS
# =============================================================================

class OptimalWindow(BaseModel):
    """Fenêtre temporelle optimale."""
    period: str = Field(..., description="Période: dawn, day, dusk, night")
    time_range: str = Field(..., description="Plage horaire")
    score: float = Field(..., ge=0, le=100, description="Score")
    quality: str = Field(..., description="Qualité: excellent, good, moderate")
    species_activity: str = Field(..., description="Activité espèce")
    legal_badge: str = Field(..., description="Badge légal")
    recommendation: str = Field(..., description="Recommandation")


# =============================================================================
# RESPONSE MODELS - METADATA
# =============================================================================

class VisualizationApplied(BaseModel):
    """Paramètres de visualisation appliqués."""
    organic_applied: bool = Field(..., description="Pipeline organique appliqué")
    smoothing_factor: float = Field(..., description="Facteur de lissage utilisé")
    terrain_adaptation: bool = Field(..., description="Adaptation terrain appliquée")
    water_exclusion: bool = Field(..., description="Exclusion eau appliquée")


class MetadataOutput(BaseModel):
    """Métadonnées de l'analyse."""
    processing_time_ms: int = Field(..., description="Temps de traitement en ms")
    data_sources: List[str] = Field(..., description="Sources de données utilisées")
    fallbacks_used: List[str] = Field(default_factory=list, description="Fallbacks utilisés")
    missing_data: List[str] = Field(default_factory=list, description="Données manquantes")
    confidence_impact: float = Field(..., ge=0, le=1, description="Impact sur la confiance")
    cache_hit: bool = Field(..., description="Cache utilisé")


# =============================================================================
# MAIN RESPONSE MODEL
# =============================================================================

class WaypointOutput(BaseModel):
    """Waypoint dans la réponse."""
    id: str = Field(..., description="Identifiant")
    name: str = Field(..., description="Nom")
    coordinates: Dict[str, float] = Field(..., description="lat/lng")


class ContractInfo(BaseModel):
    """Informations contractuelles de l'API."""
    structure: str = Field(default="scores + layers + heatmap + legal_status + optimal_windows + recommendations")
    stability: str = Field(default="stable")
    breaking_changes: List[str] = Field(default_factory=list)


# =============================================================================
# RESPONSE MODELS - CORRIDORS (NIVEAU 4)
# =============================================================================

class CorridorTypeEnum(str, Enum):
    """Types de corridors NIVEAU 4."""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    SEASONAL = "seasonal"
    THERMAL = "thermal"
    RISK = "risk"


class CorridorRenderingStyle(BaseModel):
    """Style de rendu pour un corridor."""
    stroke_color: str = Field(..., description="Couleur du trait")
    stroke_opacity: float = Field(default=1.0, description="Opacité")
    stroke_width: int = Field(default=3, description="Épaisseur en px")
    dash_array: Optional[str] = Field(default=None, description="Pattern pointillé")
    line_cap: str = Field(default="round", description="Style de fin de ligne")
    line_join: str = Field(default="round", description="Style de jonction")
    halo_color: Optional[str] = Field(default=None, description="Couleur du halo")
    halo_opacity: Optional[float] = Field(default=None, description="Opacité du halo")
    halo_weight: Optional[int] = Field(default=None, description="Épaisseur du halo")


class CorridorFactors(BaseModel):
    """Facteurs d'influence sur un corridor."""
    habitat: float = Field(default=50.0, description="Score habitat")
    edge: float = Field(default=50.0, description="Score lisières")
    thermal_stress: float = Field(default=50.0, description="Score stress thermique")
    pres_human: float = Field(default=50.0, description="Score pression humaine")
    behavior: float = Field(default=50.0, description="Score comportement")
    seasonal: float = Field(default=50.0, description="Score saisonnier")


class CorridorProperties(BaseModel):
    """Propriétés d'un corridor."""
    corridor_id: str = Field(..., description="Identifiant du corridor")
    corridor_type: str = Field(..., description="Type de corridor")
    priority: str = Field(..., description="Priorité d'utilisation")
    name: str = Field(..., description="Nom descriptif")
    description: str = Field(default="", description="Description")
    quality: str = Field(..., description="Qualité du corridor")
    composite_score: float = Field(..., description="Score composite")
    total_length_m: float = Field(..., description="Longueur totale en mètres")
    average_quality: float = Field(..., description="Qualité moyenne")
    factors: CorridorFactors = Field(..., description="Facteurs d'influence")
    active_seasons: List[str] = Field(default_factory=list, description="Saisons actives")
    active_hours: List[int] = Field(default_factory=list, description="Heures actives")
    rendering: CorridorRenderingStyle = Field(..., description="Style de rendu")
    source_ids: List[str] = Field(default_factory=list, description="Sources traçabilité")
    version: str = Field(default="1.0.0", description="Version")


class CorridorFeature(BaseModel):
    """Feature GeoJSON pour un corridor."""
    type: str = Field(default="Feature", description="Type GeoJSON")
    geometry: Geometry = Field(..., description="Géométrie LineString")
    properties: CorridorProperties = Field(..., description="Propriétés")


class CorridorStatistics(BaseModel):
    """Statistiques du réseau de corridors."""
    total_corridors: int = Field(..., description="Nombre total de corridors")
    total_length_km: float = Field(..., description="Longueur totale en km")
    average_quality: float = Field(..., description="Qualité moyenne")
    by_type: Dict[str, int] = Field(default_factory=dict, description="Nombre par type")


class CorridorNetworkProperties(BaseModel):
    """Propriétés du réseau de corridors."""
    network_id: str = Field(..., description="Identifiant du réseau")
    waypoint_id: str = Field(..., description="Waypoint de référence")
    center: Dict[str, float] = Field(..., description="Centre lat/lng")
    search_radius_km: float = Field(..., description="Rayon de recherche")
    statistics: CorridorStatistics = Field(..., description="Statistiques")
    species: str = Field(..., description="Espèce cible")
    analysis_datetime: str = Field(..., description="Date/heure d'analyse")
    source_ids: List[str] = Field(default_factory=list, description="Sources traçabilité")
    version: str = Field(default="1.0.0", description="Version")


class CorridorsOutput(BaseModel):
    """
    Réseau complet de corridors (NIVEAU 4).
    
    Format GeoJSON FeatureCollection avec tous les types de corridors:
    - primary (principaux)
    - secondary (secondaires)
    - seasonal (saisonniers)
    - thermal (thermiques)
    - risk (à risque)
    """
    type: str = Field(default="FeatureCollection", description="Type GeoJSON")
    features: List[CorridorFeature] = Field(default_factory=list, description="Corridors")
    properties: CorridorNetworkProperties = Field(..., description="Propriétés du réseau")


class WaypointAnalysisResponse(BaseModel):
    """
    Réponse complète de l'analyse waypoint-centric.
    
    Structure contractuelle BIONIC V5:
    - scores: Score final + breakdown des 9 composants
    - layers: 5 familles de couches géospatiales
    - corridors: Réseau de corridors de déplacement (NIVEAU 4)
    - heatmap: Grille fusionnée WQS + SCORE_FINAL
    - legal_status: Conformité heures légales
    - optimal_windows: Fenêtres recommandées
    - recommendations: Conseils textuels
    """
    # Versionnement
    api_schema_version: str = Field(default="1.0.0", description="Version du schéma API")
    model_version: str = Field(default="BIONIC-V5.1", description="Version du modèle")
    engine_version: str = Field(..., description="Version du moteur")
    
    # Identification
    analysis_id: str = Field(..., description="Identifiant unique de l'analyse")
    calculated_at: datetime = Field(..., description="Date/heure de calcul")
    
    # Waypoint
    waypoint: WaypointOutput = Field(..., description="Waypoint analysé")
    
    # Scores
    scores: ScoresOutput = Field(..., description="Scores complets")
    
    # Layers (5 familles)
    layers: LayersOutput = Field(..., description="Couches géospatiales")
    
    # Corridors (NIVEAU 4 - Habitat & Corridors)
    corridors: Optional[CorridorsOutput] = Field(default=None, description="Réseau de corridors de déplacement")
    
    # Heatmap
    heatmap: HeatmapOutput = Field(..., description="Grille heatmap")
    
    # Légalité
    legal_status: LegalStatusOutput = Field(..., description="Statut légal")
    
    # Fenêtres optimales
    optimal_windows: List[OptimalWindow] = Field(..., description="Fenêtres optimales")
    
    # Recommandations
    recommendations: List[str] = Field(..., description="Recommandations textuelles")
    
    # Visualisation
    visualization: VisualizationApplied = Field(..., description="Paramètres visualisation")
    
    # Métadonnées
    metadata: MetadataOutput = Field(..., description="Métadonnées")
    
    # Contrat
    contract: ContractInfo = Field(default_factory=ContractInfo, description="Info contractuelle")
    
    class Config:
        json_schema_extra = {
            "example": {
                "api_schema_version": "1.0.0",
                "analysis_id": "WPA-20251015-063045-X7K9",
                "calculated_at": "2025-10-15T06:30:45Z",
                "model_version": "BIONIC-V5.1",
                "engine_version": "2026.02.23"
            }
        }


# =============================================================================
# ERROR MODELS
# =============================================================================

class ErrorDetail(BaseModel):
    """Détail d'une erreur."""
    code: str = Field(..., description="Code erreur")
    message: str = Field(..., description="Message")
    field: Optional[str] = Field(default=None, description="Champ concerné")


class ErrorResponse(BaseModel):
    """Réponse d'erreur."""
    error: bool = Field(default=True)
    error_code: str = Field(..., description="Code erreur principal")
    message: str = Field(..., description="Message d'erreur")
    details: List[ErrorDetail] = Field(default_factory=list, description="Détails")
    timestamp: datetime = Field(..., description="Horodatage")

