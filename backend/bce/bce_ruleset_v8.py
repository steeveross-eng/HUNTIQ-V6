"""
BIONIC V8 — BCE Ruleset Complet + Auto-Run
==========================================
Ensemble complet des règles BCE pour validation écologique.

ZONES:
- bce_zone_classification_valid
- bce_zone_topographic_valid
- bce_zone_hydrology_valid
- bce_zone_human_pressure_valid

CORRIDORS:
- bce_corridor_continuity_valid
- bce_corridor_topography_valid
- bce_corridor_wwf_classification_valid
- bce_corridor_human_pressure_respected
- bce_corridor_stopover_detection_valid

AUTO-RUN:
- Validation automatique à chaque chargement territoire
- Validation à chaque classification de zone
- Validation à chaque génération de corridor
- Validation à chaque détection de stopover

VERSION: 8.0.0 — BCE Ruleset complet avec Auto-Run
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
import asyncio

logger = logging.getLogger("bionic_engine.bce_ruleset_v8")


# =====================================================================
# TYPES ET STRUCTURES
# =====================================================================

class ValidationStatus(Enum):
    COMPLIANT = "COMPLIANT"
    PARTIAL = "PARTIAL"
    NON_COMPLIANT = "NON_COMPLIANT"
    SKIPPED = "SKIPPED"


class RuleCategory(Enum):
    ZONE = "zone"
    CORRIDOR = "corridor"
    STOPOVER = "stopover"
    PIPELINE = "pipeline"


@dataclass
class RuleResult:
    """Résultat d'une règle BCE"""
    rule_name: str
    category: RuleCategory
    status: ValidationStatus
    score: float
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class BCEReport:
    """Rapport complet BCE"""
    global_status: ValidationStatus
    global_score: float
    rules_executed: int
    rules_passed: int
    rules_failed: int
    results: List[RuleResult]
    timestamp: str
    version: str = "bce_ruleset_v8.0.0"
    auto_run: bool = True


# =====================================================================
# RÈGLES ZONES
# =====================================================================

def bce_zone_classification_valid(zone_data: Dict[str, Any]) -> RuleResult:
    """Valide la classification écologique d'une zone."""
    issues = []
    score = 100
    
    zone_type = zone_data.get("zone_type", "unknown")
    species = zone_data.get("species", "unknown")
    ndvi = zone_data.get("ndvi", 0)
    
    # Validation NDVI
    ndvi_min = zone_data.get("ndvi_min", 0.3)
    ndvi_max = zone_data.get("ndvi_max", 0.8)
    
    if not (ndvi_min <= ndvi <= ndvi_max):
        issues.append(f"NDVI {ndvi:.2f} hors plage [{ndvi_min}-{ndvi_max}]")
        score -= 25
    
    # Validation cohérence zone/espèce
    valid_zones = {
        "orignal": ["alimentation", "repos", "rut", "pre_rut", "post_rut", "corridor"],
        "chevreuil": ["alimentation", "repos", "rut", "pre_rut", "post_rut", "corridor"],
        "ours_noir": ["alimentation", "repos", "taniere", "corridor"],
    }
    
    if species in valid_zones and zone_type not in valid_zones.get(species, []):
        issues.append(f"Zone '{zone_type}' non valide pour espèce '{species}'")
        score -= 30
    
    status = ValidationStatus.COMPLIANT if score >= 80 else (
        ValidationStatus.PARTIAL if score >= 50 else ValidationStatus.NON_COMPLIANT
    )
    
    return RuleResult(
        rule_name="bce_zone_classification_valid",
        category=RuleCategory.ZONE,
        status=status,
        score=max(0, score),
        message=f"Classification zone: {zone_type}/{species}",
        details={"zone_type": zone_type, "species": species, "ndvi": ndvi, "issues": issues}
    )


