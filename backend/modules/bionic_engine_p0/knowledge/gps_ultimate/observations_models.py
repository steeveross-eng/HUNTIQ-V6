"""
BIONIC V5 — OBSERVATIONS MODELS (PHASE F)
==========================================
PHASE F — GPS ULTIMATE

Modèles de données pour les observations terrain.

OBJECTIF:
- Capturer les observations de faune sur le terrain
- Alimenter le CalibrationRegistry pour atteindre 95%+ de précision
- Permettre la transition vers BIONIC V5 MASTER

CHAMPS:
- Espèce observée
- Position GPS (lat/lng) 
- Horodatage (date/heure)
- Type de comportement
- Conditions météo
- Notes libres
- Qualité de l'observation

VERSION: 7.0.0
Conformité: G-SEC | G-QA | G-DOC | BIONIC V5 PHASE F
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS
# =============================================================================

class ObservedSpecies(str, Enum):
    """Espèces observables PHASE F"""
    MOOSE = "moose"                 # Orignal
    DEER = "deer"                   # Cerf de Virginie
    MULE_DEER = "mule_deer"         # Cerf-mulet
    BEAR = "bear"                   # Ours noir
    ELK = "elk"                     # Wapiti
    OTHER = "other"                 # Autre


class ObservedBehavior(str, Enum):
    """Comportements observables PHASE F"""
    FEEDING = "feeding"             # Alimentation
    RESTING = "resting"             # Repos
    MOVING = "moving"               # Déplacement
    DRINKING = "drinking"           # Abreuvement
    RUT_ACTIVITY = "rut_activity"   # Activité de rut
    ALERT = "alert"                 # Vigilance/alerte
    GROOMING = "grooming"           # Toilettage
    SOCIAL = "social"               # Interaction sociale
    UNKNOWN = "unknown"             # Inconnu


class ObservationConfidence(str, Enum):
    """Niveau de confiance de l'observation"""
    HIGH = "high"                   # Observation directe, conditions idéales
    MEDIUM = "medium"               # Observation partielle ou conditions moyennes
    LOW = "low"                     # Indices indirects ou conditions difficiles


class WeatherCondition(str, Enum):
    """Conditions météo lors de l'observation"""
    CLEAR = "clear"                 # Dégagé
    CLOUDY = "cloudy"               # Nuageux
    RAIN = "rain"                   # Pluie
    SNOW = "snow"                   # Neige
    FOG = "fog"                     # Brouillard
    WIND = "wind"                   # Venteux


