"""
BIONIC Score de Préparation Engine
═══════════════════════════════════════════════════════════════════════════════
Calcul du score de préparation basé sur:
- Permis
- Setup
- Territoire
- Gear
- Formation
- Hotspots (si achetés)
- Capsules consultées
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
class PreparationScoreBreakdown:
    """Détail du score de préparation"""
    total_score: int = 0
    
    # Composants (total = 100)
    permis_score: int = 0          # Max 20
    setup_score: int = 0           # Max 15
    territoire_score: int = 0      # Max 20
    gear_score: int = 0            # Max 15
    formation_score: int = 0       # Max 10
    hotspots_score: int = 0        # Max 10
    capsules_score: int = 0        # Max 10
    
    # Niveau
    readiness_level: str = "Non prêt"
    readiness_level_en: str = "Not Ready"
    
    # Détails par composant
    permis_details: Dict[str, Any] = field(default_factory=dict)
    setup_details: Dict[str, Any] = field(default_factory=dict)
    territoire_details: Dict[str, Any] = field(default_factory=dict)
    gear_details: Dict[str, Any] = field(default_factory=dict)
    formation_details: Dict[str, Any] = field(default_factory=dict)
    hotspots_details: Dict[str, Any] = field(default_factory=dict)
    capsules_details: Dict[str, Any] = field(default_factory=dict)
    
    # Recommandations pour améliorer
    improvements: List[Dict[str, Any]] = field(default_factory=list)
    
    # Métadonnées
    calculated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# Niveaux de préparation
READINESS_LEVELS = [
    {"min": 0, "max": 19, "name": "Non prêt", "name_en": "Not Ready", "color": "red"},
    {"min": 20, "max": 39, "name": "Peu préparé", "name_en": "Poorly Prepared", "color": "orange"},
    {"min": 40, "max": 59, "name": "Partiellement prêt", "name_en": "Partially Ready", "color": "yellow"},
    {"min": 60, "max": 79, "name": "Bien préparé", "name_en": "Well Prepared", "color": "lime"},
    {"min": 80, "max": 94, "name": "Très bien préparé", "name_en": "Very Well Prepared", "color": "green"},
    {"min": 95, "max": 100, "name": "Prêt à 100%", "name_en": "100% Ready", "color": "emerald"},
]


class ScorePreparationService:
    """Service de calcul du score de préparation"""
    
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
    
    async def calculate_score(self, user_id: str) -> PreparationScoreBreakdown:
        """
        Calcule le score de préparation complet.
        Score total: 0 à 100
        """
        db = await self._get_db()
        
        breakdown = PreparationScoreBreakdown()
        improvements = []
        
        # 1. PERMIS (max 20)
        checklist = await db.permis_checklists.find_one({"user_id": user_id}, {"_id": 0})
        if checklist:
            completion = checklist.get('completion_percentage', 0)
            breakdown.permis_score = int(completion * 0.2)  # Max 20
            # Use safe_list to prevent TypeError on corrupted 'items' field
            items = safe_list(checklist, 'items')
            breakdown.permis_details = {
                "has_checklist": True,
                "completion_percentage": completion,
                "items_completed": len([i for i in items if isinstance(i, dict) and i.get('is_completed')])
            }
        else:
            breakdown.permis_details = {"has_checklist": False}
            improvements.append({
                "category": "permis",
                "action": "Consultez la section Permis de chasse",
                "action_en": "Visit the Hunting License section",
                "points_potential": 20,
                "url": "/permis-chasse",
                "cta_label": "Voir les permis",
                "is_purchasable": False
            })
        
        # 2. SETUP (max 15)
        setup = await db.generated_setups.find_one({"user_id": user_id}, {"_id": 0})
        if setup:
            breakdown.setup_score = 15
            breakdown.setup_details = {
                "has_setup": True,
                "gibier": setup.get('gibier'),
                "total_items": setup.get('total_items', 0)
            }
        else:
            breakdown.setup_details = {"has_setup": False}
            improvements.append({
                "category": "setup",
                "action": "Créez votre setup personnalisé",
                "action_en": "Create your personalized setup",
                "points_potential": 15,
                "url": "/setup-builder",
                "cta_label": "Créer mon setup",
                "is_purchasable": False
            })
        
        # 3. TERRITOIRE (max 20)
        context = await db.user_contexts.find_one({"user_id": user_id}, {"_id": 0})
        if context:
            has_gps = bool(context.get('gps_lat') and context.get('gps_lng'))
            has_region = bool(context.get('region'))
            # Use safe_list to prevent TypeError on corrupted 'pages_visited' field
            pages_visited = safe_list(context, 'pages_visited')
            territory_visits = len([p for p in pages_visited if isinstance(p, str) and ('territoire' in p or 'map' in p)])
            
            if has_gps:
                breakdown.territoire_score += 10
            if has_region:
                breakdown.territoire_score += 5
            if territory_visits >= 3:
                breakdown.territoire_score += 5
            
            breakdown.territoire_details = {
                "has_gps": has_gps,
                "has_region": has_region,
                "territory_visits": territory_visits
            }
            
            if not has_gps:
                improvements.append({
                    "category": "territoire",
                    "action": "Enregistrez votre territoire GPS",
                    "action_en": "Save your GPS territory",
                    "points_potential": 10,
                    "url": "/territoire",
                    "cta_label": "Analyser territoire",
                    "is_purchasable": False
                })
        else:
            breakdown.territoire_details = {"has_gps": False, "has_region": False}
            improvements.append({
                "category": "territoire",
                "action": "Analysez votre territoire avec BIONIC",
                "action_en": "Analyze your territory with BIONIC",
                "points_potential": 20,
                "url": "/territoire",
                "cta_label": "Analyser maintenant",
                "is_purchasable": False
            })
        
        # 4. GEAR (max 15)
        cart_items = await db.cart_items.find({"user_id": user_id, "item_type": "gear"}, {"_id": 0}).to_list(100)
        purchases = await db.purchases.find({"user_id": user_id}, {"_id": 0}).to_list(100)
        
        # Safely handle cart_items and purchases as lists
        cart_items_list = cart_items if isinstance(cart_items, list) else []
        purchases_list = purchases if isinstance(purchases, list) else []
        
        gear_count = len(cart_items_list) + len([p for p in purchases_list if isinstance(p, dict) and p.get('item_type') == 'gear'])
        
        if gear_count >= 5:
            breakdown.gear_score = 15
        elif gear_count >= 3:
            breakdown.gear_score = 10
        elif gear_count >= 1:
            breakdown.gear_score = 5
        
        breakdown.gear_details = {"items_count": gear_count}
        
        if gear_count < 5:
            improvements.append({
                "category": "gear",
                "action": "Complétez votre équipement",
                "action_en": "Complete your gear",
                "points_potential": 15 - breakdown.gear_score,
                "url": "/shop?category=gear",
                "cta_label": "Voir l'équipement",
                "is_purchasable": True
            })
        
        # 5. FORMATION (max 10)
        formations = await db.cart_items.find({"user_id": user_id, "item_type": "formation"}, {"_id": 0}).to_list(100)
        formations_list = formations if isinstance(formations, list) else []
        formations_purchased = len([p for p in purchases_list if isinstance(p, dict) and p.get('item_type') == 'formation'])
        
        total_formations = len(formations_list) + formations_purchased
        
        if total_formations >= 2:
            breakdown.formation_score = 10
        elif total_formations >= 1:
            breakdown.formation_score = 5
        
        breakdown.formation_details = {"formations_count": total_formations}
        
        if total_formations < 2:
            improvements.append({
                "category": "formation",
                "action": "Suivez une formation pour améliorer vos techniques",
                "action_en": "Take a training to improve your techniques",
                "points_potential": 10 - breakdown.formation_score,
                "url": "/formations",
                "cta_label": "Voir les formations",
                "is_purchasable": True,
                "subscription_required": "premium"
            })
        
        # 6. HOTSPOTS (max 10)
        hotspots = await db.cart_items.find({"user_id": user_id, "item_type": "hotspot"}, {"_id": 0}).to_list(100)
        hotspots_list = hotspots if isinstance(hotspots, list) else []
        hotspots_purchased = len([p for p in purchases_list if isinstance(p, dict) and p.get('item_type') == 'hotspot'])
        
        total_hotspots = len(hotspots_list) + hotspots_purchased
        
        if total_hotspots >= 3:
            breakdown.hotspots_score = 10
        elif total_hotspots >= 1:
            breakdown.hotspots_score = 5
        
        breakdown.hotspots_details = {"hotspots_count": total_hotspots}
        
        if total_hotspots < 3:
            improvements.append({
                "category": "hotspots",
                "action": "Achetez des hotspots pour votre territoire",
                "action_en": "Buy hotspots for your territory",
                "points_potential": 10 - breakdown.hotspots_score,
                "url": "/map?layer=hotspots",
                "cta_label": "Acheter / Commander",
                "is_purchasable": True,
                "subscription_required": "premium"
            })
        
        # 7. CAPSULES (max 10)
        if context:
            # Use safe_list to prevent TypeError on corrupted 'pages_visited' field
            pages_visited = safe_list(context, 'pages_visited')
            capsules_viewed = len([p for p in pages_visited if isinstance(p, str) and ('capsule' in p or 'formation' in p)])
            
            if capsules_viewed >= 5:
                breakdown.capsules_score = 10
            elif capsules_viewed >= 3:
                breakdown.capsules_score = 7
            elif capsules_viewed >= 1:
                breakdown.capsules_score = 3
            
            breakdown.capsules_details = {"capsules_viewed": capsules_viewed}
        else:
            breakdown.capsules_details = {"capsules_viewed": 0}
        
        if breakdown.capsules_score < 10:
            improvements.append({
                "category": "capsules",
                "action": "Consultez les capsules éducatives",
                "action_en": "Watch educational capsules",
                "points_potential": 10 - breakdown.capsules_score,
                "url": "/formations",
                "cta_label": "Voir les capsules",
                "is_purchasable": False
            })
        
        # CALCUL TOTAL
        breakdown.total_score = (
            breakdown.permis_score +
            breakdown.setup_score +
            breakdown.territoire_score +
            breakdown.gear_score +
            breakdown.formation_score +
            breakdown.hotspots_score +
            breakdown.capsules_score
        )
        
        # Déterminer le niveau
        for level in READINESS_LEVELS:
            if level['min'] <= breakdown.total_score <= level['max']:
                breakdown.readiness_level = level['name']
                breakdown.readiness_level_en = level['name_en']
                break
        
        # Trier les améliorations par potentiel
        improvements.sort(key=lambda x: -x.get('points_potential', 0))
        breakdown.improvements = improvements[:5]  # Top 5
        
        # Sauvegarder
        await db.preparation_scores.update_one(
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
        """Récupère le classement des mieux préparés"""
        db = await self._get_db()
        
        cursor = db.preparation_scores.find(
            {},
            {"_id": 0, "user_id": 1, "score": 1, "breakdown.readiness_level": 1}
        ).sort("score", -1).limit(limit)
        
        return await cursor.to_list(length=limit)


# Instance globale
score_preparation_service = ScorePreparationService()
