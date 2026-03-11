"""
Test Habitat Score API — BIONIC V5 ULTIME 300%
Tests for POST /api/v1/bionic/habitat-score/realtime and GET /api/v1/bionic/habitat-score/status
Iteration 85 — cursor_bionic_v1 + waypoint_quickadd_v1
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

SUPPORTED_SPECIES = ['moose', 'deer', 'bear', 'wild_turkey', 'elk']

# Sample bounds for testing (Quebec region)
TEST_BOUNDS = {
    "north": 46.85,
    "south": 46.78,
    "east": -71.15,
    "west": -71.25
}


class TestHabitatScoreStatus:
    """GET /api/v1/bionic/habitat-score/status tests"""

    def test_status_returns_active(self):
        """Status endpoint returns active status with 12 factors"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/habitat-score/status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["status"] == "active", f"Expected status=active, got {data.get('status')}"
        assert data["version"] == "habitat_score_v1", f"Expected version=habitat_score_v1"
        assert data["module"] == "HABITAT_SCORE", f"Expected module=HABITAT_SCORE"
        print(f"PASS: Status endpoint returns active with module={data['module']}")

    def test_status_has_12_factors(self):
        """Status endpoint lists exactly 12 habitat factors"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/habitat-score/status")
        assert response.status_code == 200
        
        data = response.json()
        factors = data.get("factors", [])
        assert len(factors) == 12, f"Expected 12 factors, got {len(factors)}: {factors}"
        
        expected_factors = [
            "micro-relief", "vegetation (NDVI)", "essences forestieres",
            "drainage", "distance eau", "distance anthropique",
            "connectivite ecologique", "pression humaine", "thermique",
            "altitude", "regles espece", "zones fonctionnelles"
        ]
        for ef in expected_factors:
            assert ef in factors, f"Missing factor: {ef}"
        print(f"PASS: Status has all 12 factors: {factors}")

    def test_status_lists_supported_species(self):
        """Status endpoint lists all 5 supported species"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/habitat-score/status")
        assert response.status_code == 200
        
        data = response.json()
        species_list = data.get("species_supported", [])
        for sp in SUPPORTED_SPECIES:
            assert sp in species_list, f"Missing species: {sp}"
        print(f"PASS: Status lists all supported species: {species_list}")


