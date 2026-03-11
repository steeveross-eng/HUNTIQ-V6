"""
Test Admin Partners & Branding APIs - Phase 6 Migration
========================================================

Tests for:
- Partners Admin: Dashboard, Types, Requests, Partners List, Email Settings
- Branding Admin: Dashboard, Config, Logos, Colors, Document Types

Phase 6 Migration - Partenaires & Branding
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestPartnersAdmin:
    """Partners Admin API Tests - Phase 6"""
    
    # ============ DASHBOARD ============
    def test_partners_dashboard(self):
        """GET /api/v1/admin/partners/dashboard - Returns dashboard stats"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/partners/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "stats" in data
        stats = data["stats"]
        # Verify structure
        assert "requests" in stats
        assert "partners" in stats
        assert "by_type" in stats
        assert "financial" in stats
        # Verify requests stats
        assert "total" in stats["requests"]
        assert "pending" in stats["requests"]
        assert "approved" in stats["requests"]
        assert "rejected" in stats["requests"]
        assert "converted" in stats["requests"]
        assert "recent_7d" in stats["requests"]
        # Verify partners stats
        assert "total" in stats["partners"]
        assert "active" in stats["partners"]
        assert "verified" in stats["partners"]
        # Verify financial stats
        assert "total_wallet" in stats["financial"]
        assert "avg_commission" in stats["financial"]
        print(f"✓ Partners dashboard: {stats['partners']['total']} partners, {stats['requests']['total']} requests")
    
    # ============ PARTNER TYPES ============
    def test_partners_types(self):
        """GET /api/v1/admin/partners/types - Returns 11 partner types"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/partners/types")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "types" in data
        types = data["types"]
        assert len(types) == 11  # 11 categories as per spec
        # Verify structure
        for ptype in types:
            assert "id" in ptype
            assert "label_fr" in ptype
            assert "label_en" in ptype
        # Verify expected types
        type_ids = [t["id"] for t in types]
        expected_types = ["marques", "pourvoiries", "proprietaires", "guides", "boutiques", 
                         "services", "fabricants", "zec", "clubs", "particuliers", "autres"]
        for expected in expected_types:
            assert expected in type_ids, f"Missing type: {expected}"
        print(f"✓ Partner types: {len(types)} types returned")
    
    # ============ REQUESTS MANAGEMENT ============
    def test_partners_requests_list(self):
        """GET /api/v1/admin/partners/requests - Returns requests list"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/partners/requests")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "total" in data
        assert "requests" in data
        assert isinstance(data["requests"], list)
        print(f"✓ Partner requests: {data['total']} total requests")
    
    def test_partners_requests_filter_by_status(self):
        """GET /api/v1/admin/partners/requests?status=pending - Filter by status"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/partners/requests?status=pending")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print(f"✓ Partner requests filtered by status: {data['total']} pending")
    
    def test_partners_requests_filter_by_type(self):
        """GET /api/v1/admin/partners/requests?partner_type=marques - Filter by type"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/partners/requests?partner_type=marques")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print(f"✓ Partner requests filtered by type: {data['total']} marques")
    
    def test_partners_requests_search(self):
        """GET /api/v1/admin/partners/requests?search=test - Search requests"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/partners/requests?search=test")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print(f"✓ Partner requests search: {data['total']} results")
    
    def test_partners_request_detail_not_found(self):
        """GET /api/v1/admin/partners/requests/{id} - Returns error for non-existent"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/partners/requests/nonexistent-id")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == False
        assert "error" in data
        print("✓ Partner request detail returns error for non-existent ID")
    
    # ============ PARTNERS LIST ============
    def test_partners_list(self):
        """GET /api/v1/admin/partners/list - Returns partners list"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/partners/list")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "total" in data
        assert "partners" in data
        assert isinstance(data["partners"], list)
        print(f"✓ Partners list: {data['total']} total partners")
    
    def test_partners_list_filter_by_type(self):
        """GET /api/v1/admin/partners/list?partner_type=guides - Filter by type"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/partners/list?partner_type=guides")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print(f"✓ Partners list filtered by type: {data['total']} guides")
    
    def test_partners_list_filter_by_active(self):
        """GET /api/v1/admin/partners/list?is_active=true - Filter by active status"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/partners/list?is_active=true")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print(f"✓ Partners list filtered by active: {data['total']} active partners")
    
    def test_partners_list_search(self):
        """GET /api/v1/admin/partners/list?search=test - Search partners"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/partners/list?search=test")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print(f"✓ Partners list search: {data['total']} results")
    
    def test_partner_detail_not_found(self):
        """GET /api/v1/admin/partners/{id} - Returns error for non-existent"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/partners/nonexistent-id")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == False
        assert "error" in data
        print("✓ Partner detail returns error for non-existent ID")
    
    # ============ EMAIL SETTINGS ============
    def test_partners_email_settings(self):
        """GET /api/v1/admin/partners/email/settings - Returns email settings"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/partners/email/settings")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "settings" in data
        settings = data["settings"]
        # Verify expected settings
        assert "acknowledgment_enabled" in settings
        assert "admin_notification_enabled" in settings
        assert "approval_enabled" in settings
        assert "rejection_enabled" in settings
        print(f"✓ Partner email settings: {settings}")
    
    def test_partners_email_toggle_invalid_type(self):
        """PUT /api/v1/admin/partners/email/toggle/{type} - Invalid type returns error"""
        response = requests.put(f"{BASE_URL}/api/v1/admin/partners/email/toggle/invalid_type")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == False
        assert "error" in data
        print("✓ Partner email toggle returns error for invalid type")


