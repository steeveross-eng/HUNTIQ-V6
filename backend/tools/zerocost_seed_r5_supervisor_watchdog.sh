#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════
# zerocost_seed_r5_supervisor_watchdog.sh
# Wrapper FOREGROUND pour supervisor · auto-relance daemon β2-ΣΤ
# P22ΩΩ_ACTIVATION_BETA2_ST_Ω · STEEVE-MAX
# ════════════════════════════════════════════════════════════════════
# Tourne en boucle infinie · vérifie toutes les 60s si workers β2-ΣΤ vivants
# · relance si tous morts. Le process supervisor reste TOUJOURS en vie
# pour bénéficier de l'autorestart au pod-restart.

set -u
CHECK_INTERVAL_S="${CHECK_INTERVAL_S:-45}"
# P22ΩΩ_WORKERS_DOWNSCALE_4_TO_3_Ω_MINFIX · 2026-06-04 · STEEVE-MAX
# Aligne MIN_WORKERS sur TARGET_WORKERS=3 pour stopper boucle RELANCE infinie
# (sinon n=3 < MIN=4 → kill+respawn tous les 45s · workers ne progressent jamais)
MIN_WORKERS="${MIN_WORKERS:-3}"
# Conf supervisor injecte historiquement MIN_WORKERS=4 (env override le défaut
# bash). Override force assignation après TARGET_WORKERS pour garantir
# cohérence MIN <= TARGET. Verrou Phase III intact.
# P22ΩΩ_WORKERS_SCALE_SAFE_Ω · 2026-02-20 · STEEVE-MAX
# Override forcé doctrinal : 12 workers SAFE LIMIT (priorité sur env supervisor).
# Précédent : 8 workers · gain attendu +50 % throughput cellulaire QC limitrophes.
# P22ΩΩ_CPU_THROTTLING_MITIGATION_Ω · 2026-06-01 · STEEVE-MAX · ACTION COMBINÉE A+F
# Réduction défensive : 12 → 6 workers (élimine CPU throttling 99.42 % avec
# CPU quota pod = 2 vCPUs). Verrou Phase III intact · aucun engine touché.
# P22ΩΩ_WORKERS_DOWNSCALE_6_TO_4_Ω · 2026-02-XX · STEEVE-MAX · DIRECTIVE GO STANDARD
# Throttling persistant constaté = 98.3 % périodes (9180/9339). Réduction
# additionnelle 6 → 4 workers pour libérer marge CPU à FastAPI (probes <100ms)
# et stopper cascade pod restart e1_monitor. Verrou Phase III intact.
# P22ΩΩ_WORKERS_DOWNSCALE_4_TO_3_Ω · 2026-06-04 · STEEVE-MAX · DIRECTIVE GO STANDARD
# Throttling persistant 96.4 % avec 4 workers · PSI cpu full 41 % · cycle pod
# 59 min (régression). Downscale additionnel 4 → 3 workers pour garantir MTBF
# ≥ plusieurs heures et permettre cohabitation stable FastAPI + MongoDB +
# e1_monitor sur quota 2 vCPUs. Vitesse R5 réduite ~25 % attendue mais
# progression continue sans restart pod. Verrou Phase III intact · escalade
# infra CPU 2→4 vCPUs en parallèle (P1 externe plateforme).
# ─── ANCIEN ASSIGN (préservé doctrinalement) : TARGET_WORKERS=3 ───
# P22ΩΩ_WORKERS_SCALE_ELITE_PLUS_Ω_AUTODETECT · 2026-06-06 · STEEVE-MAX
# Bascule automatique 3 (preview 2vCPU) / 8 (Elite 4+vCPU) via cgroup cpu.max.
# Lecture : /sys/fs/cgroup/cpu.max format "QUOTA PERIOD" en µs (-1 = pas de
# limite). Seuil discrimination ELITE = quota ≥ 400000 (4.0 vCPUs).
# Overrides env : TARGET_WORKERS_PREVIEW / TARGET_WORKERS_ELITE.
# Verrou Phase III intact · changement strictement additif · zéro impact engine.
TARGET_WORKERS_PREVIEW="${TARGET_WORKERS_PREVIEW:-3}"
TARGET_WORKERS_ELITE="${TARGET_WORKERS_ELITE:-8}"
_CPU_QUOTA_RAW=""
if [ -r /sys/fs/cgroup/cpu.max ]; then
    _CPU_QUOTA_RAW=$(awk '{print $1}' /sys/fs/cgroup/cpu.max 2>/dev/null)
