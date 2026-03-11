"""
TEST SUITE — BMPE (Behavioral Micro-Patterns Engine)
BIONIC V5 ULTIME 300% — Phase d'Optimisation #9

Validation exhaustive:
- Multi-especes (5): moose, deer, bear, wild_turkey, elk
- Multi-territoires (3): Laurentides, Gatineau, Charlevoix
- source_id dynamique BMPE_{SPECIES}
- Pipeline 9 modules: SSE→OSG→CME→WSE→VFE→SSVL→TCVE→PME→BMPE
- 5 champs micro-pattern: retreat, exploration, hesitation, fine_movement, composite
- Corridor micro-pattern analysis
- Conformite BIONIC V5 ULTIME 300%
"""

import pytest
import numpy as np

from modules.bionic_engine_p0.services.bmpe_engine import (
    generate_bmpe_composite,
    generate_bmpe_fields,
    get_supported_species,
    BMPE_PROFILES,
)
from modules.bionic_engine_p0.services.sse_engine import generate_sse_composite
from modules.bionic_engine_p0.services.osg_engine import generate_osg_multi_layer
from modules.bionic_engine_p0.services.cme_engine import generate_cme_corridors
from modules.bionic_engine_p0.services.wse_wiv_engine import generate_wind_field
from modules.bionic_engine_p0.services.vfe_engine import generate_visibility_field
from modules.bionic_engine_p0.services.ssvl_engine import generate_ssvl_fields
from modules.bionic_engine_p0.services.tcve_engine import generate_tcve_fields
from modules.bionic_engine_p0.services.pme_engine import generate_pme_fields


SPECIES_LIST = ["moose", "deer", "bear", "wild_turkey", "elk"]

TERRITORIES = {
    "laurentides": {"north": 46.95, "south": 46.85, "east": -74.00, "west": -74.15},
    "gatineau": {"north": 45.55, "south": 45.45, "east": -75.70, "west": -75.85},
    "charlevoix": {"north": 47.60, "south": 47.50, "east": -70.50, "west": -70.65},
}

RESOLUTION = 30

BMPE_FIELD_KEYS = [
    "micro_retreat_field",
    "micro_exploration_field",
    "hesitation_field",
    "fine_movement_field",
    "composite_micro_pattern",
]

STAT_KEYS = [
    "mean_retreat", "retreat_range",
    "mean_exploration", "exploration_range",
    "mean_hesitation", "hesitation_range",
    "mean_fine_movement", "fine_movement_range",
    "mean_composite", "composite_range",
]


def _build_pipeline(bounds, species, resolution=RESOLUTION):
    """Build the full SSE→...→PME pipeline for a given species and bounds."""
    sse = generate_sse_composite(bounds, species, resolution)
    osg = generate_osg_multi_layer(bounds, species, ["habitats", "alimentation"], sse, resolution, 4)
    cme = generate_cme_corridors(bounds, species, sse, osg, resolution, ["movement", "feeding_transit"], 6)
    wse = generate_wind_field(bounds, species, sse, resolution, 15.0, 270.0)
    vfe = generate_visibility_field(sse, wse, species, resolution)
    ssvl = generate_ssvl_fields(vfe, sse, wse, species, resolution)
    tcve = generate_tcve_fields(sse, wse, ssvl, vfe, species, resolution)
    pme = generate_pme_fields(sse, wse, ssvl, tcve, bounds, species, resolution)
    return sse, osg, cme, wse, vfe, ssvl, tcve, pme


# =================================================================
# 1. SUPPORTED SPECIES
# =================================================================

class TestSupportedSpecies:
    def test_all_species_present(self):
        supported = get_supported_species()
        for sp in SPECIES_LIST:
            assert sp in supported, f"{sp} manquant dans get_supported_species()"

    def test_profiles_match_species(self):
        for sp in SPECIES_LIST:
            assert sp in BMPE_PROFILES, f"{sp} manquant dans BMPE_PROFILES"

    def test_profile_keys(self):
        expected_keys = {
            "retreat_threshold", "exploration_drive", "hesitation_sensitivity",
            "fine_movement_freq", "pressure_retreat_amp", "edge_hesitation_factor",
            "wind_retreat_factor", "cover_exploration_bonus", "prudence_retreat_link",
            "terrain_movement_mod",
        }
        for sp in SPECIES_LIST:
            assert set(BMPE_PROFILES[sp].keys()) == expected_keys, f"Profil {sp} incomplet"

    def test_profile_values_range(self):
        for sp in SPECIES_LIST:
            for k, v in BMPE_PROFILES[sp].items():
                assert 0.0 <= v <= 1.0, f"{sp}.{k} = {v} hors [0,1]"


