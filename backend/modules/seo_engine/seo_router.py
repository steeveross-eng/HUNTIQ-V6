"""
BIONIC SEO Router - V5-ULTIME
=============================

Routes API pour le SEO Engine.
Prefix: /api/v1/bionic/seo

Endpoints:
- /dashboard : Dashboard SEO
- /clusters/* : Gestion des clusters
- /pages/* : Gestion des pages
- /jsonld/* : Schémas JSON-LD
- /analytics/* : Analytics et KPIs
- /automation/* : Automatisation
- /generate/* : Génération de contenu

Module isolé - Architecture LEGO V5.
"""

from fastapi import APIRouter, Query, Body
from typing import Optional, List
from datetime import datetime, timezone
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient

from .seo_service import SEOService
from .seo_clusters import SEOClustersManager
from .seo_pages import SEOPagesManager
from .seo_jsonld import SEOJsonLDManager
from .seo_analytics import SEOAnalyticsManager
from .seo_automation import SEOAutomationManager
from .seo_generation import SEOGenerationManager
from .seo_models import (
    GenerateOutlineRequest,
    GenerateMetaTagsRequest,
    GenerateViralCapsuleRequest,
    CreateContentWorkflowRequest,
    EnrichWithKnowledgeRequest,
    GeneratePillarContentRequest,
    GenerateFAQRequest
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/bionic/seo", tags=["BIONIC SEO Engine"])

# Database
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'bionic_db')
_client = None
_db = None

def get_db():
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(MONGO_URL)
        _db = _client[DB_NAME]
    return _db


# ==============================================
# MODULE INFO
# ==============================================

@router.get("/")
async def seo_engine_info():
    """Information sur le SEO Engine"""
    return {
        "module": "seo_engine",
        "version": "1.0.0",
        "description": "BIONIC SEO Engine V5-ULTIME - Plan SEO +300%",
        "architecture": "LEGO_V5_ISOLATED",
        "components": [
            "seo_clusters",
            "seo_pages",
            "seo_jsonld",
            "seo_analytics",
            "seo_automation",
            "seo_generation"
        ],
        "endpoints": {
            "dashboard": "/dashboard",
            "clusters": "/clusters/*",
            "pages": "/pages/*",
            "jsonld": "/jsonld/*",
            "analytics": "/analytics/*",
            "automation": "/automation/*",
            "generate": "/generate/*"
        },
        "integrations": ["bionic_knowledge_engine"]
    }


# ==============================================
# DASHBOARD
# ==============================================

@router.get("/dashboard")
async def get_seo_dashboard():
    """Dashboard complet du SEO Engine"""
    return await SEOService.get_dashboard(get_db())


# ==============================================
# CLUSTERS
# ==============================================

@router.get("/clusters")
async def get_all_clusters(
    cluster_type: Optional[str] = None,
    is_active: bool = True,
    limit: int = Query(100, le=500)
):
    """Liste des clusters SEO"""
    return await SEOClustersManager.get_all_clusters(get_db(), cluster_type, is_active, limit)

@router.get("/clusters/stats")
async def get_clusters_stats():
    """Statistiques des clusters"""
    return await SEOClustersManager.get_clusters_stats(get_db())

@router.get("/clusters/hierarchy")
async def get_cluster_hierarchy():
    """Hiérarchie des clusters"""
    return await SEOClustersManager.get_cluster_hierarchy(get_db())

@router.get("/clusters/{cluster_id}")
async def get_cluster(cluster_id: str):
    """Détail d'un cluster"""
    return await SEOClustersManager.get_cluster_by_id(get_db(), cluster_id)

@router.post("/clusters")
async def create_cluster(cluster_data: dict = Body(...)):
    """Créer un cluster"""
    return await SEOClustersManager.create_cluster(get_db(), cluster_data)

@router.put("/clusters/{cluster_id}")
async def update_cluster(cluster_id: str, updates: dict = Body(...)):
    """Mettre à jour un cluster"""
    return await SEOClustersManager.update_cluster(get_db(), cluster_id, updates)

