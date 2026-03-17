"""
Test User Waypoints and Places API
Tests CRUD operations for waypoints and places with MongoDB backend persistence
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://organic-zones-map.preview.emergentagent.com').rstrip('/')

# Test user ID for all tests
TEST_USER_ID = "pytest-test-user"


class TestWaypointsAPI:
    """Test waypoints CRUD operations"""
    
    created_waypoint_id = None
    
    def test_01_get_waypoints_empty_user(self):
        """GET /api/user-data/waypoints/{user_id} - Returns empty list for new user"""
        response = requests.get(f"{BASE_URL}/api/user-data/waypoints/{TEST_USER_ID}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ GET waypoints returns list (count: {len(data)})")
    
    def test_02_create_waypoint(self):
        """POST /api/user-data/waypoints/{user_id} - Creates a waypoint"""
        payload = {
            "name": "TEST_Affût Nord",
            "lat": 46.8500,
            "lng": -71.2500,
            "type": "affut",
            "active": True,
            "notes": "Test waypoint created by pytest"
        }
        response = requests.post(
            f"{BASE_URL}/api/user-data/waypoints/{TEST_USER_ID}",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "id" in data
        assert data["name"] == payload["name"]
        assert data["lat"] == payload["lat"]
        assert data["lng"] == payload["lng"]
        assert data["type"] == payload["type"]
        assert data["active"] == payload["active"]
        assert data["user_id"] == TEST_USER_ID
        assert "created_at" in data
        
        # Store ID for subsequent tests
        TestWaypointsAPI.created_waypoint_id = data["id"]
        print(f"✓ Created waypoint with ID: {data['id']}")
    
    def test_03_get_waypoints_after_create(self):
        """GET /api/user-data/waypoints/{user_id} - Verify waypoint persisted"""
        response = requests.get(f"{BASE_URL}/api/user-data/waypoints/{TEST_USER_ID}")
        assert response.status_code == 200
        data = response.json()
        
        # Find our created waypoint
        created_wp = next((wp for wp in data if wp["id"] == TestWaypointsAPI.created_waypoint_id), None)
        assert created_wp is not None, "Created waypoint not found in GET response"
        assert created_wp["name"] == "TEST_Affût Nord"
        print(f"✓ Waypoint persisted and retrieved (total: {len(data)})")
    
    def test_04_update_waypoint(self):
        """PUT /api/user-data/waypoints/{user_id}/{id} - Updates a waypoint"""
        assert TestWaypointsAPI.created_waypoint_id is not None, "No waypoint ID from create test"
        
        update_payload = {
            "name": "TEST_Affût Nord UPDATED",
            "notes": "Updated by pytest",
            "active": False
        }
        response = requests.put(
            f"{BASE_URL}/api/user-data/waypoints/{TEST_USER_ID}/{TestWaypointsAPI.created_waypoint_id}",
            json=update_payload
        )
        assert response.status_code == 200
        data = response.json()
        
        # Validate update
        assert data["name"] == update_payload["name"]
        assert data["notes"] == update_payload["notes"]
        assert data["active"] == update_payload["active"]
        assert "updated_at" in data and data["updated_at"] is not None
        print(f"✓ Waypoint updated successfully")
    
    def test_05_verify_update_persisted(self):
        """GET after PUT - Verify update persisted in database"""
        response = requests.get(f"{BASE_URL}/api/user-data/waypoints/{TEST_USER_ID}")
        assert response.status_code == 200
        data = response.json()
        
        updated_wp = next((wp for wp in data if wp["id"] == TestWaypointsAPI.created_waypoint_id), None)
        assert updated_wp is not None
        assert updated_wp["name"] == "TEST_Affût Nord UPDATED"
        assert updated_wp["active"] == False
        print(f"✓ Update persisted in database")
    
    def test_06_toggle_waypoint_active(self):
        """PATCH /api/user-data/waypoints/{user_id}/{id}/toggle - Toggle active status"""
        assert TestWaypointsAPI.created_waypoint_id is not None
        
        response = requests.patch(
            f"{BASE_URL}/api/user-data/waypoints/{TEST_USER_ID}/{TestWaypointsAPI.created_waypoint_id}/toggle"
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should toggle from False to True
        assert data["active"] == True
        print(f"✓ Waypoint toggled to active: {data['active']}")
    
    def test_07_get_active_only_waypoints(self):
        """GET /api/user-data/waypoints/{user_id}?active_only=true - Filter active waypoints"""
        response = requests.get(
            f"{BASE_URL}/api/user-data/waypoints/{TEST_USER_ID}",
            params={"active_only": True}
        )
        assert response.status_code == 200
        data = response.json()
        
        # All returned waypoints should be active
        for wp in data:
            assert wp["active"] == True
        print(f"✓ Active-only filter works (count: {len(data)})")
    
    def test_08_delete_waypoint(self):
        """DELETE /api/user-data/waypoints/{user_id}/{id} - Deletes a waypoint"""
        assert TestWaypointsAPI.created_waypoint_id is not None
        
        response = requests.delete(
            f"{BASE_URL}/api/user-data/waypoints/{TEST_USER_ID}/{TestWaypointsAPI.created_waypoint_id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == TestWaypointsAPI.created_waypoint_id
        print(f"✓ Waypoint deleted")
    
    def test_09_verify_delete(self):
        """GET after DELETE - Verify waypoint removed from database"""
        response = requests.get(f"{BASE_URL}/api/user-data/waypoints/{TEST_USER_ID}")
        assert response.status_code == 200
        data = response.json()
        
        deleted_wp = next((wp for wp in data if wp["id"] == TestWaypointsAPI.created_waypoint_id), None)
        assert deleted_wp is None, "Deleted waypoint still exists"
        print(f"✓ Waypoint removed from database")
    
    def test_10_delete_nonexistent_waypoint(self):
        """DELETE non-existent waypoint returns 404"""
        response = requests.delete(
            f"{BASE_URL}/api/user-data/waypoints/{TEST_USER_ID}/000000000000000000000000"
        )
        assert response.status_code == 404
        print(f"✓ 404 returned for non-existent waypoint")


class TestPlacesAPI:
    """Test places CRUD operations"""
    
    created_place_id = None
    
    def test_01_get_places_empty_user(self):
        """GET /api/user-data/places/{user_id} - Returns list for user"""
        response = requests.get(f"{BASE_URL}/api/user-data/places/{TEST_USER_ID}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ GET places returns list (count: {len(data)})")
    
    def test_02_create_place(self):
        """POST /api/user-data/places/{user_id} - Creates a place"""
        payload = {
            "name": "TEST_ZEC Batiscan",
            "lat": 46.9000,
            "lng": -72.5000,
            "type": "zec",
            "notes": "Test place created by pytest",
            "address": "123 Chemin de la ZEC",
            "phone": "418-555-1234"
        }
        response = requests.post(
            f"{BASE_URL}/api/user-data/places/{TEST_USER_ID}",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "id" in data
        assert data["name"] == payload["name"]
        assert data["lat"] == payload["lat"]
        assert data["lng"] == payload["lng"]
        assert data["type"] == payload["type"]
        assert data["notes"] == payload["notes"]
        assert data["address"] == payload["address"]
        assert data["phone"] == payload["phone"]
        assert data["user_id"] == TEST_USER_ID
        assert "created_at" in data
        
        TestPlacesAPI.created_place_id = data["id"]
        print(f"✓ Created place with ID: {data['id']}")
    
    def test_03_get_places_after_create(self):
        """GET /api/user-data/places/{user_id} - Verify place persisted"""
        response = requests.get(f"{BASE_URL}/api/user-data/places/{TEST_USER_ID}")
        assert response.status_code == 200
        data = response.json()
        
        created_place = next((p for p in data if p["id"] == TestPlacesAPI.created_place_id), None)
        assert created_place is not None, "Created place not found in GET response"
        assert created_place["name"] == "TEST_ZEC Batiscan"
        print(f"✓ Place persisted and retrieved (total: {len(data)})")
    
    def test_04_update_place(self):
        """PUT /api/user-data/places/{user_id}/{id} - Updates a place"""
        assert TestPlacesAPI.created_place_id is not None
        
        update_payload = {
            "name": "TEST_ZEC Batiscan UPDATED",
            "notes": "Updated by pytest",
            "rating": 4.5
        }
        response = requests.put(
            f"{BASE_URL}/api/user-data/places/{TEST_USER_ID}/{TestPlacesAPI.created_place_id}",
            json=update_payload
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == update_payload["name"]
        assert data["notes"] == update_payload["notes"]
        assert data["rating"] == update_payload["rating"]
        assert "updated_at" in data and data["updated_at"] is not None
        print(f"✓ Place updated successfully")
    
    def test_05_verify_update_persisted(self):
        """GET after PUT - Verify update persisted"""
        response = requests.get(f"{BASE_URL}/api/user-data/places/{TEST_USER_ID}")
        assert response.status_code == 200
        data = response.json()
        
        updated_place = next((p for p in data if p["id"] == TestPlacesAPI.created_place_id), None)
        assert updated_place is not None
        assert updated_place["name"] == "TEST_ZEC Batiscan UPDATED"
        assert updated_place["rating"] == 4.5
        print(f"✓ Update persisted in database")
    
    def test_06_filter_places_by_type(self):
        """GET /api/user-data/places/{user_id}?type=zec - Filter by type"""
        response = requests.get(
            f"{BASE_URL}/api/user-data/places/{TEST_USER_ID}",
            params={"type": "zec"}
        )
        assert response.status_code == 200
        data = response.json()
        
        for place in data:
            assert place["type"] == "zec"
        print(f"✓ Type filter works (count: {len(data)})")
    
    def test_07_delete_place(self):
        """DELETE /api/user-data/places/{user_id}/{id} - Deletes a place"""
        assert TestPlacesAPI.created_place_id is not None
        
        response = requests.delete(
            f"{BASE_URL}/api/user-data/places/{TEST_USER_ID}/{TestPlacesAPI.created_place_id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == TestPlacesAPI.created_place_id
        print(f"✓ Place deleted")
    
    def test_08_verify_delete(self):
        """GET after DELETE - Verify place removed"""
        response = requests.get(f"{BASE_URL}/api/user-data/places/{TEST_USER_ID}")
        assert response.status_code == 200
        data = response.json()
        
        deleted_place = next((p for p in data if p["id"] == TestPlacesAPI.created_place_id), None)
        assert deleted_place is None, "Deleted place still exists"
        print(f"✓ Place removed from database")


class TestSyncAPI:
    """Test sync and stats endpoints"""
    
    def test_01_sync_data(self):
        """POST /api/user-data/sync/{user_id} - Sync local data to backend"""
        payload = {
            "waypoints": [
                {
                    "name": "TEST_Sync Waypoint 1",
                    "lat": 46.7500,
                    "lng": -71.3000,
                    "type": "observation",
                    "active": True
                },
                {
                    "name": "TEST_Sync Waypoint 2",
                    "lat": 46.7600,
                    "lng": -71.3100,
                    "type": "saline",
                    "active": True
                }
            ],
            "places": [
                {
                    "name": "TEST_Sync Place 1",
                    "lat": 46.8000,
                    "lng": -71.4000,
                    "type": "pourvoirie"
                }
            ]
        }
        response = requests.post(
            f"{BASE_URL}/api/user-data/sync/{TEST_USER_ID}",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "waypoints_synced" in data
        assert "places_synced" in data
        assert "message" in data
        print(f"✓ Sync completed: {data['waypoints_synced']} waypoints, {data['places_synced']} places")
    
    def test_02_verify_sync_persisted(self):
        """Verify synced data is in database"""
        # Check waypoints
        wp_response = requests.get(f"{BASE_URL}/api/user-data/waypoints/{TEST_USER_ID}")
        assert wp_response.status_code == 200
        waypoints = wp_response.json()
        
        sync_wp = next((wp for wp in waypoints if "Sync Waypoint" in wp["name"]), None)
        assert sync_wp is not None, "Synced waypoint not found"
        
        # Check places
        places_response = requests.get(f"{BASE_URL}/api/user-data/places/{TEST_USER_ID}")
        assert places_response.status_code == 200
        places = places_response.json()
        
        sync_place = next((p for p in places if "Sync Place" in p["name"]), None)
        assert sync_place is not None, "Synced place not found"
        
        print(f"✓ Synced data persisted in database")
    
    def test_03_get_stats(self):
        """GET /api/user-data/stats/{user_id} - Get user data statistics"""
        response = requests.get(f"{BASE_URL}/api/user-data/stats/{TEST_USER_ID}")
        assert response.status_code == 200
        data = response.json()
        
        assert data["user_id"] == TEST_USER_ID
        assert "waypoints" in data
        assert "total" in data["waypoints"]
        assert "active" in data["waypoints"]
        assert "inactive" in data["waypoints"]
        assert "places" in data
        assert "total" in data["places"]
        assert "by_type" in data["places"]
        
        print(f"✓ Stats: {data['waypoints']['total']} waypoints, {data['places']['total']} places")
    
    def test_04_sync_duplicate_prevention(self):
        """POST /api/user-data/sync - Should not create duplicates"""
        # Sync same data again
        payload = {
            "waypoints": [
                {
                    "name": "TEST_Sync Waypoint 1",
                    "lat": 46.7500,
                    "lng": -71.3000,
                    "type": "observation",
                    "active": True
                }
            ],
            "places": []
        }
        response = requests.post(
            f"{BASE_URL}/api/user-data/sync/{TEST_USER_ID}",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should not sync duplicates (same name + coords)
        assert data["waypoints_synced"] == 0, "Duplicate waypoint was created"
        print(f"✓ Duplicate prevention works")


class TestBulkOperations:
    """Test bulk delete operations"""
    
    def test_01_bulk_delete_waypoints(self):
        """DELETE /api/user-data/waypoints/{user_id}/bulk - Delete all waypoints"""
        response = requests.delete(f"{BASE_URL}/api/user-data/waypoints/{TEST_USER_ID}/bulk")
        assert response.status_code == 200
        data = response.json()
        assert "deleted" in data
        print(f"✓ Bulk deleted {data['deleted']} waypoints")
    
    def test_02_verify_bulk_delete_waypoints(self):
        """Verify all waypoints deleted"""
        response = requests.get(f"{BASE_URL}/api/user-data/waypoints/{TEST_USER_ID}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0, f"Expected 0 waypoints, got {len(data)}"
        print(f"✓ All waypoints deleted")
    
    def test_03_bulk_delete_places(self):
        """DELETE /api/user-data/places/{user_id}/bulk - Delete all places"""
        response = requests.delete(f"{BASE_URL}/api/user-data/places/{TEST_USER_ID}/bulk")
        assert response.status_code == 200
        data = response.json()
        assert "deleted" in data
        print(f"✓ Bulk deleted {data['deleted']} places")
    
    def test_04_verify_bulk_delete_places(self):
        """Verify all places deleted"""
        response = requests.get(f"{BASE_URL}/api/user-data/places/{TEST_USER_ID}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0, f"Expected 0 places, got {len(data)}"
        print(f"✓ All places deleted")


class TestValidation:
    """Test input validation"""
    
    def test_01_create_waypoint_missing_name(self):
        """POST waypoint without name should fail validation"""
        payload = {
            "lat": 46.8500,
            "lng": -71.2500,
            "type": "affut"
        }
        response = requests.post(
            f"{BASE_URL}/api/user-data/waypoints/{TEST_USER_ID}",
            json=payload
        )
        assert response.status_code == 422  # Validation error
        print(f"✓ Validation error for missing name")
    
    def test_02_create_waypoint_invalid_lat(self):
        """POST waypoint with invalid latitude should fail"""
        payload = {
            "name": "Invalid Waypoint",
            "lat": 100.0,  # Invalid: must be -90 to 90
            "lng": -71.2500,
            "type": "affut"
        }
        response = requests.post(
            f"{BASE_URL}/api/user-data/waypoints/{TEST_USER_ID}",
            json=payload
        )
        assert response.status_code == 422
        print(f"✓ Validation error for invalid latitude")
    
    def test_03_create_waypoint_invalid_lng(self):
        """POST waypoint with invalid longitude should fail"""
        payload = {
            "name": "Invalid Waypoint",
            "lat": 46.8500,
            "lng": -200.0,  # Invalid: must be -180 to 180
            "type": "affut"
        }
        response = requests.post(
            f"{BASE_URL}/api/user-data/waypoints/{TEST_USER_ID}",
            json=payload
        )
        assert response.status_code == 422
        print(f"✓ Validation error for invalid longitude")
    
    def test_04_create_place_missing_name(self):
        """POST place without name should fail validation"""
        payload = {
            "lat": 46.9000,
            "lng": -72.5000,
            "type": "zec"
        }
        response = requests.post(
            f"{BASE_URL}/api/user-data/places/{TEST_USER_ID}",
            json=payload
        )
        assert response.status_code == 422
        print(f"✓ Validation error for missing place name")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
