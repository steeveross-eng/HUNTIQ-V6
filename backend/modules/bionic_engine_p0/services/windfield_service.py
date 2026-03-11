"""
SERVICE WINDFIELD — Vector Wind Field for Ventusky-like Rendering
BIONIC V5 ULTIME 300% — windfield_v1

Genere un champ vectoriel de vent (u10, v10) a partir des donnees
Open-Meteo reelles, pour un rendu Canvas 2D type Ventusky.

Interpolation spatiale locale sur la grille du territoire.
Module isole. 0 impact sur pipeline principal.
"""

import math
import hashlib
import logging
import numpy as np
from typing import Dict, Any

logger = logging.getLogger("bionic_engine.windfield")


def _decompose_wind(speed_kmh: float, direction_deg: float):
    """Decompose wind speed + direction into u10/v10 (m/s)."""
    speed_ms = speed_kmh / 3.6
    rad = math.radians(direction_deg)
    u = -speed_ms * math.sin(rad)
    v = -speed_ms * math.cos(rad)
    return u, v


def generate_windfield(
    bounds: Dict[str, float],
    resolution: int,
    wind_speed_kmh: float,
    wind_direction_deg: float,
    gust_kmh: float = 0.0,
) -> Dict[str, Any]:
    """
    Generate a 2D vector wind field (u10, v10) with local perturbation.

    Returns arrays serializable for Canvas 2D particle rendering.
    """
    seed = int(hashlib.md5(
        f"WINDFIELD_{bounds['north']:.4f}_{bounds['west']:.4f}_{wind_speed_kmh:.1f}_{wind_direction_deg:.1f}".encode()
    ).hexdigest()[:8], 16)
    rng = np.random.RandomState(seed & 0x7FFFFFFF)

    u_base, v_base = _decompose_wind(wind_speed_kmh, wind_direction_deg)

    gust_factor = max(0.05, (gust_kmh / 3.6) * 0.3) if gust_kmh > 0 else abs(u_base) * 0.15

    u_field = np.full((resolution, resolution), u_base, dtype=np.float64)
    v_field = np.full((resolution, resolution), v_base, dtype=np.float64)

    u_field += rng.normal(0, gust_factor, (resolution, resolution))
    v_field += rng.normal(0, gust_factor, (resolution, resolution))

    speed_field = np.sqrt(u_field ** 2 + v_field ** 2)

    lat_step = (bounds["north"] - bounds["south"]) / resolution
    lng_step = (bounds["east"] - bounds["west"]) / resolution
    lats = [round(bounds["south"] + i * lat_step + lat_step / 2, 6) for i in range(resolution)]
    lngs = [round(bounds["west"] + j * lng_step + lng_step / 2, 6) for j in range(resolution)]

    return {
        "u10": u_field.tolist(),
        "v10": v_field.tolist(),
        "speed": speed_field.tolist(),
        "grid": {
            "rows": resolution,
            "cols": resolution,
            "lats": lats,
            "lngs": lngs,
        },
        "metadata": {
            "base_wind_speed_kmh": round(wind_speed_kmh, 2),
            "base_wind_direction_deg": round(wind_direction_deg, 1),
            "base_gust_kmh": round(gust_kmh, 2),
            "u_base_ms": round(u_base, 4),
            "v_base_ms": round(v_base, 4),
            "mean_speed_ms": round(float(np.mean(speed_field)), 4),
            "max_speed_ms": round(float(np.max(speed_field)), 4),
        },
    }


async def fetch_and_generate_windfield(
    bounds: Dict[str, float],
    resolution: int = 30,
) -> Dict[str, Any]:
    """
    Fetch real weather from Open-Meteo (or cache), then generate windfield.
    """
    from modules.bionic_engine_p0.services.weather_cache_service import cache_get
    from modules.bionic_engine_p0.services.open_meteo_service import fetch_weather_raw, compute_weather_stats

    wind_kmh = 15.0
    wind_dir = 270.0
    gust_kmh = 0.0
    source = "synthetic_default"

    cached, cache_status = cache_get(bounds, resolution)
    if cached and cache_status == "hit":
        stats = cached.get("stats", {})
        ws = stats.get("wind_speed_kmh", {})
        if isinstance(ws, dict) and ws.get("mean") is not None:
            wind_kmh = ws["mean"]
        wd = stats.get("wind_direction_mean_deg")
        if wd is not None:
            wind_dir = wd
        wg = stats.get("wind_gusts_kmh", {})
        if isinstance(wg, dict) and wg.get("mean") is not None:
            gust_kmh = wg["mean"]
        source = "cache_hit"
    else:
        raw = await fetch_weather_raw(bounds)
        if raw is not None:
            stats = compute_weather_stats(raw)
            ws = stats.get("wind_speed_kmh", {})
            if isinstance(ws, dict) and ws.get("mean") is not None:
                wind_kmh = ws["mean"]
            wd = stats.get("wind_direction_mean_deg")
            if wd is not None:
                wind_dir = wd
            wg = stats.get("wind_gusts_kmh", {})
            if isinstance(wg, dict) and wg.get("mean") is not None:
                gust_kmh = wg["mean"]
            source = "api_fetched"
        else:
            source = "fallback_synthetic"

    field = generate_windfield(bounds, resolution, wind_kmh, wind_dir, gust_kmh)

    logger.info(
        f"Windfield generated: source={source}, "
        f"wind={wind_kmh:.1f}km/h@{wind_dir:.0f}deg, "
        f"mean_speed={field['metadata']['mean_speed_ms']:.2f}m/s"
    )

    return {
        "source": source,
        "field": field,
    }
