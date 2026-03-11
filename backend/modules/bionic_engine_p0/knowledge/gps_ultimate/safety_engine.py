"""
BIONIC V5 — SAFETY ENGINE (PHASE F)
====================================
PHASE F — GPS ULTIMATE

Engine de sécurité avec zones de danger et alertes temps réel.

FONCTIONNALITÉS:
1. Zones de danger automatiques
2. Zones d'évitement
3. Alertes en temps réel
4. Intégration NIVEAU 3 (PRES-HUMAN)

VERSION: 7.0.0
Conformité: G-SEC | G-QA | G-DOC | BIONIC V5 PHASE F
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

class DangerLevel(str, Enum):
    """Niveau de danger PHASE F"""
    NONE = "none"             # Pas de danger
    LOW = "low"               # Danger faible
    MODERATE = "moderate"     # Danger modéré
    HIGH = "high"             # Danger élevé
    CRITICAL = "critical"     # Danger critique


class AlertPriority(str, Enum):
    """Priorité des alertes"""
    INFO = "info"             # Information
    WARNING = "warning"       # Avertissement
    URGENT = "urgent"         # Urgent
    CRITICAL = "critical"     # Critique


class ZoneType(str, Enum):
    """Type de zone de sécurité"""
    HUNTING_ACTIVE = "hunting_active"       # Chasse active détectée
    HUMAN_PRESENCE = "human_presence"       # Présence humaine
    ROAD_PROXIMITY = "road_proximity"       # Proximité route
    RESTRICTED_AREA = "restricted_area"     # Zone restreinte
    ESCAPE_CORRIDOR = "escape_corridor"     # Corridor d'évacuation


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class DangerZone:
    """
    Zone de danger détectée.
    """
    
    zone_id: str
    zone_type: ZoneType
    danger_level: DangerLevel
    
    # Position
    lat: float
    lng: float
    radius_m: float = 200.0
    
    # Scores
    threat_score: float = 0.5       # 0-1
    confidence: float = 0.5         # 0-1
    
    # Source de la menace
    threat_source: str = "unknown"
    threat_description: str = ""
    
    # Temporalité
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    is_active: bool = True
    
    # Intégration NIVEAU 3
    pres_human_score: float = 0.0
    
    # Traçabilité
    source_ids: List[str] = field(default_factory=lambda: ["SRC-DANGER-ZONE"])
    version: str = "7.0.0"
    
    def is_expired(self) -> bool:
        """Vérifie si la zone a expiré."""
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at
    
    def to_geojson_feature(self) -> Dict[str, Any]:
        """Convertir en GeoJSON Feature."""
        # Créer un cercle
        num_points = 24
        coordinates = []
        for i in range(num_points + 1):
            angle = 2 * math.pi * i / num_points
            lat_offset = (self.radius_m / 111000) * math.cos(angle)
            lng_offset = (self.radius_m / (111000 * math.cos(math.radians(self.lat)))) * math.sin(angle)
            coordinates.append([self.lng + lng_offset, self.lat + lat_offset])
        
        # Couleur selon niveau de danger
        colors = {
            DangerLevel.NONE: "#00FF00",
            DangerLevel.LOW: "#FFFF00",
            DangerLevel.MODERATE: "#FFA500",
            DangerLevel.HIGH: "#FF4500",
            DangerLevel.CRITICAL: "#FF0000"
        }
        
        return {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [coordinates]
            },
            "properties": {
                "zone_id": self.zone_id,
                "zone_type": self.zone_type.value,
                "danger_level": self.danger_level.value,
                "center": {"lat": self.lat, "lng": self.lng},
                "radius_m": self.radius_m,
                "threat": {
                    "score": round(self.threat_score, 2),
                    "confidence": round(self.confidence, 2),
                    "source": self.threat_source,
                    "description": self.threat_description
                },
                "timing": {
                    "detected_at": self.detected_at.isoformat(),
                    "expires_at": self.expires_at.isoformat() if self.expires_at else None,
                    "is_active": self.is_active
                },
                "pres_human_score": round(self.pres_human_score, 2),
                "rendering": {
                    "fill_color": colors.get(self.danger_level, "#FF0000"),
                    "fill_opacity": 0.2 + 0.3 * self.threat_score,
                    "stroke_color": colors.get(self.danger_level, "#FF0000"),
                    "stroke_width": 3,
                    "dash_array": "5,5" if not self.is_active else None
                },
                "source_ids": self.source_ids,
                "version": self.version
            }
        }


@dataclass
class SafetyAlert:
    """
    Alerte de sécurité temps réel.
    """
    
    alert_id: str
    priority: AlertPriority
    
    # Contenu
    title: str
    message: str
    
    # Position associée
    lat: Optional[float] = None
    lng: Optional[float] = None
    
    # Zone de danger associée
    danger_zone_id: Optional[str] = None
    
    # Recommandation
    recommended_action: str = ""
    escape_direction: Optional[str] = None
    
    # Temporalité
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    
    # Traçabilité
    source_ids: List[str] = field(default_factory=lambda: ["SRC-ALERT"])
    version: str = "7.0.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire."""
        return {
            "alert_id": self.alert_id,
            "priority": self.priority.value,
            "content": {
                "title": self.title,
                "message": self.message
            },
            "location": {
                "lat": self.lat,
                "lng": self.lng
            } if self.lat else None,
            "danger_zone_id": self.danger_zone_id,
            "recommendation": {
                "action": self.recommended_action,
                "escape_direction": self.escape_direction
            },
            "timing": {
                "created_at": self.created_at.isoformat(),
                "acknowledged": self.acknowledged,
                "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None
            },
            "source_ids": self.source_ids,
            "version": self.version
        }


