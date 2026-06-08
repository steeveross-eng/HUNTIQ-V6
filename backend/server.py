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
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.openapi.utils import get_openapi

# Load environment variables
from dotenv import load_dotenv
# P22ΩΩ_DEPLOYMENT_FIX_Ω (2026-05-22) — override=False : les env vars Kubernetes
# (injectées par le pod spec deployed) priment sur le .env disk. Préserve les
# secrets de production (MONGO_URL, R2_*, etc.) sans risque d'écrasement par le
# .env Preview embedded dans l'image.
load_dotenv(override=False)

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
    
    # BCE-4X PERF: Pre-charge du cache eau au demarrage
    try:
        from modules.bionic_engine_p0.services.zone_engine_core_v2 import preload_water_cache
        preload_water_cache()
        logger.info("✓ Water cache pre-loaded (BCE-4X Performance)")
    except Exception as e:
        logger.warning(f"Water cache preload warning: {e}")
    
    # Phase 3.2-S BCE-4X: Pre-charge du cache urbain STATIQUE au demarrage
    try:
        from modules.bionic_engine_p0.services.zone_engine_core_v2 import preload_urban_cache
        preload_urban_cache()
        logger.info("✓ Urban cache pre-loaded (Phase 3.2-S SAFE MODE)")
    except Exception as e:
        logger.warning(f"Urban cache preload warning: {e}")
    
    # x7000: Create MongoDB indexes for supplier_submissions
    try:
        from engines.nutrition_intelligence.x7000_supplier_product_engine import ensure_indexes
        await ensure_indexes()
        logger.info("✓ x7000 supplier_submissions indexes created")
    except Exception as e:
        logger.warning(f"x7000 index creation warning: {e}")
    
    # CAM-Omega: Create camera engine indexes
    try:
        from modules.camera_engine.v1.router import ensure_camera_indexes
        from modules.camera_engine.dependencies import get_camera_db
        cam_db = get_camera_db()
        await ensure_camera_indexes(cam_db)
        logger.info("✓ Camera engine indexes created")
    except Exception as e:
        logger.warning(f"Camera engine index creation warning: {e}")
    
    # VIS-A: Create vision engine indexes
    try:
        from modules.vision_engine.v1.router import ensure_vision_indexes
        from modules.camera_engine.dependencies import get_camera_db as get_vis_db
        vis_db = get_vis_db()
        await ensure_vision_indexes(vis_db)
        logger.info("✓ Vision engine indexes created")
    except Exception as e:
        logger.warning(f"Vision engine index creation warning: {e}")
    
    # P22ΩΩ_BUNDLE_DEGRADED_CACHE · 2026-05-14 · COMMANDANT STEEVE-MAX
    # FastAPI utilise lifespan=lifespan → tous les @app.on_event("startup")
    # définis plus bas sont IGNORÉS (FastAPI 0.95+). On invoque donc
    # explicitement v20_startup() ici pour activer :
    #  - le chargement du cache disque
    #  - les daemons prechauffage / periodic_refresh / v5_monitor (sous env var)
    try:
        from engines.v8_institutional.v20_performance_bundle import v20_startup as _v20_startup
        await _v20_startup()
        logger.info("✓ V20-PERFORMANCE startup hook fired (BSL5 warmup scheduled)")
    except Exception as e:
        logger.warning(f"V20 startup hook from lifespan failed: {e}", exc_info=True)

    # ═══════════════════════════════════════════════════════════════════════
    # P22ΩΩ_PREWARM_SYNCHRONE_BETA · 2026-05-18 · COMMANDANT STEEVE-MAX
    # DIRECTIVE BCE-4X ULTIME ABSOLU — P0b option β VALIDÉE
    # ─────────────────────────────────────────────────────────────────────
    # OBJECTIF : Éliminer la latence cold-start de 12+ secondes sur le
    # premier hit utilisateur de /api/v20/territoire/bundle.
    #
    # STRATÉGIE :
    #   - Lance UN seul prewarm canonique (orignal @ waypoint BSL standard)
    #     en background non-bloquant pour le boot.
    #   - Utilise _warmup_single() qui set le contextvar warmup pour bypass
    #     le hardcap 20s. Le cache (LRU + Redis fallback + disk) est peuplé
    #     pour le tier le plus haut (ENRICHI_TDELTA / COMPLET_T0).
    #   - À la première requête utilisateur sur les contextes standards,
    #     cache HIT garanti (~50ms).
    #
    # PORTÉE DÉLIBÉRÉMENT RESTREINTE :
    #   - 1 espèce primaire (orignal) × 1 contexte canonique
    #   - Pas les daemons BSL5 complets (5 espèces × 2 contextes = 10 prewarms
    #     séquentiels sur 60s+ → saturation worker garantie)
    #   - Pas de prechauffage daemons périodiques (DISABLED par défaut)
    #
    # SOFT-FAIL : aucune exception ne bloque le boot.
    # ═══════════════════════════════════════════════════════════════════════
    try:
        import asyncio as _asyncio
        from engines.v8_institutional.v20_performance_bundle import _warmup_single

        async def _prewarm_canonical_omega():
            """Prewarm async non-bloquant — 2 espèces canoniques BSL séquentiel."""
            try:
                # P22ΩΩ_PREWARM_BIS · 2026-05-18 · COMMANDANT STEEVE-MAX
                # Étendu à chevreuil (alias frontend `cerf` = default
                # MonTerritoireBionicPage) + orignal (espèce primaire de
                # validation visuelle).
                # Exécution SÉQUENTIELLE (1 par 1) pour ne pas saturer le
                # single-worker uvicorn — chaque _warmup_single ~50s.
                _waypoint = (48.206657, -68.382422)  # Bas-Saint-Laurent QC canonique
                for _species in ("chevreuil", "orignal"):
                    _t = await _warmup_single(
                        lat=_waypoint[0],
                        lon=_waypoint[1],
                        species=_species,
                    )
                    logger.info(
                        f"[P22ΩΩ_PREWARM_SYNCHRONE_BETA] Bundle '{_species}' warmed in "
                        f"{_t:.1f}s @ {_waypoint[0]},{_waypoint[1]} — cache HIT actif"
                    )
                logger.info(
                    "[P22ΩΩ_PREWARM_SYNCHRONE_BETA] Prewarm complet pour "
                    "(chevreuil, orignal) — first user hit = cache HIT garanti"
                )
            except Exception as _e:
                logger.warning(f"[P22ΩΩ_PREWARM_SYNCHRONE_BETA] Warmup failed: {_e}")

        _asyncio.create_task(_prewarm_canonical_omega())
        logger.info("✓ P22ΩΩ_PREWARM_SYNCHRONE_BETA scheduled (background, non-blocking)")
    except Exception as e:
        logger.warning(f"P22ΩΩ_PREWARM_SYNCHRONE_BETA scheduling failed: {e}")
    
    # P22ΩΩ — Self-audit DÉSACTIVÉ : lance des pytest subprocess qui hog le worker
    # Pour réactiver : export P22OMEGA_SELF_AUDIT=1
    # try:
    #     from engines.v8_institutional.self_audit_omega import v20_self_audit_on_startup as _self_audit
    #     import asyncio as _asyncio
    #     _asyncio.create_task(_self_audit())
    #     logger.info("✓ SELF-AUDIT-Ω scheduled (background)")
    # except Exception as e:
    #     logger.warning(f"SELF-AUDIT-Ω startup from lifespan failed: {e}")
    logger.info("[P22ΩΩ] SELF-AUDIT-Ω DISABLED (lance subprocess pytest qui hog le worker)")

    # P22ΩΩ_TERRITOIRE_ESSENTIEL_1WORKER · 2026-05-18 · STEEVE-MAX
    # Cron pré-calcul 2000 membres : actif uniquement si P22OMEGA_PREWARM_MEMBERS_CRON=1
    try:
        import asyncio as _asyncio_cron
        from engines.v8_institutional.essentiel_prewarm_cron import (
            essentiel_prewarm_cron_daemon as _prewarm_daemon,
            _is_cron_enabled as _is_prewarm_cron_enabled,
        )
        if _is_prewarm_cron_enabled():
            _asyncio_cron.create_task(_prewarm_daemon())
            logger.info("✓ P22ΩΩ_ESSENTIEL_PREWARM cron daemon scheduled (background)")
        else:
            logger.info("[P22ΩΩ] ESSENTIEL_PREWARM cron daemon DISABLED (env P22OMEGA_PREWARM_MEMBERS_CRON != 1)")
    except Exception as e:
        logger.warning(f"P22ΩΩ_ESSENTIEL_PREWARM cron daemon failed to schedule: {e}")
    
    # P22ΩΩ_DEPLOYED_WORKERS_INPROCESS_Ω · 2026-05-22 · COMMANDANT STEEVE-MAX
    # ──────────────────────────────────────────────────────────────────────
    # OBJECTIF : démarrer les 6 workers β2-ΣΤ directement dans le pod déployé
    # (où le supervisor managed externe `zerocost-seed-r5-watchdog` n'existe
    # pas). En Preview, le supervisor externe est auto-détecté → ce launcher
    # in-process se désactive automatiquement (skip) pour éviter le doublon.
    #
    # GARANTIES :
    #   - additif strict (Verrou Phase III maintenu)
    #   - soft-fail : aucune exception ne bloque le boot
    #   - asyncio watchdog interne (check liveness toutes les 60 s)
    #   - relance automatique si workers vivants < ZEROCOST_INPROCESS_MIN_WORKERS
    #   - terminé proprement au shutdown du backend
    #
    # P22ΩΩ_DEPLOYMENT_FIX_Ω : spawn non-bloquant via asyncio.create_task pour
    # ne pas retarder la K8s readiness probe pendant le boot. Les workers
    # démarreront ~2 s après que uvicorn soit ready (gain de readiness OK).
    # ──────────────────────────────────────────────────────────────────────
    import os as _os_p22
    import asyncio as _asyncio_p22

    async def _deferred_zerocost_start():
        try:
            # Délai bref pour permettre à uvicorn de finir son startup
            # et répondre aux readiness probes K8s avant de spawn les workers.
            startup_delay = float(_os_p22.environ.get("ZEROCOST_INPROCESS_STARTUP_DELAY_S", "2"))
            await _asyncio_p22.sleep(startup_delay)
            from zerocost_workers_runtime import start_zerocost_workers_inprocess
            await start_zerocost_workers_inprocess()
        except Exception as e:
            logger.warning(f"[P22ΩΩ_DEPLOYED_WORKERS_INPROCESS_Ω] deferred start failed: {e}")

    try:
        _asyncio_p22.create_task(_deferred_zerocost_start())
        logger.info("[P22ΩΩ_DEPLOYED_WORKERS_INPROCESS_Ω] β2-ΣΤ workers spawn scheduled (deferred non-blocking)")
    except Exception as e:
        logger.warning(f"[P22ΩΩ_DEPLOYED_WORKERS_INPROCESS_Ω] task scheduling failed: {e}")

    # ──────────────────────────────────────────────────────────────────────
    # P22ΩΩ_MANIFEST_CRON_Ω · 2026-05-22 · COMMANDANT STEEVE-MAX
    # ──────────────────────────────────────────────────────────────────────
    # OBJECTIF : régénérer le manifest CDN R2 toutes les 30 min pour corriger
    # le drift R2 ↔ manifest (mesuré à 6.6× avant ce fix). Le script
    # `/app/backend/tools/zerocost_manifest_update.py` est invoqué en
    # subprocess non-bloquant via asyncio.create_subprocess_exec.
    #
    # GARANTIES :
    #   - additif strict (Verrou Phase III maintenu)
    #   - soft-fail : aucune exception ne bloque le boot
    #   - tick configurable via env var ZEROCOST_MANIFEST_INTERVAL_S (défaut 1800 s)
    #   - première exécution après ZEROCOST_MANIFEST_FIRST_DELAY_S (défaut 30 s)
    #   - désactivation explicite via ZEROCOST_MANIFEST_CRON_DISABLE=1
    # ──────────────────────────────────────────────────────────────────────
    async def _manifest_rotation_cron():
        manifest_script = "/app/backend/tools/zerocost_manifest_update.py"
        # Résolution du Python du venv backend (boto3 installé là, pas dans /usr/bin/python3)
        import sys as _sys_p22
        from pathlib import Path as _Path_p22
        _venv_py = "/root/.venv/bin/python3"
        python_bin = _venv_py if _Path_p22(_venv_py).is_file() else _sys_p22.executable
        first_delay = float(_os_p22.environ.get("ZEROCOST_MANIFEST_FIRST_DELAY_S", "30"))
        interval = float(_os_p22.environ.get("ZEROCOST_MANIFEST_INTERVAL_S", "1800"))  # 30 min
        run_count = 0
        try:
            await _asyncio_p22.sleep(first_delay)
            while True:
                run_count += 1
                started_at = _asyncio_p22.get_event_loop().time()
                try:
                    proc = await _asyncio_p22.create_subprocess_exec(
                        python_bin, manifest_script,
                        stdout=_asyncio_p22.subprocess.PIPE,
                        stderr=_asyncio_p22.subprocess.PIPE,
                    )
                    stdout, stderr = await _asyncio_p22.wait_for(proc.communicate(), timeout=120.0)
                    elapsed = _asyncio_p22.get_event_loop().time() - started_at
                    if proc.returncode == 0:
                        last_line = (stdout.decode("utf-8", errors="replace").strip().split("\n") or [""])[-1]
                        logger.info(
                            f"[P22ΩΩ_MANIFEST_CRON_Ω] run #{run_count} OK · {elapsed:.1f}s · {last_line[:160]}"
                        )
                    else:
                        err_tail = stderr.decode("utf-8", errors="replace").strip().split("\n")[-1][:200]
                        logger.warning(
                            f"[P22ΩΩ_MANIFEST_CRON_Ω] run #{run_count} FAILED · "
                            f"exit={proc.returncode} · {elapsed:.1f}s · err={err_tail}"
                        )
                except _asyncio_p22.TimeoutError:
                    logger.warning(f"[P22ΩΩ_MANIFEST_CRON_Ω] run #{run_count} TIMEOUT (>120s)")
                    try:
                        proc.kill()
                    except Exception:
                        pass
                except Exception as run_err:
                    logger.warning(f"[P22ΩΩ_MANIFEST_CRON_Ω] run #{run_count} ERROR: {run_err}")
                await _asyncio_p22.sleep(interval)
        except _asyncio_p22.CancelledError:
            logger.info("[P22ΩΩ_MANIFEST_CRON_Ω] cancelled cleanly")
        except Exception as e:
            logger.warning(f"[P22ΩΩ_MANIFEST_CRON_Ω] cron crashed: {e}")

    if _os_p22.environ.get("ZEROCOST_MANIFEST_CRON_DISABLE", "").strip() in ("1", "true", "yes"):
        logger.info("[P22ΩΩ_MANIFEST_CRON_Ω] désactivé par ZEROCOST_MANIFEST_CRON_DISABLE=1")
    else:
        try:
            _asyncio_p22.create_task(_manifest_rotation_cron())
            logger.info(
                "[P22ΩΩ_MANIFEST_CRON_Ω] manifest rotation scheduled "
                "(first=30s · interval=30min · non-blocking background)"
            )
        except Exception as e:
            logger.warning(f"[P22ΩΩ_MANIFEST_CRON_Ω] task scheduling failed: {e}")

    # ──────────────────────────────────────────────────────────────────────
    # P22ΩΩ_RAPPORT_3RF_T95_WATCHER_Ω · COMMANDANT STEEVE-MAX · 2026-02-20
    # ──────────────────────────────────────────────────────────────────────
    # Watcher asyncio LECTURE SEULE qui invoke rapport_3rf_t95_emit.py toutes
    # les ~30 min. Le wrapper court-circuite si déjà émis (idempotent).
    # Dès atteinte 95 % couverture cellulaire 3 RF, le rapport FULL est
    # écrit automatiquement dans /app/memory/RAPPORT_3RF_T+95%_Ω_EMITTED.md
    #
    # GARANTIES :
    #   - additif strict (Verrou Phase III maintenu)
    #   - LECTURE SEULE sur R2 (aucune écriture)
    #   - soft-fail (aucune exception ne bloque le boot)
    #   - idempotent (state persistant dans backend/state/)
    #   - désactivation : RAPPORT_3RF_T95_WATCHER_DISABLE=1
    # ──────────────────────────────────────────────────────────────────────
    async def _rapport_3rf_t95_watcher():
        emit_script = "/app/backend/tools/rapport_3rf_t95_emit.py"
        import sys as _sys_t95
        from pathlib import Path as _Path_t95
        _venv_py = "/root/.venv/bin/python3"
        python_bin = _venv_py if _Path_t95(_venv_py).is_file() else _sys_t95.executable
        first_delay = float(_os_p22.environ.get("RAPPORT_3RF_T95_WATCHER_FIRST_DELAY_S", "120"))
        interval = float(_os_p22.environ.get("RAPPORT_3RF_T95_WATCHER_INTERVAL_S", "1800"))  # 30 min
        run_count = 0
        try:
            await _asyncio_p22.sleep(first_delay)
            while True:
                run_count += 1
                started_at = _asyncio_p22.get_event_loop().time()
                try:
                    proc = await _asyncio_p22.create_subprocess_exec(
                        python_bin, emit_script,
                        stdout=_asyncio_p22.subprocess.PIPE,
                        stderr=_asyncio_p22.subprocess.PIPE,
                    )
                    stdout, stderr = await _asyncio_p22.wait_for(proc.communicate(), timeout=420.0)
                    elapsed = _asyncio_p22.get_event_loop().time() - started_at
                    if proc.returncode == 0:
                        last_line = (stdout.decode("utf-8", errors="replace").strip().split("\n") or [""])[-1]
                        logger.info(
                            f"[P22ΩΩ_RAPPORT_3RF_T95_Ω] check #{run_count} OK · {elapsed:.1f}s · {last_line[:200]}"
                        )
                    else:
                        err_tail = stderr.decode("utf-8", errors="replace").strip().split("\n")[-1][:200]
                        logger.warning(
                            f"[P22ΩΩ_RAPPORT_3RF_T95_Ω] check #{run_count} FAILED · "
                            f"exit={proc.returncode} · {elapsed:.1f}s · err={err_tail}"
                        )
                except _asyncio_p22.TimeoutError:
                    logger.warning(f"[P22ΩΩ_RAPPORT_3RF_T95_Ω] check #{run_count} TIMEOUT (>420s)")
                    try:
                        proc.kill()
                    except Exception:
                        pass
                except Exception as run_err:
                    logger.warning(f"[P22ΩΩ_RAPPORT_3RF_T95_Ω] check #{run_count} ERROR: {run_err}")
                await _asyncio_p22.sleep(interval)
        except _asyncio_p22.CancelledError:
            logger.info("[P22ΩΩ_RAPPORT_3RF_T95_Ω] cancelled cleanly")
        except Exception as e:
            logger.warning(f"[P22ΩΩ_RAPPORT_3RF_T95_Ω] watcher crashed: {e}")

    if _os_p22.environ.get("RAPPORT_3RF_T95_WATCHER_DISABLE", "").strip() in ("1", "true", "yes"):
        logger.info("[P22ΩΩ_RAPPORT_3RF_T95_Ω] désactivé par RAPPORT_3RF_T95_WATCHER_DISABLE=1")
    else:
        try:
            _asyncio_p22.create_task(_rapport_3rf_t95_watcher())
            logger.info(
                "[P22ΩΩ_RAPPORT_3RF_T95_Ω] watcher armé (first=120s · interval=30min · "
                "seuil=95% · LECTURE SEULE · sortie=/app/memory/RAPPORT_3RF_T+95%_Ω_EMITTED.md)"
            )
        except Exception as e:
            logger.warning(f"[P22ΩΩ_RAPPORT_3RF_T95_Ω] watcher scheduling failed: {e}")

    # ──────────────────────────────────────────────────────────────────────
    # P22ΩΩ_AUTOPILOT_4D_SAFE_Ω · COMMANDANT STEEVE-MAX · 2026-02-20
    # ──────────────────────────────────────────────────────────────────────
    # Orchestrateur 4 jours · transition Phase 1 (3RF) → Phase 2 (QC limitrophes
    # STRUCTURAL) → Phase 3 (Habitat Fusion structural). LECTURE SEULE + génération
    # rapports périodiques (T+100% final · QC progress 12h · Habitat fusion 24h).
    #
    # GARANTIES :
    #   - additif strict (Verrou Phase III maintenu)
    #   - LECTURE SEULE sur R2 (aucune écriture R2)
    #   - aucune ingestion NDVI/LiDAR réelle
    #   - aucune extension pan-Canada (priority=3 = DECLARED_NOT_COMPUTED)
    #   - aucune modification supervisor automatique (transition Phase 2 requiert
    #     validation Commandant via PHASE_2_TRANSITION_READY_Ω.md)
    #   - désactivation : AUTOPILOT_4D_SAFE_DISABLE=1
    # ──────────────────────────────────────────────────────────────────────
    async def _autopilot_4d_safe_watcher():
        emit_script = "/app/backend/tools/autopilot_4d_safe_omega.py"
        import sys as _sys_ap
        from pathlib import Path as _Path_ap
        _venv_py = "/root/.venv/bin/python3"
        python_bin = _venv_py if _Path_ap(_venv_py).is_file() else _sys_ap.executable
        first_delay = float(_os_p22.environ.get("AUTOPILOT_4D_SAFE_FIRST_DELAY_S", "240"))
        interval = float(_os_p22.environ.get("AUTOPILOT_4D_SAFE_INTERVAL_S", "1800"))  # 30 min
        run_count = 0
        try:
            await _asyncio_p22.sleep(first_delay)
            while True:
                run_count += 1
                started_at = _asyncio_p22.get_event_loop().time()
                try:
                    proc = await _asyncio_p22.create_subprocess_exec(
                        python_bin, emit_script,
                        stdout=_asyncio_p22.subprocess.PIPE,
                        stderr=_asyncio_p22.subprocess.PIPE,
                    )
                    stdout, stderr = await _asyncio_p22.wait_for(proc.communicate(), timeout=600.0)
                    elapsed = _asyncio_p22.get_event_loop().time() - started_at
                    if proc.returncode == 0:
                        last_line = (stdout.decode("utf-8", errors="replace").strip().split("\n") or [""])[-1]
                        logger.info(
                            f"[P22ΩΩ_AUTOPILOT_4D_SAFE_Ω] check #{run_count} OK · {elapsed:.1f}s · {last_line[:200]}"
                        )
                    else:
                        err_tail = stderr.decode("utf-8", errors="replace").strip().split("\n")[-1][:200]
                        logger.warning(
                            f"[P22ΩΩ_AUTOPILOT_4D_SAFE_Ω] check #{run_count} FAILED · "
                            f"exit={proc.returncode} · {elapsed:.1f}s · err={err_tail}"
                        )
                except _asyncio_p22.TimeoutError:
                    logger.warning(f"[P22ΩΩ_AUTOPILOT_4D_SAFE_Ω] check #{run_count} TIMEOUT (>600s)")
                    try:
                        proc.kill()
                    except Exception:
                        pass
                except Exception as run_err:
                    logger.warning(f"[P22ΩΩ_AUTOPILOT_4D_SAFE_Ω] check #{run_count} ERROR: {run_err}")
                await _asyncio_p22.sleep(interval)
        except _asyncio_p22.CancelledError:
            logger.info("[P22ΩΩ_AUTOPILOT_4D_SAFE_Ω] cancelled cleanly")
        except Exception as e:
            logger.warning(f"[P22ΩΩ_AUTOPILOT_4D_SAFE_Ω] watcher crashed: {e}")

    if _os_p22.environ.get("AUTOPILOT_4D_SAFE_DISABLE", "").strip() in ("1", "true", "yes"):
        logger.info("[P22ΩΩ_AUTOPILOT_4D_SAFE_Ω] désactivé par AUTOPILOT_4D_SAFE_DISABLE=1")
    else:
        try:
            _asyncio_p22.create_task(_autopilot_4d_safe_watcher())
            logger.info(
                "[P22ΩΩ_AUTOPILOT_4D_SAFE_Ω] orchestrateur armé "
                "(first=240s · interval=30min · 3RF→QC limitrophes structural · "
                "rapports T+100%/12h/24h dans /app/memory/)"
            )
        except Exception as e:
            logger.warning(f"[P22ΩΩ_AUTOPILOT_4D_SAFE_Ω] orchestrateur scheduling failed: {e}")

    logger.info("=" * 60)
    logger.info("✓ All modules loaded successfully")
    logger.info("=" * 60)
    
    yield
    
    # Shutdown
    logger.info("Server shutting down...")
    # P22ΩΩ_DEPLOYED_WORKERS_INPROCESS_Ω — arrêt propre du watchdog et SIGTERM aux workers β2-ΣΤ
    try:
        from zerocost_workers_runtime import stop_zerocost_workers_inprocess
        await stop_zerocost_workers_inprocess()
    except Exception as e:
        logger.warning(f"[P22ΩΩ_DEPLOYED_WORKERS_INPROCESS_Ω] shutdown failed: {e}")
    # P22ΩΩ_DISK_PERSIST · 2026-05-14 · STEEVE-MAX
    # Sauvegarder le cache LRU sur disque avant l'arrêt (containers éphémères).
    try:
        from engines.v8_institutional.v20_performance_bundle import v20_shutdown as _v20_shutdown
        await _v20_shutdown()
        logger.info("✓ V20-PERFORMANCE shutdown hook fired (cache saved to disk)")
    except Exception as e:
        logger.warning(f"V20 shutdown hook from lifespan failed: {e}")
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

