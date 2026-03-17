"""
BIONIC V5 Iteration 58 — Testing Species Comparison Page + Organic Zones API
Test the features fixed by main agent:
1. /comparaison-especes page (split-screen multi-species comparison)
2. POST /api/v1/bionic/organic-zones endpoint returns valid GeoJSON
3. /map page loads with BIONIC V5 zones
4. /territoire page loads with BIONIC Premium map
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://organic-zones-map.preview.emergentagent.com')

# Remove trailing slash if present
BASE_URL = BASE_URL.rstrip('/')


class TestHealthCheck:
    """Basic health check tests"""
    
    def test_health_endpoint(self):
        """TEST 1: Health endpoint returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        assert "version" in data
        print(f"✓ Health endpoint: status={data['status']}, version={data['version']}")


class TestOrganicZonesAPI:
    """Tests for POST /api/v1/bionic/organic-zones endpoint"""
    
    def test_organic_zones_basic_request(self):
        """TEST 2: Organic zones endpoint returns valid GeoJSON with moose species"""
        payload = {
            "bounds": {
                "north": 46.88,
                "south": 46.82,
                "east": -71.15,
                "west": -71.30
            },
            "species": "moose",
            "layers": ["habitats"],
            "resolution": 60,
            "max_zones_per_layer": 5
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=90  # Allow longer timeout for zone generation
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("type") == "FeatureCollection", "Response should be a GeoJSON FeatureCollection"
        assert "features" in data, "GeoJSON should have features array"
        print(f"✓ Organic zones API returned {len(data['features'])} features for moose")
    
    def test_organic_zones_deer_species(self):
        """TEST 3: Organic zones endpoint works for deer species"""
        payload = {
            "bounds": {
                "north": 46.88,
                "south": 46.82,
                "east": -71.15,
                "west": -71.30
            },
            "species": "deer",
            "layers": ["habitats", "rut"],
            "resolution": 60,
            "max_zones_per_layer": 3
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=90
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("type") == "FeatureCollection"
        print(f"✓ Organic zones API returned {len(data['features'])} features for deer")
    
    def test_organic_zones_feature_structure(self):
        """TEST 4: Organic zones features have correct structure with scoring"""
        payload = {
            "bounds": {
                "north": 46.88,
                "south": 46.82,
                "east": -71.15,
                "west": -71.30
            },
            "species": "moose",
            "layers": ["habitats"],
            "resolution": 60,
            "max_zones_per_layer": 2,
            "include_scoring": True
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=90
        )
        
        assert response.status_code == 200
        data = response.json()
        
        if len(data.get("features", [])) > 0:
            feature = data["features"][0]
            
            # Check GeoJSON structure
            assert "type" in feature, "Feature should have 'type'"
            assert feature["type"] == "Feature", "Type should be 'Feature'"
            assert "geometry" in feature, "Feature should have 'geometry'"
            assert "properties" in feature, "Feature should have 'properties'"
            
            # Check geometry
            geom = feature["geometry"]
            assert geom.get("type") == "Polygon", "Geometry should be Polygon"
            assert "coordinates" in geom, "Geometry should have coordinates"
            
            # Check properties
            props = feature["properties"]
            assert "layer_id" in props, "Properties should have layer_id"
            assert "score" in props, "Properties should have score"
            assert "style" in props, "Properties should have style info"
            
            print(f"✓ Feature structure valid: layer={props['layer_id']}, score={props['score']}")
        else:
            print("⚠ No features returned (may be expected for certain areas)")
    
    def test_organic_zones_multiple_layers(self):
        """TEST 5: Organic zones endpoint handles multiple layers"""
        payload = {
            "bounds": {
                "north": 46.88,
                "south": 46.82,
                "east": -71.15,
                "west": -71.30
            },
            "species": "moose",
            "layers": ["habitats", "rut", "alimentation", "corridors", "repos"],
            "resolution": 40,
            "max_zones_per_layer": 3
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120  # Longer timeout for multiple layers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("type") == "FeatureCollection"
        print(f"✓ Multi-layer request returned {len(data['features'])} zones")


class TestOrganicZonesLayersEndpoint:
    """Tests for GET /api/v1/bionic/organic-zones/layers endpoint"""
    
    def test_layers_endpoint(self):
        """TEST 6: Layers endpoint returns available layers and species"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/organic-zones/layers")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "layers" in data, "Response should have layers"
        assert "species" in data, "Response should have species"
        assert len(data["layers"]) > 0, "Should have at least one layer"
        assert len(data["species"]) > 0, "Should have at least one species"
        
        # Check layer structure
        layer = data["layers"][0]
        assert "id" in layer, "Layer should have id"
        assert "label" in layer, "Layer should have label"
        assert "color" in layer, "Layer should have color"
        
        print(f"✓ Layers endpoint: {len(data['layers'])} layers, {len(data['species'])} species")


class TestErrorHandling:
    """Tests for API error handling"""
    
    def test_invalid_bounds(self):
        """TEST 7: API handles invalid bounds gracefully"""
        payload = {
            "bounds": {
                "north": 91,  # Invalid - out of range
                "south": 46.82,
                "east": -71.15,
                "west": -71.30
            },
            "species": "moose",
            "layers": ["habitats"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        # Should return 422 (validation error) or 400 (bad request)
        assert response.status_code in [400, 422], f"Expected 400 or 422 for invalid bounds, got {response.status_code}"
        print(f"✓ Invalid bounds correctly rejected with status {response.status_code}")
    
    def test_empty_layers(self):
        """TEST 8: API handles empty layers array"""
        payload = {
            "bounds": {
                "north": 46.88,
                "south": 46.82,
                "east": -71.15,
                "west": -71.30
            },
            "species": "moose",
            "layers": []  # Empty layers
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        # Should return 200 with empty features or handle gracefully
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("type") == "FeatureCollection"
        print(f"✓ Empty layers handled: returned {len(data.get('features', []))} features")


class TestSpeciesComparison:
    """Tests related to species comparison functionality (backend support)"""
    
    def test_orignal_vs_chevreuil_zones(self):
        """TEST 9: Compare zone counts for orignal (moose) vs chevreuil (deer)"""
        bounds = {
            "north": 46.88,
            "south": 46.82,
            "east": -71.15,
            "west": -71.30
        }
        
        # Test moose (orignal)
        moose_response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json={
                "bounds": bounds,
                "species": "moose",
                "layers": ["habitats"],
                "resolution": 60,
                "max_zones_per_layer": 5
            },
            timeout=90
        )
        
        # Test deer (chevreuil)
        deer_response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json={
                "bounds": bounds,
                "species": "deer",
                "layers": ["habitats"],
                "resolution": 60,
                "max_zones_per_layer": 5
            },
            timeout=90
        )
        
        assert moose_response.status_code == 200, "Moose request failed"
        assert deer_response.status_code == 200, "Deer request failed"
        
        moose_data = moose_response.json()
        deer_data = deer_response.json()
        
        moose_zones = len(moose_data.get("features", []))
        deer_zones = len(deer_data.get("features", []))
        
        print(f"✓ Species comparison - Moose: {moose_zones} zones, Deer: {deer_zones} zones")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
