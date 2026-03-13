"""
STEVE-MAX++ Color Harmonization Test Suite
Tests for total color harmonization across all BIONIC components.

Test Coverage:
- bionicColorsConfig.js centralized colors (ZONE_COLORS)
- BionicZoneService.js LAYER_TYPES colors
- AnalysisSidePanel.jsx progress bar colors
- index.js BIONIC_LAYERS colors
- bionicDataAdapter.js NORM_COLORS
"""

import pytest
import requests
import os
import re

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Normative color palette (source of truth)
NORMATIVE_COLORS = {
    'habitats': '#10B981',
    'rut': '#FF4D6D',
    'repos': '#8B5CF6',
    'alimentation': '#22C55E',
    'corridors': '#06B6D4',
    'peuplements': '#15803D',
    'ndvi': '#66BB6A',
    'hydro': '#3B82F6',
    'pentes': '#FF7043',
    'orientation': '#2196F3',
    'ensoleillement': '#FCD34D',
    'salines': '#FFFF00',
    'affuts': '#F5A623',
    'trajets': '#FF9800',
    'altitude': '#78909C',
}


class TestBackendHealthAndEndpoints:
    """Backend health and BCE-4X endpoint tests"""
    
    def test_backend_health(self):
        """Backend should be healthy"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get('status') == 'healthy'
        print("✓ Backend healthy")
    
    def test_bce_validate_corridor_continuity(self):
        """BCE-4X validate-corridor-continuity endpoint works"""
        response = requests.post(
            f"{BASE_URL}/api/bce/validate-corridor-continuity",
            json={"corridors": []},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get('status') == 'PASS'
        assert 'BCE-4X-COR-006' in data.get('rule', '')
        print("✓ BCE-4X-COR-006 (corridor continuity) PASS")
    
    def test_bce_validate_visual_balance(self):
        """BCE-4X validate-visual-balance endpoint works"""
        response = requests.post(
            f"{BASE_URL}/api/bce/validate-visual-balance",
            json={"corridors": []},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get('status') == 'PASS'
        assert 'BCE-4X-VIS-007' in data.get('rule', '')
        print("✓ BCE-4X-VIS-007 (visual balance) PASS")
    
    def test_bce_validate_geometry_compliance(self):
        """BCE-4X validate-geometry-compliance endpoint works with +20% widths"""
        response = requests.post(
            f"{BASE_URL}/api/bce/validate-geometry-compliance",
            json={"corridors": []},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get('status') == 'PASS'
        
        # Check GEOM-005 specifically
        checks = data.get('checks', [])
        geom_005 = next((c for c in checks if 'GEOM-005' in c.get('name', '')), None)
        assert geom_005 is not None
        assert geom_005.get('status') == 'PASS'
        assert '+20%' in geom_005.get('detail', '')
        print("✓ BCE-4X-GEOM-005 (corridor width normalization) PASS with +20%")
    
    def test_bionic_engines_v2_status(self):
        """12 BIONIC engines should be active"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/engines-v2/status")
        assert response.status_code == 200
        data = response.json()
        assert data.get('engine_count') == 12
        
        engines = data.get('engines', [])
        for engine in engines:
            assert engine.get('status') == 'active'
        
        print(f"✓ 12 BIONIC V2 engines active: {[e['id'] for e in engines]}")


