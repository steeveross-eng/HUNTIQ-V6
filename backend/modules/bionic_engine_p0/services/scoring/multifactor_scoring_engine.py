"""
BIONIC V5 — PHASE D: Multi-Factor Scoring Engine
===================================================
PHASE D.1 — Optimisation du scoring comportemental

Moteur de scoring multi-facteur qui combine les facteurs Phase B, C
et les registres spécialisés en un score composite normalisé.

RESPONSABILITÉ:
- Calculer des scores composites multi-facteurs
- Pondérer dynamiquement selon le contexte saisonnier
- Fournir des recommandations basées sur la combinaison de facteurs

INTÉGRATION:
- CalvingModelRegistry (C.1)
- JuvenileDispersalRegistry (C.2)
- ThermalStressRegistry (C.3)
- HuntingPressureRegistry (C.4)

VERSION: 1.0.0
Conformité: G-SEC | G-QA | G-DOC | BIONIC V5 PHASE D
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import date
from dataclasses import dataclass, field

from modules.bionic_engine_p0.knowledge.seasonal.calving_models import CalvingModelRegistry
from modules.bionic_engine_p0.knowledge.seasonal.juvenile_dispersion import JuvenileDispersalRegistry
from modules.bionic_engine_p0.knowledge.seasonal.thermal_stress import ThermalStressRegistry
from modules.bionic_engine_p0.knowledge.pressure.hunting_pressure import (
    HuntingPressureRegistry, PressureIntensity
)

logger = logging.getLogger("bionic_multifactor_scoring")


@dataclass
class MultiFactorScore:
    """Résultat d'un scoring multi-facteur PHASE D."""
    score: float = 0.0
    confidence: float = 0.0
    active_factors: int = 0
    total_factors: int = 8
    factors: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    risk_level: str = "normal"
    source_ids: List[str] = field(default_factory=lambda: ["SRC-PHASE-D-MULTIFACTOR"])
    version: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "score": round(self.score, 1),
            "confidence": round(self.confidence, 2),
            "active_factors": self.active_factors,
            "total_factors": self.total_factors,
            "factors": self.factors,
            "recommendations": self.recommendations,
            "risk_level": self.risk_level,
            "source_ids": self.source_ids,
            "version": self.version
        }


@dataclass
class DynamicWeight:
    """Pondération dynamique selon le contexte."""
    base_weight: float = 1.0
    seasonal_boost: float = 0.0
    context_boost: float = 0.0

    @property
    def effective(self) -> float:
        return self.base_weight + self.seasonal_boost + self.context_boost


