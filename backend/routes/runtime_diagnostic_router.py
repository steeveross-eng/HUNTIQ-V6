"""
runtime_diagnostic_router.py — Endpoint Diagnostic Elite Production
═══════════════════════════════════════════════════════════════════════════════
P22ΩΩ_RUNTIME_DIAGNOSTIC_ELITE_Ω · COMMANDANT STEEVE-MAX · 2026-06-08
BCE-4X ULTIME ABSOLU · Verrou Phase III · STRICT ADDITIF · LECTURE SEULE

OBJECTIF
--------
Exposer des informations diagnostic sur le pod Production Elite sans nécessiter
d'accès SSH. Permet d'investiguer :
  - Variables d'environnement effectives (subset whitelist · zéro secret leak)
  - Workers β2-ΣΤ : PID + WORKER_INDEX + WORKER_COUNT + memory + CPU
  - Logs supervisor récents (whitelist programs)
  - Logs worker stderr (recent crashes)
  - Configuration bash watchdog (mtimes des scripts)

DOCTRINE
--------
- Read-only · aucune mutation
- Whitelist stricte pour les env vars (jamais de COPERNICUS_PASSWORD, R2_SECRET, etc.)
- Limit 100 lignes par fichier log (timeout protection)
- Best-effort si fichiers absent
- Verrou Phase III · additif strict · 0 modification engine existant
═══════════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import logging
import os
import re
import subprocess
import time
from pathlib import Path
from typing import Any

from fastapi import APIRouter

logger = logging.getLogger("bionic.runtime.diagnostic")

router = APIRouter(prefix="/api/v30/runtime", tags=["runtime-diagnostic"])

# Whitelist env vars · ZÉRO secrets sensibles
_ENV_WHITELIST = {
    "SPAWN_STAGGER_MS", "WORKER_PACING_MS", "WORKER_PARTIAL_RESPAWN_COOLDOWN_S",
    "MIN_PARTIAL_THRESHOLD", "PARTIAL_RESPAWN_COOLDOWN_S",
    "TARGET_WORKERS", "TARGET_WORKERS_ELITE", "MIN_WORKERS",
    "ZEROCOST_INPROCESS_WORKER_COUNT", "ZEROCOST_INPROCESS_DISABLE",
    "ZEROCOST_INPROCESS_FORCE", "ZEROCOST_INPROCESS_CHECK_INTERVAL_S",
    "ZEROCOST_INPROCESS_MIN_WORKERS", "ZEROCOST_GRID_FILE_PATH",
    "ZEROCOST_WORKER_SPAWN_LOGGING",
    "INGESTION_P1_ARMED", "INGESTION_P1_DISK_AUTHORIZED",
    "P1_MAX_TILES", "P1_MAX_SIZE_MB", "P1_TIMEOUT_S",
    "MAX_R5_CELLS", "BLOCK_OUTSIDE_3RF",
    "ENV", "ENVIRONMENT", "TIER", "ELITE_TIER",
    "COPERNICUS_USERNAME",  # username pas sensible (déjà loggué dans cdse-auth-probe)
    "PYTHONPATH", "HOSTNAME", "USER",
    # P22ΩΩ_R4_SENTINELS_WORKER_COMPLET_Ω · 2026-06-10
    "R4_LOG_DIR", "R4_COMPLETION_PATTERN", "R4_SCAN_TAIL_LINES",
}

# P22ΩΩ_R4_SENTINELS_WORKER_COMPLET_Ω · 2026-06-10 · STEEVE-MAX
# Dossier canonique des markers completed_worker_N.flag · doit matcher la
# valeur R4_LOG_DIR du watchdog (zerocost_seed_r5_supervisor_watchdog.sh).
_R4_LOG_DIR = os.environ.get("R4_LOG_DIR", "/var/log/bionic-zerocost-seed-r5")
_R4_COMPLETION_PATTERN = os.environ.get("R4_COMPLETION_PATTERN", "WORKER COMPLET")

# Patterns d'env vars sensibles · jamais exposés même en debug
_SENSITIVE_PATTERNS = re.compile(
    r"(PASSWORD|SECRET|TOKEN|KEY|CREDENTIAL|AUTH|MONGO_URL|DB_NAME)",
    re.IGNORECASE,
)


def _read_env_whitelisted() -> dict[str, str]:
    """Retourne uniquement les env vars de la whitelist · jamais de secret."""
    out: dict[str, str] = {}
    for k, v in os.environ.items():
        if _SENSITIVE_PATTERNS.search(k):
            continue
        if k in _ENV_WHITELIST:
            out[k] = v
    return dict(sorted(out.items()))


def _read_proc_environ(pid: int) -> dict[str, str]:
    """Lecture /proc/PID/environ · subset whitelist."""
    try:
        path = f"/proc/{pid}/environ"
        if not os.path.exists(path) or not os.access(path, os.R_OK):
            return {}
        with open(path, "rb") as f:
            raw = f.read()
        entries = raw.split(b"\x00")
        out: dict[str, str] = {}
        for entry in entries:
            if b"=" not in entry:
                continue
            try:
                k, v = entry.decode("utf-8", errors="ignore").split("=", 1)
            except ValueError:
                continue
            if _SENSITIVE_PATTERNS.search(k):
                continue
            if k in _ENV_WHITELIST or k.startswith("WORKER_"):
                out[k] = v
        return out
    except Exception:
        return {}


def _ps_workers() -> list[dict[str, Any]]:
    """Liste workers β2-ΣΤ via ps + lecture /proc."""
    out: list[dict[str, Any]] = []
    try:
        r = subprocess.run(
            ["ps", "-eo", "pid,ppid,pcpu,pmem,rss,etimes,comm,args"],
            capture_output=True, text=True, timeout=5,
        )
        for line in r.stdout.splitlines():
            if "zerocost_worker_seed_r5" not in line or "grep" in line:
                continue
            parts = line.split(None, 7)
            if len(parts) < 8:
                continue
            try:
                pid = int(parts[0])
            except ValueError:
                continue
            env = _read_proc_environ(pid)
            worker_idx = env.get("WORKER_INDEX")
            out.append({
                "pid": pid,
                "ppid": int(parts[1]) if parts[1].isdigit() else None,
                "pcpu": float(parts[2]) if parts[2].replace(".", "").isdigit() else None,
                "pmem": float(parts[3]) if parts[3].replace(".", "").isdigit() else None,
                "rss_kb": int(parts[4]) if parts[4].isdigit() else None,
                "etimes_s": int(parts[5]) if parts[5].isdigit() else None,
                "worker_index": int(worker_idx) if worker_idx and worker_idx.isdigit() else None,
                "worker_count_env": env.get("WORKER_COUNT"),
                "spawn_stagger_env": env.get("SPAWN_STAGGER_MS"),
                "worker_pacing_env": env.get("WORKER_PACING_MS"),
            })
    except Exception as e:
        logger.debug(f"ps_workers fail: {e}")
    return sorted(out, key=lambda x: x.get("worker_index") or 999)


def _tail_file(path: str, max_lines: int = 100, max_chars: int = 50000) -> str:
    """Lecture des dernières lignes d'un fichier · best-effort + size cap."""
    try:
        p = Path(path)
        if not p.is_file():
            return f"[NOT_FOUND] {path}"
        # Lecture intelligente · seek from end
        size = p.stat().st_size
        with p.open("rb") as f:
            if size > max_chars * 4:
                f.seek(size - max_chars * 4)
                _ = f.readline()  # skip partial line
            raw = f.read()
        text = raw.decode("utf-8", errors="ignore")
        lines = text.splitlines()
        out_lines = lines[-max_lines:]
        out = "\n".join(out_lines)
        if len(out) > max_chars:
            out = out[-max_chars:]
        return out
    except Exception as e:
        return f"[ERROR_READ] {path}: {e}"


