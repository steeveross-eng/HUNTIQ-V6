"""
BIONIC V5 — PHASE D: Dynamic Layer Generator
===============================================
PHASE D.2 — Couches dynamiques multi-facteurs

Génère des couches cartographiques dynamiques qui intègrent
les facteurs saisonniers Phase C dans les zones comportementales.

COUCHES DYNAMIQUES:
- seasonal_influence: Influence saisonnière sur les zones de confort
- pressure_overlay: Superposition de la pression de chasse
- thermal_refuge_zones: Zones de refuge thermique
- calving_exclusion: Zones d'exclusion mise bas

INTÉGRATION:
S'intègre dans le LayerAggregatorService comme 6ème famille de layers.

VERSION: 1.0.0
Conformité: G-SEC | G-QA | G-DOC | BIONIC V5 PHASE D
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import date
from dataclasses import dataclass, field

from modules.bionic_engine_p0.knowledge.seasonal.calving_models import CalvingModelRegistry
from modules.bionic_engine_p0.knowledge.seasonal.thermal_stress import ThermalStressRegistry
from modules.bionic_engine_p0.knowledge.pressure.hunting_pressure import (
    HuntingPressureRegistry, PressureIntensity
)

logger = logging.getLogger("bionic_dynamic_layers")


@dataclass
class DynamicLayerOutput:
    """Sortie d'une couche dynamique."""
    layer_id: str
    layer_type: str
    active: bool = False
    intensity: float = 0.0
    label: str = ""
    description: str = ""
    color: str = "#FFFFFF"
    opacity: float = 0.4
    metadata: Dict[str, Any] = field(default_factory=dict)
    source_ids: List[str] = field(default_factory=lambda: ["SRC-PHASE-D-DYNAMIC-LAYER"])
    version: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "layer_id": self.layer_id,
            "layer_type": self.layer_type,
            "active": self.active,
            "intensity": round(self.intensity, 2),
            "label": self.label,
            "description": self.description,
            "style": {
                "color": self.color,
                "opacity": self.opacity,
                "fillOpacity": self.opacity * 0.6
            },
            "metadata": self.metadata,
            "source_ids": self.source_ids,
            "version": self.version
        }