# MAP-PERF-Omega: GZip compression for all responses > 500 bytes
app.add_middleware(GZipMiddleware, minimum_size=500)


# ════════════════════════════════════════════════════════════════════════════
# P22ΩΩ_ZEROCOST_ENGINE_ET_TERRITOIRE_NEVER_BLANK_Ω · 2026-02-XX · STEEVE-MAX
# DOCTRINE NEVER BLANK Ω · CONTRAT D'API EN ERREUR
# ════════════════════════════════════════════════════════════════════════════
# Tout endpoint TERRITOIRE qui retourne 404 ou 500 est intercepté et remplacé
# par un JSON structuré conforme à la doctrine. Empêche TERRITOIRE de rester
# silencieusement vide ; force l'UI à afficher un état dégradé explicite.
#
# Périmètre : préfixes /api/v3, /api/v8, /api/v20, /api/v30, /api/territoire,
# /api/v1/bionic, /api/zones, /api/permis. Les autres endpoints conservent
# leur comportement HTTP standard (auth, business, etc.).
# ════════════════════════════════════════════════════════════════════════════
_NEVER_BLANK_PREFIXES = (
    "/api/v3/weather",
    "/api/v8/national",
    "/api/v8/institutional",
    "/api/v20/territoire",
    "/api/v30",
    "/api/territoire",
    "/api/v1/bionic",
    "/api/zones",
    "/api/permis",
)


