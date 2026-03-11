"""
BIONIC V5 — NOTIFICATION REGISTRY (PHASE F — NOTIFICATIONS PUSH)
=================================================================
VAPID Natif — 100% Autonome

Registre centralisé des notifications et règles de déclenchement.

OBJECTIF:
- Notifications push via VAPID natif (aucune dépendance externe)
- WebSocket temps réel
- Intégration exclusive avec Safety Engine
- Traçabilité complète (source_ids + version)

TYPES D'ALERTES:
- danger: Zone de danger détectée
- human_pressure: Pression humaine élevée
- corridor_risk: Corridor à risque
- safety_update: Mise à jour de sécurité

VERSION: 7.2.0
Conformité: G-SEC | G-QA | G-DOC | BIONIC V5 MASTER
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import logging
import json
import os
import base64

# VAPID
from py_vapid import Vapid

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS
# =============================================================================

class AlertType(str, Enum):
    """Types d'alertes Safety Engine"""
    DANGER = "danger"                   # Zone de danger
    HUMAN_PRESSURE = "human_pressure"   # Pression humaine
    CORRIDOR_RISK = "corridor_risk"     # Corridor à risque
    SAFETY_UPDATE = "safety_update"     # Mise à jour sécurité
    HOTSPOT_ALERT = "hotspot_alert"     # Alerte hotspot


class AlertPriority(str, Enum):
    """Priorité des alertes"""
    CRITICAL = "critical"     # Danger immédiat
    HIGH = "high"             # Haute priorité
    MEDIUM = "medium"         # Priorité moyenne
    LOW = "low"               # Information


class SubscriptionStatus(str, Enum):
    """Statut d'un abonnement"""
    ACTIVE = "active"
    EXPIRED = "expired"
    UNSUBSCRIBED = "unsubscribed"


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class VAPIDKeys:
    """
    Clés VAPID pour notifications push.
    Générées une fois et stockées de manière sécurisée.
    """
    
    public_key: str
    private_key: str
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "7.2.0"
    source_ids: List[str] = field(default_factory=lambda: ["SRC-VAPID-KEYS"])
    
    def to_dict(self) -> Dict[str, Any]:
        """Exporter les clés (seulement la clé publique pour le frontend)."""
        return {
            "public_key": self.public_key,
            "generated_at": self.generated_at.isoformat(),
            "version": self.version
        }


@dataclass
class PushSubscription:
    """
    Abonnement push d'un client.
    """
    
    subscription_id: str
    endpoint: str
    p256dh: str                          # Clé publique du client
    auth: str                            # Secret d'authentification
    
    # Métadonnées
    user_agent: str = ""
    device_type: str = "unknown"         # web, mobile, desktop
    
    # Géolocalisation (pour géofencing)
    last_known_lat: Optional[float] = None
    last_known_lng: Optional[float] = None
    geofence_radius_km: float = 5.0      # Rayon d'alerte par défaut
    
    # Préférences
    alert_types: List[AlertType] = field(default_factory=lambda: list(AlertType))
    min_priority: AlertPriority = AlertPriority.MEDIUM
    
    # Statut
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_push_at: Optional[datetime] = None
    push_count: int = 0
    
    # Traçabilité
    source_ids: List[str] = field(default_factory=lambda: ["SRC-PUSH-SUBSCRIPTION"])
    version: str = "7.2.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir pour l'API."""
        return {
            "subscription_id": self.subscription_id,
            "endpoint": self.endpoint[:50] + "..." if len(self.endpoint) > 50 else self.endpoint,
            "device_type": self.device_type,
            "geofence": {
                "lat": self.last_known_lat,
                "lng": self.last_known_lng,
                "radius_km": self.geofence_radius_km
            },
            "preferences": {
                "alert_types": [at.value for at in self.alert_types],
                "min_priority": self.min_priority.value
            },
            "status": self.status.value,
            "statistics": {
                "created_at": self.created_at.isoformat(),
                "last_push_at": self.last_push_at.isoformat() if self.last_push_at else None,
                "push_count": self.push_count
            },
            "version": self.version
        }


