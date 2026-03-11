"""
BIONIC Next Step Engine
═══════════════════════════════════════════════════════════════════════════════
Moteur de génération automatique des prochaines étapes pertinentes:
- Détection de l'action utilisateur
- Lecture du contexte (gibier, région, GPS, saison)
- Génération de 3-5 NEXT STEPS pertinents
- Priorité: Analyse de Territoire
═══════════════════════════════════════════════════════════════════════════════
Version: 1.0.0
Date: 2026-02-19
"""

import os
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from motor.motor_asyncio import AsyncIOMotorClient
from enum import Enum


class ActionType(str, Enum):
    """Types d'actions déclenchant le Next Step Engine"""
    PERMIS_CONSULTED = "permis_consulted"
    TERRITORY_VIEWED = "territory_viewed"
    SETUP_VIEWED = "setup_viewed"
    POURVOIRIE_VIEWED = "pourvoirie_viewed"
    FORMATION_VIEWED = "formation_viewed"
    HOTSPOT_VIEWED = "hotspot_viewed"
    CART_UPDATED = "cart_updated"
    PROFILE_COMPLETED = "profile_completed"
    LOGIN = "login"
    PURCHASE = "purchase"


class SubscriptionLevel(str, Enum):
    """Niveaux d'abonnement"""
    FREE = "free"
    PREMIUM = "premium"
    PRO = "pro"


@dataclass
class NextStep:
    """Une étape recommandée"""
    id: str
    title: str
    title_en: str
    description: str
    description_en: str
    action_url: str
    action_label: str
    action_label_en: str
    
    # Métadonnées
    priority: int = 1  # 1 = highest
    category: str = "general"
    icon: str = "arrow-right"
    
    # E-commerce
    is_purchasable: bool = False
    price: Optional[float] = None
    subscription_required: Optional[str] = None
    
    # État
    is_completed: bool = False


@dataclass
class NextStepsResponse:
    """Réponse du Next Step Engine"""
    user_id: str
    trigger_action: str
    steps: List[Dict[str, Any]] = field(default_factory=list)
    context_summary: Dict[str, Any] = field(default_factory=dict)
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ═══════════════════════════════════════════════════════════════════════════════
# DÉFINITION DES NEXT STEPS PAR CONTEXTE
# ═══════════════════════════════════════════════════════════════════════════════

# Priorité 1: Analyse de territoire (TOUJOURS en premier)
STEP_TERRITORY_ANALYSIS = {
    "id": "territory_analysis",
    "title": "Analysez votre territoire",
    "title_en": "Analyze your territory",
    "description": "Carte interactive avec hotspots, zones de passage et scoring BIONIC",
    "description_en": "Interactive map with hotspots, travel routes and BIONIC scoring",
    "action_url": "/territoire",
    "action_label": "Analyser maintenant",
    "action_label_en": "Analyze now",
    "priority": 1,
    "category": "territory",
    "icon": "map",
    "is_purchasable": False
}

STEP_INTERACTIVE_MAP = {
    "id": "interactive_map",
    "title": "Carte interactive BIONIC",
    "title_en": "BIONIC Interactive Map",
    "description": "Explorez votre territoire avec les couches GPS et waypoints",
    "description_en": "Explore your territory with GPS layers and waypoints",
    "action_url": "/map",
    "action_label": "Ouvrir la carte",
    "action_label_en": "Open map",
    "priority": 2,
    "category": "territory",
    "icon": "globe",
    "is_purchasable": False
}

STEP_HOTSPOTS = {
    "id": "discover_hotspots",
    "title": "Découvrir les Hotspots",
    "title_en": "Discover Hotspots",
    "description": "Zones à fort potentiel identifiées par l'IA BIONIC",
    "description_en": "High potential zones identified by BIONIC AI",
    "action_url": "/map?layer=hotspots",
    "action_label": "Voir les hotspots",
    "action_label_en": "View hotspots",
    "priority": 3,
    "category": "territory",
    "icon": "target",
    "is_purchasable": True,
    "price": 14.99,
    "subscription_required": "premium"
}

