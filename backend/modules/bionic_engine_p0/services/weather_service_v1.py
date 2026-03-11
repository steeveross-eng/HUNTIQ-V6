"""
BIONIC V8.2 — Weather Service V1
Service météo dynamique avec cache TTL 30 minutes.

Intègre OpenWeatherMap pour :
  - Météo actuelle (température, vent, rafales, pression, précipitations)
  - Prévisions 5 jours / 3 heures
  - Hook d'influence météo pour le scoring biologique V7

Cache:
  - TTL: 30 minutes
  - Clé: weather:{lat_rounded}:{lng_rounded}
  - Stockage: mémoire in-process (dict)
  - Garantie: max 1 appel OWM / 30 min par coordonnée

Sécurité:
  - OWM_API_KEY lu depuis .env, JAMAIS loggé ni transmis
"""

import os
import time
import math
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

import httpx

logger = logging.getLogger("bionic_engine.weather_service_v1")

OWM_BASE = "https://api.openweathermap.org/data/2.5"
CACHE_TTL_S = 1800  # 30 minutes
_weather_cache: Dict[str, Dict[str, Any]] = {}
_forecast_cache: Dict[str, Dict[str, Any]] = {}


def _get_api_key() -> str:
    key = os.environ.get("OWM_API_KEY", "")
    if not key:
        raise ValueError("OWM_API_KEY non configurée dans .env")
    return key


def _cache_key(lat: float, lng: float) -> str:
    """Arrondi à 2 décimales (~1.1km) pour regrouper les requêtes proches."""
    return f"weather:{round(lat, 2)}:{round(lng, 2)}"


def _is_cached(cache: Dict, key: str) -> bool:
    entry = cache.get(key)
    if entry is None:
        return False
    return (time.time() - entry["ts"]) < CACHE_TTL_S


def _get_cached(cache: Dict, key: str) -> Optional[Dict]:
    entry = cache.get(key)
    if entry and (time.time() - entry["ts"]) < CACHE_TTL_S:
        return entry["data"]
    return None


def _set_cache(cache: Dict, key: str, data: Dict):
    cache[key] = {"data": data, "ts": time.time()}


async def fetch_current_weather(lat: float, lng: float) -> Dict[str, Any]:
    """
    Récupère la météo actuelle pour des coordonnées.
    Utilise le cache TTL 30min — max 1 appel OWM / 30 min par coordonnée.

    Returns:
        WeatherSnapshot dict avec temp, vent, rafales, pression, précipitations, etc.
    """
    key = _cache_key(lat, lng)

    cached = _get_cached(_weather_cache, key)
    if cached:
        logger.info(f"[WEATHER-CACHE] HIT for ({lat:.2f}, {lng:.2f})")
        return {**cached, "from_cache": True}

    logger.info(f"[WEATHER-API] Fetching current weather for ({lat:.2f}, {lng:.2f})")

    try:
        api_key = _get_api_key()
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{OWM_BASE}/weather",
                params={
                    "lat": lat,
                    "lon": lng,
                    "appid": api_key,
                    "units": "metric",
                    "lang": "fr",
                },
            )
            resp.raise_for_status()
            raw = resp.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"[WEATHER-API] HTTP error: {e.response.status_code}")
        raise
    except Exception as e:
        logger.error(f"[WEATHER-API] Request failed: {e}")
        raise

    wind = raw.get("wind", {})
    main = raw.get("main", {})
    weather_arr = raw.get("weather", [{}])
    rain = raw.get("rain", {})
    snow = raw.get("snow", {})
    clouds = raw.get("clouds", {})

    snapshot = {
        "lat": lat,
        "lng": lng,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature_c": main.get("temp"),
        "feels_like_c": main.get("feels_like"),
        "temp_min_c": main.get("temp_min"),
        "temp_max_c": main.get("temp_max"),
        "humidity_pct": main.get("humidity"),
        "pressure_hpa": main.get("pressure"),
        "wind_speed_kmh": round((wind.get("speed", 0) or 0) * 3.6, 1),
        "wind_gust_kmh": round((wind.get("gust", 0) or 0) * 3.6, 1),
        "wind_direction_deg": wind.get("deg", 0),
        "precipitation_1h_mm": rain.get("1h", 0) + snow.get("1h", 0),
        "precipitation_3h_mm": rain.get("3h", 0) + snow.get("3h", 0),
        "cloud_cover_pct": clouds.get("all", 0),
        "visibility_m": raw.get("visibility", 10000),
        "condition": weather_arr[0].get("main", "Unknown"),
        "condition_detail": weather_arr[0].get("description", ""),
        "condition_icon": weather_arr[0].get("icon", ""),
        "sunrise": raw.get("sys", {}).get("sunrise"),
        "sunset": raw.get("sys", {}).get("sunset"),
        "from_cache": False,
    }

    _set_cache(_weather_cache, key, snapshot)
    logger.info(
        f"[WEATHER-API] OK: {snapshot['temperature_c']}°C, "
        f"vent {snapshot['wind_speed_kmh']}km/h, "
        f"precip {snapshot['precipitation_1h_mm']}mm"
    )

    return snapshot