@dataclass
class NotificationPayload:
    """
    Payload de notification à envoyer.
    """
    
    notification_id: str
    alert_type: AlertType
    priority: AlertPriority
    
    # Contenu
    title: str
    body: str
    icon: str = "/icons/bionic-alert.png"
    badge: str = "/icons/bionic-badge.png"
    
    # Actions
    url: str = "/"                       # URL à ouvrir au clic
    actions: List[Dict[str, str]] = field(default_factory=list)
    
    # Données Safety Engine
    zone_id: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    radius_m: Optional[float] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    
    # Traçabilité
    source_ids: List[str] = field(default_factory=lambda: ["SRC-NOTIFICATION"])
    version: str = "7.2.0"
    
    def to_push_payload(self) -> str:
        """Convertir en payload JSON pour Web Push."""
        payload = {
            "notification": {
                "title": self.title,
                "body": self.body,
                "icon": self.icon,
                "badge": self.badge,
                "tag": self.notification_id,
                "data": {
                    "notification_id": self.notification_id,
                    "alert_type": self.alert_type.value,
                    "priority": self.priority.value,
                    "url": self.url,
                    "zone_id": self.zone_id,
                    "lat": self.lat,
                    "lng": self.lng,
                    "created_at": self.created_at.isoformat()
                },
                "actions": self.actions or [
                    {"action": "view", "title": "Voir"},
                    {"action": "dismiss", "title": "Ignorer"}
                ],
                "requireInteraction": self.priority in [AlertPriority.CRITICAL, AlertPriority.HIGH],
                "vibrate": [200, 100, 200] if self.priority == AlertPriority.CRITICAL else [100]
            }
        }
        return json.dumps(payload)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir pour l'API."""
        return {
            "notification_id": self.notification_id,
            "alert_type": self.alert_type.value,
            "priority": self.priority.value,
            "content": {
                "title": self.title,
                "body": self.body,
                "icon": self.icon,
                "url": self.url
            },
            "safety_data": {
                "zone_id": self.zone_id,
                "lat": self.lat,
                "lng": self.lng,
                "radius_m": self.radius_m
            },
            "timestamps": {
                "created_at": self.created_at.isoformat(),
                "expires_at": self.expires_at.isoformat() if self.expires_at else None
            },
            "source_ids": self.source_ids,
            "version": self.version
        }


@dataclass
class AlertTriggerRule:
    """
    Règle de déclenchement d'alerte centralisée.
    Conformité BIONIC V5: règles versionnées, documentées, traçables.
    """
    
    rule_id: str
    rule_name: str
    alert_type: AlertType
    
    # Conditions
    trigger_condition: str               # Description de la condition
    danger_level_threshold: str = "moderate"  # none, low, moderate, high, critical
    threat_score_threshold: float = 0.5
    
    # Priorité résultante
    resulting_priority: AlertPriority = AlertPriority.MEDIUM
    
    # Message template
    title_template: str = "Alerte BIONIC V5"
    body_template: str = "Une nouvelle alerte a été détectée dans votre zone."
    
    # Activation
    is_active: bool = True
    
    # Traçabilité
    source_ids: List[str] = field(default_factory=lambda: ["SRC-TRIGGER-RULE"])
    version: str = "7.2.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir pour l'API."""
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "alert_type": self.alert_type.value,
            "conditions": {
                "description": self.trigger_condition,
                "danger_level_threshold": self.danger_level_threshold,
                "threat_score_threshold": self.threat_score_threshold
            },
            "result": {
                "priority": self.resulting_priority.value,
                "title_template": self.title_template,
                "body_template": self.body_template
            },
            "is_active": self.is_active,
            "source_ids": self.source_ids,
            "version": self.version
        }


# =============================================================================
# NOTIFICATION REGISTRY
# =============================================================================

