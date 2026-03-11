"""
BIONIC V5 P0 — Dynamic source_id Validation Tests
Tests the P0 fix: source_id must be dynamic based on species from orchestrator.
No hardcoded fallback allowed.

source_id format: BIONIC_V5_{SPECIES.UPPER()}
Must appear in: metadata.source_id, properties.source_id, scoring_detail.source_id
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test bounds for Quebec region
TEST_BOUNDS = {
    "north": 47.05,
    "south": 46.95,
    "east": -71.15,
    "west": -71.25
}

# All species to test
SPECIES_LIST = ["moose", "deer", "bear", "wild_turkey", "elk"]


class TestDynamicSourceIdP0:
    """Tests for P0 fix: Dynamic source_id based on species"""

    @pytest.fixture
    def api_client(self):
        """Shared requests session"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        return session

    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_source_id_dynamic_for_species(self, api_client, species):
        """
        POST /api/v1/bionic/organic-zones with species={species}
        Verify source_id=BIONIC_V5_{SPECIES} in metadata, properties, scoring_detail
        """
        expected_source_id = f"BIONIC_V5_{species.upper()}"
        
        payload = {
            "bounds": TEST_BOUNDS,
            "species": species,
            "layers": ["habitats", "alimentation"],
            "resolution": 30,
            "max_zones_per_layer": 2,
            "include_scoring": True,
            "season": "autumn"
        }
        
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/organic-zones", json=payload)
        
        # Status assertion
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify GeoJSON structure
        assert data.get("type") == "FeatureCollection", "Response must be a GeoJSON FeatureCollection"
        
        # 1. Check metadata.source_id
        metadata = data.get("metadata", {})
        assert metadata.get("source_id") == expected_source_id, \
            f"metadata.source_id expected '{expected_source_id}', got '{metadata.get('source_id')}'"
        
        # 2. Check features
        features = data.get("features", [])
        if len(features) == 0:
            pytest.skip(f"No features returned for species={species}, cannot verify source_id in properties")
        
        for i, feature in enumerate(features):
            props = feature.get("properties", {})
            
            # Check properties.source_id
            assert props.get("source_id") == expected_source_id, \
                f"Feature[{i}] properties.source_id expected '{expected_source_id}', got '{props.get('source_id')}'"
            
            # Check scoring_detail.source_id
            scoring = props.get("scoring_detail", {})
            assert scoring.get("source_id") == expected_source_id, \
                f"Feature[{i}] scoring_detail.source_id expected '{expected_source_id}', got '{scoring.get('source_id')}'"

    def test_moose_source_id_explicit(self, api_client):
        """Explicit test for moose to ensure no silent fallback"""
        expected = "BIONIC_V5_MOOSE"
        
        payload = {
            "bounds": TEST_BOUNDS,
            "species": "moose",
            "layers": ["habitats"],
            "resolution": 30,
            "max_zones_per_layer": 2,
            "include_scoring": True
        }
        
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/organic-zones", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("metadata", {}).get("source_id") == expected

    def test_deer_source_id_not_moose(self, api_client):
        """Critical: deer must NOT have BIONIC_V5_MOOSE (no fallback)"""
        
        payload = {
            "bounds": TEST_BOUNDS,
            "species": "deer",
            "layers": ["habitats"],
            "resolution": 30,
            "max_zones_per_layer": 2,
            "include_scoring": True
        }
        
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/organic-zones", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        metadata_source = data.get("metadata", {}).get("source_id")
        
        # Must NOT be MOOSE fallback
        assert metadata_source != "BIONIC_V5_MOOSE", \
            f"deer request returned MOOSE source_id - fallback detected!"
        
        # Must be DEER
        assert metadata_source == "BIONIC_V5_DEER", \
            f"Expected 'BIONIC_V5_DEER', got '{metadata_source}'"

    def test_bear_source_id_not_moose(self, api_client):
        """Critical: bear must NOT have BIONIC_V5_MOOSE (no fallback)"""
        
        payload = {
            "bounds": TEST_BOUNDS,
            "species": "bear",
            "layers": ["habitats"],
            "resolution": 30,
            "max_zones_per_layer": 2,
            "include_scoring": True
        }
        
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/organic-zones", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        metadata_source = data.get("metadata", {}).get("source_id")
        
        # Must NOT be MOOSE fallback
        assert metadata_source != "BIONIC_V5_MOOSE", \
            f"bear request returned MOOSE source_id - fallback detected!"
        
        # Must be BEAR
        assert metadata_source == "BIONIC_V5_BEAR", \
            f"Expected 'BIONIC_V5_BEAR', got '{metadata_source}'"

    def test_wild_turkey_source_id_not_moose(self, api_client):
        """Critical: wild_turkey must NOT have BIONIC_V5_MOOSE (no fallback)"""
        
        payload = {
            "bounds": TEST_BOUNDS,
            "species": "wild_turkey",
            "layers": ["habitats"],
            "resolution": 30,
            "max_zones_per_layer": 2,
            "include_scoring": True
        }
        
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/organic-zones", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        metadata_source = data.get("metadata", {}).get("source_id")
        
        # Must NOT be MOOSE fallback
        assert metadata_source != "BIONIC_V5_MOOSE", \
            f"wild_turkey request returned MOOSE source_id - fallback detected!"
        
        # Must be WILD_TURKEY
        assert metadata_source == "BIONIC_V5_WILD_TURKEY", \
            f"Expected 'BIONIC_V5_WILD_TURKEY', got '{metadata_source}'"

    def test_elk_source_id_not_moose(self, api_client):
        """Critical: elk must NOT have BIONIC_V5_MOOSE (no fallback)"""
        
        payload = {
            "bounds": TEST_BOUNDS,
            "species": "elk",
            "layers": ["habitats"],
            "resolution": 30,
            "max_zones_per_layer": 2,
            "include_scoring": True
        }
        
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/organic-zones", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        metadata_source = data.get("metadata", {}).get("source_id")
        
        # Must NOT be MOOSE fallback
        assert metadata_source != "BIONIC_V5_MOOSE", \
            f"elk request returned MOOSE source_id - fallback detected!"
        
        # Must be ELK
        assert metadata_source == "BIONIC_V5_ELK", \
            f"Expected 'BIONIC_V5_ELK', got '{metadata_source}'"


