"""
BIONIC V5 — MOBILITY PREDICTION (NIVEAU 6)
==========================================
NIVEAU 6 — Mesure & Figeage

Service de prédiction de mobilité sur fenêtre temporelle.

ENDPOINT: POST /api/v1/bionic/mobility_prediction

FONCTIONNALITÉS:
- Prédictions sur fenêtre temporelle (ex: 6h)
- Zones de mouvement probables en GeoJSON
- Trajectoires anticipées
- Intégration des facteurs NIVEAU 1-5

VERSION: 6.0.0
Conformité: G-SEC | G-QA | G-DOC | BIONIC V5 NIVEAU 6
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
import logging
import math

logger = logging.getLogger(__name__)


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class TrajectoryPoint:
    """
    Point sur une trajectoire prédite.
    """
    
    point_id: str
    sequence: int
    
    # Position
    lat: float
    lng: float
    
    # Timestamp prédit
    predicted_time: datetime
    
    # Probabilité d'être à ce point
    probability: float = 0.5
    
    # Métadonnées
    intensity: str = "moderate"
    behavior: str = "movement"
    
    def to_geojson_feature(self) -> Dict[str, Any]:
        """Convertir en GeoJSON Feature Point."""
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [self.lng, self.lat]
            },
            "properties": {
                "point_id": self.point_id,
                "sequence": self.sequence,
                "predicted_time": self.predicted_time.isoformat(),
                "probability": round(self.probability, 2),
                "intensity": self.intensity,
                "behavior": self.behavior
            }
        }


@dataclass
class MovementZone:
    """
    Zone de mouvement probable.
    
    Représentée comme un cercle ou polygone GeoJSON.
    """
    
    zone_id: str
    zone_type: str          # probable (70%+), possible (50-70%), unlikely (30-50%)
    
    # Centre de la zone
    center_lat: float
    center_lng: float
    
    # Rayon en km
    radius_km: float
    
    # Probabilité
    probability: float = 0.5
    
    # Fenêtre temporelle
    time_start: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    time_end: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Style de rendu
    fill_color: str = "#FF8A00"
    fill_opacity: float = 0.3
    stroke_color: str = "#FF8A00"
    stroke_width: int = 2
    
    # Traçabilité
    source_ids: List[str] = field(default_factory=list)
    
    def to_geojson_feature(self) -> Dict[str, Any]:
        """Convertir en GeoJSON Feature Polygon (cercle approximé)."""
        # Créer un cercle avec 32 points
        num_points = 32
        coordinates = []
        
        for i in range(num_points + 1):  # +1 pour fermer le polygone
            angle = 2 * math.pi * i / num_points
            # Convertir le rayon en degrés (approximation)
            lat_offset = (self.radius_km / 111.0) * math.cos(angle)
            lng_offset = (self.radius_km / (111.0 * math.cos(math.radians(self.center_lat)))) * math.sin(angle)
            
            coordinates.append([
                self.center_lng + lng_offset,
                self.center_lat + lat_offset
            ])
        
        return {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [coordinates]
            },
            "properties": {
                "zone_id": self.zone_id,
                "zone_type": self.zone_type,
                "center": {"lat": self.center_lat, "lng": self.center_lng},
                "radius_km": round(self.radius_km, 2),
                "probability": round(self.probability, 2),
                "time_window": {
                    "start": self.time_start.isoformat(),
                    "end": self.time_end.isoformat()
                },
                "rendering": {
                    "fill_color": self.fill_color,
                    "fill_opacity": self.fill_opacity,
                    "stroke_color": self.stroke_color,
                    "stroke_width": self.stroke_width
                },
                "source_ids": self.source_ids
            }
        }


@dataclass
class MobilityPrediction:
    """
    Prédiction de mobilité complète sur une fenêtre temporelle.
    
    Format GeoJSON FeatureCollection.
    """
    
    prediction_id: str
    
    # Waypoint de départ
    start_lat: float
    start_lng: float
    species: str
    
    # Fenêtre de prédiction
    prediction_start: datetime
    prediction_end: datetime
    window_hours: float
    
    # Trajectoire prédite
    trajectory_points: List[TrajectoryPoint] = field(default_factory=list)
    
    # Zones de mouvement
    probable_zones: List[MovementZone] = field(default_factory=list)      # 70%+
    possible_zones: List[MovementZone] = field(default_factory=list)      # 50-70%
    unlikely_zones: List[MovementZone] = field(default_factory=list)      # 30-50%
    
    # Métriques
    predicted_distance_km: float = 0.0
    average_speed_kmh: float = 0.0
    dominant_direction: str = "random"
    
    # Facteurs intégrés
    mobility_modifier: float = 1.0
    seasonal_modifier: float = 1.0
    thermal_modifier: float = 1.0
    human_pressure_modifier: float = 1.0
    
    # Confidence
    prediction_confidence: float = 0.7
    
    # Traçabilité
    source_ids: List[str] = field(default_factory=lambda: ["SRC-MOBILITY-PRED-V6"])
    version: str = "6.0.0"
    
    def to_geojson_feature_collection(self) -> Dict[str, Any]:
        """Convertir en GeoJSON FeatureCollection."""
        features = []
        
        # Ajouter les zones
        for zone in self.probable_zones:
            features.append(zone.to_geojson_feature())
        for zone in self.possible_zones:
            features.append(zone.to_geojson_feature())
        for zone in self.unlikely_zones:
            features.append(zone.to_geojson_feature())
        
        # Ajouter les points de trajectoire
        for point in self.trajectory_points:
            features.append(point.to_geojson_feature())
        
        # Ajouter la trajectoire comme LineString
        if len(self.trajectory_points) >= 2:
            trajectory_coords = [[p.lng, p.lat] for p in self.trajectory_points]
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": trajectory_coords
                },
                "properties": {
                    "type": "predicted_trajectory",
                    "points_count": len(self.trajectory_points),
                    "total_distance_km": round(self.predicted_distance_km, 2)
                }
            })
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "properties": {
                "prediction_id": self.prediction_id,
                "species": self.species,
                "start_position": {"lat": self.start_lat, "lng": self.start_lng},
                "time_window": {
                    "start": self.prediction_start.isoformat(),
                    "end": self.prediction_end.isoformat(),
                    "hours": self.window_hours
                },
                "metrics": {
                    "predicted_distance_km": round(self.predicted_distance_km, 2),
                    "average_speed_kmh": round(self.average_speed_kmh, 2),
                    "dominant_direction": self.dominant_direction
                },
                "factors": {
                    "mobility": round(self.mobility_modifier, 3),
                    "seasonal": round(self.seasonal_modifier, 3),
                    "thermal": round(self.thermal_modifier, 3),
                    "human_pressure": round(self.human_pressure_modifier, 3)
                },
                "zones_summary": {
                    "probable": len(self.probable_zones),
                    "possible": len(self.possible_zones),
                    "unlikely": len(self.unlikely_zones)
                },
                "confidence": round(self.prediction_confidence, 2),
                "source_ids": self.source_ids,
                "version": self.version
            }
        }


# =============================================================================
# MOBILITY PREDICTION SERVICE
# =============================================================================

class MobilityPredictionService:
    """
    Service de prédiction de mobilité NIVEAU 6.
    
    Génère des prédictions de mouvement sur une fenêtre temporelle.
    """
    
    def __init__(self):
        self._version = "6.0.0"
        self._prediction_counter = 0
        
        # Paramètres par espèce
        self._species_params = {
            "moose": {
                "avg_speed_kmh": 2.5,
                "max_daily_km": 12.0,
                "activity_peak_hours": [5, 6, 7, 17, 18, 19],
                "rest_hours": [11, 12, 13, 14]
            },
            "deer": {
                "avg_speed_kmh": 3.0,
                "max_daily_km": 10.0,
                "activity_peak_hours": [5, 6, 7, 16, 17, 18],
                "rest_hours": [10, 11, 12, 13]
            },
            "bear": {
                "avg_speed_kmh": 2.0,
                "max_daily_km": 15.0,
                "activity_peak_hours": [5, 6, 7, 8, 17, 18, 19],
                "rest_hours": [12, 13, 14]
            }
        }
        
        logger.info(f"MobilityPredictionService initialized: v{self._version}")
    
    def _generate_prediction_id(self) -> str:
        """Génère un ID unique pour une prédiction."""
        self._prediction_counter += 1
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"PRED-{timestamp}-{self._prediction_counter:04d}"
    
    def _get_species_key(self, species: str) -> str:
        """Convertit le nom d'espèce en clé normalisée."""
        species_lower = species.lower()
        if "orignal" in species_lower or "moose" in species_lower:
            return "moose"
        elif "cerf" in species_lower or "deer" in species_lower:
            return "deer"
        elif "ours" in species_lower or "bear" in species_lower:
            return "bear"
        return "deer"
    
    def _calculate_position_offset(
        self,
        lat: float, lng: float,
        bearing_deg: float,
        distance_km: float
    ) -> Tuple[float, float]:
        """Calcule une nouvelle position à partir d'un bearing et distance."""
        R = 6371.0  # Rayon de la Terre en km
        
        bearing_rad = math.radians(bearing_deg)
        lat_rad = math.radians(lat)
        lng_rad = math.radians(lng)
        
        new_lat_rad = math.asin(
            math.sin(lat_rad) * math.cos(distance_km / R) +
            math.cos(lat_rad) * math.sin(distance_km / R) * math.cos(bearing_rad)
        )
        new_lng_rad = lng_rad + math.atan2(
            math.sin(bearing_rad) * math.sin(distance_km / R) * math.cos(lat_rad),
            math.cos(distance_km / R) - math.sin(lat_rad) * math.sin(new_lat_rad)
        )
        
        return math.degrees(new_lat_rad), math.degrees(new_lng_rad)
    
    def predict_mobility(
        self,
        start_lat: float,
        start_lng: float,
        species: str,
        prediction_start: datetime,
        window_hours: float = 6.0,
        # Facteurs NIVEAU 1-5
        mobility_modifier: float = 1.0,
        seasonal_modifier: float = 1.0,
        thermal_modifier: float = 1.0,
        human_pressure_modifier: float = 1.0,
        current_season: str = "default",
        # Options
        include_trajectory: bool = True,
        trajectory_interval_min: int = 30
    ) -> MobilityPrediction:
        """
        NIVEAU 6 BIONIC V5 — Prédiction de mobilité sur fenêtre temporelle.
        
        Args:
            start_lat, start_lng: Position de départ
            species: Espèce cible
            prediction_start: Début de la fenêtre de prédiction
            window_hours: Durée de la fenêtre (heures)
            mobility_modifier: Modificateur NIVEAU 5
            seasonal_modifier: Modificateur NIVEAU 1
            thermal_modifier: Modificateur NIVEAU 1
            human_pressure_modifier: Modificateur NIVEAU 3
            current_season: Saison courante
            include_trajectory: Inclure les points de trajectoire
            trajectory_interval_min: Intervalle entre les points (minutes)
            
        Returns:
            MobilityPrediction avec GeoJSON
        """
        prediction_id = self._generate_prediction_id()
        species_key = self._get_species_key(species)
        params = self._species_params.get(species_key, self._species_params["deer"])
        
        prediction_end = prediction_start + timedelta(hours=window_hours)
        
        # =================================================================
        # 1. CALCUL DE LA VITESSE EFFECTIVE
        # =================================================================
        
        # Vitesse de base ajustée par les modificateurs
        base_speed = params["avg_speed_kmh"]
        effective_speed = base_speed * mobility_modifier * seasonal_modifier * thermal_modifier
        
        # Si pression humaine active, vitesse peut augmenter (fuite)
        if human_pressure_modifier < 0.7:
            effective_speed *= 1.3
        
        # =================================================================
        # 2. CALCUL DE LA DISTANCE TOTALE PRÉDITE
        # =================================================================
        
        # Tenir compte des heures d'activité
        active_hours = 0
        current_hour = prediction_start.hour
        for h in range(int(window_hours)):
            check_hour = (current_hour + h) % 24
            if check_hour in params["activity_peak_hours"]:
                active_hours += 1.5  # Activité maximale
            elif check_hour in params["rest_hours"]:
                active_hours += 0.3  # Repos
            else:
                active_hours += 0.8  # Activité normale
        
        effective_hours = active_hours
        predicted_distance = effective_speed * effective_hours
        predicted_distance = min(predicted_distance, params["max_daily_km"])
        
        # =================================================================
        # 3. DÉTERMINATION DE LA DIRECTION DOMINANTE
        # =================================================================
        
        # Direction basée sur les contraintes
        if human_pressure_modifier < 0.6:
            dominant_direction = "away_from_pressure"
            # Direction opposée à la source de pression (simplifiée)
            primary_bearing = 180 + (45 * (0.5 - human_pressure_modifier))
        elif thermal_modifier < 0.8:
            dominant_direction = "towards_refuge"
            primary_bearing = 270 + 45  # Vers le nord-ouest (zones ombragées)
        elif current_season in ["rut", "pre_rut"]:
            dominant_direction = "activity_driven"
            primary_bearing = 90  # Est (vers zones d'activité)
        else:
            dominant_direction = "random"
            primary_bearing = 0
        
        # =================================================================
        # 4. GÉNÉRATION DES ZONES DE MOUVEMENT
        # =================================================================
        
        probable_zones = []
        possible_zones = []
        unlikely_zones = []
        
        # Zone probable (70%+) - rayon basé sur la distance prédite / 3
        probable_radius = predicted_distance / 3
        probable_lat, probable_lng = self._calculate_position_offset(
            start_lat, start_lng, primary_bearing, probable_radius * 0.5
        )
        probable_zones.append(MovementZone(
            zone_id=f"{prediction_id}-PROB-1",
            zone_type="probable",
            center_lat=probable_lat,
            center_lng=probable_lng,
            radius_km=probable_radius,
            probability=0.75,
            time_start=prediction_start,
            time_end=prediction_end,
            fill_color="#00A676",
            fill_opacity=0.25,
            stroke_color="#00A676",
            source_ids=["SRC-ZONE-PROBABLE", "SRC-MOBILITY-V5"]
        ))
        
        # Zone possible (50-70%) - rayon plus large
        possible_radius = predicted_distance / 2
        possible_lat, possible_lng = self._calculate_position_offset(
            start_lat, start_lng, primary_bearing, possible_radius * 0.4
        )
        possible_zones.append(MovementZone(
            zone_id=f"{prediction_id}-POSS-1",
            zone_type="possible",
            center_lat=possible_lat,
            center_lng=possible_lng,
            radius_km=possible_radius,
            probability=0.55,
            time_start=prediction_start,
            time_end=prediction_end,
            fill_color="#FFC04D",
            fill_opacity=0.15,
            stroke_color="#FFC04D",
            source_ids=["SRC-ZONE-POSSIBLE"]
        ))
        
        # Zone unlikely (30-50%) - rayon maximal
        unlikely_radius = predicted_distance * 0.8
        unlikely_zones.append(MovementZone(
            zone_id=f"{prediction_id}-UNLIKELY-1",
            zone_type="unlikely",
            center_lat=start_lat,
            center_lng=start_lng,
            radius_km=unlikely_radius,
            probability=0.35,
            time_start=prediction_start,
            time_end=prediction_end,
            fill_color="#FF4D4D",
            fill_opacity=0.08,
            stroke_color="#FF4D4D",
            source_ids=["SRC-ZONE-UNLIKELY"]
        ))
        
        # =================================================================
        # 5. GÉNÉRATION DE LA TRAJECTOIRE
        # =================================================================
        
        trajectory_points = []
        
        if include_trajectory:
            num_points = int((window_hours * 60) / trajectory_interval_min) + 1
            current_lat = start_lat
            current_lng = start_lng
            current_time = prediction_start
            
            for i in range(num_points):
                # Calculer la vitesse pour cette heure
                hour = current_time.hour
                if hour in params["activity_peak_hours"]:
                    hour_speed = effective_speed * 1.3
                    intensity = "high"
                    behavior = "active_movement"
                elif hour in params["rest_hours"]:
                    hour_speed = effective_speed * 0.3
                    intensity = "low"
                    behavior = "resting"
                else:
                    hour_speed = effective_speed * 0.8
                    intensity = "moderate"
                    behavior = "foraging"
                
                # Probabilité décroissante avec le temps
                time_elapsed = (current_time - prediction_start).total_seconds() / 3600
                probability = max(0.3, 0.9 - (time_elapsed / window_hours) * 0.4)
                
                trajectory_points.append(TrajectoryPoint(
                    point_id=f"{prediction_id}-PT-{i:03d}",
                    sequence=i,
                    lat=current_lat,
                    lng=current_lng,
                    predicted_time=current_time,
                    probability=probability,
                    intensity=intensity,
                    behavior=behavior
                ))
                
                # Calculer la position suivante
                if i < num_points - 1:
                    # Distance pour cet intervalle
                    interval_hours = trajectory_interval_min / 60
                    interval_distance = hour_speed * interval_hours
                    
                    # Bearing avec variation aléatoire
                    bearing_variation = (i % 2) * 30 - 15  # -15 à +15 degrés
                    bearing = primary_bearing + bearing_variation
                    
                    current_lat, current_lng = self._calculate_position_offset(
                        current_lat, current_lng, bearing, interval_distance
                    )
                    current_time += timedelta(minutes=trajectory_interval_min)
        
        # =================================================================
        # 6. CALCUL DE LA CONFIDENCE
        # =================================================================
        
        # Confidence basée sur les modificateurs
        confidence = (
            mobility_modifier * 0.3 +
            seasonal_modifier * 0.2 +
            (1 - abs(1 - thermal_modifier)) * 0.2 +
            human_pressure_modifier * 0.3
        )
        confidence = max(0.3, min(0.95, confidence))
        
        # =================================================================
        # 7. CONSTRUCTION DE LA PRÉDICTION
        # =================================================================
        
        prediction = MobilityPrediction(
            prediction_id=prediction_id,
            start_lat=start_lat,
            start_lng=start_lng,
            species=species,
            prediction_start=prediction_start,
            prediction_end=prediction_end,
            window_hours=window_hours,
            trajectory_points=trajectory_points,
            probable_zones=probable_zones,
            possible_zones=possible_zones,
            unlikely_zones=unlikely_zones,
            predicted_distance_km=predicted_distance,
            average_speed_kmh=effective_speed,
            dominant_direction=dominant_direction,
            mobility_modifier=mobility_modifier,
            seasonal_modifier=seasonal_modifier,
            thermal_modifier=thermal_modifier,
            human_pressure_modifier=human_pressure_modifier,
            prediction_confidence=confidence,
            source_ids=[
                "SRC-MOBILITY-PRED-V6",
                "SRC-MOBILITY-V5",
                "SRC-SEASONAL-V2",
                f"SRC-{species_key.upper()}"
            ]
        )
        
        logger.info(
            f"MobilityPrediction generated: {prediction_id}, "
            f"distance={predicted_distance:.2f}km, "
            f"zones={len(probable_zones)}+{len(possible_zones)}+{len(unlikely_zones)}, "
            f"confidence={confidence:.2f}"
        )
        
        return prediction
    
    def get_stats(self) -> Dict[str, Any]:
        """Statistiques du service."""
        return {
            "version": self._version,
            "predictions_generated": self._prediction_counter,
            "supported_species": list(self._species_params.keys())
        }


# =============================================================================
# SINGLETON
# =============================================================================

_service_instance: Optional[MobilityPredictionService] = None


def get_mobility_prediction_service() -> MobilityPredictionService:
    """Obtenir l'instance singleton du service de prédiction."""
    global _service_instance
    if _service_instance is None:
        _service_instance = MobilityPredictionService()
    return _service_instance


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'TrajectoryPoint',
    'MovementZone',
    'MobilityPrediction',
    'MobilityPredictionService',
    'get_mobility_prediction_service'
]
