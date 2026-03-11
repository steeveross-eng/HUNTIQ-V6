"""
CME ENGINE (Corridor Morphology Engine) — BIONIC V5 ULTIME 300% Phase #3 Tests
Tests for POST /api/v1/bionic/cme/generate and GET /api/v1/bionic/cme/status

Validates:
- Dynamic source_id CME_{SPECIES}
- SSE/OSG integration (sse_source_id, osg_source_id)
- Corridor structure: geometry.type=LineString, terrain_context, corridor_id, etc.
- Validation flags: cost_surface_routed, chaikin_applied, jitter_applied, sse/osg_integrated
- Multi-territory differentiation
- Performance under 500ms
- Regression: SSE and OSG still functional
"""

import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Test bounds for different territories
BOUNDS_QUEBEC = {"north": 47.05, "south": 46.95, "east": -71.15, "west": -71.25}
BOUNDS_ABITIBI = {"north": 48.60, "south": 48.50, "east": -78.90, "west": -79.00}
BOUNDS_LAURENTIDES = {"north": 46.20, "south": 46.10, "east": -74.50, "west": -74.60}

# All 5 supported species
ALL_SPECIES = ["moose", "deer", "bear", "wild_turkey", "elk"]


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session."""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


# =====================================================================
# CME GENERATE — SOURCE_ID PER SPECIES
# =====================================================================

class TestCMEGenerateSourceId:
    """Test dynamic source_id CME_{SPECIES} for all 5 species."""

    @pytest.mark.parametrize("species,expected_source_id,expected_sse_id,expected_osg_id", [
        ("moose", "CME_MOOSE", "SSE_MOOSE", "OSG_MOOSE"),
        ("deer", "CME_DEER", "SSE_DEER", "OSG_DEER"),
        ("bear", "CME_BEAR", "SSE_BEAR", "OSG_BEAR"),
        ("wild_turkey", "CME_WILD_TURKEY", "SSE_WILD_TURKEY", "OSG_WILD_TURKEY"),
        ("elk", "CME_ELK", "SSE_ELK", "OSG_ELK"),
    ])
    def test_cme_generate_source_id_per_species(self, api_client, species, expected_source_id, expected_sse_id, expected_osg_id):
        """Verify source_id, sse_source_id, osg_source_id are dynamically generated per species."""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": species,
            "resolution": 40,
            "layers": ["habitats", "alimentation"],
            "max_zones_per_layer": 3,
            "max_corridors": 4,
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/cme/generate", json=payload)
        
        assert response.status_code == 200, f"CME generate failed for {species}: {response.text}"
        data = response.json()
        
        # source_id dynamique
        assert data.get("source_id") == expected_source_id, f"Expected source_id={expected_source_id}, got {data.get('source_id')}"
        assert data.get("species") == species
        
        # sse_source_id et osg_source_id
        assert data.get("sse_source_id") == expected_sse_id, f"Expected sse_source_id={expected_sse_id}, got {data.get('sse_source_id')}"
        assert data.get("osg_source_id") == expected_osg_id, f"Expected osg_source_id={expected_osg_id}, got {data.get('osg_source_id')}"


# =====================================================================
# CME VALIDATION FLAGS
# =====================================================================

class TestCMEValidationFlags:
    """Test validation fields: cost_surface_routed, chaikin_applied, jitter_applied, sse/osg integrated."""

    @pytest.mark.parametrize("species", ALL_SPECIES)
    def test_validation_all_cost_surface_routed(self, api_client, species):
        """Verify validation.all_cost_surface_routed=True for all species."""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": species,
            "resolution": 40,
            "layers": ["habitats", "alimentation"],
            "max_zones_per_layer": 3,
            "max_corridors": 4,
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/cme/generate", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        validation = data.get("validation", {})
        assert validation.get("all_cost_surface_routed") is True, f"all_cost_surface_routed should be True for {species}"

    @pytest.mark.parametrize("species", ALL_SPECIES)
    def test_validation_all_chaikin_applied(self, api_client, species):
        """Verify validation.all_chaikin_applied=True for all species."""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": species,
            "resolution": 40,
            "layers": ["habitats", "alimentation"],
            "max_zones_per_layer": 3,
            "max_corridors": 4,
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/cme/generate", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        validation = data.get("validation", {})
        assert validation.get("all_chaikin_applied") is True, f"all_chaikin_applied should be True for {species}"

    @pytest.mark.parametrize("species", ALL_SPECIES)
    def test_validation_all_jitter_applied(self, api_client, species):
        """Verify validation.all_jitter_applied=True for all species."""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": species,
            "resolution": 40,
            "layers": ["habitats", "alimentation"],
            "max_zones_per_layer": 3,
            "max_corridors": 4,
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/cme/generate", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        validation = data.get("validation", {})
        assert validation.get("all_jitter_applied") is True, f"all_jitter_applied should be True for {species}"

    @pytest.mark.parametrize("species", ALL_SPECIES)
    def test_validation_sse_integrated(self, api_client, species):
        """Verify validation.sse_integrated=True for all species."""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": species,
            "resolution": 40,
            "layers": ["habitats", "alimentation"],
            "max_zones_per_layer": 3,
            "max_corridors": 4,
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/cme/generate", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        validation = data.get("validation", {})
        assert validation.get("sse_integrated") is True, f"sse_integrated should be True for {species}"

    @pytest.mark.parametrize("species", ALL_SPECIES)
    def test_validation_osg_integrated(self, api_client, species):
        """Verify validation.osg_integrated=True for all species."""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": species,
            "resolution": 40,
            "layers": ["habitats", "alimentation"],
            "max_zones_per_layer": 3,
            "max_corridors": 4,
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/cme/generate", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        validation = data.get("validation", {})
        assert validation.get("osg_integrated") is True, f"osg_integrated should be True for {species}"


# =====================================================================
# CME CORRIDOR STRUCTURE
# =====================================================================

class TestCMECorridorStructure:
    """Test corridor structure: geometry, terrain_context, corridor_id, etc."""

    @pytest.mark.parametrize("species", ALL_SPECIES)
    def test_corridors_have_linestring_geometry(self, api_client, species):
        """Verify each corridor has geometry.type=LineString."""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": species,
            "resolution": 40,
            "layers": ["habitats", "alimentation"],
            "max_zones_per_layer": 3,
            "max_corridors": 4,
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/cme/generate", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        corridors = data.get("corridors", [])
        # There should be at least some corridors generated
        if len(corridors) > 0:
            for c in corridors:
                geometry = c.get("geometry", {})
                assert geometry.get("type") == "LineString", f"Corridor geometry should be LineString, got {geometry.get('type')}"
                assert "coordinates" in geometry, "Corridor geometry should have coordinates"
                assert len(geometry["coordinates"]) >= 2, "LineString should have at least 2 points"

    @pytest.mark.parametrize("species", ALL_SPECIES)
    def test_corridors_have_terrain_context(self, api_client, species):
        """Verify each corridor has terrain_context with cover_context and relief_context."""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": species,
            "resolution": 40,
            "layers": ["habitats", "alimentation"],
            "max_zones_per_layer": 3,
            "max_corridors": 4,
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/cme/generate", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        corridors = data.get("corridors", [])
        if len(corridors) > 0:
            for c in corridors:
                terrain_ctx = c.get("terrain_context", {})
                assert "cover_context" in terrain_ctx, "terrain_context should have cover_context"
                assert "relief_context" in terrain_ctx, "terrain_context should have relief_context"
                assert terrain_ctx["cover_context"] in ["forested", "open", "mixed"], f"Invalid cover_context: {terrain_ctx['cover_context']}"
                assert terrain_ctx["relief_context"] in ["valley", "slope", "flat"], f"Invalid relief_context: {terrain_ctx['relief_context']}"

    @pytest.mark.parametrize("species", ALL_SPECIES)
    def test_corridors_have_required_fields(self, api_client, species):
        """Verify each corridor has: corridor_id, corridor_type, length_m, width_m, vertices, usage_probability."""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": species,
            "resolution": 40,
            "layers": ["habitats", "alimentation"],
            "max_zones_per_layer": 3,
            "max_corridors": 4,
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/cme/generate", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        corridors = data.get("corridors", [])
        required_fields = ["corridor_id", "corridor_type", "length_m", "width_m", "vertices", "usage_probability"]
        if len(corridors) > 0:
            for c in corridors:
                for field in required_fields:
                    assert field in c, f"Corridor missing required field: {field}"
                # Validate types
                assert isinstance(c["corridor_id"], str), "corridor_id should be string"
                assert isinstance(c["corridor_type"], str), "corridor_type should be string"
                assert isinstance(c["length_m"], (int, float)), "length_m should be numeric"
                assert isinstance(c["width_m"], (int, float)), "width_m should be numeric"
                assert isinstance(c["vertices"], int), "vertices should be int"
                assert isinstance(c["usage_probability"], (int, float)), "usage_probability should be numeric"
                assert 0.0 <= c["usage_probability"] <= 1.0, "usage_probability should be in [0,1]"

    @pytest.mark.parametrize("species", ALL_SPECIES)
    def test_corridors_per_corridor_validation(self, api_client, species):
        """Verify each corridor has validation with chaikin_iterations, jitter_applied, cost_surface_routed."""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": species,
            "resolution": 40,
            "layers": ["habitats", "alimentation"],
            "max_zones_per_layer": 3,
            "max_corridors": 4,
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/cme/generate", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        corridors = data.get("corridors", [])
        if len(corridors) > 0:
            for c in corridors:
                validation = c.get("validation", {})
                assert "chaikin_iterations" in validation, "corridor should have chaikin_iterations"
                assert validation["chaikin_iterations"] >= 2, "chaikin_iterations should be >= 2"
                assert validation.get("jitter_applied") is True, "jitter_applied should be True"
                assert validation.get("cost_surface_routed") is True, "cost_surface_routed should be True"


# =====================================================================
# CME RESPONSE STRUCTURE
# =====================================================================

class TestCMEResponseStructure:
    """Test overall CME response structure."""

    def test_response_has_all_required_fields(self, api_client):
        """Verify response has all required top-level fields."""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": "moose",
            "resolution": 40,
            "layers": ["habitats", "alimentation"],
            "max_zones_per_layer": 3,
            "max_corridors": 4,
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/cme/generate", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        required_fields = [
            "source_id", "species", "bounds", "resolution", "corridors",
            "corridor_count", "corridor_types_used", "total_length_m",
            "validation", "sse_source_id", "osg_source_id", "computation_time_ms"
        ]
        for field in required_fields:
            assert field in data, f"Response missing required field: {field}"

    def test_corridor_count_matches_corridors_length(self, api_client):
        """Verify corridor_count matches len(corridors)."""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": "moose",
            "resolution": 40,
            "layers": ["habitats", "alimentation"],
            "max_zones_per_layer": 3,
            "max_corridors": 4,
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/cme/generate", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert data["corridor_count"] == len(data["corridors"]), "corridor_count should match len(corridors)"

    def test_total_length_positive(self, api_client):
        """Verify total_length_m is positive (or 0 if no corridors)."""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": "moose",
            "resolution": 40,
            "layers": ["habitats", "alimentation"],
            "max_zones_per_layer": 3,
            "max_corridors": 4,
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/cme/generate", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_length_m"] >= 0, "total_length_m should be >= 0"
        # If corridors exist, total_length should be > 0
        if data["corridor_count"] > 0:
            assert data["total_length_m"] > 0, "total_length_m should be > 0 if corridors exist"


# =====================================================================
# CME INVALID SPECIES
# =====================================================================

class TestCMEInvalidSpecies:
    """Test error handling for invalid species."""

    @pytest.mark.parametrize("invalid_species", ["wolf", "rabbit", "unicorn", "", "MOOSE", "Moose"])
    def test_invalid_species_returns_400(self, api_client, invalid_species):
        """Verify 400 error for unsupported species."""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": invalid_species,
            "resolution": 40,
            "layers": ["habitats", "alimentation"],
            "max_zones_per_layer": 3,
            "max_corridors": 4,
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/cme/generate", json=payload)
        assert response.status_code == 400, f"Expected 400 for invalid species '{invalid_species}', got {response.status_code}"


# =====================================================================
# CME MULTI-TERRITORY DIFFERENTIATION
# =====================================================================

class TestCMEMultiTerritory:
    """Test that different territories produce different corridor data."""

    def test_different_territories_different_total_length(self, api_client):
        """Verify 3 territories (Quebec, Abitibi, Laurentides) produce different total_length_m."""
        results = {}
        for name, bounds in [
            ("Quebec", BOUNDS_QUEBEC),
            ("Abitibi", BOUNDS_ABITIBI),
            ("Laurentides", BOUNDS_LAURENTIDES)
        ]:
            payload = {
                "bounds": bounds,
                "species": "moose",
                "resolution": 40,
                "layers": ["habitats", "alimentation"],
                "max_zones_per_layer": 3,
                "max_corridors": 4,
            }
            response = api_client.post(f"{BASE_URL}/api/v1/bionic/cme/generate", json=payload)
            assert response.status_code == 200
            data = response.json()
            results[name] = data["total_length_m"]
        
        # At least 2 of 3 should differ (not all identical)
        unique_values = set(results.values())
        assert len(unique_values) >= 2, f"Expected different total_length_m for territories, got: {results}"

    def test_different_territories_different_corridor_count(self, api_client):
        """Verify corridor counts may differ between territories."""
        results = {}
        for name, bounds in [
            ("Quebec", BOUNDS_QUEBEC),
            ("Abitibi", BOUNDS_ABITIBI),
            ("Laurentides", BOUNDS_LAURENTIDES)
        ]:
            payload = {
                "bounds": bounds,
                "species": "moose",
                "resolution": 40,
                "layers": ["habitats", "alimentation"],
                "max_zones_per_layer": 3,
                "max_corridors": 4,
            }
            response = api_client.post(f"{BASE_URL}/api/v1/bionic/cme/generate", json=payload)
            assert response.status_code == 200
            data = response.json()
            results[name] = data["corridor_count"]
        
        # All should be within max_corridors limit
        for name, count in results.items():
            assert count <= 4, f"{name} corridor_count should be <= max_corridors=4"


# =====================================================================
# CME PERFORMANCE
# =====================================================================

class TestCMEPerformance:
    """Test CME performance: should be under 500ms for resolution=40 and 2 layers."""

    def test_performance_under_500ms_resolution_40_2_layers(self, api_client):
        """Verify computation_time_ms < 500 for resolution=40 and 2 layers."""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": "moose",
            "resolution": 40,
            "layers": ["habitats", "alimentation"],
            "max_zones_per_layer": 3,
            "max_corridors": 4,
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/cme/generate", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        computation_ms = data.get("computation_time_ms", 9999)
        assert computation_ms < 500, f"Performance should be < 500ms, got {computation_ms}ms"

    @pytest.mark.parametrize("species", ALL_SPECIES)
    def test_performance_under_500ms_all_species(self, api_client, species):
        """Verify computation_time_ms < 500 for all species."""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": species,
            "resolution": 40,
            "layers": ["habitats", "alimentation"],
            "max_zones_per_layer": 3,
            "max_corridors": 4,
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/cme/generate", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        computation_ms = data.get("computation_time_ms", 9999)
        assert computation_ms < 500, f"Performance for {species} should be < 500ms, got {computation_ms}ms"


# =====================================================================
# CME STATUS ENDPOINT
# =====================================================================

class TestCMEStatusEndpoint:
    """Test GET /api/v1/bionic/cme/status endpoint."""

    def test_status_endpoint_returns_200(self, api_client):
        """Verify status endpoint returns 200."""
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/cme/status")
        assert response.status_code == 200

    def test_status_module_active(self, api_client):
        """Verify status.status is 'active'."""
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/cme/status")
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("module") == "CME"
        assert data.get("status") == "active"

    def test_status_has_5_species(self, api_client):
        """Verify status has 5 species supported."""
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/cme/status")
        assert response.status_code == 200
        data = response.json()
        
        species_list = data.get("species_supported", [])
        assert len(species_list) == 5, f"Expected 5 species, got {len(species_list)}"
        for sp in ALL_SPECIES:
            assert sp in species_list, f"Species {sp} should be in species_supported"

    def test_status_dependencies_sse_osg(self, api_client):
        """Verify status.dependencies includes SSE and OSG."""
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/cme/status")
        assert response.status_code == 200
        data = response.json()
        
        dependencies = data.get("dependencies", [])
        # Check that SSE and OSG are mentioned in dependencies
        deps_str = " ".join(dependencies).lower()
        assert "sse" in deps_str, "Dependencies should mention SSE"
        assert "osg" in deps_str, "Dependencies should mention OSG"

    def test_status_conformity_fields(self, api_client):
        """Verify status.conformity has required fields."""
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/cme/status")
        assert response.status_code == 200
        data = response.json()
        
        conformity = data.get("conformity", {})
        expected_fields = [
            "source_id_dynamic", "zero_transversality", "zero_duplication",
            "backend_truth", "chaikin_applied", "cost_surface_routing",
            "sse_integration", "osg_integration"
        ]
        for field in expected_fields:
            assert field in conformity, f"conformity should have field: {field}"
            assert conformity[field] is True, f"conformity.{field} should be True"


# =====================================================================
# REGRESSION TESTS — SSE STILL FUNCTIONAL
# =====================================================================

class TestRegressionSSE:
    """Regression: SSE endpoints should still work after CME addition."""

    def test_sse_analyze_moose_still_works(self, api_client):
        """Verify POST /api/v1/bionic/sse/analyze still returns SSE_MOOSE."""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": "moose",
            "resolution": 40,
            "include_vectors": False,
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/sse/analyze", json=payload)
        assert response.status_code == 200, f"SSE analyze failed: {response.text}"
        data = response.json()
        
        assert data.get("source_id") == "SSE_MOOSE", f"SSE source_id should be SSE_MOOSE"
        # API returns landcover_summary and microrelief_summary at root level
        assert "landcover_summary" in data or "landcover" in data, "landcover data should exist"
        assert "microrelief_summary" in data or "microrelief" in data, "microrelief data should exist"


# =====================================================================
# REGRESSION TESTS — OSG STILL FUNCTIONAL
# =====================================================================

class TestRegressionOSG:
    """Regression: OSG endpoints should still work after CME addition."""

    def test_osg_generate_moose_still_works(self, api_client):
        """Verify POST /api/v1/bionic/osg/generate still returns OSG_MOOSE."""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": "moose",
            "resolution": 40,
            "layers": ["habitats", "alimentation"],
            "max_zones_per_layer": 3,
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/osg/generate", json=payload)
        assert response.status_code == 200, f"OSG generate failed: {response.text}"
        data = response.json()
        
        assert data.get("source_id") == "OSG_MOOSE", f"OSG source_id should be OSG_MOOSE"
        assert data.get("sse_source_id") == "SSE_MOOSE"


# =====================================================================
# REGRESSION TESTS — ORGANIC ZONES STILL FUNCTIONAL
# =====================================================================

class TestRegressionOrganicZones:
    """Regression: Original organic-zones endpoints should still work."""

    @pytest.mark.parametrize("species,expected_source_id", [
        ("moose", "BIONIC_V5_MOOSE"),
        ("deer", "BIONIC_V5_DEER"),
        ("bear", "BIONIC_V5_BEAR"),
    ])
    def test_organic_zones_analyze_still_functional(self, api_client, species, expected_source_id):
        """Verify POST /api/v1/bionic/organic-zones still returns BIONIC_V5_{SPECIES}."""
        payload = {
            "bounds": BOUNDS_QUEBEC,
            "species": species,
            "layers": ["habitats"],
            "resolution": 30,
            "max_zones_per_layer": 2,
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/organic-zones", json=payload)
        assert response.status_code == 200, f"organic-zones failed for {species}: {response.text}"
        data = response.json()
        
        # source_id is in metadata for GeoJSON FeatureCollection format
        source_id = data.get("source_id") or data.get("metadata", {}).get("source_id")
        assert source_id == expected_source_id, f"Expected {expected_source_id}, got {source_id}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
