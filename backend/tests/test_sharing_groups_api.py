"""
Test Suite for Waypoint Sharing and Hunting Groups APIs
- Partage par email avec collecte marketing
- Partage par lien unique
- Notifications utilisateur
- Groupes de chasse avec invitations
- Admin marketing endpoints
"""

import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test user IDs
TEST_USER_ID = f"TEST_sharing_user_{uuid.uuid4().hex[:8]}"
TEST_USER_ID_2 = f"TEST_sharing_user2_{uuid.uuid4().hex[:8]}"
TEST_EMAIL = f"test_{uuid.uuid4().hex[:8]}@example.com"
TEST_EMAIL_2 = f"test2_{uuid.uuid4().hex[:8]}@example.com"


class TestSharingByEmail:
    """Tests for email sharing endpoints"""
    
    def test_share_waypoint_by_email(self):
        """POST /api/sharing/email/{owner_id} - Share waypoint by email"""
        payload = {
            "waypoint_id": f"wp_{uuid.uuid4().hex[:8]}",
            "waypoint_name": "Test Waypoint for Sharing",
            "emails": [TEST_EMAIL],
            "message": "Check out this hunting spot!",
            "permission": "collaborate"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/sharing/email/{TEST_USER_ID}",
            json=payload
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert data.get("success") == True
        assert data.get("shares_created") >= 1
        assert "share_ids" in data
        assert len(data["share_ids"]) >= 1
        assert "emails_added_to_marketing" in data
        assert data.get("message") is not None
        
        print(f"✓ Share by email created: {data['shares_created']} shares")
        return data["share_ids"][0]
    
    def test_share_waypoint_multiple_emails(self):
        """POST /api/sharing/email/{owner_id} - Share with multiple emails"""
        payload = {
            "waypoint_id": f"wp_{uuid.uuid4().hex[:8]}",
            "waypoint_name": "Multi-share Waypoint",
            "emails": [TEST_EMAIL, TEST_EMAIL_2],
            "permission": "view"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/sharing/email/{TEST_USER_ID}",
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("shares_created") == 2
        print(f"✓ Multi-email share: {data['shares_created']} shares created")
    
    def test_share_waypoint_invalid_email(self):
        """POST /api/sharing/email/{owner_id} - Invalid email format"""
        payload = {
            "waypoint_id": "wp_test",
            "waypoint_name": "Test",
            "emails": ["not-an-email"],
            "permission": "view"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/sharing/email/{TEST_USER_ID}",
            json=payload
        )
        
        # Should return 422 for validation error
        assert response.status_code == 422, f"Expected 422 for invalid email, got {response.status_code}"
        print("✓ Invalid email validation working")
    
    def test_share_waypoint_invalid_permission(self):
        """POST /api/sharing/email/{owner_id} - Invalid permission value"""
        payload = {
            "waypoint_id": "wp_test",
            "waypoint_name": "Test",
            "emails": [TEST_EMAIL],
            "permission": "invalid_permission"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/sharing/email/{TEST_USER_ID}",
            json=payload
        )
        
        # Should return 422 for validation error
        assert response.status_code == 422, f"Expected 422 for invalid permission, got {response.status_code}"
        print("✓ Invalid permission validation working")


class TestSharingByLink:
    """Tests for link sharing endpoints"""
    
    def test_create_share_link(self):
        """POST /api/sharing/link/{owner_id} - Create share link"""
        payload = {
            "waypoint_id": f"wp_{uuid.uuid4().hex[:8]}",
            "waypoint_name": "Link Share Waypoint",
            "expires_in_days": 30,
            "permission": "collaborate"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/sharing/link/{TEST_USER_ID}",
            json=payload
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert data.get("success") == True
        assert "link_id" in data
        assert "share_url" in data
        assert "expires_at" in data
        assert data.get("permission") == "collaborate"
        
        print(f"✓ Share link created: {data['link_id']}")
        return data["link_id"]
    
    def test_get_share_link_info(self):
        """GET /api/sharing/link/{link_id}/info - Get link info"""
        # First create a link
        payload = {
            "waypoint_id": f"wp_{uuid.uuid4().hex[:8]}",
            "waypoint_name": "Info Test Waypoint",
            "expires_in_days": 7,
            "permission": "view"
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/sharing/link/{TEST_USER_ID}",
            json=payload
        )
        assert create_response.status_code == 200
        link_id = create_response.json()["link_id"]
        
        # Get link info
        response = requests.get(f"{BASE_URL}/api/sharing/link/{link_id}/info")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert data.get("id") == link_id
        assert data.get("waypoint_name") == "Info Test Waypoint"
        assert data.get("permission") == "view"
        assert data.get("is_valid") == True
        assert data.get("requires_bionic_account") == True
        
        print(f"✓ Link info retrieved: {data['waypoint_name']}")
    
    def test_get_share_link_not_found(self):
        """GET /api/sharing/link/{link_id}/info - Non-existent link"""
        response = requests.get(f"{BASE_URL}/api/sharing/link/nonexistent123/info")
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Non-existent link returns 404")
    
    def test_create_share_link_custom_expiry(self):
        """POST /api/sharing/link/{owner_id} - Custom expiry days"""
        payload = {
            "waypoint_id": f"wp_{uuid.uuid4().hex[:8]}",
            "waypoint_name": "Custom Expiry Waypoint",
            "expires_in_days": 90,
            "permission": "copy"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/sharing/link/{TEST_USER_ID}",
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("permission") == "copy"
        print(f"✓ Custom expiry link created (90 days)")


class TestUserShares:
    """Tests for user shares endpoints"""
    
    def test_get_received_shares(self):
        """GET /api/sharing/received/{user_id} - Get received shares"""
        response = requests.get(f"{BASE_URL}/api/sharing/received/{TEST_USER_ID}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "shares" in data
        assert "total" in data
        assert isinstance(data["shares"], list)
        
        print(f"✓ Received shares: {data['total']} shares")
    
    def test_get_sent_shares(self):
        """GET /api/sharing/sent/{user_id} - Get sent shares"""
        response = requests.get(f"{BASE_URL}/api/sharing/sent/{TEST_USER_ID}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "email_shares" in data
        assert "link_shares" in data
        assert "total_email" in data
        assert "total_links" in data
        
        print(f"✓ Sent shares: {data['total_email']} email, {data['total_links']} links")


class TestNotifications:
    """Tests for notification endpoints"""
    
    def test_get_user_notifications(self):
        """GET /api/sharing/notifications/{user_id} - Get notifications"""
        response = requests.get(f"{BASE_URL}/api/sharing/notifications/{TEST_USER_ID}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "notifications" in data
        assert "unread_count" in data
        assert "total" in data
        assert isinstance(data["notifications"], list)
        
        print(f"✓ Notifications: {data['total']} total, {data['unread_count']} unread")
    
    def test_get_notifications_unread_only(self):
        """GET /api/sharing/notifications/{user_id}?unread_only=true"""
        response = requests.get(
            f"{BASE_URL}/api/sharing/notifications/{TEST_USER_ID}",
            params={"unread_only": True}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # All returned notifications should be unread
        for notif in data.get("notifications", []):
            assert notif.get("read") == False
        
        print(f"✓ Unread-only filter working")
    
    def test_get_notifications_with_limit(self):
        """GET /api/sharing/notifications/{user_id}?limit=5"""
        response = requests.get(
            f"{BASE_URL}/api/sharing/notifications/{TEST_USER_ID}",
            params={"limit": 5}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data.get("notifications", [])) <= 5
        print(f"✓ Limit parameter working")
    
    def test_mark_all_notifications_read(self):
        """PATCH /api/sharing/notifications/{user_id}/read-all"""
        response = requests.patch(
            f"{BASE_URL}/api/sharing/notifications/{TEST_USER_ID}/read-all"
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") == True
        print(f"✓ Mark all read: {data.get('marked_read', 0)} marked")


class TestAdminMarketing:
    """Tests for admin marketing endpoints"""
    
    def test_get_marketing_emails(self):
        """GET /api/sharing/admin/marketing-emails - Get marketing emails list"""
        response = requests.get(f"{BASE_URL}/api/sharing/admin/marketing-emails")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "emails" in data
        assert "total" in data
        assert "page" in data
        assert "pages" in data
        assert isinstance(data["emails"], list)
        
        print(f"✓ Marketing emails: {data['total']} total")
    
    def test_get_marketing_emails_pagination(self):
        """GET /api/sharing/admin/marketing-emails?page=1&limit=10"""
        response = requests.get(
            f"{BASE_URL}/api/sharing/admin/marketing-emails",
            params={"page": 1, "limit": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("page") == 1
        assert len(data.get("emails", [])) <= 10
        print(f"✓ Pagination working")
    
    def test_get_marketing_stats(self):
        """GET /api/sharing/admin/marketing-stats - Get marketing stats"""
        response = requests.get(f"{BASE_URL}/api/sharing/admin/marketing-stats")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "total_emails" in data
        assert "subscribed" in data
        assert "unsubscribed" in data
        assert "by_source" in data
        
        print(f"✓ Marketing stats: {data['total_emails']} emails, {data['subscribed']} subscribed")


class TestHuntingGroups:
    """Tests for hunting groups endpoints"""
    
    created_group_id = None
    
    def test_create_group(self):
        """POST /api/groups/{owner_id} - Create hunting group"""
        payload = {
            "name": f"Test Hunting Group {uuid.uuid4().hex[:6]}",
            "description": "A test hunting group for API testing",
            "is_public": False,
            "max_members": 10
        }
        
        response = requests.post(
            f"{BASE_URL}/api/groups/{TEST_USER_ID}",
            json=payload
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert data.get("success") == True
        assert "group" in data
        group = data["group"]
        assert group.get("name") == payload["name"]
        assert group.get("owner_id") == TEST_USER_ID
        assert group.get("is_public") == False
        assert group.get("max_members") == 10
        assert "invite_code" in group
        
        TestHuntingGroups.created_group_id = group.get("id")
        print(f"✓ Group created: {group['name']} (ID: {group['id']})")
        return group["id"]
    
    def test_get_user_groups(self):
        """GET /api/groups/{user_id}/my-groups - Get user's groups"""
        response = requests.get(f"{BASE_URL}/api/groups/{TEST_USER_ID}/my-groups")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "owned_groups" in data
        assert "member_groups" in data
        assert "total" in data
        
        print(f"✓ User groups: {len(data['owned_groups'])} owned, {len(data['member_groups'])} member")
    
    def test_create_public_group(self):
        """POST /api/groups/{owner_id} - Create public group"""
        payload = {
            "name": f"Public Group {uuid.uuid4().hex[:6]}",
            "description": "A public hunting group",
            "is_public": True,
            "max_members": 50
        }
        
        response = requests.post(
            f"{BASE_URL}/api/groups/{TEST_USER_ID}",
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["group"]["is_public"] == True
        print(f"✓ Public group created")
        return data["group"]["id"]
    
    def test_discover_public_groups(self):
        """GET /api/groups/discover/public - Discover public groups"""
        response = requests.get(f"{BASE_URL}/api/groups/discover/public")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "groups" in data
        assert "total" in data
        assert isinstance(data["groups"], list)
        
        # All returned groups should be public
        for group in data.get("groups", []):
            assert group.get("is_public") == True
        
        print(f"✓ Public groups: {data['total']} found")
    
    def test_invite_members(self):
        """POST /api/groups/{group_id}/invite - Invite members"""
        # First create a group
        group_id = self.test_create_group()
        
        payload = {
            "emails": [TEST_EMAIL, TEST_EMAIL_2],
            "message": "Join our hunting group!"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/groups/{group_id}/invite",
            json=payload,
            params={"owner_id": TEST_USER_ID}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data.get("success") == True
        assert "invites_sent" in data
        print(f"✓ Invites sent: {data['invites_sent']}")
    
    def test_invite_members_not_owner(self):
        """POST /api/groups/{group_id}/invite - Non-owner cannot invite"""
        if not TestHuntingGroups.created_group_id:
            self.test_create_group()
        
        payload = {
            "emails": [TEST_EMAIL],
            "message": "Unauthorized invite"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/groups/{TestHuntingGroups.created_group_id}/invite",
            json=payload,
            params={"owner_id": "unauthorized_user"}
        )
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ Non-owner invite blocked")
    
    def test_join_public_group(self):
        """POST /api/groups/{group_id}/join - Join public group"""
        # Create a public group
        public_group_id = self.test_create_public_group()
        
        response = requests.post(
            f"{BASE_URL}/api/groups/{public_group_id}/join",
            params={"user_id": TEST_USER_ID_2}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") == True
        print(f"✓ Joined public group")
    
    def test_join_private_group_without_code(self):
        """POST /api/groups/{group_id}/join - Cannot join private without code"""
        if not TestHuntingGroups.created_group_id:
            self.test_create_group()
        
        response = requests.post(
            f"{BASE_URL}/api/groups/{TestHuntingGroups.created_group_id}/join",
            params={"user_id": TEST_USER_ID_2}
        )
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ Private group join without code blocked")
    
    def test_share_waypoint_with_group(self):
        """POST /api/groups/{group_id}/share-waypoint - Share waypoint with group"""
        if not TestHuntingGroups.created_group_id:
            self.test_create_group()
        
        # Note: This endpoint uses query params, not body
        response = requests.post(
            f"{BASE_URL}/api/groups/{TestHuntingGroups.created_group_id}/share-waypoint",
            params={
                "user_id": TEST_USER_ID,
                "waypoint_id": f"wp_{uuid.uuid4().hex[:8]}",
                "waypoint_name": "Group Shared Waypoint"
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") == True
        print(f"✓ Waypoint shared with group")
    
    def test_create_group_validation(self):
        """POST /api/groups/{owner_id} - Validation errors"""
        # Name too short
        payload = {
            "name": "A",  # min_length=2
            "is_public": False
        }
        
        response = requests.post(
            f"{BASE_URL}/api/groups/{TEST_USER_ID}",
            json=payload
        )
        
        assert response.status_code == 422, f"Expected 422 for short name, got {response.status_code}"
        print("✓ Group name validation working")


class TestIntegration:
    """Integration tests for sharing + groups workflow"""
    
    def test_full_sharing_workflow(self):
        """Test complete sharing workflow: create link -> get info -> check sent shares"""
        # 1. Create a share link
        payload = {
            "waypoint_id": f"wp_integration_{uuid.uuid4().hex[:8]}",
            "waypoint_name": "Integration Test Waypoint",
            "expires_in_days": 14,
            "permission": "collaborate"
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/sharing/link/{TEST_USER_ID}",
            json=payload
        )
        assert create_response.status_code == 200
        link_id = create_response.json()["link_id"]
        
        # 2. Get link info
        info_response = requests.get(f"{BASE_URL}/api/sharing/link/{link_id}/info")
        assert info_response.status_code == 200
        assert info_response.json()["waypoint_name"] == "Integration Test Waypoint"
        
        # 3. Check sent shares includes the link
        sent_response = requests.get(f"{BASE_URL}/api/sharing/sent/{TEST_USER_ID}")
        assert sent_response.status_code == 200
        link_shares = sent_response.json()["link_shares"]
        assert any(l["id"] == link_id for l in link_shares)
        
        print("✓ Full sharing workflow completed")
    
    def test_full_group_workflow(self):
        """Test complete group workflow: create -> invite -> share waypoint"""
        # 1. Create group
        group_payload = {
            "name": f"Integration Group {uuid.uuid4().hex[:6]}",
            "description": "Integration test group",
            "is_public": False,
            "max_members": 20
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/groups/{TEST_USER_ID}",
            json=group_payload
        )
        assert create_response.status_code == 200
        group_id = create_response.json()["group"]["id"]
        
        # 2. Invite members
        invite_payload = {
            "emails": [TEST_EMAIL],
            "message": "Integration test invite"
        }
        
        invite_response = requests.post(
            f"{BASE_URL}/api/groups/{group_id}/invite",
            json=invite_payload,
            params={"owner_id": TEST_USER_ID}
        )
        assert invite_response.status_code == 200
        
        # 3. Share waypoint with group (uses query params)
        share_response = requests.post(
            f"{BASE_URL}/api/groups/{group_id}/share-waypoint",
            params={
                "user_id": TEST_USER_ID,
                "waypoint_id": f"wp_group_{uuid.uuid4().hex[:8]}",
                "waypoint_name": "Group Integration Waypoint"
            }
        )
        assert share_response.status_code == 200
        
        # 4. Verify group has shared waypoint
        groups_response = requests.get(f"{BASE_URL}/api/groups/{TEST_USER_ID}/my-groups")
        assert groups_response.status_code == 200
        
        print("✓ Full group workflow completed")


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
