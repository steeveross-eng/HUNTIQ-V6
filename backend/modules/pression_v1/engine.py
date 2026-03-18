"""
PRESSION-V1 — Moteur de pression humaine
==========================================
Extrait de score_consolide.py — moteur dédié conforme BionicEngine.
BCE-4X: Calcul déterministe basé sur distance routes/bâtiments.
"""
from modules.engine_registry.base import (
    BionicEngine, EngineMeta, EngineScore, GridResult, resolve_species,
)
from modules.alimentation_v1.layers import load_layers
import math


# Mapping interne CHEVREUIL → CERF pour les couches V1 legacy
_LEGACY_MAP = {
    "CHEVREUIL": "CERF", "ORIGNAL": "ORIGNAL",
    "OURS": "OURS", "DINDON": "DINDON", "WAPITI": "WAPITI",
}


def _compute_pression(lat: float, lng: float, month: int) -> float:
    """Score pression humaine 0-100. Plus c'est haut, moins il y a de pression."""
    layers = load_layers(lat, lng, month)
    pert = layers.get("perturbations", {})
    dist_route = pert.get("distance_route_m", 200)
    dist_bat = pert.get("distance_batiment_m", 300)
    return min(100.0, (dist_route / 8.0) + (dist_bat / 10.0))


class PressionV1Engine(BionicEngine):
    """Moteur PRESSION-V1 — Évalue l'éloignement des perturbations humaines."""

    def meta(self) -> EngineMeta:
        return EngineMeta(
            name="PRESSION-V1",
            version="1.0.0",
            engine_type="score",
            domain="pression",
            unit="score_0_100",
            default_weight=0.20,
            description="Éloignement des perturbations humaines (routes, bâtiments)",
            seasonal_modifiers=False,
        )

    def score_point(self, lat: float, lng: float, species: str, month: int) -> EngineScore:
        sp = resolve_species(species)
        score = _compute_pression(lat, lng, month)
        return EngineScore(
            score=round(score, 1),
            components={"distance_route": 0, "distance_batiment": 0},
            metadata={"engine": "PRESSION-V1", "species": sp, "month": month},
        )

    def score_grid(
        self, center_lat: float, center_lng: float,
        species: str, month: int, grid_size: int = 20,
    ) -> GridResult:
        sp = resolve_species(species)
        side_m = 2000.0
        half = side_m / 2.0
        lat_step = (side_m / grid_size) / 111320.0
        lng_step = (side_m / grid_size) / (111320.0 * math.cos(math.radians(center_lat)))
        lat_start = center_lat - half / 111320.0
        lng_start = center_lng - half / (111320.0 * math.cos(math.radians(center_lat)))

        points = []
        scores = []
        for r in range(grid_size):
            for c in range(grid_size):
                lat = lat_start + (r + 0.5) * lat_step
                lng = lng_start + (c + 0.5) * lng_step
                s = _compute_pression(lat, lng, month)
                points.append({"lat": round(lat, 6), "lng": round(lng, 6), "score": round(s, 1)})
                scores.append(s)

        avg = sum(scores) / len(scores) if scores else 0
        return GridResult(
            center_lat=center_lat, center_lng=center_lng,
            species=sp, month=month, grid_size=grid_size,
            points=points,
            score_avg=round(avg, 1),
            score_min=round(min(scores), 1) if scores else 0,
            score_max=round(max(scores), 1) if scores else 0,
        )
