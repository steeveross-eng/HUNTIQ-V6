"""
Hotspots Admin Service - V5-ULTIME Administration Premium
=========================================================

Service d'administration des hotspots et terres à louer:
- Gestion des annonces de terres
- Tarification et pricing
- Statistiques et KPIs
- Validation des annonces
- Gestion propriétaires/locataires

Module isolé - aucun import croisé.
Phase 4 Migration - Cœur métier BIONIC HUNT/Chasse.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class HotspotsAdminService:
    """Service isolé pour l'administration des hotspots et terres"""
    
    # ============ DASHBOARD & STATS ============
    @staticmethod
    async def get_dashboard_stats(db) -> dict:
        """Statistiques globales du module Terres"""
        # Listings
        total_listings = await db.land_listings.count_documents({})
        active_listings = await db.land_listings.count_documents({"status": "active"})
        pending_listings = await db.land_listings.count_documents({"status": "pending"})
        featured_listings = await db.land_listings.count_documents({"is_featured": True})
        
        # Users
        total_owners = await db.land_owners.count_documents({})
        total_renters = await db.land_renters.count_documents({})
        premium_renters = await db.land_renters.count_documents({
            "subscription_tier": {"$in": ["basic", "pro", "vip"]}
        })
        
        # Agreements
        total_agreements = await db.land_agreements.count_documents({})
        signed_agreements = await db.land_agreements.count_documents({"status": "signed"})
        
        # Revenue
        purchases = await db.lands_purchases.find({"status": "completed"}).to_list(length=10000)
        total_revenue = sum(p.get("amount", 0) for p in purchases)
        
        # Recent activity
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        new_listings_week = await db.land_listings.count_documents({
            "created_at": {"$gte": week_ago.isoformat()}
        })
        
        return {
            "success": True,
            "stats": {
                "listings": {
                    "total": total_listings,
                    "active": active_listings,
                    "pending": pending_listings,
                    "featured": featured_listings
                },
                "users": {
                    "owners": total_owners,
                    "renters": total_renters,
                    "premium_renters": premium_renters
                },
                "agreements": {
                    "total": total_agreements,
                    "signed": signed_agreements,
                    "conversion_rate": round((signed_agreements / max(total_agreements, 1)) * 100, 1)
                },
                "revenue": {
                    "total": round(total_revenue, 2),
                    "transactions": len(purchases)
                },
                "activity": {
                    "new_listings_week": new_listings_week
                }
            }
        }
    
    # ============ LISTINGS MANAGEMENT ============
    @staticmethod
    async def get_listings(db, status: Optional[str] = None, 
                          region: Optional[str] = None,
                          is_featured: Optional[bool] = None,
                          limit: int = 50) -> dict:
        """Liste les annonces de terres avec filtres"""
        query = {}
        if status and status != 'all':
            query["status"] = status
        if region:
            query["region"] = region
        if is_featured is not None:
            query["is_featured"] = is_featured
        
        listings = await db.land_listings.find(
            query, {"_id": 0}
        ).sort("created_at", -1).limit(limit).to_list(length=limit)
        
        total = await db.land_listings.count_documents(query)
        
        # Status counts
        status_counts = {}
        for s in ["draft", "pending", "active", "rented", "expired", "suspended"]:
            status_counts[s] = await db.land_listings.count_documents({"status": s})
        
        return {
            "success": True,
            "total": total,
            "status_counts": status_counts,
            "listings": listings
        }
    
    @staticmethod
    async def get_listing_detail(db, listing_id: str) -> dict:
        """Détail d'une annonce"""
        listing = await db.land_listings.find_one(
            {"id": listing_id},
            {"_id": 0}
        )
        
        if not listing:
            return {"success": False, "error": "Listing not found"}
        
        # Get owner info
        owner = await db.land_owners.find_one(
            {"id": listing.get("owner_id")},
            {"_id": 0, "hashed_password": 0}
        )
        
        return {
            "success": True,
            "listing": listing,
            "owner": owner
        }
    
    @staticmethod
    async def update_listing_status(db, listing_id: str, new_status: str) -> dict:
        """Changer le statut d'une annonce"""
        valid_statuses = ["draft", "pending", "active", "rented", "expired", "suspended"]
        if new_status not in valid_statuses:
            return {"success": False, "error": f"Invalid status. Must be one of: {valid_statuses}"}
        
        result = await db.land_listings.update_one(
            {"id": listing_id},
            {"$set": {"status": new_status, "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        if result.matched_count == 0:
            return {"success": False, "error": "Listing not found"}
        
        return {"success": True, "listing_id": listing_id, "new_status": new_status}
    
    @staticmethod
    async def toggle_featured(db, listing_id: str, is_featured: bool) -> dict:
        """Mettre en vedette une annonce"""
        update = {
            "is_featured": is_featured,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        if is_featured:
            update["featured_at"] = datetime.now(timezone.utc).isoformat()
        
        result = await db.land_listings.update_one(
            {"id": listing_id},
            {"$set": update}
        )
        
        if result.matched_count == 0:
            return {"success": False, "error": "Listing not found"}
        
        return {"success": True, "listing_id": listing_id, "is_featured": is_featured}
    
    @staticmethod
    async def delete_listing(db, listing_id: str) -> dict:
        """Supprimer une annonce"""
        result = await db.land_listings.delete_one({"id": listing_id})
        
        if result.deleted_count == 0:
            return {"success": False, "error": "Listing not found"}
        
        return {"success": True, "listing_id": listing_id, "deleted": True}
    
    # ============ PRICING MANAGEMENT ============
    @staticmethod
    async def get_pricing(db) -> dict:
        """Récupérer la tarification actuelle"""
        pricing = await db.lands_pricing.find_one(
            {"_id": "main"},
            {"_id": 0}
        )
        
        if not pricing:
            # Default pricing
            pricing = {
                "listing_basic": {"price": 4.99, "name": "Publication d'annonce", "description": "Publier une terre sur la plateforme"},
                "listing_featured_7": {"price": 10.99, "name": "Mise en vedette 7 jours", "description": "Annonce en haut des résultats"},
                "listing_featured_30": {"price": 29.99, "name": "Mise en vedette 30 jours", "description": "Annonce en haut des résultats"},
                "listing_auto_bump": {"price": 9.99, "name": "Remontée automatique", "description": "Votre annonce remonte chaque jour"},
                "boost_24h": {"price": 3.99, "name": "Boost 24h", "description": "Booster l'annonce pendant 24 heures"},
                "badge_premium": {"price": 4.99, "name": "Badge Terrain Premium", "description": "Badge distinctif"},
                "send_to_hunters": {"price": 7.99, "name": "Envoi ciblé", "description": "Envoyer à 100 chasseurs ciblés"},
                "generate_agreement": {"price": 10.99, "name": "Entente légale", "description": "Générer une entente légale personnalisée"},
                "ai_analysis": {"price": 19.99, "name": "Analyse IA", "description": "Analyse IA complète du terrain"},
                "renter_basic": {"price": 4.99, "name": "Accès Chasseur Basic", "description": "Accès aux nouvelles terres 48h avant", "duration_days": 30},
                "renter_pro": {"price": 9.99, "name": "Accès Chasseur Pro", "description": "Accès illimité + alertes", "duration_days": 30},
                "renter_vip": {"price": 19.99, "name": "Accès Chasseur VIP", "description": "Accès VIP + terres exclusives", "duration_days": 30},
                "owner_fee_percent": {"price": 10.0, "name": "Frais propriétaire", "description": "Frais de mise en relation"},
                "renter_fee_percent": {"price": 10.0, "name": "Frais locataire", "description": "Frais de mise en relation"}
            }
        
        return {"success": True, "pricing": pricing}
    
    @staticmethod
    async def update_pricing(db, updates: dict) -> dict:
        """Mettre à jour la tarification"""
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        await db.lands_pricing.update_one(
            {"_id": "main"},
            {"$set": updates},
            upsert=True
        )
        
        return {"success": True, "updated": True}
    
    # ============ OWNERS MANAGEMENT ============
    @staticmethod
    async def get_owners(db, limit: int = 50) -> dict:
        """Liste les propriétaires"""
        owners = await db.land_owners.find(
            {}, {"_id": 0, "hashed_password": 0}
        ).sort("created_at", -1).limit(limit).to_list(length=limit)
        
        total = await db.land_owners.count_documents({})
        
        return {
            "success": True,
            "total": total,
            "owners": owners
        }
    
    @staticmethod
    async def get_owner_detail(db, owner_id: str) -> dict:
        """Détail d'un propriétaire avec ses annonces"""
        owner = await db.land_owners.find_one(
            {"id": owner_id},
            {"_id": 0, "hashed_password": 0}
        )
        
        if not owner:
            return {"success": False, "error": "Owner not found"}
        
        # Get owner's listings
        listings = await db.land_listings.find(
            {"owner_id": owner_id},
            {"_id": 0}
        ).to_list(length=100)
        
        return {
            "success": True,
            "owner": owner,
            "listings": listings,
            "listings_count": len(listings)
        }
    
    # ============ RENTERS MANAGEMENT ============
    @staticmethod
    async def get_renters(db, subscription_tier: Optional[str] = None, limit: int = 50) -> dict:
        """Liste les locataires (chasseurs)"""
        query = {}
        if subscription_tier and subscription_tier != 'all':
            query["subscription_tier"] = subscription_tier
        
        renters = await db.land_renters.find(
            query, {"_id": 0, "hashed_password": 0}
        ).sort("created_at", -1).limit(limit).to_list(length=limit)
        
        total = await db.land_renters.count_documents(query)
        
        # Tier distribution
        tier_counts = {}
        for tier in ["free", "basic", "pro", "vip"]:
            tier_counts[tier] = await db.land_renters.count_documents({"subscription_tier": tier})
        
        return {
            "success": True,
            "total": total,
            "tier_counts": tier_counts,
            "renters": renters
        }
    
    # ============ AGREEMENTS MANAGEMENT ============
    @staticmethod
    async def get_agreements(db, status: Optional[str] = None, limit: int = 50) -> dict:
        """Liste les ententes de location"""
        query = {}
        if status and status != 'all':
            query["status"] = status
        
        agreements = await db.land_agreements.find(
            query, {"_id": 0}
        ).sort("created_at", -1).limit(limit).to_list(length=limit)
        
        total = await db.land_agreements.count_documents(query)
        
        # Status counts
        status_counts = {}
        for s in ["draft", "pending_owner", "pending_renter", "signed", "cancelled", "completed", "disputed"]:
            status_counts[s] = await db.land_agreements.count_documents({"status": s})
        
        return {
            "success": True,
            "total": total,
            "status_counts": status_counts,
            "agreements": agreements
        }
    
    @staticmethod
    async def get_agreement_detail(db, agreement_id: str) -> dict:
        """Détail d'une entente"""
        agreement = await db.land_agreements.find_one(
            {"id": agreement_id},
            {"_id": 0}
        )
        
        if not agreement:
            return {"success": False, "error": "Agreement not found"}
        
        return {"success": True, "agreement": agreement}
    
    # ============ REGIONS & ZONES ============
    @staticmethod
    async def get_regions_stats(db) -> dict:
        """Statistiques par région"""
        pipeline = [
            {"$match": {"status": "active"}},
            {"$group": {
                "_id": "$region",
                "count": {"$sum": 1},
                "avg_price_day": {"$avg": "$price_per_day"},
                "avg_surface": {"$avg": "$surface_acres"}
            }},
            {"$sort": {"count": -1}}
        ]
        
        results = await db.land_listings.aggregate(pipeline).to_list(length=50)
        
        regions = []
        for r in results:
            regions.append({
                "region": r["_id"],
                "listings_count": r["count"],
                "avg_price_per_day": round(r["avg_price_day"] or 0, 2),
                "avg_surface_acres": round(r["avg_surface"] or 0, 1)
            })
        
        return {
            "success": True,
            "regions": regions
        }
    
    # ============ PURCHASES & TRANSACTIONS ============
    @staticmethod
    async def get_purchases(db, status: Optional[str] = None, limit: int = 50) -> dict:
        """Liste les achats/transactions"""
        query = {}
        if status and status != 'all':
            query["status"] = status
        
        purchases = await db.lands_purchases.find(
            query, {"_id": 0}
        ).sort("created_at", -1).limit(limit).to_list(length=limit)
        
        total = await db.lands_purchases.count_documents(query)
        
        # Revenue par service
        pipeline = [
            {"$match": {"status": "completed"}},
            {"$group": {
                "_id": "$service_id",
                "count": {"$sum": 1},
                "total": {"$sum": "$amount"}
            }}
        ]
        revenue_by_service = await db.lands_purchases.aggregate(pipeline).to_list(length=50)
        
        return {
            "success": True,
            "total": total,
            "purchases": purchases,
            "revenue_by_service": revenue_by_service
        }
