"""
Test Admin Maintenance & Contacts APIs - Phase 3 Migration
===========================================================

Tests for:
- Maintenance Admin: status, toggle, access rules, allowed IPs, scheduled maintenance, system status
- Contacts Admin: CRUD, suppliers, partners, tags, stats

Phase 3 Migration - V5-ULTIME Administration Premium
"""

import pytest
import requests
import os
import uuid
from datetime import datetime, timedelta

# Get BASE_URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# ============ MAINTENANCE ADMIN TESTS ============

class TestMaintenanceStatus:
    """Tests for maintenance status endpoints"""
    
    def test_get_maintenance_status(self):
        """GET /api/v1/admin/maintenance/status - Returns maintenance status"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/maintenance/status")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "maintenance" in data
        assert "enabled" in data["maintenance"]
        assert "message" in data["maintenance"]
        print(f"✓ Maintenance status: enabled={data['maintenance']['enabled']}")
    
    def test_toggle_maintenance_mode_off(self):
        """PUT /api/v1/admin/maintenance/toggle - Disable maintenance mode"""
        response = requests.put(f"{BASE_URL}/api/v1/admin/maintenance/toggle?enabled=false")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["enabled"] == False
        print("✓ Maintenance mode disabled")
    
    def test_toggle_maintenance_mode_on(self):
        """PUT /api/v1/admin/maintenance/toggle - Enable maintenance mode"""
        response = requests.put(
            f"{BASE_URL}/api/v1/admin/maintenance/toggle?enabled=true&message=Test%20maintenance"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["enabled"] == True
        print("✓ Maintenance mode enabled")
        
        # Disable it back
        requests.put(f"{BASE_URL}/api/v1/admin/maintenance/toggle?enabled=false")
    
    def test_get_system_status(self):
        """GET /api/v1/admin/maintenance/system-status - Returns system status"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/maintenance/system-status")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "status" in data
        assert "maintenance_enabled" in data["status"]
        assert "access_rules" in data["status"]
        assert "scheduled_maintenances" in data["status"]
        print(f"✓ System status: maintenance_enabled={data['status']['maintenance_enabled']}")


