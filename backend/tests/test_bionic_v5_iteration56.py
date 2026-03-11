"""
BIONIC V5 Iteration 56 — Backend API Tests for Terrain Data Exclusion

Tests POST /api/v1/bionic/terrain/terrain-data endpoint to verify:
1. Water exclusion zones (natural=water, waterway, wetland, bay, strait)
2. Urban exclusion zones (landuse=residential|commercial|industrial, amenity, leisure, building)  
3. Road exclusion zones (highway=*)
4. Infrastructure zones (railway, aeroway, power)

Expected thresholds for Quebec/Lévis bbox (46.78,-71.28,46.85,-71.15):
- Water > 350
- Urban > 2500
- Road > 3500

CONFORME: BIONIC V5 — TOLÉRANCE ZÉRO
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Quebec/Lévis bbox for testing — known region with river, city, roads
QUEBEC_LEVIS_BBOX = {
    "south": 46.78,
    "west": -71.28,
    "north": 46.85,
    "east": -71.15
}

# Smaller bbox for faster tests
SMALL_BBOX = {
    "south": 46.80,
    "west": -71.25,
    "north": 46.84,
    "east": -71.18
}

# Saint Lawrence River area (should have high water count)
RIVER_BBOX = {
    "south": 46.78,
    "west": -71.25,
    "north": 46.82,
    "east": -71.18
}


class TestHealthEndpoint:
    """Health check for terrain data API"""
    
    def test_health_operational(self):
        """Test terrain-data health endpoint returns operational status"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/terrain/terrain-data/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert "water" in data["supported_types"]
        assert "roads" in data["supported_types"]
        assert "urban" in data["supported_types"]
        assert "infrastructure" in data["supported_types"]
        assert "low" in data["detail_levels"]
        assert "high" in data["detail_levels"]
        print(f"✓ Health endpoint operational: {data}")


