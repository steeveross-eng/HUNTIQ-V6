"""
BIONIC Liste d'Épicerie Engine
═══════════════════════════════════════════════════════════════════════════════
Génération de liste personnalisée:
- Gear essentiel
- Attractants
- Vêtements
- Accessoires
- Formations
- Techniques de call
- Hotspots
- Cartes BIONIC
- Zones visuelles
- Setups
- Pourvoiries

Chaque item avec prix, niveau d'abonnement, bouton Acheter/Commander.
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


class ItemCategory(str, Enum):
    """Catégories d'items"""
    GEAR = "gear"
    ATTRACTANT = "attractant"
    CLOTHING = "clothing"
    ACCESSORY = "accessory"
    FORMATION = "formation"
    CALL_TECHNIQUE = "call_technique"
    HOTSPOT = "hotspot"
    BIONIC_MAP = "bionic_map"
    VISUAL_ZONE = "visual_zone"
    SETUP = "setup"
    POURVOIRIE = "pourvoirie"
    SERVICE = "service"


@dataclass
class ListeEpicerieItem:
    """Item de la liste d'épicerie"""
    id: str
    name: str
    name_en: str
    category: str
    
    # Prix et achat
    price: float = 0.0
    is_purchasable: bool = True
    subscription_required: Optional[str] = None  # free, premium, pro
    
    # État
    is_essential: bool = False
    is_in_cart: bool = False
    quantity: int = 1
    
    # Métadonnées
    description: Optional[str] = None
    image_url: Optional[str] = None
    product_url: Optional[str] = None
    
    # CTA
    cta_label: str = "Acheter / Commander"
    cta_label_en: str = "Buy / Order"


@dataclass
class ListeEpicerieResponse:
    """Réponse de la liste d'épicerie"""
    user_id: str
    gibier: str
    
    # Items par catégorie
    items: List[Dict[str, Any]] = field(default_factory=list)
    
    # Totaux
    total_items: int = 0
    total_essential: int = 0
    total_price: float = 0.0
    items_in_cart: int = 0
    
    # Statistiques par catégorie
    by_category: Dict[str, int] = field(default_factory=dict)
    
    # Métadonnées
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ═══════════════════════════════════════════════════════════════════════════════
# CATALOGUE COMPLET
# ═══════════════════════════════════════════════════════════════════════════════

