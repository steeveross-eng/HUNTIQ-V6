"""
BIONIC Plan de Saison Engine
═══════════════════════════════════════════════════════════════════════════════
Génération de plan de saison personnalisé:
- Basé sur gibier, région, GPS, dates, météo, pression
- Actions mensuelles
- Produits clés et gear recommandé
- Bouton Acheter/Commander pour chaque item
═══════════════════════════════════════════════════════════════════════════════
Version: 1.0.0
Date: 2026-02-19
"""

import os
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field, asdict
from motor.motor_asyncio import AsyncIOMotorClient
from calendar import monthrange


@dataclass
class MonthlyAction:
    """Action mensuelle du plan"""
    month: int
    month_name: str
    month_name_en: str
    
    # Actions
    actions: List[str] = field(default_factory=list)
    actions_en: List[str] = field(default_factory=list)
    
    # État de la saison
    season_phase: str = ""  # pre_season, early_season, peak_season, late_season, off_season
    
    # Recommandations
    recommended_products: List[Dict[str, Any]] = field(default_factory=list)
    recommended_gear: List[Dict[str, Any]] = field(default_factory=list)
    
    # Priorité
    priority: str = "normal"  # low, normal, high, critical


@dataclass
class PlanSaisonResponse:
    """Réponse du plan de saison"""
    user_id: str
    gibier: str
    year: int
    
    # Plan mensuel
    monthly_plan: List[Dict[str, Any]] = field(default_factory=list)
    
    # Dates clés
    key_dates: List[Dict[str, Any]] = field(default_factory=list)
    
    # Résumé
    total_hunting_days: int = 0
    peak_periods: List[str] = field(default_factory=list)
    
    # Métadonnées
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ═══════════════════════════════════════════════════════════════════════════════
# TEMPLATES DE PLANS PAR GIBIER
# ═══════════════════════════════════════════════════════════════════════════════

