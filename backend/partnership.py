"""
Partnership Engine Module - BIONIC™
Complete partner management system with:
- Partner application form
- Admin management of requests
- Automatic email notifications
- Partner conversion and dashboard
"""

import os
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from enum import Enum
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr, Field
from fastapi import APIRouter, HTTPException, BackgroundTasks
from bson import ObjectId

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Router
router = APIRouter(prefix="/partnership", tags=["Partnership Engine"])

# Database connection
mongo_url = os.environ.get('MONGO_URL')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'scentscience')]

# Email configuration
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'steeve.ross@gmail.com')
APP_NAME_FR = "Chasse Bionic™"
APP_NAME_EN = "Bionic Hunt™"
APP_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:3000').replace('/api', '').rstrip('/')

# Email settings collection name
EMAIL_SETTINGS_COLLECTION = "partnership_settings"


# ============================================
# ENUMS & CONSTANTS
# ============================================

class PartnerType(str, Enum):
    MARQUES = "marques"
    POURVOIRIES = "pourvoiries"
    PROPRIETAIRES = "proprietaires"
    GUIDES = "guides"
    BOUTIQUES = "boutiques"
    SERVICES = "services"
    FABRICANTS = "fabricants"
    ZEC = "zec"
    CLUBS = "clubs"
    PARTICULIERS = "particuliers"
    AUTRES = "autres"