def bce_zone_topographic_valid(zone_data: Dict[str, Any]) -> RuleResult:
    """Valide les critères topographiques d'une zone."""
    issues = []
    score = 100
    
    slope = zone_data.get("slope", 0)
    aspect = zone_data.get("aspect", "")
    zone_type = zone_data.get("zone_type", "alimentation")
    
    # Contraintes de pente par type de zone
    slope_limits = {
        "alimentation": (0, 20),
        "repos": (5, 30),
        "rut": (0, 20),
        "corridor": (0, 15),
        "taniere": (15, 60),
    }
    
    min_slope, max_slope = slope_limits.get(zone_type, (0, 30))
    
    if slope < min_slope:
        issues.append(f"Pente {slope}% < min {min_slope}%")
        score -= 20
    elif slope > max_slope:
        issues.append(f"Pente {slope}% > max {max_slope}%")
        score -= 25
    
    # Validation aspect selon zone
    preferred_aspects = {
        "alimentation": ["S", "SE", "SW"],
        "repos": ["N", "NE", "NW"],
        "rut": ["S", "SE", "SW", "E", "W"],
        "taniere": ["N", "NE", "NW"],
    }
    
    if zone_type in preferred_aspects and aspect:
        if aspect not in preferred_aspects[zone_type]:
            issues.append(f"Aspect {aspect} non optimal pour {zone_type}")
            score -= 10
    
    status = ValidationStatus.COMPLIANT if score >= 80 else (
        ValidationStatus.PARTIAL if score >= 50 else ValidationStatus.NON_COMPLIANT
    )
    
    return RuleResult(
        rule_name="bce_zone_topographic_valid",
        category=RuleCategory.ZONE,
        status=status,
        score=max(0, score),
        message=f"Topographie: pente {slope}%, aspect {aspect or 'N/A'}",
        details={"slope": slope, "aspect": aspect, "zone_type": zone_type, "issues": issues}
    )


def bce_zone_hydrology_valid(zone_data: Dict[str, Any]) -> RuleResult:
    """Valide les critères hydrologiques d'une zone."""
    issues = []
    score = 100
    
    distance_to_water = zone_data.get("distance_to_water", 0)
    zone_type = zone_data.get("zone_type", "alimentation")
    species = zone_data.get("species", "orignal")
    
    # Distances maximales par espèce/zone
    water_limits = {
        ("orignal", "alimentation"): 500,
        ("orignal", "repos"): 1000,
        ("orignal", "rut"): 800,
        ("chevreuil", "alimentation"): 800,
        ("chevreuil", "repos"): 600,
        ("ours_noir", "alimentation"): 2000,
        ("ours_noir", "taniere"): 2000,
    }
    
    max_distance = water_limits.get((species, zone_type), 1000)
    
    if distance_to_water > max_distance:
        issues.append(f"Distance eau {distance_to_water}m > max {max_distance}m")
        score -= 30
    
    # Bonus proximité eau pour certaines zones
    if zone_type == "alimentation" and species in ["orignal", "ours_noir"]:
        if distance_to_water < 200:
            score = min(100, score + 10)  # Bonus
    
    status = ValidationStatus.COMPLIANT if score >= 80 else (
        ValidationStatus.PARTIAL if score >= 50 else ValidationStatus.NON_COMPLIANT
    )
    
    return RuleResult(
        rule_name="bce_zone_hydrology_valid",
        category=RuleCategory.ZONE,
        status=status,
        score=max(0, min(100, score)),
        message=f"Hydrologie: {distance_to_water}m de l'eau",
        details={"distance_to_water": distance_to_water, "max_allowed": max_distance, "issues": issues}
    )


