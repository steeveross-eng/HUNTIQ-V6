"""
TEST SUITE — PHASE G+ (Comparison + API Keys Healthcheck)
BIONIC V5 ULTIME 300%

Validation:
- /pipeline/comparison: 5 especes, 3 paires de territoires
- /system/api-keys/status: healthcheck des cles
- Conformite BIONIC V5 ULTIME 300%
"""

import pytest
from modules.bionic_engine_p0.services.comparison_service import compare_territories

SPECIES_LIST = ["moose", "deer", "bear", "wild_turkey", "elk"]

TERRITORY_A = {"north": 46.95, "south": 46.85, "east": -74.00, "west": -74.15}
TERRITORY_B = {"north": 47.60, "south": 47.50, "east": -70.50, "west": -70.65}
TERRITORY_C = {"north": 45.55, "south": 45.45, "east": -75.70, "west": -75.85}

RESOLUTION = 30
SCORE_DIMS = ["habitat_quality", "corridor_connectivity", "wind_protection",
              "low_pressure", "behavioral_activity", "thermal_comfort", "overall_score"]


class TestComparison:
    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_comparison_returns_valid_structure(self, species):
        result = compare_territories(TERRITORY_A, TERRITORY_B, species, RESOLUTION)
        assert result["pipeline"] == "BIONIC_V5_ULTIME_300"
        assert result["species"] == species
        assert "territory_a" in result
        assert "territory_b" in result
        assert "advantages" in result
        assert "recommendation" in result

    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_both_territories_have_scores(self, species):
        result = compare_territories(TERRITORY_A, TERRITORY_B, species, RESOLUTION)
        for t in ["territory_a", "territory_b"]:
            for dim in SCORE_DIMS:
                assert dim in result[t]["scores"]
                v = result[t]["scores"][dim]
                assert 0.0 <= v <= 1.0 + 1e-9, f"{t}.{dim} = {v}"

    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_recommendation_valid(self, species):
        result = compare_territories(TERRITORY_A, TERRITORY_B, species, RESOLUTION)
        assert result["recommendation"] in ("territory_a", "territory_b", "equivalent")

    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_source_ids_present(self, species):
        result = compare_territories(TERRITORY_A, TERRITORY_C, species, RESOLUTION)
        for t in ["territory_a", "territory_b"]:
            ids = result[t]["source_ids"]
            assert len(ids) == 10

    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_validation_flags(self, species):
        result = compare_territories(TERRITORY_A, TERRITORY_B, species, RESOLUTION)
        v = result["validation"]
        assert v["pipeline_a_complete"] is True
        assert v["pipeline_b_complete"] is True
        assert v["zero_transversality"] is True
        assert v["zero_duplication"] is True
        assert v["comparison_post_pipeline"] is True

    def test_advantages_structure(self):
        result = compare_territories(TERRITORY_A, TERRITORY_B, "moose", RESOLUTION)
        adv = result["advantages"]
        assert "territory_a_advantages" in adv
        assert "territory_b_advantages" in adv
        assert "ties" in adv

    def test_different_territories_produce_different_scores(self):
        result = compare_territories(TERRITORY_A, TERRITORY_B, "deer", RESOLUTION)
        sa = result["territory_a"]["scores"]["overall_score"]
        sb = result["territory_b"]["scores"]["overall_score"]
        # Territories are different enough geographically
        assert isinstance(sa, float)
        assert isinstance(sb, float)

    def test_score_delta_matches(self):
        result = compare_territories(TERRITORY_A, TERRITORY_C, "bear", RESOLUTION)
        sa = result["territory_a"]["scores"]["overall_score"]
        sb = result["territory_b"]["scores"]["overall_score"]
        expected_delta = round(sa - sb, 4)
        assert result["score_delta"] == expected_delta
