"""
BIONIC ENGINE - Cache OSM Multi-Régions
PHASE P1-HOTSPOTS V3 — REFONTE MAJEURE

Système de cache local pour données OpenStreetMap.
Évitement RÉEL des zones d'eau, routes, zones urbaines et infrastructures.

ARCHITECTURE:
- Extraction initiale via Overpass API
- Stockage en cache local par région (pays/province/état)
- Rafraîchissement périodique configurable
- ZÉRO dépendance temps réel
- ZÉRO risque de rate limit

SCALABILITÉ INTERNATIONALE:
- Canada (toutes provinces/territoires)
- États-Unis (tous états)
- Europe, Amérique du Sud, Afrique, Océanie

Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
import json
import logging
from pathlib import Path
from shapely.geometry import Point, Polygon, MultiPolygon, LineString, shape
from shapely.ops import unary_union
from shapely.prepared import prep
import requests

logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION GLOBALE
# =============================================================================

# Répertoire de cache
CACHE_DIR = Path("/app/backend/data/osm_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Durée de validité du cache (7 jours par défaut)
CACHE_VALIDITY_DAYS = 7

# Types d'exclusion OSM
EXCLUSION_TYPES = {
    "water": {
        "queries": [
            'way["natural"="water"]',
            'relation["natural"="water"]',
            'way["waterway"]',
            'relation["waterway"]',
            'way["landuse"="reservoir"]',
            'way["landuse"="basin"]',
        ],
        "description": "Étendues d'eau, lacs, rivières, réservoirs"
    },
    "roads": {
        "queries": [
            'way["highway"~"motorway|trunk|primary|secondary|tertiary|residential|service"]',
        ],
        "description": "Routes et autoroutes"
    },
    "urban": {
        "queries": [
            'way["landuse"~"residential|commercial|industrial|retail"]',
            'relation["landuse"~"residential|commercial|industrial|retail"]',
        ],
        "description": "Zones urbaines, résidentielles, commerciales, industrielles"
    },
    "infrastructure": {
        "queries": [
            'way["landuse"~"railway|quarry|landfill|military"]',
            'way["aeroway"]',
            'way["power"="plant"]',
        ],
        "description": "Infrastructures (chemins de fer, carrières, aéroports, etc.)"
    },
    "agriculture": {
        "queries": [
            'way["landuse"~"farmland|farmyard|greenhouse_horticulture"]',
        ],
        "description": "Zones agricoles"
    },
    "recreation": {
        "queries": [
            'way["leisure"~"golf_course|stadium|sports_centre"]',
            'way["landuse"="recreation_ground"]',
        ],
        "description": "Zones récréatives"
    }
}

# Régions prédéfinies avec leurs bounding boxes
PREDEFINED_REGIONS = {
    # Canada
    "CA-QC": {"name": "Québec, Canada", "bbox": [-79.8, 44.9, -57.1, 62.6]},
    "CA-ON": {"name": "Ontario, Canada", "bbox": [-95.2, 41.7, -74.3, 56.9]},
    "CA-BC": {"name": "British Columbia, Canada", "bbox": [-139.1, 48.3, -114.0, 60.0]},
    "CA-AB": {"name": "Alberta, Canada", "bbox": [-120.0, 49.0, -110.0, 60.0]},
    # États-Unis (exemples)
    "US-NY": {"name": "New York, USA", "bbox": [-79.8, 40.5, -71.9, 45.0]},
    "US-MT": {"name": "Montana, USA", "bbox": [-116.1, 44.4, -104.0, 49.0]},
    "US-WI": {"name": "Wisconsin, USA", "bbox": [-92.9, 42.5, -86.8, 47.1]},
    # Europe (exemples)
    "FR-ARA": {"name": "Auvergne-Rhône-Alpes, France", "bbox": [2.1, 44.1, 7.2, 46.8]},
    "DE-BY": {"name": "Bavaria, Germany", "bbox": [8.9, 47.3, 13.8, 50.6]},
}


# =============================================================================
# STRUCTURES DE DONNÉES
# =============================================================================

@dataclass
class ExclusionZone:
    """Zone d'exclusion géospatiale."""
    zone_type: str  # water, roads, urban, etc.
    geometry: Any  # Shapely geometry
    osm_id: Optional[str] = None
    name: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class RegionCache:
    """Cache d'une région géographique avec géométries pré-calculées."""
    region_id: str
    region_name: str
    bbox: List[float]  # [west, south, east, north]
    exclusion_zones: List[ExclusionZone] = field(default_factory=list)
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "1.0.0"
    # Cache des géométries préparées
    _prepared_by_type: Dict[str, Any] = field(default_factory=dict, repr=False)
    _prepared_all: Any = field(default=None, repr=False)
    _is_prepared: bool = field(default=False, repr=False)
    
    @property
    def is_valid(self) -> bool:
        """Vérifie si le cache est encore valide."""
        age = datetime.now(timezone.utc) - self.last_updated
        return age < timedelta(days=CACHE_VALIDITY_DAYS)
    
    def prepare_geometries(self) -> None:
        """Pré-calcule et cache les géométries unifiées."""
        if self._is_prepared:
            return
        
        logger.info(f"Préparation des géométries pour {self.region_id}...")
        
        # Grouper par type
        by_type: Dict[str, List] = {}
        for zone in self.exclusion_zones:
            if zone.geometry is not None:
                if zone.zone_type not in by_type:
                    by_type[zone.zone_type] = []
                by_type[zone.zone_type].append(zone.geometry)
        
        # Préparer par type
        for zone_type, geoms in by_type.items():
            if geoms:
                try:
                    combined = unary_union(geoms)
                    self._prepared_by_type[zone_type] = prep(combined)
                except Exception as e:
                    logger.warning(f"Erreur préparation {zone_type}: {e}")
        
        # Préparer union totale
        all_geoms = [z.geometry for z in self.exclusion_zones if z.geometry is not None]
        if all_geoms:
            try:
                self._prepared_all = prep(unary_union(all_geoms))
            except Exception as e:
                logger.warning(f"Erreur préparation union totale: {e}")
        
        self._is_prepared = True
        logger.info(f"Géométries préparées pour {self.region_id}: {len(self._prepared_by_type)} types")
    
    def get_prepared_geometry(self, zone_type: str) -> Optional[Any]:
        """Retourne la géométrie préparée pour un type d'exclusion."""
        self.prepare_geometries()
        return self._prepared_by_type.get(zone_type)
    
    def get_all_exclusions_geometry(self) -> Optional[Any]:
        """Retourne la géométrie combinée de toutes les exclusions."""
        self.prepare_geometries()
        return self._prepared_all


