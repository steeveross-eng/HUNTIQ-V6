# ══════════════════════════════════════════════════════════════
# LEGACY FIGÉ — NE PAS MODIFIER
# Remplacé par: pipeline_v7.py / zone_engine_core_v2.py / osm_extractor_v2.py
# Date gel: 2026-03-10
# ══════════════════════════════════════════════════════════════
"""
BIONIC ENGINE - OSM Data Extractor
PHASE P1-HOTSPOTS V3 — Module d'Extraction OSM

Script robuste et paramétrable pour extraire les données OpenStreetMap
via l'API Overpass avec gestion automatique du rate-limiting.

SCALABILITÉ INTERNATIONALE:
- Canada (toutes provinces/territoires)
- États-Unis (tous états)
- Europe, Amérique du Sud, Afrique, Océanie

CARACTÉRISTIQUES:
- Retry automatique avec backoff exponentiel
- Délais progressifs pour respecter les limites Overpass
- Extraction par type d'exclusion (water, roads, landuse)
- Logging détaillé
- Support multi-régions

Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
"""

import sys
import json
import time
import logging
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

import requests
from shapely.geometry import Polygon, LineString, mapping
from shapely.ops import unary_union

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION
# =============================================================================

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
CACHE_DIR = Path("/app/backend/data/osm_cache")

# Délais pour respecter le rate-limiting Overpass
BASE_DELAY = 10  # Délai de base entre requêtes (secondes)
MAX_RETRIES = 5  # Nombre maximal de tentatives
BACKOFF_MULTIPLIER = 2  # Multiplicateur pour backoff exponentiel
REQUEST_TIMEOUT = 180  # Timeout par requête (secondes)

# Régions prédéfinies avec leurs bounding boxes [west, south, east, north]
PREDEFINED_REGIONS = {
    # Canada
    "CA-QC": {"name": "Québec, Canada", "bbox": [-79.8, 44.9, -57.1, 62.6]},
    "CA-ON": {"name": "Ontario, Canada", "bbox": [-95.2, 41.7, -74.3, 56.9]},
    "CA-BC": {"name": "British Columbia, Canada", "bbox": [-139.1, 48.3, -114.0, 60.0]},
    "CA-AB": {"name": "Alberta, Canada", "bbox": [-120.0, 49.0, -110.0, 60.0]},
    "CA-MB": {"name": "Manitoba, Canada", "bbox": [-102.0, 49.0, -89.0, 60.0]},
    "CA-SK": {"name": "Saskatchewan, Canada", "bbox": [-110.0, 49.0, -102.0, 60.0]},
    "CA-NB": {"name": "New Brunswick, Canada", "bbox": [-69.1, 44.5, -63.8, 48.1]},
    "CA-NS": {"name": "Nova Scotia, Canada", "bbox": [-66.5, 43.4, -59.7, 47.1]},
    "CA-NL": {"name": "Newfoundland & Labrador, Canada", "bbox": [-67.8, 46.6, -52.6, 60.4]},
    "CA-PE": {"name": "Prince Edward Island, Canada", "bbox": [-64.5, 45.9, -62.0, 47.1]},
    "CA-YT": {"name": "Yukon, Canada", "bbox": [-141.0, 60.0, -123.8, 69.6]},
    "CA-NT": {"name": "Northwest Territories, Canada", "bbox": [-136.5, 60.0, -102.0, 78.8]},
    "CA-NU": {"name": "Nunavut, Canada", "bbox": [-120.7, 51.7, -61.1, 83.1]},
    
    # États-Unis (sélection)
    "US-NY": {"name": "New York, USA", "bbox": [-79.8, 40.5, -71.9, 45.0]},
    "US-MT": {"name": "Montana, USA", "bbox": [-116.1, 44.4, -104.0, 49.0]},
    "US-WI": {"name": "Wisconsin, USA", "bbox": [-92.9, 42.5, -86.8, 47.1]},
    "US-MI": {"name": "Michigan, USA", "bbox": [-90.4, 41.7, -82.4, 48.3]},
    "US-MN": {"name": "Minnesota, USA", "bbox": [-97.2, 43.5, -89.5, 49.4]},
    "US-PA": {"name": "Pennsylvania, USA", "bbox": [-80.5, 39.7, -74.7, 42.3]},
    "US-CO": {"name": "Colorado, USA", "bbox": [-109.1, 37.0, -102.0, 41.0]},
    "US-OR": {"name": "Oregon, USA", "bbox": [-124.6, 41.9, -116.5, 46.3]},
    "US-WA": {"name": "Washington, USA", "bbox": [-124.8, 45.5, -116.9, 49.0]},
    "US-AK": {"name": "Alaska, USA", "bbox": [-179.2, 51.2, -130.0, 71.4]},
    
    # Europe (sélection)
    "FR-ARA": {"name": "Auvergne-Rhône-Alpes, France", "bbox": [2.1, 44.1, 7.2, 46.8]},
    "FR-BFC": {"name": "Bourgogne-Franche-Comté, France", "bbox": [2.8, 46.2, 7.1, 48.4]},
    "FR-NAQ": {"name": "Nouvelle-Aquitaine, France", "bbox": [-1.8, 42.8, 2.6, 47.2]},
    "DE-BY": {"name": "Bavaria, Germany", "bbox": [8.9, 47.3, 13.8, 50.6]},
    "DE-NI": {"name": "Lower Saxony, Germany", "bbox": [6.6, 51.3, 11.6, 53.9]},
    "SE-VL": {"name": "Västra Götaland, Sweden", "bbox": [11.1, 57.4, 14.8, 59.3]},
    "FI-LP": {"name": "Lapland, Finland", "bbox": [20.6, 66.0, 30.0, 70.1]},
    
    # Amérique du Sud (sélection)
    "AR-RN": {"name": "Río Negro, Argentina", "bbox": [-71.9, -41.9, -62.8, -38.0]},
    "AR-NQ": {"name": "Neuquén, Argentina", "bbox": [-71.9, -40.1, -68.0, -36.2]},
    "CL-AI": {"name": "Aysén, Chile", "bbox": [-75.6, -49.2, -71.7, -43.6]},
    
    # Océanie
    "AU-VIC": {"name": "Victoria, Australia", "bbox": [140.9, -39.2, 150.0, -33.9]},
    "AU-NSW": {"name": "New South Wales, Australia", "bbox": [141.0, -37.5, 153.6, -28.2]},
    "NZ-CAN": {"name": "Canterbury, New Zealand", "bbox": [168.5, -45.1, 174.0, -42.1]},
    
    # Afrique (sélection)
    "ZA-WC": {"name": "Western Cape, South Africa", "bbox": [17.9, -34.8, 23.3, -31.0]},
    "NA-KH": {"name": "Khomas, Namibia", "bbox": [15.8, -23.5, 18.5, -21.5]},
}

