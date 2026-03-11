"""
BIONIC Knowledge Engine - V5-ULTIME
===================================

Module centralisé de connaissances scientifiques et empiriques pour BIONIC™.
Architecture LEGO V5 stricte - Module isolé, autonome et testable.

Composants:
- knowledge_router.py: Routes API
- knowledge_service.py: Logique métier
- knowledge_models.py: Modèles Pydantic
- knowledge_sources.py: Gestion des sources
- knowledge_rules.py: Règles comportementales
- knowledge_seasonal_models.py: Modèles saisonniers
- knowledge_validation_pipeline.py: Pipeline de validation

Version: 1.0.0
"""

from .knowledge_router import router
from .knowledge_service import KnowledgeService
from .knowledge_models import (
    SpeciesKnowledge,
    BehaviorRule,
    HabitatVariable,
    SeasonalModel,
    KnowledgeSource
)

__all__ = [
    "router",
    "KnowledgeService",
    "SpeciesKnowledge",
    "BehaviorRule",
    "HabitatVariable",
    "SeasonalModel",
    "KnowledgeSource"
]

__version__ = "1.0.0"
__module__ = "bionic_knowledge_engine"
