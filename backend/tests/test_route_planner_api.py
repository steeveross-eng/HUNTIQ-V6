"""
TEST: Route Planner API — BIONIC V5 ULTIME 300%
Tests for POST /api/v1/bionic/route-planner/compute and GET /api/v1/bionic/route-planner/status

Iteration 86 - New Feature Testing
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
SUPPORTED_SPECIES = ['moose', 'deer', 'bear', 'wild_turkey', 'elk']

# Test bounds (Quebec region)
TEST_BOUNDS = {
    "north": 46.85,
    "south": 46.75,
    "east": -71.15,
    "west": -71.25
}


class TestRoutePlannerStatus:
    """GET /api/v1/bionic/route-planner/status tests"""

    def test_status_returns_200(self):
        """Status endpoint should return 200"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/route-planner/status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("✓ GET /status returns 200")

    def test_status_returns_active(self):
        """Status should return status=active"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/route-planner/status")
        data = response.json()
        assert data.get("status") == "active", f"Expected status=active, got {data.get('status')}"
        print(f"✓ Status is active: {data.get('status')}")

    def test_status_has_features_list(self):
        """Status should include features list"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/route-planner/status")
        data = response.json()
        assert "features" in data, "Missing 'features' field"
        assert isinstance(data["features"], list), "Features should be a list"
        assert len(data["features"]) >= 3, f"Expected at least 3 features, got {len(data['features'])}"
        print(f"✓ Features count: {len(data['features'])}")
        for f in data["features"]:
            print(f"  - {f}")

    def test_status_has_supported_species(self):
        """Status should list supported species"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/route-planner/status")
        data = response.json()
        assert "species_supported" in data, "Missing 'species_supported' field"
        assert set(data["species_supported"]) == set(SUPPORTED_SPECIES), \
            f"Expected species {SUPPORTED_SPECIES}, got {data['species_supported']}"
        print(f"✓ Supported species: {data['species_supported']}")

    def test_status_has_version(self):
        """Status should have version=route_planner_v1"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/route-planner/status")
        data = response.json()
        assert data.get("version") == "route_planner_v1", f"Expected version=route_planner_v1, got {data.get('version')}"
        print(f"✓ Version: {data.get('version')}")


