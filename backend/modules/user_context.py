"""
BIONIC User Context Engine
═══════════════════════════════════════════════════════════════════════════════
Module de détection automatique du contexte utilisateur:
- Gibier principal
- Région / GPS du territoire
- Historique de navigation
- Outils utilisés
- Pourvoiries consultées
- Setups consultés
- Type de permis consulté
- Mode Saison (dates, quotas)
═══════════════════════════════════════════════════════════════════════════════
Version: 1.1.0
Date: 2026-02-19
Changelog:
- v1.1.0: Added __post_init__ validation to prevent TypeError on corrupted data
"""

import os
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field, asdict
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

# Logger for type correction logging
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# MODÈLES DE DONNÉES
# ═══════════════════════════════════════════════════════════════════════════════

class UserContextInput(BaseModel):
    """Input pour mise à jour du contexte utilisateur"""
    user_id: str
    gibier: Optional[str] = None
    region: Optional[str] = None
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None
    page_visited: Optional[str] = None
    tool_used: Optional[str] = None
    pourvoirie_id: Optional[str] = None
    setup_id: Optional[str] = None
    permis_type: Optional[str] = None


@dataclass
class UserContext:
    """Contexte utilisateur complet"""
    user_id: str
    
    # Gibier et territoire
    gibier_principal: Optional[str] = None
    gibiers_secondaires: List[str] = field(default_factory=list)
    region: Optional[str] = None
    province: Optional[str] = None
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None
    
    # Historique
    pages_visited: List[str] = field(default_factory=list)
    tools_used: List[str] = field(default_factory=list)
    pourvoiries_consulted: List[str] = field(default_factory=list)
    setups_consulted: List[str] = field(default_factory=list)
    permis_consulted: List[str] = field(default_factory=list)
    
    # Saison
    current_season: Optional[str] = None
    season_dates: Dict[str, Any] = field(default_factory=dict)
    quotas: Dict[str, int] = field(default_factory=dict)
    
    # Métadonnées
    last_activity: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    # Flags
    needs_gibier_popup: bool = True
    has_complete_profile: bool = False
    
    def __post_init__(self):
        """
        Runtime validation to prevent TypeError on corrupted MongoDB data.
        Ensures all list fields are actually lists, not integers or other types.
        """
        # Validate and correct list fields
        list_fields = [
            'gibiers_secondaires', 'pages_visited', 'tools_used',
            'pourvoiries_consulted', 'setups_consulted', 'permis_consulted'
        ]
        
        for field_name in list_fields:
            value = getattr(self, field_name)
            if not isinstance(value, list):
                logger.warning(
                    f"BIONIC TypeError Prevention: UserContext.{field_name} has type "
                    f"{type(value).__name__}, expected list. Resetting to empty list. "
                    f"user_id={self.user_id}"
                )
                setattr(self, field_name, [])
        
        # Validate and correct dict fields
        dict_fields = ['season_dates', 'quotas']
        
        for field_name in dict_fields:
            value = getattr(self, field_name)
            if not isinstance(value, dict):
                logger.warning(
                    f"BIONIC TypeError Prevention: UserContext.{field_name} has type "
                    f"{type(value).__name__}, expected dict. Resetting to empty dict. "
                    f"user_id={self.user_id}"
                )
                setattr(self, field_name, {})


# ═══════════════════════════════════════════════════════════════════════════════
# DONNÉES DE RÉFÉRENCE - SAISONS DE CHASSE QUÉBEC
# ═══════════════════════════════════════════════════════════════════════════════

