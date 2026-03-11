"""AI Engine Service - CORE

Business logic for AI-powered product analysis using GPT-5.2.
Extracted from analyzer.py ProductAnalyzer class.

Version: 1.0.0
"""

import os
import json
import uuid
from typing import Optional, Dict, Any, List

from emergentintegrations.llm.chat import LlmChat, UserMessage

from .models import (
    AIAnalysisReport, 
    ProductTechnicalSheet,
    ScientificAnalysis,
    CompetitorComparison,
    AdvancedAnalysisResponse
)
from .data.products import (
    detect_category,
    get_bionic_product,
    get_competitors
)
from .data.references import get_scientific_references

# Import scoring service for score calculation
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from scoring_engine.v1.service import ScoringService


class AIAnalysisService:
    """Service for AI-powered product analysis using GPT-5.2"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('EMERGENT_LLM_KEY', '')
        self.scoring_service = ScoringService()
        self._chat = None
    
    @property
    def chat(self):
        """Lazy initialization of LLM chat"""
        if self._chat is None and self.api_key:
            self._chat = LlmChat(
                api_key=self.api_key,
                session_id=f"analyzer_{uuid.uuid4().hex[:8]}",
                system_message="""Tu es un expert scientifique en attractants pour la chasse au Québec et en Amérique du Nord.
                Tu analyses les produits de manière impartiale et scientifique basé sur 13 critères d'évaluation.
                Tu dois fournir des analyses détaillées basées sur les ingrédients, la composition chimique et les conditions d'utilisation.
                Tu prends en compte l'espèce cible, la saison de chasse, les conditions météorologiques et le type d'habitat.
                Réponds toujours en JSON valide."""
            ).with_model("openai", "gpt-5.2")
        return self._chat
    
    def get_comparison(self, product_type: str, analyzed_score: float) -> CompetitorComparison:
        """Generate 3-column comparison table"""
        bionic = get_bionic_product(product_type)
        competitors = get_competitors(product_type)
        
        # Sort competitors by score
        sorted_competitors = sorted(competitors, key=lambda x: x["score"], reverse=True)
        
        competitor_1 = sorted_competitors[0] if len(sorted_competitors) > 0 else competitors[0]
        competitor_2 = sorted_competitors[1] if len(sorted_competitors) > 1 else competitors[0]
        
        comparison_table = []
        criteria_list = [
            ("score", "Score d'attraction"),
            ("pastille", "Pastille"),
            ("attraction_days", "Durée d'attraction (jours)"),
            ("price", "Meilleur prix (sans transport)"),
            ("price_with_shipping", "Meilleur prix (avec transport)"),
            ("buy_link", "Lien vers l'offre"),
            ("performance_price", "Performance/prix"),
            ("rainproof", "Rainproof"),
            ("feed_proof", "Feed-Proof"),
            ("certified", "Certification alimentaire"),
        ]
        
        for key, label in criteria_list:
            row = {"criterion": label}
            
            if key == "score":
                row["bionic"] = bionic["score"]
                row["competitor_1"] = competitor_1["score"]
                row["competitor_2"] = competitor_2["score"]
            elif key == "pastille":
                row["bionic"] = "🟢" if bionic["score"] >= 7.5 else "🟡"
                row["competitor_1"] = "🟢" if competitor_1["score"] >= 7.5 else "🟡" if competitor_1["score"] >= 5 else "🔴"
                row["competitor_2"] = "🟢" if competitor_2["score"] >= 7.5 else "🟡" if competitor_2["score"] >= 5 else "🔴"
            elif key == "attraction_days":
                row["bionic"] = bionic["attraction_days"]
                row["competitor_1"] = competitor_1["attraction_days"]
                row["competitor_2"] = competitor_2["attraction_days"]
            elif key == "price":
                row["bionic"] = f"${bionic['price']}"
                row["competitor_1"] = f"${competitor_1['price']}"
                row["competitor_2"] = f"${competitor_2['price']}"
            elif key == "price_with_shipping":
                row["bionic"] = f"${bionic['price_with_shipping']}"
                row["competitor_1"] = f"${competitor_1['price_with_shipping']}"
                row["competitor_2"] = f"${competitor_2['price_with_shipping']}"
            elif key == "buy_link":
                row["bionic"] = bionic["buy_link"]
                row["competitor_1"] = competitor_1["buy_link"]
                row["competitor_2"] = competitor_2["buy_link"]
            elif key == "performance_price":
                row["bionic"] = round(bionic["score"] / bionic["price"] * 10, 2)
                row["competitor_1"] = round(competitor_1["score"] / competitor_1["price"] * 10, 2)
                row["competitor_2"] = round(competitor_2["score"] / competitor_2["price"] * 10, 2)
            elif key in ["rainproof", "feed_proof", "certified"]:
                row["bionic"] = "✅" if bionic.get(key, False) else "❌"
                row["competitor_1"] = "✅" if competitor_1.get(key, False) else "❌"
                row["competitor_2"] = "✅" if competitor_2.get(key, False) else "❌"
            
            comparison_table.append(row)
        
        return CompetitorComparison(
            bionic_product={
                "name": bionic["name"],
                "image_url": bionic["image_url"],
                "score": bionic["score"],
                "price": bionic["price"],
                "price_with_shipping": bionic["price_with_shipping"],
                "buy_link": bionic["buy_link"]
            },
            competitor_1={
                "name": competitor_1["name"],
                "brand": competitor_1["brand"],
                "image_url": competitor_1["image_url"],
                "score": competitor_1["score"],
                "price": competitor_1["price"],
                "price_with_shipping": competitor_1["price_with_shipping"],
                "buy_link": competitor_1["buy_link"]
            },
            competitor_2={
                "name": competitor_2["name"],
                "brand": competitor_2["brand"],
                "image_url": competitor_2["image_url"],
                "score": competitor_2["score"],
                "price": competitor_2["price"],
                "price_with_shipping": competitor_2["price_with_shipping"],
                "buy_link": competitor_2["buy_link"]
            },
            comparison_table=comparison_table
        )
    
    async def analyze_product(self, product_name: str, product_type: Optional[str] = None) -> AIAnalysisReport:
        """Complete AI analysis of a product"""
        
        # Category detection
        detected_type = product_type or detect_category(product_name)
        
        # Import ingredients database for the prompt
        from modules.nutrition_engine.v1.data.ingredients import INGREDIENTS_DATABASE
        
        # AI analysis prompt
        analysis_prompt = f"""Analyse le produit attractant de chasse suivant: "{product_name}"

