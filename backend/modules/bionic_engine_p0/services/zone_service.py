# ══════════════════════════════════════════════════════════════
# LEGACY FIGÉ — NE PAS MODIFIER
# Remplacé par: pipeline_v7.py / zone_engine_core_v2.py / osm_extractor_v2.py
# Date gel: 2026-03-10
# ══════════════════════════════════════════════════════════════
"""
BIONIC ENGINE - Zone Service
PHASE G - P1-HOTSPOTS

Service de generation des zones comportementales.
Consomme les outputs P0-STABLE pour generer des zones 200% realistes.

Conformite: G-SEC | G-QA | G-DOC | BIONIC V5
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import logging
import math

from modules.bionic_engine_p0.modules.predictive_territorial import PredictiveTerritorialService
from modules.bionic_engine_p0.modules.behavioral_models import BehavioralModelsService
from modules.bionic_engine_p0.contracts.data_contracts import Species
from modules.bionic_engine_p0.services.contour_generator import (
    ContourGenerator,
    generate_id,
    create_zone_style
)

logger = logging.getLogger("bionic_engine.zone_service")


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class BoundsInput(BaseModel):
    north: float = Field(..., ge=-90, le=90)
    south: float = Field(..., ge=-90, le=90)
    east: float = Field(..., ge=-180, le=180)
    west: float = Field(..., ge=-180, le=180)


class ZoneRequest(BaseModel):
    bounds: BoundsInput
    species: str = "moose"
    zone_types: List[str] = ["feeding", "bedding", "rut_arena", "water_access"]
    datetime: Optional[str] = None
    include_overlaps: bool = True


class ZoneStyle(BaseModel):
    stroke_color: str
    stroke_width: float = 1.5
    stroke_dasharray: str = "none"
    fill_opacity: float = 0  # TOUJOURS 0


class BehaviorContext(BaseModel):
    primary_activity: str
    time_of_day: List[str]
    seasonal_relevance: List[int]
    species_affinity: Dict[str, float]


class Zone(BaseModel):
    id: str
    type: str
    geometry: Dict[str, Any]
    behavior_context: BehaviorContext
    overlap_zones: List[str] = []
    style: ZoneStyle


class ZoneResponse(BaseModel):
    success: bool
    zones: List[Zone]
    overlap_matrix: Dict[str, List[str]]
    metadata: Dict[str, Any]


# =============================================================================
# ZONE SERVICE
# =============================================================================

class ZoneService:
    """
    Service de generation de zones comportementales.
    
    Types de zones:
    - feeding: Zones d'alimentation
    - bedding: Zones de repos
    - rut_arena: Arenes de rut
    - thermal_cover: Couvert thermique
    - water_access: Acces a l'eau
    - predation_zone: Zones de predation
    - yarding_zone: Ravages hivernaux
    """
    
    def __init__(self):
        self._pt_service = PredictiveTerritorialService()
        self._bm_service = BehavioralModelsService()
        self._contour_gen = ContourGenerator()
    
    def generate_zones(self, request: ZoneRequest) -> ZoneResponse:
        """
        Genere les zones comportementales pour une zone geographique.
        
        Args:
            request: Parametres de requete
            
        Returns:
            ZoneResponse avec liste de zones
        """
        start_time = datetime.now(timezone.utc)
        
        # Parser datetime
        if request.datetime:
            base_datetime = datetime.fromisoformat(request.datetime.replace('Z', '+00:00'))
        else:
            base_datetime = datetime.now(timezone.utc)
        
        # Convertir species
        try:
            species = Species(request.species)
        except ValueError:
            species = Species.MOOSE
        
        zones = []
        
        # Generer points strategiques dans les bounds
        strategic_points = self._find_strategic_points(
            request.bounds,
            species,
            base_datetime,
            num_points=6
        )
        
        # Pour chaque type de zone demande
        for zone_type in request.zone_types:
            zone_points = self._select_points_for_zone_type(
                strategic_points,
                zone_type,
                max_zones=3
            )
            
            for point_data in zone_points:
                zone = self._create_zone(
                    zone_type=zone_type,
                    lat=point_data["lat"],
                    lng=point_data["lng"],
                    species=request.species,
                    factors=point_data.get("factors", {}),
                    base_datetime=base_datetime
                )
                zones.append(zone)
        
        # Calculer la matrice de superposition
        overlap_matrix = {}
        if request.include_overlaps:
            overlap_matrix = self._calculate_overlaps(zones)
            # Mettre a jour les zones avec leurs chevauchements
            for zone in zones:
                zone.overlap_zones = overlap_matrix.get(zone.id, [])
        
        calc_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        
        return ZoneResponse(
            success=True,
            zones=zones,
            overlap_matrix=overlap_matrix,
            metadata={
                "calculation_time_ms": round(calc_time, 1),
                "species": request.species,
                "zone_count": len(zones),
                "version": "P1-HOTSPOTS-1.0"
            }
        )
    
    def _find_strategic_points(
        self,
        bounds: BoundsInput,
        species: Species,
        base_datetime: datetime,
        num_points: int = 6
    ) -> List[Dict]:
        """Trouve les points strategiques dans la zone."""
        points = []
        
        # Generer une grille
        grid_size = int(math.sqrt(num_points * 2))
        lat_step = (bounds.north - bounds.south) / grid_size
        lng_step = (bounds.east - bounds.west) / grid_size
        
        for i in range(grid_size):
            for j in range(grid_size):
                lat = bounds.south + (i + 0.5) * lat_step
                lng = bounds.west + (j + 0.5) * lng_step
                
                # Calculer score P0
                result = self._pt_service.calculate_score(
                    latitude=lat,
                    longitude=lng,
                    species=species,
                    datetime_target=base_datetime,
                    include_advanced_factors=True
                )
                
                if result.success and result.overall_score >= 60:
                    points.append({
                        "lat": lat,
                        "lng": lng,
                        "score": result.overall_score,
                        "factors": result.metadata.get("advanced_factors", {}),
                        "factor_scores": result.metadata.get("advanced_factor_scores", {})
                    })
        
        # Trier par score et prendre les meilleurs
        points.sort(key=lambda p: p["score"], reverse=True)
        return points[:num_points]
    
    def _select_points_for_zone_type(
        self,
        points: List[Dict],
        zone_type: str,
        max_zones: int = 3
    ) -> List[Dict]:
        """Selectionne les points adaptes a un type de zone."""
        
        # Criteres par type
        type_criteria = {
            "feeding": lambda p: p.get("factor_scores", {}).get("digestive", 0) > 50,
            "bedding": lambda p: p.get("factor_scores", {}).get("thermal_stress", 0) < 30,
            "rut_arena": lambda p: p.get("factor_scores", {}).get("hormonal", 0) > 60,
            "thermal_cover": lambda p: True,
            "water_access": lambda p: p.get("factor_scores", {}).get("hydric_stress", 0) < 40,
            "predation_zone": lambda p: p.get("factor_scores", {}).get("predation", 0) > 50,
            "yarding_zone": lambda p: p.get("factor_scores", {}).get("snow", 0) > 40
        }
        
        criteria = type_criteria.get(zone_type, lambda p: True)
        
        # Filtrer et selectionner
        valid_points = [p for p in points if criteria(p)]
        
        # Si pas assez de points valides, prendre les meilleurs scores
        if len(valid_points) < max_zones:
            valid_points = points[:max_zones]
        
        return valid_points[:max_zones]
    
    def _create_zone(
        self,
        zone_type: str,
        lat: float,
        lng: float,
        species: str,
        factors: Dict,
        base_datetime: datetime
    ) -> Zone:
        """Cree une zone comportementale."""
        
        # Contexte comportemental par type
        context_map = {
            "feeding": BehaviorContext(
                primary_activity="browsing",
                time_of_day=["dawn", "dusk"],
                seasonal_relevance=[9, 10, 11],
                species_affinity={species: 0.9}
            ),
            "bedding": BehaviorContext(
                primary_activity="resting",
                time_of_day=["midday", "night"],
                seasonal_relevance=list(range(1, 13)),
                species_affinity={species: 0.85}
            ),
            "rut_arena": BehaviorContext(
                primary_activity="mating",
                time_of_day=["dawn", "dusk", "night"],
                seasonal_relevance=[9, 10, 11],
                species_affinity={species: 0.95}
            ),
            "thermal_cover": BehaviorContext(
                primary_activity="thermoregulation",
                time_of_day=["midday"] if base_datetime.month in [6,7,8] else ["all"],
                seasonal_relevance=[1, 2, 6, 7, 8, 12],
                species_affinity={species: 0.8}
            ),
            "water_access": BehaviorContext(
                primary_activity="drinking",
                time_of_day=["dawn", "midday", "dusk"],
                seasonal_relevance=[5, 6, 7, 8, 9],
                species_affinity={species: 0.75}
            ),
            "predation_zone": BehaviorContext(
                primary_activity="vigilance",
                time_of_day=["dawn", "dusk"],
                seasonal_relevance=list(range(1, 13)),
                species_affinity={species: 0.7}
            ),
            "yarding_zone": BehaviorContext(
                primary_activity="survival",
                time_of_day=["all"],
                seasonal_relevance=[12, 1, 2, 3],
                species_affinity={species: 0.9}
            )
        }
        
        behavior_context = context_map.get(zone_type, BehaviorContext(
            primary_activity="general",
            time_of_day=["all"],
            seasonal_relevance=list(range(1, 13)),
            species_affinity={species: 0.8}
        ))
        
        # Generer geometrie naturelle
        geometry = self._contour_gen.generate_zone_geometry(
            center_lat=lat,
            center_lng=lng,
            zone_type=zone_type,
            size_factor=1.0
        )
        
        return Zone(
            id=generate_id("ZN"),
            type=zone_type,
            geometry=geometry,
            behavior_context=behavior_context,
            overlap_zones=[],
            style=ZoneStyle(**create_zone_style(zone_type))
        )
    
    def _calculate_overlaps(self, zones: List[Zone]) -> Dict[str, List[str]]:
        """Calcule les chevauchements entre zones."""
        overlap_matrix = {}
        
        for zone in zones:
            overlap_matrix[zone.id] = []
        
        # Verifier les chevauchements simples (proximite des centres)
        for i, zone1 in enumerate(zones):
            center1 = self._get_zone_center(zone1.geometry)
            
            for j, zone2 in enumerate(zones):
                if i >= j:
                    continue
                
                center2 = self._get_zone_center(zone2.geometry)
                
                # Distance entre centres
                dist = math.sqrt(
                    (center1[0] - center2[0]) ** 2 +
                    (center1[1] - center2[1]) ** 2
                )
                
                # Si proches, considerer comme chevauchement
                if dist < 0.02:  # ~2km
                    overlap_matrix[zone1.id].append(zone2.id)
                    overlap_matrix[zone2.id].append(zone1.id)
        
        return overlap_matrix
    
    def _get_zone_center(self, geometry: Dict) -> tuple:
        """Calcule le centre approximatif d'une geometrie."""
        coords = geometry.get("coordinates", [[]])[0]
        if not coords:
            return (0, 0)
        
        lngs = [c[0] for c in coords]
        lats = [c[1] for c in coords]
        
        return (sum(lngs) / len(lngs), sum(lats) / len(lats))