CATALOGUE = {
    # GEAR
    "gear": [
        {"id": "gear_001", "name": "Arc à poulies complet", "name_en": "Complete Compound Bow", "price": 599.99, "is_essential": True, "subscription_required": None},
        {"id": "gear_002", "name": "Carabine .308 Win", "name_en": ".308 Win Rifle", "price": 899.99, "is_essential": True, "subscription_required": None},
        {"id": "gear_003", "name": "Fusil calibre 12", "name_en": "12 Gauge Shotgun", "price": 549.99, "is_essential": True, "subscription_required": None},
        {"id": "gear_004", "name": "Jumelles 10x42 HD", "name_en": "10x42 HD Binoculars", "price": 299.99, "is_essential": True, "subscription_required": None},
        {"id": "gear_005", "name": "Lunette de visée 3-9x40", "name_en": "3-9x40 Scope", "price": 349.99, "is_essential": False, "subscription_required": None},
        {"id": "gear_006", "name": "Couteau de chasse", "name_en": "Hunting Knife", "price": 79.99, "is_essential": True, "subscription_required": None},
        {"id": "gear_007", "name": "Scie pliante", "name_en": "Folding Saw", "price": 34.99, "is_essential": False, "subscription_required": None},
        {"id": "gear_008", "name": "Mirador portable", "name_en": "Portable Tree Stand", "price": 249.99, "is_essential": False, "subscription_required": None},
    ],
    
    # ATTRACTANTS
    "attractant": [
        {"id": "attr_001", "name": "Urine de vache (orignal)", "name_en": "Cow Moose Urine", "price": 24.99, "is_essential": True, "subscription_required": None},
        {"id": "attr_002", "name": "Urine de taureau (orignal)", "name_en": "Bull Moose Urine", "price": 24.99, "is_essential": False, "subscription_required": None},
        {"id": "attr_003", "name": "Urine de biche", "name_en": "Doe Urine", "price": 19.99, "is_essential": True, "subscription_required": None},
        {"id": "attr_004", "name": "Glande tarsale", "name_en": "Tarsal Gland", "price": 29.99, "is_essential": False, "subscription_required": None},
        {"id": "attr_005", "name": "Bloc de sel minéral", "name_en": "Mineral Salt Block", "price": 14.99, "is_essential": False, "subscription_required": None},
        {"id": "attr_006", "name": "Attractant pomme", "name_en": "Apple Attractant", "price": 12.99, "is_essential": False, "subscription_required": None},
    ],
    
    # CLOTHING
    "clothing": [
        {"id": "cloth_001", "name": "Ensemble camo complet", "name_en": "Complete Camo Set", "price": 249.99, "is_essential": True, "subscription_required": None},
        {"id": "cloth_002", "name": "Bottes isolées", "name_en": "Insulated Boots", "price": 189.99, "is_essential": True, "subscription_required": None},
        {"id": "cloth_003", "name": "Gants de chasse", "name_en": "Hunting Gloves", "price": 49.99, "is_essential": True, "subscription_required": None},
        {"id": "cloth_004", "name": "Tuque camo", "name_en": "Camo Beanie", "price": 29.99, "is_essential": False, "subscription_required": None},
        {"id": "cloth_005", "name": "Veste orange sécurité", "name_en": "Safety Orange Vest", "price": 39.99, "is_essential": True, "subscription_required": None},
        {"id": "cloth_006", "name": "Sous-vêtements thermiques", "name_en": "Thermal Underwear", "price": 79.99, "is_essential": True, "subscription_required": None},
    ],
    
    # ACCESSOIRES
    "accessory": [
        {"id": "acc_001", "name": "Sac à dos de chasse 45L", "name_en": "45L Hunting Backpack", "price": 149.99, "is_essential": True, "subscription_required": None},
        {"id": "acc_002", "name": "Lampe frontale", "name_en": "Headlamp", "price": 49.99, "is_essential": True, "subscription_required": None},
        {"id": "acc_003", "name": "Corde de hissage", "name_en": "Hoist Rope", "price": 29.99, "is_essential": False, "subscription_required": None},
        {"id": "acc_004", "name": "GPS portable", "name_en": "Portable GPS", "price": 299.99, "is_essential": False, "subscription_required": None},
        {"id": "acc_005", "name": "Trousse premiers soins", "name_en": "First Aid Kit", "price": 39.99, "is_essential": True, "subscription_required": None},
        {"id": "acc_006", "name": "Radio bidirectionnelle", "name_en": "Two-Way Radio", "price": 89.99, "is_essential": False, "subscription_required": None},
    ],
    
    # FORMATIONS
    "formation": [
        {"id": "form_001", "name": "Maîtriser le call d'orignal", "name_en": "Master Moose Calling", "price": 149.99, "is_essential": False, "subscription_required": "premium"},
        {"id": "form_002", "name": "De la bouche des orignaux", "name_en": "From the Moose's Mouth", "price": 199.99, "is_essential": False, "subscription_required": "premium"},
        {"id": "form_003", "name": "Pistage avancé", "name_en": "Advanced Tracking", "price": 99.99, "is_essential": False, "subscription_required": "premium"},
        {"id": "form_004", "name": "Chasse au rut", "name_en": "Rut Hunting", "price": 79.99, "is_essential": False, "subscription_required": "premium"},
        {"id": "form_005", "name": "Techniques d'affût", "name_en": "Stand Hunting Techniques", "price": 69.99, "is_essential": False, "subscription_required": "free"},
    ],
    
    # CALL TECHNIQUES
    "call_technique": [
        {"id": "call_001", "name": "Call de vache orignal", "name_en": "Cow Moose Call", "price": 34.99, "is_essential": True, "subscription_required": None},
        {"id": "call_002", "name": "Call de taureau orignal", "name_en": "Bull Moose Call", "price": 34.99, "is_essential": False, "subscription_required": None},
        {"id": "call_003", "name": "Rattle (bois de cerf)", "name_en": "Rattling Antlers", "price": 49.99, "is_essential": False, "subscription_required": None},
        {"id": "call_004", "name": "Grunt tube chevreuil", "name_en": "Deer Grunt Tube", "price": 24.99, "is_essential": True, "subscription_required": None},
        {"id": "call_005", "name": "Box call dindon", "name_en": "Turkey Box Call", "price": 39.99, "is_essential": True, "subscription_required": None},
    ],
    
    # HOTSPOTS
    "hotspot": [
        {"id": "hot_001", "name": "Pack 3 Hotspots Zone Nord", "name_en": "3 Hotspots Pack North Zone", "price": 44.97, "is_essential": False, "subscription_required": "premium"},
        {"id": "hot_002", "name": "Pack 5 Hotspots Premium", "name_en": "5 Premium Hotspots Pack", "price": 69.95, "is_essential": False, "subscription_required": "premium"},
        {"id": "hot_003", "name": "Hotspot Unitaire", "name_en": "Single Hotspot", "price": 14.99, "is_essential": False, "subscription_required": "premium"},
    ],
    
    # CARTES BIONIC
    "bionic_map": [
        {"id": "map_001", "name": "Carte BIONIC Territoire 50km²", "name_en": "BIONIC Territory Map 50km²", "price": 29.99, "is_essential": False, "subscription_required": "free"},
        {"id": "map_002", "name": "Carte BIONIC Territoire 100km²", "name_en": "BIONIC Territory Map 100km²", "price": 49.99, "is_essential": False, "subscription_required": "premium"},
        {"id": "map_003", "name": "Carte BIONIC Illimitée", "name_en": "BIONIC Unlimited Map", "price": 99.99, "is_essential": False, "subscription_required": "pro"},
    ],
    
    # ZONES VISUELLES
    "visual_zone": [
        {"id": "viz_001", "name": "Zone visuelle d'achalandage", "name_en": "Traffic Visual Zone", "price": 19.99, "is_essential": False, "subscription_required": "premium"},
        {"id": "viz_002", "name": "Pack 3 zones visuelles", "name_en": "3 Visual Zones Pack", "price": 49.99, "is_essential": False, "subscription_required": "premium"},
    ],
    
    # SETUPS
    "setup": [
        {"id": "setup_001", "name": "Setup Orignal Complet", "name_en": "Complete Moose Setup", "price": 1299.99, "is_essential": False, "subscription_required": "premium"},
        {"id": "setup_002", "name": "Setup Chevreuil Complet", "name_en": "Complete Deer Setup", "price": 899.99, "is_essential": False, "subscription_required": "premium"},
        {"id": "setup_003", "name": "Setup Dindon Complet", "name_en": "Complete Turkey Setup", "price": 599.99, "is_essential": False, "subscription_required": "free"},
    ],
    
    # SERVICES
    "service": [
        {"id": "serv_001", "name": "Consultation BIONIC 1h", "name_en": "1h BIONIC Consultation", "price": 99.99, "is_essential": False, "subscription_required": "premium"},
        {"id": "serv_002", "name": "Analyse territoire personnalisée", "name_en": "Personalized Territory Analysis", "price": 149.99, "is_essential": False, "subscription_required": "pro"},
        {"id": "serv_003", "name": "Plan de saison sur mesure", "name_en": "Custom Season Plan", "price": 199.99, "is_essential": False, "subscription_required": "pro"},
    ],
}


