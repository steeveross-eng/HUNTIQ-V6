"""
BIONIC Ad Spaces Engine - COMMANDE 4
====================================

Système complet de gestion des espaces publicitaires:
- Définition des emplacements
- Ad Slot Manager (attribution, réservations, priorités)
- Ad Render Engine (injection, rotation, tracking)
- Intégration avec Affiliate Ad Automation Engine
- Respect du Master Switch Publicitaire

Architecture LEGO V5-ULTIME - Module isolé.
"""

from fastapi import APIRouter, Body, HTTPException
from typing import Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from enum import Enum
import os
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ad-spaces", tags=["Ad Spaces Engine"])

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

class SpaceStatus(str, Enum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    ACTIVE = "active"
    EXPIRED = "expired"
    MAINTENANCE = "maintenance"


class SpaceCategory(str, Enum):
    BANNER = "banner"
    SIDEBAR = "sidebar"
    NATIVE = "native"
    CAROUSEL = "carousel"
    FEATURED = "featured"
    INLINE = "inline"


class SpacePriority(str, Enum):
    PREMIUM = "premium"
    STANDARD = "standard"
    BASIC = "basic"


# ============================================
# AD SPACES DEFINITIONS
# ============================================

AD_SPACES_CATALOG = {
    # HEADER BANNERS
    "header_banner_main": {
        "name": "Header Banner Principal",
        "category": SpaceCategory.BANNER.value,
        "location": "header",
        "position": "top",
        "size": "1200x90",
        "priority": SpacePriority.PREMIUM.value,
        "base_price_multiplier": 2.5,
        "max_concurrent": 1,
        "rotation_enabled": False,
        "pages": ["homepage", "all"],
        "description": "Bannière premium en haut de toutes les pages"
    },
    "header_banner_category": {
        "name": "Header Banner Catégorie",
        "category": SpaceCategory.BANNER.value,
        "location": "header",
        "position": "top",
        "size": "1200x90",
        "priority": SpacePriority.STANDARD.value,
        "base_price_multiplier": 1.8,
        "max_concurrent": 1,
        "rotation_enabled": True,
        "pages": ["category"],
        "description": "Bannière en haut des pages catégories"
    },
    
    # FOOTER BANNERS
    "footer_banner_main": {
        "name": "Footer Banner Principal",
        "category": SpaceCategory.BANNER.value,
        "location": "footer",
        "position": "bottom",
        "size": "1200x90",
        "priority": SpacePriority.BASIC.value,
        "base_price_multiplier": 0.8,
        "max_concurrent": 1,
        "rotation_enabled": True,
        "pages": ["all"],
        "description": "Bannière en bas de toutes les pages"
    },
    
    # SIDEBARS
    "sidebar_top": {
        "name": "Sidebar Top",
        "category": SpaceCategory.SIDEBAR.value,
        "location": "sidebar_right",
        "position": "top",
        "size": "300x250",
        "priority": SpacePriority.PREMIUM.value,
        "base_price_multiplier": 2.0,
        "max_concurrent": 1,
        "rotation_enabled": False,
        "pages": ["all"],
        "description": "Emplacement premium en haut de la sidebar"
    },
    "sidebar_mid": {
        "name": "Sidebar Mid",
        "category": SpaceCategory.SIDEBAR.value,
        "location": "sidebar_right",
        "position": "middle",
        "size": "300x250",
        "priority": SpacePriority.STANDARD.value,
        "base_price_multiplier": 1.5,
        "max_concurrent": 2,
        "rotation_enabled": True,
        "pages": ["all"],
        "description": "Emplacement au milieu de la sidebar"
    },
    "sidebar_bottom": {
        "name": "Sidebar Bottom",
        "category": SpaceCategory.SIDEBAR.value,
        "location": "sidebar_right",
        "position": "bottom",
        "size": "300x600",
        "priority": SpacePriority.STANDARD.value,
        "base_price_multiplier": 1.2,
        "max_concurrent": 1,
        "rotation_enabled": True,
        "pages": ["all"],
        "description": "Emplacement skyscraper en bas de la sidebar"
    },
    
    # NATIVE AD BLOCKS
    "native_article_inline": {
        "name": "Native Article Inline",
        "category": SpaceCategory.NATIVE.value,
        "location": "content",
        "position": "inline",
        "size": "flexible",
        "priority": SpacePriority.STANDARD.value,
        "base_price_multiplier": 1.3,
        "max_concurrent": 3,
        "rotation_enabled": True,
        "pages": ["article", "guide"],
        "description": "Publicité native intégrée dans les articles"
    },
    "native_feed_card": {
        "name": "Native Feed Card",
        "category": SpaceCategory.NATIVE.value,
        "location": "feed",
        "position": "inline",
        "size": "card",
        "priority": SpacePriority.STANDARD.value,
        "base_price_multiplier": 1.4,
        "max_concurrent": 5,
        "rotation_enabled": True,
        "pages": ["feed", "search_results"],
        "description": "Carte native dans les flux de contenu"
    },
    
    # CAROUSELS SPONSORISÉS
    "carousel_featured_products": {
        "name": "Carousel Produits Vedettes",
        "category": SpaceCategory.CAROUSEL.value,
        "location": "content",
        "position": "featured",
        "size": "carousel_4",
        "priority": SpacePriority.PREMIUM.value,
        "base_price_multiplier": 2.2,
        "max_concurrent": 4,
        "rotation_enabled": True,
        "pages": ["homepage", "category"],
        "description": "Carrousel de produits sponsorisés"
    },
    "carousel_supplier_spotlight": {
        "name": "Carousel Fournisseurs en Vedette",
        "category": SpaceCategory.CAROUSEL.value,
        "location": "content",
        "position": "spotlight",
        "size": "carousel_6",
        "priority": SpacePriority.PREMIUM.value,
        "base_price_multiplier": 2.0,
        "max_concurrent": 6,
        "rotation_enabled": True,
        "pages": ["homepage", "suppliers"],
        "description": "Carrousel de fournisseurs partenaires"
    },
    
    # FEATURED PARTNER BLOCKS
    "featured_partner_homepage": {
        "name": "Partenaire Vedette Homepage",
        "category": SpaceCategory.FEATURED.value,
        "location": "homepage",
        "position": "featured_section",
        "size": "600x400",
        "priority": SpacePriority.PREMIUM.value,
        "base_price_multiplier": 3.0,
        "max_concurrent": 1,
        "rotation_enabled": False,
        "pages": ["homepage"],
        "description": "Bloc partenaire vedette sur la page d'accueil"
    },
    "featured_partner_category": {
        "name": "Partenaire Vedette Catégorie",
        "category": SpaceCategory.FEATURED.value,
        "location": "category_page",
        "position": "top",
        "size": "400x300",
        "priority": SpacePriority.PREMIUM.value,
        "base_price_multiplier": 2.5,
        "max_concurrent": 1,
        "rotation_enabled": True,
        "pages": ["category"],
        "description": "Bloc partenaire vedette par catégorie"
    },
    
    # RECOMMENDED GEAR BLOCKS
    "recommended_gear_article": {
        "name": "Équipement Recommandé Article",
        "category": SpaceCategory.INLINE.value,
        "location": "article",
        "position": "recommendations",
        "size": "flexible",
        "priority": SpacePriority.STANDARD.value,
        "base_price_multiplier": 1.6,
        "max_concurrent": 4,
        "rotation_enabled": True,
        "pages": ["article", "guide"],
        "description": "Bloc équipements recommandés dans les articles"
    },
    "recommended_gear_checkout": {
        "name": "Équipement Recommandé Checkout",
        "category": SpaceCategory.INLINE.value,
        "location": "checkout",
        "position": "upsell",
        "size": "flexible",
        "priority": SpacePriority.PREMIUM.value,
        "base_price_multiplier": 2.8,
        "max_concurrent": 3,
        "rotation_enabled": True,
        "pages": ["checkout", "cart"],
        "description": "Bloc équipements pour upsell au checkout"
    },
    
    # TOP SUPPLIER BLOCKS
    "top_suppliers_homepage": {
        "name": "Top Fournisseurs Homepage",
        "category": SpaceCategory.FEATURED.value,
        "location": "homepage",
        "position": "suppliers_section",
        "size": "grid_8",
        "priority": SpacePriority.PREMIUM.value,
        "base_price_multiplier": 2.0,
        "max_concurrent": 8,
        "rotation_enabled": True,
        "pages": ["homepage"],
        "description": "Grille des top fournisseurs sur homepage"
    },
    "top_suppliers_category": {
        "name": "Top Fournisseurs Catégorie",
        "category": SpaceCategory.FEATURED.value,
        "location": "category_page",
        "position": "suppliers_section",
        "size": "grid_4",
        "priority": SpacePriority.STANDARD.value,
        "base_price_multiplier": 1.5,
        "max_concurrent": 4,
        "rotation_enabled": True,
        "pages": ["category"],
        "description": "Grille des top fournisseurs par catégorie"
    },
    
    # MAP OVERLAY
    "map_overlay_sponsored": {
        "name": "Map Overlay Sponsorisé",
        "category": SpaceCategory.FEATURED.value,
        "location": "map",
        "position": "overlay",
        "size": "300x200",
        "priority": SpacePriority.PREMIUM.value,
        "base_price_multiplier": 3.5,
        "max_concurrent": 1,
        "rotation_enabled": False,
        "pages": ["map", "territory"],
        "description": "Overlay sponsorisé sur la carte interactive"
    },
    
    # SEARCH RESULTS
    "search_sponsored_top": {
        "name": "Résultat Sponsorisé Top",
        "category": SpaceCategory.NATIVE.value,
        "location": "search_results",
        "position": "top",
        "size": "flexible",
        "priority": SpacePriority.PREMIUM.value,
        "base_price_multiplier": 2.5,
        "max_concurrent": 2,
        "rotation_enabled": True,
        "pages": ["search"],
        "description": "Résultats sponsorisés en haut des recherches"
    }
}


# ============================================
# MODULE INFO
# ============================================

@router.get("/")
async def get_module_info():
    """Information sur l'Ad Spaces Engine"""
    return {
        "module": "ad_spaces_engine",
        "version": "1.0.0",
        "description": "Système complet de gestion des espaces publicitaires BIONIC",
        "architecture": "LEGO_V5_ULTIME",
        "features": [
            "Définition des emplacements publicitaires",
            "Ad Slot Manager (attribution, réservations, priorités)",
            "Ad Render Engine (injection, rotation, tracking)",
            "Intégration Affiliate Ad Automation",
            "Respect Master Switch Publicitaire"
        ],
        "total_spaces": len(AD_SPACES_CATALOG),
        "categories": [c.value for c in SpaceCategory],
        "priorities": [p.value for p in SpacePriority]
    }


# ============================================
# AD SPACES CATALOG
# ============================================

@router.get("/catalog")
async def get_spaces_catalog():
    """
    Liste complète du catalogue d'espaces publicitaires.
    """
    spaces = []
    for space_id, space_data in AD_SPACES_CATALOG.items():
        spaces.append({
            "space_id": space_id,
            **space_data
        })
    
    return {
        "success": True,
        "catalog": spaces,
        "total": len(spaces),
        "categories": {
            cat.value: len([s for s in AD_SPACES_CATALOG.values() if s["category"] == cat.value])
            for cat in SpaceCategory
        }
    }


@router.get("/catalog/{space_id}")
async def get_space_details(space_id: str):
    """
    Détails d'un espace publicitaire spécifique.
    """
    if space_id not in AD_SPACES_CATALOG:
        raise HTTPException(status_code=404, detail="Espace publicitaire non trouvé")
    
    space = AD_SPACES_CATALOG[space_id]
    db = get_db()
    
    # Get current reservations
    reservations = await db.ad_slot_reservations.find({
        "space_id": space_id,
        "status": {"$in": ["reserved", "active"]}
    }).to_list(10)
    
    for r in reservations:
        r.pop("_id", None)
    
    available_slots = space["max_concurrent"] - len([r for r in reservations if r.get("status") == "active"])
    
    return {
        "success": True,
        "space": {
            "space_id": space_id,
            **space,
            "current_reservations": len(reservations),
            "available_slots": max(0, available_slots),
            "reservations": reservations
        }
    }


@router.get("/catalog/by-category/{category}")
async def get_spaces_by_category(category: str):
    """
    Liste des espaces par catégorie.
    """
    spaces = [
        {"space_id": sid, **sdata}
        for sid, sdata in AD_SPACES_CATALOG.items()
        if sdata["category"] == category
    ]
    
    return {
        "success": True,
        "category": category,
        "spaces": spaces,
        "count": len(spaces)
    }


@router.get("/catalog/by-page/{page}")
async def get_spaces_by_page(page: str):
    """
    Liste des espaces disponibles sur une page spécifique.
    """
    spaces = []
    for sid, sdata in AD_SPACES_CATALOG.items():
        if page in sdata["pages"] or "all" in sdata["pages"]:
            spaces.append({"space_id": sid, **sdata})
    
    return {
        "success": True,
        "page": page,
        "spaces": spaces,
        "count": len(spaces)
    }


# ============================================
# AD SLOT MANAGER
# ============================================

@router.post("/slots/reserve")
async def reserve_ad_slot(
    reservation_data: Dict[str, Any] = Body(...)
):
    """
    Réserver un emplacement publicitaire.
    """
    db = get_db()
    
    space_id = reservation_data.get("space_id")
    affiliate_id = reservation_data.get("affiliate_id")
    opportunity_id = reservation_data.get("opportunity_id")
    duration_days = reservation_data.get("duration_days", 30)
    
    if space_id not in AD_SPACES_CATALOG:
        raise HTTPException(status_code=404, detail="Espace publicitaire non trouvé")
    
    space = AD_SPACES_CATALOG[space_id]
    
    # Check availability
    active_reservations = await db.ad_slot_reservations.count_documents({
        "space_id": space_id,
        "status": {"$in": ["reserved", "active"]}
    })
    
    if active_reservations >= space["max_concurrent"]:
        # Check if rotation is enabled
        if not space["rotation_enabled"]:
            return {
                "success": False,
                "error": "Aucun slot disponible pour cet emplacement",
                "max_concurrent": space["max_concurrent"],
                "current_active": active_reservations
            }
    
    # Create reservation
    reservation_id = str(uuid.uuid4())
    start_date = datetime.now(timezone.utc)
    end_date = start_date + timedelta(days=duration_days)
    
    reservation = {
        "reservation_id": reservation_id,
        "space_id": space_id,
        "affiliate_id": affiliate_id,
        "opportunity_id": opportunity_id,
        "status": SpaceStatus.RESERVED.value,
        "priority": space["priority"],
        "duration_days": duration_days,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "price_multiplier": space["base_price_multiplier"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.ad_slot_reservations.insert_one(reservation)
    
    # Log action
    await _log_space_action(db, space_id, "slot_reserved", "system", {
        "reservation_id": reservation_id,
        "affiliate_id": affiliate_id
    })
    
    reservation.pop("_id", None)
    
    return {
        "success": True,
        "reservation": reservation,
        "space": space,
        "message": f"Slot réservé: {space['name']}"
    }


@router.post("/slots/{reservation_id}/activate")
async def activate_slot(reservation_id: str):
    """
    Activer une réservation après paiement.
    """
    db = get_db()
    
    # Check master switch
    master_switch = await db.ad_master_switch.find_one({"switch_id": "global"})
    if not master_switch or not master_switch.get("is_active"):
        return {
            "success": False,
            "error": "Master Switch Publicitaire désactivé - Mode pré-production",
            "mode": "PRE_PRODUCTION"
        }
    
    reservation = await db.ad_slot_reservations.find_one({"reservation_id": reservation_id})
    
    if not reservation:
        raise HTTPException(status_code=404, detail="Réservation non trouvée")
    
    await db.ad_slot_reservations.update_one(
        {"reservation_id": reservation_id},
        {
            "$set": {
                "status": SpaceStatus.ACTIVE.value,
                "activated_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    await _log_space_action(db, reservation["space_id"], "slot_activated", "system", {
        "reservation_id": reservation_id
    })
    
    return {
        "success": True,
        "reservation_id": reservation_id,
        "status": "active",
        "message": "Slot activé avec succès"
    }


@router.post("/slots/{reservation_id}/deactivate")
async def deactivate_slot(
    reservation_id: str,
    reason: str = Body("Désactivation manuelle", embed=True)
):
    """
    Désactiver un slot actif.
    """
    db = get_db()
    
    reservation = await db.ad_slot_reservations.find_one({"reservation_id": reservation_id})
    
    if not reservation:
        raise HTTPException(status_code=404, detail="Réservation non trouvée")
    
    await db.ad_slot_reservations.update_one(
        {"reservation_id": reservation_id},
        {
            "$set": {
                "status": SpaceStatus.EXPIRED.value,
                "deactivated_at": datetime.now(timezone.utc).isoformat(),
                "deactivation_reason": reason,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    await _log_space_action(db, reservation["space_id"], "slot_deactivated", "admin", {
        "reservation_id": reservation_id,
        "reason": reason
    })
    
    return {
        "success": True,
        "reservation_id": reservation_id,
        "status": "expired",
        "message": "Slot désactivé"
    }


@router.get("/slots/active")
async def get_active_slots():
    """
    Liste tous les slots actifs.
    """
    db = get_db()
    
    # Check master switch
    master_switch = await db.ad_master_switch.find_one({"switch_id": "global"})
    is_production = master_switch and master_switch.get("is_active")
    
    slots = await db.ad_slot_reservations.find({
        "status": SpaceStatus.ACTIVE.value
    }).to_list(100)
    
    for slot in slots:
        slot.pop("_id", None)
        slot["space_info"] = AD_SPACES_CATALOG.get(slot["space_id"], {})
    
    return {
        "success": True,
        "mode": "PRODUCTION" if is_production else "PRE_PRODUCTION",
        "active_slots": slots,
        "count": len(slots),
        "ads_will_render": is_production
    }


@router.get("/slots/by-space/{space_id}")
async def get_slots_by_space(space_id: str):
    """
    Liste les réservations pour un espace spécifique.
    """
    db = get_db()
    
    slots = await db.ad_slot_reservations.find({
        "space_id": space_id
    }).sort("created_at", -1).to_list(50)
    
    for slot in slots:
        slot.pop("_id", None)
    
    return {
        "success": True,
        "space_id": space_id,
        "reservations": slots,
        "count": len(slots)
    }


@router.get("/slots/conflicts")
async def check_slot_conflicts():
    """
    Vérifier les conflits d'emplacements.
    """
    db = get_db()
    
    conflicts = []
    
    for space_id, space_data in AD_SPACES_CATALOG.items():
        active_count = await db.ad_slot_reservations.count_documents({
            "space_id": space_id,
            "status": SpaceStatus.ACTIVE.value
        })
        
        if active_count > space_data["max_concurrent"]:
            conflicts.append({
                "space_id": space_id,
                "space_name": space_data["name"],
                "max_concurrent": space_data["max_concurrent"],
                "current_active": active_count,
                "overflow": active_count - space_data["max_concurrent"]
            })
    
    return {
        "success": True,
        "has_conflicts": len(conflicts) > 0,
        "conflicts": conflicts,
        "total_conflicts": len(conflicts)
    }


# ============================================
# AD RENDER ENGINE
# ============================================

@router.get("/render/{space_id}")
async def render_ad_for_space(
    space_id: str,
    page: Optional[str] = None
):
    """
    Obtenir la publicité à afficher pour un espace donné.
    Utilisé par le frontend BIONIC pour injecter les pubs.
    """
    db = get_db()
    
    # Check master switch
    master_switch = await db.ad_master_switch.find_one({"switch_id": "global"})
    if not master_switch or not master_switch.get("is_active"):
        return {
            "success": True,
            "render": False,
            "reason": "System in pre-production mode",
            "ad": None
        }
    
    if space_id not in AD_SPACES_CATALOG:
        raise HTTPException(status_code=404, detail="Espace publicitaire non trouvé")
    
    space = AD_SPACES_CATALOG[space_id]
    now = datetime.now(timezone.utc).isoformat()
    
    # Get active reservations for this space
    reservations = await db.ad_slot_reservations.find({
        "space_id": space_id,
        "status": SpaceStatus.ACTIVE.value,
        "start_date": {"$lte": now},
        "end_date": {"$gte": now}
    }).sort("priority", -1).to_list(space["max_concurrent"])
    
    if not reservations:
        return {
            "success": True,
            "render": False,
            "reason": "No active ads for this space",
            "ad": None
        }
    
    # Handle rotation if enabled
    if space["rotation_enabled"] and len(reservations) > 1:
        import random
        selected = random.choice(reservations)
    else:
        selected = reservations[0]
    
    # Get ad creative from deployed_ads
    deployed_ad = await db.deployed_ads.find_one({
        "opportunity_id": selected.get("opportunity_id"),
        "is_active": True
    })
    
    # Track impression
    if deployed_ad:
        await db.deployed_ads.update_one(
            {"ad_id": deployed_ad["ad_id"]},
            {"$inc": {"impressions": 1}}
        )
        await db.ad_opportunities.update_one(
            {"opportunity_id": selected["opportunity_id"]},
            {"$inc": {"impressions": 1}}
        )
    
    selected.pop("_id", None)
    
    return {
        "success": True,
        "render": True,
        "space": {
            "space_id": space_id,
            "size": space["size"],
            "position": space["position"]
        },
        "ad": {
            "reservation_id": selected["reservation_id"],
            "affiliate_id": selected["affiliate_id"],
            "opportunity_id": selected.get("opportunity_id"),
            "creative": deployed_ad.get("creative") if deployed_ad else None,
            "company_name": deployed_ad.get("company_name") if deployed_ad else None,
            "click_url": f"/affiliate-ads/click/{selected['reservation_id']}"
        }
    }


@router.post("/render/{reservation_id}/click")
async def track_ad_click(reservation_id: str):
    """
    Tracker un clic sur une publicité.
    """
    db = get_db()
    
    reservation = await db.ad_slot_reservations.find_one({"reservation_id": reservation_id})
    
    if not reservation:
        return {"success": False, "error": "Reservation not found"}
    
    # Update deployed ad
    await db.deployed_ads.update_one(
        {"opportunity_id": reservation.get("opportunity_id")},
        {"$inc": {"clicks": 1}}
    )
    
    # Update opportunity
    opp = await db.ad_opportunities.find_one({"opportunity_id": reservation.get("opportunity_id")})
    if opp:
        new_clicks = opp.get("clicks", 0) + 1
        new_impressions = opp.get("impressions", 1)
        new_ctr = round((new_clicks / max(new_impressions, 1)) * 100, 2)
        
        await db.ad_opportunities.update_one(
            {"opportunity_id": reservation["opportunity_id"]},
            {"$inc": {"clicks": 1}, "$set": {"ctr": new_ctr}}
        )
    
    await _log_space_action(db, reservation["space_id"], "ad_click", "visitor", {
        "reservation_id": reservation_id
    })
    
    return {"success": True, "tracked": True}


@router.get("/render/page/{page}")
async def render_all_ads_for_page(page: str):
    """
    Obtenir toutes les publicités à afficher pour une page donnée.
    """
    db = get_db()
    
    # Check master switch
    master_switch = await db.ad_master_switch.find_one({"switch_id": "global"})
    if not master_switch or not master_switch.get("is_active"):
        return {
            "success": True,
            "mode": "PRE_PRODUCTION",
            "render": False,
            "ads": []
        }
    
    # Get all spaces for this page
    page_spaces = [
        sid for sid, sdata in AD_SPACES_CATALOG.items()
        if page in sdata["pages"] or "all" in sdata["pages"]
    ]
    
    ads_to_render = []
    
    for space_id in page_spaces:
        render_result = await render_ad_for_space(space_id, page)
        if render_result.get("render"):
            ads_to_render.append({
                "space_id": space_id,
                "space_info": AD_SPACES_CATALOG[space_id],
                "ad": render_result["ad"]
            })
    
    return {
        "success": True,
        "mode": "PRODUCTION",
        "page": page,
        "render": True,
        "ads": ads_to_render,
        "count": len(ads_to_render)
    }


# ============================================
# INTEGRATION WITH AFFILIATE AD AUTOMATION
# ============================================

@router.post("/integrate/from-opportunity")
async def integrate_from_opportunity(
    opportunity_id: str = Body(..., embed=True)
):
    """
    Créer une réservation de slot à partir d'une opportunité payée.
    """
    db = get_db()
    
    opp = await db.ad_opportunities.find_one({"opportunity_id": opportunity_id})
    
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunité non trouvée")
    
    if opp.get("status") not in ["paid", "active", "paused"]:
        return {
            "success": False,
            "error": f"Opportunité non payée: {opp.get('status')}"
        }
    
    # Map placement to space_id
    placement_to_space = {
        "homepage_banner": "header_banner_main",
        "sidebar_right": "sidebar_mid",
        "category_page": "header_banner_category",
        "article_inline": "native_article_inline",
        "footer_banner": "footer_banner_main",
        "search_results": "search_sponsored_top",
        "map_overlay": "map_overlay_sponsored"
    }
    
    placement = opp.get("selected_placement", "sidebar_right")
    space_id = placement_to_space.get(placement, "sidebar_mid")
    
    # Create reservation
    reservation_data = {
        "space_id": space_id,
        "affiliate_id": opp["affiliate_id"],
        "opportunity_id": opportunity_id,
        "duration_days": opp.get("duration_days", 30)
    }
    
    result = await reserve_ad_slot(reservation_data)
    
    return result


# ============================================
# DASHBOARD & STATS
# ============================================

@router.get("/dashboard")
async def get_ad_spaces_dashboard():
    """
    Dashboard du Ad Spaces Engine.
    """
    db = get_db()
    
    # Master switch status
    master_switch = await db.ad_master_switch.find_one({"switch_id": "global"})
    
    # Count reservations by status
    status_counts = {}
    for status in SpaceStatus:
        count = await db.ad_slot_reservations.count_documents({"status": status.value})
        if count > 0:
            status_counts[status.value] = count
    
    # Count by space
    space_usage = {}
    for space_id in AD_SPACES_CATALOG.keys():
        active = await db.ad_slot_reservations.count_documents({
            "space_id": space_id,
            "status": SpaceStatus.ACTIVE.value
        })
        if active > 0:
            space_usage[space_id] = active
    
    # Total impressions and clicks
    total_impressions = 0
    total_clicks = 0
    opps = await db.ad_opportunities.find({}).to_list(1000)
    for opp in opps:
        total_impressions += opp.get("impressions", 0)
        total_clicks += opp.get("clicks", 0)
    
    return {
        "success": True,
        "dashboard": {
            "master_switch": {
                "is_active": master_switch.get("is_active", False) if master_switch else False,
                "mode": "PRODUCTION" if (master_switch and master_switch.get("is_active")) else "PRE_PRODUCTION"
            },
            "catalog": {
                "total_spaces": len(AD_SPACES_CATALOG),
                "by_category": {
                    cat.value: len([s for s in AD_SPACES_CATALOG.values() if s["category"] == cat.value])
                    for cat in SpaceCategory
                }
            },
            "reservations": {
                "by_status": status_counts,
                "by_space": space_usage
            },
            "performance": {
                "total_impressions": total_impressions,
                "total_clicks": total_clicks,
                "overall_ctr": round((total_clicks / max(total_impressions, 1)) * 100, 2)
            }
        }
    }


# ============================================
# HELPERS
# ============================================

async def _log_space_action(db, space_id: str, action: str, source: str, details: Dict = None):
    """Journaliser une action sur un espace publicitaire"""
    log_entry = {
        "space_id": space_id,
        "action": action,
        "source": source,
        "details": details or {},
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    await db.ad_space_logs.insert_one(log_entry)


logger.info("Ad Spaces Engine initialized - LEGO V5-ULTIME Module")
