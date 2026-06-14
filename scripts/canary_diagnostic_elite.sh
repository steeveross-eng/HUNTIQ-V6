#!/usr/bin/env bash
# ═════════════════════════════════════════════════════════════════════════════
# canary_diagnostic_elite.sh — BCE-4X ULTIME ABSOLU · Verrou Phase III
# COMMANDANT STEEVE-MAX · doctrine P22ΩΩ_R4_SENTINELS_WORKER_COMPLET_Ω
# ─────────────────────────────────────────────────────────────────────────────
# Sonde CANARY READ-ONLY contre /api/v30/runtime/diagnostic-elite
# Validation Kimberlite continue post-déploiement Élite.
#
# Couverture audits :
#   A. Preuve filesystem      (sentinels.flags présents)
#   B. Preuve watchdog R4     (watchdog_r4_features tous true · script propagé)
#   C. Preuve API sentinels   (champs sentinels, watchdog.skip_map structurés)
#   D. Preuve comportementale (skip_map.respawn_target_indices vide ⇒ stable)
#   E. Bonus HRDEM            (P1_MAX_SIZE_MB, P1_MAX_TILES, P1_TIMEOUT_S)
#
# Modes :
#   text (default) · pretty output coloré (TTY)
#   json           · machine-readable (CI/CD · scrape Prometheus, etc.)
#
# Exit codes :
#   0 = ALL CHECKS PASS
#   1 = CRITICAL FAIL (R4 absent OU sentinels absent OU HTTP != 200)
#   2 = DEGRADED     (HRDEM non injectés OU respawn_targets > 0)
#   3 = NETWORK ERROR (curl timeout / unreachable)
#   4 = INVALID JSON  (réponse non parsable)
#
# Variables d'environnement (toutes optionnelles) :
#   CANARY_TARGET_URL       (default: https://huntiq-restore.emergent.host)
#   CANARY_TIMEOUT_S        (default: 30)
#   CANARY_OUTPUT           (default: text · valeurs: text|json)
#   CANARY_REQUIRE_HRDEM    (default: 1 · 0 = ne pas exiger HRDEM)
#   CANARY_EXPECTED_TARGET  (default: 8 · target_workers attendu Élite)
#   CANARY_LOG_FILE         (default: vide · si set, append rapport en log)
#
# Usage :
#   ./canary_diagnostic_elite.sh
#   CANARY_OUTPUT=json ./canary_diagnostic_elite.sh > /tmp/report.json
#   CANARY_TARGET_URL=https://staging.example.com ./canary_diagnostic_elite.sh
#   crontab : */5 * * * * /app/scripts/canary_diagnostic_elite.sh >> /var/log/canary.log
# ═════════════════════════════════════════════════════════════════════════════
set -uo pipefail

# ─── CONFIGURATION ─────────────────────────────────────────────────────────
CANARY_TARGET_URL="${CANARY_TARGET_URL:-https://huntiq-restore.emergent.host}"
CANARY_TIMEOUT_S="${CANARY_TIMEOUT_S:-30}"
CANARY_OUTPUT="${CANARY_OUTPUT:-text}"
CANARY_REQUIRE_HRDEM="${CANARY_REQUIRE_HRDEM:-1}"
CANARY_EXPECTED_TARGET="${CANARY_EXPECTED_TARGET:-8}"
CANARY_LOG_FILE="${CANARY_LOG_FILE:-}"
CANARY_ENDPOINT_PATH="${CANARY_ENDPOINT_PATH:-/api/v30/runtime/diagnostic-elite}"

DOCTRINE="P22ΩΩ_R4_SENTINELS_WORKER_COMPLET_Ω · CANARY"
STARTED_AT_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
TMP_RESP="$(mktemp /tmp/canary_diag_XXXXXX.json)"
trap 'rm -f "$TMP_RESP"' EXIT

# ─── COULEURS (TTY uniquement) ────────────────────────────────────────────
if [[ -t 1 ]] && [[ "$CANARY_OUTPUT" == "text" ]]; then
    C_RESET=$'\033[0m'; C_BOLD=$'\033[1m'; C_DIM=$'\033[2m'
    C_RED=$'\033[31m'; C_GREEN=$'\033[32m'; C_YELLOW=$'\033[33m'
    C_BLUE=$'\033[34m'; C_CYAN=$'\033[36m'