Type détecté: {detected_type}

Base de données d'ingrédients connus: {json.dumps(list(INGREDIENTS_DATABASE.keys()), ensure_ascii=False)}

Fournis une analyse JSON avec cette structure exacte:
{{
    "brand": "marque détectée ou estimée",
    "estimated_price": prix estimé en dollars,
    "estimated_ingredients": ["liste", "des", "ingrédients", "estimés"],
    "olfactory_compounds": [{{"name": "nom", "category": "catégorie", "attraction_value": 1-10}}],
    "nutritional_compounds": [{{"name": "nom", "category": "catégorie", "attraction_value": 1-10}}],
    "behavioral_compounds": [{{"name": "nom", "category": "catégorie", "attraction_value": 1-10}}],
    "attraction_days": nombre de jours d'attraction estimé,
    "natural_palatability": score 1-10,
    "olfactory_power": score 1-10,
    "persistence": score 1-10,
    "nutrition": score 1-10,
    "rainproof": true/false,
    "feed_proof": true/false,
    "certified": true/false,
    "physical_resistance": score 1-10,
    "ingredient_purity": score 1-10,
    "loyalty": score 1-10,
    "chemical_stability": score 1-10,
    "notes": ["informations", "importantes", "sur", "le", "produit"],
    "recommendations": ["recommandation 1", "recommandation 2"]
}}

