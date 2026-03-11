"""
Hunting Groups (Groupes de Chasse) - Équipes de chasseurs BIONIC
- Création et gestion de groupes
- Ajout/suppression de membres
- Partage de waypoints avec le groupe entier
- Notifications de groupe
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/groups", tags=["Hunting Groups"])

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'hunttrack')

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Collections
groups_collection = db['hunting_groups']
group_invites_collection = db['group_invites']
notifications_collection = db['notifications']
users_collection = db['users']
marketing_emails_collection = db['marketing_emails']
# NOTE: Waypoints are now managed via geo_entities collection (geo_engine)


# ============================================
# PYDANTIC MODELS
# ============================================

class GroupCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    is_public: bool = Field(default=False)
    max_members: int = Field(default=20, ge=2, le=100)


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    max_members: Optional[int] = None


class GroupInvite(BaseModel):
    emails: List[EmailStr]
    message: Optional[str] = None


class GroupMember(BaseModel):
    user_id: str
    name: str
    email: str
    role: str  # owner, admin, member
    joined_at: str


class Group(BaseModel):
    id: str
    name: str
    description: Optional[str]
    owner_id: str
    owner_name: str
    is_public: bool
    max_members: int
    member_count: int
    created_at: str


class SharedWaypoint(BaseModel):
    waypoint_id: str
    waypoint_name: str
    shared_by: str
    shared_at: str
    permission: str


# ============================================
# HELPER FUNCTIONS
# ============================================

def generate_invite_code():
    """Génère un code d'invitation unique"""
    return str(uuid.uuid4())[:8].upper()


async def get_user_info(user_id: str) -> dict:
    """Récupère les infos basiques d'un utilisateur"""
    user = await users_collection.find_one(
        {"id": user_id},
        {"_id": 0, "id": 1, "name": 1, "email": 1, "first_name": 1, "last_name": 1}
    )
    if user:
        name = user.get("name") or f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or "Chasseur BIONIC"
        return {"id": user.get("id"), "name": name, "email": user.get("email")}
    return {"id": user_id, "name": "Chasseur BIONIC", "email": None}


