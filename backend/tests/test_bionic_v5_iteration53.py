"""
BIONIC V5 — Test Suite for Iteration 53
Tests zero-tolerance validation, terrain exclusion, and API functionality
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://lisibilite-pro.preview.emergentagent.com').rstrip('/')

class TestBionicV5TerrainData:
    """Tests for terrain data API - exclusion zones"""
    
    def test_health_endpoint(self):
        """Test terrain-data health returns operational status"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/terrain/terrain-data/health")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'operational'
        assert 'water' in data['supported_types']
        assert 'roads' in data['supported_types']
        assert 'urban' in data['supported_types']
        assert 'infrastructure' in data['supported_types']
        print("PASSED: Health endpoint returns operational with all exclusion types")
    
    def test_terrain_data_returns_exclusion_zones(self):
        """Test POST terrain-data returns exclusion zones from Overpass API"""
        # Quebec City rural area
        payload = {
            "south": 46.8,
            "west": -71.3,
            "north": 46.85,
            "east": -71.2,
            "exclude_types": ["water", "roads", "urban", "infrastructure"]
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/terrain/terrain-data",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert 'exclusion_zones' in data
        assert 'stats' in data
        assert len(data['exclusion_zones']) > 0, "Should return some exclusion zones"
        print(f"PASSED: Terrain data returned {len(data['exclusion_zones'])} exclusion zones")
    
    def test_terrain_data_contains_road_exclusions(self):
        """Test that terrain data includes road line geometries"""
        payload = {
            "south": 46.8,
            "west": -71.3,
            "north": 46.85,
            "east": -71.2,
            "exclude_types": ["roads"]
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/terrain/terrain-data",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        
        roads = [z for z in data['exclusion_zones'] if z['type'] == 'roads']
        assert len(roads) > 0, "Should include road exclusion zones"
        
        # Verify road geometry is line type
        road_lines = [r for r in roads if r['geometry_type'] == 'line']
        assert len(road_lines) > 0, "Roads should have line geometry"
        print(f"PASSED: Found {len(road_lines)} road line geometries")
    
    def test_terrain_data_cache(self):
        """Test that second request uses cache"""
        payload = {
            "south": 46.81,
            "west": -71.25,
            "north": 46.83,
            "east": -71.22,
            "exclude_types": ["water", "roads"]
        }
        
        # First request
        response1 = requests.post(
            f"{BASE_URL}/api/v1/bionic/terrain/terrain-data",
            json=payload
        )
        assert response1.status_code == 200
        
        # Second request with same bbox should use cache
        response2 = requests.post(
            f"{BASE_URL}/api/v1/bionic/terrain/terrain-data",
            json=payload
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2['cached'] == True, "Second request should use cache"
        print("PASSED: Cache working correctly")
    
    def test_large_bbox_rejected(self):
        """Test that bbox > 30km is rejected with 400"""
        # Large bbox (>30km)
        payload = {
            "south": 45.0,
            "west": -72.0,
            "north": 47.0,  # Too large
            "east": -70.0,
            "exclude_types": ["water"]
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/terrain/terrain-data",
            json=payload
        )
        assert response.status_code == 400
        print("PASSED: Large bbox correctly rejected with 400")
    
    def test_exclusion_zone_structure(self):
        """Validate exclusion zone structure (type, geometry_type, coordinates)"""
        payload = {
            "south": 46.8,
            "west": -71.25,
            "north": 46.82,
            "east": -71.23,
            "exclude_types": ["water", "roads", "urban"]
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/terrain/terrain-data",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        
        if len(data['exclusion_zones']) > 0:
            zone = data['exclusion_zones'][0]
            assert 'type' in zone, "Zone should have type field"
            assert 'geometry_type' in zone, "Zone should have geometry_type field"
            assert 'coordinates' in zone, "Zone should have coordinates field"
            assert zone['type'] in ['water', 'roads', 'urban', 'infrastructure']
            assert zone['geometry_type'] in ['polygon', 'line']
            assert isinstance(zone['coordinates'], list)
            print(f"PASSED: Zone structure valid - type={zone['type']}, geometry={zone['geometry_type']}")
        else:
            print("PASSED: Structure test OK (no zones in this small bbox)")


class TestBionicV5ApiRegression:
    """Regression tests for existing BIONIC APIs"""
    
    def test_root_api_accessible(self):
        """Test root API is accessible"""
        response = requests.get(f"{BASE_URL}/api")
        assert response.status_code in [200, 404]  # 404 ok if no root handler
        print("PASSED: API is accessible")
    
    def test_territory_waypoints_accessible(self):
        """Test territory waypoints API returns valid response"""
        response = requests.get(f"{BASE_URL}/api/territory/waypoints?user_id=test_user")
        # Could be 200 with empty array or 200 with data
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"PASSED: Territory waypoints returns array with {len(data)} items")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
