"""
SERVICE WEATHER CACHE — MongoDB Cache for Weather Data
BIONIC V5 ULTIME 300% — Norme de modularite stricte

Cache versionne des resultats meteo par territoire + resolution.
TTL court (6h) car meteo change rapidement.
"""

import os
import hashlib
import logging
import numpy as np
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, Tuple
from pymongo import MongoClient

logger = logging.getLogger("bionic_engine.weather_cache")

DEFAULT_TTL_HOURS = 6


def _get_collection():
    client = MongoClient(os.environ.get("MONGO_URL"))
    return client[os.environ.get("DB_NAME")]["weather_cache"]


def _cache_key(bounds: Dict[str, float], resolution: int) -> str:
    raw = f"{bounds['north']:.4f}_{bounds['south']:.4f}_{bounds['east']:.4f}_{bounds['west']:.4f}_{resolution}"
    return hashlib.sha256(raw.encode()).hexdigest()[:24]


def _serialize(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.floating, np.integer)):
        return float(obj)
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_serialize(v) for v in obj]
    return obj


def _deserialize_fields(fields):
    result = {}
    for k, v in fields.items():
        if isinstance(v, list):
            result[k] = np.array(v, dtype=np.float64)
        else:
            result[k] = v
    return result


def cache_put(
    bounds: Dict[str, float],
    resolution: int,
    species: str,
    weather_result: Dict[str, Any],
    ttl_hours: int = DEFAULT_TTL_HOURS,
) -> Dict[str, Any]:
    collection = _get_collection()
    key = _cache_key(bounds, resolution)
    now = datetime.now(timezone.utc)
    expires = now + timedelta(hours=ttl_hours)

    doc = {
        "cache_key": key,
        "bounds": bounds,
        "resolution": resolution,
        "species": species,
        "stats": _serialize(weather_result.get("stats", {})),
        "fields": _serialize(weather_result.get("fields", {})),
        "source_id": weather_result.get("source_id", ""),
        "provider": weather_result.get("provider", "Open-Meteo"),
        "latitude": weather_result.get("latitude"),
        "longitude": weather_result.get("longitude"),
        "elevation": weather_result.get("elevation"),
        "fetched_at": weather_result.get("fetched_at", now.isoformat()),
        "created_at": now.isoformat(),
        "expires_at": expires.isoformat(),
        "ttl_hours": ttl_hours,
        "version": "BIONIC_V5_ULTIME_300",
    }

    collection.update_one({"cache_key": key}, {"$set": doc}, upsert=True)
    logger.info(f"WEATHER CACHE PUT: key={key}")

    return {"cache_key": key, "action": "stored", "expires_at": expires.isoformat()}


def cache_get(
    bounds: Dict[str, float],
    resolution: int,
) -> Tuple[Optional[Dict[str, Any]], str]:
    collection = _get_collection()
    key = _cache_key(bounds, resolution)
    now = datetime.now(timezone.utc)

    doc = collection.find_one({"cache_key": key}, {"_id": 0})
    if doc is None:
        logger.info(f"WEATHER CACHE MISS: key={key}")
        return None, "miss"

    expires_str = doc.get("expires_at", "")
    if expires_str:
        expires = datetime.fromisoformat(expires_str)
        if now > expires:
            logger.info(f"WEATHER CACHE EXPIRED: key={key}")
            return None, "expired"

    doc["fields"] = _deserialize_fields(doc.get("fields", {}))
    logger.info(f"WEATHER CACHE HIT: key={key}")
    return doc, "hit"


def cache_stats() -> Dict[str, Any]:
    collection = _get_collection()
    total = collection.count_documents({})
    now = datetime.now(timezone.utc)
    active = expired = 0
    entries = []

    for doc in collection.find({}, {"_id": 0, "fields": 0}):
        exp = doc.get("expires_at", "")
        is_expired = bool(exp and now > datetime.fromisoformat(exp))
        if is_expired:
            expired += 1
        else:
            active += 1
        entries.append({
            "cache_key": doc.get("cache_key"),
            "bounds": doc.get("bounds"),
            "resolution": doc.get("resolution"),
            "species": doc.get("species"),
            "fetched_at": doc.get("fetched_at"),
            "expires_at": doc.get("expires_at"),
            "status": "expired" if is_expired else "active",
        })

    return {"total_entries": total, "active": active, "expired": expired, "entries": entries}
