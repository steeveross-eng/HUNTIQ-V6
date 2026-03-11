"""
BIONIC Permis Checklist Engine
═══════════════════════════════════════════════════════════════════════════════
Module de gestion des checklists permis et rappels annuels:
- Génération automatique de checklist après consultation permis
- Rappel annuel expiration
- Nouveautés réglementaires
- Dates de la prochaine saison
═══════════════════════════════════════════════════════════════════════════════
Version: 1.0.0
Date: 2026-02-19
"""

import os
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field, asdict
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel


class PermisChecklistItem(BaseModel):
    """Item de la checklist permis"""
    id: str
    label: str
    label_en: str
    is_completed: bool = False
    is_required: bool = True
    category: str = "general"
    url: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class PermisChecklist:
    """Checklist complète pour un permis"""
    user_id: str
    permis_type: str
    province: str
    
    # État
    items: List[Dict[str, Any]] = field(default_factory=list)
    completion_percentage: int = 0
    
    # Dates importantes
    purchase_date: Optional[str] = None
    expiration_date: Optional[str] = None
    next_season_start: Optional[str] = None
    
    # Rappels
    reminder_enabled: bool = True
    reminder_days_before: int = 30
    last_reminder_sent: Optional[str] = None
    
    # Métadonnées
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# Items de base pour une checklist permis
BASE_CHECKLIST_ITEMS = [
    {
        "id": "permis_achete",
        "label": "Permis acheté",
        "label_en": "License purchased",
        "category": "permis",
        "is_required": True
    },
    {
        "id": "certificat_chasseur",
        "label": "Certificat du chasseur valide",
        "label_en": "Valid hunter certificate",
        "category": "permis",
        "is_required": True
    },
    {
        "id": "transport_arme",
        "label": "Permis de possession et d'acquisition (PPA)",
        "label_en": "Possession and Acquisition License (PAL)",
        "category": "permis",
        "is_required": True
    },
    {
        "id": "dates_saison",
        "label": "Dates de saison vérifiées",
        "label_en": "Season dates verified",
        "category": "planification",
        "is_required": True
    },
    {
        "id": "zone_chasse",
        "label": "Zone de chasse confirmée",
        "label_en": "Hunting zone confirmed",
        "category": "planification",
        "is_required": True
    },
    {
        "id": "quotas_verifies",
        "label": "Quotas vérifiés",
        "label_en": "Quotas verified",
        "category": "planification",
        "is_required": True
    },
    {
        "id": "reglements_lus",
        "label": "Règlements de chasse lus",
        "label_en": "Hunting regulations read",
        "category": "reglementation",
        "is_required": True
    },
    {
        "id": "equipement_legal",
        "label": "Équipement conforme à la réglementation",
        "label_en": "Equipment compliant with regulations",
        "category": "equipement",
        "is_required": True
    },
    {
        "id": "vetements_visibilite",
        "label": "Vêtements de visibilité (si requis)",
        "label_en": "High visibility clothing (if required)",
        "category": "equipement",
        "is_required": False
    },
    {
        "id": "territoire_prepare",
        "label": "Territoire analysé avec BIONIC",
        "label_en": "Territory analyzed with BIONIC",
        "category": "preparation",
        "is_required": False,
        "url": "/territoire"
    },
    {
        "id": "hotspots_identifies",
        "label": "Hotspots identifiés",
        "label_en": "Hotspots identified",
        "category": "preparation",
        "is_required": False,
        "url": "/map"
    },
    {
        "id": "meteo_consultee",
        "label": "Prévisions météo consultées",
        "label_en": "Weather forecast checked",
        "category": "preparation",
        "is_required": False,
        "url": "/forecast"
    },
]