async def fetch_forecast(lat: float, lng: float) -> Dict[str, Any]:
    """
    Récupère les prévisions 5 jours / 3h pour des coordonnées.
    Cache TTL 30min.

    Returns:
        Dict avec liste de snapshots prévisionnels.
    """
    key = _cache_key(lat, lng) + ":forecast"

    cached = _get_cached(_forecast_cache, key)
    if cached:
        logger.info(f"[FORECAST-CACHE] HIT for ({lat:.2f}, {lng:.2f})")
        return {**cached, "from_cache": True}

    logger.info(f"[FORECAST-API] Fetching forecast for ({lat:.2f}, {lng:.2f})")

    try:
        api_key = _get_api_key()
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{OWM_BASE}/forecast",
                params={
                    "lat": lat,
                    "lon": lng,
                    "appid": api_key,
                    "units": "metric",
                    "lang": "fr",
                },
            )
            resp.raise_for_status()
            raw = resp.json()
    except Exception as e:
        logger.error(f"[FORECAST-API] Request failed: {e}")
        raise

    forecasts = []
    for item in raw.get("list", []):
        wind = item.get("wind", {})
        main = item.get("main", {})
        weather_arr = item.get("weather", [{}])
        rain = item.get("rain", {})
        snow = item.get("snow", {})
        clouds = item.get("clouds", {})

        forecasts.append({
            "dt": item.get("dt"),
            "dt_txt": item.get("dt_txt"),
            "temperature_c": main.get("temp"),
            "feels_like_c": main.get("feels_like"),
            "humidity_pct": main.get("humidity"),
            "pressure_hpa": main.get("pressure"),
            "wind_speed_kmh": round((wind.get("speed", 0) or 0) * 3.6, 1),
            "wind_gust_kmh": round((wind.get("gust", 0) or 0) * 3.6, 1),
            "wind_direction_deg": wind.get("deg", 0),
            "precipitation_3h_mm": rain.get("3h", 0) + snow.get("3h", 0),
            "cloud_cover_pct": clouds.get("all", 0),
            "condition": weather_arr[0].get("main", "Unknown"),
            "condition_detail": weather_arr[0].get("description", ""),
            "condition_icon": weather_arr[0].get("icon", ""),
        })

    result = {
        "lat": lat,
        "lng": lng,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "city": raw.get("city", {}).get("name", ""),
        "forecast_count": len(forecasts),
        "forecasts": forecasts,
        "from_cache": False,
    }

    _set_cache(_forecast_cache, key, result)
    return result


