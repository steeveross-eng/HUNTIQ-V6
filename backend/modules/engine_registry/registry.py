"""
ENGINE REGISTRY — Registre dynamique auto-détectable
======================================================
BCE-4X: Auto-détection des moteurs, consolidation découplée,
aucune dépendance directe vers les moteurs individuels.

Usage:
    registry = EngineRegistry()
    registry.auto_discover()  # Détecte tous les moteurs disponibles
    manifest = registry.manifest()  # JSON consommable par le frontend
"""
import logging
from typing import Dict, List, Optional
from modules.engine_registry.base import BionicEngine, EngineMeta, EngineScore, resolve_species

logger = logging.getLogger("engine_registry")


class EngineRegistry:
    """Registre central dynamique — détection automatique des moteurs."""

    def __init__(self):
        self._engines: Dict[str, BionicEngine] = {}

    def register(self, engine: BionicEngine) -> None:
        """Enregistre un moteur dans le registre."""
        meta = engine.meta()
        key = meta.name
        self._engines[key] = engine
        logger.info(f"[REGISTRY] Moteur enregistré: {key} v{meta.version} ({meta.domain})")

    def get(self, name: str) -> Optional[BionicEngine]:
        return self._engines.get(name)

    def list_engines(self) -> List[str]:
        return list(self._engines.keys())

    def all_engines(self) -> Dict[str, BionicEngine]:
        return dict(self._engines)

    def manifest(self) -> dict:
        """Génère le manifest JSON consommable par INTELLIGENCE frontend."""
        engines = []
        for name, engine in self._engines.items():
            m = engine.meta()
            engines.append({
                "name": m.name,
                "version": m.version,
                "type": m.engine_type,
                "engine_type": m.engine_type,
                "domain": m.domain,
                "species_supported": m.species_supported,
                "unit": m.unit,
                "default_weight": m.default_weight,
                "description": m.description,
                "seasonal_modifiers": m.seasonal_modifiers,
            })
        return {
            "registry_version": "1.0.0",
            "total_engines": len(engines),
            "engines": engines,
        }

    def auto_discover(self) -> None:
        """
        Détecte et enregistre automatiquement tous les moteurs disponibles.
        BCE-4X: Chaque import est isolé dans un try/except.
        Aucun moteur manquant ne bloque le système.
        """
        discoveries = [
            ("ALIMENTATION-V1", "modules.engine_registry.adapters", "AlimentationV1Adapter"),
            ("ALIMENTATION-V2", "modules.engine_registry.adapters", "AlimentationV2Adapter"),
            ("REPOS-V1", "modules.engine_registry.adapters", "ReposV1Adapter"),
            ("CORRIDORS-V10", "modules.engine_registry.adapters", "CorridorsV10Adapter"),
            ("PRESSION-V1", "modules.pression_v1.engine", "PressionV1Engine"),
        ]

        for name, module_path, class_name in discoveries:
            try:
                import importlib
                mod = importlib.import_module(module_path)
                cls = getattr(mod, class_name)
                self.register(cls())
            except Exception as e:
                logger.warning(f"[REGISTRY] Moteur {name} indisponible: {e}")

        logger.info(f"[REGISTRY] Auto-découverte terminée: {len(self._engines)} moteurs actifs")


class DynamicConsolidator:
    """
    Consolidateur dynamique BCE-4X.
    Totalement découplé — utilise uniquement le EngineRegistry.
    Aucune dépendance directe vers les moteurs.
    """

    def __init__(self, registry: EngineRegistry, weight_overrides: Optional[Dict[str, float]] = None):
        self._registry = registry
        self._weight_overrides = weight_overrides or {}

    def _get_weights(self, exclude: Optional[List[str]] = None) -> Dict[str, float]:
        """Calcule les poids normalisés dynamiquement."""
        exclude = set(exclude or [])
        weights = {}
        for name, engine in self._registry.all_engines().items():
            if name in exclude:
                continue
            w = self._weight_overrides.get(name, engine.meta().default_weight)
            if w > 0:
                weights[name] = w

        total = sum(weights.values())
        if total == 0:
            return {}
        return {k: v / total for k, v in weights.items()}

    def score_point(
        self, lat: float, lng: float, species: str, month: int,
        exclude_engines: Optional[List[str]] = None,
    ) -> dict:
        """Score consolidé pour un point, utilisant tous les moteurs du registry."""
        sp = resolve_species(species)
        weights = self._get_weights(exclude=exclude_engines)
        exclude = set(exclude_engines or [])

        components = {}
        errors = []
        for name, engine in self._registry.all_engines().items():
            if name in exclude:
                continue
            try:
                result = engine.score_point(lat, lng, sp, month)
                components[name] = result.score
            except Exception as e:
                errors.append({"engine": name, "error": str(e)})
                logger.warning(f"[CONSOLIDATOR] Erreur moteur {name}: {e}")

        # Recalculer les poids si des moteurs ont échoué
        active_weights = {k: v for k, v in weights.items() if k in components}
        total_w = sum(active_weights.values())
        if total_w > 0:
            active_weights = {k: v / total_w for k, v in active_weights.items()}

        consolidated = sum(components.get(k, 0) * active_weights.get(k, 0) for k in active_weights)
        consolidated = max(0, min(100, consolidated))

        if consolidated >= 80:
            classe, label, color = "OPTIMAL", "Optimal", "#DC2626"
        elif consolidated >= 60:
            classe, label, color = "BON", "Bon", "#F59E0B"
        elif consolidated >= 40:
            classe, label, color = "MODERE", "Modéré", "#22C55E"
        else:
            classe, label, color = "FAIBLE", "Faible", "#3B82F6"

        return {
            "score": round(consolidated, 1),
            "classe": classe,
            "label": label,
            "color": color,
            "species": sp,
            "month": month,
            "components": {k: round(v, 1) for k, v in components.items()},
            "weights": {k: round(v, 3) for k, v in active_weights.items()},
            "tracability": {
                "engines_active": list(active_weights.keys()),
                "engines_excluded": list(exclude),
                "engines_errored": errors,
                "consolidator": "DynamicConsolidator-v1",
            },
        }

    def score_grid(
        self, center_lat: float, center_lng: float,
        species: str, month: int, grid_size: int = 20,
        exclude_engines: Optional[List[str]] = None,
    ) -> dict:
        """Grille consolidée pour heatmap/intelligence."""
        sp = resolve_species(species)
        weights = self._get_weights(exclude=exclude_engines)

        import math
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
                result = self.score_point(lat, lng, sp, month, exclude_engines=exclude_engines)
                points.append({
                    "lat": round(lat, 6), "lng": round(lng, 6),
                    "score": result["score"],
                    "classe": result["classe"],
                    "color": result["color"],
                })
                scores.append(result["score"])

        avg = sum(scores) / len(scores) if scores else 0
        if avg >= 80:
            classe, label = "OPTIMAL", "Optimal"
        elif avg >= 60:
            classe, label = "BON", "Bon"
        elif avg >= 40:
            classe, label = "MODERE", "Modéré"
        else:
            classe, label = "FAIBLE", "Faible"

        return {
            "center": {"lat": center_lat, "lng": center_lng},
            "species": sp,
            "month": month,
            "grid_size": grid_size,
            "total_points": len(points),
            "score_avg": round(avg, 1),
            "score_min": round(min(scores), 1) if scores else 0,
            "score_max": round(max(scores), 1) if scores else 0,
            "overall_classe": classe,
            "overall_label": label,
            "weights": {k: round(v, 3) for k, v in weights.items()},
            "engines_integrated": list(weights.keys()),
            "points": points,
        }
