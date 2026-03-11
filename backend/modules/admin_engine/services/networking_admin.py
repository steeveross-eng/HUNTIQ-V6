"""
Networking Admin Service - V5-ULTIME Administration Premium
===========================================================

Service d'administration du réseau social chasseurs:
- Posts et publications
- Groupes et communautés
- Leads et prospects
- Parrainages et récompenses
- Portefeuilles virtuels

Module isolé - aucun import croisé.
Phase 4 Migration - Cœur métier BIONIC HUNT/Chasse.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional
import logging
import uuid

logger = logging.getLogger(__name__)


class NetworkingAdminService:
    """Service isolé pour l'administration du réseau social"""
    
    # ============ DASHBOARD & STATS ============
    @staticmethod
    async def get_dashboard_stats(db) -> dict:
        """Statistiques globales du networking"""
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        
        # Posts
        total_posts = await db.content_posts.count_documents({})
        posts_this_week = await db.content_posts.count_documents({
            "created_at": {"$gte": week_ago.isoformat()}
        })
        
        # Leads
        total_leads = await db.leads.count_documents({})
        new_leads = await db.leads.count_documents({"status": "new"})
        converted_leads = await db.leads.count_documents({"status": "converted"})
        
        # Contacts
        total_contacts = await db.contacts.count_documents({})
        
        # Groups
        total_groups = await db.groups.count_documents({})
        active_groups = await db.groups.count_documents({"is_active": True})
        
        # Referrals
        total_referrals = await db.referrals.count_documents({})
        pending_referrals = await db.referrals.count_documents({"status": "pending"})
        rewarded_referrals = await db.referrals.count_documents({"status": "rewarded"})
        
        # Wallets
        total_wallets = await db.wallets.count_documents({})
        wallets = await db.wallets.find({}, {"balance_credits": 1, "_id": 0}).to_list(length=10000)
        total_credits = sum(w.get("balance_credits", 0) for w in wallets)
        
        return {
            "success": True,
            "stats": {
                "posts": {
                    "total": total_posts,
                    "this_week": posts_this_week
                },
                "leads": {
                    "total": total_leads,
                    "new": new_leads,
                    "converted": converted_leads
                },
                "contacts": {
                    "total": total_contacts
                },
                "groups": {
                    "total": total_groups,
                    "active": active_groups
                },
                "referrals": {
                    "total": total_referrals,
                    "pending": pending_referrals,
                    "rewarded": rewarded_referrals
                },
                "wallets": {
                    "total": total_wallets,
                    "total_credits": round(total_credits, 2)
                }
            }
        }
    
    # ============ POSTS MANAGEMENT ============
    @staticmethod
    async def get_posts(db, visibility: Optional[str] = None,
                       content_type: Optional[str] = None,
                       is_featured: Optional[bool] = None,
                       limit: int = 50) -> dict:
        """Liste les publications"""
        query = {}
        if visibility and visibility != 'all':
            query["visibility"] = visibility
        if content_type and content_type != 'all':
            query["content_type"] = content_type
        if is_featured is not None:
            query["is_featured"] = is_featured
        
        posts = await db.content_posts.find(
            query, {"_id": 0}
        ).sort("created_at", -1).limit(limit).to_list(length=limit)
        
        total = await db.content_posts.count_documents(query)
        
        return {
            "success": True,
            "total": total,
            "posts": posts
        }
    
    @staticmethod
    async def toggle_post_featured(db, post_id: str, is_featured: bool) -> dict:
        """Mettre en vedette une publication"""
        result = await db.content_posts.update_one(
            {"id": post_id},
            {"$set": {"is_featured": is_featured, "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        if result.matched_count == 0:
            return {"success": False, "error": "Post not found"}
        
        return {"success": True, "post_id": post_id, "is_featured": is_featured}
    
    @staticmethod
    async def toggle_post_pinned(db, post_id: str, is_pinned: bool) -> dict:
        """Épingler une publication"""
        result = await db.content_posts.update_one(
            {"id": post_id},
            {"$set": {"is_pinned": is_pinned, "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        if result.matched_count == 0:
            return {"success": False, "error": "Post not found"}
        
        return {"success": True, "post_id": post_id, "is_pinned": is_pinned}
    
    @staticmethod
    async def delete_post(db, post_id: str) -> dict:
        """Supprimer une publication (admin)"""
        # Supprimer le post
        result = await db.content_posts.delete_one({"id": post_id})
        
        if result.deleted_count == 0:
            return {"success": False, "error": "Post not found"}
        
        # Supprimer les commentaires et likes associés
        await db.content_comments.delete_many({"post_id": post_id})
        await db.content_likes.delete_many({"target_id": post_id})
        
        return {"success": True, "post_id": post_id, "deleted": True}
    
    # ============ GROUPS MANAGEMENT ============
    @staticmethod
    async def get_groups(db, privacy: Optional[str] = None,
                        group_type: Optional[str] = None,
                        limit: int = 50) -> dict:
        """Liste les groupes"""
        query = {}
        if privacy and privacy != 'all':
            query["privacy"] = privacy
        if group_type and group_type != 'all':
            query["group_type"] = group_type
        
        groups = await db.groups.find(
            query, {"_id": 0}
        ).sort("created_at", -1).limit(limit).to_list(length=limit)
        
        total = await db.groups.count_documents(query)
        
        # Type counts
        type_counts = {}
        for gt in ["hunting_club", "family", "business", "friends", "custom"]:
            type_counts[gt] = await db.groups.count_documents({"group_type": gt})
        
        return {
            "success": True,
            "total": total,
            "type_counts": type_counts,
            "groups": groups
        }
    
    @staticmethod
    async def get_group_detail(db, group_id: str) -> dict:
        """Détail d'un groupe avec membres"""
        group = await db.groups.find_one(
            {"id": group_id},
            {"_id": 0}
        )
        
        if not group:
            return {"success": False, "error": "Group not found"}
        
        members = await db.group_memberships.find(
            {"group_id": group_id},
            {"_id": 0}
        ).to_list(length=500)
        
        return {
            "success": True,
            "group": group,
            "members": members
        }
    
    @staticmethod
    async def toggle_group_active(db, group_id: str, is_active: bool) -> dict:
        """Activer/désactiver un groupe"""
        result = await db.groups.update_one(
            {"id": group_id},
            {"$set": {"is_active": is_active}}
        )
        
        if result.matched_count == 0:
            return {"success": False, "error": "Group not found"}
        
        return {"success": True, "group_id": group_id, "is_active": is_active}
    
    @staticmethod
    async def delete_group(db, group_id: str) -> dict:
        """Supprimer un groupe (admin)"""
        result = await db.groups.delete_one({"id": group_id})
        
        if result.deleted_count == 0:
            return {"success": False, "error": "Group not found"}
        
        # Supprimer les memberships
        await db.group_memberships.delete_many({"group_id": group_id})
        
        return {"success": True, "group_id": group_id, "deleted": True}
    
    # ============ LEADS MANAGEMENT ============
    @staticmethod
    async def get_all_leads(db, status: Optional[str] = None,
                           source: Optional[str] = None,
                           limit: int = 50) -> dict:
        """Liste tous les leads (vue admin)"""
        query = {}
        if status and status != 'all':
            query["status"] = status
        if source and source != 'all':
            query["source"] = source
        
        leads = await db.leads.find(
            query, {"_id": 0}
        ).sort("created_at", -1).limit(limit).to_list(length=limit)
        
        total = await db.leads.count_documents(query)
        
        # Status counts
        status_counts = {}
        for s in ["new", "contacted", "interested", "negotiating", "converted", "lost"]:
            status_counts[s] = await db.leads.count_documents({"status": s})
        
        # Calculate values
        total_estimated = sum(l.get("estimated_value", 0) for l in leads)
        total_actual = sum(l.get("actual_value", 0) for l in leads if l.get("status") == "converted")
        
        return {
            "success": True,
            "total": total,
            "status_counts": status_counts,
            "values": {
                "total_estimated": round(total_estimated, 2),
                "total_actual": round(total_actual, 2)
            },
            "leads": leads
        }
    
    # ============ REFERRALS MANAGEMENT ============
    @staticmethod
    async def get_referrals(db, status: Optional[str] = None, limit: int = 50) -> dict:
        """Liste les parrainages"""
        query = {}
        if status and status != 'all':
            query["status"] = status
        
        referrals = await db.referrals.find(
            query, {"_id": 0}
        ).sort("created_at", -1).limit(limit).to_list(length=limit)
        
        total = await db.referrals.count_documents(query)
        
        # Status counts
        status_counts = {}
        for s in ["pending", "verified", "rewarded", "expired"]:
            status_counts[s] = await db.referrals.count_documents({"status": s})
        
        # Total rewards distributed
        rewarded = await db.referrals.find({"status": "rewarded"}).to_list(length=10000)
        total_rewards = sum(r.get("referrer_reward_amount", 0) + r.get("referee_reward_amount", 0) for r in rewarded)
        
        return {
            "success": True,
            "total": total,
            "status_counts": status_counts,
            "total_rewards_distributed": round(total_rewards, 2),
            "referrals": referrals
        }
    
    @staticmethod
    async def get_pending_referrals(db) -> dict:
        """Parrainages en attente de validation"""
        referrals = await db.referrals.find(
            {"status": "pending"},
            {"_id": 0}
        ).sort("created_at", -1).to_list(length=100)
        
        return {
            "success": True,
            "total": len(referrals),
            "referrals": referrals
        }
    
    @staticmethod
    async def verify_referral(db, referral_id: str) -> dict:
        """Vérifier et récompenser un parrainage"""
        referral = await db.referrals.find_one({"id": referral_id}, {"_id": 0})
        
        if not referral:
            return {"success": False, "error": "Referral not found"}
        
        if referral.get("status") != "pending":
            return {"success": False, "error": "Referral already processed"}
        
        now = datetime.now(timezone.utc)
        
        # Update referral status
        await db.referrals.update_one(
            {"id": referral_id},
            {"$set": {
                "status": "rewarded",
                "verified_at": now.isoformat(),
                "rewarded_at": now.isoformat()
            }}
        )
        
        # Add credits to wallets
        for user_id, amount in [
            (referral["referrer_id"], referral.get("referrer_reward_amount", 10)),
            (referral["referee_id"], referral.get("referee_reward_amount", 5))
        ]:
            # Get or create wallet
            wallet = await db.wallets.find_one({"user_id": user_id})
            if not wallet:
                wallet = {
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "balance_credits": 0,
                    "total_earned": 0,
                    "created_at": now.isoformat()
                }
                await db.wallets.insert_one(wallet)
            
            # Add credits
            await db.wallets.update_one(
                {"user_id": user_id},
                {
                    "$inc": {"balance_credits": amount, "total_earned": amount},
                    "$set": {"updated_at": now.isoformat()}
                }
            )
        
        return {
            "success": True,
            "referral_id": referral_id,
            "rewarded": True,
            "referrer_reward": referral.get("referrer_reward_amount", 10),
            "referee_reward": referral.get("referee_reward_amount", 5)
        }
    
    @staticmethod
    async def reject_referral(db, referral_id: str, reason: str = "") -> dict:
        """Rejeter un parrainage"""
        result = await db.referrals.update_one(
            {"id": referral_id, "status": "pending"},
            {"$set": {
                "status": "expired",
                "rejection_reason": reason,
                "rejected_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        if result.matched_count == 0:
            return {"success": False, "error": "Referral not found or already processed"}
        
        return {"success": True, "referral_id": referral_id, "rejected": True}
    
    # ============ WALLETS MANAGEMENT ============
    @staticmethod
    async def get_wallets(db, limit: int = 50) -> dict:
        """Liste les portefeuilles"""
        wallets = await db.wallets.find(
            {}, {"_id": 0}
        ).sort("balance_credits", -1).limit(limit).to_list(length=limit)
        
        total = await db.wallets.count_documents({})
        
        # Total credits
        all_wallets = await db.wallets.find({}, {"balance_credits": 1, "_id": 0}).to_list(length=10000)
        total_credits = sum(w.get("balance_credits", 0) for w in all_wallets)
        total_earned = sum(w.get("total_earned", 0) for w in all_wallets)
        
        return {
            "success": True,
            "total": total,
            "total_credits_circulation": round(total_credits, 2),
            "total_earned_all_time": round(total_earned, 2),
            "wallets": wallets
        }
    
    @staticmethod
    async def get_wallet_detail(db, wallet_id: str) -> dict:
        """Détail d'un portefeuille avec transactions"""
        wallet = await db.wallets.find_one(
            {"id": wallet_id},
            {"_id": 0}
        )
        
        if not wallet:
            return {"success": False, "error": "Wallet not found"}
        
        transactions = await db.wallet_transactions.find(
            {"wallet_id": wallet_id},
            {"_id": 0}
        ).sort("created_at", -1).limit(50).to_list(length=50)
        
        return {
            "success": True,
            "wallet": wallet,
            "transactions": transactions
        }
    
    @staticmethod
    async def adjust_wallet_balance(db, user_id: str, amount: float, 
                                   reason: str, adjustment_type: str = "manual") -> dict:
        """Ajuster le solde d'un portefeuille (admin)"""
        wallet = await db.wallets.find_one({"user_id": user_id})
        
        if not wallet:
            # Create wallet
            wallet = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "balance_credits": 0,
                "total_earned": 0,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.wallets.insert_one(wallet)
        
        balance_before = wallet.get("balance_credits", 0)
        balance_after = balance_before + amount
        
        if balance_after < 0:
            return {"success": False, "error": "Cannot have negative balance"}
        
        now = datetime.now(timezone.utc)
        
        # Create transaction record
        tx = {
            "id": str(uuid.uuid4()),
            "wallet_id": wallet["id"],
            "user_id": user_id,
            "transaction_type": adjustment_type,
            "amount": amount,
            "currency": "credits",
            "balance_before": balance_before,
            "balance_after": balance_after,
            "description": reason,
            "status": "completed",
            "created_at": now.isoformat()
        }
        await db.wallet_transactions.insert_one(tx)
        
        # Update wallet
        update = {
            "balance_credits": balance_after,
            "updated_at": now.isoformat()
        }
        if amount > 0:
            await db.wallets.update_one(
                {"user_id": user_id},
                {"$set": update, "$inc": {"total_earned": amount}}
            )
        else:
            await db.wallets.update_one(
                {"user_id": user_id},
                {"$set": update}
            )
        
        return {
            "success": True,
            "user_id": user_id,
            "amount": amount,
            "balance_after": balance_after
        }
    
    # ============ REFERRAL CODES MANAGEMENT ============
    @staticmethod
    async def get_referral_codes(db, is_active: Optional[bool] = None, limit: int = 50) -> dict:
        """Liste les codes de parrainage"""
        query = {}
        if is_active is not None:
            query["is_active"] = is_active
        
        codes = await db.referral_codes.find(
            query, {"_id": 0}
        ).sort("uses_count", -1).limit(limit).to_list(length=limit)
        
        total = await db.referral_codes.count_documents(query)
        
        return {
            "success": True,
            "total": total,
            "codes": codes
        }
    
    @staticmethod
    async def toggle_referral_code(db, code: str, is_active: bool) -> dict:
        """Activer/désactiver un code de parrainage"""
        result = await db.referral_codes.update_one(
            {"code": code},
            {"$set": {"is_active": is_active}}
        )
        
        if result.matched_count == 0:
            return {"success": False, "error": "Code not found"}
        
        return {"success": True, "code": code, "is_active": is_active}
