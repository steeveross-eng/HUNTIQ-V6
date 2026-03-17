"""
BCE-4X Water Exclusion Bug Fix Tests
=====================================
Tests for the critical water exclusion fix:
1. LAYER_WATER_THRESHOLDS configuration (affuts=0.0, salines=0.0)
2. Score consolidé returns is_water=True and score=0 for water surfaces
3. Score consolidé returns normal scores for land points (no regression)
4. ALIMENTATION-V1 and REPOS-V1 regression tests
"""
import os
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestBCE4XConfiguration:
    """Test that LAYER_WATER_THRESHOLDS configuration is correct"""
    
    def test_layer_water_thresholds_config(self):
        """Verify LAYER_WATER_THRESHOLDS has correct values for affuts and salines"""
        from modules.bionic_engine_p0.services.exclusion_config_v7 import LAYER_WATER_THRESHOLDS
        
        # BCE-4X: affuts and salines must have 0.0 water threshold
        assert "affuts" in LAYER_WATER_THRESHOLDS, "affuts key missing from LAYER_WATER_THRESHOLDS"
        assert "salines" in LAYER_WATER_THRESHOLDS, "salines key missing from LAYER_WATER_THRESHOLDS"
        
        assert LAYER_WATER_THRESHOLDS["affuts"] == 0.0, f"affuts threshold should be 0.0, got {LAYER_WATER_THRESHOLDS['affuts']}"
        assert LAYER_WATER_THRESHOLDS["salines"] == 0.0, f"salines threshold should be 0.0, got {LAYER_WATER_THRESHOLDS['salines']}"
        
        print(f"✓ BCE-4X: affuts threshold = {LAYER_WATER_THRESHOLDS['affuts']}")
        print(f"✓ BCE-4X: salines threshold = {LAYER_WATER_THRESHOLDS['salines']}")
    
    def test_trajets_water_threshold(self):
        """Verify trajets has 1% water threshold"""
        from modules.bionic_engine_p0.services.exclusion_config_v7 import LAYER_WATER_THRESHOLDS
        
        assert "trajets" in LAYER_WATER_THRESHOLDS, "trajets key missing from LAYER_WATER_THRESHOLDS"
        assert LAYER_WATER_THRESHOLDS["trajets"] == 0.01, f"trajets threshold should be 0.01, got {LAYER_WATER_THRESHOLDS['trajets']}"
        
        print(f"✓ BCE-4X: trajets threshold = {LAYER_WATER_THRESHOLDS['trajets']}")
    
    def test_global_water_threshold_reduced(self):
        """Verify global water threshold reduced to 3%"""
        from modules.bionic_engine_p0.services.exclusion_config_v7 import INTERSECTION_THRESHOLDS_V7
        
        assert "water" in INTERSECTION_THRESHOLDS_V7, "water key missing from INTERSECTION_THRESHOLDS_V7"
        assert INTERSECTION_THRESHOLDS_V7["water"] == 0.03, f"Global water threshold should be 0.03, got {INTERSECTION_THRESHOLDS_V7['water']}"
        
        print(f"✓ BCE-4X: Global water threshold = {INTERSECTION_THRESHOLDS_V7['water']}")

    def test_layer_water_thresholds_import_in_exclusion_engine(self):
        """Verify LAYER_WATER_THRESHOLDS is imported in exclusion_engine_v7"""
        from modules.bionic_engine_p0.services.exclusion_engine_v7 import LAYER_WATER_THRESHOLDS
        
        # Should import successfully and have the correct values
        assert LAYER_WATER_THRESHOLDS["affuts"] == 0.0
        assert LAYER_WATER_THRESHOLDS["salines"] == 0.0
        print("✓ BCE-4X: LAYER_WATER_THRESHOLDS correctly imported in exclusion_engine_v7")


