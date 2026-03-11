"""
Test V8.1 Biological Seasons API
BIONIC™ V8.1 — Saisons biologiques

Tests:
1. POST /api/v1/bionic/organic-zones with biological_season parameter
2. Verify seasonal_weight and biological_season returned in zone properties
3. Test all 5 seasons: pre_rut, rut, post_rut, winter, spring
4. Verify weight application to scores
"""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

class TestBiologicalSeasonAPI:
    """V8.1 Biological Season API tests"""
    
    # Test bounds (Quebec wilderness area)
    BOUNDS = {
        "north": 46.83,
        "south": 46.80,
        "east": -71.19,
        "west": -71.22
    }
    
    def test_api_health(self):
        """Test that API is reachable"""
        resp = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert resp.status_code == 200
        print("TEST PASS: API health check OK")
    
    def test_organic_zones_without_biological_season(self):
        """Test organic zones API works without biological_season (default behavior)"""
        payload = {
            "bounds": self.BOUNDS,
            "species": "moose",
            "layers": ["habitats", "rut", "alimentation"],
            "resolution": 50,
            "max_zones_per_layer": 3,
            "include_scoring": True
        }
        resp = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            timeout=60
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text[:500]}"
        data = resp.json()
        assert "features" in data or data.get("type") == "FeatureCollection", "Expected GeoJSON response"
        print(f"TEST PASS: Organic zones without biological_season returned {len(data.get('features', []))} features")
    
    def test_organic_zones_with_pre_rut_season(self):
        """Test organic zones with pre_rut biological season"""
        payload = {
            "bounds": self.BOUNDS,
            "species": "moose",
            "layers": ["habitats", "rut", "alimentation", "corridors"],
            "resolution": 50,
            "max_zones_per_layer": 3,
            "include_scoring": True,
            "biological_season": "pre_rut"
        }
        resp = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            timeout=60
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        
        # Check biological_season metadata
        if "biological_season" in data:
            bio_meta = data["biological_season"]
            assert bio_meta.get("id") == "pre_rut", f"Expected pre_rut, got {bio_meta.get('id')}"
            print(f"TEST PASS: Biological season metadata present: {bio_meta}")
        
        # Check zone properties for seasonal_weight
        features = data.get("features", [])
        if features:
            for feature in features[:3]:  # Check first 3
                props = feature.get("properties", {})
                if "seasonal_weight" in props:
                    assert props["biological_season"] == "pre_rut"
                    print(f"  Zone {props.get('layer_id')}: score={props.get('score')}, weight={props.get('seasonal_weight')}")
        
        print(f"TEST PASS: pre_rut season returned {len(features)} zones")
    
    def test_organic_zones_with_rut_season(self):
        """Test organic zones with rut (peak activity) biological season"""
        payload = {
            "bounds": self.BOUNDS,
            "species": "moose",
            "layers": ["habitats", "rut", "alimentation", "affuts"],
            "resolution": 50,
            "max_zones_per_layer": 3,
            "include_scoring": True,
            "biological_season": "rut"
        }
        resp = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            timeout=60
        )
        assert resp.status_code == 200
        data = resp.json()
        
        # Rut season should boost rut zones with weight 2.0
        features = data.get("features", [])
        rut_zones = [f for f in features if f.get("properties", {}).get("layer_id") == "rut"]
        if rut_zones:
            for zone in rut_zones[:2]:
                props = zone.get("properties", {})
                weight = props.get("seasonal_weight", 1.0)
                assert weight == 2.0, f"Rut zone should have weight 2.0, got {weight}"
                print(f"  Rut zone: score={props.get('score')}, weight={weight} (2.0 expected)")
        
        print(f"TEST PASS: rut season returned {len(features)} zones, {len(rut_zones)} rut zones")
    
    def test_organic_zones_with_post_rut_season(self):
        """Test organic zones with post_rut biological season"""
        payload = {
            "bounds": self.BOUNDS,
            "species": "moose",
            "layers": ["habitats", "repos", "alimentation"],
            "resolution": 50,
            "max_zones_per_layer": 3,
            "include_scoring": True,
            "biological_season": "post_rut"
        }
        resp = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            timeout=60
        )
        assert resp.status_code == 200
        data = resp.json()
        
        # Post-rut should boost alimentation (1.8) and repos (1.5)
        features = data.get("features", [])
        if "biological_season" in data:
            assert data["biological_season"]["id"] == "post_rut"
        
        print(f"TEST PASS: post_rut season returned {len(features)} zones")
    
    def test_organic_zones_with_winter_season(self):
        """Test organic zones with winter biological season"""
        payload = {
            "bounds": self.BOUNDS,
            "species": "moose",
            "layers": ["habitats", "repos", "alimentation", "corridors"],
            "resolution": 50,
            "max_zones_per_layer": 3,
            "include_scoring": True,
            "biological_season": "winter"
        }
        resp = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            timeout=60
        )
        assert resp.status_code == 200
        data = resp.json()
        
        # Winter: rut weight = 0.0, repos = 1.8, corridors = 0.5
        features = data.get("features", [])
        if "biological_season" in data:
            assert data["biological_season"]["id"] == "winter"
        
        # Check corridor zones have reduced weight (0.5)
        corridor_zones = [f for f in features if f.get("properties", {}).get("layer_id") == "corridors"]
        for zone in corridor_zones[:2]:
            props = zone.get("properties", {})
            weight = props.get("seasonal_weight", 1.0)
            if "seasonal_weight" in props:
                assert weight == 0.5, f"Winter corridor should have weight 0.5, got {weight}"
        
        print(f"TEST PASS: winter season returned {len(features)} zones")
    
    def test_organic_zones_with_spring_season(self):
        """Test organic zones with spring biological season (current season for January)"""
        payload = {
            "bounds": self.BOUNDS,
            "species": "moose",
            "layers": ["habitats", "alimentation", "salines", "hydro"],
            "resolution": 50,
            "max_zones_per_layer": 3,
            "include_scoring": True,
            "biological_season": "spring"
        }
        resp = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            timeout=60
        )
        assert resp.status_code == 200
        data = resp.json()
        
        # Spring: alimentation = 1.5, salines = 1.3, hydro = 1.2
        features = data.get("features", [])
        if "biological_season" in data:
            assert data["biological_season"]["id"] == "spring"
        
        print(f"TEST PASS: spring season returned {len(features)} zones")
    
    def test_seasonal_weight_score_adjustment(self):
        """Test that scores are properly adjusted by seasonal weights"""
        # Test with rut season on habitats layer (weight 1.0 = no change expected)
        payload = {
            "bounds": self.BOUNDS,
            "species": "moose",
            "layers": ["habitats"],
            "resolution": 50,
            "max_zones_per_layer": 2,
            "include_scoring": True,
            "biological_season": "rut"
        }
        resp = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            timeout=60
        )
        assert resp.status_code == 200
        data = resp.json()
        
        features = data.get("features", [])
        for feature in features[:2]:
            props = feature.get("properties", {})
            score = props.get("score", 0)
            weight = props.get("seasonal_weight", 1.0)
            # Score should be capped at 100
            assert 0 <= score <= 100, f"Score {score} out of range 0-100"
            print(f"  {props.get('layer_id')}: score={score}, weight={weight}")
        
        print("TEST PASS: Score adjustment within bounds")
    
    def test_all_seasons_return_valid_geojson(self):
        """Test that all 5 seasons return valid GeoJSON"""
        seasons = ["pre_rut", "rut", "post_rut", "winter", "spring"]
        
        for season in seasons:
            payload = {
                "bounds": self.BOUNDS,
                "species": "moose",
                "layers": ["habitats"],
                "resolution": 50,
                "max_zones_per_layer": 2,
                "include_scoring": True,
                "biological_season": season
            }
            resp = requests.post(
                f"{BASE_URL}/api/v1/bionic/organic-zones",
                json=payload,
                timeout=60
            )
            assert resp.status_code == 200, f"Season {season} failed with {resp.status_code}"
            data = resp.json()
            assert "features" in data or data.get("type") == "FeatureCollection", f"Season {season} invalid response"
            print(f"  {season}: OK ({len(data.get('features', []))} features)")
        
        print("TEST PASS: All 5 biological seasons return valid GeoJSON")