Sois précis et scientifique. Si des informations sont estimées, indique-le dans les notes."""

        try:
            if self.chat:
                response = await self.chat.send_message(UserMessage(text=analysis_prompt))
                
                # Parse JSON response
                json_str = response
                if "```json" in json_str:
                    json_str = json_str.split("```json")[1].split("```")[0]
                elif "```" in json_str:
                    json_str = json_str.split("```")[1].split("```")[0]
                
                analysis_data = json.loads(json_str)
            else:
                raise ValueError("No API key configured")
                
        except Exception as e:
            # Fallback with default data
            analysis_data = {
                "brand": "Marque inconnue",
                "estimated_price": 25.00,
                "estimated_ingredients": ["ingrédients non identifiés"],
                "olfactory_compounds": [],
                "nutritional_compounds": [],
                "behavioral_compounds": [],
                "attraction_days": 10,
                "natural_palatability": 6,
                "olfactory_power": 6,
                "persistence": 6,
                "nutrition": 5,
                "rainproof": False,
                "feed_proof": True,
                "certified": False,
                "physical_resistance": 6,
                "ingredient_purity": 5,
                "loyalty": 5,
                "chemical_stability": 6,
                "notes": [f"Analyse automatique - erreur: {str(e)}"],
                "recommendations": ["Vérifier les informations du produit"]
            }
        
        # Create technical sheet
        technical_sheet = ProductTechnicalSheet(
            name=product_name,
            detected_type=detected_type,
            brand=analysis_data.get("brand"),
            estimated_price=analysis_data.get("estimated_price"),
            estimated_price_with_shipping=analysis_data.get("estimated_price", 25) + 10,
            estimated_ingredients=analysis_data.get("estimated_ingredients", []),
            confidence_level="estimated",
            notes=analysis_data.get("notes", [])
        )
        
        # Create scientific analysis
        scientific_analysis = ScientificAnalysis(
            olfactory_compounds=analysis_data.get("olfactory_compounds", []),
            nutritional_compounds=analysis_data.get("nutritional_compounds", []),
            behavioral_compounds=analysis_data.get("behavioral_compounds", []),
            fixatives=[],
            durability_criteria={
                "rainproof": analysis_data.get("rainproof", False),
                "feed_proof": analysis_data.get("feed_proof", True),
                "certified": analysis_data.get("certified", False)
            }
        )
        
        # Calculate score using scoring engine
        scoring = self.scoring_service.calculate_score(analysis_data, detected_type)
        
        # Generate comparison
        comparison = self.get_comparison(detected_type, scoring.total_score)
        
        # Price analysis
        price_analysis = {
            "analyzed_product": {
                "price": analysis_data.get("estimated_price", 25),
                "price_with_shipping": analysis_data.get("estimated_price", 25) + 10,
                "performance_price_ratio": round(scoring.total_score / max(analysis_data.get("estimated_price", 25), 1) * 10, 2)
            },
            "bionic": {
                "price": comparison.bionic_product["price"],
                "price_with_shipping": comparison.bionic_product["price_with_shipping"],
                "performance_price_ratio": round(comparison.bionic_product["score"] / comparison.bionic_product["price"] * 10, 2)
            },
            "best_value": "BIONIC™" if comparison.bionic_product["score"] / comparison.bionic_product["price"] > scoring.total_score / max(analysis_data.get("estimated_price", 25), 1) else product_name
        }
        
        # Generate BIONIC arguments
        bionic_product = get_bionic_product(detected_type)
        bionic_arguments = []
        
        if bionic_product["score"] > scoring.total_score:
            bionic_arguments.append(f"Score d'attraction supérieur: {bionic_product['score']}/10 vs {scoring.total_score}/10")
        if bionic_product["attraction_days"] > analysis_data.get("attraction_days", 10):
            bionic_arguments.append(f"Durée d'attraction plus longue: {bionic_product['attraction_days']} jours vs {analysis_data.get('attraction_days', 10)} jours")
        if bionic_product.get("certified") and not analysis_data.get("certified"):
            bionic_arguments.append("Certification alimentaire ACIA/CFIA garantie")
        if bionic_product.get("rainproof") and not analysis_data.get("rainproof"):
            bionic_arguments.append("Résistance aux intempéries (Rainproof)")
        if bionic_product.get("feed_proof"):
            bionic_arguments.append("100% Feed-Proof - Sécurité alimentaire garantie")
        
        # Conclusion
        if scoring.total_score >= 8:
            conclusion = f"Le produit {product_name} présente une performance d'attraction excellente avec un score de {scoring.total_score}/10."
        elif scoring.total_score >= 6:
            conclusion = f"Le produit {product_name} offre une performance d'attraction correcte ({scoring.total_score}/10) mais pourrait être optimisé."
        else:
            conclusion = f"Le produit {product_name} présente des limitations significatives ({scoring.total_score}/10). Considérez les alternatives BIONIC™."
        
        if bionic_product["score"] > scoring.total_score:
            conclusion += f" Le produit BIONIC™ {bionic_product['name']} offre une performance supérieure documentée."
        
        return AIAnalysisReport(
            product_name=product_name,
            technical_sheet=technical_sheet,
            scientific_analysis=scientific_analysis,
            scoring={
                "total_score": scoring.total_score,
                "pastille": scoring.pastille,
                "pastille_label": scoring.pastille_label,
                "criteria_scores": scoring.criteria_scores,
                "weighted_scores": scoring.weighted_scores
            },
            comparison=comparison,
            price_analysis=price_analysis,
            recommendations=analysis_data.get("recommendations", []),
            bionic_arguments=bionic_arguments,
            conclusion=conclusion,
            scientific_references=get_scientific_references()
        )
    
    async def analyze_advanced(
        self,
        product_name: str,
        species: str = "deer",
        season: str = "fall",
        weather: str = "normal",
        terrain: str = "forest"
    ) -> AdvancedAnalysisResponse:
        """Advanced AI analysis with hunting context"""
        
        # Context prompt for GPT-5.2
        context_prompt = f"""Analyse avancée pour la chasse:

