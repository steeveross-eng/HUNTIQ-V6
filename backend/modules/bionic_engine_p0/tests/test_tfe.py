"""
TEST SUITE — TFE (Thermal Flow Engine)
BIONIC V5 ULTIME 300% — Phase d'Optimisation #10

Validation exhaustive:
- Multi-especes (5): moose, deer, bear, wild_turkey, elk
- Multi-territoires (3): Laurentides, Gatineau, Charlevoix
- source_id dynamique TFE_{SPECIES}
- Pipeline 10 modules: SSE->OSG->CME->WSE->VFE->SSVL->TCVE->PME->BMPE->TFE
- 5 champs thermiques: gradient, inertia, hot_pocket, cold_pocket, composite
- Corridor thermal analysis
- Conformite BIONIC V5 ULTIME 300%
"""

import pytest
import numpy as np

from modules.bionic_engine_p0.services.tfe_engine import (
    generate_tfe_composite,
    generate_tfe_fields,
    get_supported_species,
    TFE_PROFILES,
)
from modules.bionic_engine_p0.services.sse_engine import generate_sse_composite
from modules.bionic_engine_p0.services.osg_engine import generate_osg_multi_layer
from modules.bionic_engine_p0.services.cme_engine import generate_cme_corridors
from modules.bionic_engine_p0.services.wse_wiv_engine import generate_wind_field
from modules.bionic_engine_p0.services.vfe_engine import generate_visibility_field
from modules.bionic_engine_p0.services.ssvl_engine import generate_ssvl_fields
from modules.bionic_engine_p0.services.tcve_engine import generate_tcve_fields
from modules.bionic_engine_p0.services.pme_engine import generate_pme_fields
from modules.bionic_engine_p0.services.bmpe_engine import generate_bmpe_fields


SPECIES_LIST = ["moose", "deer", "bear", "wild_turkey", "elk"]

TERRITORIES = {
    "laurentides": {"north": 46.95, "south": 46.85, "east": -74.00, "west": -74.15},
    "gatineau": {"north": 45.55, "south": 45.45, "east": -75.70, "west": -75.85},
    "charlevoix": {"north": 47.60, "south": 47.50, "east": -70.50, "west": -70.65},
}

RESOLUTION = 30

TFE_FIELD_KEYS = [
    "thermal_gradient_field",
    "thermal_inertia_field",
    "hot_pocket_field",
    "cold_pocket_field",
    "thermal_flow_composite",
]

STAT_KEYS = [
    "mean_gradient", "gradient_range",
    "mean_inertia", "inertia_range",
    "mean_hot_pocket", "hot_pocket_range",
    "mean_cold_pocket", "cold_pocket_range",
    "mean_composite", "composite_range",
]


def _build_pipeline(bounds, species, resolution=RESOLUTION):
    """Build the full SSE->...->BMPE pipeline for TFE input."""
    sse = generate_sse_composite(bounds, species, resolution)
    osg = generate_osg_multi_layer(bounds, species, ["habitats", "alimentation"], sse, resolution, 4)
    cme = generate_cme_corridors(bounds, species, sse, osg, resolution, ["movement", "feeding_transit"], 6)
    wse = generate_wind_field(bounds, species, sse, resolution, 15.0, 270.0)
    vfe = generate_visibility_field(sse, wse, species, resolution)
    ssvl = generate_ssvl_fields(vfe, sse, wse, species, resolution)
    tcve = generate_tcve_fields(sse, wse, ssvl, vfe, species, resolution)
    pme = generate_pme_fields(sse, wse, ssvl, tcve, bounds, species, resolution)
    bmpe = generate_bmpe_fields(sse, wse, ssvl, tcve, pme, bounds, species, resolution)
    return sse, osg, cme, wse, vfe, ssvl, tcve, pme, bmpe


# =================================================================
# 1. SUPPORTED SPECIES
# =================================================================

