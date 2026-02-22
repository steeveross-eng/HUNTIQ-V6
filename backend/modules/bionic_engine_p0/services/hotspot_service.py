"""
BIONIC ENGINE - Hotspot Service
PHASE G - P1-HOTSPOTS

Service de generation des hotspots cartographiques.
Consomme les outputs P0-STABLE pour generer des hotspots 200% realistes.

Conformite: G-SEC | G-QA | G-DOC | BIONIC V5
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, Field
import logging

from modules.bionic_engine_p0.modules.predictive_territorial import PredictiveTerritorialService
from modules.bionic_engine_p0.modules.behavioral_models import BehavioralModelsService
from modules.bionic_engine_p0.contracts.data_contracts import Species
from modules.bionic_engine_p0.services.contour_generator import (
    ContourGenerator,
    generate_id,
    create_hotspot_style,
    HOTSPOT_COLORS,
    SPECIES_COLORS,
    calculate_polygon_area_m2
)

logger = logging.getLogger("bionic_engine.hotspot_service")


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class BoundsInput(BaseModel):
    north: float = Field(..., ge=-90, le=90)
    south: float = Field(..., ge=-90, le=90)
    east: float = Field(..., ge=-180, le=180)
    west: float = Field(..., ge=-180, le=180)


class UserWaypoint(BaseModel):
    id: str
    latitude: float
    longitude: float


class HotspotRequest(BaseModel):
    bounds: BoundsInput
    species: List[str] = ["moose"]
    time_range: str = "24h"
    hotspot_types: List[str] = ["activity_peak", "feeding_zone", "rut_zone"]
    datetime_start: Optional[str] = None
    min_score_threshold: int = 70
    include_waypoints: bool = False
    user_waypoints: List[UserWaypoint] = []


class HotspotStyle(BaseModel):
    stroke_color: str
    stroke_width: float = 1.5
    fill_opacity: float = 0  # TOUJOURS 0


class TimeValidity(BaseModel):
    start: str
    end: str
    optimal_hours: List[int] = []


class HotspotMetadata(BaseModel):
    source_factor: str
    factor_score: float
    dominant_behavior: str
    generated_at: str


class Hotspot(BaseModel):
    id: str
    type: str
    geometry: Dict[str, Any]
    score: float
    confidence: float
    time_validity: TimeValidity
    species: List[str]
    style: HotspotStyle
    metadata: HotspotMetadata


class HotspotStatistics(BaseModel):
    total_hotspots: int
    by_type: Dict[str, int]
    avg_score: float
    coverage_km2: float


class HotspotResponse(BaseModel):
    success: bool
    hotspots: List[Hotspot]
    statistics: HotspotStatistics
    metadata: Dict[str, Any]


# =============================================================================
# HOTSPOT SERVICE
# =============================================================================

class HotspotService:
    """
    Service de generation de hotspots.
    
    Consomme passivement les outputs de P0-STABLE:
    - PredictiveTerritorialService (scores, 12 facteurs)
    - BehavioralModelsService (timelines, comportements)
    
    Genere des hotspots conformes aux specifications visuelles:
    - Contours 1-2px, centre transparent
    - Formes naturelles (Chaikin)
    - ZERO fill, ZERO effets
    """
    
    def __init__(self):
        self._pt_service = PredictiveTerritorialService()
        self._bm_service = BehavioralModelsService()
        self._contour_gen = ContourGenerator()
    
    def generate_hotspots(self, request: HotspotRequest) -> HotspotResponse:
        """
        Genere les hotspots pour une zone et periode.
        
        Args:
            request: Parametres de requete
            
        Returns:
            HotspotResponse avec liste de hotspots
        """
        start_time = datetime.now(timezone.utc)
        
        # Parser datetime
        if request.datetime_start:
            base_datetime = datetime.fromisoformat(request.datetime_start.replace('Z', '+00:00'))
        else:
            base_datetime = datetime.now(timezone.utc)
        
        # Calculer la fin selon time_range
        time_range_hours = {"24h": 24, "72h": 72, "7d": 168}
        hours = time_range_hours.get(request.time_range, 24)
        end_datetime = base_datetime + timedelta(hours=hours)
        
        hotspots = []
        
        # Generer grille de points dans les bounds
        grid_points = self._generate_grid(request.bounds, resolution=8)
        
        # Pour chaque espece demandee
        for species_str in request.species:
            try:
                species = Species(species_str)
            except ValueError:
                continue
            
            # Pour chaque point de la grille
            for lat, lng in grid_points:
                # Calculer le score P0
                score_result = self._pt_service.calculate_score(
                    latitude=lat,
                    longitude=lng,
                    species=species,
                    datetime_target=base_datetime,
                    include_advanced_factors=True
                )
                
                if not score_result.success:
                    continue
                
                # Extraire les facteurs avances
                advanced_factors = score_result.metadata.get("advanced_factors", {})
                factor_scores = score_result.metadata.get("advanced_factor_scores", {})
                
                # Generer hotspots selon les types demandes
                for hotspot_type in request.hotspot_types:
                    hotspot = self._create_hotspot_from_factors(
                        hotspot_type=hotspot_type,
                        lat=lat,
                        lng=lng,
                        species=species_str,
                        score_result=score_result,
                        advanced_factors=advanced_factors,
                        factor_scores=factor_scores,
                        base_datetime=base_datetime,
                        end_datetime=end_datetime,
                        min_threshold=request.min_score_threshold
                    )
                    
                    if hotspot:
                        hotspots.append(hotspot)
        
        # Ajouter hotspots personnalises par waypoints utilisateur
        if request.include_waypoints and request.user_waypoints:
            for wp in request.user_waypoints:
                for species_str in request.species:
                    try:
                        species = Species(species_str)
                        wp_hotspot = self._create_waypoint_hotspot(
                            waypoint=wp,
                            species=species,
                            base_datetime=base_datetime,
                            end_datetime=end_datetime
                        )
                        if wp_hotspot:
                            hotspots.append(wp_hotspot)
                    except ValueError:
                        continue
        
        # Calculer statistiques
        by_type = {}
        total_score = 0
        for hs in hotspots:
            by_type[hs.type] = by_type.get(hs.type, 0) + 1
            total_score += hs.score
        
        avg_score = total_score / len(hotspots) if hotspots else 0
        
        # Estimation couverture
        coverage_km2 = self._estimate_coverage(request.bounds)
        
        calc_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        
        return HotspotResponse(
            success=True,
            hotspots=hotspots,
            statistics=HotspotStatistics(
                total_hotspots=len(hotspots),
                by_type=by_type,
                avg_score=round(avg_score, 1),
                coverage_km2=round(coverage_km2, 2)
            ),
            metadata={
                "calculation_time_ms": round(calc_time, 1),
                "grid_resolution": 8,
                "contour_algorithm": "marching_squares_chaikin",
                "version": "P1-HOTSPOTS-1.0"
            }
        )
    
    def _generate_grid(
        self,
        bounds: BoundsInput,
        resolution: int = 8
    ) -> List[tuple]:
        """Genere une grille de points dans les bounds."""
        points = []
        lat_step = (bounds.north - bounds.south) / resolution
        lng_step = (bounds.east - bounds.west) / resolution
        
        for i in range(resolution):
            for j in range(resolution):
                lat = bounds.south + (i + 0.5) * lat_step
                lng = bounds.west + (j + 0.5) * lng_step
                points.append((lat, lng))
        
        return points
    
    def _create_hotspot_from_factors(
        self,
        hotspot_type: str,
        lat: float,
        lng: float,
        species: str,
        score_result: Any,
        advanced_factors: Dict,
        factor_scores: Dict,
        base_datetime: datetime,
        end_datetime: datetime,
        min_threshold: int
    ) -> Optional[Hotspot]:
        """Cree un hotspot si le facteur correspondant depasse le seuil."""
        
        # Mapper type de hotspot vers facteur P0
        type_to_factor = {
            "activity_peak": ("overall", score_result.overall_score),
            "feeding_zone": ("digestive", factor_scores.get("digestive", 0)),
            "rut_zone": ("hormonal", factor_scores.get("hormonal", 0)),
            "thermal_refuge": ("thermal_stress", 100 - factor_scores.get("thermal_stress", 0)),
            "water_source": ("hydric_stress", 100 - factor_scores.get("hydric_stress", 0)),
            "predation_risk": ("predation", factor_scores.get("predation", 0)),
            "snow_impact": ("snow", factor_scores.get("snow", 0)),
            "human_avoidance": ("human_disturbance", 100 - factor_scores.get("human_disturbance", 0)),
            "mineral_site": ("mineral", factor_scores.get("mineral", 0)),
            "composite_optimal": ("overall", score_result.overall_score)
        }
        
        factor_name, score = type_to_factor.get(hotspot_type, ("overall", 0))
        
        if score < min_threshold:
            return None
        
        # Determiner heures optimales
        optimal_hours = []
        if hotspot_type in ["activity_peak", "feeding_zone"]:
            optimal_hours = [6, 7, 8, 17, 18, 19]
        elif hotspot_type == "rut_zone":
            optimal_hours = [5, 6, 7, 8, 16, 17, 18, 19]
        
        # Comportement dominant
        dominant_behavior = "normal"
        hormonal = advanced_factors.get("hormonal", {})
        if hormonal.get("phase") == "rut_peak":
            dominant_behavior = "rut_seeking"
        elif advanced_factors.get("digestive", {}).get("phase") == "active_feeding":
            dominant_behavior = "feeding"
        
        # Generer geometrie naturelle
        geometry = self._contour_gen.generate_hotspot_geometry(
            center_lat=lat,
            center_lng=lng,
            score=score,
            hotspot_type=hotspot_type
        )
        
        return Hotspot(
            id=generate_id("HS"),
            type=hotspot_type,
            geometry=geometry,
            score=round(score, 1),
            confidence=round(score_result.confidence, 2),
            time_validity=TimeValidity(
                start=base_datetime.isoformat(),
                end=end_datetime.isoformat(),
                optimal_hours=optimal_hours
            ),
            species=[species],
            style=HotspotStyle(**create_hotspot_style(hotspot_type)),
            metadata=HotspotMetadata(
                source_factor=factor_name,
                factor_score=round(score, 1),
                dominant_behavior=dominant_behavior,
                generated_at=datetime.now(timezone.utc).isoformat()
            )
        )
    
    def _create_waypoint_hotspot(
        self,
        waypoint: UserWaypoint,
        species: Species,
        base_datetime: datetime,
        end_datetime: datetime
    ) -> Optional[Hotspot]:
        """Cree un hotspot personnalise autour d'un waypoint utilisateur."""
        
        score_result = self._pt_service.calculate_score(
            latitude=waypoint.latitude,
            longitude=waypoint.longitude,
            species=species,
            datetime_target=base_datetime,
            include_advanced_factors=True
        )
        
        if not score_result.success or score_result.overall_score < 50:
            return None
        
        geometry = self._contour_gen.generate_hotspot_geometry(
            center_lat=waypoint.latitude,
            center_lng=waypoint.longitude,
            score=score_result.overall_score,
            hotspot_type="composite_optimal"
        )
        
        return Hotspot(
            id=generate_id("HS"),
            type="composite_optimal",
            geometry=geometry,
            score=round(score_result.overall_score, 1),
            confidence=round(score_result.confidence, 2),
            time_validity=TimeValidity(
                start=base_datetime.isoformat(),
                end=end_datetime.isoformat(),
                optimal_hours=[6, 7, 8, 17, 18, 19]
            ),
            species=[species.value],
            style=HotspotStyle(**create_hotspot_style("composite_optimal")),
            metadata=HotspotMetadata(
                source_factor="user_waypoint",
                factor_score=round(score_result.overall_score, 1),
                dominant_behavior="custom",
                generated_at=datetime.now(timezone.utc).isoformat()
            )
        )
    
    def _estimate_coverage(self, bounds: BoundsInput) -> float:
        """Estime la couverture en km2."""
        lat_diff = bounds.north - bounds.south
        lng_diff = bounds.east - bounds.west
        
        # Approximation: 1 degre lat ~ 111km, 1 degre lng ~ 111km * cos(lat)
        avg_lat = (bounds.north + bounds.south) / 2
        lat_km = lat_diff * 111
        lng_km = lng_diff * 111 * abs(math.cos(math.radians(avg_lat)))
        
        return lat_km * lng_km


import math
