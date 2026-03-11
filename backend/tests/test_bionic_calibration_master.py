"""
BIONIC V5 — CALIBRATION MASTER TESTS
=====================================
Tests for the calibration system (PHASE F → MASTER)

Tests:
- Health check
- Dashboard data
- Compare prediction vs observation
- Suggestions CRUD
- Master status and locking
"""

import pytest
import requests
import os
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
CALIBRATION_URL = f"{BASE_URL}/api/v1/bionic/calibration"


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture
def sample_comparison_payload():
    """Sample comparison request payload"""
    now = datetime.utcnow()
    prediction_time = now - timedelta(minutes=30)
    observation_time = now
    
    return {
        "observation_id": f"OBS-TEST-{now.strftime('%Y%m%d%H%M%S')}",
        "predicted_lat": 46.8139,
        "predicted_lng": -71.2080,
        "predicted_behavior": "feeding",
        "predicted_score": 72.5,
        "prediction_timestamp": prediction_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "observed_lat": 46.8145,
        "observed_lng": -71.2075,
        "observed_behavior": "feeding",
        "observed_timestamp": observation_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "species": "moose",
        "season": "winter"
    }


# =============================================================================
# HEALTH TESTS
# =============================================================================

class TestCalibrationHealth:
    """Health check endpoint tests"""
    
    def test_health_returns_200(self, api_client):
        """Test health endpoint returns 200"""
        response = api_client.get(f"{CALIBRATION_URL}/health")
        assert response.status_code == 200
        print("✓ Health endpoint returns 200")
    
    def test_health_response_structure(self, api_client):
        """Test health response structure"""
        response = api_client.get(f"{CALIBRATION_URL}/health")
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["version"] == "7.1.0"
        assert data["phase"] == "CALIBRATION VERS MASTER"
        assert "optimizer" in data
        assert "registry" in data
        assert "features" in data
        
        # Verify features list
        expected_features = [
            "compare_prediction_vs_observation",
            "calibration_dashboard",
            "suggestion_generation",
            "manual_validation",
            "master_locking"
        ]
        for feature in expected_features:
            assert feature in data["features"]
        
        print(f"✓ Health structure validated: v{data['version']}, {len(data['features'])} features")


# =============================================================================
# DASHBOARD TESTS
# =============================================================================

class TestCalibrationDashboard:
    """Dashboard endpoint tests"""
    
    def test_dashboard_returns_200(self, api_client):
        """Test dashboard endpoint returns 200"""
        response = api_client.get(f"{CALIBRATION_URL}/dashboard")
        assert response.status_code == 200
        print("✓ Dashboard endpoint returns 200")
    
    def test_dashboard_response_structure(self, api_client):
        """Test dashboard response structure"""
        response = api_client.get(f"{CALIBRATION_URL}/dashboard")
        data = response.json()
        
        assert data["status"] == "success"
        assert "dashboard" in data
        
        dashboard = data["dashboard"]
        
        # Verify precision structure
        assert "precision" in dashboard
        precision = dashboard["precision"]
        assert "global" in precision
        assert "target" in precision
        assert "gap" in precision
        assert "spatial" in precision
        assert "temporal" in precision
        assert "behavioral" in precision
        assert precision["target"] == 95.0
        
        # Verify statistics structure
        assert "statistics" in dashboard
        stats = dashboard["statistics"]
        assert "total_observations" in stats
        assert "total_comparisons" in stats
        assert "observations_this_week" in stats
        
        # Verify master status
        assert "master_status" in dashboard
        assert "is_ready" in dashboard["master_status"]
        
        print(f"✓ Dashboard structure validated: precision={precision['global']:.1f}%, comparisons={stats['total_comparisons']}")
    
    def test_dashboard_has_profile_and_version(self, api_client):
        """Test dashboard includes calibration profile and model version"""
        response = api_client.get(f"{CALIBRATION_URL}/dashboard")
        data = response.json()
        dashboard = data["dashboard"]
        
        # Verify calibration profile
        assert "calibration_profile" in dashboard
        profile = dashboard["calibration_profile"]
        assert "profile_id" in profile
        assert "service_weights" in profile
        assert "level_modifiers" in profile
        assert "thresholds" in profile
        
        # Verify model version
        assert "model_version" in dashboard
        version = dashboard["model_version"]
        assert "version_id" in version
        assert "version_number" in version
        assert "status" in version
        
        print(f"✓ Profile and version validated: profile={profile['profile_id']}, version={version['version_number']}")


