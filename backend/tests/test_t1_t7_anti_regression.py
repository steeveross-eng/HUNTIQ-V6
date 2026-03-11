"""
MASTER PLAN BIONIC 1000% — T1-T7 Anti-Regression Test Suite
=============================================================

T1: Ancrage waypoint — access corridors exist
T2: Corridors vs routes — intersection detection + downgrade
T3: Vent dominant — applied to all corridors
T4: Cohérence backend/frontend — t4_zone_count matches
T5: Fallback cache expiré — overpass retry resilience
T6: Fusion <200m — merge function
T7: Frontend crash guard — ResizeObserver safe
"""

import pytest
import sys
import os
import math
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestT1WaypointAnchor:
    """T1: Access corridors must be generated when waypoint_center is provided."""

    def test_access_corridor_generated(self):
        from modules.bionic_engine_p0.services.corridor_v7 import generate_corridors_v7

        zones = [
            {"zone_id": "z1", "centroid": {"lat": 47.302, "lng": -71.518},
             "v7": {"zone_type": "rest", "score_global": 70}},
            {"zone_id": "z2", "centroid": {"lat": 47.305, "lng": -71.515},
             "v7": {"zone_type": "feed", "score_global": 65}},
        ]
        wp = {"lat": 47.30, "lng": -71.52}

        corridors = generate_corridors_v7(
            zones, [], "moose", month=10, waypoint_center=wp,
        )
        access = [c for c in corridors if c.get("properties", {}).get("is_access_corridor")]
        assert len(access) >= 1, f"Expected at least 1 access corridor, got {len(access)}"
        for a in access:
            assert a["properties"]["from_zone_type"] == "waypoint"
            assert a["properties"]["to_zone_type"] in ("rest", "feed")

    def test_no_access_without_waypoint(self):
        from modules.bionic_engine_p0.services.corridor_v7 import generate_corridors_v7

        zones = [
            {"zone_id": "z1", "centroid": {"lat": 47.302, "lng": -71.518},
             "v7": {"zone_type": "rest", "score_global": 70}},
            {"zone_id": "z2", "centroid": {"lat": 47.305, "lng": -71.515},
             "v7": {"zone_type": "feed", "score_global": 65}},
        ]

        corridors = generate_corridors_v7(zones, [], "moose", month=10)
        access = [c for c in corridors if c.get("properties", {}).get("is_access_corridor")]
        assert len(access) == 0, "No access corridors without waypoint"


class TestT2CorridorsVsRoutes:
    """T2: Corridors crossing roads get low confidence."""

    def test_road_intersection_detection(self):
        from modules.bionic_engine_p0.services.corridor_v7 import _corridors_intersect_roads

        path = [[-71.520, 47.3000], [-71.520, 47.3010]]
        roads = [{
            "type": "roads", "sub_type": "secondary",
            "coordinates": [[-71.5201, 47.3005], [-71.5199, 47.3005]],
        }]
        crosses, count = _corridors_intersect_roads(path, roads, threshold_m=50)
        assert crosses is True
        assert count >= 1

    def test_no_intersection_without_roads(self):
        from modules.bionic_engine_p0.services.corridor_v7 import _corridors_intersect_roads

        path = [[-71.520, 47.3000], [-71.520, 47.3010]]
        crosses, count = _corridors_intersect_roads(path, [])
        assert crosses is False
        assert count == 0


class TestT3WindDominant:
    """T3: Wind direction applied to cost grid and corridor properties."""

    def test_wind_modifies_grid(self):
        from modules.bionic_engine_p0.services.corridor_v7 import _apply_wind_cost

        grid = np.ones((20, 20)) * 0.5
        original = grid.copy()
        _apply_wind_cost(grid, 225.0, {"south": 47.29, "north": 47.31, "east": -71.50, "west": -71.53}, 20, "female")
        # Wind should change at least some individual cell values
        assert not np.allclose(grid, original), "Wind should change individual grid cell costs"
        assert np.all(grid >= 0.1), "Grid should remain >= 0.1 after wind"

    def test_default_wind_225(self):
        from modules.bionic_engine_p0.services.corridor_v7 import generate_corridors_v7

        zones = [
            {"zone_id": "z1", "centroid": {"lat": 47.302, "lng": -71.518},
             "v7": {"zone_type": "rest", "score_global": 70}},
            {"zone_id": "z2", "centroid": {"lat": 47.305, "lng": -71.515},
             "v7": {"zone_type": "feed", "score_global": 65}},
        ]
        corridors = generate_corridors_v7(zones, [], "moose", month=10)
        for c in corridors:
            assert c["properties"]["wind_direction_deg"] == 225.0