class TestAccessRules:
    """Tests for access rules endpoints"""
    
    def test_get_access_rules(self):
        """GET /api/v1/admin/maintenance/access-rules - Returns access rules list"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/maintenance/access-rules")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "rules" in data
        assert "total" in data
        print(f"✓ Access rules: {data['total']} rules found")
    
    def test_create_access_rule(self):
        """POST /api/v1/admin/maintenance/access-rules - Creates new access rule"""
        rule_data = {
            "name": f"TEST_Rule_{uuid.uuid4().hex[:8]}",
            "type": "ip",
            "action": "allow",
            "condition": {"ip": "192.168.1.100"},
            "priority": 50,
            "enabled": True
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/admin/maintenance/access-rules",
            json=rule_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "rule" in data
        assert data["rule"]["name"] == rule_data["name"]
        assert data["rule"]["type"] == "ip"
        assert data["rule"]["action"] == "allow"
        print(f"✓ Access rule created: {data['rule']['id']}")
        return data["rule"]["id"]
    
    def test_toggle_access_rule(self):
        """PUT /api/v1/admin/maintenance/access-rules/{id}/toggle - Toggle rule"""
        # First create a rule
        rule_data = {
            "name": f"TEST_Toggle_{uuid.uuid4().hex[:8]}",
            "type": "role",
            "action": "deny",
            "enabled": True
        }
        create_response = requests.post(
            f"{BASE_URL}/api/v1/admin/maintenance/access-rules",
            json=rule_data
        )
        rule_id = create_response.json()["rule"]["id"]
        
        # Toggle it off
        response = requests.put(
            f"{BASE_URL}/api/v1/admin/maintenance/access-rules/{rule_id}/toggle?enabled=false"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["enabled"] == False
        print(f"✓ Access rule toggled off: {rule_id}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/v1/admin/maintenance/access-rules/{rule_id}")
    
    def test_delete_access_rule(self):
        """DELETE /api/v1/admin/maintenance/access-rules/{id} - Deletes rule"""
        # First create a rule
        rule_data = {
            "name": f"TEST_Delete_{uuid.uuid4().hex[:8]}",
            "type": "time",
            "action": "redirect"
        }
        create_response = requests.post(
            f"{BASE_URL}/api/v1/admin/maintenance/access-rules",
            json=rule_data
        )
        rule_id = create_response.json()["rule"]["id"]
        
        # Delete it
        response = requests.delete(
            f"{BASE_URL}/api/v1/admin/maintenance/access-rules/{rule_id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["deleted"] == True
        print(f"✓ Access rule deleted: {rule_id}")
    
    def test_delete_nonexistent_rule(self):
        """DELETE /api/v1/admin/maintenance/access-rules/{id} - Returns error for non-existent"""
        fake_id = "nonexistent-rule-id-12345"
        response = requests.delete(
            f"{BASE_URL}/api/v1/admin/maintenance/access-rules/{fake_id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == False
        assert "error" in data
        print("✓ Non-existent rule deletion returns error")


class TestAllowedIPs:
    """Tests for allowed IPs endpoints"""
    
    def test_get_allowed_ips(self):
        """GET /api/v1/admin/maintenance/allowed-ips - Returns allowed IPs list"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/maintenance/allowed-ips")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "allowed_ips" in data
        print(f"✓ Allowed IPs: {len(data['allowed_ips'])} IPs found")
    
    def test_add_allowed_ip(self):
        """POST /api/v1/admin/maintenance/allowed-ips - Adds allowed IP"""
        test_ip = f"10.0.{uuid.uuid4().int % 256}.{uuid.uuid4().int % 256}"
        response = requests.post(
            f"{BASE_URL}/api/v1/admin/maintenance/allowed-ips?ip={test_ip}&label=TEST_IP"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["ip"] == test_ip
        assert data["added"] == True
        print(f"✓ Allowed IP added: {test_ip}")
        
        # Cleanup - remove the IP
        requests.delete(f"{BASE_URL}/api/v1/admin/maintenance/allowed-ips/{test_ip}")


class TestScheduledMaintenance:
    """Tests for scheduled maintenance endpoints"""
    
    def test_get_scheduled_maintenances(self):
        """GET /api/v1/admin/maintenance/scheduled - Returns scheduled maintenances"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/maintenance/scheduled")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "schedules" in data
        assert "total" in data
        print(f"✓ Scheduled maintenances: {data['total']} found")
    
    def test_create_scheduled_maintenance(self):
        """POST /api/v1/admin/maintenance/scheduled - Creates scheduled maintenance"""
        start_time = (datetime.now() + timedelta(days=7)).isoformat()
        end_time = (datetime.now() + timedelta(days=7, hours=2)).isoformat()
        
        schedule_data = {
            "title": f"TEST_Maintenance_{uuid.uuid4().hex[:8]}",
            "description": "Test scheduled maintenance",
            "start_time": start_time,
            "end_time": end_time,
            "auto_enable": True,
            "notify_users": True
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/admin/maintenance/scheduled",
            json=schedule_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "schedule" in data
        assert data["schedule"]["title"] == schedule_data["title"]
        assert data["schedule"]["status"] == "scheduled"
        print(f"✓ Scheduled maintenance created: {data['schedule']['id']}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/v1/admin/maintenance/scheduled/{data['schedule']['id']}")
    
    def test_delete_scheduled_maintenance(self):
        """DELETE /api/v1/admin/maintenance/scheduled/{id} - Deletes scheduled maintenance"""
        # First create one
        schedule_data = {
            "title": f"TEST_ToDelete_{uuid.uuid4().hex[:8]}",
            "description": "Will be deleted",
            "start_time": (datetime.now() + timedelta(days=30)).isoformat(),
            "end_time": (datetime.now() + timedelta(days=30, hours=1)).isoformat()
        }
        create_response = requests.post(
            f"{BASE_URL}/api/v1/admin/maintenance/scheduled",
            json=schedule_data
        )
        schedule_id = create_response.json()["schedule"]["id"]
        
        # Delete it
        response = requests.delete(
            f"{BASE_URL}/api/v1/admin/maintenance/scheduled/{schedule_id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["deleted"] == True
        print(f"✓ Scheduled maintenance deleted: {schedule_id}")


# ============ CONTACTS ADMIN TESTS ============

class TestContactsCRUD:
    """Tests for contacts CRUD endpoints"""
    
    def test_get_contacts(self):
        """GET /api/v1/admin/contacts - Returns contacts list"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/contacts")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "contacts" in data
        assert "total" in data
        assert "type_counts" in data
        print(f"✓ Contacts: {data['total']} found")
    
    def test_get_contacts_stats(self):
        """GET /api/v1/admin/contacts/stats - Returns contacts statistics"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/contacts/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "stats" in data
        assert "total" in data["stats"]
        assert "active" in data["stats"]
        assert "by_type" in data["stats"]
        assert "by_priority" in data["stats"]
        print(f"✓ Contacts stats: total={data['stats']['total']}, active={data['stats']['active']}")
    
    def test_create_contact(self):
        """POST /api/v1/admin/contacts - Creates new contact"""
        contact_data = {
            "entity_type": "supplier",
            "name": f"TEST_Contact_{uuid.uuid4().hex[:8]}",
            "company": "Test Company Inc.",
            "position": "Manager",
            "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
            "phone": "514-555-1234",
            "city": "Montreal",
            "province": "QC",
            "country": "Canada",
            "status": "active",
            "priority": "normal",
            "tags": ["test", "phase3"]
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/admin/contacts",
            json=contact_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "contact" in data
        assert data["contact"]["name"] == contact_data["name"]
        assert data["contact"]["entity_type"] == "supplier"
        assert data["contact"]["status"] == "active"
        print(f"✓ Contact created: {data['contact']['id']}")
        return data["contact"]["id"]
    
    def test_update_contact(self):
        """PUT /api/v1/admin/contacts/{id} - Updates contact"""
        # First create a contact
        contact_data = {
            "entity_type": "partner",
            "name": f"TEST_Update_{uuid.uuid4().hex[:8]}",
            "company": "Original Company"
        }
        create_response = requests.post(
            f"{BASE_URL}/api/v1/admin/contacts",
            json=contact_data
        )
        contact_id = create_response.json()["contact"]["id"]
        
        # Update it
        update_data = {
            "company": "Updated Company",
            "priority": "high",
            "notes": "Updated via test"
        }
        response = requests.put(
            f"{BASE_URL}/api/v1/admin/contacts/{contact_id}",
            json=update_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["updated"] == True
        print(f"✓ Contact updated: {contact_id}")
        
        # Verify update
        get_response = requests.get(f"{BASE_URL}/api/v1/admin/contacts/{contact_id}")
        get_data = get_response.json()
        assert get_data["contact"]["company"] == "Updated Company"
        assert get_data["contact"]["priority"] == "high"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/v1/admin/contacts/{contact_id}")
    
    def test_delete_contact(self):
        """DELETE /api/v1/admin/contacts/{id} - Deletes contact"""
        # First create a contact
        contact_data = {
            "entity_type": "external",
            "name": f"TEST_Delete_{uuid.uuid4().hex[:8]}"
        }
        create_response = requests.post(
            f"{BASE_URL}/api/v1/admin/contacts",
            json=contact_data
        )
        contact_id = create_response.json()["contact"]["id"]
        
        # Delete it
        response = requests.delete(f"{BASE_URL}/api/v1/admin/contacts/{contact_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["deleted"] == True
        print(f"✓ Contact deleted: {contact_id}")
        
        # Verify deletion
        get_response = requests.get(f"{BASE_URL}/api/v1/admin/contacts/{contact_id}")
        get_data = get_response.json()
        assert get_data["success"] == False
    
    def test_delete_nonexistent_contact(self):
        """DELETE /api/v1/admin/contacts/{id} - Returns error for non-existent"""
        fake_id = "nonexistent-contact-id-12345"
        response = requests.delete(f"{BASE_URL}/api/v1/admin/contacts/{fake_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == False
        assert "error" in data
        print("✓ Non-existent contact deletion returns error")


class TestContactsFilters:
    """Tests for contacts filtering endpoints"""
    
    def test_get_suppliers(self):
        """GET /api/v1/admin/contacts/suppliers - Returns suppliers list"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/contacts/suppliers")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "contacts" in data
        # All returned contacts should be suppliers
        for contact in data["contacts"]:
            assert contact["entity_type"] == "supplier"
        print(f"✓ Suppliers: {data['total']} found")
    
    def test_get_partners(self):
        """GET /api/v1/admin/contacts/partners - Returns partners list"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/contacts/partners")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "contacts" in data
        # All returned contacts should be partners
        for contact in data["contacts"]:
            assert contact["entity_type"] == "partner"
        print(f"✓ Partners: {data['total']} found")
    
    def test_get_contacts_by_type(self):
        """GET /api/v1/admin/contacts?entity_type=trainer - Filters by type"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/contacts?entity_type=trainer")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        # All returned contacts should be trainers
        for contact in data["contacts"]:
            assert contact["entity_type"] == "trainer"
        print(f"✓ Trainers filter: {data['total']} found")
    
    def test_get_contacts_by_status(self):
        """GET /api/v1/admin/contacts?status=active - Filters by status"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/contacts?status=active")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        # All returned contacts should be active
        for contact in data["contacts"]:
            assert contact["status"] == "active"
        print(f"✓ Active contacts filter: {data['total']} found")
    
    def test_search_contacts(self):
        """GET /api/v1/admin/contacts?search=test - Searches contacts"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/contacts?search=test")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print(f"✓ Search 'test': {data['total']} contacts found")