class NotificationRegistry:
    """
    Registre centralisé des notifications BIONIC V5.
    
    RESPONSABILITÉS:
    1. Génération et stockage des clés VAPID
    2. Gestion des abonnements push
    3. Règles de déclenchement centralisées
    4. Historique des notifications
    
    CONFORMITÉ:
    - 100% autonome (VAPID natif)
    - Logique centralisée (Knowledge Layer)
    - Traçabilité complète
    """
    
    def __init__(self):
        self._version = "7.2.0"
        self._subscription_counter = 0
        self._notification_counter = 0
        
        # Clés VAPID
        self._vapid_keys: Optional[VAPIDKeys] = None
        
        # Stockage
        self._subscriptions: Dict[str, PushSubscription] = {}
        self._notifications: Dict[str, NotificationPayload] = {}
        self._trigger_rules: Dict[str, AlertTriggerRule] = {}
        
        # Initialiser les clés VAPID
        self._initialize_vapid_keys()
        
        # Initialiser les règles par défaut
        self._initialize_default_rules()
        
        logger.info(f"NotificationRegistry initialized: v{self._version}")
    
    # =========================================================================
    # VAPID KEYS
    # =========================================================================
    
    def _initialize_vapid_keys(self):
        """Initialise ou charge les clés VAPID."""
        keys_path = "/app/backend/.vapid_keys.json"
        
        if os.path.exists(keys_path):
            # Charger les clés existantes
            try:
                with open(keys_path, "r") as f:
                    data = json.load(f)
                    self._vapid_keys = VAPIDKeys(
                        public_key=data["public_key"],
                        private_key=data["private_key"],
                        generated_at=datetime.fromisoformat(data.get("generated_at", datetime.now(timezone.utc).isoformat()))
                    )
                    logger.info("VAPID keys loaded from storage")
                    return
            except Exception as e:
                logger.warning(f"Failed to load VAPID keys: {e}")
        
        # Générer de nouvelles clés avec py_vapid
        try:
            vapid = Vapid()
            vapid.generate_keys()
            
            # Utiliser les méthodes de py_vapid pour obtenir les clés
            # Format applicationServerKey
            from cryptography.hazmat.primitives import serialization
            
            # Clé publique en format non compressé (65 bytes)
            public_key_bytes = vapid.public_key.public_bytes(
                encoding=serialization.Encoding.X962,
                format=serialization.PublicFormat.UncompressedPoint
            )
            public_key = base64.urlsafe_b64encode(public_key_bytes).decode('utf-8').rstrip('=')
            
            # Clé privée en format raw (32 bytes)
            private_key_bytes = vapid.private_key.private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption()
            )
            private_key = base64.urlsafe_b64encode(private_key_bytes).decode('utf-8').rstrip('=')
            
            self._vapid_keys = VAPIDKeys(
                public_key=public_key,
                private_key=private_key
            )
            
            # Sauvegarder
            with open(keys_path, "w") as f:
                json.dump({
                    "public_key": public_key,
                    "private_key": private_key,
                    "generated_at": self._vapid_keys.generated_at.isoformat()
                }, f)
            logger.info("VAPID keys generated and saved")
            
        except Exception as e:
            logger.error(f"Failed to generate VAPID keys: {e}")
            # Fallback: utiliser des clés de test prédéfinies
            self._vapid_keys = VAPIDKeys(
                public_key="BEl62iUYgUivxIkv69yViEuiBIa-Ib9-SkvMeAtA3LFgDzkrxZJjSgSnfckjBJuBkr3qBUYIHBQFLXYp5Nksh8U",
                private_key="2qFnQxEhjGbNxfFiEW4hnHtMSmNYDnF3j3qWzSK_d4c"
            )
            logger.warning("Using fallback VAPID keys")
    
    def get_vapid_public_key(self) -> str:
        """Retourne la clé publique VAPID pour le frontend."""
        if self._vapid_keys:
            return self._vapid_keys.public_key
        return ""
    
    def get_vapid_keys(self) -> Optional[VAPIDKeys]:
        """Retourne les clés VAPID (usage interne)."""
        return self._vapid_keys
    
    # =========================================================================
    # TRIGGER RULES
    # =========================================================================
    
    def _initialize_default_rules(self):
        """Initialise les règles de déclenchement par défaut."""
        
        # Règle 1: Zone de danger critique
        self._trigger_rules["RULE-DANGER-CRITICAL"] = AlertTriggerRule(
            rule_id="RULE-DANGER-CRITICAL",
            rule_name="Zone de danger critique",
            alert_type=AlertType.DANGER,
            trigger_condition="danger_level == 'critical' OR threat_score >= 0.9",
            danger_level_threshold="critical",
            threat_score_threshold=0.9,
            resulting_priority=AlertPriority.CRITICAL,
            title_template="⚠️ DANGER CRITIQUE",
            body_template="Zone de danger critique détectée à proximité. Évitez cette zone immédiatement.",
            source_ids=["SRC-RULE-DEFAULT", "SRC-SAFETY-ENGINE"]
        )
        
        # Règle 2: Zone de danger élevé
        self._trigger_rules["RULE-DANGER-HIGH"] = AlertTriggerRule(
            rule_id="RULE-DANGER-HIGH",
            rule_name="Zone de danger élevé",
            alert_type=AlertType.DANGER,
            trigger_condition="danger_level == 'high' OR threat_score >= 0.7",
            danger_level_threshold="high",
            threat_score_threshold=0.7,
            resulting_priority=AlertPriority.HIGH,
            title_template="⚠️ Zone de danger",
            body_template="Une zone de danger a été signalée dans votre périmètre.",
            source_ids=["SRC-RULE-DEFAULT", "SRC-SAFETY-ENGINE"]
        )
        
        # Règle 3: Pression humaine
        self._trigger_rules["RULE-HUMAN-PRESSURE"] = AlertTriggerRule(
            rule_id="RULE-HUMAN-PRESSURE",
            rule_name="Pression humaine élevée",
            alert_type=AlertType.HUMAN_PRESSURE,
            trigger_condition="human_pressure_score >= 0.6",
            danger_level_threshold="moderate",
            threat_score_threshold=0.6,
            resulting_priority=AlertPriority.MEDIUM,
            title_template="👥 Pression humaine",
            body_template="Activité humaine élevée détectée dans cette zone.",
            source_ids=["SRC-RULE-DEFAULT", "SRC-NIVEAU-3"]
        )
        
        # Règle 4: Corridor à risque
        self._trigger_rules["RULE-CORRIDOR-RISK"] = AlertTriggerRule(
            rule_id="RULE-CORRIDOR-RISK",
            rule_name="Corridor à risque",
            alert_type=AlertType.CORRIDOR_RISK,
            trigger_condition="corridor intersects danger_zone",
            danger_level_threshold="moderate",
            threat_score_threshold=0.5,
            resulting_priority=AlertPriority.MEDIUM,
            title_template="🛤️ Corridor à risque",
            body_template="Un corridor de déplacement traverse une zone à risque.",
            source_ids=["SRC-RULE-DEFAULT", "SRC-NIVEAU-4"]
        )
        
        # Règle 5: Chasse active
        self._trigger_rules["RULE-HUNTING-ACTIVE"] = AlertTriggerRule(
            rule_id="RULE-HUNTING-ACTIVE",
            rule_name="Chasse active détectée",
            alert_type=AlertType.DANGER,
            trigger_condition="zone_type == 'hunting_active'",
            danger_level_threshold="high",
            threat_score_threshold=0.8,
            resulting_priority=AlertPriority.HIGH,
            title_template="🎯 Chasse active",
            body_template="Une activité de chasse a été signalée à proximité.",
            source_ids=["SRC-RULE-DEFAULT", "SRC-SAFETY-ENGINE"]
        )
        
        logger.info(f"Initialized {len(self._trigger_rules)} default trigger rules")
    
    def get_trigger_rules(self) -> List[AlertTriggerRule]:
        """Retourne toutes les règles de déclenchement."""
        return list(self._trigger_rules.values())
    
    def get_active_rules(self) -> List[AlertTriggerRule]:
        """Retourne les règles actives."""
        return [r for r in self._trigger_rules.values() if r.is_active]
    
    # =========================================================================
    # SUBSCRIPTIONS
    # =========================================================================
    
    def _generate_subscription_id(self) -> str:
        """Génère un ID unique pour un abonnement."""
        self._subscription_counter += 1
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"SUB-{timestamp}-{self._subscription_counter:04d}"
    
    def create_subscription(
        self,
        endpoint: str,
        p256dh: str,
        auth: str,
        user_agent: str = "",
        device_type: str = "web",
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        geofence_radius_km: float = 5.0,
        alert_types: Optional[List[str]] = None,
        min_priority: str = "medium"
    ) -> PushSubscription:
        """
        Crée un nouvel abonnement push.
        """
        # Convertir les types d'alerte
        types = []
        if alert_types:
            for at in alert_types:
                try:
                    types.append(AlertType(at))
                except ValueError:
                    pass
        if not types:
            types = list(AlertType)
        
        # Convertir la priorité
        try:
            priority = AlertPriority(min_priority)
        except ValueError:
            priority = AlertPriority.MEDIUM
        
        subscription = PushSubscription(
            subscription_id=self._generate_subscription_id(),
            endpoint=endpoint,
            p256dh=p256dh,
            auth=auth,
            user_agent=user_agent,
            device_type=device_type,
            last_known_lat=lat,
            last_known_lng=lng,
            geofence_radius_km=geofence_radius_km,
            alert_types=types,
            min_priority=priority
        )
        
        self._subscriptions[subscription.subscription_id] = subscription
        
        logger.info(f"Subscription created: {subscription.subscription_id}")
        
        return subscription
    
    def update_subscription_location(
        self,
        subscription_id: str,
        lat: float,
        lng: float
    ) -> Optional[PushSubscription]:
        """Met à jour la position d'un abonnement pour le géofencing."""
        sub = self._subscriptions.get(subscription_id)
        if sub:
            sub.last_known_lat = lat
            sub.last_known_lng = lng
            return sub
        return None
    
    def get_subscription(self, subscription_id: str) -> Optional[PushSubscription]:
        """Récupère un abonnement."""
        return self._subscriptions.get(subscription_id)
    
    def get_subscriptions_in_radius(
        self,
        lat: float,
        lng: float,
        radius_km: float
    ) -> List[PushSubscription]:
        """
        Récupère les abonnements dans un rayon donné (géofencing).
        """
        import math
        
        result = []
        for sub in self._subscriptions.values():
            if sub.status != SubscriptionStatus.ACTIVE:
                continue
            if sub.last_known_lat is None or sub.last_known_lng is None:
                continue
            
            # Calcul distance Haversine
            R = 6371  # km
            lat1 = math.radians(lat)
            lat2 = math.radians(sub.last_known_lat)
            dlat = math.radians(sub.last_known_lat - lat)
            dlng = math.radians(sub.last_known_lng - lng)
            
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            distance = R * c
            
            # Utiliser le rayon le plus large entre celui demandé et celui de l'utilisateur
            effective_radius = max(radius_km, sub.geofence_radius_km)
            
            if distance <= effective_radius:
                result.append(sub)
        
        return result
    
    def get_all_active_subscriptions(self) -> List[PushSubscription]:
        """Récupère tous les abonnements actifs."""
        return [s for s in self._subscriptions.values() if s.status == SubscriptionStatus.ACTIVE]
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """Désactive un abonnement."""
        sub = self._subscriptions.get(subscription_id)
        if sub:
            sub.status = SubscriptionStatus.UNSUBSCRIBED
            return True
        return False
    
    # =========================================================================
    # NOTIFICATIONS
    # =========================================================================
    
    def _generate_notification_id(self) -> str:
        """Génère un ID unique pour une notification."""
        self._notification_counter += 1
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"NOTIF-{timestamp}-{self._notification_counter:04d}"
    
    def create_notification_from_rule(
        self,
        rule_id: str,
        zone_id: Optional[str] = None,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        radius_m: Optional[float] = None,
        custom_body: Optional[str] = None
    ) -> Optional[NotificationPayload]:
        """
        Crée une notification à partir d'une règle de déclenchement.
        """
        rule = self._trigger_rules.get(rule_id)
        if not rule or not rule.is_active:
            return None
        
        notification = NotificationPayload(
            notification_id=self._generate_notification_id(),
            alert_type=rule.alert_type,
            priority=rule.resulting_priority,
            title=rule.title_template,
            body=custom_body or rule.body_template,
            zone_id=zone_id,
            lat=lat,
            lng=lng,
            radius_m=radius_m,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=4),
            source_ids=rule.source_ids + ["SRC-NOTIFICATION-GENERATED"]
        )
        
        self._notifications[notification.notification_id] = notification
        
        logger.info(f"Notification created from rule {rule_id}: {notification.notification_id}")
        
        return notification
    
    def create_custom_notification(
        self,
        alert_type: str,
        priority: str,
        title: str,
        body: str,
        zone_id: Optional[str] = None,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        radius_m: Optional[float] = None,
        url: str = "/"
    ) -> NotificationPayload:
        """
        Crée une notification personnalisée.
        """
        try:
            atype = AlertType(alert_type)
        except ValueError:
            atype = AlertType.SAFETY_UPDATE
        
        try:
            apriority = AlertPriority(priority)
        except ValueError:
            apriority = AlertPriority.MEDIUM
        
        notification = NotificationPayload(
            notification_id=self._generate_notification_id(),
            alert_type=atype,
            priority=apriority,
            title=title,
            body=body,
            url=url,
            zone_id=zone_id,
            lat=lat,
            lng=lng,
            radius_m=radius_m,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=4),
            source_ids=["SRC-NOTIFICATION-CUSTOM"]
        )
        
        self._notifications[notification.notification_id] = notification
        
        return notification
    
    def get_notification(self, notification_id: str) -> Optional[NotificationPayload]:
        """Récupère une notification."""
        return self._notifications.get(notification_id)
    
    def list_notifications(self, limit: int = 50) -> List[NotificationPayload]:
        """Liste les notifications récentes."""
        notifications = list(self._notifications.values())
        notifications.sort(key=lambda x: x.created_at, reverse=True)
        return notifications[:limit]
    
    # =========================================================================
    # STATS
    # =========================================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """Statistiques du registre."""
        active_subs = len([s for s in self._subscriptions.values() if s.status == SubscriptionStatus.ACTIVE])
        
        return {
            "version": self._version,
            "vapid_configured": self._vapid_keys is not None,
            "subscriptions": {
                "total": len(self._subscriptions),
                "active": active_subs
            },
            "notifications": {
                "total": len(self._notifications)
            },
            "trigger_rules": {
                "total": len(self._trigger_rules),
                "active": len([r for r in self._trigger_rules.values() if r.is_active])
            }
        }


# =============================================================================
# SINGLETON
# =============================================================================

_registry_instance: Optional[NotificationRegistry] = None


def get_notification_registry() -> NotificationRegistry:
    """Obtenir l'instance singleton du registre."""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = NotificationRegistry()
    return _registry_instance


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    'AlertType',
    'AlertPriority',
    'SubscriptionStatus',
    # Models
    'VAPIDKeys',
    'PushSubscription',
    'NotificationPayload',
    'AlertTriggerRule',
    # Registry
    'NotificationRegistry',
    'get_notification_registry'
]
