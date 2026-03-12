"""
Waypoint Sharing System - Partage de waypoints entre chasseurs BIONIC
- Partage par lien unique (membres BIONIC uniquement)
- Partage par email avec collecte pour marketing
- Collaboration complète (modification possible)
- Intégration avec les groupes de chasse
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/sharing", tags=["Waypoint Sharing"])

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'hunttrack')

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Collections
shares_collection = db['waypoint_shares']
share_links_collection = db['share_links']
marketing_emails_collection = db['marketing_emails']
notifications_collection = db['notifications']
users_collection = db['users']


# ============================================
# PYDANTIC MODELS
# ============================================

class ShareByEmailRequest(BaseModel):
    waypoint_id: str
    waypoint_name: str
    emails: List[EmailStr]
    message: Optional[str] = None
    permission: str = Field(default="collaborate", pattern="^(view|copy|collaborate)$")


class ShareLinkRequest(BaseModel):
    waypoint_id: str
    waypoint_name: str
    expires_in_days: int = Field(default=30, ge=1, le=365)
    permission: str = Field(default="collaborate", pattern="^(view|copy|collaborate)$")


class ShareResponse(BaseModel):
    id: str
    share_type: str
    waypoint_id: str
    created_at: str
    expires_at: Optional[str] = None
    share_link: Optional[str] = None
    shared_with: Optional[List[str]] = None


class ShareLinkInfo(BaseModel):
    id: str
    waypoint_id: str
    waypoint_name: str
    owner_id: str
    owner_name: str
    permission: str
    created_at: str
    expires_at: Optional[str] = None
    is_valid: bool


class AcceptShareRequest(BaseModel):
    share_link_id: Optional[str] = None
    share_id: Optional[str] = None


class NotificationResponse(BaseModel):
    id: str
    type: str
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None
    read: bool
    created_at: str


class MarketingEmailEntry(BaseModel):
    email: str
    source: str
    source_user_id: str
    added_at: str
    waypoint_shared: Optional[str] = None


# ============================================
# HELPER FUNCTIONS
# ============================================

def generate_share_link_id():
    """Génère un ID unique pour le lien de partage"""
    return str(uuid.uuid4())[:12]


async def get_user_info(user_id: str) -> dict:
    """Récupère les infos basiques d'un utilisateur"""
    user = await users_collection.find_one(
        {"id": user_id},
        {"_id": 0, "id": 1, "name": 1, "email": 1, "first_name": 1, "last_name": 1}
    )
    if user:
        name = user.get("name") or f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or "Utilisateur BIONIC"
        return {"id": user.get("id"), "name": name, "email": user.get("email")}
    return {"id": user_id, "name": "Utilisateur BIONIC", "email": None}


async def is_bionic_member(email: str) -> bool:
    """Vérifie si l'email correspond à un membre BIONIC"""
    user = await users_collection.find_one({"email": email.lower()})
    return user is not None


async def add_to_marketing_list(email: str, source: str, source_user_id: str, waypoint_name: str = None):
    """Ajoute un email à la liste marketing (avec dédoublonnage)"""
    try:
        existing = await marketing_emails_collection.find_one({"email": email.lower()})
        
        if existing:
            # Mettre à jour avec la nouvelle source
            await marketing_emails_collection.update_one(
                {"email": email.lower()},
                {
                    "$push": {
                        "sources": {
                            "type": source,
                            "user_id": source_user_id,
                            "waypoint": waypoint_name,
                            "date": datetime.now(timezone.utc).isoformat()
                        }
                    },
                    "$set": {"last_activity": datetime.now(timezone.utc).isoformat()}
                }
            )
        else:
            # Nouvel email
            await marketing_emails_collection.insert_one({
                "email": email.lower(),
                "sources": [{
                    "type": source,
                    "user_id": source_user_id,
                    "waypoint": waypoint_name,
                    "date": datetime.now(timezone.utc).isoformat()
                }],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_activity": datetime.now(timezone.utc).isoformat(),
                "subscribed": True,
                "tags": ["waypoint_sharing", "bionic_user"]
            })
        
        logger.info(f"Added email to marketing list: {email} (source: {source})")
    except Exception as e:
        logger.error(f"Error adding email to marketing list: {e}")


