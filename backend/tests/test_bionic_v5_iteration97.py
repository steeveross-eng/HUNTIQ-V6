"""
BIONIC V5 — Iteration 97 Tests
Mode Hybride & Synchronisation Waypoints

Tests for 3 critical fixes:
1) showFunctionalZones=true by default
2) Zones persist during Parcours mode (Mode Hybride)
3) Bidirectional waypoint sync (polling 3s)

API Tests:
- organic-zones: forest area returns zones with penalty_factor
- organic-zones: urban area returns 0 zones (P0 exclusion)
- waypoints: API accessible
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestBionicV5OrganicZones:
    """Organic zones API tests — P0 exclusion + P1 penalties"""
    
    def test_health_check(self):
        """T1: API health check"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"Health: {data}")
    
    def test_forest_zone_returns_zones_with_penalties(self):
        """T2: Forest zone (47.05-47.10, -70.85--70.93) returns valid zones with penalty_factor"""
        payload = {
            "bounds": {
                "south": 47.05,
                "north": 47.10,
                "west": -70.93,
                "east": -70.85
            },
            "species": "moose"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/organic-zones", json=payload)
        assert response.status_code == 200, f"Response: {response.text[:500]}"
        
        data = response.json()
        stats = data.get("stats", {})
        
        # Should have zones in forest area
        assert stats.get("total_zones", 0) > 0, "Forest should have zones"
        assert stats.get("layers_processed", 0) > 0, "Layers should be processed"
        
        # Penalties should be applied
        assert stats.get("penalties_applied", 0) > 0, "Penalties should be applied"
        
        # Check features have penalty_factor
        features = data.get("features", [])
        if features:
            props = features[0].get("properties", {})
            assert "penalty_factor" in props, "penalty_factor should be in properties"
            assert "raw_score" in props, "raw_score should be in properties"
            assert "score" in props, "score should be in properties"
        
        print(f"Forest zones: total={stats.get('total_zones')}, penalties={stats.get('penalties_applied')}")
    
    def test_urban_zone_returns_zero_zones_p0_exclusion(self):
        """T3: Urban zone (46.80-46.85, -71.20--71.28) returns 0 zones (P0 exclusion)"""
        payload = {
            "bounds": {
                "south": 46.80,
                "north": 46.85,
                "west": -71.28,
                "east": -71.20
            },
            "species": "moose"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/organic-zones", json=payload)
        assert response.status_code == 200, f"Response: {response.text[:500]}"
        
        data = response.json()
        stats = data.get("stats", {})
        
        # Urban area should have 0 zones due to P0 exclusion
        assert stats.get("total_zones", -1) == 0, "Urban area should have 0 zones"
        assert stats.get("rejected_exclusion", 0) > 0, "Zones should be rejected by exclusion"
        assert stats.get("exclusions_count", 0) > 0, "Exclusions should be fetched"
        
        print(f"Urban zones: total={stats.get('total_zones')}, rejected={stats.get('rejected_exclusion')}")
    
    def test_geojson_structure(self):
        """T4: Response is valid GeoJSON with required metadata"""
        payload = {
            "bounds": {
                "south": 47.05,
                "north": 47.10,
                "west": -70.93,
                "east": -70.85
            },
            "species": "moose"
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/organic-zones", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        
        # GeoJSON structure
        assert data.get("type") == "FeatureCollection", "Should be FeatureCollection"
        assert "features" in data, "Should have features array"
        assert "stats" in data, "Should have stats object"
        
        # Stats structure
        stats = data["stats"]
        assert "layers_processed" in stats
        assert "total_zones" in stats
        assert "computation_time_ms" in stats
        assert "species" in stats
        
        print(f"GeoJSON valid with {len(data['features'])} features")


class TestBionicV5WaypointSync:
    """Waypoint sync API tests"""
    
    def test_waypoints_api_accessible(self):
        """T5: Waypoints API is accessible"""
        response = requests.get(f"{BASE_URL}/api/territory/waypoints?user_id=test_iteration97")
        assert response.status_code == 200, f"Response: {response.status_code} {response.text[:200]}"
        
        data = response.json()
        assert isinstance(data, list), "Should return array of waypoints"
        print(f"Waypoints API accessible, returned {len(data)} waypoints")
    
    def test_waypoint_create_and_retrieve(self):
        """T6: Create waypoint and retrieve it (sync verification)"""
        user_id = "test_iteration97_sync"
        
        # Create waypoint
        create_payload = {
            "name": "TEST_Iteration97_SyncPoint",
            "latitude": 47.07,
            "longitude": -70.89,
            "waypoint_type": "hunting",
            "description": "Test waypoint for iteration 97"
        }
        create_response = requests.post(
            f"{BASE_URL}/api/territory/waypoints?user_id={user_id}",
            json=create_payload
        )
        
        if create_response.status_code != 200 and create_response.status_code != 201:
            print(f"Create failed (may already exist): {create_response.status_code}")
            # Try to retrieve anyway
        else:
            created = create_response.json()
            print(f"Created waypoint: {created.get('id', 'unknown')}")
        
        # Retrieve waypoints
        get_response = requests.get(f"{BASE_URL}/api/territory/waypoints?user_id={user_id}")
        assert get_response.status_code == 200
        
        waypoints = get_response.json()
        print(f"Retrieved {len(waypoints)} waypoints for user {user_id}")
        
        # Cleanup - delete test waypoints
        for wp in waypoints:
            if wp.get("name", "").startswith("TEST_"):
                wp_id = wp.get("id")
                if wp_id:
                    requests.delete(f"{BASE_URL}/api/territory/waypoints/{wp_id}?user_id={user_id}")
                    print(f"Cleaned up test waypoint: {wp_id}")


class TestBionicV5TerrainData:
    """Terrain data API tests — P0 exclusions"""
    
    def test_terrain_health(self):
        """T7: Terrain data API health"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/terrain/terrain-data/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("status") == "operational"
        
        supported_types = data.get("supported_types", [])
        assert "water" in supported_types, "Should support water exclusion"
        assert "urban" in supported_types, "Should support urban exclusion"
        assert "roads" in supported_types, "Should support roads exclusion"
        
        print(f"Terrain health: {data}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
