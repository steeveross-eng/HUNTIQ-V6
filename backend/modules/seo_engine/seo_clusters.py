"""
BIONIC SEO Clusters - V5-ULTIME
================================

Gestion des clusters SEO thématiques.
Architecture de contenu basée sur:
- Clusters principaux (espèces, régions, saisons)
- Sous-clusters (techniques, équipements)
- Maillage hiérarchique
- Intégration Knowledge Layer

Module isolé - aucun import croisé.
"""

from datetime import datetime, timezone
import logging
import uuid

logger = logging.getLogger(__name__)


class SEOClustersManager:
    """Gestionnaire des clusters SEO"""
    
    # ============================================
    # CLUSTERS DE BASE (BIONIC HUNTING)
    # ============================================
    
    BASE_CLUSTERS = {
        # ===== CLUSTERS ESPÈCES =====
        "cluster_moose": {
            "id": "cluster_moose",
            "name": "Moose Hunting",
            "name_fr": "Chasse à l'Orignal",
            "cluster_type": "species",
            "description": "Complete guide to moose hunting in Quebec",
            "description_fr": "Guide complet de la chasse à l'orignal au Québec",
            "primary_keyword": {
                "keyword": "moose hunting quebec",
                "keyword_fr": "chasse orignal québec",
                "search_volume": 12100,
                "difficulty": 0.65,
                "intent": "informational",
                "priority": 1,
                "is_primary": True
            },
            "secondary_keywords": [
                {"keyword": "moose hunting tips", "keyword_fr": "conseils chasse orignal", "search_volume": 4400},
                {"keyword": "moose hunting season", "keyword_fr": "saison chasse orignal", "search_volume": 8100},
                {"keyword": "moose calling techniques", "keyword_fr": "techniques appel orignal", "search_volume": 2900},
                {"keyword": "moose hunting zones quebec", "keyword_fr": "zones chasse orignal québec", "search_volume": 1900}
            ],
            "long_tail_keywords": [
                "best time to hunt moose quebec",
                "how to call a bull moose during rut",
                "moose hunting gear checklist",
                "where to hunt moose in quebec",
                "moose behavior during hunting season"
            ],
            "species_ids": ["moose"],
            "region_ids": ["quebec_north", "quebec_south", "laurentides", "abitibi"],
            "season_tags": ["fall", "rut", "pre_rut"],
            "is_active": True
        },
        "cluster_deer": {
            "id": "cluster_deer",
            "name": "Deer Hunting",
            "name_fr": "Chasse au Cerf de Virginie",
            "cluster_type": "species",
            "description": "Complete guide to whitetail deer hunting",
            "description_fr": "Guide complet de la chasse au cerf de Virginie",
            "primary_keyword": {
                "keyword": "deer hunting quebec",
                "keyword_fr": "chasse chevreuil québec",
                "search_volume": 9900,
                "difficulty": 0.60,
                "intent": "informational",
                "priority": 1,
                "is_primary": True
            },
            "secondary_keywords": [
                {"keyword": "whitetail hunting tips", "keyword_fr": "conseils chasse chevreuil", "search_volume": 5400},
                {"keyword": "deer rut hunting", "keyword_fr": "chasse rut chevreuil", "search_volume": 3200},
                {"keyword": "deer stand placement", "keyword_fr": "placement mirador chevreuil", "search_volume": 2100}
            ],
            "long_tail_keywords": [
                "best deer hunting zones montreal",
                "deer hunting moon phase calendar",
                "how to pattern whitetail bucks",
                "deer hunting food plots quebec"
            ],
            "species_ids": ["deer"],
            "region_ids": ["monteregie", "estrie", "outaouais", "lanaudiere"],
            "season_tags": ["fall", "rut", "pre_rut", "post_rut"],
            "is_active": True
        },
        "cluster_bear": {
            "id": "cluster_bear",
            "name": "Bear Hunting",
            "name_fr": "Chasse à l'Ours Noir",
            "cluster_type": "species",
            "description": "Complete guide to black bear hunting",
            "description_fr": "Guide complet de la chasse à l'ours noir",
            "primary_keyword": {
                "keyword": "bear hunting quebec",
                "keyword_fr": "chasse ours noir québec",
                "search_volume": 6600,
                "difficulty": 0.55,
                "intent": "informational",
                "priority": 1,
                "is_primary": True
            },
            "secondary_keywords": [
                {"keyword": "black bear baiting", "keyword_fr": "appâtage ours noir", "search_volume": 2400},
                {"keyword": "bear hunting spring", "keyword_fr": "chasse ours printemps", "search_volume": 1800},
                {"keyword": "bear hunting fall", "keyword_fr": "chasse ours automne", "search_volume": 1500}
            ],
            "long_tail_keywords": [
                "best bear baits quebec",
                "bear hunting regulations quebec 2024",
                "how to set up bear bait station"
            ],
            "species_ids": ["bear"],
            "region_ids": ["quebec_all"],
            "season_tags": ["spring", "fall", "hyperphagia"],
            "is_active": True
        },
        
        # ===== CLUSTERS RÉGIONS =====
        "cluster_laurentides": {
            "id": "cluster_laurentides",
            "name": "Laurentides Hunting",
            "name_fr": "Chasse dans les Laurentides",
            "cluster_type": "region",
            "description": "Hunting opportunities in Laurentides region",
            "description_fr": "Opportunités de chasse dans les Laurentides",
            "primary_keyword": {
                "keyword": "hunting laurentides",
                "keyword_fr": "chasse laurentides",
                "search_volume": 3300,
                "difficulty": 0.45,
                "intent": "informational",
                "priority": 2,
                "is_primary": True
            },
            "secondary_keywords": [
                {"keyword": "zec laurentides", "keyword_fr": "zec laurentides chasse", "search_volume": 1200},
                {"keyword": "pourvoirie laurentides", "keyword_fr": "pourvoirie laurentides", "search_volume": 2100}
            ],
            "region_ids": ["laurentides"],
            "species_ids": ["moose", "deer", "bear"],
            "is_active": True
        },
        "cluster_abitibi": {
            "id": "cluster_abitibi",
            "name": "Abitibi Hunting",
            "name_fr": "Chasse en Abitibi",
            "cluster_type": "region",
            "description": "Premier hunting destination in Quebec",
            "description_fr": "Destination chasse de premier choix au Québec",
            "primary_keyword": {
                "keyword": "hunting abitibi",
                "keyword_fr": "chasse abitibi",
                "search_volume": 2700,
                "difficulty": 0.40,
                "intent": "informational",
                "priority": 2,
                "is_primary": True
            },
            "secondary_keywords": [
                {"keyword": "moose hunting abitibi", "keyword_fr": "chasse orignal abitibi", "search_volume": 1800},
                {"keyword": "bear hunting abitibi", "keyword_fr": "chasse ours abitibi", "search_volume": 900}
            ],
            "region_ids": ["abitibi"],
            "species_ids": ["moose", "bear"],
            "is_active": True
        },
        
        # ===== CLUSTERS SAISONS =====
        "cluster_rut_season": {
            "id": "cluster_rut_season",
            "name": "Rut Season Hunting",
            "name_fr": "Chasse pendant le Rut",
            "cluster_type": "season",
            "description": "Hunting strategies during the rut",
            "description_fr": "Stratégies de chasse pendant le rut",
            "primary_keyword": {
                "keyword": "rut hunting tips",
                "keyword_fr": "chasse pendant le rut",
                "search_volume": 8100,
                "difficulty": 0.55,
                "intent": "informational",
                "priority": 1,
                "is_primary": True
            },
            "secondary_keywords": [
                {"keyword": "moose rut dates quebec", "keyword_fr": "dates rut orignal québec", "search_volume": 2900},
                {"keyword": "deer rut peak", "keyword_fr": "pic rut chevreuil", "search_volume": 3600},
                {"keyword": "calling during rut", "keyword_fr": "appel pendant rut", "search_volume": 1500}
            ],
            "season_tags": ["rut", "pre_rut", "post_rut"],
            "species_ids": ["moose", "deer"],
            "is_active": True
        },
        
        # ===== CLUSTERS TECHNIQUES =====
        "cluster_calling": {
            "id": "cluster_calling",
            "name": "Calling Techniques",
            "name_fr": "Techniques d'Appel",
            "cluster_type": "technique",
            "description": "Game calling strategies and techniques",
            "description_fr": "Stratégies et techniques d'appel du gibier",
            "primary_keyword": {
                "keyword": "hunting calling techniques",
                "keyword_fr": "techniques appel chasse",
                "search_volume": 4400,
                "difficulty": 0.50,
                "intent": "informational",
                "priority": 2,
                "is_primary": True
            },
            "secondary_keywords": [
                {"keyword": "moose calling", "keyword_fr": "appel orignal", "search_volume": 3600},
                {"keyword": "cow moose call", "keyword_fr": "appel femelle orignal", "search_volume": 1200},
                {"keyword": "grunt tube deer", "keyword_fr": "tube grognement chevreuil", "search_volume": 800}
            ],
            "species_ids": ["moose", "deer"],
            "is_active": True
        },
        "cluster_scouting": {
            "id": "cluster_scouting",
            "name": "Scouting & Tracking",
            "name_fr": "Repérage et Pistage",
            "cluster_type": "technique",
            "description": "Pre-season scouting and animal tracking",
            "description_fr": "Repérage pré-saison et pistage du gibier",
            "primary_keyword": {
                "keyword": "hunting scouting tips",
                "keyword_fr": "conseils repérage chasse",
                "search_volume": 2900,
                "difficulty": 0.45,
                "intent": "informational",
                "priority": 2,
                "is_primary": True
            },
            "secondary_keywords": [
                {"keyword": "trail camera placement", "keyword_fr": "placement caméra chasse", "search_volume": 3200},
                {"keyword": "reading animal signs", "keyword_fr": "lire signes animaux", "search_volume": 1100}
            ],
            "species_ids": ["moose", "deer", "bear"],
            "is_active": True
        },
        
        # ===== CLUSTERS ÉQUIPEMENT =====
        "cluster_equipment": {
            "id": "cluster_equipment",
            "name": "Hunting Equipment",
            "name_fr": "Équipement de Chasse",
            "cluster_type": "equipment",
            "description": "Essential hunting gear and equipment",
            "description_fr": "Équipement et matériel de chasse essentiels",
            "primary_keyword": {
                "keyword": "hunting gear checklist",
                "keyword_fr": "liste équipement chasse",
                "search_volume": 5400,
                "difficulty": 0.60,
                "intent": "transactional",
                "priority": 2,
                "is_primary": True
            },
            "secondary_keywords": [
                {"keyword": "best hunting rifle", "keyword_fr": "meilleure carabine chasse", "search_volume": 6600},
                {"keyword": "hunting optics", "keyword_fr": "optiques chasse", "search_volume": 2100},
                {"keyword": "hunting clothing layers", "keyword_fr": "vêtements chasse couches", "search_volume": 1800}
            ],
            "is_active": True
        }
    }
    
    # ============================================
    # CRUD OPERATIONS
    # ============================================
    
    @staticmethod
    async def get_all_clusters(db, cluster_type: str = None, is_active: bool = True, limit: int = 100) -> dict:
        """Récupérer tous les clusters"""
        try:
            # Clusters de base
            clusters = list(SEOClustersManager.BASE_CLUSTERS.values())
            
            # Ajouter clusters custom
            query = {"is_active": is_active} if is_active else {}
            if cluster_type:
                query["cluster_type"] = cluster_type
            
            custom = await db.seo_clusters.find(query, {"_id": 0}).limit(limit).to_list(limit)
            clusters.extend(custom)
            
            # Filtrer par type si nécessaire
            if cluster_type:
                clusters = [c for c in clusters if c.get("cluster_type") == cluster_type]
            
            return {
                "success": True,
                "total": len(clusters),
                "clusters": clusters
            }
        except Exception as e:
            logger.error(f"Error getting clusters: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def get_cluster_by_id(db, cluster_id: str) -> dict:
        """Récupérer un cluster par ID"""
        try:
            if cluster_id in SEOClustersManager.BASE_CLUSTERS:
                return {
                    "success": True,
                    "cluster": SEOClustersManager.BASE_CLUSTERS[cluster_id],
                    "is_base": True
                }
            
            cluster = await db.seo_clusters.find_one({"id": cluster_id}, {"_id": 0})
            if cluster:
                return {"success": True, "cluster": cluster, "is_base": False}
            
            return {"success": False, "error": "Cluster non trouvé"}
        except Exception as e:
            logger.error(f"Error getting cluster: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def create_cluster(db, cluster_data: dict) -> dict:
        """Créer un nouveau cluster"""
        try:
            cluster = {
                "id": cluster_data.get("id", f"cluster_{uuid.uuid4().hex[:8]}"),
                "name": cluster_data.get("name"),
                "name_fr": cluster_data.get("name_fr"),
                "cluster_type": cluster_data.get("cluster_type", "species"),
                "description": cluster_data.get("description", ""),
                "description_fr": cluster_data.get("description_fr", ""),
                "primary_keyword": cluster_data.get("primary_keyword", {}),
                "secondary_keywords": cluster_data.get("secondary_keywords", []),
                "long_tail_keywords": cluster_data.get("long_tail_keywords", []),
                "pillar_page_id": cluster_data.get("pillar_page_id"),
                "satellite_page_ids": cluster_data.get("satellite_page_ids", []),
                "opportunity_page_ids": cluster_data.get("opportunity_page_ids", []),
                "parent_cluster_id": cluster_data.get("parent_cluster_id"),
                "sub_cluster_ids": cluster_data.get("sub_cluster_ids", []),
                "species_ids": cluster_data.get("species_ids", []),
                "region_ids": cluster_data.get("region_ids", []),
                "season_tags": cluster_data.get("season_tags", []),
                "total_pages": 0,
                "total_traffic": 0,
                "avg_position": 0.0,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "is_active": True
            }
            
            await db.seo_clusters.insert_one(cluster)
            cluster.pop("_id", None)
            
            return {"success": True, "cluster": cluster}
        except Exception as e:
            logger.error(f"Error creating cluster: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def update_cluster(db, cluster_id: str, updates: dict) -> dict:
        """Mettre à jour un cluster"""
        try:
            if cluster_id in SEOClustersManager.BASE_CLUSTERS:
                return {"success": False, "error": "Impossible de modifier un cluster de base"}
            
            protected = ["id", "created_at"]
            for field in protected:
                updates.pop(field, None)
            
            updates["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            result = await db.seo_clusters.update_one(
                {"id": cluster_id},
                {"$set": updates}
            )
            
            if result.matched_count == 0:
                return {"success": False, "error": "Cluster non trouvé"}
            
            return {"success": True, "message": "Cluster mis à jour"}
        except Exception as e:
            logger.error(f"Error updating cluster: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def delete_cluster(db, cluster_id: str) -> dict:
        """Supprimer un cluster"""
        try:
            if cluster_id in SEOClustersManager.BASE_CLUSTERS:
                return {"success": False, "error": "Impossible de supprimer un cluster de base"}
            
            result = await db.seo_clusters.delete_one({"id": cluster_id})
            
            if result.deleted_count == 0:
                return {"success": False, "error": "Cluster non trouvé"}
            
            return {"success": True, "message": "Cluster supprimé"}
        except Exception as e:
            logger.error(f"Error deleting cluster: {e}")
            return {"success": False, "error": str(e)}
    
    # ============================================
    # HIERARCHY & MAILLAGE
    # ============================================
    
    @staticmethod
    async def get_cluster_hierarchy(db) -> dict:
        """Récupérer la hiérarchie complète des clusters"""
        try:
            all_clusters = await SEOClustersManager.get_all_clusters(db)
            
            if not all_clusters.get("success"):
                return all_clusters
            
            clusters = all_clusters["clusters"]
            
            # Organiser par type
            hierarchy = {
                "species": [],
                "region": [],
                "season": [],
                "technique": [],
                "equipment": [],
                "territory": [],
                "behavior": [],
                "weather": []
            }
            
            for cluster in clusters:
                ctype = cluster.get("cluster_type", "species")
                if ctype in hierarchy:
                    hierarchy[ctype].append({
                        "id": cluster["id"],
                        "name_fr": cluster.get("name_fr", cluster.get("name")),
                        "sub_clusters": cluster.get("sub_cluster_ids", []),
                        "pages_count": len(cluster.get("satellite_page_ids", [])) + 1
                    })
            
            return {
                "success": True,
                "hierarchy": hierarchy,
                "total_clusters": len(clusters)
            }
        except Exception as e:
            logger.error(f"Error getting hierarchy: {e}")
            return {"success": False, "error": str(e)}
    
    # ============================================
    # STATISTICS
    # ============================================
    
    @staticmethod
    async def get_clusters_stats(db) -> dict:
        """Statistiques des clusters"""
        try:
            custom_count = await db.seo_clusters.count_documents({})
            active_count = await db.seo_clusters.count_documents({"is_active": True})
            
            # Par type
            by_type = {}
            for ctype in ["species", "region", "season", "technique", "equipment"]:
                base_count = len([c for c in SEOClustersManager.BASE_CLUSTERS.values() 
                                 if c.get("cluster_type") == ctype])
                custom_type = await db.seo_clusters.count_documents({"cluster_type": ctype})
                by_type[ctype] = base_count + custom_type
            
            return {
                "success": True,
                "stats": {
                    "total_base": len(SEOClustersManager.BASE_CLUSTERS),
                    "total_custom": custom_count,
                    "total": len(SEOClustersManager.BASE_CLUSTERS) + custom_count,
                    "active": len(SEOClustersManager.BASE_CLUSTERS) + active_count,
                    "by_type": by_type
                }
            }
        except Exception as e:
            logger.error(f"Error getting cluster stats: {e}")
            return {"success": False, "error": str(e)}


logger.info("SEOClustersManager initialized - V5 LEGO Module")
