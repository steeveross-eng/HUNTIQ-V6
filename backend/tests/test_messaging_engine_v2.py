"""
Test Messaging Engine V2 - Pipeline 7 étapes avec modes TOUS/UN PAR UN
======================================================================

Tests:
- Module info avec version 2.0.0 et send_modes
- Templates avec variables company_name, contact_name, category, country
- Preview generation avec entête BIONIC ASCII
- Preview validation (individuel et batch)
- Send one (mode UN PAR UN)
- Send all (mode TOUS)
- Pipeline logs
- Dashboard avec send_modes stats
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestMessagingEngineV2ModuleInfo:
    """Test module info endpoint"""
    
    def test_module_info_version_2(self):
        """GET /api/v1/messaging/ - Version 2.0.0 avec send_modes"""
        response = requests.get(f"{BASE_URL}/api/v1/messaging/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["module"] == "messaging_engine"
        assert data["version"] == "2.0.0"
        assert "TOUS" in data["send_modes"]
        assert "UN_PAR_UN" in data["send_modes"]
        assert "pipeline_steps" in data
        assert len(data["pipeline_steps"]) == 7
        
        # Verify pipeline steps
        expected_steps = [
            "mode_selection", "template_preparation", "variable_injection",
            "preview_generation", "manual_validation", "sending", "logging"
        ]
        for step in expected_steps:
            assert step in data["pipeline_steps"]
        
        print(f"✅ Module info: version={data['version']}, send_modes={data['send_modes']}")
    
    def test_module_has_global_rule(self):
        """Module info includes global bilingual rule"""
        response = requests.get(f"{BASE_URL}/api/v1/messaging/")
        assert response.status_code == 200
        
        data = response.json()
        assert "global_rule" in data
        assert data["global_rule"]["rule_id"] == "BIONIC_BILINGUAL_PREMIUM"
        assert data["global_rule"]["is_permanent"] == True
        assert data["global_rule"]["enforcement_level"] == "mandatory"
        
        print(f"✅ Global rule: {data['global_rule']['name']}")


class TestMessagingTemplates:
    """Test templates endpoints"""
    
    def test_get_all_templates(self):
        """GET /api/v1/messaging/templates - Liste templates avec variables"""
        response = requests.get(f"{BASE_URL}/api/v1/messaging/templates")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["count"] >= 2
        
        # Check templates have required structure
        for template in data["templates"]:
            assert "variables" in template
            assert "company_name" in template["variables"]
            assert "contact_name" in template["variables"]
            # Note: category/country are in affiliate templates, notification templates have different vars
            assert "fr" in template["languages"]
            assert "en" in template["languages"]
        
        # Verify affiliate templates have category/country
        affiliate_templates = [t for t in data["templates"] if "affiliate" in t["id"]]
        for template in affiliate_templates:
            assert "category" in template["variables"]
            assert "country" in template["variables"]
        
        print(f"✅ Templates: {data['count']} templates with bilingual support")
    
    def test_get_specific_template(self):
        """GET /api/v1/messaging/templates/affiliate_prelaunch"""
        response = requests.get(f"{BASE_URL}/api/v1/messaging/templates/affiliate_prelaunch")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["template_name"] == "affiliate_prelaunch"
        assert "content" in data
        assert "fr" in data["content"]
        assert "en" in data["content"]
        
        # Check FR content
        assert "subject" in data["content"]["fr"]
        assert "greeting" in data["content"]["fr"]
        assert "body" in data["content"]["fr"]
        
        # Check EN content
        assert "subject" in data["content"]["en"]
        assert "greeting" in data["content"]["en"]
        assert "body" in data["content"]["en"]
        
        print(f"✅ Template affiliate_prelaunch: FR/EN content available")
    
    def test_template_not_found(self):
        """GET /api/v1/messaging/templates/nonexistent - 404"""
        response = requests.get(f"{BASE_URL}/api/v1/messaging/templates/nonexistent_template")
        assert response.status_code == 404


class TestPreviewGeneration:
    """Test preview generation with BIONIC header"""
    
    def test_generate_preview_tous_mode(self):
        """POST /api/v1/messaging/preview/generate - Mode TOUS"""
        payload = {
            "template": "affiliate_prelaunch",
            "send_mode": "TOUS",
            "recipients": [
                {
                    "affiliate_id": "test-affiliate-1",
                    "company_name": "TEST_Company_Alpha",
                    "contact_name": "John Doe",
                    "email": "test@alpha.com",
                    "category": "processing",
                    "country": "Canada"
                },
                {
                    "affiliate_id": "test-affiliate-2",
                    "company_name": "TEST_Company_Beta",
                    "contact_name": "Jane Smith",
                    "email": "test@beta.com",
                    "category": "optics",
                    "country": "USA"
                }
            ],
            "created_by": "TEST_AGENT"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/messaging/preview/generate",
            json=payload
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["send_mode"] == "TOUS"
        assert data["batch_id"] is not None
        assert data["previews_generated"] == 2
        assert data["requires_validation"] == True
        
        # Check preview contains BIONIC header
        if data.get("sample_preview"):
            preview = data["sample_preview"]
            assert "BIONIC" in preview.get("fr_preview", "")
            assert "BIONIC" in preview.get("en_preview", "")
            assert preview.get("bionic_header") is not None
        
        print(f"✅ Preview generated: batch_id={data['batch_id']}, count={data['previews_generated']}")
        return data["batch_id"]
    
    def test_generate_preview_un_par_un_mode(self):
        """POST /api/v1/messaging/preview/generate - Mode UN PAR UN"""
        payload = {
            "template": "affiliate_welcome",
            "send_mode": "UN_PAR_UN",
            "recipients": [
                {
                    "affiliate_id": "test-single-affiliate",
                    "company_name": "TEST_Single_Company",
                    "contact_name": "Solo User",
                    "email": "solo@test.com",
                    "category": "firearms",
                    "country": "USA"
                }
            ],
            "created_by": "TEST_AGENT"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/messaging/preview/generate",
            json=payload
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["send_mode"] == "UN_PAR_UN"
        assert data["previews_generated"] == 1
        
        # For UN_PAR_UN, all previews should be returned
        assert len(data["previews"]) == 1
        
        preview = data["previews"][0]
        assert "preview_id" in preview
        assert "fr_preview" in preview
        assert "en_preview" in preview
        
        # Verify BIONIC ASCII art header is present
        assert "██████╗" in preview["fr_preview"]  # Part of BIONIC ASCII
        assert "██████╗" in preview["en_preview"]
        
        print(f"✅ UN PAR UN preview: preview_id={preview['preview_id']}")
        return preview["preview_id"]
    
    def test_preview_requires_recipients(self):
        """POST /api/v1/messaging/preview/generate - Error without recipients"""
        payload = {
            "template": "affiliate_prelaunch",
            "send_mode": "TOUS",
            "recipients": []
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/messaging/preview/generate",
            json=payload
        )
        assert response.status_code == 400
    
    def test_preview_bionic_header_content(self):
        """Verify preview contains BIONIC ASCII art header"""
        payload = {
            "template": "affiliate_prelaunch",
            "send_mode": "UN_PAR_UN",
            "recipients": [
                {
                    "affiliate_id": "test-header-check",
                    "company_name": "TEST_Header_Check",
                    "contact_name": "Header Test",
                    "email": "header@test.com",
                    "category": "processing",
                    "country": "Canada"
                }
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/messaging/preview/generate",
            json=payload
        )
        assert response.status_code == 200
        
        data = response.json()
        preview = data["previews"][0]
        
        # Check for BIONIC ASCII art elements
        fr_preview = preview["fr_preview"]
        en_preview = preview["en_preview"]
        
        # ASCII art should contain these patterns
        assert "╔══" in fr_preview
        assert "╚══" in fr_preview
        assert "BIONIC" in fr_preview or "██████╗" in fr_preview
        
        # Check language markers
        assert "🇫🇷" in fr_preview or "FRANÇAISE" in fr_preview
        assert "🇺🇸" in en_preview or "ENGLISH" in en_preview
        
        print("✅ BIONIC ASCII header verified in preview")


class TestPreviewValidation:
    """Test preview validation endpoints"""
    
    @pytest.fixture
    def preview_id(self):
        """Create a preview for validation tests"""
        payload = {
            "template": "affiliate_prelaunch",
            "send_mode": "UN_PAR_UN",
            "recipients": [
                {
                    "affiliate_id": f"test-validate-{uuid.uuid4().hex[:8]}",
                    "company_name": "TEST_Validation_Company",
                    "contact_name": "Validator",
                    "email": "validate@test.com",
                    "category": "processing",
                    "country": "Canada"
                }
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/messaging/preview/generate",
            json=payload
        )
        data = response.json()
        return data["previews"][0]["preview_id"]
    
    def test_validate_single_preview(self, preview_id):
        """POST /api/v1/messaging/preview/{preview_id}/validate"""
        response = requests.post(
            f"{BASE_URL}/api/v1/messaging/preview/{preview_id}/validate",
            json={"admin_user": "TEST_ADMIN"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["preview_id"] == preview_id
        assert data["validated_by"] == "TEST_ADMIN"
        assert "validated_at" in data
        
        print(f"✅ Preview validated: {preview_id}")
    
    def test_validate_already_validated(self, preview_id):
        """Validate same preview twice - should succeed with message"""
        # First validation
        requests.post(
            f"{BASE_URL}/api/v1/messaging/preview/{preview_id}/validate",
            json={"admin_user": "TEST_ADMIN"}
        )
        
        # Second validation
        response = requests.post(
            f"{BASE_URL}/api/v1/messaging/preview/{preview_id}/validate",
            json={"admin_user": "TEST_ADMIN"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "déjà validé" in data.get("message", "")
    
    def test_validate_nonexistent_preview(self):
        """POST /api/v1/messaging/preview/nonexistent/validate - 404"""
        response = requests.post(
            f"{BASE_URL}/api/v1/messaging/preview/nonexistent-id/validate",
            json={"admin_user": "TEST_ADMIN"}
        )
        assert response.status_code == 404


class TestBatchValidation:
    """Test batch validation for TOUS mode"""
    
    @pytest.fixture
    def batch_id(self):
        """Create a batch for validation tests"""
        payload = {
            "template": "affiliate_prelaunch",
            "send_mode": "TOUS",
            "recipients": [
                {
                    "affiliate_id": f"test-batch-{uuid.uuid4().hex[:8]}",
                    "company_name": "TEST_Batch_Company_1",
                    "contact_name": "Batch User 1",
                    "email": "batch1@test.com",
                    "category": "processing",
                    "country": "Canada"
                },
                {
                    "affiliate_id": f"test-batch-{uuid.uuid4().hex[:8]}",
                    "company_name": "TEST_Batch_Company_2",
                    "contact_name": "Batch User 2",
                    "email": "batch2@test.com",
                    "category": "optics",
                    "country": "USA"
                }
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/messaging/preview/generate",
            json=payload
        )
        data = response.json()
        return data["batch_id"]
    
    def test_validate_all_batch(self, batch_id):
        """POST /api/v1/messaging/batch/{batch_id}/validate-all"""
        response = requests.post(
            f"{BASE_URL}/api/v1/messaging/batch/{batch_id}/validate-all",
            json={"admin_user": "TEST_BATCH_ADMIN"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["batch_id"] == batch_id
        assert data["validated_count"] >= 0
        assert data["validated_by"] == "TEST_BATCH_ADMIN"
        
        print(f"✅ Batch validated: {batch_id}, count={data['validated_count']}")


class TestSendOne:
    """Test send one message (UN PAR UN mode)"""
    
    @pytest.fixture
    def validated_preview_id(self):
        """Create and validate a preview for send tests"""
        # Generate preview
        payload = {
            "template": "affiliate_prelaunch",
            "send_mode": "UN_PAR_UN",
            "recipients": [
                {
                    "affiliate_id": f"test-send-{uuid.uuid4().hex[:8]}",
                    "company_name": "TEST_Send_Company",
                    "contact_name": "Send User",
                    "email": "send@test.com",
                    "category": "processing",
                    "country": "Canada"
                }
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/messaging/preview/generate",
            json=payload
        )
        data = response.json()
        preview_id = data["previews"][0]["preview_id"]
        
        # Validate preview
        requests.post(
            f"{BASE_URL}/api/v1/messaging/preview/{preview_id}/validate",
            json={"admin_user": "TEST_ADMIN"}
        )
        
        return preview_id
    
    def test_send_one_validated(self, validated_preview_id):
        """POST /api/v1/messaging/send/one - Send validated preview"""
        response = requests.post(
            f"{BASE_URL}/api/v1/messaging/send/one",
            json={
                "preview_id": validated_preview_id,
                "admin_user": "TEST_SENDER"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["preview_id"] == validated_preview_id
        assert data["send_mode"] == "UN_PAR_UN"
        assert "message_id" in data
        assert "sent_at" in data
        
        print(f"✅ Message sent: message_id={data['message_id']}")
    
    def test_send_one_unvalidated(self):
        """POST /api/v1/messaging/send/one - Error for unvalidated preview"""
        # Generate preview without validating
        payload = {
            "template": "affiliate_prelaunch",
            "send_mode": "UN_PAR_UN",
            "recipients": [
                {
                    "affiliate_id": f"test-unvalidated-{uuid.uuid4().hex[:8]}",
                    "company_name": "TEST_Unvalidated",
                    "contact_name": "Unvalidated User",
                    "email": "unvalidated@test.com",
                    "category": "processing",
                    "country": "Canada"
                }
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/messaging/preview/generate",
            json=payload
        )
        preview_id = response.json()["previews"][0]["preview_id"]
        
        # Try to send without validation
        response = requests.post(
            f"{BASE_URL}/api/v1/messaging/send/one",
            json={
                "preview_id": preview_id,
                "admin_user": "TEST_SENDER"
            }
        )
        assert response.status_code == 400
        assert "non validé" in response.json().get("detail", "").lower()
    
    def test_send_one_missing_preview_id(self):
        """POST /api/v1/messaging/send/one - Error without preview_id"""
        response = requests.post(
            f"{BASE_URL}/api/v1/messaging/send/one",
            json={"admin_user": "TEST_SENDER"}
        )
        assert response.status_code == 400


class TestSendAll:
    """Test send all messages (TOUS mode)"""
    
    @pytest.fixture
    def validated_batch_id(self):
        """Create and validate a batch for send tests"""
        # Generate batch
        payload = {
            "template": "affiliate_prelaunch",
            "send_mode": "TOUS",
            "recipients": [
                {
                    "affiliate_id": f"test-sendall-{uuid.uuid4().hex[:8]}",
                    "company_name": "TEST_SendAll_1",
                    "contact_name": "SendAll User 1",
                    "email": "sendall1@test.com",
                    "category": "processing",
                    "country": "Canada"
                },
                {
                    "affiliate_id": f"test-sendall-{uuid.uuid4().hex[:8]}",
                    "company_name": "TEST_SendAll_2",
                    "contact_name": "SendAll User 2",
                    "email": "sendall2@test.com",
                    "category": "optics",
                    "country": "USA"
                }
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/messaging/preview/generate",
            json=payload
        )
        batch_id = response.json()["batch_id"]
        
        # Validate all
        requests.post(
            f"{BASE_URL}/api/v1/messaging/batch/{batch_id}/validate-all",
            json={"admin_user": "TEST_ADMIN"}
        )
        
        return batch_id
    
    def test_send_all_validated(self, validated_batch_id):
        """POST /api/v1/messaging/send/all - Send all validated previews"""
        response = requests.post(
            f"{BASE_URL}/api/v1/messaging/send/all",
            json={
                "batch_id": validated_batch_id,
                "admin_user": "TEST_BATCH_SENDER"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["batch_id"] == validated_batch_id
        assert data["send_mode"] == "TOUS"
        assert data["sent_count"] >= 0
        assert "sent_messages" in data
        
        print(f"✅ Batch sent: batch_id={validated_batch_id}, sent_count={data['sent_count']}")
    
    def test_send_all_missing_batch_id(self):
        """POST /api/v1/messaging/send/all - Error without batch_id"""
        response = requests.post(
            f"{BASE_URL}/api/v1/messaging/send/all",
            json={"admin_user": "TEST_SENDER"}
        )
        assert response.status_code == 400


class TestPipelineLogs:
    """Test pipeline logs endpoint"""
    
    def test_get_pipeline_logs(self):
        """GET /api/v1/messaging/pipeline-logs"""
        response = requests.get(f"{BASE_URL}/api/v1/messaging/pipeline-logs")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "logs" in data
        assert "count" in data
        
        # Check log structure if logs exist
        if data["logs"]:
            log = data["logs"][0]
            assert "log_id" in log
            assert "batch_id" in log
            assert "pipeline_step" in log
            assert "timestamp" in log
        
        print(f"✅ Pipeline logs: {data['count']} entries")
    
    def test_get_pipeline_logs_by_batch(self):
        """GET /api/v1/messaging/pipeline-logs?batch_id=xxx"""
        # First create a batch to get logs for
        payload = {
            "template": "affiliate_prelaunch",
            "send_mode": "UN_PAR_UN",
            "recipients": [
                {
                    "affiliate_id": f"test-logs-{uuid.uuid4().hex[:8]}",
                    "company_name": "TEST_Logs_Company",
                    "contact_name": "Logs User",
                    "email": "logs@test.com",
                    "category": "processing",
                    "country": "Canada"
                }
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/messaging/preview/generate",
            json=payload
        )
        batch_id = response.json()["batch_id"]
        
        # Get logs for this batch
        response = requests.get(f"{BASE_URL}/api/v1/messaging/pipeline-logs?batch_id={batch_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        
        # All logs should be for this batch
        for log in data["logs"]:
            assert log["batch_id"] == batch_id


class TestDashboard:
    """Test dashboard endpoint"""
    
    def test_get_dashboard(self):
        """GET /api/v1/messaging/dashboard"""
        response = requests.get(f"{BASE_URL}/api/v1/messaging/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "dashboard" in data
        
        dashboard = data["dashboard"]
        
        # Check send_modes stats
        assert "send_modes" in dashboard
        assert "TOUS" in dashboard["send_modes"]
        assert "UN_PAR_UN" in dashboard["send_modes"]
        
        # Check global rule
        assert "global_rule" in dashboard
        assert dashboard["global_rule"]["status"] == "ACTIVE"
        assert dashboard["global_rule"]["enforcement"] == "MANDATORY"
        
        # Check messages stats
        assert "messages" in dashboard
        assert "total" in dashboard["messages"]
        assert "sent" in dashboard["messages"]
        
        # Check previews stats
        assert "previews" in dashboard
        assert "total" in dashboard["previews"]
        assert "validated" in dashboard["previews"]
        assert "pending_validation" in dashboard["previews"]
        
        # Check pipeline steps
        assert "pipeline_steps" in dashboard
        assert len(dashboard["pipeline_steps"]) == 7
        
        print(f"✅ Dashboard: TOUS={dashboard['send_modes']['TOUS']}, UN_PAR_UN={dashboard['send_modes']['UN_PAR_UN']}")


class TestBilingualRule:
    """Test bilingual rule endpoint"""
    
    def test_get_bilingual_rule(self):
        """GET /api/v1/messaging/rule/bilingual"""
        response = requests.get(f"{BASE_URL}/api/v1/messaging/rule/bilingual")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["status"] == "ACTIVE"
        assert data["enforcement"] == "MANDATORY"
        
        rule = data["rule"]
        assert rule["rule_id"] == "BIONIC_BILINGUAL_PREMIUM"
        assert rule["is_permanent"] == True
        assert "SEO" in rule["applies_to"]
        assert "Marketing" in rule["applies_to"]
        assert "Affiliate" in rule["applies_to"]
        
        print(f"✅ Bilingual rule: {rule['name']} - {data['enforcement']}")


class TestMessagesEndpoints:
    """Test messages listing endpoints"""
    
    def test_get_all_messages(self):
        """GET /api/v1/messaging/messages"""
        response = requests.get(f"{BASE_URL}/api/v1/messaging/messages")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "messages" in data
        assert "pagination" in data
        
        print(f"✅ Messages: {data['pagination']['total']} total")
    
    def test_get_all_previews(self):
        """GET /api/v1/messaging/previews"""
        response = requests.get(f"{BASE_URL}/api/v1/messaging/previews")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "previews" in data
        assert "pagination" in data
        
        print(f"✅ Previews: {data['pagination']['total']} total")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