# Types d'exclusion avec leurs requêtes Overpass
EXCLUSION_CONFIGS = {
    "water": {
        "description": "Étendues d'eau, lacs, rivières, réservoirs",
        "queries": [
            # Cours d'eau majeurs et lacs
            ('way["natural"="water"]', "natural_water_way"),
            ('relation["natural"="water"]', "natural_water_rel"),
            ('way["waterway"~"river|stream|canal"]', "waterway"),
            ('way["landuse"="reservoir"]', "reservoir"),
            ('way["landuse"="basin"]', "basin"),
        ]
    },
    "roads": {
        "description": "Routes et autoroutes principales",
        "queries": [
            ('way["highway"~"motorway|trunk|primary|secondary"]', "major_roads"),
            ('way["highway"~"tertiary|residential"]', "minor_roads"),
        ]
    },
    "landuse": {
        "description": "Zones résidentielles, commerciales, industrielles",
        "queries": [
            ('way["landuse"="residential"]', "residential"),
            ('way["landuse"="commercial"]', "commercial"),
            ('way["landuse"="industrial"]', "industrial"),
            ('way["landuse"="retail"]', "retail"),
            ('relation["landuse"~"residential|commercial|industrial|retail"]', "landuse_rel"),
        ]
    },
    "infrastructure": {
        "description": "Infrastructures (aéroports, voies ferrées, etc.)",
        "queries": [
            ('way["landuse"~"railway|quarry|landfill|military"]', "infrastructure"),
            ('way["aeroway"~"runway|taxiway|apron"]', "aeroway"),
        ]
    }
}


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class ExtractionResult:
    """Résultat d'une extraction OSM."""
    success: bool
    zone_type: str
    query_name: str
    element_count: int
    geometry_count: int
    error: Optional[str] = None


@dataclass
class RegionExtractionReport:
    """Rapport d'extraction pour une région."""
    region_id: str
    region_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    results: List[ExtractionResult] = field(default_factory=list)
    total_zones: int = 0
    
    @property
    def success_rate(self) -> float:
        if not self.results:
            return 0.0
        successful = sum(1 for r in self.results if r.success)
        return (successful / len(self.results)) * 100


