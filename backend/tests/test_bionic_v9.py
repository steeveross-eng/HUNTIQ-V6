"""
BIONIC V9 Backend Tests — Phase Corridors V9
=============================================
Tests BCE-4X weather compliance, V9 corridor validation, 
9 BIONIC engine evaluation, and species-specific corridors.
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestBCE4XWeatherCompliance:
    """BCE-4X Weather Engine 60-minute cache compliance tests"""
    
    def test_weather_compliance_endpoint_returns_valid_structure(self):
        """GET /api/bce/weather-compliance returns proper structure"""
        response = requests.get(f"{BASE_URL}/api/bce/weather-compliance")
        assert response.status_code == 200
        data = response.json()
        
        # Required fields
        assert "rule" in data
        assert data["rule"] == "weather_60min"
        assert "compliant" in data
        assert "cache_active" in data
        assert "source" in data
        assert "elapsed_s" in data
        assert "ttl_remaining_s" in data
        assert "update_blocked" in data
        assert "next_update_in_s" in data
        assert "bce_compliant" in data or data["compliant"] is not None
        
        # BCE compliance must always be true
        assert data["compliant"] == True
        print(f"Weather compliance: compliant={data['compliant']}, cache_active={data['cache_active']}, update_blocked={data['update_blocked']}")
    
    def test_weather_cache_blocks_updates_within_60min(self):
        """After first call, update_blocked should be true within 60 min"""
        # First call - may trigger OWM fetch
        response1 = requests.get(f"{BASE_URL}/api/bce/weather-compliance")
        assert response1.status_code == 200
        
        # Short wait
        time.sleep(2)
        
        # Second call - should show blocked
        response2 = requests.get(f"{BASE_URL}/api/bce/weather-compliance")
        assert response2.status_code == 200
        data2 = response2.json()
        
        # If cache is active, updates should be blocked
        if data2["cache_active"]:
            assert data2["update_blocked"] == True
            assert data2["next_update_in_s"] > 0
            print(f"Cache active: update_blocked={data2['update_blocked']}, next_update_in_s={data2['next_update_in_s']}")
        else:
            print("Cache not active (first fetch scenario)")


class TestBCE4XRegistry:
    """BCE-4X Registry tests for all 9 BIONIC engines"""
    
    def test_registry_returns_16_modules(self):
        """GET /api/bce/registry returns 16 total modules with all 9 engines active"""
        response = requests.get(f"{BASE_URL}/api/bce/registry")
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_modules"] == 16
        assert len(data["uncovered_active"]) == 0  # No uncovered active modules
        print(f"Total modules: {data['total_modules']}, uncovered_active: {data['uncovered_active']}")
    
    def test_all_9_bionic_engines_active(self):
        """All 9 BIONIC engines should be active in registry"""
        response = requests.get(f"{BASE_URL}/api/bce/registry")
        assert response.status_code == 200
        data = response.json()
        
        required_engines = {
            "nutrition_engine", "daily_routine_engine", "weather_engine",
            "disturbance_engine", "movement_engine", "phenology_engine",
            "typology_engine", "learning_engine", "habitat_enhancement_engine"
        }
        
        modules = data["modules"]
        for engine in required_engines:
            assert engine in modules, f"Missing engine: {engine}"
            assert modules[engine]["status"] == "active", f"Engine {engine} not active"
            assert modules[engine]["validator"] != "pending", f"Engine {engine} has pending validator"
        
        print(f"All 9 engines active: {list(required_engines)}")


class TestV9CorridorValidation:
    """V9 Corridor BCE validation tests"""
    
    def test_validate_corridors_v9_100_percent_compliance(self):
        """POST /api/bce/validate-corridors-v9 should return 100% compliance"""
        response = requests.post(f"{BASE_URL}/api/bce/validate-corridors-v9", timeout=60)
        assert response.status_code == 200
        data = response.json()
        
        assert "compliance_rate" in data
        assert data["compliance_rate"] == 100.0
        assert data["status"] == "COMPLIANT"
        assert data["total_violations"] == 0
        
        print(f"V9 Compliance: {data['compliance_rate']}%, total_corridors={data['total_corridors']}")
    
    def test_corridors_have_9_engines_evaluated(self):
        """Each corridor should have all 9 engines evaluated"""
        response = requests.post(f"{BASE_URL}/api/bce/validate-corridors-v9", timeout=60)
        assert response.status_code == 200
        data = response.json()
        
        for result in data["results"]:
            assert result["engines_evaluated"] == 9, f"Corridor {result['corridor_id']} has {result['engines_evaluated']} engines instead of 9"
        
        print(f"All {len(data['results'])} corridors have 9 engines evaluated")
    
    def test_v9_classification_levels_present(self):
        """V9 corridors should have 5-level classification (gris/jaune/orange/rouge/rouge_raye)"""
        response = requests.post(f"{BASE_URL}/api/bce/validate-corridors-v9", timeout=60)
        assert response.status_code == 200
        data = response.json()
        
        valid_levels = {"gris", "jaune", "orange", "rouge", "rouge_raye"}
        levels_found = set()
        
        for result in data["results"]:
            level = result["classification_level"]
            assert level in valid_levels, f"Invalid classification level: {level}"
            levels_found.add(level)
        
        print(f"Classification levels found: {levels_found}")
    
    def test_no_circular_corridors(self):
        """No corridor should be circular (start-end distance >= 50m)"""
        response = requests.post(f"{BASE_URL}/api/bce/validate-corridors-v9", timeout=60)
        assert response.status_code == 200
        data = response.json()
        
        circular_violations = []
        for result in data["results"]:
            for v in result.get("violations", []):
                if v.get("rule") == "non_circular":
                    circular_violations.append(result["corridor_id"])
        
        assert len(circular_violations) == 0, f"Circular corridors found: {circular_violations}"
        print("No circular corridors detected")


class TestSpeciesCorridors:
    """Species-specific corridor generation tests"""
    
    TEST_BOUNDS = {
        "north": 46.96, "south": 46.93,
        "east": -71.27, "west": -71.33
    }
    
    def test_moose_corridors_generation(self):
        """POST /api/v1/bionic/corridors-v9/by-species for moose"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/corridors-v9/by-species",
            json={
                "bounds": self.TEST_BOUNDS,
                "species": "moose",
                "resolution": 40
            },
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["species"] == "moose"
        assert data["total_corridors"] > 0
        assert "classification_v9" in data
        assert "engine_averages" in data
        assert data["bce_validation"]["status"] == "COMPLIANT"
        
        # Verify all 9 engines have averages
        assert len(data["engine_averages"]) == 9
        print(f"Moose: {data['total_corridors']} corridors, classification: {data['classification_v9']}")
    
    def test_deer_corridors_generation(self):
        """POST /api/v1/bionic/corridors-v9/by-species for deer"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/corridors-v9/by-species",
            json={
                "bounds": self.TEST_BOUNDS,
                "species": "deer",
                "resolution": 40
            },
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["species"] == "deer"
        assert data["total_corridors"] > 0
        assert data["bce_validation"]["status"] == "COMPLIANT"
        print(f"Deer: {data['total_corridors']} corridors, classification: {data['classification_v9']}")
    
    def test_bear_corridors_generation(self):
        """POST /api/v1/bionic/corridors-v9/by-species for bear"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/corridors-v9/by-species",
            json={
                "bounds": self.TEST_BOUNDS,
                "species": "bear",
                "resolution": 40
            },
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["species"] == "bear"
        assert data["total_corridors"] > 0
        assert data["bce_validation"]["status"] == "COMPLIANT"
        print(f"Bear: {data['total_corridors']} corridors, classification: {data['classification_v9']}")
    
    def test_corridors_have_v9_subscores(self):
        """Each corridor should have subscores for all 9 engines"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/corridors-v9/by-species",
            json={
                "bounds": self.TEST_BOUNDS,
                "species": "moose",
                "resolution": 40
            },
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        
        required_engines = {
            "nutrition", "daily_routine", "weather", "disturbance",
            "movement", "phenology", "typology", "learning", "habitat_enhancement"
        }
        
        for corridor in data["corridors"][:5]:  # Check first 5
            subscores = corridor["properties"]["scoring"]["subscores"]
            for engine in required_engines:
                assert engine in subscores, f"Missing engine {engine} in corridor {corridor['id']}"
                assert isinstance(subscores[engine], (int, float)), f"Engine {engine} score not numeric"
        
        print("All corridors have valid subscores for 9 engines")


class TestEngineScoreDynamics:
    """Tests that engine scores are dynamic (not hardcoded)"""
    
    def test_scores_vary_by_species(self):
        """Engine scores should differ between moose and deer"""
        bounds = {"north": 46.96, "south": 46.93, "east": -71.27, "west": -71.33}
        
        moose_response = requests.post(
            f"{BASE_URL}/api/v1/bionic/corridors-v9/by-species",
            json={"bounds": bounds, "species": "moose", "resolution": 40},
            timeout=60
        )
        deer_response = requests.post(
            f"{BASE_URL}/api/v1/bionic/corridors-v9/by-species",
            json={"bounds": bounds, "species": "deer", "resolution": 40},
            timeout=60
        )
        
        moose_data = moose_response.json()
        deer_data = deer_response.json()
        
        # Compare engine averages - at least some should differ
        moose_avgs = moose_data["engine_averages"]
        deer_avgs = deer_data["engine_averages"]
        
        differences = 0
        for engine in moose_avgs:
            if abs(moose_avgs[engine] - deer_avgs[engine]) > 0.1:
                differences += 1
        
        assert differences > 0, "Engine scores are identical for different species - may be hardcoded"
        print(f"Found {differences} engine score differences between moose and deer")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