class TestSupportedSpecies:
    def test_all_species_present(self):
        supported = get_supported_species()
        for sp in SPECIES_LIST:
            assert sp in supported

    def test_profiles_match_species(self):
        for sp in SPECIES_LIST:
            assert sp in TFE_PROFILES

    def test_profile_keys(self):
        expected = {
            "heat_avoidance", "cold_tolerance", "thermal_inertia_preference",
            "hot_pocket_sensitivity", "cold_pocket_sensitivity", "wind_chill_factor",
            "canopy_thermal_bonus", "exposure_penalty", "bmpe_retreat_thermal_link",
            "pressure_heat_amplifier",
        }
        for sp in SPECIES_LIST:
            assert set(TFE_PROFILES[sp].keys()) == expected

    def test_profile_values_range(self):
        for sp in SPECIES_LIST:
            for k, v in TFE_PROFILES[sp].items():
                assert 0.0 <= v <= 1.0, f"{sp}.{k} = {v} hors [0,1]"


# =================================================================
# 2. TFE FIELDS — MULTI-ESPECES x MULTI-TERRITOIRES
# =================================================================

class TestTFEFieldsGeneration:
    @pytest.mark.parametrize("species", SPECIES_LIST)
    @pytest.mark.parametrize("territory", TERRITORIES.keys())
    def test_fields_generated(self, species, territory):
        bounds = TERRITORIES[territory]
        sse, _, _, wse, _, ssvl, tcve, pme, bmpe = _build_pipeline(bounds, species)
        fields = generate_tfe_fields(sse, wse, ssvl, tcve, pme, bmpe, bounds, species, RESOLUTION)
        for key in TFE_FIELD_KEYS:
            assert key in fields

    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_fields_shape(self, species):
        bounds = TERRITORIES["laurentides"]
        sse, _, _, wse, _, ssvl, tcve, pme, bmpe = _build_pipeline(bounds, species)
        fields = generate_tfe_fields(sse, wse, ssvl, tcve, pme, bmpe, bounds, species, RESOLUTION)
        for key in TFE_FIELD_KEYS:
            arr = fields[key]
            assert isinstance(arr, np.ndarray)
            assert arr.shape == (RESOLUTION, RESOLUTION)

    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_fields_normalized_0_1(self, species):
        bounds = TERRITORIES["gatineau"]
        sse, _, _, wse, _, ssvl, tcve, pme, bmpe = _build_pipeline(bounds, species)
        fields = generate_tfe_fields(sse, wse, ssvl, tcve, pme, bmpe, bounds, species, RESOLUTION)
        for key in TFE_FIELD_KEYS:
            arr = fields[key]
            assert arr.min() >= 0.0
            assert arr.max() <= 1.0 + 1e-9


# =================================================================
# 3. TFE COMPOSITE — MULTI-ESPECES x MULTI-TERRITOIRES
# =================================================================

class TestTFEComposite:
    @pytest.mark.parametrize("species", SPECIES_LIST)
    @pytest.mark.parametrize("territory", TERRITORIES.keys())
    def test_composite_source_id(self, species, territory):
        bounds = TERRITORIES[territory]
        sse, _, cme, wse, _, ssvl, tcve, pme, bmpe = _build_pipeline(bounds, species)
        result = generate_tfe_composite(bounds, species, sse, wse, ssvl, tcve, pme, bmpe, cme["corridors"], RESOLUTION)
        assert result["source_id"] == f"TFE_{species.upper()}"

    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_composite_stats_keys(self, species):
        bounds = TERRITORIES["charlevoix"]
        sse, _, cme, wse, _, ssvl, tcve, pme, bmpe = _build_pipeline(bounds, species)
        result = generate_tfe_composite(bounds, species, sse, wse, ssvl, tcve, pme, bmpe, cme["corridors"], RESOLUTION)
        for key in STAT_KEYS:
            assert key in result["stats"]

    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_composite_stats_ranges_valid(self, species):
        bounds = TERRITORIES["laurentides"]
        sse, _, cme, wse, _, ssvl, tcve, pme, bmpe = _build_pipeline(bounds, species)
        result = generate_tfe_composite(bounds, species, sse, wse, ssvl, tcve, pme, bmpe, cme["corridors"], RESOLUTION)
        stats = result["stats"]
        for name in ["gradient", "inertia", "hot_pocket", "cold_pocket", "composite"]:
            mean_val = stats[f"mean_{name}"]
            rng = stats[f"{name}_range"]
            assert 0.0 <= mean_val <= 1.0
            assert len(rng) == 2
            assert rng[0] <= rng[1]
            assert 0.0 <= rng[0] and rng[1] <= 1.0 + 1e-9

    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_composite_validation_flags(self, species):
        bounds = TERRITORIES["gatineau"]
        sse, _, cme, wse, _, ssvl, tcve, pme, bmpe = _build_pipeline(bounds, species)
        result = generate_tfe_composite(bounds, species, sse, wse, ssvl, tcve, pme, bmpe, cme["corridors"], RESOLUTION)
        v = result["validation"]
        assert v["sse_integrated"] is True
        assert v["wse_integrated"] is True
        assert v["ssvl_integrated"] is True
        assert v["tcve_integrated"] is True
        assert v["pme_integrated"] is True
        assert v["bmpe_integrated"] is True
        assert v["cme_integrated"] is True
        assert v["all_fields_normalized"] is True
        assert v["species_profile_applied"] is True


