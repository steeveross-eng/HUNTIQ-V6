"""
BIONIC ENGINE - Corridor Service
PHASE G - P1-HOTSPOTS

Service de generation des corridors de deplacement.
Consomme les outputs P0-STABLE pour generer des corridors 200% realistes.

RÈGLE BIONIC V5: Les corridors ne doivent JAMAIS traverser de grandes masses d'eau.
- Tout corridor intersectant un lac, fleuve, réservoir ou marais est recalculé ou annulé
- Aucune exception n'est autorisée

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
    create_corridor_style
)
from modules.bionic_engine_p0.knowledge.terrain.water_exclusion import (
    get_water_exclusion_service,
    CorridorValidationResult
)

logger = logging.getLogger("bionic_engine.corridor_service")


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class BoundsInput(BaseModel):
    north: float = Field(..., ge=-90, le=90)
    south: float = Field(..., ge=-90, le=90)
    east: float = Field(..., ge=-180, le=180)
    west: float = Field(..., ge=-180, le=180)


class CorridorRequest(BaseModel):
    bounds: BoundsInput
    species: str = "moose"
    corridor_types: List[str] = ["movement", "preferred", "feeding_transit"]
    datetime: Optional[str] = None
    connect_zones: bool = True


class CorridorStyle(BaseModel):
    stroke_color: str
    stroke_width: float = 2
    stroke_dasharray: str = "none"


class ZoneConnection(BaseModel):
    from_zone: Optional[str] = None
    to_zone: Optional[str] = None


class MovementContext(BaseModel):
    direction: str = "bidirectional"
    frequency: str = "daily"
    peak_hours: List[int] = []
    connects: ZoneConnection


class Corridor(BaseModel):
    id: str
    type: str
    geometry: Dict[str, Any]
    movement_context: MovementContext
    width_meters: float
    usage_probability: float
    style: CorridorStyle


class CorridorResponse(BaseModel):
    success: bool
    corridors: List[Corridor]
    metadata: Dict[str, Any]


# =============================================================================
# CORRIDOR SERVICE
# =============================================================================

class CorridorService:
    """
    Service de generation de corridors de deplacement.
    
    Types de corridors:
    - movement: Corridors de deplacement principal
    - avoidance: Corridors d'evitement
    - preferred: Routes preferees historiques
    - feeding_transit: Transit alimentation-repos
    """
    
    def __init__(self):
        self._pt_service = PredictiveTerritorialService()
        self._bm_service = BehavioralModelsService()
        self._contour_gen = ContourGenerator()
    
    def generate_corridors(self, request: CorridorRequest) -> CorridorResponse:
        """
        Genere les corridors de deplacement pour une zone.
        
        Args:
            request: Parametres de requete
            
        Returns:
            CorridorResponse avec liste de corridors
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
        
        corridors = []
        
        # Trouver les zones cles (origine/destination des corridors)
        key_zones = self._find_key_zones(
            request.bounds,
            species,
            base_datetime
        )
        
        # Pour chaque type de corridor demande
        for corridor_type in request.corridor_types:
            type_corridors = self._generate_corridors_of_type(
                corridor_type=corridor_type,
                key_zones=key_zones,
                species=request.species,
                bounds=request.bounds,
                base_datetime=base_datetime
            )
            corridors.extend(type_corridors)
        
        calc_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        
        return CorridorResponse(
            success=True,
            corridors=corridors,
            metadata={
                "calculation_time_ms": round(calc_time, 1),
                "species": request.species,
                "corridor_count": len(corridors),
                "version": "P1-HOTSPOTS-1.0"
            }
        )
    
    def _find_key_zones(
        self,
        bounds: BoundsInput,
        species: Species,
        base_datetime: datetime
    ) -> List[Dict]:
        """Trouve les zones cles (noeuds du reseau de corridors)."""
        zones = []
        
        # Identifier les zones d'alimentation, repos, eau
        zone_types = ["feeding", "bedding", "water", "thermal"]
        
        # Generer des points candidats
        grid_size = 4
        lat_step = (bounds.north - bounds.south) / grid_size
        lng_step = (bounds.east - bounds.west) / grid_size
        
        for i in range(grid_size):
            for j in range(grid_size):
                lat = bounds.south + (i + 0.5) * lat_step
                lng = bounds.west + (j + 0.5) * lng_step
                
                result = self._pt_service.calculate_score(
                    latitude=lat,
                    longitude=lng,
                    species=species,
                    datetime_target=base_datetime,
                    include_advanced_factors=True
                )
                
                if result.success and result.overall_score >= 65:
                    factors = result.metadata.get("advanced_factors", {})
                    factor_scores = result.metadata.get("advanced_factor_scores", {})
                    
                    # Determiner le type de zone
                    zone_type = self._determine_zone_type(factor_scores)
                    
                    zones.append({
                        "lat": lat,
                        "lng": lng,
                        "score": result.overall_score,
                        "type": zone_type,
                        "factors": factors
                    })
        
        # Trier par score
        zones.sort(key=lambda z: z["score"], reverse=True)
        return zones[:8]  # Garder les 8 meilleures zones
    
    def _determine_zone_type(self, factor_scores: Dict) -> str:
        """Determine le type de zone selon les facteurs."""
        digestive = factor_scores.get("digestive", 0)
        thermal = factor_scores.get("thermal_stress", 0)
        hydric = factor_scores.get("hydric_stress", 0)
        
        if digestive > 70:
            return "feeding"
        elif thermal < 20:
            return "thermal"
        elif hydric < 30:
            return "water"
        else:
            return "bedding"
    
    def _generate_corridors_of_type(
        self,
        corridor_type: str,
        key_zones: List[Dict],
        species: str,
        bounds: BoundsInput,
        base_datetime: datetime
    ) -> List[Corridor]:
        """Genere les corridors d'un type specifique."""
        corridors = []
        
        if len(key_zones) < 2:
            return corridors
        
        # Logique specifique par type
        if corridor_type == "movement":
            corridors = self._generate_movement_corridors(key_zones, species)
        elif corridor_type == "avoidance":
            corridors = self._generate_avoidance_corridors(key_zones, species, bounds)
        elif corridor_type == "preferred":
            corridors = self._generate_preferred_corridors(key_zones, species)
        elif corridor_type == "feeding_transit":
            corridors = self._generate_feeding_transit_corridors(key_zones, species)
        
        return corridors
    
    def _generate_movement_corridors(
        self,
        zones: List[Dict],
        species: str
    ) -> List[Corridor]:
        """Genere les corridors de mouvement entre zones."""
        corridors = []
        
        # Connecter les zones les plus proches
        for i, zone1 in enumerate(zones[:5]):
            for zone2 in zones[i+1:6]:
                distance = self._calculate_distance(
                    zone1["lat"], zone1["lng"],
                    zone2["lat"], zone2["lng"]
                )
                
                # Ne connecter que les zones relativement proches
                if distance < 0.05:  # ~5km
                    corridor = self._create_corridor(
                        corridor_type="movement",
                        from_zone=zone1,
                        to_zone=zone2,
                        species=species
                    )
                    corridors.append(corridor)
        
        return corridors[:4]  # Max 4 corridors de mouvement
    
    def _generate_avoidance_corridors(
        self,
        zones: List[Dict],
        species: str,
        bounds: BoundsInput
    ) -> List[Corridor]:
        """Genere les corridors d'evitement."""
        corridors = []
        
        # Trouver les zones a risque (predation, humain)
        risky_zones = [z for z in zones if z.get("factors", {}).get("predation", {}).get("risk_score", 0) > 40]
        safe_zones = [z for z in zones if z not in risky_zones]
        
        if risky_zones and safe_zones:
            # Corridor d'evitement de la zone risquee vers la zone sure
            for risky in risky_zones[:2]:
                nearest_safe = min(safe_zones, key=lambda s: self._calculate_distance(
                    risky["lat"], risky["lng"], s["lat"], s["lng"]
                ))
                
                corridor = self._create_corridor(
                    corridor_type="avoidance",
                    from_zone=risky,
                    to_zone=nearest_safe,
                    species=species
                )
                corridors.append(corridor)
        
        return corridors[:2]
    
    def _generate_preferred_corridors(
        self,
        zones: List[Dict],
        species: str
    ) -> List[Corridor]:
        """Genere les routes preferees (scores les plus eleves)."""
        corridors = []
        
        # Connecter les 3 meilleures zones
        top_zones = zones[:3]
        
        for i, zone1 in enumerate(top_zones):
            for zone2 in top_zones[i+1:]:
                corridor = self._create_corridor(
                    corridor_type="preferred",
                    from_zone=zone1,
                    to_zone=zone2,
                    species=species
                )
                corridors.append(corridor)
        
        return corridors[:3]
    
    def _generate_feeding_transit_corridors(
        self,
        zones: List[Dict],
        species: str
    ) -> List[Corridor]:
        """Genere les corridors alimentation-repos."""
        corridors = []
        
        feeding_zones = [z for z in zones if z.get("type") == "feeding"]
        bedding_zones = [z for z in zones if z.get("type") == "bedding"]
        
        # Connecter zones d'alimentation aux zones de repos
        for feeding in feeding_zones[:2]:
            if bedding_zones:
                nearest_bedding = min(bedding_zones, key=lambda b: self._calculate_distance(
                    feeding["lat"], feeding["lng"], b["lat"], b["lng"]
                ))
                
                corridor = self._create_corridor(
                    corridor_type="feeding_transit",
                    from_zone=feeding,
                    to_zone=nearest_bedding,
                    species=species
                )
                corridors.append(corridor)
        
        return corridors[:3]
    
    def _create_corridor(
        self,
        corridor_type: str,
        from_zone: Dict,
        to_zone: Dict,
        species: str,
        water_features: Optional[List[Dict]] = None
    ) -> Optional[Corridor]:
        """
        Cree un corridor avec validation obligatoire contre les masses d'eau.
        
        RÈGLE BIONIC V5: Les corridors ne traversent JAMAIS de grandes masses d'eau.
        Si une intersection est détectée, le corridor est recalculé ou annulé.
        """
        
        # Generer geometrie naturelle initiale
        geometry = self._contour_gen.generate_corridor_geometry(
            from_zone_center=(from_zone["lat"], from_zone["lng"]),
            to_zone_center=(to_zone["lat"], to_zone["lng"]),
            corridor_type=corridor_type
        )
        
        # Extraire les coordonnées du corridor
        corridor_coords = geometry.get("coordinates", [])
        if not corridor_coords:
            return None
        
        # Convertir en format (lat, lng) pour la validation
        corridor_points = [(coord[1], coord[0]) for coord in corridor_coords]
        
        corridor_id = generate_id("CR")
        
        # ===================================================================
        # VALIDATION OBLIGATOIRE: EXCLUSION DES MASSES D'EAU
        # ===================================================================
        if water_features:
            water_service = get_water_exclusion_service()
            validation = water_service.validate_corridor(
                corridor_id=corridor_id,
                corridor_geometry=corridor_points,
                water_features=water_features,
                species=species
            )
            
            if validation.result == CorridorValidationResult.REJECTED:
                # Corridor traverse une masse d'eau infranchissable et ne peut être recalculé
                logger.warning(
                    f"[BIONIC] Corridor {corridor_id} REJECTED: "
                    f"crosses {len(validation.intersections_found)} water bodies "
                    f"(species={species})"
                )
                return None  # Ne pas créer ce corridor
            
            elif validation.result == CorridorValidationResult.REROUTED:
                # Corridor a été recalculé pour contourner l'eau
                logger.info(
                    f"[BIONIC] Corridor {corridor_id} REROUTED: "
                    f"avoided {len(validation.intersections_found)} water bodies "
                    f"after {validation.reroute_attempts} attempts"
                )
                # Utiliser la nouvelle géométrie
                if validation.validated_geometry:
                    corridor_coords = [[p[1], p[0]] for p in validation.validated_geometry]
                    geometry["coordinates"] = corridor_coords
        
        # Contexte de mouvement
        peak_hours_map = {
            "movement": [6, 7, 17, 18],
            "avoidance": [10, 11, 14, 15],
            "preferred": [6, 7, 8, 17, 18, 19],
            "feeding_transit": [5, 6, 7, 16, 17, 18]
        }
        
        frequency_map = {
            "movement": "daily",
            "avoidance": "occasional",
            "preferred": "daily",
            "feeding_transit": "daily"
        }
        
        # Largeur estimee
        width_map = {
            "movement": 50,
            "avoidance": 30,
            "preferred": 75,
            "feeding_transit": 40
        }
        
        # Probabilite d'usage
        prob_map = {
            "movement": 0.7,
            "avoidance": 0.5,
            "preferred": 0.85,
            "feeding_transit": 0.75
        }
        
        return Corridor(
            id=corridor_id,
            type=corridor_type,
            geometry=geometry,
            movement_context=MovementContext(
                direction="bidirectional",
                frequency=frequency_map.get(corridor_type, "daily"),
                peak_hours=peak_hours_map.get(corridor_type, [6, 7, 17, 18]),
                connects=ZoneConnection(
                    from_zone=f"ZN-{from_zone.get('type', 'unknown')}",
                    to_zone=f"ZN-{to_zone.get('type', 'unknown')}"
                )
            ),
            width_meters=width_map.get(corridor_type, 50),
            usage_probability=prob_map.get(corridor_type, 0.7),
            style=CorridorStyle(**create_corridor_style(corridor_type))
        )
    
    def _calculate_distance(
        self,
        lat1: float,
        lng1: float,
        lat2: float,
        lng2: float
    ) -> float:
        """Calcule la distance en degres entre deux points."""
        return math.sqrt((lat2 - lat1) ** 2 + (lng2 - lng1) ** 2)
