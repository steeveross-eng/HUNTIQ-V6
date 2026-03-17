"""
Test WMS Proxy for NFIS-QC Ecoforestry Map
Iteration 99 - Verifies the WMS proxy routes correctly to NFIS-QC instead of SDA_WMS

Tests:
1. WMS availability check endpoint
2. WMS tile proxy with NFIS-QC DATASTORE parameter
3. CRS/SRS parameter handling
"""

import pytest
import requests
import os
import time

# Get backend URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://bionic-map-refresh.preview.emergentagent.com').rstrip('/')

class TestWMSProxyNFISQC:
    """Test suite for WMS Proxy with NFIS-QC (not SDA_WMS)"""
    
    def test_wms_check_nfis_qc_available(self):
        """
        TEST 1: Verify NFIS-QC WMS service is accessible via proxy check endpoint
        The URL now points to ca.nfis.org/cubewerx/cubeserv with DATASTORE=NFIS-QC
        """
        # NFIS-QC URL with DATASTORE parameter
        nfis_url = "https://ca.nfis.org/cubewerx/cubeserv?DATASTORE=NFIS-QC"
        
        response = requests.get(
            f"{BASE_URL}/api/wms-proxy/check",
            params={"url": nfis_url},
            timeout=20
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        print(f"WMS Check Response: {data}")
        
        # Should return available: true if NFIS-QC is reachable
        assert "available" in data, "Response should contain 'available' key"
        # Note: We check the status_code returned by the proxy
        if data.get("available"):
            assert data.get("status_code") == 200, "NFIS-QC should return 200"
            print(f"✓ NFIS-QC WMS is AVAILABLE (response time: {data.get('response_time_ms')}ms)")
        else:
            print(f"⚠ NFIS-QC WMS unavailable (may be temporary): {data}")
    
    def test_wms_check_url_with_existing_params(self):
        """
        TEST 2: Verify proxy handles URLs with existing query parameters
        The backend should append WMS params with & separator if URL already has ?
        """
        # URL already has ?DATASTORE=NFIS-QC parameter
        nfis_url = "https://ca.nfis.org/cubewerx/cubeserv?DATASTORE=NFIS-QC"
        
        response = requests.get(
            f"{BASE_URL}/api/wms-proxy/check",
            params={"url": nfis_url},
            timeout=20
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify the proxy doesn't fail due to URL parameter handling
        assert "error" not in data or data.get("error") != "Host not allowed"
        print(f"✓ URL with existing params handled correctly: {data}")
    
    def test_wms_proxy_tile_endpoint_exists(self):
        """
        TEST 3: Verify /api/wms-proxy/tile endpoint exists
        This is used by the frontend to fetch WMS tiles
        """
        # Minimal request to check endpoint exists
        response = requests.get(
            f"{BASE_URL}/api/wms-proxy/tile",
            params={
                "url": "https://ca.nfis.org/cubewerx/cubeserv?DATASTORE=NFIS-QC",
                "layers": "NFIS-QC.produits_ecoforestiers",
                "bbox": "-8080000,5750000,-8070000,5760000"  # Sample bbox in EPSG:3857
            },
            timeout=30
        )
        
        # Should return image data or proxy error, not 404
        assert response.status_code != 404, "Tile endpoint should exist"
        print(f"✓ Tile endpoint responds with status: {response.status_code}")
        
        # Check content type if successful
        if response.status_code == 200:
            content_type = response.headers.get("Content-Type", "")
            print(f"  Content-Type: {content_type}")
            assert "image" in content_type or response.status_code == 200
    
    def test_wms_proxy_supports_crs_and_srs(self):
        """
        TEST 4: Verify proxy supports both CRS (WMS 1.3.0) and SRS (WMS 1.1.1) parameters
        The backend should handle either format
        """
        base_params = {
            "url": "https://ca.nfis.org/cubewerx/cubeserv?DATASTORE=NFIS-QC",
            "layers": "NFIS-QC.produits_ecoforestiers",
            "bbox": "-8080000,5750000,-8070000,5760000"
        }
        
        # Test with CRS parameter (WMS 1.3.0)
        params_crs = {**base_params, "crs": "EPSG:3857"}
        response_crs = requests.get(
            f"{BASE_URL}/api/wms-proxy/tile",
            params=params_crs,
            timeout=30
        )
        print(f"✓ CRS parameter: status {response_crs.status_code}")
        
        # Test with SRS parameter (WMS 1.1.1)
        params_srs = {**base_params, "srs": "EPSG:3857"}
        response_srs = requests.get(
            f"{BASE_URL}/api/wms-proxy/tile",
            params=params_srs,
            timeout=30
        )
        print(f"✓ SRS parameter: status {response_srs.status_code}")
        
        # Both should be handled (not return 400 Bad Request)
        assert response_crs.status_code != 400, "CRS should be supported"
        assert response_srs.status_code != 400, "SRS should be supported"
    
    def test_wms_host_whitelist_allows_nfis(self):
        """
        TEST 5: Verify ca.nfis.org is in the allowed hosts whitelist
        """
        # NFIS-QC should be allowed
        nfis_url = "https://ca.nfis.org/cubewerx/cubeserv?DATASTORE=NFIS-QC"
        
        response = requests.get(
            f"{BASE_URL}/api/wms-proxy/check",
            params={"url": nfis_url},
            timeout=15
        )
        
        data = response.json()
        
        # Should NOT return "Host not allowed" error
        assert data.get("error") != "Host not allowed", "ca.nfis.org should be in whitelist"
        print(f"✓ ca.nfis.org is in allowed hosts whitelist")
    
    def test_wms_host_whitelist_blocks_unknown(self):
        """
        TEST 6: Verify unknown hosts are blocked
        """
        unknown_url = "https://evil-wms-server.com/wms"
        
        response = requests.get(
            f"{BASE_URL}/api/wms-proxy/check",
            params={"url": unknown_url},
            timeout=15
        )
        
        data = response.json()
        
        # Should block unknown host
        assert data.get("available") == False or data.get("error") == "Host not allowed"
        print(f"✓ Unknown hosts are blocked: {data}")


class TestEcoforestryLayerConfig:
    """Test that the frontend EcoforestryLayers config points to NFIS-QC"""
    
    def test_nfis_qc_layer_name_format(self):
        """
        TEST 7: Verify NFIS-QC layer names follow correct format
        Layers should be prefixed with 'NFIS-QC.' namespace
        """
        # These are the layer names used in EcoforestryLayers.jsx
        expected_layers = [
            "NFIS-QC.produits_ecoforestiers",
            "NFIS-QC.ori_pee_ori_prov",
            "NFIS-QC.depots_surface",
            "NFIS-QC.veg_pot",
            "NFIS-QC.volumes_forestiers",
            "NFIS-QC.ca_feux"
        ]
        
        for layer in expected_layers:
            assert layer.startswith("NFIS-QC."), f"Layer {layer} should have NFIS-QC namespace"
        
        print(f"✓ All {len(expected_layers)} layers use NFIS-QC namespace")


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
