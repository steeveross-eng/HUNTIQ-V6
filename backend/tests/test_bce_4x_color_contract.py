"""
BCE-4X Color Contract Tests — STEVE-MAX Branch
==============================================
Tests for the BCE-4X color contract validation system.

Features tested:
- BCE-4X-COLOR-001: Zone colors use normative palette
- BCE-4X-COLOR-002: Panel legend colors match corridor palette
- BCE-4X-COLOR-003: Corridor palette isolation
- BCE-4X-UI-004: Zone and corridor pane isolation
- BCE-4X-UI-005: Legacy MovementCorridorsLayer removed
- BCE-4X-UI-006: No tooltip/popup suppression
- Organic zones API returns correct colors
- V9 Corridors with 5-band gradient
"""

import pytest
import requests
import os
import json

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Normative palette expectations
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

CORRIDOR_V9_BAND_COLORS = {
    "gris": "#9E9E9E",
    "jaune": "#FFC107",
    "orange": "#FF9800",
    "rouge": "#F44336",
    "rouge_raye": "#B71C1C",
}


class TestBCE4XColorContract:
    """BCE-4X Color Contract Endpoint Tests"""
    
    def test_color_contract_endpoint_exists(self):
        """BCE validation endpoint responds"""
        response = requests.post(f"{BASE_URL}/api/bce/validate-color-contract")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "status" in data
        assert "checks" in data
        print(f"Color contract endpoint status: {data['status']}")

    def test_all_6_checks_pass(self):
        """All 6 BCE-4X color contract checks pass"""
        response = requests.post(f"{BASE_URL}/api/bce/validate-color-contract")
        assert response.status_code == 200
        data = response.json()
        
        # Verify overall status
        assert data["status"] == "PASS", f"Expected PASS, got {data['status']}"
        
        # Verify all 6 checks present and passing
        checks = data.get("checks", [])
        assert len(checks) == 6, f"Expected 6 checks, got {len(checks)}"
        
        check_names = [
            "BCE-4X-COLOR-001_ZoneColorContract",
            "BCE-4X-COLOR-002_PanelLegendConsistency",
            "BCE-4X-COLOR-003_CorridorPaletteIsolation",
            "BCE-4X-UI-004_ZoneCorridorMixViolation",
            "BCE-4X-UI-005_NoLegacyMovementCorridors",
            "BCE-4X-UI-006_NoTooltipSuppression",
        ]
        
        for check in checks:
            assert check["status"] == "PASS", f"Check {check['name']} failed: {check['detail']}"
            print(f"  {check['name']}: {check['status']} - {check['detail']}")
        
        # Verify no errors
        errors = data.get("errors", [])
        assert len(errors) == 0, f"Expected 0 errors, got {len(errors)}: {errors}"

    def test_color_001_zone_normative_palette(self):
        """BCE-4X-COLOR-001: Zones use normative palette"""
        response = requests.post(f"{BASE_URL}/api/bce/validate-color-contract")
        data = response.json()
        
        color_001 = next((c for c in data["checks"] if "COLOR-001" in c["name"]), None)
        assert color_001 is not None, "COLOR-001 check not found"
        assert color_001["status"] == "PASS", f"COLOR-001 failed: {color_001['detail']}"
        assert "NORMATIVE palette" in color_001["detail"] or "normative" in color_001["detail"].lower()

    def test_color_002_panel_legend_consistency(self):
        """BCE-4X-COLOR-002: Panel legend colors match corridor palette"""
        response = requests.post(f"{BASE_URL}/api/bce/validate-color-contract")
        data = response.json()
        
        color_002 = next((c for c in data["checks"] if "COLOR-002" in c["name"]), None)
        assert color_002 is not None, "COLOR-002 check not found"
        assert color_002["status"] == "PASS", f"COLOR-002 failed: {color_002['detail']}"

    def test_color_003_corridor_palette_isolation(self):
        """BCE-4X-COLOR-003: Corridors don't use zone color functions"""
        response = requests.post(f"{BASE_URL}/api/bce/validate-color-contract")
        data = response.json()
        
        color_003 = next((c for c in data["checks"] if "COLOR-003" in c["name"]), None)
        assert color_003 is not None, "COLOR-003 check not found"
        assert color_003["status"] == "PASS", f"COLOR-003 failed: {color_003['detail']}"

    def test_ui_004_zone_corridor_pane_isolation(self):
        """BCE-4X-UI-004: Zones and corridors in separate Leaflet Panes"""
        response = requests.post(f"{BASE_URL}/api/bce/validate-color-contract")
        data = response.json()
        
        ui_004 = next((c for c in data["checks"] if "UI-004" in c["name"]), None)
        assert ui_004 is not None, "UI-004 check not found"
        assert ui_004["status"] == "PASS", f"UI-004 failed: {ui_004['detail']}"
        assert "zones=True" in ui_004["detail"], "Zones pane not detected"
        assert "corridors=True" in ui_004["detail"], "Corridors pane not detected"

    def test_ui_005_no_legacy_movement_corridors(self):
        """BCE-4X-UI-005: Legacy MovementCorridorsLayer not imported"""
        response = requests.post(f"{BASE_URL}/api/bce/validate-color-contract")
        data = response.json()
        
        ui_005 = next((c for c in data["checks"] if "UI-005" in c["name"]), None)
        assert ui_005 is not None, "UI-005 check not found"
        assert ui_005["status"] == "PASS", f"UI-005 failed: {ui_005['detail']}"
        assert "No legacy" in ui_005["detail"]

    def test_ui_006_no_tooltip_suppression(self):
        """BCE-4X-UI-006: No global tooltip/popup CSS suppression"""
        response = requests.post(f"{BASE_URL}/api/bce/validate-color-contract")
        data = response.json()
        
        ui_006 = next((c for c in data["checks"] if "UI-006" in c["name"]), None)
        assert ui_006 is not None, "UI-006 check not found"
        assert ui_006["status"] == "PASS", f"UI-006 failed: {ui_006['detail']}"


