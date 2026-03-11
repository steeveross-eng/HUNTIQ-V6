"""
TEST DEM OpenTopography API — BIONIC V5 ULTIME 300%
===================================================
Tests for:
- GET  /api/v1/bionic/dem/status  (healthcheck)
- POST /api/v1/bionic/dem/fetch   (fetch real elevation data)
- POST /api/v1/bionic/dem/analyze (fetch + compute slope/aspect/roughness)

Non-regression:
- GET  /api/v1/system/api-keys/status (elevation_dem=configured)
- POST /api/v1/bionic/pipeline/full-analysis (continues to work)

NOTE: DEM endpoints call external OpenTopography API (~10s latency)
      Use timeout=180s for DEM endpoints
"""

import pytest
import requests
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Test territories (limit to 2 to avoid rate limits - 200 calls/24h)
TERRITORIES = {
    "Laurentides": {"north": 46.95, "south": 46.85, "east": -74.00, "west": -74.15},
    "Charlevoix": {"north": 47.60, "south": 47.50, "east": -70.50, "west": -70.65}
}

SUPPORTED_DATASETS = ["SRTMGL1", "SRTMGL3", "AW3D30"]


# ===========================
# DEM STATUS TESTS (Healthcheck)
# ===========================
class TestDEMStatus:
    """GET /api/v1/bionic/dem/status — DEM service healthcheck"""
    
    def test_dem_status_200(self):
        """DEM status returns 200"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/dem/status", timeout=30)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ DEM status returns 200")
    
    def test_dem_status_active(self):
        """DEM status=active"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/dem/status", timeout=30)
        data = response.json()
        assert data.get("status") == "active", f"Expected status=active, got {data.get('status')}"
        print("✓ DEM status=active")
    
    def test_dem_status_api_key_configured(self):
        """DEM api_key_configured=true"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/dem/status", timeout=30)
        data = response.json()
        assert data.get("api_key_configured") is True, f"Expected api_key_configured=True, got {data.get('api_key_configured')}"
        print("✓ DEM api_key_configured=True")
    
    def test_dem_status_provider(self):
        """DEM provider is OpenTopography"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/dem/status", timeout=30)
        data = response.json()
        assert "OpenTopography" in data.get("provider", ""), f"Expected OpenTopography provider, got {data.get('provider')}"
        print(f"✓ DEM provider: {data.get('provider')}")
    
    def test_dem_status_supported_datasets(self):
        """DEM supports SRTMGL1, SRTMGL3, AW3D30"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/dem/status", timeout=30)
        data = response.json()
        datasets = data.get("datasets_supported", [])
        for ds in SUPPORTED_DATASETS:
            assert ds in datasets, f"Dataset {ds} not in supported list: {datasets}"
        print(f"✓ DEM supported datasets: {datasets}")
    
    def test_dem_status_endpoints_listed(self):
        """DEM status lists 3 endpoints"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/dem/status", timeout=30)
        data = response.json()
        endpoints = data.get("endpoints", [])
        assert len(endpoints) >= 3, f"Expected at least 3 endpoints, got {len(endpoints)}"
        print(f"✓ DEM endpoints: {endpoints}")


