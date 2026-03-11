"""
Test Admin Email & Marketing APIs - Phase 5 Migration
======================================================

Tests for:
- Email Admin: Dashboard, Templates, Variables, Logs, Config, Test sending
- Marketing Admin: Dashboard, Campaigns, Posts, Generate, Segments, Automations
"""

import pytest
import requests
import os
import json
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestEmailAdminDashboard:
    """Email Dashboard API tests"""
    
    def test_email_dashboard_returns_success(self):
        """GET /api/v1/admin/email/dashboard - Returns dashboard stats"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/email/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "stats" in data
        
        stats = data["stats"]
        assert "templates" in stats
        assert "sending" in stats
        assert "delivery" in stats
        assert "engagement" in stats
        assert "by_category" in stats
        assert "config" in stats
        
        # Verify templates structure
        assert "total" in stats["templates"]
        assert "active" in stats["templates"]
        assert stats["templates"]["total"] == 6  # 6 default templates
        
        # Verify config structure
        assert "service_configured" in stats["config"]
        assert "sender_email" in stats["config"]
        assert "provider" in stats["config"]


class TestEmailAdminTemplates:
    """Email Templates API tests"""
    
    def test_get_templates_returns_default_templates(self):
        """GET /api/v1/admin/email/templates - Returns default templates"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/email/templates")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "templates" in data
        assert "total" in data
        assert "categories" in data
        
        # Should have 6 default templates
        assert data["total"] == 6
        
        # Verify template structure
        templates = data["templates"]
        assert len(templates) == 6
        
        template_ids = [t["id"] for t in templates]
        assert "welcome" in template_ids
        assert "order_confirmation" in template_ids
        assert "password_reset" in template_ids
        assert "notification_digest" in template_ids
        assert "newsletter" in template_ids
        assert "promo_campaign" in template_ids
    
    def test_get_templates_filter_by_category(self):
        """GET /api/v1/admin/email/templates?category=transactional - Filters by category"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/email/templates?category=transactional")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        
        # All returned templates should be transactional
        for template in data["templates"]:
            assert template["category"] == "transactional"
    
    def test_get_templates_filter_by_marketing_category(self):
        """GET /api/v1/admin/email/templates?category=marketing - Filters marketing templates"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/email/templates?category=marketing")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        
        # Should have 2 marketing templates (newsletter, promo_campaign)
        assert len(data["templates"]) == 2
        for template in data["templates"]:
            assert template["category"] == "marketing"
    
    def test_get_template_detail(self):
        """GET /api/v1/admin/email/templates/{template_id} - Returns template detail"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/email/templates/welcome")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "template" in data
        
        template = data["template"]
        assert template["id"] == "welcome"
        assert template["name"] == "Email de bienvenue"
        assert "subject" in template
        assert "html_template" in template
        assert "text_template" in template
        assert "variables" in template
        assert "is_active" in template


class TestEmailAdminVariables:
    """Email Variables API tests"""
    
    def test_get_variables_returns_system_variables(self):
        """GET /api/v1/admin/email/variables - Returns system variables"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/email/variables")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "system_variables" in data
        assert "custom_variables" in data
        
        # Verify system variables exist
        system_vars = data["system_variables"]
        assert len(system_vars) > 0
        
        # Check for expected variables
        var_names = [v["name"] for v in system_vars]
        assert "user_name" in var_names
        assert "brand_name" in var_names
        assert "app_url" in var_names
        assert "year" in var_names
        
        # Verify variable structure
        for var in system_vars:
            assert "name" in var
            assert "description" in var
            assert "category" in var


class TestEmailAdminLogs:
    """Email Logs API tests"""
    
    def test_get_email_logs(self):
        """GET /api/v1/admin/email/logs - Returns email logs"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/email/logs")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "logs" in data
        assert "total" in data
        
        # Logs should be a list (may be empty)
        assert isinstance(data["logs"], list)
    
    def test_get_email_logs_with_limit(self):
        """GET /api/v1/admin/email/logs?limit=10 - Limits results"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/email/logs?limit=10")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True


class TestEmailAdminConfig:
    """Email Config API tests"""
    
    def test_get_email_config(self):
        """GET /api/v1/admin/email/config - Returns email configuration"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/email/config")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "config" in data
        
        config = data["config"]
        assert "provider" in config
        assert "sender_email" in config
        assert "is_configured" in config
        assert "daily_limit" in config
        assert "rate_limit_per_minute" in config
        
        # Service should not be configured (no RESEND_API_KEY)
        assert config["is_configured"] == False


class TestEmailAdminTestSending:
    """Email Test Sending API tests"""
    
    def test_send_test_email_simulated(self):
        """POST /api/v1/admin/email/test - Sends simulated test email"""
        response = requests.post(
            f"{BASE_URL}/api/v1/admin/email/test?template_id=welcome&recipient_email=test@example.com",
            headers={"Content-Type": "application/json"},
            json={}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["status"] == "simulated"
        assert "log_id" in data
        assert "test@example.com" in data["message"]


class TestMarketingAdminDashboard:
    """Marketing Dashboard API tests"""
    
    def test_marketing_dashboard_returns_success(self):
        """GET /api/v1/admin/marketing/dashboard - Returns dashboard stats"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/marketing/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "stats" in data
        
        stats = data["stats"]
        assert "campaigns" in stats
        assert "posts" in stats
        assert "engagement_30d" in stats
        assert "segments" in stats
        assert "automations" in stats
        assert "by_platform" in stats
        
        # Verify campaigns structure
        assert "total" in stats["campaigns"]
        assert "active" in stats["campaigns"]
        assert "draft" in stats["campaigns"]
        
        # Verify by_platform structure
        assert "facebook" in stats["by_platform"]
        assert "instagram" in stats["by_platform"]
        assert "twitter" in stats["by_platform"]
        assert "linkedin" in stats["by_platform"]