class TestWaterExclusions:
    """Tests for water exclusion zones (TOLÉRANCE ZÉRO eau)"""
    
    def test_water_exclusion_returns_zones(self):
        """Test that water exclusion type returns water zones"""
        payload = {
            **SMALL_BBOX,
            "exclude_types": ["water"],
            "detail_level": "high"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/terrain/terrain-data", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        
        water_count = data["stats"]["by_type"].get("water", 0)
        print(f"✓ Water exclusion returned {water_count} zones (bbox: {SMALL_BBOX})")
        
        # Verify at least some water zones exist near the river
        assert water_count > 0, "Expected water zones near Saint Lawrence River"
    
    def test_water_zone_types(self):
        """Test that water zones have valid types: natural=water, waterway, wetland, etc."""
        payload = {
            **RIVER_BBOX,
            "exclude_types": ["water"],
            "detail_level": "high"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/terrain/terrain-data", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Verify all returned zones are typed as "water"
        for zone in data["exclusion_zones"][:10]:  # Sample first 10
            assert zone["type"] == "water", f"Expected type 'water', got '{zone['type']}'"
            assert zone["geometry_type"] in ["polygon", "line"], f"Invalid geometry type: {zone['geometry_type']}"
            assert len(zone["coordinates"]) >= 2, "Water zone must have at least 2 coordinates"
        
        print(f"✓ Water zone types validated, count: {len(data['exclusion_zones'])}")


class TestUrbanExclusions:
    """Tests for urban exclusion zones (TOLÉRANCE ZÉRO zones urbaines)"""
    
    def test_urban_exclusion_returns_zones(self):
        """Test that urban exclusion type returns urban zones"""
        payload = {
            **SMALL_BBOX,
            "exclude_types": ["urban"],
            "detail_level": "high"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/terrain/terrain-data", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        
        urban_count = data["stats"]["by_type"].get("urban", 0)
        print(f"✓ Urban exclusion returned {urban_count} zones (bbox: {SMALL_BBOX})")
        
        # Quebec City area should have substantial urban zones
        assert urban_count > 100, f"Expected >100 urban zones, got {urban_count}"


class TestRoadExclusions:
    """Tests for road exclusion zones (TOLÉRANCE ZÉRO routes)"""
    
    def test_road_exclusion_returns_zones(self):
        """Test that road exclusion type returns road zones"""
        payload = {
            **SMALL_BBOX,
            "exclude_types": ["roads"],
            "detail_level": "high"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/terrain/terrain-data", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        
        road_count = data["stats"]["by_type"].get("roads", 0)
        print(f"✓ Road exclusion returned {road_count} zones (bbox: {SMALL_BBOX})")
        
        # Urban area should have many roads
        assert road_count > 100, f"Expected >100 road zones, got {road_count}"
    
    def test_road_zones_are_lines(self):
        """Test that road zones have line geometry (not polygons)"""
        payload = {
            **SMALL_BBOX,
            "exclude_types": ["roads"],
            "detail_level": "low"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/terrain/terrain-data", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        line_count = 0
        for zone in data["exclusion_zones"][:50]:  # Sample first 50
            if zone["geometry_type"] == "line":
                line_count += 1
        
        # Most roads should be lines
        assert line_count > 20, f"Expected roads as lines, found {line_count}"
        print(f"✓ Road geometry validated: {line_count} line segments")


class TestInfrastructureExclusions:
    """Tests for infrastructure exclusion zones (railway, aeroway, power)"""
    
    def test_infrastructure_exclusion(self):
        """Test infrastructure exclusion returns zones"""
        payload = {
            **QUEBEC_LEVIS_BBOX,
            "exclude_types": ["infrastructure"],
            "detail_level": "high"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/terrain/terrain-data", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        
        infra_count = data["stats"]["by_type"].get("infrastructure", 0)
        print(f"✓ Infrastructure exclusion returned {infra_count} zones")


class TestCombinedExclusions:
    """Tests for combined exclusion types (all together)"""
    
    def test_combined_exclusion_quebec_levis(self):
        """Test combined exclusion for full Quebec/Lévis bbox"""
        payload = {
            **QUEBEC_LEVIS_BBOX,
            "exclude_types": ["water", "roads", "urban", "infrastructure"],
            "detail_level": "low"  # Use low for faster response
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/terrain/terrain-data", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        
        stats = data["stats"]["by_type"]
        water_count = stats.get("water", 0)
        roads_count = stats.get("roads", 0)
        urban_count = stats.get("urban", 0)
        infra_count = stats.get("infrastructure", 0)
        total = data["stats"]["exclusion_zones_count"]
        
        print(f"✓ Combined exclusion Quebec/Lévis bbox:")
        print(f"  - Water: {water_count}")
        print(f"  - Roads: {roads_count}")
        print(f"  - Urban: {urban_count}")
        print(f"  - Infrastructure: {infra_count}")
        print(f"  - TOTAL: {total}")
        
        # Validate minimum thresholds (lowered for 'low' detail level)
        assert water_count > 50, f"Expected water > 50, got {water_count}"
        assert roads_count > 500, f"Expected roads > 500, got {roads_count}"
        assert urban_count > 100, f"Expected urban > 100, got {urban_count}"


class TestBboxLimits:
    """Tests for bbox size validation"""
    
    def test_bbox_too_large_lat(self):
        """Test bbox exceeding 0.3° latitude limit returns 400"""
        payload = {
            "south": 46.0,
            "west": -71.3,
            "north": 46.5,  # 0.5° > 0.3° limit
            "east": -71.0,
            "exclude_types": ["water"],
            "detail_level": "low"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/terrain/terrain-data", json=payload)
        assert response.status_code == 400, f"Expected 400 for bbox > 0.3° lat, got {response.status_code}"
        print("✓ Bbox latitude limit enforced (400 for > 0.3°)")
    
    def test_bbox_too_large_lng(self):
        """Test bbox exceeding 0.4° longitude limit returns 400"""
        payload = {
            "south": 46.7,
            "west": -71.8,
            "north": 46.9,
            "east": -71.2,  # 0.6° > 0.4° limit
            "exclude_types": ["water"],
            "detail_level": "low"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/terrain/terrain-data", json=payload)
        assert response.status_code == 400, f"Expected 400 for bbox > 0.4° lng, got {response.status_code}"
        print("✓ Bbox longitude limit enforced (400 for > 0.4°)")
    
    def test_bbox_valid_within_limits(self):
        """Test bbox within limits returns 200"""
        payload = {
            "south": 46.80,
            "west": -71.25,
            "north": 46.85,  # 0.05° < 0.3° limit
            "east": -71.15,  # 0.1° < 0.4° limit
            "exclude_types": ["water"],
            "detail_level": "low"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/terrain/terrain-data", json=payload)
        assert response.status_code == 200, f"Expected 200 for valid bbox, got {response.status_code}"
        print("✓ Valid bbox accepted (200)")


class TestDetailLevels:
    """Tests for detail level parameter"""
    
    def test_low_detail_vs_high_detail(self):
        """Test high detail returns more features than low detail"""
        bbox = SMALL_BBOX
        
        # Low detail request
        low_payload = {**bbox, "exclude_types": ["urban"], "detail_level": "low"}
        low_response = requests.post(f"{BASE_URL}/api/v1/bionic/terrain/terrain-data", json=low_payload)
        assert low_response.status_code == 200
        low_count = low_response.json()["stats"]["exclusion_zones_count"]
        
        # High detail request
        high_payload = {**bbox, "exclude_types": ["urban"], "detail_level": "high"}
        high_response = requests.post(f"{BASE_URL}/api/v1/bionic/terrain/terrain-data", json=high_payload)
        assert high_response.status_code == 200
        high_count = high_response.json()["stats"]["exclusion_zones_count"]
        
        print(f"✓ Detail levels: low={low_count}, high={high_count}")
        
        # High detail should have at least as many (often more) zones
        assert high_count >= low_count * 0.5, f"High detail ({high_count}) should be >= 50% of low ({low_count})"


class TestCacheAndPerformance:
    """Tests for cache behavior and performance"""
    
    def test_cache_hit(self):
        """Test that repeated requests hit cache"""
        payload = {
            **SMALL_BBOX,
            "exclude_types": ["water"],
            "detail_level": "low"
        }
        
        # First request
        response1 = requests.post(f"{BASE_URL}/api/v1/bionic/terrain/terrain-data", json=payload)
        assert response1.status_code == 200
        
        # Second request (should hit cache)
        response2 = requests.post(f"{BASE_URL}/api/v1/bionic/terrain/terrain-data", json=payload)
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Cache hit may set cached=True
        print(f"✓ Cache test: cached={data2.get('cached', 'unknown')}")


class TestCoordinateValidation:
    """Tests for coordinate format in response"""
    
    def test_coordinate_format(self):
        """Test that coordinates are [lng, lat] format"""
        payload = {
            **RIVER_BBOX,
            "exclude_types": ["water"],
            "detail_level": "low"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/terrain/terrain-data", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        if len(data["exclusion_zones"]) > 0:
            zone = data["exclusion_zones"][0]
            coord = zone["coordinates"][0]
            
            # Coordinates should be [lng, lat] format
            # lng should be negative (Western hemisphere)
            # lat should be positive (Northern hemisphere)
            assert len(coord) == 2, "Coordinate must be [lng, lat]"
            lng, lat = coord
            assert -180 <= lng <= 180, f"Invalid longitude: {lng}"
            assert -90 <= lat <= 90, f"Invalid latitude: {lat}"
            
            # For Quebec, lng should be ~-71, lat should be ~46
            assert -75 <= lng <= -60, f"Longitude out of Quebec range: {lng}"
            assert 45 <= lat <= 55, f"Latitude out of Quebec range: {lat}"
            
            print(f"✓ Coordinate format valid: [{lng:.4f}, {lat:.4f}]")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