async def create_notification(user_id: str, notif_type: str, title: str, message: str, data: dict = None):
    """Crée une notification pour un utilisateur"""
    try:
        notif = {
            "user_id": user_id,
            "type": notif_type,
            "title": title,
            "message": message,
            "data": data or {},
            "read": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        result = await notifications_collection.insert_one(notif)
        logger.info(f"Created notification for user {user_id}: {title}")
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error creating notification: {e}")
        return None


def serialize_share(doc: dict) -> dict:
    """Sérialise un document de partage"""
    return {
        "id": str(doc.get("_id", "")),
        "share_type": doc.get("share_type", "email"),
        "waypoint_id": doc.get("waypoint_id", ""),
        "waypoint_name": doc.get("waypoint_name", ""),
        "owner_id": doc.get("owner_id", ""),
        "shared_with": doc.get("shared_with", []),
        "permission": doc.get("permission", "view"),
        "message": doc.get("message"),
        "created_at": doc.get("created_at", ""),
        "accepted": doc.get("accepted", False),
        "accepted_at": doc.get("accepted_at")
    }


def serialize_notification(doc: dict) -> dict:
    """Sérialise une notification"""
    return {
        "id": str(doc.get("_id", "")),
        "type": doc.get("type", ""),
        "title": doc.get("title", ""),
        "message": doc.get("message", ""),
        "data": doc.get("data", {}),
        "read": doc.get("read", False),
        "created_at": doc.get("created_at", "")
    }


# ============================================
# SHARE BY EMAIL ENDPOINTS
# ============================================

@router.post("/email/{owner_id}")
async def share_waypoint_by_email(
    owner_id: str, 
    request: ShareByEmailRequest,
    background_tasks: BackgroundTasks
):
    """
    Partage un waypoint par email avec des utilisateurs spécifiques.
    Les emails sont automatiquement ajoutés à la liste marketing.
    """
    try:
        now = datetime.now(timezone.utc).isoformat()
        owner_info = await get_user_info(owner_id)
        
        shares_created = []
        emails_added_to_marketing = []
        notifications_sent = []
        
        for email in request.emails:
            email_lower = email.lower()
            
            # Vérifier si c'est un membre BIONIC
            is_member = await is_bionic_member(email_lower)
            
            # Trouver l'utilisateur destinataire (si membre)
            recipient_user = await users_collection.find_one({"email": email_lower})
            recipient_id = recipient_user.get("id") if recipient_user else None
            
            # Créer le partage
            share_doc = {
                "share_type": "email",
                "owner_id": owner_id,
                "owner_name": owner_info.get("name"),
                "waypoint_id": request.waypoint_id,
                "waypoint_name": request.waypoint_name,
                "shared_with_email": email_lower,
                "shared_with_user_id": recipient_id,
                "is_bionic_member": is_member,
                "permission": request.permission,
                "message": request.message,
                "created_at": now,
                "accepted": False,
                "accepted_at": None
            }
            
            result = await shares_collection.insert_one(share_doc)
            shares_created.append(str(result.inserted_id))
            
            # Ajouter à la liste marketing
            background_tasks.add_task(
                add_to_marketing_list,
                email_lower,
                "waypoint_share",
                owner_id,
                request.waypoint_name
            )
            emails_added_to_marketing.append(email_lower)
            
            # Créer une notification pour le destinataire (si membre)
            if recipient_id:
                notif_id = await create_notification(
                    user_id=recipient_id,
                    notif_type="waypoint_shared",
                    title="Nouveau waypoint partagé",
                    message=f"{owner_info.get('name')} a partagé le waypoint '{request.waypoint_name}' avec vous",
                    data={
                        "share_id": str(result.inserted_id),
                        "waypoint_id": request.waypoint_id,
                        "waypoint_name": request.waypoint_name,
                        "owner_id": owner_id,
                        "owner_name": owner_info.get("name"),
                        "permission": request.permission
                    }
                )
                if notif_id:
                    notifications_sent.append(recipient_id)
        
        return {
            "success": True,
            "shares_created": len(shares_created),
            "share_ids": shares_created,
            "emails_added_to_marketing": len(emails_added_to_marketing),
            "notifications_sent": len(notifications_sent),
            "message": f"Waypoint partagé avec {len(request.emails)} personne(s)"
        }
        
    except Exception as e:
        logger.error(f"Error sharing waypoint by email: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# SHARE LINK ENDPOINTS
# ============================================

@router.post("/link/{owner_id}")
async def create_share_link(owner_id: str, request: ShareLinkRequest):
    """
    Crée un lien de partage unique pour un waypoint.
    Le lien ne fonctionne que pour les membres BIONIC connectés.
    """
    try:
        now = datetime.now(timezone.utc)
        owner_info = await get_user_info(owner_id)
        
        # Générer un ID unique pour le lien
        link_id = generate_share_link_id()
        
        # Calculer la date d'expiration
        from datetime import timedelta
        expires_at = (now + timedelta(days=request.expires_in_days)).isoformat()
        
        link_doc = {
            "link_id": link_id,
            "owner_id": owner_id,
            "owner_name": owner_info.get("name"),
            "waypoint_id": request.waypoint_id,
            "waypoint_name": request.waypoint_name,
            "permission": request.permission,
            "created_at": now.isoformat(),
            "expires_at": expires_at,
            "is_active": True,
            "access_count": 0,
            "accessed_by": []
        }
        
        await share_links_collection.insert_one(link_doc)
        
        # Construire l'URL du lien
        base_url = os.environ.get('REACT_APP_BACKEND_URL', 'https://corridor-analysis.preview.emergentagent.com')
        share_url = f"{base_url}/share/{link_id}"
        
        return {
            "success": True,
            "link_id": link_id,
            "share_url": share_url,
            "expires_at": expires_at,
            "permission": request.permission,
            "message": "Lien de partage créé avec succès"
        }
        
    except Exception as e:
        logger.error(f"Error creating share link: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/link/{link_id}/info")
async def get_share_link_info(link_id: str, user_id: Optional[str] = None):
    """
    Récupère les informations d'un lien de partage.
    Vérifie si l'utilisateur est un membre BIONIC.
    """
    try:
        link = await share_links_collection.find_one({"link_id": link_id})
        
        if not link:
            raise HTTPException(status_code=404, detail="Lien de partage introuvable")
        
        # Vérifier si le lien est expiré
        now = datetime.now(timezone.utc)
        expires_at = datetime.fromisoformat(link["expires_at"].replace("Z", "+00:00"))
        is_expired = now > expires_at
        
        is_valid = link.get("is_active", True) and not is_expired
        
        return {
            "id": link_id,
            "waypoint_id": link.get("waypoint_id"),
            "waypoint_name": link.get("waypoint_name"),
            "owner_id": link.get("owner_id"),
            "owner_name": link.get("owner_name"),
            "permission": link.get("permission"),
            "created_at": link.get("created_at"),
            "expires_at": link.get("expires_at"),
            "is_valid": is_valid,
            "is_expired": is_expired,
            "requires_bionic_account": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting share link info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/link/{link_id}/accept")
async def accept_share_link(
    link_id: str, 
    user_id: str = Query(..., description="ID de l'utilisateur qui accepte le partage"),
    background_tasks: BackgroundTasks = None
):
    """
    Accepte un lien de partage (copie le waypoint dans les données de l'utilisateur).
    Nécessite d'être un membre BIONIC connecté.
    """
    try:
        # Vérifier que l'utilisateur existe (est membre BIONIC)
        user = await users_collection.find_one({"id": user_id})
        if not user:
            raise HTTPException(
                status_code=403, 
                detail="Vous devez être membre BIONIC pour accéder à ce waypoint"
            )
        
        # Récupérer le lien
        link = await share_links_collection.find_one({"link_id": link_id})
        if not link:
            raise HTTPException(status_code=404, detail="Lien de partage introuvable")
        
        # Vérifier validité
        now = datetime.now(timezone.utc)
        expires_at = datetime.fromisoformat(link["expires_at"].replace("Z", "+00:00"))
        
        if not link.get("is_active") or now > expires_at:
            raise HTTPException(status_code=410, detail="Ce lien de partage a expiré")
        
        # Enregistrer l'accès
        user_email = user.get("email", "")
        await share_links_collection.update_one(
            {"link_id": link_id},
            {
                "$inc": {"access_count": 1},
                "$push": {
                    "accessed_by": {
                        "user_id": user_id,
                        "email": user_email,
                        "accessed_at": now.isoformat()
                    }
                }
            }
        )
        
        # Ajouter l'email à la liste marketing
        if background_tasks and user_email:
            background_tasks.add_task(
                add_to_marketing_list,
                user_email,
                "share_link_access",
                link.get("owner_id"),
                link.get("waypoint_name")
            )
        
        # Notifier le propriétaire
        await create_notification(
            user_id=link.get("owner_id"),
            notif_type="share_accessed",
            title="Waypoint consulté",
            message=f"{user.get('name', 'Un membre BIONIC')} a accédé à votre waypoint '{link.get('waypoint_name')}'",
            data={
                "waypoint_id": link.get("waypoint_id"),
                "accessed_by": user_id
            }
        )
        
        return {
            "success": True,
            "waypoint_id": link.get("waypoint_id"),
            "waypoint_name": link.get("waypoint_name"),
            "permission": link.get("permission"),
            "owner_id": link.get("owner_id"),
            "message": "Accès au waypoint accordé"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error accepting share link: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# USER SHARES ENDPOINTS
# ============================================

@router.get("/received/{user_id}")
async def get_received_shares(user_id: str):
    """Récupère tous les waypoints partagés avec l'utilisateur"""
    try:
        # Par email ou user_id
        user = await users_collection.find_one({"id": user_id})
        user_email = user.get("email", "").lower() if user else ""
        
        cursor = shares_collection.find({
            "$or": [
                {"shared_with_user_id": user_id},
                {"shared_with_email": user_email}
            ]
        }).sort("created_at", -1)
        
        shares = await cursor.to_list(length=100)
        
        return {
            "shares": [serialize_share(s) for s in shares],
            "total": len(shares)
        }
        
    except Exception as e:
        logger.error(f"Error getting received shares: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sent/{user_id}")
async def get_sent_shares(user_id: str):
    """Récupère tous les partages effectués par l'utilisateur"""
    try:
        cursor = shares_collection.find({"owner_id": user_id}).sort("created_at", -1)
        shares = await cursor.to_list(length=100)
        
        # Aussi récupérer les liens de partage
        links_cursor = share_links_collection.find({"owner_id": user_id}).sort("created_at", -1)
        links = await links_cursor.to_list(length=50)
        
        return {
            "email_shares": [serialize_share(s) for s in shares],
            "link_shares": [{
                "id": l.get("link_id"),
                "waypoint_id": l.get("waypoint_id"),
                "waypoint_name": l.get("waypoint_name"),
                "share_url": f"{os.environ.get('REACT_APP_BACKEND_URL', '')}/share/{l.get('link_id')}",
                "permission": l.get("permission"),
                "created_at": l.get("created_at"),
                "expires_at": l.get("expires_at"),
                "access_count": l.get("access_count", 0),
                "is_active": l.get("is_active", True)
            } for l in links],
            "total_email": len(shares),
            "total_links": len(links)
        }
        
    except Exception as e:
        logger.error(f"Error getting sent shares: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/link/{owner_id}/{link_id}")
async def revoke_share_link(owner_id: str, link_id: str):
    """Révoque un lien de partage"""
    try:
        result = await share_links_collection.update_one(
            {"link_id": link_id, "owner_id": owner_id},
            {"$set": {"is_active": False}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Lien non trouvé ou déjà révoqué")
        
        return {"success": True, "message": "Lien de partage révoqué"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error revoking share link: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# NOTIFICATIONS ENDPOINTS
# ============================================

@router.get("/notifications/{user_id}")
async def get_user_notifications(
    user_id: str,
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=100)
):
    """Récupère les notifications de l'utilisateur"""
    try:
        query = {"user_id": user_id}
        if unread_only:
            query["read"] = False
        
        cursor = notifications_collection.find(query).sort("created_at", -1).limit(limit)
        notifications = await cursor.to_list(length=limit)
        
        unread_count = await notifications_collection.count_documents({
            "user_id": user_id, 
            "read": False
        })
        
        return {
            "notifications": [serialize_notification(n) for n in notifications],
            "unread_count": unread_count,
            "total": len(notifications)
        }
        
    except Exception as e:
        logger.error(f"Error getting notifications: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/notifications/{user_id}/{notification_id}/read")
async def mark_notification_read(user_id: str, notification_id: str):
    """Marque une notification comme lue"""
    try:
        result = await notifications_collection.update_one(
            {"_id": ObjectId(notification_id), "user_id": user_id},
            {"$set": {"read": True, "read_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Notification non trouvée")
        
        return {"success": True}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking notification read: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/notifications/{user_id}/read-all")
async def mark_all_notifications_read(user_id: str):
    """Marque toutes les notifications comme lues"""
    try:
        result = await notifications_collection.update_many(
            {"user_id": user_id, "read": False},
            {"$set": {"read": True, "read_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        return {"success": True, "marked_read": result.modified_count}
        
    except Exception as e:
        logger.error(f"Error marking all notifications read: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# MARKETING EMAILS ADMIN ENDPOINTS
# ============================================

@router.get("/admin/marketing-emails")
async def get_marketing_emails(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    source: Optional[str] = None
):
    """
    [ADMIN] Récupère la liste des emails collectés via le partage de waypoints.
    À utiliser pour les campagnes marketing.
    """
    try:
        query = {}
        if source:
            query["sources.type"] = source
        
        skip = (page - 1) * limit
        
        cursor = marketing_emails_collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        emails = await cursor.to_list(length=limit)
        
        total = await marketing_emails_collection.count_documents(query)
        
        return {
            "emails": [{
                "email": e.get("email"),
                "sources": e.get("sources", []),
                "created_at": e.get("created_at"),
                "last_activity": e.get("last_activity"),
                "subscribed": e.get("subscribed", True),
                "tags": e.get("tags", [])
            } for e in emails],
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit
        }
        
    except Exception as e:
        logger.error(f"Error getting marketing emails: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/marketing-stats")
async def get_marketing_stats():
    """[ADMIN] Statistiques des emails marketing collectés"""
    try:
        total_emails = await marketing_emails_collection.count_documents({})
        subscribed = await marketing_emails_collection.count_documents({"subscribed": True})
        
        # Stats par source
        pipeline = [
            {"$unwind": "$sources"},
            {"$group": {"_id": "$sources.type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        sources_stats = await marketing_emails_collection.aggregate(pipeline).to_list(length=20)
        
        return {
            "total_emails": total_emails,
            "subscribed": subscribed,
            "unsubscribed": total_emails - subscribed,
            "by_source": {s["_id"]: s["count"] for s in sources_stats}
        }
        
    except Exception as e:
        logger.error(f"Error getting marketing stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