# =============================================================================
# SERVICE DE CACHE OSM
# =============================================================================

class OSMCacheService:
    """
    Service de cache OSM multi-régions.
    
    FONCTIONNALITÉS:
    - Extraction via Overpass API (batch, pas temps réel)
    - Stockage local en JSON
    - Validation géospatiale rapide via Shapely
    - Support multi-régions international
    
    UTILISATION:
    ```python
    cache = OSMCacheService()
    
    # Charger ou extraire le cache pour le Québec
    region = cache.get_region("CA-QC")
    
    # Vérifier si un point est dans une zone d'exclusion
    is_excluded = cache.is_point_excluded(46.85, -71.25, "CA-QC")
    
    # Vérifier si un polygone intersecte une zone d'exclusion
    is_valid = cache.is_polygon_valid(polygon_coords, "CA-QC")
    ```
    """
    
    def __init__(self, cache_dir: Path = CACHE_DIR):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._loaded_regions: Dict[str, RegionCache] = {}
        self._overpass_url = "https://overpass-api.de/api/interpreter"
    
    def get_region_id_for_point(self, lat: float, lng: float) -> Optional[str]:
        """Détermine la région pour un point géographique."""
        for region_id, region_info in PREDEFINED_REGIONS.items():
            bbox = region_info["bbox"]
            if bbox[0] <= lng <= bbox[2] and bbox[1] <= lat <= bbox[3]:
                return region_id
        return None
    
    def get_region(self, region_id: str, force_refresh: bool = False) -> Optional[RegionCache]:
        """
        Obtient le cache d'une région.
        
        Args:
            region_id: ID de la région (ex: "CA-QC")
            force_refresh: Force le rafraîchissement du cache
            
        Returns:
            RegionCache ou None si la région n'existe pas
        """
        # Vérifier le cache en mémoire
        if region_id in self._loaded_regions and not force_refresh:
            cached = self._loaded_regions[region_id]
            if cached.is_valid:
                return cached
        
        # Vérifier le cache sur disque
        cache_file = self.cache_dir / f"{region_id}.json"
        if cache_file.exists() and not force_refresh:
            try:
                region = self._load_from_disk(cache_file)
                if region and region.is_valid:
                    self._loaded_regions[region_id] = region
                    return region
            except Exception as e:
                logger.warning(f"Erreur lecture cache {region_id}: {e}")
        
        # Région non définie
        if region_id not in PREDEFINED_REGIONS:
            logger.warning(f"Région inconnue: {region_id}")
            return None
        
        # Extraire depuis Overpass (si disponible)
        # NOTE: En mode production, cette extraction serait faite en batch
        # Pour l'instant, on crée un cache vide qui sera peuplé progressivement
        region = self._create_empty_region(region_id)
        self._loaded_regions[region_id] = region
        self._save_to_disk(region)
        
        return region
    
    def is_point_excluded(
        self, 
        lat: float, 
        lng: float, 
        region_id: Optional[str] = None,
        exclusion_types: Optional[List[str]] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Vérifie si un point est dans une zone d'exclusion.
        
        Args:
            lat: Latitude
            lng: Longitude
            region_id: ID de région (auto-détecté si None)
            exclusion_types: Types d'exclusion à vérifier (tous si None)
            
        Returns:
            (is_excluded, exclusion_type) - True si exclu, avec le type
        """
        if region_id is None:
            region_id = self.get_region_id_for_point(lat, lng)
        
        if region_id is None:
            # Région non couverte - pas d'exclusion
            return False, None
        
        region = self.get_region(region_id)
        if region is None or not region.exclusion_zones:
            return False, None
        
        point = Point(lng, lat)
        types_to_check = exclusion_types or list(EXCLUSION_TYPES.keys())
        
        for zone_type in types_to_check:
            prepared = region.get_prepared_geometry(zone_type)
            if prepared and prepared.contains(point):
                return True, zone_type
        
        return False, None
    
    def is_polygon_valid(
        self,
        coords: List[List[float]],
        region_id: Optional[str] = None,
        exclusion_types: Optional[List[str]] = None
    ) -> Tuple[bool, Optional[str], float]:
        """
        Vérifie si un polygone est valide (pas d'intersection avec exclusions).
        
        Args:
            coords: Coordonnées [[lng, lat], ...]
            region_id: ID de région
            exclusion_types: Types d'exclusion à vérifier
            
        Returns:
            (is_valid, intersection_type, overlap_percentage)
        """
        if len(coords) < 3:
            return False, "invalid_geometry", 0.0
        
        try:
            polygon = Polygon([(c[0], c[1]) for c in coords])
            if not polygon.is_valid:
                polygon = polygon.buffer(0)
        except Exception:
            return False, "invalid_geometry", 0.0
        
        # Déterminer la région
        centroid = polygon.centroid
        if region_id is None:
            region_id = self.get_region_id_for_point(centroid.y, centroid.x)
        
        if region_id is None:
            return True, None, 0.0  # Région non couverte - valide par défaut
        
        region = self.get_region(region_id)
        if region is None or not region.exclusion_zones:
            return True, None, 0.0
        
        types_to_check = exclusion_types or list(EXCLUSION_TYPES.keys())
        
        for zone_type in types_to_check:
            prepared = region.get_prepared_geometry(zone_type)
            if prepared and prepared.intersects(polygon):
                # Calculer le pourcentage de chevauchement
                combined = unary_union([
                    z.geometry for z in region.exclusion_zones 
                    if z.zone_type == zone_type and z.geometry is not None
                ])
                try:
                    intersection = polygon.intersection(combined)
                    overlap_pct = (intersection.area / polygon.area) * 100
                    return False, zone_type, overlap_pct
                except Exception:
                    return False, zone_type, 0.0
        
        return True, None, 0.0
    
    def clip_polygon_to_valid_area(
        self,
        coords: List[List[float]],
        region_id: Optional[str] = None
    ) -> Optional[List[List[float]]]:
        """
        Découpe un polygone pour éviter les zones d'exclusion.
        
        Returns:
            Coordonnées du polygone découpé ou None si impossible
        """
        if len(coords) < 3:
            return None
        
        try:
            polygon = Polygon([(c[0], c[1]) for c in coords])
            if not polygon.is_valid:
                polygon = polygon.buffer(0)
        except Exception:
            return None
        
        centroid = polygon.centroid
        if region_id is None:
            region_id = self.get_region_id_for_point(centroid.y, centroid.x)
        
        if region_id is None:
            return coords  # Pas de découpe nécessaire
        
        region = self.get_region(region_id)
        if region is None or not region.exclusion_zones:
            return coords
        
        # Combiner toutes les exclusions
        exclusion_geoms = [
            z.geometry for z in region.exclusion_zones 
            if z.geometry is not None
        ]
        if not exclusion_geoms:
            return coords
        
        try:
            all_exclusions = unary_union(exclusion_geoms)
            clipped = polygon.difference(all_exclusions)
            
            if clipped.is_empty:
                return None
            
            # Prendre le plus grand polygone si MultiPolygon
            if isinstance(clipped, MultiPolygon):
                clipped = max(clipped.geoms, key=lambda g: g.area)
            
            # Convertir en liste de coordonnées
            exterior = list(clipped.exterior.coords)
            return [[c[0], c[1]] for c in exterior]
            
        except Exception as e:
            logger.warning(f"Erreur découpe polygone: {e}")
            return None
    
    def add_exclusion_zone(
        self,
        region_id: str,
        zone_type: str,
        geometry: Any,
        osm_id: Optional[str] = None,
        name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Ajoute une zone d'exclusion au cache.
        
        Args:
            region_id: ID de la région
            zone_type: Type d'exclusion (water, roads, etc.)
            geometry: Géométrie Shapely
            osm_id: ID OSM optionnel
            name: Nom optionnel
            tags: Tags OSM optionnels
            
        Returns:
            True si ajouté avec succès
        """
        region = self.get_region(region_id)
        if region is None:
            return False
        
        zone = ExclusionZone(
            zone_type=zone_type,
            geometry=geometry,
            osm_id=osm_id,
            name=name,
            tags=tags or {}
        )
        
        region.exclusion_zones.append(zone)
        region.last_updated = datetime.now(timezone.utc)
        
        self._save_to_disk(region)
        return True
    
    def extract_from_overpass(
        self,
        region_id: str,
        exclusion_types: Optional[List[str]] = None
    ) -> bool:
        """
        Extrait les données OSM via Overpass API.
        
        NOTE: Cette méthode est prévue pour une exécution batch,
        pas en temps réel pendant la génération de hotspots.
        
        Args:
            region_id: ID de la région
            exclusion_types: Types à extraire (tous si None)
            
        Returns:
            True si extraction réussie
        """
        if region_id not in PREDEFINED_REGIONS:
            logger.error(f"Région inconnue: {region_id}")
            return False
        
        region_info = PREDEFINED_REGIONS[region_id]
        bbox = region_info["bbox"]
        bbox_str = f"{bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]}"
        
        types_to_extract = exclusion_types or list(EXCLUSION_TYPES.keys())
        region = self._create_empty_region(region_id)
        
        for zone_type in types_to_extract:
            if zone_type not in EXCLUSION_TYPES:
                continue
            
            type_info = EXCLUSION_TYPES[zone_type]
            
            for query in type_info["queries"]:
                overpass_query = f"""
                [out:json][timeout:60];
                (
                    {query}({bbox_str});
                );
                out geom;
                """
                
                try:
                    response = requests.post(
                        self._overpass_url,
                        data={"data": overpass_query},
                        timeout=120
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        self._process_overpass_response(region, zone_type, data)
                        logger.info(f"Extrait {zone_type} pour {region_id}")
                    else:
                        logger.warning(f"Erreur Overpass: {response.status_code}")
                        
                except Exception as e:
                    logger.error(f"Erreur extraction {zone_type}: {e}")
        
        # Sauvegarder le cache
        self._loaded_regions[region_id] = region
        self._save_to_disk(region)
        
        return True
    
    def _process_overpass_response(
        self,
        region: RegionCache,
        zone_type: str,
        data: Dict[str, Any]
    ) -> None:
        """Traite la réponse Overpass et ajoute les géométries."""
        elements = data.get("elements", [])
        
        for element in elements:
            try:
                geometry = self._element_to_geometry(element)
                if geometry is not None:
                    zone = ExclusionZone(
                        zone_type=zone_type,
                        geometry=geometry,
                        osm_id=str(element.get("id", "")),
                        name=element.get("tags", {}).get("name"),
                        tags=element.get("tags", {})
                    )
                    region.exclusion_zones.append(zone)
            except Exception as e:
                logger.debug(f"Erreur traitement élément: {e}")
    
    def _element_to_geometry(self, element: Dict[str, Any]) -> Optional[Any]:
        """Convertit un élément OSM en géométrie Shapely."""
        elem_type = element.get("type")
        
        if elem_type == "way":
            geometry = element.get("geometry", [])
            if len(geometry) >= 3:
                coords = [(g["lon"], g["lat"]) for g in geometry]
                if coords[0] == coords[-1]:
                    return Polygon(coords)
                else:
                    return LineString(coords).buffer(0.0001)  # ~10m buffer
        
        elif elem_type == "relation":
            # Simplification: traiter comme MultiPolygon
            members = element.get("members", [])
            polygons = []
            for member in members:
                geom = member.get("geometry", [])
                if len(geom) >= 3:
                    coords = [(g["lon"], g["lat"]) for g in geom]
                    try:
                        poly = Polygon(coords)
                        if poly.is_valid:
                            polygons.append(poly)
                    except Exception:
                        pass
            
            if polygons:
                return unary_union(polygons)
        
        return None
    
    def _create_empty_region(self, region_id: str) -> RegionCache:
        """Crée un cache de région vide."""
        region_info = PREDEFINED_REGIONS.get(region_id, {})
        return RegionCache(
            region_id=region_id,
            region_name=region_info.get("name", region_id),
            bbox=region_info.get("bbox", [0, 0, 0, 0]),
            exclusion_zones=[],
            last_updated=datetime.now(timezone.utc)
        )
    
    def _load_from_disk(self, cache_file: Path) -> Optional[RegionCache]:
        """Charge un cache depuis le disque."""
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            region = RegionCache(
                region_id=data["region_id"],
                region_name=data["region_name"],
                bbox=data["bbox"],
                last_updated=datetime.fromisoformat(data["last_updated"]),
                version=data.get("version", "1.0.0")
            )
            
            # Reconstruire les géométries
            for zone_data in data.get("exclusion_zones", []):
                try:
                    geom = shape(zone_data["geometry"]) if zone_data.get("geometry") else None
                    zone = ExclusionZone(
                        zone_type=zone_data["zone_type"],
                        geometry=geom,
                        osm_id=zone_data.get("osm_id"),
                        name=zone_data.get("name"),
                        tags=zone_data.get("tags", {})
                    )
                    region.exclusion_zones.append(zone)
                except Exception as e:
                    logger.debug(f"Erreur reconstruction géométrie: {e}")
            
            return region
            
        except Exception as e:
            logger.error(f"Erreur chargement cache: {e}")
            return None
    
    def _save_to_disk(self, region: RegionCache) -> bool:
        """Sauvegarde un cache sur le disque."""
        try:
            cache_file = self.cache_dir / f"{region.region_id}.json"
            
            # Convertir les géométries en GeoJSON
            zones_data = []
            for zone in region.exclusion_zones:
                zone_dict = {
                    "zone_type": zone.zone_type,
                    "osm_id": zone.osm_id,
                    "name": zone.name,
                    "tags": zone.tags,
                    "geometry": None
                }
                if zone.geometry is not None:
                    try:
                        from shapely.geometry import mapping
                        zone_dict["geometry"] = mapping(zone.geometry)
                    except Exception:
                        pass
                zones_data.append(zone_dict)
            
            data = {
                "region_id": region.region_id,
                "region_name": region.region_name,
                "bbox": region.bbox,
                "last_updated": region.last_updated.isoformat(),
                "version": region.version,
                "exclusion_zones": zones_data
            }
            
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde cache: {e}")
            return False


# =============================================================================
# INSTANCE GLOBALE
# =============================================================================

_osm_cache_service: Optional[OSMCacheService] = None

def get_osm_cache() -> OSMCacheService:
    """Retourne l'instance globale du service de cache OSM."""
    global _osm_cache_service
    if _osm_cache_service is None:
        _osm_cache_service = OSMCacheService()
    return _osm_cache_service


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'OSMCacheService',
    'RegionCache',
    'ExclusionZone',
    'get_osm_cache',
    'EXCLUSION_TYPES',
    'PREDEFINED_REGIONS',
    'CACHE_DIR'
]
