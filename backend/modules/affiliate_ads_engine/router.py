"""
BIONIC Affiliate Ad Automation Engine - COMMANDE 3
===================================================

Système 100% automatisé de gestion du cycle de vente publicitaire:
- Trigger automatique à l'activation affilié
- Envoi email offre publicitaire
- Portail Affiliate Ads Checkout
- Déploiement automatisé
- Suivi & renouvellement

Architecture LEGO V5-ULTIME - Module isolé.
"""

from fastapi import APIRouter, Body, Query, HTTPException
from typing import Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from enum import Enum
import os
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/affiliate-ads", tags=["Affiliate Ad Automation Engine"])

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
# ENUMS & MODELS
# ============================================

class AdOpportunityStatus(str, Enum):
    PENDING = "pending"
    EMAIL_SENT = "email_sent"
    CHECKOUT_STARTED = "checkout_started"
    PAYMENT_PENDING = "payment_pending"
    PAID = "paid"
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class AdPackage(str, Enum):
    MONTHLY = "1_month"
    QUARTERLY = "3_months"
    BIANNUAL = "6_months"
    ANNUAL = "12_months"


class AdPlacement(str, Enum):
    HOMEPAGE_BANNER = "homepage_banner"
    SIDEBAR_RIGHT = "sidebar_right"
    CATEGORY_PAGE = "category_page"
    ARTICLE_INLINE = "article_inline"
    FOOTER_BANNER = "footer_banner"
    SEARCH_RESULTS = "search_results"
    MAP_OVERLAY = "map_overlay"


# Pricing structure (paramétrable)
AD_PRICING = {
    AdPackage.MONTHLY.value: {
        "price": 99.00,
        "discount": 0,
        "duration_days": 30
    },
    AdPackage.QUARTERLY.value: {
        "price": 249.00,
        "discount": 15,
        "duration_days": 90
    },
    AdPackage.BIANNUAL.value: {
        "price": 449.00,
        "discount": 25,
        "duration_days": 180
    },
    AdPackage.ANNUAL.value: {
        "price": 799.00,
        "discount": 35,
        "duration_days": 365
    }
}

# Placement pricing multipliers
PLACEMENT_MULTIPLIERS = {
    AdPlacement.HOMEPAGE_BANNER.value: 2.0,
    AdPlacement.SIDEBAR_RIGHT.value: 1.0,
    AdPlacement.CATEGORY_PAGE.value: 1.5,
    AdPlacement.ARTICLE_INLINE.value: 1.2,
    AdPlacement.FOOTER_BANNER.value: 0.8,
    AdPlacement.SEARCH_RESULTS.value: 1.8,
    AdPlacement.MAP_OVERLAY.value: 2.5
}


# ============================================
# PYDANTIC MODELS
# ============================================

class AdCreative(BaseModel):
    type: str = Field(..., description="image, video, text")
    url: Optional[str] = None
    content: Optional[str] = None
    alt_text: Optional[str] = None
    dimensions: Optional[str] = None


class CheckoutRequest(BaseModel):
    opportunity_id: str
    package: str
    placement: str
    creative: Optional[AdCreative] = None
    payment_method: Optional[str] = "stripe"


# ============================================
# MODULE INFO
# ============================================

@router.get("/")
async def get_module_info():
    """Information sur l'Affiliate Ad Automation Engine"""
    return {
        "module": "affiliate_ad_automation_engine",
        "version": "1.0.0",
        "description": "Système 100% automatisé du cycle de vente publicitaire affilié",
        "architecture": "LEGO_V5_ULTIME",
        "features": [
            "Trigger automatique à l'activation affilié",
            "Email automatique offre publicitaire",
            "Portail Affiliate Ads Checkout",
            "Déploiement automatisé pages BIONIC",
            "Suivi impressions/clics/CTR",
            "Renouvellement automatique"
        ],
        "packages": list(AD_PRICING.keys()),
        "placements": [p.value for p in AdPlacement],
        "statuses": [s.value for s in AdOpportunityStatus]
    }


# ============================================
# AD OPPORTUNITIES (TRIGGERED ON ACTIVATION)
# ============================================

