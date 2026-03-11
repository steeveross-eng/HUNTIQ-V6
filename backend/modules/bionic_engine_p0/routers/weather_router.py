"""
BIONIC V8.2 — Weather Router
API météo dynamique pour Mon Territoire.

Endpoints:
  GET /api/v1/weather/now?lat=X&lng=Y     — Météo actuelle (cache 30min)
  GET /api/v1/weather/forecast?lat=X&lng=Y — Prévisions 5j/3h (cache 30min)
  GET /api/v1/weather/influence?lat=X&lng=Y — Influence météo sur scores
  GET /api/v1/weather/cache-stats          — Stats du cache

Sécurité: la clé OWM_API_KEY n'est JAMAIS transmise dans les réponses.
"""

import logging
from fastapi import APIRouter, HTTPException, Query

logger = logging.getLogger("bionic_engine.weather_router")
router = APIRouter(prefix="/api/v1/weather", tags=["BIONIC Weather V8.2"])


@router.get("/now")
async def get_current_weather(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lng: float = Query(..., ge=-180, le=180, description="Longitude"),
):
    """
    Retourne la météo actuelle pour les coordonnées données.
    Cache TTL 30 minutes — max 1 appel OWM / 30 min par coordonnée.
    """
    from modules.bionic_engine_p0.services.weather_service_v1 import (
        fetch_current_weather,
    )

    try:
        snapshot = await fetch_current_weather(lat, lng)
        return snapshot
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Weather fetch failed: {e}")
        raise HTTPException(
            status_code=502,
            detail="Service météo temporairement indisponible",
        )


@router.get("/forecast")
async def get_forecast(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lng: float = Query(..., ge=-180, le=180, description="Longitude"),
):
    """
    Retourne les prévisions 5 jours / 3 heures.
    Cache TTL 30 minutes.
    """
    from modules.bionic_engine_p0.services.weather_service_v1 import (
        fetch_forecast,
    )

    try:
        forecast = await fetch_forecast(lat, lng)
        return forecast
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Forecast fetch failed: {e}")
        raise HTTPException(
            status_code=502,
            detail="Service prévisions temporairement indisponible",
        )


@router.get("/influence")
async def get_weather_influence(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lng: float = Query(..., ge=-180, le=180, description="Longitude"),
):
    """
    Retourne l'influence météo actuelle sur les scores biologiques.
    Multiplicateurs par catégorie: repos, alimentation, corridors, rut, habitats.
    """
    from modules.bionic_engine_p0.services.weather_service_v1 import (
        fetch_current_weather,
        compute_weather_influence,
    )

    try:
        snapshot = await fetch_current_weather(lat, lng)
        influence = compute_weather_influence(snapshot)
        return {
            "weather": {
                "temperature_c": snapshot.get("temperature_c"),
                "wind_speed_kmh": snapshot.get("wind_speed_kmh"),
                "precipitation_1h_mm": snapshot.get("precipitation_1h_mm"),
                "condition": snapshot.get("condition"),
            },
            "influence_multipliers": influence,
            "from_cache": snapshot.get("from_cache", False),
        }
    except Exception as e:
        logger.error(f"Weather influence failed: {e}")
        return {
            "weather": None,
            "influence_multipliers": {
                "repos": 1.0,
                "alimentation": 1.0,
                "corridors": 1.0,
                "rut": 1.0,
                "habitats": 1.0,
            },
            "error": "Météo indisponible, multiplicateurs par défaut",
        }


@router.get("/cache-stats")
async def get_cache_stats():
    """Retourne les statistiques du cache météo."""
    from modules.bionic_engine_p0.services.weather_service_v1 import (
        get_cache_stats,
    )

    return get_cache_stats()
