"""
SERVICE COMPARISON — Territory Comparison Engine
BIONIC V5 ULTIME 300% — PHASE G+

Compare deux territoires cote-a-cote pour une espece donnee.
Execute le pipeline complet sur chaque territoire, puis produit
un rapport comparatif avec scores, avantages et recommandation.

0 duplication: reutilise execute_full_pipeline du pipeline_service.
0 transversalite: comparaison strictement post-pipeline.
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger("bionic_engine.comparison_service")


def _extract_module_means(module_stats: Dict[str, Any]) -> Dict[str, float]:
    """Extract all mean_* values from module stats for comparison."""
    means = {}
    for mod, stats in module_stats.items():
        if isinstance(stats, dict):
            for k, v in stats.items():
                if k.startswith("mean_") and isinstance(v, (int, float)):
                    means[f"{mod}.{k}"] = round(float(v), 4)
    return means


def _score_territory(result: Dict[str, Any]) -> Dict[str, float]:
    """Compute dimension scores from pipeline results."""
    ms = result["module_stats"]

    habitat = ms.get("SSE", {}).get("composite_mean", 0.0)
    corridors = result.get("corridor_count", 0) / 6.0
    wind_exposure = 1.0 - ms.get("WSE_WIV", {}).get("mean_wind_speed", 0.5)
    pressure = 1.0 - ms.get("PME", {}).get("mean_pressure_memory", 0.5)
    behavior = ms.get("BMPE", {}).get("mean_composite_micro_pattern", 0.5)
    thermal = ms.get("TFE", {}).get("mean_thermal_flow_composite", 0.5)

    overall = round(
        habitat * 0.20
        + corridors * 0.10
        + wind_exposure * 0.15
        + pressure * 0.20
        + behavior * 0.15
        + thermal * 0.20, 4
    )

    return {
        "habitat_quality": round(float(habitat), 4),
        "corridor_connectivity": round(float(corridors), 4),
        "wind_protection": round(float(wind_exposure), 4),
        "low_pressure": round(float(pressure), 4),
        "behavioral_activity": round(float(behavior), 4),
        "thermal_comfort": round(float(thermal), 4),
        "overall_score": overall,
    }


def _compute_advantages(scores_a: Dict, scores_b: Dict) -> Dict[str, Any]:
    """Determine which territory wins on each dimension."""
    dimensions = ["habitat_quality", "corridor_connectivity", "wind_protection",
                   "low_pressure", "behavioral_activity", "thermal_comfort"]
    advantages_a = []
    advantages_b = []
    ties = []

    for dim in dimensions:
        va = scores_a.get(dim, 0)
        vb = scores_b.get(dim, 0)
        diff = round(va - vb, 4)
        if abs(diff) < 0.005:
            ties.append(dim)
        elif diff > 0:
            advantages_a.append({"dimension": dim, "delta": diff})
        else:
            advantages_b.append({"dimension": dim, "delta": abs(diff)})

    return {
        "territory_a_advantages": advantages_a,
        "territory_b_advantages": advantages_b,
        "ties": ties,
    }


def compare_territories(
    bounds_a: Dict[str, float],
    bounds_b: Dict[str, float],
    species: str,
    resolution: int = 60,
    layers: List[str] = None,
    max_zones_per_layer: int = 4,
    max_corridors: int = 6,
    base_wind_kmh: float = 15.0,
    base_direction_deg: float = 270.0,
) -> Dict[str, Any]:
    """Compare two territories for a given species using the full 10-module pipeline."""
    from modules.bionic_engine_p0.services.pipeline_service import execute_full_pipeline

    result_a = execute_full_pipeline(
        bounds_a, species, resolution, layers,
        max_zones_per_layer, max_corridors, base_wind_kmh, base_direction_deg,
    )
    result_b = execute_full_pipeline(
        bounds_b, species, resolution, layers,
        max_zones_per_layer, max_corridors, base_wind_kmh, base_direction_deg,
    )

    scores_a = _score_territory(result_a)
    scores_b = _score_territory(result_b)
    advantages = _compute_advantages(scores_a, scores_b)

    if scores_a["overall_score"] > scores_b["overall_score"] + 0.005:
        recommendation = "territory_a"
    elif scores_b["overall_score"] > scores_a["overall_score"] + 0.005:
        recommendation = "territory_b"
    else:
        recommendation = "equivalent"

    total_ms = round(
        result_a["total_computation_time_ms"] + result_b["total_computation_time_ms"], 1
    )

    return {
        "pipeline": "BIONIC_V5_ULTIME_300",
        "comparison_type": "territory_vs_territory",
        "species": species,
        "resolution": resolution,
        "territory_a": {
            "bounds": bounds_a,
            "scores": scores_a,
            "source_ids": result_a["pipeline_source_ids"],
            "module_timings_ms": result_a["module_timings_ms"],
        },
        "territory_b": {
            "bounds": bounds_b,
            "scores": scores_b,
            "source_ids": result_b["pipeline_source_ids"],
            "module_timings_ms": result_b["module_timings_ms"],
        },
        "advantages": advantages,
        "recommendation": recommendation,
        "score_delta": round(scores_a["overall_score"] - scores_b["overall_score"], 4),
        "total_computation_time_ms": total_ms,
        "validation": {
            "pipeline_a_complete": result_a["validation"]["all_modules_executed"],
            "pipeline_b_complete": result_b["validation"]["all_modules_executed"],
            "zero_transversality": True,
            "zero_duplication": True,
            "comparison_post_pipeline": True,
        },
    }
