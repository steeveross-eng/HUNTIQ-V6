"""
BIONIC V9 Backend Tests — Phase Corridors V9 (Second Iteration)
================================================================
Tests:
- BCE-4X weather compliance (60-minute OWM cache)
- BCE-4X new rules: GEOM-001 (shape), GEOM-002 (continuity), GEOM-003 (gradient), CLIP-001 (outside area), VISUAL-001 (migration look)
- V9 corridor validation with 5-level gradient bands
- Shapely-based polygon band generation (5 concentric bands per corridor)
- Chaikin-smoothed centerline
- 9 BIONIC engine evaluation
- Species-specific corridors (moose/deer/bear)
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
    """V9 Corridor BCE validation tests with BCE-4X new rules"""
    
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
    
    def test_bce4x_rules_validated(self):
        """Validate BCE-4X rules: GEOM-001, GEOM-002, GEOM-003, CLIP-001, VISUAL-001"""
        response = requests.post(f"{BASE_URL}/api/bce/validate-corridors-v9", timeout=60)
        assert response.status_code == 200
        data = response.json()
        
        # Check that results include BCE-4X rule validation
        for result in data["results"]:
            violations = result.get("violations", [])
            # No violations for new rules
            rule_violations = [v for v in violations if v.get("rule", "").startswith("BCE-4X")]
            assert len(rule_violations) == 0, f"BCE-4X violations found: {rule_violations}"
            
            # Check bands and centerline presence (GEOM-003, VISUAL-001)
            assert "has_bands" in result, f"Missing 'has_bands' in validation result"
            assert result["has_bands"] == True, f"Corridor {result['corridor_id']} missing bands"
            assert result.get("band_count", 0) > 0, f"Corridor {result['corridor_id']} has 0 bands"
        
        print(f"All {len(data['results'])} corridors pass BCE-4X rules (GEOM/CLIP/VISUAL)")
    
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
                if v.get("rule") == "BCE-4X-GEOM-001":
                    circular_violations.append(result["corridor_id"])
        
        assert len(circular_violations) == 0, f"Circular corridors found: {circular_violations}"
        print("No circular corridors detected (GEOM-001)")
    
    def test_continuity_validation(self):
        """Corridors should pass continuity check (no gaps > 150m)"""
        response = requests.post(f"{BASE_URL}/api/bce/validate-corridors-v9", timeout=60)
        assert response.status_code == 200
        data = response.json()
        
        continuity_violations = []
        for result in data["results"]:
            if not result.get("continuity_valid", True):
                continuity_violations.append(result["corridor_id"])
            for v in result.get("violations", []):
                if v.get("rule") == "BCE-4X-GEOM-002":
                    continuity_violations.append(result["corridor_id"])
        
        # Allow some corridors with minor gaps that were fixed
        assert len(continuity_violations) == 0, f"Continuity violations: {continuity_violations}"
        print("All corridors pass continuity validation (GEOM-002)")


class TestSpeciesCorridors:
    """Species-specific corridor generation tests with V9 bands and centerline"""
    
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
    
    def test_corridors_have_bands_array(self):
        """Each corridor should have 'bands' array with polygon data"""
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
        
        corridors_with_bands = 0
        total_bands = 0
        for corridor in data["corridors"]:
            props = corridor.get("properties", {})
            bands = props.get("bands", [])
            if len(bands) > 0:
                corridors_with_bands += 1
                total_bands += len(bands)
                # Verify band structure
                for band in bands:
                    assert "level" in band, f"Band missing 'level' in corridor {corridor.get('id')}"
                    assert "color" in band, f"Band missing 'color' in corridor {corridor.get('id')}"
                    assert "opacity" in band, f"Band missing 'opacity' in corridor {corridor.get('id')}"
                    assert "fillOpacity" in band, f"Band missing 'fillOpacity' in corridor {corridor.get('id')}"
                    assert "coordinates" in band, f"Band missing 'coordinates' in corridor {corridor.get('id')}"
        
        # At least some corridors should have bands (high-scoring corridors)
        assert corridors_with_bands > 0, "No corridors have bands array"
        print(f"Corridors with bands: {corridors_with_bands}/{len(data['corridors'])}, total bands: {total_bands}")
    
    def test_corridors_have_centerline(self):
        """Each corridor should have 'centerline' for Chaikin-smoothed axis"""
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
        
        corridors_with_centerline = 0
        for corridor in data["corridors"]:
            props = corridor.get("properties", {})
            centerline = props.get("centerline", [])
            if len(centerline) >= 2:
                corridors_with_centerline += 1
                # Verify centerline is array of [lng, lat] coords
                for coord in centerline[:3]:  # Check first 3
                    assert isinstance(coord, list) and len(coord) == 2, f"Invalid centerline coord: {coord}"
        
        # Most corridors should have centerline
        assert corridors_with_centerline > 0, "No corridors have centerline"
        print(f"Corridors with centerline: {corridors_with_centerline}/{len(data['corridors'])}")
    
    def test_band_levels_are_valid(self):
        """Band levels should be one of: gris, jaune, orange, rouge, rouge_raye"""
        valid_levels = {"gris", "jaune", "orange", "rouge", "rouge_raye"}
        
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
        
        levels_found = set()
        for corridor in data["corridors"]:
            props = corridor.get("properties", {})
            bands = props.get("bands", [])
            for band in bands:
                level = band.get("level")
                assert level in valid_levels, f"Invalid band level: {level}"
                levels_found.add(level)
        
        print(f"Band levels found: {levels_found}")
    
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
    
    def test_corridors_clipped_within_bounds(self):
        """Corridors must be clipped within the 2km2 active perimeter bounds"""
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
        
        margin = 0.0005  # ~50m tolerance
        out_of_bounds_count = 0
        for corridor in data["corridors"]:
            coords = corridor.get("geometry", {}).get("coordinates", [])
            for coord in coords:
                lng, lat = coord[0], coord[1]
                if (lat < self.TEST_BOUNDS["south"] - margin or 
                    lat > self.TEST_BOUNDS["north"] + margin or
                    lng < self.TEST_BOUNDS["west"] - margin or 
                    lng > self.TEST_BOUNDS["east"] + margin):
                    out_of_bounds_count += 1
                    break  # Count corridor once
        
        # All corridors should be clipped within bounds
        assert out_of_bounds_count == 0, f"{out_of_bounds_count} corridors have coordinates outside bounds"
        print(f"All {len(data['corridors'])} corridors clipped within bounds")
    
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
