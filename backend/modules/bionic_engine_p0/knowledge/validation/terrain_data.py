"""
BIONIC V5 — TERRAIN DATA MODULE
================================
PHASE A — Données Terrain (priorité absolue)

Module pour intégrer les données terrain réelles:
1. Caméras multi-stations
2. Colliers GPS multi-espèces
3. Traces humaines (chasseurs)
4. Traces fauniques (corridors réels)
5. Flags terrain (indices, tirs, observations)

KNOWLEDGE LAYER INTEGRATION:
- Toutes les données passent par ce module
- Aucun accès direct aux sources
- Traçabilité obligatoire (source_ids)
- Versionnement des données

VERSION: 1.0.0
Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS
# =============================================================================

class TerrainDataType(str, Enum):
    """Types de données terrain supportés"""
    CAMERA = "camera"                    # Caméras multi-stations
    GPS_COLLAR = "gps_collar"            # Colliers GPS multi-espèces
    HUMAN_TRACE = "human_trace"          # Traces humaines (chasseurs)
    WILDLIFE_TRACE = "wildlife_trace"    # Traces fauniques (corridors)
    TERRAIN_FLAG = "terrain_flag"        # Flags terrain (indices, tirs, obs)


class CameraEventType(str, Enum):
    """Types d'événements caméra"""
    DETECTION = "detection"
    PASSAGE = "passage"
    FEEDING = "feeding"
    RESTING = "resting"
    INTERACTION = "interaction"
    PREDATION = "predation"


class HumanTraceType(str, Enum):
    """Types de traces humaines"""
    FOOTPRINT = "footprint"
    VEHICLE_TRACK = "vehicle_track"
    CAMP_SIGN = "camp_sign"
    HUNTING_STAND = "hunting_stand"
    BAIT_SITE = "bait_site"
    SHOT_FIRED = "shot_fired"


class WildlifeTraceType(str, Enum):
    """Types de traces fauniques"""
    TRACK = "track"                      # Piste/empreinte
    SCAT = "scat"                        # Déjections
    RUB_TREE = "rub_tree"                # Frottoir
    SCRAPE = "scrape"                    # Grattage
    BED = "bed"                          # Couche
    BROWSE = "browse"                    # Broutage
    WALLOW = "wallow"                    # Souille
    TRAIL = "trail"                      # Sentier régulier


class TerrainFlagType(str, Enum):
    """Types de flags terrain"""
    SIGHTING = "sighting"                # Observation visuelle
    HARVEST = "harvest"                  # Récolte (gibier)
    MORTALITY = "mortality"              # Mortalité naturelle
    ROAD_CROSSING = "road_crossing"      # Traversée de route
    HOTSPOT = "hotspot"                  # Point chaud identifié
    DANGER_ZONE = "danger_zone"          # Zone dangereuse
    REFUGE = "refuge"                    # Refuge thermique/sécurité


class DataQualityLevel(str, Enum):
    """Niveau de qualité des données"""
    HIGH = "high"                        # Données GPS ou caméra horodatées
    MEDIUM = "medium"                    # Observations expert
    LOW = "low"                          # Données non vérifiées
    ESTIMATED = "estimated"              # Données estimées/interpolées


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class CameraEvent:
    """
    Événement capturé par une caméra de surveillance.
    
    Source: Données terrain réelles (multi-stations)
    """
    
    event_id: str = field(default_factory=lambda: f"CAM-EVT-{uuid.uuid4().hex[:8].upper()}")
    station_id: str = ""
    
    # Localisation
    latitude: float = 0.0
    longitude: float = 0.0
    
    # Temporel
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Observation
    event_type: CameraEventType = CameraEventType.DETECTION
    species: str = ""
    individual_count: int = 1
    sex: Optional[str] = None  # "male", "female", "unknown"
    age_class: Optional[str] = None  # "juvenile", "adult", "senior"
    
    # Comportement
    behavior: str = ""
    direction_of_travel: Optional[str] = None  # "N", "NE", "E", etc.
    speed_estimate: Optional[str] = None  # "slow", "moderate", "fast"
    
    # Qualité
    confidence: float = 0.85
    image_quality: str = "good"
    data_quality: DataQualityLevel = DataQualityLevel.HIGH
    
    # Métadonnées
    raw_image_url: Optional[str] = None
    temperature_c: Optional[float] = None
    moon_phase: Optional[str] = None
    
    # Traçabilité Knowledge Layer
    source_id: str = "SRC-TERRAIN-CAM"
    validated: bool = False
    validated_by: Optional[str] = None