class ObservationSource(str, Enum):
    """Source de l'observation"""
    DIRECT_VISUAL = "direct_visual"     # Observation directe
    TRAIL_CAMERA = "trail_camera"       # Caméra de trail
    GPS_COLLAR = "gps_collar"           # Collier GPS
    TRACKS = "tracks"                   # Traces/indices
    AUDIO = "audio"                     # Vocalisation
    OTHER = "other"                     # Autre


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class FieldObservation:
    """
    Observation terrain pour la calibration BIONIC V5.
    
    Cette structure capture toutes les informations nécessaires
    pour valider et calibrer les prédictions du moteur.
    """
    
    # =================================================================
    # CHAMPS REQUIS (SANS VALEUR PAR DÉFAUT)
    # =================================================================
    
    observation_id: str
    species: ObservedSpecies
    latitude: float
    longitude: float
    
    # =================================================================
    # CHAMPS OPTIONNELS (AVEC VALEUR PAR DÉFAUT)
    # =================================================================
    
    # Espèce - comptage
    species_count: int = 1
    
    # Position GPS - optionnels
    altitude_m: Optional[float] = None
    gps_accuracy_m: Optional[float] = None
    
    # Horodatage
    observation_datetime: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    duration_minutes: Optional[int] = None
    
    # Comportement
    behavior: ObservedBehavior = ObservedBehavior.UNKNOWN
    behavior_details: str = ""
    
    # =================================================================
    # DONNÉES COMPLÉMENTAIRES
    # =================================================================
    
    # Conditions météo
    weather: WeatherCondition = WeatherCondition.CLEAR
    temperature_c: Optional[float] = None
    wind_speed_kmh: Optional[float] = None
    
    # Source et qualité
    source: ObservationSource = ObservationSource.DIRECT_VISUAL
    confidence: ObservationConfidence = ObservationConfidence.MEDIUM
    
    # Notes libres
    notes: str = ""
    
    # =================================================================
    # CONTEXTE PRÉDICTIF (pour calibration)
    # =================================================================
    
    # Était-ce prédit par BIONIC?
    was_predicted: bool = False
    predicted_zone_id: Optional[str] = None
    predicted_score: Optional[float] = None
    
    # Analyse du contexte
    habitat_observed: Optional[str] = None
    terrain_type: Optional[str] = None
    vegetation_type: Optional[str] = None
    
    # =================================================================
    # MÉTADONNÉES
    # =================================================================
    
    # Identité de l'observateur
    observer_id: Optional[str] = None
    observer_name: Optional[str] = None
    
    # Statut
    is_validated: bool = False
    validated_by: Optional[str] = None
    validated_at: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    
    # Traçabilité BIONIC V5
    source_ids: List[str] = field(default_factory=lambda: ["SRC-OBSERVATION-TERRAIN"])
    version: str = "7.0.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire pour l'API."""
        return {
            "observation_id": self.observation_id,
            "species": {
                "type": self.species.value,
                "count": self.species_count
            },
            "location": {
                "latitude": self.latitude,
                "longitude": self.longitude,
                "altitude_m": self.altitude_m,
                "gps_accuracy_m": self.gps_accuracy_m
            },
            "timing": {
                "datetime": self.observation_datetime.isoformat(),
                "duration_minutes": self.duration_minutes
            },
            "behavior": {
                "type": self.behavior.value,
                "details": self.behavior_details
            },
            "conditions": {
                "weather": self.weather.value,
                "temperature_c": self.temperature_c,
                "wind_speed_kmh": self.wind_speed_kmh
            },
            "source": {
                "type": self.source.value,
                "confidence": self.confidence.value
            },
            "notes": self.notes,
            "prediction_context": {
                "was_predicted": self.was_predicted,
                "predicted_zone_id": self.predicted_zone_id,
                "predicted_score": self.predicted_score
            },
            "habitat": {
                "observed": self.habitat_observed,
                "terrain_type": self.terrain_type,
                "vegetation_type": self.vegetation_type
            },
            "observer": {
                "id": self.observer_id,
                "name": self.observer_name
            },
            "validation": {
                "is_validated": self.is_validated,
                "validated_by": self.validated_by,
                "validated_at": self.validated_at.isoformat() if self.validated_at else None
            },
            "metadata": {
                "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat() if self.updated_at else None,
                "source_ids": self.source_ids,
                "version": self.version
            }
        }


# =============================================================================
# OBSERVATION REGISTRY
# =============================================================================

