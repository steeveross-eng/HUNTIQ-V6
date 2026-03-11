"""
BIONIC V5 — VALIDATION PIPELINE
================================
PHASE 7 — Knowledge Layer

Pipeline de validation scientifique et terrain.
Intègre: caméras de surveillance, traces, données GPS/télémétrie.

Ce module permet de valider les règles du Knowledge Layer
contre des données réelles collectées sur le terrain.

VERSION: 1.0.0
Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import uuid


class ValidationSource(str, Enum):
    """Types de sources de validation terrain"""
    CAMERA_TRAP = "camera_trap"          # Caméras de surveillance
    GPS_COLLAR = "gps_collar"            # Colliers GPS
    TELEMETRY = "telemetry"              # Données télémétrie
    TRACK_SURVEY = "track_survey"        # Relevés de traces
    AERIAL_SURVEY = "aerial_survey"      # Survols aériens
    HARVEST_DATA = "harvest_data"        # Données de récolte
    SIGHTING_REPORT = "sighting_report"  # Rapports d'observation
    EXPERT_VALIDATION = "expert_validation"  # Validation par expert


class ValidationOutcome(str, Enum):
    """Résultats possibles de validation"""
    CONFIRMED = "confirmed"              # Règle confirmée
    PARTIALLY_CONFIRMED = "partially_confirmed"
    NOT_CONFIRMED = "not_confirmed"      # Règle non confirmée
    CONTRADICTED = "contradicted"        # Règle contredite
    INSUFFICIENT_DATA = "insufficient_data"


@dataclass
class ValidationDataPoint:
    """
    Point de données de validation terrain.
    
    Représente une observation unique (caméra, GPS, etc.)
    utilisée pour valider une règle du Knowledge Layer.
    """
    
    data_id: str = field(default_factory=lambda: f"VDP-{uuid.uuid4().hex[:8].upper()}")
    
    # Source
    source_type: ValidationSource = ValidationSource.SIGHTING_REPORT
    source_device_id: Optional[str] = None
    
    # Localisation
    latitude: float = 0.0
    longitude: float = 0.0
    
    # Temporel
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Observation
    species_detected: str = ""
    behavior_observed: str = ""
    confidence: float = 0.5
    
    # Métadonnées
    raw_data: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""


@dataclass
class ValidationResult:
    """
    Résultat de validation d'une règle.
    
    Agrège les points de données pour évaluer
    si une règle du Knowledge Layer est validée.
    """
    
    result_id: str = field(default_factory=lambda: f"VR-{uuid.uuid4().hex[:8].upper()}")
    
    # Règle validée
    rule_id: str = ""
    rule_type: str = ""  # "behavior", "habitat", "seasonal"
    
    # Résultat
    outcome: ValidationOutcome = ValidationOutcome.INSUFFICIENT_DATA
    confidence: float = 0.0
    
    # Données
    data_points_count: int = 0
    data_points_confirming: int = 0
    data_points_contradicting: int = 0
    
    # Statistiques
    agreement_rate: float = 0.0
    statistical_significance: float = 0.0
    
    # Sources
    validation_sources: List[ValidationSource] = field(default_factory=list)
    
    # Recommandation
    recommendation: str = ""
    adjustment_suggested: Optional[float] = None
    
    # Métadonnées
    validated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    validated_by: str = ""


@dataclass
class CameraStation:
    """Station de caméra de surveillance pour validation"""
    
    station_id: str
    name: str
    latitude: float
    longitude: float
    
    # Statut
    is_active: bool = True
    installation_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Configuration
    trigger_sensitivity: str = "medium"
    capture_interval_s: int = 30
    
    # Statistiques
    total_triggers: int = 0
    wildlife_detections: int = 0
    last_detection: Optional[datetime] = None


@dataclass
class GPSCollar:
    """Collier GPS pour suivi télémétrique"""
    
    collar_id: str
    species: str
    individual_id: str
    
    # Statut
    is_active: bool = True
    deployment_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Configuration
    fix_interval_minutes: int = 60
    
    # Statistiques
    total_fixes: int = 0
    successful_fixes: int = 0
    last_fix: Optional[datetime] = None


class ValidationPipeline:
    """
    Pipeline de validation terrain pour le Knowledge Layer.
    
    Ce pipeline permet de:
    1. Collecter des données de terrain (caméras, GPS, traces)
    2. Comparer ces données avec les prédictions des règles
    3. Évaluer la validité des règles
    4. Suggérer des ajustements si nécessaire
    """
    
    def __init__(self):
        self._camera_stations: Dict[str, CameraStation] = {}
        self._gps_collars: Dict[str, GPSCollar] = {}
        self._data_points: List[ValidationDataPoint] = []
        self._validation_results: Dict[str, ValidationResult] = {}
        
        self._initialize_demo_infrastructure()
    
    def _initialize_demo_infrastructure(self):
        """Initialiser l'infrastructure de démonstration"""
        
        # Caméras de démonstration
        demo_cameras = [
            CameraStation(
                station_id="CAM-001",
                name="Secteur Nord - Saline",
                latitude=46.8500,
                longitude=-71.2500,
                total_triggers=1247,
                wildlife_detections=892
            ),
            CameraStation(
                station_id="CAM-002",
                name="Corridor Est",
                latitude=46.8200,
                longitude=-71.1800,
                total_triggers=856,
                wildlife_detections=543
            ),
            CameraStation(
                station_id="CAM-003",
                name="Zone Alimentation",
                latitude=46.7900,
                longitude=-71.2200,
                total_triggers=2103,
                wildlife_detections=1654
            )
        ]
        
        for cam in demo_cameras:
            self._camera_stations[cam.station_id] = cam
        
        # Colliers GPS de démonstration
        demo_collars = [
            GPSCollar(
                collar_id="GPS-M01",
                species="moose",
                individual_id="MOOSE-2023-01",
                total_fixes=8760,
                successful_fixes=8234
            ),
            GPSCollar(
                collar_id="GPS-D01",
                species="deer",
                individual_id="DEER-2023-01",
                total_fixes=4380,
                successful_fixes=4012
            )
        ]
        
        for collar in demo_collars:
            self._gps_collars[collar.collar_id] = collar
    
    def add_data_point(self, data_point: ValidationDataPoint):
        """Ajouter un point de données de validation"""
        self._data_points.append(data_point)
    
    def validate_behavior_rule(
        self,
        rule_id: str,
        species: str,
        start_date: datetime,
        end_date: datetime,
        min_data_points: int = 30
    ) -> ValidationResult:
        """
        Valider une règle comportementale contre les données terrain.
        
        Args:
            rule_id: ID de la règle à valider
            species: Espèce concernée
            start_date: Début de la période de validation
            end_date: Fin de la période de validation
            min_data_points: Nombre minimum de points requis
            
        Returns:
            ValidationResult avec l'évaluation
        """
        # Filtrer les données pertinentes
        relevant_data = [
            dp for dp in self._data_points
            if dp.species_detected.lower() == species.lower()
            and start_date <= dp.timestamp <= end_date
        ]
        
        result = ValidationResult(
            rule_id=rule_id,
            rule_type="behavior",
            data_points_count=len(relevant_data)
        )
        
        if len(relevant_data) < min_data_points:
            result.outcome = ValidationOutcome.INSUFFICIENT_DATA
            result.recommendation = f"Collecter au moins {min_data_points - len(relevant_data)} points supplémentaires"
            return result
        
        # TODO: Implémenter la logique de validation réelle
        # Pour l'instant, retourner un résultat placeholder
        result.outcome = ValidationOutcome.CONFIRMED
        result.confidence = 0.85
        result.agreement_rate = 0.87
        result.validation_sources = [ValidationSource.CAMERA_TRAP, ValidationSource.GPS_COLLAR]
        result.recommendation = "Règle validée avec haute confiance"
        
        self._validation_results[result.result_id] = result
        return result
    
    def validate_habitat_weight(
        self,
        weight_id: str,
        species: str,
        habitat_type: str,
        min_observations: int = 50
    ) -> ValidationResult:
        """
        Valider une pondération d'habitat contre les données terrain.
        
        Utilise les données de localisation (GPS, caméras) pour
        évaluer si la pondération reflète l'utilisation réelle.
        """
        result = ValidationResult(
            rule_id=weight_id,
            rule_type="habitat"
        )
        
        # TODO: Implémenter la logique de validation
        result.outcome = ValidationOutcome.PARTIALLY_CONFIRMED
        result.confidence = 0.75
        result.recommendation = "Pondération à ajuster légèrement (+0.05)"
        result.adjustment_suggested = 0.05
        
        self._validation_results[result.result_id] = result
        return result
    
    def get_camera_stations(self) -> List[CameraStation]:
        """Obtenir la liste des stations de caméras"""
        return list(self._camera_stations.values())
    
    def get_gps_collars(self) -> List[GPSCollar]:
        """Obtenir la liste des colliers GPS"""
        return list(self._gps_collars.values())
    
    def get_validation_results(self, rule_id: str = None) -> List[ValidationResult]:
        """Obtenir les résultats de validation"""
        if rule_id:
            return [r for r in self._validation_results.values() if r.rule_id == rule_id]
        return list(self._validation_results.values())
    
    def get_infrastructure_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques de l'infrastructure de validation"""
        cameras = self._camera_stations.values()
        collars = self._gps_collars.values()
        
        return {
            "cameras": {
                "total": len(cameras),
                "active": sum(1 for c in cameras if c.is_active),
                "total_detections": sum(c.wildlife_detections for c in cameras)
            },
            "gps_collars": {
                "total": len(collars),
                "active": sum(1 for c in collars if c.is_active),
                "total_fixes": sum(c.total_fixes for c in collars)
            },
            "data_points": {
                "total": len(self._data_points),
                "by_source": self._count_by_source()
            },
            "validation_results": {
                "total": len(self._validation_results),
                "confirmed": sum(1 for r in self._validation_results.values() if r.outcome == ValidationOutcome.CONFIRMED)
            }
        }
    
    def _count_by_source(self) -> Dict[str, int]:
        """Compter les points de données par source"""
        counts = {}
        for dp in self._data_points:
            source = dp.source_type.value
            counts[source] = counts.get(source, 0) + 1
        return counts


# Singleton
_pipeline_instance: Optional[ValidationPipeline] = None


def get_validation_pipeline() -> ValidationPipeline:
    """Obtenir l'instance singleton du pipeline de validation"""
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = ValidationPipeline()
    return _pipeline_instance


__all__ = [
    'ValidationSource',
    'ValidationOutcome',
    'ValidationDataPoint',
    'ValidationResult',
    'CameraStation',
    'GPSCollar',
    'ValidationPipeline',
    'get_validation_pipeline'
]
