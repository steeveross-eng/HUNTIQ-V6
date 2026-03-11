"""
# ══════════════════════════════════════════════════════════════
# LEGACY FIGÉ — NE PAS MODIFIER, NE PAS RÉACTIVER, NE PAS MIGRER
# Raison: Remplacé par bionic_engine_p0/ (pipeline V7 canonique)
# Date gel: 2026-03-10
# BCE: Ce fichier est exclu du pipeline de conformité
# ══════════════════════════════════════════════════════════════
Hydrography Service - Détection des surfaces d'eau pour BIONIC™

Ce module permet de:
1. Détecter les surfaces d'eau (fleuves, lacs, rivières, océans, étangs, marais, réservoirs)
2. Vérifier si un point est situé dans l'eau
3. Calculer la distance au rivage le plus proche
4. Appliquer une exclusion avec tolérance de distance

Sources de données officielles (par priorité):
- Québec: Hydrographie MRNF/MSP (WFS)
- Canada: Ressources naturelles Canada - CanVec Hydrography (WFS)
- USA: USGS National Hydrography Dataset NHD/NHDPlus HR (REST)
- Fallback global: OpenStreetMap (natural=water, waterway=*)

Auteur: BIONIC™ Team
"""

import math
import logging
import asyncio
import httpx
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

# ============================================
# CONFIGURATION
# ============================================

# Tolérance de distance du rivage (mètres)
SHORE_TOLERANCE_METERS = 5

# Cache des données hydrographiques (durée en secondes)
HYDRO_CACHE_DURATION = 3600  # 1 heure

# Rayon de recherche pour les données hydrographiques (mètres)
HYDRO_SEARCH_RADIUS = 5000  # 5 km

# Timeout pour les requêtes API (secondes)
API_TIMEOUT = 15

# ============================================
# SOURCES HYDROGRAPHIQUES OFFICIELLES
# ============================================

class HydroSource(Enum):
    """Sources de données hydrographiques par région"""
    QUEBEC_MRNF = "quebec_mrnf"
    CANADA_CANVEC = "canada_canvec"
    USA_NHD = "usa_nhd"
    OSM_FALLBACK = "osm_fallback"

# Configuration des services WFS/REST par source
HYDRO_SERVICES = {
    HydroSource.QUEBEC_MRNF: {
        "name": "Québec - MRNF/MSP Hydrographie",
        "type": "wfs",
        "url": "https://servicescarto.mern.gouv.qc.ca/pes/services/Territoire/SDA_WMS/MapServer/WFSServer",
        "layers": ["hydrographie_surfacique", "hydrographie_lineaire"],
        "srs": "EPSG:4326",
        "bounds": {"north": 62.0, "south": 45.0, "east": -57.0, "west": -79.5},
        "priority": 1
    },
    HydroSource.CANADA_CANVEC: {
        "name": "Canada - CanVec Hydrography (NRCan)",
        "type": "wfs",
        "url": "https://geo.api.gov.bc.ca/geo/pub/WHSE_BASEMAPPING.NTS_BC_WATER_AREAS_50K/wfs",
        "alt_url": "https://maps.geogratis.gc.ca/wms/canvec_en",
        "layers": ["waterbody", "watercourse"],
        "srs": "EPSG:4326",
        "bounds": {"north": 83.0, "south": 42.0, "east": -52.0, "west": -141.0},
        "priority": 2
    },
    HydroSource.USA_NHD: {
        "name": "USA - USGS National Hydrography Dataset",
        "type": "arcgis_rest",
        "url": "https://hydro.nationalmap.gov/arcgis/rest/services/nhd/MapServer",
        "layers": [2, 3, 6],  # Lakes, Streams, Areas
        "srs": "EPSG:4326",
        "bounds": {"north": 49.5, "south": 24.5, "east": -66.0, "west": -125.0},
        "priority": 3
    },
    HydroSource.OSM_FALLBACK: {
        "name": "OpenStreetMap - Global Fallback",
        "type": "overpass",
        "url": "https://overpass-api.de/api/interpreter",
        "layers": ["natural=water", "waterway=*"],
        "srs": "EPSG:4326",
        "bounds": {"north": 90.0, "south": -90.0, "east": 180.0, "west": -180.0},
        "priority": 99
    }
}

# Types de surfaces d'eau à exclure
WATER_TYPES = {
    'water',           # Générique
    'lake',            # Lac
    'river',           # Rivière
    'stream',          # Ruisseau
    'pond',            # Étang
    'reservoir',       # Réservoir
    'canal',           # Canal
    'wetland',         # Zone humide
    'marsh',           # Marais
    'swamp',           # Marécage
    'bay',             # Baie
    'strait',          # Détroit
    'fjord',           # Fjord
    'ocean',           # Océan
    'sea',             # Mer
    'lagoon',          # Lagune
    'estuary',         # Estuaire
    'basin',           # Bassin
    'waterway',        # Voie navigable
}

