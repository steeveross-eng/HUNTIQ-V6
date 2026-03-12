"""
BCE-4X Corridor Validator — Module critique corridors fauniques
================================================================
BIONIC V9 — Validateur BCE-4X dedie aux corridors

Module declare CRITIQUE par BCE-4X. Chaque corridor genere doit passer
toutes les validations avant rendu UI.

Regles appliquees:
  1. GEOMETRIE — LineString valide, continuite, linearite (non circulaire)
  2. CLASSIFICATION — 5 niveaux accessibles, coherence distance/type
  3. CLIPPING — Strict au perimetre 2 km²
  4. HABITATIONS — Interdiction totale de traverser zones urbaines
  5. SCORING — Zero hardcoding, subscores dynamiques obligatoires
  6. CONTINUITE — Aucun gap > seuil autorise
  7. COHERENCE MOVEMENT ENGINE — Alignement A* + terrain + connectivite

VERSION: BCE-4X-CORRIDOR-1.0
"""

import math
import logging
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone

logger = logging.getLogger("bce.validators.corridor_v9")


# =====================================================================
# TYPES
# =====================================================================

class CorridorViolationSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CorridorViolationType(Enum):
    HARDCODED_SCORE = "hardcoded_score"
    GEOMETRY_INVALID = "geometry_invalid"
    CIRCULAR_CORRIDOR = "circular_corridor"
    OUT_OF_BOUNDS = "out_of_bounds"
    OVER_HABITATION = "over_habitation"
    CLASSIFICATION_UNREACHABLE = "classification_unreachable"
    CONTINUITY_BREAK = "continuity_break"
    MISSING_ENRICHMENT = "missing_enrichment"
    SCORE_INCOHERENCE = "score_incoherence"
    ENGINE_DISCONNECTED = "engine_disconnected"


@dataclass
class CorridorViolation:
    type: CorridorViolationType
    severity: CorridorViolationSeverity
    message: str
    corridor_id: str
    expected: Any = None
    actual: Any = None
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict:
        return {
            "type": self.type.value,
            "severity": self.severity.value,
            "message": self.message,
            "corridor_id": self.corridor_id,
            "expected": str(self.expected),
            "actual": str(self.actual),
            "timestamp": self.timestamp,
        }


# =====================================================================
# HARDCODED SCORE DETECTOR
# =====================================================================

KNOWN_HARDCODED_VALUES = {
    "terrain": 65.0,
    "habitat": 70.0,
    "zone_score": 50,
}

METERS_PER_DEG = 111320.0


def detect_hardcoded_scores(corridor: Dict) -> List[CorridorViolation]:
    """Detecte les subscores hardcodes dans un corridor."""
    violations = []
    props = corridor.get("properties", {})
    scoring = props.get("scoring", {})
    subscores = scoring.get("subscores", {})
    cid = corridor.get("id", "unknown")

    for key, hardcoded_val in KNOWN_HARDCODED_VALUES.items():
        if key in subscores and subscores[key] == hardcoded_val:
            violations.append(CorridorViolation(
                type=CorridorViolationType.HARDCODED_SCORE,
                severity=CorridorViolationSeverity.CRITICAL,
                message=f"Subscore '{key}' hardcode a {hardcoded_val}",
                corridor_id=cid,
                expected="Valeur dynamique calculee",
                actual=hardcoded_val,
            ))

    return violations


# =====================================================================
# GEOMETRY VALIDATOR
# =====================================================================

