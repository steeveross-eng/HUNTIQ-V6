"""
BIONIC V5 - CALIBRATION MASTER Infrastructure Tests
======================================================
Tests for the Calibration MASTER pipeline including:
- MongoDB CRUD operations for observations terrain
- Calibration metrics dashboard
- Phase G validation endpoints
- Non-regression tests for seasonal endpoints

Test Data: Uses TEST_ prefix for cleanup
Version: 1.0.0
"""

import pytest
import requests
import os
import time
from datetime import datetime, timezone

# Base URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# ============================================================================
# TEST DATA
# ============================================================================

TEST_OBSERVATION_DATA = {
    "latitude": 46.8139,
    "longitude": -71.2080,
    "species": "orignal",
    "observed_behavior": "alimentation",
    "observation_datetime": datetime.now(timezone.utc).isoformat(),
    "region": "CA-QC",
    "notes": "TEST_observation created by pytest",
    "confidence": 0.85,
    "source_ids": ["TEST-SRC-PYTEST"]
}

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def api_client():
    """Shared requests session for API calls."""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session

@pytest.fixture
def created_observation(api_client):
    """Create a test observation and return its ID for cleanup."""
    response = api_client.post(
        f"{BASE_URL}/api/v1/bionic/calibration/observations",
        json=TEST_OBSERVATION_DATA
    )
    if response.status_code == 201:
        data = response.json()
        obs_id = data.get("observation", {}).get("observation_id")
        yield obs_id
        # Cleanup
        if obs_id:
            api_client.delete(f"{BASE_URL}/api/v1/bionic/calibration/observations/{obs_id}")
    else:
        pytest.skip(f"Could not create test observation: {response.status_code}")


# ============================================================================
# CALIBRATION OBSERVATIONS CRUD TESTS
# ============================================================================

