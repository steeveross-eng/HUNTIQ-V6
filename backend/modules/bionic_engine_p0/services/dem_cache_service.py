"""
SERVICE DEM CACHE — MongoDB Cache for DEM Data
BIONIC V5 ULTIME 300% — Norme de modularite stricte

Cache versionne des resultats DEM par territoire + dataset + resolution.
TTL configurable (defaut 90 jours). Logs complets: hit/miss/fallback.
Aucun ecrasement automatique. Tracabilite totale.

Cle de cache: hash(territoire_bounds + dataset + resolution)
Collection: dem_cache
"""

import os
import hashlib
import logging
import numpy as np
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, Tuple
from pymongo import MongoClient

logger = logging.getLogger("bionic_engine.dem_cache")

DEFAULT_TTL_DAYS = 90


def _get_collection():
    mongo_url = os.environ.get("MONGO_URL")
    db_name = os.environ.get("DB_NAME")
    client = MongoClient(mongo_url)
    return client[db_name]["dem_cache"]


def _cache_key(bounds: Dict[str, float], dataset: str, resolution: int) -> str:
    """Generate deterministic cache key from territory + dataset + resolution."""
    raw = f"{bounds['north']:.6f}_{bounds['south']:.6f}_{bounds['east']:.6f}_{bounds['west']:.6f}_{dataset}_{resolution}"
    return hashlib.sha256(raw.encode()).hexdigest()[:24]


def _serialize_stats(stats: Dict[str, Any]) -> Dict[str, Any]:
    """Convert stats to JSON-serializable format."""
    serialized = {}
    for k, v in stats.items():
        if isinstance(v, (np.floating, np.integer)):
            serialized[k] = float(v)
        elif isinstance(v, np.ndarray):
            serialized[k] = v.tolist()
        elif isinstance(v, list):
            serialized[k] = [float(x) if isinstance(x, (np.floating, np.integer)) else x for x in v]
        else:
            serialized[k] = v
    return serialized


def _serialize_fields(fields: Dict[str, Any]) -> Dict[str, Any]:
    """Serialize numpy array fields to lists for MongoDB storage."""
    serialized = {}
    for k, v in fields.items():
        if isinstance(v, np.ndarray):
            serialized[k] = v.tolist()
        else:
            serialized[k] = v
    return serialized


def _deserialize_fields(fields: Dict[str, Any]) -> Dict[str, Any]:
    """Deserialize list fields back to numpy arrays."""
    deserialized = {}
    for k, v in fields.items():
        if isinstance(v, list):
            deserialized[k] = np.array(v, dtype=np.float64)
        else:
            deserialized[k] = v
    return deserialized


def cache_put(
    bounds: Dict[str, float],
    dataset: str,
    resolution: int,
    species: str,
    dem_result: Dict[str, Any],
    ttl_days: int = DEFAULT_TTL_DAYS,
) -> Dict[str, Any]:
    """Store DEM result in cache. Returns cache metadata."""
    collection = _get_collection()
    key = _cache_key(bounds, dataset, resolution)
    now = datetime.now(timezone.utc)
    expires = now + timedelta(days=ttl_days)

    doc = {
        "cache_key": key,
        "bounds": bounds,
        "dataset": dataset,
        "resolution": resolution,
        "species": species,
        "raw_shape": dem_result.get("raw_shape", []),
        "stats": _serialize_stats(dem_result.get("stats", {})),
        "fields": _serialize_fields(dem_result.get("fields", {})),
        "source_id": dem_result.get("source_id", ""),
        "created_at": now.isoformat(),
        "expires_at": expires.isoformat(),
        "ttl_days": ttl_days,
        "version": "BIONIC_V5_ULTIME_300",
        "status": "cached",
    }

    # Upsert by cache_key (no auto-overwrite — explicit upsert)
    collection.update_one(
        {"cache_key": key},
        {"$set": doc},
        upsert=True,
    )

    logger.info(f"DEM CACHE PUT: key={key}, bounds={bounds}, dataset={dataset}, res={resolution}")

    return {
        "cache_key": key,
        "action": "stored",
        "created_at": now.isoformat(),
        "expires_at": expires.isoformat(),
        "ttl_days": ttl_days,
    }


def cache_get(
    bounds: Dict[str, float],
    dataset: str,
    resolution: int,
) -> Tuple[Optional[Dict[str, Any]], str]:
    """Retrieve DEM result from cache. Returns (result, status)."""
    collection = _get_collection()
    key = _cache_key(bounds, dataset, resolution)
    now = datetime.now(timezone.utc)

    doc = collection.find_one({"cache_key": key}, {"_id": 0})

    if doc is None:
        logger.info(f"DEM CACHE MISS: key={key}")
        return None, "miss"

    # Check TTL
    expires_str = doc.get("expires_at", "")
    if expires_str:
        expires = datetime.fromisoformat(expires_str)
        if now > expires:
            # R4: Retourner les donnees stale comme fallback (au lieu de None)
            logger.info(f"DEM CACHE STALE: key={key} (expired but data available for R4 fallback)")
            doc["fields"] = _deserialize_fields(doc.get("fields", {}))
            return doc, "stale"

    # Deserialize fields
    doc["fields"] = _deserialize_fields(doc.get("fields", {}))

    logger.info(f"DEM CACHE HIT: key={key}, created={doc.get('created_at')}")
    return doc, "hit"


def cache_invalidate(
    bounds: Dict[str, float],
    dataset: str,
    resolution: int,
) -> Dict[str, Any]:
    """Manually invalidate a cache entry."""
    collection = _get_collection()
    key = _cache_key(bounds, dataset, resolution)
    result = collection.delete_one({"cache_key": key})

    status = "invalidated" if result.deleted_count > 0 else "not_found"
    logger.info(f"DEM CACHE INVALIDATE: key={key}, status={status}")

    return {"cache_key": key, "action": status}


def cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    collection = _get_collection()
    total = collection.count_documents({})
    now = datetime.now(timezone.utc)

    expired = 0
    active = 0
    entries = []

    for doc in collection.find({}, {"_id": 0, "fields": 0}):
        expires_str = doc.get("expires_at", "")
        if expires_str:
            expires = datetime.fromisoformat(expires_str)
            if now > expires:
                expired += 1
            else:
                active += 1
        entries.append({
            "cache_key": doc.get("cache_key"),
            "bounds": doc.get("bounds"),
            "dataset": doc.get("dataset"),
            "resolution": doc.get("resolution"),
            "species": doc.get("species"),
            "created_at": doc.get("created_at"),
            "expires_at": doc.get("expires_at"),
            "status": "expired" if (expires_str and now > datetime.fromisoformat(expires_str)) else "active",
        })

    return {
        "total_entries": total,
        "active": active,
        "expired": expired,
        "entries": entries,
    }