STEP_SETUP_BUILDER = {
    "id": "setup_builder",
    "title": "Construire mon Setup",
    "title_en": "Build my Setup",
    "description": "Setup personnalisé selon votre gibier et territoire",
    "description_en": "Personalized setup for your game and territory",
    "action_url": "/setup-builder",
    "action_label": "Créer mon setup",
    "action_label_en": "Create my setup",
    "priority": 4,
    "category": "preparation",
    "icon": "settings",
    "is_purchasable": False
}

STEP_POURVOIRIE = {
    "id": "find_pourvoirie",
    "title": "Trouver une pourvoirie",
    "title_en": "Find an outfitter",
    "description": "Pourvoiries recommandées selon votre profil",
    "description_en": "Recommended outfitters for your profile",
    "action_url": "/pourvoiries",
    "action_label": "Explorer",
    "action_label_en": "Explore",
    "priority": 5,
    "category": "planning",
    "icon": "home",
    "is_purchasable": True
}

STEP_FORMATIONS = {
    "id": "formations",
    "title": "Formations disponibles",
    "title_en": "Available Training",
    "description": "Améliorez vos techniques avec nos formations",
    "description_en": "Improve your techniques with our training",
    "action_url": "/formations",
    "action_label": "Voir les formations",
    "action_label_en": "View training",
    "priority": 6,
    "category": "education",
    "icon": "graduation-cap",
    "is_purchasable": True
}

STEP_GEAR = {
    "id": "recommended_gear",
    "title": "Équipement recommandé",
    "title_en": "Recommended Gear",
    "description": "Gear optimisé pour votre gibier et saison",
    "description_en": "Optimized gear for your game and season",
    "action_url": "/shop?category=gear",
    "action_label": "Voir l'équipement",
    "action_label_en": "View gear",
    "priority": 7,
    "category": "gear",
    "icon": "package",
    "is_purchasable": True
}

STEP_FORECAST = {
    "id": "weather_forecast",
    "title": "Prévisions météo",
    "title_en": "Weather Forecast",
    "description": "Conditions optimales pour votre prochaine sortie",
    "description_en": "Optimal conditions for your next trip",
    "action_url": "/forecast",
    "action_label": "Voir les prévisions",
    "action_label_en": "View forecast",
    "priority": 8,
    "category": "planning",
    "icon": "cloud",
    "is_purchasable": False
}

STEP_PLAN_SAISON = {
    "id": "season_plan",
    "title": "Plan de saison personnalisé",
    "title_en": "Personalized Season Plan",
    "description": "Planifiez votre saison complète avec BIONIC",
    "description_en": "Plan your full season with BIONIC",
    "action_url": "/plan-saison",
    "action_label": "Créer mon plan",
    "action_label_en": "Create my plan",
    "priority": 9,
    "category": "planning",
    "icon": "calendar",
    "is_purchasable": False,
    "subscription_required": "premium"
}

STEP_LISTE_EPICERIE = {
    "id": "shopping_list",
    "title": "Ma liste d'épicerie",
    "title_en": "My Shopping List",
    "description": "Tout ce dont vous avez besoin pour votre chasse",
    "description_en": "Everything you need for your hunt",
    "action_url": "/liste-epicerie",
    "action_label": "Voir ma liste",
    "action_label_en": "View my list",
    "priority": 10,
    "category": "preparation",
    "icon": "shopping-cart",
    "is_purchasable": True
}


# ═══════════════════════════════════════════════════════════════════════════════
# RÈGLES DE GÉNÉRATION PAR ACTION
# ═══════════════════════════════════════════════════════════════════════════════

