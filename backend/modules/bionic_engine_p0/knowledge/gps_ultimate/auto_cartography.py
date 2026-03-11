"""
BIONIC V5 — AUTO-CARTOGRAPHY ENGINE (PHASE F)
==============================================
PHASE F — GPS ULTIMATE

Engine de cartographie automatique en temps réel.

FONCTIONNALITÉS:
1. Génération automatique des hotspots
2. Corridors dynamiques en temps réel
3. Recalcul continu selon NIVEAU 1-6

VERSION: 7.0.0
Conformité: G-SEC | G-QA | G-DOC | BIONIC V5 PHASE F
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

class HotspotType(str, Enum):
    """Types de hotspots PHASE F"""
    FEEDING = "feeding"           # Zone d'alimentation active
    RESTING = "resting"           # Zone de repos
    RUT_ACTIVITY = "rut_activity" # Activité de rut
    WATER_SOURCE = "water_source" # Point d'eau
    THERMAL_REFUGE = "thermal_refuge"  # Refuge thermique
    CORRIDOR_JUNCTION = "corridor_junction"  # Jonction de corridors
    HIGH_PROBABILITY = "high_probability"    # Zone haute probabilité


class CorridorStatus(str, Enum):
    """Statut d'un corridor dynamique"""
    ACTIVE = "active"         # Corridor actif
    DORMANT = "dormant"       # Corridor inactif temporaire
    BLOCKED = "blocked"       # Corridor bloqué (pression)
    SEASONAL = "seasonal"     # Actif selon saison


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class Hotspot:
    """
    Point chaud d'activité généré automatiquement.
    """
    
    hotspot_id: str
    hotspot_type: HotspotType
    
    # Position
    lat: float
    lng: float
    radius_m: float = 100.0
    
    # Scores
    intensity: float = 0.5          # 0-1
    confidence: float = 0.5         # 0-1
    probability: float = 0.5        # Probabilité de présence
    
    # Temporalité
    active_hours: List[int] = field(default_factory=list)
    peak_hour: int = 7
    
    # Intégration NIVEAU 1-6
    seasonal_factor: float = 1.0
    mobility_factor: float = 1.0
    pressure_factor: float = 1.0
    
    # Métadonnées
    species: str = ""
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Traçabilité
    source_ids: List[str] = field(default_factory=lambda: ["SRC-HOTSPOT-AUTO"])
    version: str = "7.0.0"
    
    def to_geojson_feature(self) -> Dict[str, Any]:
        """Convertir en GeoJSON Feature."""
        # Créer un cercle approximé
        num_points = 24
        coordinates = []
        for i in range(num_points + 1):
            angle = 2 * math.pi * i / num_points
            lat_offset = (self.radius_m / 111000) * math.cos(angle)
            lng_offset = (self.radius_m / (111000 * math.cos(math.radians(self.lat)))) * math.sin(angle)
            coordinates.append([self.lng + lng_offset, self.lat + lat_offset])
        
        # Couleur selon le type
        colors = {
            HotspotType.FEEDING: "#00A676",
            HotspotType.RESTING: "#4DA6FF",
            HotspotType.RUT_ACTIVITY: "#FF8A00",
            HotspotType.WATER_SOURCE: "#00CED1",
            HotspotType.THERMAL_REFUGE: "#FF4D4D",
            HotspotType.CORRIDOR_JUNCTION: "#FFC04D",
            HotspotType.HIGH_PROBABILITY: "#00FF00"
        }
        
        return {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [coordinates]
            },
            "properties": {
                "hotspot_id": self.hotspot_id,
                "hotspot_type": self.hotspot_type.value,
                "center": {"lat": self.lat, "lng": self.lng},
                "radius_m": self.radius_m,
                "scores": {
                    "intensity": round(self.intensity, 2),
                    "confidence": round(self.confidence, 2),
                    "probability": round(self.probability, 2)
                },
                "active_hours": self.active_hours,
                "peak_hour": self.peak_hour,
                "factors": {
                    "seasonal": round(self.seasonal_factor, 3),
                    "mobility": round(self.mobility_factor, 3),
                    "pressure": round(self.pressure_factor, 3)
                },
                "species": self.species,
                "last_updated": self.last_updated.isoformat(),
                "rendering": {
                    "fill_color": colors.get(self.hotspot_type, "#FF8A00"),
                    "fill_opacity": 0.3 * self.intensity,
                    "stroke_color": colors.get(self.hotspot_type, "#FF8A00"),
                    "stroke_width": 2
                },
                "source_ids": self.source_ids,
                "version": self.version
            }
        }