@router.delete("/clusters/{cluster_id}")
async def delete_cluster(cluster_id: str):
    """Supprimer un cluster"""
    return await SEOClustersManager.delete_cluster(get_db(), cluster_id)


# ==============================================
# PAGES
# ==============================================

@router.get("/pages")
async def get_all_pages(
    cluster_id: Optional[str] = None,
    page_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(100, le=500)
):
    """Liste des pages SEO"""
    return await SEOPagesManager.get_all_pages(get_db(), cluster_id, page_type, status, limit)

@router.get("/pages/stats")
async def get_pages_stats():
    """Statistiques des pages"""
    return await SEOPagesManager.get_pages_stats(get_db())

@router.get("/pages/templates")
async def get_page_templates():
    """Templates de pages disponibles"""
    return SEOPagesManager.get_all_templates()

@router.get("/pages/{page_id}")
async def get_page(page_id: str):
    """Détail d'une page"""
    return await SEOPagesManager.get_page_by_id(get_db(), page_id)

@router.post("/pages")
async def create_page(page_data: dict = Body(...)):
    """Créer une page"""
    return await SEOPagesManager.create_page(get_db(), page_data)

@router.put("/pages/{page_id}")
async def update_page(page_id: str, updates: dict = Body(...)):
    """Mettre à jour une page"""
    return await SEOPagesManager.update_page(get_db(), page_id, updates)

@router.post("/pages/{page_id}/publish")
async def publish_page(page_id: str):
    """Publier une page"""
    return await SEOPagesManager.publish_page(get_db(), page_id)

@router.delete("/pages/{page_id}")
async def delete_page(page_id: str):
    """Supprimer une page"""
    return await SEOPagesManager.delete_page(get_db(), page_id)

@router.get("/pages/{page_id}/internal-links")
async def get_internal_link_suggestions(page_id: str):
    """Suggestions de liens internes"""
    return await SEOPagesManager.calculate_internal_links(get_db(), page_id)

@router.get("/pages/{page_id}/optimize")
async def get_page_optimization(page_id: str):
    """Recommandations d'optimisation"""
    return await SEOService.optimize_page(get_db(), page_id)


# ==============================================
# JSON-LD
# ==============================================

@router.get("/jsonld")
async def get_all_schemas(
    page_id: Optional[str] = None,
    schema_type: Optional[str] = None,
    limit: int = Query(100, le=500)
):
    """Liste des schémas JSON-LD"""
    return await SEOJsonLDManager.get_all_schemas(get_db(), page_id, schema_type, limit)

@router.get("/jsonld/stats")
async def get_schemas_stats():
    """Statistiques des schémas"""
    return await SEOJsonLDManager.get_schemas_stats(get_db())

@router.post("/jsonld/generate/article")
async def generate_article_schema(page_data: dict = Body(...)):
    """Générer un schéma Article"""
    return {"success": True, "schema": SEOJsonLDManager.generate_article_schema(page_data)}

@router.post("/jsonld/generate/howto")
async def generate_howto_schema(page_data: dict = Body(...), steps: List[dict] = Body(...)):
    """Générer un schéma HowTo"""
    return {"success": True, "schema": SEOJsonLDManager.generate_howto_schema(page_data, steps)}

@router.post("/jsonld/generate/faq")
async def generate_faq_schema(request: GenerateFAQRequest):
    """Générer un schéma FAQPage"""
    return {"success": True, "schema": SEOJsonLDManager.generate_faq_schema(request.questions)}

@router.post("/jsonld/generate/breadcrumb")
async def generate_breadcrumb_schema(breadcrumbs: List[dict] = Body(...)):
    """Générer un schéma BreadcrumbList"""
    return {"success": True, "schema": SEOJsonLDManager.generate_breadcrumb_schema(breadcrumbs)}

@router.post("/jsonld/save")
async def save_schema(page_id: str, schema_type: str, schema_data: dict = Body(...)):
    """Sauvegarder un schéma"""
    return await SEOJsonLDManager.save_schema(get_db(), page_id, schema_type, schema_data)

