"""
TEST SSE ENGINE — Satellite-to-Semantic Engine
BIONIC V5 ULTIME 300% — Phase d'Optimisation #1

Tests:
  - POST /api/v1/bionic/sse/analyze for all 5 species
  - GET /api/v1/bionic/sse/status
  - source_id dynamic SSE_{SPECIES}
  - Data normalization [0, 1]
  - include_vectors=false behavior
  - Different territory bounds (Quebec, Abitibi, Laurentides)
  - Performance <500ms
  - REGRESSION: organic-zones endpoints

Iteration: 63
"""

import pytest
import requests
import os
import time

# API base URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Bounds for testing (3 different territories)
BOUNDS_QUEBEC = {"north": 47.05, "south": 46.95, "east": -71.15, "west": -71.25}
BOUNDS_ABITIBI = {"north": 48.60, "south": 48.50, "east": -78.90, "west": -79.00}
BOUNDS_LAURENTIDES = {"north": 46.20, "south": 46.10, "east": -74.50, "west": -74.60}

# All supported species
ALL_SPECIES = ["moose", "deer", "bear", "wild_turkey", "elk"]


@pytest.fixture
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


# =====================================================================
# SSE /analyze ENDPOINT TESTS — All 5 Species
# =====================================================================

class TestSSEAnalyzeAllSpecies:
    """Test /api/v1/bionic/sse/analyze for all 5 species"""

    @pytest.mark.parametrize("species,expected_source_id", [
        ("moose", "SSE_MOOSE"),
        ("deer", "SSE_DEER"),
        ("bear", "SSE_BEAR"),
        ("wild_turkey", "SSE_WILD_TURKEY"),
        ("elk", "SSE_ELK"),
    ])
    def test_sse_analyze_source_id_per_species(self, api_client, species, expected_source_id):
        """Verify source_id=SSE_{SPECIES} for each species"""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": species,
            "resolution": 40,
            "include_vectors": True
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/sse/analyze", json=payload)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        data = response.json()

        # Verify source_id is dynamic SSE_{SPECIES}
        assert "source_id" in data, "Missing source_id in response"
        assert data["source_id"] == expected_source_id, f"Expected {expected_source_id}, got {data['source_id']}"

        # Verify species matches
        assert data.get("species") == species, f"Species mismatch: expected {species}, got {data.get('species')}"

    @pytest.mark.parametrize("species", ALL_SPECIES)
    def test_sse_analyze_has_all_sublayers(self, api_client, species):
        """Verify all sub-layers are present: landcover, microrelief, composite, edge_vectors"""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": species,
            "resolution": 40,
            "include_vectors": True
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/sse/analyze", json=payload)

        assert response.status_code == 200, f"Status {response.status_code}: {response.text}"

        data = response.json()

        # landcover_summary must exist
        assert "landcover_summary" in data, "Missing landcover_summary"
        lc = data["landcover_summary"]
        assert "forest_density_range" in lc, "Missing forest_density_range"
        assert "clearing_range" in lc, "Missing clearing_range"
        assert "conifer_ratio_range" in lc, "Missing conifer_ratio_range"
        assert "wetland_prob_range" in lc, "Missing wetland_prob_range"

        # microrelief_summary must exist
        assert "microrelief_summary" in data, "Missing microrelief_summary"
        mr = data["microrelief_summary"]
        assert "ridge_range" in mr, "Missing ridge_range"
        assert "valley_range" in mr, "Missing valley_range"
        assert "slope_range" in mr, "Missing slope_range"
        assert "plateau_range" in mr, "Missing plateau_range"

        # composite_summary must exist
        assert "composite_summary" in data, "Missing composite_summary"
        cs = data["composite_summary"]
        assert "mean" in cs and "std" in cs and "min" in cs and "max" in cs

        # edge_vectors (when include_vectors=True)
        assert "edge_vectors" in data, "Missing edge_vectors"
        assert "edge_count" in data, "Missing edge_count"


