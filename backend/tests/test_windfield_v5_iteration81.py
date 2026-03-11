"""
TEST WINDFIELD API — BIONIC V5 ULTIME 300% — Phase P2
Iteration 81 — POST /api/v1/bionic/weather-shadow/windfield

Tests the NEW windfield endpoint that returns u10/v10 wind vector data
for Ventusky-like Canvas 2D rendering.

Features tested:
- Wind vector field generation (u10, v10, speed arrays)
- Grid dimensions matching resolution parameter
- Weather source validation (api_fetched, cache_hit, fallback_synthetic)
- Shadow mode validation (shadow_mode, zero_impact_on_production)
- Metadata fields (base_wind_speed_kmh, wind_direction_deg, u_base_ms, v_base_ms)
- Multiple resolutions (20, 30, 60)
- Status endpoint still returns active
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test bounds - Laurentides region (same as iteration_80)
TEST_BOUNDS = {
    "north": 46.95,
    "south": 46.85,
    "east": -74.00,
    "west": -74.15
}


class TestWindfieldEndpoint:
    """Tests for POST /api/v1/bionic/weather-shadow/windfield"""
    
    def test_windfield_returns_200_with_valid_request(self):
        """Windfield endpoint returns 200 with valid structure"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/weather-shadow/windfield",
            json={
                "bounds": TEST_BOUNDS,
                "species": "moose",
                "resolution": 30
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Check required top-level fields
        assert "version" in data, "Missing version field"
        assert data["version"] == "windfield_v1", f"Expected windfield_v1, got {data['version']}"
        assert "source" in data, "Missing source field"
        assert "bounds" in data, "Missing bounds field"
        assert "resolution" in data, "Missing resolution field"
        print(f"PASS: Windfield returns 200 with valid structure (version={data['version']})")
    
    def test_windfield_contains_u10_v10_arrays(self):
        """Windfield response contains u10, v10, speed arrays"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/weather-shadow/windfield",
            json={
                "bounds": TEST_BOUNDS,
                "species": "moose",
                "resolution": 30
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check wind vector fields
        assert "u10" in data, "Missing u10 field"
        assert "v10" in data, "Missing v10 field"
        assert "speed" in data, "Missing speed field"
        
        # Check they are 2D arrays
        assert isinstance(data["u10"], list), "u10 should be a list"
        assert isinstance(data["v10"], list), "v10 should be a list"
        assert isinstance(data["speed"], list), "speed should be a list"
        
        # Check inner arrays exist
        assert len(data["u10"]) > 0, "u10 array is empty"
        assert isinstance(data["u10"][0], list), "u10 should be 2D array"
        
        print(f"PASS: Windfield contains u10/v10/speed arrays (u10 shape: {len(data['u10'])}x{len(data['u10'][0])})")
    
    def test_windfield_grid_dimensions_match_resolution(self):
        """Grid dimensions match resolution parameter"""
        resolution = 30
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/weather-shadow/windfield",
            json={
                "bounds": TEST_BOUNDS,
                "species": "moose",
                "resolution": resolution
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check grid field
        assert "grid" in data, "Missing grid field"
        grid = data["grid"]
        
        assert "rows" in grid, "Missing grid.rows"
        assert "cols" in grid, "Missing grid.cols"
        assert "lats" in grid, "Missing grid.lats"
        assert "lngs" in grid, "Missing grid.lngs"
        
        # Verify dimensions match resolution
        assert grid["rows"] == resolution, f"Expected rows={resolution}, got {grid['rows']}"
        assert grid["cols"] == resolution, f"Expected cols={resolution}, got {grid['cols']}"
        
        # Verify array dimensions
        assert len(data["u10"]) == resolution, f"u10 rows should be {resolution}, got {len(data['u10'])}"
        assert len(data["u10"][0]) == resolution, f"u10 cols should be {resolution}, got {len(data['u10'][0])}"
        assert len(data["v10"]) == resolution, f"v10 rows should be {resolution}"
        assert len(data["speed"]) == resolution, f"speed rows should be {resolution}"
        
        # Verify lats/lngs arrays
        assert len(grid["lats"]) == resolution, f"lats should have {resolution} elements"
        assert len(grid["lngs"]) == resolution, f"lngs should have {resolution} elements"
        
        print(f"PASS: Grid dimensions match resolution={resolution} ({grid['rows']}x{grid['cols']})")
    
    def test_windfield_source_is_valid(self):
        """Source is api_fetched, cache_hit, or fallback_synthetic"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/weather-shadow/windfield",
            json={
                "bounds": TEST_BOUNDS,
                "species": "moose",
                "resolution": 30
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        valid_sources = ["api_fetched", "cache_hit", "fallback_synthetic"]
        assert data["source"] in valid_sources, f"Invalid source: {data['source']}, expected one of {valid_sources}"
        
        print(f"PASS: Weather source is valid ({data['source']})")
    
    def test_windfield_validation_block_confirms_shadow_mode(self):
        """Validation block confirms shadow_mode and zero_impact_on_production"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/weather-shadow/windfield",
            json={
                "bounds": TEST_BOUNDS,
                "species": "moose",
                "resolution": 30
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "validation" in data, "Missing validation field"
        validation = data["validation"]
        
        assert "shadow_mode" in validation, "Missing validation.shadow_mode"
        assert validation["shadow_mode"] == True, f"shadow_mode should be True, got {validation['shadow_mode']}"
        
        assert "zero_impact_on_production" in validation, "Missing validation.zero_impact_on_production"
        assert validation["zero_impact_on_production"] == True, f"zero_impact_on_production should be True"
        
        # data_real depends on source
        assert "data_real" in validation, "Missing validation.data_real"
        source = data["source"]
        if source == "fallback_synthetic":
            assert validation["data_real"] == False, "data_real should be False for fallback_synthetic"
        else:
            assert validation["data_real"] == True, f"data_real should be True for source={source}"
        
        print(f"PASS: Validation confirms shadow_mode=True, zero_impact_on_production=True, data_real={validation['data_real']}")
    
    def test_windfield_metadata_contains_required_fields(self):
        """Metadata contains base_wind_speed_kmh, wind_direction_deg, u_base_ms, v_base_ms"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/weather-shadow/windfield",
            json={
                "bounds": TEST_BOUNDS,
                "species": "moose",
                "resolution": 30
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "metadata" in data, "Missing metadata field"
        metadata = data["metadata"]
        
        # Required metadata fields
        required_fields = ["base_wind_speed_kmh", "base_wind_direction_deg", "u_base_ms", "v_base_ms"]
        for field in required_fields:
            assert field in metadata, f"Missing metadata.{field}"
        
        # Additional metadata fields
        assert "mean_speed_ms" in metadata, "Missing metadata.mean_speed_ms"
        assert "max_speed_ms" in metadata, "Missing metadata.max_speed_ms"
        
        # Validate types
        assert isinstance(metadata["base_wind_speed_kmh"], (int, float)), "base_wind_speed_kmh should be numeric"
        assert isinstance(metadata["base_wind_direction_deg"], (int, float)), "base_wind_direction_deg should be numeric"
        assert isinstance(metadata["u_base_ms"], (int, float)), "u_base_ms should be numeric"
        assert isinstance(metadata["v_base_ms"], (int, float)), "v_base_ms should be numeric"
        
        print(f"PASS: Metadata contains required fields (wind={metadata['base_wind_speed_kmh']:.1f}km/h @ {metadata['base_wind_direction_deg']:.0f}deg)")
    
    def test_windfield_resolution_20(self):
        """Resolution 20 produces 20x20 grid"""
        resolution = 20
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/weather-shadow/windfield",
            json={
                "bounds": TEST_BOUNDS,
                "species": "moose",
                "resolution": resolution
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["resolution"] == resolution
        assert data["grid"]["rows"] == resolution
        assert data["grid"]["cols"] == resolution
        assert len(data["u10"]) == resolution
        assert len(data["u10"][0]) == resolution
        
        print(f"PASS: Resolution 20 produces {resolution}x{resolution} grid")
    
    def test_windfield_resolution_30(self):
        """Resolution 30 produces 30x30 grid"""
        resolution = 30
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/weather-shadow/windfield",
            json={
                "bounds": TEST_BOUNDS,
                "species": "moose",
                "resolution": resolution
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["resolution"] == resolution
        assert data["grid"]["rows"] == resolution
        assert data["grid"]["cols"] == resolution
        
        print(f"PASS: Resolution 30 produces {resolution}x{resolution} grid")
    
    def test_windfield_resolution_60(self):
        """Resolution 60 produces 60x60 grid"""
        resolution = 60
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/weather-shadow/windfield",
            json={
                "bounds": TEST_BOUNDS,
                "species": "moose",
                "resolution": resolution
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["resolution"] == resolution
        assert data["grid"]["rows"] == resolution
        assert data["grid"]["cols"] == resolution
        
        print(f"PASS: Resolution 60 produces {resolution}x{resolution} grid")
    
    def test_windfield_computation_time_returned(self):
        """computation_time_ms is returned"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/weather-shadow/windfield",
            json={
                "bounds": TEST_BOUNDS,
                "species": "moose",
                "resolution": 30
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "computation_time_ms" in data, "Missing computation_time_ms"
        assert isinstance(data["computation_time_ms"], (int, float)), "computation_time_ms should be numeric"
        assert data["computation_time_ms"] >= 0, "computation_time_ms should be non-negative"
        
        print(f"PASS: computation_time_ms={data['computation_time_ms']:.1f}ms")


class TestWeatherShadowStatusEndpoint:
    """Tests for GET /api/v1/bionic/weather-shadow/status"""
    
    def test_status_returns_active(self):
        """Status endpoint returns active"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/weather-shadow/status")
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "active", f"Expected status=active, got {data['status']}"
        assert data["module"] == "WEATHER_SHADOW", f"Expected module=WEATHER_SHADOW, got {data['module']}"
        
        print(f"PASS: Weather shadow status is active (module={data['module']})")
    
    def test_status_confirms_shadow_mode(self):
        """Status confirms shadow mode with zero impact"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/weather-shadow/status")
        assert response.status_code == 200
        data = response.json()
        
        assert data["mode"] == "shadow (non-destructif)", f"Unexpected mode: {data['mode']}"
        assert data["impact_on_production"] == "zero", f"Unexpected impact: {data['impact_on_production']}"
        
        print(f"PASS: Status confirms shadow mode with zero impact on production")


class TestWindfieldValidation:
    """Validation tests for windfield endpoint"""
    
    def test_windfield_invalid_resolution_below_20_returns_422(self):
        """Resolution below 20 returns 422"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/weather-shadow/windfield",
            json={
                "bounds": TEST_BOUNDS,
                "species": "moose",
                "resolution": 10  # Below minimum of 20
            }
        )
        assert response.status_code == 422, f"Expected 422 for resolution=10, got {response.status_code}"
        print("PASS: Resolution below 20 returns 422")
    
    def test_windfield_invalid_bounds_returns_422(self):
        """Invalid bounds (latitude > 90) returns 422"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/weather-shadow/windfield",
            json={
                "bounds": {
                    "north": 100,  # Invalid latitude
                    "south": 46.85,
                    "east": -74.00,
                    "west": -74.15
                },
                "species": "moose",
                "resolution": 30
            }
        )
        assert response.status_code == 422, f"Expected 422 for invalid latitude, got {response.status_code}"
        print("PASS: Invalid latitude (>90) returns 422")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
