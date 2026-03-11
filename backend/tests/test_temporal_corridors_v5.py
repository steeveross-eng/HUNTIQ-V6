"""
Test: BIONIC V5 ULTIME 300% — Temporal Corridors + Tooltips Batch 1
=====================================================================
Tests movement corridors API with time_of_day parameter:
- time_of_day=6 should return temporal_activity corridor (peak hour for moose)
- time_of_day=14 should NOT return temporal_activity corridor (non-peak)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestTemporalCorridorsV5:
    """Test temporal corridors with time_of_day parameter"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Skip tests if BASE_URL not set"""
        if not BASE_URL:
            pytest.skip("REACT_APP_BACKEND_URL not set")
    
    def test_corridors_status_endpoint(self):
        """T1: Verify movement-corridors status endpoint works"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/movement-corridors/status")
        assert response.status_code == 200, f"Status check failed: {response.text}"
        
        data = response.json()
        assert data["status"] == "ACTIVE"
        assert "temporal_activity" in data["corridor_types"]["estimated"]
        print(f"PASS: Status endpoint active, temporal_activity available")
    
    def test_corridors_compute_at_peak_hour_6(self):
        """T2: time_of_day=6 should return temporal_activity corridor (moose peak hour)"""
        payload = {
            "bounds": {"north": 47.0, "south": 46.5, "east": -71.0, "west": -71.5},
            "species": "moose",
            "time_of_day": 6  # Peak activity hour for moose [5,6,7,17,18,19]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/movement-corridors/compute",
            json=payload
        )
        assert response.status_code == 200, f"Compute failed: {response.text}"
        
        data = response.json()
        assert "estimated_corridors" in data
        
        # Check for temporal_activity corridor
        temporal_corridors = [c for c in data["estimated_corridors"] if c["corridor_type"] == "temporal_activity"]
        assert len(temporal_corridors) > 0, "Expected temporal_activity corridor at hour 6 (peak)"
        
        # Verify it has dashed line style
        tc = temporal_corridors[0]
        assert tc["style"]["dashArray"] is not None, "Estimated corridor should have dashArray (dashed line)"
        assert tc["category"] == "estimated", "Temporal corridor should be categorized as estimated"
        assert "aube" in tc["name"].lower() or "6h" in tc["name"], f"Expected dawn reference in name: {tc['name']}"
        
        print(f"PASS: temporal_activity corridor found at hour 6: {tc['name']}")
        print(f"  - Score: {tc['score']}%")
        print(f"  - DashArray: {tc['style']['dashArray']}")
    
    def test_corridors_compute_at_non_peak_hour_14(self):
        """T3: time_of_day=14 should NOT return temporal_activity corridor (non-peak)"""
        payload = {
            "bounds": {"north": 47.0, "south": 46.5, "east": -71.0, "west": -71.5},
            "species": "moose",
            "time_of_day": 14  # NOT a peak activity hour
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/movement-corridors/compute",
            json=payload
        )
        assert response.status_code == 200, f"Compute failed: {response.text}"
        
        data = response.json()
        assert "estimated_corridors" in data
        
        # Check that NO temporal_activity corridor is returned
        temporal_corridors = [c for c in data["estimated_corridors"] if c["corridor_type"] == "temporal_activity"]
        assert len(temporal_corridors) == 0, f"Expected NO temporal_activity corridor at hour 14, but found {len(temporal_corridors)}"
        
        print(f"PASS: No temporal_activity corridor at hour 14 (non-peak)")
        print(f"  - Estimated corridors: {[c['corridor_type'] for c in data['estimated_corridors']]}")
    
    def test_corridors_real_vs_estimated_style(self):
        """T4: Real corridors have solid lines, estimated have dashed"""
        payload = {
            "bounds": {"north": 47.0, "south": 46.5, "east": -71.0, "west": -71.5},
            "species": "moose",
            "time_of_day": 6,
            "wind_speed": 20,  # Trigger wind_driven corridor
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/movement-corridors/compute",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check real corridors - solid lines
        for rc in data["real_corridors"]:
            assert rc["style"]["dashArray"] is None, f"Real corridor should have solid line (dashArray=null): {rc['name']}"
            assert rc["category"] == "real"
        
        # Check estimated corridors - dashed lines
        for ec in data["estimated_corridors"]:
            assert ec["style"]["dashArray"] is not None, f"Estimated corridor should have dashed line: {ec['name']}"
            assert ec["category"] == "estimated"
        
        print(f"PASS: Real corridors ({len(data['real_corridors'])}) have solid lines")
        print(f"PASS: Estimated corridors ({len(data['estimated_corridors'])}) have dashed lines")
    
    def test_corridors_metadata_contains_time_of_day(self):
        """T5: Verify metadata returns the time_of_day used"""
        payload = {
            "bounds": {"north": 47.0, "south": 46.5, "east": -71.0, "west": -71.5},
            "species": "moose",
            "time_of_day": 18  # Evening peak
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/movement-corridors/compute",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "metadata" in data
        assert "conditions" in data["metadata"]
        assert data["metadata"]["conditions"]["time_of_day"] == 18
        
        print(f"PASS: Metadata contains time_of_day: {data['metadata']['conditions']['time_of_day']}")
    
    def test_peak_hours_for_moose(self):
        """T6: Verify all peak hours generate temporal_activity"""
        peak_hours = [5, 6, 7, 17, 18, 19]
        
        for hour in peak_hours:
            payload = {
                "bounds": {"north": 47.0, "south": 46.5, "east": -71.0, "west": -71.5},
                "species": "moose",
                "time_of_day": hour
            }
            
            response = requests.post(
                f"{BASE_URL}/api/v1/bionic/movement-corridors/compute",
                json=payload
            )
            assert response.status_code == 200
            data = response.json()
            
            temporal = [c for c in data["estimated_corridors"] if c["corridor_type"] == "temporal_activity"]
            assert len(temporal) > 0, f"Expected temporal_activity at peak hour {hour}"
            print(f"  Hour {hour}: temporal_activity found ✓")
        
        print(f"PASS: All 6 peak hours generate temporal_activity corridor")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
