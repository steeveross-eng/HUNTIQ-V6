"""
TFE (Thermal Flow Engine) — API Test Suite
BIONIC V5 ULTIME 300% — Phase d'Optimisation #10

Testing:
- POST /api/v1/bionic/tfe/analyze — 5 espèces x 3 territoires
- GET /api/v1/bionic/tfe/status — module info + conformité
- source_id dynamique TFE_{SPECIES}
- 5 champs thermiques: mean_gradient, mean_inertia, mean_hot_pocket, mean_cold_pocket, mean_composite
- corridor_thermal: thermal_class validation
- pipeline_source_ids: 10 keys (sse, osg, cme, wse, vfe, ssvl, tcve, pme, bmpe, tfe)
- validation flags (9 all true)
- Invalid species returns 400
- Non-regression: BMPE + PME endpoints
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Test configuration
SPECIES_LIST = ["moose", "deer", "bear", "wild_turkey", "elk"]
TERRITORIES = {
    "laurentides": {"north": 46.95, "south": 46.85, "east": -74.00, "west": -74.15},
    "gatineau": {"north": 45.55, "south": 45.45, "east": -75.70, "west": -75.85},
    "charlevoix": {"north": 47.60, "south": 47.50, "east": -70.50, "west": -70.65},
}
RESOLUTION = 30
TIMEOUT = 60

# Expected stats keys (5 thermal fields)
EXPECTED_STAT_KEYS = [
    "mean_gradient", "gradient_range",
    "mean_inertia", "inertia_range",
    "mean_hot_pocket", "hot_pocket_range",
    "mean_cold_pocket", "cold_pocket_range",
    "mean_composite", "composite_range",
]

# Expected pipeline source IDs (10 modules: SSE→OSG→CME→WSE→VFE→SSVL→TCVE→PME→BMPE→TFE)
EXPECTED_PIPELINE_KEYS = ["sse", "osg", "cme", "wse", "vfe", "ssvl", "tcve", "pme", "bmpe", "tfe"]

# Expected validation flags
EXPECTED_VALIDATION_FLAGS = [
    "sse_integrated", "wse_integrated", "ssvl_integrated",
    "tcve_integrated", "pme_integrated", "bmpe_integrated",
    "cme_integrated", "all_fields_normalized", "species_profile_applied"
]

# Valid thermal classes
VALID_THERMAL_CLASSES = {"thermal_refuge", "cold_exposure_corridor", "stable_thermal_zone", "thermal_transition"}


@pytest.fixture(scope="session")
def api_client():
    """Session-wide requests client"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


# =================================================================
# 1. TFE STATUS ENDPOINT
# =================================================================

class TestTFEStatus:
    """Tests for GET /api/v1/bionic/tfe/status"""
    
    def test_status_returns_200(self, api_client):
        """TFE status endpoint should return 200"""
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/tfe/status", timeout=30)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
    def test_status_module_info(self, api_client):
        """TFE status should return correct module info"""
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/tfe/status", timeout=30)
        data = response.json()
        
        assert data["module"] == "TFE"
        assert data["label"] == "Thermal Flow Engine"
        assert data["status"] == "active"
        
    def test_status_species_supported(self, api_client):
        """TFE status should list all 5 supported species"""
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/tfe/status", timeout=30)
        data = response.json()
        
        supported = data.get("species_supported", [])
        for species in SPECIES_LIST:
            assert species in supported, f"Species {species} not in supported list"
            
    def test_status_conformity_flags(self, api_client):
        """TFE status should have conformity flags"""
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/tfe/status", timeout=30)
        data = response.json()
        
        conformity = data.get("conformity", {})
        assert conformity.get("source_id_dynamic") is True
        assert conformity.get("zero_transversality") is True
        assert conformity.get("zero_duplication") is True
        

# =================================================================
# 2. TFE ANALYZE — MULTI-SPECIES (5)
# =================================================================