def compute_weather_influence(snapshot: Dict[str, Any]) -> Dict[str, float]:
    """
    Calcule l'influence météo sur les scores biologiques.

    Retourne des multiplicateurs par catégorie de zone:
      - repos: pluie/froid → animal se réfugie → score repos augmenté
      - alimentation: conditions modérées → activité alimentaire normale
      - corridors: vent fort → déplacement réduit
      - rut: météo n'affecte presque pas le rut (hormonal)
      - habitats: score de base légèrement modulé

    Tous les multiplicateurs sont entre 0.7 et 1.3.
    """
    if not snapshot:
        return {
            "repos": 1.0,
            "alimentation": 1.0,
            "corridors": 1.0,
            "rut": 1.0,
            "habitats": 1.0,
        }

    temp = snapshot.get("temperature_c", 10) or 10
    wind = snapshot.get("wind_speed_kmh", 0) or 0
    precip = snapshot.get("precipitation_1h_mm", 0) or 0
    humidity = snapshot.get("humidity_pct", 50) or 50

    # --- Repos ---
    # Pluie forte ou froid → repos augmenté
    repos_mult = 1.0
    if precip > 5:
        repos_mult += 0.20  # Forte pluie → refuge
    elif precip > 1:
        repos_mult += 0.10
    if temp < -10:
        repos_mult += 0.15  # Grand froid → repos
    elif temp < 0:
        repos_mult += 0.08
    if wind > 40:
        repos_mult += 0.10  # Vent fort → repos

    # --- Alimentation ---
    # Conditions modérées = optimal. Extrêmes = réduit
    alim_mult = 1.0
    if -5 < temp < 15:
        alim_mult += 0.10  # Conditions idéales d'alimentation
    if temp < -15 or temp > 30:
        alim_mult -= 0.15  # Extrêmes → réduit alimentation
    if precip > 8:
        alim_mult -= 0.10  # Forte pluie → réduit activité

    # --- Corridors ---
    # Vent fort → déplacement réduit. Calme → déplacement facile
    corr_mult = 1.0
    if wind > 50:
        corr_mult -= 0.25  # Vent très fort → réduit corridors
    elif wind > 30:
        corr_mult -= 0.15
    elif wind < 10:
        corr_mult += 0.10  # Calme → facilite déplacement
    if precip > 10:
        corr_mult -= 0.10  # Forte pluie → réduit

    # --- Rut ---
    # Le rut est hormonal, très peu influencé par la météo
    rut_mult = 1.0
    if temp < -20:
        rut_mult -= 0.05  # Froid extrême seul impact
    if wind > 60:
        rut_mult -= 0.05

    # --- Habitats ---
    # Légèrement modulé par le confort thermique
    hab_mult = 1.0
    if -10 < temp < 20 and wind < 30 and precip < 3:
        hab_mult += 0.05  # Conditions confortables
    elif temp < -15 or wind > 50:
        hab_mult -= 0.05

    # Clamp all multipliers to [0.7, 1.3]
    def clamp(v):
        return max(0.7, min(1.3, round(v, 3)))

    return {
        "repos": clamp(repos_mult),
        "alimentation": clamp(alim_mult),
        "corridors": clamp(corr_mult),
        "rut": clamp(rut_mult),
        "habitats": clamp(hab_mult),
    }


def get_cache_stats() -> Dict[str, Any]:
    """Retourne les statistiques du cache météo."""
    now = time.time()

    def count_valid(cache):
        return sum(1 for v in cache.values() if (now - v["ts"]) < CACHE_TTL_S)

    return {
        "weather_cache_entries": len(_weather_cache),
        "weather_cache_valid": count_valid(_weather_cache),
        "forecast_cache_entries": len(_forecast_cache),
        "forecast_cache_valid": count_valid(_forecast_cache),
        "cache_ttl_seconds": CACHE_TTL_S,
        "cache_ttl_minutes": CACHE_TTL_S // 60,
    }


def clear_weather_cache():
    """Vide le cache météo (pour tests ou admin)."""
    global _weather_cache, _forecast_cache
    _weather_cache = {}
    _forecast_cache = {}