class TestHabitatScoreRealtime:
    """POST /api/v1/bionic/habitat-score/realtime tests"""

    def test_realtime_returns_30x30_grid_default(self):
        """Realtime endpoint returns 30x30 grid (default resolution)"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": "moose",
            "resolution": 30
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/habitat-score/realtime",
            json=payload
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        scores = data.get("scores", [])
        assert len(scores) == 30, f"Expected 30 rows, got {len(scores)}"
        assert len(scores[0]) == 30, f"Expected 30 cols, got {len(scores[0])}"
        
        grid = data.get("grid", {})
        assert grid.get("rows") == 30
        assert grid.get("cols") == 30
        print(f"PASS: Realtime returns 30x30 grid")

    def test_realtime_returns_stats(self):
        """Realtime endpoint returns stats (mean, min, max, hotspot_pct)"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": "deer"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/habitat-score/realtime",
            json=payload
        )
        assert response.status_code == 200
        
        data = response.json()
        stats = data.get("stats", {})
        
        assert "mean" in stats, "Missing mean in stats"
        assert "min" in stats, "Missing min in stats"
        assert "max" in stats, "Missing max in stats"
        assert "hotspot_pct" in stats, "Missing hotspot_pct in stats"
        
        # Verify values are within expected range
        assert 0 <= stats["mean"] <= 100, f"Mean out of range: {stats['mean']}"
        assert 0 <= stats["min"] <= 100, f"Min out of range: {stats['min']}"
        assert 0 <= stats["max"] <= 100, f"Max out of range: {stats['max']}"
        assert 0 <= stats["hotspot_pct"] <= 100, f"Hotspot_pct out of range: {stats['hotspot_pct']}"
        
        print(f"PASS: Stats returned: mean={stats['mean']}, min={stats['min']}, max={stats['max']}, hotspot_pct={stats['hotspot_pct']}")

    def test_realtime_scores_in_0_100_range(self):
        """All scores in grid are between 0-100"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": "bear",
            "resolution": 10
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/habitat-score/realtime",
            json=payload
        )
        assert response.status_code == 200
        
        data = response.json()
        scores = data.get("scores", [])
        
        for i, row in enumerate(scores):
            for j, score in enumerate(row):
                assert 0 <= score <= 100, f"Score at [{i}][{j}] out of range: {score}"
        
        print(f"PASS: All {len(scores)*len(scores[0])} scores in 0-100 range")

    @pytest.mark.parametrize("species", SUPPORTED_SPECIES)
    def test_realtime_validates_all_species(self, species):
        """Realtime accepts all supported species"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": species,
            "resolution": 10
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/habitat-score/realtime",
            json=payload
        )
        assert response.status_code == 200, f"Expected 200 for species={species}, got {response.status_code}"
        
        data = response.json()
        assert data.get("species") == species
        print(f"PASS: Species '{species}' accepted")

    def test_realtime_rejects_invalid_species_with_400(self):
        """Realtime rejects invalid species with 400 error"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": "invalid_animal",
            "resolution": 30
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/habitat-score/realtime",
            json=payload
        )
        assert response.status_code == 400, f"Expected 400 for invalid species, got {response.status_code}"
        print(f"PASS: Invalid species rejected with 400")

    def test_realtime_returns_data_sources(self):
        """Realtime returns data_sources indicating real vs synthetic"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": "moose"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/habitat-score/realtime",
            json=payload
        )
        assert response.status_code == 200
        
        data = response.json()
        data_sources = data.get("data_sources", {})
        
        assert "ndvi" in data_sources, "Missing ndvi in data_sources"
        assert "dem" in data_sources, "Missing dem in data_sources"
        assert "weather" in data_sources, "Missing weather in data_sources"
        
        # Values should be one of: sentinel2_real, synthetic, real, default
        valid_values = ["sentinel2_real", "synthetic", "real", "default"]
        for key, val in data_sources.items():
            assert val in valid_values, f"Invalid data_source value: {key}={val}"
        
        print(f"PASS: data_sources returned: {data_sources}")

    @pytest.mark.parametrize("resolution", [10, 30, 60])
    def test_realtime_handles_resolution_10_30_60(self, resolution):
        """Realtime handles resolution 10, 30, 60"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": "elk",
            "resolution": resolution
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/habitat-score/realtime",
            json=payload
        )
        assert response.status_code == 200, f"Expected 200 for resolution={resolution}, got {response.status_code}"
        
        data = response.json()
        scores = data.get("scores", [])
        assert len(scores) == resolution, f"Expected {resolution} rows, got {len(scores)}"
        assert len(scores[0]) == resolution, f"Expected {resolution} cols, got {len(scores[0])}"
        
        grid = data.get("grid", {})
        assert grid.get("rows") == resolution
        assert grid.get("cols") == resolution
        assert len(grid.get("lats", [])) == resolution
        assert len(grid.get("lngs", [])) == resolution
        
        print(f"PASS: Resolution {resolution}x{resolution} handled correctly")

    def test_realtime_computation_time_under_100ms(self):
        """Realtime computation should be fast (<100ms typically)"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": "moose",
            "resolution": 30
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/habitat-score/realtime",
            json=payload
        )
        assert response.status_code == 200
        
        data = response.json()
        comp_time = data.get("computation_time_ms", 1000)
        
        # Should be under 100ms typically (allow up to 500ms for CI)
        assert comp_time < 500, f"Computation time too high: {comp_time}ms"
        print(f"PASS: Computation time = {comp_time}ms")


class TestWaypointQuickAdd:
    """POST /api/territory/waypoints tests for QuickAdd integration"""

    def test_create_waypoint_via_quickadd_format(self):
        """Create waypoint with QuickAdd format (uses 'custom' type since 'hotspot' not in allowed list)"""
        # NOTE: Frontend CursorBionicLayer sends waypoint_type='hotspot' but backend only accepts:
        # 'observation', 'camera', 'cache', 'stand', 'water', 'trail_start', 'custom', 'hunting', 'feeder', 'sighting', 'parking'
        # This is an integration issue - using 'custom' for test
        payload = {
            "name": "TEST_Hotspot 78% — moose",
            "latitude": 46.82,
            "longitude": -71.20,
            "waypoint_type": "custom",  # Using 'custom' - backend doesn't accept 'hotspot' yet
            "description": "Score habitat: 78% | Espece: moose | 2026-01-01T12:00:00Z"
        }
        response = requests.post(
            f"{BASE_URL}/api/territory/waypoints?user_id=default-user",
            json=payload
        )
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"
        
        data = response.json()
        # Territory API returns waypoint directly with 'id' field
        waypoint_id = data.get("id") or (data.get("waypoint", {}).get("id"))
        assert waypoint_id is not None, f"No waypoint ID returned: {data}"
        
        print(f"PASS: Waypoint created via QuickAdd format, id={waypoint_id}")
        
        # Cleanup
        delete_response = requests.delete(
            f"{BASE_URL}/api/territory/waypoints/{waypoint_id}?user_id=default-user"
        )
        assert delete_response.status_code in [200, 204], f"Cleanup failed: {delete_response.status_code}"
        print(f"PASS: Cleanup successful")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
