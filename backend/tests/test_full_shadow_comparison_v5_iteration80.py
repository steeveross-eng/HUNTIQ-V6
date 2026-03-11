"""
FULL SHADOW COMPARISON — BIONIC V5 ULTIME 300%
===============================================
Test: POST /api/v1/bionic/shadow/full-comparison
Test: GET /api/v1/bionic/shadow/full-comparison/status

Compare synthetic pipeline vs full-real pipeline (DEM + Weather combined).
Mode: STRICT SHADOW — 0 impact on production.

Supported species: moose, deer, bear, wild_turkey, elk
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
SUPPORTED_SPECIES = ['moose', 'deer', 'bear', 'wild_turkey', 'elk']

# Test bounds (Laurentides region)
TEST_BOUNDS = {
    "north": 46.95,
    "south": 46.85,
    "east": -74.00,
    "west": -74.15
}


class TestFullComparisonStatus:
    """GET /api/v1/bionic/shadow/full-comparison/status tests"""
    
    def test_status_returns_200(self):
        """Status endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/shadow/full-comparison/status", timeout=30)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("✓ GET /full-comparison/status returns 200")
    
    def test_status_module_info(self):
        """Status returns correct module info"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/shadow/full-comparison/status", timeout=30)
        data = response.json()
        
        assert data["module"] == "FULL_SHADOW_COMPARISON", f"Wrong module: {data.get('module')}"
        assert data["version"] == "full_comparison_v1", f"Wrong version: {data.get('version')}"
        assert data["status"] == "active", f"Status not active: {data.get('status')}"
        print(f"✓ Module: {data['module']}, version: {data['version']}")
    
    def test_status_shadow_mode(self):
        """Status confirms shadow mode"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/shadow/full-comparison/status", timeout=30)
        data = response.json()
        
        validation = data.get("validation", {})
        assert validation.get("shadow_mode") is True, "shadow_mode should be True"
        assert validation.get("zero_impact_on_production") is True, "zero_impact_on_production should be True"
        assert validation.get("certified_modules_unmodified") is True, "certified_modules_unmodified should be True"
        print("✓ Shadow mode confirmed: zero impact on production")
    
    def test_status_endpoints_list(self):
        """Status returns endpoints list"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/shadow/full-comparison/status", timeout=30)
        data = response.json()
        
        endpoints = data.get("endpoints", [])
        assert len(endpoints) >= 2, f"Expected at least 2 endpoints, got {len(endpoints)}"
        assert "POST /api/v1/bionic/shadow/full-comparison" in endpoints
        assert "GET /api/v1/bionic/shadow/full-comparison/status" in endpoints
        print(f"✓ Endpoints listed: {endpoints}")
    
    def test_status_data_sources(self):
        """Status returns data sources"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/shadow/full-comparison/status", timeout=30)
        data = response.json()
        
        sources = data.get("data_sources", [])
        assert "DEM (OpenTopography)" in sources, f"DEM not in sources: {sources}"
        assert "Meteo (Open-Meteo)" in sources, f"Meteo not in sources: {sources}"
        print(f"✓ Data sources: {sources}")


class TestFullComparisonValidation:
    """Input validation tests for POST /api/v1/bionic/shadow/full-comparison"""
    
    def test_invalid_species_returns_400(self):
        """Invalid species returns 400"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": "invalid_animal",
            "resolution": 30
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/shadow/full-comparison",
            json=payload,
            timeout=30
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        assert "non supportee" in response.text.lower() or "invalid" in response.text.lower()
        print("✓ Invalid species correctly rejected with 400")
    
    def test_invalid_bounds_returns_422(self):
        """Invalid bounds returns 422"""
        payload = {
            "bounds": {
                "north": 100,  # Invalid latitude
                "south": 46.85,
                "east": -74.00,
                "west": -74.15
            },
            "species": "moose",
            "resolution": 30
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/shadow/full-comparison",
            json=payload,
            timeout=30
        )
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        print("✓ Invalid bounds correctly rejected with 422")
    
    def test_invalid_resolution_returns_422(self):
        """Invalid resolution returns 422"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": "moose",
            "resolution": 10  # Below minimum (20)
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/shadow/full-comparison",
            json=payload,
            timeout=30
        )
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        print("✓ Invalid resolution correctly rejected with 422")


