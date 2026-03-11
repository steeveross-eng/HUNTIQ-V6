"""
Networking Ecosystem Module
- Content Sharing (posts, images, videos)
- Lead Tracking (prospects)
- Contacts & Groups Management
- Likes System
- Referral & Rewards Engine
- Internal Wallet
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime, timezone, timedelta
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
import os

# Router
router = APIRouter(prefix="/networking", tags=["Networking"])

# Database connection
mongo_url = os.environ.get('MONGO_URL')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'scentscience')]

# Import notification helpers
try:
    from notifications import (
        notify_post_liked,
        notify_comment_received,
        notify_group_join,
        notify_referral_signup,
        notify_referral_rewarded,
        notify_wallet_credit,
        notify_wallet_transfer,
        notify_lead_status_change
    )
    NOTIFICATIONS_ENABLED = True
except ImportError:
    NOTIFICATIONS_ENABLED = False
    print("Notifications module not available for networking")

# ============================================
# MODELS - Content Sharing
# ============================================


class ContentPost(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    author_id: str
    author_name: str
    author_avatar: Optional[str] = None
    content_type: Literal["text", "image", "video", "link", "hunt_story"] = "text"
    title: Optional[str] = None
    body: str
    media_urls: List[str] = []
    tags: List[str] = []
    location: Optional[str] = None  # Hunt location
    species: Optional[str] = None  # Animal species
    visibility: Literal["public", "contacts", "groups", "private"] = "public"
    allowed_groups: List[str] = []  # Group IDs if visibility is "groups"
    likes_count: int = 0
    comments_count: int = 0
    shares_count: int = 0
    is_featured: bool = False
    is_pinned: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

class ContentComment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    post_id: str
    author_id: str
    author_name: str
    author_avatar: Optional[str] = None
    body: str
    parent_comment_id: Optional[str] = None  # For replies
    likes_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ContentLike(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    target_type: Literal["post", "comment"]
    target_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ============================================
# MODELS - Lead Tracking (Prospects)
# ============================================

class Lead(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    owner_id: str  # User who owns this lead
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    source: Literal["marketplace", "lands", "referral", "direct", "event", "other"] = "direct"
    source_details: Optional[str] = None  # e.g., "Listing #123"
    status: Literal["new", "contacted", "interested", "negotiating", "converted", "lost"] = "new"
    interest_type: Literal["buy", "sell", "rent", "service", "info"] = "info"
    interest_details: Optional[str] = None
    notes: List[dict] = []  # [{date, note}]
    tags: List[str] = []
    estimated_value: float = 0  # Potential revenue
    actual_value: float = 0  # If converted
    last_contact: Optional[datetime] = None
    next_followup: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    converted_at: Optional[datetime] = None

class LeadNote(BaseModel):
    note: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ============================================
# MODELS - Contacts & Groups
# ============================================

class Contact(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    owner_id: str  # User who owns this contact
    contact_user_id: Optional[str] = None  # If linked to platform user
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    role: Optional[str] = None
    avatar_url: Optional[str] = None
    relationship: Literal["friend", "business", "family", "hunting_partner", "vendor", "customer", "other"] = "other"
    tags: List[str] = []
    notes: Optional[str] = None
    is_favorite: bool = False
    last_interaction: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Group(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    owner_id: str  # Creator
    name: str
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    group_type: Literal["hunting_club", "family", "business", "friends", "custom"] = "custom"
    privacy: Literal["public", "private", "invite_only"] = "private"
    member_ids: List[str] = []
    admin_ids: List[str] = []  # Users with admin rights
    member_count: int = 0
    posts_count: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class GroupMembership(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    group_id: str
    user_id: str
    user_name: str
    role: Literal["owner", "admin", "moderator", "member"] = "member"
    joined_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    invited_by: Optional[str] = None

# ============================================
# MODELS - Referral & Rewards
# ============================================

class ReferralCode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    owner_id: str
    code: str  # Unique referral code
    reward_type: Literal["cash", "credits", "percentage", "fixed"] = "credits"
    reward_amount: float = 10.0  # Amount or percentage
    referrer_reward: float = 10.0  # What the referrer gets
    referee_reward: float = 5.0  # What the new user gets
    uses_count: int = 0
    max_uses: Optional[int] = None  # None = unlimited
    is_active: bool = True
    expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Referral(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    referrer_id: str  # User who referred
    referee_id: str  # New user who signed up
    referral_code: str
    status: Literal["pending", "verified", "rewarded", "expired"] = "pending"
    referrer_reward_amount: float = 0
    referee_reward_amount: float = 0
    action_type: Literal["signup", "purchase", "subscription", "listing"] = "signup"
    action_value: float = 0  # Value of the action (e.g., purchase amount)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    verified_at: Optional[datetime] = None
    rewarded_at: Optional[datetime] = None

class RewardTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    transaction_type: Literal["referral_bonus", "signup_bonus", "purchase_cashback", "achievement", "manual", "withdrawal", "transfer"]
    amount: float
    currency: Literal["CAD", "credits"] = "credits"
    reference_id: Optional[str] = None  # Referral ID, Order ID, etc.
    description: str
    status: Literal["pending", "completed", "cancelled"] = "completed"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ============================================
# MODELS - Internal Wallet
# ============================================

class Wallet(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    balance_cad: float = 0.0  # Real money balance
    balance_credits: float = 0.0  # Virtual credits
    total_earned: float = 0.0
    total_spent: float = 0.0
    total_withdrawn: float = 0.0
    pending_balance: float = 0.0  # Awaiting verification
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

class WalletTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    wallet_id: str
    user_id: str
    transaction_type: Literal["deposit", "withdrawal", "transfer_in", "transfer_out", "purchase", "refund", "reward", "fee"]
    amount: float
    currency: Literal["CAD", "credits"] = "credits"
    balance_before: float
    balance_after: float
    reference_type: Optional[str] = None  # "order", "referral", "transfer"
    reference_id: Optional[str] = None
    description: str
    status: Literal["pending", "completed", "failed", "cancelled"] = "completed"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ============================================
# CONTENT SHARING ENDPOINTS
# ============================================

@router.get("/posts")
async def get_posts(
    user_id: Optional[str] = None,
    visibility: Optional[str] = None,
    tag: Optional[str] = None,
    species: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
):
    """Get content posts with filters"""
    query = {}
    if user_id:
        query["author_id"] = user_id
    if visibility:
        query["visibility"] = visibility
    if tag:
        query["tags"] = tag
    if species:
        query["species"] = species
    
    posts = await db.content_posts.find(query, {"_id": 0}).sort("created_at", -1).skip(offset).limit(limit).to_list(limit)
    total = await db.content_posts.count_documents(query)
    
    return {"posts": posts, "total": total, "limit": limit, "offset": offset}

@router.get("/posts/{post_id}")
async def get_post(post_id: str):
    """Get a single post with comments"""
    post = await db.content_posts.find_one({"id": post_id}, {"_id": 0})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    comments = await db.content_comments.find({"post_id": post_id}, {"_id": 0}).sort("created_at", 1).to_list(100)
    
    return {"post": post, "comments": comments}

@router.post("/posts")
async def create_post(
    author_id: str,
    author_name: str,
    body: str,
    content_type: str = "text",
    title: Optional[str] = None,
    media_urls: List[str] = [],
    tags: List[str] = [],
    location: Optional[str] = None,
    species: Optional[str] = None,
    visibility: str = "public"
):
    """Create a new post"""
    post = ContentPost(
        author_id=author_id,
        author_name=author_name,
        content_type=content_type,
        title=title,
        body=body,
        media_urls=media_urls,
        tags=tags,
        location=location,
        species=species,
        visibility=visibility
    )
    
    doc = post.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.content_posts.insert_one(doc)
    
    # Remove MongoDB _id before returning
    doc.pop('_id', None)
    
    return {"success": True, "post": doc}

@router.put("/posts/{post_id}")
async def update_post(post_id: str, author_id: str, body: Optional[str] = None, title: Optional[str] = None, tags: Optional[List[str]] = None):
    """Update a post"""
    post = await db.content_posts.find_one({"id": post_id}, {"_id": 0})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post["author_id"] != author_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
    if body:
        update_data["body"] = body
    if title:
        update_data["title"] = title
    if tags is not None:
        update_data["tags"] = tags
    
    await db.content_posts.update_one({"id": post_id}, {"$set": update_data})
    
    return {"success": True}

@router.delete("/posts/{post_id}")
async def delete_post(post_id: str, author_id: str):
    """Delete a post"""
    post = await db.content_posts.find_one({"id": post_id}, {"_id": 0})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post["author_id"] != author_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    await db.content_posts.delete_one({"id": post_id})
    await db.content_comments.delete_many({"post_id": post_id})
    await db.content_likes.delete_many({"target_id": post_id})
    
    return {"success": True}

# ============================================
# COMMENTS ENDPOINTS
# ============================================

@router.post("/posts/{post_id}/comments")
async def add_comment(post_id: str, author_id: str, author_name: str, body: str, parent_comment_id: Optional[str] = None):
    """Add a comment to a post"""
    comment = ContentComment(
        post_id=post_id,
        author_id=author_id,
        author_name=author_name,
        body=body,
        parent_comment_id=parent_comment_id
    )
    
    doc = comment.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.content_comments.insert_one(doc)
    await db.content_posts.update_one({"id": post_id}, {"$inc": {"comments_count": 1}})
    
    # Remove MongoDB _id before returning
    doc.pop('_id', None)
    
    # Send notification to post author
    if NOTIFICATIONS_ENABLED:
        post = await db.content_posts.find_one({"id": post_id}, {"_id": 0})
        if post and post.get("author_id") != author_id:
            await notify_comment_received(
                post["author_id"],
                author_name,
                author_id,
                post_id,
                body[:50]
            )
    
    return {"success": True, "comment": doc}

@router.delete("/comments/{comment_id}")
async def delete_comment(comment_id: str, author_id: str):
    """Delete a comment"""
    comment = await db.content_comments.find_one({"id": comment_id}, {"_id": 0})
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment["author_id"] != author_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    await db.content_comments.delete_one({"id": comment_id})
    await db.content_posts.update_one({"id": comment["post_id"]}, {"$inc": {"comments_count": -1}})
    
    return {"success": True}

# ============================================
# LIKES ENDPOINTS
# ============================================

@router.post("/like")
async def toggle_like(user_id: str, user_name: str = "Utilisateur", target_type: str = "post", target_id: str = ""):
    """Toggle like on post or comment"""
    existing = await db.content_likes.find_one({
        "user_id": user_id,
        "target_type": target_type,
        "target_id": target_id
    })
    
    if existing:
        # Unlike
        await db.content_likes.delete_one({"id": existing["id"]})
        collection = "content_posts" if target_type == "post" else "content_comments"
        await db[collection].update_one({"id": target_id}, {"$inc": {"likes_count": -1}})
        return {"success": True, "action": "unliked"}
    else:
        # Like
        like = ContentLike(user_id=user_id, target_type=target_type, target_id=target_id)
        doc = like.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.content_likes.insert_one(doc)
        collection = "content_posts" if target_type == "post" else "content_comments"
        await db[collection].update_one({"id": target_id}, {"$inc": {"likes_count": 1}})
        
        # Send notification to content owner
        if NOTIFICATIONS_ENABLED and target_type == "post":
            post = await db.content_posts.find_one({"id": target_id}, {"_id": 0})
            if post and post.get("author_id") != user_id:
                await notify_post_liked(
                    post["author_id"],
                    user_name,
                    user_id,
                    target_id,
                    post.get("title")
                )
        
        return {"success": True, "action": "liked"}

@router.get("/likes/{target_type}/{target_id}")
async def get_likes(target_type: str, target_id: str):
    """Get likes for a post or comment"""
    likes = await db.content_likes.find({
        "target_type": target_type,
        "target_id": target_id
    }, {"_id": 0}).to_list(1000)
    return {"likes": likes, "count": len(likes)}

# ============================================
# LEAD TRACKING ENDPOINTS
# ============================================

@router.get("/leads")
async def get_leads(
    owner_id: str,
    status: Optional[str] = None,
    source: Optional[str] = None,
    interest_type: Optional[str] = None
):
    """Get leads for a user"""
    query = {"owner_id": owner_id}
    if status:
        query["status"] = status
    if source:
        query["source"] = source
    if interest_type:
        query["interest_type"] = interest_type
    
    leads = await db.leads.find(query, {"_id": 0}).sort("created_at", -1).to_list(500)
    
    # Stats
    stats = {
        "total": len(leads),
        "new": len([l for l in leads if l.get("status") == "new"]),
        "contacted": len([l for l in leads if l.get("status") == "contacted"]),
        "interested": len([l for l in leads if l.get("status") == "interested"]),
        "converted": len([l for l in leads if l.get("status") == "converted"]),
        "total_estimated_value": sum(l.get("estimated_value", 0) for l in leads),
        "total_actual_value": sum(l.get("actual_value", 0) for l in leads if l.get("status") == "converted")
    }
    
    return {"leads": leads, "stats": stats}

@router.post("/leads")
async def create_lead(
    owner_id: str,
    name: str,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    source: str = "direct",
    source_details: Optional[str] = None,
    interest_type: str = "info",
    interest_details: Optional[str] = None,
    estimated_value: float = 0,
    tags: List[str] = []
):
    """Create a new lead"""
    lead = Lead(
        owner_id=owner_id,
        name=name,
        email=email,
        phone=phone,
        source=source,
        source_details=source_details,
        interest_type=interest_type,
        interest_details=interest_details,
        estimated_value=estimated_value,
        tags=tags
    )
    
    doc = lead.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.leads.insert_one(doc)
    
    # Remove MongoDB _id before returning
    doc.pop('_id', None)
    
    return {"success": True, "lead": doc}

@router.put("/leads/{lead_id}")
async def update_lead(
    lead_id: str,
    owner_id: str,
    status: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    interest_details: Optional[str] = None,
    estimated_value: Optional[float] = None,
    actual_value: Optional[float] = None,
    next_followup: Optional[str] = None,
    tags: Optional[List[str]] = None
):
    """Update a lead"""
    lead = await db.leads.find_one({"id": lead_id, "owner_id": owner_id}, {"_id": 0})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    update_data = {}
    if status:
        update_data["status"] = status
        if status == "converted":
            update_data["converted_at"] = datetime.now(timezone.utc).isoformat()
    if email:
        update_data["email"] = email
    if phone:
        update_data["phone"] = phone
    if interest_details:
        update_data["interest_details"] = interest_details
    if estimated_value is not None:
        update_data["estimated_value"] = estimated_value
    if actual_value is not None:
        update_data["actual_value"] = actual_value
    if next_followup:
        update_data["next_followup"] = next_followup
    if tags is not None:
        update_data["tags"] = tags
    
    if update_data:
        await db.leads.update_one({"id": lead_id}, {"$set": update_data})
    
    return {"success": True}

@router.post("/leads/{lead_id}/note")
async def add_lead_note(lead_id: str, owner_id: str, note: str):
    """Add a note to a lead"""
    lead = await db.leads.find_one({"id": lead_id, "owner_id": owner_id}, {"_id": 0})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    note_entry = {
        "date": datetime.now(timezone.utc).isoformat(),
        "note": note
    }
    
    await db.leads.update_one(
        {"id": lead_id},
        {
            "$push": {"notes": note_entry},
            "$set": {"last_contact": datetime.now(timezone.utc).isoformat()}
        }
    )
    
    return {"success": True, "note": note_entry}

@router.delete("/leads/{lead_id}")
async def delete_lead(lead_id: str, owner_id: str):
    """Delete a lead"""
    result = await db.leads.delete_one({"id": lead_id, "owner_id": owner_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"success": True}

# ============================================
# CONTACTS ENDPOINTS
# ============================================

@router.get("/contacts")
async def get_contacts(
    owner_id: str,
    relationship: Optional[str] = None,
    tag: Optional[str] = None,
    search: Optional[str] = None
):
    """Get contacts for a user"""
    query = {"owner_id": owner_id}
    if relationship:
        query["relationship"] = relationship
    if tag:
        query["tags"] = tag
    
    contacts = await db.contacts.find(query, {"_id": 0}).sort("name", 1).to_list(1000)
    
    # Search filter
    if search:
        search_lower = search.lower()
        contacts = [c for c in contacts if search_lower in c.get("name", "").lower() or search_lower in (c.get("email") or "").lower()]
    
    return {"contacts": contacts, "total": len(contacts)}

@router.post("/contacts")
async def create_contact(
    owner_id: str,
    name: str,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    company: Optional[str] = None,
    role: Optional[str] = None,
    relationship: str = "other",
    tags: List[str] = [],
    notes: Optional[str] = None
):
    """Create a new contact"""
    contact = Contact(
        owner_id=owner_id,
        name=name,
        email=email,
        phone=phone,
        company=company,
        role=role,
        relationship=relationship,
        tags=tags,
        notes=notes
    )
    
    doc = contact.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.contacts.insert_one(doc)
    
    # Remove MongoDB _id before returning
    doc.pop('_id', None)
    
    return {"success": True, "contact": doc}

@router.put("/contacts/{contact_id}")
async def update_contact(
    contact_id: str,
    owner_id: str,
    name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    company: Optional[str] = None,
    role: Optional[str] = None,
    relationship: Optional[str] = None,
    tags: Optional[List[str]] = None,
    notes: Optional[str] = None,
    is_favorite: Optional[bool] = None
):
    """Update a contact"""
    contact = await db.contacts.find_one({"id": contact_id, "owner_id": owner_id}, {"_id": 0})
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    update_data = {}
    if name:
        update_data["name"] = name
    if email is not None:
        update_data["email"] = email
    if phone is not None:
        update_data["phone"] = phone
    if company is not None:
        update_data["company"] = company
    if role is not None:
        update_data["role"] = role
    if relationship:
        update_data["relationship"] = relationship
    if tags is not None:
        update_data["tags"] = tags
    if notes is not None:
        update_data["notes"] = notes
    if is_favorite is not None:
        update_data["is_favorite"] = is_favorite
    
    if update_data:
        await db.contacts.update_one({"id": contact_id}, {"$set": update_data})
    
    return {"success": True}

@router.delete("/contacts/{contact_id}")
async def delete_contact(contact_id: str, owner_id: str):
    """Delete a contact"""
    result = await db.contacts.delete_one({"id": contact_id, "owner_id": owner_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Contact not found")
    return {"success": True}

# ============================================
# GROUPS ENDPOINTS
# ============================================

@router.get("/groups")
async def get_groups(user_id: str, include_public: bool = True):
    """Get groups for a user"""
    query = {
        "$or": [
            {"owner_id": user_id},
            {"member_ids": user_id}
        ]
    }
    
    groups = await db.groups.find(query, {"_id": 0}).to_list(100)
    
    if include_public:
        public_groups = await db.groups.find({"privacy": "public", "owner_id": {"$ne": user_id}, "member_ids": {"$nin": [user_id]}}, {"_id": 0}).limit(50).to_list(50)
        groups.extend(public_groups)
    
    return {"groups": groups, "total": len(groups)}

@router.get("/groups/{group_id}")
async def get_group(group_id: str):
    """Get group details with members"""
    group = await db.groups.find_one({"id": group_id}, {"_id": 0})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    members = await db.group_memberships.find({"group_id": group_id}, {"_id": 0}).to_list(500)
    
    return {"group": group, "members": members}

@router.post("/groups")
async def create_group(
    owner_id: str,
    owner_name: str,
    name: str,
    description: Optional[str] = None,
    group_type: str = "custom",
    privacy: str = "private"
):
    """Create a new group"""
    group = Group(
        owner_id=owner_id,
        name=name,
        description=description,
        group_type=group_type,
        privacy=privacy,
        member_ids=[owner_id],
        admin_ids=[owner_id],
        member_count=1
    )
    
    doc = group.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.groups.insert_one(doc)
    
    # Add owner as member
    membership = GroupMembership(
        group_id=group.id,
        user_id=owner_id,
        user_name=owner_name,
        role="owner"
    )
    membership_doc = membership.model_dump()
    membership_doc['joined_at'] = membership_doc['joined_at'].isoformat()
    await db.group_memberships.insert_one(membership_doc)
    
    # Remove MongoDB _id before returning
    doc.pop('_id', None)
    
    return {"success": True, "group": doc}

@router.post("/groups/{group_id}/join")
async def join_group(group_id: str, user_id: str, user_name: str):
    """Join a group"""
    group = await db.groups.find_one({"id": group_id}, {"_id": 0})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    if group["privacy"] == "invite_only":
        raise HTTPException(status_code=403, detail="This group is invite only")
    
    if user_id in group.get("member_ids", []):
        raise HTTPException(status_code=400, detail="Already a member")
    
    membership = GroupMembership(
        group_id=group_id,
        user_id=user_id,
        user_name=user_name,
        role="member"
    )
    membership_doc = membership.model_dump()
    membership_doc['joined_at'] = membership_doc['joined_at'].isoformat()
    await db.group_memberships.insert_one(membership_doc)
    
    await db.groups.update_one(
        {"id": group_id},
        {
            "$push": {"member_ids": user_id},
            "$inc": {"member_count": 1}
        }
    )
    
    # Notify group owner
    if NOTIFICATIONS_ENABLED and group.get("owner_id") != user_id:
        await notify_group_join(
            group["owner_id"],
            user_name,
            user_id,
            group_id,
            group.get("name", "groupe")
        )
    
    return {"success": True}

@router.post("/groups/{group_id}/leave")
async def leave_group(group_id: str, user_id: str):
    """Leave a group"""
    group = await db.groups.find_one({"id": group_id}, {"_id": 0})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    if group["owner_id"] == user_id:
        raise HTTPException(status_code=400, detail="Owner cannot leave. Transfer ownership or delete the group.")
    
    await db.group_memberships.delete_one({"group_id": group_id, "user_id": user_id})
    
    await db.groups.update_one(
        {"id": group_id},
        {
            "$pull": {"member_ids": user_id, "admin_ids": user_id},
            "$inc": {"member_count": -1}
        }
    )
    
    return {"success": True}

@router.delete("/groups/{group_id}")
async def delete_group(group_id: str, owner_id: str):
    """Delete a group"""
    group = await db.groups.find_one({"id": group_id, "owner_id": owner_id}, {"_id": 0})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found or not authorized")
    
    await db.groups.delete_one({"id": group_id})
    await db.group_memberships.delete_many({"group_id": group_id})
    
    return {"success": True}

# ============================================
# REFERRAL & REWARDS ENDPOINTS
# ============================================

@router.get("/referral/code/{user_id}")
async def get_referral_code(user_id: str):
    """Get or create referral code for a user"""
    code = await db.referral_codes.find_one({"owner_id": user_id, "is_active": True}, {"_id": 0})
    
    if not code:
        # Generate new code
        import random
        import string
        code_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        new_code = ReferralCode(
            owner_id=user_id,
            code=code_str,
            reward_type="credits",
            referrer_reward=10.0,
            referee_reward=5.0
        )
        
        doc = new_code.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.referral_codes.insert_one(doc)
        # Remove MongoDB _id before returning
        doc.pop('_id', None)
        code = doc
    
    # Get referral stats
    referrals = await db.referrals.find({"referrer_id": user_id}, {"_id": 0}).to_list(1000)
    stats = {
        "total_referrals": len(referrals),
        "pending": len([r for r in referrals if r.get("status") == "pending"]),
        "verified": len([r for r in referrals if r.get("status") == "verified"]),
        "rewarded": len([r for r in referrals if r.get("status") == "rewarded"]),
        "total_earned": sum(r.get("referrer_reward_amount", 0) for r in referrals if r.get("status") == "rewarded")
    }
    
    return {"code": code, "stats": stats}

@router.post("/referral/use")
async def use_referral_code(referee_id: str, code: str, action_type: str = "signup"):
    """Use a referral code"""
    referral_code = await db.referral_codes.find_one({"code": code, "is_active": True}, {"_id": 0})
    if not referral_code:
        raise HTTPException(status_code=404, detail="Invalid or expired referral code")
    
    if referral_code["owner_id"] == referee_id:
        raise HTTPException(status_code=400, detail="Cannot use your own referral code")
    
    # Check if already used
    existing = await db.referrals.find_one({"referee_id": referee_id, "referral_code": code})
    if existing:
        raise HTTPException(status_code=400, detail="Referral code already used")
    
    # Create referral
    referral = Referral(
        referrer_id=referral_code["owner_id"],
        referee_id=referee_id,
        referral_code=code,
        status="pending",
        referrer_reward_amount=referral_code.get("referrer_reward", 10),
        referee_reward_amount=referral_code.get("referee_reward", 5),
        action_type=action_type
    )
    
    doc = referral.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.referrals.insert_one(doc)
    
    # Update code uses count
    await db.referral_codes.update_one({"code": code}, {"$inc": {"uses_count": 1}})
    
    # Notify referrer
    if NOTIFICATIONS_ENABLED:
        await notify_referral_signup(referral_code["owner_id"], "Nouvel utilisateur", code)
    
    return {"success": True, "referral_id": referral.id}

@router.post("/referral/{referral_id}/verify")
async def verify_referral(referral_id: str):
    """Verify and reward a referral (admin or system)"""
    referral = await db.referrals.find_one({"id": referral_id}, {"_id": 0})
    if not referral:
        raise HTTPException(status_code=404, detail="Referral not found")
    
    if referral["status"] != "pending":
        raise HTTPException(status_code=400, detail="Referral already processed")
    
    now = datetime.now(timezone.utc).isoformat()
    
    # Update referral status
    await db.referrals.update_one(
        {"id": referral_id},
        {"$set": {"status": "rewarded", "verified_at": now, "rewarded_at": now}}
    )
    
    # Add rewards to wallets
    for user_id, amount, desc in [
        (referral["referrer_id"], referral["referrer_reward_amount"], "Bonus de parrainage"),
        (referral["referee_id"], referral["referee_reward_amount"], "Bonus de bienvenue")
    ]:
        await _add_wallet_credits(user_id, amount, "referral_bonus", referral_id, desc)
    
    # Notify both users
    if NOTIFICATIONS_ENABLED:
        await notify_referral_rewarded(referral["referrer_id"], referral["referrer_reward_amount"], is_referrer=True)
        await notify_referral_rewarded(referral["referee_id"], referral["referee_reward_amount"], is_referrer=False)
    
    return {"success": True}

@router.get("/referrals/{user_id}")
async def get_user_referrals(user_id: str):
    """Get referrals made by a user"""
    referrals = await db.referrals.find({"referrer_id": user_id}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return {"referrals": referrals}

# ============================================
# WALLET ENDPOINTS
# ============================================

async def _get_or_create_wallet(user_id: str) -> dict:
    """Get or create wallet for user"""
    wallet = await db.wallets.find_one({"user_id": user_id}, {"_id": 0})
    if not wallet:
        new_wallet = Wallet(user_id=user_id)
        doc = new_wallet.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.wallets.insert_one(doc)
        # Remove MongoDB _id before returning
        doc.pop('_id', None)
        wallet = doc
    return wallet

async def _add_wallet_credits(user_id: str, amount: float, tx_type: str, reference_id: str, description: str):
    """Add credits to wallet"""
    wallet = await _get_or_create_wallet(user_id)
    
    balance_before = wallet.get("balance_credits", 0)
    balance_after = balance_before + amount
    
    # Create transaction
    tx = WalletTransaction(
        wallet_id=wallet["id"],
        user_id=user_id,
        transaction_type="reward",
        amount=amount,
        currency="credits",
        balance_before=balance_before,
        balance_after=balance_after,
        reference_type=tx_type,
        reference_id=reference_id,
        description=description
    )
    
    tx_doc = tx.model_dump()
    tx_doc['created_at'] = tx_doc['created_at'].isoformat()
    await db.wallet_transactions.insert_one(tx_doc)
    
    # Update wallet
    await db.wallets.update_one(
        {"user_id": user_id},
        {
            "$set": {"balance_credits": balance_after, "updated_at": datetime.now(timezone.utc).isoformat()},
            "$inc": {"total_earned": amount}
        }
    )

@router.get("/wallet/{user_id}")
async def get_wallet(user_id: str):
    """Get wallet for a user"""
    wallet = await _get_or_create_wallet(user_id)
    transactions = await db.wallet_transactions.find({"user_id": user_id}, {"_id": 0}).sort("created_at", -1).limit(50).to_list(50)
    
    return {"wallet": wallet, "recent_transactions": transactions}

@router.get("/wallet/{user_id}/transactions")
async def get_wallet_transactions(
    user_id: str,
    transaction_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Get wallet transactions"""
    query = {"user_id": user_id}
    if transaction_type:
        query["transaction_type"] = transaction_type
    
    transactions = await db.wallet_transactions.find(query, {"_id": 0}).sort("created_at", -1).skip(offset).limit(limit).to_list(limit)
    total = await db.wallet_transactions.count_documents(query)
    
    return {"transactions": transactions, "total": total}