# =============================================================================
# COMPARISON TESTS
# =============================================================================

class TestCalibrationCompare:
    """Compare prediction vs observation tests"""
    
    def test_compare_creates_comparison(self, api_client, sample_comparison_payload):
        """Test creating a comparison"""
        response = api_client.post(
            f"{CALIBRATION_URL}/compare",
            json=sample_comparison_payload
        )
        assert response.status_code == 201
        
        data = response.json()
        assert data["status"] == "success"
        assert "comparison" in data
        assert "current_precision" in data
        
        print(f"✓ Comparison created: {data['comparison']['comparison_id']}")
    
    def test_compare_response_structure(self, api_client, sample_comparison_payload):
        """Test comparison response structure"""
        response = api_client.post(
            f"{CALIBRATION_URL}/compare",
            json=sample_comparison_payload
        )
        data = response.json()
        
        comparison = data["comparison"]
        assert "comparison_id" in comparison
        assert "observation_id" in comparison
        assert "prediction" in comparison
        assert "observation" in comparison
        assert "errors" in comparison
        assert "concordance" in comparison
        assert "context" in comparison
        
        # Verify concordance structure
        concordance = comparison["concordance"]
        assert "spatial" in concordance
        assert "temporal" in concordance
        assert "behavioral" in concordance
        assert "global" in concordance
        
        # Verify current precision update
        current_precision = data["current_precision"]
        assert "global" in current_precision
        assert "target" in current_precision
        assert "is_master_ready" in current_precision
        
        print(f"✓ Comparison structure validated: global_concordance={concordance['global']:.1f}%")
    
    def test_compare_behavior_mismatch(self, api_client):
        """Test comparison with behavior mismatch"""
        now = datetime.utcnow()
        payload = {
            "observation_id": f"OBS-MISMATCH-{now.strftime('%Y%m%d%H%M%S')}",
            "predicted_lat": 46.8139,
            "predicted_lng": -71.2080,
            "predicted_behavior": "resting",
            "predicted_score": 65.0,
            "prediction_timestamp": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "observed_lat": 46.8145,
            "observed_lng": -71.2075,
            "observed_behavior": "feeding",  # Different behavior
            "observed_timestamp": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "species": "deer",
            "season": "winter"
        }
        
        response = api_client.post(f"{CALIBRATION_URL}/compare", json=payload)
        assert response.status_code == 201
        
        data = response.json()
        comparison = data["comparison"]
        
        # Behavior should not match
        assert comparison["errors"]["behavior_match"] == False
        # Behavioral concordance should be lower (30%)
        assert comparison["concordance"]["behavioral"] == 30.0
        
        print(f"✓ Behavior mismatch test passed: behavioral={comparison['concordance']['behavioral']}%")
    
    def test_compare_with_large_spatial_error(self, api_client):
        """Test comparison with significant spatial error"""
        now = datetime.utcnow()
        payload = {
            "observation_id": f"OBS-SPATIAL-{now.strftime('%Y%m%d%H%M%S')}",
            "predicted_lat": 46.8000,  # Farther away
            "predicted_lng": -71.2000,
            "predicted_behavior": "feeding",
            "predicted_score": 70.0,
            "prediction_timestamp": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "observed_lat": 46.8145,
            "observed_lng": -71.2075,
            "observed_behavior": "feeding",
            "observed_timestamp": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "species": "moose",
            "season": "winter"
        }
        
        response = api_client.post(f"{CALIBRATION_URL}/compare", json=payload)
        assert response.status_code == 201
        
        data = response.json()
        comparison = data["comparison"]
        
        # Spatial error should be significant
        assert comparison["errors"]["spatial_m"] > 500
        # Spatial concordance should be lower
        assert comparison["concordance"]["spatial"] < 90
        
        print(f"✓ Large spatial error test passed: spatial_m={comparison['errors']['spatial_m']:.0f}m, concordance={comparison['concordance']['spatial']:.1f}%")


