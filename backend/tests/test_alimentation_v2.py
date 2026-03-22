"""
Test suite for ALIMENTATION-V2 API endpoints
============================================
Tests: POST /api/v2/alimentation/analyze
       GET /api/v2/alimentation/species
       
Verifies: terrain analysis, saline optimization, nutrition database
BCE-4X compliant: no geometric modifications
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://huntiq-connect.preview.emergentagent.com')


class TestAlimentationV2SpeciesEndpoint:
    """GET /api/v2/alimentation/species - Species list endpoint"""
    
    def test_species_list_returns_200(self):
        """Species endpoint returns 200 OK"""
        response = requests.get(f"{BASE_URL}/api/v2/alimentation/species")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: Species endpoint returns 200")
    
    def test_species_list_returns_valid_data(self):
        """Species endpoint returns list with expected species"""
        response = requests.get(f"{BASE_URL}/api/v2/alimentation/species")
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "species" in data, "Response missing 'species' key"
        assert isinstance(data["species"], list), "Species should be a list"
        
        # Verify expected species
        expected_species = ["CERF", "ORIGNAL", "OURS", "WAPITI", "DINDON"]
        for sp in expected_species:
            assert sp in data["species"], f"Missing species: {sp}"
        
        print(f"PASS: Species list contains all expected species: {data['species']}")


class TestAlimentationV2AnalyzeEndpoint:
    """POST /api/v2/alimentation/analyze - Main analysis endpoint"""
    
    def test_analyze_returns_200(self):
        """Analyze endpoint returns 200 for valid request"""
        payload = {
            "center_lat": 48.19,
            "center_lng": -68.39,
            "species": "CERF",
            "month": 10
        }
        response = requests.post(
            f"{BASE_URL}/api/v2/alimentation/analyze",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: Analyze endpoint returns 200")
    
    def test_analyze_returns_version_alimentation_v2(self):
        """Response includes version: ALIMENTATION-V2"""
        payload = {
            "center_lat": 48.19,
            "center_lng": -68.39,
            "species": "ORIGNAL",
            "month": 3
        }
        response = requests.post(
            f"{BASE_URL}/api/v2/alimentation/analyze",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "version" in data, "Response missing 'version' key"
        assert data["version"] == "ALIMENTATION-V2", f"Expected ALIMENTATION-V2, got {data['version']}"
        print(f"PASS: Version is {data['version']}")
    
    def test_analyze_returns_species_info(self):
        """Response includes species and species_nom"""
        payload = {
            "center_lat": 48.19,
            "center_lng": -68.39,
            "species": "ORIGNAL",
            "month": 3
        }
        response = requests.post(
            f"{BASE_URL}/api/v2/alimentation/analyze",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "species" in data, "Response missing 'species'"
        assert "species_nom" in data, "Response missing 'species_nom'"
        assert data["species"] == "ORIGNAL"
        assert data["species_nom"] == "Orignal"
        print(f"PASS: Species info correct - {data['species']}: {data['species_nom']}")
    
    def test_analyze_returns_score_global(self):
        """Response includes score_global (0-100)"""
        payload = {
            "center_lat": 48.19,
            "center_lng": -68.39,
            "species": "CERF",
            "month": 10
        }
        response = requests.post(
            f"{BASE_URL}/api/v2/alimentation/analyze",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "score_global" in data, "Response missing 'score_global'"
        assert isinstance(data["score_global"], (int, float)), "score_global should be numeric"
        assert 0 <= data["score_global"] <= 100, f"score_global {data['score_global']} out of range 0-100"
        print(f"PASS: score_global = {data['score_global']}")
    
    def test_analyze_returns_terrain_data(self):
        """Response includes terrain analysis with expected fields"""
        payload = {
            "center_lat": 48.19,
            "center_lng": -68.39,
            "species": "CERF",
            "month": 10
        }
        response = requests.post(
            f"{BASE_URL}/api/v2/alimentation/analyze",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "terrain" in data, "Response missing 'terrain'"
        terrain = data["terrain"]
        
        # Check terrain sub-sections
        expected_sections = ["center", "relief", "eau", "foret", "sol", "alimentaire", "nutriments_sol"]
        for section in expected_sections:
            assert section in terrain, f"Terrain missing '{section}'"
        
        print(f"PASS: Terrain data contains all expected sections: {list(terrain.keys())}")
    
    def test_analyze_returns_salines(self):
        """Response includes salines array with valid entries"""
        payload = {
            "center_lat": 48.19,
            "center_lng": -68.39,
            "species": "ORIGNAL",
            "month": 3
        }
        response = requests.post(
            f"{BASE_URL}/api/v2/alimentation/analyze",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "salines" in data, "Response missing 'salines'"
        assert "n_salines" in data, "Response missing 'n_salines'"
        assert isinstance(data["salines"], list), "salines should be a list"
        assert data["n_salines"] == len(data["salines"]), "n_salines mismatch"
        
        # Verify saline structure if any exist
        if len(data["salines"]) > 0:
            sal = data["salines"][0]
            assert "id" in sal, "Saline missing 'id'"
            assert "lat" in sal, "Saline missing 'lat'"
            assert "lng" in sal, "Saline missing 'lng'"
            assert "score" in sal, "Saline missing 'score'"
            assert "type" in sal, "Saline missing 'type'"
            print(f"PASS: Found {data['n_salines']} salines with valid structure")
        else:
            print(f"INFO: No salines returned for this location")
    
    def test_analyze_returns_nutrition(self):
        """Response includes nutrition with species-specific data"""
        payload = {
            "center_lat": 48.19,
            "center_lng": -68.39,
            "species": "CERF",
            "month": 10
        }
        response = requests.post(
            f"{BASE_URL}/api/v2/alimentation/analyze",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "nutrition" in data, "Response missing 'nutrition'"
        nutrition = data["nutrition"]
        
        # Check nutrition sub-sections
        expected_fields = ["aliments_recommandes", "nutriments_essentiels", "proteines", "oligo_elements"]
        for field in expected_fields:
            assert field in nutrition, f"Nutrition missing '{field}'"
        
        # Verify aliments_recommandes is non-empty
        assert len(nutrition["aliments_recommandes"]) > 0, "aliments_recommandes should not be empty"
        
        print(f"PASS: Nutrition data complete with {len(nutrition['aliments_recommandes'])} recommended foods")
    
    def test_analyze_returns_carences_detectees(self):
        """Response includes carences_detectees array"""
        payload = {
            "center_lat": 48.19,
            "center_lng": -68.39,
            "species": "CERF",
            "month": 10
        }
        response = requests.post(
            f"{BASE_URL}/api/v2/alimentation/analyze",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "carences_detectees" in data, "Response missing 'carences_detectees'"
        assert isinstance(data["carences_detectees"], list), "carences_detectees should be a list"
        
        # If carences exist, verify structure
        if len(data["carences_detectees"]) > 0:
            carence = data["carences_detectees"][0]
            assert "element" in carence, "Carence missing 'element'"
            assert "valeur_sol" in carence, "Carence missing 'valeur_sol'"
            assert "seuil_minimum" in carence, "Carence missing 'seuil_minimum'"
            assert "deficit_pct" in carence, "Carence missing 'deficit_pct'"
        
        print(f"PASS: carences_detectees found: {len(data['carences_detectees'])} deficiencies")
    
    def test_analyze_returns_bce4x_conformite(self):
        """Response includes conformite.bce4x = True"""
        payload = {
            "center_lat": 48.19,
            "center_lng": -68.39,
            "species": "CERF",
            "month": 10
        }
        response = requests.post(
            f"{BASE_URL}/api/v2/alimentation/analyze",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "conformite" in data, "Response missing 'conformite'"
        assert data["conformite"].get("bce4x") == True, "BCE-4X conformite should be True"
        assert data["conformite"].get("zones_modifiees") == 0, "zones_modifiees should be 0"
        assert data["conformite"].get("centres_modifies") == 0, "centres_modifies should be 0"
        
        print(f"PASS: BCE-4X conformite verified")


class TestAlimentationV2DifferentSpecies:
    """Test analyze endpoint with different species"""
    
    @pytest.mark.parametrize("species,expected_nom", [
        ("CERF", "Chevreuil (Cerf de Virginie)"),
        ("ORIGNAL", "Orignal"),
        ("OURS", "Ours noir"),
        ("WAPITI", "Wapiti"),
        ("DINDON", "Dindon sauvage"),
    ])
    def test_species_returns_correct_name(self, species, expected_nom):
        """Each species returns correct species_nom"""
        payload = {
            "center_lat": 48.19,
            "center_lng": -68.39,
            "species": species,
            "month": 6
        }
        response = requests.post(
            f"{BASE_URL}/api/v2/alimentation/analyze",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["species"] == species
        assert data["species_nom"] == expected_nom
        print(f"PASS: {species} -> {expected_nom}")


class TestAlimentationV2EdgeCases:
    """Edge case tests"""
    
    def test_invalid_species_defaults_to_cerf(self):
        """Invalid species defaults to CERF"""
        payload = {
            "center_lat": 48.19,
            "center_lng": -68.39,
            "species": "INVALID_SPECIES",
            "month": 10
        }
        response = requests.post(
            f"{BASE_URL}/api/v2/alimentation/analyze",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["species"] == "CERF", "Invalid species should default to CERF"
        print("PASS: Invalid species defaults to CERF")
    
    def test_month_boundary_1(self):
        """Month 1 (January) is valid"""
        payload = {
            "center_lat": 48.19,
            "center_lng": -68.39,
            "species": "CERF",
            "month": 1
        }
        response = requests.post(
            f"{BASE_URL}/api/v2/alimentation/analyze",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        print("PASS: Month 1 is valid")
    
    def test_month_boundary_12(self):
        """Month 12 (December) is valid"""
        payload = {
            "center_lat": 48.19,
            "center_lng": -68.39,
            "species": "CERF",
            "month": 12
        }
        response = requests.post(
            f"{BASE_URL}/api/v2/alimentation/analyze",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        print("PASS: Month 12 is valid")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
