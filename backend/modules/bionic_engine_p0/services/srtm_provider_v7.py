"""
BIONIC V7 — SRTM Provider V7
Fournisseur unifie de donnees DEM SRTM 30m (NASA).

Source principale: OpenTopography API (SRTMGL1 30m)
Cache: MongoDB via dem_cache_service (TTL 90 jours)
Fallback: Donnees heuristiques si API indisponible

Fonctions:
  - fetch_dem_for_pipeline(): Fetch async avec cache
  - sample_dem_at_point(): Echantillonnage ponctuel
  - classify_terrain(): Classification terrain (vallee, crete, plateau)
  - get_slope_grid_resampled(): Grille de pente resamplee

100% independant. Consomme par pipeline_v7 et zone_engine_core_v2.
"""

import logging
import numpy as np
from typing import Dict, Any, Optional

logger = logging.getLogger("bionic_engine.srtm_provider_v7")


async def fetch_dem_for_pipeline(
    bounds: Dict[str, float],
    species: str,
    resolution: int = 60,
    dataset: str = "SRTMGL1",
) -> Optional[Dict[str, Any]]:
    """
    Fetch DEM SRTM pour le pipeline V7.
    R4: Fallback persistant — si API echoue, utilise le dernier DEM connu.

    Cascade:
      1. Cache MongoDB (TTL standard)
      2. OpenTopography API
      3. Cache MongoDB stale (TTL expire mais donnees encore presentes)
      4. None (fallback heuristique)
    """
    cached = None
    cache_status = None

    # STEP 1: Verifier le cache MongoDB (frais)
    try:
        from modules.bionic_engine_p0.services.dem_cache_service import (
            cache_get,
            cache_put,
        )

        cached, cache_status = cache_get(bounds, dataset, resolution)
        if cache_status == "hit" and cached is not None:
            logger.info(
                f"[SRTM] Cache HIT: elevation=[{cached.get('stats', {}).get('elevation_min', '?')}, "
                f"{cached.get('stats', {}).get('elevation_max', '?')}]m"
            )
            cached["status"] = "success"
            return cached
    except Exception as e:
        logger.warning(f"[SRTM] Cache check failed: {e}")

    # STEP 2: Fetch depuis OpenTopography
    try:
        from modules.bionic_engine_p0.services.dem_service import fetch_dem_composite

        result = await fetch_dem_composite(bounds, species, resolution, dataset)

        if result.get("status") == "success":
            logger.info(
                f"[SRTM] Fetched from OpenTopography: "
                f"shape={result.get('raw_shape')}, "
                f"elevation=[{result['stats']['elevation_min']}, {result['stats']['elevation_max']}]m"
            )

            # Stocker en cache
            try:
                cache_put(bounds, dataset, resolution, species, result)
            except Exception as ce:
                logger.warning(f"[SRTM] Cache store failed: {ce}")

            return result

        logger.info(f"[SRTM] OpenTopography status={result.get('status')}")

    except Exception as e:
        logger.warning(f"[SRTM] OpenTopography fetch failed: {e}")

    # STEP 3: R4 — Fallback: cache stale (expire mais toujours en MongoDB)
    if cached is not None and cache_status in ("stale", "expired"):
        logger.info("[SRTM] R4 fallback: using stale cached DEM (API unavailable)")
        cached["status"] = "success"
        cached["_stale"] = True
        return cached

    # STEP 4: Tenter cache avec bounds elargis (voisinage)
    try:
        expanded = {
            "north": bounds["north"] + 0.01,
            "south": bounds["south"] - 0.01,
            "east": bounds["east"] + 0.01,
            "west": bounds["west"] - 0.01,
        }
        nearby, nearby_status = cache_get(expanded, dataset, resolution)
        if nearby is not None:
            logger.info("[SRTM] R4 fallback: using nearby cached DEM tile")
            nearby["status"] = "success"
            nearby["_nearby_fallback"] = True
            return nearby
    except Exception:
        pass

    logger.info("[SRTM] No DEM available — pipeline uses heuristic signals")
    return None


def sample_dem_at_point(
    dem_data: Dict[str, Any],
    lat: float,
    lng: float,
) -> Optional[Dict[str, float]]:
    """
    Echantillonne les valeurs DEM a un point specifique (lat, lng).
    Retourne elevation, slope, aspect, roughness au point.
    """
    if not dem_data or dem_data.get("status") != "success":
        return None

    bounds = dem_data.get("bounds", {})
    fields = dem_data.get("fields", {})

    elevation = fields.get("elevation")
    slope = fields.get("slope")
    aspect = fields.get("aspect")
    roughness = fields.get("roughness")

    if elevation is None:
        return None

    rows, cols = elevation.shape
    lat_span = bounds.get("north", 0) - bounds.get("south", 0)
    lng_span = bounds.get("east", 0) - bounds.get("west", 0)

    if lat_span < 1e-9 or lng_span < 1e-9:
        return None

    row = int((bounds["north"] - lat) / lat_span * rows)
    col = int((lng - bounds["west"]) / lng_span * cols)
    row = max(0, min(rows - 1, row))
    col = max(0, min(cols - 1, col))

    result = {"elevation_m": float(elevation[row, col])}

    if slope is not None:
        result["slope_deg"] = float(slope[row, col])
    if aspect is not None:
        result["aspect_deg"] = float(aspect[row, col])
    if roughness is not None:
        result["roughness"] = float(roughness[row, col])

    return result


def classify_terrain_at_point(
    dem_data: Dict[str, Any],
    lat: float,
    lng: float,
) -> str:
    """
    Classifie le type de terrain a un point.
    Retourne: 'valley', 'ridge', 'plateau', 'steep_slope', 'gentle_slope', 'flat'
    """
    sample = sample_dem_at_point(dem_data, lat, lng)
    if not sample:
        return "unknown"

    slope = sample.get("slope_deg", 0)
    roughness = sample.get("roughness", 0)
    elevation = sample.get("elevation_m", 0)

    stats = dem_data.get("stats", {})
    elev_mean = stats.get("elevation_mean", elevation)
    elev_range = stats.get("elevation_max", 0) - stats.get("elevation_min", 0)

    if slope > 35:
        return "steep_slope"
    if slope > 15:
        return "moderate_slope"

    # Relative elevation position
    if elev_range > 10:
        rel_elev = (elevation - elev_mean) / max(1, elev_range)
    else:
        rel_elev = 0

    if rel_elev < -0.25 and roughness < 3:
        return "valley"
    if rel_elev > 0.25 and slope < 10:
        return "plateau"
    if rel_elev > 0.30:
        return "ridge"
    if slope < 5 and roughness < 2:
        return "flat"

    return "gentle_slope"


def get_slope_grid_resampled(
    dem_data: Dict[str, Any],
    target_rows: int,
    target_cols: int,
) -> Optional[np.ndarray]:
    """
    Retourne la grille de pente (en degres) resamplee a la taille cible.
    Utilisee par trail_cost_grid_v7 pour le cout de traversee.
    """
    if not dem_data or dem_data.get("status") != "success":
        return None

    fields = dem_data.get("fields", {})
    slope = fields.get("slope")

    if slope is None:
        return None

    if slope.shape[0] == target_rows and slope.shape[1] == target_cols:
        return slope

    from scipy.ndimage import zoom

    zoom_y = target_rows / slope.shape[0]
    zoom_x = target_cols / slope.shape[1]
    resampled = zoom(slope, (zoom_y, zoom_x), order=1)

    return resampled[:target_rows, :target_cols]
