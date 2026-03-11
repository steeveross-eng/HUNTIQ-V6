"""BIONIC V5 — Validation Pipeline Module"""
from .validation_pipeline import (
    ValidationSource,
    ValidationOutcome,
    ValidationDataPoint,
    ValidationResult,
    CameraStation,
    GPSCollar,
    ValidationPipeline,
    get_validation_pipeline
)

from .terrain_data import (
    # Enums
    TerrainDataType,
    CameraEventType,
    HumanTraceType,
    WildlifeTraceType,
    TerrainFlagType,
    DataQualityLevel,
    # Data models
    CameraEvent,
    GPSFix,
    HumanTrace,
    WildlifeTrace,
    TerrainFlag,
    Corridor,
    # Registry
    TerrainDataRegistry,
    get_terrain_data_registry
)

__all__ = [
    # Validation Pipeline
    'ValidationSource',
    'ValidationOutcome',
    'ValidationDataPoint',
    'ValidationResult',
    'CameraStation',
    'GPSCollar',
    'ValidationPipeline',
    'get_validation_pipeline',
    # Terrain Data (PHASE A)
    'TerrainDataType',
    'CameraEventType',
    'HumanTraceType',
    'WildlifeTraceType',
    'TerrainFlagType',
    'DataQualityLevel',
    'CameraEvent',
    'GPSFix',
    'HumanTrace',
    'WildlifeTrace',
    'TerrainFlag',
    'Corridor',
    'TerrainDataRegistry',
    'get_terrain_data_registry'
]