class TestBrandingAdmin:
    """Branding Admin API Tests - Phase 6"""
    
    # ============ DASHBOARD ============
    def test_branding_dashboard(self):
        """GET /api/v1/admin/branding/dashboard - Returns dashboard stats"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/branding/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "stats" in data
        stats = data["stats"]
        # Verify structure
        assert "logos" in stats
        assert "documents" in stats
        assert "uploads" in stats
        assert "colors" in stats
        # Verify logos stats
        assert "default" in stats["logos"]
        assert "custom" in stats["logos"]
        assert "total" in stats["logos"]
        assert stats["logos"]["default"] == 3  # 3 default logos
        # Verify documents stats
        assert "generated" in stats["documents"]
        assert "types" in stats["documents"]
        assert stats["documents"]["types"] == 7  # 7 document types
        # Verify colors count
        assert stats["colors"] == 7  # 7 brand colors
        print(f"✓ Branding dashboard: {stats['logos']['total']} logos, {stats['colors']} colors")
    
    # ============ BRAND CONFIG ============
    def test_branding_config(self):
        """GET /api/v1/admin/branding/config - Returns brand configuration"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/branding/config")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "config" in data
        config = data["config"]
        # Verify structure
        assert "brands" in config
        assert "colors" in config
        assert "document_types" in config
        # Verify brands (FR and EN)
        assert "fr" in config["brands"]
        assert "en" in config["brands"]
        assert config["brands"]["fr"]["name"] == "Chasse Bionic"
        assert config["brands"]["en"]["name"] == "Bionic Hunt"
        # Verify colors
        assert "primary" in config["colors"]
        assert "secondary" in config["colors"]
        assert config["colors"]["primary"]["hex"] == "#f5a623"
        # Verify document types
        assert len(config["document_types"]) == 7
        print(f"✓ Branding config: FR={config['brands']['fr']['name']}, EN={config['brands']['en']['name']}")
    
    # ============ LOGOS MANAGEMENT ============
    def test_branding_logos(self):
        """GET /api/v1/admin/branding/logos - Returns logos list"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/branding/logos")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "default" in data
        assert "custom" in data
        # Verify default logos
        assert len(data["default"]) == 3  # main, fr_full, en_full
        default_ids = [logo["id"] for logo in data["default"]]
        assert "main" in default_ids
        assert "fr_full" in default_ids
        assert "en_full" in default_ids
        print(f"✓ Branding logos: {len(data['default'])} default, {len(data['custom'])} custom")
    
    def test_branding_logo_detail_default(self):
        """GET /api/v1/admin/branding/logos/{id} - Returns default logo detail"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/branding/logos/main")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "logo" in data
        assert data["is_default"] == True
        assert data["logo"]["id"] == "main"
        assert data["logo"]["name"] == "Logo Principal BIONIC™"
        print(f"✓ Branding logo detail: {data['logo']['name']}")
    
    def test_branding_logo_detail_not_found(self):
        """GET /api/v1/admin/branding/logos/{id} - Returns error for non-existent"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/branding/logos/nonexistent-logo")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == False
        assert "error" in data
        print("✓ Branding logo detail returns error for non-existent ID")
    
    def test_branding_delete_default_logo_fails(self):
        """DELETE /api/v1/admin/branding/logos/{id} - Cannot delete default logo"""
        response = requests.delete(f"{BASE_URL}/api/v1/admin/branding/logos/main")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == False
        assert "error" in data
        print("✓ Cannot delete default logo")
    
    # ============ COLORS MANAGEMENT ============
    def test_branding_colors(self):
        """GET /api/v1/admin/branding/colors - Returns brand colors"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/branding/colors")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "colors" in data
        colors = data["colors"]
        # Verify expected colors
        expected_colors = ["primary", "secondary", "accent", "success", "danger", "text", "muted"]
        for color in expected_colors:
            assert color in colors, f"Missing color: {color}"
            assert "hex" in colors[color]
            assert "name" in colors[color]
            assert "usage" in colors[color]
        # Verify primary color
        assert colors["primary"]["hex"] == "#f5a623"
        assert colors["primary"]["name"] == "Golden Orange"
        print(f"✓ Branding colors: {len(colors)} colors")
    
    def test_branding_update_color_invalid_format(self):
        """PUT /api/v1/admin/branding/colors/{key} - Invalid hex format returns error"""
        response = requests.put(f"{BASE_URL}/api/v1/admin/branding/colors/primary?hex_value=invalid")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == False
        assert "error" in data
        print("✓ Branding update color returns error for invalid hex format")
    
    # ============ DOCUMENT TYPES ============
    def test_branding_document_types(self):
        """GET /api/v1/admin/branding/document-types - Returns document types"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/branding/document-types")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "document_types" in data
        doc_types = data["document_types"]
        assert len(doc_types) == 7  # 7 document types
        # Verify structure
        for doc_type in doc_types:
            assert "id" in doc_type
            assert "name_fr" in doc_type
            assert "name_en" in doc_type
        # Verify expected types
        type_ids = [t["id"] for t in doc_types]
        expected_types = ["letter", "email", "contract", "invoice", "partner", "zec", "press"]
        for expected in expected_types:
            assert expected in type_ids, f"Missing document type: {expected}"
        print(f"✓ Branding document types: {len(doc_types)} types")
    
    # ============ DOCUMENT HISTORY ============
    def test_branding_document_history(self):
        """GET /api/v1/admin/branding/documents/history - Returns document history"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/branding/documents/history")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "total" in data
        assert "history" in data
        assert isinstance(data["history"], list)
        print(f"✓ Branding document history: {data['total']} documents")
    
    # ============ UPLOAD HISTORY ============
    def test_branding_upload_history(self):
        """GET /api/v1/admin/branding/uploads/history - Returns upload history"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/branding/uploads/history")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "total" in data
        assert "history" in data
        assert isinstance(data["history"], list)
        print(f"✓ Branding upload history: {data['total']} uploads")
    
    # ============ BRAND ASSETS ============
    def test_branding_assets(self):
        """GET /api/v1/admin/branding/assets - Returns all brand assets"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/branding/assets")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "assets" in data
        assets = data["assets"]
        # Verify structure
        assert "brand" in assets
        assert "logos" in assets
        assert "colors" in assets
        assert "document_types" in assets
        # Verify brand info
        assert "fr" in assets["brand"]
        assert "en" in assets["brand"]
        # Verify logos
        assert "default" in assets["logos"]
        assert "custom" in assets["logos"]
        print(f"✓ Branding assets: Complete brand assets returned")