fi
# Logique sélection tier :
#   - quota numérique ≥ 400000 µs (4 vCPUs)            → ELITE
#   - quota "max" (illimité, hyperscale futur)          → ELITE
#   - sinon (2 vCPUs preview standard, ou non lisible)  → PREVIEW (défensif)
if [[ "$_CPU_QUOTA_RAW" == "max" ]]; then
    TARGET_WORKERS=$TARGET_WORKERS_ELITE
    _TIER_DETECTED="ELITE_UNLIMITED (cpu.max=max)"
elif [[ "$_CPU_QUOTA_RAW" =~ ^[0-9]+$ ]] && (( _CPU_QUOTA_RAW >= 400000 )); then
    TARGET_WORKERS=$TARGET_WORKERS_ELITE
    _TIER_DETECTED="ELITE (cpu.max=${_CPU_QUOTA_RAW}µs ≥ 400000)"
else
    TARGET_WORKERS=$TARGET_WORKERS_PREVIEW
    _TIER_DETECTED="PREVIEW (cpu.max=${_CPU_QUOTA_RAW:-unknown}µs · <400000 ou non-lisible)"
fi
# P22ΩΩ_WORKERS_DOWNSCALE_4_TO_3_Ω_HARDLOCK · 2026-06-04 · STEEVE-MAX
# HARD-OVERRIDE final de MIN_WORKERS pour neutraliser l'env supervisor
# (conf historique injecte MIN_WORKERS=4 · provoquait boucle RELANCE
# infinie après TARGET=3). Le HARD-LOCK garantit MIN==TARGET en runtime.
MIN_WORKERS=$TARGET_WORKERS
LOG_PREFIX="[β2-ΣΤ-WATCHDOG]"

# ═══════════════════════════════════════════════════════════════════════════
# P22ΩΩ_P2_WORKER_PARTIAL_RECOVERY_WATCHDOG_Ω · 2026-06-08 · STEEVE-MAX
# BCE-4X ULTIME ABSOLU · Verrou Phase III · STRICT ADDITIF
# Helpers pour partial respawn ciblé des indices manquants.
# Configuration via env :
#   PARTIAL_RESPAWN_COOLDOWN_S=300  · anti-thrash (5 min)
#   MIN_PARTIAL_THRESHOLD=3         · seuil min n_alive pour activer partial
# Le full respawn legacy reste préservé en fallback si n < min OU cooldown actif.
# ═══════════════════════════════════════════════════════════════════════════
PARTIAL_RESPAWN_COOLDOWN_S="${PARTIAL_RESPAWN_COOLDOWN_S:-300}"
MIN_PARTIAL_THRESHOLD="${MIN_PARTIAL_THRESHOLD:-3}"
LAST_PARTIAL_RESPAWN_FILE="${LAST_PARTIAL_RESPAWN_FILE:-/tmp/zerocost_last_partial_respawn.ts}"

# ═══════════════════════════════════════════════════════════════════════════
# P22ΩΩ_R4_SENTINELS_WORKER_COMPLET_Ω · 2026-06-10 · STEEVE-MAX
# BCE-4X ULTIME ABSOLU · Verrou Phase III · STRICT ADDITIF · KIMBERLITE-READY
# Détection workers en état "WORKER COMPLET" (travail R2 terminé · exit
# gracieux). Crée un marker flag idempotent et exclut l'index de la liste
# de respawn afin de stopper la boucle perpétuelle cold-start→exit→respawn.
# Configuration :
#   R4_LOG_DIR=/var/log/bionic-zerocost-seed-r5 · dir contenant worker_N.log
#   R4_COMPLETION_PATTERN="WORKER COMPLET"      · pattern doctrinal d'exit
#   R4_SCAN_TAIL_LINES=50                       · profondeur scan logs
# Markers générés (un par worker complet) :
#   $R4_LOG_DIR/completed_worker_{N}.flag       · JSON forensique
# Journalisation explicite :
#   [WATCHDOG-R4] worker N marked completed → skip respawn
# ═══════════════════════════════════════════════════════════════════════════
R4_LOG_DIR="${R4_LOG_DIR:-/var/log/bionic-zerocost-seed-r5}"
R4_COMPLETION_PATTERN="${R4_COMPLETION_PATTERN:-WORKER COMPLET}"
R4_SCAN_TAIL_LINES="${R4_SCAN_TAIL_LINES:-50}"