# =================================================================
# 2. BMPE FIELDS — MULTI-ESPECES x MULTI-TERRITOIRES
# =================================================================

class TestBMPEFieldsGeneration:
    @pytest.mark.parametrize("species", SPECIES_LIST)
    @pytest.mark.parametrize("territory", TERRITORIES.keys())
    def test_fields_generated(self, species, territory):
        bounds = TERRITORIES[territory]
        sse, _, _, wse, _, ssvl, tcve, pme = _build_pipeline(bounds, species)
        fields = generate_bmpe_fields(sse, wse, ssvl, tcve, pme, bounds, species, RESOLUTION)
        for key in BMPE_FIELD_KEYS:
            assert key in fields, f"Champ {key} manquant pour {species}/{territory}"

    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_fields_shape(self, species):
        bounds = TERRITORIES["laurentides"]
        sse, _, _, wse, _, ssvl, tcve, pme = _build_pipeline(bounds, species)
        fields = generate_bmpe_fields(sse, wse, ssvl, tcve, pme, bounds, species, RESOLUTION)
        for key in BMPE_FIELD_KEYS:
            arr = fields[key]
            assert isinstance(arr, np.ndarray), f"{key} n'est pas un ndarray"
            assert arr.shape == (RESOLUTION, RESOLUTION), f"{key} shape {arr.shape} != ({RESOLUTION},{RESOLUTION})"

    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_fields_normalized_0_1(self, species):
        bounds = TERRITORIES["gatineau"]
        sse, _, _, wse, _, ssvl, tcve, pme = _build_pipeline(bounds, species)
        fields = generate_bmpe_fields(sse, wse, ssvl, tcve, pme, bounds, species, RESOLUTION)
        for key in BMPE_FIELD_KEYS:
            arr = fields[key]
            assert arr.min() >= 0.0, f"{key} min={arr.min()} < 0 pour {species}"
            assert arr.max() <= 1.0 + 1e-9, f"{key} max={arr.max()} > 1 pour {species}"


# =================================================================
# 3. BMPE COMPOSITE — MULTI-ESPECES x MULTI-TERRITOIRES
# =================================================================

class TestBMPEComposite:
    @pytest.mark.parametrize("species", SPECIES_LIST)
    @pytest.mark.parametrize("territory", TERRITORIES.keys())
    def test_composite_source_id(self, species, territory):
        bounds = TERRITORIES[territory]
        sse, _, cme, wse, _, ssvl, tcve, pme = _build_pipeline(bounds, species)
        result = generate_bmpe_composite(bounds, species, sse, wse, ssvl, tcve, pme, cme["corridors"], RESOLUTION)
        assert result["source_id"] == f"BMPE_{species.upper()}"

    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_composite_stats_keys(self, species):
        bounds = TERRITORIES["charlevoix"]
        sse, _, cme, wse, _, ssvl, tcve, pme = _build_pipeline(bounds, species)
        result = generate_bmpe_composite(bounds, species, sse, wse, ssvl, tcve, pme, cme["corridors"], RESOLUTION)
        for key in STAT_KEYS:
            assert key in result["stats"], f"Stat {key} manquante pour {species}"

    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_composite_stats_ranges_valid(self, species):
        bounds = TERRITORIES["laurentides"]
        sse, _, cme, wse, _, ssvl, tcve, pme = _build_pipeline(bounds, species)
        result = generate_bmpe_composite(bounds, species, sse, wse, ssvl, tcve, pme, cme["corridors"], RESOLUTION)
        stats = result["stats"]
        for name in ["retreat", "exploration", "hesitation", "fine_movement", "composite"]:
            mean_val = stats[f"mean_{name}"]
            rng = stats[f"{name}_range"]
            assert 0.0 <= mean_val <= 1.0, f"mean_{name}={mean_val} hors [0,1]"
            assert len(rng) == 2, f"{name}_range invalide"
            assert rng[0] <= rng[1], f"{name}_range[0]={rng[0]} > range[1]={rng[1]}"
            assert 0.0 <= rng[0] and rng[1] <= 1.0 + 1e-9

    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_composite_validation_flags(self, species):
        bounds = TERRITORIES["gatineau"]
        sse, _, cme, wse, _, ssvl, tcve, pme = _build_pipeline(bounds, species)
        result = generate_bmpe_composite(bounds, species, sse, wse, ssvl, tcve, pme, cme["corridors"], RESOLUTION)
        v = result["validation"]
        assert v["sse_integrated"] is True
        assert v["wse_integrated"] is True
        assert v["ssvl_integrated"] is True
        assert v["tcve_integrated"] is True
        assert v["pme_integrated"] is True
        assert v["cme_integrated"] is True
        assert v["all_fields_normalized"] is True
        assert v["species_profile_applied"] is True