class TestFrontendColorHarmonization:
    """Frontend color file harmonization tests"""
    
    def test_bionic_colors_config_exists(self):
        """bionicColorsConfig.js should exist and contain ZONE_COLORS"""
        config_path = '/app/frontend/src/core/bionic/bionicColorsConfig.js'
        assert os.path.exists(config_path), f"bionicColorsConfig.js not found at {config_path}"
        
        with open(config_path, 'r') as f:
            content = f.read()
        
        assert 'ZONE_COLORS' in content
        assert 'FACTOR_COLORS' in content
        print("✓ bionicColorsConfig.js exists with ZONE_COLORS and FACTOR_COLORS")
    
    def test_bionic_colors_config_has_all_normative_colors(self):
        """bionicColorsConfig.js should have all 15 normative colors"""
        config_path = '/app/frontend/src/core/bionic/bionicColorsConfig.js'
        
        with open(config_path, 'r') as f:
            content = f.read()
        
        missing_colors = []
        for zone_id, expected_color in NORMATIVE_COLORS.items():
            # Look for zone_id: '#COLOR' pattern
            pattern = rf"{zone_id}:\s*['\"]({expected_color})['\"]"
            if not re.search(pattern, content, re.IGNORECASE):
                missing_colors.append(f"{zone_id}={expected_color}")
        
        assert len(missing_colors) == 0, f"Missing colors in bionicColorsConfig.js: {missing_colors}"
        print(f"✓ bionicColorsConfig.js contains all 15 normative colors")
    
    def test_layer_types_colors_in_bionic_zone_service(self):
        """BionicZoneService.js LAYER_TYPES should have correct colors"""
        service_path = '/app/frontend/src/services/BionicZoneService.js'
        
        with open(service_path, 'r') as f:
            content = f.read()
        
        # Key zones to verify
        key_zones = ['rut', 'salines', 'affuts', 'trajets', 'peuplements', 'pentes']
        missing = []
        
        for zone_id in key_zones:
            expected_color = NORMATIVE_COLORS[zone_id]
            # Pattern: id: 'zone_id', ... color: '#COLOR'
            if expected_color not in content:
                missing.append(f"{zone_id}={expected_color}")
        
        assert len(missing) == 0, f"Missing/wrong colors in BionicZoneService.js LAYER_TYPES: {missing}"
        print("✓ BionicZoneService.js LAYER_TYPES has correct normative colors")
    
    def test_analysis_side_panel_uses_zone_colors(self):
        """AnalysisSidePanel.jsx should import and use ZONE_COLORS"""
        panel_path = '/app/frontend/src/components/territoire/AnalysisSidePanel.jsx'
        
        with open(panel_path, 'r') as f:
            content = f.read()
        
        # Should import ZONE_COLORS from bionicColorsConfig
        assert 'ZONE_COLORS' in content, "AnalysisSidePanel should import ZONE_COLORS"
        assert 'bionicColorsConfig' in content, "AnalysisSidePanel should import from bionicColorsConfig"
        print("✓ AnalysisSidePanel.jsx imports and uses ZONE_COLORS from bionicColorsConfig")
    
    def test_bionic_layers_in_index_js(self):
        """index.js BIONIC_LAYERS should have harmonized colors"""
        index_path = '/app/frontend/src/core/bionic/index.js'
        
        with open(index_path, 'r') as f:
            content = f.read()
        
        # Verify key colors are present
        assert '#FF4D6D' in content, "index.js should have rut color #FF4D6D"
        assert '#FFFF00' in content, "index.js should have salines color #FFFF00"
        assert '#F5A623' in content, "index.js should have affuts color #F5A623"
        assert '#FF9800' in content, "index.js should have trajets color #FF9800"
        assert '#15803D' in content, "index.js should have peuplements color #15803D"
        assert '#FF7043' in content, "index.js should have pentes color #FF7043"
        print("✓ index.js BIONIC_LAYERS has harmonized normative colors")
    
    def test_bionic_data_adapter_norm_colors(self):
        """bionicDataAdapter.js should have NORM_COLORS matching normative palette"""
        adapter_path = '/app/frontend/src/core/bionic/bionicDataAdapter.js'
        
        with open(adapter_path, 'r') as f:
            content = f.read()
        
        # Should have NORM_COLORS object
        assert 'NORM_COLORS' in content, "bionicDataAdapter.js should have NORM_COLORS"
        assert '#FF4D6D' in content, "NORM_COLORS should have rut=#FF4D6D"
        assert '#FFFF00' in content, "NORM_COLORS should have salines=#FFFF00"
        print("✓ bionicDataAdapter.js NORM_COLORS has normative colors")
    
    def test_bionic_zone_diagnostic_panel_imports_factor_colors(self):
        """BionicZoneDiagnosticPanel.jsx should import colors from bionicColorsConfig"""
        panel_path = '/app/frontend/src/components/territoire/BionicZoneDiagnosticPanel.jsx'
        
        with open(panel_path, 'r') as f:
            content = f.read()
        
        # Should import from bionicColorsConfig
        assert 'bionicColorsConfig' in content, "BionicZoneDiagnosticPanel should import from bionicColorsConfig"
        assert 'FACTOR_COLORS' in content or 'ZONE_COLORS' in content, "Should use centralized color config"
        print("✓ BionicZoneDiagnosticPanel.jsx imports from bionicColorsConfig")
    
    def test_bionic_micro_zones_imports_zone_colors(self):
        """BionicMicroZones.jsx should import ZONE_COLORS from bionicColorsConfig"""
        micro_path = '/app/frontend/src/components/territoire/BionicMicroZones.jsx'
        
        with open(micro_path, 'r') as f:
            content = f.read()
        
        assert 'bionicColorsConfig' in content, "BionicMicroZones should import from bionicColorsConfig"
        assert 'ZONE_COLORS' in content, "BionicMicroZones should use ZONE_COLORS"
        print("✓ BionicMicroZones.jsx imports ZONE_COLORS from bionicColorsConfig")