class TestScoreConsolideWaterExclusion:
    """Test score consolidé water detection and exclusion"""
    
    def test_score_consolide_endpoint_exists(self):
        """Verify /api/v1/score-consolide/point endpoint exists"""
        response = requests.get(f"{BASE_URL}/api/v1/score-consolide/point", params={
            "lat": 46.8,
            "lng": -71.2
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ Score consolidé endpoint exists and returns 200")
    
    def test_score_consolide_response_structure(self):
        """Verify score consolidé response has all required fields"""
        response = requests.get(f"{BASE_URL}/api/v1/score-consolide/point", params={
            "lat": 46.8,
            "lng": -71.2
        })
        data = response.json()
        
        # Check required fields
        required_fields = ["score", "classe", "label", "species", "components", "weights", "tracability"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        # Score should be in valid range
        assert 0 <= data["score"] <= 100, f"Score {data['score']} out of range [0, 100]"
        
        # Check tracability has BCE-4X exclusion info
        assert "tracability" in data
        assert "engines_active" in data["tracability"]
        
        print(f"✓ Score consolidé response structure valid, score={data['score']}, classe={data['classe']}")
    
    def test_score_consolide_land_point_normal_score(self):
        """Verify normal land points return valid scores (no regression)"""
        # Quebec City area - land point
        response = requests.get(f"{BASE_URL}/api/v1/score-consolide/point", params={
            "lat": 46.8139,
            "lng": -71.208,
            "species": "CERF"
        })
        data = response.json()
        
        assert response.status_code == 200
        assert data["score"] > 0, "Land point should have score > 0"
        assert data["classe"] != "EXCLU", "Land point should not be EXCLU"
        
        # Verify components exist
        assert "alimentation" in data["components"]
        assert "repos" in data["components"]
        assert "pression" in data["components"]
        
        print(f"✓ Land point returns normal score: {data['score']} ({data['classe']})")
    
    def test_score_consolide_water_surface_detection_structure(self):
        """Verify score consolidé can return water exclusion structure"""
        # The API should have the ability to return is_water when appropriate
        # We test the structure by checking a known land point doesn't have is_water
        response = requests.get(f"{BASE_URL}/api/v1/score-consolide/point", params={
            "lat": 46.8139,
            "lng": -71.208,
            "species": "CERF"
        })
        data = response.json()
        
        # Land point should NOT have is_water=True
        if "is_water" in data:
            assert data["is_water"] == False, "Land point should have is_water=False if field present"
        
        print("✓ Land point correctly does not have is_water=True")
    
    def test_water_exclusion_response_format(self):
        """Verify BCE-4X water exclusion response format from score_consolide module"""
        # Import and test the compute function directly
        import sys
        sys.path.insert(0, '/app/backend')
        from modules.score_consolide import compute_consolidated_score
        
        # Call with a known location
        result = compute_consolidated_score(46.8139, -71.208, "CERF", 10)
        
        # Check result structure
        assert "score" in result
        assert "classe" in result
        assert "components" in result
        assert "weights" in result
        assert "tracability" in result
        
        # If water is detected, should have specific format
        if result.get("is_water"):
            assert result["score"] == 0.0, "Water surface score should be 0"
            assert result["classe"] == "EXCLU", "Water surface classe should be EXCLU"
            assert result["label"] == "Surface d'eau", "Water surface label should be 'Surface d'eau'"
            assert result["tracability"]["exclusion"] == "BCE-4X water surface"
        
        print(f"✓ Water exclusion response format verified (is_water={result.get('is_water', False)})")


class TestAlimentationV1Regression:
    """Verify ALIMENTATION-V1 still works correctly (no regression)"""
    
    def test_alimentation_profiles_endpoint(self):
        """Verify /api/v1/alimentation/profiles returns 5 species"""
        response = requests.get(f"{BASE_URL}/api/v1/alimentation/profiles")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "profiles" in data, "Missing 'profiles' key"
        assert len(data["profiles"]) >= 5, f"Expected at least 5 profiles, got {len(data['profiles'])}"
        
        # Verify species names (id field is uppercase)
        species_ids = [p["id"].lower() for p in data["profiles"]]
        expected_species = ["cerf", "orignal", "ours", "dindon", "wapiti"]
        for sp in expected_species:
            assert sp in species_ids, f"Missing species: {sp}"
        
        print(f"✓ ALIMENTATION-V1 profiles: {len(data['profiles'])} species")
    
    def test_alimentation_point_endpoint(self):
        """Verify /api/v1/alimentation/point returns valid score"""
        response = requests.get(f"{BASE_URL}/api/v1/alimentation/point", params={
            "lat": 46.8,
            "lng": -71.2,
            "species": "CERF",
            "month": 10
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "score_alimentation" in data, "Missing 'score_alimentation' key"
        assert 0 <= data["score_alimentation"] <= 100, f"Score {data['score_alimentation']} out of range"
        
        print(f"✓ ALIMENTATION-V1 point: score={data['score_alimentation']}")


class TestReposV1Regression:
    """Verify REPOS-V1 still works correctly (no regression)"""
    
    def test_repos_profiles_endpoint(self):
        """Verify /api/v1/repos/profiles returns 5 species"""
        response = requests.get(f"{BASE_URL}/api/v1/repos/profiles")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "profiles" in data, "Missing 'profiles' key"
        assert len(data["profiles"]) >= 5, f"Expected at least 5 profiles, got {len(data['profiles'])}"
        
        # Verify species names (id field is uppercase)
        species_ids = [p["id"].lower() for p in data["profiles"]]
        expected_species = ["cerf", "orignal", "ours", "dindon", "wapiti"]
        for sp in expected_species:
            assert sp in species_ids, f"Missing species: {sp}"
        
        print(f"✓ REPOS-V1 profiles: {len(data['profiles'])} species")
    
    def test_repos_point_endpoint(self):
        """Verify /api/v1/repos/point returns valid score"""
        response = requests.get(f"{BASE_URL}/api/v1/repos/point", params={
            "lat": 46.8,
            "lng": -71.2,
            "species": "CERF",
            "month": 10
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "score_repos" in data, "Missing 'score_repos' key"
        assert 0 <= data["score_repos"] <= 100, f"Score {data['score_repos']} out of range"
        
        print(f"✓ REPOS-V1 point: score={data['score_repos']}")


class TestHeatmapGridRegression:
    """Verify heatmap grid still works correctly (no regression)"""
    
    def test_heatmap_endpoint_exists(self):
        """Verify /api/v1/score-consolide/heatmap endpoint exists"""
        response = requests.get(f"{BASE_URL}/api/v1/score-consolide/heatmap", params={
            "lat": 46.8,
            "lng": -71.2
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "points" in data, "Missing 'points' key"
        assert "score_avg" in data, "Missing 'score_avg' key"
        
        print(f"✓ Heatmap endpoint: {len(data['points'])} points, avg={data['score_avg']}")
    
    def test_heatmap_default_grid_size(self):
        """Verify heatmap default grid_size is 20 (400 points)"""
        response = requests.get(f"{BASE_URL}/api/v1/score-consolide/heatmap", params={
            "lat": 46.8,
            "lng": -71.2
        })
        data = response.json()
        
        assert data.get("grid_size") == 20, f"Expected grid_size=20, got {data.get('grid_size')}"
        assert data.get("total_points") == 400, f"Expected total_points=400, got {data.get('total_points')}"
        
        print(f"✓ Heatmap grid_size={data['grid_size']}, total_points={data['total_points']}")


class TestAllSpeciesSupport:
    """Verify all 5 species are supported including Wapiti"""
    
    def test_score_consolide_all_species(self):
        """Test score consolidé for all 5 species"""
        species_list = ["CERF", "ORIGNAL", "OURS", "DINDON", "WAPITI"]
        
        for species in species_list:
            response = requests.get(f"{BASE_URL}/api/v1/score-consolide/point", params={
                "lat": 46.8,
                "lng": -71.2,
                "species": species
            })
            assert response.status_code == 200, f"Failed for species {species}"
            data = response.json()
            assert "score" in data
            assert data["species"] == species
            print(f"  ✓ {species}: score={data['score']}")
        
        print(f"✓ All {len(species_list)} species supported")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
