"""
ENGINE ADAPTERS — Adaptateurs BionicEngine pour moteurs existants
==================================================================
BCE-4X: Wrapping pur — aucune modification des moteurs originaux.
Chaque adaptateur traduit l'interface commune vers le moteur legacy.
Mapping espèces: CHEVREUIL → CERF pour les moteurs V1 (legacy).
"""
import math
from modules.engine_registry.base import (
    BionicEngine, EngineMeta, EngineScore, GridResult, resolve_species,
)

# Mapping canonique → legacy (moteurs V1 utilisent "CERF" en interne)
_TO_LEGACY = {
    "CHEVREUIL": "CERF", "ORIGNAL": "ORIGNAL",
    "OURS": "OURS", "DINDON": "DINDON", "WAPITI": "WAPITI",
}


def _to_legacy(species: str) -> str:
    return _TO_LEGACY.get(resolve_species(species), "CERF")


# ══════════════════════════════════════════════════════════
# ALIMENTATION-V1 Adapter
# ══════════════════════════════════════════════════════════
class AlimentationV1Adapter(BionicEngine):

    def meta(self) -> EngineMeta:
        return EngineMeta(
            name="ALIMENTATION-V1",
            version="1.0.0",
            engine_type="score",
            domain="alimentation",
            default_weight=0.25,
            description="Score alimentaire multi-espèces (couverture, feuillus, eau)",
            seasonal_modifiers=True,
        )

    def score_point(self, lat, lng, species, month) -> EngineScore:
        from modules.alimentation_v1.engine import analyze_single_point
        legacy_sp = _to_legacy(species)
        result = analyze_single_point(lat, lng, legacy_sp, month)
        return EngineScore(
            score=result.get("score_alimentation", 0),
            components=result.get("detail", {}),
            metadata={"engine": "ALIMENTATION-V1", "species": resolve_species(species), "month": month},
        )

    def score_grid(self, center_lat, center_lng, species, month, grid_size=20) -> GridResult:
        from modules.alimentation_v1.engine import analyze_single_point
        legacy_sp = _to_legacy(species)
        sp = resolve_species(species)
        side_m = 2000.0
        half = side_m / 2.0
        lat_step = (side_m / grid_size) / 111320.0
        lng_step = (side_m / grid_size) / (111320.0 * math.cos(math.radians(center_lat)))
        lat_start = center_lat - half / 111320.0
        lng_start = center_lng - half / (111320.0 * math.cos(math.radians(center_lat)))

        points, scores = [], []
        for r in range(grid_size):
            for c in range(grid_size):
                lat = lat_start + (r + 0.5) * lat_step
                lng = lng_start + (c + 0.5) * lng_step
                result = analyze_single_point(lat, lng, legacy_sp, month)
                s = result.get("score_alimentation", 0)
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


# ══════════════════════════════════════════════════════════
# ALIMENTATION-V2 Adapter
# ══════════════════════════════════════════════════════════
class AlimentationV2Adapter(BionicEngine):

    def meta(self) -> EngineMeta:
        return EngineMeta(
            name="ALIMENTATION-V2",
            version="2.0.0",
            engine_type="composite",
            domain="alimentation",
            default_weight=0.10,
            description="Analyse territoriale avancée + salines + nutrition",
            seasonal_modifiers=True,
        )

    def score_point(self, lat, lng, species, month) -> EngineScore:
        from modules.alimentation_v2.engine import analyze_alimentation_v2
        legacy_sp = _to_legacy(species)
        result = analyze_alimentation_v2(lat, lng, legacy_sp, month, max_salines=1)
        terrain = result.get("terrain", {})
        score = terrain.get("score_global", 50.0)
        return EngineScore(
            score=round(score, 1),
            components={
                "terrain_score": terrain.get("score_global", 0),
                "salines_count": len(result.get("salines", [])),
            },
            metadata={"engine": "ALIMENTATION-V2", "species": resolve_species(species), "month": month},
        )

    def score_grid(self, center_lat, center_lng, species, month, grid_size=20) -> GridResult:
        # V2 est un moteur composite, pas adapté au calcul point-par-point.
        # On retourne le score terrain global comme approximation uniforme.
        from modules.alimentation_v2.engine import analyze_alimentation_v2
        legacy_sp = _to_legacy(species)
        result = analyze_alimentation_v2(center_lat, center_lng, legacy_sp, month)
        terrain = result.get("terrain", {})
        base_score = terrain.get("score_global", 50.0)
        sp = resolve_species(species)

        points = [{"lat": center_lat, "lng": center_lng, "score": round(base_score, 1)}]
        return GridResult(
            center_lat=center_lat, center_lng=center_lng,
            species=sp, month=month, grid_size=1,
            points=points,
            score_avg=round(base_score, 1),
            score_min=round(base_score, 1),
            score_max=round(base_score, 1),
        )


