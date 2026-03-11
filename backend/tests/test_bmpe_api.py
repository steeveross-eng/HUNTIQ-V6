"""
TEST SUITE — BMPE API (Behavioral Micro-Patterns Engine)
BIONIC V5 ULTIME 300% — Phase d'Optimisation #9

Tests:
- POST /api/v1/bionic/bmpe/analyze — 5 espèces x 3 territoires
- GET /api/v1/bionic/bmpe/status — module info + conformité
- source_id dynamique BMPE_{SPECIES}
- 5 champs micro-pattern dans stats
- corridor_micro_patterns validation
- pipeline_source_ids contient 9 clés
- validation flags tous à true
- Espèce invalide retourne 400
- Non-régression: PME et TCVE endpoints
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL').rstrip('/')
TIMEOUT = 60  # Heavy pipeline needs longer timeout

SPECIES_LIST = ["moose", "deer", "bear", "wild_turkey", "elk"]

TERRITORIES = {
    "laurentides": {"north": 46.95, "south": 46.85, "east": -74.00, "west": -74.15},
    "gatineau": {"north": 45.55, "south": 45.45, "east": -75.70, "west": -75.85},
    "charlevoix": {"north": 47.60, "south": 47.50, "east": -70.50, "west": -70.65},
}

PIPELINE_SOURCE_IDS = ["sse", "osg", "cme", "wse", "vfe", "ssvl", "tcve", "pme", "bmpe"]

MICRO_PATTERN_STAT_KEYS = ["mean_retreat", "mean_exploration", "mean_hesitation", "mean_fine_movement", "mean_composite"]

VALID_PATTERN_CLASSES = ["avoidance_corridor", "exploration_corridor", "transition_hesitation", "stable_transit"]

VALIDATION_FLAGS = ["sse_integrated", "wse_integrated", "ssvl_integrated", "tcve_integrated", "pme_integrated", "cme_integrated", "all_fields_normalized", "species_profile_applied"]


class TestBMPEStatus:
    """BMPE Status endpoint tests"""
    
    def test_status_endpoint_returns_200(self):
        """GET /api/v1/bionic/bmpe/status returns 200"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/bmpe/status", timeout=10)
        assert response.status_code == 200
        print(f"✓ BMPE status endpoint returns 200")
    
    def test_status_contains_module_info(self):
        """Status contains module name and version"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/bmpe/status", timeout=10)
        data = response.json()
        assert data["module"] == "BMPE"
        assert data["label"] == "Behavioral Micro-Patterns Engine"
        assert "version" in data
        assert data["status"] == "active"
        print(f"✓ BMPE module info correct: {data['module']} v{data['version']}")
    
    def test_status_species_supported(self):
        """Status lists all 5 supported species"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/bmpe/status", timeout=10)
        data = response.json()
        for species in SPECIES_LIST:
            assert species in data["species_supported"], f"Species {species} not in supported list"
        print(f"✓ All 5 species supported: {data['species_supported']}")
    
    def test_status_conformity_flags(self):
        """Status conformity flags are correct"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/bmpe/status", timeout=10)
        data = response.json()
        conformity = data["conformity"]
        assert conformity["source_id_dynamic"] is True
        assert conformity["zero_transversality"] is True
        assert conformity["zero_duplication"] is True
        assert conformity["all_fields_normalized"] is True
        assert conformity["species_profile_applied"] is True
        print(f"✓ Conformity flags all valid")


class TestBMPEAnalyzeBasic:
    """BMPE Analyze endpoint basic tests"""
    
    def test_analyze_moose_laurentides(self):
        """POST /api/v1/bionic/bmpe/analyze — moose/laurentides"""
        payload = {
            "bounds": TERRITORIES["laurentides"],
            "species": "moose",
            "resolution": 30
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/bmpe/analyze", json=payload, timeout=TIMEOUT)
        assert response.status_code == 200
        data = response.json()
        assert data["source_id"] == "BMPE_MOOSE"
        print(f"✓ moose/laurentides: source_id={data['source_id']}, time={data.get('computation_time_ms')}ms")
    
    def test_analyze_invalid_species_returns_400(self):
        """Invalid species returns 400"""
        payload = {
            "bounds": TERRITORIES["laurentides"],
            "species": "invalid_species",
            "resolution": 30
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/bmpe/analyze", json=payload, timeout=TIMEOUT)
        assert response.status_code == 400
        print(f"✓ Invalid species returns 400")


class TestBMPESourceIdDynamic:
    """Test source_id dynamique BMPE_{SPECIES}"""
    
    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_source_id_per_species(self, species):
        """source_id = BMPE_{SPECIES.upper()}"""
        payload = {
            "bounds": TERRITORIES["laurentides"],
            "species": species,
            "resolution": 30
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/bmpe/analyze", json=payload, timeout=TIMEOUT)
        assert response.status_code == 200
        data = response.json()
        expected_source_id = f"BMPE_{species.upper()}"
        assert data["source_id"] == expected_source_id, f"Expected {expected_source_id}, got {data['source_id']}"
        print(f"✓ {species}: source_id={data['source_id']}")


class TestBMPEMicroPatternStats:
    """Test 5 micro-pattern stats in response"""
    
    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_stats_contain_5_micro_pattern_means(self, species):
        """Stats contain mean_retreat, mean_exploration, mean_hesitation, mean_fine_movement, mean_composite"""
        payload = {
            "bounds": TERRITORIES["gatineau"],
            "species": species,
            "resolution": 30
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/bmpe/analyze", json=payload, timeout=TIMEOUT)
        assert response.status_code == 200
        data = response.json()
        stats = data["stats"]
        
        for key in MICRO_PATTERN_STAT_KEYS:
            assert key in stats, f"Missing {key} in stats for {species}"
            assert 0.0 <= stats[key] <= 1.0, f"{key} out of range [0,1]: {stats[key]}"
        
        print(f"✓ {species} stats: retreat={stats['mean_retreat']:.3f}, exploration={stats['mean_exploration']:.3f}, hesitation={stats['mean_hesitation']:.3f}, fine_mov={stats['mean_fine_movement']:.3f}, composite={stats['mean_composite']:.3f}")


class TestBMPECorridorPatterns:
    """Test corridor_micro_patterns structure"""
    
    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_corridor_patterns_exist(self, species):
        """corridor_micro_patterns is a non-empty list"""
        payload = {
            "bounds": TERRITORIES["charlevoix"],
            "species": species,
            "resolution": 30
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/bmpe/analyze", json=payload, timeout=TIMEOUT)
        assert response.status_code == 200
        data = response.json()
        corridors = data["corridor_micro_patterns"]
        assert isinstance(corridors, list)
        assert len(corridors) > 0, f"No corridor patterns for {species}"
        print(f"✓ {species}: {len(corridors)} corridor patterns")
    
    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_corridor_pattern_class_valid(self, species):
        """pattern_class is one of: avoidance_corridor, exploration_corridor, transition_hesitation, stable_transit"""
        payload = {
            "bounds": TERRITORIES["laurentides"],
            "species": species,
            "resolution": 30
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/bmpe/analyze", json=payload, timeout=TIMEOUT)
        assert response.status_code == 200
        data = response.json()
        
        for cp in data["corridor_micro_patterns"]:
            assert "corridor_id" in cp
            assert "micro_pattern_analysis" in cp
            mpa = cp["micro_pattern_analysis"]
            assert mpa["pattern_class"] in VALID_PATTERN_CLASSES, f"Invalid pattern_class: {mpa['pattern_class']}"
        
        print(f"✓ {species}: All corridor pattern_class values valid")


class TestBMPEPipelineSourceIds:
    """Test pipeline_source_ids contains 9 keys"""
    
    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_pipeline_has_9_modules(self, species):
        """pipeline_source_ids contains: sse, osg, cme, wse, vfe, ssvl, tcve, pme, bmpe"""
        payload = {
            "bounds": TERRITORIES["gatineau"],
            "species": species,
            "resolution": 30
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/bmpe/analyze", json=payload, timeout=TIMEOUT)
        assert response.status_code == 200
        data = response.json()
        
        pipeline = data["pipeline_source_ids"]
        assert len(pipeline) == 9, f"Expected 9 pipeline modules, got {len(pipeline)}"
        
        for key in PIPELINE_SOURCE_IDS:
            assert key in pipeline, f"Missing {key} in pipeline_source_ids"
        
        # Verify BMPE source_id in pipeline matches response source_id
        assert pipeline["bmpe"] == data["source_id"]
        
        print(f"✓ {species}: 9 pipeline modules present, bmpe={pipeline['bmpe']}")


class TestBMPEValidationFlags:
    """Test validation flags are all true"""
    
    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_all_validation_flags_true(self, species):
        """All 8 validation flags must be true"""
        payload = {
            "bounds": TERRITORIES["charlevoix"],
            "species": species,
            "resolution": 30
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/bmpe/analyze", json=payload, timeout=TIMEOUT)
        assert response.status_code == 200
        data = response.json()
        
        validation = data["validation"]
        for flag in VALIDATION_FLAGS:
            assert flag in validation, f"Missing validation flag: {flag}"
            assert validation[flag] is True, f"Validation flag {flag} is {validation[flag]}, expected True"
        
        print(f"✓ {species}: All 8 validation flags = True")


class TestBMPEMultiTerritory:
    """Test BMPE across multiple territories"""
    
    @pytest.mark.parametrize("territory_name,territory_bounds", list(TERRITORIES.items()))
    def test_analyze_moose_all_territories(self, territory_name, territory_bounds):
        """BMPE analyze works for all 3 territories"""
        payload = {
            "bounds": territory_bounds,
            "species": "moose",
            "resolution": 30
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/bmpe/analyze", json=payload, timeout=TIMEOUT)
        assert response.status_code == 200
        data = response.json()
        assert data["source_id"] == "BMPE_MOOSE"
        assert data["bounds"]["north"] == territory_bounds["north"]
        print(f"✓ moose/{territory_name}: OK, composite={data['stats']['mean_composite']:.3f}")


class TestNonRegressionPME:
    """Non-regression: PME endpoints still work"""
    
    def test_pme_status(self):
        """GET /api/v1/bionic/pme/status"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/pme/status", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data["module"] == "PME"
        print(f"✓ PME status OK: {data['module']}")
    
    def test_pme_analyze(self):
        """POST /api/v1/bionic/pme/analyze — non-regression"""
        payload = {
            "bounds": TERRITORIES["laurentides"],
            "species": "moose",
            "resolution": 30
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/pme/analyze", json=payload, timeout=TIMEOUT)
        assert response.status_code == 200
        data = response.json()
        assert data["source_id"] == "PME_MOOSE"
        print(f"✓ PME analyze OK: source_id={data['source_id']}")


class TestNonRegressionTCVE:
    """Non-regression: TCVE endpoints still work"""
    
    def test_tcve_status(self):
        """GET /api/v1/bionic/tcve/status"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/tcve/status", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data["module"] == "TCVE"
        print(f"✓ TCVE status OK: {data['module']}")
    
    def test_tcve_analyze(self):
        """POST /api/v1/bionic/tcve/analyze — non-regression"""
        payload = {
            "bounds": TERRITORIES["laurentides"],
            "species": "moose",
            "resolution": 30
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/tcve/analyze", json=payload, timeout=TIMEOUT)
        assert response.status_code == 200
        data = response.json()
        assert data["source_id"] == "TCVE_MOOSE"
        print(f"✓ TCVE analyze OK: source_id={data['source_id']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
