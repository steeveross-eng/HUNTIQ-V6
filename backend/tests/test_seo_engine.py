"""
BIONIC SEO Engine V5 - Backend API Tests
=========================================

Tests for the SEO Engine module endpoints:
- /api/v1/bionic/seo/* endpoints
- Clusters, Pages, JSON-LD, Analytics, Automation

Iteration 9 - SEO Engine V5 Testing
"""

import pytest
import requests
import os
from datetime import datetime

# Get BASE_URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestSEOEngineInfo:
    """Test SEO Engine info endpoint"""
    
    def test_seo_engine_info(self):
        """GET /api/v1/bionic/seo/ - Returns module info"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seo/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["module"] == "seo_engine"
        assert data["version"] == "1.0.0"
        assert data["architecture"] == "LEGO_V5_ISOLATED"
        assert "components" in data
        assert len(data["components"]) >= 6  # clusters, pages, jsonld, analytics, automation, generation
        assert "endpoints" in data
        print(f"✓ SEO Engine info: v{data['version']} - {len(data['components'])} components")


class TestSEODashboard:
    """Test SEO Dashboard endpoint"""
    
    def test_seo_dashboard(self):
        """GET /api/v1/bionic/seo/dashboard - Returns dashboard data"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seo/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "dashboard" in data
        
        dashboard = data["dashboard"]
        # Check overview section
        assert "overview" in dashboard
        # Check clusters section
        assert "clusters" in dashboard
        # Check pages section
        assert "pages" in dashboard
        # Check schemas section
        assert "schemas" in dashboard
        # Check alerts section
        assert "alerts" in dashboard
        # Check suggestions section
        assert "suggestions" in dashboard
        
        print(f"✓ SEO Dashboard loaded with all sections")


class TestSEOClusters:
    """Test SEO Clusters endpoints"""
    
    def test_get_all_clusters(self):
        """GET /api/v1/bionic/seo/clusters - Returns all clusters"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seo/clusters")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "clusters" in data
        assert "total" in data
        
        # Should have at least 9 base clusters
        assert data["total"] >= 9
        
        # Verify cluster structure
        if data["clusters"]:
            cluster = data["clusters"][0]
            assert "id" in cluster
            assert "name" in cluster or "name_fr" in cluster
            assert "cluster_type" in cluster
        
        print(f"✓ Clusters list: {data['total']} clusters found")
    
    def test_get_clusters_by_type(self):
        """GET /api/v1/bionic/seo/clusters?cluster_type=species - Filter by type"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seo/clusters?cluster_type=species")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        
        # All returned clusters should be species type
        for cluster in data["clusters"]:
            assert cluster["cluster_type"] == "species"
        
        print(f"✓ Clusters filtered by type: {data['total']} species clusters")
    
    def test_get_clusters_stats(self):
        """GET /api/v1/bionic/seo/clusters/stats - Returns cluster statistics"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seo/clusters/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "stats" in data
        
        stats = data["stats"]
        assert "total_base" in stats
        assert "total_custom" in stats
        assert "total" in stats
        assert "by_type" in stats
        
        # Should have 9 base clusters
        assert stats["total_base"] == 9
        
        print(f"✓ Clusters stats: {stats['total']} total ({stats['total_base']} base, {stats['total_custom']} custom)")
    
    def test_get_cluster_hierarchy(self):
        """GET /api/v1/bionic/seo/clusters/hierarchy - Returns cluster hierarchy"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seo/clusters/hierarchy")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "hierarchy" in data
        
        hierarchy = data["hierarchy"]
        # Should have categories
        assert "species" in hierarchy
        assert "region" in hierarchy
        assert "season" in hierarchy
        assert "technique" in hierarchy
        assert "equipment" in hierarchy
        
        print(f"✓ Cluster hierarchy loaded with {len(hierarchy)} categories")
    
    def test_get_cluster_by_id(self):
        """GET /api/v1/bionic/seo/clusters/{cluster_id} - Returns specific cluster"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seo/clusters/cluster_moose")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "cluster" in data
        
        cluster = data["cluster"]
        assert cluster["id"] == "cluster_moose"
        assert cluster["cluster_type"] == "species"
        assert "primary_keyword" in cluster
        
        print(f"✓ Cluster detail: {cluster['name_fr']}")
    
    def test_get_nonexistent_cluster(self):
        """GET /api/v1/bionic/seo/clusters/{invalid_id} - Returns error"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seo/clusters/nonexistent_cluster_xyz")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == False
        assert "error" in data
        
        print(f"✓ Nonexistent cluster returns error correctly")


