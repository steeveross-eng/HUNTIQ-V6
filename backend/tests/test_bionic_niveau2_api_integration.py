"""
BIONIC V5 NIVEAU 2 — API Integration Tests for Advanced Behavioral Factors (PHASE B)
====================================================================================

API-level tests for the 4 advanced behavioral factors:
1. HIÉRARCHIE SOCIALE
2. CYCLES DIGESTIFS
3. SIGNAUX FAIBLES
4. COMPÉTITION INTER-ESPÈCES

Tests validate that the API correctly exposes PHASE B factors in advanced_factors_details.
"""

import pytest
import requests
import os
from datetime import datetime, timezone

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestAPIAdvancedFactorsPHASEB:
    """API-level tests for PHASE B advanced factors"""
    
    def _analyze_waypoint(self, species="moose", hour=6, mode="rut", extra_data=None):
        """Helper to call analyze_waypoint API"""
        target_datetime = f"2025-10-01T{hour:02d}:00:00Z"
        
        payload = {
            "waypoint": {
                "id": f"TEST-API-NIVEAU2-{species.upper()}-{hour}",
                "name": f"Test API NIVEAU 2 {species}",
                "latitude": 46.8500,
                "longitude": -71.2500
            },
            "species": species,
            "target_datetime": target_datetime,
            "parameters": {"mode": mode, "region": "CA-QC"}
        }
        if extra_data:
            payload["extra_data"] = extra_data
        
        response = requests.post(f"{BASE_URL}/api/v1/bionic/analyze_waypoint", json=payload)
        return response
    
    # =========================================================================
    # API STRUCTURE TESTS
    # =========================================================================
    
    def test_api_returns_advanced_factors_details(self):
        """TEST 1: API returns advanced_factors_details in response"""
        response = self._analyze_waypoint()
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        scores = data.get("scores", {})
        
        assert "advanced_factors_details" in scores, "advanced_factors_details missing from scores"
        
        print(f"✓ API returns advanced_factors_details")
        print(f"  - Keys: {list(scores['advanced_factors_details'].keys())}")
    
    def test_api_returns_phase_b_factors(self):
        """TEST 2: API returns all 4 PHASE B factors"""
        response = self._analyze_waypoint()
        assert response.status_code == 200
        
        data = response.json()
        factors = data["scores"]["advanced_factors_details"].get("factors", {})
        
        expected_factors = ["social", "competition", "digestive", "signals"]
        for factor in expected_factors:
            assert factor in factors, f"Factor '{factor}' missing from response"
        
        print(f"✓ All 4 PHASE B factors present:")
        for f in expected_factors:
            print(f"  - {f}: {factors.get(f, {})}")
    
    def test_api_returns_integration_mode_centralized(self):
        """TEST 3: API indicates centralized integration mode"""
        response = self._analyze_waypoint()
        assert response.status_code == 200
        
        data = response.json()
        advanced = data["scores"]["advanced_factors_details"]
        
        assert advanced.get("integration_mode") == "centralized", \
            f"Expected integration_mode='centralized', got '{advanced.get('integration_mode')}'"
        
        print(f"✓ Integration mode is 'centralized'")
    
    def test_api_returns_source_ids(self):
        """TEST 4: API returns source_ids for traceability"""
        response = self._analyze_waypoint()
        assert response.status_code == 200
        
        data = response.json()
        advanced = data["scores"]["advanced_factors_details"]
        
        source_ids = advanced.get("source_ids", [])
        assert isinstance(source_ids, list), "source_ids should be a list"
        
        print(f"✓ Source IDs in response: {source_ids[:5]}...")
    
    # =========================================================================
    # SOCIAL HIERARCHY TESTS
    # =========================================================================
    
    def test_api_returns_social_factor_structure(self):
        """TEST 5: Social factor has correct structure (modifier, rank, version)"""
        response = self._analyze_waypoint()
        assert response.status_code == 200
        
        data = response.json()
        social = data["scores"]["advanced_factors_details"]["factors"]["social"]
        
        assert "modifier" in social, "social.modifier missing"
        assert "rank" in social, "social.rank missing"
        assert "version" in social, "social.version missing"
        
        print(f"✓ Social factor structure:")
        print(f"  - modifier: {social['modifier']}")
        print(f"  - rank: {social['rank']}")
        print(f"  - version: {social['version']}")
    
    # =========================================================================
    # DIGESTIVE CYCLES TESTS
    # =========================================================================
    
    def test_api_digestive_at_6h_active_feeding(self):
        """TEST 6: At 6h, digestive phase should be active_feeding"""
        response = self._analyze_waypoint(hour=6)
        assert response.status_code == 200
        
        data = response.json()
        digestive = data["scores"]["advanced_factors_details"]["factors"]["digestive"]
        
        assert digestive["phase"] == "active_feeding", \
            f"Expected 'active_feeding' at 6h, got '{digestive['phase']}'"
        
        print(f"✓ 6h: digestive phase = {digestive['phase']}")
    
    def test_api_digestive_at_10h_rumination(self):
        """TEST 7: At 10h, digestive phase should be rumination"""
        response = self._analyze_waypoint(hour=10)
        assert response.status_code == 200
        
        data = response.json()
        digestive = data["scores"]["advanced_factors_details"]["factors"]["digestive"]
        
        assert digestive["phase"] == "rumination", \
            f"Expected 'rumination' at 10h, got '{digestive['phase']}'"
        
        print(f"✓ 10h: digestive phase = {digestive['phase']}")
    
    def test_api_digestive_at_14h_rest_digestion(self):
        """TEST 8: At 14h, digestive phase should be rest_digestion"""
        response = self._analyze_waypoint(hour=14)
        assert response.status_code == 200
        
        data = response.json()
        digestive = data["scores"]["advanced_factors_details"]["factors"]["digestive"]
        
        assert digestive["phase"] == "rest_digestion", \
            f"Expected 'rest_digestion' at 14h, got '{digestive['phase']}'"
        
        print(f"✓ 14h: digestive phase = {digestive['phase']}")
    
    def test_api_digestive_at_16h_water_seeking(self):
        """TEST 9: At 16h, digestive phase should be water_seeking"""
        response = self._analyze_waypoint(hour=16)
        assert response.status_code == 200
        
        data = response.json()
        digestive = data["scores"]["advanced_factors_details"]["factors"]["digestive"]
        
        assert digestive["phase"] == "water_seeking", \
            f"Expected 'water_seeking' at 16h, got '{digestive['phase']}'"
        
        print(f"✓ 16h: digestive phase = {digestive['phase']}")
    
    def test_api_digestive_visibility_varies(self):
        """TEST 10: Digestive visibility varies by hour"""
        visibilities = {}
        
        for hour in [6, 10, 14, 16]:
            response = self._analyze_waypoint(hour=hour)
            assert response.status_code == 200
            
            data = response.json()
            digestive = data["scores"]["advanced_factors_details"]["factors"]["digestive"]
            visibilities[hour] = digestive.get("visibility", 0)
        
        # 6h (feeding) and 16h (water) should have higher visibility than 14h (rest)
        print(f"✓ Visibility by hour:")
        for h, v in visibilities.items():
            print(f"  - {h}h: visibility={v}")
        
        # Validate visibility patterns
        assert visibilities[6] > visibilities[14], "6h visibility should be > 14h"
        assert visibilities[16] > visibilities[14], "16h visibility should be > 14h"
    
    # =========================================================================
    # SIGNALS TESTS
    # =========================================================================
    
    def test_api_returns_signals_factor_structure(self):
        """TEST 11: Signals factor has correct structure"""
        response = self._analyze_waypoint()
        assert response.status_code == 200
        
        data = response.json()
        signals = data["scores"]["advanced_factors_details"]["factors"]["signals"]
        
        assert "modifier" in signals, "signals.modifier missing"
        assert "impact" in signals, "signals.impact missing"
        assert "detected" in signals, "signals.detected missing"
        assert "version" in signals, "signals.version missing"
        
        print(f"✓ Signals factor structure:")
        print(f"  - modifier: {signals['modifier']}")
        print(f"  - impact: {signals['impact']}")
        print(f"  - detected: {signals['detected']}")
    
    # =========================================================================
    # COMPETITION TESTS
    # =========================================================================
    
    def test_api_returns_competition_factor_structure(self):
        """TEST 12: Competition factor has correct structure"""
        response = self._analyze_waypoint()
        assert response.status_code == 200
        
        data = response.json()
        competition = data["scores"]["advanced_factors_details"]["factors"]["competition"]
        
        assert "modifier" in competition, "competition.modifier missing"
        assert "competitors" in competition, "competition.competitors missing"
        assert "version" in competition, "competition.version missing"
        
        print(f"✓ Competition factor structure:")
        print(f"  - modifier: {competition['modifier']}")
        print(f"  - competitors: {competition['competitors']}")
        print(f"  - version: {competition['version']}")
    
    # =========================================================================
    # SPECIES TESTS
    # =========================================================================
    
    def test_api_moose_returns_valid_response(self):
        """TEST 13: API works correctly for moose species"""
        response = self._analyze_waypoint(species="moose")
        assert response.status_code == 200
        
        data = response.json()
        assert data["model_version"] == "BIONIC-V5.1-PHASE-B"
        
        print(f"✓ Moose analysis completed successfully")
        print(f"  - Final score: {data['scores']['score_bionic_final']}")
    
    def test_api_deer_returns_valid_response(self):
        """TEST 14: API works correctly for deer species"""
        response = self._analyze_waypoint(species="deer")
        assert response.status_code == 200
        
        data = response.json()
        assert data["model_version"] == "BIONIC-V5.1-PHASE-B"
        
        print(f"✓ Deer analysis completed successfully")
        print(f"  - Final score: {data['scores']['score_bionic_final']}")
    
    # =========================================================================
    # ANALYSIS MODES TESTS
    # =========================================================================
    
    def test_api_rut_mode_with_phase_b(self):
        """TEST 15: RUT mode integrates PHASE B factors"""
        response = self._analyze_waypoint(mode="rut")
        assert response.status_code == 200
        
        data = response.json()
        assert data["scores"]["analysis_mode"] == "rut"
        
        factors = data["scores"]["advanced_factors_details"]["factors"]
        assert "social" in factors
        assert "digestive" in factors
        
        print(f"✓ RUT mode with PHASE B: score={data['scores']['score_bionic_final']}")
    
    def test_api_live_mode_with_phase_b(self):
        """TEST 16: LIVE mode integrates PHASE B factors"""
        response = self._analyze_waypoint(mode="live")
        assert response.status_code == 200
        
        data = response.json()
        assert data["scores"]["analysis_mode"] == "live"
        
        factors = data["scores"]["advanced_factors_details"]["factors"]
        assert "social" in factors
        assert "digestive" in factors
        
        print(f"✓ LIVE mode with PHASE B: score={data['scores']['score_bionic_final']}")
    
    def test_api_pre_rut_mode_with_phase_b(self):
        """TEST 17: PRE_RUT mode integrates PHASE B factors"""
        response = self._analyze_waypoint(mode="pre_rut")
        assert response.status_code == 200
        
        data = response.json()
        assert data["scores"]["analysis_mode"] == "pre_rut"
        
        print(f"✓ PRE_RUT mode with PHASE B: score={data['scores']['score_bionic_final']}")
    
    def test_api_post_rut_mode_with_phase_b(self):
        """TEST 18: POST_RUT mode integrates PHASE B factors"""
        response = self._analyze_waypoint(mode="post_rut")
        assert response.status_code == 200
        
        data = response.json()
        assert data["scores"]["analysis_mode"] == "post_rut"
        
        print(f"✓ POST_RUT mode with PHASE B: score={data['scores']['score_bionic_final']}")
    
    # =========================================================================
    # PHASE B MODIFIER TESTS
    # =========================================================================
    
    def test_api_returns_phase_b_modifier(self):
        """TEST 19: API returns phase_b_modifier"""
        response = self._analyze_waypoint()
        assert response.status_code == 200
        
        data = response.json()
        factors = data["scores"]["advanced_factors_details"]["factors"]
        
        assert "phase_b_modifier" in factors, "phase_b_modifier missing"
        
        print(f"✓ phase_b_modifier: {factors['phase_b_modifier']}")
    
    def test_api_phase_b_modifier_is_product_of_factors(self):
        """TEST 20: phase_b_modifier is approximately product of individual factors"""
        response = self._analyze_waypoint()
        assert response.status_code == 200
        
        data = response.json()
        factors = data["scores"]["advanced_factors_details"]["factors"]
        
        social_mod = factors["social"]["modifier"]
        comp_mod = factors["competition"]["modifier"]
        digest_mod = factors["digestive"]["modifier"]
        signals_mod = factors["signals"]["modifier"]
        
        expected = social_mod * comp_mod * digest_mod * signals_mod
        actual = factors["phase_b_modifier"]
        
        # Allow some tolerance for rounding
        assert abs(expected - actual) < 0.01, \
            f"phase_b_modifier ({actual}) should be product of factors ({expected})"
        
        print(f"✓ phase_b_modifier = {actual} ≈ {social_mod}×{comp_mod}×{digest_mod}×{signals_mod}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