@app.middleware("http")
async def territoire_never_blank_omega_middleware(request, call_next):
    """Intercepte 404/500 sur les endpoints TERRITOIRE → JSON DEGRADED structuré.

    Doctrine P22ΩΩ_NEVER_BLANK_Ω · COMMANDANT STEEVE-MAX.
    """
    from fastapi.responses import JSONResponse
    from datetime import datetime, timezone
    response = await call_next(request)
    path = request.url.path
    # Active uniquement sur le périmètre TERRITOIRE
    if not any(path.startswith(p) for p in _NEVER_BLANK_PREFIXES):
        return response
    # Active uniquement sur 404 et 500/502/503/504
    if response.status_code not in (404, 500, 502, 503, 504):
        return response
    # Garde-fou : ne pas écraser une 401/403 (auth) ni une 422 (validation)
    if response.status_code in (401, 403, 422):
        return response
    # Construire la réponse NEVER BLANK
    degraded_payload = {
        "status": "DEGRADED",
        "doctrine": "P22ΩΩ_NEVER_BLANK_Ω",
        "reason": (
            f"endpoint_unavailable_http_{response.status_code}"
            if response.status_code in (404, 500)
            else f"backend_overloaded_http_{response.status_code}"
        ),
        "path": path,
        "method": request.method,
        "http_status_original": response.status_code,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "fallback_hint": (
            "frontend_should_show_degraded_banner_and_retry_with_backoff"
        ),
    }
    return JSONResponse(
        content=degraded_payload,
        status_code=200,  # 200 OK avec status=DEGRADED dans le payload
        headers={
            "X-Territoire-Status": "DEGRADED",
            "X-Territoire-Original-Code": str(response.status_code),
            "X-Territoire-Doctrine": "P22OMEGAOMEGA_NEVER_BLANK_OMEGA",
        },
    )


# P20_PHASE3 · FORCE PURGE Ω · injecte headers no-cache sur toutes les
# responses super-masters et admin-premium. Ordre Commandant STEEVE-MAX.
@app.middleware("http")
async def bce_4x_force_purge_no_cache_middleware(request, call_next):
    response = await call_next(request)
    path = request.url.path
    if (path.startswith("/api/v30/super-masters")
            or path.startswith("/admin/bce-4x-premium")):
        response.headers["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, max-age=0")
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        response.headers["X-BCE-4X-Force-Purge"] = (
            "P20_PHASE5_CANONICAL_LOCK_2026_05_08_2330")
    return response


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

# PURGE-V6-PHASE-B: Organic Zones V2 DEPRECATED (V8 Bundle terrain-aware)
# try:
#     from modules.bionic_engine_p0.routers.organic_zones_router import router as organic_zones_router
#     app.include_router(organic_zones_router)
# except Exception as e:
#     pass

# 6b. Register Spatial Clipping router (BIONIC V6 GOLDEN INVARIANT)
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

# BCE-4X: Weather Engine v3 (enrichi, nowcasting, scoring multi-criteres)
try:
    from engines.weather_v3.router import router as weather_v3_router
    app.include_router(weather_v3_router)
    logger.info("✓ Weather Engine v3 registered (/api/v3/weather)")
except Exception as e:
    logger.warning(f"Weather Engine v3 not loaded: {e}")

# BCE-4X P0: Hunt Orchestrator Engine (vent/odeurs, acces, choix affuts, orchestration)
try:
    from engines.hunt_orchestrator.router import router as hunt_orchestrator_router
    app.include_router(hunt_orchestrator_router)
    logger.info("✓ Hunt Orchestrator Engine registered (/api/v1/hunt)")
except Exception as e:
    logger.warning(f"Hunt Orchestrator Engine not loaded: {e}")

# P22ΩΩ_PALIERS_1_4_PURGE_IMMEDIATE_Ω · 2026-05-18 · COMMANDANT STEEVE-MAX
# Routers legacy supprimés physiquement :
#   - engines.corridor_unified (déjà supprimé physiquement)
#   - engines.relocation (legacy V6 — relocalisation migrée vers Ω)
#   - engines.v8_national.map_bundle (PALIER 1 purgé)
#   - engines.v8_national.phase_b_engines (PALIER 1 purgé)
#   - modules.bionic_engine_p0.routers.movement_corridors_router (PALIER 1 purgé)
#   - core.scoring_pipeline.corridors_v10.router (HTTP désactivé,
#     mais corridors_v10 reste CORE_MODULE pour score_point_consolidated)





# BCE-4X: SUPRA Advanced Engines (pertinence, risque, recommandation, correlation)
try:
    from engines.supra_advanced.router import router as supra_advanced_router
    app.include_router(supra_advanced_router)
    logger.info("✓ SUPRA Advanced Engines registered (/api/v6/supra/advanced)")
except Exception as e:
    logger.warning(f"SUPRA Advanced Engines not loaded: {e}")


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

# 23. BCE-4X PURGE: DEM Shadow DESACTIVE (STEEVE-MAX directive)
# try:
#     from modules.bionic_engine_p0.routers.dem_shadow_router import router as dem_shadow_router
#     app.include_router(dem_shadow_router)
#     logger.info("✓ DEM Shadow registered (/api/v1/bionic/dem-shadow)")
# except Exception as e:
#     logger.warning(f"DEM Shadow not loaded: {e}")
logger.info("✗ DEM Shadow DESACTIVE — BCE-4X PURGE")

# BCE-4X PURGE COMPLETE: Weather Shadow, Weather V8.2 — Fichiers supprimes 2026-03-28
logger.info("✗ Weather Shadow PURGE — Fichier supprime")

# 25. BCE-4X PURGE: Full Shadow Comparison DESACTIVE (STEEVE-MAX directive)
# try:
#     from modules.bionic_engine_p0.routers.full_comparison_router import router as full_comparison_router
#     app.include_router(full_comparison_router)
#     logger.info("✓ Full Shadow Comparison registered (/api/v1/bionic/shadow)")
# except Exception as e:
#     logger.warning(f"Full Shadow Comparison not loaded: {e}")
logger.info("✗ Full Shadow Comparison DESACTIVE — BCE-4X PURGE")

# 26. BCE-4X PURGE: NDVI Shadow DESACTIVE (STEEVE-MAX directive)
# try:
#     from modules.bionic_engine_p0.routers.ndvi_shadow_router import router as ndvi_shadow_router
#     app.include_router(ndvi_shadow_router)
#     logger.info("✓ NDVI Shadow registered (/api/v1/bionic/ndvi-shadow)")
# except Exception as e:
#     logger.warning(f"NDVI Shadow not loaded: {e}")
logger.info("✗ NDVI Shadow DESACTIVE — BCE-4X PURGE")

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

# P22ΩΩ_PALIERS_1_4_PURGE_IMMEDIATE_Ω · 2026-05-18 · STEEVE-MAX
# movement_corridors_router supprimé physiquement (PALIER 1)

# 31. Register BIONIC Compliance Engine (BCE)
try:
    from bce.router import router as bce_router
    app.include_router(bce_router)
    logger.info("✓ BCE registered (/api/bce/validate, /api/bce/status, /api/bce/certify)")
except Exception as e:
    logger.warning(f"BCE not loaded: {e}")

logger.info("✗ Weather V8.2 PURGE — Fichier supprime — Source unique: /api/v3/weather/*")

# 33. Register Compare V8.3 Router
try:
    from modules.bionic_engine_p0.routers.compare_router import router as compare_v83_router
    app.include_router(compare_v83_router)
    logger.info("✓ Compare V8.3 registered (/api/v1/compare/waypoints)")
except Exception as e:
    logger.warning(f"Compare V8.3 not loaded: {e}")



# ═══ ×5000 NUTRITION INTELLIGENCE SUPRA — 9 moteurs (STEEVE-MAX x5000) ═══
try:
    from engines.nutrition_intelligence.router import router as nutrition_intel_router
    app.include_router(nutrition_intel_router)
    logger.info("✓ NUTRITION INTELLIGENCE SUPRA registered (/api/v6/nutrition-intelligence) — x5100-x5900")
except Exception as e:
    logger.warning(f"NUTRITION INTELLIGENCE SUPRA not loaded: {e}")

# ═══ V12-SUPRA+ · FICHE SALINE ULTIME — Router autonome P22ΩΩ ═══
# P22ΩΩ_NUTRITION_V12_SUPRA_PLUS_Ω · STEEVE-MAX · 2026-02-19
# Router autonome qui ne dépend PAS du nutrition_intelligence/__init__.py
# (actuellement cassé : module x5100_mineral_score manquant)
try:
    from engines.v8_institutional.v12_plus_router import router as v12_plus_router
    app.include_router(v12_plus_router)
    logger.info("✓ V12-SUPRA+ FICHE SALINE ULTIME registered (/api/v6/nutrition-intelligence/v12-plus) — P22ΩΩ")
except Exception as e:
    logger.warning(f"V12-SUPRA+ FICHE SALINE ULTIME not loaded: {e}")

# ═══ SALINE INTELLIGENCE ULTRA — 7 moteurs scientifiques (STEEVE-MAX x1000) ═══
try:
    from modules.saline_engine.router import router as saline_ultra_router
    app.include_router(saline_ultra_router)
    logger.info("✓ SALINE INTELLIGENCE ULTRA registered (/api/v1/saline) — 7 engines")
except Exception as e:
    logger.warning(f"SALINE INTELLIGENCE ULTRA not loaded: {e}")

# ═══ SALINE INTELLIGENCE ULTRA — E-Commerce (Stripe) ═══
try:
    from modules.saline_engine.ecommerce_router import router as saline_shop_router
    app.include_router(saline_shop_router)
    logger.info("✓ SALINE E-COMMERCE registered (/api/v1/saline/shop) — Stripe")
except Exception as e:
    logger.warning(f"SALINE E-COMMERCE not loaded: {e}")

# ═══ ALIMENTATION-V1 — Moteur alimentaire scientifique multi-especes ═══
try:
    from core.scoring_pipeline.alimentation_v1.router import router as alimentation_v1_router
    app.include_router(alimentation_v1_router)
    logger.info("✓ ALIMENTATION-V1 registered (/api/v1/alimentation)")

    from core.scoring_pipeline.alimentation_v2.router import router as alimentation_v2_router
    app.include_router(alimentation_v2_router)
    logger.info("✓ ALIMENTATION-V2 registered (/api/v2/alimentation)")

    # BCE-4X P0-X: SALINES V4 — Moteur terrain-centre SUPRA valide
    from core.scoring_pipeline.alimentation_v2.router import router_v4 as alimentation_v4_router
    app.include_router(alimentation_v4_router)
    logger.info("✓ ALIMENTATION-V4 registered (/api/v4/alimentation)")
except Exception as e:
    logger.warning(f"ALIMENTATION-V1 not loaded: {e}")

# ═══ REPOS-V1 — Moteur zones de repos scientifique multi-especes ═══
try:
    from core.scoring_pipeline.repos_v1.router import router as repos_v1_router
    app.include_router(repos_v1_router)
    logger.info("✓ REPOS-V1 registered (/api/v1/repos)")
except Exception as e:
    logger.warning(f"REPOS-V1 not loaded: {e}")