# =================================================================
# 4. CORRIDOR MICRO-PATTERN ANALYSIS
# =================================================================

class TestCorridorMicroPatterns:
    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_corridor_patterns_count(self, species):
        bounds = TERRITORIES["laurentides"]
        sse, _, cme, wse, _, ssvl, tcve, pme = _build_pipeline(bounds, species)
        result = generate_bmpe_composite(bounds, species, sse, wse, ssvl, tcve, pme, cme["corridors"], RESOLUTION)
        patterns = result["corridor_micro_patterns"]
        assert len(patterns) > 0, f"Aucun corridor pattern pour {species}"

    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_corridor_pattern_structure(self, species):
        bounds = TERRITORIES["charlevoix"]
        sse, _, cme, wse, _, ssvl, tcve, pme = _build_pipeline(bounds, species)
        result = generate_bmpe_composite(bounds, species, sse, wse, ssvl, tcve, pme, cme["corridors"], RESOLUTION)
        for cp in result["corridor_micro_patterns"]:
            assert "corridor_id" in cp
            assert "micro_pattern_analysis" in cp
            mpa = cp["micro_pattern_analysis"]
            assert "mean_retreat" in mpa
            assert "mean_exploration" in mpa
            assert "mean_hesitation" in mpa
            assert "mean_fine_movement" in mpa
            assert "mean_composite" in mpa
            assert "pattern_class" in mpa
            assert "sample_count" in mpa

    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_corridor_pattern_class_valid(self, species):
        bounds = TERRITORIES["gatineau"]
        sse, _, cme, wse, _, ssvl, tcve, pme = _build_pipeline(bounds, species)
        result = generate_bmpe_composite(bounds, species, sse, wse, ssvl, tcve, pme, cme["corridors"], RESOLUTION)
        valid_classes = {"avoidance_corridor", "exploration_corridor", "transition_hesitation", "stable_transit"}
        for cp in result["corridor_micro_patterns"]:
            cls = cp["micro_pattern_analysis"]["pattern_class"]
            assert cls in valid_classes, f"pattern_class '{cls}' invalide"


# =================================================================
# 5. SPECIES DIFFERENTIATION
# =================================================================