class TestSSEDataNormalization:
    """Verify all ranges are normalized [0, 1]"""

    @pytest.mark.parametrize("species", ALL_SPECIES)
    def test_landcover_ranges_in_0_1(self, api_client, species):
        """Verify landcover ranges are within [0, 1]"""
        payload = {"bounds": BOUNDS_QUEBEC, "species": species, "resolution": 40}
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/sse/analyze", json=payload)

        assert response.status_code == 200

        data = response.json()
        lc = data["landcover_summary"]

        for key in ["forest_density_range", "clearing_range", "conifer_ratio_range", "wetland_prob_range"]:
            rng = lc[key]
            assert len(rng) == 2, f"{key} should have [min, max]"
            assert 0.0 <= rng[0] <= 1.0, f"{key} min out of [0,1]: {rng[0]}"
            assert 0.0 <= rng[1] <= 1.0, f"{key} max out of [0,1]: {rng[1]}"

    @pytest.mark.parametrize("species", ALL_SPECIES)
    def test_microrelief_ranges_in_0_1(self, api_client, species):
        """Verify microrelief ranges are within [0, 1]"""
        payload = {"bounds": BOUNDS_QUEBEC, "species": species, "resolution": 40}
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/sse/analyze", json=payload)

        assert response.status_code == 200

        data = response.json()
        mr = data["microrelief_summary"]

        for key in ["ridge_range", "valley_range", "slope_range", "plateau_range"]:
            rng = mr[key]
            assert len(rng) == 2, f"{key} should have [min, max]"
            assert 0.0 <= rng[0] <= 1.0, f"{key} min out of [0,1]: {rng[0]}"
            assert 0.0 <= rng[1] <= 1.0, f"{key} max out of [0,1]: {rng[1]}"

    @pytest.mark.parametrize("species", ALL_SPECIES)
    def test_composite_summary_in_0_1(self, api_client, species):
        """Verify composite_summary mean, std, min, max are in [0, 1]"""
        payload = {"bounds": BOUNDS_QUEBEC, "species": species, "resolution": 40}
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/sse/analyze", json=payload)

        assert response.status_code == 200

        data = response.json()
        cs = data["composite_summary"]

        assert 0.0 <= cs["mean"] <= 1.0, f"composite mean out of [0,1]: {cs['mean']}"
        assert 0.0 <= cs["std"] <= 1.0, f"composite std out of [0,1]: {cs['std']}"
        assert 0.0 <= cs["min"] <= 1.0, f"composite min out of [0,1]: {cs['min']}"
        assert 0.0 <= cs["max"] <= 1.0, f"composite max out of [0,1]: {cs['max']}"


class TestSSEIncludeVectors:
    """Test include_vectors=false behavior"""

    def test_include_vectors_false_no_edge_vectors(self, api_client):
        """When include_vectors=false, edge_vectors should not be in response"""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": "moose",
            "resolution": 40,
            "include_vectors": False
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/sse/analyze", json=payload)

        assert response.status_code == 200

        data = response.json()
        assert "edge_vectors" not in data, "edge_vectors should NOT be present when include_vectors=false"
        assert "edge_count" not in data, "edge_count should NOT be present when include_vectors=false"

    def test_include_vectors_true_has_edge_vectors(self, api_client):
        """When include_vectors=true, edge_vectors should be present"""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": "moose",
            "resolution": 40,
            "include_vectors": True
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/sse/analyze", json=payload)

        assert response.status_code == 200

        data = response.json()
        assert "edge_vectors" in data, "edge_vectors should be present when include_vectors=true"
        assert "edge_count" in data, "edge_count should be present when include_vectors=true"
        assert isinstance(data["edge_vectors"], list), "edge_vectors should be a list"


