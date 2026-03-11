"""
MASTER PLAN BIONIC 1000% — Passe 2 API Integration Tests
=========================================================

Tests API endpoint responses for C4-C8 corridor features:
  - C4 (BUG-02): Real corridors with source='real' from A* pathfinding
  - C5 (BUG-03): Access corridors from waypoint (is_access_corridor=true)
  - C6 (IC2): road_crossings property present on all corridors
  - C7 (BUG-05): Deduplication - more male than female (female dupes removed)
  - C8 (IM2): wind_direction_deg=225.0 on all corridors

Location: Rural Quebec (Laurentides) lat=47.30, lng=-71.52
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestC4RealCorridors:
    """C4 (BUG-02): API must return at least 1 corridor with source='real'."""

    def test_api_returns_real_corridors(self):
        """At least 1 corridor should have source='real' from A* terrain-aware."""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json={
                "bounds": {"south": 47.285, "north": 47.315, "west": -71.535, "east": -71.505},
                "species": "moose",
                "layers": ["habitats", "rut", "repos", "alimentation"],
                "waypoint_center": {"lat": 47.30, "lng": -71.52}
            },
            timeout=60
        )
        assert response.status_code == 200, f"API returned {response.status_code}"
        
        data = response.json()
        corridors = data.get('corridors', [])
        assert len(corridors) > 0, "No corridors returned"
        
        real_corridors = [c for c in corridors if c.get('properties', {}).get('source') == 'real']
        assert len(real_corridors) >= 1, f"Expected at least 1 real corridor, got {len(real_corridors)}"


class TestC5WaypointAccess:
    """C5 (BUG-03): API must return access corridors from waypoint."""

    def test_api_returns_access_corridors(self):
        """At least 1 access corridor should have is_access_corridor=true."""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json={
                "bounds": {"south": 47.285, "north": 47.315, "west": -71.535, "east": -71.505},
                "species": "moose",
                "layers": ["habitats", "rut", "repos", "alimentation"],
                "waypoint_center": {"lat": 47.30, "lng": -71.52}
            },
            timeout=60
        )
        assert response.status_code == 200
        
        data = response.json()
        corridors = data.get('corridors', [])
        
        access_corridors = [c for c in corridors if c.get('properties', {}).get('is_access_corridor') == True]
        assert len(access_corridors) >= 1, f"Expected at least 1 access corridor, got {len(access_corridors)}"

    def test_access_corridor_has_waypoint_origin(self):
        """Access corridors must have from_zone_type='waypoint'."""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json={
                "bounds": {"south": 47.285, "north": 47.315, "west": -71.535, "east": -71.505},
                "species": "moose",
                "layers": ["habitats", "rut", "repos", "alimentation"],
                "waypoint_center": {"lat": 47.30, "lng": -71.52}
            },
            timeout=60
        )
        assert response.status_code == 200
        
        data = response.json()
        corridors = data.get('corridors', [])
        
        access_corridors = [c for c in corridors if c.get('properties', {}).get('is_access_corridor') == True]
        for c in access_corridors:
            props = c.get('properties', {})
            assert props.get('from_zone_type') == 'waypoint', \
                f"Access corridor should have from_zone_type='waypoint', got {props.get('from_zone_type')}"


class TestC6RoadCrossings:
    """C6 (IC2): road_crossings property must be present on all corridors."""

    def test_all_corridors_have_road_crossings(self):
        """Every corridor should have road_crossings property (0 or positive)."""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json={
                "bounds": {"south": 47.285, "north": 47.315, "west": -71.535, "east": -71.505},
                "species": "moose",
                "layers": ["habitats", "rut", "repos", "alimentation"],
                "waypoint_center": {"lat": 47.30, "lng": -71.52}
            },
            timeout=60
        )
        assert response.status_code == 200
        
        data = response.json()
        corridors = data.get('corridors', [])
        
        for c in corridors:
            props = c.get('properties', {})
            assert 'road_crossings' in props, \
                f"Corridor {c.get('id', '?')} missing road_crossings property"
            assert isinstance(props['road_crossings'], int), \
                f"road_crossings should be int, got {type(props['road_crossings'])}"
            assert props['road_crossings'] >= 0, \
                f"road_crossings should be >= 0, got {props['road_crossings']}"


class TestC7Deduplication:
    """C7 (BUG-05): Duplicate male/female corridors should be eliminated."""

    def test_more_male_than_female_corridors(self):
        """Due to deduplication, male corridors should be >= female corridors."""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json={
                "bounds": {"south": 47.285, "north": 47.315, "west": -71.535, "east": -71.505},
                "species": "moose",
                "layers": ["habitats", "rut", "repos", "alimentation"],
                "waypoint_center": {"lat": 47.30, "lng": -71.52}
            },
            timeout=60
        )
        assert response.status_code == 200
        
        data = response.json()
        corridors = data.get('corridors', [])
        
        male_count = len([c for c in corridors if c.get('properties', {}).get('sex') == 'male'])
        female_count = len([c for c in corridors if c.get('properties', {}).get('sex') == 'female'])
        
        # Due to C7 deduplication, identical paths prioritize male (higher confidence)
        # So male >= female is expected
        assert male_count >= female_count, \
            f"Expected male >= female after deduplication, got male={male_count}, female={female_count}"

    def test_no_duplicate_same_route(self):
        """No two corridors should have same from_zone_id + to_zone_id + sex."""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json={
                "bounds": {"south": 47.285, "north": 47.315, "west": -71.535, "east": -71.505},
                "species": "moose",
                "layers": ["habitats", "rut", "repos", "alimentation"],
                "waypoint_center": {"lat": 47.30, "lng": -71.52}
            },
            timeout=60
        )
        assert response.status_code == 200
        
        data = response.json()
        corridors = data.get('corridors', [])
        
        seen = set()
        for c in corridors:
            props = c.get('properties', {})
            key = (props.get('from_zone_id'), props.get('to_zone_id'), props.get('sex'))
            assert key not in seen, \
                f"Duplicate corridor found: from={key[0]}, to={key[1]}, sex={key[2]}"
            seen.add(key)


class TestC8WindDirection:
    """C8 (IM2): All corridors must have wind_direction_deg=225.0 (default SO→NE)."""

    def test_all_corridors_have_wind_direction(self):
        """Every corridor should have wind_direction_deg=225.0."""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json={
                "bounds": {"south": 47.285, "north": 47.315, "west": -71.535, "east": -71.505},
                "species": "moose",
                "layers": ["habitats", "rut", "repos", "alimentation"],
                "waypoint_center": {"lat": 47.30, "lng": -71.52}
            },
            timeout=60
        )
        assert response.status_code == 200
        
        data = response.json()
        corridors = data.get('corridors', [])
        
        for c in corridors:
            props = c.get('properties', {})
            assert 'wind_direction_deg' in props, \
                f"Corridor {c.get('id', '?')} missing wind_direction_deg"
            assert props['wind_direction_deg'] == 225.0, \
                f"wind_direction_deg should be 225.0, got {props['wind_direction_deg']}"


class TestPasse1NonRegression:
    """Passe 1 Non-Regression: zones still have correct scoring and T4 coherence."""

    def test_t4_zone_count_matches_features(self):
        """stats.t4_zone_count must match len(features)."""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json={
                "bounds": {"south": 47.285, "north": 47.315, "west": -71.535, "east": -71.505},
                "species": "moose",
                "layers": ["habitats", "rut", "repos", "alimentation"],
                "waypoint_center": {"lat": 47.30, "lng": -71.52}
            },
            timeout=60
        )
        assert response.status_code == 200
        
        data = response.json()
        features = data.get('features', [])
        stats = data.get('stats', {})
        t4_count = stats.get('t4_zone_count', -1)
        
        assert t4_count == len(features), \
            f"T4 mismatch: t4_zone_count={t4_count}, features count={len(features)}"

    def test_zones_have_correct_score_format(self):
        """All zones must have score = score_display = int(score_global)."""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json={
                "bounds": {"south": 47.285, "north": 47.315, "west": -71.535, "east": -71.505},
                "species": "moose",
                "layers": ["habitats", "rut", "repos", "alimentation"],
                "waypoint_center": {"lat": 47.30, "lng": -71.52}
            },
            timeout=60
        )
        assert response.status_code == 200
        
        data = response.json()
        features = data.get('features', [])
        
        for f in features:
            props = f.get('properties', {})
            score = props.get('score')
            score_display = props.get('score_display')
            score_global = props.get('score_global')
            
            if score_global is not None:
                expected = max(25, int(score_global))
                assert score == expected, \
                    f"score mismatch: score={score}, expected={expected}"
                assert score_display == expected, \
                    f"score_display mismatch: score_display={score_display}, expected={expected}"