# Tags OSM pour les surfaces d'eau
OSM_WATER_TAGS = [
    'natural=water',
    'natural=wetland',
    'water=lake',
    'water=river',
    'water=pond',
    'water=reservoir',
    'water=canal',
    'water=stream',
    'water=marsh',
    'water=swamp',
    'water=lagoon',
    'water=bay',
    'waterway=river',
    'waterway=stream',
    'waterway=canal',
    'landuse=reservoir',
    'landuse=basin',
]

# ============================================
# CACHE EN MÉMOIRE
# ============================================

class HydrographyCache:
    """Cache en mémoire pour les données hydrographiques"""
    
    def __init__(self):
        self._cache: Dict[str, dict] = {}
        self._timestamps: Dict[str, datetime] = {}
    
    def _get_cache_key(self, lat: float, lng: float, radius: float) -> str:
        """Génère une clé de cache basée sur la position (arrondie)"""
        # Arrondir pour regrouper les requêtes proches
        lat_key = round(lat, 2)
        lng_key = round(lng, 2)
        return f"{lat_key}_{lng_key}_{radius}"
    
    def get(self, lat: float, lng: float, radius: float) -> Optional[dict]:
        """Récupère les données du cache si disponibles et non expirées"""
        key = self._get_cache_key(lat, lng, radius)
        if key in self._cache:
            timestamp = self._timestamps.get(key)
            if timestamp and (datetime.now() - timestamp).total_seconds() < HYDRO_CACHE_DURATION:
                return self._cache[key]
            else:
                # Cache expiré
                del self._cache[key]
                del self._timestamps[key]
        return None
    
    def set(self, lat: float, lng: float, radius: float, data: dict):
        """Stocke les données dans le cache"""
        key = self._get_cache_key(lat, lng, radius)
        self._cache[key] = data
        self._timestamps[key] = datetime.now()
    
    def clear(self):
        """Vide le cache"""
        self._cache.clear()
        self._timestamps.clear()

# Instance globale du cache
_hydro_cache = HydrographyCache()

# ============================================
# FONCTIONS GÉOMÉTRIQUES
# ============================================

