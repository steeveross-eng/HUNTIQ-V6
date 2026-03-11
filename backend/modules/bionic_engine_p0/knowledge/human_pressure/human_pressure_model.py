"""
BIONIC V5 — HUMAN PRESSURE MODEL (PRES-HUMAN)
==============================================
NIVEAU 3 — Pression Humaine Réelle

Module complet pour modéliser la pression humaine:
1. Densité humaine (nombre d'observations/km²)
2. Fréquence (single, occasional, regular, heavy)
3. Temporalité (heures/jours de pression)
4. Intensité (faible/moyenne/forte)

KNOWLEDGE LAYER INTEGRATION:
- Données terrain: GPS chasseurs, caméras, traces humaines
- Zones d'évitement dynamiques
- Synchronisation avec modèles saisonniers (hunting_pressure)
- Modulation par espèce et saison

CENTRALISATION:
- Ce module FOURNIT les règles au UnifiedScoringService
- AUCUNE logique de scoring locale
- Traçabilité obligatoire (source_ids, version)

VERSION: 1.0.0
Conformité: G-SEC | G-QA | G-DOC | BIONIC V5 NIVEAU 3
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import logging
import math

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS
# =============================================================================

class HumanPressureIntensity(str, Enum):
    """Intensité de la pression humaine"""
    NONE = "none"           # Aucune pression détectée
    LOW = "low"             # Faible (1-2 traces/km²)
    MODERATE = "moderate"   # Modérée (3-5 traces/km²)
    HIGH = "high"           # Forte (6-10 traces/km²)
    EXTREME = "extreme"     # Extrême (>10 traces/km²)


class HumanActivityType(str, Enum):
    """Types d'activité humaine"""
    HUNTING = "hunting"                 # Chasse active
    SCOUTING = "scouting"              # Repérage/reconnaissance
    RECREATION = "recreation"           # Loisirs (randonnée, VTT)
    FORESTRY = "forestry"              # Exploitation forestière
    AGRICULTURE = "agriculture"         # Agriculture
    RESIDENTIAL = "residential"         # Zone résidentielle
    INFRASTRUCTURE = "infrastructure"   # Routes, lignes électriques


class TemporalPattern(str, Enum):
    """Patterns temporels de pression"""
    DAWN = "dawn"           # Aube (lever du soleil - 2h)
    MORNING = "morning"     # Matin (8h-12h)
    MIDDAY = "midday"       # Mi-journée (12h-14h)
    AFTERNOON = "afternoon" # Après-midi (14h-17h)
    DUSK = "dusk"           # Crépuscule (coucher du soleil - 2h)
    NIGHT = "night"         # Nuit
    WEEKEND = "weekend"     # Week-end
    WEEKDAY = "weekday"     # Semaine


class AvoidanceZoneType(str, Enum):
    """Types de zones d'évitement"""
    STATIC = "static"       # Zone fixe (route, village)
    DYNAMIC = "dynamic"     # Zone dynamique (pression de chasse)
    TEMPORAL = "temporal"   # Zone temporelle (heures de chasse)
    SEASONAL = "seasonal"   # Zone saisonnière (saison de chasse)


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class HumanPressureObservation:
    """
    Observation de pression humaine ponctuelle.
    
    Source: Données terrain (GPS, caméras, traces)
    """
    
    observation_id: str = ""
    
    # Localisation
    latitude: float = 0.0
    longitude: float = 0.0
    
    # Temporel
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Type d'activité
    activity_type: HumanActivityType = HumanActivityType.HUNTING
    
    # Détails
    observer_count: int = 1
    vehicle_present: bool = False
    duration_minutes: float = 0.0
    
    # Qualité
    confidence: float = 0.7
    data_source: str = "terrain"  # "terrain", "gps", "camera"
    
    # Traçabilité
    source_id: str = "SRC-PRES-HUMAN"


