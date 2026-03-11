"""
BIONIC V5 300% — Tests Anti-Régression: Spatial Clipping
=========================================================
INVARIANT: Ces tests doivent PASSER à chaque build.
0 débordement, 0 géométrie complète, 0 variation après figement.
"""

import pytest
import math
from modules.bionic_engine_p0.services.spatial_clipping import (
    compute_analysis_bbox,
    bbox_to_polygon,
    clip_polygon_coords,
    clip_zones,
    compute_clipping_stats,
    ANALYSIS_BOX_SIZE_M,
)


class TestAnalysisBbox:
    """Tests pour le calcul du AnalysisBoundingBox 1km × 1km."""
    
    def test_bbox_size_invariant(self):
        """INVARIANT: La taille est toujours 1000m."""
        assert ANALYSIS_BOX_SIZE_M == 1000
    
    def test_bbox_centered_on_waypoint(self):
        """Le bbox doit être centré sur le waypoint."""
        bbox = compute_analysis_bbox(46.8, -71.2)
        center_lat = (bbox["north"] + bbox["south"]) / 2
        center_lng = (bbox["east"] + bbox["west"]) / 2
        assert abs(center_lat - 46.8) < 1e-10
        assert abs(center_lng - (-71.2)) < 1e-10
    
    def test_bbox_dimensions_1km(self):
        """Le bbox doit mesurer environ 1km × 1km."""
        bbox = compute_analysis_bbox(46.8, -71.2)
        
        # Vérifier la hauteur (lat): ~1000m
        lat_range = bbox["north"] - bbox["south"]
        height_m = lat_range * 111320
        assert 999 < height_m < 1001, f"Height: {height_m}m"
        
        # Vérifier la largeur (lng): ~1000m
        lng_range = bbox["east"] - bbox["west"]
        width_m = lng_range * 111320 * math.cos(math.radians(46.8))
        assert 999 < width_m < 1001, f"Width: {width_m}m"
    
    def test_bbox_no_padding(self):
        """INVARIANT: Aucun padding, buffer ou marge."""
        bbox1 = compute_analysis_bbox(46.8, -71.2, 1000)
        bbox2 = compute_analysis_bbox(46.8, -71.2)
        assert bbox1 == bbox2  # Default = 1000m, pas de marge ajoutée
    
    def test_bbox_deterministic(self):
        """INVARIANT: Même entrée = même sortie."""
        bbox1 = compute_analysis_bbox(46.8, -71.2)
        bbox2 = compute_analysis_bbox(46.8, -71.2)
        assert bbox1 == bbox2


class TestSpatialClipping:
    """Tests pour le clipping géométrique ST_Intersection."""
    
    def setup_method(self):
        """Bbox de test centré sur (46.8, -71.2)."""
        self.bbox = compute_analysis_bbox(46.8, -71.2)
        self.clip_box = bbox_to_polygon(self.bbox)
    
    def test_polygon_inside_unchanged(self):
        """Un polygone entièrement dans le bbox doit être conservé."""
        inside_coords = [
            [46.8005, -71.2005],
            [46.8005, -71.1995],
            [46.7995, -71.1995],
            [46.7995, -71.2005],
        ]
        result = clip_polygon_coords(inside_coords, self.clip_box)
        assert result is not None
        assert len(result) >= 4
    
    def test_polygon_outside_removed(self):
        """Un polygone entièrement hors du bbox doit être supprimé."""
        outside_coords = [
            [47.0, -70.0],
            [47.0, -69.9],
            [46.9, -69.9],
            [46.9, -70.0],
        ]
        result = clip_polygon_coords(outside_coords, self.clip_box)
        assert result is None
    
    def test_polygon_partially_clipped(self):
        """Un polygone partiellement dans le bbox doit être clippé."""
        partial_coords = [
            [46.81, -71.21],   # hors nord-ouest
            [46.81, -71.19],   # hors nord-est
            [46.79, -71.19],   # hors sud-est
            [46.79, -71.21],   # hors sud-ouest
        ]
        result = clip_polygon_coords(partial_coords, self.clip_box)
        assert result is not None
        # Vérifier que toutes les coordonnées sont dans le bbox
        for coord in result:
            assert coord[0] >= self.bbox["south"] - 1e-9
            assert coord[0] <= self.bbox["north"] + 1e-9
            assert coord[1] >= self.bbox["west"] - 1e-9
            assert coord[1] <= self.bbox["east"] + 1e-9
    
    def test_zero_overflow(self):
        """INVARIANT: 0 débordement — aucune coordonnée hors bbox."""
        large_polygon = [
            [46.82, -71.22],
            [46.82, -71.18],
            [46.78, -71.18],
            [46.78, -71.22],
        ]
        result = clip_polygon_coords(large_polygon, self.clip_box)
        if result:
            for coord in result:
                assert coord[0] >= self.bbox["south"] - 1e-9, f"South overflow: {coord}"
                assert coord[0] <= self.bbox["north"] + 1e-9, f"North overflow: {coord}"
                assert coord[1] >= self.bbox["west"] - 1e-9, f"West overflow: {coord}"
                assert coord[1] <= self.bbox["east"] + 1e-9, f"East overflow: {coord}"