@router.post("/opportunities/create")
async def create_ad_opportunity(
    affiliate_id: str = Body(..., embed=True),
    auto_send_email: bool = Body(True, embed=True)
):
    """
    Créer une opportunité publicitaire pour un affilié.
    Déclenché automatiquement quand un affilié passe ACTIVE.
    """
    db = get_db()
    
    # Verify affiliate exists and is active
    affiliate = await db.affiliate_switches.find_one({"affiliate_id": affiliate_id})
    
    if not affiliate:
        raise HTTPException(status_code=404, detail="Affilié non trouvé")
    
    # Check if opportunity already exists
    existing = await db.ad_opportunities.find_one({
        "affiliate_id": affiliate_id,
        "status": {"$nin": ["expired", "cancelled"]}
    })
    
    if existing:
        return {
            "success": False,
            "error": "Une opportunité active existe déjà",
            "existing_opportunity_id": existing.get("opportunity_id")
        }
    
    opportunity_id = str(uuid.uuid4())
    checkout_token = str(uuid.uuid4())
    
    opportunity = {
        "opportunity_id": opportunity_id,
        "affiliate_id": affiliate_id,
        "company_name": affiliate.get("company_name"),
        "email": affiliate.get("email"),
        "category": affiliate.get("category"),
        
        # Status
        "status": AdOpportunityStatus.PENDING.value,
        
        # Checkout
        "checkout_token": checkout_token,
        "checkout_url": f"/affiliate-ads/checkout/{checkout_token}",
        "checkout_started_at": None,
        "checkout_completed_at": None,
        
        # Selected options (filled during checkout)
        "selected_package": None,
        "selected_placement": None,
        "creative": None,
        
        # Pricing (calculated during checkout)
        "base_price": None,
        "discount_percent": None,
        "final_price": None,
        
        # Payment
        "payment_status": "pending",
        "payment_method": None,
        "payment_id": None,
        "paid_at": None,
        
        # Campaign dates
        "campaign_start": None,
        "campaign_end": None,
        "duration_days": None,
        
        # Performance tracking
        "impressions": 0,
        "clicks": 0,
        "ctr": 0.0,
        
        # Email tracking
        "email_sent": False,
        "email_sent_at": None,
        "email_opened": False,
        "email_clicked": False,
        
        # Renewal
        "auto_renew": False,
        "renewal_reminder_sent": False,
        "renewed_from": None,
        
        # Timestamps
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    }
    
    await db.ad_opportunities.insert_one(opportunity)
    
    # Log creation
    await _log_ad_action(db, opportunity_id, "opportunity_created", "system", {
        "affiliate_id": affiliate_id,
        "company_name": affiliate.get("company_name")
    })
    
    # Auto-send email if requested
    email_result = None
    if auto_send_email and affiliate.get("email"):
        email_result = await _send_ad_offer_email(db, opportunity_id)
    
    opportunity.pop("_id", None)
    
    return {
        "success": True,
        "opportunity": opportunity,
        "email_sent": email_result.get("sent") if email_result else False,
        "checkout_url": opportunity["checkout_url"],
        "message": f"Opportunité créée pour {affiliate.get('company_name')}"
    }


@router.get("/opportunities")
async def get_all_opportunities(
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100),
    status: Optional[str] = None,
    affiliate_id: Optional[str] = None
):
    """Liste toutes les opportunités publicitaires"""
    db = get_db()
    
    query = {}
    if status:
        query["status"] = status
    if affiliate_id:
        query["affiliate_id"] = affiliate_id
    
    skip = (page - 1) * limit
    
    opportunities = await db.ad_opportunities.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.ad_opportunities.count_documents(query)
    
    for opp in opportunities:
        opp.pop("_id", None)
    
    return {
        "success": True,
        "opportunities": opportunities,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    }


@router.get("/opportunities/{opportunity_id}")
async def get_opportunity(opportunity_id: str):
    """Détail d'une opportunité"""
    db = get_db()
    
    opp = await db.ad_opportunities.find_one({"opportunity_id": opportunity_id})
    
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunité non trouvée")
    
    opp.pop("_id", None)
    
    # Get logs
    logs = await db.ad_automation_logs.find(
        {"opportunity_id": opportunity_id}
    ).sort("timestamp", -1).limit(50).to_list(50)
    
    for log in logs:
        log.pop("_id", None)
    
    return {
        "success": True,
        "opportunity": opp,
        "logs": logs
    }


# ============================================
# CHECKOUT PORTAL
# ============================================

@router.get("/checkout/{checkout_token}")
async def get_checkout_page(checkout_token: str):
    """
    Page de checkout pour l'affilié.
    Retourne les options disponibles.
    """
    db = get_db()
    
    opp = await db.ad_opportunities.find_one({"checkout_token": checkout_token})
    
    if not opp:
        raise HTTPException(status_code=404, detail="Lien de checkout invalide ou expiré")
    
    # Check expiration
    expires_at = datetime.fromisoformat(opp["expires_at"].replace("Z", "+00:00"))
    if datetime.now(timezone.utc) > expires_at:
        return {
            "success": False,
            "error": "Cette offre a expiré",
            "expired_at": opp["expires_at"]
        }
    
    # Mark checkout started
    if not opp.get("checkout_started_at"):
        await db.ad_opportunities.update_one(
            {"checkout_token": checkout_token},
            {
                "$set": {
                    "checkout_started_at": datetime.now(timezone.utc).isoformat(),
                    "status": AdOpportunityStatus.CHECKOUT_STARTED.value
                }
            }
        )
        await _log_ad_action(db, opp["opportunity_id"], "checkout_started", "affiliate", {})
    
    return {
        "success": True,
        "checkout": {
            "opportunity_id": opp["opportunity_id"],
            "company_name": opp["company_name"],
            "category": opp["category"],
            "status": opp["status"],
            "expires_at": opp["expires_at"]
        },
        "packages": [
            {
                "id": pkg,
                "name": pkg.replace("_", " ").title(),
                "price": info["price"],
                "discount": info["discount"],
                "duration_days": info["duration_days"],
                "description": f"{info['duration_days']} jours de visibilité"
            }
            for pkg, info in AD_PRICING.items()
        ],
        "placements": [
            {
                "id": placement.value,
                "name": placement.value.replace("_", " ").title(),
                "multiplier": PLACEMENT_MULTIPLIERS.get(placement.value, 1.0),
                "description": _get_placement_description(placement.value)
            }
            for placement in AdPlacement
        ]
    }