def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calcule la distance en mètres entre deux points GPS (formule de Haversine)
    """
    R = 6371000  # Rayon de la Terre en mètres
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lng2 - lng1)
    
    a = math.sin(delta_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def point_in_polygon(point: Tuple[float, float], polygon: List[Tuple[float, float]]) -> bool:
    """
    Vérifie si un point est à l'intérieur d'un polygone (algorithme ray-casting)
    
    Args:
        point: (lat, lng)
        polygon: Liste de (lat, lng) définissant le polygone
    """
    x, y = point
    n = len(polygon)
    inside = False
    
    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    
    return inside

def distance_to_polygon_edge(point: Tuple[float, float], polygon: List[Tuple[float, float]]) -> float:
    """
    Calcule la distance minimale entre un point et le bord d'un polygone (en mètres)
    """
    min_distance = float('inf')
    lat, lng = point
    
    for i in range(len(polygon)):
        p1 = polygon[i]
        p2 = polygon[(i + 1) % len(polygon)]
        
        # Distance au segment
        dist = distance_point_to_segment(lat, lng, p1[0], p1[1], p2[0], p2[1])
        min_distance = min(min_distance, dist)
    
    return min_distance

def distance_point_to_segment(px: float, py: float, 
                               x1: float, y1: float, 
                               x2: float, y2: float) -> float:
    """
    Calcule la distance d'un point à un segment de ligne
    """
    # Vecteur du segment
    dx = x2 - x1
    dy = y2 - y1
    
    if dx == 0 and dy == 0:
        # Le segment est un point
        return haversine_distance(px, py, x1, y1)
    
    # Paramètre t de la projection du point sur la ligne
    t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
    
    # Point le plus proche sur le segment
    closest_x = x1 + t * dx
    closest_y = y1 + t * dy
    
    return haversine_distance(px, py, closest_x, closest_y)

# ============================================
# DÉTECTION DE LA RÉGION GÉOGRAPHIQUE
# ============================================

def detect_region(lat: float, lng: float) -> List[HydroSource]:
    """
    Détecte la région géographique et retourne les sources appropriées triées par priorité
    
    Note: USA NHD est exclu pour les positions clairement canadiennes:
    - Latitude > 49° (nord de la frontière)
    - Est de -67° (Maritimes, Québec est)
    - Ouest de -125° (Colombie-Britannique nord)
    - Québec/Ontario au nord du 45e parallèle
    """
    sources = []
    
    for source, config in HYDRO_SERVICES.items():
        bounds = config["bounds"]
        
        # Vérification spéciale pour USA NHD: exclure si clairement au Canada
        if source == HydroSource.USA_NHD:
            # Exclure si au nord de la frontière (49e parallèle)
            if lat > 49.0:
                continue
            # Exclure si dans l'est du Canada (Maritimes - est de -67°)
            if lng > -67.0:
                continue
            # Exclure si au Québec/Ontario au nord du 45e parallèle
            # Couvre: Québec City, Rimouski, Gaspésie, Saguenay, etc.
            if lat > 45.0 and lng >= -80.0:
                # Toute position au nord du 45e parallèle et à l'est de -80° est au Canada
                continue
            
        if (bounds["south"] <= lat <= bounds["north"] and 
            bounds["west"] <= lng <= bounds["east"]):
            sources.append((source, config["priority"]))
    
    # Trier par priorité et retourner les sources
    sources.sort(key=lambda x: x[1])
    return [s[0] for s in sources]

# ============================================
# RÉCUPÉRATION DES DONNÉES - SOURCES OFFICIELLES
# ============================================

async def fetch_water_features_quebec(lat: float, lng: float, radius_meters: float) -> Dict:
    """
    Récupère les surfaces d'eau depuis le service WFS du Québec (MRNF/MSP)
    """
    config = HYDRO_SERVICES[HydroSource.QUEBEC_MRNF]
    
    # Calculer la bounding box
    lat_delta = radius_meters / 111320
    lng_delta = radius_meters / (111320 * math.cos(math.radians(lat)))
    bbox = f"{lng - lng_delta},{lat - lat_delta},{lng + lng_delta},{lat + lat_delta}"
    
    # Requête WFS GetFeature
    params = {
        "service": "WFS",
        "version": "2.0.0",
        "request": "GetFeature",
        "typeName": "hydrographie_surfacique",
        "outputFormat": "application/json",
        "srsName": "EPSG:4326",
        "bbox": bbox
    }
    
    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(config["url"], params=params)
            if response.status_code == 200:
                data = response.json()
                features = parse_geojson_features(data, "quebec_mrnf")
                logger.info(f"Quebec MRNF: {len(features)} water features found")
                return {"features": features, "source": "quebec_mrnf", "success": True}
    except Exception as e:
        logger.warning(f"Quebec MRNF service error: {e}")
    
    return {"features": [], "source": "quebec_mrnf", "success": False, "error": str(e) if 'e' in dir() else "Unknown error"}

async def fetch_water_features_canada(lat: float, lng: float, radius_meters: float) -> Dict:
    """
    Récupère les surfaces d'eau depuis CanVec Hydrography (Ressources naturelles Canada)
    """
    config = HYDRO_SERVICES[HydroSource.CANADA_CANVEC]
    
    # Calculer la bounding box
    lat_delta = radius_meters / 111320
    lng_delta = radius_meters / (111320 * math.cos(math.radians(lat)))
    bbox = f"{lng - lng_delta},{lat - lat_delta},{lng + lng_delta},{lat + lat_delta}"
    
    # Essayer le service principal
    params = {
        "service": "WFS",
        "version": "2.0.0", 
        "request": "GetFeature",
        "typeName": "waterbody",
        "outputFormat": "application/json",
        "srsName": "EPSG:4326",
        "bbox": bbox
    }
    
    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(config["url"], params=params)
            if response.status_code == 200:
                data = response.json()
                features = parse_geojson_features(data, "canada_canvec")
                logger.info(f"Canada CanVec: {len(features)} water features found")
                return {"features": features, "source": "canada_canvec", "success": True}
    except Exception as e:
        logger.warning(f"Canada CanVec service error: {e}")
    
    return {"features": [], "source": "canada_canvec", "success": False}

async def fetch_water_features_usa(lat: float, lng: float, radius_meters: float) -> Dict:
    """
    Récupère les surfaces d'eau depuis USGS National Hydrography Dataset (NHD)
    Note: Ce service ne couvre que les États-Unis (latitude < 49°)
    """
    # Vérifier si la position est dans la zone de couverture USA
    if lat > 49.0:
        logger.debug(f"USA NHD: Position ({lat}, {lng}) is outside US coverage")
        return {"features": [], "source": "usa_nhd", "success": False, "error": "Outside US coverage"}
    
    config = HYDRO_SERVICES[HydroSource.USA_NHD]
    
    # Calculer la bounding box pour ArcGIS REST
    lat_delta = radius_meters / 111320
    lng_delta = radius_meters / (111320 * math.cos(math.radians(lat)))
    
    # Format ArcGIS: xmin,ymin,xmax,ymax
    geometry = f"{lng - lng_delta},{lat - lat_delta},{lng + lng_delta},{lat + lat_delta}"
    
    all_features = []
    
    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            for layer_id in config["layers"]:
                query_url = f"{config['url']}/{layer_id}/query"
                params = {
                    "geometry": geometry,
                    "geometryType": "esriGeometryEnvelope",
                    "inSR": "4326",
                    "outSR": "4326",
                    "spatialRel": "esriSpatialRelIntersects",
                    "outFields": "GNIS_NAME,FTYPE,FCODE",
                    "returnGeometry": "true",
                    "f": "geojson"
                }
                
                response = await client.get(query_url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    features = parse_geojson_features(data, "usa_nhd")
                    all_features.extend(features)
        
        logger.info(f"USA NHD: {len(all_features)} water features found")
        return {"features": all_features, "source": "usa_nhd", "success": True}
        
    except Exception as e:
        logger.warning(f"USA NHD service error: {e}")
    
    return {"features": [], "source": "usa_nhd", "success": False}

async def fetch_water_features_osm(lat: float, lng: float, radius_meters: float = HYDRO_SEARCH_RADIUS) -> Dict:
    """
    Récupère les surfaces d'eau depuis OpenStreetMap Overpass API (Fallback global)
    
    Args:
        lat: Latitude du centre
        lng: Longitude du centre
        radius_meters: Rayon de recherche en mètres
    
    Returns:
        Dict contenant les polygones d'eau
    """
    overpass_url = "https://overpass-api.de/api/interpreter"
    
    # Requête optimisée pour récupérer les surfaces d'eau
    # Utilise une bbox pour plus de performance
    lat_delta = radius_meters / 111320
    lng_delta = radius_meters / (111320 * math.cos(math.radians(lat)))
    bbox = f"{lat - lat_delta},{lng - lng_delta},{lat + lat_delta},{lng + lng_delta}"
    
    query = f"""
    [out:json][timeout:45][bbox:{bbox}];
    (
      // Surfaces d'eau principales
      way["natural"="water"];
      relation["natural"="water"];
      
      // Berges de rivières (grandes rivières comme le Saint-Laurent)
      way["waterway"="riverbank"];
      relation["waterway"="riverbank"];
      
      // Cours d'eau avec area
      way["waterway"]["area"="yes"];
      
      // Zones humides
      way["natural"="wetland"];
      
      // Réservoirs
      way["landuse"="reservoir"];
      way["landuse"="basin"];
    );
    out body;
    >;
    out skel qt;
    """
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(overpass_url, data={"data": query})
            response.raise_for_status()
            data = response.json()
        
        # Parser les résultats
        water_features = parse_osm_water_features(data)
        
        logger.info(f"OSM Fallback: {len(water_features)} water features found for ({lat}, {lng})")
        return {"features": water_features, "source": "osm_fallback", "success": True}
        
    except Exception as e:
        logger.error(f"OSM Overpass error: {e}")
        return {"features": [], "source": "osm_fallback", "success": False, "error": str(e)}

async def fetch_water_features_osm_with_retry(lat: float, lng: float, radius_meters: float = HYDRO_SEARCH_RADIUS, max_retries: int = 2) -> Dict:
    """
    Récupère les surfaces d'eau depuis OSM avec retry en cas d'échec
    """
    last_error = None
    
    for attempt in range(max_retries + 1):
        result = await fetch_water_features_osm(lat, lng, radius_meters)
        
        if result.get("success") and result.get("features"):
            return result
        
        last_error = result.get("error", "Unknown error")
        
        if attempt < max_retries:
            # Attendre avant de réessayer (backoff exponentiel)
            wait_time = (attempt + 1) * 2
            logger.info(f"OSM retry {attempt + 1}/{max_retries} after {wait_time}s...")
            await asyncio.sleep(wait_time)
    
    return {"features": [], "source": "osm_fallback", "success": False, "error": last_error}

# ============================================
# FONCTION PRINCIPALE - MULTI-SOURCE
# ============================================

async def fetch_water_features_multi_source(lat: float, lng: float, radius_meters: float = HYDRO_SEARCH_RADIUS) -> Dict:
    """
    Récupère les surfaces d'eau depuis les sources officielles appropriées à la région.
    Utilise un système de fallback: sources officielles → OSM global
    
    Args:
        lat: Latitude du centre
        lng: Longitude du centre
        radius_meters: Rayon de recherche en mètres
    
    Returns:
        Dict contenant les polygones d'eau de toutes les sources disponibles
    """
    # Vérifier le cache
    cached = _hydro_cache.get(lat, lng, radius_meters)
    if cached:
        logger.debug(f"Hydro data from cache for ({lat}, {lng})")
        return cached
    
    # Détecter les sources appropriées pour cette position
    sources = detect_region(lat, lng)
    logger.info(f"Detected hydro sources for ({lat:.4f}, {lng:.4f}): {[s.value for s in sources]}")
    
    all_features = []
    sources_used = []
    errors = []
    osm_tried = False
    
    # Mapper les sources aux fonctions de fetch
    fetch_functions = {
        HydroSource.QUEBEC_MRNF: fetch_water_features_quebec,
        HydroSource.CANADA_CANVEC: fetch_water_features_canada,
        HydroSource.USA_NHD: fetch_water_features_usa,
        HydroSource.OSM_FALLBACK: fetch_water_features_osm_with_retry  # Avec retry
    }
    
    # Essayer chaque source dans l'ordre de priorité
    for source in sources:
        if source == HydroSource.OSM_FALLBACK:
            osm_tried = True
            # OSM en dernier recours - skip si on a déjà des données
            if len(all_features) > 0:
                continue
            
        fetch_func = fetch_functions.get(source)
        if fetch_func:
            try:
                result = await fetch_func(lat, lng, radius_meters)
                if result.get("success") and result.get("features"):
                    all_features.extend(result["features"])
                    sources_used.append(result.get("source", source.value))
                    logger.info(f"Source {source.value}: {len(result.get('features', []))} features")
                elif not result.get("success"):
                    errors.append(f"{source.value}: {result.get('error', 'Unknown error')}")
            except Exception as e:
                errors.append(f"{source.value}: {str(e)}")
                logger.warning(f"Source {source.value} failed: {e}")
    
    # Si aucune donnée trouvée et OSM non encore essayé, forcer OSM avec retry
    if len(all_features) == 0 and not osm_tried:
        logger.info("No official data found, forcing OSM fallback with retry")
        try:
            result = await fetch_water_features_osm_with_retry(lat, lng, radius_meters)
            if result.get("success") and result.get("features"):
                all_features.extend(result["features"])
                sources_used.append("osm_fallback")
        except Exception as e:
            errors.append(f"osm_fallback_forced: {str(e)}")
    
    # Dédupliquer les features par position approximative
    unique_features = deduplicate_features(all_features)
    
    # Construire le résultat
    result = {
        "features": unique_features,
        "center": {"lat": lat, "lng": lng},
        "radius": radius_meters,
        "timestamp": datetime.now().isoformat(),
        "sources_used": sources_used,
        "sources_available": [s.value for s in sources],
        "feature_count": len(unique_features),
        "errors": errors if errors else None
    }
    
    # Stocker dans le cache
    _hydro_cache.set(lat, lng, radius_meters, result)
    
    logger.info(f"Multi-source hydro fetch complete: {len(unique_features)} features from {sources_used}")
    return result

def deduplicate_features(features: List[Dict], precision: int = 4) -> List[Dict]:
    """
    Déduplique les features par position approximative du centroïde
    """
    seen = set()
    unique = []
    
    for feature in features:
        polygon = feature.get("polygon", [])
        if not polygon:
            continue
        
        # Calculer le centroïde approximatif
        avg_lat = sum(p[0] for p in polygon) / len(polygon)
        avg_lng = sum(p[1] for p in polygon) / len(polygon)
        
        # Clé de déduplication
        key = (round(avg_lat, precision), round(avg_lng, precision))
        
        if key not in seen:
            seen.add(key)
            unique.append(feature)
    
    return unique

def parse_geojson_features(geojson_data: dict, source: str) -> List[Dict]:
    """
    Parse les features GeoJSON (format standard WFS/ArcGIS REST)
    """
    features = []
    
    for feature in geojson_data.get("features", []):
        geometry = feature.get("geometry", {})
        properties = feature.get("properties", {})
        
        # Extraire les coordonnées selon le type de géométrie
        coords = []
        geom_type = geometry.get("type", "")
        
        if geom_type == "Polygon":
            coords = geometry.get("coordinates", [[]])[0]
        elif geom_type == "MultiPolygon":
            # Prendre le premier polygone
            multi_coords = geometry.get("coordinates", [[[]]])
            if multi_coords and multi_coords[0]:
                coords = multi_coords[0][0]
        elif geom_type in ["LineString", "MultiLineString"]:
            # Pour les cours d'eau linéaires, créer un buffer simplifié
            line_coords = geometry.get("coordinates", [])
            if geom_type == "MultiLineString" and line_coords:
                line_coords = line_coords[0]
            coords = create_line_buffer(line_coords, buffer_meters=10)
        
        if len(coords) >= 3:
            # Convertir [lng, lat] → [lat, lng] pour notre format
            polygon = [[c[1], c[0]] for c in coords if len(c) >= 2]
            
            # Déterminer le type d'eau
            water_type = properties.get("FTYPE", properties.get("type", properties.get("GNIS_NAME", "water")))
            if isinstance(water_type, int):
                water_type = NHD_FTYPE_MAP.get(water_type, "water")
            
            features.append({
                "id": f"{source}_{feature.get('id', len(features))}",
                "type": str(water_type).lower(),
                "name": properties.get("GNIS_NAME", properties.get("name", "")),
                "polygon": polygon,
                "source": source,
                "tags": properties
            })
    
    return features

def create_line_buffer(line_coords: List, buffer_meters: float = 10) -> List:
    """
    Crée un buffer polygonal autour d'une ligne (pour les cours d'eau linéaires)
    """
    if len(line_coords) < 2:
        return []
    
    # Buffer simplifié: créer un rectangle autour de chaque segment
    buffer_deg = buffer_meters / 111320  # Conversion approximative
    
    left_side = []
    right_side = []
    
    for i, coord in enumerate(line_coords):
        if len(coord) < 2:
            continue
        lng, lat = coord[0], coord[1]
        
        # Offset perpendiculaire simplifié
        left_side.append([lng - buffer_deg, lat + buffer_deg])
        right_side.append([lng + buffer_deg, lat - buffer_deg])
    
    # Combiner en polygone fermé
    return left_side + list(reversed(right_side)) + [left_side[0]] if left_side else []

# Mapping des codes FTYPE NHD vers types lisibles
NHD_FTYPE_MAP = {
    390: "lake",
    460: "stream",
    336: "canal",
    378: "pond",
    436: "reservoir",
    466: "swamp",
    493: "estuary",
    537: "wetland",
}

def parse_osm_water_features(osm_data: dict) -> List[Dict]:
    """
    Parse les données OSM et extrait les polygones d'eau
    Gère les ways ET les relations (multipolygones pour les grands cours d'eau)
    """
    features = []
    nodes = {}
    ways = {}
    
    # Indexer les nodes
    for element in osm_data.get("elements", []):
        if element["type"] == "node":
            nodes[element["id"]] = (element["lat"], element["lon"])
    
    # Indexer les ways pour les relations
    for element in osm_data.get("elements", []):
        if element["type"] == "way":
            if "nodes" in element:
                way_coords = []
                for node_id in element["nodes"]:
                    if node_id in nodes:
                        way_coords.append(nodes[node_id])
                ways[element["id"]] = way_coords
    
    # Extraire les ways (polygones simples)
    for element in osm_data.get("elements", []):
        if element["type"] == "way":
            tags = element.get("tags", {})
            
            # Vérifier si c'est une surface d'eau
            is_water = False
            water_type = "unknown"
            
            if tags.get("natural") == "water":
                is_water = True
                water_type = tags.get("water", "lake")
            elif tags.get("natural") == "wetland":
                is_water = True
                water_type = tags.get("wetland", "marsh")
            elif tags.get("natural") == "bay":
                is_water = True
                water_type = "bay"
            elif tags.get("waterway") in ["riverbank", "river", "stream", "canal"]:
                is_water = True
                water_type = tags.get("waterway", "river")
            elif tags.get("waterway") and tags.get("area") == "yes":
                is_water = True
                water_type = tags.get("waterway", "river")
            elif tags.get("landuse") in ["reservoir", "basin"]:
                is_water = True
                water_type = tags.get("landuse")
            
            if is_water and "nodes" in element:
                # Construire le polygone
                polygon = []
                for node_id in element["nodes"]:
                    if node_id in nodes:
                        polygon.append(nodes[node_id])
                
                if len(polygon) >= 3:
                    features.append({
                        "id": f"way_{element['id']}",
                        "type": water_type,
                        "name": tags.get("name", ""),
                        "polygon": polygon,
                        "source": "osm_way",
                        "tags": tags
                    })
    
    # Extraire les relations (multipolygones - grands cours d'eau)
    for element in osm_data.get("elements", []):
        if element["type"] == "relation":
            tags = element.get("tags", {})
            
            # Vérifier si c'est une surface d'eau
            is_water = False
            water_type = "unknown"
            
            if tags.get("natural") == "water":
                is_water = True
                water_type = tags.get("water", "river")
            elif tags.get("water"):
                is_water = True
                water_type = tags.get("water", "river")
            elif tags.get("waterway") == "riverbank":
                is_water = True
                water_type = "river"
            elif tags.get("type") == "multipolygon" and (
                tags.get("natural") == "water" or 
                tags.get("water") or 
                tags.get("waterway")
            ):
                is_water = True
                water_type = tags.get("water", tags.get("waterway", "river"))
            
            if is_water:
                # Extraire les outer ways de la relation
                for member in element.get("members", []):
                    if member.get("role") == "outer" and member.get("type") == "way":
                        way_id = member.get("ref")
                        if way_id in ways:
                            polygon = ways[way_id]
                            if len(polygon) >= 3:
                                features.append({
                                    "id": f"rel_{element['id']}_{way_id}",
                                    "type": water_type,
                                    "name": tags.get("name", ""),
                                    "polygon": polygon,
                                    "source": "osm_relation",
                                    "tags": tags
                                })
    
    logger.info(f"Parsed {len(features)} water features from OSM data")
    return features

# ============================================
# VÉRIFICATION ET EXCLUSION
# ============================================

def is_point_in_water(lat: float, lng: float, water_features: List[Dict], 
                      tolerance_meters: float = SHORE_TOLERANCE_METERS) -> Tuple[bool, Optional[Dict]]:
    """
    Vérifie si un point est situé dans l'eau ou trop proche du rivage
    
    Méthodes de détection:
    1. Point à l'intérieur d'un polygone d'eau fermé (lac, étang)
    2. Point à moins de X mètres d'une berge (tolérance)
    3. Point entre deux berges de rivière (détection grands fleuves)
    
    Args:
        lat: Latitude du point
        lng: Longitude du point
        water_features: Liste des surfaces d'eau
        tolerance_meters: Distance minimale du rivage (défaut: 5m)
    
    Returns:
        (is_in_water, water_feature) - True si le point est dans l'eau ou trop proche
    """
    point = (lat, lng)
    
    # Première passe: vérification directe polygone + tolérance
    for feature in water_features:
        polygon = feature.get("polygon", [])
        if len(polygon) < 3:
            continue
        
        # Vérifier si le point est à l'intérieur du polygone
        if point_in_polygon(point, polygon):
            return True, feature
        
        # Vérifier la distance au bord (tolérance)
        if tolerance_meters > 0:
            distance = distance_to_polygon_edge(point, polygon)
            if distance <= tolerance_meters:
                return True, feature
    
    # Deuxième passe: détection pour les grands cours d'eau (fleuves, grandes rivières)
    # Les grandes rivières dans OSM sont souvent représentées par des relations avec
    # des ways "outer" qui forment les berges. Un point est dans l'eau si il est
    # entre les berges d'un même cours d'eau.
    
    # Grouper les features par nom de cours d'eau
    water_bodies = {}
    for feature in water_features:
        name = feature.get("name", "")
        if name and feature.get("type") in ["river", "water"]:
            if name not in water_bodies:
                water_bodies[name] = []
            water_bodies[name].append(feature)
    
    # Pour chaque cours d'eau avec plusieurs segments
    for water_name, segments in water_bodies.items():
        if len(segments) < 2:
            continue
        
        # Vérifier si le point est dans la bounding box de l'ensemble des segments
        all_lats = []
        all_lngs = []
        for seg in segments:
            polygon = seg.get("polygon", [])
            for p in polygon:
                all_lats.append(p[0])
                all_lngs.append(p[1])
        
        if not all_lats:
            continue
        
        # Vérifier si le point est dans la bbox globale
        if not (min(all_lats) <= lat <= max(all_lats) and min(all_lngs) <= lng <= max(all_lngs)):
            continue
        
        # Calculer les distances aux différents segments
        distances_to_segments = []
        for seg in segments:
            polygon = seg.get("polygon", [])
            if len(polygon) >= 2:
                min_dist = float('inf')
                for p in polygon:
                    d = haversine_distance(lat, lng, p[0], p[1])
                    min_dist = min(min_dist, d)
                distances_to_segments.append((min_dist, seg))
        
        if len(distances_to_segments) >= 2:
            # Trier par distance
            distances_to_segments.sort(key=lambda x: x[0])
            
            # Si le point est proche de 2 segments différents (< 500m chacun)
            # et que la somme des distances est < 1000m (largeur typique d'un fleuve)
            # alors le point est probablement dans l'eau
            d1, seg1 = distances_to_segments[0]
            d2, seg2 = distances_to_segments[1]
            
            # Critères: proche de 2 berges, largeur totale raisonnable
            if d1 < 500 and d2 < 500 and (d1 + d2) < 1000:
                # Vérifier que ce ne sont pas les mêmes segments (même polygone)
                if seg1.get("id") != seg2.get("id"):
                    return True, {"type": "river", "name": water_name, "source": "between_banks"}
    
    return False, None

def check_surrounded_by_water(lat: float, lng: float, river_features: List[Dict]) -> Optional[Dict]:
    """
    Vérifie si un point est entouré par des berges de rivière
    Retourne les distances minimales dans chaque direction cardinale
    """
    distances = {
        "min_north": float('inf'),
        "min_south": float('inf'),
        "min_east": float('inf'),
        "min_west": float('inf'),
        "closest_feature": None,
        "closest_distance": float('inf')
    }
    
    for feature in river_features:
        polygon = feature.get("polygon", [])
        if len(polygon) < 2:
            continue
        
        for p in polygon:
            plat, plng = p[0], p[1]
            dist = haversine_distance(lat, lng, plat, plng)
            
            # Déterminer la direction du point du polygone par rapport au point test
            dlat = plat - lat
            dlng = plng - lng
            
            # Nord (dlat > 0)
            if dlat > abs(dlng) * 0.5:  # Principalement au nord
                if dist < distances["min_north"]:
                    distances["min_north"] = dist
                    
            # Sud (dlat < 0)
            if dlat < -abs(dlng) * 0.5:
                if dist < distances["min_south"]:
                    distances["min_south"] = dist
                    
            # Est (dlng > 0)
            if dlng > abs(dlat) * 0.5:
                if dist < distances["min_east"]:
                    distances["min_east"] = dist
                    
            # Ouest (dlng < 0)
            if dlng < -abs(dlat) * 0.5:
                if dist < distances["min_west"]:
                    distances["min_west"] = dist
            
            # Garder trace du feature le plus proche
            if dist < distances["closest_distance"]:
                distances["closest_distance"] = dist
                distances["closest_feature"] = feature
    
    # Retourner seulement si on a trouvé des berges dans au moins 2 directions opposées
    has_north_south = distances["min_north"] < float('inf') and distances["min_south"] < float('inf')
    has_east_west = distances["min_east"] < float('inf') and distances["min_west"] < float('inf')
    
    if has_north_south or has_east_west:
        return distances
    
    return None

async def filter_zones_exclude_water(
    zones: List[Dict],
    bounds: Dict,
    tolerance_meters: float = SHORE_TOLERANCE_METERS
) -> Tuple[List[Dict], Dict]:
    """
    Filtre les zones BIONIC pour exclure celles situées dans l'eau
    
    Utilise les sources hydrographiques officielles:
    - Québec: MRNF/MSP
    - Canada: CanVec (NRCan)
    - USA: USGS NHD
    - Fallback: OpenStreetMap
    
    Args:
        zones: Liste des zones à filtrer
        bounds: Limites de la carte {north, south, east, west}
        tolerance_meters: Distance minimale du rivage
    
    Returns:
        (filtered_zones, stats) - Zones filtrées et statistiques
    """
    if not zones:
        return [], {"total": 0, "filtered": 0, "excluded": 0}
    
    # Calculer le centre et le rayon de recherche
    center_lat = (bounds.get("north", 0) + bounds.get("south", 0)) / 2
    center_lng = (bounds.get("east", 0) + bounds.get("west", 0)) / 2
    
    # Calculer le rayon basé sur les limites
    lat_dist = haversine_distance(bounds.get("north", 0), center_lng, 
                                   bounds.get("south", 0), center_lng)
    lng_dist = haversine_distance(center_lat, bounds.get("east", 0), 
                                   center_lat, bounds.get("west", 0))
    search_radius = max(lat_dist, lng_dist) / 2 + 1000  # +1km de marge
    
    # Récupérer les données hydrographiques depuis les sources officielles
    hydro_data = await fetch_water_features_multi_source(center_lat, center_lng, search_radius)
    water_features = hydro_data.get("features", [])
    sources_used = hydro_data.get("sources_used", [])
    
    logger.info(f"Water exclusion using sources: {sources_used}, {len(water_features)} features found")
    
    # Filtrer les zones
    filtered_zones = []
    excluded_zones = []
    
    for zone in zones:
        center = zone.get("center", [0, 0])
        lat, lng = center[0], center[1]
        
        is_water, water_info = is_point_in_water(lat, lng, water_features, tolerance_meters)
        
        if not is_water:
            filtered_zones.append(zone)
        else:
            excluded_zones.append({
                "zone_id": zone.get("id"),
                "reason": "in_water",
                "water_type": water_info.get("type") if water_info else "unknown",
                "water_name": water_info.get("name") if water_info else "",
                "water_source": water_info.get("source") if water_info else "unknown"
            })
    
    stats = {
        "total": len(zones),
        "filtered": len(filtered_zones),
        "excluded": len(excluded_zones),
        "water_features_count": len(water_features),
        "tolerance_meters": tolerance_meters,
        "sources_used": sources_used,
        "excluded_details": excluded_zones[:10]  # Limiter les détails
    }
    
    logger.info(f"Zone filtering: {stats['filtered']}/{stats['total']} zones kept, {stats['excluded']} excluded")
    
    return filtered_zones, stats

def adjust_zone_contour_for_water(
    zone: Dict,
    water_features: List[Dict],
    tolerance_meters: float = SHORE_TOLERANCE_METERS
) -> Dict:
    """
    Ajuste le contour d'une zone pour éviter les intrusions dans l'eau
    
    Cette fonction modifie le rayon de la zone si elle est trop proche de l'eau
    """
    center = zone.get("center", [0, 0])
    radius = zone.get("radiusMeters", 100)
    lat, lng = center[0], center[1]
    
    # Trouver la distance minimale à l'eau
    min_distance_to_water = float('inf')
    
    for feature in water_features:
        polygon = feature.get("polygon", [])
        if len(polygon) < 3:
            continue
        
        distance = distance_to_polygon_edge((lat, lng), polygon)
        min_distance_to_water = min(min_distance_to_water, distance)
    
    # Ajuster le rayon si nécessaire
    if min_distance_to_water < float('inf'):
        max_safe_radius = min_distance_to_water - tolerance_meters
        if max_safe_radius > 0 and max_safe_radius < radius:
            zone = zone.copy()
            zone["radiusMeters"] = max_safe_radius
            zone["radiusAdjusted"] = True
            zone["originalRadius"] = radius
    
    return zone

# ============================================
# API ENDPOINTS
# ============================================

def get_water_exclusion_stats(zones: List[Dict], stats: Dict) -> Dict:
    """
    Génère un rapport de statistiques d'exclusion
    """
    return {
        "summary": {
            "zones_total": stats.get("total", 0),
            "zones_valid": stats.get("filtered", 0),
            "zones_excluded": stats.get("excluded", 0),
            "exclusion_rate": f"{(stats.get('excluded', 0) / max(1, stats.get('total', 1)) * 100):.1f}%"
        },
        "water_detection": {
            "features_found": stats.get("water_features_count", 0),
            "tolerance_meters": stats.get("tolerance_meters", SHORE_TOLERANCE_METERS)
        },
        "excluded_details": stats.get("excluded_details", [])
    }

# ============================================
# INITIALISATION
# ============================================

logger.info("Hydrography Service initialized - Water exclusion for BIONIC zones")
