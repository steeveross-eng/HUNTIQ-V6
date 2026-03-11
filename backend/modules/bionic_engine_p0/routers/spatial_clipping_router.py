"""
BIONIC V5 300% — Spatial Clipping & Snapshot Router
=====================================================
INVARIANT BIONIC V5 300%:
- POST /api/v1/bionic/clipped-zones — Zones clippées 1km × 1km (CACHED)
- POST /api/v1/bionic/snapshot — Snapshot Territoire exportable
"""

import logging
import hashlib
import time
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from collections import OrderedDict

logger = logging.getLogger("bionic_engine.spatial_clipping_router")

router = APIRouter(prefix="/api/v1/bionic", tags=["BIONIC Spatial Clipping"])


# ============================================
# PHASE 5 — Cache déterministe pour /clipped-zones
# Clé: hash(lat_4dec + lng_4dec + species + resolution + layers)
# Le cache NE MODIFIE JAMAIS le résultat. Même input = même output.
# ============================================
class _ClippedZonesCache:
    def __init__(self, max_entries=200, ttl_seconds=3600):
        self._cache = OrderedDict()
        self._max = max_entries
        self._ttl = ttl_seconds

    def _key(self, req) -> str:
        layers_str = ",".join(sorted(req.layers)) if req.layers else "all"
        raw = f"{req.lat:.4f}|{req.lng:.4f}|{req.species}|{req.resolution}|{layers_str}"
        return hashlib.md5(raw.encode()).hexdigest()

    def get(self, req):
        k = self._key(req)
        if k in self._cache:
            entry = self._cache[k]
            if time.time() - entry["ts"] < self._ttl:
                self._cache.move_to_end(k)
                return entry["data"]
            del self._cache[k]
        return None

    def put(self, req, data):
        k = self._key(req)
        self._cache[k] = {"data": data, "ts": time.time()}
        if len(self._cache) > self._max:
            self._cache.popitem(last=False)

_clipped_cache = _ClippedZonesCache()


