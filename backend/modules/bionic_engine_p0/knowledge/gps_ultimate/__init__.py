"""
BIONIC V5 — GPS ULTIMATE MODULE (PHASE F)
==========================================
Module GPS ULTIMATE pour analyse en temps réel.

PHASE F — GPS ULTIMATE:
1. Auto-Cartography Engine (hotspots, corridors dynamiques)
2. Safety Engine (zones de danger, alertes)
3. Real-Time Integration (GPS chasseurs, recalcul instantané)
4. Observations Terrain (calibration vers MASTER)

Conformité: G-SEC | G-QA | G-DOC | BIONIC V5 PHASE F
"""

from .auto_cartography import (
    HotspotType,
    Hotspot,
    DynamicCorridor,
    AutoCartographyEngine,
    get_auto_cartography_engine
)

from .safety_engine import (
    DangerLevel,
    AlertPriority,
    DangerZone,
    SafetyAlert,
    SafetyEngine,
    get_safety_engine
)

from .realtime_integration import (
    GPSDevice,
    GPSPosition,
    RealtimeScore,
    RealtimeIntegrationService,
    get_realtime_service
)

from .observations import (
    ObservationType,
    TerrainObservation,
    ObservationResult,
    ObservationsRegistry,
    get_observations_registry
)

__all__ = [
    # Auto-Cartography
    'HotspotType',
    'Hotspot',
    'DynamicCorridor',
    'AutoCartographyEngine',
    'get_auto_cartography_engine',
    # Safety
    'DangerLevel',
    'AlertPriority',
    'DangerZone',
    'SafetyAlert',
    'SafetyEngine',
    'get_safety_engine',
    # Realtime
    'GPSDevice',
    'GPSPosition',
    'RealtimeScore',
    'RealtimeIntegrationService',
    'get_realtime_service',
    # Observations
    'ObservationType',
    'TerrainObservation',
    'ObservationResult',
    'ObservationsRegistry',
    'get_observations_registry'
]