def bce_zone_human_pressure_valid(zone_data: Dict[str, Any]) -> RuleResult:
    """Valide la pression humaine sur une zone."""
    issues = []
    score = 100
    
    human_pressure = zone_data.get("human_pressure", 0)
    distance_to_roads = zone_data.get("distance_to_roads", 1000)
    species = zone_data.get("species", "orignal")
    
    # Seuils par espèce
    pressure_thresholds = {
        "orignal": {"max": 0.30, "warning": 0.25},
        "chevreuil": {"max": 0.40, "warning": 0.35},
        "ours_noir": {"max": 0.25, "warning": 0.20},
    }
    
    thresholds = pressure_thresholds.get(species, {"max": 0.35, "warning": 0.30})
    
    if human_pressure > thresholds["max"]:
        issues.append(f"Pression humaine {human_pressure:.2f} > max {thresholds['max']}")
        score -= 40
    elif human_pressure > thresholds["warning"]:
        issues.append(f"Pression humaine {human_pressure:.2f} élevée")
        score -= 15
    
    # Distance aux routes
    min_road_distances = {"orignal": 200, "chevreuil": 100, "ours_noir": 300}
    min_road = min_road_distances.get(species, 150)
    
    if distance_to_roads < min_road:
        issues.append(f"Distance routes {distance_to_roads}m < min {min_road}m")
        score -= 25
    
    status = ValidationStatus.COMPLIANT if score >= 80 else (
        ValidationStatus.PARTIAL if score >= 50 else ValidationStatus.NON_COMPLIANT
    )
    
    return RuleResult(
        rule_name="bce_zone_human_pressure_valid",
        category=RuleCategory.ZONE,
        status=status,
        score=max(0, score),
        message=f"Pression humaine: {human_pressure:.2f}",
        details={"human_pressure": human_pressure, "distance_to_roads": distance_to_roads, "issues": issues}
    )


# =====================================================================
# RÈGLES CORRIDORS
# =====================================================================

def bce_corridor_continuity_valid(corridor_data: Dict[str, Any]) -> RuleResult:
    """Valide la continuité d'un corridor."""
    import math
    
    positions = corridor_data.get("positions", [])
    max_gap_m = corridor_data.get("max_gap_m", 100)
    
    if len(positions) < 3:
        return RuleResult(
            rule_name="bce_corridor_continuity_valid",
            category=RuleCategory.CORRIDOR,
            status=ValidationStatus.NON_COMPLIANT,
            score=0,
            message="Corridor insuffisant: moins de 3 points",
            details={"points_count": len(positions)}
        )
    
    METERS_PER_DEG = 111320.0
    issues = []
    max_found_gap = 0
    
    for i in range(len(positions) - 1):
        p1, p2 = positions[i], positions[i + 1]
        lat1 = p1.get("lat", p1[0]) if isinstance(p1, dict) else p1[0]
        lng1 = p1.get("lng", p1[1]) if isinstance(p1, dict) else p1[1]
        lat2 = p2.get("lat", p2[0]) if isinstance(p2, dict) else p2[0]
        lng2 = p2.get("lng", p2[1]) if isinstance(p2, dict) else p2[1]
        
        lat_diff = (lat2 - lat1) * METERS_PER_DEG
        lng_diff = (lng2 - lng1) * METERS_PER_DEG * math.cos(math.radians((lat1 + lat2) / 2))
        distance = math.sqrt(lat_diff**2 + lng_diff**2)
        
        max_found_gap = max(max_found_gap, distance)
        if distance > max_gap_m:
            issues.append({"segment": i, "gap_m": round(distance, 1)})
    
    score = 100 - min(50, len(issues) * 15)
    status = ValidationStatus.COMPLIANT if score >= 80 else (
        ValidationStatus.PARTIAL if score >= 50 else ValidationStatus.NON_COMPLIANT
    )
    
    return RuleResult(
        rule_name="bce_corridor_continuity_valid",
        category=RuleCategory.CORRIDOR,
        status=status,
        score=max(0, score),
        message=f"Continuité: {len(positions)} points, gap max {max_found_gap:.1f}m",
        details={"points_count": len(positions), "max_gap_m": round(max_found_gap, 1), "ruptures": issues}
    )


