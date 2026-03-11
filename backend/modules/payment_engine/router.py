"""
Payment Engine Router - V5-ULTIME Monétisation
=============================================

Intégration Stripe avec support pour:
- Paiements uniques
- Abonnements récurrents
- Apple Pay / Google Pay (via Stripe)
- Webhooks

Version: 1.0.0
"""

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel
from datetime import datetime, timezone
from enum import Enum
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/payments", tags=["Payment Engine - Monétisation"])

# Database
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'bionic_db')
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY', 'sk_test_emergent')

_client = None
_db = None

def get_db():
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(MONGO_URL)
        _db = _client[DB_NAME]
    return _db

# ==============================================
# MODELS
# ==============================================

class PaymentStatus(str, Enum):
    INITIATED = "initiated"
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    EXPIRED = "expired"
    REFUNDED = "refunded"

class PackageType(str, Enum):
    PREMIUM_MONTHLY = "premium_monthly"
    PREMIUM_YEARLY = "premium_yearly"
    PRO_MONTHLY = "pro_monthly"
    PRO_YEARLY = "pro_yearly"

# Fixed packages - amounts defined server-side only (security)
PACKAGES = {
    PackageType.PREMIUM_MONTHLY: {
        "name": "Premium Mensuel",
        "amount": 9.99,
        "currency": "cad",
        "tier": "premium",
        "duration_days": 30
    },
    PackageType.PREMIUM_YEARLY: {
        "name": "Premium Annuel",
        "amount": 99.99,
        "currency": "cad",
        "tier": "premium",
        "duration_days": 365
    },
    PackageType.PRO_MONTHLY: {
        "name": "Pro Mensuel",
        "amount": 19.99,
        "currency": "cad",
        "tier": "pro",
        "duration_days": 30
    },
    PackageType.PRO_YEARLY: {
        "name": "Pro Annuel",
        "amount": 199.99,
        "currency": "cad",
        "tier": "pro",
        "duration_days": 365
    }
}

class CheckoutRequest(BaseModel):
    package_id: PackageType
    user_id: str
    origin_url: str  # Frontend provides this for dynamic URLs

class CheckoutResponse(BaseModel):
    url: str
    session_id: str

# ==============================================
# MODULE INFO
# ==============================================

@router.get("/")
async def payment_engine_info():
    """Get payment engine information"""
    return {
        "module": "payment_engine",
        "version": "1.0.0",
        "description": "Système de paiement V5-ULTIME",
        "provider": "Stripe",
        "features": [
            "Paiements uniques",
            "Abonnements",
            "Apple Pay",
            "Google Pay",
            "Webhooks"
        ],
        "packages": [p.value for p in PackageType]
    }

# ==============================================
# PACKAGES
# ==============================================

@router.get("/packages")
async def get_packages():
    """Get available packages"""
    packages_list = []
    for pkg_id, pkg_info in PACKAGES.items():
        packages_list.append({
            "id": pkg_id.value,
            "name": pkg_info["name"],
            "amount": pkg_info["amount"],
            "currency": pkg_info["currency"],
            "tier": pkg_info["tier"],
            "duration_days": pkg_info["duration_days"]
        })
    
    return {"success": True, "packages": packages_list}

# ==============================================
# CHECKOUT SESSION
# ==============================================