else
    C_RESET=""; C_BOLD=""; C_DIM=""; C_RED=""; C_GREEN=""; C_YELLOW=""; C_BLUE=""; C_CYAN=""
fi

ok()    { echo "${C_GREEN}✓${C_RESET} $*"; }
fail()  { echo "${C_RED}✗${C_RESET} $*"; }
warn()  { echo "${C_YELLOW}⚠${C_RESET} $*"; }
info()  { echo "${C_CYAN}·${C_RESET} $*"; }
hdr()   { echo "${C_BOLD}${C_BLUE}═══ $* ═══${C_RESET}"; }

# ─── DÉPENDANCES ──────────────────────────────────────────────────────────
command -v curl   >/dev/null || { echo "FATAL: curl absent"   >&2; exit 3; }
command -v python3 >/dev/null || { echo "FATAL: python3 absent" >&2; exit 3; }

# ─── SONDE HTTP ────────────────────────────────────────────────────────────
URL="${CANARY_TARGET_URL%/}${CANARY_ENDPOINT_PATH}"
HTTP_CODE=$(curl -sS -o "$TMP_RESP" -w "%{http_code}" \
    --max-time "$CANARY_TIMEOUT_S" \
    --connect-timeout 10 \
    -H "User-Agent: BCE-4X-CANARY/1.0" \
    -H "Accept: application/json" \
    "$URL" 2>/dev/null || echo "000")
RESP_SIZE=$(wc -c < "$TMP_RESP" 2>/dev/null || echo "0")

# ─── ÉVALUATION RÉPONSE ───────────────────────────────────────────────────
EXIT_CODE=0  # 0=pass, 1=critical, 2=degraded, 3=network, 4=invalid_json

if [[ "$HTTP_CODE" == "000" ]] || [[ "$HTTP_CODE" == "" ]] || [[ "$HTTP_CODE" =~ ^0+$ ]]; then
    EXIT_CODE=3
    NETWORK_ERROR="curl failed · target unreachable or timeout (${CANARY_TIMEOUT_S}s)"
fi

if [[ "$EXIT_CODE" -eq 0 ]] && [[ "$HTTP_CODE" != "200" ]]; then
    EXIT_CODE=1
    HTTP_ERROR="HTTP $HTTP_CODE (expected 200)"
fi