class TestListComparisons:
    """List comparisons endpoint tests"""
    
    def test_list_comparisons_returns_200(self, api_client):
        """Test list comparisons returns 200"""
        response = api_client.get(f"{CALIBRATION_URL}/comparisons")
        assert response.status_code == 200
        print("✓ List comparisons returns 200")
    
    def test_list_comparisons_structure(self, api_client):
        """Test list comparisons response structure"""
        response = api_client.get(f"{CALIBRATION_URL}/comparisons")
        data = response.json()
        
        assert data["status"] == "success"
        assert "total" in data
        assert "comparisons" in data
        assert isinstance(data["comparisons"], list)
        
        print(f"✓ List comparisons structure validated: {data['total']} comparisons")
    
    def test_list_comparisons_with_limit(self, api_client):
        """Test list comparisons with limit parameter"""
        response = api_client.get(f"{CALIBRATION_URL}/comparisons?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["comparisons"]) <= 5
        
        print(f"✓ List comparisons with limit: returned {len(data['comparisons'])} comparisons")


# =============================================================================
# SUGGESTIONS TESTS
# =============================================================================

class TestGenerateSuggestions:
    """Generate suggestions endpoint tests"""
    
    def test_generate_suggestions_returns_200(self, api_client):
        """Test generate suggestions returns 200"""
        response = api_client.post(f"{CALIBRATION_URL}/suggestions/generate")
        assert response.status_code == 200
        print("✓ Generate suggestions returns 200")
    
    def test_generate_suggestions_response_structure(self, api_client):
        """Test generate suggestions response structure"""
        response = api_client.post(f"{CALIBRATION_URL}/suggestions/generate")
        data = response.json()
        
        assert data["status"] == "success"
        assert "suggestions" in data
        assert "requires_validation" in data
        assert data["requires_validation"] == True
        assert "metadata" in data
        assert data["metadata"]["mode"] == "hybrid"
        
        print(f"✓ Generate suggestions structure validated: {len(data['suggestions'])} suggestions")


class TestListSuggestions:
    """List suggestions endpoint tests"""
    
    def test_list_suggestions_returns_200(self, api_client):
        """Test list suggestions returns 200"""
        response = api_client.get(f"{CALIBRATION_URL}/suggestions")
        assert response.status_code == 200
        print("✓ List suggestions returns 200")
    
    def test_list_suggestions_structure(self, api_client):
        """Test list suggestions response structure"""
        response = api_client.get(f"{CALIBRATION_URL}/suggestions")
        data = response.json()
        
        assert data["status"] == "success"
        assert "total" in data
        assert "suggestions" in data
        assert isinstance(data["suggestions"], list)
        
        print(f"✓ List suggestions structure validated: {data['total']} suggestions")
    
    def test_list_suggestions_with_status_filter(self, api_client):
        """Test list suggestions with status filter"""
        for status in ["pending", "approved", "applied", "rejected"]:
            response = api_client.get(f"{CALIBRATION_URL}/suggestions?status_filter={status}")
            assert response.status_code == 200
            data = response.json()
            assert data["filter"] == status
            print(f"✓ List suggestions with filter={status}: {data['total']} suggestions")


class TestSuggestionApproval:
    """Suggestion approval and rejection tests"""
    
    def test_approve_nonexistent_suggestion(self, api_client):
        """Test approving non-existent suggestion returns 404"""
        response = api_client.post(
            f"{CALIBRATION_URL}/suggestions/NONEXISTENT-ID/approve",
            json={"validated_by": "TEST_USER", "notes": "Test approval"}
        )
        assert response.status_code == 404
        print("✓ Approve non-existent suggestion returns 404")
    
    def test_reject_nonexistent_suggestion(self, api_client):
        """Test rejecting non-existent suggestion returns 404"""
        response = api_client.post(
            f"{CALIBRATION_URL}/suggestions/NONEXISTENT-ID/reject",
            json={"validated_by": "TEST_USER", "reason": "Test rejection"}
        )
        assert response.status_code == 404
        print("✓ Reject non-existent suggestion returns 404")


class TestApplySuggestions:
    """Apply approved suggestions tests"""
    
    def test_apply_suggestions_returns_200(self, api_client):
        """Test apply suggestions returns 200"""
        response = api_client.post(f"{CALIBRATION_URL}/suggestions/apply")
        assert response.status_code == 200
        print("✓ Apply suggestions returns 200")
    
    def test_apply_suggestions_no_approved(self, api_client):
        """Test apply suggestions when none approved"""
        response = api_client.post(f"{CALIBRATION_URL}/suggestions/apply")
        data = response.json()
        
        assert data["status"] == "success"
        # Message may vary if nothing to apply
        if data.get("applied", 0) == 0:
            assert "message" in data
        
        print(f"✓ Apply suggestions when none: applied={data.get('applied', 0)}")


# =============================================================================
# MASTER STATUS TESTS
# =============================================================================

class TestMasterStatus:
    """Master status endpoint tests"""
    
    def test_master_status_returns_200(self, api_client):
        """Test master status returns 200"""
        response = api_client.get(f"{CALIBRATION_URL}/master-status")
        assert response.status_code == 200
        print("✓ Master status returns 200")
    
    def test_master_status_response_structure(self, api_client):
        """Test master status response structure"""
        response = api_client.get(f"{CALIBRATION_URL}/master-status")
        data = response.json()
        
        assert data["status"] == "success"
        assert "master_status" in data
        
        master = data["master_status"]
        assert "is_ready" in master
        assert "is_locked" in master
        assert "is_master" in master
        assert "current_precision" in master
        assert "target_precision" in master
        assert "gap" in master
        assert "total_comparisons" in master
        
        assert master["target_precision"] == 95.0
        
        # Model version should be included
        assert "model_version" in data
        assert "recommendation" in data
        
        print(f"✓ Master status: ready={master['is_ready']}, precision={master['current_precision']:.1f}%")
    
    def test_master_ready_threshold(self, api_client):
        """Test master readiness based on precision threshold"""
        response = api_client.get(f"{CALIBRATION_URL}/master-status")
        data = response.json()
        
        master = data["master_status"]
        
        # If precision >= 95, should be ready
        if master["current_precision"] >= 95.0:
            assert master["is_ready"] == True
            assert master["gap"] <= 0
        else:
            assert master["is_ready"] == False
            assert master["gap"] > 0
        
        print(f"✓ Master readiness test: precision={master['current_precision']:.1f}%, is_ready={master['is_ready']}")


class TestLockMaster:
    """Lock master endpoint tests"""
    
    def test_lock_master_checks_precision(self, api_client):
        """Test lock master validates precision requirement"""
        # First check current status
        status_response = api_client.get(f"{CALIBRATION_URL}/master-status")
        status_data = status_response.json()
        
        # If precision is below 95%, lock should fail
        if status_data["master_status"]["current_precision"] < 95.0:
            response = api_client.post(f"{CALIBRATION_URL}/lock-master")
            assert response.status_code == 400
            data = response.json()
            assert data["detail"]["error_code"] == "PRECISION_INSUFFICIENT"
            print("✓ Lock master rejected due to insufficient precision")
        else:
            print("✓ Precision >= 95%, lock would be allowed (not testing actual lock)")
    
    def test_lock_master_already_locked(self, api_client):
        """Test lock master when already locked"""
        status_response = api_client.get(f"{CALIBRATION_URL}/master-status")
        status_data = status_response.json()
        
        if status_data["master_status"]["is_locked"]:
            response = api_client.post(f"{CALIBRATION_URL}/lock-master")
            assert response.status_code == 400
            data = response.json()
            assert data["detail"]["error_code"] == "ALREADY_LOCKED"
            print("✓ Lock master rejected when already locked")
        else:
            print("✓ Model not locked yet, skipping already-locked test")


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestCalibrationWorkflow:
    """Full calibration workflow integration tests"""
    
    def test_complete_comparison_workflow(self, api_client):
        """Test complete comparison workflow: create → list → dashboard update"""
        # 1. Create a comparison
        now = datetime.utcnow()
        payload = {
            "observation_id": f"OBS-WORKFLOW-{now.strftime('%Y%m%d%H%M%S')}",
            "predicted_lat": 46.8139,
            "predicted_lng": -71.2080,
            "predicted_behavior": "moving",
            "predicted_score": 68.0,
            "prediction_timestamp": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "observed_lat": 46.8140,
            "observed_lng": -71.2078,
            "observed_behavior": "moving",
            "observed_timestamp": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "species": "elk",
            "season": "spring"
        }
        
        create_response = api_client.post(f"{CALIBRATION_URL}/compare", json=payload)
        assert create_response.status_code == 201
        comparison_id = create_response.json()["comparison"]["comparison_id"]
        print(f"✓ Created comparison: {comparison_id}")
        
        # 2. Verify in list
        list_response = api_client.get(f"{CALIBRATION_URL}/comparisons")
        assert list_response.status_code == 200
        comparison_ids = [c["comparison_id"] for c in list_response.json()["comparisons"]]
        assert comparison_id in comparison_ids
        print("✓ Comparison appears in list")
        
        # 3. Check dashboard reflects update
        dashboard_response = api_client.get(f"{CALIBRATION_URL}/dashboard")
        assert dashboard_response.status_code == 200
        dashboard = dashboard_response.json()["dashboard"]
        
        # Should have elk in by_species
        assert "elk" in dashboard["by_species"]
        print(f"✓ Dashboard updated: elk precision = {dashboard['by_species']['elk']:.1f}%")
    
    def test_suggestion_workflow(self, api_client):
        """Test suggestion workflow: generate → list → (approve/reject if any)"""
        # 1. Generate suggestions
        gen_response = api_client.post(f"{CALIBRATION_URL}/suggestions/generate")
        assert gen_response.status_code == 200
        suggestions = gen_response.json()["suggestions"]
        print(f"✓ Generated {len(suggestions)} suggestions")
        
        # 2. List suggestions
        list_response = api_client.get(f"{CALIBRATION_URL}/suggestions")
        assert list_response.status_code == 200
        
        # 3. If there are pending suggestions, test approve/reject
        pending = [s for s in list_response.json()["suggestions"] if s["status"] == "pending"]
        
        if pending:
            # Test approval
            sug_id = pending[0]["suggestion_id"]
            approve_response = api_client.post(
                f"{CALIBRATION_URL}/suggestions/{sug_id}/approve",
                json={"validated_by": "TEST_WORKFLOW", "notes": "Workflow test"}
            )
            assert approve_response.status_code == 200
            assert approve_response.json()["suggestion"]["status"] == "approved"
            print(f"✓ Approved suggestion: {sug_id}")
        else:
            print("✓ No pending suggestions to approve/reject")


# =============================================================================
# EDGE CASES
# =============================================================================

class TestEdgeCases:
    """Edge case tests"""
    
    def test_compare_boundary_coordinates(self, api_client):
        """Test comparison with boundary coordinate values"""
        now = datetime.utcnow()
        payload = {
            "observation_id": f"OBS-BOUNDARY-{now.strftime('%Y%m%d%H%M%S')}",
            "predicted_lat": 90.0,  # Maximum latitude
            "predicted_lng": 180.0,  # Maximum longitude
            "predicted_behavior": "resting",
            "predicted_score": 50.0,
            "prediction_timestamp": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "observed_lat": 89.9999,
            "observed_lng": 179.9999,
            "observed_behavior": "resting",
            "observed_timestamp": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "species": "bear",
            "season": "summer"
        }
        
        response = api_client.post(f"{CALIBRATION_URL}/compare", json=payload)
        assert response.status_code == 201
        print("✓ Boundary coordinates accepted")
    
    def test_compare_invalid_coordinates(self, api_client):
        """Test comparison with invalid coordinates"""
        now = datetime.utcnow()
        payload = {
            "observation_id": f"OBS-INVALID-{now.strftime('%Y%m%d%H%M%S')}",
            "predicted_lat": 100.0,  # Invalid: > 90
            "predicted_lng": -71.2080,
            "predicted_behavior": "feeding",
            "predicted_score": 72.5,
            "prediction_timestamp": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "observed_lat": 46.8145,
            "observed_lng": -71.2075,
            "observed_behavior": "feeding",
            "observed_timestamp": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "species": "moose",
            "season": "winter"
        }
        
        response = api_client.post(f"{CALIBRATION_URL}/compare", json=payload)
        assert response.status_code == 422  # Validation error
        print("✓ Invalid coordinates rejected with 422")
    
    def test_dashboard_by_behavior_tracking(self, api_client):
        """Test that dashboard tracks precision by behavior"""
        dashboard_response = api_client.get(f"{CALIBRATION_URL}/dashboard")
        dashboard = dashboard_response.json()["dashboard"]
        
        assert "by_behavior" in dashboard
        assert isinstance(dashboard["by_behavior"], dict)
        
        for behavior, precision in dashboard["by_behavior"].items():
            assert isinstance(precision, (int, float))
            assert 0 <= precision <= 100
        
        print(f"✓ By behavior tracking: {len(dashboard['by_behavior'])} behaviors tracked")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