# Détecte les workers en état WORKER COMPLET et crée/maintient un flag.
# Idempotent : si le flag existe déjà, n'écrit pas.
# Output stdout : liste indices nouvellement marqués (1 par ligne, peut être vide).
r4_detect_and_mark_completed_workers() {
    local TARGET=$1
    [[ -d "$R4_LOG_DIR" ]] || return 0
    local now_iso=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    local now_ts=$(date +%s)
    for ((idx=0; idx<TARGET; idx++)); do
        local logf="$R4_LOG_DIR/worker_${idx}.log"
        local flagf="$R4_LOG_DIR/completed_worker_${idx}.flag"
        [[ -f "$logf" ]] || continue
        # Cherche le pattern doctrinal dans les N dernières lignes
        if tail -n "$R4_SCAN_TAIL_LINES" "$logf" 2>/dev/null | grep -qF "$R4_COMPLETION_PATTERN"; then
            if [[ ! -f "$flagf" ]]; then
                # Capture la ligne de preuve (dernière occurrence du pattern)
                local evidence=$(tail -n "$R4_SCAN_TAIL_LINES" "$logf" 2>/dev/null | grep -F "$R4_COMPLETION_PATTERN" | tail -1 | sed 's/"/\\"/g')
                # Écriture atomique du flag (forensique JSON)
                printf '{"worker_index":%d,"detected_at":"%s","detected_ts":%d,"log_path":"%s","completion_pattern":"%s","completion_evidence":"%s","doctrine":"P22\\u03a9\\u03a9_R4_SENTINELS_WORKER_COMPLET_\\u03a9"}\n' \
                    "$idx" "$now_iso" "$now_ts" "$logf" "$R4_COMPLETION_PATTERN" "$evidence" \
                    > "$flagf.tmp" 2>/dev/null && mv -f "$flagf.tmp" "$flagf" 2>/dev/null
                echo "$LOG_PREFIX [WATCHDOG-R4] worker $idx marked completed → skip respawn (flag=$flagf)"
                echo "$idx"
            fi
        fi
    done
}

# Liste les indices marqués completed (flag présent sur disque)
# Output : 1 idx par ligne
r4_get_completed_indices() {
    [[ -d "$R4_LOG_DIR" ]] || return 0
    ls -1 "$R4_LOG_DIR"/completed_worker_*.flag 2>/dev/null | \
        sed -E 's|.*/completed_worker_([0-9]+)\.flag|\1|' | sort -nu
}

# Détection indices présents · lit /proc/{PID}/environ pour extraire WORKER_INDEX
# Output : liste numérique triée (1 idx par ligne)
get_present_worker_indices() {
    local PIDS=$(ps -ef 2>/dev/null | grep zerocost_worker_seed_r5 | grep -v grep | awk '{print $2}')
    for pid in $PIDS; do
        if [[ -r "/proc/$pid/environ" ]]; then
            tr '\0' '\n' < "/proc/$pid/environ" 2>/dev/null \
                | grep -E '^WORKER_INDEX=' | cut -d= -f2
        fi
    done | sort -nu
}

# Compute missing indices = expected (0..target-1) ∖ present ∖ completed (R4)
# P22ΩΩ_R4_SENTINELS_Ω : exclut les indices avec completed_worker_N.flag
get_missing_worker_indices() {
    local TARGET=$1
    local PRESENT=$(get_present_worker_indices | tr '\n' ' ')
    local COMPLETED=$(r4_get_completed_indices | tr '\n' ' ')
    local MISSING=""
    for ((idx=0; idx<TARGET; idx++)); do
        if echo " $PRESENT " | grep -qE " $idx "; then
            continue  # déjà vivant
        fi
        if echo " $COMPLETED " | grep -qE " $idx "; then
            continue  # marqué completed R4 → skip respawn
        fi
        MISSING="$MISSING $idx"
    done
    echo "$MISSING" | xargs  # trim
}

# Vérification cooldown anti-thrash
partial_respawn_cooldown_ok() {
    local LAST=0
    [[ -f "$LAST_PARTIAL_RESPAWN_FILE" ]] && LAST=$(cat "$LAST_PARTIAL_RESPAWN_FILE" 2>/dev/null || echo 0)
    local NOW=$(date +%s)
    local ELAPSED=$((NOW - LAST))
    [[ $ELAPSED -ge $PARTIAL_RESPAWN_COOLDOWN_S ]]
}

echo "$LOG_PREFIX Watchdog démarré · check toutes les ${CHECK_INTERVAL_S}s · MIN_WORKERS=$MIN_WORKERS · TARGET=$TARGET_WORKERS · TIER=$_TIER_DETECTED · PARTIAL_COOLDOWN=${PARTIAL_RESPAWN_COOLDOWN_S}s"

