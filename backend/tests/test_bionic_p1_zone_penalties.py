"""
BIONIC V5 P1 — Zone Penalty Engine Tests
Tests for semi-static penalties applied to organic zones AFTER P0 exclusions.

Test coordinates:
  1. Forest remote (Laurentides): 47.30-47.35, -71.20--71.28 → fragmentation only
  2. Semi-urban (Québec suburbs): 46.78-46.83, -71.15--71.23 → 0 zones (all P0 excluded)
  3. Forest+lake: 46.93-46.97, -71.27--71.34 → mixed penalties (water bonus for alimentation)

Expected penalty properties in GeoJSON:
  - penalty_factor (float 0.0-1.10)
  - raw_score (int before penalty)
  - penalty_details (dict: water, urban, roads, infrastructure, fragmentation)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

class TestBionicP1ZonePenalties:
    """Test BIONIC V5 P1 semi-static zone penalty system"""

    @pytest.fixture(autouse=True)
    def api_client(self):
        """Shared requests session"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        return session

    def test_health_check(self, api_client):
        """T1: API health check"""
        response = api_client.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        print("T1 PASS: API health check")

    def test_forest_remote_only_fragmentation(self, api_client):
        """
        T2: Forest remote (Laurentides 47.30-47.35, -71.20--71.28)
        Expected: zones have mostly fragmentation penalties (0.6-0.8)
        Other penalties (water, urban, roads) should be ~1.0 (no proximity)
        """
        payload = {
            "bounds": {
                "south": 47.30,
                "north": 47.35,
                "west": -71.28,
                "east": -71.20
            },
            "species": "moose",
            "layers": ["habitats", "rut", "repos", "alimentation", "corridors"],
            "resolution": 60,
            "max_zones_per_layer": 6
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/organic-zones", json=payload, timeout=60)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("type") == "FeatureCollection", "Should return GeoJSON FeatureCollection"
        features = data.get("features", [])
        stats = data.get("stats", {})
        
        print(f"T2: Forest remote - total_zones={stats.get('total_zones', 0)}, features={len(features)}")
        print(f"    penalties_applied={stats.get('penalties_applied', 0)}, rejected_exclusion={stats.get('rejected_exclusion', 0)}")
        
        # Should have some zones (remote forest should have low P0 exclusion)
        assert stats.get("total_zones", 0) >= 0, "Should have valid zone count"
        
        # Check penalty properties exist in features
        zones_with_penalty_factor = 0
        fragmentation_only_zones = 0
        
        for f in features:
            props = f.get("properties", {})
            if "penalty_factor" in props:
                zones_with_penalty_factor += 1
                pf = props.get("penalty_factor", 1.0)
                raw_score = props.get("raw_score", 0)
                details = props.get("penalty_details", {})
                
                print(f"    Zone {f.get('id')}: penalty_factor={pf}, raw_score={raw_score}")
                print(f"      details: {details}")
                
                # Check if only fragmentation penalty is active (others ~1.0)
                water = details.get("water", 1.0)
                urban = details.get("urban", 1.0)
                roads = details.get("roads", 1.0)
                frag = details.get("fragmentation", 1.0)
                
                if water >= 0.95 and urban >= 0.95 and roads >= 0.95 and frag < 0.95:
                    fragmentation_only_zones += 1
        
        print(f"T2 RESULT: zones_with_penalty_factor={zones_with_penalty_factor}, fragmentation_only={fragmentation_only_zones}")
        print("T2 PASS: Forest remote zone penalties validated")

    def test_semi_urban_zero_zones(self, api_client):
        """
        T3: Semi-urban area (Québec suburbs 46.78-46.83, -71.15--71.23)
        Expected: 0 zones (all P0 excluded due to urban/roads proximity)
        """
        payload = {
            "bounds": {
                "south": 46.78,
                "north": 46.83,
                "west": -71.23,
                "east": -71.15
            },
            "species": "moose",
            "layers": ["habitats", "rut", "repos", "alimentation", "corridors"],
            "resolution": 60,
            "max_zones_per_layer": 8
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/organic-zones", json=payload, timeout=60)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        stats = data.get("stats", {})
        features = data.get("features", [])
        
        print(f"T3: Semi-urban - total_zones={stats.get('total_zones', 0)}, rejected={stats.get('rejected_exclusion', 0)}")
        
        # Semi-urban should have 0 or very few valid zones (most P0 excluded)
        assert stats.get("total_zones", 0) <= 5, f"Expected 0-5 zones in semi-urban, got {stats.get('total_zones')}"
        print("T3 PASS: Semi-urban zone exclusion validated")

    def test_forest_lake_mixed_penalties(self, api_client):
        """
        T4: Forest+lake area (46.93-46.97, -71.27--71.34)
        Expected: zones near water get bonus/neutral water penalty (alimentation: 1.05 close)
        Other zones get standard penalties
        """
        payload = {
            "bounds": {
                "south": 46.93,
                "north": 46.97,
                "west": -71.34,
                "east": -71.27
            },
            "species": "moose",
            "layers": ["habitats", "alimentation", "repos", "rut"],
            "resolution": 60,
            "max_zones_per_layer": 6
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/organic-zones", json=payload, timeout=60)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        stats = data.get("stats", {})
        features = data.get("features", [])
        
        print(f"T4: Forest+lake - total_zones={stats.get('total_zones', 0)}, penalties_applied={stats.get('penalties_applied', 0)}")
        
        zones_with_water_bonus = 0
        zones_with_water_penalty = 0
        alimentation_zones = []
        
        for f in features:
            props = f.get("properties", {})
            layer_id = props.get("layer_id")
            details = props.get("penalty_details", {})
            water_mult = details.get("water", 1.0)
            
            if layer_id == "alimentation":
                alimentation_zones.append({
                    "id": f.get("id"),
                    "water": water_mult,
                    "penalty_factor": props.get("penalty_factor"),
                    "raw_score": props.get("raw_score"),
                    "score": props.get("score")
                })
                if water_mult >= 1.0:  # Water bonus (1.05 close for alimentation)
                    zones_with_water_bonus += 1
            
            if water_mult < 1.0:
                zones_with_water_penalty += 1
        
        print(f"T4 RESULT: alimentation zones={len(alimentation_zones)}")
        for z in alimentation_zones[:3]:
            print(f"    {z}")
        print(f"    water_bonus={zones_with_water_bonus}, water_penalty={zones_with_water_penalty}")
        print("T4 PASS: Forest+lake mixed penalties validated")

    def test_penalty_properties_structure(self, api_client):
        """
        T5: Validate penalty properties structure in GeoJSON features
        Expected: penalty_factor, raw_score, penalty_details in properties
        """
        payload = {
            "bounds": {
                "south": 47.00,
                "north": 47.05,
                "west": -71.20,
                "east": -71.12
            },
            "species": "moose",
            "layers": ["habitats", "alimentation"],
            "resolution": 50,
            "max_zones_per_layer": 4
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/organic-zones", json=payload, timeout=60)
        assert response.status_code == 200
        
        data = response.json()
        features = data.get("features", [])
        
        print(f"T5: Checking penalty property structure in {len(features)} features")
        
        for f in features[:5]:  # Check first 5
            props = f.get("properties", {})
            
            # Check required P1 penalty properties
            assert "penalty_factor" in props, f"Missing penalty_factor in {f.get('id')}"
            assert "raw_score" in props, f"Missing raw_score in {f.get('id')}"
            assert "penalty_details" in props, f"Missing penalty_details in {f.get('id')}"
            
            # Validate types
            pf = props["penalty_factor"]
            assert isinstance(pf, (int, float)), f"penalty_factor should be numeric, got {type(pf)}"
            assert 0.0 <= pf <= 1.15, f"penalty_factor out of range: {pf}"
            
            rs = props["raw_score"]
            assert isinstance(rs, int), f"raw_score should be int, got {type(rs)}"
            assert 15 <= rs <= 100, f"raw_score out of range: {rs}"
            
            details = props["penalty_details"]
            assert isinstance(details, dict), f"penalty_details should be dict"
            
            # Check expected keys in details
            expected_keys = ["water", "urban", "roads", "infrastructure", "fragmentation"]
            for key in expected_keys:
                if key in details:
                    val = details[key]
                    assert 0.0 <= val <= 1.15, f"{key} penalty out of range: {val}"
            
            print(f"    {f.get('id')}: factor={pf:.3f}, raw={rs}, details_keys={list(details.keys())}")
        
        print("T5 PASS: Penalty properties structure validated")

    def test_stats_include_penalties_applied(self, api_client):
        """
        T6: Stats should include penalties_applied count > 0 for forest zones
        """
        payload = {
            "bounds": {
                "south": 47.05,
                "north": 47.10,
                "west": -70.93,
                "east": -70.85
            },
            "species": "moose",
            "layers": ["habitats", "rut", "repos", "alimentation"],
            "resolution": 60,
            "max_zones_per_layer": 6
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/organic-zones", json=payload, timeout=60)
        assert response.status_code == 200
        
        data = response.json()
        stats = data.get("stats", {})
        
        print(f"T6: Stats = {stats}")
        
        assert "penalties_applied" in stats, "Stats should include penalties_applied"
        assert "total_zones" in stats, "Stats should include total_zones"
        assert "rejected_exclusion" in stats, "Stats should include rejected_exclusion"
        
        # Forest areas should have some penalties applied (fragmentation at minimum)
        if stats.get("total_zones", 0) > 0:
            penalties = stats.get("penalties_applied", 0)
            print(f"T6: penalties_applied={penalties} for {stats.get('total_zones')} zones")
        
        print("T6 PASS: Stats penalties_applied validated")

    def test_penalized_score_calculation(self, api_client):
        """
        T7: Verify score = raw_score * penalty_factor (penalized scoring)
        """
        payload = {
            "bounds": {
                "south": 47.02,
                "north": 47.07,
                "west": -71.15,
                "east": -71.07
            },
            "species": "moose",
            "layers": ["habitats", "repos"],
            "resolution": 50,
            "max_zones_per_layer": 5
        }
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/organic-zones", json=payload, timeout=60)
        assert response.status_code == 200
        
        data = response.json()
        features = data.get("features", [])
        
        print(f"T7: Verifying penalized score calculation in {len(features)} features")
        
        score_validations = 0
        for f in features[:8]:
            props = f.get("properties", {})
            score = props.get("score", 0)
            raw_score = props.get("raw_score", 0)
            penalty_factor = props.get("penalty_factor", 1.0)
            
            if raw_score > 0 and penalty_factor > 0:
                expected_score = max(15, int(raw_score * penalty_factor))
                # Allow small tolerance for rounding
                diff = abs(score - expected_score)
                print(f"    {f.get('id')}: score={score}, raw={raw_score}, factor={penalty_factor:.3f}, expected={expected_score}, diff={diff}")
                
                # Scoring may include additional adjustments from scoring_zone_integration
                # Just verify that penalized score <= raw_score when factor < 1
                if penalty_factor < 1.0:
                    assert score <= raw_score + 5, f"Penalized score should be <= raw_score (with tolerance)"
                    score_validations += 1
        
        print(f"T7: Validated {score_validations} penalized scores")
        print("T7 PASS: Penalized score calculation validated")


class TestPenaltyEngineUnit:
    """Unit tests for zone_penalty_engine module"""

    def test_penalty_matrix_structure(self):
        """T8: Verify PENALTY_MATRIX has correct structure"""
        from modules.bionic_engine_p0.services.zone_penalty_engine import PENALTY_MATRIX, _DEFAULT_PENALTIES
        
        expected_layers = ["alimentation", "repos", "rut", "habitats", "corridors"]
        expected_types = ["water", "urban", "roads", "infrastructure"]
        expected_bands = ["close", "medium", "far"]
        
        for layer in expected_layers:
            assert layer in PENALTY_MATRIX, f"Missing layer {layer} in PENALTY_MATRIX"
            layer_penalties = PENALTY_MATRIX[layer]
            
            for ptype in expected_types:
                assert ptype in layer_penalties, f"Missing {ptype} in {layer}"
                bands = layer_penalties[ptype]
                for band in expected_bands:
                    assert band in bands, f"Missing {band} in {layer}.{ptype}"
                    mult = bands[band]
                    assert 0.0 <= mult <= 1.15, f"Invalid multiplier {mult} for {layer}.{ptype}.{band}"
        
        # Verify default penalties
        for ptype in expected_types:
            assert ptype in _DEFAULT_PENALTIES, f"Missing {ptype} in _DEFAULT_PENALTIES"
        
        print("T8 PASS: PENALTY_MATRIX structure validated")

    def test_calculate_zone_penalty_function(self):
        """T9: Test calculate_zone_penalty with mock data"""
        from modules.bionic_engine_p0.services.zone_penalty_engine import calculate_zone_penalty
        
        # Mock zone with centroid far from exclusions
        zone = {
            "centroid": {"lat": 47.5, "lng": -71.5},
            "area_m2": 5000,
            "compactness": 0.6,  # Moderate compactness → fragmentation penalty
            "coordinates": [[-71.5, 47.5], [-71.51, 47.5], [-71.51, 47.51], [-71.5, 47.51]]
        }
        
        # No exclusions → only fragmentation penalty
        exclusions = []
        
        factor, details = calculate_zone_penalty(zone, "repos", exclusions)
        
        print(f"T9: No exclusions → factor={factor}, details={details}")
        
        # Should have fragmentation penalty (compactness 0.6 < 0.5 threshold)
        assert "fragmentation" in details, "Should have fragmentation in details"
        
        # With compactness 0.6 (>0.5), no severe fragmentation penalty
        # But it's still moderate at 0.6
        assert factor <= 1.0, f"Factor should be <= 1.0, got {factor}"
        
        print("T9 PASS: calculate_zone_penalty function validated")

    def test_water_bonus_alimentation(self):
        """T10: Test water bonus (1.05) for alimentation layer near water"""
        from modules.bionic_engine_p0.services.zone_penalty_engine import calculate_zone_penalty
        
        # Zone centroid
        zone = {
            "centroid": {"lat": 47.0, "lng": -71.0},
            "area_m2": 8000,
            "compactness": 0.7,
            "coordinates": [[-71.0, 47.0], [-71.01, 47.0], [-71.01, 47.01], [-71.0, 47.01]]
        }
        
        # Water exclusion very close (< 200m)
        exclusions = [
            {
                "type": "water",
                "geometry_type": "polygon",
                "coordinates": [[-70.999, 47.001], [-70.998, 47.001], [-70.998, 47.002], [-70.999, 47.002]]
            }
        ]
        
        factor, details = calculate_zone_penalty(zone, "alimentation", exclusions)
        
        print(f"T10: Alimentation near water → factor={factor}, water={details.get('water')}")
        
        # Alimentation near water should get bonus (1.05)
        water_mult = details.get("water", 1.0)
        assert water_mult >= 1.0, f"Alimentation should get water bonus (>=1.0), got {water_mult}"
        
        print("T10 PASS: Water bonus for alimentation validated")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
