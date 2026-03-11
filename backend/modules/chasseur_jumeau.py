"""
BIONIC Chasseur Jumeau Engine
═══════════════════════════════════════════════════════════════════════════════
Comparaison avec des profils similaires:
- Matching par gibier, région, expérience
- Recommandations de setups, gear, formations
- Sans hotspots (pour éviter cannibalisation)
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
from dataclasses import dataclass, field
from motor.motor_asyncio import AsyncIOMotorClient
import random

# Import safe_list for type-safe data access
from utils.safe_get import safe_list

# Logger for type correction logging
logger = logging.getLogger(__name__)


@dataclass
class ChasseurProfile:
    """Profil d'un chasseur jumeau"""
    id: str
    pseudo: str
    
    # Caractéristiques
    gibier_principal: str
    region: str
    experience_years: int
    hunter_score: int
    
    # Équipement utilisé
    gear_used: List[str] = field(default_factory=list)
    
    # Formations suivies
    formations_completed: List[str] = field(default_factory=list)
    
    # Stats
    trips_count: int = 0
    success_rate: float = 0.0
    
    # Match score
    similarity_score: int = 0


@dataclass
class ChasseurJumeauResponse:
    """Réponse du moteur Chasseur Jumeau"""
    user_id: str
    
    # Profils similaires
    similar_profiles: List[Dict[str, Any]] = field(default_factory=list)
    
    # Recommandations agrégées
    recommended_setups: List[Dict[str, Any]] = field(default_factory=list)
    recommended_gear: List[Dict[str, Any]] = field(default_factory=list)
    recommended_formations: List[Dict[str, Any]] = field(default_factory=list)
    recommended_pourvoiries: List[Dict[str, Any]] = field(default_factory=list)
    recommended_capsules: List[Dict[str, Any]] = field(default_factory=list)
    
    # Métadonnées
    total_similar_found: int = 0
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ═══════════════════════════════════════════════════════════════════════════════
# PROFILS SIMULÉS
# ═══════════════════════════════════════════════════════════════════════════════

MOCK_PROFILES = [
    {
        "id": "prof_001",
        "pseudo": "ChasseurNord47",
        "gibier_principal": "orignal",
        "region": "Laurentides",
        "experience_years": 8,
        "hunter_score": 85,
        "gear_used": ["Arc à poulies", "Jumelles 10x42", "Call de vache"],
        "formations_completed": ["Maîtriser le call d'orignal"],
        "trips_count": 45,
        "success_rate": 0.72
    },
    {
        "id": "prof_002",
        "pseudo": "LoupDesMauricie",
        "gibier_principal": "orignal",
        "region": "Mauricie",
        "experience_years": 12,
        "hunter_score": 92,
        "gear_used": ["Carabine .308", "Lunette 3-9x40", "Mirador"],
        "formations_completed": ["De la bouche des orignaux", "Pistage avancé"],
        "trips_count": 78,
        "success_rate": 0.85
    },
    {
        "id": "prof_003",
        "pseudo": "CerfBlancEstrie",
        "gibier_principal": "chevreuil",
        "region": "Estrie",
        "experience_years": 5,
        "hunter_score": 78,
        "gear_used": ["Carabine .270", "Grunt tube", "Rattle"],
        "formations_completed": ["Chasse au rut"],
        "trips_count": 32,
        "success_rate": 0.65
    },
    {
        "id": "prof_004",
        "pseudo": "OursNoir08",
        "gibier_principal": "ours",
        "region": "Abitibi-Témiscamingue",
        "experience_years": 10,
        "hunter_score": 88,
        "gear_used": ["Carabine .300 Win Mag", "Baril d'appât", "Spray anti-ours"],
        "formations_completed": [],
        "trips_count": 25,
        "success_rate": 0.78
    },
    {
        "id": "prof_005",
        "pseudo": "DindonMaster",
        "gibier_principal": "dindon",
        "region": "Montérégie",
        "experience_years": 6,
        "hunter_score": 82,
        "gear_used": ["Fusil cal. 12", "Box call", "Slate call", "Appelant"],
        "formations_completed": [],
        "trips_count": 40,
        "success_rate": 0.55
    },
]