# Parse JSON · extraction des champs Kimberlite via python3
PARSE_REPORT=$(python3 - "$TMP_RESP" "$CANARY_EXPECTED_TARGET" "$CANARY_REQUIRE_HRDEM" <<'PYEOF' 2>&1
import json, sys, os

resp_path = sys.argv[1]
expected_target = int(sys.argv[2])
require_hrdem = int(sys.argv[3])

try:
    with open(resp_path) as f:
        d = json.load(f)
except Exception as e:
    print(json.dumps({"parse_ok": False, "error": str(e)}))
    sys.exit(0)

def safe_get(obj, *keys, default=None):
    cur = obj
    for k in keys:
        if isinstance(cur, dict):
            cur = cur.get(k)
        else:
            return default
        if cur is None:
            return default
    return cur

# AUDIT A · sentinels.flags présence
sent = d.get("sentinels", {})
flags = sent.get("flags", [])
active = sent.get("active_workers", [])
completed = sent.get("completed_workers", [])
audit_a = {
    "present": isinstance(sent, dict) and bool(sent),
    "flags_count": len(flags),
    "completed_count": sent.get("completed_count", 0),
    "active_count": sent.get("active_count", 0),
    "log_dir": sent.get("log_dir"),
}

# AUDIT B · watchdog_r4_features + bash_scripts.watchdog mtime
feats = d.get("watchdog_r4_features", {})
required_feats = [
    "has_r4_detect_and_mark_completed_workers",
    "has_r4_get_completed_indices",
    "has_skip_completed_in_missing",
    "has_r4_log_prefix",
    "has_effective_target_branch",
]
audit_b = {
    "present": isinstance(feats, dict) and bool(feats),
    "all_features_true": all(feats.get(k) is True for k in required_feats),
    "features": {k: feats.get(k) for k in required_feats},
    "watchdog_mtime_utc": safe_get(d, "bash_scripts", "watchdog", "mtime_utc"),
    "watchdog_size_bytes": safe_get(d, "bash_scripts", "watchdog", "size_bytes"),
}

# AUDIT C · API sentinels + skip_map structure
sm = safe_get(d, "watchdog", "skip_map", default={})
audit_c = {
    "sentinels_present": audit_a["present"],
    "skip_map_present": isinstance(sm, dict) and bool(sm),
    "target_workers": sm.get("target_workers"),
    "effective_target": sm.get("effective_target"),
    "skip_indices": sm.get("skip_indices", []),
    "respawn_target_indices": sm.get("respawn_target_indices", []),
}

# AUDIT D · Comportemental : respawn_targets vide ⇒ pas de respawn loop parasite
respawn_count = len(sm.get("respawn_target_indices", []))
audit_d = {
    "respawn_target_count": respawn_count,
    "no_respawn_loop": respawn_count == 0,
    "target_match_expected": sm.get("target_workers") == expected_target,
}

# AUDIT E · HRDEM ENV
ew = d.get("env_whitelist", {})
hrdem_vars = {
    "P1_MAX_SIZE_MB": ew.get("P1_MAX_SIZE_MB"),
    "P1_MAX_TILES": ew.get("P1_MAX_TILES"),
    "P1_TIMEOUT_S": ew.get("P1_TIMEOUT_S"),
    "INGESTION_P1_ARMED": ew.get("INGESTION_P1_ARMED"),
}
audit_e = {
    "hrdem_required": bool(require_hrdem),
    "vars": hrdem_vars,
    "all_set": all(v not in (None, "", "(UNSET)") for v in [hrdem_vars["P1_MAX_SIZE_MB"], hrdem_vars["P1_MAX_TILES"], hrdem_vars["P1_TIMEOUT_S"]]),
}

# Verdict global
critical_fail = (
    not audit_a["present"]
    or not audit_b["present"]
    or not audit_b["all_features_true"]
    or not audit_c["sentinels_present"]
    or not audit_c["skip_map_present"]
)
degraded = (
    not audit_d["no_respawn_loop"]
    or (require_hrdem and not audit_e["all_set"])
    or not audit_d["target_match_expected"]
)

report = {
    "parse_ok": True,
    "served_by": d.get("served_by"),
    "doctrine_backend": d.get("doctrine"),
    "checked_at_utc": d.get("checked_at_utc"),
    "hostname": ew.get("HOSTNAME"),
    "elapsed_ms": d.get("elapsed_ms"),
    "workers_count": d.get("workers_count"),
    "audit_a_filesystem": audit_a,
    "audit_b_watchdog_r4": audit_b,
    "audit_c_api_sentinels": audit_c,
    "audit_d_behavioral": audit_d,
    "audit_e_hrdem": audit_e,
    "verdict": {
        "critical_fail": critical_fail,
        "degraded": degraded,
        "pass": (not critical_fail) and (not degraded),
    },
}
print(json.dumps(report))
PYEOF
)

# ─── PARSE EXIT CODE ──────────────────────────────────────────────────────
if ! echo "$PARSE_REPORT" | python3 -c "import sys, json; json.loads(sys.stdin.read())" 2>/dev/null; then
    EXIT_CODE=4
    PARSE_ERROR="$PARSE_REPORT"
fi

PARSE_OK=$(echo "$PARSE_REPORT" | python3 -c "import sys, json; d=json.loads(sys.stdin.read()); print(d.get('parse_ok', False))" 2>/dev/null || echo "False")
if [[ "$PARSE_OK" != "True" ]] && [[ "$EXIT_CODE" -eq 0 ]]; then
    EXIT_CODE=4
fi

# Si HTTP OK et parse OK, calculer verdict
if [[ "$EXIT_CODE" -eq 0 ]] && [[ "$HTTP_CODE" == "200" ]]; then
    CRITICAL=$(echo "$PARSE_REPORT" | python3 -c "import sys, json; d=json.loads(sys.stdin.read()); print(d.get('verdict', {}).get('critical_fail', True))" 2>/dev/null || echo "True")
    DEGRADED=$(echo "$PARSE_REPORT" | python3 -c "import sys, json; d=json.loads(sys.stdin.read()); print(d.get('verdict', {}).get('degraded', True))" 2>/dev/null || echo "True")
    if [[ "$CRITICAL" == "True" ]]; then
        EXIT_CODE=1
    elif [[ "$DEGRADED" == "True" ]]; then
        EXIT_CODE=2
    fi
fi