@dataclass
class DynamicCorridor:
    """
    Corridor dynamique recalculé en temps réel.
    """
    
    corridor_id: str
    status: CorridorStatus = CorridorStatus.ACTIVE
    
    # Géométrie
    coordinates: List[List[float]] = field(default_factory=list)
    width_m: float = 50.0
    
    # Scores temps réel
    flow_intensity: float = 0.5     # Intensité du flux
    usage_probability: float = 0.5  # Probabilité d'utilisation
    safety_score: float = 1.0       # 1.0 = sûr, 0.0 = dangereux
    
    # Connectivité
    source_hotspot_id: Optional[str] = None
    target_hotspot_id: Optional[str] = None
    
    # Intégration NIVEAU 1-6
    niveau1_seasonal: float = 1.0
    niveau3_pressure: float = 1.0
    niveau4_corridor_base: float = 1.0
    niveau5_mobility: float = 1.0
    
    # Métadonnées
    species: str = ""
    last_recalculated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    recalculation_count: int = 0
    
    # Traçabilité
    source_ids: List[str] = field(default_factory=lambda: ["SRC-CORRIDOR-DYNAMIC"])
    version: str = "7.0.0"
    
    def to_geojson_feature(self) -> Dict[str, Any]:
        """Convertir en GeoJSON Feature."""
        # Couleur selon le statut
        colors = {
            CorridorStatus.ACTIVE: "#00A676",
            CorridorStatus.DORMANT: "#808080",
            CorridorStatus.BLOCKED: "#CC0000",
            CorridorStatus.SEASONAL: "#4DA6FF"
        }
        
        return {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": self.coordinates
            },
            "properties": {
                "corridor_id": self.corridor_id,
                "status": self.status.value,
                "width_m": self.width_m,
                "scores": {
                    "flow_intensity": round(self.flow_intensity, 2),
                    "usage_probability": round(self.usage_probability, 2),
                    "safety_score": round(self.safety_score, 2)
                },
                "connectivity": {
                    "source_hotspot": self.source_hotspot_id,
                    "target_hotspot": self.target_hotspot_id
                },
                "niveau_factors": {
                    "niveau1_seasonal": round(self.niveau1_seasonal, 3),
                    "niveau3_pressure": round(self.niveau3_pressure, 3),
                    "niveau4_corridor_base": round(self.niveau4_corridor_base, 3),
                    "niveau5_mobility": round(self.niveau5_mobility, 3)
                },
                "species": self.species,
                "last_recalculated": self.last_recalculated.isoformat(),
                "recalculation_count": self.recalculation_count,
                "rendering": {
                    "stroke_color": colors.get(self.status, "#00A676"),
                    "stroke_width": max(2, int(4 * self.flow_intensity)),
                    "stroke_opacity": 0.6 + 0.4 * self.usage_probability,
                    "dash_array": "10,5" if self.status == CorridorStatus.DORMANT else None
                },
                "source_ids": self.source_ids,
                "version": self.version
            }
        }


# =============================================================================
# AUTO-CARTOGRAPHY ENGINE
# =============================================================================

