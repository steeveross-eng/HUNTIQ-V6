"""
BIONIC HUNT/Chasse V5-ULTIME-FUSION Server
==============================

Architecture Modulaire v2.0 - Phase 6 Complete

Ce fichier est le point d'entrée de l'API.
L'orchestration est déléguée à server_orchestrator.py

Modules unifiés V5:
- admin_unified_engine (fusion admin_engine + admin_advanced_engine)
- notification_unified_engine (fusion notification_engine + communication_engine)

Version: 5.0.0
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==============================================
# MODULE IMPORTS
# ==============================================
from modules.routers import CORE_ROUTERS, MODULE_STATUS
from server_orchestrator import create_orchestrator


# ==============================================
# APPLICATION LIFECYCLE
# ==============================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown"""
    logger.info("=" * 60)
    logger.info("BIONIC HUNT/Chasse V5-ULTIME-FUSION - Server Starting")
    logger.info("=" * 60)
    logger.info("Architecture: Modular v2.0 (Pure Orchestrator)")
    logger.info(f"Total Modules: {MODULE_STATUS['total_modules']}")
    
    # Initialize database
    try:
        from database import init_database
        await init_database()
        logger.info("✓ Database initialized with indexes and seed data")
    except Exception as e:
        logger.warning(f"Database initialization warning: {e}")
    
    # Initialize geo engine indexes
    try:
        from modules.geo_engine.v1 import ensure_indexes
        await ensure_indexes()
        logger.info("✓ Geo Engine 2dsphere indexes created")
    except ImportError:
        logger.info("Geo Engine indexes skipped (module not loaded)")
    except Exception as e:
        logger.warning(f"Geo Engine index creation warning: {e}")
    
    # Initialize territory sync
    try:
        from territory_sync import startup_sync
        await startup_sync()
        logger.info("✓ Territory sync initialized")
    except ImportError:
        logger.info("Territory sync not available")
    except Exception as e:
        logger.warning(f"Territory sync startup failed: {e}")
    
    logger.info("=" * 60)
    logger.info("✓ All modules loaded successfully")
    logger.info("=" * 60)
    
    yield
    
    # Shutdown
    logger.info("Server shutting down...")
    try:
        from territory_sync import shutdown_sync
        await shutdown_sync()
    except Exception:
        pass


# ==============================================
# FASTAPI APPLICATION
# ==============================================
app = FastAPI(
    title="BIONIC HUNT/Chasse V5-ULTIME-FUSION API",
    description="""
## Chasse Bionic™ - API Modulaire Intelligente

BIONIC HUNT/Chasse V5-ULTIME-FUSION est la fusion complète de toutes les versions (V2, V3, V4, BASE) 
en une architecture modulaire unifiée.

### Modules Unifiés V5
- **admin_unified_engine**: Fusion de admin_engine (V4) + admin_advanced_engine (BASE)
- **notification_unified_engine**: Fusion de notification_engine (V4) + communication_engine (BASE)

### Architecture Modulaire (56+ modules)
- **Phase 2**: Core Engines (weather, scoring, ai, nutrition, strategy)
- **Phase 3-6**: Business & Plan Maître Engines
- **Phase 7**: Decoupled Engines
- **V5-BASE**: Modules importés de BIONIC HUNT/Chasse-BASE
- **V5-UNIFIED**: Modules fusionnés et unifiés

### Fonctionnalités Clés
- 🕐 **Legal Time Engine**: Calcul heures légales de chasse
- 🔮 **Predictive Engine**: Prédiction succès de chasse
- 🤖 **AI Engine**: GPT-5.2 pour analyse et recommandations
- 📊 **Analytics Engine**: Statistiques et KPIs de chasse
- 🔔 **Notifications**: Multi-canal (in-app, email, push, SMS)

### Authentification
Certains endpoints nécessitent une authentification via JWT Bearer token.
    """,
    version="5.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    openapi_tags=[
        {"name": "Orchestrator", "description": "System status and health"},
        {"name": "Admin Unified Engine", "description": "Administration unifiée V5"},
        {"name": "Notification Unified Engine", "description": "Notifications unifiées V5"},
        {"name": "Analytics Engine", "description": "Statistiques et KPIs de chasse"},
        {"name": "Legal Time Engine", "description": "Calcul des heures légales de chasse"},
        {"name": "Predictive Engine", "description": "Prédiction de succès de chasse"},
        {"name": "AI Engine", "description": "Intelligence artificielle GPT-5.2"},
        {"name": "Weather Engine", "description": "Analyse météorologique"},
        {"name": "Scoring Engine", "description": "Évaluation des produits"},
    ]
)


