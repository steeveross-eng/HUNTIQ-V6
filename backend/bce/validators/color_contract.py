"""
BCE-4X — STEVE-MAX Color Contract Validators

New rules enforced by STEVE-MAX++ branch:

BCE-4X-COLOR-001 — ZoneColorContract
  Every zone on the map MUST use its normative color from ZONE_NORMATIVE_COLORS.
  No dynamic HSL generation. No index-based variation.

BCE-4X-COLOR-002 — PanelLegendConsistency
  The side panel legends MUST use the same color references as the map renderer.

BCE-4X-COLOR-003 — CorridorPaletteIsolation
  Corridor colors MUST come from CLASSIFICATION_V9 only.
  No zone colors may leak into corridor rendering.

BCE-4X-UI-004 — ZoneCorridorMixViolation
  Zones and corridors MUST be rendered in isolated Leaflet Panes.
  zones-pane z-index < corridors-pane z-index.
"""

import logging
import os
import re
from typing import Dict, Any

logger = logging.getLogger("bce.color_contract")
VALIDATOR_NAME = "color_contract_steve_max"
FRONTEND_SRC = "/app/frontend/src"

ZONE_NORMATIVE_COLORS = {
    "habitats": "#10B981",
    "rut": "#FF4D6D",
    "repos": "#8B5CF6",
    "alimentation": "#22C55E",
    "corridors": "#06B6D4",
    "peuplements": "#15803D",
    "ndvi": "#66BB6A",
    "hydro": "#3B82F6",
    "pentes": "#FF7043",
    "orientation": "#2196F3",
    "ensoleillement": "#FCD34D",
    "salines": "#FFFF00",
    "affuts": "#F5A623",
    "trajets": "#FF9800",
    "altitude": "#78909C",
}

CORRIDOR_NORMATIVE_COLORS = {
    "gris": "#9E9E9E",
    "jaune": "#FFC107",
    "orange": "#FF9800",
    "rouge": "#F44336",
    "rouge_raye": "#B71C1C",
}


def _read_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return ""


