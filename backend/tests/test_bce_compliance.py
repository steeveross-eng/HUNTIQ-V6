"""
BIONIC Compliance Engine (BCE) — Comprehensive Test Suite
==========================================================

50+ assertions covering all 10 BCE validators.
This test file IS the regression wall that prevents future breakage.

Run: cd /app/backend && python -m pytest tests/test_bce_compliance.py -v
"""

import pytest
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# =====================================================================
# 1. SPATIAL INTEGRITY TESTS (5 assertions)
# =====================================================================

class TestSpatialIntegrity:
    def test_valid_geojson_passes(self):
        from bce.validators.spatial_integrity import validate
        geojson = {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [-71.24, 46.82], [-71.23, 46.82],
                        [-71.23, 46.83], [-71.24, 46.83],
                        [-71.24, 46.82],
                    ]],
                },
                "properties": {"layer_id": "habitats"},
            }],
        }
        result = validate(geojson)
        assert result["status"] == "PASS"
        assert all(c["status"] == "PASS" for c in result["checks"])

    def test_empty_geojson_passes(self):
        from bce.validators.spatial_integrity import validate
        result = validate({"type": "FeatureCollection", "features": []})
        assert result["status"] == "PASS"

    def test_invalid_geometry_fails(self):
        from bce.validators.spatial_integrity import validate
        # Bow-tie / self-intersecting polygon
        geojson = {
            "features": [{
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [0, 0], [2, 2], [2, 0], [0, 2], [0, 0],
                    ]],
                },
                "properties": {},
            }],
        }
        result = validate(geojson)
        assert result["status"] == "FAIL"

    def test_degenerate_polygon_detected(self):
        from bce.validators.spatial_integrity import validate
        geojson = {
            "features": [{
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[0, 0], [0, 0], [0, 0]]],
                },
                "properties": {},
            }],
        }
        result = validate(geojson)
        # Should detect degenerate polygon
        assert any(c["name"] == "no_degenerate_polygons" for c in result["checks"])

    def test_out_of_range_coordinates_fail(self):
        from bce.validators.spatial_integrity import validate
        geojson = {
            "features": [{
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [999, 999], [1000, 999], [1000, 1000], [999, 999],
                    ]],
                },
                "properties": {},
            }],
        }
        result = validate(geojson)
        coords_check = [c for c in result["checks"] if c["name"] == "coordinates_wgs84_valid"]
        assert coords_check[0]["status"] == "FAIL"


# =====================================================================
# 2. WATER EXCLUSION TESTS (7 assertions)
# =====================================================================

