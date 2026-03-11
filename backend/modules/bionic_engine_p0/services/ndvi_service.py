"""
SERVICE NDVI — NDVI Calculation via Sentinel Hub Process API
BIONIC V5 ULTIME 300% — ndvi_v1

Utilise l'API Sentinel Hub Process pour calculer le NDVI directement
cote serveur (pas besoin de telecharger les bandes brutes).

Evalscript: NDVI = (B08 - B04) / (B08 + B04)
Fallback vers NDVI synthetique si indisponible.
Module isole. Shadow Mode. 0 impact sur pipeline principal.
"""

import hashlib
import io
import logging
import time
import numpy as np
import httpx
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional

logger = logging.getLogger("bionic_engine.ndvi_service")

SH_PROCESS_URL = "https://sh.dataspace.copernicus.eu/api/v1/process"

EVALSCRIPT_NDVI = """//VERSION=3
function setup() {
  return {
    input: [{bands: ["B04", "B08"], units: "DN"}],
    output: {bands: 1, sampleType: "FLOAT32"}
  };
}
function evaluatePixel(sample) {
  let denom = sample.B08 + sample.B04;
  if (denom == 0) return [-9999];
  return [(sample.B08 - sample.B04) / denom];
}
"""


def compute_ndvi_stats(ndvi_field: np.ndarray) -> Dict[str, Any]:
    """Compute statistics from an NDVI field."""
    valid = ndvi_field[ndvi_field > -0.5]
    if len(valid) == 0:
        valid = ndvi_field.flatten()

    return {
        "mean": round(float(np.mean(valid)), 4),
        "min": round(float(np.min(valid)), 4),
        "max": round(float(np.max(valid)), 4),
        "std": round(float(np.std(valid)), 4),
        "median": round(float(np.median(valid)), 4),
        "vegetation_pct": round(float(np.sum(valid > 0.2) / max(len(valid), 1) * 100), 1),
        "dense_vegetation_pct": round(float(np.sum(valid > 0.5) / max(len(valid), 1) * 100), 1),
        "bare_soil_pct": round(float(np.sum(valid < 0.1) / max(len(valid), 1) * 100), 1),
    }


async def fetch_ndvi_via_process_api(
    bounds: Dict[str, float],
    token: str,
    resolution: int = 30,
    days_back: int = 90,
    max_cloud_cover: float = 20.0,
) -> Optional[Dict[str, Any]]:
    """
    Use Sentinel Hub Process API to compute NDVI server-side.
    Returns a resolution x resolution NDVI field.
    """
    now = datetime.now(timezone.utc)
    from_date = (now - timedelta(days=days_back)).strftime("%Y-%m-%dT00:00:00Z")
    to_date = now.strftime("%Y-%m-%dT23:59:59Z")

    request_body = {
        "input": {
            "bounds": {
                "bbox": [bounds["west"], bounds["south"], bounds["east"], bounds["north"]],
                "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/4326"},
            },
            "data": [{
                "type": "sentinel-2-l2a",
                "dataFilter": {
                    "timeRange": {"from": from_date, "to": to_date},
                    "maxCloudCoverage": max_cloud_cover,
                    "mosaickingOrder": "leastCC",
                },
            }],
        },
        "output": {
            "width": resolution,
            "height": resolution,
            "responses": [{
                "identifier": "default",
                "format": {"type": "image/tiff"},
            }],
        },
        "evalscript": EVALSCRIPT_NDVI,
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "image/tiff",
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(SH_PROCESS_URL, json=request_body, headers=headers)
            response.raise_for_status()

        import rasterio
        with rasterio.open(io.BytesIO(response.content)) as src:
            ndvi_raw = src.read(1)

        ndvi_raw = np.where(ndvi_raw <= -9998, np.nan, ndvi_raw)
        ndvi_raw = np.nan_to_num(ndvi_raw, nan=0.0)
        ndvi_field = np.clip(ndvi_raw, -1.0, 1.0)

        logger.info(
            f"NDVI Process API success: shape={ndvi_field.shape}, "
            f"mean={np.mean(ndvi_field):.4f}, range=[{np.min(ndvi_field):.4f}, {np.max(ndvi_field):.4f}]"
        )

        return {
            "ndvi_field": ndvi_field.astype(np.float64),
            "raw_shape": list(ndvi_raw.shape),
            "resampled_shape": [resolution, resolution],
            "source": "sentinel2_process_api",
            "date_range": f"{from_date}/{to_date}",
        }

    except httpx.HTTPStatusError as e:
        body = e.response.text[:200] if e.response else ""
        logger.error(f"SH Process API HTTP error {e.response.status_code}: {body}")
        return None
    except Exception as e:
        logger.error(f"SH Process API error: {e}")
        return None


