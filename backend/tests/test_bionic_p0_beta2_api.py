"""
BIONIC ENGINE P0-BETA2 API Integration Tests
BIONIC HUNT/Chasse-V5 PHASE G

Tests the 12 behavioral factors integration via API endpoints:
- POST /api/v1/bionic/territorial/score with include_advanced_factors=true
- POST /api/v1/bionic/behavioral/predict with include_advanced_factors=true

Validates:
- metadata.advanced_factors contains 12 factors
- metadata.version = "P0-beta2"
- Advanced recommendations are present
- Advanced strategies are present
- Snow conditions (snow_depth_cm, is_crusted)
- Backward compatibility with include_advanced_factors=false
"""

import pytest
import requests
import os
from datetime import datetime, timezone

# Use the public frontend URL (routes /api to backend)
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    raise ValueError("REACT_APP_BACKEND_URL must be set")


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def api_client():
    """Requests session for API calls"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture
def sample_territorial_request():
    """Sample territorial score request with 12 factors enabled"""
    return {
        "latitude": 47.5,
        "longitude": -70.5,
        "species": "moose",
        "datetime": "2025-10-15T07:00:00Z",
        "radius_km": 5.0,
        "include_recommendations": True,
        "include_advanced_factors": True,
        "snow_depth_cm": 0,
        "is_crusted": False
    }


@pytest.fixture
def sample_behavioral_request():
    """Sample behavioral prediction request with 12 factors enabled"""
    return {
        "species": "deer",
        "datetime": "2025-10-15T07:00:00Z",
        "latitude": 48.0,
        "longitude": -71.0,
        "include_strategy": True,
        "include_advanced_factors": True,
        "snow_depth_cm": 0,
        "is_crusted": False
    }


# =============================================================================
# TERRITORIAL SCORE API TESTS - 12 Factors
# =============================================================================

class TestTerritorialScoreAPI:
    """Tests for POST /api/v1/bionic/territorial/score"""
    
    def test_territorial_score_with_advanced_factors_returns_200(self, api_client, sample_territorial_request):
        """API returns 200 with advanced factors enabled"""
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/territorial/score",
            json=sample_territorial_request
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True
    
    def test_territorial_score_version_is_p0_beta2(self, api_client, sample_territorial_request):
        """metadata.version = P0-beta2"""
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/territorial/score",
            json=sample_territorial_request
        )
        
        data = response.json()
        assert data.get("metadata", {}).get("version") == "P0-beta2", \
            f"Expected version P0-beta2, got {data.get('metadata', {}).get('version')}"
    
    def test_territorial_score_advanced_factors_enabled(self, api_client, sample_territorial_request):
        """metadata.advanced_factors_enabled = true"""
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/territorial/score",
            json=sample_territorial_request
        )
        
        data = response.json()
        assert data.get("metadata", {}).get("advanced_factors_enabled") is True
    
    def test_territorial_score_12_factors_present(self, api_client, sample_territorial_request):
        """metadata.advanced_factors contains the 12 behavioral factors"""
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/territorial/score",
            json=sample_territorial_request
        )
        
        data = response.json()
        advanced_factors = data.get("metadata", {}).get("advanced_factors", {})
        
        # List of 12 expected factors (some combined in the implementation)
        expected_factors = [
            "predation",
            "thermal_stress",
            "hydric_stress",
            "social_stress",
            "social_hierarchy",
            "competition",
            "weak_signals",
            "hormonal",
            "digestive",
            "territorial_memory",
            "adaptive_behavior",
            "human_disturbance",
            "mineral",
            "snow"
        ]
        
        # Check that at least 12 factors are present
        present_factors = [f for f in expected_factors if f in advanced_factors]
        assert len(present_factors) >= 12, \
            f"Expected at least 12 factors, got {len(present_factors)}: {present_factors}"
    
    def test_territorial_score_has_advanced_factor_scores(self, api_client, sample_territorial_request):
        """metadata.advanced_factor_scores is present"""
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/territorial/score",
            json=sample_territorial_request
        )
        
        data = response.json()
        assert "advanced_factor_scores" in data.get("metadata", {}), \
            "advanced_factor_scores should be in metadata"
    
    def test_territorial_score_has_recommendations(self, api_client, sample_territorial_request):
        """Recommendations are present when include_recommendations=true"""
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/territorial/score",
            json=sample_territorial_request
        )
        
        data = response.json()
        recommendations = data.get("recommendations", [])
        assert isinstance(recommendations, list)
        # During rut (October), there should be recommendations
        assert len(recommendations) > 0, "Expected recommendations during rut period"
    
    def test_territorial_score_with_snow_conditions(self, api_client, sample_territorial_request):
        """API handles snow_depth_cm and is_crusted parameters"""
        request = sample_territorial_request.copy()
        request["snow_depth_cm"] = 80
        request["is_crusted"] = True
        request["datetime"] = "2025-12-15T10:00:00Z"  # Winter
        
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/territorial/score",
            json=request
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check snow factor is calculated
        snow_factor = data.get("metadata", {}).get("advanced_factors", {}).get("snow", {})
        assert snow_factor.get("winter_penalty_score", 0) > 0, \
            "Deep crusted snow should have winter penalty"
    
    def test_territorial_score_backward_compatible(self, api_client, sample_territorial_request):
        """API works with include_advanced_factors=false (backward compatibility)"""
        request = sample_territorial_request.copy()
        request["include_advanced_factors"] = False
        
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/territorial/score",
            json=request
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("metadata", {}).get("advanced_factors_enabled") is False
        assert "advanced_factors" not in data.get("metadata", {})


# =============================================================================
# BEHAVIORAL PREDICT API TESTS - 12 Factors
# =============================================================================

class TestBehavioralPredictAPI:
    """Tests for POST /api/v1/bionic/behavioral/predict"""
    
    def test_behavioral_predict_with_advanced_factors_returns_200(self, api_client, sample_behavioral_request):
        """API returns 200 with advanced factors enabled"""
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/behavioral/predict",
            json=sample_behavioral_request
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True
    
    def test_behavioral_predict_version_is_p0_beta2(self, api_client, sample_behavioral_request):
        """metadata.version = P0-beta2"""
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/behavioral/predict",
            json=sample_behavioral_request
        )
        
        data = response.json()
        assert data.get("metadata", {}).get("version") == "P0-beta2", \
            f"Expected version P0-beta2, got {data.get('metadata', {}).get('version')}"
    
    def test_behavioral_predict_advanced_factors_enabled(self, api_client, sample_behavioral_request):
        """metadata.advanced_factors_enabled = true"""
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/behavioral/predict",
            json=sample_behavioral_request
        )
        
        data = response.json()
        assert data.get("metadata", {}).get("advanced_factors_enabled") is True
    
    def test_behavioral_predict_12_factors_present(self, api_client, sample_behavioral_request):
        """metadata.advanced_factors contains the 12 behavioral factors"""
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/behavioral/predict",
            json=sample_behavioral_request
        )
        
        data = response.json()
        advanced_factors = data.get("metadata", {}).get("advanced_factors", {})
        
        expected_factors = [
            "predation",
            "thermal_stress",
            "hydric_stress",
            "social_stress",
            "social_hierarchy",
            "competition",
            "weak_signals",
            "hormonal",
            "digestive",
            "territorial_memory",
            "adaptive_behavior",
            "human_disturbance",
            "mineral",
            "snow"
        ]
        
        present_factors = [f for f in expected_factors if f in advanced_factors]
        assert len(present_factors) >= 12, \
            f"Expected at least 12 factors, got {len(present_factors)}: {present_factors}"
    
    def test_behavioral_predict_has_behavioral_modifiers(self, api_client, sample_behavioral_request):
        """metadata.behavioral_modifiers is present"""
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/behavioral/predict",
            json=sample_behavioral_request
        )
        
        data = response.json()
        assert "behavioral_modifiers" in data.get("metadata", {}), \
            "behavioral_modifiers should be in metadata"
    
    def test_behavioral_predict_has_strategies(self, api_client, sample_behavioral_request):
        """Advanced strategies are present when include_strategy=true"""
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/behavioral/predict",
            json=sample_behavioral_request
        )
        
        data = response.json()
        strategies = data.get("strategies", [])
        assert isinstance(strategies, list)
        # Should have at least some strategies (rut + general + advanced)
        assert len(strategies) > 0, "Expected strategies"
    
    def test_behavioral_predict_with_snow_conditions(self, api_client, sample_behavioral_request):
        """API handles snow conditions in behavioral prediction"""
        request = sample_behavioral_request.copy()
        request["snow_depth_cm"] = 70
        request["is_crusted"] = True
        request["datetime"] = "2025-01-15T10:00:00Z"  # Winter
        
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/behavioral/predict",
            json=request
        )
        
        assert response.status_code == 200
        data = response.json()
        
        snow_factor = data.get("metadata", {}).get("advanced_factors", {}).get("snow", {})
        assert snow_factor.get("yarding_likelihood") is True or \
               snow_factor.get("winter_penalty_score", 0) > 0, \
            "Deep snow should impact behavior"
    
    def test_behavioral_predict_backward_compatible(self, api_client, sample_behavioral_request):
        """API works with include_advanced_factors=false (backward compatibility)"""
        request = sample_behavioral_request.copy()
        request["include_advanced_factors"] = False
        
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/behavioral/predict",
            json=request
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("metadata", {}).get("advanced_factors_enabled") is False
        assert "advanced_factors" not in data.get("metadata", {})


# =============================================================================
# HEALTH & MODULE TESTS
# =============================================================================

class TestBionicHealth:
    """Tests for health and module endpoints"""
    
    def test_bionic_health_endpoint(self, api_client):
        """GET /api/v1/bionic/health returns 200"""
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/health")
        
        assert response.status_code == 200
        data = response.json()
        # Accept both healthy and initializing status
        assert data.get("status") in ["healthy", "initializing"], \
            f"Expected healthy or initializing status, got {data.get('status')}"
    
    def test_bionic_modules_endpoint(self, api_client):
        """GET /api/v1/bionic/modules lists available modules"""
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/modules")
        
        assert response.status_code == 200
        data = response.json()
        assert "modules" in data
        
        # Check that territorial and behavioral modules are listed
        module_ids = [m.get("id") for m in data.get("modules", [])]
        assert "predictive_territorial" in module_ids
        assert "behavioral_models" in module_ids


# =============================================================================
# EDGE CASES AND SPECIAL SCENARIOS
# =============================================================================

class TestEdgeCases:
    """Edge case tests for the 12 factors integration"""
    
    def test_bear_hibernation_with_advanced_factors(self, api_client):
        """Bear hibernation returns 0 score even with advanced factors"""
        request = {
            "latitude": 47.5,
            "longitude": -70.5,
            "species": "bear",
            "datetime": "2025-01-15T10:00:00Z",  # January = hibernation
            "include_advanced_factors": True
        }
        
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/territorial/score",
            json=request
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("overall_score") == 0
        assert "BEAR_HIBERNATION_PERIOD" in data.get("warnings", [])
    
    def test_rut_period_with_hormonal_factor(self, api_client):
        """Hormonal factor reflects rut during October"""
        request = {
            "species": "moose",
            "datetime": "2025-10-10T07:00:00Z",  # October = rut peak
            "latitude": 48.0,
            "longitude": -71.0,
            "include_advanced_factors": True,
            "include_strategy": True
        }
        
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/behavioral/predict",
            json=request
        )
        
        assert response.status_code == 200
        data = response.json()
        
        hormonal = data.get("metadata", {}).get("advanced_factors", {}).get("hormonal", {})
        assert hormonal.get("phase") == "rut_peak", \
            f"Expected rut_peak phase in October, got {hormonal.get('phase')}"
        assert hormonal.get("activity_modifier", 1.0) > 1.0, \
            "Activity modifier should be > 1.0 during rut"
    
    def test_all_species_supported(self, api_client):
        """All 5 species work with advanced factors"""
        species_list = ["moose", "deer", "bear", "wild_turkey", "elk"]
        
        for species in species_list:
            request = {
                "latitude": 47.5,
                "longitude": -70.5,
                "species": species,
                "datetime": "2025-06-15T10:00:00Z",  # Summer (bear not hibernating)
                "include_advanced_factors": True
            }
            
            response = api_client.post(
                f"{BASE_URL}/api/v1/bionic/territorial/score",
                json=request
            )
            
            assert response.status_code == 200, f"Failed for species {species}: {response.text}"
            data = response.json()
            assert data.get("success") is True, f"Species {species} should succeed"


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
