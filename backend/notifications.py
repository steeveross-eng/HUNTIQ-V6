"""
Notifications Module
- Real-time notification system for user engagement
- Notifications for: likes, comments, group joins, referrals, wallet transactions
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime, timezone
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
import os

# Router
router = APIRouter(prefix="/notifications", tags=["Notifications"])

# Database connection
mongo_url = os.environ.get('MONGO_URL')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'scentscience')]

# ============================================
# MODELS
# ============================================

class Notification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str  # Recipient
    type: Literal[
        "like_post", "like_comment", "comment", "reply",
        "follow", "group_join", "group_invite", "group_post",
        "referral_signup", "referral_rewarded",
        "wallet_credit", "wallet_debit", "wallet_transfer",
        "lead_update", "mention", "system"
    ]
    title: str
    message: str
    icon: Optional[str] = None  # Emoji or icon name
    link: Optional[str] = None  # URL to navigate to
    actor_id: Optional[str] = None  # User who triggered the notification
    actor_name: Optional[str] = None
    actor_avatar: Optional[str] = None
    reference_type: Optional[str] = None  # "post", "comment", "group", "referral"
    reference_id: Optional[str] = None
    metadata: dict = {}  # Additional data
    is_read: bool = False
    is_seen: bool = False  # For notification badge
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class NotificationPreferences(BaseModel):
    user_id: str
    email_notifications: bool = True
    push_notifications: bool = True
    # Granular controls
    notify_likes: bool = True
    notify_comments: bool = True
    notify_follows: bool = True
    notify_groups: bool = True
    notify_referrals: bool = True
    notify_wallet: bool = True
    notify_leads: bool = True
    notify_mentions: bool = True
    # Quiet hours
    quiet_hours_enabled: bool = False
    quiet_hours_start: str = "22:00"  # 10 PM
    quiet_hours_end: str = "08:00"  # 8 AM
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ============================================
# NOTIFICATION CREATION HELPERS
# ============================================

async def create_notification(
    user_id: str,
    notification_type: str,
    title: str,
    message: str,
    icon: str = None,
    link: str = None,
    actor_id: str = None,
    actor_name: str = None,
    reference_type: str = None,
    reference_id: str = None,
    metadata: dict = {}
) -> dict:
    """Create and store a notification"""
    
    # Check user preferences
    prefs = await db.notification_preferences.find_one({"user_id": user_id}, {"_id": 0})
    
    if prefs:
        # Check if this type of notification is enabled
        type_mapping = {
            "like_post": "notify_likes",
            "like_comment": "notify_likes",
            "comment": "notify_comments",
            "reply": "notify_comments",
            "follow": "notify_follows",
            "group_join": "notify_groups",
            "group_invite": "notify_groups",
            "group_post": "notify_groups",
            "referral_signup": "notify_referrals",
            "referral_rewarded": "notify_referrals",
            "wallet_credit": "notify_wallet",
            "wallet_debit": "notify_wallet",
            "wallet_transfer": "notify_wallet",
            "lead_update": "notify_leads",
            "mention": "notify_mentions",
        }
        
        pref_key = type_mapping.get(notification_type)
        if pref_key and not prefs.get(pref_key, True):
            return None  # User disabled this notification type
    
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        message=message,
        icon=icon,
        link=link,
        actor_id=actor_id,
        actor_name=actor_name,
        reference_type=reference_type,
        reference_id=reference_id,
        metadata=metadata
    )
    
    doc = notification.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.notifications.insert_one(doc)
    doc.pop('_id', None)
    
    return doc


# ============================================
# NOTIFICATION TRIGGERS (Called from other modules)
# ============================================

async def notify_post_liked(post_author_id: str, liker_name: str, liker_id: str, post_id: str, post_title: str = None):
    """Notify when someone likes a post"""
    if post_author_id == liker_id:
        return  # Don't notify self-likes
    
    title_text = f'"{post_title[:30]}..."' if post_title else "votre publication"
    await create_notification(
        user_id=post_author_id,
        notification_type="like_post",
        title="Nouveau j'aime ❤️",
        message=f"{liker_name} a aimé {title_text}",
        icon="❤️",
        link=f"/network?post={post_id}",
        actor_id=liker_id,
        actor_name=liker_name,
        reference_type="post",
        reference_id=post_id
    )


async def notify_comment_received(post_author_id: str, commenter_name: str, commenter_id: str, post_id: str, comment_preview: str):
    """Notify when someone comments on a post"""
    if post_author_id == commenter_id:
        return
    
    await create_notification(
        user_id=post_author_id,
        notification_type="comment",
        title="Nouveau commentaire 💬",
        message=f'{commenter_name}: "{comment_preview[:50]}..."',
        icon="💬",
        link=f"/network?post={post_id}",
        actor_id=commenter_id,
        actor_name=commenter_name,
        reference_type="post",
        reference_id=post_id
    )


async def notify_group_join(group_owner_id: str, member_name: str, member_id: str, group_id: str, group_name: str):
    """Notify group owner when someone joins"""
    if group_owner_id == member_id:
        return
    
    await create_notification(
        user_id=group_owner_id,
        notification_type="group_join",
        title="Nouveau membre 👥",
        message=f"{member_name} a rejoint le groupe {group_name}",
        icon="👥",
        link=f"/network?tab=groups&group={group_id}",
        actor_id=member_id,
        actor_name=member_name,
        reference_type="group",
        reference_id=group_id
    )


async def notify_referral_signup(referrer_id: str, referee_name: str, referral_code: str):
    """Notify when someone uses your referral code"""
    await create_notification(
        user_id=referrer_id,
        notification_type="referral_signup",
        title="Nouveau parrainage! 🎁",
        message=f"Quelqu'un a utilisé votre code {referral_code}. En attente de validation.",
        icon="🎁",
        link="/network?tab=referral",
        reference_type="referral",
        reference_id=referral_code
    )


async def notify_referral_rewarded(user_id: str, amount: float, is_referrer: bool = True):
    """Notify when referral reward is credited"""
    if is_referrer:
        title = "Récompense de parrainage! 🎉"
        message = f"Vous avez reçu {amount} crédits pour votre parrainage"
    else:
        title = "Bonus de bienvenue! 🎉"
        message = f"Vous avez reçu {amount} crédits grâce au parrainage"
    
    await create_notification(
        user_id=user_id,
        notification_type="referral_rewarded",
        title=title,
        message=message,
        icon="🎉",
        link="/network?tab=wallet"
    )


async def notify_wallet_credit(user_id: str, amount: float, description: str):
    """Notify when credits are added to wallet"""
    await create_notification(
        user_id=user_id,
        notification_type="wallet_credit",
        title="Crédits reçus 💰",
        message=f"+{amount} crédits: {description}",
        icon="💰",
        link="/network?tab=wallet",
        metadata={"amount": amount}
    )


async def notify_wallet_transfer(recipient_id: str, sender_name: str, sender_id: str, amount: float):
    """Notify when receiving a transfer"""
    await create_notification(
        user_id=recipient_id,
        notification_type="wallet_transfer",
        title="Transfert reçu 💸",
        message=f"{sender_name} vous a envoyé {amount} crédits",
        icon="💸",
        link="/network?tab=wallet",
        actor_id=sender_id,
        actor_name=sender_name,
        metadata={"amount": amount}
    )


async def notify_lead_status_change(owner_id: str, lead_name: str, lead_id: str, new_status: str):
    """Notify when a lead status changes"""
    status_labels = {
        "contacted": "contacté",
        "interested": "intéressé",
        "negotiating": "en négociation",
        "converted": "converti! 🎉",
        "lost": "perdu"
    }
    
    status_text = status_labels.get(new_status, new_status)
    
    await create_notification(
        user_id=owner_id,
        notification_type="lead_update",
        title="Mise à jour prospect 📊",
        message=f"Le prospect {lead_name} est maintenant: {status_text}",
        icon="📊",
        link="/network?tab=leads",
        reference_type="lead",
        reference_id=lead_id
    )


# ============================================
# API ENDPOINTS
# ============================================

@router.get("/{user_id}")
async def get_notifications(
    user_id: str,
    unread_only: bool = False,
    limit: int = 50,
    offset: int = 0
):
    """Get notifications for a user"""
    query = {"user_id": user_id}
    if unread_only:
        query["is_read"] = False
    
    notifications = await db.notifications.find(query, {"_id": 0}).sort("created_at", -1).skip(offset).limit(limit).to_list(limit)
    
    # Count unread
    unread_count = await db.notifications.count_documents({"user_id": user_id, "is_read": False})
    unseen_count = await db.notifications.count_documents({"user_id": user_id, "is_seen": False})
    
    return {
        "notifications": notifications,
        "unread_count": unread_count,
        "unseen_count": unseen_count,
        "total": await db.notifications.count_documents({"user_id": user_id})
    }


@router.post("/{user_id}/mark-seen")
async def mark_notifications_seen(user_id: str):
    """Mark all notifications as seen (for badge)"""
    await db.notifications.update_many(
        {"user_id": user_id, "is_seen": False},
        {"$set": {"is_seen": True}}
    )
    return {"success": True}


@router.post("/{user_id}/mark-read")
async def mark_notifications_read(user_id: str, notification_ids: List[str] = None):
    """Mark notifications as read"""
    query = {"user_id": user_id}
    if notification_ids:
        query["id"] = {"$in": notification_ids}
    
    await db.notifications.update_many(query, {"$set": {"is_read": True}})
    return {"success": True}


@router.post("/{user_id}/mark-all-read")
async def mark_all_notifications_read(user_id: str):
    """Mark all notifications as read"""
    await db.notifications.update_many(
        {"user_id": user_id},
        {"$set": {"is_read": True, "is_seen": True}}
    )
    return {"success": True}


@router.delete("/{user_id}/{notification_id}")
async def delete_notification(user_id: str, notification_id: str):
    """Delete a notification"""
    result = await db.notifications.delete_one({"id": notification_id, "user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"success": True}


@router.delete("/{user_id}/clear-all")
async def clear_all_notifications(user_id: str):
    """Clear all notifications for a user"""
    await db.notifications.delete_many({"user_id": user_id})
    return {"success": True}


# ============================================
# PREFERENCES ENDPOINTS
# ============================================

@router.get("/preferences/{user_id}")
async def get_notification_preferences(user_id: str):
    """Get notification preferences for a user"""
    prefs = await db.notification_preferences.find_one({"user_id": user_id}, {"_id": 0})
    
    if not prefs:
        # Create default preferences
        prefs = NotificationPreferences(user_id=user_id).model_dump()
        prefs['updated_at'] = prefs['updated_at'].isoformat()
        await db.notification_preferences.insert_one(prefs)
        prefs.pop('_id', None)
    
    return prefs


@router.put("/preferences/{user_id}")
async def update_notification_preferences(
    user_id: str,
    email_notifications: Optional[bool] = None,
    push_notifications: Optional[bool] = None,
    notify_likes: Optional[bool] = None,
    notify_comments: Optional[bool] = None,
    notify_follows: Optional[bool] = None,
    notify_groups: Optional[bool] = None,
    notify_referrals: Optional[bool] = None,
    notify_wallet: Optional[bool] = None,
    notify_leads: Optional[bool] = None,
    notify_mentions: Optional[bool] = None,
    quiet_hours_enabled: Optional[bool] = None,
    quiet_hours_start: Optional[str] = None,
    quiet_hours_end: Optional[str] = None
):
    """Update notification preferences"""
    # Ensure preferences exist
    existing = await db.notification_preferences.find_one({"user_id": user_id})
    if not existing:
        prefs = NotificationPreferences(user_id=user_id).model_dump()
        prefs['updated_at'] = prefs['updated_at'].isoformat()
        await db.notification_preferences.insert_one(prefs)
    
    update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
    
    if email_notifications is not None:
        update_data["email_notifications"] = email_notifications
    if push_notifications is not None:
        update_data["push_notifications"] = push_notifications
    if notify_likes is not None:
        update_data["notify_likes"] = notify_likes
    if notify_comments is not None:
        update_data["notify_comments"] = notify_comments
    if notify_follows is not None:
        update_data["notify_follows"] = notify_follows
    if notify_groups is not None:
        update_data["notify_groups"] = notify_groups
    if notify_referrals is not None:
        update_data["notify_referrals"] = notify_referrals
    if notify_wallet is not None:
        update_data["notify_wallet"] = notify_wallet
    if notify_leads is not None:
        update_data["notify_leads"] = notify_leads
    if notify_mentions is not None:
        update_data["notify_mentions"] = notify_mentions
    if quiet_hours_enabled is not None:
        update_data["quiet_hours_enabled"] = quiet_hours_enabled
    if quiet_hours_start is not None:
        update_data["quiet_hours_start"] = quiet_hours_start
    if quiet_hours_end is not None:
        update_data["quiet_hours_end"] = quiet_hours_end
    
    await db.notification_preferences.update_one(
        {"user_id": user_id},
        {"$set": update_data}
    )
    
    return {"success": True}


# ============================================
# ADMIN ENDPOINT
# ============================================

@router.post("/admin/send-system")
async def send_system_notification(
    user_ids: List[str],
    title: str,
    message: str,
    link: Optional[str] = None
):
    """Send a system notification to multiple users (admin only)"""
    created = []
    for user_id in user_ids:
        notif = await create_notification(
            user_id=user_id,
            notification_type="system",
            title=title,
            message=message,
            icon="📢",
            link=link
        )
        if notif:
            created.append(notif["id"])
    
    return {"success": True, "sent_count": len(created)}


@router.get("/admin/stats")
async def get_notification_stats():
    """Get notification statistics for admin"""
    total = await db.notifications.count_documents({})
    unread = await db.notifications.count_documents({"is_read": False})
    
    # Count by type
    pipeline = [
        {"$group": {"_id": "$type", "count": {"$sum": 1}}}
    ]
    type_counts = await db.notifications.aggregate(pipeline).to_list(100)
    
    return {
        "total_notifications": total,
        "unread_notifications": unread,
        "by_type": {t["_id"]: t["count"] for t in type_counts}
    }