# ==============================================
# CORS MIDDLEWARE
# ==============================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================
# ORCHESTRATOR REGISTRATION (Phase 6)
# ==============================================
orchestrator = create_orchestrator(app)

# 1. Register orchestrator endpoints (health, status, modules)
orchestrator.finalize()

# 2. Register core modular routers
orchestrator.register_core_routers(CORE_ROUTERS)

# 3. Register special routers (root-level)
orchestrator.register_special_routers()

# 4. Register legacy router (backward compatibility)
orchestrator.register_legacy_router()

# 5. Register BIONIC Engine P0 router (Phase G)
try:
    from modules.bionic_engine_p0.router import router as bionic_p0_router
    app.include_router(bionic_p0_router, prefix="/api")
    logger.info("✓ BIONIC Engine P0 registered (/api/v1/bionic)")
except ImportError as e:
    logger.warning(f"BIONIC Engine P0 not loaded: {e}")
except Exception as e:
    logger.error(f"BIONIC Engine P0 registration failed: {e}")

# 6. Register Organic Zones V2 router (Pipeline Organique Unifié)
try:
    from modules.bionic_engine_p0.routers.organic_zones_router import router as organic_zones_router
    app.include_router(organic_zones_router)
    logger.info("✓ Organic Zones V2 registered (/api/v1/bionic/organic-zones)")
except Exception as e:
    logger.warning(f"Organic Zones V2 not loaded: {e}")

# 6b. Register Spatial Clipping router (BIONIC V5 300% INVARIANT)
try:
    from modules.bionic_engine_p0.routers.spatial_clipping_router import router as spatial_clipping_router
    app.include_router(spatial_clipping_router)
    logger.info("✓ Spatial Clipping registered (/api/v1/bionic/clipped-zones, /api/v1/bionic/snapshot)")
except Exception as e:
    logger.warning(f"Spatial Clipping not loaded: {e}")


# 7. Register Reports router
try:
    from routes.reports import router as reports_router
    app.include_router(reports_router)
    logger.info("✓ Reports router registered (/api/reports)")
except Exception as e:
    logger.warning(f"Reports router not loaded: {e}")

# 7b. Register User Data router (Waypoints & Places — P0 persistence)
try:
    from routes.user_data import router as user_data_router
    app.include_router(user_data_router)
    logger.info("✓ User Data router registered (/api/user-data)")
except Exception as e:
    logger.warning(f"User Data router not loaded: {e}")

# 8. Register Seasonal Conditions router (PHASE E — Module isolé)
try:
    from modules.bionic_engine_p0.routers.seasonal_conditions_router import router as seasonal_router
    app.include_router(seasonal_router)
    logger.info("✓ Seasonal Conditions registered (/api/v1/bionic/seasonal-conditions)")
except Exception as e:
    logger.warning(f"Seasonal Conditions not loaded: {e}")

# STEVE-MAX: Register Hunting Path & Amenagement router
try:
    from modules.bionic_engine_p0.routers.hunting_path_router import router as hunting_path_router
    app.include_router(hunting_path_router, prefix="/api")
    logger.info("✓ Hunting Path Engine registered (/api/v1/bionic/hunting-path, /api/v1/bionic/amenagement-report)")
except Exception as e:
    logger.warning(f"Hunting Path Engine not loaded: {e}")

# STEVE-MAX: Register BIONIC Engines V2 router
try:
    from modules.bionic_engine_p0.routers.engines_v2_router import router as engines_v2_router
    app.include_router(engines_v2_router, prefix="/api")

    from modules.bionic_engine_p0.routers.engines_v3_router import router as engines_v3_router
    app.include_router(engines_v3_router, prefix="/api")
    logger.info("✓ BIONIC Engines V2 registered (12 engines)")