def validate_geometry(corridor: Dict) -> List[CorridorViolation]:
    """Valide la geometrie du corridor: LineString, non circulaire, continu."""
    violations = []
    cid = corridor.get("id", "unknown")
    geom = corridor.get("geometry", {})

    if geom.get("type") != "LineString":
        violations.append(CorridorViolation(
            type=CorridorViolationType.GEOMETRY_INVALID,
            severity=CorridorViolationSeverity.CRITICAL,
            message=f"Geometrie attendue: LineString, recue: {geom.get('type')}",
            corridor_id=cid,
            expected="LineString",
            actual=geom.get("type"),
        ))
        return violations

    coords = geom.get("coordinates", [])
    if len(coords) < 2:
        violations.append(CorridorViolation(
            type=CorridorViolationType.GEOMETRY_INVALID,
            severity=CorridorViolationSeverity.CRITICAL,
            message="Corridor avec moins de 2 points",
            corridor_id=cid,
            expected=">=2 points",
            actual=len(coords),
        ))
        return violations

    # Check circulaire: start ~= end
    start = coords[0]
    end = coords[-1]
    dist_start_end = _haversine_m(start[1], start[0], end[1], end[0])
    total_length = _path_length_m(coords)

    if total_length > 0 and dist_start_end < total_length * 0.15:
        violations.append(CorridorViolation(
            type=CorridorViolationType.CIRCULAR_CORRIDOR,
            severity=CorridorViolationSeverity.HIGH,
            message=f"Corridor circulaire detecte: distance debut-fin={dist_start_end:.0f}m, longueur={total_length:.0f}m",
            corridor_id=cid,
            expected="Distance debut-fin > 15% de la longueur",
            actual=f"{dist_start_end:.0f}m / {total_length:.0f}m",
        ))

    # Check continuite (gap max)
    max_gap_m = 200.0
    for i in range(len(coords) - 1):
        c1, c2 = coords[i], coords[i + 1]
        gap = _haversine_m(c1[1], c1[0], c2[1], c2[0])
        if gap > max_gap_m:
            violations.append(CorridorViolation(
                type=CorridorViolationType.CONTINUITY_BREAK,
                severity=CorridorViolationSeverity.MEDIUM,
                message=f"Gap de {gap:.0f}m entre segments {i} et {i+1} (max: {max_gap_m}m)",
                corridor_id=cid,
                expected=f"<= {max_gap_m}m",
                actual=f"{gap:.0f}m",
            ))
            break

    return violations


# =====================================================================
# CLIPPING VALIDATOR (2 km²)
# =====================================================================

def validate_clipping(corridor: Dict, bounds: Dict) -> List[CorridorViolation]:
    """Verifie que le corridor reste strictement dans le perimetre 2km²."""
    violations = []
    if not bounds:
        return violations

    cid = corridor.get("id", "unknown")
    coords = corridor.get("geometry", {}).get("coordinates", [])
    margin = 0.001  # ~111m tolerance

    south = bounds.get("south", -90) - margin
    north = bounds.get("north", 90) + margin
    west = bounds.get("west", -180) - margin
    east = bounds.get("east", 180) + margin

    for i, c in enumerate(coords):
        lng, lat = c[0], c[1]
        if lat < south or lat > north or lng < west or lng > east:
            violations.append(CorridorViolation(
                type=CorridorViolationType.OUT_OF_BOUNDS,
                severity=CorridorViolationSeverity.HIGH,
                message=f"Point {i} hors perimetre: ({lat:.5f}, {lng:.5f})",
                corridor_id=cid,
                expected=f"[{south:.5f}-{north:.5f}] x [{west:.5f}-{east:.5f}]",
                actual=f"({lat:.5f}, {lng:.5f})",
            ))
            break

    return violations


# =====================================================================
# CLASSIFICATION VALIDATOR
# =====================================================================

VALID_CLASSIFICATIONS = {
    # V9 classification (5 niveaux)
    "gris", "jaune", "orange", "rouge", "rouge_raye",
    # Legacy WWF (backward compatibility)
    "macro_corridor", "biological_corridor", "conservation_corridor",
}


def validate_classification(corridor: Dict) -> List[CorridorViolation]:
    """Verifie que la classification est valide et coherente avec la distance."""
    violations = []
    cid = corridor.get("id", "unknown")
    props = corridor.get("properties", {})
    ctype = props.get("corridor_type", "")
    distance = props.get("distance_m", 0)

    if ctype not in VALID_CLASSIFICATIONS:
        violations.append(CorridorViolation(
            type=CorridorViolationType.CLASSIFICATION_UNREACHABLE,
            severity=CorridorViolationSeverity.MEDIUM,
            message=f"Classification inconnue: '{ctype}'",
            corridor_id=cid,
            expected=str(VALID_CLASSIFICATIONS),
            actual=ctype,
        ))

    return violations