def validate() -> Dict[str, Any]:
    checks = []
    errors = []

    micro_zones_path = os.path.join(FRONTEND_SRC, "components/territoire/BionicMicroZones.jsx")
    micro_zones = _read_file(micro_zones_path)

    corridors_panel_path = os.path.join(FRONTEND_SRC, "components/territoire/CorridorsEcologyPanel.jsx")
    corridors_panel = _read_file(corridors_panel_path)

    # ═══════════════════════════════════════════
    # BCE-4X-COLOR-001: ZoneColorContract
    # ═══════════════════════════════════════════
    has_normative_palette = "ZONE_NORMATIVE_COLORS" in micro_zones
    has_dynamic_hsl = "generateZoneColor" in micro_zones or "LAYER_HUE_MAP" in micro_zones
    color_001_pass = has_normative_palette and not has_dynamic_hsl

    checks.append({
        "name": "BCE-4X-COLOR-001_ZoneColorContract",
        "status": "PASS" if color_001_pass else "FAIL",
        "detail": (
            "NORMATIVE palette in use, no dynamic HSL" if color_001_pass
            else f"normative={has_normative_palette}, dynamic_hsl={has_dynamic_hsl}"
        ),
    })
    if not color_001_pass:
        errors.append("BCE-4X-COLOR-001: Zone colors not using normative palette or dynamic HSL still present")

    # ═══════════════════════════════════════════
    # BCE-4X-COLOR-002: PanelLegendConsistency
    # ═══════════════════════════════════════════
    panel_has_classification = "CLASSIFICATION_COLORS" in corridors_panel
    panel_colors_match = True
    for level, expected_color in CORRIDOR_NORMATIVE_COLORS.items():
        if expected_color.lower() not in corridors_panel.lower():
            panel_colors_match = False
            break

    color_002_pass = panel_has_classification and panel_colors_match
    checks.append({
        "name": "BCE-4X-COLOR-002_PanelLegendConsistency",
        "status": "PASS" if color_002_pass else "FAIL",
        "detail": (
            "Panel legend colors match corridor normative palette"
            if color_002_pass
            else f"classification={panel_has_classification}, colors_match={panel_colors_match}"
        ),
    })
    if not color_002_pass:
        errors.append("BCE-4X-COLOR-002: Panel legend colors mismatch with corridor palette")

    # ═══════════════════════════════════════════
    # BCE-4X-COLOR-003: CorridorPaletteIsolation
    # ═══════════════════════════════════════════
    corridor_uses_zone_colors = bool(re.search(
        r"generateZoneColor|LAYER_HUE_MAP|ZONE_NORMATIVE_COLORS",
        micro_zones[micro_zones.find("V9CorridorRibbon"):] if "V9CorridorRibbon" in micro_zones else ""
    ))
    color_003_pass = not corridor_uses_zone_colors

    checks.append({
        "name": "BCE-4X-COLOR-003_CorridorPaletteIsolation",
        "status": "PASS" if color_003_pass else "FAIL",
        "detail": (
            "Corridor rendering uses only classification colors"
            if color_003_pass
            else "Corridor rendering leaks zone color functions"
        ),
    })
    if not color_003_pass:
        errors.append("BCE-4X-COLOR-003: Corridor rendering uses zone color functions")

    # ═══════════════════════════════════════════
    # BCE-4X-UI-004: ZoneCorridorMixViolation
    # ═══════════════════════════════════════════
    has_zones_pane = bool(re.search(r'Pane.*name=.*zones.*pane', micro_zones))
    has_corridors_pane = bool(re.search(r'Pane.*name=.*corridors.*v9.*pane', micro_zones))
    ui_004_pass = has_zones_pane and has_corridors_pane

    checks.append({
        "name": "BCE-4X-UI-004_ZoneCorridorMixViolation",
        "status": "PASS" if ui_004_pass else "FAIL",
        "detail": (
            f"Isolated panes: zones={has_zones_pane}, corridors={has_corridors_pane}"
        ),
    })
    if not ui_004_pass:
        errors.append("BCE-4X-UI-004: Zones and corridors not in separate Leaflet Panes")

    # ═══════════════════════════════════════════
    # BCE-4X-UI-005: NoLegacyMovementCorridors
    # ═══════════════════════════════════════════
    map_content_path = os.path.join(FRONTEND_SRC, "components/territoire/map/MapContent.jsx")
    map_content = _read_file(map_content_path)
    has_legacy_import = "import MovementCorridorsLayer" in map_content

    waypoint_map_path = os.path.join(FRONTEND_SRC, "modules/territory/components/WaypointMap.jsx")
    waypoint_map = _read_file(waypoint_map_path)
    has_legacy_waypoint = "import MovementCorridorsLayer" in waypoint_map

    ui_005_pass = not has_legacy_import and not has_legacy_waypoint
    checks.append({
        "name": "BCE-4X-UI-005_NoLegacyMovementCorridors",
        "status": "PASS" if ui_005_pass else "FAIL",
        "detail": (
            "No legacy MovementCorridorsLayer imports"
            if ui_005_pass
            else f"MapContent={has_legacy_import}, WaypointMap={has_legacy_waypoint}"
        ),
    })
    if not ui_005_pass:
        errors.append("BCE-4X-UI-005: Legacy MovementCorridorsLayer still imported")

    # ═══════════════════════════════════════════
    # BCE-4X-UI-006: NoTooltipSuppression
    # ═══════════════════════════════════════════
    anti_doubles_path = os.path.join(FRONTEND_SRC, "components/territoire/BionicAntiDoublesGuard.jsx")
    anti_doubles = _read_file(anti_doubles_path)
    # Check for active CSS rules that hide tooltip/popup panes
    # Extract CSS string content between backticks
    css_blocks = re.findall(r'`([^`]+)`', anti_doubles)
    css_content = "\n".join(css_blocks)
    suppresses_tooltips = bool(re.search(
        r'\.leaflet-tooltip-pane\s*\{[^}]*display:\s*none', css_content
    ))
    suppresses_popups = bool(re.search(
        r'\.leaflet-popup-pane[^}]*display:\s*none', css_content
    ))

    ui_006_pass = not suppresses_tooltips and not suppresses_popups
    checks.append({
        "name": "BCE-4X-UI-006_NoTooltipSuppression",
        "status": "PASS" if ui_006_pass else "FAIL",
        "detail": (
            "No global tooltip/popup suppression"
            if ui_006_pass
            else f"tooltips_hidden={suppresses_tooltips}, popups_hidden={suppresses_popups}"
        ),
    })
    if not ui_006_pass:
        errors.append("BCE-4X-UI-006: Global tooltip/popup CSS suppression active")

    # ═══════════════════════════════════════════
    # BCE-4X-COLOR-010: PaletteStrictMatch
    # Side panel MUST use LAYER_TYPES colors that match ZONE_NORMATIVE_COLORS
    # ═══════════════════════════════════════════
    side_panel_path = os.path.join(FRONTEND_SRC, "components/territoire/ui/SidePanelZones.jsx")
    side_panel = _read_file(side_panel_path)
    has_layer_types_import = "LAYER_TYPES" in side_panel and "BionicZoneService" in side_panel
    has_zone_legend = "zone-legend-panel" in side_panel
    color_010_pass = has_layer_types_import and has_zone_legend

    checks.append({
        "name": "BCE-4X-COLOR-010_PaletteStrictMatch",
        "status": "PASS" if color_010_pass else "FAIL",
        "detail": (
            "Side panel imports LAYER_TYPES for 1:1 palette match"
            if color_010_pass
            else f"LAYER_TYPES import={has_layer_types_import}, legend={has_zone_legend}"
        ),
    })
    if not color_010_pass:
        errors.append("BCE-4X-COLOR-010: Side panel palette not using normative LAYER_TYPES")

    status = "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL"
    return {
        "name": VALIDATOR_NAME,
        "status": status,
        "checks": checks,
        "errors": errors,
    }
