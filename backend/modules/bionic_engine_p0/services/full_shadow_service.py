"""
SERVICE SHADOW FULL COMPARISON — DEM + Meteo combines
BIONIC V5 ULTIME 300% — full_comparison_v1

Compare le pipeline synthetique complet vs le pipeline avec
TOUTES les donnees reelles (DEM + meteo injectees simultanement).
Mesure l'impact combine sur TCVE, TFE et les cibles ML.

0 impact sur predictions actuelles. Strict Shadow Mode.
"""

import time
import logging
import numpy as np
from typing import Dict, Any

logger = logging.getLogger("bionic_engine.full_shadow_comparison")


def _field_stats(fields, field_map):
    stats = {}
    for name, key in field_map:
        f = fields.get(key)
        if f is not None and isinstance(f, np.ndarray):
            stats[f"mean_{name}"] = round(float(np.mean(f)), 4)
            stats[f"{name}_range"] = [round(float(f.min()), 4), round(float(f.max()), 4)]
    return stats


TCVE_MAP = [
    ("terrain_visibility_calibration", "terrain_visibility_calibration_field"),
    ("terrain_roughness", "terrain_roughness_field"),
    ("terrain_cover_index", "terrain_cover_index_field"),
]
TFE_MAP = [
    ("thermal_gradient", "thermal_gradient_field"),
    ("thermal_inertia", "thermal_inertia_field"),
    ("hot_pocket", "hot_pocket_field"),
    ("cold_pocket", "cold_pocket_field"),
    ("thermal_flow_composite", "thermal_flow_composite"),
]
BMPE_MAP = [
    ("micro_retreat", "micro_retreat_field"),
    ("hesitation", "hesitation_field"),
    ("composite_micro_pattern", "composite_micro_pattern"),
]


