"""
Contacts Admin Service - V5-ULTIME Administration Premium
=========================================================

Service d'administration des contacts et entités relationnelles:
- Fournisseurs (Suppliers)
- Fabricants (Manufacturers)
- Partenaires (Partners)
- Formateurs / Experts
- Contacts internes / externes
- Réseau professionnel

Module isolé - aucun import croisé.
Source de vérité V5 pour toutes les entités relationnelles.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, List
import logging
import uuid

logger = logging.getLogger(__name__)


class ContactsAdminService:
    """Service isolé pour l'administration des contacts et entités relationnelles"""
    
    # Types d'entités supportés
    ENTITY_TYPES = [
        "supplier",      # Fournisseur
        "manufacturer",  # Fabricant
        "partner",       # Partenaire
        "trainer",       # Formateur
        "expert",        # Expert
        "internal",      # Contact interne
        "external",      # Contact externe
        "professional",  # Réseau professionnel
        "other"          # Autre
    ]
    
    # ============ CONTACTS CRUD ============
    @staticmethod
    async def get_contacts(db, entity_type: Optional[str] = None, 
                          status: Optional[str] = None,
                          search: Optional[str] = None,
                          limit: int = 50) -> dict:
        """Liste les contacts avec filtres"""
        query = {}
        
        if entity_type and entity_type != 'all':
            query["entity_type"] = entity_type
        if status and status != 'all':
            query["status"] = status
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"company": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}}
            ]
        
        contacts = await db.admin_contacts.find(
            query, {"_id": 0}
        ).sort("created_at", -1).limit(limit).to_list(length=limit)
        
        total = await db.admin_contacts.count_documents(query)
        
        # Stats par type
        type_counts = {}
        for et in ContactsAdminService.ENTITY_TYPES:
            type_counts[et] = await db.admin_contacts.count_documents({"entity_type": et})
        
        return {
            "success": True,
            "total": total,
            "type_counts": type_counts,
            "contacts": contacts
        }
    
    @staticmethod
    async def get_contact_by_id(db, contact_id: str) -> dict:
        """Récupérer un contact par ID"""
        contact = await db.admin_contacts.find_one(
            {"id": contact_id},
            {"_id": 0}
        )
        
        if not contact:
            return {"success": False, "error": "Contact not found"}
        
        return {"success": True, "contact": contact}
    
    @staticmethod
    async def create_contact(db, contact_data: dict) -> dict:
        """Créer un nouveau contact"""
        entity_type = contact_data.get("entity_type", "other")
        if entity_type not in ContactsAdminService.ENTITY_TYPES:
            entity_type = "other"
        
        contact = {
            "id": str(uuid.uuid4()),
            "entity_type": entity_type,
            "name": contact_data.get("name", ""),
            "company": contact_data.get("company", ""),
            "position": contact_data.get("position", ""),
            "email": contact_data.get("email", ""),
            "phone": contact_data.get("phone", ""),
            "address": contact_data.get("address", ""),
            "city": contact_data.get("city", ""),
            "province": contact_data.get("province", ""),
            "postal_code": contact_data.get("postal_code", ""),
            "country": contact_data.get("country", "Canada"),
            "website": contact_data.get("website", ""),
            "notes": contact_data.get("notes", ""),
            "tags": contact_data.get("tags", []),
            "status": contact_data.get("status", "active"),
            "priority": contact_data.get("priority", "normal"),
            "metadata": contact_data.get("metadata", {}),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        await db.admin_contacts.insert_one(contact)
        contact.pop("_id", None)
        
        return {"success": True, "contact": contact}
    
    @staticmethod
    async def update_contact(db, contact_id: str, updates: dict) -> dict:
        """Mettre à jour un contact"""
        # Ne pas permettre de changer l'ID
        updates.pop("id", None)
        updates["updated_at"] = datetime.now(timezone.utc)
        
        result = await db.admin_contacts.update_one(
            {"id": contact_id},
            {"$set": updates}
        )
        
        if result.matched_count == 0:
            return {"success": False, "error": "Contact not found"}
        
        return {"success": True, "contact_id": contact_id, "updated": True}
    
    @staticmethod
    async def delete_contact(db, contact_id: str) -> dict:
        """Supprimer un contact"""
        result = await db.admin_contacts.delete_one({"id": contact_id})
        
        if result.deleted_count == 0:
            return {"success": False, "error": "Contact not found"}
        
        return {"success": True, "contact_id": contact_id, "deleted": True}
    
    # ============ SUPPLIERS (Fournisseurs) ============
    @staticmethod
    async def get_suppliers(db, limit: int = 50) -> dict:
        """Liste les fournisseurs"""
        return await ContactsAdminService.get_contacts(db, entity_type="supplier", limit=limit)
    
    @staticmethod
    async def create_supplier(db, supplier_data: dict) -> dict:
        """Créer un fournisseur"""
        supplier_data["entity_type"] = "supplier"
        return await ContactsAdminService.create_contact(db, supplier_data)
    
    # ============ MANUFACTURERS (Fabricants) ============
    @staticmethod
    async def get_manufacturers(db, limit: int = 50) -> dict:
        """Liste les fabricants"""
        return await ContactsAdminService.get_contacts(db, entity_type="manufacturer", limit=limit)
    
    @staticmethod
    async def create_manufacturer(db, manufacturer_data: dict) -> dict:
        """Créer un fabricant"""
        manufacturer_data["entity_type"] = "manufacturer"
        return await ContactsAdminService.create_contact(db, manufacturer_data)
    
    # ============ PARTNERS (Partenaires) ============
    @staticmethod
    async def get_partners(db, limit: int = 50) -> dict:
        """Liste les partenaires"""
        return await ContactsAdminService.get_contacts(db, entity_type="partner", limit=limit)
    
    @staticmethod
    async def create_partner(db, partner_data: dict) -> dict:
        """Créer un partenaire"""
        partner_data["entity_type"] = "partner"
        return await ContactsAdminService.create_contact(db, partner_data)
    
    # ============ TRAINERS (Formateurs) ============
    @staticmethod
    async def get_trainers(db, limit: int = 50) -> dict:
        """Liste les formateurs"""
        return await ContactsAdminService.get_contacts(db, entity_type="trainer", limit=limit)
    
    @staticmethod
    async def create_trainer(db, trainer_data: dict) -> dict:
        """Créer un formateur"""
        trainer_data["entity_type"] = "trainer"
        return await ContactsAdminService.create_contact(db, trainer_data)
    
    # ============ EXPERTS ============
    @staticmethod
    async def get_experts(db, limit: int = 50) -> dict:
        """Liste les experts"""
        return await ContactsAdminService.get_contacts(db, entity_type="expert", limit=limit)
    
    @staticmethod
    async def create_expert(db, expert_data: dict) -> dict:
        """Créer un expert"""
        expert_data["entity_type"] = "expert"
        return await ContactsAdminService.create_contact(db, expert_data)
    
    # ============ BULK OPERATIONS ============
    @staticmethod
    async def bulk_update_status(db, contact_ids: List[str], new_status: str) -> dict:
        """Mettre à jour le statut de plusieurs contacts"""
        result = await db.admin_contacts.update_many(
            {"id": {"$in": contact_ids}},
            {"$set": {"status": new_status, "updated_at": datetime.now(timezone.utc)}}
        )
        
        return {
            "success": True,
            "modified_count": result.modified_count,
            "new_status": new_status
        }
    
    @staticmethod
    async def bulk_delete(db, contact_ids: List[str]) -> dict:
        """Supprimer plusieurs contacts"""
        result = await db.admin_contacts.delete_many({"id": {"$in": contact_ids}})
        
        return {
            "success": True,
            "deleted_count": result.deleted_count
        }
    
    # ============ TAGS ============
    @staticmethod
    async def get_all_tags(db) -> dict:
        """Récupérer tous les tags utilisés"""
        pipeline = [
            {"$unwind": "$tags"},
            {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        results = await db.admin_contacts.aggregate(pipeline).to_list(length=100)
        tags = [{"tag": r["_id"], "count": r["count"]} for r in results]
        
        return {
            "success": True,
            "total": len(tags),
            "tags": tags
        }
    
    @staticmethod
    async def add_tag_to_contact(db, contact_id: str, tag: str) -> dict:
        """Ajouter un tag à un contact"""
        result = await db.admin_contacts.update_one(
            {"id": contact_id},
            {"$addToSet": {"tags": tag}, "$set": {"updated_at": datetime.now(timezone.utc)}}
        )
        
        if result.matched_count == 0:
            return {"success": False, "error": "Contact not found"}
        
        return {"success": True, "contact_id": contact_id, "tag": tag, "added": True}
    
    @staticmethod
    async def remove_tag_from_contact(db, contact_id: str, tag: str) -> dict:
        """Retirer un tag d'un contact"""
        result = await db.admin_contacts.update_one(
            {"id": contact_id},
            {"$pull": {"tags": tag}, "$set": {"updated_at": datetime.now(timezone.utc)}}
        )
        
        if result.matched_count == 0:
            return {"success": False, "error": "Contact not found"}
        
        return {"success": True, "contact_id": contact_id, "tag": tag, "removed": True}
    
    # ============ STATISTICS ============
    @staticmethod
    async def get_contacts_stats(db) -> dict:
        """Statistiques globales des contacts"""
        total = await db.admin_contacts.count_documents({})
        active = await db.admin_contacts.count_documents({"status": "active"})
        inactive = await db.admin_contacts.count_documents({"status": "inactive"})
        
        # Par type
        type_stats = {}
        for et in ContactsAdminService.ENTITY_TYPES:
            type_stats[et] = await db.admin_contacts.count_documents({"entity_type": et})
        
        # Par priorité
        priority_stats = {
            "high": await db.admin_contacts.count_documents({"priority": "high"}),
            "normal": await db.admin_contacts.count_documents({"priority": "normal"}),
            "low": await db.admin_contacts.count_documents({"priority": "low"})
        }
        
        # Récents (7 derniers jours)
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        recent = await db.admin_contacts.count_documents({
            "created_at": {"$gte": week_ago}
        })
        
        return {
            "success": True,
            "stats": {
                "total": total,
                "active": active,
                "inactive": inactive,
                "by_type": type_stats,
                "by_priority": priority_stats,
                "recent_7days": recent
            }
        }
    
    # ============ IMPORT / EXPORT ============
    @staticmethod
    async def export_contacts(db, entity_type: Optional[str] = None) -> dict:
        """Exporter les contacts"""
        query = {}
        if entity_type and entity_type != 'all':
            query["entity_type"] = entity_type
        
        contacts = await db.admin_contacts.find(
            query, {"_id": 0}
        ).to_list(length=10000)
        
        return {
            "success": True,
            "total": len(contacts),
            "export_date": datetime.now(timezone.utc).isoformat(),
            "contacts": contacts
        }
    
    @staticmethod
    async def import_contacts(db, contacts_data: List[dict]) -> dict:
        """Importer des contacts"""
        imported = 0
        errors = []
        
        for idx, contact in enumerate(contacts_data):
            try:
                # Vérifier si existe déjà (par email)
                if contact.get("email"):
                    existing = await db.admin_contacts.find_one({"email": contact["email"]})
                    if existing:
                        errors.append(f"Contact {idx}: Email already exists")
                        continue
                
                # Créer le contact
                result = await ContactsAdminService.create_contact(db, contact)
                if result.get("success"):
                    imported += 1
                else:
                    errors.append(f"Contact {idx}: {result.get('error', 'Unknown error')}")
            except Exception as e:
                errors.append(f"Contact {idx}: {str(e)}")
        
        return {
            "success": True,
            "imported": imported,
            "errors": errors,
            "total_processed": len(contacts_data)
        }
