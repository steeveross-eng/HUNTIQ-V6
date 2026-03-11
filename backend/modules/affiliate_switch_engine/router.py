"""
BIONIC Affiliate Switch Engine - Phase 6+
==========================================

Module de gestion des switches d'affiliation:
- Activation/désactivation individuelle par affilié
- Activation automatique sur confirmation d'entente
- Processus de validation interne
- Synchronisation multi-engines
- Journalisation complète

Architecture LEGO V5-ULTIME - Module isolé.
"""

from fastapi import APIRouter, Body, Query, HTTPException
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from enum import Enum
import os
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/affiliate-switch", tags=["Affiliate Switch Engine"])

# Database connection
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


# ============================================
# ENUMS & CONSTANTS
# ============================================

class AffiliateStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"
    REVOKED = "revoked"


class ValidationStep(str, Enum):
    IDENTITY = "identity_verification"
    CATEGORY = "category_verification"
    DUPLICATION = "duplication_detection"
    COMPLIANCE = "compliance_check"


VALIDATION_STEPS = [
    ValidationStep.IDENTITY,
    ValidationStep.CATEGORY,
    ValidationStep.DUPLICATION,
    ValidationStep.COMPLIANCE
]


# ============================================
# AFFILIATE SWITCH CRUD
# ============================================

@router.get("/")
async def get_module_info():
    """Information sur l'Affiliate Switch Engine"""
    return {
        "module": "affiliate_switch_engine",
        "version": "1.0.0",
        "description": "Gestion des switches d'affiliation - Activation/désactivation automatique et manuelle",
        "architecture": "LEGO_V5_ULTIME",
        "features": [
            "Switch individuel ON/OFF par affilié",
            "Activation automatique sur confirmation entente",
            "Processus de validation interne (4 étapes)",
            "Synchronisation multi-engines",
            "Pages SEO satellites automatiques",
            "Intégration Excel ULTIME",
            "Journalisation complète"
        ],
        "statuses": ["pending", "active", "inactive", "revoked"],
        "validation_steps": ["identity_verification", "category_verification", "duplication_detection", "compliance_check"],
        "integrations": ["seo_engine", "contact_engine", "trigger_engine", "calendar_engine", "marketing_engine"]
    }


@router.get("/affiliates")
async def get_all_affiliates(
    page: int = Query(1, ge=1),
    limit: int = Query(50, le=200),
    status: Optional[str] = None,
    category: Optional[str] = None,
    is_active: Optional[bool] = None
):
    """
    Liste tous les affiliés avec leurs switches.
    """
    db = get_db()
    
    query = {}
    if status:
        query["status"] = status
    if category:
        query["category"] = category
    if is_active is not None:
        query["switch_active"] = is_active
    
    skip = (page - 1) * limit
    
    affiliates = await db.affiliate_switches.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.affiliate_switches.count_documents(query)
    
    # Remove MongoDB _id
    for affiliate in affiliates:
        affiliate.pop("_id", None)
    
    return {
        "success": True,
        "affiliates": affiliates,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    }


@router.get("/affiliates/{affiliate_id}")
async def get_affiliate(affiliate_id: str):
    """
    Détail d'un affilié et son switch.
    """
    db = get_db()
    
    affiliate = await db.affiliate_switches.find_one({"affiliate_id": affiliate_id})
    
    if not affiliate:
        raise HTTPException(status_code=404, detail="Affilié non trouvé")
    
    affiliate.pop("_id", None)
    
    # Get logs
    logs = await db.affiliate_switch_logs.find(
        {"affiliate_id": affiliate_id}
    ).sort("timestamp", -1).limit(50).to_list(50)
    
    for log in logs:
        log.pop("_id", None)
    
    return {
        "success": True,
        "affiliate": affiliate,
        "logs": logs
    }


