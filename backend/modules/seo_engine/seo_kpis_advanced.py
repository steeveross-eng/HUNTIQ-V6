"""
BIONIC SEO KPIs Avancés - V5-ULTIME
====================================

KPIs avancés pour scoring complet du système SEO.

KPIs Implémentés:
- Score conformité Québec
- Score conformité internationale
- Score duplication
- Score complétude cluster
- Score complétude page
- Score maillage interne

Module isolé - Architecture LEGO V5.
"""

from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class SEOAdvancedKPIs:
    """KPIs avancés pour le SEO Engine"""
    
    # ============================================
    # DÉFINITIONS KPIs
    # ============================================
    
    KPI_DEFINITIONS = {
        "quebec_compliance_score": {
            "id": "kpi_quebec_compliance",
            "name": "Score Conformité Québec",
            "name_fr": "Score Conformité Québec",
            "description": "Mesure la conformité aux règles québécoises (Loi 96, MFFP, SEPAQ)",
            "category": "compliance",
            "target": 95.0,
            "warning_threshold": 80.0,
            "critical_threshold": 60.0,
            "unit": "%",
            "calculation": "weighted_average",
            "weight": 1.5
        },
        "international_compliance_score": {
            "id": "kpi_international_compliance",
            "name": "Score Conformité Internationale",
            "name_fr": "Score Conformité Internationale",
            "description": "Mesure la conformité aux règles des marchés internationaux",
            "category": "compliance",
            "target": 90.0,
            "warning_threshold": 75.0,
            "critical_threshold": 50.0,
            "unit": "%",
            "calculation": "weighted_average",
            "weight": 1.0
        },
        "duplication_score": {
            "id": "kpi_duplication",
            "name": "Score Anti-Duplication",
            "name_fr": "Score Anti-Duplication",
            "description": "Mesure l'absence de contenu dupliqué (100 = zéro doublon)",
            "category": "quality",
            "target": 100.0,
            "warning_threshold": 95.0,
            "critical_threshold": 85.0,
            "unit": "%",
            "calculation": "inverse_count",
            "weight": 2.0
        },
        "cluster_completeness_score": {
            "id": "kpi_cluster_completeness",
            "name": "Score Complétude Cluster",
            "name_fr": "Score Complétude Cluster",
            "description": "Mesure si chaque cluster a ses pages pilier, satellites et opportunités",
            "category": "content",
            "target": 100.0,
            "warning_threshold": 80.0,
            "critical_threshold": 50.0,
            "unit": "%",
            "calculation": "cluster_structure",
            "weight": 1.5,
            "requirements": {
                "pillar_required": 1,
                "satellites_required": 5,
                "opportunities_required": 10
            }
        },
        "page_completeness_score": {
            "id": "kpi_page_completeness",
            "name": "Score Complétude Page",
            "name_fr": "Score Complétude Page",
            "description": "Mesure si chaque page a tous les éléments requis",
            "category": "content",
            "target": 95.0,
            "warning_threshold": 80.0,
            "critical_threshold": 60.0,
            "unit": "%",
            "calculation": "field_presence",
            "weight": 1.5,
            "required_fields": [
                "title_fr", "meta_description_fr", "h1", "h2_list",
                "primary_keyword", "word_count", "jsonld_types"
            ],
            "recommended_fields": [
                "secondary_keywords", "internal_links_out", "faq_items",
                "cta", "target_audience"
            ]
        },
        "internal_linking_score": {
            "id": "kpi_internal_linking",
            "name": "Score Maillage Interne",
            "name_fr": "Score Maillage Interne",
            "description": "Mesure la qualité du maillage interne (min 8 liens bidirectionnels)",
            "category": "seo",
            "target": 100.0,
            "warning_threshold": 80.0,
            "critical_threshold": 50.0,
            "unit": "%",
            "calculation": "link_analysis",
            "weight": 2.0,
            "requirements": {
                "min_outbound_links": 8,
                "min_inbound_links": 3,
                "orphan_pages_allowed": 0
            }
        }
    }
    
    # ============================================
    # CALCUL DES KPIs
    # ============================================
    
    @staticmethod
    async def calculate_quebec_compliance(db) -> dict:
        """Calculer le score de conformité Québec"""
        try:
            total_pages = await db.seo_pages.count_documents({})
            if total_pages == 0:
                return {"score": 100.0, "details": "Aucune page à évaluer"}
            
            # Vérifier pages avec titre français
            pages_with_fr_title = await db.seo_pages.count_documents({"title_fr": {"$exists": True, "$ne": ""}})
            
            # Vérifier pages avec meta français
            pages_with_fr_meta = await db.seo_pages.count_documents({"meta_description_fr": {"$exists": True, "$ne": ""}})
            
            # Score pondéré
            title_score = (pages_with_fr_title / total_pages) * 100
            meta_score = (pages_with_fr_meta / total_pages) * 100
            
            final_score = (title_score * 0.4 + meta_score * 0.4 + 100 * 0.2)  # 20% pour autres critères
            
            return {
                "score": round(final_score, 2),
                "details": {
                    "total_pages": total_pages,
                    "pages_with_fr_title": pages_with_fr_title,
                    "pages_with_fr_meta": pages_with_fr_meta,
                    "title_compliance": round(title_score, 2),
                    "meta_compliance": round(meta_score, 2)
                },
                "status": "OK" if final_score >= 95 else ("WARNING" if final_score >= 80 else "CRITICAL")
            }
        except Exception as e:
            logger.error(f"Error calculating Quebec compliance: {e}")
            return {"score": 0, "error": str(e)}
    
    @staticmethod
    async def calculate_international_compliance(db) -> dict:
        """Calculer le score de conformité internationale"""
        try:
            # Pour l'instant, basé sur la présence de hreflang et market targeting
            total_pages = await db.seo_pages.count_documents({})
            if total_pages == 0:
                return {"score": 100.0, "details": "Aucune page à évaluer"}
            
            # Pages avec target_market défini
            pages_with_market = await db.seo_pages.count_documents({"target_market": {"$exists": True}})
            
            score = (pages_with_market / total_pages) * 100 if total_pages > 0 else 100
            
            return {
                "score": round(score, 2),
                "details": {
                    "total_pages": total_pages,
                    "pages_with_market": pages_with_market
                },
                "status": "OK" if score >= 90 else ("WARNING" if score >= 75 else "CRITICAL")
            }
        except Exception as e:
            logger.error(f"Error calculating international compliance: {e}")
            return {"score": 0, "error": str(e)}
    
    @staticmethod
    async def calculate_duplication_score(db) -> dict:
        """Calculer le score anti-duplication"""
        try:
            total_pages = await db.seo_pages.count_documents({})
            if total_pages == 0:
                return {"score": 100.0, "details": "Aucune page à évaluer"}
            
            # Compter les doublons de titres
            pipeline = [
                {"$group": {"_id": "$title_fr", "count": {"$sum": 1}}},
                {"$match": {"count": {"$gt": 1}}}
            ]
            title_duplicates = await db.seo_pages.aggregate(pipeline).to_list(100)
            duplicate_titles = sum(d["count"] - 1 for d in title_duplicates)
            
            # Compter les doublons de slugs
            pipeline = [
                {"$group": {"_id": "$slug", "count": {"$sum": 1}}},
                {"$match": {"count": {"$gt": 1}}}
            ]
            slug_duplicates = await db.seo_pages.aggregate(pipeline).to_list(100)
            duplicate_slugs = sum(d["count"] - 1 for d in slug_duplicates)
            
            # Compter les cannibalisations de mots-clés
            pipeline = [
                {"$group": {"_id": "$primary_keyword", "count": {"$sum": 1}}},
                {"$match": {"count": {"$gt": 1}, "_id": {"$ne": None, "$ne": ""}}}
            ]
            keyword_cannibalization = await db.seo_pages.aggregate(pipeline).to_list(100)
            cannibalized = sum(d["count"] - 1 for d in keyword_cannibalization)
            
            total_issues = duplicate_titles + duplicate_slugs + cannibalized
            score = max(0, 100 - (total_issues / max(total_pages, 1)) * 100)
            
            return {
                "score": round(score, 2),
                "details": {
                    "total_pages": total_pages,
                    "duplicate_titles": duplicate_titles,
                    "duplicate_slugs": duplicate_slugs,
                    "keyword_cannibalization": cannibalized,
                    "total_issues": total_issues
                },
                "status": "OK" if score >= 100 else ("WARNING" if score >= 95 else "CRITICAL")
            }
        except Exception as e:
            logger.error(f"Error calculating duplication score: {e}")
            return {"score": 0, "error": str(e)}
    
    @staticmethod
    async def calculate_cluster_completeness(db) -> dict:
        """Calculer le score de complétude des clusters"""
        try:
            # Récupérer tous les clusters
            clusters = await db.seo_clusters.find({}, {"_id": 0}).to_list(100)
            
            # Ajouter les 9 clusters de base
            from .seo_clusters import SEOClustersManager
            base_clusters = list(SEOClustersManager.BASE_CLUSTERS.values())
            
            all_clusters = clusters + base_clusters
            
            if len(all_clusters) == 0:
                return {"score": 0, "details": "Aucun cluster défini"}
            
            cluster_scores = []
            incomplete_clusters = []
            
            for cluster in all_clusters:
                cluster_id = cluster.get("id")
                
                # Compter pages par type
                pillar_count = await db.seo_pages.count_documents({
                    "cluster_id": cluster_id, "page_type": "pillar"
                })
                satellite_count = await db.seo_pages.count_documents({
                    "cluster_id": cluster_id, "page_type": "satellite"
                })
                opportunity_count = await db.seo_pages.count_documents({
                    "cluster_id": cluster_id, "page_type": "opportunity"
                })
                
                # Calculer score cluster
                pillar_score = min(100, pillar_count * 100)  # 1 pillar = 100%
                satellite_score = min(100, (satellite_count / 5) * 100)  # 5 satellites = 100%
                opportunity_score = min(100, (opportunity_count / 10) * 100)  # 10 opportunities = 100%
                
                cluster_score = (pillar_score * 0.4 + satellite_score * 0.35 + opportunity_score * 0.25)
                cluster_scores.append(cluster_score)
                
                if cluster_score < 100:
                    incomplete_clusters.append({
                        "cluster_id": cluster_id,
                        "name_fr": cluster.get("name_fr", cluster.get("name")),
                        "score": round(cluster_score, 2),
                        "pillars": pillar_count,
                        "satellites": satellite_count,
                        "opportunities": opportunity_count
                    })
            
            avg_score = sum(cluster_scores) / len(cluster_scores) if cluster_scores else 0
            
            return {
                "score": round(avg_score, 2),
                "details": {
                    "total_clusters": len(all_clusters),
                    "complete_clusters": len([s for s in cluster_scores if s >= 100]),
                    "incomplete_clusters": incomplete_clusters[:10]  # Top 10 incomplets
                },
                "status": "OK" if avg_score >= 100 else ("WARNING" if avg_score >= 80 else "CRITICAL")
            }
        except Exception as e:
            logger.error(f"Error calculating cluster completeness: {e}")
            return {"score": 0, "error": str(e)}
    
    @staticmethod
    async def calculate_page_completeness(db) -> dict:
        """Calculer le score de complétude des pages"""
        try:
            total_pages = await db.seo_pages.count_documents({})
            if total_pages == 0:
                return {"score": 100.0, "details": "Aucune page à évaluer"}
            
            required_fields = [
                "title_fr", "meta_description_fr", "h1", "primary_keyword"
            ]
            
            scores = []
            incomplete_pages = []
            
            async for page in db.seo_pages.find({}, {"_id": 0}):
                page_score = 0
                missing_fields = []
                
                # Required fields (60% du score)
                for field in required_fields:
                    if page.get(field):
                        page_score += 15
                    else:
                        missing_fields.append(field)
                
                # H2 list (15%)
                h2_list = page.get("h2_list", [])
                if len(h2_list) >= 3:
                    page_score += 15
                else:
                    missing_fields.append(f"h2_list (need 3, have {len(h2_list)})")
                
                # Word count (15%)
                word_count = page.get("word_count", 0)
                min_words = {"pillar": 2000, "satellite": 800, "opportunity": 400}.get(
                    page.get("page_type", "satellite"), 800
                )
                if word_count >= min_words:
                    page_score += 15
                else:
                    missing_fields.append(f"word_count (need {min_words}, have {word_count})")
                
                # JSON-LD (10%)
                if page.get("jsonld_types"):
                    page_score += 10
                else:
                    missing_fields.append("jsonld_types")
                
                scores.append(page_score)
                
                if page_score < 100:
                    incomplete_pages.append({
                        "page_id": page.get("id"),
                        "title": page.get("title_fr", "")[:50],
                        "score": page_score,
                        "missing": missing_fields
                    })
            
            avg_score = sum(scores) / len(scores) if scores else 0
            
            return {
                "score": round(avg_score, 2),
                "details": {
                    "total_pages": total_pages,
                    "complete_pages": len([s for s in scores if s >= 100]),
                    "incomplete_pages": incomplete_pages[:10]
                },
                "status": "OK" if avg_score >= 95 else ("WARNING" if avg_score >= 80 else "CRITICAL")
            }
        except Exception as e:
            logger.error(f"Error calculating page completeness: {e}")
            return {"score": 0, "error": str(e)}
    
    @staticmethod
    async def calculate_internal_linking(db) -> dict:
        """Calculer le score de maillage interne"""
        try:
            total_pages = await db.seo_pages.count_documents({})
            if total_pages == 0:
                return {"score": 100.0, "details": "Aucune page à évaluer"}
            
            # Pages avec assez de liens sortants
            pages_with_enough_outbound = await db.seo_pages.count_documents({
                "internal_links_out.7": {"$exists": True}  # Au moins 8 liens
            })
            
            # Pages avec liens entrants
            pages_with_inbound = await db.seo_pages.count_documents({
                "internal_links_in.0": {"$exists": True}  # Au moins 1 lien entrant
            })
            
            # Pages orphelines (sans liens entrants ni sortants)
            orphan_pages = await db.seo_pages.count_documents({
                "$and": [
                    {"$or": [{"internal_links_out": []}, {"internal_links_out": {"$exists": False}}]},
                    {"$or": [{"internal_links_in": []}, {"internal_links_in": {"$exists": False}}]}
                ]
            })
            
            outbound_score = (pages_with_enough_outbound / total_pages) * 100 if total_pages > 0 else 0
            inbound_score = (pages_with_inbound / total_pages) * 100 if total_pages > 0 else 0
            orphan_penalty = (orphan_pages / total_pages) * 50 if total_pages > 0 else 0
            
            final_score = max(0, (outbound_score * 0.5 + inbound_score * 0.3 + 100 * 0.2) - orphan_penalty)
            
            return {
                "score": round(final_score, 2),
                "details": {
                    "total_pages": total_pages,
                    "pages_with_8_outbound": pages_with_enough_outbound,
                    "pages_with_inbound": pages_with_inbound,
                    "orphan_pages": orphan_pages,
                    "outbound_score": round(outbound_score, 2),
                    "inbound_score": round(inbound_score, 2)
                },
                "status": "OK" if final_score >= 100 else ("WARNING" if final_score >= 80 else "CRITICAL")
            }
        except Exception as e:
            logger.error(f"Error calculating internal linking: {e}")
            return {"score": 0, "error": str(e)}
    
    @staticmethod
    async def get_all_kpis(db) -> dict:
        """Calculer tous les KPIs"""
        try:
            kpis = {
                "quebec_compliance": await SEOAdvancedKPIs.calculate_quebec_compliance(db),
                "international_compliance": await SEOAdvancedKPIs.calculate_international_compliance(db),
                "duplication": await SEOAdvancedKPIs.calculate_duplication_score(db),
                "cluster_completeness": await SEOAdvancedKPIs.calculate_cluster_completeness(db),
                "page_completeness": await SEOAdvancedKPIs.calculate_page_completeness(db),
                "internal_linking": await SEOAdvancedKPIs.calculate_internal_linking(db)
            }
            
            # Score global pondéré
            weights = {
                "quebec_compliance": 1.5,
                "international_compliance": 1.0,
                "duplication": 2.0,
                "cluster_completeness": 1.5,
                "page_completeness": 1.5,
                "internal_linking": 2.0
            }
            
            total_weight = sum(weights.values())
            weighted_sum = sum(
                kpis[k].get("score", 0) * weights[k] 
                for k in weights.keys()
            )
            global_score = weighted_sum / total_weight if total_weight > 0 else 0
            
            return {
                "success": True,
                "kpis": kpis,
                "global_score": round(global_score, 2),
                "global_status": "OK" if global_score >= 90 else ("WARNING" if global_score >= 70 else "CRITICAL"),
                "calculated_at": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting all KPIs: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def get_kpi_definitions() -> dict:
        """Retourner les définitions des KPIs"""
        return SEOAdvancedKPIs.KPI_DEFINITIONS


logger.info("SEOAdvancedKPIs initialized - V5 LEGO Module with 6 Advanced KPIs")
