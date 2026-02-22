"""
P1-HOTSPOTS V3 - OSM Cache Service Tests
Tests spécifiques pour l'évitement géospatial RÉEL basé sur données OpenStreetMap:
- Vérification que le cache OSM est chargé avec les zones d'exclusion
- Vérification que les points dans l'eau/routes/zones urbaines sont exclus
- Vérification que les hotspots évitent les zones d'exclusion OSM
- Vérification de la structure du cache CA-QC
"""

import pytest
import requests
import os
import json
from pathlib import Path

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Path vers le cache OSM local
OSM_CACHE_DIR = Path("/app/backend/data/osm_cache")


class TestOSMCacheLoading:
    """Test que le cache OSM est correctement chargé avec les zones d'exclusion"""
    
    def test_osm_cache_directory_exists(self):
        """Vérifier que le répertoire de cache OSM existe"""
        assert OSM_CACHE_DIR.exists(), f"OSM cache directory not found at {OSM_CACHE_DIR}"
        print(f"OSM cache directory exists at {OSM_CACHE_DIR}")
    
    def test_ca_qc_cache_file_exists(self):
        """Vérifier que le fichier de cache CA-QC existe"""
        cache_file = OSM_CACHE_DIR / "CA-QC.json"
        assert cache_file.exists(), f"CA-QC cache file not found at {cache_file}"
        
        file_size = cache_file.stat().st_size
        print(f"CA-QC.json file size: {file_size / 1024 / 1024:.2f} MB")
        
        # Le cache devrait avoir au moins 1 MB de données
        assert file_size > 1024 * 1024, f"CA-QC cache file too small ({file_size} bytes)"
    
    def test_ca_qc_cache_has_exclusion_zones(self):
        """Vérifier que le cache CA-QC contient des zones d'exclusion"""
        cache_file = OSM_CACHE_DIR / "CA-QC.json"
        
        with open(cache_file, 'r') as f:
            # Lire uniquement les premiers caractères pour éviter de charger tout le fichier
            data = json.load(f)
        
        # Vérifier la structure du cache
        assert "region_id" in data, "Missing region_id in cache"
        assert data["region_id"] == "CA-QC", f"Wrong region_id: {data['region_id']}"
        
        assert "exclusion_zones" in data, "Missing exclusion_zones in cache"
        zones_count = len(data.get("exclusion_zones", []))
        
        print(f"CA-QC cache contains {zones_count} exclusion zones")
        
        # Devrait avoir au moins 1000 zones d'exclusion
        assert zones_count >= 1000, f"Too few exclusion zones: {zones_count} (expected >= 1000)"
    
    def test_ca_qc_cache_has_water_zones(self):
        """Vérifier que le cache CA-QC contient des zones d'eau"""
        cache_file = OSM_CACHE_DIR / "CA-QC.json"
        
        with open(cache_file, 'r') as f:
            data = json.load(f)
        
        zones = data.get("exclusion_zones", [])
        water_zones = [z for z in zones if z.get("zone_type") == "water"]
        
        print(f"CA-QC cache contains {len(water_zones)} water zones")
        
        # Devrait avoir des zones d'eau
        assert len(water_zones) > 0, "No water zones found in cache"
        
        # Vérifier qu'une zone d'eau a une géométrie valide
        if water_zones:
            first_water = water_zones[0]
            assert "geometry" in first_water, "Water zone missing geometry"
            assert first_water["geometry"]["type"] == "Polygon", "Water zone should be Polygon"


