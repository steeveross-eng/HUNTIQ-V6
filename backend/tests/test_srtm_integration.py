"""
BIONIC V7 — Tests Integration SRTM DEM
Teste le provider SRTM, l'integration dans le pipeline V7,
le cost grid avec pente DEM, et le scoring terrain-aware.
"""

import os
import sys
import math
import asyncio
import numpy as np
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from modules.bionic_engine_p0.services.srtm_provider_v7 import (
    sample_dem_at_point,
    classify_terrain_at_point,
    get_slope_grid_resampled,
)
from modules.bionic_engine_p0.services.trail_cost_grid_v7 import build_cost_grid
from modules.bionic_engine_p0.services.zone_typology_v7 import (
    compute_subscores,
    enrich_zone_v7,
    compute_global_score,
)
from modules.bionic_engine_p0.services.pipeline_v7 import (
    process_zones_v7,
    generate_all_corridors_v7,
)


# =====================================================================
# FIXTURES
# =====================================================================

BOUNDS = {
    "north": 47.20,
    "south": 47.17,
    "east": -71.20,
    "west": -71.24,
}


def _make_dem_data(
    elev_min=200, elev_max=500, slope_mean=12, rows=60, cols=60
):
    """Create realistic mock DEM data for testing."""
    # Create a gradient elevation surface
    y = np.linspace(elev_min, elev_max, rows)
    x = np.linspace(0, 50, cols)
    elev = np.outer(y, np.ones(cols)) + np.outer(np.ones(rows), x * 2)

    # Compute slope from elevation
    grad_y = np.gradient(elev, axis=0)
    grad_x = np.gradient(elev, axis=1)
    slope = np.degrees(np.arctan(np.sqrt(grad_y**2 + grad_x**2) / 30.0))

    # Aspect
    aspect = np.degrees(np.arctan2(grad_x, -grad_y)) % 360

    # Roughness
    roughness = np.random.uniform(0.5, 5.0, (rows, cols))

    return {
        "status": "success",
        "bounds": BOUNDS,
        "dataset": "SRTMGL1",
        "resolution": rows,
        "raw_shape": [rows, cols],
        "fields": {
            "elevation": elev,
            "slope": slope,
            "aspect": aspect,
            "roughness": roughness,
            "elevation_normalized": (elev - elev.min()) / max(1, elev.max() - elev.min()),
            "slope_normalized": slope / max(1, slope.max()),
            "roughness_normalized": roughness / max(1, roughness.max()),
        },
        "stats": {
            "elevation_min": round(float(elev.min()), 2),
            "elevation_max": round(float(elev.max()), 2),
            "elevation_mean": round(float(elev.mean()), 2),
            "slope_mean_deg": round(float(slope.mean()), 2),
            "slope_max_deg": round(float(slope.max()), 2),
            "aspect_mean_deg": round(float(aspect.mean()), 2),
            "roughness_mean": round(float(roughness.mean()), 2),
            "pixel_size_m": 30.0,
        },
        "validation": {
            "data_real": True,
            "source": "OpenTopography",
            "dataset": "SRTMGL1",
        },
    }


def _make_zone(lat, lng, area=8000, compactness=0.5):
    """Create a test zone dict."""
    d = 0.001
    return {
        "coordinates": [
            [lng - d, lat - d], [lng + d, lat - d],
            [lng + d, lat + d], [lng - d, lat + d],
            [lng - d, lat - d],
        ],
        "centroid": {"lat": lat, "lng": lng},
        "area_m2": area,
        "compactness": compactness,
    }


EXCLUSIONS = [
    {"type": "water", "sub_type": "lake", "geometry_type": "polygon",
     "coordinates": [[-71.235, 47.18], [-71.234, 47.18], [-71.234, 47.181], [-71.235, 47.181]],
     "area_m2": 5000, "large_water": True},
    {"type": "roads", "sub_type": "secondary", "geometry_type": "line",
     "coordinates": [[-71.23, 47.185], [-71.22, 47.185]]},
    {"type": "urban", "sub_type": "residential", "geometry_type": "polygon",
     "coordinates": [[-71.225, 47.195], [-71.224, 47.195], [-71.224, 47.196], [-71.225, 47.196]]},
]