async def create_notification(user_id: str, notif_type: str, title: str, message: str, data: dict = None):
    """Crée une notification"""
    try:
        await notifications_collection.insert_one({
            "user_id": user_id,
            "type": notif_type,
            "title": title,
            "message": message,
            "data": data or {},
            "read": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
    except Exception as e:
        logger.error(f"Error creating notification: {e}")


async def add_to_marketing_list(email: str, source: str, source_user_id: str, group_name: str = None):
    """Ajoute un email à la liste marketing"""
    try:
        existing = await marketing_emails_collection.find_one({"email": email.lower()})
        
        if existing:
            await marketing_emails_collection.update_one(
                {"email": email.lower()},
                {
                    "$push": {
                        "sources": {
                            "type": source,
                            "user_id": source_user_id,
                            "group": group_name,
                            "date": datetime.now(timezone.utc).isoformat()
                        }
                    },
                    "$addToSet": {"tags": "hunting_group"},
                    "$set": {"last_activity": datetime.now(timezone.utc).isoformat()}
                }
            )
        else:
            await marketing_emails_collection.insert_one({
                "email": email.lower(),
                "sources": [{
                    "type": source,
                    "user_id": source_user_id,
                    "group": group_name,
                    "date": datetime.now(timezone.utc).isoformat()
                }],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_activity": datetime.now(timezone.utc).isoformat(),
                "subscribed": True,
                "tags": ["hunting_group", "bionic_user"]
            })
    except Exception as e:
        logger.error(f"Error adding email to marketing list: {e}")


def serialize_group(doc: dict, include_members: bool = False) -> dict:
    """Sérialise un groupe"""
    result = {
        "id": str(doc.get("_id", "")),
        "name": doc.get("name", ""),
        "description": doc.get("description"),
        "owner_id": doc.get("owner_id", ""),
        "owner_name": doc.get("owner_name", ""),
        "is_public": doc.get("is_public", False),
        "max_members": doc.get("max_members", 20),
        "member_count": len(doc.get("members", [])),
        "invite_code": doc.get("invite_code"),
        "created_at": doc.get("created_at", ""),
        "shared_waypoints_count": len(doc.get("shared_waypoints", []))
    }
    
    if include_members:
        result["members"] = doc.get("members", [])
        result["shared_waypoints"] = doc.get("shared_waypoints", [])
    
    return result


# ============================================
# GROUP CRUD ENDPOINTS
# ============================================

@router.post("/{owner_id}")
async def create_group(owner_id: str, group: GroupCreate):
    """Crée un nouveau groupe de chasse"""
    try:
        owner_info = await get_user_info(owner_id)
        now = datetime.now(timezone.utc).isoformat()
        
        # Vérifier le nombre de groupes de l'utilisateur (limite à 5)
        existing_count = await groups_collection.count_documents({"owner_id": owner_id})
        if existing_count >= 5:
            raise HTTPException(
                status_code=400, 
                detail="Vous avez atteint la limite de 5 groupes"
            )
        
        group_doc = {
            "name": group.name,
            "description": group.description,
            "owner_id": owner_id,
            "owner_name": owner_info.get("name"),
            "is_public": group.is_public,
            "max_members": group.max_members,
            "invite_code": generate_invite_code(),
            "members": [{
                "user_id": owner_id,
                "name": owner_info.get("name"),
                "email": owner_info.get("email"),
                "role": "owner",
                "joined_at": now
            }],
            "shared_waypoints": [],
            "created_at": now,
            "updated_at": now
        }
        
        result = await groups_collection.insert_one(group_doc)
        group_doc["_id"] = result.inserted_id
        
        logger.info(f"Group created: {group.name} by {owner_id}")
        
        return {
            "success": True,
            "group": serialize_group(group_doc, include_members=True),
            "message": f"Groupe '{group.name}' créé avec succès"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating group: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/my-groups")
async def get_user_groups(user_id: str):
    """Récupère tous les groupes de l'utilisateur (propriétaire ou membre)"""
    try:
        cursor = groups_collection.find({
            "members.user_id": user_id
        }).sort("created_at", -1)
        
        groups = await cursor.to_list(length=50)
        
        # Séparer les groupes possédés et ceux dont l'utilisateur est membre
        owned = []
        member_of = []
        
        for g in groups:
            serialized = serialize_group(g)
            if g.get("owner_id") == user_id:
                owned.append(serialized)
            else:
                member_of.append(serialized)
        
        return {
            "owned_groups": owned,
            "member_groups": member_of,
            "total": len(groups)
        }
        
    except Exception as e:
        logger.error(f"Error getting user groups: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{group_id}/details")
async def get_group_details(group_id: str, user_id: str = Query(...)):
    """Récupère les détails d'un groupe (membres, waypoints partagés)"""
    try:
        group = await groups_collection.find_one({"_id": ObjectId(group_id)})
        
        if not group:
            raise HTTPException(status_code=404, detail="Groupe non trouvé")
        
        # Vérifier que l'utilisateur est membre
        is_member = any(m.get("user_id") == user_id for m in group.get("members", []))
        if not is_member and not group.get("is_public"):
            raise HTTPException(status_code=403, detail="Vous n'êtes pas membre de ce groupe")
        
        return serialize_group(group, include_members=True)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting group details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{group_id}")
async def update_group(group_id: str, owner_id: str, update: GroupUpdate):
    """Met à jour un groupe (propriétaire uniquement)"""
    try:
        group = await groups_collection.find_one({"_id": ObjectId(group_id)})
        
        if not group:
            raise HTTPException(status_code=404, detail="Groupe non trouvé")
        
        if group.get("owner_id") != owner_id:
            raise HTTPException(status_code=403, detail="Seul le propriétaire peut modifier le groupe")
        
        update_data = {k: v for k, v in update.model_dump().items() if v is not None}
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        await groups_collection.update_one(
            {"_id": ObjectId(group_id)},
            {"$set": update_data}
        )
        
        updated = await groups_collection.find_one({"_id": ObjectId(group_id)})
        
        return {
            "success": True,
            "group": serialize_group(updated),
            "message": "Groupe mis à jour"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating group: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{group_id}")
async def delete_group(group_id: str, owner_id: str = Query(...)):
    """Supprime un groupe (propriétaire uniquement)"""
    try:
        group = await groups_collection.find_one({"_id": ObjectId(group_id)})
        
        if not group:
            raise HTTPException(status_code=404, detail="Groupe non trouvé")
        
        if group.get("owner_id") != owner_id:
            raise HTTPException(status_code=403, detail="Seul le propriétaire peut supprimer le groupe")
        
        # Notifier les membres
        for member in group.get("members", []):
            if member.get("user_id") != owner_id:
                await create_notification(
                    user_id=member.get("user_id"),
                    notif_type="group_deleted",
                    title="Groupe supprimé",
                    message=f"Le groupe '{group.get('name')}' a été supprimé par son propriétaire",
                    data={"group_name": group.get("name")}
                )
        
        await groups_collection.delete_one({"_id": ObjectId(group_id)})
        
        return {"success": True, "message": "Groupe supprimé"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting group: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# MEMBER MANAGEMENT ENDPOINTS
# ============================================

@router.post("/{group_id}/invite")
async def invite_members(
    group_id: str, 
    owner_id: str,
    invite: GroupInvite,
    background_tasks: BackgroundTasks
):
    """Invite des membres par email"""
    try:
        group = await groups_collection.find_one({"_id": ObjectId(group_id)})
        
        if not group:
            raise HTTPException(status_code=404, detail="Groupe non trouvé")
        
        # Vérifier permissions (owner ou admin)
        member = next((m for m in group.get("members", []) if m.get("user_id") == owner_id), None)
        if not member or member.get("role") not in ["owner", "admin"]:
            raise HTTPException(status_code=403, detail="Permission refusée")
        
        # Vérifier la limite de membres
        current_count = len(group.get("members", []))
        if current_count + len(invite.emails) > group.get("max_members", 20):
            raise HTTPException(
                status_code=400, 
                detail=f"Limite de {group.get('max_members')} membres dépassée"
            )
        
        owner_info = await get_user_info(owner_id)
        now = datetime.now(timezone.utc).isoformat()
        invites_sent = []
        
        for email in invite.emails:
            email_lower = email.lower()
            
            # Vérifier si déjà membre
            is_already_member = any(
                (m.get("email") or "").lower() == email_lower 
                for m in group.get("members", [])
            )
            if is_already_member:
                continue
            
            # Créer l'invitation
            invite_doc = {
                "group_id": group_id,
                "group_name": group.get("name"),
                "invited_email": email_lower,
                "invited_by": owner_id,
                "invited_by_name": owner_info.get("name"),
                "message": invite.message,
                "status": "pending",
                "created_at": now,
                "expires_at": None  # Pas d'expiration pour l'instant
            }
            
            await group_invites_collection.insert_one(invite_doc)
            invites_sent.append(email_lower)
            
            # Ajouter à la liste marketing
            background_tasks.add_task(
                add_to_marketing_list,
                email_lower,
                "group_invite",
                owner_id,
                group.get("name")
            )
            
            # Si l'utilisateur existe, créer une notification
            user = await users_collection.find_one({"email": email_lower})
            if user:
                await create_notification(
                    user_id=user.get("id"),
                    notif_type="group_invite",
                    title="Invitation à un groupe",
                    message=f"{owner_info.get('name')} vous invite à rejoindre le groupe '{group.get('name')}'",
                    data={
                        "group_id": group_id,
                        "group_name": group.get("name"),
                        "invite_code": group.get("invite_code")
                    }
                )
        
        return {
            "success": True,
            "invites_sent": len(invites_sent),
            "emails": invites_sent,
            "message": f"{len(invites_sent)} invitation(s) envoyée(s)"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inviting members: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{group_id}/join")
async def join_group(
    group_id: str,
    user_id: str = Query(...),
    invite_code: Optional[str] = Query(None)
):
    """Rejoindre un groupe (avec code d'invitation ou si public)"""
    try:
        group = await groups_collection.find_one({"_id": ObjectId(group_id)})
        
        if not group:
            raise HTTPException(status_code=404, detail="Groupe non trouvé")
        
        # Vérifier si déjà membre
        is_member = any(m.get("user_id") == user_id for m in group.get("members", []))
        if is_member:
            raise HTTPException(status_code=400, detail="Vous êtes déjà membre de ce groupe")
        
        # Vérifier l'autorisation
        can_join = False
        if group.get("is_public"):
            can_join = True
        elif invite_code and invite_code == group.get("invite_code"):
            can_join = True
        else:
            # Vérifier s'il y a une invitation en attente
            user_info = await get_user_info(user_id)
            user_email = user_info.get("email") or ""
            invite = await group_invites_collection.find_one({
                "group_id": group_id,
                "invited_email": user_email.lower() if user_email else "",
                "status": "pending"
            })
            if invite:
                can_join = True
                # Marquer l'invitation comme acceptée
                await group_invites_collection.update_one(
                    {"_id": invite["_id"]},
                    {"$set": {"status": "accepted", "accepted_at": datetime.now(timezone.utc).isoformat()}}
                )
        
        if not can_join:
            raise HTTPException(
                status_code=403, 
                detail="Code d'invitation invalide ou groupe privé"
            )
        
        # Vérifier la limite
        if len(group.get("members", [])) >= group.get("max_members", 20):
            raise HTTPException(status_code=400, detail="Ce groupe est complet")
        
        # Ajouter le membre
        user_info = await get_user_info(user_id)
        now = datetime.now(timezone.utc).isoformat()
        
        new_member = {
            "user_id": user_id,
            "name": user_info.get("name"),
            "email": user_info.get("email"),
            "role": "member",
            "joined_at": now
        }
        
        await groups_collection.update_one(
            {"_id": ObjectId(group_id)},
            {"$push": {"members": new_member}}
        )
        
        # Notifier le propriétaire
        await create_notification(
            user_id=group.get("owner_id"),
            notif_type="member_joined",
            title="Nouveau membre",
            message=f"{user_info.get('name')} a rejoint le groupe '{group.get('name')}'",
            data={"group_id": group_id, "new_member": user_id}
        )
        
        logger.info(f"User {user_id} joined group {group_id}")
        
        return {
            "success": True,
            "group_name": group.get("name"),
            "message": f"Vous avez rejoint le groupe '{group.get('name')}'"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error joining group: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{group_id}/members/{member_id}")
async def remove_member(
    group_id: str,
    member_id: str,
    requester_id: str = Query(...)
):
    """Retire un membre du groupe (owner/admin ou le membre lui-même)"""
    try:
        group = await groups_collection.find_one({"_id": ObjectId(group_id)})
        
        if not group:
            raise HTTPException(status_code=404, detail="Groupe non trouvé")
        
        # Vérifier les permissions
        requester = next((m for m in group.get("members", []) if m.get("user_id") == requester_id), None)
        
        is_self_remove = requester_id == member_id
        is_admin = requester and requester.get("role") in ["owner", "admin"]
        
        if not is_self_remove and not is_admin:
            raise HTTPException(status_code=403, detail="Permission refusée")
        
        # Ne pas permettre au propriétaire de se retirer
        if member_id == group.get("owner_id"):
            raise HTTPException(
                status_code=400, 
                detail="Le propriétaire ne peut pas quitter le groupe. Transférez la propriété ou supprimez le groupe."
            )
        
        # Retirer le membre
        await groups_collection.update_one(
            {"_id": ObjectId(group_id)},
            {"$pull": {"members": {"user_id": member_id}}}
        )
        
        # Notifier le membre retiré
        if not is_self_remove:
            await create_notification(
                user_id=member_id,
                notif_type="removed_from_group",
                title="Retiré du groupe",
                message=f"Vous avez été retiré du groupe '{group.get('name')}'",
                data={"group_id": group_id, "group_name": group.get("name")}
            )
        
        return {"success": True, "message": "Membre retiré du groupe"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing member: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# GROUP WAYPOINT SHARING
# ============================================

@router.post("/{group_id}/share-waypoint")
async def share_waypoint_with_group(
    group_id: str,
    user_id: str = Query(...),
    waypoint_id: str = Query(...),
    waypoint_name: str = Query(...)
):
    """Partage un waypoint avec tous les membres du groupe"""
    try:
        group = await groups_collection.find_one({"_id": ObjectId(group_id)})
        
        if not group:
            raise HTTPException(status_code=404, detail="Groupe non trouvé")
        
        # Vérifier que l'utilisateur est membre
        is_member = any(m.get("user_id") == user_id for m in group.get("members", []))
        if not is_member:
            raise HTTPException(status_code=403, detail="Vous n'êtes pas membre de ce groupe")
        
        # Vérifier si déjà partagé
        already_shared = any(
            sw.get("waypoint_id") == waypoint_id 
            for sw in group.get("shared_waypoints", [])
        )
        if already_shared:
            raise HTTPException(status_code=400, detail="Ce waypoint est déjà partagé avec le groupe")
        
        user_info = await get_user_info(user_id)
        now = datetime.now(timezone.utc).isoformat()
        
        shared_waypoint = {
            "waypoint_id": waypoint_id,
            "waypoint_name": waypoint_name,
            "shared_by": user_id,
            "shared_by_name": user_info.get("name"),
            "shared_at": now,
            "permission": "collaborate"
        }
        
        await groups_collection.update_one(
            {"_id": ObjectId(group_id)},
            {"$push": {"shared_waypoints": shared_waypoint}}
        )
        
        # Notifier tous les membres (sauf celui qui partage)
        for member in group.get("members", []):
            if member.get("user_id") != user_id:
                await create_notification(
                    user_id=member.get("user_id"),
                    notif_type="group_waypoint_shared",
                    title="Nouveau waypoint partagé",
                    message=f"{user_info.get('name')} a partagé '{waypoint_name}' avec le groupe '{group.get('name')}'",
                    data={
                        "group_id": group_id,
                        "group_name": group.get("name"),
                        "waypoint_id": waypoint_id,
                        "waypoint_name": waypoint_name
                    }
                )
        
        return {
            "success": True,
            "message": f"Waypoint partagé avec {len(group.get('members', [])) - 1} membre(s)"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sharing waypoint with group: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{group_id}/shared-waypoints")
async def get_group_shared_waypoints(group_id: str, user_id: str = Query(...)):
    """Récupère tous les waypoints partagés avec le groupe"""
    try:
        group = await groups_collection.find_one({"_id": ObjectId(group_id)})
        
        if not group:
            raise HTTPException(status_code=404, detail="Groupe non trouvé")
        
        # Vérifier l'appartenance
        is_member = any(m.get("user_id") == user_id for m in group.get("members", []))
        if not is_member:
            raise HTTPException(status_code=403, detail="Vous n'êtes pas membre de ce groupe")
        
        return {
            "group_id": group_id,
            "group_name": group.get("name"),
            "shared_waypoints": group.get("shared_waypoints", []),
            "total": len(group.get("shared_waypoints", []))
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting shared waypoints: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# PUBLIC GROUPS DISCOVERY
# ============================================

@router.get("/discover/public")
async def discover_public_groups(
    search: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=50)
):
    """Découvre les groupes publics"""
    try:
        query = {"is_public": True}
        
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
        
        cursor = groups_collection.find(query).sort("created_at", -1).limit(limit)
        groups = await cursor.to_list(length=limit)
        
        return {
            "groups": [serialize_group(g) for g in groups],
            "total": len(groups)
        }
        
    except Exception as e:
        logger.error(f"Error discovering public groups: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/join-by-code/{invite_code}")
async def get_group_by_invite_code(invite_code: str):
    """Récupère les infos d'un groupe par son code d'invitation"""
    try:
        group = await groups_collection.find_one({"invite_code": invite_code.upper()})
        
        if not group:
            raise HTTPException(status_code=404, detail="Code d'invitation invalide")
        
        return {
            "id": str(group["_id"]),
            "name": group.get("name"),
            "description": group.get("description"),
            "owner_name": group.get("owner_name"),
            "member_count": len(group.get("members", [])),
            "max_members": group.get("max_members", 20),
            "is_full": len(group.get("members", [])) >= group.get("max_members", 20)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting group by code: {e}")
        raise HTTPException(status_code=500, detail=str(e))