except Exception as e:
    logger.warning(f"Engines V2 not loaded: {e}")


# 9. Register SSE Engine router (Phase Optimisation #1)
try:
    from modules.bionic_engine_p0.routers.sse_router import router as sse_router
    app.include_router(sse_router)
    logger.info("✓ SSE Engine registered (/api/v1/bionic/sse)")
except Exception as e:
    logger.warning(f"SSE Engine not loaded: {e}")

# 10. Register OSG Engine router (Phase Optimisation #2)
try:
    from modules.bionic_engine_p0.routers.osg_router import router as osg_router
    app.include_router(osg_router)
    logger.info("✓ OSG Engine registered (/api/v1/bionic/osg)")
except Exception as e:
    logger.warning(f"OSG Engine not loaded: {e}")

# 11. Register CME Engine router (Phase Optimisation #3)
try:
    from modules.bionic_engine_p0.routers.cme_router import router as cme_router
    app.include_router(cme_router)
    logger.info("✓ CME Engine registered (/api/v1/bionic/cme)")
except Exception as e:
    logger.warning(f"CME Engine not loaded: {e}")

# 12. Register WSE/WIV Engine router (Phase Optimisation #4)
try:
    from modules.bionic_engine_p0.routers.wse_wiv_router import router as wse_wiv_router
    app.include_router(wse_wiv_router)
    logger.info("✓ WSE/WIV Engine registered (/api/v1/bionic/wse-wiv)")
except Exception as e:
    logger.warning(f"WSE/WIV Engine not loaded: {e}")

# 13. Register VFE Engine router (Phase Optimisation #5)
try:
    from modules.bionic_engine_p0.routers.vfe_router import router as vfe_router
    app.include_router(vfe_router)
    logger.info("✓ VFE Engine registered (/api/v1/bionic/vfe)")
except Exception as e:
    logger.warning(f"VFE Engine not loaded: {e}")

# 14. Register SSVL Engine router (Phase Optimisation #6)
try:
    from modules.bionic_engine_p0.routers.ssvl_router import router as ssvl_router
    app.include_router(ssvl_router)
    logger.info("✓ SSVL Engine registered (/api/v1/bionic/ssvl)")
except Exception as e:
    logger.warning(f"SSVL Engine not loaded: {e}")

# 15. Register TCVE Engine router (Phase Optimisation #7)
try:
    from modules.bionic_engine_p0.routers.tcve_router import router as tcve_router
    app.include_router(tcve_router)
    logger.info("✓ TCVE Engine registered (/api/v1/bionic/tcve)")
except Exception as e:
    logger.warning(f"TCVE Engine not loaded: {e}")

# 16. Register PME Engine router (Phase Optimisation #8)
try:
    from modules.bionic_engine_p0.routers.pme_router import router as pme_router
    app.include_router(pme_router)
    logger.info("✓ PME Engine registered (/api/v1/bionic/pme)")
except Exception as e:
    logger.warning(f"PME Engine not loaded: {e}")

# 17. Register BMPE Engine router (Phase Optimisation #9)
try:
    from modules.bionic_engine_p0.routers.bmpe_router import router as bmpe_router
    app.include_router(bmpe_router)
    logger.info("✓ BMPE Engine registered (/api/v1/bionic/bmpe)")
except Exception as e:
    logger.warning(f"BMPE Engine not loaded: {e}")

# 18. Register TFE Engine router (Phase Optimisation #10)
try:
    from modules.bionic_engine_p0.routers.tfe_router import router as tfe_router
    app.include_router(tfe_router)
    logger.info("✓ TFE Engine registered (/api/v1/bionic/tfe)")
except Exception as e:
    logger.warning(f"TFE Engine not loaded: {e}")

# 19. Register Pipeline router (Phase G — Full Analysis & Metrics)
try:
    from modules.bionic_engine_p0.routers.pipeline_router import router as pipeline_router
    app.include_router(pipeline_router)
    logger.info("✓ Pipeline Engine registered (/api/v1/bionic/pipeline)")
except Exception as e:
    logger.warning(f"Pipeline Engine not loaded: {e}")

