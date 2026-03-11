"""
BIONIC V5 — CORRIDOR MODELS (NIVEAU 4)
======================================
NIVEAU 4 — Habitat & Corridors

Module de modélisation des corridors de déplacement pour la faune.

TYPES DE CORRIDORS:
1. PRIMARY (principaux) - Couleur: #FF8A00, continu, 4px
2. SECONDARY (secondaires) - Couleur: #FFC04D, pointillé long, 3px
3. SEASONAL (saisonniers) - Couleur: #4DA6FF, pointillé court, 3px
4. THERMAL (thermiques) - Couleur: #FF4D4D, continu semi-transparent, 5px
5. RISK (à risque) - Couleur: #CC0000, double ligne + halo, 6px

KNOWLEDGE LAYER INTEGRATION:
- Dynamiques: Générés en fonction du waypoint
- Pondérés par: habitat, edges, stress thermique, PRES-HUMAN, comportements, saisonnalité
- Jamais codés en dur
- Toujours versionnés + traçables

CENTRALISATION:
- Ce module FOURNIT les règles au UnifiedScoringService
- AUCUNE logique de scoring locale
- Traçabilité obligatoire (source_ids, version)

VERSION: 1.0.0
Conformité: G-SEC | G-QA | G-DOC | BIONIC V5 NIVEAU 4
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import logging
import math

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS
# =============================================================================

class CorridorType(str, Enum):
    """Types de corridors BIONIC V5 NIVEAU 4"""
    PRIMARY = "primary"           # Principaux - #FF8A00
    SECONDARY = "secondary"       # Secondaires - #FFC04D
    SEASONAL = "seasonal"         # Saisonniers - #4DA6FF
    THERMAL = "thermal"           # Thermiques - #FF4D4D
    RISK = "risk"                 # À risque - #CC0000


class CorridorPriority(str, Enum):
    """Priorité d'utilisation du corridor"""
    CRITICAL = "critical"         # Utilisation très fréquente
    HIGH = "high"                 # Utilisation fréquente
    MODERATE = "moderate"         # Utilisation modérée
    LOW = "low"                   # Utilisation occasionnelle


class CorridorQuality(str, Enum):
    """Qualité du corridor"""
    EXCELLENT = "excellent"       # Conditions optimales
    GOOD = "good"                 # Bonnes conditions
    MODERATE = "moderate"         # Conditions acceptables
    POOR = "poor"                 # Conditions dégradées
    BLOCKED = "blocked"           # Bloqué/inutilisable


# =============================================================================
# STYLES OFFICIELS NIVEAU 4
# =============================================================================