class RequestStatus(str, Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"
    CONVERTED = "converted"


PARTNER_TYPE_LABELS = {
    "marques": {"fr": "Marques", "en": "Brands"},
    "pourvoiries": {"fr": "Pourvoiries", "en": "Outfitters"},
    "proprietaires": {"fr": "Propriétaires de terres", "en": "Land Owners"},
    "guides": {"fr": "Guides / Experts", "en": "Guides / Experts"},
    "boutiques": {"fr": "Boutiques", "en": "Retail Stores"},
    "services": {"fr": "Services spécialisés", "en": "Specialized Services"},
    "fabricants": {"fr": "Fabricants d'équipement", "en": "Equipment Manufacturers"},
    "zec": {"fr": "ZEC (Zones d'Exploitation Contrôlée)", "en": "ZEC (Controlled Harvesting Zones)"},
    "clubs": {"fr": "Clubs privés de chasse et pêche", "en": "Private Hunting & Fishing Clubs"},
    "particuliers": {"fr": "Particuliers", "en": "Individuals"},
    "autres": {"fr": "Autres", "en": "Others"}
}


# ============================================
# PYDANTIC MODELS
# ============================================

class PartnerRequestCreate(BaseModel):
    """Partner application form submission"""
    company_name: str = Field(..., min_length=2, max_length=200)
    partner_type: PartnerType
    contact_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    website: Optional[str] = None
    description: str = Field(..., min_length=20, max_length=2000)
    products_services: str = Field(..., min_length=10, max_length=1000)
    documents: Optional[List[str]] = []
    legal_consent: bool = True
    preferred_language: str = "fr"


class PartnerRequestResponse(BaseModel):
    """Partner request response"""
    id: str
    company_name: str
    partner_type: str
    partner_type_label: str
    contact_name: str
    email: str
    phone: str
    website: Optional[str]
    description: str
    products_services: str
    documents: List[str]
    status: str
    preferred_language: str
    created_at: str
    updated_at: Optional[str]
    admin_notes: Optional[str]
    assigned_to: Optional[str]
    reviewed_at: Optional[str]
    reviewed_by: Optional[str]


class ReservationStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    EXPIRED = "expired"


class AvailabilityStatus(str, Enum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    BLOCKED = "blocked"
    PENDING = "pending"


# ============================================
# PYDANTIC MODELS - CALENDAR & RESERVATIONS
# ============================================

class OfferCreate(BaseModel):
    """Partner offer/service creation"""
    title: str = Field(..., min_length=2, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    offer_type: str  # forfait, territoire, hebergement, service, equipement, acces
    category: Optional[str] = None
    price: float = Field(..., gt=0)
    price_unit: str = "jour"  # jour, nuit, semaine, personne, unite
    max_guests: Optional[int] = None
    location: Optional[str] = None
    coordinates: Optional[dict] = None  # {lat, lng}
    images: Optional[List[str]] = []
    species: Optional[List[str]] = []  # orignal, chevreuil, ours, dindon, etc.
    amenities: Optional[List[str]] = []
    rules: Optional[str] = None
    is_active: bool = True


class AvailabilityCreate(BaseModel):
    """Availability slot for an offer"""
    offer_id: str
    date: str  # YYYY-MM-DD
    status: AvailabilityStatus = AvailabilityStatus.AVAILABLE
    price_override: Optional[float] = None
    quota: Optional[int] = None  # For quota-based offers
    notes: Optional[str] = None


class AvailabilityBulkCreate(BaseModel):
    """Bulk availability creation"""
    offer_id: str
    start_date: str  # YYYY-MM-DD
    end_date: str  # YYYY-MM-DD
    status: AvailabilityStatus = AvailabilityStatus.AVAILABLE
    price_override: Optional[float] = None
    exclude_days: Optional[List[int]] = []  # 0=Monday, 6=Sunday


class ReservationCreate(BaseModel):
    """Reservation request from client"""
    offer_id: str
    partner_id: str
    dates: List[str]  # List of dates YYYY-MM-DD
    guests: Optional[int] = 1
    client_name: str
    client_email: EmailStr
    client_phone: str
    notes: Optional[str] = None


class ReservationResponse(BaseModel):
    """Reservation confirmation"""
    action: str  # confirm, cancel, complete
    notes: Optional[str] = None




class PartnerRequestUpdate(BaseModel):
    """Admin update for partner request"""
    status: Optional[RequestStatus] = None
    admin_notes: Optional[str] = None
    assigned_to: Optional[str] = None


class PartnerProfile(BaseModel):
    """Official partner profile"""
    company_name: str
    partner_type: str
    contact_name: str
    email: EmailStr
    phone: str
    website: Optional[str] = None
    description: str
    products_services: str
    address: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    commission_rate: float = 10.0
    wallet_balance: float = 0.0


class PartnerStats(BaseModel):
    """Partner dashboard statistics"""
    total_reservations: int = 0
    pending_reservations: int = 0
    confirmed_reservations: int = 0
    total_revenue: float = 0.0
    pending_payout: float = 0.0
    total_views: int = 0
    conversion_rate: float = 0.0
    rating: float = 0.0
    review_count: int = 0


# ============================================
# HELPER FUNCTIONS
# ============================================

def serialize_doc(doc: dict) -> dict:
    """Convert MongoDB document to JSON-serializable format"""
    if doc is None:
        return None
    result = {}
    for key, value in doc.items():
        if key == '_id':
            result['id'] = str(value)
        elif isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, datetime):
            result[key] = value.isoformat()
        else:
            result[key] = value
    return result


async def get_email_settings() -> dict:
    """Get email notification settings"""
    settings = await db[EMAIL_SETTINGS_COLLECTION].find_one({"_id": "email_settings"})
    if not settings:
        # Default settings - all emails enabled
        return {
            "acknowledgment_enabled": True,  # Email to partner on submission
            "admin_notification_enabled": True,  # Email to admin on new request
            "approval_enabled": True,  # Email to partner on approval
            "rejection_enabled": True,  # Email to partner on rejection
            "updated_at": None
        }
    return {
        "acknowledgment_enabled": settings.get("acknowledgment_enabled", True),
        "admin_notification_enabled": settings.get("admin_notification_enabled", True),
        "approval_enabled": settings.get("approval_enabled", True),
        "rejection_enabled": settings.get("rejection_enabled", True),
        "updated_at": settings.get("updated_at")
    }


async def is_email_type_enabled(email_type: str) -> bool:
    """Check if a specific email type is enabled"""
    settings = await get_email_settings()
    type_mapping = {
        "acknowledgment": "acknowledgment_enabled",
        "admin": "admin_notification_enabled",
        "approved": "approval_enabled",
        "rejected": "rejection_enabled"
    }
    setting_key = type_mapping.get(email_type)
    if setting_key:
        return settings.get(setting_key, True)
    return True


async def send_partner_notification_email(request_data: dict, notification_type: str):
    """Send email notification for partner requests"""
    try:
        # Check if this email type is enabled
        if not await is_email_type_enabled(notification_type):
            logger.info(f"Email type '{notification_type}' is disabled, skipping notification")
            return
        
        # Import email module
        from email_notifications import send_email
        
        lang = request_data.get('preferred_language', 'fr')
        app_name = APP_NAME_FR if lang == 'fr' else APP_NAME_EN
        partner_type_label = PARTNER_TYPE_LABELS.get(request_data.get('partner_type'), {}).get(lang, request_data.get('partner_type'))
        
        if notification_type == "acknowledgment":
            # Send acknowledgment to partner
            subject = f"Demande de partenariat reçue - {app_name}" if lang == 'fr' else f"Partnership Request Received - {app_name}"
            
            if lang == 'fr':
                content = f"""
                <h2 style="color: #f5a623; margin-bottom: 20px;">Merci pour votre demande de partenariat!</h2>
                <p>Bonjour <strong>{request_data.get('contact_name')}</strong>,</p>
                <p>Nous avons bien reçu votre demande de partenariat pour <strong>{request_data.get('company_name')}</strong>.</p>
                
                <div style="background: #222; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #f5a623;">
                    <p style="margin: 5px 0;"><strong>Type de partenariat:</strong> {partner_type_label}</p>
                    <p style="margin: 5px 0;"><strong>Courriel:</strong> {request_data.get('email')}</p>
                    <p style="margin: 5px 0;"><strong>Téléphone:</strong> {request_data.get('phone')}</p>
                </div>
                
                <p>Notre équipe examinera votre demande dans les plus brefs délais. Vous recevrez une réponse sous <strong>48 à 72 heures ouvrables</strong>.</p>
                
                <p>En attendant, n'hésitez pas à visiter notre site pour découvrir nos services.</p>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="{APP_URL}" style="background: #f5a623; color: #000; padding: 12px 30px; border-radius: 25px; text-decoration: none; font-weight: bold;">
                        Visiter {app_name}
                    </a>
                </div>
                """
            else:
                content = f"""
                <h2 style="color: #f5a623; margin-bottom: 20px;">Thank you for your partnership request!</h2>
                <p>Hello <strong>{request_data.get('contact_name')}</strong>,</p>
                <p>We have received your partnership request for <strong>{request_data.get('company_name')}</strong>.</p>
                
                <div style="background: #222; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #f5a623;">
                    <p style="margin: 5px 0;"><strong>Partnership Type:</strong> {partner_type_label}</p>
                    <p style="margin: 5px 0;"><strong>Email:</strong> {request_data.get('email')}</p>
                    <p style="margin: 5px 0;"><strong>Phone:</strong> {request_data.get('phone')}</p>
                </div>
                
                <p>Our team will review your request shortly. You will receive a response within <strong>48 to 72 business hours</strong>.</p>
                
                <p>In the meantime, feel free to visit our website to discover our services.</p>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="{APP_URL}" style="background: #f5a623; color: #000; padding: 12px 30px; border-radius: 25px; text-decoration: none; font-weight: bold;">
                        Visit {app_name}
                    </a>
                </div>
                """
            
            await send_email(request_data.get('email'), subject, content)
            logger.info(f"Acknowledgment email sent to {request_data.get('email')}")
            
        elif notification_type == "admin":
            # Send notification to admin
            subject = f"🤝 Nouvelle demande de partenariat - {request_data.get('company_name')}"
            
            content = f"""
            <h2 style="color: #f5a623; margin-bottom: 20px;">Nouvelle demande de partenariat</h2>
            
            <div style="background: #222; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #f5a623; margin-top: 0;">Informations</h3>
                <table style="width: 100%; color: #fff;">
                    <tr><td style="padding: 8px 0; color: #888;">Entreprise:</td><td style="padding: 8px 0;"><strong>{request_data.get('company_name')}</strong></td></tr>
                    <tr><td style="padding: 8px 0; color: #888;">Type:</td><td style="padding: 8px 0;">{partner_type_label}</td></tr>
                    <tr><td style="padding: 8px 0; color: #888;">Contact:</td><td style="padding: 8px 0;">{request_data.get('contact_name')}</td></tr>
                    <tr><td style="padding: 8px 0; color: #888;">Courriel:</td><td style="padding: 8px 0;"><a href="mailto:{request_data.get('email')}" style="color: #f5a623;">{request_data.get('email')}</a></td></tr>
                    <tr><td style="padding: 8px 0; color: #888;">Téléphone:</td><td style="padding: 8px 0;">{request_data.get('phone')}</td></tr>
                    <tr><td style="padding: 8px 0; color: #888;">Site web:</td><td style="padding: 8px 0;">{request_data.get('website') or 'N/A'}</td></tr>
                    <tr><td style="padding: 8px 0; color: #888;">Langue:</td><td style="padding: 8px 0;">{'Français' if lang == 'fr' else 'English'}</td></tr>
                </table>
            </div>
            
            <div style="background: #222; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #f5a623; margin-top: 0;">Description du partenariat</h3>
                <p style="color: #ccc;">{request_data.get('description')}</p>
            </div>
            
            <div style="background: #222; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #f5a623; margin-top: 0;">Produits / Services proposés</h3>
                <p style="color: #ccc;">{request_data.get('products_services')}</p>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <a href="{APP_URL}/admin" style="background: #f5a623; color: #000; padding: 12px 30px; border-radius: 25px; text-decoration: none; font-weight: bold;">
                    Gérer dans l'Admin
                </a>
            </div>
            """
            
            await send_email(ADMIN_EMAIL, subject, content)
            logger.info(f"Admin notification email sent to {ADMIN_EMAIL}")
            
        elif notification_type == "approved":
            # Send approval notification to partner
            subject = f"🎉 Partenariat approuvé - {app_name}" if lang == 'fr' else f"🎉 Partnership Approved - {app_name}"
            
            if lang == 'fr':
                content = f"""
                <h2 style="color: #f5a623; margin-bottom: 20px;">Félicitations! Votre partenariat est approuvé!</h2>
                <p>Bonjour <strong>{request_data.get('contact_name')}</strong>,</p>
                <p>Nous avons le plaisir de vous informer que votre demande de partenariat pour <strong>{request_data.get('company_name')}</strong> a été <strong style="color: #22c55e;">approuvée</strong>!</p>
                
                <div style="background: linear-gradient(135deg, #22c55e33 0%, #16a34a33 100%); padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #22c55e;">
                    <h3 style="color: #22c55e; margin-top: 0;">✓ Prochaines étapes</h3>
                    <ol style="color: #ccc;">
                        <li style="margin: 10px 0;">Connectez-vous à votre tableau de bord partenaire</li>
                        <li style="margin: 10px 0;">Complétez votre profil d'entreprise</li>
                        <li style="margin: 10px 0;">Ajoutez vos produits et services</li>
                        <li style="margin: 10px 0;">Configurez votre calendrier de disponibilités</li>
                    </ol>
                </div>
                
                <p>Un courriel avec vos identifiants de connexion vous sera envoyé séparément.</p>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="{APP_URL}/partner/dashboard" style="background: #f5a623; color: #000; padding: 12px 30px; border-radius: 25px; text-decoration: none; font-weight: bold;">
                        Accéder à mon tableau de bord
                    </a>
                </div>
                """
            else:
                content = f"""
                <h2 style="color: #f5a623; margin-bottom: 20px;">Congratulations! Your partnership is approved!</h2>
                <p>Hello <strong>{request_data.get('contact_name')}</strong>,</p>
                <p>We are pleased to inform you that your partnership request for <strong>{request_data.get('company_name')}</strong> has been <strong style="color: #22c55e;">approved</strong>!</p>
                
                <div style="background: linear-gradient(135deg, #22c55e33 0%, #16a34a33 100%); padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #22c55e;">
                    <h3 style="color: #22c55e; margin-top: 0;">✓ Next Steps</h3>
                    <ol style="color: #ccc;">
                        <li style="margin: 10px 0;">Log in to your partner dashboard</li>
                        <li style="margin: 10px 0;">Complete your company profile</li>
                        <li style="margin: 10px 0;">Add your products and services</li>
                        <li style="margin: 10px 0;">Configure your availability calendar</li>
                    </ol>
                </div>
                
                <p>An email with your login credentials will be sent separately.</p>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="{APP_URL}/partner/dashboard" style="background: #f5a623; color: #000; padding: 12px 30px; border-radius: 25px; text-decoration: none; font-weight: bold;">
                        Access my dashboard
                    </a>
                </div>
                """
            
            await send_email(request_data.get('email'), subject, content)
            logger.info(f"Approval email sent to {request_data.get('email')}")
            
        elif notification_type == "rejected":
            # Send rejection notification to partner
            subject = f"Demande de partenariat - {app_name}" if lang == 'fr' else f"Partnership Request - {app_name}"
            
            if lang == 'fr':
                content = f"""
                <h2 style="color: #f5a623; margin-bottom: 20px;">Mise à jour de votre demande de partenariat</h2>
                <p>Bonjour <strong>{request_data.get('contact_name')}</strong>,</p>
                <p>Nous vous remercions de l'intérêt que vous portez à {app_name}.</p>
                <p>Après examen de votre demande pour <strong>{request_data.get('company_name')}</strong>, nous avons décidé de ne pas donner suite à celle-ci pour le moment.</p>
                
                <p>Cette décision ne reflète pas la qualité de votre entreprise. Nous vous encourageons à nous contacter ultérieurement si votre situation évolue.</p>
                
                <p>Merci de votre compréhension.</p>
                
                <p>Cordialement,<br>L'équipe {app_name}</p>
                """
            else:
                content = f"""
                <h2 style="color: #f5a623; margin-bottom: 20px;">Partnership Request Update</h2>
                <p>Hello <strong>{request_data.get('contact_name')}</strong>,</p>
                <p>Thank you for your interest in {app_name}.</p>
                <p>After reviewing your request for <strong>{request_data.get('company_name')}</strong>, we have decided not to proceed at this time.</p>
                
                <p>This decision does not reflect the quality of your business. We encourage you to contact us again in the future if your situation changes.</p>
                
                <p>Thank you for your understanding.</p>
                
                <p>Best regards,<br>The {app_name} Team</p>
                """
            
            await send_email(request_data.get('email'), subject, content)
            logger.info(f"Rejection email sent to {request_data.get('email')}")
            
    except Exception as e:
        logger.error(f"Failed to send partner notification email: {e}")


# ============================================
# API ENDPOINTS - PARTNER REQUESTS
# ============================================

@router.get("/types")
async def get_partner_types():
    """Get list of partner types with labels"""
    return {
        "types": [
            {"value": pt.value, "label_fr": PARTNER_TYPE_LABELS[pt.value]["fr"], "label_en": PARTNER_TYPE_LABELS[pt.value]["en"]}
            for pt in PartnerType
        ]
    }


@router.post("/request", response_model=dict)
async def submit_partner_request(request: PartnerRequestCreate, background_tasks: BackgroundTasks):
    """Submit a new partner request"""
    try:
        # Check for duplicate email
        existing = await db.partner_requests.find_one({
            "email": request.email,
            "status": {"$in": ["pending", "reviewed"]}
        })
        if existing:
            raise HTTPException(status_code=400, detail="Une demande avec ce courriel est déjà en cours de traitement")
        
        # Create request document
        request_doc = {
            "company_name": request.company_name,
            "partner_type": request.partner_type.value,
            "contact_name": request.contact_name,
            "email": request.email,
            "phone": request.phone,
            "website": request.website,
            "description": request.description,
            "products_services": request.products_services,
            "documents": request.documents or [],
            "legal_consent": request.legal_consent,
            "preferred_language": request.preferred_language,
            "status": "pending",
            "created_at": datetime.now(timezone.utc),
            "updated_at": None,
            "admin_notes": None,
            "assigned_to": None,
            "reviewed_at": None,
            "reviewed_by": None
        }
        
        # Insert into database
        result = await db.partner_requests.insert_one(request_doc)
        request_doc['_id'] = result.inserted_id
        
        # Send email notifications in background
        background_tasks.add_task(send_partner_notification_email, request_doc, "acknowledgment")
        background_tasks.add_task(send_partner_notification_email, request_doc, "admin")
        
        logger.info(f"New partner request submitted: {request.company_name} ({request.email})")
        
        return {
            "success": True,
            "message": "Demande soumise avec succès" if request.preferred_language == "fr" else "Request submitted successfully",
            "request_id": str(result.inserted_id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting partner request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/requests", response_model=List[dict])
async def get_partner_requests(
    status: Optional[str] = None,
    partner_type: Optional[str] = None,
    search: Optional[str] = None
):
    """Get all partner requests (Admin only)"""
    try:
        query = {}
        
        if status:
            query["status"] = status
        if partner_type:
            query["partner_type"] = partner_type
        if search:
            query["$or"] = [
                {"company_name": {"$regex": search, "$options": "i"}},
                {"contact_name": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}}
            ]
        
        cursor = db.partner_requests.find(query).sort("created_at", -1)
        requests = []
        
        async for doc in cursor:
            serialized = serialize_doc(doc)
            serialized['partner_type_label'] = PARTNER_TYPE_LABELS.get(doc.get('partner_type'), {}).get('fr', doc.get('partner_type'))
            requests.append(serialized)
        
        return requests
        
    except Exception as e:
        logger.error(f"Error fetching partner requests: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/requests/{request_id}", response_model=dict)
async def get_partner_request(request_id: str):
    """Get a specific partner request"""
    try:
        doc = await db.partner_requests.find_one({"_id": ObjectId(request_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Demande non trouvée")
        
        serialized = serialize_doc(doc)
        serialized['partner_type_label'] = PARTNER_TYPE_LABELS.get(doc.get('partner_type'), {}).get('fr', doc.get('partner_type'))
        return serialized
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching partner request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/requests/{request_id}", response_model=dict)
async def update_partner_request(request_id: str, update: PartnerRequestUpdate, background_tasks: BackgroundTasks):
    """Update a partner request (Admin only)"""
    try:
        doc = await db.partner_requests.find_one({"_id": ObjectId(request_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Demande non trouvée")
        
        update_doc = {"updated_at": datetime.now(timezone.utc)}
        
        if update.status:
            update_doc["status"] = update.status.value
            if update.status in [RequestStatus.APPROVED, RequestStatus.REJECTED]:
                update_doc["reviewed_at"] = datetime.now(timezone.utc)
                update_doc["approved_at"] = datetime.now(timezone.utc) if update.status == RequestStatus.APPROVED else None
        
        if update.admin_notes is not None:
            update_doc["admin_notes"] = update.admin_notes
        
        if update.assigned_to is not None:
            update_doc["assigned_to"] = update.assigned_to
        
        await db.partner_requests.update_one(
            {"_id": ObjectId(request_id)},
            {"$set": update_doc}
        )
        
        # Send notification emails based on status change
        if update.status == RequestStatus.APPROVED:
            background_tasks.add_task(send_partner_notification_email, doc, "approved")
        elif update.status == RequestStatus.REJECTED:
            background_tasks.add_task(send_partner_notification_email, doc, "rejected")
        
        # AUTO-SYNC: Sync back to territory if this request is linked to a territory
        if doc.get('territory_id'):
            try:
                from territories import sync_partnership_to_territory
                await sync_partnership_to_territory(request_id)
                logger.info(f"Auto-synced partnership {request_id} back to territory")
            except Exception as sync_err:
                logger.warning(f"Auto-sync to territory failed: {sync_err}")
        
        logger.info(f"Partner request {request_id} updated: {update_doc}")
        
        return {"success": True, "message": "Demande mise à jour"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating partner request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/requests/{request_id}/convert", response_model=dict)
async def convert_to_partner(request_id: str, background_tasks: BackgroundTasks):
    """Convert an approved request to official partner"""
    try:
        # Get the request
        request_doc = await db.partner_requests.find_one({"_id": ObjectId(request_id)})
        if not request_doc:
            raise HTTPException(status_code=404, detail="Demande non trouvée")
        
        if request_doc.get('status') != 'approved':
            raise HTTPException(status_code=400, detail="La demande doit être approuvée avant conversion")
        
        # Check if partner already exists
        existing_partner = await db.partners.find_one({"email": request_doc.get('email')})
        if existing_partner:
            raise HTTPException(status_code=400, detail="Un partenaire avec ce courriel existe déjà")
        
        # Create partner profile
        partner_doc = {
            "company_name": request_doc.get('company_name'),
            "partner_type": request_doc.get('partner_type'),
            "contact_name": request_doc.get('contact_name'),
            "email": request_doc.get('email'),
            "phone": request_doc.get('phone'),
            "website": request_doc.get('website'),
            "description": request_doc.get('description'),
            "products_services": request_doc.get('products_services'),
            "documents": request_doc.get('documents', []),
            "preferred_language": request_doc.get('preferred_language', 'fr'),
            "address": None,
            "logo_url": None,
            "is_active": True,
            "is_verified": False,
            "commission_rate": 10.0,
            "wallet_balance": 0.0,
            "created_at": datetime.now(timezone.utc),
            "updated_at": None,
            "request_id": str(request_doc.get('_id')),
            # Dashboard features
            "features": {
                "products": True,
                "calendar": True,
                "reservations": True,
                "payments": True,
                "contracts": True,
                "tracking": True,
                "sponsored_content": False
            },
            # Stats
            "stats": {
                "total_reservations": 0,
                "pending_reservations": 0,
                "confirmed_reservations": 0,
                "total_revenue": 0.0,
                "pending_payout": 0.0,
                "total_views": 0,
                "rating": 0.0,
                "review_count": 0
            }
        }
        
        result = await db.partners.insert_one(partner_doc)
        
        # Update request status to converted
        await db.partner_requests.update_one(
            {"_id": ObjectId(request_id)},
            {"$set": {
                "status": "converted",
                "converted_at": datetime.now(timezone.utc),
                "partner_id": str(result.inserted_id)
            }}
        )
        
        # Create user account for partner
        import secrets
        temp_password = secrets.token_urlsafe(12)
        
        user_doc = {
            "email": request_doc.get('email'),
            "name": request_doc.get('contact_name'),
            "role": "partner",
            "partner_id": str(result.inserted_id),
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "temp_password": temp_password,  # Will be hashed on first login
            "must_change_password": True
        }
        
        # Check if user already exists
        existing_user = await db.users.find_one({"email": request_doc.get('email')})
        if existing_user:
            # Update existing user to partner role
            await db.users.update_one(
                {"email": request_doc.get('email')},
                {"$set": {"role": "partner", "partner_id": str(result.inserted_id)}}
            )
        else:
            await db.users.insert_one(user_doc)
        
        logger.info(f"Partner request {request_id} converted to partner {result.inserted_id}")
        
        return {
            "success": True,
            "message": "Partenaire créé avec succès",
            "partner_id": str(result.inserted_id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error converting to partner: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# API ENDPOINTS - PARTNERS
# ============================================

@router.get("/partners", response_model=List[dict])
async def get_partners(
    partner_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None
):
    """Get all official partners"""
    try:
        query = {}
        
        if partner_type:
            query["partner_type"] = partner_type
        if is_active is not None:
            query["is_active"] = is_active
        if search:
            query["$or"] = [
                {"company_name": {"$regex": search, "$options": "i"}},
                {"contact_name": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}}
            ]
        
        cursor = db.partners.find(query).sort("created_at", -1)
        partners = []
        
        async for doc in cursor:
            serialized = serialize_doc(doc)
            serialized['partner_type_label'] = PARTNER_TYPE_LABELS.get(doc.get('partner_type'), {}).get('fr', doc.get('partner_type'))
            partners.append(serialized)
        
        return partners
        
    except Exception as e:
        logger.error(f"Error fetching partners: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/partners/{partner_id}", response_model=dict)
async def get_partner(partner_id: str):
    """Get a specific partner"""
    try:
        doc = await db.partners.find_one({"_id": ObjectId(partner_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Partenaire non trouvé")
        
        serialized = serialize_doc(doc)
        serialized['partner_type_label'] = PARTNER_TYPE_LABELS.get(doc.get('partner_type'), {}).get('fr', doc.get('partner_type'))
        return serialized
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching partner: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/partners/{partner_id}", response_model=dict)
async def update_partner(partner_id: str, updates: dict):
    """Update partner profile"""
    try:
        doc = await db.partners.find_one({"_id": ObjectId(partner_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Partenaire non trouvé")
        
        # Remove protected fields
        protected_fields = ['_id', 'created_at', 'request_id', 'email']
        for field in protected_fields:
            updates.pop(field, None)
        
        updates['updated_at'] = datetime.now(timezone.utc)
        
        await db.partners.update_one(
            {"_id": ObjectId(partner_id)},
            {"$set": updates}
        )
        
        return {"success": True, "message": "Partenaire mis à jour"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating partner: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/partners/{partner_id}/toggle-status", response_model=dict)
async def toggle_partner_status(partner_id: str):
    """Toggle partner active status"""
    try:
        doc = await db.partners.find_one({"_id": ObjectId(partner_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Partenaire non trouvé")
        
        new_status = not doc.get('is_active', True)
        
        await db.partners.update_one(
            {"_id": ObjectId(partner_id)},
            {"$set": {"is_active": new_status, "updated_at": datetime.now(timezone.utc)}}
        )
        
        return {
            "success": True,
            "is_active": new_status,
            "message": f"Partenaire {'activé' if new_status else 'suspendu'}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling partner status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# API ENDPOINTS - PARTNER DASHBOARD
# ============================================

@router.get("/dashboard/{partner_id}/stats", response_model=dict)
async def get_partner_dashboard_stats(partner_id: str):
    """Get partner dashboard statistics"""
    try:
        partner = await db.partners.find_one({"_id": ObjectId(partner_id)})
        if not partner:
            raise HTTPException(status_code=404, detail="Partenaire non trouvé")
        
        # Get stats from partner document or calculate
        stats = partner.get('stats', {})
        
        # Get reservation counts
        reservations = await db.reservations.count_documents({"partner_id": partner_id})
        pending = await db.reservations.count_documents({"partner_id": partner_id, "status": "pending"})
        confirmed = await db.reservations.count_documents({"partner_id": partner_id, "status": "confirmed"})
        
        # Calculate revenue
        revenue_pipeline = [
            {"$match": {"partner_id": partner_id, "status": {"$in": ["confirmed", "completed"]}}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        revenue_result = await db.reservations.aggregate(revenue_pipeline).to_list(1)
        total_revenue = revenue_result[0]['total'] if revenue_result else 0
        
        return {
            "total_reservations": reservations,
            "pending_reservations": pending,
            "confirmed_reservations": confirmed,
            "total_revenue": total_revenue,
            "wallet_balance": partner.get('wallet_balance', 0),
            "pending_payout": stats.get('pending_payout', 0),
            "total_views": stats.get('total_views', 0),
            "rating": stats.get('rating', 0),
            "review_count": stats.get('review_count', 0),
            "commission_rate": partner.get('commission_rate', 10)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching partner stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# API ENDPOINTS - ADMIN STATS
# ============================================

@router.get("/admin/stats", response_model=dict)
async def get_partnership_admin_stats():
    """Get partnership admin statistics"""
    try:
        # Request stats
        total_requests = await db.partner_requests.count_documents({})
        pending_requests = await db.partner_requests.count_documents({"status": "pending"})
        approved_requests = await db.partner_requests.count_documents({"status": "approved"})
        rejected_requests = await db.partner_requests.count_documents({"status": "rejected"})
        converted_requests = await db.partner_requests.count_documents({"status": "converted"})
        
        # Partner stats
        total_partners = await db.partners.count_documents({})
        active_partners = await db.partners.count_documents({"is_active": True})
        verified_partners = await db.partners.count_documents({"is_verified": True})
        
        # By type stats
        type_stats = []
        for pt in PartnerType:
            count = await db.partners.count_documents({"partner_type": pt.value})
            if count > 0:
                type_stats.append({
                    "type": pt.value,
                    "label": PARTNER_TYPE_LABELS[pt.value]["fr"],
                    "count": count
                })
        
        return {
            "requests": {
                "total": total_requests,
                "pending": pending_requests,
                "approved": approved_requests,
                "rejected": rejected_requests,
                "converted": converted_requests
            },
            "partners": {
                "total": total_partners,
                "active": active_partners,
                "verified": verified_partners
            },
            "by_type": type_stats
        }
        
    except Exception as e:
        logger.error(f"Error fetching partnership stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# API ENDPOINTS - EMAIL SETTINGS
# ============================================

class EmailSettingsUpdate(BaseModel):
    """Email settings update model"""
    acknowledgment_enabled: Optional[bool] = None
    admin_notification_enabled: Optional[bool] = None
    approval_enabled: Optional[bool] = None
    rejection_enabled: Optional[bool] = None


@router.get("/admin/email-settings", response_model=dict)
async def get_partnership_email_settings():
    """Get partnership email notification settings"""
    try:
        settings = await get_email_settings()
        return {
            "success": True,
            "settings": settings
        }
    except Exception as e:
        logger.error(f"Error fetching email settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/admin/email-settings", response_model=dict)
async def update_partnership_email_settings(settings: EmailSettingsUpdate):
    """Update partnership email notification settings"""
    try:
        update_doc = {"updated_at": datetime.now(timezone.utc)}
        
        if settings.acknowledgment_enabled is not None:
            update_doc["acknowledgment_enabled"] = settings.acknowledgment_enabled
        if settings.admin_notification_enabled is not None:
            update_doc["admin_notification_enabled"] = settings.admin_notification_enabled
        if settings.approval_enabled is not None:
            update_doc["approval_enabled"] = settings.approval_enabled
        if settings.rejection_enabled is not None:
            update_doc["rejection_enabled"] = settings.rejection_enabled
        
        await db[EMAIL_SETTINGS_COLLECTION].update_one(
            {"_id": "email_settings"},
            {"$set": update_doc},
            upsert=True
        )
        
        # Get updated settings
        new_settings = await get_email_settings()
        
        logger.info(f"Email settings updated: {update_doc}")
        
        return {
            "success": True,
            "message": "Paramètres d'email mis à jour",
            "settings": new_settings
        }
        
    except Exception as e:
        logger.error(f"Error updating email settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/email-settings/toggle/{setting_type}", response_model=dict)
async def toggle_email_setting(setting_type: str):
    """Toggle a specific email setting ON/OFF"""
    try:
        valid_types = ["acknowledgment", "admin_notification", "approval", "rejection"]
        if setting_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Type invalide. Types valides: {valid_types}")
        
        setting_key = f"{setting_type}_enabled"
        
        # Get current setting
        current_settings = await get_email_settings()
        current_value = current_settings.get(setting_key, True)
        new_value = not current_value
        
        # Update
        await db[EMAIL_SETTINGS_COLLECTION].update_one(
            {"_id": "email_settings"},
            {"$set": {
                setting_key: new_value,
                "updated_at": datetime.now(timezone.utc)
            }},
            upsert=True
        )
        
        logger.info(f"Email setting '{setting_type}' toggled to {new_value}")
        
        return {
            "success": True,
            "setting": setting_type,
            "enabled": new_value,
            "message": f"Email '{setting_type}' {'activé' if new_value else 'désactivé'}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling email setting: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# API ENDPOINTS - OFFERS (Partner Services)
# ============================================

@router.post("/offers", response_model=dict)
async def create_offer(offer: OfferCreate, partner_id: str):
    """Create a new offer/service for a partner"""
    try:
        # Verify partner exists
        partner = await db.partners.find_one({"_id": ObjectId(partner_id)})
        if not partner:
            raise HTTPException(status_code=404, detail="Partenaire non trouvé")
        
        offer_doc = {
            "partner_id": partner_id,
            "title": offer.title,
            "description": offer.description,
            "offer_type": offer.offer_type,
            "category": offer.category,
            "price": offer.price,
            "price_unit": offer.price_unit,
            "max_guests": offer.max_guests,
            "location": offer.location,
            "coordinates": offer.coordinates,
            "images": offer.images or [],
            "species": offer.species or [],
            "amenities": offer.amenities or [],
            "rules": offer.rules,
            "is_active": offer.is_active,
            "created_at": datetime.now(timezone.utc),
            "updated_at": None,
            "views": 0,
            "reservations_count": 0,
            "rating": 0.0,
            "review_count": 0
        }
        
        result = await db.partner_offers.insert_one(offer_doc)
        logger.info(f"New offer created: {offer.title} for partner {partner_id}")
        
        return {
            "success": True,
            "offer_id": str(result.inserted_id),
            "message": "Offre créée avec succès"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating offer: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/offers", response_model=List[dict])
async def get_offers(
    partner_id: Optional[str] = None,
    offer_type: Optional[str] = None,
    species: Optional[str] = None,
    is_active: bool = True
):
    """Get offers with optional filters"""
    try:
        query = {"is_active": is_active}
        
        if partner_id:
            query["partner_id"] = partner_id
        if offer_type:
            query["offer_type"] = offer_type
        if species:
            query["species"] = species
        
        cursor = db.partner_offers.find(query).sort("created_at", -1)
        offers = []
        
        async for doc in cursor:
            serialized = serialize_doc(doc)
            # Get partner info
            partner = await db.partners.find_one({"_id": ObjectId(doc.get("partner_id"))})
            if partner:
                serialized["partner_name"] = partner.get("company_name")
                serialized["partner_type"] = partner.get("partner_type")
            offers.append(serialized)
        
        return offers
        
    except Exception as e:
        logger.error(f"Error fetching offers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/offers/{offer_id}", response_model=dict)
async def get_offer(offer_id: str):
    """Get a specific offer with availability"""
    try:
        offer = await db.partner_offers.find_one({"_id": ObjectId(offer_id)})
        if not offer:
            raise HTTPException(status_code=404, detail="Offre non trouvée")
        
        # Increment view count
        await db.partner_offers.update_one(
            {"_id": ObjectId(offer_id)},
            {"$inc": {"views": 1}}
        )
        
        serialized = serialize_doc(offer)
        
        # Get partner info
        partner = await db.partners.find_one({"_id": ObjectId(offer.get("partner_id"))})
        if partner:
            serialized["partner"] = {
                "id": str(partner["_id"]),
                "name": partner.get("company_name"),
                "type": partner.get("partner_type"),
                "phone": partner.get("phone"),
                "email": partner.get("email"),
                "rating": partner.get("stats", {}).get("rating", 0)
            }
        
        return serialized
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching offer: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/offers/{offer_id}", response_model=dict)
async def update_offer(offer_id: str, updates: dict):
    """Update an offer"""
    try:
        offer = await db.partner_offers.find_one({"_id": ObjectId(offer_id)})
        if not offer:
            raise HTTPException(status_code=404, detail="Offre non trouvée")
        
        # Remove protected fields
        protected = ["_id", "partner_id", "created_at", "views", "reservations_count"]
        for field in protected:
            updates.pop(field, None)
        
        updates["updated_at"] = datetime.now(timezone.utc)
        
        await db.partner_offers.update_one(
            {"_id": ObjectId(offer_id)},
            {"$set": updates}
        )
        
        return {"success": True, "message": "Offre mise à jour"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating offer: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# API ENDPOINTS - DYNAMIC CALENDAR
# ============================================

@router.post("/availability", response_model=dict)
async def set_availability(availability: AvailabilityCreate):
    """Set availability for a specific date"""
    try:
        # Verify offer exists
        offer = await db.partner_offers.find_one({"_id": ObjectId(availability.offer_id)})
        if not offer:
            raise HTTPException(status_code=404, detail="Offre non trouvée")
        
        # Check for existing availability
        existing = await db.availability.find_one({
            "offer_id": availability.offer_id,
            "date": availability.date
        })
        
        if existing:
            # Update existing
            await db.availability.update_one(
                {"_id": existing["_id"]},
                {"$set": {
                    "status": availability.status.value,
                    "price_override": availability.price_override,
                    "quota": availability.quota,
                    "notes": availability.notes,
                    "updated_at": datetime.now(timezone.utc)
                }}
            )
            return {"success": True, "message": "Disponibilité mise à jour"}
        else:
            # Create new
            doc = {
                "offer_id": availability.offer_id,
                "partner_id": offer.get("partner_id"),
                "date": availability.date,
                "status": availability.status.value,
                "price_override": availability.price_override,
                "quota": availability.quota,
                "notes": availability.notes,
                "created_at": datetime.now(timezone.utc)
            }
            await db.availability.insert_one(doc)
            return {"success": True, "message": "Disponibilité créée"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting availability: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/availability/bulk", response_model=dict)
async def set_bulk_availability(bulk: AvailabilityBulkCreate):
    """Set availability for a date range"""
    try:
        from datetime import timedelta
        
        offer = await db.partner_offers.find_one({"_id": ObjectId(bulk.offer_id)})
        if not offer:
            raise HTTPException(status_code=404, detail="Offre non trouvée")
        
        start = datetime.strptime(bulk.start_date, "%Y-%m-%d")
        end = datetime.strptime(bulk.end_date, "%Y-%m-%d")
        
        if end < start:
            raise HTTPException(status_code=400, detail="Date de fin avant date de début")
        
        created = 0
        updated = 0
        current = start
        
        while current <= end:
            # Check excluded days (0=Monday, 6=Sunday)
            if current.weekday() not in (bulk.exclude_days or []):
                date_str = current.strftime("%Y-%m-%d")
                
                existing = await db.availability.find_one({
                    "offer_id": bulk.offer_id,
                    "date": date_str
                })
                
                if existing:
                    await db.availability.update_one(
                        {"_id": existing["_id"]},
                        {"$set": {
                            "status": bulk.status.value,
                            "price_override": bulk.price_override,
                            "updated_at": datetime.now(timezone.utc)
                        }}
                    )
                    updated += 1
                else:
                    await db.availability.insert_one({
                        "offer_id": bulk.offer_id,
                        "partner_id": offer.get("partner_id"),
                        "date": date_str,
                        "status": bulk.status.value,
                        "price_override": bulk.price_override,
                        "created_at": datetime.now(timezone.utc)
                    })
                    created += 1
            
            current += timedelta(days=1)
        
        return {
            "success": True,
            "created": created,
            "updated": updated,
            "message": f"{created} créées, {updated} mises à jour"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting bulk availability: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/availability/{offer_id}", response_model=List[dict])
async def get_availability(
    offer_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get availability calendar for an offer"""
    try:
        query = {"offer_id": offer_id}
        
        if start_date:
            query["date"] = {"$gte": start_date}
        if end_date:
            if "date" in query:
                query["date"]["$lte"] = end_date
            else:
                query["date"] = {"$lte": end_date}
        
        cursor = db.availability.find(query).sort("date", 1)
        availability = []
        
        async for doc in cursor:
            availability.append({
                "date": doc.get("date"),
                "status": doc.get("status"),
                "price_override": doc.get("price_override"),
                "quota": doc.get("quota"),
                "notes": doc.get("notes")
            })
        
        return availability
        
    except Exception as e:
        logger.error(f"Error fetching availability: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# API ENDPOINTS - RESERVATIONS
# ============================================

@router.post("/reservations", response_model=dict)
async def create_reservation(reservation: ReservationCreate, background_tasks: BackgroundTasks):
    """Create a new reservation request"""
    try:
        # Verify offer exists
        offer = await db.partner_offers.find_one({"_id": ObjectId(reservation.offer_id)})
        if not offer:
            raise HTTPException(status_code=404, detail="Offre non trouvée")
        
        # Check availability for all dates
        for date in reservation.dates:
            avail = await db.availability.find_one({
                "offer_id": reservation.offer_id,
                "date": date
            })
            if avail and avail.get("status") not in ["available", None]:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Date {date} non disponible"
                )
        
        # Calculate total price
        base_price = offer.get("price", 0)
        total_days = len(reservation.dates)
        total_price = base_price * total_days * (reservation.guests or 1)
        
        # Get partner
        partner = await db.partners.find_one({"_id": ObjectId(reservation.partner_id)})
        commission_rate = partner.get("commission_rate", 10) if partner else 10
        commission = total_price * (commission_rate / 100)
        partner_amount = total_price - commission
        
        # Create reservation
        reservation_doc = {
            "offer_id": reservation.offer_id,
            "partner_id": reservation.partner_id,
            "offer_title": offer.get("title"),
            "dates": reservation.dates,
            "guests": reservation.guests,
            "client_name": reservation.client_name,
            "client_email": reservation.client_email,
            "client_phone": reservation.client_phone,
            "notes": reservation.notes,
            "status": "pending",
            "total_price": total_price,
            "commission": commission,
            "partner_amount": partner_amount,
            "created_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + timedelta(hours=48),
            "confirmed_at": None,
            "cancelled_at": None,
            "completed_at": None
        }
        
        result = await db.reservations.insert_one(reservation_doc)
        
        # Block dates temporarily
        for date in reservation.dates:
            await db.availability.update_one(
                {"offer_id": reservation.offer_id, "date": date},
                {"$set": {"status": "pending", "reservation_id": str(result.inserted_id)}},
                upsert=True
            )
        
        # TODO: Send notification emails
        # background_tasks.add_task(send_reservation_notification, reservation_doc, "new")
        
        logger.info(f"New reservation created: {result.inserted_id}")
        
        return {
            "success": True,
            "reservation_id": str(result.inserted_id),
            "total_price": total_price,
            "expires_at": reservation_doc["expires_at"].isoformat(),
            "message": "Réservation créée - En attente de confirmation du partenaire"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating reservation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reservations", response_model=List[dict])
async def get_reservations(
    partner_id: Optional[str] = None,
    client_email: Optional[str] = None,
    status: Optional[str] = None
):
    """Get reservations with filters"""
    try:
        query = {}
        
        if partner_id:
            query["partner_id"] = partner_id
        if client_email:
            query["client_email"] = client_email
        if status:
            query["status"] = status
        
        cursor = db.reservations.find(query).sort("created_at", -1)
        reservations = []
        
        async for doc in cursor:
            serialized = serialize_doc(doc)
            reservations.append(serialized)
        
        return reservations
        
    except Exception as e:
        logger.error(f"Error fetching reservations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reservations/{reservation_id}", response_model=dict)
async def get_reservation(reservation_id: str):
    """Get a specific reservation"""
    try:
        reservation = await db.reservations.find_one({"_id": ObjectId(reservation_id)})
        if not reservation:
            raise HTTPException(status_code=404, detail="Réservation non trouvée")
        
        return serialize_doc(reservation)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching reservation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reservations/{reservation_id}/respond", response_model=dict)
async def respond_to_reservation(
    reservation_id: str, 
    response: ReservationResponse,
    background_tasks: BackgroundTasks
):
    """Partner responds to reservation (confirm/cancel)"""
    try:
        reservation = await db.reservations.find_one({"_id": ObjectId(reservation_id)})
        if not reservation:
            raise HTTPException(status_code=404, detail="Réservation non trouvée")
        
        if reservation.get("status") != "pending":
            raise HTTPException(status_code=400, detail="Cette réservation ne peut plus être modifiée")
        
        update_doc = {"updated_at": datetime.now(timezone.utc)}
        
        if response.action == "confirm":
            update_doc["status"] = "confirmed"
            update_doc["confirmed_at"] = datetime.now(timezone.utc)
            
            # Lock the dates
            for date in reservation.get("dates", []):
                await db.availability.update_one(
                    {"offer_id": reservation.get("offer_id"), "date": date},
                    {"$set": {"status": "reserved"}}
                )
            
            # Update partner stats
            await db.partners.update_one(
                {"_id": ObjectId(reservation.get("partner_id"))},
                {"$inc": {
                    "stats.total_reservations": 1,
                    "stats.confirmed_reservations": 1
                }}
            )
            
            message = "Réservation confirmée"
            
        elif response.action == "cancel":
            update_doc["status"] = "cancelled"
            update_doc["cancelled_at"] = datetime.now(timezone.utc)
            update_doc["cancellation_reason"] = response.notes
            
            # Release the dates
            for date in reservation.get("dates", []):
                await db.availability.update_one(
                    {"offer_id": reservation.get("offer_id"), "date": date},
                    {"$set": {"status": "available", "reservation_id": None}}
                )
            
            message = "Réservation annulée"
            
        elif response.action == "complete":
            if reservation.get("status") != "confirmed":
                raise HTTPException(status_code=400, detail="La réservation doit être confirmée")
            
            update_doc["status"] = "completed"
            update_doc["completed_at"] = datetime.now(timezone.utc)
            
            # Add revenue to partner wallet
            await db.partners.update_one(
                {"_id": ObjectId(reservation.get("partner_id"))},
                {"$inc": {
                    "wallet_balance": reservation.get("partner_amount", 0),
                    "stats.total_revenue": reservation.get("total_price", 0)
                }}
            )
            
            message = "Réservation complétée - Paiement ajouté au portefeuille"
        else:
            raise HTTPException(status_code=400, detail="Action invalide")
        
        await db.reservations.update_one(
            {"_id": ObjectId(reservation_id)},
            {"$set": update_doc}
        )
        
        # TODO: Send notification emails
        # background_tasks.add_task(send_reservation_notification, reservation, response.action)
        
        return {"success": True, "message": message}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error responding to reservation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# API ENDPOINTS - PARTNER CALENDAR VIEW
# ============================================

@router.get("/calendar/{partner_id}", response_model=dict)
async def get_partner_calendar(
    partner_id: str,
    year: int,
    month: int
):
    """Get partner calendar with all offers and reservations for a month"""
    try:
        from calendar import monthrange
        
        # Get all offers for this partner
        offers = await db.partner_offers.find({"partner_id": partner_id, "is_active": True}).to_list(100)
        
        # Calculate date range
        _, last_day = monthrange(year, month)
        start_date = f"{year}-{month:02d}-01"
        end_date = f"{year}-{month:02d}-{last_day:02d}"
        
        # Get availability for all offers
        availability_map = {}
        for offer in offers:
            offer_id = str(offer["_id"])
            avails = await db.availability.find({
                "offer_id": offer_id,
                "date": {"$gte": start_date, "$lte": end_date}
            }).to_list(100)
            
            for av in avails:
                date = av.get("date")
                if date not in availability_map:
                    availability_map[date] = []
                availability_map[date].append({
                    "offer_id": offer_id,
                    "offer_title": offer.get("title"),
                    "status": av.get("status"),
                    "price_override": av.get("price_override")
                })
        
        # Get reservations for this month
        reservations = await db.reservations.find({
            "partner_id": partner_id,
            "dates": {"$elemMatch": {"$gte": start_date, "$lte": end_date}}
        }).to_list(100)
        
        reservations_by_date = {}
        for res in reservations:
            for date in res.get("dates", []):
                if start_date <= date <= end_date:
                    if date not in reservations_by_date:
                        reservations_by_date[date] = []
                    reservations_by_date[date].append({
                        "id": str(res["_id"]),
                        "offer_title": res.get("offer_title"),
                        "client_name": res.get("client_name"),
                        "status": res.get("status"),
                        "guests": res.get("guests")
                    })
        
        return {
            "year": year,
            "month": month,
            "offers": [{"id": str(o["_id"]), "title": o.get("title")} for o in offers],
            "availability": availability_map,
            "reservations": reservations_by_date
        }
        
    except Exception as e:
        logger.error(f"Error fetching partner calendar: {e}")
        raise HTTPException(status_code=500, detail=str(e))



# ============================================
# API ENDPOINTS - IMPORT TERRITORIES AS PARTNERS
# ============================================

@router.post("/import-territories", response_model=dict)
async def import_territories_as_partners():
    """
    Import all territories from the inventory as potential partner requests.
    This creates partnership applications from the territory data for easy management.
    """
    try:
        # Get all territories
        territories = await db.territories.find({}).to_list(1000)
        
        if not territories:
            return {
                "success": False,
                "message": "Aucun territoire trouvé à importer",
                "imported": 0
            }
        
        imported = 0
        updated = 0
        skipped = 0
        
        for territory in territories:
            territory_id = str(territory.get('_id'))
            
            # Check if already imported
            existing = await db.partner_requests.find_one({
                "territory_id": territory_id
            })
            
            if existing:
                # Update existing request with latest territory data
                await db.partner_requests.update_one(
                    {"territory_id": territory_id},
                    {"$set": {
                        "company_name": territory.get('name'),
                        "website": territory.get('website'),
                        "region": territory.get('region'),
                        "province": territory.get('province'),
                        "species": territory.get('species', []),
                        "services": territory.get('services', {}),
                        "scoring": territory.get('scoring', {}),
                        "coordinates": territory.get('coordinates'),
                        "updated_at": datetime.now(timezone.utc),
                        "last_sync": datetime.now(timezone.utc)
                    }}
                )
                updated += 1
                continue
            
            # Determine partner type based on establishment_type
            establishment_type = territory.get('establishment_type', 'pourvoirie')
            partner_type_map = {
                'pourvoirie': 'pourvoiries',
                'sepaq': 'pourvoiries',
                'zec': 'zec',
                'club': 'clubs',
                'outfitter': 'pourvoiries',
                'reserve': 'pourvoiries',
                'anticosti': 'pourvoiries',
                'private': 'proprietaires'
            }
            partner_type = partner_type_map.get(establishment_type, 'pourvoiries')
            
            # Create partner request from territory
            request_doc = {
                "territory_id": territory_id,
                "company_name": territory.get('name'),
                "partner_type": partner_type,
                "contact_name": territory.get('contact', {}).get('name', 'À contacter'),
                "email": territory.get('contact', {}).get('email', ''),
                "phone": territory.get('contact', {}).get('phone', ''),
                "website": territory.get('website'),
                "description": territory.get('description', f"Territoire de chasse - {territory.get('name')}"),
                "products_services": f"Type: {establishment_type.upper()}, Espèces: {', '.join(territory.get('species', []))}",
                "documents": [],
                "legal_consent": True,
                "preferred_language": "fr",
                "status": "pending",
                "source": "territory_import",
                "created_at": datetime.now(timezone.utc),
                "updated_at": None,
                "admin_notes": f"Importé depuis l'inventaire des territoires. Score BIONIC™: {territory.get('scoring', {}).get('global_score', 'N/D')}",
                "assigned_to": None,
                "reviewed_at": None,
                "reviewed_by": None,
                # Extra territory data
                "region": territory.get('region'),
                "province": territory.get('province'),
                "establishment_type": establishment_type,
                "species": territory.get('species', []),
                "hunting_zones": territory.get('hunting_zones', []),
                "services": territory.get('services', {}),
                "scoring": territory.get('scoring', {}),
                "coordinates": territory.get('coordinates'),
                "is_verified": territory.get('is_verified', False),
                "is_partner": territory.get('is_partner', False),
                "last_sync": datetime.now(timezone.utc)
            }
            
            await db.partner_requests.insert_one(request_doc)
            imported += 1
        
        logger.info(f"Territory import completed: {imported} imported, {updated} updated, {skipped} skipped")
        
        return {
            "success": True,
            "message": f"Import terminé: {imported} nouveaux partenaires, {updated} mis à jour",
            "imported": imported,
            "updated": updated,
            "skipped": skipped,
            "total_territories": len(territories)
        }
        
    except Exception as e:
        logger.error(f"Error importing territories as partners: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/territory-partners", response_model=dict)
async def get_territory_partners():
    """
    Get all partner requests that were imported from territories,
    with full territory details for management.
    """
    try:
        # Get all partner requests with territory_id
        cursor = db.partner_requests.find({"territory_id": {"$exists": True}}).sort("created_at", -1)
        
        partners = []
        async for doc in cursor:
            # Serialize ObjectId
            serialized = {k: str(v) if isinstance(v, ObjectId) else v for k, v in doc.items() if k != '_id'}
            serialized['id'] = str(doc['_id'])
            partners.append(serialized)
        
        # Get stats
        total = len(partners)
        pending = len([p for p in partners if p.get('status') == 'pending'])
        approved = len([p for p in partners if p.get('status') == 'approved'])
        converted = len([p for p in partners if p.get('status') == 'converted'])
        
        # By type
        by_type = {}
        for p in partners:
            ptype = p.get('partner_type', 'autres')
            by_type[ptype] = by_type.get(ptype, 0) + 1
        
        # By province
        by_province = {}
        for p in partners:
            prov = p.get('province', 'N/D')
            by_province[prov] = by_province.get(prov, 0) + 1
        
        return {
            "success": True,
            "partners": partners,
            "stats": {
                "total": total,
                "pending": pending,
                "approved": approved,
                "converted": converted,
                "by_type": by_type,
                "by_province": by_province
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching territory partners: {e}")
        raise HTTPException(status_code=500, detail=str(e))
