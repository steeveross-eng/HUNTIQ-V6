"""
Iteration 62 — BIONIC V3 Floating Intelligence Panel
=====================================================
Tests for the refactored architecture:
- IntelligenceDashboard is now a floating non-blocking panel
- TerritoireToolbar extracted to separate component
- NutritionPanel extracted to separate component
- MonTerritoireBionicPage reduced from 2119 to 1553 lines

Backend API Tests: /api/v3/* endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestBCE4XCompliance:
    """BCE-4X Compliance validation"""
    
    def test_engines_validate_overall_compliant(self):
        """R0: Overall BCE-4X + STEEVE-MAX compliance must be true"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/validate")
        assert response.status_code == 200
        data = response.json()
        assert data["overall_compliant"] == True
        assert data["bce4x"]["compliant"] == True
        assert data["steeve_max"]["compliant"] == True
        print(f"✓ BCE-4X: {data['bce4x']['passed']}/{data['bce4x']['total']} passed")
        print(f"✓ STEEVE-MAX: {data['steeve_max']['passed']}/{data['steeve_max']['total']} passed")

class TestIntelligenceAPIs:
    """Intelligence dashboard backend endpoints"""
    
    def test_intelligence_summary(self):
        """/api/v3/intelligence/summary returns valid structure"""
        response = requests.get(
            f"{BASE_URL}/api/v3/intelligence/summary",
            params={"lat": 46.8139, "lng": -71.2080, "species": "CHEVREUIL", "month": 10}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "intelligence_summary"
        assert "consolidated" in data
        assert "score" in data["consolidated"]
        assert "classe" in data["consolidated"]
        assert "domains" in data
        assert "engines_count" in data
        print(f"✓ Summary score: {data['consolidated']['score']}, classe: {data['consolidated']['classe']}")
    
    def test_intelligence_forecast(self):
        """/api/v3/intelligence/forecast returns 12-month data"""
        response = requests.get(
            f"{BASE_URL}/api/v3/intelligence/forecast",
            params={"lat": 46.8139, "lng": -71.2080, "species": "CHEVREUIL"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "intelligence_forecast"
        assert "monthly_data" in data
        assert len(data["monthly_data"]) == 12
        assert "best_month" in data
        assert "worst_month" in data
        assert "seasonal_scores" in data
        print(f"✓ Forecast best month: {data['best_month']}, annual avg: {data['annual_average']}")
    
    def test_intelligence_plan(self):
        """/api/v3/intelligence/plan returns action items"""
        response = requests.get(
            f"{BASE_URL}/api/v3/intelligence/plan",
            params={"lat": 46.8139, "lng": -71.2080, "species": "CHEVREUIL", "month": 10}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "intelligence_plan"
        assert "actions" in data
        assert isinstance(data["actions"], list)
        assert "overall_score" in data
        assert "overall_classe" in data
        print(f"✓ Plan has {len(data['actions'])} actions, critical_count: {data.get('critical_count', 0)}")
    
    def test_intelligence_solunar(self):
        """/api/v3/intelligence/solunar returns lunar data"""
        response = requests.get(
            f"{BASE_URL}/api/v3/intelligence/solunar",
            params={"lat": 46.8139, "lng": -71.2080, "date": "2026-01-15"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "solunar"
        assert "moon" in data
        assert "sun" in data
        assert "periods" in data
        print(f"✓ Solunar moon phase: {data['moon']['phase_name']}")
    
    def test_intelligence_guide_pro(self):
        """/api/v3/intelligence/guide-pro returns combined guide"""
        response = requests.get(
            f"{BASE_URL}/api/v3/intelligence/guide-pro",
            params={"lat": 46.8139, "lng": -71.2080, "species": "CHEVREUIL", "month": 10}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "guide_pro"
        assert "solunar" in data
        assert "hunting_windows" in data
        assert "approach_plan" in data
        print(f"✓ Guide-pro has {len(data.get('hunting_windows', []))} hunting windows")


class TestEngineRegistry:
    """Engine registry endpoints"""
    
    def test_engines_registry(self):
        """/api/v3/engines/registry returns engine manifest"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/registry")
        assert response.status_code == 200
        data = response.json()
        assert "engines" in data
        assert len(data["engines"]) > 0
        print(f"✓ Registry has {len(data['engines'])} engines")
    
    def test_engines_score_point(self):
        """/api/v3/engines/score-point returns consolidated score"""
        response = requests.get(
            f"{BASE_URL}/api/v3/engines/score-point",
            params={"lat": 46.8139, "lng": -71.2080, "species": "CHEVREUIL", "month": 10}
        )
        assert response.status_code == 200
        data = response.json()
        assert "score" in data
        assert "classe" in data
        assert "components" in data
        print(f"✓ Score-point: {data['score']}, classe: {data['classe']}")


class TestOldAnalyseRemoved:
    """Verify old /analyse endpoints are removed (BCE-4X R11)"""
    
    def test_old_v3_analyse_not_found(self):
        """/api/v3/analyse should NOT exist (removed)"""
        response = requests.get(f"{BASE_URL}/api/v3/analyse")
        assert response.status_code in [404, 422], f"Expected 404/422 but got {response.status_code}"
        print("✓ Old /api/v3/analyse correctly removed (404)")
    
    def test_old_v1_analyse_not_found(self):
        """/api/v1/analyse should NOT exist (removed)"""
        response = requests.get(f"{BASE_URL}/api/v1/analyse")
        assert response.status_code in [404, 405], f"Expected 404/405 but got {response.status_code}"
        print("✓ Old /api/v1/analyse correctly removed (404)")


class TestSpeciesEndpoint:
    """Species reference data"""
    
    def test_species_list(self):
        """/api/v3/species returns canonical species"""
        response = requests.get(f"{BASE_URL}/api/v3/species")
        assert response.status_code == 200
        data = response.json()
        assert "species" in data
        assert "CHEVREUIL" in data["species"]
        print(f"✓ Species: {data['species'][:3]}...")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
