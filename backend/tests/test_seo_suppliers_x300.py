"""
Test Suite for SEO Suppliers Database & X300% Strategy APIs
============================================================

Phase PRÉ-GO LIVE - BIONIC HUNT/Chasse V5-ULTIME
Tests for:
- SEO Suppliers Database (104 fournisseurs, 13 catégories)
- Master Switch X300%
- Contact Engine X300%

"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://territory-analysis.preview.emergentagent.com').rstrip('/')


class TestSEOSuppliersDatabase:
    """Tests for the SEO Suppliers Database - LISTE FOURNISSEURS ULTIME"""
    
    def test_get_all_suppliers(self):
        """GET /api/v1/bionic/seo/suppliers/ - Liste tous les fournisseurs"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seo/suppliers/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "suppliers" in data
        assert "pagination" in data
        assert len(data["suppliers"]) > 0
        
        # Verify supplier structure
        supplier = data["suppliers"][0]
        assert "company" in supplier
        assert "country" in supplier
        assert "official_url" in supplier
        assert "category" in supplier
    
    def test_get_categories(self):
        """GET /api/v1/bionic/seo/suppliers/categories - Liste des catégories"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seo/suppliers/categories")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "categories" in data
        assert data["total_categories"] == 13  # Expected 13 categories
        assert data["total_suppliers"] == 104  # Expected 104 suppliers
        
        # Verify expected categories exist
        category_ids = [c["id"] for c in data["categories"]]
        expected_categories = ["cameras", "arcs_arbaletes", "treestands", "urines_attractants", 
                              "vetements", "optiques", "bottes", "backpacks", "knives", 
                              "boats_kayaks", "electronics", "coolers", "processing"]
        for cat in expected_categories:
            assert cat in category_ids, f"Category {cat} not found"
    
    def test_get_suppliers_by_category_cameras(self):
        """GET /api/v1/bionic/seo/suppliers/by-category/cameras - Fournisseurs caméras"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seo/suppliers/by-category/cameras")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["category"] == "cameras"
        assert data["count"] == 13  # Expected 13 camera suppliers
        
        # Verify known suppliers exist
        company_names = [s["company"] for s in data["suppliers"]]
        assert "Spypoint" in company_names
        assert "Reolink" in company_names
        assert "Bushnell" in company_names
    
    def test_get_suppliers_by_category_arcs(self):
        """GET /api/v1/bionic/seo/suppliers/by-category/arcs_arbaletes - Fournisseurs arcs"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seo/suppliers/by-category/arcs_arbaletes")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["count"] == 12  # Expected 12 archery suppliers
    
    def test_get_stats(self):
        """GET /api/v1/bionic/seo/suppliers/stats - Statistiques (104 fournisseurs attendus)"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seo/suppliers/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "stats" in data
        
        stats = data["stats"]
        assert stats["total_suppliers"] == 104
        assert stats["categories_count"] == 13
        
        # Verify category counts
        by_category = stats["by_category"]
        assert by_category["cameras"] == 13
        assert by_category["arcs_arbaletes"] == 12
        assert by_category["treestands"] == 9
        assert by_category["urines_attractants"] == 9
        assert by_category["vetements"] == 9
        assert by_category["optiques"] == 7
        assert by_category["bottes"] == 7
        assert by_category["backpacks"] == 6
        assert by_category["knives"] == 7
        assert by_category["boats_kayaks"] == 7
        assert by_category["electronics"] == 6
        assert by_category["coolers"] == 6
        assert by_category["processing"] == 6
    
    def test_search_suppliers_spypoint(self):
        """GET /api/v1/bionic/seo/suppliers/search?q=Spypoint - Recherche"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seo/suppliers/search?q=Spypoint")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["query"] == "Spypoint"
        assert data["count"] >= 1
        
        # Verify Spypoint is in results
        companies = [r["company"] for r in data["results"]]
        assert "Spypoint" in companies
    
    def test_search_suppliers_vortex(self):
        """GET /api/v1/bionic/seo/suppliers/search?q=Vortex - Recherche optiques"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seo/suppliers/search?q=Vortex")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["count"] >= 1
    
    def test_get_seo_pages(self):
        """GET /api/v1/bionic/seo/suppliers/seo-pages - Pages SEO satellites"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seo/suppliers/seo-pages")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["count"] == 104  # One page per supplier
        assert data["ready_for_integration"] == True
        
        # Verify SEO page structure
        seo_page = data["seo_pages"][0]
        assert "slug" in seo_page
        assert "title" in seo_page
        assert "meta_description" in seo_page
        assert "h1" in seo_page
        assert "canonical_url" in seo_page
        assert seo_page["jsonld_ready"] == True
    
    def test_invalid_category_returns_404(self):
        """GET /api/v1/bionic/seo/suppliers/by-category/invalid - Should return 404"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seo/suppliers/by-category/invalid_category")
        assert response.status_code == 404


