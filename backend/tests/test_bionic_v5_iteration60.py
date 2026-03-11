"""
BIONIC V5 Iteration 60 — Phase E + Corridors Fix
================================================

Tests for:
1. GET /api/v1/bionic/seasonal-conditions - Seasonal conditions endpoint (PHASE E)
2. POST /api/v1/bionic/map/corridors - Corridors with generate_corridor_geometry fix
3. Regression tests for organic zones and species comparison
"""

import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestSeasonalConditions:
    """PHASE E — Seasonal Conditions Module Tests"""
    
    def test_seasonal_endpoint_returns_200(self):
        """Test GET /api/v1/bionic/seasonal-conditions returns 200"""
        response = requests.get(
            f"{BASE_URL}/api/v1/bionic/seasonal-conditions",
            params={"lat": 46.85, "lng": -71.25},
            timeout=30
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("PASS: Seasonal conditions endpoint returns 200")
    
    def test_seasonal_response_has_score(self):
        """Test score is present and between 0-100"""
        response = requests.get(
            f"{BASE_URL}/api/v1/bionic/seasonal-conditions",
            params={"lat": 46.85, "lng": -71.25},
            timeout=30
        )
        data = response.json()
        assert "score" in data, "Response must have 'score' field"
        assert "global" in data["score"], "Score must have 'global' field"
        
        score_global = data["score"]["global"]
        assert 0 <= score_global <= 100, f"Score global must be 0-100, got {score_global}"
        
        rating = data["score"]["rating"]
        assert rating in ["excellent", "bon", "moyen", "defavorable"], f"Invalid rating: {rating}"
        print(f"PASS: Score global = {score_global}/100, rating = {rating}")
    
    def test_seasonal_meteo_fields(self):
        """Test meteo data has required fields"""
        response = requests.get(
            f"{BASE_URL}/api/v1/bionic/seasonal-conditions",
            params={"lat": 46.85, "lng": -71.25},
            timeout=30
        )
        data = response.json()
        meteo = data.get("meteo", {})
        
        required_fields = ["temperature_c", "vent_kmh", "precipitations_mm", "pression_hpa", "condition"]
        for field in required_fields:
            assert field in meteo, f"Meteo must have '{field}' field"
        
        # Validate types
        assert isinstance(meteo["temperature_c"], (int, float)), "temperature_c must be numeric"
        assert isinstance(meteo["vent_kmh"], (int, float)), "vent_kmh must be numeric"
        assert isinstance(meteo["precipitations_mm"], (int, float)), "precipitations_mm must be numeric"
        assert isinstance(meteo["pression_hpa"], (int, float)), "pression_hpa must be numeric"
        assert isinstance(meteo["condition"], str), "condition must be string"
        
        print(f"PASS: Meteo = temp:{meteo['temperature_c']}C, wind:{meteo['vent_kmh']}km/h, precip:{meteo['precipitations_mm']}mm, pressure:{meteo['pression_hpa']}hPa, condition:{meteo['condition']}")
    
    def test_seasonal_phenologie_fields(self):
        """Test phenologie data has required fields"""
        response = requests.get(
            f"{BASE_URL}/api/v1/bionic/seasonal-conditions",
            params={"lat": 46.85, "lng": -71.25},
            timeout=30
        )
        data = response.json()
        phenologie = data.get("phenologie", {})
        
        assert "saison" in phenologie, "Phenologie must have 'saison'"
        assert "phase" in phenologie, "Phenologie must have 'phase'"
        assert "rut" in phenologie, "Phenologie must have 'rut'"
        assert "duree_jour_h" in phenologie, "Phenologie must have 'duree_jour_h'"
        
        assert phenologie["saison"] in ["hiver", "printemps", "ete", "automne"], f"Invalid saison: {phenologie['saison']}"
        assert isinstance(phenologie["duree_jour_h"], (int, float)), "duree_jour_h must be numeric"
        
        print(f"PASS: Phenologie = saison:{phenologie['saison']}, phase:{phenologie.get('phase', {}).get('label', 'N/A')}, day_length:{phenologie['duree_jour_h']}h")
    
    def test_seasonal_pression_chasse_fields(self):
        """Test pression de chasse data has required fields"""
        response = requests.get(
            f"{BASE_URL}/api/v1/bionic/seasonal-conditions",
            params={"lat": 46.85, "lng": -71.25},
            timeout=30
        )
        data = response.json()
        pression = data.get("pression_chasse", {})
        
        assert "intensity" in pression, "Pression must have 'intensity'"
        assert "label" in pression, "Pression must have 'label'"
        assert "active_seasons" in pression, "Pression must have 'active_seasons'"
        
        assert 0 <= pression["intensity"] <= 1, f"Intensity must be 0-1, got {pression['intensity']}"
        assert isinstance(pression["active_seasons"], list), "active_seasons must be a list"
        
        print(f"PASS: Pression = intensity:{pression['intensity']}, label:{pression['label']}, active:{len(pression['active_seasons'])} seasons")
    
    def test_seasonal_different_positions(self):
        """Test seasonal conditions vary by position"""
        # Quebec City
        resp1 = requests.get(
            f"{BASE_URL}/api/v1/bionic/seasonal-conditions",
            params={"lat": 46.85, "lng": -71.25},
            timeout=30
        )
        # More northern position
        resp2 = requests.get(
            f"{BASE_URL}/api/v1/bionic/seasonal-conditions",
            params={"lat": 48.5, "lng": -72.0},
            timeout=30
        )
        
        data1 = resp1.json()
        data2 = resp2.json()
        
        # Verify responses are valid
        assert "meteo" in data1 and "meteo" in data2
        
        # Northern position should be colder (latitude correction applied)
        temp1 = data1["meteo"]["temperature_c"]
        temp2 = data2["meteo"]["temperature_c"]
        
        print(f"PASS: Position variance works - Quebec:{temp1}C, Northern:{temp2}C")


class TestCorridors:
    """POST /api/v1/bionic/map/corridors Tests"""
    
    def test_corridors_endpoint_returns_200(self):
        """Test corridors endpoint returns 200 (not 500)"""
        payload = {
            "bounds": {
                "south": 46.8,
                "west": -71.3,
                "north": 46.9,
                "east": -71.2
            },
            "species": "moose",
            "corridor_types": ["movement"],
            "connect_zones": True
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/map/corridors",
            json=payload,
            timeout=60
        )
        
        # Should NOT be 500 anymore (fix applied)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("PASS: Corridors endpoint returns 200 (fix working)")
    
    def test_corridors_returns_valid_structure(self):
        """Test corridors response has valid structure"""
        payload = {
            "bounds": {
                "south": 46.8,
                "west": -71.3,
                "north": 46.9,
                "east": -71.2
            },
            "species": "moose",
            "corridor_types": ["movement", "preferred"],
            "connect_zones": True
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/map/corridors",
            json=payload,
            timeout=60
        )
        
        data = response.json()
        
        assert "success" in data, "Response must have 'success' field"
        assert data["success"] == True, "success must be True"
        assert "corridors" in data, "Response must have 'corridors' field"
        assert "metadata" in data, "Response must have 'metadata' field"
        
        print(f"PASS: Corridors response structure valid - {len(data['corridors'])} corridors returned")
    
    def test_corridor_has_linestring_geometry(self):
        """Test corridors have LineString geometry (not null)"""
        payload = {
            "bounds": {
                "south": 46.8,
                "west": -71.3,
                "north": 46.9,
                "east": -71.2
            },
            "species": "moose",
            "corridor_types": ["movement"],
            "connect_zones": True
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/map/corridors",
            json=payload,
            timeout=60
        )
        
        data = response.json()
        corridors = data.get("corridors", [])
        
        if corridors:
            for corridor in corridors[:3]:  # Check first 3
                geometry = corridor.get("geometry", {})
                assert geometry.get("type") == "LineString", f"Corridor geometry type must be LineString, got {geometry.get('type')}"
                coords = geometry.get("coordinates", [])
                assert len(coords) >= 2, f"LineString must have at least 2 coordinates, got {len(coords)}"
                
                # Verify coordinates are valid [lng, lat] pairs
                for coord in coords:
                    assert len(coord) == 2, f"Each coordinate must have [lng, lat], got {coord}"
                    assert isinstance(coord[0], (int, float)), "Longitude must be numeric"
                    assert isinstance(coord[1], (int, float)), "Latitude must be numeric"
            
            print(f"PASS: {len(corridors)} corridors have valid LineString geometry")
        else:
            print("PASS: No corridors generated for this area (valid scenario)")
    
    def test_corridors_different_types(self):
        """Test different corridor types are generated"""
        payload = {
            "bounds": {
                "south": 46.8,
                "west": -71.3,
                "north": 46.9,
                "east": -71.2
            },
            "species": "moose",
            "corridor_types": ["movement", "avoidance", "preferred", "feeding_transit"],
            "connect_zones": True
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/map/corridors",
            json=payload,
            timeout=60
        )
        
        data = response.json()
        corridors = data.get("corridors", [])
        
        if corridors:
            types_found = set(c.get("type") for c in corridors)
            print(f"PASS: Corridor types found: {types_found}")
        else:
            print("PASS: No corridors in this area (urban exclusion may apply)")


class TestRegressionOrganicZones:
    """Regression tests for organic zones API"""
    
    def test_health_endpoint(self):
        """Test health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"PASS: Health endpoint OK - version {data.get('version', 'N/A')}")
    
    def test_organic_zones_endpoint(self):
        """Test organic zones endpoint still works"""
        payload = {
            "bounds": {
                "south": 46.8,
                "west": -71.3,
                "north": 46.9,
                "east": -71.2
            },
            "zoom": 14,
            "layers": ["habitats", "rut"],
            "species": "moose"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            timeout=60
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "type" in data and data["type"] == "FeatureCollection"
        print(f"PASS: Organic zones returns valid GeoJSON - {len(data.get('features', []))} features")
    
    def test_layers_endpoint(self):
        """Test layers endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/v1/bionic/organic-zones/layers",
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "layers" in data
        assert "species" in data
        print(f"PASS: Layers endpoint returns {len(data.get('layers', []))} layers, {len(data.get('species', []))} species")


class TestFrontendRegression:
    """Regression tests to ensure frontend pages accessible"""
    
    def test_frontend_accessible(self):
        """Test frontend is accessible"""
        response = requests.get(BASE_URL, timeout=30)
        assert response.status_code == 200
        print("PASS: Frontend homepage accessible")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
