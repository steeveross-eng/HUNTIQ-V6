"""
BIONIC Knowledge Sources - V5-ULTIME
====================================

Gestion des sources de connaissances scientifiques et empiriques.
Registre centralisé de toutes les sources utilisées pour alimenter
le Knowledge Layer.

Module isolé - aucun import croisé.
"""

from datetime import datetime, timezone
from typing import List
import logging
import json
import os

logger = logging.getLogger(__name__)


class KnowledgeSourcesManager:
    """Gestionnaire des sources de connaissances"""
    
    # Types de sources avec poids de fiabilité par défaut
    SOURCE_TYPE_WEIGHTS = {
        "scientific_paper": 0.95,
        "government_report": 0.90,
        "expert_interview": 0.80,
        "field_observation": 0.75,
        "traditional_knowledge": 0.70,
        "user_report": 0.50,
        "sensor_data": 0.85,
        "ai_generated": 0.60
    }
    
    # Sources officielles de référence - chargées depuis JSON
    @staticmethod
    def _load_sources_from_json():
        """Charger les sources depuis le fichier JSON"""
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            sources_path = os.path.join(base_path, "data", "sources_registry.json")
            
            if os.path.exists(sources_path):
                with open(sources_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return {s["id"]: s for s in data.get("sources", [])}
            return {}
        except Exception as e:
            logger.error(f"Error loading sources JSON: {e}")
            return {}
    
    # Sources officielles de référence (Québec) - fallback
    OFFICIAL_SOURCES = {
        "mffp_quebec": {
            "id": "mffp_quebec",
            "name": "Ministère des Forêts, de la Faune et des Parcs du Québec",
            "source_type": "government_report",
            "reference": "https://mffp.gouv.qc.ca",
            "reliability_score": 0.95,
            "peer_reviewed": True,
            "topics": ["hunting_regulations", "wildlife_management", "habitat_conservation"]
        },
        "cic_quebec": {
            "id": "cic_quebec",
            "name": "Canards Illimités Canada - Québec",
            "source_type": "scientific_paper",
            "reference": "https://www.canards.ca",
            "reliability_score": 0.90,
            "peer_reviewed": True,
            "topics": ["wetland_conservation", "waterfowl", "habitat_restoration"]
        },
        "sepaq": {
            "id": "sepaq",
            "name": "Société des établissements de plein air du Québec",
            "source_type": "government_report",
            "reference": "https://www.sepaq.com",
            "reliability_score": 0.90,
            "topics": ["wildlife_reserves", "hunting_territories", "species_data"]
        },
        "fqf": {
            "id": "fqf",
            "name": "Fédération québécoise des chasseurs et pêcheurs",
            "source_type": "expert_interview",
            "reference": "https://www.fedecp.com",
            "reliability_score": 0.80,
            "topics": ["hunting_practices", "wildlife_behavior", "traditional_knowledge"]
        }
    }
    
    # ============ CRUD OPERATIONS ============
    
    @staticmethod
    async def get_all_sources(db, source_type: str = None, verified: bool = None, limit: int = 100) -> dict:
        """Récupérer toutes les sources"""
        try:
            query = {}
            if source_type:
                query["source_type"] = source_type
            if verified is not None:
                query["verified"] = verified
            
            sources = await db.knowledge_sources.find(
                query, {"_id": 0}
            ).limit(limit).to_list(limit)
            
            # Charger sources depuis JSON (prioritaire) ou fallback sur OFFICIAL_SOURCES
            json_sources = KnowledgeSourcesManager._load_sources_from_json()
            official_sources = list(json_sources.values()) if json_sources else list(KnowledgeSourcesManager.OFFICIAL_SOURCES.values())
            
            all_sources = official_sources + sources
            
            return {
                "success": True,
                "total": len(all_sources),
                "sources": all_sources
            }
        except Exception as e:
            logger.error(f"Error getting sources: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def get_source_by_id(db, source_id: str) -> dict:
        """Récupérer une source par ID"""
        try:
            # Vérifier sources officielles d'abord
            if source_id in KnowledgeSourcesManager.OFFICIAL_SOURCES:
                return {
                    "success": True,
                    "source": KnowledgeSourcesManager.OFFICIAL_SOURCES[source_id],
                    "is_official": True
                }
            
            source = await db.knowledge_sources.find_one({"id": source_id}, {"_id": 0})
            if source:
                return {"success": True, "source": source, "is_official": False}
            
            return {"success": False, "error": "Source non trouvée"}
        except Exception as e:
            logger.error(f"Error getting source: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def add_source(db, source_data: dict) -> dict:
        """Ajouter une nouvelle source"""
        try:
            import uuid
            
            source = {
                "id": source_data.get("id", str(uuid.uuid4())),
                "name": source_data.get("name"),
                "source_type": source_data.get("source_type", "field_observation"),
                "reference": source_data.get("reference", ""),
                "authors": source_data.get("authors", []),
                "publication_date": source_data.get("publication_date"),
                "species_covered": source_data.get("species_covered", []),
                "regions_covered": source_data.get("regions_covered", []),
                "topics": source_data.get("topics", []),
                "reliability_score": KnowledgeSourcesManager.SOURCE_TYPE_WEIGHTS.get(
                    source_data.get("source_type", "field_observation"), 0.5
                ),
                "peer_reviewed": source_data.get("peer_reviewed", False),
                "citation_count": source_data.get("citation_count", 0),
                "added_at": datetime.now(timezone.utc).isoformat(),
                "verified": False,
                "notes": source_data.get("notes")
            }
            
            await db.knowledge_sources.insert_one(source)
            source.pop("_id", None)
            
            return {"success": True, "source": source}
        except Exception as e:
            logger.error(f"Error adding source: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def update_source(db, source_id: str, updates: dict) -> dict:
        """Mettre à jour une source"""
        try:
            # Ne pas modifier les sources officielles
            if source_id in KnowledgeSourcesManager.OFFICIAL_SOURCES:
                return {"success": False, "error": "Impossible de modifier une source officielle"}
            
            protected = ["id", "added_at"]
            for field in protected:
                updates.pop(field, None)
            
            updates["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            result = await db.knowledge_sources.update_one(
                {"id": source_id},
                {"$set": updates}
            )
            
            if result.matched_count == 0:
                return {"success": False, "error": "Source non trouvée"}
            
            return {"success": True, "message": "Source mise à jour"}
        except Exception as e:
            logger.error(f"Error updating source: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def verify_source(db, source_id: str, verified: bool = True) -> dict:
        """Vérifier/dévérifier une source"""
        try:
            if source_id in KnowledgeSourcesManager.OFFICIAL_SOURCES:
                return {"success": True, "message": "Source officielle toujours vérifiée"}
            
            result = await db.knowledge_sources.update_one(
                {"id": source_id},
                {"$set": {
                    "verified": verified,
                    "verified_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            
            if result.matched_count == 0:
                return {"success": False, "error": "Source non trouvée"}
            
            return {"success": True, "verified": verified}
        except Exception as e:
            logger.error(f"Error verifying source: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def delete_source(db, source_id: str) -> dict:
        """Supprimer une source"""
        try:
            if source_id in KnowledgeSourcesManager.OFFICIAL_SOURCES:
                return {"success": False, "error": "Impossible de supprimer une source officielle"}
            
            result = await db.knowledge_sources.delete_one({"id": source_id})
            
            if result.deleted_count == 0:
                return {"success": False, "error": "Source non trouvée"}
            
            return {"success": True, "message": "Source supprimée"}
        except Exception as e:
            logger.error(f"Error deleting source: {e}")
            return {"success": False, "error": str(e)}
    
    # ============ STATISTICS ============
    
    @staticmethod
    async def get_sources_stats(db) -> dict:
        """Statistiques des sources"""
        try:
            total_custom = await db.knowledge_sources.count_documents({})
            verified_count = await db.knowledge_sources.count_documents({"verified": True})
            
            # Par type
            by_type = {}
            for stype in KnowledgeSourcesManager.SOURCE_TYPE_WEIGHTS.keys():
                count = await db.knowledge_sources.count_documents({"source_type": stype})
                by_type[stype] = count
            
            return {
                "success": True,
                "stats": {
                    "total_official": len(KnowledgeSourcesManager.OFFICIAL_SOURCES),
                    "total_custom": total_custom,
                    "total": len(KnowledgeSourcesManager.OFFICIAL_SOURCES) + total_custom,
                    "verified": verified_count + len(KnowledgeSourcesManager.OFFICIAL_SOURCES),
                    "by_type": by_type
                }
            }
        except Exception as e:
            logger.error(f"Error getting sources stats: {e}")
            return {"success": False, "error": str(e)}
    
    # ============ RELIABILITY SCORING ============
    
    @staticmethod
    def calculate_composite_reliability(sources: List[dict]) -> float:
        """Calculer un score de fiabilité composite à partir de plusieurs sources"""
        if not sources:
            return 0.0
        
        total_weight = 0
        weighted_score = 0
        
        for source in sources:
            score = source.get("reliability_score", 0.5)
            # Bonus pour peer-reviewed
            if source.get("peer_reviewed"):
                score *= 1.1
            # Bonus pour citations
            citations = source.get("citation_count", 0)
            if citations > 10:
                score *= 1.05
            
            weighted_score += min(score, 1.0)
            total_weight += 1
        
        return round(weighted_score / total_weight, 3)


logger.info("KnowledgeSourcesManager initialized - V5 LEGO Module")
