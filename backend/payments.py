"""
Stripe Payment Integration for Hunt Marketplace
- One-time payments (featured listings, boosts, renewals)
- Subscriptions (PRO plans)
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime, timezone, timedelta
import uuid
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

payments_router = APIRouter(prefix="/api/payments", tags=["Payments"])

# Database connection
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "bionic_territory")
STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY", "")

client = None
db = None

async def get_db():
    global client, db
    if client is None:
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
    return db

# ============================================
# PRICING PACKAGES - SERVER-SIDE ONLY
# ============================================

MARKETPLACE_PACKAGES = {
    # Featured Listing (mise en vedette)
    "featured_7days": {
        "id": "featured_7days",
        "name": "Mise en vedette - 7 jours",
        "description": "Votre annonce en haut des résultats pendant 7 jours",
        "amount": 9.99,
        "currency": "cad",
        "type": "one_time",
        "duration_days": 7,
        "features": ["Badge vedette", "Position prioritaire", "Plus de visibilité"]
    },
    "featured_14days": {
        "id": "featured_14days",
        "name": "Mise en vedette - 14 jours",
        "description": "Votre annonce en haut des résultats pendant 14 jours",
        "amount": 14.99,
        "currency": "cad",
        "type": "one_time",
        "duration_days": 14,
        "features": ["Badge vedette", "Position prioritaire", "Plus de visibilité", "Économie 25%"]
    },
    "featured_30days": {
        "id": "featured_30days",
        "name": "Mise en vedette - 30 jours",
        "description": "Votre annonce en haut des résultats pendant 30 jours",
        "amount": 24.99,
        "currency": "cad",
        "type": "one_time",
        "duration_days": 30,
        "features": ["Badge vedette", "Position prioritaire", "Plus de visibilité", "Meilleur rapport qualité/prix"]
    },
    
    # Auto-bump (remontée automatique)
    "auto_bump_7days": {
        "id": "auto_bump_7days",
        "name": "Auto-bump - 7 jours",
        "description": "Votre annonce remonte automatiquement chaque jour",
        "amount": 4.99,
        "currency": "cad",
        "type": "one_time",
        "duration_days": 7,
        "features": ["Remontée quotidienne", "Plus de vues"]
    },
    "auto_bump_30days": {
        "id": "auto_bump_30days",
        "name": "Auto-bump - 30 jours",
        "description": "Votre annonce remonte automatiquement chaque jour pendant 30 jours",
        "amount": 14.99,
        "currency": "cad",
        "type": "one_time",
        "duration_days": 30,
        "features": ["Remontée quotidienne", "Plus de vues", "Économie 40%"]
    },
    
    # Listing Renewal
    "listing_renewal_30days": {
        "id": "listing_renewal_30days",
        "name": "Renouvellement - 30 jours",
        "description": "Prolongez votre annonce de 30 jours supplémentaires",
        "amount": 2.99,
        "currency": "cad",
        "type": "one_time",
        "duration_days": 30,
        "features": ["Extension de 30 jours"]
    },
    "listing_renewal_90days": {
        "id": "listing_renewal_90days",
        "name": "Renouvellement - 90 jours",
        "description": "Prolongez votre annonce de 90 jours",
        "amount": 6.99,
        "currency": "cad",
        "type": "one_time",
        "duration_days": 90,
        "features": ["Extension de 90 jours", "Économie 22%"]
    },
    
    # PRO Subscriptions
    "pro_monthly": {
        "id": "pro_monthly",
        "name": "PRO Mensuel",
        "description": "Accès PRO pendant 1 mois",
        "amount": 19.99,
        "currency": "cad",
        "type": "subscription",
        "duration_days": 30,
        "features": ["Annonces illimitées", "Badge PRO", "Statistiques avancées", "Support prioritaire"]
    },
    "pro_yearly": {
        "id": "pro_yearly",
        "name": "PRO Annuel",
        "description": "Accès PRO pendant 1 an - 2 mois gratuits!",
        "amount": 199.99,
        "currency": "cad",
        "type": "subscription",
        "duration_days": 365,
        "features": ["Annonces illimitées", "Badge PRO", "Statistiques avancées", "Support prioritaire", "2 mois gratuits"]
    },
    
    # Outfitter/Pourvoyeur Packages
    "outfitter_basic": {
        "id": "outfitter_basic",
        "name": "Forfait Pourvoyeur Basic",
        "description": "Pour les pourvoyeurs avec peu d'annonces",
        "amount": 49.99,
        "currency": "cad",
        "type": "subscription",
        "duration_days": 30,
        "features": ["10 annonces actives", "Badge Pourvoyeur", "Page de profil personnalisée"]
    },
    "outfitter_premium": {
        "id": "outfitter_premium",
        "name": "Forfait Pourvoyeur Premium",
        "description": "Pour les pourvoyeurs avec beaucoup d'offres",
        "amount": 99.99,
        "currency": "cad",
        "type": "subscription",
        "duration_days": 30,
        "features": ["Annonces illimitées", "Badge Pourvoyeur Premium", "Page personnalisée", "Mise en vedette gratuite", "Support VIP"]
    }
}

# ============================================
# PYDANTIC MODELS
# ============================================

class CheckoutRequest(BaseModel):
    package_id: str
    origin_url: str
    listing_id: Optional[str] = None  # For listing-specific purchases
    seller_id: Optional[str] = None

class CheckoutResponse(BaseModel):
    url: str
    session_id: str
    package: Dict

class PaymentTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    seller_id: Optional[str] = None
    listing_id: Optional[str] = None
    package_id: str
    package_name: str
    amount: float
    currency: str
    payment_status: str = "pending"  # pending, paid, failed, expired
    status: str = "initiated"  # initiated, completed, cancelled
    metadata: Dict = {}
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

# ============================================
# API ENDPOINTS
# ============================================

@payments_router.get("/packages")
async def get_packages(package_type: Optional[str] = None):
    """Get available payment packages"""
    packages = list(MARKETPLACE_PACKAGES.values())
    
    if package_type:
        packages = [p for p in packages if p["type"] == package_type]
    
    return {
        "packages": packages,
        "categories": {
            "featured": [p for p in packages if "featured" in p["id"]],
            "auto_bump": [p for p in packages if "auto_bump" in p["id"]],
            "renewal": [p for p in packages if "renewal" in p["id"]],
            "subscriptions": [p for p in packages if p["type"] == "subscription" and "outfitter" not in p["id"]],
            "outfitter": [p for p in packages if "outfitter" in p["id"]]
        }
    }

@payments_router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout_session(request: CheckoutRequest, http_request: Request):
    """Create a Stripe checkout session"""
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Payment service not configured")
    
    # Validate package
    package = MARKETPLACE_PACKAGES.get(request.package_id)
    if not package:
        raise HTTPException(status_code=400, detail="Invalid package ID")
    
    database = await get_db()
    
    try:
        from emergentintegrations.payments.stripe.checkout import (
            StripeCheckout, 
            CheckoutSessionRequest
        )
        
        # Build URLs from frontend origin
        success_url = f"{request.origin_url}/marketplace?payment=success&session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{request.origin_url}/marketplace?payment=cancelled"
        
        # Initialize Stripe
        host_url = str(http_request.base_url).rstrip('/')
        webhook_url = f"{host_url}/api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
        
        # Prepare metadata
        metadata = {
            "package_id": request.package_id,
            "package_name": package["name"],
            "package_type": package["type"],
            "seller_id": request.seller_id or "",
            "listing_id": request.listing_id or "",
            "source": "hunt_marketplace"
        }
        
        # Create checkout session with fixed server-side amount
        checkout_request = CheckoutSessionRequest(
            amount=float(package["amount"]),
            currency=package["currency"],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata
        )
        
        session = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Create payment transaction record BEFORE redirect
        transaction = {
            "id": str(uuid.uuid4()),
            "session_id": session.session_id,
            "seller_id": request.seller_id,
            "listing_id": request.listing_id,
            "package_id": request.package_id,
            "package_name": package["name"],
            "amount": package["amount"],
            "currency": package["currency"],
            "payment_status": "pending",
            "status": "initiated",
            "metadata": metadata,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await database.payment_transactions.insert_one(transaction)
        
        logger.info(f"Checkout session created: {session.session_id} for package {request.package_id}")
        
        return CheckoutResponse(
            url=session.url,
            session_id=session.session_id,
            package=package
        )
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        raise HTTPException(status_code=500, detail="Payment library not available")
    except Exception as e:
        logger.error(f"Checkout error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@payments_router.get("/status/{session_id}")
async def get_payment_status(session_id: str):
    """Get payment status by session ID"""
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Payment service not configured")
    
    database = await get_db()
    
    # First check if already processed
    transaction = await database.payment_transactions.find_one(
        {"session_id": session_id},
        {"_id": 0}
    )
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # If already completed, return cached status
    if transaction.get("payment_status") == "paid" and transaction.get("status") == "completed":
        return {
            "status": transaction["status"],
            "payment_status": transaction["payment_status"],
            "amount": transaction["amount"],
            "currency": transaction["currency"],
            "package_id": transaction["package_id"],
            "completed_at": transaction.get("completed_at"),
            "already_processed": True
        }
    
    try:
        from emergentintegrations.payments.stripe.checkout import StripeCheckout
        
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url="")
        checkout_status = await stripe_checkout.get_checkout_status(session_id)
        
        # Update transaction status
        new_status = "completed" if checkout_status.payment_status == "paid" else transaction["status"]
        update_data = {
            "payment_status": checkout_status.payment_status,
            "status": new_status,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        if checkout_status.payment_status == "paid" and transaction.get("status") != "completed":
            update_data["completed_at"] = datetime.now(timezone.utc).isoformat()
            
            # Apply package benefits
            await apply_package_benefits(
                database,
                transaction["package_id"],
                transaction.get("seller_id"),
                transaction.get("listing_id")
            )
        
        await database.payment_transactions.update_one(
            {"session_id": session_id},
            {"$set": update_data}
        )
        
        return {
            "status": new_status,
            "payment_status": checkout_status.payment_status,
            "amount": checkout_status.amount_total / 100,  # Convert from cents
            "currency": checkout_status.currency,
            "package_id": transaction["package_id"],
            "completed_at": update_data.get("completed_at"),
            "already_processed": False
        }
        
    except Exception as e:
        logger.error(f"Status check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@payments_router.get("/transactions")
async def get_transactions(
    seller_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50
):
    """Get payment transactions"""
    database = await get_db()
    
    query = {}
    if seller_id:
        query["seller_id"] = seller_id
    if status:
        query["payment_status"] = status
    
    transactions = await database.payment_transactions.find(
        query,
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    return {"transactions": transactions}

# ============================================
# APPLY PACKAGE BENEFITS
# ============================================

async def apply_package_benefits(database, package_id: str, seller_id: Optional[str], listing_id: Optional[str]):
    """Apply the purchased package benefits to seller/listing"""
    package = MARKETPLACE_PACKAGES.get(package_id)
    if not package:
        return
    
    now = datetime.now(timezone.utc)
    duration_days = package.get("duration_days", 30)
    expires_at = now + timedelta(days=duration_days)
    
    # Featured listing
    if "featured" in package_id and listing_id:
        await database.marketplace_listings.update_one(
            {"id": listing_id},
            {
                "$set": {
                    "is_featured": True,
                    "featured_until": expires_at.isoformat(),
                    "updated_at": now.isoformat()
                }
            }
        )
        logger.info(f"Applied featured status to listing {listing_id} until {expires_at}")
    
    # Auto-bump
    if "auto_bump" in package_id and listing_id:
        await database.marketplace_listings.update_one(
            {"id": listing_id},
            {
                "$set": {
                    "auto_bump_enabled": True,
                    "auto_bump_until": expires_at.isoformat(),
                    "updated_at": now.isoformat()
                }
            }
        )
        logger.info(f"Applied auto-bump to listing {listing_id} until {expires_at}")
    
    # Listing renewal
    if "renewal" in package_id and listing_id:
        listing = await database.marketplace_listings.find_one({"id": listing_id})
        if listing:
            current_expires = listing.get("expires_at")
            if current_expires:
                try:
                    current_dt = datetime.fromisoformat(current_expires.replace('Z', '+00:00'))
                    new_expires = current_dt + timedelta(days=duration_days)
                except:
                    new_expires = expires_at
            else:
                new_expires = expires_at
            
            await database.marketplace_listings.update_one(
                {"id": listing_id},
                {
                    "$set": {
                        "expires_at": new_expires.isoformat(),
                        "availability": "disponible",
                        "updated_at": now.isoformat()
                    }
                }
            )
            logger.info(f"Renewed listing {listing_id} until {new_expires}")
    
    # PRO subscription
    if "pro_" in package_id and seller_id:
        await database.marketplace_sellers.update_one(
            {"id": seller_id},
            {
                "$set": {
                    "is_pro": True,
                    "pro_until": expires_at.isoformat(),
                    "free_listings_remaining": 999,  # Essentially unlimited
                    "updated_at": now.isoformat()
                }
            }
        )
        logger.info(f"Applied PRO status to seller {seller_id} until {expires_at}")
    
    # Outfitter subscription
    if "outfitter" in package_id and seller_id:
        is_premium = "premium" in package_id
        await database.marketplace_sellers.update_one(
            {"id": seller_id},
            {
                "$set": {
                    "is_pro": True,
                    "is_outfitter": True,
                    "outfitter_tier": "premium" if is_premium else "basic",
                    "pro_until": expires_at.isoformat(),
                    "free_listings_remaining": 999 if is_premium else 10,
                    "updated_at": now.isoformat()
                }
            }
        )
        logger.info(f"Applied Outfitter {package_id} to seller {seller_id}")

# ============================================
# WEBHOOK HANDLER
# ============================================

@payments_router.post("/webhook/stripe")
async def handle_stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Payment service not configured")
    
    database = await get_db()
    
    try:
        from emergentintegrations.payments.stripe.checkout import StripeCheckout
        
        body = await request.body()
        signature = request.headers.get("Stripe-Signature", "")
        
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url="")
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        # Update transaction based on webhook
        if webhook_response.session_id:
            transaction = await database.payment_transactions.find_one(
                {"session_id": webhook_response.session_id}
            )
            
            if transaction and transaction.get("status") != "completed":
                update_data = {
                    "payment_status": webhook_response.payment_status,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                
                if webhook_response.payment_status == "paid":
                    update_data["status"] = "completed"
                    update_data["completed_at"] = datetime.now(timezone.utc).isoformat()
                    
                    # Apply benefits
                    await apply_package_benefits(
                        database,
                        transaction["package_id"],
                        transaction.get("seller_id"),
                        transaction.get("listing_id")
                    )
                
                await database.payment_transactions.update_one(
                    {"session_id": webhook_response.session_id},
                    {"$set": update_data}
                )
        
        return {"received": True}
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

logger.info("Payment API initialized with Stripe")
