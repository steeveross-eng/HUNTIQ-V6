"""
BIONIC ENGINE — Terrain Data Router (Overpass API Proxy)
BIONIC V5 — Exclusion de terrain — TOLÉRANCE ZÉRO

Fournit les données d'exclusion géospatiales (eau, routes, urbain, infrastructures)
via un proxy vers l'API Overpass (OpenStreetMap).

Endpoint: POST /api/v1/bionic/terrain/terrain-data
Cache: MongoDB persistant TTL 1h (R5)
Tiling: Le frontend découpe les grands viewports en tuiles

Conformité: BIONIC V5 — Exclusion stricte des zones interdites
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import asyncio
import httpx
import json
import hashlib
import os
import logging
import time
import math
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger("bionic_engine.terrain_data")

router = APIRouter(prefix="/terrain", tags=["BIONIC Terrain Data"])

OVERPASS_API_URL = "https://overpass-api.de/api/interpreter"
# V7.3: Fallback mirrors for rate-limit resilience
OVERPASS_MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
]
OVERPASS_MAX_RETRIES = 3
OVERPASS_BACKOFF_BASE = 2  # seconds

# ── R5: MongoDB Cache ──────────────────────────────────────
MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME")
CACHE_TTL_SECONDS = 3600  # 1h

_mongo_client = None
_cache_collection = None


async def _get_cache_collection():
    """Initialise et retourne la collection MongoDB pour le cache Overpass."""
    global _mongo_client, _cache_collection
    if _cache_collection is not None:
        return _cache_collection
    _mongo_client = AsyncIOMotorClient(MONGO_URL)
    db = _mongo_client[DB_NAME]
    _cache_collection = db["overpass_cache_r5"]
    await _cache_collection.create_index(
        "created_at", expireAfterSeconds=CACHE_TTL_SECONDS
    )
    logger.info(f"[R5] MongoDB cache initialisé: overpass_cache_r5 (TTL={CACHE_TTL_SECONDS}s)")
    return _cache_collection


CACHE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "data", "osm_cache"
)


class TerrainDataRequest(BaseModel):
    south: float = Field(..., ge=40.0, le=65.0)
    west: float = Field(..., ge=-85.0, le=-50.0)
    north: float = Field(..., ge=40.0, le=65.0)
    east: float = Field(..., ge=-85.0, le=-50.0)
    exclude_types: List[str] = ["water", "roads", "urban", "infrastructure"]
    detail_level: str = "high"  # "low" = landuse + major roads, "high" = all details


def _cache_key(bbox: tuple, exclude_types: list, detail_level: str) -> str:
    rounded = tuple(round(c, 3) for c in bbox)
    key = f"{rounded}_{sorted(exclude_types)}_{detail_level}"
    return hashlib.md5(key.encode()).hexdigest()


async def _load_cache(cache_key: str) -> Optional[dict]:
    """R5: Charge depuis MongoDB, fallback disque."""
    try:
        col = await _get_cache_collection()
        doc = await col.find_one({"_id": cache_key}, {"_id": 0, "data": 1})
        if doc:
            logger.info(f"[R5] Cache hit MongoDB: {cache_key}")
            return doc["data"]
    except Exception as e:
        logger.warning(f"[R5] MongoDB cache read failed: {e}")
    # Fallback filesystem
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
    if os.path.exists(cache_file):
        if time.time() - os.path.getmtime(cache_file) < CACHE_TTL_SECONDS:
            try:
                with open(cache_file, "r") as f:
                    return json.load(f)
            except Exception:
                pass
    return None


async def _load_cache_expired(cache_key: str) -> Optional[dict]:
    """V7.3: Load EXPIRED cache as last resort when Overpass is unavailable.
    Better to use stale exclusions than no exclusions at all."""
    try:
        col = await _get_cache_collection()
        doc = await col.find_one({"_id": cache_key}, {"_id": 0, "data": 1})
        if doc:
            logger.info(f"[R5] Cache hit MongoDB (expired fallback): {cache_key}")
            return doc["data"]
    except Exception:
        pass
    # Fallback: disk cache even if expired
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r") as f:
                data = json.load(f)
            logger.info(f"[R5] Cache hit disk (expired fallback): {cache_key}")
            return data
        except Exception:
            pass
    return None


async def _save_cache(cache_key: str, data: dict):
    """R5: Sauvegarde dans MongoDB + disque."""
    try:
        col = await _get_cache_collection()
        await col.update_one(
            {"_id": cache_key},
            {"$set": {"data": data, "created_at": datetime.now(timezone.utc)}},
            upsert=True,
        )
        logger.info(f"[R5] Cache saved MongoDB: {cache_key}")
    except Exception as e:
        logger.warning(f"[R5] MongoDB cache write failed: {e}")
    # Also save to disk as fallback
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
    try:
        with open(cache_file, "w") as f:
            json.dump(data, f)
    except Exception as e:
        logger.warning(f"Cache file save failed: {e}")


def _build_overpass_query(south, west, north, east, exclude_types, detail_level):
    """
    Build an Overpass QL query — BIONIC V5 STRICT.
    
    TOLÉRANCE ZÉRO: Toutes les entités eau, urbaines, anthropiques,
    routes et infrastructures doivent être détectées et exclues.
    """
    bbox = f"{south},{west},{north},{east}"
    parts = ["[out:json][timeout:30];("]

    if "water" in exclude_types:
        # === EAU — TOLÉRANCE ZÉRO ===
        # Grandes masses d'eau (lacs, étangs, rivières, fleuve)
        parts.append(f'way["natural"="water"]({bbox});')
        parts.append(f'relation["natural"="water"]({bbox});')
        # Zones humides (marais, marécages, tourbières)
        parts.append(f'way["natural"="wetland"]({bbox});')
        parts.append(f'relation["natural"="wetland"]({bbox});')
        # Baies, estuaires, littoral
        parts.append(f'way["natural"~"bay|strait|coastline"]({bbox});')
        parts.append(f'relation["natural"~"bay|strait"]({bbox});')
        # Tag water=* (lacs, rivières, réservoirs, bassins, étangs)
        parts.append(f'way["water"]({bbox});')
        parts.append(f'relation["water"]({bbox});')
        # Waterway (fleuves, rivières, canaux, rives, ruisseaux, fossés)
        parts.append(f'way["waterway"~"river|riverbank|canal|stream|ditch|drain|dock"]({bbox});')
        parts.append(f'relation["waterway"~"river|riverbank|canal|dock"]({bbox});')
        # Réservoirs et bassins
        parts.append(f'way["landuse"~"reservoir|basin|salt_pond"]({bbox});')
        parts.append(f'relation["landuse"~"reservoir|basin"]({bbox});')

    if "roads" in exclude_types:
        # === ROUTES — TOLÉRANCE ZÉRO ===
        if detail_level == "high":
            parts.append(
                f'way["highway"~"motorway|motorway_link|trunk|trunk_link|primary|primary_link|secondary|secondary_link|tertiary|tertiary_link|residential|service|unclassified|living_street|pedestrian|track|footway|cycleway|path"]({bbox});'
            )
        else:
            parts.append(
                f'way["highway"~"motorway|motorway_link|trunk|trunk_link|primary|primary_link|secondary|secondary_link|tertiary|tertiary_link|residential|unclassified|living_street"]({bbox});'
            )

    if "urban" in exclude_types:
        # === ZONES URBAINES ET ANTHROPIQUES — TOLÉRANCE ZÉRO ===
        # Landuse urbain, récréatif, militaire, etc.
        # BIONIC V7.3: farmland/farmyard/orchard/vineyard/allotments RETIRÉS
        # Ces tags agricoles couvrent de vastes surfaces en milieu rural
        # et provoquaient le rejet de 100% des zones dans les contextes ruraux/chassables.
        urban_landuse = "residential|commercial|industrial|retail|recreation_ground|cemetery|construction|military|quarry|landfill"
        parts.append(f'way["landuse"~"{urban_landuse}"]({bbox});')
        parts.append(f'relation["landuse"~"{urban_landuse}"]({bbox});')

        # Aménités (écoles, hôpitaux, etc.) — zones polygonales
        parts.append(f'way["amenity"~"school|university|hospital|parking|fuel|place_of_worship|police|fire_station|townhall|community_centre|marketplace"]({bbox});')

        # Loisirs (parcs urbains, terrains de sport, etc.)
        parts.append(f'way["leisure"~"park|garden|playground|sports_centre|stadium|pitch|golf_course|swimming_pool|fitness_centre|recreation_ground|dog_park"]({bbox});')

        if detail_level == "high":
            # Bâtiments — high detail uniquement (trop lourd pour Overpass en low)
            parts.append(f'way["building"]({bbox});')
            # Surfaces artificielles
            parts.append(f'way["man_made"~"pier|bridge|breakwater|embankment|groyne|wastewater_plant"]({bbox});')
            # Parking surfaces
            parts.append(f'way["amenity"="parking"]({bbox});')

    if "infrastructure" in exclude_types:
        # === INFRASTRUCTURES — TOLÉRANCE ZÉRO ===
        parts.append(f'way["railway"]({bbox});')
        parts.append(f'way["aeroway"]({bbox});')
        parts.append(f'way["power"~"plant|substation|line"]({bbox});')
        if detail_level == "high":
            parts.append(f'way["man_made"~"works|storage_tank|water_tower|chimney|tower|mast"]({bbox});')

    parts.append(");out body geom;")
    return "".join(parts)


def _near(p1, p2, threshold=0.0001):
    """Vérifie si deux points sont proches (pour assemblage de ring)."""
    return abs(p1[0] - p2[0]) < threshold and abs(p1[1] - p2[1]) < threshold


def _assemble_rings(members):
    """
    Assemble les segments (ways) des membres d'une relation en anneaux fermés.
    Pour les multipolygones OSM (comme le Fleuve Saint-Laurent), les membres
    "outer" forment la frontière extérieure de la masse d'eau.

    Retourne une liste d'anneaux (listes de coordonnées [lng, lat]).
    """
    # Extraire les geometries des membres outer (ou sans rôle)
    segments = []
    for m in members:
        role = m.get("role", "outer")
        geom = m.get("geometry")
        if not geom or role == "inner":
            continue
        coords = [[pt["lon"], pt["lat"]] for pt in geom]
        if len(coords) >= 2:
            segments.append(coords)

    if not segments:
        return []

    # Essayer d'assembler les segments en anneaux fermés
    rings = []
    remaining = list(segments)

    while remaining:
        ring = list(remaining.pop(0))
        changed = True
        iterations = 0
        max_iterations = len(remaining) * 4

        while changed and iterations < max_iterations:
            changed = False
            iterations += 1
            for i, seg in enumerate(remaining):
                if _near(ring[-1], seg[0]):
                    ring.extend(seg[1:])
                    remaining.pop(i)
                    changed = True
                    break
                elif _near(ring[-1], seg[-1]):
                    ring.extend(list(reversed(seg))[1:])
                    remaining.pop(i)
                    changed = True
                    break
                elif _near(ring[0], seg[-1]):
                    ring = seg[:-1] + ring
                    remaining.pop(i)
                    changed = True
                    break
                elif _near(ring[0], seg[0]):
                    ring = list(reversed(seg))[:-1] + ring
                    remaining.pop(i)
                    changed = True
                    break

        # Fermer le ring si nécessaire
        if len(ring) >= 3 and not _near(ring[0], ring[-1]):
            ring.append(ring[0])

        if len(ring) >= 4:
            rings.append(ring)

    return rings


def _polygon_area_m2(coords):
    """Calcule l'aire d'un polygone [lng, lat] en m²."""
    if len(coords) < 3:
        return 0
    clat = sum(c[1] for c in coords) / len(coords)
    cos_lat = math.cos(math.radians(clat))
    area = 0
    n = len(coords)
    for i in range(n):
        j = (i + 1) % n
        xi = coords[i][0] * 111320 * cos_lat
        yi = coords[i][1] * 111320
        xj = coords[j][0] * 111320 * cos_lat
        yj = coords[j][1] * 111320
        area += xi * yj - xj * yi
    return abs(area) / 2


def _parse_overpass(data: dict, exclude_types: list) -> List[dict]:
    """
    Parse Overpass response — HYDRO FIX FINAL (V1.1 + V2).

    CORRECTIONS HYDRO:
    - natural=wetland → type="wetland" (habitat orignal, NON-eau)
    - Relations assemblées > 10 km² → filtered_out (oversized_relation)
    - sub_type=NONE/unknown → filtered_out (no_subtype_relation)
    - river > 2 km² → filtered_out (oversized_river)
    - micro-plans d'eau < 2000 m² → sub_type="micro_water"
    - waterway=stream polygones → convertis en line
    """
    exclusion_zones = []
    zone_id = 0

    WATER_NATURAL = {"water", "bay", "strait", "coastline"}
    WATER_LANDUSE = {"reservoir", "basin", "salt_pond"}
    # BIONIC V7.3: Agricultural tags REMOVED from urban exclusions.
    # farmland/farmyard/orchard/vineyard/allotments are NOT urban —
    # they are normal rural land uses where wildlife feeds.
    URBAN_LANDUSE = {
        "residential", "commercial", "industrial", "retail",
        "recreation_ground", "cemetery", "construction", "military",
        "quarry", "landfill",
    }

    AREA_10KM2 = 10_000_000
    AREA_2KM2 = 2_000_000
    AREA_MICRO = 2000

    for element in data.get("elements", []):
        tags = element.get("tags", {})

        zone_type = None
        is_wetland = False

        # 1. Wetland — type séparé (NON-eau, habitat orignal)
        if tags.get("natural") == "wetland":
            zone_type = "wetland"
            is_wetland = True
        # 2. Eau (hors wetland)
        elif (
            tags.get("natural") in WATER_NATURAL
            or "waterway" in tags
            or "water" in tags
            or tags.get("landuse") in WATER_LANDUSE
        ):
            zone_type = "water"
        # 3. Routes
        elif "highway" in tags:
            zone_type = "roads"
        # 4. Urbain / Anthropique
        elif (
            tags.get("landuse") in URBAN_LANDUSE
            or "amenity" in tags
            or "leisure" in tags
            or "building" in tags
        ):
            zone_type = "urban"
        # 5. Infrastructure
        elif (
            "railway" in tags
            or "aeroway" in tags
            or "power" in tags
            or "man_made" in tags
        ):
            zone_type = "infrastructure"

        if zone_type is None:
            continue

        # Wetland toujours inclus (reclassifié hors "water"), autres filtrés par exclude_types
        if not is_wetland and zone_type not in exclude_types:
            continue

        if element.get("type") == "way" and "geometry" in element:
            coords = [[pt["lon"], pt["lat"]] for pt in element["geometry"]]
            if len(coords) < 2:
                continue

            is_road = zone_type == "roads"
            geom_type = "line" if is_road or len(coords) < 3 else "polygon"
            sub_type = (
                tags.get("highway") or tags.get("landuse") or tags.get("natural")
                or tags.get("building") or tags.get("railway")
                or tags.get("waterway") or "unknown"
            )

            area_m2 = 0
            filtered_out = False
            reason = "valid"

            if is_wetland:
                area_m2 = _polygon_area_m2(coords) if geom_type == "polygon" else 0
                filtered_out = False
                reason = "wetland"

            elif zone_type == "water" and geom_type == "polygon":
                area_m2 = _polygon_area_m2(coords)
                st_lower = (sub_type or "").lower()

                if st_lower in ("stream", "ditch"):
                    geom_type = "line"
                    reason = "stream_to_line"
                elif st_lower == "river" and area_m2 > AREA_2KM2:
                    filtered_out = True
                    reason = "oversized_river"
                elif st_lower in ("none", "unknown", "") and area_m2 > AREA_10KM2:
                    filtered_out = True
                    reason = "oversized_unknown"
                elif area_m2 > AREA_10KM2:
                    filtered_out = True
                    reason = "oversized_relation"
                elif area_m2 < AREA_MICRO:
                    sub_type = "micro_water"
                    reason = "micro_water"
                else:
                    reason = "valid_water"

            elif zone_type == "water" and geom_type == "line":
                reason = "water_line"

            zone_id += 1
            exclusion_zones.append({
                "id": zone_id,
                "type": zone_type,
                "geometry_type": geom_type,
                "sub_type": sub_type,
                "coordinates": coords,
                "area_m2": round(area_m2, 1),
                "filtered_out": filtered_out,
                "reason": reason,
            })

        elif element.get("type") == "relation" and "members" in element:
            members = element.get("members", [])
            sub_type = (
                tags.get("water") or tags.get("waterway") or tags.get("natural")
                or tags.get("landuse") or tags.get("highway")
                or tags.get("building") or tags.get("railway") or "unknown"
            )

            if zone_type == "water":
                rings = _assemble_rings(members)
                for ring in rings:
                    area_m2 = _polygon_area_m2(ring)
                    st_lower = (sub_type or "none").lower()

                    filtered_out = False
                    reason = "valid_water"

                    if area_m2 > AREA_10KM2:
                        filtered_out = True
                        reason = "oversized_relation"
                    elif st_lower in ("none", "unknown", ""):
                        filtered_out = True
                        reason = "no_subtype_relation"
                    elif st_lower == "river" and area_m2 > AREA_2KM2:
                        filtered_out = True
                        reason = "oversized_river"

                    zone_id += 1
                    exclusion_zones.append({
                        "id": zone_id,
                        "type": zone_type,
                        "geometry_type": "polygon",
                        "sub_type": sub_type,
                        "coordinates": ring,
                        "area_m2": round(area_m2, 1),
                        "filtered_out": filtered_out,
                        "reason": reason,
                    })

                for member in members:
                    geom = member.get("geometry")
                    if not geom:
                        continue
                    coords = [[pt["lon"], pt["lat"]] for pt in geom]
                    if len(coords) >= 2:
                        zone_id += 1
                        exclusion_zones.append({
                            "id": zone_id,
                            "type": zone_type,
                            "geometry_type": "line",
                            "coordinates": coords,
                            "large_water": True,
                            "area_m2": 0,
                            "filtered_out": False,
                            "reason": "shoreline",
                        })

            elif is_wetland:
                rings = _assemble_rings(members)
                for ring in rings:
                    area_m2 = _polygon_area_m2(ring)
                    zone_id += 1
                    exclusion_zones.append({
                        "id": zone_id,
                        "type": "wetland",
                        "geometry_type": "polygon",
                        "sub_type": sub_type,
                        "coordinates": ring,
                        "area_m2": round(area_m2, 1),
                        "filtered_out": False,
                        "reason": "wetland",
                    })

            else:
                for member in members:
                    geom = member.get("geometry")
                    if not geom:
                        continue
                    coords = [[pt["lon"], pt["lat"]] for pt in geom]
                    if len(coords) >= 3:
                        area_m2 = _polygon_area_m2(coords)
                        zone_id += 1
                        exclusion_zones.append({
                            "id": zone_id,
                            "type": zone_type,
                            "geometry_type": "polygon",
                            "sub_type": sub_type,
                            "coordinates": coords,
                            "area_m2": round(area_m2, 1),
                            "filtered_out": False,
                            "reason": "valid",
                        })

    return exclusion_zones


@router.post("/terrain-data")
async def get_terrain_data(request: TerrainDataRequest):
    """
    Proxy Overpass API — Données d'exclusion de terrain.
    TOLÉRANCE ZÉRO — Aucune zone BIONIC ne doit intersecter
    eau, routes, urbain, ou infrastructures.

    Paramètre detail_level:
    - "low": Seulement les grandes entités (landuse, routes majeures, grands plans d'eau)
    - "high": Toutes les entités (bâtiments, routes secondaires, ruisseaux)

    Limite bbox: 0.3° x 0.4° par tuile. Le frontend découpe en tuiles.
    """
    try:
        lat_range = request.north - request.south
        lon_range = request.east - request.west
        if lat_range > 0.3 or lon_range > 0.4:
            raise HTTPException(
                status_code=400,
                detail="Bounding box trop grande. Max 0.3° x 0.4° par tuile."
            )

        bbox = (request.south, request.west, request.north, request.east)
        key = _cache_key(bbox, request.exclude_types, request.detail_level)

        cached = await _load_cache(key)
        if cached:
            logger.info(f"Terrain data from cache: {key}")
            return {
                "success": True,
                "exclusion_zones": cached["exclusion_zones"],
                "stats": cached["stats"],
                "cached": True,
            }

        query = _build_overpass_query(
            request.south, request.west, request.north, request.east,
            request.exclude_types, request.detail_level,
        )

        logger.info(
            f"Querying Overpass API: bbox={bbox}, detail={request.detail_level}"
        )

        # V7.3: Retry with exponential backoff + mirror rotation
        osm_data = None
        last_error = None
        for attempt in range(OVERPASS_MAX_RETRIES):
            mirror_url = OVERPASS_MIRRORS[attempt % len(OVERPASS_MIRRORS)]
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        mirror_url, data={"data": query}
                    )
                if response.status_code == 200:
                    osm_data = response.json()
                    break
                elif response.status_code == 429:
                    wait = OVERPASS_BACKOFF_BASE ** (attempt + 1)
                    logger.warning(
                        f"Overpass {mirror_url} returned 429 (attempt {attempt+1}/{OVERPASS_MAX_RETRIES}). "
                        f"Retrying in {wait}s with next mirror..."
                    )
                    last_error = "429 rate-limited"
                    await asyncio.sleep(wait)
                else:
                    logger.warning(f"Overpass {mirror_url} returned {response.status_code}")
                    last_error = f"HTTP {response.status_code}"
                    await asyncio.sleep(1)
            except Exception as e:
                logger.warning(f"Overpass {mirror_url} error: {e}")
                last_error = str(e)
                await asyncio.sleep(OVERPASS_BACKOFF_BASE)

        # V7.3: All retries failed — try expired cache as last resort
        if osm_data is None:
            logger.warning(
                f"Overpass ALL retries failed ({last_error}). Trying expired cache..."
            )
            expired_data = await _load_cache_expired(key)
            if expired_data:
                logger.info(f"[R5] Using expired cache as fallback for {key}")
                return {
                    "success": True,
                    "exclusion_zones": expired_data.get("exclusion_zones", []),
                    "stats": {**expired_data.get("stats", {}), "cache_expired_fallback": True},
                    "cached": True,
                    "cache_expired": True,
                }
            # No cache at all — fail
            logger.error(f"Overpass failed and no cache available: {last_error}")
            return {
                "success": False,
                "exclusion_zones": [],
                "stats": {"error": f"Overpass failed: {last_error}"},
                "cached": False,
            }

        exclusion_zones = _parse_overpass(osm_data, request.exclude_types)

        # SECTION 4 — HYDRO DEBUG LOG
        hydro_entries = [
            {
                "id": z.get("id"),
                "type": z.get("type"),
                "sub_type": z.get("sub_type"),
                "area_m2": z.get("area_m2", 0),
                "filtered_out": z.get("filtered_out", False),
                "reason": z.get("reason", "unknown"),
            }
            for z in exclusion_zones
            if z.get("type") in ("water", "wetland")
        ]
        if hydro_entries:
            hydro_debug_path = os.path.join(CACHE_DIR, "hydro_debug.json")
            try:
                with open(hydro_debug_path, "w") as f:
                    json.dump(hydro_entries, f, indent=2)
                logger.info(f"HYDRO DEBUG: {len(hydro_entries)} entries written to {hydro_debug_path}")
            except Exception as e:
                logger.warning(f"HYDRO DEBUG write failed: {e}")

        stats = {
            "total_osm_elements": len(osm_data.get("elements", [])),
            "exclusion_zones_count": len(exclusion_zones),
            "by_type": {},
            "detail_level": request.detail_level,
        }
        for zone in exclusion_zones:
            t = zone["type"]
            stats["by_type"][t] = stats["by_type"].get(t, 0) + 1

        cache_data = {"exclusion_zones": exclusion_zones, "stats": stats}
        await _save_cache(key, cache_data)

        logger.info(
            f"Terrain data fetched: {stats['exclusion_zones_count']} exclusion zones "
            f"(detail={request.detail_level})"
        )

        return {
            "success": True,
            "exclusion_zones": exclusion_zones,
            "stats": stats,
            "cached": False,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Terrain data error: {e}")
        raise HTTPException(status_code=500, detail=f"Terrain data error: {str(e)}")


@router.get("/terrain-data/health")
async def terrain_data_health():
    return {
        "status": "operational",
        "cache_dir": CACHE_DIR,
        "overpass_url": OVERPASS_API_URL,
        "supported_types": ["water", "roads", "urban", "infrastructure"],
        "detail_levels": ["low", "high"],
    }