# =============================================================================
# SAFETY ENGINE
# =============================================================================

class SafetyEngine:
    """
    Engine de sécurité PHASE F.
    
    Détecte les zones de danger et génère des alertes en temps réel.
    """
    
    def __init__(self):
        self._version = "7.0.0"
        self._zone_counter = 0
        self._alert_counter = 0
        
        # Cache des éléments
        self._danger_zones: Dict[str, DangerZone] = {}
        self._alerts: Dict[str, SafetyAlert] = {}
        
        logger.info(f"SafetyEngine initialized: v{self._version}")
    
    def _generate_zone_id(self) -> str:
        """Génère un ID unique pour une zone."""
        self._zone_counter += 1
        timestamp = datetime.now(timezone.utc).strftime("%H%M%S")
        return f"DNG-{timestamp}-{self._zone_counter:04d}"
    
    def _generate_alert_id(self) -> str:
        """Génère un ID unique pour une alerte."""
        self._alert_counter += 1
        timestamp = datetime.now(timezone.utc).strftime("%H%M%S")
        return f"ALT-{timestamp}-{self._alert_counter:04d}"
    
    def analyze_safety(
        self,
        center_lat: float,
        center_lng: float,
        search_radius_km: float = 3.0,
        # Facteurs NIVEAU 3
        hunting_pressure_active: bool = False,
        hunting_pressure_modifier: float = 1.0,
        human_activity_detected: bool = False
    ) -> Tuple[List[DangerZone], List[SafetyAlert]]:
        """
        PHASE F — Analyse de sécurité de la zone.
        
        Returns:
            Tuple (danger_zones, alerts)
        """
        danger_zones = []
        alerts = []
        
        # =================================================================
        # 1. ZONE DE CHASSE ACTIVE (si détectée)
        # =================================================================
        
        if hunting_pressure_active:
            # Niveau de danger basé sur le modificateur
            if hunting_pressure_modifier < 0.5:
                danger_level = DangerLevel.CRITICAL
                threat_score = 0.9
            elif hunting_pressure_modifier < 0.7:
                danger_level = DangerLevel.HIGH
                threat_score = 0.7
            else:
                danger_level = DangerLevel.MODERATE
                threat_score = 0.5
            
            hunting_zone = DangerZone(
                zone_id=self._generate_zone_id(),
                zone_type=ZoneType.HUNTING_ACTIVE,
                danger_level=danger_level,
                lat=center_lat + (search_radius_km * 0.2 / 111),
                lng=center_lng + (search_radius_km * 0.15 / 111),
                radius_m=300,
                threat_score=threat_score,
                confidence=0.85,
                threat_source="hunting_pressure",
                threat_description="Activité de chasse détectée dans cette zone",
                pres_human_score=1 - hunting_pressure_modifier,
                expires_at=datetime.now(timezone.utc) + timedelta(hours=2),
                source_ids=["SRC-DANGER-ZONE", "SRC-PRES-HUMAN", "SRC-HUNTING"]
            )
            danger_zones.append(hunting_zone)
            self._danger_zones[hunting_zone.zone_id] = hunting_zone
            
            # Créer une alerte
            alert = SafetyAlert(
                alert_id=self._generate_alert_id(),
                priority=AlertPriority.URGENT if danger_level in [DangerLevel.HIGH, DangerLevel.CRITICAL] else AlertPriority.WARNING,
                title="Zone de chasse active détectée",
                message=f"Pression de chasse détectée (niveau: {danger_level.value}). Éviter la zone.",
                lat=hunting_zone.lat,
                lng=hunting_zone.lng,
                danger_zone_id=hunting_zone.zone_id,
                recommended_action="Éviter cette zone ou se diriger vers un refuge",
                escape_direction="sud-ouest",
                source_ids=["SRC-ALERT", "SRC-HUNTING"]
            )
            alerts.append(alert)
            self._alerts[alert.alert_id] = alert
        
        # =================================================================
        # 2. PRÉSENCE HUMAINE GÉNÉRALE
        # =================================================================
        
        if human_activity_detected:
            human_zone = DangerZone(
                zone_id=self._generate_zone_id(),
                zone_type=ZoneType.HUMAN_PRESENCE,
                danger_level=DangerLevel.LOW,
                lat=center_lat - (search_radius_km * 0.1 / 111),
                lng=center_lng + (search_radius_km * 0.2 / 111),
                radius_m=150,
                threat_score=0.3,
                confidence=0.60,
                threat_source="human_activity",
                threat_description="Présence humaine générale détectée",
                pres_human_score=0.3,
                expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
                source_ids=["SRC-DANGER-ZONE", "SRC-HUMAN-ACTIVITY"]
            )
            danger_zones.append(human_zone)
            self._danger_zones[human_zone.zone_id] = human_zone
        
        # =================================================================
        # 3. CORRIDORS D'ÉVACUATION
        # =================================================================
        
        if danger_zones:
            # Créer un corridor d'évacuation
            escape_zone = DangerZone(
                zone_id=self._generate_zone_id(),
                zone_type=ZoneType.ESCAPE_CORRIDOR,
                danger_level=DangerLevel.NONE,
                lat=center_lat - (search_radius_km * 0.4 / 111),
                lng=center_lng - (search_radius_km * 0.3 / 111),
                radius_m=100,
                threat_score=0.0,
                confidence=0.75,
                threat_source="safe_zone",
                threat_description="Corridor d'évacuation recommandé",
                pres_human_score=0.0,
                source_ids=["SRC-ESCAPE-CORRIDOR"]
            )
            danger_zones.append(escape_zone)
            self._danger_zones[escape_zone.zone_id] = escape_zone
        
        logger.info(f"SafetyEngine analyzed: {len(danger_zones)} zones, {len(alerts)} alerts")
        return danger_zones, alerts
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Marque une alerte comme acquittée."""
        if alert_id in self._alerts:
            self._alerts[alert_id].acknowledged = True
            self._alerts[alert_id].acknowledged_at = datetime.now(timezone.utc)
            return True
        return False
    
    def get_active_zones(self) -> List[DangerZone]:
        """Retourne les zones de danger actives."""
        return [z for z in self._danger_zones.values() if z.is_active and not z.is_expired()]
    
    def get_pending_alerts(self) -> List[SafetyAlert]:
        """Retourne les alertes non acquittées."""
        return [a for a in self._alerts.values() if not a.acknowledged]
    
    def to_geojson_feature_collection(self) -> Dict[str, Any]:
        """Export toutes les zones en GeoJSON."""
        features = [z.to_geojson_feature() for z in self.get_active_zones()]
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "properties": {
                "total_zones": len(features),
                "alerts_pending": len(self.get_pending_alerts()),
                "version": self._version,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Statistiques de l'engine."""
        return {
            "version": self._version,
            "total_zones": len(self._danger_zones),
            "active_zones": len(self.get_active_zones()),
            "total_alerts": len(self._alerts),
            "pending_alerts": len(self.get_pending_alerts())
        }
    
    def report_danger(
        self,
        lat: float,
        lng: float,
        danger_type: str = "human_presence",
        description: str = "",
        radius_m: float = 200.0
    ) -> DangerZone:
        """
        PHASE F — Signale un danger observé sur le terrain.
        
        Crée une zone de danger temporaire basée sur le signalement.
        """
        # Mapper le type de danger
        zone_type_map = {
            "hunting_active": ZoneType.HUNTING_ACTIVE,
            "human_presence": ZoneType.HUMAN_PRESENCE,
            "road_proximity": ZoneType.ROAD_PROXIMITY,
            "restricted_area": ZoneType.RESTRICTED_AREA
        }
        zone_type = zone_type_map.get(danger_type.lower(), ZoneType.HUMAN_PRESENCE)
        
        # Déterminer le niveau de danger
        danger_level = DangerLevel.MODERATE
        threat_score = 0.6
        
        if danger_type == "hunting_active":
            danger_level = DangerLevel.HIGH
            threat_score = 0.8
        elif danger_type == "restricted_area":
            danger_level = DangerLevel.CRITICAL
            threat_score = 0.9
        
        # Créer la zone de danger
        zone = DangerZone(
            zone_id=self._generate_zone_id(),
            zone_type=zone_type,
            danger_level=danger_level,
            lat=lat,
            lng=lng,
            radius_m=radius_m,
            threat_score=threat_score,
            confidence=0.7,  # Confiance moyenne pour signalement utilisateur
            threat_source="user_report",
            threat_description=description or f"Signalement utilisateur: {danger_type}",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=4),  # Expire après 4h
            source_ids=["SRC-USER-REPORT", "SRC-DANGER-ZONE"]
        )
        
        self._danger_zones[zone.zone_id] = zone
        
        # Créer une alerte
        alert = SafetyAlert(
            alert_id=self._generate_alert_id(),
            priority=AlertPriority.WARNING if danger_level == DangerLevel.MODERATE else AlertPriority.URGENT,
            title=f"Signalement: {danger_type}",
            message=description or f"Danger signalé par un utilisateur à proximité",
            lat=lat,
            lng=lng,
            danger_zone_id=zone.zone_id,
            recommended_action="Évaluer la situation et éviter si possible",
            source_ids=["SRC-USER-REPORT-ALERT"]
        )
        self._alerts[alert.alert_id] = alert
        
        logger.info(f"Danger reported: {zone.zone_id} ({danger_type} at {lat:.4f}, {lng:.4f})")
        
        return zone
    
    def list_danger_zones(self, active_only: bool = True) -> List[DangerZone]:
        """
        PHASE F — Liste les zones de danger.
        
        Args:
            active_only: Si True, retourne uniquement les zones actives
        
        Returns:
            Liste des zones de danger
        """
        if active_only:
            return self.get_active_zones()
        return list(self._danger_zones.values())


# =============================================================================
# SINGLETON
# =============================================================================

_engine_instance: Optional[SafetyEngine] = None


def get_safety_engine() -> SafetyEngine:
    """Obtenir l'instance singleton de l'engine."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = SafetyEngine()
    return _engine_instance


__all__ = [
    'DangerLevel',
    'AlertPriority',
    'ZoneType',
    'DangerZone',
    'SafetyAlert',
    'SafetyEngine',
    'get_safety_engine'
]
