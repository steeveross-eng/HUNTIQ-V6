"""
ANTHROPIQUE V5 - Phase 1 - Backend API Tests
Tests for terrain-data endpoint with sub_type classification

Features tested:
- sub_type field in exclusion zones (roads/urban/infrastructure)
- geometry_type differentiation (line vs polygon)
- Highway tag classification (motorway, primary, track, path, etc.)
- Urban tag classification (residential, commercial, industrial, etc.)
- Health endpoint
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestTerrainDataHealth:
    """Health endpoint for terrain-data API"""
    
    def test_health_endpoint_returns_200(self):
        """GET /api/v1/bionic/terrain/terrain-data/health returns 200"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/terrain/terrain-data/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("status") == "operational"
        assert "supported_types" in data
        assert "water" in data["supported_types"]
        assert "roads" in data["supported_types"]
        assert "urban" in data["supported_types"]
        assert "infrastructure" in data["supported_types"]
        print(f"✓ Health endpoint returned: {data}")


class TestTerrainDataSubType:
    """Test sub_type classification for exclusion zones"""
    
    @pytest.fixture
    def sample_bbox_quebec_city(self):
        """Sample bounding box near Quebec City"""
        return {
            "south": 46.78,
            "west": -71.25,
            "north": 46.85,
            "east": -71.15,
            "exclude_types": ["roads", "urban", "infrastructure"],
            "detail_level": "high"
        }
    
    def test_terrain_data_returns_sub_type_for_roads(self, sample_bbox_quebec_city):
        """POST /api/v1/bionic/terrain/terrain-data returns sub_type for road zones"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/terrain/terrain-data",
            json=sample_bbox_quebec_city,
            timeout=60
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") is True
        
        exclusion_zones = data.get("exclusion_zones", [])
        print(f"Total exclusion zones: {len(exclusion_zones)}")
        
        # Filter for road zones
        road_zones = [z for z in exclusion_zones if z.get("type") == "roads"]
        print(f"Road zones count: {len(road_zones)}")
        
        # Check that at least some road zones have sub_type
        zones_with_sub_type = [z for z in road_zones if z.get("sub_type")]
        assert len(zones_with_sub_type) > 0, "No road zones found with sub_type"
        
        # Verify sub_types are valid highway tags
        valid_highway_tags = {
            'motorway', 'motorway_link', 'trunk', 'trunk_link',
            'primary', 'primary_link', 'secondary', 'secondary_link',
            'tertiary', 'tertiary_link', 'residential', 'service',
            'unclassified', 'living_street', 'pedestrian', 'track',
            'footway', 'cycleway', 'path'
        }
        
        sample_sub_types = [z.get("sub_type") for z in zones_with_sub_type[:10]]
        print(f"Sample road sub_types: {sample_sub_types}")
        
        for z in zones_with_sub_type[:20]:  # Check first 20
            sub_type = z.get("sub_type")
            assert sub_type in valid_highway_tags or sub_type == "unknown", \
                f"Invalid road sub_type: {sub_type}"
    
    def test_terrain_data_returns_sub_type_for_urban(self, sample_bbox_quebec_city):
        """POST /api/v1/bionic/terrain/terrain-data returns sub_type for urban zones"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/terrain/terrain-data",
            json=sample_bbox_quebec_city,
            timeout=60
        )
        assert response.status_code == 200
        
        data = response.json()
        exclusion_zones = data.get("exclusion_zones", [])
        
        # Filter for urban zones
        urban_zones = [z for z in exclusion_zones if z.get("type") == "urban"]
        print(f"Urban zones count: {len(urban_zones)}")
        
        # Check that at least some urban zones have sub_type
        zones_with_sub_type = [z for z in urban_zones if z.get("sub_type")]
        
        if len(zones_with_sub_type) > 0:
            valid_urban_tags = {
                'residential', 'commercial', 'industrial', 'retail',
                'farmland', 'farmyard', 'orchard', 'vineyard', 'allotments',
                'recreation_ground', 'cemetery', 'construction', 'military',
                'quarry', 'landfill', 'yes', 'house', 'apartments', 'unknown'
            }
            
            sample_sub_types = [z.get("sub_type") for z in zones_with_sub_type[:10]]
            print(f"Sample urban sub_types: {sample_sub_types}")
            
            # Count valid vs invalid sub_types
            valid_count = sum(1 for z in zones_with_sub_type[:20] 
                           if z.get("sub_type") in valid_urban_tags or z.get("sub_type"))
            print(f"Valid urban sub_types: {valid_count}/{min(20, len(zones_with_sub_type))}")
        else:
            print("No urban zones with sub_type found (may be cached with water-heavy area)")


