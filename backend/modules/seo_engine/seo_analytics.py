"""
BIONIC SEO Analytics - V5-ULTIME
================================

Analytics et KPIs pour le SEO Engine.
Métriques:
- Trafic organique
- Positions moyennes
- CTR
- Conversions
- Performance par cluster
- Évolution temporelle

Module isolé - aucun import croisé.
"""

from datetime import datetime, timezone, timedelta
import logging

logger = logging.getLogger(__name__)


class SEOAnalyticsManager:
    """Gestionnaire des analytics SEO"""
    
    # KPIs cibles
    TARGET_KPIS = {
        "avg_position": 10.0,      # Position moyenne cible
        "ctr": 5.0,               # CTR cible (%)
        "seo_score": 80.0,        # Score SEO cible
        "indexed_rate": 95.0,     # Taux d'indexation cible (%)
        "conversion_rate": 2.0    # Taux de conversion cible (%)
    }
    
    # ============================================
    # DASHBOARD
    # ============================================
    
    @staticmethod
    async def get_dashboard_stats(db) -> dict:
        """Statistiques globales du dashboard SEO"""
        try:
            # Compter pages
            total_pages = await db.seo_pages.count_documents({})
            published_pages = await db.seo_pages.count_documents({"status": "published"})
            
            # Compter clusters
            total_clusters = await db.seo_clusters.count_documents({})
            
            # Score SEO moyen
            pipeline = [
                {"$match": {"seo_score": {"$gt": 0}}},
                {"$group": {"_id": None, "avg": {"$avg": "$seo_score"}}}
            ]
            avg_result = await db.seo_pages.aggregate(pipeline).to_list(1)
            avg_seo_score = avg_result[0]["avg"] if avg_result else 0
            
            # Trafic total (agrégé des pages)
            traffic_pipeline = [
                {"$group": {"_id": None, "total_clicks": {"$sum": "$clicks"}, "total_impressions": {"$sum": "$impressions"}}}
            ]
            traffic_result = await db.seo_pages.aggregate(traffic_pipeline).to_list(1)
            total_traffic = traffic_result[0] if traffic_result else {"total_clicks": 0, "total_impressions": 0}
            
            # CTR moyen
            avg_ctr = 0
            if total_traffic["total_impressions"] > 0:
                avg_ctr = (total_traffic["total_clicks"] / total_traffic["total_impressions"]) * 100
            
            # Position moyenne
            position_pipeline = [
                {"$match": {"avg_position": {"$gt": 0}}},
                {"$group": {"_id": None, "avg": {"$avg": "$avg_position"}}}
            ]
            pos_result = await db.seo_pages.aggregate(position_pipeline).to_list(1)
            avg_position = pos_result[0]["avg"] if pos_result else 0
            
            # Conversions totales
            conv_pipeline = [
                {"$group": {"_id": None, "total": {"$sum": "$conversions"}}}
            ]
            conv_result = await db.seo_pages.aggregate(conv_pipeline).to_list(1)
            total_conversions = conv_result[0]["total"] if conv_result else 0
            
            # Score de santé global
            health_score = SEOAnalyticsManager._calculate_health_score({
                "avg_position": avg_position,
                "avg_ctr": avg_ctr,
                "avg_seo_score": avg_seo_score,
                "published_rate": (published_pages / max(total_pages, 1)) * 100
            })
            
            # Compter schémas JSON-LD
            total_schemas = await db.seo_jsonld.count_documents({})
            
            return {
                "success": True,
                "stats": {
                    "clusters": {
                        "total": total_clusters + 9,  # +9 clusters de base
                        "active": total_clusters + 9
                    },
                    "pages": {
                        "total": total_pages,
                        "published": published_pages,
                        "draft": total_pages - published_pages
                    },
                    "traffic": {
                        "total_clicks": total_traffic["total_clicks"],
                        "total_impressions": total_traffic["total_impressions"],
                        "avg_ctr": round(avg_ctr, 2)
                    },
                    "performance": {
                        "avg_position": round(avg_position, 1),
                        "avg_seo_score": round(avg_seo_score, 1),
                        "total_conversions": total_conversions
                    },
                    "technical": {
                        "schemas_count": total_schemas,
                        "health_score": round(health_score, 1)
                    }
                },
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def _calculate_health_score(metrics: dict) -> float:
        """Calculer le score de santé global"""
        score = 100.0
        
        # Pénalité position (cible: < 10)
        if metrics.get("avg_position", 0) > 0:
            if metrics["avg_position"] > 20:
                score -= 30
            elif metrics["avg_position"] > 10:
                score -= 15
        
        # Pénalité CTR (cible: > 5%)
        if metrics.get("avg_ctr", 0) < 3:
            score -= 20
        elif metrics.get("avg_ctr", 0) < 5:
            score -= 10
        
        # Pénalité score SEO (cible: > 80)
        if metrics.get("avg_seo_score", 0) < 60:
            score -= 25
        elif metrics.get("avg_seo_score", 0) < 80:
            score -= 10
        
        # Pénalité taux publication
        if metrics.get("published_rate", 0) < 50:
            score -= 15
        elif metrics.get("published_rate", 0) < 80:
            score -= 5
        
        return max(0, min(100, score))
    
    # ============================================
    # TOP PERFORMERS
    # ============================================
    
    @staticmethod
    async def get_top_pages(db, metric: str = "clicks", limit: int = 10) -> dict:
        """Récupérer les pages les plus performantes"""
        try:
            sort_field = f"-{metric}" if metric in ["clicks", "impressions", "conversions", "seo_score"] else "-clicks"
            
            pages = await db.seo_pages.find(
                {"status": "published"},
                {"_id": 0, "id": 1, "title_fr": 1, "slug": 1, "clicks": 1, "impressions": 1, 
                 "ctr": 1, "avg_position": 1, "seo_score": 1, "conversions": 1}
            ).sort(metric, -1).limit(limit).to_list(limit)
            
            return {
                "success": True,
                "metric": metric,
                "pages": pages
            }
        except Exception as e:
            logger.error(f"Error getting top pages: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def get_top_clusters(db, limit: int = 10) -> dict:
        """Récupérer les clusters les plus performants"""
        try:
            # Agréger performance par cluster
            pipeline = [
                {"$group": {
                    "_id": "$cluster_id",
                    "total_pages": {"$sum": 1},
                    "total_clicks": {"$sum": "$clicks"},
                    "total_impressions": {"$sum": "$impressions"},
                    "avg_seo_score": {"$avg": "$seo_score"}
                }},
                {"$sort": {"total_clicks": -1}},
                {"$limit": limit}
            ]
            
            results = await db.seo_pages.aggregate(pipeline).to_list(limit)
            
            return {
                "success": True,
                "clusters": results
            }
        except Exception as e:
            logger.error(f"Error getting top clusters: {e}")
            return {"success": False, "error": str(e)}
    
    # ============================================
    # TRENDS
    # ============================================
    
    @staticmethod
    async def get_traffic_trend(db, days: int = 30) -> dict:
        """Récupérer la tendance du trafic"""
        try:
            # Simulé pour l'instant - à connecter avec Google Search Console
            trend = []
            base_clicks = 100
            
            for i in range(days):
                date = datetime.now(timezone.utc) - timedelta(days=days - i - 1)
                # Simulation avec variation
                variation = 1 + (i / days) * 0.3  # Croissance de 30%
                trend.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "clicks": int(base_clicks * variation * (0.9 + 0.2 * (i % 7) / 7)),
                    "impressions": int(base_clicks * variation * 20)
                })
            
            return {
                "success": True,
                "period_days": days,
                "trend": trend
            }
        except Exception as e:
            logger.error(f"Error getting traffic trend: {e}")
            return {"success": False, "error": str(e)}
    
    # ============================================
    # OPPORTUNITIES
    # ============================================
    
    @staticmethod
    async def get_optimization_opportunities(db) -> dict:
        """Identifier les opportunités d'optimisation"""
        try:
            opportunities = []
            
            # Pages avec bon trafic mais mauvais CTR
            low_ctr_pages = await db.seo_pages.find(
                {"impressions": {"$gt": 100}, "ctr": {"$lt": 3}},
                {"_id": 0, "id": 1, "title_fr": 1, "impressions": 1, "ctr": 1}
            ).limit(5).to_list(5)
            
            for page in low_ctr_pages:
                opportunities.append({
                    "type": "low_ctr",
                    "priority": "high",
                    "page_id": page["id"],
                    "title": page.get("title_fr", ""),
                    "message": f"CTR faible ({page['ctr']}%) malgré {page['impressions']} impressions - Optimiser titre et meta description",
                    "potential_gain": "+50% clicks estimé"
                })
            
            # Pages avec mauvais score SEO
            low_seo_pages = await db.seo_pages.find(
                {"seo_score": {"$lt": 60}, "status": "published"},
                {"_id": 0, "id": 1, "title_fr": 1, "seo_score": 1}
            ).limit(5).to_list(5)
            
            for page in low_seo_pages:
                opportunities.append({
                    "type": "low_seo_score",
                    "priority": "medium",
                    "page_id": page["id"],
                    "title": page.get("title_fr", ""),
                    "message": f"Score SEO faible ({page['seo_score']}) - Optimiser le contenu",
                    "potential_gain": "Meilleur classement"
                })
            
            # Pages en position 11-20 (page 2)
            page2_pages = await db.seo_pages.find(
                {"avg_position": {"$gt": 10, "$lt": 20}},
                {"_id": 0, "id": 1, "title_fr": 1, "avg_position": 1}
            ).limit(5).to_list(5)
            
            for page in page2_pages:
                opportunities.append({
                    "type": "page_2_ranking",
                    "priority": "high",
                    "page_id": page["id"],
                    "title": page.get("title_fr", ""),
                    "message": f"Position {page['avg_position']:.0f} - Proche de la page 1!",
                    "potential_gain": "+200% trafic estimé si page 1"
                })
            
            return {
                "success": True,
                "total": len(opportunities),
                "opportunities": opportunities
            }
        except Exception as e:
            logger.error(f"Error getting opportunities: {e}")
            return {"success": False, "error": str(e)}
    
    # ============================================
    # REPORTING
    # ============================================
    
    @staticmethod
    async def generate_report(db, period: str = "monthly") -> dict:
        """Générer un rapport SEO"""
        try:
            dashboard = await SEOAnalyticsManager.get_dashboard_stats(db)
            top_pages = await SEOAnalyticsManager.get_top_pages(db, "clicks", 10)
            top_clusters = await SEOAnalyticsManager.get_top_clusters(db, 5)
            opportunities = await SEOAnalyticsManager.get_optimization_opportunities(db)
            
            report = {
                "report_type": "seo_performance",
                "period": period,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "summary": {
                    "total_pages": dashboard.get("stats", {}).get("pages", {}).get("total", 0),
                    "total_clicks": dashboard.get("stats", {}).get("traffic", {}).get("total_clicks", 0),
                    "avg_position": dashboard.get("stats", {}).get("performance", {}).get("avg_position", 0),
                    "health_score": dashboard.get("stats", {}).get("technical", {}).get("health_score", 0)
                },
                "top_performers": {
                    "pages": top_pages.get("pages", [])[:5],
                    "clusters": top_clusters.get("clusters", [])[:3]
                },
                "action_items": opportunities.get("opportunities", [])[:5],
                "recommendations": [
                    "Optimiser les pages en position 11-20 pour atteindre la page 1",
                    "Améliorer les meta descriptions des pages à faible CTR",
                    "Ajouter du contenu aux pages avec score SEO < 60",
                    "Créer des liens internes vers les nouvelles pages"
                ]
            }
            
            return {
                "success": True,
                "report": report
            }
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return {"success": False, "error": str(e)}


logger.info("SEOAnalyticsManager initialized - V5 LEGO Module")
