"""
BIONIC Engine Base — Interface commune pour tous les moteurs BIONIC
===================================================================
Chaque moteur doit heriter de BionicEngine et implementer evaluate().

Un moteur retourne:
  - score (0-100)
  - weight (poids dans le composite)
  - justification (texte ecologique/comportemental)
  - classification_impact (influence sur le niveau du corridor)
  - certainty (0-1, confiance du modele)
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List
import math

METERS_PER_DEG = 111320.0


@dataclass
class EngineResult:
    """Resultat d'evaluation d'un moteur BIONIC."""
    engine_id: str
    score: float  # 0-100
    weight: float  # poids dans le composite
    certainty: float  # 0-1
    justification: str
    classification_impact: int  # -2 a +2
    details: Dict[str, Any] = field(default_factory=dict)


class BionicEngine:
    ENGINE_ID: str = "base"
    ENGINE_NAME: str = "Base"
    DEFAULT_WEIGHT: float = 0.1

    def evaluate(self, context: Dict[str, Any]) -> EngineResult:
        raise NotImplementedError

    @staticmethod
    def haversine_m(lat1, lon1, lat2, lon2):
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
        return 6371000 * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
