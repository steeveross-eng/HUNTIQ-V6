"""
Backend Test: User Data API (Waypoints & Places)
Tests P0 persistence: CRUD operations for waypoints, places, and sync endpoint
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
USER_ID = "steeve.ross@gmail.com"

class TestWaypointsAPI:
    """Waypoints CRUD tests with MongoDB persistence verification"""
    
    def test_get_waypoints_returns_list(self):
        """GET /api/user-data/waypoints/{user_id} returns list of waypoints"""
        response = requests.get(f"{BASE_URL}/api/user-data/waypoints/{USER_ID}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ GET waypoints: {len(data)} waypoints found")
    
    def test_get_waypoints_active_only(self):
        """GET with active_only=True filters inactive waypoints"""
        response = requests.get(f"{BASE_URL}/api/user-data/waypoints/{USER_ID}?active_only=true")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # All returned waypoints should be active
        for wp in data:
            assert wp.get('active') == True, f"Found inactive waypoint: {wp.get('name')}"
        print(f"✓ GET active waypoints: {len(data)} active waypoints")
    
    def test_create_waypoint_and_verify_persistence(self):
        """POST creates waypoint and GET verifies it exists in MongoDB"""
        create_payload = {
            "name": "TEST_Pytest_WP",
            "lat": 46.85,
            "lng": -71.25,
            "type": "observation",
            "active": True,
            "notes": "Created by pytest"
        }
        
        # CREATE
        create_response = requests.post(
            f"{BASE_URL}/api/user-data/waypoints/{USER_ID}",
            json=create_payload
        )
        assert create_response.status_code == 200
        created = create_response.json()
        assert "id" in created
        assert created["name"] == create_payload["name"]
        assert created["lat"] == create_payload["lat"]
        assert created["lng"] == create_payload["lng"]
        
        waypoint_id = created["id"]
        print(f"✓ Created waypoint: {created['name']} (ID: {waypoint_id})")
        
        # VERIFY PERSISTENCE via GET all
        get_response = requests.get(f"{BASE_URL}/api/user-data/waypoints/{USER_ID}")
        assert get_response.status_code == 200
        all_waypoints = get_response.json()
        
        found = next((w for w in all_waypoints if w.get('id') == waypoint_id), None)
        assert found is not None, f"Created waypoint {waypoint_id} not found in GET response"
        assert found["name"] == create_payload["name"]
        print(f"✓ Verified persistence: waypoint found in database")
        
        # CLEANUP
        delete_response = requests.delete(f"{BASE_URL}/api/user-data/waypoints/{USER_ID}/{waypoint_id}")
        assert delete_response.status_code == 200
        print(f"✓ Cleaned up test waypoint")
    
    def test_update_waypoint_and_verify_persistence(self):
        """PUT updates waypoint and GET verifies changes persisted"""
        # CREATE first
        create_response = requests.post(
            f"{BASE_URL}/api/user-data/waypoints/{USER_ID}",
            json={"name": "TEST_Update_WP", "lat": 46.86, "lng": -71.26, "type": "autre"}
        )
        assert create_response.status_code == 200
        waypoint_id = create_response.json()["id"]
        
        # UPDATE
        update_payload = {"name": "TEST_Update_WP_Modified", "notes": "Updated notes"}
        update_response = requests.put(
            f"{BASE_URL}/api/user-data/waypoints/{USER_ID}/{waypoint_id}",
            json=update_payload
        )
        assert update_response.status_code == 200
        updated = update_response.json()
        assert updated["name"] == "TEST_Update_WP_Modified"
        assert updated["notes"] == "Updated notes"
        print(f"✓ Updated waypoint name and notes")
        
        # VERIFY via GET
        get_response = requests.get(f"{BASE_URL}/api/user-data/waypoints/{USER_ID}")
        all_waypoints = get_response.json()
        found = next((w for w in all_waypoints if w.get('id') == waypoint_id), None)
        assert found is not None
        assert found["name"] == "TEST_Update_WP_Modified"
        print(f"✓ Verified update persisted in database")
        
        # CLEANUP
        requests.delete(f"{BASE_URL}/api/user-data/waypoints/{USER_ID}/{waypoint_id}")
    
    def test_delete_waypoint_and_verify_removal(self):
        """DELETE removes waypoint and GET confirms 404"""
        # CREATE first
        create_response = requests.post(
            f"{BASE_URL}/api/user-data/waypoints/{USER_ID}",
            json={"name": "TEST_Delete_WP", "lat": 46.87, "lng": -71.27, "type": "autre"}
        )
        waypoint_id = create_response.json()["id"]
        
        # DELETE
        delete_response = requests.delete(f"{BASE_URL}/api/user-data/waypoints/{USER_ID}/{waypoint_id}")
        assert delete_response.status_code == 200
        assert delete_response.json().get("status") == "deleted"
        print(f"✓ Deleted waypoint {waypoint_id}")
        
        # VERIFY REMOVAL - waypoint should not appear in list
        get_response = requests.get(f"{BASE_URL}/api/user-data/waypoints/{USER_ID}")
        all_waypoints = get_response.json()
        found = next((w for w in all_waypoints if w.get('id') == waypoint_id), None)
        assert found is None, f"Deleted waypoint {waypoint_id} still found in database"
        print(f"✓ Verified waypoint removed from database")
    
    def test_waypoint_validation_lat_lng(self):
        """POST with invalid lat/lng should fail validation"""
        # Invalid latitude > 90
        response = requests.post(
            f"{BASE_URL}/api/user-data/waypoints/{USER_ID}",
            json={"name": "Invalid WP", "lat": 100, "lng": -71.2, "type": "autre"}
        )
        assert response.status_code == 422, f"Expected 422 for invalid lat, got {response.status_code}"
        print(f"✓ Validation: rejected lat > 90")
        
        # Invalid longitude > 180
        response = requests.post(
            f"{BASE_URL}/api/user-data/waypoints/{USER_ID}",
            json={"name": "Invalid WP", "lat": 46.8, "lng": 200, "type": "autre"}
        )
        assert response.status_code == 422
        print(f"✓ Validation: rejected lng > 180")


class TestPlacesAPI:
    """Places CRUD tests"""
    
    def test_get_places_returns_list(self):
        """GET /api/user-data/places/{user_id} returns list"""
        response = requests.get(f"{BASE_URL}/api/user-data/places/{USER_ID}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ GET places: {len(data)} places found")
    
    def test_create_place_and_verify(self):
        """POST creates place with persistence"""
        create_payload = {
            "name": "TEST_Pytest_Place",
            "lat": 46.88,
            "lng": -71.28,
            "type": "parking",
            "notes": "Test parking"
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/user-data/places/{USER_ID}",
            json=create_payload
        )
        assert create_response.status_code == 200
        created = create_response.json()
        assert "id" in created
        assert created["name"] == create_payload["name"]
        print(f"✓ Created place: {created['name']}")
        
        place_id = created["id"]
        
        # VERIFY
        get_response = requests.get(f"{BASE_URL}/api/user-data/places/{USER_ID}")
        all_places = get_response.json()
        found = next((p for p in all_places if p.get('id') == place_id), None)
        assert found is not None
        print(f"✓ Verified place persisted")
        
        # CLEANUP
        requests.delete(f"{BASE_URL}/api/user-data/places/{USER_ID}/{place_id}")


class TestSyncAPI:
    """Sync endpoint tests"""
    
    def test_sync_creates_new_waypoints(self):
        """POST /api/user-data/sync creates non-existing waypoints"""
        unique_name = f"TEST_Sync_WP_{int(time.time())}"
        sync_payload = {
            "waypoints": [
                {"name": unique_name, "lat": 46.89, "lng": -71.29, "type": "autre", "active": True}
            ],
            "places": []
        }
        
        response = requests.post(
            f"{BASE_URL}/api/user-data/sync/{USER_ID}",
            json=sync_payload
        )
        assert response.status_code == 200
        data = response.json()
        assert "waypoints_synced" in data
        assert data["waypoints_synced"] == 1
        print(f"✓ Sync created 1 new waypoint")
        
        # VERIFY
        get_response = requests.get(f"{BASE_URL}/api/user-data/waypoints/{USER_ID}")
        all_waypoints = get_response.json()
        found = next((w for w in all_waypoints if w.get('name') == unique_name), None)
        assert found is not None
        print(f"✓ Verified synced waypoint exists")
        
        # CLEANUP
        if found:
            requests.delete(f"{BASE_URL}/api/user-data/waypoints/{USER_ID}/{found['id']}")
    
    def test_sync_skips_duplicates(self):
        """POST /api/user-data/sync skips existing waypoints (same name/lat/lng)"""
        # First sync
        sync_payload = {
            "waypoints": [
                {"name": "TEST_Sync_Dup", "lat": 46.90, "lng": -71.30, "type": "autre"}
            ],
            "places": []
        }
        
        response1 = requests.post(f"{BASE_URL}/api/user-data/sync/{USER_ID}", json=sync_payload)
        assert response1.status_code == 200
        first_count = response1.json()["waypoints_synced"]
        
        # Second sync with same data should skip
        response2 = requests.post(f"{BASE_URL}/api/user-data/sync/{USER_ID}", json=sync_payload)
        assert response2.status_code == 200
        second_count = response2.json()["waypoints_synced"]
        assert second_count == 0, f"Expected 0 synced (duplicate), got {second_count}"
        print(f"✓ Sync correctly skipped duplicate")
        
        # CLEANUP - find and delete
        get_response = requests.get(f"{BASE_URL}/api/user-data/waypoints/{USER_ID}")
        all_waypoints = get_response.json()
        dup = next((w for w in all_waypoints if w.get('name') == "TEST_Sync_Dup"), None)
        if dup:
            requests.delete(f"{BASE_URL}/api/user-data/waypoints/{USER_ID}/{dup['id']}")


class TestBackendWaypointExists:
    """Verify the pre-seeded 'Test Backend WP' exists for P0 testing"""
    
    def test_backend_waypoint_exists(self):
        """Verify 'Test Backend WP' at (46.81, -71.21) exists"""
        response = requests.get(f"{BASE_URL}/api/user-data/waypoints/{USER_ID}")
        assert response.status_code == 200
        waypoints = response.json()
        
        backend_wp = next((w for w in waypoints if w.get('name') == 'Test Backend WP'), None)
        assert backend_wp is not None, "Pre-seeded 'Test Backend WP' not found"
        assert abs(backend_wp.get('lat', 0) - 46.81) < 0.01
        assert abs(backend_wp.get('lng', 0) - (-71.21)) < 0.01
        print(f"✓ Found pre-seeded 'Test Backend WP' at ({backend_wp['lat']}, {backend_wp['lng']})")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