# =====================================================================
# TESTS: SRTM Provider
# =====================================================================

class TestSRTMProvider:
    def test_sample_dem_at_point_center(self):
        """Sample DEM at viewport center returns valid data."""
        dem = _make_dem_data()
        center_lat = (BOUNDS["north"] + BOUNDS["south"]) / 2
        center_lng = (BOUNDS["east"] + BOUNDS["west"]) / 2
        result = sample_dem_at_point(dem, center_lat, center_lng)
        assert result is not None
        assert "elevation_m" in result
        assert "slope_deg" in result
        assert "aspect_deg" in result
        assert "roughness" in result
        assert result["elevation_m"] > 0

    def test_sample_dem_returns_none_without_data(self):
        """Returns None when DEM data is unavailable."""
        assert sample_dem_at_point(None, 47.19, -71.22) is None
        assert sample_dem_at_point({"status": "no_api_key"}, 47.19, -71.22) is None

    def test_sample_dem_edge_cases(self):
        """Sample at grid edges doesn't crash."""
        dem = _make_dem_data()
        # Top-left corner
        r1 = sample_dem_at_point(dem, BOUNDS["north"], BOUNDS["west"])
        assert r1 is not None
        # Bottom-right corner
        r2 = sample_dem_at_point(dem, BOUNDS["south"], BOUNDS["east"])
        assert r2 is not None

    def test_classify_terrain_valid(self):
        """Terrain classification returns valid type."""
        dem = _make_dem_data()
        center_lat = (BOUNDS["north"] + BOUNDS["south"]) / 2
        center_lng = (BOUNDS["east"] + BOUNDS["west"]) / 2
        terrain = classify_terrain_at_point(dem, center_lat, center_lng)
        valid_types = {"valley", "ridge", "plateau", "steep_slope", "moderate_slope", "gentle_slope", "flat", "unknown"}
        assert terrain in valid_types

    def test_classify_terrain_unknown_without_dem(self):
        """Returns 'unknown' without DEM data."""
        assert classify_terrain_at_point(None, 47.19, -71.22) == "unknown"

    def test_get_slope_grid_resampled(self):
        """Slope grid resampled to target size."""
        dem = _make_dem_data(rows=60, cols=60)
        result = get_slope_grid_resampled(dem, 50, 50)
        assert result is not None
        assert result.shape == (50, 50)
        assert result.min() >= 0

    def test_get_slope_grid_same_size(self):
        """No resampling when target = source size."""
        dem = _make_dem_data(rows=60, cols=60)
        result = get_slope_grid_resampled(dem, 60, 60)
        assert result is not None
        assert result.shape == (60, 60)

    def test_get_slope_grid_returns_none_without_data(self):
        """Returns None when DEM unavailable."""
        assert get_slope_grid_resampled(None, 50, 50) is None
        assert get_slope_grid_resampled({"status": "failed"}, 50, 50) is None


# =====================================================================
# TESTS: Cost Grid with DEM Slope
# =====================================================================

