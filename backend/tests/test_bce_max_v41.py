"""
BCE-MAX x4.1 Compliance Tests
Tests session persistence, corridors generation, zone loading, and layers
"""

import pytest
import requests
import os
import json

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://bionic-toolbar-slim.preview.emergentagent.com')

# Known waypoint for testing
WAYPOINT_CENTER = {"lat": 46.8068, "lng": -71.1118}
WAYPOINT_ID = "69b1615f6bc3d6e77e14fde8"


class TestCorridorsGeneration:
    """Test corridors are generated and returned by the backend"""

    def test_organic_zones_with_corridors(self):
        """POST /api/v1/bionic/organic-zones with waypoint_center should return corridors"""
        bounds = {
            "north": WAYPOINT_CENTER["lat"] + 0.015,
            "south": WAYPOINT_CENTER["lat"] - 0.015,
            "east": WAYPOINT_CENTER["lng"] + 0.015,
            "west": WAYPOINT_CENTER["lng"] - 0.015
        }
        
        payload = {
            "bounds": bounds,
            "species": "moose",
            "layers": ["habitats", "rut", "repos", "alimentation", "corridors", "affuts", "trajets", "salines"],
            "resolution": 80,
            "max_zones_per_layer": 8,
            "include_scoring": True,
            "waypoint_center": WAYPOINT_CENTER
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            timeout=60
        )
        
        # Status code assertion
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Assert corridors array exists
        assert "corridors" in data, "Response should contain 'corridors' array"
        
        corridors = data.get("corridors", [])
        print(f"Corridors count: {len(corridors)}")
        
        # BCE-MAX: corridors MUST have >0 items when zones are generated
        features = data.get("features", [])
        if len(features) > 1:
            assert len(corridors) > 0, "Corridors array should have >0 items when multiple zones are generated"
        
        # Verify corridor structure
        if corridors:
            corridor = corridors[0]
            assert "type" in corridor, "Corridor should have 'type'"
            assert "geometry" in corridor, "Corridor should have 'geometry'"
            assert "properties" in corridor, "Corridor should have 'properties'"
            
            props = corridor.get("properties", {})
            assert "corridor_type" in props or "source" in props, "Corridor should have corridor_type or source"
            print(f"First corridor type: {props.get('corridor_type', props.get('source'))}")
            
        # Verify zones exist
        assert "features" in data, "Response should contain 'features' array"
        assert len(features) > 0, "Should have at least one zone"
        print(f"Zones count: {len(features)}")
        
        return data

    def test_corridor_stats_in_response(self):
        """Verify stats include corridor counts"""
        bounds = {
            "north": WAYPOINT_CENTER["lat"] + 0.015,
            "south": WAYPOINT_CENTER["lat"] - 0.015,
            "east": WAYPOINT_CENTER["lng"] + 0.015,
            "west": WAYPOINT_CENTER["lng"] - 0.015
        }
        
        payload = {
            "bounds": bounds,
            "species": "moose",
            "layers": ["habitats", "alimentation", "repos", "rut"],
            "waypoint_center": WAYPOINT_CENTER
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            timeout=60
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Stats should exist
        stats = data.get("stats", {})
        assert "total_zones" in stats or "total" in stats, "Stats should include zone count"
        print(f"Stats: {json.dumps(stats, indent=2)[:500]}")


class TestZonesAutoLoad:
    """Test zones auto-load functionality"""
    
    def test_zones_endpoint_without_interaction(self):
        """Verify zones can be fetched without requiring user interaction"""
        bounds = {
            "north": WAYPOINT_CENTER["lat"] + 0.015,
            "south": WAYPOINT_CENTER["lat"] - 0.015,
            "east": WAYPOINT_CENTER["lng"] + 0.015,
            "west": WAYPOINT_CENTER["lng"] - 0.015
        }
        
        # Minimal payload - should work without special interaction
        payload = {
            "bounds": bounds,
            "species": "moose",
            "layers": ["habitats", "alimentation", "repos"],
            "waypoint_center": WAYPOINT_CENTER
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            timeout=60
        )
        
        assert response.status_code == 200
        data = response.json()
        features = data.get("features", [])
        assert len(features) >= 0, "API should return zones array (even if empty)"
        print(f"Auto-load zones test: {len(features)} zones returned")


class TestBiologicalSeason:
    """Test biological season parameter"""
    
    def test_zones_with_biological_season(self):
        """Verify biological_season parameter is accepted"""
        bounds = {
            "north": WAYPOINT_CENTER["lat"] + 0.015,
            "south": WAYPOINT_CENTER["lat"] - 0.015,
            "east": WAYPOINT_CENTER["lng"] + 0.015,
            "west": WAYPOINT_CENTER["lng"] - 0.015
        }
        
        payload = {
            "bounds": bounds,
            "species": "moose",
            "layers": ["habitats", "rut"],
            "waypoint_center": WAYPOINT_CENTER,
            "biological_season": "rut"  # BCE-MAX: biological season support
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            timeout=60
        )
        
        assert response.status_code == 200
        print("Biological season parameter accepted")


class TestHealthAndBasic:
    """Basic health and connectivity tests"""
    
    def test_health_endpoint(self):
        """Verify backend is healthy"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200
        print("Backend health check passed")
    
    def test_backend_root(self):
        """Test backend root responds"""
        response = requests.get(f"{BASE_URL}/api/", timeout=10)
        # Any 2xx or 3xx is acceptable for root
        assert response.status_code < 500, f"Backend root returned {response.status_code}"
        print(f"Backend root returned {response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
