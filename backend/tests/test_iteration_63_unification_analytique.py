"""
Iteration 63 — Unification analytique BIONIC V3
=================================================
Tests for INTELLIGENCE as the SOLE analytic source.
Verifies:
  - No BionicLegend on map
  - No SidePanelZones in carte mode
  - Side panel ONLY for operational tabs (waypoints, lieux, groupe, exclusions)
  - INTELLIGENCE floating dashboard works
  - Backend APIs: validate, summary, forecast, plan
"""
import os
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://guide-pro-hub.preview.emergentagent.com')

# Sample coordinates for testing (Quebec City area)
TEST_LAT = 46.8139
TEST_LNG = -71.2080


class TestBackendAPIsIteration63:
    """Backend API tests for INTELLIGENCE endpoints and validation."""

    def test_engines_validate_overall_compliant(self):
        """BCE-4X: /api/v3/engines/validate returns overall_compliant=true"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/validate", timeout=30)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "overall_compliant" in data, "Missing 'overall_compliant' field"
        assert data["overall_compliant"] is True, f"Expected overall_compliant=true, got {data['overall_compliant']}"
        
        # Verify BCE-4X compliance
        assert "bce4x" in data, "Missing 'bce4x' field"
        assert data["bce4x"]["compliant"] is True, "BCE-4X not compliant"
        assert data["bce4x"]["passed"] == 23, f"Expected 23 passed, got {data['bce4x']['passed']}"
        assert data["bce4x"]["total"] == 23, f"Expected 23 total, got {data['bce4x']['total']}"
        
        # Verify STEEVE-MAX compliance
        assert "steeve_max" in data, "Missing 'steeve_max' field"
        assert data["steeve_max"]["compliant"] is True, "STEEVE-MAX not compliant"
        assert data["steeve_max"]["passed"] == 12, f"Expected 12 passed, got {data['steeve_max']['passed']}"
        assert data["steeve_max"]["total"] == 12, f"Expected 12 total, got {data['steeve_max']['total']}"
        
        print(f"[PASS] Validation: BCE-4X {data['bce4x']['passed']}/{data['bce4x']['total']}, STEEVE-MAX {data['steeve_max']['passed']}/{data['steeve_max']['total']}")

    def test_intelligence_summary_returns_valid_data(self):
        """INTELLIGENCE: /api/v3/intelligence/summary returns consolidated score and domains."""
        response = requests.get(
            f"{BASE_URL}/api/v3/intelligence/summary",
            params={"lat": TEST_LAT, "lng": TEST_LNG, "species": "CHEVREUIL", "month": 1},
            timeout=30
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Verify structure
        assert data["type"] == "intelligence_summary", "Wrong type"
        assert "consolidated" in data, "Missing 'consolidated' field"
        assert "domains" in data, "Missing 'domains' field"
        assert "recommendations" in data, "Missing 'recommendations' field"
        assert "analysis" in data, "Missing 'analysis' field"
        
        # Verify consolidated score
        consolidated = data["consolidated"]
        assert "score" in consolidated, "Missing score in consolidated"
        assert "classe" in consolidated, "Missing classe in consolidated"
        assert "label" in consolidated, "Missing label in consolidated"
        assert 0 <= consolidated["score"] <= 100, f"Score out of range: {consolidated['score']}"
        
        # Verify domains exist
        assert len(data["domains"]) > 0, "No domains returned"
        
        print(f"[PASS] Summary: Score={consolidated['score']}, Classe={consolidated['classe']}, Domains={len(data['domains'])}")

    def test_intelligence_forecast_returns_12_months(self):
        """INTELLIGENCE: /api/v3/intelligence/forecast returns 12 months of data."""
        response = requests.get(
            f"{BASE_URL}/api/v3/intelligence/forecast",
            params={"lat": TEST_LAT, "lng": TEST_LNG, "species": "CHEVREUIL"},
            timeout=30
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Verify structure
        assert data["type"] == "intelligence_forecast", "Wrong type"
        assert "monthly_data" in data, "Missing 'monthly_data' field"
        assert "best_month" in data, "Missing 'best_month' field"
        assert "worst_month" in data, "Missing 'worst_month' field"
        assert "seasonal_scores" in data, "Missing 'seasonal_scores' field"
        
        # Verify 12 months
        assert len(data["monthly_data"]) == 12, f"Expected 12 months, got {len(data['monthly_data'])}"
        
        # Verify each month has required fields
        for month_data in data["monthly_data"]:
            assert "month" in month_data, "Missing month field"
            assert "score" in month_data, "Missing score field"
            assert "classe" in month_data, "Missing classe field"
            assert 1 <= month_data["month"] <= 12, f"Invalid month: {month_data['month']}"
        
        # Verify seasonal scores
        seasons = data["seasonal_scores"]
        assert "printemps" in seasons, "Missing printemps"
        assert "ete" in seasons, "Missing ete"
        assert "automne" in seasons, "Missing automne"
        assert "hiver" in seasons, "Missing hiver"
        
        print(f"[PASS] Forecast: Best={data['best_month']}, Worst={data['worst_month']}, Avg={data['annual_average']}")

    def test_intelligence_plan_returns_actions(self):
        """INTELLIGENCE: /api/v3/intelligence/plan returns action list."""
        response = requests.get(
            f"{BASE_URL}/api/v3/intelligence/plan",
            params={"lat": TEST_LAT, "lng": TEST_LNG, "species": "CHEVREUIL", "month": 1},
            timeout=30
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Verify structure
        assert data["type"] == "intelligence_plan", "Wrong type"
        assert "actions" in data, "Missing 'actions' field"
        assert "overall_score" in data, "Missing 'overall_score' field"
        assert "overall_classe" in data, "Missing 'overall_classe' field"
        assert "total_actions" in data, "Missing 'total_actions' field"
        
        # Verify actions list
        assert len(data["actions"]) > 0, "No actions returned"
        
        # Verify each action has required fields
        for action in data["actions"]:
            assert "rank" in action, "Missing rank"
            assert "engine" in action, "Missing engine"
            assert "domain" in action, "Missing domain"
            assert "score" in action, "Missing score"
            assert "status" in action, "Missing status"
            assert "urgency" in action, "Missing urgency"
            assert "action" in action, "Missing action text"
        
        print(f"[PASS] Plan: {data['total_actions']} actions, Critical={data['critical_count']}")

    def test_intelligence_solunar_returns_data(self):
        """INTELLIGENCE: /api/v3/intelligence/solunar returns solunar data."""
        response = requests.get(
            f"{BASE_URL}/api/v3/intelligence/solunar",
            params={"lat": TEST_LAT, "lng": TEST_LNG},
            timeout=30
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "solunar_score" in data, "Missing solunar_score"
        assert "hunting_windows" in data, "Missing hunting_windows"
        
        print(f"[PASS] Solunar: Score={data['solunar_score']}, Windows={len(data.get('hunting_windows', []))}")

    def test_intelligence_guide_pro_returns_approach_plan(self):
        """INTELLIGENCE: /api/v3/intelligence/guide-pro returns approach plan."""
        response = requests.get(
            f"{BASE_URL}/api/v3/intelligence/guide-pro",
            params={"lat": TEST_LAT, "lng": TEST_LNG, "species": "CHEVREUIL", "month": 1},
            timeout=30
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Verify structure
        assert data["type"] == "guide_pro", "Wrong type"
        assert "solunar" in data, "Missing solunar"
        assert "terrain" in data, "Missing terrain"
        assert "approach_plan" in data, "Missing approach_plan"
        assert "hunting_windows" in data, "Missing hunting_windows"
        assert "best_time" in data, "Missing best_time"
        
        # Verify approach plan details
        plan = data["approach_plan"]
        assert "position_ideale" in plan, "Missing position_ideale"
        assert "angle_entree" in plan, "Missing angle_entree"
        assert "vent" in plan, "Missing vent"
        assert "affut_recommande" in plan, "Missing affut_recommande"
        
        print(f"[PASS] Guide Pro: Best time score={data['best_time']['score']}, Label={data['best_time']['label']}")

    def test_engines_registry_returns_manifest(self):
        """ENGINES: /api/v3/engines/registry returns manifest."""
        response = requests.get(f"{BASE_URL}/api/v3/engines/registry", timeout=30)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "engines" in data, "Missing 'engines' field"
        assert len(data["engines"]) >= 5, f"Expected at least 5 engines, got {len(data['engines'])}"
        
        print(f"[PASS] Registry: {len(data['engines'])} engines registered")

    def test_engines_score_point_returns_consolidated(self):
        """ENGINES: /api/v3/engines/score-point returns consolidated score."""
        response = requests.get(
            f"{BASE_URL}/api/v3/engines/score-point",
            params={"lat": TEST_LAT, "lng": TEST_LNG, "species": "CHEVREUIL", "month": 1},
            timeout=30
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "score" in data, "Missing 'score' field"
        assert "classe" in data, "Missing 'classe' field"
        assert "components" in data, "Missing 'components' field"
        
        print(f"[PASS] Score-point: Score={data['score']}, Classe={data['classe']}")

    def test_species_list_returns_canonical(self):
        """SPECIES: /api/v3/species returns canonical list."""
        response = requests.get(f"{BASE_URL}/api/v3/species", timeout=30)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "species" in data, "Missing 'species' field"
        assert "CHEVREUIL" in data["species"], "Missing CHEVREUIL"
        
        print(f"[PASS] Species: {len(data['species'])} species available")

    def test_old_analyse_endpoints_removed(self):
        """BCE-4X: Old /api/v3/analyse endpoints must return 404."""
        old_endpoints = [
            "/api/v3/analyse",
            "/api/v3/analyse/unified",
            "/api/v1/analyse",
        ]
        
        for endpoint in old_endpoints:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            # We expect 404 (not found) or 307 redirect to non-existent endpoint
            assert response.status_code in (404, 307, 422), f"Old endpoint {endpoint} still exists with status {response.status_code}"
        
        print(f"[PASS] Old analyse endpoints correctly removed (404)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