MONTH_NAMES_FR = ["", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin", 
                   "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
MONTH_NAMES_EN = ["", "January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]

PLANS_BY_GIBIER = {
    "orignal": {
        1: {"phase": "off_season", "priority": "low", 
            "actions": ["Planification de la saison", "Réservation pourvoirie"],
            "actions_en": ["Season planning", "Outfitter booking"],
            "products": [{"id": "serv_plan", "name": "Plan de saison BIONIC", "price": 49.99}]},
        2: {"phase": "off_season", "priority": "low",
            "actions": ["Vérification équipement", "Achat munitions"],
            "actions_en": ["Equipment check", "Ammunition purchase"],
            "gear": [{"id": "gear_mun", "name": "Munitions", "price": 89.99}]},
        3: {"phase": "off_season", "priority": "low",
            "actions": ["Renouvellement permis", "Formation call"],
            "actions_en": ["License renewal", "Call training"],
            "products": [{"id": "form_call", "name": "Formation Call Orignal", "price": 149.99}]},
        4: {"phase": "pre_season", "priority": "normal",
            "actions": ["Repérage territoire", "Installation caméras de trail"],
            "actions_en": ["Territory scouting", "Trail camera setup"],
            "gear": [{"id": "gear_cam", "name": "Caméra de trail", "price": 199.99}]},
        5: {"phase": "pre_season", "priority": "normal",
            "actions": ["Analyse données caméras", "Identification zones de passage"],
            "actions_en": ["Camera data analysis", "Travel route identification"],
            "products": [{"id": "hot_pack", "name": "Pack Hotspots", "price": 44.97}]},
        6: {"phase": "pre_season", "priority": "normal",
            "actions": ["Préparation affûts", "Test équipement"],
            "actions_en": ["Stand preparation", "Equipment testing"],
            "gear": [{"id": "gear_stand", "name": "Mirador portable", "price": 249.99}]},
        7: {"phase": "pre_season", "priority": "high",
            "actions": ["Installation saline", "Repérage final"],
            "actions_en": ["Salt lick installation", "Final scouting"],
            "products": [{"id": "attr_sel", "name": "Bloc de sel minéral", "price": 14.99}]},
        8: {"phase": "pre_season", "priority": "high",
            "actions": ["Pratique du call", "Vérification zones"],
            "actions_en": ["Call practice", "Zone verification"],
            "gear": [{"id": "call_pro", "name": "Call professionnel", "price": 79.99}]},
        9: {"phase": "early_season", "priority": "critical",
            "actions": ["CHASSE À L'ARC - Période de rut précoce", "Utilisation call de vache"],
            "actions_en": ["BOW HUNTING - Early rut period", "Cow call usage"],
            "products": [{"id": "attr_urine", "name": "Urine de vache", "price": 24.99}]},
        10: {"phase": "peak_season", "priority": "critical",
            "actions": ["CHASSE ARBALÈTE/ARME À FEU - Pic du rut", "Call intensif"],
            "actions_en": ["CROSSBOW/FIREARM HUNTING - Peak rut", "Intensive calling"],
            "products": [{"id": "attr_bull", "name": "Urine de taureau", "price": 24.99}]},
        11: {"phase": "late_season", "priority": "high",
            "actions": ["Fin de saison - Dernières opportunités", "Bilan de la saison"],
            "actions_en": ["End of season - Last opportunities", "Season review"],
            "products": []},
        12: {"phase": "off_season", "priority": "low",
            "actions": ["Analyse des résultats", "Planification prochaine saison"],
            "actions_en": ["Results analysis", "Next season planning"],
            "products": [{"id": "serv_analyse", "name": "Analyse personnalisée", "price": 149.99}]},
    },
    "chevreuil": {
        9: {"phase": "pre_season", "priority": "high",
            "actions": ["Repérage lignes de déplacement", "Installation affûts"],
            "actions_en": ["Travel route scouting", "Stand installation"]},
        10: {"phase": "early_season", "priority": "critical",
            "actions": ["CHASSE À L'ARC - Pré-rut", "Utilisation attractants"],
            "actions_en": ["BOW HUNTING - Pre-rut", "Attractant usage"]},
        11: {"phase": "peak_season", "priority": "critical",
            "actions": ["CHASSE ARME À FEU - Pic du rut", "Rattling et grunt"],
            "actions_en": ["FIREARM HUNTING - Peak rut", "Rattling and grunting"]},
        12: {"phase": "late_season", "priority": "high",
            "actions": ["Fin de saison - Sources de nourriture", "Patterns tardifs"],
            "actions_en": ["End of season - Food sources", "Late patterns"]},
    },
    "dindon": {
        3: {"phase": "pre_season", "priority": "high",
            "actions": ["Repérage dortoirs", "Pratique du call"],
            "actions_en": ["Roost scouting", "Call practice"]},
        4: {"phase": "early_season", "priority": "critical",
            "actions": ["CHASSE PRINTANIÈRE - Début saison", "Localisation gobblers"],
            "actions_en": ["SPRING HUNTING - Season start", "Gobbler location"]},
        5: {"phase": "peak_season", "priority": "critical",
            "actions": ["PIC DE L'ACTIVITÉ - Call agressif", "Positionnement stratégique"],
            "actions_en": ["PEAK ACTIVITY - Aggressive calling", "Strategic positioning"]},
        10: {"phase": "early_season", "priority": "high",
            "actions": ["CHASSE AUTOMNALE - Regroupement", "Patterns différents"],
            "actions_en": ["FALL HUNTING - Flocking", "Different patterns"]},
    },
}


class PlanSaisonService:
    """Service de génération de plan de saison"""
    
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
    
    async def generate_plan(
        self,
        user_id: str,
        gibier: str,
        year: Optional[int] = None
    ) -> PlanSaisonResponse:
        """
        Génère un plan de saison personnalisé.
        """
        db = await self._get_db()
        
        if not year:
            year = datetime.now().year
        
        response = PlanSaisonResponse(
            user_id=user_id,
            gibier=gibier,
            year=year
        )
        
        # Récupérer le template pour ce gibier
        template = PLANS_BY_GIBIER.get(gibier, PLANS_BY_GIBIER['orignal'])
        
        monthly_plan = []
        key_dates = []
        hunting_days = 0
        peak_periods = []
        
        for month in range(1, 13):
            month_data = template.get(month, {
                "phase": "off_season",
                "priority": "low",
                "actions": ["Aucune action spécifique"],
                "actions_en": ["No specific action"]
            })
            
            # Construire les produits et gear avec boutons d'achat
            products = []
            for p in month_data.get('products', []):
                products.append({
                    **p,
                    "is_purchasable": True,
                    "cta_label": "Acheter / Commander",
                    "cta_label_en": "Buy / Order"
                })
            
            gear = []
            for g in month_data.get('gear', []):
                gear.append({
                    **g,
                    "is_purchasable": True,
                    "cta_label": "Acheter / Commander",
                    "cta_label_en": "Buy / Order"
                })
            
            monthly_action = {
                "month": month,
                "month_name": MONTH_NAMES_FR[month],
                "month_name_en": MONTH_NAMES_EN[month],
                "season_phase": month_data.get('phase', 'off_season'),
                "priority": month_data.get('priority', 'normal'),
                "actions": month_data.get('actions', []),
                "actions_en": month_data.get('actions_en', []),
                "recommended_products": products,
                "recommended_gear": gear
            }
            
            monthly_plan.append(monthly_action)
            
            # Compter les jours de chasse et périodes
            if month_data.get('phase') in ['early_season', 'peak_season', 'late_season']:
                days_in_month = monthrange(year, month)[1]
                if month_data.get('phase') == 'peak_season':
                    hunting_days += days_in_month
                    peak_periods.append(MONTH_NAMES_FR[month])
                else:
                    hunting_days += days_in_month // 2
            
            # Dates clés
            if month_data.get('priority') == 'critical':
                key_dates.append({
                    "month": month,
                    "month_name": MONTH_NAMES_FR[month],
                    "description": month_data.get('actions', [''])[0],
                    "importance": "critical"
                })
        
        response.monthly_plan = monthly_plan
        response.key_dates = key_dates
        response.total_hunting_days = hunting_days
        response.peak_periods = peak_periods
        
        # Sauvegarder le plan
        await db.season_plans.update_one(
            {"user_id": user_id, "gibier": gibier, "year": year},
            {"$set": {
                "user_id": user_id,
                "gibier": gibier,
                "year": year,
                "plan": asdict(response),
                "generated_at": datetime.now(timezone.utc).isoformat()
            }},
            upsert=True
        )
        
        return response
    
    async def add_plan_item_to_cart(
        self,
        user_id: str,
        item_id: str,
        item_type: str
    ) -> Dict[str, Any]:
        """Ajoute un item du plan au panier"""
        db = await self._get_db()
        
        # Chercher l'item dans les templates
        item = None
        for gibier_plan in PLANS_BY_GIBIER.values():
            for month_data in gibier_plan.values():
                for p in month_data.get('products', []) + month_data.get('gear', []):
                    if p.get('id') == item_id:
                        item = p
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
            "source": "plan_saison",
            "added_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.cart_items.insert_one(cart_item)
        
        return {
            "success": True,
            "item_id": item_id,
            "cart_action": "added"
        }


# Instance globale
plan_saison_service = PlanSaisonService()
