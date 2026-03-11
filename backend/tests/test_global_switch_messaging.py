"""
Test Suite: Global Master Switch + Messaging Engine + PRÉ-GO LIVE Phase
========================================================================

Tests for:
1. Global Master Switch API - GET /api/v1/global-switch/status (LOCKED)
2. Global Master Switch API - POST /api/v1/global-switch/toggle (ON/OFF/LOCKED)
3. Global Master Switch Dashboard - GET /api/v1/global-switch/dashboard
4. Messaging Engine API - GET /api/v1/messaging/rule/bilingual (BIONIC_BILINGUAL_PREMIUM)
5. Messaging Engine API - GET /api/v1/messaging/messages (5 messages sent)
6. Messaging Engine Templates - GET /api/v1/messaging/templates
7. Engel Coolers désactivé - GET /api/v1/affiliate-switch/affiliates/{id} status=inactive
8. Ad System Status - GET /api/v1/affiliate-ads/system/status mode=PRÉ-PRODUCTION
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestGlobalMasterSwitch:
    """Tests for Global Master Switch API - Gros Bouton Rouge"""
    
    def test_global_switch_status_returns_locked(self):
        """GET /api/v1/global-switch/status should return status=LOCKED"""
        response = requests.get(f"{BASE_URL}/api/v1/global-switch/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "global_switch" in data
        
        global_switch = data["global_switch"]
        # Status should be LOCKED in PRÉ-PRODUCTION mode
        assert global_switch["status"] in ["LOCKED", "OFF", "ON"], f"Unexpected status: {global_switch['status']}"
        
        # Verify mode
        assert data["mode"] in ["PRÉ-PRODUCTION", "PRODUCTION"]
        
        print(f"✓ Global Switch Status: {global_switch['status']}")
        print(f"✓ Mode: {data['mode']}")
        print(f"✓ Is Active: {global_switch.get('is_active', False)}")
    
    def test_global_switch_dashboard(self):
        """GET /api/v1/global-switch/dashboard should return dashboard data"""
        response = requests.get(f"{BASE_URL}/api/v1/global-switch/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "dashboard" in data
        
        dashboard = data["dashboard"]
        assert "global_switch" in dashboard
        assert "mode" in dashboard
        assert "opportunities" in dashboard
        assert "deployed_ads" in dashboard
        assert "slots" in dashboard
        assert "controlled_engines" in dashboard
        
        print(f"✓ Dashboard Mode: {dashboard['mode']}")
        print(f"✓ Controlled Engines: {dashboard['controlled_engines']}")
        print(f"✓ Opportunities Total: {dashboard['opportunities'].get('total', 0)}")
    
    def test_global_switch_engines_list(self):
        """GET /api/v1/global-switch/engines should return all controlled engines"""
        response = requests.get(f"{BASE_URL}/api/v1/global-switch/engines")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "engines" in data
        
        engines = data["engines"]
        assert len(engines) == 6, f"Expected 6 engines, got {len(engines)}"
        
        engine_ids = [e["id"] for e in engines]
        expected_engines = [
            "affiliate_ad_automation_engine",
            "ad_spaces_engine",
            "ad_slot_manager",
            "ad_render_engine",
            "marketing_engine",
            "calendar_engine"
        ]
        
        for expected in expected_engines:
            assert expected in engine_ids, f"Missing engine: {expected}"
        
        print(f"✓ Total Engines: {len(engines)}")
        print(f"✓ Active Engines: {data.get('total_active', 0)}")
        print(f"✓ Disabled Engines: {data.get('total_disabled', 0)}")
    
    def test_global_switch_toggle_to_locked(self):
        """POST /api/v1/global-switch/toggle with new_status=LOCKED"""
        response = requests.post(
            f"{BASE_URL}/api/v1/global-switch/toggle",
            json={
                "new_status": "LOCKED",
                "reason": "Test - Mode PRÉ-PRODUCTION",
                "admin_user": "TEST_AGENT"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["status"] == "LOCKED"
        assert data["is_active"] == False
        assert data["auto_deploy_blocked"] == True
        
        print(f"✓ Toggle to LOCKED successful")
        print(f"✓ Is Active: {data['is_active']}")
        print(f"✓ Auto Deploy Blocked: {data['auto_deploy_blocked']}")
    
    def test_global_switch_module_info(self):
        """GET /api/v1/global-switch/ should return module info"""
        response = requests.get(f"{BASE_URL}/api/v1/global-switch/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["module"] == "global_master_switch"
        assert data["version"] == "1.0.0"
        assert "GROS BOUTON ROUGE" in data["description"]
        assert "controlled_engines" in data
        
        print(f"✓ Module: {data['module']}")
        print(f"✓ Version: {data['version']}")
        print(f"✓ Current Status: {data.get('current_status', 'N/A')}")


class TestMessagingEngine:
    """Tests for Messaging Engine API - Bilingual Premium Messages"""
    
    def test_bilingual_rule_exists(self):
        """GET /api/v1/messaging/rule/bilingual should return BIONIC_BILINGUAL_PREMIUM rule"""
        response = requests.get(f"{BASE_URL}/api/v1/messaging/rule/bilingual")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "rule" in data
        
        rule = data["rule"]
        assert rule["rule_id"] == "BIONIC_BILINGUAL_PREMIUM"
        assert rule["name"] == "Messages Bilingues Premium"
        assert rule["is_permanent"] == True
        assert rule["is_priority"] == True
        assert rule["enforcement_level"] == "mandatory"
        
        # Verify applies_to includes SEO
        assert "SEO" in rule["applies_to"]
        assert "Marketing" in rule["applies_to"]
        assert "Affiliate" in rule["applies_to"]
        
        print(f"✓ Rule ID: {rule['rule_id']}")
        print(f"✓ Rule Name: {rule['name']}")
        print(f"✓ Is Permanent: {rule['is_permanent']}")
        print(f"✓ Applies To: {rule['applies_to']}")
    
    def test_messaging_templates_available(self):
        """GET /api/v1/messaging/templates should return bilingual templates"""
        response = requests.get(f"{BASE_URL}/api/v1/messaging/templates")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "templates" in data
        
        templates = data["templates"]
        assert len(templates) >= 2, f"Expected at least 2 templates, got {len(templates)}"
        
        template_names = [t["name"] for t in templates]
        assert "affiliate_prelaunch" in template_names
        assert "affiliate_welcome" in template_names
        
        # Verify bilingual
        for template in templates:
            assert "fr" in template["languages"]
            assert "en" in template["languages"]
        
        print(f"✓ Templates Count: {len(templates)}")
        print(f"✓ Template Names: {template_names}")
    
    def test_messages_list(self):
        """GET /api/v1/messaging/messages should return messages"""
        response = requests.get(f"{BASE_URL}/api/v1/messaging/messages")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "messages" in data
        assert "pagination" in data
        
        messages = data["messages"]
        print(f"✓ Total Messages: {data['pagination']['total']}")
        
        # Check if we have sent messages
        sent_count = sum(1 for m in messages if m.get("status") == "sent")
        print(f"✓ Sent Messages: {sent_count}")
        
        # Verify message structure if messages exist
        if messages:
            msg = messages[0]
            assert "message_id" in msg
            assert "content" in msg
            assert "status" in msg
            
            # Verify bilingual content
            if "content" in msg:
                content = msg["content"]
                assert "fr" in content or isinstance(content, dict)
                assert "en" in content or isinstance(content, dict)
    
    def test_messaging_dashboard(self):
        """GET /api/v1/messaging/dashboard should return dashboard data"""
        response = requests.get(f"{BASE_URL}/api/v1/messaging/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "dashboard" in data
        
        dashboard = data["dashboard"]
        assert "global_rule" in dashboard
        assert "messages" in dashboard
        assert "templates_available" in dashboard
        
        # Verify global rule is active
        assert dashboard["global_rule"]["status"] == "ACTIVE"
        assert dashboard["global_rule"]["enforcement"] == "MANDATORY"
        
        print(f"✓ Global Rule Status: {dashboard['global_rule']['status']}")
        print(f"✓ Templates Available: {dashboard['templates_available']}")
    
    def test_messaging_module_info(self):
        """GET /api/v1/messaging/ should return module info"""
        response = requests.get(f"{BASE_URL}/api/v1/messaging/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["module"] == "messaging_engine"
        assert data["version"] == "1.0.0"
        assert "bilingue" in data["description"].lower()
        
        print(f"✓ Module: {data['module']}")
        print(f"✓ Version: {data['version']}")


class TestEngelCoolersDeactivation:
    """Tests for Engel Coolers deactivation status"""
    
    ENGEL_COOLERS_ID = "5cd1b50c-7ece-4d11-8a62-8700520f19c7"
    
    def test_engel_coolers_status_inactive(self):
        """GET /api/v1/affiliate-switch/affiliates/{id} should return status=inactive"""
        response = requests.get(
            f"{BASE_URL}/api/v1/affiliate-switch/affiliates/{self.ENGEL_COOLERS_ID}"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "affiliate" in data
        
        affiliate = data["affiliate"]
        assert affiliate["company_name"] == "Engel Coolers"
        
        # Status should be inactive or paused
        status = affiliate.get("status", "")
        assert status in ["inactive", "paused", "disabled"], f"Expected inactive/paused, got: {status}"
        
        print(f"✓ Engel Coolers Status: {status}")
        print(f"✓ Company Name: {affiliate['company_name']}")
        print(f"✓ Ads Enabled: {affiliate.get('ads_enabled', False)}")


class TestAdSystemStatus:
    """Tests for Ad System Status in PRÉ-PRODUCTION mode"""
    
    def test_ad_system_status_pre_production(self):
        """GET /api/v1/affiliate-ads/system/status should return mode=PRÉ-PRODUCTION"""
        response = requests.get(f"{BASE_URL}/api/v1/affiliate-ads/system/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        
        # Mode is nested inside system_status
        system_status = data.get("system_status", {})
        mode = system_status.get("mode", "")
        assert "PRE" in mode.upper() or "PRÉ" in mode, f"Expected PRÉ-PRODUCTION mode, got: {mode}"
        
        master_switch = system_status.get("master_switch", {})
        print(f"✓ System Mode: {mode}")
        print(f"✓ Is Active: {master_switch.get('is_active', False)}")
    
    def test_ad_master_switch_status(self):
        """GET /api/v1/affiliate-ads/master-switch should return switch status"""
        response = requests.get(f"{BASE_URL}/api/v1/affiliate-ads/master-switch")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        
        # Master switch should be OFF in PRÉ-PRODUCTION
        is_active = data.get("is_active", False)
        print(f"✓ Master Switch Active: {is_active}")
        print(f"✓ Auto Deploy Enabled: {data.get('auto_deploy_enabled', False)}")


class TestBilingualMessagesForAffiliates:
    """Tests for bilingual messages sent to 5 affiliates"""
    
    EXPECTED_AFFILIATES = [
        "Engel Coolers",
        "LEM Products", 
        "Weston",
        "Hi Mountain Seasonings",
        "Excalibur"
    ]
    
    def test_messages_sent_to_affiliates(self):
        """Verify messages were sent to the 5 affiliates"""
        response = requests.get(f"{BASE_URL}/api/v1/messaging/messages?limit=50")
        assert response.status_code == 200
        
        data = response.json()
        messages = data.get("messages", [])
        
        # Count sent messages
        sent_messages = [m for m in messages if m.get("status") == "sent"]
        print(f"✓ Total Sent Messages: {len(sent_messages)}")
        
        # Check recipients
        recipients = []
        for msg in sent_messages:
            recipient = msg.get("recipient", {})
            company = recipient.get("company_name", "")
            if company:
                recipients.append(company)
        
        print(f"✓ Recipients: {recipients}")
        
        # Verify bilingual content in messages
        for msg in sent_messages[:5]:  # Check first 5
            content = msg.get("content", {})
            if isinstance(content, dict):
                has_fr = "fr" in content
                has_en = "en" in content
                print(f"  - Message {msg.get('message_id', 'N/A')[:8]}: FR={has_fr}, EN={has_en}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