# =============================================================================
# OSM EXTRACTOR CLASS
# =============================================================================

class OSMDataExtractor:
    """
    Extracteur de données OSM robuste et paramétrable.
    
    Gère automatiquement:
    - Rate-limiting avec backoff exponentiel
    - Retry automatique sur erreur
    - Extraction par type d'exclusion
    - Sauvegarde incrémentale du cache
    """
    
    def __init__(self, cache_dir: Path = CACHE_DIR):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "BIONIC-V5-OSM-Extractor/1.0"
        })
    
    def extract_region(
        self,
        region_id: str,
        zone_types: Optional[List[str]] = None,
        force_refresh: bool = False
    ) -> RegionExtractionReport:
        """
        Extrait les données OSM pour une région.
        
        Args:
            region_id: ID de la région (ex: "CA-QC")
            zone_types: Types d'exclusion à extraire (tous si None)
            force_refresh: Force le rafraîchissement même si cache valide
            
        Returns:
            RegionExtractionReport avec les résultats
        """
        if region_id not in PREDEFINED_REGIONS:
            logger.error(f"Région inconnue: {region_id}")
            logger.info(f"Régions disponibles: {', '.join(sorted(PREDEFINED_REGIONS.keys()))}")
            return RegionExtractionReport(
                region_id=region_id,
                region_name="Unknown",
                start_time=datetime.now(timezone.utc),
                end_time=datetime.now(timezone.utc)
            )
        
        region_info = PREDEFINED_REGIONS[region_id]
        report = RegionExtractionReport(
            region_id=region_id,
            region_name=region_info["name"],
            start_time=datetime.now(timezone.utc)
        )
        
        logger.info(f"{'='*60}")
        logger.info(f"EXTRACTION OSM: {region_info['name']} ({region_id})")
        logger.info(f"{'='*60}")
        
        # Charger ou créer le cache
        cache_data = self._load_or_create_cache(region_id, region_info)
        
        # Vérifier si extraction nécessaire
        if not force_refresh and cache_data.get("exclusion_zones"):
            logger.info("Cache existant avec données. Utilisez --force pour rafraîchir.")
        
        # Déterminer les types à extraire
        types_to_extract = zone_types or list(EXCLUSION_CONFIGS.keys())
        bbox = region_info["bbox"]
        
        # Extraire chaque type
        for zone_type in types_to_extract:
            if zone_type not in EXCLUSION_CONFIGS:
                logger.warning(f"Type inconnu: {zone_type}")
                continue
            
            config = EXCLUSION_CONFIGS[zone_type]
            logger.info(f"\n--- Extraction: {zone_type} ({config['description']}) ---")
            
            for query, query_name in config["queries"]:
                result = self._extract_query(
                    region_id=region_id,
                    bbox=bbox,
                    zone_type=zone_type,
                    query=query,
                    query_name=query_name,
                    cache_data=cache_data
                )
                report.results.append(result)
                report.total_zones += result.geometry_count
        
        # Sauvegarder le cache final
        self._save_cache(region_id, cache_data)
        
        report.end_time = datetime.now(timezone.utc)
        
        # Afficher le rapport
        self._print_report(report)
        
        return report
    
    def _extract_query(
        self,
        region_id: str,
        bbox: List[float],
        zone_type: str,
        query: str,
        query_name: str,
        cache_data: Dict[str, Any]
    ) -> ExtractionResult:
        """Extrait une requête spécifique avec retry automatique."""
        
        # Format bbox pour Overpass: south, west, north, east
        bbox_str = f"{bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]}"
        
        overpass_query = f"""
        [out:json][timeout:{REQUEST_TIMEOUT}];
        (
            {query}({bbox_str});
        );
        out geom;
        """
        
        logger.info(f"  Requête: {query_name}")
        
        # Retry avec backoff exponentiel
        for attempt in range(MAX_RETRIES):
            delay = BASE_DELAY * (BACKOFF_MULTIPLIER ** attempt)
            
            try:
                if attempt > 0:
                    logger.info(f"    Tentative {attempt + 1}/{MAX_RETRIES} après {delay}s...")
                    time.sleep(delay)
                
                response = self._session.post(
                    OVERPASS_URL,
                    data={"data": overpass_query},
                    timeout=REQUEST_TIMEOUT
                )
                
                if response.status_code == 429:
                    logger.warning(f"    Rate limited (429). Attente {delay * 2}s...")
                    time.sleep(delay * 2)
                    continue
                
                if response.status_code != 200:
                    logger.warning(f"    Erreur HTTP: {response.status_code}")
                    continue
                
                data = response.json()
                elements = data.get("elements", [])
                logger.info(f"    Éléments reçus: {len(elements)}")
                
                # Traiter et ajouter au cache
                geometry_count = self._process_elements(
                    elements=elements,
                    zone_type=zone_type,
                    cache_data=cache_data
                )
                
                # Attendre avant la prochaine requête
                time.sleep(BASE_DELAY)
                
                return ExtractionResult(
                    success=True,
                    zone_type=zone_type,
                    query_name=query_name,
                    element_count=len(elements),
                    geometry_count=geometry_count
                )
                
            except requests.exceptions.Timeout:
                logger.warning(f"    Timeout après {REQUEST_TIMEOUT}s")
            except requests.exceptions.RequestException as e:
                logger.warning(f"    Erreur réseau: {e}")
            except json.JSONDecodeError:
                logger.warning("    Erreur JSON invalide")
            except Exception as e:
                logger.error(f"    Erreur inattendue: {e}")
        
        return ExtractionResult(
            success=False,
            zone_type=zone_type,
            query_name=query_name,
            element_count=0,
            geometry_count=0,
            error=f"Échec après {MAX_RETRIES} tentatives"
        )
    
    def _process_elements(
        self,
        elements: List[Dict[str, Any]],
        zone_type: str,
        cache_data: Dict[str, Any]
    ) -> int:
        """Traite les éléments OSM et les ajoute au cache."""
        geometry_count = 0
        
        for element in elements:
            geom = self._element_to_geometry(element)
            if geom is None:
                continue
            
            try:
                zone_entry = {
                    "zone_type": zone_type,
                    "osm_id": str(element.get("id", "")),
                    "name": element.get("tags", {}).get("name"),
                    "tags": element.get("tags", {}),
                    "geometry": mapping(geom)
                }
                cache_data["exclusion_zones"].append(zone_entry)
                geometry_count += 1
            except Exception as e:
                logger.debug(f"Erreur conversion géométrie: {e}")
        
        logger.info(f"    Géométries valides: {geometry_count}")
        return geometry_count
    
    def _element_to_geometry(self, element: Dict[str, Any]) -> Optional[Any]:
        """Convertit un élément OSM en géométrie Shapely."""
        elem_type = element.get("type")
        
        if elem_type == "way":
            geometry_data = element.get("geometry", [])
            if len(geometry_data) >= 3:
                coords = [(g["lon"], g["lat"]) for g in geometry_data]
                try:
                    # Polygone fermé
                    if coords[0] == coords[-1] or (
                        abs(coords[0][0] - coords[-1][0]) < 1e-6 and 
                        abs(coords[0][1] - coords[-1][1]) < 1e-6
                    ):
                        poly = Polygon(coords)
                        if poly.is_valid and poly.area > 0:
                            return poly
                    else:
                        # Ligne (route) - ajouter un buffer de ~15m
                        line = LineString(coords)
                        if line.is_valid:
                            return line.buffer(0.00015)  # ~15m
                except Exception:
                    pass
        
        elif elem_type == "relation":
            members = element.get("members", [])
            polygons = []
            
            for member in members:
                geom_data = member.get("geometry", [])
                if len(geom_data) >= 3:
                    coords = [(g["lon"], g["lat"]) for g in geom_data]
                    try:
                        poly = Polygon(coords)
                        if poly.is_valid and poly.area > 0:
                            polygons.append(poly)
                    except Exception:
                        pass
            
            if polygons:
                return unary_union(polygons)
        
        return None
    
    def _load_or_create_cache(
        self,
        region_id: str,
        region_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Charge ou crée le cache pour une région."""
        cache_file = self.cache_dir / f"{region_id}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                logger.info(f"Cache existant chargé: {len(data.get('exclusion_zones', []))} zones")
                return data
            except Exception as e:
                logger.warning(f"Erreur lecture cache: {e}")
        
        # Créer nouveau cache
        return {
            "region_id": region_id,
            "region_name": region_info["name"],
            "bbox": region_info["bbox"],
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "version": "1.0.0",
            "exclusion_zones": []
        }
    
    def _save_cache(self, region_id: str, cache_data: Dict[str, Any]) -> bool:
        """Sauvegarde le cache sur disque."""
        cache_file = self.cache_dir / f"{region_id}.json"
        
        try:
            cache_data["last_updated"] = datetime.now(timezone.utc).isoformat()
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            logger.info(f"\nCache sauvegardé: {cache_file}")
            logger.info(f"Total zones d'exclusion: {len(cache_data.get('exclusion_zones', []))}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde cache: {e}")
            return False
    
    def _print_report(self, report: RegionExtractionReport) -> None:
        """Affiche le rapport d'extraction."""
        duration = (report.end_time - report.start_time).total_seconds()
        
        logger.info(f"\n{'='*60}")
        logger.info("RAPPORT D'EXTRACTION")
        logger.info(f"{'='*60}")
        logger.info(f"Région: {report.region_name} ({report.region_id})")
        logger.info(f"Durée: {duration:.1f} secondes")
        logger.info(f"Taux de succès: {report.success_rate:.1f}%")
        logger.info(f"Total zones extraites: {report.total_zones}")
        
        logger.info("\nDétail par requête:")
        for result in report.results:
            status = "✓" if result.success else "✗"
            logger.info(f"  {status} {result.zone_type}/{result.query_name}: {result.geometry_count} géométries")
        
        logger.info(f"{'='*60}")
    
    def list_regions(self) -> None:
        """Affiche la liste des régions disponibles."""
        logger.info("\nRÉGIONS DISPONIBLES:")
        logger.info("=" * 60)
        
        by_country = {}
        for region_id, info in PREDEFINED_REGIONS.items():
            country = region_id.split("-")[0]
            if country not in by_country:
                by_country[country] = []
            by_country[country].append((region_id, info["name"]))
        
        for country in sorted(by_country.keys()):
            logger.info(f"\n{country}:")
            for region_id, name in sorted(by_country[country]):
                logger.info(f"  {region_id}: {name}")
    
    def get_cache_status(self, region_id: str) -> Dict[str, Any]:
        """Retourne le statut du cache pour une région."""
        cache_file = self.cache_dir / f"{region_id}.json"
        
        if not cache_file.exists():
            return {"exists": False, "region_id": region_id}
        
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            zones_by_type = {}
            for zone in data.get("exclusion_zones", []):
                zone_type = zone.get("zone_type", "unknown")
                zones_by_type[zone_type] = zones_by_type.get(zone_type, 0) + 1
            
            return {
                "exists": True,
                "region_id": region_id,
                "region_name": data.get("region_name"),
                "last_updated": data.get("last_updated"),
                "total_zones": len(data.get("exclusion_zones", [])),
                "zones_by_type": zones_by_type
            }
        except Exception as e:
            return {"exists": True, "error": str(e), "region_id": region_id}


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """Point d'entrée CLI."""
    parser = argparse.ArgumentParser(
        description="Extracteur de données OSM pour BIONIC V5",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python osm_extractor.py --region CA-QC
  python osm_extractor.py --region CA-QC --types water roads
  python osm_extractor.py --region CA-QC --force
  python osm_extractor.py --list
  python osm_extractor.py --status CA-QC
        """
    )
    
    parser.add_argument(
        "--region", "-r",
        type=str,
        help="ID de la région à extraire (ex: CA-QC, US-NY)"
    )
    
    parser.add_argument(
        "--types", "-t",
        nargs="+",
        choices=list(EXCLUSION_CONFIGS.keys()),
        help="Types d'exclusion à extraire (défaut: tous)"
    )
    
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Force le rafraîchissement même si cache valide"
    )
    
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="Liste toutes les régions disponibles"
    )
    
    parser.add_argument(
        "--status", "-s",
        type=str,
        help="Affiche le statut du cache pour une région"
    )
    
    args = parser.parse_args()
    
    extractor = OSMDataExtractor()
    
    if args.list:
        extractor.list_regions()
        return
    
    if args.status:
        status = extractor.get_cache_status(args.status)
        logger.info(f"\nStatut du cache pour {args.status}:")
        logger.info(json.dumps(status, indent=2, default=str))
        return
    
    if not args.region:
        parser.print_help()
        return
    
    # Exécuter l'extraction
    report = extractor.extract_region(
        region_id=args.region,
        zone_types=args.types,
        force_refresh=args.force
    )
    
    # Code de sortie basé sur le succès
    sys.exit(0 if report.success_rate >= 50 else 1)


if __name__ == "__main__":
    main()