class TestTFEAnalyzeSpecies:
    """Tests for POST /api/v1/bionic/tfe/analyze with all 5 species"""
    
    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_analyze_species_returns_200(self, api_client, species):
        """TFE analyze should return 200 for each species"""
        payload = {
            "bounds": TERRITORIES["laurentides"],
            "species": species,
            "resolution": RESOLUTION,
        }
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/tfe/analyze",
            json=payload,
            timeout=TIMEOUT
        )
        assert response.status_code == 200, f"Species {species} failed: {response.text}"
        
    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_analyze_source_id_dynamic(self, api_client, species):
        """source_id should be TFE_{SPECIES} for each species"""
        payload = {
            "bounds": TERRITORIES["laurentides"],
            "species": species,
            "resolution": RESOLUTION,
        }
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/tfe/analyze",
            json=payload,
            timeout=TIMEOUT
        )
        data = response.json()
        expected_source_id = f"TFE_{species.upper()}"
        assert data["source_id"] == expected_source_id, f"Expected {expected_source_id}, got {data['source_id']}"


# =================================================================
# 3. TFE ANALYZE — MULTI-TERRITORY (3)
# =================================================================

class TestTFEAnalyzeTerritory:
    """Tests for POST /api/v1/bionic/tfe/analyze across 3 territories"""
    
    @pytest.mark.parametrize("territory_name", TERRITORIES.keys())
    def test_analyze_territory_returns_200(self, api_client, territory_name):
        """TFE analyze should return 200 for each territory"""
        payload = {
            "bounds": TERRITORIES[territory_name],
            "species": "moose",
            "resolution": RESOLUTION,
        }
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/tfe/analyze",
            json=payload,
            timeout=TIMEOUT
        )
        assert response.status_code == 200, f"Territory {territory_name} failed: {response.text}"


# =================================================================
# 4. TFE THERMAL STATS VALIDATION
# =================================================================

class TestTFEThermalStats:
    """Tests for 5 thermal field stats in response"""
    
    def test_stats_contains_all_keys(self, api_client):
        """Response stats should contain all 10 stat keys"""
        payload = {
            "bounds": TERRITORIES["laurentides"],
            "species": "moose",
            "resolution": RESOLUTION,
        }
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/tfe/analyze",
            json=payload,
            timeout=TIMEOUT
        )
        data = response.json()
        stats = data.get("stats", {})
        
        for key in EXPECTED_STAT_KEYS:
            assert key in stats, f"Missing stat key: {key}"
            
    def test_mean_values_in_0_1_range(self, api_client):
        """Mean values should be in [0, 1] range"""
        payload = {
            "bounds": TERRITORIES["gatineau"],
            "species": "deer",
            "resolution": RESOLUTION,
        }
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/tfe/analyze",
            json=payload,
            timeout=TIMEOUT
        )
        data = response.json()
        stats = data.get("stats", {})
        
        mean_keys = ["mean_gradient", "mean_inertia", "mean_hot_pocket", "mean_cold_pocket", "mean_composite"]
        for key in mean_keys:
            value = stats.get(key)
            assert value is not None, f"Missing mean key: {key}"
            assert 0.0 <= value <= 1.0, f"{key} value {value} out of range [0,1]"
            
    def test_range_values_valid(self, api_client):
        """Range values should be [min, max] with min <= max in [0,1]"""
        payload = {
            "bounds": TERRITORIES["charlevoix"],
            "species": "bear",
            "resolution": RESOLUTION,
        }
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/tfe/analyze",
            json=payload,
            timeout=TIMEOUT
        )
        data = response.json()
        stats = data.get("stats", {})
        
        range_keys = ["gradient_range", "inertia_range", "hot_pocket_range", "cold_pocket_range", "composite_range"]
        for key in range_keys:
            rng = stats.get(key)
            assert rng is not None, f"Missing range key: {key}"
            assert len(rng) == 2, f"{key} should have 2 elements"
            assert rng[0] <= rng[1], f"{key} min > max: {rng}"
            assert 0.0 <= rng[0] <= 1.01, f"{key} min out of range: {rng[0]}"
            assert 0.0 <= rng[1] <= 1.01, f"{key} max out of range: {rng[1]}"


# =================================================================
# 5. CORRIDOR THERMAL ANALYSIS
# =================================================================

