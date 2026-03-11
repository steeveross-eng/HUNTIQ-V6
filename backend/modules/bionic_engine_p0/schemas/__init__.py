"""
BIONIC ENGINE — Schemas Package
================================
Schémas Pydantic pour la validation des entrées/sorties API.

Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
"""

from .waypoint_analysis_schemas import (
    # Enums
    DataQuality,
    ScoreLevel,
    ZoneType,
    AttractionType,
    FusionMode,
    AnalysisMode,
    CorridorTypeEnum,
    
    # Request models
    WaypointInput,
    WQSInput,
    AnalysisParameters,
    VisualizationParameters,
    WeatherInput,
    TemporalParameters,
    WaypointAnalysisRequest,
    
    # Response models - Scores
    ScoreComponent,
    ScoreBreakdown,
    FusionContribution,
    ScoreFusion,
    ScoreCategory,
    ScoresOutput,
    DualModeScores,
    
    # Response models - Layers
    Geometry,
    RenderingStyle,
    BehavioralZone,
    MovementCorridor,
    BehavioralZonesLayer,
    AttractionPoint,
    ThermalRefuge,
    AttractionPointsLayer,
    SlopeAnalysis,
    AltitudeAnalysis,
    OrientationAnalysis,
    SolarExposure,
    WaterProximity,
    SoilMoisture,
    TerrainAnalysisLayer,
    NDVIAnalysis,
    ForestStands,
    EdgeTransition,
    VegetationAnalysisLayer,
    OptimalRoute,
    StandPosition,
    AccessibilityAnalysis,
    Trail,
    HuntPlanningLayer,
    LayersOutput,
    
    # Response models - Corridors (NIVEAU 4)
    CorridorRenderingStyle,
    CorridorFactors,
    CorridorProperties,
    CorridorFeature,
    CorridorStatistics,
    CorridorNetworkProperties,
    CorridorsOutput,
    
    # Response models - Heatmap
    HeatmapBounds,
    HeatmapCell,
    ColorScaleLevel,
    ColorScale,
    HeatmapOutput,
    
    # Response models - Other
    LegalStatusOutput,
    OptimalWindow,
    VisualizationApplied,
    MetadataOutput,
    WaypointOutput,
    ContractInfo,
    
    # Main response
    WaypointAnalysisResponse,
    
    # Errors
    ErrorDetail,
    ErrorResponse
)

__all__ = [
    # Enums
    'DataQuality',
    'ScoreLevel',
    'ZoneType',
    'AttractionType',
    'FusionMode',
    'AnalysisMode',
    'CorridorTypeEnum',
    
    # Request
    'WaypointInput',
    'WQSInput',
    'AnalysisParameters',
    'VisualizationParameters',
    'WeatherInput',
    'TemporalParameters',
    'WaypointAnalysisRequest',
    
    # Response - Scores
    'ScoreComponent',
    'ScoreBreakdown',
    'FusionContribution',
    'ScoreFusion',
    'ScoreCategory',
    'ScoresOutput',
    'DualModeScores',
    
    # Response - Layers
    'Geometry',
    'RenderingStyle',
    'BehavioralZone',
    'MovementCorridor',
    'BehavioralZonesLayer',
    'AttractionPoint',
    'ThermalRefuge',
    'AttractionPointsLayer',
    'SlopeAnalysis',
    'AltitudeAnalysis',
    'OrientationAnalysis',
    'SolarExposure',
    'WaterProximity',
    'SoilMoisture',
    'TerrainAnalysisLayer',
    'NDVIAnalysis',
    'ForestStands',
    'EdgeTransition',
    'VegetationAnalysisLayer',
    'OptimalRoute',
    'StandPosition',
    'AccessibilityAnalysis',
    'Trail',
    'HuntPlanningLayer',
    'LayersOutput',
    
    # Response - Corridors (NIVEAU 4)
    'CorridorRenderingStyle',
    'CorridorFactors',
    'CorridorProperties',
    'CorridorFeature',
    'CorridorStatistics',
    'CorridorNetworkProperties',
    'CorridorsOutput',
    
    # Response - Heatmap
    'HeatmapBounds',
    'HeatmapCell',
    'ColorScaleLevel',
    'ColorScale',
    'HeatmapOutput',
    
    # Response - Other
    'LegalStatusOutput',
    'OptimalWindow',
    'VisualizationApplied',
    'MetadataOutput',
    'WaypointOutput',
    'ContractInfo',
    
    # Main
    'WaypointAnalysisResponse',
    
    # Errors
    'ErrorDetail',
    'ErrorResponse'
]