# ─── SORTIE JSON (CI/CD mode) ─────────────────────────────────────────────
if [[ "$CANARY_OUTPUT" == "json" ]]; then
    FINAL_JSON=$(python3 - <<PYEOF
import json
try:
    inner = json.loads('''$PARSE_REPORT''')
except Exception:
    inner = {"parse_ok": False, "raw_parse_output": '''$PARSE_REPORT'''[:1000]}
out = {
    "canary_doctrine": "$DOCTRINE",
    "canary_started_at_utc": "$STARTED_AT_UTC",
    "canary_target_url": "$URL",
    "canary_timeout_s": $CANARY_TIMEOUT_S,
    "http_code": "$HTTP_CODE",
    "response_size_bytes": $RESP_SIZE,
    "exit_code": $EXIT_CODE,
    "report": inner,
}
print(json.dumps(out, indent=2))
PYEOF
)
    echo "$FINAL_JSON"
    [[ -n "$CANARY_LOG_FILE" ]] && echo "$FINAL_JSON" >> "$CANARY_LOG_FILE"
    exit $EXIT_CODE
fi

# ─── SORTIE TEXT (lecture humaine) ────────────────────────────────────────
echo ""
hdr "BCE-4X CANARY · DIAGNOSTIC ÉLITE"
echo "${C_DIM}doctrine    : $DOCTRINE"
echo "started_at  : $STARTED_AT_UTC"
echo "target      : $URL"
echo "timeout_s   : ${CANARY_TIMEOUT_S}${C_RESET}"
echo ""

hdr "RÉSEAU"
if [[ "$HTTP_CODE" == "200" ]]; then
    ok "HTTP $HTTP_CODE · size=${RESP_SIZE} bytes"
elif [[ "$HTTP_CODE" == "000" ]]; then
    fail "${NETWORK_ERROR:-network unreachable}"
else
    fail "HTTP $HTTP_CODE (expected 200)"
fi

if [[ "$EXIT_CODE" -ge 3 ]]; then
    echo ""
    fail "CANARY ABORTED · exit=$EXIT_CODE"
    exit $EXIT_CODE
fi

if [[ "$PARSE_OK" != "True" ]]; then
    echo ""
    fail "JSON parse failed"
    echo "${C_DIM}$PARSE_REPORT${C_RESET}" | head -5
    exit 4
fi

# Extraction parsée
EX() { echo "$PARSE_REPORT" | python3 -c "import sys, json; d=json.loads(sys.stdin.read()); v=d; [v:=v.get(k) for k in '$1'.split('.')]; print(v if v is not None else '(absent)')" 2>/dev/null; }

echo ""
hdr "AUDIT A · PREUVE FILESYSTEM (sentinels.flags)"
A_PRESENT=$(EX "audit_a_filesystem.present")
A_FLAGS=$(EX "audit_a_filesystem.flags_count")
A_COMPLETED=$(EX "audit_a_filesystem.completed_count")
A_ACTIVE=$(EX "audit_a_filesystem.active_count")
A_LOGDIR=$(EX "audit_a_filesystem.log_dir")
if [[ "$A_PRESENT" == "True" ]]; then ok "sentinels présent"; else fail "sentinels ABSENT (patch R4 non propagé)"; fi
info "flags_count      = $A_FLAGS"
info "completed_count  = $A_COMPLETED"
info "active_count     = $A_ACTIVE"
info "log_dir          = $A_LOGDIR"

echo ""
hdr "AUDIT B · PREUVE WATCHDOG R4 (script propagé)"
B_PRESENT=$(EX "audit_b_watchdog_r4.present")
B_ALL=$(EX "audit_b_watchdog_r4.all_features_true")
B_MTIME=$(EX "audit_b_watchdog_r4.watchdog_mtime_utc")
B_SIZE=$(EX "audit_b_watchdog_r4.watchdog_size_bytes")
if [[ "$B_PRESENT" == "True" ]]; then ok "watchdog_r4_features présent"; else fail "watchdog_r4_features ABSENT"; fi
if [[ "$B_ALL"     == "True" ]]; then ok "tous les 5 features R4 = true"; else fail "features R4 incomplets (patch partiellement propagé)"; fi
info "watchdog.mtime_utc  = $B_MTIME"
info "watchdog.size_bytes = $B_SIZE"