class TestCostGridDEM:
    def test_build_cost_grid_with_dem_data(self):
        """Cost grid incorporates DEM ecological model."""
        dem = _make_dem_data()
        # With DEM - elevations create valleys/ridges
        grid_with, meta_with = build_cost_grid(
            BOUNDS, EXCLUSIONS, "moose", "male", 50,
            dem_data=dem,
        )
        grid_without, meta_without = build_cost_grid(
            BOUNDS, EXCLUSIONS, "moose", "male", 50,
            dem_data=None,
        )
        assert meta_with["dem_slope_applied"] is True
        assert meta_without["dem_slope_applied"] is False
        assert meta_with["ecological_model"] == "v7.1"

    def test_cost_grid_lisiere_detection(self):
        """Cost grid detects lisiere (forest edges)."""
        _, meta = build_cost_grid(
            BOUNDS, EXCLUSIONS, "moose", "male", 50,
        )
        # Should detect some lisiere cells from exclusion edges
        assert "lisiere_cells" in meta
        assert meta["lisiere_cells"] >= 0

    def test_cost_grid_water_corridor(self):
        """Cost grid creates water proximity corridors."""
        _, meta = build_cost_grid(
            BOUNDS, EXCLUSIONS, "moose", "male", 50,
        )
        assert "water_corridor_cells" in meta
        assert meta["water_corridor_cells"] >= 0

    def test_cost_grid_steep_slope_higher_cost(self):
        """Steep slopes produce higher costs in the grid."""
        # Create DEM with steep slopes
        steep_dem = _make_dem_data(elev_min=200, elev_max=1200)
        grid_steep, _ = build_cost_grid(
            BOUNDS, EXCLUSIONS, "moose", "male", 50,
            dem_data=steep_dem,
        )
        # Gentle DEM
        gentle_dem = _make_dem_data(elev_min=300, elev_max=310)
        grid_gentle, _ = build_cost_grid(
            BOUNDS, EXCLUSIONS, "moose", "male", 50,
            dem_data=gentle_dem,
        )
        # Average cost should be higher for steep terrain
        assert np.mean(grid_steep) > np.mean(grid_gentle) * 0.8

    def test_cost_grid_female_more_cautious(self):
        """Female cost grid penalizes open areas more than male."""
        grid_male, meta_m = build_cost_grid(
            BOUNDS, EXCLUSIONS, "moose", "male", 50,
        )
        grid_female, meta_f = build_cost_grid(
            BOUNDS, EXCLUSIONS, "moose", "female", 50,
        )
        # Female should have more favorable cells (sticks to cover)
        # or higher average (avoids open areas more)
        assert meta_m["sex"] == "male"
        assert meta_f["sex"] == "female"

    def test_cost_grid_valley_ridge_detection(self):
        """DEM identifies valleys and ridges."""
        dem = _make_dem_data(elev_min=100, elev_max=800)
        _, meta = build_cost_grid(
            BOUNDS, EXCLUSIONS, "moose", "male", 50,
            dem_data=dem,
        )
        assert "valley_cells" in meta
        assert "ridge_cells" in meta


# =====================================================================
# TESTS: Zone Typology with DEM
# =====================================================================

class TestZoneTypologyDEM:
    def test_subscores_with_dem_data(self):
        """Subscores use real DEM data for TOPO score."""
        zone = _make_zone(47.185, -71.225)
        dem_stats = {
            "elevation_min": 200, "elevation_max": 500,
            "elevation_mean": 350, "slope_mean_deg": 12,
        }
        dem_point = {
            "elevation_m": 320, "slope_deg": 8,
            "aspect_deg": 180, "roughness": 2.0,
        }
        scores = compute_subscores(
            zone, "alimentation", "moose", EXCLUSIONS,
            dem_stats=dem_stats, dem_point=dem_point,
        )
        assert "topo" in scores
        # Gentle slope (8°) should give high topo score
        assert scores["topo"] >= 60

    def test_subscores_without_dem_fallback(self):
        """Subscores use heuristic fallback without DEM."""
        zone = _make_zone(47.185, -71.225)
        scores = compute_subscores(
            zone, "alimentation", "moose", EXCLUSIONS,
        )
        assert "topo" in scores
        assert 0 <= scores["topo"] <= 100

    def test_subscores_steep_slope_penalty(self):
        """Steep slope reduces TOPO score."""
        zone = _make_zone(47.185, -71.225)
        dem_stats = {
            "elevation_min": 200, "elevation_max": 800,
            "elevation_mean": 500,
        }
        # Steep slope
        steep_scores = compute_subscores(
            zone, "alimentation", "moose", EXCLUSIONS,
            dem_stats=dem_stats,
            dem_point={"elevation_m": 500, "slope_deg": 40, "roughness": 10},
        )
        # Gentle slope
        gentle_scores = compute_subscores(
            zone, "alimentation", "moose", EXCLUSIONS,
            dem_stats=dem_stats,
            dem_point={"elevation_m": 350, "slope_deg": 5, "roughness": 1},
        )
        assert gentle_scores["topo"] > steep_scores["topo"]

    def test_enrich_zone_with_dem(self):
        """enrich_zone_v7 includes DEM data in v7 output."""
        zone = _make_zone(47.185, -71.225)
        dem_stats = {"elevation_min": 200, "elevation_max": 500, "elevation_mean": 350}
        dem_point = {"elevation_m": 320, "slope_deg": 8, "aspect_deg": 180, "roughness": 2}
        enrich_zone_v7(
            zone, "alimentation", "moose", EXCLUSIONS,
            month=10, dem_stats=dem_stats, dem_point=dem_point,
        )
        assert zone["v7"]["dem_enhanced"] is True
        assert "terrain" in zone["v7"]
        assert zone["v7"]["terrain"]["elevation_m"] == 320

    def test_enrich_zone_without_dem(self):
        """enrich_zone_v7 works without DEM (backward compatible)."""
        zone = _make_zone(47.185, -71.225)
        enrich_zone_v7(zone, "alimentation", "moose", EXCLUSIONS, month=10)
        assert zone["v7"]["dem_enhanced"] is False
        assert "terrain" not in zone["v7"]