GIBIERS_AVAILABLE = [
    {"id": "orignal", "name": "Orignal", "name_en": "Moose", "icon": "🦌"},
    {"id": "chevreuil", "name": "Cerf de Virginie", "name_en": "White-tailed Deer", "icon": "🦌"},
    {"id": "ours", "name": "Ours noir", "name_en": "Black Bear", "icon": "🐻"},
    {"id": "dindon", "name": "Dindon sauvage", "name_en": "Wild Turkey", "icon": "🦃"},
    {"id": "perdrix", "name": "Gélinotte huppée", "name_en": "Ruffed Grouse", "icon": "🐦"},
    {"id": "canard", "name": "Sauvagine", "name_en": "Waterfowl", "icon": "🦆"},
    {"id": "oie", "name": "Oie des neiges", "name_en": "Snow Goose", "icon": "🪿"},
    {"id": "lievre", "name": "Lièvre d'Amérique", "name_en": "Snowshoe Hare", "icon": "🐰"},
    {"id": "coyote", "name": "Coyote", "name_en": "Coyote", "icon": "🐺"},
    {"id": "renard", "name": "Renard roux", "name_en": "Red Fox", "icon": "🦊"},
]

# Saisons de chasse approximatives (Québec)
SEASONS_QUEBEC = {
    "orignal": {
        "arc": {"start": "2026-09-14", "end": "2026-09-27"},
        "arbalete": {"start": "2026-10-05", "end": "2026-10-11"},
        "arme_feu": {"start": "2026-10-19", "end": "2026-10-25"},
    },
    "chevreuil": {
        "arc": {"start": "2026-09-28", "end": "2026-10-18"},
        "arbalete": {"start": "2026-10-19", "end": "2026-11-01"},
        "arme_feu": {"start": "2026-11-07", "end": "2026-11-20"},
    },
    "ours": {
        "printemps": {"start": "2026-05-15", "end": "2026-06-30"},
        "automne": {"start": "2026-08-25", "end": "2026-11-15"},
    },
    "dindon": {
        "printemps": {"start": "2026-04-25", "end": "2026-05-31"},
        "automne": {"start": "2026-10-01", "end": "2026-10-31"},
    },
    "canard": {
        "automne": {"start": "2026-09-21", "end": "2026-12-26"},
    },
}

REGIONS_QUEBEC = [
    {"id": "01", "name": "Bas-Saint-Laurent"},
    {"id": "02", "name": "Saguenay–Lac-Saint-Jean"},
    {"id": "03", "name": "Capitale-Nationale"},
    {"id": "04", "name": "Mauricie"},
    {"id": "05", "name": "Estrie"},
    {"id": "06", "name": "Montréal"},
    {"id": "07", "name": "Outaouais"},
    {"id": "08", "name": "Abitibi-Témiscamingue"},
    {"id": "09", "name": "Côte-Nord"},
    {"id": "10", "name": "Nord-du-Québec"},
    {"id": "11", "name": "Gaspésie–Îles-de-la-Madeleine"},
    {"id": "12", "name": "Chaudière-Appalaches"},
    {"id": "13", "name": "Laval"},
    {"id": "14", "name": "Lanaudière"},
    {"id": "15", "name": "Laurentides"},
    {"id": "16", "name": "Montérégie"},
    {"id": "17", "name": "Centre-du-Québec"},
]


# ═══════════════════════════════════════════════════════════════════════════════
# SERVICE PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

