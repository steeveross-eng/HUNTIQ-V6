"""
BIONIC Pourvoirie Finder Engine
═══════════════════════════════════════════════════════════════════════════════
Recommandation de pourvoiries selon:
- Gibier
- Région
- GPS
- Budget
═══════════════════════════════════════════════════════════════════════════════
Version: 1.0.0
Date: 2026-02-19
"""

import os
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from motor.motor_asyncio import AsyncIOMotorClient
import math


@dataclass
class Pourvoirie:
    """Données d'une pourvoirie"""
    id: str
    name: str
    region: str
    
    # Gibiers disponibles
    gibiers: List[str] = field(default_factory=list)
    
    # Localisation
    gps_lat: float = 0.0
    gps_lng: float = 0.0
    distance_km: Optional[float] = None
    
    # Prix et services
    price_range_min: float = 0.0
    price_range_max: float = 0.0
    deposit_amount: float = 0.0
    services: List[str] = field(default_factory=list)
    
    # Évaluation
    rating: float = 0.0
    reviews_count: int = 0
    bionic_score: int = 0
    
    # Contact
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    
    # E-commerce
    is_bookable: bool = True
    booking_url: Optional[str] = None


@dataclass
class PourvouirieSearchResponse:
    """Réponse de recherche de pourvoiries"""
    user_id: str
    gibier: str
    region: Optional[str] = None
    budget_max: Optional[float] = None
    
    pourvoiries: List[Dict[str, Any]] = field(default_factory=list)
    total_found: int = 0
    
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ═══════════════════════════════════════════════════════════════════════════════
# DONNÉES SIMULÉES - POURVOIRIES
# ═══════════════════════════════════════════════════════════════════════════════

MOCK_POURVOIRIES = [
    {
        "id": "pv_001",
        "name": "Pourvoirie du Lac Blanc",
        "region": "Laurentides",
        "gibiers": ["orignal", "chevreuil", "ours"],
        "gps_lat": 46.8532,
        "gps_lng": -74.3241,
        "price_range_min": 1200,
        "price_range_max": 2500,
        "deposit_amount": 500,
        "services": ["hébergement", "guide", "transport", "éviscération"],
        "rating": 4.8,
        "reviews_count": 127,
        "bionic_score": 92,
        "phone": "819-555-0101",
        "website": "https://www.pourvourielacblanc.ca",
        "is_bookable": True
    },
    {
        "id": "pv_002",
        "name": "Domaine de la Forêt Noire",
        "region": "Mauricie",
        "gibiers": ["orignal", "ours"],
        "gps_lat": 47.1234,
        "gps_lng": -72.8765,
        "price_range_min": 1500,
        "price_range_max": 3000,
        "deposit_amount": 750,
        "services": ["hébergement luxe", "guide expert", "transport", "éviscération", "congélation"],
        "rating": 4.9,
        "reviews_count": 89,
        "bionic_score": 95,
        "phone": "819-555-0202",
        "website": "https://www.foretnoire.ca",
        "is_bookable": True
    },
    {
        "id": "pv_003",
        "name": "Camp des Érables",
        "region": "Lanaudière",
        "gibiers": ["chevreuil", "dindon", "perdrix"],
        "gps_lat": 46.4321,
        "gps_lng": -73.5678,
        "price_range_min": 600,
        "price_range_max": 1200,
        "deposit_amount": 200,
        "services": ["hébergement", "guide"],
        "rating": 4.5,
        "reviews_count": 203,
        "bionic_score": 85,
        "phone": "450-555-0303",
        "website": "https://www.campdeserables.com",
        "is_bookable": True
    },
    {
        "id": "pv_004",
        "name": "Pourvoirie Anticosti",
        "region": "Côte-Nord",
        "gibiers": ["chevreuil"],
        "gps_lat": 49.4321,
        "gps_lng": -63.0123,
        "price_range_min": 2500,
        "price_range_max": 5000,
        "deposit_amount": 1000,
        "services": ["tout inclus", "transport aérien", "guide", "hébergement luxe"],
        "rating": 4.95,
        "reviews_count": 312,
        "bionic_score": 98,
        "phone": "418-555-0404",
        "website": "https://www.anticostipourvoirie.ca",
        "is_bookable": True
    },
    {
        "id": "pv_005",
        "name": "Seigneurie du Triton",
        "region": "Mauricie",
        "gibiers": ["orignal", "ours", "chevreuil"],
        "gps_lat": 47.3456,
        "gps_lng": -72.1234,
        "price_range_min": 1800,
        "price_range_max": 3500,
        "deposit_amount": 600,
        "services": ["hébergement", "guide", "canot", "éviscération"],
        "rating": 4.7,
        "reviews_count": 156,
        "bionic_score": 90,
        "phone": "819-555-0505",
        "is_bookable": True
    },
    {
        "id": "pv_006",
        "name": "Camp du Dindon Sauvage",
        "region": "Estrie",
        "gibiers": ["dindon"],
        "gps_lat": 45.4567,
        "gps_lng": -71.8901,
        "price_range_min": 400,
        "price_range_max": 800,
        "deposit_amount": 150,
        "services": ["guide spécialisé dindon", "hébergement"],
        "rating": 4.6,
        "reviews_count": 78,
        "bionic_score": 88,
        "phone": "819-555-0606",
        "is_bookable": True
    },
]


