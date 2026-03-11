"""
BIONIC V5 P0 — Test des exclusions de zones fonctionnelles
Tests pour vérifier les corrections critiques:
1. Routes + infrastructure ajoutées au filtrage (hard mask)
2. Filtrage multi-points (centroïde + 4 cardinaux) au lieu de centroïde seul
3. Bbox des exclusions couvre tout le viewport (tiling automatique)

Résultat attendu: aucune zone fonctionnelle ne peut apparaître dans zones urbaines,
sur l'eau, sur les routes, ou sur les infrastructures.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestBionicP0ExclusionZones:
    """Test API /api/v1/bionic/organic-zones with exclusion filtering"""
    
    def test_health_check(self):
        """Verify API is accessible"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        print("✅ API health check passed")
    
    def test_urban_zone_returns_zero_zones(self):
        """
        Zone urbaine (Québec 46.80-46.85, -71.20--71.28) doit retourner 0 zones valides
        Toutes les zones doivent être rejetées car situées en milieu urbain
        """
        payload = {
            "bounds": {
                "south": 46.80,
                "north": 46.85,
                "west": -71.28,
                "east": -71.20
            },
            "species": "moose"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        stats = data.get("stats", {})
        
        # Zone urbaine = 0 zones valides
        assert stats.get("total_zones") == 0, f"Expected 0 zones in urban area, got {stats.get('total_zones')}"
        
        # Doit avoir des rejets
        assert stats.get("rejected_exclusion", 0) > 0, "Expected rejected_exclusion > 0 in urban area"
        
        # Doit avoir des exclusions détectées
        assert stats.get("exclusions_count", 0) > 0, "Expected exclusions_count > 0"
        
        print(f"✅ Urban zone test passed: total_zones={stats.get('total_zones')}, "
              f"rejected_exclusion={stats.get('rejected_exclusion')}, "
              f"exclusions_count={stats.get('exclusions_count')}")
    
    def test_forest_zone_returns_valid_zones(self):
        """
        Zone forestière (47.05-47.10, -70.85--70.93) doit retourner des zones valides > 0
        Les zones en forêt ne sont pas exclues
        """
        payload = {
            "bounds": {
                "south": 47.05,
                "north": 47.10,
                "west": -70.93,
                "east": -70.85
            },
            "species": "moose"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        stats = data.get("stats", {})
        
        # Zone forestière = zones valides > 0
        assert stats.get("total_zones", 0) > 0, f"Expected zones > 0 in forest area, got {stats.get('total_zones')}"
        
        # Stats doivent contenir rejected_exclusion
        assert "rejected_exclusion" in stats, "Expected rejected_exclusion in stats"
        
        # Stats doivent contenir exclusions_count  
        assert "exclusions_count" in stats, "Expected exclusions_count in stats"
        
        # GeoJSON features should match total_zones
        features = data.get("features", [])
        assert len(features) == stats.get("total_zones"), \
            f"Features count ({len(features)}) should match total_zones ({stats.get('total_zones')})"
        
        print(f"✅ Forest zone test passed: total_zones={stats.get('total_zones')}, "
              f"rejected_exclusion={stats.get('rejected_exclusion')}, "
              f"exclusions_count={stats.get('exclusions_count')}")
    
    def test_api_returns_geojson_format(self):
        """Verify API returns proper GeoJSON FeatureCollection format"""
        payload = {
            "bounds": {
                "south": 47.05,
                "north": 47.10,
                "west": -70.93,
                "east": -70.85
            },
            "species": "moose"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        
        data = response.json()
        
        # Check GeoJSON structure
        assert data.get("type") == "FeatureCollection", "Expected type=FeatureCollection"
        assert "features" in data, "Expected features array"
        assert "stats" in data, "Expected stats object"
        assert "metadata" in data, "Expected metadata object"
        
        # Validate metadata
        metadata = data.get("metadata", {})
        assert metadata.get("species") == "moose", "Expected species=moose in metadata"
        assert "source_id" in metadata, "Expected source_id in metadata"
        
        print(f"✅ GeoJSON format validation passed")
    
    def test_exclusion_stats_present(self):
        """Verify stats include rejected_exclusion and exclusions_count fields"""
        payload = {
            "bounds": {
                "south": 46.90,
                "north": 46.95,
                "west": -71.10,
                "east": -71.05
            },
            "species": "moose"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        
        data = response.json()
        stats = data.get("stats", {})
        
        # Required stats fields for P0 exclusion fix
        required_fields = [
            "layers_processed",
            "total_zones", 
            "rejected_exclusion",
            "exclusions_count",
            "species",
            "bounds"
        ]
        
        for field in required_fields:
            assert field in stats, f"Expected '{field}' in stats"
        
        # rejected_exclusion should be >= 0
        assert stats.get("rejected_exclusion", -1) >= 0, "rejected_exclusion should be >= 0"
        
        # exclusions_count should be >= 0
        assert stats.get("exclusions_count", -1) >= 0, "exclusions_count should be >= 0"
        
        print(f"✅ Exclusion stats validation passed: "
              f"rejected_exclusion={stats.get('rejected_exclusion')}, "
              f"exclusions_count={stats.get('exclusions_count')}")


class TestTerrainDataAPI:
    """Test terrain data API for exclusion zones"""
    
    def test_terrain_data_health(self):
        """Verify terrain data health endpoint"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/terrain/terrain-data/health")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("status") == "operational"
        assert "supported_types" in data
        
        # Verify all 4 exclusion types are supported
        supported_types = data.get("supported_types", [])
        required_types = ["water", "roads", "urban", "infrastructure"]
        for t in required_types:
            assert t in supported_types, f"Expected '{t}' in supported_types"
        
        print(f"✅ Terrain data health check passed: supported_types={supported_types}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