while true; do
    # Compter workers β2-ΣΤ vivants
    n=$(ps -ef 2>/dev/null | grep zerocost_worker_seed_r5 | grep -v grep | wc -l)

    # ══════════════════════════════════════════════════════════════════════
    # P22ΩΩ_R4_SENTINELS_WORKER_COMPLET_Ω · 2026-06-10 · STEEVE-MAX
    # SCAN PRÉALABLE des workers en état "WORKER COMPLET" · création flags
    # idempotente AVANT le calcul de MISSING_INDICES (pour pré-exclusion).
    # Verrou Phase III · additif strict · zéro mutation engine.
    # ══════════════════════════════════════════════════════════════════════
    _r4_newly_marked=$(r4_detect_and_mark_completed_workers "$TARGET_WORKERS")
    _r4_completed_list=$(r4_get_completed_indices | tr '\n' ',' | sed 's/,$//')
    _r4_completed_count=$(r4_get_completed_indices | wc -l)

    # Configuration env stagger/pacing (TIER-aware, identique à full respawn)
    if [[ "$_TIER_DETECTED" == ELITE* ]]; then
        _SPAWN_STAGGER_MS="${SPAWN_STAGGER_MS:-2000}"
        _WORKER_PACING_MS="${WORKER_PACING_MS:-50}"
    else
        _SPAWN_STAGGER_MS="${SPAWN_STAGGER_MS:-0}"
        _WORKER_PACING_MS="${WORKER_PACING_MS:-0}"
    fi

    # P22ΩΩ_P2_WORKER_PARTIAL_RECOVERY_Ω · 2026-06-08 · STEEVE-MAX
    # Logique watchdog en 3 branches :
    #   1) n == TARGET → état stable · heartbeat 5min
    #   2) n entre MIN_PARTIAL_THRESHOLD et TARGET ET cooldown OK ET MISSING détectés
    #      → ★ PARTIAL RESPAWN ciblé des indices manquants (additif Phase III)
    #   3) n < MIN_WORKERS OU cooldown actif → FULL RESPAWN legacy (preserved)
    # P22ΩΩ_R4_SENTINELS_Ω : l'objectif effectif exclut les workers complets
    # (target effectif = total - completed). Si n == effective_target, état stable.
    _effective_target=$((TARGET_WORKERS - _r4_completed_count))
    if [[ $_effective_target -lt 0 ]]; then _effective_target=0; fi

    if [[ $n -eq $TARGET_WORKERS ]]; then
        # ── Branche 1 · État stable · heartbeat ─────────────────────────────
        if (( $(date +%s) % 300 < CHECK_INTERVAL_S )); then
            echo "$LOG_PREFIX $(date -u +%H:%M:%SZ) · workers=$n/$TARGET_WORKERS OK · load=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | tr -d ',')"
        fi
    elif [[ $n -eq $_effective_target ]] && [[ $_r4_completed_count -gt 0 ]]; then
        # ── Branche 1b · État stable R4 · workers complets respectés ───────
        if (( $(date +%s) % 300 < CHECK_INTERVAL_S )); then
            echo "$LOG_PREFIX [WATCHDOG-R4] $(date -u +%H:%M:%SZ) · workers=$n/$TARGET_WORKERS · completed=[$_r4_completed_list] (effective_target=$_effective_target) · STABLE"
        fi
    elif [[ $n -ge $MIN_PARTIAL_THRESHOLD ]] && partial_respawn_cooldown_ok; then
        # ── Branche 2 · PARTIAL RESPAWN ciblé ──────────────────────────────
        MISSING_INDICES=$(get_missing_worker_indices "$TARGET_WORKERS")
        if [[ -n "$MISSING_INDICES" ]]; then
            echo "$LOG_PREFIX $(date -u +%Y-%m-%dT%H:%M:%SZ) · PARTIAL RESPAWN · n=$n/$TARGET_WORKERS · missing=[$MISSING_INDICES] · stagger=${_SPAWN_STAGGER_MS}ms"
            for idx in $MISSING_INDICES; do
                WORKER_COUNT=$TARGET_WORKERS \
                GRID_FILE_PATH=/app/backend/cache/zerocost_v1/canada_h3_grid_r5_seed_qc_limitrophes.json \
                MAX_R5_CELLS=0 \
                BLOCK_OUTSIDE_3RF=1 \
                SPAWN_STAGGER_MS="$_SPAWN_STAGGER_MS" \
                WORKER_PACING_MS="$_WORKER_PACING_MS" \
                bash /app/backend/tools/zerocost_seed_r5_daemon.sh spawn_index "$idx" 2>&1 | tail -2
                # Stagger entre respawns pour éviter pic CPU
                if [[ $_SPAWN_STAGGER_MS -gt 0 ]]; then
                    sleep $(awk "BEGIN { print $_SPAWN_STAGGER_MS / 1000 }")
                fi
            done
            date +%s > "$LAST_PARTIAL_RESPAWN_FILE"
            echo "$LOG_PREFIX Partial respawn complet · cooldown ${PARTIAL_RESPAWN_COOLDOWN_S}s actif"
        fi
    elif [[ $((n + _r4_completed_count)) -lt $MIN_WORKERS ]]; then
        # ── Branche 3 · FULL RESPAWN legacy (Verrou Phase III preserved) ───
        # P22ΩΩ_R4_SENTINELS_Ω : seuil ajusté = n + completed_R4 < MIN_WORKERS
        # (évite de tuer 3 workers actifs alors que 5 sont en WORKER COMPLET valide).
        echo "$LOG_PREFIX $(date -u +%Y-%m-%dT%H:%M:%SZ) · workers vivants=$n + completed=$_r4_completed_count < MIN=$MIN_WORKERS · RELANCE FULL"
        # Nettoyage state file
        bash /app/backend/tools/zerocost_seed_r5_daemon.sh stop 2>&1 | tail -2 || true
        sleep 2
        WORKER_COUNT=$TARGET_WORKERS \
        GRID_FILE_PATH=/app/backend/cache/zerocost_v1/canada_h3_grid_r5_seed_qc_limitrophes.json \
        MAX_R5_CELLS=0 \
        BLOCK_OUTSIDE_3RF=1 \
        SPAWN_STAGGER_MS="$_SPAWN_STAGGER_MS" \
        WORKER_PACING_MS="$_WORKER_PACING_MS" \
        bash /app/backend/tools/zerocost_seed_r5_daemon.sh start 2>&1 | tail -3
        echo "$LOG_PREFIX Relance terminée (TARGET=$TARGET_WORKERS · grille=QC_LIMITROPHES · stagger=${_SPAWN_STAGGER_MS}ms · pacing=${_WORKER_PACING_MS}ms)"
        # P22ΩΩ_R2_ORPHAN_STATE_PURGE_AT_BOOT_Ω · 2026-06-06 · STEEVE-MAX
        # Purge automatique des clés R2 state_worker_*.json orphelines (worker_index
        # >= TARGET_WORKERS), vestiges des cycles antérieurs (6w → 3w → 8w).
        # CROSS-POD-SAFE : ne purge que les clés matchant la grille active locale
        # (préserve pods cohabitant qui écrivent sur d'autres grilles ex Phase 1).
        # Garantit lag_max_s < 60s et sync_status OK/MATCH dans /api/v30/runtime/tier-status.
        # Best-effort · zéro impact si R2 indisponible · idempotent.
        _LOCAL_GRID="/app/backend/cache/zerocost_v1/canada_h3_grid_r5_seed_qc_limitrophes.json"
        python3 -c "
