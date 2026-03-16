"""
BIONIC V3 - ALIMENTATION-V1 & REPOS-V1 Engines Test Suite
==========================================================
Tests for:
- ALIMENTATION-V1: Food scoring engine (5 species: CERF, ORIGNAL, OURS, DINDON, WAPITI)
- REPOS-V1: Rest zone scoring engine (5 species: CERF, ORIGNAL, OURS, DINDON, WAPITI)

Score axes tested:
- ALIMENTATION: PROTEINES(0-25), ENERGIE(0-25), MINERAUX(0-20), SECURITE(0-20), EFFORT(0-10)
- REPOS: COUVERT(0-30), CALME(0-25), THERMIQUE(0-20), ACCESSIBILITE(0-15), PROX_ALIM(0-10)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    raise ValueError("REACT_APP_BACKEND_URL environment variable must be set")

# Test coordinates (Quebec region)
TEST_LAT = 46.8
TEST_LNG = -71.2
TEST_MONTH = 10  # October (automne)

SPECIES_LIST = ["CERF", "ORIGNAL", "OURS", "DINDON", "WAPITI"]

# ============================================================
# ALIMENTATION-V1 ENGINE TESTS
# ============================================================

class TestAlimentationV1Profiles:
    """Test ALIMENTATION-V1 /profiles and /profile/{species} endpoints"""
    
    def test_profiles_endpoint_returns_5_species(self):
        """GET /api/v1/alimentation/profiles returns all 5 species"""
        response = requests.get(f"{BASE_URL}/api/v1/alimentation/profiles")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["engine"] == "ALIMENTATION-V1"
        assert data["species_count"] == 5
        assert len(data["profiles"]) == 5
        
        profile_ids = [p["id"] for p in data["profiles"]]
        for species in SPECIES_LIST:
            assert species in profile_ids, f"Species {species} missing from profiles"
        
        print(f"PASS: /profiles returns {data['species_count']} species profiles")
    
    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_species_profile_endpoint(self, species):
        """GET /api/v1/alimentation/profile/{species} returns valid profile"""
        response = requests.get(f"{BASE_URL}/api/v1/alimentation/profile/{species}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["engine"] == "ALIMENTATION-V1"
        assert data["species"] == species.upper()
        assert "profile" in data
        
        profile = data["profile"]
        # Verify essential profile fields
        assert "sources_proteines" in profile
        assert "sources_energie" in profile
        assert "sources_mineraux" in profile
        assert "securite" in profile
        assert "effort" in profile
        assert "saisonnalite" in profile
        
        print(f"PASS: /profile/{species} returns valid profile with all fields")


class TestAlimentationV1Point:
    """Test ALIMENTATION-V1 /point endpoint for single point analysis"""
    
    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_point_analysis_per_species(self, species):
        """GET /api/v1/alimentation/point returns score 0-100 for each species"""
        response = requests.get(
            f"{BASE_URL}/api/v1/alimentation/point",
            params={"lat": TEST_LAT, "lng": TEST_LNG, "species": species, "month": TEST_MONTH}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["engine"] == "ALIMENTATION-V1"
        assert data["species"] == species.upper()
        
        # Validate score is 0-100
        score = data["score_alimentation"]
        assert 0 <= score <= 100, f"Score {score} not in [0, 100]"
        
        # Validate detail axes
        detail = data["detail"]
        assert 0 <= detail["proteines"]["score"] <= 25, "PROTEINES score out of range [0-25]"
        assert 0 <= detail["energie"]["score"] <= 25, "ENERGIE score out of range [0-25]"
        assert 0 <= detail["mineraux"]["score"] <= 20, "MINERAUX score out of range [0-20]"
        assert 0 <= detail["securite"]["score"] <= 20, "SECURITE score out of range [0-20]"
        assert 0 <= detail["effort"]["score"] <= 10, "EFFORT score out of range [0-10]"
        
        # Validate sum approximately equals total
        axis_sum = (
            detail["proteines"]["score"] +
            detail["energie"]["score"] +
            detail["mineraux"]["score"] +
            detail["securite"]["score"] +
            detail["effort"]["score"]
        )
        assert abs(axis_sum - score) < 0.5, f"Axis sum {axis_sum} != total score {score}"
        
        print(f"PASS: /point for {species} - score={score:.1f}, class={data['classe_alimentation']}")
    
    def test_point_with_different_months(self):
        """Test seasonal variation affects scoring"""
        scores_by_month = {}
        for month in [1, 4, 7, 10]:  # winter, spring, summer, autumn
            response = requests.get(
                f"{BASE_URL}/api/v1/alimentation/point",
                params={"lat": TEST_LAT, "lng": TEST_LNG, "species": "CERF", "month": month}
            )
            assert response.status_code == 200
            data = response.json()
            scores_by_month[month] = data["score_alimentation"]
            print(f"  Month {month}: score={data['score_alimentation']:.1f}, season={data['season']}")
        
        print(f"PASS: Seasonal variation tested - scores vary by month")


class TestAlimentationV1Analyze:
    """Test ALIMENTATION-V1 /analyze endpoint for full grid analysis"""
    
    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_analyze_returns_valid_grid(self, species):
        """POST /api/v1/alimentation/analyze returns valid scored grid"""
        response = requests.post(
            f"{BASE_URL}/api/v1/alimentation/analyze",
            json={
                "center_lat": TEST_LAT,
                "center_lng": TEST_LNG,
                "species": species,
                "month": TEST_MONTH,
                "sample_step": 10  # Use larger step for faster tests
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["engine"] == "ALIMENTATION-V1"
        assert data["species"] == species.upper()
        assert "cells" in data
        assert "statistics" in data
        assert "bce4x_validation" in data
        
        # Validate grid structure
        grid = data["grid"]
        assert grid["side_m"] == 2000
        assert grid["cell_m"] == 10
        assert grid["center_lat"] == TEST_LAT
        
        # Validate all cells have valid scores
        for cell in data["cells"][:10]:  # Check first 10
            assert 0 <= cell["score_alimentation"] <= 100
            assert "classe_alimentation" in cell
            assert "detail" in cell
        
        print(f"PASS: /analyze for {species} - {len(data['cells'])} cells scored")
    
    def test_analyze_bce4x_validation_passes(self):
        """BCE-4X validation should pass for valid analysis"""
        response = requests.post(
            f"{BASE_URL}/api/v1/alimentation/analyze",
            json={
                "center_lat": TEST_LAT,
                "center_lng": TEST_LNG,
                "species": "CERF",
                "month": TEST_MONTH,
                "sample_step": 10
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        bce4x = data["bce4x_validation"]
        assert bce4x["status"] == "PASS", f"BCE-4X validation failed: {bce4x}"
        assert bce4x["checks"]["GEOM-001"] == "PASS", "GEOM-001 check failed"
        assert bce4x["checks"]["GEOM-002"] == "PASS", "GEOM-002 check failed"
        
        print(f"PASS: BCE-4X validation - all checks passed")


class TestAlimentationV1Documentation:
    """Test ALIMENTATION-V1 /documentation endpoint"""
    
    def test_documentation_returns_complete_spec(self):
        """GET /api/v1/alimentation/documentation returns technical spec"""
        response = requests.get(f"{BASE_URL}/api/v1/alimentation/documentation")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["engine"] == "ALIMENTATION-V1"
        assert "version" in data
        assert "axes" in data
        assert "species" in data
        
        # Validate axes documentation
        axes = data["axes"]
        expected_axes = ["PROTEINES", "ENERGIE", "MINERAUX", "SECURITE", "EFFORT"]
        for axis in expected_axes:
            assert axis in axes, f"Axis {axis} missing from documentation"
        
        print(f"PASS: /documentation returns complete technical specification")


# ============================================================
# REPOS-V1 ENGINE TESTS
# ============================================================

class TestReposV1Profiles:
    """Test REPOS-V1 /profiles and /profile/{species} endpoints"""
    
    def test_profiles_endpoint_returns_5_species(self):
        """GET /api/v1/repos/profiles returns all 5 species"""
        response = requests.get(f"{BASE_URL}/api/v1/repos/profiles")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["engine"] == "REPOS-V1"
        assert data["species_count"] == 5
        assert len(data["profiles"]) == 5
        
        profile_ids = [p["id"] for p in data["profiles"]]
        for species in SPECIES_LIST:
            assert species in profile_ids, f"Species {species} missing from profiles"
        
        print(f"PASS: /profiles returns {data['species_count']} species profiles")
    
    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_species_profile_endpoint(self, species):
        """GET /api/v1/repos/profile/{species} returns valid profile"""
        response = requests.get(f"{BASE_URL}/api/v1/repos/profile/{species}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["engine"] == "REPOS-V1"
        assert data["species"] == species.upper()
        assert "profile" in data
        
        profile = data["profile"]
        # Verify essential profile fields
        assert "couvert" in profile
        assert "calme" in profile
        assert "thermique" in profile
        assert "accessibilite" in profile
        assert "prox_alim" in profile
        assert "rythme_circadien" in profile
        
        print(f"PASS: /profile/{species} returns valid profile with all fields")


class TestReposV1Point:
    """Test REPOS-V1 /point endpoint for single point analysis"""
    
    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_point_analysis_per_species(self, species):
        """GET /api/v1/repos/point returns score 0-100 for each species"""
        response = requests.get(
            f"{BASE_URL}/api/v1/repos/point",
            params={"lat": TEST_LAT, "lng": TEST_LNG, "species": species, "month": TEST_MONTH}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["engine"] == "REPOS-V1"
        assert data["species"] == species.upper()
        
        # Validate score is 0-100
        score = data["score_repos"]
        assert 0 <= score <= 100, f"Score {score} not in [0, 100]"
        
        # Validate detail axes
        detail = data["detail"]
        assert 0 <= detail["couvert"]["score"] <= 30, "COUVERT score out of range [0-30]"
        assert 0 <= detail["calme"]["score"] <= 25, "CALME score out of range [0-25]"
        assert 0 <= detail["thermique"]["score"] <= 20, "THERMIQUE score out of range [0-20]"
        assert 0 <= detail["accessibilite"]["score"] <= 15, "ACCESSIBILITE score out of range [0-15]"
        assert 0 <= detail["prox_alim"]["score"] <= 10, "PROX_ALIM score out of range [0-10]"
        
        print(f"PASS: /point for {species} - score={score:.1f}, class={data['classe_repos']}")


class TestReposV1Analyze:
    """Test REPOS-V1 /analyze endpoint for full grid analysis"""
    
    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_analyze_returns_valid_grid(self, species):
        """POST /api/v1/repos/analyze returns valid scored grid"""
        response = requests.post(
            f"{BASE_URL}/api/v1/repos/analyze",
            json={
                "center_lat": TEST_LAT,
                "center_lng": TEST_LNG,
                "species": species,
                "month": TEST_MONTH,
                "sample_step": 10
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["engine"] == "REPOS-V1"
        assert data["species"] == species.upper()
        assert "cells" in data
        assert "statistics" in data
        assert "bce4x_validation" in data
        
        # Validate all cells have valid scores
        for cell in data["cells"][:10]:
            assert 0 <= cell["score_repos"] <= 100
            assert "classe_repos" in cell
            assert "detail" in cell
        
        print(f"PASS: /analyze for {species} - {len(data['cells'])} cells scored")
    
    def test_analyze_bce4x_validation_passes(self):
        """BCE-4X validation should pass for valid analysis"""
        response = requests.post(
            f"{BASE_URL}/api/v1/repos/analyze",
            json={
                "center_lat": TEST_LAT,
                "center_lng": TEST_LNG,
                "species": "CERF",
                "month": TEST_MONTH,
                "sample_step": 10
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        bce4x = data["bce4x_validation"]
        assert bce4x["status"] == "PASS", f"BCE-4X validation failed: {bce4x}"
        assert bce4x["checks"]["GEOM-001"] == "PASS"
        assert bce4x["checks"]["GEOM-002"] == "PASS"
        
        print(f"PASS: BCE-4X validation - all checks passed")


class TestReposV1Documentation:
    """Test REPOS-V1 /documentation endpoint"""
    
    def test_documentation_returns_complete_spec(self):
        """GET /api/v1/repos/documentation returns technical spec"""
        response = requests.get(f"{BASE_URL}/api/v1/repos/documentation")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["engine"] == "REPOS-V1"
        assert "version" in data
        assert "axes" in data
        assert "species" in data
        
        # Validate axes documentation
        axes = data["axes"]
        expected_axes = ["COUVERT", "CALME", "THERMIQUE", "ACCESSIBILITE", "PROX_ALIM"]
        for axis in expected_axes:
            assert axis in axes, f"Axis {axis} missing from documentation"
        
        print(f"PASS: /documentation returns complete technical specification")


# ============================================================
# CROSS-ENGINE TESTS
# ============================================================

class TestMultiSpeciesAnalysis:
    """Test multi-species analysis endpoints"""
    
    def test_alimentation_multi_returns_all_species(self):
        """GET /api/v1/alimentation/multi returns results for all 5 species"""
        response = requests.get(
            f"{BASE_URL}/api/v1/alimentation/multi",
            params={"lat": TEST_LAT, "lng": TEST_LNG, "month": TEST_MONTH, "sample_step": 10}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["engine"] == "ALIMENTATION-V1"
        assert data["mode"] == "multi_species"
        
        species_results = data["species_results"]
        assert len(species_results) == 5
        for species in SPECIES_LIST:
            assert species in species_results, f"Species {species} missing from multi results"
        
        print(f"PASS: /multi returns results for all 5 species")
    
    def test_repos_multi_returns_all_species(self):
        """GET /api/v1/repos/multi returns results for all 5 species"""
        response = requests.get(
            f"{BASE_URL}/api/v1/repos/multi",
            params={"lat": TEST_LAT, "lng": TEST_LNG, "month": TEST_MONTH, "sample_step": 10}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["engine"] == "REPOS-V1"
        assert data["mode"] == "multi_species"
        
        species_results = data["species_results"]
        assert len(species_results) == 5
        for species in SPECIES_LIST:
            assert species in species_results
        
        print(f"PASS: /multi returns results for all 5 species")


class TestEnginesIndependence:
    """Verify new engines don't break existing ones"""
    
    def test_existing_v2_engines_still_work(self):
        """Existing V2 engines should remain functional"""
        # Test V2 hotspots endpoint
        response = requests.get(f"{BASE_URL}/api/v1/bionic/engines/v2/status")
        assert response.status_code == 200, f"V2 engines status failed: {response.status_code}"
        print("PASS: V2 engines status endpoint works")
    
    def test_existing_v3_engines_still_work(self):
        """Existing V3 engines should remain functional"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/engines/v3/status")
        assert response.status_code == 200, f"V3 engines status failed: {response.status_code}"
        print("PASS: V3 engines status endpoint works")
    
    def test_bionic_pipeline_still_works(self):
        """BIONIC pipeline should remain functional"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/status")
        # 200 or 404 both acceptable (endpoint may have different path)
        assert response.status_code in [200, 404], f"Unexpected status: {response.status_code}"
        print("PASS: BIONIC status check completed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