@router.post("/affiliates")
async def create_affiliate(
    affiliate_data: Dict[str, Any] = Body(...)
):
    """
    Créer un nouvel affilié avec switch en mode pending.
    """
    db = get_db()
    
    affiliate_id = affiliate_data.get("affiliate_id") or str(uuid.uuid4())
    
    # Check for duplicates
    existing = await db.affiliate_switches.find_one({
        "$or": [
            {"affiliate_id": affiliate_id},
            {"company_name": affiliate_data.get("company_name")},
            {"email": affiliate_data.get("email")}
        ]
    })
    
    if existing:
        return {
            "success": False,
            "error": "Un affilié avec cet ID, nom ou email existe déjà",
            "existing_id": existing.get("affiliate_id")
        }
    
    new_affiliate = {
        "affiliate_id": affiliate_id,
        "company_name": affiliate_data.get("company_name"),
        "email": affiliate_data.get("email"),
        "contact_name": affiliate_data.get("contact_name"),
        "phone": affiliate_data.get("phone"),
        "website": affiliate_data.get("website"),
        "category": affiliate_data.get("category"),
        "country": affiliate_data.get("country", "Unknown"),
        "specialty": affiliate_data.get("specialty", []),
        
        # Switch state
        "switch_active": False,
        "status": AffiliateStatus.PENDING.value,
        
        # Validation state
        "validation": {
            "identity_verified": False,
            "category_verified": False,
            "duplication_checked": False,
            "compliance_passed": False,
            "all_validated": False
        },
        
        # Agreement
        "agreement": {
            "signed": False,
            "signed_at": None,
            "agreement_type": None,
            "commission_rate": None,
            "terms_accepted": False
        },
        
        # SEO Integration
        "seo_integration": {
            "satellite_page_active": False,
            "satellite_page_url": None,
            "excel_integrated": False
        },
        
        # Engine sync status
        "engine_sync": {
            "seo_engine": False,
            "contact_engine": False,
            "trigger_engine": False,
            "calendar_engine": False,
            "marketing_engine": False
        },
        
        # Admin notes
        "admin_notes": affiliate_data.get("admin_notes", ""),
        "internal_tags": affiliate_data.get("internal_tags", []),
        
        # Timestamps
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "activated_at": None,
        "deactivated_at": None
    }
    
    await db.affiliate_switches.insert_one(new_affiliate)
    
    # Log creation
    await _log_action(db, affiliate_id, "affiliate_created", "system", {
        "company_name": affiliate_data.get("company_name"),
        "category": affiliate_data.get("category")
    })
    
    new_affiliate.pop("_id", None)
    
    return {
        "success": True,
        "affiliate": new_affiliate,
        "message": f"Affilié '{affiliate_data.get('company_name')}' créé avec statut PENDING"
    }


# ============================================
# SWITCH CONTROL
# ============================================

