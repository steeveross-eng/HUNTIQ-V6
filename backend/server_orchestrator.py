"""
V5-ULTIME Server Orchestrator
==============================

Architecture Modulaire v2.0 - Phase 6 Complete

Ce fichier gère uniquement l'orchestration :
- Enregistrement des routeurs
- Cycle de vie de l'application
- Health checks

Toute logique métier est dans /modules/*
"""

import logging
from typing import List, Tuple
from fastapi import FastAPI, APIRouter

logger = logging.getLogger(__name__)


class ServerOrchestrator:
    """
    V5-ULTIME Server Orchestrator
    
    Responsabilités:
    - Enregistrer tous les routeurs de modules
    - Gérer le cycle de vie de l'application
    - Fournir les endpoints de santé et statut
    """
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.registered_modules = []
        self.orchestrator_router = APIRouter(prefix="/api")
        self._setup_orchestrator_routes()
    
    def _setup_orchestrator_routes(self):
        """Configure les routes de l'orchestrateur"""
        
        @self.orchestrator_router.get("/")
        async def root():
            """API Root - Health check"""
            return {
                "message": "Chasse Bionic™ - BIONIC HUNT/Chasse V5-ULTIME",
                "status": "operational",
                "version": "5.0.0",
                "architecture": "modular_v2.0_unified",
                "modules": len(self.registered_modules),
                "docs": "/api/docs"
            }
        
        @self.orchestrator_router.get("/health")
        async def health_check():
            """Simple health check endpoint"""
            return {
                "status": "healthy",
                "service": "huntiq-backend",
                "version": "5.0.0",
                "architecture": "V5-ULTIME"
            }
        
        @self.orchestrator_router.get("/status")
        async def status():
            """Detailed status endpoint"""
            from modules.routers import MODULE_STATUS, CORE_ROUTERS
            return {
                "status": "operational",
                "version": "5.0.0",
                "architecture": MODULE_STATUS.get("architecture_version", "V5-ULTIME"),
                "modules": {
                    "total": MODULE_STATUS.get("total_modules", 0),
                    "loaded": len(CORE_ROUTERS),
                    "unified": self._count_unified_modules()
                }
            }
        
        @self.orchestrator_router.get("/modules/status")
        async def modules_status():
            """Get status of all loaded modules"""
            from modules.routers import MODULE_STATUS, CORE_ROUTERS
            return {
                "total_modules": MODULE_STATUS.get("total_modules", 0),
                "architecture_version": MODULE_STATUS.get("architecture_version", "V5-ULTIME"),
                "unified_modules": [
                    m for m in self.registered_modules 
                    if "unified" in m.get("name", "").lower()
                ],
                "modules": [
                    {
                        "name": meta["name"],
                        "version": meta["version"],
                        "phase": meta.get("phase", 0),
                        "description": meta.get("description", ""),
                        "prefix": router.prefix
                    }
                    for router, meta in CORE_ROUTERS
                ],
                "status": "operational"
            }
        
        @self.orchestrator_router.get("/modules/health")
        async def modules_health():
            """Quick health check for all modules"""
            from modules.routers import MODULE_STATUS
            return {
                "status": "healthy",
                "total_modules": MODULE_STATUS.get("total_modules", 0),
                "unified_modules": self._count_unified_modules(),
                "phases": {
                    "phase_2": MODULE_STATUS.get("phase_2_modules", 0),
                    "phase_3": MODULE_STATUS.get("phase_3_modules", 0),
                    "phase_4": MODULE_STATUS.get("phase_4_modules", 0),
                    "phase_5": MODULE_STATUS.get("phase_5_modules", 0),
                    "phase_6": MODULE_STATUS.get("phase_6_modules", 0),
                    "phase_7": MODULE_STATUS.get("phase_7_modules", 0),
                    "V5_UNIFIED": self._count_unified_modules()
                }
            }
    
    def _count_unified_modules(self) -> int:
        """Compte les modules unifiés V5"""
        return len([m for m in self.registered_modules if m.get("phase") == "V5-UNIFIED"])
    
    def register_core_routers(self, routers: List[Tuple[APIRouter, dict]]):
        """
        Enregistre tous les routeurs principaux
        
        Args:
            routers: Liste de tuples (router, metadata)
        """
        for router, meta in routers:
            self.app.include_router(router)
            self.registered_modules.append(meta)
            logger.info(f"✓ Loaded: {meta['name']} v{meta['version']} [{router.prefix}]")
    
    def register_special_routers(self):
        """Enregistre les routeurs spéciaux (root-level, awaiting migration)"""
        
        # Site access control
        try:
            from site_access import access_router
            self.app.include_router(access_router)
            logger.info("✓ Loaded: Site Access Control [/api/site/*]")
        except ImportError as e:
            logger.debug(f"Site Access not available: {e}")
        
        # Territory analysis
        try:
            from territory import territory_router, territories_router
            self.app.include_router(territory_router)
            self.app.include_router(territories_router)
            logger.info("✓ Loaded: Territory Analysis [/api/territory/*]")
            logger.info("✓ Loaded: Territory Inventory [/api/territories/*]")
        except ImportError as e:
            logger.debug(f"Territory not available: {e}")
        
        # Admin Geo Engine
        try:
            from modules.geo_engine.admin import router as admin_geo_router
            self.app.include_router(admin_geo_router)
            logger.info("✓ Loaded: Admin Geo Engine [/api/admin/geo/*]")
        except ImportError as e:
            logger.debug(f"Admin Geo not available: {e}")
        
        # WebSocket Geo Sync
        try:
            from websocket.geo_sync import router as ws_geo_router
            self.app.include_router(ws_geo_router)
            logger.info("✓ Loaded: WebSocket Geo Sync [/ws/geo-sync]")
        except ImportError as e:
            logger.debug(f"WebSocket Geo not available: {e}")
        
        # Bathymetry
        try:
            from routes.bathymetry import router as bathymetry_router
            self.app.include_router(bathymetry_router)
            logger.info("✓ Loaded: Bathymetry API [/api/bathymetry/*]")
        except ImportError as e:
            logger.debug(f"Bathymetry not available: {e}")
        
        # Advanced Zones
        try:
            from routes.advanced_zones import router as advanced_zones_router
            self.app.include_router(advanced_zones_router)
            logger.info("✓ Loaded: Advanced Zones [/api/territory/zones/*]")
        except ImportError as e:
            logger.debug(f"Advanced Zones not available: {e}")
    
    def register_legacy_router(self):
        """Enregistre le routeur legacy (backward compatibility)"""
        try:
            from server_monolith_backup import api_router as legacy_router
            self.app.include_router(legacy_router)
            logger.info("✓ Loaded: Legacy monolith router [/api/*] (DEPRECATED)")
        except ImportError as e:
            logger.debug(f"Legacy router not available: {e}")
    
    def finalize(self):
        """Finalise l'orchestration et enregistre le routeur principal"""
        self.app.include_router(self.orchestrator_router)
        logger.info("=" * 60)
        logger.info(f"✓ V5-ULTIME Orchestrator: {len(self.registered_modules)} modules loaded")
        logger.info(f"✓ Unified modules: {self._count_unified_modules()}")
        logger.info("=" * 60)


def create_orchestrator(app: FastAPI) -> ServerOrchestrator:
    """
    Factory function pour créer l'orchestrateur
    
    Usage dans server.py:
        from server_orchestrator import create_orchestrator
        orchestrator = create_orchestrator(app)
        orchestrator.register_core_routers(CORE_ROUTERS)
        orchestrator.register_special_routers()
        orchestrator.finalize()
    """
    return ServerOrchestrator(app)