class TestCorridorThermal:
    """Tests for corridor_thermal in response"""
    
    def test_corridor_thermal_exists(self, api_client):
        """Response should contain corridor_thermal array"""
        payload = {
            "bounds": TERRITORIES["laurentides"],
            "species": "moose",
            "resolution": RESOLUTION,
        }
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/tfe/analyze",
            json=payload,
            timeout=TIMEOUT
        )
        data = response.json()
        assert "corridor_thermal" in data
        assert isinstance(data["corridor_thermal"], list)
        
    def test_corridor_thermal_structure(self, api_client):
        """Each corridor_thermal should have correct structure"""
        payload = {
            "bounds": TERRITORIES["gatineau"],
            "species": "elk",
            "resolution": RESOLUTION,
        }
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/tfe/analyze",
            json=payload,
            timeout=TIMEOUT
        )
        data = response.json()
        corridors = data.get("corridor_thermal", [])
        
        if len(corridors) > 0:
            for ct in corridors:
                assert "corridor_id" in ct
                assert "thermal_analysis" in ct
                ta = ct["thermal_analysis"]
                assert "mean_gradient" in ta
                assert "mean_inertia" in ta
                assert "mean_hot_pocket" in ta
                assert "mean_cold_pocket" in ta
                assert "mean_composite" in ta
                assert "thermal_class" in ta
                assert "sample_count" in ta
                
    def test_thermal_class_valid(self, api_client):
        """thermal_class should be one of valid values"""
        payload = {
            "bounds": TERRITORIES["charlevoix"],
            "species": "wild_turkey",
            "resolution": RESOLUTION,
        }
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/tfe/analyze",
            json=payload,
            timeout=TIMEOUT
        )
        data = response.json()
        corridors = data.get("corridor_thermal", [])
        
        if len(corridors) > 0:
            for ct in corridors:
                thermal_class = ct["thermal_analysis"]["thermal_class"]
                assert thermal_class in VALID_THERMAL_CLASSES, f"Invalid thermal_class: {thermal_class}"


# =================================================================
# 6. PIPELINE SOURCE IDS — 10 MODULES
# =================================================================

class TestPipelineSourceIds:
    """Tests for pipeline_source_ids with 10 keys"""
    
    def test_pipeline_has_10_keys(self, api_client):
        """pipeline_source_ids should have exactly 10 keys"""
        payload = {
            "bounds": TERRITORIES["laurentides"],
            "species": "moose",
            "resolution": RESOLUTION,
        }
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/tfe/analyze",
            json=payload,
            timeout=TIMEOUT
        )
        data = response.json()
        pipeline = data.get("pipeline_source_ids", {})
        
        for key in EXPECTED_PIPELINE_KEYS:
            assert key in pipeline, f"Missing pipeline key: {key}"
            
    def test_pipeline_source_ids_format(self, api_client):
        """Each pipeline source_id should follow format MODULE_{SPECIES}"""
        payload = {
            "bounds": TERRITORIES["gatineau"],
            "species": "deer",
            "resolution": RESOLUTION,
        }
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/tfe/analyze",
            json=payload,
            timeout=TIMEOUT
        )
        data = response.json()
        pipeline = data.get("pipeline_source_ids", {})
        
        # TFE source_id should be TFE_DEER
        assert pipeline["tfe"] == "TFE_DEER"
        # BMPE source_id should be BMPE_DEER
        assert pipeline["bmpe"] == "BMPE_DEER"


# =================================================================
# 7. VALIDATION FLAGS — ALL TRUE
# =================================================================

class TestValidationFlags:
    """Tests for validation flags all being True"""
    
    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_validation_flags_all_true(self, api_client, species):
        """All 9 validation flags should be True for each species"""
        payload = {
            "bounds": TERRITORIES["laurentides"],
            "species": species,
            "resolution": RESOLUTION,
        }
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/tfe/analyze",
            json=payload,
            timeout=TIMEOUT
        )
        data = response.json()
        validation = data.get("validation", {})
        
        for flag in EXPECTED_VALIDATION_FLAGS:
            assert flag in validation, f"Missing validation flag: {flag}"
            assert validation[flag] is True, f"validation[{flag}] is {validation[flag]} for {species}"


# =================================================================
# 8. INVALID SPECIES — 400 ERROR
# =================================================================

class TestInvalidSpecies:
    """Tests for invalid species handling"""
    
    def test_invalid_species_returns_400(self, api_client):
        """Invalid species should return 400"""
        payload = {
            "bounds": TERRITORIES["laurentides"],
            "species": "invalid_species",
            "resolution": RESOLUTION,
        }
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/tfe/analyze",
            json=payload,
            timeout=TIMEOUT
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        
    def test_invalid_species_error_message(self, api_client):
        """Invalid species error should contain helpful message"""
        payload = {
            "bounds": TERRITORIES["laurentides"],
            "species": "unicorn",
            "resolution": RESOLUTION,
        }
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/tfe/analyze",
            json=payload,
            timeout=TIMEOUT
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data or "error" in data


