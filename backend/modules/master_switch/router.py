"""
BIONIC Master Switch - X300% Strategy
======================================

Contrôle global ON/OFF pour:
- Captation (Contact Engine)
- Enrichissement (Identity Graph)
- Triggers (Marketing Trigger Engine)
- Scoring (Lead Scoring)
- SEO Engine
- BIONIC Engine (Next Step Engine)

Architecture LEGO V5 - Module isolé.

MODES:
- LOCKED: Système verrouillé (PRÉ-GO LIVE)
- STAGING: Développement interne uniquement (INTERNAL_ONLY)
- PRODUCTION: Système actif avec flux externes
"""

from fastapi import APIRouter, Body
from typing import Dict, Optional
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/master-switch", tags=["Master Switch X300%"])

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


# ═══════════════════════════════════════════════════════════════════════════════
# SYSTÈME DE MODES
# ═══════════════════════════════════════════════════════════════════════════════

SYSTEM_MODES = {
    "LOCKED": {
        "name": "Verrouillé",
        "description": "PRÉ-GO LIVE - Aucune activation",
        "internal_only": True,
        "external_flows": False,
        "icon": "🔒"
    },
    "STAGING": {
        "name": "Staging",
        "description": "Développement interne uniquement",
        "internal_only": True,
        "external_flows": False,
        "icon": "🔧"
    },
    "PRODUCTION": {
        "name": "Production",
        "description": "Système actif avec flux externes",
        "internal_only": False,
        "external_flows": True,
        "icon": "🚀"
    }
}

# VERROUILLAGES EXTERNES (SÉCURITÉ RENFORCÉE)
EXTERNAL_LOCKS = {
    "social_networks": {
        "name": "Réseaux Sociaux",
        "description": "Envoi automatique vers réseaux sociaux",
        "is_locked": True,
        "icon": "📱"
    },
    "partners_platforms": {
        "name": "Partenaires & Plateformes Pub",
        "description": "Envoi automatique vers partenaires/plateformes",
        "is_locked": True,
        "icon": "🤝"
    },
    "external_webhooks": {
        "name": "Webhooks Externes",
        "description": "Webhooks vers services tiers",
        "is_locked": True,
        "icon": "🔗"
    },
    "marketing_flows": {
        "name": "Flux Marketing Externes",
        "description": "Déclenchement de flux marketing externes",
        "is_locked": True,
        "icon": "📢"
    }
}

# Default switch states
DEFAULT_SWITCHES = {
    "global": {
        "name": "Master Switch Global",
        "description": "Contrôle global de tous les modules X300%",
        "is_active": True,
        "icon": "🔌"
    },
    "captation": {
        "name": "Captation",
        "description": "Tracking des visiteurs, publicités, interactions sociales",
        "is_active": True,
        "icon": "📡"
    },
    "enrichment": {
        "name": "Enrichissement",
        "description": "Identity Graph et fusion des profils",
        "is_active": True,
        "icon": "🔗"
    },
    "triggers": {
        "name": "Triggers Marketing",
        "description": "Déclencheurs automatiques et séquences",
        "is_active": True,
        "icon": "⚡"
    },
    "scoring": {
        "name": "Lead Scoring",
        "description": "Calcul automatique des scores de contact",
        "is_active": True,
        "icon": "📊"
    },
    "seo": {
        "name": "SEO Engine",
        "description": "Optimisation et génération de contenu SEO",
        "is_active": True,
        "icon": "🔍"
    },
    "marketing_calendar": {
        "name": "Marketing Calendar",
        "description": "Calendrier et planification des campagnes",
        "is_active": True,
        "icon": "📅"
    },
    "consent_layer": {
        "name": "Consent Layer",
        "description": "Gestion du consentement utilisateur",
        "is_active": True,
        "icon": "🛡️"
    },
    "bionic_engine": {
        "name": "BIONIC Engine",
        "description": "Next Step Engine, Setup Builder, Chasseur Jumeau, Scores",
        "is_active": True,
        "icon": "🎯"
    }
}