# 20. Register API Keys Status router (Phase G+ — System Healthcheck)
try:
    from modules.bionic_engine_p0.routers.api_keys_router import router as api_keys_router
    app.include_router(api_keys_router)
    logger.info("✓ API Keys Status registered (/api/v1/system/api-keys)")
except Exception as e:
    logger.warning(f"API Keys Status not loaded: {e}")

# 21. Register ML Engine router (Phase H — Behavioral Prediction)
try:
    from modules.bionic_engine_p0.routers.ml_router import router as ml_router
    app.include_router(ml_router)
    logger.info("✓ ML Engine registered (/api/v1/bionic/ml)")
except Exception as e:
    logger.warning(f"ML Engine not loaded: {e}")

# 21b. Register Ecological V8 router (Base écologique complète)
try:
    from routes.ecological_router_v8 import router as ecological_v8_router
    app.include_router(ecological_v8_router)
    logger.info("✓ Ecological V8 registered (/api/v1/ecological)")
except Exception as e:
    logger.warning(f"Ecological V8 not loaded: {e}")

# 22. Register DEM Engine router (Real Data — OpenTopography)
try:
    from modules.bionic_engine_p0.routers.dem_router import router as dem_router
    app.include_router(dem_router)
    logger.info("✓ DEM Engine registered (/api/v1/bionic/dem)")
except Exception as e:
    logger.warning(f"DEM Engine not loaded: {e}")

# 23. Register DEM Shadow router (Shadow Pipeline — Real DEM injection)
try:
    from modules.bionic_engine_p0.routers.dem_shadow_router import router as dem_shadow_router
    app.include_router(dem_shadow_router)
    logger.info("✓ DEM Shadow registered (/api/v1/bionic/dem-shadow)")
except Exception as e:
    logger.warning(f"DEM Shadow not loaded: {e}")

# 24. Register Weather Shadow router (Shadow — Open-Meteo)
try:
    from modules.bionic_engine_p0.routers.weather_shadow_router import router as weather_shadow_router
    app.include_router(weather_shadow_router)
    logger.info("✓ Weather Shadow registered (/api/v1/bionic/weather-shadow)")
except Exception as e:
    logger.warning(f"Weather Shadow not loaded: {e}")

# 25. Register Full Shadow Comparison router (DEM + Meteo combines)
try:
    from modules.bionic_engine_p0.routers.full_comparison_router import router as full_comparison_router
    app.include_router(full_comparison_router)
    logger.info("✓ Full Shadow Comparison registered (/api/v1/bionic/shadow)")
except Exception as e:
    logger.warning(f"Full Shadow Comparison not loaded: {e}")

# 26. Register NDVI Shadow router (Sentinel-2 NDVI Shadow Mode)
try:
    from modules.bionic_engine_p0.routers.ndvi_shadow_router import router as ndvi_shadow_router
    app.include_router(ndvi_shadow_router)
    logger.info("✓ NDVI Shadow registered (/api/v1/bionic/ndvi-shadow)")
except Exception as e:
    logger.warning(f"NDVI Shadow not loaded: {e}")

# 27. Register Habitat Score router (Real-time cursor scoring)
try:
    from modules.bionic_engine_p0.routers.habitat_score_router import router as habitat_score_router
    app.include_router(habitat_score_router)
    logger.info("✓ Habitat Score registered (/api/v1/bionic/habitat-score)")
except Exception as e:
    logger.warning(f"Habitat Score not loaded: {e}")

# 28. Register Route Planner router (Tactical route optimization)
try:
    from modules.bionic_engine_p0.routers.route_planner_router import router as route_planner_router
    app.include_router(route_planner_router)
    logger.info("✓ Route Planner registered (/api/v1/bionic/route-planner)")
except Exception as e:
    logger.warning(f"Route Planner not loaded: {e}")

# 29. Register WMS Proxy router (CORS proxy for Quebec WMS services)
try:
    from wms_proxy_router import router as wms_proxy_router
    app.include_router(wms_proxy_router)
    logger.info("✓ WMS Proxy registered (/api/wms-proxy)")
except Exception as e:
    logger.warning(f"WMS Proxy not loaded: {e}")