Produit: {product_name}
Espèce cible: {species}
Saison: {season}
Conditions météo: {weather}
Terrain: {terrain}

Fournis une analyse JSON avec:
{{
    "score": score 1-10 pour ce contexte,
    "recommendation": "recommandation détaillée",
    "best_time": "meilleur moment de la journée",
    "application_tips": ["conseil 1", "conseil 2", "conseil 3"],
    "alternatives": [{{"name": "produit", "reason": "raison"}}],
    "scientific_basis": "explication scientifique"
}}"""

        try:
            if self.chat:
                response = await self.chat.send_message(UserMessage(text=context_prompt))
                
                json_str = response
                if "```json" in json_str:
                    json_str = json_str.split("```json")[1].split("```")[0]
                elif "```" in json_str:
                    json_str = json_str.split("```")[1].split("```")[0]
                
                data = json.loads(json_str)
            else:
                raise ValueError("No API key configured")
                
        except Exception as e:
            # Fallback
            data = {
                "score": 7.0,
                "recommendation": "Produit adapté aux conditions moyennes",
                "best_time": "Aube et crépuscule",
                "application_tips": [
                    "Appliquer sur des branches basses",
                    "Renouveler après la pluie",
                    "Éviter le contact direct avec le sol"
                ],
                "alternatives": [],
                "scientific_basis": f"Analyse basée sur les caractéristiques du produit. Note: {str(e)}"
            }
        
        return AdvancedAnalysisResponse(
            product_name=product_name,
            species=species,
            season=season,
            weather=weather,
            terrain=terrain,
            score=data.get("score", 7.0),
            recommendation=data.get("recommendation", ""),
            best_time=data.get("best_time", "Aube et crépuscule"),
            application_tips=data.get("application_tips", []),
            alternatives=data.get("alternatives", []),
            scientific_basis=data.get("scientific_basis", "")
        )


    # ==========================================
    # NEW GPT-5.2 METHODS (P1)
    # ==========================================
    
    async def query_assistant(
        self,
        question: str,
        context: Optional[str] = None,
        species: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Q&A with the AI hunting assistant using GPT-5.2.
        
        Provides expert answers on hunting techniques, products, and wildlife.
        """
        # Build context-aware prompt
        context_info = ""
        if context:
            context_info += f"\nContexte fourni: {context}"
        if species:
            context_info += f"\nEspèce ciblée: {species}"
        
        query_prompt = f"""Tu es un expert en chasse au Québec et en Amérique du Nord.
Réponds de manière précise et utile à cette question de chasseur.
{context_info}

Question: {question}

Fournis une réponse JSON avec:
{{
    "answer": "ta réponse détaillée et experte",
    "sources": ["source 1 si applicable", "source 2"],
    "related_products": ["produit recommandé 1", "produit recommandé 2"],
    "tips": ["conseil pratique 1", "conseil pratique 2"]
}}

Sois concis mais complet. Privilégie les informations pratiques et actionnables."""

        try:
            if self.chat:
                response = await self.chat.send_message(UserMessage(text=query_prompt))
                
                # Parse JSON
                json_str = response
                if "```json" in json_str:
                    json_str = json_str.split("```json")[1].split("```")[0]
                elif "```" in json_str:
                    json_str = json_str.split("```")[1].split("```")[0]
                
                data = json.loads(json_str)
                data["session_id"] = session_id or f"session_{uuid.uuid4().hex[:8]}"
                return data
            else:
                raise ValueError("No API key configured")
                
        except json.JSONDecodeError:
            # If JSON parsing fails, return the raw response
            return {
                "answer": response if 'response' in dir() else "Désolé, je n'ai pas pu traiter cette question.",
                "sources": [],
                "related_products": [],
                "session_id": session_id or f"session_{uuid.uuid4().hex[:8]}"
            }
        except Exception as e:
            # Fallback response
            return {
                "answer": f"Je suis un assistant IA spécialisé en chasse. Pour votre question sur '{question}', je vous recommande de consulter les ressources de chasse locales ou de reformuler votre question. Erreur technique: {str(e)}",
                "sources": ["MFFP Québec", "FédéCP"],
                "related_products": [],
                "session_id": session_id or f"session_{uuid.uuid4().hex[:8]}"
            }
    
    async def compare_products_ai(
        self,
        products: List[str],
        criteria: Optional[List[str]] = None,
        species: Optional[str] = "deer"
    ) -> Dict[str, Any]:
        """
        Compare multiple products using AI analysis.
        
        Returns detailed comparison with winner and recommendations.
        """
        default_criteria = [
            "Efficacité d'attraction",
            "Durée d'action",
            "Résistance aux intempéries",
            "Rapport qualité/prix",
            "Facilité d'utilisation"
        ]
        
        criteria_list = criteria or default_criteria
        products_str = ", ".join(products)
        criteria_str = ", ".join(criteria_list)
        
        compare_prompt = f"""Compare ces produits attractants de chasse pour le {species}:
Produits: {products_str}

Critères d'évaluation: {criteria_str}

Fournis une analyse JSON avec:
{{
    "comparison": [
        {{
            "product": "nom du produit",
            "scores": {{"critère1": 8, "critère2": 7}},
            "strengths": ["force 1", "force 2"],
            "weaknesses": ["faiblesse 1"]
        }}
    ],
    "winner": "nom du meilleur produit",
    "winner_score": score total sur 10,
    "recommendation": "recommandation détaillée",
    "best_value": "meilleur rapport qualité/prix",
    "detailed_analysis": "analyse comparative détaillée"
}}

Sois objectif et scientifique dans ton évaluation."""

        try:
            if self.chat:
                response = await self.chat.send_message(UserMessage(text=compare_prompt))
                
                json_str = response
                if "```json" in json_str:
                    json_str = json_str.split("```json")[1].split("```")[0]
                elif "```" in json_str:
                    json_str = json_str.split("```")[1].split("```")[0]
                
                return json.loads(json_str)
            else:
                raise ValueError("No API key configured")
                
        except Exception as e:
            # Fallback comparison
            fallback_comparison = []
            for i, product in enumerate(products):
                fallback_comparison.append({
                    "product": product,
                    "scores": {c: 7 - i for c in criteria_list[:3]},
                    "strengths": ["Produit reconnu sur le marché"],
                    "weaknesses": ["Données insuffisantes pour analyse complète"]
                })
            
            return {
                "comparison": fallback_comparison,
                "winner": products[0],
                "recommendation": f"Basé sur les données disponibles, {products[0]} semble être un bon choix. Consultez les avis détaillés pour plus d'informations. Note: {str(e)}",
                "best_value": products[0],
                "detailed_analysis": fallback_comparison
            }
    
    async def get_suggestions(
        self,
        species: str = "deer",
        season: str = "fall",
        budget: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Get AI-powered product suggestions based on hunting context.
        """
        budget_info = f"Budget maximum: ${budget}" if budget else "Pas de limite de budget"
        
        suggestion_prompt = f"""Recommande les meilleurs attractants de chasse pour:
- Espèce: {species}
- Saison: {season}
- {budget_info}

Fournis des suggestions JSON:
{{
    "suggestions": [
        {{
            "name": "nom du produit",
            "type": "type d'attractant",
            "estimated_price": prix estimé,
            "score": score sur 10,
            "reason": "pourquoi ce produit"
        }}
    ],
    "top_pick": {{
        "name": "meilleur choix",
        "reason": "pourquoi c'est le meilleur"
    }},
    "reasoning": "explication de la stratégie recommandée"
}}

Inclus des produits BIONIC si pertinents."""

        try:
            if self.chat:
                response = await self.chat.send_message(UserMessage(text=suggestion_prompt))
                
                json_str = response
                if "```json" in json_str:
                    json_str = json_str.split("```json")[1].split("```")[0]
                elif "```" in json_str:
                    json_str = json_str.split("```")[1].split("```")[0]
                
                return json.loads(json_str)
            else:
                raise ValueError("No API key configured")
                
        except Exception as e:
            # Fallback suggestions based on context
            bionic_product = get_bionic_product("urine")
            
            return {
                "suggestions": [
                    {
                        "name": bionic_product["name"],
                        "type": "urine",
                        "estimated_price": bionic_product["price"],
                        "score": bionic_product["score"],
                        "reason": "Produit BIONIC certifié, haute efficacité"
                    },
                    {
                        "name": "Attractant minéral",
                        "type": "mineral",
                        "estimated_price": 20.00,
                        "score": 7.5,
                        "reason": f"Efficace pour {species} en {season}"
                    }
                ],
                "top_pick": {
                    "name": bionic_product["name"],
                    "reason": "Meilleur rapport efficacité/prix avec certification"
                },
                "reasoning": f"Pour la chasse au {species} en {season}, les attractants olfactifs sont recommandés. Note: {str(e)}"
            }