class PourvoirieFinderService:
    """Service de recherche de pourvoiries"""
    
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
    
    def _calculate_distance(
        self, 
        lat1: float, lng1: float, 
        lat2: float, lng2: float
    ) -> float:
        """Calcule la distance en km entre deux points GPS (formule de Haversine)"""
        R = 6371  # Rayon de la Terre en km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    async def search_pourvoiries(
        self,
        user_id: str,
        gibier: str,
        region: Optional[str] = None,
        gps_lat: Optional[float] = None,
        gps_lng: Optional[float] = None,
        budget_max: Optional[float] = None,
        limit: int = 10
    ) -> PourvouirieSearchResponse:
        """
        Recherche les meilleures pourvoiries selon les critères.
        """
        db = await self._get_db()
        
        # Filtrer les pourvoiries
        results = []
        
        for pv in MOCK_POURVOIRIES:
            # Filtre gibier
            if gibier not in pv['gibiers']:
                continue
            
            # Filtre région
            if region and pv['region'].lower() != region.lower():
                continue
            
            # Filtre budget
            if budget_max and pv['price_range_min'] > budget_max:
                continue
            
            pv_copy = pv.copy()
            
            # Calcul distance si GPS fourni
            if gps_lat and gps_lng:
                distance = self._calculate_distance(
                    gps_lat, gps_lng,
                    pv['gps_lat'], pv['gps_lng']
                )
                pv_copy['distance_km'] = round(distance, 1)
            
            # Ajouter les infos d'achat
            pv_copy['is_purchasable'] = True
            pv_copy['cta_label'] = "Réserver / Commander"
            pv_copy['cta_label_en'] = "Book / Order"
            
            results.append(pv_copy)
        
        # Trier par score BIONIC puis par distance
        if gps_lat and gps_lng:
            results.sort(key=lambda x: (-(x.get('bionic_score', 0)), x.get('distance_km', 9999)))
        else:
            results.sort(key=lambda x: -x.get('bionic_score', 0))
        
        # Limiter les résultats
        results = results[:limit]
        
        # Sauvegarder la recherche
        await db.pourvoirie_searches.insert_one({
            "user_id": user_id,
            "gibier": gibier,
            "region": region,
            "gps_lat": gps_lat,
            "gps_lng": gps_lng,
            "budget_max": budget_max,
            "results_count": len(results),
            "searched_at": datetime.now(timezone.utc).isoformat()
        })
        
        return PourvouirieSearchResponse(
            user_id=user_id,
            gibier=gibier,
            region=region,
            budget_max=budget_max,
            pourvoiries=results,
            total_found=len(results)
        )
    
    async def book_pourvoirie(
        self,
        user_id: str,
        pourvoirie_id: str,
        dates: Dict[str, str],
        guests: int = 1
    ) -> Dict[str, Any]:
        """
        Ajoute une réservation/dépôt au panier.
        """
        db = await self._get_db()
        
        # Trouver la pourvoirie
        pourvoirie = next((p for p in MOCK_POURVOIRIES if p['id'] == pourvoirie_id), None)
        
        if not pourvoirie:
            return {"success": False, "error": "Pourvoirie non trouvée"}
        
        # Créer l'item panier
        cart_item = {
            "user_id": user_id,
            "item_id": pourvoirie_id,
            "item_type": "pourvoirie_booking",
            "name": f"Réservation - {pourvoirie['name']}",
            "price": pourvoirie['deposit_amount'],
            "quantity": guests,
            "dates": dates,
            "pourvoirie_details": {
                "name": pourvoirie['name'],
                "region": pourvoirie['region'],
                "deposit": pourvoirie['deposit_amount']
            },
            "added_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.cart_items.insert_one(cart_item)
        
        return {
            "success": True,
            "item_added": pourvoirie_id,
            "cart_action": "add",
            "deposit_amount": pourvoirie['deposit_amount'],
            "total_for_guests": pourvoirie['deposit_amount'] * guests
        }
    
    async def get_pourvoirie_details(self, pourvoirie_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les détails d'une pourvoirie"""
        pourvoirie = next((p for p in MOCK_POURVOIRIES if p['id'] == pourvoirie_id), None)
        
        if pourvoirie:
            return {
                **pourvoirie,
                "is_purchasable": True,
                "cta_label": "Réserver / Commander",
                "cta_label_en": "Book / Order"
            }
        return None


# Instance globale
pourvoirie_finder_service = PourvoirieFinderService()