class TestMarketingAdminCampaigns:
    """Marketing Campaigns API tests"""
    
    def test_get_campaigns(self):
        """GET /api/v1/admin/marketing/campaigns - Returns campaigns list"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/marketing/campaigns")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "campaigns" in data
        assert "total" in data
        assert "status_counts" in data
        
        # Verify status_counts structure
        status_counts = data["status_counts"]
        assert "draft" in status_counts
        assert "active" in status_counts
        assert "paused" in status_counts
        assert "completed" in status_counts
        assert "archived" in status_counts
    
    def test_create_campaign(self):
        """POST /api/v1/admin/marketing/campaigns - Creates a new campaign"""
        campaign_data = {
            "name": "TEST_Phase5_Campaign",
            "description": "Test campaign for Phase 5 migration",
            "type": "promotional",
            "target_platforms": ["facebook", "instagram"],
            "budget": 500
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/admin/marketing/campaigns",
            headers={"Content-Type": "application/json"},
            json=campaign_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "campaign" in data
        
        campaign = data["campaign"]
        assert campaign["name"] == "TEST_Phase5_Campaign"
        assert campaign["status"] == "draft"
        assert "id" in campaign
        
        # Store campaign_id for cleanup
        TestMarketingAdminCampaigns.test_campaign_id = campaign["id"]
    
    def test_get_campaign_detail(self):
        """GET /api/v1/admin/marketing/campaigns/{campaign_id} - Returns campaign detail"""
        if not hasattr(TestMarketingAdminCampaigns, 'test_campaign_id'):
            pytest.skip("No test campaign created")
        
        campaign_id = TestMarketingAdminCampaigns.test_campaign_id
        response = requests.get(f"{BASE_URL}/api/v1/admin/marketing/campaigns/{campaign_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "campaign" in data
        assert "posts" in data
        assert "performance" in data
    
    def test_update_campaign_status(self):
        """PUT /api/v1/admin/marketing/campaigns/{campaign_id}/status - Updates campaign status"""
        if not hasattr(TestMarketingAdminCampaigns, 'test_campaign_id'):
            pytest.skip("No test campaign created")
        
        campaign_id = TestMarketingAdminCampaigns.test_campaign_id
        response = requests.put(f"{BASE_URL}/api/v1/admin/marketing/campaigns/{campaign_id}/status?status=active")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["status"] == "active"
    
    def test_delete_campaign(self):
        """DELETE /api/v1/admin/marketing/campaigns/{campaign_id} - Deletes campaign"""
        if not hasattr(TestMarketingAdminCampaigns, 'test_campaign_id'):
            pytest.skip("No test campaign created")
        
        campaign_id = TestMarketingAdminCampaigns.test_campaign_id
        response = requests.delete(f"{BASE_URL}/api/v1/admin/marketing/campaigns/{campaign_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["deleted"] == True


class TestMarketingAdminPosts:
    """Marketing Posts API tests"""
    
    def test_get_posts(self):
        """GET /api/v1/admin/marketing/posts - Returns posts list"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/marketing/posts")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "posts" in data
        assert "total" in data
    
    def test_get_scheduled_posts(self):
        """GET /api/v1/admin/marketing/posts/scheduled - Returns scheduled posts"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/marketing/posts/scheduled")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "posts" in data
        assert "total" in data
    
    def test_create_post(self):
        """POST /api/v1/admin/marketing/posts - Creates a new post"""
        post_data = {
            "content": "TEST_Phase5_Post - Testing marketing post creation",
            "hashtags": ["test", "phase5"],
            "platform": "facebook",
            "content_type": "product_promo",
            "status": "draft"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/admin/marketing/posts",
            headers={"Content-Type": "application/json"},
            json=post_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "post" in data
        
        post = data["post"]
        assert "TEST_Phase5_Post" in post["content"]
        assert post["platform"] == "facebook"
        assert "id" in post
        
        # Store post_id for cleanup
        TestMarketingAdminPosts.test_post_id = post["id"]
    
    def test_schedule_post(self):
        """PUT /api/v1/admin/marketing/posts/{post_id}/schedule - Schedules a post"""
        if not hasattr(TestMarketingAdminPosts, 'test_post_id'):
            pytest.skip("No test post created")
        
        post_id = TestMarketingAdminPosts.test_post_id
        scheduled_at = (datetime.now() + timedelta(days=1)).isoformat()
        
        response = requests.put(f"{BASE_URL}/api/v1/admin/marketing/posts/{post_id}/schedule?scheduled_at={scheduled_at}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["post_id"] == post_id
    
    def test_delete_post(self):
        """DELETE /api/v1/admin/marketing/posts/{post_id} - Deletes post"""
        if not hasattr(TestMarketingAdminPosts, 'test_post_id'):
            pytest.skip("No test post created")
        
        post_id = TestMarketingAdminPosts.test_post_id
        response = requests.delete(f"{BASE_URL}/api/v1/admin/marketing/posts/{post_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["deleted"] == True


class TestMarketingAdminGenerate:
    """Marketing Content Generation API tests"""
    
    def test_generate_content_product_promo(self):
        """POST /api/v1/admin/marketing/generate - Generates product promo content"""
        params = {
            "content_type": "product_promo",
            "platform": "facebook",
            "product_name": "BIONIC HUNT/Chasse Premium",
            "keywords": ["chasse", "Québec"],
            "tone": "professional",
            "brand_name": "BIONIC HUNT/Chasse"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/admin/marketing/generate",
            headers={"Content-Type": "application/json"},
            json=params
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "content" in data
        assert "hashtags" in data
        assert "platform" in data
        assert "content_type" in data
        
        # Verify content is not empty
        assert len(data["content"]) > 0
        assert len(data["hashtags"]) > 0
    
    def test_generate_content_educational(self):
        """POST /api/v1/admin/marketing/generate - Generates educational content"""
        params = {
            "content_type": "educational",
            "platform": "instagram",
            "tone": "informative"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/admin/marketing/generate",
            headers={"Content-Type": "application/json"},
            json=params
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["content_type"] == "educational"
        assert data["platform"] == "instagram"
    
    def test_generate_content_engagement(self):
        """POST /api/v1/admin/marketing/generate - Generates engagement content"""
        params = {
            "content_type": "engagement",
            "platform": "twitter"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/admin/marketing/generate",
            headers={"Content-Type": "application/json"},
            json=params
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        # Twitter content should be shorter
        assert len(data["content"]) <= 280


class TestMarketingAdminSegments:
    """Marketing Segments API tests"""
    
    def test_get_segments_returns_defaults(self):
        """GET /api/v1/admin/marketing/segments - Returns default segments"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/marketing/segments")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "segments" in data
        assert "total" in data
        
        # Should have 5 default segments
        segments = data["segments"]
        assert len(segments) == 5
        
        segment_ids = [s["id"] for s in segments]
        assert "all_users" in segment_ids
        assert "premium" in segment_ids
        assert "hunters" in segment_ids
        assert "landowners" in segment_ids
        assert "inactive" in segment_ids


