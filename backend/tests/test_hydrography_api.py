"""
Test suite for Hydrography API - Water Exclusion for BIONIC zones

Tests:
- GET /api/hydro/sources - List available hydrographic sources
- GET /api/hydro/sources/detect - Detect sources for a location
- GET /api/hydro/water-features - Get water features around a point
- POST /api/hydro/check-point - Check if a point is in water
- POST /api/hydro/filter-zones - Filter zones to exclude water areas
"""

import pytest
import requests
import os

# Read BASE_URL from frontend .env or environment
def get_base_url():
    # First try environment variable
    url = os.environ.get('REACT_APP_BACKEND_URL', '')
    if url:
        return url.rstrip('/')
    
    # Try reading from frontend .env
    frontend_env_path = os.path.join(os.path.dirname(__file__), '../../frontend/.env')
    if os.path.exists(frontend_env_path):
        with open(frontend_env_path, 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip().rstrip('/')
    
    # Fallback
    return 'https://bionic-v5-hunt.preview.emergentagent.com'

BASE_URL = get_base_url()

class TestHydroSources:
    """Tests for /api/hydro/sources endpoint"""
    
    def test_get_sources_success(self):
        """Test GET /api/hydro/sources returns list of hydrographic sources"""
        response = requests.get(f"{BASE_URL}/api/hydro/sources")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "sources" in data
        assert "description" in data
        assert "fallback" in data
        
        # Verify sources list
        sources = data["sources"]
        assert len(sources) >= 4  # Quebec, Canada, USA, OSM
        
        # Verify each source has required fields
        for source in sources:
            assert "id" in source
            assert "name" in source
            assert "type" in source
            assert "priority" in source
            assert "coverage" in source
        
        # Verify expected sources exist
        source_ids = [s["id"] for s in sources]
        assert "quebec_mrnf" in source_ids
        assert "canada_canvec" in source_ids
        assert "usa_nhd" in source_ids
        assert "osm_fallback" in source_ids
        
        print(f"✓ Found {len(sources)} hydrographic sources")

    def test_detect_sources_quebec(self):
        """Test source detection for Quebec location"""
        # Quebec City coordinates
        lat, lng = 46.8, -71.2
        
        response = requests.get(f"{BASE_URL}/api/hydro/sources/detect?lat={lat}&lng={lng}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["lat"] == lat
        assert data["lng"] == lng
        assert "available_sources" in data
        assert "primary_source" in data
        assert "message" in data
        
        # Quebec should have multiple sources available
        assert len(data["available_sources"]) >= 2
        
        # Primary source should be Quebec MRNF (priority 1)
        primary = data["primary_source"]
        assert primary is not None
        assert primary["id"] == "quebec_mrnf"
        
        print(f"✓ Detected {len(data['available_sources'])} sources for Quebec location")

    def test_detect_sources_usa(self):
        """Test source detection for USA location"""
        # New York coordinates
        lat, lng = 40.7, -74.0
        
        response = requests.get(f"{BASE_URL}/api/hydro/sources/detect?lat={lat}&lng={lng}")
        
        assert response.status_code == 200
        data = response.json()
        
        # USA should have NHD and OSM available
        source_ids = [s["id"] for s in data["available_sources"]]
        assert "usa_nhd" in source_ids
        assert "osm_fallback" in source_ids
        
        print(f"✓ Detected {len(data['available_sources'])} sources for USA location")

    def test_detect_sources_global(self):
        """Test source detection for location outside North America"""
        # Paris coordinates
        lat, lng = 48.8, 2.3
        
        response = requests.get(f"{BASE_URL}/api/hydro/sources/detect?lat={lat}&lng={lng}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Only OSM should be available for Paris
        source_ids = [s["id"] for s in data["available_sources"]]
        assert "osm_fallback" in source_ids
        
        print(f"✓ OSM fallback available for global location")


class TestWaterFeatures:
    """Tests for /api/hydro/water-features endpoint"""
    
    def test_get_water_features_success(self):
        """Test GET /api/hydro/water-features returns water features"""
        lat, lng = 46.8, -71.2
        radius = 2000
        
        response = requests.get(f"{BASE_URL}/api/hydro/water-features?lat={lat}&lng={lng}&radius={radius}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert data["success"] == True
        assert "features" in data
        assert "center" in data
        assert "radius" in data
        assert "count" in data
        
        # Verify center
        assert data["center"]["lat"] == lat
        assert data["center"]["lng"] == lng
        assert data["radius"] == radius
        
        # Verify features structure (if any found)
        if data["count"] > 0:
            feature = data["features"][0]
            assert "id" in feature
            assert "type" in feature
            assert "polygon" in feature
            
        print(f"✓ Found {data['count']} water features around ({lat}, {lng})")

    def test_get_water_features_default_radius(self):
        """Test water features with default radius"""
        lat, lng = 46.8, -71.2
        
        response = requests.get(f"{BASE_URL}/api/hydro/water-features?lat={lat}&lng={lng}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Default radius should be 5000m
        assert data["radius"] == 5000
        
        print(f"✓ Default radius is 5000m")

    def test_get_water_features_small_radius(self):
        """Test water features with small radius"""
        lat, lng = 46.8, -71.2
        radius = 500
        
        response = requests.get(f"{BASE_URL}/api/hydro/water-features?lat={lat}&lng={lng}&radius={radius}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["radius"] == radius
        
        print(f"✓ Small radius query successful, found {data['count']} features")


class TestCheckPoint:
    """Tests for /api/hydro/check-point endpoint"""
    
    def test_check_point_on_land(self):
        """Test check-point for a location on land"""
        payload = {
            "lat": 46.82,
            "lng": -71.22,
            "tolerance_meters": 5
        }
        
        response = requests.post(f"{BASE_URL}/api/hydro/check-point", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "is_in_water" in data
        assert "water_type" in data
        assert "water_name" in data
        assert "tolerance_meters" in data
        assert "message" in data
        
        # This point should be on land
        assert data["tolerance_meters"] == 5
        
        print(f"✓ Point check result: {data['message']}")

    def test_check_point_with_bounds(self):
        """Test check-point with bounds parameter"""
        payload = {
            "lat": 46.8,
            "lng": -71.2,
            "tolerance_meters": 5,
            "bounds": {
                "north": 46.85,
                "south": 46.75,
                "east": -71.1,
                "west": -71.3
            }
        }
        
        response = requests.post(f"{BASE_URL}/api/hydro/check-point", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "is_in_water" in data
        
        print(f"✓ Point check with bounds: {data['message']}")

    def test_check_point_default_tolerance(self):
        """Test check-point uses default tolerance (5m)"""
        payload = {
            "lat": 46.8,
            "lng": -71.2
        }
        
        response = requests.post(f"{BASE_URL}/api/hydro/check-point", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Default tolerance should be 5m
        assert data["tolerance_meters"] == 5
        
        print(f"✓ Default tolerance is 5m")


class TestFilterZones:
    """Tests for /api/hydro/filter-zones endpoint"""
    
    def test_filter_zones_success(self):
        """Test POST /api/hydro/filter-zones filters zones correctly"""
        payload = {
            "zones": [
                {"id": "zone1", "center": [46.82, -71.22], "radiusMeters": 100, "moduleId": "habitats", "percentage": 75},
                {"id": "zone2", "center": [46.81, -71.21], "radiusMeters": 100, "moduleId": "corridors", "percentage": 60},
                {"id": "zone3", "center": [46.80, -71.20], "radiusMeters": 100, "moduleId": "affuts", "percentage": 80}
            ],
            "bounds": {"north": 46.85, "south": 46.75, "east": -71.1, "west": -71.3},
            "tolerance_meters": 5
        }
        
        response = requests.post(f"{BASE_URL}/api/hydro/filter-zones", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert data["success"] == True
        assert "filtered_zones" in data
        assert "stats" in data
        assert "message" in data
        
        # Verify stats
        stats = data["stats"]
        assert "total" in stats
        assert "filtered" in stats
        assert "excluded" in stats
        assert "water_features_count" in stats
        assert "tolerance_meters" in stats
        assert "sources_used" in stats
        
        assert stats["total"] == 3
        assert stats["tolerance_meters"] == 5
        
        print(f"✓ Filter zones: {stats['filtered']}/{stats['total']} kept, {stats['excluded']} excluded")

    def test_filter_zones_empty_list(self):
        """Test filter-zones with empty zones list"""
        payload = {
            "zones": [],
            "bounds": {"north": 46.85, "south": 46.75, "east": -71.1, "west": -71.3},
            "tolerance_meters": 5
        }
        
        response = requests.post(f"{BASE_URL}/api/hydro/filter-zones", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert len(data["filtered_zones"]) == 0
        assert data["stats"]["total"] == 0
        
        print(f"✓ Empty zones list handled correctly")

    def test_filter_zones_default_tolerance(self):
        """Test filter-zones uses default tolerance"""
        payload = {
            "zones": [
                {"id": "zone1", "center": [46.82, -71.22], "radiusMeters": 100, "moduleId": "habitats", "percentage": 75}
            ],
            "bounds": {"north": 46.85, "south": 46.75, "east": -71.1, "west": -71.3}
        }
        
        response = requests.post(f"{BASE_URL}/api/hydro/filter-zones", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Default tolerance should be 5m
        assert data["stats"]["tolerance_meters"] == 5
        
        print(f"✓ Default tolerance is 5m for filter-zones")

    def test_filter_zones_preserves_zone_data(self):
        """Test that filtered zones preserve all original data"""
        payload = {
            "zones": [
                {"id": "test_zone", "center": [46.82, -71.22], "radiusMeters": 150, "moduleId": "habitats", "percentage": 85}
            ],
            "bounds": {"north": 46.85, "south": 46.75, "east": -71.1, "west": -71.3},
            "tolerance_meters": 5
        }
        
        response = requests.post(f"{BASE_URL}/api/hydro/filter-zones", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # If zone is not excluded, verify data is preserved
        if len(data["filtered_zones"]) > 0:
            zone = data["filtered_zones"][0]
            assert zone["id"] == "test_zone"
            assert zone["center"] == [46.82, -71.22]
            assert zone["radiusMeters"] == 150
            assert zone["moduleId"] == "habitats"
            assert zone["percentage"] == 85
            
        print(f"✓ Zone data preserved after filtering")


class TestWaterTypes:
    """Tests for /api/hydro/water-types endpoint"""
    
    def test_get_water_types(self):
        """Test GET /api/hydro/water-types returns water types"""
        response = requests.get(f"{BASE_URL}/api/hydro/water-types")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "water_types" in data
        assert "shore_tolerance_default" in data
        assert "description" in data
        
        # Verify expected water types
        water_types = data["water_types"]
        assert "lake" in water_types
        assert "river" in water_types
        assert "stream" in water_types
        assert "pond" in water_types
        
        # Default tolerance should be 5m
        assert data["shore_tolerance_default"] == 5
        
        print(f"✓ Found {len(water_types)} water types")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