@router.post("/checkout/{checkout_token}/submit")
async def submit_checkout(
    checkout_token: str,
    checkout_data: Dict[str, Any] = Body(...)
):
    """
    Soumettre le checkout avec les options sélectionnées.
    """
    db = get_db()
    
    opp = await db.ad_opportunities.find_one({"checkout_token": checkout_token})
    
    if not opp:
        raise HTTPException(status_code=404, detail="Lien de checkout invalide")
    
    package = checkout_data.get("package")
    placement = checkout_data.get("placement")
    creative = checkout_data.get("creative")
    auto_renew = checkout_data.get("auto_renew", False)
    
    if not package or not placement:
        raise HTTPException(status_code=400, detail="Package et placement requis")
    
    # Calculate pricing
    package_info = AD_PRICING.get(package)
    if not package_info:
        raise HTTPException(status_code=400, detail="Package invalide")
    
    placement_multiplier = PLACEMENT_MULTIPLIERS.get(placement, 1.0)
    base_price = package_info["price"]
    final_price = base_price * placement_multiplier
    
    # Update opportunity
    updates = {
        "selected_package": package,
        "selected_placement": placement,
        "creative": creative,
        "base_price": base_price,
        "discount_percent": package_info["discount"],
        "final_price": round(final_price, 2),
        "duration_days": package_info["duration_days"],
        "auto_renew": auto_renew,
        "status": AdOpportunityStatus.PAYMENT_PENDING.value,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.ad_opportunities.update_one(
        {"checkout_token": checkout_token},
        {"$set": updates}
    )
    
    await _log_ad_action(db, opp["opportunity_id"], "checkout_submitted", "affiliate", {
        "package": package,
        "placement": placement,
        "final_price": final_price
    })
    
    return {
        "success": True,
        "opportunity_id": opp["opportunity_id"],
        "summary": {
            "package": package,
            "placement": placement,
            "base_price": base_price,
            "placement_multiplier": placement_multiplier,
            "final_price": round(final_price, 2),
            "duration_days": package_info["duration_days"]
        },
        "payment_url": f"/affiliate-ads/pay/{opp['opportunity_id']}",
        "message": "Checkout complété, procédez au paiement"
    }


# ============================================
# PAYMENT PROCESSING
# ============================================

@router.post("/pay/{opportunity_id}")
async def process_payment(
    opportunity_id: str,
    payment_data: Dict[str, Any] = Body(...)
):
    """
    Traiter le paiement d'une opportunité publicitaire.
    Simule une intégration passerelle (Stripe ready).
    """
    db = get_db()
    
    opp = await db.ad_opportunities.find_one({"opportunity_id": opportunity_id})
    
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunité non trouvée")
    
    if opp["status"] not in [AdOpportunityStatus.PAYMENT_PENDING.value, AdOpportunityStatus.CHECKOUT_STARTED.value]:
        return {
            "success": False,
            "error": f"Statut invalide pour paiement: {opp['status']}"
        }
    
    payment_method = payment_data.get("payment_method", "stripe")
    
    # Simulate payment processing
    # In production, integrate with Stripe/PayPal here
    payment_id = f"pay_{uuid.uuid4().hex[:16]}"
    
    # Calculate campaign dates
    campaign_start = datetime.now(timezone.utc)
    campaign_end = campaign_start + timedelta(days=opp["duration_days"])
    
    updates = {
        "status": AdOpportunityStatus.PAID.value,
        "payment_status": "completed",
        "payment_method": payment_method,
        "payment_id": payment_id,
        "paid_at": datetime.now(timezone.utc).isoformat(),
        "checkout_completed_at": datetime.now(timezone.utc).isoformat(),
        "campaign_start": campaign_start.isoformat(),
        "campaign_end": campaign_end.isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.ad_opportunities.update_one(
        {"opportunity_id": opportunity_id},
        {"$set": updates}
    )
    
    await _log_ad_action(db, opportunity_id, "payment_completed", "payment_gateway", {
        "payment_id": payment_id,
        "amount": opp["final_price"],
        "method": payment_method
    })
    
    # Auto-deploy the ad
    deploy_result = await _deploy_ad(db, opportunity_id)
    
    return {
        "success": True,
        "opportunity_id": opportunity_id,
        "payment_id": payment_id,
        "amount": opp["final_price"],
        "campaign": {
            "start": campaign_start.isoformat(),
            "end": campaign_end.isoformat(),
            "duration_days": opp["duration_days"]
        },
        "deployed": deploy_result.get("success", False),
        "message": "Paiement accepté, campagne déployée!"
    }


# ============================================
# AD DEPLOYMENT
# ============================================

async def _deploy_ad(db, opportunity_id: str) -> Dict:
    """
    Déployer automatiquement une publicité dans les pages BIONIC.
    """
    opp = await db.ad_opportunities.find_one({"opportunity_id": opportunity_id})
    
    if not opp:
        return {"success": False, "error": "Opportunité non trouvée"}
    
    # Create deployed ad record
    deployed_ad = {
        "ad_id": str(uuid.uuid4()),
        "opportunity_id": opportunity_id,
        "affiliate_id": opp["affiliate_id"],
        "company_name": opp["company_name"],
        "placement": opp["selected_placement"],
        "creative": opp.get("creative"),
        "is_active": True,
        "campaign_start": opp["campaign_start"],
        "campaign_end": opp["campaign_end"],
        "impressions": 0,
        "clicks": 0,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.deployed_ads.insert_one(deployed_ad)
    
    # Update opportunity status
    await db.ad_opportunities.update_one(
        {"opportunity_id": opportunity_id},
        {"$set": {"status": AdOpportunityStatus.ACTIVE.value}}
    )
    
    # Schedule in Calendar Engine
    await _schedule_in_calendar(db, opp)
    
    # Register in Marketing Engine
    await _register_in_marketing(db, opp)
    
    await _log_ad_action(db, opportunity_id, "ad_deployed", "system", {
        "placement": opp["selected_placement"],
        "ad_id": deployed_ad["ad_id"]
    })
    
    return {
        "success": True,
        "ad_id": deployed_ad["ad_id"],
        "placement": opp["selected_placement"]
    }


async def _schedule_in_calendar(db, opp: Dict):
    """Planifier la campagne dans le Calendar Engine"""
    calendar_event = {
        "event_id": str(uuid.uuid4()),
        "type": "affiliate_ad_campaign",
        "title": f"Pub Affilié: {opp['company_name']}",
        "affiliate_id": opp["affiliate_id"],
        "opportunity_id": opp["opportunity_id"],
        "start_date": opp["campaign_start"],
        "end_date": opp["campaign_end"],
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.marketing_calendar.insert_one(calendar_event)


async def _register_in_marketing(db, opp: Dict):
    """Enregistrer dans le Marketing Engine pour tracking"""
    marketing_record = {
        "record_id": str(uuid.uuid4()),
        "type": "affiliate_ad",
        "affiliate_id": opp["affiliate_id"],
        "opportunity_id": opp["opportunity_id"],
        "company_name": opp["company_name"],
        "placement": opp["selected_placement"],
        "package": opp["selected_package"],
        "revenue": opp["final_price"],
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.marketing_records.insert_one(marketing_record)


# ============================================
# EMAIL AUTOMATION
# ============================================

async def _send_ad_offer_email(db, opportunity_id: str) -> Dict:
    """
    Envoyer l'email d'offre publicitaire.
    """
    opp = await db.ad_opportunities.find_one({"opportunity_id": opportunity_id})
    
    if not opp or not opp.get("email"):
        return {"sent": False, "error": "Email non disponible"}
    
    # In production, integrate with email service (Resend, SendGrid)
    email_content = {
        "to": opp["email"],
        "subject": f"🎯 Offre Publicitaire Exclusive - {opp['company_name']}",
        "body": f"""
        Bonjour,
        
        Félicitations pour votre activation en tant qu'affilié BIONIC!
        
        Nous avons le plaisir de vous proposer une offre publicitaire exclusive:
        
        📊 ESPACES DISPONIBLES:
        - Bannière Homepage (Premium)
        - Sidebar
        - Pages Catégories
        - Articles
        - Résultats de recherche
        - Carte interactive (Premium)
        
        💰 FORFAITS:
        - 1 mois: 99$ (Testez)
        - 3 mois: 249$ (-15%)
        - 6 mois: 449$ (-25%)
        - 12 mois: 799$ (-35%)
        
        👉 Accédez à votre espace de réservation:
        {opp['checkout_url']}
        
        Cette offre expire dans 30 jours.
        
        L'équipe BIONIC
        """,
        "sent_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Update opportunity
    await db.ad_opportunities.update_one(
        {"opportunity_id": opportunity_id},
        {
            "$set": {
                "email_sent": True,
                "email_sent_at": datetime.now(timezone.utc).isoformat(),
                "status": AdOpportunityStatus.EMAIL_SENT.value
            }
        }
    )
    
    await _log_ad_action(db, opportunity_id, "email_sent", "email_system", {
        "to": opp["email"],
        "subject": email_content["subject"]
    })
    
    return {"sent": True, "to": opp["email"]}


@router.post("/opportunities/{opportunity_id}/resend-email")
async def resend_ad_offer_email(opportunity_id: str):
    """Renvoyer l'email d'offre"""
    db = get_db()
    result = await _send_ad_offer_email(db, opportunity_id)
    return {"success": result.get("sent", False), **result}


# ============================================
# PERFORMANCE TRACKING
# ============================================

@router.post("/track/impression")
async def track_impression(
    ad_id: str = Body(..., embed=True)
):
    """Tracker une impression publicitaire"""
    db = get_db()
    
    await db.deployed_ads.update_one(
        {"ad_id": ad_id},
        {"$inc": {"impressions": 1}}
    )
    
    # Also update opportunity
    ad = await db.deployed_ads.find_one({"ad_id": ad_id})
    if ad:
        await db.ad_opportunities.update_one(
            {"opportunity_id": ad["opportunity_id"]},
            {"$inc": {"impressions": 1}}
        )
    
    return {"success": True}


@router.post("/track/click")
async def track_click(
    ad_id: str = Body(..., embed=True)
):
    """Tracker un clic publicitaire"""
    db = get_db()
    
    ad = await db.deployed_ads.find_one({"ad_id": ad_id})
    
    if ad:
        new_clicks = ad.get("clicks", 0) + 1
        new_impressions = ad.get("impressions", 1)
        new_ctr = round((new_clicks / max(new_impressions, 1)) * 100, 2)
        
        await db.deployed_ads.update_one(
            {"ad_id": ad_id},
            {
                "$inc": {"clicks": 1},
                "$set": {"ctr": new_ctr}
            }
        )
        
        await db.ad_opportunities.update_one(
            {"opportunity_id": ad["opportunity_id"]},
            {
                "$inc": {"clicks": 1},
                "$set": {"ctr": new_ctr}
            }
        )
    
    return {"success": True}


@router.get("/performance/{opportunity_id}")
async def get_ad_performance(opportunity_id: str):
    """Obtenir les performances d'une campagne"""
    db = get_db()
    
    opp = await db.ad_opportunities.find_one({"opportunity_id": opportunity_id})
    
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunité non trouvée")
    
    impressions = opp.get("impressions", 0)
    clicks = opp.get("clicks", 0)
    ctr = round((clicks / max(impressions, 1)) * 100, 2)
    
    return {
        "success": True,
        "performance": {
            "opportunity_id": opportunity_id,
            "company_name": opp.get("company_name"),
            "placement": opp.get("selected_placement"),
            "package": opp.get("selected_package"),
            "impressions": impressions,
            "clicks": clicks,
            "ctr": ctr,
            "campaign_start": opp.get("campaign_start"),
            "campaign_end": opp.get("campaign_end"),
            "status": opp.get("status"),
            "revenue": opp.get("final_price")
        }
    }


# ============================================
# RENEWAL SYSTEM
# ============================================

@router.get("/renewals/pending")
async def get_pending_renewals():
    """
    Liste les campagnes expirant dans les 7 prochains jours.
    """
    db = get_db()
    
    now = datetime.now(timezone.utc)
    week_later = now + timedelta(days=7)
    
    expiring = await db.ad_opportunities.find({
        "status": AdOpportunityStatus.ACTIVE.value,
        "campaign_end": {
            "$lte": week_later.isoformat(),
            "$gte": now.isoformat()
        }
    }).to_list(100)
    
    for opp in expiring:
        opp.pop("_id", None)
    
    return {
        "success": True,
        "pending_renewals": expiring,
        "count": len(expiring)
    }


@router.post("/renewals/{opportunity_id}/send-reminder")
async def send_renewal_reminder(opportunity_id: str):
    """Envoyer un rappel de renouvellement"""
    db = get_db()
    
    opp = await db.ad_opportunities.find_one({"opportunity_id": opportunity_id})
    
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunité non trouvée")
    
    # In production, send actual email
    await db.ad_opportunities.update_one(
        {"opportunity_id": opportunity_id},
        {"$set": {"renewal_reminder_sent": True}}
    )
    
    await _log_ad_action(db, opportunity_id, "renewal_reminder_sent", "system", {
        "to": opp.get("email")
    })
    
    return {
        "success": True,
        "message": f"Rappel envoyé à {opp.get('email')}"
    }


@router.post("/renewals/{opportunity_id}/renew")
async def renew_campaign(
    opportunity_id: str,
    renewal_data: Dict[str, Any] = Body(...)
):
    """Renouveler une campagne"""
    db = get_db()
    
    opp = await db.ad_opportunities.find_one({"opportunity_id": opportunity_id})
    
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunité non trouvée")
    
    # Create new opportunity based on old one
    new_package = renewal_data.get("package", opp.get("selected_package"))
    
    new_opportunity_id = str(uuid.uuid4())
    checkout_token = str(uuid.uuid4())
    
    new_opp = {
        "opportunity_id": new_opportunity_id,
        "affiliate_id": opp["affiliate_id"],
        "company_name": opp["company_name"],
        "email": opp.get("email"),
        "category": opp.get("category"),
        "status": AdOpportunityStatus.PAYMENT_PENDING.value,
        "checkout_token": checkout_token,
        "checkout_url": f"/affiliate-ads/checkout/{checkout_token}",
        "selected_package": new_package,
        "selected_placement": opp.get("selected_placement"),
        "creative": opp.get("creative"),
        "auto_renew": opp.get("auto_renew", False),
        "renewed_from": opportunity_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    }
    
    # Calculate pricing
    package_info = AD_PRICING.get(new_package, AD_PRICING[AdPackage.MONTHLY.value])
    placement_multiplier = PLACEMENT_MULTIPLIERS.get(opp.get("selected_placement", "sidebar_right"), 1.0)
    
    new_opp["base_price"] = package_info["price"]
    new_opp["discount_percent"] = package_info["discount"]
    new_opp["final_price"] = round(package_info["price"] * placement_multiplier, 2)
    new_opp["duration_days"] = package_info["duration_days"]
    
    await db.ad_opportunities.insert_one(new_opp)
    
    await _log_ad_action(db, new_opportunity_id, "renewal_created", "system", {
        "renewed_from": opportunity_id,
        "package": new_package
    })
    
    new_opp.pop("_id", None)
    
    return {
        "success": True,
        "new_opportunity": new_opp,
        "payment_url": f"/affiliate-ads/pay/{new_opportunity_id}",
        "message": "Renouvellement créé, procédez au paiement"
    }


# ============================================
# DASHBOARDS
# ============================================

@router.get("/dashboard/affiliate/{affiliate_id}")
async def get_affiliate_dashboard(affiliate_id: str):
    """
    Tableau de bord affilié - impressions, clics, CTR.
    """
    db = get_db()
    
    opportunities = await db.ad_opportunities.find({
        "affiliate_id": affiliate_id
    }).to_list(100)
    
    total_impressions = sum(opp.get("impressions", 0) for opp in opportunities)
    total_clicks = sum(opp.get("clicks", 0) for opp in opportunities)
    total_ctr = round((total_clicks / max(total_impressions, 1)) * 100, 2)
    total_spent = sum(opp.get("final_price", 0) for opp in opportunities if opp.get("payment_status") == "completed")
    
    active_campaigns = [opp for opp in opportunities if opp.get("status") == "active"]
    
    for opp in opportunities:
        opp.pop("_id", None)
    
    return {
        "success": True,
        "dashboard": {
            "affiliate_id": affiliate_id,
            "summary": {
                "total_campaigns": len(opportunities),
                "active_campaigns": len(active_campaigns),
                "total_impressions": total_impressions,
                "total_clicks": total_clicks,
                "overall_ctr": total_ctr,
                "total_spent": round(total_spent, 2)
            },
            "campaigns": opportunities
        }
    }


@router.get("/dashboard/bionic")
async def get_bionic_dashboard():
    """
    Tableau de bord BIONIC - revenus, performances globales.
    """
    db = get_db()
    
    # Get all opportunities
    all_opps = await db.ad_opportunities.find({}).to_list(1000)
    
    # Calculate totals
    total_revenue = sum(opp.get("final_price", 0) for opp in all_opps if opp.get("payment_status") == "completed")
    total_impressions = sum(opp.get("impressions", 0) for opp in all_opps)
    total_clicks = sum(opp.get("clicks", 0) for opp in all_opps)
    
    # Count by status
    by_status = {}
    for opp in all_opps:
        status = opp.get("status", "unknown")
        by_status[status] = by_status.get(status, 0) + 1
    
    # Count by placement
    by_placement = {}
    for opp in all_opps:
        placement = opp.get("selected_placement")
        if placement:
            by_placement[placement] = by_placement.get(placement, 0) + 1
    
    # Revenue by month
    revenue_by_month = {}
    for opp in all_opps:
        if opp.get("paid_at"):
            month = opp["paid_at"][:7]  # YYYY-MM
            revenue_by_month[month] = revenue_by_month.get(month, 0) + opp.get("final_price", 0)
    
    return {
        "success": True,
        "dashboard": {
            "totals": {
                "total_opportunities": len(all_opps),
                "total_revenue": round(total_revenue, 2),
                "total_impressions": total_impressions,
                "total_clicks": total_clicks,
                "overall_ctr": round((total_clicks / max(total_impressions, 1)) * 100, 2)
            },
            "by_status": by_status,
            "by_placement": by_placement,
            "revenue_by_month": revenue_by_month,
            "active_ads_count": by_status.get("active", 0)
        }
    }


# ============================================
# DEPLOYED ADS API (For BIONIC Pages)
# ============================================

@router.get("/deployed")
async def get_deployed_ads(
    placement: Optional[str] = None,
    active_only: bool = True
):
    """
    Liste les publicités déployées pour injection dans les pages BIONIC.
    """
    db = get_db()
    
    query = {}
    if placement:
        query["placement"] = placement
    if active_only:
        query["is_active"] = True
        query["campaign_end"] = {"$gte": datetime.now(timezone.utc).isoformat()}
    
    ads = await db.deployed_ads.find(query).to_list(100)
    
    for ad in ads:
        ad.pop("_id", None)
    
    return {
        "success": True,
        "ads": ads,
        "count": len(ads)
    }


@router.get("/deployed/by-placement/{placement}")
async def get_ads_by_placement(placement: str):
    """
    Obtenir les publicités actives pour un emplacement spécifique.
    Utilisé par le frontend BIONIC pour afficher les pubs.
    """
    db = get_db()
    
    now = datetime.now(timezone.utc).isoformat()
    
    ads = await db.deployed_ads.find({
        "placement": placement,
        "is_active": True,
        "campaign_start": {"$lte": now},
        "campaign_end": {"$gte": now}
    }).to_list(10)
    
    for ad in ads:
        ad.pop("_id", None)
    
    return {
        "success": True,
        "placement": placement,
        "ads": ads,
        "count": len(ads)
    }


# ============================================
# HELPERS
# ============================================

def _get_placement_description(placement: str) -> str:
    descriptions = {
        "homepage_banner": "Bannière premium en haut de la page d'accueil",
        "sidebar_right": "Sidebar droite sur toutes les pages",
        "category_page": "En-tête des pages catégories",
        "article_inline": "Intégré dans les articles",
        "footer_banner": "Bannière en pied de page",
        "search_results": "Dans les résultats de recherche",
        "map_overlay": "Overlay sur la carte interactive"
    }
    return descriptions.get(placement, "Emplacement publicitaire")


async def _log_ad_action(db, opportunity_id: str, action: str, source: str, details: Dict = None):
    """Journaliser une action publicitaire"""
    log_entry = {
        "opportunity_id": opportunity_id,
        "action": action,
        "source": source,
        "details": details or {},
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    await db.ad_automation_logs.insert_one(log_entry)


# ============================================
# AUTO-TRIGGER ON AFFILIATE ACTIVATION
# ============================================

@router.post("/trigger/on-affiliate-activated")
async def trigger_on_affiliate_activated(
    affiliate_id: str = Body(..., embed=True)
):
    """
    Webhook appelé quand un affilié est activé.
    Crée automatiquement une opportunité publicitaire.
    """
    db = get_db()
    
    # Verify affiliate is active
    affiliate = await db.affiliate_switches.find_one({
        "affiliate_id": affiliate_id,
        "switch_active": True
    })
    
    if not affiliate:
        return {
            "success": False,
            "error": "Affilié non trouvé ou non actif"
        }
    
    # Create ad opportunity
    result = await create_ad_opportunity(
        affiliate_id=affiliate_id,
        auto_send_email=True
    )
    
    return result


# ============================================
# MASTER AD SWITCH (GLOBAL ON/OFF)
# ============================================

@router.get("/master-switch")
async def get_ad_master_switch():
    """
    Obtenir l'état du Master Switch Publicitaire.
    """
    db = get_db()
    
    switch = await db.ad_master_switch.find_one({"switch_id": "global"})
    
    if not switch:
        # Initialize if not exists
        switch = {
            "switch_id": "global",
            "is_active": False,  # OFF by default (pré-production)
            "auto_deploy_enabled": False,
            "reason": "Mode pré-production - En attente du signal GO LIVE",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "updated_by": "system_init"
        }
        await db.ad_master_switch.insert_one(switch)
    
    switch.pop("_id", None)
    
    return {
        "success": True,
        "master_switch": switch
    }


@router.post("/master-switch/toggle")
async def toggle_ad_master_switch(
    is_active: bool = Body(..., embed=True),
    reason: Optional[str] = Body(None, embed=True),
    admin_user: str = Body("admin", embed=True)
):
    """
    Activer/Désactiver le Master Switch Publicitaire.
    Contrôle global de toutes les publicités.
    """
    db = get_db()
    
    updates = {
        "is_active": is_active,
        "auto_deploy_enabled": is_active,
        "reason": reason or ("Activation manuelle" if is_active else "Désactivation manuelle"),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "updated_by": admin_user
    }
    
    await db.ad_master_switch.update_one(
        {"switch_id": "global"},
        {"$set": updates},
        upsert=True
    )
    
    # Log action
    await _log_ad_action(db, "MASTER_SWITCH", "toggle", admin_user, {
        "new_state": is_active,
        "reason": reason
    })
    
    # If turning OFF, pause all active campaigns
    if not is_active:
        await db.ad_opportunities.update_many(
            {"status": "active"},
            {"$set": {"status": "paused", "paused_at": datetime.now(timezone.utc).isoformat()}}
        )
        await db.deployed_ads.update_many(
            {"is_active": True},
            {"$set": {"is_active": False, "paused_at": datetime.now(timezone.utc).isoformat()}}
        )
    
    return {
        "success": True,
        "is_active": is_active,
        "message": f"Master Switch Publicitaire {'ACTIVÉ' if is_active else 'DÉSACTIVÉ'}"
    }


@router.post("/system/deactivate-all")
async def deactivate_all_ads(
    reason: str = Body("Désactivation globale pré-production", embed=True),
    admin_user: str = Body("admin", embed=True)
):
    """
    DÉSACTIVATION GLOBALE DE TOUTES LES PUBLICITÉS.
    Mode pré-production.
    """
    db = get_db()
    
    now = datetime.now(timezone.utc).isoformat()
    
    # 1. Turn OFF master switch
    await db.ad_master_switch.update_one(
        {"switch_id": "global"},
        {
            "$set": {
                "is_active": False,
                "auto_deploy_enabled": False,
                "reason": reason,
                "updated_at": now,
                "updated_by": admin_user
            }
        },
        upsert=True
    )
    
    # 2. Pause all ACTIVE opportunities
    active_result = await db.ad_opportunities.update_many(
        {"status": "active"},
        {
            "$set": {
                "status": "paused",
                "paused_at": now,
                "pause_reason": reason
            }
        }
    )
    
    # 3. Suspend all PENDING/CHECKOUT opportunities
    pending_result = await db.ad_opportunities.update_many(
        {"status": {"$in": ["pending", "email_sent", "checkout_started", "payment_pending"]}},
        {
            "$set": {
                "status": "suspended",
                "suspended_at": now,
                "suspend_reason": reason
            }
        }
    )
    
    # 4. Deactivate all deployed ads
    deployed_result = await db.deployed_ads.update_many(
        {"is_active": True},
        {
            "$set": {
                "is_active": False,
                "deactivated_at": now,
                "deactivation_reason": reason
            }
        }
    )
    
    # 5. Log action
    await _log_ad_action(db, "SYSTEM", "global_deactivation", admin_user, {
        "reason": reason,
        "active_paused": active_result.modified_count,
        "pending_suspended": pending_result.modified_count,
        "ads_deactivated": deployed_result.modified_count
    })
    
    return {
        "success": True,
        "deactivation_report": {
            "master_switch": "OFF",
            "active_campaigns_paused": active_result.modified_count,
            "pending_opportunities_suspended": pending_result.modified_count,
            "deployed_ads_deactivated": deployed_result.modified_count,
            "reason": reason,
            "executed_at": now,
            "executed_by": admin_user
        },
        "message": "🔒 DÉSACTIVATION GLOBALE EFFECTUÉE - Mode pré-production activé"
    }


@router.post("/system/reactivate-all")
async def reactivate_all_ads(
    admin_user: str = Body("admin", embed=True)
):
    """
    RÉACTIVATION GLOBALE DES PUBLICITÉS.
    Signal GO LIVE.
    """
    db = get_db()
    
    now = datetime.now(timezone.utc).isoformat()
    
    # 1. Turn ON master switch
    await db.ad_master_switch.update_one(
        {"switch_id": "global"},
        {
            "$set": {
                "is_active": True,
                "auto_deploy_enabled": True,
                "reason": "Signal GO LIVE - Réactivation globale",
                "updated_at": now,
                "updated_by": admin_user
            }
        },
        upsert=True
    )
    
    # 2. Reactivate PAUSED opportunities
    paused_result = await db.ad_opportunities.update_many(
        {"status": "paused"},
        {
            "$set": {
                "status": "active",
                "reactivated_at": now
            },
            "$unset": {"paused_at": "", "pause_reason": ""}
        }
    )
    
    # 3. Resume SUSPENDED opportunities to pending
    suspended_result = await db.ad_opportunities.update_many(
        {"status": "suspended"},
        {
            "$set": {
                "status": "pending",
                "resumed_at": now
            },
            "$unset": {"suspended_at": "", "suspend_reason": ""}
        }
    )
    
    # 4. Reactivate deployed ads
    deployed_result = await db.deployed_ads.update_many(
        {"deactivation_reason": {"$exists": True}},
        {
            "$set": {
                "is_active": True,
                "reactivated_at": now
            },
            "$unset": {"deactivated_at": "", "deactivation_reason": ""}
        }
    )
    
    # 5. Log action
    await _log_ad_action(db, "SYSTEM", "global_reactivation", admin_user, {
        "paused_reactivated": paused_result.modified_count,
        "suspended_resumed": suspended_result.modified_count,
        "ads_reactivated": deployed_result.modified_count
    })
    
    return {
        "success": True,
        "reactivation_report": {
            "master_switch": "ON",
            "campaigns_reactivated": paused_result.modified_count,
            "opportunities_resumed": suspended_result.modified_count,
            "ads_reactivated": deployed_result.modified_count,
            "executed_at": now,
            "executed_by": admin_user
        },
        "message": "🚀 RÉACTIVATION GLOBALE EFFECTUÉE - GO LIVE!"
    }


@router.get("/system/status")
async def get_ad_system_status():
    """
    Statut complet du système publicitaire.
    """
    db = get_db()
    
    # Master switch
    switch = await db.ad_master_switch.find_one({"switch_id": "global"})
    
    # Count by status
    status_counts = {}
    for status in ["pending", "email_sent", "checkout_started", "payment_pending", "paid", "active", "paused", "suspended", "expired", "cancelled"]:
        count = await db.ad_opportunities.count_documents({"status": status})
        if count > 0:
            status_counts[status] = count
    
    # Deployed ads
    active_ads = await db.deployed_ads.count_documents({"is_active": True})
    inactive_ads = await db.deployed_ads.count_documents({"is_active": False})
    
    return {
        "success": True,
        "system_status": {
            "master_switch": {
                "is_active": switch.get("is_active", False) if switch else False,
                "auto_deploy_enabled": switch.get("auto_deploy_enabled", False) if switch else False,
                "reason": switch.get("reason") if switch else "Non initialisé",
                "last_updated": switch.get("updated_at") if switch else None
            },
            "opportunities_by_status": status_counts,
            "deployed_ads": {
                "active": active_ads,
                "inactive": inactive_ads
            },
            "mode": "PRÉ-PRODUCTION" if not (switch and switch.get("is_active")) else "PRODUCTION"
        }
    }


logger.info("Affiliate Ad Automation Engine initialized - LEGO V5-ULTIME Module")