def bce_corridor_topography_valid(corridor_data: Dict[str, Any]) -> RuleResult:
    """Valide la topographie du corridor."""
    issues = []
    score = 100
    
    terrain_types = corridor_data.get("terrain_types", [])
    avg_slope = corridor_data.get("avg_slope", 10)
    follows_drainage = corridor_data.get("follows_drainage", False)
    
    # Pénalité pente
    if avg_slope > 20:
        issues.append(f"Pente moyenne {avg_slope}% > 20%")
        score -= 30
    elif avg_slope > 15:
        issues.append(f"Pente moyenne {avg_slope}% élevée")
        score -= 15
    
    # Terrains défavorables
    unfavorable = ["urban", "highway", "cliff", "open_water"]
    crossed_unfavorable = [t for t in terrain_types if t in unfavorable]
    if crossed_unfavorable:
        issues.append(f"Terrain défavorable: {', '.join(crossed_unfavorable)}")
        score -= 25 * len(crossed_unfavorable)
    
    # Bonus drainage
    if follows_drainage:
        score = min(100, score + 10)
    
    status = ValidationStatus.COMPLIANT if score >= 80 else (
        ValidationStatus.PARTIAL if score >= 50 else ValidationStatus.NON_COMPLIANT
    )
    
    return RuleResult(
        rule_name="bce_corridor_topography_valid",
        category=RuleCategory.CORRIDOR,
        status=status,
        score=max(0, score),
        message=f"Topographie corridor: pente {avg_slope}%",
        details={"avg_slope": avg_slope, "terrain_types": terrain_types, "issues": issues}
    )


def bce_corridor_wwf_classification_valid(corridor_data: Dict[str, Any]) -> RuleResult:
    """Valide la classification WWF du corridor."""
    issues = []
    score = 100
    
    width_m = corridor_data.get("width_m", 500)
    length_m = corridor_data.get("length_m", 0)
    declared_type = corridor_data.get("wwf_type", "")
    
    # Classification attendue
    if width_m > 5000:
        expected_type = "macro_corridor"
    elif width_m >= 1000:
        expected_type = "biological_corridor"
    else:
        expected_type = "conservation_corridor"
    
    # Vérifier cohérence
    if declared_type and declared_type != expected_type:
        issues.append(f"Type déclaré '{declared_type}' ≠ attendu '{expected_type}'")
        score -= 20
    
    # Ratio longueur/largeur
    if length_m > 0:
        ratio = length_m / max(width_m, 1)
        if ratio < 2:
            issues.append(f"Ratio longueur/largeur ({ratio:.1f}) < 2")
            score -= 15
    
    # Largeur minimale
    if width_m < 50:
        issues.append(f"Largeur {width_m}m trop faible pour connectivité")
        score -= 30
    
    status = ValidationStatus.COMPLIANT if score >= 80 else (
        ValidationStatus.PARTIAL if score >= 50 else ValidationStatus.NON_COMPLIANT
    )
    
    return RuleResult(
        rule_name="bce_corridor_wwf_classification_valid",
        category=RuleCategory.CORRIDOR,
        status=status,
        score=max(0, score),
        message=f"WWF: {expected_type} ({width_m}m)",
        details={"width_m": width_m, "expected_type": expected_type, "declared_type": declared_type, "issues": issues}
    )


def bce_corridor_human_pressure_respected(corridor_data: Dict[str, Any]) -> RuleResult:
    """Valide la pression humaine sur le corridor."""
    issues = []
    score = 100
    
    human_pressure = corridor_data.get("human_pressure", 0)
    crosses_roads = corridor_data.get("crosses_roads", 0)
    species = corridor_data.get("species", "orignal")
    
    # Seuils pression
    max_pressure = {"orignal": 0.25, "chevreuil": 0.35, "ours_noir": 0.20}.get(species, 0.30)
    
    if human_pressure > max_pressure:
        issues.append(f"Pression {human_pressure:.2f} > max {max_pressure}")
        score -= 35
    
    # Pénalité traversées de routes
    if crosses_roads > 2:
        issues.append(f"{crosses_roads} traversées de routes")
        score -= 10 * min(crosses_roads, 4)
    
    status = ValidationStatus.COMPLIANT if score >= 80 else (
        ValidationStatus.PARTIAL if score >= 50 else ValidationStatus.NON_COMPLIANT
    )
    
    return RuleResult(
        rule_name="bce_corridor_human_pressure_respected",
        category=RuleCategory.CORRIDOR,
        status=status,
        score=max(0, score),
        message=f"Pression corridor: {human_pressure:.2f}",
        details={"human_pressure": human_pressure, "crosses_roads": crosses_roads, "issues": issues}
    )