class TestContactsTags:
    """Tests for contacts tags endpoints"""
    
    def test_get_all_tags(self):
        """GET /api/v1/admin/contacts/tags - Returns all tags"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/contacts/tags")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "tags" in data
        assert "total" in data
        print(f"✓ Tags: {data['total']} unique tags found")
    
    def test_add_tag_to_contact(self):
        """POST /api/v1/admin/contacts/{id}/tags - Adds tag to contact"""
        # First create a contact
        contact_data = {
            "entity_type": "expert",
            "name": f"TEST_Tag_{uuid.uuid4().hex[:8]}"
        }
        create_response = requests.post(
            f"{BASE_URL}/api/v1/admin/contacts",
            json=contact_data
        )
        contact_id = create_response.json()["contact"]["id"]
        
        # Add tag
        tag = f"test_tag_{uuid.uuid4().hex[:4]}"
        response = requests.post(
            f"{BASE_URL}/api/v1/admin/contacts/{contact_id}/tags?tag={tag}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["added"] == True
        print(f"✓ Tag '{tag}' added to contact {contact_id}")
        
        # Verify tag was added
        get_response = requests.get(f"{BASE_URL}/api/v1/admin/contacts/{contact_id}")
        get_data = get_response.json()
        assert tag in get_data["contact"]["tags"]
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/v1/admin/contacts/{contact_id}")
    
    def test_remove_tag_from_contact(self):
        """DELETE /api/v1/admin/contacts/{id}/tags/{tag} - Removes tag from contact"""
        # First create a contact with tags
        contact_data = {
            "entity_type": "trainer",
            "name": f"TEST_RemoveTag_{uuid.uuid4().hex[:8]}",
            "tags": ["tag_to_remove", "tag_to_keep"]
        }
        create_response = requests.post(
            f"{BASE_URL}/api/v1/admin/contacts",
            json=contact_data
        )
        contact_id = create_response.json()["contact"]["id"]
        
        # Remove tag
        response = requests.delete(
            f"{BASE_URL}/api/v1/admin/contacts/{contact_id}/tags/tag_to_remove"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["removed"] == True
        print(f"✓ Tag 'tag_to_remove' removed from contact {contact_id}")
        
        # Verify tag was removed
        get_response = requests.get(f"{BASE_URL}/api/v1/admin/contacts/{contact_id}")
        get_data = get_response.json()
        assert "tag_to_remove" not in get_data["contact"]["tags"]
        assert "tag_to_keep" in get_data["contact"]["tags"]
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/v1/admin/contacts/{contact_id}")


class TestContactsExport:
    """Tests for contacts export endpoint"""
    
    def test_export_all_contacts(self):
        """GET /api/v1/admin/contacts/export/all - Exports all contacts"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/contacts/export/all")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "contacts" in data
        assert "total" in data
        assert "export_date" in data
        print(f"✓ Export: {data['total']} contacts exported")
    
    def test_export_contacts_by_type(self):
        """GET /api/v1/admin/contacts/export/all?entity_type=supplier - Exports by type"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/contacts/export/all?entity_type=supplier")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        # All exported contacts should be suppliers
        for contact in data["contacts"]:
            assert contact["entity_type"] == "supplier"
        print(f"✓ Export suppliers: {data['total']} contacts exported")


# ============ CLEANUP ============

@pytest.fixture(scope="session", autouse=True)
def cleanup_test_data():
    """Cleanup TEST_ prefixed data after all tests"""
    yield
    # Cleanup contacts
    response = requests.get(f"{BASE_URL}/api/v1/admin/contacts?search=TEST_&limit=100")
    if response.status_code == 200:
        data = response.json()
        for contact in data.get("contacts", []):
            if contact.get("name", "").startswith("TEST_"):
                requests.delete(f"{BASE_URL}/api/v1/admin/contacts/{contact['id']}")
    
    # Cleanup access rules
    response = requests.get(f"{BASE_URL}/api/v1/admin/maintenance/access-rules")
    if response.status_code == 200:
        data = response.json()
        for rule in data.get("rules", []):
            if rule.get("name", "").startswith("TEST_"):
                requests.delete(f"{BASE_URL}/api/v1/admin/maintenance/access-rules/{rule['id']}")
    
    # Cleanup scheduled maintenances
    response = requests.get(f"{BASE_URL}/api/v1/admin/maintenance/scheduled")
    if response.status_code == 200:
        data = response.json()
        for schedule in data.get("schedules", []):
            if schedule.get("title", "").startswith("TEST_"):
                requests.delete(f"{BASE_URL}/api/v1/admin/maintenance/scheduled/{schedule['id']}")
    
    print("\n✓ Test data cleanup completed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
