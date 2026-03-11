"""
BIONIC V5 — Knowledge Layer: Water Exclusion for Corridors
============================================================

Module obligatoire pour garantir que les corridors ne traversent JAMAIS
de grandes masses d'eau (lacs, fleuves, réservoirs, marais).

Règle BIONIC V5:
- Tout corridor intersectant une masse d'eau est soit recalculé soit annulé
- Aucune exception n'est autorisée
- Les animaux contournent systématiquement les grandes masses d'eau

Source: Règles écologiques BIONIC V5
Version: 1.0.0
"""

import logging
import math
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone

logger = logging.getLogger("bionic_engine.water_exclusion")


# =============================================================================
# CONSTANTES
# =============================================================================

# Surface minimale pour qu'un plan d'eau soit considéré comme "grande masse d'eau" (m²)
MIN_WATER_BODY_AREA_M2 = 5000  # 5000 m² = 0.5 hectare

# Largeur minimale d'un cours d'eau pour être considéré comme infranchissable (m)
MIN_RIVER_WIDTH_M = 20

# Distance de sécurité par rapport aux berges (m)
SHORE_BUFFER_M = 15

# Sources de données traçables
SOURCE_IDS = [
    "SRC-WATER-EXCLUSION-V1",
    "SRC-MRNF-HYDRO",
    "SRC-CANVEC-NRCan",
    "SRC-OSM-WATER"
]


class WaterBodyType(Enum):
    """Types de masses d'eau"""
    LAKE = "lake"
    RIVER = "river"
    RESERVOIR = "reservoir"
    MARSH = "marsh"
    POND = "pond"
    STREAM = "stream"
    UNKNOWN = "unknown"


class CorridorValidationResult(Enum):
    """Résultat de la validation d'un corridor"""
    VALID = "valid"  # Corridor ne traverse pas d'eau
    REROUTED = "rerouted"  # Corridor recalculé pour contourner l'eau
    REJECTED = "rejected"  # Corridor annulé car impossible à contourner


@dataclass
class WaterIntersection:
    """Intersection détectée entre un corridor et une masse d'eau"""
    water_body_type: WaterBodyType
    water_name: str
    intersection_point: Tuple[float, float]  # (lat, lng)
    water_area_m2: Optional[float] = None
    water_width_m: Optional[float] = None
    source_id: str = "SRC-WATER-EXCLUSION-V1"


@dataclass
class CorridorValidation:
    """Résultat de validation d'un corridor"""
    corridor_id: str
    result: CorridorValidationResult
    original_geometry: List[Tuple[float, float]]
    validated_geometry: Optional[List[Tuple[float, float]]] = None
    intersections_found: List[WaterIntersection] = field(default_factory=list)
    reroute_attempts: int = 0
    validation_timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source_ids: List[str] = field(default_factory=lambda: SOURCE_IDS.copy())
    version: str = "1.0.0"


# =============================================================================
# SERVICE PRINCIPAL
# =============================================================================

