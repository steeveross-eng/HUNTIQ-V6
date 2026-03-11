"""
BIONIC SEO Automation - V5-ULTIME
=================================

Automatisation SEO:
- Génération automatique de pages
- Planification de contenu
- Optimisation continue
- Alertes et notifications
- Scoring automatique

Module isolé - aucun import croisé.
"""

from datetime import datetime, timezone, timedelta
import logging
import uuid

logger = logging.getLogger(__name__)


class SEOAutomationManager:
    """Gestionnaire de l'automatisation SEO"""
    
    # Règles d'automatisation par défaut
    DEFAULT_AUTOMATION_RULES = {
        "auto_internal_linking": {
            "id": "auto_internal_linking",
            "name": "Auto Internal Linking",
            "name_fr": "Maillage interne automatique",
            "description": "Suggère automatiquement des liens internes lors de la création de contenu",
            "trigger": "page_created",
            "action": "suggest_links",
            "config": {
                "max_suggestions": 5,
                "min_relevance_score": 0.6
            },
            "is_active": True
        },
        "seo_score_alert": {
            "id": "seo_score_alert",
            "name": "SEO Score Alert",
            "name_fr": "Alerte score SEO",
            "description": "Alerte quand une page a un score SEO inférieur au seuil",
            "trigger": "page_updated",
            "action": "alert",
            "config": {
                "threshold": 60,
                "alert_type": "warning"
            },
            "is_active": True
        },
        "publish_reminder": {
            "id": "publish_reminder",
            "name": "Publish Reminder",
            "name_fr": "Rappel de publication",
            "description": "Rappel pour les pages en brouillon depuis trop longtemps",
            "trigger": "scheduled",
            "action": "notify",
            "config": {
                "days_threshold": 7,
                "check_frequency": "daily"
            },
            "is_active": True
        },
        "seasonal_content": {
            "id": "seasonal_content",
            "name": "Seasonal Content Generator",
            "name_fr": "Générateur contenu saisonnier",
            "description": "Suggère du contenu basé sur les saisons de chasse",
            "trigger": "scheduled",
            "action": "suggest_content",
            "config": {
                "lead_time_weeks": 4,
                "content_types": ["article", "guide"]
            },
            "is_active": True
        },
        "keyword_tracking": {
            "id": "keyword_tracking",
            "name": "Keyword Position Tracking",
            "name_fr": "Suivi positions mots-clés",
            "description": "Suit les positions des mots-clés principaux",
            "trigger": "scheduled",
            "action": "track",
            "config": {
                "frequency": "weekly",
                "alert_on_drop": 5
            },
            "is_active": True
        }
    }
    
    # ============================================
    # AUTOMATION RULES
    # ============================================
    
    @staticmethod
    async def get_all_rules(db) -> dict:
        """Récupérer toutes les règles d'automatisation"""
        try:
            rules = list(SEOAutomationManager.DEFAULT_AUTOMATION_RULES.values())
            
            custom_rules = await db.seo_automation_rules.find({}, {"_id": 0}).to_list(50)
            rules.extend(custom_rules)
            
            return {
                "success": True,
                "total": len(rules),
                "rules": rules
            }
        except Exception as e:
            logger.error(f"Error getting automation rules: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def toggle_rule(db, rule_id: str, is_active: bool) -> dict:
        """Activer/désactiver une règle"""
        try:
            if rule_id in SEOAutomationManager.DEFAULT_AUTOMATION_RULES:
                return {"success": False, "error": "Impossible de modifier une règle par défaut"}
            
            result = await db.seo_automation_rules.update_one(
                {"id": rule_id},
                {"$set": {"is_active": is_active}}
            )
            
            return {"success": True, "is_active": is_active}
        except Exception as e:
            logger.error(f"Error toggling rule: {e}")
            return {"success": False, "error": str(e)}
    
    # ============================================
    # CONTENT SUGGESTIONS
    # ============================================
    
    @staticmethod
    async def get_content_suggestions(db, knowledge_data: dict = None) -> dict:
        """Générer des suggestions de contenu basées sur le Knowledge Layer"""
        try:
            suggestions = []
            current_month = datetime.now().month
            
            # Suggestions saisonnières
            seasonal_suggestions = {
                9: [  # Septembre - Pré-rut orignal
                    {
                        "type": "seasonal",
                        "title_fr": "Guide complet du pré-rut de l'orignal",
                        "cluster_id": "cluster_moose",
                        "priority": "high",
                        "reason": "Saison de chasse à l'orignal imminente",
                        "keywords": ["pré-rut orignal", "chasse orignal septembre", "appel orignal pré-rut"]
                    },
                    {
                        "type": "seasonal",
                        "title_fr": "Techniques d'appel de la femelle orignal",
                        "cluster_id": "cluster_calling",
                        "priority": "high",
                        "reason": "Période optimale pour l'appel",
                        "keywords": ["appel femelle orignal", "cow call moose", "vache orignal"]
                    }
                ],
                10: [  # Octobre - Pic du rut
                    {
                        "type": "seasonal",
                        "title_fr": "Stratégies pour le pic du rut de l'orignal",
                        "cluster_id": "cluster_rut_season",
                        "priority": "high",
                        "reason": "Pic du rut en cours",
                        "keywords": ["pic rut orignal", "chasse rut octobre", "meilleur moment rut"]
                    }
                ],
                11: [  # Novembre - Rut cerf
                    {
                        "type": "seasonal",
                        "title_fr": "Chasse au cerf pendant le rut - Guide complet",
                        "cluster_id": "cluster_deer",
                        "priority": "high",
                        "reason": "Pic du rut du cerf de Virginie",
                        "keywords": ["rut chevreuil novembre", "chasse cerf rut", "buck rut"]
                    }
                ]
            }
            
            # Ajouter suggestions saisonnières
            if current_month in seasonal_suggestions:
                suggestions.extend(seasonal_suggestions[current_month])
            
            # Suggestions basées sur les gaps de contenu
            existing_clusters = await db.seo_pages.distinct("cluster_id")
            
            # Clusters sans page pilier
            all_clusters = list(SEOAutomationManager.DEFAULT_AUTOMATION_RULES.keys())  # Placeholder
            for cluster_id in ["cluster_moose", "cluster_deer", "cluster_bear", "cluster_calling"]:
                cluster_pages = await db.seo_pages.count_documents({
                    "cluster_id": cluster_id,
                    "page_type": "pillar"
                })
                if cluster_pages == 0:
                    suggestions.append({
                        "type": "gap",
                        "title_fr": f"Page pilier manquante pour le cluster",
                        "cluster_id": cluster_id,
                        "priority": "medium",
                        "reason": "Aucune page pilier pour ce cluster",
                        "page_type": "pillar"
                    })
            
            # Suggestions basées sur le Knowledge Layer
            if knowledge_data:
                species = knowledge_data.get("species", [])
                for sp in species:
                    # Vérifier si contenu existe pour cette espèce
                    content_count = await db.seo_pages.count_documents({
                        "target_species": sp.get("id")
                    })
                    if content_count < 5:
                        suggestions.append({
                            "type": "knowledge_gap",
                            "title_fr": f"Contenu supplémentaire pour {sp.get('common_name_fr', '')}",
                            "species_id": sp.get("id"),
                            "priority": "medium",
                            "reason": f"Seulement {content_count} pages pour cette espèce",
                            "suggested_topics": [
                                f"Comportement {sp.get('common_name_fr', '')} - Guide détaillé",
                                f"Meilleurs territoires pour chasser {sp.get('common_name_fr', '')}",
                                f"Équipement recommandé pour {sp.get('common_name_fr', '')}"
                            ]
                        })
            
            return {
                "success": True,
                "total": len(suggestions),
                "suggestions": suggestions
            }
        except Exception as e:
            logger.error(f"Error getting content suggestions: {e}")
            return {"success": False, "error": str(e)}
    
    # ============================================
    # SCHEDULED TASKS
    # ============================================
    
    @staticmethod
    async def get_scheduled_tasks(db, status: str = None) -> dict:
        """Récupérer les tâches planifiées"""
        try:
            query = {}
            if status:
                query["status"] = status
            
            tasks = await db.seo_scheduled_tasks.find(query, {"_id": 0}).to_list(100)
            
            return {
                "success": True,
                "total": len(tasks),
                "tasks": tasks
            }
        except Exception as e:
            logger.error(f"Error getting scheduled tasks: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def schedule_task(db, task_data: dict) -> dict:
        """Planifier une nouvelle tâche"""
        try:
            task = {
                "id": f"task_{uuid.uuid4().hex[:8]}",
                "type": task_data.get("type", "content_creation"),
                "title": task_data.get("title", ""),
                "description": task_data.get("description", ""),
                "scheduled_at": task_data.get("scheduled_at"),
                "target_page_id": task_data.get("target_page_id"),
                "target_cluster_id": task_data.get("target_cluster_id"),
                "priority": task_data.get("priority", "medium"),
                "status": "pending",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            await db.seo_scheduled_tasks.insert_one(task)
            task.pop("_id", None)
            
            return {"success": True, "task": task}
        except Exception as e:
            logger.error(f"Error scheduling task: {e}")
            return {"success": False, "error": str(e)}
    
    # ============================================
    # ALERTS
    # ============================================
    
    @staticmethod
    async def get_alerts(db, is_read: bool = None, limit: int = 50) -> dict:
        """Récupérer les alertes SEO"""
        try:
            query = {}
            if is_read is not None:
                query["is_read"] = is_read
            
            alerts = await db.seo_alerts.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
            
            return {
                "success": True,
                "total": len(alerts),
                "alerts": alerts
            }
        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def create_alert(db, alert_type: str, message: str, page_id: str = None, priority: str = "medium") -> dict:
        """Créer une nouvelle alerte"""
        try:
            alert = {
                "id": f"alert_{uuid.uuid4().hex[:8]}",
                "type": alert_type,
                "message": message,
                "page_id": page_id,
                "priority": priority,
                "is_read": False,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            await db.seo_alerts.insert_one(alert)
            alert.pop("_id", None)
            
            return {"success": True, "alert": alert}
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def mark_alert_read(db, alert_id: str) -> dict:
        """Marquer une alerte comme lue"""
        try:
            result = await db.seo_alerts.update_one(
                {"id": alert_id},
                {"$set": {"is_read": True}}
            )
            
            return {"success": True, "message": "Alerte marquée comme lue"}
        except Exception as e:
            logger.error(f"Error marking alert: {e}")
            return {"success": False, "error": str(e)}
    
    # ============================================
    # CONTENT CALENDAR
    # ============================================
    
    @staticmethod
    async def get_content_calendar(db, start_date: datetime = None, end_date: datetime = None) -> dict:
        """Récupérer le calendrier de contenu"""
        try:
            if not start_date:
                start_date = datetime.now(timezone.utc)
            if not end_date:
                end_date = start_date + timedelta(days=30)
            
            # Pages planifiées
            scheduled_pages = await db.seo_pages.find(
                {
                    "status": "scheduled",
                    "scheduled_at": {"$gte": start_date.isoformat(), "$lte": end_date.isoformat()}
                },
                {"_id": 0}
            ).to_list(100)
            
            # Tâches planifiées
            scheduled_tasks = await db.seo_scheduled_tasks.find(
                {
                    "scheduled_at": {"$gte": start_date.isoformat(), "$lte": end_date.isoformat()}
                },
                {"_id": 0}
            ).to_list(100)
            
            # Organiser par date
            calendar = {}
            
            for page in scheduled_pages:
                date = page.get("scheduled_at", "")[:10]
                if date not in calendar:
                    calendar[date] = {"pages": [], "tasks": []}
                calendar[date]["pages"].append({
                    "id": page["id"],
                    "title": page.get("title_fr", ""),
                    "type": "page",
                    "page_type": page.get("page_type")
                })
            
            for task in scheduled_tasks:
                date = task.get("scheduled_at", "")[:10]
                if date not in calendar:
                    calendar[date] = {"pages": [], "tasks": []}
                calendar[date]["tasks"].append({
                    "id": task["id"],
                    "title": task.get("title", ""),
                    "type": "task",
                    "task_type": task.get("type")
                })
            
            return {
                "success": True,
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "calendar": calendar
            }
        except Exception as e:
            logger.error(f"Error getting content calendar: {e}")
            return {"success": False, "error": str(e)}


logger.info("SEOAutomationManager initialized - V5 LEGO Module")