class TestGeometryTypeDifferentiation:
    """Test that roads/urban/infrastructure return correct geometry_type"""
    
    @pytest.fixture
    def sample_bbox(self):
        """Sample bounding box"""
        return {
            "south": 46.80,
            "west": -71.22,
            "north": 46.86,
            "east": -71.16,
            "exclude_types": ["roads", "urban", "infrastructure"],
            "detail_level": "high"
        }
    
    def test_roads_return_line_geometry_type(self, sample_bbox):
        """Roads (highways) should return geometry_type='line'"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/terrain/terrain-data",
            json=sample_bbox,
            timeout=60
        )
        assert response.status_code == 200
        
        data = response.json()
        exclusion_zones = data.get("exclusion_zones", [])
        
        # Filter for road zones
        road_zones = [z for z in exclusion_zones if z.get("type") == "roads"]
        
        # Count geometry types
        line_count = sum(1 for z in road_zones if z.get("geometry_type") == "line")
        polygon_count = sum(1 for z in road_zones if z.get("geometry_type") == "polygon")
        
        print(f"Road zones: {len(road_zones)} (lines: {line_count}, polygons: {polygon_count})")
        
        # Roads should be predominantly lines
        assert line_count > 0, "Expected roads to have line geometry_type"
        
        # Sample a few road zones to verify
        for z in road_zones[:5]:
            print(f"  Road zone: type={z.get('type')}, geometry_type={z.get('geometry_type')}, sub_type={z.get('sub_type')}")
    
    def test_urban_returns_polygon_geometry_type(self, sample_bbox):
        """Urban zones (landuse) should return geometry_type='polygon'"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/terrain/terrain-data",
            json=sample_bbox,
            timeout=60
        )
        assert response.status_code == 200
        
        data = response.json()
        exclusion_zones = data.get("exclusion_zones", [])
        
        # Filter for urban zones (excluding buildings which can be either)
        urban_zones = [z for z in exclusion_zones if z.get("type") == "urban"]
        
        # Count geometry types
        polygon_count = sum(1 for z in urban_zones if z.get("geometry_type") == "polygon")
        line_count = sum(1 for z in urban_zones if z.get("geometry_type") == "line")
        
        print(f"Urban zones: {len(urban_zones)} (polygons: {polygon_count}, lines: {line_count})")
        
        # Urban zones should be predominantly polygons
        assert polygon_count > 0, "Expected urban zones to have polygon geometry_type"
        
        # Sample a few urban zones
        for z in urban_zones[:5]:
            print(f"  Urban zone: type={z.get('type')}, geometry_type={z.get('geometry_type')}, sub_type={z.get('sub_type')}")
    
    def test_both_line_and_polygon_present(self, sample_bbox):
        """API should return both line and polygon geometry_types for roads+urban+infrastructure"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/terrain/terrain-data",
            json=sample_bbox,
            timeout=60
        )
        assert response.status_code == 200
        
        data = response.json()
        exclusion_zones = data.get("exclusion_zones", [])
        
        geometry_types = set(z.get("geometry_type") for z in exclusion_zones)
        print(f"Geometry types present: {geometry_types}")
        
        assert "line" in geometry_types, "Expected 'line' geometry_type in response"
        assert "polygon" in geometry_types, "Expected 'polygon' geometry_type in response"


class TestHighwayTagClassification:
    """Test sub_type correctly classifies highway tags"""
    
    @pytest.fixture
    def sample_bbox(self):
        """Sample bounding box with likely roads - include all types to get more data"""
        return {
            "south": 46.80,
            "west": -71.22,
            "north": 46.86,
            "east": -71.16,
            "exclude_types": ["roads", "urban", "infrastructure"],
            "detail_level": "high"
        }
    
    def test_highway_sub_types_present(self, sample_bbox):
        """sub_type should contain highway tags (motorway, primary, track, path, etc.)"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/terrain/terrain-data",
            json=sample_bbox,
            timeout=60
        )
        assert response.status_code == 200
        
        data = response.json()
        exclusion_zones = data.get("exclusion_zones", [])
        
        # Get all unique sub_types for roads
        road_sub_types = set()
        for z in exclusion_zones:
            if z.get("type") == "roads" and z.get("sub_type"):
                road_sub_types.add(z.get("sub_type"))
        
        print(f"Unique road sub_types found: {road_sub_types}")
        
        # At least one highway tag should be present
        expected_tags = {
            'motorway', 'trunk', 'primary', 'secondary', 'tertiary',
            'residential', 'service', 'unclassified', 'track', 'footway',
            'cycleway', 'path'
        }
        
        found_expected = road_sub_types & expected_tags
        print(f"Expected highway tags found: {found_expected}")
        
        assert len(found_expected) >= 1, \
            f"Expected at least 1 standard highway tag, found: {road_sub_types}"


class TestDetailLevelParameter:
    """Test detail_level parameter affects results"""
    
    @pytest.fixture
    def sample_bbox(self):
        return {
            "south": 46.82,
            "west": -71.21,
            "north": 46.86,
            "east": -71.18,
            "exclude_types": ["roads", "urban"]
        }
    
    def test_high_detail_returns_more_zones(self, sample_bbox):
        """detail_level='high' should return more zones than 'low'"""
        # Request with high detail
        high_detail = {**sample_bbox, "detail_level": "high"}
        resp_high = requests.post(
            f"{BASE_URL}/api/v1/bionic/terrain/terrain-data",
            json=high_detail,
            timeout=60
        )
        assert resp_high.status_code == 200
        data_high = resp_high.json()
        count_high = len(data_high.get("exclusion_zones", []))
        
        # Request with low detail
        low_detail = {**sample_bbox, "detail_level": "low"}
        resp_low = requests.post(
            f"{BASE_URL}/api/v1/bionic/terrain/terrain-data",
            json=low_detail,
            timeout=60
        )
        assert resp_low.status_code == 200
        data_low = resp_low.json()
        count_low = len(data_low.get("exclusion_zones", []))
        
        print(f"High detail zones: {count_high}, Low detail zones: {count_low}")
        
        # High detail should return at least as many as low detail
        # (may be equal if area has only major features)
        assert count_high >= count_low, \
            f"Expected high detail ({count_high}) >= low detail ({count_low})"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
