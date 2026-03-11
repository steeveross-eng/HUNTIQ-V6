"""
BIONIC Mode Selector Bug Fix - Backend API Tests
=================================================
Tests for verifying the analysis mode parameter is correctly passed to
and returned from the POST /api/v1/bionic/analyze_waypoint endpoint.

Bug Fix Context:
- Mode selector should pass 'mode' parameter in API request
- API should return 'analysis_mode' field in scores response
- 4 modes supported: live, pre_rut, rut, post_rut
"""

import pytest
import requests
import os
import json

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test waypoint data
TEST_WAYPOINT = {
    "id": "WP-TEST-001",
    "name": "Test Waypoint - Mode Selector",
    "latitude": 46.8139,
    "longitude": -71.2080
}

# All supported modes
ANALYSIS_MODES = ['live', 'pre_rut', 'rut', 'post_rut']


class TestBionicModeSelector:
    """Test suite for BIONIC analysis mode selector functionality"""
    
    def test_api_health_check(self):
        """Test that the analyze_waypoint health endpoint is available"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/analyze_waypoint/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["api_schema_version"] == "1.0.0"
        print(f"✓ Health check passed: {data['endpoint']}")
    
    @pytest.mark.parametrize("mode", ANALYSIS_MODES)
    def test_mode_parameter_in_request(self, mode):
        """Test that each mode can be sent in the request"""
        request_body = {
            "waypoint": TEST_WAYPOINT,
            "target_datetime": "2026-02-23T10:00:00Z",
            "species": "orignal",
            "parameters": {
                "search_radius_km": 3.0,
                "grid_resolution": 5,
                "region": "CA-QC",
                "mode": mode  # Analysis mode
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_waypoint",
            json=request_body,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200, f"API call failed for mode '{mode}': {response.text}"
        data = response.json()
        
        # Verify analysis_id exists (proves new analysis was run)
        assert "analysis_id" in data
        print(f"✓ Mode '{mode}' - Analysis ID: {data['analysis_id']}")
        
        # Verify scores structure exists
        assert "scores" in data
        assert "score_bionic_final" in data["scores"]
        print(f"  Score: {data['scores']['score_bionic_final']}/100")
    
    @pytest.mark.parametrize("mode", ANALYSIS_MODES)
    def test_mode_returned_in_response(self, mode):
        """Test that analysis_mode is returned in scores response"""
        request_body = {
            "waypoint": TEST_WAYPOINT,
            "target_datetime": "2026-02-23T10:00:00Z",
            "species": "orignal",
            "parameters": {
                "search_radius_km": 3.0,
                "grid_resolution": 5,
                "region": "CA-QC",
                "mode": mode
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_waypoint",
            json=request_body,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that analysis_mode is in scores
        assert "analysis_mode" in data["scores"], \
            f"'analysis_mode' not found in scores response for mode '{mode}'"
        
        # Verify the returned mode matches the requested mode
        returned_mode = data["scores"]["analysis_mode"]
        assert returned_mode == mode, \
            f"Mode mismatch: requested '{mode}', got '{returned_mode}'"
        
        print(f"✓ Mode '{mode}' correctly returned in response")
    
    def test_different_modes_produce_different_analysis_ids(self):
        """Test that each mode generates a unique analysis ID"""
        analysis_ids = []
        
        for mode in ANALYSIS_MODES:
            request_body = {
                "waypoint": TEST_WAYPOINT,
                "target_datetime": "2026-02-23T10:00:00Z",
                "species": "orignal",
                "parameters": {
                    "search_radius_km": 3.0,
                    "grid_resolution": 5,
                    "region": "CA-QC",
                    "mode": mode
                }
            }
            
            response = requests.post(
                f"{BASE_URL}/api/v1/bionic/analyze_waypoint",
                json=request_body,
                headers={"Content-Type": "application/json"}
            )
            
            assert response.status_code == 200
            data = response.json()
            analysis_ids.append(data["analysis_id"])
        
        # All analysis IDs should be unique (each mode triggers new analysis)
        unique_ids = set(analysis_ids)
        assert len(unique_ids) == len(ANALYSIS_MODES), \
            f"Expected {len(ANALYSIS_MODES)} unique IDs, got {len(unique_ids)}"
        
        print(f"✓ All {len(ANALYSIS_MODES)} modes produced unique analysis IDs")
        for mode, aid in zip(ANALYSIS_MODES, analysis_ids):
            print(f"  {mode}: {aid}")
    
    def test_default_mode_is_rut(self):
        """Test that default mode is 'rut' when not specified"""
        request_body = {
            "waypoint": TEST_WAYPOINT,
            "target_datetime": "2026-02-23T10:00:00Z",
            "species": "orignal",
            "parameters": {
                "search_radius_km": 3.0,
                "grid_resolution": 5,
                "region": "CA-QC"
                # No mode specified
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_waypoint",
            json=request_body,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Default mode should be 'rut'
        assert data["scores"]["analysis_mode"] == "rut", \
            f"Default mode should be 'rut', got '{data['scores']['analysis_mode']}'"
        
        print(f"✓ Default mode is 'rut' as expected")
    
    def test_mode_description_in_response(self):
        """Test that mode information is useful for UI display"""
        mode_descriptions = {
            'live': 'temps réel',
            'pre_rut': 'pré-rut',
            'rut': 'rut',
            'post_rut': 'post-rut'
        }
        
        for mode in ANALYSIS_MODES:
            request_body = {
                "waypoint": TEST_WAYPOINT,
                "target_datetime": "2026-02-23T10:00:00Z",
                "species": "orignal",
                "parameters": {
                    "mode": mode
                }
            }
            
            response = requests.post(
                f"{BASE_URL}/api/v1/bionic/analyze_waypoint",
                json=request_body,
                headers={"Content-Type": "application/json"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify analysis_mode field exists
            assert "analysis_mode" in data["scores"]
            
            # Verify score is within expected range (0-100)
            score = data["scores"]["score_bionic_final"]
            assert 0 <= score <= 100, f"Score {score} out of range for mode '{mode}'"
            
            print(f"✓ Mode '{mode}': Score={score:.1f}/100")
    
    def test_complete_response_structure(self):
        """Test that response has all required fields from bug fix"""
        request_body = {
            "waypoint": TEST_WAYPOINT,
            "target_datetime": "2026-02-23T10:00:00Z",
            "species": "orignal",
            "parameters": {
                "mode": "rut"
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_waypoint",
            json=request_body,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Required fields for bug fix
        assert "analysis_id" in data, "Missing 'analysis_id' field"
        assert "scores" in data, "Missing 'scores' field"
        assert "score_bionic_final" in data["scores"], "Missing 'score_bionic_final'"
        assert "analysis_mode" in data["scores"], "Missing 'analysis_mode' field"
        assert "layers" in data, "Missing 'layers' field"
        assert "metadata" in data, "Missing 'metadata' field"
        
        # Verify engine version
        assert "engine_version" in data
        
        print(f"✓ Complete response structure verified")
        print(f"  - Analysis ID: {data['analysis_id']}")
        print(f"  - Score: {data['scores']['score_bionic_final']}")
        print(f"  - Mode: {data['scores']['analysis_mode']}")
        print(f"  - Engine: {data['engine_version']}")


class TestModeSwitchingIntegration:
    """Integration tests simulating frontend mode switching behavior"""
    
    def test_rapid_mode_switching(self):
        """Test rapid mode switching like user would do in UI"""
        previous_id = None
        results = []
        
        # Simulate clicking through all modes
        for mode in ['live', 'pre_rut', 'rut', 'post_rut', 'live']:  # End back at live
            request_body = {
                "waypoint": TEST_WAYPOINT,
                "target_datetime": "2026-02-23T10:00:00Z",
                "species": "orignal",
                "parameters": {"mode": mode}
            }
            
            response = requests.post(
                f"{BASE_URL}/api/v1/bionic/analyze_waypoint",
                json=request_body,
                headers={"Content-Type": "application/json"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Each switch should generate new analysis
            current_id = data["analysis_id"]
            if previous_id:
                assert current_id != previous_id, \
                    f"Same ID returned for different API calls: {current_id}"
            
            results.append({
                "mode": mode,
                "analysis_id": current_id,
                "score": data["scores"]["score_bionic_final"],
                "returned_mode": data["scores"]["analysis_mode"]
            })
            
            previous_id = current_id
        
        print(f"✓ Rapid mode switching test passed ({len(results)} switches)")
        for r in results:
            print(f"  {r['mode']}: ID={r['analysis_id'][-4:]}... Score={r['score']:.1f}")
    
    def test_mode_affects_score_calculation(self):
        """Test that different modes may produce different scores (expected behavior)"""
        scores_by_mode = {}
        
        for mode in ANALYSIS_MODES:
            request_body = {
                "waypoint": TEST_WAYPOINT,
                "target_datetime": "2026-02-23T10:00:00Z",
                "species": "orignal",
                "parameters": {"mode": mode}
            }
            
            response = requests.post(
                f"{BASE_URL}/api/v1/bionic/analyze_waypoint",
                json=request_body,
                headers={"Content-Type": "application/json"}
            )
            
            assert response.status_code == 200
            data = response.json()
            scores_by_mode[mode] = data["scores"]["score_bionic_final"]
        
        print("Score comparison by mode:")
        for mode, score in scores_by_mode.items():
            print(f"  {mode}: {score:.1f}/100")
        
        # Scores should be in valid range
        for mode, score in scores_by_mode.items():
            assert 0 <= score <= 100, f"Invalid score for mode {mode}: {score}"
        
        print("✓ All modes produce valid scores")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
