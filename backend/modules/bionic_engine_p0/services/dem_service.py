"""
SERVICE DEM — Digital Elevation Model (OpenTopography)
BIONIC V5 ULTIME 300% — PHASE G+ Real Data

Wrapper pour l'API OpenTopography (SRTM GL1 30m, GL3 90m, AW3D30).
Retourne les donnees d'elevation en numpy array + stats derivees.
Calcule: elevation, pente (slope), aspect, rugosité.

source_id dynamique: DEM_{SPECIES}
Consommateur: TCVE, TFE (mode donnees reelles)
"""

import os
import logging
import numpy as np
import httpx
from typing import Dict, Any, Optional
from scipy.ndimage import sobel

logger = logging.getLogger("bionic_engine.dem_service")

OPENTOPOGRAPHY_BASE_URL = "https://portal.opentopography.org/API/globaldem"


async def fetch_dem_raw(
    bounds: Dict[str, float],
    dataset: str = "SRTMGL1",
) -> Optional[np.ndarray]:
    """Fetch raw DEM data from OpenTopography API as numpy array."""
    api_key = os.environ.get("OPENTOPOGRAPHY_API_KEY", "")
    if not api_key:
        logger.warning("OPENTOPOGRAPHY_API_KEY not configured")
        return None

    params = {
        "demtype": dataset,
        "south": bounds["south"],
        "north": bounds["north"],
        "west": bounds["west"],
        "east": bounds["east"],
        "outputFormat": "GTiff",
        "API_Key": api_key,
    }

    try:
        async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
            response = await client.get(OPENTOPOGRAPHY_BASE_URL, params=params)
            response.raise_for_status()

            from rasterio.io import MemoryFile
            with MemoryFile(response.content) as memfile:
                with memfile.open() as ds:
                    elevation = ds.read(1).astype(np.float64)
                    logger.info(f"DEM fetched: shape={elevation.shape}, range=[{elevation.min():.1f}, {elevation.max():.1f}]m")
                    return elevation

    except httpx.HTTPStatusError as e:
        logger.error(f"OpenTopography HTTP error: {e.response.status_code}")
        if e.response.status_code == 401:
            raise ValueError("Cle API OpenTopography invalide")
        elif e.response.status_code == 429:
            raise RuntimeError("Rate limit OpenTopography depasse (200 requetes/24h)")
        raise
    except Exception as e:
        logger.error(f"DEM fetch error: {e}")
        raise


def compute_slope(dem: np.ndarray, pixel_size_m: float = 30.0) -> np.ndarray:
    """Compute slope in degrees from DEM using Sobel operator."""
    grad_x = sobel(dem, axis=1) / (8 * pixel_size_m)
    grad_y = sobel(dem, axis=0) / (8 * pixel_size_m)
    slope_rad = np.arctan(np.sqrt(grad_x**2 + grad_y**2))
    return np.degrees(slope_rad)


def compute_aspect(dem: np.ndarray, pixel_size_m: float = 30.0) -> np.ndarray:
    """Compute aspect (slope direction) 0-360 degrees, 0=North."""
    grad_x = sobel(dem, axis=1) / (8 * pixel_size_m)
    grad_y = sobel(dem, axis=0) / (8 * pixel_size_m)
    aspect = np.degrees(np.arctan2(grad_x, -grad_y))
    return (aspect + 360) % 360


def compute_roughness(dem: np.ndarray) -> np.ndarray:
    """Compute terrain roughness (standard deviation in 3x3 window)."""
    from scipy.ndimage import uniform_filter
    mean = uniform_filter(dem, size=3)
    mean_sq = uniform_filter(dem**2, size=3)
    variance = mean_sq - mean**2
    variance = np.maximum(variance, 0)
    return np.sqrt(variance)


def resample_to_resolution(arr: np.ndarray, target_resolution: int) -> np.ndarray:
    """Resample a 2D array to target resolution using bilinear interpolation."""
    from scipy.ndimage import zoom
    if arr.shape[0] == target_resolution and arr.shape[1] == target_resolution:
        return arr
    zoom_y = target_resolution / arr.shape[0]
    zoom_x = target_resolution / arr.shape[1]
    return zoom(arr, (zoom_y, zoom_x), order=1)


async def fetch_dem_composite(
    bounds: Dict[str, float],
    species: str,
    resolution: int = 60,
    dataset: str = "SRTMGL1",
) -> Dict[str, Any]:
    """Fetch DEM and compute all derived fields."""
    source_id = f"DEM_{species.upper()}"

    raw_dem = await fetch_dem_raw(bounds, dataset)
    if raw_dem is None:
        return {"source_id": source_id, "status": "no_api_key", "species": species}

    center_lat = (bounds["north"] + bounds["south"]) / 2
    pixel_size_m = ((bounds["north"] - bounds["south"]) * 111320.0) / raw_dem.shape[0]

    slope = compute_slope(raw_dem, pixel_size_m)
    aspect = compute_aspect(raw_dem, pixel_size_m)
    roughness = compute_roughness(raw_dem)

    # Resample to pipeline resolution
    dem_r = resample_to_resolution(raw_dem, resolution)
    slope_r = resample_to_resolution(slope, resolution)
    aspect_r = resample_to_resolution(aspect, resolution)
    roughness_r = resample_to_resolution(roughness, resolution)

    # Normalize for pipeline compatibility [0,1]
    def _norm(arr):
        mn, mx = arr.min(), arr.max()
        if mx - mn < 1e-10:
            return np.zeros_like(arr)
        return (arr - mn) / (mx - mn)

    return {
        "source_id": source_id,
        "species": species,
        "bounds": bounds,
        "dataset": dataset,
        "resolution": resolution,
        "raw_shape": list(raw_dem.shape),
        "fields": {
            "elevation": dem_r,
            "slope": slope_r,
            "aspect": aspect_r,
            "roughness": roughness_r,
            "elevation_normalized": _norm(dem_r),
            "slope_normalized": _norm(slope_r),
            "roughness_normalized": _norm(roughness_r),
        },
        "stats": {
            "elevation_min": round(float(raw_dem.min()), 2),
            "elevation_max": round(float(raw_dem.max()), 2),
            "elevation_mean": round(float(raw_dem.mean()), 2),
            "slope_mean_deg": round(float(slope.mean()), 2),
            "slope_max_deg": round(float(slope.max()), 2),
            "aspect_mean_deg": round(float(aspect.mean()), 2),
            "roughness_mean": round(float(roughness.mean()), 2),
            "pixel_size_m": round(pixel_size_m, 2),
        },
        "status": "success",
        "validation": {
            "data_real": True,
            "source": "OpenTopography",
            "dataset": dataset,
        },
    }