@router.get("/status")
async def get_all_switches():
    """
    Récupère l'état de tous les switches.
    """
    db = get_db()
    
    # Check if switches exist
    switches_doc = await db.master_switches.find_one({"_type": "switches"})
    
    if not switches_doc:
        # Initialize with defaults
        switches_doc = {
            "_type": "switches",
            "switches": DEFAULT_SWITCHES,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "updated_by": "system"
        }
        await db.master_switches.insert_one(switches_doc)
    
    switches = switches_doc.get("switches", DEFAULT_SWITCHES)
    
    # Check if global is OFF - all others should be OFF too
    if not switches.get("global", {}).get("is_active", True):
        for key in switches:
            if key != "global":
                switches[key]["effective_state"] = False
    else:
        for key in switches:
            switches[key]["effective_state"] = switches[key].get("is_active", True)
    
    active_count = sum(1 for s in switches.values() if s.get("effective_state", True))
    
    return {
        "success": True,
        "switches": switches,
        "summary": {
            "total": len(switches),
            "active": active_count,
            "inactive": len(switches) - active_count,
            "global_state": switches.get("global", {}).get("is_active", True)
        },
        "last_updated": switches_doc.get("last_updated")
    }


@router.post("/toggle/{switch_id}")
async def toggle_switch(switch_id: str, is_active: bool = Body(..., embed=True)):
    """
    Bascule l'état d'un switch spécifique.
    Si le switch global est désactivé, tous les autres sont désactivés.
    """
    db = get_db()
    
    switches_doc = await db.master_switches.find_one({"_type": "switches"})
    
    if not switches_doc:
        return {"success": False, "error": "Configuration non trouvée"}
    
    switches = switches_doc.get("switches", {})
    
    if switch_id not in switches:
        return {"success": False, "error": f"Switch '{switch_id}' non trouvé"}
    
    # Update the switch
    switches[switch_id]["is_active"] = is_active
    switches[switch_id]["toggled_at"] = datetime.now(timezone.utc).isoformat()
    
    # If toggling global OFF, mark but don't change individual states
    # If toggling global ON, restore individual states
    
    await db.master_switches.update_one(
        {"_type": "switches"},
        {
            "$set": {
                "switches": switches,
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "updated_by": "admin"
            }
        }
    )
    
    # Log the action
    log_entry = {
        "action": "switch_toggle",
        "switch_id": switch_id,
        "new_state": is_active,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    await db.master_switch_logs.insert_one(log_entry)
    
    return {
        "success": True,
        "switch_id": switch_id,
        "is_active": is_active,
        "message": f"Switch '{switches[switch_id]['name']}' {'activé' if is_active else 'désactivé'}"
    }


@router.post("/toggle-all")
async def toggle_all_switches(is_active: bool = Body(..., embed=True)):
    """
    Active ou désactive tous les switches d'un coup via le Master Switch Global.
    """
    db = get_db()
    
    switches_doc = await db.master_switches.find_one({"_type": "switches"})
    
    if not switches_doc:
        # Initialize
        switches_doc = {
            "_type": "switches",
            "switches": DEFAULT_SWITCHES
        }
    
    switches = switches_doc.get("switches", DEFAULT_SWITCHES)
    
    # Update global switch
    switches["global"]["is_active"] = is_active
    switches["global"]["toggled_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.master_switches.update_one(
        {"_type": "switches"},
        {
            "$set": {
                "switches": switches,
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "updated_by": "admin"
            }
        },
        upsert=True
    )
    
    # Log
    log_entry = {
        "action": "global_toggle",
        "new_state": is_active,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    await db.master_switch_logs.insert_one(log_entry)
    
    return {
        "success": True,
        "global_state": is_active,
        "message": f"Tous les modules X300% {'activés' if is_active else 'désactivés'}"
    }


@router.get("/check/{module}")
async def check_module_status(module: str):
    """
    Vérifie si un module spécifique est actif.
    Utilisé par les autres modules pour vérifier avant d'exécuter.
    """
    db = get_db()
    
    switches_doc = await db.master_switches.find_one({"_type": "switches"})
    
    if not switches_doc:
        return {"success": True, "is_active": True, "reason": "defaults"}
    
    switches = switches_doc.get("switches", {})
    
    # Check global first
    if not switches.get("global", {}).get("is_active", True):
        return {"success": True, "is_active": False, "reason": "global_off"}
    
    # Check specific module
    module_switch = switches.get(module, {})
    is_active = module_switch.get("is_active", True)
    
    return {
        "success": True,
        "module": module,
        "is_active": is_active,
        "reason": "module_state"
    }


@router.get("/logs")
async def get_switch_logs(limit: int = 50):
    """
    Historique des changements de switches.
    """
    db = get_db()
    
    logs = await db.master_switch_logs.find({}).sort("timestamp", -1).limit(limit).to_list(limit)
    
    for log in logs:
        log.pop("_id", None)
    
    return {
        "success": True,
        "logs": logs,
        "count": len(logs)
    }


# ═══════════════════════════════════════════════════════════════════════════════
# GESTION DES MODES SYSTÈME
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/mode")
async def get_system_mode():
    """
    Récupère le mode système actuel.
    """
    db = get_db()
    
    mode_doc = await db.master_switches.find_one({"_type": "system_mode"})
    
    if not mode_doc:
        # Initialize with STAGING mode (validation COPILOT MAÎTRE)
        mode_doc = {
            "_type": "system_mode",
            "current_mode": "STAGING",
            "internal_only": True,
            "external_flows": False,
            "external_locks": EXTERNAL_LOCKS,
            "activated_at": datetime.now(timezone.utc).isoformat(),
            "activated_by": "COPILOT_MAITRE_STEEVE",
            "validation_signature": "2026-02-19_AUDIT_VALIDATED"
        }
        await db.master_switches.insert_one(mode_doc)
    
    mode_info = SYSTEM_MODES.get(mode_doc.get("current_mode", "LOCKED"), SYSTEM_MODES["LOCKED"])
    
    return {
        "success": True,
        "current_mode": mode_doc.get("current_mode", "LOCKED"),
        "mode_info": mode_info,
        "internal_only": mode_doc.get("internal_only", True),
        "external_flows": mode_doc.get("external_flows", False),
        "external_locks": mode_doc.get("external_locks", EXTERNAL_LOCKS),
        "activated_at": mode_doc.get("activated_at"),
        "activated_by": mode_doc.get("activated_by")
    }


@router.post("/mode/set")
async def set_system_mode(mode: str = Body(..., embed=True), authorized_by: str = Body(..., embed=True)):
    """
    Change le mode système.
    REQUIERT autorisation COPILOT MAÎTRE.
    """
    db = get_db()
    
    if mode not in SYSTEM_MODES:
        return {"success": False, "error": f"Mode invalide. Modes disponibles: {list(SYSTEM_MODES.keys())}"}
    
    mode_info = SYSTEM_MODES[mode]
    
    update_data = {
        "_type": "system_mode",
        "current_mode": mode,
        "internal_only": mode_info["internal_only"],
        "external_flows": mode_info["external_flows"],
        "external_locks": EXTERNAL_LOCKS,  # Toujours verrouillés sauf PRODUCTION explicite
        "activated_at": datetime.now(timezone.utc).isoformat(),
        "activated_by": authorized_by
    }
    
    await db.master_switches.update_one(
        {"_type": "system_mode"},
        {"$set": update_data},
        upsert=True
    )
    
    # Log the mode change
    log_entry = {
        "action": "mode_change",
        "new_mode": mode,
        "authorized_by": authorized_by,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    await db.master_switch_logs.insert_one(log_entry)
    
    return {
        "success": True,
        "mode": mode,
        "mode_info": mode_info,
        "internal_only": mode_info["internal_only"],
        "external_flows": mode_info["external_flows"],
        "message": f"Mode système changé vers {mode} par {authorized_by}"
    }


@router.get("/external-locks")
async def get_external_locks():
    """
    Récupère l'état des verrouillages externes.
    """
    db = get_db()
    
    mode_doc = await db.master_switches.find_one({"_type": "system_mode"})
    
    locks = mode_doc.get("external_locks", EXTERNAL_LOCKS) if mode_doc else EXTERNAL_LOCKS
    
    all_locked = all(lock.get("is_locked", True) for lock in locks.values())
    
    return {
        "success": True,
        "external_locks": locks,
        "all_locked": all_locked,
        "security_status": "RENFORCÉ" if all_locked else "PARTIELLEMENT_ACTIF"
    }


@router.get("/full-status")
async def get_full_system_status():
    """
    Retourne le statut complet du système (mode + switches + locks).
    """
    db = get_db()
    
    # Mode
    mode_doc = await db.master_switches.find_one({"_type": "system_mode"})
    current_mode = mode_doc.get("current_mode", "LOCKED") if mode_doc else "LOCKED"
    mode_info = SYSTEM_MODES.get(current_mode, SYSTEM_MODES["LOCKED"])
    
    # Switches
    switches_doc = await db.master_switches.find_one({"_type": "switches"})
    switches = switches_doc.get("switches", DEFAULT_SWITCHES) if switches_doc else DEFAULT_SWITCHES
    
    # External Locks
    external_locks = mode_doc.get("external_locks", EXTERNAL_LOCKS) if mode_doc else EXTERNAL_LOCKS
    
    active_switches = sum(1 for s in switches.values() if s.get("is_active", True))
    all_locked = all(lock.get("is_locked", True) for lock in external_locks.values())
    
    return {
        "success": True,
        "system": {
            "mode": current_mode,
            "mode_info": mode_info,
            "internal_only": mode_info["internal_only"],
            "external_flows": mode_info["external_flows"]
        },
        "switches": {
            "total": len(switches),
            "active": active_switches,
            "global_state": switches.get("global", {}).get("is_active", True)
        },
        "security": {
            "external_locks_status": "ALL_LOCKED" if all_locked else "PARTIALLY_ACTIVE",
            "external_locks": external_locks
        },
        "bionic_engine_status": "ACTIVE" if switches.get("bionic_engine", {}).get("is_active", True) else "INACTIVE"
    }


logger.info("Master Switch X300% initialized - LEGO V5 Module - MODE STAGING ACTIVÉ")


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL MASTER SWITCH — Absorbé de global_master_switch/ (Phase 1.6-B)
# Contrôle Central du Système Publicitaire
# ═══════════════════════════════════════════════════════════════════════════════

from fastapi import Query as FastAPIQuery
from enum import Enum as PyEnum
import uuid

global_switch_router = APIRouter(prefix="/api/v1/global-switch", tags=["Global Master Switch"])


class SwitchStatus(str, PyEnum):
    ON = "ON"
    OFF = "OFF"
    LOCKED = "LOCKED"


class ControlledEngine(str, PyEnum):
    AFFILIATE_ADS = "affiliate_ad_automation_engine"
    AD_SPACES = "ad_spaces_engine"
    AD_SLOTS = "ad_slot_manager"
    AD_RENDER = "ad_render_engine"
    MARKETING = "marketing_engine"
    CALENDAR = "calendar_engine"


CONTROLLED_ENGINES = [
    {
        "id": ControlledEngine.AFFILIATE_ADS.value,
        "name": "Affiliate Ad Automation Engine",
        "description": "Cycle de vente publicitaire automatisé",
        "api_prefix": "/api/v1/affiliate-ads"
    },
    {
        "id": ControlledEngine.AD_SPACES.value,
        "name": "Ad Spaces Engine",
        "description": "Gestion des 18 espaces publicitaires",
        "api_prefix": "/api/v1/ad-spaces"
    },
    {
        "id": ControlledEngine.AD_SLOTS.value,
        "name": "Ad Slot Manager",
        "description": "Attribution et réservation des emplacements",
        "api_prefix": "/api/v1/ad-spaces/slots"
    },
    {
        "id": ControlledEngine.AD_RENDER.value,
        "name": "Ad Render Engine",
        "description": "Injection et affichage des publicités",
        "api_prefix": "/api/v1/ad-spaces/render"
    },
    {
        "id": ControlledEngine.MARKETING.value,
        "name": "Marketing Engine",
        "description": "Campagnes marketing automatisées",
        "api_prefix": "/api/v1/marketing"
    },
    {
        "id": ControlledEngine.CALENDAR.value,
        "name": "Calendar Engine",
        "description": "Planification des campagnes",
        "api_prefix": "/api/v1/calendar"
    }
]


@global_switch_router.get("/")
async def get_global_module_info():
    """Information sur le Global Master Switch"""
    db = get_db()
    switch = await db.global_master_switch.find_one({"switch_id": "BIONIC_GLOBAL"})
    return {
        "module": "global_master_switch",
        "version": "1.0.0",
        "description": "GROS BOUTON ROUGE - Contrôle global du système publicitaire BIONIC",
        "architecture": "LEGO_V5_ULTIME",
        "features": [
            "Contrôle ON/OFF/LOCKED global",
            "Synchronisation de tous les engines publicitaires",
            "Blocage du déploiement automatique",
            "Journalisation horodatée des actions",
            "Accès restreint (COPILOT MAÎTRE uniquement)"
        ],
        "current_status": switch.get("status") if switch else "NOT_INITIALIZED",
        "controlled_engines": [e["name"] for e in CONTROLLED_ENGINES]
    }


@global_switch_router.get("/status")
async def get_global_switch_status():
    """Obtenir le statut actuel du Global Master Switch."""
    db = get_db()
    switch = await db.global_master_switch.find_one({"switch_id": "BIONIC_GLOBAL"})
    if not switch:
        switch = {
            "switch_id": "BIONIC_GLOBAL",
            "status": SwitchStatus.LOCKED.value,
            "is_active": False,
            "auto_deploy_blocked": True,
            "reason": "Mode PRÉ-PRODUCTION - En attente du signal GO LIVE de COPILOT MAÎTRE",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "last_updated_by": "system_init",
            "engines_status": {e["id"]: False for e in CONTROLLED_ENGINES},
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.global_master_switch.insert_one(switch)
    switch.pop("_id", None)
    ad_master = await db.ad_master_switch.find_one({"switch_id": "global"})
    return {
        "success": True,
        "global_switch": switch,
        "ad_master_switch": {
            "is_active": ad_master.get("is_active") if ad_master else False,
            "reason": ad_master.get("reason") if ad_master else "Non initialisé"
        },
        "controlled_engines": CONTROLLED_ENGINES,
        "mode": "PRÉ-PRODUCTION" if switch["status"] != SwitchStatus.ON.value else "PRODUCTION"
    }


@global_switch_router.post("/toggle")
async def toggle_global_switch(
    new_status: str = Body(..., embed=True),
    reason: Optional[str] = Body(None, embed=True),
    admin_user: str = Body("admin", embed=True)
):
    """Basculer le Global Master Switch."""
    db = get_db()
    if new_status not in [s.value for s in SwitchStatus]:
        from fastapi import HTTPException as _HTTPException
        raise _HTTPException(
            status_code=400,
            detail=f"Statut invalide. Valeurs acceptées: {[s.value for s in SwitchStatus]}"
        )
    now = datetime.now(timezone.utc).isoformat()
    is_active = new_status == SwitchStatus.ON.value
    switch_updates = {
        "status": new_status,
        "is_active": is_active,
        "auto_deploy_blocked": not is_active,
        "reason": reason or f"Basculement vers {new_status}",
        "last_updated": now,
        "last_updated_by": admin_user
    }
    await db.global_master_switch.update_one(
        {"switch_id": "BIONIC_GLOBAL"}, {"$set": switch_updates}, upsert=True
    )
    await db.ad_master_switch.update_one(
        {"switch_id": "global"},
        {"$set": {
            "is_active": is_active,
            "auto_deploy_enabled": is_active,
            "reason": switch_updates["reason"],
            "updated_at": now,
            "updated_by": admin_user
        }},
        upsert=True
    )
    engines_status = {engine["id"]: is_active for engine in CONTROLLED_ENGINES}
    await db.global_master_switch.update_one(
        {"switch_id": "BIONIC_GLOBAL"}, {"$set": {"engines_status": engines_status}}
    )
    if not is_active:
        await db.ad_opportunities.update_many(
            {"status": "active"},
            {"$set": {"status": "paused", "paused_at": now, "pause_reason": switch_updates["reason"]}}
        )
        await db.ad_opportunities.update_many(
            {"status": {"$in": ["pending", "email_sent", "checkout_started", "payment_pending"]}},
            {"$set": {"status": "suspended", "suspended_at": now, "suspend_reason": switch_updates["reason"]}}
        )
        await db.deployed_ads.update_many(
            {"is_active": True}, {"$set": {"is_active": False, "deactivated_at": now}}
        )
        await db.ad_slot_reservations.update_many(
            {"status": "active"}, {"$set": {"status": "paused", "paused_at": now}}
        )
    await _log_global_switch_action(db, "global_toggle", admin_user, {
        "previous_status": "unknown", "new_status": new_status,
        "reason": switch_updates["reason"], "is_active": is_active
    })
    return {
        "success": True, "status": new_status, "is_active": is_active,
        "auto_deploy_blocked": not is_active, "engines_affected": len(CONTROLLED_ENGINES),
        "message": f"Global Master Switch -> {new_status}" + (" (Système ACTIF)" if is_active else " (Système VERROUILLÉ)")
    }


@global_switch_router.post("/lock")
async def lock_global_system(
    reason: str = Body(..., embed=True),
    admin_user: str = Body("COPILOT_MAITRE", embed=True)
):
    """Verrouiller le système publicitaire (mode LOCKED)."""
    return await toggle_global_switch(
        new_status=SwitchStatus.LOCKED.value, reason=reason, admin_user=admin_user
    )


@global_switch_router.post("/unlock")
async def unlock_global_system(
    admin_user: str = Body("COPILOT_MAITRE", embed=True)
):
    """Déverrouiller et activer le système (GO LIVE)."""
    return await toggle_global_switch(
        new_status=SwitchStatus.ON.value,
        reason="GO LIVE - Activation par COPILOT MAÎTRE",
        admin_user=admin_user
    )


@global_switch_router.get("/engines")
async def get_global_engines_status():
    """Obtenir le statut de tous les engines contrôlés."""
    db = get_db()
    switch = await db.global_master_switch.find_one({"switch_id": "BIONIC_GLOBAL"})
    engines_status = switch.get("engines_status", {}) if switch else {}
    engines = []
    for engine in CONTROLLED_ENGINES:
        engines.append({
            **engine,
            "is_active": engines_status.get(engine["id"], False),
            "status": "ACTIVE" if engines_status.get(engine["id"]) else "DISABLED"
        })
    return {
        "success": True,
        "global_status": switch.get("status") if switch else "NOT_INITIALIZED",
        "engines": engines,
        "total_active": sum(1 for e in engines if e["is_active"]),
        "total_disabled": sum(1 for e in engines if not e["is_active"])
    }


@global_switch_router.post("/engines/{engine_id}/toggle")
async def toggle_global_engine(
    engine_id: str,
    is_active: bool = Body(..., embed=True),
    admin_user: str = Body("admin", embed=True)
):
    """Contrôler un engine spécifique (si le Global Switch est ON)."""
    db = get_db()
    switch = await db.global_master_switch.find_one({"switch_id": "BIONIC_GLOBAL"})
    if switch and switch.get("status") == SwitchStatus.LOCKED.value:
        return {
            "success": False,
            "error": "Système verrouillé - Impossible de modifier les engines individuels",
            "global_status": "LOCKED"
        }
    valid_ids = [e["id"] for e in CONTROLLED_ENGINES]
    if engine_id not in valid_ids:
        from fastapi import HTTPException as _HTTPException
        raise _HTTPException(status_code=404, detail=f"Engine non trouvé. Engines valides: {valid_ids}")
    await db.global_master_switch.update_one(
        {"switch_id": "BIONIC_GLOBAL"}, {"$set": {f"engines_status.{engine_id}": is_active}}
    )
    await _log_global_switch_action(db, "engine_toggle", admin_user, {
        "engine_id": engine_id, "new_status": is_active
    })
    return {
        "success": True, "engine_id": engine_id, "is_active": is_active,
        "message": f"Engine '{engine_id}' -> {'ACTIVÉ' if is_active else 'DÉSACTIVÉ'}"
    }


@global_switch_router.get("/logs")
async def get_global_switch_logs(limit: int = FastAPIQuery(100, le=500)):
    """Historique des actions sur le Global Master Switch."""
    db = get_db()
    logs = await db.global_switch_logs.find({}).sort("timestamp", -1).limit(limit).to_list(limit)
    for log in logs:
        log.pop("_id", None)
    return {"success": True, "logs": logs, "count": len(logs)}


async def _log_global_switch_action(db, action: str, admin_user: str, details: Dict = None):
    """Journaliser une action sur le global switch."""
    log_entry = {
        "log_id": str(uuid.uuid4()),
        "action": action,
        "admin_user": admin_user,
        "details": details or {},
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    await db.global_switch_logs.insert_one(log_entry)


@global_switch_router.get("/dashboard")
async def get_global_switch_dashboard():
    """Dashboard du Global Master Switch."""
    db = get_db()
    switch = await db.global_master_switch.find_one({"switch_id": "BIONIC_GLOBAL"})
    total_opportunities = await db.ad_opportunities.count_documents({})
    active_opportunities = await db.ad_opportunities.count_documents({"status": "active"})
    paused_opportunities = await db.ad_opportunities.count_documents({"status": "paused"})
    suspended_opportunities = await db.ad_opportunities.count_documents({"status": "suspended"})
    active_ads = await db.deployed_ads.count_documents({"is_active": True})
    inactive_ads = await db.deployed_ads.count_documents({"is_active": False})
    active_slots = await db.ad_slot_reservations.count_documents({"status": "active"})
    paused_slots = await db.ad_slot_reservations.count_documents({"status": "paused"})
    recent_logs = await db.global_switch_logs.find({}).sort("timestamp", -1).limit(10).to_list(10)
    for log in recent_logs:
        log.pop("_id", None)
    return {
        "success": True,
        "dashboard": {
            "global_switch": {
                "status": switch.get("status") if switch else "NOT_INITIALIZED",
                "is_active": switch.get("is_active") if switch else False,
                "auto_deploy_blocked": switch.get("auto_deploy_blocked") if switch else True,
                "reason": switch.get("reason") if switch else "Non initialisé",
                "last_updated": switch.get("last_updated") if switch else None,
                "last_updated_by": switch.get("last_updated_by") if switch else None
            },
            "mode": "PRODUCTION" if (switch and switch.get("is_active")) else "PRÉ-PRODUCTION",
            "opportunities": {
                "total": total_opportunities, "active": active_opportunities,
                "paused": paused_opportunities, "suspended": suspended_opportunities
            },
            "deployed_ads": {"active": active_ads, "inactive": inactive_ads},
            "slots": {"active": active_slots, "paused": paused_slots},
            "controlled_engines": len(CONTROLLED_ENGINES),
            "recent_activity": recent_logs
        }
    }


logger.info("Global Master Switch initialized (merged into master_switch module - Phase 1.6-B)")