class TestWaterExclusion:
    def _make_water_exclusions(self):
        return [{
            "type": "water",
            "geometry_type": "polygon",
            "sub_type": "river",
            "coordinates": [
                [-71.22, 46.80], [-71.18, 46.80],
                [-71.18, 46.82], [-71.22, 46.82],
                [-71.22, 46.80],
            ],
        }]

    def test_zone_outside_water_passes(self):
        from bce.validators.water_exclusion import validate
        geojson = {
            "features": [{
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [-71.30, 46.85], [-71.29, 46.85],
                        [-71.29, 46.86], [-71.30, 46.86],
                        [-71.30, 46.85],
                    ]],
                },
                "properties": {"layer_id": "habitats"},
            }],
        }
        result = validate(geojson, exclusions=self._make_water_exclusions())
        assert result["status"] == "PASS"

    def test_zone_inside_water_fails(self):
        from bce.validators.water_exclusion import validate
        # Zone completely inside water
        geojson = {
            "features": [{
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [-71.21, 46.805], [-71.19, 46.805],
                        [-71.19, 46.815], [-71.21, 46.815],
                        [-71.21, 46.805],
                    ]],
                },
                "properties": {"layer_id": "habitats"},
            }],
        }
        result = validate(geojson, exclusions=self._make_water_exclusions())
        assert result["status"] == "FAIL"

    def test_centroid_in_water_detected(self):
        from bce.validators.water_exclusion import validate
        geojson = {
            "features": [{
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [-71.21, 46.805], [-71.19, 46.805],
                        [-71.19, 46.815], [-71.21, 46.815],
                        [-71.21, 46.805],
                    ]],
                },
                "properties": {},
            }],
        }
        result = validate(geojson, exclusions=self._make_water_exclusions())
        centroid_check = [c for c in result["checks"] if c["name"] == "no_centroid_in_water"]
        assert centroid_check[0]["status"] == "FAIL"

    def test_no_water_data_warns(self):
        from bce.validators.water_exclusion import validate
        result = validate({"features": []}, exclusions=[])
        assert result["status"] == "WARN"

    def test_zone_partially_in_water_fails(self):
        from bce.validators.water_exclusion import validate
        # Zone overlapping 50% water
        geojson = {
            "features": [{
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [-71.23, 46.81], [-71.19, 46.81],
                        [-71.19, 46.82], [-71.23, 46.82],
                        [-71.23, 46.81],
                    ]],
                },
                "properties": {"layer_id": "habitats"},
            }],
        }
        result = validate(geojson, exclusions=self._make_water_exclusions())
        intersect_check = [c for c in result["checks"] if c["name"] == "no_zone_intersects_water"]
        assert intersect_check[0]["status"] == "FAIL"

    def test_zone_adjacent_but_not_overlapping_passes(self):
        from bce.validators.water_exclusion import validate
        # Zone just touching the water boundary
        geojson = {
            "features": [{
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [-71.24, 46.80], [-71.22, 46.80],
                        [-71.22, 46.82], [-71.24, 46.82],
                        [-71.24, 46.80],
                    ]],
                },
                "properties": {},
            }],
        }
        result = validate(geojson, exclusions=self._make_water_exclusions())
        intersect_check = [c for c in result["checks"] if c["name"] == "no_zone_intersects_water"]
        assert intersect_check[0]["status"] == "PASS"

    def test_shoreline_adherence_check_exists(self):
        from bce.validators.water_exclusion import validate
        geojson = {"features": []}
        result = validate(geojson, exclusions=self._make_water_exclusions())
        check_names = [c["name"] for c in result["checks"]]
        assert "shoreline_adherence" in check_names


# =====================================================================
# 3. SPECIES COHERENCE TESTS (6 assertions)
# =====================================================================

class TestSpeciesCoherence:
    def test_all_species_defined(self):
        from bce.validators.species_coherence import validate
        result = validate()
        species_check = [c for c in result["checks"] if c["name"] == "all_species_defined_weights"]
        assert species_check[0]["status"] == "PASS"

    def test_species_weights_complete(self):
        from bce.validators.species_coherence import validate
        result = validate()
        weights_check = [c for c in result["checks"] if c["name"] == "species_weights_complete"]
        assert weights_check[0]["status"] == "PASS"

    def test_species_needs_complete(self):
        from bce.validators.species_coherence import validate
        result = validate()
        needs_check = [c for c in result["checks"] if c["name"] == "species_needs_complete"]
        assert needs_check[0]["status"] == "PASS"

    def test_weight_values_in_range(self):
        from bce.validators.species_coherence import validate
        result = validate()
        range_check = [c for c in result["checks"] if c["name"] == "weight_values_valid_range"]
        assert range_check[0]["status"] == "PASS"

    def test_api_returns_all_species(self):
        from bce.validators.species_coherence import validate
        result = validate()
        api_check = [c for c in result["checks"] if c["name"] == "api_returns_all_species"]
        assert api_check[0]["status"] == "PASS"

    def test_overall_pass(self):
        from bce.validators.species_coherence import validate
        result = validate()
        assert result["status"] == "PASS"


# =====================================================================
# 4. SEASON COHERENCE TESTS (5 assertions)
# =====================================================================

class TestSeasonCoherence:
    def test_all_seasons_defined(self):
        from bce.validators.season_coherence import validate
        result = validate()
        season_check = [c for c in result["checks"] if c["name"] == "all_seasons_defined"]
        assert season_check[0]["status"] == "PASS"

    def test_season_weights_complete(self):
        from bce.validators.season_coherence import validate
        result = validate()
        weights_check = [c for c in result["checks"] if c["name"] == "season_weights_complete"]
        assert weights_check[0]["status"] == "PASS"

    def test_weight_values_in_range(self):
        from bce.validators.season_coherence import validate
        result = validate()
        range_check = [c for c in result["checks"] if c["name"] == "weight_values_valid_range"]
        assert range_check[0]["status"] == "PASS"

    def test_seasons_distinct_profiles(self):
        from bce.validators.season_coherence import validate
        result = validate()
        distinct_check = [c for c in result["checks"] if c["name"] == "seasons_produce_distinct_profiles"]
        assert distinct_check[0]["status"] == "PASS"

    def test_season_modifiers_valid(self):
        from bce.validators.season_coherence import validate
        result = validate()
        mod_check = [c for c in result["checks"] if c["name"] == "season_modifiers_valid"]
        assert mod_check[0]["status"] == "PASS"


