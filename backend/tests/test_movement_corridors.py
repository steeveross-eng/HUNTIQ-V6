"""
Test Suite: Movement Corridors API (BIONIC V5)
Tests for real vs estimated movement corridors endpoints.
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://corridor-analysis.preview.emergentagent.com')

class TestMovementCorridorsStatus:
    """Test GET /api/v1/bionic/movement-corridors/status endpoint"""
    
    def test_status_returns_active(self):
        """Verify status endpoint returns ACTIVE status"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/movement-corridors/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ACTIVE"
        assert data["module"] == "MOVEMENT_CORRIDORS"
        assert data["version"] == "movement_corridors_v1"
    
    def test_status_has_categories(self):
        """Verify status returns real and estimated categories"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/movement-corridors/status")
        data = response.json()
        
        assert "categories" in data
        assert "real" in data["categories"]
        assert "estimated" in data["categories"]
        # Real corridors are solid lines (continuous)
        assert "lignes continues" in data["categories"]["real"] or "semi-statiques" in data["categories"]["real"]
        # Estimated corridors are dashed lines
        assert "pointillées" in data["categories"]["estimated"] or "dynamiques" in data["categories"]["estimated"]
    
    def test_status_has_five_species(self):
        """Verify status returns exactly 5 species"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/movement-corridors/status")
        data = response.json()
        
        assert "species" in data
        assert len(data["species"]) == 5
        assert "moose" in data["species"]
        assert "deer" in data["species"]
        assert "bear" in data["species"]
        assert "wild_turkey" in data["species"]
        assert "elk" in data["species"]
    
    def test_status_has_corridor_types(self):
        """Verify status lists corridor types for real and estimated"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/movement-corridors/status")
        data = response.json()
        
        assert "corridor_types" in data
        # Real types
        assert "connectivity" in data["corridor_types"]["real"]
        assert "feeding_transit" in data["corridor_types"]["real"]
        # Estimated types
        assert "wind_driven" in data["corridor_types"]["estimated"]
        assert "thermal" in data["corridor_types"]["estimated"]
        assert "pressure_avoidance" in data["corridor_types"]["estimated"]
        assert "temporal_activity" in data["corridor_types"]["estimated"]


class TestMovementCorridorsCompute:
    """Test POST /api/v1/bionic/movement-corridors/compute endpoint"""
    
    def test_compute_returns_real_and_estimated(self):
        """Verify compute returns both real and estimated corridors"""
        payload = {
            "bounds": {"north": 46.85, "south": 46.75, "east": -71.15, "west": -71.30},
            "species": "moose"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/movement-corridors/compute",
            json=payload
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "real_corridors" in data
        assert "estimated_corridors" in data
        assert len(data["real_corridors"]) > 0
        assert len(data["estimated_corridors"]) > 0
    
    def test_real_corridors_are_solid_lines(self):
        """Verify real corridors have dashArray = null (solid lines)"""
        payload = {
            "bounds": {"north": 46.85, "south": 46.75, "east": -71.15, "west": -71.30},
            "species": "moose"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/movement-corridors/compute",
            json=payload
        )
        data = response.json()
        
        for corridor in data["real_corridors"]:
            assert corridor["category"] == "real"
            assert corridor["style"]["dashArray"] is None, f"Real corridor {corridor['id']} should have dashArray = null (solid line)"
            assert corridor["corridor_type"] in ["connectivity", "feeding_transit"]
    
    def test_estimated_corridors_are_dashed_lines(self):
        """Verify estimated corridors have dashArray set (dashed lines)"""
        payload = {
            "bounds": {"north": 46.85, "south": 46.75, "east": -71.15, "west": -71.30},
            "species": "moose"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/movement-corridors/compute",
            json=payload
        )
        data = response.json()
        
        for corridor in data["estimated_corridors"]:
            assert corridor["category"] == "estimated"
            assert corridor["style"]["dashArray"] is not None, f"Estimated corridor {corridor['id']} should have dashArray set (dashed line)"
            assert corridor["corridor_type"] in ["wind_driven", "thermal", "pressure_avoidance", "temporal_activity"]
    
    def test_corridors_have_required_fields(self):
        """Verify corridors have all required fields"""
        payload = {
            "bounds": {"north": 46.85, "south": 46.75, "east": -71.15, "west": -71.30},
            "species": "moose"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/movement-corridors/compute",
            json=payload
        )
        data = response.json()
        
        all_corridors = data["real_corridors"] + data["estimated_corridors"]
        for corridor in all_corridors:
            # Check required fields
            assert "id" in corridor
            assert "category" in corridor
            assert "corridor_type" in corridor
            assert "name" in corridor
            assert "description" in corridor
            assert "points" in corridor
            assert len(corridor["points"]) >= 2
            assert "score" in corridor
            assert "probability" in corridor
            assert "style" in corridor
            assert "factors" in corridor
            
            # Validate points structure
            for point in corridor["points"]:
                assert "lat" in point
                assert "lng" in point
            
            # Validate style fields
            assert "color" in corridor["style"]
            assert "weight" in corridor["style"]
            assert "opacity" in corridor["style"]
    
    def test_metadata_is_returned(self):
        """Verify metadata is returned with computation details"""
        payload = {
            "bounds": {"north": 46.85, "south": 46.75, "east": -71.15, "west": -71.30},
            "species": "moose"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/movement-corridors/compute",
            json=payload
        )
        data = response.json()
        
        assert "metadata" in data
        assert "calculation_time_ms" in data["metadata"]
        assert "real_count" in data["metadata"]
        assert "estimated_count" in data["metadata"]
        assert "total_count" in data["metadata"]
        assert "bounds" in data["metadata"]
        
        # Verify counts match
        assert data["metadata"]["real_count"] == len(data["real_corridors"])
        assert data["metadata"]["estimated_count"] == len(data["estimated_corridors"])
        assert data["metadata"]["total_count"] == len(data["real_corridors"]) + len(data["estimated_corridors"])
    
    def test_compute_with_different_species(self):
        """Test compute works with different species"""
        for species in ["moose", "deer", "bear"]:
            payload = {
                "bounds": {"north": 46.85, "south": 46.75, "east": -71.15, "west": -71.30},
                "species": species
            }
            response = requests.post(
                f"{BASE_URL}/api/v1/bionic/movement-corridors/compute",
                json=payload
            )
            assert response.status_code == 200
            data = response.json()
            assert data["species"] == species


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