def bce_corridor_stopover_detection_valid(corridor_data: Dict[str, Any]) -> RuleResult:
    """Valide la détection des stopovers (zones critiques)."""
    issues = []
    score = 100
    
    stopovers = corridor_data.get("stopovers", [])
    corridor_length = corridor_data.get("length_m", 1000)
    
    # Vérifier présence de stopovers sur corridors longs
    if corridor_length > 5000 and len(stopovers) == 0:
        issues.append(f"Aucun stopover détecté sur corridor de {corridor_length/1000:.1f}km")
        score -= 20
    
    # Valider chaque stopover
    for i, stopover in enumerate(stopovers):
        stopover_type = stopover.get("type", "unknown")
        valid_types = ["alimentation", "repos", "rut", "pre_rut", "post_rut", "thermique", "refuge"]
        
        if stopover_type not in valid_types:
            issues.append(f"Stopover {i+1}: type '{stopover_type}' invalide")
            score -= 10
    
    status = ValidationStatus.COMPLIANT if score >= 80 else (
        ValidationStatus.PARTIAL if score >= 50 else ValidationStatus.NON_COMPLIANT
    )
    
    return RuleResult(
        rule_name="bce_corridor_stopover_detection_valid",
        category=RuleCategory.STOPOVER,
        status=status,
        score=max(0, score),
        message=f"Stopovers: {len(stopovers)} détectés",
        details={"stopovers_count": len(stopovers), "corridor_length_m": corridor_length, "issues": issues}
    )


# =====================================================================
# BCE AUTO-RUN ENGINE
# =====================================================================

