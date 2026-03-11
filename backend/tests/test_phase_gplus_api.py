"""
TEST SUITE — PHASE G+ (Comparison + API Keys Healthcheck)
BIONIC V5 ULTIME 300%

API Tests for:
- POST /api/v1/bionic/pipeline/comparison — 5 species, 3 territory pairs
- GET /api/v1/system/api-keys/status — API keys healthcheck
- Non-regression: full-analysis, pipeline/status
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Territories for comparison tests
LAURENTIDES = {"north": 46.95, "south": 46.85, "east": -74.00, "west": -74.15}
GATINEAU = {"north": 45.55, "south": 45.45, "east": -75.70, "west": -75.85}
CHARLEVOIX = {"north": 47.60, "south": 47.50, "east": -70.50, "west": -70.65}

TERRITORY_PAIRS = [
    (LAURENTIDES, GATINEAU, "Laurentides vs Gatineau"),
    (LAURENTIDES, CHARLEVOIX, "Laurentides vs Charlevoix"),
    (GATINEAU, CHARLEVOIX, "Gatineau vs Charlevoix"),
]

SPECIES_LIST = ["moose", "deer", "bear", "wild_turkey", "elk"]
SCORE_DIMENSIONS = [
    "habitat_quality", "corridor_connectivity", "wind_protection",
    "low_pressure", "behavioral_activity", "thermal_comfort", "overall_score"
]

RESOLUTION = 30


@pytest.fixture(scope="session")
def api_client():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


# ============================================================================
# COMPARISON ENDPOINT TESTS — POST /api/v1/bionic/pipeline/comparison
# ============================================================================

class TestComparisonEndpoint:
    """POST /api/v1/bionic/pipeline/comparison — 5 species, 3 pairs"""

    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_comparison_returns_200_for_all_species(self, api_client, species):
        """Comparison endpoint works for all 5 supported species"""
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/pipeline/comparison",
            json={
                "bounds_a": LAURENTIDES,
                "bounds_b": GATINEAU,
                "species": species,
                "resolution": RESOLUTION
            },
            timeout=120
        )
        assert response.status_code == 200, f"Species {species}: {response.text}"
        data = response.json()
        assert data["species"] == species
        assert data["pipeline"] == "BIONIC_V5_ULTIME_300"

    @pytest.mark.parametrize("pair", TERRITORY_PAIRS, ids=[p[2] for p in TERRITORY_PAIRS])
    def test_comparison_works_for_territory_pairs(self, api_client, pair):
        """Comparison endpoint works for 3 territory pairs"""
        bounds_a, bounds_b, desc = pair
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/pipeline/comparison",
            json={
                "bounds_a": bounds_a,
                "bounds_b": bounds_b,
                "species": "moose",
                "resolution": RESOLUTION
            },
            timeout=120
        )
        assert response.status_code == 200, f"{desc}: {response.text}"
        data = response.json()
        assert data["territory_a"]["bounds"] == bounds_a
        assert data["territory_b"]["bounds"] == bounds_b

    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_comparison_scores_per_dimension(self, api_client, species):
        """Comparison returns scores for all 7 dimensions"""
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/pipeline/comparison",
            json={
                "bounds_a": LAURENTIDES,
                "bounds_b": CHARLEVOIX,
                "species": species,
                "resolution": RESOLUTION
            },
            timeout=120
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check both territories have all score dimensions
        for territory in ["territory_a", "territory_b"]:
            scores = data[territory]["scores"]
            for dim in SCORE_DIMENSIONS:
                assert dim in scores, f"{territory} missing {dim}"
                val = scores[dim]
                assert isinstance(val, (int, float)), f"{dim} is not numeric"
                assert 0.0 <= val <= 1.1, f"{dim}={val} out of range [0,1]"

    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_comparison_recommendation(self, api_client, species):
        """Comparison returns valid recommendation"""
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/pipeline/comparison",
            json={
                "bounds_a": LAURENTIDES,
                "bounds_b": GATINEAU,
                "species": species,
                "resolution": RESOLUTION
            },
            timeout=120
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "recommendation" in data
        assert data["recommendation"] in ("territory_a", "territory_b", "equivalent")

    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_comparison_advantages(self, api_client, species):
        """Comparison returns advantages structure"""
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/pipeline/comparison",
            json={
                "bounds_a": LAURENTIDES,
                "bounds_b": CHARLEVOIX,
                "species": species,
                "resolution": RESOLUTION
            },
            timeout=120
        )
        assert response.status_code == 200
        data = response.json()
        
        adv = data["advantages"]
        assert "territory_a_advantages" in adv
        assert "territory_b_advantages" in adv
        assert "ties" in adv
        
        # Advantages should be lists
        assert isinstance(adv["territory_a_advantages"], list)
        assert isinstance(adv["territory_b_advantages"], list)
        assert isinstance(adv["ties"], list)

    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_comparison_10_source_ids_per_territory(self, api_client, species):
        """Comparison returns 10 source_ids per territory"""
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/pipeline/comparison",
            json={
                "bounds_a": GATINEAU,
                "bounds_b": CHARLEVOIX,
                "species": species,
                "resolution": RESOLUTION
            },
            timeout=120
        )
        assert response.status_code == 200
        data = response.json()
        
        for territory in ["territory_a", "territory_b"]:
            source_ids = data[territory]["source_ids"]
            assert len(source_ids) == 10, f"{territory} has {len(source_ids)} source_ids, expected 10"

    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_comparison_validation_flags(self, api_client, species):
        """Comparison returns validation flags"""
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/pipeline/comparison",
            json={
                "bounds_a": LAURENTIDES,
                "bounds_b": GATINEAU,
                "species": species,
                "resolution": RESOLUTION
            },
            timeout=120
        )
        assert response.status_code == 200
        data = response.json()
        
        v = data["validation"]
        assert v["pipeline_a_complete"] is True
        assert v["pipeline_b_complete"] is True
        assert v["zero_transversality"] is True
        assert v["comparison_post_pipeline"] is True

    def test_comparison_invalid_species_returns_400(self, api_client):
        """Invalid species returns 400"""
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/pipeline/comparison",
            json={
                "bounds_a": LAURENTIDES,
                "bounds_b": GATINEAU,
                "species": "invalid_animal",
                "resolution": RESOLUTION
            },
            timeout=30
        )
        assert response.status_code == 400
        assert "non supportee" in response.json().get("detail", "").lower() or "supportees" in response.json().get("detail", "").lower()

    def test_comparison_score_delta_matches(self, api_client):
        """score_delta matches difference of overall_score"""
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/pipeline/comparison",
            json={
                "bounds_a": LAURENTIDES,
                "bounds_b": CHARLEVOIX,
                "species": "bear",
                "resolution": RESOLUTION
            },
            timeout=120
        )
        assert response.status_code == 200
        data = response.json()
        
        score_a = data["territory_a"]["scores"]["overall_score"]
        score_b = data["territory_b"]["scores"]["overall_score"]
        expected_delta = round(score_a - score_b, 4)
        assert data["score_delta"] == expected_delta


# ============================================================================
# API KEYS STATUS ENDPOINT — GET /api/v1/system/api-keys/status
# ============================================================================

class TestApiKeysStatus:
    """GET /api/v1/system/api-keys/status — healthcheck endpoint"""

    def test_api_keys_status_returns_200(self, api_client):
        """API keys status endpoint returns 200"""
        response = api_client.get(
            f"{BASE_URL}/api/v1/system/api-keys/status",
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert data["pipeline"] == "BIONIC_V5_ULTIME_300"

    def test_api_keys_status_returns_6_keys(self, api_client):
        """API keys status returns 6 keys"""
        response = api_client.get(
            f"{BASE_URL}/api/v1/system/api-keys/status",
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_keys"] == 6
        assert len(data["key_statuses"]) == 6
        
        # Check expected keys
        expected_keys = [
            "sentinel2_ndvi", "elevation_dem", "weather_realtime",
            "thermal_flow", "ml_cloud", "storage_export"
        ]
        for key in expected_keys:
            assert key in data["key_statuses"], f"Missing key: {key}"

    def test_api_keys_status_not_configured(self, api_client):
        """All keys should be not_configured (no external keys set)"""
        response = api_client.get(
            f"{BASE_URL}/api/v1/system/api-keys/status",
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        
        for key_name, status in data["key_statuses"].items():
            assert status["status"] == "not_configured", f"{key_name} is {status['status']}"

    def test_api_keys_status_has_fallbacks(self, api_client):
        """All keys should have fallback configured"""
        response = api_client.get(
            f"{BASE_URL}/api/v1/system/api-keys/status",
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        
        for key_name, status in data["key_statuses"].items():
            assert "fallback" in status, f"{key_name} missing fallback"
            assert status["fallback"] != "none", f"{key_name} has no fallback"

    def test_api_keys_phase_compatibility(self, api_client):
        """API keys returns phase_compatibility"""
        response = api_client.get(
            f"{BASE_URL}/api/v1/system/api-keys/status",
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        
        pc = data["phase_compatibility"]
        assert "pipeline_internal" in pc
        assert pc["pipeline_internal"]["status"] == "fully_operational"
        assert "phase_g_real_data" in pc
        assert "phase_h_ml" in pc

    def test_api_keys_validation_flags(self, api_client):
        """API keys returns validation object"""
        response = api_client.get(
            f"{BASE_URL}/api/v1/system/api-keys/status",
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        
        v = data["validation"]
        assert v["pipeline_internal_operational"] is True
        assert v["all_fallbacks_available"] is True


# ============================================================================
# NON-REGRESSION TESTS — Existing endpoints
# ============================================================================

class TestNonRegression:
    """Non-regression tests for existing endpoints"""

    def test_pipeline_status_working(self, api_client):
        """GET /api/v1/bionic/pipeline/status still works"""
        response = api_client.get(
            f"{BASE_URL}/api/v1/bionic/pipeline/status",
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert data["pipeline"] == "BIONIC_V5_ULTIME_300"
        assert data["module_count"] == 10
        assert len(data["pipeline_order"]) == 10

    def test_full_analysis_working(self, api_client):
        """POST /api/v1/bionic/pipeline/full-analysis still works"""
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/pipeline/full-analysis",
            json={
                "bounds": LAURENTIDES,
                "species": "moose",
                "resolution": RESOLUTION
            },
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        assert data["pipeline"] == "BIONIC_V5_ULTIME_300"
        assert data["species"] == "moose"
        assert len(data["pipeline_source_ids"]) == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
