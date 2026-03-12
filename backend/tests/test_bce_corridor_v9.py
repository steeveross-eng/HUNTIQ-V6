"""
Tests BCE-4X Corridor Validator
================================
Tests unitaires, geometriques, ecologiques, scoring, anti-regression.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from bce.validators.corridor_v9 import (
    detect_hardcoded_scores,
    validate_geometry,
    validate_clipping,
    validate_classification,
    validate_scoring_coherence,
    validate_corridor_batch,
)


# ── Fixtures ──

def make_corridor(
    cid="test-1",
    coords=None,
    corridor_type="conservation_corridor",
    distance_m=500,
    score=60,
    terrain_subscore=55.0,
    habitat_subscore=62.0,
    pathfinding="A*",
    scores_10x=None,
    source="corridor_10x",
    sex="both",
):
    if coords is None:
        coords = [[-71.300, 46.940], [-71.2995, 46.9405], [-71.299, 46.941]]
    return {
        "id": cid,
        "type": "Feature",
        "geometry": {"type": "LineString", "coordinates": coords},
        "properties": {
            "corridor_type": corridor_type,
            "distance_m": distance_m,
            "pathfinding": pathfinding,
            "source": source,
            "sex": sex,
            "scoring": {
                "score": score,
                "subscores": {
                    "terrain": terrain_subscore,
                    "habitat": habitat_subscore,
                    "connectivity": 85.0,
                },
                "justification": [],
            },
            "scores_10x": scores_10x,
        },
    }


BOUNDS_TEST = {"south": 46.93, "north": 46.96, "west": -71.33, "east": -71.27}


# ═══════════════════════════════════════
# 1. HARDCODED SCORE DETECTION
# ═══════════════════════════════════════

class TestHardcodedScoreDetection:

    def test_detects_hardcoded_terrain_65(self):
        c = make_corridor(terrain_subscore=65.0)
        violations = detect_hardcoded_scores(c)
        assert any(v.type.value == "hardcoded_score" for v in violations)

    def test_detects_hardcoded_habitat_70(self):
        c = make_corridor(habitat_subscore=70.0)
        violations = detect_hardcoded_scores(c)
        assert any(v.type.value == "hardcoded_score" for v in violations)

    def test_passes_dynamic_scores(self):
        c = make_corridor(terrain_subscore=55.0, habitat_subscore=62.0)
        violations = detect_hardcoded_scores(c)
        assert len(violations) == 0

    def test_detects_both_hardcoded(self):
        c = make_corridor(terrain_subscore=65.0, habitat_subscore=70.0)
        violations = detect_hardcoded_scores(c)
        assert len(violations) == 2


# ═══════════════════════════════════════
# 2. GEOMETRY VALIDATION
# ═══════════════════════════════════════

class TestGeometryValidation:

    def test_valid_linestring(self):
        c = make_corridor()
        violations = validate_geometry(c)
        assert len(violations) == 0

    def test_rejects_single_point(self):
        c = make_corridor(coords=[[-71.30, 46.94]])
        violations = validate_geometry(c)
        assert any(v.type.value == "geometry_invalid" for v in violations)

    def test_detects_circular_corridor(self):
        c = make_corridor(coords=[
            [-71.30, 46.94],
            [-71.29, 46.95],
            [-71.28, 46.94],
            [-71.30, 46.94],  # retour au depart
        ])
        violations = validate_geometry(c)
        assert any(v.type.value == "circular_corridor" for v in violations)

    def test_detects_continuity_break(self):
        c = make_corridor(coords=[
            [-71.30, 46.94],
            [-71.25, 46.98],  # gap > 200m
        ])
        violations = validate_geometry(c)
        assert any(v.type.value == "continuity_break" for v in violations)


# ═══════════════════════════════════════
# 3. CLIPPING 2km² VALIDATION
# ═══════════════════════════════════════

class TestClippingValidation:

    def test_corridor_within_bounds(self):
        c = make_corridor(coords=[[-71.30, 46.94], [-71.29, 46.95]])
        violations = validate_clipping(c, BOUNDS_TEST)
        assert len(violations) == 0

    def test_corridor_out_of_bounds(self):
        c = make_corridor(coords=[[-71.30, 46.94], [-71.20, 47.00]])  # way outside
        violations = validate_clipping(c, BOUNDS_TEST)
        assert any(v.type.value == "out_of_bounds" for v in violations)

    def test_no_bounds_provided(self):
        c = make_corridor()
        violations = validate_clipping(c, None)
        assert len(violations) == 0


# ═══════════════════════════════════════
# 4. CLASSIFICATION VALIDATION
# ═══════════════════════════════════════

class TestClassificationValidation:

    def test_valid_classification(self):
        for ctype in ["macro_corridor", "biological_corridor", "conservation_corridor"]:
            c = make_corridor(corridor_type=ctype)
            violations = validate_classification(c)
            assert len(violations) == 0

    def test_invalid_classification(self):
        c = make_corridor(corridor_type="unknown_type")
        violations = validate_classification(c)
        assert any(v.type.value == "classification_unreachable" for v in violations)


# ═══════════════════════════════════════
# 5. SCORING COHERENCE
# ═══════════════════════════════════════

class TestScoringCoherence:

    def test_valid_score_range(self):
        c = make_corridor(score=60, scores_10x={"enhanced": True})
        violations = validate_scoring_coherence(c)
        assert len(violations) == 0

    def test_score_out_of_range(self):
        c = make_corridor(score=150)
        violations = validate_scoring_coherence(c)
        assert any(v.type.value == "score_incoherence" for v in violations)

    def test_missing_enrichment(self):
        c = make_corridor(scores_10x=None)
        violations = validate_scoring_coherence(c)
        assert any(v.type.value == "missing_enrichment" for v in violations)


# ═══════════════════════════════════════
# 6. BATCH VALIDATION
# ═══════════════════════════════════════

class TestBatchValidation:

    def test_compliant_batch(self):
        corridors = [
            make_corridor(cid="c1", scores_10x={"enhanced": True}),
            make_corridor(cid="c2", scores_10x={"enhanced": True}),
        ]
        report = validate_corridor_batch(corridors, BOUNDS_TEST)
        assert report["status"] == "COMPLIANT_100"
        assert report["total_violations"] == 0

    def test_blocked_on_hardcoded(self):
        corridors = [
            make_corridor(cid="c1", terrain_subscore=65.0, habitat_subscore=70.0),
        ]
        report = validate_corridor_batch(corridors, BOUNDS_TEST)
        assert report["status"] == "BLOCKED"
        assert report["by_severity"]["critical"] > 0

    def test_empty_batch(self):
        report = validate_corridor_batch([], BOUNDS_TEST)
        assert report["status"] == "COMPLIANT_100"
        assert report["corridors_validated"] == 0


# ═══════════════════════════════════════
# 7. ANTI-REGRESSION
# ═══════════════════════════════════════

class TestAntiRegression:

    def test_all_rules_applied(self):
        corridors = [make_corridor(scores_10x={"enhanced": True})]
        report = validate_corridor_batch(corridors, BOUNDS_TEST)
        expected_rules = [
            "hardcoded_score_detection",
            "geometry_linestring_valid",
            "circular_corridor_detection",
            "continuity_gap_check",
            "bounds_clipping_2km",
            "classification_valid",
            "scoring_range_check",
            "enrichment_check",
        ]
        for rule in expected_rules:
            assert rule in report["rules_applied"], f"Regle manquante: {rule}"

    def test_report_structure(self):
        report = validate_corridor_batch([make_corridor(scores_10x={"x": 1})], BOUNDS_TEST)
        assert "module" in report
        assert "version" in report
        assert "status" in report
        assert "corridors_validated" in report
        assert "total_violations" in report
        assert "by_severity" in report
        assert "by_type" in report
        assert "rules_applied" in report
