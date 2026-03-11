"""
BIONIC SEO Generation - V5-ULTIME
=================================

Génération de contenu SEO intelligente.
Intégration avec:
- Knowledge Layer (données comportementales)
- Templates de pages
- Optimisation automatique
- Schémas JSON-LD

Module isolé - aucun import croisé.
"""

from datetime import datetime, timezone
from typing import List
import logging
import uuid

logger = logging.getLogger(__name__)


class SEOGenerationManager:
    """Gestionnaire de génération de contenu SEO"""
    
    # ============================================
    # CONTENT GENERATION
    # ============================================
    
    @staticmethod
    async def generate_page_outline(cluster_id: str, page_type: str, 
                                   target_keyword: str, knowledge_data: dict = None) -> dict:
        """Générer un outline de page basé sur le cluster et le Knowledge Layer"""
        try:
            outline = {
                "id": f"outline_{uuid.uuid4().hex[:8]}",
                "cluster_id": cluster_id,
                "page_type": page_type,
                "target_keyword": target_keyword,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Structure de base selon le type
            if page_type == "pillar":
                outline["structure"] = SEOGenerationManager._generate_pillar_structure(
                    target_keyword, knowledge_data
                )
            elif page_type == "satellite":
                outline["structure"] = SEOGenerationManager._generate_satellite_structure(
                    target_keyword, knowledge_data
                )
            elif page_type == "opportunity":
                outline["structure"] = SEOGenerationManager._generate_opportunity_structure(
                    target_keyword, knowledge_data
                )
            
            # Suggestions de maillage interne
            outline["internal_links_suggestions"] = SEOGenerationManager._suggest_internal_links(
                cluster_id, page_type
            )
            
            # Schémas JSON-LD recommandés
            outline["jsonld_recommendations"] = SEOGenerationManager._recommend_jsonld(page_type)
            
            return {
                "success": True,
                "outline": outline
            }
        except Exception as e:
            logger.error(f"Error generating outline: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def _generate_pillar_structure(keyword: str, knowledge_data: dict = None) -> dict:
        """Générer la structure d'une page pilier"""
        structure = {
            "title_suggestions": [
                f"Guide complet: {keyword} au Québec",
                f"{keyword.title()} - Tout ce que vous devez savoir",
                f"Maîtriser {keyword}: Guide ultime pour chasseurs"
            ],
            "meta_description_template": f"Découvrez tout sur {keyword} au Québec. Techniques, équipement, réglementation et conseils d'experts pour une saison réussie.",
            "h1": f"Guide complet: {keyword}",
            "sections": [
                {
                    "h2": "Introduction",
                    "content_guide": "Présentation du sujet, importance pour les chasseurs québécois",
                    "word_count": 200,
                    "include_image": True
                },
                {
                    "h2": "Comprendre les fondamentaux",
                    "content_guide": "Bases essentielles, concepts clés",
                    "word_count": 400,
                    "include_knowledge": True
                },
                {
                    "h2": "Réglementation au Québec",
                    "content_guide": "Règles MFFP, zones, quotas, dates",
                    "word_count": 350,
                    "source": "mffp_quebec"
                },
                {
                    "h2": "Techniques recommandées",
                    "content_guide": "Méthodes éprouvées, stratégies",
                    "word_count": 500,
                    "include_howto": True
                },
                {
                    "h2": "Équipement essentiel",
                    "content_guide": "Matériel recommandé, checklist",
                    "word_count": 400,
                    "include_list": True
                },
                {
                    "h2": "Meilleures régions",
                    "content_guide": "Zones recommandées, pourvoiries, ZEC",
                    "word_count": 400,
                    "include_map": True
                },
                {
                    "h2": "Conseils d'experts",
                    "content_guide": "Tips avancés, erreurs à éviter",
                    "word_count": 350
                },
                {
                    "h2": "FAQ",
                    "content_guide": "Questions fréquentes (5-8 questions)",
                    "word_count": 400,
                    "include_faq_schema": True
                }
            ],
            "total_word_count": 3000,
            "reading_time_min": 12
        }
        
        # Enrichir avec Knowledge Layer si disponible
        if knowledge_data:
            species_data = knowledge_data.get("species", {})
            if species_data:
                structure["sections"].insert(1, {
                    "h2": f"Comportement et biologie",
                    "content_guide": f"Données comportementales issues du Knowledge Layer",
                    "word_count": 400,
                    "knowledge_data": species_data,
                    "include_knowledge": True
                })
                structure["total_word_count"] += 400
        
        return structure
    
    @staticmethod
    def _generate_satellite_structure(keyword: str, knowledge_data: dict = None) -> dict:
        """Générer la structure d'une page satellite"""
        return {
            "title_suggestions": [
                f"{keyword.title()} - Guide pratique",
                f"Comment maîtriser {keyword}",
                f"{keyword.title()}: Conseils et astuces"
            ],
            "meta_description_template": f"Apprenez {keyword} avec notre guide pratique. Techniques éprouvées et conseils d'experts pour les chasseurs québécois.",
            "h1": f"{keyword.title()}",
            "sections": [
                {
                    "h2": "Introduction",
                    "content_guide": "Présentation du sujet spécifique",
                    "word_count": 150
                },
                {
                    "h2": "Principes de base",
                    "content_guide": "Fondamentaux à comprendre",
                    "word_count": 300
                },
                {
                    "h2": "Guide étape par étape",
                    "content_guide": "Instructions détaillées",
                    "word_count": 400,
                    "include_howto": True
                },
                {
                    "h2": "Conseils pratiques",
                    "content_guide": "Tips et recommandations",
                    "word_count": 250
                }
            ],
            "total_word_count": 1100,
            "reading_time_min": 5
        }
    
    @staticmethod
    def _generate_opportunity_structure(keyword: str, knowledge_data: dict = None) -> dict:
        """Générer la structure d'une page opportunité (longue traîne)"""
        return {
            "title_suggestions": [
                f"{keyword.title()} - Réponse d'expert",
                f"{keyword.title()}",
                f"Tout savoir sur {keyword}"
            ],
            "meta_description_template": f"Réponse complète à votre question sur {keyword}. Conseils pratiques pour les chasseurs du Québec.",
            "h1": f"{keyword.title()}",
            "sections": [
                {
                    "h2": "Réponse rapide",
                    "content_guide": "Réponse directe et concise",
                    "word_count": 100
                },
                {
                    "h2": "Explication détaillée",
                    "content_guide": "Développement approfondi",
                    "word_count": 300
                },
                {
                    "h2": "Conseils pratiques",
                    "content_guide": "Recommandations applicables",
                    "word_count": 150
                }
            ],
            "total_word_count": 550,
            "reading_time_min": 3
        }
    
    @staticmethod
    def _suggest_internal_links(cluster_id: str, page_type: str) -> List[dict]:
        """Suggérer des liens internes"""
        suggestions = []
        
        # Lien vers page pilier du cluster
        if page_type != "pillar":
            suggestions.append({
                "type": "pillar",
                "anchor_suggestion": "Guide complet",
                "reason": "Lien vers la page pilier du cluster"
            })
        
        # Liens vers pages satellites
        suggestions.append({
            "type": "satellite",
            "anchor_suggestion": "En savoir plus sur...",
            "reason": "Approfondissement du sujet"
        })
        
        # Liens vers clusters connexes
        suggestions.append({
            "type": "related_cluster",
            "anchor_suggestion": "Voir aussi",
            "reason": "Contenu complémentaire"
        })
        
        return suggestions
    
    @staticmethod
    def _recommend_jsonld(page_type: str) -> List[str]:
        """Recommander les schémas JSON-LD"""
        recommendations = {
            "pillar": ["Article", "HowTo", "FAQPage", "BreadcrumbList"],
            "satellite": ["Article", "HowTo", "BreadcrumbList"],
            "opportunity": ["Article", "FAQPage", "BreadcrumbList"],
            "viral": ["Article"],
            "interactive": ["Article", "HowTo"],
            "tool": ["Article"]
        }
        return recommendations.get(page_type, ["Article", "BreadcrumbList"])
    
    # ============================================
    # META GENERATION
    # ============================================
    
    @staticmethod
    def generate_meta_tags(title: str, keyword: str, content_summary: str = "") -> dict:
        """Générer les meta tags optimisés"""
        # Title tag (50-60 caractères)
        if len(title) > 60:
            title = title[:57] + "..."
        
        # Meta description (150-160 caractères)
        description = f"{content_summary[:100]}... Découvrez nos conseils d'experts pour {keyword}."
        if len(description) > 160:
            description = description[:157] + "..."
        
        return {
            "title": title,
            "meta_description": description,
            "og_title": title,
            "og_description": description,
            "twitter_title": title,
            "twitter_description": description,
            "canonical_url": "",  # À définir
            "robots": "index, follow",
            "keywords": keyword
        }
    
    # ============================================
    # SEO SCORING
    # ============================================
    
    @staticmethod
    def calculate_seo_score(page_data: dict) -> dict:
        """Calculer le score SEO d'une page"""
        score = 100
        issues = []
        recommendations = []
        
        # Title (15 points)
        title = page_data.get("title_fr", page_data.get("title", ""))
        if not title:
            score -= 15
            issues.append("Titre manquant")
        elif len(title) < 30:
            score -= 5
            issues.append("Titre trop court (< 30 caractères)")
        elif len(title) > 60:
            score -= 5
            issues.append("Titre trop long (> 60 caractères)")
        
        # Meta description (10 points)
        meta = page_data.get("meta_description_fr", page_data.get("meta_description", ""))
        if not meta:
            score -= 10
            issues.append("Meta description manquante")
        elif len(meta) < 120:
            score -= 5
            issues.append("Meta description trop courte")
        elif len(meta) > 160:
            score -= 5
            issues.append("Meta description trop longue")
        
        # Keyword in title (10 points)
        keyword = page_data.get("primary_keyword", "")
        if keyword and keyword.lower() not in title.lower():
            score -= 10
            issues.append("Mot-clé principal absent du titre")
            recommendations.append("Inclure le mot-clé principal dans le titre")
        
        # H1 (10 points)
        h1 = page_data.get("h1", "")
        if not h1:
            score -= 10
            issues.append("H1 manquant")
        elif keyword and keyword.lower() not in h1.lower():
            score -= 5
            recommendations.append("Inclure le mot-clé principal dans le H1")
        
        # H2s (10 points)
        h2_list = page_data.get("h2_list", [])
        if len(h2_list) < 3:
            score -= 5
            recommendations.append("Ajouter plus de sous-titres H2 (minimum 3)")
        
        # Word count (15 points)
        word_count = page_data.get("word_count", 0)
        page_type = page_data.get("page_type", "satellite")
        
        min_words = {"pillar": 2000, "satellite": 800, "opportunity": 400}
        min_required = min_words.get(page_type, 800)
        
        if word_count < min_required:
            score -= 15
            issues.append(f"Contenu trop court ({word_count} mots, minimum {min_required})")
        elif word_count < min_required * 1.2:
            score -= 5
            recommendations.append(f"Enrichir le contenu (actuellement {word_count} mots)")
        
        # Internal links (10 points)
        internal_links = page_data.get("internal_links_out", [])
        if len(internal_links) < 2:
            score -= 10
            issues.append("Pas assez de liens internes")
            recommendations.append("Ajouter au moins 3 liens internes")
        
        # JSON-LD (10 points)
        jsonld_types = page_data.get("jsonld_types", [])
        if not jsonld_types:
            score -= 10
            recommendations.append("Ajouter des schémas JSON-LD structurés")
        
        # Images (10 points)
        # À implémenter avec données d'images
        
        return {
            "score": max(0, score),
            "issues": issues,
            "recommendations": recommendations,
            "grade": SEOGenerationManager._score_to_grade(score)
        }
    
    @staticmethod
    def _score_to_grade(score: float) -> str:
        """Convertir score en grade"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    # ============================================
    # VIRAL CONTENT
    # ============================================
    
    @staticmethod
    def generate_viral_capsule(topic: str, species_id: str = None, knowledge_data: dict = None) -> dict:
        """Générer une capsule virale basée sur le Knowledge Layer"""
        capsule = {
            "id": f"viral_{uuid.uuid4().hex[:8]}",
            "topic": topic,
            "species_id": species_id,
            "formats": []
        }
        
        # Format Fact/Stat
        capsule["formats"].append({
            "type": "fact",
            "hook": "🦌 Le saviez-vous?",
            "content_template": f"[Fait intéressant sur {topic}]",
            "platforms": ["facebook", "instagram"],
            "hashtags": ["#chasse", "#quebec", "#chasseur", "#nature"]
        })
        
        # Format Quiz
        capsule["formats"].append({
            "type": "quiz",
            "hook": "🎯 Testez vos connaissances!",
            "content_template": f"Quiz: Combien de temps dure [aspect de {topic}]?",
            "platforms": ["instagram", "tiktok"],
            "engagement_type": "poll"
        })
        
        # Format Tip
        capsule["formats"].append({
            "type": "tip",
            "hook": "💡 Conseil d'expert",
            "content_template": f"Pour améliorer votre {topic}, essayez ceci...",
            "platforms": ["facebook", "twitter"],
            "cta": "Partagez si vous êtes d'accord!"
        })
        
        # Enrichir avec Knowledge Layer
        if knowledge_data and species_id:
            species_info = knowledge_data.get("species", {})
            if species_info:
                capsule["knowledge_facts"] = [
                    f"Température optimale d'activité",
                    f"Meilleur moment de la journée",
                    f"Habitat préféré"
                ]
        
        return {
            "success": True,
            "capsule": capsule
        }


logger.info("SEOGenerationManager initialized - V5 LEGO Module")
