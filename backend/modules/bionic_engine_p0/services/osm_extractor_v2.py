"""
BIONIC ENGINE - OSM Data Extractor V2
PHASE P1-HOTSPOTS V3 — Module d'Extraction OSM Optimisé

Version optimisée pour grandes régions: extraction par sous-régions
avec fusion automatique des résultats.

Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
"""

import json
import time
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

import requests
from shapely.geometry import Polygon, LineString, mapping

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
CACHE_DIR = Path("/app/backend/data/osm_cache")

# Paramètres optimisés
BASE_DELAY = 5
MAX_RETRIES = 3
REQUEST_TIMEOUT = 120

# Zones de chasse typiques - sous-régions
# Plus petites zones = requêtes plus rapides et fiables
HUNTING_SUBREGIONS = {
    # ================= CANADA - QUÉBEC =================
    "CA-QC-QUEBEC": {
        "name": "Région Québec (Capitale-Nationale)",
        "bbox": [-72.0, 46.5, -70.5, 47.5],
        "parent": "CA-QC"
    },
    "CA-QC-SAGUENAY": {
        "name": "Région Saguenay-Lac-Saint-Jean",
        "bbox": [-73.0, 47.8, -70.0, 49.5],
        "parent": "CA-QC"
    },
    "CA-QC-LAURENTIDES": {
        "name": "Région Laurentides",
        "bbox": [-75.0, 45.5, -73.5, 47.0],
        "parent": "CA-QC"
    },
    "CA-QC-MAURICIE": {
        "name": "Région Mauricie",
        "bbox": [-73.5, 46.0, -72.0, 47.5],
        "parent": "CA-QC"
    },
    "CA-QC-OUTAOUAIS": {
        "name": "Région Outaouais",
        "bbox": [-78.0, 45.5, -75.0, 47.5],
        "parent": "CA-QC"
    },
    
    # ================= CANADA - ONTARIO =================
    "CA-ON-NORTH": {
        "name": "Northern Ontario (Hunting Belt)",
        "bbox": [-85.0, 46.5, -79.0, 50.0],
        "parent": "CA-ON"
    },
    "CA-ON-ALGONQUIN": {
        "name": "Algonquin Region",
        "bbox": [-79.0, 45.0, -77.0, 46.5],
        "parent": "CA-ON"
    },
    "CA-ON-MUSKOKA": {
        "name": "Muskoka-Parry Sound",
        "bbox": [-80.5, 44.5, -78.5, 46.0],
        "parent": "CA-ON"
    },
    "CA-ON-OTTAWA": {
        "name": "Ottawa Valley",
        "bbox": [-77.5, 44.5, -75.0, 46.0],
        "parent": "CA-ON"
    },
    
    # ================= USA - NEW YORK =================
    "US-NY-ADIRONDACKS": {
        "name": "Adirondacks Region",
        "bbox": [-75.5, 43.5, -73.5, 45.0],
        "parent": "US-NY"
    },
    "US-NY-CATSKILLS": {
        "name": "Catskills Region",
        "bbox": [-75.0, 41.5, -73.5, 42.5],
        "parent": "US-NY"
    },
    "US-NY-FINGER-LAKES": {
        "name": "Finger Lakes Region",
        "bbox": [-77.5, 42.0, -76.0, 43.0],
        "parent": "US-NY"
    },
    "US-NY-SOUTHERN-TIER": {
        "name": "Southern Tier",
        "bbox": [-79.0, 41.8, -75.5, 42.5],
        "parent": "US-NY"
    },
    
    # ================= FRANCE - AUVERGNE-RHÔNE-ALPES =================
    "FR-ARA-ISERE": {
        "name": "Isère (Alpes)",
        "bbox": [5.0, 44.7, 6.5, 45.9],
        "parent": "FR-ARA"
    },
    "FR-ARA-DROME": {
        "name": "Drôme (Préalpes)",
        "bbox": [4.6, 44.1, 5.8, 45.0],
        "parent": "FR-ARA"
    },
    "FR-ARA-ARDECHE": {
        "name": "Ardèche",
        "bbox": [3.8, 44.2, 4.9, 45.0],
        "parent": "FR-ARA"
    },
    "FR-ARA-SAVOIE": {
        "name": "Savoie (Alpes)",
        "bbox": [5.6, 45.0, 7.2, 46.0],
        "parent": "FR-ARA"
    },
}

