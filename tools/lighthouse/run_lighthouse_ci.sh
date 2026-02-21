#!/bin/bash
# HUNTIQ-V5 Lighthouse CI Audit Script
# MODE: STAGING (INTERNAL_ONLY=TRUE)
# Version: L1

set -e

# Configuration
BASE_URL="${1:-https://contour-mapper-2.preview.emergentagent.com}"
OUTPUT_DIR="/app/docs/reports/lighthouse"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Pages à auditer
declare -A PAGES=(
    ["home"]="/"
    ["mon_territoire"]="/mon-territoire"
    ["carte_interactive"]="/carte-interactive"
    ["contenus"]="/contenus"
    ["login"]="/login"
    ["shop"]="/shop"
)

# Créer le répertoire de sortie
mkdir -p "$OUTPUT_DIR"

echo "=========================================="
echo "HUNTIQ-V5 LIGHTHOUSE CI AUDIT"
echo "Mode: STAGING (INTERNAL_ONLY=TRUE)"
echo "Base URL: $BASE_URL"
echo "Timestamp: $TIMESTAMP"
echo "=========================================="

# Fonction d'audit
run_audit() {
    local page_name=$1
    local page_path=$2
    local device=$3
    local url="${BASE_URL}${page_path}"
    local output_file="${OUTPUT_DIR}/lighthouse_${page_name}_${device}.json"
    
    echo ""
    echo ">>> Auditing: $page_name ($device) - $url"
    
    local chrome_flags="--headless --no-sandbox --disable-gpu --disable-dev-shm-usage"
    local preset=""
    
    if [ "$device" == "mobile" ]; then
        preset="--preset=perf --emulated-form-factor=mobile --throttling-method=simulate"
    else
        preset="--preset=desktop --emulated-form-factor=desktop --throttling-method=simulate"
    fi
    
    lighthouse "$url" \
        --output=json \
        --output-path="$output_file" \
        --chrome-flags="$chrome_flags" \
        --only-categories=performance,accessibility,best-practices,seo \
        --quiet \
        $preset \
        2>/dev/null || echo "Warning: Audit for $page_name ($device) may have issues"
    
    if [ -f "$output_file" ]; then
        echo "    Output: $output_file"
    fi
}

# Exécuter les audits pour chaque page (desktop uniquement pour le CI initial)
for page_name in "${!PAGES[@]}"; do
    page_path="${PAGES[$page_name]}"
    run_audit "$page_name" "$page_path" "desktop"
done

echo ""
echo "=========================================="
echo "LIGHTHOUSE AUDITS COMPLETED"
echo "Reports saved to: $OUTPUT_DIR"
echo "=========================================="

# Lister les fichiers générés
ls -la "$OUTPUT_DIR"/*.json 2>/dev/null || echo "No JSON reports found"