# ═══ CORRIDORS-V10 — CORE_MODULE (HTTP router désactivé, module métier interne préservé) ═══
# P22ΩΩ_PALIERS_1_4_PURGE_IMMEDIATE_Ω · 2026-05-18 · STEEVE-MAX
# corridors_v10 sanctuarisé comme CORE_MODULE (PALIER 1 protection) :
#   - HTTP API : désactivé (commenté ci-dessous)
#   - Imports cascade INTERNES préservés :
#     * bce/exclusion_layer_bce4x.py → cost_surface._load_cell_data
#     * core/scoring_pipeline/score_consolide.py → engine.score_point_consolidated
#     * engines/wildlife_behavior_omega/router.py → species_profiles.CORRIDOR_PROFILES
#     * modules/score_consolide.py → engine.score_point_consolidated
# INTERDICTION DE PURGE AUTOMATIQUE — voir /app/memory/P22OMEGAOMEGA_PURGE_LEGACY_V8_V7_PLAN.md
# try:
#     from core.scoring_pipeline.corridors_v10.router import router as corridors_v10_router
#     app.include_router(corridors_v10_router)
# except Exception as e:
#     pass


# ═══ SCORE CONSOLIDÉ V6 — SUPPRIME (DELETE-LEGACY-V6-Omega) ═══
# Remplace par SPATIAL-ENGINE-V7 /api/v7/spatial/heatmap
# Endpoints V6 /api/v1/score-consolide/* retires le 2026-04-15
logger.info("✓ SCORE-CONSOLIDE V6: SUPPRIME — remplace par SPATIAL-ENGINE-V7")


# ═══ ENGINE REGISTRY V3 — API Gateway auto-adaptative ═══
try:
    from modules.api_gateway import gateway_v3_router
    app.include_router(gateway_v3_router)
    logger.info("✓ API-GATEWAY-V3: Routeur unifié /api/v3/* enregistré")
except Exception as e:
    logger.warning(f"API-GATEWAY-V3 not loaded: {e}")


# ═══ BSAA — BIONIC Social Ads Automation (x4500-ULTRA) ═══
try:
    from modules.bsaa.router import router as bsaa_router
    app.include_router(bsaa_router)
    logger.info("✓ BSAA: BIONIC Social Ads Automation active (/api/bsaa/*)")
except Exception as e:
    logger.warning(f"BSAA not loaded: {e}")

# ═══ ACCESS CLARITY ENGINE V7 — Moteur de guidance optimale (BCE-4X) ═══
try:
    from modules.access_clarity_engine_v7.router import router as clarity_v7_router
    app.include_router(clarity_v7_router)
    logger.info("✓ ACCESS CLARITY V7 registered (/api/v7/clarity)")
except Exception as e:
    logger.warning(f"ACCESS CLARITY V7 not loaded: {e}")

# ═══ SHARE ENGINE — Module PARTAGER BCE-4X GOLDEN V6+ ═══
try:
    from modules.share_engine.router import router as share_router
    app.include_router(share_router)
    logger.info("✓ SHARE ENGINE registered (/api/share)")
except Exception as e:
    logger.warning(f"SHARE ENGINE not loaded: {e}")

# ═══ ULTRA-MAX++ FIREWALL — Geo-fencing Urbain BCE-4X Phase C ═══
try:
    from modules.ultra_max_firewall.router import router as firewall_router
    app.include_router(firewall_router)
    logger.info("✓ ULTRA-MAX++ FIREWALL registered (/api/firewall)")
except Exception as e:
    logger.warning(f"ULTRA-MAX++ FIREWALL not loaded: {e}")

# ═══ SALINES ULTIME ENGINE — FROZEN (PURGE-V6 Phase B) ═══
# PURGE-V6-PHASE-B: Salines Ultime DEPRECATED (V8 Phase A salines)
# try:
#     from modules.salines_ultime_engine.router import router as salines_ultime_router
#     app.include_router(salines_ultime_router)
# except Exception as e:
#     pass

# SOIL ENGINE — BCE-4X GOLDEN | Classification pedologique GPS
try:
    from modules.soil_engine.router import router as soil_router
    app.include_router(soil_router)
    logger.info("✓ SOIL ENGINE registered (/api/v1/soil)")
except Exception as e:
    logger.warning(f"SOIL ENGINE not loaded: {e}")

# GUIDE PRO ENGINE — BIONIC OS V8.5 | Phase E-1 | Chasse guidee 100%
try:
    from modules.guide_pro_engine.router import router as guide_pro_router
    app.include_router(guide_pro_router)
    logger.info("✓ GUIDE PRO ENGINE registered (/api/v1/guide-pro)")
except Exception as e:
    logger.warning(f"GUIDE PRO ENGINE not loaded: {e}")

# BDRE — BIONIC Data Reliability Engine | BCE-4X GOLDEN V6+ | Phase 1
try:
    from engines.bdre.router import router as bdre_router
    app.include_router(bdre_router)
    logger.info("✓ BDRE registered (/api/v1/bdre) — 8 endpoints")
except Exception as e:
    logger.warning(f"BDRE not loaded: {e}")

# SPECIES ENGINE K3 — BCE-4X ULTIME ABSOLU | STEEVE-MAX
try:
    from modules.species_engine.router import router as species_engine_router
    app.include_router(species_engine_router)
    logger.info("✓ Species Engine K3 registered (/api/v6/species-engine) — 12 endpoints")
except Exception as e:
    logger.warning(f"Species Engine K3 not loaded: {e}")

# CARTE-2027-REBUILD-Omega — Engine cartographique terrain V7
try:
    from modules.carte2027_engine.router import router as carte2027_router
    app.include_router(carte2027_router)
    logger.info("✓ Carte 2027 Engine registered (/api/v1/carte2027) — 5 endpoints")
except Exception as e:
    logger.warning(f"Carte 2027 Engine not loaded: {e}")

# NUTRITION-ENGINE-V7 — Moteur central nutritionnel institutionnel
try:
    from modules.nutrition_engine_v7.router import router as nutrition_v7_router
    app.include_router(nutrition_v7_router)
    logger.info("✓ NUTRITION-ENGINE-V7 registered (/api/v7/nutrition) — 7 endpoints")
except Exception as e:
    logger.warning(f"Nutrition Engine V7 not loaded: {e}")

# SPATIAL-ENGINE-V7 — P22ΩΩ_BLOC_2_5_CORRIDORS_UNIQUES_PAR_ESPECE_Ω · 2026-05-18 · STEEVE-MAX
# Module engines/spatial_engine_v7/ PURGÉ PHYSIQUEMENT (directive 5).
# Logique métier MIGRÉE INLINE vers engines/v8_institutional/territoire_omega_spatial/
# (avec sous-module _v7_logic.py préservant le scoring V7.2 identique).
# Endpoints exposés via /api/v20/territoire/spatial/{heatmap,score,status} (router Ω).
logger.info(
    "[P22ΩΩ.BLOC_2_5] SPATIAL-ENGINE-V7 PURGED PHYSICALLY — "
    "logique migrée vers engines/v8_institutional/territoire_omega_spatial/"
)

# SUPRA-ENGINE-V7 — Moteur decisionnel central V7
try:
    from engines.supra_engine_v7.router import router as supra_v7_router
    app.include_router(supra_v7_router)
    logger.info("✓ SUPRA-ENGINE-V7 registered (/api/v7/supra) — 6 endpoints")
except Exception as e:
    logger.warning(f"Supra Engine V7 not loaded: {e}")

# CANADA-V7.2 — Module national pancanadien
try:
    from modules.canada_v72.router import router as canada_v72_router
    app.include_router(canada_v72_router)
    logger.info("✓ CANADA-V7.2 registered (/api/v7/canada) — 6 endpoints | 13 provinces | 16 écozones")
except Exception as e:
    logger.warning(f"Canada V7.2 not loaded: {e}")

# V8-NATIONAL — Moteurs nationaux V8 pancanadiens
try:
    from engines.v8_national.router import router as v8_national_router
    app.include_router(v8_national_router)
    logger.info("✓ V8-NATIONAL registered (/api/v8/national) — 5 endpoints | 9 biomes | 6 regimes | 8 especes")
except Exception as e:
    logger.warning(f"V8 National not loaded: {e}")

# EXCLUSION-ENGINE-V8 — Moteur centralise d'exclusion BCE-4X
try:
    from engines.v8_national.exclusion_engine import router as exclusion_v8_router
    app.include_router(exclusion_v8_router)
    logger.info("✓ EXCLUSION-ENGINE-V8 registered (/api/v8/exclusion) — 22 criteres | 24 zones urbaines | 10 zones legales | 4 militaires | 4 aeroports")
except Exception as e:
    logger.warning(f"Exclusion Engine V8 not loaded: {e}")

# V8-P1 — Pipelines donnees reelles (LiDAR WCS + IRDA Pedologie)
try:
    from engines.v8_national.p1_pipelines import router as p1_router
    app.include_router(p1_router)
    logger.info("✓ V8-P1 PIPELINES registered (/api/v8/p1) — LiDAR WCS + IRDA Pedologie (STUB mode)")
except Exception as e:
    logger.warning(f"V8 P1 Pipelines not loaded: {e}")

# V8-GOVERNANCE — Master Switch Admin Premium
try:
    from engines.v8_national.governance import router as governance_router
    app.include_router(governance_router)
    logger.info("✓ V8-GOVERNANCE registered (/api/v8/governance) — Master Switch COMMANDANT_STEEVE_MAX")
except Exception as e:
    logger.warning(f"V8 Governance not loaded: {e}")

# V8-MAP-BUNDLE — P22ΩΩ_PALIERS_1_4_PURGE_IMMEDIATE_Ω · 2026-05-18 · STEEVE-MAX
# Module engines/v8_national/map_bundle.py supprimé physiquement (PALIER 1).
logger.info("[P22ΩΩ.PALIER_1] V8-MAP-BUNDLE PURGED — engines/v8_national/map_bundle.py removed")

# V8-PHASE-A — P22ΩΩ_EXTRACTION_PHASE_A_RELOCALISATION_SALINES · 2026-05-18 · STEEVE-MAX
# Logique métier MIGRÉE vers engines/v8_institutional/territoire_omega_relocalisation_salines.py
# Exposée via /api/v20/territoire/{relocalisation,salines-placement}.
# Module legacy engines/v8_national/phase_a_engines.py supprimé physiquement.
try:
    from routes.territoire_omega_reloc_salines_router import (
        router as territoire_omega_reloc_salines_router,
    )
    app.include_router(territoire_omega_reloc_salines_router)
    logger.info(
        "✓ TERRITOIRE-Ω-RELOCALISATION-SALINES registered — "
        "/api/v20/territoire/{relocalisation,salines-placement} "
        "(migrated from V8-PHASE-A)"
    )
except Exception as e:
    logger.warning(f"TERRITOIRE-Ω Relocalisation+Salines router not loaded: {e}")

# P22ΩΩ_PALIER_3_MIGRATION_V7_SPATIAL_Ω · 2026-05-18 · STEEVE-MAX
# Endpoints Ω institutionnels qui délèguent à la logique métier V7 existante.
# Frontend consommera désormais /api/v20/territoire/spatial/* au lieu de /api/v7/spatial/*.
try:
    from routes.territoire_omega_spatial_router import (
        router as territoire_omega_spatial_router,
    )
    app.include_router(territoire_omega_spatial_router)
    logger.info(
        "✓ TERRITOIRE-Ω-SPATIAL registered — "
        "/api/v20/territoire/spatial/{heatmap,score,status} "
        "(proxy pure → SPATIAL-ENGINE-V7, V30_LOCK respecté)"
    )
except Exception as e:
    logger.warning(f"TERRITOIRE-Ω Spatial router not loaded: {e}")

logger.info("[P22ΩΩ.EXTRACTION] V8-PHASE-A MIGRATED → /api/v20/territoire/{relocalisation,salines-placement}")

# P22ΩΩ_IA_HABITAT_FUSION_P0_Ω · 2026-02-20 · STEEVE-MAX
# Router institutionnel HABITAT-FUSION_P0_Ω (additif strict · Verrou Phase III maintenu).
# Endpoints :
#   - GET /api/v30/habitat-fusion/p0/status
#   - GET /api/v30/habitat-fusion/p0/axes
#   - GET /api/v30/habitat-fusion/p0/score?species=X&lat=Y&lon=Z&season=W
#   - GET /api/v30/habitat-fusion/p0/registry
# Fusion 4 axes BCE4X (2 READY · 2 PRE_INGESTION) · 5 espèces · 4 saisons.
try:
    from routes.habitat_fusion_p0_router import router as habitat_fusion_p0_router
    app.include_router(habitat_fusion_p0_router)
    logger.info(
        "✓ HABITAT-FUSION-P0-Ω registered — "
        "/api/v30/habitat-fusion/p0/{status,axes,score,registry} "
        "(P0_PRE_FUSION · 2/4 axes effectifs)"
    )
except Exception as e:
    logger.warning(f"HABITAT-FUSION-P0-Ω router not loaded: {e}")