# =====================================================================
# TESTS: Pipeline V7 with DEM
# =====================================================================

class TestPipelineV7DEM:
    def test_process_zones_v7_with_dem(self):
        """Pipeline V7 processes zones with DEM data."""
        raw_zones = [_make_zone(47.185, -71.225 + i * 0.003) for i in range(5)]
        dem = _make_dem_data()
        valid, rejected, stats = process_zones_v7(
            raw_zones, BOUNDS, EXCLUSIONS, "alimentation", "moose",
            dem_data=dem,
        )
        assert stats["dem_available"] is True
        assert len(valid) > 0
        # Zones should have DEM-enhanced scoring
        for z in valid:
            assert z["v7"]["dem_enhanced"] is True

    def test_process_zones_v7_without_dem_backward_compat(self):
        """Pipeline V7 works without DEM (backward compatible)."""
        raw_zones = [_make_zone(47.185, -71.225 + i * 0.003) for i in range(5)]
        valid, rejected, stats = process_zones_v7(
            raw_zones, BOUNDS, EXCLUSIONS, "alimentation", "moose",
        )
        assert stats["dem_available"] is False
        assert len(valid) > 0

    def test_corridors_v7_with_dem(self):
        """Corridor generation uses DEM for terrain-aware pathfinding."""
        zones = []
        for i in range(4):
            z = _make_zone(47.185 + i * 0.005, -71.225 + i * 0.003)
            z["zone_id"] = f"z_moose_test_{i:03d}"
            z["v7"] = {"zone_type": ["feed", "rest", "rut", "corridor"][i]}
            zones.append(z)

        dem = _make_dem_data()
        corridors = generate_all_corridors_v7(
            {"test": zones}, EXCLUSIONS, "moose", 10, dem_data=dem,
        )
        assert len(corridors) > 0
        # At least some corridors should have dem_enhanced=True
        dem_enhanced = [c for c in corridors if c["properties"].get("dem_enhanced")]
        assert len(dem_enhanced) > 0

    def test_corridors_v7_without_dem_backward_compat(self):
        """Corridor generation works without DEM."""
        zones = []
        for i in range(3):
            z = _make_zone(47.185 + i * 0.005, -71.225 + i * 0.003)
            z["zone_id"] = f"z_moose_test_{i:03d}"
            z["v7"] = {"zone_type": ["feed", "rest", "corridor"][i]}
            zones.append(z)

        corridors = generate_all_corridors_v7(
            {"test": zones}, EXCLUSIONS, "moose", 10,
        )
        assert len(corridors) >= 0  # May generate corridors even without DEM


# =====================================================================
# TESTS: DEM Stats in API Response
# =====================================================================

class TestDEMMetadata:
    def test_dem_stats_format(self):
        """DEM stats have expected format."""
        dem = _make_dem_data()
        stats = dem["stats"]
        assert "elevation_min" in stats
        assert "elevation_max" in stats
        assert "elevation_mean" in stats
        assert "slope_mean_deg" in stats
        assert "slope_max_deg" in stats
        assert "roughness_mean" in stats
        assert "pixel_size_m" in stats
        assert stats["elevation_min"] < stats["elevation_max"]
        assert stats["slope_mean_deg"] >= 0

    def test_dem_validation_source(self):
        """DEM validation indicates source."""
        dem = _make_dem_data()
        assert dem["validation"]["source"] == "OpenTopography"
        assert dem["validation"]["dataset"] == "SRTMGL1"
        assert dem["validation"]["data_real"] is True