def generate_synthetic_ndvi(
    bounds: Dict[str, float],
    resolution: int = 30,
    species: str = "moose",
) -> Dict[str, Any]:
    """Generate synthetic NDVI field as fallback."""
    seed = int(hashlib.md5(
        f"NDVI_{bounds['north']:.4f}_{bounds['west']:.4f}_{species}".encode()
    ).hexdigest()[:8], 16)
    rng = np.random.RandomState(seed & 0x7FFFFFFF)

    base = rng.uniform(0.3, 0.8, (resolution, resolution))
    gradient = np.linspace(0.1, 0.0, resolution).reshape(-1, 1)
    ndvi_field = np.clip(base + gradient + rng.normal(0, 0.05, (resolution, resolution)), -0.1, 1.0)

    return {
        "ndvi_field": ndvi_field.astype(np.float64),
        "raw_shape": [resolution, resolution],
        "resampled_shape": [resolution, resolution],
        "source": "synthetic_fallback",
    }


async def fetch_ndvi_composite(
    bounds: Dict[str, float],
    species: str,
    resolution: int = 30,
) -> Dict[str, Any]:
    """
    Complete NDVI pipeline: OAuth2 -> Process API -> NDVI field.
    Falls back to synthetic if real data unavailable.
    """
    from modules.bionic_engine_p0.services.sentinel_oauth_service import get_access_token

    source_id = f"NDVI_{species.upper()}"
    start = time.time()

    try:
        token = await get_access_token()
    except Exception as e:
        logger.warning(f"OAuth2 failed, using synthetic: {e}")
        result = generate_synthetic_ndvi(bounds, resolution, species)
        stats = compute_ndvi_stats(result["ndvi_field"])
        return {
            "source_id": source_id, "species": species, "bounds": bounds,
            "resolution": resolution, "source": "synthetic_fallback",
            "reason": f"oauth_failed: {str(e)[:100]}",
            "stats": stats, "fields": {"ndvi_field": result["ndvi_field"]},
            "computation_time_ms": round((time.time() - start) * 1000, 1),
            "status": "fallback",
        }

    ndvi_result = await fetch_ndvi_via_process_api(bounds, token, resolution)

    if ndvi_result:
        stats = compute_ndvi_stats(ndvi_result["ndvi_field"])
        return {
            "source_id": source_id, "species": species, "bounds": bounds,
            "resolution": resolution, "source": "sentinel2_real",
            "date_range": ndvi_result.get("date_range"),
            "stats": stats, "fields": {"ndvi_field": ndvi_result["ndvi_field"]},
            "raw_shape": ndvi_result.get("raw_shape"),
            "computation_time_ms": round((time.time() - start) * 1000, 1),
            "status": "success",
            "validation": {"data_real": True, "source": "Sentinel Hub Process API"},
        }

    from modules.bionic_engine_p0.services.sentinel_stac_service import get_best_image

    stac_info = {}
    try:
        image = await get_best_image(bounds, token)
        if image:
            stac_info = {
                "image_found": True, "image_id": image.get("id"),
                "cloud_cover": image.get("cloud_cover"),
            }
        else:
            stac_info = {"image_found": False}
    except Exception:
        stac_info = {"image_found": False, "stac_error": True}

    result = generate_synthetic_ndvi(bounds, resolution, species)
    stats = compute_ndvi_stats(result["ndvi_field"])
    return {
        "source_id": source_id, "species": species, "bounds": bounds,
        "resolution": resolution, "source": "synthetic_fallback",
        "reason": "process_api_failed",
        "stac_info": stac_info, "stats": stats,
        "fields": {"ndvi_field": result["ndvi_field"]},
        "computation_time_ms": round((time.time() - start) * 1000, 1),
        "status": "fallback",
    }
