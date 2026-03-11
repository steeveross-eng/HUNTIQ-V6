"""
BIONIC Setup Builder Engine
═══════════════════════════════════════════════════════════════════════════════
Générateur de setup personnalisé:
- Setup complet selon gibier + GPS
- Gear recommandé
- Attractants, vêtements, accessoires
- Techniques de call
- Formations pertinentes
- Upsell Hotspots automatique
═══════════════════════════════════════════════════════════════════════════════
Version: 1.0.0
Date: 2026-02-19
"""

import os
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel


class SetupItemInput(BaseModel):
    """Input pour ajouter un item au cart"""
    item_id: str
    item_type: str
    quantity: int = 1


@dataclass
class SetupItem:
    """Item d'un setup"""
    id: str
    name: str
    name_en: str
    description: str
    category: str
    
    # Prix et achat
    price: Optional[float] = None
    is_purchasable: bool = False
    subscription_required: Optional[str] = None
    product_url: Optional[str] = None
    
    # Métadonnées
    priority: int = 1
    icon: str = "package"
    image_url: Optional[str] = None
    
    # État dans le setup
    is_essential: bool = False
    is_recommended: bool = True


@dataclass 
class HotspotUpsell:
    """Offre hotspot pour upsell"""
    hotspot_count: int = 0
    territory_name: str = ""
    efficiency_score: int = 0
    visual_zones_available: int = 0
    total_price: float = 0.0
    message: str = ""
    message_en: str = ""


@dataclass
class SetupResponse:
    """Réponse du Setup Builder"""
    user_id: str
    gibier: str
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None
    
    # Composants du setup
    gear: List[Dict[str, Any]] = field(default_factory=list)
    attractants: List[Dict[str, Any]] = field(default_factory=list)
    clothing: List[Dict[str, Any]] = field(default_factory=list)
    accessories: List[Dict[str, Any]] = field(default_factory=list)
    call_techniques: List[Dict[str, Any]] = field(default_factory=list)
    formations: List[Dict[str, Any]] = field(default_factory=list)
    
    # Upsell Hotspots
    hotspot_upsell: Optional[Dict[str, Any]] = None
    
    # Totaux
    total_items: int = 0
    total_price: float = 0.0
    
    # Métadonnées
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ═══════════════════════════════════════════════════════════════════════════════
# DONNÉES DE RÉFÉRENCE - SETUPS PAR GIBIER
# ═══════════════════════════════════════════════════════════════════════════════

GEAR_BY_GIBIER = {
    "orignal": [
        {"id": "g_arc_compose", "name": "Arc à poulies", "name_en": "Compound Bow", "category": "arme", "price": 599.99, "is_essential": True},
        {"id": "g_fleches", "name": "Flèches carbone", "name_en": "Carbon Arrows", "category": "munition", "price": 89.99, "is_essential": True},
        {"id": "g_jumelles", "name": "Jumelles 10x42", "name_en": "10x42 Binoculars", "category": "optique", "price": 249.99, "is_essential": True},
        {"id": "g_couteau", "name": "Couteau de dépeçage", "name_en": "Skinning Knife", "category": "outil", "price": 49.99, "is_essential": True},
        {"id": "g_scie", "name": "Scie pliante", "name_en": "Folding Saw", "category": "outil", "price": 34.99},
        {"id": "g_corde", "name": "Corde de hissage", "name_en": "Hoist Rope", "category": "transport", "price": 29.99},
    ],
    "chevreuil": [
        {"id": "g_carabine", "name": "Carabine .308", "name_en": ".308 Rifle", "category": "arme", "price": 899.99, "is_essential": True},
        {"id": "g_munitions_308", "name": "Munitions .308", "name_en": ".308 Ammunition", "category": "munition", "price": 45.99, "is_essential": True},
        {"id": "g_lunette", "name": "Lunette de visée 3-9x40", "name_en": "3-9x40 Scope", "category": "optique", "price": 299.99, "is_essential": True},
        {"id": "g_mirador", "name": "Mirador portatif", "name_en": "Portable Stand", "category": "affût", "price": 179.99},
    ],
    "ours": [
        {"id": "g_carabine_ours", "name": "Carabine .300 Win Mag", "name_en": ".300 Win Mag Rifle", "category": "arme", "price": 1199.99, "is_essential": True},
        {"id": "g_spray_ours", "name": "Spray anti-ours", "name_en": "Bear Spray", "category": "sécurité", "price": 49.99, "is_essential": True},
        {"id": "g_barrel", "name": "Baril d'appât", "name_en": "Bait Barrel", "category": "appât", "price": 89.99},
    ],
    "dindon": [
        {"id": "g_fusil_dindon", "name": "Fusil calibre 12", "name_en": "12 Gauge Shotgun", "category": "arme", "price": 599.99, "is_essential": True},
        {"id": "g_cartouches", "name": "Cartouches Turkey Load", "name_en": "Turkey Load Shells", "category": "munition", "price": 29.99, "is_essential": True},
        {"id": "g_appelant", "name": "Appelant dindon", "name_en": "Turkey Decoy", "category": "leurre", "price": 79.99, "is_essential": True},
    ],
}