class PermisChecklistService:
    """Service de gestion des checklists permis"""
    
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
    
    async def create_checklist(
        self, 
        user_id: str, 
        permis_type: str,
        province: str = "QC"
    ) -> PermisChecklist:
        """
        Crée une nouvelle checklist pour un permis.
        Génération automatique après consultation du permis.
        """
        db = await self._get_db()
        
        # Vérifier si une checklist existe déjà
        existing = await db.permis_checklists.find_one({
            "user_id": user_id,
            "permis_type": permis_type,
            "province": province
        })
        
        if existing:
            return PermisChecklist(**{k: v for k, v in existing.items() if k != '_id'})
        
        # Créer les items de base
        items = []
        for item in BASE_CHECKLIST_ITEMS:
            items.append({
                **item,
                "is_completed": False
            })
        
        # Calculer les dates
        now = datetime.now(timezone.utc)
        next_year = now.replace(year=now.year + 1, month=3, day=31)
        
        checklist = PermisChecklist(
            user_id=user_id,
            permis_type=permis_type,
            province=province,
            items=items,
            completion_percentage=0,
            purchase_date=now.isoformat(),
            expiration_date=next_year.isoformat(),
            reminder_enabled=True,
            reminder_days_before=30,
            created_at=now.isoformat(),
            updated_at=now.isoformat()
        )
        
        await db.permis_checklists.insert_one(asdict(checklist))
        
        return checklist
    
    async def update_item(
        self, 
        user_id: str, 
        permis_type: str,
        item_id: str,
        is_completed: bool
    ) -> PermisChecklist:
        """Met à jour un item de la checklist"""
        db = await self._get_db()
        
        checklist_doc = await db.permis_checklists.find_one({
            "user_id": user_id,
            "permis_type": permis_type
        })
        
        if not checklist_doc:
            raise ValueError("Checklist non trouvée")
        
        # Mettre à jour l'item
        items = checklist_doc.get('items', [])
        for item in items:
            if item['id'] == item_id:
                item['is_completed'] = is_completed
                break
        
        # Calculer le pourcentage
        required_items = [i for i in items if i.get('is_required', True)]
        completed_required = len([i for i in required_items if i.get('is_completed', False)])
        completion_percentage = int((completed_required / len(required_items)) * 100) if required_items else 0
        
        # Sauvegarder
        await db.permis_checklists.update_one(
            {"user_id": user_id, "permis_type": permis_type},
            {"$set": {
                "items": items,
                "completion_percentage": completion_percentage,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        checklist_doc['items'] = items
        checklist_doc['completion_percentage'] = completion_percentage
        
        return PermisChecklist(**{k: v for k, v in checklist_doc.items() if k != '_id'})
    
    async def get_checklist(self, user_id: str, permis_type: str) -> Optional[PermisChecklist]:
        """Récupère une checklist"""
        db = await self._get_db()
        
        doc = await db.permis_checklists.find_one({
            "user_id": user_id,
            "permis_type": permis_type
        })
        
        if doc:
            return PermisChecklist(**{k: v for k, v in doc.items() if k != '_id'})
        return None
    
    async def get_user_checklists(self, user_id: str) -> List[PermisChecklist]:
        """Récupère toutes les checklists d'un utilisateur"""
        db = await self._get_db()
        
        cursor = db.permis_checklists.find({"user_id": user_id}, {"_id": 0})
        docs = await cursor.to_list(length=100)
        
        return [PermisChecklist(**doc) for doc in docs]
    
    async def get_expiring_permits(self, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """
        Récupère les permis qui expirent bientôt.
        Pour le système de rappels automatiques.
        """
        db = await self._get_db()
        
        now = datetime.now(timezone.utc)
        threshold = now + timedelta(days=days_ahead)
        
        cursor = db.permis_checklists.find({
            "reminder_enabled": True,
            "expiration_date": {"$lte": threshold.isoformat()}
        }, {"_id": 0})
        
        return await cursor.to_list(length=1000)
    
    async def set_reminder(
        self, 
        user_id: str, 
        permis_type: str,
        enabled: bool,
        days_before: int = 30
    ) -> bool:
        """Configure le rappel annuel pour un permis"""
        db = await self._get_db()
        
        result = await db.permis_checklists.update_one(
            {"user_id": user_id, "permis_type": permis_type},
            {"$set": {
                "reminder_enabled": enabled,
                "reminder_days_before": days_before,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return result.modified_count > 0


# Instance globale
permis_checklist_service = PermisChecklistService()