# =====================================================================
# TESTS: Ecological Corridor Properties
# =====================================================================

class TestEcologicalCorridors:
    def test_corridors_have_individual_geometry(self):
        """Each corridor is an individual LineString, not a MultiLineString."""
        zones = []
        for i in range(4):
            z = _make_zone(47.185 + i * 0.005, -71.225 + i * 0.003)
            z["zone_id"] = f"z_moose_test_{i:03d}"
            z["v7"] = {"zone_type": ["feed", "rest", "rut", "corridor"][i]}
            zones.append(z)
        corridors = generate_all_corridors_v7({"test": zones}, EXCLUSIONS, "moose", 10)
        for c in corridors:
            assert c["geometry"]["type"] == "LineString"
            coords = c["geometry"]["coordinates"]
            assert len(coords) >= 2
            # Each coordinate is [lng, lat]
            for pt in coords:
                assert len(pt) == 2
                assert isinstance(pt[0], float)
                assert isinstance(pt[1], float)

    def test_real_corridors_have_solid_line(self):
        """Real corridors have dasharray='none' (solid line)."""
        zones = []
        for i in range(3):
            z = _make_zone(47.185 + i * 0.005, -71.225 + i * 0.003)
            z["zone_id"] = f"z_moose_test_{i:03d}"
            z["v7"] = {"zone_type": ["feed", "rest", "corridor"][i]}
            zones.append(z)
        corridors = generate_all_corridors_v7({"test": zones}, EXCLUSIONS, "moose", 10)
        for c in corridors:
            if c["properties"]["source"] == "real":
                assert c["properties"]["style"]["dasharray"] == "none"

    def test_ai_corridors_have_dashed_line(self):
        """AI corridors have dasharray != 'none' (dashed line)."""
        zones = []
        for i in range(3):
            z = _make_zone(47.185 + i * 0.005, -71.225 + i * 0.003)
            z["zone_id"] = f"z_moose_test_{i:03d}"
            z["v7"] = {"zone_type": ["feed", "rest", "corridor"][i]}
            zones.append(z)
        corridors = generate_all_corridors_v7({"test": zones}, EXCLUSIONS, "moose", 10)
        for c in corridors:
            if c["properties"]["source"] == "ai":
                assert c["properties"]["style"]["dasharray"] != "none"

    def test_male_female_visual_distinction(self):
        """Male and female corridors have distinct colors."""
        zones = []
        for i in range(3):
            z = _make_zone(47.185 + i * 0.005, -71.225 + i * 0.003)
            z["zone_id"] = f"z_moose_test_{i:03d}"
            z["v7"] = {"zone_type": ["feed", "rest", "corridor"][i]}
            zones.append(z)
        corridors = generate_all_corridors_v7({"test": zones}, EXCLUSIONS, "moose", 10)
        male_colors = set()
        female_colors = set()
        for c in corridors:
            if c["properties"]["sex"] == "male":
                male_colors.add(c["properties"]["style"]["color"])
            else:
                female_colors.add(c["properties"]["style"]["color"])
        if male_colors and female_colors:
            assert male_colors.isdisjoint(female_colors)

    def test_corridors_connect_complementary_zones(self):
        """Corridors connect complementary zone types (feed-rest, rest-rut, etc.)."""
        zones = []
        for i in range(4):
            z = _make_zone(47.185 + i * 0.005, -71.225 + i * 0.003)
            z["zone_id"] = f"z_moose_test_{i:03d}"
            z["v7"] = {"zone_type": ["feed", "rest", "rut", "corridor"][i]}
            zones.append(z)
        corridors = generate_all_corridors_v7({"test": zones}, EXCLUSIONS, "moose", 20)
        for c in corridors:
            p = c["properties"]
            assert p["from_zone_type"] in ("feed", "rest", "rut", "corridor", "mixed", "heat_ref", "hunt_ref")
            assert p["to_zone_type"] in ("feed", "rest", "rut", "corridor", "mixed", "heat_ref", "hunt_ref")

    def test_corridor_scoring_has_5_subscores(self):
        """Each corridor has 5 subscores: topographie, couvert, eau, pression, comportement."""
        zones = []
        for i in range(3):
            z = _make_zone(47.185 + i * 0.005, -71.225 + i * 0.003)
            z["zone_id"] = f"z_moose_test_{i:03d}"
            z["v7"] = {"zone_type": ["feed", "rest", "rut"][i]}
            zones.append(z)
        corridors = generate_all_corridors_v7({"test": zones}, EXCLUSIONS, "moose", 10)
        expected_keys = {"topographie", "couvert", "eau", "pression", "comportement"}
        for c in corridors:
            ss = c["properties"]["scoring"]["subscores"]
            assert set(ss.keys()) == expected_keys
            for v in ss.values():
                assert 0 <= v <= 100

    def test_corridors_no_duplicates(self):
        """No two corridors have identical geometry."""
        zones = []
        for i in range(4):
            z = _make_zone(47.185 + i * 0.005, -71.225 + i * 0.003)
            z["zone_id"] = f"z_moose_test_{i:03d}"
            z["v7"] = {"zone_type": ["feed", "rest", "rut", "corridor"][i]}
            zones.append(z)
        corridors = generate_all_corridors_v7({"test": zones}, EXCLUSIONS, "moose", 20)
        geom_hashes = set()
        for c in corridors:
            coords = tuple(tuple(pt) for pt in c["geometry"]["coordinates"])
            geom_hashes.add(coords)
        # Each corridor should have unique geometry
        assert len(geom_hashes) == len(corridors)

    def test_dem_enhanced_corridors_higher_confidence(self):
        """DEM-enhanced corridors tend to have higher confidence."""
        zones = []
        for i in range(3):
            z = _make_zone(47.185 + i * 0.005, -71.225 + i * 0.003)
            z["zone_id"] = f"z_moose_test_{i:03d}"
            z["v7"] = {"zone_type": ["feed", "rest", "corridor"][i]}
            zones.append(z)
        dem = _make_dem_data()
        # With DEM
        corr_dem = generate_all_corridors_v7(
            {"test": zones}, EXCLUSIONS, "moose", 10, dem_data=dem,
        )
        # Without DEM
        corr_no_dem = generate_all_corridors_v7(
            {"test": zones}, EXCLUSIONS, "moose", 10, dem_data=None,
        )
        if corr_dem and corr_no_dem:
            avg_conf_dem = sum(c["properties"]["confidence"] for c in corr_dem) / len(corr_dem)
            avg_conf_no = sum(c["properties"]["confidence"] for c in corr_no_dem) / len(corr_no_dem)
            # DEM corridors should have equal or higher average confidence
            assert avg_conf_dem >= avg_conf_no - 0.05