echo ""
hdr "AUDIT C · PREUVE API SENTINELS (champs structurés)"
C_SENT=$(EX "audit_c_api_sentinels.sentinels_present")
C_SM=$(EX "audit_c_api_sentinels.skip_map_present")
C_TARGET=$(EX "audit_c_api_sentinels.target_workers")
C_EFF=$(EX "audit_c_api_sentinels.effective_target")
C_SKIP=$(EX "audit_c_api_sentinels.skip_indices")
C_RESPAWN=$(EX "audit_c_api_sentinels.respawn_target_indices")
if [[ "$C_SENT" == "True" ]]; then ok "sentinels field structuré"; else fail "sentinels mal-formé"; fi
if [[ "$C_SM"   == "True" ]]; then ok "watchdog.skip_map structuré"; else fail "skip_map mal-formé"; fi
info "target_workers          = $C_TARGET (attendu=$CANARY_EXPECTED_TARGET)"
info "effective_target        = $C_EFF"
info "skip_indices            = $C_SKIP"
info "respawn_target_indices  = $C_RESPAWN"

echo ""
hdr "AUDIT D · COMPORTEMENTAL (no-respawn-loop)"
D_NORESPAWN=$(EX "audit_d_behavioral.no_respawn_loop")
D_TARGETMATCH=$(EX "audit_d_behavioral.target_match_expected")
D_RESPAWN_COUNT=$(EX "audit_d_behavioral.respawn_target_count")
if [[ "$D_NORESPAWN"   == "True" ]]; then ok "respawn_target_count=0 (pas de boucle parasite)"; else warn "respawn_target_count=$D_RESPAWN_COUNT (workers manquants détectés)"; fi
if [[ "$D_TARGETMATCH" == "True" ]]; then ok "target_workers = $CANARY_EXPECTED_TARGET (tier conforme)"; else warn "target_workers != $CANARY_EXPECTED_TARGET (vérifier tier ÉLITE)"; fi

echo ""
hdr "AUDIT E · HRDEM ENV PRODUCTION"
E_REQUIRED=$(EX "audit_e_hrdem.hrdem_required")
E_ALL=$(EX "audit_e_hrdem.all_set")
E_SIZE=$(EX "audit_e_hrdem.vars.P1_MAX_SIZE_MB")
E_TILES=$(EX "audit_e_hrdem.vars.P1_MAX_TILES")
E_TIMEOUT=$(EX "audit_e_hrdem.vars.P1_TIMEOUT_S")
E_ARMED=$(EX "audit_e_hrdem.vars.INGESTION_P1_ARMED")
if [[ "$E_REQUIRED" == "True" ]]; then
    if [[ "$E_ALL" == "True" ]]; then ok "HRDEM ENV injectés"; else warn "HRDEM ENV partiellement injectés"; fi
fi
info "P1_MAX_SIZE_MB     = $E_SIZE"
info "P1_MAX_TILES       = $E_TILES"
info "P1_TIMEOUT_S       = $E_TIMEOUT"
info "INGESTION_P1_ARMED = $E_ARMED"

echo ""
hdr "VERDICT KIMBERLITE"
case "$EXIT_CODE" in
    0) ok "${C_BOLD}PASS · R4 propagé · sentinels OK · skip_map OK · HRDEM OK${C_RESET}" ;;
    1) fail "${C_BOLD}CRITICAL · patch R4 non propagé ou sentinels absents${C_RESET}" ;;
    2) warn "${C_BOLD}DEGRADED · R4 OK mais HRDEM/respawn dégradés${C_RESET}" ;;
    3) fail "${C_BOLD}NETWORK ERROR · cible inatteignable${C_RESET}" ;;
    4) fail "${C_BOLD}INVALID JSON · réponse non parsable${C_RESET}" ;;
esac
info "exit_code = $EXIT_CODE"
echo ""

# ─── LOG FILE APPEND (si configuré) ───────────────────────────────────────
if [[ -n "$CANARY_LOG_FILE" ]]; then
    {
        echo "═══════════════════════════════════════════════════════════════"
        echo "CANARY $STARTED_AT_UTC · exit=$EXIT_CODE · http=$HTTP_CODE"
        echo "target: $URL"
        echo "$PARSE_REPORT" | python3 -m json.tool 2>/dev/null || echo "$PARSE_REPORT"
    } >> "$CANARY_LOG_FILE"
fi

exit $EXIT_CODE