class TestSSEDifferentTerritories:
    """Test different territories produce different data"""

    def test_different_territories_different_data(self, api_client):
        """Quebec, Abitibi, Laurentides should produce different data"""
        territories = [
            ("Quebec", BOUNDS_QUEBEC),
            ("Abitibi", BOUNDS_ABITIBI),
            ("Laurentides", BOUNDS_LAURENTIDES),
        ]

        results = {}
        for name, bounds in territories:
            payload = {"bounds": bounds, "species": "moose", "resolution": 40}
            response = api_client.post(f"{BASE_URL}/api/v1/bionic/sse/analyze", json=payload)
            assert response.status_code == 200, f"{name} failed: {response.text}"
            results[name] = response.json()

        # Verify composite means are different
        quebec_mean = results["Quebec"]["composite_summary"]["mean"]
        abitibi_mean = results["Abitibi"]["composite_summary"]["mean"]
        laurentides_mean = results["Laurentides"]["composite_summary"]["mean"]

        # At least 2 of 3 should differ (small tolerance for floating point)
        diffs = [
            abs(quebec_mean - abitibi_mean) > 0.001,
            abs(quebec_mean - laurentides_mean) > 0.001,
            abs(abitibi_mean - laurentides_mean) > 0.001,
        ]
        assert sum(diffs) >= 2, f"Expected different data for territories: Quebec={quebec_mean}, Abitibi={abitibi_mean}, Laurentides={laurentides_mean}"


class TestSSEInvalidSpecies:
    """Test invalid species handling"""

    def test_invalid_species_returns_400(self, api_client):
        """Invalid species should return 400"""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": "unicorn",  # Invalid species
            "resolution": 40
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/sse/analyze", json=payload)

        assert response.status_code == 400, f"Expected 400 for invalid species, got {response.status_code}"

        data = response.json()
        assert "detail" in data, "Error response should have 'detail'"


class TestSSEPerformance:
    """Test performance < 500ms for resolution=40"""

    def test_performance_under_500ms(self, api_client):
        """Response time should be < 500ms for resolution=40"""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": "moose",
            "resolution": 40,
            "include_vectors": True
        }

        start = time.time()
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/sse/analyze", json=payload)
        elapsed_ms = (time.time() - start) * 1000

        assert response.status_code == 200

        data = response.json()
        computation_time = data.get("computation_time_ms", 0)

        # Check API-reported computation time
        assert computation_time < 500, f"Computation time {computation_time}ms exceeds 500ms limit"

        # Check total request time (with network overhead)
        assert elapsed_ms < 2000, f"Total request time {elapsed_ms}ms too slow"


# =====================================================================
# SSE /status ENDPOINT TESTS
# =====================================================================

class TestSSEStatus:
    """Test GET /api/v1/bionic/sse/status endpoint"""

    def test_status_endpoint_returns_active(self, api_client):
        """Status endpoint should return active module"""
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/sse/status")

        assert response.status_code == 200, f"Status {response.status_code}: {response.text}"

        data = response.json()
        assert data.get("status") == "active", f"Expected active status, got {data.get('status')}"
        assert data.get("module") == "SSE", f"Expected module=SSE, got {data.get('module')}"

    def test_status_has_5_species(self, api_client):
        """Status should list 5 supported species"""
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/sse/status")

        assert response.status_code == 200

        data = response.json()
        species_supported = data.get("species_supported", [])
        assert len(species_supported) == 5, f"Expected 5 species, got {len(species_supported)}"
        for sp in ALL_SPECIES:
            assert sp in species_supported, f"Missing species: {sp}"

    def test_status_consumers_osg_cme_wse(self, api_client):
        """Status should list consumers: OSG, CME, WSE"""
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/sse/status")

        assert response.status_code == 200

        data = response.json()
        consumers = data.get("consumers", [])
        for consumer in ["OSG", "CME", "WSE"]:
            assert consumer in consumers, f"Missing consumer: {consumer}"


# =====================================================================
# REGRESSION TESTS — Organic Zones Endpoints
# =====================================================================

