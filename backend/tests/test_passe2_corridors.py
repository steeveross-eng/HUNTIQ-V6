"""
MASTER PLAN BIONIC 1000% — Passe 2 Anti-Regression Tests
=========================================================

Tests:
  T-C4: A* finds passable cells when centroids are impassable
  T-C5: Waypoint access corridors are generated
  T-C6: Road intersection detection works
  T-C7: Duplicate male/female corridors are eliminated
  T-C8: Wind direction is applied to cost grid
"""

import pytest
import sys
import os
import math
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestC4PassableCells:
    """C4 (BUG-02): A* must snap impassable centroids to nearest passable."""

    def test_find_nearest_passable_cell_on_passable(self):
        from modules.bionic_engine_p0.services.corridor_v7 import _find_nearest_passable_cell
        from modules.bionic_engine_p0.services.trail_cost_grid_v7 import IMPASSABLE

        grid = np.ones((10, 10)) * 0.5
        result = _find_nearest_passable_cell(grid, (5, 5))
        assert result == (5, 5), "Passable cell should return itself"

    def test_find_nearest_passable_cell_on_impassable(self):
        from modules.bionic_engine_p0.services.corridor_v7 import _find_nearest_passable_cell
        from modules.bionic_engine_p0.services.trail_cost_grid_v7 import IMPASSABLE

        grid = np.ones((10, 10)) * 0.5
        grid[5, 5] = IMPASSABLE
        result = _find_nearest_passable_cell(grid, (5, 5))
        assert result is not None, "Should find a nearby passable cell"
        assert result != (5, 5), "Should not return the impassable cell"
        assert grid[result[0], result[1]] < IMPASSABLE * 0.9

    def test_find_nearest_passable_cell_all_impassable(self):
        from modules.bionic_engine_p0.services.corridor_v7 import _find_nearest_passable_cell
        from modules.bionic_engine_p0.services.trail_cost_grid_v7 import IMPASSABLE

        grid = np.ones((10, 10)) * IMPASSABLE
        result = _find_nearest_passable_cell(grid, (5, 5), max_radius=3)
        assert result is None, "Should return None when all cells are impassable"

    def test_astar_with_impassable_start(self):
        from modules.bionic_engine_p0.services.corridor_v7 import _astar
        from modules.bionic_engine_p0.services.trail_cost_grid_v7 import IMPASSABLE

        grid = np.ones((20, 20)) * 0.5
        grid[2, 2] = IMPASSABLE
        path = _astar(grid, (2, 2), (15, 15))
        assert path is not None, "A* should find a path even with impassable start (via snap)"
        assert len(path) > 2


class TestC5WaypointAccess:
    """C5 (BUG-03): Waypoint access corridors generated."""

    def test_generate_waypoint_access(self):
        from modules.bionic_engine_p0.services.corridor_v7 import _generate_waypoint_access
        from modules.bionic_engine_p0.services.trail_cost_grid_v7 import build_cost_grid

        waypoint = {"lat": 47.30, "lng": -71.52}
        zones = [
            {
                "zone_id": "z1",
                "centroid": {"lat": 47.302, "lng": -71.518},
                "v7": {"zone_type": "rest", "score_global": 70},
            },
            {
                "zone_id": "z2",
                "centroid": {"lat": 47.305, "lng": -71.515},
                "v7": {"zone_type": "feed", "score_global": 65},
            },
        ]
        bounds = {"south": 47.29, "north": 47.31, "east": -71.50, "west": -71.53}
        grid_size = 30

        grids = {}
        grid_meta = {}
        for sex in ("male", "female"):
            grids[sex], grid_meta[sex] = build_cost_grid(
                bounds, [], "moose", sex, grid_size
            )

        result = _generate_waypoint_access(
            waypoint, zones, [], "moose", grids, bounds, grid_size,
            grid_meta, {}, False, 10, 225.0,
        )
        assert len(result) >= 1, "At least 1 access corridor should be generated"
        for c in result:
            props = c.get("properties", {})
            assert props.get("is_access_corridor") is True
            assert props.get("from_zone_type") == "waypoint"
            assert props.get("to_zone_type") in ("rest", "feed")


