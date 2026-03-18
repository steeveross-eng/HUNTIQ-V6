"""
ALIMENTATION-V2 Species-Specific Salines Tests
=================================================
Test directive: OURS and DINDON species must NOT generate salines.
CHEVREUIL, ORIGNAL, WAPITI should generate salines normally.

Frontend species IDs mapping:
  chevreuil → CERF
  orignal → ORIGNAL
  ours_noir → OURS
  dindon_sauvage → DINDON
  wapiti → WAPITI
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


@pytest.fixture
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


class TestSpeciesNoSalines:
    """Test OURS and DINDON species return salines_disabled=true and empty salines array"""

    def test_ours_noir_no_salines(self, api_client):
        """OURS NOIR (ours_noir) should NOT generate salines"""
        response = api_client.post(f"{BASE_URL}/api/v2/alimentation/analyze", json={
            "center_lat": 46.8139,
            "center_lng": -71.2080,
            "species": "ours_noir",  # Frontend ID
            "month": 10
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify salines_disabled flag
        assert data.get("salines_disabled") is True, f"Expected salines_disabled=True for OURS, got {data.get('salines_disabled')}"
        
        # Verify empty salines array
        assert data.get("n_salines") == 0, f"Expected n_salines=0 for OURS, got {data.get('n_salines')}"
        assert data.get("salines") == [], f"Expected empty salines array for OURS, got {data.get('salines')}"
        
        # Verify explanatory message exists
        assert data.get("salines_message") is not None, "Expected salines_message for OURS"
        assert "ours" in data.get("salines_message", "").lower(), f"Message should mention ours: {data.get('salines_message')}"
        
        # Verify species resolved correctly
        assert data.get("species") == "OURS", f"Expected species=OURS, got {data.get('species')}"
        
        print(f"[PASS] ours_noir: salines_disabled={data['salines_disabled']}, n_salines={data['n_salines']}, message='{data['salines_message'][:50]}...'")

    def test_dindon_sauvage_no_salines(self, api_client):
        """DINDON SAUVAGE (dindon_sauvage) should NOT generate salines"""
        response = api_client.post(f"{BASE_URL}/api/v2/alimentation/analyze", json={
            "center_lat": 46.8139,
            "center_lng": -71.2080,
            "species": "dindon_sauvage",  # Frontend ID
            "month": 10
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify salines_disabled flag
        assert data.get("salines_disabled") is True, f"Expected salines_disabled=True for DINDON, got {data.get('salines_disabled')}"
        
        # Verify empty salines array
        assert data.get("n_salines") == 0, f"Expected n_salines=0 for DINDON, got {data.get('n_salines')}"
        assert data.get("salines") == [], f"Expected empty salines array for DINDON, got {data.get('salines')}"
        
        # Verify explanatory message exists
        assert data.get("salines_message") is not None, "Expected salines_message for DINDON"
        assert "dindon" in data.get("salines_message", "").lower(), f"Message should mention dindon: {data.get('salines_message')}"
        
        # Verify species resolved correctly
        assert data.get("species") == "DINDON", f"Expected species=DINDON, got {data.get('species')}"
        
        print(f"[PASS] dindon_sauvage: salines_disabled={data['salines_disabled']}, n_salines={data['n_salines']}, message='{data['salines_message'][:50]}...'")

    def test_ours_backend_id_no_salines(self, api_client):
        """Direct backend ID 'OURS' should also NOT generate salines"""
        response = api_client.post(f"{BASE_URL}/api/v2/alimentation/analyze", json={
            "center_lat": 46.8139,
            "center_lng": -71.2080,
            "species": "OURS",  # Backend ID directly
            "month": 10
        })
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("salines_disabled") is True, f"Expected salines_disabled=True for OURS, got {data.get('salines_disabled')}"
        assert data.get("n_salines") == 0, f"Expected n_salines=0 for OURS, got {data.get('n_salines')}"
        
        print(f"[PASS] OURS (backend ID): salines_disabled={data['salines_disabled']}")

    def test_dindon_backend_id_no_salines(self, api_client):
        """Direct backend ID 'DINDON' should also NOT generate salines"""
        response = api_client.post(f"{BASE_URL}/api/v2/alimentation/analyze", json={
            "center_lat": 46.8139,
            "center_lng": -71.2080,
            "species": "DINDON",  # Backend ID directly
            "month": 10
        })
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("salines_disabled") is True, f"Expected salines_disabled=True for DINDON, got {data.get('salines_disabled')}"
        assert data.get("n_salines") == 0, f"Expected n_salines=0 for DINDON, got {data.get('n_salines')}"
        
        print(f"[PASS] DINDON (backend ID): salines_disabled={data['salines_disabled']}")


class TestSpeciesWithSalines:
    """Test CHEVREUIL, ORIGNAL, WAPITI species generate salines normally"""

    def test_chevreuil_generates_salines(self, api_client):
        """CHEVREUIL should generate salines (salines_disabled=false, n_salines>0)"""
        response = api_client.post(f"{BASE_URL}/api/v2/alimentation/analyze", json={
            "center_lat": 46.8139,
            "center_lng": -71.2080,
            "species": "chevreuil",  # Frontend ID → CERF
            "month": 10
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify salines_disabled is False
        assert data.get("salines_disabled") is False, f"Expected salines_disabled=False for CHEVREUIL, got {data.get('salines_disabled')}"
        
        # Verify salines are generated
        assert data.get("n_salines", 0) > 0, f"Expected n_salines>0 for CHEVREUIL, got {data.get('n_salines')}"
        assert len(data.get("salines", [])) > 0, f"Expected non-empty salines array for CHEVREUIL"
        
        # Verify no salines_message (or null)
        assert data.get("salines_message") is None, f"Expected no salines_message for CHEVREUIL, got {data.get('salines_message')}"
        
        # Verify species resolved correctly
        assert data.get("species") == "CERF", f"Expected species=CERF for chevreuil, got {data.get('species')}"
        
        print(f"[PASS] chevreuil: salines_disabled={data['salines_disabled']}, n_salines={data['n_salines']}")

    def test_orignal_generates_salines(self, api_client):
        """ORIGNAL should generate salines normally"""
        response = api_client.post(f"{BASE_URL}/api/v2/alimentation/analyze", json={
            "center_lat": 46.8139,
            "center_lng": -71.2080,
            "species": "orignal",  # Frontend ID → ORIGNAL
            "month": 10
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        assert data.get("salines_disabled") is False, f"Expected salines_disabled=False for ORIGNAL, got {data.get('salines_disabled')}"
        assert data.get("n_salines", 0) > 0, f"Expected n_salines>0 for ORIGNAL, got {data.get('n_salines')}"
        assert data.get("species") == "ORIGNAL", f"Expected species=ORIGNAL, got {data.get('species')}"
        
        print(f"[PASS] orignal: salines_disabled={data['salines_disabled']}, n_salines={data['n_salines']}")

    def test_wapiti_generates_salines(self, api_client):
        """WAPITI should generate salines normally"""
        response = api_client.post(f"{BASE_URL}/api/v2/alimentation/analyze", json={
            "center_lat": 46.8139,
            "center_lng": -71.2080,
            "species": "wapiti",  # Frontend ID → WAPITI
            "month": 10
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        assert data.get("salines_disabled") is False, f"Expected salines_disabled=False for WAPITI, got {data.get('salines_disabled')}"
        assert data.get("n_salines", 0) > 0, f"Expected n_salines>0 for WAPITI, got {data.get('n_salines')}"
        assert data.get("species") == "WAPITI", f"Expected species=WAPITI, got {data.get('species')}"
        
        print(f"[PASS] wapiti: salines_disabled={data['salines_disabled']}, n_salines={data['n_salines']}")

    def test_tous_defaults_to_cerf_with_salines(self, api_client):
        """'tous' species ID should default to CERF and generate salines"""
        response = api_client.post(f"{BASE_URL}/api/v2/alimentation/analyze", json={
            "center_lat": 46.8139,
            "center_lng": -71.2080,
            "species": "tous",  # Frontend ID → CERF (default)
            "month": 10
        })
        assert response.status_code == 200
        
        data = response.json()
        
        assert data.get("salines_disabled") is False, f"Expected salines_disabled=False for 'tous', got {data.get('salines_disabled')}"
        assert data.get("n_salines", 0) > 0, f"Expected n_salines>0 for 'tous', got {data.get('n_salines')}"
        assert data.get("species") == "CERF", f"Expected species=CERF for 'tous', got {data.get('species')}"
        
        print(f"[PASS] tous: salines_disabled={data['salines_disabled']}, n_salines={data['n_salines']}")


class TestSpeciesMapping:
    """Test frontend species IDs are correctly mapped to backend IDs"""

    def test_frontend_species_mapping(self, api_client):
        """Verify all frontend IDs map to correct backend IDs"""
        mappings = [
            ("chevreuil", "CERF"),
            ("orignal", "ORIGNAL"),
            ("ours_noir", "OURS"),
            ("dindon_sauvage", "DINDON"),
            ("wapiti", "WAPITI"),
            ("tous", "CERF"),
        ]
        
        for frontend_id, expected_backend_id in mappings:
            response = api_client.post(f"{BASE_URL}/api/v2/alimentation/analyze", json={
                "center_lat": 46.8139,
                "center_lng": -71.2080,
                "species": frontend_id,
                "month": 10
            })
            assert response.status_code == 200, f"Failed for {frontend_id}: {response.text}"
            
            data = response.json()
            assert data.get("species") == expected_backend_id, \
                f"Frontend ID '{frontend_id}' should map to '{expected_backend_id}', got '{data.get('species')}'"
            
            print(f"[PASS] {frontend_id} → {data.get('species')}")


class TestNutritionDataPresent:
    """Test nutrition data is always present regardless of salines status"""

    def test_ours_has_nutrition_data(self, api_client):
        """OURS should still have nutrition data even though salines are disabled"""
        response = api_client.post(f"{BASE_URL}/api/v2/alimentation/analyze", json={
            "center_lat": 46.8139,
            "center_lng": -71.2080,
            "species": "ours_noir",
            "month": 10
        })
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify nutrition data exists
        assert "nutrition" in data, "Expected nutrition data for OURS"
        nutrition = data["nutrition"]
        
        # OURS should have NO saline_composition (since salines disabled)
        # But other nutrition fields should exist
        assert "aliments_recommandes" in nutrition, "Expected aliments_recommandes for OURS"
        assert "nutriments_essentiels" in nutrition, "Expected nutriments_essentiels for OURS"
        
        print(f"[PASS] ours_noir has nutrition data: {list(nutrition.keys())}")

    def test_dindon_has_nutrition_data(self, api_client):
        """DINDON should still have nutrition data even though salines are disabled"""
        response = api_client.post(f"{BASE_URL}/api/v2/alimentation/analyze", json={
            "center_lat": 46.8139,
            "center_lng": -71.2080,
            "species": "dindon_sauvage",
            "month": 10
        })
        assert response.status_code == 200
        
        data = response.json()
        
        assert "nutrition" in data, "Expected nutrition data for DINDON"
        nutrition = data["nutrition"]
        assert "aliments_recommandes" in nutrition, "Expected aliments_recommandes for DINDON"
        
        print(f"[PASS] dindon_sauvage has nutrition data: {list(nutrition.keys())}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
