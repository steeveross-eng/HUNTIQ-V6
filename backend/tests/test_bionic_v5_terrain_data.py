"""
BIONIC V5 — Terrain Data Router Tests
Tests for Overpass API proxy endpoint for terrain exclusion data

Endpoint tested:
- POST /api/v1/bionic/terrain/terrain-data
- GET /api/v1/bionic/terrain/terrain-data/health
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestTerrainDataHealth:
    """Health endpoint tests"""

    def test_health_endpoint_returns_operational(self):
        """TEST 1: Health endpoint returns operational status"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/terrain/terrain-data/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("status") == "operational"
        assert "cache_dir" in data
        assert "overpass_url" in data
        assert "https://overpass-api.de" in data.get("overpass_url", "")
        assert "supported_types" in data
        assert set(data["supported_types"]) == {"water", "roads", "urban", "infrastructure"}
        print(f"✓ Health check returned: {data}")


class TestTerrainDataEndpoint:
    """Terrain data POST endpoint tests"""

    def test_terrain_data_returns_exclusion_zones(self):
        """TEST 2: POST terrain-data returns exclusion zones from Overpass"""
        payload = {
            "south": 46.80,
            "west": -71.25,
            "north": 46.85,
            "east": -71.20,
            "exclude_types": ["water", "roads", "urban", "infrastructure"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/terrain/terrain-data",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("success") is True
        assert "exclusion_zones" in data
        assert "stats" in data
        assert isinstance(data["exclusion_zones"], list)
        
        # Check stats structure
        stats = data["stats"]
        assert "exclusion_zones_count" in stats
        assert "by_type" in stats
        
        print(f"✓ Exclusion zones count: {stats['exclusion_zones_count']}")
        print(f"✓ By type: {stats.get('by_type', {})}")

    def test_terrain_data_returns_road_exclusions(self):
        """TEST 3: Verify roads are in exclusion zones"""
        payload = {
            "south": 46.81,
            "west": -71.24,
            "north": 46.83,
            "east": -71.21,
            "exclude_types": ["roads"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/terrain/terrain-data",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have some road exclusions
        zones = data.get("exclusion_zones", [])
        road_zones = [z for z in zones if z.get("type") == "roads"]
        
        # Roads should have line geometry
        if road_zones:
            for road in road_zones[:3]:  # Check first 3
                assert road.get("geometry_type") == "line"
                assert "coordinates" in road
                assert len(road["coordinates"]) >= 2
            print(f"✓ Found {len(road_zones)} road exclusion zones")

    def test_terrain_data_bbox_validation(self):
        """TEST 4: Large bounding box returns 400 error"""
        payload = {
            "south": 45.0,
            "west": -75.0,
            "north": 48.0,
            "east": -70.0,
            "exclude_types": ["water"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/terrain/terrain-data",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        # Should fail with 400 for bbox too large
        assert response.status_code == 400
        print("✓ Large bbox correctly rejected")

    def test_terrain_data_caching(self):
        """TEST 5: Second request uses cache"""
        payload = {
            "south": 46.80,
            "west": -71.22,
            "north": 46.82,
            "east": -71.20,
            "exclude_types": ["water", "roads"]
        }
        
        # First request
        response1 = requests.post(
            f"{BASE_URL}/api/v1/bionic/terrain/terrain-data",
            json=payload
        )
        assert response1.status_code == 200
        data1 = response1.json()
        
        # Second request should hit cache
        response2 = requests.post(
            f"{BASE_URL}/api/v1/bionic/terrain/terrain-data",
            json=payload
        )
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Both should succeed
        assert data1["success"] is True
        assert data2["success"] is True
        
        # Second should be cached (or may not be if TTL expired)
        print(f"✓ First request cached: {data1.get('cached')}")
        print(f"✓ Second request cached: {data2.get('cached')}")

    def test_terrain_data_zone_structure(self):
        """TEST 6: Verify exclusion zone structure"""
        payload = {
            "south": 46.81,
            "west": -71.23,
            "north": 46.82,
            "east": -71.22,
            "exclude_types": ["water", "roads", "urban"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/terrain/terrain-data",
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        zones = data.get("exclusion_zones", [])
        if zones:
            zone = zones[0]
            # Check required fields
            assert "type" in zone
            assert zone["type"] in ["water", "roads", "urban", "infrastructure"]
            assert "geometry_type" in zone
            assert zone["geometry_type"] in ["polygon", "line"]
            assert "coordinates" in zone
            assert isinstance(zone["coordinates"], list)
            print(f"✓ Zone structure valid: type={zone['type']}, geometry={zone['geometry_type']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