# Types d'exclusion simplifiés pour requêtes plus rapides
EXCLUSION_QUERIES = {
    "water": [
        ('way["natural"="water"]', "lakes_ponds"),
        ('way["waterway"~"river|stream"]', "rivers_streams"),
    ],
    "roads": [
        ('way["highway"~"motorway|trunk|primary|secondary|tertiary"]', "roads"),
    ],
    "landuse": [
        ('way["landuse"~"residential|commercial|industrial"]', "urban"),
    ],
}


class OSMSubregionExtractor:
    """Extracteur OSM optimisé pour sous-régions."""
    
    def __init__(self, cache_dir: Path = CACHE_DIR):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": "BIONIC-V5/1.0"})
    
    def extract_subregion(
        self,
        subregion_id: str,
        zone_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Extrait les données OSM pour une sous-région."""
        
        if subregion_id not in HUNTING_SUBREGIONS:
            logger.error(f"Sous-région inconnue: {subregion_id}")
            return {"success": False, "error": "Unknown subregion"}
        
        subregion = HUNTING_SUBREGIONS[subregion_id]
        bbox = subregion["bbox"]
        
        logger.info(f"{'='*50}")
        logger.info(f"EXTRACTION: {subregion['name']}")
        logger.info(f"Bbox: {bbox}")
        logger.info(f"{'='*50}")
        
        cache_data = {
            "region_id": subregion_id,
            "region_name": subregion["name"],
            "bbox": bbox,
            "parent_region": subregion["parent"],
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "version": "2.0.0",
            "exclusion_zones": []
        }
        
        types_to_extract = zone_types or list(EXCLUSION_QUERIES.keys())
        
        for zone_type in types_to_extract:
            if zone_type not in EXCLUSION_QUERIES:
                continue
            
            logger.info(f"\n--- {zone_type.upper()} ---")
            
            for query, query_name in EXCLUSION_QUERIES[zone_type]:
                result = self._run_query(bbox, query, query_name)
                
                if result["success"]:
                    for geom in result["geometries"]:
                        cache_data["exclusion_zones"].append({
                            "zone_type": zone_type,
                            "query": query_name,
                            "geometry": geom
                        })
                
                time.sleep(BASE_DELAY)
        
        # Sauvegarder
        cache_file = self.cache_dir / f"{subregion_id}.json"
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f)
        
        logger.info(f"\nTotal zones: {len(cache_data['exclusion_zones'])}")
        logger.info(f"Sauvegardé: {cache_file}")
        
        return {
            "success": True,
            "region_id": subregion_id,
            "total_zones": len(cache_data["exclusion_zones"])
        }
    
    def _run_query(
        self,
        bbox: List[float],
        query: str,
        query_name: str
    ) -> Dict[str, Any]:
        """Exécute une requête Overpass."""
        
        # Format: south, west, north, east
        bbox_str = f"{bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]}"
        
        overpass_query = f"""
        [out:json][timeout:{REQUEST_TIMEOUT}];
        (
            {query}({bbox_str});
        );
        out geom;
        """
        
        logger.info(f"  {query_name}...")
        
        for attempt in range(MAX_RETRIES):
            try:
                if attempt > 0:
                    delay = BASE_DELAY * (2 ** attempt)
                    logger.info(f"    Retry {attempt+1}/{MAX_RETRIES} après {delay}s")
                    time.sleep(delay)
                
                response = self._session.post(
                    OVERPASS_URL,
                    data={"data": overpass_query},
                    timeout=REQUEST_TIMEOUT
                )
                
                if response.status_code == 429:
                    logger.warning("    Rate limited, attente...")
                    time.sleep(30)
                    continue
                
                if response.status_code != 200:
                    logger.warning(f"    HTTP {response.status_code}")
                    continue
                
                data = response.json()
                elements = data.get("elements", [])
                
                geometries = []
                for elem in elements:
                    geom = self._to_geometry(elem)
                    if geom:
                        geometries.append(geom)
                
                logger.info(f"    OK: {len(geometries)} géométries")
                return {"success": True, "geometries": geometries}
                
            except Exception as e:
                logger.warning(f"    Erreur: {e}")
        
        return {"success": False, "geometries": []}
    
    def _to_geometry(self, element: Dict) -> Optional[Dict]:
        """Convertit élément OSM en GeoJSON."""
        elem_type = element.get("type")
        
        if elem_type == "way":
            geom_data = element.get("geometry", [])
            if len(geom_data) >= 3:
                coords = [(g["lon"], g["lat"]) for g in geom_data]
                try:
                    if coords[0] == coords[-1]:
                        poly = Polygon(coords)
                    else:
                        poly = LineString(coords).buffer(0.0002)
                    
                    if poly.is_valid and poly.area > 0:
                        return mapping(poly)
                except:
                    pass
        
        return None
    
    def merge_to_parent(self, parent_id: str) -> Dict[str, Any]:
        """Fusionne toutes les sous-régions vers la région parent."""
        
        logger.info(f"\n{'='*50}")
        logger.info(f"FUSION vers {parent_id}")
        logger.info(f"{'='*50}")
        
        all_zones = []
        subregions_used = []
        
        for sub_id, sub_info in HUNTING_SUBREGIONS.items():
            if sub_info["parent"] != parent_id:
                continue
            
            cache_file = self.cache_dir / f"{sub_id}.json"
            if cache_file.exists():
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                
                zones = data.get("exclusion_zones", [])
                all_zones.extend(zones)
                subregions_used.append(sub_id)
                logger.info(f"  {sub_id}: {len(zones)} zones")
        
        # Créer le cache parent fusionné
        parent_data = {
            "region_id": parent_id,
            "region_name": f"Merged: {parent_id}",
            "bbox": [-79.8, 44.9, -57.1, 62.6],  # Full Quebec
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "version": "2.0.0",
            "subregions_merged": subregions_used,
            "exclusion_zones": all_zones
        }
        
        cache_file = self.cache_dir / f"{parent_id}.json"
        with open(cache_file, 'w') as f:
            json.dump(parent_data, f)
        
        logger.info(f"\nTotal fusionné: {len(all_zones)} zones")
        logger.info(f"Sauvegardé: {cache_file}")
        
        return {
            "success": True,
            "parent_id": parent_id,
            "total_zones": len(all_zones),
            "subregions": subregions_used
        }


def main():
    """Point d'entrée."""
    import argparse
    
    parser = argparse.ArgumentParser(description="OSM Extractor V2")
    parser.add_argument("--subregion", "-s", help="Sous-région à extraire")
    parser.add_argument("--merge", "-m", help="Fusionner vers région parent")
    parser.add_argument("--list", "-l", action="store_true", help="Lister sous-régions")
    parser.add_argument("--types", "-t", nargs="+", help="Types d'exclusion")
    
    args = parser.parse_args()
    
    extractor = OSMSubregionExtractor()
    
    if args.list:
        logger.info("SOUS-RÉGIONS DISPONIBLES:")
        for sub_id, info in HUNTING_SUBREGIONS.items():
            logger.info(f"  {sub_id}: {info['name']}")
        return
    
    if args.subregion:
        extractor.extract_subregion(args.subregion, args.types)
        return
    
    if args.merge:
        extractor.merge_to_parent(args.merge)
        return
    
    parser.print_help()


if __name__ == "__main__":
    main()