@dataclass
class AvoidanceZone:
    """
    Zone d'évitement dynamique pour la faune.
    
    Calculée à partir des observations de pression humaine.
    """
    
    zone_id: str = ""
    
    # Centre et rayon
    center_lat: float = 0.0
    center_lng: float = 0.0
    radius_m: float = 300.0  # Rayon d'évitement par défaut
    
    # Type
    zone_type: AvoidanceZoneType = AvoidanceZoneType.DYNAMIC
    
    # Intensité
    intensity: HumanPressureIntensity = HumanPressureIntensity.MODERATE
    pressure_score: float = 50.0  # 0-100
    
    # Temporalité
    active_hours: List[int] = field(default_factory=list)
    active_days: List[int] = field(default_factory=list)  # 0=lundi, 6=dimanche
    
    # Validité
    valid_from: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    valid_until: datetime = field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=7))
    
    # Impact sur espèce
    species_impact: Dict[str, float] = field(default_factory=dict)  # {species: modifier}
    
    # Traçabilité
    source_ids: List[str] = field(default_factory=lambda: ["SRC-PRES-HUMAN-ZONE"])
    version: str = "1.0.0"
    
    def is_active(self, check_datetime: datetime = None) -> bool:
        """Vérifie si la zone est active à un moment donné."""
        if check_datetime is None:
            check_datetime = datetime.now(timezone.utc)
        
        # Vérifier la validité temporelle
        if not (self.valid_from <= check_datetime <= self.valid_until):
            return False
        
        # Vérifier les heures actives
        if self.active_hours and check_datetime.hour not in self.active_hours:
            return False
        
        # Vérifier les jours actifs
        if self.active_days and check_datetime.weekday() not in self.active_days:
            return False
        
        return True
    
    def get_modifier_for_species(self, species: str) -> float:
        """Retourne le modificateur pour une espèce donnée."""
        return self.species_impact.get(species.lower(), 1.0)


@dataclass
class HumanPressureModel:
    """
    Modèle complet de pression humaine pour une zone.
    
    Agrège les observations et calcule les métriques PRES-HUMAN.
    """
    
    model_id: str = ""
    
    # Zone couverte
    center_lat: float = 0.0
    center_lng: float = 0.0
    radius_km: float = 5.0
    
    # Métriques calculées
    density_per_km2: float = 0.0              # Densité d'observations
    frequency: str = "single"                  # single, occasional, regular, heavy
    intensity: HumanPressureIntensity = HumanPressureIntensity.NONE
    
    # Patterns temporels
    peak_hours: List[int] = field(default_factory=list)
    peak_days: List[int] = field(default_factory=list)
    temporal_distribution: Dict[str, float] = field(default_factory=dict)
    
    # Types d'activité présents
    activity_types: Dict[HumanActivityType, int] = field(default_factory=dict)
    dominant_activity: Optional[HumanActivityType] = None
    
    # Score global
    pressure_score: float = 0.0  # 0-100 (100 = pression maximale)
    
    # Zones d'évitement générées
    avoidance_zones: List[AvoidanceZone] = field(default_factory=list)
    
    # Modificateurs par espèce
    species_modifiers: Dict[str, float] = field(default_factory=dict)
    
    # Métadonnées
    observation_count: int = 0
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Traçabilité
    source_ids: List[str] = field(default_factory=lambda: ["SRC-PRES-HUMAN"])
    version: str = "1.0.0"
    confidence: float = 0.7


@dataclass
class SpeciesHumanPressureResponse:
    """
    Réponse comportementale d'une espèce à la pression humaine.
    
    Knowledge Layer: Règles par espèce.
    """
    
    species: str = ""
    
    # Seuils de tolérance
    tolerance_threshold: HumanPressureIntensity = HumanPressureIntensity.MODERATE
    
    # Distances d'évitement par type d'activité
    avoidance_distances_m: Dict[HumanActivityType, float] = field(default_factory=dict)
    
    # Modificateurs comportementaux
    activity_reduction_factor: float = 0.7    # Réduction d'activité diurne
    movement_increase_factor: float = 1.3     # Augmentation mouvements évasifs
    night_shift_threshold: float = 0.6        # Seuil pour shift nocturne
    
    # Patterns d'évitement
    avoidance_patterns: List[str] = field(default_factory=list)
    recovery_time_hours: float = 24.0         # Temps de récupération après perturbation
    
    # Saisonnalité
    vulnerability_by_season: Dict[str, float] = field(default_factory=dict)
    
    # Traçabilité
    source_ids: List[str] = field(default_factory=list)
    version: str = "1.0.0"


