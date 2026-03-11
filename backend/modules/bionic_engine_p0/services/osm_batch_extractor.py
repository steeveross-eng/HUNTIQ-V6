#!/usr/bin/env python3
"""
BIONIC ENGINE - Batch OSM Extractor
PHASE P1-HOTSPOTS V3 — Extraction Multi-Régions

Script pour extraire les données OSM de plusieurs régions en séquence
avec gestion automatique du rate-limiting.

Usage:
    python osm_batch_extractor.py --regions CA-ON US-NY FR-ARA
    python osm_batch_extractor.py --all

Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
"""

import sys
import json
import time
import logging
import argparse
from datetime import datetime, timezone
from typing import Dict, List, Any

# Ajouter le chemin du backend au PYTHONPATH
sys.path.insert(0, '/app/backend')

from modules.bionic_engine_p0.services.osm_extractor_v2 import (
    OSMSubregionExtractor,
    HUNTING_SUBREGIONS,
    CACHE_DIR
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Délai entre régions pour respecter le rate-limiting
INTER_REGION_DELAY = 60  # 60 secondes entre chaque région parent
INTER_SUBREGION_DELAY = 30  # 30 secondes entre sous-régions


def get_subregions_for_parent(parent_id: str) -> List[str]:
    """Retourne toutes les sous-régions d'un parent."""
    return [
        sub_id for sub_id, info in HUNTING_SUBREGIONS.items()
        if info["parent"] == parent_id
    ]


def merge_subregions_to_parent(extractor: OSMSubregionExtractor, parent_id: str) -> Dict[str, Any]:
    """Fusionne toutes les sous-régions extraites vers le parent."""
    logger.info(f"\n{'='*50}")
    logger.info(f"FUSION vers {parent_id}")
    logger.info(f"{'='*50}")
    
    all_zones = []
    subregions_used = []
    
    for sub_id, sub_info in HUNTING_SUBREGIONS.items():
        if sub_info["parent"] != parent_id:
            continue
        
        cache_file = CACHE_DIR / f"{sub_id}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                
                zones = data.get("exclusion_zones", [])
                all_zones.extend(zones)
                subregions_used.append(sub_id)
                logger.info(f"  {sub_id}: {len(zones)} zones")
            except Exception as e:
                logger.warning(f"  Erreur lecture {sub_id}: {e}")
    
    if not all_zones:
        logger.warning(f"Aucune donnée à fusionner pour {parent_id}")
        return {"success": False, "reason": "No data"}
    
    # Déterminer le bbox parent
    parent_bboxes = {
        "CA-QC": [-79.8, 44.9, -57.1, 62.6],
        "CA-ON": [-95.2, 41.7, -74.3, 56.9],
        "US-NY": [-79.8, 40.5, -71.9, 45.0],
        "FR-ARA": [2.1, 44.1, 7.2, 46.8],
    }
    
    parent_data = {
        "region_id": parent_id,
        "region_name": f"Merged: {parent_id}",
        "bbox": parent_bboxes.get(parent_id, [-180, -90, 180, 90]),
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "version": "2.0.0",
        "subregions_merged": subregions_used,
        "exclusion_zones": all_zones
    }
    
    cache_file = CACHE_DIR / f"{parent_id}.json"
    with open(cache_file, 'w') as f:
        json.dump(parent_data, f)
    
    # Calculer les stats
    zones_by_type = {}
    for z in all_zones:
        zt = z.get("zone_type", "unknown")
        zones_by_type[zt] = zones_by_type.get(zt, 0) + 1
    
    logger.info(f"\nTotal fusionné: {len(all_zones)} zones")
    logger.info(f"Par type: {zones_by_type}")
    logger.info(f"Sauvegardé: {cache_file}")
    
    return {
        "success": True,
        "parent_id": parent_id,
        "total_zones": len(all_zones),
        "zones_by_type": zones_by_type,
        "subregions": subregions_used
    }


def extract_region(parent_id: str) -> Dict[str, Any]:
    """Extrait toutes les sous-régions d'une région parent."""
    logger.info(f"\n{'='*60}")
    logger.info(f"EXTRACTION RÉGION: {parent_id}")
    logger.info(f"{'='*60}")
    
    subregions = get_subregions_for_parent(parent_id)
    
    if not subregions:
        logger.warning(f"Aucune sous-région définie pour {parent_id}")
        return {"success": False, "reason": "No subregions defined"}
    
    logger.info(f"Sous-régions à extraire: {subregions}")
    
    extractor = OSMSubregionExtractor()
    results = []
    
    for i, sub_id in enumerate(subregions):
        logger.info(f"\n--- Sous-région {i+1}/{len(subregions)}: {sub_id} ---")
        
        try:
            result = extractor.extract_subregion(sub_id)
            results.append(result)
            
            # Délai entre sous-régions
            if i < len(subregions) - 1:
                logger.info(f"Attente {INTER_SUBREGION_DELAY}s avant la prochaine sous-région...")
                time.sleep(INTER_SUBREGION_DELAY)
                
        except Exception as e:
            logger.error(f"Erreur extraction {sub_id}: {e}")
            results.append({"success": False, "subregion": sub_id, "error": str(e)})
    
    # Fusionner vers le parent
    merge_result = merge_subregions_to_parent(extractor, parent_id)
    
    return {
        "parent_id": parent_id,
        "subregion_results": results,
        "merge_result": merge_result
    }


def extract_all_regions(regions: List[str]) -> Dict[str, Any]:
    """Extrait plusieurs régions en séquence."""
    logger.info(f"\n{'#'*60}")
    logger.info(f"EXTRACTION BATCH: {len(regions)} régions")
    logger.info(f"{'#'*60}")
    logger.info(f"Régions: {regions}")
    
    start_time = datetime.now(timezone.utc)
    all_results = {}
    
    for i, region in enumerate(regions):
        logger.info(f"\n{'='*60}")
        logger.info(f"RÉGION {i+1}/{len(regions)}: {region}")
        logger.info(f"{'='*60}")
        
        result = extract_region(region)
        all_results[region] = result
        
        # Délai entre régions
        if i < len(regions) - 1:
            logger.info(f"\nAttente {INTER_REGION_DELAY}s avant la prochaine région...")
            time.sleep(INTER_REGION_DELAY)
    
    end_time = datetime.now(timezone.utc)
    duration = (end_time - start_time).total_seconds()
    
    # Rapport final
    logger.info(f"\n{'#'*60}")
    logger.info("RAPPORT FINAL D'EXTRACTION")
    logger.info(f"{'#'*60}")
    logger.info(f"Durée totale: {duration/60:.1f} minutes")
    
    for region, result in all_results.items():
        merge = result.get("merge_result", {})
        status = "✓" if merge.get("success") else "✗"
        zones = merge.get("total_zones", 0)
        logger.info(f"  {status} {region}: {zones} zones")
    
    # Sauvegarder le rapport
    report = {
        "extraction_date": start_time.isoformat(),
        "duration_seconds": duration,
        "regions": all_results
    }
    
    report_file = CACHE_DIR / "extraction_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    logger.info(f"\nRapport sauvegardé: {report_file}")
    
    return report


def list_available_regions():
    """Affiche les régions disponibles."""
    logger.info("\nRÉGIONS DISPONIBLES POUR L'EXTRACTION:")
    logger.info("=" * 50)
    
    parents = {}
    for sub_id, info in HUNTING_SUBREGIONS.items():
        parent = info["parent"]
        if parent not in parents:
            parents[parent] = []
        parents[parent].append((sub_id, info["name"]))
    
    for parent in sorted(parents.keys()):
        logger.info(f"\n{parent}:")
        for sub_id, name in sorted(parents[parent]):
            logger.info(f"  - {sub_id}: {name}")


def get_cache_status():
    """Affiche le statut du cache pour toutes les régions."""
    logger.info("\nSTATUT DU CACHE OSM:")
    logger.info("=" * 50)
    
    parents = set(info["parent"] for info in HUNTING_SUBREGIONS.values())
    
    for parent in sorted(parents):
        cache_file = CACHE_DIR / f"{parent}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                
                zones = len(data.get("exclusion_zones", []))
                updated = data.get("last_updated", "Unknown")
                size_mb = cache_file.stat().st_size / (1024 * 1024)
                
                zones_by_type = {}
                for z in data.get("exclusion_zones", []):
                    zt = z.get("zone_type", "unknown")
                    zones_by_type[zt] = zones_by_type.get(zt, 0) + 1
                
                logger.info(f"\n{parent}:")
                logger.info(f"  Zones: {zones} ({size_mb:.1f} MB)")
                logger.info(f"  Par type: {zones_by_type}")
                logger.info(f"  Mis à jour: {updated}")
            except Exception as e:
                logger.info(f"\n{parent}: Erreur lecture ({e})")
        else:
            logger.info(f"\n{parent}: [VIDE]")


def main():
    parser = argparse.ArgumentParser(
        description="Extraction OSM multi-régions pour BIONIC V5",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
    python osm_batch_extractor.py --regions CA-ON US-NY
    python osm_batch_extractor.py --regions FR-ARA
    python osm_batch_extractor.py --all
    python osm_batch_extractor.py --list
    python osm_batch_extractor.py --status
        """
    )
    
    parser.add_argument(
        "--regions", "-r",
        nargs="+",
        help="Régions à extraire (ex: CA-ON US-NY FR-ARA)"
    )
    
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Extraire toutes les régions disponibles"
    )
    
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="Lister les régions disponibles"
    )
    
    parser.add_argument(
        "--status", "-s",
        action="store_true",
        help="Afficher le statut du cache"
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_available_regions()
        return
    
    if args.status:
        get_cache_status()
        return
    
    if args.all:
        # Extraire toutes les régions uniques
        regions = sorted(set(info["parent"] for info in HUNTING_SUBREGIONS.values()))
        # Exclure CA-QC car déjà extrait
        regions = [r for r in regions if r != "CA-QC"]
        extract_all_regions(regions)
        return
    
    if args.regions:
        extract_all_regions(args.regions)
        return
    
    parser.print_help()


if __name__ == "__main__":
    main()