@router.post("/wallet/transfer")
async def transfer_credits(from_user_id: str, to_user_id: str, amount: float, description: str = "Transfer"):
    """Transfer credits between users"""
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    from_wallet = await _get_or_create_wallet(from_user_id)
    if from_wallet.get("balance_credits", 0) < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    to_wallet = await _get_or_create_wallet(to_user_id)
    
    now = datetime.now(timezone.utc).isoformat()
    
    # Debit from sender
    from_balance_before = from_wallet.get("balance_credits", 0)
    from_balance_after = from_balance_before - amount
    
    tx_out = WalletTransaction(
        wallet_id=from_wallet["id"],
        user_id=from_user_id,
        transaction_type="transfer_out",
        amount=-amount,
        currency="credits",
        balance_before=from_balance_before,
        balance_after=from_balance_after,
        reference_type="transfer",
        reference_id=to_user_id,
        description=f"Transfert vers utilisateur: {description}"
    )
    tx_out_doc = tx_out.model_dump()
    tx_out_doc['created_at'] = now
    await db.wallet_transactions.insert_one(tx_out_doc)
    
    await db.wallets.update_one(
        {"user_id": from_user_id},
        {"$set": {"balance_credits": from_balance_after, "updated_at": now}, "$inc": {"total_spent": amount}}
    )
    
    # Credit to receiver
    to_balance_before = to_wallet.get("balance_credits", 0)
    to_balance_after = to_balance_before + amount
    
    tx_in = WalletTransaction(
        wallet_id=to_wallet["id"],
        user_id=to_user_id,
        transaction_type="transfer_in",
        amount=amount,
        currency="credits",
        balance_before=to_balance_before,
        balance_after=to_balance_after,
        reference_type="transfer",
        reference_id=from_user_id,
        description=f"Transfert reçu: {description}"
    )
    tx_in_doc = tx_in.model_dump()
    tx_in_doc['created_at'] = now
    await db.wallet_transactions.insert_one(tx_in_doc)
    
    await db.wallets.update_one(
        {"user_id": to_user_id},
        {"$set": {"balance_credits": to_balance_after, "updated_at": now}, "$inc": {"total_earned": amount}}
    )
    
    return {"success": True, "from_balance": from_balance_after, "to_balance": to_balance_after}