class DynamicLayerGenerator:
    """
    Générateur de couches dynamiques PHASE D.
    
    Produit des couches cartographiques qui varient selon:
    - La date et l'heure
    - L'espèce ciblée
    - La température
    - La pression de chasse
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
        self._thermal = ThermalStressRegistry()
        self._pressure = HuntingPressureRegistry()
        self._initialized = True
        logger.info("DynamicLayerGenerator initialized (PHASE D)")

    def generate_dynamic_layers(
        self,
        species: str,
        region: str,
        check_date: date,
        hour: int = 12,
        temperature_c: Optional[float] = None,
        latitude: float = 46.8,
        longitude: float = -71.2
    ) -> Dict[str, DynamicLayerOutput]:
        """
        Génère toutes les couches dynamiques pour un contexte donné.
        """
        layers = {}

        # C.1 — Calving exclusion
        layers["calving_exclusion"] = self._generate_calving_layer(species, region, check_date)

        # C.3 — Thermal refuge
        layers["thermal_refuge"] = self._generate_thermal_layer(
            species, check_date, hour, temperature_c
        )

        # C.4 — Pressure overlay
        layers["pressure_overlay"] = self._generate_pressure_layer(
            species, region, check_date, hour
        )

        # Combined seasonal influence
        layers["seasonal_influence"] = self._generate_seasonal_influence(
            species, region, check_date, hour, temperature_c
        )

        return layers

    def _generate_calving_layer(self, species: str, region: str, check_date: date) -> DynamicLayerOutput:
        """Génère la couche d'exclusion de mise bas."""
        calving_active, model = self._calving.is_calving_active(species, region, check_date)
        modifier = self._calving.get_calving_modifier(species, region, check_date, "movement")

        return DynamicLayerOutput(
            layer_id="dynamic_calving_exclusion",
            layer_type="calving_exclusion",
            active=calving_active,
            intensity=1.0 - modifier if calving_active else 0.0,
            label="Zone de mise bas",
            description="Période de mise bas active — Mouvement réduit" if calving_active else "Hors période",
            color="#EC4899",
            opacity=0.5 if calving_active else 0.1,
            metadata={
                "calving_active": calving_active,
                "movement_modifier": modifier,
                "species": species,
                "phase": "C.1"
            }
        )

    def _generate_thermal_layer(
        self, species: str, check_date: date,
        hour: int, temperature_c: Optional[float]
    ) -> DynamicLayerOutput:
        """Génère la couche de refuges thermiques."""
        thermal_active = False
        stress_level = "none"
        modifier = 1.0

        if temperature_c is not None:
            result = self._thermal.calculate_stress(
                species, temperature_c,
                humidity=50.0, hour=hour,
                month=check_date.month
            )
            if result:
                stress_level = result.get("stress_level", "none")
                thermal_active = stress_level != "none"
                modifier = result.get("modifiers", {}).get("activity", 1.0)

        color_map = {
            "none": "#22C55E", "low": "#F59E0B",
            "moderate": "#EF4444", "high": "#DC2626",
            "critical": "#991B1B"
        }

        return DynamicLayerOutput(
            layer_id="dynamic_thermal_refuge",
            layer_type="thermal_refuge",
            active=thermal_active,
            intensity=1.0 - modifier if thermal_active else 0.0,
            label="Stress thermique",
            description=f"Niveau: {stress_level}" + (f" ({temperature_c}°C)" if temperature_c else ""),
            color=color_map.get(stress_level, "#22C55E"),
            opacity=0.5 if thermal_active else 0.1,
            metadata={
                "stress_level": stress_level,
                "temperature_c": temperature_c,
                "activity_modifier": modifier,
                "phase": "C.3"
            }
        )

    def _generate_pressure_layer(
        self, species: str, region: str,
        check_date: date, hour: int
    ) -> DynamicLayerOutput:
        """Génère la couche de pression de chasse."""
        is_season, config = self._pressure.is_hunting_season(species, region, check_date)
        is_weekend = check_date.weekday() >= 5

        modifier = 1.0
        if is_season:
            intensity = PressureIntensity.HIGH if is_weekend else PressureIntensity.MODERATE
            impact = self._pressure.calculate_pressure_impact(
                species, intensity, hour=hour, is_weekend=is_weekend
            )
            if impact:
                modifier = impact.get("global_modifier", 1.0)

        return DynamicLayerOutput(
            layer_id="dynamic_pressure_overlay",
            layer_type="pressure_overlay",
            active=is_season,
            intensity=1.0 - modifier if is_season else 0.0,
            label="Pression de chasse",
            description=("Saison active" + (" (fin de semaine)" if is_weekend else "")) if is_season else "Hors saison",
            color="#F59E0B" if is_season else "#6B7280",
            opacity=0.5 if is_season else 0.1,
            metadata={
                "hunting_season": is_season,
                "is_weekend": is_weekend,
                "modifier": modifier,
                "phase": "C.4"
            }
        )

    def _generate_seasonal_influence(
        self, species: str, region: str,
        check_date: date, hour: int,
        temperature_c: Optional[float]
    ) -> DynamicLayerOutput:
        """Génère la couche d'influence saisonnière combinée."""
        month = check_date.month

        # Calculer l'influence combinée
        calving_active, _ = self._calving.is_calving_active(species, region, check_date)
        is_season, _ = self._pressure.is_hunting_season(species, region, check_date)

        thermal_active = False
        if temperature_c is not None:
            result = self._thermal.calculate_stress(
                species, temperature_c, humidity=50.0,
                hour=hour, month=month
            )
            if result:
                thermal_active = result.get("stress_level", "none") != "none"

        active_count = sum([calving_active, thermal_active, is_season])
        influence = min(1.0, active_count / 3)

        season_names = {
            12: "hiver", 1: "hiver", 2: "hiver",
            3: "printemps", 4: "printemps", 5: "printemps",
            6: "été", 7: "été", 8: "été",
            9: "automne", 10: "automne", 11: "automne"
        }
        season = season_names.get(month, "inconnu")

        color_map = {0: "#22C55E", 1: "#F59E0B", 2: "#EF4444", 3: "#DC2626"}

        return DynamicLayerOutput(
            layer_id="dynamic_seasonal_influence",
            layer_type="seasonal_influence",
            active=active_count > 0,
            intensity=influence,
            label="Influence saisonnière",
            description=f"Saison: {season} — {active_count}/3 facteurs actifs",
            color=color_map.get(active_count, "#6B7280"),
            opacity=0.3 + influence * 0.3,
            metadata={
                "season": season,
                "month": month,
                "active_factors": active_count,
                "calving_active": calving_active,
                "thermal_active": thermal_active,
                "hunting_active": is_season,
                "phase": "D.2"
            }
        )


def get_dynamic_layer_generator() -> DynamicLayerGenerator:
    """Accès au singleton DynamicLayerGenerator."""
    return DynamicLayerGenerator()