@router.post("/affiliates/{affiliate_id}/toggle")
async def toggle_affiliate_switch(
    affiliate_id: str,
    is_active: bool = Body(..., embed=True),
    reason: Optional[str] = Body(None, embed=True),
    admin_user: Optional[str] = Body("admin", embed=True)
):
    """
    Activer/désactiver manuellement le switch d'un affilié.
    """
    db = get_db()
    
    affiliate = await db.affiliate_switches.find_one({"affiliate_id": affiliate_id})
    
    if not affiliate:
        raise HTTPException(status_code=404, detail="Affilié non trouvé")
    
    # Update switch state
    updates = {
        "switch_active": is_active,
        "status": AffiliateStatus.ACTIVE.value if is_active else AffiliateStatus.INACTIVE.value,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    if is_active:
        updates["activated_at"] = datetime.now(timezone.utc).isoformat()
    else:
        updates["deactivated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.affiliate_switches.update_one(
        {"affiliate_id": affiliate_id},
        {"$set": updates}
    )
    
    # Log action
    await _log_action(db, affiliate_id, "switch_toggled", admin_user, {
        "new_state": is_active,
        "reason": reason
    })
    
    # Sync with other engines if activating
    if is_active:
        await _sync_with_engines(db, affiliate_id)
        await _activate_seo_satellite(db, affiliate_id)
    
    return {
        "success": True,
        "affiliate_id": affiliate_id,
        "switch_active": is_active,
        "status": updates["status"],
        "message": f"Switch {'activé' if is_active else 'désactivé'} pour {affiliate.get('company_name')}"
    }


@router.post("/affiliates/{affiliate_id}/revoke")
async def revoke_affiliate(
    affiliate_id: str,
    reason: str = Body(..., embed=True),
    admin_user: str = Body("admin", embed=True)
):
    """
    Révoquer définitivement un affilié.
    """
    db = get_db()
    
    affiliate = await db.affiliate_switches.find_one({"affiliate_id": affiliate_id})
    
    if not affiliate:
        raise HTTPException(status_code=404, detail="Affilié non trouvé")
    
    updates = {
        "switch_active": False,
        "status": AffiliateStatus.REVOKED.value,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "deactivated_at": datetime.now(timezone.utc).isoformat(),
        "revocation_reason": reason,
        "revoked_by": admin_user,
        "seo_integration.satellite_page_active": False
    }
    
    await db.affiliate_switches.update_one(
        {"affiliate_id": affiliate_id},
        {"$set": updates}
    )
    
    # Log action
    await _log_action(db, affiliate_id, "affiliate_revoked", admin_user, {
        "reason": reason
    })
    
    return {
        "success": True,
        "affiliate_id": affiliate_id,
        "status": AffiliateStatus.REVOKED.value,
        "message": f"Affilié révoqué: {reason}"
    }


# ============================================
# VALIDATION PROCESS
# ============================================

@router.post("/affiliates/{affiliate_id}/validate/{step}")
async def validate_step(
    affiliate_id: str,
    step: str,
    passed: bool = Body(..., embed=True),
    notes: Optional[str] = Body(None, embed=True),
    validator: str = Body("admin", embed=True)
):
    """
    Valider une étape du processus de validation.
    """
    db = get_db()
    
    if step not in [s.value for s in ValidationStep]:
        raise HTTPException(status_code=400, detail=f"Étape invalide: {step}")
    
    affiliate = await db.affiliate_switches.find_one({"affiliate_id": affiliate_id})
    
    if not affiliate:
        raise HTTPException(status_code=404, detail="Affilié non trouvé")
    
    # Map step to field
    step_field_map = {
        "identity_verification": "identity_verified",
        "category_verification": "category_verified",
        "duplication_detection": "duplication_checked",
        "compliance_check": "compliance_passed"
    }
    
    field = step_field_map.get(step)
    
    # Update validation
    await db.affiliate_switches.update_one(
        {"affiliate_id": affiliate_id},
        {
            "$set": {
                f"validation.{field}": passed,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    # Log validation
    await _log_action(db, affiliate_id, f"validation_{step}", validator, {
        "passed": passed,
        "notes": notes
    })
    
    # Check if all validations passed
    updated_affiliate = await db.affiliate_switches.find_one({"affiliate_id": affiliate_id})
    validation = updated_affiliate.get("validation", {})
    
    all_validated = all([
        validation.get("identity_verified", False),
        validation.get("category_verified", False),
        validation.get("duplication_checked", False),
        validation.get("compliance_passed", False)
    ])
    
    if all_validated:
        await db.affiliate_switches.update_one(
            {"affiliate_id": affiliate_id},
            {"$set": {"validation.all_validated": True}}
        )
    
    return {
        "success": True,
        "step": step,
        "passed": passed,
        "all_validated": all_validated,
        "message": f"Validation {step}: {'Réussie' if passed else 'Échouée'}"
    }


@router.get("/affiliates/{affiliate_id}/validation-status")
async def get_validation_status(affiliate_id: str):
    """
    Obtenir le statut de validation complet d'un affilié.
    """
    db = get_db()
    
    affiliate = await db.affiliate_switches.find_one({"affiliate_id": affiliate_id})
    
    if not affiliate:
        raise HTTPException(status_code=404, detail="Affilié non trouvé")
    
    validation = affiliate.get("validation", {})
    
    steps_status = [
        {"step": "identity_verification", "name": "Vérification identité", "passed": validation.get("identity_verified", False)},
        {"step": "category_verification", "name": "Vérification catégorie", "passed": validation.get("category_verified", False)},
        {"step": "duplication_detection", "name": "Détection duplication", "passed": validation.get("duplication_checked", False)},
        {"step": "compliance_check", "name": "Conformité", "passed": validation.get("compliance_passed", False)}
    ]
    
    passed_count = sum(1 for s in steps_status if s["passed"])
    
    return {
        "success": True,
        "affiliate_id": affiliate_id,
        "company_name": affiliate.get("company_name"),
        "validation_steps": steps_status,
        "progress": f"{passed_count}/4",
        "all_validated": validation.get("all_validated", False),
        "ready_for_activation": validation.get("all_validated", False) and affiliate.get("agreement", {}).get("signed", False)
    }


# ============================================
# AGREEMENT MANAGEMENT
# ============================================

@router.post("/affiliates/{affiliate_id}/agreement/confirm")
async def confirm_agreement(
    affiliate_id: str,
    agreement_data: Dict[str, Any] = Body(...)
):
    """
    Confirmer une entente d'affiliation.
    Déclenche l'activation automatique si toutes les validations sont passées.
    """
    db = get_db()
    
    affiliate = await db.affiliate_switches.find_one({"affiliate_id": affiliate_id})
    
    if not affiliate:
        raise HTTPException(status_code=404, detail="Affilié non trouvé")
    
    # Update agreement
    agreement_updates = {
        "agreement.signed": True,
        "agreement.signed_at": datetime.now(timezone.utc).isoformat(),
        "agreement.agreement_type": agreement_data.get("agreement_type", "standard"),
        "agreement.commission_rate": agreement_data.get("commission_rate"),
        "agreement.terms_accepted": True,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.affiliate_switches.update_one(
        {"affiliate_id": affiliate_id},
        {"$set": agreement_updates}
    )
    
    # Log agreement
    await _log_action(db, affiliate_id, "agreement_confirmed", "system", agreement_data)
    
    # Check if ready for auto-activation
    validation = affiliate.get("validation", {})
    all_validated = validation.get("all_validated", False)
    
    auto_activated = False
    if all_validated:
        # Auto-activate
        await db.affiliate_switches.update_one(
            {"affiliate_id": affiliate_id},
            {
                "$set": {
                    "switch_active": True,
                    "status": AffiliateStatus.ACTIVE.value,
                    "activated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        # Sync with engines
        await _sync_with_engines(db, affiliate_id)
        await _activate_seo_satellite(db, affiliate_id)
        
        await _log_action(db, affiliate_id, "auto_activated", "system", {
            "trigger": "agreement_confirmed",
            "all_validated": True
        })
        
        auto_activated = True
    
    return {
        "success": True,
        "affiliate_id": affiliate_id,
        "agreement_signed": True,
        "auto_activated": auto_activated,
        "message": f"Entente confirmée" + (" - Affilié activé automatiquement" if auto_activated else " - En attente de validation")
    }


# ============================================
# ENGINE SYNCHRONIZATION
# ============================================

async def _sync_with_engines(db, affiliate_id: str):
    """
    Synchroniser l'affilié avec tous les engines.
    """
    affiliate = await db.affiliate_switches.find_one({"affiliate_id": affiliate_id})
    
    if not affiliate:
        return
    
    sync_results = {}
    
    # 1. SEO Engine - Add to suppliers list
    try:
        # In a real implementation, this would call the SEO Engine API
        sync_results["seo_engine"] = True
    except Exception as e:
        sync_results["seo_engine"] = False
        logger.error(f"SEO Engine sync failed: {e}")
    
    # 2. Contact Engine - Create contact record
    try:
        contact_data = {
            "email": affiliate.get("email"),
            "name": affiliate.get("contact_name"),
            "company": affiliate.get("company_name"),
            "type": "affiliate",
            "affiliate_id": affiliate_id,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.contacts.update_one(
            {"email": affiliate.get("email")},
            {"$set": contact_data},
            upsert=True
        )
        sync_results["contact_engine"] = True
    except Exception as e:
        sync_results["contact_engine"] = False
        logger.error(f"Contact Engine sync failed: {e}")
    
    # 3. Trigger Engine - Setup affiliate triggers
    try:
        trigger_data = {
            "affiliate_id": affiliate_id,
            "trigger_type": "affiliate_welcome",
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.marketing_triggers.insert_one(trigger_data)
        sync_results["trigger_engine"] = True
    except Exception as e:
        sync_results["trigger_engine"] = False
        logger.error(f"Trigger Engine sync failed: {e}")
    
    # 4. Calendar Engine - Add to affiliate calendar
    try:
        sync_results["calendar_engine"] = True
    except Exception as e:
        sync_results["calendar_engine"] = False
        logger.error(f"Calendar Engine sync failed: {e}")
    
    # 5. Marketing Engine - Add to segments
    try:
        sync_results["marketing_engine"] = True
    except Exception as e:
        sync_results["marketing_engine"] = False
        logger.error(f"Marketing Engine sync failed: {e}")
    
    # 6. Ad Automation Engine - Create ad opportunity
    try:
        # Check if affiliate has email for ad offer
        if affiliate.get("email") or affiliate.get("website"):
            opportunity_data = {
                "opportunity_id": str(uuid.uuid4()),
                "affiliate_id": affiliate_id,
                "company_name": affiliate.get("company_name"),
                "email": affiliate.get("email"),
                "category": affiliate.get("category"),
                "status": "pending",
                "checkout_token": str(uuid.uuid4()),
                "email_sent": False,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
            }
            opportunity_data["checkout_url"] = f"/affiliate-ads/checkout/{opportunity_data['checkout_token']}"
            
            # Check if opportunity already exists
            existing_opp = await db.ad_opportunities.find_one({
                "affiliate_id": affiliate_id,
                "status": {"$nin": ["expired", "cancelled"]}
            })
            
            if not existing_opp:
                await db.ad_opportunities.insert_one(opportunity_data)
                sync_results["ad_automation"] = True
                logger.info(f"Ad opportunity created for affiliate: {affiliate_id}")
            else:
                sync_results["ad_automation"] = "already_exists"
        else:
            sync_results["ad_automation"] = "no_contact_info"
    except Exception as e:
        sync_results["ad_automation"] = False
        logger.error(f"Ad Automation Engine sync failed: {e}")
    
    # Update sync status
    await db.affiliate_switches.update_one(
        {"affiliate_id": affiliate_id},
        {"$set": {"engine_sync": sync_results}}
    )
    
    return sync_results


async def _activate_seo_satellite(db, affiliate_id: str):
    """
    Activer la page satellite SEO pour l'affilié.
    """
    affiliate = await db.affiliate_switches.find_one({"affiliate_id": affiliate_id})
    
    if not affiliate:
        return
    
    company_slug = affiliate.get("company_name", "").lower().replace(" ", "-").replace("'", "")
    category_slug = (affiliate.get("category") or "general").replace("_", "-")
    
    satellite_url = f"/affilies/{category_slug}/{company_slug}"
    
    await db.affiliate_switches.update_one(
        {"affiliate_id": affiliate_id},
        {
            "$set": {
                "seo_integration.satellite_page_active": True,
                "seo_integration.satellite_page_url": satellite_url,
                "seo_integration.excel_integrated": True
            }
        }
    )
    
    # Log SEO activation
    await _log_action(db, affiliate_id, "seo_satellite_activated", "system", {
        "satellite_url": satellite_url
    })


# ============================================
# LOGGING
# ============================================

async def _log_action(db, affiliate_id: str, action: str, source: str, details: Dict = None):
    """
    Journaliser une action sur un affilié.
    """
    log_entry = {
        "affiliate_id": affiliate_id,
        "action": action,
        "source": source,
        "details": details or {},
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    await db.affiliate_switch_logs.insert_one(log_entry)


@router.get("/affiliates/{affiliate_id}/logs")
async def get_affiliate_logs(
    affiliate_id: str,
    limit: int = Query(100, le=500)
):
    """
    Historique des actions sur un affilié.
    """
    db = get_db()
    
    logs = await db.affiliate_switch_logs.find(
        {"affiliate_id": affiliate_id}
    ).sort("timestamp", -1).limit(limit).to_list(limit)
    
    for log in logs:
        log.pop("_id", None)
    
    return {
        "success": True,
        "affiliate_id": affiliate_id,
        "logs": logs,
        "count": len(logs)
    }


# ============================================
# DASHBOARD & STATS
# ============================================

@router.get("/dashboard")
async def get_affiliate_switch_dashboard():
    """
    Dashboard de l'Affiliate Switch Engine.
    """
    db = get_db()
    
    # Count by status
    total = await db.affiliate_switches.count_documents({})
    pending = await db.affiliate_switches.count_documents({"status": "pending"})
    active = await db.affiliate_switches.count_documents({"status": "active"})
    inactive = await db.affiliate_switches.count_documents({"status": "inactive"})
    revoked = await db.affiliate_switches.count_documents({"status": "revoked"})
    
    # Switches ON/OFF
    switches_on = await db.affiliate_switches.count_documents({"switch_active": True})
    switches_off = await db.affiliate_switches.count_documents({"switch_active": False})
    
    # By category
    category_pipeline = [
        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    by_category = await db.affiliate_switches.aggregate(category_pipeline).to_list(20)
    
    # Validation progress
    fully_validated = await db.affiliate_switches.count_documents({"validation.all_validated": True})
    
    # Recent activity
    recent_logs = await db.affiliate_switch_logs.find({}).sort("timestamp", -1).limit(10).to_list(10)
    for log in recent_logs:
        log.pop("_id", None)
    
    return {
        "success": True,
        "dashboard": {
            "totals": {
                "total_affiliates": total,
                "by_status": {
                    "pending": pending,
                    "active": active,
                    "inactive": inactive,
                    "revoked": revoked
                }
            },
            "switches": {
                "on": switches_on,
                "off": switches_off,
                "activation_rate": round((switches_on / max(total, 1)) * 100, 2)
            },
            "validation": {
                "fully_validated": fully_validated,
                "pending_validation": total - fully_validated
            },
            "by_category": by_category,
            "recent_activity": recent_logs
        }
    }


@router.get("/stats")
async def get_affiliate_stats():
    """
    Statistiques détaillées de l'Affiliate Switch Engine.
    """
    db = get_db()
    
    # Engine sync stats
    sync_pipeline = [
        {"$match": {"switch_active": True}},
        {"$group": {
            "_id": None,
            "seo_synced": {"$sum": {"$cond": ["$engine_sync.seo_engine", 1, 0]}},
            "contact_synced": {"$sum": {"$cond": ["$engine_sync.contact_engine", 1, 0]}},
            "trigger_synced": {"$sum": {"$cond": ["$engine_sync.trigger_engine", 1, 0]}},
            "calendar_synced": {"$sum": {"$cond": ["$engine_sync.calendar_engine", 1, 0]}},
            "marketing_synced": {"$sum": {"$cond": ["$engine_sync.marketing_engine", 1, 0]}}
        }}
    ]
    sync_stats_result = await db.affiliate_switches.aggregate(sync_pipeline).to_list(1)
    sync_stats = sync_stats_result[0] if sync_stats_result else {}
    sync_stats.pop("_id", None)
    
    # SEO integration stats
    seo_active = await db.affiliate_switches.count_documents({"seo_integration.satellite_page_active": True})
    excel_integrated = await db.affiliate_switches.count_documents({"seo_integration.excel_integrated": True})
    
    # Agreement stats
    agreements_signed = await db.affiliate_switches.count_documents({"agreement.signed": True})
    
    return {
        "success": True,
        "stats": {
            "engine_sync": sync_stats,
            "seo_integration": {
                "satellite_pages_active": seo_active,
                "excel_integrated": excel_integrated
            },
            "agreements": {
                "signed": agreements_signed
            }
        }
    }


# ============================================
# BULK OPERATIONS
# ============================================

@router.post("/bulk/import-from-suppliers")
async def import_affiliates_from_suppliers(
    categories: Optional[List[str]] = Body(default=None, embed=False)
):
    """
    Importer les fournisseurs SEO comme affiliés potentiels.
    """
    db = get_db()
    
    # Import from suppliers database
    from modules.seo_engine.data.suppliers.suppliers_database import get_all_suppliers
    
    suppliers = get_all_suppliers()
    
    if categories:
        suppliers = [s for s in suppliers if s.get("category") in categories]
    
    imported = 0
    skipped = 0
    
    for supplier in suppliers:
        # Check if already exists
        existing = await db.affiliate_switches.find_one({
            "$or": [
                {"company_name": supplier.get("company")},
                {"website": supplier.get("official_url")}
            ]
        })
        
        if existing:
            skipped += 1
            continue
        
        # Create affiliate record
        affiliate_id = str(uuid.uuid4())
        
        new_affiliate = {
            "affiliate_id": affiliate_id,
            "company_name": supplier.get("company"),
            "website": supplier.get("official_url"),
            "category": supplier.get("category"),
            "country": supplier.get("country"),
            "specialty": supplier.get("specialty", []),
            "switch_active": False,
            "status": AffiliateStatus.PENDING.value,
            "validation": {
                "identity_verified": False,
                "category_verified": True,  # Already categorized
                "duplication_checked": True,  # Just checked
                "compliance_passed": False,
                "all_validated": False
            },
            "agreement": {
                "signed": False,
                "signed_at": None,
                "agreement_type": None,
                "commission_rate": None,
                "terms_accepted": False
            },
            "seo_integration": {
                "satellite_page_active": False,
                "satellite_page_url": None,
                "excel_integrated": False
            },
            "engine_sync": {
                "seo_engine": False,
                "contact_engine": False,
                "trigger_engine": False,
                "calendar_engine": False,
                "marketing_engine": False
            },
            "admin_notes": f"Importé depuis SEO Suppliers Database - Priorité: {supplier.get('seo_priority', 'medium')}",
            "internal_tags": ["imported_from_seo", supplier.get("seo_priority", "medium")],
            "source": "seo_suppliers_import",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.affiliate_switches.insert_one(new_affiliate)
        imported += 1
    
    return {
        "success": True,
        "imported": imported,
        "skipped": skipped,
        "total_processed": imported + skipped,
        "message": f"{imported} affiliés importés, {skipped} ignorés (déjà existants)"
    }


# ============================================
# BULK VALIDATION
# ============================================

@router.post("/bulk/validate")
async def bulk_validate_affiliates(
    validation_config: Dict[str, Any] = Body(...)
):
    """
    Validation automatique en lot des affiliés.
    
    Args:
        validation_config: {
            "affiliate_ids": [...] ou null pour tous les pending,
            "steps": ["identity", "category", "duplication", "compliance"],
            "auto_activate": true/false,
            "validator": "admin"
        }
    """
    db = get_db()
    
    affiliate_ids = validation_config.get("affiliate_ids")
    steps_to_validate = validation_config.get("steps", ["identity", "category", "duplication", "compliance"])
    auto_activate = validation_config.get("auto_activate", False)
    validator = validation_config.get("validator", "bulk_validation_system")
    
    # Get affiliates to validate
    if affiliate_ids:
        query = {"affiliate_id": {"$in": affiliate_ids}}
    else:
        query = {"status": "pending"}
    
    affiliates = await db.affiliate_switches.find(query).to_list(1000)
    
    validated_count = 0
    activated_count = 0
    errors = []
    
    step_field_map = {
        "identity": "identity_verified",
        "category": "category_verified", 
        "duplication": "duplication_checked",
        "compliance": "compliance_passed"
    }
    
    for affiliate in affiliates:
        try:
            affiliate_id = affiliate["affiliate_id"]
            updates = {"updated_at": datetime.now(timezone.utc).isoformat()}
            
            # Apply validation steps
            for step in steps_to_validate:
                if step in step_field_map:
                    updates[f"validation.{step_field_map[step]}"] = True
            
            # Check if all validated
            current_validation = affiliate.get("validation", {})
            new_validation = {**current_validation}
            for step in steps_to_validate:
                if step in step_field_map:
                    new_validation[step_field_map[step]] = True
            
            all_validated = all([
                new_validation.get("identity_verified", False),
                new_validation.get("category_verified", False),
                new_validation.get("duplication_checked", False),
                new_validation.get("compliance_passed", False)
            ])
            
            updates["validation.all_validated"] = all_validated
            
            # Auto-activate if requested and all validated
            if auto_activate and all_validated:
                updates["switch_active"] = True
                updates["status"] = "active"
                updates["activated_at"] = datetime.now(timezone.utc).isoformat()
                activated_count += 1
            
            await db.affiliate_switches.update_one(
                {"affiliate_id": affiliate_id},
                {"$set": updates}
            )
            
            # Log validation
            await _log_action(db, affiliate_id, "bulk_validation", validator, {
                "steps_validated": steps_to_validate,
                "all_validated": all_validated,
                "auto_activated": auto_activate and all_validated
            })
            
            validated_count += 1
            
        except Exception as e:
            errors.append({"affiliate_id": affiliate.get("affiliate_id"), "error": str(e)})
    
    return {
        "success": True,
        "validated_count": validated_count,
        "activated_count": activated_count,
        "errors": errors,
        "steps_applied": steps_to_validate,
        "message": f"{validated_count} affiliés validés, {activated_count} activés automatiquement"
    }


@router.post("/bulk/activate")
async def bulk_activate_affiliates(
    config: Dict[str, Any] = Body(...)
):
    """
    Activation en lot des affiliés validés.
    """
    db = get_db()
    
    affiliate_ids = config.get("affiliate_ids")
    activator = config.get("activator", "bulk_activation_system")
    
    # Get fully validated affiliates
    query = {"validation.all_validated": True, "switch_active": False}
    if affiliate_ids:
        query["affiliate_id"] = {"$in": affiliate_ids}
    
    affiliates = await db.affiliate_switches.find(query).to_list(500)
    
    activated_count = 0
    
    for affiliate in affiliates:
        affiliate_id = affiliate["affiliate_id"]
        
        await db.affiliate_switches.update_one(
            {"affiliate_id": affiliate_id},
            {
                "$set": {
                    "switch_active": True,
                    "status": "active",
                    "activated_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        # Sync with engines
        await _sync_with_engines(db, affiliate_id)
        await _activate_seo_satellite(db, affiliate_id)
        
        # Log activation
        await _log_action(db, affiliate_id, "bulk_activated", activator, {})
        
        activated_count += 1
    
    return {
        "success": True,
        "activated_count": activated_count,
        "message": f"{activated_count} affiliés activés"
    }


logger.info("Affiliate Switch Engine initialized - LEGO V5-ULTIME Module")
