"""
P1-HOTSPOTS API Tests
Test all map overlay endpoints for hotspots, zones, and corridors
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestP1HotspotsMapStatus:
    """Test GET /api/v1/bionic/map/status endpoint"""
    
    def test_map_status_returns_200(self):
        """Verify status endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/map/status")
        assert response.status_code == 200
        
    def test_map_status_module_info(self):
        """Verify status endpoint returns correct module info"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/map/status")
        data = response.json()
        
        assert data["module"] == "P1-HOTSPOTS"
        assert data["version"] == "1.0.0"
        assert data["status"] == "active"
        
    def test_map_status_endpoints_list(self):
        """Verify status lists all 3 endpoints"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/map/status")
        data = response.json()
        
        assert len(data["endpoints"]) == 3
        paths = [ep["path"] for ep in data["endpoints"]]
        assert "/api/v1/bionic/map/hotspots" in paths
        assert "/api/v1/bionic/map/zones" in paths
        assert "/api/v1/bionic/map/corridors" in paths
        
    def test_map_status_visual_spec(self):
        """Verify visual specifications"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/map/status")
        data = response.json()
        
        spec = data["visual_spec"]
        assert spec["fill_opacity"] == 0  # Transparent fill
        assert spec["smoothing"] == "chaikin"
        assert spec["effects"] == "none"


class TestP1HotspotsEndpoint:
    """Test POST /api/v1/bionic/map/hotspots endpoint"""
    
    def test_hotspots_returns_200(self):
        """Verify hotspots endpoint returns 200"""
        payload = {
            "bounds": {"north": 47.0, "south": 46.5, "east": -71.0, "west": -71.5},
            "species": ["moose"],
            "time_range": "24h",
            "hotspot_types": ["activity_peak"],
            "min_score_threshold": 70
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/map/hotspots",
            json=payload
        )
        assert response.status_code == 200
        
    def test_hotspots_success_response(self):
        """Verify hotspots returns success=true"""
        payload = {
            "bounds": {"north": 47.0, "south": 46.5, "east": -71.0, "west": -71.5},
            "species": ["moose"],
            "time_range": "24h",
            "hotspot_types": ["activity_peak", "feeding_zone"],
            "min_score_threshold": 70
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/map/hotspots",
            json=payload
        )
        data = response.json()
        
        assert data["success"] == True
        assert "hotspots" in data
        assert "statistics" in data
        assert "metadata" in data
        
    def test_hotspots_geojson_geometry(self):
        """Verify hotspots return valid GeoJSON Polygon geometry"""
        payload = {
            "bounds": {"north": 47.0, "south": 46.5, "east": -71.0, "west": -71.5},
            "species": ["moose"],
            "time_range": "24h",
            "hotspot_types": ["activity_peak"],
            "min_score_threshold": 70
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/map/hotspots",
            json=payload
        )
        data = response.json()
        
        if data["hotspots"]:
            hotspot = data["hotspots"][0]
            assert hotspot["geometry"]["type"] == "Polygon"
            assert "coordinates" in hotspot["geometry"]
            assert len(hotspot["geometry"]["coordinates"]) > 0
            
    def test_hotspots_style_transparent_fill(self):
        """Verify hotspots have transparent fill (fill_opacity=0)"""
        payload = {
            "bounds": {"north": 47.0, "south": 46.5, "east": -71.0, "west": -71.5},
            "species": ["moose"],
            "time_range": "24h",
            "hotspot_types": ["activity_peak"],
            "min_score_threshold": 70
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/map/hotspots",
            json=payload
        )
        data = response.json()
        
        if data["hotspots"]:
            hotspot = data["hotspots"][0]
            assert hotspot["style"]["fill_opacity"] == 0
            assert "stroke_color" in hotspot["style"]
            assert hotspot["style"]["stroke_width"] > 0
            
    def test_hotspots_metadata(self):
        """Verify hotspots have metadata"""
        payload = {
            "bounds": {"north": 47.0, "south": 46.5, "east": -71.0, "west": -71.5},
            "species": ["moose"],
            "time_range": "24h",
            "hotspot_types": ["activity_peak"],
            "min_score_threshold": 70
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/map/hotspots",
            json=payload
        )
        data = response.json()
        
        if data["hotspots"]:
            hotspot = data["hotspots"][0]
            assert "id" in hotspot
            assert "type" in hotspot
            assert "score" in hotspot
            assert "time_validity" in hotspot
            assert "species" in hotspot
            assert "metadata" in hotspot


class TestP1ZonesEndpoint:
    """Test POST /api/v1/bionic/map/zones endpoint"""
    
    def test_zones_returns_200(self):
        """Verify zones endpoint returns 200"""
        payload = {
            "bounds": {"north": 47.0, "south": 46.5, "east": -71.0, "west": -71.5},
            "species": "moose",
            "zone_types": ["feeding", "bedding"],
            "include_overlaps": True
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/map/zones",
            json=payload
        )
        assert response.status_code == 200
        
    def test_zones_success_response(self):
        """Verify zones returns success=true"""
        payload = {
            "bounds": {"north": 47.0, "south": 46.5, "east": -71.0, "west": -71.5},
            "species": "moose",
            "zone_types": ["feeding", "bedding", "water_access"],
            "include_overlaps": True
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/map/zones",
            json=payload
        )
        data = response.json()
        
        assert data["success"] == True
        assert "zones" in data
        assert "overlap_matrix" in data
        assert "metadata" in data
        
    def test_zones_geojson_geometry(self):
        """Verify zones return valid GeoJSON Polygon geometry"""
        payload = {
            "bounds": {"north": 47.0, "south": 46.5, "east": -71.0, "west": -71.5},
            "species": "moose",
            "zone_types": ["feeding"],
            "include_overlaps": False
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/map/zones",
            json=payload
        )
        data = response.json()
        
        if data["zones"]:
            zone = data["zones"][0]
            assert zone["geometry"]["type"] == "Polygon"
            assert "coordinates" in zone["geometry"]
            
    def test_zones_behavior_context(self):
        """Verify zones have behavior context"""
        payload = {
            "bounds": {"north": 47.0, "south": 46.5, "east": -71.0, "west": -71.5},
            "species": "moose",
            "zone_types": ["feeding"],
            "include_overlaps": False
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/map/zones",
            json=payload
        )
        data = response.json()
        
        if data["zones"]:
            zone = data["zones"][0]
            assert "behavior_context" in zone
            assert "primary_activity" in zone["behavior_context"]
            assert "time_of_day" in zone["behavior_context"]


class TestP1CorridorsEndpoint:
    """Test POST /api/v1/bionic/map/corridors endpoint"""
    
    def test_corridors_returns_200(self):
        """Verify corridors endpoint returns 200"""
        payload = {
            "bounds": {"north": 47.0, "south": 46.5, "east": -71.0, "west": -71.5},
            "species": "moose",
            "corridor_types": ["movement", "preferred"],
            "connect_zones": True
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/map/corridors",
            json=payload
        )
        assert response.status_code == 200
        
    def test_corridors_success_response(self):
        """Verify corridors returns success=true"""
        payload = {
            "bounds": {"north": 47.0, "south": 46.5, "east": -71.0, "west": -71.5},
            "species": "moose",
            "corridor_types": ["movement", "preferred", "feeding_transit"],
            "connect_zones": True
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/map/corridors",
            json=payload
        )
        data = response.json()
        
        assert data["success"] == True
        assert "corridors" in data
        assert "metadata" in data
        
    def test_corridors_geojson_linestring(self):
        """Verify corridors return valid GeoJSON LineString geometry"""
        payload = {
            "bounds": {"north": 47.0, "south": 46.5, "east": -71.0, "west": -71.5},
            "species": "moose",
            "corridor_types": ["preferred"],
            "connect_zones": True
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/map/corridors",
            json=payload
        )
        data = response.json()
        
        if data["corridors"]:
            corridor = data["corridors"][0]
            assert corridor["geometry"]["type"] == "LineString"
            assert "coordinates" in corridor["geometry"]
            
    def test_corridors_movement_context(self):
        """Verify corridors have movement context"""
        payload = {
            "bounds": {"north": 47.0, "south": 46.5, "east": -71.0, "west": -71.5},
            "species": "moose",
            "corridor_types": ["movement"],
            "connect_zones": True
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/map/corridors",
            json=payload
        )
        data = response.json()
        
        if data["corridors"]:
            corridor = data["corridors"][0]
            assert "movement_context" in corridor
            assert "direction" in corridor["movement_context"]
            assert "frequency" in corridor["movement_context"]
            assert "usage_probability" in corridor


class TestP1HotspotsEdgeCases:
    """Test edge cases and validation"""
    
    def test_hotspots_invalid_bounds(self):
        """Test with invalid bounds"""
        payload = {
            "bounds": {"north": 45.0, "south": 47.0, "east": -71.0, "west": -71.5},
            "species": ["moose"],
            "time_range": "24h",
            "hotspot_types": ["activity_peak"],
            "min_score_threshold": 70
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/map/hotspots",
            json=payload
        )
        # Should still return 200 but with empty or adjusted results
        assert response.status_code in [200, 400, 422]
        
    def test_hotspots_all_types(self):
        """Test requesting all hotspot types"""
        all_types = [
            "activity_peak", "feeding_zone", "rut_zone", "thermal_refuge",
            "water_source", "predation_risk", "snow_impact", "human_avoidance",
            "mineral_site", "composite_optimal"
        ]
        payload = {
            "bounds": {"north": 47.0, "south": 46.5, "east": -71.0, "west": -71.5},
            "species": ["moose"],
            "time_range": "24h",
            "hotspot_types": all_types,
            "min_score_threshold": 50
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/map/hotspots",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        
    def test_zones_all_types(self):
        """Test requesting all zone types"""
        all_zone_types = [
            "feeding", "bedding", "rut_arena", "thermal_cover",
            "water_access", "predation_zone", "yarding_zone"
        ]
        payload = {
            "bounds": {"north": 47.0, "south": 46.5, "east": -71.0, "west": -71.5},
            "species": "moose",
            "zone_types": all_zone_types,
            "include_overlaps": True
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/map/zones",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