@dataclass
class GPSFix:
    """
    Point de localisation GPS d'un collier.
    
    Source: Colliers GPS multi-espèces
    """
    
    fix_id: str = field(default_factory=lambda: f"GPS-FIX-{uuid.uuid4().hex[:8].upper()}")
    collar_id: str = ""
    individual_id: str = ""
    
    # Localisation
    latitude: float = 0.0
    longitude: float = 0.0
    altitude_m: Optional[float] = None
    
    # Précision
    hdop: float = 2.0  # Horizontal Dilution of Precision
    accuracy_m: float = 10.0
    
    # Temporel
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Espèce
    species: str = ""
    
    # Comportement dérivé
    activity_state: str = "unknown"  # "moving", "resting", "feeding"
    speed_kmh: Optional[float] = None
    heading_degrees: Optional[float] = None
    
    # Qualité
    data_quality: DataQualityLevel = DataQualityLevel.HIGH
    fix_type: str = "3D"  # "2D" or "3D"
    satellites_used: int = 0
    
    # Environnement
    temperature_c: Optional[float] = None
    terrain_type: Optional[str] = None
    
    # Traçabilité
    source_id: str = "SRC-TERRAIN-GPS"


@dataclass
class HumanTrace:
    """
    Trace d'activité humaine (chasseurs, randonneurs, etc.)
    
    Source: Données terrain - traces humaines
    """
    
    trace_id: str = field(default_factory=lambda: f"HUM-{uuid.uuid4().hex[:8].upper()}")
    
    # Localisation
    latitude: float = 0.0
    longitude: float = 0.0
    
    # Temporel
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    estimated_age_hours: float = 0.0  # Âge estimé de la trace
    
    # Type
    trace_type: HumanTraceType = HumanTraceType.FOOTPRINT
    
    # Détails
    description: str = ""
    direction: Optional[str] = None
    frequency: str = "single"  # "single", "occasional", "regular", "heavy"
    
    # Impact faunique
    disturbance_radius_m: float = 200.0
    disturbance_intensity: float = 0.5  # 0.0-1.0
    
    # Qualité
    confidence: float = 0.7
    data_quality: DataQualityLevel = DataQualityLevel.MEDIUM
    
    # Observateur
    observer_id: Optional[str] = None
    observer_type: str = "hunter"  # "hunter", "biologist", "public"
    
    # Traçabilité
    source_id: str = "SRC-TERRAIN-HUMAN"


@dataclass
class WildlifeTrace:
    """
    Trace faunique (piste, corridor, indice de présence)
    
    Source: Données terrain - corridors réels
    """
    
    trace_id: str = field(default_factory=lambda: f"WLD-{uuid.uuid4().hex[:8].upper()}")
    
    # Localisation
    latitude: float = 0.0
    longitude: float = 0.0
    
    # Corridor (si applicable)
    corridor_id: Optional[str] = None
    is_corridor_segment: bool = False
    
    # Temporel
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    estimated_freshness_hours: float = 24.0
    
    # Espèce
    species: str = ""
    species_confidence: float = 0.8
    
    # Type de trace
    trace_type: WildlifeTraceType = WildlifeTraceType.TRACK
    
    # Détails
    description: str = ""
    count: int = 1
    direction: Optional[str] = None
    
    # Mesures
    track_width_cm: Optional[float] = None
    track_length_cm: Optional[float] = None
    stride_length_cm: Optional[float] = None
    
    # Usage du corridor
    usage_frequency: str = "unknown"  # "rare", "occasional", "regular", "heavy"
    usage_pattern: str = "unknown"  # "feeding", "travel", "mixed"
    
    # Qualité
    confidence: float = 0.75
    data_quality: DataQualityLevel = DataQualityLevel.MEDIUM
    
    # Observateur
    observer_id: Optional[str] = None
    
    # Traçabilité
    source_id: str = "SRC-TERRAIN-WILDLIFE"