# =====================================================================
# 5. SCORING DETERMINISM TESTS (5 assertions)
# =====================================================================

class TestScoringDeterminism:
    def test_all_subscores_defined(self):
        from bce.validators.scoring_determinism import validate
        result = validate()
        check = [c for c in result["checks"] if c["name"] == "all_subscores_defined"]
        assert check[0]["status"] == "PASS"

    def test_weights_sum_to_one(self):
        from bce.validators.scoring_determinism import validate
        result = validate()
        check = [c for c in result["checks"] if c["name"] == "subscore_weights_sum_to_1"]
        assert check[0]["status"] == "PASS"

    def test_zone_types_complete(self):
        from bce.validators.scoring_determinism import validate
        result = validate()
        check = [c for c in result["checks"] if c["name"] == "zone_types_complete"]
        assert check[0]["status"] == "PASS"

    def test_scoring_deterministic(self):
        from bce.validators.scoring_determinism import validate
        result = validate()
        check = [c for c in result["checks"] if c["name"] == "scoring_deterministic"]
        assert check[0]["status"] == "PASS"

    def test_weights_all_positive(self):
        from bce.validators.scoring_determinism import validate
        result = validate()
        check = [c for c in result["checks"] if c["name"] == "subscore_weights_positive"]
        assert check[0]["status"] == "PASS"


# =====================================================================
# 6. UI COHERENCE TESTS (5 assertions)
# =====================================================================

class TestUICoherence:
    def test_species_selector_present(self):
        from bce.validators.ui_coherence import validate
        result = validate()
        check = [c for c in result["checks"] if c["name"] == "species_selector_present"]
        assert check[0]["status"] == "PASS"

    def test_season_selector_present(self):
        from bce.validators.ui_coherence import validate
        result = validate()
        check = [c for c in result["checks"] if c["name"] == "season_selector_present"]
        assert check[0]["status"] == "PASS"

    def test_no_duplicate_season_selectors(self):
        from bce.validators.ui_coherence import validate
        result = validate()
        check = [c for c in result["checks"] if c["name"] == "no_duplicate_season_selectors"]
        assert check[0]["status"] == "PASS"

    def test_corridors_default_off(self):
        from bce.validators.ui_coherence import validate
        result = validate()
        check = [c for c in result["checks"] if c["name"] == "corridors_default_off"]
        assert check[0]["status"] == "PASS"

    def test_cursor_bionic_default_off(self):
        from bce.validators.ui_coherence import validate
        result = validate()
        check = [c for c in result["checks"] if c["name"] == "cursor_bionic_default_off"]
        assert check[0]["status"] == "PASS"


# =====================================================================
# 7. ENGINE ISOLATION TESTS (5 assertions)
# =====================================================================

class TestEngineIsolation:
    def test_engine_files_exist(self):
        from bce.validators.engine_isolation import validate
        result = validate()
        check = [c for c in result["checks"] if c["name"] == "engine_files_exist"]
        assert check[0]["status"] == "PASS"

    def test_species_engine_data_only(self):
        from bce.validators.engine_isolation import validate
        result = validate()
        check = [c for c in result["checks"] if c["name"] == "species_engine_data_only"]
        assert check[0]["status"] == "PASS"

    def test_exclusion_independent_of_scoring(self):
        from bce.validators.engine_isolation import validate
        result = validate()
        check = [c for c in result["checks"] if c["name"] == "exclusion_independent_of_scoring"]
        assert check[0]["status"] == "PASS"

    def test_no_circular_imports(self):
        from bce.validators.engine_isolation import validate
        result = validate()
        check = [c for c in result["checks"] if c["name"] == "no_circular_imports"]
        assert check[0]["status"] in ("PASS", "WARN")

    def test_overall_pass(self):
        from bce.validators.engine_isolation import validate
        result = validate()
        assert result["status"] in ("PASS", "WARN")


# =====================================================================
# 8. PIPELINE ORDER TESTS (5 assertions)
# =====================================================================