class TestSEOPages:
    """Test SEO Pages endpoints"""
    
    def test_get_all_pages(self):
        """GET /api/v1/bionic/seo/pages - Returns all pages"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seo/pages")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "pages" in data
        assert "total" in data
        
        print(f"✓ Pages list: {data['total']} pages found")
    
    def test_get_page_templates(self):
        """GET /api/v1/bionic/seo/pages/templates - Returns page templates"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seo/pages/templates")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "templates" in data
        
        templates = data["templates"]
        # Should have pillar, satellite, opportunity templates
        assert "pillar" in templates
        assert "satellite" in templates
        assert "opportunity" in templates
        
        # Verify template structure
        if templates["pillar"]:
            tpl = templates["pillar"][0]
            assert "id" in tpl
            assert "name_fr" in tpl
            assert "page_type" in tpl
            assert "structure" in tpl
        
        print(f"✓ Page templates: {len(templates['pillar'])} pillar, {len(templates['satellite'])} satellite, {len(templates['opportunity'])} opportunity")
    
    def test_create_and_get_page(self):
        """POST /api/v1/bionic/seo/pages - Create a test page"""
        page_data = {
            "cluster_id": "cluster_moose",
            "page_type": "satellite",
            "status": "draft",
            "slug": "test-seo-page",
            "url_path": "/test/test-seo-page",
            "title_fr": "TEST_Page SEO de test",
            "meta_description_fr": "Description de test pour la page SEO",
            "primary_keyword": "test seo page",
            "word_count": 1000
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/bionic/seo/pages", json=page_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "page" in data
        
        page = data["page"]
        assert page["title_fr"] == page_data["title_fr"]
        assert page["cluster_id"] == page_data["cluster_id"]
        assert "id" in page
        
        page_id = page["id"]
        print(f"✓ Page created: {page_id}")
        
        # Verify with GET
        get_response = requests.get(f"{BASE_URL}/api/v1/bionic/seo/pages/{page_id}")
        assert get_response.status_code == 200
        
        get_data = get_response.json()
        assert get_data["success"] == True
        assert get_data["page"]["id"] == page_id
        
        print(f"✓ Page verified via GET")
        
        # Cleanup - delete the test page
        delete_response = requests.delete(f"{BASE_URL}/api/v1/bionic/seo/pages/{page_id}")
        assert delete_response.status_code == 200
        print(f"✓ Test page deleted")


class TestSEOJsonLD:
    """Test SEO JSON-LD endpoints"""
    
    def test_get_all_schemas(self):
        """GET /api/v1/bionic/seo/jsonld - Returns all schemas"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seo/jsonld")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "schemas" in data
        assert "total" in data
        
        print(f"✓ JSON-LD schemas: {data['total']} schemas found")
    
    def test_get_schemas_stats(self):
        """GET /api/v1/bionic/seo/jsonld/stats - Returns schema statistics"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seo/jsonld/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "stats" in data
        
        stats = data["stats"]
        assert "total" in stats
        assert "valid" in stats
        assert "by_type" in stats
        
        print(f"✓ JSON-LD stats: {stats['total']} total, {stats['valid']} valid")
    
    def test_generate_article_schema(self):
        """POST /api/v1/bionic/seo/jsonld/generate/article - Generate Article schema"""
        page_data = {
            "title_fr": "Guide de chasse à l'orignal",
            "meta_description_fr": "Guide complet pour la chasse à l'orignal au Québec",
            "url_path": "/guides/chasse-orignal",
            "word_count": 3000
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/bionic/seo/jsonld/generate/article", json=page_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "schema" in data
        
        schema = data["schema"]
        assert schema["@type"] == "Article"
        assert schema["@context"] == "https://schema.org"
        assert schema["headline"] == page_data["title_fr"]
        
        print(f"✓ Article schema generated")
    
    def test_generate_faq_schema(self):
        """POST /api/v1/bionic/seo/jsonld/generate/faq - Generate FAQ schema"""
        questions = [
            {"question": "Quand chasser l'orignal?", "answer": "La saison de chasse à l'orignal au Québec..."},
            {"question": "Quel équipement?", "answer": "Pour la chasse à l'orignal, vous aurez besoin..."}
        ]
        
        response = requests.post(f"{BASE_URL}/api/v1/bionic/seo/jsonld/generate/faq", json=questions)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "schema" in data
        
        schema = data["schema"]
        assert schema["@type"] == "FAQPage"
        assert len(schema["mainEntity"]) == 2
        
        print(f"✓ FAQ schema generated with {len(schema['mainEntity'])} questions")
    
    def test_validate_schema(self):
        """POST /api/v1/bionic/seo/jsonld/validate - Validate a schema"""
        schema_data = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Test Article",
            "author": {"@type": "Organization", "name": "BIONIC"},
            "publisher": {"@type": "Organization", "name": "BIONIC"},
            "datePublished": "2026-01-15"
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/bionic/seo/jsonld/validate", json=schema_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "is_valid" in data
        assert "errors" in data
        assert "warnings" in data
        
        print(f"✓ Schema validation: valid={data['is_valid']}, errors={len(data['errors'])}")


class TestSEOAnalytics:
    """Test SEO Analytics endpoints"""
    
    def test_get_analytics_dashboard(self):
        """GET /api/v1/bionic/seo/analytics/dashboard - Returns analytics dashboard"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seo/analytics/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "stats" in data
        
        stats = data["stats"]
        # Check all sections
        assert "clusters" in stats
        assert "pages" in stats
        assert "traffic" in stats
        assert "performance" in stats
        assert "technical" in stats
        
        print(f"✓ Analytics dashboard loaded")
    
    def test_get_top_pages(self):
        """GET /api/v1/bionic/seo/analytics/top-pages - Returns top performing pages"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seo/analytics/top-pages?metric=clicks&limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "pages" in data
        assert "metric" in data
        
        print(f"✓ Top pages: {len(data['pages'])} pages returned")
    
    def test_get_top_clusters(self):
        """GET /api/v1/bionic/seo/analytics/top-clusters - Returns top performing clusters"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seo/analytics/top-clusters?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "clusters" in data
        
        print(f"✓ Top clusters: {len(data['clusters'])} clusters returned")
    
    def test_get_traffic_trend(self):
        """GET /api/v1/bionic/seo/analytics/traffic-trend - Returns traffic trend"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seo/analytics/traffic-trend?days=30")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "trend" in data
        assert "period_days" in data
        
        # Should have 30 days of data
        assert len(data["trend"]) == 30
        
        print(f"✓ Traffic trend: {len(data['trend'])} days of data")
    
    def test_get_opportunities(self):
        """GET /api/v1/bionic/seo/analytics/opportunities - Returns optimization opportunities"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seo/analytics/opportunities")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "opportunities" in data
        assert "total" in data
        
        print(f"✓ Opportunities: {data['total']} opportunities found")
    
    def test_get_analytics_report(self):
        """GET /api/v1/bionic/seo/analytics/report - Returns SEO report"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seo/analytics/report?period=monthly")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "report" in data
        
        report = data["report"]
        assert "report_type" in report
        assert "summary" in report
        
        print(f"✓ Analytics report generated")


