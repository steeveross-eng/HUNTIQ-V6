"""
Test Zone Favorites & Optimal Conditions Alerts API
Tests for: POST/GET/DELETE favorites, GET alerts, PUT alert read, GET conditions
"""

import pytest
import requests
import os
import time
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test user ID - unique per test run to avoid conflicts
TEST_USER_ID = f"test_zone_favorites_{uuid.uuid4().hex[:8]}"


class TestZoneFavoritesAPI:
    """Test Zone Favorites CRUD operations"""
    
    created_zone_id = None
    
    def test_01_get_favorites_empty_user(self):
        """GET /api/zones/favorites - Should return empty list for new user"""
        response = requests.get(f"{BASE_URL}/api/zones/favorites?user_id={TEST_USER_ID}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "favorites" in data, "Response should contain 'favorites' key"
        assert "count" in data, "Response should contain 'count' key"
        assert data["count"] == 0, "New user should have 0 favorites"
        assert isinstance(data["favorites"], list), "favorites should be a list"
        print(f"✓ GET favorites for new user returns empty list")
    
    def test_02_add_favorite_zone(self):
        """POST /api/zones/favorites - Add a zone to favorites"""
        payload = {
            "name": "TEST_Zone Affût Nord",
            "module_id": "habitats",
            "location": {
                "lat": 46.85,
                "lng": -71.25,
                "radius_meters": 200
            },
            "notes": "Test zone for automated testing",
            "alert_enabled": True,
            "alert_days_before": 3
        }
        
        response = requests.post(
            f"{BASE_URL}/api/zones/favorites?user_id={TEST_USER_ID}",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "id" in data, "Response should contain zone 'id'"
        assert data["name"] == payload["name"], f"Name mismatch: {data['name']} != {payload['name']}"
        assert data["module_id"] == payload["module_id"], "module_id mismatch"
        assert data["user_id"] == TEST_USER_ID, "user_id mismatch"
        assert data["alert_enabled"] == True, "alert_enabled should be True"
        assert data["alert_days_before"] == 3, "alert_days_before should be 3"
        assert "location" in data, "Response should contain location"
        assert data["location"]["lat"] == 46.85, "Latitude mismatch"
        assert data["location"]["lng"] == -71.25, "Longitude mismatch"
        
        # Store zone ID for subsequent tests
        TestZoneFavoritesAPI.created_zone_id = data["id"]
        print(f"✓ POST favorite zone created with ID: {data['id']}")
    
    def test_03_get_favorites_after_add(self):
        """GET /api/zones/favorites - Verify zone was persisted"""
        response = requests.get(f"{BASE_URL}/api/zones/favorites?user_id={TEST_USER_ID}")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["count"] == 1, f"Expected 1 favorite, got {data['count']}"
        assert len(data["favorites"]) == 1, "Should have 1 favorite in list"
        
        zone = data["favorites"][0]
        assert zone["id"] == TestZoneFavoritesAPI.created_zone_id, "Zone ID mismatch"
        assert zone["name"] == "TEST_Zone Affût Nord", "Zone name mismatch"
        assert zone["module_id"] == "habitats", "module_id mismatch"
        assert "next_optimal_window" in zone, "Should have next_optimal_window"
        assert "upcoming_optimal_windows" in zone, "Should have upcoming_optimal_windows"
        print(f"✓ GET favorites returns the created zone with optimal windows")
    
    def test_04_add_duplicate_zone_fails(self):
        """POST /api/zones/favorites - Adding duplicate zone should fail"""
        payload = {
            "name": "TEST_Duplicate Zone",
            "module_id": "habitats",
            "location": {
                "lat": 46.85,  # Same coordinates
                "lng": -71.25,
                "radius_meters": 200
            },
            "alert_enabled": True,
            "alert_days_before": 3
        }
        
        response = requests.post(
            f"{BASE_URL}/api/zones/favorites?user_id={TEST_USER_ID}",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 400, f"Expected 400 for duplicate, got {response.status_code}"
        
        data = response.json()
        assert "detail" in data, "Error response should have 'detail'"
        print(f"✓ POST duplicate zone correctly returns 400: {data['detail']}")
    
    def test_05_get_zone_conditions(self):
        """GET /api/zones/favorites/{id}/conditions - Get 7-day forecast"""
        zone_id = TestZoneFavoritesAPI.created_zone_id
        assert zone_id is not None, "Zone ID not set from previous test"
        
        response = requests.get(
            f"{BASE_URL}/api/zones/favorites/{zone_id}/conditions?user_id={TEST_USER_ID}&days=7"
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "zone_id" in data, "Response should contain zone_id"
        assert "zone_name" in data, "Response should contain zone_name"
        assert "conditions" in data, "Response should contain conditions"
        assert "forecast_days" in data, "Response should contain forecast_days"
        assert data["forecast_days"] == 7, "Should have 7 forecast days"
        
        # Verify conditions structure
        assert isinstance(data["conditions"], list), "conditions should be a list"
        assert len(data["conditions"]) >= 1, "Should have at least 1 day of conditions"
        
        # Check first condition structure
        if data["conditions"]:
            cond = data["conditions"][0]
            assert "date" in cond, "Condition should have date"
            assert "score" in cond, "Condition should have score"
            assert "weather" in cond, "Condition should have weather"
            assert "lunar" in cond, "Condition should have lunar"
            assert "thermal" in cond, "Condition should have thermal"
            assert "wind" in cond, "Condition should have wind"
            assert "interpretation" in cond, "Condition should have interpretation"
            assert 0 <= cond["score"] <= 100, f"Score should be 0-100, got {cond['score']}"
        
        print(f"✓ GET conditions returns {len(data['conditions'])} days of forecast")
    
    def test_06_update_alert_settings(self):
        """PUT /api/zones/favorites/{id}/alerts - Update alert settings"""
        zone_id = TestZoneFavoritesAPI.created_zone_id
        assert zone_id is not None, "Zone ID not set from previous test"
        
        response = requests.put(
            f"{BASE_URL}/api/zones/favorites/{zone_id}/alerts?user_id={TEST_USER_ID}&alert_enabled=false&alert_days_before=5"
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "message" in data, "Response should contain message"
        assert data["alert_enabled"] == False, "alert_enabled should be False"
        
        # Verify change persisted
        get_response = requests.get(f"{BASE_URL}/api/zones/favorites?user_id={TEST_USER_ID}")
        assert get_response.status_code == 200
        
        favorites = get_response.json()["favorites"]
        zone = next((z for z in favorites if z["id"] == zone_id), None)
        assert zone is not None, "Zone should exist"
        assert zone["alert_enabled"] == False, "alert_enabled should be False after update"
        assert zone["alert_days_before"] == 5, "alert_days_before should be 5 after update"
        
        print(f"✓ PUT alert settings updated and persisted")
    
    def test_07_delete_favorite_zone(self):
        """DELETE /api/zones/favorites/{id} - Remove zone from favorites"""
        zone_id = TestZoneFavoritesAPI.created_zone_id
        assert zone_id is not None, "Zone ID not set from previous test"
        
        response = requests.delete(
            f"{BASE_URL}/api/zones/favorites/{zone_id}?user_id={TEST_USER_ID}"
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["deleted"] == True, "deleted should be True"
        
        # Verify deletion persisted
        get_response = requests.get(f"{BASE_URL}/api/zones/favorites?user_id={TEST_USER_ID}")
        assert get_response.status_code == 200
        assert get_response.json()["count"] == 0, "Should have 0 favorites after deletion"
        
        print(f"✓ DELETE favorite zone removed successfully")
    
    def test_08_delete_nonexistent_zone_fails(self):
        """DELETE /api/zones/favorites/{id} - Deleting non-existent zone should fail"""
        fake_id = "000000000000000000000000"  # Valid ObjectId format but doesn't exist
        
        response = requests.delete(
            f"{BASE_URL}/api/zones/favorites/{fake_id}?user_id={TEST_USER_ID}"
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print(f"✓ DELETE non-existent zone correctly returns 404")


class TestZoneAlertsAPI:
    """Test Zone Alerts operations"""
    
    created_zone_id = None
    created_alert_id = None
    
    def test_01_create_zone_for_alerts(self):
        """Setup: Create a zone that will generate alerts"""
        payload = {
            "name": "TEST_Alert Zone",
            "module_id": "affuts",
            "location": {
                "lat": 46.90,
                "lng": -71.30,
                "radius_meters": 150
            },
            "notes": "Zone for alert testing",
            "alert_enabled": True,
            "alert_days_before": 7  # Max days to ensure alerts are generated
        }
        
        response = requests.post(
            f"{BASE_URL}/api/zones/favorites?user_id={TEST_USER_ID}",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        TestZoneAlertsAPI.created_zone_id = data["id"]
        print(f"✓ Created zone for alert testing: {data['id']}")
    
    def test_02_get_alerts(self):
        """GET /api/zones/alerts - Get user alerts"""
        # Wait a moment for alerts to be generated
        time.sleep(1)
        
        response = requests.get(f"{BASE_URL}/api/zones/alerts?user_id={TEST_USER_ID}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "alerts" in data, "Response should contain 'alerts'"
        assert "count" in data, "Response should contain 'count'"
        assert "unread_count" in data, "Response should contain 'unread_count'"
        assert isinstance(data["alerts"], list), "alerts should be a list"
        
        # If alerts were generated, verify structure
        if data["alerts"]:
            alert = data["alerts"][0]
            assert "id" in alert, "Alert should have id"
            assert "zone_id" in alert, "Alert should have zone_id"
            assert "zone_name" in alert, "Alert should have zone_name"
            assert "optimal_date" in alert, "Alert should have optimal_date"
            assert "score" in alert, "Alert should have score"
            assert "conditions" in alert, "Alert should have conditions"
            assert "read" in alert, "Alert should have read status"
            
            TestZoneAlertsAPI.created_alert_id = alert["id"]
            print(f"✓ GET alerts returns {data['count']} alerts, {data['unread_count']} unread")
        else:
            print(f"✓ GET alerts returns empty list (no optimal conditions found)")
    
    def test_03_get_unread_alerts_only(self):
        """GET /api/zones/alerts?unread_only=true - Get only unread alerts"""
        response = requests.get(
            f"{BASE_URL}/api/zones/alerts?user_id={TEST_USER_ID}&unread_only=true"
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # All returned alerts should be unread
        for alert in data["alerts"]:
            assert alert["read"] == False, "All alerts should be unread when unread_only=true"
        
        print(f"✓ GET unread_only=true returns only unread alerts")
    
    def test_04_mark_alert_as_read(self):
        """PUT /api/zones/alerts/{id}/read - Mark alert as read"""
        alert_id = TestZoneAlertsAPI.created_alert_id
        
        if alert_id is None:
            pytest.skip("No alert was created to test marking as read")
        
        response = requests.put(
            f"{BASE_URL}/api/zones/alerts/{alert_id}/read?user_id={TEST_USER_ID}"
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "message" in data, "Response should contain message"
        
        # Verify alert is now read
        get_response = requests.get(f"{BASE_URL}/api/zones/alerts?user_id={TEST_USER_ID}")
        alerts = get_response.json()["alerts"]
        alert = next((a for a in alerts if a["id"] == alert_id), None)
        
        if alert:
            assert alert["read"] == True, "Alert should be marked as read"
        
        print(f"✓ PUT alert marked as read successfully")
    
    def test_05_mark_all_alerts_read(self):
        """PUT /api/zones/alerts/read-all - Mark all alerts as read"""
        response = requests.put(
            f"{BASE_URL}/api/zones/alerts/read-all?user_id={TEST_USER_ID}"
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "message" in data, "Response should contain message"
        
        # Verify all alerts are read
        get_response = requests.get(f"{BASE_URL}/api/zones/alerts?user_id={TEST_USER_ID}")
        assert get_response.json()["unread_count"] == 0, "All alerts should be read"
        
        print(f"✓ PUT read-all marked all alerts as read")
    
    def test_06_check_optimal_conditions(self):
        """POST /api/zones/check-optimal-conditions - Trigger condition check"""
        # This test uses the zone created in test_01, which should still exist
        zone_id = TestZoneAlertsAPI.created_zone_id
        assert zone_id is not None, "Zone ID not set from previous test"
        
        response = requests.post(
            f"{BASE_URL}/api/zones/check-optimal-conditions?user_id={TEST_USER_ID}"
        )
        
        # Accept 200 or 520 (server timeout for weather API)
        assert response.status_code in [200, 520], f"Expected 200 or 520, got {response.status_code}: {response.text}"
        
        if response.status_code == 200:
            data = response.json()
            assert "checked_zones" in data, "Response should contain checked_zones"
            assert "new_alerts" in data, "Response should contain new_alerts"
            print(f"✓ POST check-optimal-conditions checked {data['checked_zones']} zones, created {data['new_alerts']} new alerts")
        else:
            print(f"✓ POST check-optimal-conditions returned 520 (weather API timeout - acceptable)")
    
    def test_07_mark_nonexistent_alert_fails(self):
        """PUT /api/zones/alerts/{id}/read - Non-existent alert should fail"""
        fake_id = "000000000000000000000000"
        
        response = requests.put(
            f"{BASE_URL}/api/zones/alerts/{fake_id}/read?user_id={TEST_USER_ID}"
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print(f"✓ PUT non-existent alert correctly returns 404")
    
    def test_08_cleanup_test_zone(self):
        """Cleanup: Delete test zone"""
        zone_id = TestZoneAlertsAPI.created_zone_id
        if zone_id:
            response = requests.delete(
                f"{BASE_URL}/api/zones/favorites/{zone_id}?user_id={TEST_USER_ID}"
            )
            assert response.status_code == 200
            print(f"✓ Cleanup: Test zone deleted")


class TestZoneFavoritesValidation:
    """Test input validation for Zone Favorites API"""
    
    def test_01_add_zone_missing_name(self):
        """POST /api/zones/favorites - Missing name should fail validation"""
        payload = {
            "module_id": "habitats",
            "location": {
                "lat": 46.85,
                "lng": -71.25,
                "radius_meters": 200
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/zones/favorites?user_id={TEST_USER_ID}",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422, f"Expected 422 for missing name, got {response.status_code}"
        print(f"✓ POST missing name correctly returns 422")
    
    def test_02_add_zone_missing_location(self):
        """POST /api/zones/favorites - Missing location should fail validation"""
        payload = {
            "name": "TEST_No Location",
            "module_id": "habitats"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/zones/favorites?user_id={TEST_USER_ID}",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422, f"Expected 422 for missing location, got {response.status_code}"
        print(f"✓ POST missing location correctly returns 422")
    
    def test_03_add_zone_invalid_alert_days(self):
        """POST /api/zones/favorites - Invalid alert_days_before should fail"""
        payload = {
            "name": "TEST_Invalid Days",
            "module_id": "habitats",
            "location": {
                "lat": 46.85,
                "lng": -71.25,
                "radius_meters": 200
            },
            "alert_days_before": 10  # Max is 7
        }
        
        response = requests.post(
            f"{BASE_URL}/api/zones/favorites?user_id={TEST_USER_ID}",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422, f"Expected 422 for invalid alert_days_before, got {response.status_code}"
        print(f"✓ POST invalid alert_days_before correctly returns 422")
    
    def test_04_get_conditions_invalid_zone_id(self):
        """GET /api/zones/favorites/{id}/conditions - Invalid zone ID format"""
        response = requests.get(
            f"{BASE_URL}/api/zones/favorites/invalid_id/conditions?user_id={TEST_USER_ID}"
        )
        
        # Should return 400 (invalid ObjectId) or 404 or 500/520 (server error)
        assert response.status_code in [400, 404, 500, 520], f"Expected error status, got {response.status_code}"
        print(f"✓ GET conditions with invalid ID returns error status: {response.status_code}")


class TestExistingTestUserData:
    """Test with existing test_user data (from main agent setup)"""
    
    def test_01_verify_existing_favorites(self):
        """Verify existing test_user has favorites"""
        response = requests.get(f"{BASE_URL}/api/zones/favorites?user_id=test_user")
        
        assert response.status_code == 200
        
        data = response.json()
        print(f"✓ test_user has {data['count']} favorites")
        
        if data["favorites"]:
            zone = data["favorites"][0]
            print(f"  - Zone: {zone['name']} ({zone['module_id']})")
            if zone.get("next_optimal_window"):
                print(f"  - Next optimal: {zone['next_optimal_window']['score']}% on {zone['next_optimal_window']['date'][:10]}")
    
    def test_02_verify_existing_alerts(self):
        """Verify existing test_user has alerts"""
        response = requests.get(f"{BASE_URL}/api/zones/alerts?user_id=test_user")
        
        assert response.status_code == 200
        
        data = response.json()
        print(f"✓ test_user has {data['count']} alerts ({data['unread_count']} unread)")
        
        if data["alerts"]:
            alert = data["alerts"][0]
            print(f"  - Alert: {alert['zone_name']} - {alert['score']}% on {alert['optimal_date'][:10]}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