class UserContextService:
    """Service de gestion du contexte utilisateur"""
    
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
    
    async def get_context(self, user_id: str) -> UserContext:
        """
        Récupère le contexte utilisateur.
        Crée un nouveau contexte si inexistant.
        """
        db = await self._get_db()
        
        doc = await db.user_contexts.find_one({"user_id": user_id}, {"_id": 0})
        
        if doc:
            return UserContext(**doc)
        
        # Nouveau contexte
        context = UserContext(
            user_id=user_id,
            needs_gibier_popup=True,
            created_at=datetime.now(timezone.utc).isoformat(),
            updated_at=datetime.now(timezone.utc).isoformat()
        )
        
        # Déterminer la saison actuelle
        context.current_season = self._determine_current_season()
        
        await db.user_contexts.insert_one(asdict(context))
        
        return context
    
    async def update_context(self, input_data: UserContextInput) -> UserContext:
        """Met à jour le contexte utilisateur avec de nouvelles informations"""
        db = await self._get_db()
        
        context = await self.get_context(input_data.user_id)
        
        # Mise à jour gibier
        if input_data.gibier:
            if not context.gibier_principal:
                context.gibier_principal = input_data.gibier
                context.needs_gibier_popup = False
            elif input_data.gibier not in context.gibiers_secondaires:
                context.gibiers_secondaires.append(input_data.gibier)
        
        # Mise à jour région/GPS
        if input_data.region:
            context.region = input_data.region
        if input_data.gps_lat and input_data.gps_lng:
            context.gps_lat = input_data.gps_lat
            context.gps_lng = input_data.gps_lng
        
        # Historique pages
        if input_data.page_visited:
            if input_data.page_visited not in context.pages_visited:
                context.pages_visited.append(input_data.page_visited)
                # Garder les 50 dernières
                context.pages_visited = context.pages_visited[-50:]
        
        # Historique outils
        if input_data.tool_used:
            if input_data.tool_used not in context.tools_used:
                context.tools_used.append(input_data.tool_used)
        
        # Pourvoiries
        if input_data.pourvoirie_id:
            if input_data.pourvoirie_id not in context.pourvoiries_consulted:
                context.pourvoiries_consulted.append(input_data.pourvoirie_id)
        
        # Setups
        if input_data.setup_id:
            if input_data.setup_id not in context.setups_consulted:
                context.setups_consulted.append(input_data.setup_id)
        
        # Permis
        if input_data.permis_type:
            if input_data.permis_type not in context.permis_consulted:
                context.permis_consulted.append(input_data.permis_type)
        
        # Vérifier si profil complet
        context.has_complete_profile = self._check_profile_complete(context)
        
        # Métadonnées
        context.last_activity = datetime.now(timezone.utc).isoformat()
        context.updated_at = datetime.now(timezone.utc).isoformat()
        context.current_season = self._determine_current_season()
        
        # Sauvegarder
        await db.user_contexts.update_one(
            {"user_id": context.user_id},
            {"$set": asdict(context)},
            upsert=True
        )
        
        return context
    
    async def set_gibier_principal(self, user_id: str, gibier: str) -> UserContext:
        """Définit le gibier principal (après popup)"""
        db = await self._get_db()
        
        context = await self.get_context(user_id)
        context.gibier_principal = gibier
        context.needs_gibier_popup = False
        context.updated_at = datetime.now(timezone.utc).isoformat()
        
        # Charger les dates de saison pour ce gibier
        if gibier in SEASONS_QUEBEC:
            context.season_dates = SEASONS_QUEBEC[gibier]
        
        await db.user_contexts.update_one(
            {"user_id": user_id},
            {"$set": asdict(context)},
            upsert=True
        )
        
        return context
    
    def _determine_current_season(self) -> str:
        """Détermine la saison actuelle"""
        month = datetime.now().month
        
        if month in [3, 4, 5]:
            return "printemps"
        elif month in [6, 7, 8]:
            return "ete"
        elif month in [9, 10, 11]:
            return "automne"
        else:
            return "hiver"
    
    def _check_profile_complete(self, context: UserContext) -> bool:
        """
        Vérifie si le profil est suffisamment complet.
        
        Note: The __post_init__ validation in UserContext ensures pages_visited
        and tools_used are always lists, so len() is now safe to call.
        """
        score = 0
        
        if context.gibier_principal:
            score += 30
        if context.region or (context.gps_lat and context.gps_lng):
            score += 30
        
        # Safe len() calls - validated in __post_init__
        # Additional isinstance check for extra safety
        pages_count = len(context.pages_visited) if isinstance(context.pages_visited, list) else 0
        tools_count = len(context.tools_used) if isinstance(context.tools_used, list) else 0
        
        if pages_count >= 5:
            score += 20
        if tools_count >= 2:
            score += 20
        
        return score >= 60
    
    def get_gibiers_available(self) -> List[Dict[str, Any]]:
        """Retourne la liste des gibiers disponibles"""
        return GIBIERS_AVAILABLE
    
    def get_regions_quebec(self) -> List[Dict[str, Any]]:
        """Retourne la liste des régions du Québec"""
        return REGIONS_QUEBEC
    
    def get_season_dates(self, gibier: str) -> Dict[str, Any]:
        """Retourne les dates de saison pour un gibier"""
        return SEASONS_QUEBEC.get(gibier, {})


# Instance globale
user_context_service = UserContextService()
