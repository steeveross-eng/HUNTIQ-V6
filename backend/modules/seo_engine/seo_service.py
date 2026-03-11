"""
BIONIC SEO Service - V5-ULTIME
==============================

Service principal du SEO Engine.
Orchestration de tous les composants:
- Clusters
- Pages
- JSON-LD
- Analytics
- Automation
- Generation

Module isolé - Architecture LEGO V5.
"""

from datetime import datetime, timezone
import logging

from .seo_clusters import SEOClustersManager
from .seo_pages import SEOPagesManager
from .seo_jsonld import SEOJsonLDManager
from .seo_analytics import SEOAnalyticsManager
from .seo_automation import SEOAutomationManager
from .seo_generation import SEOGenerationManager

logger = logging.getLogger(__name__)


class SEOService:
    """Service principal du SEO Engine"""
    
    # ============================================
    # DASHBOARD
    # ============================================
    
    @staticmethod
    async def get_dashboard(db) -> dict:
        """Dashboard complet du SEO Engine"""
        try:
            # Stats analytics
            analytics = await SEOAnalyticsManager.get_dashboard_stats(db)
            
            # Stats clusters
            clusters_stats = await SEOClustersManager.get_clusters_stats(db)
            
            # Stats pages
            pages_stats = await SEOPagesManager.get_pages_stats(db)
            
            # Stats schemas
            schemas_stats = await SEOJsonLDManager.get_schemas_stats(db)
            
            # Alertes non lues
            alerts = await SEOAutomationManager.get_alerts(db, is_read=False, limit=5)
            
            # Suggestions de contenu
            suggestions = await SEOAutomationManager.get_content_suggestions(db)
            
            return {
                "success": True,
                "dashboard": {
                    "overview": analytics.get("stats", {}),
                    "clusters": clusters_stats.get("stats", {}),
                    "pages": pages_stats.get("stats", {}),
                    "schemas": schemas_stats.get("stats", {}),
                    "alerts": {
                        "unread_count": len(alerts.get("alerts", [])),
                        "recent": alerts.get("alerts", [])[:3]
                    },
                    "suggestions": {
                        "count": suggestions.get("total", 0),
                        "top": suggestions.get("suggestions", [])[:3]
                    }
                },
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting SEO dashboard: {e}")
            return {"success": False, "error": str(e)}
    
    # ============================================
    # CONTENT WORKFLOW
    # ============================================
    
    @staticmethod
    async def create_content_workflow(db, cluster_id: str, page_type: str,
                                      target_keyword: str, knowledge_data: dict = None) -> dict:
        """Workflow complet de création de contenu"""
        try:
            workflow = {
                "id": f"workflow_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "status": "started",
                "steps": []
            }
            
            # Step 1: Générer outline
            outline = await SEOGenerationManager.generate_page_outline(
                cluster_id, page_type, target_keyword, knowledge_data
            )
            workflow["steps"].append({
                "step": 1,
                "name": "Generate Outline",
                "status": "completed" if outline.get("success") else "failed",
                "data": outline.get("outline")
            })
            
            # Step 2: Créer la page draft
            if outline.get("success"):
                page_data = {
                    "cluster_id": cluster_id,
                    "page_type": page_type,
                    "status": "draft",
                    "slug": target_keyword.lower().replace(" ", "-"),
                    "url_path": f"/{page_type}/{target_keyword.lower().replace(' ', '-')}",
                    "title_fr": outline["outline"]["structure"]["title_suggestions"][0],
                    "meta_description_fr": outline["outline"]["structure"]["meta_description_template"],
                    "primary_keyword": target_keyword,
                    "h1": outline["outline"]["structure"]["h1"],
                    "h2_list": [s["h2"] for s in outline["outline"]["structure"]["sections"]],
                    "word_count": outline["outline"]["structure"]["total_word_count"],
                    "reading_time_min": outline["outline"]["structure"]["reading_time_min"],
                    "jsonld_types": outline["outline"]["jsonld_recommendations"]
                }
                
                page_result = await SEOPagesManager.create_page(db, page_data)
                workflow["steps"].append({
                    "step": 2,
                    "name": "Create Draft Page",
                    "status": "completed" if page_result.get("success") else "failed",
                    "data": {"page_id": page_result.get("page", {}).get("id")}
                })
                
                # Step 3: Calculer score SEO initial
                if page_result.get("success"):
                    seo_score = SEOGenerationManager.calculate_seo_score(page_result["page"])
                    workflow["steps"].append({
                        "step": 3,
                        "name": "Calculate SEO Score",
                        "status": "completed",
                        "data": seo_score
                    })
            
            workflow["status"] = "completed"
            
            return {
                "success": True,
                "workflow": workflow
            }
        except Exception as e:
            logger.error(f"Error in content workflow: {e}")
            return {"success": False, "error": str(e)}
    
    # ============================================
    # OPTIMIZATION
    # ============================================
    
    @staticmethod
    async def optimize_page(db, page_id: str) -> dict:
        """Optimiser une page existante"""
        try:
            # Récupérer la page
            page_result = await SEOPagesManager.get_page_by_id(db, page_id)
            if not page_result.get("success"):
                return page_result
            
            page = page_result["page"]
            
            # Calculer score actuel
            current_score = SEOGenerationManager.calculate_seo_score(page)
            
            # Calculer liens internes
            internal_links = await SEOPagesManager.calculate_internal_links(db, page_id)
            
            # Recommandations JSON-LD
            jsonld_recommendations = SEOGenerationManager._recommend_jsonld(page.get("page_type", "satellite"))
            
            return {
                "success": True,
                "page_id": page_id,
                "current_score": current_score,
                "internal_links_suggestions": internal_links.get("suggestions", []),
                "jsonld_recommendations": jsonld_recommendations,
                "optimization_checklist": [
                    {"item": "Title optimization", "done": len(current_score["issues"]) == 0},
                    {"item": "Meta description", "done": "Meta description" not in str(current_score["issues"])},
                    {"item": "Internal linking", "done": len(page.get("internal_links_out", [])) >= 3},
                    {"item": "JSON-LD schemas", "done": len(page.get("jsonld_types", [])) > 0},
                    {"item": "Word count", "done": page.get("word_count", 0) >= 800}
                ]
            }
        except Exception as e:
            logger.error(f"Error optimizing page: {e}")
            return {"success": False, "error": str(e)}
    
    # ============================================
    # REPORTS
    # ============================================
    
    @staticmethod
    async def generate_seo_report(db, report_type: str = "full") -> dict:
        """Générer un rapport SEO complet"""
        try:
            report = {
                "type": report_type,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "sections": []
            }
            
            # Section 1: Executive Summary
            dashboard = await SEOService.get_dashboard(db)
            report["sections"].append({
                "title": "Executive Summary",
                "data": dashboard.get("dashboard", {}).get("overview", {})
            })
            
            # Section 2: Performance
            analytics_report = await SEOAnalyticsManager.generate_report(db)
            report["sections"].append({
                "title": "Performance Analysis",
                "data": analytics_report.get("report", {})
            })
            
            # Section 3: Top Performers
            top_pages = await SEOAnalyticsManager.get_top_pages(db, "clicks", 10)
            report["sections"].append({
                "title": "Top Performing Pages",
                "data": top_pages.get("pages", [])
            })
            
            # Section 4: Opportunities
            opportunities = await SEOAnalyticsManager.get_optimization_opportunities(db)
            report["sections"].append({
                "title": "Optimization Opportunities",
                "data": opportunities.get("opportunities", [])
            })
            
            # Section 5: Content Suggestions
            suggestions = await SEOAutomationManager.get_content_suggestions(db)
            report["sections"].append({
                "title": "Content Recommendations",
                "data": suggestions.get("suggestions", [])
            })
            
            return {
                "success": True,
                "report": report
            }
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return {"success": False, "error": str(e)}
    
    # ============================================
    # KNOWLEDGE LAYER INTEGRATION
    # ============================================
    
    @staticmethod
    async def enrich_with_knowledge(db, page_id: str, species_id: str = None, 
                                   knowledge_api_response: dict = None) -> dict:
        """Enrichir une page avec les données du Knowledge Layer"""
        try:
            page_result = await SEOPagesManager.get_page_by_id(db, page_id)
            if not page_result.get("success"):
                return page_result
            
            enrichment = {
                "page_id": page_id,
                "enrichments_applied": []
            }
            
            if knowledge_api_response:
                # Extraire les données pertinentes
                species_data = knowledge_api_response.get("species", {})
                rules_data = knowledge_api_response.get("applied_rules", {})
                seasonal_data = knowledge_api_response.get("seasonal_phase", {})
                
                updates = {
                    "knowledge_data_used": {
                        "species": species_data,
                        "rules": rules_data.get("applicable_rules", []),
                        "seasonal": seasonal_data
                    },
                    "knowledge_rules_applied": [r.get("rule_id") for r in rules_data.get("applicable_rules", [])]
                }
                
                if species_id:
                    updates["target_species"] = [species_id]
                
                # Mettre à jour la page
                await SEOPagesManager.update_page(db, page_id, updates)
                
                enrichment["enrichments_applied"] = [
                    f"Species data: {species_data.get('common_name_fr', 'N/A')}",
                    f"Rules applied: {len(rules_data.get('applicable_rules', []))}",
                    f"Seasonal phase: {seasonal_data.get('name', 'N/A')}"
                ]
            
            return {
                "success": True,
                "enrichment": enrichment
            }
        except Exception as e:
            logger.error(f"Error enriching with knowledge: {e}")
            return {"success": False, "error": str(e)}


logger.info("SEOService initialized - V5 LEGO Module")
