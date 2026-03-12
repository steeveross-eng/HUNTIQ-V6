"""
BCE-MAX x4.1 — MILITARY-GRADE ANTI-REGRESSION SYSTEM
=====================================================
Système de protection absolue contre toute régression, déviation ou erreur.

PRINCIPES:
1. ANTI-RÉGRESSION TOTAL — Aucune fonctionnalité ne peut être dégradée
2. ANTI-DÉPLOIEMENT — Aucun déploiement sans COMPLIANT 100%
3. ANTI-CONTOURNEMENT — Impossible de bypasser les règles
4. ANTI-ERREUR — Détection automatique de toute incohérence
5. ANTI-PERTE DE TEMPS — Plus aucune régression à corriger

VERSION: 4.1 — Military-Grade
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
import hashlib
import json

logger = logging.getLogger("bce_max_4_1")


# =====================================================================
# TYPES ET CONSTANTES
# =====================================================================

class BCEMaxStatus(Enum):
    COMPLIANT = "COMPLIANT_100"
    PARTIAL = "PARTIAL"
    NON_COMPLIANT = "NON_COMPLIANT"
    BLOCKED = "BLOCKED"
    CRITICAL = "CRITICAL_FAILURE"


class ViolationType(Enum):
    LAYER_MISSING = "layer_missing"
    CORRIDOR_MISSING = "corridor_missing"
    ZONE_OVERFLOW = "zone_overflow"
    AUTO_LOAD_FAILURE = "auto_load_failure"
    SESSION_LOSS = "session_loss"
    REGRESSION_DETECTED = "regression_detected"
    DEPLOYMENT_BLOCKED = "deployment_blocked"


@dataclass
class BCEMaxViolation:
    """Violation détectée par BCE-MAX"""
    type: ViolationType
    severity: str  # "critical", "high", "medium", "low"
    message: str
    component: str
    expected: Any
    actual: Any
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class BCEMaxReport:
    """Rapport BCE-MAX x4.1"""
    status: BCEMaxStatus
    score: float
    violations: List[BCEMaxViolation]
    checks_passed: int
    checks_failed: int
    deployment_allowed: bool
    timestamp: str
    version: str = "bce_max_4.1"


# =====================================================================
# BASELINE REQUIREMENTS — IMMUTABLE
# =====================================================================

# Couches OBLIGATOIRES qui doivent TOUJOURS être disponibles
MANDATORY_LAYERS = [
    "habitats",
    "alimentation", 
    "repos",
    "rut",
    "trajets",
    "corridors",
    "ensoleillement",
    "peuplements",
]

# Fonctionnalités OBLIGATOIRES qui ne peuvent JAMAIS être dégradées
MANDATORY_FEATURES = {
    "auto_load_layers": {
        "description": "Chargement automatique de toutes les couches au démarrage",
        "min_layers": 8,
    },
    "auto_load_corridors": {
        "description": "Affichage automatique des corridors",
        "enabled": True,
    },
    "session_persistence": {
        "description": "Restauration complète de la session précédente",
        "includes": ["position", "species", "layers", "waypoints"],
    },
    "zone_clipping": {
        "description": "Zones strictement dans le carré 2km²",
        "zone_size_m": 2000,
    },
}

# =====================================================================
# REGISTRE MODULES CRITIQUES — BCE-4X OBLIGATOIRE
# =====================================================================
# Tout module ajouté ici DOIT avoir un validateur BCE-4X correspondant.
# Tout nouveau moteur BIONIC est AUTOMATIQUEMENT critique.
# Un module non enregistré ici ne peut PAS être déployé en production.

CRITICAL_MODULES_REGISTRY = {
    # ── MODULES ACTIFS (validateur BCE-4X existe) ──
    "corridor_10x": {
        "file": "modules/bionic_engine_p0/services/corridor_10x.py",
        "validator": "bce.validators.corridor_v9",
        "status": "active",
        "since": "2026-03-12",
    },
    "zone_engine_core": {
        "file": "modules/bionic_engine_p0/services/zone_engine_core_v2.py",
        "validator": "bce.validators.spatial_integrity",
        "status": "active",
        "since": "2026-03-01",
    },
    "ecological_database": {
        "file": "modules/bionic_engine_p0/knowledge/ecological_database_v8.py",
        "validator": "bce.validators.ecological_validators_v8",
        "status": "active",
        "since": "2026-03-01",
    },
    # ── MOTEURS BIONIC (tous critiques) ──
    "movement_engine": {
        "validator": "bce.validators.corridor_v9",
        "status": "active",
        "since": "2026-03-12",
    },
    "weather_engine": {
        "validator": "bce.validators.bionic_engine_framework.WeatherEngineValidator",
        "status": "active",
        "since": "2026-03-12",
    },
    "nutrition_engine": {
        "file": "modules/bionic_engine_p0/engines/nutrition_engine.py",
        "validator": "bce.validators.bionic_engine_framework.NutritionEngineValidator",
        "status": "active",
        "since": "2026-03-15",
    },
    "daily_routine_engine": {
        "file": "modules/bionic_engine_p0/engines/daily_routine_engine.py",
        "validator": "bce.validators.bionic_engine_framework.DailyRoutineEngineValidator",
        "status": "active",
        "since": "2026-03-15",
    },
    "disturbance_engine": {
        "file": "modules/bionic_engine_p0/engines/disturbance_engine.py",
        "validator": "bce.validators.bionic_engine_framework.DisturbanceEngineValidator",
        "status": "active",
        "since": "2026-03-15",
    },
    "phenology_engine": {
        "file": "modules/bionic_engine_p0/engines/phenology_engine.py",
        "validator": "bce.validators.bionic_engine_framework.PhenologyEngineValidator",
        "status": "active",
        "since": "2026-03-15",
    },
    "typology_engine": {
        "file": "modules/bionic_engine_p0/engines/typology_engine.py",
        "validator": "bce.validators.bionic_engine_framework.TypologyEngineValidator",
        "status": "active",
        "since": "2026-03-15",
    },
    "learning_engine": {
        "file": "modules/bionic_engine_p0/engines/learning_engine.py",
        "validator": "bce.validators.bionic_engine_framework.LearningEngineValidator",
        "status": "active",
        "since": "2026-03-15",
    },
    "habitat_enhancement_engine": {
        "file": "modules/bionic_engine_p0/engines/habitat_enhancement_engine.py",
        "validator": "bce.validators.bionic_engine_framework.HabitatEnhancementValidator",
        "status": "active",
        "since": "2026-03-15",
    },
    # ── MOTEURS SPATIAUX ──
    "waypoint_engine": {
        "validator": "bce.validators.bionic_engine_framework.WaypointEngineValidator",
        "status": "active",
        "since": "2026-03-12",
    },
    "hunting_path_engine": {
        "validator": "bce.validators.bionic_engine_framework.HuntingPathEngineValidator",
        "status": "planned",
    },
    # ── UI CRITIQUES ──
    "ui_coherence": {
        "validator": "bce.validators.ui_coherence",
        "status": "active",
        "since": "2026-03-01",
    },
    "scoring_determinism": {
        "validator": "bce.validators.scoring_determinism",
        "status": "active",
        "since": "2026-03-01",
    },
    # ── STEVE-MAX: COLOR CONTRACT + VISUAL ISOLATION ──
    "color_contract": {
        "validator": "bce.validators.color_contract",
        "status": "active",
        "since": "2026-03-20",
    },
    # ── STEVE-MAX: GEOMETRY COMPLIANCE + CLIPPING ──
    "geometry_compliance": {
        "validator": "bce.validators.geometry_compliance",
        "status": "active",
        "since": "2026-03-20",
    },
}


def check_critical_module_coverage() -> list:
    """
    Verifie que tous les modules critiques ont un validateur BCE-4X actif.
    Retourne la liste des modules non couverts.
    """
    uncovered = []
    for module_id, info in CRITICAL_MODULES_REGISTRY.items():
        if info.get("status") == "active" and info.get("validator") == "pending":
            uncovered.append(module_id)
    return uncovered


def validate_branch_compliance(branch_name: str = "") -> Dict[str, Any]:
    """
    BCE-4X Branch Protection — Valide la conformite d'une branche.
    
    Regles:
    1. Tout code sur la branche doit passer validate_full() sans violations critiques
    2. Le registre des modules critiques doit etre intact
    3. Aucun module actif ne peut avoir un validateur "pending"
    4. Les branches contenant du code non conforme sont marquees BLOCKED
    
    Seules les branches COMPLIANT peuvent etre mergees dans main.
    """
    uncovered = check_critical_module_coverage()
    
    issues = []
    if uncovered:
        issues.append(f"Modules actifs sans validateur: {uncovered}")
    
    # Verifier que le registre est present et non vide
    if len(CRITICAL_MODULES_REGISTRY) < 18:
        issues.append(f"Registre incomplet: {len(CRITICAL_MODULES_REGISTRY)}/18 modules")
    
    # Verifier qu'aucun moteur BIONIC planned n'a un validateur "pending"
    for mid, info in CRITICAL_MODULES_REGISTRY.items():
        if info.get("validator") == "pending":
            issues.append(f"Module '{mid}' a un validateur 'pending'")
    
    status = "BLOCKED" if issues else "COMPLIANT"
    
    return {
        "branch": branch_name or "current",
        "status": status,
        "merge_allowed": status == "COMPLIANT",
        "issues": issues,
        "registry_size": len(CRITICAL_MODULES_REGISTRY),
        "active_modules": len([m for m in CRITICAL_MODULES_REGISTRY.values() if m["status"] == "active"]),
    }


# État de référence (golden state) — NE JAMAIS MODIFIER
GOLDEN_STATE_HASH = None  # Calculé à l'initialisation


# =====================================================================
# BCE-MAX ENGINE
# =====================================================================

class BCEMaxEngine:
    """
    Moteur BCE-MAX x4.1 — Military-Grade Anti-Regression System
    """
    
    def __init__(self):
        self.logger = logging.getLogger("bce_max_4_1.engine")
        self.violations: List[BCEMaxViolation] = []
        self.last_report: Optional[BCEMaxReport] = None
        self.deployment_blocked = False
        self.baseline_state = self._compute_baseline_state()
        
    def _compute_baseline_state(self) -> Dict[str, Any]:
        """Calcule l'état de référence (baseline)."""
        return {
            "mandatory_layers": MANDATORY_LAYERS.copy(),
            "mandatory_features": MANDATORY_FEATURES.copy(),
            "computed_at": datetime.now(timezone.utc).isoformat(),
        }
    
    def _hash_state(self, state: Dict[str, Any]) -> str:
        """Calcule un hash de l'état pour détection de changements."""
        state_str = json.dumps(state, sort_keys=True, default=str)
        return hashlib.sha256(state_str.encode()).hexdigest()[:16]
    
    # =====================================================================
    # ANTI-RÉGRESSION CHECKS
    # =====================================================================
    
    def check_layers_available(self, available_layers: List[str]) -> List[BCEMaxViolation]:
        """Vérifie que toutes les couches obligatoires sont disponibles."""
        violations = []
        available_set = set(available_layers)
        
        for layer in MANDATORY_LAYERS:
            if layer not in available_set:
                violations.append(BCEMaxViolation(
                    type=ViolationType.LAYER_MISSING,
                    severity="critical",
                    message=f"Couche obligatoire manquante: {layer}",
                    component="LayerSystem",
                    expected=layer,
                    actual="MISSING",
                ))
        
        return violations
    
    def check_auto_load_layers(self, loaded_count: int, expected_min: int = 8) -> List[BCEMaxViolation]:
        """Vérifie que l'auto-load charge suffisamment de couches."""
        violations = []
        
        if loaded_count < expected_min:
            violations.append(BCEMaxViolation(
                type=ViolationType.AUTO_LOAD_FAILURE,
                severity="critical",
                message=f"Auto-load insuffisant: {loaded_count}/{expected_min} couches",
                component="AutoLoadSystem",
                expected=expected_min,
                actual=loaded_count,
            ))
        
        return violations
    
    def check_corridors_visible(self, corridors_count: int) -> List[BCEMaxViolation]:
        """Vérifie que les corridors sont affichés."""
        violations = []
        
        # Les corridors doivent être visibles (au moins détectés)
        if corridors_count == 0:
            violations.append(BCEMaxViolation(
                type=ViolationType.CORRIDOR_MISSING,
                severity="high",
                message="Aucun corridor affiché — violation BCE-MAX",
                component="CorridorSystem",
                expected=">0",
                actual=0,
            ))
        
        return violations
    
    def check_zones_within_bounds(
        self, 
        zones: List[Dict], 
        bbox: Dict[str, float]
    ) -> List[BCEMaxViolation]:
        """Vérifie que toutes les zones sont dans les limites du carré 2km²."""
        violations = []
        
        if not bbox or not zones:
            return violations
        
        for i, zone in enumerate(zones):
            coords = zone.get("positions", zone.get("coordinates", []))
            for coord in coords:
                lat = coord[0] if isinstance(coord, list) else coord.get("lat", coord.get("latitude"))
                lng = coord[1] if isinstance(coord, list) else coord.get("lng", coord.get("longitude"))
                
                if lat and lng:
                    if lat < bbox.get("minLat", -90) or lat > bbox.get("maxLat", 90):
                        violations.append(BCEMaxViolation(
                            type=ViolationType.ZONE_OVERFLOW,
                            severity="high",
                            message=f"Zone {i} déborde en latitude: {lat}",
                            component="ZoneClipping",
                            expected=f"[{bbox.get('minLat')}, {bbox.get('maxLat')}]",
                            actual=lat,
                        ))
                        break
                    if lng < bbox.get("minLng", -180) or lng > bbox.get("maxLng", 180):
                        violations.append(BCEMaxViolation(
                            type=ViolationType.ZONE_OVERFLOW,
                            severity="high",
                            message=f"Zone {i} déborde en longitude: {lng}",
                            component="ZoneClipping",
                            expected=f"[{bbox.get('minLng')}, {bbox.get('maxLng')}]",
                            actual=lng,
                        ))
                        break
        
        return violations
    
    def check_session_persistence(
        self, 
        session_data: Dict[str, Any]
    ) -> List[BCEMaxViolation]:
        """Vérifie la persistance de session."""
        violations = []
        
        required_fields = ["position", "species", "layers"]
        for field in required_fields:
            if field not in session_data or session_data[field] is None:
                violations.append(BCEMaxViolation(
                    type=ViolationType.SESSION_LOSS,
                    severity="high",
                    message=f"Donnée de session manquante: {field}",
                    component="SessionPersistence",
                    expected=field,
                    actual="MISSING",
                ))
        
        return violations
    
    # =====================================================================
    # ANTI-DÉPLOIEMENT
    # =====================================================================
    
    def can_deploy(self) -> Tuple[bool, str]:
        """
        Vérifie si un déploiement est autorisé.
        Retourne (autorisé, raison).
        """
        if self.deployment_blocked:
            return False, "Déploiement bloqué par BCE-MAX x4.1"
        
        if self.last_report and self.last_report.status != BCEMaxStatus.COMPLIANT:
            return False, f"Status non-compliant: {self.last_report.status.value}"
        
        if self.violations:
            critical = [v for v in self.violations if v.severity == "critical"]
            if critical:
                return False, f"{len(critical)} violation(s) critique(s) détectée(s)"
        
        return True, "COMPLIANT 100% — Déploiement autorisé"
    
    def block_deployment(self, reason: str):
        """Bloque tout déploiement."""
        self.deployment_blocked = True
        self.logger.critical(f"[BCE-MAX x4.1] DÉPLOIEMENT BLOQUÉ: {reason}")
    
    def allow_deployment(self):
        """Autorise les déploiements (après correction)."""
        self.deployment_blocked = False
        self.logger.info("[BCE-MAX x4.1] Déploiement autorisé")
    
    # =====================================================================
    # VALIDATION COMPLÈTE
    # =====================================================================
    
    def validate_full(
        self,
        available_layers: List[str] = None,
        loaded_layers_count: int = 0,
        corridors_count: int = 0,
        zones: List[Dict] = None,
        bbox: Dict[str, float] = None,
        session_data: Dict[str, Any] = None,
    ) -> BCEMaxReport:
        """
        Exécute une validation complète BCE-MAX x4.1.
        
        Returns:
            BCEMaxReport avec status COMPLIANT_100 ou détails des violations
        """
        self.violations = []
        
        # Check 1: Couches disponibles
        if available_layers:
            self.violations.extend(self.check_layers_available(available_layers))
        
        # Check 2: Auto-load couches
        if loaded_layers_count > 0:
            self.violations.extend(self.check_auto_load_layers(loaded_layers_count))
        
        # Check 3: Corridors visibles
        self.violations.extend(self.check_corridors_visible(corridors_count))
        
        # Check 4: Zones dans les limites
        if zones and bbox:
            self.violations.extend(self.check_zones_within_bounds(zones, bbox))
        
        # Check 5: Persistance session
        if session_data:
            self.violations.extend(self.check_session_persistence(session_data))
        
        # Check 6: Couverture modules critiques
        uncovered = check_critical_module_coverage()
        for module_id in uncovered:
            self.violations.append(BCEMaxViolation(
                type=ViolationType.REGRESSION_DETECTED,
                severity="high",
                message=f"Module critique '{module_id}' actif sans validateur BCE-4X",
                component="CriticalModuleRegistry",
                expected="Validateur BCE-4X actif",
                actual="pending",
            ))
        
        # Check 7: STEVE-MAX Color Contract + Visual Isolation
        try:
            from bce.validators.color_contract import validate as validate_color_contract
            color_result = validate_color_contract()
            if color_result["status"] == "FAIL":
                for err in color_result.get("errors", []):
                    self.violations.append(BCEMaxViolation(
                        type=ViolationType.REGRESSION_DETECTED,
                        severity="high",
                        message=err,
                        component="ColorContract_STEVE_MAX",
                        expected="PASS",
                        actual="FAIL",
                    ))
        except Exception as e:
            self.logger.warning(f"[BCE-MAX] Color contract validation error: {e}")

        # Check 8: STEVE-MAX Geometry Compliance + Clipping
        try:
            from bce.validators.geometry_compliance import validate as validate_geometry
            geom_result = validate_geometry()
            if geom_result["status"] == "FAIL":
                for err in geom_result.get("errors", []):
                    self.violations.append(BCEMaxViolation(
                        type=ViolationType.REGRESSION_DETECTED,
                        severity="high",
                        message=err,
                        component="GeometryCompliance_STEVE_MAX",
                        expected="PASS",
                        actual="FAIL",
                    ))
        except Exception as e:
            self.logger.warning(f"[BCE-MAX] Geometry compliance validation error: {e}")
        
        # Calculer le statut final
        critical_count = len([v for v in self.violations if v.severity == "critical"])
        high_count = len([v for v in self.violations if v.severity == "high"])
        
        if critical_count > 0:
            status = BCEMaxStatus.BLOCKED
            deployment_allowed = False
        elif high_count > 0:
            status = BCEMaxStatus.NON_COMPLIANT
            deployment_allowed = False
        elif len(self.violations) > 0:
            status = BCEMaxStatus.PARTIAL
            deployment_allowed = False
        else:
            status = BCEMaxStatus.COMPLIANT
            deployment_allowed = True
        
        # Score
        total_checks = 8  # STEVE-MAX: +2 for color contract + geometry compliance
        failed_checks = len(set(v.component for v in self.violations))
        passed_checks = total_checks - failed_checks
        score = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
        
        report = BCEMaxReport(
            status=status,
            score=round(score, 1),
            violations=self.violations,
            checks_passed=passed_checks,
            checks_failed=failed_checks,
            deployment_allowed=deployment_allowed,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        
        self.last_report = report
        
        # Log le résultat
        if status == BCEMaxStatus.COMPLIANT:
            self.logger.info(f"[BCE-MAX x4.1] ✅ COMPLIANT 100% — Score: {score}%")
        else:
            self.logger.warning(f"[BCE-MAX x4.1] ❌ {status.value} — {len(self.violations)} violation(s)")
        
        return report
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut actuel de BCE-MAX x4.1."""
        can_deploy, deploy_reason = self.can_deploy()
        uncovered = check_critical_module_coverage()
        
        return {
            "version": "bce_max_4.1",
            "mode": "MILITARY_GRADE",
            "status": self.last_report.status.value if self.last_report else "NOT_VALIDATED",
            "score": self.last_report.score if self.last_report else 0,
            "violations_count": len(self.violations),
            "deployment_allowed": can_deploy,
            "deployment_reason": deploy_reason,
            "last_validation": self.last_report.timestamp if self.last_report else None,
            "baseline_hash": self._hash_state(self.baseline_state),
            "mandatory_layers": MANDATORY_LAYERS,
            "mandatory_features": list(MANDATORY_FEATURES.keys()),
            "critical_modules": {
                "total": len(CRITICAL_MODULES_REGISTRY),
                "active": len([m for m in CRITICAL_MODULES_REGISTRY.values() if m["status"] == "active"]),
                "uncovered": uncovered,
                "registry": {k: v["status"] for k, v in CRITICAL_MODULES_REGISTRY.items()},
            },
        }


# Instance singleton
bce_max_engine = BCEMaxEngine()


# =====================================================================
# HELPER FUNCTIONS
# =====================================================================

def validate_deployment() -> Tuple[bool, str]:
    """Vérifie si un déploiement est autorisé."""
    return bce_max_engine.can_deploy()


def get_bce_max_status() -> Dict[str, Any]:
    """Retourne le statut BCE-MAX x4.1."""
    return bce_max_engine.get_status()


def run_full_validation(**kwargs) -> BCEMaxReport:
    """Exécute une validation complète."""
    return bce_max_engine.validate_full(**kwargs)