@router.post("/jsonld/validate")
async def validate_schema(schema_data: dict = Body(...)):
    """Valider un schéma JSON-LD"""
    return await SEOJsonLDManager.validate_schema(schema_data)


# ==============================================
# ANALYTICS
# ==============================================

@router.get("/analytics/dashboard")
async def get_analytics_dashboard():
    """Dashboard analytics SEO"""
    return await SEOAnalyticsManager.get_dashboard_stats(get_db())

@router.get("/analytics/top-pages")
async def get_top_pages(
    metric: str = "clicks",
    limit: int = Query(10, le=50)
):
    """Pages les plus performantes"""
    return await SEOAnalyticsManager.get_top_pages(get_db(), metric, limit)

@router.get("/analytics/top-clusters")
async def get_top_clusters(limit: int = Query(10, le=50)):
    """Clusters les plus performants"""
    return await SEOAnalyticsManager.get_top_clusters(get_db(), limit)

@router.get("/analytics/traffic-trend")
async def get_traffic_trend(days: int = Query(30, le=90)):
    """Tendance du trafic"""
    return await SEOAnalyticsManager.get_traffic_trend(get_db(), days)

@router.get("/analytics/opportunities")
async def get_opportunities():
    """Opportunités d'optimisation"""
    return await SEOAnalyticsManager.get_optimization_opportunities(get_db())

@router.get("/analytics/report")
async def get_analytics_report(period: str = "monthly"):
    """Rapport SEO"""
    return await SEOAnalyticsManager.generate_report(get_db(), period)


# ==============================================
# AUTOMATION
# ==============================================

@router.get("/automation/rules")
async def get_automation_rules():
    """Règles d'automatisation"""
    return await SEOAutomationManager.get_all_rules(get_db())

@router.put("/automation/rules/{rule_id}/toggle")
async def toggle_automation_rule(rule_id: str, is_active: bool):
    """Activer/désactiver une règle"""
    return await SEOAutomationManager.toggle_rule(get_db(), rule_id, is_active)

@router.get("/automation/suggestions")
async def get_content_suggestions():
    """Suggestions de contenu"""
    return await SEOAutomationManager.get_content_suggestions(get_db())

@router.get("/automation/calendar")
async def get_content_calendar():
    """Calendrier de contenu"""
    return await SEOAutomationManager.get_content_calendar(get_db())

@router.get("/automation/tasks")
async def get_scheduled_tasks(status: Optional[str] = None):
    """Tâches planifiées"""
    return await SEOAutomationManager.get_scheduled_tasks(get_db(), status)

@router.post("/automation/tasks")
async def schedule_task(task_data: dict = Body(...)):
    """Planifier une tâche"""
    return await SEOAutomationManager.schedule_task(get_db(), task_data)

@router.get("/automation/alerts")
async def get_alerts(is_read: Optional[bool] = None, limit: int = Query(50, le=200)):
    """Alertes SEO"""
    return await SEOAutomationManager.get_alerts(get_db(), is_read, limit)

@router.put("/automation/alerts/{alert_id}/read")
async def mark_alert_read(alert_id: str):
    """Marquer une alerte comme lue"""
    return await SEOAutomationManager.mark_alert_read(get_db(), alert_id)


# ==============================================
# GENERATION
# ==============================================

@router.post("/generate/outline")
async def generate_page_outline(request: GenerateOutlineRequest):
    """Générer un outline de page"""
    return await SEOGenerationManager.generate_page_outline(
        request.cluster_id, request.page_type, request.target_keyword, request.knowledge_data
    )

@router.post("/generate/meta-tags")
async def generate_meta_tags(request: GenerateMetaTagsRequest):
    """Générer des meta tags optimisés"""
    return {
        "success": True,
        "meta_tags": SEOGenerationManager.generate_meta_tags(
            request.title, request.keyword, request.content_summary
        )
    }

