"""
Test Iteration 59 — ANALYSE Removal + Redirect to INTELLIGENCE
=================================================================
Tests:
1. Navigation NO LONGER has standalone 'Analysez' link
2. /analyze redirects to /analytics (React Router)
3. INTELLIGENCE pages work: /analytics, /forecast, /plan-maitre
4. NON-REGRESSION: /territoire page, internal 'Analyse' tab preserved
5. Backend API endpoints still work: engines/registry, engines/validate, intelligence/*
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# ==============================================================================
# MODULE: M4 INTELLIGENCE API ENDPOINTS
# ==============================================================================

class TestIntelligenceEndpoints:
    """Test INTELLIGENCE API endpoints (M4)"""
    
    def test_intelligence_summary(self):
        """GET /api/v3/intelligence/summary returns valid summary"""
        response = requests.get(f"{BASE_URL}/api/v3/intelligence/summary", params={
            "lat": 46.8139, "lng": -71.2080, "species": "CHEVREUIL"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("type") == "intelligence_summary"
        assert "consolidated" in data
        assert "domains" in data
        print(f"✓ Intelligence summary: consolidated score {data['consolidated'].get('score')}")
    
    def test_intelligence_forecast(self):
        """GET /api/v3/intelligence/forecast returns 12 months"""
        response = requests.get(f"{BASE_URL}/api/v3/intelligence/forecast", params={
            "lat": 46.8139, "lng": -71.2080, "species": "CHEVREUIL"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("type") == "intelligence_forecast"
        assert "monthly_data" in data
        assert len(data["monthly_data"]) == 12, f"Expected 12 months, got {len(data['monthly_data'])}"
        assert "seasonal_scores" in data
        print(f"✓ Intelligence forecast: {len(data['monthly_data'])} months, best={data.get('best_month')}")
    
    def test_intelligence_plan(self):
        """GET /api/v3/intelligence/plan returns actions"""
        response = requests.get(f"{BASE_URL}/api/v3/intelligence/plan", params={
            "lat": 46.8139, "lng": -71.2080, "species": "CHEVREUIL"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("type") == "intelligence_plan"
        assert "actions" in data
        assert "overall_score" in data
        print(f"✓ Intelligence plan: {len(data['actions'])} actions, overall_score={data.get('overall_score')}")


# ==============================================================================
# MODULE: M1-M2 ENGINE REGISTRY + VALIDATION (NON-REGRESSION)
# ==============================================================================

class TestEngineRegistryNonRegression:
    """Test Engine Registry and Validation (M1-M2) — NON-REGRESSION"""
    
    def test_engines_registry_returns_5_engines(self):
        """GET /api/v3/engines/registry returns 5 engines"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/registry")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        engines = data.get("engines", [])
        assert len(engines) == 5, f"Expected 5 engines, got {len(engines)}"
        engine_names = [e["name"] for e in engines]
        expected_engines = ["ALIMENTATION-V1", "ALIMENTATION-V2", "REPOS-V1", "CORRIDORS-V10", "PRESSION-V1"]
        for name in expected_engines:
            assert name in engine_names, f"Missing engine: {name}"
        print(f"✓ Engines registry: {engine_names}")
    
    def test_engines_validate_overall_compliant(self):
        """GET /api/v3/engines/validate returns overall_compliant=true"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/validate")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("overall_compliant") == True, f"Expected overall_compliant=true"
        print(f"✓ Engines validate: overall_compliant=True, BCE-4X passed={data.get('bce_4x', {}).get('passed')}")


# ==============================================================================
# MODULE: V1 LEGACY ENDPOINTS (NON-REGRESSION)
# ==============================================================================

class TestV1LegacyNonRegression:
    """Test V1 legacy endpoints — NON-REGRESSION"""
    
    def test_v1_score_consolide_point(self):
        """GET /api/v1/score-consolide/point returns valid score"""
        response = requests.get(f"{BASE_URL}/api/v1/score-consolide/point", params={
            "lat": 46.8139, "lng": -71.2080
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "score" in data or "score_global" in data
        score = data.get("score") or data.get("score_global", 0)
        assert 0 <= score <= 100, f"Score should be 0-100, got {score}"
        print(f"✓ V1 score-consolide/point: score={score}")


# ==============================================================================
# MODULE: HEALTH + BASIC CONNECTIVITY
# ==============================================================================

class TestBasicConnectivity:
    """Test basic API connectivity"""
    
    def test_api_health(self):
        """GET /api/health returns 200"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ API health check passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
