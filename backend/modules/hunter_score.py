"""
BIONIC Hunter Score Engine
═══════════════════════════════════════════════════════════════════════════════
Score dynamique du profil chasseur basé sur:
- Gibier
- Région
- GPS
- Saison
- Outils utilisés
- Pages consultées
- Pourvoiries consultées
- Setups consultés
═══════════════════════════════════════════════════════════════════════════════
Version: 1.1.0
Date: 2026-02-19
Changelog:
- v1.1.0: Added safe_list() to prevent TypeError on corrupted MongoDB data
"""

import os
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field, asdict
from motor.motor_asyncio import AsyncIOMotorClient

# Import safe_list for type-safe data access
from utils.safe_get import safe_list

# Logger for type correction logging
logger = logging.getLogger(__name__)


@dataclass
class HunterScoreBreakdown:
    """Détail du score chasseur"""
    total_score: int = 0
    
    # Composants du score
    gibier_score: int = 0          # Max 15
    region_score: int = 0          # Max 15
    gps_score: int = 0             # Max 10
    saison_score: int = 0          # Max 10
    tools_score: int = 0           # Max 15
    pages_score: int = 0           # Max 10
    pourvoiries_score: int = 0     # Max 10
    setups_score: int = 0          # Max 10
    permis_score: int = 0          # Max 5
    
    # Détails
    level: str = "Débutant"
    level_en: str = "Beginner"
    next_level_threshold: int = 0
    points_to_next_level: int = 0
    
    # Recommandations
    recommendations: List[str] = field(default_factory=list)


# Niveaux de chasseur
HUNTER_LEVELS = [
    {"min": 0, "max": 19, "name": "Débutant", "name_en": "Beginner"},
    {"min": 20, "max": 39, "name": "Apprenti", "name_en": "Apprentice"},
    {"min": 40, "max": 59, "name": "Intermédiaire", "name_en": "Intermediate"},
    {"min": 60, "max": 79, "name": "Avancé", "name_en": "Advanced"},
    {"min": 80, "max": 94, "name": "Expert", "name_en": "Expert"},
    {"min": 95, "max": 100, "name": "Maître Chasseur", "name_en": "Master Hunter"},
]


class HunterScoreService:
    """Service de calcul du score chasseur"""
    
    def __init__(self):
        self._client: Optional[AsyncIOMotorClient] = None
        self._db = None
    
    async def _get_db(self):
        """Connexion lazy à MongoDB"""
        if not self._client:
            mongo_url = os.environ.get('MONGO_URL')
            db_name = os.environ.get('DB_NAME', 'huntiq')
            self._client = AsyncIOMotorClient(mongo_url)
            self._db = self._client[db_name]
        return self._db
    
    async def calculate_score(self, user_id: str) -> HunterScoreBreakdown:
        """
        Calcule le score chasseur complet.
        Score total: 0 à 100
        """
        db = await self._get_db()
        
        # Récupérer le contexte utilisateur
        context = await db.user_contexts.find_one({"user_id": user_id}, {"_id": 0})
        
        if not context:
            return HunterScoreBreakdown(
                total_score=0,
                level="Débutant",
                level_en="Beginner",
                recommendations=["Définissez votre gibier principal", "Sélectionnez votre région"]
            )
        
        breakdown = HunterScoreBreakdown()
        recommendations = []
        
        # 1. Score Gibier (max 15)
        if context.get('gibier_principal'):
            breakdown.gibier_score = 15
        else:
            recommendations.append("Définissez votre gibier principal pour améliorer votre score")
        
        # 2. Score Région (max 15)
        if context.get('region'):
            breakdown.region_score = 15
        elif context.get('province'):
            breakdown.region_score = 10
        else:
            recommendations.append("Sélectionnez votre région de chasse")
        
        # 3. Score GPS (max 10)
        if context.get('gps_lat') and context.get('gps_lng'):
            breakdown.gps_score = 10
        else:
            recommendations.append("Enregistrez votre territoire GPS")
        
        # 4. Score Saison (max 10)
        current_season = context.get('current_season')
        if current_season in ['automne', 'printemps']:
            breakdown.saison_score = 10  # Saison de chasse active
        elif current_season == 'ete':
            breakdown.saison_score = 5   # Préparation
        else:
            breakdown.saison_score = 3   # Hors saison
        
        # 5. Score Outils utilisés (max 15)
        # Using safe_list() to prevent TypeError on corrupted data
        tools_used = safe_list(context, 'tools_used')
        breakdown.tools_score = min(15, len(tools_used) * 3)
        if len(tools_used) < 3:
            recommendations.append("Explorez plus d'outils BIONIC (carte, analyseur, forecast)")
        
        # 6. Score Pages consultées (max 10)
        pages_visited = safe_list(context, 'pages_visited')
        breakdown.pages_score = min(10, len(pages_visited) // 2)
        
        # 7. Score Pourvoiries (max 10)
        pourvoiries = safe_list(context, 'pourvoiries_consulted')
        breakdown.pourvoiries_score = min(10, len(pourvoiries) * 2)
        if not pourvoiries:
            recommendations.append("Consultez des pourvoiries pour planifier vos sorties")
        
        # 8. Score Setups (max 10)
        setups = safe_list(context, 'setups_consulted')
        breakdown.setups_score = min(10, len(setups) * 2)
        if not setups:
            recommendations.append("Découvrez des setups recommandés pour votre gibier")
        
        # 9. Score Permis (max 5)
        permis = safe_list(context, 'permis_consulted')
        if permis:
            breakdown.permis_score = 5
        else:
            recommendations.append("Consultez la section Permis de chasse")
        
        # Calcul du total
        breakdown.total_score = (
            breakdown.gibier_score +
            breakdown.region_score +
            breakdown.gps_score +
            breakdown.saison_score +
            breakdown.tools_score +
            breakdown.pages_score +
            breakdown.pourvoiries_score +
            breakdown.setups_score +
            breakdown.permis_score
        )
        
        # Déterminer le niveau
        for level in HUNTER_LEVELS:
            if level['min'] <= breakdown.total_score <= level['max']:
                breakdown.level = level['name']
                breakdown.level_en = level['name_en']
                breakdown.next_level_threshold = level['max'] + 1
                breakdown.points_to_next_level = max(0, level['max'] + 1 - breakdown.total_score)
                break
        
        breakdown.recommendations = recommendations[:5]  # Max 5 recommandations
        
        # Sauvegarder le score
        await db.hunter_scores.update_one(
            {"user_id": user_id},
            {"$set": {
                "user_id": user_id,
                "score": breakdown.total_score,
                "breakdown": asdict(breakdown),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }},
            upsert=True
        )
        
        return breakdown
    
    async def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Récupère le classement des meilleurs chasseurs"""
        db = await self._get_db()
        
        cursor = db.hunter_scores.find(
            {},
            {"_id": 0, "user_id": 1, "score": 1, "breakdown.level": 1}
        ).sort("score", -1).limit(limit)
        
        return await cursor.to_list(length=limit)


# Instance globale
hunter_score_service = HunterScoreService()