class ClippedZonesRequest(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    species: str = "moose"
    layers: Optional[List[str]] = None
    resolution: int = Field(default=80, ge=30, le=150)
    max_zones_per_layer: int = Field(default=8, ge=1, le=20)
    include_scoring: bool = True
    season: Optional[str] = None


class SnapshotRequest(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    species: str = "moose"
    waypoint_name: Optional[str] = None
    layers_visible: Optional[Dict[str, bool]] = None
    active_params: Optional[Dict[str, Any]] = None


@router.post("/clipped-zones")
async def generate_clipped_zones(request: ClippedZonesRequest):
    """
    Génère des zones organiques clippées dans un carré 1km × 1km.
    
    INVARIANT BIONIC V5 300%:
    - Aucune géométrie hors périmètre
    - Clipping strict via ST_Intersection (Shapely)
    """
    try:
        # PHASE 5: Cache déterministe — même input = même output
        cached = _clipped_cache.get(request)
        if cached is not None:
            logger.info(f"[CACHE HIT] clipped-zones lat={request.lat:.4f} lng={request.lng:.4f}")
            return cached

        t0 = time.time()
        from modules.bionic_engine_p0.services.spatial_clipping import (
            compute_analysis_bbox, clip_zones, compute_clipping_stats
        )
        from modules.bionic_engine_p0.services.zone_engine_core_v2 import generate_organic_zones
        from modules.bionic_engine_p0.services.scoring_zone_integration import enrich_geojson_with_scores
        bbox = compute_analysis_bbox(request.lat, request.lng)

        # 2. Générer les zones organiques dans le bbox
        bounds = {
            "north": bbox["north"],
            "south": bbox["south"],
            "east": bbox["east"],
            "west": bbox["west"],
        }

        season = request.season
        if not season:
            month = datetime.now(timezone.utc).month
            season = ["winter", "winter", "spring", "spring", "spring", "summer",
                       "summer", "summer", "autumn", "autumn", "autumn", "winter"][month - 1]

        geojson = await generate_organic_zones(
            bounds=bounds,
            species=request.species,
            layers=request.layers,
            resolution=request.resolution,
            max_zones_per_layer=request.max_zones_per_layer,
        )

        # BIONIC V7.4: Skip legacy V5 scoring when V7 engine is active
        import os
        engine_version = os.environ.get("EXCLUSION_ENGINE_VERSION", "v5")
        if request.include_scoring and engine_version != "v7":
            geojson = enrich_geojson_with_scores(geojson, request.species, season)

        # 3. Extraire les zones du GeoJSON
        features = geojson.get("features", [])
        zones = []
        for f in features:
            props = f.get("properties", {})
            coords_raw = f.get("geometry", {}).get("coordinates", [])
            # GeoJSON: [lng, lat] → convertir en [lat, lng]
            if coords_raw and len(coords_raw) > 0:
                ring = coords_raw[0] if isinstance(coords_raw[0][0], list) else coords_raw
                coords = [[c[1], c[0]] for c in ring]
                zones.append({
                    "coordinates": coords,
                    "center": [props.get("center_lat", request.lat), props.get("center_lng", request.lng)],
                    "layerId": props.get("layer_id", "unknown"),
                    "score": props.get("score", 0),
                    **props,
                })

        # 4. Appliquer le clipping strict
        clipped = clip_zones(zones, bbox)
        stats = compute_clipping_stats(zones, clipped, bbox)

        elapsed_ms = round((time.time() - t0) * 1000)
        result = {
            "clipped_zones": clipped,
            "analysis_bbox": bbox,
            "stats": {**stats, "response_time_ms": elapsed_ms, "cache": "MISS"},
            "metadata": {
                "species": request.species,
                "season": season,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "clipping_invariant": "BIONIC_V5_300_STRICT",
            },
        }

        # PHASE 5: Stocker dans le cache — le cache NE MODIFIE JAMAIS le résultat
        _clipped_cache.put(request, result)
        logger.info(f"[CACHE MISS] clipped-zones lat={request.lat:.4f} lng={request.lng:.4f} time={elapsed_ms}ms zones={len(clipped)}")
        return result

    except Exception as e:
        logger.error(f"Clipped zones error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/snapshot")
async def generate_snapshot(request: SnapshotRequest):
    """
    Génère un Snapshot Territoire complet dans le carré 1km × 1km.
    Contient toutes les données pour export PDF/JSON.
    
    INVARIANT: 100% déterministe — même waypoint + même espèce = même snapshot.
    """
    try:
        from modules.bionic_engine_p0.services.spatial_clipping import (
            compute_analysis_bbox, clip_zones, compute_clipping_stats
        )
        from modules.bionic_engine_p0.services.zone_engine_core_v2 import generate_organic_zones
        from modules.bionic_engine_p0.services.scoring_zone_integration import enrich_geojson_with_scores

        # 1. Bbox 1km × 1km
        bbox = compute_analysis_bbox(request.lat, request.lng)
        bounds = {
            "north": bbox["north"], "south": bbox["south"],
            "east": bbox["east"], "west": bbox["west"],
        }

        month = datetime.now(timezone.utc).month
        season = ["winter", "winter", "spring", "spring", "spring", "summer",
                   "summer", "summer", "autumn", "autumn", "autumn", "winter"][month - 1]

        # 2. Générer TOUTES les zones (toutes couches structurelles)
        geojson = await generate_organic_zones(
            bounds=bounds, species=request.species,
            layers=None, resolution=80, max_zones_per_layer=8,
        )
        # BIONIC V7.4: Skip legacy V5 scoring when V7 engine is active
        import os
        engine_version = os.environ.get("EXCLUSION_ENGINE_VERSION", "v5")
        if engine_version != "v7":
            geojson = enrich_geojson_with_scores(geojson, request.species, season)

        # 3. Extraire et clipper
        features = geojson.get("features", [])
        zones = []
        for f in features:
            props = f.get("properties", {})
            coords_raw = f.get("geometry", {}).get("coordinates", [])
            if coords_raw and len(coords_raw) > 0:
                ring = coords_raw[0] if isinstance(coords_raw[0][0], list) else coords_raw
                coords = [[c[1], c[0]] for c in ring]
                zones.append({
                    "coordinates": coords,
                    "center": [props.get("center_lat", request.lat), props.get("center_lng", request.lng)],
                    "layerId": props.get("layer_id", "unknown"),
                    "score": props.get("score", 0),
                    **props,
                })

        clipped = clip_zones(zones, bbox)
        stats = compute_clipping_stats(zones, clipped, bbox)

        # 4. Dynamic scores
        dynamic_scores = None
        try:
            from routes.dynamic_scores import compute_dynamic_scores
            dynamic_scores = await compute_dynamic_scores(request.lat, request.lng, request.species)
        except Exception:
            dynamic_scores = {"score": 0, "note": "dynamic scores unavailable"}

        # 5. Compiler le snapshot
        snapshot = {
            "snapshot_id": f"snap_{request.lat:.4f}_{request.lng:.4f}_{request.species}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "BIONIC_V5_300_STRICT",
            "waypoint": {
                "name": request.waypoint_name or f"WP {request.lat:.4f}, {request.lng:.4f}",
                "lat": request.lat,
                "lng": request.lng,
            },
            "analysis_bbox": bbox,
            "species": request.species,
            "season": season,
            "structural_zones": [z for z in clipped if z.get("layerId") not in ("conditions", "exclusions", "dynamic", "meteo", "pression", "stress_thermique")],
            "dynamic_scores": dynamic_scores,
            "layers_visible": request.layers_visible or {},
            "active_params": request.active_params or {},
            "clipping_stats": stats,
            "zone_summary": {},
        }

        # Zone summary by layer
        for z in clipped:
            lid = z.get("layerId", "unknown")
            if lid not in snapshot["zone_summary"]:
                snapshot["zone_summary"][lid] = {"count": 0, "avg_score": 0, "scores": []}
            snapshot["zone_summary"][lid]["count"] += 1
            snapshot["zone_summary"][lid]["scores"].append(z.get("score", 0))

        for lid, info in snapshot["zone_summary"].items():
            scores = info.pop("scores")
            info["avg_score"] = round(sum(scores) / len(scores), 1) if scores else 0

        return snapshot

    except Exception as e:
        logger.error(f"Snapshot error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
