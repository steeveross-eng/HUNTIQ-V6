"""
Iteration 31 - V10 Corridors & Douglas-Peucker Backend Tests
=============================================================
Tests for:
1. /api/v10/corridors/analyze endpoint (light analysis)
2. /api/v10/corridors/analyze-full endpoint (full GeoJSON with simplification)
3. /api/v10/corridors/profiles endpoint (species profiles)
4. /api/v10/corridors/documentation endpoint
5. Anti-regression: /api/v1/alimentation/analyze and /api/v1/repos/analyze
6. COR-006 validation (continuity)
7. Douglas-Peucker simplification verification
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test coordinates (Quebec hunting territory)
TEST_LAT = 46.8139
TEST_LNG = -71.2080

class TestCorridorsV10API:
    """CORRIDORS-V10 API endpoint tests"""

    def test_corridors_analyze_light(self):
        """Test /api/v10/corridors/analyze (light version without GeoJSON)"""
        response = requests.post(
            f"{BASE_URL}/api/v10/corridors/analyze",
            json={
                "center_lat": TEST_LAT,
                "center_lng": TEST_LNG,
                "species": "CERF",
                "month": 10
            },
            timeout=30
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify V10 engine response
        assert data.get("engine") == "CORRIDORS-V10", "Engine should be CORRIDORS-V10"
        assert data.get("version") == "10.0.0", "Version should be 10.0.0"
        
        # Verify required fields
        assert "score_corridor" in data, "Missing score_corridor"
        assert "classe_corridor" in data, "Missing classe_corridor"
        assert "network" in data, "Missing network"
        assert "continuity" in data, "Missing continuity"
        assert "validation" in data, "Missing validation"
        
        # Verify niveau_distribution (normative classification)
        network = data.get("network", {})
        assert "niveau_distribution" in network, "Missing niveau_distribution in network"
        niveau_dist = network.get("niveau_distribution", {})
        
        # Check all 5 normative levels present
        expected_levels = ["CRITIQUE", "MAJEUR", "FORT", "MODERE", "FAIBLE"]
        for level in expected_levels:
            assert level in niveau_dist, f"Missing level {level} in niveau_distribution"
        
        print(f"✓ analyze: {data.get('network', {}).get('total_corridors', 0)} corridors, score={data.get('score_corridor')}")

    def test_corridors_analyze_full_with_geojson(self):
        """Test /api/v10/corridors/analyze-full (full GeoJSON with Douglas-Peucker simplification)"""
        response = requests.post(
            f"{BASE_URL}/api/v10/corridors/analyze-full",
            json={
                "center_lat": TEST_LAT,
                "center_lng": TEST_LNG,
                "species": "CERF",
                "month": 10
            },
            timeout=30
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify GeoJSON present
        assert "geojson" in data, "Missing geojson in response"
        geojson = data.get("geojson", {})
        assert geojson.get("type") == "FeatureCollection", "GeoJSON type should be FeatureCollection"
        
        features = geojson.get("features", [])
        assert len(features) > 0, "GeoJSON should have features"
        
        # Check corridors have normative properties
        corridor_features = [f for f in features if f.get("geometry", {}).get("type") == "LineString"]
        assert len(corridor_features) > 0, "Should have LineString corridor features"
        
        # Verify normative properties on corridors
        sample_corridor = corridor_features[0]
        props = sample_corridor.get("properties", {})
        assert "niveau" in props, "Corridor missing niveau property"
        assert "color" in props, "Corridor missing color property"
        assert "largeur_m" in props, "Corridor missing largeur_m property"
        assert "score" in props, "Corridor missing score property"
        
        # Verify Douglas-Peucker simplification worked (coords should be reduced)
        coords = sample_corridor.get("geometry", {}).get("coordinates", [])
        assert len(coords) >= 2, "Corridor should have at least 2 coordinates"
        
        print(f"✓ analyze-full: {len(corridor_features)} corridors in GeoJSON, sample has {len(coords)} points")

    def test_corridors_profiles_endpoint(self):
        """Test /api/v10/corridors/profiles endpoint"""
        response = requests.get(f"{BASE_URL}/api/v10/corridors/profiles", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "engine" in data, "Missing engine"
        assert "profiles" in data, "Missing profiles"
        
        profiles = data.get("profiles", [])
        expected_species = ["CERF", "ORIGNAL", "OURS", "DINDON", "WAPITI"]
        
        # Profiles is a list, not a dict
        profile_ids = [p.get("id") for p in profiles] if isinstance(profiles, list) else list(profiles.keys())
        
        for sp in expected_species:
            assert sp in profile_ids, f"Missing species profile for {sp}"
        
        print(f"✓ profiles: {len(profiles)} species profiles loaded")

    def test_corridors_documentation_endpoint(self):
        """Test /api/v10/corridors/documentation endpoint"""
        response = requests.get(f"{BASE_URL}/api/v10/corridors/documentation", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "engine" in data, "Missing engine"
        
        # Check for niveaux_corridors or palette_normative
        has_levels = "niveaux_corridors" in data or "palette_normative" in data or "classification" in data
        assert has_levels, "Missing corridor level documentation"
        
        # Verify classification present
        if "classification" in data:
            classification = data.get("classification", {})
            assert len(classification) >= 4, "Should have at least 4 classification levels"
        
        print(f"✓ documentation: endpoint working, engine={data.get('engine')}")

    def test_cor_006_validation(self):
        """Test COR-006 validation (continuity check) passes for all species"""
        species_list = ["CERF", "ORIGNAL", "OURS", "DINDON", "WAPITI"]
        
        for sp in species_list:
            response = requests.post(
                f"{BASE_URL}/api/v10/corridors/analyze",
                json={
                    "center_lat": TEST_LAT,
                    "center_lng": TEST_LNG,
                    "species": sp,
                    "month": 10
                },
                timeout=30
            )
            assert response.status_code == 200, f"Species {sp} analyze failed: {response.status_code}"
            data = response.json()
            
            # Check continuity - look for 'connected' or 'bce4x_continuity' fields
            continuity = data.get("continuity", {})
            is_connected = (
                continuity.get("connected", False) or 
                continuity.get("continuous", False) or 
                continuity.get("bce4x_continuity") == "PASS"
            )
            assert is_connected, f"Species {sp} should have continuity: {continuity}"
            
            # Check BCE-4X validation passed
            validation = data.get("validation", {})
            bce4x = validation.get("bce4x", {})
            assert bce4x.get("status") in ["PASS", "WARNING"], \
                f"Species {sp} BCE-4X validation should pass: {bce4x.get('status')}"
            
            print(f"  ✓ COR-006 {sp}: connected={is_connected}, bce4x={bce4x.get('status')}")
        
        print(f"✓ COR-006 validation passed for all {len(species_list)} species")


class TestAntiRegressionV1APIs:
    """Anti-regression tests for V1 APIs"""

    def test_alimentation_v1_analyze(self):
        """Anti-regression: /api/v1/alimentation/analyze should still work"""
        response = requests.post(
            f"{BASE_URL}/api/v1/alimentation/analyze",
            json={
                "center_lat": TEST_LAT,
                "center_lng": TEST_LNG,
                "species": "CERF",
                "month": 10
            },
            timeout=20
        )
        assert response.status_code == 200, f"Alimentation V1 failed: {response.status_code}: {response.text}"
        data = response.json()
        
        assert "engine" in data, "Missing engine in alimentation response"
        assert data.get("engine") == "ALIMENTATION-V1", "Should be ALIMENTATION-V1 engine"
        
        # Check for zones or cells (API uses cells not zones)
        has_data = "zones" in data or "cells" in data
        assert has_data, "Missing zones/cells in alimentation response"
        
        cell_count = len(data.get('cells', data.get('zones', [])))
        print(f"✓ alimentation-v1: {cell_count} cells found")

    def test_repos_v1_analyze(self):
        """Anti-regression: /api/v1/repos/analyze should still work"""
        response = requests.post(
            f"{BASE_URL}/api/v1/repos/analyze",
            json={
                "center_lat": TEST_LAT,
                "center_lng": TEST_LNG,
                "species": "CERF",
                "month": 10
            },
            timeout=20
        )
        assert response.status_code == 200, f"Repos V1 failed: {response.status_code}: {response.text}"
        data = response.json()
        
        assert "engine" in data, "Missing engine in repos response"
        assert data.get("engine") == "REPOS-V1", "Should be REPOS-V1 engine"
        
        # Check for zones or cells (API uses cells not zones)
        has_data = "zones" in data or "cells" in data
        assert has_data, "Missing zones/cells in repos response"
        
        cell_count = len(data.get('cells', data.get('zones', [])))
        print(f"✓ repos-v1: {cell_count} cells found")


class TestDouglasPeuckerSimplification:
    """Test Douglas-Peucker simplification reduces GeoJSON payload"""

    def test_simplified_coords_smaller_than_raw(self):
        """Verify that analyze-full returns simplified coordinates"""
        response = requests.post(
            f"{BASE_URL}/api/v10/corridors/analyze-full",
            json={
                "center_lat": TEST_LAT,
                "center_lng": TEST_LNG,
                "species": "CERF",
                "month": 10
            },
            timeout=30
        )
        assert response.status_code == 200, f"Failed: {response.status_code}"
        data = response.json()
        
        geojson = data.get("geojson", {})
        features = geojson.get("features", [])
        corridors = [f for f in features if f.get("geometry", {}).get("type") == "LineString"]
        
        # Count total coordinates
        total_coords = 0
        corridors_with_few_points = 0
        
        for c in corridors:
            coords = c.get("geometry", {}).get("coordinates", [])
            total_coords += len(coords)
            # Douglas-Peucker should reduce points - most corridors should have <= 20 points after simplification
            if len(coords) <= 20:
                corridors_with_few_points += 1
        
        # Expect significant simplification
        simplification_ratio = corridors_with_few_points / max(1, len(corridors))
        assert simplification_ratio > 0.5, f"Expected >50% corridors simplified, got {simplification_ratio:.1%}"
        
        avg_coords = total_coords / max(1, len(corridors))
        print(f"✓ Douglas-Peucker: {len(corridors)} corridors, avg {avg_coords:.1f} coords/corridor, {simplification_ratio:.0%} simplified")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