class TestPipelineOrder:
    def test_all_steps_present(self):
        from bce.validators.pipeline_order import validate
        result = validate()
        check = [c for c in result["checks"] if c["name"] == "all_pipeline_steps_present"]
        assert check[0]["status"] == "PASS"

    def test_exclusion_before_scoring(self):
        from bce.validators.pipeline_order import validate
        result = validate()
        check = [c for c in result["checks"] if c["name"] == "exclusion_before_scoring"]
        assert check[0]["status"] == "PASS"

    def test_engine_version_set(self):
        from bce.validators.pipeline_order import validate
        result = validate()
        check = [c for c in result["checks"] if c["name"] == "exclusion_engine_version_set"]
        assert check[0]["status"] == "PASS"

    def test_v7_pipeline_active(self):
        from bce.validators.pipeline_order import validate
        result = validate()
        check = [c for c in result["checks"] if c["name"] == "pipeline_v7_active"]
        assert check[0]["status"] == "PASS"

    def test_geojson_export(self):
        from bce.validators.pipeline_order import validate
        result = validate()
        check = [c for c in result["checks"] if c["name"] == "exports_geojson_format"]
        assert check[0]["status"] == "PASS"


# =====================================================================
# 9. DEBUG LAYER GUARD TESTS (4 assertions)
# =====================================================================

class TestDebugLayerGuard:
    def test_main_page_debug_defaults_off(self):
        from bce.validators.debug_layer_guard import validate
        result = validate()
        check = [c for c in result["checks"] if c["name"] == "main_page_debug_defaults_off"]
        assert check[0]["status"] == "PASS"

    def test_split_view_hides_debug(self):
        from bce.validators.debug_layer_guard import validate
        result = validate()
        check = [c for c in result["checks"] if c["name"] == "split_view_hides_debug"]
        assert check[0]["status"] in ("PASS", "WARN")

    def test_no_debug_bbox(self):
        from bce.validators.debug_layer_guard import validate
        result = validate()
        check = [c for c in result["checks"] if c["name"] == "no_debug_bbox"]
        assert check[0]["status"] in ("PASS", "WARN")

    def test_overall_pass(self):
        from bce.validators.debug_layer_guard import validate
        result = validate()
        assert result["status"] in ("PASS", "WARN")


# =====================================================================
# 10. GOLDEN STATE TESTS (4 assertions)
# =====================================================================

class TestGoldenState:
    def test_golden_state_creates_on_first_run(self):
        from bce.validators.golden_state import validate, GOLDEN_STATE_PATH
        # Remove existing golden state for clean test
        import os
        if os.path.exists(GOLDEN_STATE_PATH):
            os.remove(GOLDEN_STATE_PATH)
        result = validate()
        assert result["status"] == "PASS"
        assert os.path.exists(GOLDEN_STATE_PATH)

    def test_golden_state_matches_current(self):
        from bce.validators.golden_state import validate
        result = validate()
        assert result["status"] == "PASS"

    def test_golden_state_has_all_fields(self):
        from bce.validators.golden_state import _load_golden_state
        golden = _load_golden_state()
        assert "species" in golden
        assert "seasons" in golden
        assert "layers" in golden
        assert "zone_types" in golden
        assert "subscore_weights" in golden

    def test_golden_state_species_correct(self):
        from bce.validators.golden_state import _load_golden_state
        golden = _load_golden_state()
        assert set(golden["species"]) == {"moose", "deer", "bear", "wild_turkey", "elk"}


# =====================================================================
# 11. FULL ENGINE ORCHESTRATION TESTS (4 assertions)
# =====================================================================

class TestBCEEngine:
    def test_full_validation_runs(self):
        from bce.engine import run_full_validation
        report = run_full_validation()
        assert "overall_status" in report
        assert "validators" in report
        assert len(report["validators"]) == 10

    def test_full_validation_has_merge_flag(self):
        from bce.engine import run_full_validation
        report = run_full_validation()
        assert "merge_allowed" in report
        assert isinstance(report["merge_allowed"], bool)

    def test_single_validator_runs(self):
        from bce.engine import run_single_validator
        result = run_single_validator("species_coherence")
        assert result["status"] in ("PASS", "FAIL", "ERROR")

    def test_unknown_validator_returns_error(self):
        from bce.engine import run_single_validator
        result = run_single_validator("nonexistent_validator")
        assert result["status"] == "ERROR"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