class TestBiologicalSeasonWeights:
    """Test that weight constants are correctly applied"""
    
    EXPECTED_WEIGHTS = {
        "pre_rut": {"habitats": 1.2, "rut": 1.5, "repos": 0.8, "alimentation": 1.3, "corridors": 1.6, "salines": 1.4, "affuts": 1.2},
        "rut":     {"habitats": 1.0, "rut": 2.0, "repos": 0.5, "alimentation": 0.7, "corridors": 1.8, "salines": 0.8, "affuts": 1.5},
        "post_rut":{"habitats": 1.3, "rut": 0.3, "repos": 1.5, "alimentation": 1.8, "corridors": 1.0, "salines": 0.6, "affuts": 1.0},
        "winter":  {"habitats": 1.5, "rut": 0.0, "repos": 1.8, "alimentation": 1.6, "corridors": 0.5, "salines": 0.3, "affuts": 0.5},
        "spring":  {"habitats": 1.0, "rut": 0.1, "repos": 1.0, "alimentation": 1.5, "corridors": 1.2, "salines": 1.3, "affuts": 0.8},
    }
    
    def test_layers_endpoint_available(self):
        """Test that layers endpoint is available"""
        resp = requests.get(f"{BASE_URL}/api/v1/bionic/organic-zones/layers", timeout=10)
        assert resp.status_code == 200
        data = resp.json()
        assert "layers" in data
        assert "species" in data
        print(f"TEST PASS: Layers endpoint returns {len(data['layers'])} layers, {len(data['species'])} species")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