# ══════════════════════════════════════════════════════════
# REPOS-V1 Adapter
# ══════════════════════════════════════════════════════════
class ReposV1Adapter(BionicEngine):

    def meta(self) -> EngineMeta:
        return EngineMeta(
            name="REPOS-V1",
            version="1.0.0",
            engine_type="score",
            domain="repos",
            default_weight=0.20,
            description="Zones de repos (couvert, calme, thermique, accessibilité)",
            seasonal_modifiers=True,
        )

    def score_point(self, lat, lng, species, month) -> EngineScore:
        from modules.repos_v1.engine import analyze_single_point
        legacy_sp = _to_legacy(species)
        result = analyze_single_point(lat, lng, legacy_sp, month)
        return EngineScore(
            score=result.get("score_repos", 0),
            components=result.get("detail", {}),
            metadata={"engine": "REPOS-V1", "species": resolve_species(species), "month": month},
        )

    def score_grid(self, center_lat, center_lng, species, month, grid_size=20) -> GridResult:
        from modules.repos_v1.engine import analyze_single_point
        legacy_sp = _to_legacy(species)
        sp = resolve_species(species)
        side_m = 2000.0
        half = side_m / 2.0
        lat_step = (side_m / grid_size) / 111320.0
        lng_step = (side_m / grid_size) / (111320.0 * math.cos(math.radians(center_lat)))
        lat_start = center_lat - half / 111320.0
        lng_start = center_lng - half / (111320.0 * math.cos(math.radians(center_lat)))

        points, scores = [], []
        for r in range(grid_size):
            for c in range(grid_size):
                lat = lat_start + (r + 0.5) * lat_step
                lng = lng_start + (c + 0.5) * lng_step
                result = analyze_single_point(lat, lng, legacy_sp, month)
                s = result.get("score_repos", 0)
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


# ══════════════════════════════════════════════════════════
# CORRIDORS-V10 Adapter
# ══════════════════════════════════════════════════════════
class CorridorsV10Adapter(BionicEngine):

    def meta(self) -> EngineMeta:
        return EngineMeta(
            name="CORRIDORS-V10",
            version="10.0.0",
            engine_type="spatial",
            domain="corridors",
            default_weight=0.25,
            description="Corridors fauniques (A*, multi-engine, BCE-4X validé)",
            seasonal_modifiers=True,
        )

    def score_point(self, lat, lng, species, month) -> EngineScore:
        from modules.score_consolide import _corridor_score_for_point
        legacy_sp = _to_legacy(species)
        score = _corridor_score_for_point(lat, lng, lat, lng, legacy_sp, month)
        return EngineScore(
            score=round(score, 1),
            components={"corridor_strength": round(score, 1)},
            metadata={"engine": "CORRIDORS-V10", "species": resolve_species(species), "month": month},
        )

    def score_grid(self, center_lat, center_lng, species, month, grid_size=20) -> GridResult:
        from modules.score_consolide import _corridor_score_for_point
        legacy_sp = _to_legacy(species)
        sp = resolve_species(species)
        side_m = 2000.0
        half = side_m / 2.0
        lat_step = (side_m / grid_size) / 111320.0
        lng_step = (side_m / grid_size) / (111320.0 * math.cos(math.radians(center_lat)))
        lat_start = center_lat - half / 111320.0
        lng_start = center_lng - half / (111320.0 * math.cos(math.radians(center_lat)))

        points, scores = [], []
        for r in range(grid_size):
            for c in range(grid_size):
                lat = lat_start + (r + 0.5) * lat_step
                lng = lng_start + (c + 0.5) * lng_step
                s = _corridor_score_for_point(lat, lng, center_lat, center_lng, legacy_sp, month)
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
