"""
P22ΩΩ_R4_SENTINELS_WORKER_COMPLET_Ω — Test régression
═════════════════════════════════════════════════════════════════════
BCE-4X ULTIME ABSOLU · Verrou Phase III · STRICT ADDITIF
Valide : sentinels + skip_map dans /api/v30/runtime/diagnostic-elite

Exécution :
  cd /app/backend && python -m pytest tests/test_r4_sentinels_omega.py -v

Couverture :
  - Helpers Python : _collect_r4_sentinels, _compute_watchdog_skip_map
  - Endpoint diagnostic-elite : présence champs sentinels, watchdog.skip_map
  - Idempotence
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path

import pytest

# Ajout du backend au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_r4_helpers_importable():
    """Le module diagnostic_router doit exposer les helpers R4 publics."""
    from routes import runtime_diagnostic_router as rd

    assert hasattr(rd, "_collect_r4_sentinels")
    assert hasattr(rd, "_compute_watchdog_skip_map")
    assert hasattr(rd, "_list_completed_flag_files")
    assert hasattr(rd, "_read_target_workers_from_cgroup")


def test_collect_r4_sentinels_empty(monkeypatch, tmp_path):
    """Sans flags ni workers, sentinels doit être vide mais bien structurée."""
    from routes import runtime_diagnostic_router as rd

    monkeypatch.setattr(rd, "_R4_LOG_DIR", str(tmp_path))
    out = rd._collect_r4_sentinels(workers=[])

    assert out["log_dir"] == str(tmp_path)
    assert out["completion_pattern"] == rd._R4_COMPLETION_PATTERN
    assert out["active_workers"] == []
    assert out["completed_workers"] == []
    assert out["active_count"] == 0
    assert out["completed_count"] == 0
    assert out["flags"] == []
    assert "doctrine" in out


def test_collect_r4_sentinels_with_flags(monkeypatch, tmp_path):
    """Avec flags + workers actifs, la collecte doit refléter l'état."""
    from routes import runtime_diagnostic_router as rd

    # Crée flags 3, 5, 7
    for idx in [3, 5, 7]:
        flag = tmp_path / f"completed_worker_{idx}.flag"
        flag.write_text(json.dumps({
            "worker_index": idx,
            "detected_at": "2026-06-10T00:00:00Z",
            "completion_evidence": "  [STATE_FILE_Ω] r5_idx_done=35 ≥ len=35 · WORKER COMPLET",
        }))

    monkeypatch.setattr(rd, "_R4_LOG_DIR", str(tmp_path))
    workers = [
        {"pid": 100, "worker_index": 0},
        {"pid": 101, "worker_index": 1},
        {"pid": 102, "worker_index": 2},
    ]
    out = rd._collect_r4_sentinels(workers=workers)

    assert out["active_workers"] == [0, 1, 2]
    assert out["active_count"] == 3
    assert out["completed_workers"] == [3, 5, 7]
    assert out["completed_count"] == 3
    assert len(out["flags"]) == 3
    # Vérifier le contenu JSON parsé
    flag_3 = next(f for f in out["flags"] if f["worker_index"] == 3)
    assert flag_3["content"]["worker_index"] == 3
    assert "WORKER COMPLET" in flag_3["content"]["completion_evidence"]


def test_skip_map_pure_active():
    """Tous workers actifs, aucun completed → respawn_targets vides."""
    from routes import runtime_diagnostic_router as rd

    sm = rd._compute_watchdog_skip_map(
        target_workers=3, active_indices=[0, 1, 2], completed_indices=[]
    )
    assert sm["target_workers"] == 3
    assert sm["effective_target"] == 3
    assert sm["skip_indices"] == []
    assert sm["respawn_target_indices"] == []
    for idx_str, payload in sm["by_index"].items():
        assert payload["status"] == "active"
        assert payload["skip_respawn"] is False