class BCEAutoRunEngine:
    """
    Moteur d'exécution automatique BCE.
    Valide automatiquement à chaque événement du pipeline.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("bionic_engine.bce_autorun")
        self.last_report: Optional[BCEReport] = None
        self.auto_run_enabled = True
        
        # Registre des règles
        self.zone_rules = [
            bce_zone_classification_valid,
            bce_zone_topographic_valid,
            bce_zone_hydrology_valid,
            bce_zone_human_pressure_valid,
        ]
        
        self.corridor_rules = [
            bce_corridor_continuity_valid,
            bce_corridor_topography_valid,
            bce_corridor_wwf_classification_valid,
            bce_corridor_human_pressure_respected,
            bce_corridor_stopover_detection_valid,
        ]
    
    def run_zone_validation(self, zone_data: Dict[str, Any]) -> BCEReport:
        """Exécute toutes les règles zones."""
        results = []
        for rule in self.zone_rules:
            try:
                result = rule(zone_data)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Rule {rule.__name__} failed: {e}")
                results.append(RuleResult(
                    rule_name=rule.__name__,
                    category=RuleCategory.ZONE,
                    status=ValidationStatus.SKIPPED,
                    score=0,
                    message=f"Erreur: {str(e)}"
                ))
        
        return self._create_report(results)
    
    def run_corridor_validation(self, corridor_data: Dict[str, Any]) -> BCEReport:
        """Exécute toutes les règles corridors."""
        results = []
        for rule in self.corridor_rules:
            try:
                result = rule(corridor_data)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Rule {rule.__name__} failed: {e}")
                results.append(RuleResult(
                    rule_name=rule.__name__,
                    category=RuleCategory.CORRIDOR,
                    status=ValidationStatus.SKIPPED,
                    score=0,
                    message=f"Erreur: {str(e)}"
                ))
        
        return self._create_report(results)
    
    def run_full_validation(self, data: Dict[str, Any]) -> BCEReport:
        """Exécute toutes les règles (zones + corridors)."""
        results = []
        
        # Règles zones
        for rule in self.zone_rules:
            try:
                result = rule(data)
                results.append(result)
            except Exception as e:
                self.logger.warning(f"Zone rule {rule.__name__} skipped: {e}")
        
        # Règles corridors si données présentes
        if data.get("positions") or data.get("corridor_points"):
            for rule in self.corridor_rules:
                try:
                    result = rule(data)
                    results.append(result)
                except Exception as e:
                    self.logger.warning(f"Corridor rule {rule.__name__} skipped: {e}")
        
        report = self._create_report(results)
        self.last_report = report
        return report
    
    def on_territory_load(self, territory_data: Dict[str, Any]) -> BCEReport:
        """Auto-run déclenché au chargement du territoire."""
        self.logger.info("BCE Auto-Run: Territory load event")
        return self.run_full_validation(territory_data)
    
    def on_zone_classification(self, zone_data: Dict[str, Any]) -> BCEReport:
        """Auto-run déclenché à chaque classification de zone."""
        self.logger.info("BCE Auto-Run: Zone classification event")
        return self.run_zone_validation(zone_data)
    
    def on_corridor_generation(self, corridor_data: Dict[str, Any]) -> BCEReport:
        """Auto-run déclenché à chaque génération de corridor."""
        self.logger.info("BCE Auto-Run: Corridor generation event")
        return self.run_corridor_validation(corridor_data)
    
    def on_stopover_detection(self, stopover_data: Dict[str, Any]) -> BCEReport:
        """Auto-run déclenché à chaque détection de stopover."""
        self.logger.info("BCE Auto-Run: Stopover detection event")
        return self.run_corridor_validation(stopover_data)
    
    def _create_report(self, results: List[RuleResult]) -> BCEReport:
        """Crée un rapport BCE à partir des résultats."""
        if not results:
            return BCEReport(
                global_status=ValidationStatus.SKIPPED,
                global_score=0,
                rules_executed=0,
                rules_passed=0,
                rules_failed=0,
                results=[],
                timestamp=datetime.now(timezone.utc).isoformat()
            )
        
        passed = sum(1 for r in results if r.status == ValidationStatus.COMPLIANT)
        failed = sum(1 for r in results if r.status == ValidationStatus.NON_COMPLIANT)
        avg_score = sum(r.score for r in results) / len(results)
        
        if failed > 0:
            global_status = ValidationStatus.NON_COMPLIANT
        elif avg_score >= 80:
            global_status = ValidationStatus.COMPLIANT
        else:
            global_status = ValidationStatus.PARTIAL
        
        return BCEReport(
            global_status=global_status,
            global_score=round(avg_score, 1),
            rules_executed=len(results),
            rules_passed=passed,
            rules_failed=failed,
            results=results,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut du moteur BCE Auto-Run."""
        return {
            "auto_run_enabled": self.auto_run_enabled,
            "last_report": {
                "status": self.last_report.global_status.value if self.last_report else None,
                "score": self.last_report.global_score if self.last_report else None,
                "timestamp": self.last_report.timestamp if self.last_report else None,
            } if self.last_report else None,
            "rules_count": {
                "zones": len(self.zone_rules),
                "corridors": len(self.corridor_rules),
                "total": len(self.zone_rules) + len(self.corridor_rules),
            },
            "version": "bce_autorun_v8.0.0"
        }


# Instance singleton
bce_autorun_engine = BCEAutoRunEngine()


# =====================================================================
# HELPER FUNCTIONS
# =====================================================================

def validate_territory_load(territory_data: Dict[str, Any]) -> Dict[str, Any]:
    """Valide automatiquement au chargement du territoire."""
    report = bce_autorun_engine.on_territory_load(territory_data)
    return {
        "global_status": report.global_status.value,
        "global_score": report.global_score,
        "rules_executed": report.rules_executed,
        "rules_passed": report.rules_passed,
        "rules_failed": report.rules_failed,
        "results": [
            {
                "rule": r.rule_name,
                "category": r.category.value,
                "status": r.status.value,
                "score": r.score,
                "message": r.message,
            }
            for r in report.results
        ],
        "timestamp": report.timestamp,
        "auto_run": True
    }