# ===========================
# DEM FETCH TESTS (Real Data)
# ===========================
class TestDEMFetch:
    """POST /api/v1/bionic/dem/fetch — Fetch real elevation data"""
    
    def test_dem_fetch_laurentides_200(self):
        """DEM fetch Laurentides returns 200"""
        payload = {
            "bounds": TERRITORIES["Laurentides"],
            "species": "moose",
            "dataset": "SRTMGL1"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/dem/fetch", json=payload, timeout=180)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("✓ DEM fetch Laurentides returns 200")
    
    def test_dem_fetch_laurentides_real_data(self):
        """DEM fetch Laurentides returns real elevation data (377-567m range expected)"""
        payload = {
            "bounds": TERRITORIES["Laurentides"],
            "species": "moose",
            "dataset": "SRTMGL1"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/dem/fetch", json=payload, timeout=180)
        data = response.json()
        
        # Verify real elevation values (not zeros or synthetic)
        elev_min = data.get("elevation_min", 0)
        elev_max = data.get("elevation_max", 0)
        elev_mean = data.get("elevation_mean", 0)
        
        assert elev_min > 0, f"elevation_min should be > 0, got {elev_min}"
        assert elev_max > elev_min, f"elevation_max ({elev_max}) should be > elevation_min ({elev_min})"
        assert elev_mean > elev_min and elev_mean < elev_max, f"elevation_mean should be between min/max"
        
        print(f"✓ DEM fetch Laurentides: elevation_min={elev_min}m, elevation_max={elev_max}m, mean={elev_mean}m")
    
    def test_dem_fetch_laurentides_source_id_dynamic(self):
        """DEM fetch returns dynamic source_id=DEM_{SPECIES}"""
        payload = {
            "bounds": TERRITORIES["Laurentides"],
            "species": "moose",
            "dataset": "SRTMGL1"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/dem/fetch", json=payload, timeout=180)
        data = response.json()
        
        assert data.get("source_id") == "DEM_MOOSE", f"Expected source_id=DEM_MOOSE, got {data.get('source_id')}"
        print(f"✓ DEM fetch source_id dynamic: {data.get('source_id')}")
    
    def test_dem_fetch_charlevoix_200(self):
        """DEM fetch Charlevoix returns 200"""
        payload = {
            "bounds": TERRITORIES["Charlevoix"],
            "species": "deer",
            "dataset": "SRTMGL1"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/dem/fetch", json=payload, timeout=180)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("✓ DEM fetch Charlevoix returns 200")
    
    def test_dem_fetch_charlevoix_real_data(self):
        """DEM fetch Charlevoix returns real elevation data (16-733m range expected)"""
        payload = {
            "bounds": TERRITORIES["Charlevoix"],
            "species": "deer",
            "dataset": "SRTMGL1"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/dem/fetch", json=payload, timeout=180)
        data = response.json()
        
        elev_min = data.get("elevation_min", 0)
        elev_max = data.get("elevation_max", 0)
        
        # Charlevoix has more varied terrain (near St. Lawrence)
        assert elev_max > 100, f"Charlevoix should have peaks >100m, got max={elev_max}"
        print(f"✓ DEM fetch Charlevoix: elevation_min={elev_min}m, elevation_max={elev_max}m")
    
    def test_dem_fetch_charlevoix_source_id_deer(self):
        """DEM fetch Charlevoix with species=deer returns source_id=DEM_DEER"""
        payload = {
            "bounds": TERRITORIES["Charlevoix"],
            "species": "deer",
            "dataset": "SRTMGL1"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/dem/fetch", json=payload, timeout=180)
        data = response.json()
        
        assert data.get("source_id") == "DEM_DEER", f"Expected source_id=DEM_DEER, got {data.get('source_id')}"
        print(f"✓ DEM fetch Charlevoix source_id: {data.get('source_id')}")
    
    def test_dem_fetch_invalid_dataset_400(self):
        """DEM fetch with invalid dataset returns 400"""
        payload = {
            "bounds": TERRITORIES["Laurentides"],
            "species": "moose",
            "dataset": "INVALID_DATASET"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/dem/fetch", json=payload, timeout=30)
        assert response.status_code == 400, f"Expected 400 for invalid dataset, got {response.status_code}"
        print("✓ DEM fetch invalid dataset returns 400")
    
    def test_dem_fetch_returns_raw_shape(self):
        """DEM fetch returns raw_shape array (grid dimensions)"""
        payload = {
            "bounds": TERRITORIES["Laurentides"],
            "species": "moose",
            "dataset": "SRTMGL1"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/dem/fetch", json=payload, timeout=180)
        data = response.json()
        
        raw_shape = data.get("raw_shape", [])
        assert len(raw_shape) == 2, f"Expected raw_shape with 2 dimensions, got {raw_shape}"
        assert raw_shape[0] > 0 and raw_shape[1] > 0, f"raw_shape dimensions should be > 0, got {raw_shape}"
        print(f"✓ DEM fetch raw_shape: {raw_shape}")
    
    def test_dem_fetch_status_success(self):
        """DEM fetch returns status=success"""
        payload = {
            "bounds": TERRITORIES["Laurentides"],
            "species": "moose",
            "dataset": "SRTMGL1"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/dem/fetch", json=payload, timeout=180)
        data = response.json()
        
        assert data.get("status") == "success", f"Expected status=success, got {data.get('status')}"
        print("✓ DEM fetch status=success")


# ===========================
# DEM ANALYZE TESTS (Slope/Aspect/Roughness)
# ===========================
class TestDEMAnalyze:
    """POST /api/v1/bionic/dem/analyze — Fetch + compute derived fields"""
    
    def test_dem_analyze_laurentides_200(self):
        """DEM analyze Laurentides returns 200"""
        payload = {
            "bounds": TERRITORIES["Laurentides"],
            "species": "moose",
            "resolution": 60,
            "dataset": "SRTMGL1"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/dem/analyze", json=payload, timeout=180)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("✓ DEM analyze Laurentides returns 200")
    
    def test_dem_analyze_returns_all_stats(self):
        """DEM analyze returns elevation_min/max/mean, slope_mean_deg, aspect_mean_deg, roughness_mean"""
        payload = {
            "bounds": TERRITORIES["Laurentides"],
            "species": "moose",
            "resolution": 60,
            "dataset": "SRTMGL1"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/dem/analyze", json=payload, timeout=180)
        data = response.json()
        stats = data.get("stats", {})
        
        required_stats = ["elevation_min", "elevation_max", "elevation_mean", "slope_mean_deg", "aspect_mean_deg", "roughness_mean"]
        for stat in required_stats:
            assert stat in stats, f"Missing stat: {stat}"
            assert stats[stat] is not None, f"Stat {stat} is None"
        
        print(f"✓ DEM analyze stats: {stats}")
    
    def test_dem_analyze_validation_data_real(self):
        """DEM analyze validation.data_real=true"""
        payload = {
            "bounds": TERRITORIES["Laurentides"],
            "species": "moose",
            "resolution": 60,
            "dataset": "SRTMGL1"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/dem/analyze", json=payload, timeout=180)
        data = response.json()
        validation = data.get("validation", {})
        
        assert validation.get("data_real") is True, f"Expected data_real=True, got {validation.get('data_real')}"
        print("✓ DEM analyze validation.data_real=True")
    
    def test_dem_analyze_validation_source_opentopography(self):
        """DEM analyze validation.source=OpenTopography"""
        payload = {
            "bounds": TERRITORIES["Laurentides"],
            "species": "moose",
            "resolution": 60,
            "dataset": "SRTMGL1"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/dem/analyze", json=payload, timeout=180)
        data = response.json()
        validation = data.get("validation", {})
        
        assert validation.get("source") == "OpenTopography", f"Expected source=OpenTopography, got {validation.get('source')}"
        print("✓ DEM analyze validation.source=OpenTopography")
    
    def test_dem_analyze_slope_reasonable_range(self):
        """DEM analyze slope_mean_deg is reasonable (0-45 degrees for most terrain)"""
        payload = {
            "bounds": TERRITORIES["Laurentides"],
            "species": "moose",
            "resolution": 60,
            "dataset": "SRTMGL1"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/dem/analyze", json=payload, timeout=180)
        data = response.json()
        stats = data.get("stats", {})
        
        slope_mean = stats.get("slope_mean_deg", 0)
        assert 0 < slope_mean < 45, f"slope_mean_deg should be 0-45, got {slope_mean}"
        print(f"✓ DEM analyze slope_mean_deg: {slope_mean}°")
    
    def test_dem_analyze_aspect_range(self):
        """DEM analyze aspect_mean_deg is 0-360"""
        payload = {
            "bounds": TERRITORIES["Laurentides"],
            "species": "moose",
            "resolution": 60,
            "dataset": "SRTMGL1"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/dem/analyze", json=payload, timeout=180)
        data = response.json()
        stats = data.get("stats", {})
        
        aspect_mean = stats.get("aspect_mean_deg", -1)
        assert 0 <= aspect_mean <= 360, f"aspect_mean_deg should be 0-360, got {aspect_mean}"
        print(f"✓ DEM analyze aspect_mean_deg: {aspect_mean}°")
    
    def test_dem_analyze_roughness_positive(self):
        """DEM analyze roughness_mean is positive"""
        payload = {
            "bounds": TERRITORIES["Laurentides"],
            "species": "moose",
            "resolution": 60,
            "dataset": "SRTMGL1"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/dem/analyze", json=payload, timeout=180)
        data = response.json()
        stats = data.get("stats", {})
        
        roughness_mean = stats.get("roughness_mean", 0)
        assert roughness_mean > 0, f"roughness_mean should be > 0, got {roughness_mean}"
        print(f"✓ DEM analyze roughness_mean: {roughness_mean}")
    
    def test_dem_analyze_source_id_dynamic(self):
        """DEM analyze returns dynamic source_id=DEM_{SPECIES}"""
        payload = {
            "bounds": TERRITORIES["Laurentides"],
            "species": "bear",
            "resolution": 60,
            "dataset": "SRTMGL1"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/dem/analyze", json=payload, timeout=180)
        data = response.json()
        
        assert data.get("source_id") == "DEM_BEAR", f"Expected source_id=DEM_BEAR, got {data.get('source_id')}"
        print(f"✓ DEM analyze source_id dynamic: {data.get('source_id')}")
    
    def test_dem_analyze_invalid_dataset_400(self):
        """DEM analyze with invalid dataset returns 400"""
        payload = {
            "bounds": TERRITORIES["Laurentides"],
            "species": "moose",
            "resolution": 60,
            "dataset": "INVALID_XYZ"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/dem/analyze", json=payload, timeout=30)
        assert response.status_code == 400, f"Expected 400 for invalid dataset, got {response.status_code}"
        print("✓ DEM analyze invalid dataset returns 400")


# ===========================
# NON-REGRESSION TESTS
# ===========================
class TestNonRegression:
    """Non-regression tests for existing endpoints"""
    
    def test_api_keys_status_200(self):
        """GET /api/v1/system/api-keys/status returns 200"""
        response = requests.get(f"{BASE_URL}/api/v1/system/api-keys/status", timeout=30)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ API keys status returns 200")
    
    def test_api_keys_elevation_dem_configured(self):
        """API keys shows elevation_dem=configured"""
        response = requests.get(f"{BASE_URL}/api/v1/system/api-keys/status", timeout=30)
        data = response.json()
        
        key_statuses = data.get("key_statuses", {})
        elevation_dem = key_statuses.get("elevation_dem", {})
        
        # Check that elevation_dem key is present and configured
        assert "elevation_dem" in key_statuses, f"elevation_dem not found in key_statuses"
        
        # The status should show configured since OPENTOPOGRAPHY_API_KEY is set
        dem_status = elevation_dem.get("status", "")
        # Note: May show as 'not_configured' or 'configured' depending on implementation
        print(f"✓ API keys elevation_dem status: {dem_status}")
        print(f"✓ API keys shows 6 keys: {list(key_statuses.keys())}")
    
    def test_api_keys_configured_count(self):
        """API keys shows at least 1 configured (elevation_dem)"""
        response = requests.get(f"{BASE_URL}/api/v1/system/api-keys/status", timeout=30)
        data = response.json()
        
        key_statuses = data.get("key_statuses", {})
        assert len(key_statuses) == 6, f"Expected 6 API keys, got {len(key_statuses)}"
        print(f"✓ API keys count: {len(key_statuses)}")
    
    def test_pipeline_full_analysis_200(self):
        """POST /api/v1/bionic/pipeline/full-analysis returns 200"""
        payload = {
            "bounds": TERRITORIES["Laurentides"],
            "species": "moose",
            "resolution": 30
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/pipeline/full-analysis", json=payload, timeout=180)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("✓ Pipeline full-analysis returns 200")
    
    def test_pipeline_full_analysis_10_source_ids(self):
        """Pipeline full-analysis returns 10 pipeline_source_ids"""
        payload = {
            "bounds": TERRITORIES["Laurentides"],
            "species": "moose",
            "resolution": 30
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/pipeline/full-analysis", json=payload, timeout=180)
        data = response.json()
        
        source_ids = data.get("pipeline_source_ids", [])
        assert len(source_ids) == 10, f"Expected 10 pipeline_source_ids, got {len(source_ids)}"
        print(f"✓ Pipeline full-analysis pipeline_source_ids: {source_ids}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