class TestSpeciesDifferentiation:
    def test_different_species_produce_different_stats(self):
        bounds = TERRITORIES["laurentides"]
        results = {}
        for species in SPECIES_LIST:
            sse, _, cme, wse, _, ssvl, tcve, pme = _build_pipeline(bounds, species)
            r = generate_bmpe_composite(bounds, species, sse, wse, ssvl, tcve, pme, cme["corridors"], RESOLUTION)
            results[species] = r["stats"]["mean_composite"]
        values = list(results.values())
        assert len(set(round(v, 4) for v in values)) > 1, "Toutes les especes ont le meme composite"

    def test_deer_more_hesitant_than_bear(self):
        bounds = TERRITORIES["charlevoix"]
        deer_sse, _, deer_cme, deer_wse, _, deer_ssvl, deer_tcve, deer_pme = _build_pipeline(bounds, "deer")
        deer = generate_bmpe_composite(bounds, "deer", deer_sse, deer_wse, deer_ssvl, deer_tcve, deer_pme, deer_cme["corridors"], RESOLUTION)
        bear_sse, _, bear_cme, bear_wse, _, bear_ssvl, bear_tcve, bear_pme = _build_pipeline(bounds, "bear")
        bear = generate_bmpe_composite(bounds, "bear", bear_sse, bear_wse, bear_ssvl, bear_tcve, bear_pme, bear_cme["corridors"], RESOLUTION)
        assert deer["stats"]["mean_hesitation"] > bear["stats"]["mean_hesitation"], \
            f"deer hesitation {deer['stats']['mean_hesitation']} <= bear {bear['stats']['mean_hesitation']}"


# =================================================================
# 6. TERRITORY DIFFERENTIATION
# =================================================================

class TestTerritoryDifferentiation:
    def test_different_territories_produce_different_results(self):
        species = "moose"
        results = {}
        for name, bounds in TERRITORIES.items():
            sse, _, cme, wse, _, ssvl, tcve, pme = _build_pipeline(bounds, species)
            r = generate_bmpe_composite(bounds, species, sse, wse, ssvl, tcve, pme, cme["corridors"], RESOLUTION)
            results[name] = r["stats"]["mean_composite"]
        values = list(results.values())
        assert len(set(round(v, 4) for v in values)) > 1, "Territoires identiques"


# =================================================================
# 7. PIPELINE INTEGRITY — 9 MODULES TRACABLE
# =================================================================

class TestPipelineIntegrity:
    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_source_id_dynamic(self, species):
        bounds = TERRITORIES["laurentides"]
        sse, _, cme, wse, _, ssvl, tcve, pme = _build_pipeline(bounds, species)
        result = generate_bmpe_composite(bounds, species, sse, wse, ssvl, tcve, pme, cme["corridors"], RESOLUTION)
        assert result["source_id"] == f"BMPE_{species.upper()}"
        assert result["species"] == species

    def test_resolution_preserved(self):
        bounds = TERRITORIES["laurentides"]
        for res in [20, 40]:
            sse, _, cme, wse, _, ssvl, tcve, pme = _build_pipeline(bounds, "moose", res)
            result = generate_bmpe_composite(bounds, "moose", sse, wse, ssvl, tcve, pme, cme["corridors"], res)
            assert result["resolution"] == res

    def test_bounds_preserved(self):
        for name, bounds in TERRITORIES.items():
            sse, _, cme, wse, _, ssvl, tcve, pme = _build_pipeline(bounds, "elk")
            result = generate_bmpe_composite(bounds, "elk", sse, wse, ssvl, tcve, pme, cme["corridors"], RESOLUTION)
            assert result["bounds"] == bounds, f"Bounds non preserves pour {name}"


# =================================================================
# 8. CONFORMITE BIONIC V5 ULTIME 300%
# =================================================================

class TestConformiteBionicV5:
    def test_zero_transversality(self):
        """BMPE ne doit pas recalculer les champs des modules precedents."""
        bounds = TERRITORIES["laurentides"]
        sse, _, cme, wse, _, ssvl, tcve, pme = _build_pipeline(bounds, "moose")
        result = generate_bmpe_composite(bounds, "moose", sse, wse, ssvl, tcve, pme, cme["corridors"], RESOLUTION)
        # BMPE ne doit contenir que ses propres champs, pas ceux de PME, TCVE, etc.
        assert "pressure_memory_field" not in result
        assert "terrain_roughness_field" not in result

    def test_all_validation_flags_true(self):
        for sp in SPECIES_LIST:
            bounds = TERRITORIES["laurentides"]
            sse, _, cme, wse, _, ssvl, tcve, pme = _build_pipeline(bounds, sp)
            result = generate_bmpe_composite(bounds, sp, sse, wse, ssvl, tcve, pme, cme["corridors"], RESOLUTION)
            for k, v in result["validation"].items():
                assert v is True, f"validation[{k}] = {v} pour {sp}"