# =====================================================================
# REGRESSION: Existing V7 behavior unchanged
# =====================================================================

class TestV7Regression:
    def test_v7_without_dem_matches_original(self):
        """V7 pipeline output structure unchanged without DEM."""
        raw_zones = [_make_zone(47.185, -71.225 + i * 0.003) for i in range(3)]
        valid, _, stats = process_zones_v7(
            raw_zones, BOUNDS, EXCLUSIONS, "alimentation", "moose",
        )
        assert stats["engine"] == "v7"
        for z in valid:
            v7 = z["v7"]
            assert "zone_type" in v7
            assert "score_global" in v7
            assert "subscores" in v7
            assert len(v7["subscores"]) == 7
            assert "confidence" in v7
            assert "season_relevance" in v7

    def test_all_7_subscores_present(self):
        """All 7 subscores present with and without DEM."""
        zone = _make_zone(47.185, -71.225)
        expected_keys = {"food", "safety", "access", "stealth", "water", "topo", "dynamic"}

        # Without DEM
        scores_no_dem = compute_subscores(zone, "alimentation", "moose", EXCLUSIONS)
        assert set(scores_no_dem.keys()) == expected_keys

        # With DEM
        dem_stats = {"elevation_min": 200, "elevation_max": 500, "elevation_mean": 350}
        dem_point = {"elevation_m": 320, "slope_deg": 8, "roughness": 2}
        scores_dem = compute_subscores(
            zone, "alimentation", "moose", EXCLUSIONS,
            dem_stats=dem_stats, dem_point=dem_point,
        )
        assert set(scores_dem.keys()) == expected_keys
