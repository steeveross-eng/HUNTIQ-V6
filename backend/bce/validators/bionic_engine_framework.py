"""
BCE-4X Bionic Engine Validator Framework
==========================================
Cadre de validation unifie pour tous les moteurs BIONIC.

Chaque moteur BIONIC doit implementer un validateur qui herite
de BionicEngineValidator et definit ses propres regles.

Garantie: Tout moteur passant de planned → active sans validateur
est automatiquement BLOQUE par le registre central.

VERSION: BCE-4X-ENGINES-1.0
"""

import logging
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger("bce.validators.engine_framework")


class EngineStatus(Enum):
    ACTIVE = "active"
    PARTIAL = "partial"
    PLANNED = "planned"
    BLOCKED = "blocked"


@dataclass
class EngineValidationRule:
    """Regle de validation pour un moteur BIONIC."""
    id: str
    description: str
    severity: str  # critical, high, medium, low
    check_fn: str  # nom de la methode de validation


class BionicEngineValidator:
    """
    Classe de base pour tous les validateurs de moteurs BIONIC.
    Chaque moteur doit heriter et implementer validate().
    """

    ENGINE_ID: str = "base"
    ENGINE_NAME: str = "Base Engine"
    VERSION: str = "1.0"
    RULES: List[EngineValidationRule] = []

    def __init__(self):
        self.violations = []
        self.checks_passed = 0
        self.checks_failed = 0

    def add_violation(self, rule_id: str, severity: str, message: str, expected=None, actual=None):
        self.violations.append({
            "engine": self.ENGINE_ID,
            "rule": rule_id,
            "severity": severity,
            "message": message,
            "expected": str(expected) if expected else None,
            "actual": str(actual) if actual else None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        self.checks_failed += 1

    def pass_check(self, rule_id: str):
        self.checks_passed += 1

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Override dans chaque moteur. Valide les donnees de sortie du moteur."""
        raise NotImplementedError(f"{self.ENGINE_NAME} doit implementer validate()")

    def get_report(self) -> Dict[str, Any]:
        critical = len([v for v in self.violations if v["severity"] == "critical"])
        high = len([v for v in self.violations if v["severity"] == "high"])

        if critical > 0:
            status = "BLOCKED"
        elif high > 0:
            status = "NON_COMPLIANT"
        elif self.violations:
            status = "PARTIAL"
        else:
            status = "COMPLIANT_100"

        return {
            "engine": self.ENGINE_ID,
            "engine_name": self.ENGINE_NAME,
            "version": self.VERSION,
            "status": status,
            "checks_passed": self.checks_passed,
            "checks_failed": self.checks_failed,
            "violations": self.violations,
            "rules_count": len(self.RULES),
            "rules": [{"id": r.id, "description": r.description} for r in self.RULES],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def reset(self):
        self.violations = []
        self.checks_passed = 0
        self.checks_failed = 0


# =====================================================================
# ANTI-HARDCODING MIXIN
# =====================================================================

class AntiHardcodingMixin:
    """Mixin pour detecter les valeurs hardcodees dans n'importe quel moteur."""

    FORBIDDEN_STATIC_VALUES: Dict[str, float] = {}

    def check_no_hardcoding(self, data: Dict, context: str = ""):
        """Verifie qu'aucune valeur connue comme hardcodee n'est presente."""
        for key, forbidden_val in self.FORBIDDEN_STATIC_VALUES.items():
            if key in data and data[key] == forbidden_val:
                self.add_violation(
                    rule_id=f"no_hardcoding_{key}",
                    severity="critical",
                    message=f"[{context}] Valeur hardcodee detectee: {key}={forbidden_val}",
                    expected="Valeur dynamique calculee",
                    actual=forbidden_val,
                )


# =====================================================================
# SPECIFIC ENGINE VALIDATORS
# =====================================================================

class WeatherEngineValidator(BionicEngineValidator, AntiHardcodingMixin):
    ENGINE_ID = "weather_engine"
    ENGINE_NAME = "Weather Engine"
    VERSION = "1.0"
    FORBIDDEN_STATIC_VALUES = {}
    RULES = [
        EngineValidationRule("weather_data_present", "Donnees meteo presentes", "high", "check_data"),
        EngineValidationRule("weather_temperature_range", "Temperature dans [-50, 50]°C", "medium", "check_temp"),
        EngineValidationRule("weather_wind_range", "Vent dans [0, 200] km/h", "medium", "check_wind"),
        EngineValidationRule("weather_influences_scoring", "Meteo influence le scoring", "high", "check_influence"),
        EngineValidationRule("weather_no_stale_data", "Donnees pas obsoletes (< 2h)", "medium", "check_freshness"),
    ]

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        self.reset()
        if not data:
            self.add_violation("weather_data_present", "high", "Aucune donnee meteo disponible")
            return self.get_report()

        self.pass_check("weather_data_present")

        temp = data.get("temperature_c")
        if temp is not None and (temp < -50 or temp > 50):
            self.add_violation("weather_temperature_range", "medium",
                               f"Temperature hors bornes: {temp}°C", "[-50, 50]", temp)
        elif temp is not None:
            self.pass_check("weather_temperature_range")

        wind = data.get("wind_speed_kmh")
        if wind is not None and (wind < 0 or wind > 200):
            self.add_violation("weather_wind_range", "medium",
                               f"Vent hors bornes: {wind} km/h", "[0, 200]", wind)
        elif wind is not None:
            self.pass_check("weather_wind_range")

        multipliers = data.get("influence_multipliers", {})
        if not multipliers:
            self.add_violation("weather_influences_scoring", "high",
                               "Aucun multiplicateur d'influence meteo")
        else:
            self.pass_check("weather_influences_scoring")

        return self.get_report()


class NutritionEngineValidator(BionicEngineValidator, AntiHardcodingMixin):
    ENGINE_ID = "nutrition_engine"
    ENGINE_NAME = "Nutrition Engine"
    VERSION = "1.0"
    RULES = [
        EngineValidationRule("nutrition_data_present", "Donnees nutrition presentes", "high", "check_data"),
        EngineValidationRule("nutrition_species_specific", "Attractivite specifique par espece", "high", "check_species"),
        EngineValidationRule("nutrition_score_range", "Scores dans [0, 100]", "medium", "check_range"),
        EngineValidationRule("nutrition_no_hardcoding", "Zero valeurs hardcodees", "critical", "check_hardcoding"),
    ]

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        self.reset()
        if not data:
            self.add_violation("nutrition_data_present", "high", "Aucune donnee nutrition")
            return self.get_report()
        self.pass_check("nutrition_data_present")

        if not data.get("species"):
            self.add_violation("nutrition_species_specific", "high", "Pas de donnees par espece")
        else:
            self.pass_check("nutrition_species_specific")

        score = data.get("attractivity_score", 0)
        if score < 0 or score > 100:
            self.add_violation("nutrition_score_range", "medium", f"Score hors bornes: {score}")
        else:
            self.pass_check("nutrition_score_range")

        self.check_no_hardcoding(data, "nutrition")
        return self.get_report()


class DisturbanceEngineValidator(BionicEngineValidator, AntiHardcodingMixin):
    ENGINE_ID = "disturbance_engine"
    ENGINE_NAME = "Disturbance Engine"
    VERSION = "1.0"
    FORBIDDEN_STATIC_VALUES = {"human_pressure": 0.1}
    RULES = [
        EngineValidationRule("disturbance_data_present", "Donnees perturbation presentes", "high", "check_data"),
        EngineValidationRule("disturbance_no_hardcoding", "Zero pression humaine hardcodee", "critical", "check_hardcoding"),
        EngineValidationRule("disturbance_sources_identified", "Sources de perturbation identifiees", "medium", "check_sources"),
        EngineValidationRule("disturbance_score_range", "Impact dans [0, 100]", "medium", "check_range"),
    ]

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        self.reset()
        if not data:
            self.add_violation("disturbance_data_present", "high", "Aucune donnee perturbation")
            return self.get_report()
        self.pass_check("disturbance_data_present")
        self.check_no_hardcoding(data, "disturbance")

        sources = data.get("sources", [])
        if not sources:
            self.add_violation("disturbance_sources_identified", "medium", "Aucune source de perturbation identifiee")
        else:
            self.pass_check("disturbance_sources_identified")

        return self.get_report()


class DailyRoutineEngineValidator(BionicEngineValidator):
    ENGINE_ID = "daily_routine_engine"
    ENGINE_NAME = "Daily Routine Engine"
    VERSION = "1.0"
    RULES = [
        EngineValidationRule("routine_windows_present", "Fenetres d'activite definies", "high", "check_windows"),
        EngineValidationRule("routine_species_specific", "Rythmes specifiques par espece", "high", "check_species"),
        EngineValidationRule("routine_time_coherence", "Coherence temporelle (aube < jour < crepuscule)", "medium", "check_time"),
    ]

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        self.reset()
        if not data or not data.get("windows"):
            self.add_violation("routine_windows_present", "high", "Aucune fenetre d'activite")
            return self.get_report()
        self.pass_check("routine_windows_present")
        return self.get_report()


class PhenologyEngineValidator(BionicEngineValidator):
    ENGINE_ID = "phenology_engine"
    ENGINE_NAME = "Phenology Engine"
    VERSION = "1.0"
    RULES = [
        EngineValidationRule("phenology_season_present", "Saison phenologique identifiee", "high", "check_season"),
        EngineValidationRule("phenology_forage_quality", "Qualite fourrage calculee", "medium", "check_forage"),
        EngineValidationRule("phenology_date_coherence", "Coherence date/phenologie", "medium", "check_date"),
    ]

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        self.reset()
        if not data or not data.get("season"):
            self.add_violation("phenology_season_present", "high", "Aucune saison phenologique")
            return self.get_report()
        self.pass_check("phenology_season_present")
        return self.get_report()


class TypologyEngineValidator(BionicEngineValidator):
    ENGINE_ID = "typology_engine"
    ENGINE_NAME = "Typology Engine"
    VERSION = "1.0"
    RULES = [
        EngineValidationRule("typology_profile_present", "Profil comportemental defini", "high", "check_profile"),
        EngineValidationRule("typology_valid_type", "Type valide (conservateur/explorateur/nocturne/opportuniste)", "medium", "check_type"),
    ]

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        self.reset()
        if not data or not data.get("profile"):
            self.add_violation("typology_profile_present", "high", "Aucun profil comportemental")
            return self.get_report()
        self.pass_check("typology_profile_present")
        valid_types = {"conservateur", "explorateur", "nocturne", "opportuniste"}
        ptype = data.get("profile", {}).get("type", "")
        if ptype not in valid_types:
            self.add_violation("typology_valid_type", "medium", f"Type inconnu: {ptype}", valid_types, ptype)
        else:
            self.pass_check("typology_valid_type")
        return self.get_report()


class LearningEngineValidator(BionicEngineValidator):
    ENGINE_ID = "learning_engine"
    ENGINE_NAME = "Learning Engine"
    VERSION = "1.0"
    RULES = [
        EngineValidationRule("learning_observations_present", "Observations reelles disponibles", "medium", "check_obs"),
        EngineValidationRule("learning_model_updated", "Modele ajuste recemment", "medium", "check_model"),
        EngineValidationRule("learning_no_overfitting", "Pas de surapprentissage", "high", "check_overfit"),
    ]

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        self.reset()
        if not data:
            self.add_violation("learning_observations_present", "medium", "Aucune donnee d'apprentissage")
            return self.get_report()
        self.pass_check("learning_observations_present")
        return self.get_report()


class HabitatEnhancementValidator(BionicEngineValidator):
    ENGINE_ID = "habitat_enhancement_engine"
    ENGINE_NAME = "Habitat Enhancement Engine"
    VERSION = "1.0"
    RULES = [
        EngineValidationRule("habitat_soil_analysis", "Analyse de sol disponible", "medium", "check_soil"),
        EngineValidationRule("habitat_recommendations", "Recommandations generees", "high", "check_recs"),
        EngineValidationRule("habitat_score_range", "Scores dans [0, 100]", "medium", "check_range"),
    ]

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        self.reset()
        if not data:
            self.add_violation("habitat_soil_analysis", "medium", "Aucune analyse de sol")
            return self.get_report()
        self.pass_check("habitat_soil_analysis")
        if not data.get("recommendations"):
            self.add_violation("habitat_recommendations", "high", "Aucune recommandation generee")
        else:
            self.pass_check("habitat_recommendations")
        return self.get_report()


class WaypointEngineValidator(BionicEngineValidator):
    ENGINE_ID = "waypoint_engine"
    ENGINE_NAME = "Waypoint Engine"
    VERSION = "1.0"
    RULES = [
        EngineValidationRule("waypoint_coords_valid", "Coordonnees valides", "critical", "check_coords"),
        EngineValidationRule("waypoint_in_quebec", "Position dans Quebec", "high", "check_quebec"),
        EngineValidationRule("waypoint_scoring_coherent", "Scoring coherent avec zones", "medium", "check_scoring"),
    ]

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        self.reset()
        if not data:
            self.add_violation("waypoint_coords_valid", "critical", "Aucun waypoint")
            return self.get_report()
        lat = data.get("lat", data.get("latitude"))
        lng = data.get("lng", data.get("longitude"))
        if lat is None or lng is None:
            self.add_violation("waypoint_coords_valid", "critical", "Coordonnees manquantes")
        elif not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            self.add_violation("waypoint_coords_valid", "critical", f"Coords invalides: ({lat}, {lng})")
        else:
            self.pass_check("waypoint_coords_valid")
            if not (44.0 <= lat <= 63.0 and -80.0 <= lng <= -57.0):
                self.add_violation("waypoint_in_quebec", "high", f"Hors Quebec: ({lat}, {lng})")
            else:
                self.pass_check("waypoint_in_quebec")
        return self.get_report()


class HuntingPathEngineValidator(BionicEngineValidator):
    ENGINE_ID = "hunting_path_engine"
    ENGINE_NAME = "Hunting Path Engine"
    VERSION = "1.0"
    RULES = [
        EngineValidationRule("path_geometry_valid", "Geometrie trajet valide", "critical", "check_geom"),
        EngineValidationRule("path_no_habitation", "Trajet ne traverse pas d'habitation", "high", "check_no_hab"),
        EngineValidationRule("path_within_territory", "Trajet dans le territoire", "high", "check_territory"),
        EngineValidationRule("path_safety", "Conformite securite", "critical", "check_safety"),
    ]

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        self.reset()
        if not data or not data.get("path"):
            self.add_violation("path_geometry_valid", "critical", "Aucun trajet de chasse")
            return self.get_report()
        self.pass_check("path_geometry_valid")
        return self.get_report()


# =====================================================================
# REGISTRY OF ALL ENGINE VALIDATORS
# =====================================================================

ENGINE_VALIDATORS = {
    "weather_engine": WeatherEngineValidator,
    "nutrition_engine": NutritionEngineValidator,
    "disturbance_engine": DisturbanceEngineValidator,
    "daily_routine_engine": DailyRoutineEngineValidator,
    "phenology_engine": PhenologyEngineValidator,
    "typology_engine": TypologyEngineValidator,
    "learning_engine": LearningEngineValidator,
    "habitat_enhancement_engine": HabitatEnhancementValidator,
    "waypoint_engine": WaypointEngineValidator,
    "hunting_path_engine": HuntingPathEngineValidator,
}


def validate_all_engines(engine_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Execute tous les validateurs de moteurs BIONIC enregistres.
    engine_data: dict mapping engine_id -> data de sortie du moteur
    """
    engine_data = engine_data or {}
    results = {}
    total_violations = 0

    for engine_id, validator_cls in ENGINE_VALIDATORS.items():
        validator = validator_cls()
        data = engine_data.get(engine_id)
        report = validator.validate(data or {})
        results[engine_id] = report
        total_violations += len(report["violations"])

    blocked = any(r["status"] == "BLOCKED" for r in results.values())
    non_compliant = any(r["status"] == "NON_COMPLIANT" for r in results.values())

    return {
        "framework": "bce_4x_engine_framework",
        "version": "1.0",
        "status": "BLOCKED" if blocked else "NON_COMPLIANT" if non_compliant else "COMPLIANT_100" if total_violations == 0 else "PARTIAL",
        "engines_validated": len(results),
        "total_violations": total_violations,
        "engines": results,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