# 30. Register Movement Corridors router (Real vs Estimated corridors)
try:
    from modules.bionic_engine_p0.routers.movement_corridors_router import router as movement_corridors_router
    app.include_router(movement_corridors_router)
    logger.info("✓ Movement Corridors registered (/api/v1/bionic/movement-corridors)")
except Exception as e:
    logger.warning(f"Movement Corridors not loaded: {e}")

# 31. Register BIONIC Compliance Engine (BCE)
try:
    from bce.router import router as bce_router
    app.include_router(bce_router)
    logger.info("✓ BCE registered (/api/bce/validate, /api/bce/status, /api/bce/certify)")
except Exception as e:
    logger.warning(f"BCE not loaded: {e}")

# 32. Register Weather V8.2 Router
try:
    from modules.bionic_engine_p0.routers.weather_router import router as weather_v82_router
    app.include_router(weather_v82_router)
    logger.info("✓ Weather V8.2 registered (/api/v1/weather/now, /forecast, /influence)")
except Exception as e:
    logger.warning(f"Weather V8.2 not loaded: {e}")

# 33. Register Compare V8.3 Router
try:
    from modules.bionic_engine_p0.routers.compare_router import router as compare_v83_router
    app.include_router(compare_v83_router)
    logger.info("✓ Compare V8.3 registered (/api/v1/compare/waypoints)")
except Exception as e:
    logger.warning(f"Compare V8.3 not loaded: {e}")



# ═══ ALIMENTATION-V1 — Moteur alimentaire scientifique multi-especes ═══
try:
    from modules.alimentation_v1.router import router as alimentation_v1_router
    app.include_router(alimentation_v1_router)
    logger.info("✓ ALIMENTATION-V1 registered (/api/v1/alimentation)")

    from modules.alimentation_v2.router import router as alimentation_v2_router
    app.include_router(alimentation_v2_router)
    logger.info("✓ ALIMENTATION-V2 registered (/api/v2/alimentation)")
except Exception as e:
    logger.warning(f"ALIMENTATION-V1 not loaded: {e}")

# ═══ REPOS-V1 — Moteur zones de repos scientifique multi-especes ═══
try:
    from modules.repos_v1.router import router as repos_v1_router
    app.include_router(repos_v1_router)
    logger.info("✓ REPOS-V1 registered (/api/v1/repos)")
except Exception as e:
    logger.warning(f"REPOS-V1 not loaded: {e}")

# ═══ CORRIDORS-V10 — Moteur corridors fauniques multi-especes ═══
try:
    from modules.corridors_v10.router import router as corridors_v10_router
    app.include_router(corridors_v10_router)
    logger.info("✓ CORRIDORS-V10 registered (/api/v10/corridors)")
except Exception as e:
    logger.warning(f"CORRIDORS-V10 not loaded: {e}")


# ═══ SCORE CONSOLIDÉ — Heatmap multi-moteurs ═══
try:
    from modules.score_consolide import compute_consolidated_score, compute_heatmap_grid
    from fastapi import Query as _Query

    @app.get("/api/v1/score-consolide/point", tags=["SCORE-CONSOLIDE"])
    async def get_consolidated_score(
        lat: float = _Query(...), lng: float = _Query(...),
        species: str = _Query("CERF"), month: int = _Query(10, ge=1, le=12),
    ):
        return compute_consolidated_score(lat, lng, species, month)

    @app.get("/api/v1/score-consolide/heatmap", tags=["SCORE-CONSOLIDE"])
    async def get_heatmap_grid(
        lat: float = _Query(...), lng: float = _Query(...),
        species: str = _Query("CERF"), month: int = _Query(10, ge=1, le=12),
        grid_size: int = _Query(20, ge=5, le=40),
        include_corridors: int = _Query(1, ge=0, le=1),
    ):
        return compute_heatmap_grid(lat, lng, species, month, grid_size, include_corridors=bool(include_corridors))

    logger.info("✓ SCORE-CONSOLIDE registered (/api/v1/score-consolide)")
except Exception as e:
    logger.warning(f"SCORE-CONSOLIDE not loaded: {e}")


# ═══ ENGINE REGISTRY V3 — API Gateway auto-adaptative ═══
try:
    from modules.api_gateway import gateway_v3_router
    app.include_router(gateway_v3_router)
    logger.info("✓ API-GATEWAY-V3: Routeur unifié /api/v3/* enregistré")