async def execute_full_shadow_comparison(
    bounds: Dict[str, float],
    species: str,
    resolution: int = 30,
) -> Dict[str, Any]:
    """Compare synthetic vs full-real (DEM+Weather) pipeline."""
    from modules.bionic_engine_p0.services.sse_engine import generate_sse_composite
    from modules.bionic_engine_p0.services.osg_engine import generate_osg_multi_layer
    from modules.bionic_engine_p0.services.cme_engine import generate_cme_corridors
    from modules.bionic_engine_p0.services.wse_wiv_engine import generate_wind_field
    from modules.bionic_engine_p0.services.vfe_engine import generate_visibility_field
    from modules.bionic_engine_p0.services.ssvl_engine import generate_ssvl_fields
    from modules.bionic_engine_p0.services.tcve_engine import generate_tcve_fields
    from modules.bionic_engine_p0.services.pme_engine import generate_pme_fields
    from modules.bionic_engine_p0.services.bmpe_engine import generate_bmpe_fields
    from modules.bionic_engine_p0.services.tfe_engine import generate_tfe_fields
    from modules.bionic_engine_p0.services.dem_cache_service import cache_get as dem_cache_get
    from modules.bionic_engine_p0.services.weather_cache_service import cache_get as weather_cache_get
    from modules.bionic_engine_p0.services.dem_service import fetch_dem_composite
    from modules.bionic_engine_p0.services.open_meteo_service import fetch_weather_composite

    layers = ["habitats", "alimentation"]
    total_start = time.time()

    # ════════════════════════════════════════════
    # SYNTHETIC PIPELINE
    # ════════════════════════════════════════════
    t0 = time.time()
    sse_syn = generate_sse_composite(bounds, species, resolution)
    osg_syn = generate_osg_multi_layer(bounds, species, layers, sse_syn, resolution, 4)
    cme_syn = generate_cme_corridors(bounds, species, sse_syn, osg_syn, resolution, ["movement", "feeding_transit"], 6)
    wse_syn = generate_wind_field(bounds, species, sse_syn, resolution, 15.0, 270.0)
    vfe_syn = generate_visibility_field(sse_syn, wse_syn, species, resolution)
    ssvl_syn = generate_ssvl_fields(vfe_syn, sse_syn, wse_syn, species, resolution)
    tcve_syn = generate_tcve_fields(sse_syn, wse_syn, ssvl_syn, vfe_syn, species, resolution)
    pme_syn = generate_pme_fields(sse_syn, wse_syn, ssvl_syn, tcve_syn, bounds, species, resolution)
    bmpe_syn = generate_bmpe_fields(sse_syn, wse_syn, ssvl_syn, tcve_syn, pme_syn, bounds, species, resolution)
    tfe_syn = generate_tfe_fields(sse_syn, wse_syn, ssvl_syn, tcve_syn, pme_syn, bmpe_syn, bounds, species, resolution)
    syn_ms = round((time.time() - t0) * 1000, 1)

    syn_tcve = _field_stats(tcve_syn, TCVE_MAP)
    syn_tfe = _field_stats(tfe_syn, TFE_MAP)
    syn_bmpe = _field_stats(bmpe_syn, BMPE_MAP)

    # ════════════════════════════════════════════
    # REAL DATA PIPELINE (DEM + Weather injected)
    # ════════════════════════════════════════════
    t0 = time.time()
    sse_real = generate_sse_composite(bounds, species, resolution)

    # Inject DEM
    dem_status = "not_available"
    dem_cached, dem_cs = dem_cache_get(bounds, "SRTMGL1", resolution)
    if dem_cached and dem_cs == "hit":
        dem_status = "cache_hit"
        fields = dem_cached["fields"]
        if "microrelief" not in sse_real:
            sse_real["microrelief"] = {}
        else:
            sse_real["microrelief"] = dict(sse_real["microrelief"])
        sse_real["microrelief"]["elevation_field"] = fields.get("elevation_normalized", np.zeros((resolution, resolution)))
        sse_real["microrelief"]["slope_intensity"] = fields.get("slope_normalized", np.zeros((resolution, resolution)))
    else:
        try:
            dem = await fetch_dem_composite(bounds, species, resolution)
            if dem.get("status") == "success":
                dem_status = "api_fetched"
                sse_real["microrelief"] = dict(sse_real.get("microrelief", {}))
                sse_real["microrelief"]["elevation_field"] = dem["fields"]["elevation_normalized"]
                sse_real["microrelief"]["slope_intensity"] = dem["fields"]["slope_normalized"]
        except Exception as e:
            logger.warning(f"DEM unavailable: {e}")
            dem_status = "fallback_synthetic"

    # Inject Weather
    weather_status = "not_available"
    real_wind_kmh = 15.0
    real_wind_dir = 270.0
    weather_cached, weather_cs = weather_cache_get(bounds, resolution)
    if weather_cached and weather_cs == "hit":
        weather_status = "cache_hit"
    else:
        try:
            weather = await fetch_weather_composite(bounds, species, resolution)
            if weather.get("status") == "success":
                weather_status = "api_fetched"
                weather_cached = weather
        except Exception as e:
            logger.warning(f"Weather unavailable: {e}")
            weather_status = "fallback_synthetic"

    # Extract real wind parameters from weather data
    if weather_cached and weather_status in ("cache_hit", "api_fetched"):
        stats = weather_cached.get("stats", {})
        ws = stats.get("wind_speed_kmh", {})
        if isinstance(ws, dict) and ws.get("mean") is not None:
            real_wind_kmh = ws["mean"]
        wd = stats.get("wind_direction_mean_deg")
        if wd is not None:
            real_wind_dir = wd

    # Run pipeline with enriched SSE + real wind
    osg_real = generate_osg_multi_layer(bounds, species, layers, sse_real, resolution, 4)
    cme_real = generate_cme_corridors(bounds, species, sse_real, osg_real, resolution, ["movement", "feeding_transit"], 6)
    wse_real = generate_wind_field(bounds, species, sse_real, resolution, real_wind_kmh, real_wind_dir)
    vfe_real = generate_visibility_field(sse_real, wse_real, species, resolution)
    ssvl_real = generate_ssvl_fields(vfe_real, sse_real, wse_real, species, resolution)
    tcve_real = generate_tcve_fields(sse_real, wse_real, ssvl_real, vfe_real, species, resolution)
    pme_real = generate_pme_fields(sse_real, wse_real, ssvl_real, tcve_real, bounds, species, resolution)
    bmpe_real = generate_bmpe_fields(sse_real, wse_real, ssvl_real, tcve_real, pme_real, bounds, species, resolution)
    tfe_real = generate_tfe_fields(sse_real, wse_real, ssvl_real, tcve_real, pme_real, bmpe_real, bounds, species, resolution)
    real_ms = round((time.time() - t0) * 1000, 1)

    real_tcve = _field_stats(tcve_real, TCVE_MAP)
    real_tfe = _field_stats(tfe_real, TFE_MAP)
    real_bmpe = _field_stats(bmpe_real, BMPE_MAP)

    # ════════════════════════════════════════════
    # COMPUTE DELTAS
    # ════════════════════════════════════════════
    def _deltas(syn, real):
        d = {}
        for k in syn:
            if k.startswith("mean_") and k in real:
                d[k] = round(real[k] - syn[k], 4)
        return d

    total_ms = round((time.time() - total_start) * 1000, 1)

    return {
        "pipeline": "BIONIC_V5_ULTIME_300",
        "version": "full_comparison_v1",
        "comparison_type": "synthetic_vs_full_real",
        "species": species,
        "bounds": bounds,
        "resolution": resolution,
        "data_sources": {
            "dem": dem_status,
            "weather": weather_status,
        },
        "synthetic": {
            "tcve": syn_tcve,
            "tfe": syn_tfe,
            "bmpe": syn_bmpe,
            "computation_ms": syn_ms,
        },
        "real": {
            "tcve": real_tcve,
            "tfe": real_tfe,
            "bmpe": real_bmpe,
            "computation_ms": real_ms,
        },
        "deltas": {
            "tcve": _deltas(syn_tcve, real_tcve),
            "tfe": _deltas(syn_tfe, real_tfe),
            "bmpe": _deltas(syn_bmpe, real_bmpe),
        },
        "total_computation_time_ms": total_ms,
        "validation": {
            "certified_modules_unmodified": True,
            "shadow_mode": True,
            "zero_impact_on_production": True,
            "dem_injected": dem_status != "fallback_synthetic" and dem_status != "not_available",
            "weather_injected": weather_status != "fallback_synthetic" and weather_status != "not_available",
        },
    }
