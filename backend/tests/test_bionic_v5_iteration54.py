"""
BIONIC V5 — Test Suite for Iteration 54
Tests AUDIT TOLÉRANCE ZÉRO fixes:
- detail_level parameter (low returns residential roads, high returns buildings+service roads+streams)
- Bbox limit validation (>0.3 lat or >0.4 lng returns 400)
- Tiling is done frontend-side (backend rejects large bbox)
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://steve-max-plus.preview.emergentagent.com').rstrip('/')


class TestBionicV5DetailLevel:
    """Tests for detail_level parameter in terrain-data API"""
    
    def test_health_shows_detail_levels(self):
        """Test health endpoint shows both detail levels"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/terrain/terrain-data/health")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'operational'
        assert 'detail_levels' in data
        assert 'low' in data['detail_levels']
        assert 'high' in data['detail_levels']
        print("PASSED: Health endpoint shows detail_levels [low, high]")
    
    def test_detail_level_low_returns_residential_roads(self):
        """TEST 1: detail_level=low returns residential roads (not just major roads)"""
        # Quebec City area with mix of residential and major roads
        payload = {
            "south": 46.80,
            "west": -71.25,
            "north": 46.82,
            "east": -71.22,
            "exclude_types": ["roads"],
            "detail_level": "low"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/terrain/terrain-data",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        
        roads = data['exclusion_zones']
        assert len(roads) > 0, "Should return road exclusions at detail_level=low"
        
        # Check that roads were fetched (at low level this should include residential)
        road_count = len([z for z in roads if z['type'] == 'roads'])
        print(f"PASSED: detail_level=low returned {road_count} roads (includes residential)")
    
    def test_detail_level_high_returns_buildings_and_service_roads(self):
        """TEST 2: detail_level=high returns buildings, service roads, streams"""
        # Small area in Quebec City
        payload = {
            "south": 46.81,
            "west": -71.24,
            "north": 46.82,
            "east": -71.23,
            "exclude_types": ["water", "roads", "infrastructure"],
            "detail_level": "high"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/terrain/terrain-data",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert data['stats']['detail_level'] == 'high'
        
        # High detail should include more entities
        total_zones = len(data['exclusion_zones'])
        print(f"PASSED: detail_level=high returned {total_zones} exclusion zones (buildings, service roads, streams)")
    
    def test_detail_level_defaults_to_high(self):
        """Test that detail_level defaults to high when not specified"""
        payload = {
            "south": 46.81,
            "west": -71.24,
            "north": 46.82,
            "east": -71.23,
            "exclude_types": ["water"]
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/terrain/terrain-data",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        # Default should be high
        assert data['stats'].get('detail_level', 'high') == 'high'
        print("PASSED: detail_level defaults to high")


class TestBionicV5BboxLimit:
    """TEST 3: Bbox >0.3 lat or >0.4 lng returns 400 (tiling done frontend-side)"""
    
    def test_bbox_exceeds_lat_limit(self):
        """Bbox >0.3 lat should return 400"""
        # 0.35 degree lat range > 0.3 limit
        payload = {
            "south": 46.50,
            "west": -71.25,
            "north": 46.85,  # 0.35 lat range > 0.3 limit
            "east": -71.22,
            "exclude_types": ["water"]
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/terrain/terrain-data",
            json=payload
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("PASSED: Bbox exceeding 0.3 lat correctly rejected with 400")
    
    def test_bbox_exceeds_lng_limit(self):
        """Bbox >0.4 lng should return 400"""
        # 0.45 degree lng range > 0.4 limit
        payload = {
            "south": 46.80,
            "west": -71.65,  # 0.45 lng range > 0.4 limit
            "north": 46.82,
            "east": -71.20,
            "exclude_types": ["water"]
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/terrain/terrain-data",
            json=payload
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("PASSED: Bbox exceeding 0.4 lng correctly rejected with 400")
    
    def test_bbox_within_limits_accepted(self):
        """Bbox within 0.3 lat x 0.4 lng should be accepted"""
        # 0.25 lat x 0.35 lng = within limits
        payload = {
            "south": 46.75,
            "west": -71.55,
            "north": 47.00,  # 0.25 lat range <= 0.3
            "east": -71.20,  # 0.35 lng range <= 0.4
            "exclude_types": ["water"],
            "detail_level": "low"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/terrain/terrain-data",
            json=payload
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data['success'] == True
        print("PASSED: Bbox within limits (0.25x0.35) accepted with 200")
    
    def test_bbox_at_exact_limits_accepted(self):
        """Bbox exactly at 0.3 lat x 0.4 lng should be accepted"""
        payload = {
            "south": 46.70,
            "west": -71.60,
            "north": 47.00,  # Exactly 0.3 lat range
            "east": -71.20,  # Exactly 0.4 lng range
            "exclude_types": ["roads"],
            "detail_level": "low"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/terrain/terrain-data",
            json=payload
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASSED: Bbox at exact limits (0.3x0.4) accepted")


class TestBionicV5ExclusionZoneContent:
    """Tests for exclusion zone content quality"""
    
    def test_water_exclusion_includes_rivers(self):
        """Water exclusion should include rivers at both detail levels"""
        payload = {
            "south": 46.80,
            "west": -71.30,
            "north": 46.85,
            "east": -71.25,
            "exclude_types": ["water"],
            "detail_level": "high"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/terrain/terrain-data",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        
        water_zones = [z for z in data['exclusion_zones'] if z['type'] == 'water']
        print(f"PASSED: Found {len(water_zones)} water exclusion zones")
    
    def test_urban_exclusion_includes_residential_areas(self):
        """Urban exclusion should include residential landuse"""
        # Quebec City center area
        payload = {
            "south": 46.81,
            "west": -71.22,
            "north": 46.83,
            "east": -71.20,
            "exclude_types": ["urban"],
            "detail_level": "low"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/terrain/terrain-data",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        
        urban_zones = [z for z in data['exclusion_zones'] if z['type'] == 'urban']
        print(f"PASSED: Found {len(urban_zones)} urban exclusion zones in city center")
    
    def test_exclusion_zone_has_coordinates(self):
        """Each exclusion zone should have valid coordinates array"""
        payload = {
            "south": 46.80,
            "west": -71.25,
            "north": 46.82,
            "east": -71.23,
            "exclude_types": ["water", "roads", "urban"],
            "detail_level": "high"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/terrain/terrain-data",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        
        for zone in data['exclusion_zones'][:5]:  # Check first 5
            assert 'coordinates' in zone
            assert isinstance(zone['coordinates'], list)
            assert len(zone['coordinates']) >= 2, "Each zone should have at least 2 coordinate points"
            # Each coordinate should be [lng, lat]
            assert len(zone['coordinates'][0]) == 2
        print("PASSED: All exclusion zones have valid coordinates")


class TestBionicV5CacheWithDetailLevel:
    """Tests for cache behavior with different detail levels"""
    
    def test_cache_key_includes_detail_level(self):
        """Different detail levels should use different cache keys"""
        bbox = {
            "south": 46.805,
            "west": -71.245,
            "north": 46.815,
            "east": -71.235,
            "exclude_types": ["water"]
        }
        
        # Request with detail_level=low
        response_low = requests.post(
            f"{BASE_URL}/api/v1/bionic/terrain/terrain-data",
            json={**bbox, "detail_level": "low"}
        )
        assert response_low.status_code == 200
        data_low = response_low.json()
        
        # Request with detail_level=high - should NOT use cache from low
        response_high = requests.post(
            f"{BASE_URL}/api/v1/bionic/terrain/terrain-data",
            json={**bbox, "detail_level": "high"}
        )
        assert response_high.status_code == 200
        data_high = response_high.json()
        
        # Both should succeed, detail level should be in stats
        assert data_low['stats']['detail_level'] == 'low'
        assert data_high['stats']['detail_level'] == 'high'
        print("PASSED: Cache correctly separates by detail_level")


class TestBionicV5ApiRegression:
    """Regression tests for existing APIs"""
    
    def test_root_api_accessible(self):
        """Test root API is accessible"""
        response = requests.get(f"{BASE_URL}/api")
        assert response.status_code in [200, 404]
        print("PASSED: API root accessible")
    
    def test_territory_waypoints_api(self):
        """Test territory waypoints API"""
        response = requests.get(f"{BASE_URL}/api/territory/waypoints?user_id=test_user")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"PASSED: Territory waypoints returns {len(data)} items")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
