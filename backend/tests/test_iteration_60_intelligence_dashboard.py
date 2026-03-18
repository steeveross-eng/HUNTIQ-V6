"""
Test Suite for Iteration 60 — INTELLIGENCE Dashboard Testing
==============================================================
Tests:
- INTELLIGENCE button in toolbar (replaces old Analyse button)
- Intelligence Dashboard panel opening
- 3 mode selector (GUIDE PRO, SCIENTIFIQUE, TERRAIN)
- Backend API endpoints for intelligence data
- Old Analyse button does NOT exist
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestIntelligenceBackendAPIs:
    """Test all /api/v3/intelligence/* endpoints"""

    def test_solunar_endpoint(self):
        """GET /api/v3/intelligence/solunar — returns solunar data"""
        response = requests.get(f"{BASE_URL}/api/v3/intelligence/solunar", params={
            "lat": 46.8,
            "lng": -71.2
        })
        assert response.status_code == 200, f"Status: {response.status_code}"
        data = response.json()
        
        # Verify response structure
        assert data.get("type") == "solunar", f"Expected type='solunar', got {data.get('type')}"
        assert "solunar_score" in data, "Missing solunar_score"
        assert "moon" in data, "Missing moon data"
        assert "sun" in data, "Missing sun data"
        assert "curve_24h" in data, "Missing curve_24h"
        assert "hunting_windows" in data, "Missing hunting_windows"
        assert "periods" in data, "Missing periods"
        
        # Verify moon data structure
        moon = data["moon"]
        assert "phase_name" in moon, "Missing moon phase_name"
        assert "illumination" in moon, "Missing moon illumination"
        
        # Verify curve has data points
        assert len(data["curve_24h"]) > 0, "curve_24h should have data points"

    def test_guide_pro_endpoint(self):
        """GET /api/v3/intelligence/guide-pro — returns guide pro data"""
        response = requests.get(f"{BASE_URL}/api/v3/intelligence/guide-pro", params={
            "lat": 46.8,
            "lng": -71.2,
            "species": "CHEVREUIL",
            "month": 10
        })
        assert response.status_code == 200, f"Status: {response.status_code}"
        data = response.json()
        
        # Verify response structure
        assert data.get("type") == "guide_pro", f"Expected type='guide_pro', got {data.get('type')}"
        assert data.get("species") == "CHEVREUIL", "Species mismatch"
        assert data.get("month") == 10, "Month mismatch"
        
        # Verify nested structures
        assert "solunar" in data, "Missing solunar data"
        assert "terrain" in data, "Missing terrain data"
        assert "approach_plan" in data, "Missing approach_plan"
        assert "hunting_windows" in data, "Missing hunting_windows"
        assert "best_time" in data, "Missing best_time"
        
        # Verify terrain structure
        terrain = data["terrain"]
        assert "consolidated_score" in terrain, "Missing terrain consolidated_score"
        assert "classe" in terrain, "Missing terrain classe"
        
        # Verify best_time structure
        best_time = data["best_time"]
        assert "score" in best_time, "Missing best_time score"
        assert "label" in best_time, "Missing best_time label"

    def test_scientifique_endpoint(self):
        """GET /api/v3/intelligence/scientifique — returns scientifique data with engines"""
        response = requests.get(f"{BASE_URL}/api/v3/intelligence/scientifique", params={
            "lat": 46.8,
            "lng": -71.2,
            "species": "CHEVREUIL",
            "month": 10
        })
        assert response.status_code == 200, f"Status: {response.status_code}"
        data = response.json()
        
        # Verify response structure
        assert data.get("type") == "scientifique", f"Expected type='scientifique', got {data.get('type')}"
        assert data.get("species") == "CHEVREUIL", "Species mismatch"
        assert data.get("month") == 10, "Month mismatch"
        
        # Verify consolidated structure
        assert "consolidated" in data, "Missing consolidated"
        consolidated = data["consolidated"]
        assert "score" in consolidated, "Missing consolidated score"
        
        # Verify engines array
        assert "engines" in data, "Missing engines"
        assert len(data["engines"]) > 0, "Engines should not be empty"
        
        # Verify engine structure
        engine = data["engines"][0]
        assert "name" in engine, "Missing engine name"
        assert "score" in engine, "Missing engine score"
        assert "components" in engine, "Missing engine components"
        
        # Verify formulas
        assert "formulas" in data, "Missing formulas"
        assert "consolidation" in data["formulas"], "Missing consolidation formula"
        
        # Verify BCE-4X metadata
        assert "bce4x" in data, "Missing bce4x metadata"

    def test_summary_endpoint(self):
        """GET /api/v3/intelligence/summary — returns intelligence summary"""
        response = requests.get(f"{BASE_URL}/api/v3/intelligence/summary", params={
            "lat": 46.8,
            "lng": -71.2,
            "species": "CHEVREUIL",
            "month": 10
        })
        assert response.status_code == 200, f"Status: {response.status_code}"
        data = response.json()
        
        # Verify response structure
        assert data.get("type") == "intelligence_summary", f"Expected type='intelligence_summary', got {data.get('type')}"
        assert data.get("species") == "CHEVREUIL", "Species mismatch"
        
        # Verify consolidated structure
        assert "consolidated" in data, "Missing consolidated"
        consolidated = data["consolidated"]
        assert "score" in consolidated, "Missing consolidated score"
        assert "classe" in consolidated, "Missing consolidated classe"
        assert "label" in consolidated, "Missing consolidated label"
        
        # Verify domains
        assert "domains" in data, "Missing domains"
        assert len(data["domains"]) > 0, "Domains should not be empty"
        
        # Verify recommendations
        assert "recommendations" in data, "Missing recommendations"
        
        # Verify analysis
        assert "analysis" in data, "Missing analysis"
        assert "strongest_engine" in data["analysis"], "Missing strongest_engine"
        assert "weakest_engine" in data["analysis"], "Missing weakest_engine"

    def test_forecast_endpoint(self):
        """GET /api/v3/intelligence/forecast — returns 12-month forecast"""
        response = requests.get(f"{BASE_URL}/api/v3/intelligence/forecast", params={
            "lat": 46.8,
            "lng": -71.2,
            "species": "CHEVREUIL"
        })
        assert response.status_code == 200, f"Status: {response.status_code}"
        data = response.json()
        
        # Verify response structure
        assert data.get("type") == "intelligence_forecast", f"Expected type='intelligence_forecast'"
        assert data.get("species") == "CHEVREUIL", "Species mismatch"
        
        # Verify monthly data (12 months)
        assert "monthly_data" in data, "Missing monthly_data"
        assert len(data["monthly_data"]) == 12, f"Expected 12 months, got {len(data['monthly_data'])}"
        
        # Verify best/worst month
        assert "best_month" in data, "Missing best_month"
        assert "worst_month" in data, "Missing worst_month"
        assert 1 <= data["best_month"] <= 12, "best_month out of range"
        assert 1 <= data["worst_month"] <= 12, "worst_month out of range"
        
        # Verify seasonal scores
        assert "seasonal_scores" in data, "Missing seasonal_scores"
        seasons = data["seasonal_scores"]
        assert "printemps" in seasons, "Missing printemps season"
        assert "ete" in seasons, "Missing ete season"
        assert "automne" in seasons, "Missing automne season"
        assert "hiver" in seasons, "Missing hiver season"

    def test_plan_endpoint(self):
        """GET /api/v3/intelligence/plan — returns plan maitre with actions"""
        response = requests.get(f"{BASE_URL}/api/v3/intelligence/plan", params={
            "lat": 46.8,
            "lng": -71.2,
            "species": "CHEVREUIL",
            "month": 10
        })
        assert response.status_code == 200, f"Status: {response.status_code}"
        data = response.json()
        
        # Verify response structure
        assert data.get("type") == "intelligence_plan", f"Expected type='intelligence_plan'"
        assert data.get("species") == "CHEVREUIL", "Species mismatch"
        assert data.get("month") == 10, "Month mismatch"
        
        # Verify overall score
        assert "overall_score" in data, "Missing overall_score"
        assert "overall_classe" in data, "Missing overall_classe"
        
        # Verify actions
        assert "actions" in data, "Missing actions"
        assert len(data["actions"]) > 0, "Actions should not be empty"
        
        # Verify action structure
        action = data["actions"][0]
        assert "rank" in action, "Missing action rank"
        assert "engine" in action, "Missing action engine"
        assert "score" in action, "Missing action score"
        assert "urgency" in action, "Missing action urgency"
        assert "action" in action, "Missing action text"
        
        # Verify critical count
        assert "critical_count" in data, "Missing critical_count"


class TestEnginesRegistry:
    """Test engine registry endpoints"""
    
    def test_engines_registry(self):
        """GET /api/v3/engines/registry — returns engine manifest"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/registry")
        assert response.status_code == 200
        data = response.json()
        
        assert "engines" in data, "Missing engines"
        assert len(data["engines"]) >= 4, f"Expected at least 4 engines, got {len(data['engines'])}"
    
    def test_engines_validate(self):
        """GET /api/v3/engines/validate — returns validation status"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/validate")
        assert response.status_code == 200
        data = response.json()
        
        assert "overall_compliant" in data, "Missing overall_compliant"
        assert "bce4x" in data, "Missing bce4x validation"
        assert "steeve_max" in data, "Missing steeve_max validation"


class TestHealthAndBasics:
    """Test basic health endpoints"""
    
    def test_api_health(self):
        """GET /api/health — basic health check"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
