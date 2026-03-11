"""
BIONIC V5 — PHASE C.4: HUNTING PRESSURE MODELS
===============================================

Modèles de pression de chasse réelle basés sur données terrain.

Ce module intègre les données de pression de chasse issues de:
- Observations terrain directes
- Données GPS chasseurs (anonymisées)
- Caméras de surveillance
- Traces et indices d'activité humaine
- Statistiques officielles MFFP

TYPES DE PRESSION:
- Pression statique: zones historiquement chassées
- Pression dynamique: activité en temps réel
- Pression cumulative: effet d'accumulation sur la saison

CONFORMITÉ: G-SEC | G-QA | G-DOC | BIONIC V5
TRAÇABILITÉ: source_ids obligatoires
VERSION: 1.0.0
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum

logger = logging.getLogger("bionic_engine.hunting_pressure")


# =============================================================================
# CONSTANTES ET SOURCES
# =============================================================================

SOURCE_IDS = {
    "MFFP_STATS": "SRC-MFFP-HARVEST-001",
    "MFFP_ZONE": "SRC-MFFP-ZONES-001",
    "GPS_HUNTER": "SRC-GPS-HUNTER-ANON-001",
    "TRAIL_CAM": "SRC-TRAIL-CAM-001",
    "TERRAIN": "SRC-TERRAIN-OBS-001",
    "LANDOWNER": "SRC-LANDOWNER-REPORT-001",
    "PERMITS": "SRC-PERMITS-DATA-001",
}


class PressureType(str, Enum):
    """Types de pression de chasse"""
    STATIC = "static"             # Zones historiquement chassées
    DYNAMIC = "dynamic"           # Activité actuelle détectée
    CUMULATIVE = "cumulative"     # Pression accumulée sur la saison
    PREDICTIVE = "predictive"     # Prédiction basée sur patterns


class PressureSource(str, Enum):
    """Sources de la pression"""
    HUNTER_GPS = "hunter_gps"             # Traces GPS chasseurs
    TRAIL_CAMERA = "trail_camera"         # Caméras de surveillance
    VEHICLE_ACCESS = "vehicle_access"     # Accès véhicules
    CAMP_PROXIMITY = "camp_proximity"     # Proximité campements
    GUNSHOT_REPORT = "gunshot_report"     # Rapports coups de feu
    HARVEST_HISTORY = "harvest_history"   # Historique récolte
    SIGN_DISTURBANCE = "sign_disturbance" # Signes de perturbation


class PressureIntensity(str, Enum):
    """Niveaux d'intensité de pression"""
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    EXTREME = "extreme"


class HuntingMethod(str, Enum):
    """Méthodes de chasse affectant la pression"""
    STILL_HUNT = "still_hunt"       # Chasse à l'affût
    DRIVE = "drive"                 # Battue
    CALLING = "calling"             # Appel
    STALKING = "stalking"           # Approche
    DOG_HUNT = "dog_hunt"           # Chasse au chien


@dataclass
class HuntingSeasonConfig:
    """Configuration d'une saison de chasse pour une zone."""
    species: str
    region: str
    zone_code: str
    
    # Dates de saison
    season_start: date
    season_end: date
    
    # Sous-périodes
    archery_start: Optional[date] = None
    archery_end: Optional[date] = None
    muzzleloader_start: Optional[date] = None
    muzzleloader_end: Optional[date] = None
    rifle_start: Optional[date] = None
    rifle_end: Optional[date] = None
    
    # Quotas et permis
    estimated_hunters: int = 0
    permits_issued: int = 0
    harvest_quota: Optional[int] = None
    
    # Méthodes autorisées
    allowed_methods: List[HuntingMethod] = field(default_factory=list)
    
    # Traçabilité
    source_ids: List[str] = field(default_factory=list)
    version: str = "1.0.0"