ATTRACTANTS_BY_GIBIER = {
    "orignal": [
        {"id": "a_urine_vache", "name": "Urine de vache", "name_en": "Cow Urine", "price": 24.99, "is_essential": True},
        {"id": "a_urine_taureau", "name": "Urine de taureau", "name_en": "Bull Urine", "price": 24.99},
        {"id": "a_sel", "name": "Bloc de sel minéral", "name_en": "Mineral Salt Block", "price": 14.99},
    ],
    "chevreuil": [
        {"id": "a_urine_biche", "name": "Urine de biche", "name_en": "Doe Urine", "price": 19.99, "is_essential": True},
        {"id": "a_tarsal", "name": "Glande tarsale", "name_en": "Tarsal Gland", "price": 29.99},
        {"id": "a_pomme", "name": "Attractant pomme", "name_en": "Apple Attractant", "price": 12.99},
    ],
    "ours": [
        {"id": "a_donuts", "name": "Appât sucré (donuts)", "name_en": "Sweet Bait (donuts)", "price": 34.99, "is_essential": True},
        {"id": "a_bacon", "name": "Graisse de bacon", "name_en": "Bacon Grease", "price": 19.99},
    ],
}

CLOTHING_BY_SEASON = {
    "automne": [
        {"id": "c_camo_automne", "name": "Ensemble camo automne", "name_en": "Fall Camo Set", "price": 199.99, "is_essential": True},
        {"id": "c_bottes", "name": "Bottes isolées", "name_en": "Insulated Boots", "price": 149.99, "is_essential": True},
        {"id": "c_gants", "name": "Gants de chasse", "name_en": "Hunting Gloves", "price": 39.99},
        {"id": "c_tuque", "name": "Tuque camo", "name_en": "Camo Beanie", "price": 24.99},
    ],
    "printemps": [
        {"id": "c_camo_printemps", "name": "Ensemble camo léger", "name_en": "Light Camo Set", "price": 149.99, "is_essential": True},
        {"id": "c_moustiquaire", "name": "Chapeau moustiquaire", "name_en": "Bug Net Hat", "price": 19.99},
    ],
}

CALL_TECHNIQUES = {
    "orignal": [
        {"id": "t_call_vache", "name": "Call de vache", "name_en": "Cow Call", "description": "Imitation du meuglement de la femelle", "price": 34.99},
        {"id": "t_call_taureau", "name": "Call de taureau", "name_en": "Bull Call", "description": "Imitation du grunt du mâle", "price": 34.99},
        {"id": "t_ecorce", "name": "Technique de l'écorce", "name_en": "Bark Technique", "description": "Frotter l'écorce pour simuler un orignal", "price": 0},
        {"id": "t_bouche_orignaux", "name": "De la bouche des orignaux", "name_en": "From the Moose's Mouth", "description": "Formation complète de vocalises", "price": 89.99, "is_formation": True},
    ],
    "chevreuil": [
        {"id": "t_rattle", "name": "Rattle (combat de bois)", "name_en": "Rattling Antlers", "description": "Simulation de combat entre mâles", "price": 49.99},
        {"id": "t_grunt", "name": "Grunt tube", "name_en": "Grunt Tube", "description": "Imitation du grunt du buck", "price": 24.99},
    ],
    "dindon": [
        {"id": "t_box_call", "name": "Box call", "name_en": "Box Call", "description": "Call à friction traditionnel", "price": 39.99},
        {"id": "t_slate_call", "name": "Slate call", "name_en": "Slate Call", "description": "Call en ardoise", "price": 29.99},
        {"id": "t_diaphragm", "name": "Diaphragme", "name_en": "Diaphragm Call", "description": "Call buccal", "price": 14.99},
    ],
}

FORMATIONS_BY_GIBIER = {
    "orignal": [
        {"id": "f_call_orignal", "name": "Maîtriser le call d'orignal", "name_en": "Master Moose Calling", "price": 149.99, "duration": "4h"},
        {"id": "f_pistage", "name": "Pistage avancé", "name_en": "Advanced Tracking", "price": 99.99, "duration": "3h"},
    ],
    "chevreuil": [
        {"id": "f_rut", "name": "Chasse au rut", "name_en": "Rut Hunting", "price": 79.99, "duration": "2h"},
        {"id": "f_affut", "name": "Techniques d'affût", "name_en": "Stand Hunting Techniques", "price": 69.99, "duration": "2h"},
    ],
}


