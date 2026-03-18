"""
ENGINE REGISTRY — Interface commune BionicEngine
===================================================
Norme BCE-4X + STEEVE-MAX
Chaque moteur écologique DOIT implémenter cette interface.

Mapping espèces unifié:
  CHEVREUIL | ORIGNAL | OURS | DINDON | WAPITI
  (Interdiction d'utiliser "cerf", "deer", "moose", etc.)
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import List, Optional


# ══════════════════════════════════════════════════════════
# MAPPING ESPÈCES UNIFIÉ — SOURCE DE VÉRITÉ UNIQUE
# ══════════════════════════════════════════════════════════
SPECIES_CANONICAL = ["CHEVREUIL", "ORIGNAL", "OURS", "DINDON", "WAPITI"]

SPECIES_ALIASES = {
    # Français courant
    "cerf": "CHEVREUIL", "chevreuil": "CHEVREUIL",
    "orignal": "ORIGNAL", "elan": "ORIGNAL",
    "ours": "OURS", "ours_noir": "OURS",
    "dindon": "DINDON", "dindon_sauvage": "DINDON",
    "wapiti": "WAPITI",
    # Anglais (legacy habitat_score_service)
    "deer": "CHEVREUIL", "whitetail": "CHEVREUIL",
    "moose": "ORIGNAL",
    "bear": "OURS", "black_bear": "OURS",
    "turkey": "DINDON", "wild_turkey": "DINDON",
    "elk": "WAPITI",
    # IDs frontend legacy
    "tous": "CHEVREUIL",
}


def resolve_species(raw: str) -> str:
    """Résout n'importe quel alias vers l'espèce canonique BCE-4X."""
    key = raw.strip().lower()
    if key.upper() in SPECIES_CANONICAL:
        return key.upper()
    return SPECIES_ALIASES.get(key, "CHEVREUIL")


# ══════════════════════════════════════════════════════════
# MÉTADONNÉES OBLIGATOIRES (BCE-4X §4)
# ══════════════════════════════════════════════════════════
@dataclass
class EngineMeta:
    """Métadonnées obligatoires pour chaque moteur."""
    name: str
    version: str
    engine_type: str          # "score" | "spatial" | "composite"
    domain: str               # "alimentation" | "repos" | "corridors" | "pression" | "habitat"
    species_supported: List[str] = field(default_factory=lambda: list(SPECIES_CANONICAL))
    unit: str = "score_0_100"
    default_weight: float = 0.20
    description: str = ""
    seasonal_modifiers: bool = False

    def to_dict(self):
        return asdict(self)


@dataclass
class EngineScore:
    """Résultat normalisé d'un moteur pour un point."""
    score: float              # 0-100
    components: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


@dataclass
class GridResult:
    """Résultat d'une grille de scores."""
    center_lat: float
    center_lng: float
    species: str
    month: int
    grid_size: int
    points: list = field(default_factory=list)
    score_avg: float = 0.0
    score_min: float = 0.0
    score_max: float = 0.0

    def to_dict(self):
        return asdict(self)


# ══════════════════════════════════════════════════════════
# INTERFACE COMMUNE — Contrat obligatoire BCE-4X
# ══════════════════════════════════════════════════════════
class BionicEngine(ABC):
    """
    Interface commune pour tous les moteurs écologiques BIONIC.
    Chaque moteur DOIT implémenter: meta(), score_point(), score_grid().
    """

    @abstractmethod
    def meta(self) -> EngineMeta:
        """Retourne les métadonnées du moteur."""

    @abstractmethod
    def score_point(self, lat: float, lng: float, species: str, month: int) -> EngineScore:
        """Score normalisé 0-100 pour un point unique."""

    @abstractmethod
    def score_grid(
        self, center_lat: float, center_lng: float,
        species: str, month: int, grid_size: int = 20
    ) -> GridResult:
        """Grille de scores pour visualisation / consolidation."""

    def is_species_supported(self, species: str) -> bool:
        """Vérifie si l'espèce est supportée par ce moteur."""
        return resolve_species(species) in self.meta().species_supported
