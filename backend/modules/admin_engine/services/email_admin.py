"""
Email Admin Service - V5-ULTIME Administration Premium
======================================================

Service d'administration des emails et templates:
- Gestion des templates email
- Variables dynamiques
- Historique des envois
- Tests d'envoi
- Configuration du service email

Module isolé - aucun import croisé.
Phase 5 Migration - Communication.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional
import logging
import uuid

logger = logging.getLogger(__name__)


class EmailAdminService:
    """Service isolé pour l'administration des emails"""
    
    # Templates par défaut
    DEFAULT_TEMPLATES = {
        "welcome": {
            "id": "welcome",
            "name": "Email de bienvenue",
            "subject": "Bienvenue sur {{brand_name}}!",
            "category": "transactional",
            "html_template": """
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px;">
<div style="max-width: 600px; margin: 0 auto; background: #fff; border-radius: 10px; overflow: hidden;">
    <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 30px; text-align: center;">
        <h1 style="color: #f5a623; margin: 0;">{{brand_name}}</h1>
    </div>
    <div style="padding: 30px;">
        <p>Bonjour <strong>{{user_name}}</strong>,</p>
        <p>Bienvenue sur {{brand_name}}! Nous sommes ravis de vous accueillir.</p>
        <p>Votre compte a été créé avec succès. Vous pouvez maintenant :</p>
        <ul>
            <li>Explorer notre plateforme</li>
            <li>Configurer votre profil</li>
            <li>Découvrir nos fonctionnalités</li>
        </ul>
        <p style="margin-top: 30px;">
            <a href="{{app_url}}" style="background: #f5a623; color: #000; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">Commencer</a>
        </p>
    </div>
    <div style="background: #1a1a2e; color: #888; padding: 20px; text-align: center; font-size: 12px;">
        <p>© {{year}} {{brand_name}} - Tous droits réservés</p>
    </div>
</div>
</body>
</html>
            """,
            "text_template": """
Bonjour {{user_name}},

Bienvenue sur {{brand_name}}! Nous sommes ravis de vous accueillir.

Votre compte a été créé avec succès.

Commencez maintenant: {{app_url}}

© {{year}} {{brand_name}}
            """,
            "variables": ["user_name", "brand_name", "app_url", "year"],
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z"
        },
        "order_confirmation": {
            "id": "order_confirmation",
            "name": "Confirmation de commande",
            "subject": "Confirmation de votre commande #{{order_id}}",
            "category": "transactional",
            "html_template": "<!-- Order confirmation template -->",
            "text_template": "Confirmation commande #{{order_id}}",
            "variables": ["user_name", "order_id", "order_total", "products_list", "brand_name"],
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z"
        },
        "password_reset": {
            "id": "password_reset",
            "name": "Réinitialisation mot de passe",
            "subject": "Réinitialisez votre mot de passe",
            "category": "transactional",
            "html_template": "<!-- Password reset template -->",
            "text_template": "Réinitialisez votre mot de passe: {{reset_link}}",
            "variables": ["user_name", "reset_link", "brand_name", "expiry_hours"],
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z"
        },
        "notification_digest": {
            "id": "notification_digest",
            "name": "Résumé des notifications",
            "subject": "Vous avez {{count}} nouvelles notifications",
            "category": "notification",
            "html_template": "<!-- Digest template -->",
            "text_template": "Vous avez {{count}} notifications non lues.",
            "variables": ["user_name", "count", "notifications_list", "brand_name"],
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z"
        },
        "newsletter": {
            "id": "newsletter",
            "name": "Newsletter",
            "subject": "{{newsletter_title}}",
            "category": "marketing",
            "html_template": "<!-- Newsletter template -->",
            "text_template": "{{newsletter_content}}",
            "variables": ["user_name", "newsletter_title", "newsletter_content", "brand_name", "unsubscribe_link"],
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z"
        },
        "promo_campaign": {
            "id": "promo_campaign",
            "name": "Campagne promotionnelle",
            "subject": "{{promo_title}} - {{discount}}% de rabais!",
            "category": "marketing",
            "html_template": "<!-- Promo template -->",
            "text_template": "{{promo_title}} - Profitez de {{discount}}% de rabais!",
            "variables": ["user_name", "promo_title", "discount", "promo_code", "expiry_date", "brand_name"],
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z"
        }
    }
    
    # ============ DASHBOARD & STATS ============
    @staticmethod
    async def get_dashboard_stats(db) -> dict:
        """Statistiques globales des emails"""
        try:
            # Stats templates
            templates = await db.email_templates.find({}, {"_id": 0}).to_list(100)
            total_templates = len(templates) if templates else len(EmailAdminService.DEFAULT_TEMPLATES)
            active_templates = len([t for t in templates if t.get("is_active", True)]) if templates else total_templates
            
            # Stats envois
            total_sent = await db.email_logs.count_documents({})
            sent_today = await db.email_logs.count_documents({
                "sent_at": {"$gte": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()}
            })
            sent_week = await db.email_logs.count_documents({
                "sent_at": {"$gte": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()}
            })
            
            # Stats par statut
            delivered = await db.email_logs.count_documents({"status": "delivered"})
            bounced = await db.email_logs.count_documents({"status": "bounced"})
            opened = await db.email_logs.count_documents({"opened": True})
            clicked = await db.email_logs.count_documents({"clicked": True})
            
            delivery_rate = round((delivered / max(total_sent, 1)) * 100, 1)
            open_rate = round((opened / max(delivered, 1)) * 100, 1)
            click_rate = round((clicked / max(opened, 1)) * 100, 1)
            
            # Stats par catégorie
            by_category = {}
            for cat in ["transactional", "notification", "marketing"]:
                by_category[cat] = await db.email_logs.count_documents({"category": cat})
            
            # Configuration service
            config = await db.email_config.find_one({"_id": "main"})
            
            return {
                "success": True,
                "stats": {
                    "templates": {
                        "total": total_templates,
                        "active": active_templates
                    },
                    "sending": {
                        "total": total_sent,
                        "today": sent_today,
                        "this_week": sent_week
                    },
                    "delivery": {
                        "delivered": delivered,
                        "bounced": bounced,
                        "delivery_rate": delivery_rate
                    },
                    "engagement": {
                        "opened": opened,
                        "clicked": clicked,
                        "open_rate": open_rate,
                        "click_rate": click_rate
                    },
                    "by_category": by_category,
                    "config": {
                        "service_configured": config.get("is_configured", False) if config else False,
                        "sender_email": config.get("sender_email", "Non configuré") if config else "Non configuré",
                        "provider": config.get("provider", "resend") if config else "resend"
                    }
                }
            }
        except Exception as e:
            logger.error(f"Error in get_dashboard_stats: {e}")
            return {"success": False, "error": str(e)}
    
    # ============ TEMPLATES MANAGEMENT ============
    @staticmethod
    async def get_templates(db, category: Optional[str] = None, is_active: Optional[bool] = None) -> dict:
        """Liste les templates email"""
        try:
            query = {}
            if category:
                query["category"] = category
            if is_active is not None:
                query["is_active"] = is_active
            
            templates = await db.email_templates.find(query, {"_id": 0}).to_list(100)
            
            # Si pas de templates en DB, utiliser les défauts
            if not templates:
                templates = list(EmailAdminService.DEFAULT_TEMPLATES.values())
                if category:
                    templates = [t for t in templates if t.get("category") == category]
                if is_active is not None:
                    templates = [t for t in templates if t.get("is_active") == is_active]
            
            # Catégories disponibles
            categories = {}
            for cat in ["transactional", "notification", "marketing"]:
                categories[cat] = len([t for t in templates if t.get("category") == cat])
            
            return {
                "success": True,
                "total": len(templates),
                "categories": categories,
                "templates": templates
            }
        except Exception as e:
            logger.error(f"Error in get_templates: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def get_template_detail(db, template_id: str) -> dict:
        """Détail d'un template"""
        try:
            template = await db.email_templates.find_one({"id": template_id}, {"_id": 0})
            
            if not template:
                template = EmailAdminService.DEFAULT_TEMPLATES.get(template_id)
            
            if not template:
                return {"success": False, "error": "Template non trouvé"}
            
            # Stats d'utilisation
            usage_count = await db.email_logs.count_documents({"template_id": template_id})
            
            return {
                "success": True,
                "template": template,
                "usage_count": usage_count
            }
        except Exception as e:
            logger.error(f"Error in get_template_detail: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def create_template(db, template_data: dict) -> dict:
        """Créer un nouveau template"""
        try:
            template_id = template_data.get("id") or str(uuid.uuid4())[:8]
            
            template = {
                "id": template_id,
                "name": template_data.get("name", "Nouveau template"),
                "subject": template_data.get("subject", ""),
                "category": template_data.get("category", "transactional"),
                "html_template": template_data.get("html_template", ""),
                "text_template": template_data.get("text_template", ""),
                "variables": template_data.get("variables", []),
                "is_active": template_data.get("is_active", True),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            await db.email_templates.insert_one(template)
            if "_id" in template:
                del template["_id"]
            
            return {
                "success": True,
                "template": template
            }
        except Exception as e:
            logger.error(f"Error in create_template: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def update_template(db, template_id: str, updates: dict) -> dict:
        """Mettre à jour un template"""
        try:
            updates["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            # Retirer les champs non modifiables
            updates.pop("id", None)
            updates.pop("created_at", None)
            
            result = await db.email_templates.update_one(
                {"id": template_id},
                {"$set": updates}
            )
            
            if result.matched_count == 0:
                # Créer le template s'il n'existe pas (migration depuis défauts)
                default = EmailAdminService.DEFAULT_TEMPLATES.get(template_id)
                if default:
                    merged = {**default, **updates, "id": template_id}
                    await db.email_templates.insert_one(merged)
                    return {"success": True, "template_id": template_id, "created": True}
                return {"success": False, "error": "Template non trouvé"}
            
            return {"success": True, "template_id": template_id}
        except Exception as e:
            logger.error(f"Error in update_template: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def delete_template(db, template_id: str) -> dict:
        """Supprimer un template"""
        try:
            # Ne pas permettre la suppression des templates par défaut
            if template_id in EmailAdminService.DEFAULT_TEMPLATES:
                return {"success": False, "error": "Impossible de supprimer un template système"}
            
            result = await db.email_templates.delete_one({"id": template_id})
            
            if result.deleted_count == 0:
                return {"success": False, "error": "Template non trouvé"}
            
            return {"success": True, "deleted": True}
        except Exception as e:
            logger.error(f"Error in delete_template: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def toggle_template_active(db, template_id: str, is_active: bool) -> dict:
        """Activer/désactiver un template"""
        try:
            result = await db.email_templates.update_one(
                {"id": template_id},
                {"$set": {"is_active": is_active, "updated_at": datetime.now(timezone.utc).isoformat()}}
            )
            
            if result.matched_count == 0:
                # Migration depuis défauts
                default = EmailAdminService.DEFAULT_TEMPLATES.get(template_id)
                if default:
                    template = {**default, "is_active": is_active, "updated_at": datetime.now(timezone.utc).isoformat()}
                    await db.email_templates.insert_one(template)
                    return {"success": True, "template_id": template_id, "is_active": is_active}
                return {"success": False, "error": "Template non trouvé"}
            
            return {"success": True, "template_id": template_id, "is_active": is_active}
        except Exception as e:
            logger.error(f"Error in toggle_template_active: {e}")
            return {"success": False, "error": str(e)}
    
    # ============ VARIABLES ============
    @staticmethod
    async def get_variables(db) -> dict:
        """Liste toutes les variables disponibles"""
        try:
            # Variables système
            system_vars = [
                {"name": "user_name", "description": "Nom de l'utilisateur", "category": "user"},
                {"name": "user_email", "description": "Email de l'utilisateur", "category": "user"},
                {"name": "brand_name", "description": "Nom de la marque", "category": "system"},
                {"name": "app_url", "description": "URL de l'application", "category": "system"},
                {"name": "year", "description": "Année actuelle", "category": "system"},
                {"name": "date", "description": "Date actuelle", "category": "system"},
                {"name": "order_id", "description": "ID de commande", "category": "order"},
                {"name": "order_total", "description": "Total de la commande", "category": "order"},
                {"name": "products_list", "description": "Liste des produits", "category": "order"},
                {"name": "reset_link", "description": "Lien de réinitialisation", "category": "auth"},
                {"name": "verification_link", "description": "Lien de vérification", "category": "auth"},
                {"name": "expiry_hours", "description": "Heures avant expiration", "category": "auth"},
                {"name": "promo_code", "description": "Code promo", "category": "marketing"},
                {"name": "discount", "description": "Pourcentage de rabais", "category": "marketing"},
                {"name": "unsubscribe_link", "description": "Lien de désabonnement", "category": "marketing"}
            ]
            
            # Variables custom
            custom_vars = await db.email_variables.find({}, {"_id": 0}).to_list(50)
            
            return {
                "success": True,
                "system_variables": system_vars,
                "custom_variables": custom_vars or []
            }
        except Exception as e:
            logger.error(f"Error in get_variables: {e}")
            return {"success": False, "error": str(e)}
    
    # ============ EMAIL LOGS ============
    @staticmethod
    async def get_email_logs(db, status: Optional[str] = None, 
                            template_id: Optional[str] = None,
                            limit: int = 50) -> dict:
        """Historique des emails envoyés"""
        try:
            query = {}
            if status:
                query["status"] = status
            if template_id:
                query["template_id"] = template_id
            
            logs = await db.email_logs.find(
                query, {"_id": 0}
            ).sort("sent_at", -1).limit(limit).to_list(limit)
            
            total = await db.email_logs.count_documents(query)
            
            return {
                "success": True,
                "total": total,
                "logs": logs
            }
        except Exception as e:
            logger.error(f"Error in get_email_logs: {e}")
            return {"success": False, "error": str(e)}
    
    # ============ TEST EMAIL ============
    @staticmethod
    async def send_test_email(db, template_id: str, recipient_email: str, test_variables: dict = None) -> dict:
        """Envoyer un email de test"""
        try:
            # Récupérer le template
            template = await db.email_templates.find_one({"id": template_id}, {"_id": 0})
            if not template:
                template = EmailAdminService.DEFAULT_TEMPLATES.get(template_id)
            
            if not template:
                return {"success": False, "error": "Template non trouvé"}
            
            # Préparer les variables de test
            variables = {
                "user_name": "Test User",
                "brand_name": "BIONIC HUNT/Chasse",
                "app_url": "https://app.example.com",
                "year": str(datetime.now().year),
                **(test_variables or {})
            }
            
            # Log l'envoi (simulation)
            log_entry = {
                "id": str(uuid.uuid4()),
                "template_id": template_id,
                "recipient": recipient_email,
                "subject": template.get("subject", "").replace("{{brand_name}}", variables.get("brand_name", "")),
                "status": "simulated",
                "sent_at": datetime.now(timezone.utc).isoformat(),
                "is_test": True
            }
            await db.email_logs.insert_one(log_entry)
            
            return {
                "success": True,
                "status": "simulated",
                "message": f"Email de test envoyé à {recipient_email} (mode simulation)",
                "log_id": log_entry["id"]
            }
        except Exception as e:
            logger.error(f"Error in send_test_email: {e}")
            return {"success": False, "error": str(e)}
    
    # ============ CONFIGURATION ============
    @staticmethod
    async def get_config(db) -> dict:
        """Récupérer la configuration email"""
        try:
            config = await db.email_config.find_one({"_id": "main"})
            
            if not config:
                config = {
                    "provider": "resend",
                    "sender_email": "noreply@example.com",
                    "sender_name": "BIONIC HUNT/Chasse",
                    "is_configured": False,
                    "daily_limit": 1000,
                    "rate_limit_per_minute": 60
                }
            else:
                del config["_id"]
                # Masquer la clé API
                if "api_key" in config:
                    config["api_key"] = "***" + config["api_key"][-4:] if config["api_key"] else None
            
            return {
                "success": True,
                "config": config
            }
        except Exception as e:
            logger.error(f"Error in get_config: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def update_config(db, updates: dict) -> dict:
        """Mettre à jour la configuration email"""
        try:
            updates["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            await db.email_config.update_one(
                {"_id": "main"},
                {"$set": updates},
                upsert=True
            )
            
            return {"success": True, "message": "Configuration mise à jour"}
        except Exception as e:
            logger.error(f"Error in update_config: {e}")
            return {"success": False, "error": str(e)}


logger.info("EmailAdminService initialized - Phase 5 Migration")
