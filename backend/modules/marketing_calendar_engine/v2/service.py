"""
Marketing Calendar Engine V2 - Campaign Service
================================================
Service principal de gestion des campagnes marketing.
Architecture LEGO V5 - Module isolé.
"""
import time
import uuid
import logging
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from dotenv import load_dotenv

from .models import (
    Campaign, CampaignStatus, AudienceType, GeneratedContent, GeneratedVisual, CampaignPreview,
    CalendarDay, MarketingCalendar, PlatformFormat,
    CampaignGenerationRequest, CampaignGenerationResponse
)
from .ai_service import AIContentService, AIImageService

load_dotenv()
logger = logging.getLogger(__name__)

# SLA: 60 seconds max
SLA_MAX_GENERATION_TIME_MS = 60000


class CampaignService:
    """Service de gestion des campagnes marketing"""
    
    # Templates Premium prédéfinis
    PREMIUM_TEMPLATES = {
        "hero_hunting": {
            "id": "tpl_hero_hunting",
            "name": "Hero - Chasseur Premium",
            "description": "Template hero avec chasseur en action",
            "category": "hero",
            "formats": ["meta_feed", "youtube_thumbnail"],
            "css_animation": "fade-in-up",
            "color_scheme": {
                "primary": "#f5a623",
                "secondary": "#1a1a2e",
                "accent": "#2d5a27"
            },
            "placeholders": ["headline", "subheadline", "cta"]
        },
        "feature_bionic": {
            "id": "tpl_feature_bionic",
            "name": "Feature - Technologie BIONIC",
            "description": "Mise en avant des fonctionnalités IA",
            "category": "feature",
            "formats": ["meta_carousel", "meta_feed"],
            "css_animation": "slide-in-right",
            "color_scheme": {
                "primary": "#f5a623",
                "secondary": "#0a0a0f",
                "accent": "#00d4ff"
            },
            "placeholders": ["headline", "feature_list", "cta"]
        },
        "testimonial_hunter": {
            "id": "tpl_testimonial",
            "name": "Témoignage Chasseur",
            "description": "Format témoignage avec citation",
            "category": "testimonial",
            "formats": ["meta_story", "meta_feed"],
            "css_animation": "fade-in",
            "color_scheme": {
                "primary": "#ffffff",
                "secondary": "#1a1a2e",
                "accent": "#f5a623"
            },
            "placeholders": ["quote", "author", "image"]
        },
        "cta_urgent": {
            "id": "tpl_cta_urgent",
            "name": "CTA - Offre Limitée",
            "description": "Appel à l'action avec urgence",
            "category": "cta",
            "formats": ["meta_feed", "meta_story"],
            "css_animation": "pulse",
            "color_scheme": {
                "primary": "#ff4444",
                "secondary": "#1a1a2e",
                "accent": "#f5a623"
            },
            "placeholders": ["headline", "countdown", "cta"]
        },
        "product_showcase": {
            "id": "tpl_product",
            "name": "Showcase Produit",
            "description": "Présentation produit/fonctionnalité",
            "category": "product",
            "formats": ["meta_carousel", "youtube_thumbnail"],
            "css_animation": "zoom-in",
            "color_scheme": {
                "primary": "#f5a623",
                "secondary": "#0f0f1a",
                "accent": "#4ade80"
            },
            "placeholders": ["headline", "features", "cta", "image"]
        }
    }
    
    # Animations Lottie prédéfinies
    LOTTIE_ANIMATIONS = {
        "hunting_scope": "https://assets.lottiefiles.com/packages/lf20_scope.json",
        "map_marker": "https://assets.lottiefiles.com/packages/lf20_marker.json",
        "success_check": "https://assets.lottiefiles.com/packages/lf20_check.json",
        "loading_compass": "https://assets.lottiefiles.com/packages/lf20_compass.json",
        "arrow_down": "https://assets.lottiefiles.com/packages/lf20_arrow.json"
    }
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.campaigns_collection = db.marketing_campaigns
        self.ai_content = AIContentService()
        self.ai_image = AIImageService()
    
    async def generate_campaign(
        self,
        request: CampaignGenerationRequest
    ) -> CampaignGenerationResponse:
        """
        Génère une campagne marketing complète.
        SLA: < 60 secondes.
        """
        start_time = time.time()
        
        try:
            # 1. Générer le contenu textuel (GPT-5.2)
            content_result = await self.ai_content.generate_marketing_content(
                audience_type=request.audience_type.value,
                tone=request.tone.value,
                product_focus=request.product_focus,
                custom_keywords=request.custom_keywords,
                platform=request.platforms[0] if request.platforms else "meta_feed"
            )
            
            generated_content = GeneratedContent(
                headline=content_result.get("headline", "BIONIC HUNT/Chasse Premium"),
                subheadline=content_result.get("subheadline"),
                body_text=content_result.get("body_text"),
                cta_text=content_result.get("cta_text", "Découvrir"),
                hashtags=content_result.get("hashtags", []),
                keywords=content_result.get("keywords", []),
                tone=request.tone,
                audience_type=request.audience_type,
                generation_time_ms=content_result.get("generation_time_ms", 0)
            )
            
            # 2. Générer les visuels
            visuals = []
            for platform in request.platforms[:3]:  # Max 3 plateformes pour SLA
                visual = await self._generate_visual(
                    headline=generated_content.headline,
                    audience_type=request.audience_type,
                    platform_format=platform,
                    use_ai=request.use_ai_images
                )
                visuals.append(visual)
            
            # 3. Générer les prévisualisations
            previews = []
            for i, platform in enumerate(request.platforms[:3]):
                preview = CampaignPreview(
                    campaign_id="",  # Will be set after save
                    platform=platform,
                    format=PlatformFormat(platform) if platform in [e.value for e in PlatformFormat] else PlatformFormat.META_FEED,
                    content=generated_content,
                    visual=visuals[i] if i < len(visuals) else visuals[0],
                    mock_engagement={
                        "estimated_reach": self._estimate_reach(request.audience_type),
                        "estimated_clicks": self._estimate_clicks(request.audience_type),
                        "estimated_conversions": self._estimate_conversions(request.audience_type)
                    }
                )
                previews.append(preview)
            
            # 4. Créer la campagne
            generation_time_ms = int((time.time() - start_time) * 1000)
            
            campaign = Campaign(
                id=str(uuid.uuid4()),
                name=request.name,
                scheduled_date=request.scheduled_date,
                status=CampaignStatus.DRAFT,
                audience_type=request.audience_type,
                platforms=request.platforms,
                tone=request.tone,
                content=generated_content,
                visuals=visuals,
                custom_message=request.custom_message,
                previews=previews,
                generation_time_ms=generation_time_ms
            )
            
            # Update preview campaign_ids
            for preview in campaign.previews:
                preview.campaign_id = campaign.id
            
            # 5. Sauvegarder
            await self._save_campaign(campaign)
            
            # 6. Vérifier SLA
            sla_met = generation_time_ms < SLA_MAX_GENERATION_TIME_MS
            
            logger.info(f"Campaign generated in {generation_time_ms}ms (SLA: {'✅' if sla_met else '❌'})")
            
            return CampaignGenerationResponse(
                success=True,
                campaign=campaign,
                generation_time_ms=generation_time_ms,
                sla_met=sla_met
            )
            
        except Exception as e:
            logger.error(f"Campaign generation failed: {e}")
            generation_time_ms = int((time.time() - start_time) * 1000)
            
            return CampaignGenerationResponse(
                success=False,
                campaign=None,
                generation_time_ms=generation_time_ms,
                sla_met=False,
                error=str(e)
            )
    
    async def _generate_visual(
        self,
        headline: str,
        audience_type: AudienceType,
        platform_format: str,
        use_ai: bool = False
    ) -> GeneratedVisual:
        """Génère un visuel (template ou IA)"""
        start_time = time.time()
        
        if use_ai:
            # Génération IA
            result = await self.ai_image.generate_marketing_image(
                headline=headline,
                audience_type=audience_type.value,
                platform_format=platform_format
            )
            
            return GeneratedVisual(
                id=str(uuid.uuid4()),
                template_id="ai_generated",
                format=PlatformFormat(platform_format) if platform_format in [e.value for e in PlatformFormat] else PlatformFormat.META_FEED,
                image_base64=result.get("image_base64") if result.get("success") else None,
                ai_generated=True,
                generation_time_ms=result.get("generation_time_ms", 0)
            )
        else:
            # Template Premium
            template = self._select_template(audience_type, platform_format)
            
            return GeneratedVisual(
                id=str(uuid.uuid4()),
                template_id=template["id"],
                format=PlatformFormat(platform_format) if platform_format in [e.value for e in PlatformFormat] else PlatformFormat.META_FEED,
                css_styles=self._generate_css_styles(template),
                lottie_json={"animation": self.LOTTIE_ANIMATIONS.get("map_marker")},
                ai_generated=False,
                generation_time_ms=int((time.time() - start_time) * 1000)
            )
    
    def _select_template(self, audience_type: AudienceType, platform_format: str) -> Dict:
        """Sélectionne le template optimal"""
        # Mapping audience -> template category
        audience_templates = {
            AudienceType.FABRICANTS: "product_showcase",
            AudienceType.AFFILIATION: "cta_urgent",
            AudienceType.PARTENARIATS: "hero_hunting",
            AudienceType.PROSPECTS: "feature_bionic",
            AudienceType.AUDIENCES_SPECIALISEES: "testimonial_hunter",
            AudienceType.GENERAL: "hero_hunting"
        }
        
        template_key = audience_templates.get(audience_type, "hero_hunting")
        return self.PREMIUM_TEMPLATES.get(template_key, self.PREMIUM_TEMPLATES["hero_hunting"])
    
    def _generate_css_styles(self, template: Dict) -> str:
        """Génère les styles CSS pour le template"""
        colors = template.get("color_scheme", {})
        animation = template.get("css_animation", "fade-in")
        
        return f"""
.campaign-visual {{
    background: linear-gradient(135deg, {colors.get('secondary', '#1a1a2e')}, {colors.get('primary', '#f5a623')}20);
    border: 2px solid {colors.get('primary', '#f5a623')};
    border-radius: 12px;
    animation: {animation} 0.6s ease-out;
}}
.campaign-headline {{
    color: {colors.get('primary', '#f5a623')};
    font-weight: 700;
}}
.campaign-cta {{
    background: {colors.get('primary', '#f5a623')};
    color: {colors.get('secondary', '#1a1a2e')};
}}
@keyframes fade-in {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
@keyframes fade-in-up {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
@keyframes slide-in-right {{ from {{ transform: translateX(100%); }} to {{ transform: translateX(0); }} }}
@keyframes pulse {{ 0%, 100% {{ transform: scale(1); }} 50% {{ transform: scale(1.05); }} }}
@keyframes zoom-in {{ from {{ transform: scale(0.8); opacity: 0; }} to {{ transform: scale(1); opacity: 1; }} }}
"""
    
    def _estimate_reach(self, audience_type: AudienceType) -> int:
        """Estime la portée selon l'audience"""
        reach_multipliers = {
            AudienceType.GENERAL: 10000,
            AudienceType.PROSPECTS: 5000,
            AudienceType.AUDIENCES_SPECIALISEES: 2500,
            AudienceType.FABRICANTS: 500,
            AudienceType.AFFILIATION: 1000,
            AudienceType.PARTENARIATS: 300
        }
        base = reach_multipliers.get(audience_type, 5000)
        import random
        return base + random.randint(-base//4, base//4)
    
    def _estimate_clicks(self, audience_type: AudienceType) -> int:
        """Estime les clics selon l'audience"""
        return int(self._estimate_reach(audience_type) * 0.035)  # 3.5% CTR
    
    def _estimate_conversions(self, audience_type: AudienceType) -> int:
        """Estime les conversions selon l'audience"""
        return int(self._estimate_clicks(audience_type) * 0.12)  # 12% conversion
    
    async def _save_campaign(self, campaign: Campaign) -> str:
        """Sauvegarde une campagne en base"""
        doc = campaign.dict()
        doc["_id"] = campaign.id
        
        await self.campaigns_collection.update_one(
            {"_id": campaign.id},
            {"$set": doc},
            upsert=True
        )
        
        return campaign.id
    
    async def get_calendar(self, days_ahead: int = 60) -> MarketingCalendar:
        """Récupère le calendrier marketing sur N jours"""
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=days_ahead)
        
        # Récupérer les campagnes planifiées
        campaigns = await self.campaigns_collection.find({
            "scheduled_date": {
                "$gte": start_date,
                "$lte": end_date
            }
        }).to_list(500)
        
        # Construire le calendrier
        calendar_days = []
        current_date = start_date
        
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            
            # Filtrer les campagnes du jour
            day_campaigns = [
                Campaign(**c) for c in campaigns 
                if c.get("scheduled_date", datetime.min).strftime("%Y-%m-%d") == date_str
            ]
            
            # Ajouter des événements/suggestions
            events = self._get_events_for_date(current_date)
            suggestions = self._get_suggestions_for_date(current_date)
            
            calendar_days.append(CalendarDay(
                date=date_str,
                campaigns=day_campaigns,
                events=events,
                suggestions=suggestions
            ))
            
            current_date += timedelta(days=1)
        
        # Statistiques
        all_campaigns = [c for day in calendar_days for c in day.campaigns]
        
        return MarketingCalendar(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            days=calendar_days,
            total_campaigns=len(all_campaigns),
            total_scheduled=len([c for c in all_campaigns if c.status == CampaignStatus.SCHEDULED]),
            total_draft=len([c for c in all_campaigns if c.status == CampaignStatus.DRAFT])
        )
    
    def _get_events_for_date(self, date: datetime) -> List[str]:
        """Retourne les événements pour une date"""
        events = []
        
        # Saisons de chasse (exemples pour le Québec)
        month = date.month
        if month == 9:
            events.append("🦌 Début saison cerf (arc)")
        elif month == 10:
            events.append("🦌 Saison cerf arme à feu")
        elif month == 11:
            events.append("🦃 Saison dindon automne")
        elif month == 4:
            events.append("🦃 Saison dindon printemps")
        elif month == 5:
            events.append("🐻 Saison ours printemps")
        
        # Jours spéciaux
        if date.weekday() == 4:  # Vendredi
            events.append("📊 Pic engagement social")
        
        return events
    
    def _get_suggestions_for_date(self, date: datetime) -> List[str]:
        """Suggestions de contenu pour une date"""
        suggestions = []
        
        weekday = date.weekday()
        if weekday == 0:  # Lundi
            suggestions.append("💡 Motivation Monday: Tips de la semaine")
        elif weekday == 2:  # Mercredi
            suggestions.append("💡 Feature Focus: Highlight fonctionnalité")
        elif weekday == 4:  # Vendredi
            suggestions.append("💡 Weekend Ready: Préparez votre sortie")
        
        return suggestions
    
    async def get_campaign(self, campaign_id: str) -> Optional[Campaign]:
        """Récupère une campagne par ID"""
        doc = await self.campaigns_collection.find_one({"_id": campaign_id})
        if doc:
            return Campaign(**doc)
        return None
    
    async def update_campaign(self, campaign_id: str, updates: Dict) -> bool:
        """Met à jour une campagne"""
        updates["updated_at"] = datetime.utcnow()
        result = await self.campaigns_collection.update_one(
            {"_id": campaign_id},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    async def delete_campaign(self, campaign_id: str) -> bool:
        """Supprime une campagne"""
        result = await self.campaigns_collection.delete_one({"_id": campaign_id})
        return result.deleted_count > 0
    
    async def schedule_campaign(self, campaign_id: str) -> bool:
        """Planifie une campagne (passe de DRAFT à SCHEDULED)"""
        return await self.update_campaign(campaign_id, {"status": CampaignStatus.SCHEDULED.value})
    
    async def get_campaigns_by_audience(self, audience_type: AudienceType) -> List[Campaign]:
        """Récupère les campagnes par type d'audience"""
        docs = await self.campaigns_collection.find({
            "audience_type": audience_type.value
        }).to_list(100)
        
        return [Campaign(**doc) for doc in docs]