class TestFullComparisonExecution:
    """POST /api/v1/bionic/shadow/full-comparison execution tests"""
    
    def test_moose_comparison_returns_200(self):
        """Full comparison for moose returns 200 with valid structure"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": "moose",
            "resolution": 30
        }
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/shadow/full-comparison",
            json=payload,
            timeout=60
        )
        elapsed = round((time.time() - start) * 1000)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Check required top-level keys
        required_keys = ["pipeline", "version", "comparison_type", "species", "bounds", 
                        "resolution", "data_sources", "synthetic", "real", "deltas", 
                        "total_computation_time_ms", "validation"]
        for key in required_keys:
            assert key in data, f"Missing key: {key}"
        
        print(f"✓ Moose comparison returned 200 in {elapsed}ms")
        return data
    
    def test_comparison_structure_synthetic(self):
        """Synthetic section has correct structure"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": "moose",
            "resolution": 30
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/shadow/full-comparison",
            json=payload,
            timeout=60
        )
        data = response.json()
        
        synthetic = data.get("synthetic", {})
        assert "tcve" in synthetic, "Missing tcve in synthetic"
        assert "tfe" in synthetic, "Missing tfe in synthetic"
        assert "bmpe" in synthetic, "Missing bmpe in synthetic"
        assert "computation_ms" in synthetic, "Missing computation_ms in synthetic"
        
        print(f"✓ Synthetic structure valid: tcve, tfe, bmpe, computation_ms={synthetic.get('computation_ms')}ms")
    
    def test_comparison_structure_real(self):
        """Real section has correct structure"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": "moose",
            "resolution": 30
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/shadow/full-comparison",
            json=payload,
            timeout=60
        )
        data = response.json()
        
        real = data.get("real", {})
        assert "tcve" in real, "Missing tcve in real"
        assert "tfe" in real, "Missing tfe in real"
        assert "bmpe" in real, "Missing bmpe in real"
        assert "computation_ms" in real, "Missing computation_ms in real"
        
        print(f"✓ Real structure valid: tcve, tfe, bmpe, computation_ms={real.get('computation_ms')}ms")
    
    def test_comparison_structure_deltas(self):
        """Deltas section has correct structure"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": "moose",
            "resolution": 30
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/shadow/full-comparison",
            json=payload,
            timeout=60
        )
        data = response.json()
        
        deltas = data.get("deltas", {})
        assert "tcve" in deltas, "Missing tcve in deltas"
        assert "tfe" in deltas, "Missing tfe in deltas"
        assert "bmpe" in deltas, "Missing bmpe in deltas"
        
        print(f"✓ Deltas structure valid: tcve, tfe, bmpe")
    
    def test_data_sources_status(self):
        """Data sources returns dem and weather status"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": "moose",
            "resolution": 30
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/shadow/full-comparison",
            json=payload,
            timeout=60
        )
        data = response.json()
        
        sources = data.get("data_sources", {})
        assert "dem" in sources, "Missing dem in data_sources"
        assert "weather" in sources, "Missing weather in data_sources"
        
        dem_status = sources["dem"]
        weather_status = sources["weather"]
        
        # DEM may be fallback_synthetic due to exhausted API quota
        assert dem_status in ["cache_hit", "api_fetched", "fallback_synthetic", "not_available"]
        # Weather should be from Open-Meteo
        assert weather_status in ["cache_hit", "api_fetched", "fallback_synthetic", "not_available"]
        
        print(f"✓ Data sources: DEM={dem_status}, Weather={weather_status}")
    
    def test_validation_shadow_mode(self):
        """Validation block confirms shadow mode"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": "moose",
            "resolution": 30
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/shadow/full-comparison",
            json=payload,
            timeout=60
        )
        data = response.json()
        
        validation = data.get("validation", {})
        assert validation.get("shadow_mode") is True, "shadow_mode should be True"
        assert validation.get("zero_impact_on_production") is True
        assert validation.get("certified_modules_unmodified") is True
        
        print(f"✓ Validation: shadow_mode=True, dem_injected={validation.get('dem_injected')}, weather_injected={validation.get('weather_injected')}")


class TestAllSpecies:
    """Test all supported species"""
    
    @pytest.mark.parametrize("species", SUPPORTED_SPECIES)
    def test_species_comparison(self, species):
        """Test each supported species"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": species,
            "resolution": 30
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/shadow/full-comparison",
            json=payload,
            timeout=60
        )
        
        assert response.status_code == 200, f"Species {species} failed: {response.status_code}"
        data = response.json()
        assert data["species"] == species
        print(f"✓ Species {species} comparison successful")


class TestResolutions:
    """Test different resolution values"""
    
    @pytest.mark.parametrize("resolution", [20, 30, 60])
    def test_resolution_value(self, resolution):
        """Test different resolutions (20, 30, 60)"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": "moose",
            "resolution": resolution
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/shadow/full-comparison",
            json=payload,
            timeout=60
        )
        
        assert response.status_code == 200, f"Resolution {resolution} failed: {response.status_code}"
        data = response.json()
        assert data["resolution"] == resolution
        print(f"✓ Resolution {resolution} comparison successful")


class TestComputationTimes:
    """Test computation times are returned"""
    
    def test_total_computation_time(self):
        """Total computation time is returned"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": "moose",
            "resolution": 30
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/shadow/full-comparison",
            json=payload,
            timeout=60
        )
        data = response.json()
        
        total_ms = data.get("total_computation_time_ms")
        assert total_ms is not None, "Missing total_computation_time_ms"
        assert isinstance(total_ms, (int, float)), f"total_computation_time_ms should be numeric, got {type(total_ms)}"
        assert total_ms > 0, "total_computation_time_ms should be positive"
        
        print(f"✓ Total computation time: {total_ms}ms")
    
    def test_pipeline_computation_times(self):
        """Both pipelines return computation times"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": "moose",
            "resolution": 30
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/shadow/full-comparison",
            json=payload,
            timeout=60
        )
        data = response.json()
        
        syn_ms = data.get("synthetic", {}).get("computation_ms")
        real_ms = data.get("real", {}).get("computation_ms")
        
        assert syn_ms is not None, "Missing synthetic computation_ms"
        assert real_ms is not None, "Missing real computation_ms"
        assert syn_ms > 0, "Synthetic computation_ms should be positive"
        assert real_ms > 0, "Real computation_ms should be positive"
        
        print(f"✓ Pipeline times: synthetic={syn_ms}ms, real={real_ms}ms")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