# =================================================================
# 4. CORRIDOR THERMAL ANALYSIS
# =================================================================

class TestCorridorThermal:
    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_corridor_thermal_count(self, species):
        bounds = TERRITORIES["laurentides"]
        sse, _, cme, wse, _, ssvl, tcve, pme, bmpe = _build_pipeline(bounds, species)
        result = generate_tfe_composite(bounds, species, sse, wse, ssvl, tcve, pme, bmpe, cme["corridors"], RESOLUTION)
        assert len(result["corridor_thermal"]) > 0

    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_corridor_thermal_structure(self, species):
        bounds = TERRITORIES["charlevoix"]
        sse, _, cme, wse, _, ssvl, tcve, pme, bmpe = _build_pipeline(bounds, species)
        result = generate_tfe_composite(bounds, species, sse, wse, ssvl, tcve, pme, bmpe, cme["corridors"], RESOLUTION)
        for ct in result["corridor_thermal"]:
            assert "corridor_id" in ct
            assert "thermal_analysis" in ct
            ta = ct["thermal_analysis"]
            assert "mean_gradient" in ta
            assert "mean_inertia" in ta
            assert "mean_hot_pocket" in ta
            assert "mean_cold_pocket" in ta
            assert "mean_composite" in ta
            assert "thermal_class" in ta
            assert "sample_count" in ta

    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_corridor_thermal_class_valid(self, species):
        bounds = TERRITORIES["gatineau"]
        sse, _, cme, wse, _, ssvl, tcve, pme, bmpe = _build_pipeline(bounds, species)
        result = generate_tfe_composite(bounds, species, sse, wse, ssvl, tcve, pme, bmpe, cme["corridors"], RESOLUTION)
        valid_classes = {"thermal_refuge", "cold_exposure_corridor", "stable_thermal_zone", "thermal_transition"}
        for ct in result["corridor_thermal"]:
            cls = ct["thermal_analysis"]["thermal_class"]
            assert cls in valid_classes


# =================================================================
# 5. SPECIES DIFFERENTIATION
# =================================================================

class TestSpeciesDifferentiation:
    def test_different_species_produce_different_stats(self):
        bounds = TERRITORIES["laurentides"]
        results = {}
        for species in SPECIES_LIST:
            sse, _, cme, wse, _, ssvl, tcve, pme, bmpe = _build_pipeline(bounds, species)
            r = generate_tfe_composite(bounds, species, sse, wse, ssvl, tcve, pme, bmpe, cme["corridors"], RESOLUTION)
            results[species] = r["stats"]["mean_composite"]
        values = list(results.values())
        assert len(set(round(v, 4) for v in values)) > 1

    def test_bear_higher_cold_tolerance_reflected(self):
        bounds = TERRITORIES["charlevoix"]
        bear_sse, _, bear_cme, bear_wse, _, bear_ssvl, bear_tcve, bear_pme, bear_bmpe = _build_pipeline(bounds, "bear")
        bear = generate_tfe_composite(bounds, "bear", bear_sse, bear_wse, bear_ssvl, bear_tcve, bear_pme, bear_bmpe, bear_cme["corridors"], RESOLUTION)
        turkey_sse, _, turkey_cme, turkey_wse, _, turkey_ssvl, turkey_tcve, turkey_pme, turkey_bmpe = _build_pipeline(bounds, "wild_turkey")
        turkey = generate_tfe_composite(bounds, "wild_turkey", turkey_sse, turkey_wse, turkey_ssvl, turkey_tcve, turkey_pme, turkey_bmpe, turkey_cme["corridors"], RESOLUTION)
        # Bear has lower cold_pocket_sensitivity (0.25) vs turkey (0.75), so bear should have lower cold_pocket mean
        assert bear["stats"]["mean_cold_pocket"] < turkey["stats"]["mean_cold_pocket"]


