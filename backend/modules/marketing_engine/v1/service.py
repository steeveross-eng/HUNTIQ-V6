"""
Marketing Engine V1 - Service Layer
====================================
Service for marketing automation with Tracking Engine integration.
Architecture LEGO V5 - Module isolé.
"""
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
import logging
import uuid

from .models import (
    CampaignCreate, PostCreate, SegmentCreate,
    AutomationCreate, ContentGenerationRequest, ContentGenerationResponse
)

logger = logging.getLogger(__name__)


def serialize_doc(doc: dict) -> dict:
    """Convert MongoDB document to serializable dict"""
    if doc is None:
        return None
    result = dict(doc)
    if "_id" in result:
        result["id"] = str(result.pop("_id"))
    for key, value in result.items():
        if isinstance(value, datetime):
            result[key] = value.isoformat()
        elif isinstance(value, ObjectId):
            result[key] = str(value)
    return result


class MarketingEngineService:
    """Service principal du Marketing Engine"""
    
    # Content templates for AI generation
    CONTENT_TEMPLATES = {
        "product_promo": "🎯 {product}\n\nDécouvrez notre solution scientifiquement prouvée. Testé sur le terrain par des professionnels du Québec.\n\n✅ Formule exclusive\n✅ Résultats garantis\n✅ Livraison rapide\n\n👉 Commandez maintenant!",
        "educational": "📚 Le saviez-vous?\n\nL'orignal peut détecter des odeurs jusqu'à 2km de distance par temps humide. C'est pourquoi le choix de votre attractif est crucial!\n\n🔬 Découvrez notre analyse complète.",
        "seasonal": "🍂 La saison approche!\n\nPréparez-vous pour la chasse. Nos produits sont prêts, et vous?\n\n📦 Stock limité - Commandez maintenant\n🚚 Livraison express disponible",
        "testimonial": "⭐⭐⭐⭐⭐\n\n\"Meilleur produit que j'ai utilisé en 20 ans!\"\n\n- Client satisfait\n\nMerci à nos clients pour leur confiance! 🙏",
        "tip": "💡 Conseil du pro\n\nPour maximiser l'efficacité:\n\n1️⃣ Appliquez contre le vent\n2️⃣ Renouvelez toutes les 48h\n3️⃣ Combinez avec des leurres visuels\n\n🎯",
        "engagement": "🤔 Question du jour!\n\nQuel est votre gibier préféré cette saison?\n\n🫎 Orignal\n🦌 Chevreuil\n🐻 Ours\n\nRépondez en commentaire! 👇"
    }
    
    HASHTAGS_TEMPLATES = {
        "product_promo": ["ChasseBionic", "ChasseQuebec", "Orignal", "Chevreuil", "AttractifChasse"],
        "educational": ["ConseilChasse", "ScienceChasse", "Orignal", "Apprentissage"],
        "seasonal": ["SaisonChasse", "ChasseAutomne", "Préparation", "ChasseurQuebec"],
        "testimonial": ["Témoignage", "ClientSatisfait", "ChasseQuebec", "Recommandation"],
        "tip": ["ConseilChasse", "ProTip", "TechniquesChasse", "Expert"],
        "engagement": ["Sondage", "CommunautéChasse", "Votez", "QuestionDuJour"]
    }
    
    PLATFORM_MAX_LENGTHS = {
        "facebook": 63206,
        "instagram": 2200,
        "twitter": 280,
        "linkedin": 3000
    }
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.campaigns = db['marketing_campaigns']
        self.posts = db['marketing_posts']
        self.segments = db['marketing_segments']
        self.automations = db['marketing_automations']
        self.triggers = db['marketing_behavioral_triggers']
        self.executions = db['marketing_trigger_executions']
        self.tracking_events = db['tracking_events']
    
    # ============================================
    # DASHBOARD & STATS
    # ============================================
    
    async def get_dashboard_stats(self) -> dict:
        """Get marketing dashboard statistics"""
        try:
            # Campaigns
            total_campaigns = await self.campaigns.count_documents({})
            active_campaigns = await self.campaigns.count_documents({"status": "active"})
            
            # Posts
            total_posts = await self.posts.count_documents({})
            published_posts = await self.posts.count_documents({"status": "published"})
            scheduled_posts = await self.posts.count_documents({"status": "scheduled"})
            
            # Engagement (last 30 days)
            thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
            recent_posts = await self.posts.find({
                "published_at": {"$gte": thirty_days_ago.isoformat()}
            }).to_list(1000)
            
            total_impressions = sum(p.get("impressions", 0) for p in recent_posts)
            total_clicks = sum(p.get("clicks", 0) for p in recent_posts)
            
            # Segments & Automations
            total_segments = await self.segments.count_documents({})
            total_automations = await self.automations.count_documents({})
            active_automations = await self.automations.count_documents({"is_active": True})
            
            # By platform
            by_platform = {}
            for platform in ["facebook", "instagram", "twitter", "linkedin"]:
                by_platform[platform] = await self.posts.count_documents({"platform": platform})
            
            # Behavioral triggers
            active_triggers = await self.triggers.count_documents({"is_active": True})
            recent_executions = await self.executions.count_documents({
                "executed_at": {"$gte": thirty_days_ago.isoformat()}
            })
            
            return {
                "campaigns": {
                    "total": total_campaigns,
                    "active": active_campaigns
                },
                "posts": {
                    "total": total_posts,
                    "published": published_posts,
                    "scheduled": scheduled_posts
                },
                "engagement_30d": {
                    "impressions": total_impressions,
                    "clicks": total_clicks,
                    "ctr": round((total_clicks / max(total_impressions, 1)) * 100, 2)
                },
                "segments": {"total": total_segments},
                "automations": {
                    "total": total_automations,
                    "active": active_automations
                },
                "behavioral": {
                    "active_triggers": active_triggers,
                    "executions_30d": recent_executions
                },
                "by_platform": by_platform
            }
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {e}")
            raise
    
    # ============================================
    # CAMPAIGNS
    # ============================================
    
    async def create_campaign(self, data: CampaignCreate) -> dict:
        """Create a new campaign"""
        campaign = {
            "id": str(uuid.uuid4()),
            "name": data.name,
            "description": data.description,
            "type": data.type,
            "status": "draft",
            "start_date": data.start_date,
            "end_date": data.end_date,
            "target_platforms": data.target_platforms,
            "target_segment": data.target_segment,
            "budget": data.budget,
            "goals": data.goals,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await self.campaigns.insert_one(campaign)
        campaign.pop("_id", None)
        return campaign
    
    async def get_campaigns(self, status: Optional[str] = None, limit: int = 50) -> List[dict]:
        """Get campaigns with optional status filter"""
        query = {}
        if status and status != "all":
            query["status"] = status
        
        campaigns = await self.campaigns.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
        return campaigns
    
    async def get_campaign(self, campaign_id: str) -> Optional[dict]:
        """Get a single campaign"""
        campaign = await self.campaigns.find_one({"id": campaign_id}, {"_id": 0})
        return campaign
    
    async def update_campaign_status(self, campaign_id: str, status: str) -> bool:
        """Update campaign status"""
        update = {"status": status, "updated_at": datetime.now(timezone.utc).isoformat()}
        if status == "active":
            update["activated_at"] = datetime.now(timezone.utc).isoformat()
        
        result = await self.campaigns.update_one({"id": campaign_id}, {"$set": update})
        return result.modified_count > 0
    
    async def delete_campaign(self, campaign_id: str) -> bool:
        """Delete a campaign and its posts"""
        result = await self.campaigns.delete_one({"id": campaign_id})
        await self.posts.delete_many({"campaign_id": campaign_id})
        return result.deleted_count > 0
    
    # ============================================
    # POSTS
    # ============================================
    
    async def create_post(self, data: PostCreate) -> dict:
        """Create a new post"""
        post = {
            "id": str(uuid.uuid4()),
            "campaign_id": data.campaign_id,
            "platform": data.platform,
            "content": data.content,
            "hashtags": data.hashtags,
            "media_urls": data.media_urls,
            "content_type": data.content_type,
            "status": data.status,
            "scheduled_at": data.scheduled_at,
            "impressions": 0,
            "clicks": 0,
            "engagement": 0,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await self.posts.insert_one(post)
        post.pop("_id", None)
        return post
    
    async def get_posts(self, status: Optional[str] = None, platform: Optional[str] = None, limit: int = 50) -> List[dict]:
        """Get posts with filters"""
        query = {}
        if status and status != "all":
            query["status"] = status
        if platform and platform != "all":
            query["platform"] = platform
        
        posts = await self.posts.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
        return posts
    
    async def schedule_post(self, post_id: str, scheduled_at: str) -> bool:
        """Schedule a post"""
        result = await self.posts.update_one(
            {"id": post_id},
            {"$set": {"status": "scheduled", "scheduled_at": scheduled_at}}
        )
        return result.modified_count > 0
    
    async def publish_post(self, post_id: str) -> dict:
        """Publish a post immediately"""
        now = datetime.now(timezone.utc).isoformat()
        result = await self.posts.update_one(
            {"id": post_id},
            {"$set": {"status": "published", "published_at": now}}
        )
        return {
            "success": result.modified_count > 0,
            "message": "Publication simulée (connectez vos réseaux sociaux pour publier réellement)"
        }
    
    async def delete_post(self, post_id: str) -> bool:
        """Delete a post"""
        result = await self.posts.delete_one({"id": post_id})
        return result.deleted_count > 0
    
    # ============================================
    # CONTENT GENERATION
    # ============================================
    
    async def generate_content(self, request: ContentGenerationRequest) -> ContentGenerationResponse:
        """Generate marketing content"""
        content_type = request.content_type.value if hasattr(request.content_type, 'value') else request.content_type
        platform = request.platform.value if hasattr(request.platform, 'value') else request.platform
        
        # Get template
        template = self.CONTENT_TEMPLATES.get(content_type, self.CONTENT_TEMPLATES["product_promo"])
        content = template.format(product=request.product_name or f"{request.brand_name} Premium")
        
        # Get hashtags
        hashtags = self.HASHTAGS_TEMPLATES.get(content_type, self.HASHTAGS_TEMPLATES["product_promo"]).copy()
        if request.keywords:
            hashtags.extend([k.replace(" ", "") for k in request.keywords[:3]])
        hashtags = list(set(hashtags))
        
        # Truncate for platform
        max_length = self.PLATFORM_MAX_LENGTHS.get(platform, 2200)
        if len(content) > max_length:
            content = content[:max_length - 3] + "..."
        
        return ContentGenerationResponse(
            content=content,
            hashtags=hashtags,
            platform=platform,
            content_type=content_type,
            generated_at=datetime.now(timezone.utc)
        )
    
    # ============================================
    # SEGMENTS
    # ============================================
    
    async def get_segments(self) -> List[dict]:
        """Get all segments"""
        segments = await self.segments.find({}, {"_id": 0}).sort("created_at", -1).to_list(100)
        
        if not segments:
            # Default segments
            segments = [
                {"id": "all_users", "name": "Tous les utilisateurs", "count": 0, "is_default": True},
                {"id": "premium", "name": "Utilisateurs Premium", "count": 0, "is_default": True},
                {"id": "hunters", "name": "Chasseurs actifs", "count": 0, "is_default": True},
                {"id": "landowners", "name": "Propriétaires terriens", "count": 0, "is_default": True},
                {"id": "inactive", "name": "Utilisateurs inactifs (30j+)", "count": 0, "is_default": True}
            ]
        
        return segments
    
    async def create_segment(self, data: SegmentCreate) -> dict:
        """Create a new segment"""
        segment = {
            "id": str(uuid.uuid4()),
            "name": data.name,
            "description": data.description,
            "criteria": data.criteria,
            "is_dynamic": data.is_dynamic,
            "count": 0,
            "is_default": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await self.segments.insert_one(segment)
        segment.pop("_id", None)
        return segment
    
    # ============================================
    # AUTOMATIONS
    # ============================================
    
    async def get_automations(self, is_active: Optional[bool] = None) -> List[dict]:
        """Get automations"""
        query = {}
        if is_active is not None:
            query["is_active"] = is_active
        
        automations = await self.automations.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
        
        if not automations:
            # Default automations
            automations = [
                {
                    "id": "welcome_series",
                    "name": "Série de bienvenue",
                    "trigger": "user_signup",
                    "actions": [{"type": "send_email", "config": {"template": "welcome"}}],
                    "is_active": False,
                    "runs_count": 0
                },
                {
                    "id": "cart_abandonment",
                    "name": "Panier abandonné",
                    "trigger": "cart_abandoned_24h",
                    "actions": [{"type": "send_email", "config": {"template": "cart_reminder"}}],
                    "is_active": False,
                    "runs_count": 0
                },
                {
                    "id": "reengagement",
                    "name": "Réengagement",
                    "trigger": "inactive_30_days",
                    "actions": [{"type": "send_email", "config": {"template": "reengagement"}}, {"type": "offer_discount", "config": {"amount": 10}}],
                    "is_active": False,
                    "runs_count": 0
                }
            ]
        
        return automations
    
    async def create_automation(self, data: AutomationCreate) -> dict:
        """Create a new automation"""
        automation = {
            "id": str(uuid.uuid4()),
            "name": data.name,
            "description": data.description,
            "trigger": data.trigger,
            "trigger_config": data.trigger_config,
            "actions": data.actions,
            "is_active": False,
            "runs_count": 0,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await self.automations.insert_one(automation)
        automation.pop("_id", None)
        return automation
    
    async def toggle_automation(self, automation_id: str, is_active: bool) -> bool:
        """Toggle automation status"""
        result = await self.automations.update_one(
            {"id": automation_id},
            {"$set": {"is_active": is_active, "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
        return result.modified_count > 0
    
    # ============================================
    # BEHAVIORAL TRIGGERS (Tracking Engine Integration)
    # ============================================
    
    async def create_behavioral_trigger(self, automation_id: str, event_type: str, 
                                        event_name: Optional[str] = None,
                                        page_url_pattern: Optional[str] = None,
                                        min_occurrences: int = 1,
                                        time_window_hours: int = 24) -> dict:
        """Create a behavioral trigger linked to Tracking Engine"""
        trigger = {
            "id": str(uuid.uuid4()),
            "automation_id": automation_id,
            "event_type": event_type,
            "event_name": event_name,
            "page_url_pattern": page_url_pattern,
            "min_occurrences": min_occurrences,
            "time_window_hours": time_window_hours,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await self.triggers.insert_one(trigger)
        trigger.pop("_id", None)
        
        logger.info(f"Created behavioral trigger: {trigger['id']} for automation {automation_id}")
        return trigger
    
    async def get_behavioral_triggers(self, automation_id: Optional[str] = None) -> List[dict]:
        """Get behavioral triggers"""
        query = {}
        if automation_id:
            query["automation_id"] = automation_id
        
        triggers = await self.triggers.find(query, {"_id": 0}).to_list(100)
        return triggers
    
    async def check_and_execute_triggers(self, user_id: str, session_id: str) -> List[dict]:
        """Check tracking events and execute matching triggers"""
        executed = []
        
        # Get active triggers
        active_triggers = await self.triggers.find({"is_active": True}, {"_id": 0}).to_list(100)
        
        for trigger in active_triggers:
            # Build query for tracking events
            time_window = datetime.now(timezone.utc) - timedelta(hours=trigger.get("time_window_hours", 24))
            
            event_query = {
                "user_id": user_id,
                "timestamp": {"$gte": time_window},
                "event_type": trigger.get("event_type")
            }
            
            if trigger.get("event_name"):
                event_query["event_name"] = trigger["event_name"]
            
            if trigger.get("page_url_pattern"):
                event_query["page_url"] = {"$regex": trigger["page_url_pattern"], "$options": "i"}
            
            # Count matching events
            event_count = await self.tracking_events.count_documents(event_query)
            
            if event_count >= trigger.get("min_occurrences", 1):
                # Check if already executed recently
                recent_execution = await self.executions.find_one({
                    "trigger_id": trigger["id"],
                    "user_id": user_id,
                    "executed_at": {"$gte": time_window.isoformat()}
                })
                
                if not recent_execution:
                    # Execute trigger
                    execution = {
                        "id": str(uuid.uuid4()),
                        "trigger_id": trigger["id"],
                        "automation_id": trigger["automation_id"],
                        "user_id": user_id,
                        "session_id": session_id,
                        "event_count": event_count,
                        "executed_at": datetime.now(timezone.utc).isoformat(),
                        "status": "executed"
                    }
                    
                    await self.executions.insert_one(execution)
                    
                    # Increment automation runs
                    await self.automations.update_one(
                        {"id": trigger["automation_id"]},
                        {"$inc": {"runs_count": 1}, "$set": {"last_run_at": datetime.now(timezone.utc).isoformat()}}
                    )
                    
                    execution.pop("_id", None)
                    executed.append(execution)
                    
                    logger.info(f"Executed trigger {trigger['id']} for user {user_id}")
        
        return executed
    
    async def get_trigger_executions(self, automation_id: Optional[str] = None, 
                                      user_id: Optional[str] = None,
                                      days: int = 30) -> List[dict]:
        """Get trigger execution history"""
        query = {}
        if automation_id:
            query["automation_id"] = automation_id
        if user_id:
            query["user_id"] = user_id
        
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        query["executed_at"] = {"$gte": start_date.isoformat()}
        
        executions = await self.executions.find(query, {"_id": 0}).sort("executed_at", -1).to_list(500)
        return executions
    
    # ============================================
    # ANALYTICS
    # ============================================
    
    async def get_campaign_analytics(self, campaign_id: str) -> dict:
        """Get analytics for a campaign"""
        campaign = await self.get_campaign(campaign_id)
        if not campaign:
            return {"error": "Campaign not found"}
        
        posts = await self.posts.find({"campaign_id": campaign_id}, {"_id": 0}).to_list(100)
        
        total_impressions = sum(p.get("impressions", 0) for p in posts)
        total_clicks = sum(p.get("clicks", 0) for p in posts)
        total_engagement = sum(p.get("engagement", 0) for p in posts)
        
        by_platform = {}
        for post in posts:
            platform = post.get("platform", "unknown")
            if platform not in by_platform:
                by_platform[platform] = {"posts": 0, "impressions": 0, "clicks": 0}
            by_platform[platform]["posts"] += 1
            by_platform[platform]["impressions"] += post.get("impressions", 0)
            by_platform[platform]["clicks"] += post.get("clicks", 0)
        
        return {
            "campaign": campaign,
            "total_posts": len(posts),
            "total_impressions": total_impressions,
            "total_clicks": total_clicks,
            "total_engagement": total_engagement,
            "ctr": round((total_clicks / max(total_impressions, 1)) * 100, 2),
            "by_platform": by_platform
        }
