"""
P1-HOTSPOTS REFONTE API Tests
Tests for circular hotspots with natural perturbations:
- Circular shape (not random)
- Area 2000-3000 m²
- 100+ points per contour (Chaikin smoothing)
- fill_opacity=0 (transparent center)
- Colors by species (moose=#FF6B00, deer=#8B4513, bear=#4A4A4A)
"""

import pytest
import requests
import os
import math

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


def calculate_polygon_area_m2(coords):
    """Calculate polygon area in m² using Shoelace formula"""
    if len(coords) < 3:
        return 0.0
    
    n = len(coords)
    area_deg = 0
    for i in range(n - 1):
        area_deg += coords[i][0] * coords[i + 1][1]
        area_deg -= coords[i + 1][0] * coords[i][1]
    area_deg = abs(area_deg) / 2
    
    # Convert to m² (approximate at center latitude)
    center_lat = sum(c[1] for c in coords) / n
    meters_per_deg_lat = 111320
    meters_per_deg_lng = 111320 * math.cos(math.radians(center_lat))
    return area_deg * meters_per_deg_lat * meters_per_deg_lng


class TestHotspotCircularShape:
    """Test hotspots have circular shape with 2000-3000m² area"""
    
    def test_hotspot_area_in_range_moose(self):
        """Verify moose hotspot area is 2000-3000 m²"""
        payload = {
            "bounds": {"north": 47.0, "south": 46.5, "east": -71.0, "west": -71.5},
            "species": ["moose"],
            "time_range": "24h",
            "hotspot_types": ["activity_peak"],
            "min_score_threshold": 70
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/map/hotspots", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        
        if data["hotspots"]:
            coords = data["hotspots"][0]["geometry"]["coordinates"][0]
            area = calculate_polygon_area_m2(coords)
            print(f"Hotspot area: {area:.0f} m²")
            assert 1800 <= area <= 3200, f"Area {area} out of range 2000-3000m²"
    
    def test_hotspot_area_in_range_deer(self):
        """Verify deer hotspot area is 2000-3000 m²"""
        payload = {
            "bounds": {"north": 47.0, "south": 46.5, "east": -71.0, "west": -71.5},
            "species": ["deer"],
            "time_range": "24h",
            "hotspot_types": ["feeding_zone"],
            "min_score_threshold": 70
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/map/hotspots", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        
        if data["hotspots"]:
            coords = data["hotspots"][0]["geometry"]["coordinates"][0]
            area = calculate_polygon_area_m2(coords)
            print(f"Deer hotspot area: {area:.0f} m²")
            assert 1800 <= area <= 3200, f"Area {area} out of range 2000-3000m²"


class TestHotspotChaikinSmoothing:
    """Test hotspots have 100+ points (Chaikin smoothing)"""
    
    def test_hotspot_has_100_plus_points(self):
        """Verify hotspot contour has 100+ points for smooth rendering"""
        payload = {
            "bounds": {"north": 47.0, "south": 46.5, "east": -71.0, "west": -71.5},
            "species": ["moose"],
            "time_range": "24h",
            "hotspot_types": ["activity_peak"],
            "min_score_threshold": 70
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/map/hotspots", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        if data["hotspots"]:
            coords = data["hotspots"][0]["geometry"]["coordinates"][0]
            num_points = len(coords)
            print(f"Number of points in contour: {num_points}")
            assert num_points >= 100, f"Only {num_points} points, expected 100+ for Chaikin smoothing"
    
    def test_multiple_hotspots_have_smooth_contours(self):
        """Verify multiple hotspots all have smooth contours"""
        payload = {
            "bounds": {"north": 47.0, "south": 46.0, "east": -71.0, "west": -72.0},
            "species": ["moose"],
            "time_range": "24h",
            "hotspot_types": ["activity_peak", "feeding_zone", "rut_zone"],
            "min_score_threshold": 70
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/map/hotspots", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        for i, hs in enumerate(data.get("hotspots", [])[:5]):
            coords = hs["geometry"]["coordinates"][0]
            num_points = len(coords)
            print(f"Hotspot {i+1}: {num_points} points")
            assert num_points >= 100, f"Hotspot {i+1} has only {num_points} points"


class TestHotspotTransparentCenter:
    """Test hotspots have fill_opacity=0 (transparent center)"""
    
    def test_hotspot_fill_opacity_zero(self):
        """Verify fill_opacity is exactly 0 (transparent center)"""
        payload = {
            "bounds": {"north": 47.0, "south": 46.5, "east": -71.0, "west": -71.5},
            "species": ["moose"],
            "time_range": "24h",
            "hotspot_types": ["activity_peak"],
            "min_score_threshold": 70
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/map/hotspots", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        if data["hotspots"]:
            style = data["hotspots"][0]["style"]
            assert style["fill_opacity"] == 0.0, f"fill_opacity is {style['fill_opacity']}, expected 0.0"
    
    def test_all_hotspots_transparent_center(self):
        """Verify ALL hotspots have transparent centers"""
        payload = {
            "bounds": {"north": 47.0, "south": 46.0, "east": -71.0, "west": -72.0},
            "species": ["moose", "deer"],
            "time_range": "24h",
            "hotspot_types": ["activity_peak", "feeding_zone", "rut_zone"],
            "min_score_threshold": 70
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/map/hotspots", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        for i, hs in enumerate(data.get("hotspots", [])):
            style = hs["style"]
            assert style["fill_opacity"] == 0.0, f"Hotspot {i+1} has fill_opacity={style['fill_opacity']}"


class TestHotspotSpeciesColors:
    """Test hotspots have correct colors by species"""
    
    EXPECTED_COLORS = {
        "moose": "#FF6B00",      # Orange vif (Orignal)
        "deer": "#8B4513",       # Brun (Chevreuil)
        "bear": "#4A4A4A",       # Gris fonce (Ours)
        "wild_turkey": "#DAA520", # Or fonce (Dindon)
        "elk": "#CD853F"         # Peru (Wapiti)
    }
    
    def test_moose_color(self):
        """Verify moose hotspots are orange (#FF6B00)"""
        payload = {
            "bounds": {"north": 47.0, "south": 46.5, "east": -71.0, "west": -71.5},
            "species": ["moose"],
            "time_range": "24h",
            "hotspot_types": ["activity_peak"],
            "min_score_threshold": 70
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/map/hotspots", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        if data["hotspots"]:
            color = data["hotspots"][0]["style"]["stroke_color"]
            expected = self.EXPECTED_COLORS["moose"]
            assert color == expected, f"Moose color is {color}, expected {expected}"
    
    def test_deer_color(self):
        """Verify deer hotspots are brown (#8B4513)"""
        payload = {
            "bounds": {"north": 47.0, "south": 46.5, "east": -71.0, "west": -71.5},
            "species": ["deer"],
            "time_range": "24h",
            "hotspot_types": ["activity_peak"],
            "min_score_threshold": 70
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/map/hotspots", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        if data["hotspots"]:
            color = data["hotspots"][0]["style"]["stroke_color"]
            expected = self.EXPECTED_COLORS["deer"]
            assert color == expected, f"Deer color is {color}, expected {expected}"
    
    def test_contour_width_thin(self):
        """Verify contours are ultra-thin (1-2px)"""
        payload = {
            "bounds": {"north": 47.0, "south": 46.5, "east": -71.0, "west": -71.5},
            "species": ["moose"],
            "time_range": "24h",
            "hotspot_types": ["activity_peak"],
            "min_score_threshold": 70
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/map/hotspots", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        if data["hotspots"]:
            width = data["hotspots"][0]["style"]["stroke_width"]
            assert 1.0 <= width <= 2.0, f"Stroke width is {width}px, expected 1-2px"


class TestHotspotIntegration:
    """Integration tests for complete workflow"""
    
    def test_full_hotspot_workflow(self):
        """Test complete hotspot generation workflow"""
        payload = {
            "bounds": {"north": 47.0, "south": 46.0, "east": -71.0, "west": -72.0},
            "species": ["moose"],
            "time_range": "24h",
            "hotspot_types": ["activity_peak", "feeding_zone"],
            "min_score_threshold": 70
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/map/hotspots", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        
        # Verify statistics
        stats = data.get("statistics", {})
        assert "total_hotspots" in stats
        assert "by_type" in stats
        
        # Verify metadata
        metadata = data.get("metadata", {})
        assert "calculation_time_ms" in metadata
        
        print(f"Generated {stats.get('total_hotspots', 0)} hotspots")
        print(f"By type: {stats.get('by_type', {})}")
        print(f"Calculation time: {metadata.get('calculation_time_ms', 0):.1f}ms")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
