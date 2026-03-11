"""
Branding Admin Service - V5-ULTIME Administration Premium
=========================================================

Service d'administration de l'identité visuelle:
- Gestion des logos (principal, FR, EN)
- Gestion des couleurs de marque
- Générateur de documents PDF avec en-tête
- Historique des uploads
- Assets de marque

Module isolé - aucun import croisé.
Phase 6 Migration - Partenaires & Branding.
"""

from datetime import datetime, timezone
import logging
import uuid

logger = logging.getLogger(__name__)


class BrandingAdminService:
    """Service isolé pour l'administration de l'identité visuelle"""
    
    # Configuration de la marque
    BRAND_CONFIG = {
        "fr": {
            "name": "Chasse Bionic",
            "full": "Chasse Bionic™",
            "tagline": "La science valide ce que le terrain confirme.",
            "domain": "chassebionic.ca"
        },
        "en": {
            "name": "Bionic Hunt",
            "full": "Bionic Hunt™",
            "tagline": "Science validates what the field confirms.",
            "domain": "bionichunt.com"
        }
    }
    
    # Couleurs de la marque
    BRAND_COLORS = {
        "primary": {"hex": "#f5a623", "name": "Golden Orange", "usage": "Couleur principale"},
        "secondary": {"hex": "#1a1a2e", "name": "Dark Navy", "usage": "Arrière-plan principal"},
        "accent": {"hex": "#16213e", "name": "Deep Blue", "usage": "Arrière-plan secondaire"},
        "success": {"hex": "#22c55e", "name": "Green", "usage": "États positifs"},
        "danger": {"hex": "#ef4444", "name": "Red", "usage": "États d'erreur"},
        "text": {"hex": "#ffffff", "name": "White", "usage": "Texte principal"},
        "muted": {"hex": "#6b7280", "name": "Gray", "usage": "Texte secondaire"}
    }
    
    # Types de documents
    DOCUMENT_TYPES = [
        {"id": "letter", "name_fr": "Lettre officielle", "name_en": "Official Letter"},
        {"id": "email", "name_fr": "En-tête Email", "name_en": "Email Header"},
        {"id": "contract", "name_fr": "Contrat", "name_en": "Contract"},
        {"id": "invoice", "name_fr": "Facture", "name_en": "Invoice"},
        {"id": "partner", "name_fr": "Document Partenaire", "name_en": "Partner Document"},
        {"id": "zec", "name_fr": "Document ZEC/Sépaq", "name_en": "ZEC/Sépaq Document"},
        {"id": "press", "name_fr": "Communiqué de Presse", "name_en": "Press Release"}
    ]
    
    # Logos par défaut
    DEFAULT_LOGOS = {
        "main": {
            "id": "main",
            "name": "Logo Principal BIONIC™",
            "url": "/logos/bionic-logo-main.png",
            "description": "Logo unifié Chasse Bionic™ / Bionic Hunt™"
        },
        "fr_full": {
            "id": "fr_full",
            "name": "Logo Complet FR",
            "url": "/logos/bionic-logo-main.png",
            "description": "Logo Chasse Bionic™ complet"
        },
        "en_full": {
            "id": "en_full",
            "name": "Full Logo EN",
            "url": "/logos/bionic-logo-main.png",
            "description": "Bionic Hunt™ full logo"
        }
    }
    
    # ============ DASHBOARD & STATS ============
    @staticmethod
    async def get_dashboard_stats(db) -> dict:
        """Statistiques globales du branding"""
        try:
            # Compter les logos custom
            custom_logos = await db.brand_logos.count_documents({})
            
            # Compter les documents générés
            generated_docs = await db.brand_documents.count_documents({})
            
            # Historique uploads
            upload_history = await db.brand_upload_history.count_documents({})
            
            # Dernière activité
            last_upload = await db.brand_upload_history.find_one(
                {}, {"_id": 0}, sort=[("uploaded_at", -1)]
            )
            
            return {
                "success": True,
                "stats": {
                    "logos": {
                        "default": len(BrandingAdminService.DEFAULT_LOGOS),
                        "custom": custom_logos,
                        "total": len(BrandingAdminService.DEFAULT_LOGOS) + custom_logos
                    },
                    "documents": {
                        "generated": generated_docs,
                        "types": len(BrandingAdminService.DOCUMENT_TYPES)
                    },
                    "uploads": {
                        "total": upload_history
                    },
                    "colors": len(BrandingAdminService.BRAND_COLORS),
                    "last_upload": last_upload.get("uploaded_at") if last_upload else None
                }
            }
        except Exception as e:
            logger.error(f"Error in get_dashboard_stats: {e}")
            return {"success": False, "error": str(e)}
    
    # ============ BRAND CONFIG ============
    @staticmethod
    async def get_brand_config(db) -> dict:
        """Récupérer la configuration de la marque"""
        return {
            "success": True,
            "config": {
                "brands": BrandingAdminService.BRAND_CONFIG,
                "colors": BrandingAdminService.BRAND_COLORS,
                "document_types": BrandingAdminService.DOCUMENT_TYPES
            }
        }
    
    # ============ LOGOS MANAGEMENT ============
    @staticmethod
    async def get_logos(db) -> dict:
        """Liste de tous les logos"""
        try:
            # Logos par défaut
            default_logos = list(BrandingAdminService.DEFAULT_LOGOS.values())
            
            # Logos custom
            custom_logos = await db.brand_logos.find({}, {"_id": 0}).to_list(50)
            
            return {
                "success": True,
                "default": default_logos,
                "custom": custom_logos
            }
        except Exception as e:
            logger.error(f"Error in get_logos: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def get_logo_detail(db, logo_id: str) -> dict:
        """Détail d'un logo"""
        try:
            # Vérifier les logos par défaut
            if logo_id in BrandingAdminService.DEFAULT_LOGOS:
                return {
                    "success": True,
                    "logo": BrandingAdminService.DEFAULT_LOGOS[logo_id],
                    "is_default": True
                }
            
            # Chercher dans les customs
            logo = await db.brand_logos.find_one({"id": logo_id}, {"_id": 0})
            if logo:
                return {"success": True, "logo": logo, "is_default": False}
            
            return {"success": False, "error": "Logo non trouvé"}
        except Exception as e:
            logger.error(f"Error in get_logo_detail: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def add_custom_logo(db, filename: str, url: str, language: str, logo_type: str, file_size: int = 0) -> dict:
        """Ajouter un logo personnalisé"""
        try:
            logo = {
                "id": str(uuid.uuid4()),
                "filename": filename,
                "url": url,
                "language": language,
                "logo_type": logo_type,
                "file_size": file_size,
                "uploaded_at": datetime.now(timezone.utc).isoformat()
            }
            
            await db.brand_logos.insert_one(logo)
            
            # Remove MongoDB _id before returning
            logo.pop("_id", None)
            
            # Log dans l'historique
            history_entry = {
                "id": str(uuid.uuid4()),
                "filename": filename,
                "language": language,
                "logo_type": logo_type,
                "file_size": file_size,
                "uploaded_at": datetime.now(timezone.utc).isoformat()
            }
            await db.brand_upload_history.insert_one(history_entry)
            
            return {
                "success": True,
                "logo": logo,
                "message": "Logo uploadé avec succès"
            }
        except Exception as e:
            logger.error(f"Error in add_custom_logo: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def delete_logo(db, logo_id: str) -> dict:
        """Supprimer un logo personnalisé"""
        try:
            # Ne pas supprimer les logos par défaut
            if logo_id in BrandingAdminService.DEFAULT_LOGOS:
                return {"success": False, "error": "Impossible de supprimer un logo système"}
            
            result = await db.brand_logos.delete_one({"id": logo_id})
            
            if result.deleted_count == 0:
                return {"success": False, "error": "Logo non trouvé"}
            
            return {"success": True, "message": "Logo supprimé"}
        except Exception as e:
            logger.error(f"Error in delete_logo: {e}")
            return {"success": False, "error": str(e)}
    
    # ============ COLORS MANAGEMENT ============
    @staticmethod
    async def get_colors(db) -> dict:
        """Récupérer les couleurs de la marque"""
        try:
            # Vérifier s'il y a des overrides en DB
            custom_colors = await db.brand_colors.find_one({"_id": "colors"})
            
            if custom_colors:
                del custom_colors["_id"]
                return {"success": True, "colors": custom_colors, "is_custom": True}
            
            return {"success": True, "colors": BrandingAdminService.BRAND_COLORS, "is_custom": False}
        except Exception as e:
            logger.error(f"Error in get_colors: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def update_color(db, color_key: str, hex_value: str, name: str = None) -> dict:
        """Mettre à jour une couleur"""
        try:
            # Valider le format hex
            if not hex_value.startswith("#") or len(hex_value) != 7:
                return {"success": False, "error": "Format hex invalide (ex: #f5a623)"}
            
            update_data = {f"colors.{color_key}.hex": hex_value}
            if name:
                update_data[f"colors.{color_key}.name"] = name
            update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            await db.brand_colors.update_one(
                {"_id": "colors"},
                {"$set": update_data},
                upsert=True
            )
            
            return {"success": True, "color_key": color_key, "hex": hex_value}
        except Exception as e:
            logger.error(f"Error in update_color: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def reset_colors(db) -> dict:
        """Réinitialiser les couleurs par défaut"""
        try:
            await db.brand_colors.delete_one({"_id": "colors"})
            return {"success": True, "message": "Couleurs réinitialisées", "colors": BrandingAdminService.BRAND_COLORS}
        except Exception as e:
            logger.error(f"Error in reset_colors: {e}")
            return {"success": False, "error": str(e)}
    
    # ============ DOCUMENT TEMPLATES ============
    @staticmethod
    async def get_document_types(db) -> dict:
        """Liste des types de documents"""
        return {
            "success": True,
            "document_types": BrandingAdminService.DOCUMENT_TYPES
        }
    
    @staticmethod
    async def log_document_generation(db, template_type: str, language: str, 
                                      title: str = None, recipient: str = None) -> dict:
        """Logger une génération de document"""
        try:
            log_entry = {
                "id": str(uuid.uuid4()),
                "template_type": template_type,
                "language": language,
                "title": title,
                "recipient": recipient,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
            await db.brand_documents.insert_one(log_entry)
            
            return {"success": True, "log_id": log_entry["id"]}
        except Exception as e:
            logger.error(f"Error in log_document_generation: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def get_document_history(db, limit: int = 50) -> dict:
        """Historique des documents générés"""
        try:
            history = await db.brand_documents.find(
                {}, {"_id": 0}
            ).sort("generated_at", -1).limit(limit).to_list(limit)
            
            return {
                "success": True,
                "total": len(history),
                "history": history
            }
        except Exception as e:
            logger.error(f"Error in get_document_history: {e}")
            return {"success": False, "error": str(e)}
    
    # ============ UPLOAD HISTORY ============
    @staticmethod
    async def get_upload_history(db, limit: int = 50) -> dict:
        """Historique des uploads de logos"""
        try:
            history = await db.brand_upload_history.find(
                {}, {"_id": 0}
            ).sort("uploaded_at", -1).limit(limit).to_list(limit)
            
            return {
                "success": True,
                "total": len(history),
                "history": history
            }
        except Exception as e:
            logger.error(f"Error in get_upload_history: {e}")
            return {"success": False, "error": str(e)}
    
    # ============ BRAND ASSETS ============
    @staticmethod
    async def get_brand_assets(db) -> dict:
        """Récupérer tous les assets de la marque"""
        try:
            logos_result = await BrandingAdminService.get_logos(db)
            colors_result = await BrandingAdminService.get_colors(db)
            
            return {
                "success": True,
                "assets": {
                    "brand": BrandingAdminService.BRAND_CONFIG,
                    "logos": {
                        "default": logos_result.get("default", []),
                        "custom": logos_result.get("custom", [])
                    },
                    "colors": colors_result.get("colors", BrandingAdminService.BRAND_COLORS),
                    "document_types": BrandingAdminService.DOCUMENT_TYPES
                }
            }
        except Exception as e:
            logger.error(f"Error in get_brand_assets: {e}")
            return {"success": False, "error": str(e)}


logger.info("BrandingAdminService initialized - Phase 6 Migration")
