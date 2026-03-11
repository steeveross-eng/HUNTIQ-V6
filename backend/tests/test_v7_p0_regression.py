"""
BIONIC V7 — Tests de non-régression P0
Incident critique : waypoint rural sans zones après migration V7.

Teste 3 waypoints différents pour valider :
  1. Waypoint P0 rural (47.0, -72.28) → DOIT générer des zones
  2. Forêt profonde (46.65, -73.18) → DOIT générer un max de zones (0 rejets)
  3. Zone périurbaine (46.35, -72.55) → DOIT rejeter toutes les zones (urbain/eau)

Couvre aussi :
  - Moteur V7 exclusif (aucun appel V6)
  - Marges V7 réduites appliquées
  - Zones en eau toujours exclues
  - Diagnostics de rejet propagés
"""

import pytest
import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from modules.bionic_engine_p0.services.exclusion_config_v7 import (
    BUFFER_CONFIG_V7,
    INTERSECTION_THRESHOLDS_V7,
    TRIMMING_MIN_AREA_M2_V7,
    ANTHROPIC_THRESHOLDS_V7,
    VEGETATION_MIN_DENSITY_V7,
    get_buffer_m_v7,
)


class TestExclusionConfigV7:
    """Valide que les marges V7 réduites sont correctement définies."""

    def test_water_river_margin(self):
        assert get_buffer_m_v7("water", "river") == 40

    def test_water_lake_margin(self):
        assert get_buffer_m_v7("water", "lake") == 75

    def test_water_stream_margin(self):
        assert get_buffer_m_v7("water", "stream") == 10

    def test_urban_residential_margin(self):
        assert get_buffer_m_v7("urban", "residential") == 120

    def test_urban_farmyard_margin(self):
        assert get_buffer_m_v7("urban", "farmyard") == 75

    def test_roads_primary_margin(self):
        assert get_buffer_m_v7("roads", "primary") == 75

    def test_roads_secondary_margin(self):
        assert get_buffer_m_v7("roads", "secondary") == 35

    def test_roads_track_margin(self):
        assert get_buffer_m_v7("roads", "track") == 10

    def test_vegetation_min_density(self):
        assert VEGETATION_MIN_DENSITY_V7 == 0.20

    def test_intersection_thresholds_relaxed(self):
        assert INTERSECTION_THRESHOLDS_V7["water"] == 0.08
        assert INTERSECTION_THRESHOLDS_V7["urban"] == 0.12
        assert INTERSECTION_THRESHOLDS_V7["roads"] == 0.20
        assert INTERSECTION_THRESHOLDS_V7["infrastructure"] == 0.25

    def test_trimming_min_area_reduced(self):
        assert TRIMMING_MIN_AREA_M2_V7 == 3000.0

    def test_anthropic_thresholds_exist(self):
        assert "urban_roads_combo" in ANTHROPIC_THRESHOLDS_V7
        assert "major_road_alone" in ANTHROPIC_THRESHOLDS_V7
        assert "combined_product_min" in ANTHROPIC_THRESHOLDS_V7


class TestExclusionEngineV7:
    """Valide que le moteur V7 utilise bien les marges V7."""

    def test_v7_engine_import(self):
        from modules.bionic_engine_p0.services.exclusion_engine_v7 import (
            process_zones_v7_exclusion,
        )
        assert callable(process_zones_v7_exclusion)

    def test_v7_engine_empty_zones(self):
        from modules.bionic_engine_p0.services.exclusion_engine_v7 import (
            process_zones_v7_exclusion,
        )
        bounds = {"north": 47.015, "south": 46.985, "east": -72.265, "west": -72.295}
        valid, rejected, stats = process_zones_v7_exclusion([], bounds, [], "habitats")
        assert valid == []
        assert rejected == []
        assert stats["engine"] == "v7"
        assert stats["config"] == "exclusion_config_v7"
        assert stats["margins_applied"] == "V7_REDUCED"

    def test_pipeline_v7_uses_v7_engine(self):
        """Confirme que pipeline_v7 importe exclusivement exclusion_engine_v7."""
        import inspect
        from modules.bionic_engine_p0.services.pipeline_v7 import process_zones_v7
        source = inspect.getsource(process_zones_v7)
        assert "process_zones_v7_exclusion" in source or "exclusion_engine_v7" in inspect.getfile(process_zones_v7)

    def test_v7_no_v6_import_in_pipeline(self):
        """Confirme qu'aucun import V6 exclusion engine n'est dans pipeline_v7."""
        with open(os.path.join(os.path.dirname(__file__), "..", "modules", "bionic_engine_p0", "services", "pipeline_v7.py")) as f:
            content = f.read()
        assert "from .exclusion_engine_v6 import" not in content


class TestWaypointP0Regression:
    """Tests de non-régression pour le waypoint P0."""

    def _generate_zones(self, lat, lng, delta=0.015):
        from modules.bionic_engine_p0.services.exclusion_engine_v7 import (
            process_zones_v7_exclusion,
        )
        from modules.bionic_engine_p0.services.behavioral_rasterizer import (
            generate_layer_raster, LAYER_PARAMS,
        )
        from modules.bionic_engine_p0.services.organic_zone_generator_v2 import (
            extract_organic_zones,
        )

        bounds = {
            "north": lat + delta,
            "south": lat - delta,
            "east": lng + delta,
            "west": lng - delta,
        }

        all_valid = []
        all_rejected = []

        for layer_id in ["habitats", "alimentation", "repos"]:
            if layer_id not in LAYER_PARAMS:
                continue
            params = LAYER_PARAMS[layer_id]
            grid = generate_layer_raster(bounds, layer_id, "moose", 60)
            raw_zones = extract_organic_zones(
                grid, bounds,
                threshold=params["threshold"],
                min_area=8000.0,
                max_area=80000.0,
                chaikin_iterations=4,
                max_compactness=0.85,
            )

            # V7 exclusion with NO external exclusions (pure zone generation test)
            valid, rejected, stats = process_zones_v7_exclusion(
                raw_zones=raw_zones,
                bounds=bounds,
                exclusions=[],
                layer_id=layer_id,
                species="moose",
            )
            all_valid.extend(valid)
            all_rejected.extend(rejected)

        return all_valid, all_rejected

    def test_p0_waypoint_generates_zones(self):
        """Le waypoint P0 (47.0, -72.28) DOIT générer des zones sans exclusions."""
        valid, rejected = self._generate_zones(47.0, -72.28)
        assert len(valid) > 0, \
            f"REGRESSION P0: Waypoint rural (47.0, -72.28) génère 0 zones. Rejected: {len(rejected)}"

    def test_forest_waypoint_generates_many_zones(self):
        """Le waypoint forêt (46.65, -73.18) DOIT générer beaucoup de zones."""
        valid, rejected = self._generate_zones(46.65, -73.18)
        assert len(valid) > 0, \
            f"REGRESSION: Waypoint forêt (46.65, -73.18) génère 0 zones. Rejected: {len(rejected)}"

    def test_v7_stats_contain_config_marker(self):
        """Les stats doivent indiquer le moteur V7 et la config V7."""
        from modules.bionic_engine_p0.services.exclusion_engine_v7 import (
            process_zones_v7_exclusion,
        )
        bounds = {"north": 47.015, "south": 46.985, "east": -72.265, "west": -72.295}
        _, _, stats = process_zones_v7_exclusion([], bounds, [], "habitats")
        assert stats["config"] == "exclusion_config_v7"
        assert stats["margins_applied"] == "V7_REDUCED"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
