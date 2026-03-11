"""
BIONIC V7 Corridor Filtering Tests
Tests for:
1. /api/v1/bionic/organic-zones with waypoint_center param (corridor perimeter filtering)
2. Without waypoint_center (backward compatibility - all corridors returned)
3. With waypoint_center - corridors have in_perimeter=true property
4. Backend starts correctly without ecotone_products_data.py
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL')


class TestBackendHealth:
    """Test backend starts correctly after ecotone_products_data.py deletion"""

    def test_health_endpoint(self):
        """Backend should be healthy after ecotone deletion"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        print("PASS: Backend healthy after ecotone_products_data.py deletion")

    def test_organic_zones_layers_endpoint(self):
        """Layers endpoint should work without ecotone module"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/organic-zones/layers", timeout=10)
        assert response.status_code == 200, f"Layers endpoint failed: {response.status_code}"
        data = response.json()
        assert "layers" in data
        assert "species" in data
        print(f"PASS: Layers endpoint returns {len(data['layers'])} layers")


class TestOrganicZonesWithWaypointCenter:
    """Test corridor filtering with waypoint_center parameter"""

    def test_with_waypoint_center_returns_filtered_corridors(self):
        """With waypoint_center, corridors should be filtered to 2km² perimeter"""
        payload = {
            "bounds": {
                "north": 46.875,
                "south": 46.845,
                "east": -71.185,
                "west": -71.215
            },
            "species": "moose",
            "layers": ["habitats", "rut", "repos", "alimentation", "corridors"],
            "resolution": 60,
            "max_zones_per_layer": 8,
            "waypoint_center": {
                "lat": 46.86,
                "lng": -71.20
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            timeout=60
        )
        
        assert response.status_code == 200, f"API failed: {response.status_code} - {response.text}"
        data = response.json()
        
        # Verify structure
        assert "features" in data, "Missing features in response"
        assert "stats" in data, "Missing stats in response"
        
        # Verify corridors exist
        corridors = data.get("corridors", [])
        print(f"INFO: Received {len(corridors)} corridors with waypoint_center filtering")
        
        # Check corridors have in_perimeter property
        if corridors:
            first_corridor = corridors[0]
            props = first_corridor.get("properties", {})
            assert "in_perimeter" in props, f"Corridor missing in_perimeter property: {props.keys()}"
            assert props["in_perimeter"] == True, f"in_perimeter should be True: {props.get('in_perimeter')}"
            print(f"PASS: Corridors have in_perimeter=True property")
        
        print(f"PASS: With waypoint_center - got {len(corridors)} filtered corridors")

    def test_without_waypoint_center_returns_all_corridors(self):
        """Without waypoint_center, all corridors should be returned (backward compat)"""
        # Larger bounds to generate more zones
        payload = {
            "bounds": {
                "north": 46.90,
                "south": 46.82,
                "east": -71.15,
                "west": -71.25
            },
            "species": "moose",
            "layers": ["habitats", "rut", "repos", "alimentation", "corridors"],
            "resolution": 60,
            "max_zones_per_layer": 8
            # NO waypoint_center
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            timeout=60
        )
        
        assert response.status_code == 200, f"API failed: {response.status_code}"
        data = response.json()
        
        # Verify structure
        assert "features" in data, "Missing features"
        corridors = data.get("corridors", [])
        
        print(f"INFO: Received {len(corridors)} corridors WITHOUT waypoint_center")
        
        # Should still have corridors even without waypoint_center
        # (backward compatibility)
        if corridors:
            first_corridor = corridors[0]
            props = first_corridor.get("properties", {})
            # Corridors should still have in_perimeter (always True in this case)
            assert "in_perimeter" in props, "Missing in_perimeter property"
            print(f"PASS: Backward compat - corridors have in_perimeter property")
        
        print(f"PASS: Without waypoint_center - got {len(corridors)} corridors")

    def test_corridor_structure_v7(self):
        """Verify V7 corridor structure with all properties"""
        payload = {
            "bounds": {
                "north": 46.875,
                "south": 46.845,
                "east": -71.185,
                "west": -71.215
            },
            "species": "moose",
            "layers": ["habitats", "rut", "repos", "alimentation", "corridors"],
            "resolution": 60,
            "max_zones_per_layer": 8,
            "waypoint_center": {"lat": 46.86, "lng": -71.20}
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            timeout=60
        )
        
        assert response.status_code == 200
        data = response.json()
        corridors = data.get("corridors", [])
        
        if corridors:
            corridor = corridors[0]
            
            # Verify GeoJSON structure
            assert corridor.get("type") == "Feature", "Corridor should be a GeoJSON Feature"
            assert "geometry" in corridor, "Missing geometry"
            assert corridor["geometry"]["type"] == "LineString", "Geometry should be LineString"
            assert len(corridor["geometry"]["coordinates"]) > 0, "Coordinates array empty"
            
            # Verify properties
            props = corridor.get("properties", {})
            expected_props = [
                "trail_type", "corridor_type", "sex", "source", "confidence",
                "from_zone_type", "to_zone_type", "distance_m", "species",
                "style", "scoring", "in_perimeter"
            ]
            
            for prop in expected_props:
                assert prop in props, f"Missing property: {prop}"
            
            # Verify scoring structure
            scoring = props.get("scoring", {})
            assert "score" in scoring, "Missing score in scoring"
            assert "subscores" in scoring, "Missing subscores"
            assert "distance_m" in scoring, "Missing distance_m in scoring"
            
            # Verify style structure
            style = props.get("style", {})
            assert "color" in style, "Missing color in style"
            assert "width" in style, "Missing width in style"
            
            print(f"PASS: V7 corridor structure verified with all properties")
            print(f"  - trail_type: {props.get('trail_type')}")
            print(f"  - sex: {props.get('sex')}")
            print(f"  - source: {props.get('source')}")
            print(f"  - confidence: {props.get('confidence')}")
            print(f"  - in_perimeter: {props.get('in_perimeter')}")
            print(f"  - scoring.score: {scoring.get('score')}")
        else:
            print("INFO: No corridors generated (might need more zones)")


class TestCorridorFiltering:
    """Test the perimeter filtering logic"""
    
    def test_focused_bounds_with_waypoint_returns_perimeter_corridors(self):
        """
        Focused bounds + waypoint_center should return corridors with in_perimeter=True
        """
        # Very focused bounds around waypoint
        waypoint = {"lat": 46.86, "lng": -71.20}
        payload = {
            "bounds": {
                "north": waypoint["lat"] + 0.015,  # ~1.7km north
                "south": waypoint["lat"] - 0.015,
                "east": waypoint["lng"] + 0.015,
                "west": waypoint["lng"] - 0.015
            },
            "species": "moose",
            "layers": ["habitats", "rut", "repos", "alimentation", "corridors"],
            "resolution": 60,
            "max_zones_per_layer": 8,
            "waypoint_center": waypoint
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            timeout=60
        )
        
        assert response.status_code == 200
        data = response.json()
        corridors = data.get("corridors", [])
        
        # All corridors should have in_perimeter=True (filtered by 1500m radius)
        for corridor in corridors:
            props = corridor.get("properties", {})
            assert props.get("in_perimeter") == True, f"Corridor should be in perimeter"
        
        print(f"PASS: All {len(corridors)} corridors have in_perimeter=True")

    def test_v7_metadata_includes_corridor_info(self):
        """v7_metadata should include corridor count and styles"""
        payload = {
            "bounds": {"north": 46.875, "south": 46.845, "east": -71.185, "west": -71.215},
            "species": "moose",
            "layers": ["habitats", "rut", "repos", "alimentation", "corridors"],
            "waypoint_center": {"lat": 46.86, "lng": -71.20}
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            timeout=60
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check v7_metadata exists
        v7_meta = data.get("v7_metadata", {})
        
        if v7_meta:
            assert "corridor_count" in v7_meta, "Missing corridor_count in v7_metadata"
            assert "corridor_styles" in v7_meta, "Missing corridor_styles in v7_metadata"
            print(f"PASS: v7_metadata includes corridor_count={v7_meta.get('corridor_count')}")
        else:
            print("INFO: v7_metadata not present (engine version might be different)")


class TestWaypointCenterParameter:
    """Test the WaypointCenter parameter validation"""
    
    def test_waypoint_center_accepts_valid_coords(self):
        """Valid lat/lng should be accepted"""
        payload = {
            "bounds": {"north": 46.9, "south": 46.8, "east": -71.1, "west": -71.2},
            "species": "moose",
            "layers": ["habitats"],
            "waypoint_center": {"lat": 46.85, "lng": -71.15}
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            timeout=30
        )
        
        assert response.status_code == 200
        print("PASS: Valid waypoint_center accepted")

    def test_waypoint_center_optional(self):
        """waypoint_center should be optional (backward compat)"""
        payload = {
            "bounds": {"north": 46.9, "south": 46.8, "east": -71.1, "west": -71.2},
            "species": "moose",
            "layers": ["habitats"]
            # No waypoint_center
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            timeout=30
        )
        
        assert response.status_code == 200
        print("PASS: waypoint_center is optional (backward compat)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
