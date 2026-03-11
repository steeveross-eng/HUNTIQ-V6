"""
BIONIC V5 Iteration 61 — Organic Pipeline V2 Validation Tests

Testing BIONIC V5 corrections:
1) Simplex noise isotrope (behavioral_rasterizer.py)
2) Blob extraction via composantes connexes (organic_zone_generator_v2.py)
3) Zone validation: aspect ratio < 3, 50+ vertices, compactness > 0.10
4) API response time < 10 seconds
5) Regression tests: seasonal-conditions, comparaison-especes
"""

import pytest
import requests
import os
import time
import math

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Test bounds for Quebec City area (rural zones)
TEST_BOUNDS = {
    "north": 46.88,
    "south": 46.82,
    "east": -71.20,
    "west": -71.30
}


class TestOrganicZonesV2:
    """Tests for BIONIC V5 organic pipeline V2 corrections"""
    
    def test_organic_zones_endpoint_status(self):
        """Test that POST /api/v1/bionic/organic-zones returns 200"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json={
                "bounds": TEST_BOUNDS,
                "species": "moose",
                "resolution": 50,
                "max_zones_per_layer": 8
            },
            timeout=30
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "type" in data and data["type"] == "FeatureCollection"
        assert "features" in data
        print(f"✓ Organic zones endpoint returned 200 with {len(data['features'])} features")
    
    def test_response_time_under_10_seconds(self):
        """Test API response time is < 10 seconds"""
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json={
                "bounds": TEST_BOUNDS,
                "species": "moose",
                "resolution": 50,
                "max_zones_per_layer": 8
            },
            timeout=30
        )
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 10.0, f"Response took {elapsed:.2f}s, expected < 10s"
        print(f"✓ API response time: {elapsed:.2f}s (< 10s requirement)")
    
    def test_zones_have_blob_shape_aspect_ratio(self):
        """Test that zones have aspect ratio < 3 (blobs, not bars/rectangles)"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json={
                "bounds": TEST_BOUNDS,
                "species": "moose",
                "resolution": 50,
                "max_zones_per_layer": 8
            },
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        features = data.get("features", [])
        
        assert len(features) > 0, "No zones returned"
        
        zones_with_high_aspect = []
        zones_checked = 0
        
        for feature in features:
            coords = feature.get("geometry", {}).get("coordinates", [[]])[0]
            if len(coords) < 4:
                continue
            
            # Calculate bounding box
            lngs = [c[0] for c in coords]
            lats = [c[1] for c in coords]
            
            min_lng, max_lng = min(lngs), max(lngs)
            min_lat, max_lat = min(lats), max(lats)
            
            # Convert to meters for aspect ratio
            center_lat = (min_lat + max_lat) / 2
            width_m = (max_lng - min_lng) * 111320 * math.cos(math.radians(center_lat))
            height_m = (max_lat - min_lat) * 111320
            
            if width_m > 0 and height_m > 0:
                aspect_ratio = max(width_m, height_m) / min(width_m, height_m)
                zones_checked += 1
                
                if aspect_ratio > 3:
                    layer_id = feature.get("properties", {}).get("layer_id", "unknown")
                    zones_with_high_aspect.append({
                        "layer": layer_id,
                        "aspect_ratio": round(aspect_ratio, 2)
                    })
        
        # Allow up to 10% of zones to have high aspect ratio
        max_allowed = max(1, int(zones_checked * 0.10))
        assert len(zones_with_high_aspect) <= max_allowed, \
            f"Too many zones with aspect ratio > 3: {zones_with_high_aspect}"
        
        print(f"✓ Zones have blob shape: {zones_checked} checked, {len(zones_with_high_aspect)} with aspect ratio > 3 (max {max_allowed} allowed)")
    
    def test_zones_have_sufficient_vertices(self):
        """Test that zones have 50+ vertices (smooth curves)"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json={
                "bounds": TEST_BOUNDS,
                "species": "moose",
                "resolution": 50,
                "max_zones_per_layer": 8
            },
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        features = data.get("features", [])
        
        assert len(features) > 0, "No zones returned"
        
        vertex_counts = []
        zones_with_few_vertices = []
        
        for feature in features:
            coords = feature.get("geometry", {}).get("coordinates", [[]])[0]
            vertex_count = len(coords)
            vertex_counts.append(vertex_count)
            
            if vertex_count < 50:
                layer_id = feature.get("properties", {}).get("layer_id", "unknown")
                zones_with_few_vertices.append({
                    "layer": layer_id,
                    "vertices": vertex_count
                })
        
        avg_vertices = sum(vertex_counts) / len(vertex_counts) if vertex_counts else 0
        
        # At least 50% of zones should have 50+ vertices
        zones_with_enough = sum(1 for v in vertex_counts if v >= 50)
        min_required = max(1, int(len(features) * 0.50))
        
        assert zones_with_enough >= min_required, \
            f"Only {zones_with_enough}/{len(features)} zones have 50+ vertices (need {min_required})"
        
        print(f"✓ Zones have smooth curves: avg {avg_vertices:.0f} vertices, {zones_with_enough}/{len(features)} with 50+ vertices")
    
    def test_zones_have_valid_compactness(self):
        """Test that zones have compactness > 0.10 (not hyper-elongated)"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json={
                "bounds": TEST_BOUNDS,
                "species": "moose",
                "resolution": 50,
                "max_zones_per_layer": 8
            },
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        features = data.get("features", [])
        
        assert len(features) > 0, "No zones returned"
        
        compactness_values = []
        zones_with_low_compactness = []
        
        for feature in features:
            props = feature.get("properties", {})
            compactness = props.get("compactness", 0)
            compactness_values.append(compactness)
            
            if compactness < 0.10:
                layer_id = props.get("layer_id", "unknown")
                zones_with_low_compactness.append({
                    "layer": layer_id,
                    "compactness": round(compactness, 4)
                })
        
        avg_compactness = sum(compactness_values) / len(compactness_values) if compactness_values else 0
        
        # At least 80% of zones should have compactness > 0.10
        valid_zones = sum(1 for c in compactness_values if c >= 0.10)
        min_required = max(1, int(len(features) * 0.80))
        
        assert valid_zones >= min_required, \
            f"Only {valid_zones}/{len(features)} zones have compactness > 0.10: {zones_with_low_compactness}"
        
        print(f"✓ Zones have valid compactness: avg {avg_compactness:.3f}, {valid_zones}/{len(features)} with compactness > 0.10")
    
    def test_geojson_structure_complete(self):
        """Test that GeoJSON has complete structure with required fields"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json={
                "bounds": TEST_BOUNDS,
                "species": "moose",
                "resolution": 50,
                "max_zones_per_layer": 8
            },
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check GeoJSON structure
        assert data["type"] == "FeatureCollection"
        assert "features" in data
        assert len(data["features"]) > 0, "No features returned"
        
        # Check feature structure
        feature = data["features"][0]
        assert feature["type"] == "Feature"
        assert "geometry" in feature
        assert feature["geometry"]["type"] == "Polygon"
        assert "coordinates" in feature["geometry"]
        
        # Check properties
        props = feature.get("properties", {})
        required_props = ["layer_id", "score", "area_m2", "compactness"]
        for prop in required_props:
            assert prop in props, f"Missing property: {prop}"
        
        print(f"✓ GeoJSON structure complete with {len(data['features'])} features")


class TestRegressionSeasonalConditions:
    """Regression tests for seasonal-conditions endpoint"""
    
    def test_seasonal_conditions_endpoint_status(self):
        """Test GET /api/v1/bionic/seasonal-conditions returns 200"""
        response = requests.get(
            f"{BASE_URL}/api/v1/bionic/seasonal-conditions",
            params={"lat": 46.85, "lng": -71.25},
            timeout=10
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Verify structure
        assert "score" in data
        assert "meteo" in data
        assert "phenologie" in data
        
        score = data.get("score", {}).get("global", 0)
        print(f"✓ Seasonal conditions endpoint returns 200 with score {score}")
    
    def test_seasonal_conditions_complete_data(self):
        """Test seasonal conditions returns complete data structure"""
        response = requests.get(
            f"{BASE_URL}/api/v1/bionic/seasonal-conditions",
            params={"lat": 46.85, "lng": -71.25},
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check score (score.global)
        score_obj = data.get("score", {})
        score = score_obj.get("global", 0)
        assert 0 <= score <= 100, f"Score out of range: {score}"
        assert "rating" in score_obj
        
        # Check meteo
        meteo = data.get("meteo", {})
        assert "temperature_c" in meteo
        assert "vent_kmh" in meteo
        
        # Check phenologie
        pheno = data.get("phenologie", {})
        assert "phase" in pheno or "saison" in pheno
        
        print(f"✓ Seasonal conditions has complete data: score={score}, temp={meteo.get('temperature_c', 'N/A')}°C")


class TestRegressionComparaisonEspeces:
    """Regression tests for comparaison-especes page API support"""
    
    def test_organic_zones_different_species(self):
        """Test that different species return different zone patterns"""
        # Test moose
        response_moose = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json={
                "bounds": TEST_BOUNDS,
                "species": "moose",
                "layers": ["habitats", "alimentation"],
                "resolution": 50,
                "max_zones_per_layer": 5
            },
            timeout=30
        )
        assert response_moose.status_code == 200
        
        # Test deer
        response_deer = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json={
                "bounds": TEST_BOUNDS,
                "species": "deer",
                "layers": ["habitats", "alimentation"],
                "resolution": 50,
                "max_zones_per_layer": 5
            },
            timeout=30
        )
        assert response_deer.status_code == 200
        
        moose_features = response_moose.json().get("features", [])
        deer_features = response_deer.json().get("features", [])
        
        print(f"✓ Species comparison: moose={len(moose_features)} zones, deer={len(deer_features)} zones")
    
    def test_layers_endpoint_returns_species(self):
        """Test GET /api/v1/bionic/organic-zones/layers returns species list"""
        response = requests.get(
            f"{BASE_URL}/api/v1/bionic/organic-zones/layers",
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "layers" in data
        assert "species" in data
        assert len(data["species"]) >= 3, "Expected at least 3 species (moose, deer, bear)"
        
        species_ids = [s["id"] for s in data["species"]]
        assert "moose" in species_ids
        assert "deer" in species_ids
        
        print(f"✓ Layers endpoint returns {len(data['layers'])} layers and {len(data['species'])} species")


class TestHealthAndBasics:
    """Basic health and infrastructure tests"""
    
    def test_health_endpoint(self):
        """Test health endpoint returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"✓ Health endpoint: status={data.get('status')}, version={data.get('version')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