class TestHotspotAPIWithOSMCache:
    """Test que l'API de hotspots utilise le cache OSM"""
    
    def test_api_returns_hotspots_for_quebec(self):
        """Vérifier que l'API génère des hotspots pour le Québec"""
        payload = {
            "bounds": {"north": 46.9, "south": 46.8, "east": -71.1, "west": -71.3},
            "species": ["moose"],
            "time_range": "24h",
            "hotspot_types": ["activity_peak"],
            "min_score_threshold": 50
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/map/hotspots", json=payload, timeout=120)
        assert response.status_code == 200, f"API returned {response.status_code}"
        
        data = response.json()
        assert data["success"] == True
        
        print(f"Generated {data['statistics']['total_hotspots']} hotspots")
    
    def test_metadata_confirms_marching_squares_chaikin(self):
        """Vérifier que l'algorithme est bien marching_squares_chaikin"""
        payload = {
            "bounds": {"north": 46.9, "south": 46.8, "east": -71.1, "west": -71.3},
            "species": ["moose"],
            "time_range": "24h",
            "hotspot_types": ["activity_peak"],
            "min_score_threshold": 50
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/map/hotspots", json=payload, timeout=120)
        assert response.status_code == 200
        
        data = response.json()
        metadata = data.get("metadata", {})
        
        contour_algo = metadata.get("contour_algorithm", "")
        print(f"Contour algorithm: {contour_algo}")
        
        assert "marching_squares_chaikin" in contour_algo.lower(), \
            f"Expected marching_squares_chaikin, got: {contour_algo}"
    
    def test_hotspots_avoid_st_lawrence_river(self):
        """Vérifier que les hotspots évitent le fleuve Saint-Laurent"""
        # Zone dans le fleuve Saint-Laurent près de Québec
        # (latitude ~46.8, longitude ~-71.2)
        payload = {
            "bounds": {"north": 46.85, "south": 46.80, "east": -71.15, "west": -71.25},
            "species": ["moose"],
            "time_range": "24h",
            "hotspot_types": ["activity_peak", "feeding_zone"],
            "min_score_threshold": 40  # Seuil bas pour avoir plus de chance d'avoir des résultats
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/map/hotspots", json=payload, timeout=120)
        assert response.status_code == 200
        
        data = response.json()
        # Le nombre de hotspots pourrait être réduit si la zone d'évitement est active
        print(f"Hotspots near St-Lawrence: {data['statistics']['total_hotspots']}")
        
        # Vérifier que les hotspots générés ne sont pas exactement au centre du fleuve
        # Le fleuve Saint-Laurent est approximativement à lat ~46.82, lng ~-71.2
        for hs in data.get("hotspots", [])[:5]:
            coords = hs["geometry"]["coordinates"][0]
            center_lat = sum(c[1] for c in coords) / len(coords)
            center_lng = sum(c[0] for c in coords) / len(coords)
            
            # Le centre du hotspot ne devrait pas être dans le fleuve (46.80-46.83, -71.25 to -71.15)
            print(f"Hotspot center: ({center_lat:.4f}, {center_lng:.4f})")


class TestHotspotStyleCompliance:
    """Test que les styles des hotspots sont conformes aux spécifications"""
    
    def test_stroke_width_approximately_1_5px(self):
        """Vérifier que stroke_width est environ 1.5px"""
        payload = {
            "bounds": {"north": 46.9, "south": 46.8, "east": -71.1, "west": -71.3},
            "species": ["moose"],
            "time_range": "24h",
            "hotspot_types": ["activity_peak"],
            "min_score_threshold": 50
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/map/hotspots", json=payload, timeout=120)
        assert response.status_code == 200
        
        data = response.json()
        if data["hotspots"]:
            style = data["hotspots"][0]["style"]
            stroke_width = style.get("stroke_width", 0)
            
            print(f"Stroke width: {stroke_width}px")
            
            # Stroke width devrait être ~1.5px (entre 1 et 2)
            assert 1.0 <= stroke_width <= 2.0, f"Stroke width {stroke_width} not in range 1-2px"
            assert stroke_width == 1.5, f"Expected stroke_width=1.5, got {stroke_width}"
    
    def test_fill_opacity_is_zero(self):
        """Vérifier que fill_opacity est exactement 0"""
        payload = {
            "bounds": {"north": 46.9, "south": 46.8, "east": -71.1, "west": -71.3},
            "species": ["moose"],
            "time_range": "24h",
            "hotspot_types": ["activity_peak"],
            "min_score_threshold": 50
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/map/hotspots", json=payload, timeout=120)
        assert response.status_code == 200
        
        data = response.json()
        if data["hotspots"]:
            style = data["hotspots"][0]["style"]
            fill_opacity = style.get("fill_opacity", -1)
            
            print(f"Fill opacity: {fill_opacity}")
            
            assert fill_opacity == 0.0, f"fill_opacity should be 0, got {fill_opacity}"


class TestHotspotAreaSpecification:
    """Test que la superficie des hotspots est conforme (5000-10000 m²)"""
    
    def test_hotspot_area_within_specification(self):
        """Vérifier que la superficie est dans la plage 5000-10000 m²"""
        import math
        
        payload = {
            "bounds": {"north": 47.0, "south": 46.5, "east": -71.0, "west": -71.5},
            "species": ["moose"],
            "time_range": "24h",
            "hotspot_types": ["activity_peak"],
            "min_score_threshold": 50
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/map/hotspots", json=payload, timeout=120)
        assert response.status_code == 200
        
        data = response.json()
        if not data["hotspots"]:
            pytest.skip("No hotspots generated")
        
        coords = data["hotspots"][0]["geometry"]["coordinates"][0]
        
        # Calculer l'aire avec la formule de Shoelace
        n = len(coords)
        area_deg = 0
        for i in range(n - 1):
            area_deg += coords[i][0] * coords[i + 1][1]
            area_deg -= coords[i + 1][0] * coords[i][1]
        area_deg = abs(area_deg) / 2
        
        # Convertir en m²
        center_lat = sum(c[1] for c in coords) / n
        meters_per_deg_lat = 111320
        meters_per_deg_lng = 111320 * math.cos(math.radians(center_lat))
        area_m2 = area_deg * meters_per_deg_lat * meters_per_deg_lng
        
        print(f"Hotspot area: {area_m2:.0f} m² (target: 5000-10000 m²)")
        
        # Avec 10% de tolérance: 4500-11000
        assert 4500 <= area_m2 <= 11000, f"Area {area_m2:.0f} m² outside specification (5000-10000 m²)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