class TestRoutePlannerCompute:
    """POST /api/v1/bionic/route-planner/compute tests"""

    def test_compute_returns_200(self):
        """Compute endpoint should return 200 with valid request"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": "moose",
            "resolution": 30,
            "hotspot_threshold": 70.0
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/route-planner/compute",
            json=payload
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("✓ POST /compute returns 200")

    def test_compute_returns_version(self):
        """Response should include version=route_planner_v1"""
        payload = {"bounds": TEST_BOUNDS, "species": "moose"}
        response = requests.post(f"{BASE_URL}/api/v1/bionic/route-planner/compute", json=payload)
        data = response.json()
        assert data.get("version") == "route_planner_v1", f"Expected version=route_planner_v1, got {data.get('version')}"
        print(f"✓ Version: {data.get('version')}")

    def test_compute_returns_species(self):
        """Response should echo back the species"""
        payload = {"bounds": TEST_BOUNDS, "species": "deer"}
        response = requests.post(f"{BASE_URL}/api/v1/bionic/route-planner/compute", json=payload)
        data = response.json()
        assert data.get("species") == "deer", f"Expected species=deer, got {data.get('species')}"
        print(f"✓ Species echoed: {data.get('species')}")

    def test_compute_returns_hotspots_found(self):
        """Response should include hotspots_found count"""
        payload = {"bounds": TEST_BOUNDS, "species": "moose", "hotspot_threshold": 70.0}
        response = requests.post(f"{BASE_URL}/api/v1/bionic/route-planner/compute", json=payload)
        data = response.json()
        assert "hotspots_found" in data, "Missing 'hotspots_found' field"
        assert isinstance(data["hotspots_found"], int), "hotspots_found should be int"
        print(f"✓ Hotspots found: {data['hotspots_found']}")

    def test_compute_returns_route_structure(self):
        """Response should include route with points, segments, distances, times"""
        payload = {"bounds": TEST_BOUNDS, "species": "moose", "hotspot_threshold": 50.0}  # Lower threshold for more results
        response = requests.post(f"{BASE_URL}/api/v1/bionic/route-planner/compute", json=payload)
        data = response.json()
        
        if data.get("route") is None:
            print(f"⚠ No route computed (hotspots_found={data.get('hotspots_found')}, message={data.get('message')})")
            pytest.skip("No hotspots detected - route is None")
        
        route = data["route"]
        assert "points" in route, "Missing 'points' in route"
        assert "segments" in route, "Missing 'segments' in route"
        assert "total_distance_km" in route, "Missing 'total_distance_km' in route"
        assert "total_time_min" in route, "Missing 'total_time_min' in route"
        assert "avg_path_score" in route, "Missing 'avg_path_score' in route"
        print(f"✓ Route structure: {len(route['points'])} points, {len(route['segments'])} segments")
        print(f"  - Total distance: {route['total_distance_km']} km")
        print(f"  - Total time: {route['total_time_min']} min")
        print(f"  - Avg path score: {route['avg_path_score']}%")

    def test_compute_segment_has_path_and_scores(self):
        """Each segment should have path coordinates and scores_along_path"""
        payload = {"bounds": TEST_BOUNDS, "species": "moose", "hotspot_threshold": 50.0}
        response = requests.post(f"{BASE_URL}/api/v1/bionic/route-planner/compute", json=payload)
        data = response.json()
        
        if data.get("route") is None or not data["route"].get("segments"):
            pytest.skip("No segments to test")
        
        seg = data["route"]["segments"][0]
        assert "path" in seg, "Segment missing 'path'"
        assert "scores_along_path" in seg, "Segment missing 'scores_along_path'"
        assert "distance_km" in seg or "path_distance_km" in seg, "Segment missing distance"
        assert "time_min" in seg or "estimated_time_min" in seg, "Segment missing time"
        print(f"✓ Segment has path ({len(seg['path'])} coords), scores ({len(seg['scores_along_path'])} values)")

    def test_compute_returns_grid_stats(self):
        """Response should include grid_stats"""
        payload = {"bounds": TEST_BOUNDS, "species": "moose"}
        response = requests.post(f"{BASE_URL}/api/v1/bionic/route-planner/compute", json=payload)
        data = response.json()
        assert "grid_stats" in data, "Missing 'grid_stats' field"
        stats = data["grid_stats"]
        # Should have mean, min, max, hotspot_pct
        print(f"✓ Grid stats: {stats}")

    def test_compute_returns_data_sources(self):
        """Response should include data_sources"""
        payload = {"bounds": TEST_BOUNDS, "species": "moose"}
        response = requests.post(f"{BASE_URL}/api/v1/bionic/route-planner/compute", json=payload)
        data = response.json()
        assert "data_sources" in data, "Missing 'data_sources' field"
        print(f"✓ Data sources: {data['data_sources']}")

    def test_compute_validates_shadow_mode(self):
        """Response should confirm shadow_mode=True in validation"""
        payload = {"bounds": TEST_BOUNDS, "species": "moose"}
        response = requests.post(f"{BASE_URL}/api/v1/bionic/route-planner/compute", json=payload)
        data = response.json()
        assert "validation" in data, "Missing 'validation' field"
        assert data["validation"].get("shadow_mode") is True, "shadow_mode should be True"
        print(f"✓ Shadow mode confirmed: {data['validation']}")


class TestRoutePlannerSpeciesValidation:
    """Species validation tests"""

    @pytest.mark.parametrize("species", SUPPORTED_SPECIES)
    def test_compute_accepts_valid_species(self, species):
        """Should accept all supported species"""
        payload = {"bounds": TEST_BOUNDS, "species": species}
        response = requests.post(f"{BASE_URL}/api/v1/bionic/route-planner/compute", json=payload)
        assert response.status_code == 200, f"Species '{species}' should be accepted, got {response.status_code}"
        data = response.json()
        assert data.get("species") == species
        print(f"✓ Species '{species}' accepted")

    def test_compute_rejects_invalid_species(self):
        """Should reject invalid species with 400"""
        payload = {"bounds": TEST_BOUNDS, "species": "unicorn"}
        response = requests.post(f"{BASE_URL}/api/v1/bionic/route-planner/compute", json=payload)
        assert response.status_code == 400, f"Expected 400 for invalid species, got {response.status_code}"
        print("✓ Invalid species 'unicorn' rejected with 400")


class TestRoutePlannerThresholds:
    """Threshold variation tests"""

    @pytest.mark.parametrize("threshold", [50.0, 70.0, 85.0])
    def test_compute_handles_different_thresholds(self, threshold):
        """Should handle different hotspot_threshold values"""
        payload = {"bounds": TEST_BOUNDS, "species": "moose", "hotspot_threshold": threshold}
        response = requests.post(f"{BASE_URL}/api/v1/bionic/route-planner/compute", json=payload)
        assert response.status_code == 200, f"Threshold {threshold} failed: {response.status_code}"
        data = response.json()
        # If route exists, threshold should be echoed; if no hotspots, response may not include it
        if data.get("route"):
            assert data.get("hotspot_threshold") == threshold, f"Expected threshold={threshold}"
        print(f"✓ Threshold {threshold}% accepted, hotspots_found={data.get('hotspots_found')}")


class TestRoutePlannerResolutions:
    """Resolution variation tests"""

    @pytest.mark.parametrize("resolution", [20, 30])
    def test_compute_handles_different_resolutions(self, resolution):
        """Should handle resolution 20 and 30"""
        payload = {"bounds": TEST_BOUNDS, "species": "moose", "resolution": resolution}
        response = requests.post(f"{BASE_URL}/api/v1/bionic/route-planner/compute", json=payload)
        assert response.status_code == 200, f"Resolution {resolution} failed: {response.status_code}"
        data = response.json()
        assert data.get("resolution") == resolution, f"Expected resolution={resolution}"
        print(f"✓ Resolution {resolution} accepted")


class TestRoutePlannerAnchorWaypoints:
    """Anchor waypoints integration tests"""

    def test_compute_includes_anchor_waypoints(self):
        """Should integrate anchor_waypoints into route"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": "moose",
            "hotspot_threshold": 50.0,
            "anchor_waypoints": [
                {"lat": 46.80, "lng": -71.20, "name": "Spot A"},
                {"lat": 46.82, "lng": -71.18, "name": "Spot B"}
            ]
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/route-planner/compute", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Should have anchor_waypoints_used count
        assert "anchor_waypoints_used" in data, "Missing 'anchor_waypoints_used'"
        assert data["anchor_waypoints_used"] == 2, f"Expected 2 anchors, got {data['anchor_waypoints_used']}"
        print(f"✓ Anchor waypoints used: {data['anchor_waypoints_used']}")
        
        # Check if anchors appear in route points with is_anchor=True
        if data.get("route"):
            anchor_points = [p for p in data["route"]["points"] if p.get("is_anchor")]
            print(f"  - Anchor points in route: {len(anchor_points)}")
            for ap in anchor_points:
                print(f"    - {ap.get('name')}: {ap.get('lat')}, {ap.get('lng')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