class TestRegressionEndpoints:
    """Regression tests for existing endpoints"""

    @pytest.fixture
    def api_client(self):
        """Shared requests session"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        return session

    def test_layers_endpoint_returns_layers_and_species(self, api_client):
        """GET /api/v1/bionic/organic-zones/layers must return layers and species"""
        
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/organic-zones/layers")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Must have 'layers' key with list
        assert "layers" in data, "Response missing 'layers' key"
        assert isinstance(data["layers"], list), "'layers' must be a list"
        assert len(data["layers"]) > 0, "'layers' must not be empty"
        
        # Must have 'species' key with list
        assert "species" in data, "Response missing 'species' key"
        assert isinstance(data["species"], list), "'species' must be a list"
        assert len(data["species"]) > 0, "'species' must not be empty"
        
        # Verify layer structure
        for layer in data["layers"]:
            assert "id" in layer, "Layer missing 'id'"
            assert "label" in layer, "Layer missing 'label'"

    def test_seasonal_conditions_endpoint(self, api_client):
        """GET /api/v1/bionic/seasonal-conditions must return meteo/phenologie"""
        
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/seasonal-conditions?lat=47.0&lng=-71.2")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Must have meteo data
        assert "meteo" in data or "weather" in data or "temperature" in data, \
            "Response missing weather/meteo data"
        
        # Should have score or phenologie
        has_score = "score" in data
        has_phenologie = "phenologie" in data or "phenology" in data
        assert has_score or has_phenologie, "Response missing score or phenologie"

    def test_corridors_endpoint_no_500(self, api_client):
        """POST /api/v1/bionic/map/corridors must not return 500"""
        
        payload = {
            "bounds": TEST_BOUNDS,
            "species": "moose"
        }
        
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/map/corridors", json=payload)
        
        # Must not be 500 server error
        assert response.status_code != 500, \
            f"Corridors endpoint returned 500 server error: {response.text}"
        
        # Accept 200, 404, or other non-500 codes
        assert response.status_code < 500, \
            f"Unexpected server error {response.status_code}: {response.text}"


class TestSourceIdConsistency:
    """Test source_id consistency across all locations"""

    @pytest.fixture
    def api_client(self):
        """Shared requests session"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        return session

    def test_all_source_ids_match_within_response(self, api_client):
        """All source_id values in a response must match the expected species"""
        
        for species in SPECIES_LIST:
            expected = f"BIONIC_V5_{species.upper()}"
            
            payload = {
                "bounds": TEST_BOUNDS,
                "species": species,
                "layers": ["habitats", "alimentation"],
                "resolution": 30,
                "max_zones_per_layer": 3,
                "include_scoring": True
            }
            
            response = api_client.post(f"{BASE_URL}/api/v1/bionic/organic-zones", json=payload)
            assert response.status_code == 200
            
            data = response.json()
            
            # Collect all source_ids found
            source_ids_found = []
            
            # From metadata
            if data.get("metadata", {}).get("source_id"):
                source_ids_found.append(("metadata", data["metadata"]["source_id"]))
            
            # From each feature
            for i, feature in enumerate(data.get("features", [])):
                props = feature.get("properties", {})
                if props.get("source_id"):
                    source_ids_found.append((f"feature[{i}].properties", props["source_id"]))
                
                scoring = props.get("scoring_detail", {})
                if scoring.get("source_id"):
                    source_ids_found.append((f"feature[{i}].scoring_detail", scoring["source_id"]))
            
            # All must match expected
            for location, found_id in source_ids_found:
                assert found_id == expected, \
                    f"species={species}: {location} has source_id='{found_id}', expected '{expected}'"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