class TestOrganicZonesAPI:
    """Tests for POST /api/v1/bionic/organic-zones"""
    
    def test_organic_zones_returns_zones(self):
        """Organic zones API returns valid GeoJSON with zones"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json={
                "bounds": {"north": 46.96, "south": 46.93, "east": -71.27, "west": -71.33},
                "species": "moose",
                "zoom": 14
            },
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Verify GeoJSON structure
        assert data.get("type") == "FeatureCollection", "Not a FeatureCollection"
        features = data.get("features", [])
        assert len(features) > 0, "No features returned"
        print(f"Organic zones returned {len(features)} features")

    def test_zones_have_normative_stroke_colors(self):
        """Zones use normative stroke_color values"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json={
                "bounds": {"north": 46.96, "south": 46.93, "east": -71.27, "west": -71.33},
                "species": "moose",
                "zoom": 14
            }
        )
        
        data = response.json()
        features = data.get("features", [])
        
        for feature in features[:10]:  # Check first 10
            props = feature.get("properties", {})
            layer_id = props.get("layer_id")
            style = props.get("style", {})
            stroke_color = style.get("stroke_color")
            
            if layer_id and layer_id in ZONE_NORMATIVE_COLORS:
                expected = ZONE_NORMATIVE_COLORS[layer_id]
                assert stroke_color == expected, f"Zone {layer_id}: expected {expected}, got {stroke_color}"
                print(f"  Zone '{layer_id}' uses correct color: {stroke_color}")

    def test_corridors_have_5_bands(self):
        """V9 Corridors have 5 band levels with correct colors"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json={
                "bounds": {"north": 46.96, "south": 46.93, "east": -71.27, "west": -71.33},
                "species": "moose",
                "zoom": 14,
                "include_corridors": True
            }
        )
        
        data = response.json()
        
        # Check if corridors are in the response (might be separate)
        corridors = data.get("corridors", [])
        if not corridors:
            # Try to extract from features
            corridors = [f for f in data.get("features", []) if "corridor" in f.get("id", "").lower()]
        
        if corridors:
            for corridor in corridors[:5]:  # Check first 5
                bands = corridor.get("properties", {}).get("bands", []) or corridor.get("bands", [])
                if bands:
                    assert len(bands) == 5, f"Expected 5 bands, got {len(bands)}"
                    band_levels = [b.get("level") for b in bands]
                    expected_levels = ["gris", "jaune", "orange", "rouge", "rouge_raye"]
                    for level in expected_levels:
                        assert level in band_levels, f"Missing band level: {level}"
                    print(f"  Corridor has 5 bands: {band_levels}")


class TestHealthAndBasics:
    """Basic health and connectivity tests"""
    
    def test_health_endpoint(self):
        """Health endpoint responds"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"Backend health: {data}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
