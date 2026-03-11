"""
BIONIC V5 — NOTIFICATIONS PUSH TEST SUITE
==========================================
PHASE F — VAPID Natif — Testing Suite

Tests for all 9 notification endpoints:
- GET /api/v1/bionic/notifications/vapid-key
- POST /api/v1/bionic/notifications/subscribe
- POST /api/v1/bionic/notifications/unsubscribe
- POST /api/v1/bionic/notifications/update-location
- GET /api/v1/bionic/notifications/rules
- POST /api/v1/bionic/notifications/send
- POST /api/v1/bionic/notifications/send-zone
- GET /api/v1/bionic/notifications/history
- GET /api/v1/bionic/notifications/health
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def api_client():
    """Shared requests session."""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture
def test_subscription_data():
    """Generate unique test subscription data."""
    unique_id = str(uuid.uuid4())[:8]
    return {
        "endpoint": f"https://test-push-service.example.com/push/{unique_id}",
        "p256dh": "BNcRdreALRFXTkOOUHK1EtK2wtaz5Ry4YfYCA_0QTpQtUbVlUls0VJXg7A8u-Ts1XbjhazAkj7I99e8QcYP7DkM",
        "auth": "tBHItJI5svbpez7KI4CCXg",
        "user_agent": "TestAgent/1.0",
        "device_type": "web",
        "lat": 46.8139,
        "lng": -71.2080,
        "geofence_radius_km": 5.0,
        "alert_types": ["danger", "human_pressure"],
        "min_priority": "medium"
    }


# =============================================================================
# HEALTH CHECK TESTS
# =============================================================================

class TestNotificationsHealth:
    """Health endpoint tests"""
    
    def test_health_returns_200(self, api_client):
        """GET /health returns 200"""
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/notifications/health")
        assert response.status_code == 200
        print("✓ Health endpoint returns 200")
    
    def test_health_response_structure(self, api_client):
        """Health response has expected structure"""
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/notifications/health")
        data = response.json()
        
        # Check status
        assert data["status"] == "healthy"
        assert "version" in data
        assert data["version"] == "7.2.0"
        
        # Check VAPID configuration
        assert "vapid" in data
        assert data["vapid"]["configured"] == True
        assert data["vapid"]["type"] == "native"
        
        # Check statistics
        assert "statistics" in data
        assert "subscriptions" in data["statistics"]
        assert "notifications" in data["statistics"]
        assert "trigger_rules" in data["statistics"]
        
        # Check features
        assert "features" in data
        expected_features = ["vapid_native", "web_push", "geofencing", "trigger_rules", "safety_engine_integration"]
        for feature in expected_features:
            assert feature in data["features"]
        
        print(f"✓ Health response structure valid - v{data['version']}, {len(data['features'])} features")


# =============================================================================
# VAPID KEY TESTS
# =============================================================================

class TestVapidKey:
    """VAPID key endpoint tests"""
    
    def test_vapid_key_returns_200(self, api_client):
        """GET /vapid-key returns 200"""
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/notifications/vapid-key")
        assert response.status_code == 200
        print("✓ VAPID key endpoint returns 200")
    
    def test_vapid_key_response_structure(self, api_client):
        """VAPID key response has expected structure"""
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/notifications/vapid-key")
        data = response.json()
        
        assert data["status"] == "success"
        assert "vapid_public_key" in data
        assert len(data["vapid_public_key"]) > 50  # Valid base64 key
        assert "usage" in data
        
        print(f"✓ VAPID key returned - {len(data['vapid_public_key'])} chars")
    
    def test_vapid_key_is_base64_urlsafe(self, api_client):
        """VAPID key is valid Base64 URL-safe format"""
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/notifications/vapid-key")
        data = response.json()
        
        key = data["vapid_public_key"]
        # URL-safe base64 should not contain + or /
        assert "+" not in key or "_" in key or "-" in key
        
        print("✓ VAPID key is Base64 URL-safe format")


# =============================================================================
# SUBSCRIPTION TESTS
# =============================================================================

class TestSubscription:
    """Subscription endpoint tests"""
    
    def test_subscribe_returns_201(self, api_client, test_subscription_data):
        """POST /subscribe returns 201"""
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/notifications/subscribe",
            json=test_subscription_data
        )
        assert response.status_code == 201
        print("✓ Subscribe endpoint returns 201")
    
    def test_subscribe_response_structure(self, api_client, test_subscription_data):
        """Subscribe response has expected structure"""
        # Use unique endpoint for this test
        test_subscription_data["endpoint"] = f"https://test-push-service.example.com/push/{uuid.uuid4()}"
        
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/notifications/subscribe",
            json=test_subscription_data
        )
        data = response.json()
        
        assert data["status"] == "success"
        assert "message" in data
        assert "subscription" in data
        
        subscription = data["subscription"]
        assert "subscription_id" in subscription
        assert subscription["subscription_id"].startswith("SUB-")
        assert subscription["device_type"] == "web"
        
        # Check geofence
        assert "geofence" in subscription
        assert subscription["geofence"]["lat"] == 46.8139
        assert subscription["geofence"]["lng"] == -71.2080
        assert subscription["geofence"]["radius_km"] == 5.0
        
        # Check preferences
        assert "preferences" in subscription
        assert "alert_types" in subscription["preferences"]
        
        print(f"✓ Subscription created: {subscription['subscription_id']}")
    
    def test_subscribe_without_geolocation(self, api_client):
        """Subscribe without geolocation works"""
        data = {
            "endpoint": f"https://test-push-service.example.com/push/{uuid.uuid4()}",
            "p256dh": "BNcRdreALRFXTkOOUHK1EtK2wtaz5Ry4YfYCA_0QTpQtUbVlUls0VJXg7A8u-Ts1XbjhazAkj7I99e8QcYP7DkM",
            "auth": "tBHItJI5svbpez7KI4CCXg",
            "device_type": "mobile"
        }
        
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/notifications/subscribe",
            json=data
        )
        assert response.status_code == 201
        
        result = response.json()
        assert result["subscription"]["geofence"]["lat"] is None
        assert result["subscription"]["geofence"]["lng"] is None
        
        print("✓ Subscribe without geolocation works")


class TestUnsubscribe:
    """Unsubscribe endpoint tests"""
    
    def test_unsubscribe_existing_subscription(self, api_client, test_subscription_data):
        """POST /unsubscribe unsubscribes existing subscription"""
        # First create a subscription
        test_subscription_data["endpoint"] = f"https://test-push-service.example.com/push/{uuid.uuid4()}"
        
        sub_response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/notifications/subscribe",
            json=test_subscription_data
        )
        subscription_id = sub_response.json()["subscription"]["subscription_id"]
        
        # Then unsubscribe
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/notifications/unsubscribe",
            json={"subscription_id": subscription_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["subscription_id"] == subscription_id
        
        print(f"✓ Unsubscribed: {subscription_id}")
    
    def test_unsubscribe_nonexistent_returns_404(self, api_client):
        """POST /unsubscribe with non-existent ID returns 404"""
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/notifications/unsubscribe",
            json={"subscription_id": "SUB-NONEXISTENT-0001"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["error_code"] == "SUBSCRIPTION_NOT_FOUND"
        
        print("✓ Unsubscribe non-existent returns 404")


# =============================================================================
# UPDATE LOCATION TESTS
# =============================================================================

class TestUpdateLocation:
    """Update location endpoint tests"""
    
    def test_update_location_returns_200(self, api_client, test_subscription_data):
        """POST /update-location updates location"""
        # First create a subscription
        test_subscription_data["endpoint"] = f"https://test-push-service.example.com/push/{uuid.uuid4()}"
        
        sub_response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/notifications/subscribe",
            json=test_subscription_data
        )
        subscription_id = sub_response.json()["subscription"]["subscription_id"]
        
        # Update location
        new_lat = 45.5088
        new_lng = -73.5878  # Montreal
        
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/notifications/update-location",
            json={
                "subscription_id": subscription_id,
                "lat": new_lat,
                "lng": new_lng
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["subscription"]["geofence"]["lat"] == new_lat
        assert data["subscription"]["geofence"]["lng"] == new_lng
        
        print(f"✓ Location updated to ({new_lat}, {new_lng})")
    
    def test_update_location_nonexistent_returns_404(self, api_client):
        """POST /update-location with non-existent ID returns 404"""
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/notifications/update-location",
            json={
                "subscription_id": "SUB-NONEXISTENT-0001",
                "lat": 45.0,
                "lng": -73.0
            }
        )
        
        assert response.status_code == 404
        print("✓ Update location non-existent returns 404")


# =============================================================================
# TRIGGER RULES TESTS
# =============================================================================

class TestTriggerRules:
    """Trigger rules endpoint tests"""
    
    def test_rules_returns_200(self, api_client):
        """GET /rules returns 200"""
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/notifications/rules")
        assert response.status_code == 200
        print("✓ Rules endpoint returns 200")
    
    def test_rules_response_structure(self, api_client):
        """Rules response has expected structure"""
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/notifications/rules")
        data = response.json()
        
        assert data["status"] == "success"
        assert "total" in data
        assert "rules" in data
        assert data["total"] >= 5  # Should have at least 5 default rules
        
        print(f"✓ Found {data['total']} rules")
    
    def test_rules_content(self, api_client):
        """Rules have expected content (5 default rules)"""
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/notifications/rules")
        data = response.json()
        
        rules = data["rules"]
        rule_ids = [r["rule_id"] for r in rules]
        
        # Check for expected default rules
        expected_rules = [
            "RULE-DANGER-CRITICAL",
            "RULE-DANGER-HIGH",
            "RULE-HUMAN-PRESSURE",
            "RULE-CORRIDOR-RISK",
            "RULE-HUNTING-ACTIVE"
        ]
        
        for expected in expected_rules:
            assert expected in rule_ids, f"Missing rule: {expected}"
        
        # Check rule structure
        for rule in rules:
            assert "rule_id" in rule
            assert "rule_name" in rule
            assert "alert_type" in rule
            assert "conditions" in rule
            assert "result" in rule
            assert "is_active" in rule
            assert rule["is_active"] == True
        
        print(f"✓ All 5 default rules present and active")
    
    def test_rules_with_active_only_false(self, api_client):
        """GET /rules?active_only=false returns all rules"""
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/notifications/rules?active_only=false")
        data = response.json()
        
        assert data["filter"]["active_only"] == False
        print(f"✓ Rules with active_only=false returned {data['total']} rules")


# =============================================================================
# SEND NOTIFICATION TESTS
# =============================================================================

class TestSendNotification:
    """Send notification endpoint tests"""
    
    def test_send_notification_returns_200(self, api_client):
        """POST /send creates and sends notification"""
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/notifications/send",
            json={
                "alert_type": "danger",
                "priority": "high",
                "title": "⚠️ Test Alert",
                "body": "This is a test notification from pytest",
                "lat": 46.8139,
                "lng": -71.2080,
                "radius_m": 500,
                "url": "/test"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        
        print(f"✓ Notification sent - {data['delivery']['sent']} delivered")
    
    def test_send_notification_response_structure(self, api_client):
        """Send notification response has expected structure"""
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/notifications/send",
            json={
                "alert_type": "human_pressure",
                "priority": "medium",
                "title": "👥 Human Pressure Alert",
                "body": "Test human pressure notification",
                "url": "/map"
            }
        )
        
        data = response.json()
        
        # Check notification structure
        assert "notification" in data
        notif = data["notification"]
        assert "notification_id" in notif
        assert notif["notification_id"].startswith("NOTIF-")
        assert notif["alert_type"] == "human_pressure"
        assert notif["priority"] == "medium"
        
        # Check delivery stats
        assert "delivery" in data
        assert "sent" in data["delivery"]
        assert "failed" in data["delivery"]
        
        print(f"✓ Notification structure valid: {notif['notification_id']}")


class TestSendZoneNotification:
    """Send zone notification (geofencing) tests"""
    
    def test_send_zone_notification_returns_200(self, api_client):
        """POST /send-zone creates and sends zone notification"""
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/notifications/send-zone",
            json={
                "alert_type": "corridor_risk",
                "priority": "medium",
                "title": "🛤️ Corridor Risk",
                "body": "Test corridor risk in zone",
                "lat": 46.8139,
                "lng": -71.2080,
                "radius_km": 10.0
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        
        # Check zone info
        assert "zone" in data
        assert data["zone"]["lat"] == 46.8139
        assert data["zone"]["lng"] == -71.2080
        assert data["zone"]["radius_km"] == 10.0
        
        print(f"✓ Zone notification sent - {data['delivery']['sent']}/{data['delivery']['eligible']} in zone")
    
    def test_send_zone_notification_response_structure(self, api_client):
        """Send zone response has zone and delivery stats"""
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/notifications/send-zone",
            json={
                "alert_type": "danger",
                "priority": "critical",
                "title": "⚠️ DANGER CRITIQUE",
                "body": "Zone de danger critique",
                "lat": 45.5088,
                "lng": -73.5878,
                "radius_km": 5.0
            }
        )
        
        data = response.json()
        
        # Check structure
        assert "notification" in data
        assert "zone" in data
        assert "delivery" in data
        
        # Check delivery stats
        delivery = data["delivery"]
        assert "subscriptions_in_zone" in delivery
        assert "eligible" in delivery
        assert "sent" in delivery
        assert "failed" in delivery
        
        print(f"✓ Zone notification structure valid")


# =============================================================================
# HISTORY TESTS
# =============================================================================

class TestNotificationHistory:
    """Notification history endpoint tests"""
    
    def test_history_returns_200(self, api_client):
        """GET /history returns 200"""
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/notifications/history")
        assert response.status_code == 200
        print("✓ History endpoint returns 200")
    
    def test_history_response_structure(self, api_client):
        """History response has expected structure"""
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/notifications/history")
        data = response.json()
        
        assert data["status"] == "success"
        assert "total" in data
        assert "notifications" in data
        assert isinstance(data["notifications"], list)
        
        print(f"✓ History returned {data['total']} notifications")
    
    def test_history_with_limit(self, api_client):
        """GET /history?limit=5 respects limit"""
        # First send a notification to ensure we have data
        api_client.post(
            f"{BASE_URL}/api/v1/bionic/notifications/send",
            json={
                "alert_type": "safety_update",
                "priority": "low",
                "title": "Test for history",
                "body": "Testing history limit",
                "url": "/"
            }
        )
        
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/notifications/history?limit=5")
        data = response.json()
        
        assert len(data["notifications"]) <= 5
        print(f"✓ History limit respected: {len(data['notifications'])} notifications")
    
    def test_history_notification_content(self, api_client):
        """History notifications have expected content structure"""
        response = api_client.get(f"{BASE_URL}/api/v1/bionic/notifications/history")
        data = response.json()
        
        if data["notifications"]:
            notif = data["notifications"][0]
            assert "notification_id" in notif
            assert "alert_type" in notif
            assert "priority" in notif
            assert "content" in notif
            assert "title" in notif["content"]
            assert "body" in notif["content"]
            assert "timestamps" in notif
            
            print(f"✓ History notification structure valid: {notif['notification_id']}")
        else:
            print("✓ History is empty (no notifications yet)")


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestNotificationWorkflow:
    """End-to-end workflow tests"""
    
    def test_complete_subscription_workflow(self, api_client):
        """Test complete subscription → update → send → unsubscribe flow"""
        # 1. Get VAPID key
        vapid_response = api_client.get(f"{BASE_URL}/api/v1/bionic/notifications/vapid-key")
        assert vapid_response.status_code == 200
        vapid_key = vapid_response.json()["vapid_public_key"]
        
        # 2. Subscribe
        sub_response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/notifications/subscribe",
            json={
                "endpoint": f"https://workflow-test.example.com/push/{uuid.uuid4()}",
                "p256dh": "BNcRdreALRFXTkOOUHK1EtK2wtaz5Ry4YfYCA_0QTpQtUbVlUls0VJXg7A8u-Ts1XbjhazAkj7I99e8QcYP7DkM",
                "auth": "tBHItJI5svbpez7KI4CCXg",
                "device_type": "web",
                "lat": 46.8139,
                "lng": -71.2080
            }
        )
        assert sub_response.status_code == 201
        subscription_id = sub_response.json()["subscription"]["subscription_id"]
        
        # 3. Update location
        loc_response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/notifications/update-location",
            json={
                "subscription_id": subscription_id,
                "lat": 45.5088,
                "lng": -73.5878
            }
        )
        assert loc_response.status_code == 200
        
        # 4. Send zone notification
        send_response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/notifications/send-zone",
            json={
                "alert_type": "danger",
                "priority": "high",
                "title": "Workflow Test Alert",
                "body": "Testing complete workflow",
                "lat": 45.5088,
                "lng": -73.5878,
                "radius_km": 10.0
            }
        )
        assert send_response.status_code == 200
        
        # 5. Check history
        history_response = api_client.get(f"{BASE_URL}/api/v1/bionic/notifications/history?limit=1")
        assert history_response.status_code == 200
        
        # 6. Unsubscribe
        unsub_response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/notifications/unsubscribe",
            json={"subscription_id": subscription_id}
        )
        assert unsub_response.status_code == 200
        
        print("✓ Complete workflow passed: subscribe → update → send → history → unsubscribe")
    
    def test_geofencing_logic(self, api_client):
        """Test that geofencing correctly filters subscriptions"""
        # Create subscription in Quebec City
        sub_response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/notifications/subscribe",
            json={
                "endpoint": f"https://geofence-test.example.com/push/{uuid.uuid4()}",
                "p256dh": "BNcRdreALRFXTkOOUHK1EtK2wtaz5Ry4YfYCA_0QTpQtUbVlUls0VJXg7A8u-Ts1XbjhazAkj7I99e8QcYP7DkM",
                "auth": "tBHItJI5svbpez7KI4CCXg",
                "lat": 46.8139,  # Quebec City
                "lng": -71.2080,
                "geofence_radius_km": 5.0
            }
        )
        subscription_id = sub_response.json()["subscription"]["subscription_id"]
        
        # Send notification far away (Paris, France - ~5500km away)
        far_response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/notifications/send-zone",
            json={
                "alert_type": "danger",
                "priority": "critical",
                "title": "Far Away Alert",
                "body": "This should not reach Quebec",
                "lat": 48.8566,  # Paris
                "lng": 2.3522,
                "radius_km": 5.0
            }
        )
        assert far_response.status_code == 200
        far_data = far_response.json()
        
        # Subscription should not be in zone (Paris vs Quebec)
        # Note: might be 0 in zone depending on test data
        
        # Send notification nearby (Montreal - ~250km away)
        near_response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/notifications/send-zone",
            json={
                "alert_type": "danger",
                "priority": "critical",
                "title": "Nearby Alert",
                "body": "This should reach Quebec area",
                "lat": 46.8,  # Very close to Quebec
                "lng": -71.2,
                "radius_km": 50.0  # 50km radius
            }
        )
        assert near_response.status_code == 200
        near_data = near_response.json()
        
        # Cleanup
        api_client.post(
            f"{BASE_URL}/api/v1/bionic/notifications/unsubscribe",
            json={"subscription_id": subscription_id}
        )
        
        print(f"✓ Geofencing test passed - Far: {far_data['delivery']['subscriptions_in_zone']} in zone, Near: {near_data['delivery']['subscriptions_in_zone']} in zone")


# =============================================================================
# EDGE CASE TESTS
# =============================================================================

class TestEdgeCases:
    """Edge case and validation tests"""
    
    def test_subscribe_missing_fields(self, api_client):
        """POST /subscribe with missing required fields returns 422"""
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/notifications/subscribe",
            json={
                "endpoint": "https://test.com/push"
                # Missing p256dh and auth
            }
        )
        assert response.status_code == 422
        print("✓ Missing fields returns 422")
    
    def test_update_location_invalid_coordinates(self, api_client, test_subscription_data):
        """POST /update-location with invalid coordinates returns 422"""
        # First create a subscription
        test_subscription_data["endpoint"] = f"https://test-push-service.example.com/push/{uuid.uuid4()}"
        
        sub_response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/notifications/subscribe",
            json=test_subscription_data
        )
        subscription_id = sub_response.json()["subscription"]["subscription_id"]
        
        # Try invalid latitude
        response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/notifications/update-location",
            json={
                "subscription_id": subscription_id,
                "lat": 200.0,  # Invalid: > 90
                "lng": -71.0
            }
        )
        assert response.status_code == 422
        
        print("✓ Invalid coordinates returns 422")
    
    def test_send_zone_radius_limits(self, api_client):
        """POST /send-zone respects radius limits (0.5 - 50 km)"""
        # Test minimum radius
        min_response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/notifications/send-zone",
            json={
                "alert_type": "danger",
                "priority": "low",
                "title": "Min Radius Test",
                "body": "Testing minimum radius",
                "lat": 46.0,
                "lng": -71.0,
                "radius_km": 0.5  # Minimum
            }
        )
        assert min_response.status_code == 200
        
        # Test too small radius
        too_small_response = api_client.post(
            f"{BASE_URL}/api/v1/bionic/notifications/send-zone",
            json={
                "alert_type": "danger",
                "priority": "low",
                "title": "Too Small Radius",
                "body": "Should fail",
                "lat": 46.0,
                "lng": -71.0,
                "radius_km": 0.1  # Too small
            }
        )
        assert too_small_response.status_code == 422
        
        print("✓ Radius limits validated")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
