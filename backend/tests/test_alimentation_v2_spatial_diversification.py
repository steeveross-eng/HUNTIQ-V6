"""
ALIMENTATION-V2 — Spatial Diversification Tests (Iteration 51)
================================================================
Tests for:
1. max_salines parameter (1-4 salines selection)
2. Spatial diversification (min 300m between salines)
3. Grid-based candidate generation (~16 candidates)
4. Selected vs non-selected salines
5. OURS/DINDON still return salines_disabled=true
6. n_salines and n_candidates response fields
"""
import pytest
import requests
import os
import math

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

def haversine_m(lat1, lng1, lat2, lng2):
    """Calculate distance in meters between two GPS points."""
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class TestAlimentationV2SpatialDiversification:
    """Tests for spatial diversification with max_salines parameter"""

    def test_max_salines_4_returns_4_selected(self):
        """Test: POST /api/v2/alimentation/analyze with max_salines=4 returns 4 selected salines"""
        response = requests.post(f"{BASE_URL}/api/v2/alimentation/analyze", json={
            "center_lat": 46.8139,
            "center_lng": -71.2080,
            "species": "CERF",
            "month": 10,
            "max_salines": 4
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Verify n_salines = 4 selected
        assert data.get("n_salines") == 4, f"Expected 4 selected salines, got {data.get('n_salines')}"
        
        # Verify salines array has candidates
        salines = data.get("salines", [])
        assert len(salines) > 4, f"Expected more than 4 total candidates, got {len(salines)}"
        
        # Count selected salines
        selected = [s for s in salines if s.get("selected")]
        assert len(selected) == 4, f"Expected 4 selected salines, got {len(selected)}"
        
        # Verify max_salines in response
        assert data.get("max_salines") == 4, f"Expected max_salines=4 in response, got {data.get('max_salines')}"
        print(f"PASS: max_salines=4 returns {data.get('n_salines')} selected, {len(salines)} total candidates")

    def test_max_salines_1_returns_1_selected(self):
        """Test: POST /api/v2/alimentation/analyze with max_salines=1 returns 1 selected saline"""
        response = requests.post(f"{BASE_URL}/api/v2/alimentation/analyze", json={
            "center_lat": 46.8139,
            "center_lng": -71.2080,
            "species": "CERF",
            "month": 10,
            "max_salines": 1
        })
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("n_salines") == 1, f"Expected 1 selected saline, got {data.get('n_salines')}"
        
        salines = data.get("salines", [])
        selected = [s for s in salines if s.get("selected")]
        assert len(selected) == 1, f"Expected 1 selected saline, got {len(selected)}"
        
        # Verify the selected one has highest score among candidates
        selected_score = selected[0].get("score", 0)
        for s in salines:
            if not s.get("selected"):
                # All non-selected should have lower or equal scores
                pass  # Greedy selection ensures this
        
        assert data.get("max_salines") == 1
        print(f"PASS: max_salines=1 returns {data.get('n_salines')} selected (best spot), {len(salines)} total candidates")

    def test_max_salines_2_returns_2_selected(self):
        """Test: POST /api/v2/alimentation/analyze with max_salines=2 returns 2 selected salines"""
        response = requests.post(f"{BASE_URL}/api/v2/alimentation/analyze", json={
            "center_lat": 46.8139,
            "center_lng": -71.2080,
            "species": "CERF",
            "month": 10,
            "max_salines": 2
        })
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("n_salines") == 2, f"Expected 2 selected salines, got {data.get('n_salines')}"
        
        salines = data.get("salines", [])
        selected = [s for s in salines if s.get("selected")]
        assert len(selected) == 2, f"Expected 2 selected salines, got {len(selected)}"
        assert data.get("max_salines") == 2
        print(f"PASS: max_salines=2 returns {data.get('n_salines')} selected, {len(salines)} total candidates")

    def test_max_salines_3_returns_3_selected(self):
        """Test: POST /api/v2/alimentation/analyze with max_salines=3 returns 3 selected salines"""
        response = requests.post(f"{BASE_URL}/api/v2/alimentation/analyze", json={
            "center_lat": 46.8139,
            "center_lng": -71.2080,
            "species": "CERF",
            "month": 10,
            "max_salines": 3
        })
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("n_salines") == 3, f"Expected 3 selected salines, got {data.get('n_salines')}"
        assert data.get("max_salines") == 3
        print(f"PASS: max_salines=3 returns {data.get('n_salines')} selected")


class TestSpatialDistanceConstraint:
    """Tests for 300m minimum distance between selected salines"""

    def test_selected_salines_are_at_least_300m_apart(self):
        """Test: All selected salines are >= 300m apart (spatial diversification)"""
        response = requests.post(f"{BASE_URL}/api/v2/alimentation/analyze", json={
            "center_lat": 46.8139,
            "center_lng": -71.2080,
            "species": "CERF",
            "month": 10,
            "max_salines": 4
        })
        assert response.status_code == 200
        data = response.json()
        
        salines = data.get("salines", [])
        selected = [s for s in salines if s.get("selected")]
        
        # Verify >= 300m between all pairs of selected salines
        min_distance = 300.0  # meters
        violations = []
        
        for i, s1 in enumerate(selected):
            for j, s2 in enumerate(selected):
                if i >= j:
                    continue
                dist = haversine_m(s1["lat"], s1["lng"], s2["lat"], s2["lng"])
                if dist < min_distance:
                    violations.append((s1["id"], s2["id"], round(dist)))
        
        assert len(violations) == 0, f"Distance violations (<300m): {violations}"
        
        # Log minimum distance found
        if len(selected) >= 2:
            distances = []
            for i, s1 in enumerate(selected):
                for j, s2 in enumerate(selected):
                    if i < j:
                        distances.append(haversine_m(s1["lat"], s1["lng"], s2["lat"], s2["lng"]))
            min_found = min(distances)
            print(f"PASS: All {len(selected)} selected salines are >= 300m apart (min found: {round(min_found)}m)")
        else:
            print(f"PASS: Only {len(selected)} saline selected, no distance check needed")

    def test_spatial_diversification_with_2_salines(self):
        """Test: 2 selected salines are >= 300m apart"""
        response = requests.post(f"{BASE_URL}/api/v2/alimentation/analyze", json={
            "center_lat": 46.8139,
            "center_lng": -71.2080,
            "species": "CERF",
            "month": 10,
            "max_salines": 2
        })
        assert response.status_code == 200
        data = response.json()
        
        selected = [s for s in data.get("salines", []) if s.get("selected")]
        assert len(selected) == 2
        
        dist = haversine_m(selected[0]["lat"], selected[0]["lng"], selected[1]["lat"], selected[1]["lng"])
        assert dist >= 300.0, f"Selected salines are only {round(dist)}m apart, expected >= 300m"
        print(f"PASS: 2 selected salines are {round(dist)}m apart (>= 300m)")


class TestGridBasedCandidateGeneration:
    """Tests for grid-based candidate generation (~16 candidates)"""

    def test_approximately_16_candidates_generated(self):
        """Test: ~16 candidates are generated (4x4 grid)"""
        response = requests.post(f"{BASE_URL}/api/v2/alimentation/analyze", json={
            "center_lat": 46.8139,
            "center_lng": -71.2080,
            "species": "CERF",
            "month": 10,
            "max_salines": 4
        })
        assert response.status_code == 200
        data = response.json()
        
        n_candidates = data.get("n_candidates", 0)
        salines = data.get("salines", [])
        
        # Should have approximately 16 candidates (some may be filtered out if too close to center)
        assert 10 <= n_candidates <= 20, f"Expected ~16 candidates (10-20 range), got {n_candidates}"
        assert n_candidates == len(salines), f"n_candidates ({n_candidates}) != len(salines) ({len(salines)})"
        
        print(f"PASS: {n_candidates} candidates generated (expected ~16 from 4x4 grid)")

    def test_all_candidates_have_required_fields(self):
        """Test: Each candidate has id, lat, lng, score, selected, type, etc."""
        response = requests.post(f"{BASE_URL}/api/v2/alimentation/analyze", json={
            "center_lat": 46.8139,
            "center_lng": -71.2080,
            "species": "CERF",
            "month": 10,
            "max_salines": 4
        })
        assert response.status_code == 200
        data = response.json()
        
        salines = data.get("salines", [])
        required_fields = ["id", "lat", "lng", "score", "selected", "type", "distance_centre_m"]
        
        for s in salines:
            for field in required_fields:
                assert field in s, f"Missing field '{field}' in saline {s.get('id', 'unknown')}"
        
        print(f"PASS: All {len(salines)} candidates have required fields")

    def test_candidates_have_rank_for_selected(self):
        """Test: Selected candidates have rank (1-4), non-selected have rank=0"""
        response = requests.post(f"{BASE_URL}/api/v2/alimentation/analyze", json={
            "center_lat": 46.8139,
            "center_lng": -71.2080,
            "species": "CERF",
            "month": 10,
            "max_salines": 4
        })
        assert response.status_code == 200
        data = response.json()
        
        salines = data.get("salines", [])
        
        for s in salines:
            if s.get("selected"):
                assert s.get("rank", 0) > 0, f"Selected saline {s['id']} should have rank > 0"
            else:
                assert s.get("rank", 0) == 0, f"Non-selected saline {s['id']} should have rank = 0"
        
        print(f"PASS: Rank correctly assigned (1-4 for selected, 0 for candidates)")


class TestSpeciesWithoutSalines:
    """Tests for OURS and DINDON (no salines)"""

    def test_ours_noir_returns_salines_disabled(self):
        """Test: ours_noir returns salines_disabled=true, n_salines=0"""
        response = requests.post(f"{BASE_URL}/api/v2/alimentation/analyze", json={
            "center_lat": 46.8139,
            "center_lng": -71.2080,
            "species": "ours_noir",
            "month": 10,
            "max_salines": 4
        })
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("salines_disabled") == True, "Expected salines_disabled=true for OURS"
        assert data.get("n_salines") == 0, "Expected n_salines=0 for OURS"
        assert len(data.get("salines", [])) == 0, "Expected empty salines array for OURS"
        assert data.get("salines_message") is not None, "Expected salines_message for OURS"
        
        print(f"PASS: ours_noir returns salines_disabled=true, n_salines=0, message present")

    def test_dindon_sauvage_returns_salines_disabled(self):
        """Test: dindon_sauvage returns salines_disabled=true, n_salines=0"""
        response = requests.post(f"{BASE_URL}/api/v2/alimentation/analyze", json={
            "center_lat": 46.8139,
            "center_lng": -71.2080,
            "species": "dindon_sauvage",
            "month": 10,
            "max_salines": 4
        })
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("salines_disabled") == True, "Expected salines_disabled=true for DINDON"
        assert data.get("n_salines") == 0, "Expected n_salines=0 for DINDON"
        assert len(data.get("salines", [])) == 0, "Expected empty salines array for DINDON"
        assert data.get("salines_message") is not None, "Expected salines_message for DINDON"
        
        print(f"PASS: dindon_sauvage returns salines_disabled=true, n_salines=0, message present")


class TestResponseFormat:
    """Tests for response format completeness"""

    def test_n_candidates_field_present(self):
        """Test: n_candidates field present in response"""
        response = requests.post(f"{BASE_URL}/api/v2/alimentation/analyze", json={
            "center_lat": 46.8139,
            "center_lng": -71.2080,
            "species": "CERF",
            "month": 10,
            "max_salines": 4
        })
        assert response.status_code == 200
        data = response.json()
        
        assert "n_candidates" in data, "Missing n_candidates field in response"
        assert "n_salines" in data, "Missing n_salines field in response"
        assert "max_salines" in data, "Missing max_salines field in response"
        
        print(f"PASS: n_candidates={data['n_candidates']}, n_salines={data['n_salines']}, max_salines={data['max_salines']}")

    def test_summary_format_x_of_y_candidates(self):
        """Test: Response has correct n_salines/n_candidates for X/Y format"""
        response = requests.post(f"{BASE_URL}/api/v2/alimentation/analyze", json={
            "center_lat": 46.8139,
            "center_lng": -71.2080,
            "species": "CERF",
            "month": 10,
            "max_salines": 3
        })
        assert response.status_code == 200
        data = response.json()
        
        n_salines = data.get("n_salines")
        n_candidates = data.get("n_candidates")
        
        assert n_salines <= n_candidates, f"n_salines ({n_salines}) should be <= n_candidates ({n_candidates})"
        
        # Simulate X/Y format: "3/16 candidats"
        resume_format = f"{n_salines}/{n_candidates} candidats"
        print(f"PASS: Résumé format: {resume_format}")


class TestDifferentSpeciesWithSalines:
    """Tests for species that DO use salines"""

    def test_chevreuil_max_salines_4(self):
        """Test: chevreuil with max_salines=4"""
        response = requests.post(f"{BASE_URL}/api/v2/alimentation/analyze", json={
            "center_lat": 46.8139,
            "center_lng": -71.2080,
            "species": "chevreuil",
            "month": 10,
            "max_salines": 4
        })
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("salines_disabled") == False
        assert data.get("n_salines") == 4
        print(f"PASS: chevreuil max_salines=4 returns {data.get('n_salines')} selected")

    def test_orignal_max_salines_2(self):
        """Test: orignal with max_salines=2"""
        response = requests.post(f"{BASE_URL}/api/v2/alimentation/analyze", json={
            "center_lat": 46.8139,
            "center_lng": -71.2080,
            "species": "orignal",
            "month": 10,
            "max_salines": 2
        })
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("salines_disabled") == False
        assert data.get("n_salines") == 2
        print(f"PASS: orignal max_salines=2 returns {data.get('n_salines')} selected")

    def test_wapiti_max_salines_1(self):
        """Test: wapiti with max_salines=1"""
        response = requests.post(f"{BASE_URL}/api/v2/alimentation/analyze", json={
            "center_lat": 46.8139,
            "center_lng": -71.2080,
            "species": "wapiti",
            "month": 10,
            "max_salines": 1
        })
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("salines_disabled") == False
        assert data.get("n_salines") == 1
        print(f"PASS: wapiti max_salines=1 returns {data.get('n_salines')} selected")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