# P22ΩΩ_APIS_CACHE_SAFE_Ω · 2026-02-20 · STEEVE-MAX
# Router status cache LRU APIs (additif strict · LECTURE SEULE).
try:
    from routes.api_cache_omega_router import router as api_cache_omega_router
    app.include_router(api_cache_omega_router)
    logger.info(
        "✓ API-CACHE-Ω registered — /api/v30/api-cache/{status,purge-expired} "
        "(LRU 7j · WorldPop/SoilGrids/Overpass)"
    )
except Exception as e:
    logger.warning(f"API-CACHE-Ω router not loaded: {e}")

# P22ΩΩ_RUNTIME_TIER_STATUS_Ω · 2026-06-06 · STEEVE-MAX
# Router diagnostic runtime (additif strict · LECTURE SEULE · Verrou Phase III).
# Expose tier détecté (PREVIEW/ELITE), cpu.max, memory.max, workers ZEROCOST,
# R2 state lag, pod uptime — utile pour différencier preview vs Elite à distance
# via curl après deploy sans accès au pod.
try:
    from routes.runtime_tier_status_router_omega import (
        router as runtime_tier_status_router,
    )
    app.include_router(runtime_tier_status_router)
    logger.info(
        "✓ RUNTIME-TIER-STATUS-Ω registered — /api/v30/runtime/tier-status "
        "(lecture seule · cgroup + workers + R2 lag)"
    )
except Exception as e:
    logger.warning(f"RUNTIME-TIER-STATUS-Ω router not loaded: {e}")

# P22ΩΩ_INGEST_TRIGGER_Ω_DRY_RUN_DEFAULT · 2026-06-07 · STEEVE-MAX
# Router déclencheur P1 ingestion (additif strict · 1 fichier nouveau).
# POST /api/v30/habitat-fusion/p1/ingest/trigger/{client}?dry_run=true (défaut)
# Validation OAuth2 / reachability / listing metadata · zéro téléchargement.
# dry_run=false autorise download_*() réel (peut lever NotImplementedError
# tant que P1_FULL implementation downstream non livrée).
# P22ΩΩ_INGESTION_P1_URL_OVERRIDE_Ω · 2026-06-07 · STEEVE-MAX
# Patch additif URLs P1 (NRCan HRDEM + MFFP) vers endpoints officiels 2026.
# Application AVANT include_router pour que les imports lazy du router voient
# les URLs patchées. Verrou Phase III intact.
try:
    from integrations.ingestion_p1_url_override_omega import apply_p1_url_overrides
    _p1_url_report = apply_p1_url_overrides()
    logger.info(
        f"✓ P1_URL_OVERRIDE applied · "
        f"{len(_p1_url_report.get('overrides_applied', []))} overrides · "
        f"{len(_p1_url_report.get('errors', []))} errors"
    )
except Exception as e:
    logger.warning(f"P1_URL_OVERRIDE skipped: {e}")

try:
    from routes.habitat_fusion_p1_ingest_router import (
        router as habitat_fusion_p1_ingest_router,
    )
    app.include_router(habitat_fusion_p1_ingest_router)
    logger.info(
        "✓ HABITAT-FUSION-P1-INGEST-Ω registered — "
        "/api/v30/habitat-fusion/p1/ingest/{trigger,clients} "
        "(dry_run=true par défaut · Verrou Phase III)"
    )
except Exception as e:
    logger.warning(f"HABITAT-FUSION-P1-INGEST-Ω router not loaded: {e}")

# P22ΩΩ_RUNTIME_DIAGNOSTIC_ELITE_Ω · 2026-06-08 · STEEVE-MAX
# Endpoint diagnostic Elite Production (whitelist secrets · lecture seule)
try:
    from routes.runtime_diagnostic_router import router as runtime_diagnostic_router
    app.include_router(runtime_diagnostic_router)
    logger.info(
        "✓ RUNTIME-DIAGNOSTIC-Ω registered — "
        "/api/v30/runtime/diagnostic-elite "
        "(Verrou Phase III · read-only · whitelist)"
    )
except Exception as e:
    logger.warning(f"RUNTIME-DIAGNOSTIC-Ω router not loaded: {e}")

# P22ΩΩ_NDVI_LIDAR_P1_STRUCTURAL+_Ω · 2026-02-20 · STEEVE-MAX
# Router institutionnel HABITAT-FUSION_P1_STRUCTURAL+_Ω (additif strict · Verrou Phase III).
# weight_active reste 0.35 (anti-générique strict) · clients ingestion code-ready inertes.
try:
    from routes.habitat_fusion_p1_router import router as habitat_fusion_p1_router
    app.include_router(habitat_fusion_p1_router)
    logger.info(
        "✓ HABITAT-FUSION-P1-STRUCTURAL+_Ω registered — "
        "/api/v30/habitat-fusion/p1/{status,clients,score} "
        "(P1_STRUCTURAL+ · 4 clients code-ready awaiting credentials)"
    )
except Exception as e:
    logger.warning(f"HABITAT-FUSION-P1-Ω router not loaded: {e}")

# V8-PHASE-B — P22ΩΩ_PALIERS_1_4_PURGE_IMMEDIATE_Ω · 2026-05-18 · STEEVE-MAX
# Module engines/v8_national/phase_b_engines.py supprimé physiquement (PALIER 1).
logger.info("[P22ΩΩ.PALIER_1] V8-PHASE-B PURGED — engines/v8_national/phase_b_engines.py removed")

# V8-PHASE-C — Scenario + Thermal + Multi-Engine Scoring
try:
    from engines.v8_national.phase_c_engines import router as phase_c_router
    app.include_router(phase_c_router)
    logger.info("V8-PHASE-C registered (/api/v8/engines) — Scenario/Thermal/Multi-Engine")
except Exception as e:
    logger.warning(f"V8 Phase C not loaded: {e}")

# V8-INSTITUTIONAL — 24 Engines + 4 Piliers (DOCUMENT MAITRE ULTIME MAX)
try:
    from engines.v8_institutional.piliers_router import router as institutional_router
    app.include_router(institutional_router)
    logger.info("V8-INSTITUTIONAL registered (/api/v8/institutional) — 24 Engines + 4 Piliers")
except Exception as e:
    logger.warning(f"V8 Institutional not loaded: {e}")

# V20 PERFORMANCE BUNDLE — cache TTL 24h (<1s loading target)
try:
    from engines.v8_institutional.v20_performance_bundle import (
        router as v20_perf_router,
        audit_router as v20_audit_router,
        v20_startup, v20_shutdown,
    )
    # P22ΩΩ_PHASE3_WEATHERCACHE_BETA2_B_E_PRECEDENT_16W_Ω · STEEVE-MAX
    # Route override anti-502 ENREGISTRÉE AVANT v20_perf_router pour priorité matching.
    try:
        from middleware.anti_502_zerocost_omega import register_anti_502
        register_anti_502(app)
        logger.info("[P22ΩΩ_ANTI_502] route override enregistrée AVANT v20_perf_router · NEVER BLANK Ω")
    except Exception as _e:
        logger.warning(f"Anti-502 route override non-installable: {_e}")
    app.include_router(v20_perf_router)
    app.include_router(v20_audit_router)
    logger.info("[P22Ω.V5_COMPLIANCE_LIVE_Ω] audit endpoint registered (/api/v20/audit/v5-compliance-live)")

    @app.on_event("startup")
    async def _v20_startup_hook():
        logger.info("[V20-STARTUP-HOOK] Firing — calling v20_startup()")
        try:
            await v20_startup()
            logger.info("[V20-STARTUP-HOOK] v20_startup() completed")
        except Exception as e:
            logger.warning(f"V20 startup hook failed: {e}", exc_info=True)

    @app.on_event("shutdown")
    async def _v20_shutdown_hook():
        try:
            await v20_shutdown()
        except Exception as e:
            logger.warning(f"V20 shutdown hook failed: {e}")

    logger.info("V20-PERFORMANCE registered (/api/v20/territoire/bundle) — cache 10K TTL 24h + disk persist + prechauffage")
except Exception as e:
    logger.warning(f"V20 Performance bundle not loaded: {e}")

# P22ΩΩ_CLEANUP_3D_MVT_EDGE · 2026-05-18 · COMMANDANT STEEVE-MAX
# Block V20-MVT-TILES SUPPRIMÉ — module v20_mvt_tiles.py retiré (doctrine 1-worker
# minimaliste, zéro consommation frontend confirmée par grep exhaustif).

# SELF-AUDIT-Omega — validation institutionnelle TERRITOIRE-V12 au demarrage
try:
    from engines.v8_institutional.self_audit_omega import router as self_audit_router, v20_self_audit_on_startup
    app.include_router(self_audit_router)

    @app.on_event("startup")
    async def _self_audit_startup_hook():
        import asyncio as _asyncio
        _asyncio.create_task(v20_self_audit_on_startup())

    logger.info("SELF-AUDIT-Omega registered (/api/v20/territoire/self-audit) — audit startup async")
except Exception as e:
    logger.warning(f"SELF-AUDIT-Omega not loaded: {e}")

# SLA-BASELINE-Ω — baseline institutionnelle + PERF-GUARD-Ω
try:
    from engines.v8_institutional.sla_baseline_omega import router as sla_baseline_router
    app.include_router(sla_baseline_router)
    logger.info("SLA-BASELINE-Omega registered (/api/v20/territoire/sla-baseline) — PERF-GUARD hybride")
except Exception as e:
    logger.warning(f"SLA-BASELINE-Omega not loaded: {e}")

# ENGINES-CATALOG — governance registry endpoint
try:
    from engines.v8_institutional.engines_catalog import router as engines_catalog_router
    app.include_router(engines_catalog_router)
    logger.info("ENGINES-CATALOG registered (/api/v20/territoire/engines-catalog) — SCIENCE-Ω registry")
except Exception as e:
    logger.warning(f"ENGINES-CATALOG not loaded: {e}")

# REGISTRY-LOCK-Ω — Phase XI scellé 22 engines SUPRA-Ω + hash Document Maître
try:
    from engines.v8_institutional.registry_lock_omega import router as registry_lock_router
    app.include_router(registry_lock_router)
    logger.info("REGISTRY-LOCK-Ω registered (/api/v20/territoire/registry-lock, /document-maitre-lock) — Phase XI sealed")
except Exception as e:
    logger.warning(f"REGISTRY-LOCK-Ω not loaded: {e}")

# CALIBRATION-DYNAMIQUE-Ω — Phase X ingestion observations + recalibration
try:
    from engines.v8_institutional.engine_calibration_dynamique_omega import router as calib_dyn_router
    app.include_router(calib_dyn_router)
    logger.info("CALIBRATION-DYNAMIQUE-Ω registered (/observations, /calibration-dynamique)")
except Exception as e:
    logger.warning(f"CALIBRATION-DYNAMIQUE-Ω not loaded: {e}")

# SCIENCE-GAPS-DATASETS-Ω — Phase X ingestion 4 gaps MFFP/IRDA/CWD
try:
    from engines.v8_institutional.science_gaps_datasets import router as gaps_router
    app.include_router(gaps_router)
    logger.info("SCIENCE-GAPS-DATASETS-Ω registered (/science-gaps) — 4 gaps ingested")
except Exception as e:
    logger.warning(f"SCIENCE-GAPS-DATASETS-Ω not loaded: {e}")

# ENGINE-CANADA-Ω — Phase X-B souveraineté pancanadienne
try:
    from engines.v8_institutional.engine_canada_omega import router as canada_router
    app.include_router(canada_router)
    logger.info("ENGINE-CANADA-Ω registered (/canada, /canada/province/{code}) — 13 provinces")
except Exception as e:
    logger.warning(f"ENGINE-CANADA-Ω not loaded: {e}")

# FEDERAL-DATASETS-Ω — Phase X-C LEP + HYDAT seeds
try:
    from engines.v8_institutional.federal_datasets_omega import router as federal_router
    app.include_router(federal_router)
    logger.info("FEDERAL-DATASETS-Ω registered (/federal/lep, /federal/hydat) — seed LEP+HYDAT")
except Exception as e:
    logger.warning(f"FEDERAL-DATASETS-Ω not loaded: {e}")

# ENGINE-RISQUES-HYDRO-Ω — Phase X-C risques hydrologiques
try:
    from engines.v8_institutional.engine_risques_hydro_omega import router as risques_hydro_router
    app.include_router(risques_hydro_router)
    logger.info("ENGINE-RISQUES-HYDRO-Ω registered (/risques-hydro)")
except Exception as e:
    logger.warning(f"ENGINE-RISQUES-HYDRO-Ω not loaded: {e}")

# SLA-BASELINE-30J-Ω — Phase X-D graphe 30 jours
try:
    from engines.v8_institutional.sla_baseline_30j_omega import router as sla_30j_router
    app.include_router(sla_30j_router)
    logger.info("SLA-BASELINE-30J-Ω registered (/sla-baseline-30j)")
except Exception as e:
    logger.warning(f"SLA-BASELINE-30J-Ω not loaded: {e}")

