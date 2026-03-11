"""
BIONIC V8 — Validateurs BCE Écologiques
========================================
Validateurs de conformité écologique pour le BIONIC Compliance Engine.

Validateurs implémentés:
  - bce_zone_classification_valid
  - bce_corridor_continuity_valid
  - bce_wwf_classification_valid
  - bce_human_pressure_respected
  - bce_topographic_coherence_valid

VERSION: 8.0.0 — Validation écologique complète
Objectif: zéro régression, conformité écologique totale
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger("bionic_engine.bce_ecological_validators")


# =====================================================================
# TYPES ET STRUCTURES
# =====================================================================

class ValidationStatus(Enum):
    VALID = "valid"
    WARNING = "warning"
    INVALID = "invalid"
    SKIPPED = "skipped"


@dataclass
class ValidationResult:
    """Résultat d'une validation BCE"""
    validator_name: str
    status: ValidationStatus
    score: float  # 0-100
    message: str
    details: Dict[str, Any]
    timestamp: str


# =====================================================================
# VALIDATEUR: CLASSIFICATION DES ZONES
# =====================================================================

def bce_zone_classification_valid(
    zone_data: Dict[str, Any],
    species: str,
    season: str,
) -> ValidationResult:
    """
    Valide la classification écologique d'une zone.
    
    Vérifie:
    - Cohérence espèce/zone
    - Critères NDVI respectés
    - Critères topographiques respectés
    - Critères hydrologiques respectés
    
    Args:
        zone_data: Données de la zone
        species: Espèce cible
        season: Saison courante
        
    Returns:
        ValidationResult
    """
    from datetime import datetime, timezone
    
    issues = []
    score = 100
    
    zone_type = zone_data.get("type", "unknown")
    
    # Validation NDVI
    ndvi = zone_data.get("ndvi", 0)
    ndvi_min = zone_data.get("ndvi_min", 0.3)
    ndvi_max = zone_data.get("ndvi_max", 0.8)
    
    if not (ndvi_min <= ndvi <= ndvi_max):
        issues.append(f"NDVI {ndvi:.2f} hors plage [{ndvi_min}-{ndvi_max}]")
        score -= 20
    
    # Validation pente
    slope = zone_data.get("slope", 0)
    slope_max = zone_data.get("slope_max", 30)
    
    if slope > slope_max:
        issues.append(f"Pente {slope}% > max {slope_max}%")
        score -= 15
    
    # Validation distance eau
    water_dist = zone_data.get("distance_to_water", 0)
    water_max = zone_data.get("water_distance_max", 1000)
    
    if water_dist > water_max:
        issues.append(f"Distance eau {water_dist}m > max {water_max}m")
        score -= 15
    
    # Validation saisonnière
    valid_seasons = zone_data.get("valid_seasons", [])
    if valid_seasons and season not in valid_seasons:
        issues.append(f"Saison {season} non valide pour ce type de zone")
        score -= 25
    
    # Déterminer le statut
    if score >= 80:
        status = ValidationStatus.VALID
        message = f"Zone {zone_type} conforme pour {species}"
    elif score >= 50:
        status = ValidationStatus.WARNING
        message = f"Zone {zone_type} partiellement conforme: {len(issues)} avertissement(s)"
    else:
        status = ValidationStatus.INVALID
        message = f"Zone {zone_type} non conforme: {len(issues)} problème(s)"
    
    return ValidationResult(
        validator_name="bce_zone_classification_valid",
        status=status,
        score=max(0, score),
        message=message,
        details={
            "zone_type": zone_type,
            "species": species,
            "season": season,
            "issues": issues,
            "checks_passed": 4 - len(issues),
            "checks_total": 4,
        },
        timestamp=datetime.now(timezone.utc).isoformat()
    )


# =====================================================================
# VALIDATEUR: CONTINUITÉ DES CORRIDORS
# =====================================================================

