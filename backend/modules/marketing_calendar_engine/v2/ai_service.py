"""
Marketing Calendar Engine V2 - AI Content Service
==================================================
Service de génération de contenu marketing via GPT-5.2.
Architecture LEGO V5 - Module isolé.
"""
import os
import time
import logging
from typing import Optional, List, Dict
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class AIContentService:
    """Service de génération de contenu marketing IA"""
    
    # Prompts système par type d'audience
    AUDIENCE_PROMPTS = {
        "fabricants": """Tu es un expert en communication B2B pour l'industrie de la chasse et du plein air.
Tu crées des messages premium pour des fabricants et marques d'équipement.
Ton: professionnel, exclusif, orienté partenariat stratégique.
Mets en avant: ROI, visibilité, audience qualifiée, innovation BIONIC.""",
        
        "affiliation": """Tu es un expert en marketing d'affiliation pour le secteur outdoor/chasse.
Tu crées des messages attractifs pour recruter des affiliés.
Ton: opportunité, revenus passifs, communauté, simplicité.
Mets en avant: commissions, support, outils marketing, succès stories.""",
        
        "partenariats": """Tu es un expert en développement de partenariats stratégiques.
Tu crées des messages pour établir des collaborations durables.
Ton: win-win, synergie, co-création, valeur partagée.
Mets en avant: complémentarité, audience, innovation, prestige.""",
        
        "prospects": """Tu es un expert en conversion de prospects pour une app de chasse premium.
Tu crées des messages persuasifs pour convertir les chasseurs intéressés.
Ton: urgence mesurée, bénéfices concrets, témoignages, exclusivité.
Mets en avant: fonctionnalités uniques, résultats, communauté, essai gratuit.""",
        
        "audiences_specialisees": """Tu es un expert en marketing de niche pour chasseurs passionnés.
Tu crées des messages ciblés pour des segments spécifiques (archers, trappeurs, etc.).
Ton: expertise, passion partagée, communauté, authenticité.
Mets en avant: features spécifiques, témoignages experts, contenu exclusif.""",
        
        "general": """Tu es un expert en marketing digital pour une application de chasse intelligente.
Tu crées des messages engageants pour une audience large de chasseurs.
Ton: enthousiaste, accessible, inspirant, moderne.
Mets en avant: innovation BIONIC, simplicité, résultats, communauté."""
    }
    
    # Prompts par ton
    TONE_MODIFIERS = {
        "professional": "Utilise un vocabulaire professionnel et des données chiffrées.",
        "premium": "Utilise un vocabulaire élégant, exclusif, haut de gamme.",
        "friendly": "Utilise un ton chaleureux, accessible, conversationnel.",
        "urgent": "Crée un sentiment d'urgence avec des offres limitées.",
        "exclusive": "Mets en avant l'exclusivité, l'accès privilégié, le VIP.",
        "educational": "Apporte de la valeur éducative, des conseils, du savoir-faire."
    }
    
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment")
    
    async def generate_marketing_content(
        self,
        audience_type: str,
        tone: str,
        product_focus: Optional[str] = None,
        custom_keywords: List[str] = None,
        platform: str = "meta_feed"
    ) -> Dict:
        """
        Génère du contenu marketing personnalisé.
        
        Returns:
            Dict avec headline, subheadline, body_text, cta_text, hashtags, keywords
        """
        start_time = time.time()
        
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            
            # Construire le prompt système
            system_prompt = self._build_system_prompt(audience_type, tone)
            
            # Construire le prompt utilisateur
            user_prompt = self._build_user_prompt(
                audience_type, tone, product_focus, custom_keywords, platform
            )
            
            # Initialiser le chat GPT-5.2
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"marketing_{int(time.time())}",
                system_message=system_prompt
            ).with_model("openai", "gpt-5.2")
            
            # Envoyer le message
            user_message = UserMessage(text=user_prompt)
            response = await chat.send_message(user_message)
            
            # Parser la réponse
            content = self._parse_response(response, audience_type, tone)
            
            generation_time = int((time.time() - start_time) * 1000)
            content["generation_time_ms"] = generation_time
            
            logger.info(f"Content generated in {generation_time}ms for {audience_type}")
            
            return content
            
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            # Fallback sur du contenu par défaut
            return self._get_fallback_content(audience_type, tone)
    
    def _build_system_prompt(self, audience_type: str, tone: str) -> str:
        """Construit le prompt système"""
        base_prompt = self.AUDIENCE_PROMPTS.get(audience_type, self.AUDIENCE_PROMPTS["general"])
        tone_modifier = self.TONE_MODIFIERS.get(tone, self.TONE_MODIFIERS["premium"])
        
        return f"""{base_prompt}

{tone_modifier}

Contexte: BIONIC HUNT/Chasse est une application de chasse intelligente utilisant la technologie BIONIC™.
Fonctionnalités clés: cartographie avancée, scoring de waypoints, prévisions de succès, IA prédictive.
Valeurs: Innovation, Performance, Communauté, Respect de la nature.

Tu dois TOUJOURS répondre en JSON valide avec cette structure exacte:
{{
  "headline": "Titre accrocheur (max 60 caractères)",
  "subheadline": "Sous-titre complémentaire (max 90 caractères)",
  "body_text": "Texte principal engageant (max 280 caractères)",
  "cta_text": "Appel à l'action (max 25 caractères)",
  "hashtags": ["hashtag1", "hashtag2", "hashtag3"],
  "keywords": ["mot-clé1", "mot-clé2", "mot-clé3"]
}}"""
    
    def _build_user_prompt(
        self,
        audience_type: str,
        tone: str,
        product_focus: Optional[str],
        custom_keywords: List[str],
        platform: str
    ) -> str:
        """Construit le prompt utilisateur"""
        platform_specs = {
            "meta_feed": "Format: Publication Facebook/Instagram Feed (texte court, impactant)",
            "meta_story": "Format: Story Instagram/Facebook (ultra-concis, vertical)",
            "meta_carousel": "Format: Carousel multi-images (texte par slide)",
            "tiktok": "Format: TikTok (jeune, dynamique, trending)",
            "youtube_thumbnail": "Format: Miniature YouTube (accrocheur, curiosité)",
            "email_header": "Format: Email marketing (professionnel, incitatif)"
        }
        
        prompt = f"""Génère du contenu marketing pour BIONIC HUNT/Chasse.

Audience: {audience_type}
Ton souhaité: {tone}
{platform_specs.get(platform, "Format: Publication sociale standard")}

"""
        if product_focus:
            prompt += f"Focus produit: {product_focus}\n"
        
        if custom_keywords:
            prompt += f"Mots-clés à intégrer: {', '.join(custom_keywords)}\n"
        
        prompt += """
Génère le contenu en JSON. Assure-toi que:
- Le headline est percutant et mémorable
- Le CTA incite à l'action immédiate
- Les hashtags sont pertinents pour le secteur chasse/outdoor
- Le texte respecte les limites de caractères"""
        
        return prompt
    
    def _parse_response(self, response: str, audience_type: str, tone: str) -> Dict:
        """Parse la réponse GPT en dictionnaire"""
        import json
        
        try:
            # Nettoyer la réponse
            response = response.strip()
            
            # Trouver le JSON dans la réponse
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                content = json.loads(json_str)
                content["audience_type"] = audience_type
                content["tone"] = tone
                return content
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
        
        # Si parsing échoue, retourner fallback
        return self._get_fallback_content(audience_type, tone)
    
    def _get_fallback_content(self, audience_type: str, tone: str) -> Dict:
        """Contenu de fallback si la génération échoue"""
        fallback_content = {
            "fabricants": {
                "headline": "Partenariat Premium BIONIC HUNT/Chasse",
                "subheadline": "Rejoignez l'écosystème #1 de la chasse intelligente",
                "body_text": "Accédez à une audience de chasseurs passionnés et qualifiés. Technologie BIONIC™ exclusive.",
                "cta_text": "Devenir Partenaire",
                "hashtags": ["#BIONIC HUNT/Chasse", "#Partenariat", "#ChasseSmart"],
                "keywords": ["partenariat", "fabricant", "premium"]
            },
            "affiliation": {
                "headline": "Gagnez avec BIONIC HUNT/Chasse",
                "subheadline": "Programme d'affiliation aux commissions attractives",
                "body_text": "Monétisez votre audience de chasseurs. Commissions récurrentes, outils marketing fournis.",
                "cta_text": "Rejoindre le Programme",
                "hashtags": ["#Affiliation", "#RevenusPassifs", "#BIONIC HUNT/Chasse"],
                "keywords": ["affiliation", "commissions", "revenus"]
            },
            "prospects": {
                "headline": "Chassez Plus Intelligemment",
                "subheadline": "La technologie BIONIC™ révolutionne votre chasse",
                "body_text": "Scoring de spots, prévisions météo, IA prédictive. Essai gratuit, résultats garantis.",
                "cta_text": "Essai Gratuit",
                "hashtags": ["#BIONIC HUNT/Chasse", "#ChasseBIONIC", "#Innovation"],
                "keywords": ["chasse", "technologie", "performance"]
            },
            "general": {
                "headline": "BIONIC HUNT/Chasse - Chasse BIONIC™",
                "subheadline": "L'application qui change tout pour les chasseurs",
                "body_text": "Cartographie avancée, waypoints intelligents, prévisions de succès. Rejoignez la communauté.",
                "cta_text": "Découvrir",
                "hashtags": ["#BIONIC HUNT/Chasse", "#Chasse", "#BIONIC"],
                "keywords": ["chasse", "application", "innovation"]
            }
        }
        
        content = fallback_content.get(audience_type, fallback_content["general"])
        content["audience_type"] = audience_type
        content["tone"] = tone
        content["generation_time_ms"] = 0
        
        return content


