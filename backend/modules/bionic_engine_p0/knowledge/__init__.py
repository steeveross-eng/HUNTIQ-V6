"""
BIONIC V5 — KNOWLEDGE LAYER
============================
PHASE 7 — Architecture Principale

Le Knowledge Layer est le référentiel central de toutes les connaissances
scientifiques et empiriques utilisées par le moteur BIONIC V5.

PRINCIPES FONDAMENTAUX:
1. Toute règle comportementale DOIT être traçable à une source
2. Toute pondération DOIT être justifiée et documentée
3. Tout modèle DOIT avoir un niveau de confiance documenté
4. Aucune donnée arbitraire n'est acceptée

STRUCTURE:
- sources/: Schémas de traçabilité scientifique
- species/: Règles comportementales par espèce
- weights/: Pondérations d'habitat sourcées
- seasonal/: Modèles saisonniers calibrés
- validation/: Pipeline de validation terrain + données terrain (PHASE A)

STATUT: PRODUCTION
VERSION: 1.1.0
Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
"""

from .sources.scientific_sources_schema import (
    ScientificSource,
    SourceType,
    ValidationStatus,
    ConfidenceLevel,
    SourceRegistry,
    get_source_registry
)

from .species import (
    MooseRules,
    DeerRules,
    MuleDeerRules,
    BearRules,
    ElkRules,
    get_species_rules
)

from .weights.habitat_weights import (
    HabitatWeight,
    HabitatWeightRegistry,
    get_habitat_weights
)

from .seasonal.seasonal_models import (
    SeasonalModel,
    SeasonType,
    SeasonalModelRegistry,
    get_seasonal_model
)

from .validation.validation_pipeline import (
    ValidationPipeline,
    ValidationResult,
    ValidationSource,
    get_validation_pipeline
)

# PHASE A — Données Terrain
from .validation.terrain_data import (
    TerrainDataRegistry,
    get_terrain_data_registry,
    CameraEvent,
    GPSFix,
    HumanTrace,
    WildlifeTrace,
    TerrainFlag,
    Corridor
)

__all__ = [
    # Sources
    'ScientificSource',
    'SourceType',
    'ValidationStatus',
    'ConfidenceLevel',
    'SourceRegistry',
    'get_source_registry',
    # Species
    'MooseRules',
    'DeerRules',
    'MuleDeerRules',
    'BearRules',
    'ElkRules',
    'get_species_rules',
    # Weights
    'HabitatWeight',
    'HabitatWeightRegistry',
    'get_habitat_weights',
    # Seasonal
    'SeasonalModel',
    'SeasonType',
    'SeasonalModelRegistry',
    'get_seasonal_model',
    # Validation
    'ValidationPipeline',
    'ValidationResult',
    'ValidationSource',
    'get_validation_pipeline',
    # Terrain Data (PHASE A)
    'TerrainDataRegistry',
    'get_terrain_data_registry',
    'CameraEvent',
    'GPSFix',
    'HumanTrace',
    'WildlifeTrace',
    'TerrainFlag',
    'Corridor'
]

__version__ = "1.1.0"
__author__ = "BIONIC V5 Team"