class TestRegressionOrganicZones:
    """REGRESSION: Verify organic-zones endpoints still work after SSE addition"""

    def test_organic_zones_analyze_with_moose(self, api_client):
        """POST /api/v1/bionic/organic-zones should return source_id BIONIC_V5_MOOSE"""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": "moose",
            "resolution": 30
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/organic-zones", json=payload)

        assert response.status_code == 200, f"Status {response.status_code}: {response.text}"

        data = response.json()
        # Check source_id in metadata
        metadata = data.get("metadata", {})
        source_id = metadata.get("source_id", "")
        assert "BIONIC_V5_MOOSE" in source_id, f"Expected BIONIC_V5_MOOSE, got {source_id}"

    def test_organic_zones_layers_endpoint(self, api_client):
        """GET /api/v1/bionic/organic-zones/layers should return layers and species"""
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/organic-zones/layers")

        assert response.status_code == 200, f"Status {response.status_code}: {response.text}"

        data = response.json()
        assert "layers" in data, "Missing 'layers' in response"
        assert "species" in data, "Missing 'species' in response"

        # Verify species list
        species_list = data.get("species", [])
        assert len(species_list) == 5, f"Expected 5 species, got {len(species_list)}"


# =====================================================================
# ADDITIONAL DATA VALIDATION TESTS
# =====================================================================

class TestSSEEdgeVectorsFormat:
    """Verify edge_vectors format"""

    def test_edge_vectors_have_correct_format(self, api_client):
        """Each edge vector should have start, end, intensity"""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": "moose",
            "resolution": 40,
            "include_vectors": True
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/sse/analyze", json=payload)

        assert response.status_code == 200

        data = response.json()
        edge_vectors = data.get("edge_vectors", [])

        if len(edge_vectors) > 0:
            # Check first vector format
            vec = edge_vectors[0]
            assert "start" in vec, "Edge vector missing 'start'"
            assert "end" in vec, "Edge vector missing 'end'"
            assert "intensity" in vec, "Edge vector missing 'intensity'"

            # Check start/end have lat/lng
            assert "lat" in vec["start"] and "lng" in vec["start"], "start missing lat/lng"
            assert "lat" in vec["end"] and "lng" in vec["end"], "end missing lat/lng"

            # Check intensity is in [0, 1]
            assert 0.0 <= vec["intensity"] <= 1.0, f"intensity out of range: {vec['intensity']}"

    def test_edge_vectors_limited_to_50(self, api_client):
        """Edge vectors should be limited to max 50"""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": "moose",
            "resolution": 60,  # Higher resolution to generate more edges
            "include_vectors": True
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/sse/analyze", json=payload)

        assert response.status_code == 200

        data = response.json()
        edge_vectors = data.get("edge_vectors", [])
        assert len(edge_vectors) <= 50, f"Edge vectors should be <= 50, got {len(edge_vectors)}"


class TestSSEDifferentSpeciesProduceDifferentData:
    """Verify different species produce different data"""

    def test_deer_data_differs_from_moose(self, api_client):
        """Deer analysis should differ from moose"""
        # Get moose data
        moose_payload = {"bounds": BOUNDS_QUEBEC, "species": "moose", "resolution": 40}
        moose_response = api_client.post(f"{BASE_URL}/api/v1/bionic/sse/analyze", json=moose_payload)
        assert moose_response.status_code == 200
        moose_data = moose_response.json()

        # Get deer data
        deer_payload = {"bounds": BOUNDS_QUEBEC, "species": "deer", "resolution": 40}
        deer_response = api_client.post(f"{BASE_URL}/api/v1/bionic/sse/analyze", json=deer_payload)
        assert deer_response.status_code == 200
        deer_data = deer_response.json()

        # Source IDs must differ
        assert moose_data["source_id"] != deer_data["source_id"], "source_id should differ"
        assert moose_data["source_id"] == "SSE_MOOSE"
        assert deer_data["source_id"] == "SSE_DEER"

        # Stats should differ (species profiles are different)
        moose_stats = moose_data.get("stats", {})
        deer_stats = deer_data.get("stats", {})

        # At least one stat should differ significantly
        diffs = []
        for key in ["mean_forest_density", "mean_clearing", "mean_wetland_prob"]:
            if key in moose_stats and key in deer_stats:
                diffs.append(abs(moose_stats[key] - deer_stats[key]) > 0.01)

        assert any(diffs), "Stats should differ between moose and deer"