class ObservationRegistry:
    """
    Registre des observations terrain pour PHASE F.
    
    Gère le stockage et la validation des observations.
    Intègre avec le CalibrationRegistry pour la calibration MASTER.
    """
    
    def __init__(self):
        self._version = "7.0.0"
        self._observation_counter = 0
        
        # Stockage des observations
        self._observations: Dict[str, FieldObservation] = {}
        
        logger.info(f"ObservationRegistry initialized: v{self._version}")
    
    def _generate_observation_id(self) -> str:
        """Génère un ID unique pour une observation."""
        self._observation_counter += 1
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"OBS-{timestamp}-{self._observation_counter:04d}"
    
    def create_observation(
        self,
        species: str,
        latitude: float,
        longitude: float,
        behavior: str = "unknown",
        observation_datetime: Optional[datetime] = None,
        species_count: int = 1,
        behavior_details: str = "",
        weather: str = "clear",
        temperature_c: Optional[float] = None,
        wind_speed_kmh: Optional[float] = None,
        source: str = "direct_visual",
        confidence: str = "medium",
        notes: str = "",
        observer_id: Optional[str] = None,
        observer_name: Optional[str] = None,
        habitat_observed: Optional[str] = None,
        terrain_type: Optional[str] = None,
        vegetation_type: Optional[str] = None
    ) -> FieldObservation:
        """
        Crée une nouvelle observation terrain.
        
        Returns:
            FieldObservation créée
        """
        # Convertir les enums
        try:
            species_enum = ObservedSpecies(species.lower())
        except ValueError:
            species_enum = ObservedSpecies.OTHER
        
        try:
            behavior_enum = ObservedBehavior(behavior.lower())
        except ValueError:
            behavior_enum = ObservedBehavior.UNKNOWN
        
        try:
            weather_enum = WeatherCondition(weather.lower())
        except ValueError:
            weather_enum = WeatherCondition.CLEAR
        
        try:
            source_enum = ObservationSource(source.lower())
        except ValueError:
            source_enum = ObservationSource.OTHER
        
        try:
            confidence_enum = ObservationConfidence(confidence.lower())
        except ValueError:
            confidence_enum = ObservationConfidence.MEDIUM
        
        observation = FieldObservation(
            observation_id=self._generate_observation_id(),
            species=species_enum,
            species_count=species_count,
            latitude=latitude,
            longitude=longitude,
            observation_datetime=observation_datetime or datetime.now(timezone.utc),
            behavior=behavior_enum,
            behavior_details=behavior_details,
            weather=weather_enum,
            temperature_c=temperature_c,
            wind_speed_kmh=wind_speed_kmh,
            source=source_enum,
            confidence=confidence_enum,
            notes=notes,
            observer_id=observer_id,
            observer_name=observer_name,
            habitat_observed=habitat_observed,
            terrain_type=terrain_type,
            vegetation_type=vegetation_type
        )
        
        # Stocker
        self._observations[observation.observation_id] = observation
        
        logger.info(f"Observation created: {observation.observation_id} ({species_enum.value} at {latitude:.4f}, {longitude:.4f})")
        
        return observation
    
    def get_observation(self, observation_id: str) -> Optional[FieldObservation]:
        """Récupère une observation par son ID."""
        return self._observations.get(observation_id)
    
    def list_observations(
        self,
        species: Optional[str] = None,
        validated_only: bool = False,
        limit: int = 100
    ) -> List[FieldObservation]:
        """
        Liste les observations avec filtres optionnels.
        """
        observations = list(self._observations.values())
        
        if species:
            try:
                species_enum = ObservedSpecies(species.lower())
                observations = [o for o in observations if o.species == species_enum]
            except ValueError:
                pass
        
        if validated_only:
            observations = [o for o in observations if o.is_validated]
        
        # Trier par date décroissante
        observations.sort(key=lambda x: x.observation_datetime, reverse=True)
        
        return observations[:limit]
    
    def validate_observation(
        self,
        observation_id: str,
        validated_by: str
    ) -> Optional[FieldObservation]:
        """
        Valide une observation pour inclusion dans la calibration.
        """
        obs = self._observations.get(observation_id)
        if obs:
            obs.is_validated = True
            obs.validated_by = validated_by
            obs.validated_at = datetime.now(timezone.utc)
            obs.updated_at = datetime.now(timezone.utc)
            
            logger.info(f"Observation validated: {observation_id} by {validated_by}")
            
            return obs
        
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Statistiques du registre."""
        observations = list(self._observations.values())
        validated = [o for o in observations if o.is_validated]
        
        species_counts = {}
        for obs in observations:
            sp = obs.species.value
            species_counts[sp] = species_counts.get(sp, 0) + 1
        
        behavior_counts = {}
        for obs in observations:
            bh = obs.behavior.value
            behavior_counts[bh] = behavior_counts.get(bh, 0) + 1
        
        return {
            "version": self._version,
            "total_observations": len(observations),
            "validated_observations": len(validated),
            "validation_rate": round(len(validated) / len(observations) * 100, 1) if observations else 0,
            "by_species": species_counts,
            "by_behavior": behavior_counts,
            "last_observation": observations[0].observation_datetime.isoformat() if observations else None
        }


# =============================================================================
# SINGLETON
# =============================================================================

_registry_instance: Optional[ObservationRegistry] = None


def get_observation_registry() -> ObservationRegistry:
    """Obtenir l'instance singleton du registre."""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = ObservationRegistry()
    return _registry_instance


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    'ObservedSpecies',
    'ObservedBehavior',
    'ObservationConfidence',
    'WeatherCondition',
    'ObservationSource',
    # Models
    'FieldObservation',
    # Registry
    'ObservationRegistry',
    'get_observation_registry'
]