class ListeEpicerieService:
    """Service de gestion de la liste d'épicerie"""
    
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
    
    async def generate_liste(
        self,
        user_id: str,
        gibier: str,
        include_categories: Optional[List[str]] = None
    ) -> ListeEpicerieResponse:
        """
        Génère une liste d'épicerie personnalisée.
        """
        db = await self._get_db()
        
        # Récupérer le panier existant
        cart_items = await db.cart_items.find({"user_id": user_id}, {"_id": 0, "item_id": 1}).to_list(100)
        cart_item_ids = {item['item_id'] for item in cart_items}
        
        response = ListeEpicerieResponse(
            user_id=user_id,
            gibier=gibier
        )
        
        all_items = []
        total_price = 0.0
        total_essential = 0
        items_in_cart = 0
        by_category = {}
        
        # Filtrer les catégories si spécifié
        categories_to_include = include_categories or list(CATALOGUE.keys())
        
        for category, items in CATALOGUE.items():
            if category not in categories_to_include:
                continue
            
            by_category[category] = 0
            
            for item in items:
                item_copy = item.copy()
                item_copy['category'] = category
                item_copy['cta_label'] = "Acheter / Commander"
                item_copy['cta_label_en'] = "Buy / Order"
                item_copy['is_in_cart'] = item['id'] in cart_item_ids
                
                all_items.append(item_copy)
                by_category[category] += 1
                
                if item.get('is_essential'):
                    total_essential += 1
                
                if item_copy['is_in_cart']:
                    items_in_cart += 1
                
                total_price += item.get('price', 0)
        
        response.items = all_items
        response.total_items = len(all_items)
        response.total_essential = total_essential
        response.total_price = round(total_price, 2)
        response.items_in_cart = items_in_cart
        response.by_category = by_category
        
        return response
    
    async def add_to_cart(
        self,
        user_id: str,
        item_id: str,
        quantity: int = 1
    ) -> Dict[str, Any]:
        """
        Ajoute un item au panier.
        Redirige vers le niveau d'abonnement si nécessaire.
        """
        db = await self._get_db()
        
        # Trouver l'item
        item = None
        item_category = None
        for category, items in CATALOGUE.items():
            for i in items:
                if i['id'] == item_id:
                    item = i
                    item_category = category
                    break
            if item:
                break
        
        if not item:
            return {"success": False, "error": "Item non trouvé"}
        
        # Vérifier si déjà dans le panier
        existing = await db.cart_items.find_one({"user_id": user_id, "item_id": item_id})
        
        if existing:
            # Mettre à jour la quantité
            await db.cart_items.update_one(
                {"user_id": user_id, "item_id": item_id},
                {"$inc": {"quantity": quantity}}
            )
            action = "updated"
        else:
            # Ajouter au panier
            cart_item = {
                "user_id": user_id,
                "item_id": item_id,
                "item_type": item_category,
                "name": item.get('name'),
                "name_en": item.get('name_en'),
                "price": item.get('price', 0),
                "quantity": quantity,
                "subscription_required": item.get('subscription_required'),
                "added_at": datetime.now(timezone.utc).isoformat()
            }
            await db.cart_items.insert_one(cart_item)
            action = "added"
        
        return {
            "success": True,
            "item_id": item_id,
            "cart_action": action,
            "item_name": item.get('name'),
            "price": item.get('price', 0),
            "quantity": quantity,
            "redirect_to_pricing": item.get('subscription_required') is not None,
            "subscription_required": item.get('subscription_required')
        }
    
    async def remove_from_cart(self, user_id: str, item_id: str) -> Dict[str, Any]:
        """Retire un item du panier"""
        db = await self._get_db()
        
        result = await db.cart_items.delete_one({"user_id": user_id, "item_id": item_id})
        
        return {
            "success": result.deleted_count > 0,
            "item_id": item_id,
            "cart_action": "removed"
        }
    
    async def get_cart(self, user_id: str) -> List[Dict[str, Any]]:
        """Récupère le panier complet"""
        db = await self._get_db()
        
        cursor = db.cart_items.find({"user_id": user_id}, {"_id": 0})
        items = await cursor.to_list(100)
        
        total = sum(item.get('price', 0) * item.get('quantity', 1) for item in items)
        
        return {
            "items": items,
            "total_items": len(items),
            "total_price": round(total, 2)
        }
    
    def get_catalogue(self) -> Dict[str, List[Dict[str, Any]]]:
        """Retourne le catalogue complet"""
        return CATALOGUE


# Instance globale
liste_epicerie_service = ListeEpicerieService()