class AutoCartographyEngine:
    """
    Engine de cartographie automatique PHASE F.
    
    Génère dynamiquement hotspots et corridors basés sur NIVEAU 1-6.
    """
    
    def __init__(self):
        self._version = "7.0.0"
        self._hotspot_counter = 0
        self._corridor_counter = 0
        
        # Cache des éléments générés
        self._hotspots: Dict[str, Hotspot] = {}
        self._corridors: Dict[str, DynamicCorridor] = {}
        
        logger.info(f"AutoCartographyEngine initialized: v{self._version}")
    
    def _generate_hotspot_id(self, hotspot_type: HotspotType) -> str:
        """Génère un ID unique pour un hotspot."""
        self._hotspot_counter += 1
        timestamp = datetime.now(timezone.utc).strftime("%H%M%S")
        type_prefix = hotspot_type.value[:4].upper()
        return f"HOT-{type_prefix}-{timestamp}-{self._hotspot_counter:04d}"
    
    def _generate_corridor_id(self) -> str:
        """Génère un ID unique pour un corridor."""
        self._corridor_counter += 1
        timestamp = datetime.now(timezone.utc).strftime("%H%M%S")
        return f"DYN-COR-{timestamp}-{self._corridor_counter:04d}"
    
    def generate_hotspots(
        self,
        center_lat: float,
        center_lng: float,
        species: str,
        search_radius_km: float = 3.0,
        # Facteurs NIVEAU 1-6
        seasonal_modifier: float = 1.0,
        mobility_modifier: float = 1.0,
        pressure_modifier: float = 1.0,
        current_season: str = "default",
        current_hour: int = 7
    ) -> List[Hotspot]:
        """
        PHASE F — Génère automatiquement les hotspots.
        
        Analyse la zone et génère des points chauds basés sur les facteurs NIVEAU 1-6.
        """
        hotspots = []
        
        # Paramètres par espèce
        species_config = {
            "moose": {"feeding_radius": 150, "resting_radius": 80, "water_distance": 0.5},
            "deer": {"feeding_radius": 100, "resting_radius": 60, "water_distance": 0.3},
            "bear": {"feeding_radius": 200, "resting_radius": 100, "water_distance": 0.4}
        }
        
        species_key = "deer"
        for key in species_config:
            if key in species.lower():
                species_key = key
                break
        
        config = species_config[species_key]
        
        # =================================================================
        # 1. HOTSPOT ALIMENTATION (basé sur heure et saison)
        # =================================================================
        
        is_feeding_hour = current_hour in [5, 6, 7, 16, 17, 18, 19]
        feeding_intensity = 0.7 if is_feeding_hour else 0.3
        
        # Position avec offset aléatoire
        feeding_lat = center_lat + (search_radius_km * 0.3 / 111) * (1 if current_hour < 12 else -1)
        feeding_lng = center_lng + (search_radius_km * 0.2 / 111) * 0.5
        
        feeding_hotspot = Hotspot(
            hotspot_id=self._generate_hotspot_id(HotspotType.FEEDING),
            hotspot_type=HotspotType.FEEDING,
            lat=feeding_lat,
            lng=feeding_lng,
            radius_m=config["feeding_radius"],
            intensity=feeding_intensity * seasonal_modifier,
            confidence=0.75,
            probability=0.6 * mobility_modifier,
            active_hours=[5, 6, 7, 16, 17, 18, 19],
            peak_hour=6 if current_hour < 12 else 18,
            seasonal_factor=seasonal_modifier,
            mobility_factor=mobility_modifier,
            pressure_factor=pressure_modifier,
            species=species_key,
            source_ids=["SRC-HOTSPOT-AUTO", "SRC-FEEDING", f"SRC-{species_key.upper()}"]
        )
        hotspots.append(feeding_hotspot)
        self._hotspots[feeding_hotspot.hotspot_id] = feeding_hotspot
        
        # =================================================================
        # 2. HOTSPOT REPOS (basé sur heure)
        # =================================================================
        
        is_rest_hour = current_hour in [10, 11, 12, 13, 14, 22, 23, 0, 1, 2, 3]
        resting_intensity = 0.8 if is_rest_hour else 0.2
        
        resting_lat = center_lat - (search_radius_km * 0.25 / 111)
        resting_lng = center_lng - (search_radius_km * 0.15 / 111)
        
        resting_hotspot = Hotspot(
            hotspot_id=self._generate_hotspot_id(HotspotType.RESTING),
            hotspot_type=HotspotType.RESTING,
            lat=resting_lat,
            lng=resting_lng,
            radius_m=config["resting_radius"],
            intensity=resting_intensity,
            confidence=0.70,
            probability=0.5 * (1 - mobility_modifier + 0.5),
            active_hours=[10, 11, 12, 13, 14, 22, 23, 0, 1, 2, 3],
            peak_hour=12,
            seasonal_factor=seasonal_modifier,
            mobility_factor=mobility_modifier,
            pressure_factor=pressure_modifier,
            species=species_key,
            source_ids=["SRC-HOTSPOT-AUTO", "SRC-RESTING"]
        )
        hotspots.append(resting_hotspot)
        self._hotspots[resting_hotspot.hotspot_id] = resting_hotspot
        
        # =================================================================
        # 3. HOTSPOT RUT (si saison appropriée)
        # =================================================================
        
        if current_season in ["rut", "pre_rut", "post_rut"]:
            rut_intensity = 0.9 if current_season == "rut" else 0.5
            
            rut_lat = center_lat + (search_radius_km * 0.4 / 111)
            rut_lng = center_lng + (search_radius_km * 0.3 / 111)
            
            rut_hotspot = Hotspot(
                hotspot_id=self._generate_hotspot_id(HotspotType.RUT_ACTIVITY),
                hotspot_type=HotspotType.RUT_ACTIVITY,
                lat=rut_lat,
                lng=rut_lng,
                radius_m=200,
                intensity=rut_intensity * seasonal_modifier,
                confidence=0.80,
                probability=0.7 * seasonal_modifier,
                active_hours=[5, 6, 7, 8, 17, 18, 19, 20],
                peak_hour=6,
                seasonal_factor=seasonal_modifier,
                mobility_factor=mobility_modifier,
                pressure_factor=pressure_modifier,
                species=species_key,
                source_ids=["SRC-HOTSPOT-AUTO", "SRC-RUT", "SRC-SEASONAL"]
            )
            hotspots.append(rut_hotspot)
            self._hotspots[rut_hotspot.hotspot_id] = rut_hotspot
        
        # =================================================================
        # 4. HOTSPOT EAU
        # =================================================================
        
        water_lat = center_lat - (search_radius_km * config["water_distance"] / 111)
        water_lng = center_lng + (search_radius_km * 0.1 / 111)
        
        water_hotspot = Hotspot(
            hotspot_id=self._generate_hotspot_id(HotspotType.WATER_SOURCE),
            hotspot_type=HotspotType.WATER_SOURCE,
            lat=water_lat,
            lng=water_lng,
            radius_m=50,
            intensity=0.6,
            confidence=0.85,
            probability=0.4,
            active_hours=list(range(24)),  # Toute la journée
            peak_hour=15,  # Après-midi chaud
            seasonal_factor=seasonal_modifier,
            mobility_factor=mobility_modifier,
            pressure_factor=pressure_modifier,
            species=species_key,
            source_ids=["SRC-HOTSPOT-AUTO", "SRC-WATER"]
        )
        hotspots.append(water_hotspot)
        self._hotspots[water_hotspot.hotspot_id] = water_hotspot
        
        # =================================================================
        # 5. HOTSPOT REFUGE THERMIQUE (si pression thermique)
        # =================================================================
        
        if seasonal_modifier < 0.9 or current_hour in [11, 12, 13, 14, 15]:
            thermal_lat = center_lat - (search_radius_km * 0.35 / 111)
            thermal_lng = center_lng - (search_radius_km * 0.25 / 111)
            
            thermal_hotspot = Hotspot(
                hotspot_id=self._generate_hotspot_id(HotspotType.THERMAL_REFUGE),
                hotspot_type=HotspotType.THERMAL_REFUGE,
                lat=thermal_lat,
                lng=thermal_lng,
                radius_m=120,
                intensity=0.7,
                confidence=0.70,
                probability=0.5 * (2 - seasonal_modifier),
                active_hours=[10, 11, 12, 13, 14, 15, 16],
                peak_hour=13,
                seasonal_factor=seasonal_modifier,
                mobility_factor=mobility_modifier,
                pressure_factor=pressure_modifier,
                species=species_key,
                source_ids=["SRC-HOTSPOT-AUTO", "SRC-THERMAL-REFUGE"]
            )
            hotspots.append(thermal_hotspot)
            self._hotspots[thermal_hotspot.hotspot_id] = thermal_hotspot
        
        logger.info(f"AutoCartography generated {len(hotspots)} hotspots for {species_key}")
        return hotspots
    
    def generate_dynamic_corridors(
        self,
        hotspots: List[Hotspot],
        pressure_modifier: float = 1.0,
        mobility_modifier: float = 1.0
    ) -> List[DynamicCorridor]:
        """
        PHASE F — Génère des corridors dynamiques entre hotspots.
        """
        corridors = []
        
        if len(hotspots) < 2:
            return corridors
        
        # Connecter les hotspots les plus pertinents
        for i, source in enumerate(hotspots):
            for target in hotspots[i+1:]:
                # Ne pas connecter les mêmes types sauf jonctions
                if source.hotspot_type == target.hotspot_type:
                    continue
                
                # Créer le corridor
                corridor_id = self._generate_corridor_id()
                
                # Coordonnées du corridor
                coords = [
                    [source.lng, source.lat],
                    [target.lng, target.lat]
                ]
                
                # Statut basé sur la pression
                if pressure_modifier < 0.5:
                    status = CorridorStatus.BLOCKED
                elif pressure_modifier < 0.8:
                    status = CorridorStatus.DORMANT
                else:
                    status = CorridorStatus.ACTIVE
                
                corridor = DynamicCorridor(
                    corridor_id=corridor_id,
                    status=status,
                    coordinates=coords,
                    width_m=50,
                    flow_intensity=mobility_modifier * 0.7,
                    usage_probability=(source.probability + target.probability) / 2,
                    safety_score=pressure_modifier,
                    source_hotspot_id=source.hotspot_id,
                    target_hotspot_id=target.hotspot_id,
                    niveau3_pressure=pressure_modifier,
                    niveau5_mobility=mobility_modifier,
                    species=source.species,
                    source_ids=["SRC-CORRIDOR-DYNAMIC", "SRC-AUTO-CONNECT"]
                )
                corridors.append(corridor)
                self._corridors[corridor_id] = corridor
        
        logger.info(f"AutoCartography generated {len(corridors)} dynamic corridors")
        return corridors
    
    def recalculate_all(
        self,
        pressure_modifier: float = 1.0,
        mobility_modifier: float = 1.0,
        current_hour: int = 7
    ) -> Tuple[int, int]:
        """
        PHASE F — Recalcul temps réel de tous les éléments.
        
        Returns:
            Tuple (hotspots_updated, corridors_updated)
        """
        hotspots_updated = 0
        corridors_updated = 0
        
        # Mettre à jour les hotspots
        for hotspot in self._hotspots.values():
            is_active = current_hour in hotspot.active_hours
            hotspot.intensity = 0.8 if is_active else 0.3
            hotspot.probability *= mobility_modifier
            hotspot.last_updated = datetime.now(timezone.utc)
            hotspots_updated += 1
        
        # Mettre à jour les corridors
        for corridor in self._corridors.values():
            corridor.niveau3_pressure = pressure_modifier
            corridor.niveau5_mobility = mobility_modifier
            corridor.safety_score = pressure_modifier
            corridor.flow_intensity = mobility_modifier * 0.7
            corridor.recalculation_count += 1
            corridor.last_recalculated = datetime.now(timezone.utc)
            
            # Mettre à jour le statut
            if pressure_modifier < 0.5:
                corridor.status = CorridorStatus.BLOCKED
            elif pressure_modifier < 0.8:
                corridor.status = CorridorStatus.DORMANT
            else:
                corridor.status = CorridorStatus.ACTIVE
            
            corridors_updated += 1
        
        logger.info(f"AutoCartography recalculated: {hotspots_updated} hotspots, {corridors_updated} corridors")
        return hotspots_updated, corridors_updated
    
    def to_geojson_feature_collection(self) -> Dict[str, Any]:
        """Export tous les éléments en GeoJSON."""
        features = []
        
        for hotspot in self._hotspots.values():
            features.append(hotspot.to_geojson_feature())
        
        for corridor in self._corridors.values():
            features.append(corridor.to_geojson_feature())
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "properties": {
                "total_hotspots": len(self._hotspots),
                "total_corridors": len(self._corridors),
                "version": self._version,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Statistiques de l'engine."""
        return {
            "version": self._version,
            "hotspots_count": len(self._hotspots),
            "corridors_count": len(self._corridors),
            "hotspot_types": list(set(h.hotspot_type.value for h in self._hotspots.values())),
            "corridor_statuses": list(set(c.status.value for c in self._corridors.values()))
        }


# =============================================================================
# SINGLETON
# =============================================================================

_engine_instance: Optional[AutoCartographyEngine] = None


def get_auto_cartography_engine() -> AutoCartographyEngine:
    """Obtenir l'instance singleton de l'engine."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = AutoCartographyEngine()
    return _engine_instance


__all__ = [
    'HotspotType',
    'CorridorStatus',
    'Hotspot',
    'DynamicCorridor',
    'AutoCartographyEngine',
    'get_auto_cartography_engine'
]