class TestMasterSwitchX300:
    """Tests for Master Switch X300% - Contrôle global ON/OFF"""
    
    def test_get_all_switches_status(self):
        """GET /api/v1/master-switch/status - Tous switches actifs"""
        response = requests.get(f"{BASE_URL}/api/v1/master-switch/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "switches" in data
        assert "summary" in data
        
        # Verify expected switches exist
        switches = data["switches"]
        expected_switches = ["global", "captation", "enrichment", "triggers", 
                           "scoring", "seo", "marketing_calendar", "consent_layer"]
        for switch_id in expected_switches:
            assert switch_id in switches, f"Switch {switch_id} not found"
            assert "is_active" in switches[switch_id]
            assert "name" in switches[switch_id]
            assert "description" in switches[switch_id]
        
        # Verify summary
        summary = data["summary"]
        assert summary["total"] == 8
        assert "active" in summary
        assert "inactive" in summary
        assert "global_state" in summary
    
    def test_check_module_status_captation(self):
        """GET /api/v1/master-switch/check/captation - Vérifier module captation"""
        response = requests.get(f"{BASE_URL}/api/v1/master-switch/check/captation")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["module"] == "captation"
        assert "is_active" in data
    
    def test_check_module_status_seo(self):
        """GET /api/v1/master-switch/check/seo - Vérifier module SEO"""
        response = requests.get(f"{BASE_URL}/api/v1/master-switch/check/seo")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["module"] == "seo"
    
    def test_get_switch_logs(self):
        """GET /api/v1/master-switch/logs - Historique des changements"""
        response = requests.get(f"{BASE_URL}/api/v1/master-switch/logs")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "logs" in data
        assert "count" in data


class TestContactEngineX300:
    """Tests for Contact Engine X300% - Captation totale"""
    
    def test_get_dashboard(self):
        """GET /api/v1/contact-engine/dashboard - Dashboard captation"""
        response = requests.get(f"{BASE_URL}/api/v1/contact-engine/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "dashboard" in data
        
        dashboard = data["dashboard"]
        assert "visitors" in dashboard
        assert "contacts" in dashboard
        assert "events" in dashboard
        assert "top_sources" in dashboard
        assert "average_scores" in dashboard
        
        # Verify visitors structure
        visitors = dashboard["visitors"]
        assert "total" in visitors
        assert "anonymous" in visitors
        assert "identified" in visitors
        assert "conversion_rate" in visitors
    
    def test_get_contacts_list(self):
        """GET /api/v1/contact-engine/contacts - Liste des contacts"""
        response = requests.get(f"{BASE_URL}/api/v1/contact-engine/contacts")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "contacts" in data
        assert "pagination" in data
    
    def test_track_visitor(self):
        """POST /api/v1/contact-engine/track/visitor - Track visiteur"""
        visitor_data = {
            "page_url": "/test-page",
            "referrer": "https://google.com",
            "user_agent": "TestAgent/1.0"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/contact-engine/track/visitor",
            json=visitor_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "visitor_id" in data
        assert data["status"] in ["created", "updated"]
    
    def test_track_ad_click(self):
        """POST /api/v1/contact-engine/track/ad-click - Track clic publicitaire"""
        ad_data = {
            "platform": "google",
            "campaign_id": "test_campaign",
            "ad_id": "test_ad",
            "landing_page": "/landing"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/contact-engine/track/ad-click",
            json=ad_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "visitor_id" in data
        assert data["event"] == "ad_click_tracked"
    
    def test_track_social_interaction(self):
        """POST /api/v1/contact-engine/track/social - Track interaction sociale"""
        social_data = {
            "platform": "facebook",
            "action": "share",
            "content_id": "test_content"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/contact-engine/track/social",
            json=social_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["event"] == "social_tracked"


class TestTriggerEngineX300:
    """Tests for Trigger Engine X300% - Marketing Automation"""
    
    def test_get_triggers_list(self):
        """GET /api/v1/trigger-engine/triggers - Liste des triggers"""
        response = requests.get(f"{BASE_URL}/api/v1/trigger-engine/triggers")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "triggers" in data
    
    def test_get_trigger_stats(self):
        """GET /api/v1/trigger-engine/stats - Statistiques triggers"""
        response = requests.get(f"{BASE_URL}/api/v1/trigger-engine/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "stats" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
