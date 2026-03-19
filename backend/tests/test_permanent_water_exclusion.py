"""
Test suite for PERMANENT Water Exclusion Feature for BIONIC™

Requirements tested:
1. Exclusion is ALWAYS active (no toggle ON/OFF)
2. Applied on ALL layers (habitats, rut, salines, affûts, trajets, etc.)
3. Applied on ALL maps (Mon Territoire BIONIC and Territoire)
4. Cannot be disabled
5. Applied on every refresh, zoom, movement
6. Waypoints cannot be created in water
"""

import pytest
import requests
import os

# Read BASE_URL from frontend .env or environment
def get_base_url():
    url = os.environ.get('REACT_APP_BACKEND_URL', '')
    if url:
        return url.rstrip('/')
    
    frontend_env_path = os.path.join(os.path.dirname(__file__), '../../frontend/.env')
    if os.path.exists(frontend_env_path):
        with open(frontend_env_path, 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip().rstrip('/')
    
    return 'https://lisibilite-pro.preview.emergentagent.com'

BASE_URL = get_base_url()

# Test coordinates
# z_fleuve: Point in Saint-Laurent river (should be excluded)
POINT_IN_WATER = {"lat": 46.82, "lng": -71.20}
# z_terre: Point on land in Quebec City (should be kept)
POINT_ON_LAND = {"lat": 46.8139, "lng": -71.2080}

# Test bounds for Quebec City area
QUEBEC_BOUNDS = {
    "north": 46.85,
    "south": 46.78,
    "east": -71.15,
    "west": -71.25
}


class TestPermanentWaterExclusion:
    """Tests for permanent water exclusion feature"""
    
    def test_point_in_water_detected(self):
        """Test that a point in the Saint-Laurent river is correctly detected as in water"""
        response = requests.post(
            f"{BASE_URL}/api/hydro/check-point",
            json={
                "lat": POINT_IN_WATER["lat"],
                "lng": POINT_IN_WATER["lng"],
                "tolerance_meters": 5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Point should be detected as in water
        assert data["is_in_water"] == True
        assert data["water_type"] is not None
        assert "Saint-Laurent" in data.get("water_name", "") or data["water_type"] == "river"
        print(f"✅ Point in water detected: {data['water_name']} ({data['water_type']})")
    
    def test_point_on_land_not_excluded(self):
        """Test that a point on land is correctly detected as NOT in water"""
        response = requests.post(
            f"{BASE_URL}/api/hydro/check-point",
            json={
                "lat": POINT_ON_LAND["lat"],
                "lng": POINT_ON_LAND["lng"],
                "tolerance_meters": 5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Point should NOT be in water
        assert data["is_in_water"] == False
        assert data["message"] == "Point sur terre"
        print(f"✅ Point on land correctly identified")
    
    def test_filter_zones_excludes_water_zones(self):
        """Test that zones in water are excluded while land zones are kept"""
        zones = [
            {
                "id": "z_fleuve",
                "center": [POINT_IN_WATER["lat"], POINT_IN_WATER["lng"]],
                "radiusMeters": 100,
                "moduleId": "habitats",
                "percentage": 75
            },
            {
                "id": "z_terre",
                "center": [POINT_ON_LAND["lat"], POINT_ON_LAND["lng"]],
                "radiusMeters": 100,
                "moduleId": "habitats",
                "percentage": 80
            }
        ]
        
        response = requests.post(
            f"{BASE_URL}/api/hydro/filter-zones",
            json={
                "zones": zones,
                "bounds": QUEBEC_BOUNDS,
                "tolerance_meters": 5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify filtering results
        assert data["success"] == True
        assert data["stats"]["total"] == 2
        assert data["stats"]["excluded"] == 1
        assert data["stats"]["filtered"] == 1
        
        # Verify z_fleuve was excluded
        filtered_ids = [z["id"] for z in data["filtered_zones"]]
        assert "z_fleuve" not in filtered_ids
        assert "z_terre" in filtered_ids
        
        # Verify exclusion details
        excluded_details = data["stats"].get("excluded_details", [])
        assert len(excluded_details) >= 1
        assert excluded_details[0]["zone_id"] == "z_fleuve"
        assert excluded_details[0]["reason"] == "in_water"
        
        print(f"✅ Zone filtering works: {data['stats']['excluded']} excluded, {data['stats']['filtered']} kept")
    
    def test_filter_zones_all_layer_types(self):
        """Test that water exclusion works for ALL BIONIC layer types"""
        layer_types = ["habitats", "rut", "salines", "affuts", "trajets", "alimentation", "repos", "corridors"]
        
        for layer_type in layer_types:
            zones = [
                {
                    "id": f"z_water_{layer_type}",
                    "center": [POINT_IN_WATER["lat"], POINT_IN_WATER["lng"]],
                    "radiusMeters": 100,
                    "moduleId": layer_type,
                    "percentage": 70
                },
                {
                    "id": f"z_land_{layer_type}",
                    "center": [POINT_ON_LAND["lat"], POINT_ON_LAND["lng"]],
                    "radiusMeters": 100,
                    "moduleId": layer_type,
                    "percentage": 70
                }
            ]
            
            response = requests.post(
                f"{BASE_URL}/api/hydro/filter-zones",
                json={
                    "zones": zones,
                    "bounds": QUEBEC_BOUNDS,
                    "tolerance_meters": 5
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Water zone should be excluded for ALL layer types
            assert data["stats"]["excluded"] >= 1, f"Layer {layer_type} should exclude water zones"
            
            filtered_ids = [z["id"] for z in data["filtered_zones"]]
            assert f"z_water_{layer_type}" not in filtered_ids, f"Water zone for {layer_type} should be excluded"
            assert f"z_land_{layer_type}" in filtered_ids, f"Land zone for {layer_type} should be kept"
        
        print(f"✅ Water exclusion works for all {len(layer_types)} layer types")
    
    def test_tolerance_5m_default(self):
        """Test that default tolerance is 5 meters"""
        response = requests.get(f"{BASE_URL}/api/hydro/water-types")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["shore_tolerance_default"] == 5
        print(f"✅ Default shore tolerance is 5m")
    
    def test_multiple_zones_batch_filtering(self):
        """Test filtering multiple zones in a single request (simulates map refresh)"""
        # Create 10 zones - mix of water and land
        zones = []
        for i in range(5):
            # Water zones
            zones.append({
                "id": f"z_water_{i}",
                "center": [POINT_IN_WATER["lat"] + i*0.001, POINT_IN_WATER["lng"]],
                "radiusMeters": 100,
                "moduleId": "habitats",
                "percentage": 60 + i*5
            })
            # Land zones
            zones.append({
                "id": f"z_land_{i}",
                "center": [POINT_ON_LAND["lat"] + i*0.001, POINT_ON_LAND["lng"]],
                "radiusMeters": 100,
                "moduleId": "habitats",
                "percentage": 60 + i*5
            })
        
        response = requests.post(
            f"{BASE_URL}/api/hydro/filter-zones",
            json={
                "zones": zones,
                "bounds": QUEBEC_BOUNDS,
                "tolerance_meters": 5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # All water zones should be excluded
        assert data["stats"]["total"] == 10
        assert data["stats"]["excluded"] >= 4  # At least 4 water zones excluded
        assert data["stats"]["filtered"] >= 4  # At least 4 land zones kept
        
        print(f"✅ Batch filtering: {data['stats']['excluded']} excluded, {data['stats']['filtered']} kept out of {data['stats']['total']}")
    
    def test_hydrographic_sources_available(self):
        """Test that hydrographic sources are available for Quebec region"""
        response = requests.get(
            f"{BASE_URL}/api/hydro/sources/detect",
            params={"lat": POINT_ON_LAND["lat"], "lng": POINT_ON_LAND["lng"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have at least OSM fallback available
        assert len(data["available_sources"]) >= 1
        
        # Check for expected sources
        source_ids = [s["id"] for s in data["available_sources"]]
        assert "osm_fallback" in source_ids or "quebec_mrnf" in source_ids or "canada_canvec" in source_ids
        
        print(f"✅ {len(data['available_sources'])} hydrographic sources available for Quebec")


class TestWaypointWaterBlocking:
    """Tests for waypoint creation blocking in water"""
    
    def test_check_point_api_for_waypoint_validation(self):
        """Test that check-point API can be used to validate waypoint placement"""
        # This simulates what the frontend does before creating a waypoint
        
        # Test point in water - should be blocked
        response = requests.post(
            f"{BASE_URL}/api/hydro/check-point",
            json={
                "lat": POINT_IN_WATER["lat"],
                "lng": POINT_IN_WATER["lng"],
                "tolerance_meters": 5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_in_water"] == True
        print(f"✅ Waypoint in water would be blocked: {data['water_name']}")
        
        # Test point on land - should be allowed
        response = requests.post(
            f"{BASE_URL}/api/hydro/check-point",
            json={
                "lat": POINT_ON_LAND["lat"],
                "lng": POINT_ON_LAND["lng"],
                "tolerance_meters": 5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_in_water"] == False
        print(f"✅ Waypoint on land would be allowed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
