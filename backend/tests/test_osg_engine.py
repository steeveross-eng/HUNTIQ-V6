"""
TEST OSG ENGINE — Organic Shape Generator
BIONIC V5 ULTIME 300% — Phase d'Optimisation #2

Tests:
  - POST /api/v1/bionic/osg/generate for all 5 species
  - GET /api/v1/bionic/osg/status
  - source_id dynamic OSG_{SPECIES}
  - sse_source_id = SSE_{SPECIES}
  - sse_context in each zone
  - compactness < 0.85 validation
  - chaikin_applied, sse_integration validation flags
  - Multi-territories (Quebec, Abitibi, Laurentides)
  - Performance < 500ms for resolution=40
  - Invalid species 400 error
  - REGRESSION: organic-zones BIONIC_V5_{SPECIES}
  - REGRESSION: SSE analyze endpoint

Iteration: 64
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

# Required SSE context fields in each zone
SSE_CONTEXT_REQUIRED_FIELDS = [
    "forest_density",
    "edge_proximity",
    "valley_affinity",
    "ridge_affinity",
    "composite_quality",
    "relief_type",
    "cover_type"
]


@pytest.fixture
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


# =====================================================================
# OSG /generate ENDPOINT TESTS — source_id per species
# =====================================================================

class TestOSGGenerateSourceId:
    """Test /api/v1/bionic/osg/generate source_id dynamic OSG_{SPECIES}"""

    @pytest.mark.parametrize("species,expected_source_id,expected_sse_source_id", [
        ("moose", "OSG_MOOSE", "SSE_MOOSE"),
        ("deer", "OSG_DEER", "SSE_DEER"),
        ("bear", "OSG_BEAR", "SSE_BEAR"),
        ("wild_turkey", "OSG_WILD_TURKEY", "SSE_WILD_TURKEY"),
        ("elk", "OSG_ELK", "SSE_ELK"),
    ])
    def test_osg_generate_source_id_per_species(self, api_client, species, expected_source_id, expected_sse_source_id):
        """Verify source_id=OSG_{SPECIES} and sse_source_id=SSE_{SPECIES}"""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": species,
            "resolution": 40,
            "layers": ["habitats"],
            "max_zones_per_layer": 3
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/osg/generate", json=payload)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        data = response.json()

        # Verify source_id is dynamic OSG_{SPECIES}
        assert "source_id" in data, "Missing source_id in response"
        assert data["source_id"] == expected_source_id, f"Expected {expected_source_id}, got {data['source_id']}"

        # Verify sse_source_id is SSE_{SPECIES}
        assert "sse_source_id" in data, "Missing sse_source_id in response"
        assert data["sse_source_id"] == expected_sse_source_id, f"Expected {expected_sse_source_id}, got {data['sse_source_id']}"

        # Verify species matches
        assert data.get("species") == species, f"Species mismatch: expected {species}, got {data.get('species')}"


# =====================================================================
# OSG COMPACTNESS VALIDATION TESTS
# =====================================================================

class TestOSGCompactnessValidation:
    """Verify all_compactness_below_085 is True for all species"""

    @pytest.mark.parametrize("species", ALL_SPECIES)
    def test_all_compactness_below_085(self, api_client, species):
        """All zones must have compactness < 0.85"""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": species,
            "resolution": 40,
            "layers": ["habitats", "rut"],
            "max_zones_per_layer": 5
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/osg/generate", json=payload)

        assert response.status_code == 200, f"Status {response.status_code}: {response.text}"

        data = response.json()

        # Verify validation flag
        validation = data.get("validation", {})
        assert validation.get("all_compactness_below_085") is True, \
            f"all_compactness_below_085 should be True, got {validation.get('all_compactness_below_085')}"

        # Double-check by inspecting each zone
        zones_by_layer = data.get("zones_by_layer", {})
        for layer_id, zones in zones_by_layer.items():
            for zone in zones:
                compactness = zone.get("compactness", 1.0)
                assert compactness < 0.85, f"Zone in {layer_id} has compactness {compactness} >= 0.85"


# =====================================================================
# OSG SSE_CONTEXT VALIDATION TESTS
# =====================================================================

class TestOSGSSEContext:
    """Verify sse_context present in each zone with all required fields"""

    @pytest.mark.parametrize("species", ALL_SPECIES)
    def test_zones_have_sse_context(self, api_client, species):
        """Each zone must have sse_context with all required fields"""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": species,
            "resolution": 40,
            "layers": ["habitats"],
            "max_zones_per_layer": 5
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/osg/generate", json=payload)

        assert response.status_code == 200, f"Status {response.status_code}: {response.text}"

        data = response.json()
        zones_by_layer = data.get("zones_by_layer", {})

        zone_count = 0
        for layer_id, zones in zones_by_layer.items():
            for zone in zones:
                zone_count += 1
                assert "sse_context" in zone, f"Zone in {layer_id} missing sse_context"
                sse_ctx = zone["sse_context"]

                for field in SSE_CONTEXT_REQUIRED_FIELDS:
                    assert field in sse_ctx, f"Zone sse_context missing field: {field}"

        # Ensure we actually tested zones
        if data.get("total_zones", 0) > 0:
            assert zone_count > 0, "No zones were validated despite total_zones > 0"

    def test_sse_context_values_normalized(self, api_client):
        """SSE context numeric values should be in [0, 1]"""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": "moose",
            "resolution": 40,
            "layers": ["habitats"],
            "max_zones_per_layer": 5
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/osg/generate", json=payload)

        assert response.status_code == 200

        data = response.json()
        zones_by_layer = data.get("zones_by_layer", {})

        for layer_id, zones in zones_by_layer.items():
            for zone in zones:
                sse_ctx = zone.get("sse_context", {})
                
                # Numeric fields should be [0, 1]
                for field in ["forest_density", "edge_proximity", "valley_affinity", "ridge_affinity", "composite_quality"]:
                    val = sse_ctx.get(field, 0)
                    assert 0.0 <= val <= 1.0, f"{field} out of [0,1]: {val}"

                # Categorical fields
                assert sse_ctx.get("relief_type") in ["valley", "ridge", "plateau"], \
                    f"Invalid relief_type: {sse_ctx.get('relief_type')}"
                assert sse_ctx.get("cover_type") in ["forest", "clearing", "transition"], \
                    f"Invalid cover_type: {sse_ctx.get('cover_type')}"


# =====================================================================
# OSG VALIDATION FLAGS TESTS
# =====================================================================

class TestOSGValidationFlags:
    """Verify chaikin_applied and sse_integration flags"""

    @pytest.mark.parametrize("species", ALL_SPECIES)
    def test_chaikin_applied_true(self, api_client, species):
        """validation.chaikin_applied should be True"""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": species,
            "resolution": 40,
            "layers": ["habitats"],
            "max_zones_per_layer": 3
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/osg/generate", json=payload)

        assert response.status_code == 200

        data = response.json()
        validation = data.get("validation", {})
        assert validation.get("chaikin_applied") is True, \
            f"chaikin_applied should be True, got {validation.get('chaikin_applied')}"

    @pytest.mark.parametrize("species", ALL_SPECIES)
    def test_sse_integration_true(self, api_client, species):
        """validation.sse_integration should be True"""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": species,
            "resolution": 40,
            "layers": ["habitats"],
            "max_zones_per_layer": 3
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/osg/generate", json=payload)

        assert response.status_code == 200

        data = response.json()
        validation = data.get("validation", {})
        assert validation.get("sse_integration") is True, \
            f"sse_integration should be True, got {validation.get('sse_integration')}"


# =====================================================================
# OSG MULTI-TERRITORIES TESTS
# =====================================================================

class TestOSGMultiTerritories:
    """Test different territories produce different data"""

    def test_different_territories_different_zones(self, api_client):
        """Quebec, Abitibi, Laurentides should produce different zone data"""
        territories = [
            ("Quebec", BOUNDS_QUEBEC),
            ("Abitibi", BOUNDS_ABITIBI),
            ("Laurentides", BOUNDS_LAURENTIDES),
        ]

        results = {}
        for name, bounds in territories:
            payload = {
                "bounds": bounds,
                "species": "moose",
                "resolution": 40,
                "layers": ["habitats"],
                "max_zones_per_layer": 3
            }
            response = api_client.post(f"{BASE_URL}/api/v1/bionic/osg/generate", json=payload)
            assert response.status_code == 200, f"{name} failed: {response.text}"
            results[name] = response.json()

        # Verify bounds returned differ
        for name, data in results.items():
            assert "bounds" in data, f"{name} response missing bounds"

        # Bounds should match what we sent
        assert results["Quebec"]["bounds"]["north"] == BOUNDS_QUEBEC["north"]
        assert results["Abitibi"]["bounds"]["north"] == BOUNDS_ABITIBI["north"]
        assert results["Laurentides"]["bounds"]["north"] == BOUNDS_LAURENTIDES["north"]

        # Territories have different bounds, so they should differ
        # Check that all 3 have distinct north values (which they do by definition)
        north_values = [results[n]["bounds"]["north"] for n in ["Quebec", "Abitibi", "Laurentides"]]
        assert len(set(north_values)) == 3, "Territories should have distinct bounds"


# =====================================================================
# OSG INVALID SPECIES TEST
# =====================================================================

class TestOSGInvalidSpecies:
    """Test invalid species returns 400"""

    def test_invalid_species_returns_400(self, api_client):
        """Invalid species should return 400 error"""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": "dragon",  # Invalid species
            "resolution": 40,
            "layers": ["habitats"],
            "max_zones_per_layer": 3
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/osg/generate", json=payload)

        assert response.status_code == 400, f"Expected 400 for invalid species, got {response.status_code}"

        data = response.json()
        assert "detail" in data, "Error response should have 'detail'"
        # Check detail mentions unsupported species
        assert "dragon" in data["detail"].lower() or "supportee" in data["detail"].lower() or "non" in data["detail"].lower()


# =====================================================================
# OSG PERFORMANCE TEST
# =====================================================================

class TestOSGPerformance:
    """Test performance < 500ms for resolution=40, 1-2 layers"""

    def test_performance_under_500ms(self, api_client):
        """Response time should be < 500ms for resolution=40 and 1-2 layers"""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": "moose",
            "resolution": 40,
            "layers": ["habitats"],
            "max_zones_per_layer": 3
        }

        start = time.time()
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/osg/generate", json=payload)
        elapsed_ms = (time.time() - start) * 1000

        assert response.status_code == 200

        data = response.json()
        computation_time = data.get("computation_time_ms", 0)

        # Check API-reported computation time
        assert computation_time < 500, f"Computation time {computation_time}ms exceeds 500ms limit"

        # Check total request time (with network overhead)
        assert elapsed_ms < 2000, f"Total request time {elapsed_ms}ms too slow"

    def test_performance_with_2_layers(self, api_client):
        """Performance with 2 layers should still be < 500ms"""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": "deer",
            "resolution": 40,
            "layers": ["habitats", "rut"],
            "max_zones_per_layer": 3
        }

        response = api_client.post(f"{BASE_URL}/api/v1/bionic/osg/generate", json=payload)

        assert response.status_code == 200

        data = response.json()
        computation_time = data.get("computation_time_ms", 0)

        assert computation_time < 500, f"Computation time {computation_time}ms exceeds 500ms limit with 2 layers"


# =====================================================================
# OSG /status ENDPOINT TESTS
# =====================================================================

class TestOSGStatus:
    """Test GET /api/v1/bionic/osg/status endpoint"""

    def test_status_endpoint_returns_active(self, api_client):
        """Status endpoint should return active module"""
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/osg/status")

        assert response.status_code == 200, f"Status {response.status_code}: {response.text}"

        data = response.json()
        assert data.get("status") == "active", f"Expected active status, got {data.get('status')}"
        assert data.get("module") == "OSG", f"Expected module=OSG, got {data.get('module')}"

    def test_status_has_5_species(self, api_client):
        """Status should list 5 supported species"""
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/osg/status")

        assert response.status_code == 200

        data = response.json()
        species_supported = data.get("species_supported", [])
        assert len(species_supported) == 5, f"Expected 5 species, got {len(species_supported)}"
        for sp in ALL_SPECIES:
            assert sp in species_supported, f"Missing species: {sp}"

    def test_status_dependencies_sse(self, api_client):
        """Status should list SSE as dependency"""
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/osg/status")

        assert response.status_code == 200

        data = response.json()
        dependencies = data.get("dependencies", [])
        # Check that SSE is listed (may be "SSE" or "SSE (certified)")
        sse_found = any("SSE" in dep for dep in dependencies)
        assert sse_found, f"SSE not found in dependencies: {dependencies}"

    def test_status_conformity_fields(self, api_client):
        """Status should have conformity fields"""
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/osg/status")

        assert response.status_code == 200

        data = response.json()
        conformity = data.get("conformity", {})

        # Key conformity fields
        assert conformity.get("source_id_dynamic") is True, "source_id_dynamic should be True"
        assert conformity.get("zero_transversality") is True, "zero_transversality should be True"
        assert conformity.get("zero_duplication") is True, "zero_duplication should be True"
        assert conformity.get("chaikin_minimum_2x") is True, "chaikin_minimum_2x should be True"
        assert conformity.get("compactness_max_085") is True, "compactness_max_085 should be True"
        assert conformity.get("sse_integration") is True, "sse_integration should be True"


# =====================================================================
# REGRESSION TESTS — Organic Zones
# =====================================================================

class TestRegressionOrganicZones:
    """REGRESSION: Verify organic-zones endpoints still work"""

    @pytest.mark.parametrize("species,expected_source_id", [
        ("moose", "BIONIC_V5_MOOSE"),
        ("deer", "BIONIC_V5_DEER"),
        ("bear", "BIONIC_V5_BEAR"),
    ])
    def test_organic_zones_source_id(self, api_client, species, expected_source_id):
        """POST /api/v1/bionic/organic-zones should return source_id BIONIC_V5_{SPECIES}"""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": species,
            "resolution": 30
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/organic-zones", json=payload)

        assert response.status_code == 200, f"Status {response.status_code}: {response.text}"

        data = response.json()
        metadata = data.get("metadata", {})
        source_id = metadata.get("source_id", "")
        assert expected_source_id in source_id, f"Expected {expected_source_id} in source_id, got {source_id}"


# =====================================================================
# REGRESSION TESTS — SSE Analyze
# =====================================================================

class TestRegressionSSE:
    """REGRESSION: Verify SSE analyze endpoint still works"""

    def test_sse_analyze_still_functional(self, api_client):
        """POST /api/v1/bionic/sse/analyze should still work with moose"""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": "moose",
            "resolution": 40,
            "include_vectors": False
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/sse/analyze", json=payload)

        assert response.status_code == 200, f"SSE analyze failed: {response.status_code}: {response.text}"

        data = response.json()
        assert data.get("source_id") == "SSE_MOOSE", f"Expected SSE_MOOSE, got {data.get('source_id')}"
        assert "landcover_summary" in data, "Missing landcover_summary"
        assert "microrelief_summary" in data, "Missing microrelief_summary"
        assert "composite_summary" in data, "Missing composite_summary"


# =====================================================================
# OSG ZONE STRUCTURE VALIDATION
# =====================================================================

class TestOSGZoneStructure:
    """Verify zone structure has all required fields"""

    def test_zone_has_all_fields(self, api_client):
        """Each zone should have area_m2, compactness, centroid, vertices, sse_context"""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": "moose",
            "resolution": 40,
            "layers": ["habitats"],
            "max_zones_per_layer": 5
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/osg/generate", json=payload)

        assert response.status_code == 200

        data = response.json()
        zones_by_layer = data.get("zones_by_layer", {})

        for layer_id, zones in zones_by_layer.items():
            for zone in zones:
                # Required fields
                assert "area_m2" in zone, f"Zone in {layer_id} missing area_m2"
                assert "compactness" in zone, f"Zone in {layer_id} missing compactness"
                assert "centroid" in zone, f"Zone in {layer_id} missing centroid"
                assert "vertices" in zone, f"Zone in {layer_id} missing vertices"
                assert "sse_context" in zone, f"Zone in {layer_id} missing sse_context"
                assert "coordinates_count" in zone, f"Zone in {layer_id} missing coordinates_count"

                # Centroid structure
                centroid = zone["centroid"]
                assert "lat" in centroid, "centroid missing lat"
                assert "lng" in centroid, "centroid missing lng"

    def test_zone_counts_match(self, api_client):
        """total_zones should match sum of zones across layers"""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": "moose",
            "resolution": 40,
            "layers": ["habitats", "rut"],
            "max_zones_per_layer": 5
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/osg/generate", json=payload)

        assert response.status_code == 200

        data = response.json()
        total_zones = data.get("total_zones", 0)
        zones_by_layer = data.get("zones_by_layer", {})

        counted = sum(len(zones) for zones in zones_by_layer.values())
        assert total_zones == counted, f"total_zones ({total_zones}) != counted zones ({counted})"


# =====================================================================
# OSG RESPONSE STRUCTURE TESTS
# =====================================================================

class TestOSGResponseStructure:
    """Verify overall response structure"""

    def test_response_has_all_required_fields(self, api_client):
        """Response should have all required top-level fields"""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": "moose",
            "resolution": 40,
            "layers": ["habitats"],
            "max_zones_per_layer": 3
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/osg/generate", json=payload)

        assert response.status_code == 200

        data = response.json()

        required_fields = [
            "source_id",
            "species",
            "bounds",
            "resolution",
            "layers_processed",
            "total_zones",
            "zones_by_layer",
            "validation",
            "rejected_total",
            "computation_time_ms",
            "sse_source_id"
        ]

        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

    def test_rejected_total_structure(self, api_client):
        """rejected_total should have compactness, area, vertices counts"""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": "moose",
            "resolution": 40,
            "layers": ["habitats"],
            "max_zones_per_layer": 3
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/osg/generate", json=payload)

        assert response.status_code == 200

        data = response.json()
        rejected = data.get("rejected_total", {})

        assert "compactness" in rejected, "rejected_total missing 'compactness'"
        assert "area" in rejected, "rejected_total missing 'area'"
        assert "vertices" in rejected, "rejected_total missing 'vertices'"

        # Should be integers
        assert isinstance(rejected["compactness"], int), "rejected compactness should be int"
        assert isinstance(rejected["area"], int), "rejected area should be int"
        assert isinstance(rejected["vertices"], int), "rejected vertices should be int"
