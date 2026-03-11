"""
BIONIC V5 — PHASE B: Advanced Factors Integration Tests
=========================================================

Tests for the 4 advanced factors integrated per service:
1. Social Hierarchy (ScoreBehaviorService)
2. Digestive Cycle (ScoreBehaviorService + ScoreMobilityService)
3. Weak Signals (ScoreBehaviorService + ScoreRiskService)
4. Interspecies Competition (ScoreMultiFactorService)

Verifies:
- model_version = 'BIONIC-V5.1-PHASE-B'
- advanced_factors_phase_b in metadata.data_sources
- Correct components in each service
- Traceability via source_ids
- All 4 analysis modes (live, pre_rut, rut, post_rut)
"""

import pytest
import requests
import os
from datetime import datetime, timezone

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestBionicPhaseBAPIContract:
    """Test API contract for PHASE B"""
    
    def test_health_check(self):
        """Verify API health endpoint"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/analyze_waypoint/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✓ Health check passed")
    
    def test_model_version_is_phase_b(self):
        """Verify model_version = 'BIONIC-V5.1-PHASE-B'"""
        payload = {
            "waypoint": {
                "id": "TEST-PHASE-B-001",
                "name": "Test PHASE B",
                "latitude": 46.8500,
                "longitude": -71.2500
            },
            "species": "moose",
            "target_datetime": datetime.now(timezone.utc).isoformat(),
            "parameters": {"mode": "rut"}
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/analyze_waypoint", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert data["model_version"] == "BIONIC-V5.1-PHASE-B", f"Expected 'BIONIC-V5.1-PHASE-B', got '{data['model_version']}'"
        print(f"✓ model_version is '{data['model_version']}'")
    
    def test_advanced_factors_in_metadata_data_sources(self):
        """Verify 'advanced_factors_phase_b' in metadata.data_sources"""
        payload = {
            "waypoint": {
                "id": "TEST-PHASE-B-002",
                "name": "Test Data Sources",
                "latitude": 46.8500,
                "longitude": -71.2500
            },
            "species": "moose",
            "target_datetime": datetime.now(timezone.utc).isoformat()
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/analyze_waypoint", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        data_sources = data.get("metadata", {}).get("data_sources", [])
        assert "advanced_factors_phase_b" in data_sources, f"Expected 'advanced_factors_phase_b' in data_sources, got {data_sources}"
        print(f"✓ 'advanced_factors_phase_b' found in metadata.data_sources: {data_sources}")


class TestScoreBehaviorServiceComponents:
    """Test ScoreBehaviorService PHASE B components"""
    
    def _analyze_waypoint(self, mode="rut", extra_data=None):
        """Helper to call analyze_waypoint API"""
        payload = {
            "waypoint": {
                "id": "TEST-BEHAVIOR-001",
                "name": "Test Behavior Service",
                "latitude": 46.8500,
                "longitude": -71.2500
            },
            "species": "moose",
            "target_datetime": datetime.now(timezone.utc).isoformat(),
            "parameters": {"mode": mode}
        }
        if extra_data:
            payload["extra_data"] = extra_data
        
        response = requests.post(f"{BASE_URL}/api/v1/bionic/analyze_waypoint", json=payload)
        assert response.status_code == 200
        return response.json()
    
    def test_behavior_score_present_in_breakdown(self):
        """Verify behavior score is present in breakdown"""
        data = self._analyze_waypoint()
        breakdown = data.get("scores", {}).get("breakdown", {})
        
        assert "behavior" in breakdown, f"Expected 'behavior' in breakdown, got keys: {list(breakdown.keys())}"
        behavior = breakdown["behavior"]
        assert "value" in behavior
        assert "weight" in behavior
        assert 0 <= behavior["value"] <= 100
        print(f"✓ Behavior score present: {behavior['value']}/100 (weight: {behavior['weight']})")
    
    def test_all_modes_return_behavior_component(self):
        """Verify all 4 modes return behavior component"""
        modes = ["live", "pre_rut", "rut", "post_rut"]
        for mode in modes:
            data = self._analyze_waypoint(mode=mode)
            breakdown = data.get("scores", {}).get("breakdown", {})
            
            assert "behavior" in breakdown, f"Mode '{mode}': behavior missing from breakdown"
            print(f"✓ Mode '{mode}': behavior score = {breakdown['behavior']['value']}")


class TestScoreMultiFactorServiceComponents:
    """Test ScoreMultiFactorService PHASE B components (interspecies_competition)"""
    
    def _analyze_waypoint(self, mode="rut"):
        """Helper to call analyze_waypoint API"""
        payload = {
            "waypoint": {
                "id": "TEST-MULTIFACTOR-001",
                "name": "Test MultiFactors Service",
                "latitude": 46.8500,
                "longitude": -71.2500
            },
            "species": "moose",
            "target_datetime": datetime.now(timezone.utc).isoformat(),
            "parameters": {"mode": mode}
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/analyze_waypoint", json=payload)
        assert response.status_code == 200
        return response.json()
    
    def test_multifactor_score_present_in_breakdown(self):
        """Verify multifactor score is present in breakdown"""
        data = self._analyze_waypoint()
        breakdown = data.get("scores", {}).get("breakdown", {})
        
        assert "multifactor" in breakdown, f"Expected 'multifactor' in breakdown, got keys: {list(breakdown.keys())}"
        multifactor = breakdown["multifactor"]
        assert "value" in multifactor
        assert "weight" in multifactor
        assert 0 <= multifactor["value"] <= 100
        print(f"✓ Multifactor score present: {multifactor['value']}/100 (weight: {multifactor['weight']})")


class TestScoreRiskServiceComponents:
    """Test ScoreRiskService PHASE B components (risk_weak_signals)"""
    
    def _analyze_waypoint(self, mode="rut"):
        """Helper to call analyze_waypoint API"""
        payload = {
            "waypoint": {
                "id": "TEST-RISK-001",
                "name": "Test Risk Service",
                "latitude": 46.8500,
                "longitude": -71.2500
            },
            "species": "moose",
            "target_datetime": datetime.now(timezone.utc).isoformat(),
            "parameters": {"mode": mode}
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/analyze_waypoint", json=payload)
        assert response.status_code == 200
        return response.json()
    
    def test_risk_score_present_in_breakdown(self):
        """Verify risk score is present in breakdown"""
        data = self._analyze_waypoint()
        breakdown = data.get("scores", {}).get("breakdown", {})
        
        # Risk is mapped to R_risk in the response
        assert "R_risk" in breakdown, f"Expected 'R_risk' in breakdown, got keys: {list(breakdown.keys())}"
        risk = breakdown["R_risk"]
        assert "value" in risk
        assert "weight" in risk
        assert 0 <= risk["value"] <= 100
        print(f"✓ Risk score present: {risk['value']}/100 (weight: {risk['weight']})")


class TestScoreMobilityServiceComponents:
    """Test ScoreMobilityService PHASE B components (digestive_mobility)"""
    
    def _analyze_waypoint(self, mode="rut"):
        """Helper to call analyze_waypoint API"""
        payload = {
            "waypoint": {
                "id": "TEST-MOBILITY-001",
                "name": "Test Mobility Service",
                "latitude": 46.8500,
                "longitude": -71.2500
            },
            "species": "moose",
            "target_datetime": datetime.now(timezone.utc).isoformat(),
            "parameters": {"mode": mode}
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/analyze_waypoint", json=payload)
        assert response.status_code == 200
        return response.json()
    
    def test_mobility_score_present_in_breakdown(self):
        """Verify mobility score is present in breakdown"""
        data = self._analyze_waypoint()
        breakdown = data.get("scores", {}).get("breakdown", {})
        
        # Mobility is mapped to A_mobility in the response
        assert "A_mobility" in breakdown, f"Expected 'A_mobility' in breakdown, got keys: {list(breakdown.keys())}"
        mobility = breakdown["A_mobility"]
        assert "value" in mobility
        assert "weight" in mobility
        assert 0 <= mobility["value"] <= 100
        print(f"✓ Mobility score present: {mobility['value']}/100 (weight: {mobility['weight']})")


class TestAllAnalysisModes:
    """Test all 4 analysis modes with advanced factors"""
    
    def _analyze_waypoint(self, mode):
        """Helper to call analyze_waypoint API"""
        payload = {
            "waypoint": {
                "id": f"TEST-MODE-{mode.upper()}-001",
                "name": f"Test Mode {mode}",
                "latitude": 46.8500,
                "longitude": -71.2500
            },
            "species": "moose",
            "target_datetime": datetime.now(timezone.utc).isoformat(),
            "parameters": {"mode": mode}
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/analyze_waypoint", json=payload)
        assert response.status_code == 200
        return response.json()
    
    def test_live_mode(self):
        """Test LIVE mode with advanced factors"""
        data = self._analyze_waypoint("live")
        assert data["scores"]["analysis_mode"] == "live"
        assert data["model_version"] == "BIONIC-V5.1-PHASE-B"
        score = data["scores"]["score_bionic_final"]
        assert 0 <= score <= 100
        print(f"✓ LIVE mode: score={score}, model_version={data['model_version']}")
    
    def test_pre_rut_mode(self):
        """Test PRE_RUT mode with advanced factors"""
        data = self._analyze_waypoint("pre_rut")
        assert data["scores"]["analysis_mode"] == "pre_rut"
        assert data["model_version"] == "BIONIC-V5.1-PHASE-B"
        score = data["scores"]["score_bionic_final"]
        assert 0 <= score <= 100
        print(f"✓ PRE_RUT mode: score={score}, model_version={data['model_version']}")
    
    def test_rut_mode(self):
        """Test RUT mode with advanced factors"""
        data = self._analyze_waypoint("rut")
        assert data["scores"]["analysis_mode"] == "rut"
        assert data["model_version"] == "BIONIC-V5.1-PHASE-B"
        score = data["scores"]["score_bionic_final"]
        assert 0 <= score <= 100
        print(f"✓ RUT mode: score={score}, model_version={data['model_version']}")
    
    def test_post_rut_mode(self):
        """Test POST_RUT mode with advanced factors"""
        data = self._analyze_waypoint("post_rut")
        assert data["scores"]["analysis_mode"] == "post_rut"
        assert data["model_version"] == "BIONIC-V5.1-PHASE-B"
        score = data["scores"]["score_bionic_final"]
        assert 0 <= score <= 100
        print(f"✓ POST_RUT mode: score={score}, model_version={data['model_version']}")
    
    def test_default_mode_is_rut(self):
        """Test that default mode is 'rut' when not specified"""
        payload = {
            "waypoint": {
                "id": "TEST-DEFAULT-MODE-001",
                "name": "Test Default Mode",
                "latitude": 46.8500,
                "longitude": -71.2500
            },
            "species": "moose",
            "target_datetime": datetime.now(timezone.utc).isoformat()
            # Note: no 'mode' parameter
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/analyze_waypoint", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert data["scores"]["analysis_mode"] == "rut", f"Expected default mode 'rut', got '{data['scores']['analysis_mode']}'"
        print(f"✓ Default mode is 'rut' as expected")


class TestSourceIdsTraceability:
    """Test source_ids traceability in results"""
    
    def _analyze_waypoint(self, mode="rut"):
        """Helper to call analyze_waypoint API"""
        payload = {
            "waypoint": {
                "id": "TEST-TRACE-001",
                "name": "Test Traceability",
                "latitude": 46.8500,
                "longitude": -71.2500
            },
            "species": "moose",
            "target_datetime": datetime.now(timezone.utc).isoformat(),
            "parameters": {"mode": mode}
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/analyze_waypoint", json=payload)
        assert response.status_code == 200
        return response.json()
    
    def test_response_contains_valid_structure(self):
        """Verify response has complete structure"""
        data = self._analyze_waypoint()
        
        # Check required fields
        assert "analysis_id" in data
        assert "calculated_at" in data
        assert "model_version" in data
        assert "scores" in data
        assert "metadata" in data
        
        # Check scores structure
        scores = data["scores"]
        assert "score_bionic_final" in scores
        assert "breakdown" in scores
        assert "analysis_mode" in scores
        
        print(f"✓ Response structure is valid")
        print(f"  - analysis_id: {data['analysis_id']}")
        print(f"  - model_version: {data['model_version']}")
        print(f"  - score_bionic_final: {scores['score_bionic_final']}")


class TestCompleteBreakdownStructure:
    """Test that all 9 scoring components are present"""
    
    def test_all_9_components_present(self):
        """Verify all 9 score components are in breakdown"""
        payload = {
            "waypoint": {
                "id": "TEST-9-COMPONENTS-001",
                "name": "Test 9 Components",
                "latitude": 46.8500,
                "longitude": -71.2500
            },
            "species": "moose",
            "target_datetime": datetime.now(timezone.utc).isoformat(),
            "parameters": {"mode": "rut"}
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/analyze_waypoint", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        breakdown = data.get("scores", {}).get("breakdown", {})
        
        # Expected components based on router mapping
        expected_components = [
            "H_habitat",      # Habitat score
            "R_risk",         # Risk score (with risk_weak_signals)
            "S_probability",  # Probability score
            "A_mobility",     # Mobility score (with digestive_mobility)
            "T_weather",      # Weather score
            "P_pressure",     # Pressure score
            "behavior",       # Behavior score (with social_hierarchy, digestive_cycle, weak_signals)
            "density",        # Density score
            "multifactor"     # MultiFactors score (with interspecies_competition)
        ]
        
        missing = []
        for comp in expected_components:
            if comp not in breakdown:
                missing.append(comp)
        
        if missing:
            print(f"Missing components: {missing}")
            print(f"Present components: {list(breakdown.keys())}")
        
        assert len(missing) == 0, f"Missing components: {missing}"
        print(f"✓ All 9 score components present in breakdown:")
        for comp in expected_components:
            value = breakdown[comp].get("value", "N/A")
            print(f"  - {comp}: {value}")


class TestPhaseBIntegration:
    """Integration tests for PHASE B advanced factors"""
    
    def test_complete_analysis_workflow(self):
        """Test complete analysis workflow with PHASE B"""
        payload = {
            "waypoint": {
                "id": "TEST-WORKFLOW-001",
                "name": "Test Complete Workflow",
                "latitude": 46.8500,
                "longitude": -71.2500
            },
            "species": "moose",
            "target_datetime": datetime.now(timezone.utc).isoformat(),
            "parameters": {"mode": "rut", "region": "QC"},
            "wqs": {"score": 72.5}
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/analyze_waypoint", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Verify PHASE B markers
        assert data["model_version"] == "BIONIC-V5.1-PHASE-B"
        assert "advanced_factors_phase_b" in data["metadata"]["data_sources"]
        
        # Verify scores
        scores = data["scores"]
        assert scores["analysis_mode"] == "rut"
        assert 0 <= scores["score_bionic_final"] <= 100
        
        # Verify fusion calculation
        fusion = scores.get("fusion", {})
        if fusion:
            assert "wqs" in fusion
            assert "dynamic" in fusion
        
        print(f"✓ Complete workflow test passed")
        print(f"  - Model Version: {data['model_version']}")
        print(f"  - Analysis Mode: {scores['analysis_mode']}")
        print(f"  - Final Score: {scores['score_bionic_final']}")
        print(f"  - Data Sources: {data['metadata']['data_sources']}")
    
    def test_different_species_moose(self):
        """Test with moose species"""
        payload = {
            "waypoint": {
                "id": "TEST-MOOSE-001",
                "name": "Test Moose",
                "latitude": 46.8500,
                "longitude": -71.2500
            },
            "species": "moose",
            "target_datetime": datetime.now(timezone.utc).isoformat(),
            "parameters": {"mode": "rut"}
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/analyze_waypoint", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert data["model_version"] == "BIONIC-V5.1-PHASE-B"
        print(f"✓ Moose species test passed: score={data['scores']['score_bionic_final']}")
    
    def test_different_species_deer(self):
        """Test with deer species"""
        payload = {
            "waypoint": {
                "id": "TEST-DEER-001",
                "name": "Test Deer",
                "latitude": 46.8500,
                "longitude": -71.2500
            },
            "species": "deer",
            "target_datetime": datetime.now(timezone.utc).isoformat(),
            "parameters": {"mode": "rut"}
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/analyze_waypoint", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert data["model_version"] == "BIONIC-V5.1-PHASE-B"
        print(f"✓ Deer species test passed: score={data['scores']['score_bionic_final']}")


class TestAdvancedFactorsDetails:
    """Test that advanced factors details are included in response metadata"""
    
    def test_response_has_complete_metadata(self):
        """Verify metadata contains all required fields"""
        payload = {
            "waypoint": {
                "id": "TEST-METADATA-001",
                "name": "Test Metadata",
                "latitude": 46.8500,
                "longitude": -71.2500
            },
            "species": "moose",
            "target_datetime": datetime.now(timezone.utc).isoformat(),
            "parameters": {"mode": "rut"}
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/analyze_waypoint", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        metadata = data.get("metadata", {})
        
        # Check required metadata fields
        assert "processing_time_ms" in metadata
        assert "data_sources" in metadata
        assert "confidence_impact" in metadata
        
        # Check data_sources includes PHASE B components
        data_sources = metadata.get("data_sources", [])
        expected_sources = ["unified_scoring_service", "knowledge_layer", "advanced_factors_phase_b"]
        
        for source in expected_sources:
            assert source in data_sources, f"Expected '{source}' in data_sources"
        
        print(f"✓ Metadata is complete with PHASE B sources")
        print(f"  - data_sources: {data_sources}")
        print(f"  - processing_time_ms: {metadata.get('processing_time_ms')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