class TestSpecificColorVerification:
    """Verify specific color requirements from the test plan"""
    
    def test_rut_is_pink_ff4d6d(self):
        """Zone de rut must be pink #FF4D6D across all files"""
        files_to_check = [
            '/app/frontend/src/core/bionic/bionicColorsConfig.js',
            '/app/frontend/src/services/BionicZoneService.js',
            '/app/frontend/src/core/bionic/index.js',
        ]
        
        for filepath in files_to_check:
            with open(filepath, 'r') as f:
                content = f.read().upper()
            assert '#FF4D6D' in content, f"rut color #FF4D6D not found in {filepath}"
        
        print("✓ Rut is pink #FF4D6D in all files")
    
    def test_trajets_is_orange_ff9800(self):
        """Trajets de chasse must be orange #FF9800"""
        files_to_check = [
            '/app/frontend/src/core/bionic/bionicColorsConfig.js',
            '/app/frontend/src/services/BionicZoneService.js',
        ]
        
        for filepath in files_to_check:
            with open(filepath, 'r') as f:
                content = f.read().upper()
            assert '#FF9800' in content, f"trajets color #FF9800 not found in {filepath}"
        
        print("✓ Trajets is orange #FF9800 in all files")
    
    def test_pentes_is_orange_ff7043(self):
        """Pentes must be orange #FF7043 (was gray before)"""
        files_to_check = [
            '/app/frontend/src/core/bionic/bionicColorsConfig.js',
            '/app/frontend/src/services/BionicZoneService.js',
        ]
        
        for filepath in files_to_check:
            with open(filepath, 'r') as f:
                content = f.read().upper()
            assert '#FF7043' in content, f"pentes color #FF7043 not found in {filepath}"
        
        print("✓ Pentes is orange #FF7043 (not gray)")
    
    def test_salines_is_yellow_ffff00(self):
        """Salines must be yellow #FFFF00"""
        files_to_check = [
            '/app/frontend/src/core/bionic/bionicColorsConfig.js',
            '/app/frontend/src/services/BionicZoneService.js',
        ]
        
        for filepath in files_to_check:
            with open(filepath, 'r') as f:
                content = f.read().upper()
            assert '#FFFF00' in content, f"salines color #FFFF00 not found in {filepath}"
        
        print("✓ Salines is yellow #FFFF00")
    
    def test_affuts_is_orange_f5a623(self):
        """Affuts must be orange #F5A623 (not blue)"""
        files_to_check = [
            '/app/frontend/src/core/bionic/bionicColorsConfig.js',
            '/app/frontend/src/services/BionicZoneService.js',
        ]
        
        for filepath in files_to_check:
            with open(filepath, 'r') as f:
                content = f.read().upper()
            assert '#F5A623' in content, f"affuts color #F5A623 not found in {filepath}"
        
        print("✓ Affuts is orange #F5A623 (not blue)")
    
    def test_peuplements_is_dark_green_15803d(self):
        """Peuplements must be dark green #15803D"""
        files_to_check = [
            '/app/frontend/src/core/bionic/bionicColorsConfig.js',
            '/app/frontend/src/services/BionicZoneService.js',
        ]
        
        for filepath in files_to_check:
            with open(filepath, 'r') as f:
                content = f.read().upper()
            assert '#15803D' in content, f"peuplements color #15803D not found in {filepath}"
        
        print("✓ Peuplements is dark green #15803D")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