class TestMarketingAdminAutomations:
    """Marketing Automations API tests"""
    
    def test_get_automations_returns_defaults(self):
        """GET /api/v1/admin/marketing/automations - Returns default automations"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/marketing/automations")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "automations" in data
        assert "total" in data
        
        # Should have 3 default automations
        automations = data["automations"]
        assert len(automations) == 3
        
        automation_ids = [a["id"] for a in automations]
        assert "welcome_series" in automation_ids
        assert "cart_abandonment" in automation_ids
        assert "reengagement" in automation_ids
        
        # Verify automation structure
        for automation in automations:
            assert "name" in automation
            assert "trigger" in automation
            assert "actions" in automation
            assert "is_active" in automation


class TestMarketingAdminHistory:
    """Marketing History API tests"""
    
    def test_get_history(self):
        """GET /api/v1/admin/marketing/history - Returns publish history"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/marketing/history")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "history" in data
        assert "total" in data


class TestMarketingAdminContentTypes:
    """Marketing Content Types API tests"""
    
    def test_get_content_types(self):
        """GET /api/v1/admin/marketing/content-types - Returns content types"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/marketing/content-types")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "content_types" in data
        
        content_types = data["content_types"]
        assert len(content_types) == 6
        
        type_ids = [t["id"] for t in content_types]
        assert "product_promo" in type_ids
        assert "educational" in type_ids
        assert "seasonal" in type_ids
        assert "testimonial" in type_ids
        assert "tip" in type_ids
        assert "engagement" in type_ids


class TestMarketingAdminPlatforms:
    """Marketing Platforms API tests"""
    
    def test_get_platforms(self):
        """GET /api/v1/admin/marketing/platforms - Returns platforms"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/marketing/platforms")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "platforms" in data
        
        platforms = data["platforms"]
        assert len(platforms) == 4
        
        platform_ids = [p["id"] for p in platforms]
        assert "facebook" in platform_ids
        assert "instagram" in platform_ids
        assert "twitter" in platform_ids
        assert "linkedin" in platform_ids
        
        # Verify platform structure
        for platform in platforms:
            assert "name" in platform
            assert "max_length" in platform


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