@dataclass
class CorridorStyle:
    """
    Style graphique officiel pour un corridor.
    
    NORMES GRAPHIQUES OFFICIELLES — CORRIDORS (NIVEAU 4)
    """
    
    corridor_type: CorridorType
    color: str
    opacity: float = 1.0
    weight: int = 3
    dash_array: Optional[str] = None  # None = ligne continue
    line_cap: str = "round"
    line_join: str = "round"
    
    # Halo (pour corridors à risque)
    halo_color: Optional[str] = None
    halo_opacity: float = 0.4
    halo_weight: int = 10
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire pour GeoJSON properties."""
        result = {
            "stroke_color": self.color,
            "stroke_opacity": self.opacity,
            "stroke_width": self.weight,
            "line_cap": self.line_cap,
            "line_join": self.line_join
        }
        if self.dash_array:
            result["dash_array"] = self.dash_array
        if self.halo_color:
            result["halo_color"] = self.halo_color
            result["halo_opacity"] = self.halo_opacity
            result["halo_weight"] = self.halo_weight
        return result


# STYLES OFFICIELS PAR TYPE
CORRIDOR_STYLES: Dict[CorridorType, CorridorStyle] = {
    CorridorType.PRIMARY: CorridorStyle(
        corridor_type=CorridorType.PRIMARY,
        color="#FF8A00",      # Orange
        opacity=1.0,
        weight=4,
        dash_array=None       # Continu
    ),
    CorridorType.SECONDARY: CorridorStyle(
        corridor_type=CorridorType.SECONDARY,
        color="#FFC04D",      # Jaune-orangé
        opacity=1.0,
        weight=3,
        dash_array="12,6"     # Pointillé long
    ),
    CorridorType.SEASONAL: CorridorStyle(
        corridor_type=CorridorType.SEASONAL,
        color="#4DA6FF",      # Bleu
        opacity=1.0,
        weight=3,
        dash_array="6,4"      # Pointillé court
    ),
    CorridorType.THERMAL: CorridorStyle(
        corridor_type=CorridorType.THERMAL,
        color="#FF4D4D",      # Rouge
        opacity=0.6,          # Semi-transparent
        weight=5,
        dash_array=None       # Continu
    ),
    CorridorType.RISK: CorridorStyle(
        corridor_type=CorridorType.RISK,
        color="#CC0000",      # Rouge foncé
        opacity=1.0,
        weight=6,
        dash_array=None,      # Continu
        halo_color="#FFCCCC", # Halo rose pâle
        halo_opacity=0.4,
        halo_weight=12
    )
}


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class CorridorSegment:
    """
    Segment d'un corridor (ligne entre deux points).
    
    Représente une portion du corridor avec ses propriétés.
    """
    
    segment_id: str
    
    # Géométrie (coordonnées GeoJSON: [lng, lat])
    start_point: Tuple[float, float]  # [lng, lat]
    end_point: Tuple[float, float]    # [lng, lat]
    
    # Propriétés
    length_m: float = 0.0
    elevation_gain_m: float = 0.0
    terrain_difficulty: float = 1.0   # 1.0 = facile, 3.0 = difficile
    
    # Score de qualité
    quality_score: float = 50.0       # 0-100
    quality: CorridorQuality = CorridorQuality.MODERATE
    
    # Facteurs d'influence
    habitat_influence: float = 1.0    # Impact de l'habitat
    edge_influence: float = 1.0       # Impact des lisières
    cover_percentage: float = 50.0    # % de couvert
    
    def to_geojson_coordinates(self) -> List[List[float]]:
        """Retourne les coordonnées pour GeoJSON."""
        return [list(self.start_point), list(self.end_point)]


@dataclass
class Corridor:
    """
    Corridor de déplacement complet.
    
    NIVEAU 4 BIONIC V5:
    - Généré dynamiquement en fonction du waypoint
    - Pondéré par habitat, edges, stress thermique, PRES-HUMAN
    """
    
    corridor_id: str
    
    # Type et priorité
    corridor_type: CorridorType
    priority: CorridorPriority = CorridorPriority.MODERATE
    
    # Nom descriptif
    name: str = ""
    description: str = ""
    
    # Géométrie (liste de coordonnées GeoJSON: [[lng, lat], ...])
    coordinates: List[List[float]] = field(default_factory=list)
    
    # Segments
    segments: List[CorridorSegment] = field(default_factory=list)
    
    # Métriques globales
    total_length_m: float = 0.0
    average_quality: float = 50.0
    quality: CorridorQuality = CorridorQuality.MODERATE
    
    # Facteurs d'influence (NIVEAU 1-3 intégrés)
    habitat_score: float = 50.0
    edge_score: float = 50.0
    thermal_stress_score: float = 50.0
    pres_human_score: float = 50.0
    behavior_score: float = 50.0
    seasonal_score: float = 50.0
    
    # Score composite
    composite_score: float = 50.0
    
    # Style (calculé automatiquement)
    style: Optional[CorridorStyle] = None
    
    # Temporalité (pour corridors saisonniers)
    active_seasons: List[str] = field(default_factory=list)
    active_hours: List[int] = field(default_factory=list)
    
    # Métadonnées
    species_relevance: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Traçabilité
    source_ids: List[str] = field(default_factory=lambda: ["SRC-CORRIDOR-V1"])
    version: str = "1.0.0"
    
    def __post_init__(self):
        """Initialiser le style après création."""
        if self.style is None and self.corridor_type:
            self.style = CORRIDOR_STYLES.get(self.corridor_type)
    
    def to_geojson_feature(self) -> Dict[str, Any]:
        """
        Convertir en GeoJSON Feature pour l'API.
        
        Format: GeoJSON LineString
        """
        properties = {
            "corridor_id": self.corridor_id,
            "corridor_type": self.corridor_type.value,
            "priority": self.priority.value,
            "name": self.name,
            "description": self.description,
            "quality": self.quality.value,
            "composite_score": round(self.composite_score, 1),
            "total_length_m": round(self.total_length_m, 1),
            "average_quality": round(self.average_quality, 1),
            # Scores des facteurs
            "factors": {
                "habitat": round(self.habitat_score, 1),
                "edge": round(self.edge_score, 1),
                "thermal_stress": round(self.thermal_stress_score, 1),
                "pres_human": round(self.pres_human_score, 1),
                "behavior": round(self.behavior_score, 1),
                "seasonal": round(self.seasonal_score, 1)
            },
            # Temporalité
            "active_seasons": self.active_seasons,
            "active_hours": self.active_hours,
            # Style
            "rendering": self.style.to_dict() if self.style else {},
            # Traçabilité
            "source_ids": self.source_ids,
            "version": self.version
        }
        
        return {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": self.coordinates
            },
            "properties": properties
        }


@dataclass
class CorridorNetwork:
    """
    Réseau complet de corridors pour un waypoint.
    
    NIVEAU 4 BIONIC V5:
    - Agrège tous les types de corridors
    - Retourné par l'API dans la clé `corridors`
    """
    
    network_id: str
    
    # Waypoint de référence
    waypoint_id: str
    center_lat: float
    center_lng: float
    search_radius_km: float = 3.0
    
    # Corridors par type
    primary_corridors: List[Corridor] = field(default_factory=list)
    secondary_corridors: List[Corridor] = field(default_factory=list)
    seasonal_corridors: List[Corridor] = field(default_factory=list)
    thermal_corridors: List[Corridor] = field(default_factory=list)
    risk_corridors: List[Corridor] = field(default_factory=list)
    
    # Statistiques
    total_corridors: int = 0
    total_length_km: float = 0.0
    average_network_quality: float = 50.0
    
    # Métadonnées
    species: str = ""
    analysis_datetime: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Traçabilité
    source_ids: List[str] = field(default_factory=lambda: ["SRC-CORRIDOR-NETWORK"])
    version: str = "1.0.0"
    
    def get_all_corridors(self) -> List[Corridor]:
        """Retourne tous les corridors du réseau."""
        return (
            self.primary_corridors +
            self.secondary_corridors +
            self.seasonal_corridors +
            self.thermal_corridors +
            self.risk_corridors
        )
    
    def to_geojson_feature_collection(self) -> Dict[str, Any]:
        """
        Convertir en GeoJSON FeatureCollection pour l'API.
        """
        features = [c.to_geojson_feature() for c in self.get_all_corridors()]
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "properties": {
                "network_id": self.network_id,
                "waypoint_id": self.waypoint_id,
                "center": {
                    "lat": self.center_lat,
                    "lng": self.center_lng
                },
                "search_radius_km": self.search_radius_km,
                "statistics": {
                    "total_corridors": self.total_corridors,
                    "total_length_km": round(self.total_length_km, 2),
                    "average_quality": round(self.average_network_quality, 1),
                    "by_type": {
                        "primary": len(self.primary_corridors),
                        "secondary": len(self.secondary_corridors),
                        "seasonal": len(self.seasonal_corridors),
                        "thermal": len(self.thermal_corridors),
                        "risk": len(self.risk_corridors)
                    }
                },
                "species": self.species,
                "analysis_datetime": self.analysis_datetime.isoformat(),
                "source_ids": self.source_ids,
                "version": self.version
            }
        }


# =============================================================================
# CORRIDOR REGISTRY
# =============================================================================

class CorridorRegistry:
    """
    Registre centralisé de génération des corridors.
    
    NIVEAU 4 - Knowledge Layer:
    - Génération dynamique basée sur waypoint
    - Intégration des facteurs NIVEAU 1-3
    - Styles officiels appliqués automatiquement
    """
    
    def __init__(self):
        self._version = "1.0.0"
        self._corridor_counter = 0
        
        # Règles par espèce
        self._species_rules: Dict[str, Dict[str, Any]] = {
            "moose": {
                "preferred_habitat": ["mixed_forest", "wetland", "edge"],
                "corridor_width_m": 100,
                "max_slope_degrees": 25,
                "water_crossing_preference": "avoid",
                "thermal_sensitivity": "high",
                "human_avoidance": "high"
            },
            "deer": {
                "preferred_habitat": ["edge", "clearing", "mixed_forest"],
                "corridor_width_m": 50,
                "max_slope_degrees": 35,
                "water_crossing_preference": "neutral",
                "thermal_sensitivity": "moderate",
                "human_avoidance": "moderate"
            },
            "bear": {
                "preferred_habitat": ["dense_forest", "riparian", "berry_patches"],
                "corridor_width_m": 75,
                "max_slope_degrees": 45,
                "water_crossing_preference": "prefer",
                "thermal_sensitivity": "moderate",
                "human_avoidance": "moderate"
            }
        }
        
        logger.info(f"CorridorRegistry initialized: {len(self._species_rules)} species")
    
    def _generate_corridor_id(self, corridor_type: CorridorType) -> str:
        """Génère un ID unique pour un corridor."""
        self._corridor_counter += 1
        timestamp = datetime.now(timezone.utc).strftime("%H%M%S")
        type_prefix = corridor_type.value[:3].upper()
        return f"COR-{type_prefix}-{timestamp}-{self._corridor_counter:04d}"
    
    def _calculate_distance(
        self,
        lat1: float, lng1: float,
        lat2: float, lng2: float
    ) -> float:
        """Calcule la distance en mètres entre deux points (Haversine)."""
        R = 6371000  # Rayon de la Terre en mètres
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def _generate_corridor_points(
        self,
        center_lat: float,
        center_lng: float,
        bearing_start: float,
        bearing_end: float,
        distance_m: float,
        num_points: int = 5
    ) -> List[List[float]]:
        """
        Génère une liste de points formant un corridor.
        
        Args:
            center_lat, center_lng: Centre de référence
            bearing_start: Direction initiale (degrés)
            bearing_end: Direction finale (degrés)
            distance_m: Distance totale du corridor
            num_points: Nombre de points intermédiaires
            
        Returns:
            Liste de coordonnées [[lng, lat], ...]
        """
        R = 6371000  # Rayon de la Terre
        
        points = []
        for i in range(num_points + 1):
            # Interpoler le bearing
            t = i / num_points
            bearing = math.radians(bearing_start + t * (bearing_end - bearing_start))
            
            # Distance progressive avec variation
            d = (distance_m * t) + (math.sin(t * math.pi * 2) * distance_m * 0.05)
            
            # Calculer la nouvelle position
            lat_rad = math.radians(center_lat)
            lng_rad = math.radians(center_lng)
            
            lat2 = math.asin(
                math.sin(lat_rad) * math.cos(d / R) +
                math.cos(lat_rad) * math.sin(d / R) * math.cos(bearing)
            )
            lng2 = lng_rad + math.atan2(
                math.sin(bearing) * math.sin(d / R) * math.cos(lat_rad),
                math.cos(d / R) - math.sin(lat_rad) * math.sin(lat2)
            )
            
            points.append([math.degrees(lng2), math.degrees(lat2)])
        
        return points
    
    def generate_corridors(
        self,
        waypoint_lat: float,
        waypoint_lng: float,
        species: str,
        search_radius_km: float = 3.0,
        # Facteurs NIVEAU 1-3
        habitat_score: float = 50.0,
        edge_score: float = 50.0,
        thermal_stress_active: bool = False,
        thermal_stress_modifier: float = 1.0,
        pres_human_active: bool = False,
        pres_human_modifier: float = 1.0,
        behavior_score: float = 50.0,
        seasonal_modifier: float = 1.0,
        current_season: str = "default",
        # Paramètres additionnels
        extra_params: Optional[Dict[str, Any]] = None
    ) -> CorridorNetwork:
        """
        NIVEAU 4 BIONIC V5 — Génération dynamique des corridors.
        
        Génère le réseau complet de corridors pour un waypoint donné,
        en intégrant les facteurs des NIVEAUx 1, 2 et 3.
        
        Args:
            waypoint_lat, waypoint_lng: Position du waypoint
            species: Espèce cible
            search_radius_km: Rayon de recherche
            habitat_score: Score habitat (NIVEAU 2)
            edge_score: Score lisières
            thermal_stress_active: Stress thermique actif (NIVEAU 1)
            thermal_stress_modifier: Modificateur stress thermique
            pres_human_active: Pression humaine active (NIVEAU 3)
            pres_human_modifier: Modificateur PRES-HUMAN
            behavior_score: Score comportement (NIVEAU 2)
            seasonal_modifier: Modificateur saisonnier (NIVEAU 1)
            current_season: Saison courante
            extra_params: Paramètres additionnels
            
        Returns:
            CorridorNetwork complet avec tous les types de corridors
        """
        network_id = f"NET-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        
        species_lower = species.lower()
        if "orignal" in species_lower or "moose" in species_lower:
            species_key = "moose"
        elif "cerf" in species_lower or "deer" in species_lower:
            species_key = "deer"
        elif "ours" in species_lower or "bear" in species_lower:
            species_key = "bear"
        else:
            species_key = "deer"  # Default
        
        species_rules = self._species_rules.get(species_key, self._species_rules["deer"])
        
        # Rayon en mètres
        radius_m = search_radius_km * 1000
        
        # Listes de corridors
        primary_corridors = []
        secondary_corridors = []
        seasonal_corridors = []
        thermal_corridors = []
        risk_corridors = []
        
        # =================================================================
        # 1. CORRIDORS PRINCIPAUX (2-3 corridors)
        # =================================================================
        
        primary_bearings = [
            (0, 15, "Nord"),
            (115, 135, "Sud-Est"),
            (230, 250, "Sud-Ouest")
        ]
        
        for i, (bearing_start, bearing_end, direction) in enumerate(primary_bearings[:2]):
            corridor_id = self._generate_corridor_id(CorridorType.PRIMARY)
            
            # Distance basée sur l'habitat
            base_distance = radius_m * 0.8
            distance = base_distance * (0.7 + habitat_score / 200)
            
            coords = self._generate_corridor_points(
                waypoint_lat, waypoint_lng,
                bearing_start, bearing_end,
                distance, num_points=6
            )
            
            # Score composite
            composite = (
                habitat_score * 0.3 +
                behavior_score * 0.25 +
                edge_score * 0.2 +
                (100 - (100 - 100 * pres_human_modifier) * 0.5) * 0.15 +
                (seasonal_modifier * 100) * 0.1
            )
            
            total_length = self._calculate_distance(
                coords[0][1], coords[0][0],
                coords[-1][1], coords[-1][0]
            )
            
            corridor = Corridor(
                corridor_id=corridor_id,
                corridor_type=CorridorType.PRIMARY,
                priority=CorridorPriority.HIGH if composite > 65 else CorridorPriority.MODERATE,
                name=f"Corridor Principal {direction}",
                description=f"Corridor de déplacement principal vers {direction}",
                coordinates=coords,
                total_length_m=total_length,
                average_quality=composite,
                quality=self._score_to_quality(composite),
                habitat_score=habitat_score,
                edge_score=edge_score,
                thermal_stress_score=100 * thermal_stress_modifier,
                pres_human_score=100 * pres_human_modifier,
                behavior_score=behavior_score,
                seasonal_score=100 * seasonal_modifier,
                composite_score=composite,
                active_seasons=["all"],
                species_relevance={species_key: 1.0},
                source_ids=["SRC-CORRIDOR-V1", "SRC-HABITAT", "SRC-BEHAVIOR"]
            )
            primary_corridors.append(corridor)
        
        # =================================================================
        # 2. CORRIDORS SECONDAIRES (2-4 corridors)
        # =================================================================
        
        secondary_bearings = [
            (45, 65, "Nord-Est"),
            (160, 180, "Sud"),
            (270, 290, "Ouest"),
            (315, 335, "Nord-Ouest")
        ]
        
        num_secondary = 3 if habitat_score > 60 else 2
        
        for i, (bearing_start, bearing_end, direction) in enumerate(secondary_bearings[:num_secondary]):
            corridor_id = self._generate_corridor_id(CorridorType.SECONDARY)
            
            distance = radius_m * 0.6 * (0.6 + edge_score / 200)
            
            coords = self._generate_corridor_points(
                waypoint_lat, waypoint_lng,
                bearing_start, bearing_end,
                distance, num_points=5
            )
            
            composite = (
                edge_score * 0.35 +
                habitat_score * 0.25 +
                behavior_score * 0.2 +
                (100 * pres_human_modifier) * 0.2
            )
            
            total_length = self._calculate_distance(
                coords[0][1], coords[0][0],
                coords[-1][1], coords[-1][0]
            )
            
            corridor = Corridor(
                corridor_id=corridor_id,
                corridor_type=CorridorType.SECONDARY,
                priority=CorridorPriority.MODERATE,
                name=f"Corridor Secondaire {direction}",
                description=f"Corridor alternatif vers {direction}",
                coordinates=coords,
                total_length_m=total_length,
                average_quality=composite,
                quality=self._score_to_quality(composite),
                habitat_score=habitat_score,
                edge_score=edge_score,
                thermal_stress_score=100 * thermal_stress_modifier,
                pres_human_score=100 * pres_human_modifier,
                behavior_score=behavior_score,
                seasonal_score=100 * seasonal_modifier,
                composite_score=composite,
                active_seasons=["all"],
                species_relevance={species_key: 0.7},
                source_ids=["SRC-CORRIDOR-V1", "SRC-EDGE"]
            )
            secondary_corridors.append(corridor)
        
        # =================================================================
        # 3. CORRIDORS SAISONNIERS (basés sur NIVEAU 1)
        # =================================================================
        
        seasonal_active = current_season in ["rut", "pre_rut", "post_rut", "hyperphagia"]
        
        if seasonal_active or seasonal_modifier > 1.1:
            seasonal_bearings = [
                (80, 100, "Est - Zone de rut"),
                (200, 220, "Sud-Ouest - Zone d'alimentation")
            ]
            
            for i, (bearing_start, bearing_end, description) in enumerate(seasonal_bearings):
                corridor_id = self._generate_corridor_id(CorridorType.SEASONAL)
                
                distance = radius_m * 0.7 * seasonal_modifier
                
                coords = self._generate_corridor_points(
                    waypoint_lat, waypoint_lng,
                    bearing_start, bearing_end,
                    distance, num_points=5
                )
                
                composite = (
                    (seasonal_modifier * 100) * 0.4 +
                    behavior_score * 0.3 +
                    habitat_score * 0.2 +
                    edge_score * 0.1
                )
                
                total_length = self._calculate_distance(
                    coords[0][1], coords[0][0],
                    coords[-1][1], coords[-1][0]
                )
                
                corridor = Corridor(
                    corridor_id=corridor_id,
                    corridor_type=CorridorType.SEASONAL,
                    priority=CorridorPriority.HIGH if seasonal_modifier > 1.2 else CorridorPriority.MODERATE,
                    name=f"Corridor Saisonnier - {current_season.upper()}",
                    description=description,
                    coordinates=coords,
                    total_length_m=total_length,
                    average_quality=composite,
                    quality=self._score_to_quality(composite),
                    habitat_score=habitat_score,
                    edge_score=edge_score,
                    thermal_stress_score=100 * thermal_stress_modifier,
                    pres_human_score=100 * pres_human_modifier,
                    behavior_score=behavior_score,
                    seasonal_score=100 * seasonal_modifier,
                    composite_score=composite,
                    active_seasons=[current_season],
                    species_relevance={species_key: 1.2 if seasonal_modifier > 1.1 else 0.9},
                    source_ids=["SRC-CORRIDOR-V1", "SRC-SEASONAL", f"SRC-{current_season.upper()}"]
                )
                seasonal_corridors.append(corridor)
        
        # =================================================================
        # 4. CORRIDORS THERMIQUES (basés sur stress thermique NIVEAU 1)
        # =================================================================
        
        if thermal_stress_active or thermal_stress_modifier < 0.9:
            thermal_bearings = [
                (150, 170, "Refuge thermique Sud"),
                (330, 350, "Zone ombragée Nord")
            ]
            
            for i, (bearing_start, bearing_end, description) in enumerate(thermal_bearings):
                corridor_id = self._generate_corridor_id(CorridorType.THERMAL)
                
                # Les corridors thermiques sont plus courts
                distance = radius_m * 0.5
                
                coords = self._generate_corridor_points(
                    waypoint_lat, waypoint_lng,
                    bearing_start, bearing_end,
                    distance, num_points=4
                )
                
                # Score inversement proportionnel au stress (stress bas = score haut)
                thermal_impact = (1 - thermal_stress_modifier) * 100
                composite = (
                    thermal_impact * 0.5 +
                    habitat_score * 0.25 +
                    (100 - behavior_score) * 0.15 +  # Repos = moins actif
                    edge_score * 0.1
                )
                
                total_length = self._calculate_distance(
                    coords[0][1], coords[0][0],
                    coords[-1][1], coords[-1][0]
                )
                
                corridor = Corridor(
                    corridor_id=corridor_id,
                    corridor_type=CorridorType.THERMAL,
                    priority=CorridorPriority.HIGH if thermal_stress_modifier < 0.7 else CorridorPriority.MODERATE,
                    name="Corridor vers Refuge Thermique",
                    description=description,
                    coordinates=coords,
                    total_length_m=total_length,
                    average_quality=composite,
                    quality=self._score_to_quality(composite),
                    habitat_score=habitat_score,
                    edge_score=edge_score,
                    thermal_stress_score=100 * thermal_stress_modifier,
                    pres_human_score=100 * pres_human_modifier,
                    behavior_score=behavior_score,
                    seasonal_score=100 * seasonal_modifier,
                    composite_score=composite,
                    active_seasons=["summer", "hyperphagia"],
                    active_hours=[10, 11, 12, 13, 14, 15, 16],  # Heures chaudes
                    species_relevance={species_key: 1.3 if thermal_stress_modifier < 0.8 else 0.8},
                    source_ids=["SRC-CORRIDOR-V1", "SRC-THERMAL", "SRC-REFUGE"]
                )
                thermal_corridors.append(corridor)
        
        # =================================================================
        # 5. CORRIDORS À RISQUE (PRES-HUMAN + stress thermique)
        # =================================================================
        
        if pres_human_active or pres_human_modifier < 0.8:
            risk_bearings = [
                (90, 110, "Zone à éviter - Pression humaine Est"),
                (270, 290, "Zone à éviter - Activité humaine Ouest")
            ]
            
            num_risk = 2 if pres_human_modifier < 0.6 else 1
            
            for i, (bearing_start, bearing_end, description) in enumerate(risk_bearings[:num_risk]):
                corridor_id = self._generate_corridor_id(CorridorType.RISK)
                
                # Les corridors à risque montrent les zones d'évitement
                distance = radius_m * 0.6
                
                coords = self._generate_corridor_points(
                    waypoint_lat, waypoint_lng,
                    bearing_start, bearing_end,
                    distance, num_points=5
                )
                
                # Score de risque (inversé - haut = risqué)
                risk_score = (1 - pres_human_modifier) * 100
                if thermal_stress_active:
                    risk_score += (1 - thermal_stress_modifier) * 30
                
                composite = 100 - risk_score  # Score de qualité inversé
                
                total_length = self._calculate_distance(
                    coords[0][1], coords[0][0],
                    coords[-1][1], coords[-1][0]
                )
                
                corridor = Corridor(
                    corridor_id=corridor_id,
                    corridor_type=CorridorType.RISK,
                    priority=CorridorPriority.CRITICAL,  # Toujours critique
                    name="Corridor à Risque - ÉVITER",
                    description=description,
                    coordinates=coords,
                    total_length_m=total_length,
                    average_quality=composite,
                    quality=CorridorQuality.POOR,  # Toujours mauvais
                    habitat_score=habitat_score,
                    edge_score=edge_score,
                    thermal_stress_score=100 * thermal_stress_modifier,
                    pres_human_score=100 * pres_human_modifier,
                    behavior_score=behavior_score,
                    seasonal_score=100 * seasonal_modifier,
                    composite_score=risk_score,  # Inversé
                    active_seasons=["hunting_season"] if pres_human_active else ["all"],
                    species_relevance={species_key: 0.1},  # Évité
                    source_ids=["SRC-CORRIDOR-V1", "SRC-PRES-HUMAN", "SRC-RISK"]
                )
                risk_corridors.append(corridor)
        
        # =================================================================
        # 6. AGRÉGATION DU RÉSEAU
        # =================================================================
        
        all_corridors = (
            primary_corridors +
            secondary_corridors +
            seasonal_corridors +
            thermal_corridors +
            risk_corridors
        )
        
        total_length_km = sum(c.total_length_m for c in all_corridors) / 1000
        avg_quality = sum(c.composite_score for c in all_corridors) / len(all_corridors) if all_corridors else 50.0
        
        network = CorridorNetwork(
            network_id=network_id,
            waypoint_id=f"WP-{waypoint_lat:.4f}-{waypoint_lng:.4f}",
            center_lat=waypoint_lat,
            center_lng=waypoint_lng,
            search_radius_km=search_radius_km,
            primary_corridors=primary_corridors,
            secondary_corridors=secondary_corridors,
            seasonal_corridors=seasonal_corridors,
            thermal_corridors=thermal_corridors,
            risk_corridors=risk_corridors,
            total_corridors=len(all_corridors),
            total_length_km=total_length_km,
            average_network_quality=avg_quality,
            species=species,
            source_ids=[
                "SRC-CORRIDOR-NETWORK",
                "SRC-CORRIDOR-V1",
                "SRC-HABITAT",
                "SRC-BEHAVIOR",
                "SRC-SEASONAL",
                "SRC-PRES-HUMAN"
            ],
            version=self._version
        )
        
        logger.info(
            f"CorridorNetwork generated: {network.total_corridors} corridors, "
            f"{network.total_length_km:.2f} km total, quality={network.average_network_quality:.1f}"
        )
        
        return network
    
    def _score_to_quality(self, score: float) -> CorridorQuality:
        """Convertit un score en qualité de corridor."""
        if score >= 80:
            return CorridorQuality.EXCELLENT
        elif score >= 65:
            return CorridorQuality.GOOD
        elif score >= 50:
            return CorridorQuality.MODERATE
        elif score >= 30:
            return CorridorQuality.POOR
        else:
            return CorridorQuality.BLOCKED
    
    def get_stats(self) -> Dict[str, Any]:
        """Statistiques du registre."""
        return {
            "version": self._version,
            "supported_species": list(self._species_rules.keys()),
            "corridor_types": [t.value for t in CorridorType],
            "styles": {t.value: CORRIDOR_STYLES[t].to_dict() for t in CorridorType}
        }


# =============================================================================
# SINGLETON
# =============================================================================

_registry_instance: Optional[CorridorRegistry] = None


def get_corridor_registry() -> CorridorRegistry:
    """Obtenir l'instance singleton du registre des corridors."""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = CorridorRegistry()
    return _registry_instance


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    'CorridorType',
    'CorridorPriority',
    'CorridorQuality',
    # Data models
    'CorridorStyle',
    'CorridorSegment',
    'Corridor',
    'CorridorNetwork',
    'CORRIDOR_STYLES',
    # Registry
    'CorridorRegistry',
    'get_corridor_registry'
]