class TestC6RouteValidation:
    """C6 (IC2): Corridor-route intersection detection."""

    def test_no_roads_no_intersection(self):
        from modules.bionic_engine_p0.services.corridor_v7 import _corridors_intersect_roads

        path = [[-71.52, 47.30], [-71.51, 47.31]]
        crosses, count = _corridors_intersect_roads(path, [])
        assert not crosses
        assert count == 0

    def test_crossing_road(self):
        from modules.bionic_engine_p0.services.corridor_v7 import _corridors_intersect_roads

        path = [[-71.52, 47.300], [-71.52, 47.301]]
        exclusions = [{
            "type": "roads",
            "sub_type": "secondary",
            "coordinates": [[-71.5201, 47.3005], [-71.5199, 47.3005]],
            "geometry_type": "line",
        }]
        crosses, count = _corridors_intersect_roads(path, exclusions, threshold_m=50)
        assert crosses, "Should detect road crossing"
        assert count >= 1

    def test_tracks_ignored(self):
        from modules.bionic_engine_p0.services.corridor_v7 import _corridors_intersect_roads

        path = [[-71.52, 47.300], [-71.52, 47.301]]
        exclusions = [{
            "type": "roads",
            "sub_type": "track",
            "coordinates": [[-71.5201, 47.3005], [-71.5199, 47.3005]],
            "geometry_type": "line",
        }]
        crosses, _ = _corridors_intersect_roads(path, exclusions, threshold_m=50)
        assert not crosses, "Tracks should be ignored"


class TestC7Deduplication:
    """C7 (BUG-05): Male/female duplicate elimination."""

    def test_identical_corridors_deduplicated(self):
        from modules.bionic_engine_p0.services.corridor_v7 import _deduplicate_corridors

        base_coords = [[-71.52, 47.30], [-71.51, 47.31], [-71.505, 47.315]]
        corridors = [
            {
                "id": "trail_m_000",
                "geometry": {"type": "LineString", "coordinates": base_coords},
                "properties": {
                    "sex": "male", "confidence": 0.85,
                    "from_zone_id": "z1", "to_zone_id": "z2",
                },
            },
            {
                "id": "trail_f_001",
                "geometry": {"type": "LineString", "coordinates": base_coords},
                "properties": {
                    "sex": "female", "confidence": 0.75,
                    "from_zone_id": "z1", "to_zone_id": "z2",
                },
            },
        ]
        result = _deduplicate_corridors(corridors, min_dist_m=5.0)
        assert len(result) == 1, "Identical corridors should be deduplicated"
        assert result[0]["id"] == "trail_m_000", "Higher confidence should be kept"

    def test_different_corridors_kept(self):
        from modules.bionic_engine_p0.services.corridor_v7 import _deduplicate_corridors

        corridors = [
            {
                "id": "trail_m_000",
                "geometry": {"type": "LineString", "coordinates": [[-71.52, 47.30], [-71.51, 47.31]]},
                "properties": {
                    "sex": "male", "confidence": 0.85,
                    "from_zone_id": "z1", "to_zone_id": "z2",
                },
            },
            {
                "id": "trail_f_001",
                "geometry": {"type": "LineString", "coordinates": [[-71.53, 47.30], [-71.515, 47.305]]},
                "properties": {
                    "sex": "female", "confidence": 0.75,
                    "from_zone_id": "z1", "to_zone_id": "z2",
                },
            },
        ]
        result = _deduplicate_corridors(corridors, min_dist_m=5.0)
        assert len(result) == 2, "Different corridors should be kept"


class TestC8Wind:
    """C8 (IM2): Wind direction modifies cost grid."""

    def test_wind_applied_to_grid(self):
        from modules.bionic_engine_p0.services.corridor_v7 import _apply_wind_cost

        grid = np.ones((20, 20)) * 0.5
        original = grid.copy()
        bounds = {"south": 47.29, "north": 47.31, "east": -71.50, "west": -71.53}

        _apply_wind_cost(grid, 225.0, bounds, 20, "male")
        assert not np.array_equal(grid, original), "Wind should modify the grid"
        assert np.all(grid >= 0.1), "Grid should remain >= 0.1 after wind"

    def test_wind_default_direction(self):
        from modules.bionic_engine_p0.services.corridor_v7 import generate_corridors_v7

        zones = [
            {"zone_id": "z1", "centroid": {"lat": 47.30, "lng": -71.52},
             "v7": {"zone_type": "rest", "score_global": 70}},
            {"zone_id": "z2", "centroid": {"lat": 47.305, "lng": -71.515},
             "v7": {"zone_type": "feed", "score_global": 65}},
        ]
        corridors = generate_corridors_v7(zones, [], "moose", month=10)
        if corridors:
            for c in corridors:
                assert c["properties"].get("wind_direction_deg") == 225.0