@router.post("/generate/seo-score")
async def calculate_seo_score(page_data: dict = Body(...)):
    """Calculer le score SEO"""
    return {
        "success": True,
        "seo_analysis": SEOGenerationManager.calculate_seo_score(page_data)
    }

@router.post("/generate/viral-capsule")
async def generate_viral_capsule(request: GenerateViralCapsuleRequest):
    """Générer une capsule virale"""
    return SEOGenerationManager.generate_viral_capsule(
        request.topic, request.species_id, request.knowledge_data
    )


# ==============================================
# WORKFLOW
# ==============================================

@router.post("/workflow/create-content")
async def create_content_workflow(request: CreateContentWorkflowRequest):
    """Workflow complet de création de contenu"""
    return await SEOService.create_content_workflow(
        get_db(), request.cluster_id, request.page_type, 
        request.target_keyword, request.knowledge_data
    )

@router.post("/workflow/enrich-with-knowledge")
async def enrich_page_with_knowledge(request: EnrichWithKnowledgeRequest):
    """Enrichir une page avec le Knowledge Layer"""
    return await SEOService.enrich_with_knowledge(
        get_db(), request.page_id, request.species_id, request.knowledge_api_response
    )


# ==============================================
# AI CONTENT GENERATION
# ==============================================

@router.post("/generate/pillar-content")
async def generate_pillar_content(request: GeneratePillarContentRequest):
    """Générer le contenu complet d'une page pilier via IA"""
    from .seo_content_generator import seo_content_generator
    
    result = await seo_content_generator.generate_pillar_content(
        species_id=request.species_id,
        keyword=request.keyword,
        knowledge_data=request.knowledge_data,
        language="fr"
    )
    
    # Si succès, sauvegarder en base
    if result.get("success"):
        db = get_db()
        content_doc = {
            "type": "pillar_generated",
            "species_id": request.species_id,
            "keyword": request.keyword,
            "content": result.get("content"),
            "metadata": result.get("metadata"),
            "status": "draft",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.seo_generated_content.insert_one(content_doc)
    
    return result


@router.get("/generate/pillar-content/history")
async def get_generated_content_history(limit: int = Query(20, le=100)):
    """Historique des contenus générés"""
    db = get_db()
    history = await db.seo_generated_content.find(
        {}, {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    return {
        "success": True,
        "total": len(history),
        "history": history
    }


# ==============================================
# REPORTS
# ==============================================

@router.get("/reports/full")
async def get_full_seo_report():
    """Rapport SEO complet"""
    return await SEOService.generate_seo_report(get_db(), "full")


# ==============================================
# DOCUMENTATION INTERNE
# ==============================================

@router.get("/documentation")
async def get_seo_documentation():
    """
    Récupérer la documentation interne du module SEO.
    Retourne le contenu du fichier SEO_ENGINE_DOCUMENTATION_V5.md
    """
    import os
    
    doc_path = "/app/docs/SEO_ENGINE_DOCUMENTATION_V5.md"
    
    if not os.path.exists(doc_path):
        return {
            "success": False,
            "error": "Documentation non trouvée"
        }
    
    try:
        with open(doc_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        return {
            "success": True,
            "documentation": {
                "title": "SEO Engine V5-ULTIME - Documentation Complète",
                "version": "1.0.0",
                "last_updated": "Décembre 2025",
                "content": content,
                "sections": [
                    "Vue d'Ensemble",
                    "Architecture et Structure des Fichiers",
                    "Endpoints API Complets (41)",
                    "Fonctionnalités Actives",
                    "Logique Métier Détaillée",
                    "Automatisations en Place",
                    "Règles SEO Existantes",
                    "Dépendances Internes",
                    "Intégrations Actuelles",
                    "Indicateurs de Performance (KPIs)",
                    "Paramètres et Configurations",
                    "Schémas de Données (MongoDB)",
                    "Annexes Techniques"
                ]
            }
        }
    except Exception as e:
        logger.error(f"Error reading documentation: {e}")
        return {
            "success": False,
            "error": str(e)
        }


logger.info("BIONIC SEO Router initialized - V5 LEGO Module")
