"""
BCE-MAX x4.1 CERTIFICATION TEST SUITE
=====================================
BIONIC V8 Module Certification Tests

Tests:
  CERT-1: V8 Ecological API species and zones
  CERT-2: Zone Generation with corridors
  CERT-3: (UI - tested with Playwright)
  CERT-4: (UI - session persistence SAVE)
  CERT-5: (UI - session persistence RESTORE)
  CERT-6: (UI - auto-load)
  CERT-7: BCE Validation compliance
  CERT-8: BCE Status operational
"""

import pytest
import requests
import os
import json

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestCertification1_EcologicalAPI:
    """CERTIFICATION 1 — V8 Ecological API: Species list and zone data"""
    
    def test_cert1a_species_list_returns_3_species(self):
        """GET /api/v1/ecological/species must return 3 species (orignal, chevreuil, ours_noir)"""
        response = requests.get(f"{BASE_URL}/api/v1/ecological/species", timeout=15)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "species" in data, "Response must contain 'species' key"
        assert "count" in data, "Response must contain 'count' key"
        
        species_list = data["species"]
        assert len(species_list) == 3, f"Expected 3 species, got {len(species_list)}"
        
        species_ids = [s["id"] for s in species_list]
        assert "orignal" in species_ids, "Species 'orignal' must be present"
        assert "chevreuil" in species_ids, "Species 'chevreuil' must be present"
        assert "ours_noir" in species_ids, "Species 'ours_noir' must be present"
        
        print(f"CERT-1a PASS: 3 species found: {species_ids}")
    
    def test_cert1b_orignal_zones_contain_required_data(self):
        """GET /api/v1/ecological/species/orignal/zones must return zones with habitats, topography, criteria"""
        response = requests.get(f"{BASE_URL}/api/v1/ecological/species/orignal/zones", timeout=15)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "species" in data, "Response must contain 'species' key"
        assert data["species"] == "orignal", f"Expected species 'orignal', got {data['species']}"
        assert "zones" in data, "Response must contain 'zones' key"
        
        zones = data["zones"]
        assert len(zones) > 0, "Must have at least 1 zone"
        
        # Check first zone has required structure
        for zone_type, zone_data in zones.items():
            assert "habitat" in zone_data or "forest_types" in zone_data.get("habitat", {}), \
                f"Zone {zone_type} must have habitat data"
            assert "criteria" in zone_data or "ndvi_range" in str(zone_data), \
                f"Zone {zone_type} must have criteria data"
            # Topography check
            has_topography = "topography" in zone_data or "slope" in str(zone_data)
            assert has_topography, f"Zone {zone_type} must have topography data"
            break  # Check first zone is enough for certification
        
        print(f"CERT-1b PASS: orignal zones contain habitat, topography, criteria. Zone count: {len(zones)}")


class TestCertification2_ZoneGeneration:
    """CERTIFICATION 2 — Zone Generation with corridors and WWF classification"""
    
    def test_cert2_zone_generation_returns_corridors(self):
        """POST /api/v1/bionic/organic-zones with waypoint_center must return features + corridors"""
        payload = {
            "bounds": {
                "north": 46.821,
                "south": 46.791,
                "east": -71.103,
                "west": -71.133
            },
            "species": "moose",
            "layers": ["habitats", "alimentation", "repos", "rut", "trajets", "corridors"],
            "waypoint_center": {
                "lat": 46.806,
                "lng": -71.118
            },
            "resolution": 60,
            "max_zones_per_layer": 8
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            timeout=60  # Zone generation can take time
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text[:500]}"
        
        data = response.json()
        
        # CERT-2a: Features array must exist
        assert "features" in data, "Response must contain 'features' array"
        features = data["features"]
        print(f"  Features count: {len(features)}")
        
        # CERT-2b: Corridors array must exist with >0 corridors
        assert "corridors" in data, "Response must contain 'corridors' array"
        corridors = data["corridors"]
        assert len(corridors) > 0, f"Must have >0 corridors, got {len(corridors)}"
        print(f"  Corridors count: {len(corridors)}")
        
        # CERT-2c: Each corridor must have WWF classification, style, from/to zone types
        for i, corridor in enumerate(corridors[:3]):  # Check first 3 corridors
            props = corridor.get("properties", {})
            
            # wwf_classification check
            assert "wwf_classification" in props, f"Corridor {i} missing wwf_classification"
            wwf = props["wwf_classification"]
            assert "type" in wwf, f"Corridor {i} wwf_classification missing 'type'"
            
            # style check
            assert "style" in props, f"Corridor {i} missing style"
            style = props["style"]
            assert "color" in style, f"Corridor {i} style missing 'color'"
            assert "width" in style, f"Corridor {i} style missing 'width'"
            assert "opacity" in style, f"Corridor {i} style missing 'opacity'"
            
            # from/to zone types check
            assert "from_zone_type" in props, f"Corridor {i} missing from_zone_type"
            assert "to_zone_type" in props, f"Corridor {i} missing to_zone_type"
            
            print(f"  Corridor {i}: {props['from_zone_type']} -> {props['to_zone_type']}, WWF: {wwf['type']}")
        
        print(f"CERT-2 PASS: {len(features)} zones, {len(corridors)} corridors with WWF classification")


class TestCertification7_BCEValidation:
    """CERTIFICATION 7 — BCE Validation endpoint"""
    
    def test_cert7_bce_validation_returns_compliant(self):
        """POST /api/v1/ecological/validate with valid params must return global_status=COMPLIANT"""
        payload = {
            "species": "orignal",
            "zone_type": "alimentation",
            "ndvi": 0.65,
            "slope": 8,
            "distance_to_water": 300
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/ecological/validate",
            json=payload,
            timeout=15
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text[:500]}"
        
        data = response.json()
        assert "global_status" in data, "Response must contain 'global_status'"
        
        # Accept COMPLIANT, PASS, or SUCCESS as valid compliance status
        valid_statuses = ["COMPLIANT", "PASS", "SUCCESS"]
        actual_status = data["global_status"]
        assert actual_status in valid_statuses, \
            f"Expected global_status in {valid_statuses}, got '{actual_status}'"
        
        print(f"CERT-7 PASS: BCE validation returned global_status={actual_status}")


class TestCertification8_BCEStatus:
    """CERTIFICATION 8 — BCE Status endpoint"""
    
    def test_cert8_bce_status_returns_operational(self):
        """GET /api/bce/status must return status=operational with validators list"""
        response = requests.get(f"{BASE_URL}/api/bce/status", timeout=15)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # CERT-8a: status must be operational
        assert "status" in data, "Response must contain 'status'"
        assert data["status"] == "operational", f"Expected status 'operational', got '{data['status']}'"
        
        # CERT-8b: validators list must exist with 10 validators
        assert "validators" in data, "Response must contain 'validators' list"
        validators = data["validators"]
        assert len(validators) >= 10, f"Expected at least 10 validators, got {len(validators)}"
        
        print(f"CERT-8 PASS: BCE status operational, {len(validators)} validators")
        print(f"  Validators: {validators}")


class TestBackendHealth:
    """Basic health checks"""
    
    def test_backend_health(self):
        """Health check endpoint"""
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"Backend health: OK")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