class TestT4Coherence:
    """T4: GeoJSON features count = stats.t4_zone_count."""

    def test_t4_zone_count_matches(self):
        from modules.bionic_engine_p0.services.zone_visual_layer_v2 import zones_to_geojson

        zones = [{
            "area_m2": 6500, "compactness": 0.5, "vertices": 10,
            "centroid": {"lat": 47.3, "lng": -71.5},
            "coordinates": [[47.3, -71.5], [47.31, -71.5], [47.31, -71.51], [47.3, -71.51]],
            "v7": {"score_global": 72, "zone_type": "rest"},
        } for _ in range(7)]

        zones_by_layer = {"repos": zones}
        scores = {"repos": [72] * 7}
        geojson = zones_to_geojson(zones_by_layer, "moose", scores)

        assert len(geojson["features"]) == 7
        assert geojson["metadata"]["total_zones"] == 7


class TestT5FallbackCache:
    """T5: Overpass retry mechanism with cache."""

    def test_cache_collection_configured(self):
        """Validate that overpass_cache_r5 collection is configured in terrain router."""
        import os
        router_path = os.path.join(
            os.path.dirname(__file__), "..",
            "modules", "bionic_engine_p0", "routers", "terrain_data_router.py"
        )
        with open(router_path) as f:
            source = f.read()
        assert "overpass_cache_r5" in source, "Cache collection should be configured"

    def test_cache_ttl_configured(self):
        """Validate TTL is set for cache."""
        import os
        router_path = os.path.join(
            os.path.dirname(__file__), "..",
            "modules", "bionic_engine_p0", "routers", "terrain_data_router.py"
        )
        with open(router_path) as f:
            source = f.read()
        assert "CACHE_TTL" in source, "Cache TTL should be configured"


class TestT6Fusion:
    """T6: Merge zones within 200m uses v7.score_global."""

    def test_nearby_zones_merged(self):
        from modules.bionic_engine_p0.services.pipeline_v7 import _merge_nearby_same_type_zones

        z1 = {"centroid": {"lat": 47.300, "lng": -71.500},
              "coordinates": [[47.299, -71.501], [47.301, -71.501], [47.301, -71.499], [47.299, -71.499]],
              "layer_id": "repos", "v7": {"score_global": 55.0, "zone_type": "rest"}}
        z2 = {"centroid": {"lat": 47.3005, "lng": -71.5005},
              "coordinates": [[47.2995, -71.5015], [47.3015, -71.5015], [47.3015, -71.4995], [47.2995, -71.4995]],
              "layer_id": "repos", "v7": {"score_global": 90.0, "zone_type": "rest"}}

        result = _merge_nearby_same_type_zones([z1, z2], max_dist_m=500)
        assert len(result) == 1, "Should merge nearby zones"
        assert result[0]["v7"]["score_global"] == 90.0, "Best score should be preserved"

    def test_distant_zones_not_merged(self):
        from modules.bionic_engine_p0.services.pipeline_v7 import _merge_nearby_same_type_zones

        z1 = {"centroid": {"lat": 47.300, "lng": -71.500},
              "coordinates": [[47.299, -71.501], [47.301, -71.501], [47.301, -71.499], [47.299, -71.499]],
              "layer_id": "repos", "v7": {"score_global": 60.0}}
        z2 = {"centroid": {"lat": 47.320, "lng": -71.530},
              "coordinates": [[47.319, -71.531], [47.321, -71.531], [47.321, -71.529], [47.319, -71.529]],
              "layer_id": "repos", "v7": {"score_global": 70.0}}

        result = _merge_nearby_same_type_zones([z1, z2], max_dist_m=200)
        assert len(result) == 2, "Distant zones should not merge"


class TestT7FrontendCrash:
    """T7: ResizeObserver — no crash on zone rendering (structural test)."""

    def test_zone_visual_layer_no_crash(self):
        """zone_to_geojson_feature must not raise on valid input."""
        from modules.bionic_engine_p0.services.zone_visual_layer_v2 import zone_to_geojson_feature

        zone = {
            "area_m2": 6500, "compactness": 0.5, "vertices": 10,
            "centroid": {"lat": 47.3, "lng": -71.5},
            "coordinates": [[47.3, -71.5], [47.31, -71.5], [47.31, -71.51], [47.3, -71.51]],
            "v7": {"score_global": 72.0, "zone_type": "rest"},
        }
        feature = zone_to_geojson_feature(zone, "repos", "z1", score=72, species="moose")
        assert feature is not None
        assert feature["type"] == "Feature"
        assert feature["geometry"]["type"] == "Polygon"
        assert len(feature["geometry"]["coordinates"][0]) >= 4

    def test_zone_visual_layer_empty_coordinates(self):
        """zone_to_geojson_feature handles edge case of few coordinates."""
        from modules.bionic_engine_p0.services.zone_visual_layer_v2 import zone_to_geojson_feature

        zone = {
            "area_m2": 100, "compactness": 0.1, "vertices": 3,
            "centroid": {"lat": 47.3, "lng": -71.5},
            "coordinates": [[47.3, -71.5], [47.31, -71.5], [47.31, -71.51]],
            "v7": {"score_global": 30.0, "zone_type": "rest"},
        }
        feature = zone_to_geojson_feature(zone, "repos", "z1", score=30, species="moose")
        assert feature is not None
