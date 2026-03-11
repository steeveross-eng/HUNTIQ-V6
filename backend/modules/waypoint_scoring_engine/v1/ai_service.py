"""
AI Recommendations Service - GPT-5.2 powered hunting recommendations
"""
import os
import logging
from typing import List, Optional, Dict
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class AIRecommendationService:
    """Service for generating AI-powered hunting recommendations using GPT-5.2"""
    
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        self.model_provider = "openai"
        self.model_name = "gpt-5.2"
    
    async def generate_recommendation(
        self,
        waypoint_data: Dict,
        weather_conditions: Optional[str] = None,
        target_species: str = "deer",
        current_hour: int = None,
        user_history: Optional[Dict] = None
    ) -> str:
        """Generate AI-powered hunting recommendation"""
        
        if not self.api_key:
            logger.warning("EMERGENT_LLM_KEY not configured, using fallback")
            return self._generate_fallback_recommendation(
                waypoint_data, weather_conditions, target_species, current_hour
            )
        
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            
            # Build context
            context = self._build_context(
                waypoint_data, weather_conditions, target_species, 
                current_hour, user_history
            )
            
            system_message = """Tu es un expert en chasse avec 30 ans d'expérience au Québec.
Tu fournis des conseils personnalisés basés sur les données de waypoints, la météo et les patterns comportementaux du gibier.
Réponds en français, de manière concise et actionnable (max 3 phrases).
Inclus un conseil tactique spécifique basé sur les conditions."""
            
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"huntiq-recommendation-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                system_message=system_message
            ).with_model(self.model_provider, self.model_name)
            
            user_message = UserMessage(text=context)
            
            response = await chat.send_message(user_message)
            logger.info("AI recommendation generated successfully")
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating AI recommendation: {e}")
            return self._generate_fallback_recommendation(
                waypoint_data, weather_conditions, target_species, current_hour
            )
    
    def _build_context(
        self,
        waypoint_data: Dict,
        weather_conditions: Optional[str],
        target_species: str,
        current_hour: int,
        user_history: Optional[Dict]
    ) -> str:
        """Build context prompt for AI"""
        
        species_names = {
            "deer": "cerf de Virginie",
            "moose": "orignal",
            "bear": "ours noir",
            "wild_turkey": "dindon sauvage",
            "duck": "canard"
        }
        
        species_name = species_names.get(target_species, target_species)
        
        context = f"""Analyse ce waypoint de chasse et donne-moi ta recommandation:

📍 Waypoint: {waypoint_data.get('name', 'Non spécifié')}
- Score WQS: {waypoint_data.get('wqs', 'N/A')}%
- Classification: {waypoint_data.get('classification', 'N/A')}
- Visites précédentes: {waypoint_data.get('total_visits', 0)}
- Taux de succès historique: {waypoint_data.get('success_rate', 0)}%

🎯 Espèce ciblée: {species_name}
🌤️ Météo: {weather_conditions or 'Non spécifiée'}
⏰ Heure actuelle: {current_hour}h"""

        if user_history:
            context += f"""

📊 Historique chasseur:
- Sorties totales: {user_history.get('total_trips', 0)}
- Taux de succès personnel: {user_history.get('success_rate', 0)}%
- Meilleure heure: {user_history.get('best_hour', 'N/A')}"""
        
        context += "\n\nQuelle est ta recommandation pour maximiser mes chances de succès?"
        
        return context
    
    def _generate_fallback_recommendation(
        self,
        waypoint_data: Dict,
        weather_conditions: Optional[str],
        target_species: str,
        current_hour: int
    ) -> str:
        """Generate fallback recommendation without AI"""
        
        wqs = waypoint_data.get('wqs', 50)
        classification = waypoint_data.get('classification', 'standard')
        
        # Time-based advice
        if 5 <= current_hour < 8:
            time_advice = "L'aube est le moment idéal. Positionnez-vous 30 minutes avant le lever du soleil."
        elif 16 <= current_hour < 19:
            time_advice = "Le crépuscule offre d'excellentes opportunités. Restez en place jusqu'à la tombée de la nuit."
        elif 8 <= current_hour < 12:
            time_advice = "Activité modérée le matin. Concentrez-vous sur les zones d'alimentation."
        else:
            time_advice = "Période moins active. Repérez les sentiers et signes pour vos prochaines sorties."
        
        # Weather advice
        weather_advice = ""
        if weather_conditions:
            if weather_conditions == "Nuageux":
                weather_advice = "Temps nuageux idéal pour la chasse - le gibier est plus actif."
            elif weather_conditions == "Pluvieux":
                weather_advice = "La pluie réduit votre odeur - excellent pour l'approche."
            elif weather_conditions == "Ensoleillé":
                weather_advice = "Cherchez l'ombre et les zones de fraîcheur où le gibier se réfugie."
            elif weather_conditions == "Neigeux":
                weather_advice = "Excellent pour repérer les traces fraîches."
        
        # Classification advice
        if classification == "hotspot":
            spot_advice = f"Ce waypoint est un hotspot (WQS {wqs}%) - haute probabilité de succès."
        elif classification == "good":
            spot_advice = f"Bon spot (WQS {wqs}%) - conditions favorables."
        else:
            spot_advice = f"Spot standard (WQS {wqs}%) - patience recommandée."
        
        return f"{spot_advice} {time_advice} {weather_advice}".strip()
    
    async def generate_daily_briefing(
        self,
        waypoints: List[Dict],
        weather_forecast: Optional[str] = None,
        target_species: str = "deer"
    ) -> str:
        """Generate a daily hunting briefing"""
        
        if not self.api_key:
            return self._generate_fallback_briefing(waypoints, weather_forecast, target_species)
        
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            
            # Build briefing context
            waypoints_summary = "\n".join([
                f"- {wp.get('name')}: WQS {wp.get('wqs', 0)}% ({wp.get('classification', 'N/A')})"
                for wp in waypoints[:5]
            ])
            
            context = f"""Génère un briefing de chasse pour aujourd'hui:

📍 Mes waypoints (top 5):
{waypoints_summary}

🌤️ Météo prévue: {weather_forecast or 'Non disponible'}
🎯 Espèce ciblée: {target_species}

Donne-moi un plan d'action pour la journée en 4-5 points clés."""
            
            system_message = """Tu es un guide de chasse expert au Québec.
Génère un briefing matinal concis et actionnable.
Utilise des emojis pour structurer. Réponds en français."""
            
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"huntiq-briefing-{datetime.now().strftime('%Y%m%d')}",
                system_message=system_message
            ).with_model(self.model_provider, self.model_name)
            
            response = await chat.send_message(UserMessage(text=context))
            return response
            
        except Exception as e:
            logger.error(f"Error generating briefing: {e}")
            return self._generate_fallback_briefing(waypoints, weather_forecast, target_species)
    
    def _generate_fallback_briefing(
        self,
        waypoints: List[Dict],
        weather_forecast: Optional[str],
        target_species: str
    ) -> str:
        """Generate fallback briefing"""
        
        best_waypoint = waypoints[0] if waypoints else None
        
        briefing = "🌅 **Briefing du jour**\n\n"
        
        if best_waypoint:
            briefing += f"📍 **Spot recommandé**: {best_waypoint.get('name')} (WQS: {best_waypoint.get('wqs', 0)}%)\n\n"
        
        briefing += "⏰ **Créneaux optimaux**:\n"
        briefing += "- 06:00-08:00 (Aube - priorité haute)\n"
        briefing += "- 17:00-19:00 (Crépuscule - priorité haute)\n\n"
        
        if weather_forecast:
            briefing += f"🌤️ **Météo**: {weather_forecast}\n\n"
        
        briefing += "💡 **Conseils**:\n"
        briefing += "- Arrivez 30 min avant les créneaux optimaux\n"
        briefing += "- Positionnez-vous face au vent\n"
        briefing += "- Minimisez vos mouvements\n"
        
        return briefing