class TestSEOAutomation:
    """Test SEO Automation endpoints"""
    
    def test_get_automation_rules(self):
        """GET /api/v1/bionic/seo/automation/rules - Returns automation rules"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seo/automation/rules")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "rules" in data
        assert "total" in data
        
        # Should have at least 5 default rules
        assert data["total"] >= 5
        
        # Verify rule structure
        if data["rules"]:
            rule = data["rules"][0]
            assert "id" in rule
            assert "name_fr" in rule
            assert "is_active" in rule
        
        print(f"✓ Automation rules: {data['total']} rules found")
    
    def test_get_content_suggestions(self):
        """GET /api/v1/bionic/seo/automation/suggestions - Returns content suggestions"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seo/automation/suggestions")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "suggestions" in data
        assert "total" in data
        
        print(f"✓ Content suggestions: {data['total']} suggestions found")
    
    def test_get_content_calendar(self):
        """GET /api/v1/bionic/seo/automation/calendar - Returns content calendar"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seo/automation/calendar")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "calendar" in data
        assert "period" in data
        
        print(f"✓ Content calendar loaded")
    
    def test_get_scheduled_tasks(self):
        """GET /api/v1/bionic/seo/automation/tasks - Returns scheduled tasks"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seo/automation/tasks")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "tasks" in data
        assert "total" in data
        
        print(f"✓ Scheduled tasks: {data['total']} tasks found")
    
    def test_get_alerts(self):
        """GET /api/v1/bionic/seo/automation/alerts - Returns SEO alerts"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seo/automation/alerts?limit=20")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "alerts" in data
        assert "total" in data
        
        print(f"✓ SEO alerts: {data['total']} alerts found")


class TestSEOGeneration:
    """Test SEO Generation endpoints"""
    
    def test_generate_meta_tags(self):
        """POST /api/v1/bionic/seo/generate/meta-tags - Generate meta tags"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/seo/generate/meta-tags",
            params={
                "title": "Guide chasse orignal",
                "keyword": "chasse orignal québec",
                "content_summary": "Guide complet pour la chasse à l'orignal"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "meta_tags" in data
        
        meta = data["meta_tags"]
        assert "title" in meta
        assert "meta_description" in meta
        
        print(f"✓ Meta tags generated")
    
    def test_calculate_seo_score(self):
        """POST /api/v1/bionic/seo/generate/seo-score - Calculate SEO score"""
        page_data = {
            "title_fr": "Guide complet de la chasse à l'orignal au Québec",
            "meta_description_fr": "Découvrez notre guide complet pour la chasse à l'orignal au Québec. Techniques, équipement, réglementation et meilleurs spots.",
            "primary_keyword": "chasse orignal québec",
            "word_count": 3000,
            "h1": "Guide complet de la chasse à l'orignal au Québec",
            "h2_list": ["Introduction", "Comportement", "Techniques", "Équipement", "Réglementation"]
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/bionic/seo/generate/seo-score", json=page_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "seo_analysis" in data
        
        analysis = data["seo_analysis"]
        assert "score" in analysis
        assert "issues" in analysis
        assert "recommendations" in analysis
        
        print(f"✓ SEO score calculated: {analysis['score']}")


class TestSEOWorkflow:
    """Test SEO Workflow endpoints"""
    
    def test_get_full_report(self):
        """GET /api/v1/bionic/seo/reports/full - Returns full SEO report"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seo/reports/full")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "report" in data
        
        report = data["report"]
        assert "type" in report
        assert "sections" in report
        assert len(report["sections"]) >= 4
        
        print(f"✓ Full SEO report generated with {len(report['sections'])} sections")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