# =============================================================================
# HUMAN PRESSURE REGISTRY
# =============================================================================

class HumanPressureRegistry:
    """
    Registre centralisé du modèle PRES-HUMAN.
    
    NIVEAU 3 - Knowledge Layer:
    - Règles de réponse par espèce
    - Calcul des zones d'évitement dynamiques
    - Synchronisation avec modèles saisonniers
    """
    
    def __init__(self):
        self._species_responses: Dict[str, SpeciesHumanPressureResponse] = {}
        self._observations: List[HumanPressureObservation] = []
        self._avoidance_zones: Dict[str, AvoidanceZone] = {}
        self._pressure_models: Dict[str, HumanPressureModel] = {}
        
        self._version = "1.0.0"
        self._initialize_species_responses()
        self._initialize_demo_observations()
        
        logger.info(f"HumanPressureRegistry initialized: "
                   f"{len(self._species_responses)} species, "
                   f"{len(self._observations)} observations, "
                   f"{len(self._avoidance_zones)} zones")
    
    def _initialize_species_responses(self):
        """Initialiser les réponses par espèce à la pression humaine."""
        
        # =====================================================
        # ORIGNAL (MOOSE) — Réponse à la pression humaine
        # =====================================================
        
        self._species_responses["moose"] = SpeciesHumanPressureResponse(
            species="moose",
            tolerance_threshold=HumanPressureIntensity.LOW,  # Très sensible
            avoidance_distances_m={
                HumanActivityType.HUNTING: 800,      # Très grand évitement
                HumanActivityType.SCOUTING: 500,
                HumanActivityType.RECREATION: 400,
                HumanActivityType.FORESTRY: 600,
                HumanActivityType.AGRICULTURE: 300,
                HumanActivityType.RESIDENTIAL: 1000,
                HumanActivityType.INFRASTRUCTURE: 200
            },
            activity_reduction_factor=0.5,     # Forte réduction activité diurne
            movement_increase_factor=1.5,      # Augmentation mouvements évasifs
            night_shift_threshold=0.5,         # Shift nocturne facile
            avoidance_patterns=[
                "Évite zones de chasse actives",
                "Shift vers comportement nocturne",
                "Recherche refuges denses",
                "Utilisation corridors alternatifs"
            ],
            recovery_time_hours=48.0,          # Récupération lente
            vulnerability_by_season={
                "rut": 0.8,           # Moins prudent pendant le rut
                "pre_rut": 0.9,
                "hunting_season": 1.5, # Très vulnérable
                "calving": 1.3,
                "default": 1.0
            },
            source_ids=["SRC-LAVAL-001", "SRC-MFFP-001", "SRC-GPS-HUNT-001"],
            version="1.0.0"
        )
        
        # =====================================================
        # CERF DE VIRGINIE (DEER) — Réponse à la pression humaine
        # =====================================================
        
        self._species_responses["deer"] = SpeciesHumanPressureResponse(
            species="deer",
            tolerance_threshold=HumanPressureIntensity.MODERATE,  # Plus tolérant
            avoidance_distances_m={
                HumanActivityType.HUNTING: 500,
                HumanActivityType.SCOUTING: 300,
                HumanActivityType.RECREATION: 200,
                HumanActivityType.FORESTRY: 400,
                HumanActivityType.AGRICULTURE: 150,  # Habitué aux champs
                HumanActivityType.RESIDENTIAL: 300,
                HumanActivityType.INFRASTRUCTURE: 100
            },
            activity_reduction_factor=0.6,     # Réduction modérée
            movement_increase_factor=1.4,
            night_shift_threshold=0.6,
            avoidance_patterns=[
                "Shift nocturne rapide",
                "Utilisation couvert dense",
                "Mouvements imprévisibles",
                "Réduction zone de déplacement"
            ],
            recovery_time_hours=24.0,          # Récupération plus rapide
            vulnerability_by_season={
                "rut": 0.7,           # Mâles moins prudents
                "hunting_season": 1.4,
                "fawning": 1.2,
                "default": 1.0
            },
            source_ids=["SRC-NDA-001", "SRC-QDMA-001", "SRC-MFFP-001"],
            version="1.0.0"
        )
        
        # =====================================================
        # OURS NOIR (BEAR) — Réponse à la pression humaine
        # =====================================================
        
        self._species_responses["bear"] = SpeciesHumanPressureResponse(
            species="bear",
            tolerance_threshold=HumanPressureIntensity.MODERATE,
            avoidance_distances_m={
                HumanActivityType.HUNTING: 400,
                HumanActivityType.SCOUTING: 300,
                HumanActivityType.RECREATION: 250,
                HumanActivityType.FORESTRY: 350,
                HumanActivityType.AGRICULTURE: 200,
                HumanActivityType.RESIDENTIAL: 500,
                HumanActivityType.INFRASTRUCTURE: 150
            },
            activity_reduction_factor=0.7,
            movement_increase_factor=1.3,
            night_shift_threshold=0.7,
            avoidance_patterns=[
                "Shift nocturne",
                "Évitement actif des zones humaines",
                "Utilisation corridors denses"
            ],
            recovery_time_hours=36.0,
            vulnerability_by_season={
                "hyperphagia": 0.8,    # Moins prudent (faim)
                "default": 1.0
            },
            source_ids=["SRC-PARCS-001", "SRC-MFFP-001"],
            version="1.0.0"
        )
    
    def _initialize_demo_observations(self):
        """Initialiser des observations de démonstration."""
        
        demo_observations = [
            HumanPressureObservation(
                observation_id="OBS-HUNT-001",
                latitude=46.8300,
                longitude=-71.2100,
                timestamp=datetime(2025, 9, 20, 6, 30, tzinfo=timezone.utc),
                activity_type=HumanActivityType.HUNTING,
                observer_count=1,
                vehicle_present=True,
                duration_minutes=180.0,
                confidence=0.9,
                data_source="gps",
                source_id="SRC-GPS-HUNT-001"
            ),
            HumanPressureObservation(
                observation_id="OBS-HUNT-002",
                latitude=46.8350,
                longitude=-71.2150,
                timestamp=datetime(2025, 9, 20, 7, 0, tzinfo=timezone.utc),
                activity_type=HumanActivityType.HUNTING,
                observer_count=2,
                vehicle_present=True,
                duration_minutes=240.0,
                confidence=0.85,
                data_source="camera",
                source_id="SRC-TERRAIN-CAM"
            ),
            HumanPressureObservation(
                observation_id="OBS-SCOUT-001",
                latitude=46.8200,
                longitude=-71.1900,
                timestamp=datetime(2025, 9, 15, 15, 0, tzinfo=timezone.utc),
                activity_type=HumanActivityType.SCOUTING,
                observer_count=1,
                vehicle_present=False,
                duration_minutes=60.0,
                confidence=0.7,
                data_source="terrain",
                source_id="SRC-TERRAIN-HUMAN"
            )
        ]
        
        self._observations = demo_observations
        
        # Créer une zone d'évitement de démonstration
        demo_zone = AvoidanceZone(
            zone_id="ZONE-HUNT-001",
            center_lat=46.8325,
            center_lng=-71.2125,
            radius_m=500,
            zone_type=AvoidanceZoneType.DYNAMIC,
            intensity=HumanPressureIntensity.HIGH,
            pressure_score=75.0,
            active_hours=[5, 6, 7, 16, 17, 18, 19],  # Heures de chasse
            active_days=[5, 6],  # Week-end
            valid_from=datetime(2025, 9, 13, 0, 0, tzinfo=timezone.utc),
            valid_until=datetime(2025, 11, 15, 23, 59, tzinfo=timezone.utc),
            species_impact={
                "moose": 0.4,  # Forte réduction score
                "deer": 0.5,
                "bear": 0.6
            },
            source_ids=["SRC-GPS-HUNT-001", "SRC-TERRAIN-CAM", "SRC-TERRAIN-HUMAN"]
        )
        
        self._avoidance_zones[demo_zone.zone_id] = demo_zone
    
    # =========================================================================
    # MÉTHODES PRINCIPALES — Knowledge Layer
    # =========================================================================
    
    def get_species_response(self, species: str) -> Optional[SpeciesHumanPressureResponse]:
        """Obtenir la réponse d'une espèce à la pression humaine."""
        return self._species_responses.get(species.lower())
    
    def get_avoidance_distance(
        self,
        species: str,
        activity_type: HumanActivityType
    ) -> Tuple[float, List[str]]:
        """
        Obtenir la distance d'évitement pour une espèce et type d'activité.
        
        Returns:
            Tuple[distance_m, source_ids]
        """
        response = self.get_species_response(species)
        if not response:
            return 300.0, []  # Défaut
        
        distance = response.avoidance_distances_m.get(activity_type, 300.0)
        return distance, response.source_ids
    
    def get_pressure_modifier(
        self,
        species: str,
        intensity: HumanPressureIntensity,
        season: str = "default"
    ) -> Tuple[float, List[str]]:
        """
        Calculer le modificateur de pression pour une espèce.
        
        NIVEAU 3 BIONIC V5:
        - Utilisé par UnifiedScoringService pour modifier le score
        - Intègre la sensibilité espèce × saison × intensité
        
        Returns:
            Tuple[modifier, source_ids]
        """
        response = self.get_species_response(species)
        if not response:
            return 1.0, []
        
        # Modificateur de base selon intensité
        intensity_modifiers = {
            HumanPressureIntensity.NONE: 1.0,
            HumanPressureIntensity.LOW: 0.9,
            HumanPressureIntensity.MODERATE: 0.7,
            HumanPressureIntensity.HIGH: 0.5,
            HumanPressureIntensity.EXTREME: 0.3
        }
        
        base_modifier = intensity_modifiers.get(intensity, 1.0)
        
        # Ajustement saisonnier
        season_vulnerability = response.vulnerability_by_season.get(season, 1.0)
        
        # Combiner
        final_modifier = base_modifier / season_vulnerability
        final_modifier = max(0.1, min(1.5, final_modifier))  # Clamp 0.1-1.5
        
        return final_modifier, response.source_ids
    
    def calculate_pressure_at_point(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 1.0,
        check_datetime: datetime = None
    ) -> HumanPressureModel:
        """
        Calculer le modèle de pression humaine à un point.
        
        NIVEAU 3 BIONIC V5:
        - Agrège les observations dans le rayon
        - Calcule densité, fréquence, intensité
        - Génère les zones d'évitement
        
        Returns:
            HumanPressureModel complet
        """
        if check_datetime is None:
            check_datetime = datetime.now(timezone.utc)
        
        # Filtrer les observations dans le rayon (simplifié)
        # TODO: Calcul de distance géographique réel
        relevant_observations = []
        for obs in self._observations:
            # Approximation simple pour la démo
            dist_lat = abs(obs.latitude - latitude)
            dist_lng = abs(obs.longitude - longitude)
            approx_dist_km = math.sqrt(dist_lat**2 + dist_lng**2) * 111  # ~111km par degré
            
            if approx_dist_km <= radius_km:
                relevant_observations.append(obs)
        
        # Calculer les métriques
        observation_count = len(relevant_observations)
        area_km2 = math.pi * radius_km ** 2
        density = observation_count / area_km2 if area_km2 > 0 else 0
        
        # Déterminer la fréquence
        if observation_count == 0:
            frequency = "none"
        elif observation_count <= 2:
            frequency = "single"
        elif observation_count <= 5:
            frequency = "occasional"
        elif observation_count <= 10:
            frequency = "regular"
        else:
            frequency = "heavy"
        
        # Déterminer l'intensité
        if density == 0:
            intensity = HumanPressureIntensity.NONE
        elif density < 2:
            intensity = HumanPressureIntensity.LOW
        elif density < 5:
            intensity = HumanPressureIntensity.MODERATE
        elif density < 10:
            intensity = HumanPressureIntensity.HIGH
        else:
            intensity = HumanPressureIntensity.EXTREME
        
        # Calculer le score de pression (0-100)
        pressure_score = min(100, density * 15 + observation_count * 5)
        
        # Identifier les heures de pic
        hours_count = {}
        for obs in relevant_observations:
            h = obs.timestamp.hour
            hours_count[h] = hours_count.get(h, 0) + 1
        peak_hours = sorted(hours_count.keys(), key=lambda x: hours_count[x], reverse=True)[:4]
        
        # Compter les types d'activité
        activity_counts = {}
        for obs in relevant_observations:
            activity_counts[obs.activity_type] = activity_counts.get(obs.activity_type, 0) + 1
        
        dominant_activity = max(activity_counts.keys(), key=lambda x: activity_counts[x]) if activity_counts else None
        
        # Calculer les modificateurs par espèce
        species_modifiers = {}
        for species in ["moose", "deer", "bear"]:
            modifier, _ = self.get_pressure_modifier(species, intensity)
            species_modifiers[species] = modifier
        
        # Collecter les zones d'évitement actives
        active_zones = [
            zone for zone in self._avoidance_zones.values()
            if zone.is_active(check_datetime)
        ]
        
        # Créer le modèle
        model = HumanPressureModel(
            model_id=f"PRES-{check_datetime.strftime('%Y%m%d%H%M%S')}",
            center_lat=latitude,
            center_lng=longitude,
            radius_km=radius_km,
            density_per_km2=density,
            frequency=frequency,
            intensity=intensity,
            peak_hours=peak_hours,
            peak_days=[5, 6] if dominant_activity == HumanActivityType.HUNTING else [],
            temporal_distribution={
                "dawn": 0.35,
                "dusk": 0.30,
                "morning": 0.15,
                "afternoon": 0.15,
                "night": 0.05
            },
            activity_types=activity_counts,
            dominant_activity=dominant_activity,
            pressure_score=pressure_score,
            avoidance_zones=active_zones,
            species_modifiers=species_modifiers,
            observation_count=observation_count,
            period_start=min([o.timestamp for o in relevant_observations], default=check_datetime),
            period_end=max([o.timestamp for o in relevant_observations], default=check_datetime),
            last_updated=check_datetime,
            source_ids=list(set(o.source_id for o in relevant_observations)) + ["SRC-PRES-HUMAN"],
            version="1.0.0",
            confidence=0.7 if observation_count > 0 else 0.3
        )
        
        return model
    
    def get_hunting_pressure_modifier(
        self,
        species: str,
        latitude: float,
        longitude: float,
        check_datetime: datetime = None,
        hunting_pressure_detected: bool = False
    ) -> Tuple[float, Dict[str, Any], List[str]]:
        """
        NIVEAU 3 BIONIC V5 — Méthode principale pour UnifiedScoringService
        
        Calcule le modificateur de pression de chasse pour le pipeline de scoring.
        
        Args:
            species: Espèce cible
            latitude: Latitude du point
            longitude: Longitude du point
            check_datetime: Date/heure de vérification
            hunting_pressure_detected: Pression détectée sur terrain (données réelles)
            
        Returns:
            Tuple[modifier, details, source_ids]
        """
        if check_datetime is None:
            check_datetime = datetime.now(timezone.utc)
        
        # Calculer le modèle de pression au point
        pressure_model = self.calculate_pressure_at_point(
            latitude, longitude, radius_km=2.0, check_datetime=check_datetime
        )
        
        # Obtenir le modificateur espèce
        species_modifier = pressure_model.species_modifiers.get(species.lower(), 1.0)
        
        # Amplifier si pression détectée sur terrain
        if hunting_pressure_detected:
            species_modifier *= 0.7  # Réduction supplémentaire de 30%
        
        # Vérifier les zones d'évitement actives
        in_avoidance_zone = False
        zone_modifier = 1.0
        for zone in pressure_model.avoidance_zones:
            if zone.is_active(check_datetime):
                in_avoidance_zone = True
                zone_modifier = min(zone_modifier, zone.get_modifier_for_species(species))
        
        # Combiner les modificateurs
        final_modifier = species_modifier * zone_modifier
        final_modifier = max(0.1, min(1.5, final_modifier))
        
        # Construire les détails
        details = {
            "pressure_score": pressure_model.pressure_score,
            "intensity": pressure_model.intensity.value,
            "frequency": pressure_model.frequency,
            "density_per_km2": round(pressure_model.density_per_km2, 2),
            "observation_count": pressure_model.observation_count,
            "dominant_activity": pressure_model.dominant_activity.value if pressure_model.dominant_activity else None,
            "peak_hours": pressure_model.peak_hours,
            "in_avoidance_zone": in_avoidance_zone,
            "hunting_pressure_detected": hunting_pressure_detected,
            "species_modifier": round(species_modifier, 3),
            "zone_modifier": round(zone_modifier, 3)
        }
        
        return final_modifier, details, pressure_model.source_ids
    
    # =========================================================================
    # GESTION DES OBSERVATIONS
    # =========================================================================
    
    def add_observation(self, observation: HumanPressureObservation) -> str:
        """Ajouter une observation de pression humaine."""
        self._observations.append(observation)
        return observation.observation_id
    
    def get_observations(
        self,
        activity_type: Optional[HumanActivityType] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[HumanPressureObservation]:
        """Obtenir les observations avec filtres."""
        obs = self._observations
        
        if activity_type:
            obs = [o for o in obs if o.activity_type == activity_type]
        if start_time:
            obs = [o for o in obs if o.timestamp >= start_time]
        if end_time:
            obs = [o for o in obs if o.timestamp <= end_time]
        
        return obs
    
    # =========================================================================
    # GESTION DES ZONES D'ÉVITEMENT
    # =========================================================================
    
    def add_avoidance_zone(self, zone: AvoidanceZone) -> str:
        """Ajouter une zone d'évitement."""
        self._avoidance_zones[zone.zone_id] = zone
        return zone.zone_id
    
    def get_avoidance_zones(
        self,
        zone_type: Optional[AvoidanceZoneType] = None,
        active_only: bool = True,
        check_datetime: datetime = None
    ) -> List[AvoidanceZone]:
        """Obtenir les zones d'évitement avec filtres."""
        zones = list(self._avoidance_zones.values())
        
        if zone_type:
            zones = [z for z in zones if z.zone_type == zone_type]
        
        if active_only:
            if check_datetime is None:
                check_datetime = datetime.now(timezone.utc)
            zones = [z for z in zones if z.is_active(check_datetime)]
        
        return zones
    
    # =========================================================================
    # STATISTIQUES
    # =========================================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques du registre PRES-HUMAN."""
        return {
            "version": self._version,
            "species_responses": len(self._species_responses),
            "observations": len(self._observations),
            "avoidance_zones": len(self._avoidance_zones),
            "pressure_models": len(self._pressure_models),
            "supported_species": list(self._species_responses.keys()),
            "source_ids": [
                "SRC-PRES-HUMAN",
                "SRC-GPS-HUNT-001",
                "SRC-TERRAIN-CAM",
                "SRC-TERRAIN-HUMAN"
            ]
        }


# =============================================================================
# SINGLETON
# =============================================================================

_registry_instance: Optional[HumanPressureRegistry] = None


def get_human_pressure_registry() -> HumanPressureRegistry:
    """Obtenir l'instance singleton du registre PRES-HUMAN."""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = HumanPressureRegistry()
    return _registry_instance


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    'HumanPressureIntensity',
    'HumanActivityType',
    'TemporalPattern',
    'AvoidanceZoneType',
    # Data models
    'HumanPressureObservation',
    'AvoidanceZone',
    'HumanPressureModel',
    'SpeciesHumanPressureResponse',
    # Registry
    'HumanPressureRegistry',
    'get_human_pressure_registry'
]