@dataclass
class PressureZone:
    """
    Zone de pression de chasse avec caractéristiques.
    """
    zone_id: str
    center_lat: float
    center_lng: float
    radius_m: float
    
    # Intensité
    intensity: PressureIntensity
    intensity_score: float  # 0-100
    
    # Sources de pression
    sources: List[PressureSource]
    primary_source: PressureSource
    
    # Timing
    peak_pressure_hours: List[int]
    pressure_days: List[int]  # 0=lundi, 6=dimanche
    
    # Impact comportemental
    activity_modifier: float
    movement_modifier: float
    avoidance_radius_m: float
    
    # Durée de l'effet
    persistence_hours: int  # Combien de temps l'effet persiste après le départ
    
    # Traçabilité
    detection_datetime: datetime
    source_ids: List[str] = field(default_factory=list)
    confidence: float = 0.80
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Exporte en dictionnaire traçable."""
        return {
            "zone_id": self.zone_id,
            "location": {
                "lat": self.center_lat,
                "lng": self.center_lng,
                "radius_m": self.radius_m
            },
            "pressure": {
                "intensity": self.intensity.value,
                "score": self.intensity_score,
                "avoidance_radius_m": self.avoidance_radius_m
            },
            "sources": [s.value for s in self.sources],
            "primary_source": self.primary_source.value,
            "timing": {
                "peak_hours": self.peak_pressure_hours,
                "active_days": self.pressure_days,
                "persistence_hours": self.persistence_hours
            },
            "modifiers": {
                "activity": self.activity_modifier,
                "movement": self.movement_modifier
            },
            "metadata": {
                "detection": self.detection_datetime.isoformat(),
                "source_ids": self.source_ids,
                "confidence": self.confidence
            },
            "notes": self.notes
        }


@dataclass
class HuntingPressureProfile:
    """
    Profil de réponse à la pression de chasse pour une espèce.
    """
    species: str
    
    # Sensibilité à la pression
    sensitivity_level: str  # "high", "moderate", "low"
    
    # Distance de détection (mètres)
    human_detection_distance_m: float
    vehicle_detection_distance_m: float
    gunshot_detection_distance_m: float
    
    # Réponse comportementale
    flight_distance_m: float
    alert_duration_minutes: int
    nocturnal_shift_threshold: PressureIntensity
    
    # Modificateurs par intensité
    modifiers_by_intensity: Dict[PressureIntensity, Dict[str, float]]
    
    # Adaptations
    avoidance_strategies: List[str]
    
    # Zones de refuge préférées
    refuge_preferences: List[str]
    
    # Traçabilité
    source_ids: List[str] = field(default_factory=list)
    confidence: float = 0.85
    version: str = "1.0.0"
    notes: str = ""


# =============================================================================
# REGISTRY DE PRESSION DE CHASSE
# =============================================================================

class HuntingPressureRegistry:
    """
    Registre central de la pression de chasse.
    
    Pipeline BIONIC V5:
    - Intègre données terrain et statistiques officielles
    - Calcule la pression dynamique basée sur observations
    - Traçabilité source_ids obligatoire
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._profiles: Dict[str, HuntingPressureProfile] = {}
        self._seasons: Dict[str, List[HuntingSeasonConfig]] = {}
        self._active_zones: List[PressureZone] = []
        
        self._initialize_profiles()
        self._initialize_seasons()
        self._initialized = True
        
        logger.info(f"[BIONIC] HuntingPressureRegistry initialized: "
                   f"{len(self._profiles)} profiles, {sum(len(s) for s in self._seasons.values())} seasons")
    
    def _initialize_profiles(self):
        """Initialise les profils de réponse à la pression."""
        
        # =====================================================================
        # ORIGNAL
        # =====================================================================
        
        self._profiles["moose"] = HuntingPressureProfile(
            species="moose",
            sensitivity_level="high",
            
            # Distances de détection
            human_detection_distance_m=300,
            vehicle_detection_distance_m=500,
            gunshot_detection_distance_m=2000,
            
            # Réponse
            flight_distance_m=400,
            alert_duration_minutes=120,
            nocturnal_shift_threshold=PressureIntensity.MODERATE,
            
            # Modificateurs
            modifiers_by_intensity={
                PressureIntensity.NONE: {"activity": 1.0, "movement": 1.0},
                PressureIntensity.LOW: {"activity": 0.85, "movement": 0.80},
                PressureIntensity.MODERATE: {"activity": 0.60, "movement": 0.50},
                PressureIntensity.HIGH: {"activity": 0.35, "movement": 0.30},
                PressureIntensity.EXTREME: {"activity": 0.15, "movement": 0.10}
            },
            
            avoidance_strategies=[
                "shift_nocturnal",
                "use_dense_cover",
                "increase_vigilance",
                "relocate_temporarily",
                "reduce_feeding_time"
            ],
            
            refuge_preferences=[
                "dense_conifer",
                "wetland_complex",
                "remote_ridges",
                "island_refugia"
            ],
            
            source_ids=[
                SOURCE_IDS["MFFP_STATS"],
                SOURCE_IDS["GPS_HUNTER"],
                SOURCE_IDS["TERRAIN"]
            ],
            confidence=0.88,
            notes="L'orignal devient très discret et nocturne sous pression de chasse. "
                  "Peut se déplacer de 5-10km pour éviter les zones de haute pression. "
                  "Effet de la pression persiste 24-48h après le départ des chasseurs."
        )
        
        # =====================================================================
        # CERF DE VIRGINIE
        # =====================================================================
        
        self._profiles["deer"] = HuntingPressureProfile(
            species="deer",
            sensitivity_level="high",
            
            human_detection_distance_m=200,
            vehicle_detection_distance_m=350,
            gunshot_detection_distance_m=1500,
            
            flight_distance_m=250,
            alert_duration_minutes=90,
            nocturnal_shift_threshold=PressureIntensity.LOW,
            
            modifiers_by_intensity={
                PressureIntensity.NONE: {"activity": 1.0, "movement": 1.0},
                PressureIntensity.LOW: {"activity": 0.75, "movement": 0.70},
                PressureIntensity.MODERATE: {"activity": 0.50, "movement": 0.40},
                PressureIntensity.HIGH: {"activity": 0.25, "movement": 0.20},
                PressureIntensity.EXTREME: {"activity": 0.10, "movement": 0.05}
            },
            
            avoidance_strategies=[
                "immediate_nocturnal_shift",
                "dense_cover_use",
                "smaller_home_range",
                "reduce_movement",
                "increased_vigilance"
            ],
            
            refuge_preferences=[
                "thick_brush",
                "swamp_edges",
                "steep_terrain",
                "private_lands"
            ],
            
            source_ids=[
                SOURCE_IDS["MFFP_STATS"],
                SOURCE_IDS["TRAIL_CAM"],
                SOURCE_IDS["TERRAIN"]
            ],
            confidence=0.90,
            notes="Le cerf de Virginie réagit très rapidement à la pression de chasse. "
                  "Shift nocturne quasi-immédiat dès le début de la saison. "
                  "Les mâles matures deviennent pratiquement invisibles en journée."
        )
        
        # =====================================================================
        # OURS NOIR
        # =====================================================================
        
        self._profiles["bear"] = HuntingPressureProfile(
            species="bear",
            sensitivity_level="moderate",
            
            human_detection_distance_m=250,
            vehicle_detection_distance_m=400,
            gunshot_detection_distance_m=1800,
            
            flight_distance_m=300,
            alert_duration_minutes=180,
            nocturnal_shift_threshold=PressureIntensity.MODERATE,
            
            modifiers_by_intensity={
                PressureIntensity.NONE: {"activity": 1.0, "movement": 1.0},
                PressureIntensity.LOW: {"activity": 0.90, "movement": 0.85},
                PressureIntensity.MODERATE: {"activity": 0.70, "movement": 0.60},
                PressureIntensity.HIGH: {"activity": 0.45, "movement": 0.40},
                PressureIntensity.EXTREME: {"activity": 0.25, "movement": 0.20}
            },
            
            avoidance_strategies=[
                "avoid_bait_sites",
                "nocturnal_movement",
                "use_escape_terrain",
                "avoid_roads"
            ],
            
            refuge_preferences=[
                "dense_vegetation",
                "steep_terrain",
                "swamp_complex",
                "remote_areas"
            ],
            
            source_ids=[
                SOURCE_IDS["MFFP_STATS"],
                SOURCE_IDS["TRAIL_CAM"]
            ],
            confidence=0.85,
            notes="L'ours noir est moins sensible que les cervidés mais apprend rapidement. "
                  "Évite les sites d'appâtage après avoir été dérangé. "
                  "L'hyperphagie automnale peut pousser à prendre plus de risques."
        )
        
        # =====================================================================
        # WAPITI
        # =====================================================================
        
        self._profiles["elk"] = HuntingPressureProfile(
            species="elk",
            sensitivity_level="moderate",
            
            human_detection_distance_m=400,
            vehicle_detection_distance_m=600,
            gunshot_detection_distance_m=2500,
            
            flight_distance_m=500,
            alert_duration_minutes=240,
            nocturnal_shift_threshold=PressureIntensity.MODERATE,
            
            modifiers_by_intensity={
                PressureIntensity.NONE: {"activity": 1.0, "movement": 1.0},
                PressureIntensity.LOW: {"activity": 0.80, "movement": 0.75},
                PressureIntensity.MODERATE: {"activity": 0.55, "movement": 0.50},
                PressureIntensity.HIGH: {"activity": 0.30, "movement": 0.25},
                PressureIntensity.EXTREME: {"activity": 0.15, "movement": 0.10}
            },
            
            avoidance_strategies=[
                "herd_consolidation",
                "move_to_refuge",
                "increased_vigilance",
                "nocturnal_feeding"
            ],
            
            refuge_preferences=[
                "high_elevation",
                "dense_timber",
                "private_ranches",
                "park_boundaries"
            ],
            
            source_ids=[
                SOURCE_IDS["MFFP_STATS"],
                SOURCE_IDS["GPS_HUNTER"]
            ],
            confidence=0.84,
            notes="Les hardes de wapitis peuvent se déplacer de plusieurs kilomètres sous pression. "
                  "Utilisent souvent des refuges (parcs, terres privées) pendant la saison de chasse. "
                  "Les mâles en rut restent plus vulnérables malgré la pression."
        )
    
    def _initialize_seasons(self):
        """Initialise les configurations de saisons de chasse."""
        
        # Orignal - Québec (exemple zones 1-10)
        self._seasons["moose"] = [
            HuntingSeasonConfig(
                species="moose",
                region="CA-QC",
                zone_code="QC-ZONE-1",
                season_start=date(2025, 9, 27),
                season_end=date(2025, 10, 12),
                archery_start=date(2025, 9, 13),
                archery_end=date(2025, 9, 26),
                estimated_hunters=15000,
                permits_issued=18500,
                allowed_methods=[
                    HuntingMethod.STILL_HUNT,
                    HuntingMethod.CALLING,
                    HuntingMethod.STALKING
                ],
                source_ids=[SOURCE_IDS["MFFP_STATS"], SOURCE_IDS["PERMITS"]]
            ),
            HuntingSeasonConfig(
                species="moose",
                region="CA-QC",
                zone_code="QC-ZONE-10",
                season_start=date(2025, 10, 11),
                season_end=date(2025, 10, 26),
                archery_start=date(2025, 9, 20),
                archery_end=date(2025, 10, 10),
                estimated_hunters=8000,
                permits_issued=9500,
                allowed_methods=[
                    HuntingMethod.STILL_HUNT,
                    HuntingMethod.CALLING
                ],
                source_ids=[SOURCE_IDS["MFFP_STATS"], SOURCE_IDS["PERMITS"]]
            )
        ]
        
        # Cerf - Québec
        self._seasons["deer"] = [
            HuntingSeasonConfig(
                species="deer",
                region="CA-QC",
                zone_code="QC-ZONE-6",
                season_start=date(2025, 11, 1),
                season_end=date(2025, 11, 15),
                archery_start=date(2025, 10, 1),
                archery_end=date(2025, 10, 31),
                muzzleloader_start=date(2025, 11, 16),
                muzzleloader_end=date(2025, 11, 30),
                estimated_hunters=45000,
                harvest_quota=25000,
                allowed_methods=[
                    HuntingMethod.STILL_HUNT,
                    HuntingMethod.DRIVE,
                    HuntingMethod.STALKING
                ],
                source_ids=[SOURCE_IDS["MFFP_STATS"], SOURCE_IDS["PERMITS"]]
            )
        ]
    
    # =========================================================================
    # MÉTHODES PUBLIQUES
    # =========================================================================
    
    def get_profile(self, species: str) -> Optional[HuntingPressureProfile]:
        """Récupère le profil de réponse à la pression pour une espèce."""
        return self._profiles.get(species)
    
    def get_seasons(self, species: str, region: Optional[str] = None) -> List[HuntingSeasonConfig]:
        """Récupère les configurations de saison pour une espèce."""
        seasons = self._seasons.get(species, [])
        if region:
            seasons = [s for s in seasons if s.region == region]
        return seasons
    
    def is_hunting_season(
        self, 
        species: str, 
        region: str, 
        check_date: date
    ) -> Tuple[bool, Optional[HuntingSeasonConfig]]:
        """Vérifie si c'est la saison de chasse pour une espèce/région."""
        seasons = self.get_seasons(species, region)
        
        for season in seasons:
            if season.season_start <= check_date <= season.season_end:
                return True, season
            # Vérifier aussi arc et poudre noire
            if season.archery_start and season.archery_end:
                if season.archery_start <= check_date <= season.archery_end:
                    return True, season
            if season.muzzleloader_start and season.muzzleloader_end:
                if season.muzzleloader_start <= check_date <= season.muzzleloader_end:
                    return True, season
        
        return False, None
    
    def calculate_pressure_impact(
        self,
        species: str,
        pressure_intensity: PressureIntensity,
        hour: Optional[int] = None,
        is_weekend: bool = False
    ) -> Dict[str, Any]:
        """
        Calcule l'impact de la pression de chasse sur le comportement.
        
        Args:
            species: Code espèce
            pressure_intensity: Niveau de pression
            hour: Heure (0-23) pour ajustement
            is_weekend: True si fin de semaine (pression généralement plus forte)
            
        Returns:
            Dictionnaire avec modificateurs et recommandations
        """
        profile = self.get_profile(species)
        if not profile:
            return {
                "species": species,
                "profile_found": False,
                "pressure_intensity": pressure_intensity.value
            }
        
        modifiers = profile.modifiers_by_intensity.get(
            pressure_intensity, 
            {"activity": 1.0, "movement": 1.0}
        ).copy()
        
        # Ajustement fin de semaine (+20% pression)
        if is_weekend and pressure_intensity != PressureIntensity.NONE:
            modifiers["activity"] *= 0.85
            modifiers["movement"] *= 0.85
        
        # Ajustement par heure (pression maximale 6h-18h)
        if hour is not None:
            if 6 <= hour <= 18:
                # Heures de jour: pression maximale
                modifiers["activity"] *= 0.90
            else:
                # Heures de nuit: moins de pression
                modifiers["activity"] *= 1.10
                modifiers["movement"] *= 1.10
        
        # Vérifier si shift nocturne attendu
        nocturnal_shift = (
            pressure_intensity.value in ["moderate", "high", "extreme"] and
            profile.nocturnal_shift_threshold.value in ["low", "moderate"]
        )
        
        return {
            "species": species,
            "profile_found": True,
            "sensitivity": profile.sensitivity_level,
            "pressure_intensity": pressure_intensity.value,
            "modifiers": modifiers,
            "nocturnal_shift_expected": nocturnal_shift,
            "flight_distance_m": profile.flight_distance_m,
            "alert_duration_min": profile.alert_duration_minutes,
            "avoidance_strategies": profile.avoidance_strategies[:3],
            "refuge_preferences": profile.refuge_preferences[:3],
            "source_ids": profile.source_ids
        }
    
    def register_pressure_zone(self, zone: PressureZone):
        """Enregistre une nouvelle zone de pression détectée."""
        self._active_zones.append(zone)
        logger.info(f"[BIONIC] Registered pressure zone {zone.zone_id}: "
                   f"{zone.intensity.value} ({zone.intensity_score})")
    
    def get_active_pressure_zones(
        self, 
        lat: float, 
        lng: float, 
        radius_km: float
    ) -> List[PressureZone]:
        """Récupère les zones de pression actives dans un rayon."""
        import math
        
        result = []
        for zone in self._active_zones:
            # Calcul distance approximatif
            dlat = zone.center_lat - lat
            dlng = zone.center_lng - lng
            dist_km = math.sqrt(dlat**2 + dlng**2) * 111  # Approximation
            
            if dist_km <= radius_km + (zone.radius_m / 1000):
                result.append(zone)
        
        return result
    
    def get_all_species(self) -> List[str]:
        """Retourne la liste des espèces supportées."""
        return list(self._profiles.keys())
    
    def export_all_profiles(self) -> Dict[str, Dict]:
        """Exporte tous les profils pour documentation/API."""
        return {
            species: {
                "sensitivity": profile.sensitivity_level,
                "detection_distances": {
                    "human_m": profile.human_detection_distance_m,
                    "vehicle_m": profile.vehicle_detection_distance_m,
                    "gunshot_m": profile.gunshot_detection_distance_m
                },
                "response": {
                    "flight_distance_m": profile.flight_distance_m,
                    "alert_duration_min": profile.alert_duration_minutes,
                    "nocturnal_shift_threshold": profile.nocturnal_shift_threshold.value
                },
                "modifiers": {
                    k.value: v for k, v in profile.modifiers_by_intensity.items()
                },
                "source_ids": profile.source_ids,
                "confidence": profile.confidence
            }
            for species, profile in self._profiles.items()
        }


# =============================================================================
# SINGLETON ACCESS
# =============================================================================

_hunting_registry: Optional[HuntingPressureRegistry] = None


def get_hunting_pressure_registry() -> HuntingPressureRegistry:
    """Retourne l'instance singleton du registre de pression de chasse."""
    global _hunting_registry
    if _hunting_registry is None:
        _hunting_registry = HuntingPressureRegistry()
    return _hunting_registry