class SetupBuilderService:
    """Service de génération de setups personnalisés"""
    
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
    
    async def generate_setup(
        self, 
        user_id: str,
        gibier: str,
        gps_lat: Optional[float] = None,
        gps_lng: Optional[float] = None,
        season: str = "automne"
    ) -> SetupResponse:
        """
        Génère un setup complet personnalisé.
        Inclut automatiquement l'upsell hotspots si GPS fourni.
        """
        db = await self._get_db()
        
        response = SetupResponse(
            user_id=user_id,
            gibier=gibier,
            gps_lat=gps_lat,
            gps_lng=gps_lng
        )
        
        total_price = 0.0
        total_items = 0
        
        # 1. Gear
        gear_items = GEAR_BY_GIBIER.get(gibier, [])
        for item in gear_items:
            item_copy = item.copy()
            item_copy['is_purchasable'] = True
            item_copy['category'] = 'gear'
            response.gear.append(item_copy)
            if item.get('price'):
                total_price += item['price']
            total_items += 1
        
        # 2. Attractants
        attractants = ATTRACTANTS_BY_GIBIER.get(gibier, [])
        for item in attractants:
            item_copy = item.copy()
            item_copy['is_purchasable'] = True
            item_copy['category'] = 'attractant'
            response.attractants.append(item_copy)
            if item.get('price'):
                total_price += item['price']
            total_items += 1
        
        # 3. Vêtements (selon saison)
        clothing = CLOTHING_BY_SEASON.get(season, CLOTHING_BY_SEASON['automne'])
        for item in clothing:
            item_copy = item.copy()
            item_copy['is_purchasable'] = True
            item_copy['category'] = 'clothing'
            response.clothing.append(item_copy)
            if item.get('price'):
                total_price += item['price']
            total_items += 1
        
        # 4. Techniques de call
        call_techniques = CALL_TECHNIQUES.get(gibier, [])
        for item in call_techniques:
            item_copy = item.copy()
            item_copy['is_purchasable'] = item.get('price', 0) > 0
            item_copy['category'] = 'call_technique'
            response.call_techniques.append(item_copy)
            if item.get('price'):
                total_price += item['price']
            total_items += 1
        
        # 5. Formations
        formations = FORMATIONS_BY_GIBIER.get(gibier, [])
        for item in formations:
            item_copy = item.copy()
            item_copy['is_purchasable'] = True
            item_copy['category'] = 'formation'
            item_copy['subscription_required'] = 'premium'
            response.formations.append(item_copy)
            if item.get('price'):
                total_price += item['price']
            total_items += 1
        
        # 6. UPSELL HOTSPOTS (si GPS fourni)
        if gps_lat and gps_lng:
            # Simulation de hotspots trouvés dans la zone
            hotspot_count = 3  # Simulé
            efficiency_score = 78  # Simulé
            visual_zones = 2  # Simulé
            hotspot_price = hotspot_count * 14.99
            
            response.hotspot_upsell = {
                "hotspot_count": hotspot_count,
                "territory_name": f"Zone GPS ({gps_lat:.2f}, {gps_lng:.2f})",
                "efficiency_score": efficiency_score,
                "visual_zones_available": visual_zones,
                "total_price": hotspot_price,
                "message": f"Nous avons trouvé {hotspot_count} hotspots dans ce territoire",
                "message_en": f"We found {hotspot_count} hotspots in this territory",
                "cta_label": "Acheter / Commander",
                "cta_label_en": "Buy / Order",
                "is_purchasable": True,
                "subscription_required": "premium"
            }
        
        response.total_items = total_items
        response.total_price = round(total_price, 2)
        
        # Sauvegarder le setup généré
        await db.generated_setups.insert_one({
            "user_id": user_id,
            "gibier": gibier,
            "gps_lat": gps_lat,
            "gps_lng": gps_lng,
            "season": season,
            "total_items": total_items,
            "total_price": total_price,
            "generated_at": datetime.now(timezone.utc).isoformat()
        })
        
        return response
    
    async def add_to_cart(
        self, 
        user_id: str, 
        item_id: str,
        item_type: str,
        quantity: int = 1
    ) -> Dict[str, Any]:
        """
        Ajoute un item du setup au panier.
        Redirige vers le niveau d'abonnement si nécessaire.
        """
        db = await self._get_db()
        
        # Trouver l'item dans les données
        all_items = []
        for items in GEAR_BY_GIBIER.values():
            all_items.extend(items)
        for items in ATTRACTANTS_BY_GIBIER.values():
            all_items.extend(items)
        for items in CLOTHING_BY_SEASON.values():
            all_items.extend(items)
        for items in CALL_TECHNIQUES.values():
            all_items.extend(items)
        for items in FORMATIONS_BY_GIBIER.values():
            all_items.extend(items)
        
        item = next((i for i in all_items if i.get('id') == item_id), None)
        
        if not item:
            return {"success": False, "error": "Item non trouvé"}
        
        # Ajouter au panier
        cart_item = {
            "user_id": user_id,
            "item_id": item_id,
            "item_type": item_type,
            "name": item.get('name'),
            "price": item.get('price', 0),
            "quantity": quantity,
            "added_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.cart_items.insert_one(cart_item)
        
        return {
            "success": True,
            "item_added": item_id,
            "cart_action": "add",
            "redirect_to_pricing": item.get('subscription_required') is not None,
            "subscription_required": item.get('subscription_required')
        }


# Instance globale
setup_builder_service = SetupBuilderService()
