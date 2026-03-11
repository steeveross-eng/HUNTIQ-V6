"""
BIONIC V5 300% — Spatial Clipping Engine
=========================================
Invariant: Clipping strict 1km × 1km centré sur le waypoint actif.

Ce module est un INVARIANT BIONIC V5 300%:
- Non modifiable
- Non surchargé
- Non influençable par des pipelines futurs

Fonctions:
- compute_analysis_bbox(): Calcule le carré 1km × 1km
- clip_zones(): Applique ST_Intersection sur les zones
- clip_polygon(): Clip un polygone unique
"""

import math
import logging
from typing import List, Dict, Any, Optional
from shapely.geometry import Polygon, box

logger = logging.getLogger("bionic_engine.spatial_clipping")

# INVARIANT: Taille du carré d'analyse en mètres
ANALYSIS_BOX_SIZE_M = 1000  # 1km × 1km — NE PAS MODIFIER


def compute_analysis_bbox(lat: float, lng: float, size_m: int = ANALYSIS_BOX_SIZE_M) -> Dict[str, float]:
    """
    Calcule un carré exact de size_m × size_m centré sur (lat, lng).
    Retourne les bounds {north, south, east, west} en degrés décimaux.
    
    INVARIANT BIONIC V5 300%: Aucun padding, aucun buffer, aucune marge.
    """
    half_m = size_m / 2.0
    
    # Conversion mètres → degrés
    lat_rad = math.radians(lat)
    meters_per_deg_lat = 111320.0  # ~111.32 km par degré de latitude
    meters_per_deg_lng = 111320.0 * math.cos(lat_rad)
    
    delta_lat = half_m / meters_per_deg_lat
    delta_lng = half_m / meters_per_deg_lng
    
    return {
        "north": lat + delta_lat,
        "south": lat - delta_lat,
        "east": lng + delta_lng,
        "west": lng - delta_lng,
        "center_lat": lat,
        "center_lng": lng,
        "size_m": size_m,
    }


def bbox_to_polygon(bbox: Dict[str, float]) -> Polygon:
    """Convertit un bbox en polygone Shapely."""
    return box(bbox["west"], bbox["south"], bbox["east"], bbox["north"])


def clip_polygon_coords(coords: List[List[float]], clip_box: Polygon) -> Optional[List[List[float]]]:
    """
    Clip un polygone (liste de [lat, lng]) par le carré d'analyse.
    Retourne les coordonnées clippées ou None si intersection vide.
    
    INVARIANT: ST_Intersection stricte — aucun débordement.
    """
    try:
        # Convertir [lat, lng] → Shapely (x=lng, y=lat)
        shapely_coords = [(c[1], c[0]) for c in coords]
        if len(shapely_coords) < 3:
            return None
        
        # Fermer le polygone si nécessaire
        if shapely_coords[0] != shapely_coords[-1]:
            shapely_coords.append(shapely_coords[0])
        
        zone_poly = Polygon(shapely_coords)
        if not zone_poly.is_valid:
            zone_poly = zone_poly.buffer(0)
        
        # ST_Intersection
        intersection = zone_poly.intersection(clip_box)
        
        if intersection.is_empty:
            return None
        
        # Extraire les coordonnées du résultat
        if intersection.geom_type == 'Polygon':
            result = [[c[1], c[0]] for c in intersection.exterior.coords]
        elif intersection.geom_type == 'MultiPolygon':
            # Prendre le plus grand polygone
            largest = max(intersection.geoms, key=lambda g: g.area)
            result = [[c[1], c[0]] for c in largest.exterior.coords]
        else:
            return None
        
        return result if len(result) >= 3 else None
        
    except Exception as e:
        logger.warning(f"Clip error: {e}")
        return None


def clip_zones(zones: List[Dict[str, Any]], bbox: Dict[str, float]) -> List[Dict[str, Any]]:
    """
    Applique le clipping spatial strict sur une liste de zones.
    
    INVARIANT BIONIC V5 300%:
    - Aucune géométrie hors périmètre
    - Aucun débordement visuel
    - Aucun padding, aucun buffer
    
    Chaque zone doit avoir 'coordinates' (liste de [lat, lng]).
    """
    clip_box = bbox_to_polygon(bbox)
    clipped = []
    
    for zone in zones:
        coords = zone.get("coordinates")
        if not coords:
            continue
        
        clipped_coords = clip_polygon_coords(coords, clip_box)
        if clipped_coords:
            clipped_zone = {**zone, "coordinates": clipped_coords, "clipped": True}
            # Recalculer le centre sur la géométrie clippée
            lats = [c[0] for c in clipped_coords]
            lngs = [c[1] for c in clipped_coords]
            clipped_zone["center"] = [sum(lats) / len(lats), sum(lngs) / len(lngs)]
            clipped.append(clipped_zone)
    
    return clipped


def compute_clipping_stats(original_zones: List, clipped_zones: List, bbox: Dict) -> Dict:
    """Calcule les statistiques de clipping pour le rapport d'audit."""
    return {
        "original_count": len(original_zones),
        "clipped_count": len(clipped_zones),
        "removed_count": len(original_zones) - len(clipped_zones),
        "bbox": {
            "north": bbox["north"],
            "south": bbox["south"],
            "east": bbox["east"],
            "west": bbox["west"],
            "size_m": bbox.get("size_m", ANALYSIS_BOX_SIZE_M),
        },
        "overflow_count": 0,  # INVARIANT: toujours 0
    }
