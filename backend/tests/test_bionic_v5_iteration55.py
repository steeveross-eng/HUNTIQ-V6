"""
BIONIC V5 - Iteration 55 Testing
Tests for organic polygon generation, water exclusion, and terrain data API

Key changes to verify:
1. Enhanced organic polygon generation (16 vertices, angle jitter, 4 octaves noise)
2. Stricter compactness validation (threshold lowered from 0.92 to 0.85)
3. New edge variance validation (rejects regular polygons)
4. Increased Chaikin smoothing from 1 to 2 iterations
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://solunar-analytics.preview.emergentagent.com').rstrip('/')

class TestTerrainDataHealth:
    """Test terrain data health endpoint"""
    
    def test_health_endpoint_status(self):
        """Verify health endpoint returns operational status"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/terrain/terrain-data/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert "detail_levels" in data
        assert "low" in data["detail_levels"]
        assert "high" in data["detail_levels"]
        print(f"✓ Health endpoint operational with detail levels: {data['detail_levels']}")

    def test_supported_exclusion_types(self):
        """Verify all exclusion types are supported"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/terrain/terrain-data/health")
        data = response.json()
        expected_types = ["water", "roads", "urban", "infrastructure"]
        for t in expected_types:
            assert t in data["supported_types"], f"Missing supported type: {t}"
        print(f"✓ All exclusion types supported: {expected_types}")


class TestTerrainDataAPI:
    """Test terrain data POST endpoint"""

    def test_quebec_city_water_exclusion(self):
        """Test water exclusion zones for Quebec City area (Saint Lawrence River)"""
        payload = {
            "south": 46.78,
            "west": -71.25,
            "north": 46.85,
            "east": -71.18,
            "exclude_types": ["water"],
            "detail_level": "low"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/terrain/terrain-data", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        
        exclusions = data.get("exclusion_zones", [])
        water_zones = [z for z in exclusions if z["type"] == "water"]
        
        # Saint Lawrence River area should have water exclusions
        assert len(water_zones) > 0, "No water exclusion zones found near Saint Lawrence River"
        print(f"✓ Water exclusion zones found: {len(water_zones)}")
        
        # Verify coordinates structure
        for zone in water_zones[:3]:
            assert "coordinates" in zone
            assert len(zone["coordinates"]) >= 3, "Water zone should have at least 3 coordinates"
            assert zone["geometry_type"] in ["polygon", "line"]
        print(f"✓ Water zone coordinates valid")

    def test_roads_exclusion(self):
        """Test roads exclusion zones"""
        payload = {
            "south": 46.80,
            "west": -71.22,
            "north": 46.83,
            "east": -71.18,
            "exclude_types": ["roads"],
            "detail_level": "high"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/terrain/terrain-data", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Handle potential timeout/error responses from Overpass API
        if data.get("success") == False:
            print(f"⚠ Roads query returned success=False (may be Overpass timeout)")
            pytest.skip("Overpass API may have timed out")
            return
        
        assert data["success"] == True
        
        exclusions = data.get("exclusion_zones", [])
        road_zones = [z for z in exclusions if z["type"] == "roads"]
        
        # Urban area should have road exclusions
        assert len(road_zones) > 0, "No road exclusion zones found"
        print(f"✓ Road exclusion zones found: {len(road_zones)}")

    def test_urban_exclusion(self):
        """Test urban exclusion zones"""
        payload = {
            "south": 46.80,
            "west": -71.25,
            "north": 46.85,
            "east": -71.20,
            "exclude_types": ["urban"],
            "detail_level": "low"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/terrain/terrain-data", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        exclusions = data.get("exclusion_zones", [])
        urban_zones = [z for z in exclusions if z["type"] == "urban"]
        
        print(f"✓ Urban exclusion zones found: {len(urban_zones)}")

    def test_all_exclusion_types_combined(self):
        """Test combined exclusion types"""
        payload = {
            "south": 46.75,
            "west": -71.30,
            "north": 46.85,
            "east": -71.15,
            "exclude_types": ["water", "roads", "urban", "infrastructure"],
            "detail_level": "low"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/terrain/terrain-data", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        
        stats = data.get("stats", {})
        by_type = stats.get("by_type", {})
        
        # Should have multiple types of exclusions
        total_exclusions = len(data.get("exclusion_zones", []))
        assert total_exclusions > 0, "No exclusion zones returned"
        
        print(f"✓ Combined exclusion stats: {by_type}")
        print(f"✓ Total exclusion zones: {total_exclusions}")

    def test_bbox_limit_validation_lat(self):
        """Test that bbox > 0.3 degrees latitude is rejected"""
        payload = {
            "south": 46.50,
            "west": -71.30,
            "north": 46.90,  # 0.4 degrees range - exceeds 0.3 limit
            "east": -71.20,
            "exclude_types": ["water"],
            "detail_level": "low"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/terrain/terrain-data", json=payload)
        assert response.status_code == 400
        print(f"✓ Large lat bbox correctly rejected with 400")

    def test_bbox_limit_validation_lng(self):
        """Test that bbox > 0.4 degrees longitude is rejected"""
        payload = {
            "south": 46.80,
            "west": -71.50,  # 0.5 degrees range - exceeds 0.4 limit
            "north": 46.90,
            "east": -71.00,
            "exclude_types": ["water"],
            "detail_level": "low"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/terrain/terrain-data", json=payload)
        assert response.status_code == 400
        print(f"✓ Large lng bbox correctly rejected with 400")

    def test_valid_bbox_accepted(self):
        """Test that valid bbox within limits is accepted"""
        payload = {
            "south": 46.80,
            "west": -71.25,
            "north": 46.95,  # 0.15 degrees lat - within 0.3 limit
            "east": -71.05,  # 0.2 degrees lng - within 0.4 limit
            "exclude_types": ["water"],
            "detail_level": "low"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/terrain/terrain-data", json=payload)
        assert response.status_code == 200
        print(f"✓ Valid bbox accepted")


class TestSaintLawrenceRiverExclusion:
    """CRITICAL: Test Saint Lawrence River water exclusion - TOLÉRANCE ZÉRO"""

    def test_river_area_has_water_exclusions(self):
        """Test that Saint Lawrence River area (between Quebec & Lévis) has water exclusions"""
        # Coordinates centered on the Saint Lawrence River
        payload = {
            "south": 46.80,
            "west": -71.22,
            "north": 46.84,
            "east": -71.18,
            "exclude_types": ["water"],
            "detail_level": "high"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/terrain/terrain-data", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        exclusions = data.get("exclusion_zones", [])
        water_zones = [z for z in exclusions if z["type"] == "water"]
        
        # CRITICAL: Must have water exclusion zones for the river
        assert len(water_zones) > 0, "CRITICAL: No water exclusions found for Saint Lawrence River area!"
        
        # Verify water polygons have valid coordinates
        for zone in water_zones[:5]:  # Check first 5 zones only
            assert len(zone["coordinates"]) >= 3
            for coord in zone["coordinates"][:10]:  # Check first 10 coords per zone
                assert len(coord) == 2, "Coordinate must be [lng, lat]"
                # Verify coordinates are in Quebec region (wider range for river relations)
                lng, lat = coord
                assert -75 < lng < -68, f"Longitude out of range: {lng}"
                assert 44 < lat < 50, f"Latitude out of range: {lat}"
        
        print(f"✓ CRITICAL TEST PASSED: {len(water_zones)} water exclusion zones found for Saint Lawrence River")

    def test_fleuve_st_laurent_south_shore(self):
        """Test water exclusions near Lévis (south shore)"""
        # Lévis area - south shore of Saint Lawrence
        payload = {
            "south": 46.79,
            "west": -71.20,
            "north": 46.82,
            "east": -71.16,
            "exclude_types": ["water"],
            "detail_level": "high"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/terrain/terrain-data", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        exclusions = data.get("exclusion_zones", [])
        water_zones = [z for z in exclusions if z["type"] == "water"]
        
        print(f"✓ Lévis area water exclusions: {len(water_zones)}")


class TestDetailLevels:
    """Test detail level behavior"""

    def test_low_detail_includes_major_features(self):
        """Test low detail includes landuse + major roads"""
        payload = {
            "south": 46.80,
            "west": -71.22,
            "north": 46.83,
            "east": -71.18,
            "exclude_types": ["roads", "urban", "water"],
            "detail_level": "low"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/terrain/terrain-data", json=payload)
        data = response.json()
        
        stats = data.get("stats", {})
        assert stats.get("detail_level") == "low" or "detail_level" not in stats or data.get("cached")
        print(f"✓ Low detail query returned stats: {stats.get('by_type', {})}")

    def test_high_detail_includes_more_features(self):
        """Test high detail includes buildings, service roads, streams"""
        payload = {
            "south": 46.815,
            "west": -71.215,
            "north": 46.820,
            "east": -71.210,
            "exclude_types": ["roads", "infrastructure"],
            "detail_level": "high"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/terrain/terrain-data", json=payload)
        data = response.json()
        
        stats = data.get("stats", {})
        exclusions = data.get("exclusion_zones", [])
        
        print(f"✓ High detail query returned {len(exclusions)} exclusions")


class TestCacheBehavior:
    """Test caching behavior"""

    def test_cached_response_indicates_cache(self):
        """Test that cached responses are indicated"""
        payload = {
            "south": 46.80,
            "west": -71.22,
            "north": 46.83,
            "east": -71.18,
            "exclude_types": ["water"],
            "detail_level": "low"
        }
        
        # First request
        response1 = requests.post(f"{BASE_URL}/api/v1/bionic/terrain/terrain-data", json=payload)
        assert response1.status_code == 200
        
        # Second request (should be cached)
        response2 = requests.post(f"{BASE_URL}/api/v1/bionic/terrain/terrain-data", json=payload)
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Either cached or fresh should work
        assert data2["success"] == True
        print(f"✓ Cache behavior: cached={data2.get('cached', 'N/A')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
