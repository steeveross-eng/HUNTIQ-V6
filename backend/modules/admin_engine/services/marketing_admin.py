"""
Marketing Admin Service - V5-ULTIME Administration Premium
==========================================================

Service d'administration du marketing:
- Campagnes marketing
- Génération de contenu IA
- Publications réseaux sociaux
- Segmentation audience
- Automations

Module isolé - aucun import croisé.
Phase 5 Migration - Communication.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional
import logging
import uuid

logger = logging.getLogger(__name__)


class MarketingAdminService:
    """Service isolé pour l'administration du marketing"""
    
    # Types de contenu
    CONTENT_TYPES = [
        {"id": "product_promo", "name": "Promotion Produit", "icon": "target"},
        {"id": "educational", "name": "Contenu Éducatif", "icon": "book"},
        {"id": "seasonal", "name": "Publication Saisonnière", "icon": "calendar"},
        {"id": "testimonial", "name": "Témoignage Client", "icon": "message"},
        {"id": "tip", "name": "Conseil Expert", "icon": "lightbulb"},
        {"id": "engagement", "name": "Question/Engagement", "icon": "users"}
    ]
    
    # Plateformes sociales
    PLATFORMS = [
        {"id": "facebook", "name": "Facebook", "max_length": 63206},
        {"id": "instagram", "name": "Instagram", "max_length": 2200},
        {"id": "twitter", "name": "Twitter/X", "max_length": 280},
        {"id": "linkedin", "name": "LinkedIn", "max_length": 3000}
    ]
    
    # ============ DASHBOARD & STATS ============
    @staticmethod
    async def get_dashboard_stats(db) -> dict:
        """Statistiques globales du marketing"""
        try:
            # Campagnes
            total_campaigns = await db.marketing_campaigns.count_documents({})
            active_campaigns = await db.marketing_campaigns.count_documents({"status": "active"})
            draft_campaigns = await db.marketing_campaigns.count_documents({"status": "draft"})
            
            # Publications
            total_posts = await db.marketing_posts.count_documents({})
            published_posts = await db.marketing_posts.count_documents({"status": "published"})
            scheduled_posts = await db.marketing_posts.count_documents({"status": "scheduled"})
            
            # Engagement (derniers 30 jours)
            thirty_days_ago = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            recent_posts = await db.marketing_posts.find({
                "published_at": {"$gte": thirty_days_ago}
            }).to_list(1000)
            
            total_impressions = sum(p.get("impressions", 0) for p in recent_posts)
            total_clicks = sum(p.get("clicks", 0) for p in recent_posts)
            total_engagement = sum(p.get("engagement", 0) for p in recent_posts)
            
            # Segments
            total_segments = await db.marketing_segments.count_documents({})
            
            # Automations
            total_automations = await db.marketing_automations.count_documents({})
            active_automations = await db.marketing_automations.count_documents({"is_active": True})
            
            # Stats par plateforme
            by_platform = {}
            for platform in ["facebook", "instagram", "twitter", "linkedin"]:
                by_platform[platform] = await db.marketing_posts.count_documents({"platform": platform})
            
            return {
                "success": True,
                "stats": {
                    "campaigns": {
                        "total": total_campaigns,
                        "active": active_campaigns,
                        "draft": draft_campaigns
                    },
                    "posts": {
                        "total": total_posts,
                        "published": published_posts,
                        "scheduled": scheduled_posts
                    },
                    "engagement_30d": {
                        "impressions": total_impressions,
                        "clicks": total_clicks,
                        "engagement": total_engagement,
                        "ctr": round((total_clicks / max(total_impressions, 1)) * 100, 2)
                    },
                    "segments": {
                        "total": total_segments
                    },
                    "automations": {
                        "total": total_automations,
                        "active": active_automations
                    },
                    "by_platform": by_platform
                }
            }
        except Exception as e:
            logger.error(f"Error in get_dashboard_stats: {e}")
            return {"success": False, "error": str(e)}
    
    # ============ CAMPAIGNS MANAGEMENT ============
    @staticmethod
    async def get_campaigns(db, status: Optional[str] = None, limit: int = 50) -> dict:
        """Liste des campagnes marketing"""
        try:
            query = {}
            if status and status != 'all':
                query["status"] = status
            
            campaigns = await db.marketing_campaigns.find(
                query, {"_id": 0}
            ).sort("created_at", -1).limit(limit).to_list(limit)
            
            total = await db.marketing_campaigns.count_documents(query)
            
            # Stats par statut
            status_counts = {}
            for s in ["draft", "active", "paused", "completed", "archived"]:
                status_counts[s] = await db.marketing_campaigns.count_documents({"status": s})
            
            return {
                "success": True,
                "total": total,
                "status_counts": status_counts,
                "campaigns": campaigns
            }
        except Exception as e:
            logger.error(f"Error in get_campaigns: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def get_campaign_detail(db, campaign_id: str) -> dict:
        """Détail d'une campagne"""
        try:
            campaign = await db.marketing_campaigns.find_one({"id": campaign_id}, {"_id": 0})
            
            if not campaign:
                return {"success": False, "error": "Campagne non trouvée"}
            
            # Posts de la campagne
            posts = await db.marketing_posts.find(
                {"campaign_id": campaign_id}, {"_id": 0}
            ).sort("created_at", -1).to_list(100)
            
            # Stats
            total_impressions = sum(p.get("impressions", 0) for p in posts)
            total_clicks = sum(p.get("clicks", 0) for p in posts)
            
            return {
                "success": True,
                "campaign": campaign,
                "posts": posts,
                "performance": {
                    "total_posts": len(posts),
                    "impressions": total_impressions,
                    "clicks": total_clicks,
                    "ctr": round((total_clicks / max(total_impressions, 1)) * 100, 2)
                }
            }
        except Exception as e:
            logger.error(f"Error in get_campaign_detail: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def create_campaign(db, campaign_data: dict) -> dict:
        """Créer une nouvelle campagne"""
        try:
            campaign = {
                "id": str(uuid.uuid4()),
                "name": campaign_data.get("name", "Nouvelle campagne"),
                "description": campaign_data.get("description", ""),
                "type": campaign_data.get("type", "promotional"),
                "status": "draft",
                "start_date": campaign_data.get("start_date"),
                "end_date": campaign_data.get("end_date"),
                "target_platforms": campaign_data.get("target_platforms", ["facebook"]),
                "target_segment": campaign_data.get("target_segment"),
                "budget": campaign_data.get("budget", 0),
                "goals": campaign_data.get("goals", {}),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            await db.marketing_campaigns.insert_one(campaign)
            if "_id" in campaign:
                del campaign["_id"]
            
            return {
                "success": True,
                "campaign": campaign
            }
        except Exception as e:
            logger.error(f"Error in create_campaign: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def update_campaign(db, campaign_id: str, updates: dict) -> dict:
        """Mettre à jour une campagne"""
        try:
            updates["updated_at"] = datetime.now(timezone.utc).isoformat()
            updates.pop("id", None)
            updates.pop("created_at", None)
            
            result = await db.marketing_campaigns.update_one(
                {"id": campaign_id},
                {"$set": updates}
            )
            
            if result.matched_count == 0:
                return {"success": False, "error": "Campagne non trouvée"}
            
            return {"success": True, "campaign_id": campaign_id}
        except Exception as e:
            logger.error(f"Error in update_campaign: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def update_campaign_status(db, campaign_id: str, status: str) -> dict:
        """Changer le statut d'une campagne"""
        valid_statuses = ["draft", "active", "paused", "completed", "archived"]
        if status not in valid_statuses:
            return {"success": False, "error": f"Statut invalide. Valides: {valid_statuses}"}
        
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            if status == "active":
                update_data["activated_at"] = datetime.now(timezone.utc).isoformat()
            elif status == "completed":
                update_data["completed_at"] = datetime.now(timezone.utc).isoformat()
            
            result = await db.marketing_campaigns.update_one(
                {"id": campaign_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return {"success": False, "error": "Campagne non trouvée"}
            
            return {"success": True, "campaign_id": campaign_id, "status": status}
        except Exception as e:
            logger.error(f"Error in update_campaign_status: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def delete_campaign(db, campaign_id: str) -> dict:
        """Supprimer une campagne"""
        try:
            result = await db.marketing_campaigns.delete_one({"id": campaign_id})
            
            if result.deleted_count == 0:
                return {"success": False, "error": "Campagne non trouvée"}
            
            # Supprimer les posts associés
            await db.marketing_posts.delete_many({"campaign_id": campaign_id})
            
            return {"success": True, "deleted": True}
        except Exception as e:
            logger.error(f"Error in delete_campaign: {e}")
            return {"success": False, "error": str(e)}
    
    # ============ POSTS MANAGEMENT ============
    @staticmethod
    async def get_posts(db, status: Optional[str] = None, 
                       platform: Optional[str] = None,
                       limit: int = 50) -> dict:
        """Liste des publications"""
        try:
            query = {}
            if status and status != 'all':
                query["status"] = status
            if platform and platform != 'all':
                query["platform"] = platform
            
            posts = await db.marketing_posts.find(
                query, {"_id": 0}
            ).sort("created_at", -1).limit(limit).to_list(limit)
            
            total = await db.marketing_posts.count_documents(query)
            
            return {
                "success": True,
                "total": total,
                "posts": posts
            }
        except Exception as e:
            logger.error(f"Error in get_posts: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def get_scheduled_posts(db, limit: int = 50) -> dict:
        """Publications programmées"""
        try:
            posts = await db.marketing_posts.find(
                {"status": "scheduled"},
                {"_id": 0}
            ).sort("scheduled_at", 1).limit(limit).to_list(limit)
            
            return {
                "success": True,
                "total": len(posts),
                "posts": posts
            }
        except Exception as e:
            logger.error(f"Error in get_scheduled_posts: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def create_post(db, post_data: dict) -> dict:
        """Créer une publication"""
        try:
            post = {
                "id": str(uuid.uuid4()),
                "campaign_id": post_data.get("campaign_id"),
                "platform": post_data.get("platform", "facebook"),
                "content": post_data.get("content", ""),
                "hashtags": post_data.get("hashtags", []),
                "media_urls": post_data.get("media_urls", []),
                "content_type": post_data.get("content_type", "product_promo"),
                "status": post_data.get("status", "draft"),
                "scheduled_at": post_data.get("scheduled_at"),
                "impressions": 0,
                "clicks": 0,
                "engagement": 0,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            await db.marketing_posts.insert_one(post)
            if "_id" in post:
                del post["_id"]
            
            return {
                "success": True,
                "post": post
            }
        except Exception as e:
            logger.error(f"Error in create_post: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def schedule_post(db, post_id: str, scheduled_at: str) -> dict:
        """Programmer une publication"""
        try:
            result = await db.marketing_posts.update_one(
                {"id": post_id},
                {"$set": {
                    "status": "scheduled",
                    "scheduled_at": scheduled_at,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            
            if result.matched_count == 0:
                return {"success": False, "error": "Publication non trouvée"}
            
            return {"success": True, "post_id": post_id, "scheduled_at": scheduled_at}
        except Exception as e:
            logger.error(f"Error in schedule_post: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def publish_post(db, post_id: str) -> dict:
        """Publier immédiatement (simulation)"""
        try:
            now = datetime.now(timezone.utc).isoformat()
            
            result = await db.marketing_posts.update_one(
                {"id": post_id},
                {"$set": {
                    "status": "published",
                    "published_at": now,
                    "updated_at": now
                }}
            )
            
            if result.matched_count == 0:
                return {"success": False, "error": "Publication non trouvée"}
            
            return {
                "success": True,
                "post_id": post_id,
                "status": "published",
                "message": "Publication simulée (connectez vos réseaux sociaux pour publier réellement)"
            }
        except Exception as e:
            logger.error(f"Error in publish_post: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def delete_post(db, post_id: str) -> dict:
        """Supprimer une publication"""
        try:
            result = await db.marketing_posts.delete_one({"id": post_id})
            
            if result.deleted_count == 0:
                return {"success": False, "error": "Publication non trouvée"}
            
            return {"success": True, "deleted": True}
        except Exception as e:
            logger.error(f"Error in delete_post: {e}")
            return {"success": False, "error": str(e)}
    
    # ============ AI CONTENT GENERATION ============
    @staticmethod
    async def generate_content(db, params: dict) -> dict:
        """Générer du contenu marketing avec IA (simulation)"""
        try:
            content_type = params.get("content_type", "product_promo")
            platform = params.get("platform", "facebook")
            product_name = params.get("product_name", "")
            keywords = params.get("keywords", [])
            tone = params.get("tone", "professional")
            brand_name = params.get("brand_name", "BIONIC HUNT/Chasse")
            
            # Contenu généré (simulation)
            content_templates = {
                "product_promo": f"🎯 {product_name or f'{brand_name} Premium'}\n\nDécouvrez notre solution scientifiquement prouvée. Testé sur le terrain par des professionnels du Québec.\n\n✅ Formule exclusive\n✅ Résultats garantis\n✅ Livraison rapide\n\n👉 Commandez maintenant!",
                "educational": f"📚 Le saviez-vous?\n\nL'orignal peut détecter des odeurs jusqu'à 2km de distance par temps humide. C'est pourquoi le choix de votre attractif est crucial!\n\n🔬 Découvrez notre analyse complète.",
                "seasonal": f"🍂 La saison approche!\n\nPréparez-vous pour la chasse. Nos produits sont prêts, et vous?\n\n📦 Stock limité - Commandez maintenant\n🚚 Livraison express disponible",
                "testimonial": f"⭐⭐⭐⭐⭐\n\n\"Meilleur produit que j'ai utilisé en 20 ans!\"\n\n- Client satisfait\n\nMerci à nos clients pour leur confiance! 🙏",
                "tip": f"💡 Conseil du pro\n\nPour maximiser l'efficacité:\n\n1️⃣ Appliquez contre le vent\n2️⃣ Renouvelez toutes les 48h\n3️⃣ Combinez avec des leurres visuels\n\n🎯",
                "engagement": f"🤔 Question du jour!\n\nQuel est votre gibier préféré cette saison?\n\n🫎 Orignal\n🦌 Chevreuil\n🐻 Ours\n\nRépondez en commentaire! 👇"
            }
            
            hashtags_templates = {
                "product_promo": ["ChasseBionic", "ChasseQuebec", "Orignal", "Chevreuil", "AttractifChasse"],
                "educational": ["ConseilChasse", "ScienceChasse", "Orignal", "Apprentissage"],
                "seasonal": ["SaisonChasse", "ChasseAutomne", "Préparation", "ChasseurQuebec"],
                "testimonial": ["Témoignage", "ClientSatisfait", "ChasseQuebec", "Recommandation"],
                "tip": ["ConseilChasse", "ProTip", "TechniquesChasse", "Expert"],
                "engagement": ["Sondage", "CommunautéChasse", "Votez", "QuestionDuJour"]
            }
            
            content = content_templates.get(content_type, content_templates["product_promo"])
            hashtags = hashtags_templates.get(content_type, hashtags_templates["product_promo"])
            
            # Ajouter keywords aux hashtags
            if keywords:
                hashtags = list(set(hashtags + [k.replace(" ", "") for k in keywords[:3]]))
            
            # Ajuster pour la plateforme
            platform_config = next((p for p in MarketingAdminService.PLATFORMS if p["id"] == platform), None)
            if platform_config and len(content) > platform_config["max_length"]:
                content = content[:platform_config["max_length"] - 3] + "..."
            
            # Log la génération
            await db.marketing_generations.insert_one({
                "id": str(uuid.uuid4()),
                "content_type": content_type,
                "platform": platform,
                "tone": tone,
                "generated_content": content,
                "hashtags": hashtags,
                "created_at": datetime.now(timezone.utc).isoformat()
            })
            
            return {
                "success": True,
                "content": content,
                "hashtags": hashtags,
                "platform": platform,
                "content_type": content_type,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Error in generate_content: {e}")
            return {"success": False, "error": str(e)}
    
    # ============ SEGMENTS MANAGEMENT ============
    @staticmethod
    async def get_segments(db, limit: int = 50) -> dict:
        """Liste des segments d'audience"""
        try:
            segments = await db.marketing_segments.find(
                {}, {"_id": 0}
            ).sort("created_at", -1).limit(limit).to_list(limit)
            
            # Segments par défaut si aucun
            if not segments:
                segments = [
                    {"id": "all_users", "name": "Tous les utilisateurs", "count": 0, "is_default": True},
                    {"id": "premium", "name": "Utilisateurs Premium", "count": 0, "is_default": True},
                    {"id": "hunters", "name": "Chasseurs actifs", "count": 0, "is_default": True},
                    {"id": "landowners", "name": "Propriétaires terriens", "count": 0, "is_default": True},
                    {"id": "inactive", "name": "Utilisateurs inactifs (30j+)", "count": 0, "is_default": True}
                ]
            
            return {
                "success": True,
                "total": len(segments),
                "segments": segments
            }
        except Exception as e:
            logger.error(f"Error in get_segments: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def create_segment(db, segment_data: dict) -> dict:
        """Créer un segment d'audience"""
        try:
            segment = {
                "id": str(uuid.uuid4()),
                "name": segment_data.get("name", "Nouveau segment"),
                "description": segment_data.get("description", ""),
                "criteria": segment_data.get("criteria", {}),
                "count": 0,
                "is_default": False,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            await db.marketing_segments.insert_one(segment)
            if "_id" in segment:
                del segment["_id"]
            
            return {"success": True, "segment": segment}
        except Exception as e:
            logger.error(f"Error in create_segment: {e}")
            return {"success": False, "error": str(e)}
    
    # ============ AUTOMATIONS MANAGEMENT ============
    @staticmethod
    async def get_automations(db, is_active: Optional[bool] = None, limit: int = 50) -> dict:
        """Liste des automations marketing"""
        try:
            query = {}
            if is_active is not None:
                query["is_active"] = is_active
            
            automations = await db.marketing_automations.find(
                query, {"_id": 0}
            ).sort("created_at", -1).limit(limit).to_list(limit)
            
            # Automations par défaut si aucune
            if not automations:
                automations = [
                    {
                        "id": "welcome_series",
                        "name": "Série de bienvenue",
                        "trigger": "user_signup",
                        "actions": ["send_welcome_email", "send_onboarding_tips"],
                        "is_active": False,
                        "runs_count": 0
                    },
                    {
                        "id": "cart_abandonment",
                        "name": "Panier abandonné",
                        "trigger": "cart_abandoned_24h",
                        "actions": ["send_reminder_email"],
                        "is_active": False,
                        "runs_count": 0
                    },
                    {
                        "id": "reengagement",
                        "name": "Réengagement",
                        "trigger": "inactive_30_days",
                        "actions": ["send_reengagement_email", "offer_discount"],
                        "is_active": False,
                        "runs_count": 0
                    }
                ]
            
            return {
                "success": True,
                "total": len(automations),
                "automations": automations
            }
        except Exception as e:
            logger.error(f"Error in get_automations: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def toggle_automation(db, automation_id: str, is_active: bool) -> dict:
        """Activer/désactiver une automation"""
        try:
            result = await db.marketing_automations.update_one(
                {"id": automation_id},
                {"$set": {"is_active": is_active, "updated_at": datetime.now(timezone.utc).isoformat()}}
            )
            
            if result.matched_count == 0:
                return {"success": False, "error": "Automation non trouvée"}
            
            return {"success": True, "automation_id": automation_id, "is_active": is_active}
        except Exception as e:
            logger.error(f"Error in toggle_automation: {e}")
            return {"success": False, "error": str(e)}
    
    # ============ CONTENT TYPES & PLATFORMS ============
    @staticmethod
    async def get_content_types(db) -> dict:
        """Liste des types de contenu disponibles"""
        return {
            "success": True,
            "content_types": MarketingAdminService.CONTENT_TYPES
        }
    
    @staticmethod
    async def get_platforms(db) -> dict:
        """Liste des plateformes disponibles"""
        return {
            "success": True,
            "platforms": MarketingAdminService.PLATFORMS
        }
    
    # ============ HISTORY ============
    @staticmethod
    async def get_publish_history(db, platform: Optional[str] = None, limit: int = 50) -> dict:
        """Historique des publications"""
        try:
            query = {"status": "published"}
            if platform:
                query["platform"] = platform
            
            posts = await db.marketing_posts.find(
                query, {"_id": 0}
            ).sort("published_at", -1).limit(limit).to_list(limit)
            
            return {
                "success": True,
                "total": len(posts),
                "history": posts
            }
        except Exception as e:
            logger.error(f"Error in get_publish_history: {e}")
            return {"success": False, "error": str(e)}


logger.info("MarketingAdminService initialized - Phase 5 Migration")
