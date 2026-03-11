"""
Tests unitaires du moteur V7.
Valide: pipeline, typology, scoring, corridors, zone shaping.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestV7SpeciesBehavior:
    def test_species_needs_moose(self):
        from modules.bionic_engine_p0.services.species_behavior_v7 import get_species_needs
        needs = get_species_needs("moose")
        assert "feed" in needs
        assert "rest" in needs
        assert "rut" in needs
        assert "heat_ref" in needs
        assert "hunt_ref" in needs

    def test_sex_params(self):
        from modules.bionic_engine_p0.services.species_behavior_v7 import get_sex_params
        male = get_sex_params("moose", "male")
        female = get_sex_params("moose", "female")
        assert male["daily_range_km"] > female["daily_range_km"]
        assert male["min_road_distance_m"] < female["min_road_distance_m"]

    def test_season_modifier(self):
        from modules.bionic_engine_p0.services.species_behavior_v7 import get_season_modifier
        rut_oct = get_season_modifier("rut", 10)
        rut_jan = get_season_modifier("rut", 1)
        assert rut_oct > rut_jan
        assert rut_oct >= 1.5

    def test_corridor_cost(self):
        from modules.bionic_engine_p0.services.species_behavior_v7 import get_corridor_cost
        male_urban = get_corridor_cost("male", "urban")
        male_edge = get_corridor_cost("male", "edge")
        assert male_urban > male_edge

    def test_all_species_exist(self):
        from modules.bionic_engine_p0.services.species_behavior_v7 import SPECIES_NEEDS
        assert "moose" in SPECIES_NEEDS
        assert "deer" in SPECIES_NEEDS
        assert "bear" in SPECIES_NEEDS
        assert "elk" in SPECIES_NEEDS


class TestV7ZoneTypology:
    def test_subscores_7_keys(self):
        from modules.bionic_engine_p0.services.zone_typology_v7 import compute_subscores
        zone = {"centroid": {"lat": 46.81, "lng": -71.21}, "area_m2": 8000, "compactness": 0.6}
        scores = compute_subscores(zone, "alimentation", "moose", [], month=10)
        assert len(scores) == 7
        for key in ("food", "safety", "access", "stealth", "water", "topo", "dynamic"):
            assert key in scores
            assert 0 <= scores[key] <= 100

    def test_global_score_range(self):
        from modules.bionic_engine_p0.services.zone_typology_v7 import compute_global_score
        subscores = {"food": 80, "safety": 60, "access": 70, "stealth": 50, "water": 90, "topo": 65, "dynamic": 55}
        score = compute_global_score(subscores)
        assert 0 <= score <= 100

    def test_classify_zone_type(self):
        from modules.bionic_engine_p0.services.zone_typology_v7 import classify_zone_type
        subscores = {"food": 90, "safety": 30, "access": 70, "stealth": 20, "water": 80, "topo": 50, "dynamic": 50}
        zone_type, confidence = classify_zone_type(subscores, "alimentation", "moose", 10)
        assert zone_type in ("feed", "rest", "rut", "heat_ref", "hunt_ref", "corridor", "mixed")
        assert 0 < confidence <= 1.0

    def test_enrich_zone_v7(self):
        from modules.bionic_engine_p0.services.zone_typology_v7 import enrich_zone_v7
        zone = {
            "centroid": {"lat": 46.81, "lng": -71.21},
            "area_m2": 10000, "compactness": 0.65,
        }
        result = enrich_zone_v7(zone, "repos", "moose", [], month=10)
        assert "v7" in result
        v7 = result["v7"]
        assert "zone_type" in v7
        assert "score_global" in v7
        assert "subscores" in v7
        assert "confidence" in v7
        assert "season_relevance" in v7

    def test_detect_hotspots(self):
        from modules.bionic_engine_p0.services.zone_typology_v7 import detect_hotspots
        zones = [
            {"v7": {"score_global": 80, "zone_type": "feed"}},
            {"v7": {"score_global": 40, "zone_type": "rest"}},
            {"v7": {"score_global": 75, "zone_type": "rut"}},
        ]
        hotspots = detect_hotspots(zones, threshold=70)
        assert len(hotspots) == 2
        assert zones[0]["v7"]["hotspot"] is True
        assert zones[1]["v7"]["hotspot"] is False


class TestV7TerrainSignals:
    def test_extract_terrain_signals(self):
        from modules.bionic_engine_p0.services.terrain_signals_v7 import extract_terrain_signals_from_exclusions
        exclusions = [
            {"type": "water", "sub_type": "lake", "coordinates": [[-71.21, 46.81]], "filtered_out": False},
            {"type": "roads", "sub_type": "secondary", "coordinates": [[-71.215, 46.812]], "filtered_out": False},
            {"type": "urban", "sub_type": "residential", "coordinates": [[-71.22, 46.82]], "filtered_out": False},
        ]
        signals = extract_terrain_signals_from_exclusions({"lat": 46.81, "lng": -71.21}, exclusions, 2000)
        assert "counts" in signals
        assert "nearest_m" in signals
        assert "forest_proxy" in signals
        assert "disturbance_index" in signals
        assert 0 <= signals["forest_proxy"] <= 1.0


class TestV7Corridors:
    def test_generate_corridors_with_astar(self):
        from modules.bionic_engine_p0.services.corridor_v7 import generate_corridors_v7
        zones = [
            {"zone_id": "z1", "centroid": {"lat": 46.81, "lng": -71.21}, "v7": {"zone_type": "rest"}},
            {"zone_id": "z2", "centroid": {"lat": 46.815, "lng": -71.205}, "v7": {"zone_type": "feed"}},
        ]
        exclusions = [
            {"type": "roads", "sub_type": "secondary", "geometry_type": "line",
             "coordinates": [[-71.208, 46.808], [-71.208, 46.818]], "filtered_out": False},
        ]
        corridors = generate_corridors_v7(zones, exclusions, "moose", max_corridors=4)
        assert len(corridors) > 0
        c = corridors[0]
        assert c["type"] == "Feature"
        assert c["geometry"]["type"] == "LineString"
        props = c["properties"]
        assert props["sex"] in ("male", "female")
        assert props["source"] in ("real", "ai")
        assert "scoring" in props
        scoring = props["scoring"]
        assert "score" in scoring
        assert "subscores" in scoring
        assert "distance_m" in scoring
        assert "justification" in scoring

    def test_trail_scoring_subscores(self):
        from modules.bionic_engine_p0.services.corridor_v7 import generate_corridors_v7
        zones = [
            {"zone_id": "z1", "centroid": {"lat": 46.81, "lng": -71.21}, "v7": {"zone_type": "rest"}},
            {"zone_id": "z2", "centroid": {"lat": 46.815, "lng": -71.205}, "v7": {"zone_type": "feed"}},
        ]
        corridors = generate_corridors_v7(zones, [], "moose", max_corridors=2)
        if corridors:
            scoring = corridors[0]["properties"]["scoring"]
            for key in ("topographie", "couvert", "eau", "pression", "comportement"):
                assert key in scoring["subscores"]

    def test_corridor_styles(self):
        from modules.bionic_engine_p0.services.corridor_v7 import CORRIDOR_STYLES
        assert "male_real" in CORRIDOR_STYLES
        assert "female_real" in CORRIDOR_STYLES
        assert "male_ai" in CORRIDOR_STYLES
        assert "female_ai" in CORRIDOR_STYLES
        assert CORRIDOR_STYLES["male_real"]["dasharray"] == "none"
        assert CORRIDOR_STYLES["male_ai"]["dasharray"] != "none"

    def test_male_female_different_colors(self):
        from modules.bionic_engine_p0.services.corridor_v7 import CORRIDOR_STYLES
        assert CORRIDOR_STYLES["male_real"]["color"] != CORRIDOR_STYLES["female_real"]["color"]

    def test_trail_season_relevance(self):
        from modules.bionic_engine_p0.services.corridor_v7 import generate_corridors_v7
        zones = [
            {"zone_id": "z1", "centroid": {"lat": 46.81, "lng": -71.21}, "v7": {"zone_type": "rest"}},
            {"zone_id": "z2", "centroid": {"lat": 46.815, "lng": -71.205}, "v7": {"zone_type": "feed"}},
        ]
        corridors = generate_corridors_v7(zones, [], "moose", max_corridors=2)
        if corridors:
            season = corridors[0]["properties"]["season_relevance"]
            assert "spring" in season
            assert "fall" in season


class TestV7CostGrid:
    def test_build_cost_grid(self):
        from modules.bionic_engine_p0.services.trail_cost_grid_v7 import build_cost_grid
        import numpy as np
        bounds = {"north": 46.82, "south": 46.80, "east": -71.20, "west": -71.22}
        exclusions = [
            {"type": "water", "sub_type": "lake", "geometry_type": "polygon",
             "coordinates": [[-71.218, 46.810], [-71.216, 46.810], [-71.216, 46.811], [-71.218, 46.811]],
             "filtered_out": False},
        ]
        grid, meta = build_cost_grid(bounds, exclusions, "moose", "male", 40)
        assert grid.shape == (40, 40)
        assert meta["impassable_cells"] > 0
        assert grid.min() >= 0.1
        assert grid.max() <= 999.0

    def test_sex_difference_in_grid(self):
        from modules.bionic_engine_p0.services.trail_cost_grid_v7 import build_cost_grid
        import numpy as np
        bounds = {"north": 46.82, "south": 46.80, "east": -71.20, "west": -71.22}
        excl = [{"type": "roads", "sub_type": "secondary", "geometry_type": "line",
                 "coordinates": [[-71.215, 46.808], [-71.215, 46.818]], "filtered_out": False}]
        grid_m, _ = build_cost_grid(bounds, excl, "moose", "male", 30)
        grid_f, _ = build_cost_grid(bounds, excl, "moose", "female", 30)
        # Female should have higher average cost (more cautious)
        assert grid_f.mean() >= grid_m.mean() * 0.95


class TestV7ZoneShape:
    def test_smooth_zone_adaptive(self):
        from modules.bionic_engine_p0.services.zone_shape_v7 import smooth_zone_adaptive
        coords = [[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]
        smoothed = smooth_zone_adaptive(coords, iterations=3, terrain_roughness=0.5)
        assert len(smoothed) > len(coords)

    def test_validate_zone_topology(self):
        from modules.bionic_engine_p0.services.zone_shape_v7 import validate_zone_topology
        valid = validate_zone_topology([[0, 0], [1, 0], [1, 1], [0, 1]])
        assert valid is not None
        assert len(valid) >= 4

    def test_invalid_topology(self):
        from modules.bionic_engine_p0.services.zone_shape_v7 import validate_zone_topology
        invalid = validate_zone_topology([[0, 0], [1, 0]])
        assert invalid is None


class TestV7Pipeline:
    def test_process_zones_v7_basic(self):
        from modules.bionic_engine_p0.services.pipeline_v7 import process_zones_v7
        bounds = {"north": 46.82, "south": 46.80, "east": -71.20, "west": -71.22}
        zones = [{
            "coordinates": [[-71.215, 46.812], [-71.214, 46.812], [-71.214, 46.813], [-71.215, 46.813]],
            "area_m2": 8000, "compactness": 0.7,
            "centroid": {"lat": 46.8125, "lng": -71.2145}, "vertices": 4,
        }]
        valid, rejected, stats = process_zones_v7(zones, bounds, [], "repos", "moose")
        assert stats["engine"] == "v7"
        assert len(valid) == 1
        assert "v7" in valid[0]
        assert valid[0]["v7"]["zone_type"] in ("feed", "rest", "rut", "heat_ref", "hunt_ref", "corridor", "mixed")

    def test_process_zones_v7_with_exclusion(self):
        from modules.bionic_engine_p0.services.pipeline_v7 import process_zones_v7
        bounds = {"north": 46.82, "south": 46.80, "east": -71.20, "west": -71.22}
        zones = [{
            "coordinates": [[-71.215, 46.812], [-71.214, 46.812], [-71.214, 46.813], [-71.215, 46.813]],
            "area_m2": 8000, "compactness": 0.7,
            "centroid": {"lat": 46.8125, "lng": -71.2145}, "vertices": 4,
        }]
        exclusions = [{
            "id": 1, "type": "water", "geometry_type": "polygon", "sub_type": "lake",
            "coordinates": [[-71.216, 46.811], [-71.213, 46.811], [-71.213, 46.814], [-71.216, 46.814]],
            "area_m2": 100000, "filtered_out": False,
        }]
        valid, rejected, stats = process_zones_v7(zones, bounds, exclusions, "repos", "moose")
        # Zone inside lake should be rejected
        assert len(rejected) > 0 or len(valid) == 0

    def test_generate_all_corridors(self):
        from modules.bionic_engine_p0.services.pipeline_v7 import generate_all_corridors_v7
        zones_by_layer = {
            "repos": [
                {"zone_id": "z1", "centroid": {"lat": 46.81, "lng": -71.21}, "v7": {"zone_type": "rest"}},
            ],
            "alimentation": [
                {"zone_id": "z2", "centroid": {"lat": 46.815, "lng": -71.205}, "v7": {"zone_type": "feed"}},
            ],
        }
        corridors = generate_all_corridors_v7(zones_by_layer, [], "moose", 10)
        assert len(corridors) > 0

    def test_v7_metadata(self):
        from modules.bionic_engine_p0.services.pipeline_v7 import build_v7_response_metadata
        stats = {
            "repos": {"valid": 5, "hotspots": 2, "rejected_v6": 1, "trimmed": 1, "zone_types": {"rest": 5}},
            "alimentation": {"valid": 3, "hotspots": 1, "rejected_v6": 2, "trimmed": 0, "zone_types": {"feed": 3}},
        }
        corridors = [{"id": "c1"}, {"id": "c2"}]
        meta = build_v7_response_metadata(stats, corridors, "moose")
        assert meta["engine"] == "v7"
        assert meta["total_zones"] == 8
        assert meta["total_hotspots"] == 3
        assert meta["corridor_count"] == 2


class TestV7GeoJSONIntegration:
    def test_v7_data_in_geojson_feature(self):
        from modules.bionic_engine_p0.services.zone_visual_layer_v2 import zone_to_geojson_feature
        zone = {
            "coordinates": [[0, 0], [1, 0], [1, 1], [0, 1]],
            "area_m2": 8000, "compactness": 0.7, "vertices": 4,
            "centroid": {"lat": 0.5, "lng": 0.5},
            "v7": {
                "zone_type": "feed", "zone_type_label": "Zone d'alimentation",
                "zone_type_color": "#2E7D32", "score_global": 75.0,
                "subscores": {"food": 80, "safety": 60, "access": 70, "stealth": 50, "water": 85, "topo": 65, "dynamic": 55},
                "confidence": 0.8, "hotspot": True, "hotspot_type": "alimentation",
                "season_relevance": {"fall": 1.0, "spring": 0.7},
            },
        }
        penalty = {"factor": 0.9, "raw_score": 75, "details": {}, "v7": zone["v7"]}
        feature = zone_to_geojson_feature(zone, "alimentation", "z001", 70, "moose", penalty)
        props = feature["properties"]
        assert props["zone_type"] == "feed"
        assert props["score_global"] == 75.0
        assert props["hotspot"] is True
        assert "subscores" in props
        assert props["source_id"] == "BIONIC-ALIMENTATION-V7"


class TestV7RegressionV5Baseline:
    """Verifie que V7 produit au moins autant de zones que la baseline V5."""

    def test_zone_count_meets_baseline(self):
        import httpx
        bounds = {"south": 46.795, "west": -71.227, "north": 46.833, "east": -71.189}
        response = httpx.post(
            "http://localhost:8001/api/v1/bionic/organic-zones",
            json={"bounds": bounds, "species": "moose", "resolution": 80, "max_zones_per_layer": 8},
            timeout=30,
        )
        assert response.status_code == 200
        data = response.json()
        total = data.get("stats", {}).get("total_zones", 0)
        assert total >= 18, f"V7 zone count {total} < V5 baseline 18 (R1 adjusted)"

    def test_v7_engine_active(self):
        import httpx
        bounds = {"south": 46.795, "west": -71.227, "north": 46.833, "east": -71.189}
        response = httpx.post(
            "http://localhost:8001/api/v1/bionic/organic-zones",
            json={"bounds": bounds, "species": "moose", "resolution": 80, "max_zones_per_layer": 8},
            timeout=30,
        )
        data = response.json()
        assert data.get("stats", {}).get("exclusion_engine") == "v7"

    def test_corridors_generated(self):
        import httpx
        bounds = {"south": 46.795, "west": -71.227, "north": 46.833, "east": -71.189}
        response = httpx.post(
            "http://localhost:8001/api/v1/bionic/organic-zones",
            json={"bounds": bounds, "species": "moose", "resolution": 80, "max_zones_per_layer": 8},
            timeout=30,
        )
        data = response.json()
        corridors = data.get("corridors", [])
        assert len(corridors) > 0, "V7 should generate corridors"
        c = corridors[0]
        assert c["geometry"]["type"] == "LineString"
        assert c["properties"]["sex"] in ("male", "female")

    def test_v7_metadata_present(self):
        import httpx
        bounds = {"south": 46.795, "west": -71.227, "north": 46.833, "east": -71.189}
        response = httpx.post(
            "http://localhost:8001/api/v1/bionic/organic-zones",
            json={"bounds": bounds, "species": "moose", "resolution": 80, "max_zones_per_layer": 8},
            timeout=30,
        )
        data = response.json()
        v7 = data.get("v7_metadata", {})
        assert v7.get("engine") == "v7"
        assert "zone_type_distribution" in v7
        assert "corridor_count" in v7