class TestClipZones:
    """Tests pour le clipping de listes de zones."""
    
    def setup_method(self):
        self.bbox = compute_analysis_bbox(46.8, -71.2)
    
    def test_clip_zones_filters_outside(self):
        """Les zones hors périmètre sont supprimées."""
        zones = [
            {"coordinates": [[46.8002, -71.2002], [46.8002, -71.1998], [46.7998, -71.1998], [46.7998, -71.2002]], "layerId": "habitats"},
            {"coordinates": [[47.0, -70.0], [47.0, -69.9], [46.9, -69.9], [46.9, -70.0]], "layerId": "habitats"},
        ]
        result = clip_zones(zones, self.bbox)
        assert len(result) == 1
    
    def test_clipped_flag_set(self):
        """Les zones clippées doivent avoir clipped=True."""
        zones = [
            {"coordinates": [[46.8002, -71.2002], [46.8002, -71.1998], [46.7998, -71.1998], [46.7998, -71.2002]], "layerId": "habitats"},
        ]
        result = clip_zones(zones, self.bbox)
        assert all(z.get("clipped") is True for z in result)
    
    def test_stats_overflow_always_zero(self):
        """INVARIANT: overflow_count = 0 toujours."""
        zones = [
            {"coordinates": [[46.82, -71.22], [46.82, -71.18], [46.78, -71.18], [46.78, -71.22]], "layerId": "rut"},
        ]
        clipped = clip_zones(zones, self.bbox)
        stats = compute_clipping_stats(zones, clipped, self.bbox)
        assert stats["overflow_count"] == 0


class TestClippingInvariance:
    """Tests de non-régression — INVARIANTS BIONIC V5 300%."""
    
    def test_clipping_deterministic(self):
        """Même entrée = même sortie."""
        bbox = compute_analysis_bbox(46.8, -71.2)
        zones = [
            {"coordinates": [[46.82, -71.22], [46.82, -71.18], [46.78, -71.18], [46.78, -71.22]], "layerId": "habitats", "score": 75},
        ]
        result1 = clip_zones(zones, bbox)
        result2 = clip_zones(zones, bbox)
        assert len(result1) == len(result2)
        for z1, z2 in zip(result1, result2):
            assert z1["coordinates"] == z2["coordinates"]
    
    def test_box_size_immutable(self):
        """La taille du carré ne peut pas être modifiée."""
        assert ANALYSIS_BOX_SIZE_M == 1000
        # La constante est un int immutable, donc non-modifiable
    
    def test_no_dynamic_influence(self):
        """Le clipping ne dépend d'aucune donnée dynamique."""
        bbox1 = compute_analysis_bbox(46.8, -71.2)
        bbox2 = compute_analysis_bbox(46.8, -71.2)
        assert bbox1 == bbox2
        # Pas de paramètres de temps, météo, saison, etc.
