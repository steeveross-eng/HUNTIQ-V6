"""
Partners Admin Service - V5-ULTIME Administration Premium
=========================================================

Service d'administration des partenaires:
- Dashboard et statistiques partenaires
- Gestion des demandes de partenariat
- Gestion des partenaires officiels
- Types de partenaires (11 catégories)
- Conversion demandes → partenaires
- Configuration des emails

Module isolé - aucun import croisé.
Phase 6 Migration - Partenaires & Branding.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional
import logging
import uuid

logger = logging.getLogger(__name__)


class PartnersAdminService:
    """Service isolé pour l'administration des partenaires"""
    
    # Types de partenaires
    PARTNER_TYPES = {
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
    
    # Statuts des demandes
    REQUEST_STATUSES = ["pending", "reviewed", "approved", "rejected", "converted"]
    
    # ============ DASHBOARD & STATS ============
    @staticmethod
    async def get_dashboard_stats(db) -> dict:
        """Statistiques globales des partenaires"""
        try:
            # Stats demandes
            total_requests = await db.partner_requests.count_documents({})
            pending_requests = await db.partner_requests.count_documents({"status": "pending"})
            approved_requests = await db.partner_requests.count_documents({"status": "approved"})
            rejected_requests = await db.partner_requests.count_documents({"status": "rejected"})
            converted_requests = await db.partner_requests.count_documents({"status": "converted"})
            
            # Stats partenaires
            total_partners = await db.partners.count_documents({})
            active_partners = await db.partners.count_documents({"is_active": True})
            verified_partners = await db.partners.count_documents({"is_verified": True})
            
            # Par type
            by_type = {}
            for ptype in PartnersAdminService.PARTNER_TYPES.keys():
                count = await db.partners.count_documents({"partner_type": ptype})
                if count > 0:
                    by_type[ptype] = {
                        "count": count,
                        "label": PartnersAdminService.PARTNER_TYPES[ptype]["fr"]
                    }
            
            # Revenus et commissions
            partners = await db.partners.find({}, {"commission_rate": 1, "wallet_balance": 1, "_id": 0}).to_list(1000)
            total_wallet = sum(p.get("wallet_balance", 0) for p in partners)
            avg_commission = sum(p.get("commission_rate", 10) for p in partners) / max(len(partners), 1)
            
            # Récents (7 jours)
            seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
            recent_requests = await db.partner_requests.count_documents({
                "created_at": {"$gte": seven_days_ago}
            })
            
            return {
                "success": True,
                "stats": {
                    "requests": {
                        "total": total_requests,
                        "pending": pending_requests,
                        "approved": approved_requests,
                        "rejected": rejected_requests,
                        "converted": converted_requests,
                        "recent_7d": recent_requests
                    },
                    "partners": {
                        "total": total_partners,
                        "active": active_partners,
                        "verified": verified_partners
                    },
                    "by_type": by_type,
                    "financial": {
                        "total_wallet": round(total_wallet, 2),
                        "avg_commission": round(avg_commission, 1)
                    }
                }
            }
        except Exception as e:
            logger.error(f"Error in get_dashboard_stats: {e}")
            return {"success": False, "error": str(e)}
    
    # ============ PARTNER TYPES ============
    @staticmethod
    async def get_partner_types(db) -> dict:
        """Liste des types de partenaires"""
        return {
            "success": True,
            "types": [
                {"id": k, "label_fr": v["fr"], "label_en": v["en"]}
                for k, v in PartnersAdminService.PARTNER_TYPES.items()
            ]
        }
    
    # ============ REQUESTS MANAGEMENT ============
    @staticmethod
    async def get_requests(db, status: Optional[str] = None, 
                          partner_type: Optional[str] = None,
                          search: Optional[str] = None,
                          limit: int = 50) -> dict:
        """Liste des demandes de partenariat"""
        try:
            query = {}
            if status and status != 'all':
                query["status"] = status
            if partner_type and partner_type != 'all':
                query["partner_type"] = partner_type
            if search:
                query["$or"] = [
                    {"company_name": {"$regex": search, "$options": "i"}},
                    {"contact_name": {"$regex": search, "$options": "i"}},
                    {"email": {"$regex": search, "$options": "i"}}
                ]
            
            requests = await db.partner_requests.find(
                query, {"_id": 0}
            ).sort("created_at", -1).limit(limit).to_list(limit)
            
            # Ajouter labels
            for req in requests:
                ptype = req.get("partner_type")
                if ptype in PartnersAdminService.PARTNER_TYPES:
                    req["partner_type_label"] = PartnersAdminService.PARTNER_TYPES[ptype]["fr"]
            
            total = await db.partner_requests.count_documents(query)
            
            return {
                "success": True,
                "total": total,
                "requests": requests
            }
        except Exception as e:
            logger.error(f"Error in get_requests: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def get_request_detail(db, request_id: str) -> dict:
        """Détail d'une demande"""
        try:
            request = await db.partner_requests.find_one({"id": request_id}, {"_id": 0})
            if not request:
                return {"success": False, "error": "Demande non trouvée"}
            
            ptype = request.get("partner_type")
            if ptype in PartnersAdminService.PARTNER_TYPES:
                request["partner_type_label"] = PartnersAdminService.PARTNER_TYPES[ptype]["fr"]
            
            return {
                "success": True,
                "request": request
            }
        except Exception as e:
            logger.error(f"Error in get_request_detail: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def update_request_status(db, request_id: str, status: str, admin_notes: str = None) -> dict:
        """Mettre à jour le statut d'une demande"""
        if status not in PartnersAdminService.REQUEST_STATUSES:
            return {"success": False, "error": f"Statut invalide. Valides: {PartnersAdminService.REQUEST_STATUSES}"}
        
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            if admin_notes is not None:
                update_data["admin_notes"] = admin_notes
            
            if status in ["approved", "rejected"]:
                update_data["reviewed_at"] = datetime.now(timezone.utc).isoformat()
            
            result = await db.partner_requests.update_one(
                {"id": request_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return {"success": False, "error": "Demande non trouvée"}
            
            return {"success": True, "status": status, "message": f"Statut mis à jour: {status}"}
        except Exception as e:
            logger.error(f"Error in update_request_status: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def convert_to_partner(db, request_id: str) -> dict:
        """Convertir une demande approuvée en partenaire officiel"""
        try:
            # Récupérer la demande
            request = await db.partner_requests.find_one({"id": request_id})
            if not request:
                return {"success": False, "error": "Demande non trouvée"}
            
            if request.get("status") != "approved":
                return {"success": False, "error": "La demande doit être approuvée avant conversion"}
            
            # Vérifier si partenaire existe déjà
            existing = await db.partners.find_one({"email": request.get("email")})
            if existing:
                return {"success": False, "error": "Un partenaire avec cet email existe déjà"}
            
            # Créer le partenaire
            partner_id = str(uuid.uuid4())
            partner = {
                "id": partner_id,
                "company_name": request.get("company_name"),
                "partner_type": request.get("partner_type"),
                "contact_name": request.get("contact_name"),
                "email": request.get("email"),
                "phone": request.get("phone"),
                "website": request.get("website"),
                "description": request.get("description"),
                "products_services": request.get("products_services"),
                "documents": request.get("documents", []),
                "preferred_language": request.get("preferred_language", "fr"),
                "address": None,
                "logo_url": None,
                "is_active": True,
                "is_verified": False,
                "commission_rate": 10.0,
                "wallet_balance": 0.0,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "request_id": request_id,
                "stats": {
                    "total_reservations": 0,
                    "confirmed_reservations": 0,
                    "total_revenue": 0.0,
                    "rating": 0.0,
                    "review_count": 0
                }
            }
            
            await db.partners.insert_one(partner)
            
            # Mettre à jour la demande
            await db.partner_requests.update_one(
                {"id": request_id},
                {"$set": {
                    "status": "converted",
                    "converted_at": datetime.now(timezone.utc).isoformat(),
                    "partner_id": partner_id
                }}
            )
            
            return {
                "success": True,
                "partner_id": partner_id,
                "message": "Partenaire créé avec succès"
            }
        except Exception as e:
            logger.error(f"Error in convert_to_partner: {e}")
            return {"success": False, "error": str(e)}
    
    # ============ PARTNERS MANAGEMENT ============
    @staticmethod
    async def get_partners(db, partner_type: Optional[str] = None,
                          is_active: Optional[bool] = None,
                          search: Optional[str] = None,
                          limit: int = 50) -> dict:
        """Liste des partenaires officiels"""
        try:
            query = {}
            if partner_type and partner_type != 'all':
                query["partner_type"] = partner_type
            if is_active is not None:
                query["is_active"] = is_active
            if search:
                query["$or"] = [
                    {"company_name": {"$regex": search, "$options": "i"}},
                    {"contact_name": {"$regex": search, "$options": "i"}},
                    {"email": {"$regex": search, "$options": "i"}}
                ]
            
            partners = await db.partners.find(
                query, {"_id": 0}
            ).sort("created_at", -1).limit(limit).to_list(limit)
            
            # Ajouter labels
            for p in partners:
                ptype = p.get("partner_type")
                if ptype in PartnersAdminService.PARTNER_TYPES:
                    p["partner_type_label"] = PartnersAdminService.PARTNER_TYPES[ptype]["fr"]
            
            total = await db.partners.count_documents(query)
            
            return {
                "success": True,
                "total": total,
                "partners": partners
            }
        except Exception as e:
            logger.error(f"Error in get_partners: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def get_partner_detail(db, partner_id: str) -> dict:
        """Détail d'un partenaire"""
        try:
            partner = await db.partners.find_one({"id": partner_id}, {"_id": 0})
            if not partner:
                return {"success": False, "error": "Partenaire non trouvé"}
            
            ptype = partner.get("partner_type")
            if ptype in PartnersAdminService.PARTNER_TYPES:
                partner["partner_type_label"] = PartnersAdminService.PARTNER_TYPES[ptype]["fr"]
            
            # Récupérer les offres du partenaire
            offers = await db.partner_offers.find(
                {"partner_id": partner_id}, {"_id": 0}
            ).to_list(50)
            
            return {
                "success": True,
                "partner": partner,
                "offers": offers
            }
        except Exception as e:
            logger.error(f"Error in get_partner_detail: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def update_partner(db, partner_id: str, updates: dict) -> dict:
        """Mettre à jour un partenaire"""
        try:
            # Champs protégés
            protected = ["id", "created_at", "request_id", "email"]
            for field in protected:
                updates.pop(field, None)
            
            updates["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            result = await db.partners.update_one(
                {"id": partner_id},
                {"$set": updates}
            )
            
            if result.matched_count == 0:
                return {"success": False, "error": "Partenaire non trouvé"}
            
            return {"success": True, "message": "Partenaire mis à jour"}
        except Exception as e:
            logger.error(f"Error in update_partner: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def toggle_partner_status(db, partner_id: str) -> dict:
        """Activer/désactiver un partenaire"""
        try:
            partner = await db.partners.find_one({"id": partner_id})
            if not partner:
                return {"success": False, "error": "Partenaire non trouvé"}
            
            new_status = not partner.get("is_active", True)
            
            await db.partners.update_one(
                {"id": partner_id},
                {"$set": {"is_active": new_status, "updated_at": datetime.now(timezone.utc).isoformat()}}
            )
            
            return {
                "success": True,
                "is_active": new_status,
                "message": f"Partenaire {'activé' if new_status else 'suspendu'}"
            }
        except Exception as e:
            logger.error(f"Error in toggle_partner_status: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def verify_partner(db, partner_id: str, verified: bool) -> dict:
        """Vérifier/dévérifier un partenaire"""
        try:
            result = await db.partners.update_one(
                {"id": partner_id},
                {"$set": {"is_verified": verified, "updated_at": datetime.now(timezone.utc).isoformat()}}
            )
            
            if result.matched_count == 0:
                return {"success": False, "error": "Partenaire non trouvé"}
            
            return {
                "success": True,
                "is_verified": verified,
                "message": f"Partenaire {'vérifié' if verified else 'non vérifié'}"
            }
        except Exception as e:
            logger.error(f"Error in verify_partner: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def update_commission_rate(db, partner_id: str, rate: float) -> dict:
        """Mettre à jour le taux de commission"""
        if rate < 0 or rate > 100:
            return {"success": False, "error": "Taux doit être entre 0 et 100"}
        
        try:
            result = await db.partners.update_one(
                {"id": partner_id},
                {"$set": {"commission_rate": rate, "updated_at": datetime.now(timezone.utc).isoformat()}}
            )
            
            if result.matched_count == 0:
                return {"success": False, "error": "Partenaire non trouvé"}
            
            return {"success": True, "commission_rate": rate}
        except Exception as e:
            logger.error(f"Error in update_commission_rate: {e}")
            return {"success": False, "error": str(e)}
    
    # ============ EMAIL SETTINGS ============
    @staticmethod
    async def get_email_settings(db) -> dict:
        """Récupérer les paramètres email"""
        try:
            settings = await db.partnership_settings.find_one({"_id": "email_settings"})
            
            if not settings:
                settings = {
                    "acknowledgment_enabled": True,
                    "admin_notification_enabled": True,
                    "approval_enabled": True,
                    "rejection_enabled": True
                }
            else:
                del settings["_id"]
            
            return {"success": True, "settings": settings}
        except Exception as e:
            logger.error(f"Error in get_email_settings: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def toggle_email_setting(db, setting_type: str) -> dict:
        """Activer/désactiver un type d'email"""
        valid_types = ["acknowledgment", "admin_notification", "approval", "rejection"]
        if setting_type not in valid_types:
            return {"success": False, "error": f"Type invalide. Valides: {valid_types}"}
        
        try:
            setting_key = f"{setting_type}_enabled"
            
            # Récupérer setting actuel
            settings = await db.partnership_settings.find_one({"_id": "email_settings"})
            current_value = settings.get(setting_key, True) if settings else True
            new_value = not current_value
            
            # Mettre à jour
            await db.partnership_settings.update_one(
                {"_id": "email_settings"},
                {"$set": {
                    setting_key: new_value,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }},
                upsert=True
            )
            
            return {
                "success": True,
                "setting": setting_type,
                "enabled": new_value,
                "message": f"Email '{setting_type}' {'activé' if new_value else 'désactivé'}"
            }
        except Exception as e:
            logger.error(f"Error in toggle_email_setting: {e}")
            return {"success": False, "error": str(e)}


logger.info("PartnersAdminService initialized - Phase 6 Migration")