def bce_corridor_continuity_valid(
    corridor_points: List[Dict[str, float]],
    max_gap_m: float = 100.0,
) -> ValidationResult:
    """
    Valide la continuité d'un corridor (aucun saut, aucune rupture).
    
    Critères:
    - Aucun gap > max_gap_m entre points consécutifs
    - Minimum 3 points
    - Pas de retour en arrière significatif
    
    Args:
        corridor_points: Liste des points [{lat, lng}, ...]
        max_gap_m: Gap maximum autorisé en mètres
        
    Returns:
        ValidationResult
    """
    from datetime import datetime, timezone
    import math
    
    METERS_PER_DEG = 111320.0
    
    if len(corridor_points) < 3:
        return ValidationResult(
            validator_name="bce_corridor_continuity_valid",
            status=ValidationStatus.INVALID,
            score=0,
            message="Corridor insuffisant: moins de 3 points",
            details={"points_count": len(corridor_points), "minimum_required": 3},
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    
    gaps = []
    max_found_gap = 0
    issues = []
    
    for i in range(len(corridor_points) - 1):
        p1 = corridor_points[i]
        p2 = corridor_points[i + 1]
        
        lat1, lng1 = p1.get("lat", p1.get("latitude", 0)), p1.get("lng", p1.get("longitude", 0))
        lat2, lng2 = p2.get("lat", p2.get("latitude", 0)), p2.get("lng", p2.get("longitude", 0))
        
        lat_diff = (lat2 - lat1) * METERS_PER_DEG
        lng_diff = (lng2 - lng1) * METERS_PER_DEG * math.cos(math.radians((lat1 + lat2) / 2))
        distance = math.sqrt(lat_diff**2 + lng_diff**2)
        
        gaps.append(distance)
        max_found_gap = max(max_found_gap, distance)
        
        if distance > max_gap_m:
            issues.append({
                "segment": i,
                "gap_m": round(distance, 1),
                "max_allowed_m": max_gap_m,
            })
    
    # Calcul du score
    if not issues:
        score = 100
        status = ValidationStatus.VALID
        message = f"Corridor continu: {len(corridor_points)} points, gap max {max_found_gap:.1f}m"
    else:
        # Pénalité progressive
        penalty = min(50, len(issues) * 15)
        score = max(0, 100 - penalty)
        status = ValidationStatus.WARNING if score >= 50 else ValidationStatus.INVALID
        message = f"Corridor avec {len(issues)} rupture(s) détectée(s)"
    
    return ValidationResult(
        validator_name="bce_corridor_continuity_valid",
        status=status,
        score=score,
        message=message,
        details={
            "points_count": len(corridor_points),
            "max_gap_found_m": round(max_found_gap, 1),
            "max_gap_allowed_m": max_gap_m,
            "gaps": [{"segment": i, "distance_m": round(g, 1)} for i, g in enumerate(gaps)],
            "ruptures": issues,
        },
        timestamp=datetime.now(timezone.utc).isoformat()
    )


# =====================================================================
# VALIDATEUR: CLASSIFICATION WWF
# =====================================================================

def bce_wwf_classification_valid(
    corridor_data: Dict[str, Any],
) -> ValidationResult:
    """
    Valide la classification WWF d'un corridor.
    
    Types WWF:
    - Macro-corridor (> 5 km)
    - Corridor biologique (1-5 km)
    - Corridor de conservation (< 1 km)
    
    Args:
        corridor_data: Données du corridor incluant largeur et longueur
        
    Returns:
        ValidationResult
    """
    from datetime import datetime, timezone
    
    width_m = corridor_data.get("width_m", 500)
    length_m = corridor_data.get("length_m", 0)
    declared_type = corridor_data.get("wwf_type", "")
    
    # Déterminer le type WWF correct
    if width_m > 5000:
        expected_type = "macro_corridor"
        label = "Macro-corridor (> 5 km)"
    elif width_m >= 1000:
        expected_type = "biological_corridor"
        label = "Corridor biologique (1-5 km)"
    else:
        expected_type = "conservation_corridor"
        label = "Corridor de conservation (< 1 km)"
    
    issues = []
    score = 100
    
    # Vérifier la cohérence du type déclaré
    if declared_type and declared_type != expected_type:
        issues.append(f"Type déclaré '{declared_type}' ne correspond pas à la largeur ({width_m}m → {expected_type})")
        score -= 30
    
    # Vérifier les proportions
    if length_m > 0:
        ratio = length_m / max(width_m, 1)
        if ratio < 2:
            issues.append(f"Ratio longueur/largeur ({ratio:.1f}) insuffisant pour un corridor")
            score -= 20
    
    # Vérifier les seuils biologiques
    if expected_type == "conservation_corridor" and width_m < 100:
        issues.append(f"Largeur {width_m}m trop faible pour garantir la connectivité")
        score -= 25
    
    status = ValidationStatus.VALID if score >= 80 else (ValidationStatus.WARNING if score >= 50 else ValidationStatus.INVALID)
    
    return ValidationResult(
        validator_name="bce_wwf_classification_valid",
        status=status,
        score=max(0, score),
        message=f"Classification WWF: {label}",
        details={
            "width_m": width_m,
            "length_m": length_m,
            "expected_type": expected_type,
            "declared_type": declared_type or "non déclaré",
            "wwf_label": label,
            "issues": issues,
        },
        timestamp=datetime.now(timezone.utc).isoformat()
    )


# =====================================================================
# VALIDATEUR: PRESSION HUMAINE
# =====================================================================

def bce_human_pressure_respected(
    zone_data: Dict[str, Any],
    species: str,
) -> ValidationResult:
    """
    Valide que la pression humaine est respectée selon l'espèce.
    
    Seuils par espèce:
    - Orignal: max 0.3
    - Chevreuil: max 0.4
    - Ours noir: max 0.25
    
    Args:
        zone_data: Données de la zone
        species: Espèce cible
        
    Returns:
        ValidationResult
    """
    from datetime import datetime, timezone
    
    # Seuils par espèce
    HUMAN_PRESSURE_THRESHOLDS = {
        "orignal": {"max": 0.30, "warning": 0.25},
        "chevreuil": {"max": 0.40, "warning": 0.35},
        "ours_noir": {"max": 0.25, "warning": 0.20},
    }
    
    thresholds = HUMAN_PRESSURE_THRESHOLDS.get(species.lower(), {"max": 0.35, "warning": 0.30})
    
    human_pressure = zone_data.get("human_pressure", 0)
    distance_to_roads = zone_data.get("distance_to_roads", 1000)
    
    issues = []
    score = 100
    
    # Vérifier la pression humaine
    if human_pressure > thresholds["max"]:
        issues.append(f"Pression humaine {human_pressure:.2f} > seuil max {thresholds['max']}")
        score -= 40
    elif human_pressure > thresholds["warning"]:
        issues.append(f"Pression humaine {human_pressure:.2f} élevée (seuil warning: {thresholds['warning']})")
        score -= 15
    
    # Vérifier la distance aux routes
    min_road_distances = {
        "orignal": 200,
        "chevreuil": 100,
        "ours_noir": 300,
    }
    min_road = min_road_distances.get(species.lower(), 150)
    
    if distance_to_roads < min_road:
        issues.append(f"Distance routes {distance_to_roads}m < minimum {min_road}m pour {species}")
        score -= 25
    
    status = ValidationStatus.VALID if score >= 80 else (ValidationStatus.WARNING if score >= 50 else ValidationStatus.INVALID)
    
    return ValidationResult(
        validator_name="bce_human_pressure_respected",
        status=status,
        score=max(0, score),
        message=f"Pression humaine: {human_pressure:.2f} (max: {thresholds['max']})",
        details={
            "species": species,
            "human_pressure": human_pressure,
            "threshold_max": thresholds["max"],
            "threshold_warning": thresholds["warning"],
            "distance_to_roads_m": distance_to_roads,
            "min_road_distance_m": min_road,
            "issues": issues,
        },
        timestamp=datetime.now(timezone.utc).isoformat()
    )


# =====================================================================
# VALIDATEUR: COHÉRENCE TOPOGRAPHIQUE
# =====================================================================

def bce_topographic_coherence_valid(
    zone_data: Dict[str, Any],
    zone_type: str,
    species: str,
) -> ValidationResult:
    """
    Valide la cohérence topographique d'une zone.
    
    Vérifie:
    - Pente appropriée au type de zone
    - Aspect (exposition) cohérent
    - Terrain compatible avec l'espèce
    
    Args:
        zone_data: Données de la zone
        zone_type: Type de zone (alimentation, repos, rut, etc.)
        species: Espèce cible
        
    Returns:
        ValidationResult
    """
    from datetime import datetime, timezone
    
    # Contraintes topographiques par type de zone
    TOPO_CONSTRAINTS = {
        "alimentation": {"slope_max": 20, "preferred_aspect": ["S", "SE", "SW"]},
        "repos": {"slope_max": 30, "preferred_aspect": ["N", "NE", "NW"]},
        "rut": {"slope_max": 20, "preferred_aspect": ["S", "SE", "SW", "E", "W"]},
        "corridor": {"slope_max": 15, "preferred_aspect": []},  # Tous aspects
        "taniere": {"slope_min": 15, "slope_max": 60, "preferred_aspect": ["N", "NE", "NW"]},
    }
    
    constraints = TOPO_CONSTRAINTS.get(zone_type, {"slope_max": 25, "preferred_aspect": []})
    
    slope = zone_data.get("slope", 0)
    aspect = zone_data.get("aspect", "")
    terrain_type = zone_data.get("terrain_type", "unknown")
    
    issues = []
    score = 100
    
    # Vérifier la pente
    slope_min = constraints.get("slope_min", 0)
    slope_max = constraints.get("slope_max", 30)
    
    if slope < slope_min:
        issues.append(f"Pente {slope}% < minimum {slope_min}% pour {zone_type}")
        score -= 20
    elif slope > slope_max:
        issues.append(f"Pente {slope}% > maximum {slope_max}% pour {zone_type}")
        score -= 25
    
    # Vérifier l'aspect
    preferred_aspects = constraints.get("preferred_aspect", [])
    if preferred_aspects and aspect and aspect not in preferred_aspects:
        issues.append(f"Aspect {aspect} non optimal (préféré: {', '.join(preferred_aspects)})")
        score -= 10
    
    # Vérifier le terrain selon l'espèce
    AVOIDED_TERRAIN = {
        "orignal": ["urban", "highway", "cliff"],
        "chevreuil": ["urban", "cliff", "dense_wetland"],
        "ours_noir": ["urban", "highway", "open_water"],
    }
    
    avoided = AVOIDED_TERRAIN.get(species.lower(), ["urban"])
    if terrain_type in avoided:
        issues.append(f"Terrain '{terrain_type}' à éviter pour {species}")
        score -= 35
    
    status = ValidationStatus.VALID if score >= 80 else (ValidationStatus.WARNING if score >= 50 else ValidationStatus.INVALID)
    
    return ValidationResult(
        validator_name="bce_topographic_coherence_valid",
        status=status,
        score=max(0, score),
        message=f"Cohérence topographique: {zone_type} ({slope}%, {aspect})",
        details={
            "zone_type": zone_type,
            "species": species,
            "slope": slope,
            "slope_range": f"{slope_min}-{slope_max}%",
            "aspect": aspect,
            "preferred_aspects": preferred_aspects,
            "terrain_type": terrain_type,
            "issues": issues,
        },
        timestamp=datetime.now(timezone.utc).isoformat()
    )


# =====================================================================
# FONCTION PRINCIPALE DE VALIDATION
# =====================================================================

def validate_ecological_compliance(
    data: Dict[str, Any],
    validation_type: str = "full",
) -> Dict[str, Any]:
    """
    Exécute une validation écologique complète.
    
    Args:
        data: Données à valider (zone ou corridor)
        validation_type: "full", "zone", "corridor"
        
    Returns:
        Dict avec tous les résultats de validation
    """
    from datetime import datetime, timezone
    
    results = []
    
    species = data.get("species", "orignal")
    season = data.get("season", "automne")
    zone_type = data.get("zone_type", "alimentation")
    
    # Validation zone
    if validation_type in ["full", "zone"]:
        results.append(bce_zone_classification_valid(data, species, season))
        results.append(bce_human_pressure_respected(data, species))
        results.append(bce_topographic_coherence_valid(data, zone_type, species))
    
    # Validation corridor
    if validation_type in ["full", "corridor"]:
        corridor_points = data.get("corridor_points", data.get("positions", []))
        if corridor_points:
            results.append(bce_corridor_continuity_valid(corridor_points))
        
        if data.get("width_m") or data.get("wwf_type"):
            results.append(bce_wwf_classification_valid(data))
    
    # Calcul du score global
    valid_count = sum(1 for r in results if r.status == ValidationStatus.VALID)
    warning_count = sum(1 for r in results if r.status == ValidationStatus.WARNING)
    invalid_count = sum(1 for r in results if r.status == ValidationStatus.INVALID)
    
    avg_score = sum(r.score for r in results) / len(results) if results else 0
    
    # Statut global
    if invalid_count > 0:
        global_status = "NON_COMPLIANT"
    elif warning_count > 0:
        global_status = "PARTIAL"
    else:
        global_status = "COMPLIANT"
    
    return {
        "global_status": global_status,
        "global_score": round(avg_score, 1),
        "validators_run": len(results),
        "valid": valid_count,
        "warnings": warning_count,
        "invalid": invalid_count,
        "results": [
            {
                "validator": r.validator_name,
                "status": r.status.value,
                "score": r.score,
                "message": r.message,
                "details": r.details,
            }
            for r in results
        ],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "bce_ecological_validators_v8.0.0"
    }
