"""
SERVICE SENTINEL STAC — Catalogue Search for Sentinel-2 L2A
BIONIC V5 ULTIME 300% — sentinel_stac_v1

Interroge le catalogue STAC de Copernicus Data Space pour
trouver les meilleures images Sentinel-2 L2A sur un territoire.

Filtrage par: bbox, date, couverture nuageuse.
Module isole. 0 impact sur pipeline principal.
"""

import logging
import httpx
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional

logger = logging.getLogger("bionic_engine.sentinel_stac")

STAC_URL = "https://stac.dataspace.copernicus.eu/v1"
COLLECTION = "sentinel-2-l2a"


async def search_sentinel2(
    bounds: Dict[str, float],
    token: str,
    max_cloud_cover: float = 20.0,
    days_back: int = 90,
    max_items: int = 5,
) -> List[Dict[str, Any]]:
    """
    Search STAC catalogue for Sentinel-2 L2A images.

    Returns list of items sorted by cloud cover (ascending).
    """
    now = datetime.now(timezone.utc)
    start = (now - timedelta(days=days_back)).strftime("%Y-%m-%dT00:00:00Z")
    end = now.strftime("%Y-%m-%dT23:59:59Z")

    bbox = [bounds["west"], bounds["south"], bounds["east"], bounds["north"]]

    search_body = {
        "collections": [COLLECTION],
        "bbox": bbox,
        "datetime": f"{start}/{end}",
        "limit": max_items,
        "query": {
            "eo:cloud_cover": {"lte": max_cloud_cover},
        },
        "sortby": [{"field": "properties.eo:cloud_cover", "direction": "asc"}],
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{STAC_URL}/search",
            json=search_body,
            headers=headers,
        )
        response.raise_for_status()
        data = response.json()

    features = data.get("features", [])
    logger.info(f"STAC search: {len(features)} images found (bbox={bbox}, cloud<{max_cloud_cover}%)")

    results = []
    for feat in features:
        props = feat.get("properties", {})
        assets = feat.get("assets", {})

        b04_asset = assets.get("B04") or assets.get("B04_10m") or assets.get("red") or assets.get("b04")
        b08_asset = assets.get("B08") or assets.get("B08_10m") or assets.get("nir") or assets.get("b08")

        results.append({
            "id": feat.get("id", "unknown"),
            "datetime": props.get("datetime", ""),
            "cloud_cover": props.get("eo:cloud_cover", -1),
            "platform": props.get("platform", "sentinel-2"),
            "b04_href": b04_asset.get("href") if b04_asset else None,
            "b08_href": b08_asset.get("href") if b08_asset else None,
            "has_bands": bool(b04_asset and b08_asset),
            "bbox": feat.get("bbox", bbox),
            "asset_keys": list(assets.keys()),
        })

    return results


async def get_best_image(
    bounds: Dict[str, float],
    token: str,
    max_cloud_cover: float = 20.0,
    days_back: int = 90,
) -> Optional[Dict[str, Any]]:
    """Get the best (lowest cloud cover) Sentinel-2 image for the area."""
    items = await search_sentinel2(bounds, token, max_cloud_cover, days_back, max_items=5)

    for item in items:
        if item["has_bands"]:
            logger.info(f"Best image: {item['id']} (cloud={item['cloud_cover']}%)")
            return item

    if items:
        logger.warning(f"Found {len(items)} images but none with accessible B04/B08 bands")
        return items[0]

    logger.warning("No Sentinel-2 images found for this area/timeframe")
    return None