STEPS_BY_ACTION = {
    ActionType.PERMIS_CONSULTED: [
        STEP_TERRITORY_ANALYSIS,  # TOUJOURS en premier
        STEP_INTERACTIVE_MAP,
        STEP_HOTSPOTS,
        STEP_SETUP_BUILDER,
        STEP_FORECAST
    ],
    ActionType.TERRITORY_VIEWED: [
        STEP_HOTSPOTS,
        STEP_SETUP_BUILDER,
        STEP_POURVOIRIE,
        STEP_FORECAST,
        STEP_GEAR
    ],
    ActionType.SETUP_VIEWED: [
        STEP_TERRITORY_ANALYSIS,
        STEP_GEAR,
        STEP_LISTE_EPICERIE,
        STEP_POURVOIRIE,
        STEP_FORMATIONS
    ],
    ActionType.POURVOIRIE_VIEWED: [
        STEP_TERRITORY_ANALYSIS,
        STEP_SETUP_BUILDER,
        STEP_FORECAST,
        STEP_GEAR,
        STEP_FORMATIONS
    ],
    ActionType.FORMATION_VIEWED: [
        STEP_TERRITORY_ANALYSIS,
        STEP_SETUP_BUILDER,
        STEP_GEAR,
        STEP_HOTSPOTS,
        STEP_PLAN_SAISON
    ],
    ActionType.LOGIN: [
        STEP_TERRITORY_ANALYSIS,
        STEP_FORECAST,
        STEP_PLAN_SAISON,
        STEP_FORMATIONS,
        STEP_GEAR
    ],
    ActionType.PROFILE_COMPLETED: [
        STEP_TERRITORY_ANALYSIS,
        STEP_SETUP_BUILDER,
        STEP_HOTSPOTS,
        STEP_PLAN_SAISON,
        STEP_POURVOIRIE
    ]
}


class NextStepEngine:
    """Moteur de génération des prochaines étapes"""
    
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
    
    async def generate_next_steps(
        self, 
        user_id: str, 
        action: ActionType,
        max_steps: int = 5
    ) -> NextStepsResponse:
        """
        Génère les prochaines étapes recommandées.
        
        RÈGLE: Le premier NEXT STEP est TOUJOURS l'analyse de territoire.
        """
        db = await self._get_db()
        
        # Récupérer le contexte utilisateur
        context = await db.user_contexts.find_one({"user_id": user_id}, {"_id": 0})
        context = context or {}
        
        # Récupérer les steps pour cette action
        base_steps = STEPS_BY_ACTION.get(action, STEPS_BY_ACTION[ActionType.LOGIN])
        
        # Personnaliser selon le contexte
        steps = []
        for step_template in base_steps[:max_steps]:
            step = step_template.copy()
            
            # Adapter le step selon le gibier
            gibier = context.get('gibier_principal')
            if gibier:
                step['description'] = step['description'].replace(
                    'votre gibier', 
                    f"l'{gibier}"
                )
            
            # Vérifier si déjà complété
            completed_actions = context.get('pages_visited', [])
            if step['action_url'] in completed_actions:
                step['is_completed'] = True
            
            steps.append(step)
        
        # S'assurer que l'analyse de territoire est TOUJOURS en premier
        territory_step = next((s for s in steps if s['id'] == 'territory_analysis'), None)
        if territory_step:
            steps.remove(territory_step)
            steps.insert(0, territory_step)
        elif action != ActionType.TERRITORY_VIEWED:
            steps.insert(0, STEP_TERRITORY_ANALYSIS)
            steps = steps[:max_steps]
        
        # Sauvegarder l'historique
        await db.next_steps_history.insert_one({
            "user_id": user_id,
            "action": action.value,
            "steps_generated": [s['id'] for s in steps],
            "context": {
                "gibier": context.get('gibier_principal'),
                "region": context.get('region'),
                "season": context.get('current_season')
            },
            "generated_at": datetime.now(timezone.utc).isoformat()
        })
        
        return NextStepsResponse(
            user_id=user_id,
            trigger_action=action.value,
            steps=steps,
            context_summary={
                "gibier": context.get('gibier_principal'),
                "region": context.get('region'),
                "season": context.get('current_season'),
                "has_gps": bool(context.get('gps_lat'))
            }
        )
    
    async def mark_step_completed(
        self, 
        user_id: str, 
        step_id: str
    ) -> bool:
        """Marque un step comme complété"""
        db = await self._get_db()
        
        await db.completed_steps.update_one(
            {"user_id": user_id, "step_id": step_id},
            {"$set": {
                "user_id": user_id,
                "step_id": step_id,
                "completed_at": datetime.now(timezone.utc).isoformat()
            }},
            upsert=True
        )
        
        return True
    
    async def get_completed_steps(self, user_id: str) -> List[str]:
        """Récupère les IDs des steps complétés"""
        db = await self._get_db()
        
        cursor = db.completed_steps.find({"user_id": user_id}, {"_id": 0, "step_id": 1})
        docs = await cursor.to_list(length=100)
        
        return [doc['step_id'] for doc in docs]


# Instance globale
next_step_engine = NextStepEngine()