@dataclass
class TerrainFlag:
    """
    Flag terrain (observation, récolte, indice significatif)
    
    Source: Données terrain - indices, tirs, observations
    """
    
    flag_id: str = field(default_factory=lambda: f"FLAG-{uuid.uuid4().hex[:8].upper()}")
    
    # Localisation
    latitude: float = 0.0
    longitude: float = 0.0
    
    # Temporel
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Type
    flag_type: TerrainFlagType = TerrainFlagType.SIGHTING
    
    # Espèce
    species: str = ""
    individual_count: int = 1
    sex: Optional[str] = None
    age_class: Optional[str] = None
    
    # Détails
    description: str = ""
    notes: str = ""
    
    # Pour HARVEST
    harvest_method: Optional[str] = None  # "rifle", "bow", "trap"
    harvest_success: Optional[bool] = None
    
    # Pour SIGHTING
    duration_minutes: Optional[float] = None
    behavior_observed: Optional[str] = None
    
    # Pour HOTSPOT
    hotspot_score: Optional[float] = None  # 0-100
    hotspot_reason: Optional[str] = None
    
    # Qualité
    confidence: float = 0.8
    data_quality: DataQualityLevel = DataQualityLevel.MEDIUM
    
    # Observateur
    observer_id: Optional[str] = None
    observer_type: str = "hunter"
    
    # Traçabilité
    source_id: str = "SRC-TERRAIN-FLAG"
    validated: bool = False


# =============================================================================
# TERRAIN DATA REGISTRY
# =============================================================================

@dataclass
class Corridor:
    """
    Corridor faunique réel identifié sur le terrain.
    
    Agrège les traces fauniques pour former des corridors
    de déplacement validés.
    """
    
    corridor_id: str = field(default_factory=lambda: f"COR-{uuid.uuid4().hex[:8].upper()}")
    name: str = ""
    
    # Géométrie (liste de points)
    waypoints: List[Tuple[float, float]] = field(default_factory=list)
    
    # Espèces
    primary_species: str = ""
    secondary_species: List[str] = field(default_factory=list)
    
    # Usage
    usage_frequency: str = "unknown"
    usage_pattern: str = "travel"
    peak_hours: List[int] = field(default_factory=list)
    
    # Saisonnalité
    active_seasons: List[str] = field(default_factory=list)
    
    # Statistiques
    total_observations: int = 0
    last_observation: Optional[datetime] = None
    
    # Qualité
    confidence: float = 0.7
    validation_status: str = "pending"  # "pending", "validated", "rejected"
    
    # Traçabilité
    source_ids: List[str] = field(default_factory=lambda: ["SRC-TERRAIN-CORRIDOR"])