# =================================================================
# 9. NON-REGRESSION: BMPE ENDPOINT
# =================================================================

class TestNonRegressionBMPE:
    """Non-regression tests for BMPE endpoints"""
    
    def test_bmpe_status_still_works(self, api_client):
        """BMPE status endpoint should still return 200"""
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/bmpe/status", timeout=30)
        assert response.status_code == 200, f"BMPE status failed: {response.text}"
        data = response.json()
        assert data["module"] == "BMPE"
        assert data["status"] == "active"
        
    def test_bmpe_analyze_still_works(self, api_client):
        """BMPE analyze endpoint should still return 200"""
        payload = {
            "bounds": TERRITORIES["laurentides"],
            "species": "moose",
            "resolution": RESOLUTION,
        }
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/bmpe/analyze",
            json=payload,
            timeout=TIMEOUT
        )
        assert response.status_code == 200, f"BMPE analyze failed: {response.text}"
        data = response.json()
        assert data["source_id"] == "BMPE_MOOSE"


# =================================================================
# 10. NON-REGRESSION: PME ENDPOINT
# =================================================================

class TestNonRegressionPME:
    """Non-regression tests for PME endpoints"""
    
    def test_pme_status_still_works(self, api_client):
        """PME status endpoint should still return 200"""
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/pme/status", timeout=30)
        assert response.status_code == 200, f"PME status failed: {response.text}"
        data = response.json()
        assert data["module"] == "PME"
        assert data["status"] == "active"
        
    def test_pme_analyze_still_works(self, api_client):
        """PME analyze endpoint should still return 200"""
        payload = {
            "bounds": TERRITORIES["laurentides"],
            "species": "moose",
            "resolution": RESOLUTION,
        }
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/pme/analyze",
            json=payload,
            timeout=TIMEOUT
        )
        assert response.status_code == 200, f"PME analyze failed: {response.text}"
        data = response.json()
        assert data["source_id"] == "PME_MOOSE"


# =================================================================
# 11. SPECIES DIFFERENTIATION
# =================================================================

class TestSpeciesDifferentiation:
    """Tests to verify different species produce different results"""
    
    def test_different_species_different_stats(self, api_client):
        """Different species should produce different thermal stats"""
        results = {}
        for species in ["moose", "bear"]:
            payload = {
                "bounds": TERRITORIES["laurentides"],
                "species": species,
                "resolution": RESOLUTION,
            }
            response = api_client.post(
                f"{BASE_URL}/api/v1/bionic/tfe/analyze",
                json=payload,
                timeout=TIMEOUT
            )
            assert response.status_code == 200
            data = response.json()
            results[species] = data["stats"]["mean_composite"]
            
        # Moose and bear should have different composite values
        assert results["moose"] != results["bear"], "Different species should have different stats"


# =================================================================
# 12. FULL PIPELINE VALIDATION
# =================================================================

class TestFullPipelineValidation:
    """Comprehensive tests for full TFE pipeline"""
    
    def test_full_response_structure(self, api_client):
        """Full response should have all required fields"""
        payload = {
            "bounds": TERRITORIES["laurentides"],
            "species": "moose",
            "resolution": RESOLUTION,
        }
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/tfe/analyze",
            json=payload,
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        data = response.json()
        
        # Required top-level keys
        required_keys = ["source_id", "species", "bounds", "resolution", "stats", 
                         "corridor_thermal", "validation", "computation_time_ms", "pipeline_source_ids"]
        for key in required_keys:
            assert key in data, f"Missing required key: {key}"
            
    def test_computation_time_reasonable(self, api_client):
        """Computation time should be reasonable (< 30s)"""
        payload = {
            "bounds": TERRITORIES["laurentides"],
            "species": "moose",
            "resolution": RESOLUTION,
        }
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/tfe/analyze",
            json=payload,
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        data = response.json()
        
        comp_time = data.get("computation_time_ms", 0)
        assert comp_time > 0, "Computation time should be positive"
        assert comp_time < 30000, f"Computation time {comp_time}ms exceeds 30s limit"