def _file_meta(path: str) -> dict[str, Any]:
    """Métadonnées fichier (mtime, size) pour preuve de propagation Deploy."""
    try:
        p = Path(path)
        if not p.exists():
            return {"exists": False}
        st = p.stat()
        return {
            "exists": True,
            "size_bytes": st.st_size,
            "mtime_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(st.st_mtime)),
            "mode_octal": oct(st.st_mode)[-3:],
        }
    except Exception as e:
        return {"exists": False, "error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════
# P22ΩΩ_R4_SENTINELS_WORKER_COMPLET_Ω · 2026-06-10 · STEEVE-MAX
# BCE-4X ULTIME ABSOLU · Verrou Phase III · STRICT ADDITIF · KIMBERLITE-READY
# Read-only · collecte les markers completed_worker_N.flag et expose la
# vision unifiée { active_workers, completed_workers, flags } + skip_map.
# ═══════════════════════════════════════════════════════════════════════════
import json as _json
import re as _re

_FLAG_NAME_RE = _re.compile(r"completed_worker_(\d+)\.flag$")


def _list_completed_flag_files() -> list[Path]:
    """Liste les fichiers completed_worker_N.flag dans R4_LOG_DIR."""
    p = Path(_R4_LOG_DIR)
    if not p.is_dir():
        return []
    out = []
    try:
        for f in p.iterdir():
            if f.is_file() and _FLAG_NAME_RE.search(f.name):
                out.append(f)
    except Exception:
        return []
    return sorted(out, key=lambda x: x.name)


def _read_flag_json(path: Path) -> dict[str, Any]:
    """Lit le contenu JSON d'un flag (best-effort · tolère mal-formé)."""
    try:
        raw = path.read_text(encoding="utf-8", errors="ignore").strip()
        try:
            return _json.loads(raw)
        except Exception:
            return {"_raw": raw[:500]}
    except Exception as e:
        return {"_error": str(e)}


def _collect_r4_sentinels(workers: list[dict[str, Any]]) -> dict[str, Any]:
    """Construit la structure sentinels R4 unifiée.
    
    Returns:
        {
            "doctrine": "P22ΩΩ_R4_SENTINELS_WORKER_COMPLET_Ω",
            "log_dir": "/var/log/...",
            "completion_pattern": "WORKER COMPLET",
            "active_workers": [0, 1, 2],      # indices PID-vivants
            "completed_workers": [3, 4, 5, 6, 7], # indices flag présent
            "flags": [
                {"worker_index": 3, "flag_path": "...", "size_bytes": N,
                 "mtime_utc": "...", "content": {...}}, ...
            ],
            "completed_count": 5,
            "active_count": 3,
        }
    """
    active_indices = sorted({
        w.get("worker_index") for w in workers
        if w.get("worker_index") is not None
    })
    flag_files = _list_completed_flag_files()
    flags_payload: list[dict[str, Any]] = []
    completed_indices: list[int] = []
    for f in flag_files:
        m = _FLAG_NAME_RE.search(f.name)
        if not m:
            continue
        try:
            idx = int(m.group(1))
        except ValueError:
            continue
        try:
            st = f.stat()
            meta = {
                "worker_index": idx,
                "flag_path": str(f),
                "size_bytes": st.st_size,
                "mtime_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(st.st_mtime)),
                "mode_octal": oct(st.st_mode)[-3:],
                "content": _read_flag_json(f),
            }
        except Exception as e:
            meta = {"worker_index": idx, "flag_path": str(f), "_error": str(e)}
        flags_payload.append(meta)
        completed_indices.append(idx)
    completed_indices = sorted(set(completed_indices))
    return {
        "doctrine": "P22ΩΩ_R4_SENTINELS_WORKER_COMPLET_Ω · BCE-4X · Verrou Phase III · ADDITIF strict",
        "log_dir": _R4_LOG_DIR,
        "completion_pattern": _R4_COMPLETION_PATTERN,
        "active_workers": active_indices,
        "active_count": len(active_indices),
        "completed_workers": completed_indices,
        "completed_count": len(completed_indices),
        "flags": flags_payload,
    }


def _compute_watchdog_skip_map(
    target_workers: int,
    active_indices: list[int],
    completed_indices: list[int],
) -> dict[str, Any]:
    """Calcule la skip_map du watchdog : par index, status + reason.
    
    Status enum :
      - "active"          → worker vivant (PID présent)
      - "completed"       → WORKER COMPLET (flag présent · skip respawn)
      - "missing"         → ni vivant ni completed (sera respawné branche 2)
      - "out_of_range"    → idx >= target_workers (ne s'applique pas ici)
    """
    by_index: dict[str, dict[str, Any]] = {}
    skip_indices: list[int] = []
    respawn_targets: list[int] = []
    # Union des indices à couvrir : range(target) ∪ completed_indices (peut excéder target)
    all_indices = sorted(set(list(range(target_workers)) + list(completed_indices) + list(active_indices)))
    for idx in all_indices:
        in_target = (idx < target_workers)
        if idx in active_indices:
            by_index[str(idx)] = {
                "status": "active",
                "reason": "PID alive",
                "skip_respawn": False,
                "in_target_range": in_target,
            }
        elif idx in completed_indices:
            by_index[str(idx)] = {
                "status": "completed",
                "reason": f"flag completed_worker_{idx}.flag present · pattern '{_R4_COMPLETION_PATTERN}' detected",
                "skip_respawn": True,
                "in_target_range": in_target,
            }
            skip_indices.append(idx)
        else:
            by_index[str(idx)] = {
                "status": "missing",
                "reason": "PID absent and no completion flag",
                "skip_respawn": False,
                "in_target_range": in_target,
            }
            if in_target:
                respawn_targets.append(idx)
    effective_target = target_workers - len(completed_indices)
    return {
        "doctrine": "P22ΩΩ_R4_SENTINELS_WORKER_COMPLET_Ω · skip_map",
        "target_workers": target_workers,
        "effective_target": max(effective_target, 0),
        "skip_indices": skip_indices,
        "skip_count": len(skip_indices),
        "respawn_target_indices": respawn_targets,
        "respawn_target_count": len(respawn_targets),
        "by_index": by_index,
    }


def _read_target_workers_from_cgroup() -> int:
    """Détecte TARGET_WORKERS effectif (env ELITE/PREVIEW basé sur cgroup),
    aligné sur la logique du watchdog bash. Best-effort."""
    target_preview = int(os.environ.get("TARGET_WORKERS_PREVIEW", "3"))
    target_elite = int(os.environ.get("TARGET_WORKERS_ELITE", "8"))
    try:
        with open("/sys/fs/cgroup/cpu.max") as f:
            raw = f.read().strip().split()
        if raw and raw[0] == "max":
            return target_elite
        if raw and raw[0].isdigit() and int(raw[0]) >= 400000:
            return target_elite
    except Exception:
        pass
    return target_preview


@router.get("/diagnostic-elite")
def diagnostic_elite(
    include_env: bool = True,
    include_workers: bool = True,
    include_supervisor_logs: bool = True,
    include_worker_logs: bool = True,
    log_lines: int = 80,
) -> dict[str, Any]:
    """Endpoint diagnostic complet · lecture seule · zéro secret leak.

    P22ΩΩ_RUNTIME_DIAGNOSTIC_ELITE_Ω · 2026-06-08 · STEEVE-MAX
    Permet d'investiguer pod Production Elite sans accès SSH.
    """
    t0 = time.time()

    out: dict[str, Any] = {
        "served_by": "RUNTIME-DIAGNOSTIC-Ω-ROUTER",
        "doctrine": "P22ΩΩ_RUNTIME_DIAGNOSTIC_ELITE_Ω · BCE-4X · Verrou Phase III · read-only · whitelist secrets",
        "checked_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    if include_env:
        out["env_whitelist"] = _read_env_whitelisted()

    if include_workers:
        out["workers"] = _ps_workers()
        out["workers_count"] = len(out["workers"])

    # ═══════════════════════════════════════════════════════════════════
    # P22ΩΩ_R4_SENTINELS_WORKER_COMPLET_Ω · 2026-06-10 · STEEVE-MAX
    # Sentinels R4 + watchdog.skip_map (ADDITIF · zéro mutation legacy)
    # ═══════════════════════════════════════════════════════════════════
    _workers_list = out.get("workers", [])
    sentinels = _collect_r4_sentinels(_workers_list)
    out["sentinels"] = sentinels
    _target_workers = _read_target_workers_from_cgroup()
    out["watchdog"] = {
        "doctrine": "P22ΩΩ_R4_SENTINELS_WORKER_COMPLET_Ω · watchdog snapshot",
        "target_workers_detected": _target_workers,
        "skip_map": _compute_watchdog_skip_map(
            target_workers=_target_workers,
            active_indices=sentinels["active_workers"],
            completed_indices=sentinels["completed_workers"],
        ),
    }

    # Bash watchdog scripts mtimes (preuve Deploy propagation)
    out["bash_scripts"] = {
        "watchdog": _file_meta("/app/backend/tools/zerocost_seed_r5_supervisor_watchdog.sh"),
        "daemon": _file_meta("/app/backend/tools/zerocost_seed_r5_daemon.sh"),
        "worker": _file_meta("/app/backend/tools/zerocost_worker_seed_r5.py"),
        "last_partial_respawn_marker": _file_meta("/tmp/zerocost_last_partial_respawn.ts"),
    }

    # Test si les helpers R3 + R4 sont présents dans le watchdog déployé
    try:
        with open("/app/backend/tools/zerocost_seed_r5_supervisor_watchdog.sh") as f:
            content = f.read()
        out["watchdog_r3_features"] = {
            "has_get_present_worker_indices": "get_present_worker_indices" in content,
            "has_get_missing_worker_indices": "get_missing_worker_indices" in content,
            "has_partial_respawn_branch": "PARTIAL RESPAWN" in content,
            "has_cooldown_check": "partial_respawn_cooldown_ok" in content,
        }
        # P22ΩΩ_R4_SENTINELS_Ω : preuve propagation Deploy du patch R4
        out["watchdog_r4_features"] = {
            "has_r4_detect_and_mark_completed_workers": "r4_detect_and_mark_completed_workers" in content,
            "has_r4_get_completed_indices": "r4_get_completed_indices" in content,
            "has_skip_completed_in_missing": "COMPLETED=$(r4_get_completed_indices" in content,
            "has_r4_log_prefix": "[WATCHDOG-R4]" in content,
            "has_effective_target_branch": "_effective_target" in content,
        }
    except Exception:
        out["watchdog_r3_features"] = {"error": "read_fail"}
        out["watchdog_r4_features"] = {"error": "read_fail"}

    if include_supervisor_logs:
        # Supervisor logs · whitelist programs probables
        log_dir = "/var/log/supervisor"
        candidates = [
            "backend.out.log", "backend.err.log",
            "zerocost_seed_r5_watchdog.out.log", "zerocost_seed_r5_watchdog.err.log",
            "supervisord.log",
        ]
        out["supervisor_logs"] = {}
        for fname in candidates:
            path = f"{log_dir}/{fname}"
            out["supervisor_logs"][fname] = _tail_file(path, max_lines=log_lines)

    if include_worker_logs:
        # Logs worker β2-ΣΤ · cherche les répertoires standards
        worker_log_dirs = [
            "/var/log/bionic-zerocost-seed-r5",
            "/tmp/zerocost_seed_r5",
            "/var/log/zerocost",
        ]
        out["worker_logs"] = {}
        for d in worker_log_dirs:
            if not os.path.isdir(d):
                continue
            try:
                files = sorted(os.listdir(d))[:16]  # max 16 fichiers
            except Exception:
                continue
            out["worker_logs"][d] = {
                f: _tail_file(f"{d}/{f}", max_lines=log_lines) for f in files
                if f.endswith((".log", ".err", ".out"))
            }

    # State file daemon (PIDs trackés)
    state_path = "/var/log/bionic-zerocost-seed-r5/state.json"
    if os.path.isfile(state_path):
        try:
            import json
            with open(state_path) as f:
                out["daemon_state"] = json.load(f)
        except Exception as e:
            out["daemon_state"] = {"error": str(e)}

    out["elapsed_ms"] = int((time.time() - t0) * 1000)
    return out
