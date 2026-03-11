"""
SERVICE ML — Feature Builder
BIONIC V5 ULTIME 300% — PHASE H

Extrait les features des 10 modules pour l'apprentissage comportemental.
Chaque espece/territoire produit un vecteur de features unifie.

Entrees: pipeline_service.execute_full_pipeline
Sorties: feature vector normalise [0,1]
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger("bionic_engine.ml_feature_builder")

FEATURE_SCHEMA = [
    # SSE (4 features)
    "sse_forest_density", "sse_clearing", "sse_conifer_ratio", "sse_edge_intensity",
    # OSG (2 features)
    "osg_zone_count", "osg_layer_count",
    # CME (1 feature)
    "cme_corridor_count",
    # WSE (1 feature)
    "wse_mean_wind_speed",
    # VFE (3 features)
    "vfe_mean_visibility", "vfe_mean_fog_occlusion", "vfe_mean_visual_composite",
    # SSVL (4 features)
    "ssvl_mean_prudence", "ssvl_mean_vigilance", "ssvl_mean_curiosity", "ssvl_mean_behavioral_composite",
    # TCVE (3 features)
    "tcve_mean_terrain_visibility_calibration", "tcve_mean_terrain_roughness", "tcve_mean_terrain_cover_index",
    # PME (4 features)
    "pme_mean_pressure_memory", "pme_mean_pressure_intensity", "pme_mean_pressure_recency", "pme_mean_pressure_remanence",
    # BMPE (5 features)
    "bmpe_mean_micro_retreat", "bmpe_mean_micro_exploration", "bmpe_mean_hesitation",
    "bmpe_mean_fine_movement", "bmpe_mean_composite_micro_pattern",
    # TFE (5 features)
    "tfe_mean_thermal_gradient", "tfe_mean_thermal_inertia", "tfe_mean_hot_pocket",
    "tfe_mean_cold_pocket", "tfe_mean_thermal_flow_composite",
]


def _safe_get(stats: Dict, key: str, default: float = 0.0) -> float:
    val = stats.get(key, default)
    return float(val) if isinstance(val, (int, float)) else default


def build_feature_vector(pipeline_result: Dict[str, Any]) -> Dict[str, Any]:
    """Extract a normalized feature vector from a full pipeline result."""
    ms = pipeline_result["module_stats"]

    sse = ms.get("SSE", {})
    osg = ms.get("OSG", {})
    cme = ms.get("CME", {})
    wse = ms.get("WSE_WIV", {})
    vfe = ms.get("VFE", {})
    ssvl = ms.get("SSVL", {})
    tcve = ms.get("TCVE", {})
    pme = ms.get("PME", {})
    bmpe = ms.get("BMPE", {})
    tfe = ms.get("TFE", {})

    vector = [
        _safe_get(sse, "mean_forest_density"),
        _safe_get(sse, "mean_clearing"),
        _safe_get(sse, "mean_conifer_ratio"),
        _safe_get(sse, "mean_edge_intensity"),
        min(1.0, _safe_get(osg, "total_zones", 0) / 8.0),
        min(1.0, _safe_get(osg, "layers", 0) / 4.0),
        min(1.0, _safe_get(cme, "corridor_count", 0) / 6.0),
        _safe_get(wse, "mean_wind_speed"),
        _safe_get(vfe, "mean_visibility"),
        _safe_get(vfe, "mean_fog_occlusion"),
        _safe_get(vfe, "mean_visual_composite"),
        _safe_get(ssvl, "mean_prudence"),
        _safe_get(ssvl, "mean_vigilance"),
        _safe_get(ssvl, "mean_curiosity"),
        _safe_get(ssvl, "mean_behavioral_composite"),
        _safe_get(tcve, "mean_terrain_visibility_calibration"),
        _safe_get(tcve, "mean_terrain_roughness"),
        _safe_get(tcve, "mean_terrain_cover_index"),
        _safe_get(pme, "mean_pressure_memory"),
        _safe_get(pme, "mean_pressure_intensity"),
        _safe_get(pme, "mean_pressure_recency"),
        _safe_get(pme, "mean_pressure_remanence"),
        _safe_get(bmpe, "mean_micro_retreat"),
        _safe_get(bmpe, "mean_micro_exploration"),
        _safe_get(bmpe, "mean_hesitation"),
        _safe_get(bmpe, "mean_fine_movement"),
        _safe_get(bmpe, "mean_composite_micro_pattern"),
        _safe_get(tfe, "mean_thermal_gradient"),
        _safe_get(tfe, "mean_thermal_inertia"),
        _safe_get(tfe, "mean_hot_pocket"),
        _safe_get(tfe, "mean_cold_pocket"),
        _safe_get(tfe, "mean_thermal_flow_composite"),
    ]

    return {
        "species": pipeline_result["species"],
        "bounds": pipeline_result["bounds"],
        "feature_names": FEATURE_SCHEMA,
        "feature_vector": [round(v, 6) for v in vector],
        "feature_count": len(FEATURE_SCHEMA),
        "source_ids": pipeline_result["pipeline_source_ids"],
    }


def build_multi_territory_features(
    territories: List[Dict[str, float]],
    species: str,
    resolution: int = 30,
) -> Dict[str, Any]:
    """Build feature vectors for multiple territories."""
    from modules.bionic_engine_p0.services.pipeline_service import execute_full_pipeline

    samples = []
    for bounds in territories:
        result = execute_full_pipeline(bounds, species, resolution)
        fv = build_feature_vector(result)
        samples.append(fv)

    return {
        "species": species,
        "sample_count": len(samples),
        "feature_count": len(FEATURE_SCHEMA),
        "feature_names": FEATURE_SCHEMA,
        "samples": samples,
    }


def get_feature_schema() -> Dict[str, Any]:
    return {
        "feature_count": len(FEATURE_SCHEMA),
        "feature_names": FEATURE_SCHEMA,
        "modules_contributing": {
            "SSE": 4, "OSG": 2, "CME": 1, "WSE_WIV": 1,
            "VFE": 3, "SSVL": 4, "TCVE": 3, "PME": 4, "BMPE": 5, "TFE": 5,
        },
    }
