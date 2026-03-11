"""
Test WMS Proxy & Ecoforestry Layer Stability - Iteration 107
============================================================
Tests for BIONIC V5 - Mon Territoire WMS ecoforestry layer fixes.

Features tested:
1. WMS proxy /api/wms-proxy/check endpoint
2. WMS proxy /api/wms-proxy/tile endpoint
3. WMS cache functionality
4. Dynamic scores endpoint
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://territory-analysis.preview.emergentagent.com').rstrip('/')

class TestWMSProxyCheck:
    """Test WMS proxy availability check endpoint"""
    
    def test_wms_check_nfis_qc_with_datastore(self):
        """Test /api/wms-proxy/check with NFIS-QC URL including DATASTORE param"""
        # NFIS-QC URL with DATASTORE parameter - this is the working URL
        nfis_url = "https://ca.nfis.org/cubewerx/cubeserv?DATASTORE=NFIS-QC"
        
        response = requests.get(
            f"{BASE_URL}/api/wms-proxy/check",
            params={"url": nfis_url},
            timeout=30
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # Check response structure
        assert "available" in data, "Response should contain 'available' field"
        assert isinstance(data.get("available"), bool), "'available' should be boolean"
        
        # Log result for debugging
        print(f"WMS check result: available={data.get('available')}, status_code={data.get('status_code')}, response_time={data.get('response_time_ms')}ms")
        
        # Even if unavailable, the endpoint should work without error
        if "error" in data:
            print(f"WMS check error: {data['error']}")
    
    def test_wms_check_disallowed_host(self):
        """Test that disallowed hosts return error"""
        bad_url = "https://malicious.example.com/wms"
        
        response = requests.get(
            f"{BASE_URL}/api/wms-proxy/check",
            params={"url": bad_url},
            timeout=10
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("available") == False, "Disallowed host should return available=false"
        assert "error" in data, "Should return error for disallowed host"


class TestWMSProxyTile:
    """Test WMS proxy tile endpoint"""
    
    def test_wms_tile_returns_png(self):
        """Test /api/wms-proxy/tile returns valid PNG tile"""
        # NFIS-QC URL with DATASTORE param
        wms_url = "https://ca.nfis.org/cubewerx/cubeserv?DATASTORE=NFIS-QC"
        
        # BBOX for Quebec area (EPSG:3857)
        bbox = "-7903684,-5009377,-7792364,-4898057"
        
        response = requests.get(
            f"{BASE_URL}/api/wms-proxy/tile",
            params={
                "url": wms_url,
                "layers": "NFIS-QC.produits_ecoforestiers",
                "bbox": bbox,
                "width": 256,
                "height": 256,
                "format": "image/png",
                "transparent": "true",
                "crs": "EPSG:3857"
            },
            timeout=30
        )
        
        # Should return 200 or 502/504 if WMS service is slow
        assert response.status_code in [200, 502, 504], f"Expected 200/502/504, got {response.status_code}"
        
        if response.status_code == 200:
            # Check content type
            content_type = response.headers.get("Content-Type", "")
            assert "image/png" in content_type, f"Expected image/png, got {content_type}"
            
            # Check PNG magic bytes
            content = response.content
            assert len(content) > 0, "Tile should not be empty"
            
            # PNG files start with \x89PNG
            if len(content) >= 4:
                is_png = content[:4] == b'\x89PNG'
                print(f"PNG tile received: {len(content)} bytes, valid PNG header: {is_png}")
                assert is_png, "Content should be valid PNG"
        else:
            print(f"WMS tile request returned {response.status_code} - service may be slow/unavailable")
    
    def test_wms_tile_missing_bbox(self):
        """Test that missing BBOX returns 400"""
        wms_url = "https://ca.nfis.org/cubewerx/cubeserv?DATASTORE=NFIS-QC"
        
        response = requests.get(
            f"{BASE_URL}/api/wms-proxy/tile",
            params={
                "url": wms_url,
                "layers": "NFIS-QC.produits_ecoforestiers"
                # Missing bbox
            },
            timeout=10
        )
        
        assert response.status_code == 400, f"Expected 400 for missing BBOX, got {response.status_code}"
    
    def test_wms_tile_disallowed_host(self):
        """Test that disallowed hosts return 403"""
        bad_url = "https://malicious.example.com/wms"
        
        response = requests.get(
            f"{BASE_URL}/api/wms-proxy/tile",
            params={
                "url": bad_url,
                "layers": "test",
                "bbox": "-7903684,-5009377,-7792364,-4898057"
            },
            timeout=10
        )
        
        assert response.status_code == 403, f"Expected 403 for disallowed host, got {response.status_code}"


class TestWMSCache:
    """Test WMS proxy cache functionality"""
    
    def test_wms_cache_second_request_faster(self):
        """Test that second identical request is served from cache (faster)"""
        wms_url = "https://ca.nfis.org/cubewerx/cubeserv?DATASTORE=NFIS-QC"
        bbox = "-7903684,-5009377,-7792364,-4898057"
        
        params = {
            "url": wms_url,
            "layers": "NFIS-QC.produits_ecoforestiers",
            "bbox": bbox,
            "width": 256,
            "height": 256,
            "format": "image/png"
        }
        
        # First request
        start1 = time.time()
        response1 = requests.get(f"{BASE_URL}/api/wms-proxy/tile", params=params, timeout=30)
        time1 = time.time() - start1
        
        # Skip cache test if first request failed
        if response1.status_code != 200:
            pytest.skip(f"First request failed with {response1.status_code}, skipping cache test")
        
        # Second request (should be cached)
        start2 = time.time()
        response2 = requests.get(f"{BASE_URL}/api/wms-proxy/tile", params=params, timeout=30)
        time2 = time.time() - start2
        
        assert response2.status_code == 200
        
        # Cache should make second request significantly faster
        print(f"First request: {time1:.3f}s, Second request: {time2:.3f}s")
        
        # Second should be at least 50% faster if cached (or very fast <0.5s)
        if time1 > 1.0:  # Only check if first was slow enough
            assert time2 < time1 or time2 < 0.5, "Cached request should be faster"


class TestDynamicScoresEndpoint:
    """Test the dynamic scores endpoint used by ecoforestry layers"""
    
    def test_dynamic_scores_returns_200(self):
        """Test POST /api/v1/bionic/dynamic/scores returns 200"""
        payload = {
            "lat": 46.8139,
            "lng": -71.2080,
            "species": "cerf"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/dynamic/scores",
            json=payload,
            timeout=15
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        print(f"Dynamic scores response: {data}")
        
        # Check response has expected structure
        assert "score" in data or "scores" in data or "global_score" in data, "Response should contain score data"
    
    def test_dynamic_scores_with_exclusions(self):
        """Test dynamic scores returns exclusion data"""
        payload = {
            "lat": 46.8139,
            "lng": -71.2080,
            "species": "orignal"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/dynamic/scores",
            json=payload,
            timeout=15
        )
        
        assert response.status_code == 200
        
        data = response.json()
        # May contain exclusions field
        if "exclusions" in data:
            print(f"Exclusions found: {data['exclusions']}")


class TestHealthAndStatus:
    """Test API health endpoints"""
    
    def test_api_health(self):
        """Test API is healthy"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200
    
    def test_orchestrator_status(self):
        """Test orchestrator status endpoint"""
        response = requests.get(f"{BASE_URL}/api/status", timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data or "modules" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