class TestPartnersWorkflow:
    """Partners Workflow Tests - Create Request → Approve → Convert"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test data"""
        self.test_request_id = None
        self.test_partner_id = None
        yield
        # Cleanup would go here if needed
    
    def test_update_request_status_invalid(self):
        """PUT /api/v1/admin/partners/requests/{id}/status - Invalid status returns error"""
        response = requests.put(
            f"{BASE_URL}/api/v1/admin/partners/requests/test-id/status?status=invalid_status"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == False
        assert "error" in data
        print("✓ Update request status returns error for invalid status")
    
    def test_convert_nonexistent_request(self):
        """POST /api/v1/admin/partners/requests/{id}/convert - Non-existent returns error"""
        response = requests.post(
            f"{BASE_URL}/api/v1/admin/partners/requests/nonexistent-id/convert"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == False
        assert "error" in data
        print("✓ Convert request returns error for non-existent ID")
    
    def test_toggle_nonexistent_partner(self):
        """PUT /api/v1/admin/partners/{id}/toggle - Non-existent returns error"""
        response = requests.put(
            f"{BASE_URL}/api/v1/admin/partners/nonexistent-id/toggle"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == False
        assert "error" in data
        print("✓ Toggle partner status returns error for non-existent ID")
    
    def test_verify_nonexistent_partner(self):
        """PUT /api/v1/admin/partners/{id}/verify - Non-existent returns error"""
        response = requests.put(
            f"{BASE_URL}/api/v1/admin/partners/nonexistent-id/verify?verified=true"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == False
        assert "error" in data
        print("✓ Verify partner returns error for non-existent ID")
    
    def test_update_commission_invalid_rate(self):
        """PUT /api/v1/admin/partners/{id}/commission - Invalid rate returns error"""
        response = requests.put(
            f"{BASE_URL}/api/v1/admin/partners/test-id/commission?rate=150"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == False
        assert "error" in data
        print("✓ Update commission returns error for invalid rate (>100)")


class TestBrandingWorkflow:
    """Branding Workflow Tests - Logo Upload, Color Update, Document Generation"""
    
    def test_add_custom_logo(self):
        """POST /api/v1/admin/branding/logos - Add custom logo"""
        response = requests.post(
            f"{BASE_URL}/api/v1/admin/branding/logos",
            params={
                "filename": "TEST_custom_logo.png",
                "url": "/uploads/TEST_custom_logo.png",
                "language": "fr",
                "logo_type": "full",
                "file_size": 12345
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "logo" in data
        assert data["logo"]["filename"] == "TEST_custom_logo.png"
        assert data["logo"]["language"] == "fr"
        print(f"✓ Custom logo added: {data['logo']['id']}")
        # Store for cleanup
        return data["logo"]["id"]
    
    def test_update_color(self):
        """PUT /api/v1/admin/branding/colors/{key} - Update color"""
        response = requests.put(
            f"{BASE_URL}/api/v1/admin/branding/colors/primary?hex_value=%23ff5500&name=Test%20Orange"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["color_key"] == "primary"
        assert data["hex"] == "#ff5500"
        print(f"✓ Color updated: primary -> #ff5500")
    
    def test_reset_colors(self):
        """POST /api/v1/admin/branding/colors/reset - Reset colors to default"""
        response = requests.post(f"{BASE_URL}/api/v1/admin/branding/colors/reset")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "colors" in data
        # Verify primary is back to default
        assert data["colors"]["primary"]["hex"] == "#f5a623"
        print("✓ Colors reset to default")
    
    def test_log_document_generation(self):
        """POST /api/v1/admin/branding/documents/log - Log document generation"""
        response = requests.post(
            f"{BASE_URL}/api/v1/admin/branding/documents/log",
            params={
                "template_type": "letter",
                "language": "fr",
                "title": "TEST Document",
                "recipient": "Test Recipient"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "log_id" in data
        print(f"✓ Document generation logged: {data['log_id']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