def test_skip_map_with_completed():
    """3 actifs + 5 completed (Élite TARGET=8) → effective_target=3, skip=5."""
    from routes import runtime_diagnostic_router as rd

    sm = rd._compute_watchdog_skip_map(
        target_workers=8,
        active_indices=[0, 1, 2],
        completed_indices=[3, 4, 5, 6, 7],
    )
    assert sm["target_workers"] == 8
    assert sm["effective_target"] == 3
    assert sm["skip_indices"] == [3, 4, 5, 6, 7]
    assert sm["respawn_target_indices"] == []
    assert sm["by_index"]["3"]["status"] == "completed"
    assert sm["by_index"]["3"]["skip_respawn"] is True
    assert sm["by_index"]["3"]["in_target_range"] is True
    assert sm["by_index"]["0"]["status"] == "active"


def test_skip_map_missing_triggers_respawn():
    """Workers manquants (sans flag) → respawn_target_indices remplie."""
    from routes import runtime_diagnostic_router as rd

    sm = rd._compute_watchdog_skip_map(
        target_workers=8,
        active_indices=[0, 1],
        completed_indices=[3, 4],
    )
    # Missing : 2, 5, 6, 7 (pas actifs, pas completed)
    assert set(sm["respawn_target_indices"]) == {2, 5, 6, 7}
    assert sm["by_index"]["2"]["status"] == "missing"
    assert sm["by_index"]["3"]["status"] == "completed"
    assert sm["by_index"]["3"]["skip_respawn"] is True


def test_skip_map_completed_outside_target_range():
    """Completed flag pour idx > target (descalation tier) doit être inclus."""
    from routes import runtime_diagnostic_router as rd

    sm = rd._compute_watchdog_skip_map(
        target_workers=3, active_indices=[0, 1, 2], completed_indices=[3, 4, 5, 6, 7]
    )
    # by_index doit inclure 0-7 (union)
    assert set(sm["by_index"].keys()) == {"0", "1", "2", "3", "4", "5", "6", "7"}
    # Indices > target sont marqués in_target_range=False
    assert sm["by_index"]["3"]["in_target_range"] is False
    assert sm["by_index"]["7"]["in_target_range"] is False
    assert sm["by_index"]["0"]["in_target_range"] is True


def test_watchdog_script_has_r4_block():
    """Le script bash watchdog doit contenir les helpers R4 doctrinaux."""
    p = Path("/app/backend/tools/zerocost_seed_r5_supervisor_watchdog.sh")
    content = p.read_text()
    assert "P22ΩΩ_R4_SENTINELS_WORKER_COMPLET_Ω" in content
    assert "r4_detect_and_mark_completed_workers" in content
    assert "r4_get_completed_indices" in content
    assert "[WATCHDOG-R4]" in content
    assert "_effective_target" in content
    assert "completed_worker_" in content


def test_diagnostic_elite_endpoint_exposes_sentinels(monkeypatch, tmp_path):
    """L'endpoint complet doit retourner sentinels + watchdog.skip_map."""
    from fastapi.testclient import TestClient
    from routes import runtime_diagnostic_router as rd

    # Isole R4_LOG_DIR vers tmp_path pour test
    monkeypatch.setattr(rd, "_R4_LOG_DIR", str(tmp_path))

    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(rd.router)
    client = TestClient(app)

    resp = client.get("/api/v30/runtime/diagnostic-elite")
    assert resp.status_code == 200
    body = resp.json()

    # Présence champs R4
    assert "sentinels" in body
    assert "watchdog" in body
    assert "skip_map" in body["watchdog"]
    assert "watchdog_r4_features" in body

    # Structure sentinels
    s = body["sentinels"]
    assert "active_workers" in s
    assert "completed_workers" in s
    assert "flags" in s
    assert "log_dir" in s
    assert "completion_pattern" in s

    # Structure watchdog.skip_map
    sm = body["watchdog"]["skip_map"]
    assert "target_workers" in sm
    assert "effective_target" in sm
    assert "skip_indices" in sm
    assert "respawn_target_indices" in sm
    assert "by_index" in sm

    # Verrou propagation
    feats = body["watchdog_r4_features"]
    assert feats["has_r4_detect_and_mark_completed_workers"] is True
    assert feats["has_r4_get_completed_indices"] is True
    assert feats["has_skip_completed_in_missing"] is True
    assert feats["has_r4_log_prefix"] is True
    assert feats["has_effective_target_branch"] is True
