"""
BIONIC SEO Pages - V5-ULTIME
============================

Gestion des pages SEO:
- Pages piliers (contenu approfondi)
- Pages satellites (sous-sujets)
- Pages opportunités (longue traîne)
- Capsules virales (contenu partageable)
- Guides interactifs
- Outils/widgets

Module isolé - aucun import croisé.
"""

from datetime import datetime, timezone
import logging
import uuid

logger = logging.getLogger(__name__)


class SEOPagesManager:
    """Gestionnaire des pages SEO"""
    
    # Templates de pages piliers
    PILLAR_TEMPLATES = {
        "species_guide": {
            "id": "tpl_species_guide",
            "name": "Species Hunting Guide",
            "name_fr": "Guide Complet Chasse par Espèce",
            "page_type": "pillar",
            "content_format": "guide",
            "structure": {
                "sections": [
                    {"h2": "Introduction et présentation de l'espèce", "word_count": 300},
                    {"h2": "Comportement et habitat", "word_count": 500},
                    {"h2": "Réglementation et saisons de chasse", "word_count": 400},
                    {"h2": "Techniques de chasse recommandées", "word_count": 600},
                    {"h2": "Équipement essentiel", "word_count": 400},
                    {"h2": "Meilleures régions au Québec", "word_count": 500},
                    {"h2": "Conseils d'experts", "word_count": 300},
                    {"h2": "FAQ", "word_count": 400}
                ],
                "total_word_count": 3400,
                "reading_time_min": 15
            },
            "jsonld_types": ["Article", "HowTo", "FAQPage"],
            "internal_links_target": 8
        },
        "region_guide": {
            "id": "tpl_region_guide",
            "name": "Regional Hunting Guide",
            "name_fr": "Guide Chasse par Région",
            "page_type": "pillar",
            "content_format": "guide",
            "structure": {
                "sections": [
                    {"h2": "Présentation de la région", "word_count": 300},
                    {"h2": "Gibier disponible", "word_count": 400},
                    {"h2": "Zones de chasse (ZEC, pourvoiries)", "word_count": 500},
                    {"h2": "Accès et hébergement", "word_count": 300},
                    {"h2": "Meilleurs spots recommandés", "word_count": 500},
                    {"h2": "Calendrier optimal", "word_count": 300},
                    {"h2": "Conseils locaux", "word_count": 300}
                ],
                "total_word_count": 2600,
                "reading_time_min": 12
            },
            "jsonld_types": ["Article", "LocalBusiness"],
            "internal_links_target": 6
        },
        "technique_guide": {
            "id": "tpl_technique_guide",
            "name": "Hunting Technique Guide",
            "name_fr": "Guide Technique de Chasse",
            "page_type": "pillar",
            "content_format": "guide",
            "structure": {
                "sections": [
                    {"h2": "Introduction à la technique", "word_count": 200},
                    {"h2": "Équipement nécessaire", "word_count": 300},
                    {"h2": "Guide étape par étape", "word_count": 600},
                    {"h2": "Erreurs courantes à éviter", "word_count": 300},
                    {"h2": "Conseils avancés", "word_count": 400},
                    {"h2": "Vidéos et démonstrations", "word_count": 200}
                ],
                "total_word_count": 2000,
                "reading_time_min": 10
            },
            "jsonld_types": ["Article", "HowTo"],
            "internal_links_target": 5
        }
    }
    
    # Templates de pages satellites
    SATELLITE_TEMPLATES = {
        "species_behavior": {
            "id": "tpl_species_behavior",
            "name": "Species Behavior Article",
            "name_fr": "Article Comportement Espèce",
            "page_type": "satellite",
            "content_format": "article",
            "structure": {
                "sections": [
                    {"h2": "Comportement général", "word_count": 300},
                    {"h2": "Patterns d'activité", "word_count": 400},
                    {"h2": "Impact sur la chasse", "word_count": 300}
                ],
                "total_word_count": 1000,
                "reading_time_min": 5
            },
            "jsonld_types": ["Article"],
            "internal_links_target": 3
        },
        "seasonal_tips": {
            "id": "tpl_seasonal_tips",
            "name": "Seasonal Hunting Tips",
            "name_fr": "Conseils Chasse Saisonniers",
            "page_type": "satellite",
            "content_format": "article",
            "structure": {
                "sections": [
                    {"h2": "Conditions de la saison", "word_count": 200},
                    {"h2": "Adaptations nécessaires", "word_count": 300},
                    {"h2": "Stratégies gagnantes", "word_count": 400},
                    {"h2": "Checklist équipement", "word_count": 200}
                ],
                "total_word_count": 1100,
                "reading_time_min": 5
            },
            "jsonld_types": ["Article", "HowTo"],
            "internal_links_target": 4
        }
    }
    
    # Templates d'opportunités (longue traîne)
    OPPORTUNITY_TEMPLATES = {
        "specific_question": {
            "id": "tpl_specific_question",
            "name": "Specific Question Answer",
            "name_fr": "Réponse Question Spécifique",
            "page_type": "opportunity",
            "content_format": "article",
            "structure": {
                "sections": [
                    {"h2": "Réponse directe", "word_count": 150},
                    {"h2": "Explication détaillée", "word_count": 300},
                    {"h2": "Conseils pratiques", "word_count": 200}
                ],
                "total_word_count": 650,
                "reading_time_min": 3
            },
            "jsonld_types": ["Article", "FAQPage"],
            "internal_links_target": 2
        },
        "location_specific": {
            "id": "tpl_location_specific",
            "name": "Location-Specific Guide",
            "name_fr": "Guide Lieu Spécifique",
            "page_type": "opportunity",
            "content_format": "article",
            "structure": {
                "sections": [
                    {"h2": "À propos du lieu", "word_count": 200},
                    {"h2": "Espèces présentes", "word_count": 200},
                    {"h2": "Meilleur moment", "word_count": 150},
                    {"h2": "Accès et contact", "word_count": 150}
                ],
                "total_word_count": 700,
                "reading_time_min": 3
            },
            "jsonld_types": ["Article", "LocalBusiness"],
            "internal_links_target": 3
        }
    }
    
    # ============================================
    # CRUD OPERATIONS
    # ============================================
    
    @staticmethod
    async def get_all_pages(db, cluster_id: str = None, page_type: str = None, 
                           status: str = None, limit: int = 100) -> dict:
        """Récupérer toutes les pages"""
        try:
            query = {}
            if cluster_id:
                query["cluster_id"] = cluster_id
            if page_type:
                query["page_type"] = page_type
            if status:
                query["status"] = status
            
            pages = await db.seo_pages.find(query, {"_id": 0}).limit(limit).to_list(limit)
            
            return {
                "success": True,
                "total": len(pages),
                "pages": pages
            }
        except Exception as e:
            logger.error(f"Error getting pages: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def get_page_by_id(db, page_id: str) -> dict:
        """Récupérer une page par ID"""
        try:
            page = await db.seo_pages.find_one({"id": page_id}, {"_id": 0})
            if page:
                return {"success": True, "page": page}
            return {"success": False, "error": "Page non trouvée"}
        except Exception as e:
            logger.error(f"Error getting page: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def create_page(db, page_data: dict) -> dict:
        """Créer une nouvelle page"""
        try:
            page = {
                "id": page_data.get("id", f"page_{uuid.uuid4().hex[:8]}"),
                "cluster_id": page_data.get("cluster_id"),
                "page_type": page_data.get("page_type", "satellite"),
                "status": page_data.get("status", "draft"),
                "slug": page_data.get("slug", ""),
                "url_path": page_data.get("url_path", ""),
                "title": page_data.get("title", ""),
                "title_fr": page_data.get("title_fr", ""),
                "meta_description": page_data.get("meta_description", ""),
                "meta_description_fr": page_data.get("meta_description_fr", ""),
                "content_format": page_data.get("content_format", "article"),
                "h1": page_data.get("h1", ""),
                "h2_list": page_data.get("h2_list", []),
                "word_count": page_data.get("word_count", 0),
                "reading_time_min": page_data.get("reading_time_min", 0),
                "primary_keyword": page_data.get("primary_keyword", ""),
                "secondary_keywords": page_data.get("secondary_keywords", []),
                "keyword_density": page_data.get("keyword_density", 0.0),
                "seo_score": page_data.get("seo_score", 0.0),
                "internal_links_out": page_data.get("internal_links_out", []),
                "internal_links_in": page_data.get("internal_links_in", []),
                "jsonld_types": page_data.get("jsonld_types", []),
                "jsonld_data": page_data.get("jsonld_data", {}),
                "target_audience": page_data.get("target_audience", "all"),
                "target_regions": page_data.get("target_regions", []),
                "target_seasons": page_data.get("target_seasons", []),
                "target_species": page_data.get("target_species", []),
                "knowledge_rules_applied": page_data.get("knowledge_rules_applied", []),
                "knowledge_data_used": page_data.get("knowledge_data_used", {}),
                "impressions": 0,
                "clicks": 0,
                "ctr": 0.0,
                "avg_position": 0.0,
                "conversions": 0,
                "author": page_data.get("author", "BIONIC"),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "published_at": None,
                "scheduled_at": None
            }
            
            await db.seo_pages.insert_one(page)
            page.pop("_id", None)
            
            return {"success": True, "page": page}
        except Exception as e:
            logger.error(f"Error creating page: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def update_page(db, page_id: str, updates: dict) -> dict:
        """Mettre à jour une page"""
        try:
            protected = ["id", "created_at"]
            for field in protected:
                updates.pop(field, None)
            
            updates["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            result = await db.seo_pages.update_one(
                {"id": page_id},
                {"$set": updates}
            )
            
            if result.matched_count == 0:
                return {"success": False, "error": "Page non trouvée"}
            
            return {"success": True, "message": "Page mise à jour"}
        except Exception as e:
            logger.error(f"Error updating page: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def publish_page(db, page_id: str) -> dict:
        """Publier une page"""
        try:
            result = await db.seo_pages.update_one(
                {"id": page_id},
                {"$set": {
                    "status": "published",
                    "published_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            
            if result.matched_count == 0:
                return {"success": False, "error": "Page non trouvée"}
            
            return {"success": True, "message": "Page publiée"}
        except Exception as e:
            logger.error(f"Error publishing page: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def delete_page(db, page_id: str) -> dict:
        """Supprimer une page"""
        try:
            result = await db.seo_pages.delete_one({"id": page_id})
            
            if result.deleted_count == 0:
                return {"success": False, "error": "Page non trouvée"}
            
            return {"success": True, "message": "Page supprimée"}
        except Exception as e:
            logger.error(f"Error deleting page: {e}")
            return {"success": False, "error": str(e)}
    
    # ============================================
    # TEMPLATES
    # ============================================
    
    @staticmethod
    def get_all_templates() -> dict:
        """Récupérer tous les templates"""
        return {
            "success": True,
            "templates": {
                "pillar": list(SEOPagesManager.PILLAR_TEMPLATES.values()),
                "satellite": list(SEOPagesManager.SATELLITE_TEMPLATES.values()),
                "opportunity": list(SEOPagesManager.OPPORTUNITY_TEMPLATES.values())
            }
        }
    
    @staticmethod
    def get_template_by_id(template_id: str) -> dict:
        """Récupérer un template par ID"""
        all_templates = {
            **SEOPagesManager.PILLAR_TEMPLATES,
            **SEOPagesManager.SATELLITE_TEMPLATES,
            **SEOPagesManager.OPPORTUNITY_TEMPLATES
        }
        
        if template_id in all_templates:
            return {"success": True, "template": all_templates[template_id]}
        
        return {"success": False, "error": "Template non trouvé"}
    
    # ============================================
    # INTERNAL LINKING
    # ============================================
    
    @staticmethod
    async def calculate_internal_links(db, page_id: str) -> dict:
        """Calculer les liens internes recommandés pour une page"""
        try:
            page = await db.seo_pages.find_one({"id": page_id}, {"_id": 0})
            if not page:
                return {"success": False, "error": "Page non trouvée"}
            
            cluster_id = page.get("cluster_id")
            target_species = page.get("target_species", [])
            target_regions = page.get("target_regions", [])
            
            # Trouver pages liées
            related_query = {
                "$and": [
                    {"id": {"$ne": page_id}},
                    {"status": "published"},
                    {"$or": [
                        {"cluster_id": cluster_id},
                        {"target_species": {"$in": target_species}},
                        {"target_regions": {"$in": target_regions}}
                    ]}
                ]
            }
            
            related_pages = await db.seo_pages.find(
                related_query, {"_id": 0, "id": 1, "title_fr": 1, "slug": 1, "page_type": 1}
            ).limit(10).to_list(10)
            
            # Générer suggestions de liens
            suggestions = []
            for rp in related_pages:
                suggestions.append({
                    "target_page_id": rp["id"],
                    "anchor_text_fr": rp.get("title_fr", ""),
                    "link_type": "related" if rp.get("page_type") == page.get("page_type") else "contextual",
                    "priority": 3 if rp.get("cluster_id") == cluster_id else 2
                })
            
            return {
                "success": True,
                "page_id": page_id,
                "suggestions": suggestions
            }
        except Exception as e:
            logger.error(f"Error calculating internal links: {e}")
            return {"success": False, "error": str(e)}
    
    # ============================================
    # STATISTICS
    # ============================================
    
    @staticmethod
    async def get_pages_stats(db) -> dict:
        """Statistiques des pages"""
        try:
            total = await db.seo_pages.count_documents({})
            published = await db.seo_pages.count_documents({"status": "published"})
            draft = await db.seo_pages.count_documents({"status": "draft"})
            
            # Par type
            by_type = {}
            for ptype in ["pillar", "satellite", "opportunity", "viral", "interactive", "tool"]:
                count = await db.seo_pages.count_documents({"page_type": ptype})
                by_type[ptype] = count
            
            # Score SEO moyen
            pipeline = [
                {"$match": {"seo_score": {"$gt": 0}}},
                {"$group": {"_id": None, "avg_score": {"$avg": "$seo_score"}}}
            ]
            avg_result = await db.seo_pages.aggregate(pipeline).to_list(1)
            avg_seo_score = avg_result[0]["avg_score"] if avg_result else 0
            
            return {
                "success": True,
                "stats": {
                    "total": total,
                    "published": published,
                    "draft": draft,
                    "by_type": by_type,
                    "avg_seo_score": round(avg_seo_score, 1)
                }
            }
        except Exception as e:
            logger.error(f"Error getting pages stats: {e}")
            return {"success": False, "error": str(e)}


logger.info("SEOPagesManager initialized - V5 LEGO Module")
