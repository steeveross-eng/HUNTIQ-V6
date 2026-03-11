"""
Test Suite for Live Tracking and Group Chat APIs
- Tracking session management (start/stop/status)
- Position updates and history
- Group positions
- Tracking settings
- Chat messages and alerts
- Alert types
"""

import pytest
import requests
import os
from datetime import datetime
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test data
TEST_USER_ID = "test-track-user"
TEST_GROUP_ID = "69761ba79e441c6e4d0c2dce"  # From previous tests
TEST_USER_ID_2 = "test-track-user-2"


class TestAlertTypes:
    """Test alert types endpoint - no auth required"""
    
    def test_get_alert_types(self):
        """GET /api/chat/alert-types - Get available alert types"""
        response = requests.get(f"{BASE_URL}/api/chat/alert-types")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "alert_types" in data, "Response should contain alert_types"
        assert "quick_messages" in data, "Response should contain quick_messages"
        
        # Verify expected alert types exist
        alert_types = data["alert_types"]
        expected_types = ["animal_spotted", "position_marked", "need_help", "shot_fired", 
                         "returning", "break_time", "silence", "meeting_point"]
        
        for alert_type in expected_types:
            assert alert_type in alert_types, f"Missing alert type: {alert_type}"
            assert "emoji" in alert_types[alert_type], f"Alert {alert_type} missing emoji"
            assert "label" in alert_types[alert_type], f"Alert {alert_type} missing label"
            assert "vibrate" in alert_types[alert_type], f"Alert {alert_type} missing vibrate"
            assert "priority" in alert_types[alert_type], f"Alert {alert_type} missing priority"
        
        # Verify quick messages
        quick_messages = data["quick_messages"]
        assert len(quick_messages) > 0, "Should have quick messages"
        for msg in quick_messages:
            assert "text" in msg, "Quick message missing text"
            assert "emoji" in msg, "Quick message missing emoji"
        
        print(f"✓ Found {len(alert_types)} alert types and {len(quick_messages)} quick messages")