# SELF-AUDIT-ALERTS-Ω — Phase X-D WebSocket + REST
try:
    from engines.v8_institutional.self_audit_alerts_omega import (
        router as alerts_ws_router, rest_router as alerts_rest_router,
    )
    app.include_router(alerts_ws_router)
    app.include_router(alerts_rest_router)
    logger.info("SELF-AUDIT-ALERTS-Ω registered (/ws/self-audit-alert, /self-audit-alert/*)")
except Exception as e:
    logger.warning(f"SELF-AUDIT-ALERTS-Ω not loaded: {e}")

# EXPORT-INSTITUTIONNEL-V20-Ω — Phase X-D PDF signé
try:
    from engines.v8_institutional.export_institutionnel_v20_omega import router as export_v20_router
    app.include_router(export_v20_router)
    logger.info("EXPORT-INSTITUTIONNEL-V20-Ω registered (/export/institutionnel/v20)")
except Exception as e:
    logger.warning(f"EXPORT-INSTITUTIONNEL-V20-Ω not loaded: {e}")

# ENGINE-RENDER-Ω — Phase XI-SUPRA rendu territoire institutionnel
try:
    from engines.v8_institutional.engine_render_omega import router as render_omega_router
    app.include_router(render_omega_router)
    logger.info("ENGINE-RENDER-Ω registered (/render-config, /render-validate) — 14 couches")
except Exception as e:
    logger.warning(f"ENGINE-RENDER-Ω not loaded: {e}")

# VISUAL-PROOF-Ω — Phase XI-SUPRA-B preuve visuelle institutionnelle
try:
    from engines.v8_institutional.visual_proof_omega import router as visual_proof_router
    app.include_router(visual_proof_router)
    logger.info("VISUAL-PROOF-Ω registered (/visual-proof/generate, /visual-proof/index)")
except Exception as e:
    logger.warning(f"VISUAL-PROOF-Ω not loaded: {e}")

# VISUAL-PROOF-LIVE-Ω — Phase XI-SUPRA-C capture Playwright DOM Leaflet
try:
    from engines.v8_institutional.visual_proof_live_omega import router as visual_proof_live_router
    app.include_router(visual_proof_live_router)
    logger.info("VISUAL-PROOF-LIVE-Ω registered (/visual-proof-live/generate, /index)")
except Exception as e:
    logger.warning(f"VISUAL-PROOF-LIVE-Ω not loaded: {e}")

# ENGINE-TERRITOIRE-ANTI-REGRESSION-Ω — Phase XI-SUPRA-G (ORDRE_TERRITOIRE_PROTECT_Ω)
try:
    from engines.v8_institutional.engine_territoire_anti_regression_omega import router as antireg_router
    app.include_router(antireg_router)
    logger.info("ENGINE-TERRITOIRE-ANTI-REGRESSION-Ω registered (/api/v20/territoire/anti-regression)")
except Exception as e:
    logger.warning(f"ENGINE-TERRITOIRE-ANTI-REGRESSION-Ω not loaded: {e}")

# ENGINE-IA-CORRIDORS-Ω — Phase XI-SUPRA-H (ENGINE CORRIDORS VERSION Ω)
try:
    from engines.v8_institutional.engine_ia_corridors_omega import router as ia_corridors_router
    app.include_router(ia_corridors_router)
    logger.info("ENGINE-IA-CORRIDORS-Ω registered (/api/v20/territoire/ia-corridors)")
except Exception as e:
    logger.warning(f"ENGINE-IA-CORRIDORS-Ω not loaded: {e}")

# POST-SMOOTHER X180 — lissage biologique externe (hors V30)
# Enregistré AVANT l'engine V30 pour intercepter /generate (priorité FastAPI first-match)
try:
    from engines.post_smoothing.organic_corridor_smoother import router as corridor_smoother_router
    app.include_router(corridor_smoother_router)
    logger.info("✓ ORGANIC_SMOOTHER_Ω_X180 active (intercepts /api/v20/territoire/corridors-organic/generate)")
except Exception as e:
    logger.warning(f"ORGANIC_SMOOTHER_Ω_X180 not loaded: {e}")

# ENGINE-IA-CORRIDORS-ORGANIC-Ω — Phase XI-SUPRA-M (CORRIDORS ORGANIC VERSION Ω-M)
try:
    from engines.v8_institutional.engine_ia_corridors_organic_omega import router as organic_corridors_router
    app.include_router(organic_corridors_router)
    logger.info("ENGINE-IA-CORRIDORS-ORGANIC-Ω registered (/api/v20/territoire/corridors-organic)")
except Exception as e:
    logger.warning(f"ENGINE-IA-CORRIDORS-ORGANIC-Ω not loaded: {e}")

# CORRIDORS_ANOMALY_OMEGA_X100 — P22G_REFINEMENT_X100_Ω (anomaly map + métriques)
try:
    from engines.post_smoothing.corridors_anomaly_omega import router as corridors_anomaly_router
    app.include_router(corridors_anomaly_router)
    logger.info("CORRIDORS_ANOMALY_OMEGA_X100 registered (/api/v20/territoire/corridors-organic/anomaly-map)")
except Exception as e:
    logger.warning(f"CORRIDORS_ANOMALY_OMEGA_X100 not loaded: {e}")

# LOCAL_DENSITY_PROFILE_OMEGA — P22Λ_LOCAL_MAX_DENSITY_CORRIDOR_EXPANSION_Ω
try:
    from engines.post_smoothing.local_density_profile_omega import router as local_density_router
    app.include_router(local_density_router)
    logger.info("LOCAL_DENSITY_PROFILE_OMEGA_X100 registered (/api/v20/territoire/corridors-organic/local-density-profile)")
except Exception as e:
    logger.warning(f"LOCAL_DENSITY_PROFILE_OMEGA_X100 not loaded: {e}")

# ENGINE_SPECTRAL_Ω — NEW_ENGINE_1_SPECTRAL_Ω · VERSION_ULTIME_ABSOLUE_X3 (2026-05-10 · STEEVE-MAX)
# NDVI/NDWI/EVI Sentinel-2 + LST Landsat 8/9 + STAC ingestion (anti-générique strict)
try:
    from engines.spectral_omega.router import router as spectral_omega_router
    app.include_router(spectral_omega_router)
    logger.info("ENGINE_SPECTRAL_Ω registered (/api/v20/spectral) — NEW_ENGINE_1 ANTI-GÉNÉRIQUE")
except Exception as e:
    logger.warning(f"ENGINE_SPECTRAL_Ω not loaded: {e}")

# ENGINE_GIS_Ω · ORDRE N°50 PHASE 1 · GIS RÉEL · P22N ABSORBÉ (2026-05-10 · STEEVE-MAX)
# FORET_MFFP, SOL_IRDA, ROUTES_MTQ, ZEC_SEPAQ, LIMITES, PRESSION_HUMAINE
try:
    from engines.gis_omega.router import router as gis_omega_router
    app.include_router(gis_omega_router)
    logger.info("ENGINE_GIS_Ω registered (/api/v20/gis) — ORDRE_N50_PHASE_1")
except Exception as e:
    logger.warning(f"ENGINE_GIS_Ω not loaded: {e}")

# ENGINE_TERRAIN_HR_Ω · ORDRE N°50 PHASE 2 · TERRAIN HR (2026-05-10 · STEEVE-MAX)
# DEM 30m public + dérivés (slope, aspect, roughness, cost_surface)
try:
    from engines.terrain_hr_omega.router import router as terrain_hr_router
    app.include_router(terrain_hr_router)
    logger.info("ENGINE_TERRAIN_HR_Ω registered (/api/v20/terrain-hr) — ORDRE_N50_PHASE_2")
except Exception as e:
    logger.warning(f"ENGINE_TERRAIN_HR_Ω not loaded: {e}")

# CHAINE_Ω_CASCADE · Orchestrateur SPECTRAL → TERRAIN_HR → GIS → CORRIDORS → TERRITOIRE
try:
    from engines.chain_omega_cascade import router as chain_omega_cascade_router
    app.include_router(chain_omega_cascade_router)
    logger.info("CHAINE_Ω_CASCADE registered (/api/v20/chain-omega) — PHASE_1+2 ORCHESTRATOR")
except Exception as e:
    logger.warning(f"CHAINE_Ω_CASCADE not loaded: {e}")

# P22ΩΩ_CLEANUP_3D_MVT_EDGE · 2026-05-18 · COMMANDANT STEEVE-MAX
# Block ENGINE_MESH_3D_Ω SUPPRIMÉ — engines/mesh_3d_omega/ retiré (doctrine
# 1-worker minimaliste, Cesium 3D Viewer abandonné).

# ENGINE_SUPER_RESOLUTION_Ω · NEW_ENGINE_4 (2026-05-10 · STEEVE-MAX)
# Lanczos x4 + scaffold Real-ESRGAN compatible
try:
    from engines.super_resolution_omega.router import router as super_res_router
    app.include_router(super_res_router)
    logger.info("ENGINE_SUPER_RESOLUTION_Ω registered (/api/v20/super-resolution) — NEW_ENGINE_4")
except Exception as e:
    logger.warning(f"ENGINE_SUPER_RESOLUTION_Ω not loaded: {e}")

# P22ΩΩ_CLEANUP_3D_MVT_EDGE · 2026-05-18 · COMMANDANT STEEVE-MAX
# Block V20_3D_OVERLAYS_Ω SUPPRIMÉ — module v20_3d_overlays_omega.py retiré
# (alimentait CesiumTerritoireViewer, lui-même supprimé en frontend).

# AUDIT_SUPRA_CORRIDORS_Ω · Rapport HTTPS téléchargeable (2026-05-11 · STEEVE-MAX)
# Sert /app/memory/AUDIT_SUPRA_CORRIDORS_V90.md sans auth · sans compression
try:
    from engines.v8_institutional.audit_supra_corridors_omega import router as audit_supra_router
    app.include_router(audit_supra_router)
    logger.info("AUDIT_SUPRA_CORRIDORS_Ω registered — /api/v20/audit/corridors-supra-report.{md,txt,json}")
except Exception as e:
    logger.warning(f"AUDIT_SUPRA_CORRIDORS_Ω not loaded: {e}")

# DOCTRINE_V90_Ω · Attestation P22Ω_CORRIDORS_RESTORE_V90 (2026-05-11 · STEEVE-MAX)
# Atteste de la conformité V90 (continuité ABSOLUTE, intensity FULL, affut IGNORE)
try:
    from engines.v8_institutional.doctrine_v90_omega import router as doctrine_v90_router
    app.include_router(doctrine_v90_router)
    logger.info("DOCTRINE_V90_Ω registered — /api/v20/doctrine-v90/{status,attest} · P22Ω_CORRIDORS_RESTORE_V90")
except Exception as e:
    logger.warning(f"DOCTRINE_V90_Ω not loaded: {e}")

# CASCADE_CACHE_Ω · P22J LATENCE OPTIM (TTL 30 min)
try:
    from fastapi import APIRouter as _APIRouter_cache
    from engines.cascade_cache_omega import get_cascade_cache
    _cache_router = _APIRouter_cache(prefix="/api/v20/cascade-cache", tags=["CASCADE_CACHE_Ω"])

    @_cache_router.get("/stats")
    async def _cache_stats():
        return get_cascade_cache().stats()

    @_cache_router.post("/clear")
    async def _cache_clear():
        n = get_cascade_cache().clear()
        return {"cleared": n}

    app.include_router(_cache_router)
    logger.info("CASCADE_CACHE_Ω registered (/api/v20/cascade-cache) — P22J_LATENCE TTL 30min")
except Exception as e:
    logger.warning(f"CASCADE_CACHE_Ω not loaded: {e}")

# ENGINE-RENDU-Ω — Phase XI-SUPRA-K (rendu institutionnel corridors)
try:
    from engines.v8_institutional.engine_rendu_omega import router as rendu_omega_router, visual_router as rendu_visual_router
    app.include_router(rendu_omega_router)
    app.include_router(rendu_visual_router)
    logger.info("ENGINE-RENDU-Ω registered (/api/v20/territoire/rendu-omega + /corridors-omega/visual-self-test)")
except Exception as e:
    logger.warning(f"ENGINE-RENDU-Ω not loaded: {e}")

# ENGINE-SPECIES-PROFILES-Ω — Phase XI-SUPRA-K (registre dynamique espèces)
try:
    from engines.v8_institutional.engine_species_profiles_omega import router as species_profiles_router
    app.include_router(species_profiles_router)
    logger.info("ENGINE-SPECIES-PROFILES-Ω registered (/api/v20/territoire/species-profiles)")
except Exception as e:
    logger.warning(f"ENGINE-SPECIES-PROFILES-Ω not loaded: {e}")

# ENGINE-IA-VISION-REGISTRY-Ω — Phase XI-SUPRA-K (registre IA Vision)
try:
    from engines.v8_institutional.engine_ia_vision_registry_omega import router as ia_vision_reg_router
    app.include_router(ia_vision_reg_router)
    logger.info("ENGINE-IA-VISION-REGISTRY-Ω registered (/api/v20/territoire/ia-vision)")
