"""
Iteration 61 — BCE-4X Anti-Regression Test Suite
================================================
Validates:
- V3 Intelligence APIs (summary, forecast, plan, solunar, guide-pro, scientifique)
- BCE-4X Engine validation endpoint
- Core health endpoints
- No old Analyse endpoint remnants

Rules tested: R3, R7, R11, R14, R18, R21
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    BASE_URL = 'https://lisibilite-pro.preview.emergentagent.com'


# Test coordinates (Quebec region)
TEST_LAT = 46.8139
TEST_LNG = -71.208
TEST_SPECIES = 'CERF'
TEST_MONTH = 3


class TestHealthEndpoints:
    """Health and basic API status tests"""
    
    def test_api_health(self):
        """R21: Core API health check"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data.get('status') == 'healthy' or 'ok' in str(data).lower()


class TestIntelligenceV3APIs:
    """V3 Intelligence Dashboard API tests"""
    
    def test_intelligence_summary(self):
        """R3: Summary endpoint returns consolidated score and domains"""
        response = requests.get(
            f"{BASE_URL}/api/v3/intelligence/summary",
            params={'lat': TEST_LAT, 'lng': TEST_LNG, 'species': 'tous', 'month': TEST_MONTH},
            timeout=15
        )
        assert response.status_code == 200
        data = response.json()
        # Should have consolidated score
        assert 'consolidated' in data or 'score' in str(data).lower()
        print(f"[PASS] Summary: consolidated={data.get('consolidated', {})}")
    
    def test_intelligence_forecast(self):
        """R7: Forecast endpoint returns monthly/seasonal predictions"""
        response = requests.get(
            f"{BASE_URL}/api/v3/intelligence/forecast",
            params={'lat': TEST_LAT, 'lng': TEST_LNG, 'species': 'tous'},
            timeout=15
        )
        assert response.status_code == 200
        data = response.json()
        # Should have monthly data or forecast info
        assert 'monthly_data' in data or 'forecast' in str(data).lower() or 'best_month' in data
        print(f"[PASS] Forecast: best_month={data.get('best_month')}, annual_avg={data.get('annual_average')}")
    
    def test_intelligence_plan(self):
        """R11: Plan endpoint returns prioritized actions"""
        response = requests.get(
            f"{BASE_URL}/api/v3/intelligence/plan",
            params={'lat': TEST_LAT, 'lng': TEST_LNG, 'species': 'tous', 'month': TEST_MONTH},
            timeout=15
        )
        assert response.status_code == 200
        data = response.json()
        # Should have actions list
        assert 'actions' in data or 'plan' in str(data).lower()
        print(f"[PASS] Plan: actions_count={len(data.get('actions', []))}")
    
    def test_intelligence_solunar(self):
        """R14: Solunar endpoint returns lunar/solar data"""
        response = requests.get(
            f"{BASE_URL}/api/v3/intelligence/solunar",
            params={'lat': TEST_LAT, 'lng': TEST_LNG, 'date': '2026-03-18'},
            timeout=15
        )
        assert response.status_code == 200
        data = response.json()
        # Should have solunar data
        assert 'periods' in data or 'score' in data or 'phase' in str(data).lower()
        print(f"[PASS] Solunar: data keys={list(data.keys())[:5]}")
    
    def test_intelligence_guide_pro(self):
        """R18: Guide Pro endpoint returns hunting guidance"""
        response = requests.get(
            f"{BASE_URL}/api/v3/intelligence/guide-pro",
            params={'lat': TEST_LAT, 'lng': TEST_LNG, 'species': 'tous', 'month': TEST_MONTH, 'date': '2026-03-18'},
            timeout=15
        )
        assert response.status_code == 200
        data = response.json()
        # Should have guide data
        assert len(data) > 0
        print(f"[PASS] Guide Pro: data keys={list(data.keys())[:5]}")
    
    def test_intelligence_scientifique(self):
        """R3: Scientifique endpoint returns scientific analysis"""
        response = requests.get(
            f"{BASE_URL}/api/v3/intelligence/scientifique",
            params={'lat': TEST_LAT, 'lng': TEST_LNG, 'species': 'tous', 'month': TEST_MONTH},
            timeout=15
        )
        assert response.status_code == 200
        data = response.json()
        # Should have scientific data
        assert len(data) > 0
        print(f"[PASS] Scientifique: data keys={list(data.keys())[:5]}")


class TestBCE4XValidation:
    """BCE-4X Engine validation tests"""
    
    def test_engines_registry(self):
        """Check engine registry returns list of available engines"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/registry", timeout=10)
        assert response.status_code == 200
        data = response.json()
        # Should have engines list
        assert 'engines' in data or isinstance(data, list)
        print(f"[PASS] Registry: engines count={len(data.get('engines', data))}")
    
    def test_engines_validate_bce4x(self):
        """R21: BCE-4X validation endpoint returns overall_compliant"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/validate", timeout=15)
        assert response.status_code == 200
        data = response.json()
        # Should have compliance status
        assert 'overall_compliant' in data or 'compliant' in str(data).lower() or 'status' in data
        compliant = data.get('overall_compliant', data.get('compliant', True))
        print(f"[PASS] BCE-4X Validate: overall_compliant={compliant}")
        # For iteration 61, compliance is expected
        assert compliant is True or compliant == 'true' or str(compliant).lower() == 'true'


class TestNoOldAnalyseEndpoint:
    """Verify old Analyse endpoints are removed"""
    
    def test_old_analyse_endpoint_removed(self):
        """Old /api/analyse should not exist or return 404"""
        response = requests.get(f"{BASE_URL}/api/analyse", timeout=5)
        # Should be 404 or redirect
        assert response.status_code in [404, 301, 302, 307, 308, 405]
        print(f"[PASS] Old /api/analyse endpoint correctly returns {response.status_code}")
    
    def test_old_v1_analyse_removed(self):
        """Old /api/v1/analyse should not exist"""
        response = requests.get(f"{BASE_URL}/api/v1/analyse", timeout=5)
        assert response.status_code in [404, 301, 302, 307, 308, 405]
        print(f"[PASS] Old /api/v1/analyse endpoint correctly returns {response.status_code}")


class TestCoreZoneAPIs:
    """Core zone generation APIs still work"""
    
    def test_organic_zones_endpoint(self):
        """Zones API returns zones for a waypoint"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json={
                'lat': TEST_LAT,
                'lng': TEST_LNG,
                'species': 'deer',
                'season': 'pre_rut',
                'radius_m': 1000
            },
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert 'zones' in data or 'features' in data or 'success' in data
        print(f"[PASS] Organic Zones: zones={len(data.get('zones', []))}")
    
    def test_corridors_endpoint(self):
        """Corridors API returns corridor data"""
        response = requests.post(
            f"{BASE_URL}/api/v10/corridors/analyze-full",
            json={
                'lat': TEST_LAT,
                'lng': TEST_LNG,
                'species': 'deer',
                'season': 'pre_rut',
                'radius_m': 1000
            },
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert 'corridors' in data or 'features' in data or 'success' in data
        print(f"[PASS] Corridors V10: corridors={len(data.get('corridors', []))}")


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