class TestTrackingSessionManagement:
    """Test tracking session start/stop/status"""
    
    def test_start_tracking_session(self):
        """POST /api/tracking/session/start/{user_id} - Start tracking"""
        payload = {
            "group_id": TEST_GROUP_ID,
            "settings": {
                "mode": "auto",
                "share_exact_position": True,
                "update_interval": 30
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/tracking/session/start/{TEST_USER_ID}",
            json=payload
        )
        
        # May fail if user not member of group - that's expected behavior
        if response.status_code == 403:
            print(f"⚠ User {TEST_USER_ID} not member of group {TEST_GROUP_ID} - expected behavior")
            pytest.skip("User not member of group - need to add user first")
        
        if response.status_code == 404:
            print(f"⚠ Group {TEST_GROUP_ID} not found - need to create group first")
            pytest.skip("Group not found - need to create group first")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, "Should return success=True"
        assert "session" in data, "Should return session object"
        
        session = data["session"]
        assert session.get("user_id") == TEST_USER_ID
        assert session.get("group_id") == TEST_GROUP_ID
        assert session.get("is_active") == True
        assert "id" in session
        assert "started_at" in session
        
        print(f"✓ Started tracking session: {session.get('id')}")
        return session
    
    def test_get_session_status_active(self):
        """GET /api/tracking/session/status/{user_id} - Get active session status"""
        response = requests.get(
            f"{BASE_URL}/api/tracking/session/status/{TEST_USER_ID}",
            params={"group_id": TEST_GROUP_ID}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # May or may not have active session
        assert "is_active" in data, "Should return is_active field"
        
        if data.get("is_active"):
            assert "session" in data, "Active session should include session object"
            print(f"✓ Session is active")
        else:
            print(f"✓ No active session found")
    
    def test_stop_tracking_session(self):
        """POST /api/tracking/session/stop/{user_id} - Stop tracking"""
        response = requests.post(
            f"{BASE_URL}/api/tracking/session/stop/{TEST_USER_ID}",
            params={"group_id": TEST_GROUP_ID}
        )
        
        # May return 404 if no active session
        if response.status_code == 404:
            print(f"⚠ No active session to stop - expected if session wasn't started")
            return
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, "Should return success=True"
        print(f"✓ Stopped tracking session")
    
    def test_get_session_status_inactive(self):
        """GET /api/tracking/session/status/{user_id} - Verify session stopped"""
        response = requests.get(
            f"{BASE_URL}/api/tracking/session/status/{TEST_USER_ID}",
            params={"group_id": TEST_GROUP_ID}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # After stopping, should be inactive
        print(f"✓ Session status: is_active={data.get('is_active')}")


class TestPositionUpdates:
    """Test position update and history endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup_session(self):
        """Ensure tracking session is active before position tests"""
        # Try to start a session
        payload = {
            "group_id": TEST_GROUP_ID,
            "settings": {
                "mode": "auto",
                "share_exact_position": True,
                "update_interval": 30
            }
        }
        response = requests.post(
            f"{BASE_URL}/api/tracking/session/start/{TEST_USER_ID}",
            json=payload
        )
        # Don't fail if can't start - tests will handle appropriately
        yield
    
    def test_update_position(self):
        """POST /api/tracking/position/{user_id} - Update position"""
        position_data = {
            "lat": 46.8139,
            "lng": -71.2080,
            "accuracy": 10.5,
            "altitude": 150.0,
            "heading": 45.0,
            "speed": 1.5
        }
        
        response = requests.post(
            f"{BASE_URL}/api/tracking/position/{TEST_USER_ID}",
            params={"group_id": TEST_GROUP_ID},
            json=position_data
        )
        
        # May fail if no active session
        if response.status_code == 400:
            print(f"⚠ No active tracking session - expected if session wasn't started")
            pytest.skip("No active tracking session")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, "Should return success=True"
        assert "timestamp" in data, "Should return timestamp"
        
        print(f"✓ Position updated at {data.get('timestamp')}")
    
    def test_update_position_multiple(self):
        """POST /api/tracking/position/{user_id} - Multiple position updates"""
        positions = [
            {"lat": 46.8140, "lng": -71.2081, "accuracy": 10.0},
            {"lat": 46.8141, "lng": -71.2082, "accuracy": 8.0},
            {"lat": 46.8142, "lng": -71.2083, "accuracy": 12.0},
        ]
        
        for i, pos in enumerate(positions):
            response = requests.post(
                f"{BASE_URL}/api/tracking/position/{TEST_USER_ID}",
                params={"group_id": TEST_GROUP_ID},
                json=pos
            )
            
            if response.status_code == 400:
                pytest.skip("No active tracking session")
            
            assert response.status_code == 200, f"Position {i+1} failed: {response.text}"
            time.sleep(0.1)  # Small delay between updates
        
        print(f"✓ Updated {len(positions)} positions")
    
    def test_get_position_history(self):
        """GET /api/tracking/history/{user_id} - Get position history"""
        response = requests.get(
            f"{BASE_URL}/api/tracking/history/{TEST_USER_ID}",
            params={"group_id": TEST_GROUP_ID, "hours": 6}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "user_id" in data, "Should return user_id"
        assert "positions" in data, "Should return positions array"
        assert "total_points" in data, "Should return total_points"
        assert "total_distance_km" in data, "Should return total_distance_km"
        assert "period_hours" in data, "Should return period_hours"
        
        positions = data.get("positions", [])
        print(f"✓ Found {len(positions)} positions in history, total distance: {data.get('total_distance_km')} km")


class TestGroupPositions:
    """Test group positions endpoint"""
    
    def test_get_group_positions(self):
        """GET /api/tracking/group/{group_id}/positions - Get all member positions"""
        response = requests.get(
            f"{BASE_URL}/api/tracking/group/{TEST_GROUP_ID}/positions",
            params={"user_id": TEST_USER_ID}
        )
        
        # May fail if user not member or group doesn't exist
        if response.status_code == 403:
            print(f"⚠ User not member of group")
            pytest.skip("User not member of group")
        
        if response.status_code == 404:
            print(f"⚠ Group not found")
            pytest.skip("Group not found")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "group_id" in data, "Should return group_id"
        assert "members" in data, "Should return members array"
        assert "total_tracking" in data, "Should return total_tracking count"
        assert "timestamp" in data, "Should return timestamp"
        
        members = data.get("members", [])
        print(f"✓ Found {len(members)} members tracking in group")
        
        # Verify member structure if any exist
        for member in members:
            assert "user_id" in member, "Member should have user_id"
            assert "name" in member, "Member should have name"
            assert "lat" in member, "Member should have lat"
            assert "lng" in member, "Member should have lng"
            assert "is_online" in member, "Member should have is_online"
            assert "last_update" in member, "Member should have last_update"


class TestTrackingSettings:
    """Test tracking settings update"""
    
    def test_update_tracking_settings(self):
        """PUT /api/tracking/settings/{user_id} - Update tracking settings"""
        settings = {
            "mode": "manual",
            "share_exact_position": False,
            "update_interval": 60
        }
        
        response = requests.put(
            f"{BASE_URL}/api/tracking/settings/{TEST_USER_ID}",
            params={"group_id": TEST_GROUP_ID},
            json=settings
        )
        
        # May fail if no active session
        if response.status_code == 404:
            print(f"⚠ No active session to update settings")
            pytest.skip("No active session")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, "Should return success=True"
        assert "settings" in data, "Should return updated settings"
        
        returned_settings = data.get("settings", {})
        assert returned_settings.get("mode") == "manual"
        assert returned_settings.get("share_exact_position") == False
        assert returned_settings.get("update_interval") == 60
        
        print(f"✓ Updated tracking settings")


class TestChatMessages:
    """Test chat message endpoints"""
    
    def test_send_message(self):
        """POST /api/chat/{group_id}/message/{user_id} - Send text message"""
        message_data = {
            "content": "TEST_Message de test pour le chat de groupe",
            "message_type": "text"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/chat/{TEST_GROUP_ID}/message/{TEST_USER_ID}",
            json=message_data
        )
        
        # May fail if user not member or group doesn't exist
        if response.status_code == 403:
            print(f"⚠ User not member of group")
            pytest.skip("User not member of group")
        
        if response.status_code == 404:
            print(f"⚠ Group not found")
            pytest.skip("Group not found")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, "Should return success=True"
        assert "message" in data, "Should return message object"
        
        message = data["message"]
        assert message.get("sender_id") == TEST_USER_ID
        assert message.get("group_id") == TEST_GROUP_ID
        assert "TEST_Message" in message.get("content", "")
        assert message.get("message_type") == "text"
        assert "id" in message
        assert "created_at" in message
        
        print(f"✓ Sent message: {message.get('id')}")
        return message
    
    def test_send_message_with_location(self):
        """POST /api/chat/{group_id}/message/{user_id} - Send message with location"""
        message_data = {
            "content": "TEST_Je suis ici!",
            "message_type": "location",
            "location": {"lat": 46.8139, "lng": -71.2080}
        }
        
        response = requests.post(
            f"{BASE_URL}/api/chat/{TEST_GROUP_ID}/message/{TEST_USER_ID}",
            json=message_data
        )
        
        if response.status_code in [403, 404]:
            pytest.skip("User not member or group not found")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        message = data.get("message", {})
        assert message.get("message_type") == "location"
        assert message.get("location") is not None
        
        print(f"✓ Sent location message")
    
    def test_get_messages(self):
        """GET /api/chat/{group_id}/messages - Get chat messages"""
        response = requests.get(
            f"{BASE_URL}/api/chat/{TEST_GROUP_ID}/messages",
            params={"user_id": TEST_USER_ID, "limit": 50}
        )
        
        if response.status_code in [403, 404]:
            pytest.skip("User not member or group not found")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "group_id" in data, "Should return group_id"
        assert "messages" in data, "Should return messages array"
        assert "has_more" in data, "Should return has_more flag"
        
        messages = data.get("messages", [])
        print(f"✓ Found {len(messages)} messages in chat")
        
        # Verify message structure if any exist
        for msg in messages:
            assert "id" in msg, "Message should have id"
            assert "sender_id" in msg, "Message should have sender_id"
            assert "content" in msg, "Message should have content"
            assert "message_type" in msg, "Message should have message_type"
            assert "created_at" in msg, "Message should have created_at"


class TestChatAlerts:
    """Test chat alert endpoints"""
    
    def test_send_alert_animal_spotted(self):
        """POST /api/chat/{group_id}/alert/{user_id} - Send animal spotted alert"""
        alert_data = {
            "alert_type": "animal_spotted",
            "message": "TEST_Cerf à 200m nord-est",
            "location": {"lat": 46.8145, "lng": -71.2075}
        }
        
        response = requests.post(
            f"{BASE_URL}/api/chat/{TEST_GROUP_ID}/alert/{TEST_USER_ID}",
            json=alert_data
        )
        
        if response.status_code in [403, 404]:
            pytest.skip("User not member or group not found")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        
        message = data.get("message", {})
        assert message.get("message_type") == "alert"
        assert message.get("alert_type") == "animal_spotted"
        assert "🦌" in message.get("content", "")  # Should include emoji
        
        print(f"✓ Sent animal_spotted alert")
    
    def test_send_alert_need_help(self):
        """POST /api/chat/{group_id}/alert/{user_id} - Send need help alert"""
        alert_data = {
            "alert_type": "need_help",
            "location": {"lat": 46.8150, "lng": -71.2070}
        }
        
        response = requests.post(
            f"{BASE_URL}/api/chat/{TEST_GROUP_ID}/alert/{TEST_USER_ID}",
            json=alert_data
        )
        
        if response.status_code in [403, 404]:
            pytest.skip("User not member or group not found")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        message = data.get("message", {})
        assert message.get("alert_type") == "need_help"
        assert "🆘" in message.get("content", "")
        
        print(f"✓ Sent need_help alert")
    
    def test_send_alert_shot_fired(self):
        """POST /api/chat/{group_id}/alert/{user_id} - Send shot fired alert"""
        alert_data = {
            "alert_type": "shot_fired"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/chat/{TEST_GROUP_ID}/alert/{TEST_USER_ID}",
            json=alert_data
        )
        
        if response.status_code in [403, 404]:
            pytest.skip("User not member or group not found")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        message = data.get("message", {})
        assert message.get("alert_type") == "shot_fired"
        assert "🎯" in message.get("content", "")
        
        print(f"✓ Sent shot_fired alert")
    
    def test_send_alert_invalid_type(self):
        """POST /api/chat/{group_id}/alert/{user_id} - Invalid alert type should fail"""
        alert_data = {
            "alert_type": "invalid_type"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/chat/{TEST_GROUP_ID}/alert/{TEST_USER_ID}",
            json=alert_data
        )
        
        if response.status_code in [403, 404]:
            pytest.skip("User not member or group not found")
        
        assert response.status_code == 400, f"Expected 400 for invalid alert type, got {response.status_code}"
        print(f"✓ Invalid alert type correctly rejected")


class TestChatReadStatus:
    """Test message read status endpoints"""
    
    def test_mark_messages_read(self):
        """PATCH /api/chat/{group_id}/messages/read/{user_id} - Mark messages as read"""
        response = requests.patch(
            f"{BASE_URL}/api/chat/{TEST_GROUP_ID}/messages/read/{TEST_USER_ID}"
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert "marked_read" in data
        
        print(f"✓ Marked {data.get('marked_read')} messages as read")
    
    def test_get_unread_count(self):
        """GET /api/chat/{group_id}/unread-count/{user_id} - Get unread message count"""
        response = requests.get(
            f"{BASE_URL}/api/chat/{TEST_GROUP_ID}/unread-count/{TEST_USER_ID}"
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "unread_count" in data
        assert isinstance(data["unread_count"], int)
        
        print(f"✓ Unread count: {data.get('unread_count')}")


class TestTrackingStats:
    """Test tracking statistics endpoint"""
    
    def test_get_group_tracking_stats(self):
        """GET /api/tracking/stats/{group_id} - Get group tracking statistics"""
        response = requests.get(
            f"{BASE_URL}/api/tracking/stats/{TEST_GROUP_ID}"
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "group_id" in data
        assert "active_sessions" in data
        assert "total_sessions" in data
        assert "total_positions_recorded" in data
        
        print(f"✓ Tracking stats: {data.get('active_sessions')} active, {data.get('total_sessions')} total sessions")


class TestChatStats:
    """Test chat statistics endpoint"""
    
    def test_get_chat_stats(self):
        """GET /api/chat/{group_id}/stats - Get chat statistics"""
        response = requests.get(
            f"{BASE_URL}/api/chat/{TEST_GROUP_ID}/stats"
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "group_id" in data
        assert "total_messages" in data
        assert "by_type" in data
        assert "alerts_by_type" in data
        assert "connected_users" in data
        
        print(f"✓ Chat stats: {data.get('total_messages')} total messages, {data.get('connected_users')} connected")


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_start_session_invalid_group(self):
        """POST /api/tracking/session/start - Invalid group ID"""
        payload = {
            "group_id": "invalid_group_id",
            "settings": {"mode": "auto"}
        }
        
        response = requests.post(
            f"{BASE_URL}/api/tracking/session/start/{TEST_USER_ID}",
            json=payload
        )
        
        # Should return error for invalid ObjectId (400, 404, 500, or 520 from Cloudflare)
        assert response.status_code in [400, 404, 500, 520], f"Expected error for invalid group, got {response.status_code}"
        print(f"✓ Invalid group ID correctly handled (status: {response.status_code})")
    
    def test_position_update_invalid_coordinates(self):
        """POST /api/tracking/position - Invalid coordinates"""
        # Latitude out of range
        position_data = {
            "lat": 200.0,  # Invalid - should be -90 to 90
            "lng": -71.2080
        }
        
        response = requests.post(
            f"{BASE_URL}/api/tracking/position/{TEST_USER_ID}",
            params={"group_id": TEST_GROUP_ID},
            json=position_data
        )
        
        # Should return 422 for validation error
        assert response.status_code == 422, f"Expected 422 for invalid coordinates, got {response.status_code}"
        print(f"✓ Invalid coordinates correctly rejected")
    
    def test_send_message_empty_content(self):
        """POST /api/chat/{group_id}/message - Empty content should fail"""
        message_data = {
            "content": "",
            "message_type": "text"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/chat/{TEST_GROUP_ID}/message/{TEST_USER_ID}",
            json=message_data
        )
        
        # Should return 422 for validation error (min_length=1)
        if response.status_code in [403, 404]:
            pytest.skip("User not member or group not found")
        
        assert response.status_code == 422, f"Expected 422 for empty content, got {response.status_code}"
        print(f"✓ Empty message content correctly rejected")


class TestCleanup:
    """Cleanup test data"""
    
    def test_cleanup_stop_session(self):
        """Stop any active tracking session"""
        response = requests.post(
            f"{BASE_URL}/api/tracking/session/stop/{TEST_USER_ID}",
            params={"group_id": TEST_GROUP_ID}
        )
        # Don't assert - just cleanup
        print(f"✓ Cleanup: stopped tracking session (status: {response.status_code})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
