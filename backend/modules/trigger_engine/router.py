"""
BIONIC Marketing Trigger Engine - X300% Strategy
=================================================

Moteur de déclencheurs marketing automatiques:
- Triggers basés sur visites, clics, interactions
- Promotions automatiques
- Séquences de relance
- Triggers modulaires activables/désactivables

Architecture LEGO V5 - Module isolé.
"""

from fastapi import APIRouter, Body, Query
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/trigger-engine", tags=["Marketing Trigger Engine X300%"])

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'bionic_db')

_client = None
_db = None

def get_db():
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(MONGO_URL)
        _db = _client[DB_NAME]
    return _db


# Default triggers configuration
DEFAULT_TRIGGERS = [
    {
        "id": "trigger_first_visit",
        "name": "Première visite",
        "name_fr": "Première visite",
        "trigger_type": "visit",
        "condition": {"visit_count": 1},
        "action": "show_welcome_popup",
        "action_config": {
            "popup_type": "welcome",
            "offer": "10% de réduction sur la première commande",
            "code": "BIENVENUE10"
        },
        "delay_minutes": 0,
        "is_active": True,
        "priority": 1
    },
    {
        "id": "trigger_return_visitor",
        "name": "Visiteur de retour",
        "name_fr": "Visiteur de retour",
        "trigger_type": "visit",
        "condition": {"visit_count": {"$gte": 3}},
        "action": "send_email",
        "action_config": {
            "template": "return_visitor",
            "subject": "Content de vous revoir!"
        },
        "delay_minutes": 1440,  # 24h
        "is_active": True,
        "priority": 2
    },
    {
        "id": "trigger_ad_click",
        "name": "Clic publicitaire",
        "name_fr": "Clic publicitaire",
        "trigger_type": "ad_click",
        "condition": {},
        "action": "show_promo_popup",
        "action_config": {
            "popup_type": "promo",
            "message": "Offre spéciale pour vous!",
            "discount": 15
        },
        "delay_minutes": 0,
        "is_active": True,
        "priority": 1
    },
    {
        "id": "trigger_cart_abandon",
        "name": "Abandon de panier",
        "name_fr": "Abandon de panier",
        "trigger_type": "cart_abandon",
        "condition": {"cart_value": {"$gte": 50}},
        "action": "send_email_sequence",
        "action_config": {
            "sequence": ["reminder_1h", "reminder_24h", "final_offer_48h"],
            "offer": "Livraison gratuite"
        },
        "delay_minutes": 60,
        "is_active": True,
        "priority": 1
    },
    {
        "id": "trigger_high_intent",
        "name": "Intention d'achat élevée",
        "name_fr": "Intention d'achat élevée",
        "trigger_type": "score_threshold",
        "condition": {"scores.purchase_intent": {"$gte": 50}},
        "action": "assign_to_sales",
        "action_config": {
            "notify_team": True,
            "add_tag": "hot_lead"
        },
        "delay_minutes": 0,
        "is_active": True,
        "priority": 1
    },
    {
        "id": "trigger_social_engagement",
        "name": "Engagement social",
        "name_fr": "Engagement social",
        "trigger_type": "social_interaction",
        "condition": {"action": "share"},
        "action": "reward_points",
        "action_config": {
            "points": 100,
            "message": "Merci pour le partage!"
        },
        "delay_minutes": 0,
        "is_active": True,
        "priority": 2
    },
    {
        "id": "trigger_inactive_30d",
        "name": "Inactif 30 jours",
        "name_fr": "Inactif 30 jours",
        "trigger_type": "inactivity",
        "condition": {"days_inactive": 30},
        "action": "send_reactivation_email",
        "action_config": {
            "template": "win_back",
            "offer": "20% de réduction pour revenir"
        },
        "delay_minutes": 0,
        "is_active": True,
        "priority": 3
    }
]


# ============================================
# TRIGGERS CRUD
# ============================================

@router.get("/triggers")
async def get_triggers():
    """
    Liste tous les triggers configurés.
    """
    db = get_db()
    
    # Check if triggers exist in DB
    count = await db.marketing_triggers.count_documents({})
    
    if count == 0:
        # Initialize default triggers
        for trigger in DEFAULT_TRIGGERS:
            trigger["created_at"] = datetime.now(timezone.utc).isoformat()
            await db.marketing_triggers.insert_one(trigger.copy())
    
    triggers = await db.marketing_triggers.find({}).to_list(100)
    
    for t in triggers:
        t.pop("_id", None)
    
    active_count = sum(1 for t in triggers if t.get("is_active"))
    
    return {
        "success": True,
        "triggers": triggers,
        "stats": {
            "total": len(triggers),
            "active": active_count,
            "inactive": len(triggers) - active_count
        }
    }