# Recommandations basées sur les profils
RECOMMENDATIONS_BY_GIBIER = {
    "orignal": {
        "setups": [
            {"id": "setup_orignal", "name": "Setup Orignal Pro", "price": 1299.99, "description": "Setup utilisé par 85% des chasseurs experts"},
        ],
        "gear": [
            {"id": "gear_jumelles", "name": "Jumelles HD 10x42", "price": 299.99, "popularity": 92},
            {"id": "gear_call", "name": "Call professionnel orignal", "price": 79.99, "popularity": 88},
        ],
        "formations": [
            {"id": "form_call", "name": "De la bouche des orignaux", "price": 199.99, "completions": 450},
        ],
        "capsules": [
            {"id": "cap_001", "name": "Les secrets du rut de l'orignal", "duration": "15min", "views": 12500},
            {"id": "cap_002", "name": "Techniques de call avancées", "duration": "22min", "views": 8900},
        ],
    },
    "chevreuil": {
        "setups": [
            {"id": "setup_chevreuil", "name": "Setup Chevreuil Complet", "price": 899.99, "description": "Setup recommandé par les pros"},
        ],
        "gear": [
            {"id": "gear_grunt", "name": "Grunt Tube Pro", "price": 34.99, "popularity": 95},
            {"id": "gear_rattle", "name": "Rattle Antlers authentiques", "price": 59.99, "popularity": 82},
        ],
        "formations": [
            {"id": "form_rut", "name": "Chasse au rut - Stratégies gagnantes", "price": 79.99, "completions": 680},
        ],
        "capsules": [
            {"id": "cap_003", "name": "Comprendre le comportement du buck", "duration": "18min", "views": 15200},
        ],
    },
}