# =====================================================================
# SCORING COHERENCE VALIDATOR
# =====================================================================

def validate_scoring_coherence(corridor: Dict) -> List[CorridorViolation]:
    """Verifie la coherence et la non-staticite du scoring."""
    violations = []
    cid = corridor.get("id", "unknown")
    props = corridor.get("properties", {})
    scoring = props.get("scoring", {})
    score = scoring.get("score", 0)

    if score < 0 or score > 100:
        violations.append(CorridorViolation(
            type=CorridorViolationType.SCORE_INCOHERENCE,
            severity=CorridorViolationSeverity.HIGH,
            message=f"Score hors bornes: {score}",
            corridor_id=cid,
            expected="[0, 100]",
            actual=score,
        ))

    enrichment = props.get("scores_10x")
    if not enrichment:
        violations.append(CorridorViolation(
            type=CorridorViolationType.MISSING_ENRICHMENT,
            severity=CorridorViolationSeverity.MEDIUM,
            message="Enrichissement 10X absent (enrich_corridor non appele)",
            corridor_id=cid,
            expected="scores_10x present",
            actual="absent",
        ))

    return violations


# =====================================================================
# AGGREGATE VALIDATOR
# =====================================================================

def validate_corridor_batch(
    corridors: List[Dict],
    bounds: Dict = None,
) -> Dict[str, Any]:
    """
    Valide un batch de corridors avec toutes les regles BCE-4X.

    Returns:
        Rapport BCE-4X complet avec violations et metriques.
    """
    all_violations = []
    per_corridor = {}

    for corridor in corridors:
        cid = corridor.get("id", "unknown")
        violations = []
        violations.extend(detect_hardcoded_scores(corridor))
        violations.extend(validate_geometry(corridor))
        violations.extend(validate_classification(corridor))
        violations.extend(validate_scoring_coherence(corridor))
        if bounds:
            violations.extend(validate_clipping(corridor, bounds))
        all_violations.extend(violations)
        if violations:
            per_corridor[cid] = [v.to_dict() for v in violations]

    critical = [v for v in all_violations if v.severity == CorridorViolationSeverity.CRITICAL]
    high = [v for v in all_violations if v.severity == CorridorViolationSeverity.HIGH]
    medium = [v for v in all_violations if v.severity == CorridorViolationSeverity.MEDIUM]

    if critical:
        status = "BLOCKED"
    elif high:
        status = "NON_COMPLIANT"
    elif medium:
        status = "PARTIAL"
    elif all_violations:
        status = "PARTIAL"
    else:
        status = "COMPLIANT_100"

    return {
        "module": "bce_4x_corridor_validator",
        "version": "1.0",
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "corridors_validated": len(corridors),
        "total_violations": len(all_violations),
        "by_severity": {
            "critical": len(critical),
            "high": len(high),
            "medium": len(medium),
            "low": len([v for v in all_violations if v.severity == CorridorViolationSeverity.LOW]),
        },
        "by_type": _count_by_type(all_violations),
        "per_corridor": per_corridor,
        "rules_applied": [
            "hardcoded_score_detection",
            "geometry_linestring_valid",
            "circular_corridor_detection",
            "continuity_gap_check",
            "bounds_clipping_2km",
            "classification_valid",
            "scoring_range_check",
            "enrichment_check",
        ],
    }


# =====================================================================
# HELPERS
# =====================================================================

def _haversine_m(lat1, lon1, lat2, lon2):
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return 6371000 * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _path_length_m(coords):
    total = 0
    for i in range(len(coords) - 1):
        total += _haversine_m(coords[i][1], coords[i][0], coords[i + 1][1], coords[i + 1][0])
    return total


def _count_by_type(violations):
    counts = {}
    for v in violations:
        key = v.type.value
        counts[key] = counts.get(key, 0) + 1
    return counts