except Exception as e:
    logger.warning(f"API-GATEWAY-V3 not loaded: {e}")


logger.info("=" * 60)
logger.info(f"✓ V5-ULTIME-FUSION: {len(CORE_ROUTERS)} modules registered")
logger.info("✓ PHASE G: BIONIC Engine P0 active")
logger.info("✓ ALIMENTATION-V1: Moteur alimentaire multi-especes active")
logger.info("✓ REPOS-V1: Moteur zones de repos multi-especes active")
logger.info("✓ CORRIDORS-V10: Moteur corridors fauniques multi-especes active")
logger.info("✓ SCORE-CONSOLIDE: Heatmap multi-moteurs active")
logger.info("✓ BCE: BIONIC Compliance Engine active")
logger.info("=" * 60)


# ==============================================
# CUSTOM OPENAPI SCHEMA
# ==============================================
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="BIONIC HUNT/Chasse V5-ULTIME-FUSION API",
        version="5.0.0",
        description="API modulaire de chasse intelligente - Fusion V2+V3+V4+BASE",
        routes=app.routes,
    )
    
    openapi_schema["tags"] = [
        {"name": "Orchestrator", "description": "System status and health"},
        {"name": "V5-Unified", "description": "Modules unifiés V5 (admin, notifications)"},
        {"name": "Core Engines", "description": "Phase 2 - Nutrition, Scoring, AI, Weather, Geospatial"},
        {"name": "Business Engines", "description": "Phase 3 - User, Territory, Referral"},
        {"name": "Master Plan", "description": "Phase 4 - Recommendations, Collaborative, Wildlife"},
        {"name": "Data Layers", "description": "Phase 5 - Ecoforestry, Behavioral, Simulation"},
        {"name": "Live Heading", "description": "Phase 6 - Immersive navigation"},
        {"name": "V5-BASE", "description": "Modules importés de BIONIC HUNT/Chasse-BASE"},
        {"name": "Legacy", "description": "Backward compatibility endpoints"},
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


# ==============================================
# STATIC AUDIT FILES
# ==============================================
from fastapi.responses import FileResponse, JSONResponse
import os as _os

_MIME_MAP = {
    ".md": "text/markdown",
    ".yaml": "text/yaml",
    ".yml": "text/yaml",
    ".pdf": "application/pdf",
    ".txt": "text/plain",
    ".png": "image/png",
    ".json": "application/json",
}

_AUDIT_FILES = [
    "BIONIC_AUDIT_ECOLOGIQUE_v1.md",
    "BIONIC_AUDIT_ECOLOGIQUE_v1.yaml",
    "BIONIC_AUDIT_ECOLOGIQUE_v1.pdf",
    "pipeline_ecologique_v1.txt",
    "PLAN_DE_MATCH_STEEVE_MAX_v1.md",
    "PLAN_DE_MATCH_STEEVE_MAX_v1.pdf",
]

@app.get("/api/audit/list")
async def list_audit_files():
    base = _os.path.join(_os.path.dirname(__file__), "static")
    files = []
    for f in _AUDIT_FILES:
        fpath = _os.path.join(base, f)
        if _os.path.exists(fpath):
            ext = _os.path.splitext(f)[1].lower()
            files.append({
                "filename": f,
                "size_bytes": _os.path.getsize(fpath),
                "type": _MIME_MAP.get(ext, "application/octet-stream"),
                "download_url": f"/api/audit/{f}",
            })
    return JSONResponse(content={"audit_files": files, "total": len(files)})

@app.get("/api/audit/{filename}")
async def serve_audit_file(filename: str):
    safe_name = _os.path.basename(filename)
    path = _os.path.join(_os.path.dirname(__file__), "static", safe_name)
    if _os.path.exists(path):
        ext = _os.path.splitext(safe_name)[1].lower()
        media = _MIME_MAP.get(ext, "application/octet-stream")
        return FileResponse(path, filename=safe_name, media_type=media)
    from fastapi import HTTPException as _HTTPException
    raise _HTTPException(status_code=404, detail="File not found")


# ==============================================
# MAIN
# ==============================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