@router.post("/checkout/session")
async def create_checkout_session(request: CheckoutRequest, http_request: Request):
    """Create Stripe checkout session"""
    db = get_db()
    
    # Validate package exists (security: amount from server only)
    if request.package_id not in PACKAGES:
        raise HTTPException(status_code=400, detail="Invalid package")
    
    package = PACKAGES[request.package_id]
    
    try:
        from emergentintegrations.payments.stripe.checkout import (
            StripeCheckout, CheckoutSessionRequest
        )
        
        # Build dynamic URLs
        host_url = str(http_request.base_url).rstrip('/')
        webhook_url = f"{host_url}/api/webhook/stripe"
        success_url = f"{request.origin_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{request.origin_url}/payment/cancel"
        
        # Initialize Stripe
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
        
        # Create checkout request
        checkout_request = CheckoutSessionRequest(
            amount=float(package["amount"]),
            currency=package["currency"],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "user_id": request.user_id,
                "package_id": request.package_id.value,
                "tier": package["tier"],
                "duration_days": str(package["duration_days"])
            }
        )
        
        # Create session
        session = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Create transaction record BEFORE redirect (security)
        transaction = {
            "session_id": session.session_id,
            "user_id": request.user_id,
            "package_id": request.package_id.value,
            "amount": package["amount"],
            "currency": package["currency"],
            "tier": package["tier"],
            "duration_days": package["duration_days"],
            "payment_status": PaymentStatus.INITIATED.value,
            "created_at": datetime.now(timezone.utc)
        }
        
        await db.payment_transactions.insert_one(transaction)
        
        return {
            "success": True,
            "url": session.url,
            "session_id": session.session_id
        }
        
    except ImportError as e:
        logger.error(f"Stripe integration not available: {e}")
        raise HTTPException(status_code=500, detail="Payment service unavailable")
    except Exception as e:
        logger.error(f"Checkout session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==============================================
# CHECKOUT STATUS
# ==============================================

@router.get("/checkout/status/{session_id}")
async def get_checkout_status(session_id: str):
    """Get checkout session status and update transaction"""
    db = get_db()
    
    try:
        from emergentintegrations.payments.stripe.checkout import StripeCheckout
        
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY)
        
        # Get status from Stripe
        status = await stripe_checkout.get_checkout_status(session_id)
        
        # Get existing transaction
        transaction = await db.payment_transactions.find_one(
            {"session_id": session_id}, 
            {"_id": 0}
        )
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Determine new status
        new_status = PaymentStatus.PENDING.value
        if status.payment_status == "paid":
            new_status = PaymentStatus.PAID.value
        elif status.status == "expired":
            new_status = PaymentStatus.EXPIRED.value
        
        # Update transaction (only if not already processed)
        if transaction["payment_status"] != PaymentStatus.PAID.value:
            update_data = {
                "payment_status": new_status,
                "stripe_status": status.status,
                "stripe_payment_status": status.payment_status,
                "amount_total": status.amount_total,
                "updated_at": datetime.now(timezone.utc)
            }
            
            await db.payment_transactions.update_one(
                {"session_id": session_id},
                {"$set": update_data}
            )
            
            # If payment successful, upgrade subscription
            if new_status == PaymentStatus.PAID.value:
                await _process_successful_payment(
                    db,
                    transaction["user_id"],
                    transaction["tier"],
                    transaction["duration_days"],
                    session_id
                )
        
        return {
            "success": True,
            "session_id": session_id,
            "status": status.status,
            "payment_status": status.payment_status,
            "amount_total": status.amount_total,
            "currency": status.currency,
            "processed": transaction["payment_status"] == PaymentStatus.PAID.value or new_status == PaymentStatus.PAID.value
        }
        
    except ImportError:
        raise HTTPException(status_code=500, detail="Payment service unavailable")
    except Exception as e:
        logger.error(f"Status check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def _process_successful_payment(db, user_id: str, tier: str, duration_days: int, session_id: str):
    """Process successful payment - upgrade subscription"""
    from datetime import timedelta
    
    # Check if already processed (prevent double processing)
    existing = await db.subscription_upgrades.find_one({"session_id": session_id})
    if existing:
        logger.info(f"Payment {session_id} already processed")
        return
    
    # Calculate expiration
    expires_at = datetime.now(timezone.utc) + timedelta(days=duration_days)
    
    # Update subscription
    await db.subscriptions.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "tier": tier,
                "expires_at": expires_at,
                "upgraded_at": datetime.now(timezone.utc),
                "payment_session_id": session_id
            }
        },
        upsert=True
    )
    
    # Record upgrade (prevent duplicates)
    await db.subscription_upgrades.insert_one({
        "session_id": session_id,
        "user_id": user_id,
        "tier": tier,
        "duration_days": duration_days,
        "expires_at": expires_at,
        "processed_at": datetime.now(timezone.utc)
    })
    
    logger.info(f"User {user_id} upgraded to {tier} until {expires_at}")

# ==============================================
# WEBHOOK
# ==============================================

@router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    db = get_db()
    
    try:
        from emergentintegrations.payments.stripe.checkout import StripeCheckout
        
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY)
        
        # Get raw body
        body = await request.body()
        signature = request.headers.get("Stripe-Signature")
        
        # Process webhook
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        logger.info(f"Webhook received: {webhook_response.event_type}")
        
        # Handle payment success
        if webhook_response.payment_status == "paid":
            # Update transaction
            await db.payment_transactions.update_one(
                {"session_id": webhook_response.session_id},
                {
                    "$set": {
                        "payment_status": PaymentStatus.PAID.value,
                        "webhook_event_id": webhook_response.event_id,
                        "webhook_received_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            # Get transaction for upgrade
            transaction = await db.payment_transactions.find_one(
                {"session_id": webhook_response.session_id},
                {"_id": 0}
            )
            
            if transaction:
                await _process_successful_payment(
                    db,
                    transaction["user_id"],
                    transaction["tier"],
                    transaction["duration_days"],
                    webhook_response.session_id
                )
        
        return {"success": True, "event_id": webhook_response.event_id}
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"success": False, "error": str(e)}

# ==============================================
# TRANSACTION HISTORY
# ==============================================

@router.get("/transactions/{user_id}")
async def get_transactions(user_id: str, limit: int = Query(20, le=100)):
    """Get user's transaction history"""
    db = get_db()
    
    transactions = await db.payment_transactions.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    return {"success": True, "total": len(transactions), "transactions": transactions}