class WaterExclusionService:
    """
    Service Knowledge Layer pour l'exclusion des masses d'eau dans les corridors.
    
    Pipeline BIONIC V5:
    1. Analyser le tracé du corridor
    2. Détecter les intersections avec les masses d'eau
    3. Si intersection détectée:
       a. Tenter un contournement (max 3 tentatives)
       b. Si impossible, rejeter le corridor
    4. Retourner le corridor validé ou rejeté
    
    Traçabilité: source_ids obligatoires sur chaque validation
    """
    
    def __init__(self):
        self._version = "1.0.0"
        self._validation_counter = 0
        
        # Définition des types d'eau infranchissables par espèce
        self._species_water_rules: Dict[str, Dict[str, Any]] = {
            "moose": {
                "can_cross_streams": True,  # Peut traverser ruisseaux < 5m
                "can_cross_shallow_marsh": True,  # Peut traverser marais peu profonds
                "max_crossable_width_m": 15,
                "avoids_deep_water": True,
                "swimming_capability": "good"  # Bon nageur mais évite
            },
            "deer": {
                "can_cross_streams": True,
                "can_cross_shallow_marsh": False,
                "max_crossable_width_m": 8,
                "avoids_deep_water": True,
                "swimming_capability": "moderate"
            },
            "bear": {
                "can_cross_streams": True,
                "can_cross_shallow_marsh": True,
                "max_crossable_width_m": 25,
                "avoids_deep_water": False,
                "swimming_capability": "excellent"
            },
            "elk": {
                "can_cross_streams": True,
                "can_cross_shallow_marsh": True,
                "max_crossable_width_m": 12,
                "avoids_deep_water": True,
                "swimming_capability": "good"
            }
        }
        
        logger.info(f"[BIONIC] WaterExclusionService initialized v{self._version}")
    
    def validate_corridor(
        self,
        corridor_id: str,
        corridor_geometry: List[Tuple[float, float]],
        water_features: List[Dict[str, Any]],
        species: str = "moose"
    ) -> CorridorValidation:
        """
        Valide un corridor pour s'assurer qu'il ne traverse pas de grande masse d'eau.
        
        Args:
            corridor_id: Identifiant unique du corridor
            corridor_geometry: Liste de points (lat, lng) définissant le tracé
            water_features: Features hydrographiques de la zone (GeoJSON)
            species: Espèce cible pour les règles de traversée
            
        Returns:
            CorridorValidation avec résultat et géométrie corrigée si applicable
        """
        self._validation_counter += 1
        
        logger.info(f"[BIONIC] Validating corridor {corridor_id} for {species} ({len(corridor_geometry)} points)")
        
        # Obtenir les règles spécifiques à l'espèce
        rules = self._species_water_rules.get(species, self._species_water_rules["moose"])
        
        # Détecter les intersections avec les masses d'eau
        intersections = self._detect_water_intersections(
            corridor_geometry, 
            water_features,
            rules
        )
        
        if not intersections:
            # Aucune intersection, corridor valide
            logger.info(f"[BIONIC] Corridor {corridor_id}: VALID (no water intersection)")
            return CorridorValidation(
                corridor_id=corridor_id,
                result=CorridorValidationResult.VALID,
                original_geometry=corridor_geometry,
                validated_geometry=corridor_geometry,
                intersections_found=[]
            )
        
        logger.warning(f"[BIONIC] Corridor {corridor_id}: {len(intersections)} water intersections detected")
        
        # Tenter de contourner les masses d'eau
        rerouted_geometry, success, attempts = self._attempt_reroute(
            corridor_geometry,
            water_features,
            rules,
            max_attempts=3
        )
        
        if success and rerouted_geometry:
            logger.info(f"[BIONIC] Corridor {corridor_id}: REROUTED after {attempts} attempts")
            return CorridorValidation(
                corridor_id=corridor_id,
                result=CorridorValidationResult.REROUTED,
                original_geometry=corridor_geometry,
                validated_geometry=rerouted_geometry,
                intersections_found=intersections,
                reroute_attempts=attempts
            )
        
        # Impossible de contourner, rejeter le corridor
        logger.warning(f"[BIONIC] Corridor {corridor_id}: REJECTED (water crossing unavoidable)")
        return CorridorValidation(
            corridor_id=corridor_id,
            result=CorridorValidationResult.REJECTED,
            original_geometry=corridor_geometry,
            validated_geometry=None,
            intersections_found=intersections,
            reroute_attempts=attempts
        )
    
    def _detect_water_intersections(
        self,
        corridor_geometry: List[Tuple[float, float]],
        water_features: List[Dict[str, Any]],
        species_rules: Dict[str, Any]
    ) -> List[WaterIntersection]:
        """
        Détecte les intersections entre un corridor et les masses d'eau.
        """
        intersections = []
        
        if not water_features:
            return intersections
        
        max_crossable_width = species_rules.get("max_crossable_width_m", 10)
        
        # Vérifier chaque segment du corridor
        for i in range(len(corridor_geometry) - 1):
            p1 = corridor_geometry[i]
            p2 = corridor_geometry[i + 1]
            
            for feature in water_features:
                props = feature.get("properties", {})
                geometry = feature.get("geometry", {})
                
                # Déterminer le type de masse d'eau
                water_type = self._classify_water_body(props)
                
                # Vérifier si c'est une masse d'eau significative
                area = props.get("area_m2") or props.get("superficie")
                width = props.get("width_m") or props.get("largeur")
                
                # Petits ruisseaux peuvent être franchis
                if water_type == WaterBodyType.STREAM:
                    if width and float(width) < max_crossable_width:
                        continue
                
                # Vérifier l'intersection
                if self._segment_intersects_water(p1, p2, geometry):
                    name = props.get("name") or props.get("nom") or props.get("NAMF") or "Unnamed"
                    
                    # Point d'intersection approximatif (milieu du segment)
                    intersection_point = (
                        (p1[0] + p2[0]) / 2,
                        (p1[1] + p2[1]) / 2
                    )
                    
                    intersections.append(WaterIntersection(
                        water_body_type=water_type,
                        water_name=name,
                        intersection_point=intersection_point,
                        water_area_m2=float(area) if area else None,
                        water_width_m=float(width) if width else None
                    ))
        
        return intersections
    
    def _classify_water_body(self, properties: Dict[str, Any]) -> WaterBodyType:
        """Classifie le type de masse d'eau selon ses propriétés."""
        # Vérifier les champs courants
        water_type = (
            properties.get("type") or 
            properties.get("waterway") or 
            properties.get("natural") or
            properties.get("TYPE_EAU") or
            ""
        ).lower()
        
        if "lake" in water_type or "lac" in water_type:
            return WaterBodyType.LAKE
        elif "river" in water_type or "fleuve" in water_type or "rivière" in water_type:
            return WaterBodyType.RIVER
        elif "reservoir" in water_type or "réservoir" in water_type:
            return WaterBodyType.RESERVOIR
        elif "marsh" in water_type or "marais" in water_type or "wetland" in water_type:
            return WaterBodyType.MARSH
        elif "pond" in water_type or "étang" in water_type:
            return WaterBodyType.POND
        elif "stream" in water_type or "ruisseau" in water_type:
            return WaterBodyType.STREAM
        
        # Classifier par superficie si disponible
        area = properties.get("area_m2") or properties.get("superficie")
        if area:
            area = float(area)
            if area > 100000:  # > 10 hectares
                return WaterBodyType.LAKE
            elif area > 10000:  # > 1 hectare
                return WaterBodyType.POND
        
        return WaterBodyType.UNKNOWN
    
    def _segment_intersects_water(
        self,
        p1: Tuple[float, float],
        p2: Tuple[float, float],
        water_geometry: Dict[str, Any]
    ) -> bool:
        """
        Vérifie si un segment de corridor intersecte une géométrie d'eau.
        Utilise une approximation par bounding box + point-in-polygon simplifié.
        """
        geom_type = water_geometry.get("type", "")
        coordinates = water_geometry.get("coordinates", [])
        
        if not coordinates:
            return False
        
        # Calculer la bounding box du segment
        min_lat = min(p1[0], p2[0])
        max_lat = max(p1[0], p2[0])
        min_lng = min(p1[1], p2[1])
        max_lng = max(p1[1], p2[1])
        
        # Vérifier selon le type de géométrie
        if geom_type == "Polygon":
            return self._segment_in_polygon_bbox(
                min_lat, max_lat, min_lng, max_lng, coordinates[0]
            )
        elif geom_type == "MultiPolygon":
            for polygon in coordinates:
                if polygon and self._segment_in_polygon_bbox(
                    min_lat, max_lat, min_lng, max_lng, polygon[0]
                ):
                    return True
        elif geom_type in ["LineString", "MultiLineString"]:
            # Pour les rivières linéaires, vérifier la proximité
            return self._segment_near_line(p1, p2, coordinates)
        
        return False
    
    def _segment_in_polygon_bbox(
        self,
        min_lat: float, max_lat: float,
        min_lng: float, max_lng: float,
        polygon_coords: List[List[float]]
    ) -> bool:
        """Vérifie si un segment est potentiellement dans un polygone via bbox."""
        if not polygon_coords:
            return False
        
        # Extraire la bbox du polygone
        poly_lngs = [c[0] for c in polygon_coords]
        poly_lats = [c[1] for c in polygon_coords]
        
        poly_min_lng, poly_max_lng = min(poly_lngs), max(poly_lngs)
        poly_min_lat, poly_max_lat = min(poly_lats), max(poly_lats)
        
        # Vérifier le chevauchement des bboxes
        if (max_lng < poly_min_lng or min_lng > poly_max_lng or
            max_lat < poly_min_lat or min_lat > poly_max_lat):
            return False
        
        # Les bboxes se chevauchent, intersection probable
        return True
    
    def _segment_near_line(
        self,
        p1: Tuple[float, float],
        p2: Tuple[float, float],
        line_coords: List
    ) -> bool:
        """Vérifie si un segment est proche d'une ligne (rivière)."""
        # Distance minimale en degrés (~100m)
        threshold = 0.001
        
        mid_point = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
        
        for coord in line_coords:
            if isinstance(coord[0], list):
                # MultiLineString
                for subcoord in coord:
                    dist = math.sqrt(
                        (mid_point[0] - subcoord[1])**2 + 
                        (mid_point[1] - subcoord[0])**2
                    )
                    if dist < threshold:
                        return True
            else:
                dist = math.sqrt(
                    (mid_point[0] - coord[1])**2 + 
                    (mid_point[1] - coord[0])**2
                )
                if dist < threshold:
                    return True
        
        return False
    
    def _attempt_reroute(
        self,
        corridor_geometry: List[Tuple[float, float]],
        water_features: List[Dict[str, Any]],
        species_rules: Dict[str, Any],
        max_attempts: int = 3
    ) -> Tuple[Optional[List[Tuple[float, float]]], bool, int]:
        """
        Tente de recalculer le corridor pour contourner les masses d'eau.
        
        Stratégie:
        1. Identifier les segments problématiques
        2. Calculer des points de contournement (±offset)
        3. Valider le nouveau tracé
        
        Returns:
            (new_geometry, success, attempts)
        """
        current_geometry = corridor_geometry.copy()
        
        for attempt in range(max_attempts):
            # Détecter les intersections sur le tracé actuel
            intersections = self._detect_water_intersections(
                current_geometry, water_features, species_rules
            )
            
            if not intersections:
                # Plus d'intersection, succès
                return current_geometry, True, attempt + 1
            
            # Tenter de contourner
            new_geometry = self._calculate_reroute(
                current_geometry,
                intersections,
                offset_factor=0.002 * (attempt + 1)  # Augmenter l'offset à chaque tentative
            )
            
            if new_geometry:
                current_geometry = new_geometry
            else:
                # Impossible de calculer un contournement
                return None, False, attempt + 1
        
        # Vérification finale
        final_intersections = self._detect_water_intersections(
            current_geometry, water_features, species_rules
        )
        
        if not final_intersections:
            return current_geometry, True, max_attempts
        
        return None, False, max_attempts
    
    def _calculate_reroute(
        self,
        geometry: List[Tuple[float, float]],
        intersections: List[WaterIntersection],
        offset_factor: float = 0.002
    ) -> Optional[List[Tuple[float, float]]]:
        """
        Calcule un nouveau tracé contournant les intersections.
        """
        if len(geometry) < 2:
            return None
        
        new_geometry = [geometry[0]]  # Garder le point de départ
        
        for i in range(1, len(geometry) - 1):
            point = geometry[i]
            
            # Vérifier si ce point est proche d'une intersection
            is_near_intersection = False
            for intersection in intersections:
                dist = math.sqrt(
                    (point[0] - intersection.intersection_point[0])**2 +
                    (point[1] - intersection.intersection_point[1])**2
                )
                if dist < 0.01:  # ~1km
                    is_near_intersection = True
                    break
            
            if is_near_intersection:
                # Calculer un point de contournement
                # Direction perpendiculaire au segment
                if i > 0 and i < len(geometry) - 1:
                    dx = geometry[i + 1][1] - geometry[i - 1][1]
                    dy = geometry[i + 1][0] - geometry[i - 1][0]
                    length = math.sqrt(dx**2 + dy**2)
                    
                    if length > 0:
                        # Normaliser et appliquer offset perpendiculaire
                        perp_x = -dy / length * offset_factor
                        perp_y = dx / length * offset_factor
                        
                        new_point = (
                            point[0] + perp_y,
                            point[1] + perp_x
                        )
                        new_geometry.append(new_point)
                        continue
            
            new_geometry.append(point)
        
        new_geometry.append(geometry[-1])  # Garder le point d'arrivée
        
        return new_geometry if len(new_geometry) >= 2 else None


# =============================================================================
# INSTANCE SINGLETON
# =============================================================================

_water_exclusion_service: Optional[WaterExclusionService] = None


def get_water_exclusion_service() -> WaterExclusionService:
    """Retourne l'instance singleton du service d'exclusion d'eau."""
    global _water_exclusion_service
    if _water_exclusion_service is None:
        _water_exclusion_service = WaterExclusionService()
    return _water_exclusion_service