class AIImageService:
    """Service de génération d'images marketing IA"""
    
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment")
    
    async def generate_marketing_image(
        self,
        headline: str,
        audience_type: str,
        platform_format: str,
        style: str = "premium_hunting"
    ) -> Dict:
        """
        Génère une image marketing via GPT Image 1.
        
        Returns:
            Dict avec image_base64 et metadata
        """
        import base64
        start_time = time.time()
        
        try:
            from emergentintegrations.llm.openai.image_generation import OpenAIImageGeneration
            
            # Construire le prompt d'image
            prompt = self._build_image_prompt(headline, audience_type, platform_format, style)
            
            # Générer l'image
            image_gen = OpenAIImageGeneration(api_key=self.api_key)
            images = await image_gen.generate_images(
                prompt=prompt,
                model="gpt-image-1",
                number_of_images=1
            )
            
            generation_time = int((time.time() - start_time) * 1000)
            
            if images and len(images) > 0:
                image_base64 = base64.b64encode(images[0]).decode('utf-8')
                
                logger.info(f"Image generated in {generation_time}ms")
                
                return {
                    "success": True,
                    "image_base64": image_base64,
                    "ai_generated": True,
                    "generation_time_ms": generation_time,
                    "prompt_used": prompt[:200]
                }
            
            return {
                "success": False,
                "error": "No image generated",
                "generation_time_ms": generation_time
            }
            
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return {
                "success": False,
                "error": str(e),
                "generation_time_ms": int((time.time() - start_time) * 1000)
            }
    
    def _build_image_prompt(
        self,
        headline: str,
        audience_type: str,
        platform_format: str,
        style: str
    ) -> str:
        """Construit le prompt pour la génération d'image"""
        
        style_descriptions = {
            "premium_hunting": "Professional hunting photography style, premium quality, golden hour lighting, forest/wilderness backdrop",
            "modern_tech": "Modern tech aesthetic, clean lines, dark mode colors (#1a1a2e, #f5a623), futuristic feel",
            "nature_epic": "Epic nature photography, majestic landscapes, wildlife, atmospheric lighting",
            "action_shot": "Dynamic action photography, motion blur, hunter in action, intense moment"
        }
        
        format_sizes = {
            "meta_feed": "1200x628 landscape banner",
            "meta_story": "1080x1920 vertical story",
            "meta_carousel": "1080x1080 square",
            "tiktok": "1080x1920 vertical",
            "youtube_thumbnail": "1280x720 landscape thumbnail"
        }
        
        prompt = f"""Create a premium marketing visual for a hunting technology app called BIONIC HUNT/Chasse.

Theme: {headline}
Style: {style_descriptions.get(style, style_descriptions['premium_hunting'])}
Format: {format_sizes.get(platform_format, '1200x628 landscape')}

Visual requirements:
- Professional, high-end aesthetic
- Colors: Deep blacks, forest greens, golden amber (#f5a623)
- NO text in the image
- Hunting/outdoor/nature theme
- Premium quality suitable for advertising
- Atmospheric and inspiring mood

Target audience: {audience_type}
Brand: BIONIC HUNT/Chasse - BIONIC™ Technology"""
        
        return prompt