except Exception as e:
    logger.warning(f"ENGINE-IA-VISION-REGISTRY-Ω not loaded: {e}")

# LEP-INGESTION-Ω — Phase XI-SUPRA-D (BIONIC INGESTION-FGDB+GEOJSON-Ω-V1.0)
# EXCLUDE_LAYER LEP_CRITICAL_HABITAT_NATIONAL — Directive STEEVE-MAX 2026-04-20
# STATUS OFFICIAL — router désactivé, module source conservé pour réactivation future.
# try:
#     from engines.v8_institutional.lep_ingestion_omega import router as lep_ingest_router
#     app.include_router(lep_ingest_router)
#     logger.info("LEP-INGESTION-Ω registered (/api/v20/territoire/lep)")
# except Exception as e:
#     logger.warning(f"LEP-INGESTION-Ω not loaded: {e}")

# ═══════════════════════════════════════════════════════════════════════════
# P22Ω_TERRITOIRE_UI_INJONCTION_Ω · 2026-05-13 · STEEVE-MAX
# ═══════════════════════════════════════════════════════════════════════════
# Endpoint stub pour /api/v20/territoire/lep/status (router LEP désactivé
# par directive 2026-04-20). Le frontend `InstitutionalHealthPanel.jsx`
# appelle cet endpoint et recevait HTTP 404 silencieux. Doctrine :
# retourner HTTP 200 avec status="DISABLED" pour aligner UI ↔ backend
# sans réactiver le router LEP (qui reste exclu doctrinalement).
@app.get("/api/v20/territoire/lep/status")
async def lep_status_stub_doctrinal():
    return {
        "status": "DISABLED",
        "reason": "EXCLUDE_LAYER LEP_CRITICAL_HABITAT_NATIONAL",
        "directive": "STEEVE-MAX 2026-04-20",
        "phase": "XI-SUPRA-D",
        "router_active": False,
        "module_preserved": True,
        "ingestion": {"ingested": False, "last_ingest_utc": None},
        "doctrine": "P22Ω_TERRITOIRE_UI_INJONCTION_Ω",
    }

# MONITORING-Ω + ALERTE-ANOMALIES-Ω
try:
    from engines.v8_institutional.monitoring_alerte_omega import router as monitoring_router
    app.include_router(monitoring_router)
    logger.info("MONITORING-Ω + ALERTE-ANOMALIES-Ω registered (/monitoring, /alertes)")
except Exception as e:
    logger.warning(f"MONITORING-Ω not loaded: {e}")

# ENGINE-GOUVERNANCE-Ω — fusion gouvernance unifiee
try:
    from engines.v8_institutional.engine_gouvernance_omega import router as gouv_router
    app.include_router(gouv_router)
    logger.info("ENGINE-GOUVERNANCE-Ω registered (/gouvernance)")
except Exception as e:
    logger.warning(f"GOUVERNANCE-Ω not loaded: {e}")

# ESI-Omega — Engine Securite Institutionnelle (Guardian Central)
try:
    from engines.v8_institutional.esi_omega import router as esi_router
    app.include_router(esi_router)
    logger.info("ESI-Omega registered (/api/v8/esi) — Guardian Central V8-PURE")
except Exception as e:
    logger.warning(f"ESI-Omega not loaded: {e}")

# SUPRA V8 — Integration TERRITOIRE → SUPRA (institutionnel)
try:
    from engines.v8_institutional.supra_v8 import router as supra_v8_router
    app.include_router(supra_v8_router)
    logger.info("SUPRA-V8 registered (/api/v8/supra) — Integration Institutionnelle")
except Exception as e:
    logger.warning(f"SUPRA V8 not loaded: {e}")

# V13-AUDIT — Public report endpoint
try:
    from routes.audit_report_route import router as audit_report_router
    app.include_router(audit_report_router)
except Exception as e:
    logger.warning(f"Audit report route not loaded: {e}")

# PHASE_ZERO_PLUS_X30 — CI_STATUS_Ω dashboard (lecture seule)
try:
    from routes.ci_status_omega import router as ci_status_omega_router
    app.include_router(ci_status_omega_router)
    logger.info("✓ CI_STATUS_Ω dashboard active (/api/omega/ci-status)")
except Exception as e:
    logger.warning(f"CI_STATUS_Ω route not loaded: {e}")

# PHASE_XI_SUPRA_RAPATRIEMENT_TERRITOIRE_V7_ULTIME_Ω — X195 export HTTPS
try:
    from routes.v7_ultime_export_router import router as v7_ultime_export_router
    app.include_router(v7_ultime_export_router)
    logger.info("✓ V7_ULTIME_EXPORT_X195 active (/api/v7-ultime-export/*)")
except Exception as e:
    logger.warning(f"V7_ULTIME_EXPORT router not loaded: {e}")

# PHASE_XI_SUPRA_ENGINES_OPTIMISATION_Ω — X198 DIFF_MATRIX lecture seule PRO/EXPERT
try:
    from routes.diff_matrix_router import router as diff_matrix_router
    app.include_router(diff_matrix_router)
    logger.info("✓ DIFF_MATRIX_X198_READONLY active (/api/v7-vs-actuel/diff-matrix*)")
except Exception as e:
    logger.warning(f"DIFF_MATRIX router not loaded: {e}")

# CATALOGUE_ENGINES_BIONIC — téléchargement HTTPS public
try:
    from routes.catalogue_engines_router import router as catalogue_engines_router
    app.include_router(catalogue_engines_router)
    logger.info("✓ CATALOGUE_ENGINES_BIONIC active (/api/catalogue-engines/*)")
except Exception as e:
    logger.warning(f"CATALOGUE_ENGINES router not loaded: {e}")

# ═══ X200 P0 ACTIVATION — V31_CORE_PREPARATOIRE_Ω ═══
# Ordre COMMANDANT STEEVE-MAX : activation des 5 engines P0
# (wildlife_behavior, eco_zones, hydro_topo + support reseau_veineux, bio_scoring)
for _slug, _label in [
    ("wildlife_behavior_omega", "ENGINE_WILDLIFE_BEHAVIOR_Ω (P0 #1 — CERF restauré)"),
    ("eco_zones_omega",         "ENGINE_ECO_ZONES_Ω (P0 #2 — 20 salines hiérarchisées)"),
    ("hydro_topo_omega",        "ENGINE_HYDRO_TOPO_Ω (P0 #3 — inversion hydro corrigée)"),
    ("reseau_veineux_omega",    "ENGINE_RÉSEAU_VEINEUX_Ω (support — 5 niveaux V7)"),
    ("bio_scoring_omega",       "ENGINE_BIO_SCORING_Ω (support — scoring 8-facteurs V7)"),
]:
    try:
        _mod = __import__(f"engines.{_slug}", fromlist=["router"])
        app.include_router(_mod.router)
        logger.info(f"✓ X200-P0 active : {_label}")
    except Exception as e:
        logger.warning(f"X200-P0 {_slug} not loaded: {e}")

# ═══ X200-P1-PREVIEW — Corridor pipeline preview (lecture seule) ═══
try:
    from routes.corridor_pipeline_preview_router import router as pipeline_preview_router
    app.include_router(pipeline_preview_router)
    logger.info("✓ X200-P1-PREVIEW active (/api/v7-ultime/corridor-pipeline-preview/*)")
except Exception as e:
    logger.warning(f"Pipeline preview router not loaded: {e}")

# ═══ PHASE X199 ACTIVATION — 4 engines étendus (ordre institutionnel, terrain_3d retiré) ═══
# P22ΩΩ_CLEANUP_3D_MVT_EDGE · 2026-05-18 · STEEVE-MAX
# ENGINE_3D_TERRAIN_Ω (X199 #3) SUPPRIMÉ — engines/terrain_3d_omega/ retiré.
for _slug, _label in [
    ("ecoforestry_omega",         "ENGINE_ECOFORESTRY_Ω (X199 #1 — racine)"),
    ("advanced_geospatial_omega", "ENGINE_ADVANCED_GEOSPATIAL_Ω (X199 #2)"),
    ("legal_time_omega",          "ENGINE_LEGAL_TIME_Ω (X199 #4 — racine)"),
    ("predictive_omega",          "ENGINE_PREDICTIVE_Ω (X199 #5 — dépendant de 1-4)"),
]:
    try:
        _mod = __import__(f"engines.{_slug}.router", fromlist=["router"])
        app.include_router(_mod.router)
        logger.info(f"✓ X199 active : {_label}")
    except Exception as e:
        logger.warning(f"X199 {_slug} not loaded: {e}")

# ═══ PHASE X200-P5 — ENGINE RENDUΩ (validation ultime + blocage rendu) ═══
try:
    from routes.renduomega_router import router as renduomega_router
    app.include_router(renduomega_router)
    logger.info("✓ X200-P5 active : ENGINE_RENDUΩ (/api/v7-ultime/renduomega/*)")
except Exception as e:
    logger.warning(f"X200-P5 RENDUΩ router not loaded: {e}")

# ═══ PHASE X200-P6 — ANTI_REGRESSION_Ω (observation continue 12 sous-normes X150) ═══
try:
    from routes.anti_regression_omega_router import router as anti_regression_router
    app.include_router(anti_regression_router)
    logger.info("✓ X200-P6 active : ANTI_REGRESSION_Ω (/api/v7-ultime/anti-regression/*)")
except Exception as e:
    logger.warning(f"X200-P6 ANTI_REGRESSION_Ω router not loaded: {e}")

# ═══ PHASE XII-SUPRA — DIAGNOSTIC V30 CORRIDORS STATUS Ω (lecture seule) ═══
try:
    from routes.v30_corridors_status_router import router as v30_corridors_status_router
    app.include_router(v30_corridors_status_router)
    logger.info("✓ XII-SUPRA active : V30_CORRIDORS_STATUS_Ω (/api/v30/corridors/*)")
except Exception as e:
    logger.warning(f"XII-SUPRA V30_CORRIDORS_STATUS_Ω router not loaded: {e}")

# ═══ PHASE XII-SUPRA — CACHE DIAGNOSTIC Ω (lecture seule, ENFORCEMENT_P0) ═══
try:
    from routes.cache_diagnostic_router import router as cache_diagnostic_router
    app.include_router(cache_diagnostic_router)
    logger.info("✓ XII-SUPRA active : CACHE_DIAGNOSTIC_Ω (/api/v30/corridors/cache-diagnostic)")
except Exception as e:
    logger.warning(f"XII-SUPRA CACHE_DIAGNOSTIC_Ω router not loaded: {e}")

# ═══ PHASE XVII-SUPRA — ECOLOGICAL ORCHESTRATOR Ω ═══
try:
    from routes.ecological_orchestrator_router import router as ecological_orchestrator_router
    app.include_router(ecological_orchestrator_router)
    logger.info("✓ XVII-SUPRA active : ECOLOGICAL_ORCHESTRATOR_Ω (/api/v30/corridors/ecological-orchestrator)")
except Exception as e:
    logger.warning(f"XVII-SUPRA ECOLOGICAL_ORCHESTRATOR_Ω router not loaded: {e}")

# ═══ PHASE XVIII — ENGINE PREDICTIVE_OMEGA V2 GPS USGS Ω ═══
try:
    from routes.predictive_omega_v2_router import router as predictive_omega_v2_router
    app.include_router(predictive_omega_v2_router)
    logger.info("✓ XVIII active : PREDICTIVE_OMEGA_V2_Ω (/api/v30/predictive/omega-v2)")
except Exception as e:
    logger.warning(f"XVIII PREDICTIVE_OMEGA_V2_Ω router not loaded: {e}")

# ═══ PHASE XVIII — ENGINE CORRIDORS VITAUX Ω ═══
try:
    from routes.corridors_vitaux_router import router as corridors_vitaux_router
    app.include_router(corridors_vitaux_router)
    logger.info("✓ XVIII active : CORRIDORS_VITAUX_Ω (/api/v30/corridors/vitaux-omega)")
except Exception as e:
    logger.warning(f"XVIII CORRIDORS_VITAUX_Ω router not loaded: {e}")

# ═══ PHASE XIX-P1 — ORIGINE_EXTERNE_FILTER_Ω · DÉSACTIVÉ P22Ω_V90 ═══
# Désactivé par P22Ω_CORRIDORS_RESTORE_V90 · P0_CRITICAL · 2026-05-11
# Motif : rejette silencieusement les corridors hors fenêtre [600m, 780m]
# → incompatible avec doctrine V90 (continuité ABSOLUE, full_trame_visibility)
# try:
#     from routes.origine_externe_filter_router import router as origine_externe_filter_router
#     app.include_router(origine_externe_filter_router)
#     logger.info("✓ XIX-P1 active : ORIGINE_EXTERNE_FILTER_Ω (/api/v30/corridors/origine-externe)")
# except Exception as e:
#     logger.warning(f"XIX-P1 ORIGINE_EXTERNE_FILTER_Ω router not loaded: {e}")
logger.info("[P22Ω_V90] ORIGINE_EXTERNE_FILTER_Ω DISABLED — directive P22Ω_CORRIDORS_RESTORE_V90 P0")

