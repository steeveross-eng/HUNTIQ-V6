"""
MASTER PLAN BIONIC 1000% — Passe 1 Anti-Regression Tests
=========================================================

Tests:
  T-BUG04: score = score_display = int(score_global) for all V7 zones
  T-T4:    geojson.features count = stats.t4_zone_count
  T-BUG01: Classification is based on layer_id (feed/rut/rest)
  T-MERGE: Merge function selects best zone by v7.score_global
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestBUG04ScoringCoherence:
    """BUG-04: score = score_display = int(score_global) V7."""

    def test_zone_to_geojson_feature_v7_score(self):
        """score and score_display must equal int(score_global)."""
        from modules.bionic_engine_p0.services.zone_visual_layer_v2 import zone_to_geojson_feature

        zone = {
            "area_m2": 6500,
            "compactness": 0.5,
            "vertices": 10,
            "centroid": {"lat": 47.3, "lng": -71.5},
            "coordinates": [[47.3, -71.5], [47.31, -71.5], [47.31, -71.51], [47.3, -71.51]],
            "v7": {
                "zone_type": "rest",
                "zone_type_label": "Zone de repos",
                "zone_type_color": "#8B5CF6",
                "score_global": 72.8,
                "score_raw": 65.0,
                "subscores": {},
                "confidence": 0.85,
                "season_relevance": {},
            },
        }

        feature = zone_to_geojson_feature(zone, "repos", "z1", score=999, species="moose")
        props = feature["properties"]

        expected = max(25, int(72.8))
        assert props["score"] == expected, f"score={props['score']} != {expected}"
        assert props["score_display"] == expected, f"score_display={props['score_display']} != {expected}"
        assert props["score_global"] == 72.8

    def test_zone_to_geojson_feature_v5_fallback(self):
        """Without v7 data, score should be the passed-in value."""
        from modules.bionic_engine_p0.services.zone_visual_layer_v2 import zone_to_geojson_feature

        zone = {
            "area_m2": 6500,
            "compactness": 0.5,
            "vertices": 10,
            "centroid": {"lat": 47.3, "lng": -71.5},
            "coordinates": [[47.3, -71.5], [47.31, -71.5], [47.31, -71.51], [47.3, -71.51]],
        }

        feature = zone_to_geojson_feature(zone, "habitats", "z1", score=65, species="moose")
        props = feature["properties"]

        assert props["score"] == 65
        assert props["score_display"] == 65

    def test_v7_score_no_double_penalization(self):
        """V7 scoring path: layer_scores must use score_global directly."""
        from modules.bionic_engine_p0.services.zone_visual_layer_v2 import zones_to_geojson

        zones_by_layer = {
            "repos": [
                {
                    "area_m2": 7000,
                    "compactness": 0.6,
                    "vertices": 12,
                    "centroid": {"lat": 47.3, "lng": -71.5},
                    "coordinates": [[47.3, -71.5], [47.31, -71.5], [47.31, -71.51], [47.3, -71.51]],
                    "v7": {"score_global": 80.5, "score_raw": 72.0, "zone_type": "rest"},
                }
            ]
        }
        scores_by_layer = {"repos": [80]}
        penalties_by_layer = {"repos": [{"factor": 1.0, "raw_score": 72, "details": {}, "v7": {"score_global": 80.5, "score_raw": 72.0, "zone_type": "rest"}}]}

        geojson = zones_to_geojson(zones_by_layer, "moose", scores_by_layer, penalties_by_layer)
        feature = geojson["features"][0]
        props = feature["properties"]

        assert props["score"] == 80, f"score={props['score']} (expected 80 = int(80.5))"
        assert props["score_display"] == 80
        assert props["score_global"] == 80.5


class TestT4Coherence:
    """T4: geojson features count = stats.t4_zone_count."""

    def test_zones_to_geojson_count_matches(self):
        """Number of GeoJSON features must match input zones."""
        from modules.bionic_engine_p0.services.zone_visual_layer_v2 import zones_to_geojson

        zones = [
            {
                "area_m2": 6500 + i * 100,
                "compactness": 0.5,
                "vertices": 10,
                "centroid": {"lat": 47.3 + i * 0.001, "lng": -71.5},
                "coordinates": [[47.3, -71.5], [47.31, -71.5], [47.31, -71.51], [47.3, -71.51]],
                "v7": {"score_global": 60 + i * 5, "zone_type": "rest"},
            }
            for i in range(5)
        ]

        zones_by_layer = {"repos": zones}
        scores = {"repos": [max(25, int(z["v7"]["score_global"])) for z in zones]}

        geojson = zones_to_geojson(zones_by_layer, "moose", scores)
        assert len(geojson["features"]) == 5
        assert geojson["metadata"]["total_zones"] == 5


class TestBUG01Classification:
    """BUG-01: Classification is layer_id-driven."""

    def test_zone_type_from_v7_data(self):
        """Zone type in GeoJSON must come from v7.zone_type."""
        from modules.bionic_engine_p0.services.zone_visual_layer_v2 import zone_to_geojson_feature

        for expected_type in ["feed", "rut", "rest", "mixed"]:
            zone = {
                "area_m2": 6500,
                "compactness": 0.5,
                "vertices": 10,
                "centroid": {"lat": 47.3, "lng": -71.5},
                "coordinates": [[47.3, -71.5], [47.31, -71.5], [47.31, -71.51], [47.3, -71.51]],
                "v7": {"zone_type": expected_type, "score_global": 70.0},
            }
            feature = zone_to_geojson_feature(zone, "alimentation", "z1", score=70, species="moose")
            assert feature["properties"]["zone_type"] == expected_type


class TestMergeFunction:
    """Merge selects best zone by v7.score_global."""

    def test_merge_selects_highest_score(self):
        """Merged zone should have the highest v7.score_global."""
        from modules.bionic_engine_p0.services.pipeline_v7 import _merge_nearby_same_type_zones

        zones = [
            {
                "centroid": {"lat": 47.300, "lng": -71.500},
                "coordinates": [[47.299, -71.501], [47.301, -71.501], [47.301, -71.499], [47.299, -71.499]],
                "layer_id": "repos",
                "v7": {"score_global": 50.0, "zone_type": "rest"},
                "zone_id": "z1",
                "area_m2": 6500,
            },
            {
                "centroid": {"lat": 47.3005, "lng": -71.5005},
                "coordinates": [[47.2995, -71.5015], [47.3015, -71.5015], [47.3015, -71.4995], [47.2995, -71.4995]],
                "layer_id": "repos",
                "v7": {"score_global": 85.0, "zone_type": "rest"},
                "zone_id": "z2",
                "area_m2": 7000,
            },
        ]

        result = _merge_nearby_same_type_zones(zones, max_dist_m=500)
        assert len(result) == 1, f"Expected 1 merged zone, got {len(result)}"
        assert result[0]["v7"]["score_global"] == 85.0, "Merged zone should have highest score"

    def test_no_merge_distant_zones(self):
        """Zones far apart should not be merged."""
        from modules.bionic_engine_p0.services.pipeline_v7 import _merge_nearby_same_type_zones

        zones = [
            {
                "centroid": {"lat": 47.300, "lng": -71.500},
                "coordinates": [[47.299, -71.501], [47.301, -71.501], [47.301, -71.499], [47.299, -71.499]],
                "layer_id": "repos",
                "v7": {"score_global": 60.0, "zone_type": "rest"},
                "zone_id": "z1",
            },
            {
                "centroid": {"lat": 47.310, "lng": -71.510},
                "coordinates": [[47.309, -71.511], [47.311, -71.511], [47.311, -71.509], [47.309, -71.509]],
                "layer_id": "repos",
                "v7": {"score_global": 70.0, "zone_type": "rest"},
                "zone_id": "z2",
            },
        ]

        result = _merge_nearby_same_type_zones(zones, max_dist_m=200)
        assert len(result) == 2, f"Distant zones should not merge, got {len(result)}"
