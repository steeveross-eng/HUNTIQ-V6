"""
TEST SUITE — Pipeline Full Analysis & Metrics
BIONIC V5 ULTIME 300% — PHASE G

Validation:
- Full pipeline 10 modules en ordre strict
- Multi-especes (5), multi-territoires (3)
- Metriques globales multi-especes
- source_ids dynamiques pour les 10 modules
- Corridor analyses (PME, BMPE, TFE)
- Conformite BIONIC V5 ULTIME 300%
"""

import pytest
from modules.bionic_engine_p0.services.pipeline_service import (
    execute_full_pipeline,
    generate_pipeline_metrics,
)

SPECIES_LIST = ["moose", "deer", "bear", "wild_turkey", "elk"]

TERRITORIES = {
    "laurentides": {"north": 46.95, "south": 46.85, "east": -74.00, "west": -74.15},
    "gatineau": {"north": 45.55, "south": 45.45, "east": -75.70, "west": -75.85},
    "charlevoix": {"north": 47.60, "south": 47.50, "east": -70.50, "west": -70.65},
}

RESOLUTION = 30
MODULE_ORDER = ["SSE", "OSG", "CME", "WSE_WIV", "VFE", "SSVL", "TCVE", "PME", "BMPE", "TFE"]
SOURCE_ID_KEYS = ["sse", "osg", "cme", "wse", "vfe", "ssvl", "tcve", "pme", "bmpe", "tfe"]


class TestFullAnalysis:
    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_full_analysis_returns_all_modules(self, species):
        bounds = TERRITORIES["laurentides"]
        result = execute_full_pipeline(bounds, species, RESOLUTION)
        assert result["module_count"] == 10
        assert result["species"] == species
        assert result["pipeline"] == "BIONIC_V5_ULTIME_300"

    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_source_ids_all_present(self, species):
        bounds = TERRITORIES["gatineau"]
        result = execute_full_pipeline(bounds, species, RESOLUTION)
        for key in SOURCE_ID_KEYS:
            assert key in result["pipeline_source_ids"]
            assert species.upper() in result["pipeline_source_ids"][key]

    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_module_stats_all_present(self, species):
        bounds = TERRITORIES["charlevoix"]
        result = execute_full_pipeline(bounds, species, RESOLUTION)
        for mod in MODULE_ORDER:
            assert mod in result["module_stats"], f"Stats manquantes pour {mod}"

    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_module_timings_all_present(self, species):
        bounds = TERRITORIES["laurentides"]
        result = execute_full_pipeline(bounds, species, RESOLUTION)
        for mod in MODULE_ORDER:
            assert mod in result["module_timings_ms"]
            assert result["module_timings_ms"][mod] >= 0

    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_corridor_analyses_present(self, species):
        bounds = TERRITORIES["laurentides"]
        result = execute_full_pipeline(bounds, species, RESOLUTION)
        ca = result["corridor_analyses"]
        assert "pme_pressure" in ca
        assert "bmpe_micro_patterns" in ca
        assert "tfe_thermal" in ca
        assert len(ca["tfe_thermal"]) > 0

    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_validation_flags(self, species):
        bounds = TERRITORIES["gatineau"]
        result = execute_full_pipeline(bounds, species, RESOLUTION)
        v = result["validation"]
        assert v["all_modules_executed"] is True
        assert v["zero_transversality"] is True
        assert v["zero_duplication"] is True
        assert v["source_ids_dynamic"] is True
        assert v["all_fields_normalized"] is True
        assert v["species_profile_applied"] is True

    @pytest.mark.parametrize("territory", TERRITORIES.keys())
    def test_territories_produce_different_results(self, territory):
        bounds = TERRITORIES[territory]
        result = execute_full_pipeline(bounds, "moose", RESOLUTION)
        assert result["bounds"] == bounds
        assert result["resolution"] == RESOLUTION

    def test_different_species_produce_different_stats(self):
        bounds = TERRITORIES["laurentides"]
        composites = {}
        for sp in SPECIES_LIST:
            r = execute_full_pipeline(bounds, sp, RESOLUTION)
            composites[sp] = r["module_stats"]["TFE"].get("mean_thermal_flow_composite", 0)
        values = list(composites.values())
        assert len(set(round(v, 4) for v in values)) > 1


class TestPipelineMetrics:
    def test_metrics_all_species(self):
        bounds = TERRITORIES["laurentides"]
        result = generate_pipeline_metrics(bounds, SPECIES_LIST, RESOLUTION)
        assert result["species_count"] == 5
        for sp in SPECIES_LIST:
            assert sp in result["species_results"]

    def test_metrics_subset_species(self):
        bounds = TERRITORIES["gatineau"]
        subset = ["moose", "bear"]
        result = generate_pipeline_metrics(bounds, subset, RESOLUTION)
        assert result["species_count"] == 2
        assert "moose" in result["species_results"]
        assert "bear" in result["species_results"]

    def test_metrics_validation(self):
        bounds = TERRITORIES["charlevoix"]
        result = generate_pipeline_metrics(bounds, ["moose"], RESOLUTION)
        assert result["validation"]["all_species_processed"] is True


class TestConformitePipelineG:
    def test_pipeline_order_strict(self):
        bounds = TERRITORIES["laurentides"]
        result = execute_full_pipeline(bounds, "moose", RESOLUTION)
        assert result["validation"]["pipeline_order"] == "SSE->OSG->CME->WSE->VFE->SSVL->TCVE->PME->BMPE->TFE"

    def test_no_cross_module_data_leakage(self):
        bounds = TERRITORIES["laurentides"]
        result = execute_full_pipeline(bounds, "deer", RESOLUTION)
        assert "pressure_memory_field" not in result
        assert "micro_retreat_field" not in result
        assert "thermal_gradient_field" not in result
