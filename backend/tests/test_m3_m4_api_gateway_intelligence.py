"""
M3+M4 API Gateway + Intelligence Endpoints Test Suite
======================================================
Tests for:
- M3: API Gateway extraction /api/v3/* in router.py
- M4: 3 new INTELLIGENCE endpoints: summary, forecast, plan
- Non-regression: M1/M2 engines endpoints, V1 legacy endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestIntelligenceEndpoints:
    """M4: 3 new INTELLIGENCE endpoints"""
    
    # Default test coordinates (Quebec)
    LAT = 46.8139
    LNG = -71.2080
    SPECIES = "CHEVREUIL"
    MONTH = 10

    def test_intelligence_summary_returns_correct_type(self):
        """GET /api/v3/intelligence/summary returns type=intelligence_summary"""
        response = requests.get(f"{BASE_URL}/api/v3/intelligence/summary", params={
            "lat": self.LAT, "lng": self.LNG, "species": self.SPECIES, "month": self.MONTH
        })
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "intelligence_summary"
        
    def test_intelligence_summary_has_consolidated_score(self):
        """GET /api/v3/intelligence/summary contains consolidated score"""
        response = requests.get(f"{BASE_URL}/api/v3/intelligence/summary", params={
            "lat": self.LAT, "lng": self.LNG, "species": self.SPECIES, "month": self.MONTH
        })
        data = response.json()
        assert "consolidated" in data
        assert "score" in data["consolidated"]
        assert 0 <= data["consolidated"]["score"] <= 100
        assert data["consolidated"]["classe"] in ["OPTIMAL", "BON", "MODERE", "FAIBLE"]
        assert "label" in data["consolidated"]
        
    def test_intelligence_summary_has_domains(self):
        """GET /api/v3/intelligence/summary contains domains breakdown"""
        response = requests.get(f"{BASE_URL}/api/v3/intelligence/summary", params={
            "lat": self.LAT, "lng": self.LNG, "species": self.SPECIES, "month": self.MONTH
        })
        data = response.json()
        assert "domains" in data
        assert len(data["domains"]) > 0
        # Each domain should have engines with scores
        for domain, engines in data["domains"].items():
            assert isinstance(engines, list)
            for eng in engines:
                assert "engine" in eng
                assert "score" in eng
                
    def test_intelligence_summary_has_analysis(self):
        """GET /api/v3/intelligence/summary contains analysis with strongest/weakest"""
        response = requests.get(f"{BASE_URL}/api/v3/intelligence/summary", params={
            "lat": self.LAT, "lng": self.LNG, "species": self.SPECIES, "month": self.MONTH
        })
        data = response.json()
        assert "analysis" in data
        assert "strongest_engine" in data["analysis"]
        assert "weakest_engine" in data["analysis"]
        assert "strongest_score" in data["analysis"]
        assert "weakest_score" in data["analysis"]
        
    def test_intelligence_summary_has_recommendations(self):
        """GET /api/v3/intelligence/summary contains recommendations array"""
        response = requests.get(f"{BASE_URL}/api/v3/intelligence/summary", params={
            "lat": self.LAT, "lng": self.LNG, "species": self.SPECIES, "month": self.MONTH
        })
        data = response.json()
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)
        # If recommendations exist, check structure
        for rec in data["recommendations"]:
            assert "priority" in rec
            assert rec["priority"] in ["HAUTE", "MOYENNE", "CRITIQUE", "FAIBLE"]

    def test_intelligence_forecast_returns_correct_type(self):
        """GET /api/v3/intelligence/forecast returns type=intelligence_forecast"""
        response = requests.get(f"{BASE_URL}/api/v3/intelligence/forecast", params={
            "lat": self.LAT, "lng": self.LNG, "species": self.SPECIES
        })
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "intelligence_forecast"
        
    def test_intelligence_forecast_has_12_months(self):
        """GET /api/v3/intelligence/forecast returns 12 monthly_data entries"""
        response = requests.get(f"{BASE_URL}/api/v3/intelligence/forecast", params={
            "lat": self.LAT, "lng": self.LNG, "species": self.SPECIES
        })
        data = response.json()
        assert "monthly_data" in data
        assert len(data["monthly_data"]) == 12
        # Check each month has required fields
        for m in data["monthly_data"]:
            assert "month" in m
            assert "score" in m
            assert "classe" in m
            
    def test_intelligence_forecast_has_seasonal_scores(self):
        """GET /api/v3/intelligence/forecast has seasonal_scores"""
        response = requests.get(f"{BASE_URL}/api/v3/intelligence/forecast", params={
            "lat": self.LAT, "lng": self.LNG, "species": self.SPECIES
        })
        data = response.json()
        assert "seasonal_scores" in data
        seasons = data["seasonal_scores"]
        assert "printemps" in seasons
        assert "ete" in seasons
        assert "automne" in seasons
        assert "hiver" in seasons
        
    def test_intelligence_forecast_has_best_worst_month(self):
        """GET /api/v3/intelligence/forecast has best_month and worst_month"""
        response = requests.get(f"{BASE_URL}/api/v3/intelligence/forecast", params={
            "lat": self.LAT, "lng": self.LNG, "species": self.SPECIES
        })
        data = response.json()
        assert "best_month" in data
        assert "worst_month" in data
        assert 1 <= data["best_month"] <= 12
        assert 1 <= data["worst_month"] <= 12
        
    def test_intelligence_plan_returns_correct_type(self):
        """GET /api/v3/intelligence/plan returns type=intelligence_plan"""
        response = requests.get(f"{BASE_URL}/api/v3/intelligence/plan", params={
            "lat": self.LAT, "lng": self.LNG, "species": self.SPECIES, "month": self.MONTH
        })
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "intelligence_plan"
        
    def test_intelligence_plan_has_ranked_actions(self):
        """GET /api/v3/intelligence/plan returns ranked actions"""
        response = requests.get(f"{BASE_URL}/api/v3/intelligence/plan", params={
            "lat": self.LAT, "lng": self.LNG, "species": self.SPECIES, "month": self.MONTH
        })
        data = response.json()
        assert "actions" in data
        actions = data["actions"]
        assert len(actions) > 0
        # Check ranking order
        for i, action in enumerate(actions):
            assert action["rank"] == i + 1
            assert "engine" in action
            assert "domain" in action
            assert "score" in action
            assert "urgency" in action
            assert action["urgency"] in ["CRITIQUE", "HAUTE", "MOYENNE", "FAIBLE"]
            
    def test_intelligence_plan_has_critical_count(self):
        """GET /api/v3/intelligence/plan has critical_count"""
        response = requests.get(f"{BASE_URL}/api/v3/intelligence/plan", params={
            "lat": self.LAT, "lng": self.LNG, "species": self.SPECIES, "month": self.MONTH
        })
        data = response.json()
        assert "critical_count" in data
        assert isinstance(data["critical_count"], int)
        assert data["critical_count"] >= 0


class TestM1M2RegressionEndpoints:
    """M1/M2 Regression tests - These should still work after M3+M4"""
    
    LAT = 46.8139
    LNG = -71.2080
    SPECIES = "CHEVREUIL"
    MONTH = 10
    
    def test_engines_registry_returns_5_engines(self):
        """GET /api/v3/engines/registry still returns 5 engines"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/registry")
        assert response.status_code == 200
        data = response.json()
        assert data["total_engines"] == 5
        engine_names = [e["name"] for e in data["engines"]]
        assert "ALIMENTATION-V1" in engine_names
        assert "ALIMENTATION-V2" in engine_names
        assert "REPOS-V1" in engine_names
        assert "CORRIDORS-V10" in engine_names
        assert "PRESSION-V1" in engine_names
        
    def test_engines_validate_returns_overall_compliant(self):
        """GET /api/v3/engines/validate returns overall_compliant=true"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/validate")
        assert response.status_code == 200
        data = response.json()
        assert data["overall_compliant"] == True
        assert data["bce4x"]["compliant"] == True
        assert data["steeve_max"]["compliant"] == True
        
    def test_individual_engine_score_pression(self):
        """GET /api/v3/engines/PRESSION-V1/score returns individual score"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/PRESSION-V1/score", params={
            "lat": self.LAT, "lng": self.LNG, "species": self.SPECIES, "month": self.MONTH
        })
        assert response.status_code == 200
        data = response.json()
        assert data["engine"] == "PRESSION-V1"
        assert "score" in data
        assert 0 <= data["score"] <= 100
        assert data["domain"] == "pression"
        
    def test_species_endpoint_returns_5_canonical(self):
        """GET /api/v3/species returns 5 canonical species"""
        response = requests.get(f"{BASE_URL}/api/v3/species")
        assert response.status_code == 200
        data = response.json()
        assert len(data["species"]) == 5
        assert "CHEVREUIL" in data["species"]
        assert "ORIGNAL" in data["species"]
        assert "OURS" in data["species"]
        assert "DINDON" in data["species"]
        assert "WAPITI" in data["species"]


class TestV1NonRegressionEndpoints:
    """V1 Legacy endpoints - Must still work (backward compatibility)"""
    
    LAT = 46.8139
    LNG = -71.2080
    SPECIES = "CHEVREUIL"
    MONTH = 10
    
    def test_v1_score_consolide_point_works(self):
        """GET /api/v1/score-consolide/point still returns score"""
        response = requests.get(f"{BASE_URL}/api/v1/score-consolide/point", params={
            "lat": self.LAT, "lng": self.LNG, "species": self.SPECIES, "month": self.MONTH
        })
        assert response.status_code == 200
        data = response.json()
        assert "score" in data
        assert "classe" in data
        assert "label" in data
        
    def test_v1_alimentation_point_works(self):
        """GET /api/v1/alimentation/point still returns alimentation score"""
        response = requests.get(f"{BASE_URL}/api/v1/alimentation/point", params={
            "lat": self.LAT, "lng": self.LNG, "species": self.SPECIES, "month": self.MONTH
        })
        assert response.status_code == 200
        data = response.json()
        assert "score_alimentation" in data
        assert "classe_alimentation" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