@router.post("/triggers")
async def create_trigger(
    trigger_data: Dict[str, Any] = Body(...)
):
    """
    Créer un nouveau trigger.
    """
    db = get_db()
    
    trigger = {
        "id": trigger_data.get("id") or f"trigger_{uuid.uuid4().hex[:8]}",
        "name": trigger_data.get("name"),
        "name_fr": trigger_data.get("name_fr", trigger_data.get("name")),
        "trigger_type": trigger_data.get("trigger_type"),
        "condition": trigger_data.get("condition", {}),
        "action": trigger_data.get("action"),
        "action_config": trigger_data.get("action_config", {}),
        "delay_minutes": trigger_data.get("delay_minutes", 0),
        "is_active": trigger_data.get("is_active", True),
        "priority": trigger_data.get("priority", 5),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.marketing_triggers.insert_one(trigger)
    trigger.pop("_id", None)
    
    return {"success": True, "trigger": trigger}


@router.put("/triggers/{trigger_id}/toggle")
async def toggle_trigger(trigger_id: str, is_active: bool = Body(..., embed=True)):
    """
    Activer/désactiver un trigger.
    """
    db = get_db()
    
    result = await db.marketing_triggers.update_one(
        {"id": trigger_id},
        {"$set": {"is_active": is_active, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    if result.modified_count == 0:
        return {"success": False, "error": "Trigger non trouvé"}
    
    return {"success": True, "trigger_id": trigger_id, "is_active": is_active}


@router.delete("/triggers/{trigger_id}")
async def delete_trigger(trigger_id: str):
    """
    Supprimer un trigger.
    """
    db = get_db()
    
    result = await db.marketing_triggers.delete_one({"id": trigger_id})
    
    if result.deleted_count == 0:
        return {"success": False, "error": "Trigger non trouvé"}
    
    return {"success": True, "deleted": trigger_id}


# ============================================
# TRIGGER EXECUTION
# ============================================

@router.post("/execute")
async def execute_trigger(
    execution_data: Dict[str, Any] = Body(...)
):
    """
    Exécuter un trigger manuellement ou automatiquement.
    """
    db = get_db()
    
    trigger_id = execution_data.get("trigger_id")
    contact_data = execution_data.get("contact_data", {})
    
    # Get trigger config
    trigger = await db.marketing_triggers.find_one({"id": trigger_id})
    
    if not trigger:
        return {"success": False, "error": "Trigger non trouvé"}
    
    if not trigger.get("is_active"):
        return {"success": False, "error": "Trigger désactivé"}
    
    # Log execution
    execution_log = {
        "trigger_id": trigger_id,
        "trigger_name": trigger.get("name"),
        "action": trigger.get("action"),
        "contact_id": contact_data.get("visitor_id") or contact_data.get("email"),
        "status": "executed",
        "executed_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.trigger_executions.insert_one(execution_log)
    
    return {
        "success": True,
        "execution": {
            "trigger_id": trigger_id,
            "action": trigger.get("action"),
            "action_config": trigger.get("action_config"),
            "status": "executed"
        }
    }


@router.post("/check")
async def check_triggers_for_contact(
    contact_data: Dict[str, Any] = Body(...)
):
    """
    Vérifie quels triggers doivent être déclenchés pour un contact.
    """
    db = get_db()
    
    # Get active triggers sorted by priority
    triggers = await db.marketing_triggers.find({"is_active": True}).sort("priority", 1).to_list(100)
    
    triggered = []
    
    for trigger in triggers:
        # Simple condition matching (can be extended)
        should_trigger = True
        condition = trigger.get("condition", {})
        
        for key, value in condition.items():
            contact_value = contact_data.get(key)
            
            if isinstance(value, dict):
                # Handle operators like $gte, $lte
                if "$gte" in value and (contact_value is None or contact_value < value["$gte"]):
                    should_trigger = False
                    break
                if "$lte" in value and (contact_value is None or contact_value > value["$lte"]):
                    should_trigger = False
                    break
            else:
                if contact_value != value:
                    should_trigger = False
                    break
        
        if should_trigger:
            triggered.append({
                "trigger_id": trigger.get("id"),
                "name": trigger.get("name_fr"),
                "action": trigger.get("action"),
                "action_config": trigger.get("action_config"),
                "priority": trigger.get("priority")
            })
    
    return {
        "success": True,
        "triggered": triggered,
        "count": len(triggered)
    }


# ============================================
# EXECUTION HISTORY
# ============================================

@router.get("/executions")
async def get_trigger_executions(
    trigger_id: Optional[str] = None,
    limit: int = Query(50, le=200)
):
    """
    Historique des exécutions de triggers.
    """
    db = get_db()
    
    query = {}
    if trigger_id:
        query["trigger_id"] = trigger_id
    
    executions = await db.trigger_executions.find(query).sort("executed_at", -1).limit(limit).to_list(limit)
    
    for e in executions:
        e.pop("_id", None)
    
    return {
        "success": True,
        "executions": executions,
        "count": len(executions)
    }


# ============================================
# STATS
# ============================================

@router.get("/stats")
async def get_trigger_stats():
    """
    Statistiques des triggers.
    """
    db = get_db()
    
    # Trigger counts
    total_triggers = await db.marketing_triggers.count_documents({})
    active_triggers = await db.marketing_triggers.count_documents({"is_active": True})
    
    # Execution counts
    total_executions = await db.trigger_executions.count_documents({})
    
    # Executions by trigger
    pipeline = [
        {"$group": {"_id": "$trigger_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    top_triggers = await db.trigger_executions.aggregate(pipeline).to_list(10)
    
    return {
        "success": True,
        "stats": {
            "triggers": {
                "total": total_triggers,
                "active": active_triggers,
                "inactive": total_triggers - active_triggers
            },
            "executions": {
                "total": total_executions
            },
            "top_triggers": top_triggers
        }
    }


logger.info("Marketing Trigger Engine X300% initialized - LEGO V5 Module")