# ============================================
# ADMIN ENDPOINTS
# ============================================

@router.get("/admin/stats")
async def get_networking_stats():
    """Get networking ecosystem stats for admin"""
    stats = {
        "posts": {
            "total": await db.content_posts.count_documents({}),
            "this_week": await db.content_posts.count_documents({
                "created_at": {"$gte": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()}
            })
        },
        "leads": {
            "total": await db.leads.count_documents({}),
            "new": await db.leads.count_documents({"status": "new"}),
            "converted": await db.leads.count_documents({"status": "converted"})
        },
        "contacts": {
            "total": await db.contacts.count_documents({})
        },
        "groups": {
            "total": await db.groups.count_documents({}),
            "active": await db.groups.count_documents({"is_active": True})
        },
        "referrals": {
            "total": await db.referrals.count_documents({}),
            "pending": await db.referrals.count_documents({"status": "pending"}),
            "rewarded": await db.referrals.count_documents({"status": "rewarded"})
        },
        "wallets": {
            "total": await db.wallets.count_documents({}),
            "total_credits": 0  # Will calculate below
        }
    }
    
    # Calculate total credits in circulation
    wallets = await db.wallets.find({}, {"balance_credits": 1, "_id": 0}).to_list(10000)
    stats["wallets"]["total_credits"] = sum(w.get("balance_credits", 0) for w in wallets)
    
    return stats

@router.get("/admin/pending-referrals")
async def get_pending_referrals():
    """Get pending referrals for admin approval"""
    referrals = await db.referrals.find({"status": "pending"}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return {"referrals": referrals}