# ═══ PHASE XIX-P2 — ORIGINE_EXTERNE_INVERSION_Ω ═══
try:
    from routes.origine_externe_inversion_router import router as origine_externe_inversion_router
    app.include_router(origine_externe_inversion_router)
    logger.info("✓ XIX-P2 active : ORIGINE_EXTERNE_INVERSION_Ω (/api/v30/corridors/origine-inversion)")
except Exception as e:
    logger.warning(f"XIX-P2 ORIGINE_EXTERNE_INVERSION_Ω router not loaded: {e}")

# ═══ PHASE XVIII-BIO — SPECIES_PRESENCE_MASK_Ω ═══
try:
    from routes.species_presence_mask_router import router as species_presence_mask_router
    app.include_router(species_presence_mask_router)
    logger.info("✓ XVIII-BIO active : SPECIES_PRESENCE_MASK_Ω (/api/v30/corridors/presence-mask)")
except Exception as e:
    logger.warning(f"XVIII-BIO SPECIES_PRESENCE_MASK_Ω router not loaded: {e}")

# ═══ PHASE-E — FUSION_TERRITOIRE_Ω (PRÉ-FUSION · LECTURE SEULE · AVAL V30) ═══
try:
    from routes.fusion_territoire_omega_router import router as fusion_territoire_router
    app.include_router(fusion_territoire_router)
    logger.info("✓ PHASE-E active : FUSION_TERRITOIRE_Ω (/api/v30/territoire/ultime-score)")
except Exception as e:
    logger.warning(f"PHASE-E FUSION_TERRITOIRE_Ω router not loaded: {e}")

# ═══ P22Ω_INJONCTION_DOCTRINAL_DOWNLOAD · 2026-05-13 · STEEVE-MAX ═══
# Endpoint READ-ONLY pour télécharger les rapports d'audit doctrinal
# via le préview HTTPS public (REACT_APP_BACKEND_URL).
try:
    from routes.audit_download_router import router as audit_download_router
    app.include_router(audit_download_router)
    logger.info("✓ P22Ω_INJONCTION_DOCTRINAL_DOWNLOAD active : /api/v20/territoire/audit/files")
except Exception as e:
    logger.warning(f"P22Ω_INJONCTION_DOCTRINAL_DOWNLOAD router not loaded: {e}")

# ═══ P22ΩΩ_TERRITOIRE_STRUCTURE_EXPORT (Commandant STEEVE-MAX · 2026-05-17) ═══
# Endpoint téléchargeable du JSON maître structure TERRITOIRE Ω.
try:
    from routes.territoire_structure_export_router import router as territoire_structure_export_router
    app.include_router(territoire_structure_export_router)
    logger.info("✓ P22ΩΩ_TERRITOIRE_STRUCTURE_EXPORT active : /api/export/territoire-structure")
except Exception as e:
    logger.warning(f"P22ΩΩ_TERRITOIRE_STRUCTURE_EXPORT router not loaded: {e}")

# ═══ P22ΩΩ_TERRITOIRE_ESSENTIEL_1WORKER (Commandant STEEVE-MAX · 2026-05-18) ═══
# Router admin pour le cron pré-calcul 2000 membres
try:
    from routes.essentiel_prewarm_router import router as essentiel_prewarm_router
    app.include_router(essentiel_prewarm_router)
    logger.info("✓ P22ΩΩ_ESSENTIEL_PREWARM router active : /api/admin/essentiel-prewarm/*")
except Exception as e:
    logger.warning(f"P22ΩΩ_ESSENTIEL_PREWARM router not loaded: {e}")

# ═══ PHASE_XII_ESPECES_Ω — 5 ENGINES ESPÈCES (Commandant STEEVE-MAX · 2026-04-28) ═══
try:
    from routes.especes_omega_router import router as especes_omega_router
    app.include_router(especes_omega_router)
    logger.info("✓ PHASE_XII_ESPECES_Ω active : 5 engines (chevreuil/orignal/ours/wapiti/dindon) — /api/v30/especes/*")
except Exception as e:
    logger.warning(f"PHASE_XII_ESPECES_Ω router not loaded: {e}")

# ═══ PHASE_XIII_BIO_REACTEURS_Ω — RUNTIME LOADER (Commandant STEEVE-MAX · 2026-04-29) ═══
try:
    from routes.bio_reacteur_router_omega import router as bio_reacteur_router
    app.include_router(bio_reacteur_router)
    logger.info("✓ PHASE_XIII_BIO_REACTEURS_Ω active : runtime loader 5 BIO-REACTEURS — /api/v30/especes/bio-reacteur/*")
except Exception as e:
    logger.warning(f"PHASE_XIII_BIO_REACTEURS_Ω router not loaded: {e}")

# ═══ PHASE_XIV_OMEGA — CI hook sceau + audit longitudinal + SUPER ENGINES specs (Commandant STEEVE-MAX · 2026-04-29) ═══
try:
    from routes.phase_xiv_router_omega import router as phase_xiv_router
    app.include_router(phase_xiv_router)
    logger.info("✓ PHASE_XIV_Ω active : sceau-verify + audit-longitudinal + super-engines (interfaces) — /api/v30/{sceau,audit,super-engines}/*")
except Exception as e:
    logger.warning(f"PHASE_XIV_Ω router not loaded: {e}")

# ═══ PHASE_XV_OMEGA — 5 ENGINES SCIENTIFIQUES + ENGINE_IA + migration legacy (Commandant STEEVE-MAX · 2026-04-29) ═══
try:
    from routes.phase_xv_router_omega import router as phase_xv_router
    app.include_router(phase_xv_router)
    logger.info("✓ PHASE_XV_Ω active : 5 ENGINES SCIENTIFIQUES + ENGINE_IA — /api/v30/scientifique/*")
except Exception as e:
    logger.warning(f"PHASE_XV_Ω router not loaded: {e}")

# ═══ PHASE_XIX_OMEGA — 6 SUPER MASTERS HTTP optimisés (Commandant STEEVE-MAX · 2026-04-30 · ORDRE N°39) ═══
try:
    from routes.phase_xix_router_omega import router as phase_xix_router
    app.include_router(phase_xix_router)
    logger.info("✓ PHASE_XIX_Ω active : 6 SUPER MASTERS HTTP — /api/v30/super-masters/*")
except Exception as e:
    logger.warning(f"PHASE_XIX_Ω router not loaded: {e}")


# ═══ PHASE_XXII_OMEGA — GIS RECEPTION INFRA (Commandant STEEVE-MAX · ORDRE N°42_BIS) ═══
try:
    from routes.gis_reception_router_omega import router as gis_reception_router
    app.include_router(gis_reception_router)
    logger.info("✓ PHASE_XXII_Ω active : GIS RECEPTION — /api/v30/admin-premium/gis/*")
except Exception as e:
    logger.warning(f"PHASE_XXII_Ω GIS reception router not loaded: {e}")


# ═══ PHASE_XXVII_VOIE_B — GIS S3/B2 UPLOAD (ORDRE N°52-EXT · voie B) ═══
try:
    from routes.gis_s3_upload_router_omega import router as gis_s3_router
    app.include_router(gis_s3_router)
    logger.info("✓ VOIE_B active : GIS S3/B2 — /api/v30/admin-premium/gis/upload-chunk-s3/*")
except Exception as e:
    logger.warning(f"VOIE_B GIS S3/B2 router not loaded: {e}")


# ═══ PHASE_XXVI_OMEGA — BIO_PROFILE_135 SCHEMA API (ORDRE N°52 · Commandant STEEVE-MAX) ═══
try:
    from routes.bio_profile_schema_router_omega import router as bio_profile_schema_router
    app.include_router(bio_profile_schema_router)
    # Signal institutionnel SCHEMA_READY (émis au démarrage si chargement OK)
    from engines.v8_institutional.especes.bio_profile_135_loader_omega import (
        load_bio_profile_135, file_sha256,
    )
    _bp_data = load_bio_profile_135()
    _bp_sha = file_sha256()
    logger.info(
        "✓ PHASE_XXVI_Ω active · SCHEMA_READY BIO_PROFILE_OMEGA_135 · "
        f"entries={len(_bp_data['entries'])} · sha256={_bp_sha[:16]}… · "
        "routes /api/schema/*"
    )
except Exception as e:
    logger.error(
        f"SCHEMA_VIOLATION PHASE_XXVI_Ω BIO_PROFILE_135: {e} · PIPELINE_PARTIAL"
    )


# ═══ P22ΩΩ_STUBS_AUXILIAIRES_404 — STUBS 200 OK pour endpoints frontend orphelins ═══
# (Commandant STEEVE-MAX · 2026-05-18 · DIRECTIVE P0a BCE-4X ULTIME ABSOLU)
# Élimine les 404 console (seo/meta, bdre/dashboard, bdre/sources,
# legal-time/status, legal-time/upcoming, sharing/notifications/anonymous).
# Tous documentés comme « non-bloquants » par audit Phase-A.
try:
    from routes.stubs_auxiliary_404_omega import router as stubs_aux_router
    app.include_router(stubs_aux_router, prefix="/api")
    logger.info(
        "✓ P22ΩΩ_STUBS_AUXILIAIRES_404 active : 6 endpoints stubbed — "
        "/api/{seo/meta,v1/bdre/*,v1/notification/legal-time/*,sharing/notifications/anonymous}"
    )
except Exception as e:
    logger.warning(f"P22ΩΩ_STUBS_AUXILIAIRES_404 router not loaded: {e}")


logger.info("=" * 60)
logger.info(f"✓ V5-ULTIME-FUSION: {len(CORE_ROUTERS)} modules registered")
logger.info("✓ PHASE G: BIONIC Engine P0 active")
logger.info("✓ x4100: Score consolide 22 moteurs (Option C)")
logger.info("✓ x4500-ULTRA: BSAA active")
logger.info("✓ BCE: BIONIC Compliance Engine active")
logger.info("✓ ULTRA-MAX++ FIREWALL: Geo-fencing Shapely active")
logger.info("✓ SALINES ULTIME: 5 scores + 20 sources active")
logger.info("✓ CARTE-2027: Moteur cartographique terrain V7 active")
logger.info("✓ NUTRITION-ENGINE-V7: Pipeline Sol→Nutriments→Fourrage→Gibier active")
logger.info("✓ SPATIAL-ENGINE-V7: Corridors+Zones+Heatmap+Scoring+Amenagement active")
logger.info("✓ SUPRA-ENGINE-V7: Analyse+Fiche+Compare+Recommande+Commande active")
logger.info("✓ INTELLIGENCE-V7: Score Chasse V7 active")
logger.info("✓ V8-NATIONAL: Moteurs nationaux V8 active (9 biomes, 6 regimes, 8 especes)")
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
# ARCHIVE PERMANENTE v5201 — Directive x5302
# Second endpoint HTTPS (double redondance)
# ==============================================
_ARCHIVE_DIR = _os.path.join(_os.path.dirname(__file__), "static", "archive_v5201")

@app.get("/api/archive/v5201/list")
async def list_archive_v5201():
    """Liste les fichiers de l'archive permanente v5201."""
    files = []
    if _os.path.exists(_ARCHIVE_DIR):
        for f in sorted(_os.listdir(_ARCHIVE_DIR)):
            fpath = _os.path.join(_ARCHIVE_DIR, f)
            if _os.path.isfile(fpath):
                ext = _os.path.splitext(f)[1].lower()
                files.append({
                    "filename": f,
                    "size_bytes": _os.path.getsize(fpath),
                    "type": _MIME_MAP.get(ext, "application/octet-stream"),
                    "download_url": f"/api/archive/v5201/{f}",
                })
    return JSONResponse(content={
        "archive": "BIONIC_OS_v5201",
        "status": "SCELLE — IMMUTABLE",
        "protocol": "BCE-4X GOLDEN V6+",
        "files": files,
        "total": len(files),
    })

@app.get("/api/archive/v5201/{filename}")
async def serve_archive_v5201(filename: str):
    """Sert les fichiers de l'archive permanente v5201 (second endpoint)."""
    safe_name = _os.path.basename(filename)
    path = _os.path.join(_ARCHIVE_DIR, safe_name)
    if _os.path.exists(path):
        ext = _os.path.splitext(safe_name)[1].lower()
        media = _MIME_MAP.get(ext, "application/octet-stream")
        return FileResponse(path, filename=safe_name, media_type=media)
    from fastapi import HTTPException as _HTTPException
    raise _HTTPException(status_code=404, detail="Archive file not found")


# ==============================================
# MAIN
# ==============================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