class TestCalibrationObservationsCRUD:
    """Tests for MongoDB-backed observation CRUD endpoints."""
    
    def test_create_observation_returns_201(self, api_client):
        """POST /calibration/observations creates observation with 201."""
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/calibration/observations",
            json=TEST_OBSERVATION_DATA
        )
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "created"
        assert "observation" in data
        
        obs = data["observation"]
        assert "observation_id" in obs
        assert obs["species"] == "orignal"
        assert obs["observed_behavior"] == "alimentation"
        assert "source_ids" in obs
        assert "version" in obs
        
        # Cleanup
        obs_id = obs["observation_id"]
        api_client.delete(f"{BASE_URL}/api/v1/bionic/calibration/observations/{obs_id}")
        print(f"✓ Created observation: {obs_id}")
    
    def test_create_observation_has_required_fields(self, api_client):
        """Created observation has source_ids and version fields."""
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/calibration/observations",
            json=TEST_OBSERVATION_DATA
        )
        assert response.status_code == 201
        
        obs = response.json()["observation"]
        
        # Check required traceability fields
        assert "source_ids" in obs, "Missing source_ids field"
        assert isinstance(obs["source_ids"], list), "source_ids should be a list"
        assert len(obs["source_ids"]) > 0, "source_ids should not be empty"
        
        assert "version" in obs, "Missing version field"
        assert obs["version"] == "1.0.0", f"Expected version 1.0.0, got {obs['version']}"
        
        assert "status" in obs, "Missing status field"
        assert obs["status"] == "pending", f"Expected status pending, got {obs['status']}"
        
        # Cleanup
        api_client.delete(f"{BASE_URL}/api/v1/bionic/calibration/observations/{obs['observation_id']}")
        print("✓ Observation has source_ids, version, and status fields")
    
    def test_list_observations_returns_200(self, api_client, created_observation):
        """GET /calibration/observations returns list with 200."""
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/calibration/observations")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "observations" in data
        assert "total" in data
        assert "limit" in data
        assert "skip" in data
        
        assert isinstance(data["observations"], list)
        print(f"✓ Listed {len(data['observations'])} observations (total: {data['total']})")
    
    def test_list_observations_with_species_filter(self, api_client, created_observation):
        """GET /calibration/observations?species=orignal filters correctly."""
        response = api_client.get(
            f"{BASE_URL}/api/v1/bionic/calibration/observations",
            params={"species": "orignal"}
        )
        assert response.status_code == 200
        
        data = response.json()
        # All returned observations should be orignal
        for obs in data["observations"]:
            assert obs["species"] == "orignal", f"Expected orignal, got {obs['species']}"
        print(f"✓ Species filter returned {len(data['observations'])} orignal observations")
    
    def test_list_observations_with_status_filter(self, api_client, created_observation):
        """GET /calibration/observations?status=pending filters correctly."""
        response = api_client.get(
            f"{BASE_URL}/api/v1/bionic/calibration/observations",
            params={"status": "pending"}
        )
        assert response.status_code == 200
        
        data = response.json()
        for obs in data["observations"]:
            assert obs["status"] == "pending", f"Expected pending, got {obs['status']}"
        print(f"✓ Status filter returned {len(data['observations'])} pending observations")
    
    def test_get_observation_by_id_returns_200(self, api_client, created_observation):
        """GET /calibration/observations/{id} returns specific observation."""
        response = api_client.get(
            f"{BASE_URL}/api/v1/bionic/calibration/observations/{created_observation}"
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        obs = response.json()
        assert obs["observation_id"] == created_observation
        assert obs["species"] == "orignal"
        print(f"✓ Retrieved observation: {created_observation}")
    
    def test_get_observation_not_found_returns_404(self, api_client):
        """GET /calibration/observations/{invalid_id} returns 404."""
        response = api_client.get(
            f"{BASE_URL}/api/v1/bionic/calibration/observations/OBS-INVALID-NOTEXIST"
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Invalid observation ID returns 404")
    
    def test_delete_observation_returns_200(self, api_client):
        """DELETE /calibration/observations/{id} removes observation."""
        # First create one
        create_resp = api_client.post(
            f"{BASE_URL}/api/v1/bionic/calibration/observations",
            json=TEST_OBSERVATION_DATA
        )
        assert create_resp.status_code == 201
        obs_id = create_resp.json()["observation"]["observation_id"]
        
        # Delete it
        del_resp = api_client.delete(
            f"{BASE_URL}/api/v1/bionic/calibration/observations/{obs_id}"
        )
        assert del_resp.status_code == 200, f"Expected 200, got {del_resp.status_code}"
        
        data = del_resp.json()
        assert data["status"] == "deleted"
        assert data["observation_id"] == obs_id
        
        # Verify it's gone
        get_resp = api_client.get(
            f"{BASE_URL}/api/v1/bionic/calibration/observations/{obs_id}"
        )
        assert get_resp.status_code == 404, "Observation should be deleted"
        print(f"✓ Deleted observation: {obs_id}")
    
    def test_delete_observation_not_found_returns_404(self, api_client):
        """DELETE /calibration/observations/{invalid_id} returns 404."""
        response = api_client.delete(
            f"{BASE_URL}/api/v1/bionic/calibration/observations/OBS-INVALID-DELETE"
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Delete invalid observation returns 404")


# ============================================================================
# CALIBRATION METRICS TESTS
# ============================================================================

class TestCalibrationMetrics:
    """Tests for calibration metrics dashboard endpoints."""
    
    def test_observations_metrics_returns_200(self, api_client):
        """GET /calibration/observations-metrics returns dashboard data."""
        response = api_client.get(
            f"{BASE_URL}/api/v1/bionic/calibration/observations-metrics"
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "observations_breakdown" in data, "Missing observations_breakdown"
        
        breakdown = data["observations_breakdown"]
        assert "total" in breakdown
        assert "compared" in breakdown
        assert "pending" in breakdown
        
        print(f"✓ Metrics: total={breakdown['total']}, compared={breakdown['compared']}, pending={breakdown['pending']}")
    
    def test_observations_metrics_has_precision_data(self, api_client):
        """Metrics endpoint returns precision data structure."""
        response = api_client.get(
            f"{BASE_URL}/api/v1/bionic/calibration/observations-metrics"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "precision" in data, "Missing precision data"
        assert "statistics" in data, "Missing statistics data"
        
        precision = data["precision"]
        assert "global" in precision
        assert "spatial" in precision
        assert "temporal" in precision
        assert "behavioral" in precision
        
        print(f"✓ Precision: global={precision['global']}, spatial={precision['spatial']}")
    
    def test_calibration_status_returns_200(self, api_client):
        """GET /calibration/calibration-status returns calibration status."""
        response = api_client.get(
            f"{BASE_URL}/api/v1/bionic/calibration/calibration-status"
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "calibration_status" in data
        assert "model_version" in data
        assert "global_precision" in data
        assert "target_precision" in data
        assert "is_master_ready" in data
        assert "observations_count" in data
        assert "source_ids" in data
        assert "version" in data
        
        print(f"✓ Calibration status: {data['calibration_status']}, precision: {data['global_precision']}")


# ============================================================================
# PHASE G VALIDATION TESTS
# ============================================================================

class TestPhaseGValidation:
    """Tests for Phase G validation structure endpoints."""
    
    def test_phase_g_plan_returns_200(self, api_client):
        """GET /validation/phase-g/plan returns validation plan."""
        response = api_client.get(
            f"{BASE_URL}/api/v1/bionic/validation/phase-g/plan"
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "plan_id" in data
        assert "version" in data
        assert "status" in data
        assert "target_species" in data
        assert "species_profiles" in data
        assert "source_ids" in data
        
        print(f"✓ Phase G plan: {data['plan_id']}, status: {data['status']}")
    
    def test_phase_g_plan_has_species_profiles(self, api_client):
        """Phase G plan contains species validation profiles."""
        response = api_client.get(
            f"{BASE_URL}/api/v1/bionic/validation/phase-g/plan"
        )
        assert response.status_code == 200
        
        data = response.json()
        profiles = data.get("species_profiles", {})
        
        # Should have at least orignal, cerf_de_virginie, ours_noir
        assert "orignal" in profiles, "Missing orignal profile"
        assert "cerf_de_virginie" in profiles, "Missing cerf_de_virginie profile"
        assert "ours_noir" in profiles, "Missing ours_noir profile"
        
        # Check orignal profile structure
        orignal = profiles["orignal"]
        assert "species" in orignal
        assert "tier" in orignal
        assert "min_observations" in orignal
        assert "target_precision" in orignal
        assert "thresholds" in orignal
        
        print(f"✓ Phase G has {len(profiles)} species profiles: {list(profiles.keys())}")
    
    def test_phase_g_progress_returns_200(self, api_client):
        """GET /validation/phase-g/progress returns progress data."""
        response = api_client.get(
            f"{BASE_URL}/api/v1/bionic/validation/phase-g/progress"
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "phase" in data
        assert data["phase"] == "G"
        assert "progress" in data
        assert "source_ids" in data
        assert "version" in data
        
        progress = data["progress"]
        assert "species_validated" in progress
        assert "species_total" in progress
        assert "observations_collected" in progress
        assert "observations_needed" in progress
        assert "is_complete" in progress
        
        print(f"✓ Phase G progress: {progress['species_validated']}/{progress['species_total']} species")


# ============================================================================
# NON-REGRESSION TESTS (PHASE C SEASONAL)
# ============================================================================

class TestNonRegressionSeasonal:
    """Non-regression tests for Phase C seasonal endpoints."""
    
    def test_seasonal_status_still_works(self, api_client):
        """GET /seasonal/status returns 200 (non-regression)."""
        response = api_client.get(
            f"{BASE_URL}/api/v1/bionic/seasonal/status",
            params={"species": "orignal", "region": "CA-QC"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["phase"] == "C"
        assert "factors" in data
        
        factors = data["factors"]
        assert "C1_calving" in factors
        assert "C2_dispersal" in factors
        assert "C3_thermal_stress" in factors
        assert "C4_hunting_pressure" in factors
        
        print(f"✓ Non-regression: /seasonal/status works with {len(factors)} factors")
    
    def test_seasonal_health_still_works(self, api_client):
        """GET /seasonal/health returns operational (non-regression)."""
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/seasonal/health")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["phase"] == "C"
        assert data["status"] == "operational"
        assert "modules" in data
        
        modules = data["modules"]
        assert modules.get("C1_calving") == "active"
        assert modules.get("C2_dispersal") == "active"
        assert modules.get("C3_thermal_stress") == "active"
        assert modules.get("C4_hunting_pressure") == "active"
        
        print("✓ Non-regression: /seasonal/health operational with 4 active modules")


# ============================================================================
# CALIBRATION DASHBOARD EXISTING ENDPOINTS TESTS
# ============================================================================

class TestCalibrationDashboardEndpoints:
    """Tests for in-memory CalibrationOptimizer endpoints."""
    
    def test_calibration_dashboard_returns_200(self, api_client):
        """GET /calibration/dashboard returns dashboard data."""
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/calibration/dashboard")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["status"] == "success"
        assert "dashboard" in data
        print("✓ Calibration dashboard endpoint works")
    
    def test_calibration_comparisons_returns_200(self, api_client):
        """GET /calibration/comparisons returns comparisons list."""
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/calibration/comparisons")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["status"] == "success"
        assert "comparisons" in data
        assert isinstance(data["comparisons"], list)
        print(f"✓ Comparisons endpoint works: {len(data['comparisons'])} comparisons")
    
    def test_calibration_suggestions_returns_200(self, api_client):
        """GET /calibration/suggestions returns suggestions list."""
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/calibration/suggestions")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["status"] == "success"
        assert "suggestions" in data
        print(f"✓ Suggestions endpoint works: {len(data['suggestions'])} suggestions")
    
    def test_master_status_returns_200(self, api_client):
        """GET /calibration/master-status returns master status."""
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/calibration/master-status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["status"] == "success"
        assert "master_status" in data
        
        master = data["master_status"]
        assert "is_ready" in master
        assert "current_precision" in master
        assert "target_precision" in master
        print(f"✓ Master status: is_ready={master['is_ready']}, precision={master['current_precision']}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
