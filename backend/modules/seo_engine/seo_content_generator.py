"""
BIONIC SEO Content Generator (IA) - V5-ULTIME
==============================================

Génération de contenu SEO via LLM.
Utilise Emergent Universal Key pour OpenAI/Claude/Gemini.

Module isolé - aucun import croisé.
"""

from datetime import datetime, timezone
import logging
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class SEOContentGenerator:
    """Générateur de contenu SEO via IA"""
    
    def __init__(self):
        self.api_key = os.environ.get("EMERGENT_LLM_KEY")
        self.model_provider = "openai"
        self.model_name = "gpt-4o"
    
    async def generate_pillar_content(
        self,
        species_id: str,
        keyword: str,
        knowledge_data: dict,
        language: str = "fr"
    ) -> dict:
        """Générer le contenu complet d'une page pilier"""
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            
            # Préparer les données du Knowledge Layer
            species_info = knowledge_data.get("species", {})
            seasonal_info = knowledge_data.get("seasonal", {})
            rules_info = knowledge_data.get("rules", [])
            
            # System prompt optimisé pour SEO
            system_message = """Tu es un expert en chasse au Québec et en rédaction SEO. 
Tu génères du contenu de haute qualité, informatif et optimisé pour le référencement.

RÈGLES:
1. Écris en français québécois naturel
2. Structure claire avec H2 et H3
3. Inclus des listes à puces pour les conseils
4. Utilise un ton expert mais accessible
5. Intègre les données scientifiques fournies
6. Minimum 3500 mots
7. Inclus une section FAQ avec 8 questions
8. Mentionne les sources officielles (MFFP, SEPAQ)
9. Optimise pour le mot-clé principal sans sur-optimisation
"""

            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"seo_pillar_{uuid.uuid4().hex[:8]}",
                system_message=system_message
            ).with_model(self.model_provider, self.model_name)
            
            # Construire le prompt avec les données Knowledge Layer
            prompt = self._build_pillar_prompt(
                species_id=species_id,
                keyword=keyword,
                species_info=species_info,
                seasonal_info=seasonal_info,
                rules_info=rules_info,
                language=language
            )
            
            user_message = UserMessage(text=prompt)
            
            # Générer le contenu
            content = await chat.send_message(user_message)
            
            # Parser et structurer la réponse
            structured_content = self._parse_generated_content(content, keyword)
            
            return {
                "success": True,
                "content": structured_content,
                "metadata": {
                    "species_id": species_id,
                    "keyword": keyword,
                    "model_used": f"{self.model_provider}/{self.model_name}",
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "word_count": len(content.split())
                }
            }
            
        except ImportError as e:
            logger.error(f"emergentintegrations not available: {e}")
            return {
                "success": False,
                "error": "LLM library not available. Please install emergentintegrations.",
                "fallback": self._generate_fallback_structure(species_id, keyword, knowledge_data)
            }
        except Exception as e:
            logger.error(f"Error generating pillar content: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback": self._generate_fallback_structure(species_id, keyword, knowledge_data)
            }
    
    def _build_pillar_prompt(
        self,
        species_id: str,
        keyword: str,
        species_info: dict,
        seasonal_info: dict,
        rules_info: list,
        language: str
    ) -> str:
        """Construire le prompt pour la génération du pilier"""
        
        # Mapping espèces
        species_names = {
            "moose": {"fr": "Orignal", "en": "Moose"},
            "deer": {"fr": "Cerf de Virginie", "en": "White-tailed Deer"},
            "bear": {"fr": "Ours noir", "en": "Black Bear"},
            "elk": {"fr": "Wapiti", "en": "Elk"}
        }
        
        species_name = species_names.get(species_id, {}).get(language, species_id)
        
        # Données comportementales
        temp_range = species_info.get("temperature_range", {})
        activity = species_info.get("activity_patterns", [])
        habitat = species_info.get("habitat_preferences", [])
        food = species_info.get("food_sources", [])
        rut = species_info.get("rut_info", {})
        
        # Phase saisonnière actuelle
        current_phase = seasonal_info.get("phase", {}).get("name_fr", "Non disponible")
        
        prompt = f"""
# GÉNÉRATION DE PAGE PILIER SEO

## CONTEXTE
Génère un guide complet de 3500+ mots sur la **{keyword}** au Québec.
Espèce ciblée: **{species_name}** ({species_info.get('scientific_name', 'N/A')})

## DONNÉES DU KNOWLEDGE LAYER BIONIC

### Comportement thermique
- Température optimale: {temp_range.get('optimal_min', 'N/A')}°C à {temp_range.get('optimal_max', 'N/A')}°C
- Seuil d'activité réduite: {temp_range.get('activity_threshold', 'N/A')}°C

### Patrons d'activité
{self._format_activity_patterns(activity)}

### Habitats préférés
{self._format_habitat_preferences(habitat)}

### Sources alimentaires
{self._format_food_sources(food)}

### Information sur le rut
- Pic du rut: {rut.get('peak_start_date', 'N/A')} au {rut.get('peak_end_date', 'N/A')}
- Multiplicateur d'activité: {rut.get('activity_multiplier', 'N/A')}x
- Techniques vocales efficaces: {', '.join(rut.get('vocal_behaviors', ['N/A']))}

### Phase saisonnière actuelle
{current_phase}

## STRUCTURE REQUISE

1. **Introduction** (300 mots)
   - Accroche captivante
   - Importance de l'espèce au Québec
   - Aperçu du guide

2. **Biologie et comportement** (500 mots)
   - Utiliser les données du Knowledge Layer
   - Poids, habitat, territoire
   - Cycle annuel

3. **Réglementation au Québec** (400 mots)
   - Zones de chasse (référence MFFP)
   - Quotas et permis
   - Dates de saison

4. **Meilleures périodes de chasse** (400 mots)
   - Utiliser les données saisonnières
   - Influence de la météo
   - Phases lunaires

5. **Techniques de chasse** (600 mots)
   - Appel (si applicable)
   - Approche
   - Affût
   - Tips d'experts

6. **Équipement essentiel** (400 mots)
   - Armes recommandées
   - Optiques
   - Vêtements
   - Accessoires

7. **Meilleures régions au Québec** (400 mots)
   - Zones recommandées
   - Pourvoiries
   - ZECs populaires

8. **Conseils d'experts** (300 mots)
   - Erreurs à éviter
   - Astuces de terrain
   - Sécurité

9. **FAQ** (8 questions/réponses - 400 mots)
   - Questions les plus recherchées
   - Réponses concises et utiles

10. **Conclusion** (200 mots)
    - Résumé des points clés
    - Call-to-action

## MOT-CLÉ PRINCIPAL
"{keyword}"

## CONSIGNES FINALES
- Intègre naturellement le mot-clé principal (5-8 occurrences)
- Utilise des sous-titres H3 dans chaque section
- Ajoute des listes à puces pour la lisibilité
- Cite les sources officielles (MFFP, SEPAQ, FQF)
- Ton: expert mais accessible
- Public: chasseurs québécois de tous niveaux

GÉNÈRE MAINTENANT LE CONTENU COMPLET:
"""
        return prompt
    
    def _format_activity_patterns(self, patterns: list) -> str:
        """Formater les patrons d'activité"""
        if not patterns:
            return "- Données non disponibles"
        
        lines = []
        for p in patterns:
            period = p.get("period", "N/A")
            activity = p.get("activity_level", 0) * 100
            feeding = p.get("feeding_probability", 0) * 100
            lines.append(f"- {period.capitalize()}: Activité {activity:.0f}%, Alimentation {feeding:.0f}%")
        
        return "\n".join(lines)
    
    def _format_habitat_preferences(self, habitats: list) -> str:
        """Formater les préférences d'habitat"""
        if not habitats:
            return "- Données non disponibles"
        
        lines = []
        for h in habitats[:5]:
            habitat = h.get("habitat_type", "N/A")
            score = h.get("preference_score", 0) * 100
            notes = h.get("notes", "")
            lines.append(f"- {habitat}: {score:.0f}% préférence ({notes})")
        
        return "\n".join(lines)
    
    def _format_food_sources(self, foods: list) -> str:
        """Formater les sources alimentaires"""
        if not foods:
            return "- Données non disponibles"
        
        lines = []
        for f in foods[:5]:
            name = f.get("name_fr", f.get("name", "N/A"))
            months = f.get("availability_months", [])
            preference = f.get("preference_score", 0) * 100
            lines.append(f"- {name}: Mois {months}, Préférence {preference:.0f}%")
        
        return "\n".join(lines)
    
    def _parse_generated_content(self, raw_content: str, keyword: str) -> dict:
        """Parser et structurer le contenu généré"""
        
        # Extraire le titre
        lines = raw_content.split("\n")
        title = ""
        for line in lines:
            if line.strip().startswith("# "):
                title = line.replace("# ", "").strip()
                break
        
        if not title:
            title = f"Guide complet: {keyword}"
        
        # Compter les mots
        word_count = len(raw_content.split())
        
        # Extraire les H2
        h2_list = []
        for line in lines:
            if line.strip().startswith("## "):
                h2_list.append(line.replace("## ", "").strip())
        
        # Extraire les FAQ si présentes
        faq_items = []
        in_faq = False
        current_question = ""
        
        for line in lines:
            if "FAQ" in line or "Questions" in line:
                in_faq = True
            if in_faq:
                if line.strip().startswith("**Q") or line.strip().startswith("### "):
                    current_question = line.strip().replace("**", "").replace("### ", "")
                elif current_question and line.strip() and not line.strip().startswith("#"):
                    faq_items.append({
                        "question": current_question,
                        "answer": line.strip()[:200] + "..."
                    })
                    current_question = ""
        
        return {
            "title_fr": title,
            "content_html": self._markdown_to_html(raw_content),
            "content_markdown": raw_content,
            "word_count": word_count,
            "h2_list": h2_list,
            "faq_items": faq_items[:8],
            "meta_description_fr": f"Guide complet sur {keyword} au Québec. Techniques, réglementation, équipement et conseils d'experts.",
            "primary_keyword": keyword,
            "reading_time_min": word_count // 250
        }
    
    def _markdown_to_html(self, markdown: str) -> str:
        """Conversion basique Markdown vers HTML"""
        html = markdown
        
        # Headers
        import re
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        
        # Bold
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        
        # Italic
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        
        # Lists
        html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        
        # Paragraphs
        paragraphs = html.split("\n\n")
        html = "\n".join([f"<p>{p}</p>" if not p.startswith("<") else p for p in paragraphs])
        
        return html
    
    def _generate_fallback_structure(self, species_id: str, keyword: str, knowledge_data: dict) -> dict:
        """Générer une structure de fallback sans IA"""
        species_names = {
            "moose": "Orignal",
            "deer": "Cerf de Virginie", 
            "bear": "Ours noir",
            "elk": "Wapiti"
        }
        
        species_name = species_names.get(species_id, species_id)
        species_info = knowledge_data.get("species", {})
        
        return {
            "title_fr": f"Guide Complet: Chasse à l'{species_name} au Québec",
            "structure": {
                "sections": [
                    {"h2": "Introduction", "placeholder": True},
                    {"h2": f"Biologie et comportement de l'{species_name}", "placeholder": True},
                    {"h2": "Réglementation au Québec", "placeholder": True},
                    {"h2": "Meilleures périodes de chasse", "placeholder": True},
                    {"h2": "Techniques de chasse", "placeholder": True},
                    {"h2": "Équipement essentiel", "placeholder": True},
                    {"h2": "Meilleures régions au Québec", "placeholder": True},
                    {"h2": "Conseils d'experts", "placeholder": True},
                    {"h2": "FAQ", "placeholder": True},
                    {"h2": "Conclusion", "placeholder": True}
                ]
            },
            "knowledge_data_available": {
                "temperature_range": species_info.get("temperature_range", {}),
                "activity_patterns": len(species_info.get("activity_patterns", [])),
                "habitat_preferences": len(species_info.get("habitat_preferences", [])),
                "food_sources": len(species_info.get("food_sources", []))
            },
            "word_count": 0,
            "status": "template_only"
        }


# Instance globale
seo_content_generator = SEOContentGenerator()

logger.info("SEOContentGenerator initialized - V5 LEGO Module with Emergent LLM Key")
