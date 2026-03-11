"""
BIONIC SEO JSON-LD - V5-ULTIME
==============================

Gestion des schémas JSON-LD pour le SEO structuré.
Types supportés:
- Article
- HowTo
- FAQPage
- LocalBusiness
- Product
- Event
- Organization
- BreadcrumbList
- VideoObject

Module isolé - aucun import croisé.
"""

from datetime import datetime, timezone
from typing import List
import logging
import json
import uuid

logger = logging.getLogger(__name__)


class SEOJsonLDManager:
    """Gestionnaire des schémas JSON-LD"""
    
    # Schéma de base pour l'organisation BIONIC
    ORGANIZATION_SCHEMA = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "BIONIC - Chasse Bionic",
        "alternateName": "Bionic Hunt",
        "url": "https://chassebionic.com",
        "logo": "https://chassebionic.com/logo.png",
        "description": "Plateforme intelligente de chasse au Québec - Analyses territoriales, prévisions comportementales et optimisation de chasse",
        "sameAs": [
            "https://facebook.com/chassebionic",
            "https://instagram.com/chassebionic",
            "https://youtube.com/chassebionic"
        ],
        "contactPoint": {
            "@type": "ContactPoint",
            "telephone": "+1-XXX-XXX-XXXX",
            "contactType": "customer service",
            "availableLanguage": ["French", "English"]
        }
    }
    
    # Templates JSON-LD par type
    SCHEMA_TEMPLATES = {
        "Article": {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "{title}",
            "description": "{description}",
            "image": "{image_url}",
            "author": {
                "@type": "Organization",
                "name": "BIONIC"
            },
            "publisher": {
                "@type": "Organization",
                "name": "BIONIC - Chasse Bionic",
                "logo": {
                    "@type": "ImageObject",
                    "url": "https://chassebionic.com/logo.png"
                }
            },
            "datePublished": "{date_published}",
            "dateModified": "{date_modified}",
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": "{url}"
            },
            "articleSection": "{category}",
            "wordCount": "{word_count}",
            "inLanguage": "fr-CA"
        },
        "HowTo": {
            "@context": "https://schema.org",
            "@type": "HowTo",
            "name": "{title}",
            "description": "{description}",
            "image": "{image_url}",
            "totalTime": "PT{duration}M",
            "estimatedCost": {
                "@type": "MonetaryAmount",
                "currency": "CAD",
                "value": "{cost}"
            },
            "supply": [],
            "tool": [],
            "step": []
        },
        "FAQPage": {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": []
        },
        "LocalBusiness": {
            "@context": "https://schema.org",
            "@type": "LodgingBusiness",
            "name": "{name}",
            "description": "{description}",
            "image": "{image_url}",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "{street}",
                "addressLocality": "{city}",
                "addressRegion": "QC",
                "postalCode": "{postal_code}",
                "addressCountry": "CA"
            },
            "geo": {
                "@type": "GeoCoordinates",
                "latitude": "{latitude}",
                "longitude": "{longitude}"
            },
            "telephone": "{phone}",
            "priceRange": "{price_range}",
            "openingHours": "{hours}"
        },
        "BreadcrumbList": {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": []
        },
        "VideoObject": {
            "@context": "https://schema.org",
            "@type": "VideoObject",
            "name": "{title}",
            "description": "{description}",
            "thumbnailUrl": "{thumbnail_url}",
            "uploadDate": "{upload_date}",
            "duration": "PT{duration}M{seconds}S",
            "contentUrl": "{video_url}",
            "embedUrl": "{embed_url}",
            "publisher": {
                "@type": "Organization",
                "name": "BIONIC"
            }
        }
    }
    
    # ============================================
    # GENERATION
    # ============================================
    
    @staticmethod
    def generate_article_schema(page_data: dict) -> dict:
        """Générer un schéma Article"""
        return {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": page_data.get("title_fr", page_data.get("title", "")),
            "description": page_data.get("meta_description_fr", ""),
            "image": page_data.get("image_url", "https://chassebionic.com/default-article.jpg"),
            "author": {
                "@type": "Organization",
                "name": "BIONIC"
            },
            "publisher": {
                "@type": "Organization",
                "name": "BIONIC - Chasse Bionic",
                "logo": {
                    "@type": "ImageObject",
                    "url": "https://chassebionic.com/logo.png"
                }
            },
            "datePublished": page_data.get("published_at", datetime.now(timezone.utc).isoformat()),
            "dateModified": page_data.get("updated_at", datetime.now(timezone.utc).isoformat()),
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": page_data.get("url_path", "")
            },
            "articleSection": page_data.get("cluster_name", "Chasse"),
            "wordCount": page_data.get("word_count", 0),
            "inLanguage": "fr-CA",
            "keywords": ", ".join(page_data.get("secondary_keywords", []))
        }
    
    @staticmethod
    def generate_howto_schema(page_data: dict, steps: List[dict]) -> dict:
        """Générer un schéma HowTo"""
        schema_steps = []
        for i, step in enumerate(steps, 1):
            schema_steps.append({
                "@type": "HowToStep",
                "position": i,
                "name": step.get("title", f"Étape {i}"),
                "text": step.get("description", ""),
                "image": step.get("image_url", "")
            })
        
        return {
            "@context": "https://schema.org",
            "@type": "HowTo",
            "name": page_data.get("title_fr", ""),
            "description": page_data.get("meta_description_fr", ""),
            "image": page_data.get("image_url", ""),
            "totalTime": f"PT{page_data.get('reading_time_min', 10)}M",
            "step": schema_steps,
            "inLanguage": "fr-CA"
        }
    
    @staticmethod
    def generate_faq_schema(questions: List[dict]) -> dict:
        """Générer un schéma FAQPage"""
        main_entity = []
        for q in questions:
            main_entity.append({
                "@type": "Question",
                "name": q.get("question", ""),
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": q.get("answer", "")
                }
            })
        
        return {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": main_entity
        }
    
    @staticmethod
    def generate_breadcrumb_schema(breadcrumbs: List[dict]) -> dict:
        """Générer un schéma BreadcrumbList"""
        items = []
        for i, crumb in enumerate(breadcrumbs, 1):
            items.append({
                "@type": "ListItem",
                "position": i,
                "name": crumb.get("name", ""),
                "item": crumb.get("url", "")
            })
        
        return {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": items
        }
    
    @staticmethod
    def generate_local_business_schema(business_data: dict) -> dict:
        """Générer un schéma LocalBusiness (pourvoirie, ZEC)"""
        return {
            "@context": "https://schema.org",
            "@type": "LodgingBusiness",
            "name": business_data.get("name", ""),
            "description": business_data.get("description", ""),
            "image": business_data.get("image_url", ""),
            "address": {
                "@type": "PostalAddress",
                "streetAddress": business_data.get("street", ""),
                "addressLocality": business_data.get("city", ""),
                "addressRegion": "QC",
                "postalCode": business_data.get("postal_code", ""),
                "addressCountry": "CA"
            },
            "geo": {
                "@type": "GeoCoordinates",
                "latitude": business_data.get("latitude", 0),
                "longitude": business_data.get("longitude", 0)
            },
            "telephone": business_data.get("phone", ""),
            "priceRange": business_data.get("price_range", "$$"),
            "amenityFeature": business_data.get("amenities", []),
            "starRating": {
                "@type": "Rating",
                "ratingValue": business_data.get("rating", 4)
            }
        }
    
    # ============================================
    # CRUD OPERATIONS
    # ============================================
    
    @staticmethod
    async def get_all_schemas(db, page_id: str = None, schema_type: str = None, limit: int = 100) -> dict:
        """Récupérer tous les schémas JSON-LD"""
        try:
            query = {}
            if page_id:
                query["page_id"] = page_id
            if schema_type:
                query["schema_type"] = schema_type
            
            schemas = await db.seo_jsonld.find(query, {"_id": 0}).limit(limit).to_list(limit)
            
            return {
                "success": True,
                "total": len(schemas),
                "schemas": schemas
            }
        except Exception as e:
            logger.error(f"Error getting schemas: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def save_schema(db, page_id: str, schema_type: str, schema_data: dict) -> dict:
        """Sauvegarder un schéma JSON-LD"""
        try:
            schema = {
                "id": f"jsonld_{uuid.uuid4().hex[:8]}",
                "page_id": page_id,
                "schema_type": schema_type,
                "schema_data": schema_data,
                "is_valid": True,
                "validation_errors": [],
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Supprimer ancien schéma du même type pour la même page
            await db.seo_jsonld.delete_many({"page_id": page_id, "schema_type": schema_type})
            
            await db.seo_jsonld.insert_one(schema)
            schema.pop("_id", None)
            
            return {"success": True, "schema": schema}
        except Exception as e:
            logger.error(f"Error saving schema: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def validate_schema(schema_data: dict) -> dict:
        """Valider un schéma JSON-LD"""
        errors = []
        warnings = []
        
        # Vérifier @context
        if "@context" not in schema_data:
            errors.append("Missing @context")
        elif schema_data["@context"] != "https://schema.org":
            warnings.append("@context should be 'https://schema.org'")
        
        # Vérifier @type
        if "@type" not in schema_data:
            errors.append("Missing @type")
        
        # Validations par type
        schema_type = schema_data.get("@type", "")
        
        if schema_type == "Article":
            required = ["headline", "author", "publisher", "datePublished"]
            for field in required:
                if field not in schema_data:
                    errors.append(f"Article: missing required field '{field}'")
        
        elif schema_type == "HowTo":
            if "step" not in schema_data or not schema_data["step"]:
                errors.append("HowTo: must have at least one step")
        
        elif schema_type == "FAQPage":
            if "mainEntity" not in schema_data or not schema_data["mainEntity"]:
                errors.append("FAQPage: must have at least one question")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    @staticmethod
    def render_schema_script(schema_data: dict) -> str:
        """Générer le code HTML pour le schéma"""
        return f'<script type="application/ld+json">\n{json.dumps(schema_data, indent=2, ensure_ascii=False)}\n</script>'
    
    # ============================================
    # STATISTICS
    # ============================================
    
    @staticmethod
    async def get_schemas_stats(db) -> dict:
        """Statistiques des schémas JSON-LD"""
        try:
            total = await db.seo_jsonld.count_documents({})
            valid = await db.seo_jsonld.count_documents({"is_valid": True})
            
            # Par type
            by_type = {}
            for stype in ["Article", "HowTo", "FAQPage", "LocalBusiness", "BreadcrumbList", "VideoObject"]:
                count = await db.seo_jsonld.count_documents({"schema_type": stype})
                by_type[stype] = count
            
            return {
                "success": True,
                "stats": {
                    "total": total,
                    "valid": valid,
                    "invalid": total - valid,
                    "by_type": by_type
                }
            }
        except Exception as e:
            logger.error(f"Error getting schema stats: {e}")
            return {"success": False, "error": str(e)}


logger.info("SEOJsonLDManager initialized - V5 LEGO Module")
