# Scheduler Service - Automated Background Tasks
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)


class SchedulerService:
    """
    Service de planification des tâches automatiques.
    Gère les scans de découverte de produits, les rapports, et les maintenances.
    """
    
    def __init__(self, db):
        self.db = db
        self.scheduler = AsyncIOScheduler()
        self.jobs: Dict[str, Any] = {}
        self._started = False
        
    async def start(self):
        """Démarre le scheduler"""
        if self._started:
            return
            
        try:
            self.scheduler.start()
            self._started = True
            logger.info("✅ Scheduler service started successfully")
            
            # Load saved configurations and start jobs
            await self._load_saved_jobs()
            
        except Exception as e:
            logger.error(f"❌ Failed to start scheduler: {e}")
            raise
    
    async def stop(self):
        """Arrête le scheduler"""
        if self._started:
            self.scheduler.shutdown()
            self._started = False
            logger.info("Scheduler service stopped")
    
    async def _load_saved_jobs(self):
        """Charge les configurations de jobs sauvegardées dans la DB"""
        try:
            # Load scanner config
            config = await self.db.scanner_config.find_one({"id": "main_scanner"})
            if config and config.get("is_running"):
                frequency = config.get("frequency", "daily")
                await self.schedule_product_scan(frequency)
                logger.info(f"📅 Loaded product scanner job with frequency: {frequency}")
            
            # Load other scheduled jobs
            scheduled_jobs = await self.db.scheduled_jobs.find({"active": True}).to_list(100)
            for job in scheduled_jobs:
                await self._restore_job(job)
                
        except Exception as e:
            logger.error(f"Error loading saved jobs: {e}")
    
    async def _restore_job(self, job_config: dict):
        """Restaure un job depuis sa configuration"""
        job_type = job_config.get("type")
        job_id = job_config.get("job_id")
        
        if job_type == "report":
            await self.schedule_report(
                job_id=job_id,
                frequency=job_config.get("frequency", "weekly"),
                report_type=job_config.get("report_type", "sales")
            )
    
    # ============================================
    # PRODUCT DISCOVERY SCANNER
    # ============================================
    
    async def schedule_product_scan(self, frequency: str = "daily", sources: list = None):
        """
        Planifie le scan automatique de découverte de produits.
        
        Args:
            frequency: 'hourly', 'daily', 'weekly', 'manual'
            sources: Liste des sources à scanner
        """
        job_id = "product_scanner"
        
        # Remove existing job if any
        if job_id in self.jobs:
            self.scheduler.remove_job(job_id)
            del self.jobs[job_id]
        
        if frequency == "manual":
            logger.info("Product scanner set to manual mode - no automatic scheduling")
            return
        
        # Define trigger based on frequency
        if frequency == "hourly":
            trigger = IntervalTrigger(hours=1)
        elif frequency == "daily":
            trigger = CronTrigger(hour=3, minute=0)  # 3 AM every day
        elif frequency == "weekly":
            trigger = CronTrigger(day_of_week="mon", hour=3, minute=0)  # Monday 3 AM
        elif frequency == "twice_daily":
            trigger = CronTrigger(hour="3,15", minute=0)  # 3 AM and 3 PM
        else:
            trigger = CronTrigger(hour=3, minute=0)  # Default: daily
        
        # Add job
        job = self.scheduler.add_job(
            self._run_product_scan,
            trigger=trigger,
            id=job_id,
            name="Automatic Product Discovery Scan",
            kwargs={"sources": sources},
            replace_existing=True
        )
        
        self.jobs[job_id] = job
        logger.info(f"📅 Product scanner scheduled with frequency: {frequency}")
        
        # Save configuration
        await self.db.scanner_config.update_one(
            {"id": "main_scanner"},
            {
                "$set": {
                    "frequency": frequency,
                    "is_running": True,
                    "last_scheduled": datetime.now(timezone.utc).isoformat(),
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None
                }
            },
            upsert=True
        )
        
        return {
            "job_id": job_id,
            "frequency": frequency,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None
        }
    
    async def stop_product_scan(self):
        """Arrête le scanner de produits"""
        job_id = "product_scanner"
        if job_id in self.jobs:
            self.scheduler.remove_job(job_id)
            del self.jobs[job_id]
            
            await self.db.scanner_config.update_one(
                {"id": "main_scanner"},
                {"$set": {"is_running": False}}
            )
            
            logger.info("Product scanner stopped")
            return True
        return False
    
    async def _run_product_scan(self, sources: list = None):
        """Exécute le scan de découverte de produits"""
        from product_discovery import ProductDiscoveryService
        
        logger.info("🔍 Starting automatic product discovery scan...")
        scan_start = datetime.now(timezone.utc)
        
        try:
            # Initialize discovery service
            discovery_service = ProductDiscoveryService(self.db)
            
            # Get scanner config
            config = await self.db.scanner_config.find_one({"id": "main_scanner"})
            if not config:
                config = {}
            
            # Run scan for each source
            scan_sources = sources or config.get("sources", [])
            if not scan_sources:
                scan_sources = [
                    {"url": "https://www.zone-ecotone.com", "name": "Zone Ecotone"},
                    {"url": "https://www.cabelas.ca/fr", "name": "Cabela's Canada"}
                ]
            
            total_discovered = 0
            results = []
            
            for source in scan_sources:
                try:
                    # Simulate scan (in production, this would actually scrape)
                    source_result = await discovery_service.scan_source(
                        source_url=source.get("url"),
                        source_name=source.get("name")
                    )
                    
                    total_discovered += source_result.get("products_found", 0)
                    results.append(source_result)
                    
                except Exception as e:
                    logger.error(f"Error scanning {source.get('name')}: {e}")
                    results.append({
                        "source": source.get("name"),
                        "error": str(e),
                        "products_found": 0
                    })
            
            scan_end = datetime.now(timezone.utc)
            duration = (scan_end - scan_start).total_seconds()
            
            # Save scan result
            scan_log = {
                "id": f"scan_{scan_start.strftime('%Y%m%d_%H%M%S')}",
                "started_at": scan_start.isoformat(),
                "completed_at": scan_end.isoformat(),
                "duration_seconds": duration,
                "sources_scanned": len(scan_sources),
                "total_products_discovered": total_discovered,
                "results": results,
                "status": "completed"
            }
            
            await self.db.scan_logs.insert_one(scan_log)
            
            # Update last scan time
            await self.db.scanner_config.update_one(
                {"id": "main_scanner"},
                {
                    "$set": {
                        "last_scan": scan_end.isoformat(),
                        "last_scan_duration": duration,
                        "last_scan_products": total_discovered
                    }
                }
            )
            
            logger.info(f"✅ Product scan completed: {total_discovered} products discovered in {duration:.1f}s")
            
            # Create admin notification if products found
            if total_discovered > 0:
                await self.db.admin_notifications.insert_one({
                    "id": f"notif_{scan_start.strftime('%Y%m%d_%H%M%S')}",
                    "type": "scan_complete",
                    "title": f"Scan terminé: {total_discovered} nouveaux produits",
                    "message": f"Le scan automatique a découvert {total_discovered} nouveaux produits à approuver.",
                    "read": False,
                    "created_at": datetime.now(timezone.utc).isoformat()
                })
            
            return scan_log
            
        except Exception as e:
            logger.error(f"❌ Product scan failed: {e}")
            
            # Save failed scan log
            await self.db.scan_logs.insert_one({
                "id": f"scan_{scan_start.strftime('%Y%m%d_%H%M%S')}",
                "started_at": scan_start.isoformat(),
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "status": "failed",
                "error": str(e)
            })
            
            raise
    
    async def run_scan_now(self, sources: list = None):
        """Force un scan immédiat"""
        return await self._run_product_scan(sources)
    
    # ============================================
    # REPORT GENERATION
    # ============================================
    
    async def schedule_report(self, job_id: str, frequency: str, report_type: str):
        """
        Planifie la génération automatique de rapports.
        
        Args:
            job_id: Identifiant unique du job
            frequency: 'daily', 'weekly', 'monthly'
            report_type: 'sales', 'analytics', 'referral', 'inventory'
        """
        # Remove existing job if any
        if job_id in self.jobs:
            self.scheduler.remove_job(job_id)
        
        # Define trigger
        if frequency == "daily":
            trigger = CronTrigger(hour=6, minute=0)  # 6 AM
        elif frequency == "weekly":
            trigger = CronTrigger(day_of_week="mon", hour=6, minute=0)
        elif frequency == "monthly":
            trigger = CronTrigger(day=1, hour=6, minute=0)  # 1st of month
        else:
            trigger = CronTrigger(day_of_week="mon", hour=6, minute=0)
        
        job = self.scheduler.add_job(
            self._generate_report,
            trigger=trigger,
            id=job_id,
            name=f"Auto Report: {report_type}",
            kwargs={"report_type": report_type},
            replace_existing=True
        )
        
        self.jobs[job_id] = job
        
        # Save job config
        await self.db.scheduled_jobs.update_one(
            {"job_id": job_id},
            {
                "$set": {
                    "job_id": job_id,
                    "type": "report",
                    "frequency": frequency,
                    "report_type": report_type,
                    "active": True,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None
                }
            },
            upsert=True
        )
        
        logger.info(f"📊 Report job scheduled: {report_type} ({frequency})")
        return {"job_id": job_id, "next_run": job.next_run_time}
    
    async def _generate_report(self, report_type: str):
        """Génère un rapport automatique"""
        logger.info(f"📊 Generating {report_type} report...")
        
        report_data = {
            "id": f"report_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
            "type": report_type,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "data": {}
        }
        
        try:
            if report_type == "sales":
                report_data["data"] = await self._generate_sales_report()
            elif report_type == "analytics":
                report_data["data"] = await self._generate_analytics_report()
            elif report_type == "referral":
                report_data["data"] = await self._generate_referral_report()
            elif report_type == "inventory":
                report_data["data"] = await self._generate_inventory_report()
            
            # Save report
            await self.db.reports.insert_one(report_data)
            
            logger.info(f"✅ {report_type} report generated successfully")
            return report_data
            
        except Exception as e:
            logger.error(f"❌ Failed to generate {report_type} report: {e}")
            raise
    
    async def _generate_sales_report(self) -> dict:
        """Génère un rapport de ventes"""
        now = datetime.now(timezone.utc)
        week_ago = now - timedelta(days=7)
        
        # Get orders from last week
        orders = await self.db.orders.find({
            "created_at": {"$gte": week_ago.isoformat()}
        }).to_list(1000)
        
        total_revenue = sum(o.get("total", 0) for o in orders)
        total_orders = len(orders)
        
        return {
            "period": "weekly",
            "start_date": week_ago.isoformat(),
            "end_date": now.isoformat(),
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "average_order_value": total_revenue / total_orders if total_orders > 0 else 0
        }
    
    async def _generate_analytics_report(self) -> dict:
        """Génère un rapport d'analytics"""
        now = datetime.now(timezone.utc)
        week_ago = now - timedelta(days=7)
        
        # Get analytics events
        events = await self.db.analytics.find({
            "created_at": {"$gte": week_ago.isoformat()}
        }).to_list(10000)
        
        page_views = len([e for e in events if e.get("event_type") == "page_view"])
        product_views = len([e for e in events if e.get("event_type") == "product_view"])
        
        return {
            "period": "weekly",
            "page_views": page_views,
            "product_views": product_views,
            "unique_sessions": len(set(e.get("session_id") for e in events if e.get("session_id")))
        }
    
    async def _generate_referral_report(self) -> dict:
        """Génère un rapport du programme de parrainage"""
        users = await self.db.referral_users.find({}).to_list(1000)
        
        total_referrals = sum(u.get("referral_stats", {}).get("signups", 0) for u in users)
        total_buyers = sum(u.get("referral_stats", {}).get("buyers", 0) for u in users)
        
        return {
            "total_affiliates": len(users),
            "total_referrals": total_referrals,
            "total_buyers_from_referrals": total_buyers,
            "conversion_rate": (total_buyers / total_referrals * 100) if total_referrals > 0 else 0
        }
    
    async def _generate_inventory_report(self) -> dict:
        """Génère un rapport d'inventaire"""
        products = await self.db.products.find({}).to_list(1000)
        
        return {
            "total_products": len(products),
            "by_category": {},  # Could aggregate by category
            "low_stock": []  # Could identify low stock items
        }
    
    # ============================================
    # MAINTENANCE TASKS
    # ============================================
    
    async def schedule_cleanup(self, days_to_keep: int = 30):
        """Planifie le nettoyage des anciennes données"""
        job_id = "data_cleanup"
        
        if job_id in self.jobs:
            self.scheduler.remove_job(job_id)
        
        # Run weekly on Sunday at 2 AM
        trigger = CronTrigger(day_of_week="sun", hour=2, minute=0)
        
        job = self.scheduler.add_job(
            self._run_cleanup,
            trigger=trigger,
            id=job_id,
            name="Data Cleanup",
            kwargs={"days_to_keep": days_to_keep},
            replace_existing=True
        )
        
        self.jobs[job_id] = job
        logger.info(f"🧹 Cleanup job scheduled (keeping {days_to_keep} days of data)")
    
    async def _run_cleanup(self, days_to_keep: int = 30):
        """Nettoie les anciennes données"""
        logger.info("🧹 Running data cleanup...")
        
        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days_to_keep)).isoformat()
        
        # Clean old analytics events
        result = await self.db.analytics.delete_many({
            "created_at": {"$lt": cutoff_date}
        })
        logger.info(f"Deleted {result.deleted_count} old analytics events")
        
        # Clean old scan logs
        result = await self.db.scan_logs.delete_many({
            "started_at": {"$lt": cutoff_date}
        })
        logger.info(f"Deleted {result.deleted_count} old scan logs")
        
        # Clean read notifications
        result = await self.db.admin_notifications.delete_many({
            "read": True,
            "created_at": {"$lt": cutoff_date}
        })
        logger.info(f"Deleted {result.deleted_count} old notifications")
        
        logger.info("✅ Data cleanup completed")
    
    # ============================================
    # STATUS & MANAGEMENT
    # ============================================
    
    def get_status(self) -> dict:
        """Retourne le statut actuel du scheduler"""
        jobs_info = []
        for job_id, job in self.jobs.items():
            jobs_info.append({
                "id": job_id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "pending": job.pending
            })
        
        return {
            "running": self._started,
            "jobs_count": len(self.jobs),
            "jobs": jobs_info
        }
    
    async def get_scan_history(self, limit: int = 10) -> list:
        """Retourne l'historique des scans"""
        logs = await self.db.scan_logs.find({}).sort("started_at", -1).limit(limit).to_list(limit)
        for log in logs:
            log.pop("_id", None)
        return logs


# Singleton instance
_scheduler_instance: Optional[SchedulerService] = None


def get_scheduler(db) -> SchedulerService:
    """Get or create scheduler instance"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = SchedulerService(db)
    return _scheduler_instance