class MultiFactorScoringEngine:
    """
    Moteur de scoring multi-facteur PHASE D.
    
    Combine tous les facteurs disponibles en un score composite
    avec pondération dynamique selon le contexte saisonnier.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._calving = CalvingModelRegistry()
        self._dispersal = JuvenileDispersalRegistry()
        self._thermal = ThermalStressRegistry()
        self._pressure = HuntingPressureRegistry()
        self._initialized = True
        logger.info("MultiFactorScoringEngine initialized (PHASE D)")

    def calculate_composite_score(
        self,
        species: str,
        region: str,
        check_date: date,
        hour: int = 12,
        temperature_c: Optional[float] = None,
        humidity: Optional[float] = None,
        hunting_detected: bool = False,
        extra_modifiers: Optional[Dict[str, float]] = None
    ) -> MultiFactorScore:
        """
        Calcule le score composite multi-facteur.

        Combine Phase B (social, competition, digestive, signals)
        et Phase C (calving, dispersal, thermal, pressure) en un score unique.
        """
        result = MultiFactorScore()
        weights = self._calculate_dynamic_weights(species, check_date, hour)
        factor_scores = {}
        recommendations = []
        active = 0

        # === C.1 CALVING ===
        calving_active, calving_model = self._calving.is_calving_active(species, region, check_date)
        calving_modifier = self._calving.get_calving_modifier(species, region, check_date, "movement")
        factor_scores["calving"] = {
            "active": calving_active,
            "modifier": calving_modifier,
            "weight": weights["calving"].effective,
            "contribution": (1.0 - calving_modifier) * weights["calving"].effective * 100
        }
        if calving_active:
            active += 1
            recommendations.append("Période de mise bas active — Éviter les zones de vêlage")

        # === C.2 DISPERSAL ===
        patterns = self._dispersal.get_patterns(species, region)
        dispersal_active = len(patterns) > 0
        factor_scores["dispersal"] = {
            "active": dispersal_active,
            "patterns_count": len(patterns),
            "weight": weights["dispersal"].effective,
            "contribution": len(patterns) * weights["dispersal"].effective * 5
        }
        if dispersal_active:
            active += 1
            recommendations.append(f"Dispersion juvénile: {len(patterns)} patrons actifs")

        # === C.3 THERMAL STRESS ===
        thermal_active = False
        thermal_modifier = 1.0
        if temperature_c is not None:
            month = check_date.month
            thermal_result = self._thermal.calculate_stress(
                species, temperature_c,
                humidity=humidity or 50.0,
                hour=hour, month=month
            )
            if thermal_result:
                thermal_active = thermal_result.get("stress_level", "none") != "none"
                thermal_modifier = thermal_result.get("modifiers", {}).get("activity", 1.0)

        factor_scores["thermal_stress"] = {
            "active": thermal_active,
            "modifier": thermal_modifier,
            "temperature_c": temperature_c,
            "weight": weights["thermal"].effective,
            "contribution": (1.0 - thermal_modifier) * weights["thermal"].effective * 100
        }
        if thermal_active:
            active += 1
            recommendations.append(f"Stress thermique à {temperature_c}°C — Animaux en refuges thermiques")

        # === C.4 HUNTING PRESSURE ===
        is_season, season_config = self._pressure.is_hunting_season(species, region, check_date)
        is_weekend = check_date.weekday() >= 5
        pressure_impact = self._pressure.calculate_pressure_impact(
            species, PressureIntensity.MODERATE if hunting_detected else PressureIntensity.LOW,
            hour=hour, is_weekend=is_weekend
        )
        pressure_modifier = pressure_impact.get("global_modifier", 1.0) if pressure_impact else 1.0

        factor_scores["hunting_pressure"] = {
            "active": is_season,
            "hunting_season": is_season,
            "is_weekend": is_weekend,
            "modifier": pressure_modifier,
            "weight": weights["pressure"].effective,
            "contribution": (1.0 - pressure_modifier) * weights["pressure"].effective * 100
        }
        if is_season:
            active += 1
            day_type = "fin de semaine" if is_weekend else "semaine"
            recommendations.append(f"Saison de chasse active ({day_type})")

        # === TEMPORAL (heure du jour) ===
        temporal_score = self._calculate_temporal_score(hour, species)
        factor_scores["temporal"] = {
            "active": True,
            "hour": hour,
            "activity_level": temporal_score,
            "weight": weights["temporal"].effective,
            "contribution": temporal_score * weights["temporal"].effective
        }
        active += 1

        # === SEASONAL CONTEXT ===
        season = self._get_season(check_date)
        season_score = self._calculate_season_score(season, species)
        factor_scores["seasonal_context"] = {
            "active": True,
            "season": season,
            "score": season_score,
            "weight": weights["seasonal"].effective,
            "contribution": season_score * weights["seasonal"].effective
        }
        active += 1

        # === EXTRA MODIFIERS (Phase B passthrough) ===
        extra = extra_modifiers or {}
        if extra:
            factor_scores["phase_b"] = {
                "active": True,
                "modifiers": extra,
                "combined": self._combine_dict_values(extra),
                "weight": weights["phase_b"].effective
            }
            if any(v != 1.0 for v in extra.values()):
                active += 1

        # === COMPOSITE SCORE ===
        total_weight = sum(w.effective for w in weights.values())
        total_contribution = sum(
            f.get("contribution", 0) for f in factor_scores.values()
            if isinstance(f.get("contribution"), (int, float))
        )

        composite = min(100, max(0, 50 + total_contribution / max(1, total_weight) * 10))

        # Risk level
        risk_factors = sum(1 for k in ["calving", "thermal_stress", "hunting_pressure"]
                          if factor_scores.get(k, {}).get("active", False))
        risk_level = "critical" if risk_factors >= 3 else "elevated" if risk_factors >= 2 else "moderate" if risk_factors >= 1 else "normal"

        result.score = composite
        result.confidence = min(1.0, active / 6)
        result.active_factors = active
        result.factors = factor_scores
        result.recommendations = recommendations
        result.risk_level = risk_level

        return result

    def _calculate_dynamic_weights(self, species: str, check_date: date, hour: int) -> Dict[str, DynamicWeight]:
        """Calcule les pondérations dynamiques selon le contexte."""
        season = self._get_season(check_date)
        month = check_date.month
        is_dawn_dusk = hour in range(5, 8) or hour in range(17, 20)

        weights = {
            "calving": DynamicWeight(base_weight=1.2),
            "dispersal": DynamicWeight(base_weight=0.8),
            "thermal": DynamicWeight(base_weight=1.0),
            "pressure": DynamicWeight(base_weight=1.5),
            "temporal": DynamicWeight(base_weight=1.0),
            "seasonal": DynamicWeight(base_weight=0.8),
            "phase_b": DynamicWeight(base_weight=0.6),
        }

        # Boost calving in spring
        if month in [5, 6]:
            weights["calving"].seasonal_boost = 0.5

        # Boost thermal in summer
        if month in [6, 7, 8]:
            weights["thermal"].seasonal_boost = 0.4

        # Boost pressure in hunting season (sept-dec)
        if month in [9, 10, 11, 12]:
            weights["pressure"].seasonal_boost = 0.5

        # Boost dispersal in fall
        if month in [9, 10, 11]:
            weights["dispersal"].seasonal_boost = 0.3

        # Dawn/dusk boost temporal
        if is_dawn_dusk:
            weights["temporal"].context_boost = 0.3

        return weights

    def _calculate_temporal_score(self, hour: int, species: str) -> float:
        """Score d'activité basé sur l'heure."""
        if species in ("orignal", "cerf_de_virginie"):
            if hour in range(5, 8) or hour in range(17, 20):
                return 90.0
            elif hour in range(8, 10) or hour in range(15, 17):
                return 60.0
            elif hour in range(10, 15):
                return 30.0
            else:
                return 45.0
        return 50.0

    def _calculate_season_score(self, season: str, species: str) -> float:
        """Score basé sur la saison."""
        scores = {
            "spring": 65.0, "summer": 55.0,
            "fall": 80.0, "winter": 40.0
        }
        base = scores.get(season, 50.0)
        if species == "orignal" and season == "fall":
            base += 15.0  # Rut boost
        return min(100, base)

    @staticmethod
    def _get_season(d: date) -> str:
        month = d.month
        if month in (12, 1, 2):
            return "winter"
        elif month in (3, 4, 5):
            return "spring"
        elif month in (6, 7, 8):
            return "summer"
        return "fall"

    @staticmethod
    def _combine_dict_values(d: Dict[str, float]) -> float:
        result = 1.0
        for v in d.values():
            if isinstance(v, (int, float)):
                result *= v
        return result


def get_multifactor_engine() -> MultiFactorScoringEngine:
    """Accès au singleton MultiFactorScoringEngine."""
    return MultiFactorScoringEngine()