class TerrainDataRegistry:
    """
    Registre centralisé des données terrain.
    
    Point d'entrée unique pour le Knowledge Layer.
    Aucun accès direct aux sources externes.
    """
    
    def __init__(self):
        self._camera_events: Dict[str, CameraEvent] = {}
        self._gps_fixes: Dict[str, GPSFix] = {}
        self._human_traces: Dict[str, HumanTrace] = {}
        self._wildlife_traces: Dict[str, WildlifeTrace] = {}
        self._terrain_flags: Dict[str, TerrainFlag] = {}
        self._corridors: Dict[str, Corridor] = {}
        
        self._version = "1.0.0"
        self._last_updated = datetime.now(timezone.utc)
        
        # Statistiques
        self._stats = {
            "camera_events": 0,
            "gps_fixes": 0,
            "human_traces": 0,
            "wildlife_traces": 0,
            "terrain_flags": 0,
            "corridors": 0
        }
        
        self._initialize_demo_data()
    
    def _initialize_demo_data(self):
        """Initialiser avec des données de démonstration"""
        
        # Événements caméra de démonstration
        demo_cameras = [
            CameraEvent(
                station_id="CAM-001",
                latitude=46.8500,
                longitude=-71.2500,
                timestamp=datetime(2025, 9, 20, 6, 15, tzinfo=timezone.utc),
                event_type=CameraEventType.PASSAGE,
                species="moose",
                individual_count=1,
                sex="male",
                age_class="adult",
                behavior="traveling",
                direction_of_travel="NE"
            ),
            CameraEvent(
                station_id="CAM-002",
                latitude=46.8200,
                longitude=-71.1800,
                timestamp=datetime(2025, 9, 21, 5, 45, tzinfo=timezone.utc),
                event_type=CameraEventType.FEEDING,
                species="moose",
                individual_count=2,
                behavior="feeding_browse"
            ),
            CameraEvent(
                station_id="CAM-003",
                latitude=46.7900,
                longitude=-71.2200,
                timestamp=datetime(2025, 9, 22, 18, 30, tzinfo=timezone.utc),
                event_type=CameraEventType.RESTING,
                species="deer",
                individual_count=3,
                behavior="resting"
            )
        ]
        
        for event in demo_cameras:
            self._camera_events[event.event_id] = event
        self._stats["camera_events"] = len(demo_cameras)
        
        # Fixes GPS de démonstration
        demo_gps = [
            GPSFix(
                collar_id="GPS-M01",
                individual_id="MOOSE-2023-01",
                latitude=46.8450,
                longitude=-71.2400,
                timestamp=datetime(2025, 9, 20, 6, 0, tzinfo=timezone.utc),
                species="moose",
                activity_state="moving",
                speed_kmh=2.5
            ),
            GPSFix(
                collar_id="GPS-M01",
                individual_id="MOOSE-2023-01",
                latitude=46.8520,
                longitude=-71.2380,
                timestamp=datetime(2025, 9, 20, 7, 0, tzinfo=timezone.utc),
                species="moose",
                activity_state="feeding"
            )
        ]
        
        for fix in demo_gps:
            self._gps_fixes[fix.fix_id] = fix
        self._stats["gps_fixes"] = len(demo_gps)
        
        # Traces humaines de démonstration
        demo_human = [
            HumanTrace(
                latitude=46.8300,
                longitude=-71.2100,
                trace_type=HumanTraceType.HUNTING_STAND,
                description="Stand permanent secteur ouest",
                frequency="regular",
                disturbance_radius_m=150.0
            ),
            HumanTrace(
                latitude=46.8100,
                longitude=-71.1900,
                trace_type=HumanTraceType.VEHICLE_TRACK,
                description="Chemin forestier actif",
                frequency="occasional",
                disturbance_radius_m=300.0
            )
        ]
        
        for trace in demo_human:
            self._human_traces[trace.trace_id] = trace
        self._stats["human_traces"] = len(demo_human)
        
        # Traces fauniques de démonstration
        demo_wildlife = [
            WildlifeTrace(
                latitude=46.8400,
                longitude=-71.2300,
                species="moose",
                trace_type=WildlifeTraceType.RUB_TREE,
                description="Frottoir actif - mâle dominant",
                estimated_freshness_hours=12.0,
                corridor_id="COR-001",
                usage_frequency="regular"
            ),
            WildlifeTrace(
                latitude=46.8380,
                longitude=-71.2280,
                species="moose",
                trace_type=WildlifeTraceType.TRAIL,
                description="Sentier principal corridor nord",
                corridor_id="COR-001",
                is_corridor_segment=True,
                usage_frequency="heavy"
            )
        ]
        
        for trace in demo_wildlife:
            self._wildlife_traces[trace.trace_id] = trace
        self._stats["wildlife_traces"] = len(demo_wildlife)
        
        # Flags terrain de démonstration
        demo_flags = [
            TerrainFlag(
                latitude=46.8550,
                longitude=-71.2450,
                flag_type=TerrainFlagType.HOTSPOT,
                species="moose",
                description="Point chaud rut 2024",
                hotspot_score=85.0,
                hotspot_reason="Concentration mâles observée"
            ),
            TerrainFlag(
                latitude=46.8250,
                longitude=-71.2050,
                flag_type=TerrainFlagType.HARVEST,
                species="moose",
                harvest_method="rifle",
                harvest_success=True,
                description="Récolte saison 2024"
            ),
            TerrainFlag(
                latitude=46.8600,
                longitude=-71.2500,
                flag_type=TerrainFlagType.SIGHTING,
                species="moose",
                individual_count=4,
                duration_minutes=15.0,
                behavior_observed="feeding_group"
            )
        ]
        
        for flag in demo_flags:
            self._terrain_flags[flag.flag_id] = flag
        self._stats["terrain_flags"] = len(demo_flags)
        
        # Corridors de démonstration
        demo_corridors = [
            Corridor(
                corridor_id="COR-001",
                name="Corridor Nord Principal",
                waypoints=[
                    (46.8400, -71.2300),
                    (46.8420, -71.2280),
                    (46.8450, -71.2250),
                    (46.8480, -71.2220)
                ],
                primary_species="moose",
                usage_frequency="heavy",
                usage_pattern="travel",
                peak_hours=[5, 6, 17, 18],
                active_seasons=["fall", "rut"],
                total_observations=47,
                confidence=0.88,
                validation_status="validated"
            )
        ]
        
        for corridor in demo_corridors:
            self._corridors[corridor.corridor_id] = corridor
        self._stats["corridors"] = len(demo_corridors)
        
        logger.info(f"TerrainDataRegistry initialized with demo data: {self._stats}")
    
    # =========================================================================
    # CAMERA EVENTS
    # =========================================================================
    
    def add_camera_event(self, event: CameraEvent) -> str:
        """Ajouter un événement caméra"""
        self._camera_events[event.event_id] = event
        self._stats["camera_events"] += 1
        self._last_updated = datetime.now(timezone.utc)
        return event.event_id
    
    def get_camera_events(
        self,
        species: Optional[str] = None,
        station_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[CameraEvent]:
        """Obtenir les événements caméra avec filtres"""
        events = list(self._camera_events.values())
        
        if species:
            events = [e for e in events if e.species.lower() == species.lower()]
        if station_id:
            events = [e for e in events if e.station_id == station_id]
        if start_time:
            events = [e for e in events if e.timestamp >= start_time]
        if end_time:
            events = [e for e in events if e.timestamp <= end_time]
        
        return sorted(events, key=lambda x: x.timestamp, reverse=True)
    
    # =========================================================================
    # GPS FIXES
    # =========================================================================
    
    def add_gps_fix(self, fix: GPSFix) -> str:
        """Ajouter un fix GPS"""
        self._gps_fixes[fix.fix_id] = fix
        self._stats["gps_fixes"] += 1
        self._last_updated = datetime.now(timezone.utc)
        return fix.fix_id
    
    def get_gps_fixes(
        self,
        species: Optional[str] = None,
        collar_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[GPSFix]:
        """Obtenir les fixes GPS avec filtres"""
        fixes = list(self._gps_fixes.values())
        
        if species:
            fixes = [f for f in fixes if f.species.lower() == species.lower()]
        if collar_id:
            fixes = [f for f in fixes if f.collar_id == collar_id]
        if start_time:
            fixes = [f for f in fixes if f.timestamp >= start_time]
        if end_time:
            fixes = [f for f in fixes if f.timestamp <= end_time]
        
        return sorted(fixes, key=lambda x: x.timestamp, reverse=True)
    
    # =========================================================================
    # HUMAN TRACES
    # =========================================================================
    
    def add_human_trace(self, trace: HumanTrace) -> str:
        """Ajouter une trace humaine"""
        self._human_traces[trace.trace_id] = trace
        self._stats["human_traces"] += 1
        self._last_updated = datetime.now(timezone.utc)
        return trace.trace_id
    
    def get_human_traces(
        self,
        trace_type: Optional[HumanTraceType] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        radius_km: Optional[float] = None,
        center_lat: Optional[float] = None,
        center_lng: Optional[float] = None
    ) -> List[HumanTrace]:
        """Obtenir les traces humaines avec filtres"""
        traces = list(self._human_traces.values())
        
        if trace_type:
            traces = [t for t in traces if t.trace_type == trace_type]
        if start_time:
            traces = [t for t in traces if t.timestamp >= start_time]
        if end_time:
            traces = [t for t in traces if t.timestamp <= end_time]
        
        # Filtrage par rayon (simplifié)
        if radius_km and center_lat and center_lng:
            # TODO: Implémenter calcul de distance géographique
            pass
        
        return traces
    
    def get_human_pressure_at_point(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 1.0
    ) -> Dict[str, Any]:
        """
        Calculer la pression humaine à un point donné.
        
        Retourne:
        - score: 0-100 (100 = pression maximale)
        - factors: liste des facteurs de pression
        - source_ids: traçabilité
        """
        # TODO: Implémenter calcul réel avec distance
        traces = self._human_traces.values()
        
        count = len(traces)
        hunting_stands = sum(1 for t in traces if t.trace_type == HumanTraceType.HUNTING_STAND)
        
        score = min(100, count * 15 + hunting_stands * 25)
        
        return {
            "score": score,
            "factors": {
                "traces_count": count,
                "hunting_stands": hunting_stands,
                "disturbance_level": "moderate" if score > 50 else "low"
            },
            "source_ids": ["SRC-TERRAIN-HUMAN"]
        }
    
    # =========================================================================
    # WILDLIFE TRACES
    # =========================================================================
    
    def add_wildlife_trace(self, trace: WildlifeTrace) -> str:
        """Ajouter une trace faunique"""
        self._wildlife_traces[trace.trace_id] = trace
        self._stats["wildlife_traces"] += 1
        self._last_updated = datetime.now(timezone.utc)
        return trace.trace_id
    
    def get_wildlife_traces(
        self,
        species: Optional[str] = None,
        trace_type: Optional[WildlifeTraceType] = None,
        corridor_id: Optional[str] = None,
        start_time: Optional[datetime] = None
    ) -> List[WildlifeTrace]:
        """Obtenir les traces fauniques avec filtres"""
        traces = list(self._wildlife_traces.values())
        
        if species:
            traces = [t for t in traces if t.species.lower() == species.lower()]
        if trace_type:
            traces = [t for t in traces if t.trace_type == trace_type]
        if corridor_id:
            traces = [t for t in traces if t.corridor_id == corridor_id]
        if start_time:
            traces = [t for t in traces if t.timestamp >= start_time]
        
        return traces
    
    # =========================================================================
    # TERRAIN FLAGS
    # =========================================================================
    
    def add_terrain_flag(self, flag: TerrainFlag) -> str:
        """Ajouter un flag terrain"""
        self._terrain_flags[flag.flag_id] = flag
        self._stats["terrain_flags"] += 1
        self._last_updated = datetime.now(timezone.utc)
        return flag.flag_id
    
    def get_terrain_flags(
        self,
        flag_type: Optional[TerrainFlagType] = None,
        species: Optional[str] = None,
        start_time: Optional[datetime] = None
    ) -> List[TerrainFlag]:
        """Obtenir les flags terrain avec filtres"""
        flags = list(self._terrain_flags.values())
        
        if flag_type:
            flags = [f for f in flags if f.flag_type == flag_type]
        if species:
            flags = [f for f in flags if f.species.lower() == species.lower()]
        if start_time:
            flags = [f for f in flags if f.timestamp >= start_time]
        
        return flags
    
    def get_hotspots(
        self,
        species: Optional[str] = None,
        min_score: float = 70.0
    ) -> List[TerrainFlag]:
        """Obtenir les hotspots avec score minimum"""
        hotspots = [
            f for f in self._terrain_flags.values()
            if f.flag_type == TerrainFlagType.HOTSPOT
            and (f.hotspot_score or 0) >= min_score
        ]
        
        if species:
            hotspots = [h for h in hotspots if h.species.lower() == species.lower()]
        
        return sorted(hotspots, key=lambda x: x.hotspot_score or 0, reverse=True)
    
    # =========================================================================
    # CORRIDORS
    # =========================================================================
    
    def add_corridor(self, corridor: Corridor) -> str:
        """Ajouter un corridor"""
        self._corridors[corridor.corridor_id] = corridor
        self._stats["corridors"] += 1
        self._last_updated = datetime.now(timezone.utc)
        return corridor.corridor_id
    
    def get_corridors(
        self,
        species: Optional[str] = None,
        validated_only: bool = False
    ) -> List[Corridor]:
        """Obtenir les corridors avec filtres"""
        corridors = list(self._corridors.values())
        
        if species:
            corridors = [c for c in corridors if c.primary_species.lower() == species.lower()]
        if validated_only:
            corridors = [c for c in corridors if c.validation_status == "validated"]
        
        return corridors
    
    def get_corridor_by_id(self, corridor_id: str) -> Optional[Corridor]:
        """Obtenir un corridor par ID"""
        return self._corridors.get(corridor_id)
    
    # =========================================================================
    # STATISTIQUES & MÉTADONNÉES
    # =========================================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques du registre"""
        return {
            "version": self._version,
            "last_updated": self._last_updated.isoformat(),
            "counts": self._stats.copy(),
            "data_sources": [
                "SRC-TERRAIN-CAM",
                "SRC-TERRAIN-GPS",
                "SRC-TERRAIN-HUMAN",
                "SRC-TERRAIN-WILDLIFE",
                "SRC-TERRAIN-FLAG",
                "SRC-TERRAIN-CORRIDOR"
            ]
        }
    
    def get_species_activity_summary(
        self,
        species: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Résumé d'activité d'une espèce basé sur données terrain.
        
        Agrège: caméras, GPS, traces, flags
        """
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        camera_events = self.get_camera_events(species=species, start_time=cutoff)
        gps_fixes = self.get_gps_fixes(species=species, start_time=cutoff)
        wildlife_traces = self.get_wildlife_traces(species=species, start_time=cutoff)
        terrain_flags = self.get_terrain_flags(species=species, start_time=cutoff)
        corridors = self.get_corridors(species=species, validated_only=True)
        
        return {
            "species": species,
            "period_days": days,
            "summary": {
                "camera_detections": len(camera_events),
                "gps_locations": len(gps_fixes),
                "trace_observations": len(wildlife_traces),
                "significant_flags": len(terrain_flags),
                "active_corridors": len(corridors)
            },
            "activity_level": self._calculate_activity_level(
                len(camera_events), len(gps_fixes), len(wildlife_traces)
            ),
            "source_ids": [
                "SRC-TERRAIN-CAM",
                "SRC-TERRAIN-GPS",
                "SRC-TERRAIN-WILDLIFE",
                "SRC-TERRAIN-FLAG"
            ]
        }
    
    def _calculate_activity_level(
        self,
        camera_count: int,
        gps_count: int,
        trace_count: int
    ) -> str:
        """Calculer le niveau d'activité basé sur les observations"""
        total = camera_count + (gps_count / 10) + trace_count
        
        if total > 50:
            return "high"
        elif total > 20:
            return "moderate"
        elif total > 5:
            return "low"
        else:
            return "minimal"


# =============================================================================
# SINGLETON
# =============================================================================

_registry_instance: Optional[TerrainDataRegistry] = None


def get_terrain_data_registry() -> TerrainDataRegistry:
    """Obtenir l'instance singleton du registre de données terrain"""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = TerrainDataRegistry()
    return _registry_instance


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    'TerrainDataType',
    'CameraEventType',
    'HumanTraceType',
    'WildlifeTraceType',
    'TerrainFlagType',
    'DataQualityLevel',
    # Data models
    'CameraEvent',
    'GPSFix',
    'HumanTrace',
    'WildlifeTrace',
    'TerrainFlag',
    'Corridor',
    # Registry
    'TerrainDataRegistry',
    'get_terrain_data_registry'
]