class ChasseurJumeauService:
    """Service de matching chasseur jumeau"""
    
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
    
    def _calculate_similarity(
        self,
        user_context: Dict[str, Any],
        profile: Dict[str, Any]
    ) -> int:
        """Calcule le score de similarité entre un utilisateur et un profil"""
        score = 0
        
        # Gibier principal (40 points max)
        if user_context.get('gibier_principal') == profile.get('gibier_principal'):
            score += 40
        
        # Région (30 points max)
        if user_context.get('region') == profile.get('region'):
            score += 30
        elif user_context.get('province') == "QC":
            score += 15  # Même province
        
        # Expérience similaire (20 points max)
        # Use safe_list to prevent TypeError on corrupted 'tools_used' field
        tools_used = safe_list(user_context, 'tools_used')
        user_tools = len(tools_used)
        profile_exp = profile.get('experience_years', 0)
        if user_tools < 3 and profile_exp < 5:
            score += 20  # Débutants
        elif 3 <= user_tools < 6 and 5 <= profile_exp < 10:
            score += 20  # Intermédiaires
        elif user_tools >= 6 and profile_exp >= 10:
            score += 20  # Experts
        else:
            score += 10  # Match partiel
        
        # Bonus aléatoire pour variété (10 points max)
        score += random.randint(0, 10)
        
        return min(100, score)
    
    async def find_similar_profiles(
        self,
        user_id: str,
        limit: int = 5
    ) -> ChasseurJumeauResponse:
        """
        Trouve les profils similaires et génère des recommandations.
        NOTE: Sans hotspots pour éviter cannibalisation.
        """
        db = await self._get_db()
        
        # Récupérer le contexte utilisateur
        user_context = await db.user_contexts.find_one({"user_id": user_id}, {"_id": 0})
        user_context = user_context or {}
        
        response = ChasseurJumeauResponse(user_id=user_id)
        
        # Calculer les similarités
        profiles_with_scores = []
        for profile in MOCK_PROFILES:
            similarity = self._calculate_similarity(user_context, profile)
            profile_copy = profile.copy()
            profile_copy['similarity_score'] = similarity
            profiles_with_scores.append(profile_copy)
        
        # Trier par similarité
        profiles_with_scores.sort(key=lambda x: -x['similarity_score'])
        
        # Garder les meilleurs
        response.similar_profiles = profiles_with_scores[:limit]
        response.total_similar_found = len(profiles_with_scores)
        
        # Générer les recommandations basées sur le gibier
        gibier = user_context.get('gibier_principal', 'orignal')
        recommendations = RECOMMENDATIONS_BY_GIBIER.get(gibier, RECOMMENDATIONS_BY_GIBIER['orignal'])
        
        # Ajouter les infos d'achat
        for setup in recommendations.get('setups', []):
            setup_copy = setup.copy()
            setup_copy['is_purchasable'] = True
            setup_copy['cta_label'] = "Acheter / Commander"
            setup_copy['cta_label_en'] = "Buy / Order"
            response.recommended_setups.append(setup_copy)
        
        for gear in recommendations.get('gear', []):
            gear_copy = gear.copy()
            gear_copy['is_purchasable'] = True
            gear_copy['cta_label'] = "Acheter / Commander"
            gear_copy['cta_label_en'] = "Buy / Order"
            response.recommended_gear.append(gear_copy)
        
        for formation in recommendations.get('formations', []):
            formation_copy = formation.copy()
            formation_copy['is_purchasable'] = True
            formation_copy['subscription_required'] = "premium"
            formation_copy['cta_label'] = "Acheter / Commander"
            formation_copy['cta_label_en'] = "Buy / Order"
            response.recommended_formations.append(formation_copy)
        
        for capsule in recommendations.get('capsules', []):
            capsule_copy = capsule.copy()
            capsule_copy['is_purchasable'] = False  # Capsules incluses dans l'abonnement
            capsule_copy['subscription_required'] = "free"
            response.recommended_capsules.append(capsule_copy)
        
        # Recommander des pourvoiries basées sur les profils similaires
        regions_populaires = [p['region'] for p in response.similar_profiles if p.get('success_rate', 0) > 0.7]
        if regions_populaires:
            response.recommended_pourvoiries.append({
                "id": "pv_rec_001",
                "name": f"Pourvoiries populaires en {regions_populaires[0]}",
                "region": regions_populaires[0],
                "is_purchasable": True,
                "cta_label": "Voir les pourvoiries",
                "cta_label_en": "View outfitters"
            })
        
        # Sauvegarder la recherche
        await db.chasseur_jumeau_searches.insert_one({
            "user_id": user_id,
            "gibier": gibier,
            "profiles_found": len(response.similar_profiles),
            "searched_at": datetime.now(timezone.utc).isoformat()
        })
        
        return response
    
    async def add_recommendation_to_cart(
        self,
        user_id: str,
        item_id: str,
        item_type: str
    ) -> Dict[str, Any]:
        """Ajoute une recommandation au panier"""
        db = await self._get_db()
        
        # Trouver l'item dans les recommandations
        item = None
        for gibier_recs in RECOMMENDATIONS_BY_GIBIER.values():
            for category in ['setups', 'gear', 'formations']:
                for i in gibier_recs.get(category, []):
                    if i.get('id') == item_id:
                        item = i
                        break
        
        if not item:
            return {"success": False, "error": "Item non trouvé"}
        
        cart_item = {
            "user_id": user_id,
            "item_id": item_id,
            "item_type": item_type,
            "name": item.get('name'),
            "price": item.get('price', 0),
            "quantity": 1,
            "source": "chasseur_jumeau",
            "added_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.cart_items.insert_one(cart_item)
        
        return {
            "success": True,
            "item_id": item_id,
            "cart_action": "added",
            "redirect_to_pricing": item.get('subscription_required') is not None,
            "subscription_required": item.get('subscription_required')
        }


# Instance globale
chasseur_jumeau_service = ChasseurJumeauService()