import sys
sys.path.insert(0, '/app/backend')
try:
    from integrations.r2_state_persistence_omega import prune_orphan_state_keys
    r = prune_orphan_state_keys(
        active_worker_count=$TARGET_WORKERS,
        expected_grid_file='$_LOCAL_GRID',
    )
    print(f'[R2_ORPHAN_PURGE] checked={r[\"checked\"]} · purged={len(r[\"purged\"])} · kept_active={len(r[\"kept_active\"])} · kept_other_pod={len(r[\"kept_other_pod\"])} · errors={len(r[\"errors\"])}')
    if r['purged']:
        for k in r['purged']: print(f'  PURGED      : {k}')
    if r['kept_other_pod']:
        for item in r['kept_other_pod']: print(f'  KEEP OTHER  : {item}')
    if r['errors']:
        for e in r['errors']: print(f'  ERROR       : {e}')
except Exception as e:
    print(f'[R2_ORPHAN_PURGE] skip: {e}')
" 2>&1 | head -20
    else
        # n entre min et target MAIS cooldown actif (partial bloqué) · log warning
        if (( $(date +%s) % 300 < CHECK_INTERVAL_S )); then
            LAST=0
            [[ -f "$LAST_PARTIAL_RESPAWN_FILE" ]] && LAST=$(cat "$LAST_PARTIAL_RESPAWN_FILE" 2>/dev/null || echo 0)
            COOLDOWN_LEFT=$((PARTIAL_RESPAWN_COOLDOWN_S - ($(date +%s) - LAST)))
            echo "$LOG_PREFIX $(date -u +%H:%M:%SZ) · workers=$n/$TARGET_WORKERS · cooldown partial actif (${COOLDOWN_LEFT}s restant)"
        fi
    fi

    sleep $CHECK_INTERVAL_S
done