# =================================================================
# 6. TERRITORY DIFFERENTIATION
# =================================================================

class TestTerritoryDifferentiation:
    def test_different_territories_produce_different_results(self):
        species = "moose"
        results = {}
        for name, bounds in TERRITORIES.items():
            sse, _, cme, wse, _, ssvl, tcve, pme, bmpe = _build_pipeline(bounds, species)
            r = generate_tfe_composite(bounds, species, sse, wse, ssvl, tcve, pme, bmpe, cme["corridors"], RESOLUTION)
            results[name] = r["stats"]["mean_composite"]
        values = list(results.values())
        assert len(set(round(v, 4) for v in values)) > 1


# =================================================================
# 7. PIPELINE INTEGRITY — 10 MODULES TRACABLE
# =================================================================

class TestPipelineIntegrity:
    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_source_id_dynamic(self, species):
        bounds = TERRITORIES["laurentides"]
        sse, _, cme, wse, _, ssvl, tcve, pme, bmpe = _build_pipeline(bounds, species)
        result = generate_tfe_composite(bounds, species, sse, wse, ssvl, tcve, pme, bmpe, cme["corridors"], RESOLUTION)
        assert result["source_id"] == f"TFE_{species.upper()}"
        assert result["species"] == species

    def test_resolution_preserved(self):
        bounds = TERRITORIES["laurentides"]
        for res in [20, 40]:
            sse, _, cme, wse, _, ssvl, tcve, pme, bmpe = _build_pipeline(bounds, "moose", res)
            result = generate_tfe_composite(bounds, "moose", sse, wse, ssvl, tcve, pme, bmpe, cme["corridors"], res)
            assert result["resolution"] == res

    def test_bounds_preserved(self):
        for name, bounds in TERRITORIES.items():
            sse, _, cme, wse, _, ssvl, tcve, pme, bmpe = _build_pipeline(bounds, "elk")
            result = generate_tfe_composite(bounds, "elk", sse, wse, ssvl, tcve, pme, bmpe, cme["corridors"], RESOLUTION)
            assert result["bounds"] == bounds


# =================================================================
# 8. CONFORMITE BIONIC V5 ULTIME 300%
# =================================================================

class TestConformiteBionicV5:
    def test_zero_transversality(self):
        bounds = TERRITORIES["laurentides"]
        sse, _, cme, wse, _, ssvl, tcve, pme, bmpe = _build_pipeline(bounds, "moose")
        result = generate_tfe_composite(bounds, "moose", sse, wse, ssvl, tcve, pme, bmpe, cme["corridors"], RESOLUTION)
        assert "pressure_memory_field" not in result
        assert "micro_retreat_field" not in result
        assert "terrain_roughness_field" not in result

    def test_all_validation_flags_true(self):
        for sp in SPECIES_LIST:
            bounds = TERRITORIES["laurentides"]
            sse, _, cme, wse, _, ssvl, tcve, pme, bmpe = _build_pipeline(bounds, sp)
            result = generate_tfe_composite(bounds, sp, sse, wse, ssvl, tcve, pme, bmpe, cme["corridors"], RESOLUTION)
            for k, v in result["validation"].items():
                assert v is True, f"validation[{k}] = {v} pour {sp}"
